import logging
import time

from datetime import datetime
from random import randint
from typing import TYPE_CHECKING, Generator
from uuid import uuid4

from faker import Faker
from locust import SequentialTaskSet, tag
from locust.exception import StopUser

from locust_performance_testing.helpers import AccountHolder, locust_handler, repeatable_task

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
        self.url_prefix = ""
        self.keys = locust_handler.load_secrets()
        self.headers = locust_handler.get_headers()
        self.retailer_slug = f"retailer_{randint(1, locust_handler.get_polaris_retailer_count())}"
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

        accounts_to_fetch = repeats["post_transaction"] or repeats["post_transaction_with_trc"]

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

        account: AccountHolder = next(self.account_holders, None)
        if not account:
            raise ValueError(f"no more accounts in {self.__class__.__name__}.account_holders")

        data = {"email": account.email, "account_number": account.account_number}

        self.client.post(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/getbycredentials",
            json=data,
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/getbycredentials",
        )

    @repeatable_task()
    def get_account(self) -> None:

        account: AccountHolder = next(self.account_holders)

        self.client.get(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/accounts/{account.account_holder_uuid}",
            headers=self.headers["polaris_key"],
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/accounts/<account_uuid>",
        )

    @repeatable_task()
    def get_marketing_unsubscribe(self) -> None:

        account: AccountHolder = next(self.account_holders)

        self.client.get(
            f"{self.url_prefix}/loyalty/retailer_{account.retailer}/marketing/unsubscribe?u="
            f"{account.opt_out_token}",
            name=f"{self.url_prefix}/loyalty/<retailer_slug>/marketing/unsubscribe?u=<account_uuid>",
        )

    @tag("post_random_transaction")
    @repeatable_task()
    def post_transaction(self) -> None:
        """This user task sends a transaction with an amount which meets the reward goal"""

        account: AccountHolder = next(self.account_holders)

        data = {
            "id": f"TX{uuid4()}",
            "transaction_total": randint(500, 1000),
            "transaction_id": f"BPL123456789{randint(1, 20000)}",
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

    @tag("trc_and_refund")
    @repeatable_task()
    def post_transaction_with_trc(self) -> None:
        """This user task sends a transaction with an amount which meets the reward goal
        a sufficient amount of times to reach a transaction reward cap (trc)
        and must only be included in the test where a reward cap is in place in reward_rule table
        """

        account: AccountHolder = next(self.account_holders)

        data = {
            "id": f"TX{uuid4()}",
            "transaction_total": 2000,
            "transaction_id": f"BPL123456789{randint(1, 20000)}",
            "datetime": self.now,
            "MID": "1234",
            "loyalty_id": account.account_holder_uuid,
        }

        self.client.post(
            f"{self.url_prefix}/retailers/retailer_{account.retailer}/transaction",
            headers=self.headers["vela_key"],
            json=data,
            name="transaction_with_trc",
        )

    @tag("trc_and_refund")
    @repeatable_task()
    def post_transaction_with_refund(self) -> None:
        """This user task sends a negative transaction with an amount big enough to trigger
        polaris API to absorb pending rewards + account holder campaign balance in order to meet
        the refund amount. Must only be run where data population is setup for ACCUMULATOR campaign
        """

        account: AccountHolder = next(self.account_holders)

        data = {
            "id": f"TX{uuid4()}",
            "transaction_total": -10000,
            "transaction_id": f"BPL123456789{randint(1, 20000)}",
            "datetime": self.now,
            "MID": "1234",
            "loyalty_id": account.account_holder_uuid,
        }

        self.client.post(
            f"{self.url_prefix}/retailers/retailer_{account.retailer}/transaction",
            headers=self.headers["vela_key"],
            json=data,
            name="refund_transaction",
        )

    #  endpoint not yet implemented but leaving for later
    @repeatable_task()
    def delete_account(self) -> None:

        account: AccountHolder = next(self.account_holders)

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
