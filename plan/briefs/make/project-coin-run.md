# Brief: `make/project-coin-run`

| Field | Value |
| --- | --- |
| Title | Project: Coin Run, a first finished game |
| Kind | T |
| Size | L |
| Tracks | G, B |
| Needs | `make/export`, `make/sound`, `make/play-test-debug` |
| From | gamedev "Tutorial: Coin Run" (hands-on G8, as a rolling ball, because block A has no character page); skill `strata-make-a-game` §4-8; finishing it: win, lose, restart (`Game::ReloadScene` in one step; game flow's home is `make/levels-saves`), polish, the exported game; "what next" tells a track B reader that track G is open from `make/gameplay-math` at once, and that the rest of `basics` can come later |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/project-coin-run` — Project: Coin Run, a first finished game

**Covers.** The page turns Coin Run into a finished game and ships it again, closing block A. It starts with the plan
of a small game, written as a list of what makes a round (collect every coin before the time runs out) and what is
still missing (a way to win, a way to lose, a way to start again, polish). The steps, in sections that each end in a
checkpoint. (1) A game state in one script: a `CoinRunGame` script on an empty entity holds the round's state
(playing, won, lost) as a small `enum class`, the time left as a field, and reads the coins left. (2) Win: when no coin
is left, a centred panel "You win" appears (a UI panel and text, shown with `SetActive`), the ball stops, and the
complete sound plays (`Samples/ThirdPerson/Assets/Sounds/Complete.ogg`). (3) Lose: when the time runs out, a "Time's up"
panel. (4) Restart: a Button action **Restart** in the Gameplay map; `Game::ReloadScene()` starts the round again in
one step, and why entities do not survive a scene load (game flow's home is `make/levels-saves`). (5) Polish, each a
small step: the camera framed so that the whole level reads; a difficulty field for the time; the coins' bob and spin
tuned in the Inspector; a short glow and sound when a coin goes; the HUD's colors when time runs low. (6) Check the
game by playing it: a list of what to try (collect all, let the time run out, restart twice, play at 4:3 and 21:9),
and the Console free of warnings. (7) Ship it again: version 1.0.0 on the Game page, a pruned export with **Always
Include**, the exported game run windowed and headless as `make/export` taught. (8) Credits: `CREDITS.md` complete
(the coin model, the sounds, the textures, the music) and the notices file in the folder; one sentence says that the
reader may ship the game with the book's code in it, by the permission that `appendix/credits` states, and links it.
The exercises (`new:48`) are open extensions done in the editor and in scripts. The skill
`strata-make-a-game` sections 4 to 8 are the model for the order (scripts, scene, check by playing, export); its
command-only parts (play-tests by command, viewport captures) are left to `make/automated-playtests`. "What next" for
both tracks: track G goes on at `make/gameplay-math`; a track B reader may take track G at once, from
`make/gameplay-math`, and read the rest of `basics` later, or go on with `basics/numbers`; the Tetris and platformer
projects of block C and `make/designing-a-game` are named. At the end the reader owns a finished, exported game.

**Leaves out.**

- Game flow: levels, loading screens, saves, state passed between scenes → `make/levels-saves`
- Menus, buttons and a pause screen → `make/menus`
- A player character with a controller and a follow camera → `make/characters-cameras`
- Play-tests by command and a regression script for Coin Run → `make/automated-playtests`
- Planning a game: core loop, scope, prototype, playtest → `make/designing-a-game`
- Scene switches inside → `worlds/runtime`, `editor/play-mode`
- State machines and managers as patterns → `make/patterns`

**Fit.** `fits`: about 5,300 words against L (5,000). Eight steps in four sections with their checkpoints and four short
scripts or changes from the tutorial's files take most of it, with the plan and checking lists, "what next" and three
open exercises with worked solutions.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:541` | hands-on | home | G8 as a rolling ball (block A has no character page): actions, coins as trigger prefabs that spin, the HUD, the coin sound, a win panel, a restart with `Game::ReloadScene`, title and icon, the export and its run |
| `new:48` | hands-on | home | Exercises, open extensions ("make it yours") with worked solutions: **Basic.** a field `Points` on the coin prefab, overridden on one gold coin, and the HUD's score summed from it; **Medium.** a sixth coin on a platform that the ball reaches only with a jump; **Hard.** a kinematic obstacle moved in `OnFixedUpdate` that sends the ball back to the start with `Teleport` when it touches it. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:85` (`OnFixedUpdate`), `:89-92` (the contact callbacks); `StrataScriptCore/Include/StrataScript/Physics.h:120` (`Teleport`) |
| `gamedev:198` | feature | use | `Game::ReloadScene`, in one step; its home is `make/levels-saves` |
| `gamedev:342` | concept | use | Game flow: entities do not survive a scene load |
| `gamedev:506` | rule | use | The checking list's "a scene with no light" reminder |
| `scripting:129` | feature | use | The SDK's `Game` |
| `scripting:513` | hands-on | use | Pickup and score, finished into a round |
| `editor-core:220` | feature | use | Scene reloads asked by a script, carried out by the editor in play mode |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Exporting, pruning and running the exported game | `make/export` | must |
| The HUD: canvases, texts and their script | `make/hud` | must |
| One-shots and early requests | `make/sound` | must |
| Playing, pausing and debugging a script | `make/play-test-debug` | must |
| Input actions and adding a Button action | `make/input` | must |
| Scoped enums, `if` and classes | `basics/programming-3` | must |
| Game flow and scene loads | `make/levels-saves` | helps |

**Starting state.** The end state of `make/export` (`startsFrom {"tutorial": "make/export"}`): Coin Run with its HUD,
sounds and a first export; the project's Always Include list set. The page ends with the finished, exported Coin Run.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-2 | must | stale-item | `make/prefabs` (step 4), `make/scripting-scene` (step 7), `make/project-coin-run` (step 5) | Three steps treat a coin's emission as a value of the entity. Emission belongs to the material asset `Gold.stmat` that every gold coin shares; a Mesh Renderer holds only Mesh, Material and Cast Shadows, and it sits on a child of the model's root. So `make/prefabs` step 4 changes every gold coin before Apply is pressed, and the emission raised from a script (`make/scripting-scene`) and the glow (`make/project-coin-run`) cannot be done, as the page's own `new:19` says. | `make/prefabs` step 4 changes a value an instance holds (the mesh child's Scale or its Cast Shadows on one coin) and applies it. `make/scripting-scene` step 7 swaps the mesh child's material, `SetProperty("MeshRenderer", "Material", glow)`, with `Materials/GoldGlow.stmat` asked for early, as Tetris swaps materials; `make/project-coin-run` step 5's glow is the same swap. About 60 words in all. | `allocation/make-a.md:615-616`, `:1063-1065`, `:1812-1813`, `:568`; `Strata/src/Strata/Renderer/Material.h:30-31`; `StrataTests/Architecture/ComponentSchema.json:404` (MeshRenderer: Mesh, Material, CastShadows); `Strata/src/Strata/Asset/GltfImporter.cpp:1974-1987`; `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| critic-make-a-4 | should | missing-item | `make/scripting-scene` (step 5) | `Scene::FindEntityByName` and `FindEntitiesByTag` also find inactive entities, and an entity destroyed this frame until the frame ends. So a coin hidden with `SetActive(false)` still counts among the coins left, which the HUD and `CoinRunGame` count by tag; and the hidden "You win" panel of `make/project-coin-run` can be found by its name. No page says so. | Step 5 adds two sentences: the finds see inactive entities and those destroyed this frame; a count of what is left skips them with `IsActive()`, or counts after destruction. `make/project-coin-run` step 2 finds its hidden panel that way (about 50 words). | `allocation/make-a.md:1060-1062`, `:1066`, `:1808`; `Strata/src/Strata/Scene/Scene.cpp:793-813`, `:847-866` (no test of activity); `StrataScriptCore/Include/StrataScript/Entity.h:38` |
| critic-make-a-7 | should | stale-item | `make/hud` (steps 3 to 5), `make/project-coin-run` (steps 2 and 3) | After the canvas of step 1, steps 3 to 5 make the texts and the panel with **+ ▸ UI ▸ ...**. The Hierarchy's **+** button (and the Entity menu) always creates at the top level, and a UI element made outside a canvas gets a new canvas of its own, so each step adds another canvas. An element goes into the canvas through the canvas's right-click **Create Child ▸ UI ▸ Text**, which no page names. | Step 3 makes its text with a right-click on the canvas ▸ **Create Child ▸ UI ▸ Text** and says why; steps 4 and 5 and the win and lose panels of `make/project-coin-run` do the same; `make/scenes-entities` names **Create Child** beside the "+" menu in one sentence (about 70 words). | `allocation/make-a.md:1509-1513`, `:1808-1810`; `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:560`, `:929-931`; `StrataEditor/src/EditorLayer.cpp:1582`; `StrataEditor/src/Editor/GameUIPresets.cpp:301-310`; `Docs/Manual/GameUI.md:11-14` |
| critic-make-a-11 | should | missing-item | `make/physics` (step 4), `new:48` on `make/project-coin-run` | `RigidBody::Teleport` moves the body and keeps its velocities. Step 4's reset key would put the ball back at the start still rolling at its old speed, and the Hard exercise of `new:48` would send it back still moving toward the obstacle. | Step 4 sets the linear and angular velocity to zero after `Teleport` (`SetLinearVelocity`, `SetAngularVelocity`), with the reason in one sentence; the solution of `new:48` does the same (about 40 words). | `allocation/make-a.md:1271-1272`, `:1845`; `StrataScriptCore/Include/StrataScript/Physics.h:61`, `:74`, `:117-132` |
| critic-make-a-12 | should | shape | `make/physics` (step 5), `make/project-coin-run` (step 5, `new:48`) | From `make/scripting-scene` step 4 on, `CoinPlacer` places the coins while the game plays and the five hand-placed instances are gone, so the edited scene holds no coin. Yet `make/physics` step 5 changes the coin prefab through an instance and Apply, `make/project-coin-run` step 5 tunes the coins' bob and spin in the Inspector, and `new:48` overrides a field on one gold coin. None has an instance to work on, and edits of the running copy are gone at Stop. | `make/physics` step 5 drags one coin prefab into the level, adds the collider and the body, applies, and deletes the instance (about 60 words); `make/project-coin-run` step 5 finds the values while playing, then sets them the same way; `new:48`'s coin is a sixth one placed by hand. | `allocation/make-a.md:1057-1058`, `:1130`, `:1273`, `:1812-1813`, `:1845`; `allocation/make-a.md:659` (`new:5`: no prefab edit mode); `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436-442` (Apply writes an instance back, edit mode only) |
| critic-make-a-13 | should | order | `make/project-coin-run` (steps 1, 2 and 5; `new:48`) | The round needs scripts that talk to each other, and block A never teaches it: `GetScript<T>` is `make/timers-events`', a page of block B on track G only. The HUD's timer (`CoinHud`, from `Time`) and the round's time left (a field of `CoinRunGame`, with a difficulty field) would disagree; "the ball stops" names no means; and `new:48`'s Basic exercise sums the coins' `Points` field in the HUD. | `CoinRunGame` takes over the timer's text and the time bar from `CoinHud`, so one script owns the round's time; the ball stops with `Time::SetTimeScale(0)` (taught on `make/script-loop`; a scene reload starts at 1), or with `RemoveScript("BallControl")` and its velocity set to zero; `new:48`'s Basic exercise counts a second tag (`BigCoin`, worth five) with `FindEntitiesByTag` (about 80 words). The other way is in forPlanner. | `allocation/make-a.md:1079`, `:1519-1520`, `:1806-1813`, `:1845`; `allocation/make-b1.md:89`, `:103-104`; `outline-1.md:77-81`, `:203`; `StrataScriptCore/Include/StrataScript/Entity.h:88`, `:93`; `StrataScriptCore/Include/StrataScript/Time.h:43-53`; `Strata/src/Strata/Scene/Scene.h:463`, `:924` |
| critic-make-a-19 | should | order | `make/scenes-entities`; `make/project-coin-run` (step 5) | Coin Run's camera is framed only on `make/project-coin-run`. Until then the Game view shows Basic 3D's camera, 6 m back and 2 m up, aimed at the centre with a vertical view of 60 degrees. The ground nearest the camera, from about z = 4 to the wall at z = 10, almost a third of the 20 m level, and that wall are out of view, so the ball and coins leave the screen on `make/input` to `make/hud`. | `make/scenes-entities` adds a step after the walls: the Main Camera set high and tilted down over the level (for example Translation (0, 16, 13), Rotation (-55, 0, 0)), checked with the Game camera chip (F8); `make/project-coin-run` step 5 then only adjusts it (about 120 words). | `allocation/make-a.md:221-223`, `:1812`; `StrataEditor/src/Editor/ProjectTemplates.cpp:31`, `:51-55`; `Strata/src/Strata/Scene/Components.h:133`; `StrataEditor/src/Panels/ViewportPanel.cpp:460-461` |
| critic-make-a-28 | could | thin-home | `make/export` (step 8), `make/project-coin-run` (step 7) | Step 8 names two assets that scripts load by path, the coin prefab and the coin sound. The bump of `make/sound` step 5, when its script finds the clip by path, and the complete sound of `make/project-coin-run` step 2 drop out of a pruned export the same way, and no page says how the reader finds what is missing: `Game.log` holds a warning "FindAsset (called by script ...): there is no asset at '<path>'" for each. | Step 8 lists every path that Coin Run's scripts find (or adds the folder `Sounds`, since Always Include takes folders) and reads that warning in its "If you do not see it"; `make/project-coin-run` step 7 adds `Complete.ogg` (about 50 words). | `allocation/make-a.md:1421-1423`, `:1707-1709`, `:1808-1809`, `:1815-1816`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:912-914`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:1546`, `:1555`; `StrataEditor/src/UI/SettingsPages.cpp:348-349` |
