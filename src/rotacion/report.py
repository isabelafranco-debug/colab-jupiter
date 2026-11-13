from .features import MONTHS
from .scoring import CRITERIA


def build_report(a: dict, scenario=(0.0, 0.0)) -> str:
    L = ["# Informe de rotación de cultivos", "",
         "> Herramienta de apoyo. No reemplaza el criterio del agricultor ni la asesoría agronómica local.", "",
         "## Procedencia de los datos"] + [f"- {k}: {v}" for k, v in a["provenance"].items()]
    L += ["", f"Escenario: lluvia {scenario[0]:+.0f} %, temperatura {scenario[1]:+.1f} °C", ""] + [f"- {n}" for n in a["notes"]]
    L += ["", "## Comparación"]
    for r in a["rotaciones"]:
        L += ["", f"### {r['name']} — {r['total']:.2f} (rango {r['p10']:.2f}–{r['p90']:.2f}; mejor en {r['best_prob']:.0%} de los escenarios)",
              r["description"], "", *[f"- {y}" for y in r["years_label"]], "", r["why"], "",
              "**Puntajes:** " + "; ".join(f"{CRITERIA[k]} {v:.2f}" for k, v in r["scores"].items()), "", "**Evidencia**"]
        L += [f"- {e}" for e in r["evidence"]] + ["", "**Vacíos de información**"] + [f"- {g}" for g in r["gaps"]]
        L += ["", "**Riesgos a revisar localmente**"] + [f"- {g}" for g in r["risks"]]
    return "\n".join(L)
