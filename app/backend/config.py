import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare')
APP_TITLE = os.getenv('APP_TITLE', 'Healthcare Knowledge Explorer')

# Immutable copies of every ingested raw file, keyed by SHA-256, so old versions survive raw-file updates.
SNAPSHOT_DIR = ROOT / os.getenv('SNAPSHOT_DIR', 'data/processed/snapshots')

# Local multilingual embedding model (downloaded once by fastembed; Apache-2.0).
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
EMBEDDING_CACHE_DIR = ROOT / os.getenv('EMBEDDING_CACHE_DIR', 'data/processed/models')

# Patient portal
UPLOAD_DIR = ROOT / os.getenv('UPLOAD_DIR', 'data/private_uploads')
MAX_UPLOAD_BYTES = int(float(os.getenv('MAX_UPLOAD_MB', '10')) * 1024 * 1024)
COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'false').lower() == 'true'
SESSION_HOURS = int(os.getenv('SESSION_HOURS', '12'))
REMEMBER_ME_DAYS = int(os.getenv('REMEMBER_ME_DAYS', '30'))

# Safety limits for archive extraction during ingestion.
MAX_UNCOMPRESSED_BYTES = int(os.getenv('MAX_UNCOMPRESSED_BYTES', str(500 * 1024 * 1024)))
MAX_COMPRESSION_RATIO = int(os.getenv('MAX_COMPRESSION_RATIO', '200'))
