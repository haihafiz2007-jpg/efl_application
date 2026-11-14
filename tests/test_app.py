import sqlite3

import app as app_module
import database


def test_home_page_opens_login():
    client = app_module.app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    login_response = client.get(response.headers["Location"])
    assert login_response.status_code == 200
    assert b"Sign in" in login_response.data


def test_wireframe_pages_render(tmp_path, monkeypatch):
    db_file = str(tmp_path / "test.db")
    database.init_db(db_file)
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    assert b"Currency exchange" in client.get("/converter").data
    quote_response = client.get("/quote-page")
    assert b"Savings quote" in quote_response.data
    assert b'Lump sum (GBP)' in quote_response.data
    assert b'Monthly (GBP)' in quote_response.data
    assert b'Get quote' in quote_response.data
    assert b'<th>Years</th><th>Min</th><th>Max</th><th>Profit</th><th>Fees</th><th>Tax</th>' in quote_response.data
    assert b'Best after-tax profit for your amounts' in quote_response.data
    assert b'projection-chart' in quote_response.data
    assert b"Transaction history" in client.get("/history-page").data


def test_hello_page_shows_message_from_database(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    connection = sqlite3.connect(db_file)
    connection.executescript(
        "CREATE TABLE greeting (id INTEGER PRIMARY KEY, message TEXT NOT NULL);"
        "INSERT INTO greeting (message) VALUES ('Hello from the test database!');"
    )
    connection.commit()
    connection.close()

    monkeypatch.setitem(app_module.app.config, "DB_FILE", str(db_file))
    client = app_module.app.test_client()
    response = client.get("/hello")

    assert response.status_code == 200
    assert b"EFL application" in response.data
    assert b"Hello from the test database!" in response.data