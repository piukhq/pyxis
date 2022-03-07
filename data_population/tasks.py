import logging

from data_population.tsv_creation import tsv_manager
from data_population.data_config import data_configs
from data_population.db_tasks import db_tasks

logger = logging.getLogger("TaskController")


def populate(data_configuration: str):
    """
    Communicates with selected (or all) databases to organise tsv generation and database re-population.
    """

    data_config = data_configs[data_configuration]

    #  Create all tsvs
    tsv_manager.TSVHandler(data_config).create_tsv_files()
    logger.info(f"Creating all tsvs")

    #  Repopulate all dbs
    db_tasks.DataTaskHandler().repopulate_all_databases()
