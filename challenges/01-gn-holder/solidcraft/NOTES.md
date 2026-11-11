# Challenge 01: GN 1/1 insert frame in SolidCraft (MCP)

Built 2026-11-11 by a Claude agent driving SolidCraft through its MCP server (headless
in-process session, the SolidCraft app was not running). Spec: [../DESIGN.md](../DESIGN.md) v1.

## Files

| Path | What |
|---|---|
| `gn_holder.sc` | Parametric design: one design, one body per placed part (18 bodies) |
| `step/gn_holder_assembly.step` | Whole assembly (18 bodies, coloured by part type in the .sc) |
| `step/{corner_a,corner_b,rail_middle,splice_plate,leg,divider}.step` | One STEP per part type |
| `stl/{corner_a,corner_b,rail_middle,splice_plate,leg,divider}.stl` | One STL per printed part type |
| `renders/assembly_iso.png` | Assembly, colour per part type |
| `renders/part_corner_top.png`, `renders/part_corner_bottom.png` | Split part: corner A from above (pocket, ledge, leg bolt counterbore) and below (splice recesses, insert holes, leg socket) |
| `renders/part_rail_with_dividers.png` | Middle rail with its three seat notches and the two divider bars seated |

## Approach

Everything is in one design, centred on the origin, Z up, frame bottom at Z = 0, legs going
down to Z = -`leg_h`. All sizes and positions are parameter expressions.

1. **Frame ring** from three `solid.box` features: outer block `out_l × out_w × bar_h`, rim
   pocket `open_l × open_w` cut `rim_t` deep from the top, through-hole `hole_l × hole_w`.
   The rail cross-section is an L: the wall (10 × 20) plus the ledge (8 wide), with the ledge
   top at `bar_h − rim_t` = 18 above the rail bottom. The ledge is solid down to the rail
   bottom (see "Deviations").
2. **Divider seats**: box cuts in the ledge of both long rails, `div_w + 2·tol` wide and
   `ledge_t` deep, at x = 0 (1/2) and x = ±`open_l/6` (1/3, and also where 2/3 meets 1/3,
   because 354 + 176 = 530 puts that boundary at the same place).
3. **Joint and leg features** cut into the whole ring before it is split: splice-plate
   recesses, heat-set insert holes, leg sockets, leg bolt holes.
4. **Split** with `solid.split_body` at x = ±`split_x` and on the XZ plane into 4 corners +
   2 middle rails (see the split bug below).
5. **Separate parts**: splice plates, legs (spigot + insert hole), divider bars. Copies for the
   assembly come from `solid.mirror {bodies}` and `solid.move {copy}` with expression translations.

### `layout`
SolidCraft expressions have no `if`, so the layout is two unitless 0/1 flags:
`seat_half` (seats at the 1/2 position) and `seat_third` (seats at the 1/3 and 2/3|1/3
positions). A disabled seat cutter is moved 40 mm into the through-hole, so it cuts nothing
and the volume is unchanged. The two divider bodies sit at x = ±`open_l/6·seat_third` (both
end up at x = 0 for a 1/2 layout). Default is `layout = [1/3, 1/3, 1/3]`, so both flags are 1
and 2 divider bars are placed. SolidCraft also has configuration rules that switch feature
suppression; I did not try them.

## Joint choice: M4 screws + recessed splice plates (not dovetails)

- 6 joints: 4 across the long rails at x = ±125 and 2 across the short rails at y = 0.
- Each joint has a 68 × 18 × 4 mm splice plate in a recess in the rail bottom
  (`sp_len + 2·tol` long, `sp_t` deep), so the bottom stays flat. The plate sits on the
  tension side of the rail when it sags.
- 4 × M4 per plate (2 each side of the joint, at 10 and 24 mm from it): M4 × 12 screws go up
  through Ø4.5 holes in the plate into M4 heat-set inserts (Ø5.6 × 8 holes) in the rail.
  Nothing shows on the top surface where the pan rims sit.
- Why not dovetails: the rail band is only 18 mm wide (`wall + ledge_w`), so a dovetail would
  leave thin necks. The splice is also easy to keep parametric with box and cylinder
  primitives and rectangular patterns.

**Legs** are separate 30 × 30 posts, printed standing. Each one has a 6 × 6 × 7.5 spigot in a
6.6 × 8 socket in the corner (anti-rotation) and is held by one M4 × 30 from the top: Ø4.5
through the corner with an Ø8 × 4 counterbore in the wall band, into a heat-set insert
(Ø5.6 × 12) in the leg top. The leg's inner faces line up with the through-hole, so the leg
sticks out 12 mm past the outer frame. That keeps the through-hole (pan path) completely
clear, and the wider stance helps stability.

## Part list and bed check (256 × 256, build height 250)

From `measure` and from the exported STL bounding boxes (they agree):

| Part (STL) | Count | Bbox mm (as modelled) | Print orientation | Fits bed |
|---|---|---|---|---|
| `corner_a` (Corner_PP / Corner_NN) | 2 | 151 × 173.5 × 20 | top up | yes |
| `corner_b` (Corner_PN / Corner_NP, mirror of A) | 2 | 151 × 173.5 × 20 | top up | yes |
| `rail_middle` (Rail_P / Rail_N, identical by 180° turn) | 2 | 250 × 18 × 20 | top up | yes (6 mm margin) |
| `splice_plate` | 6 | 68 × 18 × 4 | flat | yes |
| `leg` | 4 | 30 × 30 × 172.5 (165 + spigot 7.5) | standing, spigot up | yes (172.5 ≤ 250 height) |
| `divider` | 2 (default layout) | 16 × 326.4 × 18 | upside down (tabs on the bed), 45° on the bed | yes, diagonally: a 45° copy measured 242.1 × 242.1 |

Hardware: 24 × M4 × 12 (splices), 4 × M4 × 30 (legs), 28 × M4 heat-set inserts.
Total plastic is about 1.36 dm³, roughly 1.75 kg PETG at 100 % infill (much less at normal infill).

None of the parts need supports. The frame parts print top up: every feature is a vertical
wall or a downward-open recess, the pocket and seats open upward, and the sockets and
recesses open downward onto the bed. The leg is a straight prism. The divider prints
upside down, so its 8 mm end tabs lie on the bed.

## Checks

**Volumes per stage.** Each batch passed an `expect` with numbers worked out by hand:

| Stage | Expected mm³ | Measured mm³ |
|---|---|---|
| Ring + pocket + through-hole | 594 384 | 594 384.0 |
| + 6 seat notches | 591 196.8 | 591 196.8 |
| + leg holes, sockets, 6 recesses | 558 345.6 | 558 346.9 |
| + 24 insert holes | 553 617.9 | 553 621.0 |
| Full assembly, 18 bodies | 1 356 203.9 | 1 356 204.3 |

The middle rail alone was checked by hand too: 344 mm² × 250 − 3 notches − 2 half-recesses
− 4 inserts = 78 679.0, and `measure` gives 78 679.3.

**Derived dimensions** (`parameters` + `measure`):
- Outer frame: bbox of the frame bodies is x ±276, y ±173.5, so **552 × 347** ✓
- Opening (rim pocket): `open_l × open_w` = **532 × 327** ✓. The volume after the pocket cut
  matches 532·327·2 exactly.
- Through-hole: **516 × 311** ✓ (`hole_l`, `hole_w`, and the middle rail's inner face is at y = 155.5)
- Clearance: the frame bottom (which is also the bottom of the ledge) is at Z = 0 and the leg
  bottom is at Z = −165, so **165 mm** ✓. With `max_depth = 100` it is −115 ✓.
- Hole positions from `body_topology` cylinders: inserts at x = 135/149 (split_x + 10/24),
  y = 164.5 (band centre). Short-joint inserts at x = 267, y = 10/24. Leg bolt at (271, 168.5)
  with counterbore z 16…20. All as planned.
- `inspect.interference` over all 18 bodies: 0 overlaps (30 pairs checked exactly).

**Parametric checks** (`check_parameters`, and a coalesced batch that set the values and put them back):
- **GN 2/3** (`gn_l = 354`): no errors and no warnings after the fix below. Corners shrink to
  x 125…188, the short splice moves to x = ±179, leg bolts and leg inserts to x = ±183,
  dividers to x = ±59.33 (= 356/6). All cylinders follow.
- **`max_depth = 100`**: legs become 115 tall (Z min −115), and leg volume drops by exactly
  4 × 30·30·50.
- **`seat_half = 0`, `seat_third = 0`**: the middle rail gains exactly 3 × 531.2 mm³ (its notches
  close up), and the dividers move to x = 0.

## Deviations and interpretations

- **Ledge thickness.** The ledge is solid from the rim pocket floor down to the rail bottom
  (18 mm) instead of a 4 mm shelf. That needs no supports and gives no crevice. It also makes
  the rail stiffer: the section is a full 18 × 20 instead of a 10 × 20 wall with a 4 mm lip.
  `ledge_t` sets the seat-notch depth and the divider tab thickness instead.
- "Top of the ledge = `bar_h − rim_t` below the top surface" in DESIGN.md is read as "above
  the rail bottom" (z = 18), because the rim pocket is `rim_t` deep.
- The divider bars sit in seats on the long rails only. The stretch-goal long bar for
  1/4, 1/6 and 1/9 is not modelled.
- `split_x` is a separate parameter (125). It is not worked out from `bed_x`, so for other GN
  sizes or beds check the middle rail length (`2·split_x` ≤ `bed_x`) by hand. The seats at
  ±88.7 must also stay clear of the splice recess (91…159), which holds for GN 1/1.

## SolidCraft issues and limits hit (candid)

1. **Bug: `solid.hole` with an expression `position` does not follow parameters.** The feature
   stores the expressions (`at: ["open_l/2 + wall/2", …]`), but the rebuild uses the frozen
   numeric `position` [271, 168.5, 20]. With `gn_l = 354` it warned "the hole's position
   [271, 168.5, 20] is no longer on face `F1:+z`: it stays where it was placed", and the leg
   bolt holes were left outside the shrunken corner. This contradicts reference.md, which says
   the hole "then follows" length expressions. Fix: I deleted the hole and its pattern and
   inserted two `solid.cylinder` cuts (shaft + counterbore) with patterns at that place in the
   timeline (`timeline.roll_to`, add, roll to end). After that, GN 2/3 rebuilds cleanly.
2. **Limit: no "separate lumps / split into bodies" command.** The middle piece left after the
   two x splits is one body with two disjoint lumps (the +y and −y rails). `split_body` on XZ
   refused it with "the tool does not split the body", because that plane goes through the
   hole and misses both lumps. Workaround: `solid.move {copy}` the body, then cut away y < 0
   from one copy and y > 0 from the other with `solid.box` cuts that use `targets`.
3. **Body naming after splits** is mechanical ("Frame (1) (1) (1)", "Frame (1)'"). I had to
   `measure` to find out which body was which and then rename all of them. Renames survived
   the timeline edit (the roll back and insert) fine.
4. `solid.move` with `angle` rotates about the world origin. There is no pivot parameter for
   bodies (only for occurrences), so the short splice plates were built as their own feature
   instead of a rotated copy.
5. No `if` in expressions. The layout is done with 0/1 flags and by moving the cutter out of the material.
6. No crashes (`crash_reports` is empty). Nothing was refused for file access, and saving to the worktree worked.

Things that worked well: `batch` with `expect` (volume and bbox) caught nothing wrong, but it
proved every stage in the same call. `check_parameters` with `cylinders` is a very cheap way
to prove that holes follow parameters, and it is how the hole bug showed up. Expression
fields in `solid.box`, `solid.cylinder`, pattern spacings and the `split_body` plane origin
all followed parameters. `inspect.interference` is fast (0.27 s for 18 bodies).

## Effort

- Wall-clock: about 11 min of tool time (08:39 to 08:50 by the shell clock) plus writing these
  notes, about 15 min in total.
- About 45 tool calls in all, of which about 30 were SolidCraft calls (11 build batches/executes,
  the rest measures, checks, renders and exports).
- Corrections: 2. (a) A batch was refused by `split_body` on the two-lump middle body, so I
  switched to copy + targeted cuts. (b) The `solid.hole` expression bug was found by
  `check_parameters`, so I replaced it with cylinder cuts. No rebuilds from scratch.

## Open issues

- **Stiffness/creep**: a rough beam estimate for an 18 × 20 PETG rail over 552 mm with a full
  1/1 × 150 pan (about 20 kg) gives a few mm of sag, before joint play. Do the V3 load test.
  Raising `bar_h` is the parametric fix (everything follows), or add a centre leg.
- Leg racking: one M4 + a 6 mm spigot per leg. Add cross-bracing or a second bolt if it wobbles.
- The divider bar body is a solid 16 × 18 bar (about 117 g each). It could be lightened.
- Rim estimate (`rim_w`, `rim_t`) still needs a real pan (V1). Print a corner test piece first (V2).
- Screw heads of the splice screws stick out about 3 mm under the rail bottom. Use countersunk
  screws with a countersink in the plate if that matters.
