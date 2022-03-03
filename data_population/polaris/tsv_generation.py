from data_population.data_config import DataConfig
from data_population.polaris.data_generation import PolarisFactory


class TSVHandler:

    def __init__(self, data_config: DataConfig):
        self.id = 0
        self.config = data_config
        self.create_data = PolarisFactory(data_config=data_config)

        self.retailers = []
        self.account_holders = []
        self.account_holder_profiles = []

    def create_tsv_files(self):
        self.retailers = self.create_data.retailer_config()
        self.account_holders = self.create_data.account_holder()
        self.account_holder_profiles = self.create_data.account_holder_profile()

        print(len(self.retailers))
        print(len(self.account_holders))
        print(len(self.account_holder_profiles))



