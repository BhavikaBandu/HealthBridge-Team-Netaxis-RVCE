"""Record who entered each medical-history record (patient or doctor).

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-05
"""
import sqlalchemy as sa
from alembic import op

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

TABLES = ('medications', 'conditions', 'procedures', 'allergies')


def upgrade():
    for t in TABLES:
        op.add_column(t, sa.Column('reported_by_role', sa.String(20), nullable=False, server_default='patient'))
        op.add_column(t, sa.Column('reported_by_user_id', sa.Uuid(), nullable=True))
        op.create_foreign_key(f'fk_{t}_reported_by_user', t, 'users', ['reported_by_user_id'], ['id'], ondelete='SET NULL')
        # Everything entered so far came from the patient portal.
        op.execute(f'UPDATE {t} SET reported_by_user_id = patient_id WHERE reported_by_user_id IS NULL')


def downgrade():
    for t in TABLES:
        op.drop_constraint(f'fk_{t}_reported_by_user', t, type_='foreignkey')
        op.drop_column(t, 'reported_by_user_id')
        op.drop_column(t, 'reported_by_role')
