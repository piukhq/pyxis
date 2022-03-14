import datetime
import random
import uuid

from data_population.tsv_creation.fixtures import AccountHolderStatuses, marketing_preferences, profile_config
from settings import fake


class PolarisGenerators:
    def __init__(self, data_config):
        self.now = datetime.datetime.utcnow()
        self.data_config = data_config

    def retailer_config(self) -> [list]:
        """Generates n retailer_configs (n defined in data_config)"""
        retailer_configs = []
        for count in range(1, self.data_config.retailers + 1):
            retailer_configs.append(
                [
                    count,  # id
                    f"Retailer {count}",  # name
                    f"retailer_{count}",  # slug
                    str(count).zfill(4),  # account_number_prefix (e.g. '0013')
                    10,  # account_number_length
                    self.now,  # created_at
                    profile_config,  # profile_config
                    self.now,  # updated_at
                    marketing_preferences,  # marketing_preference
                    "Performance Retailer",  # loyalty_name
                    "",  # email_header_image
                    "Performance Retailer <welcome@performance_retailer.com>",  # welcome_email_from
                    "Welcome to Performance Retailer!",  # welcome_email_subject
                ]
            )
        return retailer_configs

    def account_holder(self) -> [list]:
        """Generates n account_holders (n defined in data_config)"""
        account_holders = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holders.append(
                [
                    f"user_{count}@performancetest.com",  # email
                    AccountHolderStatuses.ACTIVE,  # status
                    str(fake.credit_card_number()),  # account_number
                    True,  # is_active
                    False,  # is_superuser
                    self.now,  # created_at
                    random.randint(1, self.data_config.retailers),  # retailer_id
                    self.now,  # updated_at
                    uuid.uuid4(),  # account_holder_uuid
                    count,  # id
                    uuid.uuid4(),  # opt_out_token
                ]
            )
        return account_holders

    def account_holder_profile(self) -> [list]:
        """Generates n account_holder_profiles (n defined in data_config (1-1 w/account_holders))"""
        account_holder_profiles = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holder_profiles.append(
                [
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
                ]
            )
        return account_holder_profiles

    def account_holder_marketing_preference(self) -> [list]:
        """Generates account_holders (n defined in data_config (1-1 w/account_holders))"""
        account_holder_marketing_preferences = []
        for count in range(1, self.data_config.account_holders + 1):
            account_holder_marketing_preferences.append(
                [
                    self.now,  # created_at
                    self.now,  # updated_at
                    count,  # id
                    count,  # account_holder_id
                    "marketing_pref",  # key_name
                    "True",  # value
                    "BOOLEAN",  # value_type
                ]
            )
        return account_holder_marketing_preferences
