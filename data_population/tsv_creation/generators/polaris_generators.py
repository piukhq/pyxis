import uuid

from datetime import datetime, timedelta
from random import choice, randint

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.polaris import (
    AccountHolderStatuses,
    generate_polaris_type_key_values,
    marketing_preferences,
    polaris_task_type_ids,
    profile_config,
)
from data_population.tsv_creation.generators.task_generators import retry_task, task_type_key_value
from settings import fake


class PolarisGenerators:
    def __init__(self, data_config: DataConfig) -> None:
        self.now = datetime.utcnow()
        self.data_config = data_config

    def retailer_config(self, start: int, stop: int) -> list:
        """Generates n retailer_configs (n defined in data_config)"""
        retailer_configs = []
        for retailer_count in range(start, stop + 1):
            retailer_configs.append(
                [
                    retailer_count,  # id
                    f"Retailer {retailer_count}",  # name
                    f"retailer_{retailer_count}",  # slug
                    str(retailer_count).zfill(4),  # account_number_prefix (e.g. '0013')
                    10,  # account_number_length
                    self.now,  # created_at
                    profile_config,  # profile_config
                    self.now,  # updated_at
                    marketing_preferences,  # marketing_preference
                    "Performance Retailer",  # loyalty_name
                    "",  # email_header_image
                    "Performance Retailer <welcome@performance_retailer.com>",  # welcome_email_from
                    "Welcome to Performance Retailer!",  # welcome_email_subject
                ]
            )
        return retailer_configs

    def account_holder(self, start: int, stop: int) -> list:
        """Generates n account_holders (n defined in data_config)"""
        account_holders = []
        for account_holder_count in range(start, stop + 1):
            account_holders.append(
                [
                    f"user_{account_holder_count}@performancetest.com",  # email
                    AccountHolderStatuses.ACTIVE,  # status
                    f"{fake.credit_card_number()}_{account_holder_count}",  # account_number
                    self.now,  # created_at
                    randint(1, self.data_config.retailers),  # retailer_id
                    self.now,  # updated_at
                    uuid.uuid4(),  # account_holder_uuid
                    account_holder_count,  # id
                    uuid.uuid4(),  # opt_out_token
                ]
            )
        return account_holders

    def account_holder_profile(self, start: int, stop: int) -> list:
        """Generates n account_holder_profiles (n defined in data_config (1-1 w/account_holders))"""
        account_holder_profiles = []
        for account_holder_count in range(start, stop + 1):
            account_holder_profiles.append(
                [
                    fake.first_name(),  # first name
                    fake.last_name(),  # surname
                    self.now,  # date_of_birth
                    "01234567891",  # phone
                    "Fake_first_line_address",  # address_line1
                    "Fake_second_line_address",  # address_line2
                    "Fake_postcode",  # retailer_id
                    "Fake_city",  # city
                    account_holder_count,  # account_holder_id
                    account_holder_count,  # id
                    "",  # custom
                ]
            )
        return account_holder_profiles

    def account_holder_marketing_preference(self, start: int, stop: int) -> list:
        """Generates account_holder_marketing_preferences (n defined in data_config (1-1 w/account_holders))"""
        account_holder_marketing_preferences = []
        for account_holder_count in range(start, stop + 1):
            account_holder_marketing_preferences.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_count,  # id
                    account_holder_count,  # account_holder_id
                    "marketing_pref",  # key_name
                    "True",  # value
                    "BOOLEAN",  # value_type
                ]
            )
        return account_holder_marketing_preferences

    def account_holder_campaign_balance(self, start: int, stop: int) -> list:
        """Generates account_holder_campaign_balances (n defined in data_config (1-1 w/account_holders))"""
        account_holder_campaign_balances = []
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer
        for account_holder_count in range(start, stop + 1):
            account_holder_campaign_balances.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_count,  # id
                    f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
                    randint(100, 1000),  # balance
                    account_holder_count,  # account_holder_id
                ]
            )
        return account_holder_campaign_balances

    def account_holder_reward(self, start: int, stop: int) -> list:
        """
        Generates account_holder_rewards (1-1 w/ account_holders)
        """
        account_holder_rewards = []
        total_retailers = self.data_config.retailers  # 10

        for account_holder_count in range(start, stop + 1):

            account_holder_rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    str(uuid.uuid4()),  # reward_uuids
                    random_ascii(),  # code
                    self.now,  # issued_date
                    self.now + timedelta(days=30),  # expiry_date
                    choice(["ISSUED", "CANCELLED", "REDEEMED"]),  # status
                    self.now,
                    self.now,
                    "perftest-reward-slug",  # reward_slug
                    f"retailer_{randint(1, total_retailers)}",  # retailer_slug
                    str(uuid.uuid4()),  # idempotency_token
                    account_holder_count,  # account_holder_id
                    account_holder_count,  # id
                ]
            )
        return account_holder_rewards

    def account_holder_pending_reward(self, start: int, stop: int) -> list:
        """
        Generates account_holder_pending_rewards (1-1 w/ account_holders)
        """
        account_holder_pending_rewards = []
        total_retailers = self.data_config.retailers
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer

        for account_holder_count in range(start, stop + 1):
            account_holder_pending_rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_count,  # id
                    self.now,  # created_date
                    self.now + timedelta(days=30),  # conversion_date
                    randint(500, 1000),  # value
                    f"campaign_{randint(1,total_campaigns)}",
                    f"reward_{randint(1,total_campaigns)}",  # reward_slug
                    f"retailer_{randint(1, total_retailers)}",  # retailer_slug
                    str(uuid.uuid4()),  # idempotency_token
                    account_holder_count,  # account_holder_id
                ]
            )
        return account_holder_pending_rewards

    @staticmethod
    def retry_task(start: int, stop: int) -> list:
        """Generates retry_tasks (1-1 w/ transactions in data config)"""
        return retry_task(start=start, stop=stop, task_type_ids_dict=polaris_task_type_ids)

    def task_type_key_value(self, start: int, stop: int) -> list:
        """Generates task_type_key_value data"""
        return task_type_key_value(
            start=start,
            stop=stop,
            task_type_ids_dict=polaris_task_type_ids,
            task_type_keys_dict=generate_polaris_type_key_values(self.data_config),
            random_task_types=self.data_config.random_task_types,
        )
