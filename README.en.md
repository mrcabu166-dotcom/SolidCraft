# SolidCraft

[ภาษาไทย](README.md) | **English**

Parametric 3D-printable models built with CadQuery (Python venv in `.venv`).

| Folder | Status | Contents |
|---|---|---|
| [`microdry/`](microdry/README.en.md) | **In use**: tested Oct 2026 | MicroDry-Safe, a 20-slot slide drying rotor for the Simplus 2L chopper |
| [`archive/`](archive/README.md) | Old design. Do not print | Bayonet-ring version (`src/`, `output/`), kept for reference only (Thai docs) |

> To print only, you need nothing installed. The tested STL files are in `microdry/output/stl/`.
> Follow the setup below only if you want to change parameters and rebuild the model.

## Setup (first time after cloning)

Requires **Python 3.11** (tested with 3.11.9 on Windows 11). Install it from python.org and tick "Add python.exe to PATH".

```bash
git clone https://github.com/mrcabu166-dotcom/SolidCraft.git
cd SolidCraft
py -3.11 -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip
.venv/Scripts/python -m pip install -r requirements.txt
```

- On macOS / Linux, use `python3.11 -m venv .venv` and `.venv/bin/python` instead of `.venv/Scripts/python`.
- `cadquery` downloads OpenCASCADE (about 300–500 MB), so the first install takes several minutes.
- [`requirements.txt`](requirements.txt) pins the exact versions that produced the tested files.

Check the install:

```bash
.venv/Scripts/python -c "import cadquery, yaml, trimesh, matplotlib; print('ok', cadquery.__version__)"
```

## Rebuild the model

```bash
cd microdry
../.venv/Scripts/python slide_rotor.py              # build + 28 design-rule checks + STEP/STL export + PNG previews
../.venv/Scripts/python slide_rotor.py --no-render  # faster, skips the previews
```

The outputs go to `microdry/output/`. The build is good when it prints `design rules: 28/28 pass` and `DONE`.
On Windows, if the console shows garbled characters, set `PYTHONIOENCODING=utf-8` before running.
