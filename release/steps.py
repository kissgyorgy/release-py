import textwrap
from typing import List

import click
from .parser import Step


def wait_for_enter_press():
    click.echo("Press enter to continue...", nl=False)
    char = ""
    while char != "\r":
        char = click.getchar()


def run_steps(steps: List[Step]):
    for stepnum, step in enumerate(steps, start=1):
        click.secho(f"{stepnum}. {step.title}", fg="yellow")
        if step.description:
            indented_description = textwrap.indent(step.description, "   ")
            click.echo(indented_description)
        wait_for_enter_press()
        click.echo("✅\n")
