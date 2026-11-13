# Arquitectura propuesta

```
 Datos NASA ──► Descarga/Cache ──► Armonización ──► Indicadores ──► Motor de rotaciones ──► UI
 (POWER, SMAP,    (data/cache)    (grilla+tiempo)  (lluvia, heladas,   (puntaje explicable    (app/mapa/
  GPM, MODIS…)                                       sequía, NDVI…)      + incertidumbre)       escenarios)
        ▲                                                  ▲                    ▲
        └── Suelo local / mediciones del agricultor ───────┘     Prioridades del agricultor ─┘
```

## Módulos del prototipo
- `power.py` – descarga NASA POWER (y generador sintético para trabajar sin internet).
- `features.py` – indicadores anuales: lluvia total, lluvia en año seco (P10), días de helada, días de calor, GDD, racha seca máxima.
- `scoring.py` – puntaje por criterio (agua, N, erosión, materia orgánica, plagas, mercado, clima) con pesos del agricultor.
- `demo.py` – CLI que compara rotaciones y imprime evidencia, vacíos y riesgos.

## Enfoques de modelado (para comparar en el hackathon)
| Enfoque | Pros | Contras |
|---|---|---|
| Reglas + puntaje ponderado (base) | Explicable, rápido, sin datos de rendimiento | Subjetivo; pesos a validar |
| Estadístico (anomalías, percentiles, tendencias) | Cuantifica variabilidad | Requiere series largas |
| ML (clustering de años/zonas, árboles) | Descubre patrones (años tipo "seco-caliente") | Necesita más datos; menos explicable |

**Recomendación:** base de reglas + estadística descriptiva; ML solo para segmentar tipos de año o zonas, siempre con explicación.

## Extensiones de alto impacto
1. Calendario de **suelo desnudo** (NDVI mensual de MODIS bajo umbral).
2. **Deslizadores de escenario** (lluvia −20 %, +2 °C) que recalculan puntajes.
3. Mapa de **vulnerabilidad** (pendiente SRTM + lluvia intensa GPM → erosión; Tmin → heladas).
4. Panel "**qué validar localmente**" por cada recomendación.
