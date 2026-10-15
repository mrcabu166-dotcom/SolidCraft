"""Stand-alone render stage: 7 patent views (Front, Back, Left, Right, Top, Bottom, Isometric) for the
assembly + both parts. Shapes are written to temporary BREP files and every view is rendered in its own
process (OCCT's HLR occasionally dies with an access violation; a fresh process + retry is reliable)."""
import os, sys, time, subprocess, tempfile
import params
if os.environ.get("SHAFT_TYPE"):
    params.SHAFT_TYPE = os.environ["SHAFT_TYPE"]
import cadquery as cq
from body import build_rotor_core_body
from ring import build_bayonet_comb_ring, place_in_assembly
from assembly import opposite_pair
import render_views as rv

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.environ.get("OUT_DIR", os.path.join(HERE, "..", "output")))
RETRIES = 4


def render_view_isolated(brep, view, out_base, label):
    for attempt in range(1, RETRIES + 1):
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "render_one.py"), brep, view, out_base, label],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return attempt
        print("   %s: attempt %d failed (exit %d), retrying" % (view, attempt, r.returncode), flush=True)
    raise RuntimeError("view %s failed %d times: %s" % (view, RETRIES, r.stderr[-400:]))


def main():
    body = build_rotor_core_body()
    ring = build_bayonet_comb_ring()
    asm = cq.Compound.makeCompound([body, place_in_assembly(ring, 0.0)] + opposite_pair(0))
    d = os.path.join(OUT, "drawings")
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        for name, shape in (("rotor_assembly", asm), ("rotor_core_body", body), ("bayonet_comb_ring", ring)):
            brep = os.path.join(tmp, name + ".brep")
            shape.exportBrep(brep)
            out_dir = os.path.join(d, name)
            os.makedirs(out_dir, exist_ok=True)
            retries = 0
            for i, v in enumerate(rv.VIEWS):
                base = os.path.join(out_dir, "%s_%d_%s" % (name, i + 1, v))
                retries += render_view_isolated(brep, v, base, "%s - %s view" % (name, v.capitalize())) - 1
            rv.contact_sheet(out_dir, name, os.path.join(d, name + "_7views_sheet.png"))
            print("[%6.1fs] drawings: %s (retries: %d)" % (time.time() - t0, name, retries), flush=True)


if __name__ == "__main__":
    main()
