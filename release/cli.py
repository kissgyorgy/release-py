from pathlib import Path
import click


from .parser import load_release_config
from .steps import run_steps


@click.command()
@click.option(
    "-f",
    "release_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default="release.yaml",
)
def main(release_file: Path):
    config = load_release_config(release_file)
    run_steps(config.steps)
