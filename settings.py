import logging
import os

from faker import Faker

from environment import env_var, read_env

read_env()

LOG_LEVEL = env_var("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s")
logging.getLogger("faker").setLevel(logging.WARNING)

fake = Faker("en_GB")

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

TSV_BASE_DIR = env_var("TSV_BASE_DIR", "data_population/data")
TSV_BATCH_LIMIT = env_var("TSV_BASE_DIR", 100000)

VAULT_URL = env_var("VAULT_URL", "")
POLARIS_AUTH_KEY_NAME = env_var("POLARIS_AUTH_KEY_NAME", "bpl-polaris-api-auth-token")
VELA_AUTH_KEY_NAME = env_var("VELA_AUTH_KEY_NAME", "bpl-vela-api-auth-token")

DB_CONNECTION_URI = env_var("DB_CONNECTION_URI", "")
POLARIS_DB = env_var("POLARIS_DB", "polaris")
VELA_DB = env_var("VELA_DB", "vela")
CARINA_DB = env_var("CARINA_DB", "carina")
