import uuid

from datetime import datetime, timedelta
from random import choice, randint

from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.polaris import AccountHolderStatuses, marketing_preferences, profile_config
from settings import fake


class PolarisGenerators:
    def __init__(self, data_config: DataConfig) -> None:
        self.now = datetime.utcnow()
        self.data_config = data_config
        self.all_account_holder_retailers: dict = {}
        self.allocated_rewards: list = []
        self.unallocated_rewards: list = []
        self.account_holders_by_retailer: dict = {}

    def get_account_holders_by_retailer(self) -> dict:
        if not self.account_holders_by_retailer:
            for retailer in range(1, self.data_config.retailers + 1):
                self.account_holders_by_retailer[retailer] = [
                    k for k, v in self.all_account_holder_retailers.items() if v == retailer
                ]

        return self.account_holders_by_retailer

    def retailer_config(self) -> list:
        """Generates n retailer_configs (n defined in data_config)"""
        retailer_configs = []
        for count in range(1, self.data_config.retailers + 1):
            retailer_configs.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    count,  # id
                    f"Retailer {count}",  # name
                    f"retailer_{count}",  # slug
                    str(count).zfill(4),  # account_number_prefix (e.g. '0013')
                    10,  # account_number_length
                    profile_config,  # profile_config
                    marketing_preferences,  # marketing_preference_config
                    "Performance Retailer",  # loyalty_name
                    "",  # email_header_image
                    "Performance Retailer <welcome@performance_retailer.com>",  # welcome_email_from
                    "Welcome to Performance Retailer!",  # welcome_email_subject
                ]
            )
        return retailer_configs

    def account_holder(self) -> list:
        """Generates n account_holders (n defined in data_config)"""

        account_holders = []
        for count in range(1, self.data_config.account_holders + 1):
            account_id = count
            account_holder_uuid = uuid.uuid4()
            retailer_id = randint(1, self.data_config.retailers)
            account_holders.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_id,  # id
                    f"user_{count}@performancetest.com",  # email
                    AccountHolderStatuses.ACTIVE,  # status
                    f"{fake.credit_card_number()}_{count}",  # account_number
                    retailer_id,  # retailer_id
                    account_holder_uuid,  # account_holder_uuid
                    uuid.uuid4(),  # opt_out_token
                ]
            )
            self.all_account_holder_retailers[account_id] = retailer_id

        return account_holders

    def account_holder_profile(self) -> list:
        """Generates n account_holder_profiles (n defined in data_config (1-1 w/account_holders))"""
        account_holder_profiles = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holder_profiles.append(
                [
                    count,  # id
                    fake.first_name(),  # first name
                    fake.last_name(),  # surname
                    self.now,  # date_of_birth
                    "01234567891",  # phone
                    "Fake_first_line_address",  # address_line1
                    "Fake_second_line_address",  # address_line2
                    "Fake_postcode",  # postcode
                    "Fake_city",  # city
                    count,  # account_holder_id
                    "",  # custom
                ]
            )
        return account_holder_profiles

    def account_holder_marketing_preference(self) -> list:
        """Generates account_holder_marketing_preferences (n defined in data_config (1-1 w/account_holders))"""
        account_holder_marketing_preferences = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holder_marketing_preferences.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    count,  # id
                    count,  # account_holder_id
                    "marketing_pref",  # key_name
                    "True",  # value
                    "BOOLEAN",  # value_type
                ]
            )
        return account_holder_marketing_preferences

    def account_holder_campaign_balance(self) -> list:
        """Generates account_holder_campaign_balances (n defined in data_config (1-1 w/account_holders))"""
        account_holder_campaign_balances = []
        for account_holder_id in range(1, self.data_config.account_holders + 1):

            retailer_id = self.all_account_holder_retailers[account_holder_id]
            campaign_slug = f"campaign_{retailer_id * self.data_config.campaigns_per_retailer}"

            account_holder_campaign_balances.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_id,  # id
                    account_holder_id,  # account_holder_id
                    campaign_slug,  # campaign_slug
                    0,  # balance
                ]
            )
        return account_holder_campaign_balances

    def account_holder_reward(self) -> list:
        """
        Generates account_holder_rewards (1-1 w/ data_config.allocated_rewards)
        """
        account_holder_rewards = []
        account_holders_by_retailer = self.get_account_holders_by_retailer()

        for reward_count in range(1, self.data_config.allocated_rewards + 1):

            reward = self.allocated_rewards.pop()

            account_holder_rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    reward_count,  # id
                    reward["reward_uuid"],  # reward_uuid
                    reward["code"],  # code
                    self.now,  # issued_date
                    self.now + timedelta(days=30),  # expiry_date
                    choice(["ISSUED", "CANCELLED", "REDEEMED"]),  # status
                    "NULL",  # redeemed_date
                    "NULL",  # cancelled_date
                    f"reward_{reward['reward_config_id']}",  # reward_slug
                    f"retailer_{reward['retailer_id']}",  # retailer_slug
                    str(uuid.uuid4()),  # idempotency_token
                    choice(account_holders_by_retailer[reward["retailer_id"]]),  # account_holder_id
                    "",  # associated_url
                ]
            )
        return account_holder_rewards

    def account_holder_pending_reward(self) -> list:
        """
        Generates account_holder_pending_rewards (1-1 w/ data_config.pending_rewards)
        """

        account_holder_pending_rewards = []
        account_holders_by_retailer = self.get_account_holders_by_retailer()

        for reward_count in range(1, self.data_config.pending_rewards + 1):

            reward = self.unallocated_rewards.pop()

            account_holder_pending_rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    reward_count,  # id
                    self.now,  # created_date
                    self.now + timedelta(days=-1),  # conversion_date
                    randint(500, 1000),  # value
                    f"campaign_{reward['retailer_id'] * self.data_config.campaigns_per_retailer}",  # campaign_slug
                    f"reward_{reward['reward_config_id']}",  # reward_slug
                    f"retailer_{reward['retailer_id']}",  # retailer_slug
                    str(uuid.uuid4()),  # idempotency_token
                    choice(account_holders_by_retailer[reward["retailer_id"]]),  # account_holder_id
                ]
            )
        return account_holder_pending_rewards
