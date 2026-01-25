"""
Module containing base class for representing results.

:author: Lukas Petr
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Generic, Optional, TypeVar, cast

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
        note: str = "",
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
        self.note = note

        self.functions = functions if functions is not None else {}
        self.comparison_status = comparison_status

        if no_differing:
            self.no_differing = no_differing
        else:
            out = self.get_diffkemp_out()
            self.no_differing = out.get_no_differing() if out else 0

        # Cache for lazy-loaded project
        self._project: Optional[TProject] = None

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
