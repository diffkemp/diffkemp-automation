"""
Results of comparison of project that compare versions.

:author: Lukas Petr
"""

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from packaging.version import Version

from automation.models.projects import ProjectVersions

from .function import FunctionResult
from .result import ResultBase, ResultsBase
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

    @staticmethod
    def create_key(old_tag: str, new_tag: str) -> str:
        """Create a key for version comparison lookup."""
        return f"{old_tag} -> {new_tag}"

    def get_key(self) -> str:
        return self.create_key(self.old_tag, self.new_tag)

    def get_old_version(self) -> Version:
        return ProjectVersions.get_version_from_tag(self.old_tag)

    def get_new_version(self) -> Version:
        return ProjectVersions.get_version_from_tag(self.new_tag)

    def get_relative_viewer_path(self) -> Path:
        return Path(
            self.diffkemp_sha, self.config_file_name,
            f"{self.old_tag}-{self.new_tag}"
        )

    def to_yaml(self) -> dict:
        result_yaml = super().to_yaml()
        result_yaml.update({
            "old_tag": self.old_tag,
            "new_tag": self.new_tag,
            "type": "version"
        })
        return result_yaml

    @classmethod
    def from_yaml(cls, result: dict) -> "ResultVersion":
        kwargs = super()._parse_yaml_base(result)
        return cls(
            old_tag=result["old_tag"],
            new_tag=result["new_tag"],
            **kwargs,
        )


class ResultsVersions(ResultsBase[ResultVersion, ProjectVersions]):
    """
    Collection of version comparison results.

    Stores and manages multiple ResultVersion instances.
    """

    def __init__(
        self,
        results: Optional[Dict[str, Dict[str, List[ResultVersion]]]] = None,
    ) -> None:
        super().__init__(results)

    @classmethod
    def from_analyzer_results(
        cls, name: str, config_file_name: str, diffkemp_sha: str, path: Path
    ) -> "ResultsVersions":
        """Loads results from analyser results file."""
        with path.open("r", encoding="utf-8") as file:
            yaml_results = yaml.safe_load(file)

        all_results: dict = defaultdict(lambda: defaultdict(list))
        results = all_results[config_file_name]

        for tags, result in yaml_results.items():
            version_result = ResultVersion.from_analyzer_results(
                name=name,
                config_file_name=config_file_name,
                tags=tags,
                diffkemp_sha=diffkemp_sha,
                result=result,
            )
            results[tags].append(version_result)
        return cls(dict(all_results))
