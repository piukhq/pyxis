from enum import Enum


class PolarisTables(str, Enum):
    ACCOUNT_HOLDER = 'account_holder'
    ACCOUNT_HOLDER_CAMPAIGN_BALANCE = 'account_holder_campaign_balance'
    ACCOUNT_HOLDER_MARKETING_PREFERENCE = 'account_holder_marketing_preference'
    ACCOUNT_HOLDER_PENDING_REWARD = 'account_holder_pending_reward'
    ACCOUNT_HOLDER_REWARD = 'account_holder_reward'
    BALANCE_ADJUSTMENT = 'balance_adjustment'
    RETAILER_CONFIG = 'retailer_config'
    RETRY_TASK = 'retry_task'
    TASK_TYPE = 'task_type'
    TASK_TYPE_KEY = 'task_type_key'
    TASK_TYPE_KEY_VALUE = 'task_type_key_value'


class VelaTables(str, Enum):
    pass


class CarinaTables(str, Enum):
    pass
