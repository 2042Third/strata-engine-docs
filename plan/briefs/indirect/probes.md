# Brief: `indirect/probes`

| Field | Value |
| --- | --- |
| Title | Reflection probes |
| Kind | I |
| Size | XL |
| Tracks | E |
| Needs | `indirect/seam`, `image/pre-exposure`, `assets/residency`, `basics/math-geometry`, `draw/mip-streaming` |
| From | render-indirect ch. 5; 1.6 (box projection, blending, the probe cache and conversions, the bake and its pre-exposure, times of day) |
| Unit | `plan/allocation/indirect.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `indirect/probes` — Reflection probes

**Covers.** The job: local reflections and ambient light inside boxes, from captures baked in the editor. The page
holds the component, the renderer's gather per frame, the probe cache, the GPU conversion of a capture, the shader's
blend and box projection, and the bake. The sky's image light is `indirect/ibl`'s, screen-space reflections are
`indirect/ssr`'s.

The problem section: a reflection of the distant sky is wrong inside a room (the parallax problem); box projection
(Lagarde and Zanuttini 2012, "parallax-corrected cubemaps") fixes it for box-shaped rooms; overlapping probes blend; a
probe is baked, not captured while the game runs; priorities decide overlaps; cube arrays hold many probes. A table
compares static cube maps, parallax-corrected boxes, clustered probe lists, run-time capture and irradiance volumes. The
map is the cache diagram: up to 16 slots in a cube array, chosen least recently used, two conversions a frame, and the
takeover after a change of resolution. The contract is six rules: probes are baked in the editor, never at run time, and
a bake draws no sun disk and no lights' highlights; a bake renders where the probe stands now; a bake replaces only its
own earlier capture and trashes it in the same undo step; captures are held whole until converted; conversions are
spread, two a frame, in interactive renderers; nothing blocks (a capture not loaded lights nothing). A toy version is
box projection by hand in about 30 lines (exercise E6).

The real code, in data order: the component (`Capture`, `Extents`, `BlendDistance`, `BoxProjection`, `Intensity`,
`Priority`); `GatherReflectionProbes` and `IsStronger` (active probes with a capture, a frustum test of the bounding
sphere, priority first, then the smaller box, then the entity; non-finite transforms refused); the cache, its slots and
`acquireSlot`; the residency holds (`hold`, `holdWhole`, `ReleaseStaleReflectionProbeHolds`), because nothing draws a
capture and the streamer would never raise its levels; `ConvertReflectionProbes` (equirectangular to a scratch cube, its
levels, the six prefiltered levels by `GetProbePrefilterSamples`, then the SH projection); the SH projection itself
(texel solid angles, a shared-memory reduction, band factors 1, 2/3 and 1/4: Ramamoorthi and Hanrahan's pi, 2 pi/3 and
pi/4 divided by pi, because the probes store irradiance over pi); the shader (`ToProbeBox`, `GetProbeWeight`,
`GetProbeLookup`, two probes blended, the stronger over the weaker). Then the bake: `lighting.bakeProbes` renders with
its own renderer six 256-texel views of 90 degrees with HDR output and the probe-capture mode (`MaterialParams.w`: the
lights' diffuse light only), at a power-of-two pre-exposure, assembles a 1024x512 equirectangular `.hdr` on jobs, writes
it on an I/O job, imports it to `Assets/Lighting/<scene>/<id>.hdr` and records one undo step. What a bake sees and waits
for: its renderer (`ForBake`) takes Medium's values as Custom, without TAA, texture streaming or spreading, so a bake
never depends on a person's Graphics Quality, and a capture holds no global illumination (Medium's row is Off) and no
screen-space reflections (Medium's Checkerboard needs TAA); each probe's six views are rendered again every frame until
nothing they show is pending, for at most two minutes, after which the result says `complete: false`; the background is
the primary camera's clear color; a scene change or Play before the import ends the bake with nothing changed. Each bake
adds a bounce (the Showcase bakes eight times); a set of probes per time of day is switched with `SetActive` (the how-to
is `make/reflections`'). The bake is a step only a command can do on this track: the page gives the whole line to paste,
one sentence on what it does, and a link forward to `editor/commands`.

What Strata does not do: probes captured while the game runs, and a gizmo for a probe's box (the Scene view draws no box
for its `Extents`; exercise E5's probe-weight view shows a box's reach). Alternatives, tests
(`GPU.SceneRenderer.ReflectionProbes`, `GPU.Editor.Lighting`, `Editor.Lighting`) and changing it safely (bakes through
commands, the trash, undo) follow, with a trace of one bake through its four stages. What went wrong before: 0.7.0's
bakes drew the sun disk and the lights' highlights, shown from the v0.7.0 baseline set. Figures: a probe on and off in
the Showcase hut, box projection on and off, `BlendDistance` 0 against 1 m, 128 against 256 texels, the bake with and
without the sun disk, bakes 1, 2 and 8, and the Cornell box lit by a baked probe against the reference. The reader can
place, bake and debug probes and change their code.

**Leaves out.**

- The filter chain the conversion reuses → `indirect/ibl`
- Where the probes' light meets SSR and the sky in the shader → `indirect/seam`
- Placing probes, fitting boxes and times of day in a game → `make/reflections`
- Holds, residency and why a texture's levels rise → `assets/residency`, `draw/mip-streaming`
- Pre-exposure as a mechanism → `image/pre-exposure`
- Commands, undo steps and the trash in general → `editor/commands`, `editor/undo`, `editor/trash-references`
- The `ReflectionProbeResolution` row among the presets → `image/quality-settings`

**Fit.** `fits`: about 7,300 words against XL (8,000). The renderer's half (gather, cache, holds, conversion, SH
projection, shader) and the editor's bake with what it sees and waits for take the most words, beside seven pictures
and four diagrams.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-indirect:286` | concept | home | Local reflections: the parallax problem, box projection, blending, baking, priorities, cube arrays; Strata's choices (editor bakes, at most 16 per view, two blended per pixel, LRU slots, equirectangular captures converted at run time); errors: baking the sun disk or highlights, a box that does not fit the room, expecting probes to update at run time |
| `render-indirect:118` | feature | home | `ReflectionProbeComponent` and `c_MinExtent` (`Strata/src/Strata/Renderer/RendererComponents.h:153-170`) |
| `render-indirect:119` | feature | home | The gather and ranking per frame: priority, then the smaller volume, then the entity; at most `MaxReflectionProbes` |
| `render-indirect:120` | feature | home | The shader's two-probe blend over at most 16 box tests, with `GetProbeWeight` |
| `render-indirect:121` | feature | home | Box projection: the ray's exit from the box, looked up from the box's center |
| `render-indirect:122` | feature | home | SH irradiance: nine RGB coefficients per slot from the cube's 32-texel level, read by `EvaluateProbeIrradiance` |
| `render-indirect:123` | feature | home | The probe cache: an RGBA16F cube per slot at `ReflectionProbeResolution` (128 Low and Medium, 256 High and Ultra), six levels, LRU reuse, made with the first probe in view, kept while the scene has a probe with a capture (in view or not), released when it has none; out of view only the stale holds are let go (`Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:200-207`, `:234-243`; `Strata/src/Strata/Renderer/SceneRenderer.h:272-275`) |
| `render-indirect:124` | feature | home | The residency hold: High priority, held whole until converted, then released to its mip tail |
| `render-indirect:125` | feature | home | The GPU conversion chain, at most two a frame with `SpreadLightingUpdates` |
| `render-indirect:126` | feature | home | The resolution takeover: new cubes filled beside the shown ones, swapped once every probe in view is converted |
| `render-indirect:127` | feature | home | The bindings: SRV 9 the cube array (a black one-slot array without probes), SRV 10 the probe buffer |
| `render-indirect:128` | feature | home | The statistics `ReflectionProbes`, `ReflectionProbeConversions`, `ReflectionProbesPending` |
| `render-indirect:129` | feature | home | The bake `lighting.bakeProbes` from end to end (own renderer, six views, pre-exposure, assembly, import, one undo step that trashes the previous bake); what its renderer sees and waits for is `new:22` |
| `new:22` | feature | home | What a bake sees and waits for: `ForBake` takes Medium's quality values as Custom, with no TAA, no texture streaming and no spreading, so a bake never depends on a person's Graphics Quality; so a capture holds no global illumination (Medium's row is Off) and no screen-space reflections (Medium's Checkerboard needs TAA); each probe's six views are rendered again every frame until nothing they show is pending (assets, proxies, shadow views, probe conversions, poses), at most two minutes, after which the result says `complete: false`; the background is the primary camera's clear color; a scene change or Play before the import ends the bake with nothing changed. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:261-277`, `:3063`, `:3073`; `Strata/src/Strata/Renderer/RendererQuality.cpp:52`, `:54`; `StrataEditor/src/Editor/EditorLightingCommands.cpp:59`, `:184-210`, `:360`, `:403-407`, `:931-933`; `Docs/DeveloperGuide.md:4087-4088`, `:4968` |
| `render-indirect:130` | feature | home | Bounces by re-baking: each bake adds a bounce |
| `render-indirect:131` | feature | home | The times-of-day pattern, as the mechanism (one probe set per time, `SetActive`); the how-to is `make/reflections`' |
| `render-indirect:89` | feature | home | The probe-capture mode (`MaterialParams.w`, `LightSurface`): a bake keeps the lights' diffuse light only; taught with the bake, where a reader looks for it |
| `render-direct:63` | feature | home | The probe-capture mode as the light area lists it: `MaterialParams.w` 1 sets `LightSurface`'s specular weight to 0 (`Strata/shaders/Scene/Forward.frag.slang:84-103`); one home with `render-indirect:89`, here with the bake rather than on `indirect/seam`, because it changes the lights' direct light in a capture, not the indirect light's join |
| `render-indirect:341` | code | home | `Strata/shaders/IBL/ProbeIrradiance.comp.slang:42-87`: SH-9 projection with texel solid angles and a shared-memory reduction; with the basis at `Strata/shaders/Include/SphericalHarmonics.slang:6-17`; the band factors divided by pi |
| `render-indirect:352` | code | home | `Strata/shaders/Include/ReflectionProbes.slang:54-125`: the box-local transform, the weight, box projection and the two-probe blend |
| `render-indirect:353` | code | home | `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:193-260`: the gather with its validation of transforms; `IsStronger` at lines 59-67 |
| `render-indirect:354` | code | home | `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp:451-506`: a capture's conversion chain reusing the sky's pipelines |
| `render-indirect:355` | code | home | `StrataEditor/src/Editor/ProbeBake.h:19-47`: what a bake is: face cameras, equirectangular assembly, the power-of-two pre-exposure, the staging folder's lifetime |
| `render-indirect:701` | open | home | Settled at the pin: in `GatherReflectionProbes` (193-429) the lambdas are `findSlot` 260-268, `holdsConverted` 269-273, `acquireSlot` 279-299, `hold` 300-311, `holdWhole` 313-319 and `convert` 320-334 of `Strata/src/Strata/Renderer/SceneRendererReflectionProbes.cpp`; the page quotes the slot and hold lambdas from these lines |
| `render-indirect:390` | figure | home | Diagram: box projection in a room, the probe at the center, the reflected ray hitting a face, the lookup from the center |
| `render-indirect:392` | figure | home | Diagram: two overlapping boxes, the blend ramps, stronger over weaker |
| `render-indirect:393` | figure | home | Diagram: the cache, 16 slots, LRU, two conversions a frame, the takeover |
| `render-indirect:395` | figure | home | Diagram: the bake's timeline (six renders, readback, assembly on jobs, write on an I/O job, import, one undo step, trash) |
| `render-indirect:439` | figure | home | Off and on: a probe in the Showcase hut (toggled with its entity) |
| `render-indirect:441` | figure | home | Box projection on and off (`lookdev.patch` uses a probe without it) |
| `render-indirect:442` | figure | home | Sweep: `BlendDistance` 0 against 1 m on two overlapping boxes with different captures |
| `render-indirect:443` | figure | home | Sweep: `ReflectionProbeResolution` 128 against 256 on a mirror ball |
| `render-indirect:444` | figure | home | Crop, before and after: a bake with the sun disk (0.7.0, from the v0.7.0 baseline set) against one without (`lookdev.patch`, crop `patch`) |
| `render-indirect:445` | figure | home | Sweep: bakes 1, 2 and 8 times, bounces adding up |
| `new:8` | figure | home | The Cornell box lit by one baked probe, in a slider with the path-traced reference of `indirect/problem` (`new:2`): the probe's SH irradiance as a coarse bounce (the bake sees the glowing panel, so the capture carries its light); the figure is captured in play (its `play` field), so no preview lighting is added, and its `complete` asserts `/previewLighting` false (pipelines.md §5.2, §5.3). Evidence: `Tools/LookDev/LookDevScene.json:253-268` (the box, which holds no probe: the recipe adds one and bakes it, `StrataEditor/src/Editor/EditorLightingCommands.cpp:872`) |
| `new:9` | not-done | home | No reflection probes captured while the game runs. Evidence: `Docs/Roadmap.md:943` ("probes are baked, so a moving sun does not relight them") and `:947` ("run-time probe capture" left for later); `Docs/Releases/0.7.0.md:410-411` |
| `new:23` | not-done | home | No gizmo for reflection probes: the Scene view draws no box for a probe's `Extents`, so a box is fitted by the walls' sizes and checked after a bake by its reflections; the page names it under "What Strata does not do" and links exercise E5, whose probe-weight view shows a box's reach. Evidence: `Strata/src/Strata/Renderer/SceneGizmos.cpp:224-345` draws lights and cameras; `git grep -n "\.Gizmo(" 822a7a46 -- Strata/src StrataEditor/src` finds only the colliders and the character controller (`Strata/src/Strata/Physics/PhysicsComponents.cpp:143-184`) and the call that draws them (`Strata/src/Strata/Renderer/SceneGizmos.cpp:176`); `git grep -l ReflectionProbeComponent 822a7a46 -- Strata/src StrataEditor/src` names no gizmo or viewport file |
| `render-indirect:496` | rule | home | Probes are baked in the editor, never at run time; a bake draws no sun disk and no lights' highlights |
| `render-indirect:498` | rule | home | Bake where the probe stands now (`Scene::GetWorldTransform`, not the cached matrix) |
| `render-indirect:500` | rule | home | A bake replaces only its own earlier capture and trashes it in the same undo step |
| `render-indirect:502` | rule | home | Captures are held whole until converted, and released after |
| `render-indirect:504` | rule | home | Conversions are spread, two a frame, in interactive renderers, not in bakes and captures |
| `render-indirect:520` | rule | home | No blocking: a capture not loaded lights nothing and only captures wait for it; GI pending shows today's light (named again on `indirect/gi-cascades`) |
| `render-indirect:550` | hands-on | home | E5: a probe-weight view behind a debug view |
| `render-indirect:551` | hands-on | home | E6: box projection by hand, checked against `GetProbeLookup` (the toy version) |
| `new:24` | hands-on | home | Exercise (trace it yourself, R32, D27): one bake followed from the command to the probe's new capture through its four stages (Render, Encode, Write, Import): `RenderNextProbe` renders the six views until nothing is pending, `PollBake` moves the stages on each frame, and the solution names the function and the thread of each stage. Evidence: `StrataEditor/src/Editor/EditorLightingCommands.cpp:85-91` (the stages), `:184-221` (`RenderNextProbe`), `:397-445` (`PollBake`) |
| `render-indirect:600` | term | home | Reflection probe |
| `render-indirect:601` | term | home | Capture and bake, two entries |
| `render-indirect:602` | term | home | Influence box, extents and blend distance, three entries |
| `render-indirect:603` | term | home | Box projection (parallax correction) |
| `render-indirect:604` | term | home | Probe priority |
| `render-indirect:605` | term | home | Probe cache and slot, two entries |
| `render-indirect:607` | term | home | HDR output and ProbeCapture, two entries |
| `render-indirect:568` | term | use | The cube array, defined on `indirect/ibl` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The forms of the seam and the probes' place in the stack | `indirect/seam` | must |
| The filter chain and filtered importance sampling | `indirect/ibl` | must |
| Spherical harmonics and texel solid angles | `basics/math-sphere` | must |
| Rays against boxes | `basics/math-geometry` | must |
| A frustum test of a bounding sphere | `draw/bounds-culling` | must |
| ECS views over components and the world transform | `world/ecs` | must |
| Resolving an asset with a priority, every frame | `draw/asset-requests` | must |
| Residency, holds and pins | `assets/residency` | must |
| Resident mip levels of a streamed texture | `draw/mip-streaming` | must |
| Power-of-two pre-exposure | `image/pre-exposure` | must |
| Jobs and I/O jobs | `core/jobs` | must |
| Reading back a render target | `gpu/readback-timing` | must |
| Importing an HDR texture | `assets/importing` | helps |
| Editor commands and one undo step per change | `editor/commands` | helps |
| The trash | `editor/trash-references` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `box-projection-parallax-correction` | Box projection (parallax correction) | - |
| `probe-priority` | Probe priority | - |
| `reflection-probe` | Reflection probe | - |
