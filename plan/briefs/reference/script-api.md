# Brief: `reference/script-api`

| Field | Value |
| --- | --- |
| Title | The complete script API |
| Kind | R |
| Size | XL |
| Tracks | - |
| Needs | `basics/programming-3` |
| From | scripting ch. 16; `StrataScriptHostAPI` and `StrataScriptClassDesc` (`ScriptABI.h`), the SDK headers of `StrataScriptCore/Include/StrataScript/`, `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`; `ST_SCRIPT_HOST_FUNCTIONS` is in the engine (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp`), not in the SDK |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/script-api` — The complete script API

**Covers.** The paragraph on top says what the page is: every name a game script can call, generated from the SDK's
headers and the C table at the pin, never typed. It says how to read the two layers: game code includes only
`StrataScript.h` and calls the C++ SDK; each SDK function wraps a member of `StrataScriptHostAPI`, the C table that
the engine fills. Then the generated tables, in this order. (1) The SDK by header, in the groups of the headers:
`Entity`, the `Component` proxy and `TransformComponent`; `Scene`, `Assets` and `SubScene`; `Input` with its `Key`
and `Mouse` enums, gamepads, actions and binding capture; `Time`; `Log`; `RigidBody`, `Physics`, `RaycastHit` and
`Collision`; `CharacterController` and `GroundState`; `AudioSource` and `Audio`; `Animator` and `JointTransform`;
`Game` and `WindowMode`; `Graphics`, `GraphicsOption` and `QualityPreset`; `UIElement`, `UI` and `UIAction`; `World`
and `WorldCellRequest`; the helpers of `Gameplay.h` (`Random`, `Timer`, `KeyRepeat`, `Motion`); `AssetHandle` and the
value traits. Each function shows its declaration, the `//` comment the header gives it (the SDKReader's rules), and the
host function it calls. (2) The `Script` base class: its 15 virtual callbacks in the order of `StrataScriptClassDesc`,
with when each runs, and `GetEntity` and `GetTransform`. (3) Script fields: `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and
the field types that `c_IsFieldType` accepts. (4) The host functions in declaration order, which is the ABI's append
order, grouped as the header comments group them, each with "added in" (the first release tag that contains the commit
that added it); the count is `:value{key="hostFunctions.count"}`. (5) The C types a module sees: the value types of
`StrataScriptValue`, `StrataScriptResult`, the frozen structs with their sizes, the extensible structs that start with
`StructSize`, and the enums. Hand-written around them: one sentence per SDK group naming the page that teaches it; one
note on failure values (an SDK function returns its failure value and does nothing when the running engine lacks the
host member, `ST_SCRIPT_DETAIL_HOST_WITH`); one note that `ST_SCRIPT_ABI_VERSION` stays 1 while functions are only
appended; one note that `ST_SCRIPT_HOST_FUNCTIONS` is the engine's list in `ScriptHostAPI.cpp`, not part of the SDK.
`## Where it lives in Strata`: `StrataScriptCore/Include/StrataScript/`, `ScriptABI.h`, `ScriptHostAPI.cpp`, the
feature test's SDK reader and `SDKCoverageTests.cpp`. The tool is `tools/reference.py`, route "script API". A reader
who arrives with a name finds its declaration, its comment, the host function behind it, the release it came in and
the page that teaches it.

**Leaves out.**

- Writing, attaching and building a first script → `make/first-script`
- When each callback runs within a frame, and the fixed step → `make/script-loop`
- How the SDK turns callbacks into C calls (thunks, override detection, self-registration, class records) →
  `scripting/abi-sdk`
- How the engine implements a host function (`HostCall`, `ResolveContext`, `ReportProblem`) → `scripting/host-api`
- Adding a host function or a callback → `scripting/tutorial-host-function`
- Building and shipping a module (`strata_add_script_module`) → `make/script-builds`
- Which release brought each group, as a history → `appendix/history`

**Fit.** `fits`: about 2,250 words against XL (8,000). The generated tables give the page its size: about 165
host-function rows and some 500 SDK declarations with their comments, roughly 10,000 words. The prose is the paragraph
on top (400 words), one sentence for each of the 15 SDK groups and the 27 groups of host functions (1,250), four section
introductions and four notes (500) and the strip (100).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:706` | open | home | The count of host functions, confirmed by the generated table (`hostFunctions.count`; 165 members between `ScriptABI.h:312` and `:756` at the pin, the same number that `ST_SCRIPT_HOST_FUNCTIONS` lists) |
| `scripting:38-39` | feature | link | The two entry points a module exports and `ST_SCRIPT_ABI_VERSION`, in the note on the ABI version |
| `scripting:42-51` | feature | link | Size-prefixed structs, handles, strings, results, the value types, transforms, frozen and extensible structs and the enums, as the table of C types |
| `scripting:53-57` | feature | link | The host table, the buffer protocol of text and array functions, and the field, class and module descriptors |
| `scripting:63-90` | feature | link | The 27 groups of host functions, one introduction each with the page that teaches the group |
| `scripting:92` | feature | link | The 15 class callbacks and their order |
| `scripting:102` | feature | link | `StrataScript.h`, the one header game code includes |
| `scripting:104` | feature | use | Graceful degradation, used in the note on failure values |
| `scripting:105` | feature | link | The `Script` base class, its callbacks, `GetEntity` and `GetTransform` |
| `scripting:113-117` | feature | link | `ScriptClassBuilder`, the field macros, the field types, the value traits and `AssetHandle` |
| `scripting:118-121` | feature | link | `Entity`, the `Component` proxy, `TransformComponent`, `Scene`, `Assets` and `SubScene` as generated rows (every function with its declaration, comment, host function and failure value), linked to `make/scripting-scene`, which teaches them |
| `scripting:122` | feature | link | `Input` with its `Key` and `Mouse` enums, gamepads, actions and binding capture, as generated rows, linked to `input/devices-state` |
| `scripting:123` | feature | link | `Time`, as generated rows, linked to `make/timers-events` |
| `scripting:124` | feature | link | `Log`, as generated rows, linked to `basics/programming-1` |
| `scripting:125-126` | feature | link | `RigidBody`, `Physics`, `RaycastHit`, `Collision`, `CharacterController` and `GroundState`, as generated rows, linked to `physics/world-step` |
| `scripting:127` | feature | link | `AudioSource` and `Audio`, as generated rows, linked to `audio/scene-system` |
| `scripting:128` | feature | link | `Animator` and `JointTransform`, as generated rows, linked to `make/animation` |
| `scripting:129` | feature | link | `Game` and `WindowMode`, as generated rows, linked to `make/levels-saves` |
| `scripting:130` | feature | link | `Graphics`, `GraphicsOption` and `QualityPreset`, linked to `image/quality-settings` |
| `scripting:131` | feature | link | `UIElement`, `UI` and `UIAction`, as generated rows, linked to `ui/input` |
| `scripting:132` | feature | link | `World` and `WorldCellRequest`, linked to `worlds/physics-scripts` |
| `scripting:133` | feature | link | `Random`, as generated rows, linked to `make/recipes`; the sentence of the `Gameplay.h` group also links `scripting/abi-sdk`, which says why its helpers live in the module |
| `scripting:134-135` | feature | link | `Timer` and `KeyRepeat`, as generated rows, linked to `make/timers-events` |
| `scripting:136` | feature | link | `Motion`, as generated rows, linked to `make/gameplay-math` |
| `physics:177` | feature | link | The physics host functions and SDK classes, linked to the physics part |
| `audio-input:94-96` | feature | link | `AudioSource`, `Audio` and their host functions |
| `audio-input:173-176` | feature | link | `Input`, `KeyRepeat`, the input part of the ABI and its host functions |
| `animation:176-178` | feature | link | The animator host functions, `Animator` and `OnAnimationEvent` |
| `gameui:203-204` | feature | link | The UI host functions and the four UI callbacks, read only when `StructSize` covers them |
| `gameui:206` | feature | link | `UIElement`, `UI` and `UIAction` |
| `worlds-runtime:89-93` | feature | link | `World`, its host functions, and the window, graphics and scene-load calls of the worlds part |
| `render-image:250` | feature | link | The `Graphics` SDK of players' graphics options |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Reading a C++ declaration: types, functions, classes and their members | `basics/programming-3` | must |
| References and `const` in parameters | `basics/cpp-memory` | helps |
| What a script is and when its callbacks run | `make/script-loop` | helps |
| The script system and the dispatch of callbacks | `scripting/script-system` | helps |
| The host API: engine services behind a C table | `scripting/host-api` | helps |
| The ABI, appending and structs that start with their size | `scripting/abi-sdk` | helps |
| Entities, components and their registered names | `world/ecs` | helps |
| Asset handles | `assets/handles-meta` | helps |
| Vectors and quaternions | `basics/math-rotations` | helps |
| The fixed step and time scale | `core/time` | helps |

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
| critic-reference-8 | should | missing-item | new items on `reference/assets`, `reference/renderer`, `reference/script-api` | The other area pages have a parsed table of limits, and `appendix/not-in-strata` sends "caps and limits of the features Strata has" to `reference/renderer`, but these three pages have none. Unlisted at the pin: a texture's longest side of 16,384 texels and 2^28 decoded pixels, a glTF scale of at most 10,000, 8 levels of detail, a hierarchy depth of 1,024 and a 64 MiB document, 4,096 joints per mesh, built-in handles 1 to 255; 32,768 bindless textures, 256 GPU timestamps a frame, a 2 GiB geometry pool, the draw key's submesh and LOD bits, 8,192-texel cascades, the font limits; save file names of 64 characters and files of 64 MiB, 65,536 script classes, 4,096 fields a class, names of 1,024 bytes and strings of 256 MiB. | Each of the three pages adds a parsed limits table through `tools/reference-limits.json`, as `reference/physics` and `reference/ui` have, with one introduction that names the teaching page. About 40 words each. | `allocation/reference.md:385-406`, `:460-485`, `:5-28`; `allocation/appendix.md:48`; `Strata/src/Strata/Asset/TextureImporter.h:84`; `Strata/src/Strata/Asset/TextureImporter.cpp:24`; `Strata/src/Strata/Asset/GltfImporter.cpp:68-74`; `Strata/src/Strata/Asset/GltfImporter.h:54`; `Strata/src/Strata/Renderer/Mesh.h:46`; `Strata/src/Strata/Asset/Asset.h:36`; `Strata/src/Strata/Renderer/GraphicsDevice.h:135`; `Strata/src/Strata/Renderer/GPUProfiler.h:95`; `Strata/src/Strata/Renderer/GeometryPool.h:87`; `Strata/src/Strata/Renderer/SceneDrawKey.h:28-29`; `Strata/src/Strata/Renderer/RendererQuality.h:191`; `Strata/src/Strata/Renderer/FontValidation.h:47-58`; `Strata/src/Strata/Core/SaveFiles.h:23-24`; `Strata/src/Strata/Scripting/ScriptModule.cpp:55-57`, `:957`, `:1046`; `Strata/src/Strata/Scripting/ScriptValue.h:17` |
| critic-reference-15 | could | missing-item | `reference/script-api` | The route parses the two C structs, the SDK and the macros `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` only. The other public macros of `ScriptABI.h` (`ST_SCRIPT_EXPORT`, the entry-point names `ST_SCRIPT_GET_ABI_VERSION_SYMBOL` and `ST_SCRIPT_LOAD_SYMBOL`, `ST_SCRIPT_HAS_MEMBER`, `ST_SCRIPT_ABORT_EXCEPTION_CODE`) and the SDK's CMake package (`find_package(StrataScriptCore)`, `strata_add_script_module` with `SOURCE_DIR`, `SOURCES`, `OUTPUT_NAME`, `OUTPUT_DIRECTORY` and `NO_SDK_ENTRY`) are on no reference page. | The route also parses the `#define`s of `ScriptABI.h` with their comments, as a sixth table; a hand-checked table gives `strata_add_script_module`'s arguments and the module's file name on each system, checked against `StrataScriptModule.cmake`, naming `make/script-builds` and `scripting/abi-sdk`. About 100 words. | `allocation/reference.md:15-24`, `:38`; `../pipelines.md:1096`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:33-68`; `StrataScriptCore/CMake/StrataScriptModule.cmake:1-17` |
