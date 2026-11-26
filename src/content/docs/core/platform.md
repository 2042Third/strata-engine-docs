---
id: core/platform
title: "Talking to the operating system"
description: "How Strata reaches Windows, Linux and macOS through one seam, and how a program gets its terminal, stops on Ctrl+C, sleeps and ranks its threads."
kind: internals
size: L
tracks: [E]
needs: [core/jobs]
time: 95
learn:
  - id: platform-seam
    text: explain how engine code reaches the operating system through one seam, and where system headers may appear
  - id: windows-programs
    text: explain how a Strata program on Windows gets its terminal, and why PowerShell does not wait for the editor
  - id: interrupt-path
    text: trace Ctrl+C from the system's handler to the exit code 130
  - id: scheduling
    text: explain why Strata lowers the priority of background threads, opts out of power throttling and sleeps on its own timer
  - id: add-function
    text: add a function to the platform seam for every operating system
since: 0.3.0
status: final
---

Strata runs on Windows, Linux and macOS, and the three systems answer the same questions in three ways. Where may a program keep its settings, how does it start another program, and how does it learn that a person pressed **Ctrl+C**? How does it sleep for 8 ms? This page teaches the one place in the engine where those answers live: the class `Platform`, its neighbour `Process`, and the folders under `Strata/src/Platform/` that implement them.

The page also teaches how a Windows program gets its terminal and how Strata turns a request to stop into an orderly end. Other pages teach files and paths ([Files](files.md)), the window backends ([Windows, events and layers](windows-events.md)), script modules ([Loading script modules](../scripting/loading.md)) and the debugger and memory functions ([Debugging](debugging.md)).

## The problem and how engines solve it

Take one small task: save a settings file where the person who runs the program will find it again. Windows keeps per-user program data under `%LOCALAPPDATA%`. Linux programs use `$XDG_DATA_HOME`, which falls back to `~/.local/share`. macOS uses `~/Library/Application Support`.

Engines solve this in three ways.

- **The preprocessor.** The :term[compiler]{id=compiler} defines a :term[macro]{id=macro} for the target system (`_WIN32` on Windows), and code between `#if` and `#endif` compiles only there. This needs no machinery, but system code spreads everywhere. A reader of a :term[renderer]{id=renderer} function must read three versions of it, and the versions you cannot run may break unseen until someone builds them.
- **One interface with one implementation per system.** A header declares the functions, the project holds one :term[source file]{id=source-file} per system that defines them, and the build compiles only the file of the target. Callers hold no `#if`, and a call costs a plain call. The price is that the choice is fixed at link time: one program holds the code of one system.
- **A virtual backend.** An :term[abstract class]{id=abstract-class} declares the functions, several classes implement it, and the program picks one while it runs. That fits a choice that stays open until the program runs, such as a game that draws through two graphics interfaces. Nobody makes that choice for the :term[operating system]{id=operating-system}, so a virtual call would pay for nothing.

Window libraries add a fourth layer. GLFW gives one window, keyboard and mouse interface over the window systems of the three operating systems, and `SDL` does the same. Strata uses GLFW behind its own interface, `Window`. Two files define `Window::Create`, the GLFW one and a `NoWindow` one for builds without windows, and the build compiles one of them as it picks the system's files.

For the operating system Strata takes the second way. A **seam** is a place where two parts of a program meet and one side can change without the other noticing. Strata's seam is `Platform`, a class of static functions declared once in `Strata/src/Strata/Core/Platform.h`. One file defines them for Windows. One file serves Linux and macOS together, which share the system calls that `POSIX` names, so a few of its functions hold an `#if` of their own.

The cost is that a mistake in the file you did not build shows only when someone builds that system, so the continuous integration builds all three.

One more problem belongs here: where system headers may appear. The Windows header `<Windows.h>` defines many macros with short plain names, among them `near`, `far`, `small`, `interface`, `CreateWindow`, `GetObject` and `LoadImage`. A header that includes it hands those names to every file that includes the header, and a variable called `near` stops compiling. X11, a window system of Linux, defines `None` as a macro. System, window and graphics headers therefore appear only in their own folders under `Platform/`.

## The map

Engine code includes only the headers of the seam, `Platform.h` and `Process.h`. The build adds the folder of the target system and one window backend, and leaves the others out. `DynamicLibrary` is the seam for :term[shared libraries]{id=shared-library} in the same way, and [Loading script modules](../scripting/loading.md) teaches it.

```mermaid caption="Engine code calls only the declarations. The build compiles one folder of system code and one window backend, and each of them calls the system below it." alt="A diagram. Engine code points to a box of declarations for the platform class and the process class, and to a box for the window interface. The declarations point with dotted lines to a Windows folder and a folder for Linux and macOS, of which the build compiles one. The Windows folder points to the Windows system calls, and the other folder to those of Linux and macOS. The window box points with dotted lines to a window library folder and a folder for builds without windows."
flowchart TB
	code["Engine code: Application, JobSystem, the editor"]
	header["Core/Platform.h and Core/Process.h: declarations"]
	windowHeader["Core/Window.h: the window interface"]
	win["Platform/Windows: WindowsPlatform.cpp, WindowsProcess.cpp, WindowsUtils.h"]
	posix["Platform/Posix: PosixPlatform.cpp, PosixProcess.cpp"]
	glfw["Platform/GLFW: GLFWWindow.cpp"]
	none["Platform/NoWindow: NoWindow.cpp"]
	win32["Win32 and the C runtime"]
	unix["System calls of Linux and macOS"]
	code --> header
	code --> windowHeader
	header -. "one of the two" .-> win
	header -. "one of the two" .-> posix
	windowHeader -. "one of the two" .-> glfw
	windowHeader -. "one of the two" .-> none
	win --> win32
	posix --> unix
```

:term[CMake]{id=cmake} does the choosing (`CMake/StrataLayers.cmake`). When it collects the sources of a layer, it removes the `Platform/` folders of the other systems: on Windows the `POSIX` folder goes, on Linux and macOS the Windows folder goes. The option `STRATA_WITH_GLFW` decides between the GLFW folder and the `NoWindow` folder in the same way. The layer table puts both system folders in the same layer as `Strata/src/Strata/Core/`, so the implementations may use Core's headers ([Layers and registries](layers-registries.md)).

## The contract

This section states what callers may assume and must do, and why.

### Platform detection

Detection is the one place where the :term[preprocessor]{id=preprocessor} decides. `PlatformDetection.h` turns the compiler's own macros into exactly one of `ST_PLATFORM_WINDOWS`, `ST_PLATFORM_LINUX` and `ST_PLATFORM_MACOS`, and adds `ST_PLATFORM_POSIX` for the last two. Read the file as a list of questions asked in order.

```cpp src="Strata/src/Strata/Core/PlatformDetection.h#L5-L26"
#if defined(_WIN32)
#if defined(_WIN64)
	#define ST_PLATFORM_WINDOWS
#else
	#error "Strata requires a 64-bit Windows target"
#endif
#elif defined(__APPLE__) && defined(__MACH__)
#include <TargetConditionals.h>
#if TARGET_OS_OSX
	#define ST_PLATFORM_MACOS
#else
	#error "Unsupported Apple platform: Strata supports macOS only"
#endif
#elif defined(__linux__)
#define ST_PLATFORM_LINUX
#else
#error "Unsupported platform: Strata supports Windows, Linux and macOS"
#endif

#if defined(ST_PLATFORM_LINUX) || defined(ST_PLATFORM_MACOS)
#define ST_PLATFORM_POSIX
#endif
```

1. **Lines 5–10:** Windows counts only with 64 bits; 32-bit Windows meets an `#error`.
2. **Lines 11–17:** an Apple system is macOS only when `TARGET_OS_OSX` says so; any other Apple system stops the build.
3. **Lines 18–22:** Linux is accepted, and every other target stops the build with a message.
4. **Lines 24–26:** `ST_PLATFORM_POSIX` is added for Linux and macOS.

Everything else stops the build. A 32-bit Windows build, any Apple system that is not macOS and every other target meet an `#error` with a message. Strata therefore has no mobile, game console or web target: a compiler for one of them fails at the first include. Callers test these macros only inside `Platform/` and in the few places that compile differently, such as the private members of `Process`.

### The `Platform` class

`Platform` holds every question that has a different answer on each system. All of its members are static. A function that can fail says so in its result (`bool` or `std::optional`), and none throws. The table lists the groups; the comments in `Platform.h` give the exact rules.

| Group | Functions | What differs by system |
| --- | --- | --- |
| Names and folders | `GetName`, `GetExecutablePath`, `GetUserDataDirectory`, `FindUserDataDirectory`, `FindHomeDirectory` | The data folder is `%LOCALAPPDATA%`, `$XDG_DATA_HOME` or `~/Library/Application Support`. `FindUserDataDirectory` returns nothing where `GetUserDataDirectory` falls back to the temporary folder: use it for secrets. |
| Fallback fonts | `FindFallbackFontFiles` | Files of the system's Chinese, Japanese and Korean fonts, at most one per group of scripts. |
| Processes | `GetProcessID`, `IsProcessAlive`, `GetProcessStartTime`, `GetProcessUptime` | The start time is an opaque value that differs for a later process with the same id. |
| Memory and debugger | `GetProcessMemory`, `GetPhysicalMemorySize`, `IsDebuggerAttached` | [Debugging](debugging.md) reads them again. |
| Secure random numbers | `GenerateSecureRandom` | Fills a buffer from the system's cryptographic generator: `BCryptGenRandom`, `getrandom` or `arc4random_buf`. |
| :term[Environment variables]{id=environment-variable} | `GetEnvVar`, `SetEnvVar` | Names and values are `UTF-8`. |
| Opening and finding | `OpenWithDefaultApplication`, `FindProgram` | A file, folder or address opens with `ShellExecuteW`, `open` or `xdg-open`. `FindProgram` searches `PATH` as a typed command would, and never the :term[current folder]{id=current-folder}. |
| Error dialogs | `ShowErrorDialog`, `ShouldShowErrorDialogs` | `MessageBoxW`, `osascript`, or `zenity` or `kdialog` where one is installed. |
| Streams and interrupts | `SetBinaryStandardStreams`, `ConnectStandardStreams`, `InstallInterruptHandler`, `IsInterruptRequested` | Later sections teach them. |
| Threads and speed | `SetCurrentThreadName`, `SetCurrentThreadPriority`, `SleepUntil`, `DisableExecutionSpeedThrottling` | Later sections teach them. |

### Process

`Process` is the seam for child processes, declared in `Strata/src/Strata/Core/Process.h` and defined by `WindowsProcess.cpp` and `PosixProcess.cpp`. A `ProcessSpecification` says what to start: the :term[executable]{id=executable} (a path, or a bare name that the system finds on `PATH`), the arguments, the working folder and four options.

- `Output` is a `ProcessOutputMode`: `Capture` merges :term[standard output]{id=standard-output} and :term[standard error]{id=standard-error} into one buffer, `CaptureSeparate` keeps them apart, `Inherit` lets the child write where this program writes, and `Discard` sends them to the null device.
- `PipeInput` gives the child a pipe for :term[standard input]{id=standard-input}, written with `WriteInput` and ended with `CloseInput`.
- `Detached` puts the child in its own process group (processes that share console signals), so that console signals sent to this program do not reach it.
- `TerminateTree` makes the child and every process it starts one unit that `Terminate` ends together.

`Wait` takes an optional timeout and returns the :term[exit code]{id=exit-code}, or nothing when the time ran out. `Process::Run` starts a process, waits for it, collects its output and, on a timeout, ends it. The unit of `TerminateTree` is a job object on Windows, which also ends its processes when the last handle to it closes, and the child's own process group on `POSIX`, ended with one `SIGKILL`. A process that breaks away from the job or leaves the group escapes: that is the cost.

Four users stand out. The editor's script builds capture the output of CMake and the compilers and use `TerminateTree`, so that a cancelled build leaves no compiler running ([Script builds](../editor/script-builds.md)). The external editor and StrataCLI's launcher of the editor discard the output and detach the child. The tests start the engine's programs as helper processes.

### The rule for headers

:::rule[System headers stay in their folders]
Platform, window and graphics headers appear only in their `Platform/` folders. `<Windows.h>` never appears in a header, and X11 headers never appear in engine code. No identifier collides with a macro that Windows defines, and a plain `enum` never uses `None`. A macro ignores scopes, so one included header changes every file after it. The rule is in the engine's `AGENTS.md`, and `Architecture.Layering` enforces its first part through `ExternalOwners`.
:::

`ExternalOwners` is a list in the layer table. Each entry names include prefixes (`GLFW/`, `vulkan/`, `Windows.h` with its relatives, `unistd.h` with `sys/`) and the folders allowed to use them.

The names show in the code. The enum `AudioAttenuationModel` has a value `NoAttenuation` where a reader expects `None`, and the flag enum `EventCategory` uses `EventCategoryNone`.

At Win32's boundary one more problem appears: the functions that end in `W` take wide strings (`UTF-16`), and Strata holds `UTF-8`. `WindowsUtils`, a header in `Platform/Windows/` that may include `<Windows.h>`, converts with `Utf8ToWide` and `WideToUtf8`. The same header holds `ScopedHandle`, which closes a kernel handle on every path out of a function.

### Programs on Windows

#### Two kinds of program

Every Windows executable carries a flag, set at link time, that names its subsystem. A **console subsystem** program is one that Windows gives a console: started from Explorer, it opens a console window, and a shell waits for it to end. The other kind belongs to the graphical user interface (GUI) subsystem. A **GUI subsystem** program gets no console, and a shell does not wait for it.

A person double-clicks the editor and expects a window, not a black box beside it. `StrataEditor` and `StrataRuntime`, and so every exported game, are therefore GUI programs: CMake sets `WIN32_EXECUTABLE` on them, and under the Microsoft compiler the :term[linker]{id=linker} option `/ENTRY:mainCRTStartup` keeps the ordinary `main` as the entry point. `StrataCLI` and the tests are console programs.

The cost is that a GUI program starts with no console of its own. Started from a terminal, it has nowhere to print unless something connects its streams. `Platform::ConnectStandardStreams` does that, as the first call in `main` (`Strata/src/Strata/Engine/EntryPoint.h`), before anything prints or the log opens its console.

The function takes a `ProgramRun`. A `Console` run is one whose output is the point: `--help`, `--version`, a usage error, and the headless or scripted runs of tools (`--headless`, `--no-gpu`, `--frames`, `--commands`, `--quit-after-commands`). An `Interactive` run is a person's window. Each program decides in its `GetProgramRun`.

#### What `ConnectStandardStreams` decides

A stream counts as passed when the parent gave the program something that is not a console: a pipe, a file or the null device. CTest, StrataCLI and continuous integration pass pipes and read the output and the exit code afterwards, so the program never replaces a passed stream. An `Interactive` run also leaves the terminal alone: a process attached to a console ends with it, so the terminal's **Ctrl+C** or its closing would kill the editor. The log would also mix with the shell's prompt. The decision for a Windows run:

| Streams the parent passed | Kind of run | Parent has a console | What the program does | Fatal-error dialog |
| --- | --- | --- | --- | --- |
| Output and error both | Either | Not asked | Keeps both as they are | Only an `Interactive` run whose error stream is the null device |
| Fewer than both | `Interactive` | Not asked | Leaves everything alone; prints only to its log | Yes, when nobody reads its error stream |
| Fewer than both | `Console` | Yes, a terminal | Attaches to the console and connects the streams not passed | Never |
| Fewer than both | `Console` | No, started from Explorer | Has nothing to attach to; prints only to its log | Never |

On Linux and macOS the function does almost nothing, because programs keep the streams they are given: it notes the run and whether anyone reads standard error. That note feeds `ShouldShowErrorDialogs`. A `Console` run never shows a dialog, so a tool or a server is never stopped by one.

#### Why PowerShell does not wait

A shell waits for a console program to end and records its exit code. PowerShell does not wait for a GUI program that it starts directly. The prompt returns at once, the output arrives in the middle of the next command, and `$LASTEXITCODE` keeps the code of the command before, often 0.

The cure: pipe the output (`StrataEditor --commands script.json --quit-after-commands | Out-Host`), or start the program with `Start-Process -Wait` when you need the exit code. The command prompt and the shells of Linux and macOS wait without help.

### Interrupts

#### What the system sends

A person presses **Ctrl+C**, a script runs `kill`, or the system shuts down. A **signal** is the message a `POSIX` system sends a process for such an event; `SIGINT` is the message for **Ctrl+C** and `SIGTERM` the polite request to end. Windows has no signals of that kind. It calls a **console control handler**, a function that the program registers, for **Ctrl+C**, **Ctrl+Break** and the closing of the console.

By default these events end the process on the spot, with no chance to save a file or close a project. `Platform::InstallInterruptHandler`, the second call in `main`, replaces that with a request: the handler writes down that the system asked, and the :term[main loop]{id=game-loop} honours the request after its frame. A process without a console never receives the Windows events, so an `Interactive` run never sees them.

#### A handler that only counts

The handler adds 1 to `s_InterruptRequests`, an atomic counter that the main loop reads through `Platform::IsInterruptRequested`. A signal may arrive while the interrupted thread holds a lock or is halfway through `malloc`. A handler that prints, allocates or takes a lock then waits for something that the interrupted code owns, and never returns. A function is **async-signal-safe** when the system promises that it works even then. A :term[lock-free]{id=lock-free} atomic add is such a function, and so are `sigaction` and `raise`; logging is not.

The second request has its own rule. After a person presses **Ctrl+C** twice, the program has not stopped, and the second request must stop it. On `POSIX` the handler restores the signal's default action with `sigaction` and raises the signal again, which ends the process as it would end without a handler. On Windows the handler flushes the log for at most 250 ms and returns false, which passes the event to the default handler. A process ended that way reports `STATUS_CONTROL_C_EXIT` on Windows, not 130, and on `POSIX` loses the log lines it had not written.

Closing the console differs: Windows ends the process at most 5 seconds later, whatever the handler does. Strata's handler counts the request and sleeps for 4.25 seconds, which leaves the main loop that time to finish in order. Then it flushes the log and returns.

#### Honoured in order

`Application::Run` asks `IsInterruptRequested` after every frame (`Strata/src/Strata/Core/Application.cpp`). If the program still runs, it logs a warning, sets the exit code to 130 unless the run had failed, and stops the loop. The number 130 is the shell's convention for death by `SIGINT`, 128 plus the signal number 2; Strata uses it for `SIGTERM` as well. A request that arrives in the frame where `--frames` ends the run changes nothing: the run was over already, and its exit code stays 0.

:::example[The headless editor, stopped with Ctrl+C]
Start the editor in a terminal with `StrataEditor --headless --frames 120`. The flag `--headless` makes `GetProgramRun` answer `Console`; the streams are the terminal's, so none is passed; and `ConnectStandardStreams` attaches to the terminal's console and connects both streams. A headless editor runs at 60 frames a second, so 120 frames take about 2 s.

Press **Ctrl+C** after 1 s, which is about frame 60. Windows runs the control handler on a thread of its own, and the counter becomes 1. The :term[main thread]{id=main-thread} is inside a frame and does not notice. After the frame, `Run` sees the counter, logs `Interrupted (Ctrl+C or a request to terminate): closing`, sets the exit code 130 and leaves the loop.

Press **Ctrl+C** twice within that frame instead, and the second press reaches the default handler: the process ends at once.
:::

Left alone, the run logs:

```text capture="headless-run"
[…] [info] App: Strata Editor 0.8.0 (Windows)
[…] [info] Strata: Engine modules: Input, Scene, Renderer, Physics, Audio, Animation, Scripting, World, GameUI. Scene systems update in the order UI, Scripting, Animation, World, Physics, Audio
[…] [info] Strata: JobSystem: 23 worker threads, 2 I/O threads, 20 background threads
[…] [info] Strata: Graphics device: NVIDIA GeForce RTX 5090 (Vulkan 1.3.0, driver 621.1.0)
[…] [info] Strata: AudioEngine: mixing without an output device (48000 Hz, 2 channels)
[…] [info] Strata: RpcServer: listening on 127.0.0.1:…
[…] [info] App: Automation: listening on 127.0.0.1:… (StrataCLI and its MCP server find this editor through its session file)
[…] [info] App: Started in … s
[…] [info] Strata: RpcServer: stopped
[…] [info] App: Automation: stopped (0 requests answered)
[…] [info] Strata: AudioEngine: shut down
```

1. **Line 1:** The editor logs its version on its own :term[logger]{id=logger}, `App`.
2. **Lines 9–11:** The run ends at frame 120 with the services stopping, no warning and exit code 0.

### Scheduling and power

#### Priorities and the quantum

A :term[processor core]{id=processor-core} runs one thread at a time, and a program often has more threads that want to run than the computer has cores. The operating system decides who runs. Each thread has a **thread priority**, a rank that the system uses to pick a thread when several are ready, and a thread of a higher rank runs before one of a lower rank.

The **scheduling quantum** is the slice of time a thread may use before the system considers switching to another thread of the same rank. Its length depends on the system and runs from a few milliseconds to tens of milliseconds. Threads of equal rank take turns by quantum, and a thread of a lower rank waits until the higher ones have no work.

A worked example shows why Strata cares. Take a computer with 4 cores. The main thread and 2 workers are busy with a frame, and an import starts 8 background threads that compress textures. That makes 11 busy threads on 4 cores, so with equal ranks each gets 4 ÷ 11 = 0.36 of a core. The main thread needs a whole core to finish its frame on time, so its frame takes 1 ÷ 0.36 = 2.75 times as long.

Lower the 8 background threads by one rank. The 3 threads of the frame take 3 cores first, and the background threads share the fourth: the frame runs at full speed.

Strata does this in the job system. A thread of a `Background` pool calls `Platform::SetCurrentThreadPriority(ThreadPriority::BelowNormal)` when it starts ([Threads and the job system](jobs.md)). The call maps one portable name to each system's own: `THREAD_PRIORITY_BELOW_NORMAL` on Windows, a nice value 5 above the main thread's on Linux and four steps below the default priority on macOS. On Linux a higher nice value means a lower rank.

If the system refuses, the thread keeps its rank and the pool logs a warning. Every job still runs, so this is no error.

#### Cores of two kinds, and power throttling

Many modern processors have two kinds of cores: fast performance cores and slower efficiency cores that use less power. The system decides which thread goes to which kind.

**Power throttling (EcoQoS)** is the way Windows 11 slows a process whose windows are in the background. It lowers the clock speed and, on processors with two kinds of cores, moves the process to the efficiency cores. For a mail program that is a good idea. For an editor that keeps building while another window has the focus, it is not. The comment in `Platform.h` records that an editor frame on the reference machine takes 1.3 to 1.9 times as long under it.

The :term[constructor]{id=constructor} of `Application` calls `Platform::DisableExecutionSpeedThrottling()` at startup and logs a warning when the system refuses. On Windows the :term[function calls]{id=function-call} `SetProcessInformation` with the mechanism named in `ControlMask` and absent from `StateMask`: the process says that it controls the setting and has disabled it. Linux and macOS have no such per-process setting, so the function does nothing there and returns true. The price is higher power use while the program is in the background.

#### Names for threads

`SetCurrentThreadName` gives the calling thread a name that debuggers and profilers show, such as `Strata Log Writer`. Linux limits a name to 15 characters, so the call cuts it; macOS keeps 63.

#### Precise sleep

The frame-rate cap of [the frame loop](frame-loop.md) ends each frame by waiting until a time. On Windows the :term[standard library's]{id=standard-library} sleep wakes only at the system's timer ticks, which come every 15.6 ms by default. A wait of 8.3 ms ends at the next tick, up to 15.6 ms later. `timeBeginPeriod` can make the tick finer, but it changes the clock of the whole computer and its power use, so Strata never calls it.

`Platform::SleepUntil` uses a high-resolution timer instead, a kernel object that a thread can wait on and that wakes it to within about a millisecond. Each thread makes its own on its first wait and closes it when the thread ends. Where no such timer exists, the function falls back to the standard library's sleep, and on Linux and macOS it always does, because the standard sleep is precise there.

:::example[A cap of 120 on a 15.6 ms tick]
Assume a tick of 15.625 ms (64 ticks a second), frames that cost nothing and a cap of 120, which asks for a frame every 8.33 ms. The first slot ends at the tick of 15.6 ms, and the next, 16.7 ms, at the tick of 31.2 ms. By then the slot at 25 ms has passed, so that frame starts at once. The sketch below counts the frames of a whole second: 95, not 120.
:::

The sketch uses the cap's own rule: slots are fixed, and a frame that ends late lets the next one start at once. It counts the frames of a second for a sleep that wakes at ticks and for a precise one, and prints how long each of the first 20 frames lasts at a cap of 60. Find the frames that last two ticks.

```cpp sketch="core-platform-tick.cpp"
// A frame-rate cap on a system whose sleep wakes only at timer ticks, against a sleep that wakes at the deadline.
// The clock is simulated in microseconds, so the output is the same on every machine.
#include <cstdint>
#include <cstdio>
#include <initializer_list>

namespace
{
	constexpr int64_t c_Tick = 15625; // 15.625 ms: 64 ticks a second

	// An ordinary sleep: the thread wakes at the first tick at or after the deadline.
	int64_t WakeAtTick(int64_t deadline)
	{
		return (deadline + c_Tick - 1) / c_Tick * c_Tick;
	}

	// The frames a cap lets through in one second, with the schedule of a frame pacer and frames that cost nothing.
	int CountFrames(int64_t period, bool precise)
	{
		int64_t now = 0;
		int64_t nextFrame = period;
		int frames = 0;
		while (now < 1'000'000)
		{
			now = precise ? nextFrame : WakeAtTick(nextFrame);
			frames++;
			nextFrame += period;
			if (nextFrame < now)
				nextFrame = now;
		}
		return frames;
	}
}

int main()
{
	for (const int rate : { 60, 120 })
	{
		const int64_t period = 1'000'000 / rate;
		std::printf("cap %3d: ordinary sleep %3d frames, precise sleep %3d frames\n", rate, CountFrames(period, false),
			CountFrames(period, true));
	}

	// The start of each frame under a cap of 60 and an ordinary sleep: most frames take one tick and a few take two.
	const int64_t period = 1'000'000 / 60;
	int64_t nextFrame = period;
	int64_t previous = 0;
	std::printf("intervals at cap 60:");
	for (int frame = 0; frame < 20; frame++)
	{
		const int64_t now = WakeAtTick(nextFrame);
		std::printf(" %.1f", static_cast<double>(now - previous) / 1000.0);
		previous = now;
		nextFrame += period;
		if (nextFrame < now)
			nextFrame = now;
	}
	std::printf(" ms\n");
	return 0;
}
```

```text output-of="core-platform-tick.cpp"
cap  60: ordinary sleep  60 frames, precise sleep  61 frames
cap 120: ordinary sleep  95 frames, precise sleep 121 frames
intervals at cap 60: 31.2 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 15.6 31.2 15.6 15.6 15.6 15.6 ms
```

1. **Lines 12–15:** an ordinary sleep wakes at the first tick at or after the deadline.
2. **Lines 25–29:** the precise sleep wakes at the slot, the ordinary one at the tick after it. A slot that has passed becomes now, so late frames cause no burst.
3. **Lines 49–57:** the same rule at a cap of 60, printing each frame's length.

At a cap of 60 the ordinary sleep keeps the count, 60 frames, but not the rhythm: most frames last one tick, 15.6 ms, and about every sixteenth lasts two, 31.2 ms.

## A toy version

The toy shows this page's two mechanisms in small form. The first is a seam: callers use a class `Platform`, and one block per system defines it. Strata's build chooses between two files; the toy keeps both blocks in one file, and `#if` chooses. Watch which lines hold a system name.

```cpp sketch="core-platform-toy.cpp"
// A toy platform seam: one interface, two implementations, one of them chosen when the program is built.
// In Strata the build chooses between two files; here one file holds both, so that #if does the choosing.
#include <cstdio>
#include <string>
#include <string_view>

// Detection: exactly one TOY_PLATFORM_* is defined, or the build stops.
#if defined(_WIN32)
	#define TOY_PLATFORM_WINDOWS
#elif defined(__linux__) || defined(__APPLE__)
	#define TOY_PLATFORM_POSIX
#else
	#error "The toy supports Windows, Linux and macOS"
#endif

// What the rest of the program sees: no operating-system header and no #if.
class Platform
{
public:
	static std::string_view GetName();
	static std::string GetUserDataRule(std::string_view applicationName);
};

#if defined(TOY_PLATFORM_WINDOWS)

// This block stands for Platform/Windows/WindowsPlatform.cpp.
std::string_view Platform::GetName() { return "Windows"; }

std::string Platform::GetUserDataRule(std::string_view applicationName)
{
	return "%LOCALAPPDATA%/" + std::string(applicationName);
}

#else

// This block stands for Platform/Posix/PosixPlatform.cpp.
std::string_view Platform::GetName() { return "a POSIX system"; }

std::string Platform::GetUserDataRule(std::string_view applicationName)
{
	return "$XDG_DATA_HOME/" + std::string(applicationName);
}

#endif

int main()
{
	// Game code calls the seam and never asks which system it runs on.
	std::printf("Running on %s\n", std::string(Platform::GetName()).c_str());
	std::printf("Settings go to %s\n", Platform::GetUserDataRule("Toy").c_str());
	return 0;
}
```

1. **Lines 8–14:** detection. Exactly one macro is defined, and any other system stops the build.
2. **Lines 17–22:** the seam. Callers see declarations only: no system header and no `#if`.
3. **Lines 24–44:** the two implementations. In Strata they are two files and the build compiles one.
4. **Lines 49–50:** the caller never asks which system it runs on.

Each system prints its own lines:

::::tabs{sync=os}
:::tab[Windows]

```text output-of="core-platform-toy.cpp" platform="windows"
Running on Windows
Settings go to %LOCALAPPDATA%/Toy
```

The Windows block ran.
:::
:::tab[Linux]

```text output-of="core-platform-toy.cpp" platform="linux"
Running on a POSIX system
Settings go to $XDG_DATA_HOME/Toy
```

The POSIX block ran.
:::
:::tab[macOS]

```text output-of="core-platform-toy.cpp" platform="macos"
Running on a POSIX system
Settings go to $XDG_DATA_HOME/Toy
```

The POSIX block ran here too.
:::
::::

The second toy is the interrupt: a handler that only counts, and a loop that honours the request after its frame. It sends itself `SIGINT` with `raise` in the middle of frame 2, the same event as a person's **Ctrl+C**. It prints the exit code instead of returning it, because the book's sketches must end with 0. Watch the order of its lines.

```cpp sketch="core-platform-interrupt.cpp"
// A toy interrupt: the handler only counts, and the loop honours the request after its frame.
#include <atomic>
#include <csignal>
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr int c_InterruptedExitCode = 130;

	// Lock-free, so that a signal handler may touch it.
	std::atomic<uint32_t> s_InterruptRequests = 0;
	static_assert(std::atomic<uint32_t>::is_always_lock_free);

	void OnInterruptSignal(int)
	{
		s_InterruptRequests.fetch_add(1);
	}
}

int main()
{
	std::signal(SIGINT, OnInterruptSignal);

	int exitCode = 0;
	for (int frame = 0; frame < 6; frame++)
	{
		std::printf("frame %d begins\n", frame);
		if (frame == 2)
		{
			std::printf("  Ctrl+C arrives in the middle of frame 2\n");
			std::raise(SIGINT);
		}
		std::printf("frame %d ends\n", frame);

		if (s_InterruptRequests.load() > 0)
		{
			std::printf("Interrupted: closing\n");
			exitCode = c_InterruptedExitCode;
			break;
		}
	}

	std::printf("the layers shut down in order\n");
	std::printf("exit code %d\n", exitCode);
	return 0;
}
```

```text output-of="core-platform-interrupt.cpp"
frame 0 begins
frame 0 ends
frame 1 begins
frame 1 ends
frame 2 begins
  Ctrl+C arrives in the middle of frame 2
frame 2 ends
Interrupted: closing
the layers shut down in order
exit code 130
```

1. **Lines 12–13:** the counter is atomic and lock-free, so that the handler may touch it.
2. **Lines 15–18:** the handler only counts.
3. **Lines 29–34:** the signal arrives in frame 2, and the frame still ends.
4. **Lines 36–41:** after the frame the loop reads the counter, stops and sets the exit code.

The seam toy has no `Process` and no second file, and the interrupt toy has no second request and no log. The next section shows what Strata adds.

## The real code

The real code follows the order in which a program meets it: `main` connects its streams, installs the handler, runs the loop, and the loop sleeps. Detection was quoted above. `ConnectStandardStreams` is Windows code, and its quote is the table of the contract as code. Find where it returns early, and which streams it replaces.

```cpp src="Strata/src/Platform/Windows/WindowsPlatform.cpp#L755-L793"
void Platform::ConnectStandardStreams(ProgramRun run)
{
	s_ProgramRun = run;
	// A stream the parent passed is anything but a console: a pipe, a file or the null device. Those are kept, never
	// replaced, so that whoever reads them (CTest, StrataCLI, CI) gets the output and the program's exit code as before.
	const auto isPassed = [](DWORD id)
	{
		const HANDLE handle = GetStdHandle(id);
		DWORD mode = 0;
		return handle != nullptr && handle != INVALID_HANDLE_VALUE && !GetConsoleMode(handle, &mode);
	};
	const bool outputPassed = isPassed(STD_OUTPUT_HANDLE);
	const bool errorPassed = isPassed(STD_ERROR_HANDLE);
	// Someone reads a pipe or a file; nobody reads the null device (a character device that is no console).
	s_ErrorOutputRead = errorPassed && GetFileType(GetStdHandle(STD_ERROR_HANDLE)) != FILE_TYPE_CHAR;
	// An Interactive run leaves the terminal alone: attached to its console, the terminal's Ctrl+C and closing it would
	// end the program, and the log would run into the shell's prompt (shells do not wait for windowed programs).
	if ((outputPassed && errorPassed) || run != ProgramRun::Console)
		return;
	// Started from a terminal: print into it. Started from Explorer, there is no console to attach to.
	if (!AttachConsole(ATTACH_PARENT_PROCESS))
		return;
	// The Win32 handle for code that writes to it (the log's console sink reads GetStdHandle), and the C runtime's stream.
	const auto connect = [](DWORD id, FILE* stream)
	{
		const HANDLE console = CreateFileW(L"CONOUT$", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING,
			0, nullptr);
		if (console == INVALID_HANDLE_VALUE)
			return false;
		SetStdHandle(id, console);
		// A stream that cannot be reopened prints nowhere, as when started from the desktop: there is nothing else to try.
		FILE* reopened = nullptr;
		return freopen_s(&reopened, "CONOUT$", "w", stream) == 0;
	};
	if (!outputPassed)
		connect(STD_OUTPUT_HANDLE, stdout);
	if (!errorPassed)
		s_ErrorOutputRead = connect(STD_ERROR_HANDLE, stderr);
}
```

1. **Lines 760–768:** a stream is passed when its handle is valid and is no console: a pipe, a file or the null device.
2. **Line 769:** the null device is a character device, so a stream sent there counts as passed but nobody reads it.
3. **Lines 772–773:** the early return of the table's first and second rows.
4. **Lines 775–776:** `AttachConsole` fails when the parent has no console, as after a start from Explorer.
5. **Lines 778–792:** only the streams not passed are connected, through `CONOUT$`, both for the log's Win32 handle and for the C stream.

The toy has nothing like this, because a `POSIX` program keeps the streams it is given. On `POSIX` the handler is the toy's handler with a second branch. Find the line that tells the first request from the second.

```cpp src="Strata/src/Platform/Posix/PosixPlatform.cpp#L903-L920"
// Requests to stop (InstallInterruptHandler): written by the signal handler, read by the main loop. Lock-free, so the
// handler may touch it.
std::atomic<uint32_t> s_InterruptRequests = 0;
static_assert(std::atomic<uint32_t>::is_always_lock_free);

void OnInterruptSignal(int signal)
{
	if (s_InterruptRequests.fetch_add(1) == 0)
		return;
	// A second request while the first is honored: what the signal does without the handler (sigaction and raise are
	// async-signal-safe). What the log has queued for the console and the file is lost with the process: waiting for
	// its writer (Log::FlushFor, as the Windows console handler does) is not async-signal-safe.
	struct sigaction action = {};
	action.sa_handler = SIG_DFL;
	sigemptyset(&action.sa_mask);
	sigaction(signal, &action, nullptr);
	raise(signal);
}
```

1. **Lines 905–906:** the counter is lock-free, and the compiler checks it.
2. **Lines 910–911:** `fetch_add` returns the old value, so 0 marks the first request, which only counts.
3. **Lines 915–919:** the second request restores the default action and raises the signal again; both calls are async-signal-safe.

The comment in the handler explains why it does not wait for the log, as the Windows handler does: waiting for the log's writer is not async-signal-safe. The installation takes a few lines, and reading the counter one.

```cpp src="Strata/src/Platform/Posix/PosixPlatform.cpp#L981-L995"
void Platform::InstallInterruptHandler()
{
	struct sigaction action = {};
	action.sa_handler = OnInterruptSignal;
	sigemptyset(&action.sa_mask);
	// System calls the signal interrupts go on: the request is only noted, and the main loop honors it.
	action.sa_flags = SA_RESTART;
	sigaction(SIGINT, &action, nullptr);
	sigaction(SIGTERM, &action, nullptr);
}

bool Platform::IsInterruptRequested()
{
	return s_InterruptRequests.load() > 0;
}
```

1. **Lines 983–985:** the action names the handler and starts with no blocked signals.
2. **Line 987:** `SA_RESTART` lets an interrupted system call continue, so only the counter changes.
3. **Lines 988–989:** the same handler serves both signals.

The last quote is the precise sleep of Windows. The class holds the timer and the function uses it; find what happens when no timer exists.

```cpp src="Strata/src/Platform/Windows/WindowsPlatform.cpp#L337-L380"
	// The calling thread's high-resolution waitable timer for SleepUntil: made on the thread's first wait, closed when the
	// thread ends. Null where the system cannot make one (before Windows 10 1803).
	class ThreadWaitTimer
	{
	public:
		ThreadWaitTimer()
			: m_Handle(CreateWaitableTimerExW(nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS))
		{
		}

		~ThreadWaitTimer()
		{
			if (m_Handle)
				CloseHandle(m_Handle);
		}

		ThreadWaitTimer(const ThreadWaitTimer&) = delete;
		ThreadWaitTimer& operator=(const ThreadWaitTimer&) = delete;

		HANDLE Get() const { return m_Handle; }
	private:
		HANDLE m_Handle = nullptr;
	};

	thread_local ThreadWaitTimer t_FrameTimer;

}

void Platform::SleepUntil(std::chrono::steady_clock::time_point deadline)
{
	const auto now = std::chrono::steady_clock::now();
	if (deadline <= now)
		return;
	if (const HANDLE timer = t_FrameTimer.Get())
	{
		// A due time relative to now, in 100-nanosecond intervals (negative: relative).
		const int64_t intervals = std::chrono::duration_cast<std::chrono::nanoseconds>(deadline - now).count() / 100;
		LARGE_INTEGER due = {};
		due.QuadPart = -std::max<int64_t>(intervals, 1);
		if (SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0) && WaitForSingleObject(timer, INFINITE) == WAIT_OBJECT_0)
			return;
	}
	std::this_thread::sleep_until(deadline);
}
```

1. **Lines 342–345:** the constructor asks the system for a timer with the high-resolution flag.
2. **Line 361:** the timer is `thread_local`: each thread makes its own on its first wait and closes it when the thread ends.
3. **Lines 372–376:** the due time is negative, which means relative, in units of 100 ns, and at least 1; the thread sets the timer and waits for it.
4. **Line 379:** where there is no timer, or a call fails, the standard sleep runs.

The toy never slept; it moved a simulated clock. The real `FramePacer` of [the frame loop](frame-loop.md) calls this function with the time of the next slot, and nothing else in the engine knows that Windows needs a special timer.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| `#if` at every use | Small projects with a few system differences | No second file for a short difference | System code spread over the engine, and branches nobody tests |
| A virtual class with one :term[subclass]{id=derived-class} per system | Godot's `OS` class | A system chosen while running, which lets tests replace the system | A virtual call for each query, and a class hierarchy for a choice that never changes |
| A library for system services | `SDL`, which offers thread priorities and simple message boxes | Fewer functions to write and test | A dependency that does not know Strata's rules, such as the single seam for processes |
| A finer timer with `timeBeginPeriod` | Windows programs that need short sleeps | No timer for each thread | A changed clock and more power use for every program on the computer |

## How it is tested

The tests that guard the seam live in `StrataTests/src/`, and none of them needs a :term[graphics card]{id=gpu}.

- `Core.Platform` (`StrataTests/src/Core/PlatformTests.cpp`): queries, memory, the process's start time, the folders, the fonts, and the `Process` cases for output, input, timeouts and process trees. A process of its own tests the opt-out of power throttling, because the test runner opted out at startup.
- `Core.JobSystem` (`StrataTests/src/Core/JobSystemTests.cpp`): a job of the background pool runs at the lower priority, and the other pools keep the normal one.
- `EndToEnd.StandardStreams` (`StrataTests/src/Editor/StandardStreamsProcessTests.cpp`): the editor prints to the pipes it is given and ends with its exit code. On `POSIX`, `SIGINT` and `SIGTERM` end a headless editor in order with exit code 130. On Windows, a helper with a hidden console presses **Ctrl+C**.
- `Architecture.Layering` (`StrataTests/src/Architecture/LayeringTests.cpp`): the window system, the graphics interface and the operating system stay in their folders.
- `Perf.FramePacer` (`StrataTests/src/Perf/FramePacerPerfTests.cpp`): how closely the cap holds the editor's :term[frame rates]{id=frame-rate}, in `Release` and `Dist` builds only.

Run a suite directly after a `Debug` build on Windows. The end-to-end tests start the built editor, so build it first:

```powershell
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Platform
build/windows/bin/Debug/StrataTests.exe --test-suite=EndToEnd.StandardStreams
```

The first command runs the seam's tests and the second the tests of the terminal and the interrupt; each prints how many test cases passed.

## Changing it safely

The seam grows by one function at a time, and the steps are the same each time.

1. Declare the function in `Platform.h` with a comment that says what it returns on each system and what a failure looks like.
2. Define it in `WindowsPlatform.cpp` and in `PosixPlatform.cpp`. Where Linux and macOS differ, add an `#if defined(ST_PLATFORM_MACOS)` inside the `POSIX` file, as `SetCurrentThreadName` does.
3. Test it in `PlatformTests.cpp`, in the `Core.Platform` suite.
4. Run `Architecture.Layering`: it fails when a system header slipped into a file that may not include it.
5. Build on every system you can. The continuous integration builds Windows, Linux and macOS and catches what a local compiler accepts.

The rules that apply, each with its reason:

- Never include `<Windows.h>` in a header, or an X11 header anywhere in engine code: a macro defined there changes every file that follows.
- Never call `timeBeginPeriod`: it changes the timer of the whole computer. Use `Platform::SleepUntil`.
- Keep the interrupt handler to atomic work: a lock or an allocation inside a signal can wait forever.
- Give each program the `ProgramRun` that matches its purpose: a wrong one prints into a person's terminal or hides output from a tool.

:::why[Why the seam is static and chosen at link time]
The seam holds services that never change while a program runs, and some calls sit on hot paths: a clock, a sleep, a memory query. A static class needs no object and no virtual call, and the build omits the code of the other systems. The cost is that a test cannot replace `Platform` with a fake, so tests that need control over the system start a helper process.
:::

## What went wrong before

Once, the frame cap slept with the standard library's `sleep_until`. On Windows the sleep waited for the 15.6 ms tick, so a cap of 120 ran 20 % slow, and a cap of 60 gave frames of uneven length, as the sketch shows. The fix was `Platform::SleepUntil` with a timer for each thread, and the suite `Perf.FramePacer` measures how closely the cap now holds the rates the editor offers.

## Summary

- Engine code reaches the system through `Platform` and `Process`, declared once and defined per system in `Platform/Windows/` and `Platform/Posix/`; the build compiles one, and system, window and graphics headers stay in their folders.
- The editor and the :term[runtime]{id=runtime} are GUI programs on Windows. `ConnectStandardStreams` keeps passed streams, attaches a `Console` run to its terminal and leaves an `Interactive` run alone. PowerShell waits only when the output is piped.
- **Ctrl+C**, **Ctrl+Break**, console close, `SIGINT` and `SIGTERM` become a counted request; `Run` honours it after the frame with exit code 130, and a second request ends the process.
- Background threads run below normal priority so that frame work keeps the cores; the process opts out of power throttling; `SleepUntil` uses a timer for each thread, never `timeBeginPeriod`.
- A new `Platform` function is declared once, defined in both files, tested in `PlatformTests.cpp` and checked with `Architecture.Layering`.

## Check yourself

1. A new `Platform` function needs `GetComputerNameExW`. Where may `#include <Windows.h>` appear?

   - A. In `Platform.h`, so that both files see the types.
   - B. In `WindowsPlatform.cpp`, which already includes it.
   - C. In any `.cpp` of the engine, as long as it is not a header.
   - D. In `Platform.h`, inside `#if defined(ST_PLATFORM_WINDOWS)`.

   :::answer{tests="platform-seam,add-function"}
   B. The Windows folder owns `Windows.h`, and `Architecture.Layering` reports the include from any other file, which rules out C. A and D put it in a header, which hands its macros (`near`, `far`, `CreateWindow`) to every file that includes the header; the `#if` only hides them on the other systems.
   :::

2. In PowerShell on Windows you run `StrataEditor.exe --headless --frames 10` with nothing piped. What happens, and why?

   :::answer{tests="windows-programs"}
   The prompt returns at once while the editor still runs, and its log lines appear in the middle of the next command. `$LASTEXITCODE` keeps the code of the command before. The editor is a GUI program, so PowerShell does not wait for it. The flag `--headless` makes it a `Console` run, so it attaches to the terminal's console and prints there. Pipe the output to `Out-Host`, or use `Start-Process -Wait`, to get the exit code.
   :::

3. A person presses **Ctrl+C** once in the terminal of a headless editor on Linux, and again 1 s later while the editor closes a large project. What happens, and what does the shell report?

   :::answer{tests="interrupt-path"}
   The first signal makes the handler add 1 to the counter, and the loop ends after its frame. The second finds the counter at 1, restores the default action of `SIGINT` and raises it again, so the system ends the process in the middle of its closing. The shell reports 130, which is 128 plus the signal number 2, although this time no code of the loop set it. On Windows the second press passes to the default handler, and the process ends with `STATUS_CONTROL_C_EXIT`.
   :::

4. A computer has 6 cores. A frame uses 3 busy threads, and an import starts 9 background threads. With equal priorities, what share of a core does each thread get, and how long does the frame take compared with a quiet computer? What changes if the background threads are `BelowNormal`?

   :::answer{tests="scheduling"}
   There are 12 busy threads on 6 cores, so each gets 6 ÷ 12 = 0.5 of a core, and a main thread that needs a whole core takes 2 times as long. With `BelowNormal` the 3 frame threads take 3 cores first and the 9 background threads share the other 3, so the frame runs at full speed.
   :::

## Exercises

1. **Basic.** Write a program that prints how many frames a cap of 120 lets through in one second when the system's tick is 15.625, 8, 4 and 1 ms. Predict the pattern of the results before you run it.

   :::answer[Worked solution]{tests="scheduling" solution="sketches/core-platform-caps.cpp"}
   The counting loop is the cap's: a slot every 8.33 ms, and a wait that ends at the first tick at or after the slot. Predict first: a tick longer than the period loses frames, because two slots pass in one wait; a tick shorter than the period ends within one slot, so the schedule recovers.

   ```cpp sketch="core-platform-caps.cpp"
   // How fine must a sleep's tick be to hold a cap of 120 frames a second? The clock is simulated, in microseconds.
   #include <cstdint>
   #include <cstdio>
   #include <initializer_list>

   namespace
   {
   	// The frames in one second when each wait ends at the first tick at or after the frame's slot.
   	int CountFrames(int64_t period, int64_t tick)
   	{
   		int64_t now = 0;
   		int64_t nextFrame = period;
   		int frames = 0;
   		while (now < 1'000'000)
   		{
   			now = (nextFrame + tick - 1) / tick * tick;
   			frames++;
   			nextFrame += period;
   			if (nextFrame < now)
   				nextFrame = now;
   		}
   		return frames;
   	}
   }

   int main()
   {
   	for (const int64_t tick : { 15625, 8000, 4000, 1000 })
   		std::printf("tick %6.3f ms: %3d frames at a cap of 120\n", static_cast<double>(tick) / 1000.0, CountFrames(1'000'000 / 120, tick));
   	return 0;
   }
   ```

   ```text output-of="core-platform-caps.cpp"
   tick 15.625 ms:  95 frames at a cap of 120
   tick  8.000 ms: 120 frames at a cap of 120
   tick  4.000 ms: 120 frames at a cap of 120
   tick  1.000 ms: 120 frames at a cap of 120
   ```

   1. **Line 16:** the wait ends at the first tick at or after the slot.
   2. **Lines 19–20:** a slot that has passed becomes now, so late frames cause no burst.

   Only the 15.625 ms tick, which is longer than the period of 8.33 ms, loses frames.
   :::

2. **Medium.** Trace it yourself. Start a headless editor in a terminal without `--frames`, press **Ctrl+C**, and follow the request from the system's handler to `Platform::IsInterruptRequested` in `Run`, the warning line and the exit code 130. Use breakpoints, or a search for the names. Then say what a second **Ctrl+C** does.

   :::answer[Worked solution]{tests="interrupt-path"}
   On Windows the path starts in `OnConsoleControl` in `Strata/src/Platform/Windows/WindowsPlatform.cpp`; on `POSIX` it starts in `OnInterruptSignal` in `Strata/src/Platform/Posix/PosixPlatform.cpp`. Both do `s_InterruptRequests.fetch_add(1)`. A search for `IsInterruptRequested` finds the reader in `Application::Run` in `Strata/src/Strata/Core/Application.cpp`, which logs the warning and sets `m_ExitCode` to `c_InterruptedExitCode`, 130, when it is still 0. The `main` of `Strata/src/Strata/Engine/EntryPoint.h` returns `GetExitCode()`. A second press finds the counter above 0: the Windows handler flushes the log and returns false, and the `POSIX` handler restores `SIG_DFL` and raises the signal again.
   :::

3. **Hard.** Add a function `GetHostName` to `Platform`, which returns the computer's name as `UTF-8`, or nothing when the system does not tell. Describe each change, for Windows and for `POSIX`, and the test.

   :::answer[Worked solution]{tests="add-function"}
   In `Platform.h`, declare `static std::optional<std::string> GetHostName();` with a comment that names the calls and the failure. In `WindowsPlatform.cpp`, call `GetComputerNameExW` with `ComputerNameDnsHostname`, first with a null buffer to learn the size, then with a buffer, and convert the result with `WindowsUtils::WideToUtf8`; return nothing when a call fails. In `PosixPlatform.cpp`, call `gethostname` into a buffer of 256 :term[bytes]{id=byte}, enough for the longest host name. Write the end mark by hand, because the call does not promise one when the name is cut. No `#if` is needed, since Linux and macOS both have the call.

   In `PlatformTests.cpp`, add a case to `Core.Platform` that checks the result has a value and is not empty. Then run `Core.Platform` and `Architecture.Layering`: the layer test stays green, because `unistd.h` is allowed in `Platform/Posix/` and `Windows.h` in `Platform/Windows/`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Platform.h`: `Platform`, `ThreadPriority`, `ProgramRun`; `Strata/src/Strata/Core/PlatformDetection.h`: the `ST_PLATFORM_*` macros; `Strata/src/Strata/Core/Process.h`: `Process`, `ProcessSpecification`, `ProcessOutputMode`.
- `Strata/src/Platform/Windows/`: `WindowsPlatform.cpp`, `WindowsProcess.cpp`, `WindowsUtils.h`; `Strata/src/Platform/Posix/`: `PosixPlatform.cpp`, `PosixProcess.cpp`.
- `Strata/src/Strata/Engine/EntryPoint.h`: `main`, which calls `ConnectStandardStreams` and `InstallInterruptHandler`.
- `Strata/src/Strata/Core/Application.cpp`: the opt-out of power throttling in the constructor, and the poll of `IsInterruptRequested`.
- `Strata/src/Strata/Core/JobSystem.cpp`: the background threads' priority; `Strata/src/Strata/Core/Timer.h`: `FramePacer`, the user of `SleepUntil`.
- `StrataEditor/CMakeLists.txt` and `StrataRuntime/CMakeLists.txt`: `WIN32_EXECUTABLE` and `/ENTRY:mainCRTStartup`; `StrataTests/Architecture/Layers.json`: `ExternalOwners`.
- Tests: `StrataTests/src/Core/PlatformTests.cpp`, `JobSystemTests.cpp`, `StrataTests/src/Editor/StandardStreamsProcessTests.cpp`, `StrataTests/src/Architecture/LayeringTests.cpp`, `StrataTests/src/Perf/FramePacerPerfTests.cpp`.

## Further reading

- [Microsoft, SetConsoleCtrlHandler](https://learn.microsoft.com/en-us/windows/console/setconsolectrlhandler): the Windows handler, its thread and its five-second limit; intermediate.
- [Microsoft, timeBeginPeriod](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod): the system-wide timer resolution and its cost; advanced.
- [Microsoft, CreateWaitableTimerExW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createwaitabletimerexw): the high-resolution timer flag; advanced.
- [cppreference, `std::signal`](https://en.cppreference.com/w/cpp/utility/program/signal): what the language allows in a handler; intermediate.
- The Linux manual page signal-safety(7), on man7.org: the list of async-signal-safe functions; advanced.
- The GLFW documentation, on glfw.org: the window library Strata uses behind `Window`; beginner.
- Jason Gregory, Game Engine Architecture: the chapter on the platform independence layer; intermediate.
