from data_population.data_config import DataConfig
from row_generation import PolarisGenerators
from data_population.common.db import PolarisDB
from data_population.common.models import RetailerConfig


class TSVHandler:

    def __init__(self, data_config: DataConfig):
        self.id = 0
        self.config = data_config
        self.generator = PolarisGenerators()

    def create_tsv_files(self):
        self.create_retailers()

    def create_retailers(self):

        all_data = []
        for i in range(100, 100000):
            all_data.append(self.generator.generate_retailer(i + 1))

        with PolarisDB().open() as session:
            session.execute(RetailerConfig.__table__.delete().where(RetailerConfig.loyalty_name == ""))
            session.commit()
            session.bulk_save_objects(all_data)
            session.commit()

