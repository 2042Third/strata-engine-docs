# Notes: make/timers-events

## New terms

- cooldown: the wait before an action can be used again; a one-shot timer makes one. Home: this page. Aliases: cooldowns.

## Since

0.3.0: `Timer`, `KeyRepeat` and `Time` are in the script SDK at the pin; the first-tag date was not checked per symbol.

## Requests

- Extra words: `cooldown`, `coroutine` (one use, in "Strata has no coroutines"; written as code in the page, still counted).
- Host: none beyond `gameprogrammingpatterns.com` and `docs.unity3d.com`, both listed.
- No figure is requested: the page has no picture.

## Not verified

- That the scripts under `tutorials/make/timers-events/` build and play as described: not compiled or run (`Key::D1`, `SetProperty("UIImage", "FillAmount", ...)`, `Scene::Instantiate(handle, translation)`, and `anchor` `middleCenter` of `ui.create` are checked in headers and sources only).
- That a dynamic Rigid Body is the default `Type` of `RigidBody` for `component` values `{}` in `entity.create`.
- That `FindEntityByName` finds a text whose color alpha is 0 (the page keeps the entity and never deactivates it).
- That the Hierarchy menu items **Cube**, **Empty** and the entity context item **Create Prefab** read as written (taken from earlier pages).
- The links `/input/actions/` and `/make/menus/`: the pages may not exist yet.
- That fixed steps do not run at time scale 0 (the page does not claim it).

## Findings not applied

- critic-make-b1-3: applied as two Variations (timer on the fixed step; held action or gamepad direction).
- critic-make-b1-5: applied (paragraph after step 6).
- critic-make-b1-6: applied (step 8, with the "registered twice" message at `ScriptModule.cpp:979-983`).
- critic-make-b1-11: belongs to `make/recipes`.
- critic-make-b1-19: applied for `Timer` (hot reload starts it again, `OnReload`); the replay sentence belongs to `make/recipes`.
- The `Assumes` rows of finding 6 are not mine to edit; the page assumes `#include` and `ST_SCRIPT_CLASS` in a `.cpp` as taught.

## Clerk

- Admitted to extra-words.txt, not as a term: cooldown, cooldowns (G0 has 5: a game player's word, and the page defines it in no bold sentence); coroutine, coroutines (named once, as what Strata lacks).

## Tutorial run

- 2026-11-18, pin build (Release): the files passed as written (round 1) but only built and stepped. Strengthened with the page's own values: the prefab exists and no `Crate` is left, the texts; `scale 0.25 delta …` and `scale 0 delta 0 unscaled …` in the log (running play, as the reader plays); one crate after 2 s, two after 4 s, the first at rest on the ground at x -6; the dash moves 3 m and a second press within 1.5 s does not; the marker steps once, waits, then runs to -4; `Paused` alpha 0, 1, 0, 1 every half second after **P** and 0 after a second **P**; the player collects the crate at x -6, `Score` 1 and `Score: 1`. Exercise 1: the bar's `FillAmount` 1, about 0.5 at 0.75 s after a dash, 1 after 1.5 s.
- Measured log line at scale 0.25: `scale 0.25 delta 0.00405718 unscaled 0.0162287`; at 0: `scale 0 delta 0 unscaled 0.0169184` (the page's values). The walker of G-final-7 (WK9) read `delta 0.00206428 unscaled 0.0082571` at about 120 frames per second: since its answers the step says that `delta` is a quarter of `unscaled`, which is the frame's length, about 0.017 at 60.
- Page: step 3's command tab gained the key presses and `log.read`; at scale 0 a tap of `input.key` never ends (no step runs), so **P** and the second **L** are `press`.

## Engine

- `play.step` gives scripts the fixed step as their delta at any time scale (`Scene.cpp:2240`), though `ScriptABI.h:322` says delta times are scaled by the time scale: stepped play shows no slow motion and no freeze. Read in the source; the file checks the time scale in running play.

## Walk G-final-7

- WK10 and WK11: step 5 quotes the whole of `Player.cpp` but its first three lines and the registration (L6-L23 and
  L25-L40, two fences under the 25-line limit); step 9 quotes `Pickup.h` (L6-L12, its first lines named in prose) and
  the three lines of `Dropper.cpp` that make the crate and add `Pickup` (L27-L29), with the reason `crate` is no `const
  Entity`: `Entity::AddScript<T>()` is not `const` (`StrataScriptCore/Include/StrataScript/Entity.h:89-92`), as every
  function of `Entity` that changes the entity; the walker's C2662 is the compiler's answer to that. Not an engine fault.
- To keep the page within its size (M, 4,000 words) the sentence on the menu key repeat of the UI map, the line
  callouts of step 7, the variation on held actions (the paragraph after step 6 says the same) and a few words of the
  introduction and of the coroutine sentence went.
- The tutorial file is unchanged: it already holds these files whole.
