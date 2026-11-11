# Onshape Labs FeatureScript MCP: progress log

App Store listing: https://cad.onshape.com/appstore/apps/Onshape%20Labs/6a29aea7c03f8bf659841734

The goal is to see whether an LLM can drive Onshape through FeatureScript well enough to compete with
the OpenSCAD workflow we already use (see [open-mog](https://github.com/falkorichter/open-mog) and
[linear-actuator-crane](https://github.com/falkorichter/linear-actuator-crane)).

## 2026-11-11: subscribed

- Subscribed to **Onshape Labs FeatureScript MCP** on the "API limits apply" plan.
- According to the confirmation dialog, the app shows up in three places:
  - the document's **+** menu, as a new tab
  - the context menu of a part, assembly, feature, mate or tab (*Applications ▸ …*)
  - the right-side panel on the documents page and inside a document

![Subscription confirmation dialog](assets/2026-11-11-subscribed-dialog.png)

The App Store page has a demo GIF (the Arbor Press sample: right-click a part ▸ Applications ▸ …).
The listing page is rendered client-side, so I couldn't find the GIF's URL to download it. This is a
frame from it:

![Frame of the App Store demo GIF](assets/2026-11-11-appstore-demo-frame.png)

> TODO: save the animated GIF from the App Store page (right-click ▸ Save image) as
> `assets/2026-11-11-appstore-demo.gif` and replace the frame above.

### Connection details (from the Onshape blog, 2026-11-11)
Source: https://www.onshape.com/en/blog/featurescript-mcp-server-enables-text-code-cad

- Requirements: an Onshape account (signed in) and a subscription to the App Store app ✅ (done).
- **MCP URL: `https://fs-mcp.labs.onshape.app/mcp`**, transport **HTTP**. Works with any MCP client
  (Claude, ChatGPT and Gemini are named).
- What it does: the AI writes **FeatureScript** and inserts it into an Onshape document, then runs it,
  checks the result and fixes errors. The output is a **reusable custom feature** (shows up in the
  toolbar and can be shared), not a one-off model. Once the feature exists, running it costs no AI tokens.
- The blog's example is a parametric roller-chain sprocket. A related blog post covers data safety and
  permissions ("Is CAD Data Safe When AI Connects to Onshape?").
- Added to `.mcp.json` as `onshape` (see 2026-11-11: remote MCP endpoint, below). The command equivalent is
  `claude mcp add --transport http --scope project onshape https://fs-mcp.labs.onshape.app/mcp`.

### Open questions
- [x] How does an external MCP client connect? → remote HTTP MCP, URL above.
- [x] How does auth work in Claude Code? Standard MCP OAuth (see 2026-11-11: remote MCP endpoint).
      Login itself not done yet.
- [ ] What do "API limits apply" mean in numbers (calls per month on our plan)?
- [ ] Which tools does it expose? Can it write FeatureScript only, or also read the part studio and
      export STL/STEP?
- [ ] First test: rebuild a simple open-mog or linear-actuator-crane part and compare it with the
      OpenSCAD result (and with the same part built in SolidCraft).

## 2026-11-11: remote MCP endpoint

- URL: `https://fs-mcp.labs.onshape.app/mcp`, transport **HTTP**.
- Unauthenticated `initialize` → `401`, with
  `WWW-Authenticate: Bearer error="invalid_token" … resource_metadata="https://fs-mcp.labs.onshape.app/.well-known/oauth-protected-resource/mcp"`.
  The server is uvicorn, so probably a Python MCP server.
- The protected-resource metadata gives the authorization server `https://mcp-auth.labs.onshape.app`,
  bearer tokens in the header, and the scopes `OAuth2Read`, `OAuth2Write`, `OAuth2Delete` and
  `OAuth2ReadPII`. That's the standard MCP OAuth flow, so Claude Code should handle the login itself.
- Added to `.mcp.json` as `"onshape": {"type": "http", "url": "https://fs-mcp.labs.onshape.app/mcp"}`.
- Gotcha: it didn't show up in `/mcp` at first, because Claude Code reads `.mcp.json` from the
  folder it starts in, and only at startup. The entry was on a branch, not in the checkout in use.
- [ ] Next: restart Claude Code, `/mcp` ▸ `onshape` ▸ *Authenticate*, then record the tool list here.

## Next entries

Add dated sections below (`## YYYY-MM-DD: …`), with screenshots in `assets/`.
