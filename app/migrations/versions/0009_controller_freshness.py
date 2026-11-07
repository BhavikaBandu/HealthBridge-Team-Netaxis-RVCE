"""controller assessment and freshness fingerprints

Revision ID: 0009
Revises: 0008
Create Date: 2026-11-07 15:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('analysis_findings', sa.Column('assessment', postgresql.JSONB(astext_type=sa.Text()),
                                                 nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.add_column('analysis_findings', sa.Column('fingerprint', sa.String(length=64), nullable=True))
    op.add_column('trip_analyses', sa.Column('base_fingerprint', sa.String(length=64), nullable=True))
    op.add_column('trip_analyses', sa.Column('policy_fingerprint', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('trip_analyses', 'policy_fingerprint')
    op.drop_column('trip_analyses', 'base_fingerprint')
    op.drop_column('analysis_findings', 'fingerprint')
    op.drop_column('analysis_findings', 'assessment')
