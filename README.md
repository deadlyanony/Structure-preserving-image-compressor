# Structure-Preserving Image Compressor

Drop your image folders into `input/`, run the script, and a compressed copy of
the whole folder structure appears in `output/`. No path setup required — it
auto-detects images at any nesting depth and clones the structure exactly.

## Quick start

1. **Install** (once):
   ```
   pip install -r requirements.txt
   ```
2. **Drop folders** — copy your image folders into `input/`.
3. **Run**:
   ```
   python compressor.py
   ```
4. **Done** — the compressed tree is in `output/`, mirroring `input/` folder-for-folder.

That's it. To change format or quality, edit `config.json` and run again.

## What it does

For every image found under `input/` (any sub-sub folder depth):

1. Recreates the same relative folder path under `output/`.
2. Resizes so the longest edge is at most `max_dimension`.
3. Re-encodes to `format` at `quality`, stepping quality down (and finally
   shrinking dimensions) until each file is under `target_size_kb`.
4. Keeps the original filename and swaps the extension (e.g. `1-Img191.jpg` ->
   `1-Img191.webp`).

## Config (`config.json`)

| Key | Meaning | Default |
| --- | --- | --- |
| `format` | Output format: `webp`, `jpeg`, `jpg`, `png` | `webp` |
| `quality` | Compression rate 1–100 (higher = better quality, larger file) | `85` |
| `method` | WebP encoding effort 0–6 (higher = slower, smaller) | `4` |
| `max_dimension` | Longest edge in px (0 = no resize) | `1500` |
| `target_size_kb` | Per-file size target in KB (0 = ignore) | `500` |
| `extensions` | Source file extensions to process | `[".jpg", ".jpeg", ".png"]` |
| `exclude_folders` | Folder names to skip while walking (e.g. `["HIGH RES"]`) | `[]` |
| `naming` | Output filename template (`name`, `filename`, `ext`) | `{name}.{ext}` |
| `overwrite` | Re-encode files that already exist in `output/` | `false` |

### Optional path overrides

By default `input/` and `output/` sit inside this code folder. If you want to
point elsewhere, add either key to `config.json`:

```json
{ "input_dir": "D:/photos", "output_dir": "D:/photos-compressed" }
```

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
