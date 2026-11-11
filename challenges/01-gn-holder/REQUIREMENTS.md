# Challenge 01: requirements research

Researched 2026-11-11. ✅ = confirmed by a source, ⚠️ = estimate, still needs measuring on a real pan.

## 1. The reference product

- URL: https://www.gn-profi.de/gn-gestell-halter-gross-fuer-diverse-gn-behaelter-passend
- **The page returns HTTP 404** (checked 2026-11-11), and a web search found no copy or cached
  version. We don't have its dimensions or photos yet.
- gn-profi.de is a shop for stainless steel GN containers, lids and accessories (1/9 to 1/1). The
  product was probably in its "GN Zubehör" category: https://www.gn-profi.de/gn-zubehoer/
- From the name ("GN-Gestell / Halter **groß** / für **diverse** GN-Behälter passend"), it's a
  frame/stand that holds GN containers of several sizes. "Groß" probably means a large (1/1-sized)
  footprint.

> ❓ Open: what did the product actually look like? See [§6 Open questions](#6-open-questions).
> A screenshot or photo would settle this.

## 2. The GN standard (EN 631-1, DIN 66075 in Germany)

All GN sizes are fractions of **GN 1/1 = 530 × 325 mm** ✅. The nominal size is the **outer size of
the rim**.

| GN | Nominal (mm) ✅ | Fits in 1/1 as | Spans 325 mm side? |
|---|---|---|---|
| 2/1 | 650 × 530 | (two 1/1s) | — |
| 1/1 | 530 × 325 | 1 | yes |
| 2/3 | 354 × 325 | + 1/3 | yes |
| 2/4 | 530 × 162 | 2 side by side | no (needs a bar along the length) |
| 1/2 | 325 × 265 | 2 | yes |
| 1/3 | 325 × 176 | 3 | yes |
| 1/4 | 265 × 162 | 2 × 2 | no |
| 1/6 | 176 × 162 | 3 × 2 | no |
| 1/9 | 176 × 108 | 3 × 3 | no |
| 2/8 (rare) | 324 × 132 | | |
| 1/12, 2/24, 1/18 (rare) | 162 × 88, 132 × 108, 108 × 88 | | |

- **Depths** ✅: 20, 40, 65, 100, 150, 200 mm (nominal). The real height can be slightly more: one
  Hupfer "200" pan is 226 mm.
- Fractions add up with **~1 mm of play**: 3 × 176 = 528 ≤ 530, and 2 × 162 = 324 ≤ 325.
- **Clear inside opening** of a 1/1 pan: **505 × 300 mm** (one retailer) ⚠️. That gives a
  **rim/flange of about 12.5 mm** per side ⚠️. Rim width, corner radius and wall taper vary by
  manufacturer, and no source we found states them.
- Pans hang **by the rim** in a frame (bain-marie, saladette, cutout in a counter). Smaller pans that
  don't span the 325 mm side need **divider bars (Trennstege)** with a ledge on both sides.

## 3. What "the holder" could be

| # | Type | What it does | Print difficulty |
|---|---|---|---|
| A | **Insert frame / rack (Einsatzrahmen, Gestell)** | Open frame with a 1/1 outline (~540 × 335 outside). Pans hang in by their rim. Movable divider bars for 1/2, 1/3, 1/4, 1/6, 1/9. Stands on legs or on a table. | Bigger than any common bed, so it must be split and joined. |
| B | **Storage stand (Ständer)** | Holds empty pans and lids upright in slots, like a dish rack. | Smaller pieces. Slot pitch follows pan depth and rim thickness. |
| C | **Counter riser / buffet stand** | Holds 1–3 pans at an angle or a height for display. | Medium. |

My working guess is **A**, because "Gestell … für diverse GN-Behälter" sounds like a frame that takes
mixed fractions. This needs confirming.

## 4. Requirements (draft)

### Functional
- R1: Holds GN containers **by the rim**, with a 1/1 outline (530 × 325 nominal opening plus play).
- R2: Takes **mixed fractions** (1/1, 2/3, 1/2, 1/3, 1/4, 1/6, 1/9) via **movable/removable divider bars**.
- R3: Enough clearance under the frame for the deepest pan we want (parameter, default 150 mm, max 200).
- R4: Stable when full. A full 1/1 × 150 pan with water weighs about 20 kg (~19 L).
- R5: Food environment: easy to wipe and no deep crevices. The plastic should be food-safe if food
  ever touches it (normally only the steel pan touches food).

### Parametric (minimum set)
| Parameter | Default | Note |
|---|---|---|
| `gn_l`, `gn_w` | 530, 325 | GN 1/1 nominal |
| `play` | 1.0 | Gap between pan rim and frame, per side |
| `rim_w` | 12.5 | Rim width of the pan, measure ⚠️ |
| `ledge_w` | 8 | How far the frame supports the rim |
| `max_depth` | 150 | Deepest pan, sets the leg height |
| `layout` | `["1/3","1/3","1/3"]` | Which divider bars to place |
| `bed_x`, `bed_y` | 256, 256 | Printer bed, drives splitting |
| `wall`, `bar_h` | tbd | From the strength check |

### Printability
- R6: Every part fits on the **print bed** (`bed_x × bed_y`). The 1/1 frame (≥ 540 × 335) must be
  split into at least 4–6 parts, joined with dovetails, pins or bolts (M4/M5 + heat-set inserts).
- R7: Prints without supports (ledges ≤ 45° overhang, or printed upside down).
- R8: Material: **PETG** (dishwasher-ish, 70–80 °C, tougher) is preferred over PLA (creeps under
  load and softens near hot pans). Use ASA or PC near steam tables or bain-maries (65–90 °C).
- R9: Tolerances parametric, so they can be tuned to the printer.

### Verification
- V1: Measure a real 1/1 pan and a 1/3 pan (rim width, rim thickness, corner radius, taper) before
  finalising `rim_w`/`ledge_w`.
- V2: Print a **corner test piece** first (one ledge corner + one divider seat) and check the fit
  with real pans.
- V3: Load test: a full 1/1 × 150 pan on the assembled frame for 24 h. Check for creep.

## 5. How we compare toolchains on this
Same parameter table in each tool → STL for printing (+ STEP where possible) → photos and fit notes.
OpenSCAD can't export STEP; SolidCraft and Onshape can.

## 6. Open questions
- [ ] Which type: **A** frame/rack, **B** storage stand, **C** riser?
- [ ] Which printer and bed size?
- [ ] Which GN mix must it take (e.g. 3 × 1/3 only, or anything down to 1/9)?
- [ ] Hot use (bain-marie, steam) or cold/storage only? This decides PLA/PETG/ASA.
- [ ] Do we have a real pan to measure the rim?

## Sources
- Wikipedia, Gastronorm sizes: https://en.wikipedia.org/wiki/Gastronorm_sizes
- gn-profi.de (shop; product page 404): https://www.gn-profi.de/
- Hupfer GN datasheet (200 mm pan = 226 mm high): https://www.hupfer.com/de/additionalProductInfo/pdf/sOrdernumber/0130622H/sArticle/281
- Inner opening 505 × 300 for 1/1: https://www.barstuff.com/gastronormbehalter-65mm-tiefe-edelstahl-gn-1-1.html
- Hotel pan size guide (flange variation between brands): https://www.gofoodservice.com/guides/hotel-pan-sizes
