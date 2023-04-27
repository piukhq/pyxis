from enum import Enum

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


audit_data = [
    {
        "request": {"url": "http://polaris-api/bpl/loyalty/test-retailer/accounts/foo/adjustments"},
        "response": {"body": "{new_balance:375, campaign_slug:test-campaign-1}", "status": 200},
        "timestamp": "2021-11-01T15:39:40.050413",
    },
    {
        "request": {"url": "http://carina-api/bpl/vouchers/test-retailer/vouchers/10percentoff/allocation"},
        "response": {"body": "{}", "status": 202},
        "timestamp": "2021-11-01T15:39:40.138773",
    },
]
