#!/usr/bin/env python3
"""CLIP embeddings for ABO images → Postgres (homework)."""

from __future__ import annotations

import argparse
import sys
from itertools import islice
from pathlib import Path

import joblib
from sqlalchemy.orm import Session
from tqdm import tqdm

from db import get_engine
from models import Base, Img

HOMEWORK_DIR = Path(__file__).resolve().parent
DEFAULT_PATHS = HOMEWORK_DIR / "data" / "abo" / "valid_image_paths.txt"


def batched(iterable, n: int):
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def create_img_table(engine, *, recreate: bool) -> None:
    if recreate:
        Img.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(engine, tables=[Img.__table__])


def load_image_paths(paths_file: Path, max_images: int | None) -> list[str]:
    lines = [ln.strip() for ln in paths_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if max_images is not None:
        lines = lines[:max_images]
    return lines


def insert_images(engine, images: list[Img]) -> None:
    with Session(engine) as session:
        session.add_all(images)
        session.commit()


def vectorize_images(
    engine,
    model,
    image_paths: list[str],
    batch_size: int,
) -> None:
    from PIL import Image

    with tqdm(total=len(image_paths)) as pbar:
        for paths_batch in batched(image_paths, batch_size):
            pil_images = [Image.open(p).convert("RGB") for p in paths_batch]
            embeddings = model.encode(pil_images, batch_size=len(paths_batch), convert_to_numpy=True)
            rows = [
                Img(image_path=path, embedding=emb.tolist())
                for path, emb in zip(paths_batch, embeddings)
            ]
            insert_images(engine, rows)
            pbar.update(len(paths_batch))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-file", type=Path, default=DEFAULT_PATHS)
    parser.add_argument("--max-images", type=int, default=500)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Default: physical CPU count",
    )
    parser.add_argument(
        "--recreate-table",
        action="store_true",
        help="Drop and recreate homework images table",
    )
    parser.add_argument(
        "--create-table-only",
        action="store_true",
        help="Only create SQLAlchemy table, no vectorization",
    )
    args = parser.parse_args()

    if not args.paths_file.is_file():
        print(f"Missing {args.paths_file}. Run extract_image_paths.py first.", file=sys.stderr)
        return 1

    batch_size = args.batch_size or joblib.cpu_count(only_physical_cores=True) or 4
    engine = get_engine()
    create_img_table(engine, recreate=args.recreate_table)

    if args.create_table_only:
        print("Table 'images' ready.")
        return 0

    import torch
    from sentence_transformers import SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading clip-ViT-B-32 on {device} ...")
    model = SentenceTransformer("clip-ViT-B-32", device=device)

    image_paths = load_image_paths(args.paths_file, args.max_images)
    print(f"Vectorizing {len(image_paths)} images (batch_size={batch_size}) ...")
    vectorize_images(engine, model, image_paths, batch_size)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())