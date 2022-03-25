from dataclasses import dataclass


@dataclass
class DataConfig:
    retailers: int
    account_holders: int
    campaigns_per_retailer: int
    earn_rule_per_campaign: int
    rewards: int  # refers to rewards (i.e. claimable vouchers etc., not reward_configs or reward_rules)
    transactions: int
    reward_updates: int


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=200000,
        rewards=3000,
        transactions=2000,
        reward_updates=2000,
    ),
    "peak": DataConfig(
        retailers=5,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=390000,
        rewards=1000000,
        transactions=561600,
        reward_updates=1000000,
    ),
    "1m-tx": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=10000,
        rewards=1000,
        transactions=1000000,
        reward_updates=1000,
    ),
    "500k-tx": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=10000,
        rewards=1000,
        transactions=500000,
        reward_updates=1000,
    ),
    "750k-tx": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=10000,
        rewards=1000,
        transactions=500000,
        reward_updates=1000,
    ),
    "test": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=1000,
        rewards=1000,
        transactions=1000,
        reward_updates=1000,
    ),
}
