---
id: worlds/export
title: "Shipping a game: the export"
description: "How the editor turns an open project into a folder a player can run, one frame at a time, and why every check runs before the first file is written."
kind: internals
size: M
tracks: [E]
needs: [worlds/physics-scripts, assets/packs-export, world/projects-settings, core/files]
time: 60
learn:
  - id: trace-states
    text: trace one export through its states and name the thread that does each step
  - id: name-checks
    text: name the up-front checks of the start function in order and say why each runs before any file is written
  - id: fail-first
    text: explain why the icon is decoded and the executable stamped before the pack is written
  - id: name-folder
    text: name every file of an exported game and the check that guards it
  - id: add-check
    text: add a new check to the state where it belongs
since: 0.3.0
status: final
---

The editor keeps your sources, your imports, a project file and a script module it has loaded. A player needs none of that: a player needs one folder with a program, a pack of assets and a manifest. `GameExport` builds that folder from the open project while the editor keeps drawing frames. This page covers how it checks, waits, cooks, plans and writes, and which thread does each part. It does not cover the pack's format ([asset packs](../assets/packs-export.md)), the game's identity and icon, or the Export dialog.

## The problem and how engines solve it

Think of moving house. Your flat holds furniture, boxes of tools, a half-built shelf and the paperwork of the move. The new home needs only the furniture. Packing is the work of deciding what goes, wrapping it and checking that nothing breaks on the way.

A :term[game engine]{id=game-engine} has the same split. The editor holds :term[source files]{id=source-file}, imports of them, undo history and tools. A player's machine needs the data the game reads and a program that reads it.

Engines answer with a build step. Unity runs a player build, which compiles scripts and gathers the scenes and assets it can reach. Unreal cooks the content into platform formats and bundles it into `.pak` files. Both take minutes on big projects, and both run as a step apart from editing.

Strata's export is that step with three choices. It runs inside the editor, so it can use the imports the editor already made. It never blocks a frame: the editor stays usable while it works. And it ships exactly what the editor runs: the same script module, the same saved scenes. It writes an asset pack, a manifest, the script module, an icon and a copy of the :term[runtime]{id=runtime} program renamed after the game.

## The map

The export is a small state machine that `EditorContext` advances once per frame by calling `Update`. Two threads take part. The :term[main thread]{id=main-thread} owns the scene, the :term[asset manager]{id=asset-manager} and all planning. One job on an input and output (I/O) thread does the slow writing, and the two share a few atomic numbers and one :term[mutex]{id=mutex}.

```mermaid caption="An export starts with checks, waits and cooks on the main thread, then hands the writing to one job on an input and output thread, and ends in one of three outcomes." alt="A flow of boxes. Start checks lead to Waiting for imports, then Cooking worlds, then Packing, then Copying. Waiting, Cooking and Packing lead to Failed when a check fails or to Cancelled when asked. Copying leads to Succeeded. A note marks Start, Waiting and Cooking as the main thread, and Packing and Copying as the input and output job."
flowchart LR
    S["Start: checks, no side effects"] --> W["WaitingForImports (main thread)"]
    W --> C["CookingWorlds (main thread, cook jobs)"]
    C --> P["Packing (I/O job)"]
    P --> Y["Copying (I/O job)"]
    Y --> OK["Succeeded"]
    W -.-> X["Failed or Cancelled"]
    C -.-> X
    P -.-> X
    Y -.-> X
```

A project without worlds skips `CookingWorlds`. `StrataEditor/src/Editor/GameExport.h` holds the options, the state enum and the class. `StrataEditor/src/Editor/GameExport.cpp` holds everything else. The commands that drive it live in `StrataEditor/src/Editor/EditorAssetCommands.cpp`.

The shared numbers are what the world sees. `DoneBytes` and `TotalBytes` give the progress, `GetStage` gives a line of text, and `GetState` gives one of the seven states. The Export dialog and the `project.exportStatus` command read exactly these.

:::example
A project packs two assets of 4 MB and 2 MB stored size. Its script module is 2 MB and the runtime is 12 MB. The export counts 6 MB of pack :term[bytes]{id=byte} and 14 MB of copied bytes, so `TotalBytes` is 20 MB. Halfway through the pack, the writer has stored 3 MB. Progress is 3 divided by 20, which is 15 %, and the stage reads "Packing 2 assets (3 of 20 MB)".

When the pack is done, `DoneBytes` is set to 6 MB, so progress is 30 %. Writing the module adds 2 MB (40 %); the end sets it to 20 MB (100 %). Counting bytes keeps the bar smooth even when one asset is huge, and the code clamps the share so it never exceeds 1.
:::

## The contract

Callers and the code follow a few rules. Each has a reason.

- Call `Start` on the main thread. It returns `nullptr` and an error text, or an export that already holds its own copies of everything it needs. A refusal has no side effects: it creates no file and changes no setting. `Start` creates the export folder last, once every check passed.
- Call `Update` once per frame. It never waits for a job; it polls, returns, and tries again next frame.
- The export plans the pack once, on the main thread, when no import and no save is pending. A plan made earlier would miss what those jobs write.
- The I/O job touches only its own copies. The editor's asset manager stays alive until the job ends, which is why the :term[destructor]{id=destructor} cancels and waits.
- Cancelling is polite: `Cancel` sets a flag that the job reads between blocks. Files already written stay.
- Nothing is written until nothing that can be checked in memory is left to fail.

:::rule
The editor's rule that background work goes through `JobSystem` and its results come back through polled state, never :term[callbacks]{id=callback} that touch engine state from worker threads. `GameExport` follows it: the job writes only into `Shared`, and the main thread reads it in `Collect`. See [Jobs](../core/jobs.md) for the model.
:::

## A toy version

The toy below has the same shape in under 100 lines. A project has a saved flag, a count of pending imports and an icon that may not decode. `Start` refuses a scene that is not saved. `Update` waits one frame per pending import, then the write function checks the icon before it writes the first file. Look at the last two runs: neither leaves a file behind.

```cpp sketch="worlds-export-toy.cpp"
// A toy export: checks before work, a state per frame, and every failure before the first write.
#include <cstdio>
#include <string>
#include <vector>

enum class State
{
	WaitingForImports,
	Packing,
	Succeeded,
	Failed
};

struct Project
{
	bool SceneSaved = true;
	int PendingImports = 2;
	bool IconDecodes = true;
};

const char* ToString(State state)
{
	switch (state)
	{
		case State::WaitingForImports: return "WaitingForImports";
		case State::Packing: return "Packing";
		case State::Succeeded: return "Succeeded";
		case State::Failed: return "Failed";
	}
	return "Unknown";
}

// Start reads no file and writes nothing: a refusal leaves the disk as it was.
bool Start(const Project& project, std::string& error)
{
	if (!project.SceneSaved)
	{
		error = "The open scene has unsaved changes";
		return false;
	}
	return true;
}

// The write job: whatever can fail comes before the first write.
bool Write(const Project& project, std::vector<std::string>& folder)
{
	if (!project.IconDecodes)
		return false;
	folder.push_back("Game.stpak");
	folder.push_back("Game.stgame");
	folder.push_back("Game.exe");
	return true;
}

// One call per frame: each state does a little work and names the next state.
State Update(State state, Project& project, std::vector<std::string>& folder)
{
	if (state == State::WaitingForImports)
	{
		if (project.PendingImports > 0)
		{
			project.PendingImports--;
			return state;
		}
		return State::Packing;
	}
	if (state == State::Packing)
		return Write(project, folder) ? State::Succeeded : State::Failed;
	return state;
}

void Run(const char* name, Project project)
{
	std::string error;
	std::vector<std::string> folder;
	std::printf("%s\n", name);
	if (!Start(project, error))
	{
		std::printf("  refused: %s\n", error.c_str());
		return;
	}
	State state = State::WaitingForImports;
	for (int frame = 1; state != State::Succeeded && state != State::Failed; frame++)
	{
		state = Update(state, project, folder);
		std::printf("  frame %d: %s\n", frame, ToString(state));
	}
	std::printf("  files written: %zu\n", folder.size());
}

int main()
{
	Run("Good project", Project { true, 2, true });
	Run("Unsaved scene", Project { false, 0, true });
	Run("Broken icon", Project { true, 0, false });
	return 0;
}
```

```text output-of="worlds-export-toy.cpp"
Good project
  frame 1: WaitingForImports
  frame 2: WaitingForImports
  frame 3: Packing
  frame 4: Succeeded
  files written: 3
Unsaved scene
  refused: The open scene has unsaved changes
Broken icon
  frame 1: Packing
  frame 2: Failed
  files written: 0
```

1. **Line 34:** `Start` reads no file and writes nothing, so a refusal leaves the disk as it was.
2. **Lines 47–49:** the icon check comes before the first file is added to the folder.
3. **Line 62:** each pending import costs one frame, so the state stays put while the imports run.
4. **Line 68:** the move from `Packing` to `Succeeded` or `Failed` happens in one call.

The toy shows the three habits that matter. The checks that need no files run in `Start`, before any state exists. A state does a little work per call and names its successor. And the writing function puts everything that can fail before everything that changes the disk. The real code adds a second thread, byte counts, cancellation and many more checks.

## The real code

The real export follows the data in four steps: `Start`, waiting and cooking, planning, then the I/O job. Each difference from the toy has a reason.

### Start: checks that read no file

`Start` asks the open project questions that memory can answer. The order matters, because the first failure names what to fix first.

```cpp src="StrataEditor/src/Editor/GameExport.cpp#L174-L191"
EditorAssetManager* assets = context.GetAssetManager();
if (!assets)
	return fail("No project is open");
if (context.IsPlaying())
	return fail("Stop playing before exporting");
// A save in flight of the scene as it is now counts as saved: the export plans once it is written, and fails if it fails.
const uint64_t awaitedSave = context.IsSceneModified() ? context.FindSaveOfCurrentState() : 0;
if (context.IsSceneModified() && awaitedSave == 0)
	return fail("The open scene has unsaved changes; save it first (the export uses the saved files)");
const Project& project = *context.GetProject();
if (std::optional<std::string> problem = CheckExportDirectory(options.Directory, project.GetProjectDirectory()))
	return fail(std::move(*problem));

AssetHandle startScene = project.GetConfig().StartScene;
if (!startScene.IsValid())
	startScene = context.GetSceneHandle();
if (!startScene.IsValid() || assets->GetAssetType(startScene) != AssetType::Scene)
	return fail("The project has no start scene: save the scene and set it with project.setStartScene");
```

1. **Lines 175–178:** the first checks; every failure returns `nullptr` with a message and creates nothing.
2. **Lines 180–182:** a scene with changes passes only when a save of exactly this state is :term[in flight]{id=in-flight}.
3. **Lines 184–185:** the folder check runs before any file or project data is read.
4. **Lines 187–191:** the open scene stands in for a missing start scene, and the handle must name a scene.

The first checks cover a project, no Play, a saved scene and a good export folder. A scene with changes not yet saved passes when its save is already :term[in flight]{id=in-flight}: the export remembers that save and waits for it later. The folder check lives in its own function, `CheckExportDirectory`.

The check refuses an empty path, and a path that starts with two slashes, which is a network or device path. It also refuses a relative path, a part named like a Windows device (`con`, `nul`, `com1`), a folder inside the project and a path that is a file. The inside-the-project rule has a reason: the next export would pack the first export as part of the project.

Then come the runtime and its notices. Both must sit beside the editor program, or `Start` fails with the target to build. After them, `ReadRunningScriptModule` returns the script module exactly as the editor loaded it, and fails when it changed on disk since. Then the loading scene, the :term[settings sections]{id=settings-section-world}, the title and the icon's source: each fails with a message that names the command that fixes it, such as `project.setGameInfo`.

Four decisions of `Start` look small and cost a bug if you miss them:

1. Without a start scene in the project file, the open scene is the start scene. Only when neither exists does the export fail.
2. The loading scene may not be the start scene. The game plays the loading scene while the start scene loads, so using one scene for both would start it twice.
3. A pruned pack keeps the loading scene and every asset that a settings section names, as if they were in `AlwaysInclude`. A section that names an asset the project lacks fails the export, because the game would otherwise start with a missing asset. :term[Built-in assets]{id=built-in-asset} are skipped, since every game has them.
4. The manifest's window (1280 by 720 and windowed) comes from the export's options and not from a project setting. The manifest's `VSync` field keeps its default, on.

The settings sections go into the manifest as stored, after `Validate` accepts them. A section that a module of this build claims must be valid, or the game would refuse to start. A section that no module claims travels unchanged.

### Waiting for imports and saves

After `Start` the state is `WaitingForImports`. The next quote is the first part of `Update` that waits.

```cpp src="StrataEditor/src/Editor/GameExport.cpp#L352-L372"
// Finished imports are applied by the asset manager's update, which runs every frame.
if (m_Assets->HasPendingImports() || (m_Saver && m_Saver->IsBusy()))
	return;
if (m_AwaitedSave != 0)
{
	// Kept statuses outlast the saves an export waits for, unless dozens more ended meanwhile: then it is unknown.
	const std::optional<DocumentSaveStatus> save = m_Saver->GetStatus(m_AwaitedSave);
	if (!save || save->State != DocumentSaveState::Done)
	{
		{
			std::scoped_lock<std::mutex> lock(m_Shared->Mutex);
			m_Shared->Ended = true;
			m_Shared->Outcome = GameExportState::Failed;
			m_Shared->Error = fmt::format("The scene's save failed, so the export would hold the file from before it ({})",
				save ? save->Error : std::string("its outcome is no longer known"));
		}
		Collect();
		return;
	}
	m_AwaitedSave = 0;
}
```

1. **Lines 353–354:** a busy asset manager or `DocumentSaver` returns at once, so the frame never waits.
2. **Lines 358–359:** the export finds the awaited save and fails unless it ended `Done`.
3. **Lines 362–367:** the failure is written under the mutex as the outcome, then `Collect` ends the export.
4. **Line 371:** once the save succeeded, the export forgets it and plans.

Each frame the export asks the asset manager and the `DocumentSaver`. While either is busy it returns and tries again next frame: no frame waits. Once they are idle, the export finds the awaited save. If it is not `Done`, the export fails with a message that says the pack would hold the file from before the save. That is the check that makes "save in flight counts as saved" safe.

Next comes a scan. Some documents changed on disk after their reference search was due, and waiting for the search to settle could take long. The export scans them itself on an I/O job (`FindDocumentReferences`), then records the results with `RecordScannedReferences` on the main thread. A pruned pack needs these references to know what each scene uses. So the export does not poll for the usual searches: it finishes the work now, with a job it owns.

### Cooking worlds

`BeginCooking` starts a `WorldCook` for every world of the project, including worlds cooked before: a world already cooked costs only a look at the stamps of its cells. If there is none, the state moves straight on. Otherwise the state is `CookingWorlds`, and each frame polls the cooks. A world's save writes its World document after its cells, so the export also waits while the `DocumentSaver` is busy, and restarts a cook whose world document changed meanwhile.

When every cook succeeded, `FinishCooking` writes the results. The next quote shows the two things it writes.

```cpp src="StrataEditor/src/Editor/GameExport.cpp#L509-L521"
std::vector<uint8_t> before;
std::string error;
if (!AssetEdit::ReadDocument(*m_Assets, cook->GetWorld(), before, &error))
	return fail(fmt::format("The world '{}' cannot be read: {}", path, error));
const std::string text = JsonUtils::Dump(WorldAsset::ToDocument(cook->GetCookedData()), 1, '\t') + "\n";
const std::vector<uint8_t> after(text.begin(), text.end());
if (before != after && !AssetEdit::ApplyDocument(*m_Assets, cook->GetWorld(), after, &error))
	return fail(fmt::format("The cooked index of the world '{}' cannot be written: {}", path, error));
if (const AssetHandle persistent = cook->GetCookedData().PersistentScene; persistent.IsValid())
{
	uint32_t& capacity = m_WorldCapacities[persistent];
	capacity = std::max(capacity, cook->GetReport().RecommendedMaxBodies);
}
```

1. **Lines 509–514:** the export reads the stored document and builds the text the cook produced.
2. **Lines 515–516:** it applies the new text only when it differs, so unchanged worlds write nothing.
3. **Lines 517–520:** a :term[persistent scene]{id=persistent-scene} keeps the largest capacity any cook recommended.

The cooked index is derived data, so it is written like an import's result: into the document, with no undo step, and only when it differs from what is stored. A second export of an unchanged world therefore writes nothing. The physics room is the second product. Each :term[persistent scene]{id=persistent-scene} gets the largest `RecommendedMaxBodies` among the cooks that name it. The cook itself, and why a world needs this number, are the subject of [Worlds meet physics and scripts](physics-scripts.md).

### Planning once

`Begin` calls `PlanAssetPack` once, on the main thread, and fails the export with the planner's error if it fails. It adds up the stored sizes of the planned assets (each counts at least one byte, so an empty asset still moves the bar). It adds the script module's size and the runtime's size, and stores the total. The state becomes `Packing`. Then it copies everything the job needs into a `JobData` and submits the job.

Pruning, ordering by first use and :term[cooked documents]{id=cooked-documents} belong to the plan: see [asset packs](../assets/packs-export.md). Pruning stays off unless you ask for it. Scripts can load assets by path, and no scene shows that. A game that does so from a pruned pack loses the asset, and `AlwaysInclude` names what to keep.

### The I/O job: fail before writing

The job's first act is a check: if the project has no script module, no packed scene or :term[prefab]{id=prefab-world} may use scripts. Then it does the two slow things that can fail, in memory and before the pack exists.

```cpp src="StrataEditor/src/Editor/GameExport.cpp#L596-L631"
std::optional<GameIcon::Images> icon;
std::optional<std::vector<uint8_t>> iconPNG;
if (!data->IconSource.empty())
{
	std::string iconError;
	icon = GameIcon::ConvertFile(data->IconSource, &iconError);
	if (icon)
		iconPNG = GameIcon::EncodePNG(icon->GetLargest(), &iconError);
	if (!iconPNG)
		return end(GameExportState::Failed, fmt::format("{} (set another icon or none with project.setGameInfo)", iconError));
	result.Warnings = icon->Warnings;
}
#if defined(ST_PLATFORM_WINDOWS)
// A Windows game shows its version and icon in Explorer, the taskbar and its window from its executable's
// resources: the runtime is stamped in memory (Editor/PEResources) and written once at the end. Stamped before the
// pack is written, so that a runtime the stamp refuses (signed, or laid out otherwise) fails the export before it
// writes anything, rather than after the pack, next to an executable of an earlier export.
std::optional<std::vector<uint8_t>> executable;
if (options.IncludeRuntime)
{
	const std::optional<std::vector<uint8_t>> runtime = FileSystem::ReadBytes(data->Runtime);
	if (!runtime)
		return end(GameExportState::Failed, fmt::format("Could not read the runtime '{}'", FileSystem::ToUTF8(data->Runtime)));
	PEResources::GameVersionInfo version;
	version.Title = data->Manifest.GetDisplayTitle();
	version.Version = data->Manifest.Version;
	version.Company = data->Manifest.Company;
	version.Copyright = data->Manifest.Copyright;
	version.InternalName = data->Manifest.Name;
	version.OriginalFilename = GetExecutableFileName(data->FileName);
	std::string stampError;
	executable = PEResources::StampGame(*runtime, version, icon ? &*icon : nullptr, &stampError);
	if (!executable)
	{
		return end(GameExportState::Failed, fmt::format("Could not write the game's version and icon into the runtime '{}': {}",
			FileSystem::ToUTF8(data->Runtime), stampError));
```

1. **Lines 598–605:** the icon is converted and encoded in memory; a bad image ends the export here.
2. **Lines 616–618:** the runtime is read into memory before anything is written.
3. **Lines 627–631:** the stamp runs in memory too, and a refusal ends the export before the pack exists.

The icon is decoded and re-encoded as a 256-pixel PNG first: an image that does not decode fails here, with advice to set another icon.

On Windows the runtime is then read and stamped in memory with the game's version and icon. A runtime that the stamp refuses (already signed, or laid out in another way) fails now.

The reason is the folder. If the pack were written first, a late failure would leave a new pack beside the old :term[executable]{id=executable} of the last export, and the two would not match. Doing the fragile work first means a failed export changes nothing. The versions and icons themselves belong to the identity of the game.

After that the order is fixed. The pack is written with cooked documents. The `AdjustSceneSettings` hook raises the packed persistent scene's :term[physics capacity]{id=capacity} to the cooked value when the saved one is lower. A world therefore never starts with less room than its cook found. When the pack is done, the state becomes `Copying`.

The script module goes out next, byte for byte as loaded, under its own file name, which the manifest records in `ScriptModule`.

Its program database (PDB) file, which holds debugging symbols, follows when it exists, unless `includeScriptSymbols` is false, its default in :term[Dist]{id=dist} builds.

Then the icon, the manifest, the executable (the stamped bytes on Windows, a copy with execute permission elsewhere) and `ThirdPartyNotices.md`. On a Linux host a `.desktop` entry comes last, so that a desktop can list the game.

Every write checks its result and ends the job with a message that names the file. The job catches exceptions from libraries at its edge, because Strata's own code does not throw. `Collect` then moves the outcome to the main thread under the mutex and logs one line.

## The folder it leaves

For a project named Coin the folder holds these files. Each has a check that protects it.

| File | What reads it | Check that guards it |
| --- | --- | --- |
| `Coin.exe` (`Coin` elsewhere) | The player starts it | The runtime exists; the stamp is accepted |
| `Coin.stgame` | The runtime, to learn the start scene and settings | The settings validate; the title is usable |
| `Coin.stpak` | The runtime's asset :term[loader]{id=loader} | The plan succeeds; the settings name only assets of the project |
| The script module | The runtime, named by `ScriptModule` | The module is unchanged since it loaded |
| Its PDB | Debuggers | None; omitted by default in Dist |
| `Coin.png` | Desktops and the manifest's icon entry | The icon decodes |
| `ThirdPartyNotices.md` | People | The file sits beside the runtime |
| `Coin.desktop` (Linux hosts) | A Linux desktop | The entry text builds, else a warning |

The file names come from the project name: letters and digits stay, spaces, dashes and underscores stay, and every other character becomes an underscore. An empty result becomes `Game`.

## Driving it from commands

An agent needs no dialog. `project.export` takes `directory` and options, and it answers when the export ends. Check progress with `project.exportStatus`, stop it with `project.cancelExport`, and set the loading scene and the always-included assets with `project.setExportSettings`. The title, version, company and icon go through `project.setGameInfo`, and the start scene through `project.setStartScene`. Commands are explained in [commands](../make/commands.md); the whole walk-through is in [exporting a game](../make/export.md).

```sh
StrataCLI project.exportStatus
```

The reply lists `running`, `state`, `progress`, `stage` and `directory`. Before the first export, `state` is null.

## What the export does not do

The export copies the runtime that sits beside the editor, so it makes games only for the platform the editor runs on. It makes no macOS app bundle, does not sign the game and does not install the Linux desktop entry it writes. The engine's plans list these as later work.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A separate build tool that reads the project from disk | Unreal's cook run as a command, Unity batch mode | Runs without an editor; simple to run on a build server | Loses the editor's open imports and loaded module; a second code path to keep right |
| Blocking the editor until done | Many small tools | Fewer states, no shared numbers | A frozen window for the length of the pack |
| Writing straight into the output folder | Simple scripts | No stage for planning | Half-new folders after a failure |
| One platform target per export | Unity, Unreal | Games for other systems | A cross-compiled runtime for each, signing and packaging per system |
| Copying every asset, never pruning | Strata's default | Scripts can load anything by path | A bigger pack than the game needs |

## How it is tested

The `Editor.Export` suite in `StrataTests/src/Editor/EditorExportTests.cpp` runs exports against a harness project. One case checks that an export runs over frames on an I/O thread and reports progress every frame. Another covers cancellation and closing a project. Others check that a scene saved meanwhile is named in the failure.

One checks that a document rewritten on disk meanwhile is scanned and not waited for. Another checks that pruned exports keep what `AlwaysInclude` and the settings name.

A case writes the manifest and checks the 256-pixel icon. The case `Export directories are checked before anything is written, with what to do instead` feeds each bad folder to `project.export` and checks both the message and that nothing appeared on disk.

`Editor.Export.GameIcon` covers the icon conversion, and `StrataTests/src/Editor/WorldGameExportTests.cpp` exports a world project and starts the result.

Run them together, on a build of the pin:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Export*
```

The runner prints the cases that fail with their file and line, and ends with a count of passed cases.

## Changing it safely

To add a check, ask what it needs. If it needs only the project's state in memory, it belongs in `Start`, with a message that names the fix and a case in `Editor.Export` that proves nothing was written. If it needs finished imports or saves, it belongs in the waiting part of `Update`. If it needs file contents that may be slow to read, it belongs on the I/O job, and before the first write. When in doubt, ask which state the failure should be reported in: the earlier, the better for the person.

A few rules of the engine apply, each with a reason. Commands never block a frame, so a long step returns a deferred result: `project.export` is registered with `MayDefer`. Saves never run on the main thread, so the export waits for them and does not run them. Assets are named by handle, and the plan, not the I/O job, resolves them. A change to the pack's format extends the pack's corruption tests.

Before you commit, run `Editor.Export*`, which also holds the world export case, and the package tests if you added a file to the folder, since a file a release ships needs an install rule.

## Summary

- An export moves through `WaitingForImports`, `CookingWorlds`, `Packing` and `Copying` to `Succeeded`, `Failed` or `Cancelled`. The main thread checks, waits, cooks and plans; one I/O job writes.
- `Start` runs every check that needs no files and fails without side effects. Its order is the order of the page.
- The icon is decoded and the executable stamped before the pack is written, so a failed export never leaves a pack beside an old executable.
- The folder holds the game's program, `.stgame`, `.stpak`, the script module and its PDB, the icon PNG, the notices and, on Linux, a desktop entry. Each file has a check.
- A new check goes into the earliest state that has what it needs.

## Check yourself

1. A project has no start scene set, and the open scene is saved. What does `Start` do?

   - A. It fails: the project has no start scene.
   - B. It uses the open scene as the start scene.
   - C. It picks the first scene in the asset folder.

   :::answer{tests="name-checks"}
   B. The open scene becomes the start scene. A is wrong because the export fails only when neither exists, and C is wrong because Strata never guesses a scene by name.
   :::

2. The icon file in a project is a broken image. In which state does the export fail, and what is on disk afterwards?

   :::answer{tests="fail-first"}
   The export fails in `Packing`, as the first action of the I/O job, before the pack is written. Nothing new is on disk. The export folder exists, because `Start` created it, but it holds no new file.
   :::

3. Which thread writes the pack, and which thread plans it?

   :::answer{tests="trace-states"}
   One I/O job writes the pack; the main thread plans it, once, when no import or save is pending.
   :::

4. A pruned export of a game whose script loads `Sounds/Boom.wav` by path ships without the sound. Why, and what is the fix?

   :::answer{tests="name-folder"}
   No scene names the sound, so pruning omits it. Add the file to `AlwaysInclude` with `project.setExportSettings`. The default, no pruning, would have shipped it.
   :::

5. Where would you put a check that the project's title has no forbidden letters?

   :::answer{tests="add-check"}
   In `Start`, next to the title check that exists, because the title is in memory and needs no file. The export then fails with no side effects.
   :::

## Exercises

1. **Basic.** A pack of three assets stores 1 MB, 5 MB and 4 MB. The script module is 0.5 MB and the runtime 9.5 MB. What is `TotalBytes`, and what does the stage say when 5 MB are done?

   :::answer[Worked solution]{tests="trace-states"}
   The pack adds 10 MB and the copies 10 MB: the total is 20 MB. At 5 MB done, the stage reads "Packing 3 assets (5 of 20 MB)", and the progress is 25 %.
   :::

2. **Medium.** Trace it yourself: find where an export leaves `WaitingForImports`, and list the up-front checks of `Start` with their messages. Use a breakpoint in `GameExport::Update` and a search for `fail(` in `StrataEditor/src/Editor/GameExport.cpp`.

   :::answer[Worked solution]{tests="name-checks"}
   `GameExport::Update` leaves the waiting state by calling `BeginCooking` and then `Begin`. A search for `fail(` in `GameExport::Start` lists the checks in the order of this page. They are: no project, playing, a scene not saved, the export folder, start scene, runtime, notices, script module, loading scene, settings, title, icon, assets the settings name, always-included assets. Last, it creates the folder.
   :::

3. **Hard.** The folder check of the sketch below refuses `/games/CoinBuild` because it starts with the project's name. Fix it so that only whole path parts count, and print five cases.

   :::answer[Worked solution]{tests="add-check" solution="sketches/worlds-export-directory.cpp"}
   Compare the whole path or the project's path followed by a slash.

   ```cpp sketch="worlds-export-directory.cpp"
   // Exercise: the first rules of an export directory check, in the order the engine applies them.
   #include <cstdio>
   #include <string>

   // Returns an empty string when the directory is usable, or the reason it is not.
   std::string CheckDirectory(const std::string& directory, const std::string& project)
   {
   	if (directory.empty())
   		return "Choose the directory to export the game to";
   	if (directory.size() >= 2 && directory[0] == '/' && directory[1] == '/')
   		return "a network or device path";
   	if (directory[0] != '/')
   		return "not an absolute path";
   	// Whole path parts only: "/games/CoinBuild" lies beside the project, not inside it.
   	if (directory == project || directory.rfind(project + "/", 0) == 0)
   		return "inside the project";
   	return "";
   }

   int main()
   {
   	const std::string project = "/games/Coin";
   	const char* directories[] = { "", "//server/share", "Build", "/games/Coin/Build", "/games/CoinBuild" };
   	for (const char* directory : directories)
   	{
   		const std::string reason = CheckDirectory(directory, project);
   		std::printf("'%s': %s\n", directory, reason.empty() ? "usable" : reason.c_str());
   	}
   	return 0;
   }
   ```

   ```text output-of="worlds-export-directory.cpp"
   '': Choose the directory to export the game to
   '//server/share': a network or device path
   'Build': not an absolute path
   '/games/Coin/Build': inside the project
   '/games/CoinBuild': usable
   ```

   1. **Lines 10–11:** two leading slashes mean a network or device path.
   2. **Lines 14–16:** the project's path must be followed by a slash, so `/games/CoinBuild` lies beside the project.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/GameExport.h` and `StrataEditor/src/Editor/GameExport.cpp`: the class, `CheckExportDirectory`, the state machine.
- `StrataEditor/src/Editor/EditorAssetCommands.cpp`: `project.export` and its companions.
- `StrataTests/src/Editor/EditorExportTests.cpp` and `StrataTests/src/Editor/WorldGameExportTests.cpp`: the suites.
- Commands: `project.export`, `project.exportStatus`, `project.cancelExport`, `project.setExportSettings`, `project.setGameInfo`, `project.setStartScene`.

## Further reading

- Unity manual, "Build Settings": the player build (beginner).
- Unreal Engine documentation, "Cooking content and creating pak files": the cook and pak steps (intermediate).
