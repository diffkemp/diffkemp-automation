"""
HTTP endpoints providing results for comparison of project versions.

:author: Lukas Petr
"""
from typing import List

from flask import Blueprint, abort, render_template

from automation.models.results.results import Results
from automation.models.results.versions import ResultVersion
from automation.web.dtos.results.versions import ResultDTO, ResultOverviewDTO

versions_bp = Blueprint("versions_bp", __name__, url_prefix="/versions")


@versions_bp.route("/<config_name>/<old_tag>/<new_tag>/<diffkemp_sha>")
def version_result(
    config_name: str,
    old_tag: str,
    new_tag: str,
    diffkemp_sha: str,
) -> str:
    """Route showing iframe with result viewer."""
    results = Results().get_version_results().get(
        config_name,
        ResultVersion.create_key(old_tag, new_tag),
        diffkemp_sha,
    )

    if len(results) != 1:
        abort(404, "Result not found")

    result = results[0]
    project = result.get_project()

    dto = ResultDTO.create(result, project)

    return render_template("versions/result.html", result=dto)


@versions_bp.route(
    "/<config_name>/<old_tag>/<new_tag>/<diffkemp_sha>/differences")
def version_differences(
    config_name: str,
    old_tag: str,
    new_tag: str,
    diffkemp_sha: str,
) -> str:
    """Route showing iframe with differences for given result."""
    results = Results().get_version_results().get(
        config_name,
        ResultVersion.create_key(old_tag, new_tag),
        diffkemp_sha,
    )

    if len(results) != 1:
        abort(404, "Result not found")

    result = results[0]
    project = result.get_project()

    dto = ResultDTO.create(result, project)

    return render_template("versions/differences.html", result=dto)


@versions_bp.route("/")
def versions_list() -> str:
    """Route showing list of results for projects' versions."""
    results = Results().get_version_results().get()
    results.sort(key=lambda result: result.date, reverse=True)

    dto: List[ResultOverviewDTO] = []
    # TODO Add paging
    for result in results:
        dto.append(ResultOverviewDTO.create(result))
    return render_template("versions/list.html", results=dto)
