from collections import defaultdict
from pathlib import Path

import pygit2 as pg2


class Repo:
    """Wrapper above pygit2 for specific git operation common at release.
    Like git shortlog, getting references, tagging, etc.
    """

    def __init__(self, path: Path):
        self._repo = pg2.Repository(path.resolve())

    def get_tag_ref(self, long_tag_name: str) -> pg2.Reference:
        tag_name = long_tag_name.split("-", 1)[0]
        return self._repo.references[f"refs/tags/{tag_name}"]

    def get_latest_tag(self) -> pg2.Reference:
        tag_name = self._repo.describe(
            describe_strategy=pg2.GIT_DESCRIBE_TAGS, always_use_long_format=True
        )
        return self.get_tag_ref(tag_name)

    def get_latest_annotated_tag(self) -> pg2.Reference:
        tag_name = self._repo.describe(always_use_long_format=True)
        return self.get_tag_ref(tag_name)

    @staticmethod
    def is_merge_commit(commit: pg2.Commit):
        # A merge commit is a commit with multiple parents
        return len(commit.parents) > 1

    def get_shortlog(self, since: pg2.Reference, include_merge_commits: bool) -> str:
        shortlog = defaultdict(list)

        commits = self._repo.walk(self._repo.head.target)
        for commit in commits:
            if commit.hex == str(since.target):
                break
            if not include_merge_commits and self.is_merge_commit(commit):
                continue
            first_line = commit.message.splitlines()[0]
            shortlog[commit.committer.name].append(first_line)

        lines = []
        for name, commits in shortlog.items():
            lines.append(f"{name} ({len(commits)}):")
            for commit in commits:
                lines.append(f"      {commit}")
            lines.append("")

        return "\n".join(lines)
