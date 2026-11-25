# Brief: `engineering/feature-test`

| Field | Value |
| --- | --- |
| Title | The feature test |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `engineering/test-kinds`, `world/reflection`, `scripting/abi-sdk` |
| From | build-test ch. 9 "The feature test: coverage by construction" (the project, the coverage checks, the runners, extending it) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/feature-test` — The feature test

**Covers.** The job: one project that must exercise everything the engine registers, and the runners that play it;
it exists for golden rule 6, keep the feature test current. The problem: coverage by construction against line
coverage. Line coverage says which lines ran, not which features were checked; the registries make "every"
enumerable, so a check can demand each registered thing. The map: the coverage loop (the registries of components,
settings sections, host functions, SDK names, field types and asset types; the feature project that must exercise each;
the runners: headless in the test process, the in-process editor, the exported game, the real executables, the GPU).
The contract, what counts: every registered component on some entity, with every property non-default on some entity
and every reference resolving; every settings section non-default in `FeatureTest.stproj`; every script field type
overridden; every callback called (the journal); every host function called (the call counters); every public class,
function and macro of the SDK used, as `SDKReader` reads the headers; an asset of every type that imports without
warnings and leaves its `.meta` untouched; no warning or error the run does not expect. The toy: a coverage check over
a registry of two entries. The real code: the component check walking `ComponentRegistry` against a default-made
instance; the headless play (audio without a device, a window service without a window, saves in a folder of the test,
interpolation on, every host function's call count checked after the scenario); the SDK coverage check; the script
side, `FeatureScript` with `Expect`, `Checks`, `Failure` and `Completed`, and `Journal()`. The runners:
`StrataTests.FeatureTest` (headless, then in the in-process editor and as an exported game in `GameRuntime`, 200 frames
with a hot reload halfway and the scene's caches checked every frame), `GPU.FeatureTest`, `StrataEditor.FeatureTest`
and `StrataRuntime.FeatureTest` on a copy, `StrataRuntime.FeatureTestQuality`, `StrataEditor.InputSequence`. Extending
it: what to add for a component, a property, a settings section, a host function, a callback, a field type and an
asset type, and the tiny binary assets from `StrataTests/FeatureTest/Tools/GenerateAssets.py`, whose outputs are
committed (the Developer Guide writes `Tools/GenerateAssets.py`). The rule, in one box with the scripting side (every
new host function, SDK name, callback and field type is exercised by the feature test): a feature without its entry
cannot land. Exercises: add a component and watch the feature test fail until the feature scene holds it with
non-default values; trace it yourself: follow `Time::SetTimeScale` by a search from the SDK through its host table
entry to the feature script that calls it and the check that fails when no script does. At
the end the reader can say what the feature test demands of a new feature and extend the project so that it passes.

**Leaves out.**

- Reflection and the component registry → `world/reflection`
- The host API and its call counters → `scripting/host-api`
- The feature test's minimum for a new component → `world/tutorial-component`
- A new host function's feature script → `scripting/tutorial-host-function`
- The engine's test modules built to fail at load → `scripting/loading`
- Regression tests of a game from command scripts → `make/automated-playtests`
- The feature test in a whole change → `capstone/land`
- The test program's shards and CTests → `engineering/test-program`
- The committed generators as a workflow → `engineering/generated-code`

**Fit.** `fits`: about 3,860 words against M (3,000). One concept, four excerpts, the contract's eight checks, the
runners and the guide to extending it take the most; the page is 140 words below M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:356`, `scripting:345` | concept | home | Coverage by construction, one entry with testing the script API: a project that must hold every registered thing with non-default values; the feature test's coverage of host functions, SDK names and callbacks, and the call counters; the mistake of adding a component or host function without extending it. The test modules built to fail are `scripting/loading`'s, and regression tests of a game from command scripts `make/automated-playtests`' |
| `build-test:155-158` | feature | home | The feature project; the coverage checks; the runners; the script side |
| `assets:218` | feature | home | The check that fails when a registered asset type has no asset in the project |
| `build-test:407` | code | home | `StrataTests/src/FeatureTest/FeatureTests.cpp:152-196`: coverage by walking the component registry against a default-made instance |
| `new:11` | code | home | `StrataTests/src/FeatureTest/FeatureTests.cpp:229-281`: the headless play and the check that every host function was called |
| `new:12` | code | home | `StrataTests/src/FeatureTest/SDKCoverageTests.cpp:381-404`: every class, function and macro of the SDK used by the feature scripts |
| `new:13` | code | home | `StrataTests/FeatureTest/Scripts/FeatureScript.h:77-90`: the script side's check channel |
| `build-test:451` | figure | home | The coverage loop: registries, the project, the runners |
| `build-test:532`, `scripting:496` | rule | home | One rule box: keep the feature test current; every new host function, SDK name, callback and field type is exercised by it; it fails on what goes unexercised, so a feature without its entry cannot land |
| `build-test:584` | hands-on | home | Add a component; watch the feature test fail on the missing entity and property; extend `Feature.stscene` |
| `new:34` | hands-on | home | Trace it yourself, by a search: `Time::SetTimeScale` from the SDK's header through its entry of the host table to the feature script that calls it, and the check after the headless play that names a host function no script called (about 150 words). Evidence: `StrataScriptCore/Include/StrataScript/Time.h:49-52`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:328`; `StrataTests/FeatureTest/Scripts/TimeFeatures.cpp:40`, `:42`; `StrataTests/src/FeatureTest/FeatureTests.cpp:270-275` |
| `build-test:680`, `scripting:583` | term | home | Feature test, one entry |
| `build-test:681` | term | home | Journal (feature test), one of the qualified entries of "journal" |
| `build-test:758` | open | home | The generator's path, which `new:14` corrects |
| `scripting:691` | open | home | The runner and the SDK reader (`FeatureTestUtils.cpp`, `SDKReader.cpp`), which this page reads for its runner and SDK sections |
| `new:14` | erratum | home | `Docs/DeveloperGuide.md:828` names `Tools/GenerateAssets.py`; the file is `StrataTests/FeatureTest/Tools/GenerateAssets.py`, and `Tools/` holds no such file. The page writes the full path. Evidence: `StrataTests/FeatureTest/Tools/GenerateAssets.py`; `git ls-tree --name-only 822a7a46 Tools/` lists no `GenerateAssets.py` |
| `build-test:236` | feature | link | The generator of the project's tiny assets, in `engineering/generated-code`'s table |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The component registry and its properties | `world/reflection` | must |
| The script ABI, the host table and the SDK | `scripting/abi-sdk` | must |
| The end-to-end suites and CTest's fixture chains | `engineering/test-kinds` | must |
| Settings sections | `world/projects-settings` | helps |
| The host API's call counters | `scripting/host-api` | helps |
| Hot reload | `scripting/hot-reload` | helps |
| Asset types and `.meta` files | `assets/handles-meta` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `feature-test` | Feature test | - |
| `journal-feature-test` | Journal (feature test) | - |
