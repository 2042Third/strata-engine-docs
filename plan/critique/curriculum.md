# Critique of the plan: the curriculum editor

Lens: the book's architecture. Parts and their order, the tracks, the prerequisite graph, "one home per concept", the
kinds of page, sizes, the balance between engines in general and Strata, the master checklist of
`research/curricula.md` section 1 item by item, and the apparatus a textbook has (running example, capstone, review
chapters, glossary, index, objectives that can be tested).

Read: all nine plan files, `research/curricula.md` in full, section 8 ("Proposed chapters", with each chapter's
prerequisites) of all 19 inventories, sections 2 of `gamedev`, `assets`, `render-core`, `render-indirect`,
`foundation`, the "not in Strata" lists of `animation`, `audio-input`, `render-direct`, `render-image`, and the engine's
`Docs/Plans/Wave8/plan.md` (sections 1, 4.5) at the pin. Nothing in the engine was changed, built or run.

Severity: **blocker** (the book fails its goal or the process breaks), **major** (a reader or the process is clearly
hurt), **minor** (worth fixing).

Contents:

1. Findings (ranked)
2. The prerequisite graph: every violation found, with its evidence and fix
3. "One home per concept": rows to add and rows to change
4. The master checklist of `curricula.md` section 1, item by item
5. The corrected list of parts
6. Exact outline rows: new, split, merged, moved and retitled pages
7. The three tracks, written out
8. What I did not check

---

## 1. Findings

### F1 (blocker). The outline has no per-page prerequisites or tracks, and the part-level prerequisites are wrong in 15 of 18 engine parts

*Where:* `outline-1.md` to `outline-4.md`, every table (columns `id | Title | Kind | Size | From`); the
"Prerequisites" line above each part; `book.md` "Tracks" ("Each subsystem part is readable once its prerequisites
(listed on its first page) are read"); `site.md` "strips" plugin ("checks … that prerequisites exist and form no
cycle"); `process.md` "Novice review … Reads only the page and its prerequisites".

*Problem.* Three mechanisms of the plan depend on per-page data the outline does not hold:

- the front matter's `prerequisites:` and `tracks:` (style.md), which drive the top strip, the per-track "next" links
  and the novice review's reading list;
- the track navigation of site.md ("next and previous follow the reader's track");
- the waves of process.md ("an order where prerequisites are written before the pages that need them").

So every writer invents a page's prerequisites and tracks, the novice reviewer's reading list is chosen by the writer
it is meant to check, and nobody can compute the waves. The only check (site.md) is "no cycle", which a graph can pass
while every second edge points forward. curricula.md 3.0 proposed the right check: "every linked page comes earlier in
every track that includes this one"; the plan dropped it.

The part-level lines that do exist are incomplete or wrong in `world`, `assets`, `gpu`, `draw`, `light`, `indirect`,
`image`, `physics`, `animation`, `audio`, `input`, `ui`, `worlds`, `editor`, `engineering` (the evidence for each is
in section 2: the inventories' own chapter prerequisites contradict them). The E track's promise "then any subsystem
part" is false as the outline stands: about 45 pages need a page that comes later on every track.

*Proposal.*

1. Add two columns to every outline table: **Needs** (ids of the page's prerequisites, decided now, at most five,
   transitive ones left out) and **Tracks** (`G`, `E`, `B`, any combination). Section 7 lists the track sets.
2. Add to the strips plugin: for every track, every prerequisite of a page on that track comes earlier on that track
   (the curricula.md 3.0 check). A page may link forward in prose; a forward *prerequisite* fails the build.
3. Allow "any of" prerequisites in the schema (`prerequisites: [[make/cpp-for-scripts, basics/cpp]]`), needed where a
   game maker and an engine builder arrive by different pages.
4. Fix the order (F2 to F6) before the pilot, because two pilot pages move or change (`core/time`, `basics/math-vectors`).
5. Derive the waves of process.md from a topological sort of the Needs column (F20).

### F2 (major). The editor's commands are taught in part 18, but they are the API that every tutorial, figure and test of the book uses, and six earlier pages need them

*Where:* `book.md` "Parts" row 18; `outline-4.md` part 18 ("Chapters 1 to 15 are the editor without UI, 16 to 32 its
interface"); `style.md` "tutorial: … every step says what to do in the editor's UI and, in a second tab, the command
that does the same".

*Problem.* Pages that need `editor/commands` (and some `editor/undo`, `editor/saving`) but come before it on every
track: `input/simulated` (audio-input §8 ch. 13: "Prereq: … editor command system"), `animation/editor` (animation
ch. 13: "editor commands"), `worlds/editing` (worlds-runtime ch. 7: "editor commands and undo, document saver"),
`indirect/probes` (render-indirect ch. 5: "editor commands (other area)"), `ui/testing` (gameui ch. 9: "editor
automation chapter"), `engineering/test-kinds` (build-test ch. 8: "editor commands chapter for command scripts"). Every
E tutorial before part 18 (`world/tutorial-component`, `gpu/first-triangle`, `assets/extending`) shows commands in its
second tab without the reader knowing what a command is.

*Proposal.* Split part 18 along the line the outline already draws. Pages 1-15 become part **The editor's core**
(`editor`), placed right after *Assets* (it needs `world/reflection`, scene documents, prefabs, `core/jobs`,
`assets/references`, all earlier then). Pages 16-32 become **The editor's interface** (`editor-ui`), late, where part
18 is now. Rows: section 6. Also give "what an editor command is" a use-level home in `make/editor-tour` (F7).

### F3 (major). *Assets* comes before *The GPU*, but four asset pages need the GPU part, one of them a page whose home is in the GPU part; and three *Scenes* pages need the assets part

*Where:* `book.md` "Parts" rows 4-6; `outline-2.md` parts 4-6; `book.md` home row "Upload queue and staging
(mechanism) | gpu/upload-queue | assets/uploads".

*Problem.*

- `assets/uploads` (part 5) comes before the home of its mechanism `gpu/upload-queue` (part 6). assets ch. 9 prereq:
  "GPU command submission basics (rendering primer)".
- `assets/textures`: "basic graphics (texture sampling) from the rendering primer" (assets ch. 4).
- `assets/models-gltf`: "meshes from the rendering chapters" (assets ch. 5) → `gpu/geometry-pool`.
- `assets/mip-streaming`: "the render scene chapter for view reports" (assets ch. 10) → `draw/render-scene`,
  `draw/visibility-feedback` (part 7).
- The other way: `world/serialization` needs "asset pipeline basics (handles, loaders), job system" (scene-ecs ch. 8);
  `world/prefabs` and `world/sub-scenes` build on it; `assets/packs-export` needs cooked scenes. So world ↔ assets
  interleave.
- Part 6's own prerequisites do not need assets at all (`basics/math-vectors`, `basics/color`, `core/frame-loop`).

*Proposal.* Order: `world` (8 pages: the ECS proper) → `gpu` → `assets`, with `world/serialization`,
`world/prefabs`, `world/sub-scenes` moved into *Assets* after `assets/loading` (as `assets/scene-documents`,
`assets/prefabs`, `assets/sub-scenes`; part retitled "Assets and scene documents"), and `assets/mip-streaming` moved
to the end of *Drawing a scene* as `draw/mip-streaming`. The alternative that keeps `world` whole (gpu → assets →
world) works too but puts the ECS after 27 rendering and asset pages, which hurts readers who want physics or
scripting.

### F4 (major). The rendering parts point forward six times, and two of their homes form a cycle

*Where:* `book.md` home rows "BRDF table, split sum | indirect/ibl | light", "Energy conservation, white furnace |
indirect/energy | light", "Debug views and measuring light | indirect/measuring-light | light, image", "Sky as a light
source | light/sky | indirect", "Skinning … GPU side: draw/skinned", "Motion vectors | draw/motion-vectors | image";
`outline-3.md` line 3-4 ("Every page of parts 8 to 10 has figures … its debug view"); part 9 prerequisites "part
`light` up to `light/brdf`".

*Problem.*

- **Cycle:** `light/brdf` is render-direct ch. 3 "The BRDF in code": "GGX, Smith, Schlick, Lambert, the BRDF table,
  energy compensation, specular AA … verify with a furnace". Its homes are `indirect/ibl` and `indirect/energy`, whose
  part needs `light/brdf`. render-indirect §2 item 7 confirms energy compensation applies "everywhere image and direct
  specular appear": it is a direct-light topic.
- **Debug views** are promised on every page of parts 8-10, and explained on the last page of part 9
  (`indirect/measuring-light`, a how-to: style.md says a how-to has "No theory", so it cannot be a concept's home).
- `light/sky` needs "IBL overview (link to the reflections chapter)" (render-direct ch. 10) → `indirect/ibl`.
- `draw/occlusion` needs "shadow cascades (shadows area)" (render-scene ch. 10) → `light/sun-shadows-1`.
- `draw/skinned` needs "animation basics" (render-scene ch. 12) → `animation/skinning`, part 12.
- `draw/motion-vectors` needs "TAA concept (post area)" (render-scene ch. 13) → `image/taa`, part 10.
- `indirect/ssr` needs "motion vectors and TAA (other area)" (render-indirect ch. 7) → `image/taa`, part 10.

*Proposal.* Order the rendering parts `gpu → (assets, editor) → draw → light → image → indirect` and move five
pages: `indirect/measuring-light` → `light/measuring` (internals, right after `light/units-exposure`);
`indirect/energy` → `light/energy` (right after `light/brdf`; home of the BRDF table, energy compensation, the white
furnace and specular AA); `light/sky`, `light/fog` → `indirect/sky`, `indirect/fog` (right after `indirect/ibl`);
`draw/motion-vectors` → `image/motion-vectors` (right before `image/taa`); `draw/skinned` →
`animation/skinned-rendering` (right after `animation/skinning`). The cascade-occlusion section of `draw/occlusion`
goes to `light/sun-shadows-1` (allocation note). Rows: section 6.

### F5 (major). Testing is taught in the last part, but every internals page from part 3 on has a "how it is tested" section and part 0 already writes a test

*Where:* `style.md` "Shape per kind: internals … → how it is tested →"; `outline-1.md` `start/first-engine-change`
("build, change one thing, write a test, run it"); `outline-4.md` `engineering/testing` (part 20, prerequisite only
`basics/build`).

*Problem.* About 160 internals pages explain their tests in terms (doctest suites, labels, GPU context, exact-pixel,
sweeps, the feature test) that the book defines only at page 260. Also `audio/testing` needs "testing chapter"
(audio-input ch. 7) and `editor/ui-testing` needs "testing chapter" (editor-ui ch. 17), both earlier. Golden rule 2 of
the engine ("Everything ships with tests") is the engine's culture; the book teaches it last.

*Proposal.* Move `engineering/testing` (concept, L) to `core/testing`, after `core/conventions`. Keep the specific
suites (`engineering/test-kinds`, `feature-test`, `perf-lab`, `look-dev`) where they are. `start/first-engine-change`
links `core/testing` for the why.

### F6 (major). Three late subsystem pages need parts that come after them

*Where:* `outline-3.md` `physics/scale-streaming`, `input/simulated`; `outline-4.md` `worlds/editing`; `book.md` home
row "Simulated input | input/simulated | editor, automation".

*Problem.*

- `physics/scale-streaming` (part 11): "Prerequisites: 5, World partition" (physics ch. 11) → part 17. Its content
  ("reservation by the streamer") overlaps `worlds/physics-scripts` ("capacity reservation and the cook's
  MaxBodiesInRadius", worlds-runtime ch. 6): two homes for one thing.
- `worlds/editing` (part 17) needs part 18 (fixed by F2).
- `editor/stepping` (editor-core ch. 10) teaches "simulated input and `input.sequence` for deterministic tests",
  while the home of simulated input is `input/simulated`, which itself needs editor commands (fixed by F2 only if
  input comes after the editor's core).

*Proposal.* Split `physics/scale-streaming`: its first half becomes `physics/capacity` "Physics at scale:
capacities, growth and sliced creation" (I, M); the streaming half (parking, reservation, `MaxBodiesInRadius`) goes to
`worlds/physics-scripts`. Keep `input/simulated` in *Input* (after the editor's core) and move the `input.sequence`
section of `editor/stepping` to it.

### F7 (major). The home table sends game makers to internals pages, which contradicts "A game maker never has to read internals"

*Where:* `book.md` "Tracks" ("A game maker never has to read internals") and the home table rows "Interpolation of
fixed steps | world/interpolation", "Residency, pins, eviction | assets/residency", "Stepping a paused game |
editor/stepping | input, make", "Command scripts, record and replay | editor/command-scripts | automation, make",
"Simulated input | input/simulated", "Transform contract".

*Problem.* The one-home rule says other pages "say one sentence and link". The game maker needs, at use level: why a
follow camera judders unless it reads drawn poses (gamedev §2 item 17), why a one-shot sound is dropped unless the clip
is requested in `OnCreate` (gamedev item 19: residency), how to pause and step (gamedev item 23), how to write a
command script with `expect`/`until`. Each home is an internals page with engine-track prerequisites. Either the G
reader follows the link into internals, or the make page breaks the one-home rule. The table already solves this for
prefabs ("use: make/prefabs; data model: world/prefabs; instance sync: editor/prefab-instances") and launcher; it does
not generalize it.

*Proposal.* Give the home table a third column **Use-level home** (a make page that explains the concept as far as a
game maker needs it, one section at most) and a rule: a G-track page may list as prerequisite only G-track pages and
concept pages of level 1 whose own prerequisites are on the G track. Rows in section 3.

### F8 (major). "One home per concept" misses at least 20 concepts that several pages claim, and two of its rows conflict with the pilot

*Where:* `book.md` "One home per concept" table; `book.md` "Strata's design decisions, taught as decisions" (no home
named); `outline-1.md` `core/time` ("Time: delta time, the fixed step and interpolation", a pilot page).

*Problem.* Concepts taught on two to five pages with no home row: the C++ subset (`make/cpp-for-scripts` L and
`basics/cpp` XL, both read on track B); axes, handedness and units (`make/transforms-units`, `basics/math-vectors`,
`world/scene-graph`, `core/math`, `gpu/coordinates`); exposure and EV100 (`light/units-exposure` "pick an exposure
from EV100", `image/exposure` "manual exposure and EV100", `make/lighting`, `make/look`); pre-exposure
(`light/units-exposure` "why the HDR target needs a pre-exposure", `image/pre-exposure`); HDR (`basics/color`,
`light/units-exposure`, `image/why-post`); exporting (`make/export`, `assets/packs-export`, `worlds/export`);
immediate against retained UI (`ui/what-game-ui-does` "retained and immediate UIs compared", `editor/immediate-mode`);
the frame map (`start/what-an-engine-is`, `core/frame-loop`, `make/script-loop`, `gpu/frame-tour`); threads
(`basics/threads`, `core/jobs` whose inventory says "threads and synchronization from zero"); the script lifecycle
(`make/script-loop`, `scripting/script-system`); hot reload (`make/first-script`, `scripting/hot-reload`,
`assets/importing`); quality rows of each feature (`image/quality-settings` against each technique page; render-image
§9 asks the planner); the camera (`CameraComponent`: projection, FOV, Primary, the physical fields used by exposure and
depth of field; render-image §9: "depth of field (Camera area?)" — no page owns it); compute shaders and atomics
(prerequisite of `draw/gpu-driven`, `light/many-lights`, `indirect/ao`, `indirect/gi-voxels` per their inventories; no
page title names compute); floating point (prerequisite of `light/units-exposure`, `image/pre-exposure`; no home);
handles against pointers; determinism; the measuring method (the design decision "trade-offs are measured on the
reference machine" has its method only in `engineering/perf-lab`, part 20).

Conflicts: `core/time`'s title claims interpolation (home `world/interpolation`) and its inventory chapter claims
"pausing and stepping" (home `editor/stepping`). The eight design decisions are "stated once … on its home page" but
no home is named, and "nothing may need history" is needed by `indirect/ao` ("Ambient occlusion without history")
before any page could have stated it.

*Proposal.* The rows of section 3; retitle `core/time` "Time: delta time, fixed steps and time scale" before the
pilot; add a Home column to the design-decision list.

### F9 (major). Track B is not defined: no badge, no order, and "Foundations in order" is a 48,000-word wall for a reader who knows nothing

*Where:* `book.md` "Readers" (Beginner: "Nothing assumed"), "Tracks" ("B — beginner. Foundations in order,
interleaved with the first chapters of track G"), "Every page carries its track badges (G, E, or both)"; `style.md`
front matter `tracks: [engine] # game, engine (both allowed)`; `book.md` Parts row 2 "B, E".

*Problem.* B has no value in `tracks:`, so no badge and no "next" link; "interleaved" is not specified. Read in order,
Foundations is about 48,000 words (computer L, cpp XL, build M, bytes M, math-vectors XL, math-rotations L, color M,
math-light L, threads L, reading-code M), including Monte Carlo and spherical harmonics, before or between the first
game pages. curricula.md 5.1.5 and 5.3 warn against exactly this ("not by a prerequisite wall"; the on-ramp is
"vectors and transforms only"). And no page teaches programming from zero: `basics/cpp` is "The C++ you need to read
Strata", `make/cpp-for-scripts` is "Just enough C++ for game scripts" (gamedev §2 item 11: classes, inheritance,
virtual functions, headers, CMake), both assume variables, functions and loops.

*Proposal.* Add `beginner` to `tracks:`; write the B sequence into book.md (section 7); add `basics/programming`
(C, XL) as B's first primer; give every basics page a "Test out" box (three questions; all right → skip), as
curricula.md 5.3 proposes for the E track.

### F10 (major). Track E never reads the editor tour, but E pages use the editor from part 4 on

*Where:* `book.md` "Tracks" ("E — engine builder. Start here, Foundations, Engine architecture, Scenes, then any
subsystem part"); `outline-1.md` part 1 "track G".

*Problem.* E tutorials have UI steps (style.md), `world/tutorial-component` ends in the Inspector (scene-ecs ch. 7:
"new component in Inspector"), `indirect/probes` bakes in the editor, `editor/*` pages assume the reader has used
the editor. curricula.md 5.3: the engine builder reads "Part II chapters 1-4 (enough to use the editor, since you must
use what you build)". `start/first-engine-change` (part 0, "all") on the other hand is not for game makers (it builds
the engine from source).

*Proposal.* Tracks `G, E` on `make/editor-tour`, `make/scenes-entities`, `make/first-script`; track `E` only on
`start/first-engine-change`; make/first-script's prerequisite "any of `make/cpp-for-scripts`, `basics/cpp`" (F1.3).

### F11 (major). "Engines in general" has almost no room: 31 concept pages against 163 internals pages in the engine parts, and the internals shape has no section for the general technique

*Where:* `style.md` "Shape per kind: internals: the job → a map → the contract → a toy version → the real code walked
through → how it is tested → how to change it safely → what went wrong before"; the outline's kinds per part.

*Problem.* Counted from the outline: parts 3-20 hold 31 concept pages (about 115,000 words of ~860,000), *Input* none,
*The image* one (S), *Drawing a scene* one, *Game UI* one. The inventories proposed some 60 chapters as "concept +
internals" (for example render-image ch. 4 "tone curves, hue skew, the five classic operators"; ch. 9 TAA "jitter,
history, reprojection, Catmull-Rom, clamping and clipping"); the outline made them internals, and the internals shape
has no place for the technique as the industry knows it or for alternatives. curricula.md 3.2 had both (item 6 "Why
it differs from the toy", item 7 "Alternatives Strata did not choose"); style.md dropped item 7, leaving only the
`:::elsewhere` aside. The owner asked for "a … textbook on strata engine and engines in general".

*Proposal.*

1. style.md internals shape becomes: the job → **the technique in general** (the problem and the standard algorithm,
   at most a quarter of the page, with a figure; skipped when a concept page of the part holds it) → map → contract →
   toy → real code → **alternatives Strata did not choose** (a table: technique, who uses it, what Strata would gain
   and lose) → tests → changing it → what went wrong before.
2. Add the concept page *Input* lacks: `input/devices-to-intents` (C, M). Section 6.
3. The concept pages of F12 (signals, numbers, game design, patterns, game AI) carry most of the remaining general
   knowledge.

### F12 (major). Topics the checklist marks [gap] have no page

*Where:* `research/curricula.md` section 1 items marked [gap]; `outline-1.md` parts 0 and 2.

*Problem and evidence* (full audit in section 4):

- **Floating point** (1.1 "representation, rounding, precision far from the origin, determinism"; needed by half-float
  targets, pre-exposure, camera-relative space, the 20 km limit, FMA determinism in `engineering/flags-portability`):
  no page.
- **Signals** (1.2 "sampling, aliasing, Nyquist, reconstruction filters, convolution, mip filtering … taught five times,
  badly, or not at all"): no page; mips (`assets/textures`), AA (`image/spatial-aa` "sampling theory light"), TAA,
  shadow filtering, audio each re-derive it. Randomness and blue noise (1.2, used by `light/sun-shadows-2`) have no
  home either.
- **Git and the debugger** (1.1 "Version control and git" [gap], 1.18 "Debuggers" [gap]; curricula 5.2 Part I "tools
  of the trade (compilers, CMake, git, the debugger)"): no page; `start/first-engine-change` and every E exercise need
  them.
- **GPU debugging** (1.9.1 "Validation layers, debug names, GPU debuggers (RenderDoc), reading a frame capture" [gap];
  render-core §2 item 4, hands-on 12 "Map a frame in RenderDoc or Nsight"): no page. LearnOpenGL's lesson in
  curricula.md: "A debugging chapter early in the rendering part".
- **Debugging the engine** (memory profiling, leak detection, crash dumps): no page.
- **Game design craft** (1.13 "the core loop, prototyping, scope, game feel, playtesting, levels" [gap]; "the brief
  says some readers never made a game"): no page.
- **Gameplay programming patterns** (1.13 GPP: State, Command, Type Object, Update Method, Object Pool, Observer, Event
  Queue): no page.
- **"Coming from Unity, Unreal or Godot"** (curricula 5.2 Part 0; Unreal adopt): no page.
- **How a GPU works as hardware** (1.9.1 "warps or waves, occupancy, memory bandwidth, why branching costs" [gap]):
  `gpu/how-a-gpu-frame-works` is about commands and frames (render-core ch. 1), not the hardware.
- **Game AI** ([S-none]): neither a page nor an entry in book.md's "What Strata does not do".

*Proposal.* Rows in section 6: `basics/numbers`, `basics/signals`, `basics/tools`, `core/debugging`,
`gpu/debugging`, `make/game-design`, `make/patterns`, `start/coming-from`, `appendix/game-ai`; retitle
`gpu/how-a-gpu-frame-works` "How a GPU works and draws a frame".

### F13 (major). The W8 marks miss the animation graph, and their granularity puts a W8 page under non-W8 pages

*Where:* `README.md` decision 5 ("areas that wave 8 still changes (local lights, area lights, global illumination)");
`outline-3.md` part 12 (no W8); `outline-3.md` `light/lights` "Lights: the sun, points and spots … W8";
`outline-1.md` `make/lighting` W8 followed by `make/look` (not W8); `book.md` "What Strata does not do": "blend trees,
animation layers".

*Problem.*

- The engine's `Docs/Plans/Wave8/plan.md` ranks `animation-graph` fifth of the wave's priorities ("really really
  important"; "first claim on tranche 2") and §4.5 lists what it brings: Blend1D, layers with bone masks, sync tracks,
  state machines as graph nodes, `.stanimator` version 2. If it lands in 0.8.0, `animation/state-machines`,
  `animation/blending`, `animation/time-events`, `animation/system`, `animation/editor`, `animation/limits`,
  `make/animation`, `make/project-platformer`, `reference/animation` and the "does not do" list change, but process.md
  writes them in phase A wave 4. The same holds, at lower probability, for `volumetric` (tranche 3; render-direct §1.9
  "volumetric stream planned in wave 8") → `light/fog`, and `editor-ux` (tranche 3, mesh ghost) → `editor/placement`.
- `light/lights` (W8, phase B) holds the sun, and the sun is a prerequisite of `light/shadow-basics`,
  `light/sun-shadows-1/2` (phase A). `make/lighting` (W8) is a prerequisite of `make/look` (phase A). Phase A would
  write pages before their prerequisites, against process.md's own rule.

*Proposal.* Mark the animation pages listed above `W8?` (wait unless the stream is cut from 0.8.0) and the "does not
do" list's animation items likewise; mark `light/fog` and `editor/placement` `W8?`. Split `light/lights` into
`light/sun` (now) and `light/local-lights` (W8); `make/lighting` into `make/lighting` (sun, sky, exposure, now) and
`make/local-lights` (W8); `make/reflections-gi` into `make/reflections` (now) and `make/gi` (W8). Rows in section 6.

### F14 (major). The make part's order points forward, its projects come at the end, and three rendering pages come before the first line of game code

*Where:* `outline-1.md` part 1, rows in reading order.

*Problem.*

- `make/gameplay-2` (position 14) covers "physics, characters, audio, animation from scripts" with "Prerequisites:
  ch. 4 and the Physics, Audio, Animation chapters" (scripting ch. 5) → `make/physics` (19), `make/animation` (21),
  `make/sound` (22).
- `make/gameplay-3` (15): "Game UI, Input actions, Quality settings" and worlds (scripting ch. 6) → `make/input` (18),
  `make/ui` (23), `make/large-worlds` (25).
- `make/look` (9) ends with "a Graphics menu" (render-image ch. 12), which needs UI and scripts → `make/ui` (23),
  `make/first-script` (11).
- `make/automated-playtests` (28) builds on automation ch. 1 "Driving the editor from outside", which the outline put
  in part 19 as `automation/outside` (not on track G as book.md defines it, though the Parts table says "E, G").
- The three projects are pages 30-32 of 33. gamedev §6 designed Coin Run as G8, after G1-G7 (editor, physics, assets,
  prefabs, scripts, lighting), the "first finished game" in the middle of the progression; curricula.md 5.2: "Project
  chapters interleaved: a first game, a mid-size game, a capstone".
- `make/lighting`, `make/reflections-gi`, `make/look` (positions 7-9, about 15,000 words of exposure, tone mapping,
  reflections and GI) come before `make/cpp-for-scripts`. A reader who has "maybe no programming" and wants "a finished
  game" meets a GI how-to before any gameplay.

*Proposal.* The reordered part in section 6 (39 rows): editor and scenes → scripts → input, physics, characters, sound,
UI, export → game design → **Coin Run** → lighting and look → animation → the script API pages after their topics →
patterns and recipes → **Tetris** → testing, automation (with `automation/outside` moved in as
`make/editor-from-outside`) → large worlds, big scenes, script builds → **the platformer** → samples.

### F15 (major). Several pages have the wrong kind, or one kind holds two

*Where:* rows below; `book.md` "Each page is exactly one kind"; `style.md` "how-to: goal → steps → variations. No
theory".

*Problem.*

- `scripting/host-api` is T ("Tutorial: adding a host function") but its inventory chapter is "internals + tutorial":
  `ResolveContext`, `HostCall`, validation and `ReportProblem`, services and layering, the X-macro table, call counters
  (scripting ch. 15). The internals of the host API then have no page.
- `make/gameplay-1/2/3` are H, L: a how-to of 5,000 words with no goal in its title and "no theory" is an API tour.
  scripting ch. 4-6 call them "reference + tutorial". The reference is generated (`reference/script-api`); these
  pages are where a game maker learns the API, so they are tutorials.
- `make/assets` is H for a reader who imports a model for the first time (Diátaxis: a how-to "assumes the concept is
  known").
- `make/reflections-gi` is H and merges three inventory tutorials (render-indirect ch. 6, 8, 11).
- `indirect/measuring-light` is H and the home of a concept (F4).
- `basics/reading-code` is H, uses "Strata's own tree as the example" and comes before `core/map`, which explains that
  tree. curricula.md 1.0 describes a guided walk ("how to follow one feature from editor click to pixel"): a tutorial.
- `automation/outside` is a T for game makers (automation ch. 1 "game developers; tutorial") inside an engine part.

*Proposal.* Split `scripting/host-api` into `scripting/host-api` (I, L) and `scripting/tutorial-host-function`
(T, M); make the gameplay pages T with goal titles; `make/assets` T; split `make/reflections-gi` (F13);
`indirect/measuring-light` → `light/measuring` (I); `basics/reading-code` → `core/reading-code` (T, after `core/map`);
`automation/outside` → `make/editor-from-outside`. Rows in section 6.

### F16 (major). Sizes that are certainly wrong

*Where:* the Size column.

| Page | Planned | Evidence | Proposed |
| --- | --- | --- | --- |
| `basics/math-vectors` | XL | foundation ch. 12 "conventions, transforms, quaternions, projections and reversed Z, frustum, AABB, rays, random numbers" plus checklist 1.2's vectors, matrices, homogeneous coordinates, projections, primitives and tests, robustness, interpolation for a reader who knows nothing; the 3D Math Primer spends ten chapters on it | split in four, L L L M |
| `physics/how-simulation-works` | XL | physics ch. 4: integration, mass and inertia, broad and narrow phase, contacts as soft constraints, sub-stepping, friction, restitution, CCD, islands and sleep, plus a toy solver | split: collision detection (L) and dynamics (XL) |
| `make/editor-tour` | M | editor-ui ch. 1 "L; ~18 screenshots" | L |
| `make/ui` | L | gameui ch. 2 (L, ~10 screenshots) + ch. 3 (M, ~4) | split: L + M |
| `image/why-post` | S | render-image ch. 1 "Size M" (HDR, the chain's order, half floats, `SanitizeHDR`, the fullscreen pass, `PostSource`) | M |
| `start/install` | S | gamedev §1.1: three platforms' archives, requirements, Unblock and quarantine, the script toolchain per platform, logs; plus the source build's short form | M |
| `make/cpp-for-scripts` | L | from no programming to classes, virtual functions, headers, CMake and compile errors (gamedev §2 item 11) does not fit 5,000 words | L only with `basics/programming` as its prerequisite (F9) |
| `core/jobs` | XL | foundation ch. 9 includes "threads and synchronization from zero", the job of `basics/threads` (L) | L once the home row (section 3) holds |

The outline's total is about 1.09 million words of written prose (282 pages; S 1,500, M 3,000, L 5,000, XL 8,000),
before reference; this report's changes add about 90,000 (new primers, concept pages, capstone, reviews) and remove
about 15,000 (merges, F21).

### F17 (major). No running example and no capstone for engine builders

*Where:* `process.md` "What a writer is given … the part's running example" (per part only); `outline-*` E tutorials
(`world/tutorial-component`, `assets/extending`, `scripting/host-api`, `editor/tutorial-command`,
`image/tutorial-post-effect`, `editor/tutorial-panel`) each stand alone.

*Problem.* Track G has three projects; track E has seven unrelated tutorials and nothing that ties them into one
change of the engine. curricula.md 5.3: "Capstone contributions as tutorials … each following the repository's skills
and checklists", and the Crafting Interpreters model of one program grown through the book. The scene-ecs inventory
already chose the E tutorial's subject: ch. 7 "follow SK end to end (WindZone or Spinner)". A per-part running example
without a book-wide one gives 23 unrelated examples.

*Proposal.*

- Book-wide running examples, named in book.md: **Coin Run** for G (seeded in `start/first-game`, finished in
  `make/project-coin-run`, the scene later pages light, give a look, a menu and an export); **WindZone** for E (created
  in `world/tutorial-component`, its force applied in a physics exercise, a gizmo in `gpu/debug-drawing`'s exercise, a
  command in `editor/tutorial-command`, a host function in `scripting/tutorial-host-function`); and **one frame of
  Coin Run** traced in a short "What happens to Coin Run here" box at the start of each engine part.
- A capstone part of three tutorials (section 6) that turns WindZone into a feature that lands: design, from component
  to pixel, then tests, the feature test, a perf budget, the review checklist and a `ci/` branch.

### F18 (major). The book lacks the apparatus of a textbook: part openers and reviews, a map, an index, a notation page

*Where:* `site.md` "Navigation" ("each part's first page says what it needs and what it gives"); `outline-4.md` part
21; curricula.md 2 (LearnOpenGL "part-ending review page", PBR "index of code identifiers", Filament "a notation table
before any equation", 5.1.4 "Publish the graph (a 'map' page)").

*Problem.* A part's needs and gifts are put on its first content page, which is a concept page with its own job. There
is no review at the end of any part (the place for cumulative exercises and the part's new terms), no published
prerequisite graph, no index (Pagefind searches words; it does not say which page *defines* `RenderScene::Sync`), no
book-wide conventions and notation page (the rendering parts use L, E, F0, α and two axis conventions), and the XL hub
`gpu/frame-tour` is read before the features and never revisited.

*Proposal.* Rows in section 6: `start/map` (generated graph and track lists), `reference/index` (generated from the
excerpt fences' symbols and the glossary's home pages), `reference/notation` (R, M); an `index` page per part (what it
needs, gives, its own small graph; generated from front matter plus one paragraph) and a `review` page for every part
of eight or more pages (generated summaries and new terms, plus five to ten cumulative exercises; for the rendering
parts, "the frame again", walking `gpu/frame-tour`'s diagram with every pass now known).

### F19 (minor). "What Strata does not do" misses items the checklist and the inventories name

*Where:* `book.md` "What Strata does not do".

*Problem.* Not listed: game AI and navigation ([S-none] 1.13); localisation and right-to-left text (1.14); in-game
consoles and console variables (1.18); frame graphs (1.9.2 [S?]; render-core: NVRHI automatic barriers); MSAA and
supersampling (render-image §2: "Strata has none"); order-independent transparency (1.9.3); volumetric fog (render-direct
§1.9 "Fog limits: no volume"); billboards and impostors (1.9.7); non-photorealistic rendering; retargeting, dual
quaternion skinning (animation glossary: "not used"), additive clips (animation §1.16), motion matching; cloth,
destruction, fluids, buoyancy (1.11); sound occlusion and reverb zones (audio-input §2: "not in Strata"), music systems
and ducking; portals (1.9.2). Also `animation/limits` and `indirect/gi-limits` duplicate the appendix: say which is the
home (the subsystem page states what is missing there; the appendix only indexes and gives the general technique).

*Proposal.* Add these to the list (each checked against the inventories, as book.md already requires) and to
`appendix/not-in-strata`; add `appendix/game-ai` (C, L) as `appendix/networking` is for networking.

### F20 (major). process.md's waves contradict its own rule "prerequisites are written before the pages that need them"

*Where:* `process.md` "Order", phase A step 5.

*Problem.* Wave 4 writes `ui` (needs `gpu/text`, wave 5), `input/simulated` and `worlds/editing` (need `editor`,
wave 6), `animation/culling` (needs `draw`, wave 5); wave 2 writes `make`, whose links go to concept homes of waves 3-5
(`world/interpolation`, `assets/residency`, `physics/why`, `ui/what-game-ui-does`); phase B writes `light/lights`
after its dependants (F13). The novice reviewer then reads only outline rows of missing prerequisites, so the check of
"used before defined" is blind exactly where pages are written out of order.

*Proposal.* Waves are the layers of a topological sort of the Needs column (F1) restricted to non-W8 pages; W8 pages
and their dependants form phase B. With the corrected parts (section 5) that gives, roughly: 1 `start`, `basics`,
`core`, `world`; 2 `make` 1-19 (to Coin Run), `gpu`; 3 `assets`, `editor`; 4 `draw`, `light` (non-W8), `image`,
`physics`, `audio`, `input`, `scripting`; 5 `indirect` (non-W8), `animation` (if the graph is cut), `ui`, `worlds`,
the rest of `make`; 6 `editor-ui`, `automation`, `engineering`, `capstone`.

### F21 (minor). The editor's interface takes 17 pages where audio and input take 6 each; three can merge

*Where:* `outline-4.md` part 18, pages 16-32.

*Problem.* Part 18 is about 127,000 words, three times *Physics* (40,500) and seven times *Audio* (18,500). Several
interface pages are thin or overlap: `editor/immediate-mode` (S in editor-ui ch. 2) and `ui/what-game-ui-does` both
compare retained and immediate UIs; `editor/ui-scale` (editor-ui ch. 5, "S-M") is a section of the design system;
`editor/shortcuts` (ch. 13, "S") and `editor/status` (ch. 14) are both about routing and feedback.

*Proposal.* Merge `editor/immediate-mode` into `editor/imgui` (retained against immediate: home `ui/what-game-ui-does`);
`editor/ui-scale` into `editor/design-system`; `editor/shortcuts` and `editor/status` into `editor-ui/shortcuts-status`
"Shortcuts, focus and feedback". The words saved pay for `audio` gaining nothing it lacks; they are better spent on
F12's primers.

### F22 (minor). Learning objectives are verbs, but nothing ties them to the questions that test them

*Where:* `style.md` front matter `learn:` ("each starts with a verb"), "Check yourself", "Exercises"; `process.md`
"Definition of done".

*Problem.* A page can state "derive the step alpha" and ask only recall questions; the definition of done requires
only that questions have answers. Teaching Tech Together (curricula.md §2) and the novice review both need the mapping.

*Proposal.* Give each `learn` line an id (`learn: [{id: alpha, text: …}]`); each Check-yourself question and exercise
names the ids it tests; the strips plugin fails a page whose objective has no question or exercise; the novice
reviewer reports per objective whether the page let them meet it.

### F23 (minor). *Start here* is ordered for the plan, not for the three doors

*Where:* `outline-1.md` part 0.

*Problem.* `start/what-an-engine-is` (the frame map, curricula.md 1.0's "spine diagram" [gap], and "where Strata sits
among engines" [gap]) comes after both 30-minute tutorials, and `start/first-engine-change` sits on every reader's path
(Parts table: track "all"). The frame map has no named home at all (F8): `core/frame-loop` is E-only internals.

*Proposal.* Order: welcome → how-to-read → install → first-game → what-an-engine-is (home of the frame map and the
survey of engines; size L) → coming-from (new) → first-engine-change (E only) → map (new).

---

## 2. The prerequisite graph: every violation found

Built from the outline's part prerequisites and the prerequisites each inventory's section 8 gives its chapters
(the outline cites those chapters in its From column). "Later" means later on every track, since E is one order.

| Page (part) | Needs | Taught at | Evidence | Fix |
| --- | --- | --- | --- | --- |
| `world/scene-graph` (4) | quaternions | `basics/math-rotations`, not in part 4's list | scene-ecs ch. 3 | add to Needs |
| `world/systems` (4) | threads, the application frame loop | `basics/threads`, `core/frame-loop`, not listed | scene-ecs ch. 4 | add |
| `world/serialization` (4) | asset handles and loaders, job system | `assets/handles-meta`, `assets/loading` (5, later) | scene-ecs ch. 8 | move after `assets/loading` (F3) |
| `world/prefabs`, `world/sub-scenes` (4) | serialization | as above | scene-ecs ch. 9, 10 | move (F3) |
| `assets/textures` (5) | texture sampling, color spaces | `gpu` (6, later); `basics/color` not listed | assets ch. 4 | gpu before assets; add `basics/color`, `basics/signals` |
| `assets/models-gltf` (5) | meshes on the GPU | `gpu/geometry-pool` (6) | assets ch. 5 | gpu before assets |
| `assets/uploads` (5) | GPU submission; its mechanism's home | `gpu/upload-queue` (6) | assets ch. 9; home table | gpu before assets |
| `assets/mip-streaming` (5) | view reports, visibility feedback | `draw/render-scene`, `draw/visibility-feedback` (7) | assets ch. 10 | move to `draw/mip-streaming` |
| `gpu/*` (6) | the Graphics engine module | `core/engine-modules`, not listed | render-core §1.2 | add |
| `draw/gpu-driven` (7), `light/many-lights` (8), `indirect/ao`, `indirect/gi-voxels` (9) | compute shaders, atomics | no home | render-scene ch. 9; render-direct ch. 5; render-indirect ch. 4, 9 | home `gpu/shaders` (retitled) and `gpu/resources-lifetimes` |
| `draw/occlusion` (7) | shadow cascades | `light/sun-shadows-1` (8) | render-scene ch. 10 | cascade section to `light/sun-shadows-1` |
| `draw/skinned` (7) | skinning | `animation/skinning` (12) | render-scene ch. 12 | move to `animation/skinned-rendering` |
| `draw/motion-vectors` (7) | the TAA concept | `image/taa` (10) | render-scene ch. 13 | move to `image/motion-vectors` |
| `light/brdf` (8) | energy compensation, furnace, BRDF table | `indirect/energy`, `indirect/ibl` (9), which need `light/brdf`: cycle | render-direct ch. 3; home table | `light/energy` after `light/brdf` |
| every page of 8-10 | debug views | `indirect/measuring-light` (9, last) | outline-3 lines 3-4 | `light/measuring` after `light/units-exposure` |
| `light/shadow-basics` (8) | projections, depth buffers | `gpu/coordinates`, not listed | render-direct ch. 6 | add |
| `light/sun-shadows-2` (8) | sampling and noise | no home | render-direct ch. 8 | `basics/signals` |
| `light/units-exposure` (8), `image/pre-exposure` (10) | floating point | no home | render-direct ch. 1; render-image ch. 3 | `basics/numbers` |
| `light/sky` (8) | IBL | `indirect/ibl` (9) | render-direct ch. 10 | move to `indirect/sky` after `indirect/ibl` |
| `light/sun-shadows-1/2` (8, not W8) | the sun light | `light/lights` (W8) | outline-3 | split `light/sun` (not W8) |
| `indirect/ssr` (9) | motion vectors, TAA | `image/taa` (10) | render-indirect ch. 7 | image before indirect |
| `indirect/measuring-light` (9) | exposure | `image/exposure` (10) | render-indirect ch. 12 | moved to light; uses `light/units-exposure` |
| `indirect/probes` (9) | editor commands (the bake) | `editor/commands` (18) | render-indirect ch. 5 | editor core before draw (F2) |
| `image/motion-blur-dof` (10) | the camera's physical fields | no home | render-image ch. 10, §9 | home `gpu/coordinates` + `basics/math-projection` |
| `physics/world-step` (11) | job system, transform contract | `core/jobs`, `world/scene-graph`, not listed | physics ch. 5 | add |
| `physics/collision-layers` (11) | project settings | `world/projects-settings`, not listed | physics ch. 8 | add |
| `physics/scale-streaming` (11) | world partition | `worlds/*` (17) | physics ch. 11 | split (F6) |
| `animation/system` (12) | job system, scene services | `core/jobs`, not listed | animation ch. 11 | add |
| `animation/editor` (12) | editor commands | `editor/commands` (18) | animation ch. 13 | F2 |
| `audio/engine` (13) | engine modules, atomics | `core/engine-modules`, not listed | audio-input ch. 2 | add |
| `audio/clips-voices-sources` (13) | asset pipeline | `assets/loading`, not listed | audio-input ch. 3 | add |
| `audio/testing` (13) | testing chapter | `engineering/testing` (20) | audio-input ch. 7 | `core/testing` (F5) |
| `input/actions` (14) | project settings, JSON | `world/projects-settings`, not listed | audio-input ch. 11 | add |
| `input/mouse-cursor` (14) | editor basics (Game view) | `make/editor-tour`, not on E | audio-input ch. 9 | F10 |
| `input/simulated` (14) | editor command system | `editor/commands` (18) | audio-input ch. 13 | F2 |
| `scripting/script-system` (15) | UI events | `ui/input` (16) | scripting ch. 13 | forward mention only |
| `ui/drawing` (16) | bindless, camera-relative space | `gpu/binding`, `draw/mirrors-camera-relative`, not listed | gameui ch. 7 | add |
| `ui/input` (16) | input actions, the script ABI | `input/actions`, `scripting/abi-sdk`, not listed | gameui ch. 8 | add |
| `ui/testing` (16) | the automation chapter | `automation/outside` (19) | gameui ch. 9 | `make/editor-from-outside`, `editor/command-scripts` |
| `worlds/physics-scripts` (17) | physics basics, scripting ABI | not listed | worlds-runtime ch. 6 | add |
| `worlds/editing` (17) | editor commands, undo, document saver | `editor/*` (18) | worlds-runtime ch. 7 | F2 |
| `worlds/runtime` (17) | the application model, the renderer | `core/first-frame`, `gpu/frame-tour`, not listed | worlds-runtime ch. 9 | add |
| `worlds/measuring` (17) | profiling | `core/profiling`, not listed | worlds-runtime ch. 10 | add |
| `editor/prefab-instances` (18) | prefab data model | `world/prefabs`, not listed | editor-core ch. 8 | add |
| `editor/stepping` (18) | simulated input | `input/simulated` (14, which needs 18) | editor-core ch. 10 | move the section (F6) |
| `editor/placement`, `editor/camera-viewport` (18) | rays, AABBs, camera math | basics math, not listed | editor-core ch. 13, 14 | add |
| `editor/scene-view` (18) | readback, the scene renderer, placement | `gpu/readback-timing`, `gpu/frame-tour`, not listed | editor-ui ch. 11 | add |
| `engineering/test-kinds` (20) | GPU, editor commands | part lists only `basics/build` | build-test ch. 8 | per-page Needs |
| `engineering/feature-test` (20) | registries, scripting | not listed | build-test ch. 9 | per-page Needs |
| `engineering/look-dev` (20) | rendering basics | not listed | build-test ch. 11 | per-page Needs |
| internals pages of 3-19 | testing concepts | `engineering/testing` (20) | style.md internals shape | `core/testing` |
| `start/first-engine-change` (0) | writing a test | `engineering/testing` (20) | outline-1 row | link `core/testing` |
| `basics/reading-code` (2) | Strata's map | `core/map` (3) | outline-1 row | `core/reading-code` |
| `make/gameplay-2` (1, pos. 14) | physics, audio, animation pages | `make/physics` (19), `make/animation` (21), `make/sound` (22) | scripting ch. 5 | reorder (F14) |
| `make/gameplay-3` (1, pos. 15) | UI, input actions, quality, worlds | `make/input` (18), `make/ui` (23), `make/large-worlds` (25) | scripting ch. 6 | reorder |
| `make/look` (1, pos. 9) | a Graphics menu: UI and scripts | `make/ui` (23), `make/first-script` (11) | render-image ch. 12 | reorder |
| `make/automated-playtests` (1) | driving the editor from outside | `automation/outside` (19) | automation ch. 2 | move into make |
| `make/script-builds` (1) | shared libraries | `scripting/shared-libraries` (E) | scripting ch. 8 | teach at use level in the page |

Cycles: `light/brdf` ↔ `indirect/energy`/`indirect/ibl` (content); `input/simulated` → `editor/commands` and
`editor/stepping` → `input/simulated` is not a cycle but a zigzag across four parts. `core/time` ↔ `world/systems`
is avoided only because `core/time` is concept and `world/systems` holds the code; keep it that way.

---

## 3. "One home per concept": rows to add and to change

New column **Use-level home** (F7): where a game maker reads it, at most one section, prerequisites on track G only.

| Concept | Home | Use-level home | Others link |
| --- | --- | --- | --- |
| The frame map (what happens in one frame) | `start/what-an-engine-is` | same | `core/frame-loop`, `make/script-loop`, `gpu/frame-tour` |
| Programming from zero | `basics/programming` | same | `make/cpp-for-scripts`, `basics/cpp` |
| The C++ of scripts (classes, override, headers, `ST_SCRIPT_CLASS`) | `make/cpp-for-scripts` | same | `basics/cpp` extends it, never repeats it |
| The C++ of the engine (ownership, RAII, move, templates, lambdas) | `basics/cpp` | — | `core/conventions` (Strata's rules only) |
| Floating point, precision, determinism of floats | `basics/numbers` | — | `draw/mirrors-camera-relative`, `worlds/why-streaming`, `image/pre-exposure`, `engineering/flags-portability` |
| Sampling, aliasing, filtering, noise, blue noise | `basics/signals` | — | `assets/textures`, `image/spatial-aa`, `image/taa`, `light/sun-shadows-2`, `audio/sound-in-a-computer` |
| Axes, handedness, units, matrix order (conventions) | `basics/math-matrices` | `make/transforms-units` | `gpu/coordinates` (Strata's API conventions), `core/math`, `reference/notation` |
| Projection, frustums, depth precision | `basics/math-projection` | — | `gpu/coordinates`, `core/math`, `draw/bounds-culling` |
| The camera (`CameraComponent`, projection, Primary, physical fields) | `gpu/coordinates` | `make/look` (image), `make/characters-cameras` (following) | `image/exposure`, `image/motion-blur-dof`, `editor/camera-viewport` |
| Handles instead of pointers (IDs, generations, UUIDs) | `world/ecs` | `make/assets` (one paragraph) | `assets/handles-meta` (asset handles only) |
| Threads, races, atomics (general) | `basics/threads` | — | `core/jobs` (Strata's job system only) |
| Determinism (what breaks it, why Strata keeps it) | `core/jobs` (parallel), `core/time` (game time) | `make/play-test-debug` | physics, animation, `input/simulated` |
| Testing (kinds, why, doctest) | `core/testing` | — | every internals page, `engineering/*` |
| Measuring (method, budgets, statistics) | `core/profiling` | `make/big-scenes-fast` | `engineering/perf-lab` (the lab only), `physics/tuning`, `worlds/measuring` |
| Debugging (debugger, logs, asserts, crash dumps) | `core/debugging` | `make/play-test-debug` | `scripting/crash-containment`, `gpu/debugging` |
| Editor commands (what one is, the Command tab) | `editor/commands` | `make/editor-tour` | every tutorial |
| Interpolation of fixed steps (change: add use level) | `world/interpolation` | `make/characters-cameras` | physics, draw, editor |
| Residency, pins (change: add use level) | `assets/residency` | `make/sound` (request in `OnCreate`), `make/levels-saves` (loading screens) | draw, worlds, ui |
| Stepping a paused game (change) | `editor/stepping` | `make/play-test-debug` | `core/time` gives one sentence; input |
| Command scripts (change) | `editor/command-scripts` | `make/automated-playtests` | automation |
| Simulated input (change) | `input/simulated` (holds `input.sequence`) | `make/automated-playtests` | editor, automation |
| Compute shaders, dispatches, UAV barriers, atomics | `gpu/shaders` (retitled), barriers in `gpu/resources-lifetimes` | — | draw, light, indirect |
| HDR targets | `basics/color` (what), `image/why-post` (the chain and `SanitizeHDR`) | `make/look` | light |
| Physical units, EV100, manual exposure | `light/units-exposure` | `make/lighting` | `image/exposure` (metering and adaptation only) |
| Pre-exposure | `image/pre-exposure` | — | `light/units-exposure` says one sentence |
| Debug views and the light meter (change: was a how-to) | `light/measuring` | `make/lighting` | every rendering page |
| BRDF table, energy compensation, white furnace, specular AA (change) | `light/energy` | — | `indirect/ibl` (the split sum's prefiltered half only) |
| Sky as a light source (change) | `indirect/sky` | `make/lighting` | `light/sun` |
| Quality rows of a feature | the feature's page (its row and cost) | `make/look` | `image/quality-settings` (the system: presets, traits, players' options) |
| Immediate against retained UI | `ui/what-game-ui-does` | — | `editor-ui/imgui` |
| Exporting | `worlds/export` (the export) | `make/export` | `assets/packs-export` (the pack format only) |
| Script lifecycle and order | `make/script-loop` | same | `scripting/script-system` (the code) |
| Hot reload | `scripting/hot-reload` | `make/first-script` | `assets/importing` (asset hot reload is its own row) |
| Shared libraries, ABIs | `scripting/shared-libraries` | `make/script-builds` (what a module is, one section) | `core/platform` |
| Frustum and bounds tests | `basics/math-geometry` (math), `draw/bounds-culling` (Strata) | — | `core/math` |
| Scene services, registries, service locator | `core/layers-registries` | — | `world/systems` (scene services as one kind) |
| What a subsystem does not do | that subsystem's page (`animation/limits`, `indirect/gi-limits`, or a section) | same | `appendix/not-in-strata` indexes them and gives the general technique |

Design decisions, with homes (book.md list gets this column):

| Decision | Home |
| --- | --- |
| Nothing may need history (TAA) to look right | `gpu/frame-tour` (a section "Rules every pass keeps", read before `indirect/ao` and `light/sun-shadows-2` need it), restated in `image/taa` |
| Never render below native resolution | `image/quality-settings` |
| Global illumination traces world data, never the screen | `indirect/problem` |
| A feature that is off is invisible bit for bit and costs nothing | `gpu/frame-tour` (same section) |
| Light in real units with pre-exposure | `light/units-exposure` |
| Game time counts fixed steps, never frames | `core/time` |
| Parallel work is deterministic | `core/jobs` |
| Trade-offs are measured on the reference machine | `core/profiling` |

---

## 4. The master checklist of `curricula.md` section 1, item by item

Status: **ok** (a page teaches it), **part** (touched, no home or not on the right track), **missing** (no page),
**absent-listed** (Strata lacks it and book.md says so), **absent-unlisted** (Strata lacks it and book.md does not say
so). Pages are current outline ids; "new:" names a page of section 6.

### 1.0 Orientation

| Topic | Page | Status |
| --- | --- | --- |
| What a game is, what an engine is, runtime and tools, genres | `start/what-an-engine-is` | ok (genres: name them in the brief) |
| Survey of real engines, where Strata sits [gap] | not named in any From | part → section of `start/what-an-engine-is` + new: `start/coming-from` |
| One frame, start to finish, the spine diagram [gap] | `core/frame-loop` (E), `gpu/frame-tour` (rendering) | part → home `start/what-an-engine-is` |
| Runtime architecture as layers [S] | `core/map`, `core/layers-registries` | ok |
| Reading a big codebase [gap] | `basics/reading-code` | part (wrong kind and place) → `core/reading-code` |
| Getting, building, running, testing [S][gap] | `start/install`, `start/first-engine-change`, `engineering/building` | ok |

### 1.1 Foundations: programming and C++

| Topic | Page | Status |
| --- | --- | --- |
| Compile and link model [gap] | `basics/build` | ok |
| Build systems, CMake, presets, PCH, caches [S] | `basics/build`, `engineering/cmake`, `engineering/flags-portability` | ok |
| The C++ the engine uses [S] | `basics/cpp`, `make/cpp-for-scripts` | ok; programming from zero missing → new: `basics/programming` |
| Errors without exceptions [S][gap] | `core/conventions` | ok |
| UB, sanitizers, warnings as errors, portability [S][gap] | `engineering/flags-portability` (part 20) | part: UB belongs in `basics/cpp` |
| Strings, UTF-8, Windows paths [S][gap] | `basics/bytes`, `core/platform` | ok |
| Code style as communication [S] | `core/conventions` | ok |
| C ABIs, dynamic libraries, loading code [S][gap] | `scripting/shared-libraries` | ok |
| Concurrency, memory ordering, job systems, main-thread model [S] | `basics/threads`, `core/jobs` | ok (home row needed) |
| Caches, prefetching, branches, SIMD, data-oriented design, AoS/SoA [S] | `basics/computer` | part: SIMD and AoS/SoA not named → brief of `basics/computer` |
| Floating point [S][gap] | — | missing → new: `basics/numbers` |
| Hashing, UUIDs, radix sort, serialization, atomic writes [S] | `basics/bytes`, `draw/batching`, `core/platform`, `world/serialization` | ok |
| Version control, git, reviewing a diff, commits [gap] | — | missing → new: `basics/tools`; commits in `engineering/contributing` |
| Third-party code, licenses [S][gap] | `engineering/third-party`; game assets `make/assets` | ok |

### 1.2 Mathematics

| Topic | Page | Status |
| --- | --- | --- |
| Conventions: handedness, up axis, row/column, order [S][gap] | `make/transforms-units`, `basics/math-vectors`, `gpu/coordinates` | part (no home) → `basics/math-matrices` + `reference/notation` |
| Vectors | `basics/math-vectors` | ok |
| Matrices | `basics/math-vectors` | ok, size → split `basics/math-matrices` |
| Transforms, TRS, hierarchies, normals [S] | `basics/math-vectors`, `world/scene-graph`, `draw/mirrors-camera-relative` | ok |
| Homogeneous coordinates | `basics/math-vectors` | ok → `basics/math-matrices` |
| Projections, NDC, depth precision, reversed-Z, infinite and oblique [S][gap] | `gpu/coordinates`, `core/math` | part: no primer → new: `basics/math-projection` |
| Rotations, quaternions, slerp | `basics/math-rotations` | ok |
| Interpolation: easing, Hermite, Bézier, Catmull-Rom, splines | — (SDK `Motion` in `make/recipes`) | missing → section of `basics/math-rotations` (retitled) |
| Geometric primitives and tests | `core/math`, `draw/bounds-culling`, `physics/queries` | part: no primer → new: `basics/math-geometry` |
| Numerical robustness [gap] | — | missing → `basics/numbers`, `basics/math-geometry` |
| Calculus for simulation, numerical integration | `physics/how-simulation-works` | ok → `physics/dynamics` |
| Randomness, seeding, hashing for noise, blue noise [S] | `make/recipes` (`Random`), `light/sun-shadows-2` | part (no home) → `basics/signals` |
| Noise and procedural generation | — | missing; Strata uses it only in `Tools/Generate*` → a section of `basics/signals`, one paragraph |
| Probability, Monte Carlo, importance sampling [gap] | `basics/math-light` | ok |
| Signals: sampling, aliasing, filters, convolution [gap] | — | missing → new: `basics/signals` |
| Colour maths, spaces, white balance, adaptation [S][gap] | `basics/color`, `image/grading` | ok |
| Spherical functions, SH, cube and octahedral maps [gap] | `basics/math-light`, `indirect/ibl` | ok |
| Geometric algebra (optional) | `appendix/further-reading` | ok |

### 1.3 Memory

| Topic | Page | Status |
| --- | --- | --- |
| Stack, heap, static, lifetimes, dangling | `basics/computer`, `basics/cpp` | ok |
| Allocators, fragmentation, alignment [S] | — (`RangeAllocator`, `StagingPool` appear in `gpu/geometry-pool`, `gpu/upload-queue`) | part → section of `basics/computer`; Strata's in `gpu/geometry-pool` |
| Handles instead of pointers [S][gap] | `world/ecs`, `assets/handles-meta` | ok (home row) |
| Containers and their memory | `basics/cpp` | ok |
| Budgets, tracking, leak detection, memory stats | `assets/residency`, `core/platform` | part: leaks → new: `core/debugging` |
| GPU memory, residency, staging [S][gap] | `gpu/resources-lifetimes`, `assets/residency`, `gpu/upload-queue` | ok |
| Deferred release [S][gap] | `gpu/resources-lifetimes` | ok |

### 1.4 The game loop and time

| Topic | Page | Status |
| --- | --- | --- |
| Loop styles, who owns the loop | `core/frame-loop` | ok |
| Clocks, delta time, spikes | `core/time` | ok |
| Fixed step, accumulator, spiral of death, interpolation [S] | `core/time`, `world/systems`, `world/interpolation` | ok (conflict: F8) |
| Real time, game time, pause, scale, stepping [S][gap] | `core/time`, `editor/stepping` | ok (home: `editor/stepping`) |
| Frame pacing, vsync, latency, frames in flight [gap] | `core/frame-loop`, `gpu/how-a-gpu-frame-works`, `gpu/resources-lifetimes` | part: input-to-photon latency not named |
| The multi-threaded frame [S] | `core/jobs`, `core/frame-loop` | ok |
| Determinism | physics, animation, `editor/stepping` | part (no home) → section 3 |
| Start-up and shut-down order, modules [S] | `core/first-frame`, `core/engine-modules` | ok |

### 1.5 Platform and windowing

| Topic | Page | Status |
| --- | --- | --- |
| Why a platform layer [S] | `core/platform` | ok |
| Windows, events, resize, fullscreen, monitors, DPI [S][gap] | `core/windows-events`; DPI only `editor/ui-scale` | part: the game window's DPI → `core/windows-events` brief |
| Headless runs [S] | `core/windows-events`, `worlds/runtime` | ok |
| GUI against console programs [S][gap] | `core/platform` | ok |
| File systems, watching, locks, atomic writes [S] | `core/platform` | ok |
| Permissions, private files [S][gap] | `core/platform`, `automation/security` | ok |
| Processes, command lines, environment | `core/platform`, `automation/sessions` | ok |
| Crashes, containment, symbolising [S][gap] | `scripting/crash-containment` | ok |
| Platform differences, MoltenVK [S] | `core/platform`, `gpu/vulkan-nvrhi` | ok |

### 1.6 Input

| Topic | Page | Status |
| --- | --- | --- |
| Devices, touch | `input/devices-state`, `input/gamepads`; touch | ok; touch absent-listed |
| Polling against events, edges against levels | `input/devices-state` | ok, but no concept page → new: `input/devices-to-intents` |
| Physical key against character, text input, key repeat [S][gap] | `input/devices-state`, `make/recipes`; IME | ok; IME absent-listed |
| Mouse, capture, cursor modes [S] | `input/mouse-cursor` | ok |
| Gamepads, dead zones, mappings [S] | `input/gamepads` | ok |
| Actions, bindings, rebinding, contexts [S][gap] | `input/actions`, `input/rebinding`, `make/input` | ok |
| Routing, consumption, focus [S] | `ui/input`, `editor/game-view` | ok |
| Simulated input [S][gap] | `input/simulated` | ok |
| Accessibility: remapping, hold against toggle | `input/rebinding` | part: hold/toggle → `make/input` brief |

### 1.7 Resources and assets

| Topic | Page | Status |
| --- | --- | --- |
| Why a pipeline, source and cooked forms | `assets/what-is-an-asset` | ok |
| Handles, `.meta`, moves [S][gap] | `assets/handles-meta` | ok |
| Registry, manager, refcount against residency [S] | `assets/loading`, `assets/residency` | ok |
| Importers, versions, dependencies, cancellation [S] | `assets/importing` | ok |
| References, dependency graphs [S] | `assets/references`, `editor/trash-references` | ok |
| Async loading, "not loaded yet" [S][gap] | `assets/loading`, `draw/asset-requests` | ok |
| Streaming and residency [S] | `assets/residency` | ok |
| Textures: formats, BC, mips, bindless [S] | `assets/textures`, `assets/mip-streaming`, `gpu/binding` | ok (order: F3) |
| Meshes, LODs, geometry pools [S] | `gpu/geometry-pool`, `assets/models-gltf`, `draw/lod` | ok |
| Formats: glTF, images, fonts, audio, scenes, packs [S] | `assets/*`, `gpu/text`, `audio/clips-voices-sources`, `world/serialization` | ok |
| Untrusted input [S][gap] | `assets/robustness`, `gpu/text` | ok |
| Hot reload of assets [S] | `assets/importing`, `core/platform` | ok |
| Thumbnails [S] | `editor/thumbnails` | ok |

### 1.8 The scene and entity models

| Topic | Page | Status |
| --- | --- | --- |
| What a world is made of | `world/what-a-world-is` | ok |
| Object models compared | `world/what-a-world-is` | ok |
| ECS in practice [S] | `world/ecs`, `world/systems` | ok |
| Components as data, tags, registration [S] | `world/ecs`, `world/reflection`, `world/tutorial-component` | ok |
| Hierarchies, caches, dirty flags, the contract [S][gap] | `world/scene-graph` | ok |
| Names, tags, indexes, queries [S] | `world/scene-graph` | ok |
| Events and messaging: observers, queues [S] | `core/windows-events`, `world/systems` | part: the patterns → new: `make/patterns` |
| Services and registries against singletons [S] | `core/layers-registries`, `world/systems` | ok |
| Reflection [S][gap] | `world/reflection` | ok |
| Scene documents [S] | `world/serialization` | ok |
| Prefabs [S][gap] | `make/prefabs`, `world/prefabs`, `editor/prefab-instances` | ok |
| The scene's life: play copy, switching, background release [S] | `editor/play-mode`, `world/serialization` | ok |
| Sub-scenes [S] | `world/sub-scenes` | ok |

### 1.9 Rendering

| Topic | Page | Status |
| --- | --- | --- |
| How a GPU works (waves, occupancy, bandwidth, branches) [gap] | `gpu/how-a-gpu-frame-works` (commands and frames only) | part → retitle and brief |
| The pipeline at a glance | `gpu/how-a-gpu-frame-works`, `gpu/first-triangle` | part (not named) → brief |
| Explicit APIs, Vulkan [S] | `gpu/vulkan-nvrhi` | ok |
| RHIs [S][gap] | `gpu/vulkan-nvrhi` | ok |
| Bindless [S] | `gpu/binding` | ok |
| Shaders, SPIR-V, registers, push constants, variants [S] | `gpu/shaders`, `gpu/binding`, `engineering/generated-code` | ok |
| Compute, dispatches, UAV barriers [S] | `gpu/shaders`, `gpu/resources-lifetimes` | part (no home) → retitle `gpu/shaders` |
| Validation layers, debug names, RenderDoc [gap] | — | missing → new: `gpu/debugging` |
| Conventions: NDC, flip, UV, depth, winding [S][gap] | `gpu/coordinates` | ok |
| Cameras: view, projection, FOV, near and far [S] | `gpu/coordinates`, `core/math` | part (no camera home) → section 3 |
| Depth test, culling, blending, stencil | `gpu/first-triangle`, `gpu/coordinates`, `draw/batching` | part: blending and stencil not named → `gpu/first-triangle` brief |
| Visibility: frustum, occlusion, spatial index, portals [S] | `draw/bounds-culling`, `draw/occlusion` | ok; portals absent-unlisted |
| The render scene [S][gap] | `draw/render-scene`, `draw/render-scene-gpu` | ok |
| Draw lists, sort keys, batching, instancing [S] | `draw/batching` | ok |
| GPU-driven rendering [S] | `draw/gpu-driven`, `draw/visibility-feedback` | ok |
| LOD [S] | `draw/lod` | ok |
| Rendering architectures [S?] | `light/many-lights`, `gpu/frame-tour` | ok (forward + prepass, clustered) |
| Frame graphs [S?] | — | absent-unlisted (fixed pass order; NVRHI's automatic barriers, render-core §2 item 9) |
| Camera-relative rendering [S][gap] | `draw/mirrors-camera-relative` | ok |
| GPU-side uploads and streaming [S] | `gpu/upload-queue`, `assets/uploads` | ok (order: F3) |
| Readback [S] | `gpu/readback-timing` | ok |
| Radiometry, photometry, rendering equation, BRDF [S] | `light/units-exposure`, `light/brdf`, `indirect/problem` | part: the rendering equation is defined after the BRDF page uses it → reflection equation in `light/brdf`'s brief |
| PBR: GGX, Fresnel, F0, Smith, energy, multiscatter [S] | `light/brdf`, `indirect/energy` | ok (order: F4) |
| Textures: UVs, sampling, filtering, wrap modes [S] | `assets/textures`, `gpu/binding` | part: filtering theory → `basics/signals` |
| Normal maps, tangent space, mirrored [S][gap] | `light/materials`, `draw/mirrors-camera-relative` | ok |
| Clear coat, glass, transparency, sorting, OIT [S] | `light/clearcoat-transmission`, `light/materials`, `draw/batching` | ok; OIT absent-unlisted |
| Material systems, never in place [S] | `light/materials`, `make/materials` | ok |
| Skinned meshes on the GPU [S] | `draw/skinned` | ok (order: F4) |
| HDR targets and sanitizing [S][gap] | `image/why-post` | ok |
| Light types, units, exposure [S] | `light/lights`, `light/area-lights`, `light/units-exposure`, `image/exposure` | ok |
| Light culling: tiles, clusters [S?] | `light/many-lights` | ok |
| Shadow maps, biases, PCF, PCSS, cascades, atlases, caching, masks [S] | `light/shadow-basics`, `light/sun-shadows-1/2`, `light/local-shadows` | ok |
| Ambient occlusion [S] | `indirect/ao` | ok |
| IBL, probes, baking [S] | `indirect/ibl`, `indirect/probes` | ok |
| Screen-space reflections [S] | `indirect/ssr` | ok |
| Sky and atmosphere [S] | `light/sky` | ok |
| Fog: height, volumetric, froxels [S] | `light/fog` | ok; volumetric fog absent-unlisted (render-direct §1.9) |
| GI: the problem | `indirect/problem` | ok |
| GI approaches compared [gap] | `indirect/problem` | ok |
| World against screen space [S] | `indirect/problem`, `indirect/gi-*` | ok |
| Reference renders, white furnace [S][gap] | `indirect/energy`, `indirect/measuring-light` | ok (order: F4) |
| Anti-aliasing, MSAA, FXAA/SMAA, TAA [S] | `image/spatial-aa`, `image/taa` | ok; MSAA absent-unlisted |
| Upscaling, and why not [S] | `image/quality-settings` | ok |
| Tone mapping, exposure, bloom, DoF, motion blur, grading, grain, CA [S] | part `image` | ok |
| A neutral post chain for tests [S][gap] | `image/tutorial-post-effect` | part → name it in `engineering/test-kinds` |
| Text: fonts, atlases, shaping, SDF, untrusted fonts [S][gap] | `gpu/text`, `ui/text` | ok |
| Debug drawing, gizmos, overlays [S] | `gpu/debug-drawing`, `editor/scene-view` | ok |
| Terrain [S?] | "terrain tools" in the list | absent-listed (the showcase's terrain is generated meshes) |
| Particles and VFX [S?] | list | absent-listed |
| Water [S?] | list | absent-listed |
| Decals, billboards, impostors [S?] | decals in the list | decals absent-listed; billboards and impostors absent-unlisted |
| Non-photorealistic rendering [S-none] | — | absent-unlisted |
| GPU timing, pass timers [S] | `gpu/readback-timing`, `core/profiling` | ok |
| Finding the bottleneck (CPU, vertex, fragment, bandwidth) | `core/profiling` (bound classification), `make/big-scenes-fast` | part → `core/profiling` brief |
| Quality settings, presets, players' options [S][gap] | `image/quality-settings` | ok |

### 1.10 Animation

| Topic | Page | Status |
| --- | --- | --- |
| Kinds of animation | `animation/problem` | ok |
| Skeletons, bind and rest poses, poses as data [S] | `animation/skeletons` | ok |
| Clips, keys, compression, events [S] | `animation/clips`, `animation/time-events` | ok; compression absent-listed |
| Skinning, LBS, artefacts, dual quaternions [S] | `animation/skinning` | ok; dual quaternions absent-unlisted |
| Blending, additive, layers, blend trees [S?] | `animation/blending` | ok; layers and trees absent-listed (W8: may land), additive absent-unlisted |
| State machines [S] | `animation/state-machines` | ok (W8?) |
| Root motion [S] | `animation/root-motion` | ok |
| Parallel, deterministic evaluation [S] | `animation/system` | ok |
| IK, retargeting, motion matching [S?] | — | IK absent-listed; retargeting and motion matching absent-unlisted |
| Pipeline: import, previews [S] | `animation/importing`, `animation/editor` | ok |

### 1.11 Collision and physics

| Topic | Page | Status |
| --- | --- | --- |
| Do you need physics, middleware [S] | `physics/why` | ok |
| Shapes | `physics/bodies-colliders` | ok |
| Broad phase | `physics/how-simulation-works` | ok → `physics/collision-detection` |
| Narrow phase, GJK, EPA, manifolds | `physics/how-simulation-works` | ok → `physics/collision-detection` |
| Rigid body dynamics | `physics/how-simulation-works` | ok → `physics/dynamics` |
| Constraints, solvers, warm starting, joints | `physics/how-simulation-works` | ok; joints absent-listed |
| Islands, sleeping [S] | `physics/how-simulation-works`, `physics/tuning` | ok |
| Continuous collision | `physics/how-simulation-works` | ok |
| Layers, triggers, contact events [S] | `physics/collision-layers`, `physics/contacts-triggers` | ok |
| Kinematic bodies, character controllers [S][gap] | `physics/character-controllers`, `make/characters-cameras` | ok |
| Raycasts, shape casts, overlaps [S] | `physics/queries` | ok; sweeps absent-listed |
| Fixed rate, interpolation, determinism [S] | `core/time`, `world/interpolation`, `physics/world-step` | ok |
| Contact recycling, limits, constant-time diagnostics [S] | `physics/tuning`, `physics/scale-streaming` | ok |
| Debug visualisation [S] | `physics/tuning` | ok |
| Who owns the transform [S][gap] | `physics/world-step` | ok |
| Ragdolls, vehicles, cloth, destruction, fluids, buoyancy [S?] | list (ragdolls, vehicles) | ragdolls, vehicles absent-listed; cloth, destruction, fluids, buoyancy absent-unlisted |

### 1.12 Audio

| Topic | Page | Status |
| --- | --- | --- |
| Sound as a signal | `audio/sound-in-a-computer` | ok |
| PCM, decoding, streaming, mixing, voices [S] | `audio/engine`, `audio/clips-voices-sources` | ok |
| Attenuation, panning, Doppler, occlusion, reverb [S?] | `audio/spatial` | ok; reverb absent-listed, occlusion absent-unlisted |
| Mixer thread, latency, device abstraction, null device [S] | `audio/engine`, `audio/testing` | ok |
| Sources, buses, music, ducking [S?] | `audio/scene-system`, `make/sound` | buses absent-listed; music system and ducking absent-unlisted |
| Middleware for comparison | `audio/engine` | part → brief (the internals shape's "alternatives" section, F11) |

### 1.13 Gameplay and scripting

| Topic | Page | Status |
| --- | --- | --- |
| Game flow: menus, levels, loading, saving [S] | `make/levels-saves`, `make/ui` | ok |
| Gameplay patterns (GPP) | — | missing → new: `make/patterns` |
| Updating game objects: phases, order | `world/systems`, `make/script-loop`, `scripting/script-system` | ok |
| Why scripts, the options [S] | `scripting/why-scripts` | ok |
| A script ABI [S][gap] | `scripting/abi-sdk`, `scripting/shared-libraries` | ok |
| Crash containment, hot reload [S][gap] | `scripting/crash-containment`, `scripting/hot-reload` | ok |
| Lifecycle, fields, attaching, spawning [S] | `make/first-script`, `make/script-loop`, `make/gameplay-1` | ok |
| The gameplay API surface [S] | `make/gameplay-1..3`, `reference/script-api` | ok (order: F14) |
| Cameras for games [S?][gap] | `make/characters-cameras` | ok for G; no E page (cameras are script code in the samples: say so) |
| Game AI, pathfinding, navigation [S-none] | — | missing and absent-unlisted → new: `appendix/game-ai` |
| Game design basics [gap] | — | missing → new: `make/game-design` |

### 1.14 User interface

| Topic | Page | Status |
| --- | --- | --- |
| Immediate against retained [S] | `ui/what-game-ui-does`, `editor/immediate-mode` | ok (two homes → section 3) |
| Layout, anchors, pivots, scaling [S] | `ui/layout`, `make/ui` | ok |
| Widgets, styles, themes [S] | `make/ui`, `editor/design-system`, `editor/widget-kit` | ok |
| Input, focus, gamepad navigation, world-space UI [S] | `ui/input` | ok |
| Text, localisation, right-to-left [S?] | `ui/text` | localisation and RTL absent-unlisted |
| Rendering UI [S] | `ui/drawing` | ok |
| HUDs, menus, settings screens, accessibility | `make/ui`, `make/levels-saves` | part: accessibility (scale, contrast) → `make/ui` brief |

### 1.15 Tools and editors

| Topic | Page | Status |
| --- | --- | --- |
| Why editors | `editor/program` | ok |
| Core without UI, panels, views, selection [S] | `editor/program`, `editor/shell` | ok |
| Commands, undo, transactions [S] | `editor/commands`, `editor/undo` | ok (order: F2) |
| Inspectors from reflection [S] | `editor/inspectors` | ok |
| Viewports, gizmos, placement [S] | `editor/scene-view`, `editor/camera-viewport`, `editor/placement` | ok |
| Content browser, imports, thumbnails [S] | `editor/lists`, `editor/thumbnails`, `make/assets` | ok |
| Play in editor, edits while playing [S] | `editor/play-mode` | ok |
| No silent data loss [S][gap] | `editor/saving`, `editor/recovery` | ok |
| Prefab editing [S] | `editor/prefab-instances`, `make/prefabs` | ok |
| Project settings, preferences [S] | `world/projects-settings`, `editor/launcher-dialogs` | ok |
| Launcher, templates, samples [S] | `editor/launcher-dialogs`, `worlds/templates`, `make/samples` | ok |
| Automation, RPC, CLI, MCP, agents, security [S][gap] | part `automation`, `make/automated-playtests` | ok |
| Exporting games [S] | `make/export`, `worlds/export`, `assets/packs-export` | ok (three pages → home row) |

### 1.16 World streaming

| Topic | Page | Status |
| --- | --- | --- |
| Why one scene does not scale, coordinate limit, floating origin [S] | `worlds/why-streaming`, `draw/mirrors-camera-relative` | ok; floating origin absent-listed ("origin rebasing") |
| Cells, persistent scene, sub-scenes, budgets [S] | `worlds/grids`, `world/sub-scenes` | ok |
| Streaming policies [S] | `worlds/streamer` | ok |
| Editing streamed worlds [S] | `worlds/editing` | ok (order: F2) |
| Physics and streaming [S] | `worlds/physics-scripts`, `physics/scale-streaming` | ok (two homes: F6) |
| HLOD, impostors [S?] | list (HLOD) | absent-listed |

### 1.17 Networking

| Topic | Page | Status |
| --- | --- | --- |
| Sockets, UDP and TCP, reliability | `appendix/networking`, `automation/json-rpc` | ok |
| Lockstep, client-server, authority | `appendix/networking` | ok |
| Prediction, reconciliation, lag compensation | `appendix/networking` | ok |
| Replication, snapshots, delta compression | `appendix/networking` | ok |
| Never trust the client | `appendix/networking`, `automation/security` | ok |
| Strata has none; the RPC server as its networking | `appendix/networking`, `automation/*` | ok |

### 1.18 Debugging and profiling

| Topic | Page | Status |
| --- | --- | --- |
| Logging, levels, background writer [S] | `core/conventions` | ok |
| Asserts and verifies [S] | `core/conventions` | ok |
| Debuggers, breakpoints, optimised builds, attaching [gap] | `make/script-builds` (attach, scripts only) | missing → new: `basics/tools`, `core/debugging` |
| Debug drawing, consoles, cvars, debug cameras, cheats [S?] | `gpu/debug-drawing` | consoles and cvars absent-unlisted |
| CPU profiling, Tracy, stages [S] | `core/profiling` | ok |
| GPU profiling: timers, captures [S] | `gpu/readback-timing` | part: captures → new: `gpu/debugging` |
| Memory profiling, leak detection | — | missing → new: `core/debugging` |
| Method: measure first, budgets, statistics [S][gap] | `engineering/perf-lab` (part 20) | part → home `core/profiling` |
| Crash reports, symbolisation, script crash locations [S] | `scripting/crash-containment` | ok |
| Rendering debug views [S] | `indirect/measuring-light` | ok (order: F4) |

### 1.19 Build, test and ship

| Topic | Page | Status |
| --- | --- | --- |
| Configurations [S] | `basics/build`, `engineering/building` | ok |
| Optional modules, composition root [S] | `core/layers-registries`, `engineering/cmake` | ok |
| CI [S] | `engineering/ci` | ok |
| Testing an engine (all suite kinds) [S][gap] | `engineering/testing`, `test-kinds`, `feature-test`, `perf-lab` | ok (order: F5) |
| Packaging, what a release ships [S] | `engineering/releasing` | ok |
| Exporting a game [S] | `worlds/export` | ok |
| Versioning, release notes [S] | `engineering/releasing`, `appendix/history` | ok |
| Contributing, review checklist, rules for agents [S] | `engineering/contributing` | ok |

Totals: 245 rows; 13 rows missing, 29 partial, 16 holding absent-unlisted items.

---

## 5. The corrected list of parts

| # | Part (slug) | Track | Pages | Change |
| --- | --- | --- | --- | --- |
| 0 | Start here (`start`) | all | 8 | + `coming-from`, + `map`; reordered (F23) |
| 1 | Making games (`make`) | G (first 3 also E, B) | 39 | reordered, projects interleaved; + `game-design`, `patterns`, `ui-interaction`, `local-lights`, `gi`, `editor-from-outside` (F13, F14) |
| 2 | Foundations (`basics`) | B, E | 16 | + `programming`, `numbers`, `signals`, `tools`; math split in four; `reading-code` → core |
| 3 | Engine architecture (`core`) | E | 15 | + `reading-code`, `testing` (from engineering), `debugging` |
| 4 | Scenes and the ECS (`world`) | E | 8 | serialization, prefabs, sub-scenes → part 6 |
| 5 | The GPU and the renderer's core (`gpu`) | E | 14 | before assets; + `debugging`; `shaders` and `how-a-gpu-frame-works` retitled |
| 6 | Assets and scene documents (`assets`) | E | 15 | after gpu; + three pages from world; `mip-streaming` → draw |
| 7 | The editor's core (`editor`) | E | 15 | pages 1-15 of old part 18, moved early (F2) |
| 8 | Drawing a scene (`draw`) | E | 12 | + `mip-streaming`; `skinned` → animation; `motion-vectors` → image |
| 9 | Light and materials (`light`) | E | 14 | + `measuring`, `energy`; `lights` split into `sun` and `local-lights`; `sky`, `fog` → indirect |
| 10 | The image (`image`) | E | 13 | before indirect; + `motion-vectors` |
| 11 | Indirect light (`indirect`) | E | 10 | + `sky`, `fog`; `energy`, `measuring-light` → light |
| 12 | Physics (`physics`) | E | 11 | `how-simulation-works` split; `scale-streaming` → `capacity` |
| 13 | Animation (`animation`) | E | 14 | + `skinned-rendering`; graph pages W8? |
| 14 | Audio (`audio`) | E | 6 | — |
| 15 | Input (`input`) | E | 7 | + `devices-to-intents`; `simulated` holds `input.sequence` |
| 16 | Scripting (`scripting`) | E | 9 | `host-api` split |
| 17 | Game UI (`ui`) | E | 7 | — |
| 18 | Large worlds and shipping (`worlds`) | E | 9 | `physics-scripts` takes the streaming half of physics' scale page |
| 19 | The editor's interface (`editor-ui`) | E | 14 | pages 16-32 of old part 18, three merges (F21) |
| 20 | Automation and AI agents (`automation`) | E | 7 | `outside` → make |
| 21 | Building, testing and releasing (`engineering`) | E | 12 | `testing` → core |
| 22 | Capstone (`capstone`) | E | 3 | new (F17) |
| 23 | Reference (`reference`) | all | 20 | + `index`, `notation` |
| 24 | Appendices (`appendix`) | all | 7 | + `game-ai` |

305 pages, plus one `index` page per part (generated) and a `review` page for the 16 parts of eight or more pages
(F18). Part prerequisites, to be replaced by per-page Needs (F1), become:

| Part | Prerequisites (the part's first pages need these; later pages add their own) |
| --- | --- |
| `world` | `basics/programming` or `basics/cpp`, `basics/computer`, `basics/math-matrices`, `basics/math-rotations`, `basics/threads`, `core/map`, `core/frame-loop`, `core/time` |
| `gpu` | `basics/math-projection`, `basics/color`, `basics/numbers`, `core/frame-loop`, `core/engine-modules` |
| `assets` | `basics/bytes`, `basics/threads`, `core/jobs`, `world/ecs`, `world/reflection`, `gpu/how-a-gpu-frame-works`, `gpu/resources-lifetimes` (uploads add `gpu/upload-queue`) |
| `editor` | `world/reflection`, `world/systems`, `assets/scene-documents`, `assets/prefabs`, `core/jobs`, `core/testing`, `make/editor-tour` |
| `draw` | `gpu/frame-tour`, `gpu/shaders`, `world/scene-graph`, `assets/residency`, `basics/math-geometry` |
| `light` | `gpu/frame-tour`, `gpu/coordinates`, `basics/color`, `basics/math-light`, `basics/signals` |
| `image` | `light/units-exposure`, `light/measuring`, `basics/signals`, `draw/render-scene-gpu` (for motion vectors) |
| `indirect` | `light/energy`, `image/taa` (SSR), `basics/math-light`, `editor/commands` (bakes) |
| `physics` | `core/time`, `core/jobs`, `world/systems`, `world/scene-graph`, `world/projects-settings`, `basics/math-rotations` |
| `animation` | `basics/math-rotations`, `world/systems`, `core/jobs`, `assets/models-gltf`, `draw/bounds-culling` |
| `audio` | `basics/threads`, `basics/signals`, `core/engine-modules`, `world/systems`, `assets/loading` |
| `input` | `core/windows-events`, `world/projects-settings`, `editor/commands` (simulated), `make/editor-tour` |
| `scripting` | `basics/computer`, `basics/cpp`, `basics/build`, `core/platform`, `world/systems` |
| `ui` | `world/scene-graph`, `gpu/text`, `gpu/binding`, `input/actions`, `scripting/abi-sdk` |
| `worlds` | `assets/sub-scenes`, `assets/residency`, `assets/packs-export`, `physics/capacity`, `scripting/abi-sdk`, `editor/undo` |
| `editor-ui` | `editor/program`, `ui/what-game-ui-does`, `gpu/shaders`, `input/mouse-cursor` |
| `automation` | `editor/commands`, `editor/deferred-commands`, `basics/bytes`, `basics/threads`, `core/platform` |
| `engineering` | `basics/build`, `core/testing`, per page as section 2 |
| `capstone` | `world/tutorial-component`, `editor/tutorial-command`, `scripting/tutorial-host-function`, `engineering/feature-test`, `engineering/contributing` |

---

## 6. Exact outline rows

Columns: id | Title | Kind | Size | Tracks | Needs (main ones) | From. "Moved" keeps the old row's From.

### Part 0 — Start here

| id | Title | Kind | Size | Tracks | Needs | From |
| --- | --- | --- | --- | --- | --- | --- |
| `start/welcome` | What Strata is and what this book teaches | C | S | G E B | — | unchanged |
| `start/how-to-read` | How to read this book | H | S | G E B | — | unchanged |
| `start/install` | Getting Strata running | H | M | G E B | — | size S → M |
| `start/first-game` | Your first game in 30 minutes | T | M | G E B | `start/install` | unchanged; seeds Coin Run |
| `start/what-an-engine-is` | What a game engine is: one frame, start to finish | C | L | G E B | — | + home of the frame map and the survey of engines (curricula 1.0 [gap]); size M → L |
| `start/coming-from` | Coming from Unity, Unreal or Godot | R | M | G E | `start/what-an-engine-is` | new (curricula 5.2 Part 0; Unreal "transitioning from Unity") |
| `start/first-engine-change` | Your first engine change in 30 minutes | T | M | E | `start/install` | track all → E |
| `start/map` | The map of the book: tracks and prerequisites | R | S | G E B | — | new, generated from front matter (curricula 5.1.4) |

### Part 1 — Making games (reordered)

| # | id | Title | Kind | Size | Tracks | From / change |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `make/editor-tour` | A tour of the editor | T | L | G E B | size M → L (editor-ui ch. 1); use-level home of editor commands |
| 2 | `make/scenes-entities` | Scenes, entities and components | T | M | G E B | unchanged |
| 3 | `make/transforms-units` | Positions, rotations and units | C | M | G B | unchanged |
| 4 | `make/assets` | Bringing in assets | T | M | G B | kind H → T |
| 5 | `make/materials` | Materials | T | L | G B | unchanged |
| 6 | `make/prefabs` | Prefabs | T | M | G B | unchanged |
| 7 | `make/cpp-for-scripts` | Just enough C++ for game scripts | C | L | G B | Needs `basics/programming` for readers who never programmed |
| 8 | `make/first-script` | Your first script | T | M | G E B | Needs any of `make/cpp-for-scripts`, `basics/cpp` |
| 9 | `make/script-loop` | The game loop from a script's side | C | M | G B | home of the script lifecycle |
| 10 | `make/scripting-the-world` | Finding, moving and spawning things from scripts | T | L | G B | was `make/gameplay-1` (H → T, scripting ch. 4) |
| 11 | `make/input` | Input and input actions | T | M | G B | + hold against toggle |
| 12 | `make/physics` | Physics for game makers | T | L | G B | unchanged |
| 13 | `make/characters-cameras` | Characters and cameras | T | L | G B | use-level home of interpolation |
| 14 | `make/sound` | Sound | T | M | G B | use-level home of residency ("request in `OnCreate`") |
| 15 | `make/ui` | Menus and HUDs | T | L | G B | gameui ch. 2 only |
| 16 | `make/ui-interaction` | Buttons, events and pause menus | T | M | G B | new by split: gameui ch. 3 "Widgets, events and scripts" |
| 17 | `make/export` | Exporting and shipping | T | M | G B | unchanged |
| 18 | `make/game-design` | Designing a small game: core loop, scope, feel and playtesting | C | M | G B | new (curricula 1.13 [gap]) |
| 19 | `make/project-coin-run` | Project: Coin Run, a first finished game | T | L | G B | moved from position 30 (gamedev §6 G8) |
| 20 | `make/lighting` | Lighting a scene: the sun, the sky and exposure | T | L | G | split; not W8 |
| 21 | `make/local-lights` | Lamps, spots and area lights | T | M | G | new by split · W8 |
| 22 | `make/look` | The camera's image and graphics quality | T | L | G | moved after UI (its Graphics menu) |
| 23 | `make/reflections` | Sky light, ambient occlusion and reflections in your game | T | M | G | split from `make/reflections-gi` (render-indirect ch. 6, 8); not W8 |
| 24 | `make/gi` | Trying global illumination | T | S | G | split (render-indirect ch. 11) · W8 |
| 25 | `make/animation` | Animation for game makers | T | L | G | W8? (animation graph) |
| 26 | `make/scripting-physics-animation` | Physics, sound and animation from scripts | T | L | G | was `make/gameplay-2` (scripting ch. 5), after its topics |
| 27 | `make/levels-saves` | Levels, loading, saves and settings | H | L | G | unchanged |
| 28 | `make/scripting-player-side` | The player's side from scripts: time, saves, window and options | T | L | G | was `make/gameplay-3` (scripting ch. 6) |
| 29 | `make/patterns` | Patterns for game code: state machines, commands, pools and events | C | L | G E | new (curricula 1.13, GPP [S7]); examples from the samples' scripts |
| 30 | `make/recipes` | Building blocks and recipes | H | L | G | unchanged |
| 31 | `make/project-tetris` | Project: Tetris | T | XL | G | unchanged |
| 32 | `make/play-test-debug` | Playing, testing and debugging | H | M | G | use-level home of stepping and determinism |
| 33 | `make/editor-from-outside` | Driving the editor from outside | T | M | G E | moved from `automation/outside` |
| 34 | `make/automated-playtests` | Automated play-tests and AI agents | H | M | G | use-level home of command scripts and simulated input |
| 35 | `make/large-worlds` | Large worlds | T | L | G | unchanged |
| 36 | `make/big-scenes-fast` | Making a big scene draw fast | T | M | G | unchanged |
| 37 | `make/script-builds` | Building and shipping script modules | H | M | G | teaches "what a module is" at use level |
| 38 | `make/project-platformer` | Project: a third-person platformer | T | XL | G | W8? (animation graph) |
| 39 | `make/samples` | Studying the samples | H | M | G | unchanged |

### Part 2 — Foundations

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `basics/programming` | Programming from zero: values, functions, loops and classes | C | XL | B (G when needed) | new; sketches compiled; links learncpp lessons per section |
| `basics/computer` | How a computer runs a program: CPU, memory, stack, heap and caches | C | L | B E | + allocators, SIMD, AoS against SoA |
| `basics/numbers` | Numbers in a computer: integers, bits, floating point and precision | C | M | B E | new (curricula 1.1 floating point [gap], 1.2 robustness [gap]) |
| `basics/bytes` | Bytes, files, text and hashes | C | M | E | unchanged |
| `basics/tools` | Tools of the trade: the terminal, git, an IDE and a debugger | T | M | E | new (curricula 1.1 git [gap], 1.18 debuggers [gap]) |
| `basics/cpp` | The C++ you need to read Strata | C | XL | E | Needs `basics/programming` |
| `basics/build` | How a C++ program is built | C | M | E | unchanged |
| `basics/math-vectors` | Vectors: length, direction, dot and cross products | C | L | B E | split from `basics/math-vectors` XL (pilot stays on this id) |
| `basics/math-matrices` | Matrices and transforms: TRS, hierarchies, homogeneous coordinates and conventions | C | L | B E | split; home of conventions |
| `basics/math-rotations` | Rotations, quaternions and interpolation | C | L | B E | + lerp, easing, curves (curricula 1.2 interpolation) |
| `basics/math-projection` | Cameras and projection: view, perspective, orthographic, frustums and depth | C | L | E | split (FGED vol. 2 ch. 6 adopt: "projection and depth precision as a chapter of their own") |
| `basics/math-geometry` | Geometry for engines: rays, planes, boxes, intersection tests and robustness | C | M | E | split ([S6] adopt: "why does this fail in floats") |
| `basics/color` | Color and light for programmers: linear, sRGB, HDR | C | M | E | unchanged |
| `basics/signals` | Sampling, aliasing, filtering and noise | C | L | E | new (curricula 1.2 signals [gap], randomness, blue noise) |
| `basics/math-light` | Math for light: integrals, Monte Carlo, spherical harmonics, octahedral maps | C | L | E | unchanged |
| `basics/threads` | Threads, atomics and races | C | L | E | home of the general topic (section 3) |

### Part 3 — Engine architecture (changed and new rows; others unchanged, in this order)

`core/map` → `core/reading-code` → `core/first-frame` → `core/frame-loop` → `core/time` → `core/windows-events` →
`core/engine-modules` → `core/layers-registries` → `core/conventions` → `core/testing` → `core/debugging` →
`core/jobs` → `core/profiling` → `core/platform` → `core/math`.

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `core/reading-code` | Following one feature from a click to a pixel | T | M | E | moved from `basics/reading-code` (H → T); Needs `core/map`, `basics/tools` |
| `core/time` | Time: delta time, fixed steps and time scale | C | L | E (G link) | retitled: interpolation is `world/interpolation`'s, stepping `editor/stepping`'s |
| `core/testing` | Testing an engine | C | L | E | moved from `engineering/testing` |
| `core/debugging` | Debugging the engine: debuggers, logs, asserts, crash dumps and leaks | H | M | E | new (curricula 1.18 [gap]); foundation §1.5, §1.7 (`Platform` debugger, memory) |
| `core/jobs` | Threads and the job system | I | L | E | size XL → L (threads from zero is `basics/threads`) |
| `core/profiling` | Measuring the frame: the frame profiler, Tracy and the method | I | M | E | + home of the measuring method |

### Part 4 — Scenes and the ECS

`world/what-a-world-is`, `world/ecs`, `world/scene-graph`, `world/systems`, `world/interpolation`, `world/reflection`,
`world/tutorial-component` (creates WindZone, the E running example), `world/projects-settings`. Rows unchanged; three
rows move to part 6.

### Part 5 — The GPU and the renderer's core (changed and new rows)

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `gpu/how-a-gpu-frame-works` | How a GPU works and draws a frame | C | L | E | + the hardware: waves, occupancy, bandwidth, branches (curricula 1.9.1 [gap]) |
| `gpu/debugging` | Debugging the GPU: validation layers, debug names and frame captures | H | M | E | new; after `gpu/first-triangle` (render-core §2 item 4, hands-on 12; LearnOpenGL adopt) |
| `gpu/shaders` | Shaders and compute: Slang, the build and the dialect | I | L | E | retitled; home of compute shaders and dispatches |
| `gpu/coordinates` | Coordinate systems and the camera: clip space, reversed depth, UVs | C | M | E | + `CameraComponent` (scene-ecs §1.2 row) |

### Part 6 — Assets and scene documents (order)

`assets/what-is-an-asset`, `assets/handles-meta`, `assets/importing`, `assets/textures`, `assets/models-gltf`,
`assets/loading`, then:

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `assets/scene-documents` | Saving and loading scenes | I | L | E | moved from `world/serialization` |
| `assets/prefabs` | Prefabs: the data model | I | L | E | moved from `world/prefabs` |
| `assets/sub-scenes` | Sub-scenes and the frame's work budget | I | M | E | moved from `world/sub-scenes` |

then `assets/residency`, `assets/references`, `assets/uploads`, `assets/packs-export`, `assets/robustness`,
`assets/extending`.

### Part 7 — The editor's core

`editor/program`, `editor/commands`, `editor/undo`, `editor/saving`, `editor/recovery`, `editor/trash-references`,
`editor/prefab-instances`, `editor/play-mode`, `editor/stepping` (without the `input.sequence` section),
`editor/deferred-commands`, `editor/command-scripts`, `editor/placement` (W8?), `editor/camera-viewport`,
`editor/thumbnails`, `editor/tutorial-command` (adds `wind.*` commands to WindZone). Rows unchanged otherwise.

### Part 8 — Drawing a scene

Remove `draw/skinned`, `draw/motion-vectors`; append:

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `draw/mip-streaming` | Mip streaming | I | L | E | moved from `assets/mip-streaming`; after `draw/visibility-feedback` |

### Part 9 — Light and materials (order)

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `light/units-exposure` | Light by the numbers: units, HDR and exposure | C | L | E | unchanged; home of EV100 |
| `light/measuring` | Seeing what the renderer computes: debug views, statistics and the light meter | I | M | E | moved from `indirect/measuring-light` (H → I) |
| `light/materials` | Strata's material model | C | L | E | unchanged |
| `light/brdf` | The BRDF in code | I | L | E | + the reflection equation |
| `light/energy` | Keeping the light: energy compensation, the white furnace and specular anti-aliasing | I | M | E | moved from `indirect/energy`; home of the BRDF table |
| `light/sun` | The sun | I | M | E | split from `light/lights`; not W8 |
| `light/local-lights` | Point and spot lights | I | M | E | split from `light/lights` · W8 |
| `light/area-lights` | Area lights | I | L | E | unchanged · W8 |
| `light/many-lights` | Many lights: culling and clustered forward shading | I | L | E | unchanged · W8 |
| `light/shadow-basics` | Shadow mapping from first principles | C | L | E | unchanged |
| `light/sun-shadows-1` | Sun shadows I: stable cascades | I | L | E | + the cascades' occlusion section from `draw/occlusion` |
| `light/sun-shadows-2` | Sun shadows II: the soft shadow of a real sun | I | XL | E | unchanged |
| `light/local-shadows` | Shadows of point and spot lights | I | L | E | unchanged · W8 |
| `light/clearcoat-transmission` | Clear coat and transmission | I | M | E | unchanged |

### Part 10 — The image (order)

`image/why-post` (size S → M), `image/exposure` (metering and adaptation; EV100 is `light/units-exposure`'s),
`image/pre-exposure`, `image/tone-mapping`, `image/grading`, `image/encoding`, `image/lens-effects`,
`image/spatial-aa`, then:

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `image/motion-vectors` | Motion vectors and motion history | I | M | E | moved from `draw/motion-vectors` |

then `image/taa`, `image/motion-blur-dof`, `image/quality-settings`, `image/tutorial-post-effect`.

### Part 11 — Indirect light (order)

`indirect/problem`, `indirect/ibl` (the split sum's prefiltered half; links `light/energy` for the table), then:

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `indirect/sky` | The sky and the atmosphere | I | L | E | moved from `light/sky`; home of "sky as a light source" |
| `indirect/fog` | Aerial perspective and height fog | I | M | E | moved from `light/fog` · W8? (volumetric) |

then `indirect/ao`, `indirect/probes`, `indirect/ssr`, `indirect/gi-voxels`, `indirect/gi-cascades`,
`indirect/gi-limits`.

### Part 12 — Physics

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `physics/collision-detection` | Collision detection: shapes, broad phase and narrow phase | C | L | E | split from `physics/how-simulation-works` (Catto's BVH and GJK talks [S25], Ericson [S6]) |
| `physics/dynamics` | Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision | C | XL | E | split; the toy solver |
| `physics/capacity` | Physics at scale: capacities, growth and sliced creation | I | M | E | was `physics/scale-streaming` (first half) |

Order: `why`, `bodies-colliders`, `collision-detection`, `dynamics`, `world-step`, `contacts-triggers`, `queries`,
`collision-layers`, `character-controllers`, `capacity`, `tuning`.

### Part 13 — Animation

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `animation/skinned-rendering` | Skinned meshes in the renderer | I | M | E | moved from `draw/skinned`; after `animation/skinning` |

Mark `animation/state-machines`, `animation/blending`, `animation/time-events`, `animation/system`,
`animation/editor`, `animation/limits` W8? (the `animation-graph` stream of wave 8).

### Part 15 — Input

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `input/devices-to-intents` | How games read players: devices, events, polling and actions | C | M | E (G link) | new; audio-input §2 part B (events against polling, edges, actions) as concept |

`input/simulated` gains the `input.sequence` section of `editor/stepping`.

### Part 16 — Scripting

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `scripting/host-api` | The host API: contexts, guards and problems | I | L | E | split; scripting ch. 15 internals half |
| `scripting/tutorial-host-function` | Tutorial: adding a host function | T | M | E | split; adds `Wind::GetStrength` to WindZone |

### Part 18 — Large worlds and shipping

`worlds/physics-scripts` gains parking, reservation by the streamer and `MaxBodiesInRadius` from
`physics/scale-streaming`. Rows unchanged.

### Part 19 — The editor's interface (ids under `editor-ui/`)

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `editor-ui/imgui` | Dear ImGui from first principles | C | L | E | merges `editor/immediate-mode` and `editor/imgui` |
| `editor-ui/design-system` | The design system: theme, fonts, icons and UI scale | I | L | E | merges `editor/design-system` and `editor/ui-scale` |
| `editor-ui/shortcuts-status` | Shortcuts, focus and feedback: the status bar, toasts and idle throttling | I | L | E | merges `editor/shortcuts` and `editor/status` |

Other pages 16-32 keep their rows under `editor-ui/` (`imgui-backends`, `widget-kit`, `shell`, `lists`,
`inspectors`, `scene-view`, `game-view`, `launcher-dialogs`, `instrument-panels`, `ui-testing`, `tutorial-panel`).

### Part 22 — Capstone (new)

| id | Title | Kind | Size | Tracks | From |
| --- | --- | --- | --- | --- | --- |
| `capstone/plan` | Capstone I: designing a feature the way Strata does | T | M | E | new; WindZone (scene-ecs ch. 7 "WindZone or Spinner") grown into a feature: layers, registries, the rules that apply |
| `capstone/build` | Capstone II: from component to pixel | T | L | E | new; the system's forces on bodies, a debug gizmo, an inspector inactive reason, the script API, the command |
| `capstone/land` | Capstone III: tests, the feature test, a budget, the review and CI | T | L | E | new; `engineering/feature-test`, `perf-lab`, `contributing`, a `ci/` branch |

### Part 23 — Reference (new rows)

| id | Title | Source |
| --- | --- | --- |
| `reference/index` | Index of terms and engine identifiers | generated: glossary home pages + excerpt fences' symbols → every page that quotes or defines them (PBR [S3] adopt) |
| `reference/notation` | Conventions and notation | written, checked against `gpu/coordinates` and `basics/math-matrices`: axes, handedness, units, matrix order, depth, color spaces, the symbols of the rendering parts (Filament [S23] adopt) |

### Part 24 — Appendices (new row)

| id | Title | Kind | Size | From |
| --- | --- | --- | --- | --- |
| `appendix/game-ai` | Game AI in general: steering, pathfinding, navigation meshes and behaviour trees | C | L | new (curricula 1.13 [S-none]; Red Blob Games [S28]); Strata has none: the samples' `Wander.cpp` as the one example |

### Removed ids (all replaced above)

`basics/reading-code`, `world/serialization`, `world/prefabs`, `world/sub-scenes`, `assets/mip-streaming`,
`draw/skinned`, `draw/motion-vectors`, `light/lights`, `light/sky`, `light/fog`, `indirect/energy`,
`indirect/measuring-light`, `physics/how-simulation-works`, `physics/scale-streaming`, `make/gameplay-1/2/3`,
`make/reflections-gi`, `automation/outside`, `engineering/testing`, `editor/immediate-mode`, `editor/ui-scale`,
`editor/shortcuts`, `editor/status`, and the `editor/` ids of pages 16-32 (now `editor-ui/`). Nothing is published,
so no URL breaks.

---

## 7. The three tracks, written out

**G (game maker).** `start/welcome`, `how-to-read`, `install`, `first-game`, `what-an-engine-is`, (`coming-from`),
then `make/*` 1-39 in order. `basics/programming` before `make/cpp-for-scripts` for readers who never programmed.
G pages may link (as prerequisites) only to G pages and to these level-1 concept pages: `physics/why`,
`animation/problem`, `audio/sound-in-a-computer`, `input/devices-to-intents`, `scripting/why-scripts`,
`ui/what-game-ui-does`, `worlds/why-streaming`, `image/why-post`, `indirect/problem`, `light/units-exposure` (its
prerequisites must then be on G too: check it).

**E (engine builder).** `start/welcome`, `how-to-read`, `install`, `first-engine-change`, `what-an-engine-is`,
`coming-from`, `make/editor-tour`, `make/scenes-entities`, `make/first-script`, then parts 2 to 22 in the order of
section 5 (each basics page with a "Test out" box), the reference as needed. Specialist paths (curricula 5.3) published
on `start/map`: rendering (`basics/math-*`, `color`, `signals`, `math-light`, `gpu`, `assets` 1-6, `draw`, `light`,
`image`, `indirect`), simulation (`physics`, `animation`), tools (`editor`, `editor-ui`, `automation`).

**B (beginner).** `start/welcome`, `how-to-read`, `install`, `first-game`, `what-an-engine-is`,
`basics/programming`, `make/editor-tour`, `make/scenes-entities`, `basics/math-vectors`, `basics/math-matrices`,
`make/transforms-units`, `make/assets`, `make/materials`, `make/prefabs`, `make/cpp-for-scripts`, `make/first-script`,
`make/script-loop`, `basics/computer`, `basics/numbers`, `make/scripting-the-world`, `make/input`, `make/physics`,
`basics/math-rotations`, `make/characters-cameras`, `make/sound`, `make/ui`, `make/ui-interaction`, `make/export`,
`make/game-design`, `make/project-coin-run`. Then the reader chooses: G (continue at `make/lighting`) or E (continue
at `basics/bytes`, `basics/tools`, `basics/cpp` … then part 3). Theory and a running game alternate, as book.md
intends, and no page of B needs Monte Carlo or threads before the first finished game.

---

## 8. What I did not check

- The inventories' sections 1 (features) were not read line by line; the coverage of individual features by pages is
  the completeness critics' lens.
- Word counts are the outline's nominal sizes, not estimates of each page's content beyond the cases in F16.
- Whether `animation-graph`, `volumetric` and `editor-ux` will land in 0.8.0 is not knowable at the pin; F13 rests on
  `Docs/Plans/Wave8/plan.md` priorities and tranches.
- The site's ability to support "any of" prerequisites, per-track navigation for three tracks and generated part
  index pages was not checked against Starlight (the site operator's lens).
- The work the added pages add was not weighed against process.md's order of cuts.
