from random import choice, randint
from uuid import uuid4

from data_population.data_config import DataConfig

vela_task_type_ids = {
    "reward-adjustment": 1,
    "reward-status-adjustment": 2,
    "create-campaign-balances": 3,
    "delete-campaign-balances": 4,
}


def generate_vela_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_campaigns = data_config.retailers * data_config.campaigns_per_retailer
    total_transactions = data_config.transactions
    vela_task_type_keys: dict[int, dict] = {
        vela_task_type_ids["reward-adjustment"]: {
            1: uuid4(),  # account_holder_uuid
            2: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            3: randint(1, total_transactions),  # processed_transaction_id
            4: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
            5: randint(100, 1000),  # adjustment_amount
            6: f"test-pre-alloc-token-{randint(1, total_transactions)}",  # pre_allocation_token
            14: f"test-post-alloc-token-{randint(1, total_transactions)}",  # post_allocation_token
            15: f"test-alloc-token-{randint(1, total_transactions)}",  # allocation_token
            16: choice([True, False]),  # reward_only
            17: randint(1, total_transactions),  # secondary_reward_retry_task_id
        },
        vela_task_type_ids["reward-status-adjustment"]: {
            7: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            8: f"reward_{randint(1, total_campaigns)}",  # reward_slug
            9: choice(["active", "cancelled", "ended"]),  # status
        },
        vela_task_type_ids["create-campaign-balances"]: {
            10: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            11: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        vela_task_type_ids["delete-campaign-balances"]: {
            12: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            13: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
    }
    return vela_task_type_keys
