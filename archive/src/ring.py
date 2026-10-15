"""bayonet_comb_ring : top lock ring with 20 comb teeth + bayonet lugs (built in USE orientation:
bottom face at Z=0, top (flat, numbered) face at Z=RING_T, teeth radiate in-plane)."""
from params import *
from geom import *
from body_bayonet import lug_roof_z
from marks import ring_number_cutters


def lug():
    """เขี้ยวล็อก : ปลายบาง ฐานหนา — ผิวบนลาด 45 deg (พิมพ์กลับหัวไม่ต้อง support), ล้อกับเพดานร่อง L"""
    r_tip = R_RING_BORE - LUG_PROJ
    x_in = R_RING_BORE + 0.5                          # ฝังเข้าเนื้อแหวน
    z_tip = LUG_H - LUG_PROJ
    z_in = z_tip + (x_in - r_tip)
    return prism_xz_along_y([(r_tip, 0.0), (x_in, 0.0), (x_in, z_in), (r_tip, z_tip)], -LUG_W / 2, LUG_W / 2)


def build_bayonet_comb_ring(poly_glyph=False):
    body = cyl(R_RING_BODY, 0.0, RING_T).cut(cyl(R_RING_BORE, -1.0, RING_T + 1.0))
    tooth = box(R_TOOTH_IN, R_TOOTH_OUT, -TOOTH_W / 2, TOOTH_W / 2, 0.0, RING_T)
    teeth = polar_copies(tooth, N_SLOTS, SLOT_PITCH)                      # 20 ซี่ ตรงกับ 20 ช่อง
    lugs = polar_copies(lug(), N_BAYONET, 360.0 / N_BAYONET)
    ring = body.fuse(*teeth, *lugs).clean()
    ring = ring.cut(*ring_number_cutters(RING_T, poly_glyph)).clean()
    return ring


def to_print_orientation(ring):
    """พลิกกลับหัว 180 deg รอบแกน X : หน้าเรียบด้านบนวางบนพื้นพิมพ์ (Z=0), เขี้ยวล็อกอยู่ด้านบน."""
    flipped = ring.rotate(ORIGIN, V(1, 0, 0), 180.0)
    return flipped.translate(V(0, 0, RING_T))


def place_in_assembly(ring, twist_deg=0.0, lift=0.0):
    """twist_deg = 0 → ล็อกแล้ว ; -BAYONET_TWIST → ตำแหน่งปลดล็อก (เขี้ยวอยู่ที่ขาแนวดิ่ง)"""
    return rotz(ring, twist_deg).translate(V(0, 0, Z_HUB_TOP + lift))
