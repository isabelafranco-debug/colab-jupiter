# Adaptación a Bolivia (Santa Cruz)

## 1. Qué recursos de la lista sirven para Bolivia
| Uso | Recursos |
|---|---|
| **Núcleo (global)** | NASA POWER, SMAP, GPM/IMERG, MODIS/VIIRS, Landsat, SRTM |
| **Muy útiles** | Sentinel-2 (10–20 m, mejor para lotes), ERA5, FAO GAEZ (idoneidad de cultivos) |
| **Si da tiempo** | ECOSTRESS, GLDAS, GEDI |
| **No aplican (solo EE. UU.)** | WSS, SSURGO/STATSGO2, CDL, PRISM, NAIP, NLCD, NLDAS, CoCoRaHS, NWIS, NASS, AMS, OpenET, LANDFIRE |

> La NASA indica que no respalda fuentes no estadounidenses y que hay que cumplir los términos de uso de cada sitio. Documentar fuente y licencia de cada capa.

## 2. Qué cambió en el modelo
- **Doble campaña:** una rotación es una lista de **años**; cada año tiene hasta dos campañas (**verano** nov–abr, **invierno** may–sep). El calendario real de cada cultivo define cobertura y suelo desnudo.
- **Validación de calendario:** no se permiten dos cultivos superpuestos en el mismo año.
- **Clima de Santa Cruz:** el criterio de clima usa **calor (≥35 °C)**, **frentes fríos/surazos (mín. ≤10 °C)** y **rachas secas dentro de la campaña**, no heladas. Los umbrales están en `features.py` (`COLD_C`, `HEAT_C`, `HEAVY_MM`).
- **Erosión:** penaliza la **lluvia intensa (≥30 mm/día) que cae en meses con suelo descubierto**.
- **Riego:** un deslizador indica qué parte del faltante de agua se cubre con riego (la cosecha de invierno depende de humedad almacenada).
- **Ingreso:** dos campañas comerciales al año puntúan más en «Mercado» (tope 1.0).
- **Plagas:** el monocultivo continuo (p. ej., soya-soya) puntúa 0; suma por familias botánicas distintas.

## 3. Cultivos incluidos (`data/crops.csv`)
Verano: soya, maíz, sorgo, arroz, sésamo, mucuna (abono verde). Invierno: maíz de invierno, trigo, girasol, chía, garbanzo, nabo forrajero, crotalaria y avena (coberturas).

> ⚠️ **Todos los valores y calendarios son ILUSTRATIVOS** (conocimiento general, no una fuente oficial). Hay que validarlos antes de usarlos como evidencia.

## 4. Fuentes locales para validar y reemplazar (verificar disponibilidad)
- **Calendarios y manejo:** INIAF, CIAT (Santa Cruz), ANAPO (soya, girasol, trigo, chía), productores y técnicos de la zona.
- **Mercado:** ANAPO, CAO, IBCE.
- **Clima en tierra:** SENAMHI, para contrastar la lluvia estimada por satélite.
- **Suelos:** análisis de laboratorio del productor; SoilGrids como aproximación global (confirmar si el reto permite fuentes externas).

## 5. Preguntas para el técnico o productor (30 min)
1. ¿Qué rotaciones usa hoy y por qué? ¿Qué problemas ha visto (plagas, malezas, compactación, erosión)?
2. Fechas reales de siembra y cosecha por cultivo y campaña en su zona.
3. ¿Qué cultivos de invierno funcionan sin riego? ¿Cuáles necesitan riego?
4. ¿Qué coberturas o abonos verdes se usan y qué barreras hay (semilla, costo, maquinaria)?
5. ¿Qué mercados y precios hacen viable un cultivo nuevo (chía, sésamo, garbanzo)?
6. ¿Qué mediría para decidir mejor (humedad, lluvia, análisis de suelo)?

## 6. Zonas piloto
`ZONAS` en `service.py` trae puntos **aproximados** (Santa Cruz de la Sierra, Montero, San Julián, Cuatro Cañadas). Para el piloto, usa las coordenadas del lote concreto de un productor.
