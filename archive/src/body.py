"""rotor_core_body : main body = base + hub + cage + 20 slots + drains + shaft mount + bayonet post + marks."""
from params import *
from geom import *
from body_cage import build_cage
from body_coupling import coupling_cutters
from body_bayonet import bayonet_cutters, post_top_chamfer
from marks import rim_number_cutters


def build_rotor_core_body(poly_glyph=False):
    body = build_cage()
    body = body.cut(*coupling_cutters(), *bayonet_cutters(), post_top_chamfer()).clean()
    body = body.cut(*rim_number_cutters(poly_glyph)).clean()
    return body


if __name__ == "__main__":
    import time
    t = time.time()
    b = build_rotor_core_body()
    bb = b.BoundingBox()
    print("valid", b.isValid(), "solids", len(b.Solids()), "faces", len(b.Faces()),
          "vol cm3 %.1f" % (b.Volume() / 1000), "z", round(bb.zmin, 3), round(bb.zmax, 3), "%.1fs" % (time.time() - t))
