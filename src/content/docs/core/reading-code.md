---
id: core/reading-code
title: "Finding your way in a large codebase"
description: "Follow a command-line option from its usage line to the engine code where it acts, and write the path down as files and lines."
kind: how-to
size: M
tracks: [E]
needs: [core/first-change, core/conventions]
time: 60
learn:
  - id: map
    text: find the folder of a module, its tests and its registration from the names in the repository's tree
  - id: search
    text: find the lines that hold a name, an option or a message with git grep and the code editor's jumps
  - id: trail
    text: trace a command-line option from its usage line to the code where it acts, written down as files and lines
  - id: history
    text: find the commit that wrote a line with git blame and git log -S, and read why it was written
since: 0.4.0
status: final
---

Strata's source is far too large to read from the first file to the last. This page shows how to find the file and the
line where something happens anyway. You start from a thing you can see, such as an option, a message or a label in
the editor, and follow it through the code. On the way you write down each file and line you pass, so that you, or
someone after you, can walk the same path again. Before you start:

- You built Strata from its source in the `Debug` configuration, as the [page on building and changing the engine](first-change.md)
  describes, and your clone has not moved since then.
- You know what the first letters of the engine's names mean (`m_`, `s_`, `c_`) from the
  [page on the code style](conventions.md).
- You have a terminal open in the top folder of your clone, and :term[git]{id=git} works in it.
- You have a :term[code editor]{id=code-editor} that understands C++ projects. Visual Studio reads the solution that
  :term[CMake]{id=cmake} wrote, a file that lists every part of the build. Other editors read `compile_commands.json`,
  such as Visual Studio Code with the `clangd` extension.

## What you need

A code editor can jump from a name to the line that defines it only when it knows how each file is built. CMake tells it
in one of two ways, and which one you have depends on the `cmake --preset` command you ran.

| Command | What CMake writes | Open it with |
| --- | --- | --- |
| `cmake --preset windows` or `windows-vs2022` | A Visual Studio solution in the build folder: `build/windows/Strata.slnx` with Visual Studio 2026 | Visual Studio: File, then Open, then "Project/Solution" |
| `cmake --preset linux`, `macos` or `windows-ninja` | `compile_commands.json` in the build folder, such as `build/linux/compile_commands.json` | An editor with `clangd`, pointed at that file |

The file `compile_commands.json` is a list with one entry per :term[source file]{id=source-file}: the folder it is built in and the exact
:term[compiler]{id=compiler} command that builds it. Strata asks CMake for it in `CMake/StrataConfigurations.cmake`, but only some generators, the kinds of build files CMake can write, produce it: Ninja is one.
The Visual Studio generator writes the solution instead, which holds the same knowledge.

## Why you cannot read it all

Count first. Without the third-party libraries and the samples, Strata's C++ source is about 1,340 files and 475,000
lines. There are 155,000 in the engine, 84,000 in the editor, 228,000 in the tests and 9,000 in the
:term[runtime]{id=runtime}, the command-line client and the script interface. Suppose you read a careful 1,000 lines an
hour. The whole source then takes 475 hours, or about twelve weeks of full working days, and by the end the first files
have changed.

The question this page answers takes about 25 lines in four files instead. You run the editor as
`StrataEditor --frames 3` and it stops after three frames: where in the code does that happen? You answer it with a
**trail**: the list of files and lines that leads from something you can see to the code where it acts, each line with
a few words on what happens there. A trail is the result of every search on this page, and it is what you hand to
someone who asks the same question.

:::tip[Keep the trail in a text file]
Open an empty text file before step 1 and add a line each time you find something. A trail on paper lets you continue where you
stopped.
:::

## Follow one option to its effect

:::::steps

1. Read the map: the tree of the :term[repository]{id=repository}. List the top folder of your clone. Each top folder holds one program or one
   kind of file.

   | Folder | What it holds |
   | --- | --- |
   | `Strata/` | The engine. `src/Strata/<Module>/` holds one folder per module, such as `Audio`, `Renderer` or `Scene`. `src/Platform/` holds code for one system or library each: `Windows`, `Posix`, `GLFW`, `Vulkan`, `NoWindow`. |
   | `StrataEditor/` | The editor. `src/Editor/` is its core without a user interface, `src/UI/` and `src/Panels/` draw it, and `src/EditorApplication.cpp` starts the program. |
   | `StrataRuntime/` | The program that plays an exported game. |
   | `StrataTests/` | The tests. `src/<Module>/` holds the tests of each module, with the module's name. |
   | `StrataCLI/`, `StrataScriptCore/` | The command-line client of the editor, and the interface that game scripts are written against. |
   | `Docs/`, `Tools/`, `CMake/`, `Samples/` | The documents, the helper scripts, the build's own files and the sample games. |

   Inside a module the file names repeat one pattern. In `Strata/src/Strata/Audio/`, `AudioComponents.h` holds the
   module's components, and `AudioRegistration.cpp` holds `RegisterAudioModule`, the function that tells the engine
   what the module adds. The tests of the module are in `StrataTests/src/Audio/`, in files that end in `Tests.cpp`.

   For your question the map already narrows the search. An option you type after `StrataEditor` belongs to the editor
   program, so its first line is under `StrataEditor/src/`, most likely in `EditorApplication.cpp`.

   **You should see:** the folders of the table, beside `AGENTS.md`, `CMakeLists.txt` and `CMakePresets.json`.

   **If you do not see it:** your terminal is in a folder below the top one. Run `git rev-parse --show-toplevel`, which prints the top
   folder of the clone you are in, and change to it.

2. Read the documents as maps. Strata's developers drew a second map for you. `AGENTS.md`, at the top of the tree, holds
   the rules of each area in short form. Its table "Where the details are" sends you, for each kind of change, to the
   section of `Docs/DeveloperGuide.md` that explains it. `Docs/README.md` is the index of the folder, with a line on what
   each document covers, and `Docs/Architecture.md` explains how the parts work together, one section per part.

   The table has no row for command-line options, so search the documents for the word instead. In `AGENTS.md`, the
   last rule of the section "Editor" says that the editor's options go into `c_Arguments`. In `Docs/Architecture.md`,
   the section `Application and frame loop` lists the steps of one frame. Its last line says that the frame is counted,
   and that `MaxFrames`, which `--frames` sets, closes the application.

   You now have two names to search for, `c_Arguments` and `MaxFrames`, and a claim to check. Documents can fall behind
   the code; where the two disagree, the code is right.

   **You should see:** the rule about `c_Arguments` in `AGENTS.md` and the line with `MaxFrames` in
   `Docs/Architecture.md`.

   **If you do not see it:** search each file with your editor's find (**Ctrl+F**) for `--frames` and for
   `c_Arguments`.

3. Search the code for the name. The command `git grep` searches every file that git tracks, and only those, so the
   build folder and its millions of generated lines stay out of the results. Start wide and narrow the search until
   the results fit on a screen.

   ```sh
   git grep -l -e --frames
   git grep -l -e '"--frames"'
   git grep -n -e '"--frames"' -- StrataEditor/src
   ```

   With `-l`, the first command prints only the names of the 43 files that contain `--frames` anywhere, comments
   included. The option `-e` marks the next word as the text to search for, so that git does not read `--frames`, which starts with dashes, as one of its own options. The second searches for the option with
   its double quotes, as C++ code writes it in a string, and finds 10 files. The third shows the matching lines with
   their numbers (`-n`), but only below `StrataEditor/src` (the paths after `--`):

   ```text
   StrataEditor/src/EditorApplication.cpp:73:			{ "--frames", "<count>", "Stop after this many frames" },
   StrataEditor/src/EditorApplication.cpp:107:			if (commandLine.HasFlag("--frames"))
   StrataEditor/src/EditorApplication.cpp:109:				const std::optional<int64_t> frames = commandLine.GetIntOption("--frames");
   StrataEditor/src/EditorApplication.cpp:315:		for (const char* scripted : { "--headless", "--no-gpu", "--frames", "--commands", "--quit-after-commands", "--window-size" })
   StrataEditor/src/EditorApplication.cpp:367:		options.RecentProjectsReadOnly = !options.CommandScript.empty() || commandLine.GetIntOption("--frames").has_value();
   StrataEditor/src/EditorApplication.cpp:406:			else if (!commandLine.GetIntOption("--frames"))
   StrataEditor/src/EditorApplication.cpp:424:		if (const std::optional<int64_t> frames = commandLine.GetIntOption("--frames"))
   ```

   Seven lines in one file, from 43 files: that is the point of narrowing. Line 73 is the usage line, a row of the list
   `c_Arguments`, from which the editor prints what `StrataEditor --help` shows. Lines 107 to 109 check the value, and line 424 reads it
   to use it. Write the first lines of your trail now: the file, the line numbers and a few words for each.

   **You should see:** the seven lines above.

   **If you do not see it:** in Windows PowerShell 5.1, the double quotes inside the single quotes are lost on their way
   to git, and the search finds every `--frames` again. Run the commands in Git Bash, which comes with Git for Windows.

4. Jump with "Go to Definition" and "Find All References". A search finds text; a jump finds what the compiler
   means by a name, which is why the code editor needed `compile_commands.json` or the solution. Open
   `StrataEditor/src/EditorApplication.cpp` at line 424 (in Visual Studio, **Ctrl+G** goes to a line).

   :::question[What is `std::optional<int64_t>`?]
   A value that may be missing: it holds a whole number or nothing. The [page on modern C++](../basics/cpp-modern.md)
   explains it; here, `if (frames)` is true only when the option was given with a number, and `*frames` is that number.
   :::

   The lines around 424 take the number and store it. Watch the name on the left of the `=` on line 425: it is the field
   that receives the count.

   ```cpp src="StrataEditor/src/EditorApplication.cpp#L424-L431"
   if (const std::optional<int64_t> frames = commandLine.GetIntOption("--frames"))
   	specification.MaxFrames = static_cast<uint64_t>(*frames);
   options.MaxFrames = specification.MaxFrames;
   options.Headless = specification.Headless;
   // The project opens at once and its assets are scanned in the background, so that the automation session is published
   // within the startup (StrataCLI launch waits for the scan and the start scene); a person's window shows the start scene
   // loading. Scripted runs start with it open.
   options.OpenStartSceneInBackground = !options.MaxFrames && options.CommandScript.empty();
   ```

   `GetIntOption("--frames")` returns the number after `--frames`, or nothing when the option is absent or its value is
   not a whole number. When there is a number, line 425 stores it in `specification.MaxFrames`. Right-click `MaxFrames`
   and choose "Go to Definition". The editor opens the :term[struct]{id=struct} `ApplicationSpecification`, which a program fills to
   describe itself before the engine starts it:

   ```cpp src="Strata/src/Strata/Core/Application.h#L40-L45"
   JobSystemSpecification Jobs;
   std::optional<uint64_t> MaxFrames; // Close automatically after this many frames (automation, tests)
   float MaxTimestep = 0.25f;         // Clamp for long frames (breakpoints, loading hitches)
   // Frames per second the main loop does not exceed (0: unlimited). Headless applications have no vsync to pace
   // them and would otherwise keep a CPU core busy.
   uint32_t MaxFrameRate = 0;
   ```

   The comment on line 41 says what the field is for: the application closes by itself after that many frames. Now
   right-click `MaxFrames` on line 41 and choose "Find All References". Among the uses in the editor and the tests,
   one reads the field inside the engine: `Strata/src/Strata/Core/Application.cpp`, line 262. The same answer comes
   from a search for the whole word (`-w`) in the engine's folder:

   ```sh
   git grep -n -w MaxFrames -- Strata/src
   ```

   The search prints two lines: the definition in `Application.h` on line 41 and the check in `Application.cpp` on line 262.
   Without `-w` the search would also find names that contain the word, such as `GetMaxFramesInFlight`.

   **You should see:** the definition on line 41 of `Application.h`, and a use on line 262 of `Application.cpp`.

   **If you do not see it:** the code editor has not read the build. In Visual Studio, open the solution, not the
   folder; with `clangd`, point it at the build folder that holds `compile_commands.json`, then wait until it has read
   the files.

5. Write down the trail, and close its gaps. You know where the count is stored and where it is read, but not how the
   program gets from one to the other. Scroll up from line 424 to the start of its function,
   `CreateApplication`, and search for its caller: "Find All References" on its name, or `git grep -n -w CreateApplication -- Strata/src`.

   The search prints ten lines: eight comments, the declaration on line 30 of `ApplicationLaunch.h`, and the call, which
   ends in `CreateApplication(commandLine);`, on line 25 of `Strata/src/Strata/Engine/EntryPoint.h`. That file holds
   `main`, the first function of the editor and of the runtime. Read the order in which it does things:

   ```cpp src="Strata/src/Strata/Engine/EntryPoint.h#L16-L35"
   int main(int argc, char** argv)
   {
   	Strata::CommandLine commandLine(argc, argv);
   	// Before anything prints or the log opens its console sink: output reaches pipes, and the terminals of Console runs, as
   	// from a console program.
   	Strata::Platform::ConnectStandardStreams(Strata::GetProgramRun(commandLine));
   	// Ctrl+C in that terminal (or a termination signal) ends the run in order, through the main loop.
   	Strata::Platform::InstallInterruptHandler();

   	std::optional<Strata::ApplicationLaunch> launch = Strata::CreateApplication(commandLine);
   	if (!launch || !launch->Create)
   		return Strata::Application::GetStartupExitCode();

   	// The composition root, before anything touches a registry: the application, its layers and its modules all may.
   	Strata::Engine::RegisterBuiltinModules(launch->Registration);

   	Strata::Scope<Strata::Application> application = launch->Create();
   	if (!application)
   		return Strata::Application::GetStartupExitCode();
   	application->Run();
   ```

   1. **Line 18:** the words you typed after the program's name become a `CommandLine`, the object that line 424 asked
      for `--frames`.
   2. **Line 25:** `CreateApplication` is the editor's own function in `EditorApplication.cpp`. It checks the options,
      fills the `ApplicationSpecification` and returns a way to make the application.
   3. **Lines 32–35:** the application is made with that specification, and `Run` starts the loop that runs frame after
      frame until something stops it.

   The last link of the trail is in `Run`. Find the lines that count frames, and look at the condition that compares
   the count with `MaxFrames`:

   ```cpp src="Strata/src/Strata/Core/Application.cpp#L259-L264"
   if (frameRan)
   {
   	m_FrameCount++;
   	if (m_Specification.MaxFrames && m_FrameCount >= *m_Specification.MaxFrames)
   		m_Running = false;
   }
   ```

   After each frame that ran, the count `m_FrameCount` grows by one. When the program asked for a limit and the count
   reached it, `m_Running` becomes false, and the loop `while (m_Running)` ends. A frame the engine skipped, for example
   while the window is minimized, does not count, so `--frames 3` means three frames that ran, not three turns of the
   loop. Your trail now reads from the option to its effect:

   ```text
   Question: where does --frames N stop the editor?
   1. StrataEditor/src/EditorApplication.cpp:73        usage line: --frames <count>
   2. StrataEditor/src/EditorApplication.cpp:107-111   CheckValues refuses a count that is not positive
   3. StrataEditor/src/EditorApplication.cpp:424-425   the count goes into ApplicationSpecification::MaxFrames
   4. Strata/src/Strata/Engine/EntryPoint.h:25-35      main: CreateApplication, then Run
   5. Strata/src/Strata/Core/Application.h:41          MaxFrames, an optional count
   6. Strata/src/Strata/Core/Application.cpp:259-263   Run counts frames that ran; at MaxFrames the loop ends
   ```

   **You should see:** a trail of six lines in which each line leads to the next.

   **If you do not see it:** a link is missing where you cannot say how one line reaches the next. Ask "Find All
   References" on the name that the two lines share.

6. Read the tests of what you found. A test states what the code must do, with exact values, and the build checks it
   every time, so it is the most exact description there is. The tests of the `Core` module are in
   `StrataTests/src/Core/`; search them for the function from line 424, `GetIntOption`:

   ```sh
   git grep -n -w GetIntOption -- StrataTests/src/Core
   ```

   The search leads to `CoreTests.cpp`, where one test reads an option the way `--frames` is read. `CHECK` fails the
   test when its condition is false, and `CHECK_FALSE` when it is true. Look at what the test expects for a good number
   and for a bad one:

   ```cpp src="StrataTests/src/Core/CoreTests.cpp#L236-L245"
   TEST_CASE("CommandLine parses flags and options")
   {
   	CommandLine commandLine(std::vector<std::string> { "app", "--headless", "--project", "Game/Game.stproj", "--frames=120", "--bad=12x" });
   	CHECK(commandLine.HasFlag("--headless"));
   	CHECK_FALSE(commandLine.HasFlag("--missing"));
   	CHECK(commandLine.GetOption("--project").value() == "Game/Game.stproj");
   	CHECK(commandLine.GetIntOption("--frames").value() == 120);
   	CHECK_FALSE(commandLine.GetIntOption("--bad").has_value());
   	CHECK_FALSE(commandLine.GetOption("--missing").has_value());
   }
   ```

   1. **Line 238:** the test makes a :term[command line]{id=terminal-command} as a program would receive it, with `--frames=120` written with an
      equals sign, and `--bad=12x`.

   2. **Lines 242–243:** `--frames` gives the number 120; `12x` is not a whole number, so `GetIntOption` gives nothing.
      That is why the editor's check on line 110 must ask whether there is a value at all.

   The editor's own behaviour has a test too, which starts the built editor as a separate program. In
   `StrataTests/src/Editor/EditorAutomationProcessTests.cpp`, the test `Editor automation options are checked at start-up` runs the editor with `--frames abc` and `--frames=0`, among others, and expects :term[exit code]{id=exit-code} 3 and the usage
   text each time. Run the first test alone with its name, from the top of the clone:

   ```sh
   build/linux/bin/Debug/StrataTests --test-case="CommandLine parses flags and options"
   ```

   The path is the Linux one. On Windows the program is `build/windows/bin/Debug/StrataTests.exe`, and on macOS
   `build/macos/bin/Debug/StrataTests`; the option after it stays the same.

   **You should see:** a summary that reports one test case passed and none failed.

   **If you do not see it:** if the program is missing, build the `Debug` configuration first, as in the
   [page on building and changing the engine](first-change.md). If no test case ran, the name in the quotes differs
   from the test's: copy it from `CoreTests.cpp`.

7. Ask the history why. The code tells you what happens; the history tells you why someone made it so. The command
   `git blame` prints, for each line, the commit that last changed it. Ask it about lines 424 and 425, without the
   names and dates (`-s`):

   ```sh
   git blame -s -L 424,425 -- StrataEditor/src/EditorApplication.cpp
   ```

   Each line of the answer starts with the short name of a commit, then the line's number and its text:

   ```text
   d40f9a03f 424) 		if (const std::optional<int64_t> frames = commandLine.GetIntOption("--frames"))
   1d5baba26 425) 			specification.MaxFrames = static_cast<uint64_t>(*frames);
   ```

   Line 425 dates from one of the first commits, the one that added the editor's first shell. Line 424 changed later: run
   `git show d40f9a03` to read that commit's message and its changes. It says that `--frames 0` and `--frames abc` were
   once ignored. A scripted run with a wrong value then had no frame limit, so it did not end until the tool that started it stopped waiting. Since that commit, the editor
   refuses such a value before anything starts, with exit code 3 and the usage text.

   The command `git log -S` asks the other way round: which commits added or removed a piece of text. Search for the
   words of the error message:

   ```sh
   git log --oneline -S "positive number of frames" -- StrataEditor/src/EditorApplication.cpp
   ```

   The command prints one commit, `d40f9a03`, the same one: the message arrived with the check. Add the reason to your trail as
   its last line.

   **You should see:** the two lines of `git blame` above, and one commit from `git log -S`.

   **If you do not see it:** your clone is at another commit, or `git clone --depth 1` made it, and it holds no history.
   Run `git fetch --unshallow` to get the history, then try again.

:::::

:::rule[Options go into the list the usage line comes from]
The engine's rules say that every command-line option of the editor goes into `c_Arguments`. The same list prints the
usage text and decides which arguments are known, so the editor refuses an option missing from it at start, with exit code 3.
For a reader, the rule means that `c_Arguments` is where the trail of any editor option starts. The
[page on the first frame](first-frame.md) explains what `CommandLine` and the specification do in full.
:::

## Result

You have a trail of seven lines, from the usage line of `--frames` to the line of `Application::Run` that ends the loop,
and the commit that explains the check. Someone who reads it can open each file at its line and see the same thing you
saw, without searching. The picture below draws the same trail; read it from the top.

```mermaid caption="The trail of the frames option, from the line you type to the end of the loop." alt="Six boxes in a column: the command line, the check of its values, the specification, the main function, the frame loop, and the end of the loop when the count is reached."
flowchart TD
    A["StrataEditor --frames 3"] --> B["EditorApplication.cpp:107-111<br/>CheckValues"]
    B --> C["EditorApplication.cpp:424-425<br/>specification.MaxFrames = 3"]
    C --> D["EntryPoint.h:25-35<br/>main: CreateApplication, then Run"]
    D --> E["Application.cpp:259-261<br/>a frame ran: m_FrameCount++"]
    E --> F["Application.cpp:262-263<br/>count reached: m_Running = false"]
```

## Variations

### From a log message to the code that logs it

Search for the part of the message that never changes. A message such as "Interrupted (Ctrl+C or a request to
terminate): closing" is written in the code exactly so, and `git grep -n -F "Interrupted (Ctrl"` finds it on line 269
of `Strata/src/Strata/Core/Application.cpp`, and in two tests that expect it. The option `-F` searches for the text as
written, so that `(` means a bracket and nothing more. Many messages hold values that the code puts in, written `{}` in
the source. Omit those parts from your search: search for the words between them.

### From a label in the editor to the command it runs

Search for the label in quotes, below `StrataEditor/src`. The menu item **File ▸ New Scene** is drawn on line 1771 of
`StrataEditor/src/EditorLayer.cpp`, and the next line runs the editor command `scene.new` once the person has answered about changes not yet saved. Search for `"scene.new"`
below `StrataEditor/src/Editor` to find where the command is registered: line 379 of `EditorSceneCommands.cpp`. From
there, the trail continues into the command's own code.

### From a runtime option to its effect

The runtime has options of its own, in `StrataRuntime/src/RuntimeApplication.cpp`. The trail of `--seconds` starts at
its usage line (line 346) and its check (lines 392 to 394). It does not end in `MaxFrames`. On lines 189 to 194, the
runtime closes the application at the first frame by which the game has played that many seconds of game time, as
`GameRuntime::GetPlayedSeconds` counts them. Two options that look alike can end on different trails.

### A call stack as a trail

Your code editor can write a trail for you. Visual Studio and editors like it can run a program and stop it at a line
you choose. Choose line 259 of `Application.cpp`, then start the editor that way with
`--no-gpu --no-automation --frames 3`. When the program stops there, the editor shows the
[call stack](../basics/debugging.md), the list of functions that called each other to reach the line, from `main`
down to `Application::Run`. The [page on the engine's tools for finding bugs](debugging.md) shows how
to read it.

Following a click in the editor all the way to a pixel on the screen needs later parts of the book. It is an
exercise of the [page that plans the book's last project](../capstone/plan.md).

## Summary

- The tree is a map. Each module has a folder below `Strata/src/Strata/` and its tests a folder of the same name below
  `StrataTests/src/`; its registration is a file such as `AudioRegistration.cpp`, and each program has a top folder.
- `git grep` finds text in the tracked files; narrow it with quotes, `-w` and paths, then jump with "Go to
  Definition" and "Find All References".
- A trail of files and lines leads from the `--frames` usage line through `ApplicationSpecification::MaxFrames` to the
  frame count that ends `Application::Run`.
- `git blame` names the commit that last changed a line and `git log -S` the commits that added or removed a text;
  their messages say why.

## Check yourself

1. A run of the runtime ends with the log line "The game played 10.017 s of game time in 601 frames: stopping". A
   search for that whole line finds nothing. Why, and what do you search for instead?

   :::answer{tests="search"}
   The seconds and the count are values the code puts in, so the source holds `{}` where your line holds numbers.
   Search for a part that never changes, such as `"s of game time in"`. It leads to line 193 of
   `StrataRuntime/src/RuntimeApplication.cpp`.
   :::

2. Which folder holds the tests of the physics module, and in which file is its registration function?

   :::answer{tests="map"}
   The tests are in `StrataTests/src/Physics/`. The registration function, `RegisterPhysicsModule`, is in
   `Strata/src/Strata/Physics/PhysicsRegistration.cpp`, by the same pattern as `RegisterAudioModule`.
   :::

3. Predict what `StrataEditor --frames 0` does, from the trail you wrote.

   :::answer{tests="trail"}
   The editor never starts. `CheckValues` finds that the count is not positive and returns "--frames expects a
   positive number of frames"; `CreateApplication` prints that message and the usage text, and the program ends with
   exit code 3.
   :::

4. You start a windowed editor with `--frames 100` and minimize the window at once. Does the loop in `Run` end after
   100 turns?

   :::answer{tests="trail"}
   Not always. `Run` counts only frames that ran; while the window is minimized, frames are skipped and not counted, so
   the loop turns more than 100 times before the count reaches 100.
   :::

5. `git blame` shows that a line you care about comes from a commit that only changed the spacing of the whole file. How do you
   find the commit that really wrote it?

   :::answer{tests="history"}
   Search the history for the line's text with `git log -S "<a piece of the line>" -- <file>`: the oldest commit it
   lists is the one that added the text. You can also run `git blame` on the commit before that one, written
   `<commit>^`, to see who wrote the line before it.
   :::

## Exercises

1. **Basic.** Early in their logs, the editor and the runtime both write a line that starts with `Engine modules:` and names the
   modules it registered. Find the code that writes it with `git grep`, follow it to the function that holds it and to
   the place where that function is called, and write the trail down as files and lines.

   :::answer[Worked solution]{tests="search trail"}
   `git grep -n "Engine modules:"` finds four lines: three in `AGENTS.md`, `Docs/DeveloperGuide.md` and
   `Docs/Roadmap.md`, which use the words as the label of a rule or an item, and one in code. The code is line 172 of
   `Strata/src/Strata/Engine/BuiltinModules.cpp`, an `ST_CORE_INFO` call whose `{}` parts are filled with the names.
   Scrolling up, or the code editor's outline, shows that the line is inside `RegisterBuiltinModules`, which starts on
   line 118. "Find All References" on that name, or `git grep -n -w RegisterBuiltinModules -- Strata/src`, leads to
   line 30 of `Strata/src/Strata/Engine/EntryPoint.h`, where `main` calls it before it makes the application. The
   trail:

   ```text
   Question: where does the line "Engine modules: ..." come from?
   1. Strata/src/Strata/Engine/BuiltinModules.cpp:172   ST_CORE_INFO("Engine modules: {}. ...")
   2. Strata/src/Strata/Engine/BuiltinModules.cpp:118   inside RegisterBuiltinModules
   3. Strata/src/Strata/Engine/EntryPoint.h:30          main calls it, before the application is made
   ```

   The line comes from the engine, not the editor, which is why the runtime writes it too.

   :::

2. **Medium.** The editor's option `--idle-timeout <seconds>` closes the editor after that long without a connected
   client. Follow it from its usage line to the line that closes the editor, and write the trail down.

   :::answer{tests="search trail"}
   A search for `'"--idle-timeout"'` below `StrataEditor/src` gives the start; a search of the whole tree also finds
   the command-line client's option of the same name in `StrataCLI/`, which is another trail. The editor's trail:

   ```text
   Question: where does --idle-timeout close the editor?
   1. StrataEditor/src/EditorApplication.cpp:83        usage line
   2. StrataEditor/src/EditorApplication.cpp:119-123   CheckValues: 0 to a week, 0 means never
   3. StrataEditor/src/EditorApplication.cpp:378-379   the seconds go into EditorOptions::IdleTimeout
   4. StrataEditor/src/EditorLayer.cpp:693             passed on to the automation's specification
   5. StrataEditor/src/Editor/EditorAutomation.h:38-40 EditorAutomationSpecification::IdleTimeout
   6. StrataEditor/src/Editor/EditorAutomation.cpp:191-196  HasIdledOut: no client for that long
   7. StrataEditor/src/EditorLayer.cpp:966-972         logs a warning and closes the editor
   ```

   The test `The idle timeout runs while no client is connected and nothing is pending`, in
   `StrataTests/src/Editor/EditorAutomationTests.cpp`, checks `HasIdledOut` with a limit of 300 ms.
   :::

3. **Hard.** A headless editor runs at most 60 [frames per second](frame-loop.md), because of `c_HeadlessFrameRate`. Ask the history why
   with `git log -S` and `git blame`, down to the commit that set the cap, and write down what its message says.

   :::answer{tests="history"}
   `git blame -s -L 42,42 -- StrataEditor/src/EditorApplication.cpp` shows that the constant comes from commit
   `d9116fc5`, and so do lines 392 and 393, which apply it. `git log --oneline -S c_HeadlessFrameRate` without a path
   lists four commits, newest first, because later commits used the name in other files; with
   `-- StrataEditor/src/EditorApplication.cpp` it lists only `d9116fc5`, "Pace the frames of headless applications".
   Its message explains that a program without a window has nothing that paces it to the screen, so its loop ran as fast as it could
   and kept one core of the processor busy. That mattered once a headless editor stayed open to wait for requests from tools.
   The cap of 60 also makes a counted frame about as long as a frame of a game.
   :::

## Where it lives in Strata

- `AGENTS.md`, `Docs/README.md`, `Docs/DeveloperGuide.md` (section "Repository layout") and `Docs/Architecture.md`
  (section "Application and :term[frame loop]{id=game-loop}"): the maps.
- `StrataEditor/src/EditorApplication.cpp`: `c_Arguments`, `CheckValues` and `CreateApplication`, the editor's options.
- `Strata/src/Strata/Engine/EntryPoint.h`: `main`, the order in which every program starts.
- `Strata/src/Strata/Core/Application.h` and `Application.cpp`: `ApplicationSpecification::MaxFrames` and
  `Application::Run`.
- `StrataTests/src/Core/CoreTests.cpp` and `StrataTests/src/Editor/EditorAutomationProcessTests.cpp`: the tests of the
  command line and of the editor's options.
- `CMake/StrataConfigurations.cmake`: the request for `compile_commands.json`.

## Further reading

- [Git documentation, `git grep`](https://git-scm.com/docs/git-grep): every option of the search used on this page,
  with examples. Beginner.
- [Git documentation, `git blame`](https://git-scm.com/docs/git-blame): how to blame a range of lines, or a file as it
  was at an older commit. Beginner.
- [Git documentation, `git log`](https://git-scm.com/docs/git-log): the options `-S` and `-G`, which search the
  changes of every commit for a text. Intermediate.
- [`clangd`, "Getting started"](https://clangd.llvm.org/installation): how a code editor reads `compile_commands.json`
  to jump between definitions and references. Intermediate.
- Diomidis Spinellis, *Code Reading: The Open Source Perspective* (2003): a whole book on reading
  large programs written by others, with examples from real projects. Intermediate.
