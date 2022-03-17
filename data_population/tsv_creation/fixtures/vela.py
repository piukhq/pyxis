from random import choice, randint
from uuid import uuid4

from data_population.data_config import DataConfig

vela_task_type_ids = {
    "reward-adjustment": 1,
    "reward-status-adjustment": 2,
    "create-campaign-balances": 3,
    "delete-campaign-balances": 4,
}


def generate_vela_type_key_values(config: DataConfig) -> dict[int, dict]:
    total_retailers = config.retailers
    total_campaigns = config.campaigns_per_retailer
    total_transactions = config.transactions
    total_rewards = total_retailers * config.rewards_per_retailer
    vela_task_type_keys: dict[int, dict] = {
        vela_task_type_ids["reward-adjustment"]: {
            1: uuid4(),  # account_holder_uuid
            2: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            3: randint(1, total_transactions),  # processed_transaction_id
            4: f"perf-test-campaign-{randint(1, total_campaigns)}",  # campaign_slug
            5: randint(100, 1000),  # adjustment_amount
            6: f"test-pre-alloc-token-{randint(1, total_transactions)}",  # pre_allocation_token
            14: f"test-post-alloc-token-{randint(1, total_transactions)}",  # post_allocation_token
            15: f"test-alloc-token-{randint(1, total_transactions)}",  # allocation_token
            16: choice([True, False]),  # reward_only
            17: randint(1, total_transactions),  # secondary_reward_retry_task_id
        },
        vela_task_type_ids["reward-status-adjustment"]: {
            7: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            8: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
            9: choice(["active", "cancelled", "ended"]),  # status
        },
        vela_task_type_ids["create-campaign-balances"]: {
            10: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            11: f"perf-test-campaign-{randint(1, total_campaigns)}",  # campaign_slug
        },
        vela_task_type_ids["delete-campaign-balances"]: {
            12: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            13: f"perf-test-campaign-{randint(1, total_campaigns)}",  # campaign_slug
        },
    }
    return vela_task_type_keys
