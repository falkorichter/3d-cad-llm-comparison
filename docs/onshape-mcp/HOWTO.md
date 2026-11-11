# How to get a FeatureScript part into Onshape

Two ways to do the same thing. Both end with a **custom feature** in a Feature Studio, which you then
add to a Part Studio. Example used here: challenge 01's
[`gn_holder.fs`](../../challenges/01-gn-holder/onshape/gn_holder.fs).

## Short answer: do you need the MCP?

**Not to use a finished `.fs` file.** It's plain FeatureScript source. Paste it into a Feature Studio and
it works. That needs no MCP and costs no API calls.

**The MCP is for writing the file.** It gives the agent a compile-and-run loop inside real Onshape,
without you in the middle:

| Without the MCP (copy-paste) | With the MCP |
|---|---|
| The agent writes `.fs` blind: it can't compile it | `test_feature` compiles **and runs** it in a Part Studio |
| You paste it, read the errors and paste them back, for every iteration | The agent sees errors and fixes them itself |
| The agent never sees the result | `println` output comes back, so the agent checked every part's bbox, volume and bed fit itself |
| You create the Feature Studio and paste | `create_feature_studio` + `put_featurescript` write it into your document |
| — | `search_featurescript_documentation`, and a shared notes doc of lessons learned |
| Free | Uses the Onshape API allocation (ours: 2,500 requests/year; the GN holder used 36) |

In challenge 01 the MCP was used for: the current FeatureScript version (3112), 3 test runs (one
failed with an opaque error, then a probe, then success with the size report), creating the Feature
Studio, and writing the code into it. With copy-paste the same build would have needed you for about 2–3
paste-and-report round trips. On a harder feature, with more errors, the difference grows.

What the MCP **can't** do (as of 2026-11-11), so these stay manual either way:
- add the feature to *your* Part Studio,
- render or screenshot the result (the agent only gets numbers),
- export STL/STEP (a browser MCP like Claude in Chrome can do it through the web UI instead).

## Route A: copy-paste (no MCP, no API calls)

1. Open the Onshape document (or create one).
2. Bottom left **+** ▸ **Create Feature Studio**. Give it a name, e.g. `GN Holder`.
3. Select all of the template code in the new tab (⌘A) and delete it.
4. Paste the whole content of the `.fs` file.
   - Keep the first two lines (`FeatureScript 3112;` and the `import … version : "3112.0"`). An older
     version number still works; Onshape keeps old library versions.
5. Press the blue **Commit** button (top bar). Errors show up in the code editor and in the
   FeatureScript console (**{✓}** icon, top right).
6. Switch to the **Part Studio** tab.
7. **Search tools…** (Alt/⌥ + C) ▸ type `GN Holder` ▸ click it.
8. Check the parameters in the dialog and press the green **✓**. Without ✓ the feature isn't kept.
9. Optional: **{✓}** console shows the feature's report (each part's bbox, volume and bed fit).

To change the design later, edit the code in the Feature Studio and *Commit*. Then every Part Studio
that uses the feature rebuilds. Copy the new code back into the repo so `gn_holder.fs` stays the
source of truth.

## Route B: with the MCP (what we did)

One-time setup: see [LOG.md](LOG.md) (`.mcp.json` entry, restart Claude Code, `/mcp` ▸ `onshape` ▸
*Authenticate*, two consent screens).

1. Give Claude Code the Onshape document URL:
   `https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>`. The tools need `did` and `wid`.
2. Claude: `read_featurescript_notes` → `test_featurescript` (trivial lambda → `libraryVersion`) →
   writes the `.fs` in the repo → `test_feature` until the console report is right →
   `create_feature_studio` + `put_featurescript` into your document.
3. You: steps 6–9 of Route A (Part Studio ▸ Search tools ▸ ✓). With `put_featurescript` no *Commit*
   click was needed.
4. Export: the Onshape MCP can't, but **Claude in Chrome** (another MCP) can click it in your browser:
   Part Studio tab ▸ right-click ▸ *Export…* ▸ STL or STEP, "Export unique parts as individual files".
   STEP arrives later, after an "Export completed" notification. That's how challenge 01 got its files
   ([details](../../challenges/01-gn-holder/onshape/NOTES.md#export-2026-11-11-driven-by-claude-in-chrome)).
   Then check the STLs against the feature's `println` report.
5. `get_api_usage` afterwards, and log the cost.

## Which one when

- **Reusing or sharing** a finished `.fs` (this repo, a teammate, a workshop): Route A. Free, and you
  only need the file.
- **Developing or changing** a feature with an agent: Route B. The agent can test and verify on its own.
  Batch the checks into one run (`println` report) to save API calls.
