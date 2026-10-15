"""rotor_assembly : body + ring (locked) + simulated slides (1 opposite pair by default)."""
import cadquery as cq
from params import *
from geom import *
from ring import place_in_assembly


def slide_solid(k):
    x0 = R_HUB + SLIDE_INNER_CLEAR
    s = box(x0, x0 + SLIDE_W, -SLIDE_T / 2, SLIDE_T / 2, Z_SEAT, Z_SEAT + SLIDE_H)
    return rotz(s, slot_angle(k)) if k else s


def opposite_pair(k=0):
    return [slide_solid(k), slide_solid(k + N_SLOTS // 2)]


def all_slides():
    return [slide_solid(k) for k in range(N_SLOTS)]


def build_assembly(body, ring, slides_k=(0,)):
    ring_locked = place_in_assembly(ring, 0.0)
    slides = []
    for k in slides_k:
        slides += opposite_pair(k)
    asm = cq.Assembly(name="rotor_assembly")
    asm.add(body, name="rotor_core_body", color=cq.Color(0.45, 0.47, 0.5, 1.0))
    asm.add(ring_locked, name="bayonet_comb_ring", color=cq.Color(0.2, 0.55, 0.85, 1.0))
    for i, s in enumerate(slides):
        asm.add(s, name="slide_%d" % (i + 1), color=cq.Color(0.8, 0.95, 1.0, 0.35))
    return asm, ring_locked, slides
