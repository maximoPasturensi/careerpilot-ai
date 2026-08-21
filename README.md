# 🚀 CareerPilot AI

**Copiloto de búsqueda laboral impulsado por IA — de 45 minutos a segundos por postulación.**

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![Gemini API](https://img.shields.io/badge/Gemini_API-Google-4285F4?logo=google&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-Structured_Output-E92063?logo=pydantic&logoColor=white)
![CoderCup](https://img.shields.io/badge/CoderCup-2026-orange)

---

## 🎥 Demo en acción

<!-- TODO: reemplazar por el GIF real una vez grabado con ScreenToGif/Kap.
     Recomendado: 5-10s mostrando subir el CV + pegar la oferta + click en "Analizar"
     hasta que aparecen las métricas (score, tiempo, gaps). -->
![Análisis completo en segundos](assets/demo-analisis.gif)

> 💡 *Reemplazá este bloque por tu GIF: grabá la pantalla, guardalo en `assets/demo-analisis.gif` y el markdown de arriba ya lo va a mostrar automáticamente.*

---

## 📌 El problema

Adaptar un CV, redactar una carta de presentación personalizada y prepararse para una entrevista, para **cada** oferta laboral a la que uno postula, toma en promedio **~45 minutos**. Esto limita el volumen y la calidad de las postulaciones de cualquier persona en búsqueda activa de empleo.

## 💡 La solución

**CareerPilot AI** automatiza ese proceso completo con un pipeline de agentes de IA: subís tu CV y pegás el texto de una oferta laboral, y en segundos obtenés:

1. **Análisis de compatibilidad** (Matching Engine) — % de match y gaps de skills detectados
2. **CV adaptado** — bullets reescritos en formato STAR, alineados a la oferta
3. **Cover Letter** personalizada — con el tono adecuado a la empresa
4. **Kit de entrevista** — 5 preguntas probables con respuestas sugeridas

Todo con un principio no negociable: **el sistema nunca inventa experiencia que el candidato no tiene.**

---

## 🏗️ Arquitectura del pipeline

```
                    ┌─────────────────┐         ┌──────────────────────┐
                    │   CV (PDF/MD)   │         │  Oferta laboral (txt)│
                    └────────┬────────┘         └──────────┬───────────┘
                             │                              │
                    ┌────────▼────────┐         ┌──────────▼───────────┐
                    │   CV Parser     │         │    Job Extractor      │
                    │ (Gemini + JSON  │         │  (Gemini + JSON       │
                    │  estructurado)  │         │   estructurado)       │
                    └────────┬────────┘         └──────────┬───────────┘
                             │                              │
                             └──────────────┬───────────────┘
                                            │
                                 ┌──────────▼───────────┐
                                 │   Matching Engine     │
                                 │  Fuzzy Match + LLM-    │
                                 │  Judge (gap analysis)  │
                                 └──────────┬───────────┘
                                            │
                 ┌──────────────────────────┼──────────────────────────┐
                 │                          │                          │
        ┌────────▼────────┐      ┌──────────▼──────────┐    ┌──────────▼──────────┐
        │   CV Adapter     │      │  Cover Letter Gen.   │    │ Interview Kit Gen.   │
        │ (bullets STAR)   │      │  (carta 3 párrafos)  │    │ (5 preguntas + resp) │
        └──────────────────┘      └──────────────────────┘    └──────────────────────┘
                 │                          │                          │
                 └──────────────────────────┼──────────────────────────┘
                                            │
                                 ┌──────────▼───────────┐
                                 │   Streamlit Dashboard  │
                                 │  (4 tabs de resultado) │
                                 └───────────────────────┘
```

## 🤖 Los agentes

| Agente | Función | Input | Output estructurado |
|---|---|---|---|
| **CV Parser** | Extrae texto de PDF/MD y lo estructura en JSON | Texto crudo del CV | `CVProfile` (experiencia, educación, skills) |
| **Job Extractor** | Estructura la oferta laboral en JSON | Texto de la oferta | `JobDescription` (requisitos, seniority, etc.) |
| **Matching Engine** | Gap analysis híbrido: fuzzy match + LLM-judge para razonamiento semántico | `CVProfile` + `JobDescription` | `MatchResult` (score ponderado 70/30 hard/soft) |
| **CV Adapter** | Reescribe bullets en formato STAR, honestamente alineados a la oferta | `CVProfile` + `JobDescription` + `MatchResult` | `AdaptedCV` (antes/después por bullet) |
| **Cover Letter Generator** | Redacta carta de presentación con tono adaptado | ídem | `CoverLetter` (apertura/cuerpo/cierre) |
| **Interview Kit Generator** | Genera preguntas técnicas/comportamentales con respuestas sugeridas | ídem | `InterviewKit` (5 Q&A + nota de preparación) |

### Guardrails éticos (por diseño, no accidental)

Cada agente generativo tiene reglas explícitas en su system prompt para **nunca inventar experiencia, tecnologías o anécdotas que el candidato no tiene**. Si la oferta pide una skill que falta en el CV, el sistema lo reconoce honestamente (y muestra cómo el candidato podría cerrar esa brecha) en vez de fabricar una mentira convincente.

<!-- TODO: GIF corto (5-8s) mostrando el scroll por la tab "CV Adaptado" con el
     antes/después de un bullet, o la tab "Kit de Entrevista" con un expander
     abriéndose en la pregunta sobre un gap real (ej. Airflow). -->

---

## 📸 Capturas de pantalla

<!-- TODO: 3-4 screenshots estáticos como respaldo del GIF, por si GitHub no
     lo carga bien o el jurado lee el README en un lugar que no soporta GIFs.
     Sacá las capturas con la app ya deployada, no en local, para que se vea
     el link real de producción en la barra de direcciones. -->

<table>
  <tr>
    <td><img src="assets/screenshot-metricas.png" alt="Métricas del análisis" width="400"/></td>
    <td><img src="assets/screenshot-cv-adaptado.png" alt="CV Adaptado" width="400"/></td>
  </tr>
  <tr>
    <td><img src="assets/screenshot-cover-letter.png" alt="Cover Letter" width="400"/></td>
    <td><img src="assets/screenshot-kit-entrevista.png" alt="Kit de Entrevista" width="400"/></td>
  </tr>
</table>

---

## 🛠️ Stack técnico

- **Backend / Lógica:** Python 3.12
- **LLM:** Google Gemini API (`gemini-3.5-flash-lite`) con structured output nativo vía Pydantic
- **Validación de datos:** Pydantic v2 (schemas estrictos, `Literal` types para evitar alucinación de categorías)
- **Matching semántico:** Fuzzy matching (`rapidfuzz`) + LLM-as-judge para casos ambiguos
- **Extracción de PDF:** `pdfplumber`
- **UI / Dashboard:** Streamlit
- **Resiliencia:** Cache local (hash-based) + retry con backoff exponencial (`tenacity`) ante rate limits (429/503)

---

## ⚙️ Instalación y ejecución local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/careerpilot-ai.git
cd careerpilot-ai
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Creá un archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu-api-key-de-google-ai-studio
```

### 4. Correr la app
```bash
streamlit run app/main.py
```

La app se abre automáticamente en `http://localhost:8501`.

---

## 🧪 Tests

El proyecto incluye tests de integración para cada módulo del pipeline:

```bash
python -m tests.test_job_extractor      # Extracción de oferta laboral
python -m tests.test_match_engine       # Matching engine (fuzzy + LLM-judge)
python -m tests.test_full_pipeline      # Pipeline CV + Job + Match
python -m tests.test_cv_adapter         # Agente CV Adaptado
python -m tests.test_cover_letter       # Agente Cover Letter
python -m tests.test_interview_kit      # Agente Kit de Entrevista
python -m tests.test_pipeline           # Orquestador completo (los 6 pasos)
```

---

## 📁 Estructura del proyecto

```
careerpilot-ai/
├── app/
│   ├── main.py                      # Dashboard de Streamlit
│   ├── models.py                    # Schemas Pydantic (contratos de datos)
│   ├── config.py                    # Configuración centralizada (modelo LLM, logging)
│   ├── cache.py                     # Cache local hash-based
│   ├── retry_utils.py               # Retry con backoff exponencial
│   ├── cv_parser.py                 # Agente: extracción de CV
│   ├── job_extractor.py             # Agente: extracción de oferta laboral
│   ├── match_engine.py              # Agente: matching engine (gap analysis)
│   ├── cv_adapter.py                # Agente: CV adaptado (STAR)
│   ├── cover_letter_generator.py    # Agente: cover letter
│   ├── interview_kit_generator.py   # Agente: kit de entrevista
│   └── pipeline.py                  # Orquestador (run_full_pipeline)
├── tests/                           # Tests de integración por módulo
├── requirements.txt
├── .gitignore
├── DEPLOY.md                        # Guía de deploy a Streamlit Cloud
└── README.md
```

---

## 📊 Impacto medible

| Métrica | Proceso manual | CareerPilot AI |
|---|---|---|
| Tiempo por postulación | ~45 minutos | ~15-20 segundos |
| Reducción de tiempo | — | **~98-99%** |
| Consistencia del formato STAR | Depende del candidato | Garantizada por el agente |
| Riesgo de alucinar experiencia falsa | N/A (humano) | Mitigado por guardrails explícitos en prompt |

---

## 🏆 Proyecto desarrollado para CoderCup

Este proyecto fue construido como entrega para la competencia **CoderCup** de Coderhouse, bajo la consigna de construir una solución funcional de IA que resuelva un problema real.

#CoderCup
