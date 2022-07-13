from enum import Enum

from typer import Option, Typer, echo

from data_population.data_config import data_configs
from data_population.tasks import populate_all, upload_only

cli = Typer(name="Pyxis", help="performance sandbox test tool", no_args_is_help=True, add_completion=False)
tasks = {"populate-db": populate_all, "upload-only": upload_only}


TaskNameOptions = Enum("TaskNameOptions", {k.replace("-", "_"): k for k in tasks})  # type: ignore [misc]
DataConfigOptions = Enum("DataConfigOptions", {k.replace("-", "_"): k for k in data_configs})  # type: ignore [misc]


@cli.command(no_args_is_help=True)
def main(
    task_name: TaskNameOptions = Option(..., "--task-name", "-t", help="Task you wish to perform."),
    data_configuration: DataConfigOptions = Option(
        ..., "--data-configuration", "-d", help="Task's data configuration."
    ),
) -> None:
    """Runs the provided task with the provided configuration"""

    echo("Starting...")
    tasks[task_name.value](data_configuration.value)
    echo("Finished.")


if __name__ == "__main__":
    cli()
