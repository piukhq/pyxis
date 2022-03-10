from locust import HttpUser, constant
from locust_performance_testing.helpers import set_task_repeats, load_secrets
from locust_performance_testing.user_tasks import UserTasks


class WebsiteUser(HttpUser):

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_account_holder": 1,  # will 409 if set to > 1
        "post_get_by_credentials": 1,
        "get_account": 1,
        "get_account_profile": 1,
        "patch_account_profile": 1,
        "get_marketing_unsubscribe": 1,
        "delete_account": 1,  # will 404 if > 1
        "stop_user_after_test_suite": 1,  # Should be set to 1 in most normal situations
    }

    set_task_repeats(repeats)
    tasks = [UserTasks]
    wait_time = constant(0)
