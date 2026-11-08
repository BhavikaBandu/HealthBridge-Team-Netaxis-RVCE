# HealthBridge: A Multi-Agent Framework with Neuro-Inspired Evidence Scoring for Cross-Border Healthcare (هيلث بريدج: إطار متعدد الوكلاء لتقييم الأدلة بنظام نقاط مستوحى من آليات الجهاز العصبي في الرعاية الصحية العابرة للحدود)


## The problem

<div align="justify">

Patients who travel abroad for treatment carry medical information that does not translate cleanly across borders.
The same medicine has different brand names in each country (Crocin Advance in India, Panadol Advance in the UAE).
Laboratories report results in different units (glucose in mg/dL in India, mmol/L in the UAE). Procedures are described
differently by each provider. Rules on carrying medicines, especially controlled ones such as tramadol, are spread
across several authorities that do not always agree. Destination doctors receive all of this late, in PDFs, and in an
unfamiliar format.

</div>

## What HealthBridge does

<div align="justify">

- **Patient portal:** patients keep their medicines, conditions, procedures, allergies and documents in one place,
  plan their trips and decide which doctors can see their records.
- **Travel Health Summary:** for every trip, AI agents compare the patient's records with official destination sources:
  which UAE product matches each medicine, what each procedure is called at the destination, lab values in UAE units,
  and which rules and documents apply. Every statement cites its source.
- **Doctor portal:** invited doctors see a finding card for each medicine, procedure and document, the destination
  flags, and a confidence assessment for every finding. The Knowledge Explorer lets them search the official sources
  directly.
- **Reports:** printable patient and doctor reports in English or Arabic.
- **Private by design:** the AI runs locally on an open-source model; patients control access and every view is logged.

</div>

<div align="justify">

**Demo videos:** [watch on Google Drive](https://drive.google.com/drive/folders/1fHM1TJb_3J6om1189Yb6z32ErhwMCkEG?usp=sharing) (see [`demo/`](demo/README.md))

</div>

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
