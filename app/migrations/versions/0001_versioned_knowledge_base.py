"""Versioned knowledge base: sources, immutable source versions, records, embeddings, ingestion runs.

Revision ID: 0001
Revises:
Create Date: 2026-11-05
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

SEARCH_VECTOR_SQL = (
    "setweight(to_tsvector('simple', coalesce(title, '')), 'A') || "
    "setweight(to_tsvector('simple', coalesce(external_id, '')), 'A') || "
    "setweight(to_tsvector('simple', coalesce(content, '')), 'B')"
)


def upgrade():
    # pg_trgm ships with PostgreSQL and is a trusted extension (database owner can enable it).
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    op.create_table(
        'sources',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_id', sa.String(80), nullable=False, unique=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('workflow', sa.String(40), nullable=False, index=True),
        sa.Column('jurisdiction', sa.String(30), nullable=False),
        sa.Column('origin_url', sa.Text),
        sa.Column('licence_note', sa.Text),
        sa.Column('access_note', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('active_version_id', sa.Integer),
    )
    op.create_table(
        'source_versions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_pk', sa.Integer, sa.ForeignKey('sources.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('version_label', sa.String(80), nullable=False),
        sa.Column('sha256', sa.String(64), nullable=False),
        sa.Column('raw_path', sa.Text, nullable=False),
        sa.Column('snapshot_path', sa.Text),
        sa.Column('file_size', sa.BigInteger, nullable=False),
        sa.Column('parser_name', sa.String(80), nullable=False),
        sa.Column('parser_version', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('record_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('acquired_at', sa.DateTime(timezone=True)),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('source_pk', 'sha256', name='uq_version_source_sha'),
    )
    op.create_foreign_key('fk_sources_active_version', 'sources', 'source_versions',
                          ['active_version_id'], ['id'], ondelete='SET NULL')

    op.create_table(
        'knowledge_records',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('version_pk', sa.Integer, sa.ForeignKey('source_versions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('external_id', sa.String(250), nullable=False),
        sa.Column('kind', sa.String(40), nullable=False, index=True),
        sa.Column('workflow', sa.String(40), nullable=False, index=True),
        sa.Column('jurisdiction', sa.String(30), nullable=False),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('language', sa.String(15)),
        sa.Column('source_link', sa.Text),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('search_vector', postgresql.TSVECTOR, sa.Computed(SEARCH_VECTOR_SQL, persisted=True)),
        sa.UniqueConstraint('version_pk', 'external_id', name='uq_record_version_external'),
    )
    op.create_index('ix_records_search_vector', 'knowledge_records', ['search_vector'], postgresql_using='gin')
    # Trigram indexes make case-insensitive partial matching (ILIKE '%term%') index-assisted.
    op.execute('CREATE INDEX ix_records_title_trgm ON knowledge_records USING gin (title gin_trgm_ops)')
    op.execute('CREATE INDEX ix_records_content_trgm ON knowledge_records USING gin (content gin_trgm_ops)')
    # Exact identifier lookups (AIPS authorisation numbers, UCUM codes).
    op.execute("CREATE INDEX ix_records_meta_authorisation ON knowledge_records ((metadata->>'authorisation'))")
    op.execute("CREATE INDEX ix_records_meta_code ON knowledge_records ((metadata->>'code'))")
    op.execute('CREATE INDEX ix_records_external_id_lower ON knowledge_records (lower(external_id))')

    op.create_table(
        'record_embeddings',
        sa.Column('record_pk', sa.Integer, sa.ForeignKey('knowledge_records.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('model', sa.String(120), primary_key=True),
        sa.Column('dim', sa.Integer, nullable=False),
        sa.Column('vector', sa.LargeBinary, nullable=False),
    )

    op.create_table(
        'ingestion_runs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_id', sa.String(80), nullable=False, index=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('sha256', sa.String(64)),
        sa.Column('version_pk', sa.Integer, sa.ForeignKey('source_versions.id', ondelete='SET NULL')),
        sa.Column('records_loaded', sa.Integer, nullable=False, server_default='0'),
        sa.Column('records_skipped', sa.Integer, nullable=False, server_default='0'),
        sa.Column('message', sa.Text),
        sa.Column('errors', postgresql.JSONB, nullable=False, server_default='[]'),
    )


def downgrade():
    op.drop_table('ingestion_runs')
    op.drop_table('record_embeddings')
    op.drop_table('knowledge_records')
    op.drop_constraint('fk_sources_active_version', 'sources', type_='foreignkey')
    op.drop_table('source_versions')
    op.drop_table('sources')
