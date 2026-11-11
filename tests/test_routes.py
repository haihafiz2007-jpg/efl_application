import pytest                                                           # For the fixture
import database                                                         # To read the test database
import app as app_module                                                # Our Flask app, under a nickname so it does not clash with the app name

@pytest.fixture                                                         # Set-up code the tests can ask for
def client(db_file):                                                    # A fake browser connected to a temporary database
    app_module.app.config["DB_FILE"] = db_file                          # Point the app at the test database
    return app_module.app.test_client()                                 # Flask's built-in fake browser

def post_convert(client, amount, from_code="GBP", to_code="USD"):       # Helper: send one conversion request
    return client.post("/api/convert", json={"amount": amount, "from": from_code, "to": to_code})  # json= sets the body and the header for us

def test_currencies_route_lists_six(client):                            # GET /api/currencies
    response = client.get("/api/currencies")                            # Ask for the list
    assert response.status_code == 200                                  # OK
    assert len(response.get_json()) == 6                                # Six currencies

def test_convert_300_gbp_to_usd(client):                                # The first check value
    response = post_convert(client, "300")                              # Convert 300 GBP to USD
    data = response.get_json()                                          # Read the JSON reply
    assert response.status_code == 200                                  # OK
    assert data["converted"] == "390.00"                                # 300 x 1.30
    assert data["fee_percent"] == "3.5"                                 # Lowest band
    assert data["fee_usd"] == "13.65"                                   # 10.50 GBP in dollars

def test_convert_2501_gbp_to_usd(client):                               # The top fee band
    data = post_convert(client, "2501").get_json()                      # Convert 2,501
    assert data["converted"] == "3251.30"                               # 2,501 x 1.30
    assert data["fee_usd"] == "48.77"                                   # 1.5% band

def test_convert_saves_a_transaction(client, db_file):                  # The row must reach the database
    post_convert(client, "500")                                         # Convert once
    connection = database.get_connection(db_file)                       # Open the test database
    rows = connection.execute("SELECT amount, fee_usd FROM conversion_transaction").fetchall()  # Read what was saved
    connection.close()                                                  # Release the file
    assert len(rows) == 1                                               # Exactly one row
    assert rows[0]["fee_usd"] == 22.75                                  # 3.5% of 500 in dollars

def test_below_minimum_is_rejected_with_message(client):                # Validation reaches the user
    response = post_convert(client, "299")                              # One below the minimum
    assert response.status_code == 400                                  # Bad Request
    assert "between 300 and 5,000" in response.get_json()["error"]      # The message states the limits

def test_same_currency_is_rejected(client):                             # GBP to GBP
    response = post_convert(client, "500", "GBP", "GBP")                # Same both sides
    assert response.status_code == 400                                  # Bad Request

def test_unknown_currency_is_rejected(client):                          # A code we do not support
    response = post_convert(client, "500", "GBP", "XYZ")                # XYZ is not offered
    assert response.status_code == 400                                  # Bad Request

def test_missing_body_is_rejected(client):                              # A request with no JSON at all
    response = client.post("/api/convert")                              # No body
    assert response.status_code == 400                                  # Bad Request, not a crash