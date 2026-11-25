# Walk E-final-9: track E (engine builder, persona E1), segment 9

Entries walked: `world/serialization`, `world/prefabs`, `world/sub-scenes`, `world/projects-settings`, `world/tutorial-component`.
Package: Strata 0.8.0 Windows x64 (official package from `docs-package-0.8.0`: StrataEditor, StrataCLI; every engine program run under the perf lock, headless `--no-gpu` editor sessions, no editor left running).
Book: the built site at 127.0.0.1:4329; engine source in a scratch worktree of docs-pin at 319075e3 (removed at the end).
Work folder: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-9/` (page texts and HTML, `sk2/` the extracted sketches, `proj/` the sample copies, `run1.ps1`, `run3.ps1`, `run4.ps1` and their `run*-out/` answers).

How the walk went: every page read in full. Every engine quote (30 excerpts with file and line range) compared with the file at 319075e3: all equal (the eight blocks of the tutorial are patch hunks with context and match the patch). All 10 sketches extracted from the pages, compiled with g++ 15 `-std=c++20 -Wall -Wextra` (the three "pseudo-sketches" of prefabs, projects-settings and sub-scenes compile as given): no warnings, every printed output equals the page's output, and the line numbers of the notes match the shown code. The numbers of the pages checked against the package: Loading.stscene 3,984 bytes, 9 lines, 7 entities; Tetris Main.stscene 1,154 lines and 18,210 bytes; MaxBodyPairs in Loading; the cycle warning text; the sub-scene fields; the FixedRate caps 16 and 32; the project version message. The tutorial's patch (download `tutorials/world/tutorial-component.patch`) applies to a clean 319075e3 with `git apply` and equals the page's counts (11 changed files, 3 new, header 42 lines, test file 58 lines, schema +57 lines, 11 checks in Physics.WindZone); the exercise-2 patch applies on top of it.

Run through the editor (StrataCLI, a project copy under git for each): Serialization Basic and Medium (cycle), Prefabs Basic, the sub-scene tab, Projects and settings (set, refused values, the cap, a future version, a kept unknown member).

Not walked: the build and test steps of the tutorial (the integrator does them, see below); every click path and Inspector picture (no screen: the Wind Zone menu entry, the Inspector tooltip, the Project Settings page, the Inspector's "120 steps/s (project)" line, the Console search for "Engine modules" with the WindZone order); the Hard exercise of Serialization (read, compiled and run as the sketch, not changed); the doctest and ctest commands of "How it is tested" on all five pages (they need a build); the sub-scene tests Basic of the sub-scenes page (a test to write in the engine tree, only read); Linux and macOS.

## Built by the integrator

Patch file: `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-9/world-tutorial-component.patch` (692 lines: the tutorial's whole change as `git diff` of the scratch worktree with the three new files added intent-to-add; the same as the page's download). Apply it to a clean checkout of 319075e3 with `git apply`. The page's steps, in order:
1. After the struct only (hunk 1): `cmake --build build/<preset> --config Debug --parallel` (no error line; every file that includes the physics header compiles again).
2. After the registration (hunk 2): build again; start the editor, create a project from the Basic 3D template, add the Wind Zone component, check the three values 10, 5, Directional and the tooltip; type -3 into Radius and 5000 into Strength (stored 0.01 and 1000).
3. After the system (hunks 3 to 6): `cmake --preset <preset>` (new source files), then build; start the editor, Console search "Engine modules", Info checked: the line must end `Scene systems update in the order UI, Scripting, WindZone, Animation, World, Physics, Audio` (the unchanged package prints `UI, Scripting, Animation, World, Physics, Audio`).
4. Before the test edits: `build/<preset>/bin/Debug/StrataTests --test-suite=Scene.Systems,Engine.Modules` must fail with failed checks in SceneSystemTests.cpp and BuiltinModulesTests.cpp; after the edits it must pass.
5. After adding WindZoneTests.cpp, the reflection test and the round trip test: `cmake --preset <preset>`, `cmake --build build/<preset> --config Debug --target StrataTests --parallel`, then `build/<preset>/bin/Debug/StrataTests --test-suite=Physics.WindZone,Reflection,Scene.Serialization,Scene.Systems` (no failed test case) and `--test-suite=Physics.WindZone` alone (2 test cases, 11 assertions).
6. Break it: delete the two `IsActiveInHierarchy` lines in WindZoneSystem.cpp, build the test target, run `--test-suite=Physics.WindZone` (the second test case fails, list holds two zones); restore and run again.
7. Feature test before the scene entry: `ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"` must fail with "Component WindZone: the feature scene ... must contain it" (apply the patch without its Feature.stscene hunk to see this); after the entry it must pass.
8. `build/<preset>/bin/Debug/StrataTests --strata-test-helper=write-component-schema StrataTests/Architecture/ComponentSchema.json` then `git diff --stat StrataTests/Architecture/ComponentSchema.json` (one file, 57 lines added, none removed).
9. `ctest --preset <preset>-debug -R "^StrataTests\.FeatureTest$"` and `build/<preset>/bin/Debug/StrataTests --test-suite=Architecture.Layering,Reflection.ComponentSchema` (both pass).
10. `ctest --preset <preset>-debug -j 8 -LE gpu` (all passed).
11. Basic exercise: remove `windDescriptor.AfterIfPresent = { "Scripting" };`, build, read the Console line: expected `WindZone, UI, Scripting, Animation, World, Physics, Audio`; restore.
12. Medium exercise: the download `exercise-2.patch` (on top of the change; saved at `G:/GameEngineAI/.worktrees/docs-work/walk-E-final-9/ex2.patch`): build, run the suites; see WK9 for what the patch does and does not do. The page's prediction of failing tests needs the rename alone, without the patch's test edits.
13. Hard exercise (Turbulence): no patch is offered; the integrator may write one and check the two failing tests named by the page (FeatureTest and Reflection.ComponentSchema) and the round trip test needing no change.
14. Other pages' commands: `StrataTests.exe --test-suite=Scene.Documents`, `Scene.Prefab*`, `Scene.Streaming`, `Scene.Loader`, `Scene.SubScenes`, `Project*`, `Core.Settings`, `Scene.Timing` and `ctest --preset windows-debug` (each page's "How it is tested"; the names of the test cases quoted there were not looked up).

## WK1
- Entry: `world/serialization`
- Page: Scene documents: text, streams and the cooked form
- Step: the start of the page ("What you need", the stage download)
- What happened: the page has no "What you need" section and offers no stage download; it has "Before you start" with three links (scene graph, reflection, files you can trust). The same holds for prefabs, sub-scenes and projects-settings. Only the tutorial has a "What you need", and it too offers no stage (a source build of the first change is its start). I started each page with the package installed and the engine tree read in a scratch worktree.

## WK2
- Entry: `world/serialization`
- Page: Scene documents: text, streams and the cooked form
- Step: Exercises, Basic ("Copy a sample project to a scratch folder ... save once and commit")
- What happened: the page names no sample for the exercise. I guessed OpenWorld, whose Loading.stscene the page quotes, and took the camera ID 091558F6E234E59C from the quote and the scene handle from its `.meta`. The first save already changed two lines (the header line and the camera line), not "every line", because Loading is in the streamed layout. I also did the Tetris copy: its first save gave 21 lines added and 1,154 removed, as the page says.

## WK3
- Entry: `world/serialization`
- Page: Scene documents: text, streams and the cooked form
- Step: "What a scene file looks like", the diff of the camera, and the Basic exercise's one line
- What happened: the camera line the page prints (keys ClearColor to Projection, 9 keys) is the committed sample's. After a first save of the package's Loading.stscene the camera entity has more keys (Aperture, DepthOfField, FocusDistance, FocusEntity, and the file is 4,026 bytes, not 3,984). So the page's pictured old and new line differ only in Translation, mine in many keys. After the first commit, moving the camera gave one line changed, as the page says (`git diff --numstat` 1 1).

## WK4
- Entry: `world/serialization`
- Page: Scene documents: text, streams and the cooked form
- Step: Exercises, Medium "Trace it yourself" (load the cycle document as a scene)
- What happened: the page does not say how to load a hand-written document. I guessed: wrote the file outside the project, `asset.import` with directory Scenes, then `scene.open`. Result as the worked solution says: both entities load, First is a child of Second, and the log holds `Scene 'Cycle': Entity 00000000000000A2: parent 00000000000000A1 would create a cycle; attached at the top level`. The code locations (EntitySink.cpp 130 to 135 and 415, SceneSerializer.cpp 528 and 556) are right.

## WK5
- Entry: `world/prefabs`
- Page: Prefabs: the data model
- Step: Exercises, Basic (Torch, T1 to T4)
- What happened: the page gives no commands for making the prefab and the four instances. I guessed `entity.create` (root and child with the components), `prefab.create` (with a path I chose, `Prefabs/Torch.stprefab`), three `prefab.instantiate` instances, `component.set`, `component.remove`, `prefab.apply`. Results equal the answer: T1 4/8/0.4; T2 range 9 kept, intensity 4, volume 0.4; T3 4/8 and no AudioSource; `prefab.status` lists the Range override for T2 and the removed AudioSource for T3; the apply reported 3 updated instances. Medium (the code trace) matched the source.

## WK6
- Entry: `world/sub-scenes`
- Page: Loading scenes: whole, additive and in slices
- Step: "Watching a load from outside" (command tab `StrataCLI call scene.loadStatus` and the captured result)
- What happened: the tab says nothing of what to load first, and the capture's scene handle 43FD467DF4593C28 is the Loading scene of the ThirdPerson sample, which the page does not name. I played the OpenWorld start scene (a world) and loaded its Loading scene additively: 7 entities, 1 slice, state Loaded, but `subScene` was 9, and `subScenes` of `scene.loadStatus` also listed the world's cells (352, 2, 311, 19 ... entities), so the answer does not look like the page's one entry. The fields and their meanings match.

## WK7
- Entry: `world/projects-settings`
- Page: Projects and settings
- Step: "The project file" (the listing of the file with "Its top has a header")
- What happened: the page's text says the file's top has a header, then the configuration, then the settings, and the listing is one compact line each. A real `.stproj` (package sample, and what the editor writes) is tab-indented with sorted keys: `Project`, `Settings`, then `Strata` (the header) last, and `Scene.Timing` stored as `Value` and `Version`. The version 3 header and the contents agree otherwise. The cases of the page held: a header version 4 gave `unsupported project version 4 (this engine reads up to 3)`; a member `Cloud` in Project survived a save; `project.setSettings` with FixedRate 120 gave `maxFixedSteps` 16, 240 gave 32, a bad value or `Bogus` was refused naming the field.

## WK8
- Entry: `world/projects-settings`
- Page: Projects and settings
- Step: Exercises, Medium (Game.Tuning in a local registry) and the Inspector line with the project rate
- What happened: left unwalked as practice: the Medium exercise's code has no home outside the engine's tests (the page gives pseudocode with a helper `MakeIntField` it does not define), so I checked it only through the sketch whose output matches (the toy section). The Inspector's "120 steps/s (project)" line I could not see; the data behind it (`scene.info` settings.fixedRate: source project, 120 steps/s) matches.

## WK9
- Entry: `world/tutorial-component`
- Page: Tutorial: adding a component and a system
- Step: Exercises, Medium (rename WindZone to WindArea) and its download `exercise-2.patch`
- What happened: the exercise says to change the name "in the registration only, and leave the file Feature.stscene as it is", and the answer lists five tests that fail. The downloaded "worked solution" patch does something else: it renames in the registration, the reflection test, the round trip test, `ComponentSchema.json` and `Feature.stscene` (so those tests pass), and adds a sixth test about an unknown component kept under the old name. The patch applies, but it is not the state the answer describes; the page does not say so.

## WK10
- Entry: `world/tutorial-component`
- Page: Tutorial: adding a component and a system
- Step: the bottom strip (previous and next)
- What happened: "Next" in the strip reads "Review: scenes and the ecs", while the line "Next on your track" reads "How a GPU works and draws a frame", so a reader on track E skips the part's review without being told. Left the book: I stopped at the end of this entry.

## WK11
- Entry: `world/tutorial-component`
- Page: Tutorial: adding a component and a system
- Step: the build, editor and test steps (everything after "Declare the wind zone's data")
- What happened: the segment's rules forbid building, so these steps were not run; each is listed under "Built by the integrator". What I could check without a build: the change applies, the counts the page gives for files, lines, schema lines and assertions are right, the quoted context of each hunk equals the engine at 319075e3, and the package's own Console line (`UI, Scripting, Animation, World, Physics, Audio`) is the baseline the page's WindZone line is built from. The hard exercise (Turbulence) has no patch, so the integrator would have to write one.

## Answers

Measured with the official 0.8.0 package in `--no-gpu` editors under the perf lock (work folder
`docs-work/walkfix-E9`: `measure.py` to `measure4.py`, and `pagelines.ps1`, which runs every PowerShell line the pages
now give, as written, in Windows PowerShell 5.1). The patches under "## Built by the integrator" were applied to the pin
clone and built in `build/docs-patch` (Release) by `integrate.py` and `integrate2.py`, with a configure after each
apply and after the revert; the clone was left clean. Every changed page passes `tools/pagecheck.py`. The only tutorial
file that changed is new: `tutorials/world/projects-settings/exercise-2.patch`, passed and stamped by
`tutorials.py patch` (an engine exercise: no `run` with the pin build or the package applies to it).

### world/serialization

- **WK1** fixed on all four concept pages and the tutorial. Why: a concept page has no "What you need" by the book's
  style (style.md §7.4 gives it to tutorials), but none of the four said what its hands-on parts use. Change: one
  paragraph near the start of `world/serialization`, `world/prefabs` and `world/sub-scenes` says that they use the
  installed Strata, its samples and `StrataCLI` (link to How to read this book) and that the source files are in the
  clone of the first engine change; `world/projects-settings`, which has no room in size L, names in its Medium
  exercise what it builds on. The tutorial's "What you need" now says that it has no stage to download: it starts from
  that clone, with or without the first change, which touches none of its files.
- **WK2** fixed. Why: the exercise named no sample and gave no lines. Change: it names `OpenWorld` (the page's
  `Loading.stscene` is that sample's, as the toy and the example already said) and gives the nine PowerShell lines
  (`git -C <copy>` for the commits, `scene.open`, `scene.save`, `component.set` with the camera's ID, `git diff
  --numstat`), with `echo` for Linux and macOS and the link forward to Commands. Measured: `2 2` after the first save,
  `1 1 Assets/Scenes/Loading.stscene` after the move. The Tetris figures (21 added, 1,154 removed) stand.
- **WK3** fixed. Why: the sample was written by an older editor; the page's diff showed the committed line, not what
  a save writes. Measured: the first save drops `MaxBodyPairs` and the empty `PhysicsLayers` table from line 1 and
  adds `Aperture`, `DepthOfField`, `FocusDistance`, `FocusEntity` and `SensorHeight` to the camera (3,984 to 4,026
  bytes). Change: a paragraph says so before the diff, the diff now holds the camera line as the 0.8.0 editor writes
  it (old and new differ only in Translation), and the `Settings` paragraph no longer says the sample "still holds"
  `MaxBodyPairs`. The :::why claimed that `git diff --word-diff` helps; measured, it marks the whole line (the lines
  have no spaces), so it now gives `--word-diff-regex=[A-Za-z0-9.-]+`, which marks `[0,[-0-]{+2+},0]`.
- **WK4** fixed. Why: the exercise did not say how to load a hand-written document. Change: four lines (`asset.import`
  of the file from outside the project into `Scenes`, `scene.open`, `log.read` with `minLevel` Warn, `scene.hierarchy`)
  and a note to write the path with `/`. Measured: `Second` at depth 0, `First` below it, and the page's warning.
- The page was at the top of size L; seven sentences of the body were shortened to pay for the additions (notes).
- Engine: the samples' first save is not empty (notes, "## Engine").

### world/prefabs

- **WK5** fixed. Why: the exercise gave no commands for making the prefab and its four instances, which a track E
  reader before Commands needs as complete lines (rulings-4.md, R11). Change: two fences of PowerShell lines with
  placeholders, `scene.new`, `entity.create` of the root and of the `Flame` with its two components, `prefab.create`
  (which links the root as T1), `prefab.instantiate` three times, then the three changes and `prefab.apply` of T4; a
  sentence on `entity.get`, whose `children` give each flame's ID; the link forward to Commands. The answer now names
  the overrides' kinds. Measured with the lines as written: T1 4/8/0.4, T2 4/9/0.4, T3 4/8 without `AudioSource`,
  `updatedInstances` 3, `prefab.status` with `Property` `Range` for T2 and `RemovedComponent` `AudioSource` for T3.
- WK1 on this page: the paragraph near the start (see world/serialization).

### world/sub-scenes

- **WK6** fixed. Why: the section gave the status line without saying what to load first, and its capture is of the
  `ThirdPerson` sample, which it did not name. Change: copy `ThirdPerson`, press **Play** (the first play builds the
  scripts), then two PowerShell lines, `scene.loadAdditive` of `Scenes/Loading.stscene` and `scene.loadStatus`; a
  sentence says that in a world such as `OpenWorld` the loaded cells are sub-scenes too, so the list holds them and
  the new one gets a number after theirs (the walker's sub-scene 9). Measured with the package: the capture's entry
  exactly (sub-scene 1, handle 43FD467DF4593C28, 7 of 7, 1 slice).
- WK1 on this page: the paragraph near the start (see world/serialization).
- Not reproduced: one long measuring session lost the editor during `play.start` after a project switch; three fresh
  sessions did not (notes, "## Engine"). The page does not mention it.

### world/projects-settings

- **WK7** fixed. Why: the listing showed a compact file with the header first; `Project::MakeFileText` writes a
  sorted object with a tab before each level (`Project.cpp:387-417`), so `Project`, `Settings` and the header `Strata`
  come in that order, and a section stores `Value` before `Version`. Change: the sentence before the listing says so,
  the listing is the 23 lines the writer makes for that project, and two callouts name the sections and the header,
  which `Load` reads first wherever it stands. Checked against the file the 0.8.0 editor wrote for a copy of
  `OpenWorld` after `project.setSettings` and `project.save`. The walker's behavior checks stand.
- **WK8** fixed. Why: the Medium answer was pseudocode with an undefined helper, and nothing told where the code
  lives or how to run it. Change: the exercise asks for a test case of `Core.Settings` in a new file
  `GameTuningTests.cpp` of the reader's clone, configured, built and run. The worked solution is a patch,
  `tutorials/world/projects-settings/exercise-2.patch` (download), with the helper `MakeIntField` and the test case,
  which the answer quotes (31 lines, four callouts): the upgrade, the two refusals with their messages, and `Legacy`
  dropped at version 1 and refused at version 2. Built in `build/docs-patch`: `--test-case=Game.Tuning*` passed, 12
  assertions; the suite 8 test cases; `tutorials.py patch` passed (`Architecture.Layering`, feature test) and stamped
  it. The Inspector line: a headless editor has no Inspector, so the page now adds that `scene.info` reports the
  same under `fixedRate` (source `project`, 120 steps per second, cap 16), as measured.
- WK1 on this page: the Medium exercise names the clone of the first engine change. The page was at the top of size
  L; six sentences were shortened (notes), and `time` went to 100, the reading floor pagecheck computes.

### world/tutorial-component

- **WK9** fixed. Why: the exercise asked for the rename alone, but its worked solution is the migration, and the
  answer's list of failures was wrong. Built: the rename alone fails six test cases of the page's suites (two of
  `Reflection`, `Reflection.ComponentSchema`, one of `Engine.Modules` whose build without the game UI lists `WindZone`
  among the feature scene's unknown components, and two of `Scene.Serialization`, the committed-scenes check and the
  round trip test, which ends the run with `test case CRASHED: SIGABRT`), and the feature test fails in each test case
  that loads its scene and on `WindArea`. Change: the exercise now has two parts, predict and run the rename alone,
  then migrate the name until every test passes; the answer names the failures as measured and says that the worked
  solution is the migration (with it `Physics.WindZone` passes with three test cases). The patch is unchanged.
- **WK10** fixed. Why: the strip's "Next" is the part's review, which is not on track E. Change: the closing paragraph
  says that track E continues at How a GPU works and draws a frame, and that the review the strip offers is extra
  practice off track E.
- **WK11** built by the integrator (the patch, as the page's download). Matched: the failures before the test edits,
  the passes after them, 2 test cases and 11 assertions, the break of the two `IsActiveInHierarchy` lines (the second
  test case, two zones), the feature test's message, the layering and schema checks, the editor's log line with
  `WindZone` after `Scripting`, the defaults 10, 5 and Directional, exercise 1's order and exercise 3's two failures.
  Did not match: the schema helper writes 207 added lines, not 57: the 57 of `WindZone`, byte for byte the patch's,
  and 150 of `RectLight`, which the pin's snapshot lacks; the step's "You should see" now says so, and its "If you do
  not see it" speaks of lines changed or removed. The full `ctest -LE "gpu|perf"` of the Release build passed 85 of 85.
  Not run: the Debug configuration, and the Inspector's clamp and tooltip (no window; commands refuse the two values
  instead, with `WindZone.Radius must be between 0.01 and 1000000, not -3`). Engine: the stale snapshot (notes).
- WK1 on this page: "What you need" says there is no stage to download.

Left over: the Inspector steps of the tutorial and the "120 steps/s (project)" line need a windowed editor; the
unreproduced loss of an editor during `play.start` (sub-scenes notes). Nothing is left running, and the pin clone is
clean.


## Confirm

Walked by E1 as a reader of the built book at http://127.0.0.1:4329/strata-engine-docs/ (Strata 0.8.0 package, `--no-gpu` editors, one hold of the perf lock each, my own session folders, no editor left running). The tutorial and the projects-settings exercise were built by the integrator steps in the pin clone's `build/docs-patch` (Release; the clone was left clean and configured again). Work folder: `docs-work/walk-E-final-9/c9/` (`s1.ps1` to `s4.ps1` with their `.out`, `integrate3.py` and `integrate3/summary.log`).

The served build is older than the book's source for `world/tutorial-component` (its last commit, ba622cd7): the served page still says 57 added lines, has no bottom paragraph about track E, has the old "What you need" bullet and the old five-test answer of Exercise 2. The source holds the fixes and they match what I measured. The other four pages are served as fixed. The served downloads (`tutorial-component.patch`, both `exercise-2.patch`) are byte for byte the book's files.

### WK1: confirmed on the three concept pages; tutorial confirmed from the source only
- `world/serialization`, `world/prefabs`, `world/sub-scenes`: the paragraph near the start says that the hands-on parts use the installed Strata, its samples and StrataCLI, and that the source files are in the clone of the first engine change. I knew what to install and where the source was; no guess.
- `world/tutorial-component`: the source's bullet reads "No file to import and no stage to download: you start from that clone, with or without your first change, which touches none of the files below". The served page still has the old bullet ("No file to import. You change the engine ..."), which does not name the missing stage. Fixed in the source, not yet served.

### WK2: confirmed
- A fresh copy of OpenWorld, the nine lines run from the Strata folder in Windows PowerShell 5.1. After the first save `git diff --numstat` gave `2 2 Assets/Scenes/Loading.stscene` (I added that one line to see it; the page's lines do not print it); at the end `1 1 Assets/Scenes/Loading.stscene`. The camera ID in the line is the real one. No guess.
- One thing outside the book: `git commit` failed with "Author identity unknown" on a machine with no git identity, so the commits were missing until I set one in the environment. The exercise and Commands do not say a git identity is needed. A reader who has done the version-control page has one; noted, not counted as a mismatch.

### WK3: confirmed
- The camera line the page prints as old and new equals, character for character, the line of the diff after the second save (the 0.8.0 editor's keys, Aperture to SensorHeight); old and new differ only in `Translation`. `git diff --word-diff --word-diff-regex=[A-Za-z0-9.-]+` marks `"Translation":[0,[-0-]{+2+},0]`.

### WK4: confirmed
- Cycle.stscene written outside the project, the four lines as printed (`/` in the path): `asset.import` and `scene.open` answered; `log.read` held `Scene 'Cycle': Entity 00000000000000A2: parent 00000000000000A1 would create a cycle; attached at the top level` (and the sample's scripts warning); `scene.hierarchy` gave Second at depth 0 and First at depth 1. Equals the answer.

### WK5: confirmed
- The two fences with the IDs filled in (the id read from each answer's `id` field, the flames from `entity.get` `children`). Results: T1 intensity 4, range 8, volume 0.4; T2 intensity 4, range 9, volume 0.4; T3 intensity 4, range 8, and `component.get AudioSource` fails with "The entity has no AudioSource component"; `prefab.apply` answered `updatedInstances` 3; `prefab.status` of T2's flame holds one override of kind `Property` for `Range`, of T3's one of kind `RemovedComponent` for `AudioSource`, T1's none. Equals the answer.

### WK6: confirmed
- Copy of ThirdPerson, `play.start` (the first play built the scripts, 20.7 s, state Play), then the two lines. `scene.loadAdditive` answered `subScene` 1, handle 43FD467DF4593C28, 7 of 7 entities, 1 slice, Loaded; `scene.loadStatus` `subScenes` holds exactly the capture's one entry (all ten fields equal), beside the members the capture leaves out (lastOpen, open, play, world), as the page says.

### WK7: confirmed
- A project made by the editor (`project.create` basic3d, then `project.setSettings Scene.Timing {"FixedRate":"120","Interpolation":true}`) is written with tabs, sorted keys, `Project`, `Settings`, then `Strata` last, `Scene.Timing` as `Value` and `Version` 1, header `Format` Project, `Version` 3. It equals the page's listing (shown with two spaces; the file has tabs: harmless). The folder holds Assets, Scripts, `.strata` and `.gitignore`, as the tree says.

### WK8: confirmed, the Inspector line not seen
- Exercise 2 (Medium): `git apply` of the served `exercise-2.patch` to the clone at 319075e3 succeeded; configure, then build of `StrataTests` succeeded; `StrataTests --test-suite=Core.Settings --test-case=Game.Tuning*`: 1 test case, 12 assertions, passed; the suite `Core.Settings`: 8 test cases, 231 assertions, passed. The helper `MakeIntField` is in the patch the answer points to. Reverted.
- After `project.setSettings Scene.Timing FixedRate 120` the `scene.info` line `settings.fixedRate` reads source `project`, `stepsPerSecond` 120, `maxFixedSteps` 16, as the page says. The Inspector's "120 steps/s (project)" I cannot see (no screen).

### WK9: confirmed in the source; the served page is older
- The rename alone (the patch limited to `PhysicsComponents.cpp`), then the suites of the page: exactly six test cases fail: Reflection twice (the unique-name test and the wind zone's own), Reflection.ComponentSchema once, Engine.Modules once (the build without the UI module lists `WindZone` as unknown), Scene.Serialization twice (the committed scenes check and the round trip, which ends in `test case CRASHED: SIGABRT`). The feature test fails too (the warning, and no entity holds WindArea). That is the source's answer. The served page says "Two feature tests fail ... Three more tests fail", which does not match until the preview is rebuilt.

### WK10: confirmed in the source; not served yet
- The source's paragraph after the last section: "Track E continues with the graphics processing unit (GPU), at How a GPU works and draws a frame. The strip below also offers the review of this part, which is not on track E: take it as extra practice." It agrees with "Next on your track" in the strip. The served page has no such paragraph, so a served reader still sees two different "Next" entries without being told.

### WK11: confirmed with the source's numbers
- Applied `tutorial-component.patch` to a clean 319075e3 (no error), configured, built `StrataTests`: step 4 before the test edits fails in `Scene.Systems` and `Engine.Modules` (9 test cases), after the edits all 19 pass; step 5 suites 37 test cases pass, `Physics.WindZone` alone 2 test cases and 11 assertions; step 6 (the two `IsActiveInHierarchy` lines removed) fails on `GetZones().size() == 1`, restored it passes; step 7 the feature test fails with "Component WindZone: the feature scene ... must contain it", with the entry it passes. The schema step wrote one changed file with `207 insertions(+)` and no deletions (the source says 207: 57 of WindZone and 150 of RectLight; the served page says 57, a mismatch there). The feature test and `Architecture.Layering,Reflection.ComponentSchema` pass. Not repeated: the whole `ctest -LE gpu` run, the editor's startup line and the Basic and Hard exercises (not in this segment's list).

### Result
Confirmed: WK2 to WK8 (WK8 with the Inspector line unseen), and WK1 on the three concept pages. WK1 (tutorial bullet), WK9, WK10 and the 207 lines of WK11 are right in the book's source and measured as it says, but the served preview was built before commit ba622cd7: rebuild it from `book/write` and read those four places again.

## Answers (after confirm)

All three are right in the source at `book/write`; the confirmer measured WK9 and WK11 as the source says and read a
preview built before commit ba622cd7. Checked again in the source and run under the perf lock, with no change.

### WK9 world/tutorial-component, Exercises, Medium
- Holds. The answer (line 819 on) gives the rename alone six failing test cases (two in `Reflection`,
  `Reflection.ComponentSchema`, `Engine.Modules` and two in `Scene.Serialization`, one a SIGABRT crash) plus the feature
  test, as the confirmer counted, and the worked solution is the migration. `tutorials.py patch
  world/tutorial-component/exercise-2` in `build/docs-patch` passed: the page's patch and the exercise's, seven doctest
  suites and the feature test.

### WK10 world/tutorial-component, bottom strip
- Holds in the source: line 760, the closing paragraph, says track E continues at How a GPU works and draws a frame, and
  that the part's review the strip offers is not on track E and is extra practice.

### WK11 world/tutorial-component, build, editor and test steps
- Holds. `tutorials.py patch world/tutorial-component` passed (the page's patch, seven doctest suites and the feature
  test); the clone is clean afterwards. Line 731 of the source (step 3's "You should see") says 207 added lines, 57 for `WindZone` and 150 for
  `RectLight`, the count the confirmer measured.

## Confirm (after the second answers)

Read as a fresh reader: the pages at book/write, the 0.8.0 package, the pin, under the perf lock; results in `docs-work/walk-final-confirm-2`. Every entry below: through without guessing, leaving the book or a mismatch.

### WK9 and WK11 world/tutorial-component
- Holds as read, not patched here: the Medium answer gives six failing test cases (two in Reflection, Reflection.ComponentSchema, one in Engine.Modules, two in Scene.Serialization: six) and the feature test, and step 3's You should see says 207 added lines (57 WindZone, 150 RectLight); both agree with the fixer's measured runs (patch passed with 7 suites and the feature test).

### WK10 world/tutorial-component
- Holds. Source line 760 says track E continues at How a GPU works and draws a frame (link target exists) and that the strip's review of the part is extra practice.
