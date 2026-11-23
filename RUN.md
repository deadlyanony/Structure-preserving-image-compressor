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

The compressed copy is written to `output/`, mirroring `input/` folder-for-folder:

```
output/
  Style A/
    Group 1/
      1-shot.webp
      2-shot.webp
  Style B/
    photo.webp
```

## Change format / quality

Edit `config.json`:

- `format`: `webp`, `jpeg`, `jpg`, or `png`
- `quality`: 1–100 (higher = better quality, bigger file)
- `max_dimension`: longest edge in pixels (0 = keep original size)
- `target_size_kb`: per-file size cap (0 = no cap)

Then run `python compressor.py` again.

## Optional: skip a folder

To ignore certain folders (for example, `HIGH RES`), edit `config.json`:

```json
{ "exclude_folders": ["HIGH RES"] }
```

---

Full configuration reference is in [`README.md`](README.md).
