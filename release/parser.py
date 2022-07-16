import datetime as dt
from pathlib import Path
from string import Template
from typing import List, Optional

import yaml
from pydantic import BaseModel, validator


class FromTimeVersion(BaseModel):
    timezone: Optional[str]
    format: str


class Version(BaseModel):
    from_time: Optional[FromTimeVersion]

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
    steps: List[Step]


def load_release_config(path: Path) -> ReleaseConfig:
    with path.open("r") as f:
        release_dict = yaml.safe_load(f)
    return ReleaseConfig.parse_obj(release_dict)


def parse_version(version: Version) -> str:
    if version.from_time:
        info: FromTimeVersion = version.from_time
        now = dt.datetime.now()
        return f"{now:{info.format}}"

    raise ValueError


def render_text(text: str, version: str) -> str:
    t = Template(text)
    replaced = t.safe_substitute(version=version)
    return replaced
