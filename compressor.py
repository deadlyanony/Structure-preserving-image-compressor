#!/usr/bin/env python3
"""Structure-preserving image compressor.

Walks an input folder recursively, auto-detects image files at any nesting
depth, clones the folder structure into an output folder, and re-encodes each
image to the configured format, size, and quality.

Usage:
    python compressor.py [path/to/config.json]

Defaults to ./config.json when no path is given.
"""

import io
import json
import os
import sys

from PIL import Image

DEFAULT_CONFIG = "config.json"
SUPPORTED_FORMATS = {"webp", "jpeg", "jpg", "png"}


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(base, value):
    """Resolve a possibly-relative path against the config file's directory."""
    if not value:
        return None
    value = os.path.expanduser(os.path.expandvars(str(value)))
    if not os.path.isabs(value):
        value = os.path.join(base, value)
    return os.path.normpath(value)


def encode(im, fmt, quality, target_bytes, method):
    """Encode to `fmt`, stepping quality down to stay under target_bytes."""
    start = quality if quality is not None else 85
    qualities = [start]
    if target_bytes:
        qualities = [q for q in (start, 80, 70, 60, 50, 40, 30)]

    data = None
    for q in qualities:
        buf = io.BytesIO()
        if fmt == "webp":
            im.save(buf, "WEBP", quality=q, method=method)
        elif fmt in ("jpeg", "jpg"):
            im.save(buf, "JPEG", quality=q, optimize=True)
        else:  # png (lossless; quality not applicable)
            im.save(buf, "PNG", optimize=True)
        data = buf.getvalue()
        if not target_bytes or len(data) <= target_bytes:
            break

    # Last-resort: shrink dimensions until the target is met.
    if target_bytes and len(data) > target_bytes:
        im2 = im
        while len(data) > target_bytes:
            w, h = im2.size
            im2 = im2.resize((int(w * 0.9), int(h * 0.9)), Image.LANCZOS)
            buf = io.BytesIO()
            if fmt == "png":
                im2.save(buf, "PNG", optimize=True)
            elif fmt == "webp":
                im2.save(buf, "WEBP", quality=30, method=method)
            else:
                im2.save(buf, "JPEG", quality=30, optimize=True)
            data = buf.getvalue()

    return data


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG
    cfg = load_config(config_path)
    base = os.path.dirname(os.path.abspath(config_path))

    input_dir = resolve_path(base, cfg.get("input_dir"))
    output_dir = resolve_path(base, cfg.get("output_dir"))
    if not input_dir or not os.path.isdir(input_dir):
        raise SystemExit(f"input_dir not found: {input_dir}")

    fmt = str(cfg.get("format", "webp")).lower()
    if fmt not in SUPPORTED_FORMATS:
        raise SystemExit(f"Unsupported format '{fmt}'. Choose one of {sorted(SUPPORTED_FORMATS)}.")
    ext = "jpg" if fmt == "jpeg" else fmt

    quality = cfg.get("quality", 85)
    method = cfg.get("method", 4)
    max_dimension = cfg.get("max_dimension") or 0
    target_size_kb = cfg.get("target_size_kb") or 0
    target_bytes = int(target_size_kb * 1024) if target_size_kb else None

    extensions = tuple(e.lower() for e in cfg.get("extensions", [".jpg", ".jpeg", ".png"]))
    exclude_folders = {str(d).lower() for d in cfg.get("exclude_folders", [])}
    naming = cfg.get("naming", "{name}.{ext}")
    overwrite = cfg.get("overwrite", False)

    os.makedirs(output_dir, exist_ok=True)

    total_new = 0
    total_skipped = 0
    total_bytes = 0

    for root, dirs, files in os.walk(input_dir):
        dirs[:] = [d for d in dirs if d.lower() not in exclude_folders]
        rel_dir = os.path.relpath(root, input_dir)
        out_dir = output_dir if rel_dir == "." else os.path.join(output_dir, rel_dir)

        for fname in files:
            if not fname.lower().endswith(extensions):
                continue

            name = os.path.splitext(fname)[0]
            out_name = naming.format(name=name, filename=fname, ext=ext)
            out_path = os.path.join(out_dir, out_name)

            if os.path.exists(out_path) and not overwrite:
                total_skipped += 1
                continue

            os.makedirs(out_dir, exist_ok=True)
            im = Image.open(os.path.join(root, fname)).convert("RGB")
            w, h = im.size
            if max_dimension and max(w, h) > max_dimension:
                scale = max_dimension / max(w, h)
                im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)

            data = encode(im, fmt, quality, target_bytes, method)
            with open(out_path, "wb") as f:
                f.write(data)
            total_new += 1
            total_bytes += len(data)

    print("---")
    print(f"Done. {total_new} new files, {total_skipped} skipped, {total_bytes / 1024 / 1024:.1f} MB total.")


if __name__ == "__main__":
    main()
