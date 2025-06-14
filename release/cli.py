import os
from pathlib import Path

import click
from pydantic import ValidationError

from .config import load_release_config, parse_initial_variables
from .steps import run_steps
from .tui import ReleaseApp


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


@main.command()
@click.option(
    "--restart-on-change",
    is_flag=True,
    help="Restart the TUI when Python files in the release package change",
)
@click.pass_context
def tui(ctx: click.Context, restart_on_change: bool):
    release_file = ctx.obj["release_file"]

    while True:
        try:
            app = ReleaseApp(
                config_path=release_file, restart_on_change=restart_on_change
            )
            app.run()

            # If restart_on_change is disabled or app didn't request restart, exit
            if not restart_on_change or not getattr(app, "should_restart", False):
                break

            # Brief pause before restart to avoid rapid restarts
            import time

            time.sleep(0.1)

        except ValidationError as e:
            click.secho(f"Configuration error: {e}", fg="red")
            ctx.exit(1)
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")
            ctx.exit(1)
