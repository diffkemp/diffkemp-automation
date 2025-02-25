"""
Supported projects representation.

:author: Lukas Petr
"""

import logging
from abc import ABC
from typing import Any, Dict, TypeVar

import yaml
from git import Repo

from automation.utils import LATEST_VERSION_PATH, REPOS_DIR

logger = logging.getLogger(__package__)
TProject = TypeVar("TProject", bound="BaseProject")


class UnsupportedRepo(Exception):
    pass


class BaseProject(ABC):
    """Base class for project representation."""

    def __init__(
        self,
        config_name: str,
        config: Dict[str, Any],
        depth: int = 1,
    ) -> None:
        """
        :param config_name: Name of configuration file.
        :param config: Loaded config.
        :param depth: Depth to which clone the repo.
        """
        self.config_name = config_name
        try:
            self.project_type: str = config["type"]
            self.name: str = config["name"]
            self.git_url: str = config["git"]
        except KeyError as e:
            raise ValueError(
                f"Error: Config is missing required key {e.args[0]}!")
        self.config: Dict = config
        self._clone_repo(depth=depth)

    def _clone_repo(self, depth: int = 1) -> None:
        """
        Clones the repository if it is not already cloned, sets `self.repo`
        variable.

        :param depth: Depth to which clone the repository.
        """
        logger.debug(
            f"BaseProject._clone_repo(depth={depth}, "
            f"config_name={self.config_name})"
        )
        repo_path = REPOS_DIR / self.config_name
        if not repo_path.exists():
            repo_path.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.clone_from(self.git_url, repo_path, depth=depth)
        else:
            self.repo = Repo(repo_path)

    def _get_latest_compared(self) -> str | None:
        """
        Returns latest compared version of the project or None if the project
        has not been compared yet."""
        if not LATEST_VERSION_PATH.exists():
            return None
        with LATEST_VERSION_PATH.open("r", encoding="utf-8") as file:
            content = yaml.safe_load(file)
            if self.config_name not in content:
                return None
            return content[self.config_name]

    def _set_latest_compared(self, value: str) -> None:
        """Sets for the project latest compared version specified by value."""
        content = {}
        if LATEST_VERSION_PATH.exists():
            with LATEST_VERSION_PATH.open("r", encoding="utf-8") as file:
                content = yaml.safe_load(file)
        else:
            LATEST_VERSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        content[self.config_name] = value
        with LATEST_VERSION_PATH.open("w", encoding="utf-8") as file:
            yaml.safe_dump(content, file)
