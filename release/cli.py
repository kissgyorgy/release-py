import os
from pathlib import Path

import click
from pydantic import ValidationError

from .config import load_release_config, parse_initial_variables
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
@click.pass_context
def start(ctx: click.Context):
    try:
        config = load_release_config(ctx.obj["release_file"])
    except ValidationError as e:
        raise click.UsageError(str(e))
    variables = parse_initial_variables(config, os.environ)
    try:
        run_steps(config.steps, variables)
    except Exception as e:
        click.secho(f"\n{e}", fg="red")
        ctx.exit(1)


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
