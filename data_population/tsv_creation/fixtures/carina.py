from datetime import datetime
from random import choice, randint
from uuid import uuid4

from sqlalchemy.orm import Session

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.common import process_type_key_ids_and_values

carina_task_type_ids = {
    "reward-issuance": 1,
    "reward-status-adjustment": 2,
    "delete-unallocated-rewards": 3,
    "cancel-rewards": 4,
}

#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
carina_retry_task_types_to_populate = {"reward-issuance": ["allocated_rewards"]}


def _get_carina_type_key_values_fixture(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_reward_configs = total_retailers * data_config.campaigns_per_retailer
    carina_task_type_key_values: dict[int, dict] = {
        carina_task_type_ids["reward-issuance"]: {
            "agent_state_params_raw": random_ascii(5),
            "idempotency_token": str(uuid4()),
            "expiry_date": datetime.utcnow(),
            "account_url": "https://exampleurl/random/",
            "reward_slug": f"reward_{randint(1, total_reward_configs)}",
            "reward_uuid": str(uuid4()),
            "code": random_ascii(10),
            "reward_config_id": randint(1, total_reward_configs),
            "issued_date": datetime.utcnow(),
        },
        carina_task_type_ids["reward-status-adjustment"]: {
            "retailer_slug": f"perf-test-retailer-{randint(1, total_retailers)}",
            "date": datetime.utcnow(),
            "status": choice(["ACTIVE", "CANCELLED", "ENDED"]),
            "reward_uuid": str(uuid4()),
        },
        carina_task_type_ids["delete-unallocated-rewards"]: {
            "reward_slug": f"reward_{randint(1, total_reward_configs)}",
            "retailer_id": randint(1, total_retailers),
        },
        carina_task_type_ids["cancel-rewards"]: {
            "reward_slug": f"reward_{randint(1, total_reward_configs)}",
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
        },
    }
    return carina_task_type_key_values


def generate_carina_type_key_values(db_session: "Session", data_config: DataConfig) -> dict[int, dict]:
    carina_task_type_key_value_fixture = _get_carina_type_key_values_fixture(data_config)
    return process_type_key_ids_and_values(db_session, carina_task_type_ids, carina_task_type_key_value_fixture)
