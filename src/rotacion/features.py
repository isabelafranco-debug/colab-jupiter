"""Indicadores climaticos por año-mes (calor, frio, secas, lluvia intensa)."""
import pandas as pd

MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
COLD_C, HEAT_C, HEAVY_MM = 10.0, 35.0, 30.0   # umbrales ajustables (frente frío, calor, lluvia intensa)


def _longest_run(s) -> int:
    best = cur = 0
    for v in s.to_numpy():
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


def year_month_tables(df: pd.DataFrame) -> dict:
    y, m = df.index.year, df.index.month
    piv = lambda s: s.unstack().reindex(columns=range(1, 13)).fillna(0)
    return {
        "precip": piv(df["PRECTOTCORR"].groupby([y, m]).sum()),
        "cold": piv((df["T2M_MIN"] <= COLD_C).groupby([y, m]).sum()),
        "heat": piv((df["T2M_MAX"] >= HEAT_C).groupby([y, m]).sum()),
        "heavy": piv((df["PRECTOTCORR"] >= HEAVY_MM).groupby([y, m]).sum()),
        "dry": piv((df["PRECTOTCORR"] < 1.0).groupby([y, m]).apply(_longest_run)),  # racha seca máx. del mes
    }


def climate_from_years(tables: dict, years=None) -> dict:
    sel = (lambda t: t) if years is None else (lambda t: t.loc[years])
    P, C, H, V, D = (sel(tables[k]) for k in ("precip", "cold", "heat", "heavy", "dry"))
    annual = P.sum(axis=1)
    return {
        "n_years": int(len(P)),
        "precip_mean": float(annual.mean()),
        "precip_p10": float(annual.quantile(0.10)),   # año seco típico
        "precip_p90": float(annual.quantile(0.90)),
        "m_precip": P.mean().tolist(), "m_cold": C.mean().tolist(), "m_heat": H.mean().tolist(),
        "m_heavy": V.mean().tolist(), "m_dry": D.mean().tolist(),
    }


def summarize(df: pd.DataFrame) -> dict:
    return climate_from_years(year_month_tables(df))


def apply_scenario(df: pd.DataFrame, rain_factor: float = 1.0, temp_delta: float = 0.0) -> pd.DataFrame:
    out = df.copy()
    out["PRECTOTCORR"] = out["PRECTOTCORR"] * rain_factor
    for c in ("T2M", "T2M_MIN", "T2M_MAX"):
        out[c] = out[c] + temp_delta
    return out
