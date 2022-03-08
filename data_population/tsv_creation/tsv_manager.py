import settings
from data_population.data_config import DataConfig
from data_population.tsv_creation.generators.polaris_generators import PolarisGenerators
from data_population.tsv_creation.generators.vela_generators import VelaGenerators
from data_population.tsv_creation.generators.carina_generators import CarinaGenerators
from data_population.common.helpers import id_generator
from settings import POLARIS_DB, VELA_DB, CARINA_DB, TSV_BASE_DIR
import csv
import os

execution_order = id_generator(1)


class TSVHandler:
    """Handles whole TSV creation journey for all databases."""

    def __init__(self, data_config: DataConfig):
        self.id = 0
        self.config = data_config
        self.polaris_generator = PolarisGenerators(data_config=data_config)
        self.vela_generator = VelaGenerators(data_config=data_config)
        self.carina_generator = CarinaGenerators(data_config=data_config)

    def create_tsv_files(self):
        """
        Writes generated table data to tsvs for all databases, in execution order.

        N.b. tables will later be written to the db in the order below.
        """

        # VELA GENERATION
        self.write_to_tsv(self.vela_generator.retailer_rewards(), VELA_DB, table="retailer_rewards")
        self.write_to_tsv(self.vela_generator.campaign(), VELA_DB, table="campaign")
        self.write_to_tsv(self.vela_generator.earn_rule(), VELA_DB, table="earn_rule")
        self.write_to_tsv(self.vela_generator.reward_rule(), VELA_DB, table="reward_rule")

        # CARINA GENERATION
        self.write_to_tsv(self.carina_generator.retailer(), CARINA_DB, table="retailer")
        self.write_to_tsv(self.carina_generator.fetch_type(), CARINA_DB, table="fetch_type")
        self.write_to_tsv(self.carina_generator.retailer_fetch_type(), CARINA_DB, table="retailer_fetch_type")
        self.write_to_tsv(self.carina_generator.reward_config(), CARINA_DB, table="reward_config")
        self.write_to_tsv(self.carina_generator.reward(), CARINA_DB, table="reward")

        # POLARIS GENERATION
        self.write_to_tsv(self.polaris_generator.retailer_config(), POLARIS_DB, table="retailer_config")
        self.write_to_tsv(self.polaris_generator.account_holder(), POLARIS_DB, table="account_holder")
        self.write_to_tsv(self.polaris_generator.account_holder_profile(), POLARIS_DB, table="account_holder_profile")
        self.write_to_tsv(
            self.polaris_generator.account_holder_marketing_preference(),
            POLARIS_DB,
            table="account_holder_marketing_preference",
        )

    @staticmethod
    def write_to_tsv(data: list, db: str, table: str):
        """
        Writes data to tsv with filename containing all information needed for upload (including order).

        :param data: data to write to tsv
        :param db: database to write this data to
        :param table: table to write this data to
        """

        execute_id = next(execution_order)

        tsv_name = os.path.join(TSV_BASE_DIR, f"tsv-{db}-{execute_id}-{table}.tsv")

        with open(tsv_name, "w+") as f:
            tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)
