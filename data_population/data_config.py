from dataclasses import dataclass


@dataclass
class DataConfig:
    membership_plans: int
    users: int
    users_history: int
    membership_cards: int
    membership_cards_history: int
    payment_cards: int
    payment_cards_history: int
    transactions: int


data_configs = {
    "benchmark": DataConfig(
        membership_plans=7,
        users=500,
        users_history=600,
        membership_cards=5000,
        membership_cards_history=6000,
        payment_cards=2000,
        payment_cards_history=3000,
        transactions=10000,
    ),
    "benchmark_2": DataConfig(
        membership_plans=7,
        users=500,
        users_history=600,
        membership_cards=5000,
        membership_cards_history=6000,
        payment_cards=2000,
        payment_cards_history=3000,
        transactions=10000,
    ),
}
