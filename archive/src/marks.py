"""rotor_core_body part 4/4 + ring : balancing indicators (debossed numbers 1..10, opposite pairs 180 deg apart).

poly=False : ตัวเลขเป็นเส้นโค้ง B-spline จริง (ใช้กับ STEP และภาพเขียนแบบ)
poly=True  : เส้นขอบตัวเลขแปลงเป็น polyline ความคลาด GLYPH_SAG (0.003 mm) -> ผนังเป็นระนาบ
             ทำให้ mesh STL เป็น watertight และไม่ต้องใช้สามเหลี่ยมนับล้านที่ angular 0.1 deg
"""
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from params import *
from geom import *


def _wire_points(wire, sag):
    """Ordered closed polyline through a wire (edges chained by endpoint proximity)."""
    segs = []
    for e in wire.Edges():
        d = GCPnts_QuasiUniformDeflection(BRepAdaptor_Curve(e.wrapped), sag)
        segs.append([V(d.Value(i).X(), d.Value(i).Y(), d.Value(i).Z()) for i in range(1, d.NbPoints() + 1)])
    chain = segs.pop(0)
    while segs:
        end = chain[-1]
        for i, s in enumerate(segs):
            if (s[0] - end).Length < 1e-6:
                chain += s[1:]; segs.pop(i); break
            if (s[-1] - end).Length < 1e-6:
                chain += s[::-1][1:]; segs.pop(i); break
        else:
            raise RuntimeError("glyph wire is not a single closed loop")
    if (chain[0] - chain[-1]).Length < 1e-6:
        chain.pop()
    return chain


def _polygonize(text_shape, plane, depth, sag):
    n = plane.zDir
    out = []
    for f in text_shape.Faces():
        if f.geomType() != "PLANE":
            continue
        if abs(f.normalAt().dot(n)) < 0.999 or abs((f.Center() - plane.origin).dot(n)) > 1e-6:
            continue                                   # เอาเฉพาะหน้าฐานของตัวอักษร (ที่ระนาบ)
        outer = cq.Wire.makePolygon(_wire_points(f.outerWire(), sag), close=True)
        inner = [cq.Wire.makePolygon(_wire_points(w, sag), close=True) for w in f.innerWires()]
        out.append(cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer, inner), n * depth))
    return cq.Compound.makeCompound(out)


def _text_solid(label, plane, depth, poly=False):
    t = cq.Workplane(plane).text(str(label), NUM_FONT, depth, combine=False,
                                 font=NUM_FONT_NAME, kind="bold", halign="center", valign="center").val()
    return _polygonize(t, plane, depth, GLYPH_SAG) if poly else t


def rim_number_cutters(poly=False):
    """ตัวเลขปั๊มจมลึก NUM_DEBOSS บนขอบ (ผิวทรงกระบอก) ฐาน ตรงกับแต่ละช่อง. ช่อง k และ k+10 = เลขเดียวกัน"""
    plane = cq.Plane(origin=(R_BASE - NUM_DEBOSS, 0, Z_NUM_RIM), xDir=(0, 1, 0), normal=(1, 0, 0))
    base = {lab: _text_solid(lab, plane, NUM_DEBOSS + 1.5, poly) for lab in range(1, N_SLOTS // 2 + 1)}
    return [rotz(base[pair_label(k)], slot_angle(k)) for k in range(N_SLOTS)]


def ring_number_cutters(z_top, poly=False):
    """ตัวเลขปั๊มจมบนหน้าบนของแหวนล็อก (ตัวหนังสือชี้ออกนอก, อ่านตามเข็มนาฬิกา)"""
    plane = cq.Plane(origin=(R_NUM_RING, 0, z_top - NUM_DEBOSS), xDir=(0, -1, 0), normal=(0, 0, 1))
    base = {lab: _text_solid(lab, plane, NUM_DEBOSS + 1.0, poly) for lab in range(1, N_SLOTS // 2 + 1)}
    return [rotz(base[pair_label(k)], slot_angle(k)) for k in range(N_SLOTS)]
