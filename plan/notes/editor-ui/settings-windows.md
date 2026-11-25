# Notes: editor-ui/settings-windows

## New terms

None proposed. The page defines settings browser and settings page (the glossary's `settings-section-editor-ui`) in bold.

## Requests

- Figures (kind editor, four entries in `src/content/figures/editor-ui/settings-windows.json`) need window layouts: `layouts/settings-graphics-quality.ini`, `layouts/settings-collision-layers.ini`, `layouts/settings-input-capture.ini`, `layouts/preferences-dialog.ini`.
- Each Project Settings figure needs its page selected (probe key `ProjectSettings.Page.<section id>`, for example `ProjectSettings.Page.Renderer.Quality`); `editor.showPanel` has no page parameter. The capture figure needs a capture listening (click of the probe key `ProjectSettings.Input.Actions.Action.<a>.CaptureBinding`). Not taken yet.
- Further reading cites Dear ImGui, Unity, Godot, Unreal Engine and JSON Schema documents without links; hosts may be requested if links are wanted.
- The toy sketch is about 120 lines (the brief says about 40); the sketch's rules (standalone, warning-free, four parts) kept it longer.

## Since

0.6.0: `Docs/Releases/0.6.0.md` line 84 introduces Project Settings and Preferences (the pages of this window).

## Not verified

- Other engines' rows of the alternatives table (Unity settings providers, Unreal developer settings, Godot project settings, JSON Schema form libraries, modal rebinding menus) rest on the cited public documentation, not on a check at the pin.
- The Preferences dialog's list order (External Editor, Interface, Frame Rate) is from the inventory; the order follows registration of the user sections.
- The figure recipe parameter `layerNames` of `project.setCollisionLayers` is from the command's schema; no editor was run.

## Findings not applied

- Brief: the hands-on exercise "register a section in a patch" (Medium, extend, `solution=` patch): not on the page. A patch exercise needs `tutorials/editor-ui/settings-windows/exercise-<n>.patch` and the tutorial tools; the page offers a toy-based sketch exercise, a trace exercise (breakpoint in `Apply`) and the refused-value prediction instead. The page's "Changing it safely" says how to register a section.
- Brief: the figure "Add binding popup building a 2D composite" (`audio-input:476-477`) is not requested; only the capture listening figure is.
- Brief: the page's toy is not "about 40 lines" (see Requests).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Editor figures, taken once with the provisional build (engine 5b975ad2831e, 2026-11-18, `--provisional`); nothing
published, `waitsFor: tier 2: editor screenshot` added to every recipe. The four layouts the writer named do not exist
and none was made: the Project Settings recipes now use `layouts/first-game.ini` with `panel: ProjectSettings` (the
panel at its own pixels, about 800 x 500), the Preferences recipes `layouts/dialogs.ini` at 960 x 540.

- preferences-interface: round 1 good. The dialog lists External Editor under Scripts, Interface and Frame Rate under
  Editor, with a search field; the Interface page shows the title, one line of description, Scale (a list, Automatic)
  and a dimmed Reset to Defaults (no stored value). Caption, alt and shows now name these.
- preferences-frame-rate: round 1 good for the dialog, but the recipe's caption was wrong: the page has four fields,
  not three, and the rates are lists of options, not fields with ranges. Idle after (seconds) 0.5 is a number field;
  Idle frame rate 30, Idle frame rate in the background 10 and Active frame rate Unlimited are lists
  (`StrataEditor/src/Editor/EditorFrameRate.cpp` makes them as enum fields). Caption, alt and shows rewritten.
- graphics-quality-page, collision-layers-matrix, capture-listening: cannot. Round 1 (this take) pictured the Game
  page for all three: the Project Settings panel opens on its first page, Game, the page is not kept in the layout,
  and no command selects another page (`editor.showPanel` takes `scripts` and `search` only; `editor.showDialog`
  selects a section only in Preferences). The capture figure also needs a capture listening, which only a click of
  the page's capture button starts; no command starts one. The recipes are left with their steps and `waitsFor`.
  What the page needs: a `page` parameter of `editor.showPanel` for Project Settings (for example `Renderer.Quality`,
  `Scene.CollisionLayers`, `Input.Actions`) and a command or test hook that starts a binding capture for an action.
  Until then the page gets no picture for these three; the nearest honest pictures would be the Game page (the list
  on the left shows Input Actions, Collision Layers and Graphics Quality as entries) or a diagram of the quality
  table, the layer triangle and the capture line.

At the pin v0.8.0 (319075e3, 2026-11-23, Release build, no `--provisional`):

- preferences-interface, preferences-frame-rate: taken once and published; `waitsFor` removed (check asked). Each
  picture shows what its caption, alt and shows say: the page list (External Editor under Scripts, Interface and Frame
  Rate under Editor), the title, the description (one line; two lines on Frame Rate), the fields at their defaults
  (Scale Automatic; 0.5, 30, 10, Unlimited) and a dimmed Reset to Defaults, with Close at the bottom right. Not
  published before, so nothing to compare.
- graphics-quality-page, collision-layers-matrix, capture-listening: still blocked at the pin. `editor.showPanel`
  still takes no page, and only UI buttons (Inspector, Viewport, Export dialog) call `ShowProjectSettings(page)`;
  `InputActionsPage::BeginCapture` runs only from a click. Their `waitsFor` now names the tier 3 reason (the pin has
  `editor.screenshot`, so the tier 2 line no longer applied); not taken. Nearest honest picture and what the page
  needs: as above.

Stand-ins at the final pin (319075e3, 2026-11-24): the pin and the picture tool still cannot make the three Project
Settings pictures (no command selects a page or starts a capture; `ShowProjectSettings(page)` runs only from UI
buttons, `InputActionsPage::BeginCapture` only from a click), so each keeps its `waitsFor` as the request for a later
edition and names a drawing as its `standIn`, drawn from the pin's code; the page places the drawings, each with a
sentence before it saying what it shows. The Game page the panel opens on was not used: it is not the page any of the
three paragraphs names.

- graphics-quality-table (for graphics-quality-page): the chips with High on, the table with five of its sixteen rows
  (values from the `c_*Row` lines of `RendererQuality.cpp`) and a line naming the eleven others, High's column
  highlighted, Custom's fields dimmed, the two memory lines with dashed values (not computed for the drawing), the
  players' choices, four numbered notes. Round 2: Custom's fields on the ground for contrast, marker 2 moved off the
  header.
- collision-layers-table (for collision-layers-matrix): an example project with Player, Enemy and Coin named and two
  cleared pairs (Enemy with Coin, Player with layer 5), so the matrix shows layers 0, 1, 2, 3 and 5 and the summary
  reads "3 named · 2 pairs pass through" (`CollisionLayersPage::Describe`).
- capture-listening-line (for capture-listening): the ThirdPerson sample's Jump action with its chips Key/Space and
  Gamepad/A, the capture line in the accent with an example of seconds left, Cancel, and notes on the timeout, the
  kept Cancel rectangle, the binding added and the held keyboard. While a capture listens the add and capture buttons
  are not drawn (`DrawBindings`); the drawing and its notes say so.
- The page's reading time rose to 85 (pagecheck's floor after the three lead-in sentences).
