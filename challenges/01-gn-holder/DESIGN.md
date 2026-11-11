# Challenge 01: shared design brief (v1)

> ⚠️ **Superseded by the product analysis.** This brief was written before
> [REQUIREMENTS.md](REQUIREMENTS.md) identified the reference product as the TEKNOSTAHL **tilted
> counter rack** (15°, 704 × 300 opening, 200 mm deep pans, Giga or 250 mm-class printers). v1 is a
> **flat GN 1/1 insert frame for a 256 mm bed**. The v1 builds are still useful for comparing the
> toolchains, but a v2 brief has to follow REQUIREMENTS.md §3.

Written 2026-11-11 so that every toolchain builds **the same design** and the results can be compared.
The open questions in [REQUIREMENTS.md §6](REQUIREMENTS.md#6-open-questions) are still open, so this
brief uses these **assumed answers**. Change them here once they're confirmed.

| Question | Assumed for v1 |
|---|---|
| Type | **A**: an insert frame/rack with a GN 1/1 outline, on legs. Pans hang by their rim. |
| Printer | 256 × 256 mm bed (`bed_x`, `bed_y`), 250 mm build height |
| GN mix | Any mix that a **removable divider bar** across the 325 side allows (1/1, 2/3, 1/2, 1/3), plus one **long bar** along the 530 side for 1/4, 1/6, 1/9 (stretch goal) |
| Use | Cold/storage, PETG |
| Real pan | Not available: use the estimates below |

## Parameters (same names in every tool)

| Name | Default | Meaning |
|---|---|---|
| `gn_l`, `gn_w` | 530, 325 | GN 1/1 nominal (outer rim) |
| `play` | 1.0 | Gap per side between the pan rim and the frame |
| `rim_w` | 12.5 | Pan rim width (estimate) |
| `ledge_w` | 8 | How far the ledge reaches under the rim, inward from the opening |
| `ledge_t` | 4 | Ledge thickness |
| `rim_t` | 2 | Pan rim thickness (the rim sits in a pocket this deep, so it ends flush with the top) |
| `wall` | 10 | Frame wall thickness outside the opening |
| `bar_h` | 20 | Frame rail height |
| `max_depth` | 150 | Deepest pan |
| `clear` | 15 | Clearance under the deepest pan |
| `leg` | 30 | Leg cross-section (square) |
| `div_w` | 16 | Divider bar width (holds a rim on both sides: 2 × ledge plus tolerance) |
| `tol` | 0.3 | Fit tolerance for joints and removable parts |
| `bed_x`, `bed_y` | 256, 256 | Every printed part must fit (lying flat, rotation allowed) |

These are the derived sizes. Check against them.

- Opening (rim pocket): `gn_l + 2·play` × `gn_w + 2·play` = **532 × 327**
- Through-hole under the ledge: opening − 2·`ledge_w` = **516 × 311**. A pan body (about 505 × 300)
  must pass through it.
- Outer frame: opening + 2·`wall` = **552 × 347**
- Top of the ledge = `bar_h − rim_t` below the top surface. Total height: legs give
  `max_depth + clear` = **165 mm** of free space below the bottom of the ledge.

## Required features
1. A rectangular **frame rail** with an inner rim pocket and ledge, all round.
2. **4 legs** at the corners, either printed into the corner pieces or as separate parts with a joint.
3. **Split into printable parts.** The 552 × 347 ring doesn't fit on a 256 bed, so split it (for
   example 4 corners + 2 long middle segments, or 6 segments). Join the parts with **dovetails or
   M4 bolts and splice plates**: pick one and document it. Each part must fit inside `bed_x × bed_y`.
4. **Divider seats.** Notches or slots in the long rails at the 1/2 and 1/3 positions (and where 2/3
   meets 1/3), so a removable cross divider bar can sit in them, flush with the top.
5. **Cross divider bar** (325 side): it has a ledge on both sides and sits in the seats. If it doesn't
   fit the bed lying flat, split it or show that it fits diagonally (the bed diagonal is 362 mm).
6. A parametric `layout` (or equivalent) that chooses which seats or dividers are generated.
7. No supports needed (ledges ≤ 45°, or the orientation is chosen to avoid them).

## Deliverables per toolchain (`challenges/01-gn-holder/<tool>/`)
- The source (`.scad`, `.sc` and so on) with the parameters above
- `stl/`: one STL per printed part (and a count of how many of each part)
- STEP for the assembly and the parts, where the tool can export it
- `renders/`: an assembly render, plus at least one render of a split part
- `NOTES.md`: approach, part list and bed-fit check (bbox of each part against 256 × 256), the joint
  choice, how you checked the derived sizes, what was hard, any tool bugs or limits, how long it took
  and the number of tool calls or corrections, and open issues
