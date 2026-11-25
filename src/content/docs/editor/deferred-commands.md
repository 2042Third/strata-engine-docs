---
id: editor/deferred-commands
title: "Commands that take frames"
description: "How a Strata command that cannot answer in its frame returns a poll function, and the rules that keep the editor drawing while it waits."
kind: internals
size: M
tracks: [E]
needs: [editor/commands, core/time, assets/importing]
time: 65
learn:
  - id: never-block
    text: explain why a command that waits returns a poll function instead of blocking the frame or calling back from a thread
  - id: poll-rules
    text: name the rules a poll function keeps and the reason for each
  - id: runner-order
    text: trace in which frames the runner polls a pending command and where its journal entry completes
  - id: may-defer
    text: explain what MayDefer guards and why editor.batch refuses the commands that carry it
  - id: scan-wait
    text: explain how the registry defers Edit commands and WaitsForAssets commands while the asset scan runs
since: 0.3.0
status: final
---

Most commands answer in the frame that runs them: rename an entity, move it, undo. Some cannot. Opening a scene reads
files, a script build runs a :term[compiler]{id=compiler}, and stepping a paused game needs several frames of game time. This page explains
how Strata lets such a command take frames without freezing the editor: the command hands back a function, and the editor
asks that function once per frame until the answer is ready.

The page covers the runner that asks, the rules the function keeps, the flag that marks the commands allowed to wait, and
the registry's own wait for the :term[asset scan]{id=asset-scan}. It omits the commands that use the mechanism: opening scenes and projects
([projects](../editor/projects.md)), stepping a paused game ([stepping](../editor/stepping.md)) and script builds
([script builds](../editor/script-builds.md)). How the server that answers automation clients sends the answer of a waiting command belongs to
[the page on that server](../automation/rpc-server.md).

## The problem and how engines solve it

The editor draws a frame about every 16.7 ms at 60 :term[frames per second]{id=frame-rate}. A person drags a :term[gizmo]{id=gizmo-start}, types a name, scrolls a
list; each of these needs the next frame to arrive on time. A command that takes longer than a frame has to wait somewhere.
Three answers exist.

The first answer is to block: the handler loops until the work is done. The window stops drawing, no other request is
served, and every agent that talks to the editor waits too. Worse, some commands wait for the frames themselves. A command
that loops until two frames have passed can never finish, because the loop stops the frame from advancing.

The second answer is to start a thread that does the work and, when it ends, calls back into the editor. The scene, the
input and the scripts belong to the :term[main thread]{id=main-thread}, so a worker that touches them while a frame runs creates a race. Races
appear rarely and never in the same place twice.

The third answer is the one the engine uses everywhere it waits: never block a frame. The main thread copies what the work
needs, a job does the slow part, the main thread publishes the result, and the main thread asks again each frame whether
the work is done. Asking replaces calling back. Nothing but the main thread touches editor state, and no frame waits for
anything.

In Strata, a handler that cannot answer yet returns `EditorCommandResult::Defer(poll)`. The command is then a **deferred
command**: one that answers in a later frame, with a final result that replaces the pending one.

The argument of `Defer` is a **poll function**: a function the editor calls once per frame on the main thread. It returns
nothing while the command still runs, and the final result when the command has finished. The function may also return
another pending result, which is how a command made of stages works.

The choice has a price. Every caller must cope with an answer that comes later, and the state of the editor can change
between the start and the end of a command. The rules of the contract below pay for the first cost; the second belongs to
each command.

## The map

Three classes share the work, and all of them run on the main thread. `EditorCommandRegistry::Execute` runs a handler and
writes the journal, the record of every command that `editor.activity` returns. `EditorCommandRunner` keeps the pending commands. `EditorLayer::OnUpdate` calls the runner's `Update`
once per frame, after the editor context's own update.

```mermaid caption="A deferred command: the caller starts it in one frame, and the runner polls it in each later frame until the poll function returns the final answer." alt="A sequence diagram. The caller runs a command through the runner. The registry begins a journal entry, the handler returns a poll function, and the registry suspends the entry. In every later frame the runner resumes the entry, calls the poll function and suspends the entry again. When the poll function returns a result, the runner completes the entry and calls the caller's completion."
sequenceDiagram
	participant C as Caller
	participant R as EditorCommandRunner
	participant G as EditorCommandRegistry
	participant J as CommandJournal
	C->>R: Run(name, parameters)
	R->>G: Execute
	G->>J: Begin
	G->>G: handler returns Defer(poll)
	G->>J: Suspend
	G-->>R: pending result
	Note over R: the frame ends
	loop each later frame
		R->>J: Resume
		R->>R: poll(context)
		R->>J: Suspend
	end
	R->>J: Complete (the final answer)
	R-->>C: completion
```

The **command runner** is the object that keeps the pending commands in the order they were issued and polls each one
once per frame. A command that finishes in its own frame never enters it: `Run` calls the completion at once.

## The contract

A person or an agent sees only a result; the journal sees every poll. The rules that keep both honest follow.

- **Own your data.** The poll function copies what it needs, parameters included. The handler returns long before the
  function runs, and a reference to the request would then point at memory that is gone.
- **Allocate nothing per frame.** A poll runs inside the frames it may be measuring. An allocation can wait for the heap
  while a background thread frees a large scene, and the engine's own tests saw such waits of 0.6 to 2.7 ms in a frame that
  takes 0.6 ms. Reserve storage when the command starts.
- **Wait for a deadline on the clock, or for a condition; frames are no unit of time.** A frame lasts 33 ms at 30 frames per
  second and 7 ms at 144, so a count of frames means different times. The exception is a command whose job is to wait for frames, such as
  `editor.wait`.
- **Never throw out of a poll.** Engine code does not throw. The runner still catches an exception from a third-party
  library and turns it into a failure with the error kind `Internal`.
- **Issue new commands freely, expect them next frame.** A poll or a completion may call `Run`. The runner polls the new
  command from the next frame, never in the frame that issued it.

:::rule[Commands never block a frame]
`AGENTS.md` says that a command which has to wait returns a poll function, and that the function owns its data,
allocates nothing per frame and waits by the clock or a condition. The reason is the one above: the editor is a program
that must keep drawing, and agents rely on it answering.
:::

Two flags describe a command's relation to waiting. **`MayDefer`** is the flag on a command that declares its handler may
return a pending result. `EditorCommandRegistry::Execute` asserts it in Debug and Release builds; asserts are compiled out
of :term[Dist]{id=dist}. `editor.batch` refuses such a command before it runs anything, because a batch is one undo group that finishes in
a single frame and cannot wait for a step.

**`WaitsForAssets`** is the flag on a command that needs the asset registry to be complete, so the registry holds it back
while the project's assets are scanned in the background ([importing](../assets/importing.md)). Edit commands wait for the
scan as well, without the flag. The registry's own wait needs no `MayDefer`; what the
handler answers after the wait does.

An agent can read both flags before it calls a command. `editor.commands` lists every command with `mayDefer`,
`waitsForAssets` and `results`, which says whether the answer comes from the project's content or from the editor's
session. `waitsForAssets` reports the registry's own test, so it is true for every Edit command as well. A client that
sees `mayDefer` knows the answer may come frames later and that `editor.batch` refuses the command.

## A toy version

The toy is a runner of about 100 lines. It has three commands: one that answers at once, one that waits two frames and one
that waits 40 ms. Each frame advances a fake clock by 16 ms. Look at when each answer appears, and at how the clock-based
poll receives the time instead of reading a reference.

```cpp sketch="editor-deferred-commands-toy.cpp"
// A toy command runner: a command that cannot answer in its frame returns a poll function, polled once per frame.
#include <algorithm>
#include <cstdio>
#include <functional>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace
{
	struct Result;
	// Gets the clock in milliseconds, as the real poll gets the editor context; returns nothing while the command runs.
	using Poll = std::function<std::optional<Result>(int nowMs)>;

	struct Result
	{
		std::string Text;
		Poll Pending; // Set while the command still runs.
	};

	class Runner
	{
	public:
		void Run(const std::string& name, Result result)
		{
			if (!result.Pending)
			{
				std::printf("frame %d: %s answers %s at once\n", m_Frame, name.c_str(), result.Text.c_str());
				return;
			}
			std::printf("frame %d: %s starts and waits\n", m_Frame, name.c_str());
			m_Pending.push_back({ name, std::move(result.Pending), false });
		}

		void Update()
		{
			m_Frame++;
			m_NowMs += 16;
			// A poll may issue commands, which grow m_Pending: poll only the commands issued before this update.
			const size_t count = m_Pending.size();
			for (size_t index = 0; index < count; index++)
			{
				Poll poll = std::move(m_Pending[index].Function);
				const std::optional<Result> finished = poll(m_NowMs);
				if (!finished)
				{
					m_Pending[index].Function = std::move(poll);
					continue;
				}
				std::printf("frame %d: %s answers %s\n", m_Frame, m_Pending[index].Name.c_str(), finished->Text.c_str());
				m_Pending[index].Done = true;
			}
			std::erase_if(m_Pending, [](const Entry& entry) { return entry.Done; });
		}

		int GetNowMs() const { return m_NowMs; }

	private:
		struct Entry
		{
			std::string Name;
			Poll Function;
			bool Done;
		};

		std::vector<Entry> m_Pending;
		int m_Frame = 0;
		int m_NowMs = 0;
	};

	// Finishes at the poll that counts the last frame. The count is the poll's own copy.
	Result WaitFrames(int frames)
	{
		return { "done", [remaining = frames](int) mutable -> std::optional<Result>
		{
			if (--remaining > 0)
				return std::nullopt;
			return Result { "done", {} };
		} };
	}

	// Finishes at the first poll whose clock has reached the deadline, however long the frames are.
	Result WaitUntil(int deadlineMs)
	{
		return { "done", [deadlineMs](int nowMs) -> std::optional<Result>
		{
			if (nowMs < deadlineMs)
				return std::nullopt;
			return Result { "done", {} };
		} };
	}
}

int main()
{
	Runner runner;
	runner.Run("ping", { "pong", {} });
	runner.Run("wait 2 frames", WaitFrames(2));
	runner.Run("wait 40 ms", WaitUntil(runner.GetNowMs() + 40));
	for (int frame = 0; frame < 4; frame++)
		runner.Update();
	return 0;
}
```

```text output-of="editor-deferred-commands-toy.cpp"
frame 0: ping answers pong at once
frame 0: wait 2 frames starts and waits
frame 0: wait 40 ms starts and waits
frame 2: wait 2 frames answers done
frame 3: wait 40 ms answers done
```

1. **Line 14:** a poll takes the clock and returns nothing while the command runs, as the real poll takes the editor context.
2. **Line 41:** the count is read before the loop, so a poll that issues a command does not extend this update.
3. **Lines 44–50:** the poll is moved out of the list, called, and put back when it has no answer yet.
4. **Line 54:** finished commands leave the list after the loop, never during it.
5. **Line 75:** the frame count belongs to the function, which owns its own copy.

The command that answered at once never entered the list. The two others were polled once per update, in the order they
were issued. The 40 ms wait finished in the third frame, at 48 ms, the first clock reading at or after its deadline.
Four things differ in the real code: the poll takes the editor context, the runner keeps a journal entry for each
command, completions can issue commands, and a pending result can be cancelled.

## The real code

The real code follows the data. A command starts in `Execute`, which may defer it for the asset scan.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L124-L143"
if (command && context.IsWaitingForAssets() && WaitsForAssetScan(*command))
{
	// The registry is still filling: the command runs once the scan ended (and goes on from there if it defers itself).
	// This deferral is the registry's, not the handler's, so it needs no MayDefer; what the handler answers then does.
	result = EditorCommandResult::Defer([this, command, name = std::string(name), parameters = nlohmann::json(parameters)](EditorContext& context)
		-> std::optional<EditorCommandResult>
	{
		if (context.IsWaitingForAssets())
			return std::nullopt;
		EditorCommandResult deferred = Run(context, command, name, parameters);
		ST_ASSERT(!deferred.IsPending() || command->MayDefer, "Command '{}' answered later (Defer) but is not registered with MayDefer", name);
		return deferred;
	});
}
else
{
	result = Run(context, command, name, parameters);
	// The flag keeps editor.batch from starting what cannot finish in its frame: it must be right.
	ST_ASSERT(!result.IsPending() || !command || command->MayDefer, "Command '{}' answered later (Defer) but is not registered with MayDefer", name);
}
```

1. **Lines 128–129:** the poll copies the name and the parameters, so it owns them.
2. **Lines 131–132:** each poll asks whether the scan has ended, and answers nothing until it has.
3. **Line 134:** the handler's own wait still needs `MayDefer`.
4. **Line 142:** the same check for the direct branch.

The first branch is the registry's own wait. It copies the name and the parameters into the poll function, so the
function owns them. Once the scan ends it calls `Run`, and the assert checks what the handler then returns. The second
branch runs the handler at once.

The scan wait asks two questions: which commands wait, and what to tell the person.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L158-L177"
bool EditorCommandRegistry::WaitsForAssetScan(const EditorCommand& command)
{
	return command.Kind == EditorCommandKind::Edit || command.WaitsForAssets;
}

std::optional<std::string> EditorCommandRegistry::DescribeAssetScanWait(const EditorContext& context, std::string_view name) const
{
	const EditorCommand* command = Find(name);
	if (!command || !context.IsWaitingForAssets() || !WaitsForAssetScan(*command))
		return std::nullopt;
	const std::optional<AssetScanProgress> progress = context.GetAssetScanProgress();
	if (!progress && context.IsMigratingProject())
		return std::string("the scenes of a project saved by 0.5.0 are still being read for its collision layers");
	if (!progress)
		return std::string("the project's start scene is still being opened");
	if (progress->Total == 0)
		return std::string("the project's assets are still being scanned");
	return fmt::format("the project's assets are still being scanned ({} of {})", StringUtils::FormatThousands(progress->Done),
		StringUtils::FormatThousands(progress->Total));
}
```

1. **Lines 158–161:** Edit commands and flagged commands wait.
2. **Lines 165–167:** an unknown command, or no scan, gives no reason.
3. **Lines 168–176:** the reason gets more exact as the scan progresses, down to the count of assets.

A command waits when its kind is Edit or it carries `WaitsForAssets`. `DescribeAssetScanWait` gives the user interface a
sentence for the refusal, such as "the project's assets are still being scanned (120 of 4,000)".

Next, `editor.wait`, the smallest deferred command, shows a poll function with its own state.

```cpp src="StrataEditor/src/Editor/EditorStateCommands.cpp#L898-L925"
registry.Register(MayDefer({ "editor.wait",
	"Returns after the given number of frames. Use it to let a playing scene run, assets load or the viewport render before the next "
	"command. Returns {frames} and, when the editor measures its frames (not when a test drives it without its EditorLayer), "
	"frameTimes: the CPU time of the frames that ran entirely while waiting (all but the first), in milliseconds {count, medianMs, "
	"meanMs, p95Ms, maxMs}, without waiting for the GPU and the display, so command scripts can check frame budgets with expect.",
	ObjectSchema({ { "frames", IntegerSchema("Frames to wait (default 1)", 1, c_MaxWaitFrames) } }),
	[](EditorContext& context, const nlohmann::json& parameters)
	{
		CommandArguments arguments(parameters);
		const int64_t frames = arguments.GetInt("frames", 1, 1, c_MaxWaitFrames);
		if (!arguments.IsValid())
			return arguments.Fail();
		// Polled once per frame from the frame after this one, so it finishes when `frames` frames have passed. Each poll
		// sees the time of the frame before it. The frame this command runs in also runs whatever came before it (in a
		// command script, e.g. a scene load), so the measured frames start with the next one.
		const uint64_t firstMeasured = context.GetRecordedFrameCount() + 2;
		return EditorCommandResult::Defer([frames, remaining = frames, frameTimes = FrameTimeRecorder(firstMeasured, static_cast<size_t>(frames))](
			EditorContext& context) mutable -> std::optional<EditorCommandResult>
		{
			frameTimes.Update(context);
			if (--remaining > 0)
				return std::nullopt;
			nlohmann::json result = { { "frames", frames } };
			if (!frameTimes.IsEmpty())
				result["frameTimes"] = frameTimes.Describe();
			return EditorCommandResult::Ok(std::move(result));
		});
	}, EditorCommandKind::Query }));
```

1. **Line 913:** the first frame that counts, two records after the one the command started in.
2. **Lines 914–915:** the poll copies `frames`, its count and its recorder into the function.
3. **Lines 917–919:** each poll records a :term[frame time]{id=frame-time}, counts down and answers nothing until the last frame.
4. **Lines 920–923:** the final result carries `frames` and, when frames were measured, `frameTimes`.

The poll copies `frames` and counts `remaining` down; both live in the function, which the runner moves around freely.
`firstMeasured` skips the frame that started the command, because that frame also ran whatever came before it.

The recorder behind `frameTimes` is the rule "allocate nothing per frame" in code.

```cpp src="StrataEditor/src/Editor/CommandUtils.h#L126-L144"
class FrameTimeRecorder
{
public:
	// Records the frames from the editor's recorded frame `firstMeasured` on (EditorContext::GetRecordedFrameCount),
	// with room for `expectedFrames`.
	FrameTimeRecorder(uint64_t firstMeasured, size_t expectedFrames);

	// Records the latest frame the editor recorded, if it is measured and new (call it once per poll).
	void Update(const EditorContext& context);
	bool IsEmpty() const { return m_FrameTimes->empty(); }
	size_t GetCount() const { return m_FrameTimes->size(); }
	size_t GetCapacity() const { return m_FrameTimes->capacity(); }
	// DescribeFrameTimes of the recorded frames (at least one).
	nlohmann::json Describe() const;
private:
	std::shared_ptr<std::vector<double>> m_FrameTimes;
	uint64_t m_FirstMeasured = 0;
	uint64_t m_LastRecorded = 0;
};
```

1. **Line 131:** the :term[constructor]{id=constructor} reserves the room, when the command starts.
2. **Line 134:** `Update` records the latest frame once, and only when it is measured and new.
3. **Line 141:** the :term[shared pointer]{id=shared-pointer} lets copies of the poll function share one vector.

The vector is created and reserved in the :term[constructor]{id=constructor}, when the command starts. `Update` only appends, and the :term[shared
pointer]{id=shared-pointer} lets copies of the poll function see one vector, so copying the function never copies the data. `editor.wait`
reserves room for exactly its count of frames. `scene.open` and `project.export` reserve `c_FrameTimeReserve`, which is large enough for the
longest scene opens the perf tests measure. A command that runs for more frames than its reserve holds grows the vector, which allocates.

Now the runner. `PollCommandResult` polls one pending result.

```cpp src="StrataEditor/src/Editor/EditorCommandRunner.cpp#L274-L309" symbol="PollCommandResult"
bool PollCommandResult(EditorCommandResult& result, EditorContext& context)
{
	if (!result.IsPending())
		return true;

	// The frame profiler's stage of command work, as in EditorCommandRegistry::Execute.
	ST_PROFILE_STAGE("Editor.Commands");
	const uint64_t journalId = result.JournalId;
	CommandJournal& journal = context.GetJournal();
	journal.NoteEditsOutsideCommands(context.GetUndoStack());
	const uint64_t records = context.GetUndoStack().GetRecordCount();
	// While its poll runs the command is the running one again: what the poll does is known to be its work.
	journal.Resume(journalId);
	std::optional<EditorCommandResult> finished;
	try
	{
		finished = result.Pending(context);
	}
	catch (const std::exception& exception)
	{
		// Engine code does not throw; this guards third-party code (JSON access) used by poll functions.
		finished = EditorCommandResult::Fail(fmt::format("Command failed: {}", exception.what()), EditorCommandError::Internal);
	}
	journal.Suspend(journalId);
	journal.NotePoll(journalId);
	journal.NoteUndo(journalId, context.GetUndoStack(), records);
	if (!finished)
		return false;
	// The poll function has returned, so replacing it does not destroy a running function.
	result = std::move(*finished);
	result.JournalId = journalId;
	if (result.IsPending())
		return false;
	journal.Complete(journalId, result);
	return true;
}
```

1. **Line 286:** the journal entry becomes the running one for the length of the poll.
2. **Lines 288–296:** an exception from third-party code becomes a failure of kind `Internal`.
3. **Lines 297–301:** the entry is suspended again, and with no answer the command stays pending.
4. **Lines 303–307:** a final answer replaces the pending result and completes the journal entry.

While the poll runs, the journal entry is the running one again, so what the poll does counts as the command's work. After
the call the entry is suspended again. Only a final result completes the entry.

`Update` calls it for every pending command.

```cpp src="StrataEditor/src/Editor/EditorCommandRunner.cpp#L337-L372" symbol="EditorCommandRunner::Update"
void EditorCommandRunner::Update(EditorContext& context)
{
	ST_ASSERT(!m_Updating, "EditorCommandRunner::Update must not be called from a poll function or completion");
	m_Updating = true;
	// Poll functions and completions may issue commands (appended to m_Pending, which can reallocate it), so nothing
	// refers into the vector while they run, and only the commands issued before this update are polled.
	const size_t count = m_Pending.size();
	for (size_t index = 0; index < count; index++)
	{
		if (m_Pending[index].Done)
			continue; // Cancelled by an earlier completion

		EditorCommandResult result = std::move(m_Pending[index].Result);
		m_Pending[index].Result = {};
		const bool finished = PollCommandResult(result, context);
		if (m_Pending[index].Done)
		{
			// Cancelled while it was polled (its result was out of the list then): its journal entry ends cancelled too.
			if (!finished && m_Pending[index].Journal)
				m_Pending[index].Journal->Complete(result.JournalId, EditorCommandResult::Fail("Cancelled while it ran", EditorCommandError::Cancelled));
			continue;
		}
		if (finished)
		{
			if (m_Pending[index].FromUI)
				NotifyCommandOutcome(context.GetNotifications(), m_Pending[index].Name, result);
			Finish(index, result);
		}
		else
		{
			m_Pending[index].Result = std::move(result);
		}
	}
	std::erase_if(m_Pending, [](const PendingCommand& command) { return command.Done; });
	m_Updating = false;
}
```

1. **Line 343:** the count is read once, before any poll can issue a command.
2. **Lines 349–351:** the result moves out of the list while its poll runs, so nothing refers into a vector that can grow.
3. **Lines 359–364:** a finished command notifies the person when the interface issued it, and then finishes.
4. **Line 370:** the finished entries leave the list after the loop.

The loop reads `count` before it starts, so a command issued by a poll or a completion waits for the next update, and
nothing refers into `m_Pending` while it can grow. The finished commands are erased after the loop.

:::example[`editor.wait` with five frames]
A person runs `editor.wait {"frames": 5}` from a terminal. The editor has recorded 1 :term[frame time]{id=frame-time} so far, so
`firstMeasured` is 1 + 2 = 3. The command runs in frame 0 and answers nothing. The runner polls it in frames 1 to 5.

The
times the editor records before each poll are 9, 1, 4, 2 and 3 ms, as records 2 to 6. The poll sees record 2 and skips it
(2 is below 3), keeps 1, 4, 2 and 3, and counts `remaining` from 5 down to 0 at frame 5. The answer has `frames` 5 and a
`frameTimes` object of count 4, median 2.5 ms, mean 2.5 ms, P95 4 ms and maximum 4 ms. The journal entry stays open
through frames 1 to 4 and completes in frame 5, in the same call as the last poll.
:::

## Cancelling, quitting and measuring

`CancelAll` completes every pending command with the error kind `Cancelled` and a reason, and `EditorLayer::OnDetach` calls
it before the project closes. The clients of cancelled commands still get an answer, because automation stops afterwards.

`editor.quit` defers for a different reason: it waits for saves in flight, through `AfterSaves`
([saving](../editor/saving.md)). It refuses to quit while the scene has changes not yet saved, unless `force` is true. It answers before the editor
closes, so the caller learns the result, and the pending commands are then cancelled. `editor.perf` looks like a neighbour
of `editor.wait` but is not deferred: it answers in its own frame from the frames the profiler already recorded, at most
600 ([profiling](../core/profiling.md)).

`viewport.capture` defers because it waits for several things at once: glyphs of text, loading assets, texture
detail, the shadows of local lights, exposure, global illumination and the history of the temporal filter. Every wait
has its own limit, counted in frames because each poll renders the picture once more. The limits are 300 frames for assets, about five
seconds at 60 frames per second, 120 for glyphs and 16 for the history. When a limit runs out, the capture answers
anyway, with `complete` false and `incomplete` naming what the picture lacks. Only the readback of the picture waits by
the clock: after 30 seconds the capture fails, because the graphics device is lost or hung.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Block until done | Small tools and scripts | The simplest handlers | A live window, and any command that waits for frames |
| A thread that calls back | Many desktop programs | No polling frame by frame | Safe access to the scene, and bugs that reproduce |
| Promises and futures | Libraries with an event loop | A standard type for a late answer | A way to guarantee that results arrive on the main thread, and one journal entry per command |
| Coroutines | Engines with a :term[game loop]{id=game-loop} of tasks | Waits that read like straight code | Poll functions that own plain data and are simple to cancel |

## How it is tested

`StrataTests/src/Editor/EditorCommandRunnerTests.cpp` drives a runner with a test command that finishes after a number of
polls. Its cases check five things:

- commands that finish at once never wait;
- pending ones are polled once per update and complete in order;
- completions issue commands for the next update, and cancelling completes every entry;
- `editor.wait` finishes after the right number of frames with the right statistics;
- the recorder never grows its storage.

`CommandJournalTests.cpp` holds the lists of deferring commands and of `WaitsForAssets` commands, and compares them with the
registry.

```powershell
build/windows/bin/Debug/StrataTests.exe --test-case="editor.wait*"
```

The command runs the two `editor.wait` cases and prints how many passed.

## Changing it safely

- A new deferred command wraps its registration in `MayDefer` and joins the deferring list in `CommandJournalTests.cpp`;
  the test compares the flag with the list, so one without the other fails.
- Copy everything the poll uses into the poll. Capture `context` as the poll's argument, never as a captured reference.
- Reserve storage when the command starts if the poll collects data; copy `FrameTimeRecorder`'s way.
- Wait on a deadline taken from the clock at the start, or on a condition the context answers; never count frames unless
  frames are the point.
- A command that reads the whole asset registry sets `WaitsForAssets` and joins the list of `c_AssetScanCommands`.
- Run `Editor*` tests, then the feature test, before you commit.

## Summary

- A command that cannot answer in its frame returns a poll function. Blocking freezes the editor and a thread that calls
  back races with the main thread.
- A poll function owns copies of its data, allocates nothing per frame and waits by the clock or a condition.
- The runner polls each pending command once per frame, from the next frame, in issue order; the journal entry completes
  with the final answer.
- `MayDefer` declares a command that may answer later, and `editor.batch` refuses it before running anything;
  `editor.commands` reports it as `mayDefer`, beside `waitsForAssets`.
- While the assets scan, the registry defers Edit commands and `WaitsForAssets` commands, and
  `DescribeAssetScanWait` says why.

## Check yourself

1. A handler for a new command waits for two frames with `while (frames < 2) {}` in its own body. What happens? Choose one:
   (a) it works, only slowly; (b) it never ends, because the frame cannot advance while the loop runs; (c) it races with
   the job system; (d) the runner polls it twice.

   :::answer{tests="never-block"}
   (b). The loop holds the main thread, and frames are drawn on the main thread, so the count never changes. Answer (a)
   forgets that the loop stops the frame. Answer (c) is the fault of the other design, a thread that calls back, and there
   is no thread here. Answer (d) describes a poll function; a loop is not one.
   :::

2. A poll function captures `parameters` by reference and reads `parameters["name"]` in its third poll. Which rule does it
   break, and what goes wrong?

   :::answer{tests="poll-rules"}
   The function breaks the rule to own the data. The request that held `parameters` ended when the handler returned, so in frame 3 the
   reference points at memory that is gone: a crash, or a name that is not the one the caller sent. The fix is to capture a
   copy, as `Execute` does with `nlohmann::json(parameters)`.
   :::

3. You run `editor.wait {"frames": 3}` in frame 10. In which frames does the runner poll it, and in which does the journal
   entry complete? A poll in frame 12 issues a new command; in which frame is that polled first?

   :::answer{tests="runner-order"}
   Polls happen in frames 11, 12 and 13, and the entry completes in frame 13, when the last poll returns the final result.
   A command issued during frame 12 is polled first in frame 13, because `Update` reads the pending count before it
   starts and polls only the commands issued before it.
   :::

4. You add a command whose handler returns `Defer`, and you forget `MayDefer`. Name two consequences.

   :::answer{tests="may-defer"}
   In a Debug or Release build, `Execute` fails its assert, and the test that compares each command's flag with the list
   fails too. Without the flag, `editor.batch` would also accept the command, although the batch cannot wait for it. The
   flag has to be right for both reasons, which is why a list and a test hold it.
   :::

5. A project opens and its assets are still being scanned. `entity.create`, `asset.list` and `editor.status` are run. Which
   are deferred, and where does the person read why?

   :::answer{tests="scan-wait"}
   `entity.create` is an Edit command and `asset.list` carries `WaitsForAssets`, so the registry defers both until the scan
   ends. `editor.status` is a Query without the flag and answers at once. `DescribeAssetScanWait` gives the interface the
   reason, with the number of assets scanned out of the total when it is known.
   :::

## Exercises

1. **Basic.** An `editor.wait {"frames": 4}` starts when the editor has recorded 10 frame times. The times recorded before
   its four polls are 8, 2, 4 and 3 ms. Give `firstMeasured`, the times kept, and the median, mean and maximum.

   :::answer[Worked solution]{tests="runner-order"}
   `firstMeasured` is 10 + 2 = 12. The four polls see records 11 to 14, with 8, 2, 4 and 3 ms. The poll skips record 11
   (below 12) and keeps 2, 4 and 3. The median is 3 ms, the mean (2 + 4 + 3) / 3 = 3 ms and the maximum 4 ms.
   :::

2. **Medium.** Sketch the handler of a new command `waitSeconds`, in the group `editor`, that takes `seconds`, and say what else the change
   needs so that a batch refuses it.

   :::answer[Worked solution]{tests="poll-rules,may-defer"}
   The handler takes the deadline from the clock when it starts, copies it into the poll and returns it. The registration
   is wrapped in `MayDefer`, and the name joins the deferring list in `CommandJournalTests.cpp`. Then `editor.batch` refuses
   it, as its check reads the flag. `Now()` stands for any clock read; it is no function of the engine.

   ```cpp pseudocode
   const double deadline = Now() + seconds;
   return EditorCommandResult::Defer([deadline, seconds](EditorContext&) -> std::optional<EditorCommandResult>
   {
       if (Now() < deadline)
           return std::nullopt;
       return EditorCommandResult::Ok({ { "seconds", seconds } });
   });
   ```

   The poll holds only the deadline and a value, so it owns its data, allocates nothing and waits by the clock.
   :::

3. **Medium.** Write a program that prints how long six frames last, and how many frames 100 ms take, at 30, 60 and 144
   frames per second.

   :::answer[Worked solution]{tests="poll-rules"}
   The program computes both numbers per rate. A count of frames means different times at different rates, which is why
   a poll waits by the clock.

   ```cpp sketch="editor-deferred-commands-frames.cpp"
   // How long a wait of six frames lasts, and how many frames a wait of 100 ms takes, at three frame rates.
   #include <cstdio>

   int main()
   {
   	const int rates[] = { 30, 60, 144 };
   	for (const int rate : rates)
   	{
   		const double sixFramesMs = 6.0 * 1000.0 / rate;
   		// Whole frames: the first poll at or after the deadline answers.
   		const int framesFor100Ms = (100 * rate + 999) / 1000;
   		std::printf("%3d frames per second: 6 frames last %5.1f ms; 100 ms take %2d frames\n", rate, sixFramesMs, framesFor100Ms);
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-deferred-commands-frames.cpp"
    30 frames per second: 6 frames last 200.0 ms; 100 ms take  3 frames
    60 frames per second: 6 frames last 100.0 ms; 100 ms take  6 frames
   144 frames per second: 6 frames last  41.7 ms; 100 ms take 15 frames
   ```

   1. **Line 9:** the time of six frames is six times the length of one frame.
   2. **Lines 10–11:** a wait for 100 ms ends at the first whole frame at or after the deadline, which is a different count at each rate.
   :::

4. **Hard.** Trace it yourself: with breakpoints in `PollCommandResult` and `EditorCommandRunner::Update`, run
   `editor.wait {"frames": 2}` from a terminal. Count the polls, and name the line where the journal entry completes.

   :::answer[Worked solution]{tests="runner-order"}
   `PollCommandResult` runs twice, once in each of two `Update` calls. The first poll returns nothing. The second returns the
   final result, and the call `journal.Complete(journalId, result)` in `PollCommandResult` in
   `StrataEditor/src/Editor/EditorCommandRunner.cpp` ends the entry, after which `Update` calls `Finish`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommands.h` and `EditorCommands.cpp`: `EditorCommandResult::Defer`, `MayDefer`, `Execute`, `WaitsForAssetScan`, `DescribeAssetScanWait`.
- `StrataEditor/src/Editor/EditorCommandRunner.cpp`: `PollCommandResult`, `EditorCommandRunner::Run`, `Update`, `CancelAll`.
- `StrataEditor/src/Editor/CommandUtils.h`: `FrameTimeRecorder`, `c_FrameTimeReserve`, `AfterSaves`.
- `StrataEditor/src/Editor/EditorStateCommands.cpp`: `editor.wait`, `editor.perf`, `editor.quit`.
- `StrataEditor/src/Editor/Commands/BatchCommands.cpp`: the refusal of `MayDefer` commands.
- Tests: `EditorCommandRunnerTests.cpp` and `CommandJournalTests.cpp` in `StrataTests/src/Editor/`.

## Further reading

- Robert Nystrom, "Game Programming Patterns", the chapters "Game Loop" and "Update Method": why a game never waits inside a
  frame; beginner.
- Microsoft, the documentation of the Windows message loop: why a program that blocks its loop stops answering; beginner.
- The documentation of Boost.Asio on asynchronous operations and handlers: calls that complete later; advanced.
