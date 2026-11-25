---
id: editor/trash-references
title: "The trash and references"
description: "How the editor keeps project files in its history: deletes go to a trash after a check of users, handles survive, and each undo step re-checks its path."
kind: internals
size: M
tracks: [E]
needs: [editor/undo, assets/references]
time: 50
learn:
  - id: files-in-history
    text: explain why a delete moves a file to the trash and checks its users before it touches anything
  - id: three-sources
    text: name the three sources that AssetReferences::Find joins and say why the open scene is read from memory
  - id: step-checks
    text: predict whether the undo or redo of a file step runs or fails when another asset sits at its path
  - id: new-operation
    text: choose what an undoable file operation must record and check so that it never writes over a file
since: 0.3.0
status: final
---

A person deletes a material that three scenes use. A moment later they press **Ctrl+Z**, and they expect the material back, with every scene still pointing at it. This page is about what makes that work.

The **trash** is a folder of the project where deleted files wait before they are removed for good. The page covers it, the steps that move, delete and create project files, and the check that asks who uses an asset first. It does not cover how references are recorded ([references and closures](../assets/references.md)), what a handle is ([handles and `.meta` files](../assets/handles-meta.md)), how a save writes a document ([saving](../editor/saving.md)) or how the delete dialog is drawn.

## The problem and how engines solve it

Scene edits are simple to undo, because the scene lives in memory: an :term[undo step]{id=undo-step} copies the old value back. Files are harder. A file on disk can be deleted, replaced or renamed by a file manager, by :term[version control]{id=version-control} or by another program, and none of that passes through the editor's history. A step that remembers "I deleted `Materials/Red.stmat`" cannot assume that the path is still free when the person presses undo.

The simplest answer is to call `std::filesystem::remove` and accept that a delete cannot be undone. Another answer deletes the file after a confirmation dialog, but still never asks who uses it, so a scene silently loses its material.

Strata changes four things instead. Deletes move files to a trash and keep them for 30 days. Users are checked first, including uses that exist only in memory. Handles survive the trip. Every undo step checks that its path still holds what it recorded, and fails if it does not.

## The map

Everything starts in a command. A panel never touches a file: it calls `asset.delete` or `asset.move`, as an agent would. The command asks `AssetReferences::Find` who uses the asset, asks the :term[asset manager]{id=asset-manager} to do the file work, and records one step in the :term[undo stack]{id=undo-stack}.

```mermaid caption="A delete asks the reference check first, then the asset manager moves the files, and the step is recorded. Undo and redo later call the same asset manager again." alt="A flow from a command through the reference check and the asset manager to the undo stack, with undo and redo returning to the asset manager."
flowchart LR
  C[asset.delete command] --> R[AssetReferences::Find]
  R -->|users found, no force| F[Refuse, list referencedBy]
  R -->|free or forced| M[EditorAssetManager::MoveToTrash]
  M --> S[AssetTrashAction recorded]
  S -->|Undo| RS[RestoreFromTrash]
  S -->|Redo| CR[CheckRedo, then MoveToTrash]
```

Four classes of `StrataEditor/src/Editor/AssetFileAction.h` form the step family. `AssetTrashAction` records a delete of a file or a folder. `AssetMoveAction` records a move or rename. `AssetCreateAction` records an asset the editor made, such as a prefab built from entities. `AssetFolderCreateAction` records a new folder.

The reference check lives in `StrataEditor/src/Editor/AssetReferences.cpp`. The file work lives in `Strata/src/Strata/Asset/EditorAssetManager.cpp`. The steps run on the :term[main thread]{id=main-thread}.

## The contract

A **referencer** is anything that names an asset: another asset whose recorded references include it, the open scene, or the project itself. The rules for steps that touch files follow.

- A file step never changes the scene. `ChangesScene()` returns `false`, so a delete or a move never marks the scene as changed since its last save. The undo page explains why that flag matters.
- A step holds the asset manager weakly (a `std::weak_ptr`, see [memory in C++](../basics/cpp-memory.md)). When the project closes, the history is cleared, and a step that still runs reports "the project this step belongs to is closed" instead of touching a dead object.
- A delete refuses while any referencer exists, unless the caller passes `force`. The refusal carries the list in the error's data under `referencedBy`.
- Undo restores the files with the same handle, and fails when something else is at the path now.
- Redo runs only when the path still holds exactly the assets that were deleted, and the delete would be allowed today.
- The open scene can never be deleted, and neither can a folder that holds it.
- Moves, folder moves and trashing refuse a file that a background save is writing, with the message that it is being saved.
- A delete made by an agent or a script is announced to the person in a message; the person's own delete is not.

:::rule
**Panels never write, move or remove files.** A file changed behind the history breaks undo, the trash and the references. The test `Panels change files only through commands` in the suite `Editor.UI.Source` scans the panels' source and fails any panel that writes, moves or removes a file itself. The undo page shows what the history needs from the files: [undo and redo](../editor/undo.md).
:::

## A toy version

:::question
This sketch uses classes, a map and a vector. If those are new, read [programming 3](../basics/programming-3.md) and [generic C++](../basics/cpp-generic.md) first.
:::

The sketch below keeps a few files with handles, a list of users per handle and a trash. It has the same four behaviours as the editor: a refusal that names the user, a delete that keeps the handle, an undo that restores, and a check of the path before the undo acts. It omits folders, `.meta` files and cached imports.

```cpp sketch="editor-trash-references-toy.cpp"
#include <iostream>
#include <map>
#include <string>
#include <vector>

// A toy project: files with handles, who uses each handle, and a trash. It follows the page's rules:
// a delete asks the users first, a trashed file keeps its handle, and an undo checks the path.
struct Trashed
{
	std::string Path;
	int Handle = 0;
};

class Project
{
public:
	void Create(const std::string& path, int handle) { m_Files[path] = handle; }
	void Use(int handle, const std::string& user) { m_Users[handle].push_back(user); }

	bool Delete(const std::string& path, bool force, Trashed& outTrashed, std::string& outError)
	{
		const auto file = m_Files.find(path);
		if (file == m_Files.end())
		{
			outError = "no such file";
			return false;
		}
		const std::vector<std::string>& users = m_Users[file->second];
		if (!users.empty() && !force)
		{
			outError = "'" + path + "' is used by " + users.front();
			return false;
		}
		outTrashed = { path, file->second };
		m_Files.erase(file); // The real engine moves the file to the trash folder instead
		return true;
	}

	bool Restore(const Trashed& trashed, std::string& outError)
	{
		if (m_Files.contains(trashed.Path))
		{
			outError = "Something else is at '" + trashed.Path + "'";
			return false;
		}
		m_Files[trashed.Path] = trashed.Handle; // The same handle comes back
		return true;
	}

	int Find(const std::string& path) const
	{
		const auto file = m_Files.find(path);
		return file == m_Files.end() ? 0 : file->second;
	}
private:
	std::map<std::string, int> m_Files;
	std::map<int, std::vector<std::string>> m_Users;
};

int main()
{
	Project project;
	project.Create("Materials/Stone.stmat", 1);
	project.Create("Textures/Rust.png", 2);
	project.Use(1, "Scenes/Main.stscene");

	Trashed trashed;
	std::string error;
	if (!project.Delete("Materials/Stone.stmat", false, trashed, error))
		std::cout << "refused: " << error << "\n";

	if (project.Delete("Textures/Rust.png", false, trashed, error))
		std::cout << "deleted Rust, handle " << trashed.Handle << "\n";
	if (project.Restore(trashed, error))
		std::cout << "undo: Rust is back with handle " << project.Find("Textures/Rust.png") << "\n";

	project.Delete("Textures/Rust.png", false, trashed, error);
	project.Create("Textures/Rust.png", 3); // A new file takes the path
	if (!project.Restore(trashed, error))
		std::cout << "undo failed: " << error << "\n";
	return 0;
}
```

```text output-of="editor-trash-references-toy.cpp"
refused: 'Materials/Stone.stmat' is used by Scenes/Main.stscene
deleted Rust, handle 2
undo: Rust is back with handle 2
undo failed: Something else is at 'Textures/Rust.png'
```

1. **Lines 28–33:** the delete asks for the users first, and without `force` it refuses and names one of them.
2. **Line 35:** the file leaves the project, and the record in `trashed` keeps the path and the handle.
3. **Lines 41–45:** an undo checks that nothing sits at the path before it acts.
4. **Line 46:** the restore writes the old handle back, so references that named it work again.

Each line of output answers one rule. The material is refused because the scene uses it. The texture goes away and comes back with handle 2, the same number as before. The last undo fails: a new file with handle 3 took the path, and restoring the old one would replace it. The real editor does exactly that, with real files and a few more cases.

## The real code

### The check: three sources

`AssetReferences::Find` answers one question: who uses these targets? It joins three sources. The first is the index of recorded referencers that the asset manager keeps (`EditorAssetManager::GetReferencers`), taught in [the editor's index of referencers](../assets/references.md#the-editors-index-of-referencers). Each result becomes an `AssetReferencer`, sorted by path. Targets include the :term[sub-assets]{id=sub-asset} of a file, so deleting a model checks its meshes and materials too.

```cpp src="StrataEditor/src/Editor/AssetReferences.cpp#L164-L189" from="std::vector<AssetReferencer> referencers;" to="referencers.push_back(std::move(entry));" symbol="AssetReferences::Find"
std::vector<AssetReferencer> referencers;
const EditorAssetManager* assets = context.GetAssetManager();
if (!assets)
	return referencers;

// The assets whose recorded references name a target, each once.
std::unordered_map<AssetHandle, size_t> listed;
for (AssetHandle target : targets)
{
	for (AssetHandle referencer : assets->GetReferencers(target))
	{
		if (ignored.contains(referencer) || listed.contains(referencer))
			continue;
		const std::optional<AssetMetadata> metadata = assets->GetMetadata(referencer);
		if (!metadata)
			continue;
		// Sub-assets that reference (a model's mesh using a material) stand for their file, unless it goes too.
		if (metadata->IsSubAsset() && ignored.contains(metadata->Parent))
			continue;
		AssetReferencer entry;
		entry.Asset = referencer;
		entry.Type = metadata->Type;
		entry.Path = metadata->Path;
		entry.Name = metadata->IsSubAsset() ? metadata->SubAssetKey : std::string();
		listed.emplace(referencer, referencers.size());
		referencers.push_back(std::move(entry));
```

1. **Lines 171–176:** each target asks the index for its referencers; a result already listed, or one that goes with the targets, is skipped.
2. **Lines 180–182:** a sub-asset that references a target stands for its file, unless the file is deleted too.
3. **Lines 183–189:** each result becomes an `AssetReferencer` with the referencing handle, its kind of file, its path and its sub-asset name.

The second source is the open scene, read from memory. A scene file on disk records its references only when it is saved, so an entity that got a new material a minute ago is invisible to the index. `FindInScene` walks every registered component and every script field that holds an asset, and lists at most 1,000 uses. If the scene file is already in the list, the walk adds the entities to that entry and marks it `OpenScene`. If the scene is not in the list, because it was never saved or its file does not mention the target, a new entry goes first.

```cpp src="StrataEditor/src/Editor/AssetReferences.cpp#L198-L223" from="const std::unordered_set<AssetHandle> wanted(targets.begin(), targets.end());" to="referencers.insert(referencers.begin(), std::move(*project));" symbol="AssetReferences::Find"
const std::unordered_set<AssetHandle> wanted(targets.begin(), targets.end());
std::vector<SceneEntityReference> entities = FindInScene(*context.GetEditScene(), wanted);
const AssetHandle scene = context.GetSceneHandle();
auto open = std::find_if(referencers.begin(), referencers.end(), [scene](const AssetReferencer& entry)
{
	return scene.IsValid() && entry.Asset == scene;
});
if (open != referencers.end())
{
	open->OpenScene = true;
	open->Entities = std::move(entities);
}
else if (!entities.empty() && !(scene.IsValid() && ignored.contains(scene)))
{
	AssetReferencer entry;
	entry.Asset = scene;
	entry.Type = AssetType::Scene;
	if (const std::optional<AssetMetadata> metadata = scene.IsValid() ? assets->GetMetadata(scene) : std::nullopt)
		entry.Path = metadata->Path;
	entry.OpenScene = true;
	entry.Entities = std::move(entities);
	referencers.insert(referencers.begin(), std::move(entry));
}

if (std::optional<AssetReferencer> project = FindProjectReferencer(context, wanted))
	referencers.insert(referencers.begin(), std::move(*project));
```

1. **Line 199:** the walk reads the entities now in memory, not the scene file.
2. **Lines 201–209:** when the scene file is already listed, the entry is marked as the open scene and gets the entities.
3. **Lines 210–220:** when it is not (never saved, or its file does not show the use), a new entry goes first.
4. **Lines 222–223:** the project entry, when it names a target, goes in front of all.

The third source is the project file: the scene it starts with, the scene shown while loading, the game icon, and each settings section whose values name a target. That entry goes in front of all others. `ToJson` writes the list for `referencedBy`. `Describe` writes the sentence for the error: at most four users, three entity names for the open scene, and then a count such as "and 3 more".

### The delete and its step

`asset.delete` first resolves the asset and refuses the open scene. Then it asks for the referencers, refuses if there are any and `force` is not set, and only then moves the files. The step is recorded after the move succeeded, so a failed move leaves no step behind.

```cpp src="StrataEditor/src/Editor/EditorAssetCommands.cpp#L954-L969"
const std::string path = assets->GetMetadata(handle)->Path;
const std::vector<AssetHandle> targets = AssetReferences::WithSubAssets(context, { handle });
const std::vector<AssetReferencer> referencers = AssetReferences::Find(context, targets, { targets.begin(), targets.end() });
if (!referencers.empty() && !force)
{
	return EditorCommandResult::Fail(fmt::format("'{}' is used by {}; delete it with force: true to leave those references missing, or "
		"change them first (asset.findReferences lists them)", path, AssetReferences::Describe(referencers)),
		{ { "referencedBy", AssetReferences::ToJson(referencers) } });
}
TrashedAssets trashed;
if (!assets->MoveToTrash(path, trashed, &error))
	return EditorCommandResult::Fail(error);
context.GetUndoStack().Record(CreateScope<AssetTrashAction>(context, *assets, fmt::format("Delete {}", path), trashed, force));
context.NotifyAssetsTrashed(path, false, trashed.Handles.size(), !referencers.empty());
return EditorCommandResult::Ok({ { "asset", UUIDToJson(handle) }, { "path", path }, { "trash", FileSystem::ToUTF8(trashed.Entry) },
	{ "referencedBy", AssetReferences::ToJson(referencers) } });
```

1. **Lines 957–961:** the refusal carries a sentence for people and the full list in the error's data.
2. **Lines 963–965:** the files move before anything is recorded, so a failed move leaves no step.
3. **Line 966:** the step keeps `force`, so a redo knows whether users may exist.
4. **Line 967:** the announcement is made after the work, and only agents and scripts trigger it.

`MoveToTrash` moves the file, its `.meta` file and its cached import into a new folder of `<project>/.strata/Trash`, named by the time of the delete. A small file `Trashed.json` in that folder records what was moved, and the asset manager removes the assets from the project. Handles do not change, because a handle lives in the `.meta` file, and that file travels with the asset. An undo needs no import for the same reason: the cached import comes back with the file.

The trash is not kept forever. When a project opens, `PurgeTrash` runs on a low priority input and output job and removes trash folders whose `Trashed.json` is older than 30 days. The 30 is a constant of the editor, passed in when the project opens.

### The checks of undo and redo

Undo is short. `AssetTrashAction::Undo` calls `RestoreFromTrash`, which puts the files back and registers the assets with their handles, and fails, restoring nothing, when something else is at that place. Redo has more to check, because the world may have changed while the step was undone.

```cpp src="StrataEditor/src/Editor/AssetFileAction.cpp#L62-L92" symbol="AssetTrashAction::CheckRedo"
bool AssetTrashAction::CheckRedo(EditorAssetManager& assets, std::string* outError)
{
	// The path holds what was deleted there, and only that: whatever came there since is no part of this step.
	if (!m_Trashed.Folder)
	{
		if (m_Trashed.Handles.empty() || FindSourceAt(assets, m_Trashed.Path) != m_Trashed.Handles.front())
			return Fail(outError, fmt::format("'{}' is no longer the asset this step deleted", m_Trashed.Path));
	}
	else
	{
		const std::vector<AssetHandle> below = assets.GetAssetsBelowFolder(m_Trashed.Path);
		const std::unordered_set<AssetHandle> now(below.begin(), below.end());
		const std::unordered_set<AssetHandle> deleted(m_Trashed.Handles.begin(), m_Trashed.Handles.end());
		if (!assets.HasFolder(m_Trashed.Path) || now != deleted)
			return Fail(outError, fmt::format("The folder '{}' no longer holds what this step deleted", m_Trashed.Path));
	}
	// What asset.delete and asset.deleteFolder refuse, they refuse here too.
	const AssetHandle scene = m_Context.GetSceneHandle();
	if (scene.IsValid() && std::find(m_Trashed.Handles.begin(), m_Trashed.Handles.end(), scene) != m_Trashed.Handles.end())
		return Fail(outError, fmt::format("'{}' holds the open scene, which cannot be deleted; open another scene first", m_Trashed.Path));
	if (!m_Force)
	{
		const std::vector<AssetHandle> targets = AssetReferences::WithSubAssets(m_Context, m_Trashed.Handles);
		std::vector<AssetReferencer> referencers = AssetReferences::Find(m_Context, targets, { targets.begin(), targets.end() });
		if (m_OpenSceneFromMemory)
			AssetReferences::IgnoreSavedOpenScene(referencers);
		if (!referencers.empty())
			return Fail(outError, fmt::format("'{}' is used by {} now", m_Trashed.Path, AssetReferences::Describe(referencers)));
	}
	return true;
}
```

1. **Lines 65–69:** a file must still be the one at its path, found through its handle.
2. **Lines 70–76:** a folder must exist and hold exactly the assets it held.
3. **Lines 78–81:** the open scene may not be deleted, now or by a redo.
4. **Lines 82–90:** without `force` the users are searched again, because scenes may have changed meanwhile.

The first half asks whether the path still holds exactly what was deleted: for a file, the same handle at the path; for a folder, the same set of assets below it. The second half repeats what `asset.delete` refuses today: the open scene, and, unless the delete was forced, any referencer. The flag `m_OpenSceneFromMemory` exists for steps that replaced the scene's own use of a file and then trashed the file: it ignores a scene whose file names the target when no entity in memory does. A failed redo is not kept: the undo stack drops that step and every step after it, because the world no longer fits them.

`AssetCreateAction` shows the same idea from the other side. Its undo moves the asset to the trash only when the path still holds the asset it created. Otherwise it fails with "no longer the asset this step created", so that undoing never trashes someone else's file. `AssetMoveAction` needs no special code. `MoveAsset` already fails when another file is at the destination, which is what an undo of a move meets when a new file took the old path.

### Announcing agents' deletes

After the move, the command calls `EditorContext::NotifyAssetsTrashed`. The method finds who started the outermost running command in the journal. When the source is the interface or an internal call, it returns at once, because the person watched their own delete happen. Otherwise it posts a message, a warning when references were left missing. The message says that an agent or a command script deleted the asset, that it went to the trash, and that Undo restores it while this scene stays open.

:::example
Take a project with the open scene `Scenes/Main.stscene`, where the entity `Ground` uses the material `Materials/Stone.stmat`, and an unused texture `Textures/Rust.png`. The paths are an illustration, not a sample project.

1. Delete `Stone`. `Find` reads the scene from memory and finds `Ground`, so the command fails with a message that starts `'Materials/Stone.stmat' is used by Scenes/Main.stscene (open, used by Ground)`. The error's data holds `referencedBy` with one entry: `openScene` true and one entity. Nothing moved, and no step was recorded.
2. Delete `Rust.png`. No source names it, so it moves to a folder like `.strata/Trash/20261117-101500`. The history now ends with `Delete Textures/Rust.png`. Press **Ctrl+Z**: the file returns, with the same handle, and no import runs.
3. Move `Rust.png` to `Old/Rust.png`, then import another image under the old name `Textures/Rust.png`. The history ends with the move.
4. Press **Ctrl+Z**. The step moves `Old/Rust.png` back to `Textures/Rust.png`, but `MoveAsset` fails because a file is already there. The undo reports the error, and the step stays in the history. Move or remove the new file, and the same undo succeeds.

:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Delete the file at once, no undo | Many tools after a confirmation dialog | No trash folder and no purge job | A mistaken delete is lost for good |
| The :term[operating system's]{id=operating-system} recycle bin | File managers | Less code for the editor | No handle, `.meta` or cached import restored, and one behavior per platform |
| Delete without a reference check | Simple tools | One less walk of the scene | Scenes lose their materials and show broken references |
| Index only, without the open scene | Tools that read saved files | No walk of components | Uses not yet saved go unseen, so a delete breaks the scene that is on screen |
| Snapshot the whole project for undo | Version control based tools | Any change reverts exactly | Large copies and slow steps |

## How it is tested

The suite `Editor.AssetOperations` in `StrataTests/src/Editor/AssetCommandTests.cpp` runs the real commands against a temporary project. Its cases include `Deleting a material a scene uses fails listing the scene; with force it goes to the trash, and undo brings it back`, `An asset nothing uses is deleted without force; the open scene's unsaved uses count`, `Undoing a delete fails while another asset is at its path, and the step stays`, `Redoing a delete fails when the path holds other assets now, or the open scene`, `An imported texture comes back from the trash with its import, without importing it again` and `The trash folder of a project is cleaned of old entries when it opens`.

Run them with `build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.AssetOperations`. The panel rule lives in `Editor.UI.Source`. Every regression test of this area first fails without its fix: write the file change that the history did not see, then check that the step fails and stays.

## Changing it safely

To add an operation on files, make a step of the family and follow its rules. Record what the operation changed (the path, the handle, the folder flag), not what you expect to find later. Check in `Undo` and `Execute` that the path still holds what you recorded, and fail with a message when it does not. Never replace a file: the asset manager's moves and restores already refuse when something is at the destination, so call them and pass the error on. Add a command that records the step only after the file work succeeded, give it a description written for agents, and make a refusal return its data.

- Put a new source of users into `AssetReferences::Find`, so every delete, redo and the command `asset.findReferences` see it.
- Keep panels away from files: call a command instead, so that history and trash see the change.
- Hold the asset manager weakly in new steps, and say why the step does nothing once the project is closed.
- Extend the tests above with one case per check: the refusal, the undo that fails, the redo that fails.

## Summary

- A delete moves the file, its `.meta` and its cached import to the trash for 30 days, and refuses first when anything uses the asset.
- `AssetReferences::Find` joins the index of recorded referencers, the open scene read from memory, and the project's own references.
- Undo restores the same handle and fails when something else is at the path; redo runs only when the path holds exactly what was deleted and the delete would be allowed now.
- A new file operation records what it changed, checks the path in every direction and never writes over a file.

## Check yourself

1. A scene was never saved, and its entity `Lamp` uses a material you want to delete. Does the delete succeed?

   :::answer{tests="three-sources,files-in-history"}
   No. The index only knows saved documents, but `Find` also walks the open scene in memory and lists an entry for the open scene, with `Lamp`, even without a file path. Only `force` deletes it.
   :::

2. You delete `Textures/Rust.png`, and a colleague's version control then puts a different file there. What does **Ctrl+Z** do?
   - a) Writes the trashed file over the new file.
   - b) Fails with an error and keeps the step.
   - c) Restores the old file under a new name.

   :::answer{tests="step-checks"}
   Answer b. Restoring fails when something else is at the path, and the step stays so that the person can clear the path and undo again. Answer a would destroy a file that is outside the history, and the engine has no rule that renames files.
   :::

3. Why does a move need no `CheckRedo`, while a delete does?

   :::answer{tests="step-checks,new-operation"}
   `MoveAsset` already fails when the destination holds a file, and moving is safe whatever the references say. A delete depends on the world: its path, the open scene and the users may all have changed since.
   :::

4. An agent deletes a folder through a command. Does the person get a message?

   :::answer{tests="files-in-history"}
   Yes. The source of the outermost running command is an agent, not the interface, so `NotifyAssetsTrashed` posts a message with the folder, the count and the undo hint. The person's own delete from a panel posts nothing.
   :::

## Exercises

1. **Basic.** Extend the toy with a `CheckRedo` function: a redo runs only when the path still holds the handle that was trashed and no user is left unless forced. Print the result for two cases.

   :::answer[Worked solution]{tests="step-checks,new-operation" solution="sketches/editor-trash-references-redo.cpp"}
   The sketch keeps the same data in a smaller form. `CheckRedo` compares the handle at the path with the recorded one, then repeats the user check.

   ```cpp sketch="editor-trash-references-redo.cpp"
   #include <iostream>
   #include <map>
   #include <string>

   struct Trashed
   {
   	std::string Path;
   	int Handle = 0;
   	bool Force = false;
   };

   // A redo runs only while the path holds what the step deleted and nothing uses it (unless the delete was forced).
   bool CheckRedo(const std::map<std::string, int>& files, const std::map<int, int>& userCounts, const Trashed& trashed, std::string& outError)
   {
   	const auto file = files.find(trashed.Path);
   	if (file == files.end() || file->second != trashed.Handle)
   	{
   		outError = "'" + trashed.Path + "' is no longer the asset this step deleted";
   		return false;
   	}
   	const auto users = userCounts.find(trashed.Handle);
   	if (!trashed.Force && users != userCounts.end() && users->second > 0)
   	{
   		outError = "'" + trashed.Path + "' is used now";
   		return false;
   	}
   	return true;
   }

   int main()
   {
   	const Trashed trashed = { "Textures/Rust.png", 2, false };
   	std::string error;

   	std::map<std::string, int> files = { { "Textures/Rust.png", 2 } };
   	std::map<int, int> userCounts;
   	std::cout << "same file, no users: " << CheckRedo(files, userCounts, trashed, error) << "\n";

   	files["Textures/Rust.png"] = 3; // Another asset took the path
   	if (!CheckRedo(files, userCounts, trashed, error))
   		std::cout << "other file: " << error << "\n";
   	return 0;
   }
   ```

   ```text output-of="editor-trash-references-redo.cpp"
   same file, no users: 1
   other file: 'Textures/Rust.png' is no longer the asset this step deleted
   ```

   1. **Lines 15–20:** the handle at the path must be the recorded one.
   2. **Lines 21–26:** a forced delete may leave users; any other redo fails while one exists.
   :::

2. **Medium.** You add a command that copies a file to a new path, and a step for it. List what its step records, what its undo checks, and what it does on redo.

   :::answer[Worked solution]{tests="new-operation"}
   The step records the new path and the new handle. Undo moves the copy to the trash only if the path still holds that handle, like `AssetCreateAction`, and fails otherwise. Redo restores the trashed copy with its handle, and fails when something else is at the path.
   :::

3. **Hard.** Trace it yourself: run `asset.delete` on a material that the open scene uses, with a breakpoint in `AssetReferences::Find`. Which of the three sources named the user?

   :::answer[Worked solution]{tests="three-sources"}
   Open `StrataEditor/src/Editor/AssetReferences.cpp` and stop in `AssetReferences::Find`. If the scene is saved and its file records the material, the first loop lists the scene and the later walk only adds its entities. If the use is not saved yet, the loop finds nothing, `FindInScene` finds entities, and the branch that inserts a new entry runs. The command is in `StrataEditor/src/Editor/EditorAssetCommands.cpp`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/AssetFileAction.h` and `AssetFileAction.cpp`: the four step classes and `CheckRedo`.
- `StrataEditor/src/Editor/AssetReferences.h` and `AssetReferences.cpp`: `Find`, `FindInScene`, `ToJson` and `Describe`.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: `asset.delete`, `asset.deleteFolder`, `asset.move`, `asset.moveFolder`, `asset.findReferences`.
- `Strata/src/Strata/Asset/EditorAssetManager.cpp`: `MoveToTrash`, `RestoreFromTrash`, `PurgeTrash` and the save locks.
- `StrataEditor/src/Editor/EditorContext.cpp`: `NotifyAssetsTrashed`.
- Tests: `Editor.AssetOperations` and `Editor.UI.Source`.

## Further reading

- The Strata developer guide, section on asset files: the rules of this page in the engine's own words (advanced).
- The Freedesktop Trash specification: how desktop systems store deleted files (intermediate).
