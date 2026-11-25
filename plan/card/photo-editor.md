# Card: photographer of editor figures

Extends plan/card/photo.md for the kind `editor`.

## What the figure owes the reader

The panel or dialog the paragraph speaks of, readable in the 768 px column, in the state the step describes.

## Commands, in order

1. `$P -I tools/figures.py list | grep <part>/<chapter>`; offline `check` as photo.md says. A missing layout is only a
   `note:` (`does not exist yet`).
2. Missing layout: `... figures.py layout <name> --window-size <w>x<h> --engine <pin> --build <build> --work ../docs-work/photo-editor/layout-work --provisional`.
3. Take, PowerShell, under the lock:
   `... figures.py take --kinds editor --figures "<part>/<chapter>/*" --engine <pin> --build <build> --work <work> --provisional`.
   `<build>`: today `docs-work/photo/provisional-build/Release`; `...`: photo.md's PerfLock line.
4. Output: `<work>/shots/`; `scripts/` holds what ran. `--provisional` also takes figures waiting for `tier 2: editor screenshot`; publish refuses it.
   Keep `waitsFor`. When the pin has moved: drop `--provisional`; `check` then names the `waitsFor` lines to remove;
   publish as photo.md step 8.

## Window or panel

- `editorWindow.panel` (`Inspector`, `AssetInspector` (the Asset tab), `Hierarchy`...: `editor.showPanel`'s enum;
  `check` refuses others): the panel at its own pixels. Prefer it: a panel reads at 1:1.
- No command scrolls a panel: rows below need a taller window (1280 × 800), with its layout.
- Whole window (dialogs, a state across panels): `"windowSize": [960, 540]`; the default 1280 × 720
  reads badly at 60 %.

## Layouts

- `layouts/<name>.ini` serves one window size (its first line); `take` refuses another.
- Larger panel: edit `SizeRef` in `[Docking][Data]`. Nodes: `0x1` Hierarchy column, `0x4` Inspector column, `0x5`
  Scene/Game, `0x6` bottom tabs; `0x2` and `0x3` are their parents. Children plus 2 px make the parent.
- Another layout: copy one of the same size, or make one (its Inspector is 256 px: widen it to about 380).
- `[StrataPanels][Layout] Version` changes: the editor drops the file. Remake layouts then.

## Steps that work

- `entity.create` with `bind {"x": "/id"}`; `selection.set {entities: [{"$ref": "x"}]}`; `entityName` (first match).
- A nested entity selected opens its groups; `editor.wait {frames: 10}` then `selection.set {entities: []}`.
- `editor.showPanel {panel: "Hierarchy", search: "c:Light"}`; `{panel: "ContentBrowser", scripts: true}`.
- `editor.showDialog {dialog}`: `externalEditor`, `newScript`, `preferences`, `export`, `about`...
- `script.create {class, fields: {"Speed": "float"}}`, `script.build {wait: true}`, `script.add {entity, class, fields}`.
- `entity.setActive`, `component.set`, `scene.new`, `scene.saveAs`, `play` (the recipe field).
- Files imported from the release's `Samples/<S>`: `project: {sample: "<S>"}` holds them.
- A tutorial's own sources (build error, logs, crash): `files: [{"stage": n}]` (what stages 1 to n copy) or
  `{"from": "book:tutorials/…", "to": "Scripts/Coin.cpp"}`, copied before the window opens; `atStep: k` before
  window step k (a new window runs the rest, without play). A faulty variant is a file of its own beside the stage's.

## Automation

- `"automation": true`: the window serves automation; the pill reads "port <n> · no agent".
- `"automation": {"client": "claude-code"}`: an agent (StrataCLI mcp, named so) sends every step and stays connected:
  "Agent connected · claude-code", the agent's rows in Activity, the Scene view's chip and its 0.6 s outline of the last
  edit (the frames are waited for before your steps). Put the edit to outline last. No `atStep` with a client; the
  tooltip cannot be opened. The token stays in the take's session folder: never look for it.

## Judge

- The subject is the panel the caption names, readable, not cut. Enlarge text with sharp (photo.md).
- Each claim of caption, alt and shows is in the picture: colors, which row is dimmed, what is selected.

## Usual faults

- "Scripts built" toast over the view: picture a panel, or wait 600 frames after `script.build`.
- Hover highlight or tooltip: the pointer was over the window; retake.
- Labels ending in "...": widen the column in the layout.
- Empty half of a panel: smaller window height.
- Basic3d has `Spinner.cpp` beside your script: say "lists the files".

## What commands cannot show

- Open menus and popups (plus menu, Add Component, Overrides), drags, hover tooltips, text typed into a field, a
  native file dialog, motion: picture the state before or after, rewrite caption and alt to it, or propose a diagram.
- Content Browser folders and a model's sub-assets: only the top folder shows.
- The pill's tooltip (it needs the pointer).
- Say each, per figure, under `## Figures` in the page's notes; leave the recipe.

## Privacy

- `$env:LOCALAPPDATA/Strata/Preferences.json` must not exist: the window would show your preferences.
- No user name in a path (External Editor's list, the Console), no other project's name.

## Throughput

One editor per figure: 4 to 12 s; a sample copy adds 10 s, a script build 15 s.

## Never

Publish a provisional take; drive the window by hand; remove `waitsFor` before `check` asks.
