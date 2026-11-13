"""Descarga de clima diario desde NASA POWER (sin clave) y generador sintetico offline."""
import numpy as np
import pandas as pd
import requests

URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = ["T2M", "T2M_MIN", "T2M_MAX", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN"]


def fetch_power(lat: float, lon: float, start="20100101", end="20241231") -> pd.DataFrame:
    r = requests.get(
        URL,
        params=dict(parameters=",".join(PARAMS), community="AG", latitude=lat,
                    longitude=lon, start=start, end=end, format="JSON"),
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()["properties"]["parameter"]
    df = pd.DataFrame(data)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df.replace(-999, np.nan)


def synthetic(years: int = 12, seed: int = 0, start_year: int = 2010) -> pd.DataFrame:
    """Clima SINTETICO tipo Santa Cruz (verano lluvioso, invierno seco con surazos). Solo para practicar."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(f"{start_year}-01-01", periods=365 * years, freq="D")
    n = len(idx)
    doy = idx.day_of_year.to_numpy()
    yr = (idx.year - start_year).to_numpy()
    season = (1 + np.cos(2 * np.pi * (doy - 15) / 365)) / 2          # 1 = pleno verano
    fac = rng.lognormal(0, 0.2, years + 1)[yr]                        # variabilidad entre años
    rainy = rng.random(n) < np.clip((0.08 + 0.50 * season) * np.sqrt(fac), 0, 0.9)
    amount = rng.gamma(1.3, 7.0, n) * np.where(rng.random(n) < 0.04, 3, 1) * fac
    precip = np.where(rainy, amount, 0.0)
    surge = (rng.random(n) < 0.07 * (1 - season)) * rng.uniform(5, 11, n)   # frentes fríos (surazos)
    tmean = 23.5 + 3.0 * np.cos(2 * np.pi * (doy - 10) / 365) + rng.normal(0, 1.5, n) - surge
    return pd.DataFrame({
        "T2M": tmean,
        "T2M_MIN": tmean - 4.5 - rng.random(n) * 2.5,
        "T2M_MAX": tmean + 5.0 + rng.random(n) * 3.0 + surge * 0.5,
        "PRECTOTCORR": precip,
        "ALLSKY_SFC_SW_DWN": 19 + 4 * np.cos(2 * np.pi * (doy - 10) / 365),
    }, index=idx)
