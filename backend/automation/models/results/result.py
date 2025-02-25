"""
Module containing base class for representing results.

:author: Lukas Petr
"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

from automation.models.projects.project import TProject
from automation.models.projects.projects import ProjectsManager
from automation.utils import VIEW_RESULTS_DIR

from .diffkemp_out import DiffKempOutYaml
from .function import FunctionResult
from .types import ComparisonStatus, OverallResult

logger = logging.getLogger(__name__)

TResult = TypeVar("TResult", bound="ResultBase")


class ResultBase(Generic[TProject], ABC):
    """
    Base class for representing comparison results.
    """

    def __init__(
        self,
        name: str,
        config_file_name: str,
        diffkemp_sha: str,
        equal: int = 0,
        non_equal: int = 0,
        unknown: int = 0,
        error: int = 0,
        no_differing: Optional[int] = None,
        date: Optional[datetime] = None,
        functions: Optional[Dict[str, FunctionResult]] = None,
        comparison_status: ComparisonStatus = ComparisonStatus.SUCCESS,
    ) -> None:
        """
        :param name: Name of project (used primary for showing to user).
        :param config_file_name: Name of config file (used almost everywhere).
        :param diffkemp_sha: Which version (commit SHA) was used for the
            comparison.
        :param equal: Number of compared functions evaluated as equal.
        :param non_equal: Number of compared functions evaluated as non-equal.
        :param unknown: Number of functions not evaluated
            (evaluated as unknown).
        :param error: Number of compared functions in which error occurred
            during comparison.
        :param no_differing: Number of functions evaluated as differing.
        :param date: Date and time when to comparison was finished.
        :param functions: Dictionary mapping compared function names to their
            result.
        """
        self.name = name
        self.config_file_name = config_file_name
        self.diffkemp_sha = diffkemp_sha
        self.equal = equal
        self.error = error
        self.non_equal = non_equal
        self.unknown = unknown
        self.date = date if date else datetime.now()

        self.functions = functions if functions is not None else {}
        self.comparison_status = comparison_status

        if no_differing:
            self.no_differing = no_differing
        else:
            out = self.get_diffkemp_out()
            self.no_differing = out.get_no_differing() if out else 0

        # Cache for lazy-loaded project
        self._project: Optional[TProject] = None

    @abstractmethod
    def get_key(self) -> str:
        """Return key for this result (used for quick searching results)."""
        pass

    def get_diffkemp_verdict(self) -> OverallResult:
        """Return overall verdict based on function results."""
        if self.non_equal != 0:
            return OverallResult.NON_EQUAL
        elif self.unknown != 0:
            return OverallResult.UNKNOWN
        else:
            return OverallResult.EQUAL

    def get_project(self) -> TProject:
        """Returns project information."""
        if not hasattr(self, "_project") or self._project is None:
            self._project = cast(
                TProject,
                ProjectsManager.get(self.config_file_name)
            )
        return self._project

    @abstractmethod
    def get_relative_viewer_path(self) -> Path:
        pass

    def get_viewer_path(self) -> Path:
        """Get absolute path to viewer directory for this result."""
        return VIEW_RESULTS_DIR / self.get_relative_viewer_path()

    def get_diffkemp_out_path(self) -> Path:
        """Get path to DiffKemp output YAML file."""
        return self.get_viewer_path() / "data" / "diffkemp-out.yaml"

    def get_diffkemp_out(self) -> Optional[DiffKempOutYaml]:
        """
        Load DiffKemp output if it exists.

        Returns None if file doesn't exist (indicates all functions were
        equal).
        """
        path = self.get_diffkemp_out_path()
        if not path.exists():
            return None
        return DiffKempOutYaml.from_file(path)

    def to_yaml(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "config_file_name": self.config_file_name,
            "diffkemp_sha": self.diffkemp_sha,
            "equal": self.equal,
            "non_equal": self.non_equal,
            "unknown": self.unknown,
            "error": self.error,
            "date": self.date.isoformat(),
            "no_differing": self.no_differing,
            "functions": [
                function.to_yaml() for function in self.functions.values()],
            "comparison_status": str(self.comparison_status),
        }

    @staticmethod
    def _parse_yaml_base(result: Dict[str, Any]) -> dict:
        """
        Parse common fields from YAML representation.

        This helper method extracts base class fields. Subclasses should
        call this and add their specific fields.

        :param result: YAML result.
        """
        functions = {}
        for fun_res in result["functions"]:
            f = FunctionResult.from_yaml(fun_res)
            functions[f.name] = f
        return {
            "name": result["name"],
            "config_file_name": result["config_file_name"],
            "diffkemp_sha": result["diffkemp_sha"],
            "equal": int(result["equal"]),
            "non_equal": int(result["non_equal"]),
            "unknown": int(result["unknown"]),
            "error": int(result["error"]),
            "no_differing": int(result["no_differing"]),
            "date": datetime.fromisoformat(result["date"]),
            "functions": functions,
            "comparison_status": ComparisonStatus(result["comparison_status"]),
        }


class ResultsBase(Generic[TResult, TProject], ABC):
    """
    Base class for storing and searching of multiple results.

    :ivar results: Map results[config_name][key] -> results.
    """

    results: Dict[str, Dict[str, List[TResult]]]

    def __init__(
        self,
        results: Optional[Dict[str, Dict[str, List[TResult]]]] = None
    ) -> None:
        self.results = (
            results if results else defaultdict(lambda: defaultdict(list)))

    def add(self, result: TResult) -> None:
        """Adds result."""
        self.results[result.config_file_name][result.get_key()].append(result)

    def extend(self, other: "ResultsBase") -> None:
        """Extend results with other results."""
        for config_name, key_results in other.results.items():
            for key, results in key_results.items():
                self.results[config_name][key].extend(results)

    def get(
        self,
        config_name: Optional[str] = None,
        key: Optional[str] = None,
        diffkemp_sha: Optional[str] = None,
    ) -> list[TResult]:
        """Returns list of results specified by the parameters."""
        if (
          config_name is not None and
          key is not None and
          diffkemp_sha is not None):
            return list(
                filter(
                    lambda res: res.diffkemp_sha == diffkemp_sha,
                    self.results[config_name][key],
                )
            )
        elif config_name is not None and key is not None:
            return self.results[config_name][key]
        elif config_name is not None:
            return list(chain(*self.results[config_name].values()))
        return list(
            chain(
                *map(
                    lambda project_results: list(
                        chain(*project_results.values())
                    ),
                    self.results.values(),
                )
            )
        )

    @classmethod
    @abstractmethod
    def from_analyzer_results(
        cls, name: str, config_file_name: str, diffkemp_sha: str, path: Path
    ) -> "ResultsBase":
        """Loads results from analyzer results file."""
        pass

    def to_yaml(self) -> List[Dict[str, Any]]:
        """Serialize the results to YAML format."""
        return list(map(lambda result: result.to_yaml(), self.get()))
