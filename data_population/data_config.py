from dataclasses import dataclass


@dataclass
class DataConfig:
    retailers: int
    account_holders: int
    campaigns_per_retailer: int
    earn_rule_per_campaign: int
    allocated_rewards: int  # number of rewards already allocated to account_holders
    pending_rewards: int  # number of rewards already promised to account_holders (pending)
    spare_rewards: int  # number of spare rewards not yet allocated or promised to account_holders
    transactions: int
    reward_updates: int


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=200000,
        allocated_rewards=1000,
        pending_rewards=1000,
        spare_rewards=0,
        transactions=2000,
        reward_updates=2000,
    ),
    "peak": DataConfig(
        retailers=5,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=390000,
        allocated_rewards=210000,
        pending_rewards=210000,
        spare_rewards=100000,
        transactions=561600,
        reward_updates=0,
    ),
    "test": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=1000,
        allocated_rewards=300,
        pending_rewards=200,
        spare_rewards=50,
        transactions=2000,
        reward_updates=0,
    ),
}
