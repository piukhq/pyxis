import logging

from data_population.tsv_creation import tsv_manager
from data_population.data_config import data_configs
from data_population.db_tasks import db_tasks

logger = logging.getLogger("TaskController")


def populate_all(data_configuration: str):
    """
    Populates all databases.

    :param data_configuration: data_configuration name as passed in cli command
    """

    data_config = data_configs[data_configuration]

    #  Create all tsvs
    logger.info("Generating all tsvs")
    tsv_manager.TSVHandler(data_config).create_tsv_files()
    logger.info("All tsvs successfully generated")

    #  Repopulate all dbs
    logger.info("Attempting upload of all tsvs")
    db_tasks.DataTaskHandler().repopulate_all_databases()
    logger.info("All tsvs successfully uploaded")
