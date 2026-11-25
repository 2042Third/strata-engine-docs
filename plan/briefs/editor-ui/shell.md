# Brief: `editor-ui/shell`

| Field | Value |
| --- | --- |
| Title | The editor shell: host, layer, docking and panels |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `editor-ui/widget-kit`, `editor/saving` |
| From | editor-ui ch. 8 and §1.2 (`EditorApplication`, `EditorHost`, `EditorShell`, `EditorLayer`'s frame, the panel registry, the default layout and its versions, menus and toolbar); the anatomy of editor-ui ch. 1 "A tour of the editor"; home of asking the person (modals, the re-ask rule, `DrawDiscardQuestion`) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/shell` — The editor shell: host, layer, docking and panels

**Covers.** The editor window for the people who change it. It opens with the anatomy of the whole editor, an
annotated picture of the default layout (the tour for game makers is `make/editor-tour`'s). The job and the map (the
architecture stack): `EditorApplication` installs the theme, the fonts and the layout file and gives `EditorLayer` an
`EditorHost`, its only way to the application; `EditorLayer` is the `EditorShell` that panels may ask (dialogs, the
unsaved-changes question, panels, facts about the editor); `EditorPanelRegistry` owns the panels. The problem and how
engines solve it is one paragraph that links `editor-ui/immediate-mode`, then panel architecture and dependency
inversion: a registry of descriptors with lifecycle hooks, and the UI as a client of commands. The contract: panels never
call `ImGui::Begin`; every change goes through a command with `CommandOrigin { CommandSource::UI }`; nothing changes the
scene while its rows are drawn (deferred actions); scripted runs never write the person's layout; a new default panel
bumps the layout version. The toy is a registry of panels in about 50 lines.

The real code in frame order: `EditorLayer::OnImGuiRender` (a diagram of one frame); the panel interface and descriptor
(a diagram of a panel's life); drawing the panels, with focus requests retried for up to 4 frames and deferred behind a
modal, and tabs shown without taking focus; the `[StrataPanels]` sections of `imgui.ini`; the default layout built from
proportions with font-size minimums, its version and `DockNewToolPanels` (a diagram); the dock space host and the status
bar window; the menu bar and the main toolbar; the window title, `--screenshot`, files dropped on the window, the
window's close, `editor.showPanel` and `editor.showDialog`. Then asking the person, the home of that concept: the
unsaved-changes question and its relatives, the re-ask when the undo version moved, and `DrawDiscardQuestion` drawn
inside other modals because ImGui keeps one popup per level (a diagram and a picture). The page states two entries of
"What Strata does not do": panels torn out into windows of their own, and editor extensions written by a game project.
At the end the reader can trace a click from a menu item to the command it runs.

**Leaves out.**

- The status bar's pills and the toasts → `editor-ui/status`
- The launcher panel and the dialogs → `editor-ui/launcher-dialogs`
- Shortcuts and their routing → `editor-ui/game-view`
- Saves off the main thread, the unsaved-changes guard and `AfterSaves` → `editor/saving`
- The tour of the editor for game makers → `make/editor-tour`
- Every panel, menu item and option in tables → `reference/editor`
- Writing a panel step by step → `editor-ui/tutorial-panel`
- The split of the editor's core from its UI → `editor/program`

**Fit.** `fits`: about 7,845 words against XL (8,000). Four concepts, five excerpts, seven figures and eight rules take
the most; the two absences and the three exercises (`new:35`) fit beside them.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:51-54` | feature | home | `EditorApplication`'s set-up (theme, fonts, CJK read, `--ui-scale`, `EditorLayout.ini` unless `--layout` or `--frames`), `EditorHost`, `EditorShell`, the options that matter to the UI |
| `editor-ui:109-115` | feature | home | `EditorLayer`, the UI's frame, the dock space host and the status bar window, the default layout and `c_LayoutVersion`, `DockNewToolPanels`, the menu bar, the main toolbar |
| `editor-ui:120-123` | feature | home | The unsaved-changes question and its relatives; the window's close and files dropped on it; `editor.showPanel` and `editor.showDialog`; the window title, `--screenshot`, command-script progress and the startup time |
| `editor-ui:129-136` | feature | home | The panel registry: the panel interface, the descriptor and its validation, the panel context, window names, open states in `imgui.ini`, `Focus` against `ShowTab` and `SelectTab`, `GetShownWindowRect`, the built-in panels in drawing order |
| `editor-ui:351` | concept | home | Docking and layout persistence: dock nodes, ini sections, a default layout from proportions, a version that replaces old layouts; a new panel shipped without a version bump |
| `editor-ui:356` | concept | home | Panel architecture and dependency inversion: lifecycle hooks, `EditorShell` and `EditorHost`, the UI in tests with fakes; a panel that calls `ImGui::Begin` |
| `editor-ui:361` | concept | home | The UI as a client of commands: undo, automation and the journal see one operation; deferred actions; a panel writing a component directly |
| `editor-ui:412` | concept | home | Modality and data safety in UI: ask before replacing a scene, ask again if it changed, draw nested questions inside the modal |
| `editor-ui:445` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.h:60-93`: the panel interface and its descriptor as a contract |
| `editor-ui:446` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.cpp:168-246`: drawing panels: focus deferred behind modals and retried, tabs selected without focus, `OnHidden` |
| `editor-ui:447` | code | home | `StrataEditor/src/UI/EditorPanelRegistry.cpp:330-424`: a settings handler that adds `[StrataPanels][Open]` and `[StrataPanels][Layout]` to `imgui.ini` |
| `editor-ui:448` | code | home | `StrataEditor/src/EditorLayer.cpp:726-795`: the editor's UI frame top to bottom, and where the toasts go |
| `editor-ui:449` | code | home | `StrataEditor/src/EditorLayer.cpp:1320-1360`: the default dock layout from proportions with font-size minimums |
| `editor-ui:476` | figure | home | The architecture stack from `EditorApplication` to the panels, the core underneath, the engine's ImGui module, and the Tooling boundary |
| `editor-ui:482` | figure | home | One editor frame from window events to the executed command list |
| `editor-ui:501` | figure | home | A panel's life: registered, open or closed, `OnUpdate`, `OnImGuiRender`, `OnHidden`, focus retried and deferred |
| `editor-ui:504` | figure | home | The default dock layout with its proportions and the layout-version rule |
| `editor-ui:531` | figure | home | The unsaved-changes question: saves in flight, modified, the modal, the re-ask, the action with `force: true` |
| `editor-ui:544` | figure | home | The whole editor in its default layout on a copy of a sample, 1600x900 at 100%, annotated with the panels' names |
| `editor-ui:581` | figure | home | The unsaved-changes question (Save, Don't Save, Cancel) |
| `editor-ui:594` | rule | home | Panels never call `ImGui::Begin`: the registry gives the View menu, open states, stable window names, focus and `OnHidden` |
| `editor-ui:602` | rule | home | Every change through a command (or `SceneEditTransaction` and `SetPropertyWithUndo`); panels never write, move or remove files |
| `editor-ui:605` | rule | home | UI commands carry `CommandOrigin { CommandSource::UI }` |
| `editor-ui:612` | rule | home | Do not change the scene while iterating its rows: schedule the change |
| `editor-ui:619` | rule | home | A modal that asks while open draws the question inside itself |
| `editor-ui:621` | rule | home | Focusing a panel while a modal waits is deferred |
| `editor-ui:651` | rule | home | Scripted runs never overwrite the person's layout |
| `editor-ui:653` | rule | home | Bump `c_LayoutVersion` when the default layout gains a panel open by default |
| `editor-ui:710` | term | home | DockBuilder |
| `editor-ui:712` | term | home | Settings handler |
| `editor-ui:744` | term | home | Panel, panel registry and descriptor |
| `editor-ui:746` | term | home | Editor shell (`EditorShell`) |
| `new:35` | hands-on | home | Exercises (D27): what a person sees on the next start after `c_LayoutVersion` goes from 5 to 6, the saved arrangement replaced by the default layout and the open states reset (Basic, predict); File ▸ Save Scene followed with breakpoints to `scene.save`, run by the command runner with the UI's origin, and its entry found in the Activity panel (Medium, trace); a question asked from inside an open modal, drawn first beside it and then inside it, to see why only the second shows (Hard, predict then run: a patch). Evidence: `StrataEditor/src/EditorLayer.h:132`; `StrataEditor/src/EditorLayer.cpp:1409-1423` (the saved version against `c_LayoutVersion`), `:1493-1495` (the menu item), `:1155-1171` (`scene.save` with `CommandSource::UI`) |
| `editor-ui:747` | term | link | Editor host (`EditorHost`), homed on `editor/program` beside `editor-core:650` (duplicates.md:45) |
| `new:6` | not-done | home | Panels torn out into windows of their own: the editor has one main viewport and no platform windows of ImGui's own; the Roadmap lists ImGui multi-viewports under Later. Evidence: `Strata/src/Strata/ImGui/ImGuiPlatform.h:18-21`; `Docs/Roadmap.md:1715` (under "Later", line 1637) |
| `new:7` | not-done | home | Editor extensions written by a game project: only the editor registers panels, in `EditorLayer::RegisterBuiltinPanels`. Evidence: `StrataEditor/src/EditorLayer.cpp:337-370` (the `Register` call at 350) |
| `editor-ui:49` | feature | use | The two libraries, as `editor/program` teaches them: this page draws what `StrataEditorUI` holds |
| `editor-ui:284` | concept | use | What an editor is, from `editor/program` |
| `editor-ui:116` | feature | link | The status bar's pills (`editor-ui/status`) |
| `editor-core:138` | feature | home | `EditorShell::RequestDiscardChanges`, `RequestReleaseProject` and `RequestQuit`: they ask the person and pass `force` only for what was asked |
| `editor-core:516` | figure | home | The unsaved-changes dialog after an edit and File ▸ Open Scene: one picture with `editor-ui:581` |
| `editor-core:567` | rule | home | The UI passes `force` only for what the person was asked about: the question comes again when the undo version moved |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an editor is; the core and UI libraries; `EditorContext`; the editor's frame order | `editor/program` | must |
| Commands are the API: the registry, running a command, command origins and kinds | `editor/commands` | must |
| Commands that take frames and the command runner | `editor/deferred-commands` | must |
| No silent data loss: the unsaved-changes guard, `force`, releasing a project, settings writers | `editor/saving` | must |
| Undo and redo: the undo stack and its version | `editor/undo` | must |
| Docking, `imgui.ini`, popups and modals | `editor-ui/imgui` | must |
| The kit's modals, toolbar buttons and dialog buttons | `editor-ui/widget-kit` | must |
| Interfaces and virtual functions | `basics/cpp-classes` | must |
| `std::function` and lambdas | `basics/cpp-generic` | must |
| The activity journal and command sources | `editor/journal` | helps |
| Command scripts (`--commands`) | `editor/command-scripts` | helps |
| Importing a file into the project | `assets/importing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dockbuilder` | DockBuilder | - |
| `editor-shell` | Editor shell | EditorShell |
| `panel` | Panel | panel registry |
| `settings-handler` | Settings handler | - |
