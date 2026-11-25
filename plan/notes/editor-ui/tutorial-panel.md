# editor-ui/tutorial-panel

## New terms

- panel registry: the object (`EditorPanelRegistry`) that creates the windows of the editor's panels, keeps their open states and builds the View menu entries. Defined in bold on this page; if `editor-ui/shell` homes it, the clerk should drop the bold here.

## Since

0.3.0: `EditorPanelRegistry` arrived in commit bc6a397c of 2026-10-09, which `git tag --contains` places in v0.3.0.

## Requests

- Words used that the lists lack: none left (pagecheck passes).
- Hosts: Further reading cites github.com (listed); Kent Beck's book is cited without a link.
- No figures file: both pictures are Mermaid diagrams. The brief's "result" figure of the new panel in the editor cannot be taken at the pin (the panel exists only in the patched build); the first diagram sketches it.
- Tutorial files: `tutorials/editor-ui/tutorial-panel.tutorial.json` (startsFrom the pin, patch tutorial, no stages), `tutorials/editor-ui/tutorial-panel.patch`, the quoted files under `tutorials/editor-ui/tutorial-panel/` (`SelectionSummaryPanel.h`, `SelectionSummaryPanel.cpp`, `SelectionSummaryUITests.cpp`, identical to the patch's new files) and `exercise-1.patch` to `exercise-3.patch` (diffs against the pin plus the main patch). All five patches were checked with `git apply --check` against the pin and the chain. The patch chain was never compiled or run: the first run is the integrator's (`tutorials.py patch`).
- No checkpoints: a patch tutorial has none (card), whatever the brief says; captions of build and test output are told in words, since the patched build's output may not be captured.

## Not verified

- That `entity.create` accepts `"PointLight": {}` and `"Tag": {"Tag": "Prop"}` exactly so, and that the feature project holds no entity named `SummaryLamp`, `SummaryTorch` or `SummaryCrate`.
- That `camera.focus` succeeds in the harness (the test needs only the journal entry, which is written either way).
- The menu entry name of the ThirdPerson sample in the Open Sample dialog (the page says "your copy" and uses File, Open Recent).
- That the build log names `SelectionSummaryPanel.cpp` on every generator.
- That `StrataCLI call editor.showPanel @show.json` finds a windowed editor started by hand (the sibling page relies on `--project` for a headless editor).
- That the window is a floating window with an empty body after the registration step, and that ImGui writes the layout file a few seconds after a change.
- The claim about the Scene view's **F** key: read at `ViewportPanel.cpp:850`, that it frames the selection; not run.

## Findings not applied

None: the brief listed no open findings.

## Clerk

- Refused panel registry: it is an alias of Panel, homed on editor-ui/shell (only its home words it).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run

`tutorials.py patch` at v0.8.0 (319075e3), 3 rounds (work folders `docs-work/patch-runs/editor-ui-tutorial-panel/r<n>`).

- Round 1: the page's patch failed on `C1083` for `WindEventScripts.cpp`, a file an earlier chain had added to the
  shared `build/docs-patch` (that build reconfigured); the exercises failed on `fmt/format.h`, which is not on the
  editor's include path. The panel now includes `<spdlog/fmt/fmt.h>` as the other editor files do (after `<nlohmann>`);
  the page's listing and a new line note say so.
- Round 2: `Editor.UI`'s "The default layout is viewport first" failed on `CHECK_FALSE(inspector->Hidden)`. Registered
  last, the new panel was the last window drawn on first run, took the focus, and ImGui showed its tab over the
  Inspector's. The registration moved right after the Asset panel's (before the Console, so the Content Browser stays
  last); the page's step 2 hunk, its prose and the docking step's "Why" say why the place matters.
- Round 3: the page's patch and exercises 1 to 3 pass (`Architecture.Layering`, `Editor.UI.SelectionSummary`,
  `Editor.UI`, `Editor.UI.Source`, the feature test). The exercise patches only changed their index lines.
