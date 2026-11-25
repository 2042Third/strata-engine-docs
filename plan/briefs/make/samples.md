# Brief: `make/samples`

| Field | Value |
| --- | --- |
| Title | Studying the samples |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/project-coin-run` |
| From | gamedev "Studying the samples" (§1.20); worlds-runtime "The Launcher, Templates and Samples" (use side) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/samples` — Studying the samples

**Covers.** The goal: learn from the three samples that block C does not build (Physics Playground, Open World and the
High Desert Outpost) by playing them, reading how they are made and changing one thing. What must be true first: Open
Sample as `start/first-game` used it. The steps. Open a copy: **File ▸ Open Sample** (or the launcher's sample cards)
makes a copy in a folder the reader chooses, without the original's `.strata` folder, and the sample's picture becomes
the copy's; Play builds the scripts first. Read the README: what it shows (a table from each engine feature to the
files that hold it), its controls, how it was made (by an AI agent through the editor, with the commands named) and its
credits (the `CREDITS.md` table of files, source, author, license, attribution and changes); each sample's regression
is a command script of the engine's tests. Then the three samples, each with what to look at and one change to try.
Physics Playground: about 600 bodies of four materials, triggers counting the goal's balls, the Ghost layer that does
not collide with balls, a ball shot through the cursor and a body grabbed, 100 balls poured in one
`Scene::InstantiateMany` call, impact sounds within a budget of voices, slow motion, a reset that reloads the scene.
Open World: a world of three layers in 64 m cells around a persistent scene of 97 terrain tiles, 20,000 props drawn on
the GPU, a teleport that prefetches cells and waits for the ground, foxes in streamed cells, a day that turns into night
under the atmosphere with campfires at dusk, a loading scene. High Desert Outpost: the graphics showcase, made from
scans and generated terrain and props, three times of day each with two baked probes switched with a hold, a camera
tour, walking and flying, a photo mode (time, exposure, field of view, focus, f-number, the players' quality and
anti-aliasing), flickering fire and lanterns; its copy is the largest of the samples. The samples' rules as a model for
the reader's own game: a README with the feature table, controls, how it was made and credits, a picture, a few
screenshots within a size limit, CC0 or CC-BY assets only. Result: a list of where each feature lives in the samples.
Variations: reading a sample's regression script; changing a value of a sample's script and hot reloading it. The
exercise: the Open World's day shortened in the Inspector until the campfires light.

**Leaves out.**

- Tetris, built as a project → `make/project-tetris`
- The Third-Person Adventure, built as a project → `make/project-platformer`
- Templates, samples as copies and recent projects, as the editor models them → `editor/projects`
- The launcher and the Open Sample dialog as UI → `editor-ui/launcher-dialogs`
- Each feature the samples show → `make/physics`, `make/large-worlds`, `make/reflections`, `make/look`
- How the samples' regressions run in the engine's tests → `engineering/test-kinds`

**Fit.** `fits`: about 3,750 words against M (3,000): three steps for opening and reading, about 630 words for each
sample with its screenshots and its change to try, the samples' rules, two variations and the exercise take the most.
The Showcase is a wave 8 sample: the pin move's diff decides what is read again.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:35` | feature | home | Samples and Open Sample: `Samples.json`, copies without `.strata`, the picture as the copy's thumbnail |
| `gamedev:256` | feature | home | Physics Playground: bodies, materials, triggers, the Ghost layer, shoot, grab, pour with `InstantiateMany`, impact sounds, slow motion, reset, hot reload, the export's demo |
| `gamedev:257` | feature | home | Open World: three layers in 64 m cells, 97 terrain tiles, 20,000 props drawn GPU-driven, the source on the player, teleport with prefetch, foxes, day and night, the loading scene |
| `gamedev:258` | feature | home | High Desert Outpost: scans and generated content, three stations with baked probes, the tour, walk and flight, photo mode, flicker, the loading scene |
| `gamedev:260` | feature | home | The samples' rules: README with a feature-to-file table, controls, how it was made, credits; `CREDITS.md`; picture and screenshots within a size; source assets within a size; game identity |
| `gamedev:472` | figure | home | Physics Playground: the overview, the ball pit after a pour (existing `Screenshots/`), a grab, slow motion |
| `gamedev:473` | figure | home | Open World: the tour (existing `Tour.png`), the forest (`Forest.png`), night with campfires, the teleport's fade; a capture that shows a fox names the fox's authors and license in its caption (`appendix/credits` holds the full entry); `Samples/OpenWorld/Screenshots/Tour.png` and `Forest.png` show no fox |
| `gamedev:474` | figure | home | Showcase: the six tour shots (existing `Screenshots/`), the photo mode's panel |
| `new:27` | hands-on | home | Exercise, done in the editor: in the Open World copy, the sun's `DayNight` fields set in the Inspector, `DayLengthSeconds` 60 and `TimeOfDay` 17, then Play: the campfires light at dusk and the log says so. Evidence: `Samples/OpenWorld/Scripts/DayNight.h:19-20`, `:61-68` |
| `worlds-runtime:179` | feature | use | Samples as copies, the picture cards (home `editor/projects`) |
| `worlds-runtime:185` | feature | use | The Open World sample's world, as its README describes it |
| `editor-ui:215` | feature | use | The Open Sample dialog |
| `editor-ui:550` | figure | use | The New Project and Open Sample dialogs |
| `gamedev:254-255` | feature | link | Tetris and the Third-Person Adventure, built in block C |
| `gamedev:229` | feature | link | The samples' regressions (home `engineering/test-kinds`) |
| `gamedev:519` | rule | use | Asset licenses: CC0 or CC-BY only, credited (home `make/assets`) |
| `gamedev:575` | term | link | Sample |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Opening a copy of a sample; Play | `start/first-game` | must |
| Reading a script and its fields | `make/scripting-scene` | must |
| Hot reload | `make/first-script` | must |
| Asset licenses and credits | `make/assets` | must |
| Bodies, triggers and collision layers | `make/physics` | helps |
| Worlds, cells and prefetching | `make/large-worlds` | helps |
| Baked probes and times of day | `make/reflections` | helps |
| The camera's image and depth of field | `make/look` | helps |

**Starting state.** No project of the reader's and nothing to download: the three samples ship with the editor, and the
steps open copies of them from the editor's launcher.

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
| critic-make-b2-15 | should | shape | `make/samples` (Covers; the variation "reading a sample's regression script"); `make/automated-playtests` (the smoke-test variation) | The samples' regression scripts live in `StrataTests/Editor/`, which the release archive does not ship: it installs the programs, the samples, the SDK, the manual and the skills. The READMEs name those files, the page says each regression is a command script of the engine's tests, and its variation has the reader read one that the reader does not have. | The variation reads a part the page quotes (for example the Physics Playground's paused `until` steps), or the book offers the file among the page's downloads; the sentence on regressions says they are in the engine's repository, not in the archive. `make/automated-playtests` quotes what its smoke-test variation models in the same way. About 40 words. | `allocation/make-b2.md:986-987`, `:999`, `:734`; pin: `CMake/StrataPackaging.cmake:55-85`; `Samples/PhysicsPlayground/README.md:54`; `Samples/OpenWorld/README.md:58`; `Samples/Tetris/README.md:41`; `Samples/ThirdPerson/README.md:72` |
