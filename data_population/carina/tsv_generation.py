from ..data_config import DataConfig


class TSVHandler:

    def __init__(self):
        self.id = 0

    def create_tsv_files(self, data_config: DataConfig):
        self.create_retailers()

    def create_retailers(self):
        for i in range(data_config.retailers):
            all_data.append

