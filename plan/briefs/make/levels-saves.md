# Brief: `make/levels-saves`

| Field | Value |
| --- | --- |
| Title | Levels, loading screens and save files |
| Kind | H |
| Size | L |
| Tracks | G |
| Needs | `make/menus` |
| From | gamedev "Levels, loading, saves and settings" (§1.15, concept 21); scripting "The gameplay API, part 1" (`SubScene`, `LoadAdditive`) and "The gameplay API, part 3" (`Game`: `Quit`, `LoadScene`, `ReloadScene`, progress, save files); a save file holds one value per line, written and read with the page's exact code (`std::to_string` and `std::stoi` from `basics/programming-2`, the `std::optional` that `Game::ReadSaveText` returns from `basics/programming-3`); use home of additive loads, loading screens and state passed between scenes |
| Unit | `plan/allocation/make-b1.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/levels-saves` — Levels, loading screens and save files

**Covers.** A how-to that turns the course of `make/menus` into a game with levels, a loading screen and save files.
Game flow comes first, in a few sentences and the Third-Person sample's scene flow: a game is scenes (a main menu, a
loading scene, levels) and the moves between them, and what must outlive a scene has to be kept somewhere else, because
no entity survives `Game::LoadScene`. The numbered steps, by goal:

1. Levels: a second course; a goal trigger whose script holds the next level in a scene field and calls
   `Game::LoadScene`; a fall that restarts with `Game::ReloadScene`; a button back to the main menu. A switch loads the next
   scene in the background while the current one goes on, then swaps them between frames; asking again for the scene
   that is loading changes nothing.
2. State between scenes: variables at namespace scope in the script module stay while the game switches scenes; the
   Third-Person sample keeps its settings and its attract mode there (`ThirdPerson.h`), and its main menu starts the
   attract mode, the course playing itself, after ten idle seconds. Such state lives as long as the module's library is
   loaded: in the editor it carries over from one Play to the next, because the module unloads only when the project
   closes; every hot reload, and every reload after a crash, starts it over; an exported game starts it fresh at each
   run. So in the editor a score or a "settings read" flag kept there survives Stop and Play.
3. A loading bar: `Game::GetSceneLoadProgress` on a filled image and a text while the next level loads (the sample's
   `LoadingScreen.cpp`); then the start scene (**File > Set as Start Scene**) and the loading scene that an exported
   game plays while its start scene loads (Project Settings > Game). How fast the bar fills is bounded by the frame's
   upload budgets, which a game cannot raise for its loading screen; one sentence links `assets/uploads`, which explains
   the budgets and the staging bound.
4. A part of a level loaded beside it: `Scene::LoadAdditive` of a room's scene, `Assets::GetLoadProgress` on a bar,
   `SubScene::IsLoaded`, and `Unload`, which takes the room out at once and destroys it over the next frames; a
   sub-scene keeps the IDs of its file, so the same one cannot be loaded twice.
5. Save files: the best time written with `Game::WriteSaveFile` as one value per line (`std::to_string`) and read back
   with `Game::ReadSaveText` (a `std::optional`, empty when there is no file yet) and `std::stoi`, with the page's exact
   code, and checked, because a file can be missing or damaged; names of 1 to 64 safe characters; where the files are
   (the project's `.strata/Saves` in the editor, `<user data>/<Game>/Saves` for the exported game, the folder named after
   the project's name and not its title, so a rename keeps the saves); `ListSaveFiles` and `DeleteSaveFile`; a write
   replaces the whole file and waits for the disk, so a game saves at quiet moments (a checkpoint, a menu).
6. Settings that last: the settings of `make/menus` written to a save file when they change and read once into module
   state, as the sample's `GetSettings` does; the rebinding screen's bindings are kept by the engine already.
7. A checkpoint save: the position and the coins at a checkpoint, saved and loaded on the next start. In a world, the
   player stays in the saved scene with its streaming source, and a restored position is prefetched before the player
   is placed there, since a world starts with the cells around its sources as the scene was saved
   (`make/large-worlds`).

What Strata does not do here: the editor edits one scene at a time (with a world's loaded cells); additive loads run in
play mode only; a game cannot raise its streaming budgets for a loading screen. The exercises, done in a script: a
"Delete save" button on the main menu that removes the best time and shows that none is kept, and a third level named
in the goal's scene field. At the end the reader can split a game into scenes, show progress while one loads, carry
state from one scene to the next and keep a player's progress between runs.

**Leaves out.**

- The scene loader, sub-scene states and the frame's work budget inside → `world/sub-scenes`
- Scene switches inside the runtime of an exported game → `worlds/runtime`
- Scene switches in the editor's play mode → `editor/play-mode`
- Residency, pins and load progress inside → `assets/residency`, `assets/references`
- The upload budgets and the staging bound that limit how fast a loading bar fills → `assets/uploads`
- The export itself, its start scene and loading scene in the export dialog → `make/export`
- Streaming a world in cells, and prefetching before a teleport or a restored player → `make/large-worlds`
- Players' graphics options and their file → `make/quality`
- Text formats such as JSON for a settings file → `basics/data-formats`

**Fit.** `fits`: about 5,300 words against L (5,000). Seven goals of about 20 numbered steps with four excerpts, the
page's own save code and three rules (about 3,800 words) take the most, then game flow with its figure, the two
exercises and the absences.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:342` | concept | home | Game flow and persistence: scenes as levels and menus, loading screens, passing state (fields or module state), save files and where they are; the mistake of expecting entities to survive `LoadScene` |
| `gamedev:198` | feature | home | Scene switches: `Game::LoadScene` by handle or path, `ReloadScene`, `GetSceneLoadProgress`; the background load and the swap between frames; a scene named in a field is an asset reference that a pruned export keeps |
| `gamedev:199` | feature | home | `Game::Quit(code)`: the exported game exits with the code, the editor stops play |
| `gamedev:200` | feature | home | Additive sub-scenes: `Scene::LoadAdditive`, `SubScene::Unload`, `Assets::GetLoadProgress` (`Scene::InstantiateMany` is `make/performance`'s) |
| `gamedev:201` | feature | home | Module state across scene loads: namespace-scope state survives `LoadScene` (the attract mode, a settings cache) |
| `gamedev:202` | feature | home | The start scene (**File > Set as Start Scene**) and the loading scene that plays while the start scene loads |
| `gamedev:203` | feature | home | Save files: `WriteSaveFile`, `ReadSaveText`, `ListSaveFiles`, `DeleteSaveFile`; names; the folders of the editor and of the exported game; synchronous |
| `gamedev:379` | code | home | `Samples/ThirdPerson/Scripts/ThirdPerson.h:1-46`: what the sample's scripts share across scenes (the settings, the attract mode), with `ThirdPerson.cpp` 68-77, where the settings are read from their save file once |
| `gamedev:427` | figure | home | The scene flow of the Third-Person sample: main menu (the attract mode after 10 s), loading, course, pause; the module state beside them |
| `gamedev:504` | rule | home | Entities do not survive `Game::LoadScene`: pass state through the next scene's fields, save files or module state |
| `gamedev:647` | term | home | Save file |
| `gamedev:648` | term | home | Sub-scene (additive load) |
| `gamedev:661` | term | home | Attract mode |
| `scene-ecs:604` | hands-on | home | A part of a level loaded additively with the SDK's `SubScene`, its progress on a UI bar, and unloaded |
| `scripting:523` | hands-on | home | Save and load a checkpoint with `WriteSaveFile` and `ReadSaveText`; an invalid name fails |
| `new:11` | code | home | `Samples/ThirdPerson/Scripts/LoadingScreen.cpp:12-28`: a loading screen: `Game::GetSceneLoadProgress` on a filled image and a percentage. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:12` | code | home | `Samples/ThirdPerson/Scripts/CourseState.cpp:94-104`: reading a value back from a save file that may be missing or hold nonsense. No inventory surveyed the file (`plan/inventory/gamedev.md:694-696`) |
| `new:10` | not-done | home | The editor edits one scene at a time (and a world's loaded cells); `scene.loadAdditive` works in play mode only. Evidence: `StrataEditor/src/Editor/EditorSceneCommands.cpp:458-460` |
| `new:31` | not-done | home | Raising the streaming budgets of a game for a loading screen: no script function and no settings section sets the upload, finalization and staging budgets, and the runtime's `--asset-budget-mb` sets only the GPU texture budget; the page links `assets/uploads` for the budgets and the staging bound. Evidence: `Strata/src/Strata/Asset/AssetResidency.h:56-64` (raise all three for a loading screen); `git grep -ln -e UploadBytesPerFrame -e FinalizeMsPerFrame 822a7a46 -- Strata/src StrataEditor/src StrataRuntime/src StrataScriptCore` finds only the asset manager's files (`Strata/src/Strata/Asset/AssetManager.cpp`, `AssetManager.h`, `AssetResidency.cpp`, `AssetResidency.h`) and the editor's (`StrataEditor/src/Editor/EditorStreamingCommands.cpp`, `StrataEditor/src/Panels/StreamingPanel.cpp`); `StrataRuntime/src/RuntimeApplication.cpp:56, 94-95` |
| `new:37` | rule | home | Step 2: module state at namespace scope lives as long as the module's library is loaded: in the editor it carries over from one Play to the next, since the module unloads only when the project closes; every hot reload and every reload after a crash starts it over, because a new library is loaded; an exported game starts it fresh at each run. Evidence: `Samples/ThirdPerson/Scripts/ThirdPerson.h:3-5` (the module stays loaded while the game switches scenes); `StrataEditor/src/Editor/EditorContext.cpp:655` and `:2406-2419` (the only unload, `CloseScriptEngine`, when the project closes); `StrataEditor/src/Editor/EditorContext.cpp:2594-2604` (a build loads the module again only when it changed or crashed); `Strata/src/Strata/Scripting/ScriptEngine.cpp:107` (a reload unloads the previous module) |
| `gamedev:515` | rule | link | Prefetch before placing a restored player in a world, and keep the player with its streaming source in the saved scene, since the start cells load around the sources as the scene was saved (step 7; the rule's home is `make/large-worlds`, the prepared start's `worlds/physics-scripts`) |
| `new:32` | hands-on | home | Exercises, done in a script: a "Delete save" button on the main menu that calls `Game::DeleteSaveFile` and then shows that no best time is kept (`ReadSaveText` empty); a third level named in the goal's scene field. Evidence: `StrataScriptCore/Include/StrataScript/Game.h:129` (`ReadSaveText`), `:151` (`DeleteSaveFile`), `:47` (`LoadScene` by handle) |
| `scripting:129` | feature | home | `Game` and `WindowMode` in the SDK: quit, scene switches and their progress, save files as bytes or text; the window functions are taught on `make/menus` (`gamedev:204`); `reference/script-api` lists the declarations and links here |
| `scripting:121` | feature | use | `Scene::LoadAdditive`, `SubScene` and `Assets::GetLoadProgress` |
| `scripting:338` | concept | use | Player-facing systems: save files written whole, with validated names |
| `worlds-runtime:78-79` | feature | use | Sub-scenes and their states, in a game maker's words (their home is `world/sub-scenes`) |
| `worlds-runtime:93` | feature | use | Scene loads and quits from scripts, which the exported game honors |
| `worlds-runtime:126-127` | feature | use | Scene switches that never block, and the loading scene |
| `worlds-runtime:149` | feature | use | The saves' folder is named after the manifest's name, not the title |
| `worlds-runtime:237` | concept | use | Additive scenes |
| `worlds-runtime:288` | concept | use | Startup and scene switching as players see them |
| `worlds-runtime:448` | rule | use | Saves are keyed by the manifest's name, never the title |
| `gamedev:577` | term | use | Start scene and loading scene: this page teaches the loading scene (`gamedev:202`); the item's home stays on `make/export` for "start scene", and the glossary step splits the entry and homes "loading scene" here |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A main menu, a pause menu and a settings screen | `make/menus` | must |
| Entity and asset fields; a scene in a field | `make/script-fields` | must |
| `std::to_string` and `std::stoi` | `basics/programming-2` | must |
| `std::optional` with `has_value` and `value_or` | `basics/programming-3` | must |
| Namespaces and `::` | `basics/programming-1` | must |
| `Game::ReloadScene` in one step | `make/project-coin-run` | must |
| A filled image and a text on the HUD | `make/hud` | must |
| Triggers | `make/physics` | must |
| Asking for assets early | `make/scripting-scene` | must |
| The project folder and its hidden `.strata` folder | `make/project-files` | must |
| The exported game and the user data folder | `make/export` | must |
| Load progress and the dependency closure inside | `assets/references` | helps |

**Starting state.** The end checkpoint of `make/menus`, downloadable: the course with its main menu, pause menu,
settings screen, rebinding screen and name field. The steps add a second course scene, a goal and a small room scene.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `attract-mode` | Attract mode | - |
| `save-file` | Save file | - |
| `sub-scene-additive-load` | Sub-scene (additive load) (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b1-3 | should | shape | `make/gameplay-math`, `make/timers-events`, `make/script-fields`, `make/script-builds`, `make/levels-saves` | style.md gives a how-to a `## Variations` section: the same goal under other conditions. The Covers of these five how-tos name no variation, so the writer has nothing to fill it with. The how-tos of `make-a` and `make-b2` name theirs. (`make/recipes` has its "what to change" per recipe.) | Each Covers names two variations (about 250 words a page). From the pin: gameplay-math, aiming with the right stick through the Look action instead of the cursor (`FollowCamera.cpp:57-60`), and a turret that turns at a limited speed (critic-make-b1-16); timers-events, a timer in `OnFixedUpdate` fed with the fixed delta, for gameplay that keeps step with physics, and a held gamepad direction repeated (critic-make-b1-5); script-fields, tuning many spawners at once through their prefab (critic-make-b1-4); script-builds, the plain `cmake -S` and `-B` build as a check that the code compiles on another machine (critic-make-b1-1); levels-saves, three save slots named "Slot 1" to "Slot 3" and listed with `ListSaveFiles`. The five Fit lines count them. | `style.md:535-541`; `allocation/make-b1.md:5-24`, `:91-111`, `:174-193`, `:420-440`, `:922-962`; `allocation/make-a.md:130`, `:424`; `allocation/make-b2.md:393`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`, `:157-158` |
| critic-make-b1-7 | should | thin-home | step 5 (`scripting:523`) on `make/levels-saves` | The page reads the best time back with `std::stoi` and says the value is checked, because a file can be damaged. `std::stoi` throws on text that is no number, or a number too large, and an exception that escapes turns the script off ("The script is disabled."), as `basics/programming-2` warned. So the page's exact code must check the text before it converts. The sample reads its best time with `std::strtof`, and checks where the number ended and its range. | The page's code checks that the text is 1 to 9 digits before `std::stoi`, or uses `std::strtol` with its end pointer, as the sample does with `strtof`; the step's "If you do not see it" names the log line (about 80 words). | `allocation/make-b1.md:945-947`; `allocation/basics-a.md:244-246`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:299-307`; `Samples/ThirdPerson/Scripts/CourseState.cpp:94-104` |
| critic-make-b1-8 | should | missing-item | step 6 on `make/levels-saves` | Step 6 writes the settings "to a save file when they change". A slider reports a new value on many frames while it is dragged, and `WriteSaveFile` writes the whole file and waits for the disk before it returns. So the page would write to the disk on every frame of a drag, against its own rule of saving at quiet moments. The sample marks a save pending and writes once the slider has rested for 0.4 s of real time, or when the screen closes. | Step 6 saves as the sample does: a pending flag, the real time of the last change, one write once the value rested or the screen closed, with `SettingsMenu.h:29` and `SettingsMenu.cpp:16`, `:47-49` as a short excerpt (about 120 words). | `allocation/make-b1.md:950-952`; `StrataScriptCore/Include/StrataScript/Game.h:104-107`; `Samples/ThirdPerson/Scripts/SettingsMenu.h:29`; `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:16`, `:47-49`, `:83` |
| critic-make-b1-9 | should | thin-home | step 2 (`gamedev:201`, `gamedev:379`) on `make/levels-saves` | Step 2 tells the reader to keep state at namespace scope, but the excerpts show only the header's declarations and `GetSettings`. Where the variables live, `ThirdPerson.cpp:15-21` (an unnamed namespace in one `.cpp`, reached through functions that the header declares), is in no row. A reader who writes the variable into a header meets one of two mistakes. Two `.cpp` files that include it fail to link, because it is defined twice. Or, with `static`, each file gets a copy of its own, and the menu and the course see different values, with no warning. | Add `ThirdPerson.cpp:15-21` to the excerpts of `gamedev:379`, and the two mistakes to the step's "If you do not see it" (about 150 words). | `allocation/make-b1.md:931-936`, `:988`, `:991`; `Samples/ThirdPerson/Scripts/ThirdPerson.h:3-5`, `:31-46`; `Samples/ThirdPerson/Scripts/ThirdPerson.cpp:15-21`, `:68-77` |
| critic-make-b1-10 | should | order | recipe 4 of `make/recipes`; the managers of `make/patterns` | Recipe 4's token bucket is a variable outside any class, in an unnamed namespace of `Impact.cpp`, shared by the `Impact` script of every body; that sharing is the recipe. The page's Assumes row sends the reader to `make/levels-saves` (helps), which stands five pages later on track G, so no page before has taught it. `make/patterns`, which `make/recipes` needs, already compares a manager with a global variable. | The managers section of `make/patterns` says what such a variable is: one for the whole module, shared by every script, kept while the module stays loaded; and when it fits, such as a sound budget (about 100 words). The Assumes row of `make/recipes` then names `make/patterns` (must). `make/levels-saves` keeps the lifetime (`new:37`) and the use across scenes. | `allocation/make-b1.md:267-269`, `:352-355`, `:409`; `tracks.md:105-111`; `Samples/PhysicsPlayground/Scripts/Impact.cpp:13-36` |
| critic-make-b1-20 | could | missing-item | the game flow and step 3 of `make/levels-saves` | Four facts of game flow are in no row. Play in the editor runs a copy of the open scene, so playing the course skips the main menu and the module state it sets. The project's Loading Scene plays only while an exported game's start scene loads; between levels the bar belongs in the scene that plays. A second `LoadScene` for another scene replaces the first, and `Quit` wins over a switch. Both take effect after the frame's update, so the code after the call still runs. | Add the four facts to the game-flow paragraph and to step 3 (about 120 words). | `allocation/make-b1.md:922-941`; `StrataEditor/src/Editor/EditorContext.cpp:1382`; `Strata/src/Strata/Runtime/GameRuntime.cpp:131-144`; `StrataEditor/src/UI/SettingsPages.cpp:194-196`; `StrataScriptCore/Include/StrataScript/Game.h:27-29` |
