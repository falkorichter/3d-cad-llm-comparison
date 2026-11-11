# Challenge 01, OpenSCAD: notes

Built against [DESIGN.md](../DESIGN.md) v1 (type A insert frame on legs, 256 × 256 bed, PETG).
Tool: OpenSCAD 2021.01 (the installed Homebrew/.app build; CGAL only, no Manifold backend), run headless.

## Files

| File | What |
|---|---|
| `gn_holder.scad` | The whole model. All DESIGN.md parameters at the top under the same names, a `part` selector, `layout`, `seat_mode` |
| `build.sh` | Exports every STL and render, then runs the bed-fit, derived-size and overlap checks (`./build.sh -D 'play=1.5'` passes overrides through) |
| `check_stl.py` | Bounding box, volume and bed fit of STL files (numpy only) |
| `measure_slices.py` | Measures outer/opening/through-hole sizes and the pan-body clearance on horizontal cuts of the assembly |
| `stl/` | One STL per printed part, in print orientation, plus `assembly.stl` (reference only) |
| `renders/` | `assembly.png`, `exploded.png`, `corner_closeup.png`, `seat_divider_closeup.png`, `part_*.png` (split parts) |

**No STEP.** OpenSCAD can't export STEP (only mesh formats plus DXF/SVG/CSG), so there is none for this toolchain.

## Approach

- One CSG model of the complete frame ring in rail-local Z (0 = rail bottom):
  outer block − through-hole − a 45° frustum under the ledge (so the ledge is a gusset, no overhang) −
  rim pocket − pan-body envelope − divider seats − leg sockets. Joint bosses and corner blocks are added before
  the cuts.
- Each printed part is that frame intersected with its region box, plus its dovetail tails, minus its sockets.
  So the parts always add up to the frame, and every parameter flows into every part.
- `part=` values: `assembly` (default), `exploded`, `frame`, `corner_ne|nw|se|sw`, `middle_n|s`, `leg`,
  `divider`, plus the check helpers `slice` (2D cut at `slice_z`) and `overlap` (pairwise intersections).
- `layout = ["1/3","1/3","1/3"]` (any list of "1/1", "2/3", "1/2", "1/3" that adds up to 1) sets where the
  dividers go in the assembly. `seat_mode = "all"` cuts seats at all 1/3, 1/2 and 2/3 positions
  (x = −88.3, 0, +88.3; the 1/3 and 2/3 seats also serve 2/3 + 1/3); `seat_mode = "layout"` cuts only the
  ones the layout needs. An `assert` rejects layouts that don't add up to 1/1.
- Z stack (derived): rail bottom at `max_depth + clear − (bar_h − rim_t − ledge_t)` = 151, ledge underside 165,
  ledge top (rim seat) 169, frame top 171. The rim pocket is `rim_t` deep, so a pan rim ends flush with the top.
- Legs and corner blocks are cut back by the pan-body envelope (`gn − 2·rim_w` + 2 mm = 509 × 304), so the
  30 × 30 legs don't clash with a 505 × 300 pan body in the corners (each leg loses an 8.5 × 8.5 inner notch).

## Parts and bed fit (256 × 256, build height 250)

| Part | Count | BBox (mm, print orientation) | Fits | Print orientation |
|---|---|---|---|---|
| `corner_ne` | 1 | 162.0 × 183.5 × 20 | yes | upright (rail bottom on the bed) |
| `corner_sw` | 1 | 162.0 × 183.5 × 20 | yes | upright; same shape as `corner_ne` turned 180° |
| `corner_nw` | 1 | 162.0 × 173.5 × 20 | yes | upright |
| `corner_se` | 1 | 162.0 × 173.5 × 20 | yes | upright; same shape as `corner_nw` turned 180° |
| `middle_n` | 1 | 248.0 × 18.0 × 20 | yes | upright |
| `middle_s` | 1 | 248.0 × 18.0 × 20 | yes | upright; same shape as `middle_n` turned 180° (only while seats are symmetric, i.e. `seat_mode="all"`) |
| `leg` | 4 | 30.0 × 30.0 × 166 | yes | standing, tenon up (151 leg + 15 tenon) |
| `divider` | 2 (default layout) | 246.4 × 246.4 × 16 | yes | on its side, turned 45° on the bed (part is 338.4 long; the STL is already rotated) |

Total 14 printed parts for the default layout. Bounding boxes are measured on the exported STLs with
`check_stl.py`; all STLs are closed, consistently oriented meshes (every directed edge has its twin).

## Joints: integral dovetails (no hardware)

- Rails are cut at x = ±114 on the long sides (`split_x`) and at y = 0 on the short sides. Middle parts carry a
  tail at both ends; `corner_ne`/`corner_sw` carry a tail on their short arm; the other corners have the sockets.
- The tail is a vertical-slide dovetail (neck 6, head 11, length 10) through the rail height. Around each joint the
  void under the ledge is filled in for `boss_len` = 28 mm so the full 18 × 20 section is there for the socket
  walls (≥ 3.2 mm each side).
- The tail's underside starts 4 mm above the rail bottom at the joint plane and rises at 45° (the socket floor
  follows it, `tol` lower). So the tail prints without support, and the socket floor carries the part that is
  dropped in from above (the joint transfers the vertical load, not only tension).
- Clearance `tol` = 0.3 on the dovetail flanks and the ramp; butt faces have no gap.
- Legs: a 14 × 14 square tenon with a 45° pyramid top in a matching blind socket (`tol` all round) in the corner
  block. The pyramid roof means the socket needs no bridge. Legs are held by gravity and the tenon.
- Assembly: drop the middle parts into the corners from above (tail into socket), drop `corner_se` onto `corner_ne`'s
  tail and `corner_nw` onto `corner_sw`'s, set the frame on the legs, lay the dividers into their seats.
- Why dovetails over M4 + splice plates: no hardware, self-locating, and the frame is mostly loaded in sag, which the
  floored socket takes. Downside: a printed joint in PETG creeps more than a bolted splice, see open issues.

## Divider bar and seats

- Seat: a slot `div_w + 2·tol` wide in the long rail, from 4 mm inside the outer face (`seat_in`) through the ledge,
  floor 10 mm above the rail bottom (`ledge_bot − ledge_t`), open to the top.
- Divider: 16 wide flange (`div_w`, 4 thick, top at the ledge top so the rims sit on it at ledge height and end
  flush) on an 8 wide web (`div_web`) that reaches down to rail-bottom level, chamfered at the ends. The ends are
  blocks that fill the slot: top at 171 (flush with the frame top) outside the opening, 169 inside the rim pocket.
- At 338.4 mm it doesn't fit 256 lying straight; lying on its side and turned 45° its footprint is 246.4 × 246.4,
  so it fits the bed diagonal without a split. On its side it has no overhangs at all, and the layers run along
  its length (good for bending).

## How the derived sizes were checked

`build.sh` cuts the assembled frame + legs (dividers left out) at several heights with `part="slice"`, exports
SVG, and `measure_slices.py` measures along the lines y = 40 and x = 40 (away from joints and seats):

| Height z | Measured outer | Measured inner | Expected |
|---|---|---|---|
| 170 (rim pocket) | 552.0 × 347.0 | 532.0 × 327.0 | outer 552 × 347, opening 532 × 327 ✅ |
| 167 / 165.1 (ledge) | 552.0 × 347.0 | 516.0 × 311.0 | through-hole 516 × 311 ✅ |
| 164.9 | | 516.2 × 311.2 | just below the ledge underside: gusset starts ✅ |
| 160 | | 526.0 × 321.0 | 45° gusset ✅ |
| 150, 75, 0.5 | 552.0 × 347.0 (legs only) | none | no geometry inside the 505 × 300 pan body ✅ |

- Height: `assembly.stl` bbox is 552.0 × 347.0 × 171.0; ledge underside at 165 (the cut at 165.1 shows the
  ledge, 164.9 doesn't), so there are 165 mm of free space (`max_depth + clear`) under the ledge. No cut from
  0.5 to 164.9 has geometry inside the pan-body footprint.
- Overlap: `part="overlap"` intersects every pair of assembled parts (rails, legs, dividers); the result has
  0.000 mm³ volume, so tails, sockets, tenons and dividers don't collide.
- Parametric spot checks: `layout=["2/3","1/3"]`, `seat_mode="layout"`, `max_depth=100` renders one divider at
  x = 88.3, only that seat, and 50 mm shorter legs; `layout=["1/2","1/3"]` stops with the layout assert.

## What was hard / tool limits

- Splitting a ring that is 552 × 347 into parts that each fit 256 without putting a joint on a divider seat:
  the middle part is `2·split_x + 2·dt_len` ≤ 256 and the seats sit at ±88.3 ± 8.3, so the joint has to be in
  the narrow band 100…118. `split_x = 114`, `boss_len = 28` leaves 3.4 mm between seat and boss. Asserts guard it.
- Printability without support decided most details: legs separate (a rail cantilevered 151 mm above the bed
  is not printable), 45° gusset under the ledge, ramped dovetail tails, pyramid-roof leg sockets, divider on its side.
- OpenSCAD 2021.01: CGAL only, but this model is all boxes, so a full build (8 STLs, 9 PNGs, slices, overlap) runs in
  about 30 s. `--render` PNGs lose colours, so the assembly views use preview mode. No STEP export; no built-in
  measuring, so bbox/size checks need external scripts (the 2D `projection(cut=true)` + SVG route worked well).
- The Cornfield colour scheme draws some upward faces green in `--render` PNGs; the meshes are fine (closed,
  consistently oriented), it's just the renderer's back-face colour.

## Time and effort

- Wall clock: about 15 minutes (08:39 to 08:54, 2026-11-11), including reading the brief, modelling, checks,
  renders and this file.
- About 35 tool calls. Corrections: 4 small ones (measurement script crashed on the legs-only cut; two shell
  commands refused by the worktree guard and redone with the Edit tool; tidy-up of the Python cache). The model
  itself needed no geometry fix after the first render; the split position was chosen up front to keep the middle
  part under 256 mm with its tails.

## Open issues

- Not printed or load tested. `tol` = 0.3 and the dovetail size are untested guesses; print the corner test piece
  (REQUIREMENTS V2) first.
- Strength: the 20 mm rail height is DESIGN.md's value; a full 1/1 × 150 pan (about 20 kg) over a 552 mm span in
  PETG will probably sag and creep. Raise `bar_h` (the ledge position follows) or add a centre leg pair after a test.
- Legs are only held by a 14 mm tenon and gravity; a frame that is pushed sideways can rack. Diagonal braces or
  a lower stretcher frame would help.
- The pan-body envelope (505 × 300) and rim width are estimates (REQUIREMENTS V1). Pan corner radii are not modelled,
  the pocket corners are square (rounded pan corners fit in them).
- Stretch goal not done: the long bar along the 530 side for 1/4, 1/6, 1/9.
- With `seat_mode="layout"` and an asymmetric layout, `middle_n` and `middle_s` are mirror images, not rotated
  copies; both are exported anyway, so this only matters for the part count note above.
- Butt faces at the joints have no clearance; elephant's foot may need a light sanding or a chamfer on the bottom edge.
