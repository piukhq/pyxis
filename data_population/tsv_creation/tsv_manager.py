import csv
import logging
import os
import multiprocessing

import settings

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.carina import (
    carina_retry_task_types_to_populate,
    get_carina_task_type_key_count,
)
from data_population.tsv_creation.fixtures.polaris import (
    get_polaris_type_key_count,
    polaris_retry_task_types_to_populate,
)
from data_population.tsv_creation.fixtures.vela import get_vela_type_key_count, vela_retry_task_types_to_populate
from data_population.tsv_creation.generators.carina_generators import CarinaGenerators
from data_population.tsv_creation.generators.polaris_generators import PolarisGenerators
from data_population.tsv_creation.generators.vela_generators import VelaGenerators
from settings import BATCHING, CARINA_DB, POLARIS_DB, TSV_BASE_DIR, TSV_BATCH_LIMIT, VELA_DB

execution_order = id_generator(1)

logger = logging.getLogger("TSVHandler")

cores = multiprocessing.cpu_count()


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

        self.clear_tsvs()

        # ------------------------------------------- VELA --------------------------------------------

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.retailer_rewards,
            base_iterator=self.data_config.retailers,
            database_name=VELA_DB,
            table_name="retailer_rewards",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.campaign,
            base_iterator=self.data_config.retailers * self.data_config.campaigns_per_retailer,
            database_name=VELA_DB,
            table_name="campaign",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.earn_rule,
            base_iterator=self.data_config.retailers * self.data_config.campaigns_per_retailer,
            database_name=VELA_DB,
            table_name="earn_rule",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.reward_rule,
            base_iterator=self.data_config.retailers * self.data_config.campaigns_per_retailer,
            database_name=VELA_DB,
            table_name="reward_rule",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.transaction,
            base_iterator=self.data_config.transactions,
            database_name=VELA_DB,
            table_name="transaction",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.processed_transaction,
            base_iterator=self.data_config.transactions,
            database_name=VELA_DB,
            table_name="processed_transaction",
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.retry_task,
            base_iterator=self.data_config.transactions,
            database_name=VELA_DB,
            table_name="retry_task",
            total_row_count=self.data_config.account_holders * len(vela_retry_task_types_to_populate),
        )

        self.generate_and_write_to_tsv(
            generator=self.vela_generator.task_type_key_value,
            base_iterator=self.data_config.transactions,
            database_name=VELA_DB,
            table_name="task_type_key_value",
            total_row_count=self.data_config.account_holders
            * len(vela_retry_task_types_to_populate)
            * get_vela_type_key_count(self.data_config),
        )

        # ------------------------------------------- CARINA --------------------------------------------

        self.generate_and_write_to_tsv(
            generator=self.carina_generator.retailer,
            base_iterator=self.data_config.retailers,
            database_name=CARINA_DB,
            table_name="retailer",
        )
        self.generate_and_write_to_tsv(
            generator=self.carina_generator.fetch_type,
            base_iterator=0,
            database_name=CARINA_DB,
            table_name="fetch_type",
        )
        self.generate_and_write_to_tsv(
            generator=self.carina_generator.retailer_fetch_type,
            base_iterator=self.data_config.retailers,
            database_name=CARINA_DB,
            table_name="retailer_fetch_type",
        )
        self.generate_and_write_to_tsv(
            generator=self.carina_generator.reward_config,
            base_iterator=self.data_config.retailers,
            database_name=CARINA_DB,
            table_name="reward_config",
        )
        self.generate_and_write_to_tsv(
            generator=self.carina_generator.reward,
            base_iterator=self.data_config.rewards,
            database_name=CARINA_DB,
            table_name="reward",
        )

        self.generate_and_write_to_tsv(
            generator=self.carina_generator.reward_update,
            base_iterator=self.data_config.reward_updates,
            database_name=CARINA_DB,
            table_name="reward_update",
        )

        self.generate_and_write_to_tsv(
            generator=self.carina_generator.retry_task,
            base_iterator=self.data_config.rewards * len(carina_retry_task_types_to_populate),
            database_name=CARINA_DB,
            table_name="retry_task",
            total_row_count=self.data_config.account_holders * len(carina_retry_task_types_to_populate),
        )

        self.generate_and_write_to_tsv(
            generator=self.carina_generator.task_type_key_value,
            base_iterator=self.data_config.rewards * len(carina_retry_task_types_to_populate),
            database_name=CARINA_DB,
            table_name="task_type_key_value",
            total_row_count=self.data_config.account_holders
            * len(carina_retry_task_types_to_populate)
            * get_carina_task_type_key_count(self.data_config),
        )

        # ------------------------------------------- POLARIS --------------------------------------------
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.retailer_config,
            base_iterator=self.data_config.retailers,
            database_name=POLARIS_DB,
            table_name="retailer_config",
        )
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.account_holder,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder",
        )
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.account_holder_profile,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder_profile",
        )
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.account_holder_marketing_preference,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder_marketing_preference",
        )
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.account_holder_campaign_balance,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder_campaign_balance",
        )
        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.account_holder_reward,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder_reward",
        )
        self.generate_and_write_to_tsv(
            self.polaris_generator.account_holder_pending_reward,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="account_holder_pending_reward",
        )

        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.retry_task,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="retry_task",
            total_row_count=self.data_config.account_holders * len(polaris_retry_task_types_to_populate),
        )

        self.generate_and_write_to_tsv(
            generator=self.polaris_generator.task_type_key_value,
            base_iterator=self.data_config.account_holders,
            database_name=POLARIS_DB,
            table_name="task_type_key_value",
            total_row_count=self.data_config.account_holders
            * len(polaris_retry_task_types_to_populate)
            * get_polaris_type_key_count(self.data_config),
        )

    @staticmethod
    def write_to_tsv(data: list, db: str, table: str, batch_number: int = None) -> None:
        """
        Writes data to tsv with filename containing all information needed for upload (including order).

        :param data: data to write to tsv
        :param db: database to write this data to
        :param table: table to write this data to
        :param batch_number: number of batch for this table
        """

        execute_id = next(execution_order)

        if not os.path.isdir(TSV_BASE_DIR):
            os.mkdir(TSV_BASE_DIR)

        batch_info = str(batch_number) if batch_number is not None else "*"

        tsv_name = os.path.join(TSV_BASE_DIR, f"tsv-{db}-{execute_id}-{table}__{batch_info}.tsv")

        with open(tsv_name, "w+") as f:
            tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)

        logger.info(f"Wrote tsv {tsv_name}")

    def generate_and_write_to_tsv(
        self, generator: callable, base_iterator: int, database_name: str, table_name: str, total_row_count=None
    ) -> None:
        """Handles per-table batching, data-generation and tsv-writing"""

        if total_row_count is None:
            total_row_count = base_iterator

        if BATCHING and total_row_count > TSV_BATCH_LIMIT:
            parts = self.split_rows(base_iterator, total_row_count)
            batch_number = 0

            for start, stop in parts:
                batch_number += 1
                data = generator(start, stop)
                self.write_to_tsv(data, database_name, table_name, batch_number)

        else:
            data = generator(1, base_iterator)
            self.write_to_tsv(data, database_name, table_name)

    def generate_and_write_to_tsv_job(self, generator, start, stop, database_name, table_name, batch_number):



    @staticmethod
    def split_rows(base_iterator: int, total_rows: int) -> list:
        """
        Splits a number of rows into n sets of TSV_BATCH_LIMIT rows. If the base iterator for the table is not the same
        as the total number of rows, total_rows is used as the main batch splitter, and then this is converted to
        iterator rows.
        """

        val_list = []

        def check_validity(val):
            if val in val_list:
                val += 1
            if val == 0:
                val = 1
            if val > total_rows:
                val = total_rows
            val_list.append(val)
            return val

        parts = []
        row_marker = 0
        while row_marker < total_rows:
            row_marker += 1
            start = row_marker
            row_marker += TSV_BATCH_LIMIT - 1
            end = row_marker if row_marker <= total_rows else total_rows
            parts.append((start, end))

        if base_iterator == total_rows:
            return parts
        else:
            converted_parts = []
            for start, end in parts:
                start_converted = check_validity(round((start / total_rows) * base_iterator))
                end_converted = check_validity(round((end / total_rows) * base_iterator))
                converted_parts.append((start_converted, end_converted))
            return converted_parts

    @staticmethod
    def clear_tsvs():
        directory = settings.PROJECT_ROOT + "/" + TSV_BASE_DIR
        files = os.listdir(directory)
        for f in files:
            os.remove(os.path.join(directory, f))
        logger.info("Successfully removed old .tsvs")
