# Brief: `make/scripting-scene`

| Field | Value |
| --- | --- |
| Title | Scripts and the scene: finding, spawning and changing entities |
| Kind | H |
| Size | L |
| Tracks | G, B |
| Needs | `make/script-loop` |
| From | scripting "The gameplay API, part 1": `Entity` (name, tag, activity, hierarchy, `Destroy`, components by name, properties), the `Component` proxy, `TransformComponent` (local and world position, rotation and scale), `Scene` (create, find, roots, camera, `Instantiate`; `InstantiateMany` is `make/performance`'s), `Assets` (find, request, release, progress); use home of asking for assets early (`Instantiate` never waits); Coin Run's coins placed by a script, and a collected coin hidden or destroyed |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/scripting-scene` — Scripts and the scene: finding, spawning and changing entities

**Covers.** The goal: the coins bob, a script places Coin Run's coins, and a coin the ball reaches is hidden or
destroyed. What must be true first: Coin Run at the end of `make/first-script` (the coins spin), `make/script-loop`
read (its example is the bob), and "The same ideas in code" of `make/transforms-units` read again. First a table of
the SDK's namespaces, each with the page that teaches it (`Entity`, the `Component` proxy, `TransformComponent`,
`Scene` and `Assets` here, the home of their use; `SubScene` on `make/levels-saves`; `Input` on `make/input`;
`Physics` and `RigidBody` on `make/physics`; `AudioSource` and `Audio` on `make/sound`; `UIElement` on `make/hud`;
`Time` on `make/script-loop` and `make/timers-events`; `Game` on `make/levels-saves`; the rest in block B); the facts of
every class are `reference/script-api`'s. The steps, each with its code from the tutorial's files and what to see.
(1) The bob, as `make/script-loop`'s example: the `Coin` script sets the coin's height from a sine of
`Time::GetElapsedTime()` in `OnUpdate`, built and played, so every instance of the prefab bobs. (2) An empty entity
`Coins` with a new script `CoinPlacer`. (3) Ask for the coin
prefab early: `Assets::Find("Prefabs/Coin.stprefab")` and `Assets::RequestLoad` in `OnCreate`; the page's rule in a
`:::rule` aside: request assets early, because `Instantiate` never waits and gives back an empty entity for what is not
loaded (no frame waits for the disk). (4) Place the coins once the prefab is loaded (`Assets::IsLoaded`, then
`Scene::Instantiate` with a position, as a parent of `Coins`), in a loop over a list of positions, so the five
hand-placed coins of `make/prefabs` can go; `Assets::GetLoadProgress` and `Release` named, with a gotcha line: the
requests are the scene's, not each script's, and do not add up, so one `Release` ends a request that two scripts
made. (5) Find entities: the
ball with `Scene::FindEntityByName("Ball")`, every coin with `Scene::FindEntitiesByTag("Coin")` (the tag of
`make/scenes-entities`); `IsValid`, and storing an `Entity` rather than anything that outlives a frame. (6) Read and
write a transform: local and world positions, rotation and scale through `TransformComponent`. (7) Components by name:
`HasComponent`, `GetProperty` and `SetProperty` with the Inspector's names (a coin's emission raised as it is
collected), and the `Component` proxy. (8) Collect a coin: when the ball comes near (a distance with `glm::distance`,
given as a recipe), first hide it with `SetActive(false)`, then destroy it with `Destroy()` (it goes at the end of the
frame); during Play the ball is dragged onto a coin with the gizmo, since moving it is `make/input`'s. (9) Entities in
the hierarchy: `GetParent`, `GetChildren`, `SetParent`, `Scene::GetRootEntities`, `Scene::CreateEntity` and the primary
camera with `Scene::GetPrimaryCamera`, each in a short step on the `Coins` group. `## Result`: coins that bob, placed by
a script and collected by the ball; it ends with the download of the page's end state. `## Variations`: destroying
every entity of a tag at once (the scene inventory's exercise); placing many copies in one call is
`make/performance`'s `InstantiateMany`; a prefab chosen in a field is `make/script-fields`'. The exercises
(`new:23`) are done in a script.

**Leaves out.**

- Asset fields and `Instantiate` by a handle in a field → `make/script-fields`
- `InstantiateMany` → `make/performance`
- Scripts that find and call each other (`GetScript<T>`) → `make/timers-events`
- Residency, pins and eviction inside → `assets/residency`
- Vectors, distances and directions as recipes → `make/gameplay-math`
- Triggers that replace the distance test → `make/physics`
- The SDK's classes as facts → `reference/script-api`
- How a host call crosses into the engine → `scripting/host-api`

**Fit.** `fits`: about 4,650 words against L (5,000). Nine steps, several with two or three calls, and four code
excerpts from the tutorial's files take most of it, with the namespace table, the rule, three Variations and two
exercises; a how-to keeps theory to two sentences a section.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:127` | feature | home | The SDK's namespaces, each sent to the page that teaches it |
| `gamedev:128` | feature | home | Components by their Inspector names: `GetProperty` and `SetProperty` |
| `gamedev:494` | rule | home | Request assets early; `Instantiate` never waits |
| `scene-ecs:598` | hands-on | home | Coins found by their tag and destroyed, as step 8 and a Variation |
| `scripting:118` | feature | home | The SDK's `Entity`, the use the steps teach: `IsValid`, name and tag, `SetActive`, `Destroy` at the end of the frame, the hierarchy (`GetParent`, `GetChildren`, `SetParent`), components by their Inspector names (`HasComponent`, `GetProperty`, `SetProperty`); the typed accessors and `GetScript<T>` named with the pages that use them; the facts are `reference/script-api`'s link |
| `scripting:119` | feature | home | The SDK's `Component` proxy: `GetComponent("<name>")` and its `Get` and `Set` by property name, in step 7 |
| `scripting:120` | feature | home | The SDK's `TransformComponent` in use: local and world position, rotation and scale read and written (step 6), as "The same ideas in code" of `make/transforms-units` showed them |
| `scripting:121` | feature | home | The SDK's `Scene` and `Assets` in use: `CreateEntity`, `FindEntityByName`, `FindEntitiesByTag`, `GetRootEntities`, `GetPrimaryCamera`, `Instantiate` with a position; `Assets::Find`, `RequestLoad`, `IsLoaded`, `GetLoadProgress` and `Release`. `SubScene` is named in the table with `make/levels-saves`, which loads one, and `InstantiateMany` with `make/performance` |
| `scripting:123` | feature | use | The SDK's `Time`: `Time::GetElapsedTime` in step 1's bob |
| `new:23` | hands-on | home | Exercises, done in a script: **Basic.** log the number of coins left (`Scene::FindEntitiesByTag("Coin").size()`) once a second, and predict the count after two coins are collected; **Medium.** switch the whole `Coins` group off from `CoinPlacer` with `SetActive(false)` five seconds after the start, predict whether the coins still bob (they do not: inactive entities get no updates), and switch it on again. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:123` (`FindEntitiesByTag`); `StrataScriptCore/Include/StrataScript/Entity.h:51` (`SetActive`); `StrataScriptCore/Include/StrataScript/Script.h:46` (inactive entities receive no updates) |
| `scripting:169` | feature | use | A script's asset requests; step 4's gotcha line: they belong to the scene and do not add up, so one `Assets::Release` ends a request that two scripts made. Evidence: `Strata/src/Strata/Scripting/ScriptSystem.h:131-132`; `StrataScriptCore/Include/StrataScript/Scene.h:44-46` (read at the pin) |
| `scripting:334` | concept | use | Asynchronous assets from game code, at the maker's level |
| `scripting:481` | rule | use | Request assets early; `Instantiate` never waits |
| `scene-ecs:92` | feature | use | Finding entities by name and by tag |
| `scene-ecs:514` | rule | use | Destruction during an update is deferred |
| `scene-ecs:516` | rule | use | Do not hold an entity's data across frames; hold the `Entity` and check it |
| `assets:67` | feature | use | Asking for an asset never blocks |
| `assets:537` | rule | use | Handle "not loaded yet" every frame |
| `assets:539` | rule | use | Hold handles across frames and request what you use |
| `gamedev:359` | code | use | The `Spinner`'s transform calls, read again from `make/transforms-units` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The lifecycle: `OnCreate`, `OnUpdate`, destruction at the end of the frame; the bob of its example | `make/script-loop` | must |
| The `Coin` script, building and attaching it, and the coins' spin | `make/first-script` | must |
| Variables, loops, functions, lists, classes, `std::optional` and template arguments | `basics/programming-3` | must |
| Positions, rotations, local and world, and the same ideas in code | `make/transforms-units` | must |
| Names, tags, activity and the hierarchy | `make/scenes-entities` | must |
| The coin prefab and instances | `make/prefabs` | must |
| Assets, handles and paths in the project | `make/assets` | must |
| A distance between two points | `basics/math-vectors` | helps |

**Starting state.** The end state of `make/first-script` (`startsFrom {"tutorial": "make/first-script"}`): Coin Run
lit for play with five hand-placed coin instances that spin; `make/script-loop` has no stage. The page's step 1 makes
the coins bob, step 4 removes the five, and its end state, downloaded from `## Result`, has bobbing coins placed by
`CoinPlacer` and the distance test that collects them.

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
| critic-make-a-3 | must | missing-item | `make/scripting-scene`; `make/physics` (step 2) | No page of block A teaches how a script reaches its own entity: `Script::GetEntity()`, with `GetTransform()` (the Spinner's) as its shortcut. Hiding or destroying the coin, and reading its tag, need it. `make/physics` step 2 writes `GetRigidBody().AddForce`, which does not compile in a script: `GetRigidBody` is a member of `Entity`, not of `Script`. The only row that names `GetEntity` is on `reference/script-api`. | `make/scripting-scene` names the two members of `Script` before step 5 and writes `GetEntity().SetActive(false)` and `GetEntity().Destroy()` in step 8 (about 60 words). `make/physics` step 2 writes `GetEntity().GetRigidBody().AddForce(...)`. | `allocation/make-a.md:1065-1067`, `:1098`, `:1268`; `allocation/reference.md:58`; `StrataScriptCore/Include/StrataScript/Script.h:100-101`; `StrataScriptCore/Include/StrataScript/Entity.h:51`, `:59`, `:76` |
| critic-make-a-4 | should | missing-item | `make/scripting-scene` (step 5) | `Scene::FindEntityByName` and `FindEntitiesByTag` also find inactive entities, and an entity destroyed this frame until the frame ends. So a coin hidden with `SetActive(false)` still counts among the coins left, which the HUD and `CoinRunGame` count by tag; and the hidden "You win" panel of `make/project-coin-run` can be found by its name. No page says so. | Step 5 adds two sentences: the finds see inactive entities and those destroyed this frame; a count of what is left skips them with `IsActive()`, or counts after destruction. `make/project-coin-run` step 2 finds its hidden panel that way (about 50 words). | `allocation/make-a.md:1060-1062`, `:1066`, `:1808`; `Strata/src/Strata/Scene/Scene.cpp:793-813`, `:847-866` (no test of activity); `StrataScriptCore/Include/StrataScript/Entity.h:38` |
| critic-make-a-5 | should | stale-item | `gamedev:128` and `scripting:118` on `make/scripting-scene` (step 7) | The page says scripts name components and properties "with the Inspector's names". They take the registered names, compared without regard to case: `MeshRenderer` and `CastShadows`, not the labels "Mesh Renderer" and "Cast Shadows"; some labels differ more (the sun's "Angular Diameter" is `ShadowSoftness`). The Inspector never shows the registered name, and a wrong name fails with a problem in the Console. | Step 7 says what the name is (mostly the label without its spaces), where to read it (`reference/components`, or the component menu's **Copy Values**, which puts the component's name and values on the clipboard as JSON), and what a wrong name does; the two rows say "registered names" (about 70 words). | `allocation/make-a.md:1063-1064`, `:1095`, `:1098`; `StrataScriptCore/Include/StrataScript/Entity.h:61`, `:67-68`; `Strata/src/Strata/Reflection/ComponentRegistry.cpp:166-174`; `Strata/src/Strata/Reflection/PropertyBuilder.cpp:9-17`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:647-651`; `StrataEditor/src/Panels/InspectorPanel.cpp:861-868`; `StrataEditor/src/UI/EditorActions.cpp:255-261`; `StrataTests/Architecture/ComponentSchema.json:480`, `:485` |
| critic-make-a-6 | should | missing-item | `make/scripting-scene` (step 7), `make/hud` (step 7) | `GetProperty` and `SetProperty` take their type from the value, and the SDK converts only `bool`, `int32_t`, `uint32_t`, `int64_t`, `float`, the glm vectors, `glm::quat`, `std::string`, `Entity` and `AssetHandle`. A `double` (the literal `0.5`, or arithmetic on `Time::GetElapsedTime()`, which returns `double`) or a bare text literal does not compile, with an error about an incomplete `ValueTraits`. A float property takes an integer; an integer property refuses a float at run time. | Step 7 states the rule with its fixes (`0.5f`, `std::string("...")`, or the type named: `SetProperty<float>(...)`); `make/hud` step 7 sets the bar from a `float` and says why (about 70 words). | `allocation/make-a.md:1063-1064`, `:1519-1521`; `StrataScriptCore/Include/StrataScript/Value.h:40-41` (the template only declared), `:44-229`; `StrataScriptCore/Include/StrataScript/Entity.h:67-72`, `:388-395`; `StrataScriptCore/Include/StrataScript/Time.h:28-33`; `Strata/src/Strata/Scripting/ScriptValue.cpp:153-171` |
| critic-make-a-12 | should | shape | `make/physics` (step 5), `make/project-coin-run` (step 5, `new:48`) | From `make/scripting-scene` step 4 on, `CoinPlacer` places the coins while the game plays and the five hand-placed instances are gone, so the edited scene holds no coin. Yet `make/physics` step 5 changes the coin prefab through an instance and Apply, `make/project-coin-run` step 5 tunes the coins' bob and spin in the Inspector, and `new:48` overrides a field on one gold coin. None has an instance to work on, and edits of the running copy are gone at Stop. | `make/physics` step 5 drags one coin prefab into the level, adds the collider and the body, applies, and deletes the instance (about 60 words); `make/project-coin-run` step 5 finds the values while playing, then sets them the same way; `new:48`'s coin is a sixth one placed by hand. | `allocation/make-a.md:1057-1058`, `:1130`, `:1273`, `:1812-1813`, `:1845`; `allocation/make-a.md:659` (`new:5`: no prefab edit mode); `StrataEditor/src/Editor/EditorPrefabCommands.cpp:436-442` (Apply writes an instance back, edit mode only) |
| critic-make-a-22 | could | missing-item | `make/scripting-scene` (step 3) | The page types `"Prefabs/Coin.stprefab"` for `Assets::Find` but never says how a reader gets such a path. The Content Browser's right-click **Copy Path** copies exactly the path the call takes: relative to the Assets folder, with `/`. | Step 3 adds one sentence with **Copy Path** and the path's form; `make/sound` step 4 uses it for the clip (about 40 words). | `allocation/make-a.md:1053-1054`; `StrataEditor/src/Panels/ContentBrowserPanel.cpp:1136-1137`; `StrataEditor/src/Editor/AssetBrowserView.h:30`; `StrataScriptCore/Include/StrataScript/Scene.h:18-19` |
| critic-make-a-25 | could | stale-item | `make/scripting-scene` (step 4) | Step 4 places the coins "with a position, as a parent of `Coins`": they become children of `Coins`. The call that takes both puts the parent last, after a rotation and a scale, and the position then counts from the parent. | Say "as children of `Coins`" and show the whole call, `Scene::Instantiate(coin, position, glm::quat(1.0f, 0.0f, 0.0f, 0.0f), glm::vec3(1.0f), coins)`, with one sentence that the position is relative to the parent (about 30 words). | `allocation/make-a.md:1057`; `StrataScriptCore/Include/StrataScript/Scene.h:162-166` |
