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
- [ ] Record the agent results (time, tool calls, corrections, bed-fit, issues) here when they finish.
- [ ] v2 brief from REQUIREMENTS.md §3 (tilted rack), then rebuild.
