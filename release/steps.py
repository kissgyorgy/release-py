import textwrap
from typing import List

import click

from .parser import Step, render_text
from .types import Variables


def wait_for_enter_press():
    click.echo("Press enter to continue...", nl=False)
    char = ""
    while char != "\r":
        char = click.getchar()


def run_steps(steps: List[Step], variables: Variables):
    for stepnum, step in enumerate(steps, start=1):
        title = render_text(step.title, variables)
        click.secho(f"{stepnum}. {title}", fg="yellow")

        if step.description:
            description = render_text(step.description, variables)
            indented_description = textwrap.indent(description, "   ")
            click.echo(indented_description)

        wait_for_enter_press()
        click.echo("✅\n")
