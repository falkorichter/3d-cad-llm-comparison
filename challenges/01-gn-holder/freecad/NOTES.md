# Challenge 01, FreeCAD (MCP): notes

Built 2026-11-25 by Claude Code in the main session, driving **FreeCAD 1.1.4** through
[neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) 0.1.32 (setup:
[../../../docs/freecad-mcp/LOG.md](../../../docs/freecad-mcp/LOG.md)). Spec: [../DESIGN.md](../DESIGN.md) v1, the same
flat GN 1/1 frame as the OpenSCAD, SolidCraft and Onshape builds.

## Files

| Path | What |
|---|---|
| `gn_holder.py` | The build script: `build()`, `report()`, `export()`. Runs in the FreeCAD GUI (MCP `execute_code`) or headless (`freecadcmd`) |
| `gn_holder.FCStd` | The **parametric** FreeCAD document it produces: spreadsheet `Params` + 131 features. Open it in FreeCAD, change a cell, Recompute |
| `step/gn_holder_assembly.step` | All 18 parts |
| `step/*.step`, `stl/*.stl` | One STEP and one STL per placed part (18 each) |
| `renders/assembly_iso.png` | Assembly, colour per part type |
| `renders/part_corner_top.png`, `renders/part_corner_bottom.png` | Corner from above (rim pocket, ledge, seat, counterbore) and below (splice recesses, insert holes, spigot socket) |
| `renders/part_rail_with_dividers.png`, `renders/part_leg.png` | Middle rail with dividers and splice plates; a leg |

## Approach: a script that *produces a parametric document*

This is the main difference from OpenSCAD. The Python script doesn't compute geometry itself: it creates FreeCAD
features whose sizes and positions are **expressions bound to a spreadsheet**:

- `Params` (Spreadsheet): every DESIGN.md parameter as an alias (`gn_l`, `play`, `bar_h`, …), plus joint sizes and
  derived cells (`open_l = gn_l + 2*play`, `hole_l`, `out_l`, `leg_h`, …).
- Each solid is a `Part::Box` or `Part::Cylinder`, e.g. `Length = Params.out_l` and
  `Placement.Base.x = Params.split_x - (Params.sp_len + 2*Params.tol)/2`.
- Booleans are features too: `Frame = Cut(Outer, MultiFuse(pocket, hole, seats, recesses, inserts, sockets, bolts))`.
- **Split** like the OpenSCAD build: each printed part is `MultiCommon(Frame, region box)`, and the region boxes are
  expressions on `split_x`. So the parts always add up to the frame.
- Result: the `.FCStd` is as parametric as the SolidCraft `.sc`. Someone without the script can open it in the GUI and
  edit `Params`. The script is only the recipe.

### `layout`
FreeCAD expressions do have a ternary operator, but a feature can't be created or deleted by an expression. As in
SolidCraft, it's two 0/1 flags: `seat_half` and `seat_third`. A disabled seat cutter is lifted 100 mm above the frame
(`z = … + (1 - flag)*100`), so it cuts nothing. Dividers sit at `±open_l/6 * seat_third`.

## Joints: M4 splice plates + heat-set inserts (same as SolidCraft/Onshape)

- 6 joints: long rails at x = ±`split_x` (125), short rails at y = 0.
- A 68 × 14 × 4 plate in a 68.6 × 14.6 × 4.3 recess in the rail bottom, centred in the 18 mm band, so 2 mm lips stay at
  the sides. (SolidCraft's plate is the full band width.) 4 × Ø4.5 holes in the plate; 4 × Ø5.6 × 8 insert holes in the
  rail, at 10 and 24 mm each side of the joint.
- Legs: 30 × 30, inner faces on the through-hole edge, so the pan path stays clear and the leg sticks out 12 mm (as in
  SolidCraft). A 6 × 6 × 6 spigot goes into a 6.6 × 6.6 × 6.3 socket (anti-rotation), and one M4 × 30 from the top
  (Ø4.5 through, Ø8 × 4 counterbore in the wall) goes into a Ø5.6 × 12 insert in the leg.
- Rail section: the ledge is solid down to the rail bottom, as in SolidCraft (no overhang, no crevice).

## Parts and bed fit (256 × 256, height 250)

From `report()`: B-rep bounding boxes and volumes.

| Part | Count | BBox mm | Volume mm³ | Fits |
|---|---|---|---|---|
| Corner (PP, NP, PN, NN; NP/PN are mirrors of PP/NN) | 4 | 151 × 173.5 × 20 | 99 771.2 | yes |
| Rail (P, N; identical by a 180° turn) | 2 | 250 × 18 × 20 | 79 311.5 | yes (6 mm spare) |
| Splice plate | 6 | 68 × 14 × 4 | 3 553.5 | yes |
| Leg (165 + 6 spigot) | 4 | 30 × 30 × 171 | 148 420.4 | yes, standing |
| Divider | 2 | 16 × 326.4 × 18 | 55 654.4 | only diagonally: 243.5 × 243.5 at 45° |

18 parts, 1 284 019 mm³ in total (about 1.6 kg of PETG at 100 % infill). Hardware: 28 × M4 heat-set inserts,
24 × M4 × 12, 4 × M4 × 30.

## Checks

- **Volumes against hand calculations, worked out before the build:**
  - Frame ring (outer − hole − pocket): 594 384, the same as SolidCraft's.
  - After the 6 seat notches: 591 196.8.
  - Minus 6 recesses (6 × 4 306.7), 24 inserts (24 × 197.0), 4 sockets (4 × 274.4) and 4 bolt holes with counterbores (4 × 455.5): **557 707.7 expected, 557 707.7 measured.**
  - Middle rail: 344 mm² × 250 − 3 seats − 2 half recesses − 4 inserts = **79 311.5 expected, 79 311.5 measured**.
- **Derived sizes** (sheet + frame bbox): outer **552 × 347**, opening **532 × 327**, through-hole **516 × 311**,
  **165** mm under the frame (leg z min = −165). ✓
- **Interference:** `common()` of every pair of the 18 parts is 0 mm³. ✓
- **Validity:** all 131 features valid; every part is 1 valid solid.
- **Parametric**, by setting sheet cells, recomputing and putting them back:

  | Change | Result |
  |---|---|
  | `gn_l = 354` (GN 2/3) | No errors. Outer 376 × 347, corners x 125…188, short-joint inserts move to x = 179, dividers to ±59.33 (= 356/6) |
  | `max_depth = 100` | Legs end at z = −115, leg volume −45 000 = 30·30·50 exactly |
  | `seat_third = 0` | Rail +1 062.4 = 2 × 531.2 (two notches close). Both dividers move to x = 0 and overlap each other (expected, see open issues) |

- **Exports:** STL meshes are closed (`isSolid`, no non-manifolds), within about 2 mm³ of the B-rep (the circles become
  polygons). STEP files read back with the exact B-rep volumes; the assembly STEP has 18 solids.
- **Headless:** `freecadcmd` with the same script gives the same frame and total volumes in about 1 s.

## Time and effort

- **About 4 minutes of tool time** (21:06:45 to 21:10:30) from the first FreeCAD call to the headless check. This doesn't
  include writing the script, which happened in between and counts as model time.
- **8 FreeCAD MCP calls** (all `execute_code`): write test, failed build, sheet debug, build + report, parametric
  checks, renders, bottom render, export. About 10 local calls (file write/edit, reading renders, headless run).
- **2 corrections:**
  1. **`clear` is reserved in FreeCAD expressions.** The cell `=max_depth + clear` failed with "Unsupported operator",
     so every feature that referenced the sheet failed with "shape is invalid". The alias is now `clearance`. This is
     the only DESIGN.md name that changed.
  2. The first "bottom" render rotated the camera wrong; it was redone by rendering a flipped temporary copy.
  - Plus one cosmetic fix: `MultiFuse` takes its children's colours on recompute, so the dividers came out grey until
    they were coloured after the recompute.

## What was good / hard (tool notes)

- **Two views of the same model.** `execute_code` returns a screenshot, so the agent can look at what it built, and
  `report()` gives the numbers. That's the SolidCraft experience with FreeCAD's full Python API.
- The user watches the model appear in the FreeCAD window, as with SolidCraft's bridged mode.
- The MCP's own object tools (`create_object`, `edit_object`) weren't needed: for 131 features one Python script is
  much cheaper than 131 tool calls. In practice the MCP is "a Python REPL inside FreeCAD, with screenshots".
- **The same script runs headless**, so the build can run in CI without the MCP, like OpenSCAD.
- Unlike SolidCraft there's no `measure` or `check_parameters` command. The checks are a few lines of Python, which is
  easy because the full OCC shape API (`Volume`, `BoundBox`, `common`, `isValid`) is available.
- STEP export is built in, unlike OpenSCAD.
- Things to watch: reserved words in expressions (`clear`); error messages point at the dependent feature
  ("shape is invalid"), not at the sheet cell that caused it, so check `Params` first. `execute_code` has a 90 s
  default timeout, which is no problem here (a build takes under 1 s).

## Open issues

- Not printed or load tested. `tol` = 0.3 and the insert sizes are guesses. Same sag and creep concern as the other
  builds (552 mm span, 18 × 20 section, PETG).
- With a 1/2 layout both dividers are still placed (at x = 0). Divider_2 should be hidden or left out of the export. An
  expression can't delete a feature; FreeCAD's `Visibility` or a configuration table could, but that wasn't tried.
- `split_x` isn't derived from `bed_x`. For other GN sizes or beds, check that `2·split_x ≤ bed_x` and that the
  seats stay clear of the splice recesses by hand. A sheet cell with an assert-style check would be nice.
- Stretch goal not done: the long bar along the 530 side for 1/4, 1/6, 1/9.
