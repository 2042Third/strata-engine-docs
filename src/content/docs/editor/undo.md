---
id: editor/undo
title: "Undo and redo"
description: "How the editor records every edit as one step it can reverse: the history, the scene's entity states, merging, groups and save points."
kind: internals
size: XL
tracks: [E]
needs: [editor/commands, world/serialization]
time: 140
learn:
  - id: history-rules
    text: explain what the history does with a new edit, a merge, a failed undo, a failed redo and a save
  - id: compare-approaches
    text: compare four ways to build undo and choose one for a given kind of edit
  - id: scene-edits
    text: trace how a scene edit is captured as entity states and put back in three batches
  - id: write-step
    text: write an undo step for a change outside the scene, with a check of its precondition
  - id: predict-history
    text: predict the steps, the position and the modified flag after a list of edits, undos and saves
since: 0.3.0
status: final
---

Every change you make in the editor can be taken back, and so can every change an agent makes through a command. This page explains how. The editor keeps a list of steps, each of which knows how to reverse itself, and a position in that list. This page covers the list, the steps for the scene, the steps for files and settings, and the gate that every scene edit passes. It does not cover how a save runs in the background, how the recovery journal follows the list, or what the trash does with files: those have their own pages.

## The problem and how engines solve it

You drag a slider and the light gets too bright. You press **Ctrl+Z** and expect the light to return to the value it had before you touched the slider, not to the value it had a tenth of a second ago. That is the first rule: an **undo step** is one action as the person meant it, however many small changes it made. A drag that changes a value 90 times in 1.5 seconds is one step, and so is deleting 40 objects. A command that an agent sends is one step, even when it changes a hundred entities.

The second rule is that steps differ in size and in kind. One step changes a number. Another removes a parent and all its children, and each child has components, a place among its siblings and links from other entities that point at it. A third step renames a file on disk, and the file is outside the scene altogether. One mechanism has to reverse all of them.

The third rule is that the world can change between the step and its undo. You rename a file, then something else creates a file with the old name, then you press undo. A good history notices that it can no longer do what it promised, says so, and does not leave a half-reversed result.

Engines solve this in four main ways, and a small thought experiment shows what each costs. Suppose a scene holds 10,000 entities, and suppose each one written out as data takes about 2 KB, a round number chosen to keep the arithmetic simple. The whole scene is then about 20 MB. A history that keeps 512 steps would need about 10 GB if it stored the whole scene at each step. That cannot work, so every real approach stores something smaller.

### Four approaches

The first approach is command objects that write their own inverse. Each edit is an object with a "do" function and an "undo" function: moving an object by 3 metres has an undo that moves it by minus 3 metres. This is cheap in memory, because a step holds only its parameters. The cost is the work of writing, and testing, an inverse for every kind of edit. The inverse of "delete a parent with two children" has to recreate three entities with their components, and every new command can get its inverse wrong.

The second approach is the **memento**: a copy of the state an edit touches, taken before and after the edit, so that undo puts the old copy back. The step does not need to know what the edit did, only which parts of the world it touched.

A copy of the state is also called a **snapshot**. The cost is memory: a step that changes one number still stores whole copies of the objects that hold it, and the copies must be complete enough to rebuild an object that no longer exists.

The third approach is the transaction buffer. Unreal Engine's transactions and Unity's call that records an object work this way: before you change an object, you tell the engine, and the engine writes that object out as data and keeps the result. This is a memento where the unit is the object, and the engine finds the changes itself by comparing before and after. The cost is that code must announce each object before touching it. A change to an object nobody announced silently has no undo.

The fourth approach is a persistent :term[data structure]{id=data-structure}: a structure that never changes in place. Each edit builds a new version that shares most of its parts with the old one, so keeping every version costs little, and undo means returning to an older version. :term[Version control]{id=version-control} systems such as :term[Git]{id=git} share unchanged parts between versions in much the same way. The cost is that the whole engine must be written in this style. An entity-component system (:term[ECS]{id=ecs-entity-component-system}) such as EnTT keeps data in arrays that systems write in place, and cannot become persistent without a rewrite.

| Approach | What a step stores | Main cost |
| --- | --- | --- |
| Command objects with an inverse | The parameters of the edit | An inverse for every edit, each a place for a bug |
| Memento | The touched state, before and after | Memory for whole copies of what was touched |
| Transaction buffer | Objects written out as data, announced before the change | An edit of an object nobody announced cannot be undone |
| Persistent data structure | A pointer to an older version | The whole data model must never change in place |

### What Strata chooses

Strata uses two of these, each where it fits: for the scene it uses mementos at the grain of one entity. Every scene edit, from a dragged value to a paste of a hundred entities, ends with the same question: which entities have a different state now? A single step type answers it for all of them, so a new command gets undo by naming the entities it touches. For everything else (files, documents, settings) it uses actions of their own: classes that each implement `Execute` and `Undo` themselves, so that each can check that the world still fits the step. The next sections build both, starting with the history that holds the steps, because the history does not care what a step is.

## The map

The history is a list of steps with a position. The steps come from two places. Commands that edit the scene record steps of one class, `SceneEditAction`, through a `SceneEditTransaction`. Other commands record steps of their own classes. Both kinds sit in the same list, so one press of **Ctrl+Z** undoes whichever came last.

A list of steps with a position is the **undo stack**, and Strata names it `UndoStack`. It lives in `StrataEditor/src/Editor/UndoStack.h` and `StrataEditor/src/Editor/UndoStack.cpp`. The scene steps and the entity code live in `StrataEditor/src/Editor/SceneEdit.h` and `StrataEditor/src/Editor/SceneEdit.cpp`. All of it runs on the :term[main thread]{id=main-thread}, as the scene does.

```mermaid caption="A command records a step through the gate. Undo and redo run through the editor context, and observers hear every change the history applies." alt="A command builds a scene edit transaction and hands it to the commit gate of the editor context. The gate records a scene step on the undo stack. The edit undo and edit redo commands call the stack through the editor context. The stack tells its observers, the recovery journal and the worlds, about every step it applies."
flowchart LR
	Cmd["Command: entity.delete, property edit"] --> Tx["SceneEditTransaction"]
	Tx --> Gate["EditorContext::CommitEdit"]
	Gate -->|Record| Stack["UndoStack"]
	Other["Other commands: asset edits, settings"] -->|Execute or Record| Stack
	Undo["edit.undo, edit.redo"] --> Ctx["EditorContext::Undo, Redo"]
	Ctx --> Stack
	Stack --> Step["SceneEditAction: ApplyEntities"]
	Stack -->|OnApplied| Obs["Observers: recovery journal, worlds"]
```

Read the picture from the left. A command never writes into the history directly for scene edits: it goes through the gate. Undo and redo come from the right and also go through the context, which refuses them while a game plays. The stack tells its observers about each change it applies, so that other parts of the editor can follow the scene without asking the history what it holds.

## The contract

A person or an agent that adds an edit, and a part of the editor that reads the history, can rely on a few rules. Each rule has a reason, and the rest of the page shows the code that keeps it.

- **One command, one step.** A command that changes something records at most one step, and records none when nothing changed. The reason: a person presses undo once per thing they did, and an agent reads `edit.history` to see what a command did.
- **A step owns everything it needs.** It must work after other steps were undone and applied again around it. The reason: the position in the history moves freely, and a step that depends on outside state would break the order.
- **Undo can fail.** A step that cannot reverse itself returns a reason and changes nothing. The reason: files and settings can change under the history, and a lie about what undo did is worse than an error.
- **A step says whether it changes the scene.** A step of a material file never marks the scene as modified. The reason: saving the scene does not save a material, so a person who edited only a material must not be asked to save the scene.
- **Only the main thread touches the stack.** The reason: it holds steps that read and write the scene, and the scene belongs to the main thread.

:::rule
A command is the only way to change the scene or the project, and each command that succeeds records one undo step. The reason is that the history, the activity journal and replays all rely on one step per command. See [Commands](../editor/commands.md) for how commands end.
:::

The three rules of the scene's side come later, because they need the vocabulary of entity states. They are: track an entity before you change it, track an entity you created after you create it, and track a whole :term[subtree]{id=subtree} before you delete it.

## A toy version

To see the history's decisions without the engine around them, the toy below keeps one :term[integer]{id=integer} and records steps that add to it. The real tests of the history use the same idea: a step that adds a delta to a shared value is the simplest action that can be done, undone and merged. Strata's own test file for the history calls it `AddAction`.

The toy has the parts the real history has. A step can merge with the next one, and then the two are one step. A save point, a position that marks "this is what is on disk", stops merging across it. A capacity limit drops the oldest step.

A merged step that ends at zero is a **no-op step**, a step that changes nothing, and the history drops it.

A new edit after an undo discards the steps that were undone. They form the **redo branch**, the steps ahead of the position that redo would apply.

```cpp sketch="editor-undo-toy.cpp"
#include <cstdio>
#include <deque>
#include <cstddef>
#include <memory>
#include <utility>

// One undoable change of an integer: it adds a delta, and a mergeable one absorbs the next mergeable one.
class Action
{
public:
	Action(int delta, bool mergeable)
		: m_Delta(delta), m_Mergeable(mergeable)
	{
	}

	void Apply(int& value) const { value += m_Delta; }
	void Revert(int& value) const { value -= m_Delta; }
	bool MergeWith(const Action& next)
	{
		if (!m_Mergeable || !next.m_Mergeable)
			return false;
		m_Delta += next.m_Delta;
		return true;
	}
	bool IsNoOp() const { return m_Delta == 0; }
private:
	int m_Delta;
	bool m_Mergeable;
};

class History
{
public:
	explicit History(size_t capacity)
		: m_Capacity(capacity)
	{
	}

	void Execute(std::unique_ptr<Action> action, int& value)
	{
		action->Apply(value);
		if (m_Position < m_Entries.size())
		{
			// A new edit after undo: the redo branch goes, and a save point inside it is lost.
			m_Entries.erase(m_Entries.begin() + static_cast<std::ptrdiff_t>(m_Position), m_Entries.end());
			if (m_Saved != c_Lost && m_Saved > m_Position)
				m_Saved = c_Lost;
			m_MergeBroken = true;
		}
		// Never merge across the save point: saving ends a drag's step.
		if (!m_MergeBroken && m_Position > 0 && m_Saved != m_Position && m_Entries.back()->MergeWith(*action))
		{
			if (m_Entries.back()->IsNoOp())
			{
				m_Entries.pop_back();
				m_Position--;
				m_MergeBroken = true;
			}
			return;
		}
		m_Entries.push_back(std::move(action));
		m_Position = m_Entries.size();
		m_MergeBroken = false;
		if (m_Entries.size() > m_Capacity)
		{
			m_Entries.pop_front();
			m_Position--;
			m_Saved = (m_Saved == 0 || m_Saved == c_Lost) ? c_Lost : m_Saved - 1;
		}
	}

	bool Undo(int& value)
	{
		if (m_Position == 0)
			return false;
		m_Entries[--m_Position]->Revert(value);
		m_MergeBroken = true;
		return true;
	}

	bool Redo(int& value)
	{
		if (m_Position == m_Entries.size())
			return false;
		m_Entries[m_Position++]->Apply(value);
		m_MergeBroken = true;
		return true;
	}

	void MarkSaved() { m_Saved = m_Position; m_MergeBroken = true; }
	bool IsModified() const { return m_Saved != m_Position; }
	size_t GetCount() const { return m_Entries.size(); }
	size_t GetPosition() const { return m_Position; }
private:
	static constexpr size_t c_Lost = static_cast<size_t>(-1);
	std::deque<std::unique_ptr<Action>> m_Entries;
	size_t m_Capacity;
	size_t m_Position = 0;
	size_t m_Saved = 0;
	bool m_MergeBroken = true;
};

static void Show(const char* label, const int value, const History& history)
{
	std::printf("%-22s value=%2d steps=%zu position=%zu modified=%s\n", label, value, history.GetCount(), history.GetPosition(),
		history.IsModified() ? "yes" : "no");
}

int main()
{
	int value = 0;
	History history(512);
	history.Execute(std::make_unique<Action>(5, false), value);
	history.MarkSaved();
	Show("add 5, save", value, history);
	history.Execute(std::make_unique<Action>(2, true), value);
	history.Execute(std::make_unique<Action>(3, true), value);
	Show("drag +2, +3", value, history);
	history.Execute(std::make_unique<Action>(-5, true), value);
	Show("drag -5 (back)", value, history);
	history.Undo(value);
	Show("undo", value, history);
	history.Execute(std::make_unique<Action>(7, false), value);
	Show("add 7 (redo branch)", value, history);
	history.Undo(value);
	Show("undo again", value, history);

	int small = 0;
	History tiny(2);
	for (int delta = 1; delta <= 3; delta++)
		tiny.Execute(std::make_unique<Action>(delta, false), small);
	Show("capacity 2, three adds", small, tiny);
	while (tiny.Undo(small))
	{
	}
	Show("undo all", small, tiny);
	return 0;
}
```

```text output-of="editor-undo-toy.cpp"
add 5, save            value= 5 steps=1 position=1 modified=no
drag +2, +3            value=10 steps=2 position=2 modified=yes
drag -5 (back)         value= 5 steps=1 position=1 modified=no
undo                   value= 0 steps=1 position=0 modified=yes
add 7 (redo branch)    value= 7 steps=1 position=1 modified=yes
undo again             value= 0 steps=1 position=0 modified=yes
capacity 2, three adds value= 6 steps=2 position=2 modified=yes
undo all               value= 1 steps=2 position=0 modified=yes
```

1. **Lines 18–24:** `MergeWith` absorbs the next delta only when both steps accept a merge.
2. **Lines 42–49:** a new edit after an undo erases the redo branch, loses a save point inside it and breaks the merge.
3. **Line 51:** a merge needs a merge that is not broken, a latest step and a position that is not the save point.
4. **Lines 53–58:** a merged step that became a no-op leaves the history, and the next edit starts a step of its own.
5. **Lines 64–69:** past the capacity the oldest step goes, and the save point moves with the entries or is lost.

**Merge** means that the history lets the latest step absorb the next edit instead of recording a new step. An action says it accepts by returning true from its `MergeWith` function. In the real editor, the actions that merge compare a **merge key**, a text that names the kind of continuous edit.

To **break the merge** means to tell the history that the next edit must start a step of its own, even if it could merge. A mouse release does this when a drag ends.

Follow the numbers by hand. The first step adds 5 and the save marks position 1, so the history is not modified. The drag adds 2, which starts a new step (the save point stops a merge across it), and the second drag edit adds 3 and merges into it: value 10, still 2 steps. The edit of minus 5 merges too, and the merged delta becomes $2 + 3 - 5 = 0$. The step is a no-op, so the history drops it: value 5, one step, and the flag says not modified, because the scene is at the saved state again.

Then undo takes the value to 0, and a new edit of 7 erases the redo branch, which held the saved step. The save point sat at position 1, beyond the new position 0, so it is lost. The history stays modified from then on. A person might hope that undoing the 7 returns to the saved state, but the saved state is no longer in the history. The last lines show the capacity: with room for 2 steps, adding 1, 2 and 3 drops the step for 1, and undoing everything leaves the value at 1, not 0.

The toy omits the rest of the real design: failing actions, serial numbers, groups, observers, and the difference between steps that change the scene and steps that do not. The next section adds them one at a time, with the real code.

## The real history

The real steps are objects of a class that Strata calls an `EditorAction`. Its function list is the contract of a step. Notice the two functions that can fail and the functions that have a default, because a new action only has to override what it needs.

```cpp src="StrataEditor/src/Editor/UndoStack.h#L31-L56"
class EditorAction
{
public:
	virtual ~EditorAction() = default;

	virtual const std::string& GetName() const = 0;
	virtual bool Execute(std::string* outError) = 0;
	virtual bool Undo(std::string* outError) = 0;

	// Continuous edits (dragging a value) become one undo step: when the stack's latest action accepts the next
	// one, it absorbs its effect (the next action has already been applied) and the next action is dropped.
	virtual bool MergeWith(const EditorAction& /*next*/) { return false; }
	// Whether the action changes nothing (e.g. a merged drag that returned to its start). The stack drops a merged
	// step that became a no-op, so dragging a value back and forth leaves no undo step.
	virtual bool IsNoOp() const { return false; }
	// Whether the action changes the edited scene, which saving the scene saves. Edits of asset documents (a material)
	// write their files themselves: they share the history but never make the scene unsaved (UndoStack::IsModified).
	virtual bool ChangesScene() const { return true; }
	// What the action's effect on the scene consists of. Actions that change the scene describe it as entity states
	// where they can (GetEntityStates): an action of kind Other makes the recovery journal snapshot the whole scene.
	virtual SceneChangeKind GetSceneChange() const { return ChangesScene() ? SceneChangeKind::Other : SceneChangeKind::None; }
	// The states of the entities the action touches as the scene holds them after it (undone false) or before it
	// (undone true); null when the action does not describe its effect as entity states. Shared and never changed, so
	// that journals can keep and read them on other threads.
	virtual Ref<const std::vector<EntityState>> GetEntityStates([[maybe_unused]] bool undone) const { return nullptr; }
};
```

1. **Lines 37–38:** `Execute` and `Undo` are the two functions that can fail, with the reason in `outError`.
2. **Line 42:** `MergeWith` refuses by default, so an action merges only when it says so.
3. **Line 45:** `IsNoOp` is false by default, and an action that can return to its start overrides it.
4. **Line 48:** `ChangesScene` is true by default, so only steps of files and documents override it.
5. **Lines 51–55:** the scene change and its entity states tell the observers what the step did; the default of the states is null.

The `Execute` and `Undo` functions return false and fill `outError` when the world changed in a way the step cannot handle. The functions with defaults describe the step to the stack. `MergeWith` says whether the step absorbs the next one, `IsNoOp` says whether the step now changes nothing, and `ChangesScene` says whether saving the scene saves this step's effect. The last two describe the effect to the parts of the editor that follow the scene, which later sections explain.

### What happens to a new edit

When a command applies a step, the stack calls its private `Push` function. Read it in two parts. The first part handles the redo branch and merging.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L59-L85"
m_RecordCount++;
m_Version++;
// Recording after undoing discards the undone actions; a save point among them becomes unreachable.
if (m_Position < m_Entries.size())
{
	m_Entries.erase(m_Entries.begin() + static_cast<std::ptrdiff_t>(m_Position), m_Entries.end());
	if (m_SavedPosition != c_NoSavePoint && m_SavedPosition > m_Position)
		m_SavedPosition = c_NoSavePoint;
	m_MergeBroken = true;
}

if (!m_MergeBroken && m_Position > 0 && m_SavedPosition != m_Position && m_Entries.back().Action->MergeWith(*action))
{
	// Absorbed into the latest step (never across the save point, so saving ends a drag's step). A step that now
	// changes nothing is dropped, and the next edit starts a step of its own. Either way the scene holds what the
	// latest step describes now (a dropped one: what it started from).
	NotifyApplied(*m_Entries.back().Action, false, true);
	m_LastRecordedSerial = m_Entries.back().Serial;
	if (m_Entries.back().Action->IsNoOp())
	{
		m_LastRecordedSerial = 0;
		m_Entries.pop_back();
		m_Position--;
		m_MergeBroken = true;
	}
	return;
}
```

1. **Lines 62–68:** a new edit after an undo erases the redo branch, loses a save point inside it and breaks the merge.
2. **Line 70:** a merge needs a merge that is not broken, a latest step and a position that is not the save point.
3. **Lines 75–76:** the observers hear the merged step, and its own serial stays the last recorded one.
4. **Lines 77–83:** a merged step that became a no-op leaves the history, and its serial counts as none.

The second part records a new step and trims the oldest one when the stack is full.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L87-L104" from="m_LastRecordedSerial = m_NextSerial;" to="m_SavedPosition--;" symbol="UndoStack::Push"
m_LastRecordedSerial = m_NextSerial;
m_Entries.push_back({ std::move(action), m_NextSerial++ });
m_Position = m_Entries.size();
m_MergeBroken = false;
NotifyApplied(*m_Entries.back().Action, false);
if (m_Entries.size() > m_Capacity)
{
	// A save point before the dropped step stays at the front when that step did not change the scene (a material
	// edit): the scene there is the saved one. After a dropped scene edit, the saved scene can no longer be reached.
	const bool dropsSceneChange = m_Entries.front().Action->ChangesScene();
	if (dropsSceneChange)
		m_SceneTrims++;
	m_Entries.pop_front();
	m_Position--;
	if (m_SavedPosition == 0)
		m_SavedPosition = dropsSceneChange ? c_NoSavePoint : 0;
	else if (m_SavedPosition != c_NoSavePoint)
		m_SavedPosition--;
```

1. **Lines 87–88:** a new step takes the next serial.
2. **Lines 89–91:** the position moves to the end, merging becomes possible again and the observers hear the step.
3. **Lines 92–99:** past the capacity the oldest step goes, and a dropped step that changed the scene counts as a trim.
4. **Lines 101–104:** the save point moves with the entries, or is lost when the dropped step was a scene edit.

The real `Push` makes the same decisions as the toy, in the same order, and adds three things. It tells the observers about each step, gives each recorded step a serial number, and treats a dropped step with care. The care matters because the step that falls off the front may or may not have changed the scene. A step that did not change the scene (a material edit) leaves the save point at the front, because the scene there is still the saved one. A step that did change it makes the saved scene impossible to reach.

A **serial** is the number the stack gives a step when it records it. Serials grow with each new step and are never used again, not even after the stack is cleared, and a merged step keeps its own. Because a serial names a step for as long as the step exists, other parts of the editor use it as an address. The activity journal's "Undo to here" button finds the step again with `FindSerial`, which searches the sorted entries by :term[binary search]{id=binary-search}.

### Undo and redo fail differently

The stack's two directions treat failure differently, and the difference follows from what each direction promises. Undo promises to return to a state that was once real. Redo promises to apply an edit again in a world that may have moved on.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L156-L186" symbol="UndoStack::Undo"
bool UndoStack::Undo(std::string* outError)
{
	if (m_Group)
	{
		if (outError)
			*outError = "Undo is not available while a batch runs (editor.batch makes its steps one undo step)";
		return false;
	}
	if (!CanUndo())
	{
		if (outError)
			*outError = "Nothing to undo";
		return false;
	}
	std::string error;
	if (!m_Entries[m_Position - 1].Action->Undo(&error))
	{
		// The step stays applied: nothing changed, and undoing it again works once what blocks it is gone.
		const std::string message = fmt::format("Undo of '{}' failed: {}", m_Entries[m_Position - 1].Action->GetName(), error);
		ST_ERROR("{}", message);
		if (outError)
			*outError = message;
		m_MergeBroken = true;
		return false;
	}
	m_Version++;
	m_Position--;
	m_MergeBroken = true;
	NotifyApplied(*m_Entries[m_Position].Action, true);
	return true;
}
```

1. **Lines 158–163:** a batch that is open refuses undo.
2. **Lines 164–169:** with nothing to undo, the reason says so.
3. **Lines 171–180:** a failed undo logs the reason, returns it, breaks the merge and leaves the step and the position as they were.
4. **Lines 181–184:** a successful undo moves the position back and tells the observers that the scene is undone.

Redo has the opposite failure rule, so read its failing branch next.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L203-L215"
m_Version++;
std::string error;
if (!m_Entries[m_Position].Action->Execute(&error))
{
	// The world changed in a way the action cannot be reapplied to: drop it and everything after it.
	const std::string message = fmt::format("Redo of '{}' failed: {}", m_Entries[m_Position].Action->GetName(), error);
	ST_ERROR("{}", message);
	if (outError)
		*outError = message;
	m_Entries.erase(m_Entries.begin() + static_cast<std::ptrdiff_t>(m_Position), m_Entries.end());
	if (m_SavedPosition != c_NoSavePoint && m_SavedPosition > m_Position)
		m_SavedPosition = c_NoSavePoint;
	return false;
```

1. **Line 203:** the version changes first, because a failed redo changes the history too.
2. **Lines 205–211:** a failed `Execute` logs the reason and returns it.
3. **Lines 212–214:** the history erases the step and every step after it, and a save point among them is lost.
4. **Line 215:** the call fails.

When undo fails, the step stays applied and the position does not move, and the reason goes to the log and to the caller. Nothing changed, so a person can fix the cause (move the other file away) and press undo again. When redo fails, the history removes the step and every step after it. Those steps were recorded in a world that no longer exists, and keeping later steps whose base state changed would let a later redo do something nobody expects. Both paths also break the merge, so the next edit never merges into a step that an undo touched a moment ago.

The `edit.undo` and `edit.redo` commands call `EditorContext::Undo` and `Redo`, which add the refusal while a game plays or a scene is opening. Both return the history as `edit.history` does: the names of all steps, oldest first, and the position.

### The save point and the modified flag

A person asks whether the scene has changes that are not yet saved, and the answer must stay right after any number of undos and redos. Counting edits cannot give it, because an undo removes an edit and a save does not. The editor therefore treats the saved state as a place in the history, a **save point**: the position the history had when the scene was last written. The scene is modified when the steps between the save point and the current position change the scene.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L298-L311" symbol="UndoStack::IsModified"
bool UndoStack::IsModified() const
{
	// A save point that was trimmed or discarded can no longer be reached: whatever lies between is unknown.
	if (m_SavedPosition == c_NoSavePoint)
		return true;
	const size_t first = std::min(m_SavedPosition, m_Position);
	const size_t last = std::max(m_SavedPosition, m_Position);
	for (size_t index = first; index < last; index++)
	{
		if (m_Entries[index].Action->ChangesScene())
			return true;
	}
	return false;
}
```

1. **Lines 300–302:** a lost save point means modified.
2. **Lines 303–304:** the loop covers the steps between the two positions, whichever lies first.
3. **Lines 305–309:** one step that changes the scene is enough to report a change.
4. **Line 310:** otherwise the scene is as saved.

The flag costs the number of steps between the two positions, and counts only steps whose `ChangesScene` returns true. A material edit between them does not make the scene modified, because the material file saved itself. If the save point was lost, the flag is true, because the history cannot say what lies between.

A save that runs in the background complicates this, because the person keeps editing while the file is written. So the stack can hand out a `SavePoint` value that names a state, and the save marks it when the file is on disk. The value holds four numbers: the position, the serial of the latest applied step, the **generation** and a count of scene steps trimmed from the front. The generation belongs to the history itself, and changes each time `Clear` starts a history for another scene. The next code finds the saved state again by its serial, wherever later edits have moved the position.

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L283-L296" overload="2" symbol="UndoStack::MarkSaved"
void UndoStack::MarkSaved(const SavePoint& point)
{
	if (point.Generation != m_Generation)
		return;
	m_Version++;
	if (point.Serial == 0)
	{
		// The state before every action: still the front of the history unless a scene change was trimmed off it since.
		m_SavedPosition = point.SceneTrims == m_SceneTrims ? 0 : c_NoSavePoint;
		return;
	}
	const std::optional<size_t> index = FindSerial(point.Serial);
	m_SavedPosition = index ? *index + 1 : c_NoSavePoint;
}
```

1. **Lines 285–286:** a point of another generation marks nothing.
2. **Lines 288–293:** serial 0 means the front of the history, valid unless a scene step was trimmed.
3. **Lines 294–295:** the step with the serial is found again, and the save point is the position after it.

Four cases follow: a point of an older generation marks nothing, because it belongs to another scene. A point with serial 0 means "before every step", which stays valid unless a scene step was trimmed from the front since. A point whose step still exists becomes the new save point at the position after that step. A point whose step is gone (trimmed, dropped with a redo branch, or removed by a failed redo) leaves the scene modified. The details of the background save belong to [Saving](../editor/saving.md); the history only promises that it never claims a state is saved when it cannot prove it.

Whoever takes a point breaks the merge first, with `BreakMerge`. A drag that merges frames changes the state of its latest step, so a point taken in the middle of a drag would name a state that the next frame changes. After the break, the next frame starts a step of its own.

Picture a history of three steps. Serial 1 added 5, and the scene was saved after it. Serial 2 is a drag whose frames merged into one step. The step with serial 3 was recorded and then dropped with a redo branch, so the next step took serial 4. One undo has since moved the position back, so the step with serial 4 waits as the next redo.

```mermaid caption="A history with three steps, a save point after the first, a position of two applied steps and one step waiting for redo. The serials skip a number because a dropped step never gives its number back." alt="A row of three entries. The entry with serial one is followed by a marker for the save point. The entry with serial two is followed by a marker for the position of two applied steps. The entry with serial four, drawn after the position, is the step that redo would apply, and serial three is missing."
flowchart LR
	E1["serial 1: Add 5"] --> SP(["save point after step 1"]) --> E2["serial 2: a drag, merged"] --> POS(["position 2: two steps applied"]) -.-> E4["serial 4: redo applies this one"]
```

### Groups and observers

Some commands must be one step although they use several actions. `prefab.apply` writes the prefab's file and then updates the instances in the scene, and the two must undo together. An **action group** is a step made of several steps: `Execute` runs the members in order, `Undo` runs them in reverse order, and either one happens as a whole or not at all. When a member fails, the members that already ran are reverted, so the world is as it was.

The editor's `editor.batch` command uses a group that the stack opens while the commands run. From `BeginGroup` to `EndGroup`, every recorded action is applied at once and held in the open group. The history gets one step when the group ends, named "Batch of 3 commands" for three. A batch that must succeed as a whole calls `CancelGroup` when a command fails, which reverts what the group collected, latest first, and records nothing. If that revert fails, the group stays applied as one step, so that undo can try again later.

While a group is open, undo, redo and `GoTo` refuse, and groups do not nest.

An observer is an object that the stack tells about every change it applies: a step recorded, a merged step, a redo, an undo. The recovery journal uses one to keep a copy of the scene's changes, and an open world uses one to know which cells are dirty. The observer hears each member of a group as it is applied, then not again when the group is recorded. The action reports what it changed with `GetSceneChange`: nothing, entities, settings, or "other", the last of which makes the journal take a snapshot of the whole scene. [Recovery](../editor/recovery.md) shows what the journal does with these notices.

## How a scene edit becomes a step

The history does not care what a step is. The scene needs a step type that works for any change to any set of entities. The central idea is that undo must recreate an entity that was deleted, and the recreated entity must be the same one, with the same :term[universally unique identifier]{id=uuid} (UUID). Scripts hold UUIDs, other entities point at them through components, prefab instances remember them, and recorded replays name them. If undo gave a deleted entity a new UUID, all of those references would break, so Strata keeps one identity for an entity's whole life, including the moments when it is deleted and brought back.

### Entity states

An **`EntityState`** is everything that defines one entity at one moment: its UUID, whether it exists, its components as data, its parent, its position among its siblings and the cell it belongs to. The components are stored in the same :term[JSON]{id=json} form that [scene documents](../world/serialization.md) use. Reading the type, look at what a state of a deleted entity looks like and why `Cell` exists.

```cpp src="StrataEditor/src/Editor/SceneEdit.h#L21-L37"
// Everything that defines one entity in the edited scene: its components, its parent and its position among its
// siblings. Restoring a state recreates the entity with the same UUID, so references to it stay valid.
struct EntityState
{
	UUID ID = UUID::Null();
	bool Exists = false;
	nlohmann::json Components; // ComponentAccess::SerializeEntityComponents plus the UnknownComponentsComponent's entries
	UUID Parent = UUID::Null();
	size_t SiblingIndex = 0;
	// The scene asset of the sub-scene the entity belongs to (a world's cell; null: none, the persistent scene): its own
	// for a top-level entity, its top-level ancestor's for a descendant. A state of an entity that does not exist names
	// the cell the entity is in on the other side of its step (SceneEditAction fills it in), so that undoing a creation
	// or redoing a deletion waits for that cell too: done while it is not loaded, the entity would come back with it.
	AssetHandle Cell = UUID::Null();

	bool operator==(const EntityState& other) const = default;
};
```

1. **Lines 25–26:** the UUID and whether the entity exists.
2. **Line 27:** the components in the form of scene documents.
3. **Lines 28–29:** the parent and the position among the siblings.
4. **Line 34:** the cell of a world that holds the entity.
5. **Line 36:** states compare by value, which the transaction uses to tell whether an edit changed anything.

A state with `Exists` false describes an entity that is not there. A step stores two lists of states, before and after, naming the same entities in the same order. A creation has a before state that does not exist; a step that deletes entities has an after state that does not exist. The sibling index is the entity's position among the children of its parent, a term taught in [the scene graph](../world/scene-graph.md). The cell is the sub-scene of a world that holds the entity; [Worlds](../editor/worlds.md) explains why undo must wait for a cell that is not loaded.

### The transaction

An edit that works directly on the scene needs a way to capture the before state without every command writing it by hand. The **scene edit transaction** is an object that captures the before states of the entities an edit will touch. When the edit is done, it captures the after states and records one step if they differ. Its set of public functions is small.

```cpp src="StrataEditor/src/Editor/SceneEdit.h#L132-L169"
// Records an edit that is made directly on the scene: construct it with the entities the edit will touch, make
// the changes, Track any entities created along the way, then Commit to record one undo step. An edit that
// changed nothing records nothing.
class SceneEditTransaction
{
public:
	SceneEditTransaction(Scene& scene, std::string name, const std::vector<UUID>& entities, std::string mergeKey = {});

	// Adds an entity to the edit; call before changing it.
	void Track(UUID id);
	// Adds an entity and all its descendants; call before changing or destroying them.
	void TrackSubtree(UUID id);
	// Adds an entity (and its descendants) the edit created; call after creating it.
	void TrackCreated(UUID id);

	// Names the step after all, once what it made is known (e.g. the names of pasted entities).
	void SetName(std::string name) { m_Name = std::move(name); }
	// The entities the edit tracks, in the order tracked, and whether the edit created the one at an index.
	const std::vector<UUID>& GetEntities() const { return m_Entities; }
	bool WasCreated(size_t index) const { return !m_Before[index].Exists; }
	// Records the edit on the stack. Returns false when nothing changed.
	bool Commit(UndoStack& undoStack);
	// The edit as an action, for a step that holds more (EditorActionGroup); null when nothing changed. Ends the
	// transaction like Commit.
	Scope<EditorAction> TakeAction();
	// Restores the tracked entities to their state before the edit (a failed edit) and ends the transaction.
	void Rollback();
	// The tracked entities' states before the edit, in the order they were tracked (created ones: not existing).
	const std::vector<EntityState>& GetBefore() const { return m_Before; }
	Scene& GetScene() const { return m_Scene; }
private:
	Scene& m_Scene;
	std::string m_Name;
	std::string m_MergeKey;
	std::vector<UUID> m_Entities;
	std::unordered_set<UUID> m_Tracked;
	std::vector<EntityState> m_Before;
};
```

1. **Line 138:** the :term[constructor]{id=constructor} takes the scene, the step's name, the entities to track and an optional merge key.
2. **Lines 141–145:** the three tracking functions, one for each rule.
3. **Lines 153–156:** `Commit` records the step, and `TakeAction` hands it back for a group.
4. **Line 158:** `Rollback` restores the tracked entities.
5. **Line 160:** the states before can be read, which `entity.delete` uses to count.

The three tracking functions carry the rules of the scene's side. Call `Track` (or pass the ids to the :term[constructor]{id=constructor}) before you change an entity, because the transaction reads its state at that moment. Call `TrackSubtree` before you delete an entity, because a deleted entity cannot be read afterwards, and all its descendants vanish with it. Call `TrackCreated` after you create an entity, because the entity must exist for the transaction to find its subtree, and its before state is, by definition, "does not exist".

```mermaid caption="A transaction captures states before the change, tracks what the edit creates, and records one step only if the states after differ from the states before." alt="Boxes in a row: construct with the entities, change the scene, track created entities, take the action. A decision box asks whether the states are equal. If yes, nothing is recorded. If no, one scene step is recorded. A side arrow from the change box shows that a failure rolls the entities back to the states before."
flowchart LR
	A["Capture before states"] --> B["Change the scene"]
	B --> C["TrackCreated for new entities"]
	C --> D["Capture after states"]
	D --> E{"Equal?"}
	E -->|yes| F["Record nothing"]
	E -->|no| G["Record one SceneEditAction"]
	B -.->|failure| H["Rollback: ApplyEntities before states"]
```

Two functions end a transaction. `Commit` records the step on the stack and `TakeAction` hands back the action, for a command that wants to put it in a group. Both capture the after states, compare them with the before states and return nothing when the lists are equal. An edit that changed nothing records nothing. **Rollback** is the other way out: it puts every tracked entity back to its before state and ends the transaction, which is what a command does when its edit fails half way.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L453-L463" symbol="SceneEditTransaction::TakeAction"
Scope<EditorAction> SceneEditTransaction::TakeAction()
{
	std::vector<EntityState> after = SceneEdit::CaptureEntities(m_Scene, m_Entities);
	if (after == m_Before)
		return nullptr;
	Scope<EditorAction> action = CreateScope<SceneEditAction>(m_Scene, m_Name, std::move(m_Before), std::move(after), m_MergeKey);
	m_Before.clear();
	m_Entities.clear();
	m_Tracked.clear();
	return action;
}
```

1. **Lines 455–457:** the after states are captured, and equal lists record nothing.
2. **Line 458:** the step takes both lists by move, with the name and the key.
3. **Lines 459–462:** the transaction is over, so a second commit finds nothing to do.

### The step

The class that records the result is `SceneEditAction`. It holds the two lists as :term[shared pointers]{id=shared-pointer} to constant vectors. Once a step is recorded, its states never change in place, so a recovery journal on another thread can read them without a lock. `Execute` applies the after states and `Undo` applies the before states, both through `ApplyEntities`, after checking that every cell the states name is loaded.

Merging has a rule, shown here. Two scene steps merge when the latest has a non-empty key, the next has the same key, they belong to the same scene, and they list the same entities in the same order. The latest step then takes the next one's after states and keeps its own before states, so a drag of 90 frames is one step whose before state is the value from the first frame.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L351-L363" symbol="SceneEditAction::MergeWith"
bool SceneEditAction::MergeWith(const EditorAction& next)
{
	const auto* edit = dynamic_cast<const SceneEditAction*>(&next);
	if (!edit || m_MergeKey.empty() || edit->m_MergeKey != m_MergeKey || edit->m_Scene != m_Scene || edit->m_After->size() != m_After->size())
		return false;
	for (size_t index = 0; index < m_After->size(); index++)
	{
		if ((*edit->m_After)[index].ID != (*m_After)[index].ID)
			return false;
	}
	m_After = edit->m_After;
	return true;
}
```

1. **Lines 353–354:** the next step must be a scene step with the same non-empty key, the same scene and the same number of entities.
2. **Lines 356–360:** the entities must be the same ones in the same order.
3. **Line 361:** the step takes the next after states and keeps its own before states.

The step takes its after list by pointer, not by copy, which is why states stay constant. It also reports itself as a no-op when its two lists are equal, so a drag that returns to its start leaves nothing in the history.

### The algorithm that puts entities back

Everything above exists to feed one function. `ApplyEntities` takes a list of states and makes the scene match it, whatever the scene looks like now. It does the same job for undo of a delete, redo of a creation and a rollback, and its design must keep each of them fast for large lists.

:::example[Delete a parent and undo it]
Take a scene with three top-level entities: `Ground` at position 0, `Rig` at position 1 and `Sun` at position 2. `Rig` has two children, `Arm` at position 0 and `Hand` at position 1. The command `entity.delete` deletes `Rig`.

The transaction tracks the subtree before the delete, so the step is named "Delete 'Rig'". Its before list holds three states: `Rig` (exists, no parent, position 1), `Arm` (exists, parent `Rig`, position 0) and `Hand` (exists, parent `Rig`, position 1). The after list holds the same three UUIDs with `Exists` false. After the delete, the roots are `Ground` and `Sun`.
:::

Press undo. The step applies its before list. Read `ApplyEntities` in three parts, which are its three batches. The first part removes entities that must not exist.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L191-L199" from="std::vector<Entity> removed;" to="scene.DestroyEntities(removed);" symbol="SceneEdit::ApplyEntities"
std::vector<Entity> removed;
for (const EntityState& state : states)
{
	if (state.Exists)
		continue;
	if (Entity entity = scene.GetEntityByUUID(state.ID))
		removed.push_back(entity);
}
scene.DestroyEntities(removed);
```

In the example this batch is empty, because every state of the before list says "exists". On redo the same code runs with the after list: all three states say "does not exist", the entities are found, and one call destroys them together. The batch matters for large edits: removing many entities from one long list of siblings one at a time compacts the list for each removal, and one call compacts it once.

The second part recreates the entities that are missing.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L203-L230" from="std::unordered_map<UUID, const EntityState*> recreated;" to="Restoring entities: {}" symbol="SceneEdit::ApplyEntities"
std::unordered_map<UUID, const EntityState*> recreated;
for (const EntityState& state : states)
{
	if (state.Exists && !scene.GetEntityByUUID(state.ID))
		recreated.emplace(state.ID, &state);
}
if (!recreated.empty())
{
	nlohmann::json entities = nlohmann::json::array();
	for (const EntityState& state : states)
	{
		if (!recreated.contains(state.ID))
			continue;
		nlohmann::json entity = { { "ID", UUIDToJson(state.ID) }, { "Components", state.Components } };
		if (state.Parent.IsValid() && recreated.contains(state.Parent))
			entity["Parent"] = UUIDToJson(state.Parent);
		entities.push_back(std::move(entity));
	}
	EntityInstantiationOptions options;
	options.GenerateNewUUIDs = false;
	options.ReportUnknownComponents = false; // Snapshots of this scene: its unknown components are no news
	std::string error;
	std::vector<std::string> warnings;
	SceneSerializer::DeserializeEntities(scene, { { "Entities", std::move(entities) } }, options, &error, &warnings);
	if (!error.empty())
		ST_ERROR("Restoring entities failed: {}", error);
	for (const std::string& warning : warnings)
		ST_WARN("Restoring entities: {}", warning);
```

1. **Lines 203–208:** the entities that are missing, and that the states say should exist, are collected.
2. **Lines 213–219:** each becomes a JSON entry, with a parent link only when the parent comes back in this batch.
3. **Line 222:** the option keeps the UUIDs.
4. **Lines 226–230:** the loader's error and warnings go to the log.

Here the step builds one JSON document that lists all missing entities with their UUIDs and components. It gives the document to the same loader that reads scene files, with the option that keeps the UUIDs. The parent link is written only when the parent is itself recreated in this batch. In the example `Rig` goes in with no parent, `Arm` and `Hand` name `Rig`, and the three come back as one subtree, with the original UUIDs. The recreated `Rig` is appended at the end of the roots: the roots are now `Ground`, `Sun`, `Rig`, and `Rig` is at position 2 although it was at position 1.

The third part restores the hierarchy.

```cpp src="StrataEditor/src/Editor/SceneEdit.cpp#L246-L262" from="std::unordered_set<UUID> listsToPlace;" to="Restoring the hierarchy" symbol="SceneEdit::ApplyEntities"
std::unordered_set<UUID> listsToPlace; // By recorded parent (null: the roots)
for (const EntityState& state : states)
{
	if (!state.Exists)
		continue;
	Entity entity = scene.GetEntityByUUID(state.ID);
	if (entity && (entity.GetComponent<RelationshipComponent>().Parent != state.Parent || scene.GetSiblingIndex(entity) != state.SiblingIndex))
		listsToPlace.insert(state.Parent);
}
std::vector<Scene::EntityPlacement> placements;
for (const EntityState& state : states)
{
	if (state.Exists && listsToPlace.contains(state.Parent) && scene.GetEntityByUUID(state.ID))
		placements.push_back({ state.ID, state.Parent, state.SiblingIndex });
}
if (!scene.PlaceEntities(placements))
	ST_WARN("Restoring the hierarchy: some entities could not be placed under their recorded parent and stay at the top level");
```

1. **Lines 246–254:** a sibling list is marked when a recorded entity in it has a different parent or position.
2. **Lines 255–260:** every recorded entity of a marked list is placed, not only the ones that differ.
3. **Lines 261–262:** one placement batch does the work, and a failure only warns.

A sibling list is placed again when any recorded entity in it has a different parent or a different position than recorded. In the example, `Rig` is a root at position 2 but the state says 1, so the list of roots is marked. `Arm` and `Hand` are at their recorded positions under `Rig`, so their list is not. The placement batch contains every recorded entity of the marked list: here only `Rig`, because `Ground` and `Sun` are not in the step. `PlaceEntities` detaches them first, so that no half-finished link can form a cycle, and each lands at its recorded position, so the roots become `Ground`, `Rig`, `Sun` again.

```mermaid caption="Undo of the delete in three batches: nothing to destroy, three entities recreated with their old identity, and one list of siblings placed again." alt="Three columns for the three batches. Batch one lists no entities to destroy. Batch two lists the recreation of Rig, Arm and Hand with their old identity, ending with roots Ground, Sun, Rig. Batch three shows that the roots list is placed again so that Rig returns to position one, ending with roots Ground, Rig, Sun, while the children list stays."
flowchart LR
	subgraph B1["1 Destroy"]
		D1["states that do not exist: none"]
	end
	subgraph B2["2 Recreate"]
		D2["Rig, Arm, Hand return with their UUIDs"] --> D3["roots: Ground, Sun, Rig"]
	end
	subgraph B3["3 Place"]
		D4["roots list differs: place Rig at position 1"] --> D5["roots: Ground, Rig, Sun"]
	end
	B1 --> B2 --> B3
```

Why place every recorded entity of a list, and not only those whose position differs? Because positions can agree while the order does not, and a test of the editor shows it. Take four roots A, B, C and D. An edit moves D and B to the front, giving D, B, A, C. B is still at position 1, so its position agrees with the record, but it now stands before A.

If undo placed only D at position 3, the order would be B, A, C, D. Placing both D and B restores A, B, C, D. The test name says it: "Sibling orders are restored also where recorded positions agree by chance". A recreated entity can show the same effect: it lands where its recorded position happens to lie, and an entity inserted later goes in front of it.

The last loop of the function puts top-level entities back into the cells they belonged to. A cell that is not loaded gets a warning and the entity stays where it is; the check before the step already refused, so the loop is a second line of defense. [Worlds](../editor/worlds.md) explains cells.

### Names in steps and the other scene step

Step names are what a person reads in the **Edit** menu, which shows "Undo Delete 'Rig'", and what an agent reads in `edit.history`. One entity is named by its name in quotes, cut to 40 :term[bytes]{id=byte} with three dots added, and several entities by their count. `QuoteName` does the first and `DescribeEntities` both. A letter outside English can take several bytes, and a name cut in the middle of one would show broken text, so the cut moves back to the start of that letter.

Copies need unique names. `MakeNameUnique` renames an entity whose name a sibling already has, to the base name and a number. "Crate" becomes "Crate (1)", and a copy of "Crate (1)" becomes "Crate (2)": each gets the smallest number that no sibling uses. Commands that make many copies pass one shared table of the next number to try, so that a thousand copies cost a thousand checks, not half a million.

Not everything in a scene is an entity. The scene's settings (gravity, the fixed :term[time step]{id=time-step}, the physics capacities) have their own step, `SceneSettingsAction`: it stores the settings before and after and writes them back. It reports its change as "settings", so the recovery journal knows to save only those.

## Commands and the gate

Every scene edit ends in `EditorContext::CommitEdit`, the one gate between a transaction and the history. Read what it refuses and what it adds.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1875-L1891" symbol="EditorContext::CommitEdit"
bool EditorContext::CommitEdit(SceneEditTransaction& transaction, OverrideUpkeep overrides)
{
	if (IsPlaying())
		return false;
	if (IsSceneLoading())
	{
		// The edited scene is about to be replaced: an edit now would be lost with it, so it is undone at once.
		transaction.Rollback();
		return false;
	}
	// In a world, entities move into the cells their positions lie in, within the same step.
	if (m_World)
		m_World->Recell(transaction);
	if (overrides == OverrideUpkeep::Update)
		UpdatePrefabOverrides(transaction);
	return transaction.Commit(m_UndoStack);
}
```

1. **Lines 1877–1878:** while a game plays, nothing is recorded.
2. **Lines 1879–1884:** while a scene opens, the edit is rolled back at once.
3. **Lines 1886–1887:** a world moves entities into their cells within the same step.
4. **Lines 1888–1889:** prefab overrides are updated within the same step.
5. **Line 1890:** the transaction records its step on the stack.

While a game plays, the gate records nothing: the edit changed a running copy that the stop command discards, so a step for it would undo something that no longer exists. While a scene opens, the edited scene is about to be replaced, so the gate rolls the edit back at once and nothing is lost that was not already lost. Two kinds of extra work run inside the same step: a world moves entities into the cells their positions lie in, and prefab overrides get updated. Both become part of the one step, so one undo reverts them together. [Worlds](../editor/worlds.md) and [Prefab instances](../editor/prefab-instances.md) explain what they do.

Commands call the gate through two helpers. `FinishEdit` checks that the scene accepts edits, calls the gate, and builds the result of the command; while a game plays it adds a warning that the change touched only the running copy. `RollBackEdit` rolls the transaction back and returns the failure, with a kind that tells a bad request from a failed edit.

The `entity.create` and `entity.delete` commands show the tracking rules together. Look at where each one tracks, and at the failures that roll back.

```cpp src="StrataEditor/src/Editor/Commands/EntityCommands.cpp#L170-L194" command="entity.create"
registry.Register({ "entity.create", "Creates an entity, optionally under a parent and with components (undoable; while playing it changes the running copy only). Returns its ID.",
	ObjectSchema({
		{ "name", StringSchema("Entity name (default \"Entity\")") },
		{ "parent", OptionalEntitySchema("Parent; null or omitted for a top-level entity") },
		{ "components", AnyObjectSchema("Components and property values, e.g. {\"Transform\": {\"Translation\": [0, 1, 0]}, \"MeshRenderer\": {\"Mesh\": \"<handle>\"}}") } }),
	[](EditorContext& context, const nlohmann::json& parameters)
	{
		Scene& scene = *context.GetActiveScene();
		CommandArguments arguments(parameters);
		const std::string name = arguments.GetString("name", "Entity");
		Entity parent = arguments.FindEntity(scene, "parent");
		const nlohmann::json* components = arguments.FindObject("components");
		if (!arguments.IsValid())
			return arguments.Fail();

		SceneEditTransaction transaction(scene, fmt::format("Create {}", SceneEdit::QuoteName(name)), {});
		Entity entity = parent ? scene.CreateChildEntity(parent, name) : scene.CreateEntity(name);
		if (!entity)
			return RollBackEdit(transaction, fmt::format("The scene is full: it holds at most {} entities", Scene::c_MaxEntities), EditorCommandError::Failed);
		transaction.TrackCreated(entity.GetUUID());
		std::string error;
		if (components && !ApplyComponents(entity, *components, &error))
			return RollBackEdit(transaction, error, EditorCommandError::InvalidParameters);
		return FinishEdit(context, transaction, { { "id", UUIDToJson(entity.GetUUID()) } });
	} });
```

1. **Line 185:** the transaction starts with no entities, because none exists yet.
2. **Lines 186–188:** a full scene rolls the edit back and fails.
3. **Line 189:** the created entity and its subtree are tracked after they exist.
4. **Lines 191–192:** components that do not fit roll the edit back.
5. **Line 193:** `FinishEdit` records the step and builds the result.

The delete command shows the other two rules: it tracks a subtree before it destroys anything.

```cpp src="StrataEditor/src/Editor/Commands/EntityCommands.cpp#L196-L218" command="entity.delete"
registry.Register({ "entity.delete",
	"Deletes entities and all their descendants (undoable; while playing it changes the running copy only). Returns deleted (the IDs "
	"given) and count (the entities deleted, descendants included).",
	ObjectSchema({ { "entities", EntityArraySchema("Entities to delete") } }, { "entities" }),
	[](EditorContext& context, const nlohmann::json& parameters)
	{
		Scene& scene = *context.GetActiveScene();
		CommandArguments arguments(parameters);
		const std::vector<Entity> entities = arguments.GetEntities(scene, "entities");
		if (!arguments.IsValid())
			return arguments.Fail();

		nlohmann::json deleted = ToJson(RemoveDuplicates(entities));
		SceneEditTransaction transaction(scene, fmt::format("Delete {}", SceneEdit::DescribeEntities(entities)), {});
		for (Entity entity : entities)
			transaction.TrackSubtree(entity.GetUUID());
		// Every entity that goes, each once (descendants and entities listed below another listed one included).
		const size_t count = transaction.GetBefore().size();
		// One batch: each sibling list is compacted once (entities nested in another listed one go with it).
		scene.DestroyEntities(entities);
		context.PruneSelection(); // Deleted descendants too
		return FinishEdit(context, transaction, { { "deleted", std::move(deleted) }, { "count", count } });
	} });
```

1. **Line 209:** the step is named after the entities, with the empty transaction.
2. **Lines 210–211:** each subtree is tracked before anything is destroyed.
3. **Line 213:** the count of tracked states includes the descendants.
4. **Line 215:** one call destroys all entities.
5. **Line 217:** `FinishEdit` records the step and returns the deleted ids and the count.

The creation starts with an empty transaction, because nothing exists yet. It creates the entity and then calls `TrackCreated`, so that the entity and its subtree are in the step. When the scene is full, or the components do not fit, the command calls `RollBackEdit`: the half-created entity is removed and the command fails without a step. The delete command tracks every subtree before it destroys anything, because a deleted entity cannot be captured. It counts the states first, which includes the descendants, and the answer returns to the caller as `count`.

## Continuous edits and the inspector

A drag in the inspector changes a value every frame. Each frame is a complete edit, with its own transaction, and the history must show one step. The edit function that the inspector calls is `SetPropertyWithUndo`. Read how it builds the key.

```cpp src="StrataEditor/src/Editor/PropertyEdit.cpp#L135-L155" overload="1" symbol="SetPropertyWithUndo"
bool SetPropertyWithUndo(EditorContext& context, Entity entity, const ComponentInfo& component, const PropertyInfo& property, const PropertyValue& value,
	std::string* outError)
{
	if (!entity)
	{
		if (outError)
			*outError = "The entity does not exist";
		return false;
	}
	if (!context.CheckSceneEditable(outError))
		return false;
	const std::string mergeKey = fmt::format("Property/{}/{}/{}", entity.GetUUID().ToString(), component.Name, property.Name);
	SceneEditTransaction transaction(*entity.GetScene(), fmt::format("Edit {} {}", component.DisplayName, property.DisplayName), { entity.GetUUID() }, mergeKey);
	if (!ComponentAccess::SetProperty(entity, component, property, value, outError))
	{
		transaction.Rollback();
		return false;
	}
	context.CommitEdit(transaction);
	return true;
}
```

1. **Line 144:** a scene that is opening refuses the edit.
2. **Line 146:** the merge key holds the entity, the component and the property.
3. **Line 147:** the transaction tracks the entity and carries the key.
4. **Lines 148–152:** a failed write rolls the edit back.
5. **Line 153:** the gate records the step, which merges with the frame before it when the keys match.

The key is made from the entity, the component and the property: for a position on one entity, the same text on every frame, and a different text for another entity or another property. Frames with the same key merge, and that is the **undo merge**: a drag's many changes combined into one step. Dragging the position of `Rig` and then its scale gives two steps, because the keys differ. The edit of several entities at once puts the first entity, their count, the component and the property in the key, so the same selection edited again merges, and another selection does not. A failed property write rolls the transaction back before it reaches the gate.

Merging has to stop at some point, or the next drag would merge into the last one. The inspector calls `BreakMerge` when its widget reports that the edit is finished: the mouse is released, or the person leaves the field. The :term[gizmo]{id=gizmo-start} in the Scene view takes another way. A drag of the gizmo creates a key with a fresh random UUID inside it, so two drags of the same entities never merge, and it also breaks the merge when it starts. [The Scene view](../editor-ui/scene-view.md) shows the drag.

The save breaks the merge too, as the toy showed: the stack refuses to merge a new edit into a step when the save point sits at the same position. Saving in the middle of a drag therefore ends the step, and the part after the save is a step of its own. One undo then returns to the saved scene.

## A step that does not change the scene

A material is a file with its own save. Editing it through the editor writes the file at once, so the edit does not make the scene "modified". The class that records such an edit is `AssetDocumentAction`. It stores the :term[bytes]{id=byte} of the document before and after. Its `Execute` and `Undo` write one of them back and publish the result as the loaded asset, so everything that uses the material shows the change in the same frame.

```cpp src="StrataEditor/src/Editor/AssetEdit.h#L115-L128"
class AssetDocumentAction final : public EditorAction
{
public:
	AssetDocumentAction(EditorAssetManager& assets, AssetHandle handle, std::string name, std::vector<uint8_t> before, std::vector<uint8_t> after,
		std::string mergeKey = {});

	const std::string& GetName() const override { return m_Name; }
	bool Execute(std::string* outError) override;
	bool Undo(std::string* outError) override;
	// Consecutive edits with the same non-empty key of the same asset: the step keeps its state before and takes the
	// next one's state after.
	bool MergeWith(const EditorAction& next) override;
	bool IsNoOp() const override { return m_Before == m_After; }
	bool ChangesScene() const override { return false; }
```

1. **Line 118:** the constructor takes the document's bytes before and after, and an optional merge key.
2. **Lines 122–123:** `Execute` and `Undo` write one of the two documents.
3. **Line 126:** a merge needs the same key and the same asset.
4. **Lines 127–128:** a step that changed nothing is a no-op, and it never changes the scene.

Three lines carry the design. The `ChangesScene` line returns false, which keeps the modified flag honest, and the `IsNoOp` line compares the bytes, so editing a material and putting the value back leaves no step. The action refers to the project's asset manager weakly: when the project closes, the history is cleared with it. A step that lasted past the project would only fail with the reason "the project this edit belongs to is closed". [Trash and references](../editor/trash-references.md) teaches the steps of files and the trash, whose undo must check what is on the disk.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Command objects with their own inverse | Many desktop editors and tools written with the command pattern | Small steps: only parameters are stored | A tested inverse for every command, and every agent-written command needs one too |
| Transaction buffer with announced objects | Unreal Engine's transactions, Unity's call that records an object | Familiar to people who know those engines; no capture of untouched entities | Silent holes when code forgets to announce; no check that a command tracked what it changed |
| Persistent data structures | Version control systems, some functional editors | Cheap history of any length, and cheap branching | A rewrite of the scene storage; the ECS writes components in place |
| Memento of the whole scene | Small tools with small documents | The simplest code of all: copy it all | About 20 MB a step in the 10,000 entity example, so 10 GB at 512 steps |
| Mementos per entity plus actions of their own (Strata) | Strata | One step type for every scene edit; actions where a check of the world matters | Whole entity data stored twice for a one-value change; a command must track what it touches |

Every row costs something, and Strata's costs are the last row's. The memory cost is real but bounded: the stack holds at most 512 steps, and merged drags share their after states instead of copying. The tracking cost falls on each command author, who must track every entity the edit touches.

## How it is tested

The history and the scene steps are tested in two suites. `Editor.Undo` (in `StrataTests/src/Editor/UndoStackTests.cpp`) tests the history alone with a toy action that adds a delta to a shared integer. `Editor.SceneEdit` (in `StrataTests/src/Editor/SceneEditTests.cpp`) tests entity states against a real scene.

The history's tests cover each rule of this page:

- Actions are undone and applied again in order, and failed actions are not recorded.
- Continuous edits merge until the break, and a merge that returns to its start leaves no step.
- The save point, the modified flag and a save point before every action behave as described.
- The capacity drops the oldest step.
- A redo that fails drops the rest, and an undo that fails keeps the step.
- Groups run as a whole, and observers hear the steps in the order they were added.

The scene tests cover the algorithm and the transaction:

- Deleted subtrees return with their UUIDs, components and sibling order.
- Created entities disappear on undo and return with the same UUID on redo.
- Moves to a new parent and orders that agree by chance come back right.
- Edits without changes record nothing, and failed edits roll back.
- Components that this build does not know survive the round trip.
- Steps in a world wait for cells that are not loaded.

Run one suite directly with a filter, or the whole editor group with the test preset.

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Undo
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.SceneEdit
```

The commands run each suite alone. A failure names the test case, which names the rule it protects.

## Changing it safely

There are two ways to add a step. For a change to entities, use a `SceneEditTransaction` and commit it through the gate; for a change to something else, write an `EditorAction`. In both cases the checks below decide whether the step is right.

- **Track before you change.** A state captured after a change is not a before state. The test to write: change, undo, and compare the scene with a snapshot taken at the start.
- **Track created entities after you create them,** and a subtree before you delete it. A missed entity is not undone, and no error says so.
- **Give a continuous edit a merge key and break the merge when it ends.** Without the key, each frame is a step; without the break, the next drag joins the last.
- **Design for a failed undo.** Check in both `Execute` and `Undo` that the world still fits the step, return the reason, and change nothing when you refuse. The rename exercise below shows the shape.
- **Say when a step does not change the scene.** Override `ChangesScene` to return false for a step that writes its own file, so that the scene is not marked modified, and override `IsNoOp` where an edit can return to its start.
- **Restore entities through `ApplyEntities`.** An action that changes entities in its own undo needs UUIDs, order and cells back together, which only this function does.

:::rule
A step that does not change the scene says so, and asset steps never make the scene look changed since its last save. The reason is that a person must not be asked to save a scene for an edit that is already on disk. See [Saving](../editor/saving.md).
:::

Before you merge a change, run `Editor.Undo` and `Editor.SceneEdit`, and write a regression test that fails without your change. A new action gets its own test that does, undoes, redoes and checks the failure path.

## Summary

- The history holds steps with a position. A new edit drops the redo branch, merges into the latest step while a merge key matches, drops a merged no-op step and trims the oldest step beyond 512. A failed undo keeps the step, and a failed redo drops it and all after it.
- Four approaches exist (command objects with inverses, mementos, transaction buffers, persistent structures), and Strata uses mementos per entity for the scene and actions of their own for files, documents and settings.
- A scene edit is a transaction that tracks entities before it changes them, tracks created ones after, and records before and after states; `ApplyEntities` puts them back in three batches with the same UUIDs.
- An action for a change outside the scene returns a reason when its undo does not fit, says that it does not change the scene, and checks that the world still fits the step.
- The modified flag compares the position with the save point and counts only steps that change the scene; a trimmed or dropped save point leaves the scene modified.

## Check yourself

1. Starting at value 0 in the toy, you run a step that adds 4 and cannot merge. You save. You drag three times with steps that add 1 and can merge, and then press undo once. What are the value, the number of steps and the modified flag?

   :::answer{tests="predict-history,history-rules"}
   The value is 4, the history holds 2 steps with the position at 1, and the flag is false. The first drag edit makes a new step, because the save point sat at position 1 and merging across it is refused, and the next two merge into it. One undo reverts the whole drag, which waits as the redo branch, so the position returns to 1, the save point, and no step between the two positions changes the scene.
   :::

2. A step's `Undo` returns false because a file it needs is gone. What does the history do?

   - A. It removes the step and continues.
   - B. It keeps the step applied, leaves the position where it is, logs the reason and returns it.
   - C. It removes the step and every step after it.
   - D. It clears the whole history.

   :::answer{tests="history-rules"}
   B is right. Nothing changed, so the person can fix the cause and press undo again. A and C describe redo, which drops the step and all after it, because redo applies an edit to a world that moved on. D is a reset that only happens when a project closes or another scene opens.
   :::

3. A command deletes an entity and then calls `TrackSubtree` on it. What goes wrong, and which call would fix it?

   :::answer{tests="scene-edits"}
   A deleted entity cannot be captured, so the before state says it does not exist, and the step records no delete at all: undo cannot bring the entity back, and nothing reports it. The fix is to call `TrackSubtree` before the command deletes anything, as `entity.delete` does. For a created entity the rule is the opposite: call `TrackCreated` after creating it.
   :::

4. A command changes 3 entities of a scene that holds 100,000. Which approach stores the least, and which can undo a delete without any extra code?

   - A. Command objects with an inverse store the least, and mementos need no extra code.
   - B. Mementos store the least, and command objects need no extra code.
   - C. A copy of the whole scene stores the least, and mementos need no extra code.
   - D. Command objects store the least, and a persistent structure needs no extra code.

   :::answer{tests="compare-approaches"}
   A is right. A command object stores only parameters, which is smaller than states of 3 entities, but its inverse must be written for each command. Mementos store whole states of the 3 touched entities, and recreate a deleted one without any inverse. C is wrong, because the whole scene is the largest copy. B swaps the two facts, and D fails because a persistent structure needs the whole engine written that way.
   :::

5. You write an action that renames a file. Its `Execute` renames the file and its `Undo` renames it back. What must `ChangesScene` return, and what must `Undo` check first?

   :::answer{tests="write-step"}
   `ChangesScene` must return false, because saving the scene does not save the file and the rename must never make the scene modified. `Undo` must check that the new name still exists and that the old name is free, return a reason when not, and change nothing. Without the check, undo could replace a file that something else created in the meantime.
   :::

## Exercises

1. **Basic.** Run `Editor.Undo`, then add a test case to `UndoStackTests.cpp` that shows that a merged drag, a save and another drag give two steps.

   :::answer[Worked solution]{tests="history-rules,predict-history"}
   Run the suite first with `StrataTests.exe --test-suite=Editor.Undo` and read the cases for merging and for the save point. The new test uses the test file's `AddAction` with its `mergeable` argument set.

   ```pseudocode
   TEST_CASE("A merged drag, a save and another drag are two steps")
   {
   	int value = 0;
   	UndoStack stack;
   	stack.Execute(CreateScope<AddAction>(value, 1, true));
   	stack.Execute(CreateScope<AddAction>(value, 2, true));
   	stack.MarkSaved();
   	stack.Execute(CreateScope<AddAction>(value, 3, true));
   	stack.Execute(CreateScope<AddAction>(value, 4, true));
   	CHECK(stack.GetHistory().size() == 2);
   	REQUIRE(stack.Undo());
   	CHECK(value == 3);
   	CHECK_FALSE(stack.IsModified());
   }
   ```

   1. **Lines 5–6:** two edits that accept a merge become one step.
   2. **Line 7:** the save breaks the merge and marks position 1.
   3. **Lines 8–9:** the third edit starts a second step, and the fourth merges into it.
   4. **Line 10:** the history holds two steps.
   5. **Lines 11–13:** undo returns to the saved state.

   The first two edits merge into one step with delta 3. `MarkSaved` breaks the merge and sets the save point at position 1, so the third edit starts step two, and the fourth merges into it. The undo reverts the second step, which waits as the redo branch, and returns to the saved position, so the value is 3 and the scene is not modified. To check that the test can fail, comment out the `MarkSaved` line: the history then holds one step, and the test fails.
   :::

2. **Medium.** Write an undo step for a file rename whose undo checks that the world still fits it. Show that an undo blocked by another file reports why and changes nothing.

   :::answer[Worked solution]{solution="sketches/editor-undo-rename.cpp" tests="write-step"}
   The action keeps both names and one function that moves a file from one name to the other. Both `Execute` and `Undo` call it, in opposite directions, and it checks two things: the source exists and the target is free. It returns a reason and changes nothing when either fails.

   ```cpp sketch="editor-undo-rename.cpp"
   #include <cstdio>
   #include <set>
   #include <string>
   #include <utility>

   using Files = std::set<std::string>;

   // A rename of a file that checks, in both directions, that the world still looks as the step expects.
   class RenameAction
   {
   public:
   	RenameAction(Files& files, std::string from, std::string to)
   		: m_Files(files), m_From(std::move(from)), m_To(std::move(to))
   	{
   	}

   	bool Execute(std::string* error) { return Move(m_From, m_To, error); }
   	bool Undo(std::string* error) { return Move(m_To, m_From, error); }
   private:
   	bool Move(const std::string& source, const std::string& target, std::string* error)
   	{
   		if (!m_Files.contains(source))
   		{
   			*error = "'" + source + "' is gone";
   			return false;
   		}
   		if (m_Files.contains(target))
   		{
   			*error = "'" + target + "' is taken";
   			return false;
   		}
   		m_Files.erase(source);
   		m_Files.insert(target);
   		return true;
   	}
   private:
   	Files& m_Files;
   	std::string m_From;
   	std::string m_To;
   };

   static void Show(const char* label, const bool ok, const std::string& error, const Files& files)
   {
   	std::printf("%-14s %-4s files:", label, ok ? "ok" : "FAIL");
   	for (const std::string& file : files)
   		std::printf(" %s", file.c_str());
   	std::printf("%s%s\n", ok ? "" : "  reason: ", error.c_str());
   }

   int main()
   {
   	Files files = { "a.txt" };
   	std::string error;
   	RenameAction rename(files, "a.txt", "b.txt");
   	Show("rename", rename.Execute(&error), error, files);
   	files.insert("a.txt"); // Something else takes the old name in the meantime.
   	error.clear();
   	Show("undo (blocked)", rename.Undo(&error), error, files);
   	files.erase("a.txt");
   	error.clear();
   	Show("undo (free)", rename.Undo(&error), error, files);
   	return 0;
   }
   ```

   ```text output-of="editor-undo-rename.cpp"
   rename         ok   files: b.txt
   undo (blocked) FAIL files: a.txt b.txt  reason: 'a.txt' is taken
   undo (free)    ok   files: a.txt
   ```

   1. **Line 17:** `Execute` and `Undo` call the same function in opposite directions.
   2. **Lines 22–26:** the source must exist, or the step returns a reason and changes nothing.
   3. **Lines 27–31:** the target must be free, with the same rule.
   4. **Lines 32–34:** only after both checks do the files change.

   The first undo fails with "'a.txt' is taken", and the files stay as they were, so the history can keep the step. After the blocking file goes away, the same undo succeeds. In the engine the class would also return false from `ChangesScene`, and keep its other state in the step, as `AssetDocumentAction` does.
   :::

3. **Hard.** Trace it yourself. Delete a parent with two children with `entity.delete`, then run `edit.undo` with a breakpoint in `ApplyEntities`. Name its destroy batch, its recreation with the same UUIDs and its placement batch as they run.

   :::answer[Worked solution]{tests="scene-edits"}
   The command is registered in `StrataEditor/src/Editor/Commands/EntityCommands.cpp`; its handler tracks each subtree and calls `FinishEdit`. The undo path is `edit.undo`, then `EditorContext::Undo`, then `UndoStack::Undo`, then `SceneEditAction::Undo`, then the function `SceneEdit::ApplyEntities` in `StrataEditor/src/Editor/SceneEdit.cpp`. At the breakpoint, the destroy batch finds no state with `Exists` false, so it destroys nothing. The recreation builds one JSON document of the parent and its two children and passes it to `SceneSerializer::DeserializeEntities` with new UUIDs switched off. The placement batch then marks the list of roots, because the parent was appended at the end, and places it at its recorded position.
   :::

## Where it lives in Strata

- History: `StrataEditor/src/Editor/UndoStack.h` and `UndoStack.cpp` (`EditorAction`, `EditorActionGroup`, `UndoStack`, `UndoStackObserver`).
- Scene steps: `StrataEditor/src/Editor/SceneEdit.h` and `SceneEdit.cpp` (`EntityState`, `SceneEditTransaction`, `SceneEditAction`, `SceneSettingsAction`, `SceneEdit::ApplyEntities`).
- Inspector edits: `StrataEditor/src/Editor/PropertyEdit.cpp` (`SetPropertyWithUndo`). Gizmo drags: `StrataEditor/src/Editor/TransformEdit.cpp`.
- The gate: `StrataEditor/src/Editor/EditorContext.cpp` (`CommitEdit`, `Undo`, `Redo`); command helpers `FinishEdit` and `RollBackEdit` in `StrataEditor/src/Editor/CommandUtils.cpp`.
- Asset steps: `StrataEditor/src/Editor/AssetEdit.h` (`AssetDocumentAction`).
- Commands: `edit.undo`, `edit.redo` and `edit.history` in `StrataEditor/src/Editor/EditorStateCommands.cpp`; `editor.batch` in `StrataEditor/src/Editor/Commands/BatchCommands.cpp`.
- Tests: suites `Editor.Undo` and `Editor.SceneEdit` in `StrataTests/src/Editor/`.

## Further reading

- Unity documentation, the Undo class and its RecordObject function (<https://docs.unity3d.com/ScriptReference/Undo.RecordObject.html>): how a transaction buffer asks code to announce objects before a change. Beginner.
- Unreal Engine documentation on transactions: how the editor records object changes in scoped transactions. Intermediate.
- Gamma, Helm, Johnson and Vlissides, "Design Patterns", the Command and Memento patterns: the classic account of the first two approaches. Intermediate.
- Chris Okasaki, "Purely Functional Data Structures": persistent structures and why sharing makes old versions cheap. Advanced.
