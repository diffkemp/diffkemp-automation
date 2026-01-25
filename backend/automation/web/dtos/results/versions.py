"""
Data Transfer Objects for version comparison results.

These DTOs transform domain models into web-friendly representations,
optimized for different views (list vs detail).

:author: Lukas Petr
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from flask import url_for

from automation.models.projects.versions import ProjectVersions
from automation.models.results.function import FunctionResult
from automation.models.results.types import DiffKempResultType
from automation.models.results.versions import ResultVersion


@dataclass
class ResultDTO:
    """
    Full DTO for result detail pages.

    Contains complete information including all function results,
    viewer paths, and detailed URLs. Used when full detail is needed.
    """
    config_name: str
    name: str
    diffkemp_sha: str
    old_version: str
    new_version: str
    old_tag: str
    new_tag: str
    equal: int
    non_equal: int
    unknown: int
    error: int
    differing: int
    date: datetime
    verdict: str
    functions: Dict[str, FunctionResult]
    result_url: str
    differences_url: Optional[str]
    viewer_url: Optional[str]
    note: str

    @classmethod
    def create(
        cls,
        result: ResultVersion,
        project: ProjectVersions
    ) -> "ResultDTO":
        """
        Create ResultDTO from result and project.

        :param result: Result version object
        :param project: Project versions object
        """

        result_url = url_for(
            "versions_bp.version_result",
            config_name=project.config_name,
            old_tag=result.old_tag,
            new_tag=result.new_tag,
            diffkemp_sha=result.diffkemp_sha
        )

        differences_url = None
        viewer_url = None
        if result.non_equal > 0:
            differences_url = url_for(
                "versions_bp.version_differences",
                config_name=project.config_name,
                old_tag=result.old_tag,
                new_tag=result.new_tag,
                diffkemp_sha=result.diffkemp_sha
            )

            viewer_url = url_for(
                "view_results_bp.result_viewer",
                path=str(result.get_relative_viewer_path()) + "/",
            )

        return cls(
            config_name=project.config_name,
            name=project.name,
            diffkemp_sha=result.diffkemp_sha,
            old_version=str(result.get_old_version()),
            new_version=str(result.get_new_version()),
            old_tag=result.old_tag,
            new_tag=result.new_tag,
            equal=result.equal,
            non_equal=result.non_equal,
            unknown=result.unknown,
            error=result.error,
            differing=result.no_differing,
            date=result.date,
            verdict=result.get_diffkemp_verdict(),
            functions=result.functions,
            result_url=result_url,
            differences_url=differences_url,
            viewer_url=viewer_url,
            note=result.note,
        )

    def get_function_bg_class(self, function_name: str) -> str:
        """
        Get Bootstrap background class for a function result.

        :param function_name: Name of the function
        :return: Bootstrap bg-* class name (e.g., "bg-success")
        """
        if function_name not in self.functions:
            return ""

        result_type = self.functions[function_name].diffkemp_result

        mapping = {
            DiffKempResultType.EQUAL: "bg-success",
            DiffKempResultType.EQUAL_NO_DIFF: "bg-success",
            DiffKempResultType.NON_EQUAL: "bg-danger",
            DiffKempResultType.UNKNOWN: "bg-secondary",
            DiffKempResultType.ERROR: "bg-warning",
        }
        return mapping.get(result_type, "")


@dataclass
class ResultOverviewDTO:
    """
    Lightweight DTO for result list/overview pages.

    Contains only essential information for displaying results in tables.
    """
    date: datetime
    config_name: str
    name: str
    old_version: str
    new_version: str
    equal: int
    non_equal: int
    unknown: int
    error: int
    differing: int
    detail_url: str

    @classmethod
    def create(cls, result: ResultVersion) -> "ResultOverviewDTO":
        """
        Create overview DTO from result.

        :param result: Result version object
        :return: Lightweight DTO for list views
        """
        detail_url = url_for(
            "versions_bp.version_result",
            config_name=result.config_file_name,
            old_tag=result.old_tag,
            new_tag=result.new_tag,
            diffkemp_sha=result.diffkemp_sha
        )

        return cls(
            date=result.date,
            config_name=result.config_file_name,
            name=result.name,
            old_version=str(result.get_old_version()),
            new_version=str(result.get_new_version()),
            equal=result.equal,
            non_equal=result.non_equal,
            unknown=result.unknown,
            error=result.error,
            differing=result.no_differing,
            detail_url=detail_url,
        )
