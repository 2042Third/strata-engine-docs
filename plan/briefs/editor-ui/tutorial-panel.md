# Brief: `editor-ui/tutorial-panel`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding a panel |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/ui-testing` |
| From | new; from editor-ui ch. 7 and ch. 8: a panel registered through `EditorPanelRegistry`, drawn with the widget kit and tested without a screen |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/tutorial-panel` — Tutorial: adding a panel

**Covers.** The reader adds a panel to the editor in one engine patch: a "Selection Summary" panel that shows how many
entities are selected and which components they share, with a button that frames them in the Scene view. The sections,
each a stage of the patch: create the panel class and configure again so the new files build; register it with
`EditorPanelRegistry` in `RegisterBuiltinPanels`, find it in the View menu, open it with `editor.showPanel` and find its
open state in `imgui.ini`; draw it with the widget kit (no `ImGui::Begin`, colors from the theme, sizes from the font)
and make its button run a command with the UI's origin; dock it in the default layout and bump `c_LayoutVersion`, then
watch an old layout being replaced; test it with `HarnessEditor` and `ClickItem`, and run the `Editor.UI.Source` scans.
Each section ends with a checkpoint of the patch and its build or test output as a text capture. At the end the reader
has a panel that lands the way Strata's own panels do.

**Leaves out.**

- Adding a command for the panel to run → `editor/tutorial-command`
- Adding a component and its inspector rows → `world/tutorial-component`
- How the registry draws, focuses and persists panels → `editor-ui/shell`
- Landing a change: the review checklist and CI → `engineering/contributing`

**Fit.** `fits`: about 4,725 words against L (5,000). Five sections of two or three steps, each with a patch excerpt and
its output, take the most; the three exercises' worked solutions are patches.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:670` | hands-on | home | Add a docked panel through `RegisterBuiltinPanels`, open by default: the View menu, `editor.showPanel`, persistence; then bump `c_LayoutVersion` and dock it |
| `editor-ui:129-136` | feature | use | The panel interface, the descriptor, the context, window names, open states and `Focus` |
| `editor-ui:112` | feature | use | The default layout and `c_LayoutVersion` |
| `editor-ui:122` | feature | use | `editor.showPanel` |
| `editor-ui:594` | rule | use | Panels never call `ImGui::Begin` |
| `editor-ui:653` | rule | use | Bump `c_LayoutVersion` for a panel open by default |
| `editor-ui:600` | rule | use | Controls from the widget kit |
| `editor-ui:605` | rule | use | The button's command carries the UI's origin |
| `editor-ui:256-258` | feature | use | The harness, the harness editor and the source scans |
| `new:48` | hands-on | home | Exercises (D27), open extensions with hints and patches as worked solutions: the frame button disabled while nothing is selected, with a tooltip that says why (Basic); the selected entities' names listed below the summary, clipped with `ImGuiListClipper` (Medium); a second button that frames the whole scene through `camera.focus` without entities, and a harness test that clicks it (Hard). Evidence: `StrataEditor/src/Editor/EditorViewportCommands.cpp:1073-1076`; `StrataEditor/src/UI/DeleteAssetDialog.cpp:130` (a clipped list in a dialog) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source, configuring again after adding files, running `StrataTests` | `core/first-change` | must |
| The panel registry, the default layout and its version | `editor-ui/shell` | must |
| The widget kit and the item probe | `editor-ui/widget-kit` | must |
| The harness, `ClickItem` and the source scans | `editor-ui/ui-testing` | must |
| The selection in `EditorContext` | `editor/program` | helps |
| Running one command from a terminal (`StrataCLI call`) | `editor/commands` | helps |
| Patches and git | `basics/git` | helps |

**Starting state.** The engine's source at the pin, configured and built in Debug as `core/first-change` shows, with the
editor and `StrataTests` built and the tests passing. The tutorial's patch chain starts at the pin: it needs no patch
of the WindZone chain or of another tutorial, so no checkpoint precedes it. A copy of `Samples/ThirdPerson`, made with
File ▸ Open Sample in the built editor, gives entities to select.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
