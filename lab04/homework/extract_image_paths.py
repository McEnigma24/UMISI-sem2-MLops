#!/usr/bin/env python3
"""Extract valid ABO image paths from images.csv.gz (homework: dataset preparation)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

MIN_SIZE_PX = 1000
DEFAULT_METADATA = Path("images/metadata/images.csv.gz")


def find_dataset_root(path: Path) -> Path:
    path = path.resolve()
    if (path / DEFAULT_METADATA).is_file():
        return path
    if path.name == "metadata" and path.parent.name == "images":
        return path.parent.parent
    raise FileNotFoundError(
        f"Cannot find {DEFAULT_METADATA} under {path}. "
        "Point --dataset-root at unpacked abo-images-small.tar directory."
    )


def resolve_images_dir(dataset_root: Path, subdir: str) -> Path:
    if subdir == "auto":
        original = dataset_root / "images" / "original"
        small = dataset_root / "images" / "small"
        if small.is_dir():
            return small
        return original
    return dataset_root / "images" / subdir


def extract_paths(
    dataset_root: Path,
    *,
    min_width: int = MIN_SIZE_PX,
    min_height: int = MIN_SIZE_PX,
    images_subdir: str = "auto",
    require_file: bool = True,
) -> list[dict]:
    metadata_path = dataset_root / DEFAULT_METADATA
    df = pd.read_csv(metadata_path)
    valid = df[(df["width"] >= min_width) & (df["height"] >= min_height)].copy()

    images_dir = resolve_images_dir(dataset_root, images_subdir)
    rows: list[dict] = []
    for record in valid.itertuples(index=False):
        rel = Path(record.path)
        full = (images_dir / rel).resolve()
        if require_file and not full.is_file():
            continue
        rows.append(
            {
                "image_id": record.image_id,
                "width": int(record.width),
                "height": int(record.height),
                "path": str(full),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract ABO image paths (>= min width/height).")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parent / "data" / "abo",
        help="Root directory containing images/metadata/images.csv.gz",
    )
    parser.add_argument("--min-width", type=int, default=MIN_SIZE_PX)
    parser.add_argument("--min-height", type=int, default=MIN_SIZE_PX)
    parser.add_argument(
        "--images-subdir",
        choices=("auto", "original", "small"),
        default="auto",
        help="Image files live under images/original or images/small (small for abo-images-small.tar).",
    )
    parser.add_argument(
        "--no-require-file",
        action="store_true",
        help="Keep rows even when the image file is missing on disk (metadata-only list).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSON lines (.jsonl) with path metadata; default: <dataset-root>/valid_image_paths.jsonl",
    )
    args = parser.parse_args()

    dataset_root = find_dataset_root(args.dataset_root)
    rows = extract_paths(
        dataset_root,
        min_width=args.min_width,
        min_height=args.min_height,
        images_subdir=args.images_subdir,
        require_file=not args.no_require_file,
    )

    out = args.output or (dataset_root / "valid_image_paths.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    paths_only = dataset_root / "valid_image_paths.txt"
    paths_only.write_text("\n".join(r["path"] for r in rows) + ("\n" if rows else ""), encoding="utf-8")

    print(f"Metadata matches (>={args.min_width}px): filtered from CSV at {dataset_root}")
    print(f"Images on disk (subdir={args.images_subdir}): {len(rows)} paths")
    print(f"Wrote {out}")
    print(f"Wrote {paths_only}")
    if rows:
        print(f"Example: {rows[0]['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())