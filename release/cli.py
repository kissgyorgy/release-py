import os
from pathlib import Path

import click
from pydantic import ValidationError

from .config import load_release_config, parse_initial_variables
from .steps import run_steps


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-f",
    "release_file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    default="release.yaml",
)
@click.pass_context
def main(ctx: click.Context, release_file: Path):
    # ensure that ctx.obj exists and is a dict
    # in case main() is called by other means
    ctx.ensure_object(dict)
    ctx.obj["release_file"] = release_file


@main.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def start(ctx: click.Context):
    release_file = ctx.obj["release_file"]
    if not release_file.exists():
        raise click.UsageError(f"Release file '{release_file}' does not exist")
    try:
        config = load_release_config(release_file)
    except ValidationError as e:
        raise click.UsageError(str(e))
    variables = parse_initial_variables(config, os.environ)
    try:
        run_steps(config.steps, variables)
    except Exception as e:
        click.secho(f"\n{e}", fg="red")
        ctx.exit(1)


@main.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def validate(ctx: click.Context):
    release_file = ctx.obj["release_file"]
    if not release_file.exists():
        raise click.UsageError(f"Release file '{release_file}' does not exist")
    click.echo(f"Validating {release_file.resolve()}")
    try:
        load_release_config(release_file)
    except ValidationError as e:
        click.secho(e, fg="yellow")
        ctx.exit(1)
    else:
        click.echo("Configuration file seems valid!")


@main.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--restart-on-change",
    is_flag=True,
    help="Restart the TUI when Python files in the release package change",
)
@click.pass_context
def tui(ctx: click.Context, restart_on_change: bool):
    import importlib

    from . import tui

    release_file = ctx.obj["release_file"]
    if not release_file.exists():
        raise click.UsageError(f"Release file '{release_file}' does not exist")

    # Initialize state that persists across restarts
    persistent_state = {"current_step_index": 0, "variables": None}

    while True:
        try:
            app = tui.ReleaseApp(
                config_path=release_file,
                restart_on_change=restart_on_change,
                initial_state=persistent_state,
            )
            app.run()

            # If restart_on_change is disabled or app didn't request restart, exit
            if not restart_on_change or not getattr(app, "should_restart", False):
                break

            # Preserve state for next restart
            persistent_state = app.get_state()
            importlib.reload(tui)

            # Brief pause before restart to avoid rapid restarts
            import time

            time.sleep(0.1)

        except ValidationError as e:
            click.secho(f"Configuration error: {e}", fg="red")
            ctx.exit(1)
        except Exception as e:
            click.secho(f"Error: {e}", fg="red")
            ctx.exit(1)
