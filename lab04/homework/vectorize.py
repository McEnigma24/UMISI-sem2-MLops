#!/usr/bin/env python3
"""CLIP embeddings for ABO images → Postgres (homework)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path

import joblib
from sqlalchemy import func, select
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


def count_paths(paths_file: Path) -> int:
    return sum(1 for ln in paths_file.read_text(encoding="utf-8").splitlines() if ln.strip())


def load_image_paths(paths_file: Path, max_images: int | None) -> list[str]:
    end = max_images if max_images is not None else None
    return load_image_paths_slice(paths_file, 0, end)


def load_image_paths_slice(paths_file: Path, start: int, end: int | None) -> list[str]:
    lines = [ln.strip() for ln in paths_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if start < 0:
        start = 0
    if end is None:
        return lines[start:]
    return lines[start:end]


def count_images_in_db(engine) -> int:
    with Session(engine) as session:
        return int(session.scalar(select(func.count()).select_from(Img)) or 0)


def insert_images(engine, images: list[Img]) -> None:
    with Session(engine) as session:
        session.add_all(images)
        session.commit()


def vectorize_images(
    engine,
    model,
    image_paths: list[str],
    batch_size: int,
    *,
    pool=None,
) -> int:
    from PIL import Image

    from gpu_clip import encode_images

    inserted = 0
    with tqdm(total=len(image_paths)) as pbar:
        for paths_batch in batched(image_paths, batch_size):
            pil_images = [Image.open(p).convert("RGB") for p in paths_batch]
            embeddings = encode_images(model, pil_images, pool=pool, batch_size=batch_size)
            rows = [
                Img(image_path=path, embedding=emb.tolist())
                for path, emb in zip(paths_batch, embeddings)
            ]
            insert_images(engine, rows)
            inserted += len(paths_batch)
            pbar.update(len(paths_batch))
    return inserted


def write_run_meta(
    path: Path,
    *,
    slice_size: int,
    images_inserted: int,
    catalog_total: int,
    slice_start: int,
    slice_end: int,
    images_in_db_after: int,
    batch_size: int,
    multi_gpu: bool,
    cuda_devices: list[str],
    stage_pct_of_catalog: float | None,
    elapsed_seconds: float | None = None,
) -> None:
    meta = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "slice_start_index": slice_start,
        "slice_end_index": slice_end,
        "slice_size_requested": slice_size,
        "images_inserted_this_run": images_inserted,
        "images_in_db_after": images_in_db_after,
        "catalog_total_paths": catalog_total,
        "cumulative_pct_of_full_catalog": round(100.0 * slice_end / catalog_total, 4),
        "stage_pct_of_catalog_target": stage_pct_of_catalog,
        "batch_size": batch_size,
        "multi_gpu": multi_gpu,
        "cuda_devices": cuda_devices,
        "elapsed_seconds": elapsed_seconds,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths-file", type=Path, default=DEFAULT_PATHS)
    parser.add_argument(
        "--max-images",
        type=int,
        default=500,
        help="Legacy: ingest N paths from --start-index (ignored if --end-index set)",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start index in valid_image_paths.txt (inclusive)",
    )
    parser.add_argument(
        "--end-index",
        type=int,
        default=None,
        help="End index (exclusive). With --start-index defines incremental slice.",
    )
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
    parser.add_argument(
        "--meta-out",
        type=Path,
        default=None,
        help="Write JSON run metadata (MAX_IMAGES applied, %% of catalog, GPUs)",
    )
    parser.add_argument(
        "--stage-pct-of-catalog",
        type=float,
        default=None,
        help="Benchmark stage label (e.g. 20 for 20%% of full catalog)",
    )
    parser.add_argument(
        "--multi-gpu",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use all CUDA devices via sentence-transformers process pool",
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

    from gpu_clip import cuda_devices, load_clip, shutdown_pool

    import time

    catalog_total = count_paths(args.paths_file)
    start = args.start_index
    if args.end_index is not None:
        end = args.end_index
    elif args.max_images is not None:
        end = start + args.max_images
    else:
        end = catalog_total

    end = min(end, catalog_total)
    if start >= end:
        print(f"Empty slice [{start}:{end}) — nothing to ingest.", file=sys.stderr)
        return 0

    image_paths = load_image_paths_slice(args.paths_file, start, end)
    slice_size = len(image_paths)
    cumulative_pct = 100.0 * end / catalog_total

    label = (
        f" (stage cumulative {args.stage_pct_of_catalog}% of catalog)"
        if args.stage_pct_of_catalog is not None
        else ""
    )
    before_db = count_images_in_db(engine)
    print(
        f"Slice [{start}:{end}) → {slice_size} new images "
        f"(DB before: {before_db}, cumulative {cumulative_pct:.4f}% of {catalog_total}){label}"
    )

    model, pool = load_clip(multi_gpu=args.multi_gpu)
    gpus = cuda_devices()

    t0 = time.perf_counter()
    try:
        print(f"Vectorizing {slice_size} images (batch_size={batch_size}) ...")
        inserted = vectorize_images(engine, model, image_paths, batch_size, pool=pool)
    finally:
        shutdown_pool(model, pool)
    elapsed = time.perf_counter() - t0
    after_db = count_images_in_db(engine)
    print(f"Inserted {inserted} in {elapsed:.1f}s ({inserted / elapsed:.1f} img/s). DB rows: {after_db}")

    if args.meta_out:
        write_run_meta(
            args.meta_out,
            slice_size=slice_size,
            images_inserted=inserted,
            catalog_total=catalog_total,
            slice_start=start,
            slice_end=end,
            images_in_db_after=after_db,
            batch_size=batch_size,
            multi_gpu=bool(pool),
            cuda_devices=gpus,
            stage_pct_of_catalog=args.stage_pct_of_catalog,
            elapsed_seconds=round(elapsed, 2),
        )
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())