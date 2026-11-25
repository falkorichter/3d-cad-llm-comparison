# FreeCAD MCP: log

FreeCAD (installed at `/Applications/FreeCAD.app`) has **no MCP server of its own**. We use the community
project [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) (MIT), which is the most widely used of several
(others: [spkane/freecad-addon-robust-mcp-server](https://github.com/spkane/freecad-addon-robust-mcp-server),
[theosib/FreeCAD-MCP-Server](https://github.com/theosib/FreeCAD-MCP-Server),
[heok-yongssun/freecad-mcp](https://github.com/heok-yongssun/freecad-mcp)).

## How it works

Two parts that run in different Pythons:

```
Claude Code ──stdio MCP──> uvx freecad-mcp (Python ≥ 3.12)
                              │ XML-RPC, 127.0.0.1:9875
                              ▼
                           FreeCAD GUI + addon "FreeCADMCP" (FreeCAD's bundled Python)
```

- The **addon** lives in FreeCAD's user `Mod` folder and runs an XML-RPC server inside the FreeCAD
  window. **FreeCAD has to be open** for the MCP to work.
- The **MCP server** is a PyPI package started by Claude Code through `uvx`. Pin it to the same version
  as the addon: they compare a protocol version when they first connect.
- Unlike the SolidCraft CLI there's no headless mode for the main tools. `execute_code_headless` does
  run a script in a separate `freecadcmd` process.

## 2026-11-25: install

FreeCAD **1.1.4** (Revision 20260928). The addon is at commit `246f608` (2026-11-16), release **0.1.32**.

1. Installed `uv` / `uvx` with `brew install uv` (0.13.10). Nothing was installed into FreeCAD's own Python;
   the docs say explicitly not to do that.
2. Cloned the repo into a scratch folder and read the addon before copying it. By default the RPC
   server binds **`127.0.0.1` only**; remote access needs `remote_enabled` plus an IP list and an optional token.
3. Copied the addon:
   ```sh
   git clone --depth 1 https://github.com/neka-nat/freecad-mcp.git
   mkdir -p ~/Library/Application\ Support/FreeCAD/v1-1/Mod/
   cp -R freecad-mcp/addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/v1-1/Mod/
   ```
   FreeCAD 1.1 uses a **versioned** user folder (`v1-1/`). Before this there was no `Mod` folder at all.
4. Auto-start: wrote `~/Library/Application Support/FreeCAD/v1-1/freecad_mcp_settings.json` with
   `"auto_start_rpc": true` (localhost only). That's the same as ticking *MCP Addon ▸ FreeCAD MCP ▸
   Auto-Start Server*, but you don't have to click *Start RPC Server* every time.
5. Registered it in `.mcp.json`, pinned and with an absolute path (like `cadcraft`, because `${HOME}` didn't work there):
   ```json
   "freecad": { "command": "/opt/homebrew/bin/uvx", "args": ["freecad-mcp@0.1.32"] }
   ```

### Checks
- `open -a FreeCAD` → port 9875 open after a few seconds. XML-RPC `ping()` → `True`, and `get_rpc_status()`
  → `rpc_server: running`, `addon_version: 0.1.32`, `protocol_version: 3`, `execute_code_timeout: 90` s.
- Stdio smoke test (`initialize`, `tools/list`, `tools/call list_documents`) → **18 tools**, and
  `list_documents` → `[]`:
  `create_document, create_object, edit_object, delete_object, execute_code, execute_code_async,
  execute_code_headless, get_task_status, get_async_status, get_view, insert_part_from_library,
  get_objects, get_object, get_parts_list, reload_document, list_documents, get_rpc_status, run_fem_analysis`

### To use it
1. Start FreeCAD (the RPC server now starts by itself).
2. Restart Claude Code in this folder and approve the new `freecad` server. `/mcp` should show it as connected.

## Notes for teaching
- "FreeCAD has an MCP" really means "the community built one". Check which project, its version, and that
  the addon and server versions match.
- `execute_code` runs **arbitrary Python inside FreeCAD**. That's what makes it powerful (the whole
  Part/PartDesign API), and it's also why it should stay on localhost.
- `get_view` returns a screenshot, so the agent can *see* what it built, the way SolidCraft can and the
  Onshape MCP can't.

## 2026-11-25: first real use (challenge 01 v1)

After a Claude Code restart the 18 `mcp__freecad__*` tools were there, and FreeCAD's auto-start worked.

- Used **only `execute_code`** (8 calls). The object tools aren't worth it for a model with 131 features: one
  Python script per stage is cheaper and lands in the repo. The screenshot that comes back with each call is what
  makes the MCP useful.
- FreeCAD (a GUI app, started from Finder) could write into `~/Documents/...` without a macOS permission prompt.
- Pitfall: `clear` can't be a spreadsheet alias in an expression ("Unsupported operator"). The error then shows up
  as "shape is invalid" on the features, not on the sheet.
- Rendering: `ActiveView.saveImage(path, w, h, "White")` inside `execute_code` writes PNGs straight into the repo.
- Result and comparison: [challenges/01-gn-holder/freecad/NOTES.md](../../challenges/01-gn-holder/freecad/NOTES.md).
