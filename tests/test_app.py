import sqlite3

import app as app_module


def test_home_page_opens_login():
    client = app_module.app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"
    login_response = client.get(response.headers["Location"])
    assert login_response.status_code == 200
    assert b"Sign in" in login_response.data


def test_wireframe_pages_render():
    client = app_module.app.test_client()
    assert b"Currency exchange" in client.get("/converter").data
    assert b"Savings quote" in client.get("/quote-page").data
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