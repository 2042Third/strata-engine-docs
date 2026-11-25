# Brief: `capstone/land`

| Field | Value |
| --- | --- |
| Title | Capstone III: tests, the feature test, a budget, the review and CI |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `capstone/build`, `engineering/feature-test`, `engineering/perf-lab`, `engineering/ci` |
| From | new; the change made ready to land: unit tests, the feature test, a perf budget, the review checklist and a `ci/<name>` branch |
| Unit | `plan/allocation/capstone.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `capstone/land` — Capstone III: tests, the feature test, a budget, the review and CI

**Covers.** What the reader makes: the WindZone change made ready to land the way every change of Strata lands, and
then landed as commits. Each step section ends with a checkpoint of the patch and the test or tool output as a text
capture. The sections, in teaching order:

1. Unit tests, in a suite named after the module (`Physics.WindZone`, which the Systems shard runs; `Testing.Shards`
   fails a suite no shard runs): the force function's cases (each mode, the centre, outside the radius, Strength 0, a
   degenerate transform); the system in a real scene stepped in fixed steps, never frames: a box in a zone gains the
   speed a force gives in one step (dv = F / m * dt, as the force test of `Physics.Simulation` checks it), a static body
   and a box outside are not pushed, a sleeping box wakes, Simulate mode pushes too; a twin run with and without three
   workers gives the same poses; the gizmo's lines, read without a GPU as the character controller's gizmo test reads
   them; the inactive reason in each mode; the host function in `Scripting.API` and the API module's check of an older
   engine; `wind.sample` while editing, a refused position that changes nothing, and its kind in the kind lists. Tests
   that need Physics live in the files a build without the module leaves out (`src/Physics/` and the others listed in
   `STRATA_TESTS_OF_PHYSICS`) or behind `#if ST_WITH_PHYSICS`. Each new test is seen failing without the line it guards,
   then passing with it.
2. The feature test: `Feature.stscene` holds a zone of each mode with every property away from its default; the
   feature script that only called `Wind::GetForceAt` now expects a body pushed along the axis; `wind.sample` joins the
   editor's feature command script with an `expect`; the component schema snapshot is written again if the
   registration changed (`Reflection.ComponentSchema`); `ctest -L feature` passes.
3. A perf metric: a `Perf.Physics` test of bodies inside zones, built like the test of 1,000 character controllers: the
   median of the scene's fixed step and the wind system's part of it, in a Release build without the validation layer.
   Its `Budgets.json` entry: on any machine but the reference machine the metric is `Provisional`, measured and
   recorded, never checked; on the reference machine it gets Measured and a budget of at most 1.5 times that, and
   `Tools/PerfStability.py --runs 5` runs before it merges; budgets only go down.
4. The documents: the Developer Guide's physics section names the component and its system; `AGENTS.md` changes only if
   a rule changes, and `Docs.AgentGuide` keeps it under its limit.
5. The review: the full run of `ctest --preset <platform>-debug` stays the change's check, since it runs every suite,
   not only those the patch names: `CLI.McpToolsets` among them, which fails for a command in no toolset of the table
   and passes for `wind.sample` because `editor/tutorial-command` gave the `wind.` group its toolset; the six items of
   the pre-commit checklist walked over `git diff --staged`; `Tools/CompatLint.py --changed-since main`; the staged
   patch verified in a clean worktree in Debug and Release; the change split into commits, one logical change each, the
   perf commit's message stating the measured values.
6. CI: the branch `ci/windzone` pushed to the reader's fork, since CI runs on pushes to `ci/**`; the matrix on Windows,
   Linux and macOS with warnings as errors, including the Linux job without Audio, Physics and GLFW, which proves that
   nothing outside the Physics module names the WindZone; a failure read from its annotations with `Tools/CIStatus.py`;
   green before main.

Exercises: read a CI failure from its annotations only; say, by the ratchet's rule, what a later commit that makes the
wind cheaper must change in `Budgets.json`, and why the reader's own machine cannot set the numbers. At the end the reader has walked one feature from its design to a green CI run, and can land a change in
Strata the way its own changes land.

**Leaves out.**

- How the test program, its shards and labels work → `engineering/test-program`
- What the feature test counts and how its runners run → `engineering/feature-test`
- Noise, percentiles, confirmed checks and the canary → `engineering/perf-lab`
- The CI matrix, its caches and the Dist job → `engineering/ci`
- The checklist's reasons, clean worktrees and commit hygiene → `engineering/contributing`
- Packaging and releases → `engineering/releasing`
- The change itself → `capstone/build`

**Fit.** `fits`: about 4,800 words against L (5,000). Six step sections of two to six short steps (twenty-four), each
with its test output as a text capture, five quoted excerpts, one figure and two exercises, at the guide's lower values
for E1; the unit tests of section 1 take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:20` | code | home | `StrataTests/src/Physics/PhysicsSimulationTests.cpp:223-250`: a force acts over one step, dv = F / m * dt: the pattern of the system's test |
| `new:21` | code | home | `StrataTests/src/Renderer/DebugDrawTests.cpp:252-284`: a gizmo's lines read back without a GPU, the pattern of the WindZone's gizmo test |
| `new:22` | code | home | `StrataTests/src/Perf/PhysicsPerfTests.cpp:478-515`: the median of a scene's fixed step under a confirmed check, the pattern of the WindZone's perf test |
| `new:23` | code | home | `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp:54-59`: every command must map to a toolset the table names, which the full run checks, `wind.sample` too through the `wind.` prefix of `editor/tutorial-command` |
| `new:24` | code | home | `StrataTests/Editor/FeatureCommands.json.in:1-7`: the editor's feature command script with its `expect` steps, which `wind.sample` joins |
| `new:25` | figure | home | The way a change lands: tests, the feature test, the perf metric, the documents, the review, a clean worktree, a `ci/<name>` branch, then main. Evidence: `AGENTS.md:78-81`; `AGENTS.md:457-474` |
| `build-test:113`, `build-test:114` | feature | use | The shards and `Testing.Shards`, which the new suite must satisfy |
| `build-test:396` | code | use | `CoreShards.json`: the Systems shard runs `Physics*` |
| `build-test:508` | rule | use | Every test case in a suite, every new suite prefix in a shard |
| `build-test:107` | feature | use | Module-dependent test files: a build without Physics leaves the WindZone's tests out |
| `build-test:491` | rule | use | `ST_WITH_*` are definitions; `#if ST_WITH_PHYSICS` only in tests and the composition root |
| `build-test:520` | rule | use | A new test fails without its fix |
| `scene-ecs:541` | rule | use | Tests count game time in fixed steps, never frames |
| `physics:149` | feature | use | Determinism with any number of threads |
| `physics:323` | code | use | The twin runs, the pattern of the wind's determinism test |
| `scripting:345` | concept | use | Testing game code and the API |
| `scripting:146` | feature | use | The API test module, which checks an older engine |
| `scripting:173` | feature | use | Host call counts, which the feature test reads |
| `editor-core:60` | feature | use | Command kinds as a tested decision |
| `automation:238` | feature | use | `CLI.McpToolsets`, which the full run runs and which finds `wind.sample` in a toolset |
| `build-test:155-158` | feature | use | The feature project, its coverage checks, its runners and the script side |
| `build-test:356` | concept | use | Coverage by construction |
| `build-test:532` | rule | use | Keep the feature test current |
| `build-test:584` | hands-on | use | A component that satisfies the feature test, carried from the minimum to behaviour checks |
| `build-test:135`, `build-test:137`, `build-test:138` | feature | use | The perf suites, the budget file and confirmed checks |
| `build-test:146-149` | feature | use | The perf suites by area, the ratchet, `Tools/PerfStability.py` and `Tools/PerfLock.py` |
| `build-test:404` | code | use | The format of `Budgets.json`, provisional entries included |
| `build-test:523`, `build-test:525`, `build-test:527` | rule | use | Budgets only go down; a busy machine proves nothing; numbers only from optimized builds |
| `build-test:578` | hands-on | use | Adding a perf metric, done here for the wind |
| `physics:173` | feature | use | The `Perf.Physics` tests the new metric joins |
| `build-test:186` | feature | use | `Docs.AgentGuide`, which checks `AGENTS.md` |
| `build-test:246-248` | feature | use | The golden rules, the pre-commit checklist and verifying in a clean worktree |
| `build-test:369` | concept | use | Process discipline: review, commit hygiene, clean-worktree verification |
| `build-test:543` | rule | use | Verify exactly what is staged, in Debug and Release |
| `build-test:566` | hands-on | use | `Tools/CompatLint.py --changed-since main` on the change |
| `build-test:192`, `build-test:193`, `build-test:199`, `build-test:201` | feature | use | CI's triggers, its matrix, failure annotations and `Tools/CIStatus.py` |
| `build-test:408` | code | use | `ci.yml`: the jobs and the test step the branch runs |
| `build-test:483`, `build-test:500`, `build-test:539` | rule | use | Warnings as errors in CI; `ci/<name>` before main; annotations carry the failures |
| `build-test:591` | hands-on | use | The exercise: a CI failure read from annotations only |
| `new:28` | hands-on | home | Exercise (design): what a later commit that makes the wind cheaper must change in `Budgets.json` by the ratchet's rule (measure again, lower Measured and Budget in the same commit, state the values in its message), and why the reader's own machine cannot set the numbers (only the reference machine measures; elsewhere the metric stays `Provisional`). Evidence: `StrataTests/Perf/Budgets.json:16-25`; `AGENTS.md:109-112` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The WindZone change | `capstone/build` | must |
| Test kinds, regression tests that fail without their fix | `engineering/testing` | must |
| Suites, shards, labels and `Testing.Shards` | `engineering/test-program` | must |
| Optional modules (`ST_WITH_*`) | `core/layers-registries` | must |
| The test files a build without a module leaves out | `engineering/test-program` | must |
| The feature test's coverage and runners | `engineering/feature-test` | must |
| Perf tests, budgets, provisional metrics and the reference machine | `engineering/perf-lab` | must |
| CI, its triggers, matrix and annotations | `engineering/ci` | must |
| The review checklist, clean worktrees and commit hygiene | `engineering/contributing` | must |
| Determinism with threads; twin runs | `physics/world-step` | must |
| Game time counts fixed steps, never frames | `core/time` | must |
| The API test module and older engines | `scripting/tutorial-host-function` | must |
| A command's kind lists and its unit test | `editor/tutorial-command` | must |
| Gizmo lines read from `DebugDraw` | `gpu/debug-drawing` | must |
| Medians and percentiles | `core/profiling` | helps |
| The MCP toolsets | `automation/mcp` | helps |
| CompatLint and the three compilers | `engineering/flags-portability` | helps |
| git: branches, commits and pushing | `basics/git` | must |

**Starting state.** The end state of `capstone/build`: the chain's patches and the WindZone change applied, built in
Debug and in Release (the perf step needs Release). The repository is the reader's own clone with a fork to push to,
for the CI section. No editor project is needed.

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
| critic-capstone-2 | must | missing-item | `capstone/build` (section 2) and `capstone/land` (section 2) | When the forces arrive, the WindZone that `world/tutorial-component` put into `Feature.stscene` starts to push bodies in every run of the feature test, and `capstone/land` adds a zone of each mode. The scene has seven active dynamic bodies. Their feature scripts, and the editor's command script, expect exact motion: the Ball's X between -4.05 and -3.95 after 150 steps, and each body at rest where it fell. An active Directional zone pushes every one of them, so the feature test fails. The patch runner runs that test after `capstone/build`'s patch. Neither page says where the zones stand. | Section 2 of `capstone/build` gets a step: the feature scene's zone must push no probe. A Spherical zone stands where its Radius reaches none of the seven bodies; a Directional one sits on an inactive entity. Then the feature test runs (about 60 words). Section 2 of `capstone/land`: the Directional zone sits on an inactive entity, as the "Moon" light holds alternate values. The behaviour check uses a body of its own inside the Spherical zone, away from the seven probes, and the feature script expects that body pushed away from the centre, not along an axis (about 70 words). | `allocation/capstone.md:201-202`, `:333-336`; `allocation/world.md:963-964`; `pipelines.md:1058-1059`; `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene:727`, `:802`, `:892`, `:1196`, `:1257`, `:1318`, `:1899` (the seven dynamic bodies, each with a feature script); `StrataTests/Editor/FeatureCommands.json.in:22-29`; `StrataTests/FeatureTest/Scripts/PhysicsFeatures.cpp:42-52`; `Docs/DeveloperGuide.md:833-838` (200 frames, three runs); `.claude/skills/strata-add-component/SKILL.md:107-109` |
| critic-capstone-3 | must | stale-item | `capstone/plan` (section 2) and `capstone/land` (section 6) | `capstone/plan` says that nothing outside the Physics module may name the WindZone. `capstone/land` says that CI's Linux job without Audio, Physics and GLFW proves it. At the pin the editor can only be configured with every module (CMake stops otherwise), that job also sets `-DSTRATA_BUILD_EDITOR=OFF`, and the editor's tests are left out without the editor. So the `wind.*` commands, which name the component, and `wind.sample`, which calls the Physics function directly, are allowed, and that job never builds them. The rule as written contradicts the capstone's own command. | `capstone/plan` section 2 states the rule exactly: nothing that a build without Physics compiles names the WindZone (the other layers, the runtime, the tests outside `STRATA_TESTS_OF_PHYSICS`); `#if ST_WITH_PHYSICS` stays where `AGENTS.md` allows it; the editor may name it, because it is built only with every module (about 50 words). `capstone/land` section 6 says what the job proves: the Scene layer's service, the host function and the guarded tests compile without the module, and the other jobs build the editor's commands (about 40 words). | `allocation/capstone.md:22-25`, `:203-205`, `:350-352`; `CMakeLists.txt:36-47`; `.github/workflows/ci.yml:52-60`; `StrataTests/CMakeLists.txt:65-70`, `:76-77` |
| critic-capstone-4 | should | stale-item | `capstone/land` (section 5), row `build-test:566` | The step runs `Tools/CompatLint.py --changed-since main` as if every reader could. The tool reads the Debug compile commands of a built Ninja Multi-Config tree of the `linux` or `macos` preset, and it needs GCC 14 and LLVM 16 (Homebrew's paths by default). Without them it exits 2, so on Windows the step fails. And `--changed-since` compares the working tree with the ref: in a clone at the pin, `main` is upstream's main, which is past the pin, so the tool also compiles files the change never touched. | The step becomes OS tabs. On Linux and macOS: `--changed-since` the commit the chain starts from (the pin, `822a7a46`), with a configured and built `linux` or `macos` Debug tree. On Windows: the page says the tool does not run there, and the `ci/windzone` run is the check (about 60 words). The `use` row says the same. | `allocation/capstone.md:347`, `:411`; `allocation/engineering.md:313`; `Tools/CompatLint.py:5`, `:15-20`, `:43-46`, `:109-120` |
| critic-capstone-5 | should | missing-item | `capstone/land` (Starting state, section 6) | The page pushes `ci/windzone` to the reader's fork and reads the run with `Tools/CIStatus.py`. The tool reads the runs of origin's GitHub repository. In a clone of the engine's repository with the fork added as a second remote, it asks upstream, which has no such run, and `status` keeps exiting 3 ("no run started yet"). No page says that origin must be the fork. The page also does not say what "green before main" means for a reader whose fork's main is past the pin. | Starting state: the clone's origin is the reader's fork, with GitHub Actions on (clone the fork, or point origin at it), because `CIStatus.py` reads origin's runs (about 40 words). Section 6 ends with what landing means here: the green run of `ci/windzone` ends the tutorial; merging into the fork's main is the reader's choice, since that main is past the pin (about 30 words). | `allocation/capstone.md:350-353`, `:441-443`; `allocation/engineering.md:1056-1057`, `:1275-1278`; `Tools/CIStatus.py:8-13`, `:27-34`; `.github/workflows/ci.yml:3-6` |
| critic-capstone-6 | should | thin-home | `capstone/land` (section 4) and `capstone/plan` (section 6, the spec's docs) | The documents step names only the Developer Guide's physics section and `AGENTS.md`, which is what the skill `strata-add-component` asks for a component. But the WindZone change also adds script API and a command. At the pin the engine documents such a change in more places, and its own spec lists them under "Docs, skills and release notes": the Guide's "Gameplay API" with its host function order (each appended group named), `Docs/Manual/Scripting.md` for game makers, the API overview of the skill `strata-scripting`, and a line in the running wave's release notes. | Section 4 of `capstone/land` lists these places and what each gets: the component and its system in "Physics"; `Wind::GetStrength` and `Wind::GetForceAt` in "Gameplay API" and in the host function order; a paragraph in the Manual's scripting page; the two functions in the skill's overview; one line in the draft release notes (about 90 words). The docs section of the spec on `capstone/plan` names the same list (one sentence). | `allocation/capstone.md:45-47`, `:342-343`; `Docs/Plans/Wave8/specs/physics-timing.md:944`, `:955-956`, `:973`, `:975`; `Docs/DeveloperGuide.md:1867`, `:1950-1955`; `.claude/skills/strata-scripting/SKILL.md:140-146`; `Docs/Manual/Scripting.md:172`; `Docs/Plans/Wave8/ReleaseNotes.md:114`; `.claude/skills/strata-add-component/SKILL.md:117-120` |
| critic-capstone-8 | should | missing-item | `capstone/plan` (section 5), `capstone/build` (sections 1 and 2) | The decisions never say whether the zone entity's scale scales Radius, nor which collision layers a zone pushes. At the pin collider gizmos follow the entity's scale (a sphere's radius by the largest axis), a gizmo function gets the world matrix, and `OverlapSphere` takes a layer mask. The chain's sphere gizmo, the force function, the overlap query and `wind.sample` must follow one rule, or a scaled zone draws a sphere that is not where it pushes. | `capstone/plan` section 5 adds two decisions with their costs: whether Radius is scaled by the world transform (one rule for the gizmo, the force, the query and the command), and the layers a zone pushes (every layer, or a mask property) (about 70 words). `capstone/build` applies the scale rule in section 1 and the mask in section 2 (one clause each), and `capstone/land` section 1 adds a scaled zone to the force function's cases. | `allocation/capstone.md:38-44`, `:176-187`; `allocation/gpu.md:1121`; `Strata/src/Strata/Renderer/SceneGizmos.h:61-63`; `Strata/src/Strata/Reflection/ComponentGizmo.h:41-43`; `Strata/src/Strata/Scene/SceneServices.h:172-173`, `:187` |
| critic-capstone-9 | should | missing-item | `capstone/land` (section 5) | The page splits the change into commits, one logical change each, after section 1 wrote the tests of the whole change. It does not say that each commit ships with its own tests and passes on its own. Golden rule 2 wants tests with new behaviour and all tests passing before a commit, and the feature test fails at any commit that adds a host function, an SDK function or a property without its feature-script call or its scene value. A reader who puts the tests in a last commit makes every earlier commit fail. | Section 5 names the split, each commit with what it needs to pass: the spec; the forces with their unit tests; the arrow kind with the gizmo test; the inactive reason with its test; the host function and the SDK with the API module, the `Scripting.API` case and the feature script; the command with `Editor.WindCommands`, the kind lists and the feature command step; the perf test with its provisional entry; each document with the part it describes. Each commit is verified as staged in the clean worktree (about 90 words). | `allocation/capstone.md:322-332`, `:347-349`; `AGENTS.md:23-24`, `:472-473`; `Docs/DeveloperGuide.md:853-866` |
| critic-capstone-11 | could | duplicate | `capstone/land` (exercises, row `build-test:591`) | The first exercise, reading a CI failure from its annotations only, is the exercise that `engineering/ci` homes (`build-test:591`), and `engineering/contributing`'s exercise ends the same way (a `ci/<name>` push read with `CIStatus.py`). Both pages are in the page's Needs closure, so the track E reader does it a third time, from the same angle. style.md asks a tutorial for open "make it yours" extensions. | Replace it with an extension: land the Falloff of `capstone/build`'s exercise the way the page landed the WindZone (its unit test seen failing first, a value off its default in `Feature.stscene`, the schema snapshot written again because the registration changed, its own commit, a green `ci/<name>` run); the solution is a patch. The row of `build-test:591` becomes `link` (about the same words). | `allocation/capstone.md:355`, `:415`; `allocation/engineering.md:1094`, `:1252`; `style.md:529-530` |
| critic-capstone-13 | could | missing-item | `capstone/land` (section 1) | The engine's checklist for a component asks for an editor test: `component.add` with values and `component.set` through `EditorCommandRegistry`, with undo restoring the state, and the commands refuse a value outside a property's range with nothing changed. No page of the chain writes this test for the WindZone: `world/tutorial-component` tests reflection, the round trip and the system, and section 1 has no such case. | Section 1 adds one editor test case: a WindZone added with values; Radius set out of range is refused as `InvalidParameters` with nothing changed; undo restores the state (about 50 words). | `allocation/capstone.md:322-332`; `allocation/world.md:959-962`; `.claude/skills/strata-add-component/SKILL.md:104-105`; `Docs/DeveloperGuide.md:3458-3461` |
| critic-capstone-14 | could | thin-home | `capstone/land` (section 3) | The metric is "the median of the scene's fixed step and the wind system's part of it", but no row says how the wind system's part is measured. The pattern reads `PhysicsStats::LastStepTime`, which times the Physics system's step alone. Also, every metric a test checks or records needs its own `Budgets.json` entry, or the test fails, so two metrics need two provisional entries. | Section 3 names the measure: a time the wind system keeps for its fixed update, read through `GetSystem<WindZoneSystem>`, beside the scene update's median. It also says that each metric gets its own provisional entry (about 50 words). | `allocation/capstone.md:337-341`; `StrataTests/src/Perf/PhysicsPerfTests.cpp:478-515`, `:526-553`; `StrataTests/Perf/Budgets.json:4-6` |
