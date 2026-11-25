# Notes: `input/actions`

## New terms

None proposed. The page defines the six terms the glossary homes here (input action, action map, qualified name,
bare name, composite, UI map). "Key repeat" is plain text, not bold.

## Requests

- `tools/data/extra-words.txt`: "modifier" and "modifiers" (the input systems of other engines call a held extra key
  so; the page says Strata has none). The three word-list findings for them are left until then.
- Figure `input-actions-page` (kind editor, project ThirdPerson): needs the layout `layouts/input-actions-page.ini`
  with the Project Settings window on its Input Actions page; the recipe only opens the panel, the step that selects
  the page is the planner's.

## Since

`since: 0.6.0`: `Docs/Releases/0.6.0.md` lists "Input actions with rebinding" (lines 94 to 100 at the pin).

## Not verified

- The claims about Unity's Input System (processors, interactions, composites with a modifier) and Unreal's Enhanced
  Input (modifiers, triggers, mouse and wheel as sources) come from general knowledge; the Further reading entries have
  no links.
- The page's Application claim ("Input stage") is from the header comment of `InputActions.h` and `Application.cpp`
  line 296 to 304, not from a run.
- The 60 updates per second remark (a repeat about every sixth update) is arithmetic, not a measurement.

## Findings not applied

- Exercise "run `Perf.Input.Actions256` in Release and explain the flat arrays and `GetStateVersion`" (audio-input:597):
  the card allows four exercises; the perf test is taught in the text, the exercise is not given.
- Exercise "mouse-wheel half-axis control end to end" (audio-input:591): given as a design answer inside the
  hard exercise 3, not as an extend patch.
- The timeline of gameui:471 is a table in an example, not a figure.
- The capture functions are named only; their behavior belongs to `input/rebinding`.

## Clerk

- Admitted to extra-words.txt: modifier, modifiers.

## Figures

- `input-actions-page` (editor, 2026-11-18): cannot; not taken. The panel `ProjectSettings` opens on its first page,
  **Game**, and no command selects another page: `editor.showPanel` takes only `scripts` (Content Browser) and
  `search` (Hierarchy); `SettingsBrowser::Select` is reached only through `EditorShell::ShowProjectSettings`, called
  by buttons of the Inspector, the Scene view and the Export dialog; the panel keeps no page in the layout or the
  project. The same provisional build (5b975ad2) pictured the Game page for `make/input`'s Input Actions figure the
  same day, so a take here would show the Game page of the Third-Person project. The recipe named
  `layouts/input-actions-page.ini`, which does not exist; it now uses `layouts/first-game.ini` with
  `panel: ProjectSettings` (the panel at its own pixels, about 800 x 500, as `make/input` and
  `editor-ui/settings-windows` do), keeps its step and gains `waitsFor: tier 2: editor screenshot`.
- What the page needs: a command that selects a Project Settings page (for example `editor.showPanel` with
  `page: "Input.Actions"`); the recipe then adds that parameter. Whether the UI map's six and the Gameplay map's eight
  rows fit 500 px, and whether `UI` stands first, is unverified: a taller layout (1280 x 800) may be needed then, and
  the caption's "stands first" must be checked against the picture. Until then the page gets no picture; the table
  under the figure already gives the Gameplay map's actions, kinds and bindings. Nearest honest picture meanwhile: none
  (the Game page would teach nothing here).
- `input-actions-page` at the pin v0.8.0 (319075e3, 2026-11-24): blocked; not taken. `check` with the dumps of
  319075e3 asks to drop `tier 2: editor screenshot` (the pin has `editor.screenshot`), but its `editor.showPanel`
  still takes only `panel`, `scripts` and `search`, and no other command (`editor.showDialog`, `project.settings`,
  `inputActions.*`) selects a Project Settings page; `SettingsBrowser::Select` is still reached only from the editor's
  buttons. A take would picture the Game page. The `waitsFor` now reads as `make/input`'s Input Actions figure,
  `physics/tuning` and `editor-ui/settings-windows` do: `tier 3: the Input Actions page of Project Settings; no
  command selects a Project Settings page`. What the page needs and the nearest honest picture are as above.
- `input-actions-page`, finished at the final pin v0.8.0 (319075e3, 2026-11-24): still blocked, so a drawing stands
  in. `editor.showPanel` takes only `panel`, `scripts` and `search` (`StrataEditor/src/EditorLayer.cpp:276-290`), so
  a take would show the Game page. The entry keeps its `waitsFor` as the request for a later edition and names
  `standIn: input-actions-gameplay`. Its caption, alt and shows now follow the pin's code: the page lists the maps
  (the UI map first, as the sample stores it) and draws only the selected map's actions (`DrawMaps` selects the first
  map that is not UI; `DrawActions` writes "Actions of <map>"), and a Button has no dead zone row; the old words had
  every map listed with its actions.
- `input-actions-gameplay` (diagram, new): the page for the Third-Person sample drawn from
  `StrataEditor/src/UI/InputActionsPage.cpp` and `Samples/ThirdPerson/ThirdPerson.stproj`: summary "2 maps · 14
  actions", the two maps with Gameplay selected, its table, Move and Jump in full (Vector2 with a dead zone, Button
  without), Look and the other five Buttons summed up in dashed lines, notes on the remove, add and capture buttons.
  Device icons and the opening text are left out. Rendered and looked at in both themes; `drawings check` passes. The
  sentence before the figure now introduces the drawing.
