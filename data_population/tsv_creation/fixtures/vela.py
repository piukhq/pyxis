from random import randint, choice
from uuid import uuid4

vela_task_type_ids = {
    "reward-adjustment": 1,
    "reward-status-adjustment": 2,
    "create-campaign-balances": 3,
    "delete-campaign-balances": 4,
}

vela_task_type_keys = {
    vela_task_type_ids["reward-adjustment"]: {
        1: uuid4(),  # account_holder_uuid
        2: f"perf-test-retailer-{randint(1, 20)}",  # retailer_slug
        3: randint(1, 1000),  # processed_transaction_id
        4: f"perf-test-campaign-{randint(1, 20)}",  # campaign_slug
        5: randint(100, 1000),  # adjustment_amount
        6: f"test-pre-alloc-token-{randint(1, 1000)}",  # pre_allocation_token
        14: f"test-post-alloc-token-{randint(1, 1000)}",  # post_allocation_token
        15: f"test-alloc-token-{randint(1, 1000)}",  # allocation_token
        16: choice([True, False]),  # reward_only
        17: randint(1, 1000),  # secondary_reward_retry_task_id
    },
    vela_task_type_ids["reward-status-adjustment"]: {
        7: f"perf-test-retailer-{randint(1, 20)}",  # retailer_slug
        8: f"perf-reward-slug-{randint(1, 2000)}",  # reward_slug
        9: choice(["active", "cancelled", "ended"]),  # status
    },
    vela_task_type_ids["create-campaign-balances"]: {
        10: f"perf-test-retailer-{randint(1, 20)}",  # retailer_slug
        11: f"perf-test-campaign-{randint(1, 20)}",  # campaign_slug
    },
    vela_task_type_ids["delete-campaign-balances"]: {
        12: f"perf-test-retailer-{randint(1, 20)}",  # retailer_slug
        13: f"perf-test-campaign-{randint(1, 20)}",  # campaign_slug
    },
}
