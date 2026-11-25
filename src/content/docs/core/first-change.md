---
id: core/first-change
title: "Your first engine change: build from source, change one thing, test it"
description: "Build Strata from its source code, add one small function to the engine, and prove it with a test that you watch pass and fail."
kind: tutorial
size: L
tracks: [E]
needs: [core/map, basics/cpp-classes, basics/git]
time: 120
learn:
  - id: source-build
    text: build Strata from source on your system, from the clone and its submodules to a running editor
  - id: configurations
    text: explain what Debug, Release and Dist keep and remove, and why Dist compiles the asserts out
  - id: header-change
    text: add a function to an engine header and predict when the build needs a new configure step
  - id: test-case
    text: write a test case in the right suite and run its suite alone with a filter
  - id: failing-test
    text: run a new test against broken code to show that the test can fail
since: 0.3.0
status: final
---

## What you will make

You will build Strata from its :term[source code]{id=source-code} on your own computer, add one small function to the engine,
`StringUtils::ToUpper`, and write the test that proves it works. At the end the engine's test program runs your test,
and you have watched it pass and fail.

::figure{id=result}

## What you need

- A computer with the :term[C++ build tools]{id=build-tools}, :term[CMake]{id=cmake} and :term[git]{id=git}, as [installing Strata](../start/install.md) describes, and a
  graphics driver for [Vulkan](../gpu/vulkan-nvrhi.md) 1.2 to start the editor.
- Time: the first build is the longest part, because it compiles the engine and every library it uses. Later builds
  compile only what your change touches.
- No project, sample or file to import. You change the engine itself: one :term[header file]{id=header-file} and one test file.
- If you already built Strata while installing it, keep that clone and skip step 1 of the first section. Step 2
  moves it to the commit this book describes.

:::::note[What a source build needs]

The :term[configure step]{id=configure-step} stops with an error when CMake is too old, a package is missing or [Slang](../gpu/shaders.md) cannot be fetched. An old
:term[compiler]{id=compiler} is not checked there: it fails later, while the build compiles.

- A :term[compiler]{id=compiler} for C++20 at least as new as Microsoft Visual C++ (MSVC) 19.40, GCC 13, Clang 17 or Apple Clang 15.
- CMake 3.25 or newer. `CMakeLists.txt` and `CMakePresets.json` both ask for that version.
- A network connection the first time. Strata compiles its :term[shaders]{id=shader} with [Slang](../gpu/shaders.md), which is no :term[submodule]{id=submodule}: the first
  configure step downloads one pinned release into a cache of your user account and checks its [SHA-256](../basics/data-formats.md) digest. On a
  computer without a network, download that release yourself and pass its folder as `-DSTRATA_SLANG_ROOT=<folder>`.
- The Vulkan software development kit is optional. The build needs none of it, because the Vulkan header files come
  as a submodule. Installing the kit adds the [validation layer](../gpu/vulkan-nvrhi.md), which reports misuse of the :term[graphics card]{id=gpu} in `Debug`
  builds.

::::tabs{sync=os}
:::tab[Windows]
Visual Studio 2026, for the :term[CMake preset]{id=cmake-preset} `windows`, or Visual Studio 2022, for the CMake
preset `windows-vs2022`, with its C++ desktop tools. Visual Studio brings the compiler and the build tool.
:::
:::tab[Linux]
Ninja, which the `linux` CMake preset builds with, and the development packages of the window systems and of the
file dialogs:

```sh
sudo apt-get install ninja-build libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev \
  libwayland-dev libxkbcommon-dev libgtk-3-dev
```

Without them, the configure step of [GLFW](windows-events.md) stops at the first missing header file, with an error that names the
package to install. The configure step of the file dialogs stops when it cannot find the package of `libgtk-3-dev`.
:::
:::tab[macOS]
Xcode's :term[command line]{id=terminal-command} tools for Apple Clang, and Ninja, which the `macos` CMake preset builds with. Vulkan runs on
Metal through a library that comes with the Vulkan kit for macOS, or with the packages `molten-vk` and
`vulkan-loader` that `brew install` installs.
:::
::::

:::::

You change two files of the engine. The rest of the tree you only build:

:::files[The two files of the change]

- `GameEngine/` your clone
  - `Strata/src/Strata/Core/`
    - **StringUtils.h**: small text functions; you add `ToUpper` here
  - `StrataTests/src/Core/`
    - **StringUtilsTests.cpp**: their tests; you add one test case here
  - `CMakeLists.txt`, `CMakePresets.json`: what the build is made of, and every CMake preset
  - …

:::

## Get the source at the book's commit

Every output this page shows comes from one commit of the engine. At a later commit, file lines and counts can
differ from the ones you read here. So the first section puts your clone at the same commit as the book. You need
three commands of git, which [git and its submodules](../basics/git.md) explains.

:::::steps

1. Clone the :term[repository]{id=repository} into a new folder. Open a terminal in the folder that should hold the clone.

   ```sh
   git clone https://github.com/2042Third/GameEngine.git
   cd GameEngine
   ```

   **You should see:** git counts and receives the objects. Then the folder `GameEngine` holds `CMakeLists.txt`,
   `Strata`, `StrataEditor`, `StrataTests` and the other folders of the engine.

   **If you do not see it:** when the terminal says that `git` is not a command, git is missing from your computer
   or from its path. Install it as [installing Strata](../start/install.md) says, and open a new terminal.

2. Create a branch at the commit this book describes. The commit is :value{key="engine.commit"}; copy it whole in
   place of `<commit>`.

   ```sh
   git switch -c first-change <commit>
   ```

   **You should see:** git reports that it switched to a new branch, `first-change`. Your work stays on that branch,
   and the branch `main` stays as it was.

   **If you do not see it:** when git says that the reference is not valid, the commit was cut short while copying.
   Copy it again; `git log -1` then shows the commit your branch starts from.

   **Why:** a branch of your own keeps your change apart from the engine's history, and `git diff` shows it at any
   time.

3. Fetch the third-party libraries. Strata keeps each of them, GLFW and EnTT among them, as a submodule at a pinned
   commit in `Strata/vendor/`.

   ```sh
   git submodule update --init --recursive --depth 1
   ```

   `--init` registers every submodule the repository lists, and `--recursive` also fetches submodules of submodules.
   `--depth 1` fetches only the pinned commit of each library instead of its whole history.

   **You should see:** one block of lines per library as git clones it, each ending with the path in `Strata/vendor/`
   and the commit it checked out. The repository pins 19 of them, and the library of the file dialogs brings one
   more of its own, which `--recursive` fetches.

   **If you do not see it:** when git stops with a network error, run the same command again. It fetches only the
   libraries that are still missing.

:::::

The configure step refuses to start without the submodules. Soon after it names the project, `CMakeLists.txt`
checks for one file of one library, `Strata/vendor/glfw/CMakeLists.txt`. When that file is missing, the configure
step stops at once with a message that names the fix. CMake breaks the message into short lines, and the command
stands between two `` ` `` marks:

```text
CMake Error at CMakeLists.txt:14 (message):
  Third-party submodules are missing.  Run `git submodule update --init
  --recursive --depth 1`.


-- Configuring incomplete, errors occurred!
```

Run the command of the message, which is the command of step 3, then the configure step again.

:::why[Stop at the first missing piece]
Without that check, CMake would read on into `Strata/vendor/CMakeLists.txt`, which adds each library from its folder
with `add_subdirectory`. The first empty folder would stop it there, with an error about that folder which names
neither submodules nor the command that fetches them. Strata checks one file early instead, and the message holds
the command that fixes the clone. The cost is small, and so is the cover:
the check looks at one library only, so a clone where only some submodules arrived passes it and fails later.
:::

## Build the engine and start the editor

A CMake preset is a named set of build settings in `CMakePresets.json`. Strata has one CMake preset per system for the configure step,
`windows`, `linux` and `macos`, and each writes its build into a folder of its own, `build/<preset>`. The configure
step reads the engine's CMake files and writes that build folder; the build step compiles and links. The two steps
are explained in [compiling and linking with CMake](../basics/build.md).

One build folder holds several configurations: each compiles the same code with other settings. You build `Debug` now, and the end of this section
compares it with the other two.

:::::steps

1. Run the configure step with the CMake preset of your system. Run it in the clone's folder, where
   `CMakePresets.json` is.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --preset windows
   ```

   With Visual Studio 2022, run `cmake --preset windows-vs2022`, and write `build/windows-vs2022` in place of
   `build/windows` in every later command.
   :::
   :::tab[Linux]

   ```sh
   cmake --preset linux
   ```

   The `linux` CMake preset uses the generator `Ninja Multi-Config`, which keeps every configuration in one build
   folder, as Visual Studio does.
   :::
   :::tab[macOS]

   ```sh
   cmake --preset macos
   ```

   :::
   ::::

   **You should see:** the log of the configure step. The first time, it prints `Downloading` and the name of the
   Slang archive. Every time, it prints a line that starts with `Slang 2026.20:` and names the path of the Slang
   compiler it uses. The last lines say that CMake wrote the build files, and name the
   folder `build/<preset>`.

   **If you do not see it:** read the first line that says `CMake Error`. "Third-party submodules are missing" means
   that step 3 of the first section did not finish. On Linux, a missing header file (`RandR headers not found`) or a
   missing `gtk+-3.0` means that a package of the box above is missing. A failed download of Slang needs the network
   once, or `STRATA_SLANG_ROOT`.

2. Build the `Debug` configuration of every program.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --build build/windows --config Debug --parallel
   ```

   The CMake preset `windows-debug` names the same folder and configuration, so
   `cmake --build --preset windows-debug --parallel` does the same.
   :::
   :::tab[Linux]

   ```sh
   cmake --build build/linux --config Debug --parallel
   ```

   The CMake preset `linux-debug` names the same folder and configuration, so
   `cmake --build --preset linux-debug` does the same.
   :::
   :::tab[macOS]

   ```sh
   cmake --build build/macos --config Debug --parallel
   ```

   :::
   ::::

   `--config Debug` chooses the configuration, and `--parallel` compiles several files at the same time.

   **You should see:** many lines of compiling, and at the end no line with `error`. The programs are in
   `build/<preset>/bin/Debug/`: `StrataEditor`, `StrataRuntime`, `StrataCLI` and the test program `StrataTests`. The
   libraries of the engine are in `build/<preset>/lib/`.

   **If you do not see it:** Strata builds its own code with warnings treated as errors, so a newer compiler that warns
   about something stops the build. Read the first `error` line: it names the file and the line. For an experiment of
   your own you may run the configure step with `-DSTRATA_WARNINGS_AS_ERRORS=OFF`. A change that others receive builds without
   warnings.

3. Start the editor you built, once. Ask it for its version first, then open its window.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   build\windows\bin\Debug\StrataEditor.exe --version | Out-Host
   build\windows\bin\Debug\StrataEditor.exe
   ```

   The editor is a windowed program, and PowerShell does not wait for those. `| Out-Host` makes it wait and print
   what the editor writes.
   :::
   :::tab[Linux]

   ```sh
   ./build/linux/bin/Debug/StrataEditor --version
   ./build/linux/bin/Debug/StrataEditor
   ```

   The first line prints and ends; the second keeps the terminal until you close the window.
   :::
   :::tab[macOS]

   ```sh
   ./build/macos/bin/Debug/StrataEditor --version
   ./build/macos/bin/Debug/StrataEditor
   ```

   :::
   ::::

   **You should see:** the first command prints one line and ends:

   ```text capture="editor-version"
   Strata Editor 0.8.0
   ```

   The second opens the editor's window with the heading "Welcome to Strata", the buttons **New Project** and
   **Open Sample...**, and the list **Recent projects**. Close the window: the next section changes the engine, and
   the build has to write this program again.

   **If you do not see it:** when no window opens, the editor reports why, in a message that names its log file. The
   usual cause is a graphics driver without Vulkan 1.2, or a graphics card that lacks a feature the :term[renderer]{id=renderer} needs.
   The log names the missing feature.

:::::

The build you made is `Debug`, one of Strata's three configurations. An assert is a line of code that checks
something that must always be true and stops the program when it is false. `Debug` compiles without making the code
faster, and it keeps every assert and log line, so that you can follow each line of code as it runs. `Release`
compiles the code to run fast and still keeps the asserts and the log: it is the build for everyday work and for
measuring speed.

**Dist** is Strata's shipping configuration: the compiled code of `Release` with the asserts compiled out. Strata's
releases ship it, and games are exported with it. Dist uses the compiler settings of `Release`; what differs is one
definition, `ST_DIST`, which only Dist sets. Code that tests that definition behaves differently: for example, it
has no asserts, and in scripting it does not count the calls of the [host functions](../scripting/host-api.md). Every configuration and option has its place in [building Strata](../engineering/building.md).

:::why[Why the shipping build drops the asserts]
An assert such as "this text is not empty" runs every time its line runs. Each check costs a little time, and a player cannot fix the program anyway, so Dist omits them. The cost is
that a mistake an assert would catch in `Debug` passes without a word in Dist. For that reason the release steps run
the tests in Dist as well, and a check that must stay in shipping builds is written as a verify, `ST_CORE_VERIFY`,
which Dist keeps.
:::

## Add `ToUpper` beside `ToLower`

Your change gives the engine a function that turns text into capital letters: `ToUpper("file.png")` returns
`"FILE.PNG"`. The engine has its opposite, `ToLower`, in `Strata/src/Strata/Core/StringUtils.h`. The script build of
the editor already has a `ToUpper` of its own in `ScriptBuild.cpp`, which no other file can call. A shared function in
the core library is what such code can use instead. The change is small, it lives in one header file, and it can be
tested without a window or a graphics card: good properties for a first change.

:::::steps

1. Open `Strata/src/Strata/Core/StringUtils.h` in your :term[code editor]{id=code-editor} and read `ToLower`, the function you copy.

   ```cpp src="Strata/src/Strata/Core/StringUtils.h#L12-L19"
   // ASCII case conversion for identifiers and file extensions; bytes outside ASCII (UTF-8 sequences) are unchanged.
   inline std::string ToLower(std::string_view text)
   {
   	std::string result(text);
   	for (char& character : result)
   		character = static_cast<char>(std::tolower(static_cast<unsigned char>(character)));
   	return result;
   }
   ```

   The comment states what the function promises: only the letters A to Z change, and every :term[byte]{id=byte} above 127 stays as
   it is. [UTF-8](../basics/bytes.md), the way Strata stores text, writes a letter such as é as two such bytes, so `ToLower` leaves it alone.

   `ToLower` takes a `std::string_view`, a view of text that does not copy it, and makes a copy, `result`, that it
   may change. The loop visits each `char` by reference and replaces it with its lower-case form. The inner cast to
   `unsigned char` matters: `std::tolower` expects a value from 0 to 255, and a `char` that holds a :term[byte]{id=byte} above 127
   can be negative.

   **You should see:** the comment, then the function, near the top of the file, inside
   `namespace Strata::StringUtils`.

   **If you do not see it:** you opened another file of the same name. The path starts at the clone's folder:
   `Strata`, then `src`, then `Strata` again.

2. Add `ToUpper` right below `ToLower`. Copy the lines that start with `+`; the others show where they go.

   ```diff src="book:tutorials/core/first-change.patch#hunk-1"
    		return result;
    	}
    
   +	// The capital letters of ToLower's conversion: ASCII letters become upper case, other bytes are unchanged.
   +	inline std::string ToUpper(std::string_view text)
   +	{
   +		std::string result(text);
   +		for (char& character : result)
   +			character = static_cast<char>(std::toupper(static_cast<unsigned char>(character)));
   +		return result;
   +	}
   +
    	inline bool EqualsIgnoreCase(std::string_view a, std::string_view b)
    	{
    		if (a.size() != b.size())
   ```

   1. **Line 4:** the comment states the promise, as the comment of `ToLower` does: the letters a to z change, and
      every other byte stays as it is.
   2. **Line 5:** `inline` lets 58 :term[source files]{id=source-file} include the header file without the linker meeting 58 definitions
      of one function.
   3. **Line 9:** the only difference from `ToLower`: `std::toupper` in place of `std::tolower`.

   **You should see:** your file has `ToUpper` between `ToLower` and `EqualsIgnoreCase`, with one tab at the start of
   each line, like its neighbours.

   **If you do not see it:** when the next step reports an error at these lines, compare them with the lines above. A
   missing `;` or brace is the usual cause.

3. Build again, with the same command as before.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --build build/windows --config Debug --parallel
   ```

   On Windows the editor must not be running while the build writes it.
   :::
   :::tab[Linux]

   ```sh
   cmake --build build/linux --config Debug --parallel
   ```

   Ninja prints one line per step, and the count of steps shows how much the change touched.
   :::
   :::tab[macOS]

   ```sh
   cmake --build build/macos --config Debug --parallel
   ```

   :::
   ::::

   **You should see:** a much shorter build than the first. The build compiles again each source file that includes
   `StringUtils.h`, then links the programs that use them, and it ends without an `error` line.

   **If you do not see it:** on Windows, a build while the editor still runs fails when it tries to write
   `StrataEditor.exe`, because Windows locks the file of a running program. Close the editor and build again.

:::::

The build did not need a new configure step, and the reason is how the build finds its files. Strata's CMake files
collect the source files with a pattern, `file(GLOB_RECURSE ... CONFIGURE_DEPENDS)`: every file under a folder whose
name ends in `.h`, `.cpp` or one of a few other endings of code. CMake follows that pattern at the configure step and writes the list it found into the build. You changed
the contents of a file that is already on the list, and the build tool notices a changed file by itself.

:::rule[Run the configure step again after adding or removing a source file]
A new file is not on the list until the configure step runs again (`cmake --preset <preset>`). The Visual Studio
generator even checks the pattern during the build, but that build still compiles with the old list, so a new file
would appear only in the build after it. A change inside files that exist, like yours, needs no new configure step.
The details are in [the CMake inside the build](../engineering/cmake.md).
:::

How many files did the build compile again? At the commit of this book, 58 source files include `StringUtils.h`
directly, and no header file includes it, so a change to it reaches those 58 and no others. Your build compiles those
of them that belong to your system and to the programs you build. A change to a header file that many other header
files include, such as the one with the engine's basic types, would make the build compile far more.

## Prove the change with a test

A build that finishes proves that your code compiles, not that it does what you meant. For that the engine has a
test program, `StrataTests`, which you built in the last section. Its tests are written with [doctest](../engineering/testing.md): a test case is
a named function of checks, and a test suite groups the test cases of one module under a name such as
`Core.StringUtils`. A `CHECK` compares two values. When they differ, doctest prints both and counts the check as
failed, and the test case continues with its next check.

`StringUtilsTests.cpp` already holds the suite of your file. Here is its first test case, the shape your test copies:

```cpp src="StrataTests/src/Core/StringUtilsTests.cpp#L9-L20"
TEST_SUITE("Core.StringUtils")
{
	TEST_CASE("Counts are formatted with their thousands separated")
	{
		CHECK(StringUtils::FormatThousands(0) == "0");
		CHECK(StringUtils::FormatThousands(999) == "999");
		CHECK(StringUtils::FormatThousands(1000) == "1,000");
		CHECK(StringUtils::FormatThousands(12345) == "12,345");
		CHECK(StringUtils::FormatThousands(123456) == "123,456");
		CHECK(StringUtils::FormatThousands(1000000) == "1,000,000");
		CHECK(StringUtils::FormatThousands(UINT64_MAX) == "18,446,744,073,709,551,615");
	}
```

1. **Line 9:** `TEST_SUITE` names the suite. Every test case inside its braces belongs to `Core.StringUtils`.
2. **Line 11:** `TEST_CASE` takes a sentence that says what must hold; doctest prints it when a check fails.
3. **Lines 13–19:** each `CHECK` calls the function with one input and compares the answer with a value worked out by
   hand, from the smallest case to the largest number the type can hold.

:::question[What do the names in capital letters do?]
`TEST_CASE` makes a function and registers it with doctest before `main` runs, with the kind of class work that
[classes and inheritance in C++](../basics/cpp-classes.md) introduced. You can use them without reading how they work.
:::

:::::steps

1. Add a test case of `ToUpper` at the end of the suite, inside its closing brace.

   ```diff src="book:tutorials/core/first-change.patch#hunk-2"
    		const std::string repaired = StringUtils::MakeValidUTF8("\xE6\x97 \x8F\xFF ok");
    		CHECK(StringUtils::MakeValidUTF8(repaired) == repaired);
    	}
   +
   +	TEST_CASE("Letters become capitals, digits and punctuation stay as they are")
   +	{
   +		CHECK(StringUtils::ToUpper("hello") == "HELLO");
   +		CHECK(StringUtils::ToUpper("Debug") == "DEBUG");
   +		CHECK(StringUtils::ToUpper("file.png") == "FILE.PNG");
   +		CHECK(StringUtils::ToUpper("x64 build 2") == "X64 BUILD 2");
   +	}
    }
   ```

   1. **Line 5:** the name says what the function promises, in words that a reader of a failure understands.
   2. **Lines 7–10:** four inputs, each answer worked out by hand. In `"x64 build 2"` only the six letters change;
      the digits 6, 4 and 2 and the spaces stay, so the answer is `"X64 BUILD 2"`.
   3. **Line 12:** the suite's closing brace. Your test case is above it, so it belongs to `Core.StringUtils`.

   **You should see:** three test cases in the file, the two that were there and yours, all inside the braces of
   `TEST_SUITE("Core.StringUtils")`.

   **If you do not see it:** a test case below the last brace belongs to no suite. Such a case is never run by
   `ctest`, and the test suite `Testing.Shards` fails and names it. Move it inside the braces.

2. Build the test program alone, then run your suite alone. `--target StrataTests` builds only that program and the
   libraries it needs. The filter `--test-suite` of doctest runs only the suites whose names match.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   cmake --build build/windows --config Debug --target StrataTests --parallel
   build\windows\bin\Debug\StrataTests.exe --test-suite=Core.StringUtils
   ```

   The test program is a console program, so PowerShell waits for it without help.
   :::
   :::tab[Linux]

   ```sh
   cmake --build build/linux --config Debug --target StrataTests --parallel
   ./build/linux/bin/Debug/StrataTests --test-suite=Core.StringUtils
   ```

   The filter is not case sensitive and takes `*` for any characters and `?` for one, so `core.stringutils` matches too.
   :::
   :::tab[macOS]

   ```sh
   cmake --build build/macos --config Debug --target StrataTests --parallel
   ./build/macos/bin/Debug/StrataTests --test-suite=Core.StringUtils
   ```

   :::
   ::::

   **You should see:** three lines that start with `[doctest]` end the output. Predict them before you run. The suite
   has three test cases, and its checks are the 7 of the first case, the 10 of the second and your 4: 21 in all. The
   first line counts the test cases, `3 | 3 passed | 0 failed`, and then a large number skipped: the test cases of
   every other suite, which the filter omitted. The second line counts the checks, `21 | 21 passed | 0 failed`, and
   the third reads `Status: SUCCESS!`.

   **If you do not see it:** when doctest counts 0 test cases, the filter matched no suite; compare its spelling with
   the name in `TEST_SUITE`. When it counts 2, the program was not built again after your change. Run the build
   command again and read its last lines.

3. Break `ToUpper` on purpose and run the suite again. In `StringUtils.h`, inside `ToUpper` only, change
   `std::toupper` to `std::tolower`. That is the mistake you would make by copying `ToLower` and forgetting one word.
   Then build and run with the two commands of the last step.

   **You should see:** predict it first. With the mistake, `ToUpper("hello")` returns `"hello"`, which differs from
   `"HELLO"`. The same holds for all four inputs, because each has a lower-case letter. So doctest reports each of
   your four checks with its file and line, the words `is NOT correct!` and a line `values:` with the two sides as
   the test saw them. The summary counts `3 | 2 passed | 1 failed` test cases and `21 | 17 passed | 4 failed`
   checks, and reads `Status: FAILURE!`.

   **If you do not see it:** when the run still passes, you changed `ToLower` instead of `ToUpper`, or the build did
   not run. When the build fails instead, the edit broke a name or a bracket: compare `ToUpper` with the lines of
   the change again.

   Now restore `std::toupper` in `ToUpper`, then build and run once more. The summary reads `Status: SUCCESS!` again.

4. Run the groups of tests with the label `core`. CMake comes with a test runner, the program `ctest`, which runs
   them.

   ::::tabs{sync=os}
   :::tab[Windows]

   ```powershell
   ctest --preset windows-debug -L core
   ```

   Add `-j 8` to run eight of them side by side.
   :::
   :::tab[Linux]

   ```sh
   ctest --preset linux-debug -L core
   ```

   Add `-j 8` to run eight of them side by side.
   :::
   :::tab[macOS]

   ```sh
   ctest --preset macos-debug -L core
   ```

   :::
   ::::

   The test program holds hundreds of suites. `ctest` runs most of them in 13 groups, each one run of `StrataTests`
   with a filter. All 13 groups carry the label `core`, which `-L core`
   selects. Your suite is in the group `StrataTests.Core.Core`, and one of its filters, `Core*`, matches every suite
   whose name starts with `Core`. How the groups are chosen is the subject of [the test program](../engineering/test-program.md).

   **You should see:** one line per group, each `Passed`, and a summary that all tests passed. The names on those
   lines are the groups that `ctest -N -L core` lists without running them:

   ```text capture="core-groups"
   …  Test  #1: StrataTests.Core.Core
   …  Test  #2: StrataTests.Core.Asset
   …  Test  #3: StrataTests.Core.Scene
   …  Test  #4: StrataTests.Core.SceneTiming
   …  Test  #5: StrataTests.Core.Systems
   …  Test  #6: StrataTests.Core.Settling
   …  Test  #7: StrataTests.Core.LoaderFaults
   …  Test  #8: StrataTests.Core.Renderer
   …  Test  #9: StrataTests.Core.Network
   …  Test #10: StrataTests.Core.Samples
   …  Test #11: StrataTests.Core.EditorUI
   …  Test #12: StrataTests.Core.EditorData
   …  Test #13: StrataTests.Core.Editor

   Total Tests: 13
   ```

   1. **Lines 1–13:** each line names one group, and the line of a run that names it ends in `Passed`.
   2. **Line 15:** the count of the groups with the label `core`, which the summary of a run counts too.

   **If you do not see it:** the CMake preset for tests prints the output of a test that fails. So the doctest lines of
   the failing group appear above the summary, with the file and line of each failed check. Fix the cause, or read
   [finding why a test fails or crashes](../core/debugging.md).

:::::

:::rule[A new test must fail without its change]
Run each new test once against code without the change, or with the change broken, and watch it fail. A test that
passes either way proves nothing: its checks may compare a value with itself, or test inputs that the mistake does
not touch. Strata's guide for its developers asks this of every regression test. The reasons, and the kinds of tests:
[testing an engine](../engineering/testing.md).
:::

Your change is complete: two files, a function and the test that proves it. `git diff` shows both, and `git status`
lists the two files as changed. How a change is reviewed and joins the engine is the subject of
[contributing to Strata](../engineering/contributing.md).

## Summary

- You built Strata from source: the clone at the book's commit, its 19 submodules, the CMake preset of your system and
  the `Debug` build, with the programs in `build/<preset>/bin/Debug/`. Then you started the editor you built.
- `Debug` keeps everything for finding mistakes, `Release` runs fast and keeps the asserts, and Dist, the shipping
  configuration, compiles the asserts out because players cannot act on them.
- A change inside a header file that exists needs no new configure step. Adding or removing a source file does,
  because the file lists are collected at the configure step.
- Your test case lives in the suite `Core.StringUtils`, and `--test-suite=Core.StringUtils` runs it alone.
- You broke the function on purpose and saw your test fail, so you know the test can catch the mistake it is for.

## Check yourself

1. You clone the engine and run `cmake --preset linux` at once. What happens, and why does the engine check this
   before anything else?

   :::answer{tests="source-build"}
   The configure step stops with the message that the third-party submodules are missing, which names the command
   `git submodule update --init --recursive --depth 1`. `git clone` alone leaves the submodule folders empty.
   `CMakeLists.txt` checks for the `CMakeLists.txt` of GLFW first, so that the error names the cause instead of an
   empty folder later.
   :::

2. A test passes in `Debug` and the same test fails in Dist. Name one difference between the two builds that can
   cause it.

   :::answer{tests="configurations"}
   Dist defines `ST_DIST`, which compiles every assert out and changes code that tests the definition, such as the
   call counts of the host functions. A test that expects an assert, or a counted call, behaves differently in Dist;
   such a test says so with `#if defined(ST_DIST)`. `Debug` also compiles without making the code faster, which can
   hide a bug that reads memory it should not.
   :::

3. You put a new function into a new header file, `TitleCase.h`, beside `StringUtils.h`, and include it from a test.
   Does the build need a new configure step? Would it for a change inside `StringUtils.h`?

   :::answer{tests="header-change"}
   Yes for the new file: the file lists come from a pattern that CMake follows only at the configure step, so run
   `cmake --preset <preset>` again. No for a change inside `StringUtils.h`: the file is on the list already, and the
   build tool sees that it changed.
   :::

4. A colleague writes their test case after the last closing brace of `StringUtilsTests.cpp`. The program builds.
   What goes wrong?

   :::answer{tests="test-case"}
   The test case belongs to no suite. No group that `ctest` runs holds it, and `--test-suite=Core.StringUtils` does not select
   it, so it never runs. The test suite `Testing.Shards` fails and names it.
   :::

5. With the mistake of the last section, `std::tolower` in `ToUpper`, which of these checks still passes:
   `ToUpper("123") == "123"`, `ToUpper("Debug") == "DEBUG"` or `ToUpper("A") == "A"`? What does that tell you about
   choosing inputs?

   :::answer{tests="failing-test"}
   `ToUpper("123") == "123"` passes, because digits have no case. `ToUpper("A") == "A"` fails, since the mistake
   turns `A` into `a`, and `ToUpper("Debug")` fails too. A check passes the mistake when the mistake leaves its input
   alone. So at least one input of a test has to reach the code the change adds: here, a lower-case letter.
   :::

## Exercises

1. **Basic.** Add two checks to your test case: one for empty text, and one for text with a letter outside a to z,
   such as `été`. The comment of `ToLower` promises that such bytes stay unchanged. Predict each answer before you run
   the suite.

   Hint: in C++ source, write `é` as its two [UTF-8](../basics/bytes.md) bytes, `\xC3\xA9`, so that the encoding of the file cannot change
   the test.

   :::answer{tests="test-case failing-test" solution="tutorials/core/first-change/exercise-1.patch"}
   The empty text has no characters, so `ToUpper("")` returns `""`. In `été` only the `t` is a letter from a to z.
   Each `é` is the bytes 195 and 169, which `std::toupper` leaves as they are, so the answer is `éTé`, written
   `"\xC3\xA9T\xC3\xA9"`. The two checks are:

   - `CHECK(StringUtils::ToUpper("") == "");`
   - `CHECK(StringUtils::ToUpper("\xC3\xA9t\xC3\xA9") == "\xC3\xA9T\xC3\xA9");`

   The suite then counts 23 checks, all passed. With the mistake of the last section, the empty check passes and the
   check of `été` fails, because `t` stays lower case. The worked solution is the patch of this exercise: the two
   checks alone, which apply on top of the change of the page.
   :::

2. **Medium.** Add `StringUtils::StartsWithIgnoreCase(text, prefix)` beside `EqualsIgnoreCase`. It returns true when
   `text` starts with `prefix`, whatever the case of their letters. Write its test case in the same suite, with at
   least one input that must give `false`.

   Hint: `StartsWith` in the same file shows the shape, and `EqualsIgnoreCase` compares without case. The input
   system has a copy of the same function of its own, in a :term[namespace]{id=namespace} without a name, in
   `Strata/src/Strata/Input/InputActionSet.cpp`. Leave it alone: one change at a time keeps a failure simple to place.

   :::answer{tests="header-change test-case" solution="tutorials/core/first-change/exercise-2.patch"}
   The function returns `text.size() >= prefix.size()` combined with `&&` and a call of `EqualsIgnoreCase` on the
   first `prefix.size()` characters of `text`. The size test comes first, because a text shorter than `prefix`
   cannot begin with it.

   The test case checks `"Gamepad.A"` with `"gamepad."`, `"KEY.SPACE"` with `"Key."`, and an
   empty `prefix`, which every text begins with. Two inputs must give `false`: `"Key"` with the longer `"Keyboard."`, and
   `"Mouse.Left"` with `"Key."`. `CHECK_FALSE` passes when its value is false. The new function lives in the header
   file, so the build needs no new configure step, and the suite counts 4 test cases. The worked solution applies on
   top of the change of the page, as the Basic exercise's does.
   :::

3. **Hard.** Put an assert into `ToUpper` on purpose. Make
   `ST_CORE_ASSERT(!text.empty(), "ToUpper was given empty text");` its first line, with
   `#include "Strata/Core/Assert.h"` at the top of `StringUtils.h`. Keep the empty check of the Basic exercise. Build
   and run the suite in `Debug`, then in Dist, and explain the difference.

   Hint: Dist has its own folder, `build/<preset>/bin/Dist/`, and its own build command, with `--config Dist`.

   :::answer{tests="configurations"}
   In `Debug` the empty check calls `ToUpper("")`, the condition of the assert is false, and the program logs a
   critical line. The line starts with `Assertion '!text.empty()' failed at` and names the file, the line and your
   message. Then the assert ends the program.

   On Windows, a `Debug` build first shows a message box that says `abort()` has been called. Once you close it,
   doctest reports your test case as crashed with `SIGABRT` and prints its summary, which reads `Status: FAILURE!`.
   On Linux and macOS, the test program prints `Fatal signal 6 in test case:` and the name of your test case, and
   ends without a summary. In Dist the same run passes all 23 checks. `Base.h` defines `ST_ENABLE_ASSERTS` only when `ST_DIST` is not defined, and
   without it `ST_CORE_ASSERT` compiles to nothing.

   Build Dist with `cmake --build build/<preset> --config Dist --target StrataTests --parallel` and run
   `build/<preset>/bin/Dist/StrataTests` with the same filter, or run `ctest --preset <preset>-dist -L core`. The
   lesson: an assert is for mistakes of programmers that must never happen, and it costs nothing in a shipped game.
   Empty text is a valid input, so the assert is wrong here. Remove it once you have seen both runs. This exercise has
   no worked solution to download: its change is the two lines the exercise gives, and its point is a run that fails.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/StringUtils.h`: `ToLower`, `EqualsIgnoreCase` and the other small text functions; the
  whole list is in [the core library's reference](../reference/core.md).
- `StrataTests/src/Core/StringUtilsTests.cpp`: the suite `Core.StringUtils`.
- `CMakeLists.txt`: the check for the submodules, and the build options such as `STRATA_WARNINGS_AS_ERRORS`.
- `CMakePresets.json`: the CMake presets of every system, for the configure step, the build step and the test step.
- `CMake/StrataConfigurations.cmake`: `Debug`, `Release` and `Dist`, and the folders the programs land in.
- `CMake/StrataSlang.cmake`: the pinned download of Slang at the first configure step.
- `StrataTests/CoreShards.json`: which group runs which suites.
- `CMake/StrataCompilerOptions.cmake`: the definition each configuration sets, the one of Dist among them.
- `Strata/src/Strata/Core/Assert.h` and `Base.h`: the asserts, and the lines that remove them from Dist.

## Further reading

- [CMake's manual, `cmake-presets`](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html): the format of
  `CMakePresets.json`, with a CMake preset for each step. Intermediate.
- [Pro Git, "Git Tools: Submodules"](https://git-scm.com/book/en/v2/Git-Tools-Submodules): what a submodule is, and
  how cloning, updating and pinning work. Beginner.
- [doctest, "Command line"](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): every filter
  and option of a doctest program, `--test-suite` and `--test-case` among them. Beginner.
- [The page of `std::toupper` in an online manual of C++](https://en.cppreference.com/w/cpp/string/byte/toupper): why the argument is cast
  to `unsigned char` first. Intermediate.
