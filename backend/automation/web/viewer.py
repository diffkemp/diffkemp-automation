"""
Contains HTTP endpoint with DiffKemp viewer.

:author: Lukas Petr
"""
from flask import Blueprint, Response, send_from_directory

from automation.utils import VIEW_RESULTS_DIR

view_results_bp = Blueprint(
    "view_results_bp",
    __name__,
    url_prefix="/view_results",
)


@view_results_bp.route("<path:path>")
def result_viewer(path: str) -> Response:
    """Returns viewer files for given result."""
    if path.endswith("/"):
        path += "index.html"
    return send_from_directory(VIEW_RESULTS_DIR, path)
