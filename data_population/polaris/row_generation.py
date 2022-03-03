import time
import datetime
import uuid

from settings import fake
import components


class PolarisFactory:

    def __init__(self):
        self.now = datetime.datetime.utcnow()

    def retailer_config(self, count):
        return [
            count,  # id
            f"Retailer {count}",  # name
            f"retailer_{count}",  # slug
            str(count).zfill(4),  # account_number_prefix (e.g. '0013')
            10,  # account_number_length
            self.now,  # created_at
            components.profile_config,  # profile_config
            self.now,  # updated_at
            components.marketing_preferences,  # marketing_preference
            "Performance Retailer",  # loyalty_name
            "",  # email_header_image
            "Performance Retailer <welcome@performance_retailer.com>",  # welcome_email_from
            "Welcome to Performance Retailer!"  # welcome_email_subject
            ]

    def account_holder(self, count, retailer_id):
        return [
            fake.email(),  # email
            'ACTIVE',  # status
            "hello",  # account_number
            True,  # is_active
            False,  # is_superuser
            self.now,  # created_at
            retailer_id,  # retailer_id
            self.now,  # updated_at
            uuid.uuid4(),  # account_holder_uuid
            count,  # id
            "",  # opt_out_token
            ]
