# HealthBridge: A Multi-Agent Framework with Neuro-Inspired Evidence Scoring for Cross-Border Healthcare (هيلث بريدج: إطار متعدد الوكلاء لتقييم الأدلة بنظام نقاط مستوحى من آليات الجهاز العصبي في الرعاية الصحية العابرة للحدود)


## Overview

<div align="justify">

HealthBridge helps patients who travel abroad for treatment carry their medical history across borders. Patients keep
their records and documents in one place; for each trip, four retrieval-augmented (RAG) agents compare those records
with official sources of the destination country and explain what each medicine, procedure, lab value and travel rule
means there, citing the source for every statement. Doctors see the findings in their own portal, and patients get a
printable report in English or Arabic.

A neuro-signal-inspired Dopamine–Cortisol controller then decides how far each finding can be trusted. Like the two
signals in the brain, Dopamine ("go") rises with confirmed evidence and agreement between code and AI, while Cortisol
("caution") rises with missing details, risk and contradictions. Together they decide whether a finding is shown as
validated, shown with limitations or sent to a doctor for review.

</div>

## Problem statement

<div align="justify">

Medical information does not translate cleanly across borders: medicines have different brand names, labs use different
units, procedures are named differently, and rules on carrying medicines are spread across authorities that do not
always agree. Patients and destination doctors have no reliable, source-backed way to bridge these differences before
treatment.

</div>

## Project features

<div align="justify">

**Patient portal**
- Account with a public Patient ID.
- Medical history: medications (strength, form, dose, schedule), conditions, procedures, allergies and an allergy declaration.
- Documents: upload PDFs and images and link them to records; text and values are extracted automatically on upload.
- Trips: origin, destination, dates and purpose.
- Travel Health Summary for each trip, with refresh and a printable report in English or Arabic.
- Doctor Access: accept or decline invitations, revoke access at any time and see who viewed what.

**Doctor portal**
- Doctor sign-up with registration details; accounts start as "awaiting verification".
- Dashboard: assigned patients, pending invitations and upcoming arrivals.
- Patient Records: invite a patient by Patient ID and browse their medications, conditions, procedures, allergies and documents.
- Finding cards: origin vs destination comparison, allergy check, what to verify, sources and the Dopamine–Cortisol assessment.
- Flags: destination rules for the trip, with sources, and the complete patient report.
- Knowledge Explorer: search the official sources behind every finding, by keyword or similar meaning, with a link to each original document.

</div>

## Agents

| AI agent | RAG architecture | Main purpose |
|---|---|---|
| 1. Medicine Agent | Hybrid RAG + structured SQL retrieval | Match medicines across countries using active ingredients, strength, formulation, brand names and regulatory product information. |
| 2. Procedure Agent | Medical terminology-aware hybrid RAG | Map procedures between countries using medical terminology, synonyms, anatomical details, modality and clinical context. |
| 3. Medical Reports Agent | Clinical document RAG + deterministic normalisation | Interpret report terminology, extract findings and standardise laboratory units without changing the original clinical meaning. |
| 4. Policy & Jurisdiction Agent | Hierarchical, jurisdiction-aware legal RAG | Retrieve applicable healthcare regulations using country, authority, document hierarchy, effective dates and legal provisions. |
| 5. Translation Agent | LLM localisation with a fixed glossary and number-preservation checks | Translate patient and doctor reports into Arabic, right-to-left, without changing any value, strength or warning. |

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
