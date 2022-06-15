from random import choice, randint
from uuid import uuid4

from data_population.data_config import DataConfig

vela_task_type_ids = {
    "reward-adjustment": 1,
    "reward-status-adjustment": 2,
    "create-campaign-balances": 3,
    "delete-campaign-balances": 4,
    "convert-or-delete-pending-rewards": 5,
}

#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
vela_retry_task_types_to_populate = {"reward-adjustment": ["transactions"]}


def generate_vela_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_campaigns = data_config.retailers * data_config.campaigns_per_retailer
    total_transactions = data_config.transactions
    vela_task_type_keys: dict[int, dict] = {
        vela_task_type_ids["reward-adjustment"]: {
            1: uuid4(),  # account_holder_uuid
            2: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            3: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
            4: randint(100, 1000),  # adjustment_amount
            5: randint(1, total_transactions),  # processed_transaction_id
            6: f"test-alloc-token-{randint(1, total_transactions)}",  # allocation_token
            7: f"test-pre-alloc-token-{randint(1, total_transactions)}",  # pre_allocation_token
            8: f"test-post-alloc-token-{randint(1, total_transactions)}",  # post_allocation_token
            9: choice([True, False]),  # reward_only
            10: randint(1, total_transactions),  # secondary_reward_retry_task_id
        },
        vela_task_type_ids["reward-status-adjustment"]: {
            11: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            12: f"reward_{randint(1, total_campaigns)}",  # reward_slug
            13: choice(["active", "cancelled", "ended"]),  # status
        },
        vela_task_type_ids["create-campaign-balances"]: {
            14: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            15: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        vela_task_type_ids["delete-campaign-balances"]: {
            16: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            17: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        vela_task_type_ids["convert-or-delete-pending-rewards"]: {
            18: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            19: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
            20: choice([True, False]),  # issue_pending_rewards
        },
    }
    return vela_task_type_keys
