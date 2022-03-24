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


def generate_carina_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_retailers = data_config.retailers
    total_rewards = data_config.rewards
    total_reward_config_ids = total_retailers * data_config.campaigns_per_retailer
    carina_task_type_key_values: dict[int, dict] = {
        carina_task_type_ids["reward-issuance"]: {
            1: "https://exampleurl/random/",  # account_url
            2: datetime.utcnow(),  # issued_date
            3: datetime.utcnow(),  # expiry_date
            4: randint(1, total_reward_config_ids),  # reward_config_id
            5: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
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
            13: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            14: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
        },
        carina_task_type_ids["delete-unallocated-rewards"]: {
            15: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            16: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
        },
    }
    return carina_task_type_key_values
