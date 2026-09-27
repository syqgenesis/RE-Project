import datetime as dt
import json

from flip.sources import land_registry, web


def test_parse_rightmove_page_model():
    model = {"propertyData": {
        "address": {"displayAddress": "Mill Road, Cambridge", "outcode": "CB1", "incode": "2AB"},
        "prices": {"primaryPrice": "£525,000"}, "tenure": {"tenureType": "FREEHOLD"},
        "propertySubType": "Semi-Detached", "bedrooms": 3,
        "sizings": [{"unit": "sqft", "minimumSize": 1000}, {"unit": "sqm", "minimumSize": 93}],
        "text": {"description": "<p>A <b>tired</b> house</p>"},
        "images": [{"url": "https://x/1.jpg"}], "floorplans": [{"url": "https://x/fp.png"}],
        "location": {"latitude": 52.2, "longitude": 0.14}}}
    html = f"<script>window.PAGE_MODEL = {json.dumps(model)}</script>"
    d = web.parse_listing_html(html)
    assert d["postcode"] == "CB1 2AB" and d["asking_price"] == 525000
    assert d["tenure"] == "FREEHOLD" and d["floor_area_m2"] == 93
    assert "tired" in d["description"] and "<b>" not in d["description"]
    assert d["photos"] == ["https://x/1.jpg"]


def test_sector():
    assert land_registry.sector("CB1 2AB") == "CB1 2"
    assert land_registry.sector("cb10 1aa") == "CB10 1"


def test_price_paid_filters(tmp_path):
    rows = [
        ["{A}", "500000", "2026-03-01 00:00", "CB1 2AB", "S", "N", "F", "12", "", "MILL ROAD", "", "CAMBRIDGE", "", "", "A", "A"],
        ["{B}", "300000", "2026-03-01 00:00", "CB1 2AB", "F", "N", "L", "3", "FLAT 1", "MILL ROAD", "", "CAMBRIDGE", "", "", "A", "A"],
        ["{C}", "900000", "2020-03-01 00:00", "CB1 2AB", "D", "N", "F", "1", "", "MILL ROAD", "", "CAMBRIDGE", "", "", "A", "A"],
        ["{D}", "450000", "2026-02-01 00:00", "CB10 1AA", "T", "N", "F", "2", "", "HIGH ST", "", "SAFFRON WALDEN", "", "", "A", "A"],
        ["{E}", "1", "2026-02-01 00:00", "CB1 2AB", "T", "N", "F", "4", "", "MILL ROAD", "", "CAMBRIDGE", "", "", "B", "A"],
    ]
    import csv
    with open(tmp_path / "pp-2026.csv", "w", newline="") as f:
        csv.writer(f).writerows(rows)
    out = land_registry.price_paid({"CB1 2"}, dt.date(2025, 1, 1), ppd_dir=tmp_path)
    assert [r["price"] for r in out] == [500000, 300000]
    assert out[1]["property_type"] == "flat" and out[1]["tenure"] == "leasehold"


def test_wayback_spread():
    rel = [{"date": f"20{i:02d}-01-01"} for i in range(14, 27)]
    picked = web.pick_spread(rel, 4)
    assert picked[0]["date"] == "2014-01-01" and picked[-1]["date"] == "2026-01-01" and len(picked) == 4


def test_buffer_wkt_closed():
    w = web.buffer_wkt(52.2, 0.14, 10)
    assert w.startswith("POLYGON((") and w.count(",") == 4
