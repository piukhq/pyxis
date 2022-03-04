import datetime

from data_population.common.helpers import id_generator


class CarinaGenerators:
    """
    Notes:
        Assumes a 121 relationship between reward_config (CARINA) and reward_rule/campaign (VELA)
    """

    def __init__(self, data_config):
        self.now = datetime.datetime.utcnow()
        self.end_date = self.now + datetime.timedelta(weeks=100)
        self.data_config = data_config

    def retailer(self):
        retailers = []
        for retailer_count in range(1, self.data_config.retailers + 1):
            retailers.append([
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # id
                    f"retailer_{retailer_count}",  # slug
                    ])
        return retailers

    def fetch_type(self):
        fetch_types = [[
            self.now,  # created_at
            self.now,  # updated_at
            1,  # id
            'Performance Fetch Type',  # name
            {"validity_days": "integer"},  # required_fields
            ""  # path
        ]]
        return fetch_types

    def retailer_fetch_type(self):
        retailer_fetch_types = []
        for retailer_count in range(1, self.data_config.retailers + 1):
            retailer_fetch_types.append([
                    self.now,  # created_at
                    self.now,  # updated_at
                    retailer_count,  # retailer_id
                    1,  # fetch_type_id
                    ""  # agent_config
                    ])
        return retailer_fetch_types

    def reward_config(self):
        id_gen = id_generator(1)

        reward_configs = []
        for retailer_count in range(1, self.data_config.retailers + 1):
            for campaign_count in range(self.data_config.campaigns_per_retailer):

                reward_configs.append([
                        next(id_gen),  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        f"retailer_{retailer_count}_reward_{campaign_count}",  # reward_slug
                        'ACTIVE',  # status
                        retailer_count,  # retailer_id
                        1,  # fetch_type_id
                        {"validity_days": "90"},  # required_fields_values
                        ])
            return reward_configs
