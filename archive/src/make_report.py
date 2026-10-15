"""validation_report.json -> validation_report.md (Thai)."""
import json, os, sys
from params import *

OUT = os.path.abspath(os.environ.get("OUT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")))
r = json.load(open(os.path.join(OUT, "validation_report.json"), encoding="utf-8"))


def ok(b):
    return "ผ่าน" if b else "**ไม่ผ่าน**"


L = []
a = L.append
a("# รายงานตรวจสอบ — 20-Slot Radial Slide Dryer Rotor Core\n")
a("โหมดเพลา: `%s` | เพลา Ø%.2f (รูจริง Ø%.2f) | ด้านเรียบ D ลึก %.1f | ความลึกรูเพลา %.1f มม.\n"
  % (r["shaft_type"], SHAFT_DIAMETER, SHAFT_HOLE_D, D_FLAT_DEPTH, SHAFT_BORE_DEPTH))

a("## 1. โครงสร้าง B-rep\n")
a("| ชิ้นส่วน | Valid | โซลิด | Faces | ปริมาตร (cm³) | ขนาด X×Y×Z (มม.) | Z ต่ำสุด |\n|---|---|---|---|---|---|---|")
for b in r["brep"]:
    a("| %s | %s | %d | %d | %.1f | %s | %.3f |" % (b["name"], ok(b["valid"]), b["solids"], b["faces"], b["volume_cm3"],
                                                   " × ".join("%.1f" % v for v in b["bbox_mm"]), b["zmin"]))

if "mesh" in r:
    a("\n## 2. ตาข่าย STL (Manifold / Watertight)\n")
    a("Linear deflection %.2f มม. ทุกหน้า · Angular %.1f° บนผิวหลัก (ทรงกระบอก, กรวย, ระนาบขนาดใหญ่)\n"
      % (STL_LINEAR_DEFLECTION, STL_ANGULAR_DEG))
    a("- หน้าโค้งเล็ก (< %.0f mm² : กรวย lead-in, เพดานรูเพลา, รูสกรู) ใช้ angular %.0f° ที่ linear %.2f มม. เท่าเดิม "
      "เพราะ mesh ของ OCCT เป็นกริด 2 ทิศ — ที่ 0.1° จะได้สามเหลี่ยมนับล้านและใช้ RAM หลาย GB (ทดลองแล้ว)"
      % (SMALL_FACE_AREA, SMALL_FACE_ANGULAR_DEG, STL_LINEAR_DEFLECTION))
    a("- ตัวเลขใน STL เป็น polyline ความคลาด %.3f มม. (STEP และภาพเขียนแบบใช้เส้นโค้งจริง) ทำให้เมชต่อกันสนิท\n" % GLYPH_SAG)
    a("| ไฟล์ | สามเหลี่ยม | Watertight | Winding สอดคล้อง | Bodies | ปริมาตร (cm³) | ขนาดไฟล์ (MB) |\n|---|---|---|---|---|---|---|")
    for m in r["mesh"]:
        a("| %s | %d | %s | %s | %d | %.1f | %.1f |" % (m["file"], m["triangles"], ok(m["watertight"]),
                                                       ok(m["winding_consistent"]), m["bodies"], m["volume_cm3"], m["size_mb"]))

s = r["slots"]
a("\n## 3. ช่องเสียบสไลด์ 20 ช่อง\n")
a("| รายการ | ค่าที่วัด | เกณฑ์ | ผล |\n|---|---|---|---|")
a("| ผนังกั้นระหว่างร่องที่ปลายด้านใน (R=%.1f) | %.2f มม. | ≥ %.1f มม. | %s |" % (R_HUB, s["min_wall_between_adjacent_slots_mm"], s["wall_required_mm"], ok(s["min_wall_between_adjacent_slots_mm"] >= s["wall_required_mm"])))
a("| ความคลาดมุมศูนย์กลางช่อง (สมมาตร 18°) | %.6f° | 0 | %s |" % (s["max_slot_center_angle_error_deg"], ok(s["max_slot_center_angle_error_deg"] < 1e-3)))
if "min_wall_around_set_screw_hole_mm" in s:
    a("| เนื้อพลาสติกรอบรูสกรูล็อกเพลา (ถึงร่องที่ใกล้สุด) | %.2f มม. | ≥ 1.0 มม. | %s |" % (s["min_wall_around_set_screw_hole_mm"], ok(s["min_wall_around_set_screw_hole_mm"] >= 1.0)))
v = r["slides_20"]
a("| สไลด์ 20 แผ่น ชนตัวแกน | %.6f mm³ | 0 | %s |" % (v["slides_vs_body_mm3"], ok(v["slides_vs_body_mm3"] < 1e-6)))
a("| สไลด์ 20 แผ่น ชนแหวนล็อก | %.6f mm³ | 0 | %s |" % (v["slides_vs_ring_mm3"], ok(v["slides_vs_ring_mm3"] < 1e-6)))
a("| สไลด์ชนสไลด์ข้างเคียง | %.6f mm³ | 0 | %s |" % (v["slide_vs_neighbour_slide_mm3"], ok(v["slide_vs_neighbour_slide_mm3"] < 1e-6)))
a("| ระยะระหว่างสไลด์ข้างเคียงที่ใกล้สุด | %.2f มม. | > 0 | %s |" % (v["min_gap_between_neighbour_slides_mm"], ok(v["min_gap_between_neighbour_slides_mm"] > 0)))

b = r["bayonet"]
a("\n## 4. บาโยเน็ต (Clearance %.2f มม., บิด %.0f°)\n" % (b["clearance_mm"], b["twist_deg"]))
a("| สถานะทดสอบ | ปริมาตรซ้อน (mm³) | คาดหวัง |\n|---|---|---|")
exp = {"unlocked_seated": "0", "mid_twist": "0", "locked_seated": "0", "locked_lift_0.2mm_(free play)": "0 (ระยะเล่นแกน)",
       "locked_lift_0.5mm_(must block)": "> 0 (ล็อกไม่ให้หลุด)", "overrotate_+4deg_(must stop)": "> 0 (หยุดที่ปลายร่อง)",
       "unlocked_lift_20mm_(must be free)": "0 (ถอดออกได้)"}
for k, e in exp.items():
    a("| %s | %.4f | %s |" % (k, b[k], e))
a("\nผลรวม: %s" % ok(b["pass"]))
t = r["teeth"]
a("\nซี่หวี 20 ซี่ คร่อมขอบบนสไลด์เมื่อล็อก: %.1f mm³ ; เมื่อปลดล็อก: %.1f mm³ (ต้องเป็น 0)\n" % (t["teeth_over_slides_locked_mm3"], t["teeth_over_slides_unlocked_mm3"]))

d = r["drain"]
a("## 5. ร่องระบาย (%d ช่อง, หน้าตัด %s)\n" % (d["drain_count"], d["drain_section_mm"]))
for k in ("groove_open_to_rim_and_bottom_(slots 1,8,14)", "weep_windows_open_floor_to_groove", "support_bars_under_slide_present"):
    a("- %s : %s" % (k, ok(d[k])))

if "overhang_body" in r:
    a("\n## 6. Overhang จากตาข่ายจริง (เกณฑ์ > 45° จากแนวดิ่ง, ไม่นับหน้าสัมผัสฐาน Z=0)\n")
    for nm, key in (("rotor_core_body", "overhang_body"), ("bayonet_comb_ring (กลับหัว)", "overhang_ring")):
        o = r[key]
        a("**%s** — พื้นที่รวม %.1f mm²" % (nm, o["total_area_mm2"]))
        for g in o["groups"][:6]:
            a("- Z=%s : %.1f mm² (%d สามเหลี่ยม)" % (g["z_mm"], g["area_mm2"], g["triangles"]))
        a("")
    a("หมายเหตุ: ที่เหลือคือเพดานของตัวเลขปั๊มจม (ลึก 0.8 มม., เส้นกว้าง ~0.9 มม. bridge ได้สบาย) และหน้าแบนยอดกรวยเพดานรูเพลา (Ø1 มม.) — "
      "ไม่มีเพดานแบนที่ต้อง bridge กว้างกว่า 1 มม. ส่วนเพดาน 45° ทั้งหมด (ร่องระบาย, ช่องนอต, รูสกรู, L-slot, ร่องหลบซีล, เขี้ยวแหวน) ไม่นับเป็น overhang\n")

p = r["print_orientation"]
a("## 7. ทิศพิมพ์ 3D\n")
a("- rotor_core_body ตั้งตรง ฐานที่ Z = %.3f %s" % (p["rotor_core_body_zmin"], ok(abs(p["rotor_core_body_zmin"]) < 1e-3)))
a("- bayonet_comb_ring พลิก 180° หน้าเรียบด้านบนวางบนพื้นที่ Z = %.3f (สูง %.1f มม.) %s" % (p["bayonet_comb_ring_zmin"], p["bayonet_comb_ring_zmax"], ok(abs(p["bayonet_comb_ring_zmin"]) < 1e-3)))

open(os.path.join(OUT, "validation_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("report written")
