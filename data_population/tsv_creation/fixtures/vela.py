from random import choice, randint
from uuid import uuid4

from sqlalchemy.orm import Session

from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.common import process_type_key_ids_and_values

vela_task_type_ids = {
    "reward-adjustment": 1,
    "reward-status-adjustment": 2,
    "create-campaign-balances": 3,
    "delete-campaign-balances": 4,
    "convert-or-delete-pending-rewards": 5,
}

#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
vela_retry_task_types_to_populate = {"reward-adjustment": ["transactions"]}


def _get_vela_type_key_values_fixture(data_config: DataConfig) -> dict[int, dict[str, str | int]]:
    total_retailers = data_config.retailers
    total_campaigns = data_config.retailers * data_config.campaigns_per_retailer
    total_transactions = data_config.transactions
    vela_task_type_keys: dict[int, dict] = {
        vela_task_type_ids["reward-adjustment"]: {
            "account_holder_uuid": uuid4(),
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
            "adjustment_amount": randint(100, 1000),
            "processed_transaction_id": randint(1, total_transactions),
            "allocation_token": f"test-alloc-token-{randint(1, total_transactions)}",
            "pre_allocation_token": f"test-pre-alloc-token-{randint(1, total_transactions)}",
            "post_allocation_token": f"test-post-alloc-token-{randint(1, total_transactions)}",
            "reward_only": choice([True, False]),
            "secondary_reward_retry_task_id": randint(1, total_transactions),
        },
        vela_task_type_ids["reward-status-adjustment"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "reward_slug": f"reward_{randint(1, total_campaigns)}",
            "status": choice(["active", "cancelled", "ended"]),
        },
        vela_task_type_ids["create-campaign-balances"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
        vela_task_type_ids["delete-campaign-balances"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
        vela_task_type_ids["convert-or-delete-pending-rewards"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
            "issue_pending_rewards": choice([True, False]),
        },
    }
    return vela_task_type_keys


def generate_vela_type_key_values(db_session: "Session", data_config: DataConfig) -> dict[int, dict]:
    vela_task_type_key_value_fixture = _get_vela_type_key_values_fixture(data_config)
    return process_type_key_ids_and_values(db_session, vela_task_type_ids, vela_task_type_key_value_fixture)
