---
id: editor/play-mode
title: "Play mode: the running copy"
description: "How the editor plays a copy of your scene, what it keeps and discards, and how a game's quit, scene switch and crash reach the editor."
kind: internals
size: L
tracks: [E]
needs: [editor/deferred-commands, editor/undo, scripting/script-system]
time: 80
learn:
  - id: why-copy
    text: explain why Strata plays a copy of the edited scene instead of saving and reloading it or starting a second process
  - id: start-stop
    text: trace what Play copies, resets and restores, and what Stop discards, in order
  - id: which-scene
    text: predict for a command whether it acts on the edited scene or the running copy and what its result says
  - id: requests
    text: explain what the editor does when a running game quits, switches scenes or crashes
  - id: game-shell
    text: name the game services the editor stands in for and where saves and players' options go
since: 0.3.0
status: final
---

When you press Play, the editor must answer three questions at once. Where does the game run, so that the scene you built stays as it was? What does the game see of the editor around it, such as its window, its cursor and its speakers? And who decides when the game is over? **Play mode** is the editor's answer: it runs a copy of your scene with scripts, physics and audio, and returns to the original when you stop.

This page covers the code that starts, runs and stops that copy. It does not cover pausing and stepping, building scripts before Play, or how the Game view draws. Those have pages of their own, linked where they meet this one.

## The problem and how engines solve it

Think of a designer who builds a small level: a floor, a crate, a sun, a player. She presses Play to try it. In the game, a script moves the crate, a physics body falls off the floor, and the player collects three coins that vanish from the scene. When she presses Stop, she expects the level exactly as she left it: the crate where she put it, the coins back, the sun at its angle. If any of that is lost, she can never trust a test run, because every run costs her some of her work.

Now add three more demands. The game may ask to go fullscreen, but the editor must keep its window. The game may hide and lock the mouse cursor, but the editor must give it back. The game may set its volume to 20 %, but the editor's own sounds must not stay quiet afterwards. The game is a guest inside the tool, and a guest must leave things as it found them.

Engines meet these demands with three approaches, and each has a price. The first duplicates the world in memory: the editor builds a second copy of the scene's data and runs the game on it. Unreal Engine's play in editor works this way, as its documentation describes. The cost is memory and time, since a scene of a million entities exists twice and the copy must be built before the first frame. The gain is speed of return, because discarding the copy is a matter of freeing memory.

The second approach saves and reloads. The editor stores the scene's state, lets the game change the live objects, and restores the stored state at the end. Unity's play mode follows this idea, as its manual on entering play mode describes. The cost is that the restore must bring back everything the game could have touched, and anything the storage format forgets is lost. The gain is that no second copy sits in memory.

The third approach runs the game as a separate process. The editor starts the game program, which loads the saved scene from disk. Godot runs your project this way. The cost is that the game sees only what was saved, so edits not yet saved do not play unless the editor saves first. The gain is isolation: a crash in the game cannot take the editor down, and the game cannot touch the editor's window at all.

Strata chooses the first approach. Playing starts from the scene as it is on screen, changes not yet saved included, which rules out the third. Strata's scenes also hold things a store-and-restore would have to track: physics bodies, audio voices and script instances, which makes the second approach fragile. A copy has a simple promise: the original is never touched, because the game never holds a reference to it.

:::elsewhere
Unreal Engine duplicates the world for play in editor, Unity stores and restores the scene around play mode, and Godot starts the game as another process. Each project's documentation lists the exact behavior; the names of those pages are under Further reading.
:::

The scene you edit, with its undo history, is the **edited scene**.

The scene that play mode builds from the edited scene and runs is the **running copy**.

Four more rules follow from the choice of a copy. Commands act on the running copy while it plays. Edits to it are not recorded for undo, and they are gone after Stop. The game's requests to its window are recorded instead of applied.

## The map

The editor is in one of three states, the values of `SceneState`: `Edit`, `Play` and `Simulate`.

**Play** starts the full game on the copy: scripts, physics and audio.

**Simulate** starts the copy with only the systems that declare they run in it, which means physics and the streaming of a world's cells.

**Simulate mode** is the state that follows, used to watch physics settle or to test a scene before any script exists.

```mermaid caption="The editor is in one of three states. Play and Simulate each start from Edit, and Stop, a quit or a crash returns to Edit." alt="A state diagram with three states: Edit, Play and Simulate. Arrows lead from Edit to Play and to Simulate, and an arrow from each of them back to Edit."
stateDiagram-v2
	[*] --> Edit
	Edit --> Play: Play
	Edit --> Simulate: Simulate
	Play --> Edit: Stop, quit or crash
	Simulate --> Edit: Stop
```

The diagram has one rule worth reading twice: there is no arrow from Play to Simulate. You stop first, so every session starts from the edited scene. Play mode never continues from the state of a previous run.

The code lives in `StrataEditor/src/Editor/`. `EditorContext` owns both scenes, the state and the session counter. The `play.*` commands in `Commands/PlayCommands.cpp` call into it. `CommandUtils` holds the helpers that mark an edit as one of the running copy. `EditorGameWindow` records what the game asks of its window.

```mermaid caption="Commands act on whichever scene is active. The game never touches the editor directly: its requests wait in the running copy and the editor reads them after each update." alt="A flow diagram. Commands go to the active scene, which is the running copy while playing and the edited scene otherwise. The game's window requests go to a recorder, and its quit and scene switch requests go to the editor after each update."
flowchart LR
	C[Commands] --> A{Active scene}
	A -->|playing| R[Running copy]
	A -->|editing| E[Edited scene]
	R --> G[Game: scripts, physics, audio]
	G -->|window requests| W[Recorded, not applied]
	G -->|quit, scene switch| Q[Read after each update]
	Q --> S[Stop or swap the copy]
```

Two views show the result, and the next figure puts them side by side. The Scene view draws through the editor's camera, which you move to look around. The Game view draws through the scene's :term[primary camera]{id=primary-camera}, which is what a player would see. The Game view's resolution and focus rules are the subject of [the Game view](../editor-ui/game-view.md).

::figure{id=scene-and-game-view}

## The contract

Code that calls into play mode, and commands that run while it is on, follow a few rules. Each has a reason, and the reasons are what you need when you change the code.

The **active scene** is the scene commands work on: the running copy while play mode runs, and the edited scene otherwise. `EditorContext::GetActiveScene` returns the right one, and a command that edits entities reads it instead of asking for the edited scene. A command that always chose the edited scene would change something the person cannot see while the game plays, and one that always chose the copy would break editing. One accessor makes the choice in one place.

The **Game view** is the editor panel that shows the game through the scene's primary camera. It is the window the game believes it plays in.

Edits to the running copy are never recorded. :term[Undo steps]{id=undo-step} describe changes to the edited scene, and a step that described a scene Stop deletes would point at nothing. So `EditorContext::CommitEdit` does nothing while playing, and undo and redo refuse with the message that they are not available while the scene is running. When play starts, the editor also breaks any run of merged undo steps, so a drag that began before Play cannot continue into a step after it.

Every result tells the truth about this. A scene command that changes something while the scene plays adds a `warning` to its result and marks the result as one of the running copy. People and agents read that warning and learn that the change will vanish. A recorded session replays the editing steps again, and a change to a running copy must not be replayed into the edited scene, so the mark also keeps those steps out of a replay.

:::rule
Every change to the scene goes through a command, and a command's result must be exact about what it did. A change that only lasts until Stop says so in its result. The engine's developer guide states it in its section on edits while playing.
:::

Settings are the exception. A change to the project's settings belongs to the project and stays after Stop, so such commands carry neither the warning nor the mark. A few commands whose only target is the running game, such as `scene.loadAdditive`, set the mark without the warning, since the warning would only repeat what the command is for.

The game must never reach the editor's state. Its requests go through services that the editor provides in place of the real ones; the section on the game shell shows them. The editor reads the game's requests only between updates, on the :term[main thread]{id=main-thread}, so no game code runs while the editor changes the scene it plays.

Finally, a session leaves nothing behind. Start resets the simulated input, the players' options and the shell. Stop does the same, restores the master volume, and forgets the selection of entities the game created. The next section builds a model that keeps these rules.

## A toy version

A model of play mode needs only a few parts: a scene, a copy, a flag for whether the game runs, an undo counter and a volume. The toy below holds a list of lights as its scene. It copies the edited scene on Play, lets commands act on whichever scene is active, refuses to record undo steps while playing, and puts the volume back on Stop.

:::question
The sketch uses classes, `std::vector` and `std::optional`. If they are new, read [classes](../basics/programming-3.md) and [vectors](../basics/programming-2.md), and [optional values](../basics/cpp-modern.md), first.
:::

The sketch has a `Scene` that holds lights and a `ToyEditor` that holds two of them. Search for the single line that builds the copy, the function that decides which scene a command changes, and the place where Stop undoes everything the game did.

```cpp sketch="editor-play-mode-toy.cpp"
#include <cstdio>
#include <optional>
#include <utility>
#include <vector>

struct Light
{
	float Intensity = 3.0f;
};

struct Scene
{
	std::vector<Light> Lights;
};

class ToyEditor
{
public:
	explicit ToyEditor(Scene scene)
		: m_EditScene(std::move(scene))
	{
	}

	bool IsPlaying() const { return m_RuntimeScene.has_value(); }
	size_t GetUndoSteps() const { return m_UndoSteps; }
	float GetMasterVolume() const { return m_MasterVolume; }
	void SetMasterVolume(float volume) { m_MasterVolume = volume; }
	const Scene& GetEditScene() const { return m_EditScene; }

	// The scene that commands act on: the running copy while it exists, else the edited scene.
	Scene& GetActiveScene() { return m_RuntimeScene ? *m_RuntimeScene : m_EditScene; }

	bool Play()
	{
		if (IsPlaying())
			return false;
		m_VolumeBeforePlay = m_MasterVolume;
		m_RuntimeScene = m_EditScene; // The copy: from here on the two scenes share nothing
		return true;
	}

	void Stop()
	{
		m_RuntimeScene.reset(); // Everything the game did to its copy goes with it
		m_MasterVolume = m_VolumeBeforePlay;
	}

	// A command that sets a light's intensity. Edits are recorded for undo; edits of the running copy are not.
	const char* SetIntensity(size_t index, float intensity)
	{
		GetActiveScene().Lights[index].Intensity = intensity;
		if (IsPlaying())
			return "warning: applies to the running copy and is discarded by Stop";
		m_UndoSteps++;
		return "ok";
	}
private:
	Scene m_EditScene;
	std::optional<Scene> m_RuntimeScene;
	size_t m_UndoSteps = 0;
	float m_MasterVolume = 1.0f;
	float m_VolumeBeforePlay = 1.0f;
};

int main()
{
	ToyEditor editor(Scene { { Light {} } });
	std::printf("edit:  %s\n", editor.SetIntensity(0, 5.0f));
	editor.Play();
	editor.SetMasterVolume(0.2f); // The game's own volume setting
	std::printf("play:  %s\n", editor.SetIntensity(0, 20.0f));
	std::printf("running copy %.1f, edited scene %.1f\n", editor.GetActiveScene().Lights[0].Intensity, editor.GetEditScene().Lights[0].Intensity);
	editor.Stop();
	std::printf("stopped: intensity %.1f, undo steps %zu, volume %.1f\n", editor.GetActiveScene().Lights[0].Intensity, editor.GetUndoSteps(),
		editor.GetMasterVolume());
	return 0;
}
```

```text output-of="editor-play-mode-toy.cpp"
edit:  ok
play:  warning: applies to the running copy and is discarded by Stop
running copy 20.0, edited scene 5.0
stopped: intensity 5.0, undo steps 1, volume 1.0
```

1. **Line 31:** the one place that decides which scene a command changes.
2. **Line 38:** the copy; from here on the two scenes share nothing.
3. **Lines 44–45:** Stop drops the copy and puts the volume back.
4. **Lines 52–55:** an edit of the copy returns a warning and records no undo step.

The output shows the whole contract in four lines. The edit before Play recorded an undo step and set the intensity to 5.0. During play the game changed its own volume and a command set the intensity to 20.0, but the result carried a warning, and no step was recorded. After Stop the edited scene still holds 5.0, the undo count is still one, and the volume is back at 1.0.

The toy omits most of what makes the real code long. It has no entities with identities, no physics, no audio and no files. It never asks whether a scene is still loading. It has no game requests, and the game never runs a frame. The real code adds those, and the rest of this page names each difference.

## The real code

Play mode lives in `EditorContext`. The order below follows the data: the call that starts play, the start, the frames that run, what a frame reads from the game, the crash path, the end, and the commands on top.

### Play

`Play` is the entry the person's button reaches. It refuses first and starts second. If the script engine holds a crash from an earlier run, the module stays disabled until the person builds or reloads it, so `Play` fails with a message that names both commands. Otherwise it makes this engine the active one, because scenes use the script engine that is active when they start, and calls `StartRuntime`. Search for the last check: a crash while scripts start (:term[constructors]{id=constructor} and `OnCreate`) ends play before it began.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1331-L1356" symbol="EditorContext::Play"
bool EditorContext::Play(std::string* outError)
{
	auto fail = [outError](std::string message)
	{
		if (outError)
			*outError = std::move(message);
		return false;
	};

	if (m_ScriptEngine)
	{
		if (std::optional<ScriptFault> fault = m_ScriptEngine->GetFault())
		{
			return fail(fmt::format("The script module crashed earlier ({}: {}); it stays disabled until it is rebuilt (script.build) or reloaded "
				"(script.reload)", fault->ClassName.empty() ? fault->ModuleName : fault->ClassName + "::" + fault->Method, fault->Description));
		}
		// Scenes use the engine that is active when they start.
		ScriptEngine::SetActive(m_ScriptEngine);
	}
	if (!StartRuntime(SceneRuntimeMode::Play, outError))
		return false;
	// A crash while the scripts start (constructors, OnCreate) ends play mode right away.
	if (StopOnScriptFault())
		return fail("A script crashed while the scene started; play mode was stopped (see the log or script.status)");
	return true;
}
```

1. **Lines 1342–1346:** a crash from an earlier run refuses Play and names the two ways back.
2. **Line 1348:** scenes use the script engine that is active when they start.
3. **Line 1350:** the start itself; its failure ends the function.
4. **Lines 1353–1354:** a crash while scripts start stops play at once and fails the call.

### `StartRuntime`

`StartRuntime` does the work of the start. Look at the order: the checks that can refuse come first, the copy next, then the resets, and the call that starts the scene comes before the state changes. The state only becomes `Play` or `Simulate` at the end, so a reader that asks "is the game running?" never sees a half-started game.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1363-L1409" symbol="EditorContext::StartRuntime"
bool EditorContext::StartRuntime(SceneRuntimeMode mode, std::string* outError)
{
	if (IsPlaying())
	{
		if (outError)
			*outError = fmt::format("The scene is already running ({})", SceneStateToString(m_SceneState));
		return false;
	}
	if (IsSceneLoading())
	{
		if (outError)
		{
			*outError = fmt::format("A scene is being opened ({}, {:.0f}%): play once it is open (scene.open answers then; scene.loadStatus)",
				m_SceneLoadStatus.Scene.ToString(), m_SceneLoadStatus.Progress * 100.0f);
		}
		return false;
	}
	m_UndoStack.BreakMerge();
	m_MasterVolumeBeforePlay = AudioEngine::GetMasterVolume();
	m_RuntimeScene = Scene::Copy(m_EditScene);
	// A world plays with the cells the editor has loaded (its edit radius), never the whole world: the game streams the
	// others around the play camera from their saved documents.
	const std::vector<WorldCellKey> pinnedCells = m_World ? m_World->PrepareRuntimeCopy(*m_RuntimeScene) : std::vector<WorldCellKey>();
	m_RuntimeSceneAsset = UUID::Null();
	m_PlaySession++;
	m_ReplacedFixedSteps = 0;
	m_FrozenInputFrames = 0;
	// Keys a tool held down in an earlier session (input.* commands) must not leak into this one.
	ResetSimulatedInput();
	ResetGameShell();
	// The bindings and graphics options players saved in an earlier session (the project's .strata/Saves), as an exported
	// game loads them.
	InputActions::LoadBindings();
	m_GameGraphics->LoadPlayerOptions();
	m_RuntimeScene->SetTimeDilation(m_Specification.TimeDilation);
	m_RuntimeScene->SetInterpolation(m_Specification.Interpolation);
	m_RuntimeScene->OnRuntimeStart(mode);
	// Cells with unsaved edits stay for the session: their documents on disk are older than what plays.
	if (WorldStreamingSystem* streaming = m_RuntimeScene->GetSystem<WorldStreamingSystem>())
	{
		for (const WorldCellKey& key : pinnedCells)
			streaming->PinCell(key);
	}
	m_SceneState = mode == SceneRuntimeMode::Play ? SceneState::Play : SceneState::Simulate;
	UpdateInputSuspension();
	return true;
}
```

1. **Lines 1365–1379:** both refusals come before anything changes, with messages that say what to do.
2. **Lines 1381–1382:** the volume is kept, then the copy is made.
3. **Lines 1391–1396:** simulated input, the shell, the players' bindings and the players' graphics options start clean.
4. **Line 1399:** the scene builds its systems and starts its scripts.
5. **Line 1406:** the state changes last, so no reader sees a half-started game.

The checks are two. A scene that already runs refuses a second start. A scene that is still opening refuses play, because the edited scene is about to be replaced and its copy would be a copy of the wrong scene. The error messages say what to do next, so an agent that reads them can recover.

The copy is `Scene::Copy`, the call [the scene systems page](../world/systems.md) describes. Strata keeps the master volume first, in `m_MasterVolumeBeforePlay`, because a game may set it. For a world, `PrepareRuntimeCopy` makes the copy hold only the cells the editor has loaded, and returns the cells that carry edits not yet saved. The game then streams the other cells in around its own camera from their saved documents, and those cells are pinned so that streaming never unloads what the person changed. [Worlds in the editor](worlds.md) covers that case.

The resets follow. `m_PlaySession` counts sessions, so a tool that waits for a step can tell that play restarted. The simulated input is cleared, because a key an automation command held in an earlier session must not leak into this one. `ResetGameShell` clears what the game asked of its window, and the code then loads the players' input bindings and graphics options from the project's saves, as an exported game would on its start.

:term[Time dilation]{id=time-dilation} and :term[interpolation]{id=interpolation} come from the editor's specification. Time dilation slows the game when fixed steps cannot match the clock, and interpolation draws motion between two poses ([time](../core/time.md) and [interpolation](../world/interpolation.md) explain both). `OnRuntimeStart` finally builds the scene's systems and runs the scripts' start, for `Play` or `Simulate`.

### Stop

`Stop` is shorter than the start, because discarding is cheaper than building. It cancels a scene load that is :term[in flight]{id=in-flight}, remembers the step count and session for tools that read them after the stop, and gives the copy to `Scene::ReleaseInBackground`. The scene stops on the main thread, but its memory is freed by a background job, so Stop does not take a frame for a large scene.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1411-L1433" symbol="EditorContext::Stop"
void EditorContext::Stop()
{
	if (!m_RuntimeScene)
		return;
	if (m_RuntimeSceneLoad)
	{
		m_RuntimeSceneLoad->Request.Cancel();
		m_RuntimeSceneLoad.reset();
	}
	m_FixedStepsAtStop = GetFixedStepCount();
	m_StoppedSession = m_PlaySession;
	// Stopped here and destroyed off the frame, like a replaced scene (ReplaceRuntimeScene).
	Scene::ReleaseInBackground(std::move(m_RuntimeScene));
	m_RuntimeSceneAsset = UUID::Null();
	m_SceneState = SceneState::Edit;
	// A game's volume setting belongs to the game session, not to the editor.
	AudioEngine::SetMasterVolume(m_MasterVolumeBeforePlay);
	m_GameInputActive = false;
	ResetSimulatedInput(); // The game that a tool's simulated input was meant for is gone
	ResetGameShell();
	UpdateInputSuspension();
	PruneSelection(); // Entities created during play are gone
}
```

1. **Lines 1415–1418:** a scene load in flight is cancelled with the game.
2. **Line 1423:** the copy leaves through the background release.
3. **Line 1427:** the volume returns to what Play kept.
4. **Lines 1429–1430:** simulated input and the shell reset again.
5. **Line 1432:** the selection drops entities the game made.

The line to notice is the one that restores the master volume, with its comment: a game's volume setting belongs to the game session, not to the editor. The game may have lowered it to 20 %, and Stop returns it to the value that `StartRuntime` kept. The last lines clear the game's input and shell again, and drop the selected entities that the game made, since they no longer exist.

### The frame

Each editor frame runs the loading work, then the copy's update, and then, if no script crashed, it reads the game's requests. A paused game still runs those steps; only its :term[fixed steps]{id=fixed-step} wait, a topic for [stepping](stepping.md). Both outcomes of the requests go through `HandleRuntimeRequests`.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L1435-L1448" symbol="EditorContext::HandleRuntimeRequests"
void EditorContext::HandleRuntimeRequests()
{
	if (const std::optional<int32_t> exitCode = m_RuntimeScene->GetQuitRequest())
	{
		ST_INFO("The game quit with exit code {}; play mode stopped", *exitCode);
		Stop();
		return;
	}

	const std::optional<UUID> request = m_RuntimeScene->TakeSceneLoadRequest();
	std::string error;
	if (request && !SwitchRuntimeScene(*request, &error))
		ST_ERROR("The game cannot switch scenes: {}", error);
}
```

1. **Lines 1437–1442:** a quit logs its code and stops play; nothing may use the copy afterwards.
2. **Line 1444:** the request is taken, so it is read once.
3. **Lines 1446–1447:** a failed switch logs an error and the game keeps running.

The function looks at two things. A quit request carries an :term[exit code]{id=exit-code}: the editor logs it, calls `Stop`, and returns, because everything after a stop would use a copy that is gone. A scene-load request names a scene asset, and `SwitchRuntimeScene` starts the load. A failure logs an error and leaves the running game as it is.

Where does a request come from? A script calls the :term[SDK's]{id=sdk} `Game::LoadScene` or `Game::Quit`. These reach host functions, which only record the request on the scene (`RequestSceneLoad` and `RequestQuit`), and the editor reads it after the update. The game never calls the editor, and the editor never runs while the game's code is on the stack. [The script system page](../scripting/script-system.md) describes the host side.

### Switching scenes

`SwitchRuntimeScene` does not freeze a frame. It starts a background load with `SceneLoader::LoadAsync`, asks that the scene's systems prepare it (physics bodies, for example), and returns. The running scene continues playing while the next one loads. Each frame, `UpdateRuntimeSceneLoad` spends part of the frame's budget on the load and sets the load's progress on the running scene, so a loading screen can read it. When the load is ready, `ReplaceRuntimeScene` swaps it in.

Four details matter. Asking again for the scene that already loads keeps that load, because scripts may ask in every update while a condition holds. Asking for another scene replaces the load in progress. A null handle restarts what runs: the scene switched to last, or else a fresh copy of the edited scene. And the swap keeps the mode: a game that was paused, with steps still to run, stays paused with those steps in the new scene.

The swap logs `Play mode switched to` the new scene's name and writes a journal event of the play group with the old and the new scene. Commands and agents then know which scene runs. `Stop` after a switch still returns to the edited scene, because the edited scene never changed. What a shipped game does on a switch is the subject of [scene switches in worlds](../worlds/runtime.md).

### A crash during play

A script that crashes does not take the editor down, because every call into script code is guarded ([crash containment](../scripting/crash-containment.md) shows how). The guard records a fault and the editor reacts in `StopOnScriptFault`, which runs after each update and also right after the start. Read the function for what the person sees: a log line, a toast, and the end of the session.

```cpp src="StrataEditor/src/Editor/EditorContext.cpp#L2644-L2670" symbol="EditorContext::StopOnScriptFault"
bool EditorContext::StopOnScriptFault()
{
	if (m_SceneState != SceneState::Play || !m_ScriptEngine)
		return false;
	std::optional<ScriptFault> fault = m_ScriptEngine->GetFault();
	if (!fault)
		return false;

	const std::string where = fault->ClassName.empty() ? fmt::format("module '{}' ({})", fault->ModuleName, fault->Method)
		: fmt::format("{}::{} on entity '{}' ({})", fault->ClassName, fault->Method, fault->EntityName, fault->Entity.ToString());
	const std::string location = fault->Symbolized && fault->Location ? " at " + DescribeScriptCodeLocation(*fault->Location) : std::string();
	ST_ERROR("Script crash in {}{}: {}. Play mode stopped; fix the script and rebuild (script.build) or reload it (script.reload)", where, location,
		fault->Description);
	// Symbolization runs on a job: its location is reported when it arrives (UpdateScriptFaultLocation).
	m_ScriptFaultLocationPending = !fault->Symbolized;
	EditorNotification notification;
	notification.Level = NotificationLevel::Error;
	notification.Title = "Script crash: play mode stopped";
	notification.Message = fmt::format("{}: {}", where, fault->Description);
	notification.ShowConsole = true;
	// The Problems panel leads with the crash: where it happened and the stack, once symbolized.
	notification.ShowProblems = true;
	m_Notifications.Post(std::move(notification));
	m_LastScriptFault = std::move(fault);
	Stop();
	return true;
}
```

1. **Line 2646:** only Play runs scripts, so only Play can stop for a crash.
2. **Lines 2652–2656:** the log line names the class, the :term[callback]{id=callback}, the entity and the way back.
3. **Line 2658:** symbolization is still pending, so the location arrives later.
4. **Lines 2661–2666:** the toast leads to the Problems panel and the Console.
5. **Line 2668:** the game stops through the same Stop as the button.

The function only acts in `Play`, since Simulate runs no scripts. It builds a description of where the crash happened: the class, the :term[callback]{id=callback} and the entity for a script, or the module for a crash outside any class. It logs an error that tells the person the way back, `script.build` or `script.reload`. It posts an error toast that leads to the Problems panel and the Console, where the details are. It keeps the fault, and then calls `Stop`.

The location in the :term[source file]{id=source-file} arrives later, because finding a file and line from a crashed address is work for a background job (see [symbolization](../scripting/symbolization.md)). `UpdateScriptFaultLocation` runs every frame, also outside play, and waits for that job. When the location is ready it logs a second line with the file and line, and it updates the stored fault so the Problems panel shows the stack. If the person reloaded the module meanwhile, the fault is gone and the function drops its wait. Until a rebuild or a reload, `play.start` fails with the message that `Play` builds at its first check.

### The commands

The `play.*` commands are small. `play.start` has two parameters: `build` (default true) and `paused` (default false). Without `build: false` it first asks whether the scripts need a build, because their sources changed or a scene uses scripts that are not loaded. If they do, it starts a build (or waits for the one that runs) and returns a deferred result, as [deferred commands](deferred-commands.md) describes: the poll checks each frame whether the build ended. A failed build fails `play.start` with its first errors and asks the user interface (UI) to show the Problems panel; [script builds](script-builds.md) covers the build itself.

With `paused: true`, `play.start` pauses the game right after `Play`, before any fixed step has run. Steps run in the frames' updates, never inside `Play`, so the game is paused at step 0. A tool that plays and steps the game can then see every step from the first. `play.simulate` and `play.stop` call `Simulate` and `Stop`.

Edits while playing leave through `FinishEdit`. Most scene commands end in it, which is how the warning reaches them all.

```cpp src="StrataEditor/src/Editor/CommandUtils.cpp#L435-L451" symbol="CommandUtils::FinishEdit"
EditorCommandResult FinishEdit(EditorContext& context, SceneEditTransaction& transaction, nlohmann::json value)
{
	if (std::string error; !context.CheckSceneEditable(&error))
	{
		transaction.Rollback();
		return EditorCommandResult::Fail(std::move(error));
	}
	context.CommitEdit(transaction);
	if (!context.IsPlaying())
		return EditorCommandResult::Ok(std::move(value));
	if (!value.is_object())
		value = nlohmann::json::object();
	value["warning"] = GetRunningCopyWarning(context);
	EditorCommandResult result = EditorCommandResult::Ok(std::move(value));
	result.RunningCopy = true;
	return result;
}
```

1. **Lines 437–441:** a scene that is being opened refuses the edit and rolls it back.
2. **Line 442:** the commit does nothing while playing.
3. **Lines 443–444:** outside play, the value returns unchanged.
4. **Line 447:** the warning joins the result.
5. **Line 449:** the mark tells the journal that this is a change of the running copy.

The function checks that the scene can be edited, commits the transaction (which does nothing while playing, as the contract says), and returns the command's value unchanged when the editor edits. While playing, it makes sure the value is an object, adds `warning` with the text from `GetRunningCopyWarning`, and marks the result as one of the running copy. The text names the state and the remedy: "this change applies to the running copy and is discarded by play.stop".

### The game shell

The game was written to run in a window, with saves and options of its own. In the editor it plays in the Game view, so the editor provides the services the game would find in an exported program. That set is the **game shell**: the services the editor provides to the running copy in place of the real window, the real save folder and the real player settings.

`EditorGameWindow` provides the window. When the game asks for fullscreen, for a resolution or for :term[vsync]{id=vsync}, the shell records the request and does not apply it. The editor's window keeps its size and mode, though the Game view can render at a requested resolution when you choose that.

The editor reports the request in `editor.status` and as a notice over the Game view, so a person sees that the game asked. A request equal to the last one changes nothing and is not logged again, because some games apply their options every frame. The requests are forgotten when play starts and when it stops.

The cursor gets the same care. A game that hides and locks the cursor does so in a mode the editor owns; `ResetGameShell` returns the cursor to normal on both ends of a session. The input actions' session state (map enables, simulated actions, players' bindings) and the game's graphics options are reset the same way, so one session's changes do not reach the next.

Saves go to the project, in `.strata/Saves`. The game asks the save service for a folder, and the editor answers with the `Saves` folder inside the open project's `.strata` folder, or with nothing when no project is open. The same folder holds the players' bindings file and `GraphicsOptions.json`, which `StartRuntime` loads at each start. A game therefore keeps its saves between runs in the editor, but a save never lands in your content, and your edited scene never changes because a game saved.

## An example: change a light while playing

The example plays a project whose scene has a directional light entity named `Sun`. A directional light's intensity defaults to 3.0 lux. You will edit it, play, edit it again, stop, and check what is left. Each command is the :term[JSON]{id=json} an agent sends; a person does the same with the Inspector.

:::example
First the edit before play. The `entity` parameter takes an entity's identifier, and `5A1C93E07B2D4F18` stands here for the one that `entity.find` returns for `Sun`. The command sets the intensity to 5.0 on the edited scene. The undo history grows by one step.

```json
{ "method": "component.set", "params": { "entity": "5A1C93E07B2D4F18", "component": "DirectionalLight", "values": { "Intensity": 5.0 } } }
```

The result holds the component's values and no warning. Next, `play.start` returns the state `Play`. Now the same command with `20.0` changes the running copy. The result carries the warning text, "The scene is running (Play): this change applies to the running copy and is discarded by play.stop", and the undo history keeps its length. The game sees a sun of 20.0 lux; the edited scene still holds 5.0.

After `play.stop` the state is `Edit` and `Sun` reads 5.0. An `edit.undo` reverts the first change to 3.0, not the second, because the second was never recorded. The numbers to remember are three: 3.0 at the start, 5.0 in the edited scene throughout, and 20.0 that lived and died inside the copy.
:::

If you tune `Intensity` to 20.0 while playing and want to keep it, set it again after Stop, on the edited scene.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Save and reload the live scene around play | Unity's play mode, per its manual | No second scene in memory | Fragile restore for bodies, voices and scripts; a crash mid-play can leave the scene changed |
| Run the game as a separate process | Godot | A crashed game cannot touch the editor; the game owns its window | Edits not yet saved do not play; a second program to start and keep in step |
| Copy the scene and run the copy | Unreal's play in editor | (This is Strata's choice) | Memory for two scenes; start time grows with the scene |

The price of Strata's choice is the last column of the third row. A very large scene takes time and memory to copy, and a person who tunes a value while playing must set it again on the edited scene afterwards.

## How it is tested

The tests sit in `StrataTests/src/Editor/`. The main regression test is `Play mode runs a copy and discards its changes`, in the `Editor.Commands` suite. It creates an entity and starts play, then renames and creates entities while playing. It checks that the undo history did not grow and that `edit.undo` fails.

The test then stops and compares a snapshot of the scene with the one taken before. Last it starts simulate and stops it again.

The `Editor.GameFlow` suite checks the requests: `Play mode stops when the game quits and switches scenes when it asks`, a switch that keeps play paused with its steps, and the journal event after a switch. The file `EditorGameShellTests.cpp` checks the shell: window requests that are reported and not applied, the same request logged once, saves in `.strata/Saves`, and the players' bindings loaded at the start and forgotten at the end. `EditorGameGraphicsTests.cpp` does the same for the players' graphics options. The `Editor.Audio` suite checks that audio plays in play mode and that the master volume returns. The crash path has `A script crash stops play mode and keeps the module disabled until it is reloaded` in `EditorScriptTests.cpp`.

Run one suite with the test program's filter, for example `StrataTests.exe --test-suite=Editor.GameFlow`, or run everything with `ctest`. A regression test for a change to play mode follows the same pattern: record the edited scene, play, change, stop, compare.

## Changing it safely

Extension points are few. A new game service that the shell must stand in for follows the pattern of `EditorGameWindow` and the save service. It needs an :term[engine service]{id=scene-service} interface, a provider that the context owns and registers while it lives, and a reset in `ResetGameShell`, so that the service starts and ends clean with each session.

A new command that edits the scene ends in `FinishEdit` and reads `GetActiveScene`, so it gets the warning and the mark for free.

Several rules of the engine's guide apply, each with its reason. Commands never block a frame, so a command that has to wait returns a deferred result and owns the data of its poll. Scenes are let go with `Scene::ReleaseInBackground`, never by dropping the last reference on the main thread, because a large scene takes tens of milliseconds to destroy. Scenes load through `SceneLoader`, never by a blocking load, so a scene switch does not stall the frame. And tools count game time in fixed steps, never in frames, which is why `Stop` keeps the step count.

Before you commit a change here, check four things. A copy never shares state with the edited scene. `Stop` restores everything `StartRuntime` kept. The new path works while a scene is still opening. A crash in a script cannot leave the state at `Play` with no copy.

Then run the `Editor.*` suites and `Scripting.*` suites. A new regression test should fail without your fix: remove the fix and watch it fail before you keep it.

What play mode cannot do is edit several scenes at once. The editor edits one scene, and a world's loaded cells, and `scene.loadAdditive` works in play mode only. A sub-scene you load that way ends with the game.

## Summary

- Strata plays a copy of the edited scene because a copy cannot damage the original, takes edits not yet saved, and keeps the game inside the editor's process.
- `StartRuntime` keeps the volume, copies the scene, resets input and the shell, loads players' options, and starts the copy; `Stop` releases it in the background and restores what was kept.
- Commands act on the active scene; edits to the running copy are not recorded, carry a warning and a mark, and vanish at Stop, while settings changes stay.
- A quit stops play, a scene switch loads in the background and swaps once ready, and a script crash logs, posts a toast and stops play.
- The game shell records window requests, keeps saves and players' options in `.strata/Saves`, and resets the cursor, input and volume.

## Check yourself

1. A designer presses Play, deletes the crate in the running scene with a command, and presses Stop. Which statement is right?
   (A) The crate is deleted from the edited scene too, and Undo brings it back.
   (B) The crate is back, because the command acted on the running copy, which Stop discards.
   (C) The command fails, because scene commands refuse to run while playing.

   :::answer{tests="why-copy,which-scene"}
   (B) is right: the command acts on the active scene, which is the running copy, and its result carries the warning. (A) is wrong because the two scenes share nothing and nothing is recorded for Undo. (C) is wrong because scene commands run on the copy and warn.
   :::

2. A game sets its master volume to 0.2 during play. What is the volume after Stop, if it was 0.8 at Play?
   :::answer{tests="start-stop,game-shell"}
   The volume is 0.8. `StartRuntime` keeps the volume in `m_MasterVolumeBeforePlay`, and `Stop` restores it, because a game's volume setting belongs to the game session.
   :::

3. Name the scene that each command changes while the game plays: `component.set`, `project.setSettings`, `edit.undo`.
   :::answer{tests="which-scene"}
   `component.set` changes the running copy, and its result warns. `project.setSettings` changes the project, which stays after Stop, with no warning. `edit.undo` changes nothing: it fails, because undo is not available while the scene runs.
   :::

4. A script's `OnUpdate` crashes on frame 40. List what the editor does, in order, and say what `play.start` does afterwards.
   :::answer{tests="requests"}
   After the update, `StopOnScriptFault` logs the class, the callback and the entity, posts an error toast that leads to the Problems panel and the Console, and calls `Stop`. `UpdateScriptFaultLocation` logs the file and line once the background job has found them. `play.start` fails until `script.build` or `script.reload`.
   :::

5. A game asks to be fullscreen at 1920 x 1080 pixels, every frame. What does the editor do with the first request and with the later ones?
   :::answer{tests="game-shell"}
   The shell records the first request and reports it in `editor.status` and as a notice over the Game view. It does not apply it. Later requests equal to the last one change nothing and are not logged again. Stop forgets the requests.
   :::

6. Why does the editor refuse to start play while a scene is being opened?
   :::answer{tests="start-stop"}
   The edited scene is about to be replaced. A copy would be a copy of a scene that is leaving, and the person would play something that is no longer there.
   :::

## Exercises

1. **Basic.** Change the toy so `Stop` forgets to restore the volume, and predict the last line of the output. Then restore it and find which line of the output would reveal a missing copy in `Play`.

   :::answer[Worked solution]{tests="why-copy,start-stop"}
   Without the restore, the last line shows volume 0.2 instead of 1.0, because the game's setting stays. A missing copy (`m_RuntimeScene = m_EditScene` removed) would make `GetActiveScene` return the edited scene, so the line "running copy 20.0, edited scene 20.0" would show equal numbers and the stopped line would read 20.0.
   :::

2. **Medium.** Write a toy game shell: a class that records window requests, reports a request once even if it repeats, and forgets all on `Clear`. Run it for two sessions.

   :::answer[Worked solution]{tests="game-shell" solution="sketches/editor-play-mode-shell.cpp"}
   The class keeps the last width, height and vsync as optional values. A request that equals the stored value returns false and prints nothing; a new one stores and prints. `Clear` resets all of them, as `Stop` does. The program asks twice in the first session, clears, and asks again in the second, which prints once more.

   ```cpp sketch="editor-play-mode-shell.cpp"
   #include <cstdint>
   #include <cstdio>
   #include <optional>

   // A toy game shell for the window: it records what the game asks for and reports a request once.
   class ToyGameWindow
   {
   public:
   	bool SetResolution(uint32_t width, uint32_t height)
   	{
   		if (m_Width == width && m_Height == height)
   			return false; // The same request as the last one: nothing changes, nothing is logged
   		m_Width = width;
   		m_Height = height;
   		std::printf("recorded: resolution %u x %u (the editor's window keeps its size)\n", width, height);
   		return true;
   	}

   	bool SetVSync(bool enabled)
   	{
   		if (m_VSync == enabled)
   			return false;
   		m_VSync = enabled;
   		std::printf("recorded: vsync %s\n", enabled ? "on" : "off");
   		return true;
   	}

   	// Called when play starts and when it stops: requests belong to one session.
   	void Clear()
   	{
   		m_Width.reset();
   		m_Height.reset();
   		m_VSync.reset();
   	}
   private:
   	std::optional<uint32_t> m_Width;
   	std::optional<uint32_t> m_Height;
   	std::optional<bool> m_VSync;
   };

   int main()
   {
   	ToyGameWindow window;
   	std::printf("session 1\n");
   	for (int frame = 0; frame < 3; frame++)
   	{
   		window.SetResolution(1920, 1080); // A game that applies its options every frame
   		window.SetVSync(false);
   	}
   	window.Clear(); // Stop
   	std::printf("session 2\n");
   	window.SetResolution(1920, 1080);
   	return 0;
   }
   ```

   ```text output-of="editor-play-mode-shell.cpp"
   session 1
   recorded: resolution 1920 x 1080 (the editor's window keeps its size)
   recorded: vsync off
   session 2
   recorded: resolution 1920 x 1080 (the editor's window keeps its size)
   ```

   1. **Lines 11–12:** a request equal to the last one changes nothing and prints nothing.
   2. **Lines 29–34:** Clear forgets every request, as Stop does for a session.
   3. **Lines 45–49:** a game that asks every frame prints each request only once.
   4. **Line 50:** the session ends before the second asks, so the second request prints again.
   :::

3. **Hard.** Trace it yourself: a script calls `Game::LoadScene(scene)`. Find where the request is recorded, where the editor reads it, and where the new scene replaces the old one.

   :::answer[Worked solution]{tests="requests"}
   The SDK's `Game::LoadScene` in `StrataScriptCore/Include/StrataScript/Game.h` calls the host function `HostLoadScene` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, which calls `Scene::RequestSceneLoad`. `EditorContext::HandleRuntimeRequests` takes it with `TakeSceneLoadRequest` after the update and calls `SwitchRuntimeScene`, which starts the background load. `UpdateRuntimeSceneLoad` finishes it, and `ReplaceRuntimeScene` swaps the scene and records a journal event of the play group.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorContext.cpp`: `Play`, `Simulate`, `StartRuntime`, `Stop`, `HandleRuntimeRequests`, `SwitchRuntimeScene`, `UpdateRuntimeSceneLoad`, `ReplaceRuntimeScene`, `StopOnScriptFault`, `UpdateScriptFaultLocation`, `ResetGameShell`.
- `StrataEditor/src/Editor/Commands/PlayCommands.cpp`: `play.start`, `play.simulate`, `play.stop`.
- `StrataEditor/src/Editor/CommandUtils.cpp`: `GetRunningCopyWarning`, `FinishEdit`, `RollBackEdit`.
- `StrataEditor/src/Editor/EditorGameWindow.h`: the recorded window requests.
- Tests: `Editor.Commands`, `Editor.GameFlow`, `Editor.Input`, `Editor.GameGraphics`, `Scripting.Game`, `Editor.Audio`.

## Further reading

- Unreal Engine documentation, "Play in editor": how the engine duplicates the world for a play session (intermediate).
- Unity manual, "Enter Play mode" and its settings: what the editor stores and reloads (intermediate).
- Godot documentation, "Running the project": how a game starts as its own process (beginner).
