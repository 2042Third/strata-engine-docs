# Notes: make/recipes

## New terms

None proposed. The page defines seed and token bucket, both homed in the glossary for this page.

## Since

0.3.0: `Random` is in the SDK header of the first tag (Gameplay.h, added at v0.3.0). The samples' Coin.cpp and Impact.cpp first appear at v0.5.0.

## Requests

- Host for Further reading: pcg-random.org (the PCG paper by Melissa O'Neill is cited without a link).
- No figures file: the one picture is a Mermaid diagram (the token bucket).
- The exercise 1 tutorial file starts from the basic3d template and checks the trigger's body and tag by commands; it was not run.

## Not verified

- The editor path to make a child entity: the page says to drag the model's row onto the coin in the Hierarchy; only the command (`entity.create` with `parent`) was checked.
- The label of the sample in the launcher's Open Sample list (the page says "the sample"); the command `project.openSample` takes `ThirdPerson`.
- That an empty entity is made by the **+** button's menu (taken from sibling pages, not from the pin).
- Whether a hidden (inactive) entity's own script keeps running; the exercise 2 solution avoids the question by hiding only the model.
- The result of the dice replay (numbers of `Range(1, 6)` for seed 1): the page states only that two runs match.
- Mouse units of the pointer ray on a scaled display (critic-make-b1-22): the grab uses the same division as `Playground::GetPointerRay`; not checked.
- Asset import of copied clips: the page says the editor imports them when it sees them (as the sound page teaches); not run. The command form, `asset.import` of the three clips of `Samples/PhysicsPlayground/Assets/Sounds/Impacts/` of the 0.8.0 package into `Sounds/Impacts`, was run (`docs-work/walkfix-G7/run`): three assets at the three paths.

## Findings not applied

- critic-make-b1-22: the open item about mouse units on a scaled display is not carried as a page item; it is listed under Not verified.
- critic-make-b1-3 (variations): applied as the page's `## Variations`.
- critic-make-b1-10: applied: the shared variable is explained where the token bucket is taught (module-wide, shared by every instance, kept while the module is loaded); `make/levels-saves` is not linked.
- critic-make-b1-11: applied: the section "Take a recipe into your project" says to write one's own script, to replace calls to scripts one lacks, to copy sounds found by path and to list them under Always Include.
- critic-make-b1-19: applied: the `Random` section says a plain `Random` member starts over on a hot reload and the replay script re-seeds and skips the rolls made; the `Timer` case is in exercise 2's answer.
- The Open World day and night script is named in `## Result` with a link to `make/reflections`; `Timer` and `KeyRepeat` are only touched by exercise 2.

## Clerk

- Admitted to external-hosts.txt: pcg-random.org (its front page is the PCG site).
- Left for the planner: the exercise tutorial's first run.

## Walk G-final-7

- WK16: step 1 of Recipe 4 names the source of the three clips, the Physics Playground's own (`Samples/PhysicsPlayground/
  Assets/Sounds/Impacts/`, Kenney, CC0 by the sample's `CREDITS.md:14`), and its command tab imports them with
  `asset.import`.
- WK17: the page quotes `Impact.cpp` lines 6-11 (the includes, with `<algorithm>` for `std::clamp`, whose absence gives
  C2039), 38-46 (the fields, `OnCreate` and `OnReload`) and 63-87 (`FindSound`, the member, the registration); with the
  two excerpts that were there, every line of the class is on the page.
- WK18: the page quotes `Coin.cpp` lines 10-15 (the fields) and 47-59 (the members and the registration), says to keep
  the SDK's include in place of `CourseState.h` and to add `<cmath>`, and gives `c_BallScale` (0.5,
  `Samples/PhysicsPlayground/Scripts/Playground.cpp:19`) and `<algorithm>` for the pour. The walker's results matched
  with exactly these values.
