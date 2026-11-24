#!/usr/bin/env python3
"""Structure-preserving image compressor.

Drop your image folders into `input/`, run this script, and the compressed copy
of the whole folder structure appears in `output/`. No path setup required.

Usage:
    python compressor.py [path/to/config.json]

Defaults to ./config.json (next to this script) when no path is given.
"""

import io
import json
import os
import re
import sys

from PIL import Image

DEFAULT_CONFIG = "config.json"
SUPPORTED_FORMATS = {"webp", "jpeg", "jpg", "png"}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_path(base, value):
    """Resolve a possibly-relative path against `base`."""
    if not value:
        return None
    value = os.path.expanduser(os.path.expandvars(str(value)))
    if not os.path.isabs(value):
        value = os.path.join(base, value)
    return os.path.normpath(value)


def natural_key(text):
    """Sort key that orders embedded numbers numerically (2 before 10)."""
    return [
        (1, int(part)) if part.isdecimal() else (0, part.lower())
        for part in re.split(r"(\d+)", text)
        if part
    ]


def build_output_map(input_dir, output_dir, extensions, exclude_folders, rename, ext):
    """Map each source image to its (out_dir, out_name) before encoding.

    Naming is planned up front so resume skips do not renumber files. The
    `rename` mapping holds the user's switches:

    - enabled: rename files at all (otherwise keep the original name)
    - use_sub_level: use the second path segment instead of the top-level folder
    - as_prefix: put the name before the number, otherwise after it
    - use_folder_name: prefix with the folder name, otherwise with `text`
    - text: fixed prefix text, or the suffix text

    Images directly under input_dir always keep their original name.
    """
    enabled = bool(rename["enabled"])
    use_sub_level = bool(rename["use_sub_level"])
    as_prefix = bool(rename["as_prefix"])
    use_folder_name = bool(rename["use_folder_name"])
    text = str(rename["text"]).strip()

    mapping = {}
    groups = {}

    for root, dirs, files in os.walk(input_dir):
        dirs[:] = sorted(
            (d for d in dirs if d.lower() not in exclude_folders),
            key=natural_key,
        )
        rel_dir = os.path.relpath(root, input_dir)
        for fname in sorted(files, key=natural_key):
            if not fname.lower().endswith(extensions):
                continue
            src = os.path.join(root, fname)
            stem = os.path.splitext(fname)[0]
            if rel_dir == "." or not enabled:
                out_dir = output_dir if rel_dir == "." else os.path.join(output_dir, rel_dir)
                mapping[src] = (out_dir, f"{stem}.{ext}")
                continue

            parts = rel_dir.split(os.sep)
            top = parts[0]
            if use_sub_level:
                sub = parts[1] if len(parts) > 1 else None
                key = (top, sub)
                folder = sub or top
            else:
                key = top
                folder = top
            groups.setdefault(key, []).append((src, rel_dir, fname, stem, folder))

    for items in groups.values():
        for index, (src, rel_dir, fname, stem, folder) in enumerate(items, start=1):
            out_dir = os.path.join(output_dir, rel_dir)
            if as_prefix:
                label = folder if use_folder_name else text
                name = f"{label}-{index}" if label else str(index)
            else:
                name = f"{index}-{text}" if text else str(index)
            mapping[src] = (out_dir, f"{name}.{ext}")

    targets = {}
    for src, (out_dir, out_name) in mapping.items():
        out_path = os.path.join(out_dir, out_name)
        key = os.path.normcase(os.path.abspath(out_path))
        targets.setdefault(key, (out_path, []))[1].append(src)

    for out_path, sources in targets.values():
        if len(sources) > 1:
            raise SystemExit(
                f"Output filename collision: {out_path} would be written by:\n  "
                + "\n  ".join(sources)
                + "\nChange the renaming settings or rename the sources."
            )

    return mapping


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
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, DEFAULT_CONFIG)
    cfg = load_config(config_path)

    # `input` and `output` live inside this code folder by default.
    input_dir = resolve_path(BASE_DIR, cfg.get("input_dir", "input"))
    output_dir = resolve_path(BASE_DIR, cfg.get("output_dir", "output"))

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
    rename = {
        "enabled": cfg.get("rename_enabled", True),
        "use_sub_level": cfg.get("rename_use_sub_level", False),
        "as_prefix": cfg.get("rename_as_prefix", True),
        "use_folder_name": cfg.get("rename_use_folder_name", True),
        "text": cfg.get("rename_text", "AF"),
    }
    overwrite = cfg.get("overwrite", False)

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Input : {input_dir}")
    print(f"Output: {output_dir}")

    total_new = 0
    total_skipped = 0
    total_bytes = 0

    output_map = build_output_map(
        input_dir, output_dir, extensions, exclude_folders, rename, ext
    )

    for src, (out_dir, out_name) in output_map.items():
        out_path = os.path.join(out_dir, out_name)

        if os.path.exists(out_path) and not overwrite:
            total_skipped += 1
            continue

        os.makedirs(out_dir, exist_ok=True)
        im = Image.open(src).convert("RGB")
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
    if total_new == 0 and total_skipped == 0:
        print(f"No images found. Put your image folders inside: {input_dir}")


if __name__ == "__main__":
    main()
