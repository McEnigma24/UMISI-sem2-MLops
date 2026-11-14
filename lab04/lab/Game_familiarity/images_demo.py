#!/usr/bin/env python3
"""Smoke test: random image embeddings, top-k and similarity filtering.

Run from lab04 root: uv run python lab/Game_familiarity/images_demo.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

_PACKAGE_DIR = Path(__file__).resolve().parent
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))

from config import get_engine  # noqa: E402
from models import Base, Images  # noqa: E402


def insert_image(engine: Engine, image_path: str, image_embedding: list[float]) -> None:
    with Session(engine) as session:
        image = Images(image_path=image_path, image_embedding=image_embedding)
        session.add(image)
        session.commit()


def find_k_images(engine: Engine, k: int, original_image: Images) -> list[Images]:
    with Session(engine) as session:
        result = session.execute(
            select(Images)
            .order_by(Images.image_embedding.cosine_distance(original_image.image_embedding))
            .limit(k),
            execution_options={"prebuffer_rows": True},
        ).scalars().all()
        return result


def find_images_with_similarity_score_greater_than(
    engine: Engine, similarity_score: float, original_image: Images
) -> list[Images]:
    with Session(engine) as session:
        result = session.execute(
            select(Images).filter(
                (1 - Images.image_embedding.cosine_distance(original_image.image_embedding))
                > similarity_score
            ),
            execution_options={"prebuffer_rows": True},
        ).scalars().all()
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Images table vector search demo")
    parser.add_argument("--n", type=int, default=100, help="Number of random images to insert")
    parser.add_argument("--k", type=int, default=10, help="Top-k similar images")
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.5,
        help="Min similarity (1 - cosine_distance) for filtering demo",
    )
    args = parser.parse_args()

    engine = get_engine()
    Base.metadata.create_all(engine)

    for i in range(args.n):
        insert_image(engine, f"image_{i}.jpg", np.random.rand(Images.VECTOR_LENGTH).tolist())

    with Session(engine) as session:
        image = session.scalars(select(Images).limit(1)).first()

    if image is None:
        raise RuntimeError("No images in table after insert")

    similar_images = find_k_images(engine, args.k, image)
    print(f"Top {args.k} similar to {image.image_path}:")
    for row in similar_images:
        print(f"  {row.id}: {row.image_path}")

    filtered = find_images_with_similarity_score_greater_than(
        engine, args.similarity_threshold, image
    )
    print(f"Images with similarity > {args.similarity_threshold}: {len(filtered)}")


if __name__ == "__main__":
    main()