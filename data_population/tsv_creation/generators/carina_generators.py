from datetime import datetime, timedelta
from random import choice, randint
from uuid import uuid4

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig


class CarinaGenerators:
    def __init__(self, data_config: DataConfig) -> None:
        self.now = datetime.utcnow()
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.reward_ids: list = []

    def retailer(self) -> list:
        """Generates n retailers (n defined in data_config)"""
        retailers = []

        for retailer_count in range(1, self.data_config.retailers + 1):
            retailers.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # id
                    f"retailer_{retailer_count}",  # slug
                ]
            )
        return retailers

    def fetch_type(self) -> list:
        """Generates n fetch types (fixed n - can add more if needed)"""
        fetch_types = [
            [
                self.now,  # created_at
                self.now,  # updated_at
                1,  # id
                "Performance Fetch Type",  # name
                {"validity_days": "integer"},  # required_fields
                "app.fetch_reward.pre_loaded.PreLoaded",  # path
            ]
        ]
        return fetch_types

    def retailer_fetch_type(self) -> list:
        """Generates n retailer<->fetch_type links (1 per retailer (fetch type 1 only))"""
        retailer_fetch_types = []

        for retailer_count in range(1, self.data_config.retailers + 1):
            retailer_fetch_types.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # retailer_id
                    1,  # fetch_type_id
                    "",  # agent_config
                ]
            )
        return retailer_fetch_types

    def reward_config(self) -> list:
        """
        Generates n reward_configs (n defined in data_config as retailers * campaigns per retailer)
        Assumes a 121 relationship between reward_config (CARINA) and reward_rule/campaign (VELA) (i.e. only one config
        per campaign)
        """
        id_gen = id_generator(1)
        reward_configs = []

        for retailer_count in range(1, self.data_config.retailers + 1):
            for campaign_count in range(self.data_config.campaigns_per_retailer):

                reward_id = next(id_gen)

                reward_configs.append(
                    [
                        reward_id,  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        f"reward_{reward_id}",  # reward_slug
                        "ACTIVE",  # status
                        retailer_count,  # retailer_id
                        1,  # fetch_type_id
                        {"validity_days": 90},  # required_fields_values
                    ]
                )
        return reward_configs

    def reward(self) -> list:
        """
        Generates n rewards/vouchers (total n defined as rewards in data_config)
        Saves reward uuids generated as: [reward_uuids] for later use by reward_updates table
        """

        reward_configs = self.data_config.retailers * self.data_config.campaigns_per_retailer
        rewards = []

        for reward in range(self.data_config.rewards):

            reward_id = str(uuid4())
            self.reward_ids.append(reward_id)

            rewards.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    reward_id,  # id
                    str(uuid4()),  # code
                    False,  # allocated
                    randint(1, reward_configs),  # reward_config_id
                    False,  # deleted
                    randint(1, self.data_config.retailers),  # retailer_id
                ]
            )
        return rewards

    def reward_update(self) -> list:
        """
        Generates n reward_updates. n is defined at the dataconfig
        Note: This re-uses uuids from self.reward_id. So must be run after
        reward generator
        """

        reward_updates = []
        reward_ids = self.reward_ids

        for count in range(self.data_config.reward_updates):
            reward_updates.append(
                [
                    count,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    self.now.date(),  # date
                    choice(["CANCELLED", "REDEEMED", "ISSUED"]),  # allocated
                    choice(reward_ids),  # reward_uuid
                ]
            )
        return reward_updates
