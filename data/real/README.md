# Contrato de datos reales (soltar archivos aquí)

Si un archivo existe, la app lo usa **en lugar del sintético** y lo marca como real en pantalla.

| Archivo | Columnas | Cómo generarlo |
|---|---|---|
| `power_daily.csv` | índice fecha + `T2M,T2M_MIN,T2M_MAX,PRECTOTCORR,ALLSKY_SFC_SW_DWN` | `fetch_power(lat,lon).to_csv("data/real/power_daily.csv")` |
| `ndvi_monthly.csv` | `date,ndvi` (MODIS MOD13/Landsat, promedio mensual del lote) | AppEEARS o earthaccess |
| `smap_monthly.csv` | `date,sm` (humedad del suelo, m³/m³) | AppEEARS o earthaccess |
| `slope.csv` | `slope_pct` (pendiente media del lote, SRTM) | OpenTopography / AppEEARS |

Los archivos de esta carpeta se ignoran en git si se agregan a `.gitignore` (datos pesados).
