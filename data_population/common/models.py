from sqlalchemy import Table
from sqlalchemy.orm import relationship
from data_population.common.db import PolarisDB


class RetailerConfig(PolarisDB().Base):
    __table__ = Table("retailer_config", PolarisDB().metadata, autoload=True)
