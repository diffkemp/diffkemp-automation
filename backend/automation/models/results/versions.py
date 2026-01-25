"""
Results of comparison of project that compare versions.

:author: Lukas Petr
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import yaml
from packaging.version import Version

from automation.models.projects import ProjectVersions

from .function import FunctionResult
from .result import ResultBase
from .types import ComparisonStatus, DiffKempResultType

logger = logging.getLogger(__name__)


class ResultVersion(ResultBase):
    """Results of comparison between two project versions."""

    def __init__(
        self,
        old_tag: str,
        new_tag: str,
        *,
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
        :param old_tag: Old tag of the project, that was compared.
        :param new_tag: New tag of the project, that was compared.
        """
        self.old_tag = old_tag
        self.new_tag = new_tag
        # Necessary to call after attributes are set - they are used by
        # abstract method.
        super().__init__(
            name=name,
            config_file_name=config_file_name,
            diffkemp_sha=diffkemp_sha,
            equal=equal,
            non_equal=non_equal,
            unknown=unknown,
            error=error,
            no_differing=no_differing,
            date=date,
            functions=functions,
            comparison_status=comparison_status,
            note=note,
        )

    @classmethod
    def from_analyzer_results(
        cls,
        name: str,
        config_file_name: str,
        tags: str,
        diffkemp_sha: str,
        result: Dict[str, str],
    ) -> "ResultVersion":
        """
        Load results from analyzer result.yml format.

        :param name: Name of the project.
        :param config_file_name: File name containing config of the project.
        :param tags: Tags that were compared (in format `tag1 -> tag2`).
        :param diffkemp_sha: SHA of DiffKemp that were used for the comparison.
        :param result: Result of the comparison.
        """
        old_tag, new_tag = tags.split(" -> ", 1)

        equal = 0
        non_equal = 0
        unknown = 0
        functions = {}

        for function_name, res_value in result.items():
            # Categorize result
            if res_value in ["no_diff", "syntactic"]:
                equal += 1
                res_type = (
                    DiffKempResultType.EQUAL_NO_DIFF
                    if res_value == "no_diff"
                    else DiffKempResultType.EQUAL
                )
            elif res_value == "semantic":
                non_equal += 1
                res_type = DiffKempResultType.NON_EQUAL
            else:
                unknown += 1
                res_type = DiffKempResultType.UNKNOWN
            functions[function_name] = FunctionResult(function_name, res_type)
        return cls(
            name=name,
            config_file_name=config_file_name,
            old_tag=old_tag,
            new_tag=new_tag,
            diffkemp_sha=diffkemp_sha,
            equal=equal,
            non_equal=non_equal,
            unknown=unknown,
            functions=functions,
        )

    def get_old_version(self) -> Version:
        return ProjectVersions.get_version_from_tag(self.old_tag)

    def get_new_version(self) -> Version:
        return ProjectVersions.get_version_from_tag(self.new_tag)

    def get_relative_viewer_path(self) -> Path:
        return Path(
            self.diffkemp_sha, self.config_file_name,
            f"{self.old_tag}-{self.new_tag}"
        )


class ResultsVersions():
    """Class for parsing results for versions."""

    @staticmethod
    def from_analyzer_results(
        name: str, config_file_name: str, diffkemp_sha: str, path: Path
    ) -> list[ResultVersion]:
        """Loads results from analyser results file and returns them."""
        with path.open("r", encoding="utf-8") as file:
            yaml_results = yaml.safe_load(file)

        results = []

        for tags, result in yaml_results.items():
            version_result = ResultVersion.from_analyzer_results(
                name=name,
                config_file_name=config_file_name,
                tags=tags,
                diffkemp_sha=diffkemp_sha,
                result=result,
            )
            results.append(version_result)
        return results
