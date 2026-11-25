---
id: core/first-frame
title: "From main to the first frame"
description: "How a Strata program starts: the one main, the launch, the specification, the startup order, a start that fails cleanly, the command line and the exit codes."
kind: internals
size: L
tracks: [E]
needs: [core/conventions]
time: 95
learn:
  - id: trace-start
    text: trace the start of a Strata program from main to its first frame, naming each step in order
  - id: specification
    text: explain what each field of ApplicationSpecification decides, with the editor's --headless and --no-gpu as the example
  - id: unwinding
    text: explain what a failed start ends, in which order, and how the person learns why
  - id: exit-codes
    text: predict the exit code of a Strata program from its command line and from how its run ended
  - id: failing-step
    text: add a startup step that fails cleanly, and test it
since: 0.3.0
status: final
---

A Strata program is a process that starts in `main`, makes one `Application`, lets it run frames and ends with an :term[exit code]{id=exit-code}. This page follows that path from the first line of `main` to the first frame. It also follows the paths that end earlier: a request for help, a :term[command line]{id=terminal-command} that nobody understands, a window that cannot open, an engine module that cannot start. Each of them must end cleanly. The program releases what it started, tells the person why it stopped, and returns a code that a script can read.

The page does not teach the :term[frame loop]{id=game-loop} that `Run` starts ([The frame loop](frame-loop.md)). Other pages teach what an engine module is ([Engine modules](engine-modules.md)), how Windows attaches a terminal to a program ([The platform layer](platform.md)) and the registries that the composition root opens ([Layers and registries](layers-registries.md)).

## The problem and how engines solve it

Starting a program looks like the simple part. The :term[operating system]{id=operating-system} calls `main`, and `main` calls what the program needs. The difficulty is that an engine needs many services before its first frame: threads for background work, a window, a graphics device, a sound device, a project. Each of them can fail on some computer. A start must answer two questions: in which order do the services start, and what happens to the ones that already run when a later one fails?

Engines answer in three common ways. The first is to write the calls in `main`: open the window, create the device, start the sound, one after the other. A program then shows exactly what it runs, and nothing starts that it did not ask for. The cost is repetition: the editor, the game :term[runtime]{id=runtime} and every test program repeat the list, and each failure needs cleanup code that someone wrote by hand in the reverse order. A forgotten line appears on the one computer where that step fails.

The second way gives each service a start function and a stop function, and keeps the service in a global object that any code can reach. The program calls the start functions in an order that the programmer knows, and the stop functions in the reverse order. The cost is that the order lives in a person's head. Services reach each other without saying so, and a test cannot make a second copy of a global object.

The third way uses static :term[constructors]{id=constructor}: objects at file level whose constructors C++ runs before `main`. A service that is linked in starts itself. The cost is large. C++ does not define the order in which different files run their static constructors, and a constructor that fails cannot tell the person anything, because `main` has not run and the log is not open.

Strata keeps one object, the `Application`, whose constructor starts the program's parts in a fixed order. The program hands it a list of the services it wants, and the application calls nothing else of the engine. If a part fails, the constructor ends the parts that started, in reverse, and reports once. The cost is that every program must give its list, and that services find each other by asking for a type, as [Engine modules](engine-modules.md) shows.

## The map: the start sequence

The start runs on the main thread; the job system's worker threads begin at one step, `JobSystem::Init`. The sequence has three owners. The program (the editor or the runtime) owns the decisions: what kind of run this is, what the command line means, which modules to run. The shared `main` in `Strata/src/Strata/Engine/EntryPoint.h` owns the order of the calls. The `Application` owns what exists after the launch: the window, the layers, the modules and the loop.

```mermaid caption="The calls of a start, from the shared main function to the end of the run. The program answers two questions before the application exists." alt="A sequence diagram with five lanes: the main function, the program, the platform layer, the composition root and the application. The main function asks the program what kind of run this is, then asks the platform layer to connect the standard streams and install the interrupt handler. It asks the program for a launch, calls the composition root, and calls the launch's create function, which makes the application and runs its startup. Last it calls run and reads the exit code."
sequenceDiagram
    participant M as main
    participant P as Program
    participant L as Platform
    participant R as Composition root
    participant A as Application
    M->>P: GetProgramRun(commandLine)
    P-->>M: Console or Interactive
    M->>L: ConnectStandardStreams(run)
    M->>L: InstallInterruptHandler()
    M->>P: CreateApplication(commandLine)
    P-->>M: ApplicationLaunch, or nothing
    M->>R: RegisterBuiltinModules(Registration)
    M->>A: Create(): startup steps
    M->>A: Run()
    A-->>M: GetExitCode()
```

## The contract

The contract is what a program may assume of the start and what it must do. The sections below follow the order in which data flows. First comes the kind of run, then the launch, the specification and the startup order. Last come what happens when a step fails and what the process returns.

### One main for both programs

The editor and the runtime have the same `main`. The file `Strata/src/Strata/Engine/EntryPoint.h` holds it, and each program includes that file once, after it defines the two functions that `main` calls: `GetProgramRun` and `CreateApplication`. The file defines `main` itself, so only one :term[source file]{id=source-file} of a program may include it; a second one would define `main` twice and the link would fail. That is the point: one entry for the whole engine means that every program starts, stops and reports in the same way.

On Windows the editor and the runtime are windowed programs with no console window; [The platform layer](platform.md) teaches how they still print into a terminal.

### The kind of run

Before anything prints, the program decides what kind of run this is. A **Console run** is a run whose output is the point: it prints help or a usage error, or it runs without a window for a tool, a script or a person at a terminal. An **Interactive run** is a person's windowed session. A Console run prints into the terminal that started it, and the terminal's Ctrl+C asks it to quit. An Interactive run leaves the terminal alone, and a fatal error that no stream shows goes to a dialog.

The decision comes from the command line, and the program writes it in `GetProgramRun`. The editor answers Console for `--help`, `-h` and `--version`, for any command line it does not understand, and for the scripted options `--headless`, `--no-gpu`, `--frames`, `--commands`, `--quit-after-commands` and `--window-size`. Anything else is Interactive. The answer goes to `Platform::ConnectStandardStreams`, the first call of `main` after the command line is read. The order matters: the stream is connected before the log opens its console output, so the first line already goes to the right place.

`main` then calls `Platform::InstallInterruptHandler`. From that point Ctrl+C in the terminal of a Console run, or a termination signal, does not kill the process. It sets a flag that the frame loop reads, so that the run ends in order. Both calls are the platform page's; this page only uses them.

### The launch

`CreateApplication` is the program's second function. It reads the command line and returns a `std::optional<ApplicationLaunch>`. An `ApplicationLaunch` holds two things: `Registration`, the options of the composition root, and `Create`, a function that makes the application. The two parts exist so that registration can happen before the application does. The editor puts its asset pipeline and its preference sections into `Registration`, and builds the application only when `Create` runs.

An empty optional means that there is nothing to run. The program has already printed what it had to print, and it stores the exit code of the process with `Application::SetStartupExitCode`. The default is 1, the code of a start that failed. After `--help` and `--version` the editor stores 0, and after a command line it does not understand it stores 3.

`main` then calls `Engine::RegisterBuiltinModules`, the composition root. It opens the registries, runs each module's registration in layer order, and freezes them. [Layers and registries](layers-registries.md) teaches it; for this page it is the step that must finish before any application, layer or module touches a registry.

### The specification

`Create` builds an `Application` from an `ApplicationSpecification`: a plain :term[struct]{id=struct} whose fields say what the program is. The table lists every field with its default and what it decides.

| Field | Default | What it decides |
| --- | --- | --- |
| `Name` | "Strata Application" | The window title if the window has none, the title of dialogs and the start of failure messages |
| `WorkingDirectory` | empty | The folder the process moves to at startup; empty keeps the current one |
| `CommandLineArgs` | empty | The command line, kept for code that asks later |
| `Window` | a `WindowSpecification` | Title, size and state of the window |
| `WindowFactory` | empty | A function that makes the window instead of `Window::Create`; tests give a stand-in, and a result of null means the window could not open |
| `Headless` | false | Whether the program runs without a window |
| `Modules` | empty | The factories of the engine modules the program runs |
| `Jobs` | defaults | The sizes of the job system's thread pools |
| `MaxFrames` | none | A number of frames after which the loop closes by itself |
| `MaxTimestep` | 0.25 | The longest step, in seconds, that one frame may count, so that a pause in a debugger does not become a leap |
| `MaxFrameRate` | 0 | The highest number of frames per second; 0 means no limit |

A program is **headless** when it runs without a window. The editor reads two options into `Headless`. `--headless` runs without a window but keeps the graphics device, so a capture of the scene still works. `--no-gpu` drops the device as well and implies `--headless`: it is for computers without a :term[graphics processing unit]{id=gpu} (GPU), where the editor still exports games and processes assets. A headless program has no display to pace its frames, so the editor sets `MaxFrameRate` to 60; without it, a headless editor that waits for automation would keep one core of the processor busy.

The editor's modules follow from the same two options. Graphics is in the list unless `--no-gpu` is given. Audio is always there, and it gets a null device when the program is headless, so sound is mixed but never played. The module that draws the interface (ImGui) is in the list only when the program is not headless, since it needs a window. The project module is always there.

### One Application at a time

:::rule[Only one Application exists at a time]
The `Application` constructor checks that its static pointer `s_Instance` is empty, and the check stays in shipping builds (`ST_CORE_VERIFY`). `Application::Get()` returns that pointer, so a second application would take the first one's place. Tests make many applications, one after another and never together, and they never create graphics devices: they share one per process through `Tests::GPUContext`. The rule is in the engine's `AGENTS.md`; [Engine modules](engine-modules.md) shows how a test application is made.
:::

The **application** is the object that owns the window, the layers, the engine modules, the queue of work for the main thread and the pacing of frames, and that runs the loop. It is also the only holder of the state that a frame needs.

### The startup order

The constructor runs these steps in this order. Only the window and the modules can stop the start; the other steps log a problem and continue.

1. The constructor claims `s_Instance`, as the rule above says.
2. The constructor asks the system not to slow the process down while its windows are in the background (`Platform::DisableExecutionSpeedThrottling`). If the system refuses, the constructor logs a warning.
3. The constructor moves to `WorkingDirectory` when that is set. A failure is logged as an error and the start continues.
4. The constructor starts the job system with `Jobs` (`JobSystem::Init`).
5. Unless the program is headless, the constructor opens the window, through `WindowFactory` when there is one and through `Window::Create` when not. A window with no title takes the application's name. A result of null is a failure.
6. The constructor resets the input state (`Input::Reset`). This step also runs after a failed start, because tests run several applications in one process.
7. The constructor makes the engine modules from the list, puts them in dependency order, and calls each one's `OnInit`. A module that returns false is a failure.

After the constructor, `Run` calls the application's `OnInit` and enters the loop. The first pass of that loop is the first frame. The editor's own constructor runs between the two: it sets the window icon, applies the editor's theme and fonts, and pushes the `EditorLayer`, but only when the base constructor left the application running.

### When a start fails

A failed start ends only what has started, in the reverse order, and then tells the person. The table lists the three failures of the constructor.

| What fails | What exists at that moment | What the constructor does | What the person reads |
| --- | --- | --- | --- |
| The window cannot open | The job system | Reports, sets the exit code 1 and stops; no module is made. The :term[destructor]{id=destructor} later ends the job system | A message that the window could not open, with the advice to start with `--headless` when no display exists |
| The module list cannot be ordered: a missing dependency, a cycle, a name used twice, a factory that makes nothing | The job system and the window | Closes the window and reports; no module started | A message that names the modules |
| A module's `OnInit` returns false | The job system, the window and the modules before it | Clears the layers, releases the started modules in reverse, stops the job system, shuts the modules down in reverse, closes the window and then reports | The `Problem` and `Advice` that the module describes; with an empty `Problem` only the log says which module failed |

Two details are worth knowing. First, the report comes last on purpose: a dialog that appears while the program's window is still open would sit on top of a half-started program, and the person would not know what to close. Second, a failed start never calls `OnStop` on a module, because `OnStop` belongs to a loop that never ran. The modules that started get `OnRelease`, which lets go of what needs the job system and the device, and then `OnShutdown`, which ends the rest. The module that failed gets nothing: it cleans up what it started itself, before it returns false.

The constructor sets `m_Running` to false and the exit code to 1. `main` still calls `Run`, which returns at once, reads the exit code, destroys the application and shuts the log down. The destructor ends whatever is left, and what has already ended is not ended again.

### Telling the person

`Application::ReportFatalError` takes a title, a problem and an optional advice. It does four things in this order.

1. The function writes the problem and the advice to the log at the critical level.
2. The function stops there when `Platform::ShouldShowErrorDialogs` is false. That function is true only for an Interactive run whose :term[standard error]{id=standard-error} reaches no reader. Examples are a program that the desktop started, one that left its terminal alone, and one whose output goes to the null device. A terminal, a pipe or a file counts as a reader. A Console run never shows a dialog, so tools, build servers and other programs do not wait for one.
3. The function builds the message: the problem, a blank line, the advice, a blank line and a line that names the log file, `The log has the details: <path>`. It flushes the log so that the file holds everything.
4. The function shows the message in a dialog and waits until the person dismisses it. The :term[environment variable]{id=environment-variable} `STRATA_ERROR_DIALOG_FILE` replaces the dialog for tests: when it names a file, the function writes the title, a line break and the message there, and returns.

The function runs on the main thread and blocks. If no dialog program exists, as on a Linux desktop without `zenity` or `kdialog`, the problem stays in the log, and the function logs a warning.

### The command line

`CommandLine` holds the arguments as text, with the program's name at index 0, and four functions read it. `HasFlag("--x")` is true for `--x` and for `--x=value`. `GetOption` returns the text after `--x` or after `--x=`, and for the form `--x value` it returns the next argument whatever it looks like. `GetIntOption` accepts the whole text as one :term[integer]{id=integer} and nothing else. `GetSizeOption` reads `WxH`, two whole numbers from 1 to 65,535 joined by `x`, as in `1920x1080`.

`CommandLineOptions` catches what a program does not understand. A program lists its options in a table of name, value placeholder and description. `FindUnknownArgument` walks the arguments after the program's name, cuts each one at the first `=` and looks the name up. It reports an unknown name, a flag that was given a value, and an option that has no value left; when an option takes its value as the next argument, it skips that argument. `FormatUsage` writes `Usage: <program> [options]`, a blank line, `Options:`, and one line for each option.

The editor answers `--help` and `--version` first, on :term[standard output]{id=standard-output}, before any log file, window or session exists, and stores exit code 0. A problem found by `FindUnknownArgument` or by the editor's own value checks goes to standard error, followed by the usage, with exit code 3 (`CommandLineOptions::c_UsageExitCode`). Because the answer comes before the log opens, a wrong command line leaves no log file.

### Exit codes

A run ends with one of four codes.

- **0**: the run ended as planned. The window closed, `MaxFrames` was reached, a command asked to quit, or the program printed what `--help` or `--version` asked for.
- **1**: the start failed, in the constructor or before the launch, or an exception left the frame loop. A program that returns no launch and sets no other code also gets 1.
- **3**: the command line is not understood.
- **130**: Ctrl+C or a termination signal ended the run. The number is 128 plus 2, the number of the interrupt signal, as shells report for an interrupted program. The frame loop sets it only when the code is still 0, so a run that had failed keeps its own code.

An exception that leaves the frame loop ends with 1 as well. `Run` logs it as critical, stops the loop, shuts down in order and sets the code 1 only when it was still 0, so a code set before stays ([The frame loop](frame-loop.md) shows the code). The log names the exception.

The programs add codes of their own. The runtime ends a headless run with 2 after a script crash, and it exits with the code that a game asks for when it quits ([The runtime](../worlds/runtime.md)). The editor ends with 1 when a command script fails or a screenshot cannot be saved. It also ends with 1 when the automation server of a headless editor without `--frames` cannot start, since nothing could reach it ([Command scripts](../editor/command-scripts.md)).

## The example: an editor to its first frame

:::example[The editor from a terminal, 120 frames]
Start the editor you built in [your first change](first-change.md) without a window, and let it close after 120 frames. The command line has four arguments, the program's name at index 0 and three more.

```sh
StrataEditor --headless --frames 120
```

In Windows PowerShell, send the output to `Out-Host`, so that PowerShell waits for the windowed editor and prints its
log, then read the exit code:

```powershell
.\StrataEditor.exe --headless --frames 120 | Out-Host
$LASTEXITCODE
```

`GetProgramRun` finds `--headless` in its list of scripted options and answers Console. The check for unknown arguments passes, since `--frames` takes the next argument as its value, and the value check passes since 120 is positive. `CreateApplication` opens the log at `Logs/StrataEditor.log` in your :term[user data folder]{id=user-data-folder}, then fills the specification: `Headless` is true, so `MaxFrameRate` becomes 60. The modules are Graphics, Audio with a null device and Project, with no ImGui because there is no window, and `MaxFrames` is 120.

The composition root runs, and `Create` builds the application. It skips the window, starts the job system, resets the input and starts the three modules in the order of the list. Then the editor's constructor pushes the `EditorLayer`, and `Run` enters the loop. After the 120th counted frame the loop stops, which takes at least 2 seconds at 60 frames a second. The exit code is 0, the layers and modules end in reverse, and `main` closes the log.
:::

The same path ends differently when a start fails. The editor opens its window before it searches for a graphics device, so a computer with no usable driver shows the person a window that closes at once, followed by a dialog. The editor's own test makes such a computer by pointing the Vulkan loader at a driver file that does not exist, and sends the dialog's text to a file. It sets two variables, since older loaders read `VK_ICD_FILENAMES`. You can do the same.

::::tabs{sync=os}
:::tab[Windows]

In PowerShell, set the three variables in the terminal, start the editor and print its exit code:

```powershell
$env:VK_DRIVER_FILES = 'C:\nowhere\NoDriver.json'
$env:VK_ICD_FILENAMES = 'C:\nowhere\NoDriver.json'
$env:STRATA_ERROR_DIALOG_FILE = "$PWD\dialog.txt"
(Start-Process .\StrataEditor.exe -ArgumentList '--windowed' -Wait -PassThru).ExitCode
Remove-Item Env:VK_DRIVER_FILES, Env:VK_ICD_FILENAMES, Env:STRATA_ERROR_DIALOG_FILE
```

`Start-Process` starts the editor as the desktop does, with no standard streams. `-Wait` waits for its end, and
`-PassThru` returns the process, whose `ExitCode` PowerShell prints. The last line removes the three variables again.
:::
:::tab[Linux]

```sh
VK_DRIVER_FILES=/nowhere/NoDriver.json VK_ICD_FILENAMES=/nowhere/NoDriver.json STRATA_ERROR_DIALOG_FILE=dialog.txt StrataEditor --windowed 2>/dev/null
echo $?
```

`2>/dev/null` sends standard error to the null device, and `echo $?` prints the exit code.

:::
:::tab[macOS]

```sh
VK_DRIVER_FILES=/nowhere/NoDriver.json VK_ICD_FILENAMES=/nowhere/NoDriver.json STRATA_ERROR_DIALOG_FILE=dialog.txt StrataEditor --windowed 2>/dev/null
echo $?
```

`2>/dev/null` sends standard error to the null device, and `echo $?` prints the exit code.

:::
::::

The run is Interactive, since `--windowed` is not a scripted option, and its standard error reaches no reader: the null device, or no stream at all. So the dialog is allowed.

Graphics is the first module, and its `OnInit` fails because no device is found: it stores a `Problem` ("Strata Editor cannot start: no usable graphics device was found (it needs Vulkan 1.2 or later).") and an `Advice` about installing a driver. No module had started, so the constructor clears the layers, stops the job system, closes the window and reports. The shell prints 1.

The file has this shape.

```text
Strata Editor
Strata Editor cannot start: no usable graphics device was found (it needs Vulkan 1.2 or later).

<the advice of the graphics device>

The log has the details: <the user data folder>/Logs/StrataEditor.log
```

The first line is the title, which is the application's `Name`. The advice and the path depend on the system.

## A toy version

The toy does the job of the start in 120 lines, with no window and no modules: only steps with names. It has the same shape as the real start. A function reads the command line and returns a launch or nothing. The launch's `Create` makes the application, and the constructor starts the steps in order and ends them in reverse when one fails. `main` runs four command lines and prints the exit code of each.

Watch the second run. The audio step fails, and the lines before the exit code show what the constructor ended and in which order.

```cpp sketch="core-first-frame-toy.cpp"
// A toy program start: a launch made before the application, startup steps that unwind, a loop and the exit codes.
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace
{
	struct Step
	{
		std::string Name;
		bool Works = true;
	};

	class Application
	{
	public:
		Application(const std::vector<Step>& steps, int maxFrames)
			: m_MaxFrames(maxFrames)
		{
			for (const Step& step : steps)
			{
				if (!step.Works)
				{
					std::printf("  %s failed\n", step.Name.c_str());
					Unwind();
					m_ExitCode = 1;
					return;
				}
				std::printf("  started %s\n", step.Name.c_str());
				m_Started.push_back(step.Name);
			}
			m_Running = true;
		}

		~Application() { Unwind(); }

		void Run()
		{
			for (int frame = 1; m_Running && frame <= m_MaxFrames; frame++)
				std::printf("  frame %d\n", frame);
		}

		int GetExitCode() const { return m_ExitCode; }
	private:
		void Unwind()
		{
			for (; !m_Started.empty(); m_Started.pop_back())
				std::printf("  stopped %s\n", m_Started.back().c_str());
		}
	private:
		std::vector<std::string> m_Started;
		int m_MaxFrames;
		bool m_Running = false;
		int m_ExitCode = 0;
	};

	struct Launch
	{
		std::function<std::unique_ptr<Application>()> Create;
	};

	int s_StartupExitCode = 1;

	// Reads the command line. Nothing to run: no launch, and the exit code the process ends with.
	std::optional<Launch> CreateApplication(const std::vector<std::string>& arguments)
	{
		bool audioWorks = true;
		int frames = 0;
		for (size_t index = 0; index < arguments.size(); index++)
		{
			if (arguments[index] == "--help")
			{
				std::printf("  usage: toy [--fail-audio] [--frames <count>]\n");
				s_StartupExitCode = 0;
				return std::nullopt;
			}
			if (arguments[index] == "--fail-audio")
				audioWorks = false;
			else if (arguments[index] == "--frames" && index + 1 < arguments.size())
				frames = std::atoi(arguments[++index].c_str());
			else
			{
				std::printf("  unknown argument '%s'\n", arguments[index].c_str());
				s_StartupExitCode = 3;
				return std::nullopt;
			}
		}
		const std::vector<Step> steps = { { "jobs" }, { "window" }, { "audio", audioWorks }, { "project" } };
		return Launch { [steps, frames]() { return std::make_unique<Application>(steps, frames); } };
	}

	int RunProgram(const std::vector<std::string>& arguments)
	{
		std::optional<Launch> launch = CreateApplication(arguments);
		if (!launch)
			return s_StartupExitCode;
		std::unique_ptr<Application> application = launch->Create();
		application->Run();
		return application->GetExitCode();
	}
}

int main()
{
	const std::vector<std::vector<std::string>> runs = { { "--frames", "2" }, { "--fail-audio" }, { "--help" }, { "--bogus" } };
	for (const std::vector<std::string>& arguments : runs)
	{
		std::printf("toy");
		for (const std::string& argument : arguments)
			std::printf(" %s", argument.c_str());
		std::printf("\n");
		s_StartupExitCode = 1;
		const int exitCode = RunProgram(arguments);
		std::printf("  exit code %d\n", exitCode);
	}
}
```

```text output-of="core-first-frame-toy.cpp"
toy --frames 2
  started jobs
  started window
  started audio
  started project
  frame 1
  frame 2
  stopped project
  stopped audio
  stopped window
  stopped jobs
  exit code 0
toy --fail-audio
  started jobs
  started window
  audio failed
  stopped window
  stopped jobs
  exit code 1
toy --help
  usage: toy [--fail-audio] [--frames <count>]
  exit code 0
toy --bogus
  unknown argument '--bogus'
  exit code 3
```

1. **Line 24:** the constructor starts the steps in order and remembers the names of those that started; the real constructor keeps a count of the started modules instead.
2. **Lines 26–31:** a step that fails ends the ones before it, in reverse, and sets the exit code 1.
3. **Line 39:** the destructor ends what is left. After a failed start nothing is left, so the real destructor can run on every path.
4. **Lines 85–89:** a command line that the program cannot run returns an empty optional and stores the exit code, as the editor does with 3 for a mistake. Help does the same with 0, in lines 75–79.
5. **Line 93:** a launch holds a function, so that nothing is built before the code that must come first has run.

The first run starts the four steps, runs two frames, stops the steps in reverse and returns 0. The second run stops at `audio`: it ends `window` and `jobs`, in that order, and returns 1. The third and fourth runs never build an application. What the toy omits is what makes the real start hard. The real start has a window that can fail before the modules, modules that depend on each other, the job system, and a report to a person that comes after the modules end.

## The real code

The real start has the toy's shape. Read `main` first. Search for the three early returns, and for the one line that makes the application: it is the only call that can fail after the registration.

```cpp src="Strata/src/Strata/Engine/EntryPoint.h#L16-L41"
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
	const int exitCode = application->GetExitCode();
	application.reset();

	Strata::Log::Shutdown();
	return exitCode;
}
```

1. **Line 21:** the kind of run is decided and the streams are connected before anything prints.
2. **Line 23:** from here on, Ctrl+C asks the loop to quit and does not kill the process.
3. **Lines 25–27:** no launch, or a launch without a `Create` function, ends the process with the stored startup code. No application exists yet.
4. **Line 30:** the composition root runs before `Create`, so the application and its modules find every registry ready.
5. **Lines 32–40:** an application that cannot be made ends with the startup code. One that can is run, its code is read and it is destroyed; only then does the log shut down, so that the destructor's lines are written.

The constructor comes next. Follow the order of the steps, and search for the place where a failure is noticed and the place where it is acted on.

```cpp src="Strata/src/Strata/Core/Application.cpp#L64-L112"
Application::Application(const ApplicationSpecification& specification)
	: m_Specification(specification), m_FramePacer(specification.MaxFrameRate)
{
	ST_CORE_VERIFY(!s_Instance, "Only one Application may exist at a time");
	s_Instance = this;

	// Editors and games are interactive: they keep their speed while another window has the focus (Platform.h).
	if (!Platform::DisableExecutionSpeedThrottling())
		ST_CORE_WARN("The system did not exempt the process from power throttling: it may run slower while its windows are in the background");

	if (!m_Specification.WorkingDirectory.empty())
	{
		std::error_code error;
		std::filesystem::current_path(m_Specification.WorkingDirectory, error);
		if (error)
			ST_CORE_ERROR("Failed to set working directory to '{}': {}", FileSystem::ToUTF8(m_Specification.WorkingDirectory), error.message());
	}

	JobSystem::Init(m_Specification.Jobs);

	bool windowOpened = true;
	if (!m_Specification.Headless)
	{
		WindowSpecification windowSpecification = m_Specification.Window;
		if (windowSpecification.Title.empty())
			windowSpecification.Title = m_Specification.Name;
		m_Window = m_Specification.WindowFactory ? m_Specification.WindowFactory(windowSpecification) : Window::Create(windowSpecification);
		if (m_Window)
		{
			m_Window->SetEventCallback(ST_BIND_EVENT_FN(OnEvent));
			Input::SetWindow(m_Window.get());
		}
		else
		{
			// The window backend logged why (GLFW's error, or a build without a window backend).
			ReportFatalError(m_Specification.Name, fmt::format("{} cannot start: its window could not be opened.", m_Specification.Name),
				"It needs a desktop session with a display; to run without a window, start it with --headless.");
			windowOpened = false;
		}
	}
	// Also after a failed start: tests run several applications in one process.
	Input::Reset();

	if (!windowOpened || !StartModules())
	{
		m_Running = false;
		m_ExitCode = 1;
	}
}
```

1. **Line 67:** the check of the one-application rule stays in shipping builds, and the pointer is claimed on the next line.
2. **Line 82:** the job system starts with the sizes of `Jobs`, after the step that moves to `WorkingDirectory` and before the window and the modules.
3. **Lines 90–102:** the window comes from the factory or from `Window::Create`; a null result is reported at once, and `windowOpened` remembers it.
4. **Line 105:** the input state is reset on every path, also after a failed start.
5. **Lines 107–111:** a failed window or a failed module start stops the application with the exit code 1. The short-circuit in line 107 means that no module is made after a window failure.

The toy kept the names of the steps it had started. The real constructor cannot: modules are objects, made together and put in dependency order before the first one starts, so it keeps a count of how many have started (`m_StartedModules`). The toy also reported nothing; the real one reports a window failure itself and leaves the module failures to `StartModules`, which comes next.

```cpp src="Strata/src/Strata/Core/Application.cpp#L126-L160"
bool Application::StartModules()
{
	std::string error;
	if (!m_Modules.Create(m_Specification.Modules, &error))
	{
		Input::SetWindow(nullptr);
		m_Window.reset();
		ReportFatalError(m_Specification.Name, fmt::format("{} cannot start: {}.", m_Specification.Name, error));
		return false;
	}

	EngineContext context { *this, m_Window.get(), m_Modules };
	for (EngineModule* module : m_Modules.GetAll())
	{
		if (module->OnInit(context))
		{
			m_StartedModules++;
			continue;
		}
		ST_CORE_CRITICAL("Engine module '{}' could not start; the application cannot run", module->GetName());
		// The person learns what the module describes once nothing of the program is left on the screen: the modules that
		// started end in their usual order, then the window, which would never show anything, closes. The layers those
		// modules pushed (ImGui's overlay) go first, as in ~Application, so that no layer outlives what it uses; the
		// program's own layers do not exist yet.
		const EngineModuleStartFailure failure = module->GetStartFailure();
		m_LayerStack.Clear();
		ShutDownModules();
		Input::SetWindow(nullptr);
		m_Window.reset();
		if (!failure.Problem.empty())
			ReportFatalError(m_Specification.Name, failure.Problem, failure.Advice);
		return false;
	}
	return true;
}
```

1. **Lines 129–135:** making the modules orders them; if that fails, no module has started, so only the window closes, and the error names the modules.
2. **Lines 138–143:** each module starts in order, and a success is counted. The count is what every later hook and the end of the run use.
3. **Lines 150–154:** the module's description of its failure is read first. Then the layers go, the started modules end in reverse, the job system stops and the window closes.
4. **Lines 155–157:** the report comes last, and only when the module wrote a `Problem`; with an empty one the critical line of line 145 is all there is.

The report itself is a small function. Look at the order of its four decisions.

```cpp src="Strata/src/Strata/Core/Application.cpp#L42-L62"
void Application::ReportFatalError(std::string_view title, std::string_view problem, std::string_view advice)
{
	ST_CORE_CRITICAL("{}{}{}", problem, advice.empty() ? "" : " ", advice);
	if (!Platform::ShouldShowErrorDialogs())
		return;
	std::string message(problem);
	if (!advice.empty())
		message += fmt::format("\n\n{}", advice);
	if (const std::filesystem::path logFile = Log::GetLogFile(); !logFile.empty())
		message += fmt::format("\n\nThe log has the details: {}", FileSystem::ToUTF8(logFile));
	Log::Flush();
	// Tests read what the dialog would say instead of a dialog nobody could dismiss.
	if (const std::optional<std::string> file = Platform::GetEnvVar("STRATA_ERROR_DIALOG_FILE"); file && !file->empty())
	{
		if (!FileSystem::WriteText(FileSystem::FromUTF8(*file), fmt::format("{}\n{}\n", title, message)))
			ST_CORE_ERROR("Cannot write the error dialog's text to '{}'", *file);
		return;
	}
	if (!Platform::ShowErrorDialog(title, message))
		ST_CORE_WARN("No dialog could show the error: it is only in the log");
}
```

1. **Line 44:** the log gets the problem first, in every kind of run.
2. **Lines 45–46:** a Console run, or any run whose output someone reads, stops here.
3. **Lines 50–52:** the log file's path is added, and the log is flushed so that the file already holds the details when the person reads the dialog.
4. **Lines 54–59:** a test names a file in `STRATA_ERROR_DIALOG_FILE`; the title and message go there and the function returns, so no dialog blocks the test.
5. **Lines 60–61:** the dialog blocks until dismissed; if no program could show one, a warning says that the log is all there is.

The last piece is the program's side: the editor fills the specification from its command line. The `--no-gpu` of the example and of an exercise below is in these lines.

```cpp src="StrataEditor/src/EditorApplication.cpp#L384-L398"
ApplicationSpecification specification;
specification.Name = "Strata Editor";
specification.CommandLineArgs = commandLine;
// --no-gpu: automation that needs no rendering (export, asset processing) on machines without a GPU.
const bool graphics = !commandLine.HasFlag("--no-gpu");
specification.Headless = commandLine.HasFlag("--headless") || !graphics;
// Without a window there is no vsync: a headless editor waiting for automation would otherwise spin a CPU core,
// and playing scenes advance about as they would in a 60 Hz game.
if (specification.Headless)
	specification.MaxFrameRate = c_HeadlessFrameRate;
// The modules: the device (offscreen when headless, for captures and thumbnails), sound (mixed without a device when
// headless), the UI in a window, the project.
if (graphics)
	specification.Modules.push_back(GraphicsModule::Factory());
specification.Modules.push_back(AudioModule::Factory({ .NullDevice = specification.Headless }));
```

1. **Line 388:** `graphics` is false only for `--no-gpu`.
2. **Line 389:** `Headless` is true for either option.
3. **Lines 392–393:** a headless program has no display to pace it, so its rate is capped at 60 frames a second.
4. **Lines 396–398:** Graphics is in the list only when there is a device, and Audio always is, with a null device when the program is headless.

The lines after these add the ImGui module when the program has a window and then the project module, as the table above says.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Each program writes its start calls in `main` | Small programs, and most introductions to a graphics library | Every call is visible in one place, and nothing starts by surprise | The list and the cleanup repeated in every program, and a start that each program ends by hand, and differently |
| Managers with start-up and shut-down calls, kept in global objects | The engine architecture that Jason Gregory describes in his book | Simple code, since any code reaches any manager | An order that only the programmer knows, a test that cannot make a second copy, and no way to report why a start failed |
| Services that register themselves from static constructors | Plug-in systems built on global objects | A program that lists nothing; linking a file is enough | An order that C++ does not define between files, and failures that no person can be told about before `main` |
| A failing step ends the process on the spot with an exit call | Quick tools | The shortest code for a failure | Local objects that never end, a log that is not flushed, and a dialog that appears over a window that is still open |

## How it is tested

The start is tested at three levels: the functions in a unit test, an application with test modules, and the built programs themselves.

- `Core` (`StrataTests/src/Core/CoreTests.cpp`): the cases `CommandLine parses flags and options`, `CommandLineOptions find what a program does not understand and format its usage` and `CommandLine parses sizes written width x height` check the forms of an option and a size. They also check the messages for a bad command line, the usage text and the exit code 3.
- `Core.EngineModules` (`EngineModuleTests.cpp`): `A module that cannot start ends the program, and only the modules that started end` checks that the journal holds `Init A`, `Init B` and the end of A, with no `Stop`, and that the exit code is 1. `A program whose modules cannot be ordered does not start, and the message names them` checks the error texts and that no module started.
- `EndToEnd.StandardStreams` (`StrataTests/src/Editor/StandardStreamsProcessTests.cpp`): runs the built editor and runtime with their output read or discarded, and checks the exit code, the dialog file and that a Console run never shows a dialog. `GPU.Startup` runs the editor without a driver, as in the example.
- `StrataRuntime.Arguments.Help` and `StrataRuntime.Arguments.Unknown` (`StrataTests/CMakeLists.txt`): the runtime's `--help` prints its usage, and `--bogus` prints `Unknown argument '--bogus'` and ends with 3.

Run the first two groups with `build/windows/bin/Debug/StrataTests.exe --test-suite=Core*`. The end-to-end suite needs the built programs next to the tests.

## Changing it safely

A new thing the program needs before its first frame is almost always an engine module, not a new line in the constructor. The constructor knows no module, on purpose, and a list in the program's specification keeps it that way. Give the module an `OnInit` that returns false when it cannot start, let it clean up what it began, and fill `GetStartFailure` so that the person learns why. [Engine modules](engine-modules.md) shows the hooks.

A new step in the constructor itself must fail in a way that the rest of the constructor can see, must have a place in the table of failures, and must have a test. Copy the case that makes a module fail, and check the journal of hooks, the exit code and the log.

:::rule[Application never names a module]
`Application` calls nothing of the engine except through the module list that the program gives it, and other code finds a module with `GetModules().Find<T>()`. The rule keeps the start independent of the modules: a test application needs no graphics device to fail, and a new module needs no change in the constructor. [Engine modules](engine-modules.md) teaches it.
:::

Before you commit a change to the start, run the `Core*` suites, the end-to-end suite and `ctest --preset <platform>-debug -LE gpu`.

## Summary

- A Strata program runs one `main`. It decides Console or Interactive, connects the streams, installs the interrupt handler and asks the program for a launch. Then it runs the composition root, makes the application, runs it and returns its exit code.
- `ApplicationSpecification` says what the program is; the editor sets `Headless` for `--headless`, and for `--no-gpu`, which also drops the Graphics module.
- The constructor starts the job system, the window, the input and the modules in that order; a failure ends only what started, in reverse, and then `ReportFatalError` tells the person.
- The exit codes are 0, 1, 3 and 130, with the programs' own codes beside them.
- A new startup step is a module that can fail, with a `Problem` and an `Advice`, and a test that checks how the started parts end.

## Check yourself

1. Put these calls in the order in which they run: `RegisterBuiltinModules`, `InstallInterruptHandler`, the `Application` constructor, `GetProgramRun`, `Run`, `CreateApplication`, `ConnectStandardStreams`.

   :::answer{tests="trace-start"}
   `GetProgramRun`, `ConnectStandardStreams`, `InstallInterruptHandler`, `CreateApplication`, `RegisterBuiltinModules`, the constructor (called through `Create`) and `Run`. The kind of run must be known before the streams are connected, and the registries must be ready before the application, its layers or its modules use them.
   :::

2. The editor starts with `--no-gpu`. Which statement is right? (a) Only the window is omitted. (b) `Headless` becomes true, the Graphics module is not in the list, and the Audio module gets a null device. (c) `Headless` stays false until `--headless` is also given.

   :::answer{tests="specification"}
   (b) is right. `--no-gpu` makes `graphics` false and `Headless` is true for `--headless` or for no graphics. Graphics is not added, the ImGui module is not added either since the run is headless, and Audio gets its null device. (a) is wrong: the device goes too. (c) is wrong: the option implies `--headless`.
   :::

3. A program lists modules A, B and C. B's `OnInit` returns false with a `Problem`. Which hooks run on A, B and C, in what order does the person learn of the problem, and what is the exit code?

   :::answer{tests="unwinding"}
   A gets `OnInit`, then `OnRelease` and `OnShutdown`, but no `OnStop`. B gets only its `OnInit`, and C gets nothing. The layers go first, the job system stops between `OnRelease` and `OnShutdown`, the window closes, and only then does the report show B's `Problem`. The exit code is 1.
   :::

4. What are the exit codes of `StrataEditor --frames 0`, of `StrataEditor --version`, and of a windowed editor that the person closes?

   :::answer{tests="exit-codes"}
   3, 0 and 0. The value check refuses 0 frames (`--frames expects a positive number of frames`), prints the problem and the usage, and stores the usage code. `--version` prints the version and stores 0. A closed window ends the loop with the code that nobody changed, 0.
   :::

5. You add a module whose `OnInit` returns false when a file is missing. A test application starts it. What three things must be true afterwards, and why does the test not find a dialog file?

   :::answer{tests="failing-step,unwinding"}
   The modules before it ended in reverse (the journal shows `Release` and `Shutdown` but no `Stop`), the exit code is 1, and the log holds the module's problem once. No dialog file exists because the test program is a Console run (it connects its streams as one), so `ReportFatalError` writes to the log and returns before it reaches the file.
   :::

## Exercises

1. **Basic.** Predict the exit codes of these four runs of the editor, then run them: `StrataEditor --help`, `StrataEditor` with an option it does not have, `StrataEditor --headless --frames 10`, and `StrataEditor --headless` stopped with Ctrl+C. Read each code with `echo $?` on Linux and macOS. In Windows PowerShell, end each line with `| Out-Host` and read `$LASTEXITCODE` after it, as in the example above.

   :::answer[Worked solution]{tests="exit-codes"}
   The codes are 0, 3, 0 and 130. `--help` prints the usage and stores 0. An option that is not in the table sends the problem and the usage to standard error, with 3. The third run stops after 10 frames with the code that nobody changed, 0, on a computer with a Vulkan driver; add `--no-gpu` when there is none. The fourth runs until Ctrl+C: the frame loop sees the interrupt, logs a warning and returns 130, because the code was still 0.

   Windows PowerShell differs in two runs. With `| Out-Host` the unknown option shows its exit code 3 but not its message; `2>&1 | Out-Host` shows the message too, as a PowerShell error. Ctrl+C makes PowerShell end the editor itself, so the warning never comes and `$LASTEXITCODE` reads -1. The engine's test `On Windows Ctrl+C in the terminal ends a headless editor in order` passes the key to the editor as a console does, and gets 130.
   :::

2. **Medium.** Trace it yourself. Follow `--no-gpu` from its line in the usage to `Headless`, to the null audio device and to the Graphics module that the editor omits. Name the file, the function and the lines.

   :::answer[Worked solution]{tests="specification,trace-start"}
   The usage line is the `--no-gpu` entry of `c_Arguments` in `StrataEditor/src/EditorApplication.cpp`. `GetProgramRun` lists it among the scripted options. In `CreateApplication`, `graphics` is `!commandLine.HasFlag("--no-gpu")`, and `specification.Headless` is true for `--headless` or when `graphics` is false. `AudioModule::Factory` receives `.NullDevice = specification.Headless`. The editor adds `GraphicsModule::Factory()` only `if (graphics)`, and the ImGui factory only `if (!specification.Headless)`, so it runs Audio and Project.
   :::

3. **Medium.** Change the toy so that a failed step reports a problem and advice, and so that the report is made after the steps end. Print what the dialog would show, then check the order of the lines.

   :::answer[Worked solution]{tests="unwinding"}
   Each step gets two texts, and the failure path first ends the started steps and then calls a function that prints the report, as `ReportFatalError` does. In the output, the `stopped` lines come before the report line.

   ```cpp sketch="core-first-frame-report.cpp"
   // The toy start with a failure that tells the person why: the started steps end first, then the report is made.
   #include <cstdio>
   #include <string>
   #include <vector>

   namespace
   {
   	struct Step
   	{
   		std::string Name;
   		bool Works = true;
   		std::string Problem; // What the person reads when this step fails
   		std::string Advice;
   	};

   	// The engine writes the message so: the problem, a blank line, the advice. The toy prints it instead of showing a dialog.
   	void ReportFatalError(const std::string& title, const std::string& problem, const std::string& advice)
   	{
   		std::printf("  dialog titled '%s': %s", title.c_str(), problem.c_str());
   		if (!advice.empty())
   			std::printf(" | %s", advice.c_str());
   		std::printf("\n");
   	}

   	// Starts the steps in order. A step that fails ends the ones before it, in reverse, and only then is the report made.
   	int StartProgram(const std::string& name, const std::vector<Step>& steps)
   	{
   		std::vector<std::string> started;
   		for (const Step& step : steps)
   		{
   			if (step.Works)
   			{
   				std::printf("  started %s\n", step.Name.c_str());
   				started.push_back(step.Name);
   				continue;
   			}
   			std::printf("  %s failed\n", step.Name.c_str());
   			for (size_t index = started.size(); index > 0; index--)
   				std::printf("  stopped %s\n", started[index - 1].c_str());
   			ReportFatalError(name, step.Problem, step.Advice);
   			return 1;
   		}
   		return 0;
   	}
   }

   int main()
   {
   	const std::vector<Step> steps = { { "jobs", true, "", "" }, { "window", true, "", "" },
   		{ "audio", false, "Toy cannot start: no sound device was found.", "Plug in speakers or start it with --no-audio." }, { "project", true, "", "" } };
   	const int exitCode = StartProgram("Toy", steps);
   	std::printf("  exit code %d\n", exitCode);
   }
   ```

   ```text output-of="core-first-frame-report.cpp"
     started jobs
     started window
     audio failed
     stopped window
     stopped jobs
     dialog titled 'Toy': Toy cannot start: no sound device was found. | Plug in speakers or start it with --no-audio.
     exit code 1
   ```

   1. **Lines 17–22:** the report function prints what the dialog would show: the title, the problem and the advice.
   2. **Lines 37–41:** the failing step first ends the started ones in reverse, then makes the report, then returns the exit code 1.
   :::

4. **Hard.** On the source build, write a test in `StrataTests/src/Core/EngineModuleTests.cpp` that starts an application whose second module fails, with a `Problem` and an `Advice`. Check the journal, the exit code and the log. Then say how you would read the dialog text.

   :::answer[Worked solution]{tests="failing-step,unwinding"}
   Copy the case "A module that cannot start ends the program, and only the modules that started end". Give the second `MakeModule` the behavior `{ .FailInit = true, .StartFailureProblem = "..." }` and build a `JournalApplication` from `MakeSpecification`. Check three things. The journal holds the `Init` lines, the end of the first module and no `Stop`; `GetExitCode()` is 1; and `Tests::CountLogMessages` finds the problem once.

   The helper module in that file passes only a `Problem`, so add an `Advice` field to its behavior if you want to check both. The test cannot read a dialog, since the test program is a Console run. To read the text, run a built program as in the example, with `STRATA_ERROR_DIALOG_FILE` set and its output discarded. Run `build/windows/bin/Debug/StrataTests.exe --test-suite=Core.EngineModules`, then break the reverse order of the ending on purpose and watch the test fail.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Engine/EntryPoint.h`: `main`. `Strata/src/Strata/Engine/ApplicationLaunch.h`: `ApplicationLaunch`, `GetProgramRun` and `CreateApplication`.
- `Strata/src/Strata/Core/Application.h` and `Application.cpp`: `ApplicationSpecification`, the constructor, `StartModules`, `ShutDownModules`, `ReportFatalError`, `SetStartupExitCode`, `c_InterruptedExitCode`.
- `Strata/src/Strata/Core/CommandLine.h`, `CommandLineOptions.h`: the command line, its options and `c_UsageExitCode`.
- `Strata/src/Strata/Core/Platform.h`: `ProgramRun`, `ConnectStandardStreams`, `InstallInterruptHandler`, `ShouldShowErrorDialogs`, `ShowErrorDialog`.
- `StrataEditor/src/EditorApplication.cpp`: the editor's `GetProgramRun`, `CreateApplication` and options.
- Tests: `StrataTests/src/Core/CoreTests.cpp`, `EngineModuleTests.cpp`, `StrataTests/src/Editor/StandardStreamsProcessTests.cpp`.
- Environment variable: `STRATA_ERROR_DIALOG_FILE`.

## Further reading

- [Robert Nystrom, "Singleton", in Game Programming Patterns](https://gameprogrammingpatterns.com/singleton.html): why a global object that anyone can reach is risky; beginner.
- [cppreference, "Static Initialization Order Fiasco"](https://en.cppreference.com/w/cpp/language/siof): why the order of static constructors across files cannot be trusted; intermediate.
- Jason Gregory, *Game Engine Architecture*, the section on start-up and shut-down of engine subsystems: the manager-and-singleton way that Strata's list of modules replaces; intermediate.
