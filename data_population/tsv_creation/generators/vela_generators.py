import pprint

from datetime import datetime, timedelta
from random import choice, randint
from uuid import UUID, uuid4

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig


class VelaGenerators:
    def __init__(self, data_config: DataConfig, account_holder_uuids: list[UUID]) -> None:
        self.now = datetime.utcnow()
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.retailer_ids: list = []
        self.account_holder_uuids = account_holder_uuids

    def retailer_rewards(self) -> list:
        retailers = []
        for count in range(1, self.data_config.retailers + 1):
            self.retailer_ids.append(count)
            retailers.append(
                [
                    count,  # id
                    f"retailer_{count}",  # slug
                    "ACTIVE",  # status
                ]
            )
        return retailers

    def retailer_stores(self) -> list:
        """Generates retailer store record 1-1 with retailer_rewards"""
        return [
            [
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                f"retailer_store_{count}",  # retailer store name
                f"mid_{count}",  # mid
                count,  # retailer_id
            ]
            for count in self.retailer_ids
        ]

    def campaign(self) -> list:
        """Generates campaigns (n defined in data_config as retailers * campaigns per retailer)"""
        id_gen = id_generator(1)
        campaigns = []
        for count in range(1, self.data_config.retailers + 1):
            for _ in range(1, self.data_config.campaigns_per_retailer + 1):

                campaign_id = next(id_gen, None)
                if not campaign_id:
                    raise ValueError("no campaign_id value found")

                campaigns.append(
                    [
                        campaign_id,  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        "ACTIVE",  # status
                        f"Campaign {campaign_id}",  # name
                        f"campaign_{campaign_id}",  # slug
                        count,  # retailer_id
                        self.data_config.loyalty_type,  # loyalty_type
                        self.now,  # start_date
                        self.end_date,  # end_date (set to 100 weeks in the future)
                    ]
                )
        return campaigns

    def earn_rule(self) -> list:
        """
        Generates earn_rules (n defined in data_config as retailers * campaigns per retailer * earn_rules per campaign)
        """
        id_gen = id_generator(1)

        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer
        increment = 500 if self.data_config.loyalty_type == "STAMPS" else "NULL"

        earn_rules = []
        for campaign_count in range(1, total_campaigns + 1):
            for _ in range(self.data_config.earn_rule_per_campaign):
                earn_rules.append(
                    [
                        next(id_gen),  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        100,  # threshold
                        increment,  # increment
                        1,  # increment_multiplier
                        campaign_count,  # campaign_id
                        0,  # max_amount
                    ]
                )
        return earn_rules

    def reward_rule(self) -> list:
        """Generates reward_rules (n defined in data_config as retailers * campaigns per retailer (1-1 w/campaigns))"""
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer

        reward_rules = []
        for count in range(1, total_campaigns + 1):
            reward_rules.append(
                [
                    count,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    500,  # reward_goal
                    f"reward_{count}",  # reward_slug
                    self.data_config.allocation_window,  # allocation_window
                    count,  # campaign_id
                    self.data_config.reward_cap,  # reward_cap
                ]
            )
        return reward_rules

    def transaction(self) -> list:
        """Generates transactions (n defined in n data_config)"""
        id_gen = id_generator(1)
        transactions = []
        for count in range(1, self.data_config.transactions + 1):
            transactions.append(
                [
                    next(id_gen),  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    f"tx_{count}",  # transaction_id
                    randint(500, 1000),  # amount
                    "MID_1234",  # mid
                    self.now,  # datetime
                    uuid4(),  # account_holder_uuid, not a fkey
                    randint(1, self.data_config.retailers),  # retailer_rewards.id fkey
                    f"tx_payment_{count}",  # payment_transaction_id
                    choice(["PROCESSED", "DUPLICATE", "NO_ACTIVE_CAMPAIGNS"]),  # status
                ]
            )
        return transactions

    def processed_transaction(self) -> list:
        """Generates processed transaction (1-1 w/ transactions in data config)"""
        id_gen = id_generator(1)
        processed_transactions = []

        for count in range(1, self.data_config.transactions + 1):
            processed_transactions.append(
                [
                    next(id_gen),  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    f"tx_{count}",  # transaction_id
                    randint(500, 1000),  # amount
                    "MID_1234",  # mid
                    self.now,  # datetime
                    choice(self.account_holder_uuids),  # account_holder_uuid, not a fkey
                    randint(1, self.data_config.retailers),  # retailer_rewards.id fkey
                    '{"campaign_1", "campaign_2"}',  # campaign_slugs: array
                    f"tx_payment_{count}",  # payment_transaction_id
                ]
            )
        return processed_transactions
