# Installing `cadcraft-cli` (macOS)

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

## Install

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

`curl` doesn't add the macOS quarantine flag. A zip downloaded in a browser does, and Gatekeeper may
then block the first run. Downloading with `curl` as above avoids that.

## Check it

```sh
~/.local/bin/cadcraft-cli --help
```

Then restart Claude Code in this folder (or run `/mcp` ▸ `cadcraft` ▸ reconnect). `/mcp` should show
`cadcraft` as connected, with the tools `command_line`, `execute`, `inspect_drawing`, `query_entities`
and `render`.

## Upgrading

To upgrade, change `0.19.0` / `v0.19.0` in the commands above to the new version and overwrite the
binary. The `-c` check takes the expected hash from that release's `SHA256SUMS.txt` for you. The path
in `.mcp.json` stays the same.

## Elsewhere

You can put the binary somewhere other than `~/.local/bin` if you prefer, but then change
`mcpServers.cadcraft.command` in `.mcp.json` to that **absolute** path. `${HOME}` didn't expand
there: Claude Code tried to spawn the literal `${HOME}/.local/bin/cadcraft-cli` (2026-11-11).
