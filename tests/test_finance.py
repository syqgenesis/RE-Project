import copy

import pytest

from flip.config import load_assumptions
from flip.stages.finance import DealInputs, max_price, profit, sdlt, sensitivity

CFG = load_assumptions()


def cfg_with(buyer: str) -> dict:
    c = copy.deepcopy(CFG)
    c["investor"]["buyer_type"] = buyer
    return c


@pytest.mark.parametrize("price,expected", [
    (125_000, 0),
    (250_000, 2_500),                 # 2% of 125k
    (500_000, 2_500 + 12_500),        # + 5% of 250k
    (1_000_000, 2_500 + 33_750 + 7_500),  # 5% of 675k, 10% of 75k
])
def test_sdlt_main_residence_bands(price, expected):
    assert sdlt(price, cfg_with("individual_main")) == pytest.approx(expected)


def test_sdlt_additional_dwelling_surcharge():
    # 500k: standard 15,000 + 5% surcharge on the whole price (25,000)
    assert sdlt(500_000, cfg_with("individual_additional")) == pytest.approx(40_000)


def test_sdlt_company_without_relief_is_flat_17pct():
    c = cfg_with("company")
    c["investor"]["company_developer_relief"] = False
    assert sdlt(600_000, c) == pytest.approx(102_000)


def test_residual_hits_target_profit_on_cost():
    d = DealInputs(gdv=700_000, works=60_000, planning_fee=0, months=6)
    p = max_price(d, CFG)
    assert p is not None and 0 < p < 700_000
    pr, tot = profit(p, d, CFG)
    # at the max price, profit equals the 20% target within the rounding step
    assert pr == pytest.approx(0.20 * tot, abs=300)
    pr2, tot2 = profit(p + 1_000, d, CFG)
    assert pr2 < 0.20 * tot2


def test_hand_calculated_cost_lines():
    c = cfg_with("individual_main")
    d = DealInputs(gdv=500_000, works=40_000, planning_fee=0, months=6)
    pr, tot = profit(300_000, d, c)
    expected_costs = (300_000 + 5_000 + 2_500 + 1_200 + 46_000 + 3_200
                      + 210_000 * 0.0085 * 6 + 210_000 * 0.03 + 450 * 6 + 7_500 + 1_500)
    assert tot == pytest.approx(expected_costs)
    assert pr == pytest.approx(500_000 - expected_costs)


def test_no_price_works_returns_none():
    d = DealInputs(gdv=100_000, works=200_000, planning_fee=0, months=6)
    assert max_price(d, CFG) is None


def test_sensitivity_monotone():
    d = DealInputs(gdv=700_000, works=60_000, planning_fee=0, months=6)
    rows = sensitivity(d, CFG, asking=450_000)
    assert len(rows) == 8
    base = next(r for r in rows if r["gdv_shift"] == 0 and r["works_shift"] == 0)
    worst = next(r for r in rows if r["gdv_shift"] == -0.10 and r["works_shift"] == 0.15)
    assert worst["max_price"] < base["max_price"]
    assert worst["profit_at_asking"] < base["profit_at_asking"]
