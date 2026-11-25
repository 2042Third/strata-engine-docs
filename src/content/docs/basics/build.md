---
id: basics/build
title: "How a C++ program is built: from two files by hand to CMake"
description: "Build a two-file C++ program by hand, then with CMake: compiler, linker, libraries, build systems, Debug and Release, and the errors each step gives."
kind: primer
size: L
tracks: [B, E]
needs: [basics/tools, basics/programming-3, basics/computer]
time: 90
learn:
  - id: build-steps
    text: explain how a compiler and a linker turn source files into one executable
  - id: errors
    text: fix a compile error and a link error in a two-file program
  - id: libraries
    text: choose between an executable, a static library, a shared library and a module library
  - id: cmake
    text: write a CMakeLists.txt for two files and run its configure step and its build step
  - id: configurations
    text: predict what a Debug build and a Release build change in the same program
status: final
---

::::test-out

1. A game has 10 `.cpp` files, and 4 of them include `Util.h`. You change one line of `Util.h` and run the build with a build system. How many `.cpp` files are compiled again?

   :::answer{tests="build-steps"}
   Four. The build system compiles again each file whose inputs changed, and a header is an input of every file that includes it. The other 6 files keep their object files.
   :::

2. A build stops with `undefined reference to 'Spawn(int)'`. Is that a compile error or a link error, and what are the two usual causes?

   :::answer{tests="errors"}
   A link error: every file compiled, and the linker found a use of `Spawn` with no definition. Either no file defines the function, or the file that defines it was not compiled or was left off the link line.
   :::

3. Write the one CMake line that links a library named `physics` into a program named `game`.

   :::answer{tests="cmake"}
   `target_link_libraries(game PRIVATE physics)`. The program comes first, then the keyword that says who needs the library, then the library.
   :::

4. A game wants to load a new version of its script code while it runs, without stopping the game. Which kind of library does it use: static, shared or module?

   :::answer{tests="libraries"}
   A module library, a kind of shared library that the program loads on purpose, at a moment it chooses. A static library is copied into the program when it is built, so it cannot be replaced while the program runs.
   :::

5. A program contains `assert(++checks == 1);` and then prints `checks`, with `checks` starting at 0. It prints 1 in a Debug build. What does a Release build print, and why?

   :::answer{tests="configurations"}
   A Release build prints 0: it defines `NDEBUG`, and `assert` then expands to nothing, so the expression with `++checks` never runs.
   :::

::::

## Why you will need this

A script, a shader and the engine itself are all text files, and a computer runs none of them as text. Something must turn the text into :term[machine code]{id=machine-code}, and when that fails, the message comes from a tool you have not met yet. This page teaches that chain from the beginning, on a program of three small files.

You use it at once. [The map of the engine](../core/map.md) names the pieces of Strata by what they are built into. [Shared libraries in Strata](../scripting/shared-libraries.md) explains how a game loads its script module. [Script builds in the editor](../editor/script-builds.md) shows the build that **Ctrl+B** starts, and you will know what each of its steps does.

This page needs no download and no project: it uses a C++ compiler and CMake, which the next section finds. Only the optional last exercise opens a project of the editor, the one that holds your `Playground` script.

## Open a terminal that finds a compiler

Everything below runs in a terminal and needs a compiler and CMake. The editor finds both by itself, so nothing before this page needed them on the `PATH`, the list of folders where a terminal searches for programs. In an ordinary terminal they may be missing.

On Windows, Visual Studio puts the compiler `cl` and its own CMake on the `PATH` only in its developer terminals. Open the Start menu and start **x64 Native Tools Command Prompt for VS**, which prepares the 64-bit compiler that the editor's 64-bit script modules need. Every Windows line on this page runs in it as written. Type `cl`: the banner must end with "for x64". The Start menu also holds **Developer PowerShell for VS**, which does not fit: it prepares the 32-bit compiler, and its banner ends with "for x86".

In an ordinary terminal, `cl` is "not recognized". Type `where cmake` in the new terminal: the first line it prints must be in the Visual Studio folder. A CMake of another installation that comes first may choose another generator; then add `-G "Visual Studio 18 2026"` to each configure line on this page, or `-G "Visual Studio 17 2022"` for Visual Studio 2022.

On Linux, run `sudo apt install g++ cmake ninja-build`. On macOS, run `xcode-select --install` for the compiler, then `brew install cmake ninja`; CMake.app from the CMake website works too, once you run its menu item "How to Install For :term[Command Line]{id=terminal-command} Use" under "Tools". The check on both: `c++ --version` and `cmake --version` print a version, and CMake is 3.25 or later.

## A compiler turns one source file into one object file

Take a program of three files. `Greeting.h` declares a function, `Greeting.cpp` defines it, and `main.cpp` calls it and prints the result. Make a folder `hello` and write them in it.

```cpp src="book:sketches/basics-build-Greeting.h#L1-L6"
#pragma once

#include <string>

// The text the program prints for a player's name.
std::string MakeGreeting(const std::string& name);
```

The header is the promise: a function named `MakeGreeting` exists, takes a name and gives back a string. The first line, `#pragma once`, tells the compiler to read the header only once per :term[source file]{id=source-file}. Older code does the same with include guards, a few lines of `#ifndef` around the header, and both prevent the error "defined twice" when two headers include the same third one.

```cpp src="book:sketches/basics-build-Greeting.cpp.txt#L1-L6"
#include "Greeting.h"

std::string MakeGreeting(const std::string& name)
{
	return "Hello, " + name + "!";
}
```

The `.cpp` file keeps the promise: it holds the body. `main.cpp` uses the function without ever seeing the body.

```cpp src="book:sketches/basics-build-main.cpp.txt#L1-L9"
#include "Greeting.h"

#include <iostream>

int main()
{
	std::cout << MakeGreeting("Coin Run") << "\n";
	return 0;
}
```

A **compiler** is the program that reads source code and writes machine code for the processor. It works on one source file at a time.

The result of one compile is an **object file**: a file of machine code for one source file, in which some names still wait to be connected to their definitions. The next commands compile the two source files separately. The flag `-c` (`/c` for `cl`) means "compile, and stop before linking". The flag `/EHsc` enables the exception handling that the standard library expects.

::::tabs{sync=os}
:::tab[Windows]

```powershell
cl /EHsc /c main.cpp
cl /EHsc /c Greeting.cpp
```

Two files appear next to the sources: `main.obj` and `Greeting.obj`. The compiler also prints each file's name as it works.
:::
:::tab[Linux]

```sh
c++ -c main.cpp
c++ -c Greeting.cpp
```

Two files appear: `main.o` and `Greeting.o`. The compiler prints nothing when all is well.
:::
:::tab[macOS]

```sh
c++ -c main.cpp
c++ -c Greeting.cpp
```

:::
::::

On macOS, `c++` starts Apple's compiler. Neither object file runs, because each is only a part. The next picture shows the whole chain, with the linker that comes in a moment.

```mermaid caption="Each source file becomes one object file, and the linker joins the object files into the program." alt="A flow from left to right with two rows. The first source file goes into the compiler and comes out as an object file. The second source file goes through the compiler the same way. Both object files go into the linker, which writes the program."
flowchart LR
    M["main.cpp"] --> C1["compiler"] --> MO["main.o"] --> L["linker"]
    G["Greeting.cpp"] --> C2["compiler"] --> GO["Greeting.o"] --> L
    L --> H["hello"]
```

## A translation unit is a source file with its headers copied in

You wrote `#include "Greeting.h"` in two files. Before the compiler reads a source file, a first step called the preprocessor replaces each `#include` line with the full text of that header, and does so again inside the copied text. The result is the **translation unit**: one source file with every header copied in, the unit the compiler translates in one go.

Two facts follow. First, a header is never compiled alone: its text becomes part of each source file that includes it, once for each. A header with a small mistake gives its error in the source file that included it, and the error is reported at the header's own line. Second, the compiler sees only one translation unit at a time. In `main.cpp` it knows what `Greeting.h` promised and nothing else, so it cannot check that a body exists.

So C++ separates a declaration from a definition. A **declaration** tells the compiler that a name exists and what type it has: `std::string MakeGreeting(const std::string& name);`. A **definition** is the body, the one place that makes the thing exist. A name may be declared in many translation units and must be defined in exactly one program-wide. This is the **one-definition rule**.

:::note
Why does the header carry declarations and not the bodies? Suppose `Greeting.h` held the body and 50 files included it. Each of the 50 object files would then hold a copy of the function, and the linker would complain about 50 definitions of one name. Small functions may be defined in a header when they are marked `inline`, which allows the copies.
:::

:::example[How many translation units, and how many compiles?]
A project has `A.cpp`, `B.cpp` and `C.cpp`, and two headers, `X.h` and `Y.h`. `A.cpp` and `B.cpp` include `X.h`, `C.cpp` includes `Y.h`, and `Y.h` includes `X.h`.

The project has 3 translation units, one for each `.cpp` file, and the headers make none of their own. `X.h` is copied into all 3, directly into two and through `Y.h` into `C.cpp`. A full build runs the compiler 3 times, and no compile touches `X.h` or `Y.h` as a file by itself.
:::

Try it: the same project adds `D.cpp`, which includes nothing. How many translation units are there, and in how many does the text of `X.h` appear?

:::answer
4 translation units, and `X.h` appears in 3 of them: `A.cpp`, `B.cpp` and `C.cpp`. `D.cpp` includes no header, so it holds only its own text.
:::

## The linker joins object files and connects names

Look inside the two object files with a tool that lists their symbols. A **symbol** is a name that an object file defines or needs, such as a function. On Linux and macOS the tool is `nm`; on Windows it is `dumpbin`, in the developer terminal. The flag `-C` turns the machine form of the C++ names back into names you can read.

```sh
nm -C main.o
nm -C Greeting.o
```

`main.o` needs `MakeGreeting` and does not define it. `Greeting.o` defines it. The letter in front of the name tells which: `U` means undefined, `T` means a function that the file defines. This is the real output for the two lines that matter, on one system; others add some lines, and the long type of the argument differs between compilers.

```text
                 U MakeGreeting(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)
0000000000000000 T MakeGreeting(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)
```

On Windows, run `dumpbin /symbols main.obj | findstr MakeGreeting` and the same for `Greeting.obj`; `findstr` keeps only the lines with the name. `dumpbin` gives the same facts in other words. Where `nm` writes `U`, it writes `UNDEF`; where `nm` writes `T`, it writes the number of the section that holds the code, such as `SECT5`. Each line shows the machine form of the name first, then the form you can read, between round brackets. `External` marks a name that other files may use, and the extra lines marked `Static` are names that only this file uses.

The **linker** is the program that joins object files and libraries into one program: it connects each use of a name to the definition of that name. It finds the `U` in `main.o`, finds the matching `T` in `Greeting.o`, and writes the address of the function into the call. A good picture is a book assembled from chapters: where one chapter says "see the table in chapter 4", the binder writes in the page number.

:::analogy[A book made of chapters]
Each author writes a chapter alone and leaves a blank where it refers to another chapter: "see chapter 4, page ___". The binder collects the chapters, finds where chapter 4 landed and writes the page number into every blank. If no chapter 4 was handed in, the binder cannot finish the book and reports a reference to nothing.

**Where it breaks:** a binder only copies numbers on paper, while a linker also lays the machine code of all the chapters out in one file and may drop chapters that nothing refers to.
:::

The **executable** is the file that results: a program the :term[operating system]{id=operating-system} can start. The next commands link the two object files into one.

::::tabs{sync=os}
:::tab[Windows]

```powershell
link main.obj Greeting.obj /OUT:hello.exe
.\hello.exe
```

The linker writes `hello.exe`, and the second line starts it.
:::
:::tab[Linux]

```sh
c++ main.o Greeting.o -o hello
./hello
```

The compiler driver `c++` starts the linker for you when it gets object files, and `-o` names the result.
:::
:::tab[macOS]

```sh
c++ main.o Greeting.o -o hello
./hello
```

:::
::::

Both systems print one line.

```text
Hello, Coin Run!
```

The linker connected the call in `main.o` to the body in `Greeting.o`, and the program ran. Every later build on this page prints the same line.

## Two kinds of error: compile errors and link errors

The compiler and the linker fail in different ways, and a reader who knows which stage spoke knows where to look. Break the program twice. First delete the `;` at the end of the `std::cout` line in `main.cpp` and compile it again.

```text
main.cpp: In function 'int main()':
main.cpp:7:54: error: expected ';' before 'return'
    7 |         std::cout << MakeGreeting("Coin Run") << "\n"
      |                                                      ^
      |                                                      ;
    8 |         return 0;
      |         ~~~~~~
```

A **compile error** comes from the compiler about one translation unit: it names a file and a line, here line 7, and no object file is written. MSVC prints `main.cpp(8): error C2143: syntax error: missing ';' before 'return'`, with an error code that starts with C. It names line 8, where it met the `return` that the `;` should come before. A compiler names the line where it noticed the mistake, which can be the line after the one to fix. Read the first error first, because later ones are often its echoes.

Now restore the `;` and link without `Greeting.o`, as if you had forgotten to compile or to name that file.

```sh
c++ main.o -o broken
```

The compiler had nothing to complain about, since `Greeting.h` made the promise. The linker finds that the promise was not kept.

```text
ld.exe: main.o:main.cpp:(.text+0x40): undefined reference to `MakeGreeting(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)'
collect2.exe: error: ld returned 1 exit status
```

A **link error** comes from the linker: a name is used and has no definition, or has two. It names the object file that uses the name, not a source line. The words to search for are "undefined reference" with the linker of Linux and "Undefined symbols" with the linker of Apple. The linker of MSVC says "unresolved external symbol", with the error `LNK2019` and then `LNK1120`, which counts them. To fix it, find where the name should be defined, and check that the file is compiled and named on the link line.

:::example[Which stage spoke?]
Three messages from three builds. `main.cpp:12: error: 'Spawn' was not declared in this scope`. `ld: undefined reference to 'Spawn(int)'`. `Player.cpp:30: error: expected ')' before ';'`.

The first and third give a source file and a line, so they come from the compiler. In the first, `main.cpp` never included the header that declares `Spawn`, so the fix is an `#include`. The second comes from the linker: the header was included and the call compiled, but nothing defines `Spawn(int)` in what was linked.
:::

Try it: a build prints `multiple definition of 'Score'`. Which stage printed it, and what happened?

:::answer
The linker. Two object files each define `Score`, which breaks the one-definition rule; the usual cause is a function body written in a header that two source files include.
:::

## Executables and libraries

A program rarely comes from loose object files. A **library** is a collection of compiled code that other programs use: it has no `main` of its own and cannot start by itself. An executable is the other kind of build result, the program with its `main`.

A **static library** is an archive of object files that the linker copies from into each program that uses it. On Linux and macOS it is a `.a` file made by `ar`, on Windows a `.lib`. Make `Greeting.o` into one and link with it.

```sh
ar rcs libgreeting.a Greeting.o
c++ main.o -L. -lgreeting -o hello
```

The first line packs the object file into `libgreeting.a`. In the second, `-L.` says "search for libraries in this folder", and `-lgreeting` names `libgreeting.a`. The program prints the same line. The linker copied the object files it needed out of the archive, so the code now lives inside `hello`, and you may delete the archive without harming the program.

With `ld`, the linker of Linux, the order on the link line matters. It reads left to right, and when it reaches a library it takes only the object files that satisfy names it already needs. A library that another library needs must therefore stand after that library.

Suppose `Greeting.cpp` calls a function `Frame` from a second library. Then `main.o -lgreeting -lframe` links. The line `main.o -lframe -lgreeting` fails with `undefined reference to 'Frame(...)'`, because nothing needed `Frame` when `libframe.a` was read, so the linker took nothing from it. The linkers of MSVC and Apple's :term[toolchain]{id=build-tools} read all libraries before they decide, so for them the order does not matter.

:::why
Strata's engine is built from layers, and each layer is a static library (`CMake/StrataLayers.cmake`) that the editor and the runtime link into their own executables. The choice keeps the engine in one piece with no loading step and lets the linker drop code a program never calls. The cost is that every program holds its own copy of the layers it uses, and a change to a layer means linking each program again.
:::

## Libraries loaded while the program runs

A **shared library** is a library in its own file that the operating system loads when a program starts, so that programs share one copy on the drive. It is a `.dll` file on Windows, a `.so` file on Linux and a `.dylib` file on macOS. At link time, the linker only records that the program needs the library, and the loading happens at the start of every run. If the file is missing then, the program does not start.

A **module library** is a shared library that the program loads on purpose, by its path, at a moment of its choice, and may unload again. The program asks the operating system for the file and then finds the functions it wants by name. The file itself is no different from a shared library; the difference is who loads it and when.

In Strata, a game's script code is built as a module library. The build uses CMake's `MODULE` kind of library (`StrataScriptCore/CMake/StrataScriptModule.cmake`), and the editor loads the result while the game runs. It can replace the file with a new build without stopping the game.

| Kind | File | Joined into the program | Chosen by |
| --- | --- | --- | --- |
| Executable | `.exe` or no extension | It is the program | The operating system starts it |
| Static library | `.lib` or `.a` | Copied in at link time | The linker |
| Shared library | `.dll`, `.so`, `.dylib` | Loaded at every start | The operating system, from the list recorded at link time |
| Module library | the same three | Loaded on request | The program's own code |

:::note
The details of how Strata hides and exports names in its modules, and how it loads and swaps them, belong to [Shared libraries in Strata](../scripting/shared-libraries.md).
:::

## What runs before main

A program does not start at `main`. First every global variable of the program is built, which is **static initialization**: a global with a :term[constructor]{id=constructor} runs that constructor before `main` begins. Within one source file the order is the order of the definitions.

The next program has two globals whose constructors print a line. Look at the order of the lines and at where `main` comes.

```cpp sketch="basics-build-order.cpp"
#include <cstdio>

// A global is built before main runs. Within one file, in the order of its definitions.
struct Announcer
{
	explicit Announcer(int number)
	{
		std::printf("building global %d\n", number);
	}
};

Announcer g_First(1);
Announcer g_Second(2);

int main()
{
	std::printf("main starts\n");
	return 0;
}
```

1. **Line 12:** `g_First` is defined before `g_Second` in this file, so its constructor runs first.
2. **Line 17:** this line of `main` prints only after both globals are built.

```text output-of="basics-build-order.cpp"
building global 1
building global 2
main starts
```

Between two source files, C++ leaves the order open. If `A.cpp` and `B.cpp` each define a global and one needs the other to be built, the result may differ between compilers and even between builds, so a program must not rely on it. Use the globals only from `main` and after, or build them on first use.

The linker adds a second surprise. When it takes object files from a static library, it takes only those that some needed name points to. An object file that holds only a global whose constructor registers something is named by nothing, so the linker drops it, and the registration never happens.

Here is a small case. `Registry.o` holds only a global whose constructor prints `registered`, and `Empty.o` holds a `main` that prints `main runs` and never names it. Linked through a library with `-lreg`, the program printed only `main runs`. With `Registry.o` named on the link line, it printed `registered` first and then `main runs`.

A program that needs such objects names them on the link line or asks its build system to keep the whole library. Strata avoids the trap by calling each module's registration function by name from one place, and [Layers and registries](../core/layers-registries.md) tells how.

## A build system builds only what changed

A real program has hundreds of files, and typing a command for each is too much work. A **build system** is a program that knows which files depend on which and runs the compiler and the linker for only the parts that changed. It gets the rules from a description of the project, and it decides what changed by comparing file times.

The rule is small. An object file is out of date when its source file, or any header the source includes, has a later modification time. An executable is out of date when any of its object files is. Suppose `Greeting.cpp` was saved at 10:00 and `Greeting.o` was written at 10:05: the object file is newer, so it is current. Save `Greeting.cpp` again at 10:20 and the object file is older than its source, so the build system compiles it again, and then links again, because an input of the executable changed.

A header makes the cost larger. `Greeting.h` is part of the translation unit of every file that includes it, so a change to it makes all of them out of date, while a change to `Greeting.cpp` touches only that file. This is why a change to a widely used header can make a large program rebuild for minutes, and why a program keeps its headers small.

## CMake describes the project, and a generator writes the build

**CMake** is a program that reads a description of a project and writes the files of a build system for it. Writing the description once serves every system: CMake can make a Visual Studio solution on Windows and a Ninja file on Linux. Its description is a `CMakeLists.txt` file. Put this one next to the three sources.

```cmake
cmake_minimum_required(VERSION 3.25)
project(Hello CXX)

set(CMAKE_CXX_STANDARD 20)

add_library(greeting STATIC Greeting.cpp)
add_executable(hello main.cpp)
target_link_libraries(hello PRIVATE greeting)
```

The first line names the oldest CMake that may read the file. `project` names the project and its language, and the standard is C++20. `add_library` makes a **target**, a thing to build, named `greeting` from `Greeting.cpp`, and `add_executable` makes the target `hello`. The last line says that `hello` needs `greeting`; `PRIVATE` means that only `hello` itself needs it, and programs that would link `hello` do not. CMake finds the right compiler flags and file names for the system.

CMake works in two steps. The **configure step** reads the `CMakeLists.txt` files, tests the compiler and writes the build files into a build folder. The build step starts the build system on those files. Run both, with a build folder named `build` beside the sources.

::::tabs{sync=os}
:::tab[Windows]

```powershell
cmake -S . -B build
cmake --build build
```

The first line configures with Visual Studio as the **generator**, the part of CMake that writes the files of one build system. The second starts it.
:::
:::tab[Linux]

```sh
cmake -S . -B build -G Ninja
cmake --build build
```

Here `-G Ninja` picks Ninja, a fast build system, as the generator. Without it, Linux uses `Unix Makefiles`.
:::
:::tab[macOS]

```sh
cmake -S . -B build -G Ninja
cmake --build build
```

:::
::::

With Ninja on one system, the build step printed these four lines. Windows names object files `.obj` and Linux and macOS `.o`, and Visual Studio words its lines in another style.

```text
[1/4] Building CXX object CMakeFiles/greeting.dir/Greeting.cpp.obj
[2/4] Building CXX object CMakeFiles/hello.dir/main.cpp.obj
[3/4] Linking CXX static library libgreeting.a
[4/4] Linking CXX executable hello.exe
```

Each step of the by-hand build is there. Run `cmake --build build` again and Ninja prints `ninja: no work to do.`, because nothing is newer than its object file. Now change `Greeting.cpp` and build: 3 steps run (one compile and two links). Change `Greeting.h` and build: 4 steps run, because both source files include it. These counts are the file-time rule at work.

CMake keeps its choices in a **cache**, the file `CMakeCache.txt` in the build folder, so a second configure remembers the compiler and any `-D` setting you gave. A `-D` sets a cache entry: `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release` records the configuration. If you edit a `CMakeLists.txt`, the build step notices and runs the configure step first by itself. Delete the build folder to start with a clean cache.

A build can also pass a name to the source code. `target_compile_definitions(hello PRIVATE GAME_NAME="Coin Run")` adds `-DGAME_NAME="Coin Run"` to the compiler's line for the target, which defines a macro `GAME_NAME` that the source can test with `#if` and `#ifdef`. Macros are the subject of [C++ modern features](cpp-modern.md); you meet the same mechanism in the next section, where CMake passes `NDEBUG` for you.

## A configuration trades speed of running for ease of finding bugs

The same sources can be built in different ways. A **build configuration** is a named set of compiler and linker settings; the usual ones are Debug and Release. Debug leaves the machine code close to your source, so that a debugger can step line by line; Release optimizes.

**Optimization** means that the compiler rewrites your code into machine code that does the same job in less time. It keeps values in registers, replaces a call with the function's body, and removes work whose result nothing uses. The flags are `-O0` (none) and `-O2` (much) for the `c++` of Linux and macOS, and `/Od` and `/O2` for MSVC. A test program that finds the primes up to 20,000,000 took 0.63 s at `-O0` and 0.10 s at `-O2` on one machine, about six times less. The two programs print the same answer.

**Debug information** is data beside the machine code that tells a debugger which instruction belongs to which line and where each variable lives. MSVC keeps it in a `.pdb` file and asks for it with `/Zi` and `/DEBUG`; other systems keep it inside the program file or beside it and ask with `-g`. It does not change what the program does, and it only makes the files larger. The same program was 267,280 :term[bytes]{id=byte} without and 303,538 with `-g`. [Debugging](debugging.md) shows what a debugger reads from it.

The third difference is asserts. `assert(condition)` stops the program with a message if the condition is false, and it is a check for the programmer. The C++ library keeps it only when the macro `NDEBUG` is not defined; CMake's Release configuration defines it. Look at what that does to a program whose assert has a side effect.

```cpp sketch="basics-build-assert.cpp"
#include <cassert>
#include <cstdio>

int main()
{
	int checks = 0;

	// The expression inside assert runs only in a build that keeps asserts.
	assert(++checks == 1);

	std::printf("checks run: %d\n", checks);
	return 0;
}
```

1. **Line 9:** the expression `++checks == 1` adds 1 to `checks` and then compares, so it does work as well as check.
2. **Line 11:** the print shows whether that work happened.

The program is built here with no `NDEBUG`, as a Debug build is.

```text output-of="basics-build-assert.cpp"
checks run: 1
```

Built with `c++ -DNDEBUG`, the same file prints `checks run: 0`: the assert vanished with its `++`. An assert holds only a check, never work the program needs. So a bug can hide in one configuration, and a program must be tested in the configuration that ships.

Where is the configuration chosen? It depends on the generator. Visual Studio, Xcode and Ninja Multi-Config are **multi-config generators**: one build folder holds every configuration, and the build step picks one with `--config`. Ninja and `Unix Makefiles` are single-config: the configure step picks it, once, and a build folder holds one configuration. If you give `--config Release` to a single-config build, nothing changes, and you get a program with no optimization, without a word of warning.

::::tabs{sync=os}
:::tab[Windows]

```powershell
cmake -S . -B build
cmake --build build --config Release
```

Visual Studio is multi-config: the build step chooses.
:::
:::tab[Linux]

```sh
cmake -S . -B buildr -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build buildr
```

Ninja is single-config: the configure step chooses, so a Release build needs a folder of its own.
:::
:::tab[macOS]

```sh
cmake -S . -B buildr -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build buildr
```

:::
::::

With `-v` after `--build` (a Ninja build), the compile line of this build was `c++ -O3 -DNDEBUG -std=gnu++20 -c Greeting.cpp`: CMake chose the flags that belong to Release.

Strata uses three configurations: Debug, Release and Dist. `CMake/StrataConfigurations.cmake` describes Debug as built without optimization, with asserts and logging. It describes Release as optimized, with debug information, asserts and logging, and Dist as optimized the same way with asserts compiled out, for exported games. Strata's own check macro `ST_CORE_ASSERT` plays the part of `assert`.

The presets use Visual Studio on Windows and Ninja Multi-Config on Linux and macOS, so `--config` picks the configuration there. When the editor builds a script module, it passes the configuration as `-DCMAKE_CONFIGURATION_TYPES` to a multi-config generator and as `-DCMAKE_BUILD_TYPE` to the others. Building the engine itself, and what each configuration costs, is the subject of [Building Strata](../engineering/building.md). Strata's own CMake files, with their layers, options and presets, are the subject of [Inside Strata's CMake](../engineering/cmake.md).

## A linker can drop code and merge functions

A Release link can make the program smaller. Two options of MSVC's linker, `/OPT:REF` and `/OPT:ICF`, are on in Strata's Release and Dist links (`CMake/StrataConfigurations.cmake`, with `/DEBUG` beside them to keep the debug information). The first drops functions and data that nothing reaches from `main`. The second, identical code folding, notices functions whose machine code is the same and keeps one copy.

The folding has a side effect that surprises programs. After it, two different functions that compile to the same instructions share one address, so a program that compares function addresses to tell functions apart may think two are the same. Do not use a function's address as its identity.

## Common mistakes

- **Taking a link error for a compile error.** The symptom: the build prints `undefined reference to 'X'` and you search the source line, which is not given. The fix: find where `X` should be defined, and check that the file is compiled and named on the link line.
- **Thinking that a header is compiled by itself.** The symptom: you rebuild after changing a header and expect one file to change. The fix: the header is copied into every file that includes it, so each of them compiles again.
- **Defining a function in a header.** The symptom: `multiple definition of 'X'` when two source files include the header. The fix: declare it in the header and define it in one `.cpp` file, or mark it `inline`.
- **Putting libraries in the wrong order on the link line of Linux.** The symptom: `undefined reference` to a function whose library is on the line. The fix: put a library after every library and object file that needs it.
- **Asking for Release in the wrong place.** The symptom: a "Release" build that runs slowly and still has its asserts. The fix: for Ninja and `Unix Makefiles`, give `-DCMAKE_BUILD_TYPE=Release` to the configure step; for Visual Studio, give `--config Release` to the build step.
- **Doing needed work inside an assert.** The symptom: the program works in Debug and fails in Release. The fix: do the work on a line of its own and assert on the result.

## Summary

- A compiler turns each translation unit, a source file with its headers copied in, into one object file. The linker joins the object files and libraries into an executable and connects each name to its one definition.
- A :term[compile error]{id=compile-error} names a file and line and comes from one translation unit. A link error names a symbol and comes from the linker: a name has no definition, or two, usually because a file was not compiled or not named on the link line.
- A static library is copied into each program at link time, and on Linux its place on the link line matters. A shared library is loaded at every start, and a module library is loaded on purpose while the program runs, as a script module is.
- A build system compares file times and builds only what changed, so a header rebuilds every file that includes it. CMake describes targets in `CMakeLists.txt`; its configure step writes the build files for a generator, and its build step runs them.
- A Debug build keeps the code close to the source, with asserts. A Release build is optimized and usually drops asserts. With Visual Studio the build step picks the configuration; with Ninja the configure step does.

## Check yourself

1. A project has 5 `.cpp` files and 3 headers. Each `.cpp` file includes 2 headers. How many translation units are there?

   - A. 3
   - B. 5
   - C. 8
   - D. 10

   :::answer{tests="build-steps"}
   B. A translation unit is one source file with its headers copied in, so there is one for each `.cpp` file: 5. A header is no unit of its own (A and C), and the number of includes does not add units (D).
   :::

2. Which message is a link error?

   - A. `main.cpp:7:54: error: expected ';' before 'return'`
   - B. `Player.cpp:30: error: 'Vec2' does not name a type`
   - C. `main.o: undefined reference to 'Update(float)'`
   - D. `Score.h:2: error: redefinition of 'struct Score'`

   :::answer{tests="errors"}
   C. It names an object file and a symbol, not a source line. A and B come from the compiler, which names a source line, and D is also a compile error: a header included twice, which `#pragma once` prevents.
   :::

3. `Greeting.cpp` calls `Frame`, which `libframe.a` defines, and `libgreeting.a` holds `Greeting.o`. With the linker of Linux, why does `c++ main.o -lframe -lgreeting` fail and `c++ main.o -lgreeting -lframe` work?

   :::answer{tests="libraries"}
   The linker reads left to right. In the first line, `libframe.a` is read when nothing needs `Frame` yet, so nothing is taken from it, and then `libgreeting.a` brings in the need and finds no definition. In the second, the need comes first and the later library satisfies it.
   :::

4. You add a source file to a `CMakeLists.txt` and run `cmake --build build`. Do you need to run the configure step yourself first?

   :::answer{tests="cmake"}
   No. The build step sees that the `CMakeLists.txt` is newer than the build files and runs the configure step first by itself. Running it by hand is also fine.
   :::

5. A game stops with an assertion in Debug and runs on in Release, and the condition is false in both. Which statement fits?

   - A. Release fixed the bug.
   - B. Release removed the check; the bug is still there.
   - C. The Release compiler found the error and repaired it.
   - D. The assert was wrong.

   :::answer{tests="configurations"}
   B. With `NDEBUG` defined, the assert expands to nothing, so the false condition goes unnoticed. A and C suggest that optimization corrects programs, which it does not. D may be true but is not shown by the difference.
   :::

## Practice

These exercises use the terminal you opened above, in the `hello` folder.

1. **Basic.** With the CMake project built, predict which files a build compiles again after `Greeting.cpp` changes, and which after `Greeting.h` changes. Then check with `touch` (Linux and macOS) or by saving the file in an editor, and `cmake --build build`.

   :::answer[Worked solution]{tests="build-steps cmake"}
   After `Greeting.cpp` changes, only `Greeting.cpp` is compiled, and the library and the program are linked again: 3 steps. After `Greeting.h` changes, both `Greeting.cpp` and `main.cpp` are compiled, since both include it, and the two links follow: 4 steps. The program still prints `Hello, Coin Run!`.
   :::

2. **Medium.** Create `Score.h` with the declaration `int ScoreFor(int coins);`. Make `main.cpp` include it and print `ScoreFor(5)`. Build without writing a `Score.cpp`. Read the error, say what stage printed it, and fix it.

   :::answer[Worked solution]{tests="errors"}
   Every file compiles, because the header made the promise, and the link stops with `undefined reference to 'ScoreFor(int)'` (or `LNK2019` on MSVC). The linker printed it. The fix is to write `Score.cpp` that includes `Score.h` and defines `int ScoreFor(int coins)`, then to compile it and add it to the link line, or to add it to the `add_executable` line of the `CMakeLists.txt`.
   :::

3. **Medium.** Write `stop.cpp`: it reads a whole number `coins` from :term[standard input]{id=standard-input}, asserts that it is not negative, and prints it. Build it with CMake in Debug and in Release, and feed it 5 and then -5 with `echo -5 | ./stop` (on Windows, `echo -5 | .\stop.exe` in the Command Prompt). Predict which of the four runs stops, and mind where each system chooses its configuration.

   :::answer[Worked solution]{tests="configurations cmake" solution="sketches/basics-build-stop.cpp"}
   Only the Debug run with -5 stops. A Release build defines `NDEBUG` and removes the check.

   Add the line `add_executable(stop stop.cpp)` to the `CMakeLists.txt` and run the program from its build folder; Visual Studio puts it in a `Debug` or `Release` folder inside. With Visual Studio, one build folder holds both configurations and `--config` picks one. With Ninja, use two folders, configured with `-DCMAKE_BUILD_TYPE=Debug` and `-DCMAKE_BUILD_TYPE=Release`. Here is a program that does it, with its output when nothing is piped in, so that `coins` stays 0:

   ```cpp sketch="basics-build-stop.cpp"
   #include <cassert>
   #include <iostream>

   int main()
   {
   	int coins = 0;
   	std::cin >> coins;

   	// Stops a Debug build for a negative number; a Release build removes this line.
   	assert(coins >= 0 && "coins cannot be negative");

   	std::cout << "coins: " << coins << "\n";
   	return 0;
   }
   ```

   1. **Line 10:** the check is false for a negative number, and it exists only where `NDEBUG` is not defined.
   2. **Line 12:** the print shows the number that passed the check.

   ```text output-of="basics-build-stop.cpp"
   coins: 0
   ```

   In a Debug build, `echo -5 | ./stop` stops with `Assertion failed: coins >= 0 && "coins cannot be negative", file stop.cpp, line 10`; the words differ between systems. A Release build prints `coins: -5`.

   In Windows PowerShell 5.1, the same pipe can send three bytes before the text, a byte order mark, when the console uses UTF-8. `std::cin` then reads no number, and every run prints `coins: 0`. The Command Prompt sends the text alone.
   :::

4. **Hard.** Turn `Greeting.cpp` into a static library `libgreeting.a` by hand (on Windows, `lib /OUT:greeting.lib Greeting.obj`). Add a second library `frame` with a function `Frame` that `Greeting.cpp` calls. On Linux, swap the two libraries on the link line and read the error. On Windows and macOS, whose linkers do not depend on the order, leave `frame` off the line instead and read that error.

   :::answer[Worked solution]{tests="libraries errors"}
   With the right order, `c++ main.o -L. -lgreeting -lframe -o hello` links and prints the framed greeting. With `-lframe -lgreeting` the linker of Linux stops with `undefined reference to 'Frame(...)'`, and it names `Greeting.o` inside `libgreeting.a` as the file that needs it. With `frame` left off, every linker gives the same kind of error: `unresolved external symbol` on MSVC, `Undefined symbols` on macOS.
   :::

5. **Hard.** Optional, on a project of the editor with scripts, such as the one that holds your `Playground`. Open the `CMakeLists.txt` the editor wrote in its `Scripts` folder and read it. Find the line that makes the script module and the comment that gives the build-by-hand command. Run that command in your terminal, and find the module file it produced.

   :::answer[Worked solution]{tests="cmake"}
   The file calls `find_package(StrataScriptCore ...)` and then `strata_add_script_module`, which makes a module library from every `.cpp` and `.h` file below the folder. Its comment gives two commands joined by `&&`: `cmake -S Scripts -B <build directory> -DSTRATA_ENGINE_DIR=<Strata folder>` and `cmake --build <build directory>`. Run them from the project folder, with a build folder of your choice outside `Scripts` and the folder of your Strata installation. The Command Prompt runs them as written; in Windows PowerShell 5.1, which has no `&&`, run them as two lines.

   The module is a `.dll`, `.so` or `.dylib` file under the build folder. The editor itself builds into `.strata/Scripts/Bin` with its own compiler and configuration, so use the editor for the copy that the game loads.
   :::

## Where the book uses it

- [The map of the engine](../core/map.md) builds on the compiler and linker: it names the engine's pieces by the libraries and programs they are built into.
- [Shared libraries in Strata](../scripting/shared-libraries.md) builds on shared and module libraries: it shows how a game loads its script module.
- [Script builds in the editor](../editor/script-builds.md) builds on CMake and configurations: it walks through the build that the editor starts for a script module.
- [Building Strata](../engineering/building.md) builds on the build steps and configurations: it builds the engine from source.

## Further reading

- Kitware, "CMake Tutorial": steps from one file to a project with libraries, tests and packages (beginner).
- Kitware, "CMake Reference Documentation": every command and variable (intermediate).
- John R. Levine, "Linkers and Loaders": how object files, libraries and loading work (advanced).
- Microsoft, "MSVC compiler options": every `cl` and `link` flag (intermediate).
