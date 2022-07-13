from dataclasses import dataclass
from random import randint
from typing import Any

import psycopg2

from faker import Faker

import settings

_fake = Faker(locale="en_GB")


#  We will generate retry rows for each of the following task types equal to the sum of their data_config values:
polaris_retry_task_types_to_populate = {
    "enrolment-callback": ["account_holders"],
    "account-holder-activation": ["account_holders"],
    "create-campaign-balances": ["account_holders"],
    "send-welcome-email": ["account_holders"],
    "pending-reward-allocation": ["pending_rewards", "allocated_rewards"],
    "convert-pending-rewards": ["pending_rewards"],
    "delete-pending-rewards": ["pending_rewards"],
}
vela_retry_task_types_to_populate = {"reward-adjustment": ["transactions"]}
carina_retry_task_types_to_populate = {"reward-issuance": ["allocated_rewards"]}

_tk_type_to_faker = {
    "STRING": _fake.pystr,
    "INTEGER": _fake.pyint,
    "FLOAT": _fake.pyfloat,
    "BOOLEAN": lambda: bool(randint(0, 1)),
    "DATE": _fake.date,
    "DATETIME": _fake.date_time,
    "JSON": lambda: {_fake.pystr(): _fake.pystr() for _ in range(2)},
}


@dataclass
class TaskTypeKeyData:
    type: str
    task_type_key_id: int


def fetch_task_types_ids(db_name: str) -> dict[str, int]:
    db_uri = settings.DB_CONNECTION_URI.replace("/postgres?", f"/{db_name}?")
    task_type_query = "SELECT name, task_type_id FROM task_type"

    with psycopg2.connect(db_uri) as db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute(task_type_query)
            result = dict(cursor.fetchall())

    db_connection.close()
    return result


def _generate_fake_val_for_type(tk_type: str) -> Any:
    if tk_type not in _tk_type_to_faker:
        raise ValueError(f"Could not find {tk_type} type, allowed types {_tk_type_to_faker}")

    return _tk_type_to_faker[tk_type]()


def generate_task_type_key_values(db_name: str) -> dict[int, dict[int, Any]]:
    db_uri = settings.DB_CONNECTION_URI.replace("/postgres?", f"/{db_name}?")
    task_type_key_query = "SELECT type, task_type_key_id, task_type_id FROM task_type_key"
    task_type_key_data: dict[int, list[TaskTypeKeyData]] = {}

    with psycopg2.connect(db_uri) as db_connection:
        with db_connection.cursor() as cursor:

            cursor.execute(task_type_key_query)

            for tk_type, tk_id, tt_id in cursor.fetchall():

                if tt_id not in task_type_key_data:
                    task_type_key_data[tt_id] = []

                task_type_key_data[tt_id].append(TaskTypeKeyData(type=tk_type, task_type_key_id=tk_id))

    db_connection.close()

    return {
        tt_id: {tk_data.task_type_key_id: _generate_fake_val_for_type(tk_data.type) for tk_data in values}
        for tt_id, values in task_type_key_data.items()
    }
