"""Validation suite: B-rep validity, manifold/watertight mesh, interference, bayonet tolerances,
slot walls, drain paths and FDM overhang (zero-support) analysis."""
import math
import numpy as np
import cadquery as cq
from params import *
from geom import *
from ring import place_in_assembly
from assembly import all_slides, slide_solid
from body_cage import slot_cutter
from body_coupling import coupling_cutters

EPS_VOL = 1e-6


def vol_int(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return float("nan")


def brep_report(name, shape):
    bb = shape.BoundingBox()
    return {"name": name, "valid": bool(shape.isValid()), "solids": len(shape.Solids()),
            "faces": len(shape.Faces()), "volume_cm3": round(shape.Volume() / 1000.0, 3),
            "bbox_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)], "zmin": round(bb.zmin, 4)}


def mesh_report(path):
    import trimesh
    m = trimesh.load(path, force="mesh")
    return {"file": path.replace("\\", "/").split("/")[-1], "triangles": int(len(m.faces)),
            "watertight": bool(m.is_watertight), "winding_consistent": bool(m.is_winding_consistent),
            "bodies": int(m.body_count), "euler": int(m.euler_number),
            "volume_cm3": round(float(m.volume) / 1000.0, 3), "size_mb": round(_size_mb(path), 1),
            "zmin": round(float(m.bounds[0][2]), 4), "zmax": round(float(m.bounds[1][2]), 3)}


def _size_mb(path):
    import os
    return os.path.getsize(path) / 1e6


def slot_checks(body):
    r = {}
    walls = [box(R_HUB, R_SLOT_OUT, -SLOT_W / 2, SLOT_W / 2, Z_SEAT, Z_HUB_TOP + 1.0) for _ in range(2)]
    walls[1] = rotz(walls[1], SLOT_PITCH)
    r["min_wall_between_adjacent_slots_mm"] = round(walls[0].distance(walls[1]), 3)
    r["wall_required_mm"] = MIN_WALL_BETWEEN_SLOTS
    r["wall_formula_at_inner_end_mm"] = round(2 * R_HUB * math.sin(math.radians(SLOT_PITCH / 2)) - SLOT_W, 3)
    # ช่องทั้ง 20 ต้องไม่เอียง (ขนานแนวรัศมี) และสมมาตร: ตรวจตำแหน่งศูนย์กลางของทุกช่อง
    ang_err = 0.0
    for k in range(N_SLOTS):
        c = rotz(box(R_HUB, R_SLOT_OUT, -SLOT_W / 2, SLOT_W / 2, Z_SEAT, Z_SEAT + 1), slot_angle(k)).Center()
        a = math.degrees(math.atan2(c.y, c.x)) % 360
        ang_err = max(ang_err, abs(((a - slot_angle(k) + 180) % 360) - 180))
    r["max_slot_center_angle_error_deg"] = round(ang_err, 6)
    # ผนังรอบรูสกรูล็อกเพลา = ระยะจากรูสกรูถึงร่องสไลด์ที่ใกล้ที่สุด
    hole = coupling_cutters()[-1] if SHAFT_TYPE != "THREADED_NUT" else None
    if hole is not None:
        slots = [rotz(box(R_HUB, R_SLOT_OUT, -SLOT_W / 2, SLOT_W / 2, Z_SEAT, Z_HUB_TOP + 1.0), slot_angle(k)) for k in (0, 1)]
        r["min_wall_around_set_screw_hole_mm"] = round(min(hole.distance(s) for s in slots), 3)
    return r


def slide_checks(body, ring_locked):
    slides = all_slides()
    comp = cq.Compound.makeCompound(slides)
    r = {"slides_vs_body_mm3": round(vol_int(body, comp), 6), "slides_vs_ring_mm3": round(vol_int(ring_locked, comp), 6)}
    pair = 0.0
    for k in range(N_SLOTS):
        pair += vol_int(slides[k], slides[(k + 1) % N_SLOTS])
    r["slide_vs_neighbour_slide_mm3"] = round(pair, 6)
    r["min_gap_between_neighbour_slides_mm"] = round(slides[0].distance(slides[1]), 3)
    r["slide_to_slot_wall_clearance_each_side_mm"] = round((SLOT_W - SLIDE_T) / 2, 3)
    r["slide_top_to_ring_gap_mm"] = round(Z_HUB_TOP - Z_SLIDE_TOP, 3)
    return r


def bayonet_checks(body, ring):
    def v(tw, lift):
        return vol_int(body, place_in_assembly(ring, tw, lift))
    t = BAYONET_TWIST
    res = {"unlocked_seated": v(-t, 0.0), "mid_twist": v(-t / 2, 0.0), "locked_seated": v(0.0, 0.0),
           "locked_lift_0.2mm_(free play)": v(0.0, 0.2), "locked_lift_0.5mm_(must block)": v(0.0, 0.5),
           "overrotate_+4deg_(must stop)": v(4.0, 0.0), "unlocked_lift_20mm_(must be free)": v(-t, 20.0)}
    res = {k: round(x, 5) for k, x in res.items()}
    res["pass"] = bool(res["unlocked_seated"] < EPS_VOL and res["mid_twist"] < EPS_VOL and res["locked_seated"] < EPS_VOL
                       and res["locked_lift_0.2mm_(free play)"] < EPS_VOL and res["unlocked_lift_20mm_(must be free)"] < EPS_VOL
                       and res["locked_lift_0.5mm_(must block)"] > 0.1 and res["overrotate_+4deg_(must stop)"] > 0.1)
    res["clearance_mm"] = BAYONET_CLEARANCE
    res["twist_deg"] = BAYONET_TWIST
    return res


def teeth_footprint_check(ring):
    """ซี่หวีต้องคร่อมขอบบนสไลด์เมื่อล็อก และไม่คร่อมแผ่นใดเลยเมื่อปลดล็อก (เหตุผลที่เลือกบิด 10 deg)"""
    slides = cq.Compound.makeCompound(all_slides())
    outer = cyl(R_TOOTH_OUT + 5, -1.0, RING_T + 1.0).cut(cyl(R_RING_BODY + 0.2, -2.0, RING_T + 2.0))
    teeth = ring.intersect(outer)                       # เฉพาะส่วนซี่หวีที่ยื่นพ้นตัวแหวน (frame ของแหวน)
    def overlap(twist):
        t = rotz(teeth, twist).translate(V(0, 0, Z_SLIDE_TOP - 2.0))   # ดันลงมาให้ซ้อนขอบบนสไลด์ 2 mm
        return round(vol_int(t, slides), 4)
    return {"teeth_over_slides_locked_mm3": overlap(0.0),
            "teeth_over_slides_unlocked_mm3": overlap(-BAYONET_TWIST)}


def drain_checks(body):
    """เดินจุดทดสอบตามเส้นทางระบาย: ร่องใต้ฐานต้องว่างตลอดถึงขอบ และหน้าต่างต้องทะลุจากพื้นร่องลงร่อง"""
    def solid_at(p):
        return body.isInside(V(*p))
    out = {}
    rows = []
    for k in (0, 7, 13):
        a = math.radians(slot_angle(k))
        ok = True
        for x in np.arange(WEEP_X[0][0], R_BASE + 1.0, 0.5):
            if solid_at((x * math.cos(a), x * math.sin(a), 1.0)) or solid_at((x * math.cos(a), x * math.sin(a), 2.0)):
                ok = False
        rows.append(ok)
    out["groove_open_to_rim_and_bottom_(slots 1,8,14)"] = all(rows)
    win = []
    for xa, xb in WEEP_X:
        xm = (xa + xb) / 2
        win.append(not solid_at((xm, 0.0, 8.0)) and not solid_at((xm, 0.0, 3.5)))
    out["weep_windows_open_floor_to_groove"] = all(win)
    bars = [solid_at(((w0[1] + w1[0]) / 2, 0.0, Z_SEAT - 1.0)) for w0, w1 in zip(WEEP_X[:-1], WEEP_X[1:])]
    bars.append(solid_at(((R_HUB + WEEP_X[0][0]) / 2, 0.0, Z_SEAT - 1.0)))
    out["support_bars_under_slide_present"] = all(bars)
    out["drain_section_mm"] = "%.1f x %.1f (45deg roof)" % (DRAIN_W, DRAIN_H)
    out["drain_count"] = N_SLOTS
    return out


def overhang_report(stl_path, limit_deg=45.0, bed_tol=0.02):
    """FDM overhang from the exported mesh. Faces whose normal points down more than `limit_deg`
    from vertical (excluding bed-contact faces at Z=0) need support/bridging. Grouped by Z level."""
    import trimesh
    m = trimesh.load(stl_path, force="mesh")
    n = m.face_normals
    areas = m.area_faces
    tri = m.triangles
    zc = tri[:, :, 2].mean(axis=1)
    zmin = tri[:, :, 2].min(axis=1)
    zmax = tri[:, :, 2].max(axis=1)
    flat = (zmax - zmin) < 1e-4
    sin_lim = math.sin(math.radians(limit_deg))
    steep = (-n[:, 2]) > sin_lim + 5e-3
    on_bed = zmax < bed_tol
    bad = steep & (~on_bed)
    groups = {}
    for i in np.where(bad)[0]:
        key = round(float(zc[i]), 1) if flat[i] else "slanted"
        g = groups.setdefault(key, [0.0, 0])
        g[0] += float(areas[i]); g[1] += 1
    rows = [{"z_mm": k, "area_mm2": round(v[0], 2), "triangles": v[1]} for k, v in sorted(groups.items(), key=lambda kv: -kv[1][0])]
    return {"limit_deg": limit_deg, "total_area_mm2": round(float(areas[bad].sum()), 2), "groups": rows[:12]}
