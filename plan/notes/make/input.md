# Notes: make/input

## New terms

None proposed.

## Since

`since: 0.3.0`: device input (keys, mouse, gamepads, cursor modes) is listed at 0.3.0 in the inventory (`gamedev:143`); input actions came with 0.6.0 (`gamedev:144`); the page teaches both, so it takes the older.

## Requests

- Name `Xbox` (the gamepad layout) is written as code in one sentence because it is on no word list: add it to `tools/data/extra-words.txt` or `names.txt`, then the code span can go.
- Words not on the lists: `rebind` and `rebinding` were avoided on the page (the glossary's alias words, if any, stay in the link text); no other request.
- Editor figure `input-actions-page`: no command selects a Project Settings page (see `## Figures`); the recipe uses `layouts/first-game.ini` and keeps its `waitsFor` (a command that selects a Project Settings page, for example `editor.showPanel` with a `page`) as the request for a later edition. Its stand-in is the drawing `input-actions-drawing`.
- Tutorial: stage 6 has no commands (the Vehicle map and the camera script stay out of the end state); stage 5 only adds the `Look` action. Stage 1 expects an entity named `Ball` from the starting tutorial (`make/scripting-scene`).
- Tutorial files hold `BallControl-1.cpp` to `-4.cpp` (stage files), `-toggle.cpp`, `-vehicle.cpp`, `LookCamera.cpp` (quoted only) and `exercise-2/BallControl.cpp`. None was compiled or run.
- `term-defined` for `ref` fails and cannot pass: the lint matches glossary names by words and breaks a name at code, so the term "`$ref`" never matches a bold definition. The page defines it in bold code in "What you need". Please change the entry's name or the lint.

## Not verified

- The scripts compile and run (not built; only read against `Input.h`, `Entity.h`, `Time.h`, `Log.h`).
- The sign conventions of `LookCamera` (yaw and pitch directions) were derived by hand, not played.
- A new project's `Input.Actions` holds no map but `UI` (the page says only that the page lists `UI`).
- `OnUpdate`'s `deltaTime` is the time-scaled one (from `Time::GetDeltaTime` and the exercise's claim; `ScriptSystem::OnUpdate` not read to the end).
- The two Further reading pages (Godot "Input examples", Unity Input System "Actions") were not fetched.
- The Content Browser shows `Scripts/BallControl.cpp` after **Scripts ▸ New Script...** (file name taken from the class name, not read).

## Findings not applied

- `critic-make-a-19` (the Main Camera framing): it names `make/scenes-entities` and `make/project-coin-run`, not this page.
- `critic-make-a-16` and `critic-make-a-18` are applied (the labels **File ▸ Project Settings...** and **Input Actions** under **Input**; -Z forward with `-move.y`).

## Clerk

- Admitted to names.txt: Xbox (the code span may go).
- Left for the planner: the lint's `term-defined` on `$ref` (a tool change), the layout file and the tutorial's stages.
- The build's checkpoint rule: "Why games name actions" moved before "## What you need"; "What Strata does not do here" and "Reading devices or reading actions" became ### sections of the last step section, before its checkpoint.

## Tutorial run

Run 2026-11-18 against the pin's Release build (two rounds; both passed, the chain through make/scripting-scene too).

- Round 1 passed as written, but the file was thinner than the page: it copied the stage file in place of
  `script.create`, made Move in one `setAction`, and neither played nor checked a "You should see".
- Round 2: the file follows the page's tabs (stage 1 `script.create`, then the file on `script.build`; stage 3 the map,
  the kind, one binding, three bindings) and plays where the page plays. Checks: Speed 4 (and kept after the reload),
  W for 60 steps from (0, 0.5, 6) ends at z 1.999; the stick (0.3, 0.6) ends at (1.088, 3.812), the page's 0.61 ×
  4 m; the action (0, 1) at z 2.000; both Space lines logged; dead zone 0.15, chips 1 and 3, the Button kinds.
- Page: the play tabs of stages 1 to 3 gained `play.stop` (and the In-the-editor tabs "Press **Stop**"); stage 1's
  tab taps Space, which its "You should see" asks for; stage 2's stick tab starts with `play.start`.
- Exercise 2 checks the Pause action's kind and its two bindings; the solution's "the ball stops" is not played
  (not tried: whether `input.*` holds, counted in fixed steps, end while the time scale is 0 was not read).
- 2026-11-24, track G walk segment 5 (WK8-WK10): stage 4 now plays Boost held with W (`input.key` `press` and
  `release` of LeftShift around a 60-step W tap: z from 6 to about -2) and checks `Jump pressed` and `BoostFactor` 2.
  The optional LookCamera and Vehicle sections are quoted whole; they stay out of the checkpoints, and both were run once from the input end state with the pin build (a scratch
  exercise file, removed): LookCamera turned the camera to yaw -60 after 30 steps of the right stick, and the vehicle
  version moved the ball 4 m before V and 8 m after it. Passed with the pin build and the 0.8.0 package.

## Engine

Nothing found: every command did what its description says.

## Figures

Photographed 2026-11-18 (two rounds, seven `scene` figures published; `dead-zones` is a diagram, `input-actions-page`
waits for tier 2: editor screenshot).

- The pictures stage the end positions; nothing is played. Positions follow the page's numbers (Speed 4 m/s, one
  second = the commands' 60 steps): W and D (2.83, -2.83); stick (0.3, 0.6) stretched to 0.61, (1.09, -2.18); the
  action at (0, 1), (0, -4); Boost (0, -8); the Vehicle with W and D (5.66, -5.66).
- Round 1 (recipes as written, fov 60): the ball was small; the moved pictures could not show "where it began"
  (only the first picture, far up the page, shows the start); `ball-action` stood left of the start, but the page's
  command holds (0, 1), straight ahead; `ball-boost` and `ball-vehicle` were the same picture; `ball-look` moved the
  ball instead of turning the camera. The template's ground renders flat grey and its sky pale grey-brown, not
  "dark stone" and "blue": alts rewritten.
- Round 2: one camera for all (0, 6, 7) to (0, 0, -2), fov 45; an orange disc marks the start in the moved pictures and
  a blue disc where a second of walking ends in `ball-boost` and `ball-vehicle` (the captions say the discs are added
  for the picture); `ball-vehicle` drives diagonally with W and D so it differs from `ball-boost`; `ball-look` keeps
  the ball at the start and turns the camera 15 degrees left. Materials carry the figure's id in their path because a
  page's figures share one project.
- Perspective shortens the far half of the distances in `ball-boost` and `ball-vehicle` (the blue disc is not midway on
  the screen); the captions speak of ground covered, not screen distance.
- `input-actions-page` (editor, 2026-11-18, one round with the provisional build 5b975ad2): cannot. The recipe named
  `layouts/input.ini`, which did not exist; it now uses `layouts/first-game.ini` with `panel: ProjectSettings`, so the
  panel is pictured at its own pixels (about 800 px wide, readable). The take shows the panel on its first page,
  **Game**, with **Input Actions** only as an entry of the list under **Input**: the recipe's `inputActions.setMap`
  and `setAction` steps ran, but no command selects a page (`editor.showPanel` has no page parameter; the panel's
  `Select` is called only by Inspector, Scene view and Export dialog buttons, never by a command), and the layout file
  keeps no selected page. Recipe left otherwise as written; `shows` no longer asks for "marked" buttons, which a
  screenshot cannot mark. The page gets nothing until a command (for example `editor.showPanel` with a `page`) selects
  `Input Actions`; then the same steps plus that page give the picture the caption describes. Nearest honest picture
  meanwhile: none (the Game page would teach nothing here, and the steps' JSON already names the map, action, kind and
  bindings).
- Retaken 2026-11-23 at the pin v0.8.0 (319075e3, its Release build), one round. The seven `scene` figures came out
  bit for bit the published ones (`figures.py compare`: 0 of 7 differ); looked at again, each still shows its caption
  (ball and coins, orange start disc, blue walk disc from above, the turned camera with one coin cut by the right edge).
  `publish` left them unchanged, so their stamps keep the pin 822a7a46: the tool records no new pin for an identical
  original.
- `input-actions-page` at v0.8.0: still cannot. The pin has `editor.screenshot`, so `check` asked to drop
  `waitsFor: tier 2: editor screenshot`, but `editor.showPanel` still takes only `panel`, `scripts` and `search`,
  `editor.showDialog`'s `section` serves Preferences only, and `ProjectSettingsPanel::Select` is still called by no
  command; the panel opens on **Game**. `waitsFor` now names that: a command that selects a Project Settings page.
  Not taken (a take would show the Game page). Nearest honest picture meanwhile: none, as above.
- Finished 2026-11-24 at the final pin v0.8.0 (319075e3): the pin still has no command that selects a Project Settings
  page, so the picture cannot be taken. In its place the page shows the drawing `input-actions-drawing`, which stands
  in for it (`standIn` on the waiting entry): the Project Settings window on **Input Actions** at the end of the
  section "Make the Move action", drawn from `StrataEditor/src/UI/InputActionsPage.cpp` and `SettingsPages.cpp` (page
  list, heading, both descriptions cut, "2 maps · 7 actions", the maps UI and Gameplay, Map and Enabled at start, Move
  with Vector2, dead zone 0.15, three chips with device icons and remove buttons, the plus button, the capture button,
  Add Action). The lead-in gained one sentence, a paragraph of its own, that introduces the drawing.
- The old caption said the buttons beside the plus sign listen for the next key. At the pin the capture button after
  the plus sign is disabled for a Vector2 (`InputActionsPage.cpp:528-533`: its tooltip sends you to the plus sign,
  whose popup captures each part of a 2D composite). The drawing shows it dimmed, and both captions now say so.
