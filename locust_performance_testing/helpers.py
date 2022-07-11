import logging

from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generator

import psycopg2

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from locust import task
from locust.exception import StopUser
from redis import Redis

import settings


@dataclass
class AccountHolder:
    email: str
    account_number: str
    account_holder_uuid: str
    retailer: int
    account_holder_id: int
    marketing: bool = True


class LocustHandler:
    logger = logging.getLogger("LocustHandler")
    polaris_connection_string: str = settings.DB_CONNECTION_URI.replace("/postgres?", f"/{settings.POLARIS_DB}?")

    def __init__(self) -> None:
        self.redis = Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=3,
            socket_keepalive=True,
            retry_on_timeout=False,
            decode_responses=True,
        )
        self.repeat_tasks: dict = {}  # value assigned by locustfile
        self.all_secrets: dict = {}  # value assigned by load_secrets()
        self.retailer_count: int | None = None  # value assigned by get_polaris_retailer_count()
        self.account_holder_count: int | None = None
        self.headers: dict = {}  # value assigned by get_headers()

    def load_secrets(self) -> dict:

        if not self.all_secrets:
            vault_logger = logging.getLogger("VaultHandler")
            client = SecretClient(vault_url=settings.VAULT_URL, credential=DefaultAzureCredential())
            vault_logger.info(
                f"Attempting to load secrets [{settings.POLARIS_AUTH_KEY_NAME}], [{settings.VELA_AUTH_KEY_NAME}]"
            )
            self.all_secrets.update(
                {
                    "polaris_key": client.get_secret(settings.POLARIS_AUTH_KEY_NAME).value,
                    "vela_key": client.get_secret(settings.VELA_AUTH_KEY_NAME).value,
                }
            )
            vault_logger.info("Successfully loaded secrets")

        return self.all_secrets

    def get_polaris_retailer_count(self) -> int:
        """
        Returns current retailer count in Polaris. Only contacts db on first execution.

        :return: Number of retailers in Polaris.
        """

        if not self.retailer_count:
            with psycopg2.connect(self.polaris_connection_string) as polaris_connection:
                with polaris_connection.cursor() as cursor:
                    query = "SELECT count(*) from retailer_config;"
                    cursor.execute(query)
                    results = cursor.fetchone()

                    self.retailer_count = int(results[0])

            polaris_connection.close()

        return self.retailer_count

    def get_polaris_account_holder_count(self) -> int:
        """
        Returns current retailer count in Polaris. Only contacts db on first execution.

        :return: Number of retailers in Polaris.
        """

        if not self.account_holder_count:
            with psycopg2.connect(self.polaris_connection_string) as polaris_connection:
                with polaris_connection.cursor() as cursor:
                    query = "SELECT count(*) from account_holder;"
                    cursor.execute(query)
                    results = cursor.fetchone()

                    self.account_holder_count = int(results[0])

            polaris_connection.close()

        return self.account_holder_count

    def get_headers(self) -> dict:

        for key, value in self.all_secrets.items():
            if key not in self.headers:
                self.headers[key] = {}

            self.headers[key].update(
                {
                    "Authorization": f"token {value}",
                    "bpl-user-channel": "foo",
                }
            )

        return self.headers

    @staticmethod
    def account_holder_gen(array: list[AccountHolder]) -> Generator[AccountHolder, None, None]:
        index = 0
        while True:
            yield array[index]
            if index < len(array) - 1:
                index += 1
            else:
                index = 0

    def set_initial_starting_pk(self) -> None:
        self.redis.set("pyxis_starting_pk", 1)

    def get_and_increment_starting_pk(self, increment: int) -> int:
        max_id = self.get_polaris_account_holder_count()
        starting_pk = int(self.redis.get("pyxis_starting_pk") or "1")

        if starting_pk + increment > max_id:  # If we get to the end of the account_holder table, restart at 1.
            starting_pk = 1

        self.redis.set("pyxis_starting_pk", starting_pk + increment)

        return starting_pk

    # pylint: disable=too-many-locals
    def fetch_preloaded_account_holder_information(self, number_of_accounts: int = 1) -> list[AccountHolder]:
        """
        Tries to get account holder information directly from polaris in a retry loop.

        :param number_of_accounts: number of accounts to be fetched. Defaults to 1.
        :return: dictionary of {account_holder_email: {account_number: 1234, account_holder_uuid: 1a2b3c}}.
        """

        starting_pk = self.get_and_increment_starting_pk(number_of_accounts)

        id_fetch_list = list(range(starting_pk, starting_pk + number_of_accounts))

        all_account_holders = []

        self.logger.info(f"Fetching account information for ids: {id_fetch_list}")

        with psycopg2.connect(self.polaris_connection_string) as polaris_connection:
            with polaris_connection.cursor() as cursor:

                query = (
                    "SELECT email, account_number, account_holder_uuid, retailer_id, id "
                    "FROM account_holder "
                    "WHERE id IN %s;"
                )

                try:
                    cursor.execute(query, (tuple(id_fetch_list),))
                    results = cursor.fetchall()
                except Exception as ex:
                    raise StopUser("Unable to direct fetch account_holder information from db") from ex

                for email, account_number, account_holder_uuid, retailer_id, account_holder_id in results:

                    account_holder = AccountHolder(
                        email=email,
                        account_number=account_number,
                        account_holder_uuid=account_holder_uuid,
                        retailer=retailer_id,
                        account_holder_id=account_holder_id,
                    )
                    all_account_holders.append(account_holder)

        polaris_connection.close()

        return all_account_holders


locust_handler = LocustHandler()


def repeatable_task() -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @task
        def wrapper(*args: Any, **kwargs: Any) -> bool:
            num = locust_handler.repeat_tasks.get(func.__name__, 0)
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator
