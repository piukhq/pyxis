import logging
import time

from functools import wraps

import psycopg2

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from locust import task
from locust.exception import StopUser

import settings as s

repeat_tasks: dict = {}  # value assigned by locustfile

all_secrets: dict = {}  # value assigned by load_secrets()
retailer_count = None  # value assigned by get_polaris_retailer_count()

headers: dict = {}  # value assigned by get_headers()

logger = logging.getLogger("LocustHandler")


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


def get_account_holder_information_via_cursor(all_accounts_to_fetch: list, timeout: int, retry_period: float) -> dict:
    """
    Tries to get account holder information directly from polaris in a retry loop.

    :param email: account holder email
    :param timeout: maximum amount of time for which we continue to ask for information from the db
    :param retry_period: frequency of database query
    :return: account number, account holder uuid if account is found within timeout period. Else returns empty strings.
    """
    logger.info(f"Fetching accounts {all_accounts_to_fetch}")

    accounts_to_fetch = all_accounts_to_fetch
    account_data = {}

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
                    print(result)
                    if result[1] is not None and result[2] is not None:
                        # need to ensure we have both account_number and account_holder_uuid
                        email = result[0]
                        account_number = result[1]
                        account_holder_id = result[2]
                        account_data.update(
                            {
                                email: {
                                    "account_number": account_number,
                                    "account_holder_uuid": account_holder_id
                                }
                            }
                        )

                        accounts_to_fetch.remove(email)

                time.sleep(retry_period)
                total_retry_time += retry_period  # type: ignore

                if total_retry_time >= timeout:
                    logger.info(
                        f"Timeout ({timeout})s on direct fetch of account_holder information with emails: {accounts}"
                    )  # only if timeout occurs

            return account_data
