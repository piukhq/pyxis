import json

from datetime import datetime, timedelta
from random import choice, randint

from data_population.common.utils import id_generator
from data_population.tsv_creation.fixtures.common import audit_data


def retry_task(config, task_type_ids_dict) -> list:
    task_type_ids = task_type_ids_dict.values()
    id_gen = id_generator(1)
    retry_tasks = []
    total_task_types = len(task_type_ids)
    retry_tasks_per_task_type = int(config.retry_tasks / total_task_types)
    for task_type_id in task_type_ids:
        for _ in range(1, retry_tasks_per_task_type + 1):
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


def task_type_key_value(task_type_ids_dict, task_type_keys_dict, rows) -> list:
    task_type_ids = task_type_ids_dict.values()
    task_type_key_value_rows = []
    total_task_types = len(task_type_ids)
    total_task_type_key_values = int(rows / total_task_types)
    for task_type_id in task_type_ids:
        for task_type_key_id, value in task_type_keys_dict[task_type_id].items():
            id_gen = id_generator(1)
            for _ in range(1, total_task_type_key_values + 1):
                now = datetime.utcnow()
                task_type_key_value_rows.append(
                    [
                        now,  # created_at
                        now,  # updated_at
                        value,  # task_type_key_value
                        next(id_gen),  # retry_task_id
                        task_type_key_id,  # task_type_key_id
                    ]
                )
    return task_type_key_value_rows
