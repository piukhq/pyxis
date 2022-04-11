from locust import HttpUser, constant, events
from locust.env import Environment

from locust_performance_testing.helpers import set_initial_starting_pk, set_task_repeats
from locust_performance_testing.user_tasks import UserTasks


class WebsiteUser(HttpUser):

    """
    Repeats is a dictionary representing the total number of runs per task. i.e. 2 = task is run 2 times
    in total.
    ALL tasks to be run must be in this list and have the @repeatable_task decorator.
    """

    repeats = {
        "post_account_holder": 10,
        "post_get_by_credentials": 1,
        "get_account": 39,
        "get_marketing_unsubscribe": 10,
        "post_transaction": 14,
        "delete_account": 0,  # will 404 if > post_account_holder (ENDPOINT NOT IMPLEMENTED)
        "stop_locust_after_test_suite": 1,  # Should be set to 1 in most normal situations
    }

    set_task_repeats(repeats)
    tasks = [UserTasks]
    wait_time = constant(0)


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs) -> None:  # type: ignore
    print("Test started")
    set_initial_starting_pk()
