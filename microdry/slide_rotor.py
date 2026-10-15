"""MicroDry-Safe — 20-slot radial slide rotor for a Simplus 2L 300 W chopper (glass jar).

Parts (units: mm, Z = 0 at the inside floor of the jar, everything modelled in its working position):
  rotor_body      shaft (pin bore at the bottom, 8-tooth gear socket at the top) + lower slotted disc
  rotor_top_ring  slotted top ring, slides down over the neck, locked on a hex by two M3 grub screws in heat-set inserts;
                  pair numbers 1..10 engraved on disc and ring (same number = opposite slots)

Machine / material values that must be measured live in params.yaml (tagged estimated / measured).
Design values live in the DESIGN block below.

Run:  ../.venv/Scripts/python slide_rotor.py            (build + checks + export + previews)
      ../.venv/Scripts/python slide_rotor.py --no-render
"""
import json
import math
import os
import sys

import cadquery as cq
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")

# ----------------------------------------------------------------------------------------------
# Measured / estimated machine values (params.yaml)
# ----------------------------------------------------------------------------------------------
with open(os.path.join(HERE, "params.yaml"), encoding="utf-8") as fh:
    P = yaml.safe_load(fh)

JAR_BOTTOM_D = P["jar"]["bottom_inner_d"]
JAR_MOUTH_D = P["jar"]["mouth_inner_d"]
JAR_H = P["jar"]["inner_height"]                 # floor -> underside of lid
PIN_D = P["jar"]["center_pin_d"]
PIN_H = P["jar"]["center_pin_h"]
FLOOR_BOSS_D = P["jar"]["floor_boss_d"]
FLOOR_BOSS_H = P["jar"]["floor_boss_h"]
LID_HOLE_D = P["lid"]["hole_d"]
LID_T = P["lid"]["thickness"]
ORIG_SHAFT_LEN = P["original_shaft"]["length"]
SHAFT_Z0 = P["original_shaft"]["bottom_gap"]     # shaft bottom height above the floor
PIN_BORE_DEPTH = P["original_shaft"]["pin_bore_depth"]
GEAR_OD = P["gear_head"]["outer_d"]
GEAR_ROOT_D = P["gear_head"]["root_d"]
GEAR_TEETH = int(P["gear_head"]["teeth"])
GEAR_TOOTH_W = P["gear_head"]["tooth_w"]
GEAR_LEN = P["gear_head"]["length"]
DRIVE_METHOD = P["gear_head"]["drive_method"]
PIN_CLEAR = P["fit"]["pin_bore_clear"]
SOCKET_CLEAR = (P["fit"]["socket_clear_metal_insert"] if DRIVE_METHOD == "metal_insert"
                else P["fit"]["socket_clear_printed"])
HEX_CLEAR = P["fit"]["hex_clear"]
SLIDE_L = P["slide"]["length"]
SLIDE_W = P["slide"]["width"]
SLIDE_T_MIN = P["slide"]["thickness_min"]
SLIDE_T_MAX = P["slide"]["thickness_max"]
SLIDE_MASS_G = P["slide"]["mass_g"]
INSERT_OD = P["hardware"]["insert_od"]
INSERT_LEN = P["hardware"]["insert_len"]
INSERT_HOLE_D = P["hardware"]["insert_hole_d"]
GRUB_LEN = P["hardware"]["grub_len"]
RPM_NOMINAL = P["machine"]["rpm_nominal"]
DENSITY = P["material"]["density"]

# ----------------------------------------------------------------------------------------------
# DESIGN values
# ----------------------------------------------------------------------------------------------
N_SLOTS = 20
R_IN = 18.0                     # inner end of every slot
R_OUT = R_IN + 26.0             # outer end of every slot (slide outer edge bears here under load)
DISC_R = R_OUT + 3.0            # outer radius of disc and ring -> OD 94
SLOT_GAP = 0.6                  # slot width over the THICKEST slide
SLOT_W = SLIDE_T_MAX + SLOT_GAP
HUB_D = 32.0                    # hub boss on the disc; leaves R_IN - HUB_D/2 = 2 mm to the slots
HUB_H = 6.0                     # hub boss height above the disc, then a 45 deg cone to the shaft
FLOOR_CLEAR = 6.0               # disc underside above the jar floor
DISC_FLOOR_T = 3.0              # plastic under the slide (drain holes go through it)
DISC_SLOT_DEPTH = 5.0           # slide engagement in the disc
DISC_LEADIN = 0.6               # 45 deg lead-in on the disc slots (blind entry)
SHAFT_D = 22.0                  # main shaft between disc and ring; its top face is the ring seat
HEX_AF = 16.0                   # hex across flats (ring lock)
NECK_D = 15.0                   # neck above the ring, passes through the lid
SLIDE_EXPOSED = 10.0            # slide length standing above the top face of the ring (finger grip)
RING_T = 6.0                    # ring plate thickness (slide engagement in the ring)
RING_LEADIN = 1.0               # 45 deg lead-in on the ring slots
RING_BOSS_D = HUB_D             # boss that carries the M3 grub screws
RING_BOSS_H = 8.0
INSERT_POCKET_EXTRA = 0.5       # insert pocket deeper than the insert (room for displaced plastic)
M3_CLEAR_D = 3.2                # grub screw passage between insert pocket and hex bore
LABEL_FONT = 4.0                # pair numbers 1..10 on disc and ring top faces (slot k and k+10 share a number)
LABEL_DEPTH = 0.6               # engraving depth (3 layers at 0.2)
LABEL_R = 41.0                  # label centre radius (outside the vent holes)
LABEL_GAP = 1.0                 # label edge to the lead-in edge of its own slot
DRAIN_D = 2.4                   # round drain holes in every slot floor
DRAIN_R = (22.0, 31.0, 40.0)    # radii of the drain holes in each slot
VENT_D = 4.0                    # holes between slots (disc and ring)
VENT_R = 36.0
SOCKET_EXTRA = 0.5              # socket deeper than the gear head
MIN_SIDE_CLEAR = 5.0            # rotor OD to jar wall, per side
MIN_LID_CLEAR = 5.0             # slide tip / ring boss to underside of lid
MIN_SLOT_WALL = 3.0             # plastic between adjacent slots at R_IN
MIN_NECK_LID_CLEAR = 1.0        # neck to lid hole, per side

# Derived Z stack
DISC_Z0 = FLOOR_CLEAR
SLIDE_Z0 = DISC_Z0 + DISC_FLOOR_T                    # slot floor = slide bottom
DISC_Z1 = SLIDE_Z0 + DISC_SLOT_DEPTH
SLIDE_TOP = SLIDE_Z0 + SLIDE_L
RING_Z1 = SLIDE_TOP - SLIDE_EXPOSED
RING_Z0 = RING_Z1 - RING_T
BOSS_Z1 = RING_Z1 + RING_BOSS_H
SHAFT_TOP = SHAFT_Z0 + ORIG_SHAFT_LEN                # same top as the original shaft
LID_Z = JAR_H
SLOT_PITCH = 360.0 / N_SLOTS
PIN_BORE_R = PIN_D / 2 + PIN_CLEAR
SOCKET_DEPTH = GEAR_LEN + SOCKET_EXTRA
SCREW_Z = (RING_Z1 + BOSS_Z1) / 2                    # grub screw axis height (mid boss)
BOSS_WALL = RING_BOSS_D / 2 - (HEX_AF / 2 + HEX_CLEAR)  # boss outer face -> hex bore flat
INSERT_POCKET = INSERT_LEN + INSERT_POCKET_EXTRA
SLIDE_R0 = R_IN + ((R_OUT - R_IN) - SLIDE_W) / 2     # slide inner edge radius


def jar_inner_r(z):
    return (JAR_BOTTOM_D + (JAR_MOUTH_D - JAR_BOTTOM_D) * z / JAR_H) / 2


def slot_wall_at(r, w=SLOT_W, pitch=SLOT_PITCH):
    """Plastic between two adjacent straight radial slots, measured from the inner corner of one slot
    to the near side wall of the next one."""
    a = math.radians(pitch)
    return r * math.sin(a) - (w / 2) * math.cos(a) - w / 2


def hole_to_slot_wall(r_hole, d_hole, angle_from_slot_deg):
    return r_hole * math.sin(math.radians(angle_from_slot_deg)) - d_hole / 2 - SLOT_W / 2


# ----------------------------------------------------------------------------------------------
# Design rules. STOP_ASK rules mean "do not auto-fix, ask the owner first".
# ----------------------------------------------------------------------------------------------
def design_checks():
    od = 2 * DISC_R
    c = []

    def rule(name, value, ok, need, stop_ask=False):
        c.append({"rule": name, "value": round(value, 3), "need": need, "ok": bool(ok), "stop_ask": stop_ask})

    rule("rotor OD + 2x%.0f < jar bottom inner D" % MIN_SIDE_CLEAR, od + 2 * MIN_SIDE_CLEAR,
         od + 2 * MIN_SIDE_CLEAR < JAR_BOTTOM_D, "< %.1f" % JAR_BOTTOM_D, True)
    rule("rotor OD <= 94", od, od <= 94.0, "<= 94")
    rule("slide tip below lid", LID_Z - SLIDE_TOP, LID_Z - SLIDE_TOP >= MIN_LID_CLEAR, ">= %.1f" % MIN_LID_CLEAR, True)
    rule("ring boss top below lid", LID_Z - BOSS_Z1, LID_Z - BOSS_Z1 >= MIN_LID_CLEAR, ">= %.1f" % MIN_LID_CLEAR, True)
    rule("neck to lid hole, per side", (LID_HOLE_D - NECK_D) / 2,
         (LID_HOLE_D - NECK_D) / 2 >= MIN_NECK_LID_CLEAR, ">= %.1f" % MIN_NECK_LID_CLEAR, True)
    rule("shaft top not above original shaft top", SHAFT_TOP - (SHAFT_Z0 + ORIG_SHAFT_LEN),
         SHAFT_TOP <= SHAFT_Z0 + ORIG_SHAFT_LEN + 1e-9, "<= 0")
    rule("slot gap, thickest slide", SLOT_W - SLIDE_T_MAX, 0.5 - 1e-9 <= SLOT_W - SLIDE_T_MAX <= 0.8 + 1e-9, "0.5..0.8")
    rule("slot gap, thinnest slide", SLOT_W - SLIDE_T_MIN, 0.5 - 1e-9 <= SLOT_W - SLIDE_T_MIN <= 0.8 + 1e-9, "0.5..0.8")
    rule("slot length over slide width", (R_OUT - R_IN) - SLIDE_W, (R_OUT - R_IN) - SLIDE_W >= 0.4, ">= 0.4")
    rule("plastic between slots at R_IN", slot_wall_at(R_IN), slot_wall_at(R_IN) >= MIN_SLOT_WALL, ">= %.1f" % MIN_SLOT_WALL)
    rule("hub edge to slots", R_IN - HUB_D / 2, R_IN - HUB_D / 2 >= 2.0, ">= 2.0")
    rule("vent hole to slot wall", hole_to_slot_wall(VENT_R, VENT_D, SLOT_PITCH / 2),
         hole_to_slot_wall(VENT_R, VENT_D, SLOT_PITCH / 2) >= 2.0, ">= 2.0")
    rule("drain hole to drain hole (innermost)", 2 * DRAIN_R[0] * math.sin(math.radians(SLOT_PITCH / 2)) - DRAIN_D,
         2 * DRAIN_R[0] * math.sin(math.radians(SLOT_PITCH / 2)) - DRAIN_D >= 2.0, ">= 2.0")
    # slide stability: ring must sit high enough on the slide (two supports far apart)
    span = RING_Z1 - SLIDE_Z0
    rule("top support height / slide length", span / SLIDE_L, span / SLIDE_L >= 2 / 3, ">= 0.667", True)
    rule("gap disc top -> ring bottom", RING_Z0 - DISC_Z1, RING_Z0 - DISC_Z1 >= 30.0, ">= 30", True)
    rule("pin top below pin bore top", (SHAFT_Z0 + PIN_BORE_DEPTH) - PIN_H, PIN_H < SHAFT_Z0 + PIN_BORE_DEPTH, "> 0", True)
    rule("shaft bottom above floor boss", SHAFT_Z0 - FLOOR_BOSS_H, SHAFT_Z0 > FLOOR_BOSS_H, "> 0", True)
    rule("socket wall in neck", (NECK_D - GEAR_OD) / 2 - SOCKET_CLEAR, (NECK_D - GEAR_OD) / 2 - SOCKET_CLEAR >= 2.0, ">= 2.0")
    rule("ring passes over neck (hex inscribed > neck)", HEX_AF - NECK_D, HEX_AF > NECK_D, "> 0")
    rule("ring seat width on shaft shoulder (min)", SHAFT_D / 2 - (HEX_AF / 2 + HEX_CLEAR) / math.cos(math.pi / 6),
         SHAFT_D / 2 - (HEX_AF / 2 + HEX_CLEAR) / math.cos(math.pi / 6) >= 1.0, ">= 1.0")
    rule("boss to slide inner edge", R_IN - RING_BOSS_D / 2, R_IN - RING_BOSS_D / 2 >= 2.0, ">= 2.0")
    # heat-set insert in the ring boss
    rule("insert pocket stop before hex bore", BOSS_WALL - INSERT_POCKET, BOSS_WALL - INSERT_POCKET >= 1.0, ">= 1.0")
    rule("insert hole over insert OD (melt-in interference)", INSERT_OD - INSERT_HOLE_D,
         0.3 <= INSERT_OD - INSERT_HOLE_D <= 0.8, "0.3..0.8")
    rule("plastic above insert", BOSS_Z1 - (SCREW_Z + INSERT_OD / 2), BOSS_Z1 - (SCREW_Z + INSERT_OD / 2) >= 1.5, ">= 1.5")
    # grub tip on the shaft hex flat (r = HEX_AF/2): thread engagement in the insert and head below the slide
    engage = min(RING_BOSS_D / 2, HEX_AF / 2 + GRUB_LEN) - (RING_BOSS_D / 2 - INSERT_LEN)
    rule("grub thread engagement in insert", engage, engage >= 3.0, ">= 3.0")
    proud = HEX_AF / 2 + GRUB_LEN - RING_BOSS_D / 2
    rule("grub head proud of boss vs slide inner edge", SLIDE_R0 - RING_BOSS_D / 2 - proud,
         SLIDE_R0 - RING_BOSS_D / 2 - proud >= 1.0, ">= 1.0")
    for z, r in ((DISC_Z0, DISC_R), (RING_Z1, DISC_R)):
        rule("radial clearance to jar at Z=%.0f" % z, jar_inner_r(z) - r, jar_inner_r(z) - r >= MIN_SIDE_CLEAR,
             ">= %.1f" % MIN_SIDE_CLEAR, True)
    return c


def enforce(checks):
    bad = [x for x in checks if not x["ok"]]
    for x in bad:
        print("  FAIL %s: %s (need %s)%s" % (x["rule"], x["value"], x["need"], "  -> STOP, ask owner" if x["stop_ask"] else ""))
    assert not bad, "design rule(s) failed, see above"


# ----------------------------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------------------------
Z_AXIS = cq.Vector(0, 0, 1)
ORIGIN = cq.Vector(0, 0, 0)


def revolve(pts):
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()


def rot(shape, deg):
    return shape.rotate(ORIGIN, Z_AXIS, deg)


def hex_prism(af, z0, h):
    rv = af / math.sqrt(3)   # vertex radius; vertices at 30 + 60k deg -> flat normals at 0, 60, ... deg
    pts = [(rv * math.cos(math.radians(30 + 60 * k)), rv * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(h).val()


def slot_cutter(z0, z1, leadin, z_top):
    """Straight radial slot along +X (R_IN..R_OUT) from z0 up through z1, with a 45 deg lead-in at z_top."""
    box = cq.Solid.makeBox(R_OUT - R_IN, SLOT_W, z1 - z0, pnt=cq.Vector(R_IN, -SLOT_W / 2, z0))
    if leadin <= 0:
        return box
    xc, L = (R_IN + R_OUT) / 2, R_OUT - R_IN
    funnel = (cq.Workplane("XY", origin=(xc, 0, z_top - leadin)).rect(L, SLOT_W)
              .workplane(offset=2 * leadin).rect(L + 4 * leadin, SLOT_W + 4 * leadin).loft().val())
    return box.fuse(funnel)


def circular(shape, n, start_deg=0.0):
    return [rot(shape, start_deg + k * 360.0 / n) for k in range(n)]


def gear_socket(z_top, depth, clear):
    """Female 8-tooth socket opening at z_top, going down `depth`, with a 0.5 mm 45 deg entry chamfer."""
    z0 = z_top - depth
    h = depth + 1.0
    core = cq.Solid.makeCylinder(GEAR_ROOT_D / 2 + clear, h, cq.Vector(0, 0, z0))
    tw = GEAR_TOOTH_W + 2 * clear
    tooth = cq.Solid.makeBox(GEAR_OD / 2 + clear, tw, h, pnt=cq.Vector(0, -tw / 2, z0))
    s = core.fuse(*circular(tooth, GEAR_TEETH))
    r_mouth = GEAR_OD / 2 + clear
    chamfer = cq.Solid.makeCone(r_mouth, r_mouth + 1.0, 1.0, cq.Vector(0, 0, z_top - 0.5))
    return s.fuse(chamfer).clean()


def pin_bore(z_bottom, depth, r):
    c = 0.8   # entry chamfer
    return revolve([(0, z_bottom - 0.5), (r + c + 0.5, z_bottom - 0.5), (r, z_bottom + c),
                    (r, z_bottom + depth), (0.5, z_bottom + depth + r - 0.5),   # 45 deg cone roof, prints w/o
                    (0, z_bottom + depth + r - 0.5)])                         # support; flat tip keeps STL closed


def slot_labels(z_face, leadin):
    """Pair numbers engraved in a top face. Slot k and slot k + N/2 (180 deg apart) carry the same number,
    so loading both slots of a number keeps the rotor balanced. Each label reads outward along its slot and
    hugs the CCW side of it (LABEL_GAP from the slot's lead-in edge)."""
    cutters = []
    for k in range(N_SLOTS):
        num = k % (N_SLOTS // 2) + 1
        txt = "%d." % num if num in (6, 9) else str(num)    # labels are seen from every side: 6. vs 9.
        t = cq.Workplane("XY").text(txt, LABEL_FONT, LABEL_DEPTH + 1.0, combine=False,
                                    kind="bold", halign="center", valign="center").val()
        bb = t.BoundingBox()
        y_off = SLOT_W / 2 + leadin + LABEL_GAP + bb.ylen / 2
        t = t.translate(cq.Vector(LABEL_R - (bb.xmin + bb.xmax) / 2, y_off - (bb.ymin + bb.ymax) / 2,
                                  z_face - LABEL_DEPTH - bb.zmin))
        cutters.append(rot(t, k * SLOT_PITCH))
    return cutters


def insert_pockets():
    """Two M3 heat-set insert pockets in the ring boss (0 and 180 deg, on hex flat normals), each with a
    0.5 mm entry chamfer and an M3 clearance hole on to the hex bore."""
    r_face, z = RING_BOSS_D / 2, SCREW_Z
    x_dir = cq.Vector(1, 0, 0)
    pocket = cq.Solid.makeCylinder(INSERT_HOLE_D / 2, INSERT_POCKET + 1.0, cq.Vector(r_face - INSERT_POCKET, 0, z), x_dir)
    chamfer = cq.Solid.makeCone(INSERT_HOLE_D / 2, INSERT_HOLE_D / 2 + 1.0, 1.0, cq.Vector(r_face - 0.5, 0, z), x_dir)
    passage = cq.Solid.makeCylinder(M3_CLEAR_D / 2, r_face, cq.Vector(0, 0, z), x_dir)
    one = pocket.fuse(chamfer, passage).clean()
    return [one, rot(one, 180)]


def rim_notches(r, z0, z1):
    """Two V alignment notches (0 and 180 deg) on an outer rim, 1 mm deep."""
    s = 1.0 * math.sqrt(2)
    b = cq.Solid.makeBox(s, s, z1 - z0 + 2, pnt=cq.Vector(-s / 2, -s / 2, z0 - 1))
    b = b.rotate(ORIGIN, Z_AXIS, 45).translate(cq.Vector(r, 0, 0))
    return [b, rot(b, 180)]


# ----------------------------------------------------------------------------------------------
# Parts
# ----------------------------------------------------------------------------------------------
def build_rotor_body():
    r_sh, r_hub, r_neck = SHAFT_D / 2, HUB_D / 2, NECK_D / 2
    lower = revolve([
        (0, SHAFT_Z0), (r_sh - 1.0, SHAFT_Z0), (r_sh, SHAFT_Z0 + 1.0),           # shaft stub, 1 mm chamfer
        (r_sh, DISC_Z0), (DISC_R - 0.8, DISC_Z0), (DISC_R, DISC_Z0 + 0.8),       # disc underside
        (DISC_R, DISC_Z1 - 0.5), (DISC_R - 0.5, DISC_Z1),                        # disc rim
        (r_hub, DISC_Z1), (r_hub, DISC_Z1 + HUB_H),                              # hub boss
        (r_sh, DISC_Z1 + HUB_H + (r_hub - r_sh)),                                # 45 deg cone to shaft
        (r_sh, RING_Z0), (0, RING_Z0)])                                          # ring seat (shoulder)
    hexp = hex_prism(HEX_AF, RING_Z0, BOSS_Z1 - RING_Z0)
    neck = revolve([(0, BOSS_Z1 - 0.01), (r_neck, BOSS_Z1 - 0.01), (r_neck, SHAFT_TOP - 0.5),
                    (r_neck - 0.5, SHAFT_TOP), (0, SHAFT_TOP)])
    body = lower.fuse(hexp, neck).clean()

    cutters = [pin_bore(SHAFT_Z0, PIN_BORE_DEPTH, PIN_BORE_R),
               gear_socket(SHAFT_TOP, SOCKET_DEPTH, SOCKET_CLEAR)]
    cutters += circular(slot_cutter(SLIDE_Z0, DISC_Z1 + 1, DISC_LEADIN, DISC_Z1), N_SLOTS)
    drain = [cq.Solid.makeCylinder(DRAIN_D / 2, DISC_FLOOR_T + 2, cq.Vector(r, 0, DISC_Z0 - 1)) for r in DRAIN_R]
    for d in drain:
        cutters += circular(d, N_SLOTS)
    vent = cq.Solid.makeCylinder(VENT_D / 2, DISC_Z1 - DISC_Z0 + 2, cq.Vector(VENT_R, 0, DISC_Z0 - 1))
    cutters += circular(vent, N_SLOTS, SLOT_PITCH / 2)
    cutters += rim_notches(DISC_R, DISC_Z0, DISC_Z1)
    cutters += slot_labels(DISC_Z1, DISC_LEADIN)
    return body.cut(*cutters).clean()


def build_top_ring():
    plate = revolve([(HUB_D / 4, RING_Z0), (DISC_R - 0.5, RING_Z0), (DISC_R, RING_Z0 + 0.5),
                     (DISC_R, RING_Z1 - 0.5), (DISC_R - 0.5, RING_Z1),
                     (RING_BOSS_D / 2, RING_Z1), (RING_BOSS_D / 2, BOSS_Z1 - 0.5),
                     (RING_BOSS_D / 2 - 0.5, BOSS_Z1), (HUB_D / 4, BOSS_Z1)])
    cutters = [hex_prism(HEX_AF + 2 * HEX_CLEAR, RING_Z0 - 1, BOSS_Z1 - RING_Z0 + 2)]
    cutters += circular(slot_cutter(RING_Z0 - 1, RING_Z1 + 1, RING_LEADIN, RING_Z1), N_SLOTS)
    vent = cq.Solid.makeCylinder(VENT_D / 2, RING_T + 2, cq.Vector(VENT_R, 0, RING_Z0 - 1))
    cutters += circular(vent, N_SLOTS, SLOT_PITCH / 2)
    cutters += insert_pockets()
    cutters += rim_notches(DISC_R, RING_Z0, RING_Z1)
    cutters += slot_labels(RING_Z1, RING_LEADIN)
    return plate.cut(*cutters).clean()


def build_slides(t=SLIDE_T_MAX):
    """Dummy glass slides, centred in their slots (worst case = thickest slide)."""
    r0 = R_IN + ((R_OUT - R_IN) - SLIDE_W) / 2
    s = cq.Solid.makeBox(SLIDE_W, t, SLIDE_L, pnt=cq.Vector(r0, -t / 2, SLIDE_Z0))
    return circular(s, N_SLOTS)


def build_fit_test():
    """Shortest piece that carries both machine interfaces: pin bore (bottom) and gear socket (top),
    separated by a 1 mm web. Printed pin-bore-down; Z = 0 on the bed."""
    web = 1.0
    z_step = PIN_BORE_DEPTH + PIN_BORE_R + web            # above the bore's cone roof
    top = z_step + SOCKET_DEPTH + web
    r_sh, r_neck = SHAFT_D / 2, NECK_D / 2
    blank = revolve([(0, 0), (r_sh - 1.0, 0), (r_sh, 1.0), (r_sh, z_step), (r_neck, z_step),
                     (r_neck, top - 0.5), (r_neck - 0.5, top), (0, top)])
    return blank.cut(pin_bore(0, PIN_BORE_DEPTH, PIN_BORE_R), gear_socket(top, SOCKET_DEPTH, SOCKET_CLEAR)).clean()


def build_jar_dummy():
    rb, rm, w = JAR_BOTTOM_D / 2, JAR_MOUTH_D / 2, 4.0
    jar = revolve([(0, -w), (rb + w, -w), (rm + w, JAR_H), (rm, JAR_H), (rb, 0), (0, 0)])
    pin = cq.Solid.makeCylinder(PIN_D / 2, PIN_H + 0.01, cq.Vector(0, 0, -0.01))
    parts = [jar, pin]
    if FLOOR_BOSS_H > 0 and FLOOR_BOSS_D > 0:
        parts.append(cq.Solid.makeCylinder(FLOOR_BOSS_D / 2, FLOOR_BOSS_H + 0.01, cq.Vector(0, 0, -0.01)))
    jar = parts[0].fuse(*parts[1:]).clean()
    lid = revolve([(LID_HOLE_D / 2, LID_Z), (rm + w, LID_Z), (rm + w, LID_Z + LID_T), (LID_HOLE_D / 2, LID_Z + LID_T)])
    return jar, lid


# ----------------------------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------------------------
def rcf(r_mm, rpm):
    return 1.118e-5 * (r_mm / 10.0) * rpm ** 2


def rcf_table():
    rows = []
    r_in = R_IN + ((R_OUT - R_IN) - SLIDE_W) / 2
    r_out = R_OUT
    print("\nRCF at the slide edges (RCF = 1.118e-5 x r[cm] x rpm^2)")
    print("   rpm | inner edge r=%.1f mm | outer edge r=%.1f mm" % (r_in, r_out))
    for rpm in (500, 1000, 1500, 2000, 2800, 3500):
        a, b = rcf(r_in, rpm), rcf(r_out, rpm)
        rows.append({"rpm": rpm, "rcf_inner_g": round(a, 1), "rcf_outer_g": round(b, 1)})
        print("  %4d | %8.1f g          | %8.1f g" % (rpm, a, b))
    return rows


def common_volume(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return float("nan")


def geometry_checks(body, ring, slides, jar, lid):
    res = {}
    res["body_solids"] = len(body.Solids())
    res["ring_solids"] = len(ring.Solids())
    res["body_valid"] = body.isValid()
    res["ring_valid"] = ring.isValid()
    sl = cq.Compound.makeCompound(slides)
    res["slides_x_body_mm3"] = common_volume(sl, body)
    res["slides_x_ring_mm3"] = common_volume(sl, ring)
    res["slide_x_neighbour_mm3"] = common_volume(slides[0], slides[1])
    res["ring_x_body_mm3"] = common_volume(ring, body)
    rot_parts = cq.Compound.makeCompound([body, ring] + slides)
    res["rotor_x_jar_mm3"] = common_volume(rot_parts, jar)
    res["rotor_x_lid_mm3"] = common_volume(rot_parts, lid)
    # contact = nothing floating: ring rests on the shoulder, every slide rests on its slot floor
    res["ring_to_body_gap_mm"] = ring.distance(body)
    res["slide_to_body_gap_mm"] = max(s.distance(body) for s in slides)
    res["slide_to_ring_gap_mm"] = min(s.distance(ring) for s in slides)
    res["slide_to_slide_gap_mm"] = slides[0].distance(slides[1])
    # measured (not formula) plastic between two adjacent slots at R_IN
    a = slot_cutter(SLIDE_Z0, DISC_Z1, 0, DISC_Z1)
    res["slot_wall_measured_mm"] = a.distance(rot(a, SLOT_PITCH))
    # label 1 (slot 0) to its own slot, the next slot and the vent between them, at the face it is cut into
    vent = rot(cq.Solid.makeCylinder(VENT_D / 2, 200, cq.Vector(VENT_R, 0, 0)), SLOT_PITCH / 2)
    for name, z, li in (("disc", DISC_Z1, DISC_LEADIN), ("ring", RING_Z1, RING_LEADIN)):
        below = cq.Solid.makeBox(200, 200, 10, pnt=cq.Vector(-100, -100, z - 10))   # only what is cut into the part
        lab = slot_labels(z, li)[0].intersect(below)
        s0 = slot_cutter(z - 10, z + 1, li, z).intersect(below)
        res["label_%s_to_own_slot_mm" % name] = round(lab.distance(s0), 3)
        res["label_%s_to_next_slot_mm" % name] = round(lab.distance(rot(s0, SLOT_PITCH)), 3)
        res["label_%s_to_vent_mm" % name] = round(lab.distance(vent), 3)
    return res


# ----------------------------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------------------------
def export_all(body, ring, slides, fit):
    for d in ("step", "stl"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    step = lambda n: os.path.join(OUT, "step", n + ".step")
    stl = lambda n: os.path.join(OUT, "stl", n + ".stl")

    cq.exporters.export(body, step("rotor_body"))
    cq.exporters.export(ring, step("rotor_top_ring"))
    asm = cq.Assembly(name="rotor_assembly")
    asm.add(body, name="rotor_body", color=cq.Color(0.20, 0.45, 0.80))
    asm.add(ring, name="rotor_top_ring", color=cq.Color(0.95, 0.55, 0.15))
    for i, s in enumerate(slides):
        asm.add(s, name="slide_%02d" % (i + 1), color=cq.Color(0.75, 0.90, 0.95, 0.6))
    asm.export(step("rotor_assembly"))

    # STL in print orientation, lowest point on Z = 0
    tol, ang = 0.01, 0.05
    bb = body.BoundingBox()
    cq.exporters.export(body.translate(cq.Vector(0, 0, -bb.zmin)), stl("rotor_body"), tolerance=tol, angularTolerance=ang)
    cq.exporters.export(ring.translate(cq.Vector(0, 0, -RING_Z0)), stl("rotor_top_ring"), tolerance=tol, angularTolerance=ang)
    cq.exporters.export(fit, stl("fit_test"), tolerance=tol, angularTolerance=ang)
    cq.exporters.export(fit, step("fit_test"))

    import trimesh
    mesh = {}
    for n in ("rotor_body", "rotor_top_ring", "fit_test"):
        m = trimesh.load(stl(n))
        mesh[n] = {"triangles": len(m.faces), "watertight": bool(m.is_watertight),
                   "bodies": len(m.split(only_watertight=False)), "volume_cm3": round(m.volume / 1000, 2),
                   "zmin": round(float(m.bounds[0][2]), 3), "size_mm": [round(float(x), 2) for x in m.extents]}
    return mesh


# ----------------------------------------------------------------------------------------------
# Previews (matplotlib, shaded)
# ----------------------------------------------------------------------------------------------
def _tris(shape, tol=0.25):
    import numpy as np
    v, t = shape.tessellate(tol, 0.3)
    v = np.array([(p.x, p.y, p.z) for p in v])
    return v[np.array(t)]


def render_previews(body, ring, slides, jar, lid):
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from matplotlib.collections import PolyCollection
    os.makedirs(os.path.join(OUT, "png"), exist_ok=True)
    light = np.array([0.4, -0.5, 0.75]); light /= np.linalg.norm(light)

    def shaded(tris, rgb, alpha=1.0):
        n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
        n /= np.linalg.norm(n, axis=1)[:, None] + 1e-12
        k = 0.35 + 0.65 * np.abs(n @ light)
        return np.clip(np.array(rgb)[None, :] * k[:, None], 0, 1), alpha

    parts = [(body, (0.25, 0.5, 0.85), 1.0), (ring, (0.95, 0.6, 0.2), 1.0),
             (cq.Compound.makeCompound(slides), (0.6, 0.85, 0.9), 0.55)]
    meshes = [(_tris(s), c, a) for s, c, a in parts]

    def view3d(fname, elev, azim, title):
        fig = plt.figure(figsize=(9, 9), dpi=130)
        ax = fig.add_subplot(111, projection="3d")
        # one collection for all parts, so matplotlib depth-sorts per triangle and not per part
        all_t, all_c = [], []
        for tris, rgb, alpha in meshes:
            fc, a = shaded(tris, rgb, alpha)
            all_t.append(tris)
            all_c.append(np.hstack([fc, np.full((len(fc), 1), a)]))
        ax.add_collection3d(Poly3DCollection(np.vstack(all_t), facecolors=np.vstack(all_c), edgecolors="none"))
        R = DISC_R + 3
        ax.set_xlim(-R, R); ax.set_ylim(-R, R); ax.set_zlim(0, SHAFT_TOP)
        ax.set_box_aspect((2 * R, 2 * R, SHAFT_TOP))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(title)
        fig.savefig(os.path.join(OUT, "png", fname), bbox_inches="tight")
        plt.close(fig)

    view3d("rotor_iso.png", 28, -55, "MicroDry-Safe rotor - isometric (20 dummy slides)")
    view3d("rotor_top.png", 90, -90, "MicroDry-Safe rotor - top view")

    # half section in the XZ plane (Y = 0 cuts slots 1 and 11, the drain holes and both M3 screws)
    plane = cq.Face.makePlane(400, 400, cq.Vector(0, 0, 0), cq.Vector(0, 1, 0))
    fig, ax = plt.subplots(figsize=(11, 9), dpi=130)
    items = [(jar, "#b8c4cc", "jar (dummy)"), (lid, "#8f9ba3", "lid (dummy)"), (body, "#3f7fd9", "rotor_body"),
             (ring, "#f29a33", "rotor_top_ring"), (cq.Compound.makeCompound(slides), "#7fd3e0", "slides (dummy)")]
    for shape, col, lab in items:
        sec = shape.intersect(plane)
        polys = []
        for f in sec.Faces():
            tr = _tris(f, 0.05)
            polys += [t[:, [0, 2]] for t in tr]
        ax.add_collection(PolyCollection(polys, facecolors=col, edgecolors=col, linewidths=0.2, label=lab))
    x = np.linspace(-70, 70, 2)
    ax.axhline(LID_Z, color="k", lw=0.6, ls="--")
    ax.axhline(LID_Z - MIN_LID_CLEAR, color="r", lw=0.8, ls=":")
    ax.text(-68, LID_Z - MIN_LID_CLEAR - 3, "lid - %.0f mm limit (Z=%.0f)" % (MIN_LID_CLEAR, LID_Z - MIN_LID_CLEAR), color="r", fontsize=8)
    ax.text(-68, SLIDE_TOP + 0.8, "slide tip Z=%.1f" % SLIDE_TOP, fontsize=8)
    ax.text(DISC_R + 1, DISC_Z0 - 4, "OD %.0f / jar %.0f" % (2 * DISC_R, JAR_BOTTOM_D), fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-72, 72); ax.set_ylim(-8, LID_Z + LID_T + 20)
    ax.set_title("Half section Y=0 inside dummy jar (Z=0 jar floor)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, lw=0.3)
    fig.savefig(os.path.join(OUT, "png", "rotor_section_in_jar.png"), bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
def main():
    render = "--no-render" not in sys.argv
    print("drive method: %s (socket clearance %.2f mm/side)" % (DRIVE_METHOD, SOCKET_CLEAR))
    checks = design_checks()
    enforce(checks)
    print("design rules: %d/%d pass" % (sum(c["ok"] for c in checks), len(checks)))
    rcf_rows = rcf_table()

    body, ring, slides = build_rotor_body(), build_top_ring(), build_slides()
    fit = build_fit_test()
    jar, lid = build_jar_dummy()
    geo = geometry_checks(body, ring, slides, jar, lid)
    for k, v in geo.items():
        print("  %-28s %s" % (k, v))
    assert geo["body_solids"] == 1 and geo["ring_solids"] == 1, "a part is not one solid"
    for k in ("slides_x_body_mm3", "slides_x_ring_mm3", "slide_x_neighbour_mm3", "ring_x_body_mm3",
              "rotor_x_jar_mm3", "rotor_x_lid_mm3"):
        assert geo[k] < 1e-3, "interference: %s = %s" % (k, geo[k])
    assert geo["ring_to_body_gap_mm"] < 1e-3 and geo["slide_to_body_gap_mm"] < 1e-3, "floating part"
    assert geo["slot_wall_measured_mm"] >= MIN_SLOT_WALL
    for k, v in geo.items():
        if k.startswith("label_"):
            assert v >= 0.8, "label too close: %s = %s" % (k, v)

    mass = {n: {"volume_cm3": round(s.Volume() / 1000, 2), "mass_g": round(s.Volume() / 1000 * DENSITY, 1)}
            for n, s in (("rotor_body", body), ("rotor_top_ring", ring), ("fit_test", fit))}
    mesh = export_all(body, ring, slides, fit)
    for n, m in mesh.items():
        assert m["watertight"], "%s.stl not watertight" % n
    if render:
        render_previews(body, ring, slides, jar, lid)

    bb_asm = cq.Compound.makeCompound([body, ring] + slides).BoundingBox()
    omega = RPM_NOMINAL * 2 * math.pi / 60
    report = {
        "drive_method": DRIVE_METHOD, "design_rules": checks, "rcf": rcf_rows, "geometry": geo, "mass": mass,
        "mesh": mesh,
        "z_stack": {"shaft_bottom": SHAFT_Z0, "disc_bottom": DISC_Z0, "slot_floor": SLIDE_Z0, "disc_top": DISC_Z1,
                    "ring_bottom": RING_Z0, "ring_top": RING_Z1, "boss_top": BOSS_Z1, "slide_tip": SLIDE_TOP,
                    "lid_underside": LID_Z, "shaft_top": SHAFT_TOP},
        "assembly_size_mm": [round(bb_asm.xlen, 2), round(bb_asm.ylen, 2), round(bb_asm.zlen, 2)],
        "slide_force_N_at_nominal_rpm": round(SLIDE_MASS_G / 1000 * omega ** 2 * ((R_IN + R_OUT) / 2) / 1000, 1),
    }
    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("mass:", mass)
    print("assembly size:", report["assembly_size_mm"])
    print("DONE")


if __name__ == "__main__":
    main()
