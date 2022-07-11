import logging

from collections.abc import Iterator
from dataclasses import dataclass
from functools import wraps

import psycopg2
import redis

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from locust import task
from locust.exception import StopUser

import settings as s

repeat_tasks: dict = {}  # value assigned by locustfile

all_secrets: dict = {}  # value assigned by load_secrets()
retailer_count: int | None = None  # value assigned by get_polaris_retailer_count()
account_holder_count: int | None = None

headers: dict = {}  # value assigned by get_headers()

logger = logging.getLogger("LocustHandler")

r = redis.from_url(s.REDIS_URL)

polaris_connection_string: str = s.DB_CONNECTION_URI.replace("/postgres?", f"/{s.POLARIS_DB}?")


def repeatable_task():  # type: ignore
    def decorator(func):  # type: ignore
        @wraps(func)
        @task
        def wrapper(*args, **kwargs):  # type:ignore
            num = repeat_tasks.get(func.__name__, 0)
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


def set_task_repeats(repeats: dict) -> None:
    global repeat_tasks
    repeat_tasks = repeats


def get_task_repeats() -> dict:
    global repeat_tasks
    return repeat_tasks


def load_secrets() -> dict:
    global all_secrets

    if not all_secrets:
        logger = logging.getLogger("VaultHandler")

        client = SecretClient(vault_url=s.VAULT_URL, credential=DefaultAzureCredential())

        logger.info(f"Attempting to load secrets [{s.POLARIS_AUTH_KEY_NAME}], [{s.VELA_AUTH_KEY_NAME}]")
        all_secrets.update(
            {
                "polaris_key": client.get_secret(s.POLARIS_AUTH_KEY_NAME).value,
                "vela_key": client.get_secret(s.VELA_AUTH_KEY_NAME).value,
            }
        )
        logger.info("Successfully loaded secrets")

    return all_secrets


def get_polaris_retailer_count() -> int:
    """
    Returns current retailer count in Polaris. Only contacts db on first execution.

    :return: Number of retailers in Polaris.
    """
    global retailer_count

    if not retailer_count:
        with psycopg2.connect(polaris_connection_string) as polaris_connection:
            with polaris_connection.cursor() as cursor:
                query = "SELECT count(*) from retailer_config;"
                cursor.execute(query)
                results = cursor.fetchone()

                retailer_count = int(results[0])

        polaris_connection.close()

    return retailer_count


def get_polaris_account_holder_count() -> int:
    """
    Returns current retailer count in Polaris. Only contacts db on first execution.

    :return: Number of retailers in Polaris.
    """
    global account_holder_count

    if not account_holder_count:
        with psycopg2.connect(polaris_connection_string) as polaris_connection:
            with polaris_connection.cursor() as cursor:
                query = "SELECT count(*) from account_holder;"
                cursor.execute(query)
                results = cursor.fetchone()

                account_holder_count = int(results[0])

        polaris_connection.close()

    return account_holder_count


def get_headers() -> dict:
    global headers
    global all_secrets

    if not headers:
        headers = {}

        for key_name in all_secrets.keys():
            headers[key_name] = {}
            headers[key_name].update(
                {
                    "Authorization": f"token {all_secrets[key_name]}",
                    "bpl-user-channel": "foo",
                }
            )

    return headers


@dataclass
class AccountHolder:
    email: str
    account_number: str
    account_holder_uuid: str
    retailer: int
    account_holder_id: int
    marketing: bool = True


def account_holder_gen(array: list[AccountHolder]) -> Iterator[AccountHolder]:
    index = 0
    while True:
        yield array[index]
        if index < len(array) - 1:
            index += 1
        else:
            index = 0


def set_initial_starting_pk() -> None:
    r.set("pyxis_starting_pk", 1)


def get_and_increment_starting_pk(increment: int) -> int:

    max_id = get_polaris_account_holder_count()

    starting_pk = int(r.get("pyxis_starting_pk").decode())  # type: ignore

    if starting_pk + increment > max_id:  # If we get to the end of the account_holder table, restart at 1.
        starting_pk = 1

    r.set("pyxis_starting_pk", starting_pk + increment)

    return starting_pk


def fetch_preloaded_account_holder_information(number_of_accounts: int = 1) -> list[AccountHolder]:
    """
    Tries to get account holder information directly from polaris in a retry loop.

    :param number_of_accounts: number of accounts to be fetched. Defaults to 1.
    :return: dictionary of {account_holder_email: {account_number: 1234, account_holder_uuid: 1a2b3c}}.
    """

    starting_pk = get_and_increment_starting_pk(number_of_accounts)

    id_fetch_list = [i for i in range(starting_pk, starting_pk + number_of_accounts)]

    all_account_holders = []

    logger.info(f"Fetching account information for ids: {id_fetch_list}")

    with psycopg2.connect(polaris_connection_string) as polaris_connection:

        with polaris_connection.cursor() as cursor:

            query = (
                "select email, account_number, account_holder_uuid, retailer_id, id from account_holder WHERE id IN %s;"
            )

            try:
                cursor.execute(query, (tuple(id_fetch_list),))
                results = cursor.fetchall()
            except Exception:
                raise StopUser("Unable to direct fetch account_holder information from db")

            for result in results:

                email = result[0]
                account_number = result[1]
                account_holder_uuid = result[2]
                retailer_id = result[3]
                account_holder_id = result[4]
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
