# Brief: `editor-ui/game-view`

| Field | Value |
| --- | --- |
| Title | The Game view, shortcuts and who owns the keyboard |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/scene-view`, `editor/play-mode`, `input/mouse-cursor` |
| From | editor-ui ch. 12 "The Game view and who owns input" and ch. 13 "Shortcuts and focus" (resolution modes, letterboxing, `Input::SetViewport`, cursor lock, Shift+F1, Play and Stop tab switching; global and focused shortcuts and their guards) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/game-view` — The Game view, shortcuts and who owns the keyboard

**Covers.** Who owns the keyboard and the mouse: the game or the editor. The problem and how engines solve it: the
editor's camera against the game's; aspect ratios, letterboxing and fixed resolutions; mouse positions in the game's
pixels; a person who types in the Inspector while the game reads keys; a locked cursor that must never trap the person;
global against focus-scoped shortcuts. The map is two diagrams: who gets the keyboard and the mouse in play mode, and
how a key chord is routed. The contract: the game gets input only while the Game view is shown, focused and playing;
Shift+F1 always leaves; selection shortcuts are focus-routed, and global ones check for a modal and for the game.

The real code: the Game view's input ownership (the `Input` module enabled only then, `Input::SetViewport` with the
rendered resolution, a locked cursor setting `ImGuiConfigFlags_NoMouse`, Shift+F1 and the hint shown for a few
seconds); Play bringing the Game tab forward with the keyboard and Stop bringing the Scene view back; the global
shortcuts (`ImGuiInputFlags_RouteGlobal`, nothing behind a modal, Ctrl+P always, undo and redo through their commands,
the edit shortcuts only while the running game does not take them) and the focus-routed selection shortcuts of the
Hierarchy and the Scene view. Then the resolution menu (free, aspect ratios letterboxed, fixed sizes scaled to fit, the
game's own request) with targets freed while hidden and the "no camera" message as the game shows it; the panel keys;
Edit-menu actions sharing code with the shortcuts, the clipboard as JSON text; the Scene view's keys (Q, W, E, R, F,
Home, F8, F2); on macOS, Cmd in place of Ctrl, because ImGui swaps the two. One sentence links the game's UI scale in
play (the display's, without the person's factor: `editor-ui/ui-scale`). The page states the entry of "What Strata
does not do": the editor's shortcuts cannot be rebound. Pictures: a letterboxed 16:9, a fixed 1920x1080 scaled to
fit, the "no camera" notice, the locked-cursor hint. At the end the reader can add a key to the Scene view that
respects the guards.

**Leaves out.**

- Play and Simulate, the running copy and the game shell → `editor/play-mode`
- Pausing and stepping a game → `editor/stepping`
- Cursor modes and the input module's state → `input/mouse-cursor`
- UI hit tests in the game's pixels → `ui/input`
- The full shortcut table, generated → `reference/editor`
- The Scene view's tools that the keys select → `editor-ui/scene-view`

**Fit.** `fits`: about 5,490 words against L (5,000). Two concepts, three excerpts, two diagrams and three exercises
take the most; the shortcut table is short here because `reference/editor` generates the full one.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:143` | feature | home | The Game view panel |
| `editor-ui:203` | feature | home | The Scene view's keys: Q, W, E, R, F, Home, F8, the selection shortcuts and F2 |
| `editor-ui:207-208` | feature | home | The Game view: the primary camera with its HUD, the resolution menu, letterboxing, targets freed while hidden, the "no camera" message; game input ownership |
| `editor-ui:238-241` | feature | home | Global shortcuts and their guards; focus-routed selection shortcuts; panel keys; Edit-menu actions sharing code with shortcuts, the clipboard as JSON |
| `editor-ui:399` | concept | home | The Scene view against the Game view, and who owns input; the game reading input while the person types |
| `editor-ui:403` | concept | home | Keyboard shortcuts and focus: global against focused, text fields keep their keys, modals block, play filters edits, layouts and Cmd; Delete in the Content Browser deleting entities |
| `editor-ui:450` | code | home | `StrataEditor/src/EditorLayer.cpp:951-985`: global shortcuts and their guards; with the focus-routed ones in `StrataEditor/src/UI/EditorActions.cpp:318-338` |
| `editor-ui:464` | code | home | `StrataEditor/src/Panels/GameViewPanel.cpp:241-281`: input ownership between the editor and the game, the cursor lock and `NoMouse` |
| `new:10` | code | home | `StrataEditor/src/EditorLayer.cpp:1243-1275`: Play brings the Game tab forward (taking the keyboard, so the game gets its input) and Stop brings the Scene view back |
| `editor-ui:522` | figure | home | Input ownership in play mode: Game view focused and playing, cursor locked, Shift+F1, chips that never take focus |
| `editor-ui:524` | figure | home | Shortcut routing: global (modal check, Ctrl+P, `AcceptsEditShortcuts`), focused (Hierarchy, Scene view), text fields |
| `editor-ui:570` | figure | home | The Game view in play: 16:9 letterboxed in a tall panel; 1920x1080 scaled to fit; the "no camera" notice; the locked-cursor hint |
| `editor-ui:614` | rule | home | Selection shortcuts are focus-routed; global shortcuts check modals and `AcceptsEditShortcuts` |
| `editor-ui:644` | rule | home | The game gets input only while the Game view is focused in play; Shift+F1 always leaves |
| `editor-ui:676` | hands-on | home | Add a Scene view key (G toggles the grid) that follows the routing guards of `ViewportPanel::HandleShortcuts` |
| `editor-ui:734` | term | home | Shortcut routing (`RouteGlobal`, `RouteFocused`) |
| `editor-ui:775` | term | home | Letterboxing |
| `editor-ui:883` | open | home | Settled at the pin: on macOS Cmd is the shortcut modifier, because ImGui swaps Cmd and Ctrl under `ConfigMacOSXBehaviors`, which it sets on Apple builds (`Strata/vendor/imgui/imgui.cpp:1731-1735`); the platform backend passes keys as they are, and `StrataTests/src/ImGui/ImGuiPlatformTests.cpp:147-170` pins it |
| `new:39` | not-done | home | Rebinding the editor's shortcuts: the chords are written in the code as literal keys of `ImGui::Shortcut`, and no preference holds them; the Roadmap leaves rebinding editor shortcuts for later. Evidence: `StrataEditor/src/EditorLayer.cpp:951-985`; `StrataEditor/src/UI/EditorActions.cpp:318-338` (the focus-routed ones); `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:985-993` ("rebinding editor shortcuts and theme variants", left for later) |
| `new:40` | hands-on | home | Trace it yourself (D27): a breakpoint in `GameViewPanel::UpdateGameInput` during play shows `Input` enabled only while the Game view is shown, focused and playing, `ImGuiConfigFlags_NoMouse` set when the game locks the cursor, and Shift+F1 taking the focus away. Evidence: `StrataEditor/src/Panels/GameViewPanel.cpp:241-281` |
| `editor-ui:777` | term | use | Cursor lock, as `input/mouse-cursor` defines it |
| `editor-ui:616` | rule | link | Chips never take focus (`editor-ui/widget-kit`) |
| `new:28` | feature | link | The game's UI scale in play, without the person's factor (`editor-ui/ui-scale`), in one sentence |
| `audio-input:177` | feature | home | The Game view's focus: only the focused Game view in play feeds `Input`; `SetViewport`; the locked cursor; Shift+F1: taught with `editor-ui:208` |
| `audio-input:479` | figure | home | The Game view with a locked cursor and its Shift+F1 and Ctrl+P hint: one picture with `editor-ui:570` |
| `editor-core:228-229` | feature | home | `SetGameInputActive`, with edit shortcuts off meanwhile; `GameViewMode` and `ComputeGameViewFrame` |
| `editor-core:613` | hands-on | home | Set 4:3 and a fixed 1280x720, and check that a HUD button is hit where it is drawn |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Play and Simulate: the running copy, the game shell, edits while playing | `editor/play-mode` | must |
| Input ownership in the engine: the enabled flag, typed text, keyboard and pointer capture | `input/devices-state` | must |
| The mouse, the cursor modes and the game view's viewport | `input/mouse-cursor` | must |
| The Scene view's panel and its tools | `editor-ui/scene-view` | must |
| ImGui's focus and key chords | `editor-ui/imgui` | must |
| Running commands (`edit.undo`) and the clipboard of `entity.copy` | `editor/commands` | must |
| Pausing and stepping a game | `editor/stepping` | helps |
| UI input in the game's pixels | `ui/input` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `letterboxing` | Letterboxing | - |
| `shortcut-routing` | Shortcut routing | - |
