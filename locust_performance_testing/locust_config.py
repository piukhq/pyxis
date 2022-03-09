from functools import wraps
from locust import task

repeat_tasks = {}  # values assigned by locustfile


def repeatable_task():
    def decorator(func):
        @wraps(func)
        @task
        def wrapper(*args, **kwargs):
            num = repeat_tasks.get(func.__name__, 0)
            for _ in range(num):
                func(*args, **kwargs)
            return True

        return wrapper

    return decorator


def set_task_repeats(repeats: dict):
    global repeat_tasks
    repeat_tasks = repeats