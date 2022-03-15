from datetime import datetime, timedelta
from random import randint
from typing import Optional
from uuid import uuid4

from data_population.common.utils import id_generator


class VelaGenerators:
    def __init__(self, data_config):
        self.now = datetime.utcnow()
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.retailer_ids = []

    def retailer_rewards(self) -> list:
        retailers = []
        for count in range(1, self.data_config.retailers + 1):
            self.retailer_ids.append(count)
            retailers.append([count, f"retailer_{count}"])  # id  # slug
        return retailers

    def campaign(self) -> list:
        """Generates campaigns (n defined in data_config as retailers * campaigns per retailer)"""
        id_gen = id_generator(1)
        campaigns = []
        for count in range(1, self.data_config.retailers + 1):
            for campaign_count in range(1, self.data_config.campaigns_per_retailer + 1):
                campaigns.append(
                    [
                        next(id_gen),  # id
                        "ACTIVE",  # status
                        f"Retailer {count} Campaign {campaign_count}",  # name
                        f"retailer_{count}_campaign_{campaign_count}",  # slug
                        self.now,  # created_at
                        self.now,  # updated_at
                        count,  # retailer_id
                        "STAMPS",  # loyalty_type
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
        earn_rules = []
        for campaign_count in range(1, total_campaigns + 1):
            for earn_rule_count in range(self.data_config.earn_rule_per_campaign):
                earn_rules.append(
                    [
                        next(id_gen),  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        3,  # threshold
                        1,  # increment
                        1,  # increment_multiplier
                        campaign_count,  # campaign_id
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
                    3,  # reward_goal
                    count,  # campaign_id
                    f"reward_{count}",  # reward_slug
                    0,  # allocation_window
                ]
            )
        return reward_rules

    def transaction(self, additionals: Optional[list] = []) -> list:
        id_gen = id_generator(1)
        transactions = []
        retailer_ids = self.retailer_ids
        total_retailers = len(retailer_ids)
        tx_per_retailer = int(self.data_config.transactions / total_retailers)

        for retailer_id in retailer_ids:
            for count in range(1, tx_per_retailer + 1):
                data = [
                    next(id_gen),  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    f"tx_{count}",  # transaction_id
                    randint(500, 1000),  # amount
                    f"mid_{randint(1, self.data_config.transactions)}",  # mid
                    self.now,  # datetime
                    uuid4(),  # account_holder_uuid, not a fkey
                    retailer_id,  # retailer_rewards.id fkey
                ]
                if bool(additionals):
                    data.extend(additionals)
                transactions.append(data)
        return transactions

    def processed_transaction(self) -> list:
        additional_col = ['{"test_campaign_1", "test_campaign_2"}']  # campaign_slug, array
        return self.transaction(additionals=additional_col)
