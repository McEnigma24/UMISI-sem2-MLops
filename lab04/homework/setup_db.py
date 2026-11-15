#!/usr/bin/env python3
"""Database setup: URL, engine, Img table (homework § Database setup)."""

from db import build_db_url, get_engine
from models import Base, Img


def main() -> None:
    url = build_db_url()
    print(f"Connecting to {url.host}:{url.port}/{url.database} as {url.username}")
    engine = get_engine()
    Img.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(engine, tables=[Img.__table__])
    print(f"Table '{Img.__tablename__}' created (vector dim={Img.VECTOR_LENGTH}).")


if __name__ == "__main__":
    main()