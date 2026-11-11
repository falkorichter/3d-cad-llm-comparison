# Challenge 01: GN container holder

**Status:** research (started 2026-11-11)

## Task (as given)

> Ein Behälter für Gastro-Behälter, 3D-druckbar und parametrisch.

A holder/rack for gastronorm (GN) containers that is **3D printable** and **parametric**.

Reference product: [GN-Gestell / Halter groß für diverse GN-Behälter passend](https://www.gn-profi.de/gn-gestell-halter-gross-fuer-diverse-gn-behaelter-passend)
(gn-profi.de; the link returned HTTP 404 on 2026-11-11, so details are reconstructed from other
sources, see [REQUIREMENTS.md](REQUIREMENTS.md)).

## Why this is a good first challenge

- Real-world part with a hard external standard (GN / EN 631), so the result can be checked.
- Needs to be parametric (GN size, depth, number of slots), which separates the toolchains.
- Larger than a typical print bed, so it forces design decisions (split, joints, frame vs. solid).

## Toolchains to compare

| Toolchain | Folder | Status |
|---|---|---|
| OpenSCAD (baseline) | `openscad/` | not started |
| SolidCraft via MCP | `solidcraft/` | not started |
| Onshape FeatureScript MCP | `onshape/` | not started |

For each one, record the time it took, how many prompts and corrections were needed, whether it
exports STEP and STL, and print results.
