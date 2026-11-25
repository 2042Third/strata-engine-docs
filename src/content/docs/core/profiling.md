---
id: core/profiling
title: "Measuring the frame: the frame profiler, Tracy and the method"
description: "How Strata times each part of a frame all the time, and how to read the numbers: self time, percentiles and what paces the frame."
kind: internals
size: L
tracks: [E]
needs: [core/jobs]
time: 85
learn:
  - id: self-time
    text: explain how nested stages record self time, and why the stages of a frame never add up to more than the frame
  - id: percentiles
    text: compute the mean, P50 and P95 of a list of frame times by nearest rank, and say what each one shows
  - id: frame-bound
    text: predict from the work, GPU and interval times of a frame whether it is CPU-bound, GPU-bound or capped
  - id: add-stage
    text: add a stage to a layer and read its self time in the Performance panel or through editor.perf
  - id: stage-rules
    text: explain which code a stage may wrap and why a stage inside a job records nothing
since: 0.3.0
status: final
---

A game at 60 :term[frames per second]{id=frame-rate} has 16.7 ms for everything one frame does, and when a frame takes longer, the player sees a hitch. Strata answers where the time went in every build, all the time, for about a microsecond a frame. It splits the :term[main thread's]{id=main-thread} frame into **frame stages**, each a named, timed part of the frame, and keeps the times of the last 600 frames. You learn here how those numbers are made, how to read them and how to add a stage of your own. The page omits benchmarks and budgets ([the performance lab](../engineering/perf-lab.md)), the timestamps of the :term[graphics processing unit]{id=gpu} (GPU) ([GPU timing](../gpu/readback-timing.md)) and how the Performance panel draws itself ([instrument panels](../editor-ui/instrument-panels.md)).

## The problem and how engines solve it

### Where the time went

A game feels slow. A clock around the whole frame says that it takes 24 ms, where 60 frames per second allow 16.7 ms. That one number says nothing else. To fix the game you must split the 24 ms into parts. You must do it with real data, in a game that is running, and without slowing the game down.

### Two kinds of profiler

A **profiler** is a tool that measures where a program spends its time. Two designs exist. A sampling profiler interrupts the program many times a second and writes down which function runs at that moment. After a minute, the functions it saw most often are where the time goes.

A sampling profiler needs no change to the code and sees every function, also those of libraries. Its answer is statistical, so a part that takes 2 ms once a second can escape it, and it knows nothing about frames.

An instrumenting profiler works the other way. A programmer writes markers around the parts to measure, and the profiler reads the clock at the start and at the end of each part. The answer is exact for the marked parts and silent about the rest. Strata uses this design, because its question is "which part of this frame", and a marker can name the part.

### Zones, frame markers and Tracy

An instrumenting profiler calls a marked part of the code a zone: a named span of time on one thread, from its start to its end. Zones nest, as :term[function calls]{id=function-call} do. A frame marker is one more mark, put once per frame, which tells the tool where one frame ends and the next begins. With it the tool can show the time per frame instead of one long stream.

**Tracy** is an open-source instrumenting profiler for games. Your program links a small client library that records zones and sends them over the network to a viewer, a separate program that draws the zones of every thread on a time line. Strata uses Tracy 0.14.1. The client costs time in every zone, and the viewer must run beside the game, so a tester's computer or a shipped game has neither. Strata therefore builds Tracy in only on request, and keeps a second, much smaller layer that is always on.

### Always-on stages and self time

The second layer is the frame stage. Where Tracy sends every zone to a viewer, the engine adds up the time of each stage per frame into a few numbers and keeps the last 600 frames in memory. Each stage costs two clock reads and a few additions. The test `Perf.FrameProfiler` measures about 0.6 microseconds for a whole frame of 16 stages, which is 0.004 % of a frame at 60 frames per second. Because the numbers are always there, the editor, a command and a log file can show them without a special build.

Stages nest: while the scene :term[renderer]{id=renderer} extracts draws, the rendering stage is still open around it. The time inside the inner stage then belongs to two stages. If both counted it, the stages of a frame would add up to more than the frame. Strata therefore keeps for each stage its **self time**, the time spent in the stage without the time of the stages nested in it. The **inclusive time** of a stage is its time with the nested ones.

The picture shows one outer stage with one stage nested in it. The outer stage runs for 2.0 ms, the inner one for 3.0 ms, and the outer one for 1.0 ms more.

```mermaid caption="Time runs from left to right. The outer stage pauses while the inner stage runs, so the outer stage's self time is its two boxes added together." alt="Three boxes in a row. The first, an outer stage, runs 2.0 ms. The second, an inner stage nested in the outer one, runs 3.0 ms. The third is the outer stage again, 1.0 ms."
flowchart LR
	a["Outer stage<br/>2.0 ms"] --> b["Inner stage<br/>3.0 ms<br/>(outer is paused)"] --> c["Outer stage<br/>1.0 ms"]
```

The inclusive time of the outer stage is 2.0 + 3.0 + 1.0 = 6.0 ms. Its self time is 2.0 + 1.0 = 3.0 ms. The inner stage has a self time of 3.0 ms. The self times add up to 3.0 + 3.0 = 6.0 ms, the real time that passed; the inclusive times add up to 9.0 ms, which counts the inner stage twice. That is why the panel can stack self times into one bar whose height is the frame.

## The map: from a stage to a number on the screen

Everything on the page follows the path in the diagram. The main thread drives the profiler, the stages feed it, and every reader takes its numbers from the ring of recorded frames.

```mermaid caption="The main thread feeds the frame profiler; the graphics side adds its times later; every reader takes numbers from the ring of recorded frames." alt="A diagram. The main thread's frame function and the stage scopes feed the frame profiler, and so do the job system's statistics. The graphics profiler attaches times some frames later. The profiler keeps a ring of frames, which feeds summaries, snapshots and listeners. Summaries feed the Performance panel, the status bar and the editor perf command."
flowchart TD
	run["Application::RunFrame"] -->|"BeginFrame, EndFrame(work time)"| profiler["FrameProfiler"]
	scopes["ST_PROFILE_STAGE scopes"] -->|"BeginStage, EndStage"| profiler
	jobs["JobSystem::GetStats"] -->|"busy time of the pools"| profiler
	gpu["GPUProfiler"] -.->|"RecordGPUFrame, frames later"| profiler
	profiler --> ring["ring of 600 frames"]
	ring --> summarize["Summarize: mean, P50, P95, max"]
	ring --> snapshot["TakeSnapshot: a copy"]
	ring --> listeners["frame listeners"]
	summarize --> panel["Performance panel, status bar"]
	summarize --> perf["editor.perf"]
	snapshot --> panel
```

Only the main thread writes to the profiler. `Application::RunFrame` begins a frame, the stage scopes add time to it, and the frame ends with the :term[work time]{id=work-time} that the :term[frame loop]{id=game-loop} measured. The end of a frame also asks `JobSystem::GetStats` how long the job system's threads were busy, as [the job system](jobs.md) counts. The graphics side works on another schedule: the GPU finishes a frame some frames after the main thread recorded it, and its times arrive then. The ring replaces its oldest frame with each new one, so memory use never grows.

## The contract

The profiler is a small class with strict rules. This section states them, each with its reason. Where a rule needs a number, the number is in the code at the pin: `Strata/src/Strata/Core/FrameProfiler.h` holds the class and `Strata/src/Strata/Core/Profiling.h` the :term[macros]{id=macro}.

### The Tracy macros

Four macros mark Tracy zones. They are written in the code once and cost nothing in a normal build.

- `ST_PROFILE_FRAME()` marks the end of a frame; `Application::Run` calls it at the top of every turn of the loop.
- `ST_PROFILE_FUNCTION()` makes a zone named after the function, from the line to the end of the scope.
- `ST_PROFILE_SCOPE(name)` makes a zone with a name you choose, a constant string, for the rest of the scope.
- `ST_PROFILE_THREAD(name)` names the calling thread in the viewer. At the pin, no engine code calls it.

All four compile to nothing unless the engine is configured with `-DSTRATA_ENABLE_TRACY=ON`; the option is off by default. With it on, :term[CMake]{id=cmake} builds Tracy's client library, defines `ST_ENABLE_TRACY` for the core library, and uses Tracy's on-demand mode, in which the client sends data only while a viewer is connected. A shipped game thus carries no zones, and the zones in hot code cost nothing until someone profiles.

### Frame stages and the twelve built-in ones

`ST_PROFILE_STAGE("Name")` is different from the four: it is always on, in every build. It times the rest of its scope as a stage called `Name`, and with Tracy it is also a zone of that name. The profiler registers twelve stages first, in this order, so their ids are their positions:

- `Input`: the input and the window's events.
- `Assets.Update`: the asset manager's update for the frame.
- `Assets.Finalize`: finishing loaded assets on the main thread, including uploads to the graphics card.
- `Scene.Load`: the main-thread work of loading scenes.
- `Scene.Scripts`: the :term[callbacks]{id=callback} of the scripting system.
- `Scene.Physics`: stepping the physics and its contact callbacks.
- `Scene.Audio`: the audio system.
- `Scene.Transforms`: refreshing the scene's world transforms.
- `Render.Extract`: gathering lights, draws and shadow casters from the scene.
- `Render.Submit`: recording and submitting the renderer's commands.
- `Editor.UI`: drawing the interface with ImGui.
- `Present`: presenting the finished image, which lies outside the work time.

`Present` is the only built-in stage outside the work time, because presenting can wait for the display, and a wait is no work. [The upload queue](../gpu/upload-queue.md) explains that wait. Scene systems, the game's user interface (UI) and the editor add five more stages: `Scene.UI`, `Scene.Animation`, `World.Streaming`, `Render.UI` and `Editor.Commands`. The generated table on [the performance reference](../reference/performance.md) lists every stage of the main thread. The stages the graphics card owns are a different kind, taken up below.

### What a stage may wrap

A stage records time only on the frame thread, inside a frame. The profiler checks this in `BeginStage`: a call from a worker thread, or between `EndFrame` and the next `BeginFrame`, returns at once and records nothing. So a stage written inside a job records nothing; with Tracy, its zone still appears on the worker. Time spent in jobs shows as the pools' busy shares instead.

Three more limits protect the numbers. A stage nested more than 32 deep is not timed, and its time counts for the stage around it. The table holds 64 stages, those of the :term[central processing unit]{id=processor} (CPU) and of the GPU together; the 65th name gets an invalid id, one warning in the log, and no timing. A stage that is still open when a frame ends counts up to that moment, and continues in the next frame.

:::rule[Wrap a unit of frame work]
A stage goes around a unit of the frame's work, such as one system's update, and never around calls that take nanoseconds. The reason is the accounting. Every entry and exit reads the clock and changes the stack, so a stage inside a loop of 50,000 calls costs more than the calls. It also fills one of the 64 slots with a name nobody reads. For the same reason `Scene::UpdateWorldTransforms` times only the updates that calculate something.
:::

### Summaries, snapshots and listeners

`FrameProfiler::Summarize(frames)` turns the latest frames into statistics. It covers the work time, the interval between frames, the sum of the stages, the rest of the frame that no stage accounts for, and each stage's self time. For each of these it gives the mean, the P50, the P95 and the maximum (the next section explains them).

The summary also holds the busy shares of the job system's pools. For each frame the profiler takes the busy time that the pool's threads added since the previous frame, and divides it by the time that passed, times the number of threads. It clamps the result to 0 to 100 %, and the summary averages the frames.

A listener is a function the profiler calls for every recorded frame, for code that needs each frame and not a summary. `StrataRuntime` uses two to write its perf log, one row per frame. A listener of the kind `WithGPU` waits until the frame's graphics times are attached, but at most eight frames. A snapshot is a copy of the ring up to one frame, about 331 KB for a full ring. The Performance panel takes one when you pause it, so that the numbers hold still while the profiler keeps recording.

## Percentiles: reading a frame's times

You know the average: add the samples and divide by their count. The summaries show it as the mean, the column **Avg ms**. When all frames take about the same time, the mean describes them well. When a few frames are far longer, it hides them, as a story shows.

Take twenty frames on a display that shows 60 images a second: sixteen frames take 16 ms, two take 17 ms and two take 50 ms. The times add up to 16 × 16 + 2 × 17 + 2 × 50 = 390 ms, so the mean is 390 / 20 = 19.5 ms, which is 51 frames per second. That looks like a game that is slightly slow but smooth. The player sees something else: two hitches in 0.39 s.

To see the hitches, sort the twenty times from the smallest to the largest: sixteen 16s, then 17, 17, 50, 50. The **median** is the middle sample of the sorted list: half of the frames take no longer. It is also called the 50th percentile, or P50. A **percentile** with a share $p$ is the sample that this share of all samples does not exceed. The 95th percentile, **P95**, is the time that 95 of 100 frames stay within.

With twenty samples the middle lies between the 10th and the 11th. Strata uses **nearest rank**: it counts the samples from the smallest, starting at 1, and takes the sample at the rank in this formula.

$$r = \lceil p \times n \rceil$$

Here $r$ is the rank of the sample and $n$ is the number of samples. The share $p$ is a fraction: 0.50 for P50 and 0.95 for P95. The brackets round up to a whole number.

For twenty samples the rank of P50 is $\lceil 0.50 \times 20 \rceil = 10$, and the rank of P95 is $\lceil 0.95 \times 20 \rceil = 19$. Check the limits: one sample gives rank 1 for every share, so the mean, P50, P95 and maximum are all that sample; a share of 1 gives the rank $n$, the maximum. A list with no samples gives zeros. Nearest rank never invents a value between two samples, so every percentile is a frame that really happened, and you can find it in the data.

The sketch repeats the arithmetic for the twenty frames. Read its list of times, then predict the four numbers before you read the output below it, which shows what each number says about the same frames.

```cpp sketch="core-profiling-percentiles.cpp"
// Mean, P50, P95 and maximum of frame times by nearest rank, and what paces the frames.
#include <algorithm>
#include <cstdio>
#include <vector>

namespace
{
	// The sample at rank ceil(percent * count / 100), counting from 1 at the smallest (whole numbers: no rounding error).
	float AtRank(const std::vector<float>& sorted, size_t percent)
	{
		const size_t rank = (sorted.size() * percent + 99) / 100;
		return sorted[std::max<size_t>(rank, 1) - 1];
	}
}

int main()
{
	// Twenty frames of a game on a 60 Hz display, in milliseconds.
	std::vector<float> frames(20, 16.0f);
	frames[3] = 17.0f;
	frames[8] = 17.0f;
	frames[11] = 50.0f;
	frames[15] = 50.0f;

	float sum = 0.0f;
	for (const float frame : frames)
		sum += frame;
	std::sort(frames.begin(), frames.end());

	const float p50 = AtRank(frames, 50);
	const float p95 = AtRank(frames, 95);
	std::printf("mean %.1f ms, P50 %.1f ms, P95 %.1f ms, max %.1f ms\n", sum / 20.0f, p50, p95, frames.back());

	// The classification of the medians: work 15.5 ms, GPU busy 6.0 ms, interval 16.7 ms.
	const float work = 15.5f;
	const float gpu = 6.0f;
	const float interval = 16.7f;
	const bool gpuBound = gpu >= 0.9f * interval && gpu > work;
	const bool cpuBound = work >= 0.9f * interval;
	std::printf("bound at %.2f ms: %s\n", 0.9f * interval, gpuBound ? "GPU" : (cpuBound ? "CPU" : "Capped"));
	return 0;
}
```

```text output-of="core-profiling-percentiles.cpp"
mean 19.5 ms, P50 16.0 ms, P95 50.0 ms, max 50.0 ms
bound at 15.03 ms: CPU
```

1. **Lines 8–12:** nearest rank in whole numbers, the way the engine does it, so no :term[rounding error]{id=rounding-error} can move the rank.
2. **Lines 19–23:** the twenty frames: sixteen of 16 ms, two of 17 ms and two of 50 ms.
3. **Lines 28–31:** sort the times, then take the samples at the ranks of P50 and P95.
4. **Lines 34–40:** the 90 % rule of the next section, for the medians of one example.

The mean of 19.5 ms suggests 51 frames per second. P50 says that a typical frame takes 16 ms. P95 says that the slowest frames take 50 ms. Read P50 alone and you miss the hitches; that is the most common mistake with these numbers.

Read the maximum alone and one bad frame in 600 alarms you, although a game can live with it. P95 sits between them: it ignores the 30 worst of 600 frames, and it shows any trouble that touches more than one frame in twenty. A rare single spike still needs the maximum.

A stage's row uses the same statistics over its self time in each frame, and a frame in which the stage did not run counts as 0. A stage that runs in 4 frames of 10 has a P50 of 0, a small mean and a large maximum. Read its P95 and its maximum, and ask how often it runs.

## CPU, GPU or capped

When a game runs too slowly, the first question is which side is the slow one: the CPU, the GPU or neither. [The map of an engine's frame](../start/what-an-engine-is.md) shows the two sides working on different frames: the CPU prepares frame 41 while the GPU draws frame 40. They overlap, so the frame rate is set by the slower side. If both finish early and wait for the display, the pace comes from the wait.

Three numbers answer the question. The work time of a frame is the CPU's time without its waits, as [the frame loop](frame-loop.md) defines it. The interval is the time from the start of a frame to the start of the next one. The GPU's busy time is the time of the GPU's stages in that frame added up. From them, Strata names what limits the frame rate:

- **CPU-bound**: the CPU's work takes at least 90 % of the interval, so the GPU waits for the CPU.
- **GPU-bound**: the GPU's busy time takes at least 90 % of the interval and is longer than the work time, so the CPU waits for the GPU.
- **Capped**: neither is true, so something else sets the pace: :term[vsync]{id=vsync}, a :term[frame-rate cap]{id=frame-rate-cap} or idle throttling.

Take a display at 60 Hz. The interval is 16.7 ms, and 90 % of it is 15.0 ms. Four frames show the rules:

- Work 6 ms, GPU busy 7 ms: capped. Both sides finish early, and the display sets the 16.7 ms.
- Work 16 ms, GPU busy 8 ms: CPU-bound, because 16 is more than 15.
- Work 9 ms, GPU busy 16 ms: GPU-bound, because 16 is more than 15 and more than 9.
- Work 16.2 ms, GPU busy 16 ms: CPU-bound, not GPU-bound, because the GPU's time does not exceed the work time.

Strata asks the question of the medians of the summarized frames, not of single frames. The reason is stability: if one frame in 120 takes 60 ms, the medians do not change, and the verdict stays. The answer is Unknown when there are no GPU times, for example when the GPU writes no timestamps. The function is short:

```cpp src="Strata/src/Strata/Core/FrameProfiler.cpp#L603-L612" symbol="FrameProfiler::ClassifyFrameBound"
FrameBound FrameProfiler::ClassifyFrameBound(float workMs, float gpuBusyMs, float intervalMs)
{
	if (intervalMs <= 0.0f)
		return FrameBound::Unknown;
	if (gpuBusyMs >= c_BoundShare * intervalMs && gpuBusyMs > workMs)
		return FrameBound::GPU;
	if (workMs >= c_BoundShare * intervalMs)
		return FrameBound::CPU;
	return FrameBound::Capped;
}
```

1. **Line 605:** with no interval there is nothing to compare, so the answer is Unknown.
2. **Line 607:** the GPU rule comes first: its busy time must reach 90 % of the interval and exceed the work time.
3. **Line 609:** the CPU rule: the work time reaches 90 % of the interval.
4. **Line 611:** what is left is capped.

The GPU's times come late. The card writes timestamps while it draws a frame, and the renderer can read them only after the card has finished that frame, a few frames after the CPU recorded it. `editor.perf` describes them as known two to three frames late.

The profiler therefore records a frame without GPU times. The renderer attaches them later with `RecordGPUFrame`, while the frame is still in the ring, and a frame that has left the ring takes none. GPU stages are never part of the work time or of the stage sum, and a summary counts one only over the frames whose times arrived. [GPU timing](../gpu/readback-timing.md) teaches how the card's timestamps are read back.

## A toy version

The toy is the heart of the real code: stages that nest, a fixed-depth stack and self time. Its clock is simulated, in microseconds, so the output is the same on every computer.

The program runs `Update` for 2 ms. `Physics` then runs for 3 ms inside it, and `Render` for 1 ms inside that. `Extra` would run for 0.5 ms as a fourth level, but the stack holds three levels. After that, `Update` runs 1 ms more. Predict the four self times before you read the output.

```cpp sketch="core-profiling-toy.cpp"
// A toy stage timer: stages nest, and each one records only its own time (its self time).
// The clock is simulated in whole microseconds, so the output is the same on every machine.
#include <cstdint>
#include <cstdio>

namespace
{
	constexpr uint32_t c_StageCount = 4;
	constexpr uint32_t c_MaxDepth = 3;
	constexpr const char* c_Names[c_StageCount] = { "Update", "Physics", "Render", "Extra" };
	int64_t s_Now = 0; // the simulated clock, in microseconds

	struct OpenStage
	{
		uint32_t Stage = 0;
		int64_t Start = 0;
	};

	int64_t s_SelfTime[c_StageCount] = {};
	OpenStage s_Open[c_MaxDepth] = {};
	uint32_t s_Depth = 0;

	// Returns whether the stage was entered: only then must EndStage follow.
	bool BeginStage(uint32_t stage)
	{
		if (s_Depth == c_MaxDepth)
			return false; // too deep: its time counts for the stage around it
		if (s_Depth > 0) // the stage around this one pauses
			s_SelfTime[s_Open[s_Depth - 1].Stage] += s_Now - s_Open[s_Depth - 1].Start;
		s_Open[s_Depth++] = { stage, s_Now };
		return true;
	}

	void EndStage()
	{
		const OpenStage& inner = s_Open[--s_Depth];
		s_SelfTime[inner.Stage] += s_Now - inner.Start;
		if (s_Depth > 0) // the stage around it resumes
			s_Open[s_Depth - 1].Start = s_Now;
	}

	class StageScope
	{
	public:
		explicit StageScope(uint32_t stage)
			: m_Active(BeginStage(stage))
		{
		}

		~StageScope()
		{
			if (m_Active)
				EndStage();
		}
	private:
		bool m_Active;
	};
}

int main()
{
	{
		StageScope update(0);
		s_Now += 2000;
		{
			StageScope physics(1);
			s_Now += 3000;
			{
				StageScope render(2);
				s_Now += 1000;
				StageScope extra(3); // a fourth level: not timed
				s_Now += 500;
			}
		}
		s_Now += 1000;
	}
	for (uint32_t stage = 0; stage < c_StageCount; stage++)
		std::printf("%-8s %.1f ms\n", c_Names[stage], static_cast<double>(s_SelfTime[stage]) / 1000.0);
	std::printf("elapsed  %.1f ms\n", static_cast<double>(s_Now) / 1000.0);
}
```

```text output-of="core-profiling-toy.cpp"
Update   3.0 ms
Physics  3.0 ms
Render   1.5 ms
Extra    0.0 ms
elapsed  7.5 ms
```

1. **Lines 26–27:** with the stack full, the stage is not entered, and its time stays with the stage around it.
2. **Lines 28–30:** the stage around this one pauses, so its time so far is added; then the new stage is pushed with the current time.
3. **Lines 36–39:** the inner stage ends and adds its time, and the stage around it resumes from now.
4. **Lines 50–54:** the :term[destructor]{id=destructor} ends the stage only if it was entered, so a scope cannot forget to end.

`Update` has 3.0 ms of its own, the two parts before and after `Physics`. `Physics` has 3.0 ms. `Render` shows 1.5 ms: its own 1.0 ms and the 0.5 ms of `Extra`, which was not timed because the stack was full. The self times add up to 7.5 ms, the time that passed.

The real code is this idea at full strength. It has a stack that stays small and a table of results that many readers share. Its scope cleans up by itself, in the style named :term[resource acquisition is initialization]{id=raii} (RAII).

## The real code

The real code differs from the toy in four ways. Ids come from a table of names, and a stage is registered once per place in the code. The clock is read through `Now()`, so tests can replace it, and a stage is entered only when the thread and the frame are right. Start with the macro, and notice the `static` variable: it is why registering costs one lookup per place in the code, not one per frame.

```cpp src="Strata/src/Strata/Core/Profiling.h#L37-L42"
#endif

#define ST_PROFILE_STAGE(name) \
static const ::Strata::FrameStageID ST_PROFILE_CONCAT(s_FrameStage, __LINE__) = ::Strata::FrameProfiler::Get().RegisterStage(name); \
const ::Strata::FrameStageScope ST_PROFILE_CONCAT(frameStageScope, __LINE__)(::Strata::FrameProfiler::Get(), ST_PROFILE_CONCAT(s_FrameStage, __LINE__)); \
ST_PROFILE_STAGE_ZONE(name)
```

The macro makes three things from one line:

- a `static const` id, set from the name the first time the line runs;
- a scope object that times the rest of the block;
- the Tracy zone, which is empty without Tracy.

Both names carry `__LINE__`, so two stages can stand in one block. Many places can use one name, as `Render.Extract` is used in ten places: `RegisterStage` finds the name and returns the same id, and the times add up.

The scope class is the RAII part. Its :term[constructor]{id=constructor} asks `BeginStage` whether the stage was entered, and its :term[destructor]{id=destructor} ends the stage only then.

```cpp src="Strata/src/Strata/Core/FrameProfiler.h#L386-L406"
// Times a stage of the frame for as long as it lives (see FrameProfiler; ST_PROFILE_STAGE makes one).
class FrameStageScope
{
public:
	FrameStageScope(FrameProfiler& profiler, FrameStageID stage)
		: m_Profiler(profiler), m_Active(profiler.BeginStage(stage))
	{
	}

	~FrameStageScope()
	{
		if (m_Active)
			m_Profiler.EndStage();
	}

	FrameStageScope(const FrameStageScope&) = delete;
	FrameStageScope& operator=(const FrameStageScope&) = delete;
private:
	FrameProfiler& m_Profiler;
	bool m_Active = false;
};
```

1. **Lines 390–393:** the constructor asks `BeginStage` and remembers the answer.
2. **Lines 395–399:** the destructor ends the stage only when it was entered.
3. **Lines 401–402:** copying is deleted, so one entry can never be ended twice.

`BeginStage` and `EndStage` are the toy's two functions with guards. Notice the first condition of `BeginStage`, which is the rule of the frame thread.

```cpp src="Strata/src/Strata/Core/FrameProfiler.cpp#L409-L422" symbol="FrameProfiler::BeginStage"
bool FrameProfiler::BeginStage(FrameStageID stage)
{
	if (!IsTimingThisThread() || stage >= GetStageCount() || m_Depth == c_MaxDepth || m_StageKinds[stage] != FrameStageKind::CPU)
		return false;
	const int64_t now = Now();
	// The stage around this one pauses: its self time excludes this one's.
	if (m_Depth > 0)
	{
		OpenStage& outer = m_Open[m_Depth - 1];
		m_Accumulated[outer.Stage] += now - outer.Start;
	}
	m_Open[m_Depth++] = OpenStage { stage, now };
	return true;
}
```

1. **Line 411:** the guard: the frame thread, inside a frame, a registered CPU stage, and a stack below its depth limit.
2. **Lines 414–418:** the stage around this one pauses: its time so far is added to its own total.
3. **Line 420:** the new stage is pushed with the current time.

`EndStage` is the other half.

```cpp src="Strata/src/Strata/Core/FrameProfiler.cpp#L424-L434" symbol="FrameProfiler::EndStage"
void FrameProfiler::EndStage()
{
	if (m_Depth == 0 || !IsFrameThread())
		return;
	const int64_t now = Now();
	const OpenStage& inner = m_Open[--m_Depth];
	m_Accumulated[inner.Stage] += now - inner.Start;
	// The stage around it resumes.
	if (m_Depth > 0)
		m_Open[m_Depth - 1].Start = now;
}
```

1. **Lines 426–427:** a call from another thread, or with no stage open, changes nothing.
2. **Lines 429–430:** the inner stage leaves the stack and adds its time.
3. **Lines 431–433:** the stage around it resumes counting from now.

`ComputeStatsInPlace` finds the percentiles. The editor summarizes up to 600 frames for every stage while it draws, so sorting every row in full would cost more than the answer needs. Notice how the second search starts after the first.

```cpp src="Strata/src/Strata/Core/FrameProfiler.cpp#L503-L516" overload="2" from="// Nearest rank: the sample at rank" to="stats.P95 = *p95;" symbol="FrameProfiler::ComputeStatsInPlace"
// Nearest rank: the sample at rank ceil(p * n) (1-based), found without sorting everything. nth_element leaves the
// samples after the median's position no smaller than the median, and the 95th percentile's rank is at least the
// median's, so the second search looks only there.
const auto atRank = [&values](size_t percent)
{
	const size_t rank = std::max<size_t>((values.size() * percent + 99) / 100, 1);
	return values.begin() + static_cast<std::ptrdiff_t>(rank - 1);
};
const auto median = atRank(50);
std::nth_element(values.begin(), median, values.end());
stats.P50 = *median;
const auto p95 = atRank(95);
std::nth_element(median, p95, values.end());
stats.P95 = *p95;
```

1. **Lines 506–510:** the rank by the formula of nearest rank, in whole numbers, as an :term[iterator]{id=iterator} into the samples.
2. **Lines 511–513:** `std::nth_element` puts the median sample at its place, without sorting the rest.
3. **Lines 514–516:** the second search starts at the median, because the rank of P95 is never lower.

## A stage of your own

:::example[A stage in a layer, nested, read in the panel]
You write an application on the engine, and its layer's `OnUpdate` runs a function that takes about 4.0 ms. You want to see it in the Performance panel. Add one line at the top of the function, and a second one around the part that finds paths:

```pseudocode
void MyLayer::OnUpdate(Timestep timestep)
{
	ST_PROFILE_STAGE("Game.MyWork");   // include Strata/src/Strata/Core/Profiling.h
	UpdateEnemies();                   // 2.5 ms of its own
	{
		ST_PROFILE_STAGE("Game.Pathfinding");
		FindPaths();                   // 1.5 ms
	}
}
```

Build and run, and the stage registers the first time the line runs. In the panel's table, `Game.MyWork` has a self time of 2.5 ms and `Game.Pathfinding` 1.5 ms. The inclusive time of `Game.MyWork`, 4.0 ms, appears nowhere, by design. The row **Untimed (rest of the frame)** shrinks by 4.0 ms, because the stage sum grew by that much. Without the nested stage, the one stage would show 4.0 ms, and you would not know that a third of it is path finding.
:::

The same numbers come through a command. The one line below asks the editor, which must be running, for the statistics of the latest 120 frames. The command answers within its own frame, from the frames the profiler already recorded (at most 600), so it never waits. With fewer recorded, it answers with fewer, and `frames` says how many. [The editor commands](../editor/commands.md) teach how to read and run a command.

::::tabs{sync=os}
:::tab[Windows]
Windows PowerShell 5.1 drops the quotes inside a JSON argument, so pipe the parameters in: the `-` reads them from :term[standard input]{id=standard-input}.

```powershell
'{ "frames": 120 }' | StrataCLI call editor.perf -
```

`StrataCLI` prints the result as JSON.
:::
:::tab[Linux]

```sh
StrataCLI call editor.perf '{"frames": 120}'
```

`StrataCLI` prints the result as JSON.
:::
:::tab[macOS]

```sh
StrataCLI call editor.perf '{"frames": 120}'
```

`StrataCLI` prints the result as JSON.
:::
::::

The result has the fields `frames`, `frame`, `framesPerSecond`, `interval`, `stageSum`, `untimed`, `stages` (each with `avgMs`, `p50Ms`, `p95Ms`, `maxMs` and `inFrameTime`), `jobs` and `gpu`, whose `boundBy` field holds `cpu`, `gpu`, `capped` or `unknown`. The fields `renderStats` and `gameRenderStats` describe the latest frame of the Scene view and of the Game view, and are null while a view draws nothing. An editor started with `--headless` draws its views only for pictures, and one started with `--no-gpu` has no graphics device. In both, the two fields are null, and `boundBy` reads `unknown` once the frames asked for hold no GPU times.

The Performance panel shows the same statistics as stacked bars over time and a table with the columns **Avg ms**, **p50 ms**, **p95 ms** and **Max ms**. A copy button in the panel copies `editor.perf`'s JSON for you to paste. The **Pause** button takes a snapshot, so the numbers stop moving while the game continues.

The figure shows the panel while the game plays.

::figure{id=performance-panel variant=playing crop=top}

The status bar's frame pill shows the work time and the frame rate. Hold the pointer over it, and a text says CPU-bound, GPU-bound or Capped for the last 120 frames; a click opens the panel.

::figure{id=frame-pill}

A text figure shows part of the command's real result for a playing game, taken in an editor started with `--no-gpu`. The figure keeps `frames`, `frame`, `interval`, `stageSum` and one stage; the full result lists every stage of the main thread and holds the other fields too.

```text capture="editor-perf-json"
{
  "frames": 60,
  "frame": {
    "avgMs": 1.0835000276565552,
    "maxMs": 1.6119999885559082,
    "p50Ms": 1.083299994468689,
    "p95Ms": 1.2860000133514404
  },
  "interval": {
    "avgMs": 1.6704349517822266,
    "maxMs": 17.98040008544922,
    "p50Ms": 1.0917999744415283,
    "p95Ms": 1.4320000410079956
  },
  "stageSum": {
    "avgMs": 1.0733516216278076,
    "maxMs": 1.604200005531311,
    "p50Ms": 1.0742000341415405,
    "p95Ms": 1.2782000303268433
  },
  "stages": {
    "Scene.Physics": {
      "avgMs": 0.7026150226593018,
      "inFrameTime": true,
      "maxMs": 1.0566999912261963,
      "p50Ms": 0.7008000016212463,
      "p95Ms": 0.8729000091552734
    }
  }
}
```

1. **Line 2:** the number of frames the summary covers.
2. **Lines 3–7:** the work time of a frame: mean, maximum, median and 95th percentile, in milliseconds.
3. **Lines 9–13:** the same four numbers for the interval between frames; here its maximum is far above its median: one gap between frames was long, though no frame's work time (line 5) was.
4. **Lines 15–19:** the same four numbers for the sum of all stages.
5. **Lines 21–28:** one entry per stage; the figure keeps only `Scene.Physics` of them, and `inFrameTime` says its time counts in the frame's work time.

With the editor built with Tracy, the same frame appears in the viewer. Every stage is a zone on the main thread, and the zones of `ST_PROFILE_SCOPE` and `ST_PROFILE_FUNCTION` lie inside a stage or on the row of the worker thread that ran them. The sketch shows how the viewer lays out one frame; it is drawn from the code, not captured.

::figure{id=tracy-frame}

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Sampling profiler only | Linux perf, Visual Studio's profiler | No markers to write, and every function seen, also in libraries | Frames as a unit, exact stage times and any use inside a shipped game |
| Tracy zones only | Many engines that link Tracy | A complete view of every thread, with no home-made code | Numbers in a build without Tracy, and a summary the editor and a command can read |
| Trace files of every frame | Unreal Insights, Unity's Profiler recordings | Every frame kept for later analysis, not only the last 600 | A fixed memory use, and an answer within one frame of the command |
| The mean as the only statistic | Many on-screen frame counters | One number, simple to chart and compare | The hitches that P95 and the maximum show |

## How it is tested

The suite `Core.FrameProfiler` in `StrataTests/src/Core/FrameProfilerTests.cpp` drives the profiler with a clock the test controls, so every time is exact. Its cases check:

- nested self time, stages outside the work time and the frame thread rule;
- a frame that begins and never ends, and the ring;
- percentiles by nearest rank, also in place and with repeated samples;
- late GPU times, listeners and snapshots;
- the 64-stage limit, and what bounds the frames: the case "What bounds the frames follows the 90% rules" holds the values of the example above.

`Editor.Perf` in `StrataTests/src/Editor/EditorProfilerTests.cpp` runs `editor.perf` on the playing feature scene and checks that command work shows as the `Editor.Commands` stage. `Perf.FrameProfiler` measures the cost per frame; it runs only in `Release` and `Dist` builds.

```powershell
build/windows/bin/Debug/StrataTests.exe --test-suite=Core.FrameProfiler
```

The command runs the profiler's cases and prints how many passed.

## Changing it safely

Most changes add a stage, and that needs no change to the profiler. Follow this list.

- Put the stage around a unit of work on the frame thread, and give it a name of the form `Group.Name`. A stage in code that runs in some frames only shows zeros in the others, which the statistics handle.
- Register a stage that a program should log from its first frame when its module registers, as the game UI does for `Render.UI`. A stage that first registers after a perf log wrote its header gets no column.
- Count the 64 slots. GPU stages use them too, so a module that adds many stages must check `RegisterStage` for `c_InvalidFrameStage`.
- Never read the profiler from another thread except for `RegisterStage`, `FindStage` and the stage names. The ring belongs to the frame thread.
- A change to the 90 % rule, the percentiles or the order of the built-in stages needs a change of the test that holds the same numbers, and of the docs that quote them.

A change to a stage name touches `editor.perf`'s result and every perf log column, so a script that reads them must change in the same commit. Run `Core.FrameProfiler` and `Editor.Perf`, and run `Perf.FrameProfiler` in a `Release` build when you touch the scope or the stack.

## Summary

- A nested stage records its self time, the time without the stages inside it, so a frame's stages never add up to more than the frame; the inclusive time counts the inner stage twice.
- The mean hides hitches. P50 is the typical frame, P95 the time that 19 frames in 20 stay within, and nearest rank takes the sample at rank $\lceil p \times n \rceil$.
- A frame is CPU-bound when the median work time is at least 90 % of the median interval. It is GPU-bound when the median GPU busy time reaches that share and exceeds the work time, and capped otherwise.
- `ST_PROFILE_STAGE("Group.Name")` adds an always-on stage that the Performance panel, the status bar and `editor.perf` show; `ST_PROFILE_SCOPE` and its kin add Tracy zones only in a Tracy build.
- A stage counts only on the frame thread, inside a frame; a stage in a job records nothing, and a stage around calls of nanoseconds costs more than it shows.

## Check yourself

1. A frame has an outer stage `A` of 10 ms inclusive. Inside it, `B` takes 4 ms inclusive, and inside `B`, `C` takes 1 ms. What is each stage's self time?

   :::answer{tests="self-time"}
   `C` has 1 ms. `B` has 4 − 1 = 3 ms. `A` has 10 − 4 = 6 ms. The three self times add up to 10 ms, the time of `A`; adding the inclusive times, 10 + 4 + 1, would count `B` and `C` more than once.
   :::

2. Ten frames take 12, 12, 13, 12, 14, 12, 13, 40, 12 and 13 ms. Compute the mean, P50 and P95.

   :::answer{tests="percentiles"}
   The sum is 153 ms, so the mean is 15.3 ms. Sorted, the list is 12 (five times), 13 (three times), 14 and 40. The rank of P50 is $\lceil 0.5 \times 10 \rceil = 5$, so P50 is 12 ms. The rank of P95 is $\lceil 9.5 \rceil = 10$, so P95 is 40 ms, the largest sample. The mean 15.3 ms and the P50 hide the one 40 ms hitch that P95 shows.
   :::

3. The medians are an interval of 16.7 ms, a work time of 8 ms and a GPU busy time of 16 ms. Which answer is right: (a) CPU-bound, because the CPU prepares the frame; (b) GPU-bound; (c) capped, because the work time is below 15 ms; (d) unknown?

   :::answer{tests="frame-bound"}
   (b). The GPU's 16 ms is at least 90 % of 16.7 ms, which is 15.0 ms, and it is longer than the work time of 8 ms. Answer (a) confuses who prepares the frame with who limits it. Answer (c) forgets that the GPU can reach the 90 % share too. Answer (d) is right only when no GPU times exist.
   :::

4. A function that a job calls 50,000 times a frame on a worker thread gets `ST_PROFILE_STAGE("Game.Hash")`. What does the stage record, and what is wrong?

   :::answer{tests="stage-rules"}
   Nothing: `BeginStage` returns at once on a thread that is not the frame thread, so the stage records no time, and the job's work shows only in the busy share of the worker pool. Two things are wrong. The stage cannot work on that thread. And a stage around calls of nanoseconds would cost more than the calls even on the frame thread.
   :::

5. You add `Game.MyWork` to a layer, and the **Untimed (rest of the frame)** row gets smaller. Why?

   :::answer{tests="add-stage"}
   The rest of the frame, the row that no stage accounts for, is its work time minus the sum of the stages that lie inside the work time. The new stage raises the sum by its self time, so that row falls by the same amount; the work time itself does not change.
   :::

## Exercises

1. **Basic.** A layer's `OnUpdate` has a work time of 14 ms. Its stage `Game.MyWork` takes 6.0 ms inclusive, `Game.Pathfinding` inside it 2.0 ms and `Game.Cache` inside that 0.5 ms. The other stages of the frame add up to 7 ms. Give each new stage's self time and the time of the rest of the frame.

   :::answer[Worked solution]{tests="self-time,add-stage"}
   `Game.Cache` has 0.5 ms. `Game.Pathfinding` has 2.0 − 0.5 = 1.5 ms. `Game.MyWork` has 6.0 − 2.0 = 4.0 ms. The new stages add 0.5 + 1.5 + 4.0 = 6.0 ms to the stage sum, which is now 7 + 6 = 13 ms. The rest of the frame is 14 − 13 = 1 ms.
   :::

2. **Medium.** Write a program that prints what paces a frame by the 90 % rule. Its five cases give the work, GPU busy and interval times in ms: 6, 7, 16.7; 16, 8, 16.7; 9, 16, 16.7; 5, 6.5, 6.9 (a 144 Hz display); and 7, 3, 6.9.

   :::answer[Worked solution]{tests="frame-bound"}
   The program tests the GPU rule first, then the CPU rule, then reports capped, as the engine does. The sketch prints the five verdicts.

   ```cpp sketch="core-profiling-bound.cpp"
   // What paces a frame, by the 90 % rule: the GPU rule first, then the CPU rule, otherwise capped.
   #include <cstdio>

   namespace
   {
   	struct Case
   	{
   		float WorkMs;
   		float GPUBusyMs;
   		float IntervalMs;
   	};

   	const char* Classify(const Case& frame)
   	{
   		const float bound = 0.9f * frame.IntervalMs;
   		if (frame.GPUBusyMs >= bound && frame.GPUBusyMs > frame.WorkMs)
   			return "GPU-bound";
   		if (frame.WorkMs >= bound)
   			return "CPU-bound";
   		return "capped";
   	}
   }

   int main()
   {
   	const Case cases[] = {
   		{ 6.0f, 7.0f, 16.7f },
   		{ 16.0f, 8.0f, 16.7f },
   		{ 9.0f, 16.0f, 16.7f },
   		{ 5.0f, 6.5f, 6.9f },
   		{ 7.0f, 3.0f, 6.9f },
   	};
   	for (const Case& frame : cases)
   		std::printf("work %4.1f, GPU %4.1f, interval %4.1f: %s\n", frame.WorkMs, frame.GPUBusyMs, frame.IntervalMs, Classify(frame));
   	return 0;
   }
   ```

   ```text output-of="core-profiling-bound.cpp"
   work  6.0, GPU  7.0, interval 16.7: capped
   work 16.0, GPU  8.0, interval 16.7: CPU-bound
   work  9.0, GPU 16.0, interval 16.7: GPU-bound
   work  5.0, GPU  6.5, interval  6.9: GPU-bound
   work  7.0, GPU  3.0, interval  6.9: CPU-bound
   ```

   1. **Lines 15–20:** the GPU rule first, then the CPU rule, and capped when neither holds, as the engine's function does.
   2. **Lines 26–32:** the five cases of the exercise.
   :::

3. **Medium.** Build the editor with Tracy, capture a frame with the viewer, and compare the zones with the stages.

   :::answer[Worked solution]{tests="stage-rules"}
   Configure with `cmake --preset windows -DSTRATA_ENABLE_TRACY=ON`, then build with `cmake --build build/windows --config Debug --parallel`. Start the Tracy viewer, which is a separate program of the same Tracy version, and start the editor; the on-demand client connects once the viewer asks. On the main thread, each stage is a zone of its own name, such as `Editor.UI` and `Render.Submit`, with the zones of `ST_PROFILE_SCOPE` and `ST_PROFILE_FUNCTION` inside. A stage written inside a job records no time, but its Tracy zone still appears on the worker.
   :::

4. **Hard.** Trace it yourself: with `git grep` for `ProfileStage`, `RegisterStage` and `ST_PROFILE_STAGE`, find where each stage beyond the twelve is registered or timed, and check the result against the generated table and the stages of `editor.perf`.

   :::answer[Worked solution]{tests="stage-rules"}
   `Scene.UI` is the `ProfileStage` of the descriptor in `Strata/src/Strata/GameUI/GameUIRegistration.cpp`, and `Scene.Animation` in `Strata/src/Strata/Animation/AnimationRegistration.cpp`. `World.Streaming` is set and registered in `Strata/src/Strata/World/WorldRegistration.cpp`, and the editor also times it with `ST_PROFILE_STAGE` in `StrataEditor/src/Editor/EditorContext.cpp`. `Render.UI` is registered in `RegisterGameUIRenderer` and timed by `ST_PROFILE_STAGE` in `Strata/src/Strata/GameUI/GameUIRenderer.cpp`. `Editor.Commands` is timed in `EditorCommandRegistry::Execute` in `StrataEditor/src/Editor/EditorCommands.cpp`, and in `StrataEditor/src/Editor/EditorCommandRunner.cpp`. The scene registers each `ProfileStage` string when its systems are created, in the loop over the systems of `Scene::OnRuntimeStart`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/Profiling.h`: the Tracy macros and `ST_PROFILE_STAGE`.
- `Strata/src/Strata/Core/FrameProfiler.h` and `FrameProfiler.cpp`: `FrameProfiler`, `FrameStageScope`, `c_BuiltinFrameStages`, `ClassifyFrameBound`, `ComputeStatsInPlace`, `FrameProfileSnapshot`.
- `Strata/src/Strata/Core/Application.cpp`: `RunFrame` begins and ends the frame.
- `StrataEditor/src/Panels/PerformancePanel.cpp`: the panel; `StrataEditor/src/EditorLayer.cpp`: the status bar's frame pill; `StrataEditor/src/Editor/EditorStateCommands.cpp`: `editor.perf`.
- `StrataRuntime/src/RuntimeApplication.cpp`: the perf log's listeners (`--perf-log`).
- Setting: the CMake option `STRATA_ENABLE_TRACY`. Tests: `Core.FrameProfiler`, `Editor.Perf`, `Perf.FrameProfiler`.

## Further reading

- [Tracy, the profiler's repository and manual](https://github.com/wolfpld/tracy): how zones, frame marks and the viewer work; intermediate.
- [Unity, the Profiler](https://docs.unity3d.com/Manual/Profiler.html): another engine's instrumenting profiler with a frame history; beginner.
- Brendan Gregg, "Systems Performance": methodology, percentiles and sampling profilers such as Linux perf; advanced.
- [Microsoft, profiling tools of Visual Studio](https://learn.microsoft.com/en-us/visualstudio/profiling/): a sampling profiler built into an editor; beginner.
- Epic Games, the documentation of Unreal Insights: recording every frame of a trace to a file; intermediate.
