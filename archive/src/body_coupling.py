"""rotor_core_body - part 2/4 : reinforced central shaft mount (bore, lead-in, captive nut, set screw)."""
import math
import cadquery as cq
from params import *
from geom import *


def _hex_pts(af, z):
    """Hexagon with flats facing +/-X (local), across-flats = af."""
    rc = af / math.sqrt(3.0)
    return [V(rc * math.cos(math.radians(30 + 60 * i)), rc * math.sin(math.radians(30 + 60 * i)), z)
            for i in range(6)]


def _hex_prism(af, z0, z1, taper=0.0):
    f = cq.Face.makeFromWires(cq.Wire.makePolygon(_hex_pts(af, z0), close=True))
    return cq.Solid.extrudeLinear(f, V(0, 0, z1 - z0), taper)


def u_flat():
    """ตำแหน่งด้านเรียบที่สกรูกด (ระยะจากแกนเพลาตามทิศสกรู)."""
    if SHAFT_TYPE == "HEX_COUPLING":
        return SHAFT_HOLE_D / 2.0
    return D_FLAT_U


def _bore_d_shaft():
    rb, depth = SHAFT_HOLE_D / 2.0, SHAFT_BORE_DEPTH
    half = box(-rb - 3, D_FLAT_U, -rb - 3, rb + 3, -1.0, depth + rb + 2)
    body = cq.Solid.makeCylinder(rb, depth + 1.0, V(0, 0, -1.0), ZAXIS)
    ceil = cq.Solid.makeCone(rb, CONE_TIP_R, rb - CONE_TIP_R, V(0, 0, depth), ZAXIS)   # เพดานกรวย 45 deg (ตัดยอด)
    bore = body.fuse(ceil).intersect(half)
    # lead-in chamfer 1.0 x 45 deg ที่ปากรู (ส่วนโค้ง + ด้านเรียบ)
    L = BORE_LEADIN
    cone = cq.Solid.makeCone(rb + L + 0.5, rb, L + 0.5, V(0, 0, -0.5), ZAXIS)
    wedge = prism_xz_along_y([(-rb - 4, -0.5), (D_FLAT_U + L + 0.5, -0.5), (D_FLAT_U, L), (-rb - 4, L)],
                             -rb - 4, rb + 4)
    return bore.fuse(cone.intersect(wedge))


def _bore_hex():
    af, depth = SHAFT_HOLE_D, SHAFT_BORE_DEPTH
    L = BORE_LEADIN
    prism_ = _hex_prism(af, -1.0, depth)
    ceil = _hex_prism(af, depth, depth + af / 2.0 - CONE_TIP_R, taper=45.0)  # เพดานพีระมิด 45 deg (ตัดยอด)
    leadin = _hex_prism(af + 2 * (L + 0.5), -0.5, L, taper=45.0)
    return prism_.fuse(ceil, leadin)


def _bore_threaded_nut():
    rb, depth = SHAFT_HOLE_D / 2.0, SHAFT_BORE_DEPTH
    thru = cq.Solid.makeCylinder(rb, depth + 1.0, V(0, 0, -1.0), ZAXIS)
    ceil = cq.Solid.makeCone(rb, CONE_TIP_R, rb - CONE_TIP_R, V(0, 0, depth), ZAXIS)
    pocket = _hex_prism(NUT_AF + NUT_POCKET_CLEAR, -1.0, NUT_THICK + 0.5)   # นอตเหล็กฝังจากด้านล่าง
    return thru.fuse(ceil, pocket)


def coupling_cutters():
    """Return list of cutters (already placed at SET_SCREW_ANGLE)."""
    if SHAFT_TYPE == "D_SHAFT":
        cutters = [_bore_d_shaft()]
    elif SHAFT_TYPE == "HEX_COUPLING":
        cutters = [_bore_hex()]
    elif SHAFT_TYPE == "THREADED_NUT":
        return [rotz(_bore_threaded_nut(), SET_SCREW_ANGLE)]
    else:
        raise ValueError("SHAFT_TYPE must be D_SHAFT | HEX_COUPLING | THREADED_NUT")

    # ช่องนอตตัวเมีย M3 (ใส่จากด้านล่างดุม) เพดาน 45 deg
    u0 = u_flat() + NUT_WALL
    hw = CAPTIVE_NUT_WIDTH / 2.0
    zc = Z_SET_SCREW + 3.2 + 0.3                       # across-corners/2 + เผื่อ
    nut = prism_yz_along_x([(-hw, -0.5), (hw, -0.5), (hw, zc), (0.0, zc + hw), (-hw, zc)],
                           u0, u0 + CAPTIVE_NUT_THICKNESS)
    # รูสกรูตัวหนอน M3 จากร่องระหว่างช่องด้านนอก พุ่งเข้าหาด้านเรียบ (ตัดไม่ให้เลยผิวดุม)
    hole = teardrop_along_x(SET_SCREW_DIA / 2.0, Z_SET_SCREW, u_flat() - 1.0, R_HUB_FILL + 3.0)
    hole = hole.intersect(cyl(R_HUB_FILL, Z_SEAT, Z_SEAT + 20.0))
    return [rotz(c, SET_SCREW_ANGLE) for c in cutters + [nut, hole]]
