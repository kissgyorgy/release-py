import datetime as dt
from pathlib import Path
from typing import List, Mapping, Optional

import yaml
from pydantic import BaseModel, root_validator, validator

from .git import GitConfig
from .parser import render_with_envvars
from .runner import RunConfig
from .types import Variables


class Version(BaseModel):
    from_time: Optional[str]

    @validator("from_time")
    def check_version(cls, v):
        if not v:
            raise ValueError("Version must be specified")
        return v


class Step(BaseModel):
    # TODO: make title and desc optional
    title: str
    description: Optional[str] = None
    git: Optional[GitConfig] = None
    set_variable: Optional[str] = None
    run: Optional[RunConfig] = None
    gitlab: Optional[dict] = None
    environments: Optional[list] = None
    checklist: Optional[list] = None
    open_url: Optional[str] = None

    @property
    def has_action(self):
        # currently git is the only action-type field
        return self.git is not None

    @validator("title")
    def strip_title(cls, v: str) -> str:
        return v.strip()

    @validator("description")
    def add_newline(cls, v: str) -> str:
        if v and not v.endswith("\n"):
            return v + "\n"
        return v

    @root_validator(pre=True)
    def validate_only_one_action(cls, values):
        if "git" in values and "run" in values:
            raise ValueError(
                "Only 1 action can be specified for a Step at once.\n"
                '  Specified actions: "git" and "run".'
            )
        return values


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
