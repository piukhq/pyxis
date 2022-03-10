import random

from locust import SequentialTaskSet
from locust.exception import StopUser
from locust_performance_testing.helpers import (
    repeatable_task,
    load_secrets,
    get_polaris_retailer_count,
    get_headers,
    get_account_holder_information_via_cursor,
)
from faker import Faker


class UserTasks(SequentialTaskSet):
    """
    User behaviours for the BPL performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be run a number of times, as defined in the locustfile which instantiates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator, and must also be included in the 'repeats'
    dictionary in the parent locustfile.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.url_prefix = "/bpl"
        self.keys = load_secrets()
        self.headers = get_headers()
        self.retailer_slug = f"retailer_{random.randint(1, get_polaris_retailer_count())}"
        self.fake = Faker()
        self.first_name = self.fake.first_name()
        self.last_name = self.fake.last_name()
        self.email = f"{self.first_name}_{self.last_name}_{self.fake.pyint()[:5]}@performance.com"
        self.account_number = ""
        self.account_uuid = ""

    # ---------------------------------POLARIS ENDPOINTS---------------------------------

    @repeatable_task()
    def post_account_holder(self):

        data = {
            "credentials": {"email": self.email, "first_name": self.first_name, "last_name": self.last_name},
            "marketing_preferences": [],
            "callback_url": "",
            "third_party_identifier": "",
        }

        with self.client.post(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/enrolment",
            json=data,
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/enrolment",
        ) as response:

            if response.status_code == 202:
                self.account_number, self.account_uuid = get_account_holder_information_via_cursor(self.email, 10, 0.5)

    @repeatable_task()
    def post_get_by_credentials(self):

        data = {"email": self.email, "account_number": self.account_number}

        self.client.post(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/getbycredentials",
            json=data,
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/getbycredentials",
        )

    @repeatable_task()
    def get_account(self):

        self.client.get(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}",
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    @repeatable_task()
    def get_account_profile(self):

        self.client.get(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}/profile",
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>/profile",
        )

    @repeatable_task()
    def patch_account_profile(self):

        data = {
            "credentials": {
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "phone": self.fake.pyint(),
            }
        }

        self.client.patch(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}/profile",
            json=data,
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>/profile",
        )

    @repeatable_task()
    def get_marketing_unsubscribe(self):

        self.client.get(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/marketing/unsubscribe?u={self.account_uuid}",
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/marketing/unsubscribe?u=<account_uuid>",
        )

    @repeatable_task()
    def delete_account(self):

        self.client.delete(
            f"{self.url_prefix}/loyalty/{self.retailer_slug}/accounts/{self.account_uuid}",
            headers=self.headers["polaris"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self):
        raise StopUser()
