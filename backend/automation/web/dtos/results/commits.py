"""
Data Transfer Objects for commit comparison results.

These DTOs transform domain models into web-friendly representations,
optimized for different views (list vs detail).

:author: Lukas Petr
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from flask import url_for

from automation.models.projects.commits import ProjectCommits
from automation.models.results.commits import ResultCommit
from automation.models.results.function import FunctionResult
from automation.models.results.types import DiffKempResultType


@dataclass
class CommitOverviewDTO:
    SHA: str
    summary: str

    @classmethod
    def create(cls, result: ResultCommit) -> "CommitOverviewDTO":
        return cls(
            SHA=result.commit,
            summary=result.get_commit_summary(),
        )


@dataclass
class CommitDTO:
    SHA: str
    summary: str
    message: str
    diff: str
    date: datetime

    @classmethod
    def create(cls, result: ResultCommit) -> "CommitDTO":
        return cls(
            SHA=result.commit,
            summary=result.get_commit_summary(),
            message=result.get_commit_message(),
            diff=result.get_diff(),
            date=result.get_commit_datetime(),
        )


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
    commit: CommitDTO
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
    commit_info_url: str

    @classmethod
    def create(
        cls,
        result: ResultCommit,
        project: ProjectCommits,
    ) -> "ResultDTO":
        """Create ResultDTO from result and project."""

        result_url = url_for(
            "commits_bp.commit_result",
            config_name=project.config_name,
            commit=result.commit,
            diffkemp_sha=result.diffkemp_sha
        )

        commit_info_url = url_for(
            "commits_bp.commit_info",
            config_name=project.config_name,
            commit=result.commit,
            diffkemp_sha=result.diffkemp_sha
        )

        differences_url = None
        viewer_url = None
        if result.non_equal > 0:
            differences_url = url_for(
                "commits_bp.commit_differences",
                config_name=project.config_name,
                commit=result.commit,
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
            commit=CommitDTO.create(result),
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
            commit_info_url=commit_info_url,
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
    commit: CommitOverviewDTO
    equal: int
    non_equal: int
    unknown: int
    error: int
    differing: int
    detail_url: str

    @classmethod
    def create(cls, result: ResultCommit) -> "ResultOverviewDTO":
        """Create overview DTO from result."""
        detail_url = url_for(
            "commits_bp.commit_result",
            config_name=result.config_file_name,
            commit=result.commit,
            diffkemp_sha=result.diffkemp_sha
        )

        return cls(
            date=result.date,
            config_name=result.config_file_name,
            name=result.name,
            commit=CommitOverviewDTO.create(result),
            equal=result.equal,
            non_equal=result.non_equal,
            unknown=result.unknown,
            error=result.error,
            differing=result.no_differing,
            detail_url=detail_url,
        )
