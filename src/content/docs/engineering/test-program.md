---
id: engineering/test-program
title: "Inside StrataTests"
description: "How the one test binary StrataTests is built, started, split into shards, made safe against crashes and used as its own helper process."
kind: internals
size: L
tracks: [E]
needs: [engineering/testing, engineering/cmake]
time: 80
learn:
  - id: shard-contract
    text: explain why every suite runs in exactly one shard and which labels and locks keep a parallel run safe
  - id: add-suite
    text: add a suite with a new prefix where CTest will run it, and read the failure that guards the step
  - id: helper-process
    text: write a test that starts a child process of the test binary without any outside program
  - id: crash-handlers
    text: explain why doctest's signal handlers are off and how a crash still names its test case
  - id: sweep-seeds
    text: write a corruption sweep whose failures repeat, sampled in Debug and full in Release
since: 0.4.0
status: final
---

Strata has one test program, `StrataTests`. Every module's tests are compiled into it, and every test case lives in a named suite. The program does three jobs. It runs the tests, it is the child process that some tests start, and it is split by suite name into parts that CTest runs side by side.

This page opens that program: what it compiles, what its `main` does before the first test, how it plays the role of :term[CMake]{id=cmake} or of an editor. The page also shows how the program divides its suites so that none is lost. The kinds of tests, doctest and tests that fail at random belong to [the testing page](testing.md). The graphics, end-to-end and package tests are on [the page about test kinds](test-kinds.md), the feature test on [its own page](feature-test.md), and the perf suites on [the perf lab](perf-lab.md).

## The problem and how engines solve it

An engine of this size has thousands of test cases. They must all run before every commit, and a person waits for them. Three choices decide how long that wait is and whether a test is ever skipped.

The first choice is how many programs to build. One program per module keeps each small, but every one links the engine again and starts its own process. One program for everything links once, but a run takes every test, unless something splits it. Strata chose one program and splits the work with names.

The second choice is how to run the program. **CTest** is CMake's test runner: it knows a list of tests, and each test is a command with properties (a name, a :term[current folder]{id=current-folder}, labels, a time limit). It runs the commands, many at once with `-j 8`, and reports which passed. If the tests ran as one command, one slow test would hold up the rest. Strata gives CTest a command per group of suites.

A **shard** is one such group: a set of suites, chosen by name patterns, that CTest runs as one test in one process. Shards let eight processes work at the same time. Strata keeps each shard under about a minute in Debug, because a shard that grows past it becomes the slowest part of every run.

The third choice is how to tell CTest what each test needs. A **label** is a word attached to a CTest test, such as `gpu` or `perf`, that a developer selects or skips with `ctest -L` and `ctest -LE`. A machine without a :term[graphics card]{id=gpu} runs `ctest -LE gpu`. The labels also separate cheap tests from costly ones.

Splitting has one danger that the other choices do not have. A suite that no group's pattern matches runs nowhere, and nothing fails. The test is green only because it never ran. Strata answers with a test that checks the split itself, shown below.

The file `Docs/Roadmap.md` records what the split bought. On `macOS`, after wave 4, a Debug `ctest` took 94 to 163 s with `-j 8`, where the serial run had taken 500 to 804 s.

## The map: one binary, many ways to run it

Every suite of the binary stands in one column of the figure. The eight own CTests take the suites that need special care: the tests that need a graphics device, the :term[end-to-end tests]{id=end-to-end-test}, the package tests, the perf tests and the feature test. The 13 shards take the rest. A suite whose name ends in `.Sweep` also goes to `StrataTests.Fuzz`. One test of the binary, `Testing.Shards`, reads the table and fails when a suite has no run or two.

```mermaid caption="Every suite of the test program goes to exactly one own test or one shard; sweep suites also go to the full fuzz run, and a check reads the table." alt="A column of suite name patterns on the left. Arrows lead to eight own tests for special suites and thirteen shards for the rest. Suites that end in Sweep also have an arrow to a fuzz run. A check box reads the table and the list of suites and fails when a suite has no run or two."
flowchart LR
    S["Suites of the binary"] --> O["8 own CTests"]
    S --> C["13 Core shards"]
    S -- "suites ending in .Sweep" --> F["StrataTests.Fuzz"]
    T["CoreShards.json"] --> O
    T --> C
    T --> F
    K["Testing.Shards"] -. "reads the table and the suite list" .-> T
    K -. "each suite once" .-> S
```

Three files carry the design. `StrataTests/CoreShards.json` is the table. `StrataTests/CMakeLists.txt` turns the table into CTests. `StrataTests/src/Testing/ShardTests.cpp` holds the check. The binary's `main` is in `StrataTests/src/TestMain.cpp`, and the crash naming is in `StrataTests/src/TestCrashReporter.cpp`.

Each CTest is one process of the binary. That process runs its test cases one after another on the :term[main thread]{id=main-thread}, so two cases of one shard never run at the same time. Tests that need a child start another copy of the binary, and the child ends before the test does.

## The contract

Callers of the test program, which means the people who add tests, rely on four rules and must follow them.

Every test case belongs to a `TEST_SUITE`. A case outside any suite has the suite name "", the list of suites omits it, and no CTest filter matches it, so it would run nowhere. The check fails and names the case.

Every suite prefix belongs to a shard or to an own CTest. A suite that only matches no filter fails the same check. Both rules guard the one thing that must hold: every test runs.

:::rule[Every test case in a suite, every new suite prefix in a shard]
Without this, a test runs in no CTest and nobody sees it. A shard stays under about a minute in Debug, so a slow suite goes into a shard of its own. [Why the split exists](#the-problem-and-how-engines-solve-it).
:::

Tests write only into `Tests::CreateTemporaryDirectory()` and never open a sample project in place; `Tests::CopySampleProject` copies one. Tests run side by side, and a test that wrote into the source tree or the user's folders would change what the next test sees.

:::rule[Never set the process's environment for a child]
:term[Environment variables]{id=environment-variable} belong to the whole process, and tests run beside each other. A test that needs a child with another environment starts the helper mode `run-with-environment`, which sets the variables in a process of its own.
:::

Tests follow the transform contract of the scene, wait by a clock or a condition and never by frames, and tests of the graphics device share one device. Those rules belong to other pages; the four above belong to this one.

## A toy version

:::question[Do I need to know C++ for the next code?]
The code uses functions, classes, pointers, lambdas and `constexpr`, which [functions and loops](../basics/programming-2.md), [classes and calls](../basics/programming-3.md), [pointers](../basics/cpp-memory.md), [lambdas](../basics/cpp-generic.md) and [modern C++](../basics/cpp-modern.md) teach. Read the comments and the notes after the code: the idea does not depend on the details of the writing.
:::

The toy below is a test runner in 53 lines. It has a list of test cases with suite names, and it runs them one by one. One of its arguments, `--toy-helper=<mode>`, turns the program into a child process. Two test cases use that: a child that ends with code 0 and a child that ends with code 7. Search for two things: `main` decides first whether it is a helper, and a test starts the helper with its own path.

```cpp sketch="engineering-test-program-toy.cpp"
// A test runner whose program is also the child process its tests start: one helper mode, selected by an argument.
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <string>
#include <string_view>
#include <vector>

struct TestCase
{
	std::string Suite;
	std::string Name;
	std::function<bool()> Body;
};

static std::string s_Self;

// The helper mode: stands in for an outside program and ends with the exit code it is told.
static int RunHelperMode(std::string_view mode, int argc, char** argv)
{
	if (mode == "exit-code" && argc > 2)
		return std::atoi(argv[2]);
	std::fprintf(stderr, "unknown helper mode '%s'\n", std::string(mode).c_str());
	return 99;
}

// A test starts the helper as a child: this program again, with the helper argument.
static int RunHelper(const std::string& arguments)
{
	return std::system(("\"" + s_Self + "\" --toy-helper=" + arguments).c_str());
}

int main(int argc, char** argv)
{
	constexpr std::string_view helperPrefix = "--toy-helper=";
	if (argc > 1 && std::string_view(argv[1]).substr(0, helperPrefix.size()) == helperPrefix)
		return RunHelperMode(std::string_view(argv[1]).substr(helperPrefix.size()), argc, argv);
	s_Self = argv[0];

	const std::vector<TestCase> tests = {
		{ "Math", "Addition", []() { return 1 + 1 == 2; } },
		{ "Process", "A child that succeeds", []() { return RunHelper("exit-code 0") == 0; } },
		{ "Process", "A child that fails", []() { return RunHelper("exit-code 7") != 0; } },
	};
	int failures = 0;
	for (const TestCase& test : tests)
	{
		const bool passed = test.Body();
		std::printf("[%s] %s / %s\n", passed ? "passed" : "FAILED", test.Suite.c_str(), test.Name.c_str());
		failures += passed ? 0 : 1;
	}
	return failures;
}
```

```text output-of="engineering-test-program-toy.cpp"
[passed] Math / Addition
[passed] Process / A child that succeeds
[passed] Process / A child that fails
```

1. **Lines 21-22:** the one helper mode: a test can ask for an :term[exit code]{id=exit-code} and the program ends with it.
2. **Line 30:** a test starts the helper by running its own program again, with the helper argument.
3. **Lines 35-37:** `main` checks for the helper argument first and returns before any test runs.
4. **Line 38:** `main` stores its own path, which the tests use to start the child.
5. **Lines 42-43:** the tests judge the child by its exit code only, as the real tests do.

The toy shows the design in small. No test needs a program from outside, because the program itself can stand in for any outside program a test needs. The toy omits what makes the real runner safe on a shared machine: private folders, the crash naming and the registration of the engine's modules.

## The real code: what the binary is made of

`StrataTests/CMakeLists.txt` builds the binary from all of `StrataTests/src`, minus two kinds of files. When a build has no editor, the editor tests are omitted. When a build omits a module, that module's tests are omitted too, through the lists `STRATA_TESTS_OF_PHYSICS`, `STRATA_TESTS_OF_AUDIO`, `STRATA_TESTS_OF_ANIMATION` and `STRATA_TESTS_OF_GLFW`. The binary links the engine, the :term[tooling layer]{id=tooling-layer}, the script development kit, doctest and the libraries the tests read.

The test script modules are built beside it with `strata_add_script_module`, the same function a game uses: `StrataTestScriptsAPI`, `StrataTestScriptsReloadV1`, `StrataTestScriptsFaults` and the others. Each module's file name reaches the tests as a definition such as `STRATA_TEST_SCRIPTS_API`.

The definitions are the tests' view of the build. `STRATA_SOURCE_DIR` names the :term[repository]{id=repository}. `ST_TESTS_HAVE_EVERY_MODULE` and `ST_TESTS_HAVE_EDITOR` are 1 or 0, never undefined. A file that forgets an include then cannot read them as 0 and drop its cases from every build. `DOCTEST_CONFIG_NO_POSIX_SIGNALS` is explained after `main`.

The `main` of the runner follows a strict order. It runs in the same way for the test process and for each helper, up to the point where the two part. Before the first quote, `main` connects the standard streams as a console program and sets the log to Warn. Helpers print what they find on those streams, and a test reads it, so the log must not add lines of its own.

```cpp src="StrataTests/src/TestMain.cpp#L1369-L1388"
constexpr std::string_view helperPrefix = "--strata-test-helper=";
const bool isHelper = argc > 1 && std::string_view(argv[1]).substr(0, helperPrefix.size()) == helperPrefix;
const std::string_view helperMode = isHelper ? std::string_view(argv[1]).substr(helperPrefix.size()) : std::string_view();
if (isHelper)
{
	if (const std::optional<int> result = Strata::Tests::RunModuleRegistrationHelper(helperMode, argc, argv))
		return *result;
}

// Like every program that uses the engine, before anything touches a registry; with the asset pipeline, like the editor.
Strata::Engine::ModuleRegistrationOptions modules;
modules.AssetPipeline = Strata::RegisterAssetPipeline;
#if ST_TESTS_HAVE_EDITOR
// And the editor's preference sections, as the editor registers them.
modules.Extra.push_back([]() { Strata::EditorPreferences::RegisterSections(Strata::SettingsRegistry::GetProcessRegistry()); });
#endif
Strata::Engine::RegisterBuiltinModules(modules);

if (isHelper)
	return RunHelperMode(helperMode, argc, argv);
```

1. **Line 1369:** the prefix that marks a child run; a helper is a normal run with a first argument.
2. **Lines 1372-1376:** helper modes that need their own registry of modules run first and may end the process.
3. **Lines 1379-1385:** the engine's modules are registered as every program registers them, with the asset pipeline. Editor builds add the editor's preference sections. Helpers and tests then see the same registries.
4. **Lines 1387-1388:** every other helper mode runs now, and its code is the process's exit code.

After the helper branch, `main` handles the two stand-ins of the next section. It then disables the throttling of execution speed that the :term[operating system]{id=operating-system} applies to programs in the background, as applications do, so that the perf suites measure the engine as it runs in a game. Last, it makes the test process private.

```cpp src="StrataTests/src/TestMain.cpp#L1402-L1418"
	const std::filesystem::path runtimeDirectory = Strata::Tests::CreateTemporaryDirectory("Runtime");
	std::error_code permissionError;
	std::filesystem::permissions(runtimeDirectory, std::filesystem::perms::owner_all, std::filesystem::perm_options::replace, permissionError);
	Strata::Platform::SetEnvVar("STRATA_RUNTIME_DIR", Strata::FileSystem::ToUTF8(runtimeDirectory));
	// Editors the tests start keep their recent projects in the test's directory, never in the user's list.
	Strata::Platform::SetEnvVar("STRATA_RECENT_PROJECTS", Strata::FileSystem::ToUTF8(runtimeDirectory / "RecentProjects.json"));
	// Script builds of projects too deep for MSBuild go to the test's directory, never to the user's build directory.
	Strata::Platform::SetEnvVar("STRATA_SCRIPT_BUILDS_DIR", Strata::FileSystem::ToUTF8(runtimeDirectory / "ScriptBuilds"));

	doctest::Context context(argc, argv);
	const int result = context.run();

	Strata::Tests::GPUContext::ShutdownShared();
	Strata::Log::Shutdown();
	Strata::Tests::CleanupTemporaryDirectories();
	return result;
}
```

1. **Lines 1402-1405:** a fresh temporary folder becomes `STRATA_RUNTIME_DIR`, so script module copies never land in the user's :term[runtime]{id=runtime} folder.
2. **Lines 1406-1409:** the recent-projects file and the script build folder also move into it. The editors and helpers that the tests start inherit all three.
3. **Lines 1411-1412:** only then does doctest run.
4. **Lines 1414-1416:** the shared graphics device shuts down last, because every graphics test used it, and the temporary folders are removed.

## The real code: the binary as its own helper process

A **helper mode** is a first argument of the form `--strata-test-helper=<mode>` that turns `StrataTests` into a small program with one job, so that a test can start a child process without any program from outside. `RunHelperMode` in `TestMain.cpp` holds more than 40 modes. Examples are `record-arguments`, which stands in for the :term[code editor]{id=code-editor} that the editor starts, `console-output`, `exit-code`, `echo`, `sleep`, `guarded-abort`, `run-with-environment` and `write-component-schema`. The last one writes the component schema snapshot again.

A test that starts `cat`, Python or a real CMake depends on the machine: a different version, a missing program, a slower run. A test that starts its own binary depends on nothing it did not build. That is why no unit test uses an outside program.

The mode is also the only safe way to give a child another environment. `run-with-environment` takes environment assignments, each a name, an equals sign and a value, up to `--`, sets them in its own process and starts the program after `--` with the standard streams inherited. It ends with that program's exit code. The test process itself never changes.

The **fake CMake** is the same trick for the build tool. Suppose the variable `STRATA_TEST_FAKE_CMAKE` holds `succeed`, `fail` or `fail-configure`, and the binary starts with `-S` or `--build`. Then `RunAsFakeCMake` stands in for CMake.

With `succeed` it builds nothing and prints which step it ran. With `fail` it reports a :term[compiler error]{id=compile-error} in `Scripts/Broken.cpp`, and with `fail-configure` a CMake error in the :term[configure step]{id=configure-step}. The tests of script builds read those lines.

The fake editor is the same idea for the tests of the command-line client. When the binary starts as an editor (`Tests::IsFakeEditorLaunch`), it answers the way an editor does. No test needs a real editor window.

The `Package*` suites build in the system's temporary folder, where `MSBuild` does not track files (warning `MSB8029`). A build there can link a module again that did not change. A test must not rely on a build that leaves a module unchanged: it uses the fake CMake.

## The real code: why doctest's signal handlers are off

A fault in a script module must not take the engine down. `CrashGuard` catches the fault signals around each call into a module and turns them into a failure. Signal handlers belong to the process, and a process has one handler per signal. doctest installs its own handlers around every test case and restores the old ones afterwards. That would remove the guard's handlers and leave a script crash either not contained or reported as a failed test.

So `CMakeLists.txt` defines `DOCTEST_CONFIG_NO_POSIX_SIGNALS`. The cost is that a crash outside a guarded call ends the run without a name. `TestCrashReporter.cpp` pays that cost back: a doctest listener remembers the running case, and a fatal-signal handler prints it.

```cpp src="StrataTests/src/TestCrashReporter.cpp#L68-L76"
void test_case_start(const doctest::TestCaseData& data) override
{
	SetCurrentTestCase(data.m_test_suite, data.m_name);
	if (m_Trace)
	{
		std::fprintf(stderr, "[test case] %s\n", s_CurrentTestCase);
		std::fflush(stderr);
	}
}
```

The listener records the suite and the name when a case starts. With `STRATA_TEST_TRACE=1`, which continuous integration (CI) sets, it also prints each case as it starts. The last line before a dying process then names the culprit even when the crash skips the handler. The handler is installed during :term[static initialization]{id=static-initialization}, before any guard exists, and the guard passes faults outside guarded calls to it. On Windows doctest's own crash report names the case.

## The real code: shards and the check that guards them

`CoreShards.json` is the table the shards come from. Its sections are `OwnTests`, `FuzzSuites` and `Shards`. `OwnTests` holds the eight CTests with suites of their own, and `FuzzSuites` holds one filter, `*.Sweep`. `Shards` holds 13 shards, here sorted by name: `Asset`, `Core`, `Editor`, `EditorData`, `EditorUI`, `LoaderFaults`, `Network`, `Renderer`, `Samples`, `Scene`, `SceneTiming`, `Settling` and `Systems`. The Developer Guide and the build-test skill name 12; they omit `SceneTiming`, which runs the suites `Scene.Timing*` that the `Scene` shard excludes.

```json src="StrataTests/CoreShards.json#L14-L19"
"Shards": [
	{ "Name": "Core", "Suites": [ "Core*", "Math*", "Reflection*", "Engine*", "Architecture*", "PerfLab*", "TestHelpers*", "Testing*", "Docs*" ] },
	{ "Name": "Asset", "Suites": [ "Asset*" ] },
	{ "Name": "Scene", "Suites": [ "Scene*", "Project*", "Animation*" ], "Exclude": [ "Scene.Timing*" ] },
	{ "Name": "SceneTiming", "Suites": [ "Scene.Timing*" ] },
	{ "Name": "Systems", "Suites": [ "Physics*", "Audio*", "Scripting*", "World*" ], "Exclude": [ "Scripting.LoaderFaults", "Physics.Settling" ] },
```

A filter is a doctest pattern: `*` matches any characters, `?` matches one, and case does not matter. The `Scene` shard says `Scene*` and excludes `Scene.Timing*`, so the suite Scene.Timing.Fixed runs in `SceneTiming` and nowhere else. CMake reads the file at configure time and makes the CTests.

```cmake src="StrataTests/CMakeLists.txt#L239-L255"
	set(shardExcludes ${STRATA_OWN_TEST_SUITES})
	string(JSON excludeType ERROR_VARIABLE excludeError TYPE "${STRATA_CORE_SHARDS}" Shards ${index} Exclude)
	if(NOT excludeError)
		string(JSON excludeCount LENGTH "${STRATA_CORE_SHARDS}" Shards ${index} Exclude)
		math(EXPR lastExclude "${excludeCount} - 1")
		foreach(excludeIndex RANGE ${lastExclude})
			string(JSON exclude GET "${STRATA_CORE_SHARDS}" Shards ${index} Exclude ${excludeIndex})
			list(APPEND shardExcludes "${exclude}")
		endforeach()
	endif()
	string(REPLACE ";" "," shardSuites "${shardSuites}")
	string(REPLACE ";" "," shardExcludes "${shardExcludes}")
	add_test(NAME StrataTests.Core.${shardName}
		COMMAND StrataTests "--test-suite=${shardSuites}" "--test-suite-exclude=${shardExcludes}" --no-intro=true
		WORKING_DIRECTORY "$<TARGET_FILE_DIR:StrataTests>")
	set_tests_properties(StrataTests.Core.${shardName} PROPERTIES LABELS "core")
endforeach()
```

1. **Line 239:** the own tests' suites are always in the exclude list, whatever a shard's filters say.
2. **Lines 240-248:** the shard's own `Exclude` entries join them when the key exists.
3. **Lines 251-253:** the CTest runs `StrataTests` with the two filter lists, in the build's folder.
4. **Line 254:** every shard gets the label `core`, so `ctest -R StrataTests.Core` and `-L core` select all of them.

Run the :term[configure step]{id=configure-step} again after you edit the table: the file is a configure dependency.

The check is `CheckShards` in `ShardTests.cpp`. One test case starts a child process of the binary with `--list-test-suites`, which prints every suite name, and gives that list to `CheckShards` with the parsed table.

```cpp src="StrataTests/src/Testing/ShardTests.cpp#L118-L153"
ShardReport CheckShards(const ShardTable& table, const std::vector<std::string>& suites)
{
	ShardReport report;
	for (const std::string& suite : suites)
	{
		std::vector<std::string> runs;
		for (const Shard& run : table.Runs)
		{
			if (MatchesAny(suite, run.Suites) && !MatchesAny(suite, run.Exclude))
				runs.push_back(run.Name);
		}
		if (runs.empty())
		{
			report.Problems.push_back(fmt::format("{} runs in no Core shard and no CTest of its own: add it to StrataTests/CoreShards.json", suite));
		}
		else if (runs.size() > 1)
		{
			std::string names;
			for (const std::string& run : runs)
				names += (names.empty() ? "" : ", ") + run;
			report.Problems.push_back(fmt::format("{} runs in several CTests ({}): exclude it from all but one", suite, names));
		}
	}
	for (const Shard& run : table.Runs)
	{
		for (const std::string& filter : run.Suites)
		{
			bool used = false;
			for (const std::string& suite : suites)
				used = used || MatchesFilter(suite, filter);
			if (!used)
				report.UnusedFilters.push_back(fmt::format("{}: {}", run.Name, filter));
		}
	}
	return report;
}
```

1. **Line 126:** the rule in one line: a run takes a suite when a `Suites` filter matches and no `Exclude` filter does.
2. **Line 129:** no run is the first problem, a suite that runs nowhere.
3. **Lines 141-151:** a filter that matches no suite is only reported, because a build may lack a module whose suites the table names.

The matching code, `MatchesFilter`, is a small matcher for patterns with stars. At a `*` it remembers the place. When a later character fails to match, it returns to the star and lets the star take one more character. A second test case lists the cases that are outside every suite with `--list-test-cases --test-suite-exclude=?*`. That filter excludes every suite name of at least one character, so only the cases without a suite remain.

When the check fails, doctest prints the message that `INFO` collected. This is the message for a new suite called Water.Waves:

```text
StrataTests/CoreShards.json:
  Water.Waves runs in no Core shard and no CTest of its own: add it to StrataTests/CoreShards.json
```

The first line names the table to edit. The second line names the suite and says what to do.

:::example[Where three suite names run]
Take Scene.Timing.Fixed. For the `Scene` shard, `Scene*` matches it but `Scene.Timing*` excludes it. For `SceneTiming`, `Scene.Timing*` matches it, and that shard excludes only the own tests' suites. One run: correct.

Take `GPU.Startup`. The `Renderer` shard matches `Renderer*`, not `GPU*`. The own test `StrataTests.GPU` matches `GPU*`, and every shard excludes `GPU*`. One run.

Take Water.Waves, which no filter matches. Zero runs: the check fails and names it. The fix is one line in the `Suites` of a shard that is under its minute.
:::

The command `ctest -N -L core` lists the shards that CTest knows from the label `core`, without running them:

```text capture="core-shard-list"
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

1. **Lines 1–13:** each line is one shard as a CTest, and the number after `#` is its position in the list.
2. **Line 15:** the count of the tests that carry the label `core`.

## The real code: labels, fixtures and locks

The tests of the build carry labels: `core` (the shards), `fuzz`, `gpu`, `perf`, `package`, `feature` and `tools`. A person selects by label. The command `ctest --preset linux-debug -LE gpu` skips what needs a graphics device, and `ctest -L perf` runs the perf tests. CI skips `perf`, whose numbers mean something only on the reference machine.

A **fixture** (CTest) is a test that prepares or removes something that other tests need, declared with `FIXTURES_SETUP`, `FIXTURES_REQUIRED` and `FIXTURES_CLEANUP`. A chain such as `StrataExport.Clean`, then `StrataEditor.Export`, then the runtime tests lets CTest order the steps and skip the dependants when a setup fails, even under `-j 8`.

A **resource lock** is a name that tests hold while they run, so that CTest never runs two tests with the same name at once, however many jobs it has. The tests with the label `package` hold `RESOURCE_LOCK toolchain`. Builds that run at the same time through one :term[toolchain]{id=build-tools} fail at random, with errors such as C1090 and `LNK` failures from `MSBuild` and `mspdbsrv`.

**`RUN_SERIAL`** is a property that makes CTest run a test alone, with nothing else beside it. The perf tests have it, because another process would change their timings.

Nothing else is shared between CTests. Each test process makes its files in temporary folders of its own, and the editors and games that CTests start use free ports and private session folders.

## The real code: corruption sweeps and the fuzz run

A loader must reject a damaged file without crashing, and the way to test that is to damage files. A **sweep** is a test that damages one valid file in many ways, one at a time, and checks that the code under test fails cleanly or reads right every time. Sweeps live in suites whose names end in `.Sweep`, so `Asset.Pack.Sweep` is the sweep of the pack format. The page on [corruption and crash safety](../assets/robustness.md) teaches what the loaders do about damaged files.

Two kinds of damage are usual: a cut, where the file ends early at an offset, and a changed :term[byte]{id=byte}, where one byte is flipped. A file of 10,000 bytes has 10,000 cut lengths and 10,000 flips. A real pack is far larger, and a Debug build cannot afford millions of attempts in each shard.

Strata therefore sweeps in two modes. In a shard the sweep takes a sample. In `StrataTests.Fuzz`, the **fuzz run**, the sweeps run with `STRATA_TEST_SWEEP=full` and every offset is tested. The fuzz run exists in Release and :term[Dist]{id=dist} only, and every Release `ctest -LE perf`, including CI's, runs it. The sample keeps the shards fast, and the whole run still checks every offset.

```cpp src="StrataTests/src/TestHelpers.cpp#L700-L737"
std::vector<size_t> SelectSweepOffsets(size_t size, const std::vector<SweepRange>& mustInclude, size_t boundary, size_t randomCount)
{
	std::vector<size_t> offsets;
	if (size == 0)
		return offsets;
	if (IsFullSweep())
	{
		offsets.resize(size);
		for (size_t offset = 0; offset < size; offset++)
			offsets[offset] = offset;
		return offsets;
	}

	for (const SweepRange& range : mustInclude)
	{
		for (size_t offset = range.Begin; offset < std::min(range.End, size); offset++)
			offsets.push_back(offset);
	}
	constexpr size_t c_BoundaryReach = 8;
	if (boundary > 0)
	{
		for (size_t edge = 0; edge <= size; edge += boundary)
		{
			const size_t first = edge > c_BoundaryReach ? edge - c_BoundaryReach : 0;
			for (size_t offset = first; offset <= edge + c_BoundaryReach && offset < size; offset++)
				offsets.push_back(offset);
		}
	}
	// A fixed seed: every run tests the same offsets, so a failure repeats.
	std::mt19937_64 random(0x5EEDF00DCAFEull ^ size);
	std::uniform_int_distribution<size_t> pick(0, size - 1);
	for (size_t index = 0; index < randomCount; index++)
		offsets.push_back(pick(random));

	std::sort(offsets.begin(), offsets.end());
	offsets.erase(std::unique(offsets.begin(), offsets.end()), offsets.end());
	return offsets;
}
```

1. **Lines 705-711:** in a full sweep every offset is returned and nothing else matters.
2. **Lines 713-717:** otherwise every offset of the ranges the caller names comes first, such as a :term[header]{id=header} and the tables.
3. **Lines 719-727:** the bytes near each block edge follow, 8 before and 8 after every multiple of the block size, because bugs gather at block edges.
4. **Line 729:** the seed is fixed and mixed with the size, so every run on the same file tests the same offsets.
5. **Lines 734-735:** the offsets are sorted and made unique, so a sweep never tests one twice.

The pack sweep in `StrataTests/src/Asset/AssetPackTests.cpp` calls it with the range of the header, the range of the tables at the file's end and the pack's entry alignment, `AssetPack::c_EntryAlignment`, as the boundary. A fixed seed is the whole point. If the seed came from the clock, a failure in a shard would not come back at the next run, and the developer could not find it again. With a fixed seed the failing offset is the same in every run, and the test prints it with `CAPTURE`.

Strata has no coverage-guided fuzzer, such as `libFuzzer` or `AFL`. Its sweeps test fixed, seeded offsets, and `SelectSweepIterations(sample, full)` does the same for sweeps that draw random cases.

:::example[How many offsets a sample takes]
Take a file of 10,000 bytes, a header range of 64 bytes, a block size of 4,096 and the default 512 random offsets. The header gives offsets 0 to 63: 64 offsets. The block edges are 0, 4,096 and 8,192. Each edge adds the bytes 8 before and 8 after it.

The edge 0 adds 0 to 8, which the header holds already. The edge 4,096 adds 4,088 to 4,104 (17 offsets) and the edge 8,192 adds 8,184 to 8,200 (17 offsets). That makes 64 + 17 + 17 = 98 distinct offsets. The 512 seeded draws add at most 512 more. The sample is at most 610 of 10,000 offsets, 6 %, and the same 610 every time.
:::

## The real code: the helpers tests share

`StrataTests/src/TestHelpers.h` holds the helpers that most suites use.

- `WaitUntil(condition, timeout)` checks a condition every 5 ms until it is true or the time is up, and returns the final value. A test waits by the clock or a condition, never by frames.
- `LogCapture` collects the log entries written since its creation and requires that the log buffer dropped none.
- `ScopedEnvironmentVariable` sets a variable for the length of one scope. Use it only where no child is involved: a child gets its environment from the helper mode.
- `CopySampleProject(name)` copies a sample into a new temporary folder.
- `CheckSceneCaches` in `StrataTests/src/Scene/SceneTestUtils.h` compares the scene's caches (the hierarchy, the world transforms and the game UI's layout) with values computed again from the scene, for tests that write transforms.
- `RunCommandToCompletion` in `StrataTests/src/Editor/CommandTestUtils.h` runs an editor command that defers until it ends.

`ImGuiHarness`, which draws the editor's interface without a window, belongs to [the page on testing the user interface](../editor-ui/ui-testing.md).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One CTest per test case (a discovery step lists the cases) | Projects that use the CMake discovery of doctest or `GoogleTest` | Timing, repeats and :term[parallelism]{id=parallelism} per case | Thousands of process starts, each registering every module |
| One CTest for the whole binary | Small projects | Nothing to maintain | A serial run of 500 to 804 s on `macOS`, and one failure hides the rest |
| A coverage-guided fuzzer (`libFuzzer`, `AFL`) | Projects that read untrusted data in bulk | Inputs that nobody thought of, found by feedback | A fuzz target and a saved corpus for each :term[parser]{id=parser}; the sweeps need none |
| A new random seed at each run | Libraries for property-based testing | Different inputs at every run, so more coverage over time | A failure that does not come back |

## How it is tested

The test program tests itself. The suite `Testing.Shards` holds four test cases. One checks the matcher against doctest's rules, and one checks that suites in no shard or in several are found. One checks that the own tests omit the suites they exclude, and one is the check of every suite described above.

The suite `TestHelpers` checks `SelectSweepOffsets`, `SelectSweepIterations` and the other helpers, in the shard `Core`.

Run them directly:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Testing.Shards
ctest --preset windows-debug -N -L core
ctest --preset windows-debug -R StrataTests.Core -j 8
```

The first line runs the check in one process. The second lists the shards without running them. The third runs all shards side by side. Release builds add `ctest --preset windows-release -R StrataTests.Fuzz`.

## Changing it safely

To add a suite with a new prefix, put its cases in a `TEST_SUITE` and add the prefix to a shard in `CoreShards.json`. Run the configure step again, then `Testing.Shards`. Choose the shard by the minute: split a shard that takes more than about 60 s in Debug. A suite that needs a graphics device, a started program or a perf budget is not for a shard. It belongs to an own test, the work of [the page about test kinds](test-kinds.md).

For a new helper mode, add a branch to `RunHelperMode` that reads its arguments and ends with a code. Start it from the test with `Process::Run` and the test binary's own path (`Tests::GetTestExecutablePath()`), never with `cat`, Python or CMake.

A test that crashes the dynamic loader, such as a module that faults in static initialization, goes in the `LoaderFaults` shard, as the next section explains. A corruption sweep gets a suite named `*.Sweep`, takes its offsets from `SelectSweepOffsets` and prints each offset with `CAPTURE`.

Before the commit, run the shard of the suite, `Testing.Shards` and the whole `ctest -j 8`. A new regression test must fail without its fix: remove the fix once and see it fail.

## What went wrong before

On Linux a crash in the :term[static initialization]{id=static-initialization} of a library leaves the lock of the dynamic loader held by the main thread. A test that loads such a module is fine until a later thread needs the loader. A job thread's first `thread_local` with a :term[destructor]{id=destructor} is one such need, and it blocks for good and hangs the run.

The fix is organizational. Such tests live in the `LoaderFaults` shard, the suite `Scripting.LoaderFaults`, where no other test runs jobs beside them. The `Systems` shard excludes the suite, and `Testing.Shards` keeps both in line.

## Summary

- Every suite runs in exactly one shard or own CTest, and the labels `core`, `gpu`, `perf` and `package`, the lock `toolchain` and `RUN_SERIAL` keep parallel runs safe.
- A new suite prefix gets a line in `CoreShards.json`; `Testing.Shards` fails and names a suite in no run or in two, and a case outside a suite.
- A helper mode turns `StrataTests` into the child process that a test needs, so tests depend on no outside program and never change their own environment.
- doctest's signal handlers are off because they would take `CrashGuard`'s away; a listener names the running case, and `STRATA_TEST_TRACE=1` prints each case.
- A sweep selects offsets with a fixed seed, so failures repeat; a shard runs a sample and `StrataTests.Fuzz` runs every offset.

## Check yourself

1. The suite `Scripting.LoaderFaults` matches the filter `Scripting*` of the `Systems` shard. In which shard does it run, and why?

   :::answer{tests="shard-contract"}
   In the `LoaderFaults` shard only. The `Systems` shard lists `Scripting.LoaderFaults` under `Exclude`, so the suite runs once. The suite stands apart because a module that crashes in static initialization can leave the loader's lock held on Linux, and a job thread would then hang.
   :::

2. You add a `TEST_SUITE` called Water.Waves and nothing else. What happens?

   - A. All tests pass; a new suite is not checked.
   - B. `Testing.Shards` fails and names Water.Waves; the shards pass, and the new suite ran in none.
   - C. The build fails at configure time.
   - D. Water.Waves runs in the `Core` shard by default.

   :::answer{tests="add-suite"}
   B. No filter matches the new prefix, so the suite runs nowhere, and the check names it. A is the mistake the check exists for: a suite that never ran looks green. C is wrong because the build does not read suite names. D is wrong because a shard runs only what its filters match.
   :::

3. Why does `SelectSweepOffsets` seed its generator with a constant mixed with the size, and not with the time?

   :::answer{tests="sweep-seeds"}
   The same file then gets the same offsets at every run, so a failing offset comes back and a developer can study it. The size keeps two files of different sizes from drawing the same positions. A time seed would give a different sample each run, and a failure in a shard could vanish at the next one.
   :::

4. A script crashes inside a guarded call of a test. Which handler runs, and what would happen if the doctest definition were removed?

   :::answer{tests="crash-handlers"}
   `CrashGuard`'s handler runs and contains the crash. Without `DOCTEST_CONFIG_NO_POSIX_SIGNALS`, doctest would install its handlers around each case and restore the old ones afterwards. That removes the guard's handlers, and the crash is either not contained or reported as a failed test.
   :::

5. A test needs a child whose `VK_DRIVER_FILES` points at no driver. Why does it not call `SetEnvVar` and start the child?

   :::answer{tests="helper-process"}
   The environment belongs to the whole test process, and other tests run beside it with `-j 8`: a changed variable would reach them too. The test starts `--strata-test-helper=run-with-environment` with the assignment, which sets it only in the helper process, and the helper starts the child.
   :::

## Exercises

1. **Basic.** You write a `TEST_SUITE` called Water.Waves with one case. What do you change so that CTest runs it, and in which shard do you put it?

   :::answer[Worked solution]{tests="add-suite"}
   Run `Testing.Shards` first and read the message that names Water.Waves. Then add `"Water*"` to the `Suites` of a shard whose time allows it: `Core` for a quick suite of pure logic. Run `cmake --preset windows` again, because the file is a configure dependency, and run the check again: it passes. If the suite takes longer than a minute in Debug, add a shard `Water` with `"Suites": [ "Water*" ]` instead.
   :::

2. **Medium.** Follow `--strata-test-helper=run-with-environment` by a search from `main` to the code that runs it. Say what the child's environment holds and why the test process's own is untouched.

   :::answer[Worked solution]{tests="helper-process"}
   Search for `strata-test-helper` in `StrataTests/src/TestMain.cpp`. In `main`, the prefix is found and, for a helper, `RunHelperMode(helperMode, argc, argv)` is called after the modules are registered. `RunHelperMode` holds the branch `mode == "run-with-environment"`. It reads the arguments up to `--` as name and value pairs, calls `Platform::SetEnvVar` for each in the helper's own process, then starts the program after `--` with `ProcessOutputMode::Inherit` and returns its exit code.

   The child's environment is the environment of the test process, including `STRATA_RUNTIME_DIR`, which `main` of the test process set, plus the assignments. The test's own environment is untouched because the assignments are made in the helper, a separate process.
   :::

3. **Medium.** Add a helper mode `write-lines` that writes N lines of text to :term[standard output]{id=standard-output}, and a test that runs it and checks the output and the exit code.

   :::answer[Worked solution]{tests="helper-process"}
   In `RunHelperMode`, a new branch reads the count and prints the lines. The mode ends with 0, and other modes end with 99 when an argument is wrong.

   ```cpp pseudocode
   if (mode == "write-lines" && argc > 2)
   {
   	for (int line = 0; line < std::atoi(argv[2]); line++)
   		std::printf("line %d\n", line);
   	return 0;
   }
   ```

   The test starts the binary with its own path and reads what the child printed. The expected output has exactly three lines.

   ```cpp pseudocode
   ProcessSpecification specification;
   specification.Executable = Tests::GetTestExecutablePath();
   specification.Arguments = { "--strata-test-helper=write-lines", "3" };
   const Process::RunResult result = Process::Run(specification, std::chrono::seconds(30));
   REQUIRE(result.Started);
   CHECK(result.ExitCode == 0);
   CHECK(result.Output == "line 0\nline 1\nline 2\n");
   ```

   The time limit makes a child that hangs fail the test, not the run. On Windows the output may hold carriage returns: compare after removing them.
   :::

4. **Hard.** Write a corruption sweep for a parser of names, sampled and full, whose failures repeat.

   :::answer[Worked solution]{tests="sweep-seeds" solution="sketches/engineering-test-program-sweep.cpp"}
   The format is one byte for the count of names and, for each name, one length byte and the characters. The parser checks every length against the bytes that remain, as [the page on corruption and crash safety](../assets/robustness.md) teaches.

   The sweep cuts the file at each selected length, which must always fail. It then flips one byte at each selected offset, which must fail or read right and never crash.

   The offsets come from a function with three parts, like Strata's. A full sweep takes all offsets. A sample takes the header, the bytes near the block edges and a few draws from a fixed seed, sorted and made unique. The sketch is the whole program.

   ```cpp sketch="engineering-test-program-sweep.cpp"
   // A corruption sweep for a small parser: truncation at every selected length and one changed byte at every selected offset.
   #include <algorithm>
   #include <cstdint>
   #include <cstdio>
   #include <cstdlib>
   #include <random>
   #include <vector>

   // The format: one byte holds the number of names; each name is a length byte followed by that many characters.
   static bool ParseNames(const std::vector<uint8_t>& bytes, size_t& count)
   {
   	if (bytes.empty())
   		return false;
   	size_t position = 1;
   	for (uint8_t name = 0; name < bytes[0]; name++)
   	{
   		if (position >= bytes.size())
   			return false;
   		const size_t length = bytes[position++];
   		if (length > bytes.size() - position)
   			return false;
   		position += length;
   	}
   	count = bytes[0];
   	return position == bytes.size();
   }

   // Every offset in a full sweep; else the header, the bytes near the block edges and offsets from a fixed seed.
   static std::vector<size_t> SelectOffsets(size_t size, bool full, size_t header, size_t boundary, size_t randomCount)
   {
   	std::vector<size_t> offsets;
   	for (size_t offset = 0; offset < size; offset++)
   	{
   		const size_t distance = offset % boundary < boundary / 2 ? offset % boundary : boundary - offset % boundary;
   		if (full || offset < header || distance <= 2)
   			offsets.push_back(offset);
   	}
   	std::mt19937_64 random(0x5EED ^ size);
   	for (size_t index = 0; !full && index < randomCount; index++)
   		offsets.push_back(random() % size);
   	std::sort(offsets.begin(), offsets.end());
   	offsets.erase(std::unique(offsets.begin(), offsets.end()), offsets.end());
   	return offsets;
   }

   int main()
   {
   	std::vector<uint8_t> good = { 3 };
   	for (uint8_t length : { 4, 2, 5 })
   	{
   		good.push_back(length);
   		good.insert(good.end(), length, 'x');
   	}
   	for (bool full : { false, true })
   	{
   		const std::vector<size_t> offsets = SelectOffsets(good.size(), full, 2, 8, 6);
   		size_t wrongAccepts = 0;
   		size_t rejected = 0;
   		for (size_t length : offsets)
   		{
   			size_t count = 0;
   			wrongAccepts += ParseNames(std::vector<uint8_t>(good.begin(), good.begin() + static_cast<std::ptrdiff_t>(length)), count) ? 1 : 0;
   		}
   		for (size_t offset : offsets)
   		{
   			std::vector<uint8_t> changed = good;
   			changed[offset] ^= 0xA5;
   			size_t count = 0;
   			rejected += ParseNames(changed, count) ? 0 : 1;
   		}
   		std::printf("%s: %zu of %zu offsets, truncated files accepted %zu, changed bytes rejected %zu\n", full ? "full   " : "sampled", offsets.size(),
   			good.size(), wrongAccepts, rejected);
   	}
   	return 0;
   }
   ```

   ```text output-of="engineering-test-program-sweep.cpp"
   sampled: 12 of 15 offsets, truncated files accepted 0, changed bytes rejected 4
   full   : 15 of 15 offsets, truncated files accepted 0, changed bytes rejected 4
   ```

   1. **Lines 10-26:** the parser compares every length with the bytes that remain, so a cut file ends in a failure and never in a read past the end.
   2. **Lines 29-43:** the selection of offsets, with the full mode first.
   3. **Line 38:** the seed is a constant mixed with the size, so the draws repeat.
   4. **Lines 54-72:** both sweeps run in both modes, and the program counts the cut files that were accepted: it must stay 0.

   The sample tests fewer offsets than the full sweep and accepts no cut file in either run. In a real suite the names would stand in a `.Sweep` suite and `Tests::IsFullSweep()` would replace the flag. Run it twice and the sampled line does not change: the seed is fixed.
   :::

## Where it lives in Strata

- `StrataTests/CMakeLists.txt`: the binary, its definitions, the test script modules, the shards, `StrataTests.Fuzz`, labels, fixtures and locks.
- `StrataTests/CoreShards.json`: the own tests, the fuzz filter and the 13 shards.
- `StrataTests/src/TestMain.cpp`: `main`, `RunHelperMode` and `RunAsFakeCMake`.
- `StrataTests/src/TestCrashReporter.cpp`: the listener and the fatal-signal handler.
- `StrataTests/src/Testing/ShardTests.cpp`: `MatchesFilter`, `CheckShards` and the suite `Testing.Shards`.
- `StrataTests/src/TestHelpers.h` and `StrataTests/src/TestHelpers.cpp`: `WaitUntil`, `LogCapture`, `ScopedEnvironmentVariable`, `CopySampleProject`, `SelectSweepOffsets`.
- `StrataTests/src/Asset/AssetPackTests.cpp`: the suite `Asset.Pack.Sweep`, the example of a sweep.
- Environment: `STRATA_TEST_SWEEP`, `STRATA_TEST_TRACE`, `STRATA_TEST_FAKE_CMAKE`.

## Further reading

- CMake's manual on `ctest` and on the test properties `LABELS`, `RESOURCE_LOCK`, `RUN_SERIAL` and `FIXTURES_SETUP` (cmake.org): what each property does. Intermediate.
- The documentation of doctest, "Command line" and "Test suites": the filters that the shards use. Beginner.
- The documentation of libFuzzer, from the LLVM project: how a coverage-guided fuzzer finds inputs that crash a parser. Advanced.
