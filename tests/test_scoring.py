import pathlib
import pandas as pd
import pytest
from rotacion.data_layer import load_layers
from rotacion.features import apply_scenario, summarize, year_month_tables
from rotacion.power import synthetic
from rotacion.scoring import (CRITERIA, adjust_weights, calendar_grid, campaign_months, compare, score_rotation,
                              sensitivity, uncertainty, validate_year)
from rotacion.service import analyze, load_catalog, load_templates

catalog = load_catalog()
templates = {k: v["years"] for k, v in load_templates().items()}
df = synthetic()
clim = summarize(df)


def test_summary():
    assert clim["n_years"] >= 10 and clim["precip_p10"] <= clim["precip_p90"]
    assert all(len(clim[k]) == 12 for k in ("m_precip", "m_cold", "m_heat", "m_dry", "m_heavy"))


def test_synthetic_has_wet_summer_dry_winter():
    p = clim["m_precip"]
    assert p[0] > 2 * p[6]


def test_campaign_wraps_year():
    assert campaign_months(11, 4) == [10, 11, 0, 1, 2, 3]


def test_validate_year_detects_overlap():
    assert validate_year(["soya", "mucuna"], catalog)
    assert not validate_year(["soya", "trigo"], catalog)


def test_all_templates_are_valid():
    for name, years in templates.items():
        assert not [e for y in years for e in validate_year(y, catalog)], name


def test_double_campaign_improves_cover():
    a = score_rotation([["soya"]], catalog, clim)["scores"]["cover"]
    b = score_rotation([["soya", "trigo"]], catalog, clim)["scores"]["cover"]
    assert b > a


def test_monoculture_worst_on_pests():
    mono = score_rotation([["soya"]], catalog, clim)["scores"]["pest"]
    div = score_rotation(templates["Doble campaña diversificada"], catalog, clim)["scores"]["pest"]
    assert div > mono


def test_scores_valid_and_explainable():
    res = compare({"Actual": [["soya"]], **templates}, catalog, clim)
    assert len(res) >= 3
    for r in res:
        assert 0 <= r["total"] <= 1 and set(r["scores"]) == set(CRITERIA)
        assert r["gaps"] and r["risks"] and r["evidence"]


def test_drier_scenario_lowers_water_and_irrigation_helps():
    dry = summarize(apply_scenario(df, rain_factor=0.5))
    y = [["soya", "trigo"]]
    assert score_rotation(y, catalog, dry)["scores"]["water"] < score_rotation(y, catalog, clim)["scores"]["water"]
    assert score_rotation(y, catalog, dry, irrigation=1.0)["scores"]["water"] > score_rotation(y, catalog, dry)["scores"]["water"]


def test_barbecho_only_year_is_handled():
    assert score_rotation([[]], catalog, clim)["total"] == 0.0
    assert len(calendar_grid([[]], catalog)) == 1


def test_uncertainty():
    u = uncertainty({"A": [["soya"]], **templates}, catalog, year_month_tables(df), n=30)
    assert all(x["p10"] <= x["p50"] <= x["p90"] for x in u.values())
    assert abs(sum(x["best_prob"] for x in u.values()) - 1) < 1e-9


def test_adjust_weights():
    w, notes = adjust_weights({k: 1.0 for k in CRITERIA}, 8, "arenoso")
    assert w["erosion"] > 1 and w["water"] > 1 and len(notes) == 2


def test_sensitivity_bool():
    assert isinstance(sensitivity({"A": [["soya"]], **templates}, catalog, clim), bool)


def test_data_layer_fallback_and_real(tmp_path):
    L = load_layers(folder=tmp_path)
    assert "SINTÉTICO" in L["provenance"]["Clima"]
    pd.DataFrame({"date": pd.date_range("2020-01-01", periods=24, freq="MS"), "ndvi": 0.5}).to_csv(tmp_path / "ndvi_monthly.csv", index=False)
    L = load_layers(folder=tmp_path)
    assert "archivo local" in L["provenance"]["NDVI (vegetación)"]


def test_service_analyze(tmp_path):
    a = analyze(folder=tmp_path, n_boot=20)
    assert len(a["rotaciones"]) >= 3 and a["rotaciones"][0]["calendar"] and "provenance" in a
    assert "error" in analyze(current=[["soya", "mucuna"]], folder=tmp_path)
    assert len(analyze(excluded=["chia"], folder=tmp_path, n_boot=20)["rotaciones"]) == 4


def test_api():
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/cultivos").json()["cultivos"]
    assert c.post("/api/analisis", json={"current": [["soya", "trigo"]]}).json()["rotaciones"]


def test_frontend_is_served():
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from api.main import app
    r = TestClient(app).get("/")
    assert r.status_code == 200 and "Analiza tu finca" in r.text
