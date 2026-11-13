"""Capa de datos: usa archivos reales si existen (data/real/), si no API/sintetico.
Cada capa informa su procedencia para mostrarla al usuario (honestidad sobre los datos)."""
import pathlib
import numpy as np
import pandas as pd
from .power import fetch_power, synthetic

ROOT = pathlib.Path(__file__).resolve().parents[2]
REAL = ROOT / "data" / "real"


def _norm(x):
    x = np.asarray(x, float)
    return (x - x.min()) / (x.max() - x.min() + 1e-9)


def _monthly_csv(path, col) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    s = df.groupby(df["date"].dt.month)[col].mean().reindex(range(1, 13))
    return s.interpolate().bfill().ffill()


def load_layers(lat=-17.78, lon=-63.18, use_api=False, folder=REAL) -> dict:
    folder, prov = pathlib.Path(folder), {}
    p = folder / "power_daily.csv"
    if p.exists():
        daily, prov["Clima"] = pd.read_csv(p, index_col=0, parse_dates=True), "NASA POWER (archivo local)"
    elif use_api:
        try:
            daily, prov["Clima"] = fetch_power(lat, lon), "NASA POWER (API)"
        except Exception as e:  # sin red, límite, etc.
            daily, prov["Clima"] = synthetic(), f"SINTÉTICO (falló la API: {type(e).__name__})"
    else:
        daily, prov["Clima"] = synthetic(), "SINTÉTICO"

    mp = (daily["PRECTOTCORR"].groupby(daily.index.month).sum() / daily.index.year.nunique())
    mp = mp.reindex(range(1, 13)).fillna(0).to_numpy()

    f = folder / "ndvi_monthly.csv"
    if f.exists():
        ndvi, prov["NDVI (vegetación)"] = _monthly_csv(f, "ndvi"), "MODIS/Landsat (archivo local)"
    else:
        ndvi = pd.Series(0.12 + 0.55 * _norm(np.roll(mp, 1)), index=range(1, 13))
        prov["NDVI (vegetación)"] = "SINTÉTICO (derivado de la lluvia)"

    f = folder / "smap_monthly.csv"
    if f.exists():
        sm, prov["Humedad del suelo"] = _monthly_csv(f, "sm"), "SMAP (archivo local)"
    else:
        sm = pd.Series(0.08 + 0.35 * _norm(mp + np.roll(mp, 1)), index=range(1, 13))
        prov["Humedad del suelo"] = "SINTÉTICO (derivado de la lluvia)"

    f = folder / "slope.csv"
    if f.exists():
        slope, prov["Pendiente"] = float(pd.read_csv(f)["slope_pct"].mean()), "SRTM (archivo local)"
    else:
        slope, prov["Pendiente"] = 2.0, "VALOR POR DEFECTO (ingresar la del lote)"
    return {"daily": daily, "ndvi": ndvi, "soil_moisture": sm, "slope_pct": slope, "provenance": prov}
