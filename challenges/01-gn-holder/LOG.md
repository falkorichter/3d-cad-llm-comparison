# Challenge 01: log

## 2026-11-11

- Research: [REQUIREMENTS.md](REQUIREMENTS.md). The first pass couldn't load the product page (404).
  A second pass found that the URL needs the trailing slash, and rewrote the requirements around the
  real product: the TEKNOSTAHL tilted rack, 15°, 704 × 300 opening. A
  [MEASUREMENTS.md](MEASUREMENTS.md) for the customer was added at the same time.
- Started two build agents in parallel, OpenSCAD → `openscad/` and SolidCraft (MCP) → `solidcraft/`,
  from a shared brief [DESIGN.md](DESIGN.md) v1. **Mistake:** the brief was written from the *first*
  requirements pass, so it specifies a flat GN 1/1 insert frame on a 256 mm bed, not the tilted
  rack. The builds still compare the toolchains on the same part, but they aren't the product.
  Lesson: write the build brief only after the requirements have settled, and re-read the
  requirements just before starting agents.
- Onshape: MCP endpoint found (HTTP + OAuth) and registered; login still to do. CADCraft is out
  because it's 2D only.
- **SolidCraft v1 done** (agent, 08:39–08:50 tool time, ~15 min total; ~56 tool calls, ~30 of them
  to SolidCraft; 2 corrections, no rebuild from scratch). Details in [solidcraft/NOTES.md](solidcraft/NOTES.md).
  - 18 bodies / 6 part types (corner A and B, middle rail, splice plate, leg, divider). Every part fits
    256 × 256; the 326 mm divider only fits diagonally. M4 screws and recessed splice plates, no supports.
  - Measured outer 552 × 347, opening 532 × 327, through-hole 516 × 311, 165 mm clearance. All match the
    brief. Volumes match the hand calculation; switching to GN 2/3 and `max_depth` = 100 rebuilds cleanly.
  - **SolidCraft bug:** `solid.hole` with an expression position does not follow parameters (it rebuilds
    from frozen numbers). Worked around with `solid.cylinder` cuts.
  - **Limits:** no command to split a body that has two disjoint pieces; no `if` in expressions (the
    layout became 0/1 flags); automatic body names like "Frame (1) (1) (1)"; `solid.move` rotation has
    no pivot. No crashes.
- **OpenSCAD v1 done** (agent, 08:39–08:54, ~15 min; ~42 tool calls; 4 small corrections, none of
  them to the geometry). Details in [openscad/NOTES.md](openscad/NOTES.md). OpenSCAD 2021.01 (CGAL),
  so the faster Manifold backend wasn't available; `build.sh` exports everything and reruns all checks
  in about 30 s.
  - 14 printed parts: 4 corners, 2 middle rails, 4 legs and 2 dividers. Every part fits 256 × 256; the
    338 mm divider only fits diagonally (9.6 mm spare). Joints are integral **dovetails**, no bolts;
    legs use a tenon and socket.
  - Measured on horizontal cuts: outer 552 × 347, opening 532 × 327, through-hole 516 × 311, ledge
    underside at z = 165. All match. Every pair of parts intersects at 0 mm³. A `layout` that doesn't
    add up to 1/1 stops with an assert.
  - No STEP (OpenSCAD can't export it).

### v1 comparison (same brief, built in parallel)

| | OpenSCAD | SolidCraft (MCP) |
|---|---|---|
| Time / tool calls | ~15 min / ~42 | ~15 min / ~56 (~30 to SolidCraft) |
| Corrections | 4 (scripts and guard, no geometry fixes) | 2 (tool bug workaround, body split) |
| Joints | dovetails, no hardware | M4 screws + splice plates + heat-set inserts |
| Printed parts | 14 | 18 |
| STEP | no | yes (assembly + each part) |
| How it was checked | own scripts: STL bbox, slices, pairwise intersection | built-in `measure`, `body_topology`, `check_parameters` |
| Parametric `layout` | list of fractions plus an assert | 0/1 flags (no `if` in expressions) |
| Tool problems | old 2021.01 build, no Manifold | `solid.hole` position bug, no way to split disjoint bodies |

Both say the long rails will sag under a full pan, and neither has been printed. The tolerances are guesses.
- [ ] v2 brief from REQUIREMENTS.md §3 (tilted rack), then rebuild.
