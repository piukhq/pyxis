from dataclasses import dataclass
from typing import Literal


@dataclass
class DataConfig:
    retailers: int
    stores_per_retailer: int
    account_holders: int
    campaigns_per_retailer: int
    loyalty_type: Literal["STAMPS", "ACCUMULATOR"]
    earn_rule_per_campaign: int
    allocation_window: Literal["NULL"] | int
    reward_cap: Literal["NULL"] | int
    allocated_rewards: int  # number of rewards already allocated to account_holders
    pending_rewards: int  # number of rewards already promised to account_holders (pending)
    pending_reward_conversion: bool
    spare_rewards: int  # number of spare rewards not yet allocated or promised to account_holders
    transactions: int
    reward_updates: int


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window="NULL",
        reward_cap="NULL",
        account_holders=200000,
        allocated_rewards=1000,
        pending_reward_conversion=False,
        pending_rewards=1000,
        spare_rewards=0,
        transactions=2000,
        reward_updates=2000,
    ),
    "benchmark_trc_refund": DataConfig(
        retailers=10,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window=1,
        reward_cap=2,
        account_holders=200000,
        allocated_rewards=1000,
        pending_rewards=0,
        pending_reward_conversion=False,
        spare_rewards=0,
        transactions=2000,
        reward_updates=2000,
    ),
    "peak": DataConfig(
        retailers=5,
        stores_per_retailer=50,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window=0,
        reward_cap="NULL",
        account_holders=390000,
        allocated_rewards=210000,
        pending_rewards=210000,
        pending_reward_conversion=False,
        spare_rewards=100000,
        transactions=561600,
        reward_updates=0,
    ),
    "peak_trc_refund": DataConfig(
        retailers=5,
        stores_per_retailer=50,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window=1,
        reward_cap=2,
        account_holders=390000,
        allocated_rewards=210000,
        pending_rewards=0,
        pending_reward_conversion=False,
        spare_rewards=100000,
        transactions=561600,
        reward_updates=0,
    ),
    "test": DataConfig(
        retailers=10,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window="NULL",
        reward_cap="NULL",
        account_holders=1000,
        allocated_rewards=300,
        pending_rewards=200,
        pending_reward_conversion=False,
        spare_rewards=50,
        transactions=2000,
        reward_updates=0,
    ),
    "test_trc_refund": DataConfig(
        retailers=10,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window=1,
        reward_cap=2,
        account_holders=1000,
        allocated_rewards=300,
        pending_rewards=0,
        pending_reward_conversion=False,
        spare_rewards=50,
        transactions=2000,
        reward_updates=0,
    ),
    "peak_pending_rewards": DataConfig(
        retailers=5,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="ACCUMULATOR",
        earn_rule_per_campaign=1,
        allocation_window=1,
        reward_cap="NULL",
        account_holders=390000,
        allocated_rewards=210000,
        pending_rewards=210000,
        pending_reward_conversion=True,
        spare_rewards=100000,
        transactions=561600,
        reward_updates=0,
    ),
    "test-migration-script": DataConfig(
        retailers=1,
        stores_per_retailer=20,
        campaigns_per_retailer=1,
        loyalty_type="STAMPS",
        earn_rule_per_campaign=1,
        allocation_window="NULL",
        reward_cap=1,
        account_holders=2000,
        allocated_rewards=300,
        pending_rewards=200,
        pending_reward_conversion=False,
        spare_rewards=50,
        transactions=25000,
        reward_updates=0,
    ),
}
