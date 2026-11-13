# Datasets NASA: qué aportan y cómo acceder

> Verifica enlaces y versiones en la pestaña **Resources** del reto; pueden añadirse más recursos.

| Dataset | Mide | Resolución (aprox.) | Uso en el proyecto | Acceso típico |
|---|---|---|---|---|
| **NASA POWER** | Temperatura, lluvia, radiación, viento (reanálisis + satélite) | ~0.5° (varía por variable), diaria, desde 1981 | Línea base climática, heladas, olas de calor, GDD | API REST sin clave (usado en `src/rotacion/power.py`) |
| **SMAP** | Humedad del suelo (superficie y zona raíz) | ~9–36 km, 2–3 días | Estrés hídrico, anomalías de humedad | Earthdata (earthaccess), AppEEARS |
| **GPM / IMERG** | Precipitación | ~10 km, 30 min–mensual | Lluvia extrema, sequías, patrón estacional | GES DISC, earthaccess |
| **MODIS** (NDVI/EVI, ET, LST) | Vegetación, evapotranspiración, temperatura superficial | 250 m–1 km | **Periodos de suelo desnudo**, estrés de la vegetación | AppEEARS, earthaccess |
| **Landsat 8/9** | Reflectancia, NDVI | 30 m, 16 días | Detalle a nivel de parcela | Earthdata, Google Earth Engine |
| **ECOSTRESS** | Temperatura superficial y estrés hídrico de plantas | ~70 m, irregular | Estrés por calor a escala de campo | LP DAAC / AppEEARS |
| **GRACE / GRACE-FO** | Cambios en almacenamiento de agua (total) | ~300 km, mensual | Tendencia de largo plazo del agua subterránea (contexto regional) | PO.DAAC |
| **SRTM / elevación** | Elevación, pendiente | 30 m | Riesgo de erosión, zonas frías (heladas), escorrentía | OpenTopography, AppEEARS |
| **GEDI** | Estructura de vegetación / biomasa | huellas de 25 m | Biomasa (opcional) | LP DAAC |

## Cuenta Earthdata
Crea una cuenta gratuita en NASA Earthdata (https://urs.earthdata.nasa.gov) — todo el equipo, **antes** del hackathon.

## Satélite vs. mediciones en campo
- El satélite da cobertura amplia y larga historia, pero **promedia** en píxeles grandes y puede fallar con nubes.
- La medición en campo es precisa y local, pero puntual y escasa.
- Lo ideal: usar satélite para patrones y **calibrar/validar con datos del agricultor** (pluviómetro, calicatas, rendimientos históricos).

## Armonización a una grilla común
1. Elegir una **grilla de análisis** (p. ej., 1 km o el polígono de la finca).
2. **Remuestrear**: agregar lo fino (promedio de Landsat → 1 km) y *no* inventar detalle donde no hay (SMAP a 9 km se declara como 9 km).
3. Alinear en tiempo: **mensual** o **decadal** suele ser el denominador común.
4. Guardar metadatos: fuente, versión, fecha de descarga, resolución original.
