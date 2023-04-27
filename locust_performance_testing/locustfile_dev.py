from locust import HttpUser, constant

from locust_performance_testing.helpers import locust_handler
from locust_performance_testing.user_tasks import UserTasks


class WebsiteUser(HttpUser):

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_account_holder": 1,
        "post_get_by_credentials": 1,
        "get_account": 1,
        "get_marketing_unsubscribe": 1,
        "post_transaction": 1,
        "post_transaction_with_trc": 1,
        "post_transaction_with_refund": 1,
        "delete_account": 0,  # will 404 if > post_account_holder (ENDPOINT NOT IMPLEMENTED)
        "stop_locust_after_test_suite": 1,  # Should be set to 1 in most normal situations
    }

    locust_handler.repeat_tasks = repeats
    tasks = [UserTasks]
    wait_time = constant(0)
