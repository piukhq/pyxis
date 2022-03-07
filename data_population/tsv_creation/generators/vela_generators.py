import datetime

from data_population.common.helpers import id_generator


class VelaGenerators:
    """
    Notes:
        Assumes a 121 relationship between reward_rule/campaign (VELA) and reward_config (CARINA)
    """

    def __init__(self, data_config):
        self.now = datetime.datetime.utcnow()
        self.end_date = self.now + datetime.timedelta(weeks=100)
        self.data_config = data_config

    def retailer_rewards(self):
        retailers = []
        for count in range(1, self.data_config.retailers + 1):
            retailers.append([
                    count,  # id
                    f"retailer_{count}"  # slug
                    ])
        return retailers

    def campaign(self):
        id_gen = id_generator(1)
        campaigns = []
        for count in range(1, self.data_config.retailers + 1):
            for campaign_count in range(self.data_config.campaigns_per_retailer):
                campaigns.append([
                    next(id_gen),  # id
                    'ACTIVE',  # status
                    f'Retailer {count} Campaign {campaign_count}',  # name
                    f'retailer_{count}_campaign_{campaign_count}',  # slug
                    self.now,  # created_at
                    self.now,  # updated_at
                    count,  # retailer_id
                    "STAMPS",  # loyalty_type
                    self.now,  # start_date
                    self.end_date,  # end_date (set to 100 weeks in the future)
                    ])
        return campaigns

    def earn_rule(self):
        id_gen = id_generator(1)
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer
        earn_rules = []
        for campaign_count in range(1, total_campaigns + 1):
            for earn_rule_count in range(self.data_config.earn_rule_per_campaign):
                earn_rules.append([
                    next(id_gen),  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    3,  # threshold
                    1,  # increment
                    1,  # increment_multiplier
                    campaign_count,  # campaign_id
                ])
        return earn_rules

    def reward_rule(self):
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer
        reward_rules = []
        for count in range(1, total_campaigns + 1):
            reward_rules.append([
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                3,  # reward_goal
                count,  # campaign_id
                f"reward_{count}",  # reward_slug
                0,  # allocation_window
            ])
        return reward_rules
