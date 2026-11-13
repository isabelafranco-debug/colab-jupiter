import pathlib, sys
import pandas as pd
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rotacion.features import MONTHS
from rotacion.report import build_report
from rotacion.scoring import CRITERIA, validate_year
from rotacion.service import PRESETS, ZONAS, analyze, load_catalog

st.set_page_config(page_title="Rotación de cultivos · Bolivia", page_icon="🌱", layout="wide")
st.title("🌱 ¿Qué sembrar después? Rotaciones para Santa Cruz")
st.caption("Herramienta de apoyo con observaciones de la NASA. No reemplaza el criterio del agricultor ni la asesoría agronómica local.")

catalog = load_catalog()
names = dict(zip(catalog.crop, catalog.nombre))
summer = list(catalog[catalog.season == "verano"].crop)
winter = list(catalog[catalog.season == "invierno"].crop)
fmt = lambda x: "Barbecho" if x == "—" else names[x]


@st.cache_data(show_spinner="Analizando…")
def run(**kw):
    return analyze(**kw)


with st.sidebar:
    st.header("1 · Mi finca")
    zona = st.selectbox("Zona", list(ZONAS) + ["Otra (ingresar)"])
    lat0, lon0 = ZONAS.get(zona, (-17.78, -63.18))
    lat = st.number_input("Latitud", value=lat0, format="%.3f")
    lon = st.number_input("Longitud", value=lon0, format="%.3f")
    use_api = st.checkbox("Descargar clima real (NASA POWER)", value=False)
    texture = st.selectbox("Textura del suelo", ["franco", "arenoso", "arcilloso"])
    slope = st.slider("Pendiente del lote (%)", 0.0, 20.0, 2.0)
    irrigation = st.slider("Riego disponible (% del faltante de agua)", 0, 100, 0) / 100
    st.header("2 · Mi rotación actual")
    n_years = st.slider("Años de mi rotación", 1, 4, 1)
    current = []
    for i in range(n_years):
        a, b = st.columns(2)
        v = a.selectbox(f"Año {i + 1} · verano", ["—"] + summer, index=1 if i == 0 else 0, format_func=fmt, key=f"v{i}")
        w_ = b.selectbox(f"Año {i + 1} · invierno", ["—"] + winter, format_func=fmt, key=f"w{i}")
        current.append([x for x in (v, w_) if x != "—"])
    excluded = st.multiselect("No puedo / no quiero sembrar", list(catalog.crop), format_func=fmt)
    st.header("3 · Mis prioridades")
    preset = st.radio("¿Qué me importa más?", list(PRESETS), label_visibility="collapsed")
    with st.expander("Ajuste fino (0-3)"):
        weights = {k: float(st.slider(v, 0, 3, int(PRESETS[preset].get(k, 1)), key=f"{preset}_{k}")) for k, v in CRITERIA.items()}
    st.header("4 · Escenario")
    rain = st.slider("Cambio de lluvia (%)", -30, 30, 0)
    temp = st.slider("Cambio de temperatura (°C)", -2.0, 4.0, 0.0)

errs = [f"Año {i + 1}: {e}" for i, y in enumerate(current) for e in validate_year(y, catalog)]
if errs:
    st.error("Tu rotación tiene cultivos que se superponen en el calendario:\n\n" + "\n".join(f"- {e}" for e in errs))
    st.stop()
if sum(weights.values()) == 0:
    st.warning("Elige al menos una prioridad.")
    st.stop()

A = run(lat=lat, lon=lon, use_api=use_api, texture=texture, slope=slope, current=current, excluded=tuple(excluded),
        preset=preset, weights=weights, rain_pct=rain, temp_delta=temp, irrigation=irrigation)
if any("SINTÉTICO" in v or "DEFECTO" in v for v in A["provenance"].values()):
    st.warning("Algunas capas usan datos sintéticos o por defecto (ver «Mi finca»). No usar como evidencia real.")
for wmsg in A["warnings"]:
    st.warning(wmsg)
R = A["rotaciones"]


def grid(rows):
    return pd.DataFrame([{"Campaña": r["label"], **{m: "■" if f else "·" for m, f in zip(MONTHS, r["months"])}} for r in rows])


t1, t2, t3, t4 = st.tabs(["1 · Resumen", "2 · Mi finca", "3 · Rotaciones", "4 · Informe y fuentes"])

with t1:
    best, actual = R[0], next(r for r in R if r["name"] == "Actual")
    if best["name"] == "Actual":
        st.info(f"Con tus prioridades, tu rotación actual es la mejor opción ({best['total']:.2f}).")
    else:
        st.success(f"Con tus prioridades, **{best['name']}** puntúa {best['total']:.2f} frente a {actual['total']:.2f} de tu rotación actual. "
                   f"Es la mejor en {best['best_prob']:.0%} de los escenarios climáticos simulados.")
    st.dataframe(pd.DataFrame([{"Rotación": r["name"], "Secuencia": " | ".join(r["years_label"]),
                                "Puntaje (rango)": f"{r['p50']:.2f} ({r['p10']:.2f}–{r['p90']:.2f})",
                                "Prob. de ser la mejor": f"{r['best_prob']:.0%}"} for r in R]), hide_index=True)
    st.caption("El rango (P10–P90) remuestrea los años históricos: refleja solo la variabilidad del clima histórico; NO incluye la incertidumbre de los parámetros de cultivos ni de los datos.")
    st.info("Ranking " + ("estable" if A["stable_ranking"] else "sensible") + " ante cambios de ±20 % en tus prioridades.")
    for n in A["notes"]:
        st.caption("• " + n)

with t2:
    cl = A["climate"]
    st.subheader("Calendario de mi rotación actual (■ = con cultivo, · = suelo descubierto)")
    st.dataframe(grid(actual["calendar"]), hide_index=True)
    c1, c2 = st.columns(2)
    c1.write("**Lluvia media mensual (mm)**"); c1.bar_chart(pd.Series(cl["m_precip"], index=MONTHS))
    c2.write("**Días con lluvia intensa (≥30 mm) por mes**"); c2.bar_chart(pd.Series(cl["m_heavy"], index=MONTHS))
    c3, c4 = st.columns(2)
    c3.write("**Días de calor (≥35 °C) por mes**"); c3.bar_chart(pd.Series(cl["m_heat"], index=MONTHS))
    c4.write("**Días de frente frío (mín. ≤10 °C) por mes**"); c4.bar_chart(pd.Series(cl["m_cold"], index=MONTHS))
    c5, c6 = st.columns(2)
    c5.write("**Racha seca máxima típica (días)**"); c5.bar_chart(pd.Series(cl["m_dry"], index=MONTHS))
    c6.write("**NDVI mensual (verdor)**"); c6.bar_chart(pd.Series(A["ndvi"], index=MONTHS))
    st.write("**Meses con vegetación baja (NDVI < 0.25):** " + (", ".join(MONTHS[m] for m in A["low_ndvi_months"]) or "ninguno"))
    st.subheader("Cuándo es más vulnerable mi rotación actual")
    st.dataframe(pd.DataFrame([{"Año": v["year"], "Cultivo": v["nombre"], "Ciclo": f"{MONTHS[v['idx'][0]]}–{MONTHS[v['idx'][-1]]}",
                                "Lluvia en año seco (mm)": round(v["rain_dry_year"]), "Necesidad (mm)": round(v["need"]),
                                "Días ≥35 °C": round(v["heat_days"], 1), "Días ≤10 °C": round(v["cold_days"], 1),
                                "Racha seca (días)": round(v["dry_spell"]), "Lluvia intensa (días)": round(v["heavy_days"], 1)}
                               for v in A["current_vulnerability"]["campaigns"]]), hide_index=True)
    st.subheader("Procedencia de los datos")
    st.table(pd.Series(A["provenance"], name="Fuente"))

with t3:
    for r in R:
        with st.expander(f"{r['name']} — {r['total']:.2f} (rango {r['p10']:.2f}–{r['p90']:.2f})", expanded=r is R[0]):
            st.write(r["description"])
            st.write("**Secuencia:** " + " | ".join(r["years_label"]))
            st.dataframe(grid(r["calendar"]), hide_index=True)
            st.write("**Por qué:** " + r["why"])
            st.write("**Evidencia:**"); [st.write("- " + e) for e in r["evidence"]]
            st.write("**Vacíos de información:**"); [st.write("- " + g) for g in r["gaps"]]
            st.write("**Riesgos a revisar localmente:**"); [st.write("- " + g) for g in r["risks"]]
            st.bar_chart(pd.Series({CRITERIA[k]: v for k, v in r["scores"].items()}))

with t4:
    report = build_report(A, (rain, temp))
    st.download_button("⬇️ Descargar informe (Markdown)", report, "informe_rotacion.md", "text/markdown")
    st.info("Los datos satelitales de la NASA no están respaldados por la NASA para fuentes no estadounidenses; respeta los términos de uso de cada fuente.")
    st.markdown(report)
