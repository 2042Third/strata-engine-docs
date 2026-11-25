# The glossary's merge

Written by `plan/glossary/merge.py` (rulings-11.md, R51); do not edit. It lists what the merge could not decide.

## Counts

| What | Count |
| --- | --- |
| Entries written to `src/content/glossary.json` | 1905 |
| of them the glossary's own entries, kept | 19 of 19 |
| of them the seed's | 394 of 400 |
| of them the inventories' | 1265 |
| of them admitted from the pages' notes (`plan/glossary/admitted.json`) | 227 |
| Term items of the inventories | 1567 |
| Entries their lines give, before joining | 1714 |
| Entries with a use home | 60 |
| Terms with a parenthesis that qualifies them, kept as the source writes it | 119 |
| Inventory terms that are one everyday word of `tools/data/common-words.txt` | 172 |
| Entries of one word with several meanings, qualified by their part (R53) | 75 |

## Left out and listed, by reason

| Reason | Count | What it means |
| --- | --- | --- |
| no home row | 3 | No unit's page homes the item, and it joins no entry that has a home. |
| row asks for more entries | 22 | A row asks for several entries, and the item's line gives one definition for its names. |
| one definition for several things | 24 | The label names several things (split at ", " or " vs ") and the definition does not split into a part for each. |
| id collides | 7 | The term's id is the id of an entry kept before it (the glossary's, the seed's, then the inventories' in their order): the later one is left out. |
| no id | 2 | The term has no letter or digit: its id would be empty. |
| definition refused | 5 | The checks refuse the definition even after the mechanical changes. |
| parenthesis dropped | 8 | A parenthesis inside a name, dropped from the name (the entry is kept). |

## Mechanical changes to definitions

| Change | Definitions |
| --- | --- |
| "..." written "…" | 17 |
| abbreviation written out ("and others") | 2 |
| abbreviation written out ("for example") | 6 |
| backquotes removed | 132 |
| bold marks removed | 4 |
| full stop added | 195 |

## No home row

No unit's page homes the item, and it joins no entry that has a home.

- `physics:541` Job system: no unit's page homes the item or what it joins
- `physics:541` worker: no unit's page homes the item or what it joins
- `render-indirect:589` specular AA: no unit's page homes the item or what it joins

## Row asks for more entries

A row asks for several entries, and the item's line gives one definition for its names.

- `automation:757` Private directory / owner-only file: the row asks for two entries; the line gives one definition for its names
- `build-test:627` Debug / Release / Dist: the row asks for two entries; the line gives one definition for its names
- `build-test:652` Layer table / `MayInclude` / `Tooling` / `Option`: the row asks for four entries; the line gives one definition for its names
- `foundation:571` Timestep / delta time: the row asks for two entries; the line gives one definition for its names
- `foundation:578` Frame pacing / frame-rate cap: the row asks for two entries; the line gives one definition for its names
- `foundation:579` Vsync / FIFO present mode: the row asks for two entries; the line gives one definition for its names
- `foundation:592` Worker / I/O / background thread: the row asks for three entries; the line gives one definition for its names
- `foundation:609` CPU-bound / GPU-bound / capped: the row asks for three entries; the line gives one definition for its names
- `foundation:611` Assert / verify: the row asks for two entries; the line gives one definition for its names
- `foundation:619` Platform layer / seam: the row asks for two entries; the line gives one definition for its names
- `foundation:623` Console run / Interactive run: the row asks for two entries; the line gives one definition for its names
- `foundation:624` Signal / console control handler: the row asks for two entries; the line gives one definition for its names
- `foundation:631` Reparse point / junction / symbolic link: the row asks for three entries; the line gives one definition for its names
- `render-indirect:601` Capture / bake: the row asks for two entries; the line gives one definition for its names
- `render-indirect:602` Influence box / extents / blend distance: the row asks for three entries; the line gives one definition for its names
- `render-indirect:605` Probe cache / slot: the row asks for two entries; the line gives one definition for its names
- `render-indirect:607` HDR output / ProbeCapture: the row asks for two entries; the line gives one definition for its names
- `render-indirect:612` Ray march / step / bisection: the row asks for three entries; the line gives one definition for its names
- `render-indirect:627` Slab / region / brick / anchor: the row asks for four entries; the line gives one definition for its names
- `render-indirect:629` Winding / solid fill: the row asks for two entries; the line gives one definition for its names
- `render-indirect:641` Depth moments / Chebyshev test (DDGI): the row asks for two entries; the line gives one definition for its names
- `render-indirect:645` Re-injection / multi-bounce / bounce gain: the row asks for three entries; the line gives one definition for its names

## One definition for several things

The label names several things (split at ", " or " vs ") and the definition does not split into a part for each.

- `animation:542` Step, linear, cubic spline: 3 names split at ", " or " vs " share one definition
- `audio-input:613` WAV, FLAC, MP3, Ogg Vorbis: 4 names split at ", " or " vs " share one definition
- `build-test:615` Usage requirements, PUBLIC/PRIVATE/INTERFACE: 2 names split at ", " or " vs " share one definition
- `build-test:633` `/Z7` vs PDB: 2 names split at ", " or " vs " share one definition
- `editor-ui:793` Inter, JetBrains Mono, Lucide: 3 names split at ", " or " vs " share one definition
- `foundation:599` Atomic, memory order, fence: 3 names split at ", " or " vs " share one definition
- `foundation:607` Self time vs inclusive time: 2 names split at ", " or " vs " share one definition
- `foundation:608` Percentile (P50, P95), nearest rank: 2 names split at ", " or " vs " share one definition
- `foundation:613` Logger, sink, level: 3 names split at ", " or " vs " share one definition
- `foundation:622` Console vs GUI subsystem: 2 names split at ", " or " vs " share one definition
- `foundation:632` Right-handed coordinates, +Y up, -Z forward: 3 names split at ", " or " vs " share one definition
- `gamedev:639` Rect, anchor, pivot: 3 names split at ", " or " vs " share one definition
- `gamedev:641` Layout group, mask: 2 names split at ", " or " vs " share one definition
- `gamedev:642` Selectable, focus, navigation: 3 names split at ", " or " vs " share one definition
- `gamedev:649` World, persistent scene, layer, cell, streaming source, edit layer, cook: 7 names split at ", " or " vs " share one definition
- `gamedev:660` MCP, toolset: 2 names split at ", " or " vs " share one definition
- `render-direct:719` Depth bias, slope bias, normal offset, receiver plane bias: 4 names split at ", " or " vs " share one definition
- `render-direct:723` Logarithmic vs uniform splits, distribution: 3 names split at ", " or " vs " share one definition
- `render-image:658` Reinhard, ACES, AgX, Khronos PBR Neutral: 4 names split at ", " or " vs " share one definition
- `render-image:667` CIE 1931 xy, CIE 1960 uv: 2 names split at ", " or " vs " share one definition
- `render-image:669` Chromatic adaptation, von Kries, CAT02: 3 names split at ", " or " vs " share one definition
- `render-image:696` Z, L, U shapes: 3 names split at ", " or " vs " share one definition
- `render-scene:585` `multiDrawIndirect`, `drawIndirectFirstInstance`, `maxDrawIndirectCount`: 3 names split at ", " or " vs " share one definition
- `render-scene:636` Skin, joint, skeleton: 3 names split at ", " or " vs " share one definition

## Id collides

The term's id is the id of an entry kept before it (the glossary's, the seed's, then the inventories' in their order): the later one is left out.

- `editor-core:708` `force`: the id "force" is the id of "force"
- `foundation:617` `Scope`: the id "scope" is the id of "scope"
- `gamedev:655` bind: the id "bind" is the id of "`bind`"
- `gamedev:655` expect: the id "expect" is the id of "`expect`"
- `gamedev:655` until: the id "until" is the id of "`until`"
- `render-core:757, render-direct:703, render-image:638` Half float: the id "half-float" is the id of "half-float"
- `scripting:605` `$ORIGIN`: the id "origin" is the id of "origin"

## No id

The term has no letter or digit: its id would be empty.

- `editor-ui:705` `###`: the term has no letter or digit, so its id would be empty
- `editor-ui:705` `##`: the term has no letter or digit, so its id would be empty

## Definition refused

The checks refuse the definition even after the mechanical changes.

- `audio-input:679` Action kind: not one sentence by the site's test (no "?" or "!", a "." only before a character that is not a space): Button, Axis (-1..1), Vector2 (two values, length <= 1).
- `gameui:623` Match width or height: not one sentence by the site's test (no "?" or "!", a "." only before a character that is not a space): 0..1 blend (in log space) between following the screen's width or height.
- `gameui:629` Stretched axis: not one sentence by the site's test (no "?" or "!", a "." only before a character that is not a space): an axis where AnchorMin != AnchorMax; the rect's size follows the parent (margins).
- `render-indirect:592` GTAO: more than one sentence (tools/pages.py): ground-truth AO, horizon-based integration in screen slices (Jimenez et al. 2016).
- `scene-ecs:686` Intermediate directory: not one sentence by the site's test (no "?" or "!", a "." only before a character that is not a space): .strata/, never committed.

## Parenthesis dropped

A parenthesis inside a name, dropped from the name (the entry is kept).

- `foundation:645` Offset (range) allocator: "Offset (range) allocator": the parenthesis inside the name is dropped
- `gameui:659` Display (sRGB) values: "Display (sRGB) values": the parenthesis inside the name is dropped
- `gameui:673` Spatial (automatic) navigation: "Spatial (automatic) navigation": the parenthesis inside the name is dropped
- `render-core:705` Register (tN, sN, bN, uN) and space: "Register (tN, sN, bN, uN) and space": the parenthesis inside the name is dropped
- `render-direct:737` Edge-aware (bilateral) blur: "Edge-aware (bilateral) blur": the parenthesis inside the name is dropped
- `render-image:634` HDR (high dynamic range) image: "HDR (high dynamic range) image": the parenthesis inside the name is dropped
- `render-image:721` Vogel (golden-angle) disk: "Vogel (golden-angle) disk": the parenthesis inside the name is dropped
- `render-indirect:615` Hi-Z (hierarchical depth) march: "Hi-Z (hierarchical depth) march": the parenthesis inside the name is dropped

## Terms with a parenthesis

The parenthesis qualifies the term: the lint matches the name before it (rulings-11.md, R53), and the glossary page shows the whole name.

10-bit intermediate (R10G10B10A2), `cmake_language(DEFER)`, Agent (appendix), Animation controller (state machine), Animation event (notify), Attachment (socket), Batch (gpu), Binding (clip to skeleton), Block (pack), Block compression (BC1-BC7), Box projection (parallax correction), BRDF table (LUT), Cache (CMake), Canvas mode (2D), Capture (editor), Chromatic aberration (lateral), Clip (animation), Clone (render scene), Compaction (defragmentation), Containment (cascade selection), Context (world), Continuous collision (CCD), Cube shadow (six faces), Custom (preset), Data source (miniaudio), Decomposition (of a transform), Dependency (import), Determinism (cross-platform), Directional albedo (E), Discarded (recovery), Draft (editor-ui), Dynamic textures (ImGui 1.92), ECS (entity-component-system), Edge (transition), Engine module registration (Register<Module>Module), Environment map (equirectangular HDR), Event (input), Exclusive (cases), Exposure (EV), Fence (basics), Filmic (Strata), Fixture (CTest), Forward (-Z), Frame (audio), Game camera (pilot), Generator (CMake), GPU stage (Strata), Handle (EnTT), Hash (SHA-256), HDR (RGBA16F), Hemisphere (quaternion), Hold (editor), Identity (rotation), Instance (VkInstance), Interface library (CMake), Jitter (networking), Jitter (TAA), Joint (bone), Journal (feature test), Key (editor), Label (CTest), Latency (networking), Layer (application), Layout (cached), Luminance (Y), Merge (basics), model space (of a pose), Morph target (blend shape), Mover (box3d), Multi-select (BeginMultiSelect), Nine-slice (sliced image), Part (of a prefab), Patch (basics), Pipeline (PSO), Power throttling (EcoQoS), Priority (jobs), Profiler (instrumenting vs sampling), Projecting (basis functions), Prototype (make), Provider (of poses), Push speed (contactSpeed), Radix sort (LSD), Range (light), Registry (world), Request (touch), Resident (proxy), Rollback (networking), Runner (GitHub Actions), Scale (s), Scope (make), Section (property), Sharpening (TAA), Skeleton (rig), Skin (glTF), Smith visibility (height-correlated), Snapshot (networking), Snapshot (save), Specular anti-aliasing (geometric), Specular occlusion (Lagarde), Submodule (git), Supersampling (SSAA), Suppression (capture), Tag (git), Target (CMake), Teleport (audio), Texture table (Strata), Thread (gpu), Tick (networking), Ticket (upload), Tokens (LLM), Topological order (basics), Topological order (parents first), Triangle-box overlap (Akenine-Moller), Uniform (distribution), Uniform grid (physics), Variant (basics), Variant (shader), Viewport (input), Waveform (preview)

## Inventory terms that are one everyday word

The lint asks for no mark at an unmarked use of these on a page that is not their home (style.md §3, rulings-11.md, R53): a writer marks the word where the page uses the term's sense.

accept, Acquire, active, Adoption, advance, alpha, Anchor, Application, arena, bake, Banner, Barrier, Blend, Bloom, Bucket, Bus, Candidate, Canvas, Capacity, card, Chip, chunk, Claim, clip, Clipping, Command, Composite, Compound, Confidence, Context, contrast, Cook, Cooking, Damping, deferred, Dependency, Discard, Discovery, Down, encoded, Event, Exposure, Extinction, Fault, Fence, Field, floor, fly, Focus, focused, Forward, Freeze, Friction, Frontier, Gain, Gesture, Ghosting, Hard, Headless, History, Hook, Host, Hovered, Import, Index, Influence, Instancing, interval, Island, Item, Join, joint, Local, Manifest, map, Margin, mask, Material, Measure, Median, Metallic, Metering, Metric, Mixer, Model, orbit, overlap, pack, page, pan, Pancaking, Panel, Panning, patch, pending, Picking, Pill, Pin, Pinning, Pitch, pixels, Play, Points, poll, Polling, Port, Presence, present, Pressed, Priority, Probe, Property, Prototype, provisional, Pruning, Reach, Reflection, Registry, Released, Relevance, relocation, Replay, Requirement, Reservation, Residency, Revert, Serial, server, Service, Settled, Simple, Simulate, Single, Skeleton, skin, Skinning, Sleeping, Slope, Slot, Socket, Softness, Source, Split, State, step, Stepping, Style, Surface, Surrogate, Sweep, target, Template, Theme, tile, Tint, Toast, Toe, Token, Tool, Transmission, Trash, Trigger, Trim, Unpack, Validation, validity, Version, View, Voice, Watchdog, Winding, Window

## Admitted from the pages' notes

- "Agent (appendix)" (agent-appendix): a new entry, homed on appendix/game-ai
- "Batch (gpu)" (batch-gpu): a new entry, homed on gpu/upload-queue
- "Batch (gpu)": the alias "upload batch" its home page asked for
- "Blend" (blend): the definition of its home page, world/interpolation
- "CPU twin" (cpu-twin): a new entry, homed on image/tone-mapping
- "CPU twin": the alias "CPU reference" its home page asked for
- "CPU-bound" (cpu-bound): a new entry, homed on core/profiling
- "Cache (CMake)" (cache-cmake): a new entry, homed on basics/build
- "Capture (editor)" (capture-editor): a new entry, homed on editor/camera-viewport
- "Compose" (compose): a new entry, homed on world/interpolation
- "Console run" (console-run): a new entry, homed on core/first-frame
- "Context (world)" (context-world): a new entry, homed on world/ecs
- "Dead zone": the alias "axial dead zone" its home page asked for
- "Dead zone": the alias "radial dead zone" its home page asked for
- "Draft (editor-ui)" (draft-editor-ui): a new entry, homed on editor-ui/inspectors
- "Endpoints": the alias "endpoint" its home page asked for
- "Exact" (exact): a new entry, homed on world/interpolation
- "Exclusive (cases)" (exclusive-cases): a new entry, homed on basics/math-probability
- "Exclusive (cases)": the alias "mutually exclusive" its home page asked for
- "FIFO present mode" (fifo-present-mode): a new entry, homed on core/frame-loop
- "FIFO present mode": the alias "FIFO present modes" its home page asked for
- "Fence (basics)" (fence-basics): a new entry, homed on basics/threads
- "Fence (basics)": the alias "memory fence" its home page asked for
- "GPU scene" (gpu-scene): a new entry, homed on draw/entities-to-draws
- "GPU-bound" (gpu-bound): a new entry, homed on core/profiling
- "Identity (rotation)" (identity-rotation): a new entry, homed on basics/math-rotations
- "Identity (rotation)": the alias "identity quaternion" its home page asked for
- "Jitter (networking)" (jitter-networking): a new entry, homed on appendix/networking
- "Key (editor)" (key-editor): a new entry, homed on editor/thumbnails
- "Key (editor)": the alias "thumbnail key" its home page asked for
- "Latency (networking)" (latency-networking): a new entry, homed on appendix/networking
- "Latency (networking)": the alias "round-trip time" its home page asked for
- "Merge (basics)" (merge-basics): a new entry, homed on basics/git
- "Morton order" (morton-order): a new entry, homed on basics/numbers
- "Morton order": the alias "Z-order" its home page asked for
- "NAT traversal" (nat-traversal): a new entry, homed on appendix/networking
- "NAT traversal": the alias "NAT" its home page asked for
- "Orbit camera" (orbit-camera): the definition of its home page, editor/camera-viewport
- "Patch (basics)" (patch-basics): a new entry, homed on basics/git
- "Priority (jobs)" (priority-jobs): a new entry, homed on core/jobs
- "Projecting (basis functions)" (projecting-basis-functions): a new entry, homed on basics/math-sphere
- "Projecting (basis functions)": the alias "projection onto basis functions" its home page asked for
- "Prototype (make)" (prototype-make): a new entry, homed on make/designing-a-game
- "Rebinding": the alias "rebind" its home page asked for
- "Rebinding": the alias "rebinds" its home page asked for
- "Registry (world)" (registry-world): a new entry, homed on world/ecs
- "Rollback (networking)" (rollback-networking): a new entry, homed on appendix/networking
- "Rollback (networking)": the alias "rollback network code" its home page asked for
- "Scope (make)" (scope-make): a new entry, homed on make/designing-a-game
- "Snapshot (networking)" (snapshot-networking): a new entry, homed on appendix/networking
- "Sub-scene" (sub-scene): the definition of its home page, world/sub-scenes
- "Sub-scene": the alias "sub-scenes" its home page asked for
- "TPDF": the alias "triangular dither" its home page asked for
- "Tag (git)" (tag-git): a new entry, homed on basics/git
- "Target (CMake)" (target-cmake): a new entry, homed on engineering/cmake
- "Target (CMake)": the alias "CMake target" its home page asked for
- "Thread (gpu)" (thread-gpu): a new entry, homed on gpu/compute
- "Thread (gpu)": the alias "invocation" its home page asked for
- "Tick (networking)" (tick-networking): a new entry, homed on appendix/networking
- "Tick (networking)": the alias "tick rate" its home page asked for
- "Topological order (basics)" (topological-order-basics): a new entry, homed on basics/trees-graphs
- "Uniform (distribution)" (uniform-distribution): a new entry, homed on basics/math-probability
- "Uniform (distribution)": the alias "uniform distribution" its home page asked for
- "Uniform grid (physics)" (uniform-grid-physics): a new entry, homed on physics/collision-detection
- "Variant (basics)" (variant-basics): a new entry, homed on basics/cpp-modern
- "`ci/<name>` branch" (ci-name-branch): the definition of its home page, engineering/ci
- "`ci/<name>` branch": the alias "`ci/<name>`" its home page asked for
- "additive load" (additive-load): a new entry, homed on world/sub-scenes
- "additive load": the alias "additive loads" its home page asked for
- "affine transform" (affine-transform): a new entry, homed on basics/math-matrices
- "affine transform": the alias "affine transformation" its home page asked for
- "affine transform": the alias "affine transforms" its home page asked for
- "alignment" (alignment): a new entry, homed on basics/bytes
- "angular velocity" (angular-velocity): a new entry, homed on basics/math-rotations
- "archetype" (archetype): a new entry, homed on world/what-a-world-is
- "archetype": the alias "archetypes" its home page asked for
- "assert handler" (assert-handler): a new entry, homed on core/debugging
- "assert handler": the alias "assertion handler" its home page asked for
- "assertion" (assertion): a new entry, homed on core/conventions
- "asset field" (asset-field): a new entry, homed on make/project-platformer
- "authority" (authority): a new entry, homed on appendix/networking
- "authority": the alias "authoritative server" its home page asked for
- "azimuth" (azimuth): a new entry, homed on basics/math-sphere
- "backlog" (backlog): a new entry, homed on core/time
- "bandwidth" (bandwidth): a new entry, homed on gpu/how-a-gpu-frame-works
- "bandwidth": the alias "memory bandwidth" its home page asked for
- "behaviour tree" (behaviour-tree): a new entry, homed on appendix/game-ai
- "behaviour tree": the alias "behaviour trees" its home page asked for
- "bilinear interpolation" (bilinear-interpolation): a new entry, homed on basics/math-interpolation
- "bilinear interpolation": the alias "bilinear blend" its home page asked for
- "binary heap" (binary-heap): a new entry, homed on basics/trees-graphs
- "binary heap": the alias "binary heaps" its home page asked for
- "binary search tree" (binary-search-tree): a new entry, homed on basics/trees-graphs
- "binary search tree": the alias "binary search trees" its home page asked for
- "bisection" (bisection): a new entry, homed on indirect/ssr
- "bisection": the alias "bisect" its home page asked for
- "bisection": the alias "bisections" its home page asked for
- "bisection": the alias "bisects" its home page asked for
- "bitangent" (bitangent): a new entry, homed on basics/math-bases
- "bitangent": the alias "bitangents" its home page asked for
- "bounding volume" (bounding-volume): a new entry, homed on basics/math-geometry
- "bounding volume": the alias "bounding volumes" its home page asked for
- "capped" (capped): a new entry, homed on core/profiling
- "client-side prediction" (client-side-prediction): a new entry, homed on appendix/networking
- "configuration struct" (configuration-struct): a new entry, homed on basics/cpp-generic
- "conjugate" (conjugate): a new entry, homed on basics/math-rotations
- "conjugate": the alias "quaternion conjugate" its home page asked for
- "convex" (convex): a new entry, homed on basics/math-geometry
- "core loop" (core-loop): a new entry, homed on make/designing-a-game
- "coverage by construction" (coverage-by-construction): a new entry, homed on engineering/feature-test
- "cut list" (cut-list): a new entry, homed on make/designing-a-game
- "cycle" (cycle): a new entry, homed on basics/trees-graphs
- "datagram" (datagram): a new entry, homed on appendix/networking
- "datagram": the alias "datagrams" its home page asked for
- "decal" (decal): a new entry, homed on appendix/not-in-strata
- "decal": the alias "decals" its home page asked for
- "definition" (definition): a new entry, homed on basics/build
- "delta compression" (delta-compression): a new entry, homed on appendix/networking
- "determinant" (determinant): a new entry, homed on basics/math-bases
- "deterministic lockstep" (deterministic-lockstep): a new entry, homed on appendix/networking
- "deterministic lockstep": the alias "lockstep" its home page asked for
- "diagnostic" (diagnostic): a new entry, homed on editor/script-builds
- "diagnostic": the alias "build diagnostic" its home page asked for
- "dielectric" (dielectric): a new entry, homed on light/materials
- "dispatch" (dispatch): a new entry, homed on gpu/compute
- "double cover" (double-cover): a new entry, homed on basics/math-rotations
- "double sun" (double-sun): a new entry, homed on light/sky
- "dynamic tree" (dynamic-tree): a new entry, homed on physics/collision-detection
- "editor camera" (editor-camera): a new entry, homed on editor/camera-viewport
- "entity interpolation" (entity-interpolation): a new entry, homed on appendix/networking
- "epoch" (epoch): a new entry, homed on image/pre-exposure
- "equirectangular map" (equirectangular-map): a new entry, homed on basics/math-sphere
- "equirectangular map": the alias "latitude-longitude map" its home page asked for
- "exponential decay" (exponential-decay): a new entry, homed on basics/math-interpolation
- "extrapolation" (extrapolation): a new entry, homed on world/interpolation
- "extrapolation": the alias "extrapolate" its home page asked for
- "extrapolation": the alias "extrapolated" its home page asked for
- "extrapolation": the alias "extrapolates" its home page asked for
- "extrapolation": the alias "extrapolating" its home page asked for
- "fallback stack" (fallback-stack): a new entry, homed on indirect/seam
- "fallback stack": the alias "fallback hierarchy" its home page asked for
- "fat box" (fat-box): a new entry, homed on physics/collision-detection
- "fat box": the alias "fattened box" its home page asked for
- "fiber" (fiber): a new entry, homed on core/jobs
- "flaky test" (flaky-test): a new entry, homed on engineering/testing
- "flaky test": the alias "flaky tests" its home page asked for
- "flaky test": the alias "flaky" its home page asked for
- "format header" (format-header): a new entry, homed on basics/data-formats
- "forwarding reference" (forwarding-reference): a new entry, homed on basics/cpp-modern
- "forwarding reference": the alias "forwarding references" its home page asked for
- "frame pacing" (frame-pacing): a new entry, homed on core/frame-loop
- "frame-rate cap" (frame-rate-cap): a new entry, homed on core/frame-loop
- "frame-rate cap": the alias "frame rate cap" its home page asked for
- "framebuffer" (framebuffer): a new entry, homed on core/windows-events
- "framebuffer": the alias "framebuffers" its home page asked for
- "free list" (free-list): a new entry, homed on basics/data-structures
- "free list": the alias "free lists" its home page asked for
- "function pointer" (function-pointer): a new entry, homed on basics/cpp-generic
- "function pointer": the alias "function pointers" its home page asked for
- "geometric series" (geometric-series): a new entry, homed on basics/math-interpolation
- "glob" (glob): a new entry, homed on basics/data-formats
- "glob": the alias "globs" its home page asked for
- "goal-oriented action planning" (goal-oriented-action-planning): a new entry, homed on appendix/game-ai
- "goal-oriented action planning": the alias "GOAP" its home page asked for
- "grey box" (grey-box): a new entry, homed on make/designing-a-game
- "group barrier" (group-barrier): a new entry, homed on gpu/compute
- "half-life" (half-life): a new entry, homed on basics/math-interpolation
- "half-life": the alias "half-lives" its home page asked for
- "hardware thread" (hardware-thread): a new entry, homed on basics/computer
- "hardware thread": the alias "hardware threads" its home page asked for
- "head-of-line blocking" (head-of-line-blocking): a new entry, homed on appendix/networking
- "header" (header): a new entry, homed on basics/bytes
- "hitch" (hitch): a new entry, homed on start/what-an-engine-is
- "image plane" (image-plane): a new entry, homed on basics/math-projection
- "immediate representation" (immediate-representation): a new entry, homed on draw/entities-to-draws
- "incomplete type" (incomplete-type): a new entry, homed on basics/cpp-modern
- "integrated development environment" (integrated-development-environment): a new entry, homed on make/script-builds
- "integrated development environment": the alias "IDE" its home page asked for
- "integrated development environment": the alias "IDEs" its home page asked for
- "interest management" (interest-management): a new entry, homed on appendix/networking
- "interpolated set" (interpolated-set): a new entry, homed on world/interpolation
- "interpolation": the alias "interpolate" its home page asked for
- "interpolation": the alias "interpolated" its home page asked for
- "interpolation": the alias "interpolates" its home page asked for
- "interpolation": the alias "interpolating" its home page asked for
- "judder" (judder): a new entry, homed on world/interpolation
- "kick" (kick): a new entry, homed on make/project-tetris
- "lag compensation" (lag-compensation): a new entry, homed on appendix/networking
- "light space" (light-space): a new entry, homed on light/shadow-basics
- "lightmap" (lightmap): a new entry, homed on appendix/not-in-strata
- "lightmap": the alias "lightmaps" its home page asked for
- "line coverage" (line-coverage): a new entry, homed on engineering/feature-test
- "line of sight" (line-of-sight): a new entry, homed on appendix/game-ai
- "live line" (live-line): a new entry, homed on editor-ui/inspectors
- "live line": the alias "live lines" its home page asked for
- "load factor" (load-factor): a new entry, homed on basics/data-structures
- "local avoidance" (local-avoidance): a new entry, homed on appendix/game-ai
- "log level" (log-level): a new entry, homed on core/conventions
- "log level": the alias "log levels" its home page asked for
- "logger" (logger): a new entry, homed on core/conventions
- "logger": the alias "loggers" its home page asked for
- "magic number" (magic-number): a new entry, homed on basics/bytes
- "magic number": the alias "magic numbers" its home page asked for
- "merge conflict" (merge-conflict): a new entry, homed on basics/git
- "merge conflict": the alias "merge conflicts" its home page asked for
- "mesh collider" (mesh-collider): a new entry, homed on make/project-platformer
- "mesh collider": the alias "triangle-mesh collider" its home page asked for
- "moiré" (moir): a new entry, homed on basics/signals
- "moiré": the alias "moire" its home page asked for
- "navigation mesh" (navigation-mesh): a new entry, homed on appendix/game-ai
- "navigation mesh": the alias "nav mesh" its home page asked for
- "navigation mesh": the alias "navigation meshes" its home page asked for
- "navigation mesh": the alias "navmesh" its home page asked for
- "node handle" (node-handle): a new entry, homed on basics/cpp-generic
- "node handle": the alias "node handles" its home page asked for
- "normal offset" (normal-offset): a new entry, homed on light/shadow-basics
- "normalization": the alias "normalized" its home page asked for
- "normalization": the alias "normalizing" its home page asked for
- "object pool" (object-pool): a new entry, homed on make/patterns
- "object pool": the alias "object pools" its home page asked for
- "obscurance" (obscurance): a new entry, homed on indirect/ao
- "off-by-one mistake" (off-by-one-mistake): a new entry, homed on basics/programming-2
- "off-by-one mistake": the alias "off by one" its home page asked for
- "one-paragraph design" (one-paragraph-design): a new entry, homed on make/designing-a-game
- "optimization" (optimization): a new entry, homed on basics/build
- "optimization": the alias "optimize" its home page asked for
- "optimization": the alias "optimized" its home page asked for
- "optimization": the alias "optimizes" its home page asked for
- "optimization": the alias "optimizing" its home page asked for
- "orbit" (orbit): the definition of its home page, editor/camera-viewport
- "ordered float" (ordered-float): a new entry, homed on light/many-lights
- "ordered map" (ordered-map): a new entry, homed on basics/trees-graphs
- "ordered map": the alias "ordered maps" its home page asked for
- "orthonormal basis" (orthonormal-basis): a new entry, homed on basics/math-bases
- "orthonormal basis": the alias "orthonormal frame" its home page asked for
- "packet loss" (packet-loss): a new entry, homed on appendix/networking
- "padding" (padding): a new entry, homed on basics/bytes
- "parser" (parser): a new entry, homed on basics/data-formats
- "parser": the alias "parsers" its home page asked for
- "ping-pong" (ping-pong): a new entry, homed on image/taa
- "play revision" (play-revision): a new entry, homed on animation/culling
- "playtest" (playtest): a new entry, homed on make/designing-a-game
- "playtest": the alias "play testing" its home page asked for
- "pointer to a member" (pointer-to-a-member): a new entry, homed on basics/cpp-generic
- "polar angle" (polar-angle): a new entry, homed on basics/math-sphere
- "post pass" (post-pass): a new entry, homed on image/spatial-aa
- "pre-commit review checklist" (pre-commit-review-checklist): a new entry, homed on engineering/contributing
- "pre-commit review checklist": the alias "review checklist" its home page asked for
- "preferences" (preferences): a new entry, homed on editor/projects
- "prefix sum" (prefix-sum): a new entry, homed on basics/data-structures
- "prefix sum": the alias "prefix sums" its home page asked for
- "priority queue" (priority-queue): a new entry, homed on basics/trees-graphs
- "priority queue": the alias "priority queues" its home page asked for
- "project migration" (project-migration): a new entry, homed on editor/projects
- "pull model" (pull-model): a new entry, homed on audio/sound-in-a-computer
- "quadratic equation" (quadratic-equation): a new entry, homed on basics/math-geometry
- "quadratic equation": the alias "quadratic equations" its home page asked for
- "quadratic equation": the alias "quadratic" its home page asked for
- "ragdoll" (ragdoll): a new entry, homed on animation/limits
- "rasterization" (rasterization): a new entry, homed on gpu/how-a-gpu-frame-works
- "rasterization": the alias "rasterize" its home page asked for
- "rasterization": the alias "rasterized" its home page asked for
- "rasterization": the alias "rasterizer" its home page asked for
- "rasterization": the alias "rasterizes" its home page asked for
- "rasterization": the alias "rasterizing" its home page asked for
- "recent projects" (recent-projects): a new entry, homed on editor/projects
- "recent projects": the alias "recent list" its home page asked for
- "recoverable failure" (recoverable-failure): a new entry, homed on core/conventions
- "recoverable failure": the alias "recoverable failures" its home page asked for
- "reflectance" (reflectance): a new entry, homed on light/reflectance
- "register" (register): a new entry, homed on basics/computer
- "regular expression" (regular-expression): a new entry, homed on basics/data-formats
- "regular expression": the alias "regex" its home page asked for
- "regular expression": the alias "regular expressions" its home page asked for
- "relay server" (relay-server): a new entry, homed on appendix/networking
- "retained representation" (retained-representation): a new entry, homed on draw/entities-to-draws
- "ringing" (ringing): a new entry, homed on basics/math-sphere
- "rotation box" (rotation-box): a new entry, homed on make/project-tetris
- "seam" (seam): a new entry, homed on core/platform
- "self time" (self-time): a new entry, homed on core/profiling
- "self time": the alias "self-time" its home page asked for
- "separating axis test" (separating-axis-test): a new entry, homed on physics/collision-detection
- "separating axis" (separating-axis): a new entry, homed on basics/math-geometry
- "sequence number" (sequence-number): a new entry, homed on core/debugging
- "sequence number": the alias "sequence numbers" its home page asked for
- "server reconciliation" (server-reconciliation): a new entry, homed on appendix/networking
- "shared memory" (shared-memory): a new entry, homed on gpu/compute
- "signed distance" (signed-distance): a new entry, homed on basics/math-geometry
- "significand" (significand): a new entry, homed on basics/numbers
- "significand": the alias "mantissa" its home page asked for
- "simple mode" (simple-mode): a new entry, homed on animation/state-machines
- "simplex" (simplex): a new entry, homed on physics/collision-detection
- "sink" (sink): a new entry, homed on core/conventions
- "sky preset" (sky-preset): a new entry, homed on light/sky
- "slab" (slab): a new entry, homed on basics/math-geometry
- "slicing" (slicing): a new entry, homed on basics/cpp-classes
- "source record" (source-record): a new entry, homed on audio/scene-system
- "source scan" (source-scan): a new entry, homed on editor-ui/ui-testing
- "source scan": the alias "source scans" its home page asked for
- "spatial tree" (spatial-tree): a new entry, homed on basics/trees-graphs
- "spatial tree": the alias "spatial trees" its home page asked for
- "spec" (spec): a new entry, homed on capstone/plan
- "spec": the alias "specs" its home page asked for
- "specular power" (specular-power): a new entry, homed on light/materials
- "stable hash" (stable-hash): a new entry, homed on basics/data-formats
- "stable sort" (stable-sort): a new entry, homed on basics/trees-graphs
- "stable sort": the alias "stable sorts" its home page asked for
- "staging area" (staging-area): a new entry, homed on basics/git
- "stamp" (stamp): a new entry, homed on editor/script-builds
- "stamp": the alias "build stamp" its home page asked for
- "standard deviation" (standard-deviation): a new entry, homed on basics/math-probability
- "standard-layout type" (standard-layout-type): a new entry, homed on basics/bytes
- "state machine" (state-machine): a new entry, homed on make/patterns
- "state machine": the alias "state machines" its home page asked for
- "static initialization" (static-initialization): a new entry, homed on basics/build
- "steering behaviour" (steering-behaviour): a new entry, homed on appendix/game-ai
- "steering behaviour": the alias "steering behaviours" its home page asked for
- "stratified sampling" (stratified-sampling): a new entry, homed on basics/math-probability
- "stratified sampling": the alias "stratified offsets" its home page asked for
- "stratified sampling": the alias "stratified" its home page asked for
- "structured binding" (structured-binding): a new entry, homed on basics/cpp-modern
- "structured binding": the alias "structured bindings" its home page asked for
- "subnormal number" (subnormal-number): a new entry, homed on basics/numbers
- "subnormal number": the alias "denormal" its home page asked for
- "subnormal number": the alias "subnormal numbers" its home page asked for
- "subnormal number": the alias "subnormal" its home page asked for
- "subnormal number": the alias "subnormals" its home page asked for
- "subtree" (subtree): a new entry, homed on basics/trees-graphs
- "subtree": the alias "subtrees" its home page asked for
- "support point" (support-point): a new entry, homed on physics/collision-detection
- "swap-remove" (swap-remove): a new entry, homed on basics/data-structures
- "swap-remove": the alias "swap and pop" its home page asked for
- "sweep and prune" (sweep-and-prune): a new entry, homed on physics/collision-detection
- "sweep and prune": the alias "sweep-and-prune" its home page asked for
- "symbol" (symbol): a new entry, homed on basics/build
- "tangent space" (tangent-space): a new entry, homed on basics/math-bases
- "tangent space": the alias "tangent frame" its home page asked for
- "task graph" (task-graph): a new entry, homed on core/jobs
- "task graph": the alias "task graphs" its home page asked for
- "texture coordinates" (texture-coordinates): a new entry, homed on gpu/coordinates
- "texture coordinates": the alias "UV coordinates" its home page asked for
- "texture coordinates": the alias "UV" its home page asked for
- "thread group" (thread-group): a new entry, homed on gpu/compute
- "thread group": the alias "workgroup" its home page asked for
- "time constant" (time-constant): a new entry, homed on basics/math-interpolation
- "time constant": the alias "tau" its home page asked for
- "trail" (trail): a new entry, homed on core/reading-code
- "trail": the alias "code trail" its home page asked for
- "transpose" (transpose): a new entry, homed on basics/math-bases
- "transpose": the alias "transposed matrix" its home page asked for
- "type argument" (type-argument): a new entry, homed on basics/cpp-generic
- "type argument": the alias "type arguments" its home page asked for
- "type trait" (type-trait): a new entry, homed on basics/cpp-modern
- "type trait": the alias "type traits" its home page asked for
- "union-find" (union-find): a new entry, homed on basics/trees-graphs
- "union-find": the alias "disjoint sets" its home page asked for
- "untrusted input" (untrusted-input): a new entry, homed on assets/robustness
- "untrusted input": the alias "untrusted file" its home page asked for
- "update method" (update-method): a new entry, homed on make/patterns
- "usage requirements" (usage-requirements): a new entry, homed on engineering/cmake
- "user pointer" (user-pointer): a new entry, homed on basics/cpp-generic
- "user pointer": the alias "user data" its home page asked for
- "utility AI" (utility-ai): a new entry, homed on appendix/game-ai
- "variance" (variance): a new entry, homed on basics/math-probability
- "vertical slice" (vertical-slice): a new entry, homed on make/designing-a-game
- "view space" (view-space): a new entry, homed on basics/math-projection
- "view space": the alias "camera space" its home page asked for
- "view space": the alias "eye space" its home page asked for
- "virtual table" (virtual-table): a new entry, homed on basics/cpp-classes
- "virtual table": the alias "virtual tables" its home page asked for
- "virtual table": the alias "vtable" its home page asked for
- "vsync" (vsync): a new entry, homed on core/frame-loop
- "vsync": the alias "V-sync" its home page asked for
- "vsync": the alias "vertical synchronization" its home page asked for
- "work stealing" (work-stealing): a new entry, homed on core/jobs
- "workflow" (workflow): a new entry, homed on engineering/ci
- "workflow": the alias "GitHub Actions workflow" its home page asked for
- "workflow": the alias "workflows" its home page asked for
- "worktree" (worktree): a new entry, homed on basics/git
- "worktree": the alias "worktrees" its home page asked for
- "write-ahead ordering" (write-ahead-ordering): a new entry, homed on assets/robustness

## One word, several meanings

- "Baseline (editor)": homed on editor/prefab-instances; "Baseline" is also homed in part gpu
- "Batch (assets)": homed on assets/uploads; "Batch" is also homed in part core, part draw, part editor, part automation
- "Batch (automation)": homed on automation/json-rpc; "Batch" is also homed in part core, part assets, part draw, part editor
- "Batch (core)": homed on core/jobs; "Batch" is also homed in part assets, part draw, part editor, part automation
- "Batch (draw)": homed on draw/batching; "Batch" is also homed in part core, part assets, part editor, part automation
- "Batch (editor)": homed on editor/command-scripts; "Batch" is also homed in part core, part assets, part draw, part automation
- "Budget (assets)": homed on assets/residency; "Budget" is also homed in part engineering
- "Cell (worlds)": homed on worlds/why-streaming; "Cell" is also homed in part gpu
- "Channel (animation)": homed on animation/clips; "Channel" is also homed in part audio
- "Channel (audio)": homed on audio/sound-in-a-computer; "Channel" is also homed in part animation
- "Debug view (editor-ui)": homed on editor-ui/scene-view; "Debug view" is also homed in part gpu
- "Debug view (gpu)": homed on gpu/debugging; "Debug view" is also homed in part editor-ui
- "Entry point (gpu)": homed on gpu/shaders; "Entry point" is also homed in part scripting
- "Entry point (scripting)": homed on scripting/shared-libraries; "Entry point" is also homed in part gpu
- "Framing (automation)": homed on automation/json-rpc; "Framing" is also homed in part editor
- "Framing (editor)": homed on editor/camera-viewport; "Framing" is also homed in part automation
- "Generation (assets)": homed on assets/loading; "Generation" is also homed in part editor
- "Generation (editor)": homed on editor/undo; "Generation" is also homed in part assets
- "Gizmo (editor-ui)": homed on editor-ui/scene-view; "Gizmo" is also homed in part start, part gpu
- "Gizmo (gpu)": homed on gpu/debug-drawing; "Gizmo" is also homed in part start, part editor-ui
- "Gizmo (start)": homed on start/first-game; "Gizmo" is also homed in part gpu, part editor-ui
- "HMAC (automation)": homed on automation/security; "HMAC" is also homed in part basics
- "HMAC (basics)": homed on basics/data-formats; "HMAC" is also homed in part automation
- "Instance (draw)": homed on draw/render-scene; "Instance" is also homed in part scripting
- "Instance (scripting)": homed on scripting/script-system; "Instance" is also homed in part draw
- "Listener (audio)": homed on audio/spatial; "Listener" is also homed in part make, part automation
- "Listener (automation)": homed on automation/json-rpc; "Listener" is also homed in part make, part audio
- "Merge (editor)": homed on editor/undo; "Merge" is also homed in part indirect
- "Merge (indirect)": homed on indirect/gi-cascades; "Merge" is also homed in part editor
- "Overlay (core)": homed on core/windows-events; "Overlay" is also homed in part gpu
- "Overlay (gpu)": homed on gpu/debug-drawing; "Overlay" is also homed in part core
- "Perceptual roughness": homed on light/materials, the first page of part light that homes it; also homed on light/reflectance
- "Pivot (editor)": homed on editor/camera-viewport; "Pivot" is also homed in part ui
- "Pivot (ui)": homed on ui/layout; "Pivot" is also homed in part editor
- "Prefab (make)": homed on make/prefabs; "Prefab" is also homed in part world
- "Prefab (world)": homed on world/prefabs; "Prefab" is also homed in part make
- "Prefetch (assets)": homed on assets/references; "Prefetch" is also homed in part make, part scripting
- "Prefetch (make)": homed on make/large-worlds; "Prefetch" is also homed in part assets, part scripting
- "Prefetch (scripting)": homed on scripting/script-system; "Prefetch" is also homed in part make, part assets
- "Publish (assets)": homed on assets/loading; "Publish" is also homed in part editor
- "Publish (editor)": homed on editor/saving; "Publish" is also homed in part assets
- "Sample (audio)": homed on audio/sound-in-a-computer; "Sample" is also homed in part start, part editor
- "Sample (editor)": homed on editor/projects; "Sample" is also homed in part start, part audio
- "Sample (start)": homed on start/first-game; "Sample" is also homed in part audio, part editor
- "Settings section (editor-ui)": homed on editor-ui/settings-windows; "Settings section" is also homed in part world
- "Settings section (world)": homed on world/projects-settings; "Settings section" is also homed in part editor-ui
- "Slice (indirect)": homed on indirect/ao; "Slice" is also homed in part world, part light
- "Slice (world)": homed on world/sub-scenes; "Slice" is also homed in part light, part indirect
- "Snapping (editor)": homed on editor/placement; "Snapping" is also homed in part editor-ui
- "Snapping (editor-ui)": homed on editor-ui/scene-view; "Snapping" is also homed in part editor
- "Snapshot (world)": homed on world/serialization; "Snapshot" is also homed in part editor
- "Tent filter (image)": homed on image/lens-effects; "Tent filter" is also homed in part light
- "Tent filter (light)": homed on light/sun-shadows-2; "Tent filter" is also homed in part image
- "Texel density (draw)": homed on draw/mip-streaming; "Texel density" is also homed in part light
- "Texel density (light)": homed on light/sun-shadows-1; "Texel density" is also homed in part draw
- "Tone mapping (make)": homed on make/look; "Tone mapping" is also homed in part image
- "Transition (animation)": homed on animation/state-machines; "Transition" is also homed in part make, part ui
- "Transition (ui)": homed on ui/input; "Transition" is also homed in part make, part animation
- "Transmittance (indirect)": homed on indirect/gi-cascades; "Transmittance" is also homed in part light
- "Upload budget (draw)": homed on draw/render-scene-gpu; "Upload budget" is also homed in part gpu
- "Upload budget (gpu)": homed on gpu/upload-queue; "Upload budget" is also homed in part draw
- "View bias (worlds)": homed on worlds/streamer; "View bias" is also homed in part indirect
- "World (editor-ui)": homed on editor-ui/scene-view; "World" is also homed in part worlds
- "World (worlds)": homed on worlds/why-streaming; "World" is also homed in part editor-ui
- "baseline (gpu)": homed on gpu/text; "baseline" is also homed in part editor
- "budget (engineering)": homed on engineering/perf-lab; "budget" is also homed in part assets
- "cascade (indirect)": homed on indirect/gi-cascades; "cascade" is also homed in part light
- "cascade (light)": homed on light/sun-shadows-1; "cascade" is also homed in part indirect
- "cell (gpu)": homed on gpu/text; "cell" is also homed in part worlds
- "listener (make)": homed on make/sound; "listener" is also homed in part audio, part automation
- "slice (light)": homed on light/sun-shadows-1; "slice" is also homed in part world, part indirect
- "snapshot (editor)": homed on editor/undo; "snapshot" is also homed in part world
- "tone mapping (image)": homed on image/why-post; "tone mapping" is also homed in part make
- "tone mapping": homed on image/why-post, the first page of part image that homes it; also homed on image/tone-mapping
- "transition (make)": homed on make/animation; "transition" is also homed in part animation, part ui
- "transmittance (light)": homed on light/atmosphere; "transmittance" is also homed in part indirect
- "view bias (indirect)": homed on indirect/gi-cascades; "view bias" is also homed in part worlds
- "volatile constant buffer": homed on gpu/resources-lifetimes, the first page of part gpu that homes it; also homed on gpu/binding

## Joins the rows' notes made

- "Draw list": homed on draw/batching, the page of the item the rows name; also homed on editor-ui/imgui-backends
- "Headless": homed on core/first-frame, the page of the item the rows name; also homed on automation/sessions
- "Layer table": homed on core/layers-registries, the page of the item the rows name; also homed on worlds/why-streaming
- "Pin": homed on assets/residency, the page of the item the rows name; also homed on worlds/streamer
- "Registry": homed on core/layers-registries, the page of the item the rows name; also homed on world/ecs
- "Toast": homed on editor-ui/status, the page of the item the rows name; also homed on automation/json-rpc
- "Trigger": homed on physics/contacts-triggers, the page of the item the rows name; also homed on animation/state-machines
- "`$ref`": homed on editor/command-scripts, the page of the item the rows name; also homed on input/actions
- "glyph": homed on gpu/text, the page of the item the rows name; also homed on editor-ui/design-system
- animation:536 joins foundation:638 (basics-b.md:369)
- animation:554 joins render-scene:640 (draw.md:1044)
- assets:660 joins foundation:551 (assets.md:1152)
- assets:682 joins render-core:699 (assets.md:1153)
- assets:692 joins render-core:744 (assets.md:1154)
- assets:693 joins render-core:743 (assets.md:1155)
- assets:695 joins render-core:698 (assets.md:1157)
- assets:696 joins render-core:690 (assets.md:1158)
- assets:700 joins render-core:712 (assets.md:1159)
- assets:701 joins render-core:715 (assets.md:1160)
- assets:722 joins foundation:643 (assets.md:1163)
- assets:723 joins foundation:643 (assets.md:1163)
- assets:727 joins scene-ecs:663 (assets.md:1164)
- assets:731 joins foundation:628 (assets.md:1165)
- assets:733 joins editor-core:714 (assets.md:1166)
- assets:734 joins editor-core:713 (assets.md:1167)
- assets:735 joins foundation:561 (assets.md:1168)
- assets:736 joins foundation:549 (assets.md:1169)
- assets:737 joins foundation:565 (assets.md:1170)
- audio-input:633 joins foundation:600 (core.md:942)
- audio-input:690 joins foundation:572 (core.md:522)
- audio-input:692 joins scripting:590 (scripting.md:744)
- audio-input:693 joins scripting:567 (scripting.md:214)
- automation:705 joins editor-core:651 (automation.md:614)
- automation:707 joins editor-core:652 (automation.md:615)
- automation:708 joins editor-core:654 (automation.md:615)
- automation:709 joins editor-core:657 (automation.md:616)
- automation:710 joins editor-core:659 (automation.md:616)
- automation:711 joins editor-core:662 (automation.md:617)
- automation:713 joins editor-core:664 (automation.md:618)
- automation:729 joins editor-core:653 (automation.md:621)
- automation:730 joins editor-core:666 (automation.md:621)
- automation:738 joins foundation:588 (automation.md:622)
- automation:739 joins assets:668 (assets.md:597)
- automation:759 joins foundation:630 (automation.md:626)
- automation:760 joins foundation:629 (automation.md:626)
- automation:767 joins foundation:626 (automation.md:627)
- automation:780 joins editor-core:668 (automation.md:629)
- automation:781 joins editor-core:669 (automation.md:629)
- automation:783 joins editor-core:670 (automation.md:631)
- automation:785 joins editor-core:688 (automation.md:633)
- automation:786 joins foundation:572 (automation.md:634)
- build-test:644 joins render-core:721 (gpu.md:258)
- build-test:645 joins render-core:720 (gpu.md:258)
- build-test:647 joins render-core:682 (gpu.md:163)
- build-test:648 joins render-core:724 (gpu.md:962)
- build-test:651 joins foundation:558 (core.md:45)
- build-test:654 joins foundation:549 (core.md:834)
- build-test:668 joins render-core:691 (gpu.md:167)
- build-test:669 joins render-core:758 (gpu.md:1047)
- build-test:670 joins foundation:583 (core.md:339)
- editor-core:685 joins scene-ecs:626 (world.md:233)
- editor-core:686 joins scene-ecs:621 (world.md:120)
- editor-core:691 joins foundation:572 (core.md:522)
- editor-core:692 joins foundation:575 (core.md:523)
- editor-core:694 joins editor-ui:763 (editor.md:774)
- editor-core:697 joins render-direct:756 (light.md:615)
- editor-core:699 joins audio-input:688 (audio-input.md:999)
- editor-core:702 joins foundation:628 (core.md:1132)
- editor-core:715 joins scene-ecs:666 (world.md:740)
- editor-core:716 joins scene-ecs:666 (world.md:740)
- editor-core:717 joins scene-ecs:666 (world.md:740)
- editor-core:718 joins scene-ecs:666 (world.md:740)
- editor-core:719 joins scene-ecs:666 (world.md:740)
- editor-core:720 joins scene-ecs:666 (world.md:740)
- editor-core:725 joins physics:520 (physics.md:650)
- editor-core:726 joins render-scene:597 (draw.md:238)
- editor-core:733 joins foundation:634 (basics-b.md:289)
- editor-core:737 joins render-core:758 (gpu.md:1046)
- editor-core:738 joins editor-ui:748 (editor-ui.md:965)
- editor-core:739 joins foundation:583 (core.md:340)
- editor-ui:716 joins render-core:768 (gpu.md:1197)
- editor-ui:721 joins gameui:624 (core.md:608)
- editor-ui:747 joins editor-core:650 (editor.md:56)
- editor-ui:755 joins scene-ecs:649 (world.md:555)
- editor-ui:756 joins scene-ecs:649 (world.md:555)
- editor-ui:759 joins scene-ecs:666 (world.md:740)
- editor-ui:763 joins editor-core:694 (editor.md:775)
- editor-ui:777 joins audio-input:670 (audio-input.md:684)
- editor-ui:779 joins foundation:582 (core.md:415)
- editor-ui:782 joins audio-input:686 (audio-input.md:931)
- editor-ui:786 joins render-core:704 (gpu.md:779)
- editor-ui:787 joins render-core:698 (gpu.md:57)
- editor-ui:788 joins render-core:699 (gpu.md:56)
- editor-ui:789 joins render-core:707 (gpu.md:779)
- editor-ui:791 joins render-core:683 (gpu.md:164)
- foundation:576 joins scene-ecs:679 (world.md:447)
- foundation:581 joins render-core:696 (gpu.md:54)
- foundation:587 joins audio-input:655 (audio-input.md:527)
- foundation:610 joins render-core:759 (gpu.md:1049)
- foundation:618 joins build-test:629 (engineering.md:317)
- foundation:633 joins render-core:728 (basics-b.md:286)
- foundation:635 joins render-core:731 (gpu.md:397)
- foundation:637 joins render-scene:594 (basics-b.md:453)
- foundation:641 joins build-test:629 (engineering.md:317)
- foundation:642 joins scene-ecs:621 (world.md:120)
- foundation:644 joins render-scene:581 (draw.md:406)
- foundation:645 joins render-core:749 (gpu.md:865)
- gamedev:607 joins scripting:590 (scripting.md:743)
- gameui:638 joins scene-ecs:631 (ui.md:695)
- gameui:640 joins scene-ecs:622 (ui.md:696)
- gameui:641 joins scene-ecs:623 (ui.md:697)
- gameui:644 joins render-core:766 (ui.md:698)
- gameui:645 joins render-core:762 (gpu.md:1196)
- gameui:646 joins render-core:767 (ui.md:700)
- gameui:647 joins render-core:768 (ui.md:701)
- gameui:653 joins render-core:712 (ui.md:702)
- gameui:655 joins render-core:707 (ui.md:703)
- gameui:661 joins render-core:730 (ui.md:705)
- gameui:662 joins render-core:741 (ui.md:706)
- gameui:668 joins audio-input:691 (ui.md:707)
- gameui:674 joins audio-input:684 (ui.md:708)
- gameui:675 joins audio-input:663 (ui.md:709)
- gameui:676 joins audio-input:677 (ui.md:710)
- gameui:681 joins scene-ecs:645 (ui.md:712)
- gameui:682 joins scene-ecs:641 (ui.md:713)
- gameui:683 joins scene-ecs:635 (ui.md:714)
- physics:493 joins foundation:572 (physics.md:926)
- physics:494 joins foundation:573 (physics.md:926)
- physics:495 joins foundation:574 (physics.md:926)
- physics:496 joins foundation:575 (physics.md:926)
- physics:501 joins foundation:637 (physics.md:927)
- physics:526 joins scene-ecs:622 (physics.md:929)
- physics:534 joins scene-ecs:679 (physics.md:930)
- physics:535 joins scene-ecs:680 (physics.md:930)
- physics:536 joins scene-ecs:681 (physics.md:930)
- physics:537 joins scene-ecs:682 (physics.md:930)
- render-core:728 joins foundation:633 (basics-b.md:287)
- render-core:730 joins foundation:634 (basics-b.md:289)
- render-core:738 joins render-scene:643 (draw.md:577)
- render-core:739 joins render-scene:645 (draw.md:577)
- render-core:741 joins render-scene:647 (draw.md:577)
- render-core:751 joins render-scene:573 (draw.md:146)
- render-core:752 joins render-scene:575 (draw.md:402)
- render-core:753 joins render-scene:583 (draw.md:403)
- render-core:757 joins render-direct:703 (basics-b.md:696)
- render-core:773 joins editor-ui:772 (editor-ui.md:793)
- render-direct:682 joins render-indirect:580 (indirect.md:174)
- render-direct:689 joins render-indirect:590 (indirect.md:178)
- render-direct:703 joins render-image:638 (basics-b.md:694)
- render-direct:716 joins foundation:634 (basics-b.md:289)
- render-direct:734 joins render-image:721 (basics-b.md:873)
- render-direct:758 joins render-core:760 (gpu.md:1048)
- render-image:654 joins render-core:758 (gpu.md:1046)
- render-image:702 joins render-scene:648 (draw.md:1122)
- render-image:703 joins render-scene:649 (draw.md:1122)
- render-image:725 joins render-core:707 (gpu.md:787)
- render-image:726 joins render-core:711 (gpu.md:788)
- render-indirect:566 joins render-direct:742 (indirect.md:1079)
- render-indirect:569 joins assets:702 (indirect.md:1080)
- render-indirect:573 joins render-direct:695 (indirect.md:1083)
- render-indirect:574 joins render-direct:681 (indirect.md:1084)
- render-indirect:575 joins render-direct:671 (indirect.md:1085)
- render-indirect:576 joins render-direct:679 (indirect.md:1086)
- render-indirect:577 joins render-direct:678 (indirect.md:1087)
- render-indirect:579 joins render-direct:677 (indirect.md:1089)
- render-indirect:581 joins render-direct:683 (indirect.md:1090)
- render-indirect:588 joins render-direct:686 (indirect.md:1094)
- render-indirect:589 joins render-direct:687 (indirect.md:1095)
- render-indirect:594 joins render-direct:737 (indirect.md:1096)
- render-indirect:595 joins render-scene:605 (indirect.md:1097)
- render-indirect:606 joins render-direct:702 (indirect.md:1098)
- render-indirect:619 joins render-image:700 (indirect.md:1103)
- render-indirect:620 joins render-image:702 (indirect.md:1104)
- render-indirect:648 joins render-image:736 (indirect.md:1105)
- render-indirect:650 joins render-direct:755 (indirect.md:1107)
- render-scene:606 joins render-core:733 (gpu.md:961)
- render-scene:607 joins render-core:733 (gpu.md:961)
- render-scene:608 joins foundation:634 (basics-b.md:289)
- render-scene:620 joins render-core:743 (gpu.md:689)
- render-scene:627 joins render-core:758 (gpu.md:1046)
- render-scene:637 joins animation:532 (animation.md:273)
- render-scene:638 joins animation:552 (animation.md:273)
- render-scene:639 joins animation:549 (animation.md:273)
- render-scene:642 joins animation:577 (animation.md:831)
- scene-ecs:629 joins foundation:640 (basics-b.md:136)
- scene-ecs:646 joins foundation:565 (core.md:717)
- scene-ecs:647 joins foundation:549 (core.md:813)
- scene-ecs:648 joins foundation:558 (core.md:44)
- scene-ecs:664 joins foundation:643 (basics-a.md:1207)
- scene-ecs:684 joins animation:537 (basics-b.md:371)
- scene-ecs:691 joins physics:517 (physics.md:516)
- scripting:565 joins assets:683 (assets.md:692)
- scripting:566 joins audio-input:686 (audio-input.md:931)
- scripting:578 joins foundation:612 (core.md:102)
- scripting:579 joins scene-ecs:682 (world.md:447)
- scripting:580 joins foundation:565 (core.md:717)
- scripting:606 joins scene-ecs:645 (world.md:347)
- scripting:617 joins foundation:577 (core.md:524)
- scripting:618 joins physics:485 (physics.md:586)
- worlds-runtime:524 joins audio-input:677 (audio-input.md:746)
- worlds-runtime:538 joins physics:530 (physics.md:799)
- worlds-runtime:539 joins physics:530 (physics.md:799)
- worlds-runtime:546 joins render-core:742 (draw.md:579)
- worlds-runtime:557 joins foundation:583 (core.md:341)
- worlds-runtime:563 joins foundation:575 (core.md:523)
- worlds-runtime:564 joins foundation:572 (core.md:522)
- worlds-runtime:566 joins editor-ui:745 (editor-ui.md:1047)

## Use homes

- "ABI": home scripting/shared-libraries, use make/script-builds
- "Activity journal": home editor/journal, use make/automated-playtests
- "Animator": home animation/importing, use make/animation
- "Asset handle": home assets/handles-meta, use make/assets
- "Binding capture": home input/rebinding, use make/menus
- "CMake": gamedev:611 homes it on start/install, a first use (book.md): the home is basics/build
- "Candela": home light/units-exposure, use make/lighting
- "Canvas": home ui/what-game-ui-does, use make/hud
- "Character controller": home physics/character-controllers, use make/characters-cameras
- "Collider": home physics/bodies-colliders, use make/physics
- "Collision layer": home physics/collision-layers, use make/physics
- "Command script": home editor/command-scripts, use make/automated-playtests
- "Command": home editor/commands, use make/automated-playtests
- "Composite": home input/actions, use make/input
- "Cross-fade": home animation/blending, use make/animation
- "Dead zone": home input/gamepads, use make/input
- "Event target": home ui/input, use make/menus
- "Game identity": home worlds/game-identity, use make/export
- "Game view": gamedev:595 homes it on start/first-game, a first use (book.md): the home is editor/play-mode
- "Headless": home core/first-frame, use make/export
- "Import settings": home assets/importing, use make/assets
- "Import": home assets/what-is-an-asset, use make/assets
- "Input action": home input/actions, use make/input
- "Input sequence": home editor/stepping, use make/automated-playtests
- "Launcher": gamedev:572 homes it on start/first-game, a first use (book.md): the home is editor-ui/launcher-dialogs
- "Loading scene": home worlds/runtime, use make/export
- "Lux": home light/units-exposure, use make/lighting
- "One-shot": home audio/engine, use make/sound
- "Outdated instance": home editor/prefab-instances, use make/prefabs
- "Play": home editor/play-mode, use make/play-test-debug
- "Preset": gamedev:611 homes it on start/install, a first use (book.md): the home is engineering/building
- "Preview lighting": home light/lights, use make/lighting
- "Raycast": home physics/queries, use make/physics
- "Recovery journal": home editor/recovery, use make/project-files
- "Reference resolution": home ui/layout, use make/hud
- "Reflection probe": home indirect/probes, use make/reflections
- "Replay": home draw/asset-requests, use make/automated-playtests
- "Revert": home world/prefabs, use make/prefabs
- "Rigid body": home physics/bodies-colliders, use make/physics
- "Root motion": home animation/root-motion, use make/animation
- "SDK": home scripting/abi-sdk, use make/first-script
- "Scene view": gamedev:595 homes it on start/first-game, a first use (book.md): the home is editor-ui/scene-view
- "Simulated input": home input/simulated, use make/automated-playtests
- "Start scene": home worlds/runtime, use make/export
- "State": home animation/state-machines, use make/animation
- "Sub-asset": home assets/handles-meta, use make/assets
- "Sub-scene": home world/sub-scenes, use make/levels-saves
- "Template": gamedev:574 homes it on start/first-game, a first use (book.md): the home is editor/projects
- "Time scale": home core/time, use make/script-loop
- "Trigger": home physics/contacts-triggers, use make/physics
- "Unpack": home world/prefabs, use make/prefabs
- "`$ref`": home editor/command-scripts, use make/input
- "accumulator": home core/time, use make/script-loop
- "asset": home start/what-an-engine-is, use make/editor-tour
- "callback": home basics/cpp-generic, use make/script-loop
- "component": gamedev:579 homes it on start/first-game, a first use (book.md): the home is world/ecs
- "delta time": gamedev:614 homes it on start/what-an-engine-is, a first use (book.md): the home is core/time
- "entity": gamedev:578 homes it on start/first-game, a first use (book.md): the home is world/ecs
- "export": home start/what-an-engine-is, use make/export
- "fixed step": home core/time, use make/script-loop
- "frame": foundation:569 homes it on start/what-an-engine-is, a first use (book.md): the home is core/frame-loop
- "frame": gamedev:614 homes it on start/what-an-engine-is, a first use (book.md): the home is core/frame-loop
- "interpolation": home world/interpolation, use make/characters-cameras
- "overlap": home indirect/gi-cascades, use make/physics
- "parameter": home basics/programming-2, use make/animation
- "quaternion": home basics/math-rotations, use make/transforms-units
- "scene": gamedev:576 homes it on start/first-game, a first use (book.md): the home is make/scenes-entities
- "script class": gamedev:604 homes it on start/first-game, a first use (book.md): the home is make/first-script
- "script module": gamedev:604 homes it on start/first-game, a first use (book.md): the home is make/first-script
- "seed": home basics/math-probability, use make/recipes
- "step alpha": home world/interpolation, use make/characters-cameras
- "time dilation": home core/time, use make/script-loop
- "transform": home basics/math-matrices, use make/scenes-entities
- "unscaled time": home core/time, use make/timers-events

## The seed and the glossary

- "component" of the seed joins the glossary's "component"
- "entity" of the seed joins the glossary's "entity"
- "frame rate" of the seed joins the glossary's "frame rate"
- "frame" of the seed joins the glossary's "frame"
- "interpolation" of the seed joins the glossary's "interpolation"
- "scene" of the seed joins the glossary's "scene"
- animation:561 "Condition" (row home animation/state-machines) keeps the seed's home basics/programming-1
- animation:562 "Parameter" (row home animation/state-machines) keeps the seed's home basics/programming-2
- assets:637 "Asset" (row home assets/what-is-an-asset) keeps the seed's home start/what-an-engine-is
- assets:640 "Source file" (row home assets/what-is-an-asset) keeps the seed's home basics/programming-3
- assets:672 "Hot reload" (row home assets/importing) keeps the glossary's home make/first-script
- audio-input:607 "Sample rate" (row home audio/sound-in-a-computer) keeps the seed's home basics/signals
- audio-input:623 "Decibel" (row home audio/sound-in-a-computer) keeps the seed's home basics/numbers
- audio-input:632 "Lock-free" (row home audio/engine) keeps the seed's home basics/threads
- audio-input:673 "Axis" (row home input/gamepads) keeps the seed's home basics/math-matrices
- build-test:687 "Matrix" (row home engineering/ci) keeps the seed's home basics/math-matrices
- editor-core:669 "Origin" (row home editor/journal) keeps the seed's home basics/math-vectors
- editor-core:686 "UUID" (row home world/ecs) keeps the seed's home basics/data-formats
- foundation:569 "Frame" (row home start/what-an-engine-is) keeps the glossary's home core/frame-loop
- foundation:570 "Frame loop" (row home core/frame-loop) keeps the seed's home start/what-an-engine-is
- foundation:588 "Main thread" (row home core/frame-loop) keeps the seed's home basics/threads
- foundation:590 "Thread pool" (row home core/jobs) keeps the seed's home basics/threads
- foundation:591 "Job" (row home core/jobs) keeps the seed's home basics/threads
- foundation:636 "Frustum" (row home draw/bounds-culling) keeps the seed's home basics/math-projection
- foundation:642 "UUID" (row home world/ecs) keeps the seed's home basics/data-formats
- gamedev:576 "Scene" (row home start/first-game) keeps the glossary's home make/scenes-entities
- gamedev:578 "Entity" (row home start/first-game) keeps the glossary's home world/ecs
- gamedev:579 "Component" (row home start/first-game) keeps the glossary's home world/ecs
- gamedev:604 "script class" (row home start/first-game) keeps the glossary's home make/first-script
- gamedev:604 "script module" (row home start/first-game) keeps the glossary's home make/first-script
- gamedev:611 "CMake" (row home start/install) keeps the seed's home basics/build
- gamedev:614 "Frame" (row home start/what-an-engine-is) keeps the glossary's home core/frame-loop
- gamedev:614 "delta time" (row home start/what-an-engine-is) keeps the glossary's home core/time
- render-core:679 "GPU" (row home gpu/how-a-gpu-frame-works) keeps the seed's home start/install
- render-core:688 "Queue" (row home gpu/how-a-gpu-frame-works) keeps the seed's home basics/data-structures
- render-core:718 "Shader" (row home gpu/how-a-gpu-frame-works) keeps the seed's home start/what-an-engine-is
- render-core:726 "Derivative" (row home gpu/shaders) keeps the seed's home basics/math-change
- render-core:754 "HDR" (row home image/why-post) keeps the seed's home basics/color
- render-core:762 "code point" (row home gpu/text) keeps the seed's home basics/bytes
- render-image:636 "Scene-linear" (row home image/why-post) keeps the seed's home basics/color
- render-image:676 "Banding" (row home image/encoding) keeps the seed's home basics/color
- render-indirect:609 "Depth buffer" (row home gpu/coordinates) keeps the seed's home basics/math-projection
- render-scene:626 "Overflow" (row home draw/gpu-driven) keeps the seed's home basics/numbers
- scene-ecs:611 "Entity" (row home world/what-a-world-is) keeps the glossary's home world/ecs
- scene-ecs:613 "Component" (row home world/what-a-world-is) keeps the glossary's home world/ecs
- scene-ecs:618 "Storage" (row home world/ecs) keeps the seed's home basics/computer
- scene-ecs:621 "UUID" (row home world/ecs) keeps the seed's home basics/data-formats
- scene-ecs:622 "Signal" (row home world/scene-graph) keeps the seed's home basics/signals
- scene-ecs:624 "Scene" (row home world/what-a-world-is) keeps the glossary's home make/scenes-entities
- scene-ecs:685 "Project" (row home world/projects-settings) keeps the seed's home start/first-game
- scene-ecs:691 "matrix" (row home physics/collision-layers) keeps the seed's home basics/math-matrices
- scripting:591 "Hot reload" (row home scripting/hot-reload) keeps the glossary's home make/first-script
- scripting:596 "script module" (row home scripting/shared-libraries) keeps the glossary's home make/first-script
- scripting:609 "Signal" (row home core/platform) keeps the seed's home basics/signals
- worlds-runtime:548 "Export" (row home worlds/export) keeps the seed's home start/what-an-engine-is
- worlds-runtime:556 "Runtime" (row home worlds/runtime) keeps the seed's home start/what-an-engine-is

## Aliases dropped

- ".stgame" of "Game manifest": a name of "Manifest" or an avoid name
- ".stpak" of "pack": a name of "Asset pack" or an avoid name
- "Simulate mode" of "Play mode": a name of "Simulate mode" or an avoid name
- "SoA" of "Structure of arrays": a name of "struct of arrays" or an avoid name
- "descriptor" of "Panel": a name of "Descriptor" or an avoid name
- "engine service" of "Service": a name of "Scene service" or an avoid name
- "front face" of "Winding": a name of "Winding order" or an avoid name
- "layer matrix" of "Collision layer": a name of "layer matrix" or an avoid name
- "local space" of "World (editor-ui)": a name of "local space" or an avoid name
- "mip chain" of "Mip": a name of "Mip chain" or an avoid name
- "prefix" of "Install tree": a name of "Partial load" or an avoid name
- "readback" of "Picking": a name of "Readback" or an avoid name
- "stderr" of "stdio": a name of "standard error" or an avoid name
- "stdin" of "stdio": a name of "standard input" or an avoid name
- "stdout" of "stdio": a name of "standard output" or an avoid name

## Names not made aliases: one everyday word of tools/data/common-words.txt, which would make the lint mark its everyday uses

- "Apply" of "Prefab (make)"
- "Apply" of "Prefab (world)"
- "Binding" of "`$ref`"
- "Compose" of "Blend"
- "Exact" of "Blend"
- "Instance" of "Prefab (world)"
- "Key" of "keyframe"
- "Layer" of "Layer table"
- "Override" of "Prefab (world)"
- "Palette" of "skinning palette"
- "Pause" of "Play"
- "Requires" of "Requirement"
- "Shaping" of "Text shaping"
- "Simulate" of "Play"
- "Spatial" of "Checkerboard"
- "Step" of "Play"
- "action" of "Undo step"
- "anchor" of "Range selection"
- "arrange" of "Measure"
- "assertions" of "assertion"
- "batch" of "Draw run"
- "binding" of "`$ref`"
- "break" of "Teleport"
- "bullet" of "Continuous collision (CCD)"
- "cap" of "frame-rate cap"
- "clip" of "Discard"
- "cooked" of "Cook"
- "cycles" of "cycle"
- "demand" of "Capacity"
- "diagnostics" of "diagnostic"
- "distance" of "Attenuation color"
- "export" of "Replay script"
- "fibers" of "fiber"
- "ghost" of "Lens flare"
- "group" of "Bus"
- "halo" of "Lens flare"
- "halving" of "bisection"
- "history" of "Undo stack"
- "hitches" of "hitch"
- "indices" of "Endpoints"
- "instance" of "Prefab (make)"
- "knob" of "Quality preset"
- "legend" of "Debug view (editor-ui)"
- "mask" of "Clip rect"
- "migration" of "project migration"
- "mirror" of "GPU copy"
- "mount" of "Patch pack"
- "offset" of "Slope"
- "operator" of "tone mapping (image)"
- "overflow" of "Ellipsis"
- "overlap" of "Raycast"
- "override" of "Prefab (make)"
- "palette" of "Token"
- "partitions" of "Endpoints"
- "path" of "Channel (animation)"
- "priorities" of "Priority (jobs)"
- "pyramid" of "Mip chain"
- "registers" of "register"
- "relevancy" of "interest management"
- "room" of "Capacity"
- "row" of "Quality preset"
- "scissor" of "Clip rectangle"
- "score" of "Priority"
- "seams" of "seam"
- "sensor" of "Trigger"
- "shape" of "Collider"
- "shininess" of "specular power"
- "shoulder" of "Toe"
- "sinks" of "sink"
- "slabs" of "slab"
- "slot" of "Bindless"
- "slot" of "Body record"
- "source" of "origin"
- "stop" of "Exposure"
- "sweep" of "Settle scene"
- "symbols" of "symbol"
- "trail" of "Ghosting"
- "trails" of "trail"
- "tunnelling" of "Continuous collision (CCD)"
- "velocity" of "Motion vector"
- "watch" of "Contact interest"
- "weight" of "Influence"
