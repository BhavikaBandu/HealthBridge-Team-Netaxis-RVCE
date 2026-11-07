from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={'connect_timeout': 5})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# The schema is managed by Alembic migrations (see migrations/). Run: python -m alembic upgrade head
