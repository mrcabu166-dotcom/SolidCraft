"""Render ONE view of a BREP file:  python render_one.py <shape.brep> <view> <out_base> <label>
(called by render_all.py, one process per view, so an occasional OCCT HLR crash can simply be retried)."""
import sys
import cadquery as cq
import render_views as rv

if __name__ == "__main__":
    brep, view, out_base, label = sys.argv[1:5]
    shape = cq.Shape.importBrep(brep)
    n = rv.render_view(shape, view, out_base + ".png", out_base + ".svg", label=label)
    print("rendered", view, n, flush=True)
