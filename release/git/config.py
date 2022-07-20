import enum

from pydantic import BaseModel


class SinceWhat(enum.Enum):
    LATEST_TAG = "LATEST_TAG"
    LATEST_ANNOTATED_TAG = "LATEST_ANNOTATED_TAG"
    LATEST_MERGE = "LATEST_MERGE"


class GetShortlogConfig(BaseModel):
    include_merge_commits: bool
    since: SinceWhat


class GitConfig(BaseModel):
    repo: str
    get_shortlog: GetShortlogConfig
