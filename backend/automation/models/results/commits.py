"""
Results of comparison of project that compare commits.

:author: Lukas Petr
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from git import Commit

from automation.models.projects.commits import ProjectCommits

from .function import FunctionResult
from .result import ResultBase
from .types import ComparisonStatus, DiffKempResultType


class ResultCommit(ResultBase[ProjectCommits]):
    """Results of comparison for project's commit."""
    def __init__(
        self,
        commit: str,
        all_diffs_matched: bool = False,
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
    ):
        """
        :param commit: For which commit are the results.
        :param all_diffs_matched: True if all diffs added in the commit were
            matched to functions (was located in which function the diff
            belongs to).
        """
        self.commit = commit
        self.all_diffs_matched = all_diffs_matched
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
        commit: str,
        diffkemp_sha: str,
        result: Dict[str, Any],
    ) -> "ResultCommit":
        # Failed comparison map
        failed_verdict_map = {
            "FAIL": ComparisonStatus.FAIL,
            "NO-FUNCTIONS": ComparisonStatus.NO_FUNCTIONS,
        }
        verdict = result["verdict"]
        if verdict in failed_verdict_map.keys():
            return cls(name=name,
                       config_file_name=config_file_name,
                       commit=commit,
                       diffkemp_sha=diffkemp_sha,
                       comparison_status=failed_verdict_map[verdict])

        functions = {}
        result_map = {
            "eq": DiffKempResultType.EQUAL,
            "neq": DiffKempResultType.NON_EQUAL,
            "unk": DiffKempResultType.UNKNOWN,
            "err": DiffKempResultType.ERROR,
        }
        for function, fun_result in result["functions"].items():
            functions[function] = FunctionResult(
                name=function, diffkemp_result=result_map[fun_result])
        return cls(
            name=name,
            config_file_name=config_file_name,
            commit=commit,
            diffkemp_sha=diffkemp_sha,
            equal=result["eq"],
            non_equal=result["neq"],
            unknown=result["unk"],
            error=result["err"],
            functions=functions,
            all_diffs_matched=result["confident"],
        )

    def get_relative_viewer_path(self) -> Path:
        return Path(
            self.diffkemp_sha, self.config_file_name, self.commit)

    def get_commit(self) -> Commit:
        return self.get_project().repo.commit(self.commit)

    def get_commit_summary(self) -> str:
        return str(self.get_commit().summary)

    def get_commit_message(self) -> str:
        """
        Returns commit message describing of the commit that was compared."""
        return str(self.get_commit().message)

    def get_commit_datetime(self) -> datetime:
        return self.get_commit().committed_datetime

    def get_diff(self) -> str:
        return self.get_project().repo.git.diff(f"{self.commit}^!")

    @classmethod
    def from_yaml(cls, result: dict) -> "ResultCommit":
        kwargs = super()._parse_yaml_base(result)
        return cls(
            commit=result["commit"],
            all_diffs_matched=result["all_diffs_matched"],
            **kwargs
        )


class ResultsCommits():
    """Class for parsing results for commits."""

    @staticmethod
    def from_analyzer_results(
        name: str,
        config_file_name: str,
        diffkemp_sha: str,
        path: Path,
    ) -> list[ResultCommit]:
        """Loads results from analyser results file and returns them."""
        with path.open("r") as file:
            yaml_results = yaml.safe_load(file)

        results = []

        for commit, result in yaml_results.items():
            commit_result = ResultCommit.from_analyzer_results(
                name=name,
                config_file_name=config_file_name,
                commit=commit,
                diffkemp_sha=diffkemp_sha,
                result=result
            )
            results.append(commit_result)
        return results
