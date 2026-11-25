---
id: editor/journal
title: "The activity journal and replays"
description: "How the editor records every command with its origin, shows agent work to the person, and turns a session into a script that repeats it."
kind: internals
size: M
tracks: [E]
needs: [editor/undo, editor/command-scripts]
time: 60
learn:
  - id: record-journal
    text: explain what the journal records for each command, where it records it and what it keeps
  - id: origin-rule
    text: explain why UI code passes its origin and how the person is told what others did
  - id: build-replay
    text: trace how an export finds the edits to repeat and turns IDs into references in two passes
  - id: replay-limits
    text: name what a replay cannot repeat and how the export counts it
  - id: choose-kind
    text: choose the kind of a new command so that the journal and a replay treat it right
since: 0.3.0
status: final
---

When a person and an agent share an editor, two questions come up at once. What did the agent do a moment ago, and can I undo it? The **activity journal** is the editor's record of every command it ran: who ran it, with what parameters, how it ended and which entities it touched. Two features grow from that record: the Activity panel with the agent's presence in the interface, and a script that repeats a whole session on a fresh copy of a project.

The journal does not undo anything and does not run anything. It remembers, and the undo history and the :term[command scripts]{id=command-script} do the rest.

## The problem and how engines solve it

An editor that people and programs drive together needs accountability, a way to see afterwards who changed what. Logs, undo histories, :term[macro]{id=macro} recorders and event sourcing each give part of it, with different costs. [Agents and accountability](../automation/agents.md) compares them. Strata keeps one record, written in the single function that runs every command, and builds its three uses on it: the person's view, the agent's presence and the replay.

## The map

Every command, whoever starts it, passes through `EditorCommandRegistry::Execute`. That function asks the journal to begin an entry, runs the command, and completes the entry. Everything else reads the ring of entries. All of it runs on the :term[main thread]{id=main-thread}, because the journal is not thread-safe and does not need to be.

```mermaid caption="Commands from three sources pass through one function, which writes the journal. The panel, the query command and the export read it, and a replay runs the exported script on a copy." alt="A flow from the person, an agent and a command script into one execute step, which writes a journal. The journal feeds a panel, a query command and an export. The export makes a script that runs on a copy of the project, and a comparison checks the copy."
flowchart LR
  P[Person] --> X[Execute]
  A[Agent] --> X
  S[Command script] --> X
  X --> J[(Journal ring)]
  J --> V[Activity panel]
  J --> Q[editor.activity]
  J --> E[editor.activity.export]
  E --> R[Replay script]
  R --> C[Run on a copy]
  C --> D[Compare documents]
```

The files are small. `StrataEditor/src/Editor/CommandJournal.h` and `CommandJournal.cpp` hold the entries, the ring and the replay builder. `StrataEditor/src/Editor/EditorCommands.cpp` calls them. The two commands live in `StrataEditor/src/Editor/EditorStateCommands.cpp`, and the panel in `StrataEditor/src/Panels/ActivityPanel.cpp`.

## What one entry holds

An entry answers the questions of a review.

The **origin** says who ran the command, and it is one of four sources. `UI` is the person through the interface. `Automation` is a tool or an agent, with the name the client gave when it connected. `CommandScript` is a script given with `--commands`. `Internal` is the editor itself, or a command that another command ran: such a command is a child of its parent entry, whoever started the parent.

The rest of the entry describes the run. It holds the command's name and kind, its parameters, and whether it succeeded, with the error or warning. It adds a summary of the result, the identifiers (IDs) the result holds, the time it took and the frames it needed.

The entry also holds the entities its :term[undo step]{id=undo-step} touched, at most 256, and the name of that step. Parameters stay whole up to 256 KiB. A larger set is shortened and marked, and the entry can no longer be run again exactly.

The journal keeps at most 2,000 entries and 8 MB; the oldest go first, and the newest always stays. A :term[deferred command]{id=deferred-command}, one that finishes over several frames, gets its entry at once, as pending. The entry completes on the command's final poll, so each command is recorded once, with its real end. See [Commands that take frames](../editor/deferred-commands.md) for how those polls work.

## The contract

Code that runs commands, and code that reads the journal, follows a few rules. Each has a reason.

- **Pass the origin.** User interface (UI) code runs a command with `CommandOrigin { CommandSource::UI }`. An omitted origin is recorded as `Internal`, and the journal would no longer say who did what.
- **Declare the kind.** A command is `Edit`, `Query` or `Session`. A replay repeats `Edit` commands only, so the kind decides what a replay holds. A command with no kind counts as an edit, the safe default: a replay may repeat too much, never too little.
- **Run commands through `Execute`.** A change made another way is invisible to the journal.
- **Record undo steps by commands where you can.** Steps recorded directly are counted, not repeated.

:::rule
UI code passes `CommandOrigin { CommandSource::UI }`, so the journal says who did what. The reason is the one above: the person's actions and an agent's actions look the same without the origin, and the notices below depend on it. The rule is stated in `AGENTS.md`, and the [command conventions](../editor/commands.md) explain the rest of the registry's contract.
:::

### Telling the person what happened

The person must learn what others did, and need not be told what they did themselves. Strata decides by the outermost running command's origin. When an agent or a script deletes an asset or a folder, or replaces the scene and discards changes that were not saved, the editor posts a notification. It names the client ("An agent deleted an asset") and says where the changes went.

When the origin is `UI` or `Internal`, the person saw it happen, and an asset delete posts nothing. A person's own discard posts a notice only to offer the recovery data.

The same record feeds **presence**, the part of the interface that shows an agent working. The journal keeps the latest finished command that came from automation, ran at the top level and changed something: its name, client, outcome and entities. A query after an edit leaves it alone, so the display keeps naming the edit. The drawing is for the [Scene view](../editor-ui/scene-view.md), and the Activity panel, which lists commands of the person, an agent and a script, is for [the instrument panels](../editor-ui/instrument-panels.md).

A command script ran every row of the picture below, so each row shows the script's icon, a scroll. Rows that the person ran show a mouse pointer, and rows of an agent show a robot.

::figure{id=activity-panel}

A summary reads like "Rename 'Crate' to 'Box'": the name of the undo step the command recorded. An error shows its first line, a warning shows itself, and a forced scene replace shows "discarded changes".

## Edits outside commands

Not every change is a command. Dragging a :term[gizmo]{id=gizmo-start} or typing in an inspector field records its undo step directly, because it must merge a hundred frames of motion into one step. The journal cannot hold such a change as a command. **Edits outside commands** are the undo steps that continuous UI edits record directly, which the journal counts but cannot repeat.

The count works by watching the undo history. Before every top-level command, the journal compares the history's record count with what it saw last. New records mean someone edited outside a command. A drag of a hundred frames is one step however many merges made it, so it counts once.

## A toy version

The toy below keeps the central idea of the replay builder and nothing else. A session is a list of entries. Each has a kind, the ID its parameters name and the ID its result holds. The builder walks the list twice and prints the commands a replay would run.

:::question
New to C++ lists, functions and :term[structs]{id=struct}? Read [programming 1](../basics/programming-1.md), [programming 2](../basics/programming-2.md) and [programming 3](../basics/programming-3.md) first.
:::

The program has seven entries. A creation makes an entity with the ID `A7`, which will differ in every run. A selection query also answers `A7`, but its answer is the session's own state, so the replay will not use it.

The toy marks it `Session` to keep one flag; in Strata `selection.get` is a `Query` whose results are declared to follow the session, which has the same effect. A search finds the template's sun, `B1`, which exists in every copy. Another search finds a crate that no edit uses, and one rename names an ID that no entry produced.

Search for what the second loop adds and what the printing omits.

```cpp sketch="editor-journal-toy.cpp"
#include <cstdio>
#include <string>
#include <vector>

enum class Kind { Edit, Query, Session };

struct Entry
{
	int Id = 0;
	std::string Command;
	Kind CommandKind = Kind::Edit;
	std::string Target;   // The ID the command's parameters name, or empty
	std::string Argument; // Another parameter, or empty
	std::string Produced; // The ID its result holds, or empty
};

static int FindProducer(const std::vector<Entry>& entries, const std::vector<bool>& producing, size_t before, const std::string& id)
{
	for (size_t i = 0; i < before; i++)
	{
		if (producing[i] && entries[i].Produced == id)
			return static_cast<int>(i);
	}
	return -1;
}

static void PrintReplay(const std::vector<Entry>& entries)
{
	const size_t count = entries.size();
	std::vector<bool> producing(count, false);
	std::vector<bool> needed(count, false);
	std::vector<bool> bound(count, false);
	std::vector<int> producer(count, -1);

	// Forward: which entry gave each ID first, and which entries are edits.
	for (size_t i = 0; i < count; i++)
	{
		const Entry& entry = entries[i];
		if (!entry.Target.empty())
			producer[i] = FindProducer(entries, producing, i, entry.Target);
		needed[i] = entry.CommandKind == Kind::Edit;
		producing[i] = entry.CommandKind != Kind::Session && !entry.Produced.empty();
	}

	// Backward: an edit pulls in the entry that gave it an ID.
	for (size_t i = count; i-- > 0;)
	{
		if (!needed[i] || producer[i] < 0)
			continue;
		needed[producer[i]] = true;
		bound[producer[i]] = true;
	}

	for (size_t i = 0; i < count; i++)
	{
		if (!needed[i])
			continue;
		std::printf("%s", entries[i].Command.c_str());
		if (!entries[i].Target.empty() && producer[i] >= 0)
			std::printf(" target=$ref(e%d)", entries[producer[i]].Id);
		else if (!entries[i].Target.empty())
			std::printf(" target=%s", entries[i].Target.c_str());
		if (!entries[i].Argument.empty())
			std::printf(" name=%s", entries[i].Argument.c_str());
		if (bound[i])
			std::printf(" bind=e%d", entries[i].Id);
		std::printf("\n");
	}
}

int main()
{
	const std::vector<Entry> session = {
		{ 1, "entity.create", Kind::Edit, "", "", "A7" },
		{ 2, "selection.get", Kind::Session, "", "", "A7" },
		{ 3, "entity.find", Kind::Query, "", "Sun", "B1" },
		{ 4, "entity.rename", Kind::Edit, "A7", "Box", "" },
		{ 5, "entity.rename", Kind::Edit, "B1", "Lamp", "" },
		{ 6, "entity.find", Kind::Query, "", "Crate", "C2" },
		{ 7, "entity.rename", Kind::Edit, "Z9", "Old", "" } };
	PrintReplay(session);
	return 0;
}
```

```text output-of="editor-journal-toy.cpp"
entity.create bind=e1
entity.find name=Sun bind=e3
entity.rename target=$ref(e1) name=Box
entity.rename target=$ref(e3) name=Lamp
entity.rename target=Z9 name=Old
```

1. **Lines 36–43:** the forward loop notes the producer of each target and the edits; session answers never produce.
2. **Lines 46–52:** the backward loop marks the producer that an edit needs and binds it.
3. **Lines 54–68:** only needed entries print, a target as a reference when a producer exists.

The output shows five of the seven entries. The creation is bound, as `e1`, because a later rename uses its result. The search for the sun stays, because the rename of the sun needs a value from it, and it is bound too. The selection query and the unused search are gone. The last rename keeps its ID as it is, because nothing in the session produced it: the project already had that entity.

## The real code

The real journal differs from the toy in what it must survive: nested commands, commands that finish over frames, parameters too large to copy, and a ring that forgets. The data flows in the order of a command's life, so the code is read in that order.

### Recording

`Execute` first lets the journal count edits outside commands, then begins the entry before the handler runs. The second half runs after it. Search for the two paths: a pending command and a finished one.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L144-L153" from="// A step the handler recorded (or extended) is the command's." to="journal.Complete(entry, result);" symbol="EditorCommandRegistry::Execute"
// A step the handler recorded (or extended) is the command's.
journal.NoteUndo(entry, undo, records);
result.JournalId = entry;
if (result.IsPending())
{
	journal.Suspend(entry);
}
else
{
	journal.Complete(entry, result);
```

1. **Line 145:** the journal compares the undo history's record count with the count taken before the handler ran.
2. **Lines 147–150:** a pending command stops being the running one, and its entry stays pending.
3. **Line 153:** a command that finished completes its entry at once.

`Begin` decides the origin and the size.

```cpp src="StrataEditor/src/Editor/CommandJournal.cpp#L431-L440" from="// A command that runs inside another one belongs to it, whoever the outer one came from." to="entry.Client = origin.Client;" symbol="CommandJournal::Begin"
// A command that runs inside another one belongs to it, whoever the outer one came from.
if (!m_Running.empty())
{
	entry.Parent = m_Running.back();
	entry.Source = CommandSource::Internal;
}
else
{
	entry.Source = origin.Source;
	entry.Client = origin.Client;
```

1. **Lines 432–436:** a command run inside another becomes its child with the source `Internal`.
2. **Lines 438–440:** a top-level command keeps the origin it was given.

`NoteEditsOutsideCommands` is the counter.

```cpp src="StrataEditor/src/Editor/CommandJournal.cpp#L496-L510" symbol="CommandJournal::NoteEditsOutsideCommands"
void CommandJournal::NoteEditsOutsideCommands(const UndoStack& undo)
{
	if (!m_Running.empty())
		return;
	const uint64_t records = undo.GetRecordCount();
	const uint64_t steps = undo.GetStepCount();
	if (records > m_SeenUndoRecords)
	{
		// Steps count once however many merges made them (a drag of a hundred frames is one edit); merges alone, into a step
		// recorded before, count as one edit more.
		m_EditsOutsideCommands += std::max<uint64_t>(steps > m_SeenUndoSteps ? steps - m_SeenUndoSteps : 0, 1);
	}
	m_SeenUndoRecords = records;
	m_SeenUndoSteps = std::max(m_SeenUndoSteps, steps);
}
```

1. **Line 498:** while a command runs, its own steps belong to it, so nothing is counted.
2. **Line 502:** new undo records since the last look mean someone edited outside a command.
3. **Line 506:** the count adds the new steps, at least one, so a drag of many merges counts once.

### Building the replay

`BuildReplayScript` starts by refusing a ring that has forgotten the start. When the oldest entry kept is newer than `since` plus one, entries are missing, and a script without them would build another scene. It then keeps the successful top-level entries after `since`. A batch of commands repeats as its steps, never as both.

```cpp src="StrataEditor/src/Editor/CommandJournal.cpp#L749-L773" from="const bool edit = entry.Kind == EditorCommandKind::Edit && !entry.RunningCopy;" to="produced.emplace(id, ReplayReference { index, pointer });" symbol="CommandJournal::BuildReplayScript"
const bool edit = entry.Kind == EditorCommandKind::Edit && !entry.RunningCopy;
if (entry.Kind == EditorCommandKind::Edit && entry.RunningCopy)
	script.SkippedWhilePlaying++;
// Other commands that recorded an undo step changed the scene in a way the script cannot repeat (scene.recover
// applies a recovery file the copy does not have).
if (entry.Kind != EditorCommandKind::Edit && entry.UndoSerial != 0)
	script.UnrepeatableEdits++;
if (edit && entry.ParametersTruncated)
{
	return fail(fmt::format("The parameters of #{} ({}) were too large to keep in the journal, so it cannot be repeated: export from since {} "
		"or later", entry.Id, entry.Command, entry.Id));
}
parameters[index] = ReplaceProducedIds(entry.Parameters, produced, literal, references[index], entryIds);
needed[index] = edit;
// Results of edits and queries give IDs a replay takes from its own run. Those of session commands (the projects and
// scenes they open), of edits of the running copy and queries while playing (the running copy's entities have the
// edited scene's IDs, and what play created is gone after play.stop) and the handles of built-in assets name what
// every run has: they stay as they are. Queries whose results follow the session (the selection) collect no IDs.
const bool producing = edit || (entry.Kind == EditorCommandKind::Query && !entry.Playing);
for (const auto& [pointer, id] : entry.ResultIds)
{
	if (!producing || BuiltinAssets::IsBuiltin(id))
		literal.insert(id);
	else if (!literal.contains(id) && !produced.contains(id))
		produced.emplace(id, ReplayReference { index, pointer });
```

1. **Line 749:** only a top-level `Edit` that did not change the :term[running copy]{id=running-copy} is an edit to repeat.
2. **Lines 754–755:** a command of another kind that recorded an undo step counts as an edit that a script cannot repeat.
3. **Line 761:** the parameters are rewritten, so earlier results become references.
4. **Line 767:** only edits and queries outside :term[play mode]{id=play-mode} produce IDs a replay takes from its own run.
5. **Lines 770–773:** built-in handles stay literal, and the first producer of an ID wins.

The backward pass walks the entries from the last to the first, so a producer pulled in by a late edit can itself pull in an earlier one.

```cpp src="StrataEditor/src/Editor/CommandJournal.cpp#L779-L786" from="for (size_t index = entries.size(); index-- > 0;)" to="binds[reference.Producer].insert(reference.Pointer);" symbol="CommandJournal::BuildReplayScript"
for (size_t index = entries.size(); index-- > 0;)
{
	if (!needed[index])
		continue;
	for (const ReplayReference& reference : references[index])
	{
		needed[reference.Producer] = true;
		binds[reference.Producer].insert(reference.Pointer);
```

1. **Line 781:** only needed entries pull in others, so an unused lookup stays out.
2. **Lines 783–786:** each reference marks its producer as needed and notes the pointer to bind.

A **replay script** is the command script that this builder makes from the journal to repeat a session. The forward pass rewrites parameters through `ReplaceProducedIds`: a value equal to an ID that an earlier entry produced becomes `{"$ref": "e12.id"}`. The binding's name is the entry's number and the :term[JSON pointer]{id=json-pointer} of the ID in the result, with `/` written as `.`. The last step writes each needed entry as a step, with `bind` where later steps refer to it. How such a script runs is the subject of [command scripts](../editor/command-scripts.md).

## Reading a replay

:::example[Export your session as a regression script]
Start an editor with a project open and `StrataCLI` attached. Create an entity and rename it from a terminal, then drag the entity in the Scene view by hand. Export the session.

```sh
StrataCLI call entity.create '{"name": "Crate"}'
StrataCLI call entity.rename '{"entity": "<the ID that entity.create returned>", "name": "Box"}'
StrataCLI call editor.activity.export '{"path": "Session.json"}'
```

The export returns `steps`, `edits`, `lookups`, `bindings` and three counts of what the script omits: `skippedWhilePlaying`, `editsOutsideCommands` and `unrepeatableEdits`. For this session, expect two steps and two edits. `editsOutsideCommands` is 1 for the drag, and a `warning` says so: the script does not repeat it. The file holds one step that creates and binds, and one that refers to the binding.

```json
[
	{ "command": "entity.create", "parameters": { "name": "Crate" }, "bind": { "e12.id": "/id" } },
	{ "command": "entity.rename", "parameters": { "entity": { "$ref": "e12.id" }, "name": "Box" } }
]
```

The number 12 is the entry of the creation in this editor's journal; yours differs. The script replays on a copy of the project as it was at the start, and the copy then holds an entity named `Box` with a new ID, never the old one.
:::

### What a replay cannot hold

A replay repeats commands on a copy, so what no command did is missing from it. Four cases matter:

- Edits outside commands: inspector fields, gizmo drags and the material editor. The export counts them in `editsOutsideCommands`, and a warning names them.
- IDs taken from the selection or from `editor.status` stay as they are, because the replay does not repeat the selection. They work for what the project already had.
- What `scene.recover` applied: the recovery file is not in a copy. The export counts it in `unrepeatableEdits`.
- Files no command wrote, such as script sources an agent edited or :term[source assets]{id=source-file} it generated. The fresh copy needs its `Scripts/` folder before the script runs.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Text log of calls | Many servers | Simple to search | No structure to rebuild a script from |
| Undo history only | Most editors | Already present, no new code | No origin, no failures, no queries, and undone steps vanish |
| Macro recorder of input events | Office tools | Records edits outside commands too | A replay breaks when a window moves |
| Event sourcing of all state | Some databases | Every state can be rebuilt | Every change must be an event, even a drag |
| Per-client journal | Multi-user tools | Each client replays its own work | No single view of what happened in order |

The choice costs a gap: edits outside commands. Strata takes that cost because a gizmo drag would otherwise need a command per frame, and the counts say honestly what the replay misses.

## How it is tested

The suite `Editor.Journal` checks several rules. Commands of every source are recorded once with their client, and a deferred command is recorded when it finishes. Failures carry their kind, the ring keeps at most 2,000 entries and 8 MB, and every built-in command declares its kind. `Editor.CommandScriptBindings` checks the script side of the references. `Editor.Replay` runs an agent's session in process, replays it on a fresh copy and compares the scene and the assets.

The CTest test `StrataEditor.Replay`, built from `StrataTests/Editor/ReplaySession.cmake`, does the same with the real editor program: it exports a session, replays it on a copy and compares the documents.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Journal
ctest --preset windows-debug -R StrataEditor.Replay
```

The first line runs the journal's own suite, and the second runs the end-to-end replay through CTest.

## Changing it safely

To add a command whose work the journal records and a replay repeats, you register it with a kind and make it a command that can be undone. An edit changes the scene, assets or project files. A query reads, waits or renders. A session command changes only the editor's state.

Declare the kind, because the test `Every built-in command declares the kind its effect calls for, and which results follow the session` fails otherwise. If the result holds IDs that follow the session, such as the selection, declare that too, so a replay never binds them.

- Never record a command's work behind the journal's back. Edits that skip `Execute` cannot be replayed.
- Keep the journal on the main thread. Its entries are plain data, and no lock protects them.
- When you add a field to an entry, count its :term[bytes]{id=byte}, or the 8 MB limit stops being true.
- After a change, run `Editor.Replay` and `StrataEditor.Replay`.

## Summary

- The journal records every command once, in `Execute`, with its origin, kind, parameters, outcome, result IDs, duration, entities and undo step, in a ring of 2,000 entries and 8 MB.
- UI code passes the `UI` origin so the journal says who did what, and the person is told what agents and scripts did, never what they did themselves.
- An export finds the edits to repeat, binds the IDs that results gave first in a forward pass, and adds the lookups the edits need in a backward pass.
- A replay cannot hold edits outside commands, IDs from the selection, what `scene.recover` applied and files no command wrote; the export counts the first and the third.
- A new command declares its kind: only `Edit` commands are repeated, and a command with no kind counts as `Edit`.

## Check yourself

1. A new button of the tool bar runs `Execute` with no origin. What does the journal record, and what goes wrong?

   :::answer{tests="origin-rule,record-journal"}
   The source is `Internal`, so the entry no longer says the person acted. Notices that depend on the origin treat the action as the person's, which is right here, but the Activity panel cannot tell it from the editor's own work. The fix is to pass `CommandOrigin { CommandSource::UI }`.
   :::

2. An agent sends an `Edit` command whose parameters are 300 KiB. What does the journal keep, and what does an export do?

   :::answer{tests="record-journal,build-replay"}
   The journal shortens the parameters and marks the entry, because 300 KiB is above the limit of 256 KiB. An export that needs that command fails and says to export from a later entry; the command cannot be run again exactly.
   :::

3. In the toy's session, `entity.find` for the crate (entry 6) is dropped. Entry 5 renames the sun, found by entry 3. What would change if entry 6 had a rename that used `C2`?

   :::answer{tests="build-replay"}
   The backward pass would mark entry 6 as needed, because an edit refers to its result. The replay would then hold the search as a bound lookup, and the rename would use `$ref(e6)`.
   :::

4. Which of these does a replay hold: a gizmo drag, `entity.rename`, `selection.set`, `scene.recover`? Which are counted?

   :::answer{tests="replay-limits"}
   Only `entity.rename`. The drag is counted as an edit outside commands, `scene.recover` as an edit that a script cannot repeat, and `selection.set` is a `Session` command that changes no project content, so nothing counts it.
   :::

5. A new command writes a generated image into the project's `Assets` folder. Which kind is right: `Edit`, `Query` or `Session`? What happens with no kind?

   :::answer{tests="choose-kind"}
   `Edit`, because it changes the project's files, and a replay must repeat it. With no kind the command counts as an edit, so the replay still repeats it; the declaration only makes the intent explicit, and the kinds test requires it.
   :::

## Exercises

1. **Basic.** A session ran 2,100 small commands without a break. You call `editor.activity.export` with `since` 0. What happens, and what should you do?

   :::answer[Worked solution]{tests="record-journal,build-replay"}
   The ring keeps 2,000 entries, so entries 1 to 100 are gone and the oldest kept is 101. The export fails, since 101 is larger than 0 plus 1, and its message names entries 1 to 100 and tells you to export from since 100 or later. A script from 100 on still has to start from a project as it was at entry 100.
   :::

2. **Medium.** Extend the toy so that it counts commands that are not edits yet changed the scene, like `scene.recover`, and prints a warning line.

   :::answer[Worked solution]{solution="sketches/editor-journal-unrepeatable.cpp" tests="build-replay,replay-limits"}
   The entry gets a flag for an undo step. In the forward loop, a non-edit entry with the flag adds to a counter, and the function returns the count for `main` to print.

   ```cpp sketch="editor-journal-unrepeatable.cpp"
   #include <cstdio>
   #include <string>
   #include <vector>

   enum class Kind { Edit, Query, Session };

   struct Entry
   {
   	int Id = 0;
   	std::string Command;
   	Kind CommandKind = Kind::Edit;
   	std::string Target;        // The ID the command's parameters name, or empty
   	std::string Argument;      // Another parameter, or empty
   	std::string Produced;      // The ID its result holds, or empty
   	bool ChangedScene = false; // It recorded an undo step
   };

   static int FindProducer(const std::vector<Entry>& entries, const std::vector<bool>& producing, size_t before, const std::string& id)
   {
   	for (size_t i = 0; i < before; i++)
   	{
   		if (producing[i] && entries[i].Produced == id)
   			return static_cast<int>(i);
   	}
   	return -1;
   }

   static size_t PrintReplay(const std::vector<Entry>& entries)
   {
   	const size_t count = entries.size();
   	std::vector<bool> producing(count, false);
   	std::vector<bool> needed(count, false);
   	std::vector<bool> bound(count, false);
   	std::vector<int> producer(count, -1);
   	size_t unrepeatable = 0;

   	// Forward: which entry gave each ID first, and which entries are edits.
   	for (size_t i = 0; i < count; i++)
   	{
   		const Entry& entry = entries[i];
   		if (!entry.Target.empty())
   			producer[i] = FindProducer(entries, producing, i, entry.Target);
   		needed[i] = entry.CommandKind == Kind::Edit;
   		if (entry.CommandKind != Kind::Edit && entry.ChangedScene)
   			unrepeatable++;
   		producing[i] = entry.CommandKind != Kind::Session && !entry.Produced.empty();
   	}

   	// Backward: an edit pulls in the entry that gave it an ID.
   	for (size_t i = count; i-- > 0;)
   	{
   		if (!needed[i] || producer[i] < 0)
   			continue;
   		needed[producer[i]] = true;
   		bound[producer[i]] = true;
   	}

   	for (size_t i = 0; i < count; i++)
   	{
   		if (!needed[i])
   			continue;
   		std::printf("%s", entries[i].Command.c_str());
   		if (!entries[i].Target.empty() && producer[i] >= 0)
   			std::printf(" target=$ref(e%d)", entries[producer[i]].Id);
   		else if (!entries[i].Target.empty())
   			std::printf(" target=%s", entries[i].Target.c_str());
   		if (!entries[i].Argument.empty())
   			std::printf(" name=%s", entries[i].Argument.c_str());
   		if (bound[i])
   			std::printf(" bind=e%d", entries[i].Id);
   		std::printf("\n");
   	}
   	return unrepeatable;
   }

   int main()
   {
   	const std::vector<Entry> session = {
   		{ 1, "entity.create", Kind::Edit, "", "", "A7", false },
   		{ 2, "selection.get", Kind::Session, "", "", "A7", false },
   		{ 3, "entity.find", Kind::Query, "", "Sun", "B1", false },
   		{ 4, "entity.rename", Kind::Edit, "A7", "Box", "", false },
   		{ 5, "entity.rename", Kind::Edit, "B1", "Lamp", "", false },
   		{ 6, "entity.find", Kind::Query, "", "Crate", "C2", false },
   		{ 7, "entity.rename", Kind::Edit, "Z9", "Old", "", false },
   		{ 8, "scene.recover", Kind::Session, "", "", "", true } };
   	const size_t unrepeatable = PrintReplay(session);
   	if (unrepeatable > 0)
   		std::printf("warning: %zu edit(s) came from commands a script does not repeat\n", unrepeatable);
   	return 0;
   }
   ```

   ```text output-of="editor-journal-unrepeatable.cpp"
   entity.create bind=e1
   entity.find name=Sun bind=e3
   entity.rename target=$ref(e1) name=Box
   entity.rename target=$ref(e3) name=Lamp
   entity.rename target=Z9 name=Old
   warning: 1 edit(s) came from commands a script does not repeat
   ```

   1. **Line 45:** the real builder counts exactly these entries as `UnrepeatableEdits`.
   :::

3. **Hard.** Trace it yourself. Create an entity with `entity.create`, rename it with `entity.rename`, export the session, and find where the rename's entity ID becomes a `$ref`.

   :::answer[Worked solution]{tests="build-replay"}
   Put a breakpoint in `CommandJournal::BuildReplayScript` in `StrataEditor/src/Editor/CommandJournal.cpp`, at the call of `ReplaceProducedIds`. For the rename it finds the creation's ID in `produced` and returns the object with `$ref`, built from `MakeBindingName`. The backward loop then marks the creation as needed and records the pointer to bind.
   :::

## Where it lives in Strata

- Journal: `StrataEditor/src/Editor/CommandJournal.h` and `CommandJournal.cpp` (`CommandJournal`, `CommandJournalEntry`, `BuildReplayScript`).
- Recording: `EditorCommandRegistry::Execute` in `StrataEditor/src/Editor/EditorCommands.cpp`.
- Commands: `editor.activity` and `editor.activity.export` in `StrataEditor/src/Editor/EditorStateCommands.cpp`.
- Notices: `EditorContext::NotifyDiscardedChanges` and `NotifyAssetsTrashed` in `StrataEditor/src/Editor/EditorContext.cpp`.
- Panel: `StrataEditor/src/Panels/ActivityPanel.cpp`.
- Tests: suites `Editor.Journal`, `Editor.CommandScriptBindings` and `Editor.Replay` in `StrataTests/src/Editor/`, and the CTest test `StrataEditor.Replay`.

## Further reading

- Martin Fowler, "Event Sourcing": why recording every change as an event allows a state to be rebuilt. Intermediate.
- Robert Nystrom, "Game Programming Patterns", the Command pattern: commands as objects that can be recorded. Beginner.
