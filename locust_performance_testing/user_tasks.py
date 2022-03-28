import random
import time

from datetime import datetime

from faker import Faker
from locust import SequentialTaskSet, task
from locust.exception import StopUser

from locust_performance_testing.helpers import (
    get_account_holder_information_via_cursor,
    get_headers,
    get_polaris_retailer_count,
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
        self.accounts_to_fetch = []
        self.accounts = {}

    # ---------------------------------POLARIS ENDPOINTS---------------------------------

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

        with self.client.post(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/enrolment",
            json=data,
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/enrolment",
        ) as response:

            if response.status_code == 202:
                self.accounts_to_fetch.append(email)

    @task
    def update_account_information(self):
        """
        Helper function to populate account data by direct db query (replaces BPL callback)
        """
        t = time.time()
        self.accounts = get_account_holder_information_via_cursor(self.accounts_to_fetch, 10, 0.5)
        print(f"Fetched data {self.accounts} in {time.time()-t} seconds.")

    @repeatable_task()
    def post_get_by_credentials(self) -> None:

        data = {"email": self.email, "account_number": self.account_number}

        self.client.post(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/getbycredentials",
            json=data,
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/getbycredentials",
        )

    @repeatable_task()
    def get_account(self) -> None:

        self.client.get(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    @repeatable_task()
    def get_marketing_unsubscribe(self) -> None:

        self.client.get(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/marketing/unsubscribe?u={self.account_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/marketing/unsubscribe?u=<account_uuid>",
        )

    @repeatable_task()
    def post_transaction(self) -> None:

        data = {
            "id": f"TX{self.fake.pyint()}",
            "transaction_total": random.randint(1000, 9999),
            "datetime": self.now,
            "MID": "1234",
            "loyalty_id": self.account_uuid,
        }

        self.client.post(
            f"{self.url_prefix}/retailers/{self.retailer_slug}/transaction",
            headers=self.headers["vela_key"],
            json=data,
            name=f"{self.url_prefix}/retailers/<retailer_slug>/transaction",
        )

    #  endpoint not yet implemented but leaving for later
    @repeatable_task()
    def delete_account(self) -> None:

        self.client.delete(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self) -> None:
        raise StopUser()
