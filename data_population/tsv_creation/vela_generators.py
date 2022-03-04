import time
import datetime
import uuid
import random

from settings import fake
from data_population.polaris import components


class VelaFactory:

    def __init__(self, data_config):
        self.now = datetime.datetime.utcnow()
        self.data_config = data_config

    def retailer_rewards(self):
        retailers = []
        for count in range(1, self.data_config.retailers + 1):
            retailers.append([
                    count,  # id
                    f"retailer_{count}"  # slug
                    ])
        return retailers

    def account_holder_profile(self):
        account_holder_profiles = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holder_profiles.append([
                fake.first_name(),  # first name
                fake.last_name(),  # surname
                self.now,  # date_of_birth
                "01234567891",  # phone
                "Fake_first_line_address",  # address_line1
                "Fake_second_line_address",  # address_line2
                "Fake_postcode",  # retailer_id
                "Fake_city",  # city
                count,  # account_holder_id
                count,  # id
                "",  # custom
                ])
        return account_holder_profiles


