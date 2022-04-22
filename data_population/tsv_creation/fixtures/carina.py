from datetime import datetime
from random import choice, randint
from uuid import uuid4

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig

carina_task_type_ids = {
    "reward-issuance": 1,
    "reward-status-adjustment": 2,
    "delete-unallocated-rewards": 3,
    "cancel-rewards": 4,
}

#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
carina_retry_task_types_to_populate = {"reward-issuance": ["allocated_rewards"]}


def generate_carina_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_reward_configs = total_retailers * data_config.campaigns_per_retailer
    carina_task_type_key_values: dict[int, dict] = {
        carina_task_type_ids["reward-issuance"]: {
            1: random_ascii(5),  # agent_state_params_raw
            2: str(uuid4()),  # idempotency_token
            3: datetime.utcnow(),  # expiry_date
            4: "https://exampleurl/random/",  # account_url
            5: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
            6: str(uuid4()),  # reward_uuid
            7: random_ascii(10),  # code
            8: randint(1, total_reward_configs),  # reward_config_id
            9: datetime.utcnow(),  # issued_date
        },
        carina_task_type_ids["reward-status-adjustment"]: {
            10: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            11: datetime.utcnow(),  # date
            12: choice(["ACTIVE", "CANCELLED", "ENDED"]),  # status
            13: str(uuid4()),  # reward_uuid
        },
        carina_task_type_ids["delete-unallocated-rewards"]: {
            14: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
            15: randint(1, total_retailers),  # retailer_id
        },
        carina_task_type_ids["cancel-rewards"]: {
            16: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
            17: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
        },
    }
    return carina_task_type_key_values
