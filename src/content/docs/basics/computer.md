---
id: basics/computer
title: "How a computer runs a program: CPU, memory, caches and processes"
description: "Learn how a processor runs a program from memory, why the order of data matters, what SIMD is, and what a process, the stack and the heap are."
kind: primer
size: L
tracks: [B, E]
needs: [start/first-game]
time: 60
learn:
  - id: run-program
    text: explain how a processor runs a program that is kept in a file and copied into memory
  - id: cache-order
    text: predict why reading data in the order it lies in memory is faster than jumping around
  - id: simd
    text: explain what SIMD does and why a program built for newer instructions can fail on an older processor
  - id: process-viewer
    text: find a running program's process id, memory and child processes in the system's process viewer
  - id: regions
    text: name the four regions of a process's memory and say what each one holds
status: final
---

::::test-out

1. Your game is a file on your drive. Where is the list of instructions that the file holds while the game plays?

   :::answer{tests="run-program"}
   In memory. The operating system copies the instructions from the file, which stays on the drive, into memory, and
   the processor reads them from there.
   :::

2. A cache line is 64 bytes. A list of 1,000 numbers of 4 bytes lies in a row, and a program adds them in order. About
   how many cache lines does the processor load from memory?

   :::answer{tests="cache-order"}
   About 63. The list holds 1,000 times 4, which is 4,000 bytes, and 4,000 divided by 64 is 62.5, rounded up. Each line
   serves 16 numbers, so only one read in 16 waits for memory.
   :::

3. One instruction can add 8 numbers at once. How many such instructions add two lists of 800 numbers, pair by pair?

   :::answer{tests="simd"}
   100, because 800 divided by 8 is 100. Adding one pair at a time takes 800 instructions.
   :::

4. A game keeps three things. The first is the text "Game Over" that its code contains. The second is the count of loop turns left in the step it does now. The third is a list of 50,000 objects that lives as long as the level. Which region of its memory holds each?

   :::answer{tests="regions"}
   The text is fixed data, the count is on the stack, and the list is on the heap. The stack holds the short-lived data
   of steps in progress, and the heap holds data kept as long as it is needed.
   :::

5. The editor has process id 4120 and starts CMake. What does CMake have that it does not share with the editor?

   :::answer{tests="process-viewer"}
   Its own process id, its own memory and its own exit code at its end. It also gets a copy of the editor's
   environment, which is what a child process receives.
   :::

::::

## Why you will need this

You have built and played a game. This page explains what the computer did while you played. Your game's instructions waited in one place, another part of the machine ran them, and the order of the data decided how fast that went.

Four later pages build on it. [Threads, atomics and races](threads.md) needs the cores and the hardware threads of this page. [C++ memory](cpp-memory.md) writes the stack and the heap in code, [Numbers in a computer](numbers.md) opens up the byte, and [How a C++ program is built](build.md) starts from the machine code. Every page about speed uses the picture of the processor and its memory that you build here.

There is no code in this page. You use pictures, numbers worked by hand, and the system's own tools: the process viewer
of your computer and the **Console** of the editor.

## A program is a list of instructions in a file

A **program** is a list of instructions for the computer, kept in a file, that a person starts to do something useful.
Your game, the editor and the compiler that builds your scripts are programs. A program file does nothing while it
lies on the drive, as a recipe cooks nothing on its shelf.

Each step in the list is a **machine instruction**: one very small order, such as add two numbers, copy a number, compare two numbers or jump to another step of the list. An instruction does little: a single line of a game, such as "move the cube", needs many of them.

The **processor**, also called the central processing unit (CPU), is the chip that does the instructions of every program on the computer.

The instructions are numbers. The whole list, as the processor reads it, is **machine code**: the numbers that the
processor takes as instructions. A person does not write machine code by hand. Another program, the compiler, makes it
from the text a person writes, and [How a C++ program is built](build.md) tells that story.

Running a program means that the processor does its instructions one after another. The processor has a clock that
ticks at a fixed rate, the **clock rate**, and a simple instruction takes about one tick. A processor of 4 billion ticks
a second does 4 billion simple instructions a second. That is why a computer seems to do many things at once: each one
is a very long list, done very fast.

:::example[How many ticks fit in one frame?]
Your game draws 60 frames a second, so a frame lasts 1,000 ms divided by 60, which is 16.7 ms. A processor with 4
billion ticks a second does 4 ticks in each nanosecond, and 16.7 ms is 16,700,000 ns. So one frame holds 16,700,000
times 4, which is 66.8 million ticks.

For the game to hold 60 frames a second, all its work for a frame must fit in about 67 million ticks on each core that
helps. That is a lot, but it is not unlimited, and the rest of this page shows how ticks are lost to waiting.
:::

Try it: a processor does 3 billion ticks a second. How many ticks are in 1 ms?

:::answer
3 million. A second holds 1,000 ms, and 3,000,000,000 divided by 1,000 is 3,000,000.
:::

## Memory is a row of numbered bytes

The processor must keep the instructions and the numbers it works on somewhere. That place is **memory**, also called
random access memory (RAM) or main memory: the part of the computer that holds the data of the programs that run now.

Picture a very long row of boxes. Each box holds one **byte**, a small whole number from 0 to 255, and the boxes are
numbered from 0 up: 0, 1, 2 and so on, for billions of boxes.

The number of a box is its **memory address**. An address finds one byte in the way a house number finds one house in
a street. A number that needs more than one byte, such as a number of 4 bytes, takes four boxes in a row, and its
address is the address of its first box. [Numbers in a computer](numbers.md) explains how bytes make numbers, letters
and colours; this page only needs the idea that every piece of data has an address.

Memory loses its content when the computer is switched off. **Storage**, the drive of your computer, keeps its content
without power: it holds your files, your projects and the program files. A program must therefore be copied from
storage into memory before the processor can run it. When you start the editor, part of the wait is this copy of the
engine from storage into memory.

The sizes differ a lot. A typical computer today has 16 to 64 GB of memory and 500 GB or more of storage. Memory is
many times faster than storage, and that is the reason it exists: storage is the big shelf, memory is the desk.

## Cores and hardware threads

Old processors did one list of instructions at a time. A modern processor holds several **processor cores**, each of
which is a complete small processor that does its own list of instructions, at the same time as the others. A chip with
8 cores can run 8 lists at once, and the lists need not have anything to do with one another.

Many x64 processors give each core two **hardware threads**: the core keeps two lists in progress and uses the time that
one list spends waiting to work on the other. The :term[operating system]{id=operating-system} shows each hardware thread as a **logical
processor**. A chip with 8 cores and two hardware threads each shows 16 logical processors in the system's tools. Two
hardware threads on one core do not give twice the speed; they give less, because they share the core. Apple's
processors give each core one hardware thread, so their number of logical processors equals the number of cores.

Some processors mix two kinds of cores: fast cores for hard work and small cores that use little power for light work. The
operating system chooses which core runs which list. [Platform, scheduling and priorities](../core/platform.md)
explains how Strata deals with it. Making a program use several cores is [Threads, atomics and
races](threads.md)' subject.

One more processor sits in your computer. The :term[graphics processing unit]{id=gpu} (GPU) is a second processor, with its own
memory, made for drawing pictures. The CPU prepares a frame and the GPU draws the one before at the same time.
[How a GPU frame works](../gpu/how-a-gpu-frame-works.md) explains what the GPU does with a frame.

## Memory is slow, so the processor keeps copies

A processor does a simple instruction in one tick, but reading a number from memory takes about 80 ns, which is 320
ticks at 4 billion ticks a second. The processor would wait most of the time if it went to memory for every number.

:::example[What waiting costs in a frame]
A game must read 100,000 numbers from memory, and each read waits the full 80 ns. The total is 100,000 times 80 ns,
which is 8,000,000 ns, 8 ms. A frame at 60 frames a second lasts 16.7 ms, so 8 ms is 48 % of it, spent doing nothing
but waiting.
:::

The fix is a **CPU cache**: a small, fast memory inside the processor that keeps copies of recently used data. The next read of the same data then does not wait for memory.

A processor has several caches in levels.
The first, called L1, is the smallest and the fastest, and each core has its own. L2 is larger and slower, and L3 is
larger again and shared by the cores. Next to the caches the processor has **registers**: a few dozen places inside a
core where the numbers wait that an instruction works on right now.

```mermaid caption="From a core down to memory: each level holds more and takes longer to read." alt="A vertical chain of five boxes joined by arrows. From top to bottom: the registers of a core, the first level cache, the second level cache, the third level cache shared by the cores, and memory."
flowchart TB
    R["Registers of a core"] --> L1["Level 1 cache"]
    L1 --> L2["Level 2 cache"]
    L2 --> L3["Level 3 cache, shared by the cores"]
    L3 --> M["Memory"]
```

The table gives rough times for a desktop computer. The numbers differ from chip to chip and are meant to show the
size of the steps, not to be exact.

| Place | Size | Time to read | Ticks at 4 billion a second |
| --- | --- | --- | --- |
| Register | a few hundred bytes | under 1 ns | 1 or less |
| L1 cache | 32 to 64 KB per core | 1 ns | 4 |
| L2 cache | 0.5 to 2 MB per core | 4 ns | 16 |
| L3 cache | 8 to 64 MB for all cores | 15 ns | 60 |
| Memory | 16 to 64 GB | 80 ns | 320 |
| Storage (a solid-state drive) | 500 GB or more | 100,000 ns | 400,000 |

Each step down is slower by a factor of about 4 to 20, and storage is slower than memory by a factor of more than a
thousand. A program that finds its data in L1 runs 80 times faster, on that read, than one that waits for memory.

The cache does not copy single bytes. It copies a **cache line**: a block of 64 bytes on x64 processors that memory
gives to the cache in one step. Apple's processors use 128 bytes. When the processor reads one byte, the cache loads
the whole line around it, and the neighbours come free.

:::note
A line starts at an address that is a multiple of 64. The line from 960 to 1,023 holds the bytes with these addresses
and no others. Reading the byte at address 1,000 loads all of them, and the next byte, 1,001, is already in the cache.
:::

## Reading in order is fast, jumping around is slow

The cache line explains why the order of data matters. If a program reads numbers that lie next to one another, the
first read of a line waits for memory and the next reads find the rest of the line in the cache. If it reads numbers
far apart, each read may load a new line and use only a few bytes of it.

:::example[Two ways through 16 million numbers]
A list holds 16,000,000 numbers of 4 bytes each, 64 MB in all, far more than any cache holds. The program adds them up
and reads each number once.

1. In order: each 64-byte line holds 16 numbers. The list needs 64,000,000 divided by 64, which is 1,000,000 lines.
   Each load waits 80 ns, so the pass takes 1,000,000 times 80 ns, which is 80 ms.
2. Jumping around: the program visits the same numbers in a shuffled order, and each read lands in a line that left the
   cache since the last visit. It loads 16,000,000 lines, one for each number, and takes 16,000,000 times 80 ns, which
   is 1,280 ms, 1.28 s.

Both do the same additions, but the second is 16 times slower, and the factor 16 is the number of numbers in a line.
:::

Real processors are even kinder to the first way. They notice that the program reads in order and load the next lines
before the program asks for them, so most of the waiting disappears. The shuffled way gives them nothing to guess. The
estimate of the example therefore shows a smaller gap than the real one.

Try it: a list holds 4,000,000 numbers of 8 bytes each, and a program reads them in order. How many cache lines of 64
bytes does it load, and how long does the pass take if each load waits 80 ns?

:::answer
A line holds 64 divided by 8, which is 8 numbers, so the list needs 4,000,000 divided by 8, which is 500,000 lines. The
pass takes 500,000 times 80 ns, which is 40,000,000 ns, 40 ms.
:::

The rule that follows is plain: keep the data that a loop uses together, in one row, in the order the loop reads it.
A game holds thousands of objects, and how their data lies in memory can matter more for speed than how clever the code
is. [Data structures](data-structures.md) shows how programs arrange their data for this.

## Code is in memory too

The processor reads data from memory, and it reads instructions from memory in the same way. Instructions are bytes at
addresses, and the processor keeps recent ones in a cache of their own, so a loop that runs many times is read from
memory once.

The place where the code lands in memory can therefore change a measurement a little. Two builds of the same program
may put the same function at different addresses, share cache lines differently, and run a few percent apart without
any change to the function. A person who measures speed must expect such small differences and measure more than once;
[the performance lab](../engineering/perf-lab.md) shows how.

## Instruction sets and SIMD

Processors do not all understand the same instructions. A processor speaks an instruction set: the list of instructions it knows. Most computers with Intel or AMD processors speak x64. The recent computers of Apple, and most phones, speak Arm. A program built for one set does not run on a processor of the other.

The most useful instructions that a processor can add are called single instruction, multiple data (SIMD) instructions. A **SIMD** instruction does the same operation on several numbers at once: a SIMD register holds a row of numbers, and one instruction adds the whole row to another row.

An instruction set grows by extensions. Streaming SIMD Extensions (SSE) 4.2 and Advanced Vector Extensions 2 (AVX2) are extensions of x64 that add instructions, many of them SIMD. A register of SSE holds 4 numbers of 4 bytes, and a register of AVX2 holds 8. A program may be built to use them, and Strata's build enables AVX2 by default (`CMake/StrataCompilerOptions.cmake`).

A processor that lacks those instructions cannot do them. The program stops at the first such instruction with an error such as "illegal instruction", often not at the start but later, when the code first reaches one.

:::example[Adding two lists]
A program adds two lists of 1,000 numbers of 4 bytes, pair by pair, into a third list.

1. One pair at a time: 1,000 add instructions.
2. With SSE, 4 pairs at a time: 1,000 divided by 4, which is 250 instructions.
3. With AVX2, 8 pairs at a time: 1,000 divided by 8, which is 125 instructions.

The speed of the last case is not exactly 8 times, because the numbers still must come from memory, and then the order
of data matters again. SIMD works best on numbers that lie in a row.
:::

Try it: a game moves 2,400 positions by adding one number to each. How many add instructions does it need with AVX2?

:::answer
2,400 divided by 8 is 300 instructions, against 2,400 one at a time.
:::

## The operating system and processes

Your computer runs many programs, and they must not harm one another. The operating system (Windows, macOS or Linux) is the program that controls the machine: it starts the other programs, gives each one its own memory, shares
the cores between them and keeps the files.

A **process** is a running program with its own memory. When you start a program, the operating system copies its file
from storage into memory, creates the process and gives it a number, the **process id**, that names it while it runs.
The system may give the same number to a later process once the first has ended.

A process has four things that matter on this page:

- its own memory: address 1,000 in one process is not address 1,000 in another, so a program that writes where it should
  not damages only itself;
- a process id;
- an environment, a list of named texts such as the folders where programs live, that the process hands to every process
  it starts, its child processes;
- an exit code, a number that it reports when it ends, where 0 means that all went well.

[The tools](tools.md) shows how to read an exit code and how to set a variable of the environment.

When there are more lists to run than cores, the operating system gives each list a short slice of time on a core and
changes between them many times a second. You see this as many programs running at once.

A process that starts another is its **parent**, and the new one is its child. The processes form a tree. The editor
is the example that you have used.

```mermaid caption="Pressing the build shortcut in the editor starts a chain of child processes; the numbers are examples." alt="A tree of four boxes joined by arrows, from top to bottom: the editor with process id 4120, CMake with process id 8832, the build tool, and the compiler."
flowchart TB
    E["Editor, process id 4120"] --> C["CMake, process id 8832"]
    C --> B["Build tool"]
    B --> K["Compiler"]
```

When you press **Ctrl+B**, the editor starts CMake, the program that organizes a build, as a child process. The command is `cmake --build <folder> --parallel --config <configuration>`: the folder is your project's build folder, and the configuration is the one the editor was built in. CMake starts a build tool, `Ninja`, `make` or `MSBuild` depending on the computer, and the tool starts the compilers that turn your changed script files into machine code. Every one of them is a process with its own process id and its own exit code. The editor reads what they print and shows it in the **Console**.

The editor writes the command line it started to its log, on a line that begins `[Scripts] >` and then names CMake, usually with its full path. You can read the line in the **Console** after a build. The first build of a project, and the first one after its list of script files changed, starts CMake with other arguments, to prepare the build folder, and builds second.

Strata starts these processes through its `Process` class in `Strata/src/Strata/Core/Process.h`. The class also ends the whole tree when you close the project or the editor in the middle of a build, so no compiler stays running. [Platform, scheduling and priorities](../core/platform.md) tells more.

## The regions of a process's memory

The operating system gives a process a large range of addresses, and the process splits it into regions. Four matter:

- the code: the machine instructions of the program, which the processor reads but never changes;
- the fixed data: texts and numbers that the program contains, such as the words "Game Over";
- the **stack**: the place for the short-lived data of the steps in progress;
- the **heap**: the place for data of any size that lives as long as it is needed.

The stack is like a pile of plates. A step that starts puts its data on the top of the pile. A step that it starts in turn puts its own on top of that. When a step ends, its plate comes off first, so the last plate put on is the first taken off. Taking and putting is quick, because the pile only has a top: the processor changes one number that says
where the top is.

:::example[A pile of three steps]
A game runs a step called "update the world". It needs a counter and room for one position of 12 bytes, so it puts 16 bytes on the stack. Its work calls a step "move the cube", which needs 8 bytes more, so the pile is 24 bytes high. When
"move the cube" ends, its 8 bytes come off and the pile is 16 bytes. When "update the world" ends, the pile is empty.
:::

Try it: a step puts 40 bytes on the stack and starts a step that puts 24 bytes on. How high is the pile, and how high
is it after the second step ends?

:::answer
64 bytes while both steps run, and 40 bytes after the second ends, because its plate comes off first.
:::

The stack is small, a few MB at most on most systems, and its data must end when its step ends. A level of a game is neither small nor short: it holds thousands of objects and lives for minutes. Such data lives on the heap. A program asks the
system for a block of the size it needs and receives its address, uses it as long as it wants, and then gives it back.

The heap is slower than the stack, because the system must find a free block, and it is the program's job to give
blocks back. [C++ memory](cpp-memory.md) shows how code takes and gives back heap memory, and how a mistake with it
harms a game.

## Common mistakes

- **Taking memory for storage.** The symptom: you expect the data of a program to be there after you switch the computer off and on, or you trust a change that only lives in the editor. The fix: save, so that the data is written to
  storage; memory loses everything when the program ends.
- **Taking more cores for a faster single task.** The symptom: a computer with 16 logical processors runs one long task
  and the processor graph shows one logical processor full and the total at about 6 %. The fix: the program itself must
  split the task into parts that run at the same time, which is the subject of the page on threads.
- **Thinking that jumping around memory costs nothing.** The symptom: two loops do the same number of instructions and
  one takes many times longer. The fix: keep the data that a loop uses together, in the order the loop reads it.
- **Running a program built for newer instructions on an older processor.** The symptom: the program stops with
  "illegal instruction", sometimes only after it has been running for a while. The fix: build for the older
  instruction set, or run it on a processor that has the newer one.

## Summary

- A processor runs a program by doing its machine instructions one after another, billions a second; the program is a
  file on storage that the operating system copies into memory first.
- Memory is slow next to the processor, so caches keep copies in lines of 64 bytes (128 on Apple's processors). Reading data in the order it lies is fast, because one load serves the whole line.
- SIMD does one operation on 4 or 8 numbers with one instruction; a program built for newer instruction extensions
  stops at the first such instruction on an older processor.
- A process is a running program with its own memory, a process id, an environment for its child processes and an exit code. The process viewer of the system shows them, and the editor's build starts CMake and the compilers as child
  processes.
- A process's memory has the code, the fixed data, the stack for short-lived data in a pile and the heap for data
  kept as long as it is needed.

## Check yourself

1. A processor reads the 4-byte number at address 1,000, which lies in the cache line from 960 to 1,023. Which read is
   most likely to find its data already in the cache?

   - A. The number at address 1,004.
   - B. The number at address 1,024.
   - C. The number at address 1,100.
   - D. The number at address 5,000.

   :::answer{tests="cache-order"}
   A. The cache loaded the whole line from 960 to 1,023, and address 1,004 lies in it. Address 1,024 starts the next
   line, which nobody loaded yet; B is the mistake of thinking that the cache loads what comes next. C and D lie in
   other lines too.
   :::

2. A processor has 8 cores with two hardware threads each. The system's tools show one logical processor at 100 % and
   the rest idle. About what share of the whole processor does the program use?

   :::answer{tests="process-viewer"}
   About 6 %. The system shows 16 logical processors, and 1 divided by 16 is 6.25 %. One long task keeps one logical
   processor busy; the others stay idle unless the program splits its work.
   :::

3. A game is built for AVX2 and started on a processor that has only SSE 4.2. What happens, and when?

   :::answer{tests="simd"}
   The processor does not know the AVX2 instructions, so the program stops with an error such as "illegal instruction",
   at the first such instruction it reaches. That may be at the start or later in the program. SSE 4.2 instructions
   still work, but the program cannot avoid the others.
   :::

4. Put the places in order from the fastest to read to the slowest: memory, L2 cache, a register, storage, L1 cache.

   :::answer{tests="cache-order"}
   Register, L1 cache, L2 cache, memory, storage. Each step is slower, with times of under 1 ns, 1 ns, 4 ns, 80 ns
   and about 100,000 ns.
   :::

5. A program starts, and its stack holds 16 bytes. It starts a step that puts 48 bytes on, and then a second step of
   8 bytes inside that one. The second step ends. How many bytes does the stack hold?

   :::answer{tests="regions"}
   64 bytes. The pile was 16, then 64, then 72 while the second step ran; when the second ends its 8 bytes come off,
   and the 48 bytes of the first step stay until it ends too.
   :::

6. Put these three steps in order: the processor does the instructions of your game; you start the game; the operating system copies the game's instructions from storage into memory.

   :::answer{tests="run-program"}
   First you start the game, then the operating system copies its instructions from storage into memory, and then the
   processor does them. The processor cannot read the file on the drive directly, so the copy comes before the work.
   :::

## Practice

1. **Basic.** Open your system's process viewer: "Task Manager" on Windows (**Ctrl+Shift+Esc**), "Activity Monitor" on
   macOS, "System Monitor" on Linux. Start the editor, find its process and write down its process id, its memory and
   its number of threads.

   :::answer[Worked solution]{tests="process-viewer"}
   On Windows, open the **Details** tab, find `StrataEditor.exe` and add the **PID** and **Threads** columns by
   right-clicking a column heading and choosing **Select columns**. The memory is in the **Memory** column. On macOS,
   search for `StrataEditor` in Activity Monitor; its id and thread count are columns of the table. Your numbers differ
   from mine, and the id is new each time you start the editor.

   An editor with its window uses hundreds of MB and tens of threads: about 230 MB and 80 threads with Your first game
   open, in one run on Windows. `StrataCLI launch --no-gpu` starts an editor without a window and without a graphics
   device. It loads no graphics driver and keeps no pictures for the GPU, so it uses tens of MB: about 30 MB and 55
   threads in the same run.
   :::

2. **Basic.** A processor does 3 billion ticks a second and a game runs at 120 frames a second. How many ticks does one
   frame hold, and what share of a frame do 50,000 reads from memory of 80 ns each take?

   :::answer[Worked solution]{tests="run-program cache-order"}
   A frame lasts 1,000 divided by 120, which is 8.3 ms, and 3 billion ticks a second give 3 million a millisecond, so
   a frame holds about 25 million ticks. The reads take 50,000 times 80 ns, which is 4 ms, and 4 divided by 8.3 is
   48 % of the frame.
   :::

3. **Medium.** Open the project of your first game, `FirstGame`, or download the project at the last checkpoint of
   [Make it spin with a script](../start/first-game.md#make-it-spin-with-a-script) and open its `FirstGame.stproj`
   with **File ▸ Open Project...**. In `Scripts/Spinner.cpp`, change one character of a comment: the full stop at the
   end of the line `// Turns its entity around the world's Y axis.`, above `class Spinner`. Press **Ctrl+B**. Read
   the lines that start `[Scripts] >` in the **Console**, and watch the process viewer while the build runs.

   :::answer[Worked solution]{tests="process-viewer run-program" solution="tutorials/basics/computer/exercise-3.tutorial.json"}
   The build starts CMake with `--build`, the folder of the build, `--parallel` and `--config` with a configuration: `Dist` for the installed Strata, the configuration it was built in. With Visual Studio the line ends with `-- /nodeReuse:false`, which asks `MSBuild` to leave no process of its own running.

   The comment changed the file, so a compiler starts for it and appears for a moment in the viewer. It is a child of the build tool, below CMake, which is
   a child of the editor. A build of a file that has not changed starts CMake but no compiler, and a build lasts about a second, so
   you may need to try twice to see the compiler. The **Console** keeps the command lines.

   The download of the worked solution holds the `Spinner.cpp` of Your first game with that one change. In another
   project, change the character in your own file instead of copying this one over it.
   :::

4. **Medium.** Open the graphs of the logical processors: in Windows' Task Manager, **Performance**, **CPU**, then
   right-click the graph and choose **Change graph to**, **Logical processors**. Press **Play** in a scene and watch.
   How many logical processors are busy, and why not all?

   :::answer[Worked solution]{tests="process-viewer"}
   The graphs of the machine you use differ. On macOS use **Window**, **CPU History** in Activity Monitor. On Linux the **Resources** tab of the System Monitor shows one graph for each processor. A small scene often keeps only a few logical processors busy. A program uses more of them only when its work is split into parts that run at the same time, and a game of this size has little work to split.
   :::

5. **Hard.** A game keeps 100,000 objects of 128 bytes each in a row, and a loop reads only a 12-byte position at the
   start of each. Count the cache lines of 64 bytes that the loop loads. Then count them if the 100,000 positions lie
   in a row of their own, and give the time of each at 80 ns a line.

   :::answer[Worked solution]{tests="cache-order"}
   Each object starts on its own pair of lines, so the loop loads one line for each, 100,000 lines, and 100,000 times
   80 ns is 8 ms. The separate positions fill 100,000 times 12, which is 1,200,000 bytes, and 1,200,000 divided by 64 is
   18,750 lines, which take 18,750 times 80 ns, which is 1.5 ms. The loop is about 5 times faster, because every byte
   of every line it loads is a byte it uses.
   :::

## Where the book uses it

- [Threads, atomics and races](threads.md) builds on cores and hardware threads: a program uses several cores only when
  it starts threads.
- [C++ memory](cpp-memory.md) builds on the stack and the heap: it shows how code puts data on each and gives it back.
- [Numbers in a computer](numbers.md) builds on the byte and the memory address, and shows what a byte can hold.
- [How a C++ program is built](build.md) builds on the machine code and the compiler that makes it.

## Further reading

- Ulrich Drepper, "What Every Programmer Should Know About Memory" (2007): how caches and memory work, in great
  detail (advanced).
- Charles Petzold, "Code: The Hidden Language of Computer Hardware and Software": builds a computer from the idea of a
  switch (beginner).
- Intel, "Intel Intrinsics Guide": the list of SSE and AVX instructions (advanced).
