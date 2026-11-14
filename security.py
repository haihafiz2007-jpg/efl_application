from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def current_user_id():
    """Return the authenticated user id, or None when no user is signed in."""
    user_id = session.get("user_id")
    return int(user_id) if user_id is not None else None


def login_required(view):
    """Require an authenticated session for a page or API endpoint."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user_id() is None:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Sign in to continue."}), 401
            return redirect(url_for("pages.login_page"))
        return view(*args, **kwargs)
    return wrapped