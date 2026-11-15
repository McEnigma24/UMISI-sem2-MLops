"""CLIP loading with optional multi-GPU encoding (sentence-transformers process pool)."""

from __future__ import annotations

import torch
from sentence_transformers import SentenceTransformer

CHECKPOINT = "clip-ViT-B-32"


def cuda_devices() -> list[str]:
    if not torch.cuda.is_available():
        return []
    return [f"cuda:{i}" for i in range(torch.cuda.device_count())]


def load_clip(*, multi_gpu: bool | None = None):
    """
    Returns (model, pool). pool is None unless multi_gpu and >=2 CUDA devices.
    Call stop_multi_process_pool when finished.
    """
    devices = cuda_devices()
    if multi_gpu is None:
        multi_gpu = len(devices) >= 2

    model = SentenceTransformer(CHECKPOINT)
    if multi_gpu and len(devices) >= 2:
        print(f"Multi-GPU encode on: {devices}")
        pool = model.start_multi_process_pool(target_devices=devices)
        return model, pool

    device = devices[0] if devices else "cpu"
    model = SentenceTransformer(CHECKPOINT, device=device)
    print(f"Single device encode: {device}")
    return model, None


def encode_images(model, images, *, pool, batch_size: int):
    import numpy as np

    if pool is not None:
        emb = model.encode_multi_process(images, pool, batch_size=batch_size)
        if isinstance(emb, list):
            return np.asarray(emb)
        return emb
    return model.encode(images, batch_size=batch_size, convert_to_numpy=True)


def shutdown_pool(model, pool) -> None:
    if pool is not None:
        model.stop_multi_process_pool(pool)