import os
import secrets
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

import config
import database
import pages
import routes_auth
import routes_convert
import routes_quote
import security

app = Flask(__name__)
app.config["DB_FILE"] = config.DB_FILE
app.config["SECRET_KEY"] = os.environ.get("EFL_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("EFL_COOKIE_SECURE", "").lower() == "true"
app.secret_key = app.config["SECRET_KEY"]

app.register_blueprint(pages.bp)
app.register_blueprint(routes_auth.bp)
app.register_blueprint(routes_convert.bp)
app.register_blueprint(routes_quote.bp)

log_dir = Path(config.LOG_DIR)
if not log_dir.is_absolute():
    log_dir = Path(__file__).parent / log_dir
log_dir.mkdir(parents=True, exist_ok=True)
if not any(getattr(handler, "baseFilename", "").endswith("efl.log") for handler in app.logger.handlers):
    file_handler = RotatingFileHandler(log_dir / "efl.log", maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel("ERROR")
    app.logger.addHandler(file_handler)
app.logger.setLevel("INFO")

@app.context_processor
def inject_current_user():
    return {"current_user_id": security.current_user_id()}


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    if isinstance(error, HTTPException) and (error.code or 500) < 500:
        return error

    if isinstance(error, HTTPException):
        app.logger.error("HTTP %s error on %s.", error.code, request.path)
    else:
        app.logger.exception("Unhandled application error on %s.", request.path)
    try:
        database.log_error(
            request.path,
            type(error).__name__ + ": " + str(error),
            app.config["DB_FILE"],
        )
    except Exception:
        app.logger.exception("Could not write the application error to the database.")

    user_id = security.current_user_id()
    if user_id is not None and request.method in {"POST", "PUT", "PATCH"}:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            try:
                database.save_quote_draft(user_id, data, app.config["DB_FILE"])
            except Exception:
                app.logger.exception("Could not cache submitted form data.")

    if request.path.startswith("/api/"):
        return jsonify({"error": "An unexpected error occurred. Your submitted data was retained when possible."}), 500
    return "An unexpected error occurred. Please try again.", 500

if __name__ == "__main__":
    app.run(debug=os.environ.get("EFL_DEBUG", "").lower() == "true")