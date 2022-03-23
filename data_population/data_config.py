from dataclasses import dataclass


@dataclass
class DataConfig:
    retailers: int
    account_holders: int
    campaigns_per_retailer: int
    earn_rule_per_campaign: int
    rewards_per_retailer: int  # refers to rewards (i.e. claimable vouchers etc., not reward_configs or reward_rules)
    transactions: int
    reward_updates: int


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        account_holders=200000,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        rewards_per_retailer=3000,
        transactions=2000,
        reward_updates=2000,
    )
}
