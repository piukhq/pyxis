from locust import HttpUser, constant
from locust_performance_testing.locust_config import set_task_repeats


class WebsiteUser(HttpUser):

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        # --TOKEN--
        "post_token": 1,  # REQUIRED

    }

    set_task_repeats(repeats)
    tasks = [UserBehavior]
    wait_time = constant(0)
