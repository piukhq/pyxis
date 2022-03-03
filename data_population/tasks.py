import logging

from enum import Enum
from data_population.polaris import tsv_generation as polaris_tsv
from settings import POLARIS_DB, VELA_DB, CARINA_DB
from data_population import database_tables
from data_population.data_config import data_configs

logger = logging.getLogger("Data-controller")


class DataGroups(str, Enum):
    ALL = "all"
    POLARIS = "polaris"
    VELA = "vela"
    CARINA = "carina"


data_mapping = {
    DataGroups.POLARIS: {
        "data_creation_modules": [polaris_tsv],
        "upload_lists": [{"database": POLARIS_DB, "tables": database_tables.PolarisTables}],
    },
    DataGroups.VELA: {
        "data_creation_modules": ["vela_tsv"],
        "upload_lists": [{"database": VELA_DB, "tables": database_tables.VelaTables}],
    },
    DataGroups.CARINA: {
        "data_creation_modules": ["carina_tsv"],
        "upload_lists": [{"database": CARINA_DB, "tables": database_tables.CarinaTables}],
    },
    DataGroups.ALL: {
        "data_creation_modules": [polaris_tsv, "vela", "carina"],
        "upload_lists": [
            {"database": POLARIS_DB, "tables": database_tables.PolarisTables},
            {"database": VELA_DB, "tables": database_tables.VelaTables},
            {"database": CARINA_DB, "tables": database_tables.CarinaTables},
        ],
    },
}

def populate_db(group_config_name: str, data_config_name: str):
    """Creates and uploads the requested tsv files"""



    data_config = data_configs[data_config_name]

    data_creation_modules = data_mapping[group_config_name]["data_creation_modules"]
    for data_creation_module in data_creation_modules:
        controller = data_creation_module.TSVHandler(data_config)
        controller.create_tsv_files()
        logger.info(f"Creating tsvs with {data_creation_module.__name__}")

    all_data_to_upload = data_mapping[group_config_name]["upload_lists"]
    for data_to_upload in all_data_to_upload:
        #  upload_named_group_of_tsv_files(data_to_upload["database"], data_to_upload["tables"])
        logger.info("Uploading tsvs")


def hello(group_config_name: str, data_config_name: str):
    print("hello")
