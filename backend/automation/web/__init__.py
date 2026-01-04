"""
Python package proving web interface for the automation.

:author: Lukas Petr
"""
import logging
import sys

import gunicorn.app.wsgiapp as wsgiapp
from flask import Flask, redirect, url_for
from flask.typing import ResponseReturnValue


def create_app() -> Flask:
    app = Flask(__name__)

    from .commits import commits_bp
    from .versions import versions_bp
    from .viewer import view_results_bp

    app.register_blueprint(versions_bp)
    app.register_blueprint(commits_bp)
    app.register_blueprint(view_results_bp)

    @app.route("/")
    def index() -> ResponseReturnValue:
        return redirect(url_for("versions_bp.versions_list"))

    return app


def development_run() -> None:
    """Entry point for running the web server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the DiffKemp Automation web server"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)"
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    app = create_app()
    app.run(host=args.host, port=args.port, debug=True)


def release_run() -> None:
    sys.argv = ["gunicorn", "-w", "4", "-b", "localhost:49000",
                "automation.web:create_app()"]
    wsgiapp.run()
