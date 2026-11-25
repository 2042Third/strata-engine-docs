# Inventory: Scripting (game code in C++ behind a C ABI)

Surveyed at `main` 822a7a46. Paths are relative to the repository root `G:/GameEngineAI`. Line numbers are at this
commit. "DG" is `Docs/DeveloperGuide.md`, "ARCH" is `Docs/Architecture.md`, "MAN" is `Docs/Manual/Scripting.md`,
"SKILL" is `.claude/skills/strata-scripting/SKILL.md`.

Document sections used (heading, line):

- DG "Scripting" 1850; "Gameplay API" 1867; "ABI rules" 1972; "Adding a host function" 1997; "Building and loading
  scripts" 2018; "The editor's script engine" 2081; "Scripts of exported games" 2103; "Hosting modules and hot reload"
  2114; "Crash locations and containment" 2133 (ends at 2163). Related: "Script modules and package tests" 883, "Input
  actions" 1442, "Scripts through commands" 3135, "Quality settings" 4009.
- ARCH "Scripting" 3133-3216 (the layer diagram is at 3138-3146).
- MAN headings: Create a script 9, Attach it and play 55, When the build fails 66, Your code editor 74, IntelliSense 94,
  Input actions and rebinding 109, Graphics options 136, Following moving things 157, Hot reload 177, When a script
  crashes 183, Debugging with a debugger 200, Where builds happen 208.
- SKILL: A script class 20, Lifecycle 79, API cheat sheet 103, Gameplay API 165 (Physics 167, Character controllers
  228, Contacts 252, Audio 272, Animation 285, Game UI 322, Game flow 380, Streaming 394, Gamepads and the cursor 435,
  Input actions 455, Graphics options 489, Window and save files 517, Building blocks 537, Recipes 555), Rules 648,
  Workflow through editor commands 660, Building outside the editor 738, Testing scripts 765, Feature test 776.
- Releases: scripting predates the first numbered release; `Docs/Releases/0.3.0.md` "Scripting" (line 67) is the first
  release note that describes it. `Docs/Roadmap.md` tracks the host-function count per wave (lines 256-259, 389, 441,
  457, 508, 530, 571; 0.7.0's note line 125).

Size of the area: engine side `Strata/src/Strata/Scripting/` 9 headers + 9 sources, 7,036 lines (ScriptHostAPI.cpp alone
3,719); SDK `StrataScriptCore/` 18 headers (4,590 lines), 1 source, 2 CMake files; platform code (crash guard,
dynamic library, symbolizer) about 1,100 lines; 19 `Scripting.*` test files with 134 test cases; 21 test script
modules' sources; 22 feature-script files (2,881 lines); about 4,400 lines of sample scripts.

---

## 1. Features

### 1.1 The C ABI (`StrataScriptCore/Include/StrataScript/ScriptABI.h`, 858 lines, pure C)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Module entry points | Every module exports `StrataScript_GetABIVersion` and `StrataScript_Load(host, hostABIVersion, outModule)` | ScriptABI.h 3-27, 47-49, 853-854; `StrataScriptCore/Source/ScriptModuleEntry.cpp` 73-81 | ARCH 3148-3151; DG 1861 |
| ABI version | `ST_SCRIPT_ABI_VERSION 1u`; the engine refuses other versions; still 1 after 8 waves | ScriptABI.h 33 | DG 2013-2016; Roadmap 279, 457, 508 |
| Export/extern macros | `ST_SCRIPT_EXPORT` (dllexport / visibility default), `ST_SCRIPT_EXTERN_C` | ScriptABI.h 35-45 | — |
| Layout static asserts | `ST_SCRIPT_DETAIL_STATIC_ASSERT` works in C11 and C++; frozen structs check sizes and offsets | ScriptABI.h 59-65, 172-175, 190-192, 217-220, 297-302 | DG 1985-1986 |
| Size-prefixed extensibility | Every extensible struct starts with `StructSize`; `ST_SCRIPT_HAS_MEMBER(type, ptr, member)` tells whether the other side knows a member | ScriptABI.h 67-69 | DG 1979-1986, 2007-2009 |
| Opaque handles | `StrataScriptContext` (per scene; really a `ScriptSystem*`), `StrataScriptInstance` (void*), entity and asset ids as `uint64_t` UUIDs, 0 is null | ScriptABI.h 76-85 | ARCH 3151 |
| Strings | `StrataScriptString {Data, Size}`, UTF-8, not null-terminated | ScriptABI.h 87-92 | DG 1976 |
| Results | `StrataScriptResult` Ok / Exception / ABIMismatch / InvalidArgument (stored as `uint32_t`) | ScriptABI.h 94-101 | ScriptABI.h 23-24 |
| Tagged-union value | `StrataScriptValue` with 11 types (Empty, Bool, Int, Float, Vec2-4, Quat, String, Entity, Asset) | ScriptABI.h 111-140 | DG 1976 |
| Transforms | `StrataScriptTransform` (translation, quaternion x y z w, scale) and the `TransformPart` mask | ScriptABI.h 142-157 | — |
| Frozen data structs | `StrataScriptRaycastHit` (40 bytes), `StrataScriptCharacterState` (56 bytes): no size, never extended | ScriptABI.h 159-175, 194-220 | DG 1985-1986 |
| Engine-filled extensible struct | `StrataScriptCollision` (engine memory, read only if `StructSize` covers a member) | ScriptABI.h 177-192 | Script.h 276-286 |
| Module-filled-by-engine extensible struct | `StrataScriptGraphicsOptionInfo` (module gives capacity, engine fills at most that, first version 80 bytes) | ScriptABI.h 277-302 | DG 1982-1985 |
| Enums for the API | GroundState, CursorMode, WindowMode, UIAction, InputDevices, GraphicsOptionType, GraphicsOptionSource | ScriptABI.h 194-275 | — |
| Abort exception code | `ST_SCRIPT_ABORT_EXCEPTION_CODE 0xE0535441` ("STA") raised by modules when they `abort()` on Windows | ScriptABI.h 51-56; `Core/CrashGuard.h` 25-28 | DG 2146-2149 |
| Host API table | `StrataScriptHostAPI`: `StructSize`, `ABIVersion` and **165 function pointers** in 27 groups (table below) | ScriptABI.h 304-756 | DG 1867-1970 |
| Buffer protocol | Text and array functions copy at most `capacity` and return the full size, so the caller retries larger | ScriptABI.h 309-310; SDK `Host.h` 69-100 | — |
| Field descriptor | `StrataScriptFieldDesc` {StructSize, Type, Name, DefaultValue} | ScriptABI.h 758-764 | — |
| Class descriptor | `StrataScriptClassDesc`: name, fields, Create/Destroy/GetField/SetField, 15 callbacks (null = not implemented) | ScriptABI.h 766-831 | ScriptABI.h 766-771 (lifecycle) |
| Module description | `StrataScriptModuleAPI` {StructSize, ABIVersion, Name, ClassCount, Classes, Unload} | ScriptABI.h 833-851 | DG 1979-1981 |

Host function groups (165 in all; the arrival wave from `Docs/Roadmap.md` and DG 1950-1955):

| Group | Functions | ABI lines | Arrived |
| --- | --- | --- | --- |
| Diagnostics | Log (any thread), ReportException | 317-320 | initial set (51 functions through GetScrollDelta) |
| Time | GetDeltaTime, GetFixedDeltaTime, GetElapsedTime, GetFrameIndex, GetTimeScale, SetTimeScale | 322-328 | initial |
| Entities | CreateEntity ... GetChildren (15) | 330-347 | initial |
| Components (by registered name) | HasComponent, AddComponent, RemoveComponent, GetProperty, SetProperty | 349-360 | initial |
| Transform fast paths | Get/SetTransform, Get/SetWorldTransform | 362-366 | initial |
| Scene | GetPrimaryCamera, GetRootEntities, Instantiate (never waits) | 368-374 | initial |
| Assets | FindAsset, IsAssetLoaded, RequestAssetLoad | 376-380 | initial |
| Scripts | GetScriptInstance, HasScript, AddScript, RemoveScript | 382-387 | initial |
| Input devices | IsKeyDown/Pressed/Released, mouse buttons, position, delta, scroll | 389-398 | initial |
| Physics bodies | velocities, forces, impulses, torque, Teleport (11) | 400-419 | pre-0.3.0 append |
| Physics queries | Raycast, RaycastAll, OverlapSphere, OverlapBox | 421-438 | pre-0.3.0 append |
| Audio | AudioPlay ... AudioGetMasterVolume (10) | 440-461 | pre-0.3.0 append |
| Game flow | QuitGame, LoadScene | 463-473 | pre-0.3.0 append |
| Residency | ReleaseAsset | 475-481 | wave 1 (asset-residency) |
| Scene streaming | LoadSceneAdditive, UnloadSubScene, IsSubSceneLoaded, GetSceneLoadProgress, GetAssetLoadProgress, InstantiateMany | 483-507 | wave 2 (scene-streaming) |
| Animators | AnimatorPlay ... AnimatorGetJointTransform (12) | 509-534 | wave 2 (animation) |
| Character controllers | CharacterMove, Jump, Teleport, GetState | 536-549 | wave 3, 0.3.0 (gameplay-and-scripting) |
| Gamepads | IsGamepadConnected, buttons, GetGamepadAxis | 551-562 | wave 3, 0.3.0 |
| Cursor | SetCursorMode, GetCursorMode | 564-570 | wave 3, 0.3.0 |
| Window | SetWindowMode, SetResolution, SetVSync, GetWindowSize | 572-582 | wave 3, 0.3.0 |
| Save files | WriteSaveFile, ReadSaveFile, DeleteSaveFile, ListSaveFiles | 584-596 | wave 3, 0.3.0 (119 total) |
| Collision layers | PhysicsSetLayersCollide, GetLayersCollide, GetLayerIndex | 598-610 | wave 3, 0.3.0 |
| Game UI + unscaled time + typed text | UIGetText ... UIIsActionDown (15), GetUnscaledDeltaTime, GetRealTime, GetTypedText | 612-645 | wave 4, 0.4.0 (game-ui, 18) |
| World streaming | WorldRequestCellsAround ... WorldIsLayerEnabled (5) | 647-661 | wave 4, 0.4.0 (142 total) |
| Input actions | InputIsActionDown ... InputSaveBindings (10) | 663-688 | wave 6, 0.6.0 |
| Binding capture | InputBeginBindingCapture, Poll, Cancel | 690-704 | wave 6, 0.6.0 (155 total) |
| Graphics options | GraphicsGetOptionCount ... GraphicsSaveOptions (7) | 706-737 | wave 7, 0.7.0 (162 total) |
| Interpolation | GetStepAlpha, GetDrawnTransform, ResetInterpolation | 739-753 | wave 8 (unreleased at this commit; 165 total) |

Class callbacks (15, `StrataScriptClassDesc` and engine enum `ScriptCallback`, `Scripting/ScriptTypes.h` 16-37):
OnCreate, OnUpdate, OnFixedUpdate, OnLateUpdate, OnDestroy, OnReload (initial); OnCollisionEnter/Exit,
OnTriggerEnter/Exit (appended with physics); OnAnimationEvent (wave 2); OnUIClick, OnUIValueChanged, OnUIFocusChanged
(wave 4); OnUISubmit (wave 4, after the others). `c_ScriptCallbackCount` (ScriptTypes.h 39-41) is derived from the last
value.

### 1.2 The C++ SDK (`StrataScriptCore/Include/StrataScript/*.h`, header-only)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Umbrella header | `StrataScript.h` includes everything; game code includes only it | StrataScript.h 1-25 | SKILL 8-13 |
| SDK plumbing | `Detail::s_Host`, `s_Context`, `s_ConstructingEntity`; `ContextScope` (nested current context); `ToABIString`/`FromABIString`; `ReadHostString`/`ReadHostIDs` (256-byte / 64-id stack buffer then retry) | Host.h 16-102 | — |
| Graceful degradation | `ST_SCRIPT_DETAIL_HOST_WITH(Function)` returns the table only when the engine has that member and it is non-null | Host.h 106-111 | DG 2007-2009 |
| `Script` base class | 15 virtual callbacks, `GetEntity()`, `GetTransform()`; binds entity and context in its constructor | Script.h 30-108 | Script.h 30-69; SKILL 79-101 |
| Exception firewall | `InvokeScript` runs every callback under `ContextScope` and try/catch, turns exceptions into `StrataScriptResult_Exception` plus `ReportException` | Script.h 178-203 | DG 1977-1978 |
| Thunks | C functions per callback that recover the `Script*` and call the virtual (`OnUpdateThunk`, `ContactThunk<>`, `UIClickThunk`...) | Script.h 205-337 | — |
| Override detection | `OverridesOnX<T>()` with `requires { &T::OnX; }` compares member-pointer types; `GetCallbackFlags<T>()` | Script.h 348-541 | Script.h 368-370 |
| Static self-registration | `ClassRegistrar<T>` links a `ClassRegistration` into an intrusive list during static init (no allocation) | Script.h 543-617 | Script.h 543-544 |
| Class records | `BuildClassRecord`: fields, defaults read from a default-constructed instance, the ABI descriptor with null for unimplemented callbacks | Script.h 638-690 | SKILL 74-75 |
| Version-safe module description write | `CanReceiveModuleAPI`, `WriteModuleAPI` (write at most the engine's capacity) | Script.h 692-710 | DG 1979-1981 |
| `Detail::LoadModule` | ABI checks (version, baseline member `GetScrollDelta`, capacity), builds every record, catches exceptions | Script.h 712-762 | DG 2015-2016 |
| `ScriptClassBuilder<T>::Field<&T::M>` | Field registration with static_asserts on owner and type | Script.h 766-797 | — |
| `ST_SCRIPT_CLASS` / `ST_SCRIPT_FIELD` | Registration macros (uses `__COUNTER__`; spelled type name is the class name) | Script.h 842-865 | SKILL 61-77; MAN 34-53 |
| Field types | bool, int32_t, float, glm::vec2/3/4, glm::quat, std::string, Entity, AssetHandle (`c_IsFieldType`) | Script.h 133-137; Value.h | MAN 51-53 |
| Value traits | `ValueTraits<T>` ToValue/FromValue, integers range-checked, quaternions x y z w | Value.h 33-277 | — |
| `AssetHandle` | constexpr 64-bit handle | Value.h 18-31 | — |
| `Entity` | id wrapper: name, tag, activity, hierarchy, Destroy, components by name, `GetProperty<T>`/`SetProperty`, typed accessors (RigidBody, CharacterController, AudioSource, Animator, UI), scripts (`GetScript<T>`, `AddScript<T>`) | Entity.h 28-96, 249-420; Script.h 816-838 | SKILL 105-111 |
| `Component` proxy | `entity.GetComponent("Camera").Get<float>("FOV")` | Entity.h 126-158 | — |
| `TransformComponent` | local and world get/set, Euler, forward/right/up (-Z forward), drawn pose, `ResetInterpolation` | Entity.h 161-245, 421-490 | SKILL 118-119, 142-146 |
| `Scene`, `Assets`, `SubScene` | create/find entities, roots, camera, `Instantiate` (by handle or path, with transform), `InstantiateMany`, `LoadAdditive`; assets find/loaded/request/release/progress | Scene.h 20-232 | SKILL 120-126, 394-433 |
| `Input` | keys (`Key::` enum), mouse (`Mouse::`), gamepads, sticks with round dead zone, cursor mode, typed text, input actions, binding capture | Input.h 13-532 | SKILL 127-152, 435-487; MAN 109-134 |
| `Time` | delta, fixed delta, elapsed, frame index, time scale, unscaled delta, real time, step alpha | Time.h 11-79 | SKILL 138-141 |
| `Log` | variadic, ostream-concatenated, glm/Entity/AssetHandle formatting | Log.h 15-89 | SKILL 155 |
| `RigidBody`, `Physics`, `RaycastHit`, `Collision` | bodies, queries, `c_AllLayers`, collision layers | Physics.h 16-307 | SKILL 167-226 |
| `CharacterController`, `GroundState` | Move, Jump, Teleport, ground state, normal, entity, velocity | CharacterController.h 11-126 | SKILL 228-250 |
| `AudioSource`, `Audio` | source control, one-shots, master volume | Audio.h 9-122 | SKILL 272-283 |
| `Animator`, `JointTransform` | states, clips, cross-fade, parameters, speed, state queries, joints | Animator.h 14-145 | SKILL 285-320 |
| `Game`, `WindowMode` | Quit, LoadScene, ReloadScene, progress, window mode, resolution, vsync, window size, save files (bytes or text) | Game.h 16-175 | SKILL 380-392, 517-535 |
| `Graphics`, `GraphicsOption`, `QualityPreset` | players' graphics options by name, presets, reset, save | Graphics.h 14-238 | MAN 136-155; SKILL 489-515; DG 1939-1949 |
| `UIElement`, `UI`, `UIAction` | text, image, color, interactable, value, focus; UI actions, pointer over UI | UI.h 13-183 | SKILL 322-378 |
| `World`, `WorldCellRequest` | prefetch cells around a point, layers | World.h 11-80 | SKILL 198-214; DG 1960-1964 |
| `Random` | PCG32 (XSH-RR), deterministic across platforms, unbiased integer ranges by rejection | Gameplay.h 19-110 | SKILL 545-546; DG 1968-1970 |
| `Timer` | count-down, repeating timer keeps overshoot so it does not drift, non-positive durations stop | Gameplay.h 112-176 | SKILL 547-549 |
| `KeyRepeat` | press, delay, interval repeat (menus, falling blocks) | Gameplay.h 178-219 | SKILL 550-551 |
| `Motion` | `LookAt`, critically damped `SmoothDamp` (scalar and vector) | Gameplay.h 222-321 | SKILL 377-378 |
| Module entry source | `ScriptModuleEntry.cpp`: `#pragma init_seg(lib)`, SIGABRT handler raising the abort exception (Windows /MT only), the two exports | ScriptModuleEntry.cpp 1-81 | DG 2146-2151 |

### 1.3 Building a module (`StrataScriptCore/CMake/`, `StrataScriptCore/CMakeLists.txt`)

| Feature | Where | Documented |
| --- | --- | --- |
| `StrataScriptCore` INTERFACE target (headers + glm, C++20) | `StrataScriptCore/CMakeLists.txt` 1-12 | DG 1862 |
| `strata_add_script_module(<target> [SOURCE_DIR] [SOURCES] [OUTPUT_NAME] [OUTPUT_DIRECTORY] [NO_SDK_ENTRY])`: MODULE library, glob that skips dot-folders and nested build trees, adds `ScriptModuleEntry.cpp`, hidden visibility, static C runtime (`MultiThreaded[Debug]`), `ST_SCRIPT_MODULE_NAME`, PDB in every configuration (Embedded under a compiler launcher), `/OPT:REF /OPT:ICF` back on, `-fno-gnu-unique` on GCC (else `dlclose` is a no-op), `--no-undefined` on Linux | `CMake/StrataScriptModule.cmake` 1-134 | DG 2022-2038; SKILL 738-763 |
| Package for game projects: `find_package(StrataScriptCore CONFIG ... PATHS <engine>/StrataScriptCore/CMake)`, glm from the install or the vendor folder, glm defines matching the engine, a `Dist` configuration with Release flags | `CMake/StrataScriptCoreConfig.cmake` 1-66 | DG 2022-2032, 883-889 |
| Engine test modules (Dependent, API, ReloadV1/V2, Faults, LoadFault, ABIMismatch, Malformed, NewerSDK, FeatureTest, World) | `StrataTests/CMakeLists.txt` 30-44; sources `StrataTests/Scripts/**`, `StrataTests/FeatureTest/Scripts` | DG 883-889, 1864-1865 |
| Editor build pipeline (`ScriptBuilder`, toolchain detection, `CMakePresets.json`, diagnostics parsing, per-user build directory for paths MSBuild cannot handle) | `StrataEditor/src/Editor/ScriptBuild.h/.cpp` (285/1323 lines), `ScriptToolchain.h/.cpp`, `ScriptProject.h/.cpp`, `ScriptSources.h/.cpp`, `ScriptBuildConfig.h.in` | DG 2033-2079; MAN 208-219 (editor area: summarized, not read in depth) |

### 1.4 The engine side (`Strata/src/Strata/Scripting/`)

| Feature | What it is | Where | Documented |
| --- | --- | --- | --- |
| Registration | `RegisterScriptingModule`: the Script component and the "Scripting" scene system (play only, not simulate; profile stage `Scene.Scripts`; scripts update before physics) | ScriptingRegistration.h/.cpp (13/26 lines) | AGENTS "Module registration" |
| Script component | `ScriptComponent { vector<ScriptEntry{ClassName, Fields}> }`, JSON and binary serialization, references for asset/entity fields, remapping, equality | ScriptingComponents.h 1-39; .cpp 60-287 | — |
| `ScriptModule` | one loaded library: in-place or private-copy load, ABI check, guarded `StrataScript_Load`, validated description, guarded calls, fault record, symbolization job, guarded unload | ScriptModule.h 18-176; .cpp 1-1106 | ARCH 3152-3155; DG 1987-1989 |
| Load modes | `ScriptModuleLoadMode::InPlace` / `Copy`; a file already loaded or abandoned is always loaded from a copy | ScriptModule.h 25-33; .cpp 377-450 | DG 2114-2124 |
| Private copy directory | one per process under `Platform::GetUserRuntimeDirectory("Strata")`, `ScriptModules-*`, owner `FileLock`, stale directories of dead processes removed | ScriptModule.cpp 26-50, 155-215, 254-299 | DG 2118-2121 |
| Library registry | handles of loaded libraries, abandoned files (crash in loader) only loaded from copies | ScriptModule.cpp 71-154 | ScriptModule.h 59-68 |
| Call results | `ScriptCallResult` Ok / Exception / Rejected / Faulted / Unavailable | ScriptModule.h 35-42 | — |
| Call sites | `ScriptCallSite` {Class, Method, Entity, Scene} for reports and the watchdog; thread-local current call | ScriptModule.h 44-51; .cpp 59-60, 220-250 | — |
| Description validation | limits (65,536 classes, 4,096 fields, 1,024-byte names), duplicate names, required members, field type and default type checks; functions copied out once | ScriptModule.cpp 53-66, 942-1094 | DG 1987-1989 |
| `ScriptEngine` | owns the module, reload protocol across running scenes, hot reload watcher (300 ms debounce, 20 retries at 250 ms), faults, watchdog, active engine | ScriptEngine.h 1-136; .cpp 1-309 | ARCH 3156-3158, 3209-3213 |
| Containment contract | what is and is not contained, listed exactly | ScriptEngine.h 25-45 | DG 2146-2162 |
| `ScriptSystem` | per playing scene: instances, lifecycle, sync points, update order, dispatch lists, contacts, animation and UI events, asset pins, problem reports, binding capture ownership | ScriptSystem.h 1-309; .cpp 1-1560 | ARCH 3159-3178 |
| Update order | hierarchy order then entry order; incremental insertion by binary search, re-placement of moved scripted entities, lazy compaction at 1/8 destroyed | ScriptSystem.h 47-57; .cpp 894-1219 | ARCH 3160-3166 |
| Dispatch lists | per update callback, only implementing instances; software prefetch 12 instances / 4 objects ahead | ScriptSystem.cpp 24-35, 241-287, 1178-1219 | ARCH 3166-3171 |
| Sync points | deferred destroys, reconcile dirty entities, OnReload, OnCreate; at most 64 rounds | ScriptSystem.cpp 482-505 | ScriptSystem.h 189-197 |
| Field values | snapshot/restore on reload, live get/set for the inspector and `script.get` | ScriptSystem.cpp 748-784, 1392-1424 | — |
| Asset requests | `AssetPin` per requested asset, `AssetGroupRequest` per progress query, released at stop | ScriptSystem.cpp 1504-1539 | DG 1965-1967 |
| `ReportProblem` | warning naming the calling script and entity, deduplicated, 1,024 per scene | ScriptSystem.cpp 1541-1558 | DG 1990-1992 |
| Host API implementation | 165 `Host<Name>` functions, `HostCall`, `ResolveContext`, validators, the X-macro table, call counters | ScriptHostAPI.h 1-35; .cpp 1-3719 | ARCH 3179-3181; DG 1990-1992, 1997-2016 |
| Context registry | contexts are registered `ScriptSystem*` values, single owner thread | ScriptHostAPI.cpp 50-53, 3705-3719 | ScriptHostAPI.h 17-20 |
| Host call counts | `GetScriptHostCallCounts` / `Reset...` (not in Dist) for the feature test | ScriptHostAPI.h 22-33; .cpp 3627-3703 | DG 2010-2012 |
| Value conversion | exact for fields, lenient for component properties (ints for enums, vec3/vec4 for colors, vec4/quat for rotations); `c_MaxScriptStringSize` 256 MiB | ScriptValue.h 1-39; .cpp 1-305 | — |
| Types | `ScriptCallback`, `ScriptFieldInfo`, `ScriptClassInfo` (callback bit mask), `ScriptCodeLocation`, `ScriptFault`, `DescribeScriptCodeLocation` | ScriptTypes.h 1-103; .cpp 1-61 | — |
| Watchdog | thread that logs a call running longer than the timeout (cannot interrupt native code) | ScriptWatchdog.h 1-59; .cpp 1-81 | ARCH 3214-3215 |
| Problems the host reports | invalid context, wrong thread, call outside a callback, crashed module, null/non-finite input, unknown component/property, not-loaded asset, full scene | ScriptHostAPI.cpp 55-96, 128-278 | DG 1990-1992 |

### 1.5 Crash containment and crash locations (Core and Platform)

| Feature | Where | Documented |
| --- | --- | --- |
| `CrashGuard::Invoke(function, userData, outInfo)` and `CrashInfo` (description, code, address, stack) | `Strata/src/Strata/Core/CrashGuard.h` 12-68 | ARCH 3182-3189 |
| Windows: SEH `__try/__except`, filter choosing 18 exception codes, x64 stack unwind with `RtlLookupFunctionEntry`/`RtlVirtualUnwind`, `_resetstkoflw`, 32 KiB stack guarantee | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp` 1-214 | ARCH 3183-3186 |
| POSIX: SIGSEGV/SIGBUS/SIGFPE/SIGILL/SIGTRAP handlers on an alternate stack, `sigsetjmp`/`siglongjmp` (Linux), return into a recovery routine (macOS); SIGABRT reported only; forwarding to previous handlers; glibc forced unwind passes | `Strata/src/Platform/Posix/PosixCrashGuard.cpp` 1-404 | ARCH 3186-3189 |
| Abort containment in modules (Windows, static CRT only) | `ScriptModuleEntry.cpp` 1-71 | DG 2146-2151 |
| `DynamicLibrary` (load with dependency directory, never CWD or PATH; truncated files refused) | `Core/DynamicLibrary.h` 1-63; `Platform/Windows/WindowsDynamicLibrary.cpp`, `Platform/Posix/PosixDynamicLibrary.cpp` | DG 2125-2128 |
| `Symbolizer::Describe` (cheap, at fault time) and `Resolve` (job; DbgHelp PDB with inline frames on Windows, ELF `.symtab` on Linux, dladdr on macOS) | `Core/Symbolizer.h` 1-51; `Platform/Windows/WindowsSymbolizer.cpp` (201), `Platform/Posix/PosixSymbolizer.cpp` (127) | DG 2135-2145; ARCH 3194-3208 |
| Fault location choice (first module frame with a source that is not CRT or the entry file) | ScriptModule.cpp 580-605 | DG 2140-2143 |
| Exception vs crash policy: exception disables one instance, crash faults the module | ScriptSystem.cpp 299-308; ScriptModule.cpp 301-344 | ARCH 3190-3193 |

### 1.6 Hosts of the script engine

| Feature | Where | Documented |
| --- | --- | --- |
| Active engine (`ScriptEngine::SetActive/GetActive`): scenes use the engine active when they start | ScriptEngine.cpp 294-302 | ARCH 3156-3158 |
| Editor: one engine per project, hot reload on, `Update()` per frame, Play builds first, crash stops play | `StrataEditor/src/Editor/EditorContext.cpp` 1348, 2216-2221, 2421-2436, 2536-2579 | DG 2081-2101 |
| Exported game: `GameRuntime` loads the module in place, crash disables scripts, headless exit code 2 | `Strata/src/Strata/Runtime/GameRuntime.cpp` 100-170; `StrataRuntime/src/RuntimeApplication.cpp` 152 | DG 2103-2112 |
| Engine services a host must provide (`IGameSaves`, `IGameWindow`, `IGameGraphics`, `IAudioOutput`, `IProjectSettings`) | `Strata/src/Strata/Core/EngineServices.h` (other area) | DG 1929-1938 |
| Scene services the host API goes through (`IBodyControl`, `IBodyMotionQuery`, `IPhysicsQueries`, `ICharacterControl`, `IAudioPlayback`, `IAnimatorControl`, `IUIControl`, `IWorldStreaming`; events `ICollisionEventSource`, `IAnimationEventSource`, `IUIEvents`) | `Strata/src/Strata/Scene/SceneServices.h` (other area); uses at ScriptHostAPI.cpp sections 1167, 1590, 1970, 2395, 2646 | DG 1871-1928 |
| Layering: Scripting may include only Core, Input, Asset, Reflection, Scene | `StrataTests/Architecture/Layers.json` 76-78 | AGENTS "Layers" |

### 1.7 Editor workflow around scripts (editor area; listed for completeness)

- Commands (13): `script.status`, `script.list`, `script.get`, `script.build`, `script.reload`, `script.load`,
  `script.init`, `script.create`, `script.open`, `script.setExternalEditor`, `script.add`, `script.remove`,
  `script.setField` (`StrataEditor/src/Editor/EditorScriptCommands.cpp` 247-635; DG 3135-3174; SKILL 660-736).
- UI: Scripts menu (New Script..., Build Scripts Ctrl+B, External Editor..., Open Scripts Folder, Show Problems),
  `UI/ScriptDialogs`, Content Browser Scripts root (`UI/ScriptBrowser`), Inspector Script drawer (`Editor/ScriptEdit`),
  Problems panel, status-bar pills ("Building", "Build failed", "Scripts crashed", "Scripts unused") (MAN 9-72, DG
  3159-3174).
- Export: the module and its PDB next to the game, named in the `.stgame` manifest v2 (DG 2105-2112).

### 1.8 Tests that define the behavior

`StrataTests/src/Scripting/` suites and counts: API 17, Animation 4, Audio 3, Collisions 7, Faults 10, Game 2,
Graphics 6, Helpers 3, InputActions 6, Lifecycle 16, Module 23, Physics 7, Reload 4, Input (ScriptShellTests) 8,
Streaming 2, Order 6, UI 8, World 2. Also `StrataTests/src/Architecture/ScriptSDKTests.cpp` (no engine TU includes
the SDK's C++ headers), `StrataTests/src/Perf/ScriptingPerfTests.cpp` (5 perf tests, budgets in
`StrataTests/Perf/Budgets.json` 40-47: 100k trivial OnUpdate 1.856 ms measured, 300k 5.745 ms), the feature test
(`StrataTests/src/FeatureTest/FeatureTests.cpp`, `SDKCoverageTests.cpp`, `SDKReader.cpp`), the editor tests
(`StrataTests/src/Editor/Script*Tests.cpp`, `EditorScriptTests.cpp`) and the package/end-to-end runners
(`StrataTests/Editor/ScriptsEndToEnd.cmake`, `SampleProject.cmake`).

### How completeness was checked

- Every file of `Strata/src/Strata/Scripting/` (18) and `StrataScriptCore/` (18 headers, 1 source, 3 CMake files) is
  named above; every SDK header has a row.
- Host functions: counted 165 function-pointer members in `StrataScriptHostAPI` (ScriptABI.h 312-756) and 164
  `Host<Name>(StrataScript...` definitions plus `HostLog` in ScriptHostAPI.cpp; group sums (51 + 15 + 10 + 2 + 1 + 6 +
  12 + 4 + 5 + 2 + 4 + 4 + 3 + 18 + 5 + 13 + 7 + 3) give 165 and match the Roadmap's running totals 119, 142, 155, 162.
  The X-macro list `ST_SCRIPT_HOST_FUNCTIONS` (ScriptHostAPI.cpp 3431-3596) is checked against the struct by a
  `static_assert` (3610-3622).
- Callbacks: 15 in `StrataScriptClassDesc`, `ScriptCallback`, `CallbackFlag` and `ClassFunctions` (all four agree).
- Registered things: one component ("Script"), one scene system ("Scripting"), no settings section, no asset type, no
  shader. Scripting registers no editor command itself (the `script.*` family is the editor's).
- Field types: 10 (`c_IsFieldType`, Script.h 135-137) match `ScriptFieldTypeToPropertyType` and the docs.

---

## 2. Concepts to teach (dependency order)

1. **Why games need "scripts" at all: engine code vs game code.** Problem: the engine is generic and large, game rules
   change hourly; rebuilding and restarting the whole engine for each tweak kills iteration. Approaches: embedded
   interpreted languages (Lua in many engines, Python in tools), managed runtimes (C# in Unity, Godot's C#), custom
   languages (GDScript, UnrealScript historically), visual scripting (Blueprints), native code in plug-in libraries
   (Unreal's C++ modules with Live Coding, Hazel's C# via Mono, many in-house engines' DLL hot reload). Strata: native
   C++20 in a shared library behind a C ABI (ScriptABI.h 3-27; AGENTS.md intro). Why: one language for engine and game,
   full speed, the C++ tooling (debuggers, IDEs) people already use; the costs (crashes, ABI, compile time) are paid by
   the containment and hot-reload machinery. Newcomers think "script" means interpreted; here it means "game code the
   engine loads", and they underestimate how much engineering a native choice requires.
2. **Shared libraries and dynamic loading.** What a DLL/.so/.dylib is, exported symbols, `LoadLibrary`/`dlopen`,
   `GetProcAddress`/`dlsym`, static initializers running at load, reference counting (loading a loaded file returns the
   same library and shares its state: DynamicLibrary.h "GetNativeHandle" comment), dependency search paths (Windows
   search order, RUNPATH, `$ORIGIN`), symbol visibility and interposition. Strata: `DynamicLibrary`, module copies,
   hidden visibility, `-fno-gnu-unique`. Mistakes: believing unloading always unloads (GCC unique symbols), relying on
   PATH or the current directory, forgetting that static constructors are code that can crash.
3. **ABI vs API.** An API is source-level; an ABI is the binary contract (calling convention, struct layout, name
   mangling, exception model, allocator, STL layout). C++ has no stable ABI across compilers, versions and Debug/Release
   (MSVC `_ITERATOR_DEBUG_LEVEL`), so engines expose C. Approaches: COM-style interfaces with vtables, C function tables
   (Strata, also Vulkan's dispatch tables), flat C exports, IDL-generated bindings. Strata: two exported functions and
   function-pointer tables, plain data only, strings as (pointer, size), ids as `uint64_t`, quaternions as x y z w
   (DG 1974-1978). Mistakes: passing `std::string` or a `glm` type across, freeing memory on the other side, letting an
   exception cross, assuming `bool` and enum sizes match (Strata stores enums as `uint32_t`).
4. **Versioning a binary interface.** Forward/backward compatibility; append-only structs; size prefixes
   (`StructSize`, the Win32 `cbSize` pattern); feature detection vs version numbers; frozen structs for arrays the
   engine writes. Strata: one version number for incompatible changes, append-only host table and class descriptor,
   `ST_SCRIPT_HAS_MEMBER`, `ST_SCRIPT_DETAIL_HOST_WITH`, `WriteModuleAPI` writing at most the receiver's capacity, the
   graphics-option struct filled in the other direction, and the baseline check at `GetScrollDelta` (Script.h
   719-721). Why: modules built for 0.6.0 load unchanged on 0.7.0 and vice versa (Releases/0.7.0.md 125-126).
   Mistakes: inserting a member in the middle, extending a struct that the other side allocates in arrays
   (`StrataScriptRaycastHit`), checking only the version and then calling a null pointer.
5. **The host API / service table pattern.** The engine hands the module a table of function pointers plus an opaque
   context; the module never links the engine. Same idea as plug-in SDKs and Vulkan loaders. Strata's context is the
   scene's `ScriptSystem*` validated against a registry (ScriptHostAPI.cpp 50-96, 3705-3719). Why: isolation (scripts
   see no engine headers: `Architecture.ScriptSDK`), hot reload safety, testability (call counters). Mistakes: thinking
   the module can call the engine from its own threads or outside callbacks.
6. **A C++ SDK over a C ABI.** The idiomatic layer: classes, `std::optional`, `std::string_view`, RAII wrappers that
   translate to C calls. Techniques worth teaching on their own: thunks (C function per virtual), static
   self-registration through global constructors and an intrusive linked list, member-pointer templates for fields,
   detecting overrides at compile time with `requires` and `decltype(&T::OnUpdate)`, `__COUNTER__` in macros, the
   buffer-retry protocol. Strata: Script.h. Mistakes: registering in a header (two translation units, two
   registrations), side effects in constructors (the module constructs each class once to read defaults: Script.h
   638-660, SKILL 74-75).
7. **Component-based game objects and where scripts attach.** Prerequisite from the Scene area (entities, components,
   hierarchy, UUIDs). Scripts are a component holding a list of class names plus field overrides; instances live
   outside the ECS registry in the ScriptSystem. Approaches: script-as-component (Unity MonoBehaviour), scripts as
   systems (pure ECS), actor subclasses (Unreal). Strata: entry list per entity, one instance per entry, ordered.
8. **The script lifecycle.** Construct, apply stored field values, OnCreate (after all initial instances exist and all
   systems started), per-frame OnUpdate, zero or more OnFixedUpdate, OnLateUpdate, OnDestroy (descendants first), and on
   reload OnReload instead of OnCreate (ScriptABI.h 766-771; ScriptSystem.h 40-57; SKILL 79-101). Concept of a fixed
   timestep and why input "pressed" edges must be read in OnUpdate (SKILL 133-137). Mistakes: initializing in the
   constructor, reading `IsKeyPressed` in OnFixedUpdate, caching `T*` across frames.
9. **Deferred mutation and safe points.** Problem: script code can destroy the entity whose callback is running, or the
   system iterating over it. Approaches: command buffers, deferred destruction, generation-checked handles. Strata:
   destruction requested through `ScriptSystem::DestroyEntity` (end of frame), removed instances flagged and destroyed
   at sync points, copies of lists before calling script code, a bounded number of sync rounds (ScriptSystem.cpp
   482-505, 1485-1496). Mistakes: holding iterators across script calls, unbounded recursion of spawns in OnCreate.
10. **Update order and its cost.** Deterministic order (parents first) vs cache efficiency; incremental maintenance of
    an order under spawns and hierarchy moves; dispatch lists of only implementing instances; prefetching and why
    hardware prefetchers failed (ARCH 3166-3171). Engine-developer chapter; game developers only need "parents first,
    then entry order".
11. **Crash containment of native code.** Hardware exceptions (access violation, divide by zero, stack overflow),
    Windows structured exception handling vs POSIX signals, `setjmp`/`longjmp` recovery, alternate signal stacks, stack
    guard pages and `_resetstkoflw`, why destructors do not run, why a crashed module is never called again, what
    cannot be contained (fail-fast, heap corruption under allocator locks, `exit`) (CrashGuard.h 35-61; ScriptEngine.h
    25-45). Approaches elsewhere: process isolation (separate process per plug-in, browsers), sandboxed VMs (Lua, WASM),
    nothing at all (most engines crash). Strata: in-process guard plus "fault the module, keep the engine". Mistakes:
    believing containment makes the process safe after a stray write (it does not detect those), expecting `abort()` to
    be contained on Linux.
12. **Exceptions vs crashes.** C++ exceptions are caught by the SDK in the module (InvokeScript) and disable one
    instance; anything that escapes the SDK is a crash. Why the engine never lets its own exceptions unwind into the
    module (`HostCall`, noexcept). Mistakes: thinking `try` in engine code catches module exceptions (different runtimes,
    different heaps).
13. **Symbolization: from an address to a file and line.** Return addresses, unwinding with unwind tables, module base
    and offset, debug information (PDB, DWARF, ELF symbol tables), inlining and inline frames, why the fault location
    skips CRT frames (ScriptModule.cpp 580-720; WindowsCrashGuard.cpp 61-94). Why it runs on a job (DbgHelp is slow and
    single-threaded).
14. **Hot reload.** Problem: change code while the game runs. Approaches: restart with state saved, DLL swap with state
    serialization (Strata, many in-house engines), binary patching (Live++, Unreal Live Coding), interpreters reloading
    functions. Strata: watch the file (300 ms debounce), load the new module beside the old one, snapshot fields of
    every instance, destroy without OnDestroy, unload the old library, recreate, restore fields with same name and type,
    OnReload (ScriptEngine.cpp 65-124, 196-229; ScriptSystem.cpp 1221-1348). Why private copies: Windows locks a loaded
    DLL, so the build could not overwrite it. Mistakes: keeping state in non-field members, keeping pointers to module
    memory across a reload, `$ORIGIN` RUNPATH dependencies that break under copies.
15. **Serialized fields and the editor.** Reflection lite: the module describes fields with names, types and defaults;
    the engine stores per-entity overrides by name and type in the Script component and the scene file; the inspector
    edits them; reload keeps live values. Mistakes: renaming a field (its stored values are ignored with a warning),
    changing its type.
16. **The gameplay API as a facade over engine services.** Dependency inversion: the Scripting layer may not include
    Physics, Audio, Animation, GameUI or World (Layers.json 76-78), so every gameplay function goes through a scene
    service interface or an engine service, and fails (reported) when the service is absent, e.g. in simulate mode.
    Teach once, then each subsystem chapter (physics, audio, animation, UI, worlds) shows its script face.
17. **Asynchronous assets from game code.** Never block the main thread: `Instantiate` starts the load and returns
    null; request early, spawn when loaded; pins keep requested assets resident; progress of a dependency closure
    (ScriptHostAPI.cpp 830-897; ScriptSystem.cpp 1504-1539). Mistakes: spawning in OnCreate without requesting first,
    loops that wait for loading.
18. **Player-facing systems: saves, rebindable input, graphics options, window.** Atomic save files with validated
    names, input actions instead of keys, binding capture, graphics options by name so later engine rows need no new
    code, window requests applied after the frame. Each owned by one engine service (AGENTS "Scripting" bullets).
19. **Interpolation of fixed-step motion** (from the Scene/Physics area): why a follow camera reads the drawn pose in
    OnLateUpdate (MAN 157-175).
20. **Determinism helpers.** Seeded PRNG (PCG32), unbiased ranges by rejection, timers that keep overshoot, critically
    damped smoothing; why they live in the module (ODR: engine classes share the names, DG 1968-1970).
21. **Testing game code and the API.** Feature test coverage of every host function and SDK function, call counters,
    test modules that crash on purpose, command-script regression tests for games (SKILL 765-803).

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader needs first |
| --- | --- | --- | --- |
| 1 | `StrataScriptCore/Include/StrataScript/ScriptABI.h` 3-27 | The whole contract in one comment: two exports, plain data, append-only, results, single thread | Concepts 2-3 |
| 2 | ScriptABI.h 67-69 and 304-320 | `ST_SCRIPT_HAS_MEMBER` and the head of the host table (`StructSize`, `ABIVersion`, `Log`) | C structs, offsetof |
| 3 | ScriptABI.h 111-140 | A tagged union as the one value type crossing the boundary | unions |
| 4 | ScriptABI.h 159-192 | A frozen struct with layout asserts vs an extensible one with `StructSize`, and why (comments) | 2 |
| 5 | ScriptABI.h 758-851 | Field, class and module descriptors: what the engine learns about a module | 1-4 |
| 6 | `StrataScriptCore/Source/ScriptModuleEntry.cpp` 1-81 | The module's two exports; abort containment with `init_seg(lib)`, `_set_abort_behavior`, SIGABRT handler raising an SEH exception | DLLs, static init order |
| 7 | `StrataScriptCore/Include/StrataScript/Host.h` 36-55, 69-85, 106-111 | Current-context scope, the buffer-retry protocol, `ST_SCRIPT_DETAIL_HOST_WITH` | 2, RAII |
| 8 | `StrataScriptCore/Include/StrataScript/Script.h` 70-108 | The `Script` base class a game programmer sees | classes, virtual functions |
| 9 | Script.h 184-203 and 246-250 | `InvokeScript`: the exception firewall; a thunk | exceptions, lambdas |
| 10 | Script.h 371-378, 506-541 | Compile-time override detection with `requires` and member-pointer types | templates, concepts (teach) |
| 11 | Script.h 543-617 and 852-865 | Static self-registration and the `ST_SCRIPT_CLASS`/`ST_SCRIPT_FIELD` macros | static storage, macros |
| 12 | Script.h 638-690 | `BuildClassRecord`: defaults from a default-constructed instance; null callbacks for unimplemented ones | 10-11 |
| 13 | Script.h 692-762 | `WriteModuleAPI` and `LoadModule`: version checks and writing at most the receiver's capacity | 4 |
| 14 | `Strata/src/Strata/Scripting/ScriptModule.cpp` 301-344 | `ScriptModule::Call`: every module call through `CrashGuard`, fault recording, result mapping | 9, 16 |
| 15 | ScriptModule.cpp 377-515 | `ScriptModule::Load`: in place or copy, export lookup, version, guarded `StrataScript_Load`, guarded description read, "move complete results out" | 14 |
| 16 | `Strata/src/Strata/Core/CrashGuard.h` 35-68 | The containment contract, including what is not contained | concept 11 |
| 17 | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp` 96-159, 196-212 | SEH filter, `_resetstkoflw`, why the `__try` is in a separate function (C2712) | SEH basics (teach) |
| 18 | WindowsCrashGuard.cpp 43-94 | Stack guarantee for stack overflows; unwinding a stack with `RtlVirtualUnwind` | stacks, calling conventions |
| 19 | `Strata/src/Platform/Posix/PosixCrashGuard.cpp` 28-40, 239-260, 348-402 | Signals, alternate stack, `sigsetjmp`/`siglongjmp`, unblocking the signal, the macOS difference | signals (teach) |
| 20 | ScriptModule.cpp 942-1094 | Validating untrusted module data; copying function pointers once so later calls never read module memory | 5 |
| 21 | ScriptModule.cpp 622-720 and 580-605 | Recording a fault, describing frames now, symbolizing on a job; choosing the reported frame | 13 |
| 22 | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp` 67-116 | `ResolveContext` and `HostCall`: the two guards every host function starts with | 5 |
| 23 | ScriptHostAPI.cpp 356-370 and 830-897 | A tiny host function (`SetTimeScale`, input validation and ReportProblem) and a real one (`Instantiate`: never waits, creates pending instances) | 22 |
| 24 | ScriptHostAPI.cpp 3427-3437 (head of the X-macro), 3598-3622, 3641-3669 | X-macro table, a `constexpr` check that the list covers the struct exactly, counted thunks, Dist without counters | macros, constexpr |
| 25 | `Strata/src/Strata/Scripting/ScriptEngine.cpp` 65-124 and 196-229 | Load beside the old module, reload protocol across scenes, debounced hot reload with retries | 14-15 |
| 26 | `Strata/src/Strata/Scripting/ScriptSystem.cpp` 195-221 and 482-505 | The three update phases and the sync point loop with a bound | concept 9 |
| 27 | ScriptSystem.cpp 241-287 | The dispatch loop: skip conditions, activity from the cache, software prefetch and why | pointers, caches |
| 28 | ScriptSystem.cpp 1221-1348 | Hot reload in a scene: snapshot, destroy without OnDestroy, recreate, restore, OnReload or OnCreate | 25 |
| 29 | ScriptSystem.cpp 340-383 | Contact delivery: every Enter gets its Exit, copies of lists, normals flipped for the other side | physics contacts |
| 30 | `StrataScriptCore/Include/StrataScript/Gameplay.h` 19-110 | PCG32 and unbiased ranges by rejection (an algorithm readers can verify) | integer arithmetic |
| 31 | `StrataScriptCore/CMake/StrataScriptModule.cmake` 85-133 | What building a module means: MODULE library, hidden visibility, static CRT, PDB, `-fno-gnu-unique` | CMake basics |
| 32 | `Samples/ThirdPerson/Scripts/Coin.cpp` 1-59 | A complete small game script: fields, OnCreate/OnReload, OnUpdate, OnTriggerEnter, calling another script | game-dev basics |
| 33 | `Samples/ThirdPerson/Scripts/FollowCamera.cpp` 43-100 | Camera in OnLateUpdate, drawn position, unscaled time, raycast against walls, exponential smoothing | 32, interpolation |
| 34 | `Docs/Manual/Scripting.md` 13-38 | The template New Script writes | none |

Excerpts 14, 15, 25 and 28 together are the central algorithm (load, call, reload); 17-19 are the second (containment).
Keep the platform excerpts short in the main text and the full listings in an appendix.

---

## 4. Figures

Diagrams:

1. **The layers** (redraw of ARCH 3138-3146): game code / SDK / entry / C ABI line / ScriptModule / ScriptEngine /
   ScriptSystem / ScriptHostAPI, with the services below (scene services and engine services) and arrows for calls in
   each direction.
2. **Who owns what in memory**: engine heap (ScriptSystem::Instance, ScriptClassInfo, copied ClassFunctions) vs module
   heap (Script objects, ClassRecords, descriptors); the instance's `Handle` pointing across; which side frees what.
3. **Loading a module (sequence diagram)**: file check, copy or in place, `LoadLibrary` under guard (static init),
   register handle, `GetABIVersion`, `StrataScript_Load` with host table and capacity, module writes description,
   guarded description read, validation, ready.
4. **Struct versioning**: two bars for an old engine and a new module (and the reverse), `StructSize` on entry and on
   return, the overlap read by both; the same for `StrataScriptGraphicsOptionInfo` in the other direction.
5. **A host call round trip**: script `entity.SetProperty(...)` -> SDK `ValueTraits::ToValue` -> table pointer -> counted
   thunk -> `HostSetProperty` -> `HostCall` -> `ResolveContext` -> ComponentAccess -> back, with the failure exits
   (null context, other thread, outside callback, faulted module, bad input -> ReportProblem).
6. **Instance lifecycle state machine**: Constructed (fields applied) -> PendingStart -> Created (OnCreate) -> updating;
   Disabled (exception); Removed (flag) -> destroyed at sync point (OnDestroy, Destroy); Reload: Snapshot -> handle null
   -> reconstructed -> PendingReload (OnReload) or PendingStart; Faulted module: abandoned.
7. **A frame timeline for scripts**: GameUI events -> OnUpdate (with sync points before/after) -> fixed steps (physics
   step, contact callbacks, OnFixedUpdate, sync) x N -> animation events -> OnLateUpdate -> end-of-frame destruction;
   where `Time::GetStepAlpha` becomes final. (Ties to the Scene/frame-loop chapter.)
8. **Crash containment flow (Windows and POSIX side by side)**: guarded call, fault, filter/handler, unwind or longjmp,
   `Invoke` returns false, `RecordFault`, module faulted, editor stops play; and the uncontained exits.
9. **Hot reload timeline**: build writes file, watcher debounce 300 ms, `Update` between frames, new module loads beside
   old, BeginModuleReload (snapshot, destroy), old module unloaded, EndModuleReload (recreate, restore), next sync
   point OnReload; failure branch keeps the old module; retry branch for a busy file.
10. **Update order maintenance**: a hierarchy tree, the flat order array with placed prefix and appended tail, a binary
    search insertion, tombstones and the 1/8 compaction.
11. **Symbolization**: stack of return addresses -> module + offset (at fault time) -> job -> PDB lookup with inline
    frames -> chosen location.
12. **The editor workflow loop**: edit source -> Build (CMake configure if files changed, build) -> load or hot reload ->
    Play (builds first if stale) -> crash -> Problems panel -> fix.

Screenshots (all from the editor; no rendering feature is involved, so no quality-row isolation is needed):

1. Scripts > New Script... dialog, and the file it opened in an external editor (MAN 9-44).
2. Inspector with a Script component: class picker, fields of every type with defaults and reset buttons (MAN 55-62).
3. Content Browser's Scripts root listing files with the classes they register (MAN 46-49).
4. Status bar pills: "Building", "Building to play", "Build failed · 2 errors", "Scripts crashed", "Scripts unused".
5. Problems panel with a compiler error (file, line) and with a crash and its stack frames, one marked "(inlined)"
   (MAN 183-198). Reproduce with the Faults test module or a deliberate null write in a sample copy.
6. Console showing the crash message and the location line, and a toast with Show Problems.
7. Hot reload in action: two screenshots of a playing sample (ThirdPerson's Coin spin speed changed in code) before
   and after a rebuild, with the log line "Reloaded script module ...".
8. External Editor preferences page listing found editors (MAN 74-92).
9. `script.status` output in a terminal (StrataCLI) showing classes, fields, callbacks and a fault (SKILL 696-721).
10. A game's options menu driving `Graphics::` (ThirdPerson's SettingsMenu) and a rebinding row using binding capture.

---

## 5. Rules and pitfalls (the "why" boxes)

1. **Only plain C data crosses the ABI** (no STL, engine types or exceptions; DG 1974-1978). Why: C++ layouts and
   exception models differ between compilers, versions and configurations; modules may be built with another compiler.
2. **Append, never insert, reorder or remove** host functions and callbacks; appending keeps the ABI version, anything
   else bumps it (DG 1997-2016). Why: old modules index the table by offset.
3. **Check `ST_SCRIPT_HAS_MEMBER` before using a function appended after the initial set** (SDK does it with
   `ST_SCRIPT_DETAIL_HOST_WITH`). Why: an older engine's table is shorter; reading past it is reading garbage.
4. **Frozen structs stay frozen** (`StrataScriptRaycastHit`, `StrataScriptCharacterState`). Why: the engine writes arrays
   of them into module buffers sized by the module's view.
5. **Every module call goes through `ScriptModule` (CrashGuard), including load and unload; read module memory only
   inside guarded calls and move complete results out** (DG 1987-1989). Why: a fault must never leave engine objects
   half-written, and module memory can be garbage.
6. **Host functions wrap their body in `HostCall`, start with `ResolveContext`, report misuse, return failure values,
   never assert** (DG 1990-1992). Why: no exception may unwind into the module; scripts are untrusted callers; an
   assert would kill the editor for a game bug.
7. **Engine is single-threaded towards scripts; call it only from callbacks, never from your threads** (ScriptABI.h
   25-26; SKILL 650). Why: the scene is owned by the main thread; `ResolveContext` refuses other threads.
8. **Script code never runs while engine state it could invalidate is in use: destroy through
   `ScriptSystem::DestroyEntity`** (AGENTS "Scripting"). Why: OnDestroy and destructors are script code that may touch
   the lists being walked.
9. **Classes are default-constructible and constructors have no side effects; initialize in OnCreate** (Script.h
   68-69). Why: the module constructs each class once at load to read defaults, and the engine applies fields after
   construction.
10. **One `ST_SCRIPT_CLASS` per class, in a .cpp, never in a header** (SKILL 70-77). Why: each translation unit would
    register it again; the engine refuses duplicate class names.
11. **Only fields survive hot reload; re-acquire everything else in OnReload** (Script.h 49-52; SKILL 552-553). Why:
    instances are deleted and reconstructed from new code; pointers into the old module are dangling.
12. **Never keep `T*` from `GetScript<T>()` across frames; store `Entity`** (SKILL 651-652). Why: the instance may be
    destroyed or reloaded.
13. **Exceptions disable an instance; crashes fault the module** (ARCH 3190-3193). Why: an exception left the module's
    state consistent (unwound); a crash did not, so nothing in that module is trusted again, and its instances are
    leaked on purpose.
14. **Never block in a script** (no sleeps, busy loops, synchronous I/O; SKILL 658). Why: native code cannot be
    preempted; the watchdog can only log.
15. **Request assets early; `Instantiate` never waits** (ScriptABI.h 368-370). Why: loading on the main thread would
    stall frames.
16. **Read press/release edges in OnUpdate, held state anywhere** (SKILL 133-137). Why: OnFixedUpdate runs zero or more
    times per frame.
17. **Read the drawn pose in OnLateUpdate for cameras; move ridden platforms in OnFixedUpdate** (MAN 157-175). Why:
    fixed-step motion is drawn interpolated one step behind.
18. **Use input actions for anything a player might rebind; only `InputActions` touches the bindings file; only
    `GameGraphicsService` touches `GraphicsOptions.json`; saves go through `IGameSaves`** (AGENTS "Scripting"). Why:
    one owner per file, and players' choices must survive.
19. **SDK helpers named like engine classes (`Random`, `Timer`) are tested only inside a module; no engine TU includes
    the SDK's C++ headers** (`Architecture.ScriptSDK`). Why: the one-definition rule.
20. **Windows modules must use the static C runtime and the SDK's entry points to contain `abort()`** (ScriptModuleEntry
    1-12). Why: a shared CRT's abort handler belongs to every user of that runtime.
21. **Hot reload runs a copy; `$ORIGIN`/`@loader_path` RUNPATH points at the copy's directory** (DG 2125-2128). Why: the
    original must stay writable for the build.
22. **Every new host function, SDK function, callback and field type must be exercised by the feature test** (golden
    rule 6; SKILL 776-803). Why: the call counters and SDK reader prove nothing is dead or untested.
23. **Field values convert exactly, component properties leniently** (ScriptValue.h 28-37). Why: fields are the
    script's own typed data; properties accept the natural script types for enums, colors and rotations.
24. **A crash inside the loader (static init/teardown) poisons that file for the process** (ScriptModule.h 63-68). Why:
    the platform loader may hand the half-initialized library out again.

---

## 6. Hands-on

For game developers:

1. **Hello script** (easy): New Script `Spinner`, rotate the entity in OnUpdate, add a `Speed` field, change it in the
   Inspector. Proves: lifecycle, fields, the build/attach/play loop.
2. **Hot reload a running game** (easy): in a copy of ThirdPerson, change `Coin::SpinSpeed`'s behavior while playing and
   rebuild; then add a non-field member and see it reset. Proves: what survives reload, OnReload.
3. **Pickup and score** (easy-medium): trigger collider + `OnTriggerEnter`, a UIText HUD, `Audio::PlayOneShot` with an
   early `Assets::RequestLoad`. Proves: contacts, UI text, asset requests.
4. **Spawner** (medium): `Timer` + `Scene::Instantiate` of a prefab field; handle "not loaded yet"; then
   `InstantiateMany` with 100 transforms. Proves: asynchronous assets, prefabs from scripts.
5. **Character and camera** (medium): `CharacterController` driven by `Gameplay/Move` and `Gameplay/Jump` actions, a
   follow camera in OnLateUpdate with `GetDrawnPosition` and a wall raycast. Proves: input actions, fixed vs frame
   update, interpolation.
6. **Pause and settings menu** (medium): time scale 0, unscaled time, `OnUIClick`, a graphics preset row with
   `Graphics::SetPreset` and `Save`, a rebind row with `BeginBindingCapture`/`PollBindingCapture`. Proves: player-facing
   services.
7. **Save and load** (easy-medium): `Game::WriteSaveFile`/`ReadSaveText` of a checkpoint; invalid names fail. Proves:
   save files and their rules.
8. **Crash on purpose** (easy): write through a null pointer in OnUpdate, read the Problems panel; then throw an
   exception instead and compare (one instance disabled vs module faulted). Proves: containment semantics.
9. **Deterministic replay** (medium): seed `Random` from a field, record outcomes, reproduce them. Proves: PRNG
   determinism.

For engine developers:

1. **Trace one host call** (easy): follow `Time::SetTimeScale` from the SDK to `HostSetTimeScale` and the counted thunk;
   explain each guard. Proves: the call path.
2. **Add a host function end to end** (hard): e.g. `GetEntityCount`: append to `StrataScriptHostAPI`, implement
   `HostGetEntityCount`, append to `ST_SCRIPT_HOST_FUNCTIONS` (see the static_assert fail first), wrap in the SDK with
   `ST_SCRIPT_DETAIL_HOST_WITH`, test in the API module and a `Scripting.*` test, use it in a feature script. Proves:
   DG 1997-2016 in practice, ABI compatibility.
3. **Add a callback** (hard): e.g. `OnBecameVisible`: append to `StrataScriptClassDesc`, `ScriptCallback`,
   `CallbackFlag`, `ClassFunctions` with `ST_SCRIPT_HAS_MEMBER`, a thunk, dispatch. Proves: descriptor versioning.
4. **Simulate an old module** (medium): reason through (or write a test module like `NewerSDK`) what happens when a
   module's `StrataScriptModuleAPI` is larger/smaller than the engine's. Proves: `WriteModuleAPI`.
5. **Break the ABI and watch it refused** (easy): build a module with `ST_SCRIPT_ABI_VERSION 2` (the `ABIMismatch`
   test module does it); read the error. Proves: version checks.
6. **Crash guard lab** (medium-hard): write a tiny program around `CrashGuard::Invoke` that divides by zero, overflows
   the stack twice (why `_resetstkoflw`), and calls `abort()`; compare Windows and Linux. Proves: concept 11.
7. **Measure dispatch** (medium): run `Perf.Scripting.TrivialUpdate100k` (Release) with and without the prefetch lines;
   explain the result with ARCH 3166-3171. Proves: cache behavior.
8. **Exercise: why copy the list** (easy): find every "A copy: ... script code may change ..." comment in
   ScriptSystem.cpp and construct the bug each prevents. Proves: reentrancy reasoning.
9. **Exercise: design review** (medium): compare Strata's in-process containment with running scripts in a child
   process or WASM; list what each costs per call and what each contains. Proves: trade-offs.

---

## 7. Glossary

- **ABI (application binary interface)**: the binary contract between separately compiled code: layouts, calling
  conventions, symbol names.
- **ABI version**: `ST_SCRIPT_ABI_VERSION`, changed only by incompatible changes.
- **Append-only**: struct members are only ever added at the end, so old readers still find theirs.
- **Abandoned library/file**: a library whose static init or teardown crashed; kept loaded and its file only loaded
  from copies.
- **Active engine**: the `ScriptEngine` scenes use when they start playing (`SetActive`).
- **Alternate signal stack**: a separate stack POSIX delivers signals on, so a handler can run after a stack overflow.
- **AssetPin**: a hold that keeps an asset loaded regardless of memory budgets (from scripts' `RequestLoad`).
- **Binding capture**: listening for the next control a player presses, to rebind an action.
- **Buffer protocol**: host functions write at most `capacity` and return the full size; callers retry with a larger
  buffer.
- **Call site**: `ScriptCallSite`, who is being called (class, method, entity) for reports and the watchdog.
- **Callback**: a method of a script class the engine calls (OnUpdate...); null in the descriptor when not overridden.
- **Class descriptor**: `StrataScriptClassDesc`, a module's description of one script class.
- **Context**: `StrataScriptContext*`, opaque per-scene handle (the scene's ScriptSystem) every scene host function takes.
- **CrashGuard**: the engine's facility that runs a function and turns hardware faults into a false return.
- **CRT (C runtime)**: the C standard library implementation linked into a binary (static /MT or shared /MD on MSVC).
- **DbgHelp**: Windows library that reads PDBs and resolves addresses to functions, files and lines.
- **Debounce**: waiting until a file stopped changing for a while (300 ms) before acting.
- **Dispatch list**: the list of instances whose class implements one update callback.
- **Dist**: Strata's shipping configuration (asserts off, no host call counters).
- **Drawn transform**: where fixed-step motion is drawn this frame, interpolated between the last two steps.
- **Engine service**: a process-wide service a host program provides (`IGameSaves`, `IGameWindow`, `IGameGraphics`).
- **Entry point**: an exported function the loader looks up (`StrataScript_Load`).
- **Fault**: a crash inside script code; the module is marked faulted and never called again.
- **Feature test**: the test project that must exercise every host function, SDK function, callback and field type.
- **Field**: a public data member registered with `ST_SCRIPT_FIELD`: shown in the inspector, stored per entity, kept
  across hot reload.
- **Field override**: a per-entity stored value of a field (`ScriptEntry::Fields`).
- **Fixed update**: a callback run at a constant timestep, zero or more times per frame.
- **Frozen struct**: a struct without `StructSize` whose layout never changes within an ABI version.
- **Host**: the engine side of the ABI; the host API is its function table.
- **Host function**: one entry of `StrataScriptHostAPI`, implemented as `Host<Name>`.
- **Hot reload**: replacing the module while the game runs, keeping fields.
- **Inlining / inline frame**: the compiler copying a function into its caller; debug info can still name the copied
  function's line.
- **Instance**: one object of a script class for one Script component entry.
- **Interposition**: one library's symbol replacing another's of the same name; prevented by hidden visibility.
- **Module (script module)**: the shared library of a game's script classes.
- **Module description**: `StrataScriptModuleAPI`, filled by `StrataScript_Load`.
- **ODR (one-definition rule)**: C++ rule that a name has one definition per program; why SDK `Random` must not meet
  engine `Random`.
- **PCG32**: a small, fast, statistically good pseudo-random generator.
- **PDB**: Microsoft's program database (debug information) file.
- **Prefetch**: an instruction asking the CPU to load memory into cache ahead of use.
- **Private copy**: the copy of a module file the engine loads under hot reload, in a user-only directory.
- **ReportProblem**: the engine's warning for script API misuse, naming the calling script, logged once per message.
- **RUNPATH / `$ORIGIN`**: ELF search path for a library's dependencies; `$ORIGIN` is the loaded file's directory.
- **Scene service**: an interface a scene system offers to others (`IBodyControl`, `IAudioPlayback`...).
- **SDK**: the header-only C++ layer game code is written against.
- **SEH (structured exception handling)**: Windows mechanism (`__try/__except`) for hardware and software exceptions.
- **Signal**: POSIX asynchronous notification (SIGSEGV, SIGFPE...) a handler can catch.
- **`sigsetjmp`/`siglongjmp`**: save a point of execution and jump back to it, here out of a signal handler.
- **Stack guarantee**: Windows reserve kept at the end of a thread's stack for handling a stack overflow.
- **`StructSize`**: first member of an extensible struct; the size the writer (or capacity the reader) knows.
- **Symbolization**: turning addresses into module, function, file and line.
- **Sync point**: a moment with no script code on the stack where pending destroys, creations, OnReload and OnCreate
  run.
- **Thunk**: a small adapter function, here a C function that calls a C++ virtual.
- **Time scale**: multiplier on game time; unscaled time ignores it (pause menus).
- **Trigger**: a collider that reports overlaps without collision response.
- **Update order**: hierarchy order (parents first), then entry order on an entity.
- **Watchdog**: a thread that logs a script call running longer than a timeout.
- **X-macro**: a macro taking another macro as argument, to generate several lists from one.

---

## 8. Proposed chapters (teaching order)

1. **Game code and the engine: why scripts** (concept, both, S, 0 screenshots). The problem, the industry's approaches
   (interpreted, managed, visual, native), Strata's choice and its costs. Prerequisites: "What an engine is",
   "Entities and components".
2. **Your first script** (tutorial, game, M, 5 screenshots). New Script, fields, attach, Play builds first, hot reload,
   crash on purpose, the Problems panel. Prerequisites: "The editor tour", chapter 1.
3. **The script lifecycle and the frame** (concept, both, M, 1). Callbacks, order, fixed vs frame updates, input edges,
   destruction at frame end, OnReload; figure 6 and 7. Prerequisites: "The frame loop and fixed timestep", ch. 2.
4. **The gameplay API, part 1: entities, components, transforms, spawning, assets** (reference + tutorial, game, L, 2).
   `Entity`, `Component`, `TransformComponent`, `Scene`, `Assets`, `SubScene`, asynchronous spawning. Prerequisites:
   ch. 3, "Assets and handles".
5. **The gameplay API, part 2: physics, characters, audio, animation from scripts** (reference + tutorial, game, L, 2).
   `RigidBody`, `Physics`, contacts, `CharacterController`, `AudioSource`/`Audio`, `Animator`, drawn poses for cameras.
   Prerequisites: ch. 4 and the Physics, Audio, Animation chapters (or their concept sections).
6. **The gameplay API, part 3: the player's side** (reference + tutorial, game, L, 3). Input devices and actions,
   rebinding with capture, game UI callbacks, time scale and unscaled time, game flow and loading screens, window, save
   files, graphics options, worlds. Prerequisites: ch. 4, "Game UI", "Input actions", "Quality settings".
7. **Building blocks and recipes** (tutorial, game, M, 1). `Random`, `Timer`, `KeyRepeat`, `Motion`; recipes from the
   samples (Coin, FollowCamera, Tetris board); exercises. Prerequisites: ch. 4-6.
8. **Building and shipping script modules** (concept + reference, both, M, 2). What a module is, the CMake function and
   package, toolchains, IDE presets, where builds go, export and the runtime, debugging with a debugger. Prerequisites:
   ch. 2, "Shared libraries" (taught here if not before).
9. **Shared libraries and binary interfaces** (concept, engine, M, 0). DLLs, symbols, loading, ABI vs API, why C, struct
   versioning patterns (figure 4). Prerequisites: C++ basics chapter.
10. **Inside the ABI and the SDK** (internals, engine, L, 0). ScriptABI.h tour, the host table, descriptors, the SDK's
    thunks, registration, override detection, `LoadModule` and `WriteModuleAPI` (excerpts 1-13). Prerequisites: ch. 9,
    templates and macros primer.
11. **Loading, calling and validating modules** (internals, engine, L, 0). `ScriptModule`, load modes and copies,
    validation, `Call`, `ScriptEngine`, active engine (excerpts 14-15, 20, 25). Prerequisites: ch. 10.
12. **Crash containment** (internals, engine, L, 0). Hardware exceptions, SEH and signals, CrashGuard on Windows and
    POSIX, abort, what is not contained, exceptions vs crashes, the watchdog, symbolization (excerpts 16-19, 21;
    figures 8, 11). Prerequisites: ch. 11, "How a CPU runs code: stacks and calls" primer.
13. **ScriptSystem: instances in a playing scene** (internals, engine, L, 0). Instances, sync points, reconciliation,
    update order and dispatch lists, prefetching, contacts/animation/UI events, asset pins (excerpts 26-29; figure 10).
    Prerequisites: ch. 11, "Scene and hierarchy internals".
14. **Hot reload** (internals, engine, M, 1). Watcher, copies, reload protocol in engine and scenes, what survives,
    failure handling (excerpt 28; figure 9). Prerequisites: ch. 11, 13.
15. **The host API: implementing and extending it** (internals + tutorial, engine, L, 0). `ResolveContext`, `HostCall`,
    validation and ReportProblem, services and layering, the X-macro table, call counters, adding a host function and a
    callback end to end, the feature test (excerpts 22-24). Prerequisites: ch. 10-13, "Scene services".
16. **Reference: the complete script API** (reference, game, XL, 0). Every SDK class and function grouped as in section
    1.2, with the host function each wraps and its failure behavior. Prerequisites: none (look-up).

---

## 9. Not determined

- Not read line by line: most of the 165 host function bodies (about 3,000 lines of ScriptHostAPI.cpp; I read
  diagnostics, time, entities, components/properties, transforms, Instantiate, assets, scripts, save write, window
  size, graphics describe, step alpha and the table), `ScriptSystem.cpp`'s update-order algorithm (894-1219), the
  reconciliation edge cases beyond what is shown, `ScriptValue.cpp`'s conversions in detail, `ScriptingComponents.cpp`
  serialization, `ScriptTypes.cpp`, `PosixCrashGuard.cpp`'s macOS recovery path (162-235), `WindowsSymbolizer.cpp`,
  `PosixSymbolizer.cpp`, both `DynamicLibrary` implementations.
- The SDK headers Input.h, Entity.h, Scene.h, Physics.h, CharacterController.h, Audio.h, Animator.h, Game.h, UI.h,
  World.h, Time.h, Log.h, Value.h were read by outline and selected bodies, not every line; Motion (Gameplay.h 222-321)
  was not read.
- The editor side (ScriptBuild, ScriptToolchain, ScriptProject, ScriptSources, ScriptEdit, EditorScriptCommands,
  ScriptBrowser, ScriptDialogs, EditorContext's script parts, the Problems panel) was taken from DG/MAN/SKILL, not the
  code; it belongs to the editor area's inventory.
- GameRuntime's script handling was located (GameRuntime.cpp 100-170) but not read.
- The tests were read by name (TEST_CASE titles), not by body; test script modules only by their header comments.
- The exact wave in which physics bodies, queries, audio and game flow were appended (before wave 3's 119 total) is
  not stated in the documents I read; I called them "pre-0.3.0 appends". Asset residency (wave 1) and scene streaming
  and animation (wave 2) come from DG 1887-1888, 1896-1897 and Roadmap lines 55, 232, 237, but the per-wave split of the
  first 100 functions is inferred.
- The feature test's runner (`StrataTests/src/FeatureTest/FeatureTestUtils.cpp`, `SDKReader.cpp`) and how the SDK reader
  parses headers were not read.
- Whether a build without the scripting module is possible: Roadmap 710-711 says it is not offered yet.
- Small doc inconsistency to resolve: `Core/Symbolizer.h` 9-12 says POSIX uses dladdr only, but
  `Platform/Posix/PosixSymbolizer.cpp` 33-48 reads the ELF `.symtab` on Linux (as DG 2139-2140 says).
