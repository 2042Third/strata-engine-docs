---
id: editor/saving
title: "Saving without stalling"
description: "How the editor saves a scene in the background without freezing, and how every command that replaces work first protects what nobody has saved."
kind: internals
size: L
tracks: [E]
needs: [editor/undo, editor/deferred-commands, core/files, core/jobs]
time: 100
learn:
  - id: snapshot-job
    text: explain why a save takes a snapshot in the frame and writes it on a background job
  - id: save-point
    text: predict which edits stay unsaved when a background save ends
  - id: claim-publish
    text: name what the atomic write, the document claim and the publish each protect
  - id: coalescing
    text: explain how a newer save replaces a queued one and who hears about it
  - id: guard
    text: choose the guard, the wait for saves and the deferral for a command that replaces the scene
since: 0.4.0
status: final
---

When you press save, the editor must write the whole scene to disk, and that work must not stop the frames you are
looking at. The editor's saving code takes a copy of the scene in one frame, hands it to a background job, and lets you
keep editing while the job writes. It also decides, when the job ends, which of your edits the file holds and which it
does not. The second half of the page covers the opposite risk: commands such as opening another scene or closing the
project, which could throw away work nobody saved.

Four neighbors are left to other pages. [The editor shell](../editor-ui/shell.md)
covers how the interface asks the person. [Recovering work](../editor/recovery.md) covers the recovery journal,
[Files you can trust](../core/files.md) the atomic write itself, and [Worlds in the editor](../editor/worlds.md) the world's two-step save.

## The problem and how engines solve it

Start with a number from Strata's own history. In 0.3.0, saving a scene of one million entities froze the editor for 22 s
on the development machine, as the release notes of 0.4.0 say. At 60 :term[frames per second]{id=frame-rate} a frame lasts 16.7 ms, so 22 s is
about 1,320 frames in which nothing was drawn and no key was read. A person who sees a frozen window for 22 s may
believe the program has crashed and kill it, and that is the moment the save was written for.

A second problem hides behind the first. A command that replaces the scene, such as opening another one, destroys every
edit that is not on disk. The editor needs to know exactly what is on disk, and an answer such as "something was saved a while ago" is not enough.

Four first answers are natural, and each one fails in a way you can name.

1. **Save on the main thread.** The code turns the scene into file :term[bytes]{id=byte} inside the frame. It is the simplest design, and it is the
   0.3.0 behavior: the freeze grows with the scene.
2. **Keep one dirty bit.** A flag says "changed since the last save". A bit cannot say which edits a file holds, so it
   cannot answer the question of a save that takes seconds while you keep working.
3. **Mark everything saved when the save ends.** Suppose the save starts at second 0 and ends at second 5, and you
   edit at second 2. The file holds the scene of second 0, and the editor now believes the scene of second 5 is on disk.
   Close the editor and the edit is gone, silently.
4. **Write the file in place.** The writer opens the target file and replaces its content step by step. If the program, the power or the disk
   fails 3 s into a 5 s write, the old scene is destroyed and the new one is half written.

Engines and tools meet this problem in a few ways. Some block and show a progress bar. Some lock the scene as read-only while
it is written, which keeps the freeze out of the frame but stops the person from working.

Others copy the data first and write the copy later, which costs memory and time for the copy and gives the person all their frames back. A few use the
:term[operating system]{id=operating-system} to copy a whole process cheaply. Others keep a log of edits and replay it, so a save writes only what changed.
Strata copies the scene and writes the copy on a job. The page [Alternatives Strata did not choose](#alternatives-strata-did-not-choose)
compares them, and the rest of this page shows how Strata makes the copy-and-write approach safe.

:::question
Why not make the freeze shorter by writing faster?

Writing faster moves the limit but keeps the rule that a bigger scene means a longer freeze. A scene ten times larger
freezes ten times as long, and the freeze is the problem however long it lasts.
:::

## The map

Two ideas make a background save safe. The first idea is the save itself. Take a copy in the frame and convert it to bytes on a job.
Write it so that a crash cannot hurt, and give the result back on the :term[main thread]{id=main-thread}. The second idea is the guard: every command
that would discard work checks first, waits for saves in flight, and discards only what it was told to discard.

The diagram shows who owns what. Everything above the job line runs on the main thread, which owns the scene and the undo
history, as the [job system page](../core/jobs.md) explains for every engine program.

```mermaid caption="The files of a scene save. The command and the context run on the main thread, the save queue hands one job to the job system, and the asset manager holds the claim on the file." alt="A flow chart. The scene.save command calls the editor context, which calls the save queue. The queue claims the file in the asset manager and submits a job. The job writes the file and the queue publishes the result back through the asset manager."
flowchart TB
  subgraph Main["Main thread"]
    Cmd["scene.save"] --> Ctx["EditorContext: SubmitSceneSave"]
    Ctx --> Saver["DocumentSaver: Submit, Update"]
    Saver --> Claim["EditorAssetManager: ClaimDocumentWrite"]
    Saver --> Publish["EditorAssetManager: PublishWrittenDocument"]
    Ctx --> Ended["EditorContext: OnSceneSaveEnded"]
  end
  subgraph Job["Background job"]
    Write["SceneDocumentWriter, hash, AtomicFileWriter, Commit"]
  end
  Saver -- "JobSystem::Submit" --> Write
  Write -- "Done flag" --> Saver
  Saver -- "completion" --> Ended
```

Five files carry the design:

- `StrataEditor/src/Editor/DocumentSaver.cpp` is the one path for saving engine-native documents.
- `StrataEditor/src/Editor/EditorContext.cpp` starts a scene save and reacts when it ends.
- `StrataEditor/src/Editor/SettingsFileWriter.cpp` writes the project file and the preferences by the same recipe.
- `StrataEditor/src/Editor/CommandUtils.cpp` holds the guard.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp` owns the claim on a file and the publish.

## The contract of a save

A save has four steps, and each one protects something. Read the steps in order, because each one exists for the reason
the one before it creates.

The first step is the **snapshot** (save), a private copy of the scene that the frame makes and no later edit can reach. A
background job writes from it. The frame does only the copy and a few numbers. It does not convert anything to bytes, scan
references or touch the disk, and a test of `Editor.Saves` checks that the frame which starts a save converts nothing.

The second step is the write, and it runs on a job, never in the frame. The job streams the snapshot through
`SceneDocumentWriter`, scans the references the document makes, :term[hashes]{id=hash} the :term[bytes]{id=byte} and writes them to a temporary file beside
the target. Only when every byte is written does it replace the target in one step, the atomic write of
[Files you can trust](../core/files.md). A crash at any moment leaves the old file or the new one, never half of each.

The third step protects the file from the editor itself. The :term[asset manager]{id=asset-manager} watches the asset folder, and a save without
protection would look like an outside change: the watcher would search the file again and reload it under the person's hands. A
**document claim** is a lock that the asset manager holds on the file a save writes. While the claim lives, the watcher leaves the
path alone, and a move or a trash of that asset fails. The claim also takes the manager's exclusive :term[file lock]{id=file-lock} for the
moment of the replace, so no reader has the file open while it changes.

The fourth step is the **publish**: making the written document the asset's state, on the main thread, in one cheap step.
The job already knows the file's size, time and references, so the main thread reads nothing from disk again. Publishing on
the main thread keeps the asset registry in the one place that may change it.

One more rule keeps repeated saves cheap. Press save three times in a row while the first save writes, and the editor
would hold three copies of a large scene. **Coalescing** means that a newer save of the same documents takes the place of one still waiting in the queue.
The newer snapshot is written once, and both requests are told when it is on disk, each with the status of that one write.

:::rule[Saves never convert a document on the main thread]
Converting a million entities holds a frame for seconds, as 0.3.0 showed. Saves go through `DocumentSaver`, and the project
file and the preferences go through `SettingsFileWriter`.
:::

## Save points under concurrent edits

The editor must know afterwards which edits the file holds. The undo history already numbers its actions, so a :term[save point]{id=save-point} can
name a state of the history.

A **save point** records four numbers. The first is the position, how many actions are applied. The second is the
serial of the latest applied action, the number the history gave that action when it was recorded. The third is the history's generation, since clearing the history starts a new one.
The fourth counts scene changes trimmed from the front.

A worked example uses three actions with serials 1, 2 and 3. A save starts while the history holds all three, so the point
is position 3, serial 3.

Edit D (serial 4) happens while the job writes. When the save ends, the editor calls
`MarkSaved` with the point. The history finds the action with serial 3, so the saved position becomes 3. The history now
holds 4 applied actions and 4 differs from 3, so the scene is modified, which is true: D is not on disk. Undo D, and the
position is 3 again: the scene is clean, which is also true.

The point stays right wherever the history moves. Undo twice and edit E instead, and the history drops actions 2 and 3, so no
action with serial 3 exists any more. `MarkSaved` finds none, stores "no save point" and the scene stays modified for
good, because no state of the history matches the file. A point from another generation marks nothing: that history was
cleared, and the scene is another scene.

One trap remains. A drag in the viewport sends a new position every frame, and the :term[undo stack]{id=undo-stack} merges those frames into one
action to keep the history short. Merging changes an action after it was recorded.

Suppose a save starts while the drag is
at x = 1 and the drag continues to x = 2 inside the same action. Marking that action saved then claims that x = 2 is on disk,
while the file holds x = 1. The remedy is to end merging before the point is taken, so the next edit starts an action of
its own. A test of `Editor.Saves` checks the numbers 1 and 2 of this very example: a continuous edit begun before the save does not merge into the saved step.

:::rule[Take the save point after ending the merge]
Frames of a drag that continues would otherwise change the saved action after the point named it, and no state of the history would match the file.
`SubmitSceneSave` calls `BreakMerge` first, then `GetSavePoint`. The mechanism is the subject of
[Undo and redo](../editor/undo.md).
:::

The quote is `UndoStack::MarkSaved` taking a save point. Notice its three outcomes: nothing, a position, or "no save point".

```cpp src="StrataEditor/src/Editor/UndoStack.cpp#L285-L295"
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
```

1. **Line 285:** a point of another generation returns before anything changes.
2. **Line 288:** serial 0 means the state before every action, still the front of the history unless scene changes were
   trimmed off it since.
3. **Line 294:** the serial is found now, wherever the history has moved.
4. **Line 295:** found, the saved position is the index after that action; not found, `c_NoSavePoint` keeps the scene modified.

## The contract of the guard

The second idea concerns commands that throw away the edited scene: opening another one, closing the project or quitting. Such a command
destroys every edit that is not saved. Three terms describe what the command may do about it.

A **discard scope** names how much a replacing command throws away. `Scene` fits commands that replace the scene (`scene.open`,
`scene.new`, `scene.recover`). `Project` fits those that also release the project (`project.open`, `project.create`,
`project.close`, `project.openSample`). `Editor` fits `editor.quit`, which also lets go of the person's preferences.

The parameter `force` lets a command discard changes that are not saved. Without it the command fails and says why. With it the
command continues. The scene's discarded changes are kept as recovery data when the project can hold them; a scene
without a project loses them, and so do unwritten settings within the scope.

**Unwritten settings** are changes to the project or the preferences that the disk never received, because the last write failed.
The newest values are only in memory. They count as work that is not saved, and the guard names them when the scope would drop them. A settings write that
failed stays unwritten until a later write succeeds.

Two rules follow from this. First, a command checks before it acts: `CheckUnsavedChanges` returns a failure when anything
at stake is not saved, unless `force` is true.

Second, a command never discards a save that is still in flight, because the file will hold that work in a moment. The command
waits instead, through `AfterSaves`, and decides only after the save was published. A forced command waits too: `force` discards edits, never a save.

```mermaid caption="The decision of a command that replaces the scene. It waits for saves in flight first, then refuses or continues depending on what is not saved and on whether force is set." alt="A flow chart. A command first asks whether saves are in flight and, if so, waits and asks again. It then asks whether force is set; if so it continues. Otherwise it asks whether the scene has changes that are not saved or whether settings are unwritten within its scope; if so it fails with the reason, and if not it continues."
flowchart TB
  A["Command that replaces the scene"] --> B{"Saves in flight?"}
  B -- yes --> W["Defer: ask again next frame"]
  W --> B
  B -- no --> C{"force set?"}
  C -- yes --> G["Continue; scene changes go to recovery"]
  C -- no --> D{"Scene modified, or settings unwritten within the scope?"}
  D -- yes --> F["Fail with the reason"]
  D -- no --> G
```

:::rule[Replacing commands combine three pieces]
A command that replaces the scene, closes the project or quits calls `CheckUnsavedChanges`, runs inside `AfterSaves` and is
registered with `MayDefer`. Without `AfterSaves`, a forced command could replace the scene while a save still runs. See
[Deferred commands](../editor/deferred-commands.md) for `MayDefer`.
:::

## A toy version

:::question
The toy uses a thread, an atomic flag and a lambda, which [Threads](../basics/threads.md) and
[Generic C++](../basics/cpp-generic.md) explain; classes and references are in [C++ basics](../basics/programming-3.md).
:::

The toy below saves a scene of names the way Strata does, with every real detail removed. It takes a snapshot, writes it on
another thread through a temporary file and a rename, and lets the main thread edit meanwhile. It marks the save point
only when the job ends, and it prints what the naive "mark everything saved" would have claimed. Notice where each number is taken.

```cpp sketch="editor-saving-toy.cpp"
// A toy background save: snapshot in the frame, write on another thread, then mark the save point.
#include <atomic>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

struct Scene
{
	std::vector<std::string> Names;
};

static void WriteAtomically(const std::filesystem::path& target, const Scene& snapshot)
{
	// Write beside the target, then replace it in one step: a crash leaves the old file or the new one.
	const std::filesystem::path temporary = target.string() + ".tmp";
	{
		std::ofstream file(temporary);
		for (const std::string& name : snapshot.Names)
			file << name << '\n';
	}
	std::filesystem::rename(temporary, target);
}

int main()
{
	const std::filesystem::path target = "strata-toy-save.txt";
	Scene scene{ { "Camera", "Sun" } };
	size_t edits = 2;      // Edits applied to the scene so far
	size_t savedEdits = 0; // The save point: how many edits the file on disk holds

	// Frame 1: the only work of the frame is a copy and a number.
	const Scene snapshot = scene;
	const size_t savePoint = edits;
	std::atomic<bool> release = false; // Holds the job so that the frames below happen while it "writes"
	std::atomic<bool> done = false;
	std::thread job([&]()
	{
		while (!release.load())
			std::this_thread::yield();
		WriteAtomically(target, snapshot);
		done.store(true, std::memory_order_release);
	});

	// Frames 2 and 3: the person goes on editing.
	scene.Names.push_back("Tree");
	edits++;
	scene.Names.push_back("Rock");
	edits++;
	release.store(true);

	// A later frame: the job ended, so the main thread publishes the result.
	while (!done.load(std::memory_order_acquire))
		std::this_thread::yield();
	job.join();
	savedEdits = savePoint;
	const size_t naiveSaved = edits; // What marking "everything saved" now would claim

	std::ifstream file(target);
	std::string line;
	size_t lines = 0;
	while (std::getline(file, line))
		lines++;
	std::cout << "file holds " << lines << " names, scene has " << scene.Names.size() << "\n";
	std::cout << "modified: " << (edits != savedEdits ? "yes" : "no") << "\n";
	std::cout << "naive mark at the end would say modified: " << (edits != naiveSaved ? "yes" : "no") << "\n";
	file.close(); // Windows refuses to remove an open file
	std::filesystem::remove(target);
	return 0;
}
```

```text output-of="editor-saving-toy.cpp"
file holds 2 names, scene has 4
modified: yes
naive mark at the end would say modified: no
```

1. **Lines 35–36:** the frame's whole work: a copy and the save point, in the same frame.
2. **Line 24:** the rename replaces the target in one step, so a crash leaves one whole file.
3. **Lines 48–51:** two edits arrive while the job waits; they change the scene but not the snapshot.
4. **Line 58:** only after the job ended does the main thread mark the save point.
5. **Line 68:** the naive mark taken at the end would claim that nothing is modified.

The file holds two names because the snapshot was taken when the scene had two. The scene now has four, so it is
still modified: its two newer edits are not on disk. The naive mark would have said "not modified", and closing
the editor would have lost both edits without a word. Strata keeps exactly this separation of snapshot, job, save point and
publish, and adds the details that real documents, real failures and real users need.

## The real code: a scene save

A scene save starts in `EditorContext::SubmitSceneSave`. Notice the order of the first three actions: break merging, take the
save point, copy the scene.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1048-L1064"
m_UndoStack.BreakMerge();
DocumentSaveRequest request;
request.SavePoint = m_UndoStack.GetSavePoint();
request.Snapshot = Scene::Copy(m_EditScene, SceneCopyOptions { true });
request.Label = m_EditScene->GetName();
DocumentSaveItem item;
item.Asset = handle;
item.NewPath = newPath;
request.Items.push_back(std::move(item));
const SceneRecovery::SaveToken token = m_Recovery->BeginSave();
const uint64_t id = m_DocumentSaver.Submit(std::move(request), [this, handle, token, restore](const DocumentSaveStatus& status)
{
	OnSceneSaveEnded(status, handle, token, restore);
}, outError);
if (id == 0)
	m_Recovery->ReleaseSave(token);
return id;
```

1. **Line 1048:** end merging first, so the save point names a state the snapshot really holds.
2. **Line 1050:** the save point comes before the copy, in the same frame, so no edit can fall between them.
3. **Line 1051:** the copy keeps only what a scene file stores (`SerializedOnly`), and
   nothing changes it afterwards.
4. **Line 1057:** the recovery journal gets a token, so it can tell later which journal entries this save covers.
5. **Lines 1062–1063:** when the queue refuses the request, the token is released at once.

`DocumentSaver::Submit` validates the request, then queues it or starts it. Notice what happens when a queued request
already exists for the same documents.

```cpp src="StrataEditor/src/Editor/DocumentSaver.cpp#L244-L256"
const uint64_t id = m_NextID++;
for (const Scope<Pending>& queued : m_Queue)
{
	if (!SameDocuments(queued->Request, request))
		continue;
	// The queued request never started: the newer snapshot is written for both.
	ReleaseSnapshot(queued->Request.Snapshot);
	queued->Request = std::move(request);
	queued->Assets = m_Assets;
	queued->IDs.push_back(id);
	queued->Completions.push_back(std::move(onComplete));
	return id;
}
```

1. **Line 245:** only queued requests are candidates; the running one already holds its snapshot.
2. **Line 247:** two requests are the same when they write the same assets.
3. **Line 250:** the old snapshot is released, so a large scene is never held twice.
4. **Lines 253–254:** the newer request keeps the old request's id and completion, so every caller is told.

`DocumentSaver::Start` turns the request into a job. The claims are taken here, on the main thread, because the asset manager
is main-thread state.

```cpp src="StrataEditor/src/Editor/DocumentSaver.cpp#L270-L291"
void DocumentSaver::Start(Scope<Pending> pending)
{
	Ref<Job> job = CreateRef<Job>();
	job->Started = std::chrono::steady_clock::now();
	job->Snapshot = std::move(pending->Request.Snapshot);
	pending->Request.Snapshot = nullptr;
	job->Items.reserve(pending->Request.Items.size());
	for (const DocumentSaveItem& item : pending->Request.Items)
	{
		Job::Item& jobItem = job->Items.emplace_back();
		jobItem.Spec = item;
		jobItem.Result.Asset = item.Asset;
		std::string error;
		jobItem.Claim = pending->Assets->ClaimDocumentWrite(item.Asset, &error);
		jobItem.Result.Path = jobItem.Claim ? jobItem.Claim->GetPath() : item.NewPath;
		if (!jobItem.Claim)
			jobItem.Result.Error = error;
	}
	pending->Running = job;
	job->Handle = JobSystem::Submit([job]() { job->Run(); }, JobPriority::Background);
	m_Running = std::move(pending);
}
```

1. **Line 274:** the snapshot moves into the job, so the main thread keeps no reference to it.
2. **Line 283:** one claim per item; a claim that fails records its reason and the other items continue.
3. **Line 289:** the job runs at background priority, so saves never compete with the work a frame needs.

The job itself writes one item at a time. Notice the three results a writer reports: bytes, references and a hash.

```cpp src="StrataEditor/src/Editor/DocumentSaver.cpp#L184-L210"
	SceneWriteOptions options = item.Spec.Write;
	const float first = static_cast<float>(index) / static_cast<float>(Items.size());
	const float share = 1.0f / static_cast<float>(Items.size());
	options.Progress = [this, first, share](float done) { Progress.store(first + share * done, std::memory_order_relaxed); };
	if (!options.ExtraReferences)
		options.ExtraReferences = ScanExtraReferences;
	SceneWriteResult written;
	if (!SceneDocumentWriter::Write(*Snapshot, output, options, &written, &error))
	{
		result.Error = file.GetError().empty() ? error : file.GetError();
		return;
	}
	references = std::move(written.References);
	contentHash = written.ContentHash;
	result.Sha256 = written.Sha256;
	result.Entities = written.Entities;
}
result.References = references;
if (!item.Claim->Commit(file, contentHash, std::move(references), item.Written, &error))
{
	result.Error = error;
	return;
}
item.Written.Claim = item.Claim;
item.Written.Reload = item.Spec.Reload;
result.Bytes = item.Written.Size;
item.Committed = true;
```

1. **Line 187:** progress is an atomic number the main thread reads for the status, never a lock.
2. **Line 188:** the reference scan runs while the writer streams, so the references cost no second pass.
3. **Line 191:** the writer streams straight into the temporary file; no copy of the whole text exists in memory.
4. **Line 202:** `Commit` finishes the atomic write and replaces the target under the asset manager's lock.
5. **Line 210:** only a committed item is published later.

The commit itself lives in the asset manager. Notice what happens for a new asset and for a failure.

```cpp src="Strata/src/Strata/Asset/EditorAssetManager.cpp#L3982-L3996"
std::unique_lock<std::shared_mutex> fileLock(m_Work->FileMutex);
if (m_New)
{
	// Something appeared at the reserved place meanwhile: it is never overwritten.
	if (FileSystem::Exists(m_AbsolutePath))
		return fail(fmt::format("'{}' exists already: the new asset was not written", m_Path));
	if (!FileSystem::WriteText(GetMetaPath(m_AbsolutePath), m_MetaText))
		return fail(fmt::format("Could not write '{}{}'", m_Path, c_MetaExtension));
}
if (!file.Commit(&error))
{
	if (m_New)
		FileSystem::Remove(GetMetaPath(m_AbsolutePath));
	return fail(error);
}
```

1. **Line 3982:** the exclusive lock covers only the replace, never the long write.
2. **Line 3986:** something that appeared at a reserved path meanwhile is never replaced.
3. **Line 3988:** a new asset gets its `.meta` file before its document appears.
4. **Line 3991:** the rename is the atomic step; lines 3993–3994 remove the `.meta` file again when it fails.

When the job ends, it sets its `Done` flag, an atomic value that both threads may read safely. The main thread's next
`Update` sees the flag and runs `Collect`.

```cpp src="StrataEditor/src/Editor/DocumentSaver.cpp#L303-L319"
std::string errors;
for (Job::Item& item : job.Items)
{
	if (item.Committed)
	{
		m_Running->Assets->PublishWrittenDocument(item.Written);
	}
	else
	{
		if (item.Claim && item.Claim->IsNewAsset())
			m_Running->Assets->ReleaseNativeAssetReservation(item.Spec.Asset);
		errors += fmt::format("{}'{}': {}", errors.empty() ? "" : "; ", item.Result.Path.empty() ? item.Spec.Asset.ToString() : item.Result.Path,
			item.Result.Error);
	}
	item.Claim.reset();
	item.Written.Claim.reset();
}
```

1. **Line 304:** every item is looked at, so a request with one bad document still publishes the good ones.
2. **Line 308:** the publish: the written document becomes the asset's state.
3. **Line 313:** a failed new asset gives its reserved path and handle back.
4. **Line 314:** the errors collect into one message that names each failed item.
5. **Line 317:** the claim is dropped here, and the watcher takes notice of the path again.

The completion of the request then runs, once per id, so a save that replaced others tells everyone. For a scene save the completion is
`OnSceneSaveEnded`. Notice every outcome that is not a plain success.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1072-L1102"
const bool sameScene = status.SavePoint.Generation == m_UndoStack.GetSavePoint().Generation;
// A save as a new asset that failed gives the scene its previous handle and name back, also when a newer save of the
// new asset replaced it before it began (that one's completion has nothing to give back).
if (status.State != DocumentSaveState::Done && sameScene && restore && m_SceneHandle == handle)
{
	m_SceneHandle = restore->Handle;
	m_EditScene->SetName(restore->Name);
	m_EditScene->SetSourceAsset(restore->SourceAsset);
}
// A newer save of the same scene replaced this one before it began: the newer one's completion does the rest.
if (status.WrittenID != status.ID)
{
	m_Recovery->ReleaseSave(token);
	return;
}
if (status.State != DocumentSaveState::Done)
{
	m_Recovery->ReleaseSave(token);
	NotifySaveFailed(status.Label, status.Error, handle);
	return;
}
if (!sameScene)
{
	m_Recovery->ReleaseSave(token);
	return;
}
m_UndoStack.MarkSaved(status.SavePoint);
OnSceneSaved();
const auto [sceneFile, scenePath] = GetSceneFile(handle);
const std::string baseHash = status.Items.empty() ? std::string() : Crypto::ToHex(status.Items.front().Sha256);
m_Recovery->OnSaved(handle, sceneFile, scenePath, baseHash, token, *m_EditScene, IsSceneModified());
```

1. **Line 1072:** the editor compares the save point's generation with the history's: was the scene replaced meanwhile?
2. **Line 1075:** a failed Save As gives the scene its previous handle and name back.
3. **Line 1082:** a request that a newer one replaced does nothing more; the newer one's completion finishes the work.
4. **Line 1087:** a failed save releases the token and tells the person.
5. **Line 1098:** only now is the point marked saved, followed by the recovery journal's note at line 1102.

The differences from the toy are the ones the toy skipped. The toy has one document, no claim, no failure and one request
at a time. The real queue has items that fail independently, a claim per file, a queue with coalescing, a hash for the
recovery journal and a completion that handles several outcomes. The structure is the same.

The two commands that clients see are thin. `scene.save` answers once the file is published by default, and with
`wait` set to false it answers at once with a `saveId` and a `state` of Writing or Queued. The `saving` section of
`editor.status` lists the saves in flight, each with its `saveId`, `label`, `documents`, `state` and `progress`, so a client
can poll without waiting. In the editor window the status bar shows a save in flight, as the tests of `Editor.UI.Saves` check.

## The real code: settings and what is still in the frame

The project file and the preferences are small, but a slow disk or a failing one must not stall a frame either.
`SettingsFileWriter` repeats the recipe with a different job. Submitting a write queues it, and the writer runs one job at
a time. Look at how a second submit behaves while one write runs.

```cpp src="StrataEditor/src/Editor/SettingsFileWriter.cpp#L54-L66"
void SettingsFileWriter::Submit(WriteFunction write)
{
	if (m_Running)
		m_Waiting = std::move(write);
	else
		Start(std::move(write));
}

void SettingsFileWriter::Update()
{
	if (Collect() && m_Waiting)
		Start(std::exchange(m_Waiting, nullptr));
}
```

1. **Line 57:** a write submitted while another runs replaces the waiting one, which is coalescing again: the newest state wins.
2. **Line 59:** with nothing running, the write starts at once.
3. **Line 64:** `Update` starts the waiting write after the running one was collected.

A write owns a snapshot of the values, small copies made in the frame, so the job touches nothing the main thread changes.
`EditorContext::SaveProjectFile` shows it: the :term[lambda captures]{id=lambda-capture} the copy, and the job calls its `Save`.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L292-L296"
if (!m_Project)
	return;
// The snapshot: a copy of the project's small in-memory values, serialized and written on the writer's job.
Ref<const Project> snapshot = CreateRef<Project>(*m_Project);
m_ProjectFileWriter->Submit([snapshot](std::string* outError) { return snapshot->Save(outError); });
```

A failed write sets the state to Unwritten and keeps the error. The newest values stay in memory, the next submit tries again,
and the guard of the previous section refuses to discard them without `force`.

`ProjectSettingsAction` makes a settings change an :term[undo step]{id=undo-step}. Its `Execute` and `Undo` set the project's values and queue
a write of the project file in the background. Its `ChangesScene` returns false, so the edited scene stays saved when
only a setting changed. The projects' settings sections themselves belong to
[Project settings](../world/projects-settings.md).

The design has a limit at the pin. Prefab, material and animation controller documents are still written in the frame. `prefab.apply` calls
`AssetEdit::ApplyDocument` at `StrataEditor/src/Editor/EditorPrefabCommands.cpp` line 570, and that :term[function calls]{id=function-call}
`EditorAssetManager::SaveNativeAsset` on the main thread (`StrataEditor/src/Editor/AssetEdit.cpp` line 95). These documents are small compared with a
world scene, and the frame still pays for each write. Saves of a scene, a world's through `scene.save` too, are the ones that use `DocumentSaver`.

## The real code: the guard

`CheckUnsavedChanges` is the guard. Notice the order of its checks: `force` first, then the settings, then the scene.

```cpp src="StrataEditor/src/Editor/CommandUtils.cpp#L278-L319"
std::optional<EditorCommandResult> CheckUnsavedChanges(const EditorContext& context, bool force, std::string_view action, DiscardScope scope)
{
	if (force)
		return std::nullopt;
	// Both are named when both are at stake, so that one answer covers what force would discard.
	std::string settings;
	if (scope != DiscardScope::Scene && context.HasUnwrittenProjectSettings())
	{
		settings = fmt::format("The project file '{}' could not be written ({}): the project's settings changed since are only in the "
			"editor, and {} would discard them. Write it with project.save once the cause is fixed, or pass force: true to discard them",
			FileSystem::ToUTF8(context.GetProject()->GetProjectFile()), context.GetProjectFileError(), action);
	}
	if (scope == DiscardScope::Editor && context.HasUnwrittenPreferences())
	{
		const EditorPreferences& preferences = context.GetPreferences();
		settings += fmt::format("{}The preferences file '{}' could not be written ({}): the preferences changed since are only in the "
			"editor, and {} would discard them. Write it with preferences.save once the cause is fixed, or pass force: true to discard them",
			settings.empty() ? "" : ". ", FileSystem::ToUTF8(preferences.GetFile()), preferences.GetFileError(), action);
	}
	if (!context.IsSceneModified())
	{
		if (settings.empty())
			return std::nullopt;
		return EditorCommandResult::Fail(std::move(settings));
	}
	const std::string& scene = context.GetEditScene()->GetName();
	std::string message;
	if (!context.HasProject())
	{
		message = fmt::format("The scene '{}' has unsaved changes, which {} would discard; without a project they cannot be saved: pass "
			"force: true to discard them", scene, action);
	}
	else
	{
		const char* save = context.GetSceneHandle().IsValid() ? "scene.save" : "scene.saveAs, as the scene was never saved";
		message = fmt::format("The scene '{}' has unsaved changes, which {} would discard: save them first ({}) or pass force: true to "
			"discard them (they are kept as recovery data, scene.recoveryStatus)", scene, action, save);
	}
	if (!settings.empty())
		message += ". " + settings;
	return EditorCommandResult::Fail(std::move(message));
}
```

1. **Line 280:** `force` ends the check at once; the discarded changes go to recovery elsewhere.
2. **Line 284:** project settings count only for `Project` and `Editor` scopes.
3. **Line 290:** preferences count only for the `Editor` scope.
4. **Line 297:** a scene without changes and with settled settings passes; with unwritten settings it fails naming them.
5. **Line 312:** the advice names the command that fixes it: `scene.save`, or `scene.saveAs` when the scene was never saved.

`AfterSaves` is a function that takes a handler and returns a handler. Look at the two moments it checks `HasSavesInFlight`.

```cpp src="StrataEditor/src/Editor/CommandUtils.cpp#L321-L334"
EditorCommandHandler AfterSaves(EditorCommandHandler handler)
{
	return [handler = std::move(handler)](EditorContext& context, const nlohmann::json& parameters) -> EditorCommandResult
	{
		if (!context.HasSavesInFlight())
			return handler(context, parameters);
		return EditorCommandResult::Defer([handler, parameters = nlohmann::json(parameters)](EditorContext& context) -> std::optional<EditorCommandResult>
		{
			if (context.HasSavesInFlight())
				return std::nullopt;
			return handler(context, parameters);
		});
	};
}
```

1. **Line 325:** nothing in flight, so the handler runs at once and the command is as fast as before.
2. **Line 327:** otherwise the command returns a deferred result that owns a copy of the parameters.
3. **Line 329:** while a save, a project file write or a preferences write is in flight, the poll says "not yet".
4. **Line 331:** the handler runs only then, so its guard sees the scene as the finished save left it.

`scene.new` shows the three pieces together in one real command.

```cpp src="StrataEditor/src/Editor/EditorSceneCommands.cpp#L379-L406"
registry.Register(MayDefer({ "scene.new",
	"Replaces the edited scene with a new, unsaved one: empty by default, or with a template's content, e.g. \"basic3d\" (a lit start: camera, "
	"sun, procedural sky, ground, post-processing; the editor camera then looks through the scene's camera; the ground's material "
	"Materials/Ground.stmat is added to a project that lacks it). Fails while the edited scene has unsaved changes unless force is true (save "
	"first). Save the new scene with scene.saveAs. Waits for saves in flight (scene.save) first. Returns discardedChanges (whether unsaved "
	"changes were discarded).",
	ObjectSchema({
		{ "name", StringSchema("Scene name") },
		{ "template", { { "type", "string" }, { "enum", { ProjectTemplates::c_Empty, ProjectTemplates::c_Basic3D } },
			{ "description", "What the scene starts with (default \"empty\"; see project.templates)" } } },
		{ "force", ForceSchema() } }),
	AfterSaves([](EditorContext& context, const nlohmann::json& parameters)
	{
		CommandArguments arguments(parameters);
		const std::string name = arguments.GetString("name", "Untitled");
		const std::string templateId = arguments.GetString("template", std::string(ProjectTemplates::c_Empty));
		const bool force = arguments.GetBool("force", false);
		if (arguments.IsValid() && !ProjectTemplates::Find(templateId))
			arguments.SetError(fmt::format("Unknown template '{}' (templates: {})", templateId, ProjectTemplates::ListIds()));
		if (!arguments.IsValid())
			return arguments.Fail();
		if (std::optional<EditorCommandResult> refused = CheckUnsavedChanges(context, force, "starting a new scene", DiscardScope::Scene))
			return std::move(*refused);
		const bool discarded = context.IsSceneModified();
		if (!context.NewScene(name, templateId))
			return EditorCommandResult::Fail(fmt::format("The template '{}' could not be applied", templateId));
		return EditorCommandResult::Ok({ { "discardedChanges", discarded } });
	}) }));
```

1. **Line 379:** `MayDefer` tells the registry that the command can return a pending result.
2. **Line 390:** the whole handler sits inside `AfterSaves`.
3. **Line 400:** the guard comes before any change, so a refusal changes nothing.
4. **Line 402:** whether changes are discarded is read before the scene is replaced, to be reported afterwards.
5. **Line 403:** only now does the scene change.

When the guard passes, the replacement goes through `ResetScene`, whichever command asked. Look at its order: the recovery
journal is written before anything is let go.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L690-L716"
Stop();
// Discarded changes name where the scene is now, also when it moved in this frame.
FollowSceneMoves();
// Unsaved changes of the scene that goes are written as recovery data first, so nothing is lost whatever replaced
// it (a forced command, the unsaved-changes dialog's Don't Save, closing the editor).
std::string lostReason;
const DiscardOutcome discarded = m_Recovery->EndScene(*m_EditScene, IsSceneModified(), &lostReason);
if (discarded != DiscardOutcome::Unmodified && notice != DiscardNotice::None)
	NotifyDiscardedChanges(m_EditScene->GetName(), discarded, lostReason, notice);
// The scene that goes keeps its view for when it opens again.
m_Viewport.StoreSceneCamera(m_SceneHandle);
m_PendingFrame.reset();
m_AnimationPreview.reset(); // Of the scene that goes, which it refers to: before the scene is released
m_World.reset();             // Likewise
Ref<Scene> previous = std::exchange(m_EditScene, std::move(scene));
AdoptProjectLayers(*m_EditScene, handle);
CreateAnimationPreview();
m_SceneHandle = handle;
ClearSelection();
m_UndoStack.Clear();
// A world's persistent scene streams its cells around the editor camera.
if (m_AssetManager)
	m_World = EditorWorld::Attach(*m_AssetManager, *m_EditScene, m_UndoStack);
// The scene that goes is destroyed off the frame (a million entities take tens of milliseconds).
Scene::ReleaseInBackground(std::move(previous));
const auto [sceneFile, scenePath] = GetSceneFile(handle);
m_Recovery->BeginScene(*m_EditScene, handle, sceneFile, scenePath);
```

1. **Line 690:** play stops first, since the running copy refers to the scene that is about to go.
2. **Line 696:** changes that are not saved are written as recovery data before the scene is replaced, whatever caused the replacement.
3. **Line 698:** the person is told what was discarded, unless the caller asked for no notice.
4. **Line 709:** the history is cleared, which also starts a new generation, so a late save point marks nothing.
5. **Line 714:** the old scene is destroyed off the frame, since a million entities take tens of milliseconds.

`ReleaseProject` goes further, and it blocks. It finishes every save and the project file write.
It cancels the export, the loads and a migration, stores the viewport state and resets the scene, which writes the journal.
Last it closes scripts, thumbnails and the asset manager. Through commands and the interface the project closes only after saves
ended, so the blocking happens only when the editor itself goes away.

## A worked example: a large save and a refused open

:::example[A large save and a refused open]
An agent drives the editor over its command interface. The project holds a scene of about a million entities, and
the agent changes one entity, then runs these commands.

1. `scene.save` with `{"wait": false}`. The frame takes a snapshot and answers at once: `saveId` 7, state Writing. The
   history holds 12 actions, so the save point is position 12.
2. The agent moves another entity (action 13) and polls `editor.status`. Its `saving` section lists `saveId` 7 with a growing
   `progress`. The status bar of the editor window shows the save too.
3. The agent runs `scene.open` for another scene, without `force`. `AfterSaves` sees a save in flight and defers the command, which
   answers as pending.
4. The job ends. The next `Update` publishes the document and runs `OnSceneSaveEnded`, which marks position 12 saved.
   The history holds 13 actions, so the scene is modified: action 13 is not on disk.
5. The deferred poll runs the handler. `CheckUnsavedChanges` finds the modified scene and fails: the scene has changes that are not saved,
   save them first with `scene.save` or pass `force`.

The file holds the scene as step 1 found it, the second move is still in the editor, and nothing was lost. Had the agent
passed `force`, the handler would still wait for the save, then discard action 13, and `ResetScene` would write it to the
recovery data first.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Save on the main thread | Simple tools, and Strata 0.3.0 | No copy and no second thread | A freeze that grows with the scene: 22 s at a million entities |
| Lock the scene as read-only during the save | Tools with a progress dialog | No second copy of the scene in memory | The person cannot edit while saving |
| Copy the whole process with the operating system (fork) | Database servers on systems that have it | No copying code of our own | Windows has no fork, and the copy includes the whole editor |
| Keep a log of edits and replay it | Databases, and editors with an automatic log | A save that writes only what changed | The file is no plain document; loading must replay the log |

The copy-and-write choice costs memory for the second copy of the scene while a save runs, and time in the frame for the
copy. In return a save of any size leaves the frame almost free and lets the person edit meanwhile, which is the gain
the release notes of 0.4.0 describe.

## How it is tested

Three suites carry the behavior. Run any of them with the build's test program, for example
`build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Saves`, or all of them with `ctest --preset windows-debug`.

- `Editor.Saves` (`StrataTests/src/Editor/DocumentSaveTests.cpp`) covers the save queue. Its cases include several documents in one request and an item
  that fails while the others are written. Others check queued and replaced saves and the :term[file watcher]{id=file-watcher} leaving the document alone.
  Further cases check a frame that converts nothing to bytes, edits during a save, and commands that wait for a save in flight.
- `Editor.UI.Saves` (the same file) covers the status bar, the saving dialog while a save runs and the notification of a failed save.
- `Editor.DataSafety` (`StrataTests/src/Editor/DataSafetyTests.cpp`) covers the guard: replacing commands refuse without
  `force`, the guard holds while a copy plays, and failed project file or preferences writes are asked about.

The tests hold a save in flight with `GatedJobSystem` and `BackgroundGate` (`StrataTests/src/Editor/SaveTestUtils.h`): a job
occupies the single background worker, so the save's job waits behind it until the test opens the gate. No test waits for
frames or sleeps for a guessed time. A perf test measures the save of a world in a helper process and reports the frames
that ran meanwhile.

## Changing it safely

To save a new kind of document, build a `DocumentSaveRequest` with a snapshot and one `DocumentSaveItem` per document, and
submit it to `DocumentSaver`. Reserve new paths first with `ReserveNativeAsset`. To write a new small settings file, give a
`SettingsFileWriter` a function that owns a copy of the values. To add a command that replaces the scene, copy `scene.new`:
the guard, `AfterSaves` and `MayDefer`, with the scope that matches what the command lets go of.

The rules in `AGENTS.md` that apply, and the reason for each:

- Saves never convert a document to bytes on the main thread, because the freeze is the bug this design removed.
- The save point is taken after `BreakMerge`, because a merged drag would otherwise leave no state of the history that matches the file.
- A command that throws away the scene, the project or the editor uses `CheckUnsavedChanges`, `AfterSaves` and `MayDefer` together,
  because each piece covers a loss the others cannot.
- A step that changes files first checks that they still fit, and fails with the reason instead of replacing what the editor did not write.

Pass the three suites above before a commit. A new command that replaces the scene gets a case in `Editor.DataSafety` that
refuses without `force`, and a case in `Editor.Saves` that runs it while a save is held.

## Summary

- A save takes a snapshot in the frame, writes it on a background job and publishes the result on the main thread, so no frame waits for the disk.
- A save point names a state of the undo history, so edits made during a save stay not saved and a merged drag is cut first.
- The atomic write keeps the old file after a crash, the document claim keeps the watcher and moves away, and the publish updates the asset on the main thread.
- A queued save of the same documents is replaced by the newer one, and every request is told when that one write ends.
- A command that replaces the scene checks `CheckUnsavedChanges`, waits through `AfterSaves` and is registered with `MayDefer`.

## Check yourself

1. Which work does the frame that starts a scene save do?

   - A. It converts the scene to bytes and writes the file, and the job only renames it.
   - B. It breaks merging, takes the save point and copies the scene; the job does the rest.
   - C. It marks the scene saved at once and the job repairs the mark if the write fails.

   :::answer{tests="snapshot-job"}
   B. Answer A is wrong because converting in the frame is the 0.3.0 freeze. Answer C is wrong because a mark before the
   write would claim a file that does not exist yet, and a crash would then lose the edits silently.
   :::

2. The history holds actions with serials 1 to 5. A save starts and takes the point at serial 5. You make edit 6, the save
   ends, and then you undo edit 6. Is the scene modified after the save ended, and after the undo?

   :::answer{tests="save-point"}
   Modified after the save ended, because 6 applied actions differ from the saved position 5; clean after the undo, because
   the position is 5 again. Marking everything saved at the end would have shown clean at the wrong time.
   :::

3. A save writes `Level.stscene`. Meanwhile the file watcher sees the temporary file replace the target. Why does the
   editor not reload the scene, and what would go wrong without that protection?

   :::answer{tests="claim-publish"}
   The save holds a claim on the path, so the watcher leaves it alone. Without the claim the watcher would report an outside
   change, search the file again and reload a document the editor itself wrote a moment ago.
   :::

4. A save R1 is writing. You press save three more times, creating R2, R3 and R4 while R1 writes. How many snapshots does
   the editor hold, how many writes follow R1, and who is told when they end?

   :::answer{tests="coalescing"}
   One waiting snapshot, the one of R4, because R3 and R2 were replaced while they waited. One write follows R1, and the
   completions of R2, R3 and R4 all run, each with the status of that one write.
   :::

5. You add a new command that reloads the scene from disk. Which three pieces does it need, and which one stops
   a forced run from discarding a save in flight?

   :::answer{tests="guard"}
   The command needs `CheckUnsavedChanges` with the `Scene` scope, `AfterSaves` around its handler and registration through `MayDefer`.
   `AfterSaves` makes a forced run wait for the save; `force` only waives the check about edits that are not saved.
   :::

## Exercises

1. **Basic.** A scene save freezes the editor for 22 s. How many frames at 60 frames per second does the person lose, and
   what share of them does a background save lose when the frame only copies for 20 ms?

   :::answer[Worked solution]{tests="snapshot-job"}
   22 s × 60 frames per second = 1,320 frames. The copy of 20 ms costs about 1 frame of 16.7 ms plus a little, so
   about 2 frames at most, which is 0.15 % of 1,320. The rest of the time the person keeps working.
   :::

2. **Medium.** Extend the toy: write a queue where one request writes, at most one waits, and a newer request replaces the
   waiting one. Submit snapshots 10, 11, 12 and 13, and print what each write covers.

   :::answer[Worked solution]{tests="coalescing" solution="sketches/editor-saving-coalesce.cpp"}
   The sketch keeps `m_Running` and `m_Waiting`. A submit with nothing running starts at once; a submit with a waiting
   request replaces its snapshot and adds its id; a finish moves the waiting request up. Snapshot 10 writes alone,
   then one write of snapshot 13 answers requests 2, 3 and 4.

   ```cpp sketch="editor-saving-coalesce.cpp"
   // A toy save queue: one request writes, at most one waits, and a newer request replaces the waiting one.
   #include <iostream>
   #include <optional>
   #include <utility>
   #include <vector>

   struct Request
   {
   	int Snapshot = 0;                // Which state of the scene the request holds
   	std::vector<int> CompletionIds;  // Everyone who is told when it is written
   };

   class Queue
   {
   public:
   	int Submit(int snapshot)
   	{
   		const int id = m_NextId++;
   		if (!m_Running)
   		{
   			m_Running = Request{ snapshot, { id } };
   			return id;
   		}
   		if (m_Waiting)
   		{
   			// The waiting request never started: the newer snapshot is written for both.
   			m_Waiting->Snapshot = snapshot;
   			m_Waiting->CompletionIds.push_back(id);
   			return id;
   		}
   		m_Waiting = Request{ snapshot, { id } };
   		return id;
   	}

   	void Finish()
   	{
   		std::cout << "wrote snapshot " << m_Running->Snapshot << " for requests";
   		for (const int id : m_Running->CompletionIds)
   			std::cout << " " << id;
   		std::cout << "\n";
   		m_Running = std::move(m_Waiting);
   		m_Waiting.reset();
   	}

   	bool IsBusy() const { return m_Running.has_value(); }
   private:
   	std::optional<Request> m_Running;
   	std::optional<Request> m_Waiting;
   	int m_NextId = 1;
   };

   int main()
   {
   	Queue queue;
   	queue.Submit(10); // Starts writing at once
   	queue.Submit(11); // Waits
   	queue.Submit(12); // Replaces 11's snapshot
   	queue.Submit(13); // Replaces 12's snapshot
   	while (queue.IsBusy())
   		queue.Finish();
   	return 0;
   }
   ```

   ```text output-of="editor-saving-coalesce.cpp"
   wrote snapshot 10 for requests 1
   wrote snapshot 13 for requests 2 3 4
   ```

   1. **Lines 26–28:** a waiting request keeps its place, takes the newer snapshot and adds the new id.
   2. **Line 41:** when the write ends, the waiting request moves up to run.
   3. **Lines 55–58:** four submits, of which only the first and the last snapshot are ever written.
   :::

3. **Hard.** Trace it yourself: find which test holds a background save in flight while `scene.new` runs, and what the
   test checks. Then remove `AfterSaves` from `scene.new` on a scratch branch and say which check fails and why.

   :::answer[Worked solution]{tests="guard"}
   Search the tests for `scene.new` next to `BackgroundGate`: the case in `Editor.Saves` (`StrataTests/src/Editor/DocumentSaveTests.cpp`).
   It holds the save with the gate, runs `scene.new` and requires the result to be pending and the scene's name to stay
   "Main". Without `AfterSaves` the command runs at once, so the pending check fails. Run the suite on the scratch
   branch to confirm; the cases of `Editor.DataSafety` stay green because no save is in flight there.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/DocumentSaver.h` and `DocumentSaver.cpp`: `DocumentSaver`, `DocumentSaveRequest`, `DocumentSaveStatus`.
- `StrataEditor/src/Editor/SettingsFileWriter.cpp` and `ProjectSettingsAction.h`: settings writes and their undo steps.
- `StrataEditor/src/Editor/EditorContext.cpp`: `SubmitSceneSave`, `OnSceneSaveEnded`, `ResetScene`, `ReleaseProject`, `HasSavesInFlight`.
- `StrataEditor/src/Editor/CommandUtils.cpp`: `CheckUnsavedChanges`, `AfterSaves`, `DiscardScope`.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp`: `ClaimDocumentWrite`, `DocumentWriteClaim::Commit`, `PublishWrittenDocument`.
- Commands: `scene.save`, `scene.saveAs`, `scene.new`, `scene.open`, `editor.status`. Tests: `Editor.Saves`, `Editor.UI.Saves`, `Editor.DataSafety`.

## Further reading

- The release notes of Strata 0.4.0 ("Background saves and large projects"): what changed for users; beginner.
- The Redis persistence documentation: how a database copies a process to write a snapshot; intermediate.
- "Designing Data-Intensive Applications" by Martin Kleppmann, the chapters on storage and logs: why logs and snapshots trade off; advanced.
