import uuid

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from random import choice, randint

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.common import AccountHolderStatuses, marketing_preferences, profile_config
from settings import fake


class CosmosGenerators:
    def __init__(self, data_config: DataConfig, account_holder_uuids: list[uuid.UUID]) -> None:
        self.now = datetime.now(timezone.utc)
        self.data_config = data_config
        self.all_account_holder_retailers: dict = {}
        self.allocated_rewards: list = []
        self.unallocated_rewards: list = []
        self.account_holders_by_retailer: dict = {}
        self.account_holder_uuids = account_holder_uuids
        self.campaigns_by_retailer: defaultdict = defaultdict(list)
        self.retailers_by_campaign: dict = {}
        self.end_date = self.now + timedelta(weeks=100)
        self.data_config = data_config
        self.retailers_by_reward_config: dict = {}
        self.retailer_ids: list = []
        # self.reward_configs_by_retailer: dict = {}

    def get_account_holders_by_retailer(self) -> dict:
        if not self.account_holders_by_retailer:
            for retailer in range(1, self.data_config.retailers + 1):
                self.account_holders_by_retailer[retailer] = [
                    k for k, v in self.all_account_holder_retailers.items() if v == retailer
                ]

        return self.account_holders_by_retailer

    def retailer(self) -> list:
        """Generates n retailer objects (n defined in data_config)"""
        return [
            [
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                f"Retailer {count}",  # name
                f"retailer_{count}",  # slug
                str(count).zfill(4),  # account_number_prefix (e.g. '0013')
                10,  # account_number_length
                profile_config,  # profile_config
                marketing_preferences,  # marketing_preference_config
                f"Performance Retailer {count}",  # loyalty_name
                "ACTIVE",  # status
                "NULL",  # balance_lifespan
                "NULL",  # balance_reset_advanced_warning_days
            ]
            for count in range(1, self.data_config.retailers + 1)
        ]

    def campaign(self) -> list:
        """Generates campaigns (n defined in data_config as retailers * campaigns per retailer)"""
        id_gen = id_generator(1)
        campaigns = []
        for count in range(1, self.data_config.retailers + 1):
            for _ in range(1, self.data_config.campaigns_per_retailer + 1):
                if campaign_id := next(id_gen, None):
                    campaigns.append(
                        [
                            campaign_id,  # id
                            self.now,  # created_at
                            self.now,  # updated_at
                            "ACTIVE",  # status
                            f"Campaign {campaign_id}",  # name
                            f"campaign_{campaign_id}",  # slug
                            count,  # retailer_id
                            self.data_config.loyalty_type,  # loyalty_type
                            self.now,  # start_date
                            self.end_date,  # end_date (set to 100 weeks in the future)
                        ]
                    )
                    self.campaigns_by_retailer[count].append(campaign_id)
                    self.retailers_by_campaign[campaign_id] = count
                else:
                    raise ValueError("no campaign_id value found")

        return campaigns

    def earn_rule(self) -> list:
        """
        Generates earn_rules (n defined in data_config as retailers * campaigns per retailer * earn_rules per campaign)
        """
        id_gen = id_generator(1)
        total_campaigns = self.data_config.retailers * self.data_config.campaigns_per_retailer
        earn_rules: list = []
        increment = 500 if self.data_config.loyalty_type == "STAMPS" else "NULL"
        for campaign_count in range(1, total_campaigns + 1):
            earn_rules.extend(
                [
                    next(id_gen),  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    100,  # threshold
                    increment,  # increment
                    1,  # increment_multiplier
                    0,  # max_amount
                    campaign_count,  # campaign_id
                ]
                for _ in range(self.data_config.earn_rule_per_campaign)
            )
        return earn_rules

    def reward_config(self) -> list:
        """
        Generates n reward_configs (n defined in data_config as retailers * campaigns per retailer)
        Assumes a 121 relationship between reward_config and reward_rule/campaign (i.e. only one config
        per campaign)
        """
        id_gen = id_generator(1)
        reward_configs = []

        for retailer_count in range(1, self.data_config.retailers + 1):
            for _ in range(self.data_config.campaigns_per_retailer):
                reward_config_id = next(id_gen)

                reward_configs.append(
                    [
                        reward_config_id,  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        f"reward_{reward_config_id}",  # reward_slug
                        retailer_count,  # retailer_id
                        1,  # fetch_type_id
                        "TRUE",  # active
                        {"validity_days": 90},  # required_fields_values
                    ]
                )

                self.retailers_by_reward_config[reward_config_id] = retailer_count
                # self.reward_configs_by_retailer[retailer_count].append(reward_config_id)

        return reward_configs

    def reward_rule(self) -> list:
        """Generates reward_rules (n defined in data_config as retailers * campaigns per retailer (1-1 w/campaigns))"""

        id_gen = id_generator(1)
        reward_rules = []
        for _ in range(1, self.data_config.retailers + 1):
            for _ in range(self.data_config.campaigns_per_retailer):
                id_ = next(id_gen)
                reward_rules.append(
                    [
                        id_,  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        500,  # reward_goal
                        self.data_config.allocation_window,  # allocation_window
                        self.data_config.reward_cap,  # reward_cap
                        id_,  # campaign_id
                        id_,  # reward_config_id
                    ]
                )
        return reward_rules

    def account_holder(self) -> list:  # sourcery skip: use-assigned-variable
        """Generates n account_holders (n defined in data_config)"""

        account_holders = []
        for count in range(1, self.data_config.account_holders + 1):
            account_id = count
            account_holder_uuid = self.account_holder_uuids.pop()
            retailer_id = randint(1, self.data_config.retailers)
            account_holders.append(
                [
                    account_id,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    f"user_{count}@bink-performancetest.com",  # email
                    AccountHolderStatuses.ACTIVE,  # status
                    f"{fake.credit_card_number()}_{count}",  # account_number
                    account_holder_uuid,  # account_holder_uuid
                    uuid.uuid4(),  # opt_out_token
                    retailer_id,  # retailer_id
                ]
            )
            self.all_account_holder_retailers[account_id] = retailer_id

        return account_holders

    def account_holder_profile(self) -> list:
        """Generates n account_holder_profiles (n defined in data_config (1-1 w/account_holders))"""
        return [
            [
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                count,  # account_holder_id
                fake.first_name(),  # first name
                fake.last_name(),  # surname
                self.now,  # date_of_birth
                "01234567891",  # phone
                "Fake_first_line_address",  # address_line1
                "Fake_second_line_address",  # address_line2
                "Fake_postcode",  # postcode
                "Fake_city",  # city
                "",  # custom
            ]
            for count in range(1, self.data_config.account_holders + 1)
        ]

    def retailer_store(self) -> list:
        """Generated retailer store objects for retailers"""
        stores = []
        id_ = id_generator(1)
        for retailer_count in range(1, self.data_config.retailers + 1):
            for store_count in range(1, self.data_config.stores_per_retailer + 1):
                stores.append(
                    [
                        next(id_),  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        f"Store {retailer_count}-{store_count}",  # store_name
                        f"mid-{retailer_count}-{store_count}",  # mid
                        retailer_count,  # retailer_id
                    ]
                )
        return stores

    def marketing_preference(self) -> list:
        """Generates account_holder_marketing_preferences (n defined in data_config (1-1 w/account_holders))"""
        return [
            [
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                count,  # account_holder_id
                "marketing_pref",  # key_name
                "True",  # value
                "BOOLEAN",  # value_type
            ]
            for count in range(1, self.data_config.account_holders + 1)
        ]

    def campaign_balance(self) -> list:
        """Generates account_holder_campaign_balances (n defined in data_config (1-1 w/account_holders))"""
        account_holder_campaign_balances = []
        for account_holder_id in range(1, self.data_config.account_holders + 1):
            retailer_id = self.all_account_holder_retailers[account_holder_id]
            campaign_id = choice(self.campaigns_by_retailer[retailer_id])

            account_holder_campaign_balances.append(
                [
                    account_holder_id,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_id,  # account_holder_id
                    campaign_id,  # campaign_id
                    0,  # balance
                    "NULL",  # reset_date
                ]
            )
        return account_holder_campaign_balances

    def transaction(self) -> list:
        """Generates transactions (n defined in n data_config)"""

        transactions = []
        account_holder_retailers: list[tuple[int, int]] = list(self.all_account_holder_retailers.items())
        for count in range(1, self.data_config.transactions + 1):
            account_holder_id, retailer_id = choice(account_holder_retailers)
            transactions.append(
                [
                    count,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    account_holder_id,  # account_holder_id
                    retailer_id,  # retailer_id
                    f"tx_{count}",  # transaction_id
                    randint(500, 1000),  # amount
                    f"mid-{retailer_id}-{choice(list(range(1, self.data_config.stores_per_retailer + 1)))}",  # mid
                    self.now,  # datetime
                    f"tx_payment_{count}",  # payment_transaction_id
                    "TRUE",  # processed
                ]
            )
        return transactions

    def transaction_earn(self) -> list:
        """Generates transaction_earns (one per transaction)"""

        return [
            [
                count,  # id
                self.now,  # created_at
                self.now,  # updated_at
                count,  # transaction_id
                "ACCUMULATOR",
                randint(500, 1000),  # earn_amount
            ]
            for count in range(1, self.data_config.transactions + 1)
        ]

    def reward(self) -> list:
        """
        Generates n rewards/vouchers (total n defined as allocated_rewards + pending_rewards + spare_rewards in
        data_config).
        """

        rewards = []

        for reward in range(
            self.data_config.allocated_rewards + self.data_config.pending_rewards + self.data_config.spare_rewards
        ):
            account_holders_by_retailer = self.get_account_holders_by_retailer()
            # first <allocated_rewards> rewards should be set as allocated
            reward_id = str(uuid.uuid4())
            reward_config_id = choice(list(self.retailers_by_reward_config))
            retailer_id = self.retailers_by_reward_config[reward_config_id]  # retailer_id
            account_holder_id = (
                choice(account_holders_by_retailer[retailer_id])
                if reward < self.data_config.allocated_rewards
                else None
            )
            campaign_id = choice(self.campaigns_by_retailer[retailer_id]) if account_holder_id else "NULL"
            code = str(uuid.uuid4())

            rewards.append(
                [
                    reward,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    reward_id,  # reward_uuid
                    reward_config_id,  # reward_config_id
                    account_holder_id or "NULL",  # account_holder_id
                    code,  # code
                    "FALSE",  # deleted
                    self.now,  # issued_date
                    self.end_date,  # expiry_date
                    "NULL",  # redeemed_date
                    "NULL",  # cancelled_date,
                    "http://associated.url",  # associated_url
                    retailer_id,  # retailer_id
                    campaign_id,  # campaign_id
                    "NULL",  # reward_file_log_id
                ]
            )

            if not account_holder_id:
                self.unallocated_rewards.append(
                    {
                        "reward_uuid": reward_id,
                        "reward_config_id": reward_config_id,
                        "retailer_id": retailer_id,
                        "code": code,
                    }
                )

        return rewards

    def pending_reward(self) -> list:
        """
        Generates pending_rewards (1-1 w/ data_config.pending_rewards)
        """

        pending_rewards = []
        account_holders_by_retailer = self.get_account_holders_by_retailer()
        pending_reward_value = 500
        if self.data_config.pending_reward_conversion:
            conversion_date = self.now + timedelta(days=-1)
        else:
            conversion_date = self.now + timedelta(days=1)

        for reward_count in range(1, self.data_config.pending_rewards + 1):
            reward = self.unallocated_rewards.pop()

            pending_rewards.append(
                [
                    reward_count,  # id
                    self.now,  # created_at
                    self.now,  # updated_at
                    uuid.uuid4(),  # pending_reward_uuid
                    choice(account_holders_by_retailer[reward["retailer_id"]]),  # account_holder_id
                    choice(self.campaigns_by_retailer[reward["retailer_id"]]),  # campaign_id
                    self.now,  # created_date
                    conversion_date,  # conversion_date
                    pending_reward_value,  # value
                    1,  # count
                    pending_reward_value,  # total_cost_to_user
                ]
            )
        return pending_rewards

    def email_template_types(self) -> list:
        """Generates email_template_type rows - one of each per retailer"""
        row_id = id_generator(1)
        template_types: list = []
        for _ in range(1, self.data_config.retailers + 1):
            for slug in ("WELCOME_EMAIL", "REWARD_ISSUANCE", "PURCHASE_PROMPT"):
                template_types.extend(
                    [
                        self.now,  # created_at
                        self.now,  # updated_at
                        next(row_id),  # id
                        slug,  # slug
                    ]
                    for _ in range(1, self.data_config.retailers + 1)
                )
        return template_types

    def email_template(self) -> list:
        """
        Generates email_template rows (2-1 w/ data_config.retails)
        Different email templates for each retailer
        """

        email_templates = []
        row_id = id_generator(1)

        for retailer_id in range(1, self.data_config.retailers + 1):
            for template_type_id in range(1, 4):
                id_ = next(row_id)
                email_templates.append(
                    [
                        id_,  # id
                        self.now,  # created_at
                        self.now,  # updated_at
                        id_,  # template_id
                        retailer_id,  # retailer_id
                        "NULL",  # required_field_values
                        template_type_id,  # email_type_id
                    ]
                )
        return email_templates

    def retailer_fetch_type(self) -> list:
        """Generates n retailer<->fetch_type links (1 per retailer (fetch type 1 only))"""
        return [
            [
                self.now,  # created_at
                self.now,  # updated_at
                retailer_count,  # retailer_id
                1,  # fetch_type_id (1=Preloaded, 2=Jigsaw)
                "",  # agent_config
            ]
            for retailer_count in range(1, self.data_config.retailers + 1)
        ]

    def reward_update(self) -> list:
        """
        Generates n reward_updates. n is defined at the dataconfig
        Note: This re-uses uuids from self.reward_id. So must be run after
        reward generator
        """

        reward_uuids = [item["reward_uuid"] for item in self.allocated_rewards]

        return [
            [
                self.now,  # created_at
                self.now,  # updated_at
                count,  # id
                choice(reward_uuids),  # reward_uuid
                self.now.date(),  # date
                choice(["CANCELLED", "REDEEMED", "ISSUED"]),  # status
            ]
            for count in range(self.data_config.reward_updates)
        ]
