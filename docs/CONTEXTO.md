# Contexto del proyecto (para retomar en un chat nuevo)

> Mantener actualizado. Al abrir un chat nuevo con Claude: "Retomo un proyecto. Repo: <enlace>. Lee `docs/CONTEXTO.md` y haz <tarea concreta>."

## Objetivo
Herramienta de apoyo a decisiones de rotación de cultivos con datos NASA para el reto de hackathon (NASA Space Apps). Piloto en Santa Cruz, Bolivia.
Debe comparar **≥3 rotaciones (incluida la actual)** y, para cada una, explicar: por qué se sugiere, evidencia, beneficios, vacíos de información y riesgos a revisar localmente.
**Apoya, no reemplaza, el criterio del agricultor ni la asesoría agronómica local.**

## Estado actual
- **Motor Python** (`src/rotacion/`): `data_layer` (datos reales si existen en `data/real/`, si no API/sintético, siempre con procedencia), `features` (indicadores año-mes), `scoring` (puntaje, vulnerabilidad, incertidumbre, sensibilidad), `service` (función `analyze` que devuelve JSON), `report`, `demo`.
- **Modelo:** una rotación es una lista de **años**; cada año tiene hasta 2 campañas (**verano** nov–abr, **invierno** may–sep). Se valida que no haya superposición de calendario.
- **Cultivos** (`data/crops.csv`, 14): soya, maíz verano/invierno, sorgo, arroz, sésamo, trigo, girasol, chía, garbanzo y coberturas (mucuna, nabo forrajero, crotalaria, avena). **Valores y calendarios ILUSTRATIVOS, no validados.**
- **8 criterios:** agua, nitrógeno, erosión, materia orgánica, cobertura, plagas, mercado, clima (calor ≥35 °C, frentes fríos ≤10 °C, rachas secas, lluvia intensa ≥30 mm sobre suelo descubierto). Ajustes por riego, textura y pendiente.
- **Incertidumbre:** bootstrap de años (200 remuestreos): rango P10–P90 y probabilidad de ser la mejor. Solo refleja variabilidad climática, no incertidumbre de parámetros.
- **Interfaces:** app Streamlit (`app/`), API FastAPI (`api/main.py`, sirve el frontend), frontend HTML (`frontend/index.html`) inspirado en la sección «Detección y monitoreo» de satellitesonfire.com (solo estructura, textos propios).
- **Datos:** sintéticos por defecto (clima tipo Santa Cruz); NASA POWER por API (`fetch_power`); archivos reales en `data/real/` (contrato en `data/real/README.md`).
- **Pruebas:** 17 en verde (`pytest`, `pytest.ini` ya define el path).

## Qué NO está hecho / límites conocidos
- NDVI (MODIS) y humedad del suelo (SMAP) **solo se muestran, no entran al puntaje**.
- `fetch_power` **no se ha probado con red real** desde el entorno de desarrollo.
- No hay descarga automática de SMAP, MODIS, IMERG ni SRTM (requiere cuenta Earthdata; vía AppEEARS o `earthaccess`).
- Sin historial de análisis, sin mapa, sin alertas.
- Fuentes solo de EE. UU. (WSS, SSURGO, CDL, PRISM, NASS, etc.) descartadas por no cubrir Bolivia.

## Pendiente (en orden de valor)
1. Integrar NDVI y humedad del suelo reales al puntaje (cobertura y agua).
2. Probar `fetch_power` con red y guardar el CSV en `data/real/`; descargar NDVI y SMAP reales.
3. Validar cultivos y calendarios con técnicos/productores (INIAF, CIAT, ANAPO). Ver preguntas en `docs/09-bolivia-santa-cruz.md`.
4. IMERG (lluvia extrema) y SRTM (pendiente) reales.
5. Historial por lote, mapa (Leaflet/MapLibre) y, si se quiere, alertas por umbral.
6. Incluir incertidumbre de parámetros en el rango.

## Decisiones tomadas
- Python para datos y motor; el frontend consume la API (`docs/10-api-frontend.md`).
- Todo resultado muestra procedencia (real/sintético), vacíos y riesgos; nunca presentar sintético como evidencia.
- Modelo explicable (reglas + puntaje ponderado) antes que ML.
- Usar solo texto/estructura propios al inspirarse en sitios de terceros.

## Mapa de documentos
`README.md` · `docs/08-guia-mvp.md` (integración de datos reales, demo, plan B) · `docs/09-bolivia-santa-cruz.md` · `docs/10-api-frontend.md` · `docs/06-plan-hackathon.md` · `docs/07-checklist-entrega.md` · `exercises/README.md`.

## Comandos (PowerShell, desde la carpeta del repo)
```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m pytest -q
python -m streamlit run app/streamlit_app.py
python -m uvicorn api.main:app --reload        # frontend en http://localhost:8000
```
