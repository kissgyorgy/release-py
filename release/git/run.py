from pathlib import Path

from ..parser import render_text
from ..types import Variables
from .client import Repo
from .config import GitConfig, SinceWhat


def run_step(git_config: GitConfig, variables: Variables) -> str:
    repo_path = render_text(git_config.repo, variables)
    repo_path = Path(repo_path)
    repo = Repo(repo_path)
    if git_config.get_shortlog:
        conf = git_config.get_shortlog
        if conf.since is SinceWhat.LATEST_TAG:
            since = repo.get_latest_tag()
        elif conf.since is SinceWhat.LATEST_ANNOTATED_TAG:
            since = repo.get_latest_annotated_tag()
        print("Getting shortlog")
        return repo.get_shortlog(since, conf.include_merge_commits)
    raise ValueError("Invalid git config")
