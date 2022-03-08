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

VAULT_CONFIG = dict(
    VAULT_URL=env_var("VAULT_URL", ""),
    AES_KEYS_VAULT_NAME=env_var("AES_KEYS_VAULT_NAME", "aes-keys"),
    API2_PRIVATE_KEYS_NAME=env_var("API2_PRIVATE_KEYS_NAME", "api2-channel-private-keys"),
    CHANNEL_SECRET_NAME=env_var("CHANNEL_SECRET_NAME", "channels"),
)

DB_CONNECTION_URI = env_var("DB_CONNECTION_URI")
POLARIS_DB = env_var("POLARIS_DB", "polaris")
VELA_DB = env_var("VELA_DB", "vela")
CARINA_DB = env_var("CARINA_DB", "carina")

SERVICE_API_KEY = "F616CE5C88744DD52DB628FAD8B3D"
