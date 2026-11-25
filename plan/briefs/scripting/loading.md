# Brief: `scripting/loading`

| Field | Value |
| --- | --- |
| Title | Loading, calling and validating modules |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `scripting/abi-sdk`, `core/platform`, `core/files` |
| From | scripting ch. 11 (`ScriptModule`, load modes and copies, validation, `Call`, `ScriptEngine`, the active engine) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `abandoned-library-file` | Abandoned library/file | - |
| `active-engine` | Active engine | - |
| `call-site` | Call site | - |
| `private-copy` | Private copy | - |
