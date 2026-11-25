# Notes: make/levels-saves

## New terms

- None proposed. The page defines attract mode, save file, sub-scene (additive load) and loading scene in bold.

## Requests

- The exercise file starts from the sample ThirdPerson: the Coin Run chain through `make/menus` has no goal entity, and the page has no tutorial file of its own, so the sample's `Course` scene stands in for `Main`.

## Since

- since 0.3.0: Game.h with the save files and scene switches is in v0.3.0 (git tag --contains at the pin).

## Not verified

- Module state across Play and Stop in the editor, and its reset by hot reload (taken from the brief's evidence lines, EditorContext.cpp and ScriptEngine.cpp, not read).
- The command tabs of steps 4, 5 and 8 only build; steps 1 to 3, 6 and 7 were run once with the 0.8.0 package (see Tutorial run), not by a tutorial file. The loading scene during an exported game's first load was not watched.
- Editor path "Play rebuilds changed sources" is taken from the script.create command text.

## Findings not applied

- critic-make-b1-3: only the three-slots variation is carried, with two more (version line, attract mode).
- critic-make-b1-20: three of the four facts are in the game-flow paragraphs; the editor Play copy is in the page, the loading scene note is in the loading bar section.
- The sample's CourseState strtof reading is described, not quoted (it needs pointers outside the closure).

## Clerk

- No term or word asked.

## Tutorial run

- exercise-1 passes (2026-11-18, round 3). It was a single `scene.saveAs`; it now builds the page's step 1 and 2 state on the sample (opens `Scenes/Course.stscene`, writes `NextLevel.cpp` from step 2's code, saves `Level2`, attaches `NextLevel` with `Next` = `Scenes/MainMenu.stscene`), then does the answer: saves `Level3` (its goal keeps the main menu), sets `Next` of `Level2`'s goal to `Scenes/Level3.stscene`, plays `Level2`, moves the player into the goal and waits for the running scene `Level3`.
- `script.add` and `script.setField` take a scene path for an `AssetHandle` field and keep its handle; `script.get` shows the handle, so the file checks the path through `asset.info`.
- For the page's writer, not run: step 2's command tab runs after step 1's `scene.saveAs`, so it attaches `NextLevel` with `Next` = `Scenes/Level2.stscene` to the goal of `Level2` itself, while the tab's prose gives `Level1`'s goal `Level2` and `Level2`'s the main menu; the tab needs a `scene.open` of `Main` (and `Level2`'s goal the menu) once the page has a tutorial file.
- 2026-11-24, track G walk segment 8 (WK14 to WK16): "Build it" now makes a goal and the player's tag (the course of
  `make/menus` has neither), shows `NextLevel.cpp` whole and the new `RoomDoor.cpp`, and gives commands for the loading
  scene and the room. The page still has no tutorial file of its own; its steps 1 to 3, 6, 7 and 8 were checked with the
  0.8.0 package on Menus' checkpoint 7 (`docs-work/walkfix-G8/verify.py`): `Main` to `Level2` to `MainMenu` through
  the goals, the Filled bar and its script, the room loading and unloading, and the save files `best-time.txt.save` and
  `checkpoint.txt.save`.
