# Summary of the ten critiques of the plan

For the planner who revises the plan. It merges the ten reports in this folder. Critic keys:

| Key | Report | Key | Report |
| --- | --- | --- | --- |
| CF | `complete-foundation.md` | GM | `game-maker.md` |
| RA | `complete-rendering-a.md` | BG | `beginner.md` |
| RB | `complete-rendering-b.md` | CU | `curriculum.md` |
| SM | `complete-simulation.md` | SO | `site-operator.md` |
| ED | `complete-editor.md` | PL | `pipelines.md` |

A reference like "CU F3", "PL M6", "RA m2" or "BG 12" is that critic's own finding number, so the full text can be found
fast. A finding's severity is the highest severity any critic gave it. Where critics disagree, every position is given
with its evidence, marked **Contradiction**. This summary does not choose between them.

Merged findings: **8 blockers, 62 major, 41 minor.**

Contents: 1 verdicts · 2 findings by plan file · 3 the outline proposal · 4 the "one home per concept" rows · 5 engine
facts the critics checked · 6 questions only the owner can answer.

---

## 1. The ten verdicts

| Critic | Verdict (one line) |
| --- | --- |
| CF | Every item of foundation, build-test, scene-ecs and assets has a home. But the prerequisites of parts 4, 5 and 20 and the wave order are wrong, three concept pages hold internals, and about ten concepts have two homes (one of them is the pilot `core/time`). No blockers. |
| RA | render-core, render-scene and render-image map onto parts 6, 7 and 10 almost row for row. The seams fail: there is no compute, floating-point or sampling foundation, internals pages have no slot for "how engines solve it", some concepts have two homes, prerequisites are missing and some wave 8 pages carry no mark. No blockers. |
| RB | Parts 8 and 9 hold every feature, but the theory is placed wrongly. The BRDF table and energy compensation are in part 9 although part 8 uses them, no concept page teaches reflectance, exposure and HDR have four claimants, and there is no signals primer. Some W8 marks are wrong. No blockers. |
| SM | The simulation and gameplay areas are mostly covered and in good order. But the animation part ignores 0.8.0's planned animation graph (**blocker**), the waves break the prerequisite rule for ui, animation and input, shared concepts have no home rows, and five pages have the wrong kind or size. |
| ED | Almost every item of worlds-runtime, editor-core, editor-ui and automation has a page. But editor and worlds pages come before the pages they build on, several editor concepts have two homes, and track G lost undo, saving, recovery and the AI-agent chapters. No blockers. |
| GM | Track G fails a reader who has never programmed. The install leaves out the C++ build tools that the first success needs (**blocker**), the first finished game comes after 29 pages and about 117,000 words (**blocker**), the script API pages come before their topics, and the use-level homes are internals pages. |
| BG | A complete beginner cannot start from zero. No page teaches programming, a first program, the tools or school mathematics (**blocker**), and track B is only a sentence with no badge, no order and no reviewer persona (**blocker**). |
| CU | The outline has no per-page prerequisites or tracks, and the part prerequisites are wrong in 15 of 18 engine parts (**blocker**). Commands, the GPU and testing are taught after the pages that use them, the one-home table misses 20+ concepts, track B is not defined, and "engines in general" has little room. |
| SO | Every named version exists and fits. But the spike has no pass or fail line (**blocker**), and `site.md` contradicts `research/framework.md`. The image pipeline, the KaTeX check, the excerpt marks, the crawl, the base path, deployment, versions, Mermaid, the glossary, the generated reference, search and CI are wrong or not specified. |
| PL | The four pipelines are the right idea, but phase A has no editor binary at the pin (**blocker**). The recipe and fence formats name things that the engine and Expressive Code do not have, and the completeness test, the takes, the formats, tutorials, the reference listings and the engine additions need rework. |

---

## 2. Findings by plan file

Most findings change several files. Each finding is listed once, under the file it mostly changes, with the other files
named. Rows that the outline needs are in section 3, and home rows are in section 4.

### 2.1 `book.md`

**BK1 — blocker — Track B is a sentence, not a track** (BG 2 blocker; CU F9, F1; BG minor)
- *Problem:* `tracks:` has no `beginner` value. Nothing gives the B order, and nothing says what "interleaved with the
  first chapters of track G" means. The novice persona follows the track, so the primers are reviewed as an engine
  builder would read them, and no persona is written down. Reading Foundations in order is about 48,000 words, Monte
  Carlo included (CU).
- *Change:*
  - (a) `beginner` in `tracks` (style.md front matter) and `B` badges (book.md line 34).
  - (b) The exact B sequence: BG wants a new `plan/tracks.md`, CU wants it in book.md.
  - (c) Three personas with knowledge lists in style.md. BG's B persona: "has used a PC for games and school; has never
    programmed or opened a terminal; school math up to linear equations, no trigonometry; reads English at CEFR B1;
    Windows 11, a mid-range GPU".
  - (d) process.md line 46: pages of `start` and `basics`, and every level-1 page, get the B persona whatever their
    track (BG).
  - (e) Every basics page gets a "Test out" box: three questions, and a reader who answers all of them can skip the page
    (CU).
  - (f) `start/welcome` says which track a beginner continues on, and how far along B they must be (BG minor).
- Two B sequences were proposed:
  - BG §6.12: welcome → what-an-engine-is → how-to-read → install → first-game → `make/editor-tour` →
    `make/scenes-entities` → `basics/math-numbers` → `basics/math-vectors` → `make/transforms-units` →
    `basics/first-program` → `basics/programming-1..3` → `basics/debugging` → `make/cpp-for-scripts` →
    `make/script-loop` → `make/first-script` → `basics/math-change` → the rest of track G. Engine builders then go on
    to `basics/tools` → `basics/computer` → ….
  - CU §7: welcome, how-to-read, install, first-game, what-an-engine-is, `basics/programming`, `make/editor-tour`,
    `make/scenes-entities`, `basics/math-vectors`, `basics/math-matrices`, `make/transforms-units`, `make/assets`,
    `make/materials`, `make/prefabs`, `make/cpp-for-scripts`, `make/first-script`, `make/script-loop`,
    `basics/computer`, `basics/numbers`, `make/scripting-the-world`, `make/input`, `make/physics`,
    `basics/math-rotations`, `make/characters-cameras`, `make/sound`, `make/ui`, `make/ui-interaction`, `make/export`,
    `make/game-design`, `make/project-coin-run`. The reader then goes on with G (`make/lighting`) or E (`basics/bytes`,
    `basics/tools`, `basics/cpp` …, part 3).

**BK2 — major — The home table breaks "A game maker never has to read internals"** (GM F4; CU F7; BG 11)
- *Problem:* the table homes fixed steps, interpolation, stepping, simulated input, command scripts, the journal, debug
  views, residency and sub-scenes on E internals pages. Under "say one sentence and link", a make page cannot teach what
  a game maker does with them: the Tetris project, for example, needs the reader to write `expect`/`until` scripts.
- *Change:*
  - Add the column **Use-level home** and GM's rule: "A concept a game maker acts on has a *use home* in `make` that
    teaches everything a maker does with it; its E home explains the mechanism and links back."
  - Add CU's and BG's rule: "a G-track page lists as prerequisites only G pages and level-1 concept pages whose own
    prerequisites are on G; a concept page that a make page links for 'why' has prerequisites only in start, make or G
    primers". The strips plugin enforces it (SI17).
  - The use homes are in §4.

**BK3 — major — The one-home table misses about 80 concepts, and some of its rows conflict**
(CF F4-F9, F19; RA M4, M5, M13, M16, m3, m5, m8; RB F1, F4-F7, F9-F13, F16, F18, F23; SM F3, F7; ED F3, F5, F6, F12;
CU F8 and §3; BG 1, 3, 10)
- *Change:* replace the table with §4.1 and §4.2 (contradictory rows are marked there).

**BK4 — major — The design decisions have no home pages, and one of them is untrue as written** (CF F22; RA m6; RB F19;
CU F8)
- *Change:* add a Home column to the decisions (§4.3; the homes contradict each other).
- Reword "nothing may need history (TAA) to look right" so it names the engine's own exception: Medium's Checkerboard
  screen-space reflections need TAA (`Docs/Roadmap.md` 951-953) (RA m6).

**BK5 — major — "What Strata does not do": two items are wrong, one is conditional, and about 75 absences are missing**
(CF F10, F11; RA M8, M17; RB F17; SM F1, F13, F14; ED F13, F14; CU F19; BG 14)

Changes to the items it lists:
- "touch and IME":
  - SM: "touch input, and IME composition (text that the input method has committed arrives; the text being composed
    and the candidate window are not shown)".
  - ED: "touch input; input-method composition in game UI". On Windows, the editor's ImGui text fields do take composed
    text and place the candidate list.
  - The two are not in conflict: SM checked game input and ED the editor, and the wording needs both facts.
- "blend trees, animation layers" depends on wave 8's animation graph:
  - SM: "blend trees and animation layers (until 0.8.0's animation graph: see `animation/graph`), blend spaces in two
    dimensions, IK, additive clips, morph targets, clip compression".
  - CF: mark the item "checked at the 0.8.0 pin".
  - ED: keep both out of the list until tranche 2 is decided.
- "shape sweeps" → "sweeps are used only inside the character controller" (SM).
- "gameplay networking": add that the engine has network code for editor automation only, in a Tooling layer that games
  never link (ED).
- "particles, terrain tools, water and decals": confirmed absent (RA, RB).
- Mark the items that wave 8 streams can change "re-check at v0.8.0", and add them to the pin tool's list (RA M8).
- Homes:
  - The subsystem page states what it lacks (`animation/limits`, `indirect/gi-limits`, or a section of the page). The
    appendix only indexes these and gives the general technique (CU F19).
  - Each item gets its paragraph on the page where a reader would look (RB F17 names `light/fog`, `light/area-lights`,
    `indirect/problem`, `indirect/probes`, `indirect/ssr`, `light/materials`, `image/quality-settings`,
    `image/encoding` and `indirect/gi-limits`).
  - Add to the From of `appendix/not-in-strata`: "`Docs/Releases/0.8.0.md` 'Known issues' and 'Not in this release'"
    (CF).

Items to add (the evidence is in §5):
- *Assets, core, platform* (CF; RA): OBJ and FBX import; BC6H (HDR textures stay RGBA16F); mesh streaming, per-LOD mesh
  streaming included; virtual texturing and sparse residency; custom shaders and material graphs; mobile, console and web
  targets; work stealing, fibers and frame task graphs; run-time engine plugins; leaving scripting out of a build.
- *Rendering* (RA M17; RB F17; CU F19):
  - anti-aliasing and resolution: MSAA and supersampling; rendering below native resolution, dynamic resolution and
    temporal upscalers (left out by decision, not missing);
  - output and image: HDR display output; post-process volumes; non-photorealistic rendering;
  - architecture: hardware ray tracing; mesh shaders and meshlets; a render or frame graph; portals;
  - lights and shadows: area lights (unless 0.8.0 ships rect lights) and soft light from sized lamps; a second shadowed
    sun; virtual shadow maps;
  - indirect light: lightmaps and baked GI; reflection probes captured at run time; reflections of and through
    transparent surfaces; GI from lamps and from moving or skinned objects;
  - materials and assets: subsurface scattering, sheen, anisotropy, iridescence, specular and thickness maps; EXR import;
  - transparency, fog and sprites: order-independent transparency; volumetric fog, light shafts and fog volumes;
    billboards and impostors;
  - other: complex-script text shaping and CFF fonts; compute and dual-quaternion skinning; debug drawing from scripts.
- *Physics* (SM F14; CU; ED): height-field and cylinder colliders; cloth, soft bodies, destruction, fluids, buoyancy;
  bodies beyond 1e5 m; bodies that move between world cells.
- *Animation* (SM; CU): additive clips; sync markers (until the graph lands); inertialization; dual-quaternion and GPU
  compute skinning; retargeting beyond matching names; float curves; a skeleton overlay in the viewport; motion matching.
- *Audio* (SM; CU): occlusion; virtual voices and voice priorities; streaming from disk or packs; an attenuation model per
  component (components always use Inverse); listeners per world; reverb zones; music systems and ducking.
- *Input* (SM): action modifiers, chords, processors and interactions; force feedback; assigning devices to players for
  local multiplayer.
- *Scripting* (SM): languages other than C++; script calls from other threads; static linking of modules.
- *Game UI* (SM; CU): scroll views, drop-downs, rich text, multi-line input fields; localization and right-to-left text;
  lit world-space UI; game hit tests that respect geometry in front.
- *Editor and export* (CF; ED; CU): a prefab edit mode; editing several scenes at once; panels torn out into windows;
  editor extensions written by a game project; automating an exported game; exports for another platform, macOS app
  bundles, signed exports, crash reports in shipped games; in-game consoles and console variables.
- *Gameplay* (BG; CU): game AI, pathfinding and navigation meshes (CU also adds `appendix/game-ai`).

**BK6 — major — Track E's reading order cannot hold** (CF F2; CU F3, F10)
- *Problem:* the Scenes pages use asset terms before Assets defines them. E pages use the editor from part 4 on, but
  track E never reads the editor tour.
- *Change*, **Contradiction**:
  - CF keeps the part order and changes book.md line 29 to "*Scenes* up to `world/reflection`, *Assets* up to
    `assets/loading`, the rest of *Scenes*, then any subsystem part".
  - CU reorders the parts (OL7), puts tracks G and E on `make/editor-tour`, `make/scenes-entities` and
    `make/first-script`, and makes `start/first-engine-change` E only.

**BK7 — major — There is no book-wide running example and no capstone for engine builders** (CU F17; BG 13)
- *Change* (CU), named in book.md:
  - **Coin Run** is the G example. It is seeded in `start/first-game`, finished in `make/project-coin-run`, and later lit,
    given a look, a menu and an export.
  - **WindZone** is the E example. It is created in `world/tutorial-component`, its force is applied in a physics
    exercise, `gpu/debug-drawing`'s exercise gives it a gizmo, `editor/tutorial-command` a command and
    `scripting/tutorial-host-function` a host function.
  - A box "What happens to Coin Run here" opens each engine part.
  - A capstone part (§3.2).
- BG: build Coin Run in stages, each stage closing the page that enables it.
- **Contradiction** with GM F11 about how Coin Run is designed (OL4).

**BK8 — major — There is no primer kind** (BG 7)
- *Change:* add the kind `primer` (letter P) to book.md's table of kinds, and add its shape to style.md: "what you can
  do after this page → what you already know (links) → small steps, each a worked example then a try-it → common
  mistakes → a practice set with worked solutions → summary".
- It is used for every basics page except reading-code, and for `make/cpp-for-scripts`.
- CU's tables keep the primers as kind C. The difference is not argued.

*Minor:*
- **BK9** (CF F20): extend the last row to "'Module', 'layer', 'registry', 'service' (two meanings each) | `core/map`".
  The other words with two meanings (prefetch, block, journal, snapshot, hot reload, batch) get two qualified glossary
  entries each (PI16).
- **BK10** (RB F24; CU §5; BG; ED): the page counts of the Parts table follow section 3. RB counts 288 pages; CU counts
  305, plus generated part index and review pages; BG adds 15 primers; ED adds three make pages.
- **BK11** (SO 13): for readers who are contributors or agents, consider `starlight-llms-txt` 0.12.0.

### 2.2 `outline-1.md` … `outline-4.md`

**OL1 — blocker — The outline has no per-page prerequisites or tracks, and its part prerequisites are wrong**
(CU F1 blocker; CF F1, F2, F3, F22, further; RA M9, M10; RB F8; SM F5; ED F2, F11; BG 11, 12; GM F5, F18)
- *Problem:* the front matter's `prerequisites` and `tracks`, the track navigation, the novice reviewer's reading list
  and the waves all need per-page data the outline does not have, so writers would invent it. About 45 pages need a page
  that comes later on every track (CU).
- *Change:*
  - Add the columns **Needs** (at most five ids; transitive ones left out) and **Tracks** (G, E, B).
  - Allow "any of" prerequisites (`[[make/cpp-for-scripts, basics/cpp]]`).
  - Correct the part lines as in §3.1.
  - A prerequisite that points forward fails the build (SI17).
  - Do this before the pilot, because two pilot pages change.

**OL2 — blocker — Nothing teaches programming, a first program or the tools** (BG 1, 6; GM F7; CU F9, F12)
- *Problem:* `basics/cpp` is about *reading* Strata, and `make/cpp-for-scripts` is one L concept page that comes before
  the reader can run any code. No page has a first program, the terminal, git, a code editor or a debugger.
- *Change*, **Contradiction** about the form (rows in §3.2):
  - BG puts it in basics:
    - `basics/first-program` (T, M), `basics/programming-1..3` (P, M each), `basics/tools` (T, M),
      `basics/debugging` (T, M), and `basics/cpp` split into four M pages;
    - `make/cpp-for-scripts` becomes the bridge page "C++ in a Strata script" (M), with programming-1..3 as its
      prerequisites;
    - the minimum is first-program, programming-1..3, the cpp split and the bridge;
    - if no pages are added, book.md lines 19 and 22-23 must name the entry knowledge instead.
  - CU: `basics/programming` (C, XL) is B's first primer, plus `basics/tools` (T, M) and `core/debugging` (H, M);
    `basics/cpp` stays XL with Needs `basics/programming`; `make/cpp-for-scripts` stays L with the same Needs.
  - GM puts it in make:
    - `make/cpp-1` (T, L), `make/cpp-2` (T, M) and `make/gameplay-math` (T, M) replace `make/cpp-for-scripts`;
    - they come after `make/first-script`, so that the script module is the reader's playground;
    - the G door of `start/welcome` says that game logic is C++ (no visual scripting) and that an agent can help.
  - Home row: "Programming basics | `basics/programming(-*)` | `make/cpp-for-scripts` links" (BG; CU).

**OL3 — blocker — The animation part is planned on 0.7.0, but 0.8.0 plans the animation graph** (SM F1 blocker; CF F11;
RA M8; ED F14; CU F13)
- *Evidence:* `Docs/Plans/Wave8/plan.md` §4.5 and its tranche table put `animation-graph` first in tranche 2, and 0.8.0
  comes after landing 2. None of it is in the tree at the pin (§5).
- *Change:*
  - The W8 (animation-graph) marks of §3.3, and the new rows `animation/graph` and `animation/sync-layers` (W8).
  - Write the unaffected pages now: `animation/problem`, `skeletons`, `clips`, `skinning`, `importing`.
  - README decision 5 and process step 7 name the animation graph.
  - Add to process step 6: "if 0.8.0 is cut from landing 1, the W8 (animation-graph) marks are removed and the two new
    pages are dropped" (SM).
- The critics mark different sets: SM 12 pages, CF 3 (state-machines, blending, limits), ED 4 (those plus
  `make/animation`), CU 9 (marked "W8?").

**OL4 — blocker — In part make, the first finished game comes after 29 pages (about 117,000 words), and the API pages come
before their topics** (GM F2 blocker, F3; BG 13; CU F14; SM F4)
- *Problem:* the projects are pages 30-32 of 33. `gameplay-2` and `gameplay-3` need physics, audio, animation, UI, input
  actions and quality, which all come after them. Three rendering L pages come before any code. The research says to
  interleave the projects.
- **Contradictions:**
  - *gameplay-2 and gameplay-3:*
    - SM F4 and GM F3: dissolve them into the topic pages; the full listing is only in `reference/script-api`.
    - CU: keep them as T pages after their topics, as `make/scripting-physics-animation` and
      `make/scripting-player-side`.
    - SM's fallback: put them after `make/sound` and `make/levels-saves` as "API at a glance" pages that teach nothing
      first.
  - *gameplay-1:* GM makes it `make/scripting-scene` (H, L), CU makes it `make/scripting-the-world` (T, L), and BG wants
    the gameplay pages to be kind T.
  - *Order (both orders are in §3.2):*
    - GM: three blocks, each ending in a project; Coin Run is page 22.
    - CU: one order of 39 rows; Coin Run is 19, Tetris 31, the platformer 38.
    - BG: Coin Run is built in stages after the pages that enable them, its project page becomes a short assembly, and
      Tetris follows the recipes.
  - *Coin Run:*
    - GM redesigns it as a rolling ball on Basic 3D: an input action, force applied in `OnFixedUpdate`, a camera that
      follows the drawn position, trigger coins as a prefab, a HUD, a sound, a win panel, a restart and an export. Its
      From becomes "gamedev G8 (rolling-ball variant); skill make-a-game §4-8".
    - CU keeps gamedev G8 (a first-person `CharacterController` player) and moves it to position 19.
  - *First script and C++:* GM puts `make/first-script` before the C++ pages. BG puts the primers, `make/cpp-for-scripts`
    and `make/script-loop` before `make/first-script` (or teaches `deltaTime` in `make/cpp-for-scripts`). CU's order is
    `make/cpp-for-scripts` → `make/first-script` → `make/script-loop`.
  - *`make/play-test-debug`:* GM puts it right after the scene-scripting page, with debugger attach. CU puts it after
    Tetris (position 32).

**OL5 — blocker — `start/install` leaves out the C++ build tools that the first success needs, and part start does not
fit a beginner** (GM F1 blocker; BG 9; CU F16, F23)
- *Evidence:* pressing Play in a sample builds its scripts first (PackageReadme "Make a game"). Without Visual Studio's
  C++ workload the editor stops with a message (`ScriptToolchain.cpp` L272-276), and installing that workload alone takes
  longer than "30 minutes".
- *Change:*
  - `start/install` becomes GM's row (§3.2): H, M; the release download, tabs per OS, the script toolchain, a
    recommended code editor, and a final check (`script.status`, or Build Scripts on the generated `Spinner.cpp`).
  - The source build moves out. GM moves it to `start/first-engine-change`, BG to `engineering/building` (a small
    difference).
- **Contradictions:**
  - *`start/first-game`:* GM keeps a sample: play the Tetris copy within five minutes, then Basic 3D with falling
    bodies, then attach the generated Spinner, with the "30 minutes" counted after the install. BG keeps it free of
    code: gamedev G2-G3 on Basic 3D, no samples, based on gamedev rather than the skill; otherwise the time goes out of
    the title.
  - *Order:* BG puts `start/what-an-engine-is` second. CU and GM put it after `start/first-game`.
  - *`start/first-engine-change`:* E only, inside start (GM; CU), or moved to `engineering/first-change` (BG, as an
    option).

**OL6 — major — Primers that many parts need are missing** (RA M2, M6, m2, m4; RB F6, F7, App. D; ED F12, F21; CU F12,
F16; BG 3, 4, 5, 8, 25; GM F7)
- *Floating point* (RA M2; ED F12; CU F12; BG 4). **Contradiction:**
  - Its own page `basics/numbers`: CU after `basics/computer`, ED after `basics/bytes`, one of RA's options.
  - Inside `basics/bytes`, raised to L with numbers in the title: BG and RA's other option.
- *Sampling, aliasing, filtering, noise* (RB F7; CU; BG 4): `basics/signals` (RB after `basics/math-light`, CU after
  `basics/color`), or `basics/sampling` (BG). **Contradiction:** RA m4 homes "pixels as samples and the kinds of
  aliasing" in `gpu/how-a-gpu-frame-works` (or `basics/gpu`).
- *School algebra, powers, logarithms, trigonometry:* BG adds `basics/math-numbers`, also on track G. GM instead gives G
  readers `make/gameplay-math` (a different home).
- *Change over time, Euler, Newton:* BG adds `basics/math-change`. *Data structures and their cost:* BG adds
  `basics/data-structures`.
- *Splitting the math pages:*
  - `basics/math-vectors` (XL): CU splits it into vectors, matrices, projection and geometry (L, L, L, M); BG into
    vectors (M) and matrices (L).
  - `basics/math-light`: BG splits it into probability (M) and the sphere (M); CU keeps it.
- *GPU basics in Foundations:* RA M6a moves `gpu/how-a-gpu-frame-works` to `basics/gpu`.
- *Processes:* pid, exit code, standard streams, environment and child processes go into the scope of `basics/computer`
  (ED F21).
- *JSON* (BG 25): a short home in `start/how-to-read` ("How to read a command"), named in `basics/bytes`'s title; G pages
  say that the command tab is optional.
- *Additions to existing primers:*
  - `basics/computer`: allocators, SIMD, AoS against SoA (CU).
  - `basics/color`: chromaticity, white point and gamut (RA m2); it states the working color space, scene-linear
    Rec. 709 (RB App. D), and it is the home of the half-float range (RB F6).

**OL7 — major — Parts and pages come before what they need** (CF F1, F2; CU F2-F6, F20; RA M5, M6, M9, M10, M13; RB F1,
F8; SM F2, F3, F7; ED F1, F3, F6; BG 12)
- **a. World, assets and the GPU.** **Contradiction:**
  - CF keeps the part order and adds prerequisites. It writes `assets/textures`, `assets/uploads` and
    `assets/mip-streaming` in wave 5, after gpu, and changes track E's order (BK6).
  - CU reorders the parts: world (8 pages) → gpu → assets. `world/serialization`, `world/prefabs` and `world/sub-scenes`
    move into assets as `assets/scene-documents`, `assets/prefabs` and `assets/sub-scenes`, and the part becomes "Assets
    and scene documents". Its alternative order is gpu → assets → world.
  - RA M6 moves `gpu/how-a-gpu-frame-works` to `basics/gpu` and merges `gpu/upload-queue` into `assets/uploads`. If the
    split stays, `gpu/resources-lifetimes` and `gpu/upload-queue` are written in wave 3.
  - BG writes gpu up to `gpu/upload-queue` in wave 3.
- **b. Six earlier pages, and every tutorial's second tab, need the editor's commands.** **Contradiction:**
  - CU splits part 18. Pages 1-15 become the part "The editor's core" (`editor`), right after Assets; pages 16-32 become
    the part "The editor's interface" (`editor-ui`), where part 18 is now.
  - ED keeps part 18, moves pages into it (`worlds/editing` → `editor/worlds`, `automation/journal` → `editor/journal`)
    and writes the dependent pages in later waves.
  - SM moves `input/simulated` and `ui/testing` to wave 6.
- **c. Cycles and forward references in the rendering parts.**
  - Agreed:
    - `indirect/energy` becomes `light/energy`, right after `light/brdf` (RB F1; CU F4).
    - `indirect/measuring-light` moves into part 8 as an internals page (RB F11; CU F4).
    - The cascades' occlusion and the cascade cache go to `light/sun-shadows-1` (RA M5; RB F8; CU F4).
    - The image part comes before the indirect part (RB F8; CU F4).
  - **Contradictions:**
    - *The measuring page:* after `light/energy` (RB) or after `light/units-exposure` (CU).
    - *`light/sky` and `light/fog`:* they stay in part 8 and are split (RB), or they move to `indirect/sky` and
      `indirect/fog`, after `indirect/ibl` (CU).
    - *`draw/motion-vectors`:* it moves to `image/motion-vectors` (CU), or it stays and its allocation drops TAA as a
      prerequisite (RB F8).
    - *`draw/skinned`:* it moves to `animation/skinned-rendering` (CU), or it stays with Needs `animation/skinning` and
      `animation/culling` (RA M9).
    - *Mip streaming:* CF says `assets/mip-streaming` needs `draw/asset-requests`; RA says `draw/asset-requests` needs
      `assets/mip-streaming`; CU moves the page to `draw/mip-streaming`, after `draw/visibility-feedback`.
- **d. Testing is taught in the last part.** **Contradiction:**
  - CU moves `engineering/testing` to `core/testing` (C, L), after `core/conventions`.
  - CF keeps it in part 20 and splits it into `engineering/testing` (C, M) and `engineering/test-program` (I, L).
  - RA homes "writing a GPU test" in `gpu/first-triangle` and writes `image/tutorial-post-effect` in wave 6.
- **e. `physics/scale-streaming` needs part 17** (CU F6; SM F7; ED F6).
  - SM and ED keep the page, give it Needs `world/sub-scenes` and add a home row.
  - CU renames the page `physics/capacity` and moves parking, reservation and `MaxBodiesInRadius` to
    `worlds/physics-scripts`.
- **f. `input/simulated` and `editor/stepping` zigzag across four parts** (CU F6; SM F3). **Contradiction:** SM homes
  holds counted in fixed steps, `input.sequence` and `input.click` in `editor/stepping`; CU moves the `input.sequence`
  section to `input/simulated`.
- **g.** Part ui (wave 4) needs `gpu/text` (wave 5) (SM F2; BG 12; CU F20). This is fixed in the process waves (PR1).
- **h.** `gpu/first-triangle` comes before `gpu/shaders` and `gpu/coordinates`, and it needs building and testing
  (BG 12). Move it after `gpu/coordinates`, with Needs `start/first-engine-change` (or `engineering/first-change`).

**OL8 — major — W8 marks are wrong or missing beyond animation** (RA M7, M8; RB F2, F3, F11, F14, F15, F22; CF F11, F12;
SM F21, F23; ED F18; CU F13; GM F9)
- *Change:* the marks of §3.3.
- **Contradictions:**
  - *`light/lights`:* RB removes the mark; CU splits the page into `light/sun` and `light/local-lights` (W8).
  - *`light/area-lights`:* RB gives it a new scope with a phase A part; SM takes it out until a release brings area
    lights; CU leaves it unchanged.
  - *`light/many-lights`:* RB writes it in phase A and revises one section later; CU keeps it W8.
  - *`image/quality-settings`:* RA gives it a new mark W8r (revised in phase B); RB marks it W8, or requires that its
    prose names no preset values and that only the generated reference holds the rows.
  - *Wave 8 work that has already landed:* CF adds a new mark W8L on 14 pages, re-read at the pin move; SM and ED add no
    mark, only a "new in 0.8.0" label and targeted re-reads.

**OL9 — major — Pages whose kind cannot hold what is allocated to them** (CF F15, F16, further; SM F9, F11, F12; RB F5,
F10, F11, F13, F14; ED F7; CU F11, F15; GM F5; BG 7, 10)
- The rows are in §3.2.
- Concept pages that hold internals:
  - `engineering/testing` (C): the internals of the test program have no page;
  - `assets/textures` (C): it holds the importer, the cooker and Strata's own BC7 encoder;
  - `light/materials` (C): it holds the 144-byte GPU record.
- Tutorial and how-to pages that hold internals:
  - `scripting/host-api` (T): it holds the host API's internals;
  - `animation/editor` (H): it holds the internals of `AnimationPreview`;
  - `indirect/measuring-light` (H): it is the home of a concept.
- Pages of part make:
  - `make/reflections-gi` (H): it merges three tutorials and is never run;
  - `make/gameplay-*` (H): CU and BG want T, while GM keeps H for `scripting-scene`;
  - `make/assets` (H): CU wants T.
- Pages in the wrong part or of the wrong kind:
  - `basics/reading-code` (H) comes before `core/map`: CU wants `core/reading-code` (T);
  - the primers are C, where BG wants P;
  - `automation/outside` is a G tutorial inside an E part;
  - `assets/robustness` is I, where CF wants C, as the home of untrusted input.
- Missing concept pages:
  - input has no concept page: SM's `input/how-input-works` and CU's `input/devices-to-intents` are the same page with
    a different id and title;
  - no concept page teaches reflectance: RB adds `light/reflectance`.

**OL10 — major — Some sizes cannot hold their content, and the XL no-split rule** (CF F14, F17, F18; RA M12, m1, m2;
SM F6, F8, F15, F17-F19; ED F8, F16; GM F10, F12; CU F16, F21; BG 8; SO 14)
- *Size changes:* see §3.2.
- *Rule changes to outline-1 line 8:*
  - BG: "Pages of tracks B and G, and all primers, are at most L. A larger subject becomes several pages."
  - GM: project tutorials may be split into numbered pages, or else each of their sections must end in a playable,
    downloadable state.
  - SO: the no-split rule is for prose pages; `reference/commands` may split by command group.
- **Contradiction:**
  - CU merges three pairs of editor-interface pages: `immediate-mode` into `imgui`, `ui-scale` into `design-system`, and
    `shortcuts` with `status`.
  - ED makes `editor/undo` XL, `editor/imgui-backends` L (or splits it) and `editor/lists` L, and splits
    `editor/launcher-dialogs`. ED would merge `shortcuts` with `game-view` instead.

**OL11 — major — Material for game makers sits in E parts, or was dropped** (GM F5, F6, F16; ED F9-F11; CU F15)
- Moves:
  - the how-to half of `animation/editor` → `make/animation`;
  - the use half of `physics/tuning` → `make/physics`;
  - `ui/testing` → `make/automated-playtests`;
  - `worlds/measuring` → `make/big-scenes-fast`, retitled "Making your game run fast";
  - using the debug views → `make/lighting` (and the albedo audit → `make/materials`, RB F11);
  - `automation/outside` → part 1;
  - `input/rebinding` is reworded to the engine side, and the rebinding menu stays in `make/input` (GM).
- Part 19 becomes track E (ED F11).
- **Contradictions:**
  - *The page moved from automation:* ED's `make/command-line` (T, M); GM's `make/commands` (H, M), with `start/terminal`
    (H, S); CU's `make/editor-from-outside` (T, M).
  - *AI-agent pages:* ED proposes two, `make/ai-agent` (T, M) and `make/agent-game` (T, L); GM one, `make/with-an-agent`
    (H, M); CU none, keeping `make/automated-playtests` as "…and AI agents".
  - *Undo, saving and recovery for game makers:* ED adds `make/undo-save-recover` (H, S); GM makes `make/editor-tour`
    their use home.

**OL12 — major — Topics that no page holds** (CU F12, F17, F18; GM F17, F19, F22; BG 14; RA M1, m9; RB F5, F10, F12,
F13; SM F10, F12; ED F7, F8, F17; CF F14-F16, F21, F22)
- New rows, all in §3.2:
  - part start and part make: game design (GM, CU, BG; the ids differ), patterns for game code (CU), coming from other
    engines (GM, CU), the project's files (GM), `start/map` (CU);
  - foundations and core: `core/debugging` (CU), `core/files` (CF);
  - the GPU: `gpu/compute` (RA; CU instead retitles `gpu/shaders`), `gpu/debugging` (CU; RA instead adds a section to
    `gpu/frame-tour`);
  - light and indirect light: `light/reflectance`, `light/material-data`, `light/atmosphere`, `indirect/seam` (RB);
  - assets, editor and worlds: `assets/texture-cooking` (CF), `editor/script-builds` (SM: no inventory surveyed
    `ScriptBuild*`), `editor/projects`, `editor/settings-windows`, `worlds/game-identity` (ED);
  - engineering: `engineering/test-program`, `engineering/measuring` (CF);
  - reference and appendices: `reference/scene`, `reference/performance` (CF), `reference/index`, `reference/notation`
    (CU), the game-AI appendix (CU);
  - book apparatus: a generated index and review page per part, and the capstone part (CU).

**OL13 — major — The figure rule of parts 8 to 10 asks for pictures that cannot exist** (RA M15; RB F21)
- *Change:* replace outline-3 lines 3-4. The two wordings fit together:
  - RA: "Every page of parts 8 to 10 that teaches a visible effect has figures rendered by the engine: the effect off
    and on where it has a switch, its debug view where one exists, and a sweep of its main setting; the part brief lists
    which page gets which". `image/pre-exposure` is exempt (it uses render-image's diagrams 3-4).
  - RB: "Every page of parts 8 to 10 takes its figures from its inventory's 'Screenshots' and 'Diagrams' lists (RD 4,
    RI 4, render-image 4); a feature with a switch gets off and on, its debug view and a sweep; one without gets a
    diagram or a lab."

**OL14 — major — The reference part lost material and names wrong sources** (CF F21; RA M7, M11; ED F18, F22; CU F18;
SO 12, 14; PL m14; SM F1)
- The rows are in §3.2:
  - new pages: `reference/scene`, `reference/performance`, `reference/index`, `reference/notation`;
  - retitled: `reference/assets` and `reference/renderer`;
  - corrected sources: `reference/editor`, `reference/script-api`;
  - other changes: `reference/commands` may split; `reference/glossary` becomes one list; `reference/animation` gets W8;
    `reference/worlds-runtime` is re-checked at the pin move.

**OL15 — major — The order inside parts** (CF F13, further; ED F4, F5, F19; SM F20; BG 12; RB F3, F24; CU §6)
- `core/conventions` becomes the second page, after `core/map` (CF F13). **Contradiction:** CU's order keeps it ninth.
- `editor/deferred-commands` becomes the third page, after `editor/commands` (ED F4). `editor/camera-viewport` moves next
  to `editor/scene-view` (ED F5).
- `physics/collision-layers` moves before `physics/contacts-triggers` (SM F20). **Contradiction:** CU's order puts it
  after `physics/queries`.
- `world/tutorial-component` moves to the end of part 4, because its skill needs a serialization round trip (CF).
- `gpu/first-triangle` moves after `gpu/coordinates`, and `make/script-loop` before `make/first-script` (BG 12; for the
  second, see the contradiction in OL4).
- `make/large-worlds` keeps the in-editor Play check; its exported-start check moves to `make/export` as "A world that
  waits for its ground" (ED F19).
- `light/area-lights` moves after `light/many-lights` (RB F3). Parts 8 and 9 get a new order (RB F24; CU §6).

*Minor:*
- **OL16** — From columns (CF F24, F25; ED F15, F20, F22; RA m8; GM F11; SM F10): the From of the primers,
  `automation/agents`, `editor/inspectors` (the Asset tab), `reference/editor` (three inventories), `make/ui`
  (`TextComponent`), `make/project-coin-run`, and the retitled `engineering/generated-code`. The rows are in §3.2.
- **OL17** — small size changes (CF; RA; SM; CU): `world/interpolation` L, `image/grading` L, `image/motion-blur-dof`
  split, `animation/clips` L, `make/input` L, `scripting/crash-containment` XL (or split), `draw/visibility-feedback`
  could be S, `make/assets` perhaps L.
- **OL18** — retitles:
  - `ui/text` → "Text and text fields" (SM F16);
  - `make/levels-saves` → "Levels, loading screens and save files" (GM F23);
  - `editor/play-mode` → "Play mode: the running copy" and `editor/command-scripts` → "Command scripts and batches" (ED);
  - `gpu/vulkan-nvrhi` and `gpu/binding` (RA).
- **OL19** — `appendix/math-cheatsheet`: add a "how to read the symbols" table (Σ, ∫, ‖v‖, ·, ×, θ) that names the page
  teaching each symbol (BG).

### 2.3 `style.md`

**ST1 — major — The internals shape has no place for the general technique or the alternatives** (RA M3; CU F11)
- *Problem:* the engine parts hold 31 concept pages against 163 internals pages (CU), so "engines in general" has almost
  no room.
- *Change:* the internals shape becomes:
  1. the job;
  2. **the problem and how engines solve it**: the approaches with their costs, at most a fifth (RA) or a quarter (CU)
     of the page, skipped when a concept page of the part holds it (CU);
  3. the map, the contract, the toy version, the real code;
  4. **the alternatives Strata did not choose**: a table of technique, who uses it, and what Strata would gain and lose
     (CU);
  5. the tests, how to change it, what went wrong before.
- The part briefs name which internals pages carry the general section (RA).

**ST2 — major — The language rules cannot be measured** (BG 20, §4)
- *Change:*
  - Sentences of 20 words or fewer on average, none over 35; paragraphs of at most five sentences.
  - At most four new terms per section; every acronym spelled out at its first use on the page.
  - A word list: about 3,000 common English words, plus the glossary, plus the code's names. A word outside it is
    defined.
  - No noun stacks of more than two nouns, no phrasal verb where a single verb exists, and no pronoun far from its noun.
  - Target reading level: CEFR B1.
  - "Never copy sentences from the inventories, AGENTS.md or the Developer Guide."
  - Five pairs of good and bad sentences, and one exemplar page that shows the voice.
  - The style linter measures these (SI17).

**ST3 — major — The code rules assume a reader who already reads C++** (BG 17)
- *Change:*
  - On level-1, B and G pages, a quote is at most 25 lines.
  - Each quote is preceded by its idea in plain words (or as Pseudocode) and followed by at most five numbered callouts
    that say why.
  - The first use of a C++ feature not yet taught adds a `:::question` ("What is `std::optional`?") of two lines and a
    link.
  - `start/how-to-read` gets a section "How to read code you do not understand yet".

**ST4 — major — Nothing helps readers who fear mathematics** (BG 18)
- *Change:* a section "Math for readers who fear it":
  - The order: the idea in words and a picture → one example with small numbers worked by hand → the formula, each
    symbol read aloud with its units → the code → a check at the limits.
  - Long derivations go in a collapsible "Where this comes from" box marked "you can skip this".
  - Each part's first page has a notation table.
  - G pages state results in words, with formulas in boxes.
  - Ban "it follows", "clearly" and "it is easy to see".

**ST5 — major — Teaching devices are missing, and the exercise rule does not fit G and how-to pages** (BG 19; GM F21)
- *Change:*
  - Kinds of exercise: worked examples and faded examples, Parsons problems, predict-then-run, and check questions whose
    wrong answers come from the inventories' "Newcomer error" items.
  - "At least one worked example before the first exercise."
  - The asides `:::simplified` and `:::analogy` (the latter with "where it breaks").
  - A "Common mistakes" section in the concept and primer shapes.
- The exercise rule:
  - BG: "at least one exercise is done in the editor (G) or runs code on the reader's workbench (B, E)".
  - GM: "(for G pages before `make/first-script`: does something in the editor and checks its result, or runs a
    command)".

**ST6 — major — The tutorial shape needs pictures, recovery steps and checkpoints** (BG 16; GM F6, F12)
- *Change:*
  - Every step has the action, "you should see" with a whole-editor picture wherever the screen changes (the control
    to click marked), and "if you don't".
  - A checkpoint project after each section, downloadable (PI8).
  - "A step with no UI says so and gives the command; its page lists `make/commands` as a prerequisite" (GM).
  - Under Figures: a picture after each tutorial step that changes the screen (BG §4).

*Minor:*
- **ST7** (CF F4): the example title in the front matter (style.md line 38) follows the retitle of `core/time`.
- **ST8** (BG §4): "No mention … of agents" → "of the agents that wrote the book" (the automation pages are about
  agents).
- **ST9** (BG minor): add a `time:` field (minutes) shown on the top strip, and say on the strip what levels 1-3 mean.
- **ST10** (BG minor; CU F22): each `learn` line gets one Summary sentence and at least one check question.
  `learn: [{id, text}]`; questions and exercises name the ids they test; the strips plugin fails a page with an untested
  objective; the novice reviewer reports per objective.
- **ST11** (SM F21; ED F18): features added after 0.7.0 are labelled "new in 0.8.0".
- **ST12** (BG minor): on G pages, say what a number measured on the RTX 5090 means on a typical player's machine, or
  give it as a share of the frame.

### 2.4 `site.md`

**SI1 — blocker — The spike has no pass or fail line** (SO 1)
- *Problem:* budgets "set by the spike" can never fail. `framework.md` §7 had numbers, which site.md dropped. The Quarto
  fallback is not cheap either: `:::why`, `:term[x]` and fence meta have no Pandoc spelling, so moving needs a converter
  and a rewrite of every plugin.
- *Change:* write SO's appendix E table into site.md before the spike. Each row names its machine (i7-13700K or GitHub
  `ubuntu-latest`) and what happens when it fails.

  | Measure | Pass |
  | --- | --- |
  | Warm full build | ≤ 4 min on the i7-13700K, ≤ 8 min on `ubuntu-latest` |
  | Cold build, pictures and diagrams included (`ubuntu-latest`) | ≤ 30 min |
  | Rebuild after editing one page | ≤ 90 s |
  | `astro dev`: start, refresh after an edit | ≤ 60 s, ≤ 3 s |
  | Peak memory of the build | ≤ 4 GB |
  | Two builds of one commit | identical `dist/` except time stamps |
  | `dist/`, one version | ≤ 400 MB; HTML+CSS+JS ≤ 80 MB; ≤ 15,000 files |
  | Largest page (brotli); median page | ≤ 300 KB; ≤ 60 KB |
  | JavaScript per page without search | ≤ 40 KB |
  | Search transfer: first two-word query; next query | ≤ 300 KB; ≤ 100 KB |
  | Search quality, 60 fixed queries | home page in the top 3 for ≥ 90 %, API names 100 % |
  | Lighthouse mobile, heaviest figure page | performance ≥ 90, accessibility 100, CLS ≤ 0.05, LCP ≤ 2.5 s |
  | axe, all pages, both themes | 0 serious or critical |
  | Crawl gates; base portability | 0 failures; `/`, `/strata-engine-docs/` and `/x/y/` all pass |
  | Mermaid | 0 clipped labels |
  | Print view of `make` | ≤ 5 min, ≤ 4 GB |
  | SO's "confirm items" | all confirmed |

  Add: "the spike's verdict is final; after the pilot starts, the framework is not revisited before 0.8.0".

**SI2 — major — The spike is half the book's size, and fake pictures would measure the wrong thing** (SO 16)
- *Change:*
  - The fake content follows the outline: 282 pages at their listed sizes, about 1.09 million words.
  - The reference is generated at its real sizes: 151 commands with schemas, 165 host functions, 1,592 terms.
  - One print view per part.
  - The pictures are the twelve sample screenshots at the pin, upscaled once to 1920×1080 and varied.
  - Measure on both machines, and report sizes as apparent sizes.

**SI3 — major — `site.md` contradicts `research/framework.md` in what a builder copies** (SO 2)
- *Problem:* the two files differ on 13 points: the environment variable names, the content tree and URLs, the link
  form, the picture originals, the derived sizes, the version scheme, the front-matter keys, the deploy folder and
  server, the tools folder, the glossary file, the engine pin, the sidebar and the site title.
- *Change:* add the section "Where this file overrides `research/framework.md`" with SO's table, and a banner on
  `framework.md` §5: "Background only; `plan/site.md` and `plan/pipelines.md` decide". Add `labs/` and `diagrams/` to the
  repository layout.

**SI4 — major — The image pipeline upscales, encodes twice and smooths the pixel crops** (SO 3; PL M5)
- *Problem:* for 1920 captures the 3840 width is an upscale. AVIF and WebP made from a q92 WebP are a second lossy
  generation. Resampling the nearest-neighbour crops smooths the stair-steps they exist to show. Python's standard
  library cannot encode WebP. The plan as written costs about 1.2-1.5 GB per version.
- *Both critics agree:* no upscaling; crops are never resampled and are served pixelated.
- **Contradiction** on the details:
  - SO:
    - a render's published 1920 file is served unchanged, with one 960 AVIF (quality ≥ 80) derived from it; 3840 only
      when the capture is 3840;
    - crops and editor pictures are lossless and shown at their exact pixel size; crops are published at capture size
      and enlarged in CSS (`image-rendering: pixelated`);
    - both sides of a slider use identical settings, quality ≥ 90 or lossless;
    - one format per picture: AVIF for renders, lossless WebP for crops and UI;
    - derived file names carry a content hash.
  - PL:
    - `figures.py` writes PNG only, and the sha256 covers the PNG; the published original is a PNG;
    - a recipe says `publish: "lossy" | "lossless"`; the default is lossless for parts image, indirect and light, and
      for every crop and slider;
    - AVIF and WebP widths are derived only for lossy figures.

**SI5 — major — "KaTeX errors fail the build" is false with the named packages** (SO 4)
- *Problem:* `rehype-katex` 7.0.1 drops `throwOnError` and only emits a warning.
- *Change:* add a `math` row: "a rehype step after `rehype-katex` fails the build when the file has a message with
  `source: 'rehype-katex'` or the tree contains `.katex-error`". Add to check 4: "the built HTML contains no
  `katex-error` and no Mermaid error SVG".

**SI6 — major — The crawl misses what breaks under the prefix at run time** (SO 6)
- *Problem:* a crawl over static files cannot see script requests (Pagefind, `versions.json`), `srcset`, CSS `url()`,
  canonical and `og:url`, `Location` headers, response headers, case, the server's 404 behaviour, or links built only by
  scripts.
- *Change:* replace site.md lines 35-38 with three gates:
  - (a) *Static:* lychee 0.24.2 offline over the staged folder, plus `tools/crawl.py` for what lychee cannot check
    (lowercase paths, unreferenced files, canonical equal to `DOCS_SITE + DOCS_BASE`, allowlisted hosts, engine links at
    the full SHA).
  - (b) *Runtime:* Playwright against the real nginx and Caddy configurations, in containers in CI: one page per kind, a
    deep 404, two searches, the theme and track toggles. Every request must stay under the prefix and answer 2xx.
  - (c) *Headers:* MIME types, `Cache-Control`, `Content-Encoding`, CSP.
  - The track "next" links of every track are written into the HTML (`data-track-next-g` …).

**SI7 — major — Base-path leaks that the plan neither configures nor checks** (SO 7)
- *Change* (SO's table of channels):
  - every `head` href is built from `DOCS_BASE`;
  - one `withBase()` helper is used by every plugin, with unit tests at bases `/` and `/a/b/`;
  - no `import.meta.env` inside `is:inline` scripts;
  - `versions.json` is reached through `DOCS_ROOT`;
  - ship no `robots.txt`;
  - drop the web manifest, or specify it fully;
  - a release build fails while `DOCS_SITE` is the default or contains a path;
  - no Astro redirects (a `redirects.json` generates server rules);
  - CI also builds with `DOCS_BASE=/` and `/x/y/`, and the latter contains no `strata-engine-docs` outside text.

**SI8 — major — The deployment section names features instead of giving configurations** (SO 8)
- *Change:* `deploy/` ships the blocks of SO's appendix C (nginx http and location snippets, the CSP snippet, Caddy, the
  Dockerfile, `container.conf`, the host proxy, the two-pass rsync). Their ten requirements are asserted by gate (b):
  1. `location ^~ /strata-engine-docs/`, so that the owner's regex locations cannot take the files;
  2. 301 to the slashed form, with `absolute_redirect off`;
  3. a 404 under the prefix that keeps status 404 (Caddy: `handle_errors 404` with a `path` matcher);
  4. caching by name, not by folder;
  5. precompressed text files;
  6. security headers, with a CSP generated from the built HTML (`'wasm-unsafe-eval'`, `worker-src 'self' blob:`);
  7. no nested `add_header`;
  8. nginx ≥ 1.30.6, with `root`, never `alias`;
  9. two rsync passes, the second excluding `/v[0-9]*/`;
  10. behind a proxy, `proxy_pass` without a URI part, and Caddy `handle`, never `handle_path`.

**SI9 — major — Versions cannot be "kept as static files"** (SO 9)
- *Change:*
  - Add `DOCS_ROOT` and `DOCS_ARCHIVED` now.
  - "Old versions are rebuilt from their tag with their own base", in an archived mode: banner, noindex, canonical to the
    current page, no sitemap.
  - The deploy excludes `/v[0-9]*/` and `versions.json`.
  - Slugs `v[0-9]*` are reserved.
  - The book's `localStorage` keys are namespaced by `DOCS_ROOT`.

**SI10 — major — The container builds the site, and container tests cannot run on the authoring machine** (SO 10)
- *Change:*
  - `deploy/Dockerfile` serves an already built folder and builds nothing; an optional `deploy/Dockerfile.build` states
    its RAM need.
  - The deployment tests run in CI.
  - The artifact has the top folder `strata-engine-docs/`.
  - Release builds are attached to a GitHub Release with a SHA-256 file (workflow artifacts expire).

**SI11 — major — Mermaid: no renderer named, a browser in every build, fonts that differ, no alt text** (SO 11)
- *Change* (site.md line 17):
  - "Mermaid 11.17.2 through `mermaid-isomorphic` 3.1.0, `htmlLabels: false`, Inter embedded as a subset `@font-face`".
  - Rendered by `npm run diagrams` and committed as `src/generated/diagrams/<hash>-{light,dark}.svg`.
  - Every fence has `accTitle` and `accDescr`, copied into `alt` and a caption.
  - Theme contrast is checked once against 4.5:1.
  - A check fails when a fence has no committed SVG.

**SI12 — major — Automatic glossary linking is the riskiest plugin, and a `title` tooltip is not accessible** (SO 12)
- *Change:*
  - "`:term[text]{id=…}` marks a term explicitly", and the linter reports the first unmarked use of a known term.
  - The definition opens in a `popover`.
  - `reference/glossary` is one `<dl>`: each `<dt>` has an `id` and `data-pagefind-title`, and the page sets
    `tableOfContents: false`.

**SI13 — major — Most "own" plugins exist as packages; the table hides which ones are risky** (SO 13)
- *Change:* rewrite the plugin table with a "package or ours" column:

  | Row | Package | Ours |
  | --- | --- | --- |
  | Link validation | `starlight-links-validator` 0.27.0 | — |
  | Link rewriting | `astro-rehype-relative-markdown-links` 0.19.2 | or 50 lines of ours |
  | Excerpts | — | an Expressive Code plugin |
  | Asides, answers | `starlight-markdown-blocks` 0.1.1 | — |
  | Front-matter schema | `docsSchema({ extend })` | — |
  | Zoom | `starlight-image-zoom` 0.16.2 | — |
  | Compare slider | `img-comparison-slider` 8.0.7 (optional) | — |

- Two rules for our own plugins:
  - Starlight does not restore unknown container directives, so the checker fails on an unknown `:::name` and allows
    `note`, `tip`, `caution` and `danger`.
  - Component scripts are loaded through a component override.
- Figures, tabs, the glossary and track navigation are what the spike exercises first.

**SI14 — major — The generated reference lands at the wrong URLs** (SO 14; PL M12)
- *Problem:* Starlight skips files whose name starts with `_`, but not folders, so `reference/_generated/*.md` becomes
  duplicate pages. The commands page alone is about 1-3 MB of HTML.
- *Change:*
  - Generate into `src/generated/reference/*.md`, outside the collection, and include it with `::include`; or generate
    the whole page with `editUrl: false`.
  - Each file starts with a stamp, and CI checks that the stamp's pin equals `engine.pin`.
  - Render parameters as tables, with each schema in a collapsed block.
  - Split `reference/commands` per command group when it exceeds the page budget.
  - HTML-escape all engine text.
- **Naming conflict:** PL M12 also writes `reference/_generated/*.md` (SO's point applies to it).

**SI15 — major — Search: the promised result display needs an override, and nothing measures its quality** (SO 15)
- *Change:*
  - Pages carry `data-pagefind-meta` `title:<title> · <part> · <kind>` and `data-pagefind-filter` for part, kind and
    track.
  - Weights: code 0.5, generated reference 0.3.
  - `data-pagefind-ignore` on line-number gutters, the top strip and `.katex-html`.
  - A search test of 60 fixed queries: the term's home page is in the top three for 90 % of them, and for 100 % of API
    names.

**SI16 — major — CI is one sentence** (SO 17)
- *Change:* add a section "CI":
  - jobs: lint, excerpts, build at three bases, serve-test, release, weekly external links;
  - the engine fetch: `git fetch --depth 1 --filter=blob:none origin <full-sha>`, a sparse checkout of `Strata*`,
    `StrataTests`, `Tools`, `CMake` and `Docs` cached by SHA, read through `git cat-file --batch`;
  - caches: npm, `node_modules/.astro`, derived pictures, Playwright;
  - `concurrency` with `cancel-in-progress` (one commit per page means 300+ runs);
  - sparse checkouts for the lint jobs; `fetch-depth: 0` if `lastUpdated` is used;
  - sketches use only the standard library and the pinned glm.

**SI17 — major — The site checks for the new teaching rules** (CU F1, F22; BG 2, 11, 18, 20; SO 6)
- *Change:*
  - The strips plugin checks, for every track, that each prerequisite comes earlier on that track (curricula 3.0), and
    accepts "any of" prerequisites.
  - Track navigation for G, E and B, with the next links of all tracks in the HTML.
  - The style linter measures sentence and paragraph length, terms per section and words outside the list, and bans the
    words of ST4.
  - The learn-id check of ST10.

*Minor:*
- **SI18** (SO 18): print views prefix every id with the chapter id, set `pagefind: false`, are kept out of the sitemap,
  open all `details`, load images eagerly and are noindex. The spike measures the print view of `make`.
- **SI19** (SO 19): `deploy/README.md` "Reading offline": `python -m http.server` in the unpacked folder.
- **SI20** (SO 20): axe on every page in both themes, keyboard tests for tabs, the slider, answers, the popover and track
  navigation, Lighthouse accessibility 100 on one page per kind, accessible names for the badges.
- **SI21** (SO 21): a retaken picture is committed only when a perceptual difference exceeds a threshold; check 9 includes
  the repository's pack size (≤ 1 GB before the 0.9 book); CI never fetches LFS objects.
- **SI22** (SO 22): the authoring drive is exFAT (case-insensitive, `node_modules` 6.2 GB on disk). Budgets use apparent
  sizes, only the integrator runs `npm ci`, and case checks run on Linux.
- **SI23** (SO 23): list what plain Markdown loses from MDX and its replacements: `:::steps`, `:::files`, badges from front
  matter, and the component overrides the book depends on (`PageTitle`, `Pagination`, `Footer`, `MarkdownContent`),
  re-checked at every Starlight upgrade.
- **SI24** (SO 24): list the Astro settings the book depends on: `base`, `site`, `trailingSlash: 'always'`,
  `build.format: 'directory'`, `compressHTML`, `markdown.processor: unified()`. The spike checks that a space between
  two inline code spans survives.
- **SI25** (SO, versions table): also list `@astrojs/markdown-remark` (a peer of Starlight; 7.3.6), `sharp` 0.35.5,
  Mermaid 11.17.2, nginx ≥ 1.30.6, Caddy 2.11.9 and lychee 0.24.2; note the risk that Starlight moves to Pagefind's
  Component UI.

### 2.5 `pipelines.md`

**PI1 — blocker — Phase A has no editor at the pin, and "the working tree does not matter" is false** (PL B1)
- *Evidence:*
  - The process forbids every way of getting a binary, and no package of `822a7a46` exists.
  - `--headless` keeps the GPU; only `--no-gpu` runs without a device.
  - `build/windows` follows `main`.
  - Script builds compile against the live tree's `StrataScriptCore`.
  - LookDev copies the checkout's Samples.
  - `--version` prints no commit.
- *Change*, pipelines.md "The pin": two engine inputs.
  - (a) `--engine <clone>`: a separate clone, not a worktree of `G:/GameEngineAI`, read with `git cat-file --batch` at
    the full 40-hex pin.
  - (b) `--build <folder>`: a build of exactly that commit. In phase A, one Release build of the pin, made once by the
    orchestrator in that clone, under `Tools/PerfLock.py`. In phase B, the official v0.8.x Windows package, checked
    against its `.sha256`.
  - Every tool calls `editor.status {sections: ["engine"]}` and stops when `engineCommit` is not a prefix of the pin.
  - For figures and labs, the clone is checked out at the pin and clean.
- process.md lines 97-99 become: "Phase A editors run with `--no-gpu`, one at a time, each inside
  `python <engine>/Tools/PerfLock.py --label docs-<tool> --limit 90 -- …`".
- PL's block "Proposed tool commands" replaces the tool interfaces of pipelines.md.

**PI2 — major — The recipe format names things that do not exist, and lacks what most figures need** (PL M1; RA m7, M14)
- *Problem:* `entity.setProperty`, `"AntiAliasing = None"` and `"shot": "Showcase/Dusk"` do not exist. The recipe lacks
  the scene, a scene camera, overlays, play mode, world cells, stations, Custom quality rows, material previews, the
  debug view, recorded numbers, project kinds and normalized crops.
- *Change:* replace pipelines.md lines 53-72 with PL M1's recipe and its field rules:
  - `project` is `{sample}`, `{template}`, `{lookdev}` or `{lab, template}`;
  - `camera` is explicit or `"scene"`; `"editor"` is refused;
  - `quality` is a preset or `{custom: {rows}}`;
  - also allowed: `world`, `station`, `postProcess`, `materials`, `debugView`, `play`, and `engine` for "before"
    pictures;
  - a variant may override any field except `camera`, `size` and `crops`;
  - `setup` steps are command-script steps plus `entityName`, resolved through `entity.find` and `bind`;
  - crops are normalized `[x0, y0, x1, y1]`;
  - `record` holds result pointers;
  - `taken` moves out of the writer's file.
- RA m7: captions write numbers as `{stats.x}`, filled from the recorded values; a check fails on a caption number that
  has no recorded source and no reference-machine note.
- RA M14: live recipes carry `atFixedStep` and `frames`.

**PI3 — major — The completeness test fails every picture without TAA, and skips fields the capture reports** (PL M2)
- *Change:* define `"expect": "complete"` as PL's pointer set: `pendingAssets`, `texturesBelowWanted`, `stalePoses`,
  `pendingTextGlyphs`, `ui/pendingGlyphs`, `localShadowViewsPending`, `reflectionProbesPending`,
  `renderStats/deferredInstanceBytes` (all equal 0); `preExposureSettled` and `globalIlluminationSettled` equal true;
  `previewLighting` equals false.
- Conditional additions:
  - `temporalFrames ≥ 8` only when the variant uses TAA;
  - `debugView/shadows/complete` with the shadows view;
  - the tool fails when `notice` is present;
  - a recipe may relax `previewLighting`.
- An engine addition (PI14) gives the result a `complete` flag and an `incomplete` list.

**PI4 — major — The take algorithm leaks state between variants and figures** (PL M3)
- *Change:* per figure and variant, in one editor per project copy, in this order:
  1. `scene.open {force}`, then `scene.loadStatus {wait}`, then `world.loadCells` for worlds;
  2. reset `Renderer.Quality` (or apply the custom value);
  3. the station steps (generated, never copied), the shot's setup, the figure's and the variant's setup;
  4. AA and `postProcess` on the one PostProcess entity;
  5. `play`;
  6. two captures with explicit `overlays`, `quality` and `debugView`;
  7. `play.stop`.
- A figure that bakes probes gets a fresh copy of its own.

**PI5 — major — "Capture twice and require identical files" applies only to stills** (PL M4; RA M14)
- *Change:*
  - The identity rule applies to `kind: scene` only.
  - *Live:* PL requires equal `fixedSteps` across runs; RA takes three, requires the same `fixedSteps` and camera in
    their stats, and has the photographer judge them by eye (the two are compatible). Live figures first set the
    project's `Renderer.Quality` on the copy.
  - *Runtime:* pass `--quality` and `--save-directory <empty dir>`, and require exit code 0.
  - On a repeat mismatch, retake once in a fresh editor. If it still differs, mark the figure `nondeterministic`, do not
    publish it, and report it to the engine with both images.

**PI6 — major — The fence format collides with Expressive Code, and has no rules for real engine files** (PL M6; SO 5)
- *Problem:*
  - In Expressive Code a quoted `mark` value marks text, and its line markers count the block's own lines.
  - `Scene::OnUpdate` does not exist, and `OnUpdateRuntime` is 156 lines long.
  - There are overloads, and lambdas inside 400-line functions.
  - The code is indented by tabs, with preprocessor lines at column 0, and lines reach 245 columns.
  - A short SHA stops resolving once another object shares its prefix.
- *Change:*
  - Book-owned attributes, which the plugin turns into Expressive Code's `startLineNumber` and block-relative marks.
  - `check` fails on a quoted `mark` that starts with `L`.
  - The pin is the full SHA.
  - The header is written by an Expressive Code plugin (SO).
  - While a page is written, anchors replace lines: `symbol=… from=… to=…`, `overload=2`, `command="viewport.capture"`.
  - `fill` refuses ranges over 60 lines.
  - Normalization: strip the common leading tabs, ignoring column-0 preprocessor lines; tabs show as 4 columns; `wrap`
    with `preserveIndent` (PL).
- **Naming difference:** SO writes `lines="L2239-L2262" marks="L2251,L2255"`; PL writes
  `src="engine:<path>" lines="2220-2243" highlight="2224,2238-2240"`.

**PI7 — major — `git show <pin>:path` cannot read vendor code or the book's own files** (PL M7)
- *Problem:* all 19 libraries in `Strata/vendor` are gitlinks.
- *Change:*
  - Source namespaces: `engine:<path>`; `vendor:<lib>/<path>`, read from the submodule commit, linked to the library's
    GitHub, with its license line in `appendix/credits`; `book:<path>`.
  - Build outputs are shown only through their templates and generators.
  - `relocate` searches the whole tree at the new pin (`git grep -F`) before it falls back to the symbol.

**PI8 — major — A tutorial cannot be a plain command script, and has no starting points, assets or checkpoints**
(PL M8; GM F12; BG 16)
- *Problem:*
  - The script loader rejects every key except `command`, `parameters`, `expect`, `bind` and `until`.
  - `project.create` and `asset.import` need absolute paths, and no command writes a script's source.
  - The only templates are `empty` and `basic3d`.
  - `expect` has only `equals`, `min` and `max`, and `log.read` has no text filter.
- *Change:*
  - A book format `tutorials/<part>/<chapter>.tutorial.json`:
    - `startsFrom` is a template, a sample or an earlier tutorial (which is replayed first);
    - placeholders such as `@PROJECT@`;
    - `stages`, each with `files`, `commands` and `checks` (`contains`, `approx`, `length`);
    - `tutorials.py` compiles each stage into a command script, and readers download the compiled script;
    - game time is counted in `play.step` / `until {steps}`, never frames.
  - Tutorial assets come from the release's `Samples/*/Assets` (CC0, already credited) or from a small
    `tutorials/assets/` pack with a `CREDITS.md`; every page names the file it imports (GM).
  - Each section's end state is published as a downloadable zip (GM; BG).

**PI9 — major — Eight tutorials that change the engine, and every code exercise, have no runner** (RA M13; BG 15; PL M9)
- *Change:* `tutorials.py patch`:
  1. apply `tutorials/<part>/<chapter>.patch` to the pin clone;
  2. build only the touched targets, in one persistent docs build directory;
  3. run the tests the page names, plus `Architecture.Layering` and the feature test;
  4. revert, and write the stamp.
- The page quotes hunks with `src="book:…patch#hunk-2"`. The runner runs in phase B, under PerfLock (PL), with the GPU
  (RA).
- Exercise solutions are stamped the same way: sketches with expected output, editor exercises as command scripts,
  engine exercises as patches (BG). The novice reviewer answers conceptual questions only (PL).

**PI10 — major — The UI steps cannot be verified as planned** (GM F13; BG 16; PL M10)
- *Change:*
  - Strike "the reviewer walks them by hand".
  - The names lint (PI13) checks every **Menu ▸ Item** path and button label against the string literals of
    `StrataEditor/src/{UI,Panels}` and `EditorLayer.cpp` at the pin.
  - In phase B, every step gets a whole-editor picture judged against the step's text (PL). The UI path of each G
    tutorial is walked once in a windowed editor from a release package, by the owner or by an agent that controls the
    screen (GM; BG); steps that cannot be walked are marked command-only.
  - Figure manifests list the pictures only a person can take (GM).

**PI11 — major — The reference tables assume listings that the engine does not have** (PL M11; RA M11; ED F18, F22; CF F21)
- *Change:* replace the table on lines 123-131 with PL's route table:

  | Table | Route |
  | --- | --- |
  | commands | `editor.commands` plus parsing; there is no result schema |
  | components | `component.list`, defaults from a dump script, inactive reasons parsed |
  | settings | `project.settings` on an empty project, `preferences.get`, using `default` |
  | asset types and importer versions | parsed, or a new `asset.types` command |
  | quality rows | parse `RendererQuality.cpp`, plus the section schema |
  | debug views | the `viewport.capture` enum |
  | GPU stages | parsed |
  | script API | `StrataScriptHostAPI` in `ScriptABI.h`, `StrataScriptClassDesc`, the SDK through `SDKReader`'s rules, the macros, "added in" through `git log -S` |

- Add:
  - the `renderStats` keys (parsed from `EditorStateCommands.cpp`) and the fields of `SceneRendererSpecification` and
    `SceneRendererStats` (parsed from `SceneRenderer.h`) (RA);
  - the runtime perf-log columns (`FramePerfLog`, `GameRenderer::MakePerfLogColumns`) and the editor and runtime option
    tables from `c_Arguments` (ED);
  - `Budgets.json`, the scene limits, the asset budgets and statistics (CF).
- Line 125: "JSON Schema of parameters and result" → "parameter schema; the result as the description states, with an
  example result recorded by a tutorial run".

**PI12 — major — The reference is generated too late, and its CI check cannot run** (PL M12; SO 14)
- *Change:*
  - `reference.py dump --build <pin build> --no-gpu` writes `reference/_dumps/<pin>/*.json`, each with `engineCommit`.
    It runs in phase A step 2 and at every pin move.
  - `reference.py render` is pure Python.
  - CI checks that rendering reproduces the committed Markdown and that the dumps' commit equals `engine.pin`.
  - The rendered output goes outside the docs collection (SI14).

**PI13 — major — Reviewers need a names lint** (PL M13)
- *Problem:* the plan's own examples name four things that do not exist.
- *Change:* `tools/names.py` checks:
  - every backticked command, parameter, component, property, enum value, settings id, debug view, quality row, SDK
    function and macro, against the dumps and the SDK parse;
  - every path, against `git ls-tree -r <pin>`;
  - every UI path, against the UI literals.
- It is the writer's exit check and a site check. The technical reviewer gets its report together with the tutorial logs
  and the capture sidecars.

**PI14 — major — The engine additions are not "a small engine change", miss items, and would split the pin** (PL M15;
RA m9)
- *Change:* replace lines 97-101 with tiers:
  - *Tier 1:* `complete` / `incomplete` and `screenSpaceReflectionsPending` in the capture result; flags in
    `editor.commands`; `asset.types`; `--window-size`.
  - *Tier 2:* `editor.screenshot` through `EditorHost`; `viewport.capture {renderer: {…}}` (energy compensation
    included); the debug views `specular`, `diffuse`, `clusters`, `culled` and `wireframe`.
  - *Tier 3:* captures of intermediate targets (depth, normals, velocity, shadow mask, cascades, the local shadow atlas,
    bloom levels, the glyph atlas) and motion stills.
- The additions land on a `release/0.8` branch as **v0.8.1**, containing only them, and `engine.pin` moves to v0.8.1 for
  text and pictures alike. Engine agents make them, under the engine's review.
- RA m9: `gpu/frame-tour`'s section on frame captures is checked on the GPU in phase B.

**PI15 — major — Prose claims and numbers that wave 8 can move are not caught by the pin tool** (CF F12; RA M7; RB F15;
ED F18)
- *Change:*
  - The pin tool also lists the pages with W8L or W8r marks and each page's list of movable claims (PR7).
  - `reference/renderer` is generated only (RA).
  - Counts are stated through generated values, or through the tests that pin them (`CommandJournalTests.cpp` 101-165,
    `EditorMcpToolsetsTests.cpp` 113) (ED).
  - A check flags prose numbers on pages whose reference tables changed (ED).

**PI16 — major — The glossary cannot flag the beginner's words; terms with two meanings** (BG 24; CF F20)
- *Change:*
  - Before writing starts, seed `glossary.json` with a beginner base vocabulary of about 300 terms (variable, function,
    terminal, git, integer, floating point, array, integral, probability, debugger, folder, path, byte …), each homed in
    a start or basics page; process step 3 merges it first (BG).
  - A term with two meanings gets two qualified entries ("pack block", "BC block") (CF).

*Minor:*
- **PI17** (CF F23; ED note; GM F13c): add the figure kinds "text capture" (a command run at the pin, its output in a
  fence, re-run at the pin move) and "tool screenshot" (a manual recipe judged by eye: Tracy, ctest, Visual Studio, GitHub
  Actions, LookDev's `index.html`, Windows Properties, OS file browsers). Say which figures may be text only.
- **PI18** (PL m1; SO 5): `engine.pin` holds the full 40-hex SHA, with the tag as a comment.
- **PI19** (PL m2): whole-editor pictures vary with UI scale, window size, the launcher footer, timestamps and thumbnails,
  not with fonts (the fonts are committed). Use `--windowed --ui-scale 1`, a copied `--layout`, a controlled
  `STRATA_RECENT_PROJECTS` and a final `editor.wait`.
- **PI20** (PL m3): shipped-game pictures add `--save-directory <empty dir>`, `--quality` and `--windowed`;
  `--screenshot` needs a window and a GPU.
- **PI21** (PL m4): make sample copies with `project.openSample {sample, directory}`.
- **PI22** (PL m5): take "before" pictures from the LookDev baselines on the reference machine, with the owner's leave,
  and add `engine` to the recipe.
- **PI23** (PL m6): a stamp holds `engineCommit` and the build or package id, the OS and configuration, the sha256 of the
  compiled script and of every copied file, and the checks' results. Draft pages are exempt until phase B.
- **PI24** (PL m7): at a pin move, retake every picture and diff with `LookDev.py compare`.
- **PI25** (PL m8): read the engine through one `git cat-file --batch` process.
- **PI26** (PL m9; BG minor): Slang sketches use the slangc pinned by `CMake/StrataSlang.cmake`; C++ sketches use
  `-std=c++20` and glm from the pin's submodule; a sketch shown with output must run, and its output is compared.
- **PI27** (PL m10): labs assume an open project; their textures are generated, or committed CC0 files.
- **PI28** (PL m11): shots with `Camera: "editor"` or entity IDs cannot be reproduced on copies; re-judge reused shots at
  each pin move.
- **PI29** (PL m12): the capture's own camera is an editor view, so game pictures use `camera: "scene"` or play mode.
- **PI30** (PL m13): players' graphics options cannot be set by any command, so figures of the options menu need a
  script in play mode or a new command.
- **PI31** (PL m16): every tool runs under PerfLock, with a private `STRATA_SESSION_DIR`, a controlled
  `STRATA_RECENT_PROJECTS`, and `--no-gpu` unless it captures.
- **PI32** (PL m17): optionally, after 0.8.0, CI re-runs the editor tutorials on the Linux package with `--no-gpu`.
- **PI33** (RB F20): a Monte Carlo path tracer sketch of the Cornell box in `indirect/problem`, and a "reference" figure
  kind that `indirect/ao`, `indirect/probes` and `indirect/gi-cascades` compare against.
- **PI34** (RA notes): `reference/figures` names the GPU of the figure machine (the GPU-driven path never ran on the CI
  GPUs). A figure of the cascade cache is taken on the GPU path; thumbnails force the CPU path.

### 2.6 `process.md`

**PR1 — major — The waves contradict "prerequisites are written before the pages that need them"** (CF F1; SM F2;
CU F20; ED F1; RA M6, M10; BG 12; RB F2)
- *Problem:*
  - Wave 3 writes assets before gpu.
  - Wave 4 writes ui (which needs `gpu/text`), `input/simulated` and `worlds/editing` (which need the editor), and
    `animation/culling` (which needs draw).
  - Wave 2's make pages link to homes of waves 3-5.
  - Phase B writes `light/lights` after the pages that need it.
- **Contradiction** on the fix:
  - SM: swap waves 4 and 5, and move `input/simulated` and `ui/testing` into wave 6.
  - CU: the waves are the layers of a topological sort of the Needs column. Its rough result:

    | Wave | Pages |
    | --- | --- |
    | 1 | start, basics, core, world |
    | 2 | make up to Coin Run, gpu |
    | 3 | assets, the editor's core |
    | 4 | draw, light (non-W8), image, physics, audio, input, scripting |
    | 5 | indirect (non-W8), animation (if the graph is cut), ui, worlds, the rest of make |
    | 6 | editor-ui, automation, engineering, capstone |

  - Specific moves:
    - CF: `assets/textures`, `assets/uploads` and `assets/mip-streaming` in wave 5;
    - RA: `gpu/resources-lifetimes` and `gpu/upload-queue` in wave 3 if the upload split is kept, and
      `image/tutorial-post-effect` in wave 6;
    - BG: gpu up to `gpu/upload-queue` in wave 3, and ui in wave 5 (or `gpu/text` in wave 4);
    - ED: `worlds/editing` in wave 6, `worlds/runtime` and `worlds/export` in wave 5 or 6;
    - RB: unmark `light/lights`.

**PR2 — major — The pilot misses the pages most likely to fail** (BG 23; GM F15; PL M17; CF F4; CU F1)
- **Contradiction** (the proposals differ; they do not exclude each other except where they replace the same page):
  - BG: replace `core/time` with `make/cpp-for-scripts` (or `basics/programming-1`), add `start/install`, and review
    both with the B persona and the provenance check.
  - GM: add `make/project-coin-run` (or swap `make/first-script` for it), and stamp its run before the tools are frozen.
  - PL: either allow one PerfLock'd GPU session for the pilot's recipes, or replace `image/tone-mapping` with a page whose
    figures are diagrams and move the recipe pilot to the start of phase B. In phase A step 2, add an offline
    `figures.py check`.
  - CF and CU: retitle `core/time` before the pilot. In CU's split, `basics/math-vectors` keeps the pilot id.

**PR3 — major — The novice review has the wrong persona, rests on a feeling, is closed by non-novices, and sees no
pictures** (BG 21, 22; PL M9, M18; CU F1)
- *Change:*
  - The review becomes a **provenance check**. The reviewer gets the persona's knowledge list and the `learn` lines,
    summaries and glossary terms of the page's prerequisite closure. For each section it lists every idea, term, symbol,
    C++ feature and UI action used, and the sentence that taught it.
  - It also runs the reading metrics of ST2.
  - "No code" becomes "no access to the engine's source".
  - The reading list comes from the Needs column, not from the writer (CU).
  - A fresh novice reviewer confirms every fix of a novice finding.
  - The fixer may not reject "used but not taught"; it may only move the teaching to a prerequisite and say where.
  - After the pictures, a second novice pass covers tutorials and level-1 pages (BG); PL M18 asks for a short re-read of
    the captions and the text around each figure on every page, and `final` requires it.
  - Code exercises are judged by the runner (PI9), not by the novice (PL).
  - Real beginners: owner question 7.

**PR4 — major — Nothing tests a track as a whole, though the definition of done claims it** (GM F14)
- *Change:* phase B step 10 adds a **track G walk**. A fresh agent with only the published book, a release package and a
  user profile without Strata data follows track G from `start/install` to the exported Coin Run and then to the
  platformer, using the UI where it can, and logs every place where it had to guess or leave the book. Do the same for
  track E, up to `start/first-engine-change` and one tutorial.

**PR5 — major — Excerpts are filled after the review, so reviewers judge code they cannot see** (PL M14)
- *Change:*
  - The write stage ends with `excerpts.py fill && excerpts.py check`, `figures.py check`, `tutorials.py check` and
    `names.py`.
  - A page that still has anchor-form fences cannot enter review.
  - Any change of a fence's `src` or `lines` after review triggers a confirm.

**PR6 — major — Several agents would write the same files** (PL M16, m15; SO 22)
- *Change:* PL's ownership table:

  | File | Only written by |
  | --- | --- |
  | pages | writer, fixer, part editor; the integrator for mechanical repairs only |
  | figure manifests | writer, fixer |
  | published pictures and sidecars | `figures.py` |
  | tutorials | writer, fixer; stamps only `tutorials.py` |
  | labs | the page the brief names as their owner |
  | sketches | that page's writer, with a page-prefixed name |
  | glossary | one admitter at a time |
  | sidebar, `engine.pin` | the integrator; the pin moves only during a freeze |
  | dumps and generated reference | `reference.py` |
  | notes and reviews | their own author |

- Each page pipeline works on a branch of its own, and the integrator merges.
- The integrator's kit: the pin clone, the pinned Node and Python tools, the dumps, and write access to its rows only. A
  content failure goes back to the fixer.
- Only the integrator runs `npm ci` (SO 22).

**PR7 — major — Phase B steps 6 and 7 need the wave 8 rules** (SM F1, F21; RA M7, M8; RB F15, F22; CF F11, F12; ED F18)
- *Change:*
  - Writers' notes list every claim of the page that wave 8 can move: numbers of shadowed lights, views per frame, noise,
    quality values, GI views (RB F15).
  - Step 6 re-reviews those lists and the W8L or W8r pages together with the pin tool's output, and re-reads
    `assets/references`, `reference/assets`, `animation/root-motion` and `world/interpolation` (CF; SM).
  - Step 6 checks the 0.8.0 release notes for `animation-graph`, `volumetric`, `showcase-engine`, `editor-ux` and area
    lights.
  - Step 6 applies SM's rule for a cut from landing 1.
  - Step 7 becomes "the W8 pages are written and the W8r pages revised" (RA).
  - `editor/placement` and `editor/scene-view` are written last in wave 6 and re-read at the pin move (ED).

**PR8 — major — The part briefs and the allocation must carry more** (RA M3, M15, notes; GM F6; CF further; SM F10, F22;
CU F17; ED notes)
- *Change:* each brief:
  - names the internals pages that carry the general section (ST1);
  - says which page gets which figures (OL13);
  - lists the steps of G pages that only a command can do (GM);
  - lists errata and docs drift so that pages do not repeat them (CF; SM):
    - the Developer Guide and the skill name 12 shards, `CoreShards.json` has 13;
    - the comment at `BuiltinModules.h` 21-27 names fewer modules than the table;
    - `SceneRegistration.h` 6-9 omits `Scene.Timing`;
    - the Developer Guide gives the wrong path of `GenerateAssets.py`;
    - gameui says 12 components, but 11 are registered;
    - an inventory says the glTF importer is version 9, but it is 11;
    - `Symbolizer.h` contradicts `PosixSymbolizer.cpp`;
    - the UI's Submit defaults are not settled;
    - the command count is given as 151, 153 and 154 (§5).
  - names the book-wide running examples (BK7);
  - carries the allocation notes:
    - `CameraComponent`: `GetProjection` → `gpu/coordinates`, the depth-of-field fields → the depth-of-field page, the
      primary-camera lookup → `world/scene-graph` (CF);
    - the `FrameCounterModule` exercise is required in `core/engine-modules` (CF);
    - `image/encoding` gets a forward sentence about FXAA and grain (RA);
    - the structure of StrataCLI goes to `automation/mcp` (ED).
- The allocator of part 18 reads `ScriptBuild*`, `ScriptToolchain*`, `ScriptProject*`, `ScriptSources*`,
  `ExternalEditor*` and `Panels/ProblemsPanel*`, which no inventory surveyed (SM F10).

*Minor:*
- **PR9** (PL M11, M18; CU F22): in the definition of done, "(generated, so by construction)" → "every component
  `component.list` returns, with the hidden and `NoSerialize` ones listed from the source"; `final` requires the re-read
  after pictures; every objective is tested.

### 2.7 `README.md`

These edits follow from findings above and are counted there:
- Decision 5's W8 list becomes "local lights, global illumination, and, if they land, the animation graph, volumetric
  fog and material layers" (RA M8; SM F1; CU F13, which adds `editor-ux`). Area lights follow OL8.
- Decision 5's re-pin target becomes v0.8.1, if the capture additions ship as v0.8.1 (PI14).
- Decision 3, "Reference pages are generated", becomes "generated, or parsed and checked" (PI11).
- Decision 4 gets the spike's pass/fail rule (SI1).

*Minor:*
- **RM1**: add the questions of §6 to "Open questions for the owner" (SO 7; BG 22; PL m5, M10, M15; GM F13).

---

## 3. A consolidated proposal for the outline

### 3.0 Columns and legend

- **New columns** (OL1): `| id | Title | Kind | Size | Tracks | Needs | From |`. The rows below keep the current five
  columns, plus a last column **Change (critics)** that is an annotation: drop it when pasting. Where a critic gave
  tracks, they are stated in the annotation.
- **Kinds:** add P, primer (BG 7).
- **The XL rule** (outline-1 line 8): see OL10.
- **W8 legend:**
  - "W8" — waits for 0.8.0.
  - "W8 (animation-graph)" — waits unless the stream is cut from 0.8.0 (SM). CU writes this as "W8?".
  - "W8r" — written in phase A, revised in phase B (RA).
  - "W8L" — wave 8 work that has landed; re-read at the pin move (CF). SM and ED add no such mark, only a "new in 0.8.0"
    label (ST11).
- **The figure rule of outline-3 lines 3-4:** OL13.

### 3.1 Corrected part prerequisite lines

This is the union of what the critics added to each part's line ("+" adds to the current line). These lines are replaced
by the per-page Needs once that column exists.

| Part | Line (union of proposals) | Per-page additions | Critics |
| --- | --- | --- | --- |
| core | `basics/computer`, `basics/cpp`, `basics/build` | `core/jobs` + `basics/threads`; `core/math` + `basics/math-vectors`, `basics/math-rotations`; `core/reading-code` + `core/map`, `basics/tools` | CF F22; CU |
| world | `basics/computer`, `basics/cpp` (or `basics/programming`), `basics/math-vectors` (or `math-matrices`), `basics/math-rotations`, `basics/threads`, `core/map`, `core/frame-loop`, `core/time`, `core/layers-registries`, `core/jobs`, `core/math` | `world/serialization`, `world/prefabs`, `world/sub-scenes` + `assets/handles-meta`, `assets/loading` (if they stay in world) | CF F2, F7; CU |
| assets | `basics/bytes`, `basics/color`, `basics/threads`, `core/jobs`, `core/layers-registries`, `world/ecs`, `world/reflection`, `gpu/how-a-gpu-frame-works` (or `basics/gpu`), `gpu/resources-lifetimes` | `assets/residency`, `assets/uploads` + `gpu/upload-queue`; `assets/mip-streaming` + `gpu/binding`, `draw/asset-requests`; `assets/references`, `assets/packs-export` + `world/serialization`; `assets/textures` + `basics/signals` | CF F1; CU; RB F7; RA M6; BG 12 |
| gpu | + `basics/build`, `basics/threads`, `basics/bytes`, `basics/numbers` (or the float page), `core/engine-modules`, `core/layers-registries`; CU: `basics/math-projection` | `gpu/first-triangle` + `start/first-engine-change` | RA M2, M9; CU; BG 12 |
| draw | part `gpu` up to `gpu/readback-timing`, `gpu/shaders`, `world/scene-graph`, `world/interpolation`, `core/jobs`, `core/math`, `assets/residency`; CU: `basics/math-geometry` | `draw/gpu-driven`, `draw/occlusion` + `gpu/compute`; `draw/skinned` + `animation/skinning`, `animation/culling` (if it stays); `draw/asset-requests` + `assets/mip-streaming` (RA; contradicts CF) | RA M1, M9; CF F7; CU |
| light | `gpu/frame-tour`, `gpu/binding`, `gpu/coordinates`, `basics/color`, `basics/math-vectors`, `basics/math-light`, `basics/signals`, `assets/textures`, part `draw` up to `draw/render-scene-gpu` | shadow pages + `draw/gpu-driven`; `light/many-lights` + `gpu/compute`; `light/shadow-basics` + `gpu/coordinates` | RB F1, F8; CU; RA M1 |
| image | `gpu/frame-tour`, `gpu/readback-timing`, `gpu/compute`, `light/units-exposure`, `light/measuring(-light)`, `basics/signals`, the float page, `draw/motion-vectors` (or `draw/render-scene-gpu` if motion vectors move into image) | `image/tutorial-post-effect` + `engineering/feature-test` and the GPU-test home; `image/exposure` + `gpu/compute` | RA M2, M10; CU |
| indirect | `light/brdf`, `light/energy`, `light/sky`, `image/pre-exposure`, `basics/math-light`, `editor/commands` (bakes) | `indirect/ssr` + `draw/motion-vectors`, `image/taa`; `indirect/gi-voxels` + `gpu/geometry-pool`, `draw/render-scene`; `indirect/ao` + `gpu/compute` | RB F8; CU; RA M1 |
| physics | + `world/ecs`, `world/scene-graph`, `world/systems`, `world/projects-settings`, `world/interpolation`, `core/jobs`; BG: `basics/math-change` | `physics/scale-streaming` + `world/sub-scenes`; physics broad phase + `draw/bounds-culling` (BG table) | SM F5, F7; CU; BG |
| animation | + `core/jobs`, `world/scene-graph`, `assets/residency`, `assets/models-gltf`, `draw/bounds-culling` | `animation/root-motion` + `physics/character-controllers`; `animation/culling` + `draw/bounds-culling` | SM F5; CU |
| audio | + `core/engine-modules`, `core/frame-loop`, `assets/importing`, `assets/loading`, `basics/math-vectors`, `basics/signals` | `audio/testing` + the testing page | SM F5; CU; RB F7 |
| input | + `core/frame-loop`, `core/time`, `world/projects-settings`, `basics/bytes`, `make/editor-tour` | `input/simulated` + `editor/commands` | SM F5; CU |
| scripting | + `core/platform`, `core/conventions`, `world/reflection`, `make/script-loop` | — | SM F5; CU |
| ui | + `input/actions`, `gpu/binding`, `gpu/coordinates`, `draw/mirrors-camera-relative`, `scripting/abi-sdk` | — | SM F5; CU |
| worlds | + `physics/scale-streaming` (or `physics/capacity`), `scripting/abi-sdk`, the float page, `editor/undo` | `worlds/runtime` + `core/first-frame`, `core/engine-modules`, `scripting/script-system`, `image/quality-settings`, `gpu/frame-tour`, `basics/computer`; `worlds/measuring` + `core/profiling` | ED F1, F21; CU |
| editor (pages 1-15) | `world/systems`, `world/reflection`, `world/serialization`, `world/prefabs`, `assets/handles-meta`, `core/time`, `core/jobs`, `basics/threads`; CU adds the testing page and `make/editor-tour` | `editor/prefab-instances` + `world/prefabs`; `editor/camera-viewport` + `gpu/coordinates`; `editor/placement` + `draw/bounds-culling` | ED F2; CU |
| editor (pages 16-32) | the line above, + `core/windows-events`, `gpu/vulkan-nvrhi`, `gpu/binding`, `gpu/readback-timing`, `basics/color`, `input/mouse-cursor`, `world/projects-settings`; CU: `editor/program`, `ui/what-game-ui-does`, `gpu/shaders` | `editor/ui-testing` + `engineering/testing`; `editor/scene-view` + `gpu/readback-timing`, `gpu/frame-tour`; `editor/imgui-backends` + `gpu/vulkan-nvrhi`; `editor/settings-windows` + `world/projects-settings` | ED F2, F17; RA notes; CU |
| automation | track E; `editor/commands`, `editor/deferred-commands`, `editor/journal`, `basics/bytes`, `basics/threads`, `basics/computer`, `core/platform` | — | ED F11; CU |
| engineering | `basics/build`, plus the testing page (CU) | `engineering/cmake` + `core/layers-registries`; `engineering/generated-code` + `gpu/shaders`; `engineering/test-kinds` + `gpu/vulkan-nvrhi`, `editor/command-scripts`; `engineering/feature-test` + `world/reflection`, `scripting/abi-sdk`; `engineering/perf-lab` + `core/profiling`; `engineering/look-dev` + `gpu/frame-tour` | CF F3; CU |
| make | the rule of BK2 | `make/first-script` needs any of `make/cpp-for-scripts`, `basics/cpp` | CU; BG 11 |

### 3.2 Rows, part by part

Only changed or new rows are listed. "Option X" marks rows that contradict each other.

**Part 0 — start**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `start/welcome` | What Strata is and what this book teaches | C | S | new; three doors; the G door says game logic is C++ (no visual scripting) and that an agent can help; says which track a beginner continues on | From (GM F7, F16; BG) |
| `start/how-to-read` | How to read this book | H | S | new; + "How to read a command" (JSON); + "How to read code you do not understand yet" | From (BG 25, 17) |
| `start/install` | Installing Strata and the C++ build tools | H | M | gamedev 1.1 (release archives, requirements, first start, script toolchain discovery, logs); PackageReadme "Requirements", "First start"; Manual/Scripting "Where builds happen" | retitle, S→M; source build out (GM F1; BG 9; CU F16) |
| `start/terminal` | Using a terminal | H | S | new; PackageReadme "First start" (PowerShell, Terminal: folders, running a program with arguments, quoting paths, `\| Write-Output`) | new after install (GM F6) |
| `start/first-game` | Option GM: Your first game | T | M | gamedev "Launcher and first project"; the Tetris copy played within 5 minutes, Basic 3D with falling bodies, the generated Spinner attached; the 30 minutes start after the install | GM F1 |
| `start/first-game` | Option BG: Your first game | T | M | gamedev hands-on G2-G3 on Basic 3D; no code, no samples | BG 9; seeds Coin Run (CU) |
| `start/what-an-engine-is` | What a game engine is: one frame, start to finish | C | L | foundation "What an engine is…" (first half); gamedev "What it takes to make a game"; home of the frame map and the survey of engines | retitle, M→L (CU F23); position contradicts (BG: second; CU, GM: after first-game) |
| `start/coming-from` | Coming from Unity, Unreal or Godot | R | M | curricula 5.2; gamedev concepts 4, 7 (GameObject vs entity, prefab variants vs Strata's overrides, Blueprints vs C++ scripts) | new (GM F22; CU F12) |
| `start/first-engine-change` | Your first engine change in 30 minutes | T | M | new; build, change one thing, write a test, run it; + "Building Strata (short form)" | track E only (GM F18; CU F10; BG 9) |
| `engineering/first-change` | Option BG: Your first engine change | T | M | the row above, moved; Needs `basics/tools`, `basics/build`, `basics/cpp-classes` | BG 9 (instead of keeping it in start) |
| `start/map` | The map of the book: tracks and prerequisites | R | S | new, generated from front matter (curricula 5.1.4) | new (CU F18) |

Orders: CU — welcome, how-to-read, install, first-game, what-an-engine-is, coming-from, first-engine-change, map. GM —
welcome, how-to-read, install, terminal, first-game, what-an-engine-is, first-engine-change. BG — welcome,
what-an-engine-is, how-to-read, install, first-game.

**Part 1 — make**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `make/editor-tour` | A tour of the editor | T | L | gamedev; editor-ui "A tour of the editor"; use home of editor commands (CU) and of autosave and recovery (GM) | M→L (ED F16; GM F10; CU F16); tracks G E B |
| `make/project-files` | Your project's files: what to keep, back up and never touch | H | S | gamedev 1.2 (project file, creation, migration), concept 3, diagram 2, pitfall 1; release notes "Upgrading" | new after editor-tour (GM F19) |
| `make/assets` | Bringing in assets | T | M | gamedev; assets (use side); licenses, CC0 sources (Kenney, Poly Haven, Quaternius, ambientCG), a `CREDITS.md` | H→T (CU F15); From (GM F20); perhaps L (CF) |
| `make/undo-save-recover` | Undo, saving and getting work back | H | S | editor-core "Autosave and crash recovery", "Project files as history" (use side); editor-ui §1.11 | new after make/prefabs (ED F9); contradicts GM F4 (use home in editor-tour) |
| `make/materials` | Materials | T | L | gamedev; render-direct "Strata's material model" (use side); + albedo audit with the debug view | From (RB F11); W8 if showcase-engine lands (RB F22) |
| `make/lighting` | Lighting a scene: sun, sky and exposure | T | L | gamedev 1.8 (units, sky sources, presets, fog, sun shadows, exposure, preview lighting, debug views luminance/albedo); render-direct "Lighting a scene in the editor" (outdoor half) | split, not W8 (GM F9; CU F13) |
| `make/lamps` | Option GM: Lamps, torches and area lights | T | M | render-direct (indoor half), gamedev 1.8 Source Radius, local shadows · W8 | new by split (GM F9) |
| `make/local-lights` | Option CU: Lamps, spots and area lights | T | M | the same · W8 | new by split (CU F13) |
| `make/reflections` | Sky light, ambient occlusion and reflections in your game | T | L (RB) / M (CU) | render-indirect ch. 6 and 8 (sky sources, AO, probes and bakes, times of day, a wet floor with SSR) | split, not W8 (RB F14; CU F13); size contradicts |
| `make/global-illumination` | Trying global illumination | T | S | render-indirect ch. 11 · W8 | split (RB F14); CU names it `make/gi` |
| `make/look` | Option GM: The camera's image | T | L | render-image ch. 12; Manual/Camera | split (GM F10) |
| `make/quality` | Option GM: Anti-aliasing, graphics quality and players' options | H | M | Manual/AntiAliasing, Manual/Graphics (presets, costs, quality chip, `--quality`, players' options, why no render scale); home of `Graphics::` | new by split (GM F10, F23) |
| `make/look` | Option CU: The camera's image and graphics quality | T | L | unchanged | moved after the UI pages (CU F14); W8r (RA M7) or its Graphics Quality section W8 (RB F15) |
| `make/cpp-for-scripts` | Option BG: C++ in a Strata script | P | M | gamedev concept 11; Needs `basics/programming-1..3` | bridge page (BG 1) |
| `make/cpp-for-scripts` | Option CU: Just enough C++ for game scripts | C | L | unchanged; Needs `basics/programming` for readers who never programmed | CU F9, F16 |
| `make/cpp-1` | Option GM: Programming from zero, inside a script | T | L | gamedev concept 11; values, types, if, loops, functions, arrays and `std::vector`, reading compile errors | replaces cpp-for-scripts, after first-script (GM F7) |
| `make/cpp-2` | Option GM: Classes, fields and callbacks: the C++ of a script | T | M | gamedev concept 11; Script.h L30-110; headers and sources, override, enums, namespaces, module state | GM F7 |
| `make/gameplay-math` | Option GM: The math of moving things: vectors, directions, angles and smoothing | T | M | new; skill make-a-game L158-256, FollowCamera.cpp L43-101, Playground.cpp L183-207 | GM F7 |
| `make/first-script` | Your first script | T | M | gamedev; scripting "Your first script"; + external editor, `strata` preset and IntelliSense, Problems panel, crash toast | From (GM F8); tracks G E B; Needs any of `make/cpp-for-scripts`, `basics/cpp` (CU) |
| `make/script-loop` | The game loop from a script's side | C | M | unchanged; home of the script lifecycle; use home of fixed step, frame vs fixed updates, time scale, FixedRate | role (SM F3; GM F4; CU) |
| `make/scripting-scene` | Option GM: Changing the scene from a script: entities, components, spawning and assets | H | L | scripting "Gameplay API 1" | was `make/gameplay-1`, after script-loop (GM F3) |
| `make/scripting-the-world` | Option CU: Finding, moving and spawning things from scripts | T | L | scripting ch. 4 | was `make/gameplay-1`, H→T (CU F15) |
| `make/gameplay-2`, `make/gameplay-3` | Option SM/GM: deleted | — | — | their allocation goes to the topic pages; the full listing to `reference/script-api` | SM F4; GM F3 |
| `make/scripting-physics-animation` | Option CU: Physics, sound and animation from scripts | T | L | scripting ch. 5 | was `make/gameplay-2`, after its topics (CU) |
| `make/scripting-player-side` | Option CU: The player's side from scripts: time, saves, window and options | T | L | scripting ch. 6 | was `make/gameplay-3` (CU) |
| `make/recipes` | Option GM: Helpers and patterns for game code | H | M | scripting "Building blocks and recipes" (Random, Timer, KeyRepeat, Motion; show/hide instead of create/destroy; cooldowns; state machines in code) | L→M (GM F3) |
| `make/patterns` | Option CU: Patterns for game code: state machines, commands, pools and events | C | L | new (curricula 1.13, GPP); examples from the samples' scripts | new (CU F12); CU keeps recipes L |
| `make/input` | Input and input actions | T | L | gamedev; audio-input "Controls players can change" (use side); + devices, hold vs toggle, the rebinding menu with capture | M→L (SM F18; GM F10; CU) |
| `make/physics` | Physics for game makers | T | L | gamedev; physics (use side); + use half of `physics/tuning` (`Physics.Simulation`, `physics.stats`, the pile that never sleeps); closing exercise G12 (cursor-ray toy) | From (GM F5, F11) |
| `make/characters-cameras` | Characters and cameras | T | L | unchanged; use home of interpolation for game code | role (GM F4; CU) |
| `make/sound` | Sound | T | M | unchanged; use home of residency ("request in `OnCreate`") | role (CU) |
| `make/ui` | Option SM/CU: Menus and HUDs | T | L | gameui "Making menus and HUDs"; + render-core "Text and fonts" (`TextComponent`: text without a canvas) | split (SM F8; CU F16); From (RA m8) |
| `make/ui-widgets` | Option SM: Making UI do things: widgets, events and scripts | T | M | gameui "Widgets, events and scripts" | new by split (SM F8); CU: `make/ui-interaction` "Buttons, events and pause menus" (T, M) |
| `make/ui` | Option GM: HUDs: canvases, anchors, text and images | T | M | gameui ch. 2 | split (GM F10) |
| `make/menus` | Option GM: Menus that work: buttons, sliders, focus, pause and main menus | T | L | gameui ch. 3, ch. 2 (main menu scene); + the players' settings menu (volume, window, vsync, graphics row) | new by split (GM F10, F23) |
| `make/levels-saves` | Levels, loading screens and save files | H | L | gamedev; use home of additive loads and loading scenes | retitle (GM F23) |
| `make/large-worlds` | Large worlds | T | L | unchanged; the exported-start check moves to `make/export` | ED F19 |
| `make/big-scenes-fast` | Making your game run fast | T | M | render-scene "Tutorial: making a big scene draw fast"; + `worlds/measuring` (`--perf-log`), Performance panel, `renderStats`, quality costs | retitle (GM F5); W8r (RA M7) |
| `make/play-test-debug` | Playing, testing and debugging | H | M | gamedev; + debugger attach; use home of pausing, stepping and determinism | moved (GM: after the scene-scripting page; CU: position 32) |
| `make/command-line` | Option ED: Driving the editor from a terminal | T | M | automation "Driving the editor from outside"; Needs `make/editor-tour`, `make/scenes-entities` | moved from `automation/outside` (ED F11) |
| `make/commands` | Option GM: Running editor commands yourself: StrataCLI and command scripts | H | M | automation "Driving the editor from outside" (use side); skill make-a-game §1 | before automated-playtests and animation (GM F6) |
| `make/editor-from-outside` | Option CU: Driving the editor from outside | T | M | moved from `automation/outside` | CU F15 |
| `make/automated-playtests` | Automated play-tests | H | M | gamedev 1.17, 1.19; command scripts with `play.step`, `input.sequence`, `expect`, `until`, `bind`; replay export as a regression test; `ui.create`/`ui.layout`/`ui.hitTest`/`input.click` checks | agent material out (ED F10; GM F10); `ui/testing` in (GM F5); CU keeps "…and AI agents" |
| `make/ai-agent` | Option ED: Working with an AI agent | T | M | automation "Connecting an AI agent (MCP)": connect Claude Code, toolsets, presence, Activity, Undo to here, safe steering | new (ED F10) |
| `make/agent-game` | Option ED: Project: a game made by an agent | T | L | automation "Making a game as an agent"; skill `strata-make-a-game`; Tetris as the model | new (ED F10) |
| `make/with-an-agent` | Option GM: Making a game with an AI agent | H | M | automation "Connecting an AI agent", "Making a game as an agent"; the launcher's agent card; Activity panel | new (GM F10, F16) |
| `make/export` | Exporting and shipping | T | M | gamedev; + worlds-runtime "Shipping a game: the export" (use side, hands-on 7, 9); + "Giving your game to players" (credits screen, notices file, SmartScreen, quarantine, `.desktop`); + "A world that waits for its ground" | From (ED F6, F19; GM F20) |
| `make/designing-a-game` | Option GM/BG: Planning a small game: the core loop, scope, prototype, playtest | C | M | curricula 1.13; gamedev concept 23 (testing); the samples' READMEs as examples (BG: + GPP's State, Update Method, Object Pool) | new before Coin Run (GM F17; BG 14) |
| `make/game-design` | Option CU: Designing a small game: core loop, scope, feel and playtesting | C | M | new (curricula 1.13) | new (CU F12) |
| `make/project-coin-run` | Option GM: Project: Coin Run, a first finished game | T | L | gamedev G8 (rolling-ball variant); skill make-a-game §4-8 | redesigned, end of block A (GM F11) |
| `make/project-coin-run` | Option CU: Project: Coin Run, a first finished game | T | L | gamedev §6 G8 | moved to position 19 (CU F14) |
| `make/project-coin-run` | Option BG: Project: Coin Run, a first finished game | T | — (short; size not given) | assembles and polishes the stages built after `make/first-script`, `make/input`/`make/physics`, `make/ui`/`make/sound`, `make/export` | BG 13 |
| `make/project-tetris` | Project: Tetris | T | XL | unchanged; after recipes and automated-playtests; each section ends with a "you should now have" picture | GM F2; BG |
| `make/animation` | Animation for game makers | T | L | unchanged; + the how-to of `animation/editor` (`animation.*` commands, Asset tab tables, Inspector's live state, preview chip) · W8 (animation-graph) | SM F1, F11; GM F5; CF F11; ED F14; CU F13 |
| `make/project-platformer` | Project: a third-person platformer | T | XL | unchanged · W8 (animation-graph) | SM F1; CU F13 |
| `make/script-builds` | Building and shipping script modules | H | M | unchanged; building outside the editor, other compilers, long paths; "what a module is" at use level | moved to block C (GM F8); CU |
| `make/samples` | Studying the samples | H | M | unchanged · W8 (animation-graph) for the robot's description | SM F1 |

The two complete orders:
- **GM (three blocks):**
  - *A, "Your first finished game"* (no W8 page): editor-tour, project-files, scenes-entities, transforms-units, assets,
    materials, prefabs, lighting, first-script, cpp-1, cpp-2, gameplay-math, script-loop, scripting-scene,
    play-test-debug, input, physics, sound, ui (HUDs), export, designing-a-game, project-coin-run.
  - *B, "Bigger games":* recipes, menus, levels-saves, commands, automated-playtests, project-tetris,
    characters-cameras, animation, project-platformer.
  - *C, "Polish, scale and help":* lamps, reflections-gi, look, quality, big-scenes-fast, large-worlds, with-an-agent,
    script-builds, samples.
- **CU (39 rows):** 1 editor-tour, 2 scenes-entities, 3 transforms-units, 4 assets, 5 materials, 6 prefabs,
  7 cpp-for-scripts, 8 first-script, 9 script-loop, 10 scripting-the-world, 11 input, 12 physics,
  13 characters-cameras, 14 sound, 15 ui, 16 ui-interaction, 17 export, 18 game-design, 19 project-coin-run,
  20 lighting, 21 local-lights, 22 look, 23 reflections, 24 gi, 25 animation, 26 scripting-physics-animation,
  27 levels-saves, 28 scripting-player-side, 29 patterns, 30 recipes, 31 project-tetris, 32 play-test-debug,
  33 editor-from-outside, 34 automated-playtests, 35 large-worlds, 36 big-scenes-fast, 37 script-builds,
  38 project-platformer, 39 samples.
- **ED's additions:** `make/undo-save-recover` after prefabs; `make/command-line` before `make/ai-agent`; then
  `make/agent-game`, then `make/automated-playtests`.

**Part 2 — basics** (the union of rows; BG and CU each proposed a whole table)

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `basics/first-program` | Your first program: write it, build it, run it, break it | T | M | new; sets up the reader's workbench (compiler, terminal, editor, `sketches/`) per OS | new, also G (BG 1, 6) |
| `basics/programming` | Option CU: Programming from zero: values, functions, loops and classes | C | XL | new; sketches compiled; learncpp lessons linked per section | new, track B (CU F9) |
| `basics/programming-1` | Option BG: Values, variables, decisions and loops | P | M | new | BG 1, also G |
| `basics/programming-2` | Option BG: Functions, parameters and the call stack | P | M | new | BG 1, also G |
| `basics/programming-3` | Option BG: Grouping data: arrays, strings, structs and classes | P | M | new | BG 1, also G |
| `basics/tools` | Your workbench: the terminal, folders and paths, git, a code editor (BG) / Tools of the trade: the terminal, git, an IDE and a debugger (CU) | T | M | new (curricula 1.1 git, 1.18 debuggers) | new (BG 6; CU F12) |
| `basics/debugging` | Finding bugs: compiler errors, logs and the debugger | T | M | new | new, also G (BG 6); CU has `core/debugging` instead |
| `basics/computer` | How a computer runs a program: CPU, memory, stack, heap and caches | C (BG: P) | L | new; scene-ecs concept 4; foundation concepts 16-17; + allocators, SIMD, AoS vs SoA; + processes (pid, exit code, streams, environment, children) | From (CF F24; CU; ED F21) |
| `basics/numbers` | Numbers in a computer: integers, bits, floating point and precision | C | M | new (curricula 1.1 floating point, 1.2 robustness); two's complement, shifts and masks, packing keys, IEEE 754, spacing with magnitude, rounding and determinism | new: CU after computer, ED after bytes (CU F12; ED F12; RA M2 option) |
| `basics/bytes` | Option BG: Bytes, integers, floating point, text, JSON and hashes | P | L | foundation concepts 23, 26; assets concept 19; build-test excerpt 13 | retitle, M→L, numbers inside (BG 4; RA M2 option "Bytes, numbers, files, text and hashes") |
| `basics/bytes` | Option CU/ED: Bytes, files, text and hashes | C | M | foundation concepts 23, 26; assets concept 19; build-test excerpt 13; JSON named (BG 25) | From only (CF F24) |
| `basics/cpp` | Option CU: The C++ you need to read Strata | C | XL | foundation "C++ for engine code"; scene-ecs concept 17; the "Reader must know first" columns of foundation, scene-ecs, assets; + undefined behavior | From (CF F24; CU); Needs `basics/programming` |
| `basics/cpp-memory` | Option BG: Pointers, references and who owns what (RAII, `Scope`, `Ref`, move) | P | M | split from `basics/cpp` | BG 1 |
| `basics/cpp-classes` | Option BG: Classes in depth: inheritance, `virtual`, `override`, operators | P | M | split | BG 1 |
| `basics/cpp-generic` | Option BG: Templates, lambdas and the standard library's containers | P | M | split | BG 1 |
| `basics/cpp-modern` | Option BG: The modern C++ Strata uses: `optional`, `span`, `string_view`, `constexpr`, `enum class`, `if constexpr`, `requires`, macros | P | M | split | BG 1 |
| `basics/data-structures` | Data structures and what they cost | P | L | new; arrays, lists, hash maps, queues, trees, graphs, big-O | new (BG 5) |
| `basics/math-numbers` | Numbers, functions, powers, logarithms and angles | P | L | new; before math-vectors; also G | new (BG 3) |
| `basics/math-vectors` | Vectors: length, direction, dot and cross products (CU, L) / Vectors (BG, M) | C/P | L/M | split from the XL page (the pilot keeps this id) | split (CU F16; BG 8) |
| `basics/math-matrices` | Matrices and transforms: TRS, hierarchies, homogeneous coordinates and conventions | C | L | split; home of conventions | split (CU; BG) |
| `basics/math-projection` | Cameras and projection: view, perspective, orthographic, frustums and depth | C | L | split (FGED vol. 2 ch. 6) | split (CU) |
| `basics/math-geometry` | Geometry for engines: rays, planes, boxes, intersection tests and robustness | C | M | split (Ericson [S6]) | split (CU) |
| `basics/math-rotations` | Rotations, quaternions and interpolation | C | L | animation "Quaternions, slerp and TRS"; + lerp, easing, curves | retitle (CU) |
| `basics/math-change` | Change over time: rates, accumulation, motion and interpolation | P | L | new; derivatives, integrals, Euler, Newton's laws | new, also G (BG 4) |
| `basics/color` | Color and light for programmers: linear, sRGB, HDR | C | M | new; + chromaticity, white point, gamut; the working space (scene-linear Rec. 709); home of the half-float range | learn lines (RA m2; RB F6, App. D) |
| `basics/signals` | Sampling, aliasing, filtering and noise | C | L | new; curricula 1.2 "Signals" and "Randomness"; kernels, mip prefiltering, white vs blue noise, Hammersley, Vogel, Poisson, IGN, ordered dither, spatial denoising | new (RB F7; CU F12); BG: `basics/sampling` "Sampling, aliasing and filtering" (P, L) |
| `basics/math-light` | Option CU: Math for light: integrals, Monte Carlo, spherical harmonics, octahedral maps | C | L | unchanged | kept (CU) |
| `basics/math-probability` | Option BG: Chance: random numbers, probability and Monte Carlo | P | M | split from math-light | BG 4 |
| `basics/math-sphere` | Option BG: Directions on a sphere: solid angle, spherical harmonics, octahedral maps | P | M | split from math-light | BG 4 |
| `basics/threads` | Threads, atomics and races | C | L | new; foundation concept 16; home of the general topic | From (CF F24; CU) |
| `basics/gpu` | Option RA: How a GPU draws a frame (moved) | C | L | the pipeline at a glance, textures, sampling and filtering, buffers, command submission, frames in flight | `gpu/how-a-gpu-frame-works` moved (RA M6a) |
| `basics/reading-code` | Option CU: removed | — | — | becomes `core/reading-code` | CU F15; BG keeps it (H, M) |

Orders: BG — first-program, programming-1..3, tools, debugging, computer, bytes, cpp-memory, cpp-classes, cpp-generic,
cpp-modern, build, data-structures, math-numbers, math-vectors, math-matrices, math-rotations, math-change, color,
sampling, math-probability, math-sphere, threads, reading-code. CU — programming, computer, numbers, bytes, tools, cpp,
build, math-vectors, math-matrices, math-rotations, math-projection, math-geometry, color, signals, math-light, threads.

**Part 3 — core**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `core/conventions` | Ownership, errors and logging in Strata | I | M | unchanged | moved to second row (CF F13); CU keeps it ninth · W8L (CF) |
| `core/reading-code` | Following one feature from a click to a pixel | T | M | moved from `basics/reading-code`; Needs `core/map`, `basics/tools` | CU F15 |
| `core/time` | Time: delta time, the fixed step and time scale | C | L | foundation; physics "The fixed step" | retitle (CF F4 a; CU F8); CF F4 b keeps the title and rewords the home row · W8L |
| `core/frame-loop`, `core/windows-events`, `core/layers-registries` | unchanged | I | — | unchanged | W8L (CF F12) |
| `core/testing` | Option CU: Testing an engine | C | L | moved from `engineering/testing` | after conventions (CU F5) |
| `core/debugging` | Debugging the engine: debuggers, logs, asserts, crash dumps and leaks | H | M | new (curricula 1.18); foundation §1.5, §1.7 (`Platform` debugger, memory) | new (CU F12) |
| `core/jobs` | Threads and the job system | I | L | foundation | XL→L (CU F16) |
| `core/profiling` | Measuring the frame: the frame profiler, Tracy and the method | I | M | foundation; + home of the measuring method | retitle (CU); contradicts CF F22 and RA m6 (§4.3) · W8L |
| `core/platform` | Talking to the operating system | I | L | foundation §1.7 (`Platform`), §1.2 (interrupts, GUI subsystem, power throttling), concepts 19, 21-22: seams and detection, console vs GUI programs, signals and exit codes, dialogs, thread priorities, sleep precision | M→L, split (CF F14) |
| `core/files` | Files you can trust | I | M | foundation §1.7 (`FileSystem`, `AtomicFileWriter`, `FileReader`, `FileLock`, `FileWatcher`, `BoundedRead`), concepts 23-24: UTF-8 paths, atomic writes, private files and TOCTOU | new by split (CF F14) |

CU's order: map → reading-code → first-frame → frame-loop → time → windows-events → engine-modules → layers-registries
→ conventions → testing → debugging → jobs → profiling → platform → math. (CF: conventions second, files after
platform.)

**Part 4 — world**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `world/systems`, `world/projects-settings` | unchanged | I | — | unchanged | W8L (CF F12) |
| `world/interpolation` | Drawing between fixed steps | I | L | unchanged; + the deferred list (`Docs/Roadmap.md` 1698-1702) as "what it does not do yet" | M→L (CF F18) · W8L |
| `world/serialization` | Option CF: Scene documents: text, streams and the cooked form | I | L | scene-ecs §1.9 | retitle, formats only (CF F17) |
| `world/sub-scenes` | Option CF: Loading scenes: whole, additive and in slices | I | L | scene-ecs §1.8, §1.11, `SceneAsset` (§1.10); worlds-runtime "Sub-scenes and the frame budget"; `SceneLoader` and its states, `PrepareSystems`/`PrepareLoadedScene`, prepared states, `RequestSceneLoad`, `ReleaseInBackground` | retitle, M→L (CF F17) |
| `assets/scene-documents` | Option CU: Saving and loading scenes | I | L | moved from `world/serialization` | CU F3 |
| `assets/prefabs` | Option CU: Prefabs: the data model | I | L | moved from `world/prefabs` | CU F3 |
| `assets/sub-scenes` | Option CU: Sub-scenes and the frame's work budget | I | M | moved from `world/sub-scenes` | CU F3 |
| `world/tutorial-component` | Tutorial: adding a component and a system | T | L | unchanged; creates WindZone | moved to the end of part 4 (CF); CU keeps it before projects-settings |

**Part 5 — assets**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `assets/textures` | Textures for the GPU: mips, color spaces, block compression | C | M | assets ch. 4 (the general problem and the formats) | L→M (CF F16) |
| `assets/texture-cooking` | Cooking textures: Strata's importer, mips and BC7 encoder | I | L | assets §1.8 (texture importer, defaults from name tokens, version 5, `ChooseFormat`, Mitchell cooker, `BC7Encoder.cpp`, `HDRSun` setting, STTX v2, `GetMipByteSize`, BC decode fallback), excerpts 12-15, rules 4, 14, 15 | new after textures (CF F16) |
| `assets/uploads` | Option RA: Getting bytes to the GPU: staging and budgeted uploads | I | L | render-core 1.5; assets "Budgeted uploads and staging" | merged with `gpu/upload-queue` (RA M6 b) |
| `assets/uploads` | Option CF: Budgeted uploads | I | M | unchanged; owns steps of `c_AssetUploadStepBytes`, the first step of a frame, `AssetFinalizeContext`/`Result`, `Texture::UploadLevels`, one batch per `Update` (`gpu/upload-queue` keeps `PlanStep`, `StagingPool`, the transfer queue, `PrepareBackBuffer`) | item split (CF further) |
| `assets/robustness` | Corruption, crash safety and cancellation | C | M | assets; home of "untrusted input: validate before use, checksums, bounded sizes" and "write-ahead ordering" | I→C (CF further) |
| `assets/mip-streaming` | Option CU: removed | — | — | becomes `draw/mip-streaming` | CU F3 |

**Part 6 — gpu**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `gpu/how-a-gpu-frame-works` | How a GPU works and draws a frame | C | L | render-core; + the hardware: waves, occupancy, bandwidth, branches; + pixels as samples and the kinds of aliasing (RA m4) | retitle (CU F12); RA M6 a moves it to `basics/gpu` |
| `gpu/vulkan-nvrhi` | Vulkan, NVRHI, the graphics device and the Renderer's services | I | L | render-core; + 1.2-1.3 (`GraphicsModule`, back-buffer capture, the `Renderer` hub, samplers, fallback textures) | retitle (RA m9) |
| `gpu/shaders` | Option CU: Shaders and compute: Slang, the build and the dialect | I | L | render-core; home of compute shaders and dispatches (barriers in `gpu/resources-lifetimes`) | retitle (CU F12) · W8L (CF) |
| `gpu/compute` | Option RA: Compute shaders: dispatches, thread groups, shared memory and atomics | I | M | render-core concepts 9, 13; render-scene concept 14 (prefix allocation); toy: a histogram and a prefix sum | new after `gpu/shaders` (RA M1) |
| `gpu/coordinates` | Coordinate systems and the camera: clip space, reversed depth, UVs | C | M | render-core; + `CameraComponent` (scene-ecs §1.2, `GetProjection`) | retitle (CU) |
| `gpu/first-triangle` | Tutorial: your first triangle in Strata | T | L | render-core; home of "writing a GPU test" | moved after `gpu/coordinates` (BG 12); role (RA M13) |
| `gpu/debugging` | Option CU: Debugging the GPU: validation layers, debug names and frame captures | H | M | new; after `gpu/first-triangle` (render-core §2 item 4, hands-on 12) | new (CU F12) |
| `gpu/frame-tour` | A frame of the scene renderer, pass by pass | I | XL | render-core; Option RA: + section "Looking inside a frame: validation messages, markers and a frame capture" (checked on the GPU in phase B) | W8r (RA M7); RA m9 |
| `gpu/binding` | Pipelines and binding: layouts, registers and bindless | I | L | render-core; + PSOs and the `PipelineKey` cache (render-core 1.6, concept 18; render-scene 1.4) | retitle (RA M16) |
| `gpu/upload-queue` | Option RA: removed (merged into `assets/uploads`) | — | — | — | RA M6 b |

**Part 7 — draw**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `draw/visibility-feedback` | Visibility feedback | I | S | unchanged | could be S (RA note) |
| `draw/skinned` | Option CU: moved to `animation/skinned-rendering` | — | — | — | CU F4; RA M9 keeps it with Needs `animation/skinning`, `animation/culling` |
| `draw/motion-vectors` | Option CU: moved to `image/motion-vectors` | — | — | — | CU F4; RB F8 keeps it without TAA as a prerequisite |
| `draw/mip-streaming` | Option CU: Mip streaming | I | L | moved from `assets/mip-streaming`; after `draw/visibility-feedback` | CU F3 |

**Part 8 — light**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `light/units-exposure` | Option RB: Light by the numbers: radiometric and photometric units | C | L | render-direct ch. 1 (radiometry, lumen/candela/lux/nit conversions, the spot rule, the sun-to-sky ratio, the reference table) | retitle (RB F6); CU and RA keep the title, with this page as the home of EV100 |
| `light/materials` | Strata's material model | C | L | render-direct (the model, maps, alpha modes, emission in nits, plausible albedos, IOR as a field, normal maps and tangent space as a concept) | allocation (RB F13) · W8 if showcase-engine lands (RB F22) |
| `light/material-data` | From a material file to the shader: the material record and its textures | I | M | render-direct 1.1 (GPU rows), code #2-#5, figure 5, rules 7-9 and 14 | new after materials (RB F13) · W8 if showcase-engine lands |
| `light/reflectance` | How surfaces reflect light: the reflection equation and microfacets | C | L | new; render-direct concepts 6-7; render-indirect concepts 2-3 | new before brdf (RB F5); CU puts the reflection equation in `light/brdf` instead |
| `light/brdf` | Option RB: The forward shader and the BRDF in code | I | L | render-direct ch. 3; RD 1.2 (variants, EQUAL test, `[earlydepthstencil]`, derivative rule, minimum roughness, `SanitizeHDR`), RD code #6, #7, #10, #19, figure 20, rules 6, 10, 29 | retitle (RB F5, F9) |
| `light/energy` | Option RB: Keeping the energy: directional albedo, the BRDF table and the white furnace | I | M | RD concept 9, RI concept 7, RD code #8, #9 (`BRDFLut.comp.slang:20-49`), RI code #1, #5, #6, furnace tests `GPUSceneLightingTests.cpp:860-1010`, shot `lookdev.furnace`, RI rule 2, RD figure 4, RI figure 6 | moved from `indirect/energy` (RB F1) |
| `light/energy` | Option CU: Keeping the light: energy compensation, the white furnace and specular anti-aliasing | I | M | moved from `indirect/energy`; home of the BRDF table | CU F4 (specular AA here contradicts RB F4) |
| `light/measuring-light` | Option RB: Measuring light: the debug views and their statistics | I | M | render-direct 1.10, render-indirect 1.9 | moved from part 9, H→I, after energy (RB F11) |
| `light/measuring` | Option CU: Seeing what the renderer computes: debug views, statistics and the light meter | I | M | moved from `indirect/measuring-light` | after units-exposure (CU F4) |
| `light/lights` | Option RB: Lights: the sun, points and spots | I | L | render-direct 1.3 (components, falloff, cone, one sun, records, `LightData`, spot bounds, drawn transforms, preview lighting) | W8 removed (RB F2) |
| `light/sun` | Option CU: The sun | I | M | split from `light/lights` | not W8 (CU F13) |
| `light/local-lights` | Option CU: Point and spot lights | I | M | split from `light/lights` · W8 | CU F13 |
| `light/many-lights` | Many lights: culling and clustered forward shading | I | L | render-direct; keeps tiled vs clustered and Strata's culling | RB: phase A, light-loop section revised at 0.8.0; CU: W8 |
| `light/area-lights` | Option RB: Lights with size: sized highlights and area lights | I | L | render-direct concept 12, 1.13; lobe widening (`GetSourceLobeAlpha2`, `GetLobeAlpha`, `RenderData::GetSunLobeAlpha2`, `PBR.slang:12-31, 119-124`); W8 section: rect lights (branch `agent/wave8-area-lights`) | retitle; after many-lights; if 0.8.0 has no rect lights the section becomes "how engines shade area lights" and the page shrinks to M (RB F3) |
| `light/area-lights` | Option SM: removed until a release brings area lights | — | — | content to `appendix/not-in-strata` | SM F23 (CU keeps it unchanged · W8) |
| `light/sun-shadows-1` | Sun shadows I: stable cascades | I | L | render-direct; + sun caster selection, the cascade cache and its versions, cascade occlusion; + the shadows view | allocation (RA M5; RB F11, F16; CU F4) |
| `light/sun-shadows-2` | Sun shadows II: the soft shadow of a real sun | I | XL | unchanged | note: one sentence about TAA and local lights turns false on wave 8 (RB F15) |
| `light/sky` | Option RB: The sky as a light: sources, sun extraction and presets | I | M | render-direct 1.8 (source rows) | split, L→M (RB F12) |
| `light/atmosphere` | Option RB: Earth's atmosphere and aerial perspective | I | L | render-direct 1.8 (atmosphere rows), 1.9 (aerial perspective), concept 20 | new by split (RB F12) |
| `light/fog` | Option RB: Height fog | I | M | render-direct 1.9 (the closed-form integral, its lighting, the sky at infinity, `c_MinHeightFalloff`, what non-volumetric fog cannot do) | retitle (RB F12) · W8 if `volumetric` lands (RB F22) |
| `light/clearcoat-transmission` | Option RB: Transparency, clear coat and glass | I | L | render-direct; home of transparency, blending and premultiplied alpha, and of the scene-color copies | retitle, M→L (RB F18, F23) |

Orders: RB (18 pages) — units-exposure, materials, material-data, reflectance, brdf, energy, measuring-light, lights,
many-lights, area-lights, shadow-basics, sun-shadows-1, sun-shadows-2, local-shadows, sky, atmosphere, fog,
clearcoat-transmission. CU (14 pages) — units-exposure, measuring, materials, brdf, energy, sun, local-lights,
area-lights, many-lights, shadow-basics, sun-shadows-1, sun-shadows-2, local-shadows, clearcoat-transmission.

**Part 9 — indirect** (placed after part 10, per RB F8 and CU F4)

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `indirect/problem` | The indirect-light problem | C | M | render-indirect; + a Monte Carlo path tracer sketch of the Cornell box as the reference image | From (RB F20) |
| `indirect/ibl` | Image-based lighting and the split sum | I | L | render-indirect; the split sum's prefiltered half, reusing `light/energy`'s table; home of the horizon fade | allocation (RB F1, F4; CU) |
| `indirect/seam` | Where indirect light meets the surface: inputs, gathers and fallbacks | I | M | render-indirect 1.3, code #8-#10, #30 | new after ibl (RB F10) |
| `indirect/sky` | Option CU: The sky and the atmosphere | I | L | moved from `light/sky`; home of "sky as a light source" | CU F4 |
| `indirect/fog` | Option CU: Aerial perspective and height fog | I | M | moved from `light/fog` · W8? (volumetric) | CU F4, F13 |
| `indirect/energy`, `indirect/measuring-light` | removed (moved to part 8) | — | — | — | RB F1, F11; CU F4 |

Orders: RB — problem, ibl, seam, ao, probes, ssr, gi-voxels, gi-cascades, gi-limits. CU — problem, ibl, sky, fog, ao,
probes, ssr, gi-voxels, gi-cascades, gi-limits.

**Part 10 — image**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `image/why-post` | Why images need post-processing, and Strata's post chain | C | M | render-image ch. 1; 1.1 whole; code #1-3 | S→M (RA M12; CU F16) |
| `image/exposure` | Exposure: camera, eye and meter | I | L | render-image; CU/RA: metering, adaptation and the key only (EV100 is `light/units-exposure`'s); RB: also the camera exposure and EV100 | allocation contradicts (§4) |
| `image/grading` | White balance, grading and lookup tables | I | L | render-image ch. 5 | M→L (RA m2) |
| `image/motion-vectors` | Option CU: Motion vectors and motion history | I | M | moved from `draw/motion-vectors`; before `image/taa` | CU F4 |
| `image/motion-blur` | Motion blur | I | M | render-image 1.7 (tile max, neighbor max, gather, CPU profile model, shutter-angle and cut rules), concept 16, diagram 19 | split (RA m1) |
| `image/depth-of-field` | Depth of field | I | L | render-image 1.7 (five shaders, thin-lens CoC, `CameraLens::FromEntity`, the camera's fields), concept 17, diagram 20 | split (RA m1) |
| `image/quality-settings` | Quality settings and players' graphics options | I | L | unchanged | W8r (RA M7), or W8 with no preset values in its prose (RB F15) |
| `image/tutorial-post-effect` | Tutorial: adding a post effect | T | L | unchanged; Needs `engineering/feature-test` and the GPU-test home | written in wave 6 (RA M10) |

**Part 11 — physics**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `physics/collision-detection` | Collision detection: shapes, broad phase and narrow phase | C | L | split from `physics/how-simulation-works` (Catto's BVH and GJK talks, Ericson) | CU F16 |
| `physics/dynamics` | Rigid body dynamics: integration, contacts, solvers, sleep and continuous collision | C | XL | split; the toy solver | CU F16 |
| `physics/building-bodies` | From entities to bodies: records, shapes, mesh colliders | I | L | physics §1.2-1.4 (records and slots, `AddColliderParts`, baked scale, shared hulls, `ApplyMass`, mesh cooking and the provider, pending and suspended bodies, change rounds) | split (SM F6) |
| `physics/world-step` | Inside `PhysicsWorld`: one step | I | L | physics §1.5 (`Simulate`, sync, forces and teleports, the characters' step, events per step, the write-back bitmap, parallel write-back, the task system, determinism) | XL→L (SM F6) |
| `physics/collision-layers` | Collision layers | I | M | unchanged | before contacts-triggers (SM F20); CU's order puts it after queries |
| `physics/scale-streaming` | Option SM/ED: Physics at scale and in streaming worlds | I | M | unchanged; Needs `world/sub-scenes` | SM F7; ED F6 |
| `physics/capacity` | Option CU: Physics at scale: capacities, growth and sliced creation | I | M | first half of `physics/scale-streaming`; parking, reservation and `MaxBodiesInRadius` go to `worlds/physics-scripts` | CU F6 |
| `physics/tuning` | Tuning and measuring | H | M | solver-side tuning only; the use half moves to `make/physics` | GM F5 |

**Part 12 — animation**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `animation/clips` | Clips: sampling motion | I | L | unchanged | M→L (SM F19) |
| `animation/skinned-rendering` | Option CU: Skinned meshes in the renderer | I | M | moved from `draw/skinned`; after `animation/skinning` | CU F4 |
| `animation/state-machines`, `blending`, `time-events`, `root-motion`, `system`, `culling`, `limits` | unchanged | — | — | unchanged | W8 (animation-graph) (§3.3) |
| `animation/graph` | The animation graph: nodes, parameters and `.stanimator` 2 | I | L | new · W8 | after blending (SM F1) |
| `animation/sync-layers` | Sync tracks, blend spaces and masked layers | I | L | new · W8 | SM F1 |
| `animation/editor` | Edit-mode poses and previews | I | M | animation (§1.11, concept 21) · W8 (animation-graph) | H→I, retitle; how-to into `make/animation` (SM F11) |

**Part 13 — audio** (SM F15: option a or b)

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `audio/clips-voices-sources` | Option a: Clips, voices and sources | I | L | unchanged | M→L |
| `audio/scene-system` | The Audio scene system | I | L | unchanged | M→L |
| `audio/clips` | Option b: clip loading and the importer (title not given) | I | M | audio-input §1.2 | new by split |
| `audio/voices-sources` | Option b: voices and sources (title not given) | I | M | audio-input §1.3 | new by split |

**Part 14 — input**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `input/how-input-works` | Option SM: How input reaches a game: events, polling, edges and intents | C | M | audio-input B1, B2, B5-B7 | new first row (SM F12) |
| `input/devices-to-intents` | Option CU: How games read players: devices, events, polling and actions | C | M | audio-input §2 part B | new first row (CU F11) |
| `input/rebinding` | Players' bindings inside the engine (the bindings file, capture in `InputActions`) | I | M | audio-input (the code side) | retitle (GM F5) |
| `input/simulated` | Simulated input | I | M | unchanged; CU: + the `input.sequence` section of `editor/stepping`; SM: device and merge rules only | wave 6 (SM F2); contradiction (OL7 f) |

**Part 15 — scripting**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `scripting/host-api` | The host API: engine services behind a C table (SM) / The host API: contexts, guards and problems (CU) | I | L | scripting "The host API" (code #22-#24, concept 16) | T→I, split (SM F9; CU F15) |
| `scripting/tutorial-host-function` | Tutorial: adding a host function and a callback (SM) / Tutorial: adding a host function (CU) | T | M | scripting hands-on E2-E3; CU: adds `Wind::GetStrength` to WindZone | new by split |
| `scripting/crash-containment` | Crash containment | I | XL | unchanged | L→XL, or split (SM F17) |
| `scripting/symbolization` | From an address to a file and line | I | M | scripting concept 13, code #21 | new by split (SM F17, option) |

**Part 16 — ui**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `ui/text` | Text and text fields | I | M | gameui (how rects drive `ShapeText`; input-field editing: concept 20, §1.9 input-field row, `GameUISystem.cpp` 557-747, code #18) | retitle (SM F16; RA m8) |
| `ui/testing` | Testing and automating game UI | H | M | unchanged | moved into `make/automated-playtests` (GM F5), or written in wave 6 (SM F2) |

**Part 17 — worlds**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `worlds/physics-scripts` | Worlds meet physics and scripts | I | M | unchanged; CU: + parking, reservation by the streamer, `MaxBodiesInRadius` | CU F6 |
| `worlds/editing` | Option ED: moved to `editor/worlds` | — | — | — | ED F1; CU keeps it in worlds with the editor's core earlier |
| `worlds/export` | Shipping a game: the export | I | L | worlds-runtime §1.8-1.9: the state machine, up-front checks, "fail before writing", planning, world cooking at export, what the folder holds | narrowed (ED F8) |
| `worlds/game-identity` | (title not given; scope: the game's identity) | I | M | worlds-runtime §1.8: manifest v5 and why it is untrusted, `ProjectGameInfo`, `GamePresentation`, saves keyed by Name, `GameIcon`, `PEResources`, `DesktopEntry`, the Dock icon, signing after export | new; order export, game-identity, runtime (ED F8) |
| `worlds/measuring` | Measuring shipped games | H | M | unchanged | moved into `make/big-scenes-fast` (GM F5); perf-log columns re-checked at 0.8.0 (ED F18) |
| `worlds/templates` | removed | — | — | becomes `editor/projects` | ED F7 |

**Part 18 — editor**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `editor/deferred-commands` | Commands that take frames | I | M | editor-core (`Defer`, the runner, poll rules, `FrameTimeRecorder`, `editor.wait`/`editor.perf`, `MayDefer`, `WaitsForAssets`) | moved to third (ED F4) |
| `editor/projects` | Projects: creating, opening and migrating | I | M | editor-core §1.9 (templates and `scene.new {template}`, samples as copies without `.strata`, recent projects, `BeginOpenProject`, `ProjectMigration`, opening scenes in the background and the read-only guard, `project.create/open/close/openSample`); worlds-runtime "Launcher, templates and samples" (code side) | new after deferred-commands (ED F7) |
| `editor/undo` | Undo and redo | I | XL | unchanged | L→XL (ED F16) |
| `editor/worlds` | Option ED: Editing a streamed world | I | L | worlds-runtime "Editing a streamed world" | moved from worlds, after prefab-instances (ED F1) |
| `editor/play-mode` | Play mode: the running copy | I | L | editor-core | retitle (ED F5) |
| `editor/script-builds` | Building scripts from the editor: toolchains, CMake, diagnostics | I | M | new; scripting §1.3, §1.7 | new after play-mode (SM F10) |
| `editor/stepping` | Pausing, stepping and exact tests | I | M | SM: home of holds in fixed steps, `input.sequence`, `input.click`; CU: without the `input.sequence` section | contradiction (OL7 f) |
| `editor/journal` | The activity journal and replays | I | M | automation "Recording and replaying"; editor-core §1.11 (`CommandJournal`, `BuildReplayScript`, origins, agent presence) | moved from automation, before command-scripts (ED F3) |
| `editor/command-scripts` | Command scripts and batches | I | M | editor-core (`expect`, `bind`/`$ref`, `until`, `editor.batch`) | retitle (ED F3) |
| `editor/placement` | Placing content | I | M | unchanged | written last in wave 6 and re-read at the pin move (ED F18); W8? for editor-ux (CU F13) |
| `editor/camera-viewport` | The editor camera and viewport state | I | M | unchanged | moved next to `editor/scene-view` (ED F5) |
| `editor/imgui` | Option CU: Dear ImGui from first principles (becomes `editor-ui/imgui`) | C | L | merges `editor/immediate-mode` | CU F21 |
| `editor/imgui-backends` | ImGui backends | I | L | unchanged; Needs `gpu/vulkan-nvrhi` | M→L, or split into `editor/imgui-platform` (I, M) + `editor/imgui-renderer` (I, L) (ED F16; RA) |
| `editor/design-system` | Option CU: The design system: theme, fonts, icons and UI scale | I | L | merges `editor/ui-scale`; home of the editor's font loading (ImGui's own atlas) | CU F21; ED |
| `editor/lists` | Lists that scale | I | L | unchanged | M→L (ED F16) |
| `editor/inspectors` | Inspectors from reflection | I | L | editor-ui "Inspectors generated from reflection" and the Asset tab (`AssetInspectorPanel`, `MaterialEditor`, `AnimationAssetViews`, `AudioPreview`); examples chosen outside wave 8 subjects | From (ED F20, F18) |
| `editor/scene-view` | The Scene view | I | XL | unchanged | re-read at the pin move (ED F18) |
| `editor/shortcuts-status` | Option CU: Shortcuts, focus and feedback: the status bar, toasts and idle throttling | I | L | merges `editor/shortcuts` and `editor/status` | CU F21; ED would rather merge shortcuts with game-view ("The Game view, shortcuts and who owns the keyboard", L) |
| `editor/launcher-dialogs` | (title not given; settings windows moved out) | I | M | editor-ui §1.11 | L→M, split (ED F17) |
| `editor/settings-windows` | Settings windows from schemas | I | M | editor-ui §1.12; Needs `world/projects-settings` | new by split (ED F17) |

CU option: pages 1-15 become the part "The editor's core" (`editor/`), placed after Assets; pages 16-32 become the part
"The editor's interface", with ids under `editor-ui/` (OL7 b).

**Part 19 — automation** (track E only, ED F11)

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `automation/outside` | removed (moved to part 1) | — | — | — | ED F11; GM F6; CU F15 |
| `automation/agents` | How the editor makes games with agents | C | M | automation 2.1, 2.12 (tool design), 2.13, 2.14; gamedev ch. 30 (the agent path diagram) | From (ED F15) |
| `automation/journal` | Option ED: removed (moved to `editor/journal`) | — | — | — | ED F3 |

**Part 20 — engineering**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `engineering/testing` | Option CF: Testing an engine | C | M | build-test ch. 7 (concept half: test kinds, determinism and flakiness, regression tests that fail without the fix, coverage by construction, sweeps as an idea) | L→M (CF F15); CU moves it to `core/testing` |
| `engineering/test-program` | Inside StrataTests | I | L | build-test §1.6 (`TestMain`, helper modes, fake CMake and editor, `CoreShards.json` and `Testing.Shards`, labels, fixtures, locks, `SelectSweepOffsets` and `StrataTests.Fuzz`, `TestCrashReporter`, test helpers), excerpts 19-23 | new before test-kinds (CF F15) |
| `engineering/generated-code` | Generated code: shaders, embedded files, version stamps and committed generators | I | M | build-test §1.4, §1.13 (GenerateBlueNoise, FitFilmic, FitAOMultiBounce, GenerateAreaTable, GenerateWhiteBalance, GenerateBrandAssets, GenerateShowcase*, GenerateIslandTerrain, GenerateIconHeader.py, the feature test's GenerateAssets.py); render-image 1.11 | retitle (CF F25; RA note) · W8L |
| `engineering/measuring` | Measuring performance honestly: noise, percentiles, budgets | C | M | foundation concept 20; build-test concept 21 | new before perf-lab (CF F22); contradicts CU (`core/profiling`) |
| `engineering/cmake`, `engineering/third-party`, `engineering/ci` | unchanged | — | — | unchanged | W8L (CF F12) |

**Part 21 — reference**

| id | Title | Source | Change (critics) |
| --- | --- | --- | --- |
| `reference/scene` | Scene, reflection and settings: types, flags, formats, limits | generated from the headers (scene-ecs ch. 12: Scene/Entity API, `ComponentFlags`, `PropertyType`/`PropertyFlags`, `SettingsField` types, file formats, `c_Max*` limits, 512 KiB settings cap) | new (CF F21) |
| `reference/assets` | Asset types, file formats, importer versions, budgets and statistics | assets "Reference"; `AssetResidencyBudgets`, `AssetManagerStats` | retitle (CF F21) |
| `reference/performance` | Measured costs and their budgets | generated from `StrataTests/Perf/Budgets.json` | new (CF F21) |
| `reference/renderer` | Passes, bindings, switches, statistics, debug views, quality rows, device requirements | as now; + `renderStats` keys (`EditorStateCommands.cpp`), `SceneRendererSpecification` and `SceneRendererStats` fields (`SceneRenderer.h`), fallback textures and samplers, a hand-checked table of the renderer's rules | retitle, generated only (RA M7, M11) |
| `reference/editor` | Editor reference: panels, shortcuts, arguments | editor-ui, editor-core, automation; option tables generated from `c_Arguments` (`EditorApplication.cpp` 63-82) and `RuntimeApplication.cpp` | From (ED F22) |
| `reference/script-api` | The complete script API | `StrataScriptHostAPI` (`ScriptABI.h`), `StrataScriptClassDesc`, SDK headers (SDKReader rules), `ST_SCRIPT_CLASS`/`ST_SCRIPT_FIELD`; `ST_SCRIPT_HOST_FUNCTIONS` lives in the engine (`Scripting/ScriptHostAPI.cpp:3431`), not in the SDK | source (PL m14) |
| `reference/commands` | The command catalogue | as now | may be one page per command group (SO 14) |
| `reference/glossary` | Glossary | as now | one `<dl>`, `tableOfContents: false` (SO 12) |
| `reference/animation` | Animation reference | as now | W8 (animation-graph) (SM F1) |
| `reference/worlds-runtime` | Worlds, export, runtime options, manifest | as now | re-check the perf-log columns at 0.8.0 (ED F18) |
| `reference/figures` | Index of figures and their recipes | as now; names the figure machine's GPU | RA note |
| `reference/index` | Index of terms and engine identifiers | generated: glossary home pages + the excerpt fences' symbols | new (CU F18) |
| `reference/notation` | Conventions and notation | written, checked against `gpu/coordinates` and `basics/math-matrices` | new (CU F18) |

**Part 22 — appendix**

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `appendix/not-in-strata` | What Strata does not do, and how engines do it | C | L | as now; + `Docs/Releases/0.8.0.md` "Known issues" and "Not in this release" | From (CF F10) |
| `appendix/game-ai` | Game AI in general: steering, pathfinding, navigation meshes and behaviour trees | C | L | new (curricula 1.13; Red Blob Games); the samples' `Wander.cpp` as the one example | new (CU F12, F19) |
| `appendix/math-cheatsheet` | Math cheat sheet | R | M | as now; + "how to read the symbols" table | BG minor |

**New part — Capstone (`capstone`, track E)** (CU F17)

| id | Title | Kind | Size | From | Change (critics) |
| --- | --- | --- | --- | --- | --- |
| `capstone/plan` | Capstone I: designing a feature the way Strata does | T | M | new; WindZone grown into a feature: layers, registries, the rules that apply | new |
| `capstone/build` | Capstone II: from component to pixel | T | L | new; forces on bodies, a debug gizmo, an inspector inactive reason, the script API, the command | new |
| `capstone/land` | Capstone III: tests, the feature test, a budget, the review and CI | T | L | new; `engineering/feature-test`, `perf-lab`, `contributing`, a `ci/` branch | new |

Also from CU F18: one generated `index` page per part, and a `review` page for every part of eight or more pages.

### 3.3 Corrected W8 marks

| Page | Now | Proposed | Critics | Evidence |
| --- | --- | --- | --- | --- |
| `animation/state-machines`, `animation/blending`, `animation/limits` | — | W8 (animation-graph) | SM F1; CF F11; ED F14; CU F13 | `Docs/Plans/Wave8/plan.md` §4.5, tranche 2 |
| `animation/time-events`, `animation/system`, `animation/editor` | — | W8 (animation-graph) | SM F1; CU F13 | sync tracks, weighted events, graph nodes in jobs, Inspector and Asset tab tables |
| `animation/root-motion`, `animation/culling` | — | W8 (animation-graph) | SM F1 | transition root-motion modes; `WhenVisible` runs nodes |
| `make/animation`, `make/project-platformer`, `reference/animation` | — | W8 (animation-graph) | SM F1; CU F13; ED F14 (make/animation) | the robot becomes a Blend1D plus a layer; `.stanimator` 2 |
| `make/samples` | — | W8 (animation-graph) | SM F1 | the robot's description |
| `animation/graph`, `animation/sync-layers` (new) | — | W8 | SM F1 | — |
| `light/lights` | W8 | **Contradiction:** none (RB F2) / split into `light/sun` (none) + `light/local-lights` (W8) (CU F13) | RB; CU | the wave 8 branches touch neither `RendererComponents.h` nor `RenderLights.*` |
| `light/area-lights` | W8 | **Contradiction:** a W8 section only, with a fallback (RB F3) / out until a release brings it (SM F23) / unchanged (CU) | RB; SM; CU | no area-light stream in the Wave8 plan; the branch has CPU math only |
| `light/many-lights` | W8 | **Contradiction:** phase A, one section revised at 0.8.0 (RB F2) / W8 (CU) | RB; CU | local-lights changes 5 lines of the light loop |
| `light/local-shadows`, `indirect/gi-voxels`, `indirect/gi-cascades`, `indirect/gi-limits` | W8 | W8 (agreed) | RB; CU | local-lights and rc-world branches |
| `make/lighting` | W8 | split: lighting (none) + lamps or local-lights (W8) | GM F9; CU F13; RB App. C (W8, drafted in phase A) | — |
| `make/reflections-gi` | W8 | split: reflections (none) + global illumination (W8) | RB F14; CU F13 | reflections R1/R2 are on main |
| `gpu/frame-tour`, `make/big-scenes-fast` | — | W8r | RA M7 | new stats; `renderStats` keys; the GI join and volumetric passes |
| `image/quality-settings` | — | **Contradiction:** W8r (RA M7) / W8, or no preset values in prose (RB F15) | RA; RB | new row `LocalShadowViewsPerFrame`, `MaxShadowedLocalLights` {4,16,16,16} → {4,16,64,256}, `c_SectionVersion` 6 → 7, GI memory |
| `make/look` | — | W8r (RA M7) / its Graphics Quality section W8 (RB F15) | RA; RB | the presets follow `RendererQuality` |
| `light/measuring-light` (moved) | — | W8 for its GI views only; the GI views go to `indirect/gi-cascades` | RB F11 | `ProbeView.frag`, `GIField.slang` on rc-world |
| `light/fog` (or `indirect/fog`) | — | W8 if `volumetric` lands | RB F22; CU F13; RA M8 | tranche 3, no branch |
| `light/materials`, `light/material-data`, `make/materials` | — | W8 if `showcase-engine` lands | RB F22 | tranche 3 changes `MaterialData` |
| `editor/placement` | — | W8? (editor-ux) (CU) / none, written last and re-read (ED F18) | CU; ED | tranche 3: mesh ghost, live material preview |
| `light/units-exposure`, `light/clearcoat-transmission` | — | a note: rect-light units and the coat under rect lights, if area lights land | RB F15 | `AreaLightUnits` on the branch |
| `light/sun-shadows-2`, `image/exposure` | — | none; one sentence re-checked | RB F15; RA M7 | local lights' noise fixed on the branch; `AdaptationSeconds` also drives shadow fades |
| `assets/references`, `reference/assets` | — | re-read at the pin move | CF F11 | animation-graph touches `AssetDependencies` |
| `worlds/measuring`, `reference/worlds-runtime` | — | re-check at the pin move | ED F18 | perf-log columns of local-lights |
| `core/time`, `core/frame-loop`, `core/profiling`, `core/windows-events`, `core/layers-registries`, `core/conventions`, `world/systems`, `world/interpolation`, `world/projects-settings`, `gpu/shaders`, `engineering/cmake`, `engineering/generated-code`, `engineering/third-party`, `engineering/ci` | — | **Contradiction:** W8L (CF F12) / no mark, "new in 0.8.0" label, re-read `animation/root-motion` and `world/interpolation` (SM F21; ED F18) | CF; SM; ED | wave 8 step 0 and landing 1 work, already on main |
| `draw/gpu-driven`, `draw/occlusion`, `draw/render-scene`, `editor/scene-view`, `editor/status`, physics, audio, input, scripting, ui pages, `indirect/ibl`, `ao`, `probes`, `ssr` | — | none (confirmed) | RA; RB; SM; ED | `gpu/shaders`' Slang landed in step 0; the HZB fix is on main; local shadow culling goes to `light/local-shadows` |

---

## 4. "One home per concept": the corrected rows

**Contradiction** marks rows whose homes contradict each other. "Use" is the proposed use-level home column (BK2).

### 4.1 Changes to existing rows

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Fixed step, accumulator, time dilation | `core/time` (concept), `world/systems` (code) | `make/script-loop` | physics, scripting, animation, make | GM F4 |
| Interpolation of fixed steps | `world/interpolation`; CF F4 b: "the idea (interpolate vs extrapolate, one step of latency) `core/time`; Strata's interpolated set, roles and drawn transforms `world/interpolation`" | `make/characters-cameras` (`GetDrawnPosition` in `OnLateUpdate`, `ResetInterpolation`, platforms in `OnFixedUpdate`) | physics, draw, editor | CF F4; GM F4; CU |
| Prefabs | use: `make/prefabs`; data model, overrides and propagation (`EntityPrototype`, instantiation, `PrefabInstances`, `PrefabOverrides`): `world/prefabs` (or `assets/prefabs`, CU); keeping them exact while editing (`PrefabSync`, `UpdatePrefabOverrides` in `CommitEdit`, baselines, apply/revert as undo steps): `editor/prefab-instances` | — | — | CF F9 |
| Sub-scenes and the frame's work budget | **Contradiction:** `world/sub-scenes`, retitled "Loading scenes…" (CF F17) / `assets/sub-scenes` (CU) | — | worlds, assets | CF; CU |
| Upload queue and staging | **Contradiction:** `assets/uploads`, merged (RA M6) / mechanism `gpu/upload-queue` (`PlanStep`, `StagingPool`, transfer queue, `PrepareBackBuffer`); what is queued `assets/uploads` (CF further) | — | — | RA; CF |
| Residency, pins, eviction | `assets/residency` | `make/sound` (request in `OnCreate`), `make/levels-saves` (loading screens), `make/scripting-scene` (`RequestLoad`; `Instantiate` never waits) | draw, worlds, ui | CU; GM |
| Motion vectors | **Contradiction:** `draw/motion-vectors` (RB) / `image/motion-vectors` (CU) | — | image | RB F8; CU F4 |
| Shadow casters, light records (replaced) | sun caster selection (`FindShadowCasters`, sub-texel, `CanShadowView`), the cascade cache and its versions, cascade occlusion: `light/sun-shadows-1`; local shadow casters, view caches and culling: `light/local-shadows`. **Contradiction** on light records: `light/many-lights` (RA M5) / the mechanism (render-scene records and change logs, lights included) `draw/render-scene`, and what a record holds, the sun's choice and `LightData` `light/lights` (RB F16) | — | `draw/bounds-culling`, `draw/occlusion`, `draw/gpu-driven` | RA M5; RB F16 |
| BRDF table, split sum (split in two) | BRDF table (directional albedo, its derivation): `light/energy`; split sum (prefiltered radiance times the table): `indirect/ibl` | — | light; indirect | RB F1; CU |
| Sky as a light source | **Contradiction:** `light/sky` (RB) / `indirect/sky` (CU) | `make/lighting` | indirect; `light/sun` | RB F12; CU |
| Energy conservation, white furnace | `light/energy` | — | indirect | RB F1; CU |
| Debug views and measuring light (split) | **Contradiction:** RB F11: lighting, luminance, albedo and indirect views with their statistics and the sun-to-sky ratio `light/measuring-light`; shadows view `light/sun-shadows-1`; AO view `indirect/ao`; GI views `indirect/gi-cascades`; furnace `light/energy`; flicker meter `engineering/test-kinds`; look-dev `engineering/look-dev`. RA m3: lighting views (lighting, ao, indirect, luminance, albedo, shadows, voxels) `indirect/measuring-light`; drawing views, the mechanism `gpu/debug-drawing`; how to read each drawing view `draw/lod`, `assets/mip-streaming`, `draw/motion-vectors`. CU: `light/measuring` | `make/lighting` (`luminance`, `albedo`), `make/materials` | every rendering page | RB; RA; CU; GM |
| Depth of field | `image/depth-of-field` | — | — | RA m1 |
| Text: fonts, shaping, SDF | `gpu/text` (fonts, `ShapeText` layout, atlas, SDF) | `make/ui` (`TextComponent`) | `ui/text` (how rects, sizes and overflow modes drive `ShapeText`); the editor uses ImGui's own atlas, its font loading homed in `editor/design-system` | RA m8; ED |
| Skinning | math `animation/skinning`; GPU side **Contradiction:** `draw/skinned` (RA) / `animation/skinned-rendering` (CU) | — | — | RA M9; CU |
| Simulated input | **Contradiction:** device and merge rules `input/simulated`; holds in fixed steps, `input.sequence`, `input.click` `editor/stepping` (SM F3) / `input/simulated` holds `input.sequence` (CU F6) | `make/automated-playtests` | editor, automation | SM; CU |
| Stepping a paused game | `editor/stepping` | `make/play-test-debug` | `core/time` says one sentence; input | GM; CU |
| Command scripts, record and replay (split) | activity journal, command origins, replay export (`BuildReplayScript`), agent presence: `editor/journal`; command scripts (`expect`, `bind`/`$ref`, `until`) and `editor.batch`: `editor/command-scripts`; the Activity panel's drawing: `editor/instrument-panels` | `make/automated-playtests` | automation, make | ED F3; CU |
| Activity journal | `editor/journal` (ED); was `automation/journal` | `make/with-an-agent` (GM) / `make/ai-agent` (ED) | editor | ED; GM |
| Launcher, templates, samples | use: `start/first-game`, `make/samples`; code: `editor/projects` (model), `editor/launcher-dialogs` (UI); project pictures: `editor/thumbnails` | — | — | ED F7 |
| "Module" and "layer" (two meanings each) | `core/map`, extended to "registry" and "service" | — | — | CF F20 |

### 4.2 Rows to add

**Programming, mathematics, foundations**

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Programming from zero | `basics/programming` (CU) / `basics/programming-1..3` (BG) | — | `make/cpp-for-scripts`, `basics/cpp` | BG 1; CU |
| The C++ of scripts (classes, override, headers, `ST_SCRIPT_CLASS`) | `make/cpp-for-scripts` | — | `basics/cpp` extends it, never repeats it | CU |
| The C++ of the engine (ownership, RAII, move, templates, lambdas) | `basics/cpp` | — | `core/conventions` (Strata's rules only) | CU |
| Floating point, precision, float determinism | `basics/numbers` (CU, ED) / `basics/bytes` (BG) | — | `draw/mirrors-camera-relative`, `worlds/why-streaming` (home of the 20 km limit, ED), `image/pre-exposure`, `engineering/flags-portability` | CU; ED F12; BG |
| FMA contraction and floating-point determinism | `engineering/flags-portability` | — | `core/math`, physics | CF F19 |
| Logarithms and EV stops; degrees and radians | `basics/math-numbers` | — | light, audio (decibels), make | BG 3 |
| Vectors for game makers | `basics/math-vectors` | — | `make/transforms-units` | BG 10 |
| Rotations at the user level | `make/transforms-units`; the math `basics/math-rotations` | — | — | BG 10 |
| Axes, handedness, units, matrix order | `basics/math-matrices` | `make/transforms-units` | `gpu/coordinates` (Strata's API conventions), `core/math`, `reference/notation` | CU |
| Projections and reversed Z | math: `basics/math-vectors` (CF, RA) / `basics/math-projection` (CU); Strata's conventions and depth precision: `gpu/coordinates`; the code (`PerspectiveReverseZ*`, `Ray::FromNDC`): `core/math` | — | `draw/bounds-culling` | CF F7; RA M16; CU |
| Frustum and AABB tests | `draw/bounds-culling` (plane extraction, positive vertex, `AABB::Transformed`); CU: the math in `basics/math-geometry` | — | `core/math` (the types only) | CF F7; RA M16; CU |
| Sampling, aliasing, filtering, noise; sampling patterns (blue noise, Vogel, Poisson, IGN, ordered dither) | **Contradiction:** `basics/signals` (RB, CU; BG `basics/sampling`) / "pixels as samples and the kinds of aliasing" in `gpu/how-a-gpu-frame-works` or `basics/gpu` (RA m4) | — | `assets/textures`, `image/spatial-aa`, `image/taa`, `light/sun-shadows-2`, `indirect/ao`, `audio/sound-in-a-computer` | RB F7; CU; BG; RA |
| Spherical harmonics (the math) | `basics/math-light` | — | indirect | RB F23 |
| Handles instead of pointers; UUIDs | `world/ecs` | `make/assets` (one paragraph) | `assets/handles-meta` (asset handles only) | CU; CF F19 |
| Threads, races, atomics (general) | `basics/threads` | — | `core/jobs` (Strata's job system only) | CU |
| The threading model; the threads of a process | `core/jobs` (foundation figure 12) | — | — | CF F19 |
| Deterministic parallel work (ordered records, fixed chunks, serial publish) | `core/jobs` | `make/play-test-debug` | physics, animation, scripting, `input/simulated` | SM F3; CU (determinism of game time: `core/time`) |
| The frame map (one frame, start to finish) | `start/what-an-engine-is` | same | `core/frame-loop`, `make/script-loop`, `gpu/frame-tour` | CU |

**Engine architecture**

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Engine services and scene services; dependency inversion | **Contradiction:** engine services `core/engine-modules`, scene services `world/systems`, dependency inversion `core/layers-registries` (CF F19; SM F3) / "Scene services, registries, service locator" `core/layers-registries`, with `world/systems` covering scene services as one kind (CU) | — | physics, animation, audio, ui, scripting, assets | CF; SM; CU |
| Registries that open, accept and freeze | `core/layers-registries` (`world/reflection` covers only `ComponentRegistry`'s builder) | — | assets registries | CF F19 |
| Topological sort (Kahn) | `core/engine-modules` (`world/systems` covers only "built from the back") | — | — | CF F19 |
| Layer table, optional modules (`ST_WITH_*`), no tooling in games | rules, why and tests: `core/layers-registries`; the CMake (`strata_add_layer_libraries`, link-closure walk, linker map, `LayerLibraries.json`): `engineering/cmake` | — | scripting, `worlds/export` | CF F5 |
| Atomic writes, private files, TOCTOU | **Contradiction:** `core/files` (CF F14, F19) / `core/platform` (ED F6) | — | `assets/importing`, `assets/robustness`, `editor/saving`, `engineering/generated-code`, `automation/sessions` | CF; ED |
| Shared libraries and ABIs | `scripting/shared-libraries` | `make/script-builds` (what a module is) | `core/platform` | CU |
| Testing (kinds, why, doctest) | **Contradiction:** `core/testing` (CU) / `engineering/testing` (concept) + `engineering/test-program` (the program) (CF) | — | every internals page, `engineering/*` | CU F5; CF F15 |
| Writing a GPU test (shared `GPUContext`, error count, pixel readback) | `gpu/first-triangle` | — | `engineering/test-kinds`, `image/tutorial-post-effect` | RA M13 |
| Corruption sweeps and fuzzing | `engineering/test-program` | — | `assets/robustness` | CF F19 |
| Measuring: method, percentiles, self time, "CPU, GPU or capped" | **Contradiction:** `core/profiling` (CU; CF F19 for percentiles) / `engineering/measuring` (CF F22) | `make/big-scenes-fast` | `engineering/perf-lab` (the lab only), `physics/tuning`, `worlds/measuring` | CU; CF |
| Debugging (debugger, logs, asserts, crash dumps) | `core/debugging` | `make/play-test-debug` | `scripting/crash-containment`, `gpu/debugging` | CU |
| Shader build | writing and registering a shader, the dialect and its checks: `gpu/shaders`; the CMake custom commands, `StrataShaderTool`'s SPIR-V patch, the generated registry: `engineering/generated-code`; Slang's pinned download: `engineering/third-party`; the CI shader steps: `engineering/ci` | — | each links the others in one sentence | CF F6 |
| Hot reload | `scripting/hot-reload` | `make/first-script` | `assets/importing` (asset hot reload is its own row) | CU; CF F20 |

**Scenes, assets, export**

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Prepared loads (`PrepareSystems`, the `Preparing` state, `PrepareLoadedScene`) | **Contradiction:** `world/sub-scenes` retitled "Loading scenes…" (CF F17) / `world/serialization` (the loader's states) with `worlds/physics-scripts` showing the World hook (ED F6) / `assets/scene-documents` (CU) | — | — | CF; ED; CU |
| Loading scenes and scene switches | `worlds/runtime`; load progress and prefetch: `assets/references` | `make/levels-saves` | — | ED F6 |
| Export | the pack (format, planning, pruning, `AlwaysInclude`, patches, cooked documents): `assets/packs-export`; the export as a whole (`GameExport`, state machine, up-front checks, world cooking, what the folder holds): `worlds/export`; manifest and identity: `worlds/game-identity` | `make/export` | `world/projects-settings` | CF F8; ED F6, F8; CU |
| Cooked scenes (STSC) | **Contradiction:** format and validation `world/serialization`, when and why the export cooks `assets/packs-export` (CF F8) / cooked documents under `assets/packs-export` (ED F6) | — | — | CF; ED |
| Physics capacity, growth limit, `Reserve`, sliced building, parking | `physics/scale-streaming` (or `physics/capacity`, CU) | — | `worlds/physics-scripts` (what a world reserves, `MaxBodiesInRadius`, the cook, prefetch before teleport) | SM F7; ED F6; CU F6 |
| The camera (`CameraComponent`, projection, Primary, physical fields) | `gpu/coordinates` | `make/look`, `make/characters-cameras` | `image/exposure`, `image/depth-of-field`, `editor/camera-viewport` | CU; CF further |
| What a subsystem does not do | that subsystem's page (`animation/limits`, `indirect/gi-limits`, or a section) | same | `appendix/not-in-strata` indexes them | CU F19 |
| Project folder and files | `make/project-files` | same | `world/projects-settings` | GM F4, F19 |
| Autosave and recovery, undo of asset deletes | `editor/recovery`, `editor/trash-references` | **Contradiction:** `make/editor-tour` (GM F4) / `make/undo-save-recover` (ED F9) | — | GM; ED |

**Rendering**

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Compute shaders, dispatches, UAV barriers, atomics | **Contradiction:** `gpu/compute` (RA M1) / `gpu/shaders` retitled, barriers in `gpu/resources-lifetimes` (CU) | — | draw, light, indirect, image | RA; CU |
| Light units, EV100, the camera exposure model | **Contradiction:** `light/units-exposure` (RA M4; CU) / photometric units, conversions and reference values `light/units-exposure`, camera exposure, EV100, metering and the key `image/exposure` (RB F6) | `make/lighting` | `image/exposure`, `make/look` | RA; RB; CU |
| Metering, adaptation, exposure key | `image/exposure` | — | `light/units-exposure` | RA; RB; CU |
| Pre-exposure | `image/pre-exposure` (the mechanism: readbacks, epochs, settling, TAA rescale); one paragraph on why in `light/units-exposure` | — | light, `indirect/probes`, `indirect/ssr` | RA; RB; CU |
| HDR target, half-float limits, `SanitizeHDR` | **Contradiction:** `image/why-post`, with the idea in `basics/color` (RA M4; CU) / half-float range and subnormals `basics/color`, `SanitizeHDR` `light/brdf`, the first HDR writer (RB F6) | `make/look` | light, `image/lens-effects` | RA; RB; CU |
| The sRGB transfer function | `basics/color` | — | `image/encoding` (quantization, dither), `assets/textures` (sRGB textures) | RA M4 |
| Radiometry in use, the reflection equation, microfacet theory | **Contradiction:** `light/reflectance` (RB F5) / the reflection equation in `light/brdf` (CU) | — | `indirect/problem` (the full rendering equation) | RB; CU |
| Fresnel, F0 from IOR | `light/reflectance` (the physics), the IOR field in `light/materials` | — | indirect | RB F4 |
| Specular anti-aliasing, the derivative rule | **Contradiction:** `light/brdf` (RB F4) / `light/energy` (CU) | — | indirect, `draw/gpu-driven` | RB; CU |
| Sized sources (lobe widening) | `light/area-lights` (retitled) | — | `light/lights`, `indirect/probes` (bakes draw no highlights) | RB F4 |
| Horizon fade | `indirect/ibl` (it fades image light only) | — | `light/brdf` | RB F4 |
| The forward shader's anatomy and shading order | `light/brdf` | — | indirect, image | RB F9 |
| Forward, deferred, visibility buffer; the prepass, `EQUAL` and invariant positions | `gpu/frame-tour` | — | `light/many-lights` (owns tiled vs clustered), `gpu/shaders`, `draw/lod`, `draw/skinned`, `draw/motion-vectors` | RA M16; RB F9 |
| The indirect seam, the fallback stack | `indirect/seam` | — | probes, ssr, gi | RB F10 |
| Participating media: extinction, transmittance, phase functions | `light/atmosphere` | — | fog, `light/clearcoat-transmission` (Beer's law), `indirect/gi-cascades` (the march) | RB F12 |
| Normal maps and tangent space | `light/materials` (concept), `light/material-data` (decode) | — | `assets/textures` (BC5), `draw/mirrors-camera-relative` (handedness) | RB F13 |
| Mirrored transforms; float precision and camera-relative rendering | `draw/mirrors-camera-relative` | — | `gpu/coordinates` (states the CCW convention only), `worlds/*`, `make/large-worlds` | RA M16; ED F12 |
| Geometry pool | `gpu/geometry-pool` | — | `draw/batching` | RA M16 |
| Pipelines and the `PipelineKey` cache | `gpu/binding` (retitled) | — | `gpu/frame-tour`, `draw/batching` | RA M16 |
| Render-scene change logs | `draw/render-scene` | — | `draw/render-scene-gpu`, shadow caches | RA M16; RB F16 |
| GPU timestamps and stages | `gpu/readback-timing` | — | `core/profiling` (shows them) | RA M16 |
| Picking (async entity-ID readback) and gizmos (`TransformDrag`) | `editor/scene-view` | — | `gpu/readback-timing` (the one-pixel readback); `editor/undo` names `TransformDrag` as a merge-key example | RA M16; ED F5 |
| Transparency (blending, premultiplied alpha, the transparent pass) | **Contradiction:** `draw/batching` (RA M16) / `light/clearcoat-transmission` (retitled), with sorting in `draw/batching` (RB F18) | — | `image/taa` (reactive mask), `indirect/ssr` | RA; RB |
| Scene-color copies | `light/clearcoat-transmission` | — | `indirect/ssr` | RB F23 |
| Jitter on the frame's camera copy only | `image/taa` | — | `gpu/frame-tour`, `gpu/debug-drawing`, shadows | RA M16 |
| Players' graphics options | mechanism `image/quality-settings` | **Contradiction:** `make/levels-saves` (RA M16) / `make/quality` (GM F4, F23) | `make/look`, the gameplay pages | RA; GM |
| Quality rows of a feature | the feature's page (its row and cost) | `make/look` | `image/quality-settings` (presets, traits, players' options) | CU |
| Screen fraction (`GetScreenFraction`) | `draw/bounds-culling` ("How big does it look?") | — | `draw/lod`, `draw/asset-requests`, `assets/mip-streaming` | RA m5 |
| Preview lighting | `light/lights` (code) | `make/lighting` | indirect | RB F23 |
| Sky presets, Extract and Remove Sun, `HDRSun` | `light/sky` (`assets/texture-cooking` gives the setting) | `make/lighting` | `indirect/ibl` | RB F23; CF F19 |
| The default template's lighting | `make/lighting` | same | `editor/projects` (was `worlds/templates`) | RB F23 |
| Overlay passes (`SceneOverlayRegistry`) | `gpu/debug-drawing` | — | `ui/drawing` | SM F3 |
| Posed bounds; reach | `draw/skinned`; `animation/culling` | — | — | SM F3 |

**Simulation, gameplay, editor**

| Concept | Home | Use | Others link | Critics |
| --- | --- | --- | --- | --- |
| Script lifecycle and callbacks | `make/script-loop` | same | `scripting/script-system` (the code) | SM F3; CU |
| Contacts and triggers reaching scripts | `physics/contacts-triggers` | — | `scripting/script-system` | SM F3 |
| Play and Simulate modes | `editor/play-mode` | `make/play-test-debug` | `world/systems`, physics, audio, scripting | SM F3 |
| Input ownership: enabled flag, pointer, keyboard and binding capture | **Contradiction:** `input/devices-state`, with `editor/game-view` linking (SM F3) / the Game view's resolutions, letterboxing and input ownership `editor/game-view` (ED F5) | — | `ui/input` | SM; ED |
| UI actions and menu key repeat | `input/actions` | — | `ui/input` | SM F3 |
| Immediate vs retained UI | **Contradiction:** `ui/what-game-ui-does`, with `editor/immediate-mode` merged into `editor/imgui` (CU) / `editor/immediate-mode` only compares retained and immediate UIs (ED F5) | — | `editor-ui/imgui` | CU; ED |
| What an editor is, and why it is not the game | `editor/program` | — | `editor/immediate-mode` | ED F5 |
| Commands are the API (three clients, one registry) | `editor/commands` | `make/editor-tour` | automation, every tutorial | ED F5; CU |
| Editor camera (controls and math), per-scene cameras, viewport settings | `editor/camera-viewport` | — | `editor/scene-view` | ED F5 |
| The Game view: running copy, game shell, edits while playing | `editor/play-mode` | — | `editor/game-view` | ED F5 |
| No silent data loss: guards, `AfterSaves`, `ResetScene` | `editor/saving`; asking the person (modals, re-ask, `DrawDiscardQuestion`) `editor/shell` | — | — | ED F5 |
| Hierarchy and asset views, clipping, multi-select; notifications | `editor/lists`; `editor/status` (model and drawing) | — | — | ED F5 |

### 4.3 Design decisions and their homes

| Decision | Homes proposed | Critics |
| --- | --- | --- |
| Nothing may need history (TAA) to look right | **Contradiction:** `image/taa`, with the Checkerboard exception and a link to `indirect/ssr` (RA m6) / `light/sun-shadows-2`, its first use, with `indirect/ao` and `image/taa` linking (RB F19) / a section "Rules every pass keeps" in `gpu/frame-tour`, restated in `image/taa` (CU) | RA; RB; CU |
| Never render below native resolution | `image/quality-settings` (agreed) | RA; RB; CU |
| Global illumination traces world data, never the screen | **Contradiction:** `indirect/problem` (RA; CU) / `indirect/gi-voxels` (RB) | RA; RB; CU |
| A feature that is off is invisible bit for bit and costs nothing | **Contradiction:** `gpu/frame-tour` (RA; CU) / `indirect/seam` (the `x * 1 + 0` join, dummy SRVs) (RB) | RA; RB; CU |
| Light in real units with pre-exposure | `light/units-exposure` (RA; CU); RB: units `light/units-exposure`, the mechanism `image/pre-exposure` | RA; RB; CU |
| Game time counts fixed steps, never frames | `core/time` (agreed) | CF; RA; CU |
| Parallel work is deterministic | `core/jobs` (agreed; the parallel writer's deterministic bytes in `world/serialization`, CF) | CF; RA; SM; CU |
| Trade-offs are measured on the reference machine | **Contradiction:** `engineering/perf-lab` (RA) / new `engineering/measuring` (CF) / `core/profiling` (CU) | RA; CF; CU |

---

## 5. Engine facts the critics checked (at `822a7a46` unless a branch is named)

**Assets, core, platform**

| Feature | Answer | Evidence | Critic |
| --- | --- | --- | --- |
| OBJ and FBX import | absent; only glTF models | `Strata/src/Strata/Asset/AssetImporters.cpp:159-177`; `Docs/Releases/0.7.0.md:414` | CF |
| BC6H | absent (HDR textures are RGBA16F) | `Docs/Releases/0.7.0.md:403` | CF |
| Mesh streaming | absent (only textures register partial loads); per-LOD mesh streaming is "later" | `Renderer/RendererRegistration.cpp:93`; `Docs/Roadmap.md:1691` | CF; RA |
| Virtual texturing, sparse residency | absent | none in `Strata/src` (grep `sparseBinding`: none) | CF; RA |
| Shader asset type, material graphs | absent; shaders are embedded at build time | `Asset/AssetTypes.h:14-31`; `strata_add_shaders` | CF |
| Mobile, console, web | absent | `Core/PlatformDetection.h` (`#error`) | CF |
| Work stealing, fibers, task graph | absent ("later") | `Docs/Roadmap.md:1705` | CF |
| Run-time engine plugins | absent; modules are compile-time (`ST_WITH_*`) | — | CF |
| Leaving scripting out of a build | absent | `Docs/Releases/0.7.0.md:404` | CF |
| Prefab edit mode | absent | `Docs/Releases/0.7.0.md:380, 414` | CF; ED |
| Nested prefabs and variants | absent (the book's claim is true) | `Scene/PrefabInstances.h:129-130` (`StripLinks`, `MakeTemplate`); `StrataEditor/src/Editor/EditorAssetCommands.cpp:1185, 1216` | CF; ED |
| Fixed-step interpolation (`physics-timing`) | present (landed in wave 8 landing 1) | `Scene/TransformInterpolation.h`, `SceneInterpolation.cpp`, `ProjectSceneTiming.h/.cpp`; `Docs/Roadmap.md:639-642` | SM; CF |
| Test shards | 13 in `CoreShards.json` (DG and skill say 12) | `StrataTests/CoreShards.json` | CF |
| glTF importer version | 11 (an inventory says 9) | `GltfImporter.h:39` | SM |

**Rendering**

| Feature | Answer | Evidence | Critic |
| --- | --- | --- | --- |
| Particles, decals | absent | no match in `Strata/src` or `Strata/shaders` | RA; RB |
| Terrain | absent as an engine feature; sample terrains are generated meshes | comments only in `SpatialIndex.h`, `RenderScene.h`, `Mesh.cpp`, `WorldAsset.h`; `Tools/Generate*Terrain.py` | RA; RB |
| Water | absent; only a material value | `Material.h:59` (IOR 1.33) | RB |
| HLOD, origin rebasing | absent ("later") | `Docs/Roadmap.md` 1690-1694, 1706; `Docs/Releases/0.7.0.md:386` | RA; ED |
| MSAA | absent; targets with `sampleCount != 1` are refused | `SceneRenderer.cpp:2767`; `Docs/Roadmap.md` 944, 1670 | RA; RB |
| HDR display output | absent; only `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` | `VulkanGraphicsDevice.cpp:1131-1136` | RA; RB |
| Rendering below native, dynamic resolution, upscalers | absent by decision | `Docs/Roadmap.md:1642`, 944-945 | RA; RB |
| Post-process volumes | absent; the first active `PostProcessComponent` wins | `SceneRenderer.cpp:1447-1455` | RA |
| Hardware ray tracing, mesh shaders, meshlets, render graph | absent; passes ordered by hand in `RenderFrame` | grep `rayQuery`, `AccelerationStructure`, `Meshlet`, `RenderGraph`, `FrameGraph`: none | RA |
| Complex-script shaping, CFF fonts | absent; `FontValidation` rejects CFF | render-core 1.14 | RA |
| Compute and dual-quaternion skinning | absent | `Docs/Roadmap.md:675`; no "dual quaternion" in `Strata/src` or shaders | RA; SM |
| Volumetric fog, light shafts, fog volumes | absent; tranche 3, no branch | `RendererComponents.h:126-129`; `Scene.slang:13-14` (SRV 34, 36 reserved); `Docs/Roadmap.md:948`; Wave8 plan §4 | RA; RB |
| Debug drawing from scripts | absent | no host function in `StrataScriptCore/Include/StrataScript/*.h` | RA |
| Area lights | absent on main; the branch `agent/wave8-area-lights` has LTC tables and CPU math only; no wave 8 stream; Roadmap lists them after wave 8 | `AreaLights.h` (branch); `Docs/Plans/Wave8/plan.md` §4; `Docs/Roadmap.md` ~1672 | RB; SM |
| Lightmaps, baked GI | absent; probes are the only bake | no `Lightmap` in the engine | RB |
| Subsurface scattering | absent; the owner's item 7 is not in wave 8 | no `Subsurface`; `Docs/Plans/Wave8/owner_feedback.md` | RB |
| Sheen, anisotropy, iridescence, specular and thickness maps, EXR import | absent | `Docs/Roadmap.md:949` | RB |
| Run-time probe capture; SSR of and through transparent surfaces | absent | `Docs/Roadmap.md` 940-943, 947-948 | RB |
| A second shadowed sun; virtual shadow maps | absent | `Docs/Roadmap.md` 949-950, 1670; `CollectLights` takes one sun | RB |
| GI from local lights, moving or skinned objects | absent (below the GI spec's cut) | render-indirect 1.8, spec D18 | RB |
| Debug views | 11: streaming, lod, mip, motion, shadows, lighting, ao, indirect, luminance, albedo, voxels | `EditorViewportCommands.cpp:1263-1270` | RA |
| Dither switch | code only (`DitherOutput`) | `research/captures.md` 660; `SceneRenderer.h` 142-254 | RA; PL |
| Medium's Checkerboard SSR needs TAA | present (an exception to "no history") | `Docs/Roadmap.md` 951-953 | RA |
| Forward shader uses the BRDF table and `SpecularEnergy` for direct light | present | `Strata/shaders/Scene/Forward.frag.slang:211-218` (coat 220-226); `GPUSceneLightingTests.cpp:958` | RB |
| Thumbnails force the CPU path; the cascade cache works on the GPU path only | present | `SceneRenderer.cpp:248-251`; `Docs/Roadmap.md` 675-677 | RA |
| `renderStats` keys | present | `EditorStateCommands.cpp:228-292` | RA |
| Working color space | scene-linear sRGB (Rec. 709) primaries | `PostProcessMath.h:62` | RB |
| `temporalFrames` without TAA; `globalIlluminationSettled` without GI | 0; true | `SceneRenderer.cpp:3045`; `SceneRenderer.h:676` | PL |
| Wave 8 local lights | new quality row `LocalShadowViewsPerFrame` (12, 12, 24, 48); `MaxShadowedLocalLights` {4,16,16,16} → {4,16,64,256}; `c_SectionVersion` 6 → 7; `SceneRendererSpecification::LocalShadowViewsPerFrame` removed; new `renderStats` keys; local shadow noise fixed; no change to light components or records | branch `agent/wave8-local-lights` (`RendererQuality.h/.cpp`, `SceneRenderer.h`, `LocalShadows.slang`, `EditorStateCommands.cpp`) | RA; RB |
| Wave 8 GI | the GI row's memory changes; SH probes, `ProbeView.frag`, `GIField.slang` | branch `agent/wave8-rc-world` | RA; RB |

**Physics, animation, audio, input, scripting, game UI**

| Feature | Answer | Evidence | Critic |
| --- | --- | --- | --- |
| Joints | absent | no `b3Create*Joint` in `Strata/src/Strata/Physics` | SM |
| Ragdolls, vehicles | absent | only a comment, `World/WorldComponents.h` 20 | SM |
| Shape sweeps | absent from the API; used only inside the character controller | `PhysicsWorld.cpp` 5413, 5435 (`b3World_CastRay`); `CharacterControllers.cpp` 373 (`b3World_CastMover`) | SM |
| Height-field and cylinder colliders | absent; Box, Sphere, Capsule, Mesh only | `PhysicsComponents.h` 44-68 | SM |
| Cloth, soft bodies, destruction | absent | none found | SM |
| Coordinate limit of bodies | 1e5 m | `c_MaxBodyCoordinate`, `PhysicsWorld.cpp` 73 | SM |
| Animation graph (Blend1D, masked layers, sync tracks, `.stanimator` 2) | absent at the pin; planned for tranche 2 of wave 8 | `Docs/Plans/Wave8/plan.md` §4.5 (729-770), 363, 386; `Docs/Roadmap.md` 1551, 1614-1626; `AnimationController.cpp` 516-539 (format 1 only); `git grep -i blend1d` finds nothing | SM; CF; ED; CU |
| IK | absent (wave 9) | — | SM |
| Morph targets | absent; weight channels skipped | `GltfImporter.cpp` 1031 | SM |
| Clip compression | absent (wave 9 "if measured to help") | `Docs/Roadmap.md` | SM |
| Audio buses, effects, reverb, HRTF | absent; only `ma_node_set_output_bus_volume` | `Strata/src/Strata/Audio`; `AudioVoice.cpp` 308 | SM |
| Audio streaming from disk | absent; streamed clips decode bytes held in memory | `AudioClip.h` 45-51; Release 0.3.0 line 197 | SM |
| Attenuation model per component | absent (always Inverse) | `AudioComponents.h` | SM |
| Touch | absent | no touch code in `Input/` or `Platform/GLFW` | SM |
| IME | game: committed text arrives, composition absent (GLFW 3.4 has no preedit); editor: composition supported, candidate list on Windows | `Input/Input.h` 148; `Strata/vendor/glfw/include/GLFW/glfw3.h`; `Strata/src/Strata/ImGui/ImGuiPlatform.h` 25-26, `ImGuiPlatform.cpp` 81 | SM; ED |
| Input modifiers, chords; force feedback | absent | `InputActionSet.h`; no rumble or haptic code | SM |
| Other script languages | absent (no `lua_`, `mono_`, CoreCLR) | — | SM |
| Script calls from other threads | absent ("Everything is single-threaded") | `ScriptABI.h` 25-26 | SM |
| Game UI components | 11 registered (gameui inventory says 12); input fields are one line; no localization | `GameUIComponents.cpp` 211-397 | SM |
| Lit world-space UI; hit tests respecting geometry | absent | gameui rule 24; `Docs/Roadmap.md` 708-709 | SM |
| `ST_SCRIPT_HOST_FUNCTIONS` | in the engine, not the SDK | `Scripting/ScriptHostAPI.cpp:3431`; host table `ScriptABI.h` from 312; callbacks 772-831; macros `Script.h` 852-857 | PL |

**Editor, automation, export, tools**

| Feature | Answer | Evidence | Critic |
| --- | --- | --- | --- |
| Network code | present for editor automation only, in a Tooling layer games never link | `StrataTests/Architecture/Layers.json` 99-102 | ED |
| Editing several scenes at once | absent (`scene.loadAdditive` is play mode only) | `EditorSceneCommands.cpp` 458-460 | ED |
| Panels torn out into windows | absent ("Single main viewport") | `ImGuiPlatform.h`; `Docs/Roadmap.md:1715` | ED |
| Editor extensions by a game project | absent; panels registered only by the editor | `EditorLayer.cpp` 350 | ED |
| Automating an exported game | absent | `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` | ED |
| Exports for another platform, macOS bundle, signing, crash reports | absent | `Docs/Releases/0.7.0.md` 411-412; `GameExport.h` 30 | ED |
| Bodies moving between world cells | absent | `Docs/Releases/0.7.0.md:387` | ED |
| Wave 8 editor lane (placement by ray, box ghost, frame-rate preferences, Performance pause) | present (landed in step 0) | `Docs/Roadmap.md:1564` | ED |
| Runtime perf-log columns of local shadows | present, from the local-lights stream | `GameRenderer.cpp` 178-200 | ED |
| Editor options | one array | `c_Arguments`, `EditorApplication.cpp` 63-82 | ED |
| Running an arbitrary command from the editor's UI | absent | menus `EditorLayer.cpp` L1460-1606; Activity panel `ActivityPanel.cpp` L372-397 | GM |
| Creating an animation controller from the UI | absent; command only (`animation.createController`) | `EditorAnimationCommands.cpp` L153; `ContentBrowserPanel.cpp` L568-578 | GM |
| Project templates | `empty` and `basic3d` only; Basic 3D's 20×20 ground, top at y = 0 | `ProjectTemplates.cpp` L49-95; `EditorAssetCommands.cpp:281` | GM; PL |
| Script build without VS's C++ workload | refused with a message | `ScriptToolchain.cpp` L272-276 | GM |
| Export ships `ThirdPartyNotices.md` | present | `GameExport.cpp` L32, L200-201, L707 | GM |
| `entity.setProperty` | absent; properties are set with `component.set`; entity ids are hex only | `Commands/EntityCommands.cpp:721-729`; `CommandUtils.cpp:71-74` | PL |
| `AntiAliasing = None` | absent; `AntiAliasing` is a bool, `AntiAliasingMethod` is FXAA, TAA or Morphological | `Renderer/RendererComponents.cpp:490-491` | PL |
| Shot `Showcase/Dusk` | absent; shots are named like `showcase.shot6`; Dusk is a station of `GenerateShowcaseTerrain.py`; `lookdev.thin` exists | `STATIONS` 175-178; `Shots.json` | PL |
| `Scene::OnUpdate` | absent; `OnUpdateRuntime` (2199, 156 lines) and `OnUpdateEditor` (2355) | `Scene.cpp` | PL |
| Headless editor without a GPU | `--headless` keeps the GPU; only `--no-gpu` runs without a device; the default window is 1600×900 | `EditorApplication.cpp:70-72` | PL |
| Commit of a build | `--version` prints only "Strata Editor 0.7.0"; `editor.status` reports `engineCommit` (12 hex, no dirty flag) | `EditorApplication.cpp:269`; `CMake/StrataVersionCommit.cmake` | PL |
| A package of `822a7a46` | absent (releases stop at v0.7.0) | GitHub releases | PL |
| Script SDK of a dev build | the live engine tree | `ScriptToolchain.cpp:712`; `ScriptProject.cpp:223` | PL |
| Vendor libraries | gitlinks (mode 160000) | `git ls-tree 822a7a46 Strata/vendor/` | PL |
| Command-script keys; `expect` operators; `log.read` filter | only `command`, `parameters`, `expect`, `bind`, `until`; only `equals`, `min`, `max`; no text filter | `EditorCommandRunner.cpp:431-433`; `EditorCommandRunner.h:79-81`; `EditorStateCommands.cpp:985-992` | PL |
| Result schema of commands; component defaults and inactive reasons | absent from `editor.commands` and `component.list` | `EditorCommands.h:87-106`; `PropertyJson.cpp:488-517`; `EntityCommands.cpp:619-626` | PL |
| Importer versions | `return N;` in each importer | `TextureImporter.h:89`, `GltfImporter.h:39`, `ColorLookupImporter.h:49`, `AssetImporters.cpp` 47, 92, 146 | PL |
| Setting players' graphics options by command | absent (only `graphics.resetPlayerOptions`) | — | PL |
| `editor.showPanel`, `editor.showDialog` headless | fail | `EditorLayer.cpp` 177-328 | PL |
| UI labels | string literals (`BeginMenu("File")`, `"Add Component"`) | `EditorLayer.cpp:1456`; `Panels/InspectorPanel.cpp:448`; `SceneHierarchyPanel.cpp:929` | PL |
| Number of registered commands | **discrepancy:** 151 (automation inventory), 153 (editor-core inventory), 154 (PL's count) | — | SO; ED; PL |
| Engine repository size at the pin | 134.7 MB, of which `Samples/` 107.3 MB; twelve 960×540 sample screenshots | `git ls-tree` | SO |
| Public repositories | `2042Third/GameEngine` and `2042Third/strata-engine-docs` are public | GitHub API | SO |

---

## 6. Questions only the owner can answer

1. **License** of the book's text and pictures (already open in README.md).
2. **Where the site lives.** The real origin for `DOCS_SITE`: today it is `https://example.com`, and SO 7 makes a release
   build fail on that default. Which server it is (nginx or Caddy, version, the other `location` blocks, RAM), so that
   the deploy blocks fit. Whether to copy files or run a container.
3. **Picture storage.** PL proposes committed lossless PNG originals, and SO estimates about 300 MB for the first take
   (GitHub recommends under 1 GB; LFS is 10 GiB on the free plan). Is that growth in the docs repository acceptable, or
   should there be a separate media repository (README's alternative)?
4. **0.8.0's scope**, if the engine's wave 8 plan does not already fix it. Is 0.8.0 cut after landing 2 (animation graph,
   local lights) or after landing 1? Do `volumetric`, `showcase-engine` or `editor-ux` land? Are rect area lights in
   0.8.0 at all, given that no wave 8 stream schedules them?
5. **Engine additions for captures.** May the capture commands and debug views (PI14) ship as a v0.8.1 point release from
   a `release/0.8` branch, made by engine agents under the engine's review, with the book pinned to v0.8.1?
6. **The engine on the owner's machine in phase A.** May one Release build of `822a7a46` be made in a separate clone, and
   may docs tools run `--no-gpu` editors and script builds under PerfLock while wave 8's agents work (PI1)?
7. **Real beginners.** Before phase B, can the owner have two or three real beginners do `start/install` →
   `start/first-game` → `make/first-script`, and note where they stopped (BG 22)?
8. **The UI walk.** Who walks the UI path of each G tutorial once in a windowed editor: the owner, or an agent that
   controls the owner's screen (GM F13; PL M10)?
9. **"Before" pictures.** May they be taken from the LookDev baselines on the reference machine (PL m5)?
