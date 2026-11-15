"""Text → image similarity search (homework)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib

if not os.environ.get("DISPLAY") and matplotlib.get_backend().lower() != "agg":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from models import Img


class ImageSearch:
    def __init__(self, engine: Engine, model: SentenceTransformer):
        self.engine = engine
        self.model = model

    def __call__(
        self,
        image_description: str,
        k: int = 5,
        *,
        save_path: Path | None = None,
        show: bool = True,
    ) -> list[Img]:
        found = self.find_similar_images(image_description, k)
        for i, row in enumerate(found, start=1):
            print(f"{i}. {row.image_path}")
        paths = [row.image_path for row in found]
        self.display_images(paths, save_path=save_path, show=show)
        return found

    def find_similar_images(self, image_description: str, k: int) -> list[Img]:
        embedding = self.model.encode(image_description).tolist()
        with Session(self.engine) as session:
            query = (
                select(Img)
                .order_by(Img.embedding.cosine_distance(embedding))
                .limit(k)
            )
            result = session.execute(query, execution_options={"prebuffer_rows": True})
            return list(result.scalars().all())

    def display_images(
        self,
        image_paths: list[str],
        *,
        save_path: Path | None = None,
        show: bool = True,
    ) -> None:
        n = len(image_paths)
        if n == 0:
            print("No images to display.")
            return
        fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
        if n == 1:
            axes = [axes]
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            axes[i].imshow(img)
            axes[i].axis("off")
            axes[i].set_title(Path(img_path).name[:20], fontsize=8)
        plt.tight_layout()
        out = save_path or Path("search_results.png")
        if save_path is not None or not os.environ.get("DISPLAY"):
            fig.savefig(out, dpi=120, bbox_inches="tight")
            print(f"Saved preview: {out.resolve()}")
        if show and os.environ.get("DISPLAY"):
            plt.show()
        else:
            plt.close(fig)


def default_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformer("clip-ViT-B-32", device=device)


def main() -> int:
    parser = argparse.ArgumentParser(description="Text query → similar ABO images")
    parser.add_argument("query", nargs="+", help="Text description of the image")
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("-o", "--output", type=Path, default=Path("search_results.png"))
    args = parser.parse_args()
    query = " ".join(args.query)

    from db import get_engine

    print(f"Query: {query!r}")
    search = ImageSearch(get_engine(), default_model())
    search(query, k=args.k, save_path=args.output, show=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())