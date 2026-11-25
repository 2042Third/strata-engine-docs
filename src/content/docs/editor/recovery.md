---
id: editor/recovery
title: "Autosave and crash recovery"
description: "How the editor keeps a journal of unsaved scene changes so that a crash, a power cut or a forced scene change loses little or nothing."
kind: internals
size: M
tracks: [E]
needs: [editor/saving]
time: 55
learn:
  - id: choose-journal
    text: compare periodic full copies, a write-ahead journal and Strata's journal of entity states
  - id: write-timing
    text: compute when the journal is written for a series of edits
  - id: fold-segments
    text: trace which steps fold into the segment before them and which start a new one
  - id: snapshot-limit
    text: predict what the journal does for a scene that was never saved, by its size
  - id: discard-kept
    text: explain why a forced discard and Don't Save leave recovery data behind
since: 0.3.0
status: final
---

You edit a scene for an hour and the editor crashes, or an agent forces a scene open and your edits go with the old scene. Strata answers both with the same part: `SceneRecovery`, which writes the changes you have not saved to a file while you work. The part watches the :term[undo stack]{id=undo-stack}, writes when you pause, and offers the file again when the project opens. It does not replace saving, and it does not draw the dialog that offers recovery.

## The problem and how engines solve it

A crash can come at any moment: a driver fault, a power cut, or a person who ends the process. Everything that lives only in memory then disappears, and the scene on disk is the one from your last save. The question is what to write between saves, and when.

The first approach is a periodic full copy. Every few minutes the editor writes the whole scene to a side file, as many content tools and engines do, and recovery means opening the copy. The cost grows with the scene. Suppose a scene of 100,000 entities makes a file of 17 MB: a copy every 10 seconds writes about 100 MB a minute (6 writes of 17 MB), although you changed one entity.

The second approach is a journal written ahead of the change, as databases do. Before the program changes anything, it appends a line that says what it will change. After a crash, the program replays the lines. The cost per line is small, but the program must write before every change, and a drag changes values many times a second.

The third approach keeps a snapshot plus the changes since it. The snapshot is the saved file, which already exists, so only the changes need writing. Strata takes this approach with three rules. The journal holds the states of the entities that edits touched, it is tied to the exact saved file it applies to, and it is written when the editor is quiet.

A **recovery journal** is the file in which Strata keeps the changes of the edited scene that are not saved yet, so that an editor that ends badly can restore them. The cost of the choice is that recovery needs the saved file unchanged. Edit the scene file with another program after a crash, and the journal no longer applies.

## The map

The undo stack tells `SceneRecovery` about each applied step. The editor's context calls it once per frame. The diagram shows how the work splits across threads.

```mermaid caption="The journal follows the undo stack on the main thread, builds its text on a background worker and writes the file on an input and output job." alt="A diagram. An edit becomes an undo step. The undo stack tells the recovery journal on the main thread. Once per frame the editor context asks the journal to update. When the timer is due, a background worker builds the text and an input and output job writes the file in the recovery folder of the project."
flowchart LR
	edit["edit"] --> undo["UndoStack (main thread)"]
	undo -->|"OnApplied"| journal["SceneRecovery (main thread)"]
	context["EditorContext::Update"] -->|"once per frame"| journal
	journal -->|"timer due"| worker["background worker: build text"]
	worker --> io["I/O job: write file"]
	io --> file[".strata/Recovery/*.strecovery"]
```

The file operations run one at a time, in the order asked for, so a removal after a save is never overtaken by an earlier write.

### How the journal follows the undo stack

The journal learns of edits through the **observer pattern**: an object that wants to know about events registers with the object that causes them, and the cause calls it when one happens. The editor's context registers `SceneRecovery` with the undo stack once, in its :term[constructor]{id=constructor}. From then on, every time the stack applies a step, by a new edit, an undo or a redo, it calls `OnApplied`.

An :term[undo step]{id=undo-step} already holds the states of the entities it touched, so that undo can restore them. The journal receives a shared reference to those states, never a copy of the scene. Following a step costs one reference on the :term[main thread]{id=main-thread}.

## The contract

What callers may count on, and what they must do:

- The journal covers the edited scene only, and only while a project is open. With no project there is no folder to write to, and nothing is journaled.
- A write never blocks a frame: a worker builds the text and an input and output job writes it.
- A crash at any moment leaves the previous complete file or the new complete file, never half. The writer writes `<file>.tmp` and renames it over the journal, the way [Files you can trust](../core/files.md) describes.
- The journal applies only to one file: the :term[SHA-256]{id=sha-256} of the saved scene file is stored in it, and recovery refuses when the file changed.
- Saving removes the journal, and so does undoing back to the saved state.
- Replacing the edited scene that has changes not saved yet writes the journal at once, marked discarded.

:::rule[Only the journal writes recovery files]
Only `Editor/SceneRecovery` writes recovery files, and every replacement of the edited scene goes through `EditorContext::ResetScene`. The reason: `ResetScene` is the one place that calls `EndScene`, which keeps changes that are not saved. A second path that replaced the scene would lose them, and a second writer would break the order of file operations. See [Saving scenes](saving.md).
:::

## A toy version

Before the real code, a toy shows the folding idea without threads, files or timers. Each undo step is a list of entity states before and after. The toy asks whether a step is structural and either starts a new segment or folds into the last one.

A **structural step** is an undo step that creates, removes or moves an entity. Any other step, such as a value edit or a drag of a number, is not structural. A moved entity is one whose parent or position among its siblings changed.

:::question
The next listing uses classes, loops and functions of C++; if they are new, read [Programming 3](../basics/programming-3.md) first.
:::

The toy defines a state, a step and `IsStructural`. `Fold` walks the steps in order and builds segments. Look at how a segment keeps only the latest state of each entity. The program feeds it seven steps: entity 1 is created and edited twice, entity 2 is created and edited, entity 2 moves under entity 1, and entity 1 is edited again.

```cpp sketch="editor-recovery-toy.cpp"
// A toy recovery journal: steps that create, remove or move no entity fold into the segment before them.
#include <cstdio>
#include <map>
#include <string>
#include <vector>

struct State
{
	int Id;
	bool Exists;
	int Parent;
	std::string Value;
};

// What one undo step left (After) and what the same entities held before it (Before).
struct Step
{
	std::vector<State> Before;
	std::vector<State> After;
};

// The latest state of every entity the segment touched, in the order of the entity ids.
using Segment = std::map<int, State>;

bool IsStructural(const Step& step)
{
	if (step.Before.size() != step.After.size())
		return true;
	for (size_t index = 0; index < step.After.size(); index++)
	{
		const State& before = step.Before[index];
		const State& after = step.After[index];
		if (after.Id != before.Id || after.Exists != before.Exists)
			return true;
		if (after.Exists && after.Parent != before.Parent)
			return true;
	}
	return false;
}

std::vector<Segment> Fold(const std::vector<Step>& steps)
{
	std::vector<Segment> segments;
	for (const Step& step : steps)
	{
		if (segments.empty() || IsStructural(step))
			segments.emplace_back();
		for (const State& state : step.After)
			segments.back()[state.Id] = state;
	}
	return segments;
}

int main()
{
	const State none1 = { 1, false, 0, "" };
	const State none2 = { 2, false, 0, "" };
	const std::vector<Step> steps = {
		{ { none1 }, { { 1, true, 0, "a0" } } },
		{ { { 1, true, 0, "a0" } }, { { 1, true, 0, "a1" } } },
		{ { { 1, true, 0, "a1" } }, { { 1, true, 0, "a2" } } },
		{ { none2 }, { { 2, true, 0, "b0" } } },
		{ { { 2, true, 0, "b0" } }, { { 2, true, 0, "b1" } } },
		{ { { 2, true, 0, "b1" } }, { { 2, true, 1, "b1" } } },
		{ { { 1, true, 0, "a2" } }, { { 1, true, 0, "a3" } } } };

	const std::vector<Segment> segments = Fold(steps);
	std::printf("%zu steps became %zu segments\n", steps.size(), segments.size());
	for (size_t index = 0; index < segments.size(); index++)
	{
		std::printf("segment %zu:", index + 1);
		for (const auto& [id, state] : segments[index])
			std::printf(" [entity %d, parent %d, %s]", id, state.Parent, state.Value.c_str());
		std::printf("\n");
	}
}
```

```text output-of="editor-recovery-toy.cpp"
7 steps became 3 segments
segment 1: [entity 1, parent 0, a2]
segment 2: [entity 2, parent 0, b1]
segment 3: [entity 1, parent 0, a3] [entity 2, parent 1, b1]
```

1. **Line 23:** a segment maps an entity id to the latest state the segment holds, so a later state replaces an earlier one.
2. **Lines 25–39:** a step is structural when the entity count, an id, its existence or its parent differs.
3. **Lines 46–47:** a segment starts only for the first step or a structural step.
4. **Line 49:** every other step writes its states into the last segment.

Seven steps became three segments. The two edits of entity 1 and the one of entity 2 cost no segment of their own. The last edit of entity 1 landed in the third segment, although entity 1 first appeared in the first. That is correct: the third segment is applied after the first two, and it leaves each entity where the segment put it. The real code does the same.

## The real code

The real code follows a session: edits arrive, the timer fires, the text is built, a file appears. Then come the cases that make it complete: scenes never saved, saves in progress, discards, and finally recovery itself.

### Edits arrive

`OnApplied` is the observer function. It first ignores steps that change nothing in the scene. For a step that changes entities, it keeps the states the step left and the states before it, and marks the journal changed. A step that merges into the one before, a frame of a drag, replaces the states kept for it, so a long drag holds one step.

```cpp src="StrataEditor/src/Editor/SceneRecovery.cpp#L629-L669" symbol="SceneRecovery::OnApplied"
void SceneRecovery::OnApplied(const EditorAction& action, bool undone, bool merged)
{
	if (!IsActive() || !m_Journal)
		return;
	if (action.GetSceneChange() != SceneChangeKind::None)
		RetainStep(action, undone, merged);
	switch (action.GetSceneChange())
	{
		case SceneChangeKind::None:
			return;
		case SceneChangeKind::Entities:
			// A journal that takes a snapshot when it is written needs no steps.
			if (!m_NeedsSnapshot && !m_Unjournaled)
			{
				Ref<const std::vector<EntityState>> states = action.GetEntityStates(undone);
				if (!states)
				{
					m_NeedsSnapshot = true;
				}
				else if (merged && !m_PendingSteps.empty() && m_PendingSteps.back().Action == &action)
				{
					// A drag merges a frame at a time into its step: the step's latest states replace those of the frame
					// before, which would otherwise wait for the write with every other frame's.
					m_PendingSteps.back().States = std::move(states);
					m_PendingSteps.back().Prior = action.GetEntityStates(!undone);
				}
				else
				{
					m_PendingSteps.push_back({ std::move(states), action.GetEntityStates(!undone), &action });
				}
			}
			break;
		case SceneChangeKind::Settings:
			break; // Every write records the settings
		case SceneChangeKind::Other:
			m_NeedsSnapshot = true;
			break;
	}
	m_Changed = true;
	m_LastChange = std::chrono::steady_clock::now();
}
```

1. **Lines 631–632:** with no project or no journal, nothing is kept.
2. **Lines 648–654:** a merged step, a frame of a drag, replaces the states kept for it.
3. **Line 657:** any other step is kept with its states and the states before it.
4. **Line 664:** a step of kind Other asks for a snapshot at the next write.
5. **Lines 667–668:** the journal is marked changed and the time of the edit is noted.

Why does a step keep its `Prior` states? To tell later whether it was structural. A step of kind Other, which is not made of entity states, sets the flag `m_NeedsSnapshot`, which the section on complete journals explains.

### The quiet timer

`Update` runs once per frame. It first pumps the queue of file operations. Then, if the journal changed, it writes when the changes stopped for `c_QuietSeconds` (2 s) or when the last write is `c_MaxIntervalSeconds` (10 s) old.

```cpp src="StrataEditor/src/Editor/SceneRecovery.cpp#L671-L688" symbol="SceneRecovery::Update"
void SceneRecovery::Update(const Scene& scene, bool modified)
{
	PumpOperations();
	if (m_Scan && m_Scan->Done.load(std::memory_order_acquire))
		FinishScan();
	// Changes discarded since the last scan are offered at once: a scan queued now runs after their write. A scan expected
	// (ExpectScan) reads them too, once what it waits for is done.
	if (m_RescanDue && IsActive() && !IsScanning())
	{
		m_RescanDue = false;
		Scan();
	}
	if (!IsActive() || !m_Journal || !m_Changed)
		return;
	const auto now = std::chrono::steady_clock::now();
	if (SecondsBetween(m_LastChange, now) >= c_QuietSeconds || SecondsBetween(m_LastWrite, now) >= c_MaxIntervalSeconds)
		Write(scene, modified, false);
}
```

1. **Line 673:** the queue of file operations moves on every frame.
2. **Lines 678–682:** a discard asks for a new scan, which starts when none runs.
3. **Lines 683–684:** with nothing changed, there is nothing to write.
4. **Lines 685–687:** the write is due after 2 s of quiet or 10 s since the last write.

Two numbers follow. While you work without stopping, the write comes every 10 s, so a crash costs at most about 10 s of continuous work. When you stop, the write comes 2 s later. An edit after a long pause is written within a frame, because the last write is already more than 10 s old.

### Building the text and writing it

`Write` takes the steps that wait, and queues two operations. The first runs on a background worker (`JobPriority::Background`), because asset loads and mip reads share the input and output threads. It builds the text: it folds the steps into segments and writes them out as text. The second runs on an input and output job and writes the file. Writing the file replaces the old one only when the new one is complete.

The base hash comes from another operation, queued when the scene opens. The **base hash** is the SHA-256 of the saved scene file that a journal's changes apply to. The :term[hash]{id=hash} reads the file 1 MB at a time (`c_HashChunkBytes`), because a scene file can be hundreds of MB and the hash never needs it whole.

### Folding

The fold is the toy's idea in the real code. Inside the worker's function, each step either starts a segment or merges into the last one. The map of a segment keeps entity states by entity id, and a second list keeps the order in which they were first touched, so the file is the same every time it is written.

```cpp src="StrataEditor/src/Editor/SceneRecovery.cpp#L754-L765" from="for (const AppliedStep& step : steps)" to="segment.Order.push_back(states[index].ID);" symbol="SceneRecovery::Write"
for (const AppliedStep& step : steps)
{
	const std::vector<EntityState>& states = *step.States;
	// Steps that move no entity fold into the one before; those that do are replayed as they came.
	if (target.Segments.empty() || IsStructural(states, step.Prior.get()))
		target.Segments.emplace_back();
	Segment& segment = target.Segments.back();
	for (size_t index = 0; index < states.size(); index++)
	{
		const auto [entry, added] = segment.States.insert_or_assign(states[index].ID, std::make_pair(step.States, index));
		if (added)
			segment.Order.push_back(states[index].ID);
```

1. **Lines 758–759:** a segment starts for the first step or a structural one.
2. **Line 763:** a later state of an entity replaces an earlier one in the segment.
3. **Lines 764–765:** the first touch of an entity records its place in the order.

Compare it with the toy. The real `IsStructural` also compares sibling position and the cell of a world (a part of a large world that loads on its own), besides the parent. A segment holds a shared reference to the states of the step, plus an index, never a copy of the state. And the segments are kept between writes: each write adds only the steps since the last one, so its cost follows the edits and not the scene's size.

```cpp src="StrataEditor/src/Editor/SceneRecovery.cpp#L61-L77" symbol="IsStructural"
// Whether applying `states` over `prior` creates, removes or moves an entity (also into another cell of a world). Steps
// that do not can be folded into the step before them in a journal: positions recorded there stay what they were.
bool IsStructural(const std::vector<EntityState>& states, const std::vector<EntityState>* prior)
{
	if (!prior || prior->size() != states.size())
		return true;
	for (size_t index = 0; index < states.size(); index++)
	{
		const EntityState& after = states[index];
		const EntityState& before = (*prior)[index];
		if (after.ID != before.ID || after.Exists != before.Exists)
			return true;
		if (after.Exists && (after.Parent != before.Parent || after.SiblingIndex != before.SiblingIndex || after.Cell != before.Cell))
			return true;
	}
	return false;
}
```

1. **Lines 65–66:** with no earlier states, or a different count, the step is structural.
2. **Lines 71–72:** an entity that appears, disappears or changes its id is structural.
3. **Lines 73–74:** a new parent, sibling position or cell is a move.
4. **Line 76:** anything else folds.

### Scenes that were never saved

A scene that was never saved has no file to apply changes to, and so no base hash. Its journal is complete: it starts from an empty scene, with every entity the scene holds when it opens, and the steps follow. A step of kind Other turns any journal into a complete snapshot of every entity at the next write.

Both cases capture every entity on the main thread, and that has a price. A snapshot of a large scene would hold up a frame, so Strata snapshots only up to `c_MaxSnapshotEntities`, which is 256 entities. A never-saved scene that starts with more entities, or a larger scene after a step of kind Other, is not journaled until you save it. The journal says so: `scene.recoveryStatus` reports why in `skipped`, and asks for a save. The limit is the one place where the guarantee gets weaker, and Strata reports it rather than hiding it.

### Saves in progress

A save writes in the background, so edits can arrive while it runs, and without a token they would sit in neither the saved file nor the journal. The save holds a token from `BeginSave`, and the journal keeps the steps applied after the token's snapshot. When the save finishes, `OnSaved` removes the old journal and starts a new one for the saved document. The base hash is then the hash of the written document, and the new journal carries the steps made during the save. The new file replaces the old one before anything is removed.

### Discards

When the edited scene is replaced while it has changes not saved yet, `ResetScene` calls `EndScene`. It writes the journal at once with `Discarded` set, and the project's files are listed again so the changes are offered immediately. **Discarded** changes are recovery data that the editor wrote on purpose when a scene was replaced, so that they stay on offer.

An agent that discards scene after scene must not bury you in offers. A scan offers the newest eight discarded files (`c_MaxOfferedDiscards`), those that still apply first, and moves the rest to `Recovery/Discarded`, where 20 are kept (`c_MaxDiscardedFiles`). What a crash left is never moved.

:::why
Why keep what a person or an agent threw away? A discard is a decision made in a moment, often by a program that cannot know what the changes were worth. Writing the file costs one write. Losing an hour of work costs far more, and the person can still discard the file for good.
:::

### Offers, owners and moves

When a project opens, a scan lists the recovery files. It skips a file whose owner still runs and has not discarded it: another editor on the same project, or this one. The file records the process id and the process start time, because the system gives an id again to a later process. A crashed editor's id may belong to a new process, and only the start time tells them apart.

The scan also finds the scene by its handle, not its path. You may have renamed or moved the scene since, and the handle stays. For each file the scan checks that the scene asset still exists and that the scene file's hash equals the stored base hash; otherwise the entry is not applicable, and says why.

### Recovering

`scene.recover` with `apply` opens the scene in the background, as `scene.open` does. When it is in, the recovered states apply as one undo step back to the saved state. One **Undo** returns the scene to its saved form, and the scene stays modified so that you save it. The file is removed only after the new journal holds the same changes, so nothing is ever on neither disk place.

## Worked example: a crash and a recovery

:::example[Power fails two seconds after an edit]
You open `Main` and save at 14:00:00. The journal file does not exist. Then you work:

| Time | What you do | What the file holds |
| --- | --- | --- |
| 14:03:10 | Create `Crate` | Written within a frame: 1 segment, `Crate` |
| 14:03:20 to 14:03:24 | Drag `Crate` for 4 s | One merged step; written at 14:03:20 (10 s after the last write) and at 14:03:26; still 1 segment, `Crate` where you dropped it |
| 14:05:00 | Move `Rock` under `Crate` | Written within a frame: 2 segments |
| 14:05:01 | Change the color of `Rock` | Not written yet |
| 14:05:02 | Power fails | Segment 1 and 2 as at 14:05:00 |

You start the editor and open the project. A scan finds the file. The owner's process no longer runs, the scene is found by its handle, and the SHA-256 of `Main` equals the base hash, so the entry applies. The dialog offers it. With a command, the same steps read:

```json
{ "method": "scene.recoveryStatus", "params": {} }
```

Then:

```json
{ "method": "scene.recover", "params": { "scene": "Scenes/Main.stscene", "action": "apply" } }
```

The scene returns with `Crate` dropped where you left it and `Rock` under it. The color change of 14:05:01 is lost, because its write was due at 14:05:03.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Periodic full copy of the scene | Many content tools and engines | Recovery needs no saved file and no base hash | The whole scene file at every write, however little changed |
| Write-ahead log of every change | Databases | Nothing lost at all | A write before each change; a drag writes many times a second |
| Snapshot of every entity at every write | Simple periodic saves of a small scene | A file that never needs the saved scene | The main-thread capture, bounded to 256 entities |

## How it is tested

The suite `Editor.Recovery`, in `StrataTests/src/Editor/RecoveryTests.cpp`, runs the real editor context in a temporary project. Its harness runs commands, flushes the journal, closes the project to imitate a crash, and opens it again. The cases cover the timing, the worker, edits during a save, the owner check, discards and their limits, never-saved scenes and the size limit, damaged files and moved scenes. The drag case checks that 60 frames of one drag leave one waiting step and the final position.

Run the suite directly from the build folder of your preset:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Recovery
```

The filter runs only the cases of that suite.

## Changing it safely

A new kind of undo step takes part by returning entity states from `GetEntityStates` and a kind from `GetSceneChange`. A step of kind Other forces snapshots, which stop in scenes above 256 entities.

The rules that apply, with reasons:

- Write recovery files only in `SceneRecovery`, so the order of file operations holds.
- Write through a temporary file and a rename, so a crash leaves a whole file.
- Never block the main thread with a file operation or a text build. The snapshot is the only capture there, and its limit exists for that.
- Replace the scene only through `ResetScene`.

Before you finish, run `Editor.Recovery` and the other editor suites that open and close scenes.

## Summary

- A journal of the entity states since the last save, written against the hash of the saved file, beats periodic full copies on cost and write-ahead logs on simplicity.
- The journal is written once edits have stopped for 2 s, and every 10 s during continuous work; an edit after a long pause is written within a frame.
- A step that creates, removes or moves no entity folds into the segment before it, so the file grows with the structural edits only.
- A never-saved scene, or a step of kind Other, needs a snapshot taken on the main thread, so it is journaled only up to 256 entities; above that the status says why.
- A forced discard and `Don't Save` write the journal marked discarded, so the changes stay on offer.

## Check yourself

1. A scene file holds 100,000 entities and weighs 17 MB. An editor wrote a full copy every 10 s. How much does it write in one minute, and how does the journal differ?

   :::answer{tests="choose-journal"}
   Six copies of 17 MB are about 102 MB a minute, however little you changed. The journal writes the states of the
   touched entities and folds value edits, so its size follows the edits. It also builds its text on a worker and
   writes on an input and output job, so no frame waits.
   :::

2. The editor opens at 0 s, and you edit once a second from 1 s to 5 s, then stop. When is the journal written? (a) at 5 s, (b) at 7 s, (c) at 10 s.

   :::answer{tests="write-timing"}
   (b). The last edit is at 5 s, and the quiet limit of 2 s ends at 7 s. (a) would need a limit of 0 s. (c) is the cap
   of 10 s since the last write, which does not come first because the edits stop earlier.
   :::

3. Steps: create A; edit A; edit A; move A under another parent; edit A. How many segments? (a) 1, (b) 2, (c) 3.

   :::answer{tests="fold-segments"}
   (b). Create starts segment 1, and the two edits fold into it. The move is structural and starts segment 2,
   and the last edit folds into segment 2. (a) fails because the move is structural. (c) counts the edit after
   the move as a segment of its own, but a step that moves no entity never starts one.
   :::

4. You create a new scene from a template with 300 entities and edit it. A crash comes. What does recovery find, and what told you?

   :::answer{tests="snapshot-limit"}
   Nothing. A never-saved scene needs a snapshot of every entity, taken on the main thread, and only scenes up to 256
   entities get one. At 300 the changes are not journaled until you save. `scene.recoveryStatus` reports why in
   `skipped` for the journal of the edited scene. A save gives the scene a file, a base hash and a journal.
   :::

5. You press `Don't Save` and the scene changes. Where are your changes? (a) Gone. (b) In the recovery folder, marked discarded. (c) In the saved scene file.

   :::answer{tests="discard-kept"}
   (b). `ResetScene` calls `EndScene`, which writes the journal marked discarded and offers it. (a) is the outcome only
   when no project is open or the changes cannot be journaled. (c) is wrong: the saved file changes only when you save.
   :::

## Exercises

1. **Basic.** Edits come once a second from 1 s to 22 s, and the scene opened at 0 s. Predict every write time, then check it with a program that runs the timer in tenths of a second.

   :::answer[Worked solution]{tests="write-timing" solution="sketches/editor-recovery-timer.cpp"}
   The first write comes when 10 s have passed since the start, at 10 s. The next is 10 s later, at 20 s. The last edit
   is at 22 s, so the quiet limit writes at 24 s.

   ```cpp sketch="editor-recovery-timer.cpp"
   // The journal's write timer: an edit every second from 1 s to 22 s, time counted in tenths of a second.
   #include <cstdio>

   constexpr int c_QuietTicks = 20;
   constexpr int c_MaxIntervalTicks = 100;

   int main()
   {
   	int lastChange = 0;
   	int lastWrite = 0;
   	bool changed = false;
   	for (int now = 0; now <= 300; now++)
   	{
   		if (now % 10 == 0 && now >= 10 && now <= 220)
   		{
   			changed = true;
   			lastChange = now;
   		}
   		if (changed && (now - lastChange >= c_QuietTicks || now - lastWrite >= c_MaxIntervalTicks))
   		{
   			std::printf("write at %d.%d s\n", now / 10, now % 10);
   			changed = false;
   			lastWrite = now;
   		}
   	}
   }
   ```

   ```text output-of="editor-recovery-timer.cpp"
   write at 10.0 s
   write at 20.0 s
   write at 24.0 s
   ```

   1. **Lines 14–18:** an edit arrives once a second, and sets the change flag and the time of the last change.
   2. **Lines 19–24:** the write is due after 2 s of quiet or 10 s since the last write, and it resets the flag.
   :::

2. **Medium.** On paper, write the segments for: create A, rename A, create B, color B, move B under A, color A. Then add a case to `Editor.Recovery` that produces the same steps through commands and checks the file.

   :::answer[Worked solution]{tests="fold-segments"}
   Create A starts segment 1, and the rename folds into it. Create B starts segment 2, and the color folds into it.
   Moving B is structural and starts segment 3 with B, and the color of A folds into it, so the segments hold 1, 1 and 2
   states, with B before A in the last. For the test, use `RecoveryHarness` to run commands that make these steps, call
   `FlushJournal`, read the file with `SceneRecovery::Read`, and check that `Data->Steps` has sizes 1, 1 and 2. The case
   was not run.
   :::

3. **Hard.** Trace it yourself: with a breakpoint in `SceneRecovery::OnApplied`, make one edit in a saved scene, wait 2 s, and find the file that the quiet timer wrote.

   :::answer[Worked solution]{tests="write-timing fold-segments"}
   The breakpoint stops in `OnApplied` in `StrataEditor/src/Editor/SceneRecovery.cpp`. The edit lands in `m_PendingSteps`
   and `m_LastChange` is set. `EditorContext::Update` calls `SceneRecovery::Update` each frame, which calls `Write`
   once 2 s have passed. `Write` queues two operations through `Enqueue`: the text on a background worker, then the file
   through `WriteFileReplacing`. The file is under `<project>/.strata/Recovery`, named with the scene's handle and a session id, with the extension `.strecovery`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/SceneRecovery.h` and `SceneRecovery.cpp`: the journal, `OnApplied`, `Update`, `Write`, `IsStructural`, `EndScene`, `BeginSave`, `OnSaved` and the scan.
- `StrataEditor/src/Editor/EditorContext.cpp`: `ResetScene`, which calls `EndScene`, and `ApplyRecovery`.
- `StrataEditor/src/Editor/EditorStateCommands.cpp`: `scene.recoveryStatus` and `scene.recover`.
- `StrataTests/src/Editor/RecoveryTests.cpp`: the suite `Editor.Recovery`.
- Files: `<project>/.strata/Recovery/*.strecovery` and `Recovery/Discarded`.

## Further reading

- Database systems that use a write-ahead log: what a log is and why it is replayed after a crash (intermediate).
- Operating system texts on atomic rename: why a rename leaves the old file or the new one (beginner).
