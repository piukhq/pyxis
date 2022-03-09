from locust import SequentialTaskSet
from locust.exception import StopUser
from faker import Faker
from locust_performance_testing.helpers import repeatable_task


class UserTasks(SequentialTaskSet):
    """
    User behaviours for the BPL performance test suite.
    N.b. Tasks here use a preconfigured 'repeatable_task' decorator, which extends the locust @task decorator and allows
    each task to be run a number of times, as defined in the locustfile which creates this class. All functions to
    be called by the User MUST have the @repeatable_task() decorator, and must also be included in the 'repeats'
    dictionary in the parent locustfile.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.url_prefix = "/bpl"
        self.fake = Faker()

    # ---------------------------------POLARIS ENDPOINTS---------------------------------
    @repeatable_task()
    def endpoint_call(self):
        pass

    # ---------------------------------SPECIAL TASKS---------------------------------

    @repeatable_task()
    def stop_locust_after_test_suite(self):
        raise StopUser()
