# How to Run

A beginner-friendly, step-by-step guide. You only need Python installed.

## 1. Install the one dependency (only once)

Open a terminal **in this folder** and run:

```
pip install -r requirements.txt
```

> Tip: in Windows File Explorer, open this folder, click the address bar,
> type `cmd`, and press Enter to open a terminal already in this folder.

## 2. Put your images in the `input` folder

Copy your image folders into `input/`. Any folder structure works — the tool
auto-detects images at every level.

```
input/
  Style A/
    Group 1/
      1-shot.jpg
      2-shot.jpg
  Style B/
    photo.jpg
```

## 3. Run the compressor

In the same terminal, run:

```
python compressor.py
```

## 4. Get your compressed images

The compressed copy is written to `output/`, mirroring `input/` folder-for-folder.
By default, images are renamed using the top-level folder name plus a running
number, so `Style A`'s images become `Style A-1.webp`, `Style A-2.webp`, and so on:

```
output/
  Style A/
    Group 1/
      Style A-1.webp
      Style A-2.webp
  Style B/
    Style B-1.webp
```

## Change format / quality

Edit `config.json`:

- `format`: `webp`, `jpeg`, `jpg`, or `png`
- `quality`: 1–100 (higher = better quality, bigger file)
- `max_dimension`: longest edge in pixels (0 = keep original size)
- `target_size_kb`: per-file size cap (0 = no cap)

Then run `python compressor.py` again.

## Change renaming

These `true`/`false` settings live in `config.json`:

- `rename_enabled`: `true` renames files; `false` keeps original names.
- `rename_use_sub_level`: `false` uses the top-level folder; `true` uses the
  second folder level.
- `rename_as_prefix`: `true` puts the name before the number; `false` after it.
- `rename_use_folder_name`: in prefix mode, `true` uses the folder name;
  `false` uses `rename_text`.
- `rename_text`: fixed text used for suffix mode, or for prefix mode when the
  folder name is off.

The defaults produce names like `AF7689-1.webp`. Full examples are in
[`README.md`](README.md#renaming).

## Optional: skip a folder

To ignore certain folders (for example, `HIGH RES`), edit `config.json`:

```json
{ "exclude_folders": ["HIGH RES"] }
```

---

Full configuration reference is in [`README.md`](README.md).
