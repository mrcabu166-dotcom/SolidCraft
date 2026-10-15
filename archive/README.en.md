# SolidCraft — 20-Slot Radial Slide Dryer Rotor Core

[ภาษาไทย](README.md) | **English**

> **ARCHIVE: old design (bayonet-ring version). Do not print.**
> The design in use is in [`../microdry/`](../microdry/README.en.md) (MicroDry-Safe for the Simplus 2L, fully tested October 2026).
> Moved into `archive/` on 15 Oct 2026. Run the commands below from `archive/src`; the venv is at `../../.venv`.
> `output/` is **not in the Git repository** (383 MB, excluded by `.gitignore`). After cloning, rebuild it with `build_all.py`.

Parametric model (CadQuery / OpenCASCADE) of a 20-slot slide drying rotor core with a bayonet-locking comb ring.

> "SolidCraft" is the project folder name, not a CAD program. The models are built with CadQuery (Python).
> `output/check/` holds test and diagnostic files from development. The whole folder can be deleted.

## Rebuild

```bash
cd archive/src
../../.venv/Scripts/python build_all.py                 # build + validate + export + render 7 views
../../.venv/Scripts/python make_report.py               # write output/validation_report.md (in Thai)
SHAFT_TYPE=HEX_COUPLING ../../.venv/Scripts/python build_all.py   # switch shaft mode (set OUT_DIR=... to keep outputs apart)
```

Options: `--no-validate`  `--no-render`  `--no-export`

## Changing dimensions

All values are in `src/params.py`. The top block holds the shaft parameters:

- `SHAFT_TYPE`, `SHAFT_DIAMETER`, `SHAFT_CLEARANCE`
- `D_FLAT_DEPTH`, `SHAFT_BORE_DEPTH`
- `SET_SCREW_DIA`, `CAPTIVE_NUT_WIDTH/THICKNESS`, `BOTTOM_SKIRT_CLEARANCE`

`SHAFT_TYPE` is one of `"D_SHAFT"`, `"HEX_COUPLING"` or `"THREADED_NUT"`.

## Files

| File | Purpose |
|---|---|
| `src/params.py` | All parameters |
| `src/body_cage.py` | Base disc, hub, guide walls, 20 slots, drain holes, seal relief groove |
| `src/body_coupling.py` | Shaft socket, 1×45° lead-in, M3 nut trap, set-screw hole |
| `src/body_bayonet.py` | Bayonet post with 4 L-slots |
| `src/marks.py` | Recessed numbers 1–10 (opposite pairs, 180° apart) |
| `src/ring.py`, `src/assembly.py` | Comb locking ring; assembly with one pair of slides |
| `src/validate.py` | Interference, watertight, overhang, and wall-between-slots checks |
| `src/export_models.py`, `src/render_views.py` | STEP/STL export and 7-view line drawings (HLR) |

## Outputs (`output/`)

- `step/`: `rotor_core_body.step`, `bayonet_comb_ring.step` (in print orientation), `rotor_assembly.step`
- `stl/`: `.stl` files with the same names, meshed as follows (the reasoning is in `validation_report.md`):
  - main surfaces: linear 0.01 mm on every face, angular 0.1°
  - small curved faces under 200 mm²: angular 5°
  - numbers: polylines with 0.003 mm sag
- `drawings/<part>/`: PNG and SVG in 7 views (Front, Back, Left, Right, Top, Bottom, Isometric), plus a combined `*_7views_sheet.png`
- `validation_report.md` / `.json`
