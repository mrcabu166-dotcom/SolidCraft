"""Small geometry helpers on top of CadQuery (all in mm / deg)."""
import math
import cadquery as cq

V = cq.Vector
ORIGIN = V(0, 0, 0)
ZAXIS = V(0, 0, 1)


def rotz(shape, deg):
    return shape.rotate(ORIGIN, ZAXIS, deg)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, V(0, 0, z0), ZAXIS)


def prism(points, vec):
    """Extrude closed polygon (3D points) along vec."""
    w = cq.Wire.makePolygon([V(*p) for p in points], close=True)
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), V(*vec))


def prism_yz_along_x(poly_yz, x0, x1):
    """Polygon given as (y, z) pairs, extruded along +X from x0 to x1."""
    return prism([(x0, y, z) for (y, z) in poly_yz], (x1 - x0, 0, 0))


def prism_xz_along_y(poly_xz, y0, y1):
    """Polygon given as (x, z) pairs, extruded along +Y from y0 to y1."""
    return prism([(x, y0, z) for (x, z) in poly_xz], (0, y1 - y0, 0))


def revolve_rz(poly_rz, deg=360.0, start_deg=0.0):
    """Revolve polygon given as (r, z) pairs about Z; sweeps CCW from start_deg."""
    w = cq.Wire.makePolygon([V(r, 0, z) for (r, z) in poly_rz], close=True)
    s = cq.Solid.revolve(w, [], deg, ORIGIN, ZAXIS)
    return rotz(s, start_deg) if start_deg else s


def teardrop_along_x(r, zc, x0, x1):
    """Horizontal round hole along +X (axis at y=0,z=zc) with a 45-deg pointed roof
    so it prints without support. The hole's lower half is the true circle."""
    circ = cq.Solid.makeCylinder(r, x1 - x0, V(x0, 0, zc), V(1, 0, 0))
    t = r / math.sqrt(2.0)
    tri = prism_yz_along_x([(-t, zc + t), (t, zc + t), (0.0, zc + r * math.sqrt(2.0))], x0, x1)
    return circ.fuse(tri)


def fuse_all(first, others):
    return first.fuse(*others).clean() if others else first


def cut_all(base, tools):
    return base.cut(*tools).clean() if tools else base


def polar_copies(shape, n, step_deg, start_deg=0.0):
    return [rotz(shape, start_deg + i * step_deg) for i in range(n)]
