"""
Representation of project for comparison of commits.

:author: Lukas Petr
"""
import logging
import re

from .project import BaseProject

COMMIT_FILTER = re.compile(r"\b(re)?factor\b", re.IGNORECASE)

logger = logging.getLogger(__package__)


class ProjectCommits(BaseProject):
    """Representation of project for comparison of commit."""
    def __init__(
            self,
            name: str,
            config: dict,
    ) -> None:
        logger.debug(f"ProjectCommits.__init__(name={name}, config={config})")
        super().__init__(name, config, depth=int(config["depth"]))
        self.commit_prefixes = config["commit-prefixes"]

    def pull_changes(self) -> None:
        self.repo.remote().pull(rebase=True)

    def get_commits_to_compare(self, initial_comparison: int = 3) -> list[str]:
        """Returns SHA of commits that should be analyzed ordered from oldest
        to newest."""
        self.pull_changes()
        latest_compared_commit = self.get_latest_compared_commit()
        commits_to_analyze = []
        for commit in self.repo.iter_commits("master"):
            # If some version was already analyzed stop on the previously
            # analyzed commit.
            if (latest_compared_commit is not None
                    and commit.hexsha == latest_compared_commit):
                break
            analyze = False
            for prefix in self.commit_prefixes:
                if not commit.summary.startswith(prefix):
                    continue
                if COMMIT_FILTER.search(str(commit.summary)) is None:
                    continue
                analyze = True
                break
            if analyze:
                commits_to_analyze.append(commit.hexsha)

        # If project was not compared, use initial_comparison commits.
        if latest_compared_commit is None:
            commits_to_analyze = commits_to_analyze[0:initial_comparison]
        # Reversing order, so the new latest is last
        commits_to_analyze.reverse()
        return commits_to_analyze

    def get_latest_compared_commit(self) -> str | None:
        return self._get_latest_compared()

    def set_latest_compared_commit(self, commit: str) -> None:
        self._set_latest_compared(commit)
