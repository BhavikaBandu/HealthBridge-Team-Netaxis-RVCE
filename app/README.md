# HealthBridge — Application

**Local-first, evidence-grounded cross-border healthcare intelligence.**

This directory contains the patient and doctor portals, official-source knowledge base, five AI agents, LangGraph orchestration, and the Dopamine–Cortisol confidence controller. For the project vision, see the [main README](../README.md).

> **Research prototype:** Not for diagnosis, prescribing, approving medicine substitutions, or authorizing travel with medicines. Use synthetic data only.

## Contents

- [Architecture & tech stack](#architecture--tech-stack)
- [Getting started](#getting-started)
- [Run the application](#run-the-application)
- [First-use walkthrough](#first-use-walkthrough)
- [Developer reference](#developer-reference)
- [Troubleshooting](#troubleshooting)

## Architecture & tech stack

**Workflow:** Patient records + destination → domain-specific evidence retrieval → specialized AI agents → Dopamine–Cortisol confidence assessment → doctor findings and bilingual reports.

| Layer | Implementation |
|---|---|
| Web application | FastAPI, Jinja2, CSS, JavaScript |
| Orchestration | LangGraph; five agents and confidence controller |
| Local LLM | Ollama (`qwen3:30b-a3b` by default); configurable provider |
| Knowledge retrieval | Official-source ingestion, keyword and semantic search, multilingual embeddings |
| Data | PostgreSQL 16/17, SQLAlchemy/psycopg, Alembic migrations |
| Reports | Printable English and Arabic reports |

<details>
<summary><strong>Project directory structure</strong></summary>

```text
app/
├── backend/
│   ├── main.py             FastAPI entry point
│   ├── config.py           Environment settings
│   ├── models.py           Knowledge-base models
│   ├── ai/                 Agents, LangGraph, controller, reporting, translation
│   │   └── providers/      LLM provider implementations
│   ├── api/                Search and evidence APIs
│   ├── ingestion/          Source registry, parsers, ingestion pipeline
│   ├── portal/             Portal routes, security, document handling
│   └── retrieval/          Domain retrievers, embeddings, search
├── frontend/
│   ├── templates/          Patient, doctor and report pages
│   └── static/             CSS and JavaScript
├── migrations/             Alembic migrations
└── data/                   Runtime files (not committed)
    ├── processed/          Snapshots and embedding model
    └── private_uploads/    Patient documents
```
</details>

## Getting started

### 1. Prerequisites

- **Python 3.11**, **Git**, **PostgreSQL 16 or 17** (local port `5432`), and [Ollama](https://ollama.com).
- Approximately **20 GB free disk space** (around 18 GB for the LLM and 240 MB for embeddings). **32 GB RAM or a 24 GB GPU** recommended.
- PostgreSQL **pgvector is not required**.

### 2. Clone and install

```bash
git clone <repository-url> healthbridge
cd healthbridge/app
```

**Windows (PowerShell):**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-semantic.txt
```

**macOS / Linux:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-semantic.txt
```

The semantic requirements install FastEmbed and NumPy for similarity search. All subsequent commands run from `app/` with the virtual environment active.

### 3. Add the official source files

Source files belong in `../source-data/raw/` relative to `app/`. If provided separately, extract them beside `app/` or configure `RAW_DATA_DIR` to point to the extracted `raw/` directory.

```text
source-data/
├── manifests/
└── raw/
    ├── medicines/          MED01, MED02, MED07, MED08, Swiss AIPS
    ├── medical_reports/    LAB01, LAB02, LAB03, UCUM
    ├── procedures/         PROC04, PROC05-K, PROC05-R
    └── policies/           AE11, AE12, AE26, AE27, AE28, AE33
```

### 4. Create the database

In pgAdmin Query Tool or `psql`, as PostgreSQL administrator:

```sql
CREATE USER healthcare WITH PASSWORD 'healthcare';
CREATE DATABASE healthcare OWNER healthcare;
```

These credentials are for **local development only**. Change them and update `DATABASE_URL` for other environments.

### 5. Configure environment

```bash
# Windows PowerShell
Copy-Item .env.example .env
# macOS / Linux: cp .env.example .env
```

| Variable | Default / purpose |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare` |
| `RAW_DATA_DIR` | `../source-data/raw` |
| `LLM_PROVIDER` | `ollama` |
| `LLM_MODEL` | `qwen3:30b-a3b` |
| `LLM_TIMEOUT_SECONDS` | `300` |
| `UPLOAD_DIR` | `data/private_uploads` |
| `COOKIE_SECURE` | `false`; set `true` when using HTTPS |

**Never commit `.env` or patient uploads.** Check configuration with:

```bash
python -m backend.check_env
```

## Run the application

### 1. Initialize tables and knowledge retrieval

Run these in order:

```bash
python -m alembic upgrade head
python -m backend.ingestion.pipeline
python -m backend.retrieval.embeddings
```

The ingestion step processes official sources into approximately **31,000 searchable records** and structured fact tables, retaining hashed source snapshots. Re-running skips unchanged files. Embeddings are **384-dimensional**; the multilingual embedding model downloads on first use, and only missing vectors are computed.

### 2. Start the local model

With Ollama installed and running at `http://localhost:11434`:

```bash
ollama pull qwen3:30b-a3b
```

If Ollama is unavailable, agents fall back to code-generated template wording.

### 3. Launch the server

```bash
python -m uvicorn backend.main:app --reload
```

| URL | Purpose |
|---|---|
| http://127.0.0.1:8000 | Patient / doctor sign-in and sign-up |
| http://127.0.0.1:8000/travel-summary | Patient Travel Health Summary |
| http://127.0.0.1:8000/doctor/patients | Doctor Patient Records |
| http://127.0.0.1:8000/doctor/knowledge | Doctor Knowledge Explorer |
| http://127.0.0.1:8000/docs | Interactive API documentation |

## First-use walkthrough

1. **Register a patient** at `/signup` and note the generated Patient ID (`HC-XXXXXXXX`).
2. **Register a doctor.** New doctor accounts await verification; the Knowledge Explorer is available before approval, but patient access is restricted.
3. **Approve the doctor** from the command line (no admin web page):

   ```bash
   python -m backend.portal.doctors list
   python -m backend.portal.doctors approve doctor@example.com
   ```

4. **Connect doctor and patient:** Doctor invites the patient using the Patient ID; patient accepts under **Doctor Access**.
5. **Add patient information:** Medicines, procedures, allergies, documents, and a trip (e.g., India → United Arab Emirates).
6. **Review results:** Adding a trip starts background analysis (roughly one minute). The patient opens **Travel Health Summary** and generates an English or Arabic report. The doctor reviews record-level finding cards and destination flags.

After changes to medical history, **Reprocess now** reruns only the affected analysis components.

## Developer reference

### Useful commands

| Command | Action |
|---|---|
| `python -m backend.check_env` | Verify dependencies, database, configuration |
| `python -m backend.ai.analysis --patient <PATIENT_ID>` | Reanalyze changed parts of next trip |
| `python -m backend.ai.analysis --patient <PATIENT_ID> --full` | Rerun all agents for next trip |
| `python -m backend.portal.doctors list` | List doctor accounts |
| `python -m backend.portal.doctors approve <email>` | Approve a doctor |
| `python -m backend.portal.doctors reject <email>` | Reject a doctor |
| `python -m backend.ai.snapshot save <name> --patient <PATIENT_ID>` | Save a trip-analysis snapshot |
| `python -m backend.ai.snapshot restore <name> --patient <PATIENT_ID>` | Restore a snapshot |

### Add a new official source

1. Place the file at `source-data/raw/<domain>/<SOURCE_ID>/` with a `metadata.json` describing its origin.
2. Register source ID, domain, country, publisher, parser, and licence note in `backend/ingestion/registry.py`.
3. Rebuild affected knowledge records and vectors:

   ```bash
   python -m backend.ingestion.pipeline
   python -m backend.retrieval.embeddings
   ```

Unchanged sources are skipped; modified files are versioned while older snapshots are retained.

### Change AI or embedding models

- **Switch Ollama model:** Pull another model and update `LLM_MODEL` in `.env`.
- **Switch LLM provider:** Add a provider under `backend/ai/providers/` implementing `generate(system_prompt, payload, schema, model, timeout)`; set `LLM_PROVIDER` to its name.
- **Tune Ollama:** Configure `OLLAMA_URL` and `OLLAMA_NUM_CTX`.
- **Change embedding model:** Set `EMBEDDING_MODEL`, then rebuild embeddings.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| `503 Database schema missing` | Run `python -m alembic upgrade head` |
| Cannot connect to PostgreSQL | Start the service and verify `DATABASE_URL` |
| Source files not found | Check `source-data/raw/` or `RAW_DATA_DIR` |
| No semantic search matches | Install `requirements-semantic.txt` and build embeddings |
| AI summaries use template wording | Start Ollama, pull the model, and refresh the summary |
| Doctor cannot invite patients | Approve the doctor via `backend.portal.doctors` CLI |

---

For the problem statement, solution, and project demos, return to the [HealthBridge main README](../README.md).
