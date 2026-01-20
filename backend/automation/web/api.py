"""File defining HTML REST API endpoints."""
from flask import Blueprint, Response, abort, request, session

from automation.db import FunctionResultsRepo
from automation.models.results.types import ExpectedResultType

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


@api_bp.put(
    "/commits/<config_name>/<commit>/<diffkemp_sha>"
    "/functions/<function_name>/expected-result"
)
def update_fun_expected_res_for_commit(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
    function_name: str,
) -> Response:
    """Update the expected result for a function."""
    # Check if user is logged in
    if "user" not in session:
        abort(403)

    repo = FunctionResultsRepo()
    function_result = repo.getForCommit(
        config_name=config_name,
        commit=commit,
        diffkemp_sha=diffkemp_sha,
        function_name=function_name,
    )

    if not function_result:
        abort(404)

    expected_result = ExpectedResultType(request.json["expected_result"])
    function_result.expected_result = expected_result
    function_result.expected_result_changed_by = session["user"]

    repo.update(function_result)
    return Response(status=200)


@api_bp.put(
    "/versions/<config_name>/<old_tag>/<new_tag>/<diffkemp_sha>"
    "/functions/<function_name>/expected-result"
)
def update_fun_expected_res_for_version(
    config_name: str,
    old_tag: str,
    new_tag: str,
    diffkemp_sha: str,
    function_name: str,
) -> Response:
    """Update the expected result for a function."""
    # Check if user is logged in
    if "user" not in session:
        abort(403)

    repo = FunctionResultsRepo()
    function_result = repo.getForVersion(
        config_name=config_name,
        old_tag=old_tag,
        new_tag=new_tag,
        diffkemp_sha=diffkemp_sha,
        function_name=function_name,
    )

    if not function_result:
        abort(404)

    expected_result = ExpectedResultType(request.json["expected_result"])
    function_result.expected_result = expected_result
    function_result.expected_result_changed_by = session["user"]

    repo.update(function_result)
    return Response(status=200)
