import datetime as dt
from pathlib import Path
from string import Template
from typing import List, Mapping, Optional

import yaml
from pydantic import BaseModel, validator

from .types import Variables


class Version(BaseModel):
    from_time: Optional[str]

    @validator("*")
    def check_version(cls, values):
        if not values:
            raise ValueError("Version must be specified")
        return values


class Step(BaseModel):
    title: str
    description: Optional[str]

    @validator("title")
    def strip_title(cls, v: str) -> str:
        return v.strip()

    @validator("description")
    def add_newline(cls, v: str) -> str:
        if not v.endswith("\n"):
            return v + "\n"
        return v


class ReleaseConfig(BaseModel):
    version: Version
    variables: Variables
    steps: List[Step]


def load_release_config(path: Path) -> ReleaseConfig:
    with path.open("r") as f:
        release_dict = yaml.safe_load(f)
    return ReleaseConfig.parse_obj(release_dict)


def parse_version(version: Version) -> str:
    if version.from_time:
        format_str = version.from_time
        now = dt.datetime.now()
        return f"{now:{format_str}}"

    raise ValueError


def parse_initial_variables(config: ReleaseConfig, env: Mapping[str, str]) -> Variables:
    version = parse_version(config.version)
    variables = {"version": version}
    for name, value in config.variables.items():
        variables[name] = render_with_envvars(value, variables, env)
    return variables


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
