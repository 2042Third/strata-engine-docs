# Allocation: scripting

## `scripting/why-scripts` — Why game code lives outside the engine

**Covers.** The page opens on what the reader did in `start/first-game`: the `Spinner` script was changed, built with
**Ctrl+B** and run again while the editor kept running, and the engine was never rebuilt. From it the problem: an
engine is large and general, a game's rules change by the hour, and a bug in game code should not take the editor
down. The naive answer, game code compiled into the engine, and where it breaks (a rebuild and a restart for every
change; every game links the engine's internals). The idea in one paragraph and one diagram, the layers of the part:
game code, the SDK, the module's entry points, the C line, then `ScriptModule`, `ScriptEngine`, `ScriptSystem` and the
host API with the scene and engine services below, each box named with the page that opens it. The approaches engines
use, each brought in by the flaw of the one before: an embedded interpreted language (Lua), a managed runtime (C# in
Unity and Godot), a language of the engine's own (GDScript; UnrealScript in its time), visual scripting (Blueprints),
and native code in plug-in libraries (Unreal's C++ modules with Live Coding, the DLL reload of in-house engines), with
a table of speed, time to see a change, safety, tools and who uses them. Where game code attaches to objects: script
components (Unity's MonoBehaviour), scripts as systems in a pure ECS, actor subclasses (Unreal), and Strata's Script
component, an ordered list of class names whose instances live outside the registry. Strata's choice in a `:::why`
aside: native C++20 in a shared library behind a C ABI, so one language for engine and game, full speed, and the
debuggers and IDEs people already use; and its three costs, which the rest of the part pays: crashes (containment),
the binary boundary (the ABI and the SDK), compile time (hot reload). What Strata does not do: visual scripting, and
any script language but C++. Common mistakes: reading "script" as "interpreted", and underestimating what a native
choice costs. At the end the reader can say why an engine loads game code as a module, compare the five approaches
by cost, and name the page of the part that answers each cost.

**Leaves out.**

- What a shared library and a binary interface are → `scripting/shared-libraries`
- Writing, building and attaching a script → `make/first-script`
- The script lifecycle and its callbacks → `make/script-loop`, `scripting/script-system`
- How a crash in game code is contained → `scripting/crash-containment`
- How a module is replaced while the game runs → `scripting/hot-reload`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,700 words against M (3,000). The five approaches with their table and the four object models
take the most words, with the exercises about 250; the ABI stays with `scripting/shared-libraries`.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:243` | concept | home | Why games need scripts: engine code against game code, the five approaches with their costs, Strata's native choice and what it costs; the mistake "script means interpreted" |
| `scripting:285` | concept | home | Where scripts attach: script components, scripts as systems, actor subclasses; Strata's ordered entry list per entity, one instance per entry, instances outside the registry |
| `scripting:398` | figure | home | The layers of the part (a redraw of `Docs/Architecture.md:3138-3146`), calls in each direction, each box naming its page |
| `new:1` | not-done | home | Visual scripting: game logic is C++ script classes. Evidence: `git grep -niE "visual ?script" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore` and `git grep -niw "blueprints\?" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore` find nothing (run at the pin); `AGENTS.md:269-271` |
| `new:2` | not-done | home | Script languages other than C++. Evidence: `git grep -niE "lua_" 822a7a46 -- Strata/src StrataEditor/src StrataScriptCore StrataRuntime`, the same with `mono_` and with `coreclr`, find nothing (run at the pin); `Strata/vendor` holds no interpreter or runtime |
| `new:20` | hands-on | home | The page's exercises (R32, D27): a design exercise, three games (rules that change every day, a game that players extend, a console game that may load no code at run time) each matched to an approach of the page's table with the cost that decides it; and one done on the workbench: change the `Spinner` of `start/first-game`, build with **Ctrl+B**, and note which file the build wrote (the module, in the project's build folder) and how long the change took to show, against a build of the engine from `core/first-change` (about 250 words). Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:241-254` (the `Spinner`); `StrataEditor/src/EditorLayer.cpp:983`, `:1591` (Ctrl+B builds the scripts); `StrataScriptCore/CMake/StrataScriptModule.cmake:106-107` (the module's output folder); `Docs/Roadmap.md:1709` (a console port would link modules statically) |
| `scripting:154` | feature | use | The Script component, named as the place scripts attach |
| `scripting:201` | feature | link | The layer rule of Scripting, named once as the reason for the host API |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a game engine is; the frame map | `start/what-an-engine-is` | must |
| Writing and building a script in the editor (the `Spinner` of the first game) | `start/first-game` | must |
| Object models: inheritance, components, ECS | `world/what-a-world-is` | must |
| Handles instead of pointers; UUIDs as stable identities | `world/ecs` | helps |
| How a C++ program is built: compiling, linking, static and shared libraries | `basics/build` | must |
| C++ classes in depth: inheritance and virtual calls | `basics/cpp-classes` | helps |
| "Module", "layer", "registry" and "service" | `core/map` | helps |
| The layer table, optional modules, no tooling in games | `core/layers-registries` | helps |

## `scripting/shared-libraries` — Shared libraries and binary interfaces

**Covers.** The problem as the reader meets it: the `Spinner`'s module is a file in the project's build folder that the
editor loads while it runs; what is that file, and how do two programs built at different times by different
compilers call each other? The naive answer, passing C++ classes across, and where it breaks. Then, from zero and in
this order: what a shared library is (DLL, `.so`, `.dylib`), exported symbols, loading a library and looking up a
function (`LoadLibrary` and `dlopen`, `GetProcAddress` and `dlsym`), static initializers that run when it loads,
reference counts (loading a file that is loaded already returns the same library and shares its state), where a
library's own dependencies are searched (the Windows search order, RUNPATH and `$ORIGIN`), symbol visibility and
interposition. API against ABI: calling conventions, struct layout and padding, name mangling, the exception model,
allocators and the C runtime, the standard library's layouts, Debug against Release (`_ITERATOR_DEBUG_LEVEL`), so C++
has no stable ABI and engines expose C. The approaches to a binary interface, with a table of their costs: COM-style
interfaces with vtables, C function tables (also Vulkan's dispatch tables), flat C exports, bindings generated from an
interface language. Versioning a binary interface: forward and backward compatibility, append-only structs, size
prefixes (Win32's `cbSize`), feature detection against version numbers, frozen structs for arrays one side fills, with
the figure of an old engine meeting a new module and the reverse. Strata's choice: two exported functions,
function-pointer tables, plain data only (strings as a pointer and a size in UTF-8, ids as 64-bit numbers,
quaternions as x, y, z, w), one version number for incompatible changes; and how a module is built, walked in the
CMake excerpt: `StrataScriptCore` as a header-only target, `strata_add_script_module` with a MODULE library, hidden
visibility, the static C runtime, a PDB in every configuration, `-fno-gnu-unique` so that `dlclose` really unloads,
and `--no-undefined`. What the choice cannot do: share C++ types, or call into the module from another thread. Common
mistakes: a `std::string` or a glm type passed across, memory freed on the other side, an exception that crosses,
`bool` and enum sizes assumed, unloading that does not unload, dependencies found through PATH or the current folder,
static constructors forgotten as code that can crash. At the end the reader can say what may cross a binary boundary
and why, and design a struct that a newer and an older program can both read.

**Leaves out.**

- The tour of Strata's ABI header and the SDK → `scripting/abi-sdk`
- How the engine loads, validates and calls a module, and its private copies → `scripting/loading`
- The editor's builds: finding compilers, running CMake, diagnostics → `editor/script-builds`
- Building a module outside the editor, other compilers and long paths → `make/script-builds`
- The CMake of the engine's own libraries → `engineering/cmake`

**Fit.** `fits`: about 4,900 words against L (5,000). Three concepts taught from zero for a reader who has met libraries
only in `basics/build` take the most words, with the approaches table, the versioning figure, one CMake excerpt and the
exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:252` | concept | home | Shared libraries and dynamic loading: exports, loading and lookup, static initializers at load, reference counts, search paths, visibility and interposition; the mistakes |
| `scripting:258` | concept | home | ABI against API, why C, the approaches to a binary interface and Strata's choice; the mistakes of passing C++ types, freeing across, exceptions, enum sizes |
| `scripting:265` | concept | home | Versioning a binary interface: append-only, size prefixes, feature detection, frozen structs; Strata's one version number for incompatible changes (modules of 0.6.0 load on 0.7.0, `Docs/Releases/0.7.0.md:125-127`) |
| `scripting:406` | figure | home | Struct versioning: two bars for an old engine and a new module and the reverse, `StructSize` on entry and on return, the overlap both read; the same for the struct the engine fills |
| `scripting:143` | feature | home | `StrataScriptCore`, the header-only target with glm and C++20 that a module links |
| `scripting:144` | feature | home | `strata_add_script_module` and what each of its settings is for |
| `scripting:384` | code | home | `StrataScriptCore/CMake/StrataScriptModule.cmake:85-133`: what building a module means (the SDK's entry file, MODULE library, hidden visibility, static C runtime, PDB in every configuration, `-fno-gnu-unique`, `--no-undefined`) |
| `scripting:557` | term | home | ABI (application binary interface) |
| `scripting:560` | term | home | Append-only |
| `scripting:574` | term | home | CRT (C runtime) |
| `scripting:581` | term | home | Entry point |
| `scripting:595` | term | home | Interposition |
| `scripting:596` | term | home | Module (script module), the qualified meaning of "module" |
| `scripting:605` | term | home | RUNPATH and `$ORIGIN` |
| `new:21` | hands-on | home | The page's exercises (R32, D27): one done in a terminal, the exported symbols of the `Spinner`'s module listed (`dumpbin /exports` on Windows, `nm -D --defined-only` on Linux) and the two `StrataScript_` functions of the SDK's entry file found among them, with why hidden visibility keeps the script classes out of the list; and a design exercise, a member appended to a struct with a size prefix, and what an older engine and an older module each read of it (about 250 words). Evidence: `StrataScriptCore/Source/ScriptModuleEntry.cpp:73-81`; `StrataScriptCore/Include/StrataScript/ScriptABI.h:36`, `:38` (`ST_SCRIPT_EXPORT`); `StrataScriptCore/CMake/StrataScriptModule.cmake:101-102` (hidden visibility) |
| `scripting:187` | feature | use | `DynamicLibrary`'s search rules, as Strata's answer to search paths (its home is `scripting/loading`) |
| `scripting:448` | rule | link | "Only plain C data crosses the ABI", named as the rule the page's reasons lead to |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Why game code lives outside the engine | `scripting/why-scripts` | must |
| How a C++ program is built: compiling, linking, static and shared libraries, CMake | `basics/build` | must |
| How a computer runs a program: memory, the stack and the heap, processes | `basics/computer` | must |
| Inheritance, virtual calls and interfaces | `basics/cpp-classes` | must |
| Pointers, references, lifetimes, RAII and smart pointers | `basics/cpp-memory` | must |
| Templates and the standard containers | `basics/cpp-generic` | helps |
| Bytes, text encodings and UTF-8 | `basics/bytes` | helps |
| Integers of fixed sizes and binary | `basics/numbers` | helps |
| The terminal, paths and environment variables | `basics/tools` | helps |
| C++ exceptions and the engine's error policy | `core/conventions` | helps |

## `scripting/abi-sdk` — Inside the ABI and the SDK

**Covers.** The job: the two sides of the boundary, the C header `ScriptABI.h` that both sides compile and the
header-only C++ SDK that game code is written against; what they are responsible for and what loading and the host API
do instead. The problem in one paragraph that links `scripting/shared-libraries`. The map: the SDK's files
(`ScriptABI.h`, `Host.h`, `Script.h`, `Value.h`, the umbrella `StrataScript.h`, the entry file) and which side owns
what. The toy: a two-function host table and a one-class descriptor in about 60 lines of C and C++. Then the real code
in the order data crosses the boundary. First the C side: the contract comment; the two exports and their macros; opaque
handles and ids; strings, results and the tagged-union value; transforms; a frozen struct (`StrataScriptRaycastHit`, 40
bytes, layout asserts) against an extensible one (`StrataScriptCollision`, with `StructSize`) and the struct the engine
fills up to the module's capacity (`StrataScriptGraphicsOptionInfo`); `ST_SCRIPT_HAS_MEMBER` and the head of the host
table, with the buffer protocol for text and arrays; the field, class and module descriptors, the class descriptor's 15
callback slots null when not implemented. Then the SDK, which turns that C into classes: `Host.h`'s current context as a
scope, the buffer-retry reads, and `ST_SCRIPT_DETAIL_HOST_WITH` for functions an older engine lacks; the `Script` base
class and how it binds its entity in its constructor; `InvokeScript`, the exception firewall, and one thunk per
callback; override detection at compile time with `requires` and member-pointer types, so the engine never calls a
callback a class does not implement; static self-registration through `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD`
(`__COUNTER__`, an intrusive list built during static initialization without allocation, `ScriptClassBuilder::Field`
with its static asserts, the ten field types and their value traits); `BuildClassRecord`, which reads defaults from one
default-constructed instance (why a constructor must do nothing); `LoadModule` and `WriteModuleAPI`, which check the
versions and the baseline member `GetScrollDelta` and write at most the engine's capacity. Last, the helpers that run
entirely in the module (`Random`, `Timer`, `KeyRepeat`, `Motion`) and why they never meet engine classes of the same
name (the one-definition rule). The example is the ThirdPerson sample's `Coin`: its `ST_SCRIPT_CLASS` block followed to
the descriptor the engine reads. What Strata does not do: calls into scripts from other threads. Tests: `Scripting.API`,
the `NewerSDK` module, and `Architecture.ScriptSDK`, which keeps the SDK's classes away from the engine's classes of the
same name: it scans the sources of the engine, the editor, the runtime, the CLI and the tests, and fails on any include
of a `StrataScript/` header other than `ScriptABI.h` outside a raw string. At the end the reader can read any struct of
the ABI, say which side may read which member, and trace a class from its macro to its descriptor.

**Leaves out.**

- Why C, and how binary interfaces are versioned → `scripting/shared-libraries`
- Loading the module and validating its description → `scripting/loading`
- How host functions are implemented and listed → `scripting/host-api`
- Abort containment in the SDK's entry file → `scripting/crash-containment`
- Every SDK class and function with the host function it wraps → `reference/script-api`
- Writing a script class, `override` and fields as a game maker does → `make/first-script`
- The PCG32 algorithm of `Random` → `basics/math-probability`

**Fit.** `over`: about 6,600 words against L (5,000). Twelve excerpts with what to look for, the C++ they use (member
pointers, `requires`, token pasting), seven rules and three exercises take the most words; by S2 the next size, XL
(8,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:38-51` | feature | home | The C side in order: the two entry points, the ABI version, the export macros, layout asserts, size-prefixed extensibility, opaque handles, strings, results, the tagged-union value, transforms, frozen structs, the engine-filled and the module-filled extensible structs, the API's enums |
| `scripting:53-57` | feature | home | The host table as a struct (its `StructSize`, `ABIVersion`, 165 function pointers), the buffer protocol, the field, class and module descriptors |
| `scripting:102-117` | feature | home | The SDK: umbrella header, plumbing, graceful degradation, the `Script` base class, the exception firewall, thunks, override detection, static self-registration, class records, the version-safe module write, `LoadModule`, `ScriptClassBuilder`, the macros, the ten field types, value traits, `AssetHandle` |
| `scripting:137` | feature | home | The module entry source: the two exports every module gets (its abort containment is `scripting/crash-containment`'s) |
| `scripting:278` | concept | home | A C++ SDK over a C ABI: thunks, static self-registration, member-pointer fields, compile-time override detection, `__COUNTER__`, the buffer-retry protocol; the mistakes (registration in a header, side effects in constructors) |
| `scripting:343` | concept | link | The determinism helpers named where the page says why they live in the module (`scripting:490`); the concept's home is `make/recipes` |
| `scripting:354` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:3-27`: the whole contract in one comment |
| `scripting:355` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:304-320`: the head of the host table with the buffer protocol's comment; with lines 67-69, `ST_SCRIPT_HAS_MEMBER` |
| `scripting:356` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:111-140`: the tagged union, the one value type that crosses |
| `scripting:357` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:159-192`: a frozen struct with layout asserts against an extensible one, and the comments that say why |
| `scripting:358` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:758-851`: the field, class and module descriptors |
| `scripting:360` | code | home | `StrataScriptCore/Include/StrataScript/Host.h:36-55`: the current context as a scope; with lines 69-85 (the buffer-retry read) and 106-111 (`ST_SCRIPT_DETAIL_HOST_WITH`) |
| `scripting:361` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:70-108`: the `Script` base class, binding its entity and context in its constructor |
| `scripting:362` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:184-203`: `InvokeScript`, the exception firewall; with lines 246-250, one thunk |
| `scripting:363` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:371-378`: override detection with `requires` and a member-pointer type; with lines 506-541, `GetCallbackFlags` |
| `scripting:364` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:543-617`: static self-registration into an intrusive list; with lines 852-865, the macros |
| `scripting:365` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:638-690`: `BuildClassRecord`, defaults from a default-constructed instance, null slots for callbacks not implemented |
| `scripting:366` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:692-762`: `WriteModuleAPI` and `LoadModule`, the version checks and writing at most the receiver's capacity |
| `gamedev:362` | code | home | `StrataScriptCore/Include/StrataScript/Script.h:348-376`: the callback flags and the first override check, and with lines 842-865 the macros; the page shows these lines once, inside the excerpts of `scripting:363` and `scripting:364` |
| `scripting:448` | rule | home | Only plain C data crosses the ABI, with its reason |
| `scripting:450` | rule | home | Append, never insert, reorder or remove; appending keeps the ABI version |
| `scripting:452` | rule | home | Check `ST_SCRIPT_HAS_MEMBER` before using a function appended after the initial set |
| `scripting:454` | rule | home | Frozen structs stay frozen, because the engine writes arrays of them into the module's buffers |
| `scripting:467` | rule | home | Classes are default-constructible and constructors do nothing: the mechanism (one instance at load reads the defaults); the game maker's rule is `make/first-script`'s |
| `scripting:470` | rule | home | One `ST_SCRIPT_CLASS` per class, in a `.cpp`: each translation unit would register it again, and the engine refuses the duplicate |
| `scripting:490` | rule | home | SDK helpers named like engine classes are tested only inside a module; no engine source includes the SDK's C++ headers (`Architecture.ScriptSDK`) |
| `build-test:184` | feature | home | `Architecture.ScriptSDK`, the test of `scripting:490`: it reads every `.h`, `.cpp` and `.mm` of `Strata/src`, `StrataEditor/src`, `StrataRuntime/src`, `StrataCLI/src` and `StrataTests/src` and lists each include of a `StrataScript/` header other than `ScriptABI.h`, lines inside raw strings skipped (`StrataTests/src/Architecture/ScriptSDKTests.cpp:87-160`) |
| `audio-input:541` | rule | home | The same rule as the input area states it (`KeyRepeat`, `Random`, `Timer`); one rule box with `scripting:490` |
| `animation:483` | rule | home | New host functions are appended, never inserted, with the animators' twelve functions as the example; one rule box with `scripting:450` |
| `audio-input:693` | term | home | Text buffer protocol; one glossary entry with `scripting:567` |
| `scripting:540` | hands-on | home | Exercise: what happens when a module's `StrataScriptModuleAPI` is larger or smaller than the engine's (as the `NewerSDK` test module does) |
| `gamedev:557` | hands-on | home | Exercise: add an SDK helper to `Gameplay.h` (a `Cooldown` class), used and tested only inside a script module |
| `new:22` | hands-on | home | The "trace it yourself" exercise (R32, D27): `ST_SCRIPT_CLASS(Coin)` followed with a search from the macro to its static `ClassRegistrar`, then with a breakpoint in `BuildClassRecord` while the engine loads a ThirdPerson copy's module, to the class descriptor that `WriteModuleAPI` hands over and `ScriptModule::ReadModuleDescription` reads (about 250 words). Evidence: `Samples/ThirdPerson/Scripts/Coin.cpp:54`; `StrataScriptCore/Include/StrataScript/Script.h:589-617`, `:640`, `:702`, `:852`, `:864`; `Strata/src/Strata/Scripting/ScriptModule.cpp:942` |
| `scripting:559` | term | home | ABI version |
| `scripting:567` | term | home | Buffer protocol |
| `scripting:571` | term | home | Class descriptor |
| `scripting:572` | term | home | Context, the opaque per-scene handle |
| `scripting:588` | term | home | Frozen struct |
| `scripting:589` | term | home | Host |
| `scripting:597` | term | home | Module description |
| `scripting:598` | term | home | ODR (one-definition rule) |
| `scripting:607` | term | home | SDK |
| `scripting:612` | term | home | `StructSize` |
| `scripting:616` | term | home | Thunk |
| `new:3` | not-done | home | Calls into scripts from other threads: the engine calls the module on its main thread only, and the module calls the host only from within those calls. Evidence: `StrataScriptCore/Include/StrataScript/ScriptABI.h:25-26` |
| `scripting:92` | feature | use | The 15 callback slots of the class descriptor (their order and dispatch are `scripting/script-system`'s) |
| `scripting:359` | code | use | `StrataScriptCore/Source/ScriptModuleEntry.cpp:73-81`, the two exports; the rest of the file is `scripting/crash-containment`'s |
| `scripting:385` | code | use | The `Coin` script's registration block as the example (its home is `make/recipes`) |
| `scripting:133-136` | feature | link | `Random`, `Timer`, `KeyRepeat` and `Motion` named as the helpers that live in the module; their homes are `make/recipes` (`Random`), `make/timers-events` (`Timer`, `KeyRepeat`) and `make/gameplay-math` (`Motion`), and `reference/script-api` lists their facts |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shared libraries and binary interfaces: exports, static initializers at load, ABI against API, size prefixes | `scripting/shared-libraries` | must |
| Templates, lambdas and pointers to members | `basics/cpp-generic` | must |
| `constexpr`, `if constexpr`, concepts and `requires`, macros, `std::string_view` | `basics/cpp-modern` | must |
| Inheritance and virtual calls | `basics/cpp-classes` | must |
| Reflection: one registration, many uses | `world/reflection` | must |
| C++ exceptions and the engine's error policy | `core/conventions` | must |
| Bytes, text encodings and UTF-8 | `basics/bytes` | helps |
| The script lifecycle and its callbacks | `scripting/script-system` | helps |
| What is special to script code (the `Script` base class, `override`, the macros) | `start/first-game` | helps |

## `scripting/loading` — Loading, calling and validating modules

**Covers.** The job: `ScriptModule` loads one module file, checks it, reads its description once and makes every later
call through a guard; `ScriptEngine` owns the module and the faults, and names the active engine that scenes take when
they start. The problem in one paragraph that links `scripting/shared-libraries`. The map: who owns what in memory
(figure): the engine's records (`ScriptClassInfo`, the copied class functions, the instances' bookkeeping) against the
module's objects (script instances, class records, descriptors), the instance handle that points across, and which side
frees what. The toy: load a library, look up two functions, call them, about 40 lines. Then a load in the order it
happens (sequence figure), walked in `ScriptModule::Load`: the file check; in place or from a private copy (the two load
modes; a file that is loaded already or abandoned always loads from a copy; the per-process copy directory under the
user runtime directory, held by a `FileLock`, and the stale directories of dead processes removed); `DynamicLibrary`, a
Core class that owns one loaded library (move-only; on Windows dependencies are searched beside the file and the
original, never in the current folder or PATH; on Linux and macOS through the module's RUNPATH, where `$ORIGIN` is the
copy's folder, the loader's environment variables and the system paths; a file cut short refused before the loader reads
past its end, a file loaded twice sharing one handle, and `Release`, which forgets a library whose unload crashed and
leaves it loaded); loading under `CrashGuard`, because static initializers run; the library registry and abandoned files
(a crash in a module's static initialization or teardown poisons that file for the process);
`StrataScript_GetABIVersion`; the guarded `StrataScript_Load` with the host table and a zeroed module struct of known
capacity; the guarded description read and its validation as untrusted data (at most 65,536 classes, 4,096 fields and
1,024-byte names, duplicate names, required members, field and default types), with the function pointers copied out
once so that no later call reads module memory; ready. Then `ScriptModule::Call`: every call through `CrashGuard`, the
call site that reports and the watchdog read, and the mapping of results (Ok, Exception, Rejected, Faulted,
Unavailable). The engine-side types (`ScriptCallback`, `ScriptClassInfo` with its callback mask, `ScriptFault`,
`ScriptCodeLocation`). `ScriptEngine` and the active engine; the two hosts that create one, the editor (hot reload on)
and a shipped game (in place), each told in one sentence with a link. What `script.status` shows of a loaded module (a
text capture). What Strata does not do: modules linked statically. Tests: `Scripting.Module`, the test modules built to
fail (`ABIMismatch`, `Malformed`, `LoadFault`), and one that must load, `NewerSDK`, whose larger module description the
engine bounds. The example is the `Spinner`'s module of `start/first-game`, followed from its file to its first call. At
the end the reader can say what the engine checks before it calls into a module, and why module memory is read only
inside guarded calls.

**Leaves out.**

- What the description's structs hold → `scripting/abi-sdk`
- What happens inside a guarded call that faults → `scripting/crash-containment`
- Naming the frames of a fault → `scripting/symbolization`
- Replacing the module while scenes play → `scripting/hot-reload`
- The instances of a playing scene → `scripting/script-system`
- The editor's script engine and building before Play → `editor/script-builds`
- A shipped game's script engine → `worlds/runtime`

**Fit.** `fits`: about 5,300 words against L (5,000). The load walked in parts with its sequence figure, three more
excerpts, the ownership figure, one text capture and two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:155-161` | feature | home | `ScriptModule`, its load modes, the private copy directory, the library registry, call results, call sites and description validation |
| `scripting:162` | feature | home | `ScriptEngine`: one module, its faults and the watchdog (the reload protocol it runs is `scripting/hot-reload`'s) |
| `scripting:175` | feature | home | The engine-side types: `ScriptCallback`, `ScriptFieldInfo`, `ScriptClassInfo` with its callback mask, `ScriptCodeLocation`, `ScriptFault` |
| `scripting:187` | feature | home | `DynamicLibrary`: on Windows dependencies searched beside the file and the original, never in the current folder or PATH; on Linux and macOS through the module's RUNPATH (`$ORIGIN` and `@loader_path` name the copy's folder), the loader's environment variables and the system paths, the original's folder not searched (`Strata/src/Strata/Core/DynamicLibrary.h:24-31`); truncated files refused |
| `foundation:129` | feature | home | `DynamicLibrary` as the Core layer lists it, taught with `scripting:187`: a move-only class that owns one library, `Load` with a dependency directory (searched on Windows only), `GetFunction`, one handle for a file loaded twice, and `Release`, which `ScriptModule` calls when a module's unload crashed (`Strata/src/Strata/Core/DynamicLibrary.h:12-61`) |
| `scripting:196` | feature | home | The active engine: scenes use the engine that is active when they start |
| `scripting:146` | feature | home | The engine's test modules, above all those built to fail at load (ABIMismatch, Malformed, LoadFault), and one that must load, NewerSDK: its module description is larger than the engine's, and the test checks that it loads and that the engine bounds what it writes (`StrataTests/Scripts/NewerSDK/NewerSDKModule.cpp:1-3`; `StrataTests/src/Scripting/ScriptModuleTests.cpp:188-197`) |
| `scripting:367` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:301-344`: `ScriptModule::Call`, every call through `CrashGuard`, the fault recorded, the results mapped |
| `scripting:368` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:377-515`: `ScriptModule::Load`, in place or from a copy, the exports, the version, the guarded load and description read, complete results moved out |
| `scripting:373` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:942-1094`: validating the module's description as untrusted data, and copying the function pointers once |
| `new:5` | code | home | `Strata/src/Strata/Core/DynamicLibrary.h:24-41`: the loading contract (where dependencies are searched, a truncated file refused, one handle per loaded file) |
| `scripting:401` | figure | home | Who owns what in memory: the engine's records against the module's objects, and which side frees what |
| `scripting:403` | figure | home | Loading a module, a sequence diagram from the file check to ready |
| `scripting:441` | figure | home | `script.status` as a text capture: classes, fields, callbacks and a fault, what the engine learned from the description |
| `scripting:456` | rule | home | Every module call goes through `ScriptModule`, load and unload included; module memory is read only inside guarded calls, and complete results are moved out |
| `scripting:500` | rule | home | A crash inside the loader poisons that file for the process |
| `scripting:542` | hands-on | home | Exercise: build a module with `ST_SCRIPT_ABI_VERSION 2` (as the `ABIMismatch` module does) and read the refusal |
| `new:23` | hands-on | home | The "trace it yourself" exercise (R32, D27): with a breakpoint in `ScriptModule::Load` on the source build, the editor opens the first game's project and the reader follows the load of the `Spinner`'s module: the copy or the file, `LoadLibraryGuarded`, the ABI version, the guarded `StrataScript_Load` and `ReadModuleDescription`, back to `ScriptEngine::LoadModule` and its log line "Loaded script module" (about 250 words). Evidence: `Strata/src/Strata/Scripting/ScriptModule.cpp:346`, `:377-515`, `:942`; `Strata/src/Strata/Scripting/ScriptEngine.cpp:83`, `:120`; `StrataEditor/src/Editor/EditorContext.cpp:2213`, `:2225`, `:2436` (the editor loads the module when it opens the project's script engine) |
| `scripting:561` | term | home | Abandoned library or file |
| `scripting:563` | term | home | Active engine |
| `scripting:569` | term | home | Call site |
| `scripting:603` | term | home | Private copy |
| `new:4` | not-done | home | Script modules linked statically; the Roadmap names it with a console port. Evidence: `Docs/Roadmap.md:1709` |
| `scripting:198` | feature | link | A shipped game's script engine, named in one sentence (its home is `worlds/runtime`) |
| `scripting:197` | feature | link | The editor's script engine, named in one sentence (its home is `editor/script-builds`) |
| `scripting:369` | code | use | `CrashGuard`'s contract in one sentence, where `Call` uses it |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The ABI's two exports, descriptors and `StructSize` | `scripting/abi-sdk` | must |
| Shared libraries: loading, symbols, search paths, reference counts | `scripting/shared-libraries` | must |
| Talking to the operating system: platform seams, processes | `core/platform` | must |
| Files you can trust: UTF-8 paths, private files, `FileLock` | `core/files` | must |
| Errors returned instead of thrown; logging | `core/conventions` | must |
| The threading model and jobs | `core/jobs` | helps |
| What a guarded call returns when the code it runs faults | `scripting/crash-containment` | helps |

## `scripting/crash-containment` — Crash containment

**Covers.** The job: keep the engine and the editor running when native game code faults, and say exactly what cannot be
contained. The problem and how engines solve it, the full section for the part: most engines go down with the game;
process isolation (a process per plug-in, as browsers do); sandboxed virtual machines (Lua, WebAssembly); and Strata's
guard in the same process, which faults the module and keeps the engine, with a table of what each costs per call and
what each contains. Then from zero: hardware exceptions (an access violation, a division by zero, an illegal
instruction, a stack overflow and the guard page; integer division by zero traps on x64 but not on ARM64, where it gives
0, so the engine's fault tests leave it out there), Windows structured exception handling against POSIX signals, and how
a guard resumes after a fault (`__try` and `__except`; `sigsetjmp` and `siglongjmp` from a handler on an alternate
signal stack). Where the guard lives: `CrashGuard` and `Symbolizer` are Core classes with their halves in
`Platform/Windows` and `Platform/Posix`, and only `ScriptModule` calls them. The contract as `CrashGuard.h` writes it:
what is contained, what is not (fail-fast terminations, `abort()` on POSIX, a heap corrupted while the allocator holds
its locks, `exit`), destructors that do not run, the module that is never called again until it is reloaded (a rebuild
or `script.reload` clears the fault). The toy: a POSIX guard in about 40 lines. The real code: the Windows filter that
chooses 18 exception codes, `_resetstkoflw` after a stack overflow and the separate function that error C2712 forces;
the 32 KiB stack guarantee; the POSIX handler on its alternate stack, the delivered signal unblocked, handlers of other
code forwarded, and macOS's return into a recovery routine. Abort containment in modules: the SDK's entry file with
`init_seg(lib)`, `_set_abort_behavior` and a SIGABRT handler that raises `ST_SCRIPT_ABORT_EXCEPTION_CODE`, only with the
static C runtime. Exceptions against crashes: an exception the SDK's firewall caught disables one instance; a crash
faults the module, whose instances are leaked on purpose. The watchdog, a thread that can only log a call that runs too
long: it is off by default, `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it (only
tests do), so an endless loop freezes the editor and logs nothing; and why a script must never block. What the person
sees: the Console's crash line, and the toast whose button is **Show Problems**. Tests: `Scripting.Faults` with the
`Faults` and `LoadFault` modules, and the guard's own cases in `Core.Platform` (faults repeated, on other threads,
nested, the signal mask kept), whose helper processes show what the guard lets through: an `abort()`, a signal another
process sends, and a thread that exits on Linux. The example is a null write in a copy of the `Coin` script's
`OnUpdate`, then an exception thrown in its place, compared. At the end the reader can say for any fault whether Strata
contains it, and in what state the engine is afterwards.

**Leaves out.**

- Walking the stack and naming its frames → `scripting/symbolization`
- Debugging a crash with a debugger, and the engine's own crash reports → `core/debugging`
- What the editor does after a crash (play stops) → `editor/play-mode`
- A shipped game's crash policy (scripts disabled, exit code 2) → `worlds/runtime`
- Process signals such as SIGINT and SIGTERM, and exit codes → `core/platform`

**Fit.** `fits`: about 6,300 words against L (5,000). The full section on how engines solve the problem, the hardware
background taught from zero, five excerpts and three exercises take the most words; the stack walk is
`scripting/symbolization`'s.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:303` | concept | home | Crash containment of native code: hardware exceptions, SEH against signals, recovery by jump, alternate stacks, guard pages, destructors that do not run, what cannot be contained; the approaches elsewhere; the mistakes |
| `scripting:311` | concept | home | Exceptions against crashes, and why the engine's own exceptions never unwind into the module |
| `scripting:183-186` | feature | home | `CrashGuard::Invoke` and `CrashInfo`; the Windows guard; the POSIX guard; abort containment in modules |
| `scripting:52` | feature | home | `ST_SCRIPT_ABORT_EXCEPTION_CODE` (0xE0535441), the exception a module raises when it calls `abort()` on Windows |
| `scripting:163` | feature | home | The containment contract that `ScriptEngine.h` lists |
| `scripting:176` | feature | home | The watchdog: off by default; `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it, only tests (`Strata/src/Strata/Scripting/ScriptEngine.h:95-96`, `ScriptEngine.cpp:257-266`; `StrataTests/src/Scripting/ScriptFaultTests.cpp:346`, `ScriptModuleTests.cpp:330`, `:341`); when on, it logs a call that runs too long and cannot interrupt it |
| `scripting:190` | feature | home | The policy: an exception disables one instance, a crash faults the module |
| `foundation:97` | feature | home | `CrashGuard` and `Symbolizer` as the Core layer lists them: Core classes with their halves in `Platform/`, called only by `ScriptModule`; the guard's cases in `Core.Platform` (`StrataTests/src/Core/PlatformTests.cpp:729-912`). The facts of `Symbolizer` are taught with `scripting:188` on `scripting/symbolization` |
| `scripting:369` | code | home | `Strata/src/Strata/Core/CrashGuard.h:35-68`: the contract, what is not contained included |
| `scripting:370` | code | home | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp:96-159`: the SEH filter, `_resetstkoflw`, the `__try` in its own function (C2712); with lines 196-212, `Invoke` |
| `scripting:372` | code | home | `Strata/src/Platform/Posix/PosixCrashGuard.cpp:348-402`: `Invoke` with `sigsetjmp`, the unblocked signal, the alternate stack check; with lines 28-40 (leaving the handler on Linux and macOS) and 239-260 (the handler) |
| `scripting:359` | code | home | `StrataScriptCore/Source/ScriptModuleEntry.cpp:1-81`: abort containment in the module, `init_seg(lib)`, `_set_abort_behavior` and the SIGABRT handler, and the two exports |
| `scripting:417` | figure | home | Crash containment, Windows and POSIX side by side: the guarded call, the fault, the filter or handler, unwind or jump, `Invoke` returns false, the fault recorded, the module faulted; and the exits that are not contained |
| `scripting:437` | figure | home | The Console's crash message and location line, and the toast with **Show Problems** |
| `scripting:476` | rule | home | Exceptions disable an instance; crashes fault the module |
| `scripting:479` | rule | home | Never block in a script: native code cannot be preempted, and the watchdog can only log, and only where a host turned it on; the editor and the runtime do not, so an endless loop freezes the editor without a line in the log |
| `scripting:492` | rule | home | Windows modules use the static C runtime and the SDK's entry points to contain `abort()` |
| `scripting:525` | hands-on | home | Crash on purpose: a null write in `OnUpdate`, then an exception in its place; one instance disabled against the module faulted |
| `scripting:544` | hands-on | home | Lab: a small program around `CrashGuard::Invoke` that divides by zero, overflows the stack twice and calls `abort()`, on Windows and Linux; integer division by zero traps on x64, not on ARM64, where it gives 0 (`StrataTests/src/Scripting/ScriptFaultTests.cpp:31-34`) |
| `scripting:550` | hands-on | home | Design review: in-process containment against a child process or WebAssembly, the cost per call and what each contains |
| `new:24` | hands-on | home | The "trace it yourself" exercise (R32, D27): the null write of `scripting:525` followed with a debugger on the source build: on Windows the first-chance access violation, the filter that accepts it and `Invoke` returning false; on Linux the handler on the alternate stack and the jump back into `Invoke`; then `ScriptModule::Call`, which records the fault and returns `Faulted` (about 250 words). Evidence: `Strata/src/Platform/Windows/WindowsCrashGuard.cpp:96-159`, `:196-212`; `Strata/src/Platform/Posix/PosixCrashGuard.cpp:239-260`, `:348-402`; `Strata/src/Strata/Scripting/ScriptModule.cpp:317-327` |
| `scripting:564` | term | home | Alternate signal stack |
| `scripting:573` | term | home | CrashGuard |
| `scripting:582` | term | home | Fault: a faulted module is never called again until the module is reloaded; a rebuild or `script.reload` clears the fault (`Strata/src/Strata/Scripting/ScriptEngine.h:27-29`) |
| `scripting:608` | term | home | SEH (structured exception handling) |
| `scripting:610` | term | home | `sigsetjmp` and `siglongjmp` |
| `scripting:611` | term | home | Stack guarantee |
| `scripting:620` | term | home | Watchdog: off by default; `SetWatchdogTimeout` turns it on, and neither the editor nor the runtime calls it |
| `scripting:371` | code | use | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp`, lines 43-60 of the excerpt: the stack guarantee (the stack walk of lines 61-94 is `scripting/symbolization`'s) |
| `scripting:106` | feature | use | The SDK's exception firewall, which decides that an exception is no crash |
| `scripting:385` | code | use | The `Coin` script, broken on purpose in a copy |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| How a computer runs a program: the CPU, the stack and the heap | `basics/computer` | must |
| Talking to the operating system: signals, exit codes, platform seams | `core/platform` | must |
| Debugging the engine: debuggers, asserts and crash reports | `core/debugging` | must |
| C++ exceptions and the engine's error policy | `core/conventions` | must |
| `ScriptModule::Call` and the fault it records | `scripting/loading` | must |
| The SDK's exception firewall (`InvokeScript`) | `scripting/abi-sdk` | must |
| Threads and per-thread state | `basics/threads` | helps |
| Hexadecimal numbers and bit patterns | `basics/numbers` | helps |
| Play mode and what stops it | `editor/play-mode` | helps |

## `scripting/symbolization` — From an address to a file and line

**Covers.** The job: turn the addresses a fault recorded into module, function, file and line, and choose the frame the
report names. The problem in one paragraph (offline symbolization of crash dumps, symbol servers, in-process
symbolizers). From zero: return addresses and the call stack in memory; unwinding with unwind tables
(`RtlLookupFunctionEntry` and `RtlVirtualUnwind` on Windows x64, and a leaf function, which has none); a module's base
and an offset into it; debug information (the PDB; DWARF; the ELF symbol table); inlining and inline frames. The
contract of `Symbolizer`: `Describe` is cheap, needs no debug information and runs at fault time while the module is
still loaded; `Resolve` reads debug information, blocks, runs on a job and is serialized, because DbgHelp is
single-threaded. The toy: an address and a sorted symbol table, the nearest symbol below it, in about 30 lines. The
real code in the order data flows: the stack the Windows guard captures from the fault's context (none after a stack
overflow; on POSIX the faulting instruction only); `RecordFault`, which describes every frame at once and resolves the
module's frames on a job, inline frames marked; DbgHelp's resolve with a session handle of its own, the module read
from its file at its base, and the inline trace; Linux's bounds-checked read of the ELF `.symtab`, because the module
hides its symbols from `dladdr` (a function, no file or line: Strata has no DWARF reader); macOS's `dladdr`;
`ChooseFaultLocation`, which skips the C runtime's frames and the SDK's entry file. The erratum the page must not
repeat: `Symbolizer.h` says that POSIX uses `dladdr` only. What the person sees: the Problems panel with a crash's
frames, one marked "(inlined)". Tests: the fault-location cases of `Scripting.Faults`. The example is the null write of
`scripting/crash-containment`, built in Release so that the compiler inlines a helper. At the end the reader can
explain why an optimized build on Windows still names the line that crashed, and why Linux and macOS name only the
function.

**Leaves out.**

- Catching the fault and the containment contract → `scripting/crash-containment`
- Debuggers, and the engine's own crash reports → `core/debugging`
- How the Problems panel draws its list → `editor-ui/instrument-panels`
- Why every configuration writes a PDB (the module's CMake) → `scripting/shared-libraries`

**Fit.** `over`: about 5,100 words against M (3,000). Five ideas taught from zero (return addresses, unwinding, a
module's base, debug information, inlining) and five excerpts on three platforms take the most words; by S2 the next
size, L (5,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:315` | concept | home | Symbolization: return addresses, unwind tables, module and offset, debug information, inline frames, why the fault location skips runtime frames, why it runs on a job |
| `scripting:188` | feature | home | `Symbolizer::Describe` and `Resolve`: DbgHelp with inline frames on Windows, the ELF `.symtab` on Linux, `dladdr` on macOS |
| `scripting:189` | feature | home | The fault location: the first module frame with a source that is not the C runtime or the entry file |
| `scripting:371` | code | home | `Strata/src/Platform/Windows/WindowsCrashGuard.cpp:61-94`: the stack walk from the fault's context with `RtlVirtualUnwind`, and the leaf function (lines 43-60 of the inventory's excerpt, the stack guarantee, are used by `scripting/crash-containment`) |
| `scripting:374` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:622-720`: recording a fault, describing the frames now and symbolizing on a job; with lines 580-605, choosing the reported frame |
| `new:7` | code | home | `Strata/src/Platform/Windows/WindowsSymbolizer.cpp:148-199`: `Resolve` with DbgHelp, serialized, the module loaded from its file at its base and size |
| `new:8` | code | home | `Strata/src/Platform/Windows/WindowsSymbolizer.cpp:79-107`: the calls the compiler inlined at an address, from DbgHelp's inline trace |
| `new:9` | code | home | `Strata/src/Platform/Posix/PosixSymbolizer.cpp:48-91`: the function at an offset from the ELF file's `.symtab`, every read bounds-checked; lines 96-125 show `Describe` and `Resolve` on POSIX |
| `new:6` | erratum | home | `Strata/src/Strata/Core/Symbolizer.h:14` says that POSIX uses `dladdr` only; Linux also reads the ELF `.symtab` for the module's hidden functions, and neither POSIX system gives a file or line. Evidence: `Strata/src/Strata/Core/Symbolizer.h:14`; `Strata/src/Platform/Posix/PosixSymbolizer.cpp:32-35`, `106-111`, `117` |
| `scripting:424` | figure | home | Symbolization: the stack of return addresses, module and offset at fault time, the job, the PDB lookup with inline frames, the chosen location |
| `scripting:435` | figure | home | The Problems panel with a crash and its stack frames, one marked "(inlined)"; its compiler-error half is used by `editor/script-builds` |
| `new:25` | hands-on | home | The page's exercises (R32, D27), with its "trace it yourself": the null write of `scripting/crash-containment` moved into a helper that the compiler inlines, built in Release; the reader predicts the frames, then follows with breakpoints the frames `RecordFault` describes and the first location it chooses, the job that resolves them with `Symbolizer::Resolve` and puts the inline frame first, and `GetFault`, which chooses again once the job is done; and a question: what Linux shows of the same crash, and why (a function, no file or line) (about 250 words). Evidence: `Strata/src/Strata/Scripting/ScriptModule.cpp:591`, `:608-620`, `:622`, `:674`, `:686-719`; `Strata/src/Platform/Posix/PosixSymbolizer.cpp:48-91` |
| `scripting:575` | term | home | DbgHelp |
| `scripting:592` | term | home | Inlining and inline frame |
| `scripting:601` | term | home | PDB |
| `scripting:613` | term | home | Symbolization |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| `CrashGuard` and the stack it records | `scripting/crash-containment` | must |
| Shared libraries: a module's base, symbols and their visibility | `scripting/shared-libraries` | must |
| The threading model and jobs, results returned to the main thread | `core/jobs` | must |
| How a computer runs a program: the stack in memory | `basics/computer` | must |
| The call stack and a debugger | `basics/debugging` | helps |
| Hexadecimal addresses | `basics/numbers` | helps |
| Atomics and memory order | `basics/threads` | helps |
| Reading untrusted files with bounded reads | `core/files` | helps |

## `scripting/script-system` — The script system

**Covers.** The job: `ScriptSystem` runs the scripts of one playing scene: it creates instances from Script components,
calls their callbacks in a fixed order and stays consistent while scripts change the scene under it. The problem in one
paragraph that links `scripting/why-scripts`. Registration: the Script component (its entries, field overrides,
serialization, references for entity and asset fields) and the "Scripting" scene system (Play only, not Simulate;
profile stage `Scene.Scripts`; before physics). The callbacks and their order, named here for track E (their home for
game makers is `make/script-loop`), on a frame timeline (figure): UI events, `OnUpdate`, the fixed steps with contacts
and `OnFixedUpdate`, animation events, `OnLateUpdate`, where the step alpha is final, so a camera reads drawn poses
there and a ridden platform moves in `OnFixedUpdate`, and destruction at the end of the frame; why press edges are read
in `OnUpdate`; the 15 callbacks of the class descriptor and when each arrived. The map: the instance's states (figure):
constructed with its fields, pending start, created, disabled after an exception, removed and destroyed at a sync point.
The toy: a system with a list of instances, a frame and a deferred destroy, about 60 lines. Then the real code: the
start of play (the scripted entities marked in hierarchy order, their instances created and `OnCreate` run at the first
sync point, once every scene system has started) and its stop (`OnDestroy` in the reverse of the update order,
descendants first, then the asset pins released); what a call's result does (an exception disables its instance, a
faulted module gets no further calls); the three update phases and the sync-point loop, bounded at 64 rounds (deferred
destroys, dirty entities reconciled, `OnReload`, `OnCreate`); what reconciliation does with entries the module cannot
serve (a class the module lacks gets no instance and a problem, a class listed twice on one entity runs once, so
renaming a class detaches it from every entity, as renaming a field loses its value); deferred mutation through
`ScriptSystem::DestroyEntity` and the copies of lists taken before script code runs; the dispatch loop over lists of
only the implementing instances, its skip conditions, activity read from the scene's cache (inactive entities get no
`OnUpdate`, `OnFixedUpdate` or `OnLateUpdate` and no new contacts or animation events, while `OnCreate` and `OnDestroy`
run anyway) and the software prefetch, with why the hardware prefetcher did not help. Update order and its cost:
hierarchy order, then entry order, kept by binary-search insertion, the re-placement of moved entities and lazy
compaction at one eighth destroyed (figure). Contact delivery (every Enter gets its Exit; normals flipped for the other
side); animation and UI events. Fields: per-entity overrides by name and type, live get and set for the inspector and
`script.get`. Assets from game code: an `AssetPin` for each requested asset and a group request for each progress query,
released when play stops, so `Instantiate` never waits; the requests are the scene's, not the script's, and do not add
up, so one `Assets::Release` ends a request that two scripts made. The rule against keeping a `T*` from `GetScript<T>()`
across frames. Tests: `Scripting.Lifecycle`, `Scripting.Order`, `Scripting.Collisions` and the `Perf.Scripting` dispatch
tests. The example is the ThirdPerson sample's `Coin`: its three fields, `OnCreate` that finds the model,
`OnTriggerEnter` and its call to `CourseState`. At the end the reader can predict the order of a scene's callbacks, and
say why a script may destroy the entity whose callback is running.

**Leaves out.**

- The lifecycle as a game maker uses it → `make/script-loop`
- How contacts are found and folded → `physics/contacts-triggers`
- How the UI raises its events → `ui/input`
- How animation events are found → `animation/time-events`
- Replacing instances on a reload → `scripting/hot-reload`
- The host functions that scripts call (`Instantiate` among them) → `scripting/host-api`
- Residency and pins in general → `assets/residency`
- The running copy of Play mode → `editor/play-mode`
- The inspector's Script drawer → `editor-ui/inspectors`

**Fit.** `over`: about 6,700 words against L (5,000). Four concepts, three excerpts, three figures and five rules, with
the callbacks named for track E, take the most words; by S2 the next size, XL (8,000).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:153-154` | feature | home | `RegisterScriptingModule` (the Script component and the "Scripting" scene system) and the Script component itself |
| `scripting:164-169` | feature | home | `ScriptSystem`, update order, dispatch lists, sync points, field values, asset requests |
| `scripting:92` | feature | home | The 15 class callbacks, when each arrived, and the four lists that agree (`StrataScriptClassDesc`, `ScriptCallback`, `CallbackFlag`, `ClassFunctions`) |
| `animation:178` | feature | home | `OnAnimationEvent`: its flag, its thunk and the dispatch from the system's listener to the active scripts on the animator's entity (`Strata/src/Strata/Scripting/ScriptSystem.cpp:389-407`), the example of an event callback |
| `scripting:294` | concept | home | Deferred mutation and safe points: deferred destruction, flagged removals, copies of lists, bounded sync rounds; the mistakes |
| `scripting:299` | concept | home | Update order and its cost: a deterministic order against cache use, incremental maintenance, dispatch lists, prefetching |
| `scripting:326` | concept | home | Serialized fields and the editor: per-entity overrides by name and type; renaming or retyping a field |
| `scripting:334` | concept | home | Asynchronous assets from game code: request early, spawn when loaded, pins, progress of a closure |
| `scripting:379` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:195-221`: the three update phases; with lines 482-505, the sync point and its bound |
| `scripting:380` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:241-287`: the dispatch loop, its skip conditions, activity from the cache, software prefetch and why; beside it the rule for inactive entities: no update callbacks and no new contacts or animation events, but `OnCreate` and `OnDestroy` run anyway (`ScriptSystem.h:55-56`; `ScriptSystem.cpp:347-351`, `:394`, `:664-680`; no `Scripting.*` test plays a script on an entity inactive at its start, so the `OnCreate` half is read, not tested) |
| `scripting:382` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:340-383`: contact delivery, every Enter with its Exit, copies of lists, normals flipped |
| `new:27` | feature | home | Script entries the module cannot serve, beside reconciliation (critic-scripting-8): an entry whose class the module lacks (renamed or deleted) gets no instance and a problem is reported; the same class listed twice on one entity runs once, the duplicate reported; on a hot reload a class that no longer exists loses its instances, with a problem, while its entries stay and get an instance again once a module has the class; so renaming a class detaches it from every entity, as renaming a field loses its value (about 100 words). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.cpp:611-625`, `:1290-1297`, `:1346-1347`; `Strata/src/Strata/Scripting/ScriptEngine.h:60-62` |
| `new:28` | feature | home | A script's asset requests belong to the scene, not to the script, and do not add up: one `Assets::Release` ends a request that two scripts made, and the asset may then be evicted while the other script still uses it; one sentence beside the pins (critic-scripting-17). Evidence: `Strata/src/Strata/Scripting/ScriptSystem.h:131-132`; `StrataScriptCore/Include/StrataScript/Scene.h:44-47` |
| `scripting:411` | figure | home | The instance's states, from constructed to destroyed, with the disabled and the reload branches |
| `scripting:414` | figure | home | A frame from the scripts' side, and where `Time::GetStepAlpha` becomes final |
| `scripting:422` | figure | home | Update order maintenance: the hierarchy, the flat order with its placed part and appended tail, a binary-search insertion, tombstones and the compaction |
| `scripting:464` | rule | home | Script code never runs while engine state it could invalidate is in use: destroy through `ScriptSystem::DestroyEntity` |
| `scripting:474` | rule | home | Never keep a `T*` from `GetScript<T>()` across frames; store the `Entity` |
| `scripting:481` | rule | home | Request assets early; `Instantiate` never waits |
| `scripting:483` | rule | home | Read press and release edges in `OnUpdate`: `OnFixedUpdate` runs zero or more times per frame |
| `scripting:485` | rule | home | Read the drawn pose in `OnLateUpdate`; move ridden platforms in `OnFixedUpdate` (the drawn transforms are `world/interpolation`'s) |
| `scripting:546` | hands-on | home | Measure dispatch: `Perf.Scripting.TrivialUpdate100k` in Release with and without the prefetch lines |
| `scripting:548` | hands-on | home | Why copy the list: find each "A copy" comment of `ScriptSystem.cpp` and build the bug it prevents |
| `scripting:565` | term | link | `AssetPin`: a script's request holds one; the term's entry is on `assets/residency` |
| `scripting:577` | term | home | Dispatch list |
| `scripting:586` | term | home | Field override |
| `scripting:594` | term | home | Instance (of a script class) |
| `scripting:602` | term | home | Prefetch (the CPU's) |
| `scripting:614` | term | home | Sync point |
| `scripting:619` | term | home | Update order |
| `scripting:289` | concept | use | The script lifecycle and its callbacks, named for track E; its home is `make/script-loop` |
| `scripting:385` | code | use | The `Coin` script as the page's example |
| `scripting:341` | concept | link | Interpolation of fixed-step motion, one sentence and a link to `world/interpolation` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Systems, phases and fixed steps in `Scene`; scene services | `world/systems` | must |
| The fixed step, the accumulator and time dilation | `core/time` | must |
| The transform contract and the hierarchy | `world/scene-graph` | must |
| Residency, pins and eviction | `assets/residency` | must |
| Contacts and triggers reaching scripts | `physics/contacts-triggers` | must |
| Animation events | `animation/time-events` | must |
| Calls into a module through `ScriptModule` | `scripting/loading` | must |
| Caches, and why the order of data in memory matters | `basics/computer` | must |
| Arrays, binary search and their costs | `basics/data-structures` | must |
| Interpolation of fixed steps: drawn transforms | `world/interpolation` | helps |
| Reflection and the registry's signals | `world/reflection` | helps |
| UI events reaching scripts | `ui/input` | helps |
| The script lifecycle as game makers learn it | `make/script-loop` | helps |

## `scripting/hot-reload` — Hot reload

**Covers.** The job: replace the module while the game runs and keep what the scripts can keep. The problem and how
engines solve it, the full section, since this page is the home of hot reload of scripts: a restart with saved state;
swapping a library with its state serialized (Strata, many in-house engines); binary patching (Live++, Unreal's Live
Coding); interpreters that reload functions; with a table of what each keeps, what each costs and who uses it. The
timeline (figure), walked in code: hot reload turned on moves a module that runs from its file to a private copy,
because Windows locks a loaded DLL; the watcher reports the file once it stayed unchanged for 300 ms;
`ScriptEngine::Update` reloads between frames and retries up to 20 times at 250 ms while the file is busy; the new
module loads beside the old one, so a broken build leaves the old one running; each running scene's `BeginModuleReload`
snapshots the fields of every instance and destroys the instances without `OnDestroy`; the old library unloads;
`EndModuleReload` recreates the instances, restores the fields that keep their name and type, and `OnReload` runs
instead of `OnCreate` at the next sync point. The toy: a reload of a one-class module with its fields in about 50 lines.
What survives: fields only; everything else (cached entities, script pointers, plain members) starts over and is found
again in `OnReload`, and the module's globals and statics start over too, because the new module is another library.
Copies and dependencies: `$ORIGIN` and `@loader_path` resolve from the copy's folder. Failures: a module that does not
load, a reload refused while script code is on the stack, a faulted module replaced by a good one, and a class that no
longer exists, whose instances are dropped with a problem. What the person sees: a playing ThirdPerson copy before and
after a rebuild, and the log line "Reloaded script module". Tests: `Scripting.Reload` with the `ReloadV1` and `ReloadV2`
modules. The example is the ThirdPerson `Coin`: `SpinSpeed` keeps the value set in the Inspector, the non-field `m_Time`
starts over, and its `OnReload` calls `OnCreate` to find its model again. At the end the reader can say what a reload
keeps and loses, and why the build never fights the running game for the file.

**Leaves out.**

- The load modes and the private copy directory → `scripting/loading`
- The editor's builds that write the new module → `editor/script-builds`
- Hot reload of assets, the other meaning → `assets/importing`
- Using hot reload while making a game → `make/first-script`

**Fit.** `fits`: about 4,800 words against L (5,000). The full section on how engines reload code, three excerpts, the
timeline, the before-and-after screenshots and two exercises take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:319` | concept | home | Hot reload: the approaches, Strata's swap with fields kept, why private copies; the mistakes (state in plain members, pointers into the old module, RUNPATH under copies) |
| `scripting:378` | code | home | `Strata/src/Strata/Scripting/ScriptEngine.cpp:65-124`: the new module loaded beside the old one and the reload across scenes; with lines 196-229, the debounced reload with retries |
| `scripting:381` | code | home | `Strata/src/Strata/Scripting/ScriptSystem.cpp:1221-1348`: a reload in a scene, the snapshot, destruction without `OnDestroy`, the recreation, the restore, `OnReload` or `OnCreate` |
| `new:10` | code | home | `Strata/src/Strata/Scripting/ScriptEngine.cpp:154-189`: turning hot reload on moves a module to a copy; the watcher with its 300 ms debounce |
| `scripting:419` | figure | home | The hot reload timeline, with the failure branch that keeps the old module and the retry branch for a busy file |
| `scripting:438` | figure | home | Hot reload in action: a playing ThirdPerson copy before and after a rebuild of `Coin`, with the log line |
| `scripting:472` | rule | home | Only fields survive hot reload; re-acquire everything else in `OnReload`; the module's globals and statics start over too, since the new module is another library loaded beside the old one, which then unloads (`Strata/src/Strata/Scripting/ScriptEngine.cpp:79-83`, `:107`) |
| `scripting:494` | rule | home | Hot reload runs a copy; `$ORIGIN` and `@loader_path` point at the copy's folder |
| `scripting:511` | hands-on | home | Hot reload a running game: change `Coin`'s behaviour while playing a ThirdPerson copy, then add a plain member and see it start over |
| `new:26` | hands-on | home | The "trace it yourself" exercise (R32, D27): with a breakpoint in `ScriptSystem::BeginModuleReload` while a ThirdPerson copy plays and `Coin` is rebuilt, the reader walks up the stack to `ScriptEngine::Update`, which the watcher's report started, then on through the swap in `ScriptEngine::LoadInternal`, `EndModuleReload` and the `OnReload` call at the next sync point (about 250 words). Evidence: `Strata/src/Strata/Scripting/ScriptEngine.cpp:65`, `:101`, `:107`, `:114`, `:196-229`; `Strata/src/Strata/Scripting/ScriptSystem.cpp:659-660`, `:1221`, `:1276` |
| `scripting:576` | term | home | Debounce |
| `scripting:591` | term | home | Hot reload (of scripts), one of the two meanings |
| `scripting:156-157` | feature | use | Load modes and the private copy directory (their home is `scripting/loading`) |
| `scripting:168` | feature | use | Field values, snapshot and restore |
| `new:27` | feature | use | A class that no longer exists after a reload, named among the failures in one sentence (its home is `scripting/script-system`) |
| `scripting:385` | code | use | The `Coin` script as the example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Instances, sync points and field values | `scripting/script-system` | must |
| Load modes and private copies | `scripting/loading` | must |
| Shared libraries: unloading, reference counts, RUNPATH | `scripting/shared-libraries` | must |
| Files you can trust: watching a folder, private files | `core/files` | must |
| What a fault leaves behind | `scripting/crash-containment` | helps |
| Building scripts from the editor | `editor/script-builds` | helps |

## `scripting/host-api` — The host API: engine services behind a C table

**Covers.** The job: give game code the engine's services through one C table, without letting it see an engine
header. The pattern, the full section: a table of function pointers and an opaque context, as plug-in SDKs and
Vulkan's loader do, and why (isolation, safe reloads, testing by counting calls). A host call round trip in the order
data flows (figure), walked from the SDK's side (`Entity::SetProperty` and `GetProperty`, `ValueTraits`, the second
read for long strings) to the counted thunk, `HostSetProperty`, `HostCall`, `ResolveContext` and the component access,
with every failure exit. The toy: a table of two functions with a context check, about 50 lines. Then the real code.
The two guards every host function starts with: `ResolveContext` against the registry of contexts (no context, another
thread, a stale context, no call in progress, a faulted module) and `HostCall` (no exception unwinds into the module).
Validation and `ReportProblem`: what the host reports (the list), a warning that names the calling script and entity,
once per message, at most 1,024 per scene; and why a host function never asserts. A tiny host function
(`SetTimeScale`) and a real one (`Instantiate`, which starts the load and returns no entity until the asset is
loaded, and creates the new entities' instances at once). The X-macro table `ST_SCRIPT_HOST_FUNCTIONS`, the `constexpr`
check that it covers the struct exactly, the counted thunks, and Dist builds without counters. The gameplay API as a
facade: Scripting may include only Core, Input, Asset, Reflection and Scene, so every gameplay function goes through
a scene service or an engine service and fails, reported, when the service is absent, as the host's own messages say:
an engine without the physics, audio or animation module ("the scene plays without physics (the engine has no physics
module)"), a scene that streams no world ("the scene streams no world"), a program with no window or no save directory
("the program running the game has no save directory"); scripts never run in Simulate; the table's 27
groups, the service each reaches and the wave each arrived in, up to 165 functions. Player-facing services: save
files, rebindable input, graphics options and the window, each with one owner of its file. The save service as the
example: the save functions ask `IGameSaves` for the directory and call `SaveFiles`, which checks a name in the engine
before any path is formed (1 to 64 ASCII characters, no `..`, no device name), writes atomically, refuses more than
64 MiB and blocks the main thread; `SaveDirectory` is what a shipped game provides, found on first use, and the
editor's play mode keeps saves in the project's `.strata/Saves`. Value conversion: exact for
fields, lenient for component properties (integers for enums, three or four numbers for colors, a vector or a
quaternion for rotations). Tests: the `Scripting.*` suites, which page each belongs to, and the call counters the
feature test reads. The example is `Time::SetTimeScale`, followed from the SDK to `HostSetTimeScale` (the trace
exercise). At the end the reader can say what a host function must do before it touches the engine, which service it
must go through, and where a new one must be listed.

**Leaves out.**

- Every host function and SDK call with its failure value → `reference/script-api`
- Adding a host function step by step → `scripting/tutorial-host-function`
- Scene services and where each is implemented → `world/systems`
- Engine services and engine modules → `core/engine-modules`
- The script face of physics queries → `physics/queries`
- The script face of audio → `audio/scene-system`
- The script face of animators → `animation/system`
- The script bridge of the game UI → `ui/input`
- The script face of world streaming → `worlds/physics-scripts`
- Players' graphics options → `image/quality-settings`
- The feature test's coverage checks → `engineering/feature-test`

**Fit.** `fits`: about 6,200 words against L (5,000). Four excerpts, the round-trip figure, the table of 27 groups and
the save service take the most words; the subsystems' script faces are linked, not taught.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:63-90` | feature | home | The 27 groups of the host table as one table: their functions, the service each reaches, the wave each arrived in |
| `scripting:170-174` | feature | home | `ReportProblem`, the host API's implementation, the registry of contexts, the call counts, value conversion |
| `scripting:177` | feature | home | The problems the host reports |
| `scripting:199-201` | feature | home | The engine services and the scene services the host API goes through, and the layer rule that forces them |
| `scripting:216` | feature | home | The `Scripting.*` suites and the other tests of the part, each named with its page |
| `scripting:273` | concept | home | The host API as a service table: the pattern, why, and the mistake of calling the engine from other threads or outside callbacks |
| `scripting:330` | concept | home | The gameplay API as a facade over engine services, taught once; each subsystem's page shows its script face |
| `scripting:338` | concept | home | Player-facing systems: saves, rebindable input, graphics options, the window; one service owns each file |
| `foundation:130` | feature | home | The save service behind the save functions: `SaveFiles` (names checked before a path is formed, atomic writes, the 64 MiB cap, calls that block) and `SaveDirectory`, the `IGameSaves` a shipped game provides (`Strata/src/Strata/Core/SaveFiles.h:14-65`, `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:2224-2262`); where an exported game's saves go is `worlds/game-identity`'s |
| `audio-input:365` | concept | home | Crossing the script ABI for audio and input: action names and bindings as strings, the text buffer protocol, failure values and `ReportProblem`; one instance of the facade, whose audio and input sides `audio/scene-system` and `input/actions` show |
| `animation:176` | feature | home | The twelve animator host functions, one row of the groups table |
| `animation:179` | feature | home | The animator functions' misuse reporting (`RequireAnimation`, `RequireAnimator`, `ControlAnimator` inside `HostCall`), an example of a subsystem's guards |
| `audio-input:543` | rule | home | Host functions report misuse and return failure values, as the input area states it; one rule box with `scripting:459` |
| `scripting:375` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:67-116`: `ResolveContext` and `HostCall` |
| `scripting:376` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:356-370`: `SetTimeScale`, input checked and reported; with lines 830-897, `Instantiate`, which never waits |
| `scripting:377` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3598-3622`: the `constexpr` check that the list covers the struct; with lines 3427-3437 (the head of the X-macro) and 3624-3672 (counted thunks, and Dist without counters) |
| `gamedev:363` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:358-396`: `GetProperty` and `SetProperty`, the SDK's side of a host call, with the stack buffer and the second read; with `Host.h:19-24` and `105-111` (the table pointer and `ST_SCRIPT_DETAIL_HOST_WITH`), which `scripting/abi-sdk` showed |
| `scripting:408` | figure | home | A host call round trip, with the failure exits |
| `scripting:459` | rule | home | Host functions wrap their body in `HostCall`, start with `ResolveContext`, report misuse, return failure values and never assert |
| `scripting:462` | rule | home | The engine is single-threaded towards scripts: call it only from callbacks, never from your own threads |
| `scripting:487` | rule | home | Input actions for anything a player might rebind; one owner for the bindings file, the graphics options file and the saves |
| `scripting:498` | rule | home | Field values convert exactly, component properties leniently |
| `scripting:532` | hands-on | home | Trace one host call: `Time::SetTimeScale` from the SDK to `HostSetTimeScale` and its counted thunk, each guard explained |
| `scripting:590` | term | home | Host function |
| `gamedev:607` | term | home | Host function, as a game maker's guide names it; one entry with `scripting:590` |
| `audio-input:692` | term | home | Host function, as the input area names it; one entry with `scripting:590` |
| `scripting:604` | term | home | ReportProblem |
| `scripting:621` | term | home | X-macro |
| `scripting:687` | open | home | When the first groups arrived (physics, queries, audio, game flow before 0.3.0): the page checks the release notes and the Roadmap at the pin, and states only what they say |
| `new:18` | erratum | home | Concept 16 of `plan/inventory/scripting.md` (lines 330-333) gives Simulate as the case where a gameplay service is absent (`process.md`'s table of errata, kind `inventory`); scripts never run in Simulate, since the Scripting system runs only in Play, and a host function reports an absent service when the engine has no physics, audio or animation module, when the scene streams no world, or when the program has no window or no save directory. Evidence: `Strata/src/Strata/Scripting/ScriptingRegistration.cpp:15-17`; `Strata/src/Strata/Scripting/ScriptSystem.h:37-38`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1172-1174`, `:2150`, `:2230`, `:2649` |
| `scripting:53` | feature | use | The host table as a struct (its home is `scripting/abi-sdk`) |
| `scripting:118-136` | feature | link | The SDK's gameplay classes, each named with its group and linked to its home: the subsystems' pages for the classes with a twin, `make/scripting-scene`, `basics/programming-1`, `make/levels-saves`, `make/recipes` and `make/timers-events` for the others, `image/quality-settings` for `Graphics`, `worlds/physics-scripts` for `World`; `reference/script-api` lists their facts |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Engine services and engine modules | `core/engine-modules` | must |
| The composition root, dependency inversion and the layer table | `core/layers-registries` | must |
| Scene services | `world/systems` | must |
| The host table, the buffer protocol and `ST_SCRIPT_DETAIL_HOST_WITH` | `scripting/abi-sdk` | must |
| Contexts, call sites and instances of the script system | `scripting/script-system` | must |
| Reflection: components and properties by name | `world/reflection` | must |
| Macros and `constexpr` | `basics/cpp-modern` | must |
| Atomics and relaxed counters | `basics/threads` | helps |
| Residency and loading without stalling | `assets/residency` | helps |
| Input actions | `input/actions` | helps |
| Players' graphics options | `image/quality-settings` | helps |

## `scripting/tutorial-host-function` — Tutorial: adding a host function and a callback

**Covers.** What the reader makes: the WindZone of `world/tutorial-component` becomes readable from scripts through a
new host function behind `Wind::GetStrength`, and scripts hear about wind through a callback appended to
`StrataScriptClassDesc`. Every step follows the newest group of the table (`GetStepAlpha` and its neighbours, wave 8) as
its model, quoted beside the reader's change. Section 1, the host function: append the member at the end of
`StrataScriptHostAPI` and see the build fail at the `static_assert` of `ST_SCRIPT_HOST_FUNCTIONS` (a text capture);
reach the zones through a new scene service, because the WindZone is the Physics module's and Scripting may include only
Core, Input, Asset, Reflection and Scene (`StrataTests/Architecture/Layers.json:76-78`): an interface in
`Scene/SceneServices.h` that the WindZone's system registers in its constructor and unregisters in its destructor, as
`PhysicsSystem` does with its services, and that the host function looks up with `GetService`, reporting the absent
service when no system offers it, so that `Architecture.Layering` passes; implement the host function with `HostCall`,
`ResolveContext` and `ReportProblem`; list it at the end of the X-macro; wrap it in the SDK with
`ST_SCRIPT_DETAIL_HOST_WITH`, so a module built for this engine still runs on an older one; call it from the API test
module with the "older engine" check, and from a `Scripting.*` test; call it from a feature script and run the feature
test, which fails before the call and passes after it (two sentences say what the feature test checks of a new host
function and link `engineering/feature-test`, which teaches it). Section 2, the callback: append it to
`StrataScriptClassDesc` and to `ScriptCallback` (whose `c_ScriptCallbackCount` follows the last value); in the SDK, its
virtual function, `CallbackFlag`, override check, thunk and slot in `BuildClassRecord`; in the engine, its member of
`ClassFunctions`, read only when the module's `StructSize` covers it; dispatch it from the system that raises it; test
it, with a module that lacks it. Each section ends with its patch's checkpoint and the test output as a text capture.
Every step is a code change, a build or a test run from a terminal; no step needs an editor command. Exercises: a second
host function of the reader's choice (a `Game::GetLanguage`), and the WindZone's `ReportProblem` cases. At the end the
reader has a patch that keeps `ST_SCRIPT_ABI_VERSION` at 1 and passes `Architecture.Layering`, `Physics.WindZone`, the
new tests and the feature test.

**Leaves out.**

- The WindZone component and its system → `world/tutorial-component`
- The WindZone's gizmo, the exercise whose solution this page starts from → `gpu/debug-drawing`
- Scene services in general and where each is implemented → `world/systems`
- The rules and guards of host functions → `scripting/host-api`
- The feature test in full → `engineering/feature-test`
- The `wind.*` commands → `editor/tutorial-command`
- Forces on bodies and the WindZone as a whole feature → `capstone/build`

**Fit.** `fits`: about 5,300 words against L (5,000). Two changes end to end, about 16 steps with their build or test
output and eight short model excerpts take the most words, the scene service's step of D38 the longest.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `scripting:534` | hands-on | home | Add a host function end to end: the ABI, the implementation, the X-macro (the `static_assert` failing first), the SDK wrapper, the API module, a `Scripting.*` test, a feature script |
| `scripting:538` | hands-on | home | Add a callback: the descriptor, `ScriptCallback`, `CallbackFlag`, `ClassFunctions` with `ST_SCRIPT_HAS_MEMBER`, a thunk, the dispatch |
| `gamedev:558` | hands-on | home | The page's "make it yours" exercise: a second host function (`Game::GetLanguage`) added the same way |
| `animation:508` | hands-on | home | A harder exercise: a new `IAnimatorControl` query (`GetStateDuration`) end to end, through the scene service, the system, the host function, the SDK, a `Scripting.*` test and a feature script |
| `scripting:345` | concept | use | The feature test's coverage of host functions, SDK functions and callbacks, applied in the feature-script step: two sentences say what the reader adds and link forward to `engineering/feature-test`, the concept's home |
| `scripting:496` | rule | use | Every new host function, SDK function, callback and field type is exercised by the feature test, applied in the feature-script step; the rule box is on `engineering/feature-test` |
| `new:11` | code | home | `StrataScriptCore/Include/StrataScript/ScriptABI.h:739-755`: the newest group with its "check `ST_SCRIPT_HAS_MEMBER` before use" comment, and the line where new functions are appended |
| `new:12` | code | home | `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3378-3386`: `HostGetStepAlpha`, the model of a small host function and its failure value |
| `new:13` | code | home | `StrataScriptCore/Include/StrataScript/Time.h:70-76`: the SDK's wrapper with `ST_SCRIPT_DETAIL_HOST_WITH` and its fallback value |
| `new:14` | code | home | `StrataTests/Scripts/API/TransformScripts.cpp:93-116`: the API module checks what an older engine gives (a table cut before the function, and null entries) |
| `new:15` | code | home | `StrataTests/src/Scripting/ScriptAPITests.cpp:231-266`: the `Scripting.API` test case of the newest group |
| `new:16` | code | home | `Strata/src/Strata/Scripting/ScriptModule.cpp:998-1016`: appended callbacks read only when the module's descriptor holds them |
| `new:17` | code | home | `Strata/src/Strata/Scripting/ScriptTypes.h:16-41`: `ScriptCallback` and `c_ScriptCallbackCount`, defined from the last value |
| `new:19` | code | home | `Strata/src/Strata/Scene/SceneServices.h:19-33`: the contract of scene services (a system registers its interface while it exists, others look it up and get null when no system offers it), the model of the WindZone's service (R32, D38); with `Strata/src/Strata/Physics/PhysicsSystem.cpp:58-80` (services registered in the constructor and unregistered in the destructor) and `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:1176-1180` (a host function's lookup) |
| `scripting:450` | rule | use | Append, never insert: the reason the reader appends at both ends |
| `scripting:452` | rule | use | `ST_SCRIPT_HAS_MEMBER` before an appended function or callback |
| `scripting:459` | rule | use | `HostCall` and `ResolveContext` in the new function |
| `scripting:201` | feature | use | The layer rule of Scripting, which is why the WindZone needs a scene service: Physics is no layer that Scripting may include |
| `scripting:377` | code | use | The X-macro table and its check, whose end the reader extends (`ScriptHostAPI.cpp:3594-3596`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source; one test case written and run | `core/first-change` | must |
| The WindZone component and its system; the feature test's minimum | `world/tutorial-component` | must |
| `HostCall`, `ResolveContext`, `ReportProblem`, the X-macro table and its `static_assert` | `scripting/host-api` | must |
| `ST_SCRIPT_HAS_MEMBER`, `StructSize`, append-only structs, the SDK's thunks and callback flags | `scripting/abi-sdk` | must |
| Dispatch lists and the order of callbacks | `scripting/script-system` | must |
| Scene services | `world/systems` | must |
| The layer table and dependency inversion | `core/layers-registries` | must |
| The feature test's coverage checks | `engineering/feature-test` | helps |
| A patch and git | `basics/git` | helps |
| The WindZone's gizmo, the solution of `gpu/debug-drawing`'s exercise | `gpu/debug-drawing` | helps |

**Starting state.** The source build of `core/first-change` at the pin with the WindZone chain applied up to the
solution of `gpu/debug-drawing`'s exercise: the tutorial file's `startsFrom` is `{"tutorial": "gpu/debug-drawing",
"exercise": <n>}` (R41; `pipelines.md` §6), so the runner replays `gpu/debug-drawing`, which starts from
`world/tutorial-component`, and applies its `exercise-<n>.patch`, the one that gives the WindZone its gizmo. The
WindZone component and its system are registered, the zone draws its gizmo, and its serialization round trip and the
feature test's minimum pass (`Physics.WindZone`). A reader who skipped the exercise applies its solution patch. No
project or editor checkpoint is used.

**Command-only steps.** none

## Passed on

| Item | Type | To | Why |
| --- | --- | --- | --- |
| `scripting:118-121` | feature | `make/scripting-scene` | `Entity`, the `Component` proxy, `TransformComponent`, `Scene`, `Assets` and `SubScene` have no engine twin; that page teaches them as scripts use them (R31, D26; R46); `reference/script-api` links them |
| `scripting:122` | feature | `input/devices-state` | `Input`, one entry with its twin `audio-input:173` on the page that teaches it (R31, D26); `reference/script-api` links it |
| `scripting:123` | feature | `make/timers-events` | `Time`, taught there beside `gameui:208` (R31, D26); `reference/script-api` links it |
| `scripting:124` | feature | `basics/programming-1` | `Log`, the reader's first call into the SDK (R31, D26; R46); `reference/script-api` links it |
| `scripting:125-126` | feature | `physics/world-step` | `RigidBody`, `Physics`, `RaycastHit`, `Collision`, `CharacterController` and `GroundState`, one entry with their twin `physics:177` (R31, D26); `physics/character-controllers` uses the controller |
| `scripting:127` | feature | `audio/scene-system` | `AudioSource` and `Audio`, one entry with their twins `audio-input:94-95` (R31, D26) |
| `scripting:128` | feature | `make/animation` | `Animator` and `JointTransform`, one entry with their twin `animation:177` (R31, D26) |
| `scripting:129` | feature | `make/levels-saves` | `Game` and `WindowMode`: quitting, scene switches and save files are taught there (R31, D26; R46) |
| `scripting:130` | feature | `image/quality-settings` | `book.md` makes that page the home of players' graphics options, the SDK's `Graphics` named in it |
| `scripting:131` | feature | `ui/input` | `UIElement`, `UI` and `UIAction`, one entry with their twin `gameui:206` on the page of the script bridge (R31, D26) |
| `scripting:132` | feature | `worlds/physics-scripts` | Its From names the SDK's `World` and prefetch before a teleport |
| `scripting:133` | feature | `make/recipes` | `Random`, taught there with seeds and the replay (R31, D26; R46); `scripting/abi-sdk` says why it lives in the module |
| `scripting:134-135` | feature | `make/timers-events` | `Timer` and `KeyRepeat`, beside `gameui:208`; `KeyRepeat` is one entry with its twins `gamedev:146` and `audio-input:174` (R31, D26); `scripting/abi-sdk` says why they live in the module |
| `scripting:136` | feature | `make/gameplay-math` | `Motion`, one entry with its twin `gameui:207` (R31, D26); `scripting/abi-sdk` says why it lives in the module |
| `scripting:145` | feature | `make/script-builds` | `book.md` makes it the home of building script modules outside the editor, the package included |
| `scripting:147` | feature | `editor/script-builds` | The editor's build pipeline, which that page reads at the pin |
| `scripting:197` | feature | `editor/script-builds` | The editor's script engine: one per project, hot reload on, Play builds first (the Developer Guide's "The editor's script engine") |
| `scripting:198` | feature | `worlds/runtime` | A shipped game's script engine is part of `GameRuntime`, whose home that page is |
| `scripting:205` | feature | `editor/script-builds` | The `script.*` commands are the editor's; that page is their center, and `reference/commands` lists them |
| `scripting:208` | feature | `make/first-script` | The Scripts menu, New Script, the Script drawer, the Problems panel and the pills are the game maker's first script |
| `scripting:212` | feature | `worlds/export` | The module and its PDB in the exported folder are the export's |
| `scripting:289` | concept | `make/script-loop` | `book.md` makes it the home of the script lifecycle and its callbacks; `scripting/script-system` names them for track E |
| `scripting:341` | concept | `world/interpolation` | Interpolation of fixed-step motion is that page's (the item comes from the scene area); `make/characters-cameras` is its use home |
| `scripting:343` | concept | `make/recipes` | That page teaches determinism with seeds and the replay (`scripting:527`); `basics/math-probability`, `make/timers-events` and `make/gameplay-math` use its parts, and `scripting/abi-sdk` links it (critic-scripting-5) |
| `scripting:345` | concept | `engineering/feature-test` | Testing the API is taught there, one entry with the build-test items; `scripting/tutorial-host-function` applies it and links forward (critic-scripting-18) |
| `scripting:383` | code | `basics/math-probability` | Its From names the SDK's `Random` as its PCG32 example: an algorithm a reader can check by hand |
| `scripting:385` | code | `make/recipes` | Its From names the `Coin` recipe; `scripting/script-system`, `scripting/hot-reload` and `scripting/crash-containment` use it as their example |
| `scripting:386` | code | `nowhere` | Repeats `gamedev:378` (the same lines of `FollowCamera.cpp`), which the router passed to `make/characters-cameras` |
| `scripting:387` | code | `nowhere` | Repeats `gamedev:360` (the New Script template of `Docs/Manual/Scripting.md`), passed to `make/first-script` |
| `scripting:426` | figure | `editor/script-builds` | The editor's loop of edit, build, load, Play and Problems is that page's subject |
| `scripting:431` | figure | `nowhere` | Repeats `gamedev:449` (the New Script dialog and the file in the code editor), passed to `make/first-script` |
| `scripting:432` | figure | `make/script-fields` | Fields of every type in the Inspector are taught there |
| `scripting:433` | figure | `nowhere` | Repeats `gamedev:445` (the Content Browser's Scripts root), passed to `make/assets` |
| `scripting:434` | figure | `editor/script-builds` | The pills show the states of the editor's builds |
| `scripting:440` | figure | `nowhere` | Repeats `gamedev:453` (the External Editor page with the editors found), passed to `make/first-script` |
| `scripting:442` | figure | `make/menus` | The settings screen and the rebinding row are built there |
| `scripting:496` | rule | `engineering/feature-test` | One rule box with the build-test items on the page of the feature test; `scripting/tutorial-host-function` applies it (critic-scripting-18) |
| `scripting:509` | hands-on | `make/first-script` | Hello script is the first script |
| `scripting:513` | hands-on | `make/hud` | A pickup with a score, a sound and an early request ends in the HUD's coin count |
| `scripting:515` | hands-on | `make/script-fields` | A spawner with a prefab field, `Instantiate` by handle and "not loaded yet" |
| `scripting:517` | hands-on | `make/characters-cameras` | A character with actions and a follow camera in `OnLateUpdate` |
| `scripting:520` | hands-on | `make/menus` | The pause and settings menu is built there |
| `scripting:523` | hands-on | `make/levels-saves` | Save files are taught there |
| `scripting:527` | hands-on | `make/recipes` | `Random` and seeds are taught there |
| `scripting:565` | term | `assets/residency` | `AssetPin` is one class: one glossary entry with `assets:683` (`proposals/duplicates.md`, "`AssetPin`"; critic-assets-12); `scripting/script-system` links it |
| `scripting:566` | term | `input/rebinding` | `book.md` makes it the home of binding capture |
| `scripting:570` | term | `make/script-loop` | The script meaning of "callback" belongs to the home of the lifecycle and its callbacks |
| `scripting:578` | term | `core/first-change` | Dist is homed there, one entry with `foundation:612` (R31, D33); `engineering/building` teaches every configuration and links the entry |
| `scripting:579` | term | `world/interpolation` | Drawn transforms are that page's |
| `scripting:580` | term | `core/engine-modules` | `book.md` makes it the home of engine services |
| `scripting:583` | term | `engineering/feature-test` | The home of the feature test |
| `scripting:584` | term | `make/first-script` | `book.md` makes it the home of `ST_SCRIPT_FIELD` |
| `scripting:587` | term | `make/script-loop` | It is the use home of frame and fixed updates |
| `scripting:600` | term | `basics/math-probability` | The PCG32 excerpt goes there |
| `scripting:606` | term | `world/systems` | `book.md` makes it the home of scene services |
| `scripting:609` | term | `core/platform` | Signals are taught there first; `scripting/crash-containment` uses the fault signals |
| `scripting:617` | term | `core/time` | `book.md` makes it the home of time scale |
| `scripting:618` | term | `physics/contacts-triggers` | Triggers are taught there |
| `scripting:673` | open | `nowhere` | A note of the survey about files it did not read line by line; the writers of `scripting/host-api`, `scripting/script-system`, `scripting/crash-containment` and `scripting/symbolization` read them at the pin |
| `scripting:679` | open | `nowhere` | A note of the survey about SDK headers read by outline; `reference/script-api` is generated from them |
| `scripting:682` | open | `nowhere` | A note of the survey: the editor's side belongs to the editor's area, and `editor/script-builds` reads its files at the pin |
| `scripting:685` | open | `worlds/runtime` | `GameRuntime`'s script handling, which that page reads at the pin |
| `scripting:686` | open | `nowhere` | A note of the survey: tests read by name; each page's "How it is tested" reads its suites at the pin |
| `scripting:691` | open | `engineering/feature-test` | The feature test's runner and SDK reader, which that page explains |
| `scripting:693` | open | `core/layers-registries` | That page says that a build without scripting is not offered (`book.md`, "What Strata does not do") |
| `scripting:694` | open | `nowhere` | Repeats the erratum that `scripting/symbolization` holds as `new:6`, which `process.md`'s table settled |

## Not taken

none

## Questions for the planner

none
