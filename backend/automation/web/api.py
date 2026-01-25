"""File defining HTML REST API endpoints."""
from functools import wraps
from typing import Any, Callable

from flask import Blueprint, Response, abort, request, session

from automation.db import FunctionResultsRepo, ResultsRepo
from automation.models.results.types import ExpectedResultType

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


def login_required(f: Callable[..., Response]) -> Callable[..., Response]:
    """Decorator to require user to be logged in."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Response:
        if "user" not in session:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@api_bp.put(
    "/commits/<config_name>/<commit>/<diffkemp_sha>"
    "/functions/<function_name>/expected-result"
)
@login_required
def update_fun_expected_res_for_commit(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
    function_name: str,
) -> Response:
    """Update the expected result for a function."""
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
@login_required
def update_fun_expected_res_for_version(
    config_name: str,
    old_tag: str,
    new_tag: str,
    diffkemp_sha: str,
    function_name: str,
) -> Response:
    """Update the expected result for a function."""
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


@api_bp.put(
    "/commits/<config_name>/<commit>/<diffkemp_sha>"
    "/note"
)
@login_required
def update_res_note_for_commit(
    config_name: str,
    commit: str,
    diffkemp_sha: str,
) -> Response:
    """Update the result note for a commit result."""
    repo = ResultsRepo()
    results = repo.get_commits(
        config_file_name=config_name,
        commit=commit,
        diffkemp_sha=diffkemp_sha,
    )

    if not results:
        abort(404)

    result = results[0]
    note = request.json["note"]

    result.note = note
    repo.update(result)
    return Response(status=200)


@api_bp.put(
    "/versions/<config_name>/<old_tag>/<new_tag>/<diffkemp_sha>"
    "/note"
)
def update_res_note_for_version(
    config_name: str,
    old_tag: str,
    new_tag: str,
    diffkemp_sha: str,
) -> Response:
    """Update the result note for version result."""
    repo = ResultsRepo()
    results = repo.get_versions(
        config_file_name=config_name,
        old_tag=old_tag,
        new_tag=new_tag,
        diffkemp_sha=diffkemp_sha,
    )

    if not results:
        abort(404)

    result = results[0]
    note = request.json["note"]

    result.note = note
    repo.update(result)
    return Response(status=200)
