import app as app_module
import config
import currency
import database


def signed_in_client(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    return client


def test_unexpected_api_failure_is_logged_and_form_data_is_cached(
    db_file, monkeypatch
):
    client = signed_in_client(db_file, monkeypatch)

    def fail_rate(*args, **kwargs):
        raise RuntimeError("rate calculation failed")

    monkeypatch.setattr(currency, "get_rate", fail_rate)
    response = client.post(
        "/api/convert",
        json={"amount": "500", "from": "GBP", "to": "USD"},
    )

    assert response.status_code == 500
    connection = database.get_connection(db_file)
    error = connection.execute("SELECT source, message FROM error_log").fetchone()
    draft = connection.execute("SELECT form_data FROM draft").fetchone()
    connection.close()
    assert error["source"] == "/api/convert"
    assert "rate calculation failed" in error["message"]
    assert '"amount":"500"' in draft["form_data"]


def test_rate_refresh_failure_is_written_to_local_file_and_uses_stored_rates(
    db_file, monkeypatch, tmp_path
):
    client = signed_in_client(db_file, monkeypatch)
    monkeypatch.setattr(config, "LOG_DIR", str(tmp_path / "logs"))

    def fail_refresh(*args, **kwargs):
        raise OSError("provider unavailable")

    monkeypatch.setattr(currency, "refresh_rates", fail_refresh)
    response = client.post(
        "/api/convert",
        json={"amount": "500", "from": "GBP", "to": "USD"},
    )

    assert response.status_code == 200
    assert "latest stored rates" in response.get_json()["warning"]
    log = (tmp_path / "logs" / "network.log").read_text(encoding="utf-8")
    assert "provider unavailable" in log
