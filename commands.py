import click
import logging

from data_population.data_config import data_configs
from data_population.tasks import populate, hello, data_mapping

logger = logging.getLogger("Data-controller")


tasks = {
    "populate-db": populate,
    "hello": hello,
}

param_options = {
    "tasks": list(tasks.keys()),
    "group": list(data_mapping.keys()),
    "data_configuration": list(data_configs.keys()),
}

TASK_HELP = f"Task you wish to perform (required) " f"Please choose from: {param_options['tasks']}"

DATA_CONFIGURATION_HELP = f"Data Configuration (required). " f"Please choose from: {param_options['data_config']}"

DB_HELP = (
    f"Database to be populated. If none is selected, all databases will be selected. Please choose from: "
    f"{param_options['group']}"
)


@click.command()
@click.option("-t", "--task-name", type=click.Choice(param_options["tasks"]), required=True, help=TASK_HELP)
@click.option(
    "-d", "--data-configuration", type=click.Choice(param_options["data_configuration"]), required=True, help=DATA_CONFIGURATION_HELP
)
@click.option(
    "-db", "--db", type=click.Choice(param_options["group"]), default=None, help=DB_HELP
)
def main(task_name: str, data_configuration: str, db: str):
    tasks[task_name](data_configuration, db)


if __name__ == "__main__":
    main()
