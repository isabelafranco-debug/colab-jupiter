> **Nota:** el modelo ahora usa rotaciones por años con doble campaña y cultivos de Santa Cruz; ver `09-bolivia-santa-cruz.md`. Las referencias a heladas y cultivos de ejemplo de esta guía son del diseño anterior.

# Guía MVP: de "nos entregan los datos" a una solución bien hecha

Este repo ya contiene un **MVP de referencia que funciona de punta a punta con datos sintéticos**. El día del hackathon NO se empieza de cero: se **reemplazan las capas sintéticas por datos reales** y se mejora lo que más puntúa.

## 1. Qué es el MVP (y qué no)
**Historia de usuario:** *"Soy agricultor. Indico dónde estoy, qué siembro hoy y qué me importa (agua, ingreso, suelo). La herramienta me muestra al menos 3 rotaciones —incluida la mía—, por qué las sugiere, con qué evidencia, qué no sabe y qué debo validar con un experto."*

| Dentro del MVP | Fuera (v2) |
|---|---|
| Clima NASA POWER real + NDVI y humedad como contexto | Mapa interactivo por píxel |
| Calendario de cultivos → suelo desnudo y vulnerabilidad por temporada | Modelos de rendimiento |
| 3+ rotaciones con puntaje explicable (8 criterios) | Predicción climática futura |
| Prioridades, textura, pendiente, exclusiones, escenarios lluvia/temperatura | Multi-parcela / multiusuario |
| Rango de incertidumbre (bootstrap) + estabilidad del ranking | Integración con mercados en vivo |
| Informe descargable con evidencia, vacíos y riesgos | App móvil |

## 2. Mapa del código (qué tocar y por qué)
| Archivo | Rol | Cuándo lo tocas |
|---|---|---|
| `data_layer.py` | Carga datos reales si existen en `data/real/`; si no, sintético. Informa la **procedencia** | Al recibir datos |
| `features.py` | Tablas año×mes y clima resumido | Para añadir indicadores (lluvia extrema GPM, sequía) |
| `scoring.py` | Puntaje, vulnerabilidad, incertidumbre, sensibilidad | Para calibrar criterios y pesos con expertos |
| `data/crops.csv` | Parámetros y calendario de cultivos | **Primero**: reemplazar con fuentes locales |
| `data/rotations.json` | Rotaciones candidatas | Ajustar a la región |
| `app/streamlit_app.py` | UI en 4 pestañas | Lenguaje, diseño, mapa |

## 3. Procedimiento cuando entreguen datos y referencias (≈ 6 h para integrar)
1. **(30 min) Inventario.** Por cada fuente: variable, resolución, periodo, formato, huecos. Anótalo en `docs/01-datasets-nasa.md`.
2. **(30 min) Elegir la región piloto** (1 zona pequeña, bien explicada) y el polígono/punto del lote.
3. **(90 min) Datos a `data/real/`** siguiendo `data/real/README.md` (mismo formato = la app los toma sola). Ver en pantalla que la procedencia cambie de "SINTÉTICO" a "archivo local".
4. **(90 min) Cultivos y suelo locales.** Con la referencia del reto/expertos: ajustar `crops.csv` (calendario, agua, heladas) y citar la fuente en una columna.
5. **(60 min) Promover un dato a "evidencia".** Elegir la mejora de mayor valor, p. ej.: meter NDVI al puntaje de cobertura (`cover` = meses con NDVI > 0.25 en vez de calendario), o humedad SMAP al criterio `water`.
6. **(60 min) Validar.** Un resultado que contradiga el sentido común agronómico = bug o parámetro mal puesto. Revisar con alguien del dominio.

## 4. Si algo falla (plan B)
| Problema | Respuesta |
|---|---|
| API/descarga lenta o caída | Cachear en `data/real/` ANTES; la app ya cae a sintético y lo avisa |
| Un dataset llega con resolución gruesa | Declararlo en vacíos de información; no inventar detalle |
| Series cortas (<10 años) | La app ya advierte "confianza baja"; mostrar rangos |
| Sin datos de suelo | Usar textura/pendiente del agricultor y marcarlo como vacío |

## 5. Estándar de calidad ("bien hecho")
- **Honestidad:** cada capa muestra si es real o sintética; nunca presentar sintético como evidencia.
- **Explicabilidad:** todo puntaje se descompone en criterios y evidencia concreta.
- **Incertidumbre visible:** rangos P10–P90, probabilidad de ser la mejor, ranking estable/sensible.
- **Lenguaje de agricultor:** sin siglas sin explicar; probar con 2 personas no técnicas.
- **Humildad:** vacíos y riesgos siempre presentes; el agricultor decide.
- **Reproducible:** `pytest` en verde, README claro, datos con fuente y versión.

## 6. Guion de demo (3 min)
1. **(20 s) Problema:** un agricultor con monocultivo, sequías y heladas.
2. **(40 s) Datos:** "usamos NASA POWER + NDVI + SMAP + SRTM" (mostrar procedencia real).
3. **(60 s) Uso:** ingresar finca y prioridad "Ahorrar agua" → resumen → vulnerabilidad de su rotación actual → mover el deslizador de lluvia −20 %.
4. **(40 s) Confianza:** rango, vacíos, riesgos; "qué debe validar un agrónomo".
5. **(20 s) Impacto y siguiente paso:** piloto con cooperativas, más regiones, mapa por lote.

## 7. Preparación del equipo AHORA (antes del hackathon)
- [ ] Todos con cuenta NASA Earthdata y el repo corriendo (`pytest`, `streamlit run`).
- [ ] Probar `fetch_power` con 2 ubicaciones y guardar en `data/real/`.
- [ ] Hacer **una** descarga de NDVI (AppEEARS) y una de SMAP, aunque sea para un punto.
- [ ] Un integrante investiga cultivos/calendarios de la región y rellena `crops.csv` con fuentes.
- [ ] Ensayar el guion de demo una vez completo con cronómetro.
- [ ] Decidir roles (ver `06-plan-hackathon.md`) y quién da la demo.

## 8. Ideas para destacar (si sobra tiempo, en este orden)
1. NDVI real en el puntaje de cobertura y alerta de "suelo desnudo".
2. Lluvia extrema (GPM P95) → riesgo de erosión combinado con pendiente SRTM.
3. Mapa (folium) con zonas de helada/erosión del lote.
4. Calibración con datos del agricultor (pluviómetro, rendimientos).
5. Idioma local y modo "solo texto" para baja conectividad.
