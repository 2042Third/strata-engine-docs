# Notes: make/menus

## New terms

None proposed. Defined on the page in bold: rebinding, toggle group, binding capture, event target (the four of the brief), and the plain words widget, focus, selectable, UI actions, time scale, vsync, input field, mask.

## Since

0.4.0: `Docs/Releases/0.4.0.md` names OnUIClick and UIButton (the game UI). Rebinding functions came later (not dated here).

## Requests

- Words on no list: HUD (acronym used 11 times after its expansion), rebinds, playtests (now removed), Ana (now code). Please add HUD to extra-words.txt.
- Figures: all eight are `scene` recipes on the basic3d template built from `ui.create`; none is a real capture of the finished screen. The main menu figure (`menu-works`) needs the live capture without a camera (`new:26`). Settings, rebinding and credits figures need a photographer to rebuild the recipe on the course; no whole-editor pictures are asked for the steps (not drawn).
- Tutorial stages carry the script files and the `ui.create` calls of the first menu; wiring of Event Target and script fields is not in the commands (the field value syntax for entities was not verified), so the integrator completes it.

## Not verified

- The course's cursor mode (the pause script saves and restores whatever mode the game has).
- Exact Hierarchy menu names for the layout preset (`Vertical Layout` is written as code).
- Commands `script.create`, `viewport.capture`, `prefab.create`, `input.key`, `input.type`, `component.set` parameters for UI properties.
- `Gamepad/Start` as a valid binding name; the 2D canvas mode's button name; that a mask or text child of the input field is made by the preset.
- Forms `Pause` action default with Escape also bound to UI Cancel.

## Findings not applied

- critic-make-b1-15: applied (registration shown, slider range 0 to 1, divide-by-10 shown as a mistake).
- critic-make-b1-17: applied (resolution buttons, no list of display modes); the evidence search was not re-run.
- critic-make-b1-18: applied (`UI::IsPointerOverUI`).
- Brief step 4 on simulated taps at time scale 0: stated in one sentence, no link to `editor/stepping`.
- Brief steps 8 and 9 merged into one section, steps 1 and 2 merged, so seven checkpoints.
- Whole-editor pictures per step are not asked for.

## Clerk

- Added the aliases rebind, rebinds to the term rebinding, homed here (the glossary's definition kept). HUD was already in extra-words.txt.
- Left for the planner: the eight figures, the wiring of Event Target in the tutorial.

## Figures

The photographer, 2026-11-18. All eight are published, `scene` figures on the basic3d template built with `ui.create`;
the recipes are written by a generator kept in the work folder (`docs-work/photo/make-menus-gen/gen.py`).

- Round 1 (the writer's recipes): every screen was a bare vertical layout without a background, drawn at two thirds
  scale (the canvas's 1920 x 1080 reference) in the middle third of the picture; all of them showed the same blue
  buttons and toggles, no state (no focus, every toggle off, the slider at 0, the field showing its placeholder
  `NameInput`, the label `NameLabel`), and `credits-sign` had neither a mask nor a sign.
- Round 2: each screen is a panel with a padded vertical layout on a canvas whose reference resolution is 1280 x 720
  (canvas units are the picture's pixels). `result` shows the main menu beside the settings screen. `menu-works`
  turns off Ground, Sky and Sun and gives the camera a black clear color. `focus-shown` and `paused` play the scene,
  and one tap of the Down arrow focuses the top-left selectable (the image is white, Normal Color blue, Focused Color
  orange). `settings-screen` sets the slider's Value to 0.5 and gives the three window toggles one Group, with only
  Borderless on. `rebind-capturing` writes the button labels the script would write. `name-shown` sets the field's
  Text and the label. `credits-sign` has a masked credits panel and a world-space sign. Seven passed.
- Round 3: `credits-sign`'s sign floated in the air; it now hangs on a wall (a scaled `Builtin/Cube`), turned 25
  degrees, with a shadow that shows it is in the world. `name-shown` now uses the name Ana, as the page's step does
  (`Player: Ana`), not Robo.

What the pictures cannot show as the page words it:

- `menu-works`: `viewport.capture` with camera "scene" fails without a camera, so the picture keeps the camera
  and turns off the world instead. It looks like a scene without a camera, but the caption does not claim the reason.
- `result` and `paused`: there is no course in the basic3d template; the screens draw over its ground and sky,
  and `paused` has no HUD under the pause canvas (Sort Order 10 is set but has nothing to cover).
- `focus-shown`: the page says to give Focused Color a visible tint. The default button image is blue, and a tint
  multiplies it, so an orange tint over blue would only darken it. The recipe draws the image white and puts the
  blue in Normal Color.
- `rebind-capturing` and `name-shown` show the state the scripts produce (labels and the field's Text set by the
  setup); no script runs and nothing is typed. A take with the tutorial's scripts would need `script.create` and a
  build in the recipe.

2026-11-23, at the pin v0.8.0 (319075e3): all eight taken again in one hold (`docs-work/photo/make-menus`) and
compared with the published originals (`figures.py compare`, output in `docs-work/photo/make-menus-compare`). Seven
originals are byte-identical to the published ones; `credits-sign` differs in one pixel by one level, and its stamp now
records the check at 319075e3. Looked at again: each picture still shows what its caption says (in `paused` the
banner's text shows faintly through the see-through panel). The recipes are unchanged. `publish` leaves the stamps of
byte-identical retakes as they were, so the seven still name the pin 822a7a46 with no `checkedAt`; the identical
originals are the evidence that they hold at 319075e3.

2026-11-23, a viewer's fault in `credits-sign`: the title Credits floated without a backing over the ground just above
the masked panel's cut top line, so it read as credits text escaping the mask. The title is now the child of its own
panel `CreditsHeader` (380 x 64, 24 units above the masked panel), retaken under the lock and published; alt and shows
name the title bar. The manifest now differs from the generator's output (`make-menus-gen/gen.py`) in this figure.

## Tutorial run

The runner, 2026-11-18, four rounds (`docs-work/tutorial-runs/make-menus-1` to `-4`). The file carried only the
`ui.create` calls of the first menu and the script builds; it now does every step the page tells, with checks of the
page's "You should see" values: the column's stacking (`ui.layout` rects), no camera in the menu scene, Play loading
the course and Quit ending play mode, the focus moving Play, Settings, Quit with Down and Enter quitting, the pause
panel hidden, shown with Resume focused and hidden again, the toggle group and the slider's click, the prefab
instance under `PausePanel` holding the script, the Jump row showing `Key/Space, Gamepad/A`, then "Press a
control...", then `Key/K`, `Player: Ana` after typing, the credits moving 45 units in 60 steps, the sign's World Space.
The exercise's worked solution now does what its answer says (`exercise-1-SettingsMenu.cpp`, field `OpenedFrom`).

What the chain lacked and the page now says: the course from Animation has no `Gameplay/Boost` and no HUD canvas
(the rebinding step adds the action, the name field step makes a canvas `HUD`).

What the runs found:

- Round 1: a quit stops play mode, so a `play.step` across it fails; the file now steps with `wait: false` and asks
  `play.state` until it answers `Edit` (and the page says a quit ends play mode in the editor).
- Rounds 2 and 3: the toggle preset of `ui.create` (and the Hierarchy's) starts with Is On true, and a group acts
  only when one switches on, so all three window toggles were on and the click on Fullscreen changed nothing. The
  page now has the reader turn Borderless and Fullscreen off; the file does and checks it.
- Round 4: the tutorial passed in the editor, and the exercise passed in full, but the reader's copy of stage 1
  failed in its second part: a fresh editor opens the start scene (the course), so the menu's entities were not
  found. Mended after the last round: `scene.save` before `script.create`, `scene.open` of the menu after the
  build. Not run yet (the round limit): the next run must confirm stage 1's reader copy and the stamps.
- 2026-11-23, at the pin v0.8.0 (319075e3), `docs-work/tutorial-runs/make-menus-5`: the chain from make/animation,
  the tutorial's seven stages with their reader copies (stage 1's included) and the exercise passed as written.
- 2026-11-24, track G walk segment 8 (WK11, WK12): stage 1 copies `MainMenu.cpp` before its commands and no longer runs
  `script.create` (its reader's copy could not run as one file); every stage ends with `scene.save`, since the runner
  saved between stages and the reader's copies did not. Passed with the pin build and the 0.8.0 package.
