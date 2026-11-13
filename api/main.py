"""API para el frontend. Ejecutar: uvicorn api.main:app --reload  (con PYTHONPATH=src)"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rotacion.service import PRESETS, ZONAS, analyze, load_catalog
from rotacion.scoring import CRITERIA

app = FastAPI(title="Rotación de cultivos con datos NASA - Bolivia")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Finca(BaseModel):
    lat: float = -17.78
    lon: float = -63.18
    use_api: bool = False
    texture: str = "franco"
    slope: float = 2.0
    current: list[list[str]] = [["soya"]]
    excluded: list[str] = []
    preset: str = "Equilibrado"
    weights: dict[str, float] | None = None
    rain_pct: float = 0.0
    temp_delta: float = 0.0
    irrigation: float = 0.0


@app.get("/api/salud")
def salud():
    return {"ok": True}


@app.get("/api/cultivos")
def cultivos():
    return {"cultivos": load_catalog().to_dict("records"), "criterios": CRITERIA,
            "prioridades": list(PRESETS), "zonas": ZONAS}


@app.post("/api/analisis")
def analisis(f: Finca):
    return analyze(**f.model_dump())


# Sirve el frontend en http://localhost:8000 (debe ir al final, después de las rutas /api)
app.mount("/", StaticFiles(directory=pathlib.Path(__file__).resolve().parents[1] / "frontend", html=True), name="web")
