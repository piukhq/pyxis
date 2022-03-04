import logging

from data_population.polaris import tsv_generation as polaris_tsv, db_tasks as polaris_db_tasks

from settings import POLARIS_DB, VELA_DB, CARINA_DB
from data_population import database_tables
from data_population.data_config import data_configs

logger = logging.getLogger("TaskController")

data_mapping = {
    "polaris": {
        "data_creation_module": polaris_tsv,
        "db_tasks_module": polaris_db_tasks,
    },
    "vela": {
        "data_creation_module": "vela_tsv",
        "db_tasks_module": polaris_db_tasks,
    },
    "carina": {
        "data_creation_module": "carina_tsv",
        "db_tasks_module": polaris_db_tasks,
    },
}


def populate(data_configuration: str, db_to_populate: str = None):
    """
    Communicates with selected (or all) databases to organise tsv generation and database re-population.
    """

    data_config = data_configs[data_configuration]

    if db_to_populate is None:
        dbs_to_populate = (list(data_mapping.keys()))
    else:
        dbs_to_populate = [db_to_populate]

    #  Create all tsvs
    for db in dbs_to_populate:
        module = data_mapping[db]["data_creation_module"]
        module.TSVHandler(data_config).create_tsv_files()
        logger.info(f"Created tsvs for {db} with {module.__name__}")

    #  Repopulate all dbs
    for db in dbs_to_populate:
        module = data_mapping[db]["db_tasks_module"]
        module.DataTaskHandler().repopulate_tables()
