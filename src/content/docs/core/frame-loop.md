---
id: core/frame-loop
title: "The frame loop"
description: "What one turn of Strata's main loop does, in which order, what it counts as work and how it waits for the next frame."
kind: internals
size: L
tracks: [E]
needs: [core/first-frame, basics/threads]
time: 85
learn:
  - id: frame-order
    text: name the stages of one Strata frame in the order the loop runs them
  - id: skipped-frame
    text: explain why a frame is skipped or not counted, and where its time goes
  - id: work-time
    text: explain what the work time of a frame counts and what it omits
  - id: frame-pacing
    text: predict when a frame-rate cap lets each frame start, also after a late frame
  - id: main-thread-queue
    text: explain how another thread hands work to the main thread
since: 0.3.0
status: final
---

Once a Strata program has started, one loop runs it until it closes. A **frame** is one turn of that loop: one pass
that reads the input, lets the game or the editor do its work, draws the user interface and shows one new image. The
loop also counts the frames, measures what each one cost, and waits before the next one when the program should not
run faster. This page follows one frame from its first line to its last, in `Application::Run` and
`Application::RunFrame`, and then the end of the program.

The loop calls two kinds of code. A layer is a part of the program's own behaviour, such as the editor's interface or
the game; the program keeps its layers in an ordered list, the layer stack. A module is an engine module, a service that runs for
the whole program, such as graphics or audio, and the loop calls its hooks: functions it has for each moment of a
frame. [Windows, events and layers](windows-events.md) and [Engine modules](engine-modules.md) teach them in full, and
[Time](time.md) teaches how the game's time moves forward.

This page needs no project and no download. Its toy is a whole program for the compiler of [How a C++ program is
built](../basics/build.md#open-a-terminal-that-finds-a-compiler), and its one editor command runs with the installed
Strata. Its test commands and its trace need the source build of [your first engine
change](first-change.md#build-the-engine-and-start-the-editor), in `Debug`.

## The problem and how engines solve it

A program you use every day, such as a text editor, spends most of its life asleep. It asks the :term[operating system]{id=operating-system} for
the next event (a key, a click, a window that moved) and does nothing until one arrives. When nothing happens, the
program uses no time at all. A game cannot work that way. The ball keeps rolling while nobody touches the keys, and the
clouds keep moving across the sky.

The world of a game changes without input, so the game must make a new picture many times a second, whether or not an
event came. A game therefore runs a **frame loop**: a loop that repeats frames until the program closes. It is also
called the :term[game loop]{id=game-loop}. In each frame the loop takes whatever input arrived since the last one, moves the world forward
by the time that passed, and draws the result. The loop never waits for an event: it asks whether events came, and
continues when none did.

The book Game Programming Patterns describes three common forms of the loop. The oldest form runs at a fixed rate and
assumes that every frame takes the same time, which fails on a faster or slower computer. The second form measures the
time each frame took and moves the world by that much. The third form moves the world in steps of one fixed length and
draws as often as it can between them.

Strata's loop has the second form on the outside: it measures the time of each frame. Inside a running scene, the third
form takes over, and [Time](time.md) explains why.

### The stages of a frame

Every engine splits a frame into the same few stages, and their order matters:

1. Input comes first, so that the frame reacts to the key the player pressed a moment ago, not one frame later.
2. The update comes next: the :term[game logic]{id=game-logic}, physics and animation move the world by the frame's time.
3. The user interface is drawn after the update, so that a health bar shows the health the update has computed.
4. Presenting the image comes last, because the image is finished only when everything above has drawn into it.

Change the order and you see the result. A game that reads the keys after its update reacts one frame late, which a
player feels as a slow control. A menu drawn before the update shows the numbers of the last frame. An image shown
before the interface is drawn appears without the interface, which arrives one frame later.

### Frame pacing

A loop that never waits runs as fast as the computer allows: a thousand frames a second for a small scene. That speed
is waste. Most displays show only 60 or 120 new images a second. Every extra frame burns power and heats the machine
for a picture nobody sees. **Frame pacing** is deciding when each frame may start, so that frames come at a steady rate
the display and the player can use.

The usual way to pace a loop is to let the display do it. The :term[graphics card]{id=gpu}, or graphics processing unit (GPU), draws
the images; with **vsync**, the card hands a finished image to the display only when the display starts its next
refresh. A program then cannot finish frames faster than the display shows them. [Vulkan](../gpu/vulkan-nvrhi.md), the programming interface
Strata draws through, offers several [present modes](../gpu/how-a-gpu-frame-works.md), which are rules for when a finished image reaches the screen.

One of them keeps the finished images in a line, first in, first out (:term[FIFO]{id=queue}). The **FIFO present mode** is the present
mode in which the display takes one image from that line at each refresh, and it is the mode that gives vsync. A
program that asks for the next free image waits until the display has taken one, and that wait paces its loop.

Two cases need more than the display. A program without a window, such as the editor when a test drives it, has no
display to wait for, and its loop would run at full speed. Such a program limits its rate with a clock instead: it
sleeps out the rest of each frame's share of a second. The second case is a late frame. When one frame takes too long,
a schedule could run the next frames with no wait until it has caught up again.

That burst looks worse than the late frame itself. The player sees a pause, then several images in a rush, then the
steady rate again: two jolts instead of one. A good schedule lets the late frame go and continues from the moment it
ended.

The waits raise one more question. When a program waits 9 ms for the display in a frame of 16.7 ms, does the
frame cost 16.7 ms or 7.7 ms? Only the second number says what the frame costs the processor, so an engine that wants
to report its cost honestly measures a frame without its waits.

## One frame on a time line

The picture follows one frame of the editor on a display that shows 60 images a second, with vsync. The numbers are an
example chosen to add up, not a measurement. The blue blocks are work. The striped blocks are waits for something
outside the program.

::figure{id=frame-timeline}

The loop runs on the **main thread**, the one thread that owns the scene, the input, the scripts and the sending of
drawing work to the graphics card. Other threads, such as the job system's workers and the jobs that load assets, never
call into the loop. They hand their results to the :term[main thread]{id=main-thread} instead.

The frame starts with two short blocks of work. The first is the **main-thread queue**: a list of functions that other
threads have handed in for the main thread, which runs them at the start of every frame. The second is the input. Then
the graphics module waits for the display. After the wait, the layers, the modules and the user interface do their
work, and last the graphics module presents the image.

The **work time** of a frame is the processor time it costs without its waits. Here the work blocks add up to 9.5 ms
and the waits to 7.2 ms, so the work time is 9.5 ms. Strata also calls it the frame work time.

The calls of one turn look like this:

```mermaid caption="Who calls whom in one turn of the loop; other threads only hand in work for the main thread." alt="A diagram. The main function calls the run function. Run calls the frame function and the schedule, which calls a precise sleep. The frame function calls the queue, the window's events, the module hooks and the layer updates. Worker threads hand functions to the queue."
flowchart TD
	main["main (Engine/EntryPoint.h)"] --> run["Application::Run"]
	run --> frame["Application::RunFrame"]
	run --> pacer["FramePacer::WaitForNextFrame"]
	pacer --> sleep["Platform::SleepUntil"]
	frame --> queue["ExecuteMainThreadQueue"]
	frame --> events["Window::ProcessEvents"]
	frame --> hooks["EngineModule hooks"]
	frame --> layers["Layer::OnUpdate"]
	workers["worker threads"] -. "SubmitToMainThread" .-> queue
```

Everything in the diagram lives in `Strata/src/Strata/Core/`, except `main`, which is in
`Strata/src/Strata/Engine/EntryPoint.h`. `Application` owns the window, the layer stack, the modules, the queue and the
`FramePacer`. It calls no module by name: it calls the hooks of whatever modules the program listed.

:::example[The work time of the example frame]
Add the work blocks of the picture. The queue takes 0.3 ms and the input 0.7 ms. The editor's layer takes 4.0 ms,
the modules' update 0.5 ms and the user interface 4.0 ms. The sum is 9.5 ms. The frame took 16.7 ms from start to
start, so the waits took 16.7 − 9.5 = 7.2 ms: 6.0 ms at the start of the frame and 1.2 ms while presenting.

Now move the editor to a display that shows 120 images a second. Frames would start 8.3 ms apart, and a frame that
costs 9.5 ms cannot keep that pace. The waits shrink to nothing, and the editor runs at fewer than 120 frames a second.
The work time tells you so. The length of the frame alone would not.
:::

## The contract

This section states what the loop promises and what it asks of the code it calls, rule by rule, with the reason for
each.

### One turn of `Run`

`Run` repeats one turn while the application is running. A turn does these things, in this order:

1. The turn reads the clock and computes the [time step](../basics/math-change.md): the time since the previous turn, clamped to
   `ApplicationSpecification::MaxTimestep`, 0.25 s by default. A turn after a [breakpoint](../basics/debugging.md) that held the program for a
   minute moves the game by 0.25 s, not by a minute. Why the clamp exists is the subject of [Time](time.md).
2. The turn runs `RunFrame` inside a `try` and `catch` block. An exception is the way C++ code stops and reports an
   error to its callers, and the block catches such a report. `RunFrame` returns whether the frame ran.
3. The turn counts the frame only when it ran. When the count reaches `ApplicationSpecification::MaxFrames`, the
   application closes. Tests and scripts use the limit to run a fixed number of frames.
4. The turn asks whether the person pressed **Ctrl+C** in the terminal or the system asked the program to end. If so,
   the turn logs a warning, sets the :term[exit code]{id=exit-code} 130 unless the program had already set another,
   and closes.
5. While the application still runs, the turn waits for the `FramePacer`.

Callers may assume that a turn always runs to its end. A request to close (`Application::Close`, the window's close
button, **Ctrl+C**) never stops a frame in the middle: it takes effect after the turn.

### The order of `RunFrame`

`RunFrame` is one frame. It runs these stages, and the order is a promise every module and layer may rely on:

1. The main-thread queue: every function that other threads handed in since the last drain runs.
2. The Input stage: a new [input frame](../input/devices-state.md) begins, the window delivers its events (keys, the mouse, a change of size)
   through the modules and the layers, and the project's [input actions](../input/actions.md) take the frame's input.
3. When the window is minimized, the frame ends here: the loop sleeps 16 ms and the frame is not counted.
4. Each module's `OnBeginFrame`, in the modules' order. A module answers `Continue`, `Skip` or `Close`.
5. Each layer's `OnUpdate`, in the order of the layer stack, with the time step.
6. Each module's `OnUpdate`, then each module's `OnRenderUI`.
7. The work time is measured.
8. Each module's `OnEndFrame`, in reverse order. The graphics module comes first in the order, so it ends last, and
   there it [presents the image](../gpu/how-a-gpu-frame-works.md).

A module that answers `Skip` ends the frame: the loop sleeps 16 ms and the frame is not counted. The graphics module
does so while the images of the window change size. A module that answers `Close` closes the application after the
turn; the graphics module does so when the graphics device was lost. In both cases the modules after it get no
`OnBeginFrame`, and no module gets the frame's other hooks, not even `OnEndFrame`. A module must therefore cope with a
frame it began that never ends.

Why sleep 16 ms? A frame that cannot draw would fail again at once, and without the sleep the loop would keep one
:term[processor core]{id=processor-core} busy for nothing. 16 ms is about one frame at 60 frames a second, so the
program soon notices when it can draw again.

Why not count a skipped frame? The count (`GetFrameCount`) is what `MaxFrames` compares against, and a test that asks
for three frames wants three frames that ran. The next turn measures its time step from the start of the skipped turn,
so the skipped turn's time reaches the game. The step the skipped turn measured, from the turn before it, is
dropped: a step covers one turn, never several.

Check your reading before you continue. A game runs at 60 frames a second, and its window is minimized for exactly one
second. About how many frames does the loop count in that second, and how many turns does it run?

:::answer
The loop counts none, because every turn of that second ends at the minimized test. It runs about 60 turns, since each
one sleeps 16 ms and does little else. The exact number depends on how long the input stage takes.
:::

### What the work time omits

`Application::GetLastFrameWorkTime` returns the work time of the last frame that ran, in seconds. The measurement
starts at the top of `RunFrame` and ends after the last `OnRenderUI`. Three kinds of time are not part of it:

- the time the modules report as waiting (`EngineFrame::WaitSeconds`), such as the graphics module's wait for the
  graphics card's earlier frames and for the display's next image;
- the time of the frame's stages that lie outside the work time. A stage is a named, timed part of the frame, such as
  `Input`, whose times [Measuring the frame](profiling.md) teaches you to read. Of the built-in stages only `Present`
  lies outside; it also covers the wait for the display's image where the driver hands it out only at its
  first use. A module may register more such stages (`FrameProfiler::RegisterStage`);
- everything after the measurement: the modules' `OnEndFrame` and the wait for the next frame.

The length of a frame depends on the display and on any limit of the rate.
The work time does not. The editor records the work time of every frame, and the `editor.wait` command reports it. A
script that measures a scene therefore learns what the scene costs, not how fast the display is.

The rule for module writers follows. A module that waits for something outside the program adds the time it waited to
the frame's `WaitSeconds`, or times the wait as a stage outside the work time. A module that waits without saying so
makes every frame look busier than it is.

### Handing work to the main thread

Other threads may not touch the scene, the input or the drawing state, because the main thread uses them without a
lock. Instead, they hand their results to the main thread through the main-thread queue. `SubmitToMainThread` adds a
function to the queue under a :term[mutex]{id=mutex}, so any thread may call it at any time.

The queue promises three things. A function handed in during a frame runs at the start of the next one, before its
input. A function handed in while the queue is being drained waits for the next drain, because the drain takes the
whole list first and runs it afterwards. A function handed in during the last frame still runs: `Run` drains the queue
once more after the loop, while the layers that asked for the work still exist.

:::rule[Results from other threads return through the main thread]
The engine's rules let background work return its results only through `Application::SubmitToMainThread` or queues
the main thread reads, never through :term[callbacks]{id=callback} that touch engine state from a worker thread. A callback on a worker
would change the scene while the main thread reads it: a :term[data race]{id=data-race} that no test reliably catches. The rule is in the
engine's `AGENTS.md`, under "Architecture rules", and [Threads and the job system](jobs.md) explains the threads.
:::

### The frame-rate cap

A program's **frame rate** is the number of frames it completes in a second.

A **frame-rate cap** is a highest frame rate that a loop does not exceed. In Strata the cap is the `FramePacer` that the application owns.
`ApplicationSpecification::MaxFrameRate` sets its first rate (0 means no cap), and `Application::SetMaxFrameRate`
changes the rate while the program runs.

The editor and the :term[runtime]{id=runtime} cap themselves at 60 when they run without a window, because nothing else would pace them.
With a window, vsync paces the program, and the cap works on top of it.

The `FramePacer` keeps a fixed schedule. Each frame's slot starts one period after the last one, and a frame that ended
early sleeps until its slot. The first wait has no last slot, so it sleeps one whole period from the moment the frame
ended; so does the first wait after a new rate. A frame that ended after its slot lets the next frame start at once. The schedule then
continues from that moment, so a late frame causes no burst of frames without waits.

Setting a new rate starts a new schedule at the next wait. Setting the rate it already has changes nothing, so a caller
may set the rate in every frame. The editor does so: while the person does nothing, it lowers the cap, as
[Status bar, toasts and idle throttling](../editor-ui/status.md) describes.

The `FramePacer` sleeps with `Platform::SleepUntil`, which promises to wake as close to the deadline as the system
allows. On Windows it wakes within about 1 ms, where the :term[standard library's]{id=standard-library} sleep would wait for the system's clock
tick, 15.6 ms by default. How each system sleeps is in [Talking to the operating system](platform.md).

### Clocks: `Timer`, `Time::GetTime` and `Timestep`

The loop reads one clock: `Time::GetTime`, a time in seconds as a `double` that only moves forward. It counts from its
first call, early in the program's start; the comment in the code calls it the time since the process started. Strata
builds it on the standard library's `steady_clock`. The time of day would be wrong here: it jumps when the computer
corrects its clock, and when the clocks change for summer time.

The time step is a `Timestep`: a `float` of seconds, with `GetSeconds` and `GetMilliseconds`. A `float` keeps about
seven digits, enough for a step of a few ms but not for a time since the start. After three hours (10,800 s), two
`float` values next to each other are about 1 ms apart, so the time since the start is a `double`.

`Timer` is a small clock for code that measures a stretch of time. It starts when you make it or call `Reset`, and
`Elapsed` and `ElapsedMillis` return what passed since then.

### The end of the program

When the loop ends, `Run` finishes in this order: the main-thread queue drains once more, the program's own
`OnShutdown` runs, and the modules get `OnStop` in reverse order, while the layers still exist. The application's
:term[destructor]{id=destructor} then removes the layers, from the top down. It ends the modules in reverse order in three steps: `OnRelease`
while the job system still runs; then `JobSystem::Shutdown`, with a drain of the queue before and after it; then
`OnShutdown`.

Last, the destructor destroys the modules and closes the window. Then `main` closes the log and returns the exit code it
read right after `Run`.

The order has a reason at each step. Layers go first, because they use the modules. Modules
release their assets while the job system runs, because the [asset manager](../assets/what-is-an-asset.md) waits for its loading jobs. The graphics
device goes last of all, because the released assets owned graphics memory.

### A failure in a frame and the exit code

Engine code does not throw exceptions, but other libraries it uses may: the graphics library can report a lost device
by throwing one. `Run` catches any exception of the standard kind (`std::exception` and the types built on it) that escapes a frame. It logs a critical line,
`Unhandled exception in the main loop`, and ends the loop. The program then shuts down in the usual order and keeps its
log, but the rest of that frame's hooks never run, so its `OnEndFrame` does not happen.

The catch also sets the exit code to 1, `Application::c_UnhandledExceptionExitCode`, unless a layer had set another
one before. A script or a test that reads the exit code then sees a failed run. Before 0.8.0 the code stayed 0, the
code for success. An exception that is not a standard exception is not caught at all and ends the program at once.

## A toy version

The toy does the loop's job in 79 lines, without a window, a graphics card or modules. A simulated clock that counts
in steps of 1 ms replaces the real one, so that the output is the same on every computer.

In the toy, a worker thread hands one function to the queue. The third turn finds the window minimized. The fourth turn works 30 ms, more than its
slot of 20 ms, and after the sixth, a breakpoint holds the program for 400 ms. Watch the start times and the steps.

```cpp sketch="core-frame-loop-toy.cpp"
// A toy frame loop: the order of one frame, a skipped frame, the work time, the clamp and a frame-rate cap.
// The clock is simulated in whole milliseconds, so the output is the same on every machine.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <mutex>
#include <thread>
#include <vector>

namespace
{
	long long s_Now = 0; // the simulated clock, in milliseconds

	std::mutex s_QueueMutex;
	std::vector<std::function<void()>> s_Queue;

	void SubmitToMainThread(std::function<void()> function)
	{
		std::scoped_lock lock(s_QueueMutex);
		s_Queue.push_back(std::move(function));
	}

	void DrainQueue()
	{
		std::vector<std::function<void()>> queue;
		{
			std::scoped_lock lock(s_QueueMutex);
			queue.swap(s_Queue);
		}
		for (std::function<void()>& function : queue)
			function();
	}
}

int main()
{
	constexpr long long c_Period = 20;   // the frame-rate cap: 50 frames per second
	constexpr long long c_MaxStep = 250; // the clamp of the step
	constexpr int c_MaxFrames = 6;

	std::thread worker([] { SubmitToMainThread([] { std::printf("         queue: a worker's result runs on the main thread\n"); }); });
	worker.join(); // here the worker posts before the first frame, so the output never changes

	int framesRun = 0;
	long long lastTurn = s_Now;
	long long nextSlot = 0;
	bool scheduled = false;
	for (int turn = 1; framesRun < c_MaxFrames; turn++)
	{
		const long long turnStart = s_Now;
		const long long step = std::min(turnStart - lastTurn, c_MaxStep);
		lastTurn = turnStart;
		DrainQueue();
		if (turn == 3) // the input stage learns that the window is minimized
		{
			s_Now += 16;
			std::printf("turn %d at %3lld ms: minimized, slept 16 ms, not counted\n", turn, turnStart);
		}
		else
		{
			const long long wait = 3;               // begin: wait for the GPU's earlier frame
			const long long work = turn == 4 ? 30 : 5; // update and UI (turn 4 is a slow frame)
			s_Now += wait + work;
			const long long workTime = s_Now - turnStart - wait;
			s_Now += 1;                             // end: present the image
			if (turn == 6)
				s_Now += 400; // a breakpoint holds the program
			framesRun++;
			std::printf("turn %d at %3lld ms: step %3lld ms, work %2lld ms, frame %d\n", turn, turnStart, step, workTime, framesRun);
		}
		if (framesRun == c_MaxFrames)
			break;
		// The pacer: the next slot is one period after the last one, or now when that slot has passed.
		nextSlot = scheduled ? std::max(nextSlot + c_Period, s_Now) : s_Now + c_Period;
		scheduled = true;
		s_Now = std::max(s_Now, nextSlot);
	}
	return 0;
}
```

```text output-of="core-frame-loop-toy.cpp"
         queue: a worker's result runs on the main thread
turn 1 at   0 ms: step   0 ms, work  5 ms, frame 1
turn 2 at  29 ms: step  29 ms, work  5 ms, frame 2
turn 3 at  49 ms: minimized, slept 16 ms, not counted
turn 4 at  69 ms: step  20 ms, work 30 ms, frame 3
turn 5 at 103 ms: step  34 ms, work  5 ms, frame 4
turn 6 at 123 ms: step  20 ms, work  5 ms, frame 5
turn 7 at 532 ms: step 250 ms, work  5 ms, frame 6
```

1. **Lines 17–32:** the queue. `SubmitToMainThread` adds under the mutex. `DrainQueue` trades the whole list for an empty one
   under the mutex and runs it afterwards, so a function never runs while the lock is held.
2. **Line 51:** the step is the time since the previous turn, clamped. Turn 7 starts 409 ms after turn 6, but its step
   is 250 ms.
3. **Lines 54–58:** the minimized turn sleeps 16 ms and does not count. Turn 4's step is 20 ms, measured from the
   start of turn 3, so the minimized turn's time reaches the game. Turn 3's own step, the 20 ms since turn 2, is dropped.
4. **Line 64:** the work time is the turn's time without the wait at its start. The present at line 65 and the
   schedule come after it, so they are not counted either.
5. **Lines 73–76:** the schedule. The first slot lies one period after turn 1 ends at 9 ms, so turn 2 starts at
   29 ms. Turn 4 ends at 103 ms, after its next slot at 89 ms, so turn 5 starts at once, at
   103 ms. Turn 6 starts at 123 ms, one period later. A schedule that kept its old slots would start turn 6 the moment
   turn 5 ended, at 112 ms, to catch up with the slot at 109 ms.

The queue runs first, and a skipped turn counts no frame and drops
the step it measured. The work time omits the waits, and the schedule never bursts. Imagine `c_Period` set to 0: every turn would
start the moment the previous one ended, as a program with no cap and no vsync does.

## The real code

Strata's loop has the toy's shape, with the real clock, real modules and two more ways for a turn to end. Read `Run`
first. Search it for the four things the toy has (the clamp, the frame count, the schedule, the drain at the end) and
the two it lacks: the `try` and `catch` block and the interrupt.

```cpp src="Strata/src/Strata/Core/Application.cpp#L228-L287" symbol="Application::Run"
	if (!m_Running)
		return;

	OnInit();

	m_LastFrameTime = Time::GetTime();
	while (m_Running)
	{
		ST_PROFILE_FRAME();
		const double time = Time::GetTime();
		const float elapsed = static_cast<float>(time - m_LastFrameTime);
		m_LastFrameTime = time;
		m_LastTimestep = Timestep(std::min(elapsed, m_Specification.MaxTimestep));

		bool frameRan = false;
		try
		{
			frameRan = RunFrame(m_LastTimestep);
		}
		catch (const std::exception& exception)
		{
			// Engine code does not throw; this catches third-party failures (e.g. the graphics driver reporting a
			// lost device inside NVRHI) so the application still shuts down in order and flushes its logs.
			ST_CORE_CRITICAL("Unhandled exception in the main loop: {}", exception.what());
			m_Running = false;
			// The run failed: a caller (CI, a script, the launcher) must not read success. A code set before (a failed
			// command script, an interrupt) says more and stays.
			if (m_ExitCode == 0)
				m_ExitCode = c_UnhandledExceptionExitCode;
		}

		if (frameRan)
		{
			m_FrameCount++;
			if (m_Specification.MaxFrames && m_FrameCount >= *m_Specification.MaxFrames)
				m_Running = false;
		}
		// Ctrl+C in the terminal of a Console run, or a termination signal: the frame ran to its end, and the layers
		// shut down as after any other close.
		if (m_Running && Platform::IsInterruptRequested())
		{
			ST_CORE_WARN("Interrupted (Ctrl+C or a request to terminate): closing");
			if (m_ExitCode == 0)
				m_ExitCode = c_InterruptedExitCode;
			m_Running = false;
		}
		if (m_Running)
			m_FramePacer.WaitForNextFrame();
	}

	// What the last frame posted for the main thread (a screenshot answered without the Graphics module, a job's
	// result) runs as the next frame would have run it: while the layers that asked for it still exist, and before
	// main reads the exit code it may set.
	ExecuteMainThreadQueue();

	OnShutdown();
	const std::span<EngineModule* const> started = GetStartedModules();
	for (auto it = started.rbegin(); it != started.rend(); ++it)
		(*it)->OnStop();
}
```

1. **Line 240:** the step, clamped to `MaxTimestep`. The toy's clamp was a constant; here it is part of the
   application's specification, so a test may change it.
2. **Lines 243–257:** the `try` and `catch` block. `frameRan` stays `false` when an exception escapes, so the failed
   frame is not counted. `m_Running` becomes `false`, and the exit code becomes 1 unless it already held another.
3. **Lines 259–264:** only a frame that ran is counted, and `MaxFrames` closes the program after the frame that
   reaches it. The toy stopped the same way.
4. **Lines 267–273:** the interrupt, which the toy did not have. The turn asks for it once, after the frame, so a frame
   is never cut in half.
5. **Lines 281–286:** the end of `Run`: the last drain, the program's `OnShutdown`, and the modules' `OnStop` in
   reverse order.

`Run` also calls `OnInit` once before the loop, so a program's own start code runs after the modules have started. It
returns at once when the application failed to start.

`RunFrame` is the toy's body with real modules. Search it for the order of the hooks, the two ways a frame ends early,
and the line that measures the work time.

```cpp src="Strata/src/Strata/Core/Application.cpp#L289-L348" symbol="Application::RunFrame"
bool Application::RunFrame(Timestep timestep)
{
	// The frame's work time (GetLastFrameWorkTime) leaves out what the modules wait for and what they do after the
	// frame's work (OnEndFrame). The frame profiler's frame is the same: it is ended with that work time, and a skipped
	// frame is never ended.
	const double frameStart = Time::GetTime();
	FrameProfiler& profiler = FrameProfiler::Get();
	profiler.BeginFrame();
	ExecuteMainThreadQueue();

	{
		ST_PROFILE_STAGE("Input");
		Input::BeginFrame();
		if (m_Window)
		{
			m_Window->ProcessEvents();
			m_Minimized = m_Window->IsMinimized();
		}
		// The frame's input is in: the actions take it (once per input frame; a binding capture at every call).
		InputActions::Update();
	}

	if (m_Minimized)
	{
		// Avoid spinning at 100% CPU while minimized.
		std::this_thread::sleep_for(c_SkippedFrameWait);
		return false;
	}

	const std::span<EngineModule* const> modules = GetStartedModules();
	EngineFrame frame { timestep, 0.0, m_LayerStack };
	for (EngineModule* module : modules)
	{
		switch (module->OnBeginFrame(frame))
		{
			case EngineFrameAction::Continue:
				break;
			case EngineFrameAction::Skip:
				std::this_thread::sleep_for(c_SkippedFrameWait);
				return false;
			case EngineFrameAction::Close:
				Close();
				return false;
		}
	}

	for (Layer* layer : m_LayerStack)
		layer->OnUpdate(timestep);
	for (EngineModule* module : modules)
		module->OnUpdate(frame);
	for (EngineModule* module : modules)
		module->OnRenderUI(frame);
	// Waits timed as stages outside the work time (the display's image at its first use) are no work either.
	m_LastFrameWorkTime = std::max(0.0, Time::GetTime() - frameStart - frame.WaitSeconds - profiler.GetOutOfWorkSeconds());

	for (auto it = modules.rbegin(); it != modules.rend(); ++it)
		(*it)->OnEndFrame(frame);
	profiler.EndFrame(m_LastFrameWorkTime);
	return true;
}
```

1. **Line 297:** the queue runs after the work time's clock started, so its functions count as the frame's work.
2. **Lines 311–316:** the minimized frame. The loop asks the window after its events, so the answer reflects what the
   person did a moment ago. A program without a window is never minimized.
3. **Lines 320–333:** the modules' `OnBeginFrame`. The toy had one fixed wait here. Strata asks every module, and the
   first one that answers `Skip` or `Close` ends the frame.
4. **Line 342:** the work time: the time since `frameStart`, minus what the modules reported, minus the stages
   outside the work time, never below zero.
5. **Lines 344–345:** `OnEndFrame` in reverse order, after the measurement. The profiling record of the frame ends
   with the same work time, and a frame that returned early never ends it.

The real drain of the queue is the toy's, line for line.

```cpp src="Strata/src/Strata/Core/Application.cpp#L356-L366" symbol="Application::ExecuteMainThreadQueue"
void Application::ExecuteMainThreadQueue()
{
	std::vector<std::function<void()>> queue;
	{
		std::scoped_lock<std::mutex> lock(m_MainThreadQueueMutex);
		queue.swap(m_MainThreadQueue);
	}

	for (std::function<void()>& function : queue)
		function();
}
```

1. **Lines 358–362:** the lock is held only for the swap. A function that hands in another function therefore does
   not wait for itself, and the new function runs in the next drain.

The `FramePacer` is the toy's three lines of schedule, made into a class whose rate can change. Search it for the test
that keeps the schedule when the rate is the same, and for the line that drops the missed slots.

```cpp src="Strata/src/Strata/Core/Timer.h#L51-L103"
// Keeps a loop at or below a frame rate by sleeping out the rest of each frame's time slot, e.g. for headless
// applications, which have no vsync to pace them. Frames are scheduled at fixed intervals, so a frame that overslept
// is followed by a shorter wait. A frame that ends after the next slot has begun lets the next frame start at once,
// and the schedule continues from there (late frames are not made up with a burst). It waits with Platform::SleepUntil,
// within about a millisecond also on Windows, whose ordinary sleep waits for the system's timer tick.
class FramePacer
{
public:
	// 0: unlimited (WaitForNextFrame returns at once).
	explicit FramePacer(uint32_t maxFrameRate = 0)
	{
		SetMaxFrameRate(maxFrameRate);
	}

	// Another rate starts a new schedule at the next wait; setting the current rate again changes nothing, so a loop
	// may set its rate every frame.
	void SetMaxFrameRate(uint32_t maxFrameRate)
	{
		if (maxFrameRate == m_MaxFrameRate)
			return;
		m_MaxFrameRate = maxFrameRate;
		m_Period = maxFrameRate > 0 ? std::chrono::nanoseconds(1'000'000'000 / maxFrameRate) : std::chrono::nanoseconds(0);
		m_Scheduled = false;
	}

	uint32_t GetMaxFrameRate() const { return m_MaxFrameRate; }

	// Call once per frame, when the frame's work is done: returns when the next frame may start.
	void WaitForNextFrame()
	{
		if (m_MaxFrameRate == 0)
			return;

		const auto now = std::chrono::steady_clock::now();
		if (m_Scheduled)
		{
			m_NextFrame += m_Period;
			if (m_NextFrame < now)
				m_NextFrame = now;
		}
		else
		{
			m_NextFrame = now + m_Period;
			m_Scheduled = true;
		}
		Platform::SleepUntil(m_NextFrame);
	}
private:
	uint32_t m_MaxFrameRate = 0;
	std::chrono::nanoseconds m_Period { 0 };
	std::chrono::steady_clock::time_point m_NextFrame;
	bool m_Scheduled = false;
};
```

1. **Lines 67–74:** `SetMaxFrameRate`. The same rate returns at once. Another rate computes the period and forgets the
   schedule, so the next wait starts a new one.
2. **Line 72:** the period, as a count of `std::chrono::nanoseconds`, of which a second holds 1,000,000,000. At 60
   frames a second it is 1,000,000,000 / 60 = 16,666,666 of them, about 16.7 ms.
3. **Lines 85–95:** the schedule. The next slot is one period after the last. When that moment has passed, the slot
   becomes now, which is how a late frame causes no burst. A wait with no schedule yet places its slot one period
   after now.
4. **Line 96:** the precise sleep. The toy moved its clock forward; the real `FramePacer` asks the system to wake it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Wait for events, and draw only when something changed | Godot, in its low processor usage mode | No processor time at all while the editor is idle | Every change would have to ask for a new frame, and a running game needs frames anyway. Strata lowers its cap while idle instead. |
| Update the game on one thread, and record its drawing on another thread that runs behind it | Unreal Engine, with its game thread and its rendering thread | The two halves of a frame run at the same time on two cores | A copy of the drawing data for each frame, one more frame between input and image, and stricter rules for every module |
| Make the ordinary sleep precise with `timeBeginPeriod` | Windows programs that need short sleeps, as Microsoft's documentation describes | Precise sleeps without a clock of each thread's own | More power use, and on versions of Windows before 10 version 2004, a changed clock for every program on the computer |
| Run at a fixed rate, with no measured step | The oldest form of the game loop, in Game Programming Patterns | The simplest loop | The game runs at another speed on every computer that cannot hold the rate |

## How it is tested

The loop's tests live in `StrataTests/src/Core/`. They run without a window or a graphics card, on applications
without a window and on test modules that write down every hook they receive.

- `Core.Application` (`ApplicationFrameTests.cpp`, `ApplicationPacingTests.cpp`): the work time omits the wait of the
  cap (frames capped at 10 a second) and a 150 ms wait inside the `Present` stage. The profiling record keeps every
  frame with the same work time. Work handed in on the last frame runs before the layers go and can still set the exit
  code. A helper program whose layer throws ends in order with exit code 1. The cap can change while the program runs.
- `Core.EngineModules` (`EngineModuleTests.cpp`): every frame begins, updates and draws the interface of the modules
  in order, and ends them in reverse. A module that skips leaves its frame not counted, and one that closes ends the
  loop. A wait that a module reports stays out of the work time.
- `Core` (`CoreTests.cpp`): two `FramePacer` cases check that a loop stays at or below its rate, that a late frame
  causes no burst, and that the cap switches between a rate and no limit.
- `Perf.FramePacer` (`StrataTests/src/Perf/FramePacerPerfTests.cpp`): how precisely the `FramePacer` holds the
  editor's rates on the computer that runs it. The suite reports and does not fail, and it runs only in `Release` and `Dist`
  builds.

Run a suite with the test program's filter, in the folder of your source build, after a `Debug` build on Windows:

```powershell
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.Application
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.EngineModules
```

Each command prints how many test cases passed. The `Perf.FramePacer` suite runs with `ctest --preset windows-release -L perf` after a `Release` build.

## Changing it safely

Most changes never touch `Application.cpp`. The loop has these points where other code adds to it:

- an engine module's hooks, for a service that needs a place in every frame ([Engine modules](engine-modules.md));
- a layer's `OnUpdate`, for a program's own work in each frame ([Windows, events and layers](windows-events.md));
- `SubmitToMainThread`, for a result from another thread;
- `SetMaxFrameRate`, and the specification's `MaxFrames`, `MaxTimestep` and `MaxFrameRate`.

When you change the loop itself, keep the promises of the contract, because modules and layers rely on each one:

- Keep the order of the stages. The engine's `Docs/Architecture.md` lists it under "Application and frame loop", and
  `Core.EngineModules` checks it.
- Keep waits out of the work time. A new wait in a module goes into `WaitSeconds` or into a stage outside the work
  time. Otherwise a program held back by its cap looks as if the processor were its limit.
- Keep a skipped frame not counted, and keep the clamp in `Run`, not in each caller.
- Keep the drain after the loop before the program's `OnShutdown`, and keep the order of the destructor.

Then run `Core.Application`, `Core.EngineModules` and `Core`. After a change to the `FramePacer`, also run `Perf.FramePacer` in a
`Release` build.

## What went wrong before

Two real bugs shaped the end of the loop and its work time, and each left a regression test.

The first bug was in the drain after the loop. The editor without a graphics card answers a screenshot through the
main-thread queue. When a screenshot was asked for on the last frame, its answer ran only in the application's destructor,
after the editor's layer was gone. The command `StrataEditor --no-gpu --frames 3 --screenshot x.png` logged that the screenshot
failed and then crashed with exit code 139. The exit code that the answer set would have been lost anyway, because
`main` reads it before the destructor runs.

Since then, `Run` drains the queue after its loop. A `Core.Application` case checks that work handed in on the last
frame runs while its layer exists, and that it sets the exit code `main` reads. The command still logs
`Screenshot failed: Image is empty`, since without a graphics card there is no image, and then ends in order with exit
code 1, as the engine's test `StrataEditor.ScreenshotWithoutGPU` expects. In PowerShell, add `| Out-Host` and read
`$LASTEXITCODE`.

The second bug was a wait counted as work. On macOS, the driver hands out the display's image only at its first use,
inside the stage of the user interface. An idle editor at 120 images a second showed that stage at 7.3 ms and a work
time equal to the whole frame. It called itself limited by the processor, which worked less than 1 ms.

Strata now times the first use of the image as the `Present` stage, outside the work time. The same editor then showed
the interface stage at 0.41 ms, `Present` at 7.41 ms and a work time of 0.91 ms. The `Core.Application` case with the
150 ms wait in the `Present` stage keeps it that way.

## Summary

- One frame runs the main-thread queue, the input, the modules' `OnBeginFrame`, the layers' `OnUpdate`, the modules'
  `OnUpdate` and `OnRenderUI`, then `OnEndFrame` in reverse, where the image is presented.
- A minimized window or a module's `Skip` ends the frame with a sleep of 16 ms and no count; its time reaches the next
  step.
- The work time counts the frame up to the last `OnRenderUI`, without the waits the modules report, the stages outside
  the work time, the present and the wait for the next frame.
- The frame-rate cap keeps a fixed schedule: a late frame lets the next one start at once, with no burst afterwards.
- Other threads hand in functions through `SubmitToMainThread`. The main thread runs them at the start of the next
  frame, and once more after the last frame.

## Check yourself

1. Put these in the order of one frame: the layers' `OnUpdate`, `OnEndFrame`, the Input stage, `OnRenderUI`, the
   main-thread queue, `OnBeginFrame`.

   :::answer{tests="frame-order"}
   The main-thread queue, the Input stage, `OnBeginFrame`, the layers' `OnUpdate`, `OnRenderUI`, `OnEndFrame`. The
   modules' `OnUpdate` comes between the layers' update and `OnRenderUI`.
   :::

2. The graphics module answers `Skip` while the images of the window change size. Which hooks of the audio module,
   which comes after it, run in that frame, and does the frame count?

   :::answer{tests="skipped-frame"}
   None of its frame hooks run: the modules after the one that skipped get no `OnBeginFrame`, and no module gets the
   frame's other hooks. Only the events of the Input stage, which comes before, may have reached its `OnEvent`. The
   frame is not counted, the loop sleeps 16 ms, and the next frame's step covers the time from the start of the skipped turn.
   :::

3. A frame starts, waits 5 ms in `OnBeginFrame` for the display, works 6 ms, and spends 1 ms presenting in
   `OnEndFrame`. The frame-rate cap then waits 4 ms. What is its work time?

   :::answer{tests="work-time"}
   The work time is 6 ms. The graphics module reports the 5 ms wait in `WaitSeconds`, and the present and the wait
   for the next frame come after the measurement.
   :::

4. A program is capped at 50 frames a second, and its slots start at 0, 20 and 40 ms. The frame that starts at 40 ms
   ends at 75 ms. When do the next two frames start, if they are short?

   :::answer{tests="frame-pacing"}
   The slot after 40 ms is 60 ms, which has passed at 75 ms, so the next frame starts at once, at 75 ms. The schedule
   continues from there, and the frame after it starts at 95 ms. No frame starts at 80 ms to win back the lost slot.
   :::

5. A job thread finishes loading an image file and wants the scene to use it. Why may it not change the scene itself,
   and what does it do instead?

   :::answer{tests="main-thread-queue"}
   The main thread reads and changes the scene without a lock, so a change from another thread would be a data race.
   The job hands a function to `SubmitToMainThread`, and the main thread runs it at the start of the next frame,
   before the input.
   :::

## Exercises

1. **Basic.** In the toy, change `c_Period` to 10, and predict the start times of turns 1 to 4 before you run it.

   :::answer[Worked solution]{tests="frame-pacing"}
   Turn 1 starts at 0 ms and ends at 9 ms. Its first slot is one period after that, at 19 ms, so turn 2 starts at
   19 ms and ends at 28 ms. The next slot is 29 ms, so turn 3 starts at 29 ms. Turn 3 is minimized and ends at 45 ms,
   after its slot at 39 ms, so turn 4 starts at once, at 45 ms. With slots of 10 ms and frames of 9 ms, the cap waits
   only 1 ms: the frames themselves set the pace.
   :::

2. **Medium.** Trace it yourself. Build the editor in `Debug`, open a project, and set breakpoints at the start of
   `Application::RunFrame` and in the built-in modules' frame hooks. Continue from breakpoint to breakpoint for one
   frame, write down the order, and compare it with the contract.

   :::answer[Worked solution]{tests="frame-order"}
   The loop is `Application::RunFrame` in `Strata/src/Strata/Core/Application.cpp`. The editor's modules are
   Graphics, Audio, [ImGui](../ui/what-game-ui-does.md) and Project, in that order. One frame stops in `GraphicsModule::OnBeginFrame`
   (`Strata/src/Strata/Renderer/GraphicsModule.cpp`), then in `EditorLayer::OnUpdate`
   (`StrataEditor/src/EditorLayer.cpp`), then in `AudioModule::OnUpdate` (`Strata/src/Strata/Audio/AudioModule.cpp`),
   then in `ImGuiModule::OnRenderUI` (`Strata/src/Strata/ImGui/ImGuiModule.cpp`), and last in
   `GraphicsModule::OnEndFrame`. The Project module has no frame hooks, so it never stops. Each breakpoint holds the
   program, so the next frame's step is clamped to 0.25 s.
   :::

3. **Hard.** A module waits 2 ms in its `OnUpdate` for a file to arrive over the network, and does not report the
   wait. The editor is capped at 60 frames a second, and its frames work 8 ms. What does the work time show, what does
   the frame rate show, and what should the module change?

   :::answer[Worked solution]{tests="work-time"}
   The work time shows 10 ms instead of 8 ms, because the wait sits inside the measured part of the frame and nothing
   subtracts it. The frame rate stays at 60, since 10 ms still fits in a slot of 16.7 ms. The module could add its
   2 ms to `frame.WaitSeconds`. Better, it waits on another thread and hands the file to the main thread through
   `SubmitToMainThread`, so that the frame does not wait at all.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Application.cpp`: `Application::Run`, `RunFrame`, `ExecuteMainThreadQueue`,
  `SubmitToMainThread`, the destructor and `ShutDownModules`.
- `Strata/src/Strata/Core/Application.h`: `ApplicationSpecification` (`MaxFrames`, `MaxTimestep`, `MaxFrameRate`),
  `GetLastFrameWorkTime`, `GetFrameCount`, `SetMaxFrameRate`.
- `Strata/src/Strata/Core/Timer.h`: `Timer`, `Time::GetTime`, `FramePacer`; `Strata/src/Strata/Core/Timestep.h`:
  `Timestep`.
- `Strata/src/Strata/Core/EngineModule.h`: `EngineFrame` and its `WaitSeconds`, `EngineFrameAction`, the hooks.
- `Strata/src/Strata/Engine/EntryPoint.h`: `main`, which runs the loop and returns the exit code.
- Tests: `StrataTests/src/Core/ApplicationFrameTests.cpp`, `ApplicationPacingTests.cpp`, `EngineModuleTests.cpp`,
  `CoreTests.cpp`, and `StrataTests/src/Perf/FramePacerPerfTests.cpp`.

## Further reading

- [Robert Nystrom, "Game Loop", in Game Programming Patterns](https://gameprogrammingpatterns.com/game-loop.html): why
  games loop and the common forms of the loop, with drawings; beginner.
- [Glenn Fiedler on fixing the time step](https://gafferongames.com/post/fix_your_timestep/): from a measured step to
  [fixed steps](time.md); intermediate.
- [The Vulkan specification, `VkPresentModeKHR`](https://registry.khronos.org/vulkan/specs/latest/man/html/VkPresentModeKHR.html):
  the present modes, FIFO among them; advanced.
- [Godot, `OS.low_processor_usage_mode`](https://docs.godotengine.org/en/stable/classes/class_os.html#class-os-property-low-processor-usage-mode):
  an engine that draws only when something changed; intermediate.
- [Epic Games, "Threaded Rendering in Unreal Engine"](https://dev.epicgames.com/documentation/en-us/unreal-engine/threaded-rendering-in-unreal-engine):
  a game thread and a thread for drawing that runs behind it; advanced.
- [Microsoft, the `timeBeginPeriod` function](https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timebeginperiod):
  how a Windows program changes the system's clock tick, and what it costs; advanced.
