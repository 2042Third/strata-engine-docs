---
id: core/debugging
title: "Debugging the engine: debuggers, asserts, the log and crash reports"
description: "Find a bug in Strata's own code with a debugger, its asserts, its log and what a crash leaves behind, on Windows, Linux and macOS."
kind: internals
size: L
tracks: [E]
needs: [core/first-change, core/platform, basics/debugging]
time: 90
learn:
  - id: debug-engine
    text: run the engine's test program under the debugger of your system with one test case selected, in Debug or in Release
  - id: assert-action
    text: predict what a failed assert does with a debugger attached, without one and with a replaced handler
  - id: log-writer
    text: explain which log lines a crash can lose, and why a warning reaches the file before the next line of code runs
  - id: log-file
    text: find the log file of the editor, of a game and of a test run, and say when each one is emptied
  - id: crash-left
    text: find which test case crashed from the output of the test program, and say what a crash in engine code leaves
since: 0.3.0
status: final
---

When something in Strata goes wrong, four tools can tell you what happened. A :term[debugger]{id=debugger} stops the program at a line. An assert names the rule that code broke. The log records what the engine did while it ran. A crash leaves some traces, and Strata leaves most of them to the :term[operating system]{id=operating-system}.

This page shows how Strata builds each tool, and how you use it on Windows, Linux and macOS. The page applies the method of [debugging, the method](../basics/debugging.md) to Strata, and does not teach that method. It omits debugging a game's scripts, debugging the :term[graphics card]{id=gpu}, and how to write log calls.

## The problem and how engines solve it

An engine is harder to debug than a small program for four reasons. The code that runs fast is :term[optimized]{id=optimization}, and an optimized build moves, merges and removes lines and variables, so a debugger stops at places that do not match the source. An engine runs many threads at once, so the order of events changes from run to run, and a thread you stop may hold up the others. Much of the work happens on the graphics card, where an ordinary debugger cannot step. Last, a crash often lands in code you did not write: a library, or a script of a game.

Engines answer with a few tools, one for each reason. A build that keeps the source's shape serves stepping, asserts stop at the first broken rule, and a log records the order of events without a debugger. Some engines add crash reports. Each tool costs something, and Strata chose which costs to pay. The rest of the page shows what it paid.

## Where each tool hooks in

The map shows the path of two things: a log call, and a failed assert. A :term[logger]{id=logger} is a named object that takes the calls of one family of :term[macros]{id=macro} and gives every line to the same sinks, the objects that store or print it. A failed assert logs first, so both meet in a logger. From there a line goes two ways: at once into a ring of recent messages, and into a queue that a writer thread empties into the console and the file.

```mermaid caption="A log call and a failed assert meet in the loggers. The ring is filled at once and read by the console panel and a command. The writer thread writes the console and the file. A failed assert asks the handler, which stops the debugger or ends the program." alt="A diagram of boxes and arrows. A log call and a failed assert both lead to the loggers. The loggers lead to a ring of recent messages, which the console panel and a command read, and to a queue, which a writer thread empties into the console and the log file. The failed assert also leads to a handler, which either stops in the debugger or ends the program."
flowchart TD
	call["ST_CORE_WARN, ST_WARN, script logs"] --> loggers["Loggers: Strata, App, Script"]
	assert["ST_CORE_ASSERT, ST_CORE_VERIFY"] --> failure["HandleAssertFailure"]
	failure --> loggers
	failure --> handler["AssertHandler: Break, Abort, Continue"]
	handler --> debugger["ST_DEBUGBREAK: the debugger stops"]
	handler --> abort["std::abort: the process ends"]
	loggers --> ring["LogBuffer: the ring"]
	loggers --> queue["BackgroundLogSink: the queue"]
	ring --> readers["Console panel, log.read"]
	queue --> writer["Writer thread"]
	writer --> files["Console and log file"]
```

The code lives in `Strata/src/Strata/Core/`: `Log.h` and `Log.cpp` hold the loggers and the ring, `BackgroundLogSink.h` and `BackgroundLogSink.cpp` the queue and the writer, and `Assert.h` and `Assert.cpp` the asserts. The debugger and its detection belong to `Platform`, in `Strata/src/Strata/Core/Platform.h`, with one implementation for each system under `Strata/src/Platform/`. The test program adds its own crash reporter in `StrataTests/src/TestCrashReporter.cpp`.

Two threads matter. Any thread may log, including the :term[main thread]{id=main-thread}, which owns the frame. The writer thread, named `Strata Log Writer` in a debugger's list of threads, is the only thread that touches the console and the file while the program runs. Keep both in mind when you stop in a debugger: stopping the main thread does not stop the writer, so the lines already queued still reach the file.

## The contract

This section says what you can rely on in each tool, and what you must do.

### The engine under a debugger

A debugger needs a build that carries :term[debug information]{id=debug-information}, and that is a source build, as in [your first engine change](first-change.md). The :term[configure step]{id=configure-step} of your preset writes the project files; each system uses them differently. The test program, `StrataTests`, is the best target to practise on, because it starts in a second and runs one test case when you ask. The editor works the same way.

::::tabs{sync=os}
:::tab[Windows]
The preset `windows` writes a Visual Studio solution, `build/windows/Strata.slnx`. Open it, right-click the project `StrataTests` in the Solution Explorer, and choose "Set as Startup Project". Then open the project's properties, page "Debugging", and write the selection into "Command Arguments", for example `--test-suite=Core.Log`. The key **F5** starts the program under the debugger, and **F9** sets a :term[breakpoint]{id=breakpoint} on the current line. With Visual Studio 2022, the preset is `windows-vs2022`, and the solution is `build/windows-vs2022/Strata.sln`.
:::
:::tab[Linux]
The preset `linux` uses Ninja and builds into `build/linux`. Install the debugger `gdb` with your package manager, and start the test program under it. The command `gdb --args` takes the program and then its arguments, so the program sees the arguments, not `gdb`. Inside `gdb`, `run` starts it, `break` sets a breakpoint, and `bt` prints the :term[call stack]{id=call-stack}.
:::
:::tab[macOS]
The preset `macos` also uses Ninja and builds into `build/macos`. Xcode's developer tools include the debugger `lldb`. The command `lldb --` takes the program and its arguments. Inside `lldb`, `run` starts the program, `breakpoint set` sets a breakpoint and `bt` prints the call stack.
:::
::::

The commands below start the test program on Linux and on macOS, after a `Debug` build, with every test case of the suite `Core.Log` selected. Each runs from the engine's folder.

```sh
gdb --args build/linux/bin/Debug/StrataTests --test-suite=Core.Log
lldb -- build/macos/bin/Debug/StrataTests --test-suite=Core.Log
```

The first line is for Linux and the second for macOS. You get a prompt at which you type `run`, and the program runs until it ends or stops.

Visual Studio is not the only choice. :term[CMake]{id=cmake} can write a file, `compile_commands.json`, that lists the exact :term[compiler]{id=compiler} command of every :term[source file]{id=source-file}. The engine asks for it (`CMAKE_EXPORT_COMPILE_COMMANDS` in `CMake/StrataConfigurations.cmake`), and a Ninja build writes it into its build folder. Another :term[code editor]{id=code-editor}, such as Visual Studio Code with a language server, reads it to find the headers of each file and to show the same errors the compiler shows. The Visual Studio generator writes no such file; on Windows, a Ninja preset (`windows-ninja`) does.

#### `Debug` for stepping, `Release` for a bug that hides

`Debug` compiles without optimization, so each line is a place a debugger can stop and each variable holds a value you can read. Use it first.

`Release` is optimized and keeps the asserts. Use it when a bug appears only there: a variable read before it is set, a race between threads, a timing problem. On Windows its compile and link options keep debug information, so a debugger still shows source lines; it may show "optimized out" for a variable, and stepping may jump between lines. Then place the breakpoint on a call, or log the value. On Linux and macOS `Release` compiles without `-g`, so a debugger shows no source lines or variables there.

`Dist` is the third configuration, for exported games: it compiles the asserts out. A check you need in a shipped game is a verify, which stays. The page [your first engine change](first-change.md) shows how the configurations differ.

### Asserts while debugging

An assert is a check that a rule of the code still holds. `ST_CORE_ASSERT` checks a rule of the engine, and `ST_ASSERT` checks one of a program built on it. `ST_CORE_VERIFY` and `ST_VERIFY` do the same in every configuration, as [conventions](conventions.md) describes.

When the condition is false, the :term[macro]{id=macro} calls `HandleAssertFailure`. That function logs a critical line and flushes it, asks the **assert handler** what to do, and acts on the answer. The assert handler is a function that gets the failure (the condition, the file, the line and the message) and returns one of three actions.

- `Break` stops in the debugger at the assert's own line, through `ST_DEBUGBREAK`.
- `Abort` shuts the log down, which writes what is queued, and ends the process with `std::abort`.
- `Continue` ignores the failure and lets the program continue; tests use it.

The code that does this is short, and it is the best thing to read when an assert stops you.

```cpp src="Strata/src/Strata/Core/Assert.cpp#L16-L66"
static AssertAction DefaultAssertHandler(const AssertInfo&)
{
	if (Platform::IsDebuggerAttached())
		return AssertAction::Break;

	return AssertAction::Abort;
}

void SetAssertHandler(AssertHandler handler)
{
	s_AssertHandler.store(handler);
}

namespace Detail
{

	AssertAction HandleAssertFailure(bool isCore, bool isVerify, const char* condition, const char* file, int line, std::string message)
	{
		AssertInfo info;
		info.IsCoreAssert = isCore;
		info.IsVerify = isVerify;
		info.Condition = condition;
		info.File = file;
		info.Line = line;
		info.Message = std::move(message);

		const char* kind = isVerify ? "Verify" : "Assertion";
		if (Log::IsInitialized())
		{
			auto& logger = isCore ? Log::GetCoreLogger() : Log::GetClientLogger();
			if (info.Message.empty())
				logger->critical("{} '{}' failed at {}:{}", kind, condition, file, line);
			else
				logger->critical("{} '{}' failed at {}:{}: {}", kind, condition, file, line, info.Message);
			logger->flush();
		}
		else
		{
			std::fprintf(stderr, "%s '%s' failed at %s:%d: %s\n", kind, condition, file, line, info.Message.c_str());
			std::fflush(stderr);
		}

		AssertHandler handler = s_AssertHandler.load();
		const AssertAction action = handler ? handler(info) : DefaultAssertHandler(info);
		if (action == AssertAction::Abort)
		{
			Log::Shutdown();
			std::abort();
		}
		return action;
	}
```

1. **Line 18:** with a debugger attached, the default answer is `Break`.
2. **Line 21:** without one, the default answer is `Abort`.
3. **Lines 45–50:** the failure is logged as a critical line and flushed, so it is on disk before any handler runs.
4. **Lines 58–59:** a replaced handler answers; with none, the default handler does.
5. **Lines 60–64:** on `Abort` the log shuts down, which writes what is queued, and the process ends.

The default handler is the one at the top: with a debugger attached it answers `Break`, and without one `Abort`. A program or a test may replace it with `SetAssertHandler`, and `SetAssertHandler(nullptr)` restores the default. The test of the physics module does this to check that a bad shape asserts and is refused: its handler answers `Continue`, counts the failure, and the test restores the default afterwards.

`Platform::IsDebuggerAttached` asks each system a different question. Windows calls `IsDebuggerPresent`. Linux reads the line `TracerPid:` of `/proc/self/status`, which is not zero while a debugger traces the process. macOS asks the kernel whether a debugger traces the process.

The break itself differs too. On Windows, `ST_DEBUGBREAK` is `__debugbreak()`, an instruction that Visual Studio shows as a breakpoint at the line. With GCC and Clang it is `__builtin_trap()`, which the processor reports as a signal, and `gdb` or `lldb` shows that as a stop at the line. After a failed assert, do not continue: the code that follows may rest on the broken rule. Read the stack and the variables, then end the program.

:::rule[Asserts check programmer errors, and nothing else]
`ST_CORE_ASSERT` is for programmer errors and is compiled out of `Dist`, so its condition must have no side effects. A check that must stay in shipping builds is `ST_CORE_VERIFY`. A failure that can happen in a correct program, such as a missing file, returns an error and logs; it never asserts. The reason: an assert that fires on a bad input from a player would end that player's game, and an assert with a side effect would change the program between `Debug` and `Dist`. See [conventions](conventions.md).
:::

### The log as a tool

The log is the tool that works when no debugger is attached, and it is the only record of a run that ended. Its levels, from low to high, are `Trace`, `Info`, `Warn`, `Error` and `Critical`. Three loggers share one set of destinations: `Strata` for the engine, `App` for an editor or a game, and `Script` for game scripts. How to choose a level is the subject of [conventions](conventions.md). Here the question is where the lines go.

#### The ring: `LogBuffer`

A **ring buffer** keeps a fixed number of the newest entries and replaces the oldest one when it is full. `LogBuffer` is a ring of log entries; its default capacity is 4,096, and a :term[mutex]{id=mutex} guards it. Each entry gets a **sequence number**: the first entry is 1, each next entry is one higher, and a number is never used twice. A reader remembers the last number it saw and asks for the entries after it, with `GetEntries(afterSequence)`. The idea and its costs are the subject of [data structures](../basics/data-structures.md).

A worked example with the default capacity: the engine logs 5,000 lines. The ring holds the last 4,096, which carry the sequence numbers 905 to 5,000, because 5,000 − 4,096 + 1 = 905. A reader that last saw number 800 asks for entries after 800 and receives 905 to 5,000. It sees from the jump that 104 entries, 801 to 904, were lost before it looked. This is why the ring suits a console: it costs a fixed amount of memory, and the reader can tell when it lost lines.

Two readers use it. The editor's **Console** panel shows the entries, with four switches (**Trace**, **Info**, **Warnings** and **Errors**) that hide levels, a filter box, **Clear** and **Auto-scroll**.

::figure{id=console-panel}

The command `log.read` returns the entries to a client, oldest first after a sequence number, or newest first. With the parameters below it returns the warnings and worse that come after entry 120, from the engine's logger only.

```json
{ "after": 120, "minLevel": "Warn", "logger": "Strata", "limit": 50 }
```

Save them as `logread.json` and run `StrataCLI call log.read '@logread.json'`. A file keeps its quotes in every shell, while Windows PowerShell 5.1 drops the quotes inside a JSON argument. The reply holds a list of entries, each with its sequence, level, logger, message and time. Driving the editor with commands is the subject of [play tests by command](../make/automated-playtests.md).

#### The writer: `BackgroundLogSink`

Writing a line to a terminal or a file can block for milliseconds: a terminal whose reader is busy, a pipe that is full, a file that a virus scanner is reading. A frame at 60 frames a second lasts 16.7 ms, so one slow write on the main thread is one slow frame. **Asynchronous logging** moves the writing to a thread of its own, so that the thread that logs never waits for the console or the file. In Strata, that thread belongs to `BackgroundLogSink`.

```mermaid caption="Where one log call goes. The ring is filled before the call returns. The queue passes the line to the writer, which writes in order. A warning adds a flush, and the call returns only when the writer has flushed." alt="A sequence diagram with four columns: the logging thread, the ring, the queue and the writer thread. The logging thread pushes the line into the ring at once, then queues it. The writer wakes, writes the line to the console and the file, and flushes. For a warning, the logging thread waits until the writer reports the flush, and then returns."
sequenceDiagram
	participant M as Logging thread
	participant R as Ring
	participant Q as Queue
	participant W as Writer thread
	M->>R: push the line at once
	M->>Q: queue the line
	Q->>W: wake the writer
	W->>W: write to the console and the file
	M->>Q: warning: ask for a flush
	W-->>M: written and flushed, the call returns
```

The sink makes four promises, and each has a reason.

- **Order.** The writer writes lines in the order they were logged, so a file reads like the program ran.
- **Warnings and errors are on disk when the call returns.** Each logger flushes on a warning, and a flush waits for the writer. A process that dies on the next line has still written every warning before it.
- **The queue is bounded.** At most 65,536 messages wait. A thread that logs more waits for room, so a burst that no writer can match does not eat all the memory.
- **Stopping loses nothing that was logged before.** `Stop` writes the queue and ends the writer. The process calls it at exit, and `Log::Shutdown` calls it too.

A promise the sink cannot keep is the cost. A process that ends without running its exit handlers, because of a crash or a forced end, loses the information and trace lines that are still queued. Warnings and errors are already written. Say a frame logs 40 `Info` lines and the process then crashes: up to 40 lines can be missing from the file. If the 41st line was a warning, all 41 were on disk before its call returned.

`FlushFor` exists for one case: the console's control handler on Windows, which runs when a console is closed or interrupted a second time. It writes the queue within a time limit, 250 ms, before the system ends the process. It takes none of the locks that a log call holds, so any thread may call it. On Linux and macOS a second **Ctrl+C** ends the process at once and loses the queued lines.

:::why[Why the log has a thread of its own]
The frame is the engine's unit of time, and a log call in it must cost microseconds. The first versions of Strata wrote the console and the file on the thread that logged. Writing to a console, a pipe or a file can take milliseconds, and that holds up the frame. The writer thread costs one more thread and the loss of queued information lines in a crash, and Strata accepts both.
:::

#### Where the log is

Every program starts its log file empty. The file sink opens the file and empties it, so the text of the earlier run is gone at each start. Read or copy the log of a run that crashed before you start the program again. The places are these.

| Program | File | Console |
| --- | --- | --- |
| The editor | `StrataEditor.log` in the folder `Logs` of the :term[user data folder]{id=user-data-folder} `Strata`; every editor of the user writes the same file | On Windows only in a :term[Console run]{id=console-run}; on Linux and macOS the terminal that started it |
| An exported game, and `StrataRuntime` | `Game.log` in the folder `Logs` of the game's own user data folder | As for the editor |
| The test program | None | Warnings and errors, always |
| The command-line client | None | Warnings and errors on the error stream, and every level when you ask for detail |

The user data folder is `%LOCALAPPDATA%` on Windows, `~/.local/share` on Linux (or `$XDG_DATA_HOME`) and `~/Library/Application Support` on macOS, followed by the program's folder name. A Console run is a run whose output is the point, such as `--help`, a headless run or a scripted one: it prints into the terminal that started it. On Windows a run with a window of its own leaves the terminal alone, so its log file is the only record. Each file line reads `[date time] [level] logger: message`, with the level in words such as `warning`, and the console line is the same without the date.

### What a crash leaves

What a crash leaves depends on where it happens.

In a test, the program names the test case. On Windows, doctest, the test library, prints `test case CRASHED` with a description of the fault. On Linux and macOS the test program installs a reporter of its own, in `StrataTests/src/TestCrashReporter.cpp`. A listener remembers the running test case, and a handler for the fatal signals prints `Fatal signal 6 in test case: Core.Log / <name>` before the process ends. The number is the signal, and 6 is the signal of `std::abort`, which a failed assert ends with.

The test library's own signal handlers are off, because the crash guard of the scripting system owns the signals. A crash can still bypass the reporter, so set the :term[environment variable]{id=environment-variable} `STRATA_TEST_TRACE` to `1`. The program then prints `[test case] <suite> / <name>` to the error stream as each test case starts. The last line before the process dies names the culprit, and the continuous integration sets the variable for every run.

In a script, the crash is contained. A guarded call catches the fault, the engine marks the module as failed, and the log gets an error with the fault's description and, when the debug information is there, a file and a line. That subject is [crash containment](../scripting/crash-containment.md), and the step from an address to a line is [symbolization](../scripting/symbolization.md).

In engine code, nothing of Strata's own remains. Strata has no crash handler and writes no dump: a search of the engine's source finds no call that installs a handler for crashes, such as `SetUnhandledExceptionFilter`, a terminate handler or `MiniDumpWriteDump`. Outside a guarded call, a signal goes where it would have gone without the guard. What is left is the log up to its last flushed line (every warning and error, not the queued information lines) and the report of the operating system.

:::caution[What Strata does not do: no crash reports of its own]
A crash in engine code ends the process with no report and no dump from Strata. Run the program under a debugger, which stops at the fault with the whole stack, or enable the dumps of your system. Windows can store a dump for a crashed program through its error reporting; Linux writes a core file when the limit on its size allows one; macOS keeps a crash report for each crash.
:::

### Debugging one test alone

The test program holds hundreds of suites, and you run one case at a time when you debug. The doctest filters select by name, and `*` matches any text.

- `--test-case=<filter>` selects test cases by name.
- `--test-suite=<filter>` selects suites.
- `--list-test-cases` prints the names that match, and runs nothing.

Run the program under the debugger of your system with the filter as its argument, as the tabs above show. A failed `CHECK` also stops in the debugger when one is attached, and the option `--no-breaks` disables that.

For a crash that no debugger is at hand to catch, such as one that only the continuous integration meets, write temporary checkpoints. A checkpoint is a line like `std::fprintf(stderr, "checkpoint 1\n");` followed by `std::fflush(stderr);`. Put them between the statements you suspect, and run the one test case. The last checkpoint printed is the last one reached. Keep a copy of the file first, and remove the checkpoints afterwards, because they are not part of the change.

### Memory as a clue

A leak or a runaway cache shows as memory that grows. `Platform::GetProcessMemory` reports the memory of the current process as the system accounts it: `PrivateBytes`, the memory only this process uses, and `WorkingSet`, what sits in physical memory, each with its peak since the process started. It returns nothing where a system does not report it. On Linux the kernel keeps no peak of private memory, so the peak is the largest value any call has seen, and a spike between two calls is missed.

The engine's own test shows the scale. It allocates 256 MiB of fresh pages and writes one :term[byte]{id=byte} to each page of 4,096 bytes. Then it demands that the private memory grew by at least half of that, 128 MiB, and that the peaks kept the growth. Untouched pages cost no physical memory, which is why the test writes.

You read the same numbers from a running editor: the command `editor.status` with the section `memory` returns `privateMB`, `workingSetMB` and their peaks. The `--perf-log` file of `StrataRuntime` has the columns `PrivateMB` and `PeakPrivateMB` for every frame.

## A worked example: a test that asserts on purpose

The example breaks a test on purpose, finds the cause with the debugger, and fixes it. You will add one test case at the end of `StrataTests/src/Core/BackgroundLogSinkTests.cpp`, and add the line `#include "Strata/Core/Assert.h"` among its includes. Remove both when you finish, or restore the file with `git restore`.

:::::example[The mean of the last three values]
The function `MeanOfWindow` returns the mean of `count` values that start at index `first`. The assert says that the window must lie inside the values. The test wants the last three of six values, which are 16, 23 and 42, with a mean of 81 / 3 = 27. It has one deliberate mistake.

```cpp pseudocode
TEST_SUITE("Core.Log")
{
	// The mean of count values that start at index first.
	static float MeanOfWindow(const std::vector<int>& values, size_t first, size_t count)
	{
		ST_CORE_ASSERT(first + count <= values.size(), "window {} + {} passes the {} values", first, count, values.size());
		int sum = 0;
		for (size_t index = first; index < first + count; index++)
			sum += values[index];
		return static_cast<float>(sum) / static_cast<float>(count);
	}

	TEST_CASE("The mean of the last three values")
	{
		const std::vector<int> values = { 4, 8, 15, 16, 23, 42 };
		const size_t first = values.size() - 3 + 1;
		CHECK(MeanOfWindow(values, first, 3) == 27.0f);
	}
}
```

1. **Line 6:** the assert states the rule and its message names the three numbers, so the log line says what they were.
2. **Line 16:** the mistake. The window starts at index 4, and the last three values start at index 3.

The file already exists, so no new configure step is needed. Build the `Debug` test program, then start it under the debugger with `--test-case="The mean of the last three values"`. Each system shows the same stop in its own way.

::::tabs{sync=os}
:::tab[Windows]
Visual Studio stops with a message that the program triggered a breakpoint, at the `ST_CORE_ASSERT` line. Open the window "Call Stack" and double-click the second row, the test case. The window "Locals" shows `first` as 4 and the vector with 6 elements. The console of the test program shows the log line: it starts with `Assertion` and the condition, and ends with the message `window 4 + 3 passes the 6 values`.
:::
:::tab[Linux]
`gdb` stops with a signal at the assert's line. The commands below print the stack, select the frame of the test case, and print the two values.

```sh
bt
frame 1
print first
print values.size()
```

The values are 4 and 6. Quit with `quit`, because the program cannot run on from the trap.
:::
:::tab[macOS]
`lldb` stops with a breakpoint exception at the assert's line. The commands below do the same as the commands on Linux.

```sh
bt
frame select 1
frame variable first
```

:::
::::

The log line that the failed assert wrote has the form `Assertion '<condition>' failed at <file>:<line>: <message>`. Here the condition is `first + count <= values.size()` and the message is `window 4 + 3 passes the 6 values`. The numbers tell the story: 4 + 3 is 7, and there are 6 values. The stack tells where it began: frame 1, the test case, computed `first` as `values.size() - 3 + 1`. The fix is to remove the `+ 1`, which gives `first` = 3 and a window of 16, 23 and 42, and the test then passes with a mean of 27.
:::::

Without the debugger, the same test ends differently. On Linux and macOS the program logs the critical line, the default handler answers `Abort`, and the crash reporter prints `Fatal signal 6 in test case: Core.Log / The mean of the last three values`. You get the same facts, one at a time, and no variables.

## A toy version

The toy is the log's writer in 80 lines. The logging thread queues a line and continues; the writer thread prints the lines in order; a warning waits until its own line is printed; the queue holds at most four lines. Read the member `m_Written` as "lines the writer has printed", and `m_Queued` as "lines ever queued". The program queues two information lines and a warning, then two information lines more, and its output is the same on every run.

```cpp sketch="core-debugging-toy.cpp"
// A toy asynchronous log: lines are queued, a writer thread prints them in order, and a warning waits for its own line.
#include <condition_variable>
#include <cstdio>
#include <deque>
#include <mutex>
#include <string>
#include <thread>

class ToySink
{
public:
	ToySink()
		: m_Thread([this]() { Run(); })
	{
	}
	~ToySink() { Stop(); }

	void Log(const std::string& line, bool isWarning)
	{
		std::unique_lock<std::mutex> lock(m_Mutex);
		m_Progress.wait(lock, [this]() { return m_Queue.size() < c_MaxQueued; }); // a burst waits for room
		m_Queue.push_back(line);
		const size_t target = ++m_Queued;
		m_Wake.notify_one();
		if (isWarning)
			m_Progress.wait(lock, [&]() { return m_Written >= target; }); // returns once the line is out
	}

	void Stop()
	{
		{
			std::scoped_lock<std::mutex> lock(m_Mutex);
			m_Stopping = true;
		}
		m_Wake.notify_one();
		if (m_Thread.joinable())
			m_Thread.join();
	}
private:
	void Run()
	{
		std::unique_lock<std::mutex> lock(m_Mutex);
		while (true)
		{
			m_Wake.wait(lock, [this]() { return !m_Queue.empty() || m_Stopping; });
			if (m_Queue.empty())
				return; // stopping, and everything is written
			const std::string line = m_Queue.front();
			m_Queue.pop_front();
			m_Progress.notify_all(); // there is room again
			lock.unlock();
			std::printf("writer: %s\n", line.c_str()); // the slow part runs outside the lock
			lock.lock();
			m_Written++;
			m_Progress.notify_all();
		}
	}
	static constexpr size_t c_MaxQueued = 4;
	std::mutex m_Mutex;
	std::condition_variable m_Wake;     // for the writer: a line or Stop
	std::condition_variable m_Progress; // for the loggers: room, or a line written
	std::deque<std::string> m_Queue;
	size_t m_Queued = 0;
	size_t m_Written = 0;
	bool m_Stopping = false;
	std::thread m_Thread; // last, so that everything it uses exists before it starts
};

int main()
{
	ToySink sink;
	sink.Log("info: loading the scene", false);
	sink.Log("info: 3 meshes", false);
	sink.Log("warning: a texture is missing", true);
	std::printf("main: the warning returned, so three lines are out\n");
	sink.Log("info: using the fallback", false);
	sink.Log("info: scene ready", false);
	sink.Stop();
	std::printf("main: stopped, nothing is left in the queue\n");
}
```

```text output-of="core-debugging-toy.cpp"
writer: info: loading the scene
writer: info: 3 meshes
writer: warning: a texture is missing
main: the warning returned, so three lines are out
writer: info: using the fallback
writer: info: scene ready
main: stopped, nothing is left in the queue
```

1. **Line 21:** a burst waits here for room, which is the bound of the queue.
2. **Line 23:** the target is the count of lines queued so far, this one included.
3. **Line 26:** only a warning waits, until the writer has printed that many lines.
4. **Line 47:** the writer ends only when `Stop` was called and the queue is empty.
5. **Line 52:** the slow print runs outside the lock, so other threads can queue meanwhile.

The warning returned only after the writer printed the three lines up to it. That is the second promise of the sink: when the call for a warning returns, the line is out. The `Stop` call then printed the last two lines before it returned. The toy omits much of the real sink: the inner sinks, a flush that no line asks for, the time limit of `FlushFor`, and what happens when a thread logs while `Stop` runs.

## The real code

The code follows the data. The loggers and sinks are objects of `spdlog`, the logging library under Strata. `Log::Init` builds the sinks, then `BackgroundLogSink::log` and `flush` take the lines. First the sinks: the ring is made at the capacity of the specification, a sink fills it, and the console and the file are collected apart for the writer.

```cpp src="Strata/src/Strata/Core/Log.cpp#L200-L227"
data.Buffer = CreateScope<LogBuffer>(specification.BufferCapacity);
data.LogFile.clear();

// The shared buffer is filled at once (the editor's console and automation read it); the console and the log file are
// written by the background writer, so that a log call never waits for them (BackgroundLogSink).
std::vector<spdlog::sink_ptr> sinks;
sinks.push_back(std::make_shared<LogBufferSink>(*data.Buffer, std::chrono::system_clock::now()));
std::vector<spdlog::sink_ptr> writtenSinks;

if (specification.ConsoleOutput)
{
	auto consoleSink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
	consoleSink->set_pattern("%^[%T] [%l] %n: %v%$");
	writtenSinks.push_back(consoleSink);
}

if (!specification.LogFile.empty())
{
	try
	{
		std::error_code error;
		if (specification.LogFile.has_parent_path())
			std::filesystem::create_directories(specification.LogFile.parent_path(), error);

		auto fileSink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(specification.LogFile.string(), true);
		fileSink->set_pattern("[%Y-%m-%d %T.%e] [%l] %n: %v");
		writtenSinks.push_back(fileSink);
		data.LogFile = specification.LogFile;
```

1. **Line 200:** the ring is made with the capacity of the specification, 4,096 by default.
2. **Lines 205–207:** the sink of the ring comes first and stands alone; the console and the file are collected apart, for the writer.
3. **Line 212:** the console pattern shows the time, the level, the logger and the message.
4. **Line 224:** the second argument, `true`, opens the file empty.
5. **Line 225:** the file pattern adds the date to each line.

Then the writer and the loggers. A line logged by any of the three loggers goes through the same sinks, so the file keeps one order for all of them.

```cpp src="Strata/src/Strata/Core/Log.cpp#L241-L267"
else if (!writtenSinks.empty())
{
	Ref<BackgroundLogSink> writer = CreateRef<BackgroundLogSink>(std::move(writtenSinks));
	sinks.push_back(writer);
	{
		std::scoped_lock<std::mutex> writerLock(data.WriterMutex);
		data.Writer = std::move(writer);
	}
	if (!data.ExitHandlerRegistered)
		data.ExitHandlerRegistered = std::atexit(&StopWriterAtExit) == 0;
}

const spdlog::level::level_enum level = ToSpdlogLevel(specification.Level);
// Warnings and errors flush the sinks, which waits for the writer: they are on the console and in the file when the
// call that logged them returns (and survive a crash right after).
auto createLogger = [&](const char* name)
{
	auto logger = std::make_shared<spdlog::logger>(name, sinks.begin(), sinks.end());
	logger->set_level(level);
	logger->flush_on(spdlog::level::warn);
	return logger;
};

data.CoreLogger = createLogger("Strata");
data.ClientLogger = createLogger("App");
data.ScriptLogger = createLogger("Script");
data.Initialized = true;
```

1. **Lines 243–244:** the writer owns the console and the file, and joins the ring as one more sink.
2. **Line 250:** the exit handler writes what is still queued when the process ends in order.
3. **Line 258:** every logger gets the same sinks, so one order holds for all three.
4. **Line 260:** a warning or worse flushes the sinks, which waits for the writer.
5. **Lines 264–266:** the three loggers, `Strata`, `App` and `Script`.

At last the sink, in two calls: `log` and `flush`.

```cpp src="Strata/src/Strata/Core/BackgroundLogSink.cpp#L36-L78"
void BackgroundLogSink::log(const spdlog::details::log_msg& message)
{
	{
		std::unique_lock<std::mutex> lock(m_Mutex);
		if (m_Running && std::this_thread::get_id() != m_WriterId)
		{
			m_ProgressMade.wait(lock, [this]() { return m_Queue.size() < c_MaxQueuedMessages || m_Stopping || !m_Running; });
			// Once Stop was called nothing is queued: what it waits for stays what was logged before it, however fast other
			// threads log. This message is written by this thread once the writer has written those before it.
			if (m_Stopping)
				m_ProgressMade.wait(lock, [this]() { return !m_Running; });
			if (m_Running)
			{
				m_Queue.emplace_back(message);
				m_Queued++;
				lock.unlock();
				m_WriterWake.notify_one();
				return;
			}
		}
	}
	// The writer has stopped (or this is the writer itself, should an inner sink log): written right away, after what the
	// writer had left (it holds the write lock while it writes that).
	std::scoped_lock<std::recursive_mutex> writeLock(m_WriteMutex);
	WriteToSinks(message);
}

void BackgroundLogSink::flush()
{
	std::unique_lock<std::mutex> lock(m_Mutex);
	if (!m_Running || std::this_thread::get_id() == m_WriterId)
	{
		lock.unlock();
		std::scoped_lock<std::recursive_mutex> writeLock(m_WriteMutex);
		FlushSinks();
		return;
	}
	// Everything logged before this call, written and flushed; what other threads log meanwhile is not waited for.
	const uint64_t target = m_Queued;
	m_FlushRequested = std::max(m_FlushRequested, target);
	m_WriterWake.notify_one();
	m_ProgressMade.wait(lock, [this, target]() { return m_Flushed >= target || m_Finished; });
}
```

1. **Line 42:** a thread that finds 65,536 messages waiting waits for room.
2. **Lines 49–50:** the line is queued and counted; the count orders every flush.
3. **Lines 59–60:** after `Stop`, the thread that logs writes its own line, after those of the writer.
4. **Line 74:** the target of a flush is the count of lines logged before the call.
5. **Line 77:** the call waits until the writer has flushed that many lines, and no more.

The real sink differs from the toy in four ways. It queues copies of the message that `spdlog` builds, not strings. Its flush has a target, the count of messages logged before the call, so a thread that keeps logging cannot delay a warning; the history below tells why. After `Stop`, nothing is queued: the threads that log write their own lines, once the writer has written those before them. The writer holds a second lock, `m_WriteMutex`, for the lines it writes when it stops.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Write each line on the logging thread and flush it | The default sinks of `spdlog`, and most small programs | No lines lost in a crash, and no extra thread | A slow console or file stalls the frame |
| The asynchronous logger of `spdlog` | Programs that use `spdlog` | Code that others write and test | The exact rules of Strata's sink, which the engine's tests check: the order after `Stop`, the bound and the flush with a time limit |
| A crash handler that writes a dump | Chromium, with its crash reporter, and Unreal Engine's crash reporter | A report from a player's computer | Code for each system, storage of dumps, and a handler that runs inside a broken process |
| End the process at every failed assert | The C library's `assert` | One simple rule | No stop in the debugger at the line, and no tests that count asserts |

## How it is tested

The log's tests are in `StrataTests/src/Core/BackgroundLogSinkTests.cpp`, in the suite `Core.Log`, and the ring's test is in `StrataTests/src/Core/CoreTests.cpp`. They use a sink that blocks on demand, so no test depends on how fast a disk is.

- Log calls return while the console or file is blocked, and the messages follow in order.
- Warnings and errors are written when the call that logs them returns.
- Nothing is queued after `Stop`; a full queue makes the thread that logs wait; a bounded flush waits at most its time.
- `LogBuffer keeps the most recent entries with increasing sequence numbers` checks the ring.
- The suite `Core.Platform` checks `GetProcessMemory`, including the 256 MiB case.

Run one suite with the filter, after a `Debug` build, from the engine's folder:

```powershell
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Log
```

The command prints how many test cases and checks passed. The physics tests replace the assert handler with one that answers `Continue`, to check that a bad shape asserts and is refused. The suites hold no test of the default handler or of the crash reporter: every failed assert or crash of any test shows them at work.

## Changing it safely

The points where other code joins the log are few: a new sink for the loggers, a new reader of `LogBuffer`, and a handler for `SetAssertHandler`. Keep these rules when you change the machinery.

- Keep the order of the writer, and keep the flush on warnings: other code relies on a warning being on disk.
- Keep the queue bounded, and let no log call take a lock that `FlushFor` needs. Its callers run where almost nothing else is safe.
- Read the log only through `LogBuffer`, by sequence number, and never keep a pointer into it: the ring replaces its oldest entries.
- Add no side effect to an assert's condition, because `Dist` removes it.
- Log with `ST_CORE_*` in the engine and `ST_*` in programs, as [conventions](conventions.md) says.

Then run `Core.Log`, `Core.Platform` and `Core`, in `Debug` and in `Release`.

## What went wrong before

A warning once waited as long as another thread kept logging. The writer finished a flush only when it found the queue empty. A thread that logged about as fast as the console wrote, such as a script that logs every frame in a Console run, kept the queue full. Every warning on every other thread then waited, together with any lock that thread held. A measurement with a writer at 200 microseconds a line and a producer 1.33 times as fast held one warning for 2.4 seconds.

Since commit `6dbf7bf5`, a flush ends when the lines logged before it are written. The case `A warning and Stop wait for what was logged before them, not for what another thread keeps logging` keeps it so: a thread logs a line every 75 microseconds into a sink that takes 100, and the warning must return while that thread still logs.

## Summary

- The engine runs under any debugger from a source build: Visual Studio with the solution of the preset `windows`, `gdb` on Linux and `lldb` on macOS, with `StrataTests` and a doctest filter as the target. Use `Debug` for stepping and `Release` when a bug shows only optimized.
- A failed assert logs and flushes a critical line, then asks the handler: `Break` with a debugger, `Abort` without one, `Continue` only when a test replaces the handler.
- The ring `LogBuffer` keeps the newest entries with sequence numbers for the Console panel and `log.read`. The writer thread of `BackgroundLogSink` writes the console and the file in order. A warning is on disk when its call returns; queued information lines can be lost in a crash.
- The log file is emptied at every start; every editor of a user writes the same `StrataEditor.log`, and a game writes `Game.log`.
- A crashed test is named by doctest on Windows and by the reporter on Linux and macOS, and `STRATA_TEST_TRACE=1` names it where those fail. A crash in engine code leaves the log and the report of the system, because Strata writes no dump.

## Check yourself

1. A bug appears only in the `Release` build. Which build do you debug, which tool of the build still works there, and what can the debugger not show?

   :::answer{tests="debug-engine"}
   You debug the `Release` build, with the same preset, because the bug may depend on the optimization. The asserts still work: they are compiled out only in `Dist`. On Windows the debugger may show "optimized out" for variables and jump between lines, so place breakpoints on calls, or log the values. On Linux and macOS `Release` has no debug information, so you log the values.
   :::

2. On Linux, no debugger is attached, and an `ST_CORE_ASSERT` fails in the test case `Core.Log / The mean of the last three values`. What appears, in which order, and what ends the process?

   :::answer{tests="assert-action"}
   First the critical line `Assertion '<condition>' failed at <file>:<line>: <message>`, written and flushed. The default handler answers `Abort`, and `Log::Shutdown` and `std::abort` end the process. The signal is 6, so the crash reporter prints `Fatal signal 6 in test case: Core.Log / The mean of the last three values`. With a debugger attached, the answer would be `Break` and the program would stop at the assert's line instead.
   :::

3. A frame logs 30 `Info` lines and then dies with an access violation. A second program logs 30 `Info` lines and a warning, and then dies. How many lines can each file lack?

   :::answer{tests="log-writer"}
   The first file can lack up to all 30 lines: the writer may not have written the queued ones, and an access violation runs no :term[exit code]{id=exit-code}. The second file lacks none: the warning's flush waits until every earlier line is written and flushed before the call returns. The warning is the barrier.
   :::

4. The ring holds 4,096 entries and the engine has logged 10,000 lines. A reader last saw number 5,000. Which numbers does it receive next, and how many did it miss?

   :::answer{tests="log-writer"}
   The ring holds 5,905 to 10,000, because 10,000 − 4,096 + 1 = 5,905. The reader receives these, and it missed 5,001 to 5,904, which are 904 entries. It sees the gap because the first number it gets is not 5,001.
   :::

5. You start the editor, it crashes at startup, and you start it again before reading the log. Where is the first run's log, and what changes if a second editor is open?

   :::answer{tests="log-file"}
   The first log is gone: the file `StrataEditor.log` in the `Logs` folder of the user data folder is opened empty at every start. With a second editor open the file is shared, because every editor of a user writes it, and the second start empties it. Copy the file before you start the program again.
   :::

6. The test program dies on a continuous integration machine with no sign of the test case. What do you set, and how do you find the case?

   :::answer{tests="crash-left"}
   Set `STRATA_TEST_TRACE` to `1`. The program then prints `[test case] <suite> / <name>` to the error stream as each case starts, so the last such line before the process dies names the culprit. Run that case alone under a debugger.
   :::

## Exercises

1. **Basic.** The engine logs 12,000 lines into a ring of 4,096 entries. What are the numbers of the oldest and the newest entry, and what does a console that last read number 7,000 miss?

   :::answer[Worked solution]{tests="log-writer"}
   The newest number is 12,000. The oldest is 12,000 − 4,096 + 1 = 7,905. A reader at 7,000 wants 7,001 and gets 7,905, so it missed 7,001 to 7,904, which is 904 entries.
   :::

2. **Medium.** Write a program of your own with a ring of capacity 3. Push five messages, ask for the entries after number 1, and print them and the count of lost entries.

   :::answer[Worked solution]{tests="log-writer" solution="sketches/core-debugging-ring.cpp"}
   The ring pops the oldest entry when it is full, and `GetEntries` keeps the entries above the number. The first entry returned is 3, so entry 2 is lost.

   ```cpp sketch="core-debugging-ring.cpp"
   // A ring of log entries with sequence numbers, and a reader that asks for what came after the last number it saw.
   #include <cstdint>
   #include <cstdio>
   #include <deque>
   #include <string>
   #include <vector>

   struct Entry
   {
   	uint64_t Sequence = 0;
   	std::string Message;
   };

   class Ring
   {
   public:
   	explicit Ring(size_t capacity)
   		: m_Capacity(capacity)
   	{
   	}

   	void Push(const std::string& message)
   	{
   		if (m_Entries.size() >= m_Capacity)
   			m_Entries.pop_front(); // the oldest entry is overwritten
   		m_Entries.push_back({ m_NextSequence++, message });
   	}

   	std::vector<Entry> GetEntries(uint64_t afterSequence) const
   	{
   		std::vector<Entry> result;
   		for (const Entry& entry : m_Entries)
   		{
   			if (entry.Sequence > afterSequence)
   				result.push_back(entry);
   		}
   		return result;
   	}
   private:
   	std::deque<Entry> m_Entries;
   	size_t m_Capacity;
   	uint64_t m_NextSequence = 1;
   };

   int main()
   {
   	Ring ring(3);
   	for (const char* message : { "one", "two", "three", "four", "five" })
   		ring.Push(message);

   	const uint64_t lastSeen = 1; // the reader has shown entry 1 and nothing after it
   	const std::vector<Entry> entries = ring.GetEntries(lastSeen);
   	for (const Entry& entry : entries)
   		std::printf("%llu %s\n", static_cast<unsigned long long>(entry.Sequence), entry.Message.c_str());
   	const uint64_t missed = entries.front().Sequence - lastSeen - 1;
   	std::printf("entries lost between two reads: %llu\n", static_cast<unsigned long long>(missed));
   	return 0;
   }
   ```

   ```text output-of="core-debugging-ring.cpp"
   3 three
   4 four
   5 five
   entries lost between two reads: 1
   ```

   1. **Line 25:** the oldest entry is dropped before the new one goes in.
   2. **Line 34:** the filter on the sequence number is the whole of the reader's interface.
   3. **Line 55:** the count of lost entries is the gap between the number the reader had and the first it receives.
   :::

3. **Hard.** Trace it yourself. Add a temporary test case that calls `Log::Init` with a `LogSpecification` whose `LogFile` is a file in `Tests::CreateTemporaryDirectory()`, then `ST_CORE_WARN("trace me {}", 42);`. Run it alone under the debugger, with breakpoints, and name the functions the warning visits from the macro to the file.

   :::answer[Worked solution]{tests="log-writer log-file"}
   The macro `ST_CORE_WARN` in `Strata/src/Strata/Core/Log.h` calls the core logger of `spdlog`. The logger passes the line to its sinks in order: first `LogBufferSink::sink_it_` in `Strata/src/Strata/Core/Log.cpp`, which calls `LogBuffer::Push`, so the ring has the line at once. Then `BackgroundLogSink::log` in `Strata/src/Strata/Core/BackgroundLogSink.cpp` queues it and wakes the writer. On the thread `Strata Log Writer`, `BackgroundLogSink::Run` takes the batch and calls `WriteToSinks`, which reaches the file sink. The logger flushes on a warning, so `BackgroundLogSink::flush` sets the flush target and waits until `Run` has written and flushed up to it; only then does the call return.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Log.h`, `Log.cpp`: `Log::Init`, `LogBuffer`, `LogSpecification`, `Log::FlushFor`, `Log::GetLogFile`.
- `Strata/src/Strata/Core/BackgroundLogSink.h`, `BackgroundLogSink.cpp`: `BackgroundLogSink`, `c_MaxQueuedMessages`, `FlushFor`, `Stop`.
- `Strata/src/Strata/Core/Assert.h`, `Assert.cpp`, `Base.h`: the macros, `SetAssertHandler`, `AssertAction`, `ST_DEBUGBREAK`.
- `Strata/src/Strata/Core/Platform.h`: `Platform::IsDebuggerAttached`, `Platform::GetProcessMemory`, `ProcessMemoryInfo`.
- `StrataEditor/src/Panels/ConsolePanel.cpp` and the command `log.read` in `StrataEditor/src/Editor/EditorStateCommands.cpp`.
- `StrataTests/src/TestCrashReporter.cpp`, and the test case suites `Core.Log`, `Core.Platform` and `Core`.
- Commands and settings: `log.read`, `editor.status` with the section `memory`, `STRATA_TEST_TRACE`, `--test-case`, `--test-suite`.

## Further reading

- [Microsoft, the Visual Studio debugger](https://learn.microsoft.com/en-us/visualstudio/debugger/): breakpoints, the call stack and the locals window; beginner.
- [Microsoft, collecting user-mode dumps](https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps): how Windows stores a dump of a crashed program; intermediate.
- [spdlog](https://github.com/gabime/spdlog): the logging library under Strata's loggers, with its asynchronous mode; intermediate.
- [doctest's command line](https://github.com/doctest/doctest/blob/master/doc/markdown/commandline.md): the filters and options of the test program; beginner.
- The GDB manual, and the LLDB tutorial: the commands of the two debuggers; beginner.
