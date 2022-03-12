from enum import Enum
from random import randint, choice
from uuid import uuid4
from data_population.common.utils import random_ascii

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

# todo: these should be converted to yaml on write (?)


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

polaris_task_type_keys = {
    polaris_task_type_ids["enrolment-callback"]: {
        1: str(uuid4()), # account_holder_uuid
        2: f"{random_ascii(10)}", # third_party_identifier
        3: f"https://{random_ascii(10)}/example_url", # callback_url
    },
    polaris_task_type_ids["account-holder-activation"]: {
        4: randint(1, 2000), # account_holder_id
        5: randint(1, 2000), # callback_retry_task_id
        14: randint(1, 2000), # welcome_email_retry_task_id
    },
    polaris_task_type_ids["delete-campaign-balances"]: {
        6: f"perf-test-retailer-{randint(1, 20)}", # retailer_slug
        7: f"perf-test-campaign-{randint(1, 20)}", # campaign_slug
    },
    polaris_task_type_ids["create-campaign-balances"]: {
        8: f"perf-test-retailer-{randint(1, 20)}", # retailer_slug,
        9: f"perf-test-campaign-{randint(1, 20)}", # campaign_slug
    },
    polaris_task_type_ids["cancel-rewards"]: {
        10: f"perf-test-retailer-{randint(1, 20)}", # retailer_slug
        11: f"perf-reward-slug-{randint(1, 2000)}", # reward_slug
    },
    polaris_task_type_ids["send-welcome-email"]: {
        12: str(uuid4()), # account_holder_uuid
        13: f"{random_ascii(5)}@test-email.com", # email
    },
    polaris_task_type_ids["pending-reward-allocation"]: {
        15: f"perf-test-retailer-{randint(1, 20)}", # retailer_slug
        16: f"perf-reward-slug-{randint(1, 2000)}", # reward_slug
        17: str(uuid4()), # account_holder_uuid,
        18: randint(1, 2000), # pending_reward_id,
    }
}