import logging

from data_population.common.utils import timed_function
from data_population.data_config import data_configs
from data_population.db_tasks import db_tasks
from data_population.tsv_creation import tsv_manager

logger = logging.getLogger("TaskController")


@timed_function
def populate_all(data_configuration: str) -> None:
    """
    Populates all databases.

    :param data_configuration: data_configuration name as passed in cli command
    """

    data_config = data_configs[data_configuration]

    #  Create all tsvs
    logger.info("Generating tsvs")
    tsv_manager.TSVHandler(data_config).create_tsv_files()
    logger.info("All tsvs successfully generated")

    #  Repopulate all dbs
    logger.info("Attempting upload of all tsvs")
    db_tasks.DataTaskHandler().repopulate_all_databases()
    logger.info("All tsvs successfully uploaded")
