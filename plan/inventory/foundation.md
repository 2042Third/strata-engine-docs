# Inventory: Foundations of the engine (application, frame loop, threading, platform)

Area key: `foundation`. Surveyed at `main` 822a7a46 (engine version 0.7.0 in `CMakeLists.txt`, wave 8 in progress).
Scope read: `Strata/src/Strata/Core` (all 79 files), `Strata/src/Strata/Events` (4), `Strata/src/Strata/Math` (10),
`Strata/src/Strata/Engine` (4), `Strata/src/Platform` (GLFW, NoWindow, Windows, Posix; Vulkan only where the device is
made), `stpch.h`, `StrataTests/Architecture/Layers.json`, the tests under `StrataTests/src/Core`, `Engine`, `Math`,
`Platform`, and the documentation sections named below. Paths are relative to the repository root unless they start with
`Core/`, `Events/`, `Math/` or `Engine/`, which mean `Strata/src/Strata/<that>`.

Release key used below: "W1"/"W2" = waves 1 and 2 (landed 2026-10-10/11, first shipped in 0.3.0); "0.3.0" = in its
release notes; "0.4.0" = wave 4 (2026-10-19); "W8" = wave 8, landed on main after 0.7.0 and not yet released
(Docs/Roadmap.md "Status", lines 34-1098, and "Waves", 1099 on). "n/s" = the documents do not say.

Document abbreviations: **A** = Docs/Architecture.md, **DG** = Docs/DeveloperGuide.md, **AG** = AGENTS.md,
**RM** = Docs/Roadmap.md. Sections of A: "Targets and dependencies" 26-188, "Engine modules" 189-568 (Core, Events, Math
paragraphs 191-215, 239-241), "Layers" 569-618, "Composition root and registries" 619-714, "Application and frame loop"
715-859, "Frame profiler" 860-958, "Threading model" 1381-1445. Sections of DG: "Repository layout" 127-148, "Precompiled
headers" 223-255, "Optional modules" 256-287, "Windows subsystem" 316-338, "Code style" 919-937, "Architecture rules"
938-1085, "Platform seams" 1086-1145, "Fixed rate" 1384-1441, "Interpolation" 2468-2566, "Test rules and helper
processes" 782-813.

---

## 1. Features

### 1.1 Program start and the composition root

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Entry point | The one `main` of the editor and the runtime: reads the command line, connects stdio, installs the interrupt handler, calls the program's `CreateApplication`, runs the composition root, makes and runs the `Application`, returns its exit code, shuts the log down | `Engine/EntryPoint.h` 16-41 | A 159-188 (Targets), DG 316-338 | 0.3.0 (GUI subsystem); n/s for the rest |
| `ApplicationLaunch` | What `CreateApplication` returns: `Registration` options plus a `Create` factory, so registration happens before the application exists | `Engine/ApplicationLaunch.h` 18-30 | A 159-163, 680-686 | 0.4.0 |
| `GetProgramRun` / `ProgramRun` | Program-defined decision whether a run is Console (output matters) or Interactive (a person's window), taken before anything prints | `Engine/ApplicationLaunch.h` 24-27, `Core/Platform.h` 29-40 | DG 316-338, A 168-176 | 0.3.0 |
| Composition root `Engine::RegisterBuiltinModules` | Opens every registry, runs each engine module's `Register<Module>Module` from a table in layer order, then the asset pipeline and `Extra` registrations, then freezes the component and settings registries and logs the scene-system order; second call is a no-op with an error | `Engine/BuiltinModules.cpp` 118-180 (table 61-77), `Engine/BuiltinModules.h` | A 619-714, DG 1010-1043 (Module registration) | W1 (`module-foundation`, RM 41-45) |
| `ModuleRegistrationOptions` | `AssetPipeline` (tools hand in the importers so games never link them), `Extra` (games/tests register components and settings sections), `Exclude` (test a game without a module; Input/Scene/Renderer refused) | `Engine/BuiltinModules.h` 10-24 | A 660-686, DG 256-287 | W1; `Exclude` n/s |
| `GetBuiltinModuleNames`, `GetRegisteredModules`, `AreBuiltinModulesRegistered` | Introspection of the table and what registered | `Engine/BuiltinModules.cpp` 105-116, 176-179 | A 641-643 | n/s |
| Optional modules (`ST_WITH_PHYSICS/AUDIO/ANIMATION`) | Compile-time removal of a module; `#if` appears only in the composition root (and pipeline, runtime, tests) | `Engine/BuiltinModules.cpp` 19-27, 65-73 | DG 256-287 | 0.4.0 |
| Registration state machine | `NotRegistered -> Registering -> Registered`, atomic; registries verify they were opened (use before registration fails `ST_CORE_VERIFY` naming the root) | `Engine/BuiltinModules.cpp` 41-49, 118-131 | A 686-689 | W1 |

### 1.2 Application shell (App layer)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `ApplicationSpecification` | Name, working directory, command line, window spec, `WindowFactory`, `Headless`, `Modules` (engine module factories), `Jobs`, `MaxFrames`, `MaxTimestep` (0.25 s), `MaxFrameRate` | `Core/Application.h` 25-46 | A 715-760 | n/s; `Modules` 0.4.0 |
| `Application` singleton | Owns window, layer stack, module registry, main-thread queue, frame pacer; one instance at a time (`ST_CORE_VERIFY`) | `Core/Application.h` 48-144, `Core/Application.cpp` 64-124 | A 191-194, 715 | n/s |
| Startup order | Power-throttling opt-out, working directory, `JobSystem::Init`, window (or factory, or none), `Input::Reset`, modules made, ordered and started | `Core/Application.cpp` 64-112, 126-160 | A 766-775 | n/s |
| Frame loop `Run` / `RunFrame` | Clamped wall-clock timestep, try/catch around the frame, frame counting and `MaxFrames`, interrupt polling, frame pacer wait | `Core/Application.cpp` 226-344 | A 776-822 (hook table and numbered frame) | n/s |
| Frame skipping | Minimized window or a module's `Skip` sleeps 16 ms and does not count the frame | `Core/Application.cpp` 27-28, 307-329 | A 782-783 | n/s |
| Frame work time | `GetLastFrameWorkTime`: steps 1-7 minus module waits (`EngineFrame::WaitSeconds`) and out-of-work stages (`Present`) | `Core/Application.h` 92-97, `Core/Application.cpp` 337-338 | A 823-829 | W2/W8 (out-of-work stages) |
| `SubmitToMainThread` | Mutex-guarded queue of `std::function`, drained at frame start and after the last frame | `Core/Application.cpp` 196-200, 352-362, 274-277 | A 1436-1445 | n/s |
| `ReportFatalError` | Log critical, and for Interactive runs nobody reads, a native dialog with advice and the log path; `STRATA_ERROR_DIALOG_FILE` for tests | `Core/Application.cpp` 42-62 | A 177-188, DG 330-334 | 0.3.0 |
| Exit codes | 0, 1 (startup failed), 3 (usage), 130 (interrupted) | `Core/Application.h` 60-71, `Core/CommandLineOptions.h` 25-27 | DG 330, 137 | 0.3.0 |
| Shutdown order | Main-thread queue, `OnShutdown` (program), modules' `OnStop` reverse; destructor: layers top-down, `OnRelease` reverse, queue, `JobSystem::Shutdown`, queue, `OnShutdown` reverse, modules destroyed, window | `Core/Application.cpp` 114-124, 162-177, 274-283 | A 850-858 | 0.4.0 |
| `Layer` / `LayerStack` | Slices of app behaviour; layers update in stack order, events go top-down; overlays sit above layers; the stack owns raw `Layer*` and deletes them top-down | `Core/Layer.h`, `Core/LayerStack.h`, `Core/LayerStack.cpp` | A 191-195 | n/s (Hazel lineage) |
| `FramePacer` and `SetMaxFrameRate` | Fixed-interval schedule, no burst catch-up; changeable while running; editor idle throttling uses it | `Core/Timer.h` 51-104, `Core/Application.h` 99-103 | A 838-850 | W8 (high-resolution wait, RM 1566) |
| `Timer`, `Time::GetTime`, `Timestep` | Monotonic stopwatch; seconds since start as double; float seconds wrapper | `Core/Timer.h` 12-49, `Core/Timestep.h` | A 830 | n/s |
| `CommandLine`, `CommandLineOptions` | UTF-8 args, `--name value`/`--name=value`/`--flag`, sizes `WxH`; unknown-argument detection and usage text | `Core/CommandLine.h`, `Core/CommandLineOptions.h` | DG 137 | n/s |
| Interrupt handling | Ctrl+C / Ctrl+Break / console close (Windows), SIGINT/SIGTERM (POSIX) become a quit request the loop honours; a second one ends the process | `Core/Platform.h` 213-218, `Platform/Windows/WindowsPlatform.cpp` 730-815, `Platform/Posix/PosixPlatform.cpp` 908-995 | A 176-181, DG 326-330 | 0.3.0 |
| Windows GUI subsystem and `ConnectStandardStreams` | Editor/runtime link as GUI programs (`/ENTRY:mainCRTStartup`); Console runs attach to the parent's console, passed pipes are kept | `Platform/Windows/WindowsPlatform.cpp` 755-793, `StrataEditor/CMakeLists.txt`, `StrataRuntime/CMakeLists.txt` | DG 316-338, A 165-176 | 0.3.0 |
| Power-throttling opt-out | `Platform::DisableExecutionSpeedThrottling` (Windows 11 EcoQoS) at Application start | `Core/Application.cpp` 70-72, `Platform/Windows/WindowsPlatform.cpp` 394-412 | A 766-770 | n/s |

### 1.3 Engine modules

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `EngineModule` interface | Program-lifetime service with hooks `OnInit`, `GetStartFailure`, `OnBeginFrame` (Continue/Skip/Close), `OnUpdate`, `OnRenderUI`, `OnEndFrame`, `OnEvent`, `OnStop`, `OnRelease`, `OnShutdown`; `c_Name`; `GetDependencies` | `Core/EngineModule.h` 22-106 | A 715-797, DG 1044-1055 | 0.4.0 (`engine-modules`, RM 1186) |
| `EngineContext`, `EngineFrame`, `EngineFrameAction`, `EngineModuleStartFailure` | Data passed to hooks | `Core/EngineModule.h` 30-63 | A 721-727 | 0.4.0 |
| `EngineModuleRegistry` | Makes modules from factories, stable topological sort (Kahn, first ready in listing order), refuses null factories, duplicate names, missing required dependencies, cycles (reports only the cycle members); `Find<T>()` by `T::c_Name`, no RTTI | `Core/EngineModule.h` 108-139, `Core/EngineModule.cpp` 27-186 | A 728-733 | 0.4.0 |
| Built-in modules | `GraphicsModule` ("Graphics": makes the Vulkan device, swapchain, `Renderer::Init`, begin/present, back-buffer captures), `AudioModule`, `ImGuiModule` (requires Graphics), `ProjectModule` | `Strata/Renderer/GraphicsModule.{h,cpp}`, `Strata/Audio/AudioModule.h`, `Strata/ImGui/ImGuiModule.h`, `Strata/Project/ProjectModule.{h,cpp}` | A 734-750 | 0.4.0 |
| Programs' module lists | Editor windowed/headless/no-GPU, runtime windowed/headless | `StrataEditor/src/EditorApplication.cpp` 318-366, `StrataRuntime/src/RuntimeApplication.cpp` 473-488 | A 742-750 | 0.4.0 |
| Where the device is made | `GraphicsModule::OnInit` -> `GraphicsDevice::Create` -> `VulkanGraphicsDevice::Initialize` (`LoadVulkanLibrary`, `CreateInstance`, `SelectPhysicalDevice`, `CreateLogicalDevice`) | `Strata/Renderer/GraphicsModule.cpp` 26-61, `Platform/Vulkan/VulkanGraphicsDevice.cpp` 290-299, 460, 486-602, 929, 968 | A 290-293 | n/s |
| `EngineServices` | Process-wide typed provider slots (`Register<T>`, `Get<T>`, `ScopedProvider<T>`) for what modules cannot include: `IGameWindow`, `IGameSaves`, `IGameGraphics`, `IProjectSettings`, `IAudioOutput`, `IAssetGraphics` | `Core/EngineServices.h` 11-69 (interfaces 76-184) | A 202-206, DG 994-997 | n/s |

### 1.4 Events and window (Input and App layers)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Event classes | `EventType` (15 kinds), `EventCategory` bit flags (plain enum, avoids X11 `None`), `ST_EVENT_CLASS_TYPE/CATEGORY` macros, `Handled` | `Events/Event.h` 15-58, `ApplicationEvent.h`, `KeyEvent.h`, `MouseEvent.h` | A 216-220 | n/s |
| `EventDispatcher` | Type-checked dispatch to a `bool(T&)` handler that ORs into `Handled` | `Events/Event.h` 60-81 | A 216-220 | n/s |
| Event propagation | Application bookkeeping (resize -> minimized), then modules in dependency order, then layers top-down, stopping at `Handled`; unhandled `WindowClose` ends the loop (a layer can veto) | `Core/Application.cpp` 202-224 | A 216-220, 788 | 0.4.0 (modules) |
| `Window` interface and `WindowSpecification` | Pure interface: events, framebuffer size, content scale, vsync, modes (Windowed/Fullscreen/Borderless), resolution, cursor shape, clipboard, layout keys, icon, `GetVulkanPresentation` | `Core/Window.h` 101-213 | A 194-197, DG 1090-1110 | n/s; modes n/s |
| GLFW backend | `GLFWWindow`: GLFW init on first window (with the engine's Vulkan loader), callbacks translate into `Input::Process*` then events, `ProcessEvents` = `glfwPollEvents`, surface creation, Dock icon | `Platform/GLFW/GLFWWindow.{h,cpp}` (Create 132-138, Open 140-, callbacks 232-400, ProcessEvents 410-412, surface 677), `GLFWApplicationIcon.{h,cpp}` | A 194-197, DG 1090-1110 | n/s |
| No-window backend | `STRATA_WITH_GLFW=OFF`: `Window::Create` returns null with an error | `Platform/NoWindow/NoWindow.cpp` | DG 281-285, 1122-1129 | W8 (RM 1569) |
| `WindowFactory` / `Tests::StubWindow` | Inject a window (embedder, tests) | `Core/Application.h` 31-33, `StrataTests/src/StubWindow.h` | DG 1095-1098, 1130-1134 | n/s |
| `VulkanLoader`, `VulkanPresentation` | Window-side half of presentation, in App layer, so the renderer never includes GLFW | `Platform/Vulkan/VulkanLoader.{h,cpp}`, `VulkanPresentation.h` | DG 1104-1110 | W8 (sealing) |

### 1.5 Diagnostics: logging, asserts, profiling

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Log` | spdlog loggers "Strata" (core), "App" (client), "Script"; macros `ST_CORE_*`/`ST_*`; fmt formatting with glm formatters; flush on warn | `Core/Log.h`, `Core/Log.cpp` 193-265 | A 198-201, DG 923-927, AG Code style | n/s |
| `LogBuffer` | Thread-safe ring of recent entries with monotonic sequence numbers: the editor Console and `log.read` | `Core/Log.h` 44-66, `Core/Log.cpp` 56-117 | A 198 | n/s |
| `BackgroundLogSink` | Console and file written on a writer thread; warnings/errors flush before returning; bounded queue (65,536); `FlushFor` for console control handlers | `Core/BackgroundLogSink.{h,cpp}` | A 198-201, 1423-1425, DG 923-927 | W8 (RM 880-890) |
| Asserts and verifies | `ST_CORE_ASSERT`/`ST_ASSERT` (compiled out of Dist), `ST_CORE_VERIFY`/`ST_VERIFY` (always), pluggable `AssertHandler` (Break/Abort/Continue), debugger detection | `Core/Assert.h`, `Core/Assert.cpp`, `Core/Base.h` 10-21 | AG Code style | n/s |
| `ErrorThrottle` | Logs a repeating error once until cleared | `Core/ErrorThrottle.{h,cpp}` | n/s | n/s |
| Tracy macros | `ST_PROFILE_FRAME/FUNCTION/SCOPE/THREAD`, compiled out unless `STRATA_ENABLE_TRACY` | `Core/Profiling.h` 1-36, `CMakeLists.txt` 23, `Strata/CMakeLists.txt` 46-48 | DG 928-934 | n/s |
| `ST_PROFILE_STAGE` and `FrameProfiler` | Always-on main-thread stage timer: 12 built-in stages, nested self time, ring of 600 frames, summaries (mean, nearest-rank P50/P95, max), job-pool busy percentages, GPU stages attached late, listeners, snapshots, bound classification (CPU/GPU/Capped) | `Core/Profiling.h` 39-42, `Core/FrameProfiler.h` (stages 67-81), `Core/FrameProfiler.cpp` | A 860-958, DG 928-934 | W2 (`streaming-observatory`, RM 106-110); GPU stages 0.4.0; snapshot W8 |
| `Symbolizer`, `CrashGuard` | Names code addresses; contains faults in guarded calls (SEH / signals) | `Core/Symbolizer.h`, `Core/CrashGuard.h`, `Platform/*/*CrashGuard.cpp`, `*Symbolizer.cpp` | DG Scripting "Crash locations and containment" 2133 | n/s (belongs mainly to the scripting area) |

### 1.6 Threads and jobs

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `JobSystem` pools | Workers (hardware threads - 1, normal priority), I/O (2), Background (below normal priority, leaves 4 hardware threads to the frame, at least half) | `Core/JobSystem.h` 62-155, `Core/JobSystem.cpp` 410-453, 568-573 | A 1381-1410, DG 940-955 | n/s; background pool W2 (RM 121-124) |
| `Submit`, `SubmitIO`, `SubmitBackgroundPart`, `JobPriority` | Queue a job; priorities High/Normal/Low/Background; work started from background stays background | `Core/JobSystem.h` 15-25, 109-118, `Core/JobSystem.cpp` 460-500 | A 1386-1414, DG 940-955 | `SubmitBackgroundPart` W8 n/s |
| `JobHandle`, `Wait`, `WaitAll` | Shared job state; a waiter claims and runs an unstarted job itself (no deadlock, never runs other jobs) | `Core/JobSystem.h` 27-60, `Core/JobSystem.cpp` 33-81, 502-520 | A 1427-1433 | W2 (RM 123) |
| `ParallelFor` | Batches over `[0, count)`, caller runs batches, helpers dropped once all batches are taken | `Core/JobSystem.cpp` 357-401, 522-566 | A 1429-1433 | n/s |
| Inline fallback | Jobs before `Init`/after `Shutdown` run on the caller | `Core/JobSystem.cpp` 350-355, 218-220 | A 1427 | n/s |
| Exception containment in jobs | try/catch around every job and batch | `Core/JobSystem.cpp` 37-48, 381-392 | n/s | n/s |
| `GetStats` and `ThreadActivity` | Per-thread busy time and job counts under a sequence lock, read without stopping the pool | `Core/JobSystem.cpp` 88-163, 613-626 | A 916-919 | W2/W8 n/s |
| `SequenceLockedValue<T>` | Single-writer single-reader lock-free hand-off (audio thread) | `Core/SequenceLock.h` | A 1419-1420 | n/s |
| `ParallelClone` | Member-wise copy with large array members copied in parallel | `Core/ParallelClone.h` | n/s | n/s |
| `Platform::SetCurrentThreadName/Priority`, `SleepUntil` | Thread naming, priorities, precise sleep (Windows high-resolution waitable timer) | `Core/Platform.h` 131-143, `Platform/Windows/WindowsPlatform.cpp` 337-392, `Platform/Posix/PosixPlatform.cpp` 483-526 | A 838-845 | W8 (SleepUntil) |
| Threading model | Main thread owns scene, input, scripts, rendering submission; results return by polling or `SubmitToMainThread` (table of producers and hand-offs) | (rules) | A 1381-1445, AG Architecture rules, DG 940-955 | n/s |

### 1.7 Platform services, files and paths (Core layer + Platform/Windows, Platform/Posix)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Platform detection | Exactly one `ST_PLATFORM_*`; `#error` on 32-bit Windows, non-macOS Apple, others | `Core/PlatformDetection.h` | DG 1145 (OS list) | n/s |
| `Platform` static class | Executable path, user data/home dirs, fallback CJK fonts, debugger, process id/liveness/start time/uptime, memory (`GetProcessMemory`, peaks), physical memory, secure random, env vars, open with default app, `FindProgram`, error dialogs, binary stdio | `Core/Platform.h` 63-237, `Platform/Windows/WindowsPlatform.cpp`, `Platform/Posix/PosixPlatform.cpp` | A 191-210, DG 1086-1145 | `GetProcessMemory` W1 (RM 39-40); others n/s |
| Private directories and files | One contract: owner-only creation (0700 / protected DACL), existing dirs verified (no links), `WritePrivateFile` (exclusive temp + rename, 0600), `IsTrustedFile`, `ReadRegularFile`/`ReadTrustedFile` (check and read through one handle), `RenameNoReplace`, `GetUserRuntimeDirectory` (`STRATA_RUNTIME_DIR`) | `Core/Platform.h` 92-190, `Platform/Windows/WindowsFileSecurity.{h,cpp}`, `WindowsPlatform.cpp` 279-321, 603-706, `PosixPlatform.cpp` 415-460, 763-890 | AG Code style (private files), DG 926 | n/s |
| `FileSystem` | Exception-free reads (whole, prefix, range), atomic writes (temp + rename), queries, copy (no link following), UTF-8 conversions `FromUTF8`/`ToUTF8` (generic `/`), `RemoveTrailingSeparators`, containment (`IsInside`, `IsInsideResolved`), `GetUniquePath`, per-thread operation counter for "no file I/O on the main thread" tests | `Core/FileSystem.h`, `Core/FileSystem.cpp` (atomic write 102-135, UTF-8 341-350, counter 15-27) | A 199-200, AG Code style | n/s |
| `AtomicFileWriter`, `DocumentOutput` | Streaming atomic writer (1 MB buffer, `<path>.tmp<n>`, `Commit`/`Abort`) for huge documents on background threads | `Core/AtomicFileWriter.{h,cpp}`, `Core/DocumentOutput.h` | n/s (Scene documents section of A 1292) | n/s |
| `FileReader` | One open file read at explicit offsets by many threads (overlapped `ReadFile` / `pread`) | `Core/FileReader.h`, `Platform/*/*FileReader.cpp` | A 200-201 | n/s |
| `FileWatcher`, `FileChangeNotifier` | Background thread rescanning a tree (debounced), woken by OS notifications on Windows, polled elsewhere; `PollChanges` on the caller's thread | `Core/FileWatcher.{h,cpp}`, `Core/FileChangeNotifier.h`, `Platform/*/*FileChangeNotifier.cpp` | A 1415-1418 | n/s (asset-pipeline area) |
| `FileLock` | Exclusive cross-process lock, released when the process ends | `Core/FileLock.h`, `Platform/*/*FileLock.cpp` | A 201 | n/s |
| `BoundedRead` | Read a source to its end with a size cap, never trusting a stale size | `Core/BoundedRead.{h,cpp}` | n/s | n/s |
| `Process` | Child processes with captured/discarded/inherited output, piped input, timeouts, process-tree termination (job objects / process groups) | `Core/Process.h`, `Platform/*/*Process.cpp` | A 1422, DG 1139 | n/s (scripting builds area) |
| `DynamicLibrary` | RAII shared library with safe dependency search, truncated-file refusal, `Release` | `Core/DynamicLibrary.{h,cpp}`, `Platform/*/*DynamicLibrary.cpp` | DG 1137 | n/s (scripting area) |
| `SaveFiles` / `SaveDirectory` | Validated save names, atomic writes, size cap; `IGameSaves` provider | `Core/SaveFiles.{h,cpp}` | A 207-209, DG Gameplay API | n/s (scripting area) |
| `SettingsRegistry`, `ProjectSettings` | Settings sections and the project's values (`IProjectSettings`) | `Core/SettingsRegistry.{h,cpp}`, `Core/ProjectSettings.{h,cpp}` | DG "Project settings" 1146 | 0.6.0 (belongs to the project-settings area) |
| Sockets | `Platform/*/*Socket.cpp` live in Platform but belong to the Network (tooling) layer | `Platform/Windows/WindowsSocket.cpp`, `Platform/Posix/PosixSocket.cpp` | A 586 | n/s (automation area) |
| `WindowsUtils` | `Utf8ToWide`/`WideToUtf8` at Win32 boundaries | `Platform/Windows/WindowsUtils.h` | n/s | n/s |

### 1.8 Math (Core layer)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Conventions | Right-handed, +Y up, -Z forward (glTF); D3D clip space through NVRHI (NDC +Y up, depth 0-1); reversed Z | `Math/Math.h` 9-11 | A 239-241, AG Renderer conventions | n/s |
| Transforms | `DecomposeTransform` (rejects non-finite/degenerate, folds reflection into X), `ComposeTransform`, `ComposeWorldTransform` (one compiled multiply so FMA contraction cannot make paths disagree) | `Math/Math.h` 13-21, `Math/Math.cpp` 9-69 | n/s | n/s |
| Projections | `PerspectiveReverseZ`, `PerspectiveReverseZInfinite`, `OrthographicReverseZ` | `Math/Math.cpp` 71-91 | AG Renderer conventions | n/s |
| Rotations | Euler degrees <-> quaternion, forward/right/up, `LookRotation` with up fallback, `IsNearlyEqual` (quat sign-agnostic) | `Math/Math.h` 30-55, `Math/Math.cpp` 93-119 | n/s | n/s |
| `AABB` | Empty-by-default box, expand, contains, intersects, `Transformed` (Arvo) | `Math/AABB.h`, `Math/AABB.cpp` | n/s | n/s |
| `Frustum` | Gribb-Hartmann plane extraction for 0-1 depth either direction, infinite far handled; point/sphere/AABB (positive vertex) tests | `Math/Frustum.{h,cpp}` | n/s | n/s |
| `Ray` | `FromNDC` (works with infinite reversed Z), ray-AABB (slabs), sphere, plane, triangle (Moller-Trumbore) | `Math/Ray.{h,cpp}` | n/s | n/s |
| `Random` | Thread-local mt19937_64, seeded from `random_device`; `Seed` for reproducibility | `Math/Random.{h,cpp}` | A 241 | n/s |

### 1.9 Core utilities

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| `Ref`/`Scope`/`WeakRef`, `CreateRef`/`CreateScope` | Aliases of `shared_ptr`/`unique_ptr`/`weak_ptr` | `Core/Base.h` 40-61 | AG Conventions | n/s |
| Base macros | `ST_DEBUGBREAK`, `ST_BIT`, `ST_BIND_EVENT_FN`, `ST_DEFINE_ENUM_FLAG_OPERATORS`, `ST_ENABLE_ASSERTS` | `Core/Base.h` 10-37 | AG Naming | n/s |
| `UUID` | 64-bit random non-zero id, 16 hex digits, `std::hash` | `Core/UUID.{h,cpp}` | A asset sections | n/s |
| `Hash` | FNV-1a 64 (constexpr), `Combine`, CRC-32C with hardware instructions | `Core/Hash.{h,cpp}` | A 203-204 | n/s |
| `Crypto` | SHA-256, HMAC-SHA256, constant-time compare, hex | `Core/Crypto.{h,cpp}` | A 204 (automation security) | n/s |
| `Base64` | Strict RFC 4648 | `Core/Base64.{h,cpp}` | n/s | n/s |
| `BinaryWriter`/`BinaryReader` | Little-endian, bounds-checked, sticky failure | `Core/BinaryStream.h` | n/s | n/s |
| `JsonUtils`, `JsonEvents` | Exception-free nlohmann parsing/dumping, typed getters, progress, SAX parse | `Core/JsonUtils.{h,cpp}`, `Core/JsonEvents.h` | A 205 | n/s |
| `StringUtils` | ASCII case, thousands separators, invalid UTF-8 repair | `Core/StringUtils.h` | n/s | n/s |
| `RadixSort`, `SortIndices` | Stable LSD radix sort that skips constant bytes | `Core/RadixSort.{h,cpp}` | (Render scene) | n/s |
| `RangeAllocator` | Offset allocator with size-class free lists, coalescing, bounded compaction planning | `Core/RangeAllocator.{h,cpp}` | DG "Batching" | n/s |
| `AmortizedCheck` | Paces whole-structure Debug validation by a per-call element budget | `Core/AmortizedCheck.h` | DG 1076-1081 | n/s |
| `Prefetch` | Cache-line prefetch hint | `Core/Prefetch.h` | n/s | n/s |
| `EmbeddedFiles` | Default font compiled in | `Core/EmbeddedFiles.h`, `CMake/StrataEmbeddedFiles.cmake` | A 104 | n/s |
| `Version.h` | Version macros and `c_EngineCommit` generated by CMake | `Core/Version.h.in` | A 109-113 | n/s |
| Precompiled header `stpch.h` | Standard library, EnTT, nlohmann, Core basics; every engine `.cpp` includes it first | `Strata/src/stpch.h` | DG 223-255 | 0.4.0 (faster builds) |

### 1.10 Layers as the build

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Layer table | 21 layers with `Paths`, `Exclude`, `MayInclude`, `Tooling`, `Option`, `Notes`, `ExternalOwners`, `MaxAllowlistEntries` (0) | `StrataTests/Architecture/Layers.json`, `LayeringAllowlist.txt` | A 569-618, DG 984-1009 | W1; libraries 0.4.0 |
| Per-layer static libraries | `strata_add_layer_libraries` makes `Strata_<Layer>` linking exactly `MayInclude` | `CMake/StrataLayers.cmake` | A 28-43 | 0.4.0 |
| `Architecture.Layering`, `.Libraries`, `.PrecompiledHeaders`, `.HeaderWeight` tests | Include analyzer and build checks | `StrataTests/src/Architecture/` | A 597-610, DG 230-255 | W1/0.4.0 |
| `ExternalOwners` | GLFW, Vulkan and OS headers only in their Platform folders | `Layers.json` | DG 1111-1120 | W8 |
| Tooling-free runtime | `strata_check_link_closure`, `StrataRuntime.NoTooling` linker-map check | `CMake/`, `StrataTests/Architecture/CheckNoTooling.cmake` | A 79-90 | 0.4.0 |

### 1.11 Time and the fixed step (lives in Scene, used by every game)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Variable timestep | Wall time since the previous frame, clamped to 0.25 s | `Core/Application.cpp` 237-240 | A 830 | n/s |
| Fixed-step accumulator | `Scene::OnUpdateRuntime`: `OnUpdate`, then due `OnFixedUpdate` steps up to `GetMaxFixedSteps`, backlog dropped, then `OnLateUpdate`; time scale; unscaled time | `Strata/Scene/Scene.cpp` 2199-2330, `Scene.h` 425-490 | DG 1384-1441, 2468-2566 | 0.3.0 (time dilation: release notes 0.3.0 line 60) |
| Time dilation | Stops catch-up steps when they take longer in wall time than they simulate | `Strata/Scene/Scene.cpp` 2272-2304 | `Scene.h` 465-472 | 0.3.0 |
| Pause and `Step` | Advance exactly one fixed step per frame while paused; `GetFixedStepCount` as the tools' clock | `Strata/Scene/Scene.h` 427-438 | AG Editor ("Tools count game time in fixed steps") | n/s |
| Project `Scene.Timing` `FixedRate` | 30/60/120/240 steps per second overriding scenes; max steps `ceil(rate*2/15)` | `Strata/Scene/ProjectSceneTiming.h`, `Scene.cpp` 230-251 | DG 1384-1441 | W8 (RM 1568) |
| Interpolation | Drawn transforms between the last two step poses, `m_StepAlpha` | `Strata/Scene/Scene.cpp` 2313-2321, `Scene/SceneInterpolation.cpp` | DG 2468-2566 | W8 |

### How completeness was checked

- Every file of `Core/` (79), `Events/` (4), `Math/` (10), `Engine/` (4) and `Platform/{GLFW,NoWindow,Windows,Posix}` was
  listed with `find` and is accounted for in a row above (Core files outside this area's teaching focus are listed with
  the area that should teach them: CrashGuard/Symbolizer/DynamicLibrary/Process/SaveFiles -> scripting, FileWatcher ->
  asset pipeline, SettingsRegistry/ProjectSettings -> project settings, sockets -> automation).
- Every engine module implementing `EngineModule` was found by searching `: public EngineModule` (Graphics, Audio,
  ImGui, Project, plus three test modules).
- Every row of `c_BuiltinModules` (9: Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI) and
  every built-in frame stage of `c_BuiltinFrameStages` (12) is named.
- Every `Platform::` function was listed from both `WindowsPlatform.cpp` and `PosixPlatform.cpp` (41 functions each).
- No component, command, asset type, host function or shader entry is registered by this area itself; `Scene.Timing`
  (a settings section) is registered by the Scene module and noted in 1.11.

---

## 2. Concepts to teach (dependency order)

1. **What a program is, and what an engine adds.** Process, `main`, executable vs library, static vs shared libraries,
   the build. Engines in general: a reusable runtime (loop, platform, rendering, assets, simulation) plus tools.
   Strata: three executables over one set of static layer libraries (editor, runtime, CLI), game code as separately
   loaded script modules. Newcomers think the editor *is* the engine; in Strata the runtime runs games without any
   editor code, proven by a linker-map test (A 79-90).

2. **The game loop.** Why games loop instead of waiting for events like a desktop app: the world changes without input.
   General forms: fixed frame rate, variable delta, fixed update with variable render (Glenn Fiedler's "Fix your
   timestep", Robert Nystrom's "Game Programming Patterns: Game Loop"). Strata: `Application::Run` measures wall time,
   clamps it to 0.25 s, runs `RunFrame`, paces. Mistake: thinking a frame is "one update"; in Strata a frame contains
   zero or several fixed steps.

3. **Stages of a frame.** Input, update, UI, render submission, present; why ordering matters (input before update,
   present last). Strata's order is a numbered table (A 805-822) and its hooks a fixed contract; modules end in reverse
   order. Mistake: drawing before the input of the frame is polled, or presenting before UI.

4. **Time.** Wall clock vs monotonic clock (`steady_clock`), double for absolute time and float for deltas, the clamp
   against breakpoints and hitches, frame counting vs game time. Strata: `Time::GetTime` (double, since start),
   `Timestep` (float). Mistake: using `system_clock` (it jumps) or float absolute time (precision loss after hours).

5. **Fixed timestep, accumulator, spiral of death, interpolation, time scale.** Approaches: lockstep, semi-fixed,
   accumulator with max steps, time dilation, render interpolation vs extrapolation. Strata: accumulator with
   `GetMaxFixedSteps` (2/15 s of steps at the project rate), backlog dropped, optional time dilation (wall-clock owners
   only, so tests stay deterministic), interpolation one step behind, `Step` while paused, tools count fixed steps.
   Mistake: physics in `OnUpdate`, counting frames in tests, forgetting teleports need `BreakInterpolation`.

6. **Frame pacing and vsync.** Present modes (FIFO), driver overrides, frame-rate caps for headless runs, sleeping
   precision (Windows' 15.6 ms timer tick; `timeBeginPeriod` changes the whole system), fixed-interval schedules without
   catch-up bursts. Strata: `FramePacer` + `Platform::SleepUntil` with a high-resolution waitable timer; work time
   excludes waits. Mistake: measuring "frame time" including the vsync wait, then "optimizing" a capped frame.

7. **Events vs polling.** Callbacks from the OS window system, an event object hierarchy, dispatch by type, `Handled`
   propagation, observers. Strata: synchronous events (`Event`, `EventDispatcher`) plus a polling `Input` state that
   the window feeds before the event; modules see events before layers; an unhandled close ends the loop, so a layer can
   veto (unsaved changes). Mistake: doing game input through events (miss held keys) or assuming events are queued
   (they run inside `glfwPollEvents`).

8. **Layers and overlays.** Splitting an application into stacked slices (Hazel-style `LayerStack`): update bottom-up,
   events top-down. Strata: the editor and the runtime each push one layer; ImGui's module pushes an overlay. Mistake:
   ownership: the stack deletes raw `Layer*` it was given.

9. **Subsystems and their lifecycles.** Init order, dependencies, reverse shutdown, failure during startup. General
   approaches: hard-coded init in `main`, singleton managers with explicit `StartUp`/`ShutDown` (Gregory, "Game Engine
   Architecture"), plugin/module systems (Unreal's `IModuleInterface`), service locators. Strata: `EngineModule` with
   declared dependencies, stable topological sort, a fixed hook table, start failures that clean up and explain
   themselves; `Application` never names a module. Mistake: a module that frees GPU assets after the device is gone
   (why `OnRelease` comes before `JobSystem::Shutdown` and `OnShutdown`).

10. **Topological sorting.** Graphs, in-degree, Kahn's algorithm, stability, cycle detection and reporting. Strata's
    registry reports only true cycle members (EngineModule.cpp 131-160).

11. **Layered architecture and dependency inversion.** Why lower code must not call higher code; interfaces below,
    registries filled from above, services. Strata: an enforced layer table that *is* the build (one static library
    per layer, linking only what it may include), `ExternalOwners` for OS/GLFW/Vulkan headers, an empty allowlist.
    Mistake: "fixing" a forbidden include by widening `MayInclude`.

12. **Composition root and registries.** Self-registration through static initializers (common, fragile: the linker
    drops unreferenced objects of static libraries; initialization order is undefined) vs an explicit composition root.
    Strata: `Engine::RegisterBuiltinModules`, a table in layer order, registries that open, accept, freeze; use before
    registration fails loudly; tooling handed in so games never link it. Mistake: registering a component after the
    freeze, or from a static constructor.

13. **Ownership in C++.** RAII, destructors, `unique_ptr`/`shared_ptr`/`weak_ptr`, move semantics, why aliases
    (`Scope`/`Ref`). Strata: `Ref`/`Scope` everywhere, registries own modules through `Scope` and expose raw pointers.
    Mistake: holding `Ref`s to assets across frames (the asset rules ask for handles), or a lambda capturing the last
    reference of something that must die on a particular thread (see 17).

14. **Errors: asserts, verifies, results, exceptions.** Programmer errors vs recoverable failures; compiled-out
    asserts (side effects vanish in Dist); verifies that stay; return values (`bool`, `std::optional`, result structs);
    engine code does not throw, third-party exceptions are caught at the call site, the frame loop catches what escapes.
    Mistake: asserting on file contents or user input.

15. **Logging.** Levels, loggers, sinks, patterns, ring buffers for in-app consoles, asynchronous writing, flush policy
    (warnings flush so they survive a crash). Strata: spdlog with three loggers, `LogBuffer`, `BackgroundLogSink`.
    Mistake: logging every frame (use `ErrorThrottle`), logging secrets (the automation token).

16. **Threads and synchronization basics.** Threads, data races, mutexes, condition variables, atomics and memory
    order (acquire/release, fences), thread-local storage. Strata examples: `ThreadActivity`'s sequence lock,
    `JobState` claim flag, `t_` thread-locals.

17. **Job systems.** Thread pools, task graphs, work stealing, fibers (Naughty Dog's GDC 2015 talk), priorities,
    blocking I/O pools. Strata: three central-queue pools (workers, I/O, background), a waiter runs the job it waits for
    if unstarted (claim by atomic exchange) and never others, `ParallelFor` with caller participation and dropped
    helpers, inline fallback, priorities that keep frame work on normal-priority threads and leave four hardware threads
    free. Why: measured stalls (BC7 compression stretching 3 ms frames to 10-30 ms; A 1392-1404). Mistakes: waiting on a
    job from a job in a naive pool (deadlock), a waiter that picks up unrelated long jobs, `std::function` moved but not
    emptied (libc++ copies small callables) so captured objects die on the wrong thread.

18. **Threading model of an engine.** Main-thread ownership of mutable world state vs fully parallel engines; hand-off
    by queues and polling instead of callbacks from workers. Strata's table of producers and consumers (A 1434-1445).
    Mistake: a worker callback touching the scene.

19. **OS scheduling and power.** Priorities, scheduling quanta, hybrid CPUs (P/E cores), Windows 11 power throttling
    of background windows. Strata: `ThreadPriority::BelowNormal` for background pools, `DisableExecutionSpeedThrottling`.

20. **Profiling.** Instrumentation vs sampling, zones, frame markers, Tracy; always-on low-cost stage timers; self time
    vs inclusive time; percentiles (nearest rank) instead of averages; CPU-bound vs GPU-bound vs capped; GPU timestamps
    arriving frames late. Strata: `FrameProfiler` (0.6 microseconds per frame of 16 stages), its 90% rules.
    Mistake: reading P50 as "frame time" while P95 stutters; wrapping nanosecond calls in stages.

21. **Platform abstraction.** Preprocessor detection, link-time selection of implementations (one interface,
    `Platform/<OS>/` files compiled per OS) vs virtual backends, window libraries (GLFW, SDL), where OS headers may
    appear. Strata: static `Platform` class with per-OS `.cpp`, `Window` interface with GLFW and NoWindow backends,
    `ExternalOwners`. Mistake: including `<Windows.h>` in a header (macros like `near`, `CreateWindow`), X11's `None`.

22. **Program kinds on Windows.** Console vs GUI subsystem, attaching to a parent console, why PowerShell does not wait
    for GUI programs, signals and console control handlers, async-signal safety, exit codes. Strata: `ProgramRun`,
    `ConnectStandardStreams`, `InstallInterruptHandler`, exit code 130.

23. **Text and paths.** Unicode, UTF-8 vs UTF-16, Windows' wide APIs, `std::filesystem::path` constructed from narrow
    strings (ANSI code page on Windows), `u8string`/`char8_t`. Strata: UTF-8 `std::string` everywhere, `FromUTF8`/
    `ToUTF8` at boundaries, generic `/` separators. Mistake: `path(std::string)` on Windows.

24. **Safe file writing and trust.** Partial writes and crashes, temp-file-plus-rename atomicity, Windows rename
    retries, TOCTOU races, permissions (POSIX modes, Windows DACLs), symbolic links and junctions. Strata: atomic writes
    everywhere, private files through one handle.

25. **Math for engines.** Vectors, matrices (column-major glm), homogeneous coordinates, TRS composition and
    decomposition, quaternions (double cover), Euler angles, handedness and up axis, projection matrices, NDC, depth
    precision and reversed Z, frustum plane extraction, bounding volumes and culling tests, ray casting. Strata picks
    glTF conventions and reversed Z with an infinite far plane option. Mistakes: mixing row/column major, comparing
    quaternions component-wise, expecting a 0-1 depth range to behave like OpenGL's -1..1, FMA making "the same" product
    differ (why `ComposeWorldTransform` is one function).

26. **Utilities engines need.** Stable hashes vs `std::hash`, UUIDs, CRCs for corruption, cryptographic hashes and HMAC
    for authentication, constant-time compares, base64, binary serialization and validating untrusted lengths, radix
    sort, offset allocators, amortized checks.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `Strata/src/Strata/Engine/EntryPoint.h` 16-41 | The whole life of a program in 25 lines: streams, interrupt handler, launch, registration, run, exit code | functions, `std::optional`, `unique_ptr` |
| 2 | `Strata/src/Strata/Engine/BuiltinModules.cpp` 61-77 and 118-174 | A composition root: a table of registration functions in layer order, `#if ST_WITH_*` only here, open-register-freeze | function pointers, static vs dynamic init |
| 3 | `Strata/src/Strata/Core/Application.cpp` 226-283 | The game loop: clamped delta, try/catch, frame count, interrupt, pacer, ordered shutdown | concept 2, 4 |
| 4 | `Strata/src/Strata/Core/Application.cpp` 285-344 | One frame: main-thread queue, Input stage, minimized skip, module/layer hook order, work time | excerpt 3, `EngineModule` |
| 5 | `Strata/src/Strata/Core/Application.cpp` 64-112, 126-160 | Startup with failure paths that unwind in order and report to a person | RAII, excerpt 7 |
| 6 | `Strata/src/Strata/Core/Application.cpp` 202-224 | Event propagation with `Handled`, and the close veto | excerpt 9 |
| 7 | `Strata/src/Strata/Core/EngineModule.h` 22-106 | Designing a lifecycle interface: hook contract written in comments, Skip/Close | virtual functions |
| 8 | `Strata/src/Strata/Core/EngineModule.cpp` 49-186 (Kahn 95-130, cycle report 131-160) | Stable topological sort and error messages naming only cycle members | graphs |
| 9 | `Strata/src/Strata/Events/Event.h` 15-81 | An event hierarchy with type ids without RTTI, category bit flags, templated dispatcher | enums, templates |
| 10 | `Strata/src/Strata/Core/LayerStack.cpp` 7-54 | Layers vs overlays with one insert index; detaching top-down | `std::vector` |
| 11 | `Strata/src/Platform/GLFW/GLFWWindow.cpp` 225-330 | Turning C callbacks with a user pointer into engine events, feeding the polled `Input` first | function pointers, lambdas |
| 12 | `Strata/src/Strata/Core/Base.h` 10-61 | `Scope`/`Ref` aliases, `ST_BIND_EVENT_FN`, flag operators for `enum class` | templates, perfect forwarding |
| 13 | `Strata/src/Strata/Core/Assert.h` 52-73 and `Assert.cpp` 32-66 | Assert vs verify macros (`do { } while (false)`, `[[unlikely]]`, compiled out in Dist), pluggable handler | preprocessor |
| 14 | `Strata/src/Strata/Core/Log.cpp` 193-265 | Building loggers from sinks: ring buffer sink, async writer, file sink, flush-on-warn | concept 15 |
| 15 | `Strata/src/Strata/Core/BackgroundLogSink.h` 21-89 | Asynchronous logging contract: ordering, flush semantics, bounded queue, stop | mutex, condition variable |
| 16 | `Strata/src/Strata/Core/JobSystem.cpp` 33-81 and 502-514 (`ExecuteJob`, `TryRunJob`, `DropJob`, `Wait`) | Claim-by-exchange: whoever claims first runs it; waiting without deadlock | atomics, condition variables |
| 17 | `Strata/src/Strata/Core/JobSystem.cpp` 165-313 (`JobPool`, `ThreadMain` 274-304) | A thread pool with priority queues and draining shutdown | excerpt 16 |
| 18 | `Strata/src/Strata/Core/JobSystem.cpp` 357-401 and 522-566 | `ParallelFor`: atomic batch counter, caller participation, dropping helpers, lifetime via shared state | excerpt 16 |
| 19 | `Strata/src/Strata/Core/JobSystem.cpp` 335-342, 460-474 | A real-world bug class: `std::function` moved but not emptied by libc++; where captures die | move semantics |
| 20 | `Strata/src/Strata/Core/JobSystem.cpp` 88-163 or `Core/SequenceLock.h` 13-66 | Sequence lock: odd sequence while writing, fences, retry | memory order |
| 21 | `Strata/src/Strata/Core/FrameProfiler.cpp` 409-434 (with `Core/Profiling.h` 39-42 and `FrameProfiler.h` 386-406) | Self-time accounting of nested scopes with a fixed-depth stack; RAII scope; static stage id per call site | RAII, `static` locals |
| 22 | `Strata/src/Strata/Core/Timer.h` 51-104 | Fixed-interval frame pacing without catch-up bursts | concept 6 |
| 23 | `Strata/src/Platform/Windows/WindowsPlatform.cpp` 337-380 | Precise sleep on Windows (high-resolution waitable timer, thread-local) | Win32 handles |
| 24 | `Strata/src/Platform/Posix/PosixPlatform.cpp` 900-922 and 981-995 | Async-signal-safe interrupt handler: count, and re-raise on the second | signals |
| 25 | `Strata/src/Platform/Windows/WindowsPlatform.cpp` 755-793 | Console vs GUI subsystem: keeping passed pipes, attaching to a parent console | concept 22 |
| 26 | `Strata/src/Strata/Core/FileSystem.cpp` 102-135 and 341-350 | Atomic write (temp, flush, rename, cleanup) and UTF-8 path conversion via `char8_t` | `std::filesystem` |
| 27 | `Strata/src/Strata/Core/Platform.h` 92-129 | Writing a security contract as an interface comment (private directories) | permissions |
| 28 | `Strata/src/Strata/Scene/Scene.cpp` 2239-2329 | The fixed-step accumulator with max steps, time dilation, backlog drop and interpolation alpha (the central time algorithm) | concept 5 |
| 29 | `Strata/src/Strata/Math/Math.cpp` 71-91 and `Math/Frustum.cpp` 12-35, 57-73 | Reversed-Z projections (swap near/far; infinite far) and plane extraction / positive-vertex AABB test | matrices, NDC |
| 30 | `Strata/src/Strata/Core/EngineServices.h` 21-69 | A minimal typed service locator with variable templates and scoped providers | templates |

Smaller supporting pieces: `Strata/src/Strata/Project/ProjectModule.cpp` 10-24 (the smallest real module, for the
tutorial), `Strata/src/Strata/Renderer/GraphicsModule.cpp` 26-85 (a module that reports waits and start failures),
`StrataTests/src/Core/EngineModuleTests.cpp` 62-120 and 289-334 (a journaling test module that proves the hook order),
`Math/AABB.cpp` 7-25 (Arvo's transformed box), `Math/Ray.cpp` 7-16 (ray from NDC with reversed Z), `Math/Math.cpp` 9-54
(decomposition with reflection folded into X).

---

## 4. Figures

Diagrams:

1. **Executables and layer libraries** (dependency graph): editor, runtime, CLI, tests over `Strata_<Layer>` libraries;
   tooling layers off to the side; script modules linking only `StrataScriptCore`. Source: A 45-62 mermaid and the
   layer table A 576-596.
2. **The layer DAG** (Core, Input, App, Asset, Reflection, Scene, Renderer, Physics, Audio, Animation, World, GameUI,
   Scripting, Project, Runtime, Engine; tooling Network, ImGui, AssetPipeline), arrows = `MayInclude`; highlight the
   two proven downward dependencies (Audio and Project on App).
3. **Program start sequence** (sequence diagram): `main` -> `GetProgramRun` -> `ConnectStandardStreams` ->
   `InstallInterruptHandler` -> `CreateApplication` (log opens) -> `RegisterBuiltinModules` (open registries, nine
   module registrations, pipeline, Extra, freeze) -> `Application` constructor (throttling, jobs, window, Input,
   modules `OnInit`) -> layers pushed -> `Run`.
4. **One frame timeline** (horizontal timeline): main-thread queue, Input stage (`glfwPollEvents`, events into modules
   and layers, `InputActions::Update`), `OnBeginFrame` (GPU/swapchain wait shaded as "wait"), layers' `OnUpdate`,
   modules' `OnUpdate`, `OnRenderUI`, end of work time, `OnEndFrame` reverse (Present), pacer sleep; brace showing
   what `GetLastFrameWorkTime` counts.
5. **Module hook order** (swimlanes for modules A, B where B depends on A): Init A, Init B, Begin A, Begin B, Update,
   UI, End B, End A, Stop B, Stop A, Release, JobSystem shutdown, Shutdown. Matches the test at
   `StrataTests/src/Core/EngineModuleTests.cpp` 289-334.
6. **Kahn's algorithm worked example**: modules C(needs A), A, B(after C, optional), D(after Missing, optional) ->
   order A, C, B, D (the test's case).
7. **Event propagation**: window callback -> `Input::Process*` -> event -> application bookkeeping -> modules ->
   layers top-down (overlay first) -> stop on `Handled`; close veto branch.
8. **Fixed step on a time axis**: frames of varying length, accumulator filling, fixed steps falling out, max-steps
   cap dropping the backlog, interpolation alpha between the last two poses (one step behind).
9. **Job system**: three pools with their priority queues, who submits to which (frame work -> workers, reads -> I/O,
   imports/exports -> background), priorities of the threads, the four hardware threads left to the frame.
10. **JobState state machine**: Queued -> Claimed (by pool thread or by waiter) -> Completed; Dropped path for
    `ParallelFor` helpers.
11. **ParallelFor**: batches 0..N, atomic `NextBatch`, caller and helpers taking batches, helpers dropped, wait for
    `FinishedBatches`.
12. **Threads of the editor process and hand-offs** (A 1381-1445): main, workers, I/O, background, file watchers,
    audio mixer, RPC, log writer, process readers; arrows into the main thread's polled queues.
13. **BackgroundLogSink pipeline**: log call -> `LogBufferSink` (immediate) and queue -> writer thread -> console and
    file; flush barrier for warnings.
14. **FrameProfiler nesting and self time**: nested scopes on a time bar with the outer stage paused while inner runs;
    ring of 600 frames; GPU times attached frames later.
15. **Console vs Interactive decision table/flowchart** (Windows): passed streams? Console run? attach to parent
    console? show dialog?
16. **Atomic write** (temp file, flush, rename; crash at each point leaves old or new file) and the private-file TOCTOU
    picture (check and read through one handle).
17. **Reversed Z depth precision**: plot of depth vs distance for standard and reversed Z (float precision near 0).
18. **Frustum planes and the positive vertex test** (2D sketch), and **ray from NDC** through near plane and depth 0.5.
19. **Coordinate conventions**: right-handed axes, +Y up, -Z forward; NDC with +Y up and 0-1 depth; framebuffer origin
    top-left.

Screenshots (this area has no rendering feature; these show the instruments and behaviours):

1. Editor **Performance panel** with the stacked stage timeline (Input, Assets.*, Scene.*, Render.*, Editor.UI,
   Present) while a sample plays (e.g. Samples/PhysicsPlayground in play mode), and paused (the snapshot feature).
2. The status bar's **frame pill** and its tooltip (CPU/GPU/Capped bound).
3. **Tracy** capture of the editor built with `-DSTRATA_ENABLE_TRACY=ON`, showing `ST_PROFILE_STAGE` zones on the main
   thread and job zones on "Strata Worker n" threads.
4. The editor **Console panel** (backed by `LogBuffer`) showing core/App/Script loggers and levels.
5. A **terminal** running `StrataEditor --headless --frames 120` (Console run output with `[time] [level] logger:`)
   and the Ctrl+C message "Interrupted (Ctrl+C or a request to terminate): closing".
6. The **fatal-error dialog** ("cannot start: no usable graphics device was found") as an Interactive run shows it
   (can be produced with `STRATA_ERROR_DIALOG_FILE` for the text, or on a machine without Vulkan).
7. Optional: `editor.perf` JSON output via StrataCLI, next to the panel, to show the same numbers as a command.

---

## 5. Rules and pitfalls ("why" boxes)

1. **The main thread owns the scene, input, scripts and rendering submission; workers hand results back by queues or
   `SubmitToMainThread`.** Why: the scene and its caches are not thread-safe; a callback from a worker races the frame
   (AG Architecture rules, A 1434-1445).
2. **Never block a frame on a job that might run long, and never let a waiting thread run other jobs.** Why: a frame
   waiting for its own work could pick up an import's compression (A 1427-1433; `JobSystem.h` 99-100).
3. **Long work goes to `JobPriority::Background`; frame work stays on normal-priority workers.** Why: measured stalls
   of 5-30 ms when background work shared every processor with the frame's threads and the driver (A 1392-1404).
4. **What a job captures is released where it runs.** Why: libc++ copies small callables on move; the submitting
   thread could destroy the last reference to a scene on the main thread (`JobSystem.cpp` 335-342, DG 951-953).
5. **Application never names a module; modules are found with `GetModules().Find<T>()`, which may be null.** Why:
   headless, no-GPU and game programs run different module sets (A 715-750, DG 1044-1055).
6. **A module that fails `OnInit` cleans up what it started and describes the failure (`GetStartFailure`).** Why:
   the application unwinds only started modules and tells the person once the window is gone (`Application.cpp`
   140-158).
7. **`OnRelease` (assets, project) comes before `JobSystem::Shutdown`, `OnShutdown` (device) after.** Why: asset
   managers wait for load jobs, and assets own GPU resources (`Application.cpp` 162-177).
8. **Report waits in `EngineFrame::WaitSeconds`; time out-of-work waits as stages outside the work time.** Why: a
   frame's cost must not include vsync or the display's image, or a capped program looks CPU-bound (A 823-829).
9. **Registration only through the composition root, before anything reads a registry; nothing after the freeze.**
   Why: frozen registries take no locks and are safe from any thread; self-registration is dropped by linkers
   (A 619-714).
10. **`#if ST_WITH_<MODULE>` only in the composition root, the asset pipeline, the runtime and tests.** Why: other
    code reaches optional modules through services, so a build without them needs no guards (DG 262-270).
11. **Never widen `MayInclude` or add an allowlist line to make an upward or sideways include pass; invert the
    dependency.** Why: the layer table is the build; a game must never link tooling (DG 984-1009).
12. **Platform, window-system and graphics-API headers only in their `Platform/` folders; never `<Windows.h>` in a
    header; no X11 headers; no identifiers that collide with Windows macros; unscoped enums never use `None`.** Why:
    macro pollution and portability (AG Code style; `Event.h` 23).
13. **Engine code does not throw; third-party exceptions are caught at the call site; recoverable failures return
    errors and log; asserts only for programmer errors, verifies for checks that must stay.** Why: Dist compiles
    asserts out (with their side effects), and an escaped exception ends the loop (`Application.cpp` 243-253).
14. **Asserted conditions must have no side effects.** Why: they vanish in Dist (`Assert.h` 63).
15. **Strings are UTF-8; convert at `std::filesystem` boundaries with `FromUTF8`/`ToUTF8`.** Why: on Windows a path
    from a narrow string uses the ANSI code page and mangles non-ASCII names.
16. **Files only the current user may change go through the private-file functions; trusted files are checked and read
    through one handle.** Why: tokens and loaded code must not be planted or swapped (TOCTOU) (`Platform.h` 92-190).
17. **All writes are atomic (temp + rename).** Why: a crash or a concurrent reader never sees half a file
    (`FileSystem.h` 27-30).
18. **Do not log per frame; throttle repeating errors.** Why: floods hide the first message and cost time
    (`ErrorThrottle.h`); and warnings flush synchronously, so a warning per frame waits for the console every frame.
19. **Put `ST_PROFILE_STAGE` around a unit of frame work, not around calls that take nanoseconds.** Why: self-time
    accounting and the 64-stage limit (DG 928-934, `FrameProfiler.h` 169-172).
20. **Timesteps are clamped (0.25 s); fixed-step backlogs are dropped.** Why: a breakpoint or hitch would otherwise
    explode the simulation or start a spiral of death (`Application.h` 42, `Scene.cpp` 2296-2302).
21. **Read the fixed step through `Scene::GetFixedTimestep`/`GetMaxFixedSteps`, and count game time in fixed steps,
    never frames.** Why: the project's `Scene.Timing` wins over scene settings; frame rates differ per machine (AG
    Architecture rules, Editor).
22. **Windows sleeps are coarse; never call `timeBeginPeriod`.** Why: the default tick is 15.6 ms (a 120 Hz cap ran
    20% slow), and `timeBeginPeriod` changes the whole system (A 838-845).
23. **GUI-subsystem programs and PowerShell**: pipe their output or use `Start-Process -Wait` to get exit codes. Why:
    PowerShell does not wait for windowed programs (DG 334-337).
24. **A second Ctrl+C ends the process at once; the signal handler only counts.** Why: only async-signal-safe work is
    allowed in a handler; the first request must let layers shut down in order (A 176-181).
25. **One `Application` at a time; tests run several in sequence and must not create GPU devices themselves.** Why:
    `s_Instance` (`Application.cpp` 67) and shared device rules (AG Testing).
26. **Compose world matrices only through `Math::ComposeWorldTransform`.** Why: compilers fuse multiply-adds
    differently when inlined into different callers, and cached and recomputed transforms must agree bit for bit
    (`Math.h` 17-21).

---

## 6. Hands-on

For engine developers:

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Trace a frame: build Debug, set breakpoints in `Application::RunFrame` and each built-in module's hooks, write down the order, compare with A 805-822 | Easy | Reads the frame loop and hook contract |
| Write a `FrameCounterModule : EngineModule` (`c_Name`, `Factory`, `OnUpdate` counting frames, `OnStop` logging) in a test application, find it with `Find<T>()`; add a test in the style of `EngineModuleTests.cpp` | Medium | The module lifecycle, registry, testing with a journal |
| Make a module that depends on "Graphics" and one with `Required = false` on a missing module; observe ordering and the refusal message for a cycle | Easy | Dependencies, Kahn's sort, error reporting |
| Make a module return `EngineFrameAction::Skip` every 10th frame; confirm the frame count and profiler discard | Easy | Skip semantics, frame counting |
| Add a custom `ST_PROFILE_STAGE("Game.MyWork")` in a layer, run `editor.perf` or the Performance panel, nest a stage and verify self times | Easy | Frame profiler, self time |
| Build with `-DSTRATA_ENABLE_TRACY=ON`, capture with Tracy, compare `ST_PROFILE_SCOPE` zones with stage times | Medium | Instrumenting profilers |
| Parallelize a loop with `JobSystem::ParallelFor`, measure batch sizes 1/64/4096 with the profiler's worker busy percentage | Medium | Job granularity and overhead |
| Write a test that submits a job that waits on another job from inside a job, then explain why it cannot deadlock (read `TryRunJob`) | Medium | Claim-by-exchange |
| Reproduce the "captured last reference" rule: submit a job holding the last `Ref` of an object whose destructor records its thread id | Medium | Job lifetime rules |
| Implement a tiny lock-free hand-off with `SequenceLockedValue<T>` between a producer thread and the main loop | Hard | Memory ordering |
| Write the fixed-step accumulator yourself in a toy loop (variable frames, max steps, drop backlog, interpolation alpha), then compare with `Scene.cpp` 2239-2329 | Medium | Fixed timestep |
| Add a new `Platform::` function: declare in `Core/Platform.h`, implement in `WindowsPlatform.cpp` and `PosixPlatform.cpp`, test in `PlatformTests.cpp`; run `Architecture.Layering` | Medium | Platform seams and layer rules |
| Try including `<GLFW/glfw3.h>` from a Scene file and read the `Architecture.Layering` failure; then fix by inversion | Easy | Layer enforcement |
| Register a game component through `ModuleRegistrationOptions::Extra`, then try registering after the freeze and read the error | Easy | Composition root and freeze |
| Use `Exclude = {"Physics"}` in a test helper and observe unknown components and the scripts' message | Medium | Optional modules |
| Write a file atomically with `FileSystem::WriteText`, kill the process mid-write in a loop (or simulate), verify old-or-new | Medium | Atomic writes |
| Implement a frustum-culling test using `Frustum` and `AABB::Transformed` for a grid of boxes and a reversed-Z infinite projection | Medium | Math toolkit |
| Derive `PerspectiveReverseZInfinite` on paper and check it against `MathTests.cpp` 79-93 | Hard | Projection math |

For game developers (no engine change):

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Run `StrataRuntime --game <file> --headless --frames 300` and `--seconds 5`; explain why frames and seconds differ across machines | Easy | Frames vs game time |
| Change the project's `Scene.Timing` FixedRate (Project Settings) between 30 and 240 in Samples/PhysicsPlayground and observe contacts and interpolation | Easy | Fixed rate trade-offs |
| In a script, move an object in `OnUpdate` vs `OnFixedUpdate`, play at different frame caps, compare | Easy | Update vs fixed update |
| Use time scale 0 for a pause menu and drive a fade with unscaled time (scripts' unscaled delta) | Medium | Time scale |
| Read the Performance panel during play and identify whether the game is CPU-bound, GPU-bound or capped | Easy | Reading the profiler |
| Find the game's log file (user data dir `Logs/Game.log`) and read a warning a script produced | Easy | Logging for game makers |

---

## 7. Glossary

- **Application**: the object that owns the window, layers, modules and frame loop (`Core/Application.h`).
- **Composition root**: the one place that wires the program together by calling every module's registration
  (`Engine::RegisterBuiltinModules`).
- **Registry**: a table modules fill at startup (components, loaders, systems, settings); Strata's registries open,
  accept, then freeze.
- **Freeze**: closing a registry so it never changes again and can be read without locks.
- **Engine module (EngineModule)**: a service with a program-long lifecycle (graphics, audio, ImGui, project).
- **Engine module registration (Register<Module>Module)**: a module's static registration into registries; distinct
  from an EngineModule object (two meanings of "module" in Strata: the code folder/layer and the runtime service).
- **Hook**: a virtual function the application calls at a defined moment (`OnInit`, `OnBeginFrame`...).
- **Layer (application)**: a slice of program behaviour in the `LayerStack` (`Layer`); different from an
  **architecture layer** (a row of `Layers.json`, a static library).
- **Overlay**: a layer kept above ordinary layers; gets events first.
- **Layer table / `Layers.json`**: the list of architecture layers, their files and allowed includes.
- **Allowlist**: known exceptions to the layer rules; empty in Strata.
- **Tooling layer**: a layer games never link (AssetPipeline, Network, ImGui).
- **Dependency inversion**: making high-level code provide an implementation of an interface defined lower down.
- **Service / engine service**: an interface a module provides process-wide (`EngineServices::Get<T>`).
- **Service locator**: a global lookup of service implementations by type.
- **Topological sort**: ordering a graph's nodes so every node comes after what it depends on.
- **Kahn's algorithm**: topological sort by repeatedly taking nodes with no unmet dependencies.
- **Frame**: one iteration of the main loop.
- **Frame loop / game loop**: the loop that runs frames until the program closes.
- **Timestep / delta time**: the time a frame or step advances the game.
- **Fixed timestep**: a constant simulation step independent of frame rate.
- **Accumulator**: the time owed to fixed steps, filled by frames, emptied by steps.
- **Spiral of death**: when catching up costs more time than it simulates, so the backlog grows.
- **Time dilation**: Strata's choice to slow the simulation instead of catching up indefinitely.
- **Interpolation (render)**: drawing between the last two simulation poses for smooth motion.
- **Time scale**: a multiplier on game time (slow motion, pause at 0); **unscaled time** ignores it.
- **Frame pacing / frame-rate cap**: limiting how often frames start (`FramePacer`).
- **Vsync / FIFO present mode**: presenting in step with the display's refresh.
- **Swapchain**: the ring of images a GPU renders into and a display shows.
- **Present**: handing a finished image to the display.
- **Work time**: Strata's CPU cost of a frame without waits (`GetLastFrameWorkTime`).
- **Headless**: running without a window (and possibly without GPU).
- **Event**: an object describing something that happened (key press, resize) delivered synchronously.
- **Dispatcher**: code that calls the handler matching an event's type.
- **Handled flag**: marks an event consumed so it propagates no further.
- **Polling input**: reading current input state each frame instead of reacting to events.
- **Main thread**: the thread that runs the frame loop and owns the scene.
- **Main-thread queue**: functions queued by any thread to run at the next frame start.
- **Thread pool**: a fixed set of threads running queued jobs.
- **Job**: a unit of work submitted to a pool; **job handle**: the way to wait for it.
- **Worker / I/O / background thread**: Strata's three pools (frame CPU work, blocking reads, long low-priority work).
- **ParallelFor**: splitting an index range into batches run in parallel.
- **Batch**: a contiguous slice of a `ParallelFor` range.
- **Claim**: atomically taking a job so exactly one thread runs it.
- **Deadlock**: threads waiting for each other forever.
- **Data race**: unsynchronized concurrent access where one side writes.
- **Mutex / condition variable**: lock / wait-until-signalled primitives.
- **Atomic, memory order, fence**: indivisible operations and ordering guarantees between threads.
- **Sequence lock**: a lock-free scheme where readers retry if a writer was active (odd sequence).
- **Thread-local**: a variable with one instance per thread (`t_` prefix).
- **Thread priority / scheduling quantum**: OS ranking of threads / the slice of time a thread runs before switching.
- **Power throttling (EcoQoS)**: Windows 11 slowing background processes.
- **Profiler (instrumenting vs sampling)**: tool measuring where time goes by markers vs periodic stack samples.
- **Tracy**: an open-source instrumenting frame profiler.
- **Frame stage**: a named, timed part of the main thread's frame (`ST_PROFILE_STAGE`).
- **Self time vs inclusive time**: time in a scope excluding vs including nested scopes.
- **Percentile (P50, P95), nearest rank**: the sample below which that share of samples lie.
- **CPU-bound / GPU-bound / capped**: what limits the frame rate.
- **GPU timestamp**: a time the GPU writes into a query, read frames later.
- **Assert / verify**: debug-only / always-on checks of programmer assumptions.
- **Dist**: Strata's shipping configuration (asserts compiled out).
- **Logger, sink, level**: named log source, output destination, severity.
- **Ring buffer**: fixed-capacity buffer that overwrites the oldest entries.
- **Asynchronous logging**: writing log output on a separate thread.
- **RAII**: tying resource release to object destruction.
- **`Scope` / `Ref` / `WeakRef`**: Strata's names for unique, shared and weak ownership pointers.
- **Precompiled header (`stpch.h`)**: a header compiled once and reused to speed builds.
- **Platform layer / seam**: the boundary behind which OS-specific code lives.
- **GLFW**: a C library for windows, input and Vulkan surfaces.
- **Window backend**: the implementation of `Window` (GLFW or NoWindow).
- **Console vs GUI subsystem**: Windows' two kinds of executables (with or without a console window).
- **Console run / Interactive run**: Strata's `ProgramRun` kinds.
- **Signal (SIGINT, SIGTERM) / console control handler**: OS mechanisms to ask a process to stop.
- **Async-signal-safe**: operations allowed inside a signal handler.
- **Exit code**: the integer a process returns (Strata: 0, 1, 3, 130).
- **UTF-8 / UTF-16 / code page**: Unicode encodings / Windows' legacy narrow encoding.
- **Atomic write**: writing to a temporary file and renaming it over the target.
- **TOCTOU**: time-of-check to time-of-use race.
- **DACL / file mode 0700**: Windows access control list / POSIX owner-only permissions.
- **Reparse point / junction / symbolic link**: file-system redirections.
- **Right-handed coordinates, +Y up, -Z forward**: Strata's world axes (glTF).
- **NDC**: normalized device coordinates after projection and divide.
- **Reversed Z**: mapping near to depth 1 and far to 0 for float precision.
- **Infinite far plane**: a projection without a far clip.
- **Frustum / frustum culling**: the visible volume / skipping objects outside it.
- **AABB**: axis-aligned bounding box.
- **Quaternion**: a 4-number rotation representation; q and -q are the same rotation.
- **Euler angles**: rotations as pitch/yaw/roll.
- **TRS**: translation-rotation-scale transform.
- **FMA (fused multiply-add)**: one-rounding multiply-add that can change floating results.
- **UUID**: Strata's 64-bit random identifier (zero is null).
- **FNV-1a / CRC-32C / SHA-256 / HMAC**: stable hash / corruption checksum / cryptographic hash / keyed authentication.
- **Radix sort**: sorting by digits (bytes) rather than comparisons.
- **Offset (range) allocator**: hands out ranges of a buffer without owning memory.

---

## 8. Proposed chapters (teaching order)

1. **What an engine is, and how Strata is put together** (concept, both, M, 1 screenshot): the problem an engine
   solves, the executables, the layer stack, where game code lives. Prerequisites: none.
2. **From `main` to the first frame** (internals, engine, M): entry point, `ProgramRun`, interrupt handler, the
   composition root, `Application` startup and its failure paths. Prerequisites: ch. 1, C++ basics.
3. **The frame loop** (concept + internals, both, L, 1 screenshot): why loops, stages, the hook table, frame skipping,
   work time, vsync and frame pacing, the main-thread queue, shutdown. Prerequisites: ch. 2.
4. **Time: delta time, the fixed step and interpolation** (concept, both, M): clocks, clamping, accumulator, max steps,
   time dilation, time scale, pausing and stepping, `Scene.Timing`. Prerequisites: ch. 3 (scene systems from the
   Scene area for the callbacks).
5. **Windows, events and layers** (internals, engine, M): `Window` interface, GLFW callbacks, events and dispatch,
   polled input, layers and overlays, the close veto, NoWindow and stub windows. Prerequisites: ch. 3.
6. **Engine modules** (internals + tutorial, engine, M): the lifecycle, dependencies and Kahn's sort, failures, the four
   built-in modules (where the GPU device is made), engine services; tutorial: write a module. Prerequisites: ch. 3, 5.
7. **Layers, registries and the composition root** (internals, engine, L): layered architecture, dependency inversion,
   `Layers.json` as the build, enforcement tests, registries and freezing, optional modules, tooling-free games.
   Prerequisites: ch. 2, 6.
8. **C++ for engine code: ownership, errors and logging** (concept + reference, engine, M, 1 screenshot): RAII,
   `Scope`/`Ref`, asserts vs verifies vs results, exceptions policy, logging and the background writer, code style.
   Prerequisites: ch. 1 (can be read early, alongside ch. 2).
9. **Threads and the job system** (concept + internals, engine, XL): threads and synchronization from zero, thread
   pools, Strata's three pools and priorities, claim-and-run waiting, `ParallelFor`, lifetime of captures, sequence
   locks, the threading model and hand-offs. Prerequisites: ch. 3, 8.
10. **Measuring the frame: the frame profiler and Tracy** (internals + tutorial, both, M, 3 screenshots): stages, self
    time, percentiles, job busy time, GPU stages, bound classification, Tracy builds. Prerequisites: ch. 3, 9.
11. **Talking to the operating system** (internals, engine, L, 2 screenshots): platform seams, `Platform` services,
    console vs GUI programs, signals, dialogs, UTF-8 paths, atomic writes, private files, file reader/lock/watcher,
    processes and libraries (pointers to the scripting area). Prerequisites: ch. 2, 8.
12. **The math toolkit** (concept, both, L): conventions, transforms, quaternions, projections and reversed Z, frustum,
    AABB, rays, random numbers. Prerequisites: high-school algebra (the book teaches vectors and matrices here or in a
    shared math chapter).
13. **Core utilities reference** (reference, engine, M): UUID, hashes and CRC, crypto, Base64, binary streams, JSON
    helpers, string helpers, radix sort, range allocator, amortized checks, command line. Prerequisites: ch. 8.

---

## 9. Not determined

- `Core/BackgroundLogSink.cpp`, `Core/FrameProfiler.cpp` beyond the stage and frame functions (summaries, GPU
  listener delivery, snapshots), `Core/SettingsRegistry.cpp`, `Core/ProjectSettings.cpp`, `Core/FileWatcher.cpp`,
  `Core/RangeAllocator.cpp`, `Core/RadixSort.cpp`, `Core/Crypto.cpp`, `Core/Hash.cpp`, `Core/SaveFiles.cpp`, and the
  Platform files `*CrashGuard.cpp`, `*Process.cpp`, `*Socket.cpp`, `*Symbolizer.cpp`, `*DynamicLibrary.cpp`,
  `*FileReader.cpp`, `*FileLock.cpp`, `WindowsFileSecurity.cpp`, `GLFWApplicationIcon.cpp`, most of `GLFWWindow.cpp`
  (modes, gamepads, clipboard, layout keys) and `VulkanGraphicsDevice.cpp` past device creation were only skimmed
  through their headers or function lists, not read line by line.
- The tests were read by their case names (and EngineModuleTests in part), not in full.
- Release attribution is partial: the documents do not say when Application, layers, events, logging, asserts, the
  job system's first version, `FileSystem`, the Math module or most Platform services arrived (before wave 1 or in
  0.1/0.2; there are no release notes before 0.3.0).
- Possible defect, not verified: `Core/Log.cpp` passes `specification.LogFile.string()` to spdlog's file sink, and no
  `SPDLOG_WCHAR_FILENAMES` is defined in the build; on Windows that narrow conversion uses the ANSI code page, so a log
  path with characters outside it (a user profile name) may fail or be misnamed, contrary to the UTF-8 path rule.
- Documentation drift seen in passing: the comment of `Engine/BuiltinModules.h` 26-27 lists the modules as "Scene,
  Renderer, Physics, Audio, Animation, Scripting" and 21-22 says "Scene and Renderer are part of every engine", while
  the table also has Input, World and GameUI and refuses excluding Input too (`BuiltinModules.cpp` 80); the roadmap's
  "eleven built-in stages" (RM 106) is now twelve (`Present` included). Not checked whether A lists every stage the
  code registers (Scene.UI, Render.UI, Scene.Animation, World.Streaming, Editor.Commands come from other modules).
- `UUID.cpp` names its thread-local engine `s_Engine` where the style asks for `t_` (minor; not checked elsewhere).
- Whether the editor's idle throttling preferences (`Editor.FrameRate`) and `GameRuntime::GetFrameRateCap` belong to
  this area or to the editor/runtime areas is a planner decision; only their use of `SetMaxFrameRate` was read.
- The Hazel lineage of `Layer`/`LayerStack`/`Event`/`ST_BIND_EVENT_FN` is an observation from the "Hazel conventions"
  naming in AGENTS.md and the code's shape; no document of the repository states where the design came from.
