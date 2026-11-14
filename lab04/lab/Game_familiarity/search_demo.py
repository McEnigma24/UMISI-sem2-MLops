#!/usr/bin/env python3
"""Vector search over games with metadata filters (lab examples).

Run from lab04 root: uv run python lab/Game_familiarity/search_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

_PACKAGE_DIR = Path(__file__).resolve().parent
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))

from config import get_engine  # noqa: E402
from embeddings import generate_embeddings  # noqa: E402
from models import Games  # noqa: E402


def find_game(
    engine: Engine,
    game_description: str,
    windows: Optional[bool] = None,
    linux: Optional[bool] = None,
    mac: Optional[bool] = None,
    price: Optional[int] = None,
) -> Games | None:
    with Session(engine) as session:
        game_embedding = generate_embeddings(game_description)

        query = select(Games).order_by(
            Games.game_description_embedding.cosine_distance(game_embedding)
        )

        if price is not None:
            query = query.filter(Games.price <= price)
        if windows:
            query = query.filter(Games.windows == True)  # noqa: E712
        if linux:
            query = query.filter(Games.linux == True)  # noqa: E712
        if mac:
            query = query.filter(Games.mac == True)  # noqa: E712

        result = session.execute(query, execution_options={"prebuffer_rows": True})
        return result.scalars().first()


def print_game(game: Games | None) -> None:
    if game is None:
        print("No matching game found.")
        return
    desc = game.description
    if len(desc) > 300:
        desc = desc[:300] + "..."
    print(f"Game: {game.name}")
    print(f"Price: {game.price}")
    print(f"Description: {desc}")
    print()


def main() -> None:
    engine = get_engine()

    game = find_game(
        engine,
        "This is a game about a hero who saves the world",
        price=10,
    )
    print_game(game)

    game = find_game(engine, game_description="Home decorating", price=20)
    print_game(game)

    game = find_game(engine, game_description="Home decorating", mac=True, price=5)
    print_game(game)


if __name__ == "__main__":
    main()