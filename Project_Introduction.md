# HealthBridge: A Multi-Agent Framework with Neuro-Inspired Evidence Scoring for Cross-Border Healthcare (هيلث بريدج: إطار متعدد الوكلاء لتقييم الأدلة بنظام نقاط مستوحى من آليات الجهاز العصبي في الرعاية الصحية العابرة للحدود)

<p align="center"><code>AI for Good Sandbox Hackathon</code></p>

> ⚠️ بيانات محاكاة لأغراض الهاكاثون فقط — every patient record in this repository is synthetic. No real or realistic patient data exists here.

<div align="justify">

**Your medical history shouldn't get lost in translation.**

Healthcare changes across borders, but patient records don't adapt with it. Medicines have different names, lab results
use different units, procedures follow different terminology, and medical regulations vary by country. This leaves
patients unprepared and doctors navigating unfamiliar records.

</div>

**Demo video:** [watch on Google Drive](https://drive.google.com/drive/folders/1fHM1TJb_3J6om1189Yb6z32ErhwMCkEG?usp=sharing) (see [`demo/`](demo/README.md))

## The Solution

<div align="justify">

**HealthBridge is a privacy-first, multi-agent AI platform that makes medical information understandable, accessible,
and actionable across borders.**

Built for cross-border healthcare, it bridges the gap between patients, doctors, and destination-specific medical
regulations.

- **Unified Patient Portal** — Manage medical history, medications, allergies, documents, travel plans, and doctor access.
- **AI-Powered Health Intelligence** — Map equivalent medications, standardize lab units, interpret procedures, and
  identify destination-specific regulatory requirements.
- **Doctor Decision Support** — Deliver source-backed findings, confidence assessments, regulatory alerts, and
  searchable medical knowledge.
- **Bilingual Reports** — Generate structured, printable health summaries in English or Arabic.
- **Privacy by Design** — Run AI locally using open-source models, with patient-controlled permissions and auditable
  access.

</div>

## Agents

| AI agent | RAG architecture | Main purpose |
|---|---|---|
| 1. Medicine Agent | Hybrid RAG + structured SQL retrieval | Match medicines across countries using active ingredients, strength, formulation, brand names and regulatory product information. |
| 2. Procedure Agent | Medical terminology-aware hybrid RAG | Map procedures between countries using medical terminology, synonyms, anatomical details, modality and clinical context. |
| 3. Medical Reports Agent | Clinical document RAG + deterministic normalisation | Interpret report terminology, extract findings and standardise laboratory units without changing the original clinical meaning. |
| 4. Policy & Jurisdiction Agent | Hierarchical, jurisdiction-aware legal RAG | Retrieve applicable healthcare regulations using country, authority, document hierarchy, effective dates and legal provisions. |
| 5. Translation Agent | LLM localisation with a fixed glossary and number-preservation checks | Translate patient and doctor reports into Arabic, right-to-left, without changing any value, strength or warning. |

## Team details

| Name | Email |
|---|---|
| Dr. K. A. Nethravathi | nethravathika@rvce.edu.in |
| Jaya Sri Jawahar Sripathy | jayasrijs.ec23@rvce.edu.in |
| Bhavika Bandu | bhavikabandu.cs23@rvce.edu.in |
| Shriyam Adya Sharma | shriyamadyas.cs23@rvce.edu.in |

## Repository layout

```
healthbridge/
├── app/            the application: code, database migrations and setup instructions
├── demo/           demo videos (link to the Google Drive folder)
└── knowledge-base/ the official source files the knowledge base is built from, with licence notes
```

## Technology

<div align="justify">

Python 3.11 · FastAPI · PostgreSQL 17 · SQLAlchemy and Alembic · LangGraph · Ollama with Qwen3 ·
fastembed multilingual embeddings · Jinja2, Bootstrap 5 and JavaScript

</div>

## Data and licences

<div align="justify">

- **Code:** the files in `app/` are the project's own work.
- **Source data:** the files in `knowledge-base/` come from regulators, reference laboratories, hospitals and
  manufacturers and keep their original terms. See `knowledge-base/README.md` before reusing or redistributing them.

</div>

## Disclaimer

<div align="justify">

HealthBridge is a research prototype. It does not diagnose, prescribe, approve medicine substitutions or grant
permission to carry medicines. Its output is information for a patient and a clinician to review. Use synthetic data
only for testing purposed.

</div>
