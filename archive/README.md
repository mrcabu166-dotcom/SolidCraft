# SolidCraft — 20-Slot Radial Slide Dryer Rotor Core

> **ARCHIVE — แบบเก่า (รุ่นแหวนบาโยเน็ต) อย่านำไปพิมพ์**
> รุ่นที่ใช้งานจริงอยู่ที่ [`../microdry/`](../microdry/README.md) (MicroDry-Safe สำหรับ Simplus 2L — ทดสอบผ่านแล้ว ตุลาคม 2026)
> ย้ายมาไว้ใน `archive/` เมื่อ 15 ต.ค. 2026 — คำสั่งด้านล่างรันจาก `archive/src` และ venv อยู่ที่ `../../.venv`

โมเดล Parametric (CadQuery / OpenCASCADE) ของแกนปั่นตากสไลด์ 20 ช่อง + แหวนหวีล็อกบาโยเน็ต

> ในเครื่องไม่มีโปรแกรม CAD ชื่อ "SolidCraft" — โฟลเดอร์นี้ใช้เป็นโปรเจกต์ และสร้างโมเดลด้วย CadQuery (Python, venv ที่ `.venv`).
> `output/check/` เป็นไฟล์ทดสอบ/วินิจฉัยระหว่างพัฒนา (ลบได้ทั้งโฟลเดอร์)

## รันใหม่

```bash
cd archive/src
../../.venv/Scripts/python build_all.py                 # สร้าง + ตรวจสอบ + export + เรนเดอร์ภาพ 7 มุม
../../.venv/Scripts/python make_report.py               # สร้าง output/validation_report.md (ไทย)
SHAFT_TYPE=HEX_COUPLING ../../.venv/Scripts/python build_all.py   # สลับโหมดเพลา (OUT_DIR=... เพื่อแยกโฟลเดอร์)
```

ตัวเลือก: `--no-validate`  `--no-render`  `--no-export`

## ปรับขนาด

ทุกค่าอยู่ใน `src/params.py` (บล็อกบนสุดคือพารามิเตอร์เพลา: `SHAFT_TYPE`, `SHAFT_DIAMETER`, `SHAFT_CLEARANCE`,
`D_FLAT_DEPTH`, `SHAFT_BORE_DEPTH`, `SET_SCREW_DIA`, `CAPTIVE_NUT_WIDTH/THICKNESS`, `BOTTOM_SKIRT_CLEARANCE`).
`SHAFT_TYPE` = `"D_SHAFT"` | `"HEX_COUPLING"` | `"THREADED_NUT"`.

## โครงสร้างไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `src/params.py` | พารามิเตอร์ทั้งหมด |
| `src/body_cage.py` | จานฐาน ดุม ผนังนำร่อง ร่อง 20 ช่อง รูระบาย ร่องหลบซีล |
| `src/body_coupling.py` | เบ้าเพลา, lead-in 1×45°, ช่องนอต M3, รูสกรูล็อก |
| `src/body_bayonet.py` | แกนรับล็อก + L-slot 4 ตำแหน่ง |
| `src/marks.py` | ตัวเลข 1–10 ปั๊มจม (คู่ตรงข้าม 180°) |
| `src/ring.py`, `src/assembly.py` | แหวนหวีล็อก, ชุดประกอบ + สไลด์ 1 คู่ |
| `src/validate.py` | interference / watertight / overhang / ผนังระหว่างร่อง |
| `src/export_models.py`, `src/render_views.py` | STEP/STL และภาพลายเส้น 7 มุม (HLR) |

## ผลลัพธ์ (`output/`)

- `step/` — `rotor_core_body.step`, `bayonet_comb_ring.step` (ทิศพิมพ์), `rotor_assembly.step`
- `stl/` — ไฟล์ `.stl` ชื่อเดียวกัน (linear 0.01 mm ทุกหน้า / angular 0.1° บนผิวหลัก; หน้าโค้งเล็ก < 200 mm² ใช้ 5°, ตัวเลขเป็น polyline sag 0.003 mm — เหตุผลอยู่ใน `validation_report.md`)
- `drawings/<ชิ้นงาน>/` — PNG + SVG 7 มุม (Front, Back, Left, Right, Top, Bottom, Isometric) และแผ่นรวม `*_7views_sheet.png`
- `validation_report.md` / `.json`
