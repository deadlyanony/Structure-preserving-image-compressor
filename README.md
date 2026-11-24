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
4. Renames images dynamically using a running number plus a top-level folder,
   second-level folder, or fixed text (see [Renaming](#renaming)). Files placed
   directly in `input/` keep their original filename with the new extension.

## Config (`config.json`)

| Key | Meaning | Default |
| --- | --- | --- |
| `format` | Output format: `webp`, `jpeg`, `jpg`, `png` | `webp` |
| `quality` | Compression rate 1–100 (higher = better quality, larger file) | `85` |
| `method` | WebP encoding effort 0–6 (higher = slower, smaller) | `4` |
| `max_dimension` | Longest edge in px (0 = no resize) | `1500` |
| `target_size_kb` | Per-file size target in KB (0 = ignore) | `500` |
| `extensions` | Source file extensions to process | `[".jpg", ".jpeg", ".png"]` |
| `exclude_folders` | Folder names to skip while walking | `["HIGH RES"]` |
| `rename_enabled` | Rename output files; `false` keeps original filenames | `true` |
| `rename_use_sub_level` | `false` uses the top-level folder; `true` uses the second-level folder | `false` |
| `rename_as_prefix` | `true` puts the name before the number; `false` puts it after | `true` |
| `rename_use_folder_name` | Prefix source: `true` uses the folder name; `false` uses `rename_text` | `true` |
| `rename_text` | Fixed text: suffix text, or prefix text when folder name is off | `"AF"` |
| `overwrite` | Re-encode files that already exist in `output/` | `false` |

### Renaming

All renaming switches are `true`/`false` values in `config.json`:

- `rename_enabled` — turn renaming on or off.
- `rename_use_sub_level` — `false` uses the top-level folder (`AF7689`); `true`
  uses the second folder level (`Group 1`). If an image has no second level, the
  top-level name is used.
- `rename_as_prefix` — `true` puts the name before the number; `false` puts it
  after the number.
- `rename_use_folder_name` — in prefix mode, `true` uses the selected folder
  name; `false` uses `rename_text`.
- `rename_text` — fixed text used as the suffix, or as the prefix when
  `rename_use_folder_name` is `false`.

| Settings | Example output |
| --- | --- |
| Default (top-level, prefix, folder name) | `AF7689-1.webp` |
| `rename_use_sub_level: true` | `Group 1-1.webp` (number restarts per second-level folder) |
| `rename_use_folder_name: false`, `rename_text: "AF"` | `AF-1.webp` |
| `rename_as_prefix: false`, `rename_text: "AF"` | `1-AF.webp` |
| `rename_enabled: false` | `1-Img191.webp` |

Numbering continues across nested subfolders in top-level mode and restarts in
each second-level folder in sub-level mode. Files placed directly in `input/`
always keep their original names. If the selected text is empty, only the
running number is used. The old `naming` template is replaced by these switches.

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

`HIGH RES` folders are skipped by default. To skip additional folders too:

```json
{ "exclude_folders": ["HIGH RES", "RAW"] }
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
- Numbering is based on the current source files. If you add or remove images
  between runs, numbers shift and can collide with existing output; set
  `"overwrite": true` or clear `output/` when the source set changes.
