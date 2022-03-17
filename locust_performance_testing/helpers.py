import logging
import time

from functools import wraps

import psycopg2

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from locust import task
from locust.exception import StopUser

from settings import DB_CONNECTION_URI, POLARIS_AUTH_KEY_NAME, VAULT_URL, VELA_AUTH_KEY_NAME

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

        credential = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_interactive_browser_credential=True,
        )

        client = SecretClient(vault_url=VAULT_URL, credential=credential)

        logger.info(f"Attempting to load secrets [{POLARIS_AUTH_KEY_NAME}], [{VELA_AUTH_KEY_NAME}]")
        all_secrets.update(
            {
                "polaris_key": client.get_secret(POLARIS_AUTH_KEY_NAME).value,
                "vela_key": client.get_secret(VELA_AUTH_KEY_NAME).value,
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

        connection = DB_CONNECTION_URI.replace("DATABASE", "polaris")

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


def get_account_holder_information_via_cursor(email: str, timeout: int, retry_period: float) -> tuple[str, str]:
    """
    Tries to get account holder information directly from polaris in a retry loop.

    :param email: account holder email
    :param timeout: maximum amount of time for which we continue to ask for information from the db
    :param retry_period: frequency of database query
    :return: account number, account holder uuid if account is found within timeout period. Else returns empty strings.
    """
    connection = DB_CONNECTION_URI.replace("DATABASE", "polaris")

    with psycopg2.connect(connection) as connection:
        with connection.cursor() as cursor:

            total_retry_time = 0

            while total_retry_time <= timeout:

                query = "SELECT account_number, account_holder_uuid, email from account_holder WHERE email = %s ;"

                try:
                    cursor.execute(query, (email,))
                    results = cursor.fetchone()
                except Exception:
                    raise StopUser("Unable to direct fetch account_holder information from db")

                if None not in results:  # need to test that all fields are populated
                    return results[0], results[1]

                if total_retry_time >= timeout:
                    logger.info(
                        f"Timeout ({timeout})s on direct fetch of account_holder information with email {email}"
                    )
                time.sleep(retry_period)
                total_retry_time += retry_period  # type: ignore

            return "", ""  # only if timeout occurs
