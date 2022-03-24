from enum import Enum
from random import randint
from uuid import uuid4

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig

profile_config = {
    "email": {"required": "true", "label": "email"},
    "first_name": {"required": "true", "label": "first_name"},
    "last_name": {"required": "true", "label": "last_name"},
    "date_of_birth": {"required": "true", "label": "date_of_birth"},
    "phone": {"required": "true", "label": "phone"},
    "address_line1": {"required": "true", "label": "address_line1"},
    "address_line2": {"required": "true", "label": "address_line2"},
    "postcode": {"required": "true", "label": "postcode"},
    "city": {"required": "true", "label": "city"},
}

marketing_preferences = {
    "marketing_pref": {
        "label": "Would you like to receive marketing?",
        "type": "boolean",
    }
}


class AccountHolderStatuses(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    FAILED = "FAILED"
    INACTIVE = "INACTIVE"


polaris_task_type_ids = {
    "enrolment-callback": 1,
    "account-holder-activation": 2,
    "delete-campaign-balances": 3,
    "create-campaign-balances": 4,
    "cancel-rewards": 5,
    "send-welcome-email": 6,
    "pending-reward-allocation": 7,
}


def generate_polaris_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_account_holders = data_config.account_holders
    total_retailers = data_config.retailers
    total_campaigns = data_config.campaigns_per_retailer
    total_rewards = data_config.rewards
    polaris_task_type_keys: dict[int, dict] = {
        polaris_task_type_ids["enrolment-callback"]: {
            1: str(uuid4()),  # account_holder_uuid
            2: f"{random_ascii(10)}",  # third_party_identifier
            3: f"https://{random_ascii(10)}/example_url",  # callback_url
        },
        polaris_task_type_ids["account-holder-activation"]: {
            4: randint(1, total_account_holders),  # account_holder_id
            5: randint(1, total_account_holders),  # callback_retry_task_id
            14: randint(1, total_account_holders),  # welcome_email_retry_task_id
        },
        polaris_task_type_ids["delete-campaign-balances"]: {
            6: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            7: f"perf-test-campaign-{randint(1, total_campaigns)}",  # campaign_slug
        },
        polaris_task_type_ids["create-campaign-balances"]: {
            8: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug,
            9: f"perf-test-campaign-{randint(1, total_retailers)}",  # campaign_slug
        },
        polaris_task_type_ids["cancel-rewards"]: {
            10: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            11: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
        },
        polaris_task_type_ids["send-welcome-email"]: {
            12: str(uuid4()),  # account_holder_uuid
            13: f"perf-{random_ascii(5)}@test-email.com",  # email
        },
        polaris_task_type_ids["pending-reward-allocation"]: {
            15: f"perf-test-retailer-{randint(1, total_retailers)}",  # retailer_slug
            16: f"perf-reward-slug-{randint(1, total_rewards)}",  # reward_slug
            17: str(uuid4()),  # account_holder_uuid,
            18: randint(1, total_rewards),  # pending_reward_id,
        },
    }
    return polaris_task_type_keys
