# Challenge 01: requirements

Collected 2026-11-11. ✅ = confirmed by a source, ⚠️ = estimate or unclear, 📏 = the customer measures it
(see [MEASUREMENTS.md](MEASUREMENTS.md)).

## 1. Reference product (what we're replacing)

**TEKNOSTAHL® GN-Gestell / Halter groß**, item no. 86213254, €19.95 ✅
https://www.gn-profi.de/gn-gestell-halter-gross-fuer-diverse-gn-behaelter-passend/
(the URL **needs the trailing slash**; without it the shop redirects to its home page, which looked
like a 404 to scripts).

A **tilted counter rack** that holds a row of GN pans by their rims, for buffet or prep display.

| Property | Value (shop text) | Note |
|---|---|---|
| Material | Chromnickelstahl, **15 × 15 mm Vierkantrohr** ✅ | Stainless square tube |
| Tilt | **"leicht geneigt (ca. 15 Grad)"** ✅ | The pan plane faces the user |
| Outer size | "Länge: 74 mm ⚠️, Breite: 420 mm, Höhe: 460 mm" | 74 mm is clearly a typo for **740 mm** |
| GN opening | **70 cm × 30 cm** ✅ | Pans hang on two long rails ~300 mm apart, so the 325 mm side of a pan spans them |
| Max pan depth | **200 mm** ✅ | Sets the height under the rails |
| Feet | "rutschhemmende Füße" ✅ | |
| Assembly | "einfache Montage" ✅ | Photos show bolted joints where the side legs cross |
| Combinations | **4 × 1/3, 2 × 2/3, 8 × 1/6 (+ 3 adapters)** ✅ | "Nahezu unbegrenzt" |
| Small pans | **1/6 and 1/9 need the GN adapter** (item 67359222) ✅ | Bar that splits the opening |

**Construction, from the 5 product photos** ([1](https://www.gn-profi.de/media/image/5d/b9/2d/86213254_1FxxEq83mXMgfb_600x600@2x.jpg),
[2](https://www.gn-profi.de/media/image/10/6b/c1/86213254_2_600x600@2x.jpg),
[3](https://www.gn-profi.de/media/image/da/4b/44/86213254_36iE6sZdXtIgI3_600x600@2x.jpg),
[4](https://www.gn-profi.de/media/image/01/16/05/86213254_47hDwgVdhfaNH3_600x600@2x.jpg);
not copied into the repo because they're the shop's photos):
- A **rectangular top frame** (two long rails + two short ends), tilted ~15°.
- **Two side frames**, each bent from one tube: an X/Z shape where the legs cross and are bolted
  together. The back end is a rounded "C" bend that lifts the back of the top frame.
- **Cross rails** between the side frames at the feet keep it square.
- Photo 3: mixed pans in two rows (2 × 1/6 + 2 × 1/6 + 2 × 2/8-style long pans), so the
  adapters/bars make a two-row layout possible.
- Photo 4: the **large holder as the back tier** with the **small holder in front** ("perfekte
  Kombination"). Both are sold to be used together.

### Related products (same shop)
| Product | Specs ✅ | Relevance |
|---|---|---|
| [GN-Gestell / Halter **klein**](https://www.gn-profi.de/gn-gestell-halter-klein-fuer-diverse-gn-behaelter-passend/) (86213252, €24.95) | 6 mm stainless **wire**, slightly tilted, **680 × 160 × 150 mm**, for 1/9, 1/6, 1/3, max depth **100 mm**, no assembly | Possible challenge 01b. It's small, so it's easy to print. |
| [GN-Adapter / Zwischensteg](https://www.gn-profi.de/gn-behaelter-gastronorm-edelstahl-adapter-zwischensteg-325-mm-oder-530-mm/) (67359222, from €3.50) | Stainless bar, **325 mm or 530 mm**, EN 631-1. Use 2 cross bars **or** 1 long bar, never both at once | We can print these as parametric divider bars |

## 2. The GN standard (EN 631-1, DIN 66075 in Germany)

All sizes are fractions of **GN 1/1 = 530 × 325 mm** ✅, nominal = **outer size of the rim**.

| GN | Nominal (mm) ✅ | Across a 300 mm opening? |
|---|---|---|
| 1/1 | 530 × 325 | yes (325 side) |
| 2/3 | 354 × 325 | yes |
| 1/2 | 325 × 265 | yes |
| 1/3 | 325 × 176 | yes |
| 2/4 | 530 × 162 | no, needs a bar |
| 1/4 | 265 × 162 | no |
| 1/6 | 176 × 162 | no |
| 1/9 | 176 × 108 | no |
| 2/8 | 324 × 132 | yes (324 side) |

- Depths ✅: 20, 40, 65, 100, 150, 200 mm nominal. A real "200" can be **226 mm** (Hupfer).
- Fractions add up with ~1 mm play (3 × 176 = 528 ≤ 530).
- Clear opening of a 1/1: 505 × 300 mm ⚠️ → rim ≈ 12.5 mm per side ⚠️ 📏.
- ⚠️ 4 × 1/3 = 4 × 176 = **704 mm**, but the shop says the opening is "70 cm". Either it's rounded,
  or the pans overlap slightly at the rims. 📏 on the real product.

## 3. Requirements for our printed version

### Functional
- **F1** Holds GN pans **by the rim** on two long rails. Default opening **704 × 300 mm** (4 × 1/3), parametric.
- **F2** Takes the shop's combinations: **4 × 1/3, 2 × 2/3, 8 × 1/6**, plus 1/9 with bars.
- **F3** Parametric **divider bars** (longitudinal and/or cross) that click into the rails, replacing
  the steel adapter. Ideally longitudinal and cross bars can be used **together** (the steel one can't).
- **F4** **Tilt** parametric, default **15°**.
- **F5** Clearance under the rails for the deepest pan: default **200 mm** (226 real), parametric.
- **F6** Stable when full: 4 × 1/3 × 200 mm of liquid ≈ 4 × 5.7 L ≈ **23 kg**. No tipping forward at 15°.
- **F7** Non-slip feet (TPU pads, printed; we have TPU printers).
- **F8** Optional: stacks or combines with a **front tier** (the "klein" holder) like photo 4.
- **F9** Easy to clean; no deep slots where food collects.

### Parametric (minimum set)
| Parameter | Default | Source |
|---|---|---|
| `opening_l` | 704 | 4 × 1/3 nominal 📏 |
| `opening_w` | 300 | Shop ✅ 📏 |
| `rim_w` | 12.5 | ⚠️ 📏 |
| `rim_t` | — | 📏 Rim thickness (sets the rail lip) |
| `tilt` | 15° | Shop ✅ |
| `max_depth` | 200 (+26 tolerance) | Shop ✅, Hupfer ✅ |
| `front_h` | — | 📏 Height of the front rail above the table |
| `rail_section` | 15 × 15 → printed profile tbd | Shop ✅ |
| `bars` | `[]` | List of divider positions |
| `bed` | depends on printer, see §4 | |
| `play` | 1.0 | Fit, tune after a test print |

### Printability
- **P1** Every part fits the chosen printer. Splits and joints are parametric (bolted M5 +
  heat-set inserts, or dovetails).
- **P2** No supports where possible (rails printed lying down, the rim lip ≤ 45°).
- **P3** Material: **PETG** (cold/room temperature) by default. **ASA/PC** if the pans are hot (bain-marie or
  steam 65–90 °C). PLA creeps under 23 kg, so no PLA for load-bearing parts.
- **P4** Long rails (≥ 704 mm) are the weak point for bending. Options: print on the big printer,
  or a printed rail with a **steel/aluminium rod or tube** inside (hybrid). Decide after a load
  estimate.

### Verification
- **V1** Customer measurements → parameter values ([MEASUREMENTS.md](MEASUREMENTS.md)).
- **V2** Test print of **one rail section + one end joint + one bar seat**; fit with a real 1/3 and 1/6 pan.
- **V3** Load test: 4 × 1/3 full of water for 24 h. Check deflection and creep.
- **V4** Tipping test at 15° with only the front row full.

## 4. Printers available (ifsmb.de equipment list)

From https://github.com/falkorichter/ifsmb.de (`_equipment/`):

| Printer | Build volume | Fit for this job |
|---|---|---|
| **Elegoo OrangeStorm Giga** (Philippe Bietenholz) | **800 × 800 × 1000 mm** | Whole rack or whole side frames **in one piece**. Long rails without joints. |
| German RepRap X400 | ~400 × 390 × 320 mm | Side frames (420 × 460) almost fit; rails in 2 parts |
| FLSUN V400 (delta) | Ø 300 × 410 mm | Smaller parts, tall pieces |
| Snapmaker U1 (enclosed, 4 toolheads) | 270 × 270 × 270 mm | **Enclosed**, so good for ASA/PETG. Multi-material (PETG + TPU feet in one print) |
| Prusa MK4 + MMU | 250 × 210 × 220 mm | Joints, bars, test pieces |
| 2 × Bambu Lab P2S + AMS (Rosalind-Franklin-Gymnasium) | ~256 × 256 × 256 mm | Enclosed |
| Prusa MK3S (xHain, enclosed, hardened nozzle) | 250 × 210 × 210 mm | PETG proven; CF filaments possible |
| LulzBot TAZ 6 / Mini | | TPU feet |
| Bambu A1 mini | 180 × 180 × 180 mm | Test pieces |

→ Two design variants, chosen by one parameter:
- **Variant G (Giga):** few large parts, minimal joints.
- **Variant S (small bed, 250 mm class):** split into ≤ 250 mm parts with bolted joints.
Both come from the same parametric model.

## 5. Toolchain notes (for the comparison)
- OpenSCAD: mesh only, no STEP.
- SolidCraft MCP: works (headless smoke test OK). STEP + STL.
- Onshape FeatureScript MCP: remote server **`https://fs-mcp.labs.onshape.app/mcp`** (HTTP transport)
  ✅ (Onshape blog). It makes a *custom feature*, so the rack would become a reusable "GN rack"
  feature with parameters in the Onshape UI. See [../../docs/onshape-mcp/LOG.md](../../docs/onshape-mcp/LOG.md).

## 6. Open questions
- [ ] Customer measurements (see [MEASUREMENTS.md](MEASUREMENTS.md)).
- [ ] Hot or cold use? (material P3)
- [ ] Which printer: can we book the OrangeStorm Giga? (variant G vs S)
- [ ] Copy exactly (4 × 1/3 in a 15° tube rack) or improve (bars in both directions, tier stacking)?
- [ ] Also do the "klein" holder as challenge 01b?

## Sources
- Product: https://www.gn-profi.de/gn-gestell-halter-gross-fuer-diverse-gn-behaelter-passend/
- Small holder: https://www.gn-profi.de/gn-gestell-halter-klein-fuer-diverse-gn-behaelter-passend/
- Adapter bar: https://www.gn-profi.de/gn-behaelter-gastronorm-edelstahl-adapter-zwischensteg-325-mm-oder-530-mm/
- Wikipedia, Gastronorm sizes: https://en.wikipedia.org/wiki/Gastronorm_sizes
- Hupfer datasheet: https://www.hupfer.com/de/additionalProductInfo/pdf/sOrdernumber/0130622H/sArticle/281
- 505 × 300 inner size: https://www.barstuff.com/gastronormbehalter-65mm-tiefe-edelstahl-gn-1-1.html
- Printers: https://github.com/falkorichter/ifsmb.de/tree/main/_equipment
- Onshape FeatureScript MCP: https://www.onshape.com/en/blog/featurescript-mcp-server-enables-text-code-cad
