# Ejercicios

## 1. Datos NASA (rol Datos) — 60 min
Descarga 10 años de NASA POWER para 2 lugares distintos con `fetch_power`. Compara lluvia anual y días de helada. **Hecho cuando:** hay una tabla comparativa y una nota sobre limitaciones.

## 2. Indicadores (rol Modelado) — 90 min
Añade a `features.py` un indicador nuevo (p. ej. lluvia por trimestre o precipitación extrema P95). **Hecho cuando:** tiene test en `tests/`.

## 3. Armonización (rol Datos) — 2 h
Con `earthaccess` o AppEEARS, descarga NDVI MODIS mensual para un punto. Calcula los meses con NDVI < 0.25 ("suelo desnudo probable") y cruza con lluvia. **Hecho cuando:** existe `bare_months(ndvi_series)` con test.

## 4. Puntaje e incertidumbre (rol Modelado) — 2 h
Implementa un análisis de sensibilidad: variar pesos ±20 % y reportar si cambia el ranking. **Hecho cuando:** la app muestra "ranking estable / sensible".

## 5. UX para agricultores (rol Frontend) — 90 min
Reescribe las tarjetas de resultados en lenguaje no técnico y añade un deslizador de escenario (lluvia −20 % … +20 %). **Hecho cuando:** 2 personas ajenas al proyecto entienden la pantalla sin ayuda.

## 6. Validación agronómica (rol Dominio) — 90 min
Reemplaza 5 cultivos de `data/crops.csv` con valores de fuentes locales y cita la fuente en una columna nueva.
