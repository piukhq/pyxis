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

        "post_token": 1,
        "stop_user_after_test_suite": 1,
    }

    set_task_repeats(repeats)
    tasks = [UserTasks]
    wait_time = constant(0)
