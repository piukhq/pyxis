from datetime import datetime
from random import choice, randint
from uuid import uuid4

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig

carina_task_type_ids = {
    "reward-issuance": 1,
    "reward-status-adjustment": 2,
    "cancel-rewards": 3,
    "delete-unallocated-rewards": 4,
}

#  We will generate <data_config.rewards> retry rows for each of the following task types:
carina_retry_task_types_to_populate = {"reward-issuance": "rewards"}


def generate_carina_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_reward_configs = total_retailers * data_config.campaigns_per_retailer
    carina_task_type_key_values: dict[int, dict] = {
        carina_task_type_ids["reward-issuance"]: {
            1: "https://exampleurl/random/",  # account_url
            2: datetime.utcnow(),  # issued_date
            3: datetime.utcnow(),  # expiry_date
            4: randint(1, total_reward_configs),  # reward_config_id
            5: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
            6: str(uuid4()),  # reward_uuid
            7: random_ascii(10),  # code
            12: str(uuid4()),  # idempotency_token
            17: random_ascii(5),  # customer_card_ref
        },
        carina_task_type_ids["reward-status-adjustment"]: {
            8: str(uuid4()),  # reward_uuid
            9: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            10: datetime.utcnow(),  # date
            11: choice(["ACTIVE", "CANCELLED", "ENDED"]),
        },
        carina_task_type_ids["cancel-rewards"]: {
            13: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            14: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
        },
        carina_task_type_ids["delete-unallocated-rewards"]: {
            15: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            16: f"reward_{randint(1, total_reward_configs)}",  # reward_slug
        },
    }
    return carina_task_type_key_values
