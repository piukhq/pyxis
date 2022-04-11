import logging
import random
import time

from datetime import datetime
from uuid import uuid4

from faker import Faker
from locust import SequentialTaskSet
from locust.exception import StopUser

from locust_performance_testing.helpers import (
    AccountHolder,
    fetch_preloaded_account_holder_information,
    gen,
    get_headers,
    get_polaris_retailer_count,
    get_task_repeats,
    load_secrets,
    repeatable_task,
)


class UserTasks(SequentialTaskSet):
    """
    User behaviours for the BPL performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be run a number of times, as defined in the locustfile which instantiates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator, and must also be included in the 'repeats'
    dictionary in the parent locustfile.
    """

    def __init__(self, parent) -> None:  # type: ignore
        super().__init__(parent)
        self.url_prefix = "/bpl"
        self.keys = load_secrets()
        self.headers = get_headers()
        self.retailer_slug = f"retailer_{random.randint(1, get_polaris_retailer_count())}"
        self.fake = Faker()
        self.account_number = ""
        self.account_uuid = ""
        self.now = int(datetime.timestamp(datetime.now()))
        self.accounts: list[AccountHolder] = []
        self.begin_time: float = time.time()
        self.account_holders: iter = None

    # ---------------------------------POLARIS ENDPOINTS---------------------------------

    def on_start(self):

        repeats = get_task_repeats()

        accounts_to_fetch = max(repeats["post_transaction"], repeats["get_marketing_unsubscribe"])

        accounts = fetch_preloaded_account_holder_information(accounts_to_fetch)

        self.account_holders = gen(accounts)

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
            "callback_url": "http://luna-api/enrol/callback/success",
            "third_party_identifier": "perf",
        }

        self.client.post(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/enrolment",
            json=data,
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/enrolment",
        )

    @repeatable_task()
    def post_get_by_credentials(self) -> None:

        account = next(self.account_holders)

        data = {"email": account.email, "account_number": account.account_number}

        self.client.post(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/getbycredentials",
            json=data,
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/getbycredentials",
        )

    @repeatable_task()
    def get_account(self) -> None:

        account = next(self.account_holders)

        self.client.get(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/{account.account_holder_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    @repeatable_task()
    def get_marketing_unsubscribe(self) -> None:

        account = next(self.account_holders)

        self.client.get(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/marketing/unsubscribe?u="
            f"{account.account_holder_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/marketing/unsubscribe?u=<account_uuid>",
        )

    @repeatable_task()
    def post_transaction(self) -> None:

        account = next(self.account_holders)

        data = {
            "id": f"TX{uuid4()}",
            "transaction_total": random.randint(1000, 9999),
            "datetime": self.now,
            "MID": "1234",
            "loyalty_id": account.account_holder_uuid,
        }

        self.client.post(
            f"{self.url_prefix}/retailers/retailer_{account.retailer}/transaction",
            headers=self.headers["vela_key"],
            json=data,
            name=f"{self.url_prefix}/retailers/<retailer_slug>/transaction",
        )

    #  endpoint not yet implemented but leaving for later -
    @repeatable_task()
    def delete_account(self) -> None:

        account = next(self.account_holders)

        with self.client.delete(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{account.account_holder_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        ) as response:
            if response.status_code == 200:
                self.accounts.remove(account)

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self) -> None:
        logger = logging.getLogger("UserTimer")
        logger.info(f"User completed all tasks in {time.time() - self.begin_time} seconds.")
        raise StopUser()
