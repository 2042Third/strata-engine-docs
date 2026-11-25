# Brief: `draw/entities-to-draws`

| Field | Value |
| --- | --- |
| Title | From entities to draw calls |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `gpu/frame-tour`, `world/scene-graph` |
| From | render-scene; the CPU path and the GPU-driven path at a glance |
| Unit | `plan/allocation/draw.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `draw/entities-to-draws` — From entities to draw calls

**Covers.** The page starts from what the reader sees: the Showcase sample open in the editor, with the Scene view's
**Stats** chip turned on. The overlay counts the visible proxies, the draw calls and instances they became and the
bytes uploaded, and a still frame uploads no instance at all (the writer takes the sample's numbers from a capture at
the pin, never from memory). The page asks what had to happen between the entities and the GPU. First the
naive answer: walk every entity each frame and issue one draw per mesh. It breaks twice: the walk costs time in
proportion to the whole scene, and every draw costs the CPU a driver call and the GPU a change of state. Then the
ideas, in this order. What a draw call is and why its count matters (instancing, merged geometry and indirect draws
named, as answers). Retained against immediate scene representations: a persistent record per drawable entity, kept
current from change signals, against walking the scene each frame, and the GPU scene as the third answer. A table
compares the three and names engines that use each. Strata's choice: retained render proxies in a render scene, culled,
batched into instanced draws, on two paths, the CPU path (the reference and the fallback) and the GPU-driven path (the
default where the device can do it). The two paths must agree pixel for pixel, and parallel work is merged in chunk
order, so the result never depends on the number of threads; this is a design constraint of the whole part.

Two diagrams are the part's map: "entity to pixels" (who owns which data, on which thread) and the frame's extraction
timeline in two lanes, with each stage linked to the page of this part that explains it. The page ends with the frame's
numbers: what each line of the Stats overlay measures and which stage makes it, and the same numbers read as
`renderStats` from `viewport.capture` (the complete command line to paste, one sentence on what it does, a link forward
to `editor/commands`). Common mistakes: thinking the triangle count is the only cost; thinking fewer draw calls is
always faster. At the end the reader can name the stages from an entity to a draw, read the Stats overlay and
`renderStats`, and say which page of the part explains each number.

**Leaves out.**

- The render scene's records and code → `draw/render-scene`
- How the visible set is found → `draw/bounds-culling`
- Sort keys, batches and indirect arguments → `draw/batching`
- The GPU-driven path and its mode switch → `draw/gpu-driven`
- The passes of the frame and what each draws → `gpu/frame-tour`
- Every `renderStats` key and `SceneRendererStats` field in one table → `reference/renderer`
- Making a game draw fast, for game makers → `make/performance`

**Fit.** `fits`: about 3,100 words against M (3,000). Three concepts with the approaches table take the most, then the
two diagrams and the reading of the frame's numbers.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-scene:215` | concept | home | What a draw call is and why its count matters; the answers engines use |
| `render-scene:221` | concept | home | Retained against immediate scene representations, the GPU scene; "cost follows change and view" |
| `render-scene:331` | concept | home | Two paths that must agree, chunked work merged in order: agreement as a design constraint |
| `render-scene:383` | figure | home | The frame's extraction timeline in two lanes, the CPU path and the GPU-driven path |
| `render-scene:388` | figure | home | Entity to pixels: components, signals, proxy, instances, GPU copy, draw list, vertex shader |
| `render-scene:184` | feature | home | The Scene view's Stats overlay (`ViewportToolbar::DrawStatsOverlay`): its lines at `StrataEditor/src/Panels/ViewportToolbar.cpp:117-131`, a few of the values of `SceneRendererStats` (not most of its fields), and what each line counts |
| `render-scene:181` | feature | home | `renderStats` in `viewport.capture` and `editor.state`: the keys grouped by the stage that makes them |
| `render-scene:522` | hands-on | home | Read a frame's statistics: capture a sample and explain each group of `renderStats` |
| `render-scene:123` | feature | link | The `GPUDriven` mode switch, named; its home is `draw/gpu-driven` |
| `render-scene:30` | feature | link | The render proxy, named; its home is `draw/render-scene` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a draw command records: a pipeline, bindings, a range of vertices and indices; command submission | `gpu/how-a-gpu-frame-works` | must |
| The passes of the scene renderer's frame, the depth prepass and forward shading | `gpu/frame-tour` | must |
| Entities, components and the scene's registry | `world/ecs` | must |
| Change signals and the transform contract | `world/scene-graph` | must |
| The CPU and the GPU working on different frames | `start/what-an-engine-is` | helps |
| Deterministic parallel work: ordered records, fixed chunks, serial publish | `core/jobs` | helps |
| Reading and running an editor command | `start/how-to-read` | helps |
| Commands are the API (linked forward from the command line the page gives) | `editor/commands` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
