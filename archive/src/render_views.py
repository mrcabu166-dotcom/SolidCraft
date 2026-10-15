"""Patent-style line drawings: orthographic, hidden lines removed (OCCT HLR), black on pure white."""
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepLib import BRepLib

S3 = 1.0 / math.sqrt(3.0)
S2 = 1.0 / math.sqrt(2.0)
# name -> (direction toward viewer, screen-right direction)
VIEWS = {
    "front":     ((0, -1, 0), (1, 0, 0)),
    "back":      ((0, 1, 0), (-1, 0, 0)),
    "left":      ((-1, 0, 0), (0, -1, 0)),
    "right":     ((1, 0, 0), (0, 1, 0)),
    "top":       ((0, 0, 1), (1, 0, 0)),
    "bottom":    ((0, 0, -1), (1, 0, 0)),
    "isometric": ((S3, -S3, S3), (S2, S2, 0)),
}


def _edges_to_polylines(compound, defl):
    out = []
    if compound is None or compound.IsNull():
        return out
    BRepLib.BuildCurves3d_s(compound, 1e-4)
    exp = TopExp_Explorer(compound, TopAbs_EDGE)
    while exp.More():
        e = TopoDS.Edge_s(exp.Current())
        try:
            ad = BRepAdaptor_Curve(e)
            d = GCPnts_QuasiUniformDeflection(ad, defl)
            if d.IsDone() and d.NbPoints() >= 2:
                out.append([(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)])
        except Exception:
            pass
        exp.Next()
    return out


def hlr_lines(shape, view, defl=0.03):
    """Return (sharp_edges, outlines) as lists of 2D polylines for the given view name."""
    vz, vx = VIEWS[view]
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*vz), gp_Dir(*vx))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    sharp = _edges_to_polylines(h.VCompound(), defl)
    outl = _edges_to_polylines(h.OutLineVCompound(), defl)
    return sharp, outl


def draw(ax, sharp, outl, lw=0.55):
    ax.add_collection(LineCollection(sharp, colors="black", linewidths=lw, capstyle="round"))
    ax.add_collection(LineCollection(outl, colors="black", linewidths=lw * 1.2, capstyle="round"))
    pts = [p for pl in sharp + outl for p in pl]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def render_view(shape, view, out_png, out_svg=None, label=None, px=2000, defl=0.03):
    sharp, outl = hlr_lines(shape, view, defl)
    w_in = 8.0
    fig = plt.figure(figsize=(w_in, w_in), dpi=px / w_in, facecolor="white")
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.92])
    x0, x1, y0, y1 = draw(ax, sharp, outl)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) / 2 * 1.06
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal")
    ax.axis("off")
    if label:
        fig.text(0.5, 0.012, label, ha="center", va="bottom", fontsize=11, family="sans-serif")
    fig.savefig(out_png, facecolor="white")
    if out_svg:
        fig.savefig(out_svg, facecolor="white")
    plt.close(fig)
    return len(sharp), len(outl)


def render_all(shape, out_dir, prefix, title, **kw):
    os.makedirs(out_dir, exist_ok=True)
    stats = {}
    for i, v in enumerate(VIEWS):
        base = os.path.join(out_dir, "%s_%d_%s" % (prefix, i + 1, v))
        stats[v] = render_view(shape, v, base + ".png", base + ".svg",
                               label="%s - %s view" % (title, v.capitalize()), **kw)
    return stats


def contact_sheet(out_dir, prefix, out_png, cols=4):
    from PIL import Image
    names = ["front", "back", "left", "right", "top", "bottom", "isometric"]
    ims = [Image.open(os.path.join(out_dir, "%s_%d_%s.png" % (prefix, i + 1, n))).convert("RGB")
           for i, n in enumerate(names)]
    s = 700
    ims = [im.resize((s, s)) for im in ims]
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * s, rows * s), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * s, (i // cols) * s))
    sheet.save(out_png)
