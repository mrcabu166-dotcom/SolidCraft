"""Build everything: parts -> validation -> STEP/STL -> 7-view patent drawings -> report.

usage:  python build_all.py [--no-validate] [--no-render] [--no-export]
env:    SHAFT_TYPE=D_SHAFT|HEX_COUPLING|THREADED_NUT   OUT_DIR=...
"""
import os, sys, json, time
import params
if os.environ.get("SHAFT_TYPE"):
    params.SHAFT_TYPE = os.environ["SHAFT_TYPE"]
from params import *
from geom import *
import cadquery as cq
from body import build_rotor_core_body
from ring import build_bayonet_comb_ring, to_print_orientation, place_in_assembly
from assembly import build_assembly
import export_models as ex

OUT = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output"))
OUT = os.path.abspath(OUT)
ARGS = set(sys.argv[1:])


def stage(msg, t0=[time.time()]):
    now = time.time()
    print("[%6.1fs] %s" % (now - t0[0], msg), flush=True)


def main():
    rep = {"shaft_type": SHAFT_TYPE}
    if "--no-render" not in ARGS:
        import subprocess
        r = subprocess.run([sys.executable, "-u", os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_all.py")],
                           env=dict(os.environ, OUT_DIR=OUT))
        if r.returncode != 0:
            raise RuntimeError("render stage failed (exit %d)" % r.returncode)
        stage("drawings rendered (separate process, before heavy stages)")
    body = build_rotor_core_body();                    stage("body built")
    ring = build_bayonet_comb_ring();                  stage("ring built")
    ring_print = to_print_orientation(ring)
    asm, ring_locked, slides = build_assembly(body, ring, slides_k=(0,))
    asm_compound = cq.Compound.makeCompound([body, ring_locked] + slides)
    stage("assembly built")
    # STL twins : เหมือนกันทุกอย่างยกเว้นตัวเลขเป็น polyline (sag 0.003 mm) เพื่อ mesh watertight
    body_stl = build_rotor_core_body(poly_glyph=True)
    ring_stl = build_bayonet_comb_ring(poly_glyph=True)
    ring_print_stl = to_print_orientation(ring_stl)
    asm_stl = cq.Compound.makeCompound([body_stl, place_in_assembly(ring_stl, 0.0)] + slides)
    stage("STL twins built")

    if "--no-export" not in ARGS:
        step_dir, stl_dir = os.path.join(OUT, "step"), os.path.join(OUT, "stl")
        ex.export_step(body, os.path.join(step_dir, "rotor_core_body.step"))
        ex.export_step(ring_print, os.path.join(step_dir, "bayonet_comb_ring.step"))
        ex.export_step(asm, os.path.join(step_dir, "rotor_assembly.step"));        stage("STEP exported")
        ex.export_stl(body_stl, os.path.join(stl_dir, "rotor_core_body.stl"));          stage("STL body")
        ex.export_stl(ring_print_stl, os.path.join(stl_dir, "bayonet_comb_ring.stl"));  stage("STL ring")
        ex.export_stl(asm_stl, os.path.join(stl_dir, "rotor_assembly.stl"));   stage("STL assembly")

    if "--no-validate" not in ARGS:
        import validate as V
        rep["brep"] = [V.brep_report("rotor_core_body", body), V.brep_report("bayonet_comb_ring (print orientation)", ring_print),
                       V.brep_report("rotor_assembly", asm_compound)]
        rep["slots"] = V.slot_checks(body);                          stage("slot checks")
        rep["slides_20"] = V.slide_checks(body, ring_locked);        stage("slide interference")
        rep["bayonet"] = V.bayonet_checks(body, ring);               stage("bayonet checks")
        rep["teeth"] = V.teeth_footprint_check(ring);                stage("teeth footprint")
        rep["drain"] = V.drain_checks(body);                         stage("drain checks")
        if "--no-export" not in ARGS:
            rep["mesh"] = [V.mesh_report(os.path.join(stl_dir, n)) for n in
                           ("rotor_core_body.stl", "bayonet_comb_ring.stl", "rotor_assembly.stl")]
            rep["overhang_body"] = V.overhang_report(os.path.join(stl_dir, "rotor_core_body.stl"))
            rep["overhang_ring"] = V.overhang_report(os.path.join(stl_dir, "bayonet_comb_ring.stl"))
            stage("mesh + overhang checks")
        if "--no-export" not in ARGS:
            mb = {m["file"]: m for m in rep["mesh"]}
            rep["print_orientation"] = {
                "rotor_core_body_zmin": mb["rotor_core_body.stl"]["zmin"],
                "bayonet_comb_ring_zmin": mb["bayonet_comb_ring.stl"]["zmin"],
                "bayonet_comb_ring_zmax": mb["bayonet_comb_ring.stl"]["zmax"]}
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "validation_report.json"), "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, ensure_ascii=False)

    stage("DONE")
    return rep


if __name__ == "__main__":
    main()
