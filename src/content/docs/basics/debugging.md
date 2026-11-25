---
id: basics/debugging
title: "Finding bugs: a method, the log and the debugger"
description: "A six-step method for finding bugs, the Console as a tool, and a debugger attached to the editor with breakpoints, stepping and the call stack."
kind: primer
size: L
tracks: [G, B, E]
needs: [basics/programming-3]
time: 90
learn:
  - id: method
    text: explain the six steps of a method that finds a bug, and why each one changes one thing only
  - id: log
    text: write log lines that show the values a bug depends on, without flooding the Console
  - id: attach
    text: run a debugger attached to the editor and stop on a line of a script
  - id: stepping
    text: set a breakpoint with a condition, and step over, into and out of calls while you watch a variable
  - id: call-stack
    text: name the frames of a call stack and the function that called each one
status: final
---

::::test-out

1. A cube turns too slowly. Write the first three steps of the method, in order, before you change any code.

   :::answer{tests="method"}
   Make the bug happen again, look at what really happens, and guess one cause. Changing code comes after the guess, as
   one change that tests it.
   :::

2. What does the line `Log::Info("angle ", 0.5f, " ok ", true);` write after the time and the name `Script`?

   :::answer{tests="log"}
   `angle 0.5 ok true`. `Log` joins the pieces in order with nothing added, and a `bool` prints as a word.
   :::

3. A breakpoint stands on the line `m_Counter = m_Counter + 1;` and `m_Counter` holds 4. What does a watch show when the
   program stops, and what after one step over?

   :::answer{tests="stepping"}
   4, then 5. The program stops before the line runs, and a step over runs that one line.
   :::

4. The call stack shows three frames, newest first: `ToRadians`, `TurnAngle`, `OnUpdate`. Which function runs now, and
   which function called `TurnAngle`?

   :::answer{tests="call-stack"}
   `ToRadians` runs now, at the top. `OnUpdate` called `TurnAngle`, because each frame below the top is the caller of the
   frame above it.
   :::

5. You attached the debugger to the editor, but a breakpoint in your script never binds. Which folder do you add to the
   debugger's symbol search path?

   :::answer{tests="attach"}
   The folder `.strata/Scripts/Bin` of your project, where the module's program database stays.
   :::

::::

## Why you will need this

Every script you write will fail to do what you meant at least once. This page gives you a way to learn why, from the
first symptom to the changed line, and the two tools that show you what the program does: the Console and a debugger.

Three later pages use it. [Play, test and debug](../make/play-test-debug.md) debugs a Coin Run script while the game
plays. [Debugging the engine](../core/debugging.md) applies the same ideas to the engine's own code. [Crash containment](../scripting/crash-containment.md) shows what the editor does with a script that crashes. At the end of this page you
plant a bug in a coin's spin and find it.

## A bug is a gap between what you meant and what happens

A **bug** is a mistake in a program that makes it do something other than what its maker meant. The program still builds
and runs, so no message tells you where the mistake is. That differs from a build error, where the compiler names a line,
and from a crash, where the editor reports the place.

**Debugging** is finding the cause of a bug and fixing it. The work is a search: the program has thousands of lines, the
mistake sits in one of them, and a good search discards most lines quickly. Guessing and changing lines until the symptom
goes away fails, because a change can hide a bug without removing it, or add a second one.

## Six steps find a bug

Professional programmers follow a fixed order. Each step answers one question, and the order keeps you from changing
code before you know what is wrong.

```mermaid caption="The six steps. When the check fails, the guess was wrong, so you return to looking at what really happens." alt="A flow of six boxes: make it happen again, observe, guess one cause, test with one change, fix, check. An arrow leads from the check back to the observe box when the bug remains."
flowchart LR
    A["1 Make it happen again"] --> B["2 Observe"]
    B --> C["3 Guess one cause"]
    C --> D["4 Test with one change"]
    D --> E["5 Fix"]
    E --> F["6 Check, and keep the check"]
    F -- "bug remains" --> B
```

1. **Make the bug happen again.** Find the exact steps that show it: which scene, which button, which values. A bug you
   cannot repeat you cannot test a guess on.
2. **Observe what really happens.** Read the numbers the program uses, with log lines or a debugger. Do not trust what
   you believe the code does; the program does what the code says.
3. **Guess one cause.** Write the guess as a sentence that the next step can prove wrong: "the count grows twice as fast
   as the clock".
4. **Test the guess with one change.** Change one thing, or look at one more value, and predict the result before you
   run. If the result differs from the prediction, the guess was wrong; return to step 2.
5. **Fix it.** When a test confirms the guess, write the real fix, which can differ from the test.
6. **Check, and keep the check.** Repeat step 1's steps and confirm that the bug has disappeared. Then keep the check as a
   short note, a command script or a test, so that the bug cannot return unseen.

The rule behind steps 3 and 4 is one cause and one change. With two changes at once, a result that improves tells you
nothing about which change helped.

:::example[A message that comes early]
A `Playground` script should write `Time is up` after 3 seconds of play. The Console shows the line after about 1.5
seconds, counted with a clock. The script adds the frame's time to a field and compares it with a limit:

```cpp pseudocode
m_Time += deltaTime * 2.0f;
if (m_Time > 3.0f)
	Log::Info("Playground.OnUpdate: Time is up");
```

Step 1: play again; the line comes at 1.5 seconds every time, so the bug repeats. Step 2: add `Log::Info("m_Time ", m_Time)`
below the first line. At 60 frames per second one frame lasts 1 / 60 = 0.0167 seconds, so you expect 0.017, 0.033 and
0.050 in the first three frames. The Console shows 0.033, 0.067 and 0.100.

Step 3: the field grows twice as fast as the clock, perhaps because of a factor 2. Step 4: remove the `* 2.0f`
and predict 0.017, 0.033 and 0.050; the Console shows exactly those. Step 5 needs nothing more, since the test was already
the fix. Step 6: play, count 3 seconds by the clock, and see the line arrive, then delete the observing log line.
:::

Try it: the same script writes `Time is up` after 6 seconds, not 3. Which factor in the line would you guess, and which
numbers in the log would confirm it?

:::answer
A factor of 0.5: `deltaTime * 0.5f`, which makes the field grow half as fast as the clock. The log would show 0.008,
0.017 and 0.025 in the first three frames, half of the expected 0.017, 0.033 and 0.050.
:::

## The log shows what happens while the program runs

The cheapest way to observe is to ask the program to say what it does. A script writes a line with `Log`, a class of the
script library that sends text to the engine's log, and the **Console** panel shows the log. You met `Log::Info` in
[Programming from zero I](../basics/programming-1.md); here it becomes a tool.

`Log` has four functions, one for each level of importance. Pick the level by what the line means, because the Console
lets you hide levels you do not need.

| Function | Use it for | Shown in the Console |
| --- | --- | --- |
| `Log::Trace` | Detail you want only while hunting one bug | Hidden until you tick **Trace** |
| `Log::Info` | Normal progress: a level loaded, a coin collected | Shown |
| `Log::Warn` | Something wrong that the script survives | Shown, in the warning color |
| `Log::Error` | Something that failed | Shown, in the error color |

The Console has one box for each level (**Trace**, **Info**, **Warnings**, **Errors**), a **Search** field that keeps
only the lines holding your text, and a **Clear** button. A line starts with the time in seconds and the name `Script`,
then your text. Put the values that matter into the text, and put the place there too:
`Log::Info("Coin.OnUpdate: angle ", angle)`. A script's own line carries no file and line, so the class and the callback
in the text are how you find the line again with **Search**. Only :term[compiler errors]{id=compile-error} and crash reports in the Console carry
a file and a line, and clicking such a line opens the code.

A log line helps when it shows a value at the moment it goes wrong. Three habits make that work:

- Write the name and the value together: `"speed ", speed`, never the value alone.
- Log once per event, not once per frame: inside an `if` that fires when something changes.
- Remove the line when you have fixed the bug, or lower it to `Log::Trace`.

:::example[A line in every frame floods the Console]
`OnUpdate` runs every frame. At 60 frames per second, one `Log::Info` there writes 60 lines per second. The Console keeps
the last 4,096 lines, so it holds 4,096 / 60 = 68 seconds of them, and then it drops the oldest line for each new one.

A script on the five coins of Coin Run writes 5 × 60 = 300 lines per second, and the Console holds only the last
4,096 / 300 = 13.7 seconds. The line you wanted from 20 seconds ago has gone from the Console. The log file keeps every
line of the editor's run: the file is `StrataEditor.log`, in the `Logs` folder where the editor keeps your user data.
:::

Try it: a script on one cube logs two lines in every frame at 50 frames per second. How long until the Console drops a
line?

:::answer
2 lines × 50 frames = 100 lines per second, so 4,096 / 100 = 41 seconds. After that, each new line pushes out the
oldest one.
:::

## A debugger stops a running program and shows its variables

A log shows only what you decided to print before you ran. To see any value at any moment, you need a program that
stops the game and shows you the inside. First, what the debugger stops.

A **process** is a running program: the system loads the program's file, gives it its own memory and starts it. The
editor is one process, named `StrataEditor`. The engine, the panels and the script modules the editor loads all run in
that process, so one process holds your script's variables. [Computers](../basics/computer.md) explains processes in full.

A **debugger** is a program that controls another program: it stops it where you ask, shows its variables and lets
it continue step by step. Visual Studio and Visual Studio Code both contain one. While the debugger holds the editor stopped,
the window does not draw or answer input, because the whole editor is one process. Press **Continue** and it runs on.

When a program does something forbidden, such as reading memory that is not its own, the system stops it. That is a
**crash**, the end of a program, or of a script module in Strata's case, caused by an error it cannot continue from.
Strata contains a crash in a script: it stops Play and reports the place, as [Your first script](../make/first-script.md)
shows. A debugger also helps with bugs that do not crash.

## Debug information names the files, lines and variables

A program in memory is machine instructions and numbers. The compiler throws away the names of your files, lines and
variables, because the processor does not need them. A debugger needs them, so the build writes them beside the program as
**debug information**: tables that map instruction addresses to file and line, and memory to variable names and types.
Debuggers call these names the program's symbols.

On Windows the debug information of a script module is a program database (PDB), a file next to the module. Strata's
script CMake file asks the Microsoft compiler for a PDB in every configuration, so the module always has one. The build
writes the module and its PDB into `.strata/Scripts/Bin` of your project.

The editor does not run that file itself. It copies the module into a private folder under your user data and runs the
copy, so a new build can replace the original while the editor runs. The copy still records where its PDB lies, which is
`.strata/Scripts/Bin`, so the debugger finds it there. A breakpoint binds when the debugger finds the instructions of its line in those
tables, and this is why a breakpoint in your script binds. Do not move or
delete the PDB while you debug.

Two more facts shape what you see. First, the Release and Dist configurations make the code fast: the compiler copies
small functions into their callers, moves lines and keeps variables in processor registers. In such code stepping jumps
between lines in an odd order, and the debugger may report a variable as `optimized out`. The downloaded Strata comes from a
build in `Dist`, and the editor builds your scripts in its own configuration, so expect odd steps. A source build in `Debug`
steps line by line.

Second, Linux and macOS use the compilers GCC and Clang to build scripts. Since 0.8.0 the script CMake file asks them for
debug information in every configuration too, as it asks the Microsoft compiler for a PDB. On Linux the tables stay
inside the module itself. On macOS they stay in the object files of the script build, and the module records where those
lie, so do not delete the build folder while you debug. A breakpoint in a script therefore binds with the downloaded
editor on every system.

## Attach the debugger to the editor

**Attaching a debugger** connects it to a process that already runs, so you start the editor as usual and then ask the
debugger to take control of it. Strata's manual calls this the way to debug scripts: attach to `StrataEditor`, set
breakpoints in your script files, press **Play**. First check what your system asks before it lets one program attach to
another.

::::tabs{sync=os}
:::tab[Windows]
Nothing special: a debugger running as your user may attach to your own programs. Visual Studio needs its C++ tools,
which the script build needs too, so a reader who built a script has them. The editor shows as `StrataEditor.exe`.
:::
:::tab[Linux]
Ubuntu allows a process to attach only to its own children, through a Linux setting named `kernel.yama.ptrace_scope`
whose default is 1. To attach to an editor you started from the desktop, change it until the next boot with
`sudo sysctl kernel.yama.ptrace_scope=0`. Visual Studio Code needs the debugger `gdb`: install it with `sudo apt install gdb`.
:::
:::tab[macOS]
The first attach shows a prompt that asks you to let the debugger control another process, and it needs your password or
fingerprint. Allow it. Visual Studio Code uses the debugger `lldb` for this, which comes with Apple's command line tools.
:::
::::

### With Visual Studio on Windows

Use these steps on Windows with Visual Studio. The picture of the dialog is yours to see on your screen; the labels below
are the ones of Visual Studio.

1. Start `StrataEditor.exe` and open your project. Build the scripts with **Ctrl+B** once, so a module exists.
2. In Visual Studio, choose "File ▸ Open ▸ File..." and open a script of your project, for example `Scripts/Coin.cpp`.
3. Choose "Debug ▸ Attach to Process...", select `StrataEditor.exe` in the list and choose "Attach". The code type is
   native code, which "Automatic" picks.
4. Click the grey margin left of a line number in your script. A red dot appears: the breakpoint.
5. In the editor, press **Play**. The editor freezes when the line runs, and Visual Studio shows the line.

If the dot stays hollow and says that it found no symbols, add the folder. Choose "Tools ▸ Options ▸ Debugging ▸
Symbols", then add `.strata/Scripts/Bin` of your project, as a full path, to the list of symbol file locations. The window
"Debug ▸ Windows ▸ Modules" shows whether the module's symbols loaded.

### With a launch file

Visual Studio Code starts a debugger through a file named `launch.json`, which the Strata editor does not write. It holds data in the
JSON format, which [Data formats](../basics/data-formats.md) teaches; here you copy the file whole and change the marked
parts. The
file belongs in a folder named `.vscode` inside your project's `Scripts` folder, a folder whose name starts with a dot,
which the script build neither compiles nor watches.

Visual Studio Code needs Microsoft's C/C++ extension, installed from its "Extensions" view. On Linux it also needs `gdb`, as the tab
above says. Open the `Scripts` folder with "File ▸ Open Folder...", then paste the file for your system.

::::tabs{sync=os}
:::tab[Windows]

```json
{
	"version": "0.2.0",
	"configurations": [
		{
			"name": "Attach to StrataEditor",
			"type": "cppvsdbg",
			"request": "attach",
			"processId": "${command:pickProcess}"
		}
	]
}
```

1. **Line 5:** the name that appears in Visual Studio Code's list of debug configurations.
2. **Line 6:** `cppvsdbg` is the Windows debugger of the C/C++ extension; it reads the PDB like Visual Studio does.
3. **Line 8:** `${command:pickProcess}` makes Visual Studio Code show a list of processes when you start; pick `StrataEditor.exe`.

:::
:::tab[Linux]

```json
{
	"version": "0.2.0",
	"configurations": [
		{
			"name": "Attach to StrataEditor",
			"type": "cppdbg",
			"request": "attach",
			"program": "<full path of the StrataEditor program>",
			"processId": "${command:pickProcess}",
			"MIMode": "gdb"
		}
	]
}
```

1. **Line 6:** `cppdbg` is the debugger of the C/C++ extension that drives `gdb`.
2. **Line 8:** replace the marked text with the full path of the `StrataEditor` program in your Strata folder.
3. **Line 10:** the name of the debugger program that `cppdbg` starts.

:::
:::tab[macOS]

```json
{
	"version": "0.2.0",
	"configurations": [
		{
			"name": "Attach to StrataEditor",
			"type": "cppdbg",
			"request": "attach",
			"program": "<full path of the StrataEditor program>",
			"processId": "${command:pickProcess}",
			"MIMode": "lldb"
		}
	]
}
```

1. **Line 6:** `cppdbg` is the debugger of the C/C++ extension.
2. **Line 8:** replace the marked text with the full path of the `StrataEditor` program in your Strata folder.
3. **Line 10:** `lldb` is the debugger program of macOS.

:::
::::

Open `Coin.cpp`, click left of a line number to set a breakpoint, press **F5**, pick the `StrataEditor` process, and press
**Play** in the editor. A second editor that runs another project appears as a second entry in the list; pick the one
of your project.

## A breakpoint stops the program before a line runs

A **breakpoint** is a mark on a line that tells the debugger to stop the program immediately before that line runs. The program
keeps all its values at the moment of the stop, so you can read them. Pausing stops the whole editor: a script runs inside
the editor's frame, so the frame cannot finish while the script waits.

A breakpoint can carry a **condition**, an expression the debugger tests each time the line runs; it stops only
when the expression is true. In Visual Studio you right-click the red dot and choose "Conditions..."; in Visual Studio Code you
right-click the margin and choose "Add Conditional Breakpoint...".

:::example[A breakpoint that waits for frame 100]
A script counts frames in `m_Counter` and you want to see the state when it reaches 100. A plain breakpoint on the line
`m_Counter++;` stops in every frame: you would press "Continue" 100 times, and each press shows one frame. With the condition `m_Counter == 100`, the debugger checks it at each frame and stops once. At 60 frames
per second that is after 100 / 60 = 1.7 seconds of play.
:::

Try it: which condition stops only when `m_Counter` is a multiple of 50? (The operator `%` gives a remainder.)

:::answer
`m_Counter % 50 == 0`. It is true for 50, 100, 150 and so on, because the remainder of the division by 50 is zero there.
:::

## Stepping runs the code line by line

A stop is only the start. **Stepping through code** runs the program a little at a time from the stop, with three moves:

- **Step over** runs the current line completely, including any function it calls, and stops at the next line.
- **Step into** enters the function that the line calls and stops on that function's first line.
- **Step out** runs until the current function returns, and stops in its caller.

Visual Studio and Visual Studio Code both use **F10** for step over, **F11** for step into and **Shift+F11** for step out, and **F5**
continues the program. On some laptops the function keys need **Fn**.

While stopped, the debugger lists the **variables** of the current function. You add expressions to a **watch** list,
such as `DegreesPerSecond * deltaTime`, and the debugger computes them again at each stop.

You can also change a value: double-click it in the list and type a new one (Visual Studio Code: right-click it and choose "Set
Value"). The program continues with your number until its own code writes the variable again. That tests a guess without a
rebuild: change the value, continue, and see whether the symptom goes.

In fast Release or Dist code, a variable may read as `optimized out`, and a step may skip lines. The debugger works as
designed. Add a log line, or build the scripts in a Debug configuration, to see the value.

## The call stack lists the calls that have not returned

When `OnUpdate` calls `TurnAngle`, which calls `ToRadians`, the program must remember where to return when each function ends.
It keeps one record for each call that has started and not returned. The **call stack** is the list of those open calls,
newest first.

Each record is a **stack frame**: the arguments of one call, its :term[local variables]{id=local-variable} and the place it returns to.

The program below shows the growth. Each function prints the depth of the stack while it runs, and the depth falls back as
the calls return.

```cpp sketch="basics-debugging-stack.cpp"
// Each function prints how many calls are open while it runs: that count is the depth of the call stack.
#include <cstdio>
float ToRadians(float degrees, int depth)
{
	std::printf("depth %d: ToRadians\n", depth);
	return degrees * 3.14159265f / 180.0f;
}

float TurnAngle(float degreesPerSecond, float deltaTime, int depth)
{
	std::printf("depth %d: TurnAngle\n", depth);
	return ToRadians(degreesPerSecond * deltaTime, depth + 1);
}

void OnUpdate(float deltaTime)
{
	std::printf("depth 1: OnUpdate\n");
	const float angle = TurnAngle(90.0f, deltaTime, 2);
	std::printf("depth 1: OnUpdate again, angle %.4f\n", angle);
}

int main()
{
	OnUpdate(0.016f);
}
```

```text output-of="basics-debugging-stack.cpp"
depth 1: OnUpdate
depth 2: TurnAngle
depth 3: ToRadians
depth 1: OnUpdate again, angle 0.0251
```

1. **Lines 3–7:** `ToRadians` runs at depth 3, the deepest point, and returns a value to its caller.
2. **Lines 9–13:** `TurnAngle` calls `ToRadians` with `depth + 1`; the depth counts the open calls.
3. **Lines 15–20:** `OnUpdate` ends with depth 1 again, because the two calls it made have returned.

In a debugger, the "Call Stack" window shows those frames with the newest on top. Click a lower frame, and the
variables panel shows that call's own variables, so you see what `OnUpdate` held when it called `TurnAngle`. That answers
the question "how did the program get here?", which a bug in a shared helper function needs.

A **stack trace** prints the call stack at one moment, usually when something goes wrong. A script crash report holds one.

On Windows the editor reads the PDB to name the file and line of each frame. The Problems panel
lists the frames below the crash line with their files, and marks a frame that the compiler copied into its caller with
"(inlined)". On Linux and macOS the report gives the function and the offset in the module, and not the file and line.
[Symbolization](../scripting/symbolization.md) explains how the editor finds them.

## The coins crawl: a worked bug

:::example[The speed turned into radians twice]
Plant the bug in your `Coin` script. Find the line that builds the turn, which reads like the line of the example
`Spinner`: it passes `glm::radians(DegreesPerSecond * deltaTime)` to `glm::angleAxis`. Change it to
`glm::radians(glm::radians(DegreesPerSecond * deltaTime))`, build and play. The coins still build and spin, but they
crawl.

Step 1: the coins crawl at every play, so the bug repeats. Step 2: put a breakpoint on that line and the expression
`DegreesPerSecond * deltaTime` in a watch. At 90 degrees per second and 60 frames per second you read 90 / 60 = 1.5
degrees per frame, as expected. The angle that `glm::angleAxis` receives should be those 1.5 degrees in radians, 0.0262,
and the watch of that angle shows 0.000457.

Step 3: guess that the code converts the angle to radians twice. A second conversion divides by 57.3, and 0.0262 / 57.3 =
0.000457, which matches. Step 4: remove one `glm::radians`; the watch now shows 0.0262. Step 5 needs nothing more. Step 6:
check that all five coins turn at their old speeds again, a half turn in 2 seconds at 90 degrees per second, and keep a
note of the steps.
:::

The program below does the numbers of this example in plain C++, so you can see the two angles side by side.

```cpp sketch="basics-debugging-radians.cpp"
// The Coin Run bug: the angle of one frame turned into radians twice, beside the angle turned once.
#include <cstdio>

float ToRadians(float degrees)
{
	return degrees * 3.14159265f / 180.0f;
}

int main()
{
	const float degreesPerSecond = 90.0f;
	const float deltaTime = 1.0f / 60.0f; // one frame at 60 frames per second
	const float degrees = degreesPerSecond * deltaTime;

	const float correct = ToRadians(degrees);
	const float planted = ToRadians(ToRadians(degrees));

	std::printf("degrees in one frame: %.4f\n", degrees);
	std::printf("correct angle in radians: %.6f\n", correct);
	std::printf("planted angle in radians: %.6f\n", planted);
	std::printf("the planted coin turns %.1f times too slowly\n", correct / planted);
	return 0;
}
```

```text output-of="basics-debugging-radians.cpp"
degrees in one frame: 1.5000
correct angle in radians: 0.026180
planted angle in radians: 0.000457
the planted coin turns 57.3 times too slowly
```

1. **Lines 15–16:** the correct angle converts once; the planted angle converts twice.
2. **Lines 18–21:** the ratio is 57.3, the number of degrees in one radian, which is why the coins look frozen.

## Common mistakes

- **Changing several things at once.** The symptom disappears and you do not know why. Undo, and change one thing per
  test.
- **A bug you cannot repeat.** You test a guess against a bug that sometimes is not there. Find the steps that show it
  every time before step 2.
- **A log line in every frame.** The Console fills and the line you wanted has disappeared. Log when a value changes, or add an
  `if`.
- **A breakpoint that never stops.** The script never runs: the game is not playing, the class is not on an entity, or
  the module is old. Build again, attach the class to an entity and press **Play**.
- **A hollow breakpoint.** The debugger has no symbols. Add `.strata/Scripts/Bin` to the symbol search path, and check
  that you built after your last edit.
- **A frozen editor while stopped.** This is normal: the whole editor waits for the debugger. Press "Continue".
- **Trusting every step in fast code.** Lines skip and variables vanish. Read the value in a log line.
- **Attaching to the wrong process.** Two editors show as two `StrataEditor` entries. Pick the one that has your project.

## Summary

- Make the bug happen again, observe, guess one cause, test it with one change, fix it, then check and keep the check;
  one cause and one change at a time keep the result clear.
- The Console shows `Log` lines at four levels, hides Trace until you tick its box, keeps 4,096 lines and does not open
  script lines; write names with values and log on events, never every frame.
- A debugger attached to `StrataEditor` stops the whole editor on a breakpoint; the module's PDB in `.strata/Scripts/Bin`
  lets it bind, and the symbol path fixes a hollow breakpoint.
- A condition makes a breakpoint stop only when it is true; step over runs a line, step into enters a call, step out
  returns, and a watch shows or changes a value.
- The call stack lists the open calls newest first, a stack frame is one call's record, and a stack trace is the list that a
  crash report prints.

## Check yourself

1. A coin crawls after you edited its script. Which action comes first: A, delete the last edited line; B, write down the
   steps that show the crawl; C, change the speed field to 1000; or D, add a breakpoint in the engine?

   :::answer{tests="method"}
   B. You cannot test a guess on a bug that you cannot repeat. A and C change code before you observe anything. D looks at the
   wrong code.
   :::

2. A script writes `Log::Info("hits ", hits)` in `OnUpdate` on 8 cubes at 60 frames per second. How long until the
   Console drops lines: A, 8 seconds; B, 8.5 seconds; C, 85 seconds; or D, never?

   :::answer{tests="log"}
   B. 8 × 60 = 480 lines per second, and 4,096 / 480 = 8.5 seconds. C divides by 48, a slip of one digit. D forgets
   the limit, and A rounds 8.5 down.
   :::

3. You attached the debugger and `Coin.cpp` has a red breakpoint, but **Play** never stops there. Which cause is the
   least likely: A, no entity carries `Coin`; B, the editor is not playing; C, the line sits in a branch that never
   runs; or D, Visual Studio has the wrong version?

   :::answer{tests="attach"}
   D. A, B and C each mean the line never runs. The Visual Studio version does not matter once the symbols load.
   :::

4. A breakpoint with the condition `m_Counter == 100` stands on `m_Counter++;`, and the counter starts at 0. When does it
   stop: A, before the line runs, with 100 in the counter; B, after the line ran in the 100th frame, with 101; C, at the
   start; or D, never?

   :::answer{tests="stepping"}
   A. The debugger tests the condition when it reaches the line, before the line runs, so it stops with 100 in the
   counter. B would need a step over.
   :::

5. The call stack, newest first, is `Clamp`, `TurnAngle`, `OnUpdate`. After one step out, which function is current: A,
   `Clamp`; B, `TurnAngle`; C, `OnUpdate`; or D, the engine?

   :::answer{tests="call-stack"}
   B. Step out runs until `Clamp` returns, and stops in its caller, `TurnAngle`.
   :::

## Practice

Exercises 1, 2, 3 and 5 need a breakpoint that binds in your script, and it binds with the downloaded Strata on every
system. Exercise 4 needs no debugger. Exercises 1 to 4 run in your `Playground` script, on its own entity.

1. **Basic.** Put a breakpoint on the first line of `OnUpdate`, press **Play**, and add `deltaTime` to a watch. Press
   **Continue** three times and write the three values.

   :::answer[Worked solution]{tests="attach"}
   The values differ slightly in each frame, around 0.0167 at 60 frames per second, because frames last different
   times. The breakpoint stops again in every frame, so each continue shows the next frame's value.
   :::

2. **Medium.** Add a field `int32_t m_Counter = 0;` to `Playground` and `m_Counter++;` in `OnUpdate`. Put a breakpoint
   on that line with the condition `m_Counter == 100`. At what time of play does it stop, at 60 frames per second?

   :::answer[Worked solution]{tests="stepping"}
   After 100 / 60 = 1.7 seconds. The debugger stops once, before the line runs, with the watch showing 100, and 101 after
   one step over. A plain breakpoint would have stopped 100 times.
   :::

3. **Medium.** Write a function `float TurnAngle(float degrees)` that calls a second function `ToRadians`, and call
   `TurnAngle` from `OnUpdate`. Put a breakpoint in `OnUpdate`, step into twice, read the call stack, and step out twice.

   :::answer[Worked solution]{tests="call-stack stepping"}
   After two steps into, the call stack shows `ToRadians`, `TurnAngle`, `OnUpdate`, newest first, as the program of the
   call stack section prints for depths 3, 2 and 1. Each step out removes the top frame.
   :::

4. **Hard.** The script below should log `Playground.OnUpdate: ten frames` when its counter reaches 10, and it never
   does. Find the bug by the method alone: before each test, write your guess and your prediction on paper.

   ```cpp pseudocode
   void OnUpdate(float deltaTime) override
   {
   	m_Counter++;
   	if (m_Counter == 10)
   		Log::Info("Playground.OnUpdate: ten frames");
   }

   void OnLateUpdate(float deltaTime) override
   {
   	m_Counter = 0;
   }
   ```

   1. **Lines 1–6:** `OnUpdate` counts one frame and logs when the count is 10.
   2. **Lines 8–11:** `OnLateUpdate` also runs in every frame, after `OnUpdate`.

   :::answer[Worked solution]{tests="method log" solution="sketches/basics-debugging-counter.cpp"}
   Observe with `Log::Info("counter ", m_Counter)` in `OnUpdate`: it shows 1 in every frame. Guess: something sets the
   counter back to zero after each `OnUpdate`. Predict: removing the reset in `OnLateUpdate` gives 1, 2, 3 and the line at
   10. The program below repeats the bug in plain C++.

   ```cpp sketch="basics-debugging-counter.cpp"
   // The Hard exercise: a counter that never reaches 10, because a callback that runs every frame sets it back to zero.
   #include <cstdio>

   struct Playground
   {
   	int Counter = 0;
   	void OnUpdate()
   	{
   		Counter++;
   		std::printf("counter %d\n", Counter);
   		if (Counter == 10)
   			std::printf("ten frames reached\n");
   	}
   	void OnLateUpdate() { Counter = 0; } // meant to run once, in OnCreate
   };

   int main()
   {
   	Playground script;
   	for (int frame = 1; frame <= 12; frame++)
   	{
   		script.OnUpdate();
   		script.OnLateUpdate();
   	}
   }
   ```

   ```text output-of="basics-debugging-counter.cpp"
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   counter 1
   ```

   1. **Line 14:** the callback that runs after every `OnUpdate` sets the counter to 0, the bug.
   2. **Lines 20–24:** the loop runs both callbacks in every frame, as the engine does.

   The fix moves the reset to `OnCreate`, which runs once.
   :::

5. **Hard.** Plant the bug of the worked example in `Coin.cpp` and find it with a breakpoint on the turn's line and a
   watch on the angle. Find the two numbers that differ.

   :::answer[Worked solution]{tests="method attach" solution="sketches/basics-debugging-radians.cpp"}
   The watch shows 0.000457 where 0.0262 belongs. The converted value is 57.3 times too small, which points to a second
   conversion. The program below prints both angles.

   ```cpp sketch="basics-debugging-radians.cpp"
   // The Coin Run bug: the angle of one frame turned into radians twice, beside the angle turned once.
   #include <cstdio>

   float ToRadians(float degrees)
   {
   	return degrees * 3.14159265f / 180.0f;
   }

   int main()
   {
   	const float degreesPerSecond = 90.0f;
   	const float deltaTime = 1.0f / 60.0f; // one frame at 60 frames per second
   	const float degrees = degreesPerSecond * deltaTime;

   	const float correct = ToRadians(degrees);
   	const float planted = ToRadians(ToRadians(degrees));

   	std::printf("degrees in one frame: %.4f\n", degrees);
   	std::printf("correct angle in radians: %.6f\n", correct);
   	std::printf("planted angle in radians: %.6f\n", planted);
   	std::printf("the planted coin turns %.1f times too slowly\n", correct / planted);
   	return 0;
   }
   ```

   ```text output-of="basics-debugging-radians.cpp"
   degrees in one frame: 1.5000
   correct angle in radians: 0.026180
   planted angle in radians: 0.000457
   the planted coin turns 57.3 times too slowly
   ```

   1. **Lines 15–16:** one conversion for the correct angle, two for the planted one.
   :::

## Where the book uses it

- [Play, test and debug](../make/play-test-debug.md) uses the attached debugger and breakpoints on a script that plays.
- [Debugging the engine](../core/debugging.md) uses the method, the call stack and stack traces on the engine's own code.
- [Crash containment](../scripting/crash-containment.md) uses the stack trace that a script crash report holds.

## Further reading

- Microsoft Learn, "Attach to running processes with the Visual Studio debugger": the steps of the Attach to Process
  dialog; beginner.
- Microsoft Learn, "Debugging in Visual Studio": breakpoints, stepping, watch windows and the call stack; beginner.
- Visual Studio Code documentation, "C++ debugging configurations": the fields of `launch.json` for `cppdbg` and `cppvsdbg`;
  intermediate.
- Andreas Zeller, "Why Programs Fail": the method of this page in full, with a theory of finding causes; advanced.
