"""
Representation of project used for comparison of versions.

:author: Lukas Petr
"""

import bisect
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
from packaging.version import Version

from .project import BaseProject, UnsupportedRepo

# Regex for extracting version from tag
VERSION_REGEX = re.compile(r"(\d+(?:\.\d+)*)")
# API request timeout in seconds
REQUEST_TIMEOUT = 10

logger = logging.getLogger(__name__)


class VersionError(RuntimeError):
    """Raised when version cannot be extracted."""

    pass


class APIError(RuntimeError):
    """Raised when API requests fail."""

    pass


class ProjectVersions(BaseProject):
    """Representation of project for comparison of versions."""

    def __init__(self, config_name: str, config: Dict[str, Any]):
        """
        :param config_name: Name of the config file (without .yml extension).
        :param config: Loaded config of the file.
        :raises ValueError: If the config has missing required fields.
        """
        super().__init__(config_name, config)

        self.release_monitor_id: Optional[int] = config.get(
            "release-monitor-id")

        if "functions" not in config:
            raise ValueError(
                f"Config '{config_name}' has missing field 'functions'!")
        self.functions: List[str] = config["functions"]

        self.tag_filter: Optional[str] = config.get("tag-filter")

    def fetch_tags(self) -> None:
        """Fetches tags from the upstream repository."""
        self.repo.remote().fetch(depth=1, tags=True)

    @staticmethod
    def get_version_from_tag(tag: str) -> Version:
        """Extracts version from given tag.

        :param tag: Git tag string.
        :raises VersionError: If version cannot be extracted from the tag.
        """
        version_match = VERSION_REGEX.search(tag)
        if version_match is None:
            raise VersionError(f"Cannot extract version from '{tag}'")
        return Version(version_match[0])

    def has_new_release(self) -> bool:
        """Checks if there are new releases/versions of the project."""
        latest_release_version = self.get_latest_compared_version()
        if latest_release_version is None:
            return True

        return self.get_latest_release() > latest_release_version

    def get_tags_to_compare(self, initial_comparison: int = 3) -> List[str]:
        """
        Returns sorted list of project tags that should be compared.

        If no version was compared, returns the most recent
        `initial_comparison` tags.

        :param initial_comparison: Number of release tags to return if no
            version was yet compared.
        """
        if initial_comparison < 2:
            raise ValueError("Error: Initial comparison must be 2+")

        latest_compared = self.get_latest_compared_version()
        tags = self.get_sorted_release_tags()

        # If project was not compared, return initial_comparison latest tags.
        if latest_compared is None:
            return tags[-initial_comparison:]

        # Find index of the latest compared tag
        latest_index = bisect.bisect_left(
            tags, latest_compared, key=lambda t: self.get_version_from_tag(t)
        )
        return tags[latest_index:]

    def get_config_for_analysis(self, tags: List[str]) -> Dict[str, Any]:
        """
        Returns config acceptable by version comparison tool.

        :param tags: Tags which should be compared.
        """
        config = self.config.copy()
        # The commit-analysis tool expects the `name` field to be the repo name
        config["name"] = self.config_name
        config["tags"] = tags
        return config

    def get_latest_release(self) -> Version:
        """
        Returns latest release version of the project.

        :raises APIError: If release information cannot be fetched.
        :raises UnsupportedRepo: If repository type is not supported.
        """
        if "github.com" in self.git_url:
            return self._get_github_latest()
        elif self.release_monitor_id is not None:
            return self._get_release_monitor_latest()
        else:
            raise UnsupportedRepo(
                "Error: Unable to extract latest release for given project"
            )

    def _get_github_latest(self) -> Version:
        """Fetch latest release from GitHub API."""
        url = "https://api.github.com/repos/{}/releases/latest".format(
            self.get_org_and_repo()
        )

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if "tag_name" not in data:
                raise APIError(
                    f"GitHub API response missing 'tag_name' for {self.name}"
                )
            return self.get_version_from_tag(data["tag_name"])

        except requests.Timeout:
            raise APIError(f"GitHub API timeout for {self.name}")

    def _get_release_monitor_latest(self) -> Version:
        """Fetch latest release from release-monitor.org"""
        url = (
            "https://release-monitoring.org/api/v2/versions/?"
            f"project_id={self.release_monitor_id}"
        )

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if "latest_version" not in data:
                raise APIError(
                    "Release monitor API missing 'latest_version' for "
                    f"{self.name}"
                )
            return Version(data["latest_version"])
        except requests.Timeout:
            raise APIError(f"Release monitor API timeout for {self.name}")

    def get_latest_compared_version(self) -> Optional[Version]:
        """
        Returns version of the project that was compared as last.

        :return: Version or None if not yet compared or invalid tag."""
        latest = self._get_latest_compared()
        if latest is None:
            return None

        try:
            return Version(latest)
        except Exception:
            logger.warning(
                f"Invalid version string '{latest}' for '{self.name}'")
            return None

    def set_latest_compared_tag(self, tag: str) -> None:
        """
        Extracts from the tag version and saves it as latest compared.

        :param tag: Git tag string.
        :raises VersionError: If version cannot be extracted from tag.
        """
        version = self.get_version_from_tag(tag)
        self._set_latest_compared(str(version))

    def get_release_tags(self) -> list[str]:
        """
        Returns list of all project tags representing release.

        :raises APIError: If tags cannot be fetched from API.
        """
        if "github.com" in self.git_url:
            tags = self._get_github_release_tags()
        elif "git.lysator.liu.se" in self.git_url:
            tags = self._get_lysator_tags()
        else:
            raise UnsupportedRepo(f"Unsupported repository: {self.git_url}")

        # Apply tag filter if configured
        if self.tag_filter is not None:
            regex = re.compile(self.tag_filter)
            tags = [tag for tag in tags if regex.fullmatch(tag)]

        return tags

    def _get_github_release_tags(self) -> List[str]:
        """Fetch release tags from GitHub API."""
        org_repo = self.get_org_and_repo()
        url = f"https://api.github.com/repos/{org_repo}/releases"

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            releases = response.json()

            if not isinstance(releases, list):
                raise APIError(f"GitHub API returned non-list for {self.name}")
            return [
                release["tag_name"] for release in releases
                if "tag_name" in release
            ]

        except requests.Timeout:
            raise APIError(f"GitHub API timeout fetching tags for {self.name}")

    def _get_lysator_tags(self) -> List[str]:
        """Fetch tags from Lysator GitHub instance."""
        org_repo = quote_plus(self.get_org_and_repo())
        url = (
            f"https://git.lysator.liu.se/api/v4/projects/{org_repo}/"
            "repository/tags"
        )
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise APIError(
                    f"Lysator API returned non-list for {self.name}")
            return [tag["name"] for tag in data if "name" in tag]

        except requests.Timeout:
            raise APIError(
                f"Lysator API timeout fetching tags for {self.name}")

    def get_sorted_release_tags(self) -> List[str]:
        """
        Return list of all releases sorted by version.

        Tags with invalid versions are logged and skipped.
        """
        tags = self.get_release_tags()
        tags_versions = []

        for tag in tags:
            try:
                version = self.get_version_from_tag(tag)
                tags_versions.append((tag, version))
            except VersionError:
                logger.warning(
                    f"Skipped tag '{tag}' for {self.name}: invalid version")

        tags_versions.sort(key=lambda tv: tv[1])
        return [tag for tag, _ in tags_versions]

    def get_org_and_repo(self) -> str:
        """Returns 'organization>/<repository' of the project."""
        url = self.git_url

        if "github.com" not in url and "git.lysator.liu.se" not in url:
            raise UnsupportedRepo(f"Unsupported repository: {url}")

        # Match org/repo pattern before optional .git suffix
        match = re.search(r"([^/]+/[^/]+?)(?:.git)?$", url)
        if match is None or len(match.groups()) != 1:
            raise UnsupportedRepo(f"Cannot extract org/repo from url: {url}")

        return match.group(1)
