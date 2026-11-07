from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from backend.config import DATABASE_URL
from backend.database import Base
from backend import models  # noqa: F401  (registers tables on Base.metadata)
from backend.portal import models as portal_models  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

# Indexes created with raw SQL in 0001 (trigram / expression indexes) are not in the models;
# keep autogenerate from proposing to drop them.
RAW_SQL_INDEXES = {'ix_records_title_trgm', 'ix_records_content_trgm', 'ix_records_meta_authorisation',
                   'ix_records_meta_code', 'ix_records_external_id_lower'}


def include_object(obj, name, type_, reflected, compare_to):
    return not (type_ == 'index' and name in RAW_SQL_INDEXES)


def run_migrations_offline():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_object=include_object)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
