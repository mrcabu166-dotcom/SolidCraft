# MicroDry-Safe — 20-slot slide drying rotor

[ภาษาไทย](README.md) | **English**

A rotor for the Simplus 2L 300W chopper (glass jar) that replaces the original blade assembly.
Status: **fully tested, ready for use** (October 2026)

## Files

| File | Purpose |
|---|---|
| `params.yaml` | Values from the real machine and printer clearances. Every value is tagged `measured` or `estimated` |
| `slide_rotor.py` | Builds the model, checks 28 design rules, and exports everything |
| `output/stl/rotor_body.stl` | Rotor body (shaft + lower disc), about 102 g |
| `output/stl/rotor_top_ring.stl` | Top ring, about 47 g |
| `output/stl/fit_test.stl` | Small test piece for the pin bore and gear socket fit, 13.7 g |
| `output/step/` | STEP files of every part, plus the assembly with 20 slides |
| `output/png/` | Isometric view, top view, and section in the jar |
| `output/report.json` | All check results |

Rebuild (run from the `microdry` folder):

```bash
../.venv/Scripts/python slide_rotor.py
```

Add `--no-render` to skip the previews. If any design rule fails, the script stops and prints the rule's name.
See the [top-level README](../README.en.md) for venv setup.

## Values measured on the real machine

| Item | Value (mm) |
|---|---|
| Jar inner height (floor to underside of lid) | 95 |
| Lid hole the shaft neck passes through | Ø18 |
| Gear head | tip Ø9 / root Ø7 / 8 teeth / tooth width 1.6 / length 12 |
| Jar floor pin | Ø6, 15 high. The floor is flat, with no raised boss around the pin |
| Original shaft | 110 long. Its bottom sits 1 above the jar floor |

## Tested clearances

Tested with the actual printer and PETG (values are per side).

| Feature | Value | Result |
|---|---|---|
| Pin bore (`pin_bore_clear`) | 0.15 | Good fit |
| Printed gear socket (`socket_clear_printed`) | 0.25 | Good fit (0.20 was tight) |
| Ring hex bore (`hex_clear`) | 0.15 | Good fit |
| Slide slots (1.8 wide) | — | Slides fit well |

If you change the printer, filament or nozzle, print `fit_test.stl` again first and adjust in steps of 0.05.

## Slicer settings (PETG)

- 0.2 mm layers, 4–5 walls, 5 top/bottom layers, at least 40 % gyroid infill
- `rotor_body`:
  - Use tree supports **under the disc only**.
  - Add support blockers in the slide slots, the drain holes, and the pin bore.
  - Add a 100 % infill modifier over the top 20 mm of the shaft (the gear socket).
- `rotor_top_ring` needs no supports.
- Use the same settings you used for `fit_test`.

## Parts to buy

- 2 × M3 heat-set inserts. The design assumes M3 × 5.7 × 4.6, which needs a Ø4.0 hole.
- 2 × M3 × 8 grub (set) screws. M3 × 6 also works. **Do not use M3 × 10**: the screw end sticks out far enough to hit the slides.

## Assembly

1. Press the inserts into the two holes in the ring boss with a soldering iron at about 230–240 °C. Stop when they sit flush with the surface.
2. Put the rotor in the jar so the bore at the bottom of the shaft fits over the floor pin.
3. Slide the ring onto the hex so the V notch on the ring lines up with the V notch on the disc. 0° and 180° both work, and the slot numbers match either way.
4. Tighten both grub screws **before loading slides**. The screws line up with slot 1, so a hex key cannot reach them once slides are in.
5. Drop the slides through the ring slots down to the bottom of the disc slots. **Load them in pairs by number**: slots with the same number are 180° apart. The 6 and 9 labels carry a dot (`6.`, `9.`) so they cannot be mixed up.
6. Close the lid and spin.

To take it apart, reverse the order: remove all slides first, then loosen the screws and lift the ring off.

## Use and care

- **Always load slides in pairs.** With an odd number of slides, put a blank slide in the paired slot. Never spin with only one slide of a pair loaded.
- Hold the jar and press down on the lid while spinning. If the sound changes or it starts to vibrate, let go of the button at once.
- At 2800 rpm the outer edge of a slide sees about 386 g. The script prints the full RCF table.
- Every 5–10 uses, check:
  - the gear socket, for plastic debris or play
  - the bottoms of the slide slots and the area around the inserts, for white stress cracks
  - the ring, that it is still locked tight
- Do not wash above 60 °C and do not oven-dry. PETG softens.
- If the gear socket wears, reprint `rotor_body`. Alternatively, set `drive_method: metal_insert` in `params.yaml` to switch to a metal socket insert.

## Test results (October 2026)

| Step | Result |
|---|---|
| Fit tests: pin / gear / hex / slide slots | All good fit |
| Inserts + M3 × 8 grub screws locking the ring | Locked, no movement |
| Empty spin, pulse | Smooth, no rubbing |
| 1 pair of slides / all 10 pairs | Smooth, slides stay in place |
| 20 slides, 30 s spin | Smooth, no vibration |
| Inspection after spinning | No gear socket wear, ring still tight, no cracks |

## Values still estimated (working, but not measured)

- **Jar inner diameter**: 110 at the floor, 125 at the mouth. There is 8.5 mm of side clearance, well over the 5 mm rule.
- **Slide size**: 75 × 25.4, 1.0–1.2 thick. If you change slide brand, test the fit in a slot first.
- **Insert size, motor rpm, and PETG density**: used only for checks and calculations.
