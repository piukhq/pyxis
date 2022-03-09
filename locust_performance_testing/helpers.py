from functools import wraps
from locust import task
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from settings import VAULT_CONFIG

repeat_tasks = {}  # values assigned by locustfile

all_secrets = {}

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


def load_secrets():
    global all_secrets
    if all_secrets:
        return all_secrets
    else:
        credential = DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_visual_studio_code_credential=True,
            exclude_interactive_browser_credential=True,
        )

        client = SecretClient(vault_url=VAULT_CONFIG['VAULT_URL'], credential=credential)
