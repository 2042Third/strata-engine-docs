# Brief: `editor-ui/ui-testing`

| Field | Value |
| --- | --- |
| Title | Testing a UI without a screen |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/shell`, `core/first-change` |
| From | editor-ui ch. 17 (`ImGuiHarness`, `FakeEditorHost`, probes, clicks over frames, source scans, panel perf tests) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/ui-testing` — Testing a UI without a screen

**Covers.** Testing a UI without a window or a GPU. The problem and how engines solve it: tests that click by
coordinates break when a layout moves; UI tests drive a real UI library with injected input over frames, find widgets
by key, and turn rules a compiler cannot check into scans of the source; panels with huge data get perf budgets. The map
is a diagram: `FakeEditorHost` and an ImGui context with the editor's fonts and theme → `EditorLayer` or one panel →
the input queue → `ItemProbe` lookups. The contract: one harness at a time; widgets found by probe keys; the scans keep
empty allowlists. The toy is a harness of about 40 lines that clicks one button.

The real code: `ClickItem` over three frames (hover first, because ImGui decides hovering from the previous frame, then
press and release, because buttons act on the release); the `Editor.UI.Source` scans (colors only from the theme, sizes
that scale with the font, panels drawn through the registry, no built-in font, UTF-8 encoded once, panels that change
files only through commands); a panel perf test measured per frame, the 95th percentile and the frames that refresh a
table. Then the fake host and the harness editor, the suites of the area and what each pins, and where the panels'
budgets live (five rows, one of them provisional). At the end the reader can write a test that clicks a kit widget,
and add a scan rule with its self-test.

**Leaves out.**

- The test program: shards, labels, locks and helpers → `engineering/test-program`
- Perf tests in general: noise, budgets, the reference machine → `engineering/perf-lab`
- GPU tests and end-to-end tests of the editor → `engineering/test-kinds`
- Writing a panel and its test step by step → `editor-ui/tutorial-panel`
- Every measured budget → `reference/performance`

**Fit.** `fits`: about 4,255 words against L (5,000). One concept, three excerpts, the scans' rules and two exercises
take the most; room is left for a worked test of a panel.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:256-260` | feature | home | `ImGuiHarness`; `FakeEditorHost` and `HarnessEditor`; the `Editor.UI.Source` scans; the suites of the area; the panels' perf tests and the 100,000-entity idle test |
| `editor-ui:415` | concept | home | Testing a UI without a screen: a real context, injected input over frames, probe keys, lints over the source, perf budgets for panels; tests that click by coordinates |
| `editor-ui:465` | code | home | `StrataTests/src/Editor/ImGuiHarness.cpp:118-132`: clicking a widget: hover, press, release over three frames |
| `editor-ui:466` | code | home | `StrataTests/src/Editor/EditorUISourceTests.cpp:499-545`: lint rules as tests: colors, sizes, panels, fonts |
| `new:24` | code | home | `StrataTests/src/Editor/EditorPanelPerfTests.cpp:94-138`: the Streaming panel with 10,000 assets measured per frame against confirmed budgets |
| `editor-ui:533` | figure | home | The test harness: the fake host, the ImGui context and `EditorLayer`, the input queue, the probe lookup, `ClickItem` over three frames |
| `editor-ui:679` | hands-on | home | Add a source-scan rule to `EditorUISourceTests.cpp` with its self-test |
| `editor-ui:743` | term | home | UI harness |
| `editor-ui:885` | open | home | Settled at the pin: the panels' budgets are the five `Perf.EditorPanels.*` rows of `StrataTests/Perf/Budgets.json` (101-105), and one of them, `Performance600FramesPausedP95`, is provisional, with a target and no measurement; the page names where they live, says that one is provisional, and links `reference/performance` for the values (critic-editor-ui-11) |
| `new:47` | hands-on | home | Trace it yourself (D27): a breakpoint in `ImGuiHarness::ClickItem` while an `Editor.UI` test clicks a toolbar button shows the probe lookup, then the three frames: the hover, the press, and the release on which the button acts. Evidence: `StrataTests/src/Editor/ImGuiHarness.cpp:118-132` |
| `editor-ui:100` | feature | use | The item probe that tests read |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| One test case with doctest, and running `StrataTests` | `core/first-change` | must |
| ImGui's frames; hovering decided from the previous frame | `editor-ui/imgui` | must |
| ImGui's input queue | `editor-ui/imgui-backends` | must |
| The item probe and the kit | `editor-ui/widget-kit` | must |
| `EditorHost`, `EditorLayer` and the panel registry | `editor-ui/shell` | must |
| Testing an engine: test kinds, determinism, regression tests | `engineering/testing` | helps |
| Benchmarks, noise and perf budgets | `engineering/perf-lab` | helps |
| Regular expressions and scanning source text | `basics/data-formats` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ui-harness` | UI harness | - |
