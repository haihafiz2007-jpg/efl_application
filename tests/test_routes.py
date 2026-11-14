import pytest
import database
import app as app_module

@pytest.fixture
def client(db_file):
    app_module.app.config["DB_FILE"] = db_file
    test_client = app_module.app.test_client()
    with test_client.session_transaction() as session:
        session["user_id"] = 1
    return test_client

def post_convert(client, amount, from_code="GBP", to_code="USD"):
    return client.post("/api/convert", json={"amount": amount, "from": from_code, "to": to_code})

def test_currencies_route_lists_six(client):
    response = client.get("/api/currencies")
    assert response.status_code == 200
    assert len(response.get_json()) == 6

def test_convert_300_gbp_to_usd(client):
    response = post_convert(client, "300")
    data = response.get_json()
    assert response.status_code == 200
    assert data["converted"] == "390.00"
    assert data["fee_percent"] == "3.5"
    assert data["fee_usd"] == "13.65"

def test_convert_2501_gbp_to_usd(client):
    data = post_convert(client, "2501").get_json()
    assert data["converted"] == "3251.30"
    assert data["fee_usd"] == "48.77"

def test_convert_saves_a_transaction(client, db_file):
    post_convert(client, "500")
    connection = database.get_connection(db_file)
    rows = connection.execute("SELECT amount, fee_usd FROM conversion_transaction").fetchall()
    connection.close()
    assert len(rows) == 1
    assert rows[0]["fee_usd"] == 22.75

def test_below_minimum_is_rejected_with_message(client):
    response = post_convert(client, "299")
    assert response.status_code == 400
    assert "between 300 and 5,000" in response.get_json()["error"]

def test_same_currency_is_rejected(client):
    response = post_convert(client, "500", "GBP", "GBP")
    assert response.status_code == 400

def test_unknown_currency_is_rejected(client):
    response = post_convert(client, "500", "GBP", "XYZ")
    assert response.status_code == 400

def test_missing_body_is_rejected(client):
    response = client.post("/api/convert")
    assert response.status_code == 400
