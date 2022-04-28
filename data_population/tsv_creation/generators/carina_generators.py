from datetime import datetime, timedelta
from random import choice
from uuid import uuid4

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig


class CarinaGenerators:
    def __init__(self, data_config: DataConfig) -> None:
        self.now = datetime.utcnow()
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.allocated_rewards: list = []
        self.pending_rewards: list = []
        self.unallocated_rewards: list = []
        self.all_reward_configs: dict = {}

    def retailer(self) -> list:
        """Generates n retailers (n defined in data_config)"""
        retailers = []

        total_retailers = self.data_config.jigsaw_retailers + self.data_config.preloaded_retailers

        for retailer_count in range(1, total_retailers + 1):
            retailers.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # id
                    f"retailer_{retailer_count}",  # slug
                ]
            )
        return retailers

    def retailer_fetch_type(self) -> list:
        """Generates n retailer<->fetch_type links (1 per retailer (fetch type 1 only))"""
        retailer_fetch_types = []

        total_retailers = self.data_config.jigsaw_retailers + self.data_config.preloaded_retailers

        for retailer_count in range(1, total_retailers + 1):
            fetch_type_id = 1 if retailer_count <= self.data_config.preloaded_retailers else 2
            # (1=Preloaded, 2=Jigsaw)

            retailer_fetch_types.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # retailer_id
                    fetch_type_id,  # fetch_type_id
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

        total_retailers = self.data_config.jigsaw_retailers + self.data_config.preloaded_retailers

        for retailer_count in range(1, total_retailers + 1):
            fetch_type_id = 1 if retailer_count <= self.data_config.preloaded_retailers else 2
            # (1=Preloaded, 2=Jigsaw)
            for campaign_count in range(self.data_config.campaigns_per_retailer):
                reward_config_id = next(id_gen)

                reward_configs.append(
                    [
                        self.now,  # created_at
                        self.now,  # updated_at
                        reward_config_id,  # id
                        f"reward_{reward_config_id}",  # reward_slug
                        retailer_count,  # retailer_id
                        fetch_type_id,  # fetch_type_id
                        "ACTIVE",  # status
                        {"validity_days": 90},  # required_fields_values
                    ]
                )

                self.all_reward_configs[reward_config_id] = {'retailer': retailer_count, 'fetch_type': fetch_type_id}

        return reward_configs

    def reward(self) -> list:
        """
        Generates n rewards/vouchers (total n defined as allocated_rewards + preloaded_pending_rewards + spare_rewards
        in data_config) for carina's rewards table.

        Saves allocated_rewards and pending_rewards (n=jigsaw_pending_rewards + preloaded_pending_rewards) for later use
         by Polaris' account_holder_reward and account_holder_pending_reward tables.

         For clarity: we generate jigsaw_pending_rewards here to be later added into polaris' pending_rewards table (via
          self.pending_rewards: dict), but we don't actually save these into carina's rewards table in the process -
          these rewards will be fetched from jigsaw, not from carina's preloaded rewards, so we don't need an allocation
           for these in carina.
        """

        all_rewards = []
        preloaded_reward_configs = {}
        jigsaw_reward_configs = {}

        # Split out reward configs by fetch type
        for config in self.all_reward_configs:
            if config['fetch_type'] == 1:
                preloaded_reward_configs.update(config)
            else:
                jigsaw_reward_configs.update(config)

        def get_rewards(number_of_rewards: int, allocated: bool, reward_configs: dict, output_to_list: list = None):

            rewards = []

            for i in range(number_of_rewards):
                reward_id = str(uuid4())
                reward_config_id = choice(list(reward_configs))
                retailer_id = reward_configs[reward_config_id]['retailer']  # retailer_id
                code = str(uuid4())

                rewards.append(
                    [
                        self.now,  # created_at
                        self.now,  # updated_at
                        reward_id,  # id (:uuid)
                        code,  # code
                        allocated,  # allocated
                        False,  # deleted
                        reward_config_id,  # reward_config_id
                        retailer_id,  # retailer_id
                    ]
                )

                #  Save reward details for later use in polaris
                if output_to_list:
                    output_to_list.append(
                        {
                            "reward_uuid": reward_id,
                            "reward_config_id": reward_config_id,
                            "retailer_id": retailer_id,
                            "code": code,
                            "allocated": allocated,
                        }
                    )

            return rewards

        # Allocated rewards - correspond to those already allocated in polaris/account_holder_reward
        allocated_rewards = get_rewards(
            number_of_rewards=self.data_config.allocated_rewards,
            allocated=True,
            reward_configs=self.all_reward_configs,
            output_to_list=self.allocated_rewards
        )
        all_rewards.append(allocated_rewards)

        # Preloaded pending rewards - used to populate both carina rewards table and polaris pending_rewards
        # (fetch_type 1 retailers)
        preloaded_pending_rewards = get_rewards(
            number_of_rewards=self.data_config.preloaded_pending_rewards,
            allocated=False,
            reward_configs=preloaded_reward_configs,
            output_to_list=self.pending_rewards
        )
        all_rewards.append(preloaded_pending_rewards)

        # Jigsaw pending rewards - used to populate only polaris pending_rewards (no need to add to carina rewards as
        # these will be fetched from Jigsaw, but we generate these here for simplicity) (fetch_type 2 retailers)
        get_rewards(
            number_of_rewards=self.data_config.jigsaw_pending_rewards,
            allocated=False,
            reward_configs=jigsaw_reward_configs,
            output_to_list=self.pending_rewards
        )

        # Spare rewards - used to populate only carina rewards table with extra rewards for later issuance by fetch_type
        # 1 retailers
        spare_rewards = get_rewards(
            number_of_rewards=self.data_config.spare_rewards,
            allocated=False,
            reward_configs=preloaded_reward_configs,
            output_to_list=self.pending_rewards
        )
        all_rewards.append(spare_rewards)

        return all_rewards

    def reward_update(self) -> list:
        """
        Generates n reward_updates. n is defined at the dataconfig
        Note: This re-uses uuids from self.reward_id. So must be run after
        reward generator
        """

        reward_updates = []
        reward_uuids = [item["reward_uuid"] for item in self.allocated_rewards]

        for count in range(self.data_config.reward_updates):
            reward_updates.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    count,  # id
                    choice(reward_uuids),  # reward_uuid
                    self.now.date(),  # date
                    choice(["CANCELLED", "REDEEMED", "ISSUED"]),  # status
                ]
            )
        return reward_updates
