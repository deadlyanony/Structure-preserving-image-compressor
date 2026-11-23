# Structure-Preserving Image Compressor

Walk a source image library, auto-detect images at any nesting depth, clone the
folder structure into an output folder, and re-encode every image to a
compressed format (WebP by default) with a configurable quality and size.

## Workflow

1. **Configure** — edit `config.json` (see below).
2. **Install** — `pip install -r requirements.txt`.
3. **Run** — `python compressor.py`.
4. **Verify** — the cloned, compressed tree is written to `output_dir`.

The script recursively walks `input_dir` and, for every image file it finds:

1. Recreates the same relative folder path under `output_dir` (the whole tree is
   cloned, including any sub-sub folders).
2. Resizes so the longest edge is at most `max_dimension`.
3. Re-encodes to `format` at `quality`, stepping quality down (and finally
   shrinking dimensions) until each file is under `target_size_kb`.
4. Keeps the original filename and swaps the extension (e.g. `1-Img191.jpg` ->
   `1-Img191.webp`), unless a custom `naming` template is set.

No folder names need to be configured — the structure is detected automatically.

## Config (`config.json`)

| Key | Meaning | Default |
| --- | --- | --- |
| `input_dir` | Source folder to scan (cloned recursively) | — |
| `output_dir` | Where the cloned, compressed tree is written | — |
| `format` | Output format: `webp`, `jpeg`, `jpg`, `png` | `webp` |
| `quality` | Compression rate 1–100 (higher = better quality, larger file) | `85` |
| `method` | WebP encoding effort 0–6 (higher = slower, smaller) | `4` |
| `max_dimension` | Longest edge in px (0 = no resize) | `1500` |
| `target_size_kb` | Per-file size target in KB (0 = ignore) | `500` |
| `extensions` | Source file extensions to process | `[".jpg", ".jpeg", ".png"]` |
| `exclude_folders` | Folder names to skip while walking (e.g. `["HIGH RES"]`) | `[]` |
| `naming` | Output filename template (`name`, `filename`, `ext`) | `{name}.{ext}` |
| `overwrite` | Re-encode files that already exist in `output_dir` | `false` |

Paths are resolved relative to the config file's location, so keep
`config.json` and the source/output folders next to each other or use absolute
paths.

## Examples

Compress everything to WebP at quality 85, max 1500 px, under 500 KB:

```json
{ "format": "webp", "quality": 85, "max_dimension": 1500, "target_size_kb": 500 }
```

Skip the high-resolution originals and only process the low-res set:

```json
{ "exclude_folders": ["HIGH RES"] }
```

JPEG at quality 70, no size cap:

```json
{ "format": "jpeg", "quality": 70, "max_dimension": 2000, "target_size_kb": 0 }
```

## Notes

- `png` is lossless; `quality` and `target_size_kb` only apply to lossy
  formats (`webp`, `jpeg`). A size target on PNG is met by resizing only.
- The script is resumable: already-created output files are skipped unless
  `overwrite` is `true`.
