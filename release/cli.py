from pathlib import Path

import click
from pydantic import ValidationError

from .parser import load_release_config, parse_version
from .steps import run_steps


@click.group()
@click.option(
    "-f",
    "release_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default="release.yaml",
)
@click.pass_context
def main(ctx: click.Context, release_file: Path):
    # ensure that ctx.obj exists and is a dict
    # in case main() is called by other means
    ctx.ensure_object(dict)
    ctx.obj["release_file"] = release_file


@main.command()
@click.pass_obj
def start(obj: dict):
    try:
        config = load_release_config(obj["release_file"])
    except ValidationError as e:
        raise click.UsageError(str(e))
    version = parse_version(config.version)
    run_steps(version, config.steps)


@main.command()
@click.pass_context
def validate(ctx: click.Context):
    release_file = ctx.obj["release_file"]
    click.echo(f"Validating {release_file.resolve()}")
    try:
        load_release_config(release_file)
    except ValidationError as e:
        click.secho(e, fg="yellow")
        ctx.exit(1)
    else:
        click.echo("Configuration file seems valid!")
