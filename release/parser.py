from string import Template
from typing import Mapping

from .types import Variables


class EnvTemplate(Template):
    """Substitute variables regularly, but environment variables need "env." prefix,
    and only with the braced syntax.
    For example: ${env.HOME} works, but $env.HOME does nothing.
    """

    braceidpattern = rf"(?:env\.)?{Template.idpattern}"


def render_with_envvars(text: str, variables: Variables, env: Mapping[str, str]):
    envvars = {f"env.{k}": v for k, v in env.items()}
    return EnvTemplate(text).safe_substitute({**envvars, **variables})


def render_text(text: str, variables: Variables) -> str:
    return Template(text).safe_substitute(variables)
