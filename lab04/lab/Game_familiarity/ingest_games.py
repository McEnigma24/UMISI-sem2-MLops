#!/usr/bin/env python3
"""Load Steam games from Hugging Face, embed descriptions, insert into Postgres.

Run from lab04 root:
  uv run python lab/Game_familiarity/ingest_games.py --limit 500

Requires vectorscale_db: cd lab/vectorscale_db && docker compose up -d
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from datasets import load_dataset
from sqlalchemy.orm import Session
from tqdm import tqdm

_PACKAGE_DIR = Path(__file__).resolve().parent
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))

from config import get_engine  # noqa: E402
from embeddings import generate_embeddings  # noqa: E402
from models import Base, Games  # noqa: E402

COLUMNS_TO_KEEP = [
    "name",
    "windows",
    "linux",
    "mac",
    "detailed_description",
    "supported_languages",
    "price",
]


def load_steam_subset(limit: int):
    dataset = load_dataset("FronkonGames/steam-games-dataset")
    train = dataset["train"].select_columns(COLUMNS_TO_KEEP)
    return train.select(range(min(limit, len(train))))


def insert_games(engine, dataset) -> int:
    inserted = 0
    with tqdm(total=len(dataset)) as pbar:
        for game in dataset:
            game_description = game["detailed_description"] or ""
            name = game["name"]
            price = game["price"]
            if name and game_description and price is not None:
                game_embedding = generate_embeddings(game_description)
                row = Games(
                    name=name,
                    description=game_description,
                    windows=game["windows"],
                    linux=game["linux"],
                    mac=game["mac"],
                    price=price,
                    game_description_embedding=game_embedding,
                )
                with Session(engine) as session:
                    session.add(row)
                    session.commit()
                inserted += 1
            pbar.update(1)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Steam games with embeddings")
    parser.add_argument(
        "--limit",
        type=int,
        default=40000,
        help="Max rows from HF train split (default: 40000)",
    )
    args = parser.parse_args()

    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    print(f"Loading up to {args.limit} games from Hugging Face...")
    dataset = load_steam_subset(args.limit)
    print(f"Dataset size: {len(dataset)}")

    count = insert_games(engine, dataset)
    print(f"Inserted {count} games into table 'games'")


if __name__ == "__main__":
    main()