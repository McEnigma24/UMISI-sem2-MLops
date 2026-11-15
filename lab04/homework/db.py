import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL


def build_db_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "password"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5555")),
        database=os.environ.get("POSTGRES_DB", "similarity_search_service_db"),
    )


def get_engine() -> Engine:
    return create_engine(build_db_url())