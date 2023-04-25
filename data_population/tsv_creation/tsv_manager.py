import csv
import logging
import os

from uuid import uuid4

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures import (
    fetch_task_types_ids,
    generate_task_type_key_values,
    cosmos_retry_task_types_to_populate
)
from data_population.tsv_creation.generators.cosmos_generators import CosmosGenerators
from data_population.tsv_creation.generators.task_generators import retry_task, task_type_key_value
from settings import COSMOS_DB, TSV_BASE_DIR

execution_order = id_generator(1)

logger = logging.getLogger("TSVHandler")


class TSVHandler:
    """Handles whole TSV creation journey for all databases."""

    def __init__(self, data_config: DataConfig) -> None:
        self.id = 0  # pylint: disable=invalid-name
        self.data_config = data_config
        account_holder_uuids = [uuid4() for _ in range(data_config.account_holders)]
        self.cosmos_generator = CosmosGenerators(data_config=data_config, account_holder_uuids=account_holder_uuids)
        self.cosmos_task_type_ids = fetch_task_types_ids(COSMOS_DB)

    def create_tsv_files(self) -> None:
        """
        Writes generated table data to tsvs for all databases, in execution order.

        N.b. tables will later be written to the db in the order below.
        """

        self.write_to_tsv(self.cosmos_generator.retailer(), COSMOS_DB, table="retailer")
        self.write_to_tsv(self.cosmos_generator.campaign(), COSMOS_DB, table="campaign")
        self.write_to_tsv(self.cosmos_generator.earn_rule(), COSMOS_DB, table="earn_rule")
        self.write_to_tsv(self.cosmos_generator.reward_config(), COSMOS_DB, table="reward_config")
        self.write_to_tsv(self.cosmos_generator.reward_rule(), COSMOS_DB, table="reward_rule")
        self.write_to_tsv(self.cosmos_generator.account_holder(), COSMOS_DB, table="account_holder")
        self.write_to_tsv(self.cosmos_generator.account_holder_profile(), COSMOS_DB, table="account_holder_profile")
        self.write_to_tsv(self.cosmos_generator.retailer_store(), COSMOS_DB, table="retailer_store")
        self.write_to_tsv(self.cosmos_generator.transaction(), COSMOS_DB, table="transaction")
        self.write_to_tsv(self.cosmos_generator.transaction_earn(), COSMOS_DB, table="transaction_earn")
        self.write_to_tsv(
            self.cosmos_generator.marketing_preference(),
            COSMOS_DB,
            table="marketing_preference",
        )
        self.write_to_tsv(
            self.cosmos_generator.campaign_balance(),
            COSMOS_DB,
            table="campaign_balance",
        )
        self.write_to_tsv(self.cosmos_generator.email_template(), COSMOS_DB, table="email_template")
        self.write_to_tsv(self.cosmos_generator.retailer_fetch_type(), COSMOS_DB, table="retailer_fetch_type")
        self.write_to_tsv(self.cosmos_generator.reward(), COSMOS_DB, table="reward")
        self.write_to_tsv(
            self.cosmos_generator.pending_reward(), COSMOS_DB, table="pending_reward"
        )
        self.write_to_tsv(self.cosmos_generator.reward_update(), COSMOS_DB, table="reward_update")

        self.write_to_tsv(
            retry_task(self.cosmos_task_type_ids, cosmos_retry_task_types_to_populate, data_config=self.data_config),
            COSMOS_DB,
            table="retry_task",
        )
        self.write_to_tsv(
            task_type_key_value(
                task_type_ids_dict=self.cosmos_task_type_ids,
                task_type_keys_dict=generate_task_type_key_values(COSMOS_DB),
                task_types_to_populate=cosmos_retry_task_types_to_populate,
                data_config=self.data_config,
            ),
            COSMOS_DB,
            table="task_type_key_value",
        )

    @staticmethod
    def write_to_tsv(data: list, db_name: str, table: str) -> None:
        """
        Writes data to tsv with filename containing all information needed for upload (including order).

        :param data: data to write to tsv
        :param db: database to write this data to
        :param table: table to write this data to
        """

        execute_id = next(execution_order)

        if not os.path.isdir(TSV_BASE_DIR):
            os.mkdir(TSV_BASE_DIR)

        tsv_name = os.path.join(TSV_BASE_DIR, f"tsv-{db_name}-{execute_id}-{table}.tsv")

        with open(tsv_name, "w+", encoding="utf-8") as file:
            tsv_writer = csv.writer(file, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)

        logger.info(f"Wrote tsv {tsv_name}")
