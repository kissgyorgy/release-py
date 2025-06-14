from pathlib import Path
from typing import Optional

from pydantic import BaseModel, root_validator

from ..types import Variables


class RunConfig(BaseModel):
    chdir: Path = Path.cwd()
    env: Variables = {}

    command: Optional[str]
    script: Optional[str]

    @root_validator(pre=True)
    def validate_at_least_one_command(cls, values):
        run_types = "command", "script"
        num_types = sum(rt in values for rt in run_types)
        if num_types == 0:
            raise ValueError(f"At least one of {run_types!r} is required")
        elif num_types > 1:
            raise ValueError(f"Only one of {run_types!r} can be specified in one Step")

        return values
