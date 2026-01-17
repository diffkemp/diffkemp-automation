"""Module solving authentication of users."""
import logging
import os
from urllib.parse import urlparse

import requests
from flask import Blueprint, flash, redirect, request, session
from werkzeug.wrappers import Response

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")
logger = logging.getLogger(__package__)


def is_safe_redirect(target: str) -> bool:
    """Check if redirect URL is safe (same domain as request)."""
    if not target:
        return False

    # Parse the target URL
    parsed = urlparse(target)

    # Allow relative URLs
    if not parsed.scheme and not parsed.netloc:
        return target.startswith("/") and not target.startswith("//")

    # For absolute URLs, check if domain matches current request
    request_host = urlparse(request.url).netloc
    return parsed.netloc == request_host


@auth_bp.route("/login")
def login() -> Response:
    """For user log in via GitHub App OAuth."""
    # Setting next for redirecting back to the original page after user is
    # logged in.
    next = request.args.get("next", "/")
    session["oauth_next"] = next

    if "GITHUB_LOGIN_CLIENT_ID" not in os.environ:
        raise ValueError("Missing GITHUB_LOGIN_CLIENT_ID var")
    client_id = os.getenv("GITHUB_LOGIN_CLIENT_ID", "")
    github_oauth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
    )
    return redirect(github_oauth_url)


@auth_bp.route("/auth")
def auth() -> Response:
    """Called back from GitHub OAuth."""
    code = request.args.get("code")
    if not code:
        flash("Authentication failed: No code received", "danger")
        logger.error("Authentication failed: No code received")
        return redirect("/")
    secret = os.getenv("GITHUB_LOGIN_SECRET")
    client_id = os.getenv("GITHUB_LOGIN_CLIENT_ID")
    allowed_users = os.getenv("GITHUB_LOGIN_ALLOWED_USERS")

    # Get access token
    try:
        res = requests.post(
            "https://github.com/login/oauth/access_token"
            f"?client_id={client_id}&client_secret={secret}&code={code}",
            headers={"Accept": "application/json"}
        )
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        flash("GitHub authentication failed", "danger")
        logger.error(f"Failed to authenticate: {e}")
        return redirect("/")

    access_token = data["access_token"]

    # Get user information
    try:
        res = requests.get(
            "https://api.github.com/user",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            })
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        flash("Unable to get user information from GitHub", "danger")
        logger.error(f"Unable to get user information from GitHub: {e}")
        return redirect("/")

    login = data["login"]
    if allowed_users and login in allowed_users.split(","):
        session["user"] = login
    else:
        flash("You are not on list of allowed users!!!", "danger")
        logger.error(f"Attempt to log in from {login}")

    # Redirecting back to the original page
    next = session.pop("oauth_next", "/")
    if not is_safe_redirect(next):
        next = "/"
    return redirect(next)


@auth_bp.route("/logout")
def logout() -> Response:
    """Logs out the user."""
    session.pop("user", None)

    next = request.args.get("next", "/")
    if not is_safe_redirect(next):
        next = "/"
    return redirect(next)
