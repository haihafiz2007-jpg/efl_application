import app as app_module
import database


def test_private_routes_require_a_login(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()

    assert client.get("/converter").status_code == 302
    assert client.post("/api/convert", json={}).status_code == 401
    assert client.get("/api/profile").status_code == 401


def test_registration_stores_hashed_password_and_contact_details(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()

    response = client.post(
        "/api/register",
        json={
            "name": "Ada Example",
            "email": "Ada@example.test",
            "phone": "555-0101",
            "password": "a secure passphrase",
        },
    )

    assert response.status_code == 201
    user = database.get_user_by_email("ada@example.test", db_file)
    assert user["password_hash"] != "a secure passphrase"
    assert user["phone"] == "555-0101"
    assert client.get("/api/profile").get_json()["name"] == "Ada Example"


def test_login_rejects_bad_credentials_and_profile_edits_stay_scoped(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()
    client.post(
        "/api/register",
        json={"name": "Ada", "email": "ada@example.test", "password": "a secure passphrase"},
    )

    client.post("/api/logout")
    response = client.post(
        "/api/login",
        json={"email": "ada@example.test", "password": "incorrect password"},
    )
    assert response.status_code == 401
    assert client.get("/api/profile").status_code == 401

    client.post(
        "/api/login",
        json={"email": "ada@example.test", "password": "a secure passphrase"},
    )
    response = client.put(
        "/api/profile", json={"name": "Ada Lovelace", "phone": "555-0102"}
    )
    assert response.status_code == 200
    assert response.get_json()["phone"] == "555-0102"
