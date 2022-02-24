import click
import logging

from data_population.data_config import data_configs
from data_population.tasks import populate_db, hello, DataGroups

logger = logging.getLogger("Data-controller")


tasks = {
    "populate-db": populate_db,
    "hello": hello,
}

param_options = {
    'tasks': list(tasks.keys()),
    'group': [group.value for group in DataGroups],
    'data_config': list(data_configs.keys())
}

TASK_HELP = (
    f"Task you wish to perform (required) "
    f"Please choose from: {param_options['tasks']}"
)

DATA_CONFIG_HELP = (
    f"Data Configuration (required). "
    f"Please choose from: {param_options['data_config']}"
)

GROUP_CONFIG_HELP = (
    f"Group of data you wish to interact with. Defaults to 'all'. "
    f"Please choose from: {param_options['group']}"
)


@click.command()
@click.option("-t", "--task-name",
              type=click.Choice(param_options['tasks']),
              required=True,
              help=TASK_HELP)
@click.option("-d", "--data-config-name",
              type=click.Choice(param_options['data_config']),
              required=True,
              help=DATA_CONFIG_HELP)
@click.option("-g", "--group-config-name",
              type=click.Choice(param_options['group']),
              default="all",
              help=GROUP_CONFIG_HELP)
def main(task_name: str, group_config_name: str, data_config_name: str):
    tasks[task_name](group_config_name, data_config_name)


if __name__ == '__main__':
    main()
