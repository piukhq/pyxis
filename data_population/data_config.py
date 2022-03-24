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
    random_task_types: bool


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=200000,
        rewards=3000,
        transactions=2000,
        reward_updates=2000,
        random_task_types=False,
    ),

    "1m-tx": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=10000,
        rewards=3000,
        transactions=1000000,
        reward_updates=3000,
        random_task_types=False,
    ),

    "test": DataConfig(
        retailers=10,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        account_holders=1000,
        rewards=3000,
        transactions=1000,
        reward_updates=3000,
        random_task_types=False,
    )
}
