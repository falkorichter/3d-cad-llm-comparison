# Installing `cadcraft-cli` (macOS)

> ⚠️ **CADCraft is 2D only.** It's AutoCAD-style 2D drafting (DXF/DWG). Despite the similar name, it isn't
> a 3D CAD tool like SolidCraft: the project's own roadmap gives 3D modelling as 0% (checked v0.19.0,
> 2026-11-11). Use it for drawings, not for modelling 3D-printable parts.

The `cadcraft` MCP server in [`.mcp.json`](../.mcp.json) runs `~/.local/bin/cadcraft-cli`. Until that
file exists, Claude Code reports:

```
cadcraft (ENOENT): posix_spawn '/Users/<you>/.local/bin/cadcraft-cli'
```

## Where it is (and isn't)

| Place you might look | Has `cadcraft-cli`? |
|---|---|
| `/Applications/CADCraft.app/Contents/MacOS/` | **No.** It only has the GUI binary `CADCraft` (checked on v0.19.0). SolidCraft does bundle its CLI; CADCraft doesn't. |
| ArtCraft Launcher | **No.** It installs only the app. |
| `PATH` / `which cadcraft-cli` | Not until you install it as shown below. |
| [GitHub release](https://github.com/storytold/cadcraft/releases/tag/v0.19.0) → **Assets** | **Yes:** `cadcraft-cli-0.19.0-macos-universal.zip`. The release has about 40 assets, mostly Linux/FreeBSD packages, so expand the list and look for `cadcraft-cli-…-macos-universal.zip`. Don't use the `.dmg`, which is the GUI app. |

## Install with Ansible (recommended, replayable)

[`ansible/cadcraft-cli.yml`](../ansible/cadcraft-cli.yml) does the whole install and can be rerun
safely (a second run reports `changed=0`). Requires `ansible` (`brew install ansible`).

```sh
# download from GitHub (checksum-verified):
ansible-playbook -i ansible/inventory.ini ansible/cadcraft-cli.yml
# or use a zip you already downloaded:
ansible-playbook -i ansible/inventory.ini ansible/cadcraft-cli.yml \
  -e cadcraft_cli_zip=~/Downloads/cadcraft-cli-0.19.0-macos-universal.zip
```

What it does:

1. It checks the zip's SHA-256 against `cadcraft_cli_sha256`, the value from the release's
   `SHA256SUMS.txt`.
2. It unpacks the zip into `~/.local/share/cadcraft-cli/<version>/`, keeping the licenses next to the
   binary.
3. It checks `codesign --verify --strict` and Team ID `DJ6XS33FX8`.
4. It removes `com.apple.quarantine` from the binary if that flag is set (see the note below).
5. It symlinks `~/.local/bin/cadcraft-cli` to that version, which is the path `.mcp.json` runs.
6. It runs `cadcraft-cli --help` as a smoke test.

**Upgrade:** set `cadcraft_version` and `cadcraft_cli_sha256` in the playbook (or pass them with `-e`)
and rerun. Old versions stay in `~/.local/share/cadcraft-cli/` until you delete them.

## Install by hand

Use the same version as the app. Check it with
`defaults read /Applications/CADCraft.app/Contents/Info CFBundleShortVersionString`
(or in the launcher). The steps below are for **0.19.0**.

```sh
cd "$(mktemp -d)"
curl -LO https://github.com/storytold/cadcraft/releases/download/v0.19.0/cadcraft-cli-0.19.0-macos-universal.zip
curl -LO https://github.com/storytold/cadcraft/releases/download/v0.19.0/SHA256SUMS.txt
shasum -a 256 -c --ignore-missing SHA256SUMS.txt
# expect: cadcraft-cli-0.19.0-macos-universal.zip: OK
#   (6db9565a5fec6bacdfccbf62628a89e4430c9dbb5cc1eb85dbbef71e36e49da9)
unzip -q cadcraft-cli-0.19.0-macos-universal.zip
mkdir -p ~/.local/bin
cp cadcraft-cli-0.19.0-macos-universal/cadcraft-cli ~/.local/bin/
chmod +x ~/.local/bin/cadcraft-cli
```

The binary is code-signed (Team ID `DJ6XS33FX8`). You can check that with
`codesign -dv ~/.local/bin/cadcraft-cli 2>&1 | grep TeamIdentifier`.

**Quarantine:** `curl` doesn't add the macOS quarantine flag, but browsers do. On 2026-11-11 a zip
downloaded with Chrome had `com.apple.quarantine`, and the binary extracted from it by Ansible's
`unarchive` had it too. The playbook removes it with
`xattr -d com.apple.quarantine <binary>`, but only after the checksum and signature checks pass.

## Check it

```sh
~/.local/bin/cadcraft-cli --help
```

Then restart Claude Code in this folder (or run `/mcp` ▸ `cadcraft` ▸ reconnect). `/mcp` should show
`cadcraft` as connected. For a check without Claude Code, send `initialize` + `tools/list` over stdio:

```sh
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | (cat; sleep 3) | ~/.local/bin/cadcraft-cli mcp 2>/dev/null
```

With 0.19.0 the server reports `{"name":"cadcraft","title":"CADCraft","version":"0.19.0"}` and 12
tools: `command_line`, `script`, `execute`, `list_commands`, `inspect_drawing`, `query_entities`,
`render`, `find_text`, `new_drawing`, `open`, `save`, `cancel`.

## Upgrading (by hand)

To upgrade, change `0.19.0` / `v0.19.0` in the commands above to the new version and overwrite the
binary. The `-c` check takes the expected hash from that release's `SHA256SUMS.txt` for you. The path
in `.mcp.json` stays the same.

## Elsewhere

You can put the binary somewhere other than `~/.local/bin` if you prefer, but then change
`mcpServers.cadcraft.command` in `.mcp.json` to that **absolute** path. `${HOME}` didn't expand
there: Claude Code tried to spawn the literal `${HOME}/.local/bin/cadcraft-cli` (2026-11-11).

## Log

**2026-11-11:** installed 0.19.0 on macOS.

- The zip was downloaded in Chrome to `~/Downloads/cadcraft-cli-0.19.0-macos-universal.zip`. Its
  SHA-256 `6db9565a…9da9` matches the published hash.
- It was installed with `ansible/cadcraft-cli.yml -e cadcraft_cli_zip=…`. Result: `ok=11 changed=4`
  (unpack, quarantine removed, symlink, …). A second run gave `changed=0`.
- The signature check passed (Team ID `DJ6XS33FX8`). `--help` printed `cadcraft-cli: headless CADCraft`.
- The MCP `initialize` + `tools/list` check passed, with 12 tools (listed above).
- `/mcp` in Claude Code still needs checking. Restart Claude Code in the repo, or reconnect `cadcraft`.
