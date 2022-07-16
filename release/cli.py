from pathlib import Path
import click

from . import parser


@click.command()
@click.option(
    "-f",
    "release_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default="release.yaml",
)
def main(release_file: Path):
    pass
