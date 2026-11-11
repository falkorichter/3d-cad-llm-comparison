# Challenge 01: GN container holder

**Status:** research (started 2026-11-11)

## Task (as given)

> Ein Behälter für Gastro-Behälter, 3D-druckbar und parametrisch.

A holder/rack for gastronorm (GN) containers that is **3D printable** and **parametric**.

Reference product: [TEKNOSTAHL GN-Gestell / Halter groß](https://www.gn-profi.de/gn-gestell-halter-gross-fuer-diverse-gn-behaelter-passend/)
(gn-profi.de, €19.95). It's a counter rack of 15 × 15 mm stainless tube, tilted ~15°, with a GN
opening of 70 × 30 cm, for pans up to 200 mm deep (4 × 1/3, 2 × 2/3, 8 × 1/6 with adapter bars).
The link only works **with the trailing slash**.

- [REQUIREMENTS.md](REQUIREMENTS.md): product analysis, GN standard, requirements, parameters, printers
- [MEASUREMENTS.md](MEASUREMENTS.md): measurement list for the customer (German)
- [DESIGN.md](DESIGN.md): shared build brief v1 for the agents. It predates the product analysis above, see the note in it
- [LOG.md](LOG.md): what we did, in date order

The customer will supply the measurements. Until then the parameters use the nominal GN values.

## Why this is a good first challenge

- Real-world part with a hard external standard (GN / EN 631), so the result can be checked.
- Needs to be parametric (GN size, depth, number of slots), which separates the toolchains.
- Larger than a typical print bed, so it forces design decisions (split, joints, frame vs. solid).

## Toolchains to compare

| Toolchain | Folder | Status |
|---|---|---|
| OpenSCAD (baseline) | `openscad/` | v1 in progress (agent, 2026-11-11). Built to [DESIGN.md](DESIGN.md) v1, a flat 1/1 frame; see [LOG.md](LOG.md) |
| SolidCraft via MCP | `solidcraft/` | v1 in progress (agent, 2026-11-11). Built to [DESIGN.md](DESIGN.md) v1, a flat 1/1 frame; see [LOG.md](LOG.md) |
| Onshape FeatureScript MCP | `onshape/` | not started. MCP registered (HTTP + OAuth); authenticate via `/mcp` first |
| CADCraft | none | **not applicable**: CADCraft is 2D only. Could later make a dimensioned drawing of the result |

For each one, record the time it took, how many prompts and corrections were needed, whether it
exports STEP and STL, and print results.
