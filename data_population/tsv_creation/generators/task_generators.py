import json

from datetime import datetime, timedelta
from random import choice, randint

from data_population.common.utils import id_generator
from data_population.data_config import DataConfig
from data_population.tsv_creation.fixtures.common import audit_data


def retry_task(task_type_ids_dict: dict, task_types_to_populate: dict, data_config: DataConfig) -> list:
    """
    `tasks` = DataConfig.account_holder or DataConfig.reward_updates or DataConfig.transactions.

    `task_type_ids_dict` refer to the fixtures that should be passed. These will be app specific to
    polaris, carina and vela.
    """
    id_gen = id_generator(1)
    retry_tasks = []
    for task_type, value_list in task_types_to_populate.items():
        rowcount = sum(getattr(data_config, i) for i in value_list)
        for _ in range(1, rowcount + 1):
            task_type_id = task_type_ids_dict[task_type]
            now = datetime.utcnow()
            retry_tasks.append(
                [
                    now,  # created_at
                    now,  # updated_at
                    next(id_gen),  # retry_task_id
                    randint(1, 3),  # attempts
                    json.dumps(audit_data),  # audit data
                    now + timedelta(minutes=5),  # next_time_attempt
                    choice(["SUCCESS", "REQUEUED", "CANCELLED"]),  # status
                    task_type_id,  # task_type_id
                ]
            )
    return retry_tasks


def task_type_key_value(
    task_type_ids_dict: dict, task_type_keys_dict: dict, task_types_to_populate: dict, data_config: DataConfig
) -> list:
    """
    `tasks` = DataConfig.account_holder or DataConfig.reward_updates or DataConfig.transactions.

    `task_type_ids_dict` and `task_type_keys_dict` refer to the fixtures that should be passed.
    These will be app specific to polaris, carina and vela.
    """

    retry_task_id_gen = id_generator(1)

    task_type_key_value_rows = []
    for task_type, value_list in task_types_to_populate.items():
        rowcount = sum(getattr(data_config, i) for i in value_list)
        for _ in range(1, rowcount + 1):

            retry_task_id = next(retry_task_id_gen)

            for task_type_key_id, value in task_type_keys_dict[task_type_ids_dict[task_type]].items():
                now = datetime.utcnow()
                task_type_key_value_rows.append(
                    [
                        now,  # created_at
                        now,  # updated_at
                        value,  # task_type_key_value
                        retry_task_id,  # retry_task_id
                        task_type_key_id,  # task_type_key_id
                    ]
                )
    return task_type_key_value_rows
