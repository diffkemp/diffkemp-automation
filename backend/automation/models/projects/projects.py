"""
Module for accessing projects.

:author: Lukas Petr
"""

import logging
from pathlib import Path
from typing import Optional, Union

import yaml

from automation.utils import CONFIGS_DIR

from .commits import ProjectCommits
from .versions import ProjectVersions

Project = Union[ProjectVersions, ProjectCommits]

logger = logging.getLogger(__name__)


class ProjectsManager:
    """Class allowing to access projects."""

    @classmethod
    def get_all(cls) -> list[Project]:
        """Returns all projects."""
        if not CONFIGS_DIR.exists():
            return []

        projects = []

        for project_file in CONFIGS_DIR.glob("*.yml"):
            try:
                project = cls._load_project(project_file)
                projects.append(project)
            except (ValueError, RuntimeError) as e:
                logger.error(f"Failed to load '{project_file.stem}': {e}")

        return projects

    @classmethod
    def get_projects_tags_for_comparison(
        cls, projects: Optional[list[str]] = None, init_amount: int = 3
    ) -> list[tuple[ProjectVersions, list[str]]]:
        """
        Checks if projects have new releases.
        For those that do, returns list of (project, tags_to_compare) tuples.

        :param projects: List of projects (their config file names) that should
            be checked for new releases. If None, checks all projects.
        :param init_amout: Initial amount of tags to compare if the project
            has no compared tags.
        """
        if projects is None:
            loaded_projects = [project for project in cls.get_all()]
        else:
            loaded_projects = [cls.get(project) for project in projects]

        projects_tags = []
        for project in loaded_projects:
            if isinstance(project, ProjectVersions):
                try:
                    if project.has_new_release():
                        tags = project.get_tags_to_compare(
                            initial_comparison=init_amount
                        )
                        projects_tags.append((project, tags))
                except Exception as e:
                    logger.error(
                        f"Failed to check releases for {project.name}: {e}"
                    )

        return projects_tags

    @classmethod
    def get_projects_commits_for_comparison(
        cls,
        projects: Optional[list[str]] = None,
        init_amount: int = 3,
    ) -> list[tuple[ProjectCommits, list[str]]]:
        """
        Checks if projects has new commits to compare.
        For those who have, returns [project, commits].
        """
        if projects is None:
            loaded_projects = [project for project in cls.get_all()]
        else:
            loaded_projects = [cls.get(project) for project in projects]

        projects_commits = []
        for project in loaded_projects:
            if isinstance(project, ProjectCommits):
                commits = project.get_commits_to_compare(
                    initial_comparison=init_amount,
                )
                if len(commits) > 0:
                    projects_commits.append((project, commits))
        return projects_commits

    @classmethod
    def get(cls, config_name: str) -> Project:
        """
        Returns project specified by its config name.

        :param config_name: Name of the config file (without .yml extension).
        :raises FileNotFoundError: If config file does not exist.
        """
        path = CONFIGS_DIR / f"{config_name}.yml"

        if not path.exists():
            raise FileNotFoundError(f"Config not found: {config_name}.yml")
        return cls._load_project(path)

    @staticmethod
    def _load_project(path: Path) -> Project:
        """
        Loads project from file specified by path.

        :raises RuntimeError: If a config file is not in YAML format.
        :raises ValueError: If a config file is invalid.
        """
        try:
            with path.open("r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse '{path.name}' config") from e

        config_name = path.stem

        if "type" not in config:
            raise ValueError(
                f"Config '{config_name}' is missing required 'type' field")

        project_type = config["type"]

        if project_type == "versions":
            return ProjectVersions(config_name, config)
        elif config["type"] == "commits":
            return ProjectCommits(config_name, config)
        else:
            raise ValueError(
                f"Unknown project type: '{project_type}' in config "
                f"'{config_name}'"
            )
