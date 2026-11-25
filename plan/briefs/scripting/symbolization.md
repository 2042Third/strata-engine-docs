# Brief: `scripting/symbolization`

| Field | Value |
| --- | --- |
| Title | From an address to a file and line |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `scripting/crash-containment` |
| From | scripting ch. 12, the symbolization half (concept 13, code #21: DbgHelp with inline frames, ELF `.symtab`, `dladdr`, the choice of the fault frame) |
| Unit | `plan/allocation/scripting.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

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

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `dbghelp` | DbgHelp | - |
| `inline-frame` | inline frame | - |
| `inlining` | Inlining | - |
| `pdb` | PDB | - |
| `symbolization` | Symbolization | - |
