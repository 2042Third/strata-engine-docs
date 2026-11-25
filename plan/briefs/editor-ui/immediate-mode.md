# Brief: `editor-ui/immediate-mode`

| Field | Value |
| --- | --- |
| Title | Why immediate mode |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `editor/program`, `ui/what-game-ui-does` |
| From | editor-ui ch. 2 (why the editor's UI is immediate: tools against the game, Tooling layers, why Dear ImGui); what an editor is: `editor/program`; the general comparison: `ui/what-game-ui-does` |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/immediate-mode` — Why immediate mode

**Covers.** The page starts from a problem the reader can picture: a panel with one slider for a light's intensity. In
a retained toolkit the program builds a slider object, connects a callback, and keeps the slider's value and the
light's value in step. A tool that changes every week breaks where the two copies disagree. The naive answer, the
retained game UI that `ui/what-game-ui-does` explained, needs the same synchronization. Then the idea: in an
immediate-mode UI the code describes the whole UI every frame, one call draws a widget and returns what the person did
with it, and the program's own variable is the state. The library keeps only a little state, keyed by IDs (a diagram
of the two data flows). The approaches table compares retained toolkits (Qt, WPF, the HTML DOM, Unreal's Slate,
Unity's UI Toolkit) with immediate-mode libraries (Dear ImGui, Unity's IMGUI) by code per change, state to keep in
step, layout power, accessibility and cost per frame, for tools only; the general comparison stays on
`ui/what-game-ui-does`.

Strata's choice follows: Dear ImGui for the editor and tools, retained components for games. The `ImGui` layer is a
Tooling layer, so a shipped game links no ImGui, and the editor's UI is a library apart from its core, so a button runs
a command. The page ends with what the choice cannot do (accessibility, rich layout, layout decided one frame late, a
cost that grows with what is submitted) and the common mistakes: thinking ImGui stores the value, waiting for a
callback, forgetting that one call both draws and reports. The running example is the light slider, sketched both ways
in about ten lines each. At the end the reader can say why the editor's UI is immediate and the game's retained, and
read an immediate-mode widget call.

**Leaves out.**

- ImGui's frames, windows, items and IDs → `editor-ui/imgui`
- What an editor is, and the split of the editor's core from its UI → `editor/program`
- The general comparison of retained and immediate UIs, and why the game UI is retained → `ui/what-game-ui-does`
- How panels, the host and the shell fit together → `editor-ui/shell`
- Panels torn out into windows of their own (Strata has one main viewport) → `editor-ui/shell`

**Fit.** `fits`: about 3,175 words against M (3,000). The three exercises (`new:25`) and the idea with the diagram of
the two data flows take the most; the table compares the approaches for tools only, because the general table is
`ui/what-game-ui-does`'.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:291` | concept | home | Retained against immediate mode for tools: code-first UI, no state to keep in step, layout every frame, the trade-offs, why Strata takes Dear ImGui, the three newcomers' mistakes |
| `editor-ui:480` | figure | home | The two data flows side by side: a widget tree with callbacks, and per-frame code with ImGui's state by ID producing draw data |
| `editor-ui:284` | concept | use | What an editor is and why it is not the game: one sentence and a link; the Tooling half (games link no ImGui) is taught here |
| `editor-ui:700-701` | term | use | Immediate-mode and retained-mode GUI, as `ui/what-game-ui-does` defines them |
| `editor-ui:702` | term | use | Dear ImGui named and placed; its home is `editor-ui/imgui` |
| `editor-ui:35` | feature | link | The ImGui module lives in the Tooling layer `ImGui` (`StrataTests/Architecture/Layers.json:105-111`) |
| `new:1` | feature | link | The version and build of Dear ImGui, taught on `editor-ui/imgui` |
| `new:6` | not-done | link | One main viewport: no panel in a window of its own, stated on `editor-ui/shell` |
| `new:25` | hands-on | home | Exercises (D27): what `UI::ToolbarButton` returns in a frame where the person only hovers it, and where a toggle chip's state lives (Basic, predict); the page's light slider written both ways as a C++ sketch on the workbench, a retained slider object with a callback and an immediate function that draws and returns the new value, both driven by the same three simulated frames of a drag and their output compared (Medium, done); which of three tools a team should build retained (a level editor, a settings screen for players, a debug overlay), and why (Hard, design). Evidence: `StrataEditor/src/UI/Widgets.h:45-55` (the kit's buttons return what the person did; `ToggleChip` writes the caller's `bool`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an editor is, and why it is not the game; the editor's core and UI libraries | `editor/program` | must |
| What a game UI must do; retained against immediate UIs | `ui/what-game-ui-does` | must |
| The layer table, Tooling layers and why games link no tooling | `core/layers-registries` | must |
| Commands are the API: a button runs a command | `editor/commands` | helps |
| A frame and the frame loop | `core/frame-loop` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
