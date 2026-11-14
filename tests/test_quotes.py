from decimal import Decimal

import app as app_module
import database
import quotes
from errors import InputError


def test_projection_has_three_scenarios_and_supported_periods(db_file):
    result = quotes.calculate_quote(1, "1000", "150", db_file)

    assert result["recommended_plan_id"] in {1, 2, 3}
    for scenario in ("low", "mid", "high"):
        assert list(result["projections"][scenario]) == [1, 5, 10]
        assert (
            result["projections"][scenario][1]["final_value"]
            < result["projections"][scenario][5]["final_value"]
            < result["projections"][scenario][10]["final_value"]
        )
    assert (
        result["projections"]["low"][10]["final_value"]
        < result["projections"]["mid"][10]["final_value"]
        < result["projections"]["high"][10]["final_value"]
    )
    assert result["projections"]["low"][1]["total_profit"] < 0


def test_quote_validation_enforces_plan_limits(db_file):
    try:
        quotes.calculate_quote(2, "100", "40", db_file)
    except InputError as error:
        assert "minimum" in str(error)
    else:
        raise AssertionError("Ineligible plan inputs should be rejected.")


def test_quote_submission_saves_results_and_scopes_saved_quotes(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1

    response = client.post(
        "/api/quotes",
        json={"plan_id": "1", "lump_sum": "1000", "monthly_amount": "150", "save": False},
    )
    assert response.status_code == 201
    quote_id = response.get_json()["quote_id"]
    assert len(response.get_json()["projections"]) == 3
    assert database.list_saved_quotes(1, db_file) == []
    assert client.post(f"/api/quotes/{quote_id}/save").status_code == 200
    assert len(database.list_saved_quotes(1, db_file)) == 9
    with client.session_transaction() as session:
        session["user_id"] = 2
    assert client.post(f"/api/quotes/{quote_id}/save").status_code == 404


def test_failed_quote_is_cached_for_signed_in_user(db_file, monkeypatch):
    monkeypatch.setitem(app_module.app.config, "DB_FILE", db_file)
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1

    response = client.post(
        "/api/quotes",
        json={"plan_id": "2", "lump_sum": "100", "monthly_amount": "40"},
    )
    assert response.status_code == 400
    connection = database.get_connection(db_file)
    draft = connection.execute(
        "SELECT user_id, form_data FROM draft ORDER BY draft_id DESC LIMIT 1"
    ).fetchone()
    connection.close()
    assert draft["user_id"] == 1
    assert '"monthly_amount":"40"' in draft["form_data"]


def test_tax_rules_apply_only_above_each_threshold():
    assert quotes._tax_for_profit(
        Decimal("50000"), [(12000, 10), (40000, 20)]
    ) == Decimal("4800")
