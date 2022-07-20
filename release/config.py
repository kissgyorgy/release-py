import datetime as dt
from pathlib import Path
from typing import List, Mapping, Optional

import yaml
from pydantic import BaseModel, validator

from .git import GitConfig
from .parser import render_with_envvars
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
    git: Optional[GitConfig]
    set_variable: Optional[str]

    @property
    def has_action(self):
        # currently git is the only action-type field
        return self.git is not None

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

    @validator("steps", each_item=True)
    def validate_set_variable(cls, v: Step):
        if not v.has_action and v.set_variable:
            raise ValueError(f"has no action, but variable {v.set_variable!r} is set")
        return v


def load_release_config(path: Path) -> "ReleaseConfig":
    with path.open("r") as f:
        release_dict = yaml.safe_load(f)
    return ReleaseConfig.parse_obj(release_dict)


def parse_version(version: Version) -> str:
    if version.from_time:
        format_str = version.from_time
        now = dt.datetime.now()
        return f"{now:{format_str}}"

    raise ValueError


def parse_initial_variables(
    config: "ReleaseConfig", env: Mapping[str, str]
) -> Variables:
    version = parse_version(config.version)
    variables = {"version": version}
    for name, value in config.variables.items():
        variables[name] = render_with_envvars(value, variables, env)
    return variables
