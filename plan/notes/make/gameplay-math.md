# Notes: make/gameplay-math

## New terms

None proposed. The page defines **offset**, **unit vector**, **dot product**, **yaw** and **cross product** in bold as plain explanations; the glossary homes none of them here, so the clerk may admit them.

## Requests

- Word list, extra words: "turret" (the page's example, 38 uses). The example could be renamed "guard" if the editor refuses it.
- No new hosts.

## Not verified

- Whether the pointer ray's division of `Input::GetMousePosition` by `Game::GetWindowSize` agrees on a scaled display in an exported game (check "Mouse units on a scaled display", critic-make-b1-22); the page tells the reader to check that the barrel lands under the cursor.
- The Inspector's display of an `Entity` script field and the way a reader sets it (the page says "set `Target` to `Ball`"); the command form (`script.add` with `fields`) is verified in the command's description.
- `script.create` accepting the field type `Entity` in `fields` (the type name is taken from the SDK's field types, not from the command's schema).
- The exact text of log lines of floats (the page says "7 or close to it").
- Editor labels **+ ▸ Cylinder**, **+ ▸ Cube**, **+ ▸ Sphere** are used as the physics page uses **+ ▸ Cube**.

## Findings not applied

- critic-make-b1-2, -3, -16 are applied (shot velocity in `OnFixedUpdate`; two variations; smoothing a turn with the wrap and `slerp`). critic-make-b1-22 is applied as a hedge only (see Not verified).
- The brief's "rolling ball" with a dynamic RigidBody is changed to a ball moved by the `Orbit` script (no body), so that its path and the numbers of the worked examples are exact.
- The exercise G12 is started from a new Basic 3D project (`startsFrom` template), not from the page's end state, because the page has no checkpoints.

## Tutorial run

- Exercise 3 passed as written at the pin (round 1); the file was then strengthened with the exercise's own result:
  in play, a `Shot` instance dropped onto the goal logs "Goal: 1" and is removed (so the instance keeps the root's
  name `Shot`), and one dropped onto `GlassWall` falls through to the ground (Translation y 0.5).
- The click itself (`Shooter`'s pointer ray) cannot be run: the runner's editor is headless, where no Game view sets
  the input viewport, so `Game::GetWindowSize` is (0, 0) and `GetPointerRay` returns false (Input.cpp:542,
  GameViewPanel.cpp:279 at the pin); a simulated click spawned no ball (round 2). Not an engine fault: no command
  promises a window size without a Game view.

## Since

0.3.0: the first release of the scripting module (as the other pages of the make part); the release of `Motion` itself was not checked.

## Clerk

- Refused as terms: unit vector, dot product and cross product (the glossary homes them on basics/math-vectors; only their home words them), yaw (an alias of yaw angle, basics/math-rotations), offset (a common word, tools/data/common-words.txt). The bold explanations may stay plain.
- Admitted to extra-words.txt: turret, turrets (G0 has 5).

## Walk G-final-7

Checked with the official 0.8.0 package (`docs-work/walkfix-G7`, `verify.py` in `run/`, `verify2.py` in `run2/`).

- WK1: "Before you start" gives the `project.create` line and says that the page offers no download of its steps.
- WK4: `entity.create` refuses a parent given by name ("Parameter 'parent' must be an ID (16 hexadecimal digits)",
  reproduced); the command tab gives `<id of Turret>`.
- WK5: the editor camera of a new Basic 3D project stands at (0, 2, 6), forward (0, -0.316, -0.949) (`camera.get`); the
  capture from it (`run/turret-editor.png`) shows the cylinder and a thin edge of the barrel above its top, and one from
  (-3, 6, 2) toward (-3, 0.5, 0) (`run/turret-above.png`) shows the barrel sticking out of the far side. The step says
  both, and how to look from above.
- WK6: the SDK's `Log::Info` writes floats through a standard stream (`StrataScriptCore/Include/StrataScript/Log.h`),
  so a tiny rounding error reads with an exponent (`-5.96046e-08`, the walker's line); the step says so.
- WK7: Since the answers, the step removes the script and adds it again. Checked (`run2/`): with `Turret-8.cpp` built and `Target` set, then `Turret-9.cpp` built, play logged `Script fields: script 'Turret' has no field 'Target'; the stored value is ignored`; after `script.remove` and `script.add`, play logged no such line.
- WK8: the answer of exercise 3 says how to run the download's `stage-1.commands.json` with `StrataEditor --commands`,
  the runner `tutorials.py run` uses for every reader copy, with the Windows line of `make/automated-playtests`.
