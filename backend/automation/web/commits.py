"""
HTTP endpoints providing results for comparison of project commits.

:author: Lukas Petr
"""
from typing import List

from flask import Blueprint, abort, render_template

from automation.db import ResultsRepo
from automation.web.dtos.results.commits import ResultDTO, ResultOverviewDTO

commits_bp = Blueprint("commits_bp", __name__, url_prefix="/commits")


@commits_bp.route("/<config_name>/<commit>/<diffkemp_sha>")
def commit_result(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
) -> str:
    """Route showing iframe with result viewer."""
    repo = ResultsRepo()
    results = repo.get_commits(
        config_file_name=config_name,
        commit=commit,
        diffkemp_sha=diffkemp_sha,
    )

    if len(results) != 1:
        abort(404, "Result not found")

    result = results[0]
    project = result.get_project()

    dto = ResultDTO.create(result, project)

    return render_template("commits/result.html", result=dto)


@commits_bp.route("/<config_name>/<commit>/<diffkemp_sha>/differences")
def commit_differences(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
) -> str:
    """Route showing iframe with differences for given result."""
    repo = ResultsRepo()
    results = repo.get_commits(
        config_file_name=config_name,
        commit=commit,
        diffkemp_sha=diffkemp_sha,
    )

    if len(results) != 1:
        abort(404, "Result not found")

    result = results[0]
    project = result.get_project()

    dto = ResultDTO.create(result, project)

    return render_template("commits/differences.html", result=dto)


@commits_bp.route("/<config_name>/<commit>/<diffkemp_sha>/info")
def commit_info(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
) -> str:
    """Route showing iframe with differences for given result."""
    repo = ResultsRepo()
    results = repo.get_commits(
        config_file_name=config_name,
        commit=commit,
        diffkemp_sha=diffkemp_sha,
    )

    if len(results) != 1:
        abort(404, "Result not found")

    result = results[0]
    project = result.get_project()

    dto = ResultDTO.create(result, project)

    return render_template("commits/info.html", result=dto)


@commits_bp.route("/")
def commits_list() -> str:
    """Route showing list of results for projects' commits."""
    repo = ResultsRepo()
    results = repo.get_commits()

    dto: List[ResultOverviewDTO] = []
    # TODO Add paging
    for result in results:
        dto.append(ResultOverviewDTO.create(result))
    return render_template("commits/list.html", results=dto)
