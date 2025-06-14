import textwrap
from typing import List, Optional

import click

from . import git, runner
from .config import Step
from .parser import render_text
from .types import Variables

PADDING = " " * 4


def wait_for_enter_press():
    click.echo("Press enter to continue...", nl=False)
    char = ""
    while char != "\r":
        char = click.getchar()


def print_title(stepnum: int, title: str, variables: Variables):
    title = render_text(title, variables)
    click.secho(f"{stepnum}. {title}", fg="yellow")


def print_description(description: Optional[str], variables: Variables):
    if description:
        description = render_text(description, variables)
        indented_description = textwrap.indent(description, PADDING)
        click.echo(indented_description)


def run_action(step: Step, variables: Variables) -> str:
    if step.git:
        output = git.run_step(step.git, variables)
    elif step.run:
        if step.run.command:
            click.echo(PADDING + f"$ {step.run.command}")
        output = runner.run(step.run)
    else:
        output = ""

    return output


def run_steps(steps: List[Step], variables: Variables):
    for stepnum, step in enumerate(steps, start=1):
        print_title(stepnum, step.title, variables)
        print_description(step.description, variables)
        output = run_action(step, variables)
        if step.set_variable:
            variables[step.set_variable] = output

        wait_for_enter_press()
        click.echo("✅\n")
