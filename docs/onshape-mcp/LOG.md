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

### Open questions
- [ ] How does an external MCP client (Claude Code) connect? Is there a remote MCP URL with OAuth,
      or does it only work inside the Onshape tab?
- [ ] What do "API limits apply" mean in numbers (calls per month on our plan)?
- [ ] Which tools does it expose? Can it write FeatureScript only, or also read the part studio and
      export STL/STEP?
- [ ] First test: rebuild a simple open-mog or linear-actuator-crane part and compare it with the
      OpenSCAD result (and with the same part built in SolidCraft).

## Next entries

Add dated sections below (`## YYYY-MM-DD: …`), with screenshots in `assets/`.
