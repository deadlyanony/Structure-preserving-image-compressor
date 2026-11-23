# Structure-Preserving Image Compressor

Clone the folder structure of a source image library and re-encode every image
to a compressed format (WebP by default) with a configurable quality and size.

## Workflow

1. **Configure** — edit `config.json` (see below).
2. **Install** — `pip install -r requirements.txt`.
3. **Run** — `python compressor.py`.
4. **Verify** — the cloned, compressed tree is written to `output_dir`.

For each top-level folder in `input_dir` the script:

1. Reads images from `source_subfolder` (e.g. `LOW RES`), falling back to
   `fallback_subfolder` (e.g. `HIGH RES`) when missing.
2. Resizes so the longest edge is at most `max_dimension`.
3. Re-encodes to `format` at `quality`, stepping quality down (and finally
   shrinking dimensions) until each file is under `target_size_kb`.
4. Writes the cloned tree to `output_dir`, naming files with
   `{folder-prefix}-{n}.{ext}` (a leading number from the source filename is
   preserved, so `1-Img191.jpg` -> `AF7362-1.webp`).

## Config (`config.json`)

| Key | Meaning | Default |
| --- | --- | --- |
| `input_dir` | Source folder to scan (top-level folders are cloned) | — |
| `output_dir` | Where the cloned, compressed tree is written | — |
| `format` | Output format: `webp`, `jpeg`, `jpg`, `png` | `webp` |
| `quality` | Compression rate 1–100 (higher = better quality, larger file) | `85` |
| `method` | WebP encoding effort 0–6 (higher = slower, smaller) | `4` |
| `max_dimension` | Longest edge in px (0 = no resize) | `1500` |
| `target_size_kb` | Per-file size target in KB (0 = ignore) | `500` |
| `source_subfolder` | Subfolder to read images from | `LOW RES` |
| `fallback_subfolder` | Used when `source_subfolder` is missing | `HIGH RES` |
| `extensions` | Source file extensions to process | `[".jpg", ".jpeg", ".png"]` |
| `folder_prefix_regex` | Regex capturing the filename prefix from the folder name | `^[^-\s]+` |
| `naming` | Output filename template (`prefix`, `n`, `ext`, `name`) | `{prefix}-{n}.{ext}` |
| `overwrite` | Re-encode files that already exist in `output_dir` | `false` |

Paths are resolved relative to the config file's location, so keep
`config.json` and the source/output folders next to each other or use absolute
paths.

## Examples

WebP at quality 85, max 1500 px, under 500 KB:

```json
{ "format": "webp", "quality": 85, "max_dimension": 1500, "target_size_kb": 500 }
```

JPEG at quality 70:

```json
{ "format": "jpeg", "quality": 70, "max_dimension": 2000, "target_size_kb": 0 }
```

## Notes

- `png` is lossless; `quality` and `target_size_kb` only apply to lossy
  formats (`webp`, `jpeg`). A size target on PNG is met by resizing only.
- The script is resumable: already-created output files are skipped unless
  `overwrite` is `true`.
