from locust import HttpUser, constant

from locust_performance_testing.helpers import set_task_repeats
from locust_performance_testing.user_tasks import UserTasks


class WebsiteUser(HttpUser):

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_account_holder": 16,  # will 409 if set to > 1
        "post_get_by_credentials": 2,
        "get_account": 65,
        "get_marketing_unsubscribe": 16,
        "post_transaction": 22,
        "delete_account": 0,  # will 404 if > 0 (ENDPOINT NOT IMPLEMENTED)
        "stop_locust_after_test_suite": 1,  # Should be set to 1 in most normal situations
    }

    set_task_repeats(repeats)
    tasks = [UserTasks]
    wait_time = constant(0)
