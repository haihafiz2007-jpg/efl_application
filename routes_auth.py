"""Account registration, authentication, and contact details."""
import sqlite3
import re

from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import database
import security

bp = Blueprint("auth", __name__)


def _text(data, key):
    value = data.get(key, "")
    return value.strip() if isinstance(value, str) else ""


@bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = _text(data, "name")
    email = _text(data, "email").lower()
    phone = _text(data, "phone")
    password = data.get("password", "")
    if not isinstance(password, str):
        password = ""
    if (
        not name
        or len(name) > 120
        or len(email) > 254
        or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)
    ):
        return jsonify({"error": "Enter a valid name and email address."}), 400
    if len(password) < 12:
        return jsonify({"error": "Use a password with at least 12 characters."}), 400
    try:
        user_id = database.create_user(
            name,
            email,
            phone,
            generate_password_hash(password),
            current_app.config["DB_FILE"],
        )
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with that email already exists."}), 409
    session.clear()
    session["user_id"] = user_id
    return jsonify({"message": "Account created.", "user_id": user_id}), 201


@bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = database.get_user_by_email(_text(data, "email"), current_app.config["DB_FILE"])
    password = data.get("password", "")
    if not isinstance(password, str):
        password = ""
    if (
        user is None
        or user["password_hash"] == "not-set"
        or not check_password_hash(user["password_hash"], password)
    ):
        return jsonify({"error": "Email or password is incorrect."}), 401
    session.clear()
    session["user_id"] = user["user_id"]
    return jsonify({"message": "Signed in.", "user_id": user["user_id"]})


@bp.route("/api/logout", methods=["POST"])
@security.login_required
def logout():
    session.clear()
    return jsonify({"message": "Signed out."})


@bp.route("/api/profile", methods=["GET", "PUT"])
@security.login_required
def profile():
    db_file = current_app.config["DB_FILE"]
    user_id = security.current_user_id()
    if request.method == "GET":
        return jsonify(database.get_user(user_id, db_file))

    data = request.get_json(silent=True) or {}
    name = _text(data, "name")
    phone = _text(data, "phone")
    if not name or len(name) > 120 or len(phone) > 40:
        return jsonify({"error": "Enter a name and a phone number of at most 40 characters."}), 400
    if not database.update_user_contacts(user_id, name, phone, db_file):
        return jsonify({"error": "Your account could not be found."}), 404
    return jsonify(database.get_user(user_id, db_file))
