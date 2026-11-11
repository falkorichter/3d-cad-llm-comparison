# FeatureScript, OpenSCAD and SolidCraft: three ways to describe a part

Written 2026-11-11, after challenge 01 was built in all three
([LOG](../challenges/01-gn-holder/LOG.md)). Same part, same parameters, three very different kinds of
source file.

**In one line:** OpenSCAD and FeatureScript are **programs that generate a model**. SolidCraft (like
Onshape's or Fusion's normal UI) stores a **model as a list of features**, and the agent built that list
by sending commands.

| | OpenSCAD | Onshape FeatureScript | SolidCraft |
|---|---|---|---|
| Source of truth | `gn_holder.scad` (code) | `gn_holder.fs` (code), in a Feature Studio | `gn_holder.sc`: zip with `document.json` (feature list) |
| How the agent wrote it | wrote the file, ran the CLI | wrote the file, `test_feature` via MCP | **no file written**: ~11 `batch` calls of commands over MCP |
| Geometry kernel | CSG on meshes (CGAL; Manifold in newer builds) | Parasolid B-rep, in the cloud | own B-rep kernel, local app |
| Exact faces/edges, STEP | no (mesh only, no STEP) | yes | yes |
| Parameters | top-level variables (+ Customizer comments) | `precondition` → a dialog in the UI | named parameters with expressions (`open_l = gn_l + 2*play`) |
| Loops, `if` | yes | yes | **no**: patterns, mirrors, 0/1 flags instead |
| Can pick existing faces/edges | no | yes (queries) | yes (pick by point, follows the face) |
| Measure inside the model | no (external scripts) | yes (`evVolume`, `evBox3d`) | yes, from outside (`measure`, `body_topology`) |
| Where it runs | locally, free | Onshape servers (API calls when driven by MCP) | locally, free |
| Diff in git | good | good | poor (zip; JSON inside is readable) |
| Result in the UI | none (a viewer only) | **one feature** in a normal Onshape timeline, with a dialog | a timeline of 58 normal features |

## The same first steps in all three

Outer block, rim pocket, through-hole. That's the start of the frame in every build.

**OpenSCAD**: CSG expressions. `difference()` subtracts every child after the first from the first:

```openscad
difference() {
    translate([-out_l/2, -out_w/2, 0])          cube([out_l, out_w, bar_h]);
    translate([-open_l/2, -open_w/2, bar_h-rim_t]) cube([open_l, open_w, rim_t + 1]);
    translate([-hole_l/2, -hole_w/2, -1])       cube([hole_l, hole_w, bar_h + 2]);
}
```

**FeatureScript**: you call operations on a `context` (the Part Studio). Every operation needs a unique
`id`, and bodies are found later with queries:

```javascript
const frame = gnBox(context, id + "outer", -m.outL / 2, -m.outW / 2, 0 * millimeter, m.outL / 2, m.outW / 2, H);
tools = append(tools, gnBox(context, id + "pocket", -m.openL / 2, -m.openW / 2, m.zl, m.openL / 2, m.openW / 2, H + EPS));
tools = append(tools, gnBox(context, id + "hole", -m.holeL / 2, -m.holeW / 2, -EPS, m.holeL / 2, m.holeW / 2, H + EPS));
opBoolean(context, id + "cut", { "tools" : qUnion(tools), "targets" : frame,
                                 "operationType" : BooleanOperationType.SUBTRACTION });
```

**SolidCraft**: no code. These are three entries in `document.json`, made by `solid.box` commands with
expression strings. They're stored as data, and the app rebuilds them when a parameter changes:

```json
{"id": 1, "type": "box", "name": "FrameBlock", "operation": "new_body",
 "length": "out_l", "width": "out_w", "height": "bar_h",
 "corner": ["(0 mm) - (out_l) / 2", "(0 mm) - (out_w) / 2", "(bar_h/2) - (bar_h) / 2"]}
{"id": 2, "type": "box", "name": "RimPocket", "operation": "cut",
 "length": "open_l", "width": "open_w", "height": "rim_t + 1 mm", ...}
{"id": 3, "type": "box", "name": "ThroughHole", "operation": "cut", ...}
```

## FeatureScript in more detail

**What it is.** Onshape's own language for features. Every built-in Onshape tool (Extrude, Fillet, Hole…)
is written in FeatureScript, and that standard library is public. A *custom feature* that you write is
the same kind of thing. It appears in the toolbar, and you insert it into a Part Studio's feature list
next to sketches and extrudes made by hand. Other people can use it from their own documents.

**What a feature looks like:**

```javascript
FeatureScript 3112;                                   // language/library version, pinned
import(path : "onshape/std/common.fs", version : "3112.0");

annotation { "Feature Type Name" : "GN Holder" }
export const gnHolder = defineFeature(function(context is Context, id is Id, definition is map)
    precondition {                                    // = the dialog the user sees
        annotation { "Name" : "GN length (nominal)" }
        isLength(definition.gnL, { (millimeter) : [100, 530, 1000] } as LengthBoundSpec);
        annotation { "Name" : "Layout" }
        definition.layout is GNLayout;                // an enum becomes a dropdown
    }
    {
        buildGnHolder(context, id, definition);       // = what happens on every rebuild
    }, { "gnL" : 530 * millimeter, "layout" : GNLayout.THIRDS });  // defaults
```

**The building blocks:**
- **`op…`** operations change geometry: `opBoolean`, `opExtrude`, `opFillet`, `opSplitPart`…
- **`f…`** are simple primitives: `fCuboid`, `fCylinder`.
- **`q…`** queries *describe* entities, and are evaluated **lazily**: `qCreatedBy(id, EntityType.BODY)`,
  `qContainsPoint`, `qSubtraction`. Use `evaluateQuery` to pin one down right away (bug avoided in challenge 01).
- **`ev…`** measures: `evVolume`, `evBox3d`, `evDistance`. The GN feature uses these to check its own parts and
  `println` a report.
- **Units are types.** `530 * millimeter` is a length, and adding a length to a number is an error. That
  catches the classic "mm or inch?" mistake. OpenSCAD only has plain numbers.
- **Ids** are hierarchical (`id + "part0" + "frame" + "outer"`). Every body knows which feature and sub-step
  made it, and that is what queries use.

**Compared with OpenSCAD.** It feels similar: code, variables, loops, and a "compile" that builds geometry.
The differences that matter:

1. **B-rep, not mesh.** Exact cylinders and planes, real fillets/chamfers on any edge, STEP export.
2. **It lives inside an interactive CAD.** The feature can work on geometry someone drew by hand
   (query "the edges of this face" and fillet them), and people can add normal features after it. OpenSCAD
   is all or nothing: the file *is* the model.
3. **The parameters become a real dialog** with units, bounds and dropdowns, stored per insert. One feature,
   many configurations in different Part Studios.
4. **Cloud only.** No local compiler. Testing means a round trip to Onshape, and through the MCP every round
   trip costs API calls (36 for the whole GN build).
5. **Stricter language.** Typed parameters (`is Context`, `is map`), `const` vs `var`, every operation needs
   its own id, and queries are lazy. More ceremony than OpenSCAD, but you get fewer silent mistakes.

## How SolidCraft did it: commands, not a script

The SolidCraft agent never wrote a source file. It talked to the SolidCraft app over its MCP server:

```text
batch([
  ... define parameters such as open_l = "gn_l + 2*play" ...
  {"cmd": "solid.box", "name": "FrameBlock", "length": "out_l", ...},
  {"cmd": "solid.box", "name": "RimPocket", "operation": "cut", ...},
  {"cmd": "measure", "expect": {"volume": 594384}}      // checked in the same call
])
```

(Shape of the calls, simplified: not a verbatim transcript. `solid.box`, `measure`, `batch` with `expect`
are the real command names from [solidcraft/NOTES.md](../challenges/01-gn-holder/solidcraft/NOTES.md); the stored result
below is real, read from the saved file.)

Each command adds a **feature to a timeline**, just like clicking Extrude in Onshape. `save` writes the
design as `gn_holder.sc`, a zip archive:

| File in the zip | Content |
|---|---|
| `document.json` (20 KB) | **the model**: 38 parameters with expressions, 58 features (16 box, 16 pattern, 13 cylinder, 5 move, 4 mirror, 4 split), 18 named bodies |
| `cache/model.json`, `cache/bodies.bin` (5.5 MB) | the computed B-rep, so opening the file doesn't need a rebuild |
| `cache/thumbnail.png` | preview |

So SolidCraft is closest to **a normal CAD driven by an agent instead of a mouse**. The "program" only
existed as the conversation. The result is a parametric feature tree: change `gn_l` and the 58 features
rebuild. But there's no code to read, diff or reuse in a different design, and the expression language has
no `if` or loops. That's why the divider layout became 0/1 flags and a cutter moved out of the way.

## Which one when (for this project)

- **OpenSCAD**: quick, free, fully local, great in git. Use it when a mesh/STL is all you need and nobody
  needs to edit the part in a CAD.
- **FeatureScript**: the parametric logic is real code (loops, `if`, self-checks) *and* the result is a
  proper B-rep feature in a CAD that others use interactively. Best for reusable, configurable parts (a
  "GN holder generator"). Costs: cloud only, API budget, and the agent can't see the result.
- **SolidCraft**: best when the agent should *model like a human*, with picks, fillets and a visible
  timeline, and check its work step by step (`measure`, screenshots). Weakest for logic (no `if`) and
  for git.

All three gave the same frame to within a few mm³ (middle rail: 78 679 mm³ in both B-rep tools). The
geometry wasn't the hard part. The differences are in authoring, verification and reuse.
