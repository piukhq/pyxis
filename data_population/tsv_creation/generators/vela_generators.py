from datetime import datetime, timedelta
from random import randint
from typing import Optional
from uuid import uuid4

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.vela import generate_vela_type_key_values, vela_task_type_ids
from data_population.tsv_creation.generators.task_generators import retry_task, task_type_key_value


class VelaGenerators:
    def __init__(self, data_config: DataConfig) -> None:
        self.now = datetime.utcnow()
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.retailer_ids: list = []

    def retailer_rewards(self, start, stop) -> list:
        retailers = []
        for retailer_count in range(start, stop + 1):
            self.retailer_ids.append(retailer_count)
            retailers.append([retailer_count, f"retailer_{retailer_count}"])  # id  # slug
        return retailers

    def campaign(self, start, stop) -> list:
        """Generates campaigns (n defined in data_config as retailers * campaigns per retailer)"""
        id_gen = id_generator((start - 1 * self.data_config.campaigns_per_retailer) + 1)
        campaigns = []
        for retailer_count in range(start, stop + 1):
            for campaign_count in range(1, self.data_config.campaigns_per_retailer + 1):

                campaign_id = next(id_gen)

                campaigns.append(
                    [
                        campaign_id,  # id
                        "ACTIVE",  # status
                        f"Campaign {campaign_id}",  # name
                        f"campaign_{campaign_id}",  # slug
                        self.now,  # created_at
                        self.now,  # updated_at
                        retailer_count,  # retailer_id
                        "STAMPS",  # loyalty_type
                        self.now,  # start_date
                        self.end_date,  # end_date (set to 100 weeks in the future)
                    ]
                )
        return campaigns

    def earn_rule(self, start, stop) -> list:
        """
        Generates earn_rules (n defined in data_config as retailers * campaigns per retailer * earn_rules per campaign)
        """
        id_gen = id_generator((start - 1 * self.data_config.earn_rule_per_campaign) + 1)
        earn_rules = []
        for campaign_count in range(start, stop + 1):
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

    def reward_rule(self, start, stop) -> list:
        """Generates reward_rules (n defined in data_config as retailers * campaigns per retailer (1-1 w/campaigns))"""
        reward_rules = []
        for count in range(start, stop + 1):
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

    def transaction(self, start, stop, additionals: Optional[list] = None) -> list:
        """Generates transactions (n defined in n data_config)"""
        transactions = []

        for transaction_count in range(start, stop + 1):
            data = [
                transaction_count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                f"tx_{transaction_count}",  # transaction_id
                randint(500, 1000),  # amount
                "MID_1234",  # mid
                self.now,  # datetime
                uuid4(),  # account_holder_uuid, not a fkey
                randint(1, self.data_config.retailers),  # retailer_rewards.id fkey
            ]
            if additionals is not None:
                data.extend(additionals)  # type: ignore
            transactions.append(data)
        return transactions

    def processed_transaction(self, start, stop) -> list:
        """Generates processed transaction (1-1 w/ transactions in data config)"""
        additional_col = ['{"campaign_1", "campaign_2"}']  # campaign_slug, array
        return self.transaction(start, stop, additionals=additional_col)

    @staticmethod
    def retry_task(start, stop) -> list:
        """Generates retry_tasks (1-1 w/ transactions in data config)"""
        return retry_task(start=start, stop=stop, task_type_ids_dict=vela_task_type_ids)

    def task_type_key_value(self, start, stop) -> list:
        """Generates task_type_key_value data"""
        return task_type_key_value(
            start=start,
            stop=stop,
            task_type_ids_dict=vela_task_type_ids,
            task_type_keys_dict=generate_vela_type_key_values(self.data_config),
            random_task_types=self.data_config.random_task_types,
        )
