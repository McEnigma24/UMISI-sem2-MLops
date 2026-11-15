#!/usr/bin/env bash
# Download and unpack Amazon Berkeley Objects images-small archive (~3 GB).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA="$ROOT/data"
ARCHIVE="$DATA/abo-images-small.tar"
URL="https://amazon-berkeley-objects.s3.amazonaws.com/archives/abo-images-small.tar"
DEST="$DATA/abo"

mkdir -p "$DATA"
if [[ -f "$DEST/images/metadata/images.csv.gz" ]]; then
  echo "Already unpacked at $DEST"
  exit 0
fi

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Downloading $URL ..."
  curl -L --progress-bar -o "$ARCHIVE" "$URL"
fi

mkdir -p "$DEST"
echo "Extracting to $DEST ..."
tar -xf "$ARCHIVE" -C "$DEST"
echo "Done. Run: uv run python homework/extract_image_paths.py"