# Brief: `make/performance`

| Field | Value |
| --- | --- |
| Title | Making your game run fast |
| Kind | T |
| Size | M |
| Tracks | G |
| Needs | `make/quality`, `make/large-worlds`, `make/animation` |
| From | render-scene "Tutorial: making a big scene draw fast"; worlds-runtime "Measuring Shipped Games" (use side: `--perf-log`); the Performance panel, `renderStats`, the quality costs; scripting "The gameplay API, part 1": `Scene::InstantiateMany` (many instances in one call; each transform is built by one given line, such as `glm::translate(glm::mat4(1.0f), position)`, because track G has no page on matrices); use home of measuring a game · W8r (the `renderStats` keys and the Performance panel's numbers) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/performance` — Making your game run fast

**Covers.** The tutorial builds a scene too big to run well, measures it and makes it fast, on the page's own example: a
field of 5,000 props spawned by a script, then the Open World copy for streaming. The ideas come first, at a maker's
level: a frame's time in milliseconds against frames per second; a frame is bound by the CPU, by the GPU or by the
display's cap; an average hides spikes, so the panel shows p95 and the maximum; measure, change one thing, measure
again, on a named computer (the design decision that trade-offs are measured and the numbers shown, named again with a
link to `engineering/perf-lab`). The sections: spawn the field with one `Scene::InstantiateMany` call, each transform
built by one given line (`glm::translate(glm::mat4(1.0f), position)`); the viewport's **Stats** chip (draw calls opaque
and shadow, instances, triangles, visible and occluded proxies, assets loading), with the camera moved behind the hut to
see occluded proxies rise, and what raises the draw-call line, with a link to `draw/batching`: draws follow the mesh,
its submesh and level of detail and the pipeline state (double-sided, alpha-masked, mirrored, skinned), never the
material or the number of copies, so the common advice to merge materials to cut draw calls does not apply here; **View
▸ Performance** while playing (frame time, p95, maximum, FPS, the CPU and GPU stages, what bounds the frame, **Pause**
with Space to read a spike, **Copy as JSON**), and the editor's idle throttling in two sentences with a link to
`editor-ui/status`: while nothing happens the editor redraws at 30 frames per second, 10 without the focus, so the frame
pill shows that and not the game's speed; while the game plays it redraws up to the active frame rate of the
Preferences' Frame Rate page, unlimited by default (vsync sets the pace); levels of detail (200 copies of an imported
model receding, the LOD debug view, the project's preset Low against Ultra and its "Level of detail error" row); the
cost of shadows per object (Cast Shadows off on the field's small props and the shadow draw calls falling); streaming
(the Open World copy in the Streaming debug view, requests following the view as the camera flies); the exported game
(`--perf-log run.csv --frames 600 --resolution 1280x720`, the file opened in a spreadsheet program, frame time and GPU
stages per row, `--quality low` against `ultra`). Variations: vsync on and off in the exported game from the settings
screen, and what a capped frame shows in the panel; a world's streaming columns in the perf log; many animated
characters and their culling mode, read in the panel's animation stage; many scripts against one manager script, with
the engine's measured cost of a trivial `OnUpdate` and the rule to override only the callbacks you use. The exercise:
ten materials on the field's props, and the opaque draw calls that do not change. The W8r section, the Stats overlay's
lines and the Performance panel's numbers, is revised in phase B. At the end the reader can tell what bounds a game's
frame and lower its cost with numbers to show for it.

**Leaves out.**

- How the profiler measures stages, self time and percentiles → `core/profiling`
- How culling, batching, levels of detail and streaming work → `draw/bounds-culling`, `draw/batching`, `draw/lod`, `draw/asset-requests`
- GPU timestamps and readbacks → `gpu/readback-timing`
- Every perf budget and the machine it was measured on → `reference/performance`
- The runtime's options in general → `worlds/runtime`
- The presets and their rows → `make/quality`
- Spawning many instances by a command → `make/commands`

**Fit.** `over`: about 4,050 words against M (3,000): the three ideas, seven sections of about 16 steps with their
numbers, four variations and the exercise reach M's top; the next size is L (5,000) by S2, which also holds phase B's
revised numbers. W8r: phase B revises the section on the Stats overlay's lines and the Performance panel's numbers (and
the `renderStats` keys behind them), and the costs the presets show.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:56` | feature | home | The Streaming and Performance panels: budgets, loads, uploads, the cell map, physics; frame timings per stage with a pause |
| `foundation:541` | hands-on | home | Reading the Performance panel during play: CPU-bound, GPU-bound or capped |
| `render-core:661` | hands-on | home | Variation: vsync on and off in the exported game and its cost (the editor keeps its own vsync in play) |
| `render-core:672` | hands-on | home | The GPU stages of the game from `--perf-log` or the Performance panel, and which feature they come from |
| `render-scene:550` | hands-on | home | Is the scene drawing efficiently: draws, instances, triangles, visible and occluded, read on the Stats overlay instead of `renderStats` |
| `render-scene:553` | hands-on | home | The LOD view on 200 copies of a model, Graphics Quality Low against Ultra |
| `render-scene:555` | hands-on | home | Cast Shadows off on a dense prop field and the shadow draw calls |
| `render-scene:557` | hands-on | home | The Open World copy in the streaming view: requests follow the view |
| `render-scene:80`, `render-scene:82` | feature | use | What the draw-call line counts and what raises it: the pipeline state (double-sided, alpha-masked, mirrored, skinned), the mesh, its submesh and level of detail; not the material or the number of copies (`Strata/src/Strata/Renderer/SceneDrawKey.h:9-13`; 10,000 materials in one opaque draw call, `StrataTests/Perf/Budgets.json:155`; home `draw/batching`) |
| `render-scene:182-184` | feature | use | The debug views lod and streaming, the quality rows of detail, the Stats overlay |
| `render-scene:181` | feature | link | `renderStats`, the same numbers for commands (`make/commands`) |
| `editor-ui:150-151` | feature | use | The Streaming and Performance panels |
| `editor-ui:118` | feature | use | Idle throttling as a maker meets it: an idle editor redraws at 30 frames per second, 10 without the focus; while the game plays, up to the active frame rate of Preferences, Frame Rate, unlimited by default (home `editor-ui/status`; `StrataEditor/src/Editor/EditorFrameRate.h:26-28`, `:39`; `StrataEditor/src/EditorLayer.h:118-124`) |
| `foundation:303` | concept | use | Profiling: the method, frame time, percentiles, CPU-bound, GPU-bound or capped (home `core/profiling`) |
| `foundation:431`, `foundation:433` | figure | use | The Performance panel's stacked stages; the frame pill and what bounds the frame |
| `foundation:608-609` | term | link | Percentile; CPU-bound, GPU-bound, capped |
| `scripting:121` | feature | use | `Scene::InstantiateMany` (home `make/scripting-scene`) |
| `gamedev:239` | feature | use | The runtime's options `--perf-log`, `--frames`, `--resolution`, `--quality` (home `make/export`) |
| `worlds-runtime:130`, `worlds-runtime:132`, `worlds-runtime:136` | feature | use | The perf log's columns: the runtime's, the renderer's, the column groups |
| `worlds-runtime:295` | concept | use | Measuring a shipped game: per-frame logs, deterministic runs; the mistake of comparing runs whose game time followed the frame rate |
| `worlds-runtime:408` | figure | use | A perf log plotted in a spreadsheet |
| `worlds-runtime:481` | hands-on | use | Measure a run with `--frames 600 --perf-log run.csv --resolution 1280x720`, Low against Ultra |
| `animation:520` | hands-on | home | Variation: 500 animated characters spawned at once, their Culling Mode Always Animate against When Visible, read in the `Scene.Animation` stage of the Performance panel |
| `new:28` | hands-on | home | Variation: many scripts against one manager script. 100,000 scripts with a trivial `OnUpdate` take about 1.9 ms a frame on the reference machine, about 20 ns a call; a class that does not override a callback costs nothing for it, so an empty `OnUpdate` is not free: override only the callbacks you use. Evidence: `StrataTests/Perf/Budgets.json:40`, `:42` (`Perf.Scripting.TrivialUpdate100k` and `300k`, measured 1.856 and 5.745 ms); `Strata/src/Strata/Scripting/ScriptSystem.cpp:27-28`; `Strata/src/Strata/Scripting/ScriptSystem.h:54-55` |
| `new:23` | hands-on | home | Exercise, done in the editor: the field's props given ten different materials, and the Stats chip read before and after: the opaque draw calls stay as they were, because draws follow the mesh, its level of detail and the pipeline state, not the material. Evidence: `Strata/src/Strata/Renderer/SceneDrawKey.h:9-13`; `StrataTests/Perf/Budgets.json:155` (10,000 materials drawn in one opaque draw call); `StrataTests/src/Renderer/GPURenderSceneTests.cpp:120` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Frame time in milliseconds and frames per second | `start/what-an-engine-is` | must |
| Spawning a prefab from a script | `make/scripting-scene` | must |
| Importing a model | `make/assets` | must |
| The Graphics Quality presets and the project's page | `make/quality` | must |
| Running the exported game from a terminal with options | `make/export` | must |
| Mesh renderers and their Cast Shadows | `make/scenes-entities` | must |
| A world's cells and streaming | `make/large-worlds` | helps |
| Vsync on the settings screen | `make/menus` | helps |
| An Animator and its Culling Mode | `make/animation` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template with the
book's tutorial asset pack's prop prefab (a CC0 rock with its credit) and a small hut of built-in cubes to hide behind;
a copy of the Open World sample for the streaming section; the exported game of the same project for the last section.

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
| critic-make-b2-16 | should | missing-item | `make/performance` (the exported game's section; `worlds-runtime:408`, `worlds-runtime:481`) | The step opens `run.csv` "in a spreadsheet program" and the figure plots it, but G0's list holds no spreadsheet program and no CSV file, and no page of the book teaches either. | One paragraph where the step is: a CSV file is a table written as text, a row per line and commas between the columns; a free program opens it (LibreOffice Calc, or a spreadsheet in the web browser); select the frame-time column and insert a line chart. About 120 words, and no Assumes row, since no page teaches it. | `allocation/make-b2.md:593-595`, `:642-643`; `style.md:39-73` (G0's lists); a search of `allocation/start.md`, `make-a.md`, `make-b1.md` and `basics-a.md` for "csv" and "spreadsheet" finds nothing |
