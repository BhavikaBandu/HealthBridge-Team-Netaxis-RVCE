# HealthBridge — Application

This folder contains the HealthBridge application: patient and doctor portals, the knowledge base and its retrieval,
five AI agents, the Dopamine–Cortisol controller and the LangGraph pipeline. For what HealthBridge is and why, see the
[main README](../README.md).

> Research prototype. It does not diagnose, prescribe, approve medicine substitutions or grant permission to carry
> medicines. Use synthetic data only.

---

## 1. Prerequisites

| Requirement | Notes |
|---|---|
| **Python 3.11** | `py -3.11 --version` (Windows) or `python3.11 --version` |
| **PostgreSQL 16 or 17** | Running locally on port 5432, with pgAdmin or `psql`. pgvector is **not** needed. |
| **Ollama** | https://ollama.com — runs the local language model |
| **Git** | To clone the repository |
| **Disk / memory** | About 20 GB free (≈18 GB language model + ≈240 MB embedding model). 32 GB RAM, or a GPU with 24 GB, recommended. |

## 2. Get the code

```bash
git clone <repository-url> healthbridge
cd healthbridge/app
```

All commands below are run from the `app/` folder.

## 3. Bring in the source data

The knowledge base is built from the official source files in `source-data/` (next to `app/`). The application reads
them from the folder set by `RAW_DATA_DIR` in `.env` (default `../source-data`).

- **Cloned with the repository:** nothing to do.
- **Downloaded separately:** unzip it next to `app/` so the layout is `healthbridge/app` and `healthbridge/source-data`,
  or put it anywhere and set `RAW_DATA_DIR` to that folder.

Expected layout:

```
source-data/
├── manifests/          source catalogue
├── medicines/          MED01, MED02, MED07, MED08, Swiss AIPS
├── medical_reports/    LAB01, LAB02, LAB03, UCUM
├── procedures/         PROC04, PROC05-K, PROC05-R
└── policies/           AE11, AE12, AE26, AE27, AE28, AE33
```

## 4. Create the database

Open pgAdmin's Query Tool or `psql` as the PostgreSQL administrator and run:

```sql
CREATE USER healthcare WITH PASSWORD 'healthcare';
CREATE DATABASE healthcare OWNER healthcare;
```

These are local development credentials. If you choose others, change `DATABASE_URL` in `.env` (step 6).

## 5. Create the Python environment and install packages

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

`requirements-semantic.txt` adds fastembed and NumPy for similar-meaning search.

## 6. Configure

```powershell
Copy-Item .env.example .env        # macOS / Linux: cp .env.example .env
```

| Setting | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare` | Database from step 4 |
| `RAW_DATA_DIR` | `../source-data` | Folder with the official source files (step 3) |
| `LLM_PROVIDER` | `ollama` | Local model through Ollama (`mock` = template wording, no AI) |
| `LLM_MODEL` | `qwen3:30b-a3b` | Ollama model name |
| `LLM_TIMEOUT_SECONDS` | `300` | Time allowed per AI call |
| `UPLOAD_DIR` | `data/private_uploads` | Where patient documents are stored (never committed) |
| `COOKIE_SECURE` | `false` | Set `true` when served over HTTPS |

Never commit `.env`. To check the whole setup at any point:

```powershell
python -m backend.check_env
```

## 7. Build the database and knowledge base

Run these once, in this order (virtual environment active):

```powershell
python -m alembic upgrade head              # 1. create all tables
python -m backend.ingestion.pipeline        # 2. ingest the official sources
python -m backend.retrieval.embeddings      # 3. build the search embeddings
```

1. **Tables:** Alembic applies the migrations in `migrations/versions/`.
2. **Ingestion:** reads every source in `source-data/`, stores a hashed copy in `data/processed/snapshots/`, and creates
   about 31,000 searchable records and the structured fact tables (medicine products and ingredients, lab references,
   procedure terms, policy clauses, controlled substances). Re-running is safe: unchanged files are skipped.
3. **Embeddings:** downloads the multilingual embedding model on first run into `data/processed/models/` and computes a
   384-dimension vector for every record. Only missing vectors are computed. This can take several minutes on a CPU.

## 8. Set up the local AI model

Install Ollama, make sure it is running (it serves on `http://localhost:11434`), then download the model once:

```bash
ollama pull qwen3:30b-a3b
```

If Ollama is not running, HealthBridge still works: the agents fall back to template wording written by code.

## 9. Run

```powershell
python -m uvicorn backend.main:app --reload
```

| Address | Page |
|---|---|
| http://127.0.0.1:8000 | Sign in / sign up (Patient or Doctor) |
| http://127.0.0.1:8000/travel-summary | Patient Travel Health Summary |
| http://127.0.0.1:8000/doctor/patients | Doctor Patient Records |
| http://127.0.0.1:8000/doctor/knowledge | Knowledge Explorer (doctors) |
| http://127.0.0.1:8000/docs | API documentation |

## 10. First use

The database starts with no users. To try the full flow:

1. **Sign up a patient** at `/signup`. The patient gets a Patient ID (for example `HC-XXXXXXXX`).
2. **Sign up a doctor** with "Doctor" sign-up. Doctor accounts start as *awaiting verification*: they can sign in and
   use the Knowledge Explorer, but patient features stay locked until approval.
3. **Approve the doctor** from the command line (there is no admin page):

   ```powershell
   python -m backend.portal.doctors list
   python -m backend.portal.doctors approve doctor@example.com
   ```

4. **As the doctor**, open Patient Records and invite the patient by Patient ID.
5. **As the patient**, accept the invitation under Doctor Access, add medicines, procedures, allergies and documents,
   then add a trip (for example India → United Arab Emirates).
6. Adding a trip runs the analysis in the background (about a minute). Open **Travel Health Summary**, choose the trip
   and generate a report in English or Arabic. The doctor sees the finding cards under each record and the Flags page.

After editing medical history, the patient is offered **Reprocess now**; only the changed parts are re-run.

## 11. Useful commands

| Command | Purpose |
|---|---|
| `python -m backend.ai.analysis --patient <PATIENT_ID>` | Re-run the changed parts of the patient's next trip |
| `python -m backend.ai.analysis --patient <PATIENT_ID> --full` | Re-run every agent for that trip |
| `python -m backend.portal.doctors list` / `approve <email>` / `reject <email>` | Review doctor accounts |
| `python -m backend.ai.snapshot save <name> --patient <PATIENT_ID>` | Save a named copy of a trip analysis |
| `python -m backend.ai.snapshot restore <name> --patient <PATIENT_ID>` | Restore a saved copy |
| `python -m backend.check_env` | Check Python packages, database and configuration |

## 12. Code structure

```
app/
├── backend/
│   ├── main.py            FastAPI application
│   ├── config.py          settings read from .env
│   ├── models.py          knowledge-base tables
│   ├── ai/                five agents, Dopamine–Cortisol controller, LangGraph pipeline, fingerprints,
│   │   │                  report builder and translation, analysis runner, snapshot tool
│   │   └── providers/     LLM providers (ollama.py)
│   ├── api/               knowledge search and evidence retrieval APIs
│   ├── ingestion/         source registry, parsers, terminology, ingestion pipeline
│   ├── portal/            portals: routes, page rendering, models, security, document extraction, doctor review tool
│   └── retrieval/         keyword and similar-meaning search, embeddings, per-domain evidence retrievers
├── frontend/
│   ├── templates/         Jinja2 pages for both portals and the printable report
│   └── static/            CSS and JavaScript
├── migrations/            Alembic database migrations
└── data/                  created at runtime, never committed
    ├── processed/         source snapshots and the embedding model
    └── private_uploads/   patient documents
```

## 13. Adding a new source

1. Put the file in `source-data/<domain>/<SOURCE_ID>/` with a `metadata.json` describing where it came from.
2. Register it in `backend/ingestion/registry.py` (source ID, domain, country, publisher, parser, licence note).
3. Re-run ingestion and then embeddings:

   ```powershell
   python -m backend.ingestion.pipeline
   python -m backend.retrieval.embeddings
   ```

Unchanged sources are skipped; a changed file becomes a new version and the old one is kept.

## 14. Configuration notes

- **Different language model:** set `LLM_MODEL` to any Ollama model you have pulled (larger Qwen3 models give better
  wording and Arabic). `OLLAMA_URL` and `OLLAMA_NUM_CTX` change the server address and context size.
- **No AI:** `LLM_PROVIDER=mock` skips the language model; every agent uses template wording written by code.
- **Another provider:** add a module in `backend/ai/providers/` exposing
  `generate(system_prompt, payload, schema, model, timeout)` and set `LLM_PROVIDER` to its name.
- **Embedding model:** `EMBEDDING_MODEL` changes the model; rebuild embeddings afterwards.

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| Pages return 503 "Database schema missing" | Run `python -m alembic upgrade head` |
| Cannot connect to the database | Start the PostgreSQL service and check `DATABASE_URL` in `.env` |
| Ingestion cannot find source files | Check that `source-data/` is next to `app/`, or set `RAW_DATA_DIR` |
| Knowledge Explorer finds no "similar meaning" results | Install `requirements-semantic.txt` and run `python -m backend.retrieval.embeddings` |
| Summaries use plain template wording | Start Ollama and run `ollama pull qwen3:30b-a3b`; then press Refresh summary |
| Doctor sees "awaiting verification" and cannot invite patients | Approve the account with `python -m backend.portal.doctors approve <email>` |
