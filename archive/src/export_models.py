"""STEP + high-resolution STL export (Linear deflection <= 0.01 mm, Angular tolerance <= 0.1 deg)."""
import os, math
import cadquery as cq
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from params import *


def _premesh_small_features(shape):
    """OCCT mesh หน้าโค้งแบบ grid 2 ทิศ -> หน้าเล็ก ๆ ที่ angular 0.1 deg ทำให้สามเหลี่ยมเป็นล้านและกิน RAM หลาย GB.
    จึง mesh หน้าเล็กไว้ก่อน (linear 0.01 mm เท่าเดิม) : ผนังตัวเลข (EXTRUSION) ที่ GLYPH_ANGULAR_DEG,
    หน้าโค้งอื่นที่พื้นที่ < SMALL_FACE_AREA ที่ SMALL_FACE_ANGULAR_DEG ; BRepMesh จะไม่ทำซ้ำหน้าที่ mesh แล้ว.
    หน้าอื่นทั้งหมด (ทรงกระบอก/กรวย/ระนาบขนาดใหญ่) ใช้ 0.01 mm / 0.1 deg ตามข้อกำหนด."""
    n = 0
    for f in shape.Faces():
        gt = f.geomType()
        if gt == "EXTRUSION":
            ang = GLYPH_ANGULAR_DEG
        elif gt != "PLANE" and f.Area() < SMALL_FACE_AREA:
            ang = SMALL_FACE_ANGULAR_DEG
        else:
            continue
        BRepMesh_IncrementalMesh(f.wrapped, STL_LINEAR_DEFLECTION, False, math.radians(ang), False)
        n += 1
    return n


def export_step(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(obj, cq.Assembly):
        obj.save(path, "STEP")
    else:
        cq.exporters.export(cq.Workplane("XY").add(obj), path, "STEP")
    return path


def export_stl(shape, path):
    """absolute deflection (relative=False) so 0.01 mm really means 0.01 mm."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _premesh_small_features(shape)
    ok = shape.exportStl(path, tolerance=STL_LINEAR_DEFLECTION, angularTolerance=STL_ANGULAR_RAD,
                         ascii=False, relative=False, parallel=True)
    if not ok:
        raise RuntimeError("STL export failed: " + path)
    return path
