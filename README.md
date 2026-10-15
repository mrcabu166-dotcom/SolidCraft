# SolidCraft

โปรเจกต์โมเดล 3D แบบ parametric (CadQuery, Python venv อยู่ที่ `.venv`)

| โฟลเดอร์ | สถานะ | เนื้อหา |
|---|---|---|
| [`microdry/`](microdry/README.md) | **ใช้งานจริง** — ทดสอบผ่าน ต.ค. 2026 | MicroDry-Safe โรเตอร์ปั่นตากสไลด์ 20 ช่อง สำหรับ Simplus 2L |
| [`archive/`](archive/README.md) | แบบเก่า — อย่านำไปพิมพ์ | รุ่นแหวนบาโยเน็ต (`src/`, `output/`) เก็บไว้อ้างอิง |

> ถ้าจะพิมพ์อย่างเดียว ไม่ต้องติดตั้งอะไร — ไฟล์ STL ที่ทดสอบแล้วอยู่ใน `microdry/output/stl/`
> ติดตั้งด้านล่างเฉพาะเมื่อต้องการแก้ค่าแล้วสร้างโมเดลใหม่

## ติดตั้ง (ครั้งแรกหลัง clone)

ต้องมี **Python 3.11** (ทดสอบกับ 3.11.9 บน Windows 11) — ดาวน์โหลดจาก python.org แล้วติ๊ก "Add python.exe to PATH" ตอนติดตั้ง

```bash
git clone https://github.com/mrcabu166-dotcom/SolidCraft.git
cd SolidCraft
py -3.11 -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip
.venv/Scripts/python -m pip install -r requirements.txt
```

- macOS / Linux: ใช้ `python3.11 -m venv .venv` และ `.venv/bin/python` แทน `.venv/Scripts/python`
- `cadquery` ดาวน์โหลด OpenCASCADE ราว 300–500 MB ครั้งแรกใช้เวลาหลายนาที
- เวอร์ชันใน [`requirements.txt`](requirements.txt) ล็อกไว้ตรงกับชุดที่ใช้สร้างไฟล์ที่ทดสอบผ่านแล้ว

ตรวจว่าติดตั้งถูก:

```bash
.venv/Scripts/python -c "import cadquery, yaml, trimesh, matplotlib; print('ok', cadquery.__version__)"
```

## สร้างโมเดลใหม่

```bash
cd microdry
../.venv/Scripts/python slide_rotor.py              # สร้าง + ตรวจ 28 กฎ + export STEP/STL + ภาพ PNG
../.venv/Scripts/python slide_rotor.py --no-render  # เร็วกว่า ไม่สร้างภาพ
```

ผลลัพธ์อยู่ที่ `microdry/output/` — ถ้าเห็น `design rules: 28/28 pass` และ `DONE` แปลว่าใช้ได้
(บน Windows ถ้าข้อความภาษาไทยเพี้ยน ให้ตั้ง `PYTHONIOENCODING=utf-8` ก่อนรัน)
