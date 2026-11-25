# Critique: completeness against the survey, simulation and gameplay areas

Key: `complete-simulation`. Lens: completeness of the plan against the inventories `physics.md`, `animation.md`,
`audio-input.md`, `scripting.md` and `gameui.md` (each read in full), with the engine at `822a7a46` (read-only) as the
arbiter where the inventories are unsure. Line numbers are those of the plan files as they stand.

## Verdict

The five areas are mostly well covered: almost every feature group of the five inventories has a plausible page, and the
part orders follow the inventories' teaching orders. Three things would hurt the book:

1. **The animation part is planned on the 0.7.0 model, but 0.8.0 is planned to ship the animation graph.** Wave 8's
   plan puts `animation-graph` first in tranche 2, and 0.8.0 is cut after landing 2. No animation page is marked W8, and
   the "does not do" list names blend trees and layers, which that stream adds.
2. **The writing waves break the plan's own prerequisite rule** for `ui`, `animation` and `input`. They are written in
   wave 4, before `gpu`/`draw` (wave 5) and `editor` (wave 6), and those parts hold their prerequisites.
3. **Concepts that all five areas share have no row in "one home per concept"**: scene and engine services,
   deterministic parallel work, input ownership and capture, Play versus Simulate, and the script lifecycle. Several
   pages are kinds or sizes that cannot hold what was allocated to them: `scripting/host-api`, `animation/editor`,
   `make/ui`, `physics/world-step` and `input/devices-state`.

Change first: mark the animation pages W8 (conditionally) and fix the "does not do" list. That is the one change without
which a part of the book is wrong for the release it targets.

---

## Findings, most severe first

### F1 (blocker): the animation part is not marked W8, but 0.8.0 is planned to change it

- **Where**: `outline-3.md` rows 85-97 (Part 12) carry no W8 mark. `outline-1.md` row 49 (`make/animation`) and row 60
  (`make/project-platformer`), and `outline-4.md` row 139 (`reference/animation`), have none either. `book.md` line 96
  says Strata has no "blend trees, animation layers". `README.md` line 28 and `process.md` line 86 name only local
  lights, area lights and GI as W8 work. `outline-3.md` row 97 (`animation/limits`) is framed around "the planned
  animation graph".
- **Evidence**:
  - `Docs/Plans/Wave8/plan.md` §4.5 (lines 729-770): the stream `animation-graph` adds pose tasks (Sample, Blend,
    MaskedBlend), sync tracks, a graph of Clip, Blend1D, Layer, BoneMask, StateMachine and Transition nodes (sync, time
    match, easing, root motion modes), sampled events with weights, `.stanimator` version 2, `animation.info` with live
    node weights, and extended Inspector and Asset tab tables. It also changes the Third-Person robot to "Idle, Walk, Run
    in a Blend1D synced on `Footstep`; Wave as an upper-body layer". Its cut line never cuts "sync, Blend1D, the masked
    layer, agent commands or the Third-Person proof".
  - The tranche table (plan.md line 363) puts `animation-graph` first in tranche 2, ending with landing 2. Section 7,
    steps 4 and 13 (lines 970, 991), release 0.8.0 after landing 2. Only "if the wave has to end early" is 0.8.0 cut
    from landing 1 (line 377-378).
  - At `822a7a46` none of it is in the tree: `Strata/src/Strata/Animation/` has no Blend1D, BoneMask or SyncTrack.
    `AnimationController.cpp` 516-539 reads and writes format version 1 only.
  - The animation inventory §1.16 says the same: "Wave 8 tranche 2 plans `animation-graph` ... None of it is in the tree".
- **Proposal**:
  - Mark these pages `W8 (animation-graph)`: `animation/state-machines`, `animation/blending`, `animation/time-events`
    (sync tracks, weighted events), `animation/root-motion` (transition root-motion modes), `animation/system` (graph
    nodes in jobs), `animation/culling` (`WhenVisible` "runs nodes and skips tasks"), `animation/editor`,
    `animation/limits`, `make/animation`, `make/project-platformer`, `make/samples` (the robot's description) and
    `reference/animation`.
  - Add two conditional rows after `animation/blending`:
    - `animation/graph` | The animation graph: nodes, parameters and `.stanimator` 2 | I | L | new · W8
    - `animation/sync-layers` | Sync tracks, blend spaces and masked layers | I | L | new · W8
  - Change `book.md` line 96 to: "blend trees and animation layers (until 0.8.0's animation graph: see
    `animation/graph`), blend spaces in two dimensions, IK, additive clips, morph targets, clip compression". Its final
    wording waits for the tag.
  - Add "the animation graph" to `README.md` decision 5 and to `process.md` step 7.
  - Add a rule to `process.md` phase B, step 6: "if 0.8.0 is cut from landing 1, the W8 (animation-graph) marks are
    removed and the two new pages are dropped".
  - The pages that do not change can be written now: `animation/problem`, `skeletons`, `clips`, `skinning` and
    `importing`.

### F2 (major): the writing waves put `ui`, `animation` and `input` pages before the parts that hold their prerequisites

- **Where**: `process.md` lines 75-80 (waves 4, 5 and 6). The rule at line 74 says "in an order where prerequisites are
  written before the pages that need them".
- **Evidence**:
  - `outline-4.md` line 22 lists `gpu/text` as a prerequisite of Part 16, but `gpu` is wave 5 and `ui` is wave 4.
  - `ui/drawing` needs bindless binding (`gpu/binding`), reversed-Z (`gpu/coordinates`) and camera-relative transforms
    (`draw/mirrors-camera-relative`). See gameui inventory §1.7 (`UploadTransforms`, texture slot table) and the
    prerequisites of its chapter 7.
  - `animation/skinning` shares its home with `draw/skinned` (`book.md` line 74).
  - `animation/culling` needs the renderer's visibility report and posed bounds. See animation inventory §1.10
    (`SceneRendererExtraction.cpp` 286-309) and the prerequisites of its chapter 12 ("culling").
  - `input/simulated` covers `input.sequence`, holds counted in fixed steps and `input.click`. Those live in
    `StrataEditor/src/Editor/SimulatedInput.*`, `InputSequence.*` and `EditorInputCommands.cpp` (audio-input §1.10). They
    need `editor/commands` and `editor/stepping`, which are wave 6. The inventory's chapter 13 lists "editor command
    system" as a prerequisite.
  - `ui/testing` (`ui.create`, `ui.layout`, `ui.hitTest`) needs `editor/commands` (wave 6).
- **Proposal**: swap waves 4 and 5 (`gpu`, `draw` and the non-W8 rendering pages first, then `physics`, `animation`,
  `audio`, `input`, `ui`, `worlds`). Move `input/simulated` and `ui/testing` into wave 6, after `editor/stepping`.

### F3 (major): "one home per concept" lacks rows for concepts that all five areas teach

- **Where**: `book.md` lines 51-83.
- **Evidence**: each inventory has its own "concept to teach" for these. Without a row, five allocators will each teach
  them again:
  - **Scene services and engine services.** physics §1 (7 services), animation concept 20, audio concept A9 and
    `IAudioOutput`, scripting concept 16 ("teach once, then each subsystem chapter shows its script face") and §1.6,
    gameui §1.10. The scene-ecs inventory's chapter 4 includes "scene services" and foundation §1 has `EngineServices`.
    The word "service" appears nowhere in the plan.
  - **Deterministic parallel work.** This is a design decision named in `book.md` line 90, but no home is named for it.
    It is claimed by physics concept 20, character moves (`CharacterControllers.cpp` 928-999), animation concept 17 and
    scripting concept 20 (PCG32).
  - **Input ownership and capture.** The enabled flag, pointer capture, keyboard capture and binding capture are claimed
    by audio-input concept B6, gameui concept 17, `editor/game-view` ("input ownership") and `ui/input`.
  - **Play mode versus Simulate.** Physics runs in both modes. Scripts, animation and audio run in Play only (physics
    §1.4, animation §1.1, audio §1.4, scripting §1.4). Each inventory has a pitfall about it.
  - **Script lifecycle and callbacks.** This is `make/script-loop` (C). `scripting/script-system` implements it.
  - **Contact delivery to scripts.** Physics §1.6 (`DispatchCollisionEvents`) and scripting code #29
    (`ScriptSystem.cpp` 340-383: every Enter gets its Exit, normals flipped).
  - **UI actions and menu key repeat.** `UIActionState` lives in `Input/UIActions.*` (audio-input §1.9) but is used by
    gameui §1.9.
  - **The overlay registry.** `SceneOverlayRegistry` belongs to `gpu/debug-drawing`'s title, but gameui concept 14 also
    teaches it.
  - **Posed bounds versus reach.** Both `draw/skinned` and `animation/culling` need them.
  - **Simulated input.** The row at line 75 gives it all to `input/simulated`. But editor-core's chapter 10 ("Time in
    steps") also teaches "simulated input and `input.sequence` for deterministic tests", which is `editor/stepping`'s
    row at line 76.
- **Proposal**: add these rows (Concept | Home | Others link):
  - Scene services; engine services | `world/systems`; `core/engine-modules` | physics, animation, audio, ui, scripting
  - Deterministic parallel work (ordered records, fixed chunks, serial publish) | `core/jobs` | physics, animation, scripting
  - Input ownership: enabled, pointer, keyboard and binding capture | `input/devices-state` | ui/input, editor/game-view
  - Play and Simulate modes | `editor/play-mode` (use: `make/play-test-debug`) | world/systems, physics, audio, scripting
  - Script lifecycle and callbacks | `make/script-loop` | scripting/script-system (how it is implemented)
  - Contacts and triggers reaching scripts | `physics/contacts-triggers` | scripting/script-system
  - UI actions and menu repeat | `input/actions` | ui/input
  - Overlay passes (`SceneOverlayRegistry`) | `gpu/debug-drawing` | ui/drawing
  - Posed bounds; reach | `draw/skinned`; `animation/culling` | |
  - Simulated input: device and merge rules | `input/simulated` | editor, automation
  - Holds in fixed steps, `input.sequence`, `input.click` | `editor/stepping` | input, automation, make

### F4 (major): `make/gameplay-2` and `make/gameplay-3` come before the pages whose subjects they script, and double their homes

- **Where**: `outline-1.md` rows 42-43, before rows 46-53 (`make/input` ... `make/large-worlds`).
- **Evidence**: scripting's proposed chapter 5 (Gameplay API 2) covers physics, contacts, characters, audio and animation
  from scripts, with prerequisites "the Physics, Audio, Animation chapters". Chapter 6 (Gameplay API 3) covers input
  actions, rebinding, game UI callbacks, game flow, saves, graphics options and worlds, with prerequisites "Game UI",
  "Input actions" and "Quality settings". On track G these pages come before the reader has met a rigid body, an action
  map or a canvas. The topic pages after them teach the same script calls again: `make/physics` has the Playground
  scripts, `make/input` has the action reads and capture, `make/ui` has `OnUIClick`, `make/sound` has the one-shots
  (physics hands-on, audio-input game hands-on 3-10, gameui hands-on 1-4).
- **Proposal**: keep `make/gameplay-1` (entities, components, transforms, spawning, assets: what every topic page
  needs). Dissolve `make/gameplay-2` and `make/gameplay-3` into the topic pages that own each subject (physics,
  characters-cameras, sound, animation, input, ui, levels-saves, look, large-worlds), and leave the complete listing to
  `reference/script-api`. If they stay, move `gameplay-2` after `make/sound` and `gameplay-3` after `make/levels-saves`,
  and make them "API at a glance" pages that link back to the topic pages and teach nothing first.

### F5 (major): the part prerequisites of the five areas are understated

- **Where**: `outline-3.md` lines 64, 81, 101 and 114; `outline-4.md` lines 7 and 22. `book.md` line 22 says "the book
  never assumes more than the page's listed prerequisites".
- **Evidence and proposal**:

  | Part | Add | Because (inventory) |
  | --- | --- | --- |
  | physics (line 64) | `world/scene-graph`, `world/ecs`, `core/jobs`, `world/projects-settings`, `world/interpolation` | Sync and write-back use the transform contract and EnTT signals (§1.4, §1.5, concept 17). `PhysicsTaskSystem`, parallel creation and deterministic characters use jobs. `Physics.Simulation` and `Scene.CollisionLayers` are settings sections. Teleport breaks interpolation. |
  | animation (line 81) | `core/jobs`, `world/scene-graph`, `assets/residency`, page-level `physics/character-controllers` (root motion) and `draw/bounds-culling` (culling) | Parallel evaluation (§1.8). Root motion and attachments signal through the transform contract (rules 4 and 15). Asset sets request every update (rule 19). The prerequisites of chapters 10 and 12. |
  | audio (line 101) | `core/engine-modules`, `core/frame-loop`, `assets/importing`, `assets/loading`, `basics/math-vectors` | `AudioModule` is an `EngineModule` (§1.1). Clips have an importer, a cooked format and asynchronous states (§1.2, §1.4). Spatial sound needs vectors (A7, A8). |
  | input (line 114) | `core/frame-loop`, `core/time`, `world/projects-settings`, `basics/bytes` | The Input stage of the frame (code #5). Edges in `OnFixedUpdate` and holds counted in fixed steps (B2, B10). `Input.Actions` is a settings section with live edits by `IProjectSettings::GetVersion` (§1.9). The UTF-8 decoder (code #7). Also `editor/commands` for `input/simulated` (see F2). |
  | scripting (line 7) | `core/platform`, `core/conventions`, `world/reflection`, `make/script-loop` | `DynamicLibrary` and private directories (§1.4, §1.5). "Engine code does not throw" against module exceptions (concept 12). Fields are reflection lite, and properties go by registered name (concept 15). The lifecycle's home (F3). |
  | ui (line 22) | `input/actions`, `gpu/binding`, `gpu/coordinates`, `draw/mirrors-camera-relative`, `scripting/abi-sdk` | The UI map (§1.9). The bindless slot table and reversed-Z world pipeline (§1.7). Camera-relative world canvases (code #24). The prerequisites of chapter 8 ("scripting ABI chapter"). |

### F6 (major): `physics/world-step` (XL) holds two chapters' worth: building bodies and stepping them

- **Where**: `outline-3.md` row 71.
- **Evidence**: the inventory's chapter 5 allocates to it "records and slots, change tracking, sync, write-back,
  determinism with threads, task system, mesh cooking, capacities". Behind that list are §1.2 (shape building, shared
  box hulls, baked scale, mass, pending and suspended bodies), §1.3 (the mesh provider, cooking on jobs, the mesh wait,
  hot reload), §1.4 (change rounds, parking) and §1.5 (the whole step). Those are code excerpts #6-#12 and #24-#26, ten
  quotes of up to 60 lines. `PhysicsWorld.cpp` is 5,695 lines, and the inventory itself skimmed 2,000 of them.
- **Proposal**: split the row in two:
  - `physics/building-bodies` | From entities to bodies: records, shapes, mesh colliders | I | L | physics §1.2-1.4
    (records and slots, `AddColliderParts`, baked scale, shared hulls, `ApplyMass`, mesh cooking and the provider,
    pending and suspended bodies, change rounds)
  - `physics/world-step` | Inside `PhysicsWorld`: one step | I | L | physics §1.5 (`Simulate`, sync, forces and
    teleports, characters' step, events per step, write-back bitmap, parallel write-back, task system, determinism)
  - Capacities and parking stay in `physics/scale-streaming`.

### F7 (major): `physics/scale-streaming` and `worlds/physics-scripts` both claim the prepared start and reservation

- **Where**: `outline-3.md` row 76; `outline-4.md` row 43.
- **Evidence**:
  - Physics chapter 11 covers "capacities and growth, sliced and parallel creation, parking, reservation by the
    streamer".
  - worlds-runtime chapter 6 covers "prepared start, capacity reservation and the cook's MaxBodiesInRadius".
  - Physics chapter 11 also lists "World partition" as a prerequisite, but Part 11 comes six parts before Part 17.
- **Proposal**:
  - Add a row to `book.md`: "Physics capacity, growth, sliced building, parking (the mechanism) | `physics/scale-streaming`
    | `worlds/physics-scripts` (when the streamer reserves and prepares, `MaxBodiesInRadius`, prefetch before teleport)".
  - Give `physics/scale-streaming` the prerequisite `world/sub-scenes` (Part 4) instead of anything in Part 17.
  - Have `worlds/physics-scripts` link to it.

### F8 (major): `make/ui` (T, L) holds two proposed chapters

- **Where**: `outline-1.md` row 51 (`gameui "Making menus and HUDs", "Widgets, events and scripts"`).
- **Evidence**: gameui chapter 2 is a tutorial of size L with about 10 screenshots: canvases, anchors, scale modes,
  images, text, layout groups, masks, 2D mode, the Game UI chip, the camera-less menu. Chapter 3 is a tutorial of size M
  with about 4 screenshots: buttons, toggles, sliders, input fields, event targets, focus, gamepad navigation, pause
  menus on unscaled time, world-space signs. Together that is about 8,000 words and 14 pictures in a 5,000-word page,
  and game hands-on 1-6 are six exercises.
- **Proposal**: split it into two rows:
  - `make/ui` | Menus and HUDs | T | L | gameui "Making menus and HUDs"
  - `make/ui-widgets` | Making UI do things: widgets, events and scripts | T | M | gameui "Widgets, events and scripts"

### F9 (major): `scripting/host-api` is a tutorial, but it was given an internals chapter

- **Where**: `outline-4.md` row 18.
- **Evidence**: scripting chapter 15 is "internals + tutorial, L". Its internals are `ResolveContext` and `HostCall`
  (code #22), validation and `ReportProblem` (#23), the X-macro table with its `static_assert` and counted thunks
  (#24), Dist without counters, and "services and layering" (concept 16, the gameplay API as a facade over services).
  `style.md` lines 64-66 give a tutorial only numbered steps, with no place for a contract, a toy version or the real
  code walked through. Engineering hands-on 3 (adding a callback through `StrataScriptClassDesc`) has no home either.
- **Proposal**: split it into two rows:
  - `scripting/host-api` | The host API: engine services behind a C table | I | L | scripting "The host API"
    (code #22-#24, concept 16)
  - `scripting/tutorial-host-function` | Tutorial: adding a host function and a callback | T | M | scripting hands-on
    E2-E3

### F10 (major): no page owns the editor's script build pipeline, and no inventory surveyed it in depth

- **Where**: Part 18 (`outline-4.md` rows 57-88) and `make/script-builds` (`outline-1.md` row 45, H).
- **Evidence**:
  - editor-core.md line 8 puts "script builds in depth" out of its scope.
  - scripting.md §1.3 lists `ScriptBuild.h/.cpp` (285 and 1,323 lines), `ScriptToolchain`, `ScriptProject`,
    `ScriptSources` and `ScriptBuildConfig.h.in` as "editor area: summarized, not read in depth".
  - gamedev.md rows 22, 130, 134 and 136 cover only the use side: toolchain discovery, Play builds first, presets, the
    long-path fallback.
  - So how the editor finds compilers, runs CMake, parses diagnostics into the Problems panel, builds before Play and
    triggers hot reload is in no internals page and in no allocation.
- **Proposal**: add `editor/script-builds` | Building scripts from the editor: toolchains, CMake, diagnostics | I | M |
  new; scripting §1.3, §1.7. Put it after `editor/play-mode`. Have the allocator of Part 18 read `ScriptBuild*`,
  `ScriptToolchain*`, `ScriptProject*`, `ScriptSources*`, `ExternalEditor*` and `Panels/ProblemsPanel*` before
  allocating, because no inventory did.

### F11 (major): `animation/editor` is a how-to page, but its material is internals

- **Where**: `outline-3.md` row 96 (`H | M`).
- **Evidence**: animation §1.11 and concept 21 describe `AnimationPreview`, which is an `ISkinningPoses` provider. It
  holds rest poses shared per skeleton (recomputed only on reimport), the `ClipStart` edit pose, render transforms for
  attachments that change no scene data, and signal-driven idle cost. The inventory gives it code excerpts and rules
  12, 20 and 21. Its chapter 13 is "internals + tutorial". `style.md` line 67 says a how-to has "No theory; links to
  the concept page", so this content would be lost.
- **Proposal**: change the row to `animation/editor` | Edit-mode poses and previews | I | M | animation (§1.11, concept
  21). Move the how-to steps (`animation.*` commands, Asset tab tables, the Inspector's live state, the preview chip)
  into `make/animation`.

### F12 (major): the input part has no concept page, and `input/devices-state` (M) holds a concept-plus-internals chapter of size L

- **Where**: `outline-3.md` rows 118-123 (all six are I). `book.md` line 48 says per subsystem "one or more concept
  pages".
- **Evidence**: audio-input concepts B1-B7 are concept material: where input comes from, events versus polling, edges,
  key codes versus characters, text is not keys, focus and capture, and actions instead of keys compared across Unity's
  Input System, Unreal's Enhanced Input and Godot's InputMap. Chapter 8 is "concept + internals, L" and covers the GLFW
  feed, edges, input frames and suspension, the enabled flag, typed text, captures and raw reads.
- **Proposal**: add a first row, `input/how-input-works` | How input reaches a game: events, polling, edges and
  intents | C | M | audio-input B1, B2, B5-B7. Keep `input/devices-state` (I, M) for the code.

### F13 (major): `book.md` "does not do" lists IME, but Strata does receive IME text; the missing part is composition

- **Where**: `book.md` line 98 ("touch and IME").
- **Evidence**:
  - `Strata/src/Strata/Input/Input.h` line 148: "A character typed on the keyboard (the window's character event:
    layouts, dead keys and input methods applied)". Text committed by an IME arrives through `GetTypedText` and reaches
    `UIInputField`.
  - What is missing is composition: GLFW 3.4 (`Strata/vendor/glfw/include/GLFW/glfw3.h`, version 3.4) has no preedit
    API (0 matches), and `Strata/src` has no preedit or composition code.
  - gameui.md "Not determined" says the same ("IME / composition text ... presumably unsupported").
  - Touch is absent: no match for "touch" in `Strata/src/Strata/Input` or `Strata/src/Platform/GLFW`.
- **Proposal**: change "touch and IME" to "touch input, and IME composition (text that the input method has committed
  arrives; the text being composed and the candidate window are not shown)".

### F14 (major): "does not do" misses absences in these five areas that a reader will look for

- **Where**: `book.md` lines 93-99.
- **Evidence and proposal**: add these items (each checked at `822a7a46`):
  - **Physics**
    - Height-field and cylinder colliders: the only collider components are Box, Sphere, Capsule and Mesh
      (`PhysicsComponents.h` 44-68). No height-field appears in `Strata/src`. Height-field colliders are planned as
      "Later" in the Roadmap (`world-environment`).
    - Cloth, soft bodies and destruction: none found.
    - Physics beyond 1e5 m (`c_MaxBodyCoordinate`, `PhysicsWorld.cpp` 73).
  - **Animation**
    - Additive clips, sync markers (until F1's stream), inertialization, dual-quaternion skinning, GPU compute
      skinning, retargeting beyond matching names, float curves, and a skeleton overlay in the viewport (animation
      §1.16; no "dual quaternion" in `Strata/src` or the shaders).
  - **Audio**
    - Occlusion, virtual voices, voice priorities, and streaming from disk or packs. Streamed clips decode encoded
      bytes held in memory (`AudioClip.h` 45-51; Release 0.3.0 line 197).
    - An attenuation model per component: the API has four models, but `AudioComponents.h` has no field, so components
      always use Inverse (audio-input §1.4).
    - Per-world listeners (Roadmap "Further").
    - `Strata/src/Strata/Audio` has no `ma_sound_group`, reverb, HRTF or filter nodes. This confirms the buses,
      effects, reverb and HRTF claim.
  - **Input**
    - Action modifiers, chords, processors and interactions (none in `InputActionSet.h`; DG 1464-1465).
    - Force feedback (no rumble, vibration or haptic code in `Strata/src` or `StrataScriptCore`).
    - Per-player device assignment for local multiplayer: action bindings read every pad (audio-input §1.9, "Multiple
      gamepads"). The Roadmap lists "input contexts" under "Further".
  - **Scripting**
    - Languages other than C++: no `lua_`, `mono_` or CoreCLR code.
    - Script calls from other threads: `ScriptABI.h` lines 25-26 say "Everything is single-threaded".
    - Static linking of modules for consoles (Roadmap "Further").
  - **Game UI**
    - Scroll views, drop-downs, rich text, multi-line input fields and localization. There are 11 registered UI
      components, `GameUIComponents.cpp` 211-397. Input fields are one line (gameui §1.5), and the engine has no
      localization code.
    - Lit world-space UI, and game hit tests that respect geometry in front (gameui rule 24; Roadmap 708-709).

### F15 (major): `audio/clips-voices-sources` and `audio/scene-system` are sized M for content the inventory sizes L

- **Where**: `outline-3.md` rows 107 and 109.
- **Evidence**:
  - Chapter 3 (L) covers clip load modes and chunked safe decoding, the "STAU" cooked format and the importer, the
    custom miniaudio data source (C vtable, atomic cursor), destruction order with a real-time reader, lock-free
    parameters, and `AudioSource` semantics with its two races. That is code #17-#20 and #24, five quotes.
  - Chapter 5 (L) covers records, diffing without signals, the clip state machine, listener choice by sibling-index
    paths, the up-vector policy, scene pause, one-shots with a 0.25 s deadline, services and inspection. That is code
    #26-#29.
- **Proposal**: make both L, or move clip loading and the importer to a separate `audio/clips` (I, M) and keep voices and
  sources in `audio/voices-sources` (I, M).

### F16 (minor): `ui/input` (L) is overloaded and `ui/text` (M) is thin; move text-field editing to `ui/text`

- **Where**: `outline-4.md` rows 29 and 31.
- **Evidence**: gameui chapter 8 gives `ui/input` ten topics: hit grids, world-space rays, gestures and capture, widget
  state machines, navigation scoring, UI actions and repeat, input-field editing, event dispatch and the script bridge
  (§1.8-§1.10, code #25-#30). `ui/text` keeps only layout once glyphs are `gpu/text`'s.
- **Proposal**: retitle `ui/text` as "Text and text fields" and move input-field editing to it (concept 20, §1.9's
  input-field row, `GameUISystem.cpp` 557-747, code #18). `ui/input` keeps pointer, focus and events.

### F17 (minor): `scripting/crash-containment` (L) also carries symbolization

- **Where**: `outline-4.md` row 15.
- **Evidence**: chapter 12 covers hardware exceptions, Windows SEH with stack guarantees and unwinding, POSIX signals
  with the Linux and macOS paths, abort containment with a static CRT, what is not contained, exceptions versus
  crashes, the watchdog, and symbolization (DbgHelp with inline frames, ELF `.symtab`, `dladdr`, the choice of fault
  frame). Those are code #16-#19 and #21, figures 8 and 11. The inventory also asks for "full listings in an appendix",
  and no appendix row exists for them.
- **Proposal**: make it XL, or split it into `scripting/crash-containment` (I, L) and `scripting/symbolization` (I, M,
  "From an address to a file and line": concept 13, code #21).

### F18 (minor): `make/input` (T, M) carries more than M

- **Where**: `outline-1.md` row 46.
- **Evidence**: audio-input chapter 12 (tutorial, M, 5 screenshots) is only the rebinding half. Game hands-on 6-9 add
  devices, gamepad sticks, mouse look with cursor modes, conversion to actions with maps, and a rebinding menu with
  capture and saving.
- **Proposal**: make it L. With F4, it also receives `make/gameplay-3`'s input section.

### F19 (minor): `animation/clips` (M) for a chapter sized L

- **Where**: `outline-3.md` row 87.
- **Evidence**: chapter 4 (L) covers sampling with the three glTF interpolations, keyframe reduction with tolerances,
  shared key times, the STAC cooked format and safe loading. That is code #6-#10, five quotes.
- **Proposal**: make it L.

### F20 (minor): order inside Part 11: `collision-layers` comes after the pages that filter by layers

- **Where**: `outline-3.md` rows 72-74.
- **Evidence**: contacts, triggers and queries all take layer masks. Physics concept 13 (filtering) is taught before
  14-16 (triggers, contacts, queries), and the prerequisites of chapter 7 name layers.
- **Proposal**: move `physics/collision-layers` before `physics/contacts-triggers`.

### F21 (minor): pages about features that are new in 0.8.0 but already landed need no W8 mark, only a "new in 0.8.0" note

- **Where**: `outline-1.md` row 48 (`make/characters-cameras`); `outline-2.md` (`world/interpolation`); `core/time`.
- **Evidence**:
  - `physics-timing` landed in landing 1 (Roadmap lines 639-642). `Scene/TransformInterpolation.h`,
    `SceneInterpolation.cpp` and `ProjectSceneTiming.h/.cpp` are in the tree at `822a7a46`.
  - What is left of interpolation is "Later" (Roadmap line 1698), not wave 8.
  - The one later touch is that `animation-graph` "merges main with `physics-timing` ... rerun the root motion tests and
    the attachment test" (Wave8 plan §4.5).
- **Proposal**: leave them unmarked. State in `style.md` that a feature added after 0.7.0 is labelled "new in 0.8.0".
  Have the pin move re-read `animation/root-motion` and `world/interpolation` (attachments on joints).

### F22 (minor): the inventories carry small errors the allocators must not repeat

- **Where**: allocation step, `process.md` line 70.
- **Evidence**:
  - gameui.md "How completeness was checked" says 12 components, but lists and registers 11
    (`GameUIComponents.cpp` 211-397).
  - animation.md notes that AR 2627 says importer version 9 while `GltfImporter.h` 39 returns 11.
  - scripting.md notes that `Symbolizer.h` 9-12 contradicts `PosixSymbolizer.cpp` 33-48.
  - The UI's Submit defaults are open (gameui "Not determined": `UI.h` and the Manual against `UIActions.h`).
- **Proposal**: add an "errata" list to each part brief, so the writer checks the code (the honesty rule in `style.md`
  lines 101-104 already covers the principle).

### F23 (minor, outside the lens, file only): the plan's W8 list names area lights, but at `822a7a46` they are not wave 8 work

- **Evidence**: `Docs/Roadmap.md` lists "area lights" under "Rendering after wave 8" (line ~1672). `Docs/Plans/Wave8/plan.md`
  has no area-light stream. `outline-3.md` row 16 marks `light/area-lights` "new · W8 (wave 8, stages 1 to 3)".
- **Proposal**: the rendering critic should check the source of "stages 1 to 3". If it is not in wave 8, the page is
  outside 0.8.0 and belongs in `appendix/not-in-strata` until a release brings it.

---

## Where each inventory's items land

The result of steps (1) to (3): a home for each section of each inventory. "Gap" marks a group with no plausible home or
a wrong one, and names the finding.

### physics.md

| Inventory group | Home | Note |
| --- | --- | --- |
| §1.1 components, composition rule, gizmos | `physics/bodies-colliders` (C); use: `make/physics`; `reference/components` | |
| §1.2 body types, shapes, scale baking, mass, CCD, triggers, limits, pending and suspended bodies | `physics/bodies-colliders` (concepts); code: gap, F6 (`physics/building-bodies`) | |
| §1.3 mesh colliders and cooking | gap, F6 | otherwise buried in the XL step page |
| §1.4 world lifecycle, runtime hooks, task system, change tracking, parking, capacities, parallel and sliced creation | `physics/world-step` / `physics/building-bodies`; capacities and parking: `physics/scale-streaming` | overlap with `worlds/physics-scripts`, F7 |
| §1.5 the step | `physics/world-step` | |
| §1.6 contacts and events | `physics/contacts-triggers` | script delivery row, F3 |
| §1.7 queries | `physics/queries`; use: `make/physics` | sweep as an exercise there |
| §1.8 collision layers | `physics/collision-layers`; editor page: `editor/launcher-dialogs` | order, F20 |
| §1.9 character controllers | `physics/character-controllers`; use: `make/characters-cameras` | |
| §1.10 settings, tuning, determinism | `physics/tuning`; determinism row, F3 | |
| §1.11 fixed step and interpolation | `core/time`, `world/systems`, `world/interpolation` | no W8 needed, F21 |
| §1.12 diagnostics, perf | `physics/tuning`; `engineering/perf-lab` | |
| §1.13 script API | `make/physics`, `make/characters-cameras` (F4); `reference/script-api` | |
| §1.14 Physics Playground | `make/samples`, `make/physics` | |
| Concepts 1-23 | 1 `physics/why`; 2 `make/transforms-units`; 3-6 `physics/bodies-colliders`; 7 `core/time`; 8-12 `physics/how-simulation-works`; 13 `collision-layers`; 14-15 `contacts-triggers`; 16 `queries`; 17 `world-step`; 18 `character-controllers`; 19 `world/interpolation`; 20 `core/jobs` (F3); 21-22 `scale-streaming`; 23 `tuning` | |
| Rules 1-25 | spread across the above; rule 8 belongs to `scripting/script-system` | |
| Proposed chapters | 1 kept, 2 merged into `core/time`, 3 into `make/physics` + `bodies-colliders`, 4-9 kept, 10 merged into `world/interpolation`, 11-12 kept, 13 `reference/physics` | no content lost except via F6 and F7 |

### animation.md

| Inventory group | Home | Note |
| --- | --- | --- |
| §1.1 module, optional build | `animation/system`; `core/layers-registries`; `engineering/cmake` | |
| §1.2 types and math | `basics/math-rotations`; `animation/clips` | |
| §1.3 assets (skeleton, clip, controller) | `animation/skeletons`, `animation/clips`, `animation/state-machines` | clips undersized, F19; controller v2, F1 |
| §1.4 glTF import | `animation/importing`; `assets/models-gltf` | |
| §1.5 components | `reference/components`; `make/animation` | |
| §1.6 playback | `state-machines`, `blending`, `time-events` | W8, F1 |
| §1.7 root motion | `animation/root-motion` | |
| §1.8 the system | `animation/system`, `animation/culling` | |
| §1.9 services | `animation/system`; services row, F3 | |
| §1.10 skinning in the renderer | `draw/skinned`; math in `animation/skinning` | written later than its users, F2 |
| §1.11 edit-mode poses | `animation/editor`, wrong kind, F11 | |
| §1.12 scripting | `make/animation`; `reference/script-api` | |
| §1.13 editor commands and views | `make/animation` (use), `animation/editor` (internals), `editor/thumbnails` | |
| §1.15 sample | `make/samples`, `make/project-platformer` | W8, F1 |
| §1.16 absent features | `animation/limits`, `appendix/not-in-strata` | W8, F1 and F14 |
| Concepts 1-22 | 1 `problem`; 2 `world/scene-graph`; 3-4 `basics/math-rotations` + `clips`; 5 `skeletons`; 6-7 `clips`; 8-9 `skinning` + `draw/skinned`; 10 `state-machines`; 11 `blending`; 12-13 `time-events`; 14 `root-motion`; 15-20 `system`; 19 `culling`; 21 `editor`; 22 `importing` | 17 and 20 also need F3's rows |
| Proposed chapters | 2 into `basics/math-rotations`; 13 into an H page (F11); 14 `make/animation`; 15 `reference/animation`; 16 `limits` | content lost only through F11 |

### audio-input.md

| Inventory group | Home | Note |
| --- | --- | --- |
| §1.1 output engine | `audio/engine` | |
| §1.2 clips, importer | `audio/clips-voices-sources` | undersized, F15 |
| §1.3 voices and sources | `audio/clips-voices-sources` | F15 |
| §1.4 scene system, services | `audio/scene-system`, `audio/spatial` | undersized, F15 |
| §1.5 SDK, `audio.state`, Asset tab preview, samples | `make/sound`; `audio/testing`; preview job: `audio/clips-voices-sources` | |
| §1.6-1.7 codes, devices, per-frame state | `input/devices-state`, `input/mouse-cursor`, `input/gamepads` | concept page missing, F12 |
| §1.8 simulated device | `input/simulated` | split with `editor/stepping`, F3; order, F2 |
| §1.9 actions, bindings, capture, UI actions | `input/actions`, `input/rebinding` | UI actions row, F3 |
| §1.10 SDK, editor, runtime | `make/input` (F18); Input Actions page: `editor/launcher-dialogs`; Game view focus: `editor/game-view` | |
| §1.11 boundary items | `core/windows-events`, `ui/input`, `editor/imgui-backends` | |
| Concepts A1-A12, B1-B11 | A1-A2, A12 `sound-in-a-computer`; A3 `basics/threads` + `audio/engine`; A4-A6 `clips-voices-sources`; A7-A8 `spatial`; A9-A10 `scene-system`; A11 `testing`; B1-B7 the new C page (F12); B8 `actions`; B9 `rebinding`; B10 `simulated` / `editor/stepping`; B11 `scripting/host-api` | |
| Proposed chapters | 6 to `make/sound`; 12 to `make/input` + `input/rebinding`; 14 to `reference/audio-input` | none lost |

### scripting.md

| Inventory group | Home | Note |
| --- | --- | --- |
| §1.1 C ABI, host table, descriptors | `scripting/abi-sdk`; versioning concept in `scripting/shared-libraries` | |
| §1.2 SDK | `scripting/abi-sdk`; the use side in `make/*`; helpers in `make/recipes` | |
| §1.3 building a module | `make/script-builds`; CMake function (code #31): `scripting/shared-libraries`; editor pipeline: gap, F10 | |
| §1.4 engine side | `scripting/loading`, `scripting/script-system`, `scripting/hot-reload`, `scripting/host-api` | host API kind, F9 |
| §1.5 crash containment | `scripting/crash-containment` | load, F17 |
| §1.6 hosts | `scripting/loading`; `worlds/runtime`; engine services row, F3 | |
| §1.7 editor workflow | `make/first-script`, `make/script-builds`; internals gap, F10 | |
| §1.8 tests | each page's "how it is tested"; `engineering/feature-test` | |
| Concepts 1-21 | 1 `why-scripts`; 2-4 `shared-libraries`; 5-6 `abi-sdk`; 7 `make/scenes-entities`; 8 `make/script-loop` (F3); 9-10 `script-system`; 11-13 `crash-containment`; 14 `hot-reload`; 15 `abi-sdk` + `world/reflection`; 16 `host-api` (F9); 17-18 `make/gameplay-*` (F4); 19 `world/interpolation`; 20 `make/recipes`; 21 `engineering/feature-test` + `make/automated-playtests` | |
| Proposed chapters | 2-8 in `make`; 15 a tutorial (F9); 16 `reference/script-api` | content lost through F9 |

### gameui.md

| Inventory group | Home | Note |
| --- | --- | --- |
| §1.1 module, registration, inactive reasons | `ui/what-game-ui-does`; `editor/inspectors` | |
| §1.2 components | `reference/components`, `make/ui` | 11 components, F22 |
| §1.3 per-scene model | `ui/contract`, `ui/layout` | |
| §1.4 layout | `ui/layout` | |
| §1.5 text | `ui/text`; glyphs `gpu/text` | F16 |
| §1.6-1.7 quads, pass, shaders | `ui/drawing` | prerequisites and order, F2 and F5 |
| §1.8-1.9 hit testing, input system | `ui/input` | F16 |
| §1.10 services and scripts | `make/ui-widgets` (F8); `ui/input`; services row (F3) | |
| §1.11 editor authoring | `make/ui` (use); `ui/testing` (commands); canvas mode: `editor/scene-view`; UI Rect drawer: `editor/inspectors` | |
| §1.12-1.13 samples, tests | `make/samples`, each page's tests section | |
| Concepts 1-23 | 1 `what-game-ui-does`; 2-6 `layout`; 7 `text` + `gpu/text`; 8, 11-15 `drawing`; 9-10 `contract`; 16-19, 21 `input`; 20 `text` (F16); 22 `core/time`; 23 `testing` | |
| Proposed chapters | 2 and 3 merged into one page (F8) | content squeezed, F8 |

---

## "What Strata does not do", item by item (my areas)

| Item in `book.md` line 96-98 | At `822a7a46` | Evidence | What the page should say |
| --- | --- | --- | --- |
| Joints | Absent | no `b3Create*Joint` in `Strata/src/Strata/Physics`; Roadmap "Ragdoll nodes, after a physics joints stream" | as written |
| Ragdolls, vehicles | Absent | only a comment mentions a vehicle (`World/WorldComponents.h` 20) | as written |
| Shape sweeps | Absent from the API | queries use `b3World_CastRay` (`PhysicsWorld.cpp` 5413, 5435); `b3World_CastMover` only in `CharacterControllers.cpp` 373 | "sweeps are used only inside the character controller" |
| Blend trees, animation layers | Absent now, planned for 0.8.0 | Wave8 `plan.md` §4.5 | conditional, F1 |
| IK | Absent | no IK in `Animation/`; wave 9 `animation-runtime-2` | as written |
| Morph targets | Absent | `GltfImporter.cpp` 1031 skips weight channels | as written |
| Clip compression | Absent | Roadmap wave 9, "if measured to help" | as written |
| Audio buses, effects, reverb, HRTF | Absent | no group, reverb, HRTF or filter nodes in `Audio/`; only `ma_node_set_output_bus_volume` (`AudioVoice.cpp` 308) | as written; add F14's audio items |
| Touch | Absent | no touch code in `Input/` or `Platform/GLFW` | as written |
| IME | Half: committed text works, composition does not | `Input.h` 148; GLFW 3.4 has no preedit | F13 |
| Visual scripting | Absent | | as written; add "only C++" (F14) |

## W8 in my areas

| Page | Wave 8 change | Marked? | Should be |
| --- | --- | --- | --- |
| `animation/state-machines`, `blending`, `time-events`, `root-motion`, `system`, `culling`, `editor`, `limits` | `animation-graph` (tranche 2, before 0.8.0) | no | W8, conditional (F1) |
| `make/animation`, `make/project-platformer`, `make/samples` (robot), `reference/animation` | robot controller to Blend1D plus a layer; `.stanimator` 2 | no | W8, conditional (F1) |
| new `animation/graph`, `animation/sync-layers` | the stream itself | n/a | W8 (F1) |
| `core/time`, `world/interpolation`, `make/characters-cameras` | `physics-timing`, landed in landing 1 | no | no W8; "new in 0.8.0" (F21) |
| physics, audio, input, scripting, ui pages | none beyond the above | no | no W8 |

## Not checked

- The other 14 inventories, except where cited (scene-ecs, foundation, worlds-runtime, gamedev and editor-core chapter
  lists, which I read for the overlaps).
- Whether the `make` tutorials are runnable as command scripts (the pipelines critic's subject).
- The sizes in words of the inventories' proposed chapters, which I compared by their listed content, not by counting.
- The research files.
