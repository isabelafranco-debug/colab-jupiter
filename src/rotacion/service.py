"""Capa de servicio: UNA función que devuelve todo en JSON. La usan Streamlit y la API (frontend)."""
import json, pathlib
import pandas as pd
from .data_layer import load_layers, REAL
from .features import apply_scenario, climate_from_years, year_month_tables
from .scoring import (CRITERIA, adjust_weights, calendar_grid, compare, describe, sensitivity,
                      uncertainty, validate_year, vulnerability)

ROOT = pathlib.Path(__file__).resolve().parents[2]
PRESETS = {"Equilibrado": {}, "Ahorrar agua": {"water": 3, "climate": 2},
           "Más ingreso": {"market": 3}, "Mejorar el suelo": {"nitrogen": 3, "organic": 3, "erosion": 2, "cover": 2}}
ZONAS = {  # coordenadas APROXIMADAS: verificar sobre el lote real
    "Santa Cruz de la Sierra (referencia)": (-17.78, -63.18), "Montero (aprox.)": (-17.34, -63.25),
    "San Julián (aprox.)": (-16.92, -62.62), "Cuatro Cañadas (aprox.)": (-17.20, -62.55),
}


def load_catalog() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data/crops.csv")


def load_templates() -> dict:
    return json.loads((ROOT / "data/rotations.json").read_text(encoding="utf-8"))


def analyze(lat=-17.78, lon=-63.18, use_api=False, texture="franco", slope=2.0, current=None, excluded=(),
            preset="Equilibrado", weights=None, rain_pct=0.0, temp_delta=0.0, irrigation=0.0,
            n_boot=200, folder=REAL) -> dict:
    catalog, templates = load_catalog(), load_templates()
    current = current or [["soya"]]
    errs = [f"Año {i + 1}: {e}" for i, y in enumerate(current) for e in validate_year(y, catalog)]
    if errs:
        return {"error": errs}
    layers = load_layers(lat, lon, use_api, folder)
    tables = year_month_tables(apply_scenario(layers["daily"], 1 + rain_pct / 100, temp_delta))
    climate = climate_from_years(tables)
    base = weights or {k: float(PRESETS.get(preset, {}).get(k, 1)) for k in CRITERIA}
    w, notes = adjust_weights(base, slope, texture)
    rotations, descs = {"Actual": current}, {"Actual": "Tu rotación actual (línea base)."}
    for k, v in templates.items():
        if not ({c for y in v["years"] for c in y} & set(excluded)):
            rotations[k], descs[k] = v["years"], v["description"]
    results = compare(rotations, catalog, climate, w, irrigation)
    unc = uncertainty(rotations, catalog, tables, w, irrigation, n=n_boot)
    out = []
    for r in results:
        out.append({**r, "description": descs[r["name"]], "years_label": describe(r["years"], catalog),
                    "calendar": calendar_grid(r["years"], catalog), **unc[r["name"]]})
    return {
        "provenance": layers["provenance"], "notes": notes, "climate": climate,
        "ndvi": layers["ndvi"].tolist(), "soil_moisture": layers["soil_moisture"].tolist(),
        "low_ndvi_months": [m - 1 for m, v in layers["ndvi"].items() if v < 0.25],
        "slope_default": layers["slope_pct"], "rotaciones": out,
        "stable_ranking": sensitivity(rotations, catalog, climate, w, irrigation),
        "current_vulnerability": vulnerability(current, catalog, climate, irrigation),
        "warnings": ["Quedan menos de 3 rotaciones para comparar."] if len(rotations) < 3 else [],
    }
