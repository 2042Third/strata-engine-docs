# Brief: `animation/limits`

| Field | Value |
| --- | --- |
| Title | What Strata's animation does not do yet |
| Kind | C |
| Size | S |
| Tracks | E |
| Needs | `animation/system` |
| From | animation ch. 16; 1.16 (blend trees, layers, sync markers, IK, morph targets, clip compression, compute skinning) and how other engines provide them |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/limits` — What Strata's animation does not do yet

**Covers.** The problem as a reader meets it: someone who comes from another engine looks for a blend tree, an IK
foot or a facial blend shape and does not find one. Each absence gets one paragraph, in the order of the pages that
would hold it: what Strata does not have, how engines usually do it (with a source in Further reading), and what
Strata offers instead. Blend trees and blend spaces, animation layers and masks (Strata offers cross-fades of up to
four entries); additive clips, sync markers and phase matching, float curves, inertialization and motion matching (the
robot's walk-to-run slide is the example); IK, and ragdolls, for which physics has no joints (`physics/why`); morph
targets (the importer reports them skipped, and the robot's faces are not imported); clip compression (Strata has
keyframe reduction and shared key times); retargeting beyond matching joint names; compute skinning and dual-quaternion
skinning (linear blend skinning runs per draw in the vertex shader); a skeleton overlay in the viewport (only the Asset
tab's joint tree shows joints). What the engine's documents plan is quoted only from the Roadmap's wave 9 entries
(`Docs/Roadmap.md:1645-1653`: `animation-tools`, `animation-runtime-2` and the ragdoll nodes), never from its tranche 2
line on `animation-graph` (`:1616-1620`), and never as a date or a promise; the writer runs each entry's evidence again
at the pin. The page's example is the design exercise E8: an Additive flag for states, its reference pose, and where it
would enter `Evaluate`; an editor task comes before it: the importer's report of the morph targets it skips. The page
links `appendix/not-in-strata`. At the end the reader knows where Strata's animation
stops and what a game or an engine change would have to add.

**Leaves out.**

- The general techniques behind every absence of the engine, indexed → `appendix/not-in-strata`
- Joints and ragdolls as a physics absence → `physics/why`
- Creating an animation controller without a command → `make/animation`

**Fit.** `fits`: about 2,150 words against S (1,500). The eight absences, one paragraph each, take the most; the two
exercises take about 500, and the estimate is 100 words below S's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:52` | feature | home | No clip compression: raw float32 keys, reduction and shared times only |
| `animation:223` | feature | home | The list of what is not in Strata yet, and the Roadmap's wave 9 entries (`Docs/Roadmap.md:1645-1653`), quoted |
| `animation:505` | hands-on | home | E8 |
| `new:35` | hands-on | home | Editor task (done, track E), before E8: import a copy of the robot's model into the playground project, find in the **Console** the importer's warning "Not imported: morph targets" (the robot's faces), then find with a search the two lines that skip morph targets and their animation. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:283-284` (each skipped feature becomes a warning "Not imported: ..."), `:1378-1379`, `:1637-1640`; `Strata/src/Strata/Asset/EditorAssetManager.cpp:2274-2275` (import warnings are logged); `Samples/ThirdPerson/Assets/Models/Robot/RobotExpressive.glb` (its meshes carry morph targets) |
| `animation:641` | open | home | No bounds overlay or skeleton gizmo in the viewport; the search, run again at the pin, is `new:12` |
| `animation:650` | open | home | The animation graph: no code at the pin; the page quotes only the Roadmap's wave 9 entries (`Docs/Roadmap.md:1645-1653`), never the tranche 2 line (`:1616-1620`), which names a stream that left wave 8 (animation-q6; R32, D43) |
| `new:9` | not-done | home | Blend trees, animation layers, IK, morph targets, clip compression. Evidence: `Strata/src/Strata/Asset/GltfImporter.cpp:1031` (weight channels skipped), `:1379` and `:1639` (morph targets reported skipped); `Docs/Roadmap.md:1649-1652` (Blend2D, IK and compressed clips listed for wave 9); `git grep -niE "blend ?(tree\|space\|1d\|2d)\|\bik\b\|inverse kinematic\|compress\|mask" 822a7a46 -- Strata/src/Strata/Animation` finds nothing; `git grep -niE "layer"` there finds only a comment on the Scene layer (`AnimationComponents.cpp:32`) |
| `new:10` | not-done | home | Additive clips, sync markers, float curves, inertialization, motion matching. Evidence: `Docs/Roadmap.md:1647-1651`; `git grep -niE "additive\|sync ?mark\|curve\|inertiali\|motion matching" 822a7a46 -- Strata/src/Strata/Animation` finds nothing |
| `new:11` | not-done | home | Retargeting beyond matching joint names. Evidence: `Strata/src/Strata/Animation/AnimationClip.h:38` ("clips bind to skeletons by name"); `Strata/src/Strata/Animation/AnimationClip.cpp:438-457` (`Bind` looks each target up by name); `git grep -niE "retarget" 822a7a46 -- Strata/src/Strata/Animation` finds nothing |
| `new:12` | not-done | home | A skeleton overlay in the viewport (`book.md`, "What Strata does not do"; the search run again at 822a7a46). Evidence: `git grep -nilE "joint" 822a7a46 -- StrataEditor/src Strata/src/Strata/Renderer Strata/shaders` finds the Asset tab's joint and channel views, the animation commands, the editor's bounds code, the `AttachToJoint` entity icon and the skinning code, and other words (`JoinTypeNames` in `StrataEditor/src/Editor/EditorUICommands.cpp`, "disjoint" in `Strata/src/Strata/Renderer/GlobalIlluminationLayout.h` and `.cpp`); nothing draws joints in a view |
| `new:13` | not-done | home | Compute skinning and dual-quaternion skinning: skinning runs per draw in the vertex shader. Evidence: `Docs/Roadmap.md:675`; `git grep -niE "dual[ -]?quat" 822a7a46 -- Strata/src Strata/shaders` finds nothing |
| `animation:569-570` | term | link | Sync markers and inertialization, defined on `animation/blending` |
| `animation:545` | term | link | Clip compression, defined on `animation/clips` |
| `animation:550` | term | link | Dual quaternion skinning, defined on `animation/skinning` |
| `animation:589` | term | link | Morph target, defined on `animation/problem` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Animation system | `animation/system` | must |
| Cross-fades and blend weights | `animation/blending` | must |
| Linear blend skinning (the paragraph on compute and dual-quaternion skinning names it and links it) | `animation/skinning` | helps |
| Keyframe reduction and binding by name | `animation/clips` | must |
| Why games need physics (no joints) | `physics/why` | helps |
| Overlay passes and debug drawing | `gpu/debug-drawing` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
