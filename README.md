# 🌱 Rotación de cultivos con datos NASA — Repositorio de entrenamiento

Repositorio para **entrenar a nuestro equipo** antes del hackathon (NASA Space Apps) y arrancar con un prototipo funcional.

**El reto:** crear una herramienta de apoyo a la decisión que combine observaciones de la Tierra de la NASA, información local de suelo, características de cultivos y prioridades del agricultor, para explorar estrategias de rotación que fortalezcan la salud del suelo y la resiliencia al clima.

> ⚠️ La herramienta **apoya**, no reemplaza, el criterio del agricultor ni la experiencia agronómica local.

## Qué incluye
| Carpeta | Contenido |
|---|---|
| `docs/` | Guías: reto, datasets NASA, glosario, arquitectura, estrategias, incertidumbre, plan del hackathon |
| `exercises/` | Ejercicios por rol con criterios de "hecho" |
| `src/rotacion/` | Prototipo base: descarga NASA POWER, indicadores climáticos, puntaje de rotaciones |
| `app/` | App Streamlit de ejemplo (prioridades del agricultor + comparación de 3+ rotaciones) |
| `data/` | Catálogo de cultivos y rotaciones de ejemplo (**valores ilustrativos**, hay que reemplazarlos) |
| `tests/` | Pruebas para no romper el núcleo mientras se itera |

> 🧭 **¿Retomas el proyecto en un chat nuevo o con alguien del equipo?** Empieza por `docs/CONTEXTO.md`.

## 🎯 MVP de referencia (adaptado a Santa Cruz, Bolivia)
Funciona de punta a punta con datos sintéticos: doble campaña (verano/invierno), cultivos de la región, calor, frentes fríos y rachas secas, riego, suelo desnudo, vulnerabilidad por temporada, incertidumbre e informe descargable.
- **Guía MVP y datos reales:** `docs/08-guia-mvp.md`
- **Adaptación a Bolivia (cultivos, fuentes, preguntas al técnico):** `docs/09-bolivia-santa-cruz.md`
- **API para el frontend:** `docs/10-api-frontend.md`

## Inicio rápido
```bash
git clone <URL-DE-TU-REPO> && cd rotacion-nasa-entrenamiento
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                            # debe pasar
PYTHONPATH=src python -m rotacion.demo               # PowerShell: $env:PYTHONPATH="src"
PYTHONPATH=src python -m rotacion.demo --api         # con NASA POWER real
streamlit run app/streamlit_app.py                   # app
uvicorn api.main:app --reload                        # API (con PYTHONPATH=src)
```

## Ruta de entrenamiento (5 sesiones)
1. **Entender el problema** → `docs/00-reto.md`, `docs/02-glosario.md`
2. **Conocer los datos NASA** → `docs/01-datasets-nasa.md` + ejercicio 1
3. **Indicadores y armonización** → `docs/03-arquitectura.md` + ejercicios 2 y 3
4. **Puntaje de rotaciones e incertidumbre** → `docs/04-estrategias-rotacion.md`, `docs/05-incertidumbre.md` + ejercicio 4
5. **Simulacro de hackathon** → `docs/08-guia-mvp.md` + `docs/06-plan-hackathon.md` + `docs/07-checklist-entrega.md`

## Cómo trabajamos en equipo
- Rama por persona: `feat/<nombre>-<tema>`; Pull Request con 1 revisión.
- Todo dato nuevo se documenta en `docs/01-datasets-nasa.md` (fuente, resolución, limitaciones).
- Cada resultado de la herramienta debe mostrar **evidencia, vacíos de información y riesgos**.
