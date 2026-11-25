---
id: editor/script-builds
title: "Building scripts from the editor: toolchains, CMake, diagnostics"
description: "How the editor finds a C++ toolchain, runs CMake without blocking a frame, shows each error at its file and line, and builds before Play."
kind: internals
size: L
tracks: [E]
needs: [editor/play-mode, scripting/hot-reload, basics/build]
time: 90
learn:
  - id: one-build
    text: explain how one script build runs in child processes without blocking a frame
  - id: toolchain
    text: explain how the editor picks a toolchain, and what it reports when none exists
  - id: configure-rule
    text: predict when a build removes its tree, configures again or only builds, and where the tree lives
  - id: diagnostics
    text: explain how a build log becomes diagnostics and why a failed build always names its cause
  - id: play-build
    text: trace how play.start decides to build, waits for the build and ends
since: 0.3.0
status: final
---

When a game maker changes a script and presses Play, the editor must turn the script's C++ into a module before the game runs, with a :term[compiler]{id=compiler} it may have to find on this machine. It must do that while the window keeps drawing, and it must show every :term[compiler error]{id=compile-error} at its file and line. The `ScriptBuilder` class does the work: it runs :term[CMake]{id=cmake} in child processes, one build at a time, and polls them once per frame. This page follows one build from the press of Play to the loaded module. It omits the child processes themselves, the module's binary interface and the drawing of the Problems panel, the editor's list of build errors and warnings.

## The problem and how engines solve it

Think of the person at the keyboard. They fix one line, press Play, and wait. Every second the window freezes is a second they suspect a crash. Every error shown as a wall of compiler text is a search for one line in hundreds. Four first answers each fail in a way you can measure.

The first answer is to build on the :term[main thread]{id=main-thread}. The call returns when the compiler is done, so a build of 20 seconds is 1,200 frames at 60 :term[frames per second]{id=frame-rate} that never draw. The :term[operating system]{id=operating-system} may even mark the window as not responding. The second answer is to run the CMake :term[configure step]{id=configure-step} every time. That step reads every build file and, on Windows, writes every project file again, so each press of Play pays seconds for work that rarely changes anything.

The third answer is the opposite: configure once and never again. Visual Studio compiles every project the way it stood when CMake configured it, so a new `.cpp` file added later is missing from the module, and the class in it never appears. The fourth answer is to show the raw build log. The cause of a failure is one line among hundreds, and a failure such as a missing compiler may print nothing useful at all.

Engines that compile game code meet the same four problems and answer in a few ways. Some run the compiler in a background process and swap the result into the running program. Some ship their own compiler, so the answer never depends on the machine. Some avoid compiling on the person's machine by using a scripting language that the engine reads while it runs. Each choice moves the cost somewhere else, and the table near the end of this page lists them against Strata's choice.

Strata keeps the compiler out of the engine and out of the way. :term[Game logic]{id=game-logic} is C++ in a module that talks to the engine only through a C interface, so any compiler of the platform can build it. The editor therefore drives an ordinary CMake build in child processes. The rest of this page is about doing that well: finding the tools, deciding how much to rebuild, reading the result and tying it to Play.

## The map

The diagram shows one build. Solid arrows are steps of the main thread and the processes it watches. The dashed arrows lead through the :term[toolchain]{id=build-tools} search, which runs on a worker thread. It happens only when the editor must find its tools: in an installed editor, or when a tool baked into it is gone.

```mermaid caption="One script build from Play to the loaded module, with the thread that runs each step." alt="A flow of boxes. Play checks the sources and starts the build. An optional search for tools runs on a worker thread. A configure process and a build process follow, and then the module loads and a toast reports it."
flowchart LR
  A["play.start / script.build<br/>main thread"] --> B["GetPlayBuildReason<br/>sources vs last build"]
  B --> C["ScriptBuilder::Start<br/>one build at a time"]
  C -.-> D["FindingToolchain<br/>I/O job"]
  D -.-> E
  C --> E["Configuring<br/>cmake child process"]
  E --> F["Building<br/>cmake --build child process"]
  F --> G["Finish<br/>diagnostics, result"]
  G --> H["OnScriptBuildFinished<br/>load or hot reload, toast"]
```

These files own the parts. `StrataEditor/src/Editor/ScriptBuild.cpp` holds the builder, the build tree rules, the presets and the log :term[parser]{id=parser}, and `StrataEditor/src/Editor/ScriptToolchain.cpp` finds tools on the machine. `StrataEditor/src/Editor/ScriptSources.cpp` lists and compares the script folder. `StrataEditor/src/Editor/EditorContext.cpp` decides when to build and what happens after. The commands `play.start`, `script.build` and `script.status` live in `StrataEditor/src/Editor/Commands/PlayCommands.cpp` and `StrataEditor/src/Editor/EditorScriptCommands.cpp`.

## The contract

A caller, whether a menu, a command or `play.start`, may rely on these rules. Each has its reason.

- **One build at a time.** A second request fails while one runs, with the number of the running build. Two builds in one tree would corrupt each other, and one result is easier to reason about than two.
- **The main thread owns the builder.** `ScriptBuilder::Update` runs once per frame and never waits: it reads what the child process printed since the last frame and checks whether it ended. The frame never blocks on a compiler.
- **Anything slow leaves the frame.** The compiler runs in a child process. The search for a :term[toolchain]{id=build-tools} runs programs and waits for them, so it runs as an I/O job (see [the job system](../core/jobs.md)).
- **The build ends as a tree.** Cancelling, closing the project or quitting ends CMake and everything it started, so no compiler keeps writing into the build folder.
- **A failure always names its cause.** The error of a failed build holds the reason and its first errors, and when the log holds only summaries, its last lines.
- **The module matches the engine by default.** The compiler and configuration the engine was configured with build the scripts, so the two agree about the :term[runtime]{id=runtime} library.
- **Projects never choose what runs.** This is a rule of the engine's guide, and the block below gives its reason.

:::rule
A project may come from someone else, so opening one of its files must never start a program the project chose. The external editor is therefore the user's own setting, or the variable `STRATA_EXTERNAL_EDITOR`, and it starts without a shell. The command `script.open` refuses everything but code, CMake and text files inside the project or the engine. For building outside the editor, see [script builds outside the editor](../make/script-builds.md).
:::

## A toy planner

Before the real code, here is the decision at the heart of a build, reduced to a program. The stamp is a note the build tree keeps about how it was configured. The planner compares the note with the machine now and answers with one of three plans. A second function finds the first error in a GCC style log line.

:::question
New to this C++? The program uses structs, functions and `std::vector` ([programming 2](../basics/programming-2.md)), member calls ([programming 3](../basics/programming-3.md)), `std::sort` ([generic C++](../basics/cpp-generic.md)) and `std::optional` ([modern C++](../basics/cpp-modern.md)).
:::

The sketch has two parts: `Decide`, which answers the three-way question, and `FindFirstError`, which cuts a log line at its colons. Look at how little `Decide` compares: the toolchain's name and a sorted list of file names, nothing else.

```cpp sketch="editor-script-builds-toy.cpp"
// A toy script build planner: what a build must do, and where its first error is.
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

// What the last configure step recorded: the toolchain and the script files, sorted.
struct Stamp
{
	std::string Toolchain;
	std::vector<std::string> Files;
};

enum class Plan
{
	RemoveThenConfigure,
	ConfigureAgain,
	BuildOnly
};

std::string Describe(Plan plan)
{
	if (plan == Plan::RemoveThenConfigure)
		return "remove the tree, configure, build";
	if (plan == Plan::ConfigureAgain)
		return "configure again where it is, build";
	return "build only";
}

Plan Decide(const std::optional<Stamp>& previous, const std::string& toolchain, std::vector<std::string> files)
{
	std::sort(files.begin(), files.end());
	if (!previous || previous->Toolchain != toolchain)
		return Plan::RemoveThenConfigure;
	if (previous->Files != files)
		return Plan::ConfigureAgain;
	return Plan::BuildOnly;
}

struct Problem
{
	std::string File;
	int Line = 0;
	std::string Message;
};

// Finds the first "file:line:column: error: message" line of a GCC style log.
std::optional<Problem> FindFirstError(const std::string& log)
{
	size_t start = 0;
	while (start < log.size())
	{
		size_t end = log.find('\n', start);
		if (end == std::string::npos)
			end = log.size();
		const std::string line = log.substr(start, end - start);
		start = end + 1;

		const size_t marker = line.find(": error: ");
		if (marker == std::string::npos || marker == 0)
			continue;
		const size_t columnColon = line.rfind(':', marker - 1);
		const size_t lineColon = columnColon == std::string::npos || columnColon == 0 ? std::string::npos : line.rfind(':', columnColon - 1);
		if (lineColon == std::string::npos)
			continue;
		Problem problem;
		problem.File = line.substr(0, lineColon);
		problem.Line = std::atoi(line.substr(lineColon + 1, columnColon - lineColon - 1).c_str());
		problem.Message = line.substr(marker + 9);
		return problem;
	}
	return std::nullopt;
}

int main()
{
	const std::vector<std::string> files = { "Spinner.cpp", "CMakeLists.txt" };
	const Stamp stamp { "Visual Studio 18 2026", { "CMakeLists.txt", "Spinner.cpp" } };

	std::cout << "first build:   " << Describe(Decide(std::nullopt, "Visual Studio 18 2026", files)) << "\n";
	std::cout << "same files:    " << Describe(Decide(stamp, "Visual Studio 18 2026", files)) << "\n";
	std::cout << "new file:      " << Describe(Decide(stamp, "Visual Studio 18 2026", { "Spinner.cpp", "CMakeLists.txt", "Coin.cpp" })) << "\n";
	std::cout << "other compiler: " << Describe(Decide(stamp, "Ninja", files)) << "\n";

	const std::string log = "[1/2] Building CXX object Spinner.cpp.o\nSpinner.cpp:14:9: error: 'speed' was not declared\nninja: build stopped\n";
	if (const std::optional<Problem> problem = FindFirstError(log))
		std::cout << "first error:   " << problem->File << " line " << problem->Line << ": " << problem->Message << "\n";
	return 0;
}
```

```text output-of="editor-script-builds-toy.cpp"
first build:   remove the tree, configure, build
same files:    build only
new file:      configure again where it is, build
other compiler: remove the tree, configure, build
first error:   Spinner.cpp line 14: 'speed' was not declared
```

1. **Line 34:** Sorting makes the order of the files irrelevant; the engine sorts its list the same way.
2. **Lines 35–36:** No stamp, or another toolchain, removes the tree.
3. **Lines 37–38:** The same toolchain with other files configures again where the tree is.
4. **Lines 64–65:** Two cuts from the right at the colons give the line and the column.

The first build has no stamp, so it starts clean. The same files and toolchain give a build alone. A new file changes the list, so the tree is configured again where it stands. Another compiler makes the old tree useless, so it goes. The real builder adds more fields to the stamp, files that may not be listed, and the work of running processes, but the shape is this.

## The real code, in the order data flows

### Play asks whether to build

When you press Play, `play.start` first asks `EditorContext::GetPlayBuildReason` for a reason to build. The function answers with text or with nothing. Nothing means the loaded module is the one to run.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L2318-L2337" from="const ScriptSourceListing sources = StampScriptSources(scripts);" to="if (moduleTime && newest && newest->LastWriteTime > *moduleTime)" symbol="EditorContext::GetPlayBuildReason"
const ScriptSourceListing sources = StampScriptSources(scripts);
const std::optional<int64_t> moduleTime = FileSystem::GetLastWriteTime(module);
const std::optional<uint64_t> moduleSize = FileSystem::GetFileSize(module);
// The module the editor's last build left: what changed since that build compiled them. A build that left the
// module as it was (nothing it compiles changed) settles it like one that wrote a new module.
if (m_BuiltScriptSources && moduleTime == m_BuiltScriptSources->ModuleTime && moduleSize == m_BuiltScriptSources->ModuleSize)
{
	if (const std::optional<ScriptSourceChange> change = FindScriptSourceChange(m_BuiltScriptSources->Sources, sources))
		return describe(change->Path, ScriptSourceChangeKindToString(change->Kind));
	return std::nullopt;
}
// A module built elsewhere (an IDE, an earlier session): what it was built from is unknown, so a source newer than
// it is the sign.
const ScriptSourceFile* newest = nullptr;
for (const ScriptSourceFile& file : sources.Files)
{
	if (!newest || file.LastWriteTime > newest->LastWriteTime)
		newest = &file;
}
if (moduleTime && newest && newest->LastWriteTime > *moduleTime)
```

1. **Line 2318:** The listing comes from the disk now and holds only sizes and times, so it is cheap.
2. **Lines 2323–2328:** The module is the one the last editor build left, so only the first file that differs from that build's listing counts.
3. **Lines 2331–2337:** A module of unknown origin is judged by its newest :term[source file]{id=source-file}.

The function compares files one by one, not the clock of the whole folder. It holds the listing that the editor's last build compiled, with the module's time and size. If the module on disk is the one that build left, `FindScriptSourceChange` returns the first file that changed, was added or was removed. The reason then names it: `'Scripts/Spinner.cpp' changed after the scripts were built`. A build that left the module as it was settles the question like one that wrote a new module.

If the module came from elsewhere, such as an integrated development environment (IDE) or an earlier session, the editor does not know what it was built from. A source newer than the module is then the sign.

Comparing by file has a reason. A build that compiled nothing leaves the module older than its sources, so a rule of times alone would build again at every Play, and a removed file leaves no newer time at all. The listing compares sizes and times, not contents, so saving a file without changing it still counts as a change. A listing taken before the compiler starts also means a file you save during the build counts as changed after it, which is true.

With no loaded module the answer depends on the scenes: a project whose scenes use scripts gets "the project's scripts are not built yet" or "the project's script module is not loaded".

`play.start` then decides what to do with the reason. The next excerpt shows the branch.

```cpp src="StrataEditor/src/Editor/Commands/PlayCommands.cpp#L104-L123" from="if (builder.IsRunning())" to="return FinishPlayBuild(pollContext, *state);" symbol="StartPlayAfterBuild"
if (builder.IsRunning())
{
	state->WaitingFor = builder.GetCurrentID();
}
else
{
	state->Reason = context.GetPlayBuildReason().value_or(std::string());
	std::string error;
	if (!context.StartPlayBuild(&error))
		return EditorCommandResult::Fail(fmt::format("The scripts must be built before playing ({}), and the build could not start: {}",
			state->Reason, error));
	state->OwnBuild = state->WaitingFor = context.GetPlayBuildID();
	ST_INFO("Building the scripts before playing: {}", state->Reason);
}
return EditorCommandResult::Defer([state](EditorContext& pollContext) -> std::optional<EditorCommandResult>
{
	const ScriptBuilder& pollBuilder = pollContext.GetScriptBuilder();
	if (pollBuilder.IsRunning() && pollBuilder.GetCurrentID() == state->WaitingFor)
		return std::nullopt;
	return FinishPlayBuild(pollContext, *state);
```

1. **Lines 104–107:** A build that runs is waited for, never doubled.
2. **Lines 110–116:** Otherwise one build starts with its reason, and a start that fails says why.
3. **Lines 118–123:** The poll returns nothing while the build runs, so the command stays pending.

When a build already runs, `play.start` waits for it. Otherwise it starts one and remembers its number. It then returns `Defer` with a poll function, so the command answers a frame at a time without blocking (see [Commands that take frames](deferred-commands.md)).

When the build ends, `FinishPlayBuild` runs. A failed build fails `play.start` with the first errors and asks the interface to show the Problems panel. A cancelled build only ends the command. If someone else started the build, the sources may have changed again, so `play.start` builds once itself and polls again. Only then does the scene play, and `play.start {"build": false}` skips all of this to play what is loaded.

### Finding a toolchain

The toolchain is the set of programs that turns source files into a module: CMake, a compiler, a :term[linker]{id=linker} and a build tool, with the generator that ties them together. The engine's own toolchain is baked into the editor when the editor is built: CMake writes `ScriptBuildConfig.h` from `ScriptBuildConfig.h.in`, with the paths, the generator and the configuration. A build tree uses it, so the modules match the engine.

An installed editor cannot use those paths: they belong to the machine that built the release. The next excerpt decides which case applies.

```cpp src="StrataEditor/src/Editor/ScriptToolchain.cpp#L589-L603" symbol="ScriptBuildSettings::Detect"
ScriptBuildSettings ScriptBuildSettings::Detect()
{
	ScriptBuildSettings settings = GetEngineDefaults();
	if (const std::optional<EngineInstallation> installation = FindEngineInstallation(Platform::GetExecutableDirectory()))
	{
		// The build machine's paths mean nothing here: the installation's SDK, and a toolchain of this machine.
		settings.EngineDirectory = installation->Directory;
		settings.FindToolchain = true;
	}
	else
	{
		settings.FindToolchain = !IsScriptToolchainPresent(settings);
	}
	return settings;
}
```

1. **Line 592:** The marker file decides whether this is an installation.
2. **Lines 595–596:** The installation's kit replaces the baked one, and a search is asked for.
3. **Line 600:** In a build tree the search happens only when a baked tool is gone.

The marker file `StrataInstall.json` sits beside the :term[executables]{id=executable} of an installation. When it exists, the editor takes the installation's own copy of the script software development kit (:term[SDK]{id=sdk}) as the engine folder and sets `FindToolchain`. In a build tree it keeps the baked toolchain, and searches only if a baked tool no longer exists, for example after its removal.

With `FindToolchain` set, the first build starts in the phase `FindingToolchain`. A job on the I/O pool calls `ResolveScriptToolchain`, because the search runs `vswhere` and `cmake --version` and waits for them. Meanwhile `ScriptBuilder::Update` only checks one flag per frame. When the job is done, the build continues with the toolchain it found or ends as failed. Later builds keep using that toolchain while its files still exist (`IsScriptToolchainPresent`).

On Windows the search wants a Visual Studio 2022 of version 17.10 or later, or a Visual Studio 2026, with the C++ tools, found through `vswhere`. It also wants a CMake 3.25 or later that knows the generator. The editor asks `cmake -E capabilities` which generators a CMake knows and never guesses from its version. The CMake inside Visual Studio 2026 reports 4.1 and knows that generator, while the CMake releases know it only from 4.2.

Candidates are the CMake the build was configured with, the one on `PATH`, one in Program Files and the one inside the Visual Studio installation. On Linux and macOS the search wants a C++ compiler (`CXX`, `c++`, `g++` or `clang++`), Ninja or Make, and a CMake 3.25 or later that knows their generator.

When nothing fits, the build fails with a message that says what to install. The message starts with the action, for example "Building scripts needs Visual Studio's C++ tools: install Visual Studio 2022 (17.10 or later) or 2026", because a notification shows only the start of a message. The message becomes the first diagnostic, so the Problems panel has a row for it.

### Choosing where the build tree lives

By default the editor's tree is `.strata/Scripts/Build` inside the project, unless Visual Studio's file tracker would fail there. The tracker of `MSBuild` writes logs below each project's folder in the build tree. It cannot create a file whose path has more than 259 characters, even where Windows allows long paths. The failure is an unclear error, `FTK1011`, that does not name the cause.

:::example
A project lives in a folder whose path has 140 characters. Its build folder is that path plus `\.strata\Scripts\Build`, which is 22 more: 162 characters. The deepest file the editor knows of is a tracking log that CMake's compiler check writes during the configure step. Its path below the build folder is `/CMakeFiles/CMakeScratch/TryCompile-xxxxxx/cmTC_xxxxx.dir/Debug/cmTC_xxxxx.tlog/link-cvtres.write.1.tlog`, which is 104 characters.

The module's own deepest log is shorter: for a module name of 17 characters it is 78. The longest path is 162 + 104 = 266, which is 7 characters over the limit of 259.
:::

`CheckScriptBuildPathLength` makes this sum before anything is written, and `ResolveScriptBuildLocation` acts on it. If the project's tree is too deep, the build moves to a private per-user folder, `<user data>/Strata/Builds/<hash>/Build`, one folder per project, named by a :term[hash]{id=hash} of the project's folder. The log says why.

The editor creates that folder through the private-folder functions, because :term[object files]{id=object-file} built there become code the engine loads, and only the user may change them (see [files you can trust](../core/files.md)). Only when the per-user path is also too deep does the build refuse, with the real path to move the project to. Other generators have no tracker, so they never move.

The same step writes `Scripts/CMakePresets.json` for IDEs. It holds a configure preset named `strata` with the engine's toolchain, `STRATA_ENGINE_DIR` and the module's output in the project's binary folder, so an IDE build is hot reloaded like the editor's. A vendor entry marks the file as written by Strata. Strata rewrites the file only when it is missing, or when it carries that mark and differs, and a file the project wrote itself is kept. A `.gitignore` beside it keeps it out of :term[version control]{id=version-control}, because it holds this machine's paths.

### Configure, or only build

A build tree has a note about how it was configured: the file `StrataScriptBuild.json`, the **stamp**. It records the generator, platform, toolset, compiler, build program, configuration, engine folder, source folder and binary folder, and after a successful configure it also lists the script folder's files, sorted.

```cpp src="StrataEditor/src/Editor/ScriptBuild.cpp#L1024-L1046" from="const std::filesystem::path binaryDirectory = project.GetScriptBinaryDirectory();" to="m_Phase = configured ? ScriptBuildPhase::Building : ScriptBuildPhase::Configuring;" symbol="ScriptBuilder::Begin"
const std::filesystem::path binaryDirectory = project.GetScriptBinaryDirectory();
const nlohmann::json treeStamp = MakeStamp(settings, sourceDirectory, binaryDirectory);
const nlohmann::json sourcesStamp = m_SourcePaths;
const std::optional<std::string> stampText = FileSystem::ReadText(m_BuildDirectory / c_StampFile);
std::optional<nlohmann::json> previousStamp = stampText ? JsonUtils::Parse(*stampText) : std::nullopt;
nlohmann::json previousSources;
if (previousStamp && previousStamp->is_object() && previousStamp->contains(c_StampSourcesKey))
{
	previousSources = std::move((*previousStamp)[c_StampSourcesKey]);
	previousStamp->erase(c_StampSourcesKey);
}
const bool reusable = FileSystem::IsRegularFile(m_BuildDirectory / "CMakeCache.txt") && previousStamp && *previousStamp == treeStamp;
const bool configured = reusable && !m_SourcesTruncated && previousSources == sourcesStamp;
if (!reusable && FileSystem::Exists(m_BuildDirectory) && !FileSystem::Remove(m_BuildDirectory))
	return fail(fmt::format("Cannot remove the outdated script build directory '{}'", FileSystem::ToUTF8(m_BuildDirectory)));
if (!FileSystem::CreateDirectories(m_BuildDirectory) || !FileSystem::CreateDirectories(binaryDirectory))
	return fail(fmt::format("Cannot create the script build directories in '{}'", FileSystem::ToUTF8(project.GetIntermediateDirectory())));

m_Configured = !configured;
std::string error;
const std::vector<std::string> arguments = configured ? MakeScriptBuildArguments(settings, m_BuildDirectory)
	: MakeScriptConfigureArguments(settings, sourceDirectory, m_BuildDirectory, binaryDirectory);
m_Phase = configured ? ScriptBuildPhase::Building : ScriptBuildPhase::Configuring;
```

1. **Line 1035:** A tree is kept only with its cache and an equal stamp.
2. **Line 1036:** It counts as configured only when the files also match and the listing is complete.
3. **Lines 1037–1038:** A tree that cannot be kept is removed.
4. **Lines 1044–1046:** One flag picks both the arguments and the phase.

Compare this with the toy. A tree can be kept when its `CMakeCache.txt` exists and its stamp, without the file list, equals the stamp of now. It counts as configured when the files also match and the listing was not cut short. A tree that cannot be kept is removed, because a tree configured with another compiler or elsewhere cannot serve. A tree that can be kept but was configured for other files is configured again where it is, which keeps what it built.

Before the configure step runs, the stamp on disk is empty for a new tree and lacks its file list for the other case. A configure that fails half way therefore leaves a stamp that asks for another one. The file list is written only after the configure step succeeded.

Why track the files at all, when the module's CMake lists its sources with `CONFIGURE_DEPENDS`? Visual Studio compiles every project the way it stood when CMake configured it, even if CMake finds new files during the build. So the editor takes a listing with `StampScriptSources` right before the build. The listing holds at most 4,096 files and looks at most at 65,536 folder entries. When it is cut short, its files are unknown, so the build configures again.

### Running the processes and polling them

The builder asks `Process` to run CMake here. Look at the last setting, `TerminateTree`.

```cpp src="StrataEditor/src/Editor/ScriptBuild.cpp#L1127-L1134" from="ProcessSpecification specification;" to="specification.TerminateTree = true;" symbol="ScriptBuilder::StartProcess"
ProcessSpecification specification;
specification.Executable = FileSystem::IsRegularFile(m_Settings.CMake) ? m_Settings.CMake : std::filesystem::path("cmake");
specification.Arguments = arguments;
specification.Output = ProcessOutputMode::Capture;
specification.HideWindow = true;
// Cancelling (also by closing the project or the editor) must stop MSBuild, ninja, the compilers and the linker too,
// or they keep writing the build and binary directories.
specification.TerminateTree = true;
```

The specification asks `Process` to capture the output, hide the console window and end the whole process tree when the build is terminated. `Process` is taught on [the platform page](../core/platform.md): here you need only that `TerminateTree` is why a cancel stops `MSBuild`, `ninja`, the compilers and the linker together. The program is the CMake of the settings, or `cmake` on `PATH` when that file is gone. The two runs are `cmake -S <sources> -B <tree> -G <generator> ...` and `cmake --build <tree> --parallel --config <configuration>`. For Visual Studio the second adds `/nodeReuse:false`, because `MSBuild` worker nodes would otherwise stay behind and keep the output pipe and the module's debug file open.

```cpp src="StrataEditor/src/Editor/ScriptBuild.cpp#L1190-L1208" from="CollectOutput(false);" to="const int exitCode = m_Process->GetExitCode().value_or(-1);" symbol="ScriptBuilder::Update"
CollectOutput(false);
if (!m_Draining)
{
	if (m_Process->IsRunning())
		return false;
	m_Draining = true;
	m_ExitTime = std::chrono::steady_clock::now();
}
// The last lines (often the errors) may still be on their way: wait until the output ended.
if (!m_Process->IsOutputFinished())
{
	if (std::chrono::steady_clock::now() - m_ExitTime < c_OutputDrainLimit)
		return false;
	ST_WARN("[Scripts] The build's output did not end within {} s after CMake exited; a process it started still holds it",
		c_OutputDrainLimit.count());
}

CollectOutput(true);
const int exitCode = m_Process->GetExitCode().value_or(-1);
```

1. **Line 1190:** Output is drained every frame, before anything else.
2. **Lines 1193–1194:** While the process runs, the frame returns at once.
3. **Lines 1199–1205:** After the exit the builder still waits for the output, but for 5 seconds at most.
4. **Line 1208:** Only now is the :term[exit code]{id=exit-code} read.

Each frame `Update` drains what the process printed. `OutputLineSplitter` cuts the text into lines, and cuts a line that never ends after 64 KiB, so a tool that prints no line break cannot grow memory without bound. Each complete line goes to the log with the prefix `[Scripts]`, which is how the Console shows build output while it arrives. The editor keeps at most 8 MiB of the log for diagnostics and keeps the newer half when it passes that.

When the process has exited, its last lines may still be in transit, and the errors are often the last lines. The builder waits until the output ends, for at most 5 seconds, and then warns that a process it started still holds the output. Then it reads the exit code. A configure that exits with 0 writes the stamp's file list and starts the build process. A build that exits with 0 must also have produced the module file; otherwise it fails with a message that tells you to keep the module's name and output folder.

Everything ends in `Finish`. It parses the whole log into diagnostics, keeps the last 40 lines as `LogTail`, records the seconds, whether the build configured and whether the module file changed, and logs one error entry for a failure.

### Reading the log

A **diagnostic** is one error or warning found in a build log, split into file, line, column, severity, code and message. `ParseScriptBuildDiagnostics` reads MSVC, GCC, Clang, `MSBuild`, CMake and the linkers of the `GNU`, LLVM, Apple and Microsoft toolchains. It returns them in order and without duplicates, because `MSBuild` repeats every error in its summary. It returns at most 100.

Take the line `Scripts\Spinner.cpp(14,9): error C2065: 'speed': undeclared identifier [G:\Moon\.strata\Scripts\Build\MoonScripts.vcxproj]`. The parser takes file `Scripts\Spinner.cpp`, line 14, column 9, the severity from the word error, the code `C2065`, and the message without the project name that `MSBuild` appends in brackets. A GCC line `Spinner.cpp:14:9: error: ...` gives the same without a code. CMake prints `CMake Error at CMakeLists.txt:5 (find_package):` and puts the message on the lines below it that start with spaces, so the parser joins those. Messages longer than 4,096 :term[bytes]{id=byte} are cut at a character boundary; the log keeps them whole.

Some errors say only that a step failed, such as the `ld` linker's "returned 1 exit status", "linker command failed", `LNK1120` or "exited with code 2" from `cl.exe`. They are summaries, and the cause is on another line. `IsScriptBuildSummary` tells them apart, and the next function uses it.

```cpp src="StrataEditor/src/Editor/ScriptBuild.cpp#L736-L752" symbol="DescribeScriptBuildFailure"
std::string DescribeScriptBuildFailure(const std::string& reason, const std::vector<ScriptDiagnostic>& diagnostics, std::string_view log)
{
	std::string description = reason;
	size_t errors = 0;
	bool onlySummaries = true;
	for (const ScriptDiagnostic& diagnostic : diagnostics)
	{
		if (diagnostic.Severity != "error")
			continue;
		onlySummaries = onlySummaries && IsScriptBuildSummary(diagnostic);
		if (errors++ < c_ErrorsInSummary)
			description += "\n" + FormatScriptDiagnostic(diagnostic);
	}
	if (onlySummaries)
		description += "\nLast lines of the build log:\n" + GetLogTail(log, c_FailureLogTailLines);
	return description;
}
```

1. **Line 745:** One error that is no summary is enough to keep the log lines out.
2. **Line 746:** Only the first five errors enter the message.
3. **Lines 749–750:** With only summaries, or none, the last 15 log lines follow.

The error of a failed build is the reason plus up to five errors. If every error is a summary, or there is none, the last 15 lines of the log follow, so the cause is never missing. `CountScriptBuildErrors` counts what the Problems panel counts: diagnostics that are not warnings.

`FindSourceReference` lets the Console find a source line in an ordinary log message: a compiler diagnostic, also after the `[Scripts] ` prefix, or a crash report that says "at file(line)". Only code and CMake files count, so a message that mentions a number in round brackets does not open a random file. <!-- markdownlint-disable-line MD038 -->

### After the build

`OnScriptBuildFinished` runs in the frame the build ended. It first turns the :term[file watcher]{id=file-watcher} back on. The editor paused hot reload while its own build ran, because the linker's write would otherwise trigger a second reload of the same module. The module loads from a :term[private copy]{id=private-copy}, so the next build can replace the file while the old module runs. Then it remembers what the build compiled: the listing taken before it started, with the module's time and size, which `GetPlayBuildReason` compares later.

A successful build loads the module, or hot reloads it when one is loaded (see [hot reload](../scripting/hot-reload.md)). A module that is loaded and unchanged stays, except that a module which crashed is loaded again even when unchanged. A successful build is the way back to a working module, also when the crash came from data.

Finally one toast changes from "Building scripts" to the outcome. The outcomes are:

- "Scripts built" or "Scripts built and reloaded", with the seconds.
- "Script build failed", with the first diagnostic and a request for the Problems panel.
- "Scripts built, but not loaded", with the load error.
- "Script build cancelled", with no error, because someone ended it.

### Script files, the external editor and the rule

The script folder is listed as the build compiles it: code and CMake files, without folders whose names start with a dot and without build trees (folders holding a `CMakeCache.txt`). Files are read for `ST_SCRIPT_CLASS` lines, outside comments and strings, up to 1 MiB each. A list kept on an I/O thread (`ScriptSourceList`) changes its version only when the files differ.

A new project gets a `CMakeLists.txt` that calls `strata_add_script_module` through the `StrataScriptCore` package, and an example class `Spinner` that turns its entity. `script.init` writes these when missing; `script.create` writes a class from a template, after it checks that the class and field names are identifiers that neither the project nor the SDK declare. Existing files are never replaced.

The external editor opens a file at a line, from `script.open`, the Problems panel or a crash report. Its command is a template such as `code -g {file}:{line}:{column}`. `ExpandCommand` splits the template into a program and arguments, fills the placeholders and starts the program directly, never through a shell, so a file name is never read as a command. Batch files are refused, except that the launcher of Visual Studio Code, a batch file, starts `Code.exe` beside it.

The command comes from `STRATA_EXTERNAL_EDITOR`, otherwise from the user's preferences, and never from the project. Without one, the default application opens the file. The command `script.open` opens only code, CMake and text files inside the project or the engine, because the default application of another type might run them.

## A build, start to finish

:::example
Start a project from the `basic3d` template, then break a script on purpose. Create the project, add a class and build it, so that a module exists.
:::

These three commands create the project, write the class `Coin` and build the scripts once.

```sh
StrataCLI call project.create '{"directory": "C:/Games/Coin", "name": "Coin", "template": "basic3d"}'
StrataCLI call script.create '{"class": "Coin"}'
StrataCLI call script.build
```

Each command is one request. A new project already has its script `CMakeLists.txt`, and `script.create` writes `Coin.cpp` beside it. The `script.build` call finds no stamp, so it configures, builds and loads the module, and its result says `"configured": true`. Now open `Coin.cpp` in your :term[code editor]{id=code-editor}, find the line `ST_SCRIPT_FIELD(Speed);` that registers its field, and change the name in it to one the class does not declare. Then press Play, or run the next two commands.

```sh
StrataCLI call play.start
StrataCLI call script.status
```

`play.start` asks `GetPlayBuildReason`, which names `Coin.cpp` as changed, and starts a build. This time the stamp matches and the file list is the same, so the build only builds. The compiler fails, `play.start` fails with the first errors, and the scene does not play. `script.status` lists each diagnostic with file, line, column, code and message, plus the end of the log.

Fix the line and run `play.start` again. It builds once more, the module hot reloads, and the game plays. Add a second file by hand, and the next build says it configures again.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A scripting language read at run time | Godot's GDScript, many engines with Lua | No compile step, no toolchain to find | Game code in C++ and its speed; the C interface is the same either way |
| A compiler shipped with the editor | Unity's own script compilation | The toolchain is never missing | A large download, and one more compiler to keep in step |
| Patching the running program | Unreal's Live Coding | Changes without leaving Play | Subtle state bugs; a harder contract with the module |
| Running the configure step every time | Simple build scripts | No stamp to keep right | Seconds on every Play |
| Building on the main thread | Early or tiny editors | Less code | A frozen window for the length of the build |

## How it is tested

Five suites cover the page, all in `StrataTests/src/Editor/`. `Editor.ScriptBuild` checks the arguments each generator gets, the diagnostics parser on MSVC, GCC, Clang, linker and CMake output, and that a failed build names its cause. It also checks the bounded line splitting, the path-length rules with the move to the per-user folder, and that adding or removing a file configures again.

`Editor.ScriptToolchain` describes whole machines with a `ScriptToolchainEnvironment` and checks the search on Windows, Linux and macOS, including a machine with no usable tools. `Editor.ScriptSources` checks listing and comparing. `Editor.ScriptWorkflow` checks `script.create` and the external editor. It also checks that Play builds changed sources, fails with the build's errors and stops when its build is cancelled. `Package.ScriptBuild` builds, loads, hot reloads and exports a real project.

To run the first four, use the test program's suite filter from the build folder, for example `StrataTests.exe --test-suite=Editor.Script*`. The package tests carry the label `package` and need CMake and a compiler on the machine.

## Changing it safely

Extension points are few. A new diagnostic format goes into `ParseScriptBuildDiagnostics` with a case in the parser test, not into a new log reader. A new platform tool goes into `ResolveScriptToolchain` and gets a described machine in the toolchain tests. A new input of the stamp goes into `MakeStamp`, and it must decide whether it removes the tree or only configures again.

Keep these rules, each with its reason.

- Never block a frame on a build or a search: the main thread owns the scene and the window.
- Every file the builder writes must be checked before it is written. A build that fails before it starts must say why, as the path rules do.
- Never start a program chosen by a project. That is the rule above.
- Keep `TerminateTree` on: without it a cancelled build leaves compilers running in the build folder.
- A message that reaches a person starts with what to do.

To check a change, run the five suites, then `ctest --preset windows-debug -j 8` on Windows, or the preset of your platform. The feature test and scripting tests also build modules.

## What went wrong before

Visual Studio builds in deep folders failed with errors such as `FTK1011` ("could not create the new file tracking log file") that did not name the path as the cause. The fix is the path-length check and the per-user folder. The tests are the path cases of `Editor.ScriptBuild`. One refuses a project that is too deep even for the per-user folder, with the real path to move it to. Another builds a deep project in the per-user folder.

## Summary

- A build runs as CMake child processes that `ScriptBuilder::Update` polls once per frame, one at a time, in the phases `FindingToolchain`, `Configuring` and `Building`, and the whole process tree ends on cancel.
- The engine's own toolchain is baked in; an installed editor finds one on an I/O job, or fails with what to install.
- The stamp decides: another toolchain removes the tree, other files configure again, otherwise the build only builds; deep trees move to a per-user folder.
- Diagnostics carry file, line, column, code and message, summaries are told from causes, and every failure names its cause.
- `play.start` builds first when `GetPlayBuildReason` finds a changed, added or removed file, waits for the build, and fails with its first errors.

## Check yourself

1. A project's build tree was configured for files `A.cpp` and `CMakeLists.txt`. You add `B.cpp` and press Play. What does the next build do first?

   - Only builds, because CMake finds new files by itself.
   - Removes the tree and configures.
   - Configures again where the tree is, then builds.

   :::answer{tests="configure-rule"}
   The third. The stamp's list of files differs, so the tree is configured again where it stands, and what it built stays. The first is wrong because a Visual Studio build compiles projects as configured. The second is wrong because the toolchain did not change.
   :::

2. `ScriptBuilder::Update` runs during a 20 second compile. How long does it take in one frame, and why?

   :::answer{tests="one-build"}
   Almost no time. It drains the output already captured, checks whether the child process ended and returns. The compiler runs in another process, so frames keep drawing.
   :::

3. An installed editor on a machine with no Visual Studio presses Play. What does the person see?

   :::answer{tests="toolchain"}
   The build fails in the `FindingToolchain` phase. The toast "Script build failed" shows the message, which starts with what to install, the Problems panel gets that message as a row, and `play.start` fails with it.
   :::

4. A link step prints an error `LNK2019` (unresolved external symbol) and then `LNK1120` (1 unresolved externals). Which line is the cause, and how does the failure text treat the other?

   :::answer{tests="diagnostics"}
   `LNK2019` is the cause. `LNK1120` is a summary, so `DescribeScriptBuildFailure` lists the `LNK2019` error among the first five. Not every error is a summary, so it adds no log lines.
   :::

5. You press Play and a build already runs, started by `script.build`. Does `play.start` start another?

   :::answer{tests="play-build"}
   No. It waits for the running build. When that ends, it asks `GetPlayBuildReason` again, and starts one build itself only if the sources changed meanwhile.
   :::

## Exercises

1. **Basic.** A Visual Studio build folder is 150 characters long and the module name has 20 characters, with the configuration `Debug`. Does the build stay in the project? Use 104 for the configure log. The module's own deepest log is 61 plus the length of the name, for a name of more than 16 characters.

   :::answer[Worked solution]{tests="configure-rule"}
   The module's log is 61 + 20 = 81 characters, less than 104, so the longest path below the build folder is 104. Then 150 + 104 = 254, which is under 259, so the build stays in the project. With a build folder of 156 characters the sum is 260, one over, and the build moves to the per-user folder.
   :::

2. **Medium.** Write a program that takes the length of a build folder and a module name, and says whether Visual Studio's file tracker accepts them. Run it for three cases: a folder of 150 characters, one of 156, and one of 30 characters with a module name of 60 characters.

   :::answer[Worked solution]{tests="configure-rule" solution="sketches/editor-script-builds-exercise2.cpp"}
   The program follows the sum of the example: the longest path is the folder's length plus the larger of the two logs.

   ```cpp sketch="editor-script-builds-exercise2.cpp"
   // Would Visual Studio's file tracker accept a build folder and a module name?
   #include <algorithm>
   #include <iostream>
   #include <string>

   constexpr size_t c_MaxPath = 259;
   constexpr size_t c_ConfigureLog = 104;

   // The deepest tracking log of the module's own build, for the Debug configuration.
   size_t GetModuleLog(const std::string& module)
   {
   	const size_t trackingName = std::min<size_t>(module.size(), 17);
   	return 1 + module.size() + 5 + 5 + 1 + trackingName + 5 + 27;
   }

   void Check(size_t folderLength, const std::string& module)
   {
   	const size_t longest = folderLength + std::max(c_ConfigureLog, GetModuleLog(module));
   	std::cout << "folder " << folderLength << ", module of " << module.size() << " characters: longest path " << longest
   			  << (longest <= c_MaxPath ? ", fits" : ", too deep") << "\n";
   }

   int main()
   {
   	Check(150, std::string(20, 'M'));
   	Check(156, std::string(20, 'M'));
   	Check(30, std::string(60, 'M'));
   	return 0;
   }
   ```

   ```text output-of="editor-script-builds-exercise2.cpp"
   folder 150, module of 20 characters: longest path 254, fits
   folder 156, module of 20 characters: longest path 260, too deep
   folder 30, module of 60 characters: longest path 151, fits
   ```

   1. **Line 12:** The tracker shortens the name of a long module to 17 characters.
   2. **Line 13:** The fixed parts of the path add up around the module name.
   3. **Line 18:** The longest path is the folder plus the larger of the two logs.
   :::

3. **Hard.** Trace it yourself: change a script's source, press Play with a breakpoint in `GetPlayBuildReason`, and name the file it found changed. Then step through `ScriptBuilder::Update` and name the phase when CMake configures and when it builds.

   :::answer[Worked solution]{tests="play-build,one-build"}
   The function is `EditorContext::GetPlayBuildReason` in `StrataEditor/src/Editor/EditorContext.cpp`. It returns the path that `FindScriptSourceChange` reports. In `ScriptBuilder::Update` in `StrataEditor/src/Editor/ScriptBuild.cpp` the phase is `Configuring` while the first process runs, then `Building` once the stamp is written and the second process starts.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/ScriptBuild.h`, `ScriptBuild.cpp`: `ScriptBuilder`, the settings, the stamp, the presets and the diagnostics.
- `StrataEditor/src/Editor/ScriptToolchain.h`, `ScriptToolchain.cpp`: `ResolveScriptToolchain`, `FindEngineInstallation`.
- `StrataEditor/src/Editor/ScriptSources.cpp`: `ListScriptSources`, `FindScriptSourceChange`.
- `StrataEditor/src/Editor/ExternalEditor.cpp`, `ScriptProject.cpp`: the external editor and the project's script files.
- Commands: `play.start`, `script.build`, `script.status`, `script.list`, `script.init`, `script.create`, `script.open`.
- Tests: `Editor.ScriptBuild`, `Editor.ScriptToolchain`, `Editor.ScriptSources`, `Editor.ScriptWorkflow`, `Package.ScriptBuild`.

## Further reading

- CMake documentation, "cmake(1)" and "cmake-generators(7)" (cmake.org): what the two runs and the generators do. Beginner to intermediate.
- Microsoft Learn, MSBuild and the file tracker (learn.microsoft.com): why path length matters. Intermediate.
- Epic Games, "Live Coding" in the Unreal Engine documentation; Unity manual, "Script compilation": how two other engines build game code. Intermediate.
- Godot documentation, "GDScript" (docs.godotengine.org): a scripting language instead of a compiler. Beginner.
