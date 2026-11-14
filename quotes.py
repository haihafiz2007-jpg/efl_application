"""Savings projections and plan recommendations."""
import re
from decimal import Decimal, ROUND_HALF_UP

import database
from errors import InputError

SUPPORTED_YEARS = (1, 5, 10)
SCENARIOS = ("low", "mid", "high")


def _money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _tax_for_profit(profit, rules):
    tax = Decimal("0")
    for index, (threshold, rate) in enumerate(rules):
        threshold = Decimal(str(threshold))
        rate = Decimal(str(rate))
        next_threshold = (
            Decimal(str(rules[index + 1][0]))
            if index + 1 < len(rules)
            else profit
        )
        taxable = max(Decimal("0"), min(profit, next_threshold) - threshold)
        tax += taxable * rate / Decimal("100")
    return tax


def _project(plan, rules, lump_sum, monthly_amount, years, annual_return):
    balance = lump_sum
    contributions = lump_sum
    fees = Decimal("0")
    monthly_return = Decimal(str(annual_return)) / Decimal("1200")
    monthly_fee = Decimal(str(plan["monthly_fee_pct"])) / Decimal("100")
    snapshots = {}
    for month in range(1, years * 12 + 1):
        interest = balance * monthly_return
        fee = balance * monthly_fee
        fees += fee
        balance += interest - fee + monthly_amount
        contributions += monthly_amount
        if month % 12 == 0:
            year = month // 12
            profit = balance - contributions
            tax = _tax_for_profit(max(Decimal("0"), profit), rules)
            snapshots[year] = {
                "final_value": _money(balance - tax),
                "total_profit": _money(profit - tax),
                "total_fees": _money(fees),
                "total_tax": _money(tax),
            }
    return snapshots


def calculate_quote(plan_id, lump_sum, monthly_amount, db_file=None):
    """Return all supported periods/scenarios and the best eligible plan."""
    try:
        plan_id_text = str(plan_id).strip()
        if not re.fullmatch(r"[0-9]+", plan_id_text):
            raise ValueError
        plan_id = int(plan_id_text)
        lump_sum = Decimal(str(lump_sum))
        monthly_amount = Decimal(str(monthly_amount))
    except (TypeError, ValueError, ArithmeticError):
        raise InputError("Choose a plan and enter valid savings amounts.")
    if not lump_sum.is_finite() or not monthly_amount.is_finite():
        raise InputError("Enter finite savings amounts.")
    if lump_sum < 0 or monthly_amount < 0 or (lump_sum == 0 and monthly_amount == 0):
        raise InputError("Enter a lump sum or a monthly contribution greater than zero.")
    if lump_sum.as_tuple().exponent < -2 or monthly_amount.as_tuple().exponent < -2:
        raise InputError("Use at most two decimal places for savings amounts.")

    plans, tax_rules = database.get_plans_and_tax_rules(db_file)
    selected = next((plan for plan in plans if plan["plan_id"] == plan_id), None)
    if selected is None:
        raise InputError("Choose an available investment plan.")

    contribution_per_year = lump_sum + monthly_amount * Decimal("12")
    if monthly_amount < Decimal(str(selected["min_monthly"])):
        raise InputError("The monthly contribution is below this plan's minimum.")
    if selected["min_lump_sum"] is not None and lump_sum < Decimal(str(selected["min_lump_sum"])):
        raise InputError("The initial amount is below this plan's minimum lump sum.")
    if selected["max_per_year"] is not None and contribution_per_year > Decimal(str(selected["max_per_year"])):
        raise InputError("The savings amount exceeds this plan's annual limit.")

    eligible_plans = []
    for plan in plans:
        if monthly_amount < Decimal(str(plan["min_monthly"])):
            continue
        if plan["min_lump_sum"] is not None and lump_sum < Decimal(str(plan["min_lump_sum"])):
            continue
        if plan["max_per_year"] is not None and contribution_per_year > Decimal(str(plan["max_per_year"])):
            continue
        eligible_plans.append(plan)

    max_year = max(SUPPORTED_YEARS)
    selected_rules = tax_rules.get(plan_id, [])
    projections = {}
    for scenario, rate in zip(
        SCENARIOS,
        (selected["return_min_pct"], (selected["return_min_pct"] + selected["return_max_pct"]) / 2, selected["return_max_pct"]),
    ):
        annual = _project(selected, selected_rules, lump_sum, monthly_amount, max_year, rate)
        projections[scenario] = {year: annual[year] for year in SUPPORTED_YEARS}

    recommendation = None
    best_value = None
    years = SUPPORTED_YEARS[-1]
    for plan in eligible_plans:
        rules = tax_rules.get(plan["plan_id"], [])
        midpoint = (plan["return_min_pct"] + plan["return_max_pct"]) / 2
        value = _project(plan, rules, lump_sum, monthly_amount, years, midpoint)[years]["final_value"]
        if best_value is None or value > best_value:
            best_value = value
            recommendation = plan["plan_id"]

    return {
        "plan_id": plan_id,
        "recommended_plan_id": recommendation,
        "projections": projections,
    }
