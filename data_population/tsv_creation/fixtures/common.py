from typing import Union

from sqlalchemy.orm import Session

from db_query import get_task_type

audit_data = [
    {
        "request": {"url": "http://polaris-api/bpl/loyalty/test-retailer/accounts/foo/adjustments"},
        "response": {"body": "{new_balance:375, campaign_slug:test-campaign-1}", "status": 200},
        "timestamp": "2021-11-01T15:39:40.050413",
    },
    {
        "request": {"url": "http://carina-api/bpl/vouchers/test-retailer/vouchers/10percentoff/allocation"},
        "response": {"body": "{}", "status": 202},
        "timestamp": "2021-11-01T15:39:40.138773",
    },
]


def _get_task_type_key_ids_and_value(db_session, task_name: str) -> dict:
    task_type = get_task_type(db_session, task_name=task_name)
    return task_type.get_key_ids_by_name()


def process_type_key_ids_and_values(
    db_session: "Session",
    task_type_ids: dict[str, int],
    task_type_key_value_fixture: dict[int, dict[int, Union[str, int]]],
) -> dict[int, dict[int, Union[str, int]]]:
    task_type_keys: dict[int, dict] = {}
    task_names: list[str] = list(task_type_ids.keys())
    for task_name in task_names:
        task_type_keys[task_type_ids[task_name]] = _get_task_type_key_ids_and_value(db_session, task_name)

    for task_type_id, task_type_key_dict in task_type_key_value_fixture.items():
        for key, value in task_type_keys.items():
            if key == task_type_id:
                for k in list(task_type_key_dict.keys()):
                    task_type_key_dict[value[k]] = task_type_key_dict.pop(k)

    return task_type_key_value_fixture
