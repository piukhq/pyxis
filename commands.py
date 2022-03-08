import click
import logging

from data_population.data_config import data_configs
from data_population.tasks import populate_all

logger = logging.getLogger("Data-controller")

tasks = {
    "populate-db": populate_all,
}

param_options = {
    "tasks": list(tasks.keys()),
    "data_configuration": list(data_configs.keys()),
}

TASK_HELP = f"Task you wish to perform (required) " f"Please choose from: {param_options['tasks']}"

DATA_CONFIGURATION_HELP = (
    f"Data Configuration (required). " f"Please choose from: {param_options['data_configuration']}"
)


@click.command()
@click.option("-t", "--task-name", type=click.Choice(param_options["tasks"]), required=True, help=TASK_HELP)
@click.option(
    "-d",
    "--data-configuration",
    type=click.Choice(param_options["data_configuration"]),
    required=True,
    help=DATA_CONFIGURATION_HELP,
)
def main(task_name: str, data_configuration: str):
    """Parses cli command -> tasks.py"""

    tasks[task_name](data_configuration)


if __name__ == "__main__":
    main()
