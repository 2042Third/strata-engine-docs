# Notes: world/tutorial-component

## New terms

None. The page homes no glossary term and defines no new one.

## Requests

- Extra words: `tooltip` and `tooltips` (the text a property shows when the pointer rests on its label; the engine's own word, and the code names it `WithTooltip`), and `capstone` (the name of the part that the page links to, `capstone/build`). Covering line for both: E1 has 5.
- External hosts: none new. The page links github.com (doctest's command line) and cites skypjack.github.io and gameprogrammingpatterns.com by name in Further reading, which are listed already.
- Figures: no figures file. The result picture is a Mermaid diagram. The editor step of the second section (Add Component, the Inspector clamping a negative radius) has no editor picture: the pin's editor has no wind zone, and a picture of the patched editor cannot be taken from the pin's build. Please decide whether it waits for a later pin.
- Names: `names` reports `Physics.WindZone`, the doctest suite that the page's patch adds, so it is not a suite at the pin. Leave it.
- Tutorial file: `tutorials/world/tutorial-component.tutorial.json` starts from the pin, names the patch `tutorials/world/tutorial-component.patch` and the suites `Physics.WindZone`, `Reflection`, `Scene.Serialization`, `Scene.Systems`, `Engine.Modules` and `Reflection.ComponentSchema`. The page is the first of the WindZone chain; the first run of `tutorials.py patch` is the integrator's. The patch was made with git against the pin and checked with `git apply --check` there; it was never built.
- Exercise 2 has a worked solution, `tutorials/world/tutorial-component/exercise-2.patch`, written to apply after the page's patch (the chain order of `tutorials.py patch`). Its download under `public/downloads/solutions/world/tutorial-component/` is for `tutorials.py compile`.
- The page has no checkpoints, because an engine-changing tutorial has none (card, kind T).

## Since

`since: 0.3.0`. The subject is older than the first tag: the physics module with its `Register<T>` registrations and its scene system exist since 0.3.0 (inventory `physics:70`, "0.3.0"), and the add-component checklist describes the same registration path.

## Not verified

- That the Console panel still holds the startup line `Engine modules: ...` when the editor window opens, and that its **Search** field finds it.
- How the Inspector shows a clamped value (whether it rounds 0.01), and whether typing a number into a drag field reaches the property's clamp before or after ImGui's own limit. The page says only that the stored value is the end of the range.
- That the schema snapshot that the helper `write-component-schema` writes is byte for byte the 57 lines the patch holds for `WindZone` (the entry was written by hand from `ComponentSchema.cpp` and the neighbouring entries).
- That every other test of the engine passes with the wind zone and its system; the page claims it for the final `ctest -LE gpu` run, and the patch was not built or run. The tests that name the six built-in systems or count components were searched for with grep in `StrataTests/`, and the five test cases of `SceneSystemTests.cpp` and four lines of `BuiltinModulesTests.cpp` that needed changes were recomputed with a copy of `ComputeUpdateOrder` (it reproduced the six-system lists of the pin before the wind system was added).
- The counts "2 test cases and 11 assertions" for `Physics.WindZone` come from counting the checks in the file, not from a run.
- That the feature scene's new entity `Gust` leaves the other tests that read `Feature.stscene` unchanged (the editor tests, `CookedSceneTests`, the GPU feature test).

## Findings not applied

- The brief says `BeforeIfPresent = { "Physics" }`. The page uses it, with `AfterIfPresent = { "Scripting" }` added, as the physics system does for scripts. Reason: the test `The built-in systems update in the order ...` asks that no built-in descriptor has a hard `After` or `Before`; without the `AfterIfPresent` the system would run first of all (`WindZone, UI, Scripting, ...`), which exercise 1 uses on purpose.
- The brief says the page's sections end with a checkpoint and a "You should now have" picture. The card says an engine-changing tutorial has none; each section ends with one sentence that says what the reader has.
- The brief asks for "You should see" as a text capture of build or test output. The card forbids captures of a patched build, so the page tells the output in words and quotes the key lines in backticks.
- The brief's "six quoted hunks": the page quotes ten blocks of the patch (data, registration, system header, system source, system registration, system test, reflection test, round trip test, one list of expected systems, the feature scene entry), because each stage of the checklist is one block. The schema snapshot's 57 lines are not quoted (63 lines with context, above the limit of 60).
- The brief's second step names the editor check (Add Component lists Wind Zone under Physics, the Inspector clamps a negative radius) with a picture; no picture is requested (see Requests).
- The brief says the test of the system also checks `CallsUpdate`; it does, in `The system takes part in fixed steps only`.
- The docs part of the engine checklist is one line (`Docs/Architecture.md`); the `Docs/DeveloperGuide.md` is not changed.

## Clerk

- `extra-words.txt`: tooltip, tooltips, capstone.
- Left for the planner: the editor picture of the patched build; `Physics.WindZone` in `names`.

## Names of this page

- `Physics.WindZone`: the doctest suite the page's own patch adds.

## Tutorial run

- 2026-11-24, `tutorials.py patch` at the pin 319075e3: the page's patch (already remade for the pin: the reflection list's context holds `RectLight` and `LightSurface`) and exercise 2 pass, with the 7 doctest suites and the feature test. Exercise 2's patch no longer applied (the same context line of `ReflectionTests.cpp`); it was remade in a scratch worktree after the page's patch, with the same change.
- The first round failed to link `WindZoneSystem`: the shared build folder reconfigured during the build (GLOB mismatch for the new files) and compiled the old file list; the second round passed unchanged.

## Walk E-final-9

Track walk E-final-9 (2026-11-24; `docs-work/walkfix-E9`, `integrate.py` and `integrate2.py`, the pin clone's
`build/docs-patch` in Release, clone clean afterwards). Run by the integrator, against the page's "You should see":

- Before the test edits (the patch without its `SceneSystemTests.cpp` and `BuiltinModulesTests.cpp` changes):
  `--test-suite=Scene.Systems,Engine.Modules` 19 test cases, 9 failed, failed checks in both files. After them: 19
  passed. `Physics.WindZone,Reflection,Scene.Serialization,Scene.Systems` 37 passed; `Physics.WindZone` alone 2 test
  cases, 11 assertions.
- Without the two `IsActiveInHierarchy` lines: the second test case fails at `REQUIRE( 2 == 1 )`, 4 assertions run.
- Without the feature scene entry: `StrataTests.FeatureTest` failed with the page's check and message.
- `write-component-schema`: 207 lines added, none removed. The `WindZone` entry is byte for byte the patch's 57 lines;
  the other 150 are `RectLight`'s, which the pin's snapshot lacks. The page now says so (see "## Engine").
- The feature test and `Architecture.Layering,Reflection.ComponentSchema` passed.
- Exercise 1 (no `AfterIfPresent`): the helper output reads `systems: WindZone UI Scripting Animation World Physics
  Audio`, as the answer says.
- Exercise 2, the rename alone: six test cases failed (two of `Reflection`, `Reflection.ComponentSchema`, one of
  `Engine.Modules`, two of `Scene.Serialization`, whose round trip test ended the run with `test case CRASHED:
  SIGABRT`), and the feature test failed in each test case that loads the feature scene and on `WindArea`. The old
  answer named five tests; the answer now names what fails. The worked solution's stamp stands (unchanged files).
- Exercise 3, `Turbulence` in the struct and the registration only: only `Reflection.ComponentSchema` and the feature
  test fail; `Scene.Serialization` passes, as the answer says.
- The whole build (126 s after the apply), then the built editor (`--no-gpu`): its log line `Engine modules: Input,
  Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI. Scene systems update in the order UI,
  Scripting, WindZone, Animation, World, Physics, Audio`; a `WindZone` added by `entity.create` holds 10, 5 and
  `Directional`; `component.set` refuses -3 and 5000 (`WindZone.Radius must be between 0.01 and 1000000, not -3`),
  which the Inspector clamps instead (not seen: no window).
- `ctest --test-dir build/docs-patch -C Release -LE "gpu|perf" -j 8`: 85 of 85 passed in 423 s. The page's Debug run
  was not made (no Debug build in `build/docs-patch`).

## Engine

- `StrataTests/Architecture/ComponentSchema.json` at 319075e3 lacks the entry of `RectLight` (150 lines): the snapshot
  was not written again when the rect light landed, and `Reflection.ComponentSchema` allows components it lacks, so
  nothing failed. A reader who writes the snapshot, as the page's step does, gets 207 added lines instead of 57; the
  page says so. For the engine's agents: write the snapshot again so that `RectLight`'s registration is checked too.
