"""Puntaje explicable de rotaciones con doble campaña (verano/invierno). Escala 0-1.
Una rotación es una lista de AÑOS; cada año es una lista de 0-2 cultivos (campañas)."""
import numpy as np
import pandas as pd
from .features import climate_from_years, MONTHS

CRITERIA = {
    "water": "Uso de agua",
    "nitrogen": "Nitrógeno (leguminosas)",
    "erosion": "Reducción de erosión",
    "organic": "Materia orgánica",
    "cover": "Cobertura del suelo",
    "pest": "Ruptura de ciclos de plagas",
    "market": "Mercado / ingreso",
    "climate": "Ajuste al clima (calor, frío, secas)",
}
DEFAULT_WEIGHTS = {k: 1.0 for k in CRITERIA}

GAPS = [
    "Humedad del suelo (SMAP) y NDVI se muestran como contexto, pero aún no entran al puntaje.",
    "Suelo local (textura, materia orgánica, compactación) solo se aproxima con textura y pendiente: validar con análisis de laboratorio.",
    "Calendarios y parámetros de cultivos genéricos: ajustar a variedades, fechas y zona con técnicos locales.",
    "Los datos satelitales son de baja resolución: describen la zona, no la parcela exacta.",
    "Precios y costos no están integrados: el criterio de mercado es una estimación relativa.",
]
RISKS = [
    "Disponibilidad de semilla, maquinaria, mano de obra y silos/acopio.",
    "Precios, contratos y acceso a mercado de los cultivos propuestos.",
    "Plagas y enfermedades locales específicas (p. ej., por repetir soya).",
    "Validar con un agrónomo o extensionista antes de decidir.",
]


def campaign_months(sow: int, harvest: int) -> list:
    m, out = sow - 1, []
    while True:
        out.append(m % 12)
        if m % 12 == harvest - 1:
            return out
        m += 1


def validate_year(year: list, catalog: pd.DataFrame) -> list:
    c, used, errs = catalog.set_index("crop"), {}, []
    for crop in year:
        r = c.loc[crop]
        ms = set(campaign_months(int(r.sow_month), int(r.harvest_month)))
        errs += [f"{r.nombre} y {c.loc[o].nombre} se superponen en el calendario." for o, om in used.items() if ms & om]
        used[crop] = ms
    return errs


def describe(years: list, catalog: pd.DataFrame) -> list:
    n = catalog.set_index("crop").nombre
    return [f"Año {i + 1}: " + (" + ".join(n[x] for x in y) if y else "barbecho") for i, y in enumerate(years)]


def calendar_grid(years: list, catalog: pd.DataFrame) -> list:
    c, rows = catalog.set_index("crop"), []
    for i, y in enumerate(years):
        for crop in y or []:
            r = c.loc[crop]
            idx = campaign_months(int(r.sow_month), int(r.harvest_month))
            rows.append({"label": f"Año {i + 1} · {r.nombre}", "months": [m in idx for m in range(12)]})
        if not y:
            rows.append({"label": f"Año {i + 1} · barbecho", "months": [False] * 12})
    return rows


def vulnerability(years, catalog, climate, irrigation=0.0) -> dict:
    c = catalog.set_index("crop")
    a = {k: np.array(climate[k]) for k in ("m_precip", "m_cold", "m_heat", "m_dry", "m_heavy")}
    scale = climate["precip_p10"] / climate["precip_mean"] if climate["precip_mean"] > 0 else 1.0
    camps, ys = [], []
    for i, year in enumerate(years):
        covered = set()
        for crop in year:
            r = c.loc[crop]
            idx = campaign_months(int(r.sow_month), int(r.harvest_month))
            covered |= set(idx)
            rain, need = float(a["m_precip"][idx].sum() * scale), float(r.water_need_mm)
            camps.append({
                "year": i + 1, "crop": crop, "nombre": r.nombre, "idx": idx, "need": need,
                "rain_dry_year": rain, "water_ratio": min((rain + irrigation * max(need - rain, 0)) / need, 1.0),
                "cold_days": float(a["m_cold"][idx].sum()), "heat_days": float(a["m_heat"][idx].sum()),
                "dry_spell": float(a["m_dry"][idx].max()), "heavy_days": float(a["m_heavy"][idx].sum()),
            })
        ys.append({"year": i + 1, "bare": [m for m in range(12) if m not in covered]})
    return {"campaigns": camps, "years": ys}


def _pest_score(families: list) -> float:
    n = len(families)
    if n == 0:
        return 0.0
    d = len(set(families))
    r = sum(families[i] == families[(i + 1) % n] for i in range(n))
    return float(np.clip((d - 1) / 3 - 0.25 * r / n, 0, 1))


def score_rotation(years, catalog, climate, weights=None, irrigation=0.0) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    c = catalog.set_index("crop")
    flat = [x for y in years for x in y]
    if not flat:
        z = {k: 0.0 for k in CRITERIA}
        return {"years": years, "total": 0.0, "scores": z, "why": "Sin cultivos: solo barbecho.",
                "evidence": ["Sin cobertura ni ingreso."], "gaps": GAPS, "risks": RISKS}
    v = vulnerability(years, catalog, climate, irrigation)
    camps, ys = v["campaigns"], v["years"]
    heavy_bare = float(np.mean([np.array(climate["m_heavy"])[y["bare"]].sum() for y in ys]))

    def pen(x):
        r = c.loc[x["crop"]]
        return (0.35 * r.cold_sensitive * min(x["cold_days"] / 8, 1) + 0.35 * r.heat_sensitive * min(x["heat_days"] / 10, 1)
                + 0.30 * r.drought_sens * float(np.clip((x["dry_spell"] - 10) / 20, 0, 1)))

    scores = {
        "water": float(np.mean([x["water_ratio"] for x in camps])),
        "nitrogen": float(np.mean([min(c.loc[y].n_fixing.sum(), 1) for y in years])),
        "erosion": float(np.clip(c.loc[flat].erosion.mean() * (1 - 0.5 * min(heavy_bare / 5, 1)), 0, 1)),
        "organic": float(c.loc[flat].organic.mean()),
        "cover": float(np.mean([(12 - len(y["bare"])) / 12 for y in ys])),
        "pest": _pest_score(list(c.loc[flat].family)),
        "market": float(np.mean([min(c.loc[y].market.sum(), 1) for y in years])),
        "climate": float(np.clip(1 - np.mean([pen(x) for x in camps]), 0, 1)),
    }
    tw = sum(weights[k] for k in CRITERIA)
    contrib = {k: weights[k] * scores[k] / tw for k in CRITERIA}
    top = sorted(contrib, key=contrib.get, reverse=True)[:2]
    ww, wx = min(camps, key=lambda x: x["water_ratio"]), max(camps, key=pen)
    bare_mean = float(np.mean([len(y["bare"]) for y in ys]))
    evidence = [
        f"Agua: en un año seco, {ww['nombre']} (año {ww['year']}) recibiría ≈{ww['rain_dry_year']:.0f} mm en su campaña frente a ≈{ww['need']:.0f} mm necesarios"
        + (f" (con riego cubriendo {irrigation:.0%} del faltante)." if irrigation > 0 else "."),
        f"Clima: {wx['nombre']} es el cultivo más expuesto: ≈{wx['heat_days']:.0f} días ≥35 °C, ≈{wx['cold_days']:.0f} días ≤10 °C y rachas secas de ≈{wx['dry_spell']:.0f} días.",
        f"Suelo: ≈{bare_mean:.1f} meses/año sin cultivo; en ellos caen ≈{heavy_bare:.1f} días/año de lluvia intensa (≥30 mm).",
        f"Basado en {climate['n_years']} años de datos" + (" (pocos: confianza baja)." if climate["n_years"] < 10 else "."),
    ]
    return {"years": years, "total": round(sum(contrib.values()), 3), "scores": {k: round(x, 3) for k, x in scores.items()},
            "why": "Principales aportes: " + ", ".join(CRITERIA[k] for k in top) + ".",
            "evidence": evidence, "gaps": GAPS, "risks": RISKS}


def compare(rotations: dict, catalog, climate, weights=None, irrigation=0.0) -> list:
    res = [{"name": n, **score_rotation(y, catalog, climate, weights, irrigation)} for n, y in rotations.items()]
    return sorted(res, key=lambda d: d["total"], reverse=True)


def adjust_weights(weights: dict, slope_pct: float, texture: str):
    w, notes = {k: float(v) for k, v in weights.items()}, []
    if slope_pct >= 5:
        w["erosion"] *= 1.5; w["cover"] *= 1.3
        notes.append(f"Pendiente {slope_pct:.0f} %: se dio más peso a erosión y cobertura.")
    if texture == "arenoso":
        w["water"] *= 1.3; w["organic"] *= 1.2
        notes.append("Suelo arenoso: retiene poca agua; más peso a agua y materia orgánica.")
    if texture == "arcilloso":
        notes.append("Suelo arcilloso: riesgo de encharcamiento y compactación no modelado; validar localmente.")
    return w, notes


def uncertainty(rotations, catalog, tables, weights=None, irrigation=0.0, n=200, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    years = np.array(tables["precip"].index)
    tot, wins = {k: [] for k in rotations}, {k: 0 for k in rotations}
    for _ in range(n):
        res = compare(rotations, catalog, climate_from_years(tables, rng.choice(years, len(years))), weights, irrigation)
        for r in res:
            tot[r["name"]].append(r["total"])
        wins[res[0]["name"]] += 1
    return {k: {"p10": float(np.percentile(v, 10)), "p50": float(np.percentile(v, 50)),
                "p90": float(np.percentile(v, 90)), "best_prob": wins[k] / n} for k, v in tot.items()}


def sensitivity(rotations, catalog, climate, weights=None, irrigation=0.0, delta=0.2) -> bool:
    base = weights or DEFAULT_WEIGHTS
    best = compare(rotations, catalog, climate, base, irrigation)[0]["name"]
    for k in CRITERIA:
        for f in (1 - delta, 1 + delta):
            w = dict(base); w[k] = base[k] * f
            if compare(rotations, catalog, climate, w, irrigation)[0]["name"] != best:
                return False
    return True
