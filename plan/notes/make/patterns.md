# Notes: make/patterns

## New terms

- state machine: a script that is always in exactly one of a fixed list of named states and moves between them along written rules; this page is the home; alias: state machines, states.
- manager: one script that owns a piece of shared work or state, so that other scripts ask it instead of keeping copies; this page is the home; alias: managers.
- object pool: a set of objects made once and reused instead of created and destroyed; this page is the home; alias: pool, pools.
- update method: a function that the engine calls once a frame on every object so that the object moves itself a little; this page is the home.
- flag: a variable that is either true or false; this page is the home; alias: flags.

## Requests

- Word list: `Nystrom` (author of Game Programming Patterns; names.txt).
- Hosts: gameprogrammingpatterns.com, docs.unity3d.com and docs.godotengine.org are already on the list.
- Link targets assumed to exist when the book is built: `../appendix/game-ai.md`, `../appendix/not-in-strata.md`, `../animation/state-machines.md`, `levels-saves.md`, `animation.md`.
- For the tool builder: `tools/tutorials.py compile` writes the entries of solution zips with the date 1980-01-01, so a
  reader who copies a file over one the editor made meets the stale build of `## Engine`. A date of the compile (or of
  the pin) would avoid it; reproducible zips would need a fixed date that is still recent.

## Since

- since 0.3.0: scripts, `SetActive` and contacts date from the first tag (inventory gamedev:321, 374).

## Not verified

- That a module-level variable (`s_Tokens` of `Impact.cpp`) starts over after a hot reload of the module: written from how modules load, not read in code.
- The sample README line that says the Tetris cells are "created and destroyed by a script" (taken from the brief, `Samples/Tetris/README.md:14`); the code side (no `Destroy` in `Samples/Tetris/Scripts`) was checked.
- The claims about Unity's Find and Godot's get_node in the comparison table rest on the cited manuals, not read for this page.
- The 240 creations in the gun example are arithmetic (4 shots a second for 60 seconds), not a measurement.

## Findings not applied

- critic-make-b1-21: applied. The row `new:18` is not claimed as a home; the pool section keeps its sentence about what a hidden entity receives.
- critic-make-b1-10 and critic-make-b1-14 applied (the global variable paragraph; the prefab pool paragraph). The Assumes row of `make/recipes` is not this page's file.
- Brief item gamedev:372 (the rules class kept apart) appears only in the "Where it lives" list, not taught.
- The brief's pause-menu excerpt is quoted from `OnUpdate`; the settings panel is read through `IsOpen`, so the "three situations" are two stored values, as the page says.

## Clerk

- Admitted terms homed here: state machine (alias state machines; "states" stays plain, since the glossary's State is animation/state-machines'), object pool (alias object pools; pool and pools stay plain beside memory pool and thread pool), update method.
- Refused as terms: manager and flag, common words (tools/data/common-words.txt); the bold explanations may stay.
- Admitted to names.txt: Nystrom.
- Left for the planner: the link targets to unwritten pages.

## Walk G-final-7

- WK15: the answer of exercise 2 says to paste the text of the download's `Scripts/BulletPool.cpp` into the file that
  **New Script...** wrote, and why a copied file is not built. Checked with the 0.8.0 package (`docs-work/walkfix-G7/run`,
  `verify.py`): with the template built and the download's file copied in with the date 1980-01-01, `script.build`
  answered success with `moduleChanged` false and the log line `(the module was up to date)`, and play held no bullet;
  after the date was set to now, the build changed the module and play held 20 bullets.

## Engine

- `script.build` keeps a module whose source was replaced by a file with an older modification time: the script build
  is the generated MSBuild project's incremental build (`StrataEditor/src/Editor/ScriptBuild.cpp`; `ModuleChanged` at
  line 1285 compares the module's write time), which compiles only sources newer than their objects. The command reports
  success, so a reader sees the old class with no error. The page tells the reader to paste the text instead.
