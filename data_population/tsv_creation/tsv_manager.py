import csv
import logging
import os

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures import (
    carina_retry_task_types_to_populate,
    carina_task_type_ids,
    generate_carina_type_key_values,
    generate_polaris_type_key_values,
    generate_vela_type_key_values,
    polaris_retry_task_types_to_populate,
    polaris_task_type_ids,
    vela_retry_task_types_to_populate,
    vela_task_type_ids,
)
from data_population.tsv_creation.generators.carina_generators import CarinaGenerators
from data_population.tsv_creation.generators.polaris_generators import PolarisGenerators
from data_population.tsv_creation.generators.task_generators import retry_task, task_type_key_value
from data_population.tsv_creation.generators.vela_generators import VelaGenerators
from settings import CARINA_DB, POLARIS_DB, TSV_BASE_DIR, VELA_DB

execution_order = id_generator(1)

logger = logging.getLogger("TSVHandler")


class TSVHandler:
    """Handles whole TSV creation journey for all databases."""

    def __init__(self, data_config: DataConfig) -> None:
        self.id = 0
        self.data_config = data_config
        self.polaris_generator = PolarisGenerators(data_config=data_config)
        self.vela_generator = VelaGenerators(data_config=data_config)
        self.carina_generator = CarinaGenerators(data_config=data_config)

    def create_tsv_files(self) -> None:
        """
        Writes generated table data to tsvs for all databases, in execution order.

        N.b. tables will later be written to the db in the order below.
        """

        # VELA GENERATION
        self.write_to_tsv(self.vela_generator.retailer_rewards(), VELA_DB, table="retailer_rewards")
        self.write_to_tsv(self.vela_generator.campaign(), VELA_DB, table="campaign")
        self.write_to_tsv(self.vela_generator.earn_rule(), VELA_DB, table="earn_rule")
        self.write_to_tsv(self.vela_generator.reward_rule(), VELA_DB, table="reward_rule")
        self.write_to_tsv(self.vela_generator.transaction(), VELA_DB, table="transaction")
        self.write_to_tsv(self.vela_generator.processed_transaction(), VELA_DB, table="processed_transaction")

        self.write_to_tsv(
            retry_task(vela_task_type_ids, vela_retry_task_types_to_populate),
            VELA_DB,
            table="retry_task",
        )
        self.write_to_tsv(
            task_type_key_value(
                task_type_ids_dict=vela_task_type_ids,
                task_type_keys_dict=generate_vela_type_key_values(self.data_config),
                task_types_to_populate=vela_retry_task_types_to_populate,
            ),
            VELA_DB,
            table="task_type_key_value",
        )

        # CARINA GENERATION
        self.write_to_tsv(self.carina_generator.retailer(), CARINA_DB, table="retailer")
        self.write_to_tsv(self.carina_generator.fetch_type(), CARINA_DB, table="fetch_type")
        self.write_to_tsv(self.carina_generator.retailer_fetch_type(), CARINA_DB, table="retailer_fetch_type")
        self.write_to_tsv(self.carina_generator.reward_config(), CARINA_DB, table="reward_config")
        self.write_to_tsv(self.carina_generator.reward(), CARINA_DB, table="reward")
        self.write_to_tsv(self.carina_generator.reward_update(), CARINA_DB, table="reward_update")

        self.write_to_tsv(
            retry_task(carina_task_type_ids, carina_retry_task_types_to_populate),
            CARINA_DB,
            table="retry_task",
        )
        self.write_to_tsv(
            task_type_key_value(
                task_type_ids_dict=carina_task_type_ids,
                task_type_keys_dict=generate_carina_type_key_values(self.data_config),
                task_types_to_populate=carina_retry_task_types_to_populate,
            ),
            CARINA_DB,
            table="task_type_key_value",
        )

        # POLARIS GENERATION
        self.write_to_tsv(self.polaris_generator.retailer_config(), POLARIS_DB, table="retailer_config")
        self.write_to_tsv(self.polaris_generator.account_holder(), POLARIS_DB, table="account_holder")
        self.write_to_tsv(self.polaris_generator.account_holder_profile(), POLARIS_DB, table="account_holder_profile")
        self.write_to_tsv(
            self.polaris_generator.account_holder_marketing_preference(),
            POLARIS_DB,
            table="account_holder_marketing_preference",
        )
        self.write_to_tsv(
            self.polaris_generator.account_holder_campaign_balance(),
            POLARIS_DB,
            table="account_holder_campaign_balance",
        )
        self.write_to_tsv(
            self.polaris_generator.account_holder_reward(),
            POLARIS_DB,
            table="account_holder_reward",
        )
        self.write_to_tsv(
            self.polaris_generator.account_holder_pending_reward(), POLARIS_DB, table="account_holder_pending_reward"
        )

        self.write_to_tsv(
            retry_task(polaris_task_type_ids, polaris_retry_task_types_to_populate),
            POLARIS_DB,
            table="retry_task",
        )
        self.write_to_tsv(
            task_type_key_value(
                task_type_ids_dict=polaris_task_type_ids,
                task_type_keys_dict=generate_polaris_type_key_values(self.data_config),
                task_types_to_populate=polaris_retry_task_types_to_populate,
            ),
            POLARIS_DB,
            table="task_type_key_value",
        )

    @staticmethod
    def write_to_tsv(data: list, db: str, table: str) -> None:
        """
        Writes data to tsv with filename containing all information needed for upload (including order).

        :param data: data to write to tsv
        :param db: database to write this data to
        :param table: table to write this data to
        """

        execute_id = next(execution_order)

        if not os.path.isdir(TSV_BASE_DIR):
            os.mkdir(TSV_BASE_DIR)

        tsv_name = os.path.join(TSV_BASE_DIR, f"tsv-{db}-{execute_id}-{table}.tsv")

        with open(tsv_name, "w+") as f:
            tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)

        logger.info(f"Wrote tsv {tsv_name}")
