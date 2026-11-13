import argparse
from .service import analyze


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=-17.78)
    ap.add_argument("--lon", type=float, default=-63.18)
    ap.add_argument("--api", action="store_true", help="descarga NASA POWER si no hay archivos en data/real")
    a = ap.parse_args()
    res = analyze(a.lat, a.lon, a.api)
    print("Procedencia:", res["provenance"])
    for r in res["rotaciones"]:
        print(f"\n== {r['name']}: {r['total']} (P10-P90 {r['p10']:.2f}-{r['p90']:.2f}; mejor {r['best_prob']:.0%})")
        print("  ", " | ".join(r["years_label"]), "\n  ", r["why"])
        for e in r["evidence"]: print("   -", e)
    print("\nRanking estable ante cambios de pesos:", res["stable_ranking"])


if __name__ == "__main__":
    main()
