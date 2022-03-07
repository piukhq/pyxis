from dataclasses import dataclass


@dataclass
class DataConfig:
    retailers: int
    account_holders: int
    campaigns_per_retailer: int
    earn_rule_per_campaign: int
    membership_cards_history: int
    payment_cards: int
    payment_cards_history: int
    transactions: int


data_configs = {
    "benchmark": DataConfig(
        retailers=10,
        account_holders=1000,
        campaigns_per_retailer=1,
        earn_rule_per_campaign=1,
        membership_cards_history=6000,
        payment_cards=2000,
        payment_cards_history=3000,
        transactions=10000,
    )
}
