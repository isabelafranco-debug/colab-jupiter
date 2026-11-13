# API para conectar tu frontend

El motor está separado de la interfaz: **Streamlit** y la **API** llaman a la misma función `rotacion.service.analyze`.

## Arrancar
```powershell
$env:PYTHONPATH = "src"
python -m uvicorn api.main:app --reload
```
Documentación interactiva automática: http://localhost:8000/docs

## Endpoints
| Método | Ruta | Qué devuelve |
|---|---|---|
| GET | `/api/salud` | `{"ok": true}` |
| GET | `/api/cultivos` | catálogo de cultivos, criterios, prioridades y zonas |
| POST | `/api/analisis` | todo el análisis de una finca |

## Entrada de `/api/analisis`
```json
{
  "lat": -17.78, "lon": -63.18, "use_api": false,
  "texture": "franco", "slope": 2.0,
  "current": [["soya", "trigo"], ["maiz_verano"]],
  "excluded": ["arroz"],
  "preset": "Ahorrar agua", "weights": null,
  "rain_pct": -20, "temp_delta": 1.0, "irrigation": 0.3
}
```
`current` es una lista de años; cada año, una lista de ids de cultivo (ver `/api/cultivos`). Si hay superposición de calendario devuelve `{"error": [...]}`.

## Salida (campos principales)
- `provenance`: fuente real o sintética de cada capa (mostrarla siempre).
- `climate`: series mensuales (`m_precip`, `m_heat`, `m_cold`, `m_dry`, `m_heavy`) y `precip_p10/mean/p90`.
- `ndvi`, `soil_moisture`: 12 valores mensuales; `low_ndvi_months`: índices 0-11.
- `rotaciones[]`: `name`, `description`, `years_label`, `total`, `p10/p50/p90`, `best_prob`, `scores`, `why`, `evidence`, `gaps`, `risks`, `calendar` (filas con 12 booleanos por campaña).
- `current_vulnerability`, `stable_ranking`, `notes`, `warnings`.

## Para tu frontend
El frontend de ejemplo está en `frontend/index.html` y lo sirve la propia API en http://localhost:8000. Mapa sugerido para una v2: Leaflet o MapLibre con el punto `lat/lon`.
