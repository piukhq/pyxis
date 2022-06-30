from enum import Enum
from random import randint
from typing import Union

from sqlalchemy.orm import Session

from data_population.common.utils import random_ascii
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.common import process_type_key_ids_and_values

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


def _get_polaris_task_type_key_values_fixture(data_config: DataConfig) -> dict[int, dict[int, Union[str, int]]]:
    total_account_holders = data_config.account_holders
    total_retailers = data_config.retailers
    total_campaigns = data_config.retailers * data_config.campaigns_per_retailer
    _polaris_task_type_key_values_fixture: dict[int, dict[int, Union[str, int]]] = {
        polaris_task_type_ids["account-holder-activation"]: {
            "account_holder_id": randint(1, total_account_holders),
            "welcome_email_retry_task_id": randint(1, total_account_holders),
            "callback_retry_task_id": randint(1, total_account_holders),
        },
        polaris_task_type_ids["send-welcome-email"]: {
            "account_holder_id": randint(1, total_account_holders),
        },
        polaris_task_type_ids["enrolment-callback"]: {
            "account_holder_id": randint(1, total_account_holders),
            "callback_url": f"https://{random_ascii(10)}/example_url",
            "third_party_identifier": f"{random_ascii(10)}",
        },
        polaris_task_type_ids["create-campaign-balances"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_retailers)}",
        },
        polaris_task_type_ids["delete-campaign-balances"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
        polaris_task_type_ids["cancel-rewards"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "reward_slug": f"reward_{randint(1, total_campaigns)}",
        },
        polaris_task_type_ids["pending-reward-allocation"]: {
            "pending_reward_id": randint(1, data_config.pending_rewards),
            "account_holder_id": randint(1, total_account_holders),
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "reward_slug": f"reward_{randint(1, total_campaigns)}",
        },
        polaris_task_type_ids["anonymise-account-holder"]: {
            "account_holder_id": randint(1, total_account_holders),
            "retailer_id": randint(1, total_retailers),
        },
        polaris_task_type_ids["pending-accounts-activation"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
        polaris_task_type_ids["convert-pending-rewards"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
        polaris_task_type_ids["delete-pending-rewards"]: {
            "retailer_slug": f"retailer_{randint(1, total_retailers)}",
            "campaign_slug": f"campaign_{randint(1, total_campaigns)}",
        },
    }
    return _polaris_task_type_key_values_fixture


def generate_polaris_type_key_values(db_session: "Session", data_config: DataConfig) -> dict[int, dict]:
    polaris_task_type_key_value_fixture = _get_polaris_task_type_key_values_fixture(data_config)
    return process_type_key_ids_and_values(db_session, polaris_task_type_ids, polaris_task_type_key_value_fixture)
