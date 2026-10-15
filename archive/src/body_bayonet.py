"""rotor_core_body - part 3/4 : bayonet L-slots on the top post (N_BAYONET positions, symmetric).

Unrolled picture of one L-slot (lug travels left -> right when twisting CCW viewed from top):

      post top ->   |   |
                    | V |        V = vertical entry leg  (width LUG_W + 2c)
                    |   |______
                    |    H     \\  H = horizontal (twist) leg, roof rises 45 deg outward -> prints w/o support
      floor (hub) ->'----------'

The lug on the ring has a matching 45-deg chamfer, so lifting the ring in the locked position
is blocked after only BAYONET_CLEARANCE of axial play.
"""
import math
from params import *
from geom import *


def lug_roof_z(r):
    """Height (above the floor) of the L-slot roof at radius r; 45 deg, = lug top + clearance."""
    r_tip = R_RING_BORE - LUG_PROJ                    # 12.3
    return (LUG_H - LUG_PROJ) + (r - r_tip) + BAYONET_CLEARANCE


def end_margin_deg():
    """มุมเผื่อปลายร่องล็อก ให้เขี้ยวไม่ชนผนังปลาย (clearance 0.30 บนผิวเขี้ยว)"""
    return math.degrees(math.asin((LUG_W / 2.0 + BAYONET_CLEARANCE) / R_GROOVE_FLOOR))


def bayonet_angles():
    """มุมของร่องแนวดิ่ง (ตำแหน่งปลดล็อก) ; ปลายร่องบิดอยู่ที่ +BAYONET_TWIST = ตรงกับมุมช่องสไลด์"""
    step = 360.0 / N_BAYONET
    return [-BAYONET_TWIST + i * step for i in range(N_BAYONET)]


def lslot_cutter(theta_v):
    w_s = LUG_W + 2 * BAYONET_CLEARANCE
    # ขาแนวดิ่ง : เสียบแหวนลงในแนวดิ่ง
    vert = box(R_GROOVE_FLOOR, R_POST + 1.0, -w_s / 2, w_s / 2, Z_HUB_TOP, Z_POST_TOP + 1.0)
    # ขาแนวนอน : บิดล็อก BAYONET_TWIST ; เพดานลาด 45 deg (teardrop)
    r_out = R_POST + 0.5
    prof = [(R_GROOVE_FLOOR, Z_HUB_TOP), (r_out, Z_HUB_TOP),
            (r_out, Z_HUB_TOP + lug_roof_z(r_out)), (R_GROOVE_FLOOR, Z_HUB_TOP + lug_roof_z(R_GROOVE_FLOOR))]
    horiz = revolve_rz(prof, BAYONET_TWIST + end_margin_deg())
    return rotz(vert.fuse(horiz), theta_v)


def bayonet_cutters():
    return [lslot_cutter(a) for a in bayonet_angles()]


def post_top_chamfer():
    """ลบคมยอดแกน 0.8 mm (lead-in ให้แหวนสวมง่าย)"""
    c = 0.8
    return revolve_rz([(R_POST - c, Z_POST_TOP + 0.01), (R_POST + 1.0, Z_POST_TOP + 0.01),
                       (R_POST + 1.0, Z_POST_TOP - c - 1.0), (R_POST, Z_POST_TOP - c)], 360.0)
