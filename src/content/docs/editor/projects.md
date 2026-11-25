---
id: editor/projects
title: "Opening projects and scenes: templates, background loads and migration"
description: "How the editor creates, opens and closes projects and scenes without a stalled frame or a lost edit, and how a project from 0.5.0 is upgraded once."
kind: internals
size: L
tracks: [E]
needs: [editor/saving, world/projects-settings, world/sub-scenes]
time: 80
learn:
  - id: background-open
    text: explain why a scene opens in the background while the old one stays read-only, and where the swap happens
  - id: project-open-order
    text: trace what project.open does in order and name what the start scene waits for
  - id: migration
    text: explain how a project saved by 0.5.0 or older is migrated once and what the merge does with conflicts
  - id: templates-samples
    text: name the two templates and explain why a sample opens as a copy without local editor data
  - id: preferences
    text: name what the preferences file holds and what happens when a write of it fails
since: 0.3.0
status: final
---

When you open a project in the editor, or send `project.open` from a script, a person or an agent expects two things. The editor stays alive while the work runs, and nothing the person made is lost. This page follows a project from its creation to its close and a scene from the request to the frame that shows it. It covers the two templates, the samples, the list of recent projects, the upgrade of old projects and the file of the person's preferences. It does not cover the guard for changes not yet saved, the dialogs or the loader's inner states: those have pages of their own.

## The problem and how engines solve it

Think of a project with forty thousand assets and a start scene of one million entities. Reading all of it takes many seconds, and the editor draws a frame about every 16.7 ms. An open that blocks the :term[frame loop]{id=game-loop} for ten seconds skips about 600 frames. The window turns white, the :term[operating system]{id=operating-system} offers to close the program, and an automation client that sent the command times out.

The first answer is to load everything before the first frame. It is the simplest code, and it is what small tools do. The cost is the empty window: the person sees nothing, cannot cancel, and cannot tell a slow load from a crash.

The second answer keeps the frames going and lets the person edit the old scene while the new one loads. The cost appears at the end. The new scene replaces the old one, and every edit made meanwhile belongs to a scene that is gone. Either the edits vanish, or the editor must merge two scenes that never met.

The third answer is the one Strata uses, and it has four parts. The editor loads the new content on other threads while the old scene stays on screen. It marks the old scene read-only, so nothing can be lost. It swaps the scenes between two frames, so no frame shows half of each. And it cancels a load when a newer request arrives, so a person who clicks twice gets the second scene and no leftover work.

What this design costs is time without edits. While a large scene loads, the person can look and fly around, but cannot change anything. Strata accepts that: a short read-only wait is cheaper than a lost hour of work, and the viewport says why it waits.

## The map: who calls whom

Three kinds of code take part. The **commands** (`project.create`, `project.open`, `project.close`, `project.openSample`, `scene.new`, `scene.open`, `scene.loadStatus`) live in `StrataEditor/src/Editor/EditorAssetCommands.cpp` and `StrataEditor/src/Editor/EditorSceneCommands.cpp`. They check the guard, call the context and answer when the work ends. `EditorContext` in `StrataEditor/src/Editor/EditorContext.cpp` owns the open project, the edited scene and the load under way. The helpers each hold one job: `ProjectTemplates`, `ProjectSamples`, `RecentProjects`, `ProjectMigration` and `EditorPreferences`.

```mermaid caption="The steps of a project's open, from the project file to the start scene, with what waits for what" alt="A flow of boxes from reading the project file to the recent list. The old project closes, the asset scan starts, the migration may start, and the start scene waits for the scan and the migration."
flowchart TD
	A["Project::Load reads the project file"] --> B["CloseProject lets go of the old project"]
	B --> C["EditorAssetManager::BeginScan starts on jobs"]
	C --> D["Trash purge, recovery scan expected"]
	D --> E["OpenScriptEngine"]
	E --> F{"File version below 3?"}
	F -- yes --> G["BeginProjectMigration on a job"]
	F -- no --> H["Start scene waits for the scan"]
	G --> H
	H --> I["BeginOpenScene when both are done"]
	I --> J["RecentProjects::Add"]
```

The second picture shows who acts in one scene open, over time. The command starts the load and then polls once per frame. The loader works on its own threads, and each frame `EditorContext::UpdateSceneLoad` lets it use a share of the frame's :term[work budget]{id=work-budget}. Only when the load is ready does the swap happen.

```mermaid caption="One scene open over several frames: the request, the frames that continue, and the frame that swaps the new scene in" alt="A sequence of messages between the command, the editor context and the scene loader. The command starts the load, the loader works while frames continue, the context swaps the scene in at the start of a frame, and the command answers one frame later."
sequenceDiagram
	participant C as scene.open
	participant E as EditorContext
	participant L as SceneLoader
	C->>E: BeginOpenScene
	E->>L: LoadAsync
	loop every frame
		E->>L: Update with the frame's budget
		L-->>E: state and progress
	end
	E->>E: FinishOpenScene swaps the scene
	E->>E: prefab catch-up
	C-->>C: answers one frame later
```

## The contract

Callers of these functions may assume a few things, and must do a few. Each rule has a reason.

- A project opens at once. `BeginOpenProject` returns when the project is the open one, before its assets are scanned and before its start scene is loaded. The reason is the first idea of this page: nothing may hold a frame for the length of a scan.
- The project file is read before the open project closes. A file that cannot be read leaves the person in the project they had. The reason is that failure must change nothing.
- What needs the whole asset registry waits for the scan. Commands that answer from the registry, the start scene and the recovery scan all wait. The reason is that a half-filled registry gives wrong answers, such as "this scene does not exist".
- A project saved by 0.5.0 or older is migrated once, before its start scene opens. The reason is that the scene must open with the project's collision layers, which the migration is about to create.
- A scene being opened is read-only. The reason is the one the problem section gave: edits made to a scene that is about to go are lost.
- Opening, creating and closing a project take the guard for changes not yet saved and wait for saves in flight, as [Saving: the guard, background writes and resets](../editor/saving.md) explains. A save is never lost.

:::rule
A scene being opened is read-only: code that edits the scene outside `CommitEdit` calls `CheckSceneEditable` first. The reason is that only `CommitEdit` rolls an edit back when a load starts, so an edit made around it would be lost without notice.
:::

:::rule
Scenes load through `SceneLoader`, never through `LoadAssetSync`, and a scene that is no longer needed is released with `Scene::ReleaseInBackground`. The reason is the cost of a large scene: reading it blocks a frame, and destroying a million entities takes tens of milliseconds. The loader's states are the subject of [Sub-scenes: loading a scene into a scene](../world/sub-scenes.md).
:::

## A toy version

The toy below keeps only the ideas of a scene's open. A scene has a name and a count of entities. The editor shows one scene, and `BeginOpenScene` starts a load that creates 1,000 entities per frame. `TryEdit` is refused while a load runs, and a newer request replaces the load under way. The program runs five frames and prints what happens in each.

```cpp sketch="editor-projects-toy.cpp"
#include <algorithm>
#include <cstdio>
#include <string>

struct Scene
{
	std::string Name;
	int Entities = 0;
};

struct SceneLoad
{
	int Id = 0;
	Scene Result;
	int Created = 0;

	bool IsDone() const { return Created >= Result.Entities; }
};

class ToyEditor
{
public:
	void BeginOpenScene(const std::string& name, int entities)
	{
		// A newer request replaces the load under way.
		if (m_Loading)
			std::printf("  request %d cancelled\n", m_Load.Id);
		m_Load = { m_NextId++, { name, entities }, 0 };
		m_Loading = true;
	}

	bool TryEdit() const
	{
		// The scene on screen is read-only while another one is being opened.
		if (m_Loading)
		{
			std::printf("  edit refused: '%s' is being opened (%d%%)\n", m_Load.Result.Name.c_str(),
				m_Load.Created * 100 / m_Load.Result.Entities);
			return false;
		}
		std::printf("  edit applied to '%s'\n", m_Shown.Name.c_str());
		return true;
	}

	// One call per frame, before anything is drawn: the swap happens between two frames.
	void Update(int entitiesPerFrame)
	{
		if (!m_Loading)
			return;
		m_Load.Created = std::min(m_Load.Created + entitiesPerFrame, m_Load.Result.Entities);
		if (!m_Load.IsDone())
			return;
		m_Shown = m_Load.Result;
		m_Loading = false;
		std::printf("  request %d swapped in: '%s', %d entities\n", m_Load.Id, m_Shown.Name.c_str(), m_Shown.Entities);
	}

private:
	Scene m_Shown = { "Blank", 0 };
	SceneLoad m_Load;
	bool m_Loading = false;
	int m_NextId = 1;
};

int main()
{
	ToyEditor editor;
	for (int frame = 0; frame < 5; frame++)
	{
		std::printf("frame %d\n", frame);
		editor.Update(1000);
		if (frame == 0)
			editor.BeginOpenScene("Big", 2500);
		if (frame == 1)
			editor.TryEdit();
		if (frame == 2)
			editor.BeginOpenScene("Small", 1000);
		if (frame == 4)
			editor.TryEdit();
	}
}
```

```text output-of="editor-projects-toy.cpp"
frame 0
frame 1
  edit refused: 'Big' is being opened (40%)
frame 2
  request 1 cancelled
frame 3
  request 2 swapped in: 'Small', 1000 entities
frame 4
  edit applied to 'Small'
```

1. **Lines 25–28:** A newer request finds a load under way and cancels it, so only the latest request survives.
2. **Lines 35–39:** The guard: while a load runs, the shown scene refuses edits and reports the progress.
3. **Line 50:** One frame's share of work: the load makes at most `entitiesPerFrame` entities, so no frame stalls.
4. **Lines 53–54:** The swap: the finished scene becomes the shown one inside `Update`, before anything draws.

The first request asks for 2,500 entities, which is three frames of work. In frame 1 the edit is refused at 40 %, because 1,000 of 2,500 entities exist. In frame 2 a newer request cancels the first, and the new scene of 1,000 entities finishes in frame 3. In frame 4 the editor accepts edits again, on the new scene. The toy has no threads and no files: the real code adds them, and the rest of this page shows how.

## The real code: a project's life

### Creating a project and its first scene

`project.create` takes a folder, a name and a **template**, which is a recipe that fills a new project or scene with starting content. Strata has two. The template `empty` makes a project without a scene: you start from nothing. The template `basic3d` makes a lit start scene, saved as `Scenes/Main.stscene`, so that the first press of Play shows something.

The template `basic3d` holds five entities: a main camera with an audio listener, a sun, a sky, a ground, and a post-process entity. The sun comes from the Clear sky preset, and the post process uses filmic tone mapping with automatic exposure and temporal anti-aliasing. The ground needs more care than the rest, because the game must stand on it.

```cpp src="StrataEditor/src/Editor/ProjectTemplates.cpp#L77-L85" from="Entity ground = scene.CreateEntity(" to="collider.Offset = glm::vec3(0.0f, -c_Basic3DGroundColliderHalfThickness, 0.0f);" symbol="PopulateBasic3D"
Entity ground = scene.CreateEntity("Ground");
ground.GetComponent<TransformComponent>().Scale = glm::vec3(c_Basic3DGroundSize, 1.0f, c_Basic3DGroundSize);
MeshRendererComponent& renderer = ground.AddComponent<MeshRendererComponent>();
renderer.Mesh = BuiltinAssets::PlaneMesh;
renderer.Material = assets.GroundMaterial;
// A collider without a rigid body is a static body of its own: what falls on the ground stays on it.
BoxColliderComponent& collider = ground.AddComponent<BoxColliderComponent>();
collider.HalfExtents = glm::vec3(0.5f, c_Basic3DGroundColliderHalfThickness, 0.5f);
collider.Offset = glm::vec3(0.0f, -c_Basic3DGroundColliderHalfThickness, 0.0f);
```

The lighting values of the template belong to the lighting pages. What matters here is how a template is built: a function that takes a scene and creates entities, so the same code serves `project.create` and `scene.new`. The command `scene.new` takes the same `template` parameter, replaces the edited scene with a new one that is not saved, and fails while the edited scene holds changes not yet saved unless `force` is true. The material of the ground is a file of the project, `Materials/Ground.stmat`, and the editor creates it when the project lacks it.

`project.create` is a :term[deferred command]{id=deferred-command} with the guard in front: it refuses before it creates anything when the scene holds changes not yet saved. Then `EditorContext::CreateProject` makes the project, its script build files and an example script, opens it through the same function as `project.open`, and saves the template's scene as the start scene. The project file is written in the background, like every change of the project's settings.

### Opening a project

`project.open` wraps `BeginOpenProject` in the guard and in `AfterSaves`, which waits for saves in flight before the handler runs. `BeginOpenProject` calls `OpenProjectInternal`, which holds the order of the whole open. The first half reads the project, replaces the open one and starts the scan.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L374-L407" from="Ref<Project> project = Project::Load(projectFile, outError, &GetSettingsRegistry());" to="m_AssetManager->PurgeTrash(c_TrashKeepTime);" symbol="EditorContext::OpenProjectInternal"
Ref<Project> project = Project::Load(projectFile, outError, &GetSettingsRegistry());
if (!project)
	return false;

CloseProject();
m_Project = project;
m_ProjectGeneration++;
Project::SetActive(m_Project);
// The blank scene CloseProject left took the layers and fixed rate of no project. It stays the edited scene when the
// project has no start scene or it cannot be opened, so it takes this project's now.
ApplyProjectLayers();
m_ProjectFileWriter = CreateScope<SettingsFileWriter>([this](const std::string& error) { OnProjectFileWritten(error); });

// The editor camera and viewport settings continue where they were when the project was last closed.
const std::filesystem::path viewportState = GetViewportStateFile();
std::string viewportError;
if (FileSystem::Exists(viewportState) && !m_Viewport.Load(viewportState, &viewportError))
	ST_WARN("The saved viewport state is ignored: {}", viewportError);

EditorAssetManagerSpecification specification;
specification.AssetDirectory = m_Project->GetAssetDirectory();
specification.CacheDirectory = m_Project->GetCacheDirectory();
specification.TrashDirectory = m_Project->GetIntermediateDirectory() / c_TrashDirectory;
specification.WatchFiles = m_Specification.WatchAssetFiles;
m_AssetManager = CreateRef<EditorAssetManager>(specification);
AssetManager::SetActive(m_AssetManager);
m_DocumentSaver.SetAssetManager(m_AssetManager);
// In the background, the project opens at once: the scan's jobs prepare the assets while frames go on, and what needs
// the whole registry waits for it (commands, the start scene, the script usage scan).
if (m_Specification.ImportInBackground)
	m_AssetManager->BeginScan(ScanImports::InBackground);
else
	m_AssetManager->Scan(ScanImports::Wait);
m_AssetManager->PurgeTrash(c_TrashKeepTime);
```

1. **Line 374:** The project file is read before anything closes, so a broken file leaves the open project alone.
2. **Line 378:** `CloseProject` lets the old project go only now, when the new one is known to load.
3. **Lines 401–406:** The scan starts on jobs, so the project opens at once; the waiting form is for tools and tests.
4. **Line 407:** `PurgeTrash` removes what is older than the 30 days of `c_TrashKeepTime`.

Read it in three blocks. First, `Project::Load` runs before `CloseProject`, so a broken project file fails with the old project still open. Second, the viewport state of the project, the editor camera and its settings, returns from the file written when the project was last closed. Third, the :term[asset manager]{id=asset-manager} is created and, with `ImportInBackground` on, starts a scan on jobs: the project is open while its assets are still being found. The trash then drops what is older than 30 days.

The second half decides what waits for the scan. The recovery scan judges work not yet saved that was left behind by a crash against the asset registry, so it waits until the scan has filled it. The script engine opens. A project of an older version starts its migration. And the start scene is not opened but recorded: while the scan or the migration runs, the load status says `LoadingScene` and `IsSceneLoading` is true, so the scene is already read-only.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L419-L449" from="OpenScriptEngine(created);" to="m_RecentProjects.Add(m_Project->GetConfig().Name, m_Project->GetProjectFile());" symbol="EditorContext::OpenProjectInternal"
OpenScriptEngine(created);
// A project saved by 0.5.0 or older kept its collision layers in its scenes: they are read on a job before the start
// scene opens, so that it opens with the project's.
if (m_Project->GetFileVersion() < Project::c_FormatVersion)
	BeginProjectMigration();

// Continue with the start scene when the project has one: it loads in the background (UpdateSceneLoad warns when it
// cannot be opened), once the assets are registered and the migration is done. Meanwhile it counts as the scene being
// opened (IsSceneLoading).
const AssetHandle startScene = m_Project->GetConfig().StartScene;
const bool scanning = m_AssetManager->IsScanning();
if (scanning)
	m_AfterAssetScan = true;
else
	StartScriptUsageScan();
if (startScene.IsValid() && (scanning || m_ProjectMigration))
{
	CancelSceneLoad();
	m_StartSceneAfterScan = startScene;
	m_SceneLoadStatus = EditorSceneLoadStatus();
	m_SceneLoadStatus.ID = m_NextSceneLoadID++;
	m_SceneLoadStatus.Scene = startScene;
	m_SceneLoadStatus.State = SceneLoadState::LoadingScene;
	m_SceneLoadStatus.StartScene = true;
	m_SceneLoadStatus.Started = std::chrono::steady_clock::now();
}
else if (startScene.IsValid())
{
	OpenStartScene(startScene, m_NextSceneLoadID);
}
m_RecentProjects.Add(m_Project->GetConfig().Name, m_Project->GetProjectFile());
```

1. **Lines 422–423:** A project of a version below the current one starts its migration job before anything opens.
2. **Lines 429–431:** While the scan runs, a flag makes the recovery scan and the script usage scan wait for it.
3. **Lines 434–444:** With a scan or a migration under way, the start scene is only recorded; its status says `LoadingScene`, so the scene is read-only.
4. **Lines 445–447:** With nothing to wait for, the start scene opens at once through `OpenStartScene`.
5. **Line 449:** The project joins the recent list whatever becomes of its start scene.

Notice that the last line, the move of the project to the front of the recent list, runs at once: the person opened the project, whatever happens to its start scene. If the start scene fails to load, the project stays open with an empty scene, and the answer of `project.open` says why in `startSceneError`. When the command answers, it reports `startScene`, `startSceneOpened`, `seconds` and `migrated`.

:::note
`OpenProject` is the blocking form of the same open, for tools and tests: it calls `BeginOpenProject` and then waits for the load. The editor calls it only at the startup of a scripted run, one with a command script or the `--frames` option, which starts with its scene open. Once frames run for a person, a wait is a stalled frame.
:::

### Migrating a project saved by 0.5.0 or older

Versions up to 0.5.0 stored a scene's collision layers in the scene. Later versions keep one table for the whole project, in the settings section the page on [Projects and settings: the file, versions and sections](../world/projects-settings.md) describes. A project file of version 1 or 2 therefore has no table, and its layers are spread over its scenes. A **project migration** is the one-time upgrade that reads those scenes and writes the project's table, so that the project becomes version 3.

`BeginProjectMigration` submits one job. It calls `ProjectMigration::ScanSceneLayers`, which reads every scene document of the asset folder and keeps the layers each stores. A scan that finds the default table counts that scene as storing none. The job can be cancelled: closing the project sets a flag, and the scan stops reading. Nothing of a cancelled migration is applied.

When the job is complete, `UpdateProjectMigration` runs on the :term[main thread]{id=main-thread}, once per frame, and merges the result.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L513-L549" from="const Scope<PendingMigration> migration = std::move(m_ProjectMigration);" to="ApplyProjectLayers();" symbol="EditorContext::UpdateProjectMigration"
const Scope<PendingMigration> migration = std::move(m_ProjectMigration);
const ProjectMigration::SceneLayerScan& scan = *migration->Scan;
const ProjectMigration::LayerMerge merge = ProjectMigration::MergeSceneLayers(scan.Scenes, m_Project->GetConfig().StartScene);
std::vector<std::string> unreadable = scan.Problems;
// No undo step: the project had no table to go back to.
if (merge.Layers && !merge.Layers->IsDefault())
{
	std::string error;
	if (!m_Project->GetSettings().Set(ProjectCollisionLayers::c_SectionId, merge.Layers->ToJson(), GetSettingsRegistry(), &error))
		unreadable.push_back(fmt::format("The scenes' collision layers could not become the project's: {}", error));
}
// The version records that the migration ran, so the file is written as version 3 also when no table resulted: a
// project migrates once, and a table reset later never comes back from the scenes.
SaveProjectFile();
auto list = [](const std::vector<std::string>& items, std::string_view separator)
{
	std::string text;
	for (const std::string& item : items)
		text += (text.empty() ? "" : std::string(separator)) + item;
	return text;
};
if (!merge.Scenes.empty())
{
	ST_INFO("The collision layers of {} scene(s) are the project's now (Project Settings > Collision Layers): {}", merge.Scenes.size(),
		list(merge.Scenes, ", "));
}
if (!merge.Conflicts.empty() || !unreadable.empty())
{
	std::vector<std::string> problems = merge.Conflicts;
	problems.insert(problems.end(), unreadable.begin(), unreadable.end());
	ST_WARN("Making the scenes' collision layers the project's: {}", list(problems, "; "));
}
m_ProjectMigrationResult = { { "collisionLayers", {
	{ "scenes", merge.Scenes },
	{ "conflicts", merge.Conflicts },
	{ "unreadable", unreadable } } } };
ApplyProjectLayers();
```

1. **Line 515:** The merge runs on the main thread with the start scene's handle, so its names come first.
2. **Lines 518–523:** A table that is not the default becomes the project's layer settings; a refusal is reported, not thrown.
3. **Lines 524–526:** The file is saved even when no table results, so the version records that the migration ran.
4. **Lines 539–549:** Conflicts become one warning and the `migrated` result, and the layers apply to the edited scene.

The merge itself, `MergeSceneLayers`, follows one rule: names come from the start scene first, then from the other scenes by path. A scene that names a layer differently from an earlier scene, or gives a layer a name that another layer already has, causes a conflict, and the first name stays. A pair of layers that any scene keeps apart stays apart. Scenes whose collision matrices differ are a conflict too, and the report names the pairs they disagree on.

Consider two scenes. `Main` names layer 1 "Player" and layer 2 "Enemy", and `Cave` names layer 2 "Monster", layer 3 "Enemy" and layer 4 "Pickup". `Main` is the start scene, so it comes first.

Layer 2 stays "Enemy", because "Monster" arrives second. Layer 3 gets no name, because "Enemy" is taken. Layer 4 is added.

The result has three named layers and two conflicts, each reported in a log warning and in the `migrated` field of the answer.

Two details matter. The file is saved even when no table results, because the version records that the migration ran: a project migrates once, and a table that the person resets later never comes back from old scenes. And the scene files are not touched: the layers they store are ignored from now on and dropped at their next save.

### Waiting for the start scene

The start scene waits for two things: the scan, and the migration. When both are done, the same function that opens any scene, `BeginOpenScene`, starts the load. That is why a project with a million-entity start scene opens its window at once, with an empty scene and a progress card.

## The real code: a scene's open

`scene.open` runs `OpenSceneAndWait`, which calls `BeginOpenScene` and then returns a deferred result. The function checks the handle first, then asks the loader for the scene.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L784-L806" from="SceneLoadOptions options;" to="return true;" symbol="EditorContext::BeginOpenScene"
SceneLoadOptions options;
// The current file, not a copy loaded earlier.
options.Reload = true;
options.Prepare = GetScenePreparation();
Scope<SceneLoad> next = CreateScope<SceneLoad>();
next->Request = SceneLoader::LoadAsync(handle, options);
next->RequestedBy = m_Journal->GetOutermostRunningId();
// A load under way is replaced: its pins and the loads only it needed go. The new one started first, so that what
// both use keeps loading (Cancel leaves assets others pin alone).
CancelSceneLoad();
m_SceneLoad = std::move(next);
m_SceneLoadStatus = EditorSceneLoadStatus();
m_SceneLoadStatus.ID = m_NextSceneLoadID++;
m_SceneLoadStatus.Scene = handle;
m_SceneLoadStatus.State = m_SceneLoad->Request.GetState();
m_SceneLoadStatus.Started = std::chrono::steady_clock::now();
// It fails at once only for what LoadAsync rejects (checked above already); otherwise Update advances it.
if (m_SceneLoad->Request.IsFinished())
{
	UpdateSceneLoad();
	return fail(m_SceneLoadStatus.Error);
}
return true;
```

1. **Lines 785–786:** `Reload` asks for the file as it is now, not a copy loaded earlier.
2. **Line 787:** `Prepare` builds the render proxies while the old scene is shown, so the swap frame builds none.
3. **Lines 789–793:** The new load starts before the old one is cancelled, so assets both use keep loading.
4. **Lines 801–805:** A load that fails at once is judged right away; otherwise the update of each frame advances it.

Three details carry the design. The option `Reload` asks for the file as it is now, not for a copy loaded earlier, because the person may have saved the scene since. The `Prepare` function builds the scene's render proxies, the drawing code's own records of what each entity draws. It builds them while the old scene is shown: a hundred thousand mesh :term[renderers]{id=renderer} take tens of milliseconds to prepare, and the swap must not pay them in one frame.

The new load also starts before the old one is cancelled, so that assets both use keep loading. A load pins its assets, that is, asks to keep them in memory, and `Cancel` leaves alone the assets that other requests pin.

The read-only guard is short.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L869-L879" symbol="EditorContext::CheckSceneEditable"
bool EditorContext::CheckSceneEditable(std::string* outError) const
{
	if (!IsSceneLoading() || IsPlaying())
		return true;
	if (outError)
	{
		*outError = fmt::format("Scene {} is being opened ({:.0f}%): the edited scene is read-only until it replaces it (scene.loadStatus)",
			m_SceneLoadStatus.Scene.ToString(), m_SceneLoadStatus.Progress * 100.0f);
	}
	return false;
}
```

1. **Line 871:** Edits are refused only while a scene loads, and a running game is exempt, because its edits go to a copy.
2. **Lines 873–876:** The message names the scene and the progress, and points to `scene.loadStatus`.

Edits that go through `CommitEdit` are rolled back by it. Code that edits in another way, such as the property edit helpers and many commands, calls this function and returns its message. A running game is exempt: its edits go to the running copy, which `play.stop` discards.

Each frame, the editor calls `UpdateSceneLoad` after the saves and the :term[asset scan]{id=asset-scan}, with one work budget for all loading work. When the request is finished and ready, the swap runs.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L927-L941" from="const uint64_t requestedBy = m_SceneLoad->RequestedBy;" to="m_Journal->NoteUndo(requestedBy, m_UndoStack, records);" symbol="EditorContext::UpdateSceneLoad"
const uint64_t requestedBy = m_SceneLoad->RequestedBy;
const uint64_t records = m_UndoStack.GetRecordCount();
if (requestedBy != 0)
	m_Journal->NoteEditsOutsideCommands(m_UndoStack);
const bool resumed = m_Journal->Resume(requestedBy);
// The scene is in place before the request (and its pins) goes, so what it uses is requested from now on.
FinishOpenScene(request.TakeScene(), handle, request.GetAssets());
m_SceneLoad.reset();
// Once the scene is editable: instances of prefabs that changed while it was closed take their values (an undo step)
// before anything else, scene.open's answer included, sees the scene.
m_PrefabSync.OnSceneOpened(*this);
if (resumed)
	m_Journal->Suspend(requestedBy);
if (requestedBy != 0)
	m_Journal->NoteUndo(requestedBy, m_UndoStack, records);
```

1. **Lines 927–931:** The command that asked is remembered, so the swap counts as its work in the activity journal, the editor's record of what each command did, and for its :term[undo step]{id=undo-step}.
2. **Line 933:** The swap itself: the scene is in place before the request, and its pins, are let go.
3. **Line 937:** The :term[prefab]{id=prefab-world} catch-up runs before anyone sees the scene.
4. **Lines 940–941:** The catch-up's undo step is recorded as the command's.

The swap goes through `FinishOpenScene`.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L944-L961" symbol="EditorContext::FinishOpenScene"
void EditorContext::FinishOpenScene(Ref<Scene> scene, AssetHandle handle, std::span<const AssetHandle> loaded)
{
	ResetScene(std::move(scene), handle);
	// What the previous scene used, this one's load did not bring in and the viewport does not request for this one in its
	// first frames is released then.
	m_AssetManager->ScheduleTrim(AssetResidency::c_SceneSwitchTrimFrames, AssetResidency::c_SceneSwitchTrimFrames, loaded);
	if (!m_Viewport.RestoreSceneCamera(handle))
	{
		// Shown for the first time: frame what it renders. Meshes that are still loading stand in as placeholder boxes,
		// so the view is framed again once they are known.
		std::vector<AssetHandle> pendingMeshes;
		if (m_Viewport.FrameScene(*this, &pendingMeshes) && !pendingMeshes.empty())
		{
			m_PendingFrame = PendingFrame { handle, std::move(pendingMeshes), m_Viewport.GetCamera(),
				std::chrono::steady_clock::now() + c_PendingFrameTimeout };
		}
	}
}
```

1. **Line 946:** `ResetScene` replaces the scene, as the page on saving describes.
2. **Line 949:** A trim lets assets that only the old scene used leave after a few frames.
3. **Lines 950–960:** The stored camera returns, or the view frames the scene and frames it again once the pending meshes are known.

`ResetScene` does the replacement itself, as the page on [saving](../editor/saving.md) explains: it writes recovery data for changes not yet saved, clears the :term[undo stack]{id=undo-stack} and the selection, and lets the old scene go with `Scene::ReleaseInBackground`. Then `ScheduleTrim` lets assets that only the old scene used leave memory after three frames, as [Residency: keeping and releasing what is loaded](../assets/residency.md) describes. The editor camera returns to the view stored for the scene, or frames what the scene renders. Meshes that still load are drawn as boxes, so the view is framed again once they are known, but only if the person has not moved the camera and not after 30 seconds.

Last comes the :term[prefab]{id=prefab-world} catch-up: `PrefabSync::OnSceneOpened` updates every instance of a prefab that changed while the scene was closed, as one :term[undo step]{id=undo-step}. It runs before anyone sees the scene, `scene.open`'s answer included. The answer comes one frame after the swap, because the editor records a frame's time at the start of the next one. It reports `scene`, `name`, `entities`, `seconds`, `frames` and `frameTimes`: the count, median, mean, 95th percentile and maximum of the time that the processor spent on the frames that ran meanwhile.

:::example
A worked example opens a copy of the sample `OpenWorld`, a game with a world of streamed cells. The request names the sample and a folder for the copy.

```json
{ "sample": "OpenWorld", "directory": "C:/Work/OpenWorldCopy" }
```

The command `project.openSample` copies the sample without `.strata`, opens the copy and answers once the start scene replaced the empty scene. While it waits, a second client asks `scene.loadStatus`. The `open` part of the answer holds `state`, one of `LoadingScene`, `LoadingDependencies` and `Preparing`, and `progress` from 0 to 1. After the swap, `open` is null and `lastOpen` says `Ready` and how many `seconds` the load took.

Now the client tries to change something during that time, for example `entity.create` with a name. The command fails, and its error is the text of `CheckSceneEditable`: the scene, the percentage, and the words that the edited scene is read-only until the new one replaces it. After `lastOpen` says `Ready`, the same call works.

Count frames as the toy does. If the loader made 1,000 entities per frame, a scene of 25,000 entities would take at least 25 frames, about 0.4 seconds at 60 :term[frames per second]{id=frame-rate}. Every one of those frames still draws and answers input.
:::

## Samples, recent projects and closing

A **sample** is a finished game that ships with the editor to learn from, opened as a copy so that the original never changes. `ProjectSamples` finds them through `Samples.json`, the index of a `Samples` folder next to the editor's :term[executable]{id=executable}, which the build fills from the :term[repository's]{id=repository} `Samples/` folder. `project.samples` lists their id, name, description and picture. `project.openSample` copies one into an empty or new folder without `.strata`, the local editor data: the :term[import cache]{id=import-cache}, the script builds and the editor state.

The copy starts clean and builds its own scripts, so the command's description tells you to run `script.build` before you play. A failed copy removes what it created.

Opening a sample in place would change a file the next person needs untouched. A copy costs disk space and a script build, and Strata accepts both.

`project.close` takes the same guard as `project.open` and returns `closed`. Without a project it does nothing. `CloseProject` first finishes the saves in flight, cancels an export and a scene load, stops a migration, stores the scene's camera and lets the project go, then the editor shows its launcher.

The **recent projects** are the list the launcher shows. `RecentProjects` keeps at most 12, most recent first, in `RecentProjects.json` in the `Strata` folder of the user's data folder.

Every editor of that user shares the file. A change reads the file first, so projects other editors added are kept. Projects whose file is gone do not appear, but one on a drive that is out of reach stays, so a network share never loses its entry. Scripted runs, those with a command script or the `--frames` option, only read the list: they are not the person's sessions.

## The preferences store

The recent projects share the `Strata` folder with the **preferences**, the person's own settings that hold for every project, such as the external :term[code editor]{id=code-editor}. `EditorPreferences` keeps them in `Preferences.json`, format 1, at most 64 KiB. The file stores the values of the settings registry's user sections, each as `Version` and `Value`. Each stored section is validated by its section. A value the section refuses stays as stored while the section's default applies, so nothing a newer editor wrote is lost.

Writes run in the background, through the same writer as the project file. A failed write keeps the change in memory and leaves the file unwritten until a later write works. The editor tells the person, and `preferences.save` tries again once the cause is gone.

Suppose a later editor wrote the file in a format this editor cannot read. Then the file is left alone, every section has its default, and changes are refused. Replacing it would destroy that editor's settings. On the first start, the external editor stored in 0.5.0's `EditorSettings.json` is imported once; that file is read and never written.

`preferences.set` and `preferences.save` are Session commands: they record no undo step, because the person's preferences are not part of any scene. The window that draws them is the subject of another page.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Load everything before the first frame | Simple tools | The simplest code, no states | A frozen window for the length of the load, no cancel |
| Edit the old scene while the new one loads | Editors with one live document | No wait without edits | Edits that vanish at the swap, or a merge of two scenes |
| One document window per scene | Multi-document editors | Several scenes open at once | The memory of both, and a second set of panels and undo history |
| Migrate old projects on every open | :term[Importers]{id=importer} that never rewrite files | No version in the file | A scan of all scenes on each open, and conflicts decided again each time |

## How it is tested

The suites sit in `StrataTests/src/Editor/`.

`EditorSceneLoadTests.cpp` checks these things, among others. A `scene.open` loads while the old scene stays shown and read-only. Opening another scene, a new scene or closing the project cancels a load. A scene deleted while it opens fails the command. And `project.open` answers once the start scene replaced the empty one.

`ProjectMigrationTests.cpp` checks the merge: names, conflicts, pairs that a scene disables, a version 3 project that is not migrated again, and copies of `PhysicsPlayground` and `OpenWorld`. `ProjectSamplesTests.cpp` checks `project.samples`, `project.openSample`, the index and `project.close`. `EditorTemplateTests.cpp`, `RecentProjectsTests.cpp` and `EditorPreferencesTests.cpp` cover the templates, the recent list and the preferences.

Run some suites directly with a doctest filter: `build/windows/bin/Debug/StrataTests.exe --test-suite=Editor*`. The tests keep their files in `Tests::CreateTemporaryDirectory()` and copy samples with `Tests::CopySampleProject`, as the testing rules require.

## Changing it safely

The extension points are few. A new template is an entry in the table of `ProjectTemplates`, an id constant, a case in `Populate`, and a function that populates a scene; `HasStartScene` is already true for every template but `empty`. The `template` parameter of `project.create` and `scene.new` lists the ids in its schema, so both schemas change too; `project.templates` reads the table. A new step of the open goes into `OpenProjectInternal` only if it needs no file on the main thread, because opening must stay quick.

These rules apply, each with its reason.

- A command that replaces the edited scene begins with `CommandUtils::CheckUnsavedChanges` and is wrapped in `CommandUtils::AfterSaves`. Without them, a forced open could race a save and lose it.
- Code that edits outside `CommitEdit` calls `CheckSceneEditable`. Without it, an edit lands on a scene the swap is about to discard.
- Nothing waits for a background load: a command that must wait returns a deferred result whose poll allocates nothing per frame. A wait in a command is a frozen frame.
- A change to the project file's version needs a migration and tests that a project migrates once.

Before a commit, run the suites above and the feature test, and walk the engine's review checklist.

## Summary

- A scene opens on other threads while the old one stays on screen and read-only; the swap happens between two frames, and a newer request cancels the load under way.
- `project.open` reads the file first, closes the old project, scans assets in the background, opens the script engine, migrates old projects, then opens the start scene when the scan and the migration are done.
- A project of version 1 or 2 is migrated once. Scene layers are read on a job and merged, the start scene's names first, conflicts are reported, and the file is written as version 3.
- The templates are `empty` and `basic3d`; a sample opens as a copy without `.strata`, and the recent list holds at most 12 projects.
- The preferences file holds user sections for every project; a failed write stays in memory, and a file from a later editor is left alone.

## Check yourself

1. A client sends `scene.open` for a large scene and, five frames later, `entity.create`. What happens, and why?
   :::answer{tests="background-open"}
   The second command fails with the read-only message. The edited scene stays shown, but `CheckSceneEditable` refuses edits while a scene is being opened, because an edit made now would be lost at the swap. Calling it again after `scene.loadStatus` reports `Ready` works.
   :::
2. In `OpenProjectInternal`, which of these happens first? (a) the asset scan starts, (b) the old project closes, (c) the project file is read.
   :::answer{tests="project-open-order"}
   The order is (c), then (b), then (a). The file is read first, so a broken file leaves the old project open. The old project closes next, and then the new project's scan starts. The start scene waits for the scan and, for an old project, the migration.
   :::
3. A project of version 2 has scene `A` as its start scene, which names layer 1 "Wall", and scene `B`, which names layer 1 "Floor". What is layer 1 after the migration, and what does the person see?
   :::answer{tests="migration"}
   Layer 1 is "Wall", because the start scene's names come first. The conflict is logged as a warning and listed under `conflicts` in the answer's `migrated` field. The file is written as version 3, so the project is never migrated again.
   :::
4. Why does `project.openSample` copy the sample instead of opening it?
   :::answer{tests="templates-samples"}
   Opening in place would change the shipped sample. The copy omits `.strata`, the local editor data, so it starts clean, and you build its scripts with `script.build`. The two templates are `empty` and `basic3d`; samples are separate games.
   :::
5. The disk is full, and a preferences write fails. What does the person lose?
   :::answer{tests="preferences"}
   Nothing yet: the change stays in memory, the file stays unwritten, and the editor reports the failure. A later change or `preferences.save` writes it again once the cause is gone. Only closing the editor with the file still unwritten loses the change.
   :::

## Exercises

1. **Basic.** Trace it yourself: open a copy of a sample with `project.openSample`, with breakpoints in `BeginOpenScene`, `UpdateSceneLoad` and `FinishOpenScene`. Count the frames between the request and the swap, and name what runs after the swap before anyone sees the scene.
   :::answer[Worked solution]{tests="background-open"}
   All three functions are in `StrataEditor/src/Editor/EditorContext.cpp`. `BeginOpenScene` runs once, in the frame of the request. `UpdateSceneLoad` runs once per frame until the request is ready, and the number of frames between the two breakpoints is the count you want. `FinishOpenScene` runs in the frame of the swap, and right after it `PrefabSync::OnSceneOpened` runs the prefab catch-up, before the command answers.
   :::
2. **Medium.** Read `PopulateBasic3D` and plan a third template, `physics-test`, with a ground and ten boxes. List the files and tables you would change.
   :::answer[Worked solution]{tests="templates-samples"}
   Add an entry to `c_Templates` in `StrataEditor/src/Editor/ProjectTemplates.cpp` with an id, a name and a description, and a function that creates the entities. Add the id constant, a case in `Populate` and the id in the `enum` of the `template` parameter of `project.create` and `scene.new`. Add a test to `EditorTemplateTests.cpp`, and exercise it in the feature test.
   :::
3. **Hard.** Write a separate program that merges the layer names of two scenes, the start scene first, and reports conflicts.
   :::answer[Worked solution]{solution="sketches/editor-projects-merge.cpp" tests="migration"}
   The program keeps a map from layer index to name, and visits the scenes in order. An index that is already named keeps its name and reports a conflict if the new name differs. A new index whose name belongs to another layer reports a conflict and gets no name. The program prints the merged table and the conflicts.

   ```cpp sketch="editor-projects-merge.cpp"
   #include <cstdio>
   #include <map>
   #include <string>
   #include <vector>

   struct SceneLayers
   {
   	std::string Path;
   	std::map<int, std::string> Names;
   };

   int main()
   {
   	// The start scene comes first, so that its names win.
   	const std::vector<SceneLayers> scenes = {
   		{ "Scenes/Main.stscene", { { 1, "Player" }, { 2, "Enemy" } } },
   		{ "Scenes/Cave.stscene", { { 2, "Monster" }, { 3, "Enemy" }, { 4, "Pickup" } } } };

   	std::map<int, std::string> merged;
   	std::vector<std::string> conflicts;
   	for (const SceneLayers& scene : scenes)
   	{
   		for (const auto& [index, name] : scene.Names)
   		{
   			const auto existing = merged.find(index);
   			if (existing != merged.end())
   			{
   				if (existing->second != name)
   					conflicts.push_back(scene.Path + ": layer " + std::to_string(index) + " stays '" + existing->second + "', not '" + name + "'");
   				continue;
   			}
   			bool nameTaken = false;
   			for (const auto& [otherIndex, otherName] : merged)
   				nameTaken = nameTaken || otherName == name;
   			if (nameTaken)
   				conflicts.push_back(scene.Path + ": '" + name + "' already names another layer, so layer " + std::to_string(index) + " gets no name");
   			else
   				merged[index] = name;
   		}
   	}

   	for (const auto& [index, name] : merged)
   		std::printf("layer %d: %s\n", index, name.c_str());
   	for (const std::string& conflict : conflicts)
   		std::printf("conflict: %s\n", conflict.c_str());
   }
   ```

   ```text output-of="editor-projects-merge.cpp"
   layer 1: Player
   layer 2: Enemy
   layer 4: Pickup
   conflict: Scenes/Cave.stscene: layer 2 stays 'Enemy', not 'Monster'
   conflict: Scenes/Cave.stscene: 'Enemy' already names another layer, so layer 3 gets no name
   ```

   1. **Line 14:** The start scene stands first, so its names win.
   2. **Lines 25–30:** An index that already has a name keeps it, and a different name is a conflict.
   3. **Lines 32–38:** A name that already belongs to a different layer is a conflict, and this layer gets no name.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorContext.cpp`: `OpenProjectInternal`, `BeginOpenScene`, `UpdateSceneLoad`, `FinishOpenScene`, `CheckSceneEditable`, `UpdateProjectMigration`.
- `StrataEditor/src/Editor/ProjectMigration.h`: `ScanSceneLayers` and `MergeSceneLayers`.
- `StrataEditor/src/Editor/ProjectTemplates.cpp`, `ProjectSamples.h`, `RecentProjects.h` and `EditorPreferences.h`.
- Commands: `project.create`, `project.open`, `project.close`, `project.openSample`, `project.samples`, `project.templates`, `scene.new`, `scene.open`, `scene.loadStatus`, `preferences.get`, `preferences.set`, `preferences.save`.
- Tests: `StrataTests/src/Editor/EditorSceneLoadTests.cpp`, `ProjectMigrationTests.cpp` and `ProjectSamplesTests.cpp`.

## Further reading

- Game Programming Patterns, "Game Loop" chapter, by Robert Nystrom: why a frame loop must never block (beginner).
