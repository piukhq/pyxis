from data_population.data_config import DataConfig
from data_population.tsv_creation.polaris_generators import PolarisFactory
import csv



class TSVHandler:

    def __init__(self, data_config: DataConfig):
        self.id = 0
        self.config = data_config
        self.polaris_generator = PolarisFactory(data_config=data_config)
        self.vela_generator = PolarisFactory(data_config=data_config)
        self.carina_generator = PolarisFactory(data_config=data_config)

        self.retailers = []
        self.account_holders = []
        self.account_holder_profiles = []

    def create_tsv_files(self):

        # Core
        self.generate_tsv(data=self.polaris_generator.retailer_config(), db='polaris', table='retailer_config')

        # Load
        self.account_holders = self.polaris_generator.account_holder()
        self.account_holder_profiles = self.polaris_generator.account_holder_profile()


        print(len(self.retailers))
        print(len(self.account_holders))
        print(len(self.account_holder_profiles))

    @staticmethod
    def generate_tsv(data, db, table):
        tsv_name = f"tsv-{db}-{table}.tsv"

        with open(tsv_name, 'w+') as f:
            tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)

