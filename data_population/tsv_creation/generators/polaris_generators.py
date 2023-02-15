import json
import math
import uuid

from datetime import datetime, timedelta
from random import choice, randint

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.polaris import (
    TX_EARNED_DATA,
    AccountHolderStatuses,
    marketing_preferences,
    profile_config,
)
from settings import fake


class PolarisGenerators:
    def __init__(self, data_config: DataConfig, account_holder_uuids: list[uuid.UUID]) -> None:
        self.now = datetime.utcnow()
        self.data_config = data_config
        self.all_account_holder_retailers: dict = {}
        self.allocated_rewards: list = []
        self.unallocated_rewards: list = []
        self.account_holders_by_retailer: dict = {}
        self.account_holder_uuids = account_holder_uuids

    def get_account_holders_by_retailer(self) -> dict:
        if not self.account_holders_by_retailer:
            for retailer in range(1, self.data_config.retailers + 1):
                self.account_holders_by_retailer[retailer] = [
                    k for k, v in self.all_account_holder_retailers.items() if v == retailer
                ]

        return self.account_holders_by_retailer

    def retailer_config(self) -> list:
        """Generates n retailer_configs (n defined in data_config)"""
        return [
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
                "ACTIVE",  # status
                0,  # balance_lifespan
                0,  # balance_reset_advanced_warning_days
            ]
            for count in range(1, self.data_config.retailers + 1)
        ]

    def account_holder(self) -> list:
        """Generates n account_holders (n defined in data_config)"""

        account_holders = []
        for count in range(1, self.data_config.account_holders + 1):
            account_id = count
            account_holder_uuid = self.account_holder_uuids.pop()
            retailer_id = randint(1, self.data_config.retailers)
            account_holders.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_id,  # id
                    f"user_{account_id}@performancetest.com",  # email
                    AccountHolderStatuses.ACTIVE,  # status
                    f"{fake.credit_card_number()}_{account_id}",  # account_number
                    retailer_id,  # retailer_id
                    account_holder_uuid,  # account_holder_uuid
                    uuid.uuid4(),  # opt_out_token
                ]
            )
            self.all_account_holder_retailers[account_id] = retailer_id

        return account_holders

    def account_holder_profile(self) -> list:
        """Generates n account_holder_profiles (n defined in data_config (1-1 w/account_holders))"""
        return [
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
            for count in range(1, self.data_config.account_holders + 1)
        ]

    def account_holder_marketing_preference(self) -> list:
        """Generates account_holder_marketing_preferences (n defined in data_config (1-1 w/account_holders))"""
        return [
            [
                self.now,  # created_at
                self.now,  # updated_at
                count,  # id
                count,  # account_holder_id
                "marketing_pref",  # key_name
                "True",  # value
                "BOOLEAN",  # value_type
            ]
            for count in range(1, self.data_config.account_holders + 1)
        ]

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
                    self.now + timedelta(days=30),  # reset_date
                ]
            )
        return account_holder_campaign_balances

    def account_holder_reward(self) -> list:
        """
        Generates account_holder_rewards (1-1 w/ data_config.allocated_rewards)
        """
        account_holder_rewards = []
        account_holders_by_retailer = self.get_account_holders_by_retailer()
        total_campaigns = self.data_config.campaigns_per_retailer * self.data_config.retailers
        rewards_per_campaign = math.ceil(self.data_config.allocated_rewards / total_campaigns)
        reward_id = id_generator(1)

        for campaign_count in range(1, total_campaigns + 1):
            for _ in range(1, rewards_per_campaign + 1):

                reward = self.allocated_rewards.pop()

                account_holder_rewards.append(
                    [
                        self.now,  # created_at
                        self.now,  # updated_at
                        next(reward_id),  # id
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
                        f"campaign_{campaign_count}",  # campaign_slug
                    ]
                )
        return account_holder_rewards

    def account_holder_pending_reward(self) -> list:
        """
        Generates account_holder_pending_rewards (1-1 w/ data_config.pending_rewards)
        """

        account_holder_pending_rewards = []
        account_holders_by_retailer = self.get_account_holders_by_retailer()
        pending_reward_value = 500
        if self.data_config.pending_reward_conversion:
            conversion_date = self.now + timedelta(days=-1)
        else:
            conversion_date = self.now + timedelta(days=1)

        for reward_count in range(1, self.data_config.pending_rewards + 1):

            reward = self.unallocated_rewards.pop()
            account_holder_pending_rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    reward_count,  # id
                    self.now,  # created_date
                    conversion_date,  # conversion_date
                    pending_reward_value,  # value
                    f"campaign_{reward['retailer_id'] * self.data_config.campaigns_per_retailer}",  # campaign_slug
                    f"reward_{reward['reward_config_id']}",  # reward_slug
                    f"retailer_{reward['retailer_id']}",  # retailer_slug
                    str(uuid.uuid4()),  # idempotency_token
                    choice(account_holders_by_retailer[reward["retailer_id"]]),  # account_holder_id
                    False,  # enqueued
                    1,  # count
                    pending_reward_value,  # total_cost_to_user
                    str(uuid.uuid4()),  # pending_reward_uuid
                ]
            )
        return account_holder_pending_rewards

    def balance_adjustment(self) -> list:
        """
        Generates balance_adjustment rows (1-1 w/ data_config.transactions)
        """

        return [
            [
                count,  # id
                f"token_{count}",  # token
                randint(500, 1000),  # adjustment
                self.now,  # created_at
                randint(1, self.data_config.account_holders),  # account_holder_id
            ]
            for count in range(1, self.data_config.transactions + 1)
        ]

    def email_template(self) -> list:
        """
        Generates email_template rows (2-1 w/ data_config.retails)
        Different email templates for each retailer
        """

        email_templates: list = []
        row_id = id_generator(1)
        template_id = id_generator(1)

        for template_type in ("WELCOME_EMAIL", "REWARD_ISSUANCE"):
            email_templates.extend(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    next(row_id),  # id
                    next(template_id),  # template_id
                    template_type,  # type
                    count,  # retailer_id
                ]
                for count in range(1, self.data_config.retailers + 1)
            )
        return email_templates

    def account_holder_transaction_history(self) -> list:
        """
        Generates transaction history record for account holders
        """

        tx_history: list = []
        row_id = id_generator(1)

        transactions_per_account = math.ceil(self.data_config.transactions / self.data_config.account_holders)
        transaction_id = id_generator(1)

        for _ in range(1, self.data_config.transactions + 1):
            tx_history.extend(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    next(row_id),  # id
                    f"tx_{next(transaction_id)}",  # transaction_id
                    self.now,  # datetime
                    randint(500, 1000),  # amount
                    "GBP",  # amount_currency
                    "N/A",  # location_name
                    json.dumps(TX_EARNED_DATA, ensure_ascii=False),
                    account_holder_count,
                ]
                for account_holder_count in range(1, transactions_per_account + 1)
            )
        return tx_history
