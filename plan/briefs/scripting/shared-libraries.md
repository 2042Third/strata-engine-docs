# Brief: `scripting/shared-libraries`

| Field | Value |
| --- | --- |
| Title | Shared libraries and binary interfaces |
| Kind | C |
| Size | L |
| Tracks | E |
| Needs | `basics/build`, `basics/cpp-classes`, `scripting/why-scripts` |
| From | scripting ch. 9 "Shared libraries and binary interfaces"; home of shared libraries and ABIs |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `abi` | ABI | application binary interface |
| `append-only` | Append-only | - |
| `crt` | CRT | C runtime |
| `entry-point-scripting` | Entry point (scripting) | - |
| `interposition` | Interposition | - |
| `runpath` | RUNPATH | - |
