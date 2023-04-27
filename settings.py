import logging
import os

from environs import Env
from faker import Faker

env = Env()
env.read_env()

LOG_LEVEL = env.log_level("LOG_LEVEL", "DEBUG")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TSV_BASE_DIR = env("TSV_BASE_DIR", "data_population/data")

VAULT_URL = env("VAULT_URL", "")
POLARIS_AUTH_KEY_NAME = env("POLARIS_AUTH_KEY_NAME", "bpl-polaris-api-auth-token")
VELA_AUTH_KEY_NAME = env("VELA_AUTH_KEY_NAME", "bpl-vela-api-auth-token")

REDIS_URL = env("REDIS_URL", "redis://localhost:6379/0")

DB_CONNECTION_URI = env("DB_CONNECTION_URI", "")
COSMOS_DB = env("COSMOS_DB", "perf_bpl_cosmos")
ACCOUNTS_API_URL = env("ACCOUNTS_API_URL", "")
TRANSACTIONS_API_URL = env("TRANSACTIONS_API_URL", "")
PUBLIC_API_URL = env("PUBLIC_API_URL", "")
LUNA_API_URL = env("LUNA_API_URL", "http://luna-api")
