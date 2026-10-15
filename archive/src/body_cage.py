"""rotor_core_body - part 1/4 : base disk, solid hub, guide-plate cage, 20 radial slots, drains."""
from params import *
from geom import *


def slot_cutter(k=0):
    """Slot k: parallel-walled radial slot (0 deg tilt) + weep windows + teardrop drain groove."""
    hw = SLOT_W / 2.0
    parts = [box(R_HUB, R_SLOT_OUT, -hw, hw, Z_SEAT, Z_HUB_TOP + 1.0)]
    for xa, xb in WEEP_X:                       # หน้าต่างระบายทะลุพื้นร่องลงสู่ร่องใต้ฐาน
        parts.append(box(xa, xb, -hw, hw, 3.0, Z_SEAT + 0.01))
    rect_h = DRAIN_H - DRAIN_W / 2.0            # เพดานหน้าตัด 45 deg (teardrop)
    dw = DRAIN_W / 2.0
    groove = prism_yz_along_x(
        [(-dw, -0.5), (dw, -0.5), (dw, rect_h), (0.0, DRAIN_H), (-dw, rect_h)],
        WEEP_X[0][0] - 1.0, R_BASE + 2.0)
    parts.append(groove)
    cutter = parts[0].fuse(*parts[1:]).clean()
    return rotz(cutter, slot_angle(k)) if k else cutter


def seal_relief():
    """ร่องหลบซีลยาง/เบ้าลูกปืนใต้ฐาน : ยกขอบฐานดุม BOTTOM_SKIRT_CLEARANCE, ผนังนอก 45 deg พิมพ์ได้ไม่ต้อง support."""
    h = BOTTOM_SKIRT_CLEARANCE
    pts = [(R_BOSS, -0.5), (R_BOSS, h)]
    if RELIEF_FLAT > 1e-6:
        pts.append((R_BOSS + RELIEF_FLAT, h))
    pts += [(R_RELIEF_OUT, 0.0), (R_RELIEF_OUT + 0.5, -0.5)]
    return revolve_rz(pts)


def base_notches():
    """ร่องบาก (V-notch) บนขอบฐานตรงกลางแต่ละช่อง ; ช่องที่ 1 ใหญ่กว่าเป็น datum."""
    out = []
    for k in range(N_SLOTS):
        s = 1.5 if k == 0 else 1.0
        w, d = NOTCH_W * s, NOTCH_D * s
        n = prism_yz_along_x([(-w / 2, BASE_T + 0.01), (w / 2, BASE_T + 0.01), (0.0, BASE_T - d)],
                             R_END_OUT, R_BASE + 0.5)
        out.append(rotz(n, slot_angle(k)) if k else n)
    return out


def build_cage():
    base = cyl(R_BASE, 0.0, BASE_T)
    hub = cyl(R_HUB_FILL, 0.0, Z_HUB_TOP)
    box0 = box(R_HUB, R_END_OUT, -(SLOT_W / 2 + T_PLATE), SLOT_W / 2 + T_PLATE, BASE_T - 1.0, Z_CAGE_TOP)
    boxes = polar_copies(box0, N_SLOTS, SLOT_PITCH)
    post = cyl(R_POST, Z_HUB_TOP - 0.5, Z_POST_TOP)
    body = base.fuse(hub, post, *boxes).clean()
    cutters = [slot_cutter(k) for k in range(N_SLOTS)]
    body = body.cut(*cutters, seal_relief(), *base_notches()).clean()
    return body
