# HealthBridge: A Multi-Agent Framework with Neuro-Inspired Evidence Scoring for Cross-Border Healthcare (هيلث بريدج: إطار متعدد الوكلاء لتقييم الأدلة بنظام نقاط مستوحى من آليات الجهاز العصبي في الرعاية الصحية العابرة للحدود)


## Overview

<div align="justify">

HealthBridge helps patients who travel abroad for treatment carry their medical history across borders. Patients keep
their records and documents in one place; for each trip, four retrieval-augmented (RAG) agents compare those records
with official sources of the destination country and explain what each medicine, procedure, lab value and travel rule
means there, citing the source for every statement. A Dopamine–Cortisol controller then scores every finding, balancing
the evidence for it (Dopamine) against gaps and risks (Cortisol), and decides whether it is shown as validated, shown
with limitations or sent to a doctor for review. Doctors see the findings in their own portal, and patients get a
printable report in English or Arabic.

</div>

## Problem statement

<div align="justify">

Medical information does not translate cleanly across borders: medicines have different brand names, labs use different
units, procedures are named differently, and rules on carrying medicines are spread across authorities that do not
always agree. Patients and destination doctors have no reliable, source-backed way to bridge these differences before
treatment.

</div>

## Agents

<div align="justify">

- **Medicine Agent (RAG + LLM):** matches each medicine to a destination product with the same ingredients and strength,
  and checks it against the patient's allergies.
- **Procedure Agent (RAG + LLM):** finds the destination service that matches each procedure (scan type, body area,
  protocol), even when it is named differently.
- **Report Agent (RAG + LLM):** reads uploaded documents and converts lab values into the units used at the destination.
- **Policy Agent (RAG + LLM):** checks the destination's rules for carrying each medicine (controlled status, documents,
  quantity limits) and picks the safer rule when sources disagree.
- **Translation Agent (LLM):** translates the patient and doctor reports into Arabic.

</div>

**Demo video:** [watch on Google Drive](https://drive.google.com/drive/folders/1fHM1TJb_3J6om1189Yb6z32ErhwMCkEG?usp=sharing) (see [`demo/`](demo/README.md))

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
└── source-data/    the official source files the knowledge base is built from, with licence notes
```

## Getting started

<div align="justify">

Full setup instructions are in **[`app/README.md`](app/README.md)**. In short:

</div>

<div align="justify">

1. Install Python 3.11, PostgreSQL and Ollama.
2. Create the database and install the Python packages.
3. Build the knowledge base from `source-data/` (migrations, ingestion, embeddings).
4. Download the local AI model and start the application.

</div>

## Technology

<div align="justify">

Python 3.11 · FastAPI · PostgreSQL 17 · SQLAlchemy and Alembic · LangGraph · Ollama with Qwen3 ·
fastembed multilingual embeddings · Jinja2, Bootstrap 5 and JavaScript

</div>

## Data and licences

<div align="justify">

- **Code:** the files in `app/` are the project's own work.
- **Source data:** the files in `source-data/` come from regulators, reference laboratories, hospitals and
  manufacturers and keep their original terms. See `source-data/README.md` before reusing or redistributing them.

</div>

## Disclaimer

<div align="justify">

HealthBridge is a research prototype. It does not diagnose, prescribe, approve medicine substitutions or grant
permission to carry medicines. Its output is information for a patient and a clinician to review. Use synthetic data
only for testing purposed.

</div>
