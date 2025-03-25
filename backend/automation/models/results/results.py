"""
Module representing results of projects' comparison.

:author: Lukas Petr
"""

import logging
from typing import Any, Dict, List, Union

import yaml

from automation.utils import RESULTS_PATH

from .commits import ResultCommit, ResultsCommits
from .versions import ResultsVersions, ResultVersion

logger = logging.getLogger(__name__)

ResultsSubTypes = Union[ResultsVersions, ResultsCommits]


class Results:
    """
    Class representing results of projects' comparison.

    :ivar versions: Results of comparison of projects's versions.
    """

    def __init__(self) -> None:
        self.versions = ResultsVersions()
        self.commits = ResultsCommits()

        if not RESULTS_PATH.exists():
            return

        self._load_from_file()

    def _load_from_file(self) -> None:
        """Loads results from the results file."""
        with RESULTS_PATH.open("r", encoding="utf-8") as file:
            results = yaml.safe_load(file)

        # Empty file
        if not results:
            return

        # Load results
        for result in results:
            if result["type"] == "version":
                self.versions.add(ResultVersion.from_yaml(result))
            elif result["type"] == "commit":
                self.commits.add(ResultCommit.from_yaml(result))

    def extend(self, results: ResultsSubTypes) -> None:
        """Add multiple results to this instance."""
        if isinstance(results, ResultsVersions):
            self.versions.extend(results)
        elif isinstance(results, ResultsCommits):
            self.commits.extend(results)
        else:
            raise TypeError(f"Unknown results class: {type(results)}")

    def get_version_results(self) -> ResultsVersions:
        """Returns results of projects that compared versions."""
        return self.versions

    def get_commit_results(self) -> ResultsCommits:
        """Returns results of projects that compared commits."""
        return self.commits

    def to_yaml(self) -> List[Dict[str, Any]]:
        """Serialize the results to YAML format."""
        results = []
        results.extend(self.versions.to_yaml())
        results.extend(self.commits.to_yaml())
        return results

    def save(self) -> None:
        """Saves the results to disk."""
        RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

        data = self.to_yaml()

        with RESULTS_PATH.open("w", encoding="utf-8") as file:
            yaml.safe_dump(data, file)
