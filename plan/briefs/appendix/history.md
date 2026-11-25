# Brief: `appendix/history`

| Field | Value |
| --- | --- |
| Title | Which release brought what |
| Kind | R |
| Size | M |
| Tracks | - |
| Needs | - |
| From | `Docs/Releases/` of the engine |
| Unit | `plan/allocation/appendix.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `appendix/history` — Which release brought what

**Covers.** One paragraph on how to read it: versions follow the engine's development waves (0.3.0, the first release,
held waves 1 to 3; each later minor version holds one wave) and patch versions carry fixes; the book targets 0.8.0, and
at the pin the programs still report 0.7.0, which is not a mistake (one sentence, as `style.md` §13 asks). Then one
section per release, oldest first: 0.3.0 (waves 1 to 3, the last completed on 2026-10-12), 0.4.0 (wave 4, completed on
2026-10-19), 0.5.0 (wave 5, completed on 2026-10-20, the release that moved physics from Jolt to box3d), 0.6.0 (wave 6,
completed on 2026-10-23), 0.7.0 (wave 7, integrated on 2026-10-28) and 0.8.0 (wave 8). Each section gives the date and
the wave, a table of what the release brought by area (editor, worlds, rendering, game UI, physics, audio and
animation, scripting, exported games, AI agents, instruments and scale, as the release notes group them), each row
linking the page that teaches the feature, and the upgrade notes that changed projects (in 0.6.0 the collision layers
became the project's, migrated once from 0.5.0's scenes). The rows come from each release's "What's new" (for 0.3.0,
"What you can do with it"), "What changes with box3d" and "Upgrading from" sections, and from the Roadmap's Status
paragraph of each wave. The 0.8.0 section is drafted at the pin from `Docs/Plans/Wave8/ReleaseNotes.md` and rewritten
from `Docs/Releases/0.8.0.md` at the tag; its rows agree with the pages' `since: 0.8.0` front matter, so the table and
the "New in 0.8.0" labels name the same features. The build and tests, which the release notes group under no area of
their own, get a row in each release that the Roadmap's Status dates them in (the perf lab in wave 1, the CI jobs and
shards of wave 4, the look-dev harness of wave 7, Slang in wave 8). Features the documents do not date (the surveyors
list them, below) are named as not dated, never guessed. The page states no plan: what the Roadmap lists for later is quoted on
`appendix/not-in-strata` and the subsystem pages.

**Leaves out.**

- What each feature does and how it works → `reference/term-index`
- What the engine's documents plan for later → `appendix/not-in-strata`
- How a release is built, packaged and published → `engineering/releasing`

**Fit.** `fits`: about 1,200 words against M (3,000). That is the prose: a paragraph per release with its date, wave
and upgrade notes (750), the undated features (250) and the paragraph on versions and the pre-release pin (200); the
page's size comes from its tables, written by hand from the release notes (R36): six release tables of about 12 rows
each (1,300 words) and the build and test rows (150), whose 0.8.0 section phase B rewrites from the notes at the tag.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `audio-input:755` | open | home | The dating of audio and input: audio, basic input, gamepads and simulated input in 0.3.0; `input.sequence`, `input.click` and UI navigation in 0.4.0; simulated input at time scale 0 in 0.5.0; input actions and rebinding in 0.6.0; the players' bindings in the user data folder of shipped games in 0.7.0; finer dating stated as not traced |
| `gamedev:699` | open | home | Features whose release the documents do not state (the long-path build fallback, `UIMask` and world-space canvases, the Scripts root of the Content Browser, the Hierarchy's search tokens); morphological anti-aliasing is 0.7.0's by its notes |
| `gamedev:701` | open | home | Wave 8's status at the pin: the Showcase, `Scene.Timing` and interpolation, the drop ghost and `asset.place`, the editor's frame-rate preferences, Source Radius and experimental global illumination are on main; what 0.8.0 ships is read from its notes at the tag |
| `new:131` | feature | home | 0.3.0, the first release: waves 1 to 3, completed on 2026-10-12. Evidence: `Docs/Releases/0.3.0.md:3-6`, "What you can do with it" at `:24-107`; `Docs/Roadmap.md:36, 66, 202` (the Status paragraphs of waves 1, 2 and 3) |
| `new:132` | feature | home | 0.4.0: wave 4, completed on 2026-10-19. Evidence: `Docs/Releases/0.4.0.md:3-6`, "What's new in 0.4.0" at `:27-95`; `Docs/Roadmap.md:360` |
| `new:133` | feature | home | 0.5.0: wave 5, completed on 2026-10-20; physics on box3d instead of Jolt. Evidence: `Docs/Releases/0.5.0.md:3-6`, "What's new in 0.5.0" at `:28-73`, "What changes with box3d" at `:75-103`; `Docs/Roadmap.md:460, 488` |
| `new:134` | feature | home | 0.6.0: wave 6, completed on 2026-10-23, and the upgrade from 0.5.0. Evidence: `Docs/Releases/0.6.0.md:3-7`, "What's new in 0.6.0" at `:30-115`, "Upgrading from 0.5.0" at `:117-151`; `Docs/Roadmap.md:511, 1334` (collision layers for the whole project, migrated once from 0.5.0's scenes) |
| `new:135` | feature | home | 0.7.0: wave 7, integrated on 2026-10-28, and the upgrade from 0.6.0. Evidence: `Docs/Releases/0.7.0.md:3-7`, "What's new in 0.7.0" at `:31-95`, "Upgrading from 0.6.0" at `:97-130`; `Docs/Roadmap.md:574` |
| `new:136` | feature | home | 0.8.0: wave 8, from the draft notes at the pin and the release notes at the tag. Evidence: `Docs/Roadmap.md:609` ("Wave 8 in progress"); `Docs/Plans/Wave8/ReleaseNotes.md:1-6` (written into `Docs/Releases/0.8.0.md` at the release), "What's new" at `:8-307`, "Defaults that change" at `:308-324`, "Upgrading from 0.7.0" at `:325-368` |
| `new:137` | feature | home | Versions follow the waves, and patch versions carry fixes. Evidence: `Docs/Releases/0.3.0.md:5-6`; `Docs/Releases/0.7.0.md:6-7` |
| `new:138` | feature | home | At the pin the programs report 0.7.0 while the book targets 0.8.0: a pre-release build reports the previous release. Evidence: `CMakeLists.txt:4` (`VERSION 0.7.0`); `Strata/src/Strata/Core/Version.h.in:17` (`c_EngineVersion`) |
| `gamedev:254-258` | feature | use | The samples and the release each arrived in (Tetris 0.3.0; Third-Person, Physics Playground and Open World 0.5.0; the Showcase in wave 8) |
| `physics:126` | feature | use | The collision layers' migration from 0.5.0's scenes, an upgrade note of 0.6.0 |
| `animation:645` | open | use | What the documents do not date in animation (the refinements of `WhenVisible`) |
| `assets:799` | open | use | What the documents do not date in the asset pipeline |
| `automation:841` | open | use | The automation area already exists in 0.3.0; the RPC core came in waves 1 and 2, before any release file |
| `build-test:765` | open | home | The dating of the build and tests: the perf lab in wave 1; release 0.3.0 with the Dist CI job, the perf lock, the CI-compiler lint and the CI status tool in wave 4's step 0; layer libraries, optional modules, precompiled headers, the Core shards, the fuzz run, the compiler cache and the Windows Debug CI job in 0.4.0; the look-dev harness in 0.7.0; Slang and the build without GLFW in wave 8, not yet released at the pin; the rest stated as not dated |
| `editor-core:800` | open | use | What the documents do not date in the editor's core |
| `editor-ui:874` | open | home | The release of arrival of the editor's interface features: what the documents date (idle throttling, the launcher, multi-edit, the Activity, Streaming, Performance and Problems panels, CJK fonts in 0.3.0; the Game view and others later) and what they leave undated, stated as such |
| `foundation:696` | open | use | What the documents do not date in the foundation |
| `gameui:740` | open | use | The game UI's history inside 0.4.0 to 0.7.0 |
| `physics:582` | open | use | What the documents do not date in physics |
| `render-core:843` | open | use | What the documents do not date in the renderer's core |
| `render-direct:824` | open | use | The release of the shadows' horizon fade, not stated |
| `render-image:804` | open | use | The image features whose release is partly inferred (bloom, tone mapping, grading, FXAA) |
| `render-scene:718` | open | use | What the documents do not date in drawing a scene |
| `scene-ecs:742` | open | use | What the documents do not date in scenes and the ECS |
| `scripting:687` | open | use | The wave in which physics bodies, queries, audio and game flow joined the script API, not stated |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The engine's programs, libraries, modules and layers | `core/map` | helps |
| How a release is packaged and published | `engineering/releasing` | helps |
| Layers, registries and modules chosen at compile time (the areas the tables group by) | `core/layers-registries` | helps |

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
| critic-appendix-18 | could | missing-item | `appendix/history`; new term on `engineering/releasing` | The page reads "versions follow the engine's development waves", and the book's W8 marks use the word throughout. No inventory glossary and no seed entry defines a wave, and a page of kind R explains nothing. | `engineering/releasing`, which teaches "the procedure at the end of every wave", homes the term "development wave": a planned batch of workstreams that ends in a release (the Roadmap's "Waves"). `appendix/history` links it. About 30 words. | `allocation/appendix.md:492-493`; `allocation/engineering.md:1140`; `glossary/seed.json` (no entry); pin `Docs/Roadmap.md:1099`; `Docs/Releases/0.3.0.md:5-6` |
