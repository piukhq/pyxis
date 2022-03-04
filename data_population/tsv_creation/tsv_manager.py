
from data_population.data_config import DataConfig
from data_population.tsv_creation.polaris_generators import PolarisGenerators
from data_population.tsv_creation.vela_generators import VelaGenerators
from data_population.tsv_creation.carina_generators import CarinaGenerators
import csv

class TSVHandler:


    def __init__(self, data_config: DataConfig):
        self.id = 0
        self.config = data_config
        self.polaris_generator = PolarisGenerators(data_config=data_config)
        self.vela_generator = VelaGenerators(data_config=data_config)
        self.carina_generator = CarinaGenerators(data_config=data_config)


    def create_tsv_files(self):

        # VELA GENERATION
        self.write_to_tsv(self.vela_generator.retailer_rewards(), 'vela', 'retailer_rewards')
        self.write_to_tsv(self.vela_generator.campaign(), 'vela', 'campaign')
        self.write_to_tsv(self.vela_generator.earn_rule(), 'vela', 'earn_rule')
        self.write_to_tsv(self.vela_generator.reward_rule(), 'vela', 'reward_rule')

        # CARINA GENERATION
        self.write_to_tsv(self.carina_generator.retailer(), 'vela', 'retailer')
        self.write_to_tsv(self.carina_generator.fetch_type(), 'vela', 'fetch_type')
        self.write_to_tsv(self.carina_generator.retailer_fetch_type(), 'vela', 'retailer_fetch_type')
        self.write_to_tsv(self.carina_generator.reward_config(), 'vela', 'reward_config')


        # POLARIS GENERATION
        self.write_to_tsv(self.polaris_generator.retailer_config(), 'polaris', 'retailer_config')
        self.write_to_tsv(self.polaris_generator.account_holder(), 'polaris', 'account_holder')
        self.write_to_tsv(self.polaris_generator.account_holder_profile(), 'polaris', 'account_holder_profile')
        self.write_to_tsv(self.polaris_generator.account_holder_marketing_preference(), 'polaris',
                          'account_holder_marketing_preference')



    @staticmethod
    def write_to_tsv(data, db, table):
        tsv_name = f"tsv-{db}-{table}.tsv"

        with open(tsv_name, 'w+') as f:
            tsv_writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar="", quotechar="")
            tsv_writer.writerows(data)



