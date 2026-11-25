# Brief: `basics/computer`

| Field | Value |
| --- | --- |
| Title | How a computer runs a program: CPU, memory, caches and processes |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `start/first-game` |
| From | new; the CPU, memory, the stack and the heap as places in memory, caches and why the order of data in memory matters, SIMD in one section; processes: process id, environment, child processes; its exercises are editor tasks (track B reads it before any programming); threads are `basics/threads`' (foundation concept 16), job systems `core/jobs`' (foundation concept 17), allocators and the stack and the heap in code `basics/cpp-memory`', arrays of structs and sparse sets `basics/data-structures`', exit codes and the standard streams `basics/tools`' |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/computer` — How a computer runs a program: CPU, memory, caches and processes

**Covers.** The page is read on track B right after `make/lighting`, before any programming, so it teaches with
pictures, numbers and the editor, never with code. In order: a program is a list of machine instructions kept in a
file, and running it means that the processor does them one after another, billions of times a second (machine
instruction, machine code, processor, clock rate). Memory is a long row of numbered bytes; a memory address finds one
byte the way a house number finds a house; storage keeps data while the computer is off, memory only while it runs.
A processor holds several cores, and a core can run two lines of instructions at once (hardware threads, which the
operating system shows as "logical processors"); one paragraph says that some processors mix two kinds of cores and
links `core/platform`. Memory is far slower than the processor, so the processor keeps copies of recent data in small
caches, in levels, and copies memory in cache lines of 64 bytes; a figure with a table of rough waiting times (a
register, each cache level, memory) shows why reading data in the order it lies in memory is fast and jumping around
is slow (caches and why the order of data in memory matters). Code is data in memory too, read through its own cache,
so where code lands can change a measurement a little (the place of code in memory, for `engineering/perf-lab`).
Processors speak an instruction set (x64, ARM) with extensions such as SSE 4.2 and AVX2; a program built for newer
instructions does not start on an older processor; SIMD in one section: one instruction that adds four or eight
numbers at once. One paragraph names the GPU as a second processor with its own memory, made for drawing, which works
at the same time as the CPU (its frame is `gpu/how-a-gpu-frame-works`'). Then the operating system: it starts
programs, gives each one its own memory and shares the cores between them. A process is a running program, with its
own memory, a process id, an environment of named texts that it passes to the processes it starts (child processes),
and an exit code when it ends (exit codes and setting environment variables are `basics/tools`'). The editor is the
example: building the scripts with **Ctrl+B** starts CMake as a child process, which starts the compiler, and the
editor's log shows the command line it ran. Last, a process's memory has regions: its code, its fixed data, the stack
for the short-lived data of the steps in progress (a pile of plates: the last put on is the first taken off) and the
heap for data of any size kept as long as it is needed. The exercises are editor and system tasks: find the editor's
process, its id, memory and threads in the Task Manager (Activity Monitor, System Monitor), press **Ctrl+B** and watch
CMake and the compiler appear under it, watch the logical processors' graphs while a scene plays.

**Leaves out.**

- Threads that a program starts, races and locks → `basics/threads`
- Strata's job system and its pools → `core/jobs`
- The stack and the heap in code, allocators → `basics/cpp-memory`
- The call stack and stack frames as a debugger shows them → `basics/debugging`
- Arrays of structs against structs of arrays, sparse sets → `basics/data-structures`
- Exit codes, the standard streams and setting environment variables → `basics/tools`
- Binary numbers, and what a byte can hold → `basics/numbers`
- How source code becomes machine code → `basics/build`
- What the GPU does with a frame → `gpu/how-a-gpu-frame-works`
- Priorities and the two kinds of cores in Strata → `core/platform`

**Fit.** `fits`: about 5,100 words against L (5,000). Twelve ideas from zero at B0's length with the cache figure and
its table (about 4,150), the three exercises in the editor and the system's tools (about 350) and the fixed parts
(about 600), no code; caches and the order of data, processes and the regions of memory take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | concept | home | A program as a list of machine instructions kept in a file; machine code. General knowledge. |
| `new:2` | concept | home | The processor runs instructions one after another, billions a second; the clock rate. General knowledge. |
| `new:3` | concept | home | Memory as numbered bytes, a memory address, and storage that keeps data while the computer is off. General knowledge. |
| `new:4` | concept | home | Processor cores and hardware threads (logical processors); processors with two kinds of cores named. General knowledge. |
| `new:5` | concept | home | Memory is slow next to the processor: CPU caches in levels, cache lines of 64 bytes, rough waiting times. General knowledge. |
| `new:6` | concept | home | Caches and why the order of data in memory matters: reading in order against jumping around, with a figure. General knowledge. |
| `new:7` | concept | home | Code lives in memory too and is read through its own cache, so the place of code can change a measurement. General knowledge. |
| `new:8` | concept | home | Instruction sets (x64, ARM) and their extensions (SSE 4.2, AVX2); a program built for newer instructions on an older processor. General knowledge. |
| `new:9` | concept | home | SIMD: one instruction on four or eight numbers at once. General knowledge. |
| `new:10` | concept | home | The GPU as a second processor with its own memory, working at the same time as the CPU, in one paragraph. General knowledge. |
| `new:11` | concept | home | The operating system starts programs, gives each its own memory and shares the cores between them. General knowledge. |
| `new:12` | concept | home | A process: its own memory, a process id, an environment it passes to its child processes, an exit code at its end. General knowledge. |
| `new:13` | concept | home | The editor's script build as the example of a child process: **Ctrl+B** runs `cmake --build <folder> --parallel`, which runs the compilers, and the log line `[Scripts] > cmake ...` shows the command. Evidence: `StrataEditor/src/Editor/ScriptBuild.cpp:451-460`, `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153` |
| `new:14` | concept | home | The regions of a process's memory: code, fixed data, the stack (a pile of plates) and the heap. General knowledge. |
| `new:15` | hands-on | home | Exercises in the system's process viewer: the editor's process, id, memory and threads; CMake and the compiler under it during a build; the logical processors' graphs while a scene plays. Evidence: `StrataEditor/src/Editor/ScriptBuild.cpp:1125-1153` |
| `automation:714` | term | home | Process: a running program with its own memory, named by a process id |
| `foundation:208` | concept | use | What a program is, its process and an executable, the general half; Strata's programs are `core/map`'s |
| `scripting:147` | feature | use | The editor's build pipeline, named only as the program that starts CMake |
| `foundation:128` | feature | link | Strata's `Process`, which starts the script builds' child processes, linked to `core/platform` |
| `foundation:300` | concept | link | Scheduling, priorities and two kinds of cores, linked to `core/platform` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building the scripts with **Ctrl+B**, pressing **Play**, and the Console | `start/first-game` | must |
| One frame, and the CPU preparing a frame while the GPU draws the one before | `start/what-an-engine-is` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `byte` | byte | - |
| `cache-line` | cache line | - |
| `cpu-cache` | CPU cache | processor cache |
| `heap` | heap | - |
| `machine-code` | machine code | - |
| `machine-instruction` | machine instruction | processor instruction |
| `memory` | memory | RAM, main memory |
| `memory-address` | memory address | - |
| `process` | process | - |
| `processor` | processor | CPU, central processing unit |
| `processor-core` | processor core | CPU core |
| `program` | program | - |
| `simd` | SIMD | single instruction, multiple data |
| `stack` | stack | - |
| `storage` | storage | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-21 | should | shape | `basics/computer`, `basics/tools`, `basics/git`, `basics/data-structures`, `basics/trees-graphs`, `basics/bytes`, `basics/data-formats` | A primer has a "Common mistakes" section: each mistake, its symptom and its fix. These seven pages list none: no Covers, row or Fit line of theirs names a mistake, while the other eleven pages of the unit do. | Each page's Covers names three or four mistakes with their symptoms (about 250 words a page). For example: tools, a path with a space not quoted, a program run from the wrong folder, Ctrl+C taken for copy; git, a commit without `git add`, conflict markers left in a file, build output committed (the editor's `.gitignore` keeps `.strata/` out); data-structures, an index kept across a swap-remove, a hash map's order relied on; trees-graphs, a recursive walk of a deep tree that overflows the stack, a graph walk without a visited set; bytes, a length read from a file and used unbounded, UTF-8 cut by bytes; data-formats, a float written with too few digits, `std::hash` stored in a file, a trailing comma in JSON; computer, memory taken for storage, more cores taken for a faster single task. | `style.md:476`; `allocation/basics-a.md:5-46`, `:82-120`, `:459-485`, `:607-639`, `:677-701`, `:1088-1114`, `:1152-1186`; `Strata/src/Strata/Project/Project.cpp:198-199` |
| critic-basics-a-24 | could | stale-item | `basics/computer` (`new:4`, `new:5`, `new:8`, `new:15`) | Three sentences are not true of every computer the book supports, and one exercise may show nothing. Apple silicon runs one line of instructions per core and reports cache lines of 128 bytes, not 64. A program built for newer instructions does start on an older processor and stops with an illegal instruction where it first uses one (critic-build-test-5 found this for Strata's AVX2 builds). And a Ctrl+B with nothing changed starts CMake but no compiler, so "watch CMake and the compiler appear" needs a changed script file first, and the build lasts about a second. | Say "two lines on many x64 processors", "64 bytes on x64, 128 on Apple silicon" and "stops at the first such instruction"; the exercise changes one character of a comment before Ctrl+B and also reads the command lines in the Console (about 60 words). | `allocation/basics-a.md:10-13`, `:17-18`, `:27-29`, `:66`; `CMake/StrataCompilerOptions.cmake:51`, `:62`; `allocation/completeness.md:132`; the line size and the absence of two hardware threads per core on Apple silicon are general knowledge, not at the pin |
| critic-basics-a-27 | could | missing-item | `basics/programming-2` (`new:47`) | An endless loop freezes the editor and "the editor must be closed", but a frozen window does not close from its own button. Track G reads this page without `basics/computer`, which teaches the system's process viewer. | One sentence per OS: Task Manager's End task, Force Quit (Cmd+Option+Esc), the System Monitor's End Process or `kill` (about 50 words). | `allocation/basics-a.md:234-237`, `:272`; `tracks.md:77-85`; `style.md:41-44` |
| critic-basics-a-28 | could | duplicate | `basics/debugging` (`new:76`) | `new:76` is a second home of "a process", which `new:12` homes on `basics/computer` with its glossary term (`automation:714`). By the rule for a page whose Needs closure lacks the home, `basics/debugging` explains the word in a paragraph and links the home. | Split `new:76`: "what a debugger is" stays `home`; "a process in one paragraph" becomes a `use` row of `new:12` with the link. No words change. | `allocation/basics-a.md:63`, `:67`, `:390`, `:428`; `allocation/README.md:243-246` |
