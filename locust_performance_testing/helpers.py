import logging
import time

from dataclasses import dataclass
from functools import wraps

import psycopg2

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from locust import task
from locust.exception import StopUser
from psycopg2 import pool

import settings as s

repeat_tasks: dict = {}  # value assigned by locustfile

all_secrets: dict = {}  # value assigned by load_secrets()
retailer_count = None  # value assigned by get_polaris_retailer_count()

headers: dict = {}  # value assigned by get_headers()

logger = logging.getLogger("LocustHandler")

try:
    polaris_connection_string = s.DB_CONNECTION_URI.replace("/postgres?", f"/{s.POLARIS_DB}?")
    polaris_connection_pool = pool.SimpleConnectionPool(1, 20, polaris_connection_string)
except Exception:
    logger.error("Failed to create PostgreSQL connection pool")


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


@dataclass
class AccountHolder:
    email: str
    account_number: str
    account_holder_uuid: str
    marketing: bool = True


def get_polaris_retailer_count() -> int:
    """
    Returns current retailer count in Polaris. Only contacts db on first execution.

    :return: Number of retailers in Polaris.
    """
    global retailer_count

    if not retailer_count:

        connection = s.DB_CONNECTION_URI.replace("/postgres?", f"/{s.POLARIS_DB}?")

        with psycopg2.connect(connection) as connection:
            with connection.cursor() as cursor:
                query = "SELECT count(*) from retailer_config;"
                cursor.execute(query)
                results = cursor.fetchone()

                retailer_count = int(results[0])

    return retailer_count


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


def get_account_holder_information_via_cursor_bulk(
    all_accounts_to_fetch: list, timeout: int, retry_period: float
) -> list[AccountHolder]:
    """
    Tries to get account holder information directly from polaris in a retry loop.

    :param all_accounts_to_fetch: array of account_holder_emails to be used as pk for data query
    :param timeout: maximum amount of time for which we continue to ask for information from the db
    :param retry_period: frequency of database query
    :return: dictionary of {account_holder_email: {account_number: 1234, account_holder_uuid: 1a2b3c}}.
    """
    logger.info(f"Fetching account information for {len(all_accounts_to_fetch)} accounts")

    t = time.time()

    accounts_to_fetch = all_accounts_to_fetch
    account_data = []

    connection = s.DB_CONNECTION_URI.replace("/postgres?", f"/{s.POLARIS_DB}?")

    with psycopg2.connect(connection) as connection:
        with connection.cursor() as cursor:

            total_retry_time = 0

            while total_retry_time < timeout and accounts_to_fetch:

                query = "SELECT email, account_number, account_holder_uuid from account_holder WHERE email IN %s ;"

                try:
                    cursor.execute(query, (tuple(accounts_to_fetch),))
                    results = cursor.fetchall()
                except Exception:
                    raise StopUser("Unable to direct fetch account_holder information from db")

                for result in results:
                    if result[1] is not None and result[2] is not None:
                        # need to ensure we have both account_number and account_holder_uuid
                        email = result[0]
                        account_number = result[1]
                        account_holder_id = result[2]
                        account_data.append(AccountHolder(email, account_number, account_holder_id))
                        accounts_to_fetch.remove(email)
                        logger.info(f"Found information for user {email} and removed from fetch list")

                time.sleep(retry_period)
                total_retry_time += retry_period  # type: ignore

                if total_retry_time >= timeout:
                    logger.info(
                        f"Timeout ({timeout})s on direct fetch of account information with remaining emails: "
                        f"{accounts_to_fetch}"
                    )  # only if timeout occurs

                if not accounts_to_fetch:
                    logger.info(f"Successfully fetched all account information from db in {time.time() - t} seconds")

            return account_data


def get_account_holder_information_via_cursor_sequential(
    email: str, timeout: int, retry_period: float
) -> AccountHolder:
    """
    Tries to get account holder information directly from polaris in a retry loop.

    :param email: account_holder_email to be used as pk for data query
    :param timeout: maximum amount of time for which we continue to ask for information from the db
    :param retry_period: frequency of database query
    :return: dictionary of {account_holder_email: {account_number: 1234, account_holder_uuid: 1a2b3c}}.
    """
    logger.info(f"Fetching account information for {email}")

    connection = polaris_connection_pool.getconn()

    with connection.cursor() as cursor:

        total_retry_time = 0

        while total_retry_time < timeout:

            query = "SELECT email, account_number, account_holder_uuid from account_holder WHERE email = %s ;"

            try:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
            except Exception:
                raise StopUser("Unable to direct fetch account_holder information from db")

            if result[1] is not None and result[2] is not None:
                # need to ensure we have both account_number and account_holder_uuid
                email = result[0]
                account_number = result[1]
                account_holder_id = result[2]
                return AccountHolder(email, account_number, account_holder_id)

            time.sleep(retry_period)
            total_retry_time += retry_period  # type: ignore

            if total_retry_time >= timeout:
                logger.info(
                    f"Timeout ({timeout})s on direct fetch of account information with email: " f"{email}"
                )  # only if timeout occurs
                return AccountHolder("", "", "")

    polaris_connection_pool.putconn(connection)  # returns connection to pool
