from enum import Enum
from random import randint

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
    "account-holder-activation": 1,
    "send-welcome-email": 2,
    "enrolment-callback": 3,
    "create-campaign-balances": 4,
    "delete-campaign-balances": 5,
    "cancel-rewards": 6,
    "pending-reward-allocation": 7,
    "anonymise-account-holder": 8,
    "pending-accounts-activation": 9,
    "convert-pending-rewards": 10,
    "delete-pending-rewards": 11,
}

#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
polaris_retry_task_types_to_populate = {
    "enrolment-callback": ["account_holders"],
    "account-holder-activation": ["account_holders"],
    "create-campaign-balances": ["account_holders"],
    "send-welcome-email": ["account_holders"],
    "pending-reward-allocation": ["pending_rewards", "allocated_rewards"],
    "convert-pending-rewards": ["pending_rewards"],
    "delete-pending-rewards": ["pending_rewards"],
}


def generate_polaris_type_key_values(data_config: DataConfig) -> dict[int, dict]:
    total_account_holders = data_config.account_holders
    total_retailers = data_config.retailers
    total_campaigns = data_config.retailers * data_config.campaigns_per_retailer
    polaris_task_type_keys: dict[int, dict] = {
        polaris_task_type_ids["account-holder-activation"]: {
            1: randint(1, total_account_holders),  # account_holder_id
            2: randint(1, total_account_holders),  # welcome_email_retry_task_id
            3: randint(1, total_account_holders),  # callback_retry_task_id
        },
        polaris_task_type_ids["send-welcome-email"]: {
            4: randint(1, total_account_holders),  # account_holder_id
        },
        polaris_task_type_ids["enrolment-callback"]: {
            5: randint(1, total_account_holders),  # account_holder_id
            6: f"https://{random_ascii(10)}/example_url",  # callback_url
            7: f"{random_ascii(10)}",  # third_party_identifier
        },
        polaris_task_type_ids["create-campaign-balances"]: {
            8: f"retailer_{randint(1, total_retailers)}",  # retailer_slug,
            9: f"campaign_{randint(1, total_retailers)}",  # campaign_slug
        },
        polaris_task_type_ids["delete-campaign-balances"]: {
            10: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            11: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        polaris_task_type_ids["cancel-rewards"]: {
            12: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            13: f"reward_{randint(1, total_campaigns)}",  # reward_slug
        },
        polaris_task_type_ids["pending-reward-allocation"]: {
            14: randint(1, data_config.pending_rewards),  # pending_reward_id,
            15: randint(1, total_account_holders),  # account_holder_id
            16: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            17: f"reward_{randint(1, total_campaigns)}",  # reward_slug
        },
        polaris_task_type_ids["anonymise-account-holder"]: {
            18: randint(1, total_account_holders),  # account_holder_id
            19: randint(1, total_retailers),  # retailer_id
        },
        polaris_task_type_ids["pending-accounts-activation"]: {
            20: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            21: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        polaris_task_type_ids["convert-pending-rewards"]: {
            22: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            23: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
        polaris_task_type_ids["delete-pending-rewards"]: {
            24: f"retailer_{randint(1, total_retailers)}",  # retailer_slug
            25: f"campaign_{randint(1, total_campaigns)}",  # campaign_slug
        },
    }
    return polaris_task_type_keys
