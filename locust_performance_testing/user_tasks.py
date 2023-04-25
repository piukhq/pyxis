import logging
import random
import time

from datetime import datetime
from random import randint
from typing import TYPE_CHECKING, Generator
from uuid import uuid4

from faker import Faker
from locust import SequentialTaskSet
from locust.exception import StopUser

from locust_performance_testing.helpers import AccountHolder, locust_handler, repeatable_task
from settings import ACCOUNTS_API_URL, LUNA_API_URL, PUBLIC_API_URL, TRANSACTIONS_API_URL

if TYPE_CHECKING:
    from locust import HttpUser


class UserTasks(SequentialTaskSet):
    """
    User behaviours for the BPL performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be run a number of times, as defined in the locustfile which instantiates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator, and must also be included in the 'repeats'
    dictionary in the parent locustfile.
    """

    account_holders: Generator[AccountHolder, None, None]

    def __init__(self, parent: "HttpUser") -> None:
        super().__init__(parent)
        self.url_prefix = "api"
        self.keys = locust_handler.load_secrets()
        self.headers = locust_handler.get_headers()
        self.retailer_slug = f"retailer_{random.randint(1, locust_handler.get_retailer_count())}"
        self.fake = Faker()
        self.account_number = ""
        self.account_uuid = ""
        self.now = int(datetime.timestamp(datetime.now()))
        self.accounts: list[AccountHolder] = []
        self.begin_time: float = time.time()

    # ---------------------------------POLARIS ENDPOINTS---------------------------------

    def on_start(self) -> None:
        repeats = locust_handler.repeat_tasks

        # We get a 'group' of account_holders from the db equal to the number of transactions for this user, as we
        # ideally want to send 1 transaction per account holder.

        accounts_to_fetch = repeats["post_transaction"]

        accounts = locust_handler.fetch_preloaded_account_holder_information(accounts_to_fetch)

        self.account_holders = locust_handler.account_holder_gen(accounts)

    @repeatable_task()
    def post_account_holder(self) -> None:
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        email = f"{first_name}_{last_name}_{str(self.fake.pyint())[:5]}@performance.com".lower()

        data = {
            "credentials": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": "010101",
                "phone": "000000000000",
                "address_line1": "address1",
                "address_line2": "address2",
                "postcode": "pe000rf",
                "city": "Performanceville",
            },
            "marketing_preferences": [{"key": "marketing_pref", "value": True}],
            "callback_url": f"{LUNA_API_URL}/enrol/callback/success",
            "third_party_identifier": "perf",
        }

        self.client.post(
            f"{ACCOUNTS_API_URL}{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/enrolment",
            json=data,
            headers=self.headers["accounts_api_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/enrolment",
        )

    @repeatable_task()
    def post_get_by_credentials(self) -> None:
        account: AccountHolder = next(self.account_holders, None)
        if not account:
            raise ValueError(f"no more accounts in {self.__class__.__name__}.account_holders")

        data = {"email": account.email, "account_number": account.account_number}

        self.client.post(
            f"{ACCOUNTS_API_URL}{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/getbycredentials",
            json=data,
            headers=self.headers["accounts_api_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/getbycredentials",
        )

    @repeatable_task()
    def get_account(self) -> None:
        account: AccountHolder = next(self.account_holders)

        self.client.get(
            f"{ACCOUNTS_API_URL}{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/{account.account_holder_uuid}",
            headers=self.headers["accounts_api_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    @repeatable_task()
    def get_marketing_unsubscribe(self) -> None:
        account: AccountHolder = next(self.account_holders)

        self.client.get(
            f"{PUBLIC_API_URL}{self.url_prefix}/public/retailer_{account.retailer}/marketing/unsubscribe?u="
            f"{account.opt_out_token}",
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/marketing/unsubscribe?u=<account_uuid>",
        )

    @repeatable_task()
    def post_transaction(self) -> None:
        account: AccountHolder = next(self.account_holders)

        data = {
            "id": f"TX{uuid4()}",
            "transaction_total": random.randint(100, 400),
            "transaction_id": f"BPL123456789{randint(1, 20000)}",
            "datetime": self.now,
            "MID": "1234",
            "loyalty_id": account.account_holder_uuid,
        }

        self.client.post(
            f"{TRANSACTIONS_API_URL}{self.url_prefix}/transactions/retailer_{account.retailer}",
            headers=self.headers["transactions_api_key"],
            json=data,
            name=f"{self.url_prefix}/retailers/<retailer_slug>/transaction",
        )

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self) -> None:
        logger = logging.getLogger("UserTimer")
        logger.info(f"User completed all tasks in {time.time() - self.begin_time} seconds.")
        raise StopUser()
