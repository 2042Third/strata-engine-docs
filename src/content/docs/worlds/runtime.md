---
id: worlds/runtime
title: "The runtime"
description: "How an exported game runs without the editor: its start, its scene switches, its frame, its window and graphics options, and how you measure it."
kind: internals
size: XL
tracks: [E]
needs: [worlds/game-identity, core/engine-modules, core/windows-events, scripting/script-system, image/quality-settings]
time: 115
learn:
  - id: trace-start
    text: trace the start of an exported game from the command line to its first scene, naming each check and each failure
  - id: run-kinds
    text: predict which switches a windowed run, a run that ends by itself and a headless run get, and the exit code of each failure
  - id: scene-switch
    text: explain how a scene switch avoids a black window and a stalled frame, and what the game does when the switch fails
  - id: measure
    text: run an exported game headless with a frame count and a perf log, and read its exit code and its CSV
  - id: add-option
    text: add a runtime option, with its check, its usage line and its test
since: 0.3.0
status: final
---

A shipped game is the engine without the editor. The program that plays it is `StrataRuntime`, which an export copies next to the game's manifest and :term[asset pack]{id=asset-pack} and renames after the game. It runs the same scenes, scripts, physics and :term[renderer]{id=renderer} as the editor's play mode, but under another **composition root**: the one place that decides which parts of the engine a program contains. The :term[runtime]{id=runtime} holds no :term[importers]{id=importer}, no inspector, no hot reload and no editor commands. It also has a headless mode, which runs the game with no window and no :term[graphics card]{id=gpu}, for servers and automated checks.

The page does not teach how scenes load ([Sub-scenes](../world/sub-scenes.md) does), how the players' graphics options work ([Quality settings](../image/quality-settings.md)) or how the editor plays a scene. It teaches how a program that only plays starts, switches scenes, draws, ends and reports what it did.

## The problem and how engines solve it

An editor and a game need the same simulation, but they want different programs. The editor must open any project, import files, undo edits and show panels. A shipped game opens one project that is already cooked, and its players need a small, fast program that fails in a way a person understands. A second reason is trust. A game that carries the importers and the editor's commands carries their code and their bugs, and every added line is a line that can crash on a computer you never tested.

Engines solve this in three common ways.

The first is to ship the editor with its panels hidden, started with a "play" flag. That costs the least work at first, and the game and the editor never differ. The price is size, start time and exposure: the player's computer runs everything the editor can do.

The second is a separate player program that shares the engine's libraries but not the editor's. The price is a second way to start the engine, and a second set of mistakes: a feature that works in the editor can fail in the player.

The third is a fully separate engine build for each game, which gives the smallest program and the least shared code.

Strata chooses the second way. The engine is a set of :term[static libraries]{id=static-library}, and a program picks the parts it links and the :term[engine modules]{id=engine-module} it lists. `StrataRuntime` links the engine without the layers for tools, and a test reads the :term[linker's]{id=linker} map of the program to prove it. The cost is that every behavior the editor offers around the game, such as simulated input, stepping a paused game or command scripts, is absent from a shipped game. The runtime has its own options instead, and the rest of this page explains them.

:::why
Strata does not ship the editor as the player because the editor's job is to change things. A player program that cannot change a project cannot corrupt one, and a game maker who tests the exported game tests what the players get. The cost is two programs to keep consistent, which the shared `GameRuntime` class reduces: the editor's play mode and the runtime both run scenes through the same scene code.
:::

The most common mistake with this split is to call editor-only code from game code. A script or a module that includes an importer, or reads a project folder instead of the asset pack, runs in the editor and fails at the player's first launch. The layer table forbids the include, as [Layers and registries](../core/layers-registries.md) shows, so the build refuses it before a player can meet it.

## The map

The runtime is four classes in two places. `StrataRuntime` is the program: its `RuntimeLayer` is a layer of the application ([Layers and events](../core/windows-events.md)), and it owns the objects that need a window. Beneath it, in the engine library, `GameRuntime` is the core that needs no window at all, so the same core runs headless and in the tests. `GameRenderer` draws what the core plays, `GameWindowService` applies the game's window requests, and `FramePerfLog` writes the numbers of the frames.

```mermaid caption="The runtime's pieces. A layer owns the core, the window service, the renderer and the perf log, and a headless run omits the renderer, the graphics module and the real window." alt="A box for the application containing a runtime layer. The layer points to four boxes: the game runtime, which holds the asset pack, the scene and the scripts; the game renderer; the window service; and the perf log. The renderer and the graphics module are marked as absent in a headless run."
flowchart TD
	A[Application: modules and layers] --> L[RuntimeLayer]
	L --> G[GameRuntime: pack, scenes, scripts, saves, graphics options]
	L --> R[GameRenderer: not in a headless run]
	L --> W[GameWindowService: without a window, it only records requests]
	L --> P[FramePerfLog: only with a perf log]
	A --> M[Modules: Graphics only with a window, Audio, Project]
	G --> S[Scene and SceneLoader]
	R --> D[SceneRenderer]
```

Two threads matter. The :term[main thread]{id=main-thread} runs everything in the picture: it owns the scene, the scripts and the drawing. Every game also starts two background threads, because a game has one background job: letting a scene go after a switch. The tools' import and compression work never runs in a game, so the pool stays small.

## The contract

The runtime promises a game's author and the person who plays it a few things, each with a reason.

- A mistake on the :term[command line]{id=terminal-command} ends the run before a log, a module or a window exists, with :term[exit code]{id=exit-code} 3 and the usage. The reason is that a script with a wrong option learns it at once, in its terminal.
- A game that cannot start ends with exit code 1, and a person who started it learns why. Every failure of `GameRuntime::Create` is an error that comes back as text, never a crash.
- A scene switch never stops the frame, because the player would see a black window or a frozen picture while a level loads. The running scene keeps playing until its successor is ready.
- A failed switch is logged, and the running scene continues. A game that cannot load level two is still a game at level one.
- The window never changes in the middle of a frame. Requests wait, and one step applies them between frames.
- A run that ends by itself keeps every :term[fixed step]{id=fixed-step} and draws no poses between steps, so the state it shows after a given number of steps does not depend on the computer. A run for a player follows the wall clock.
- A script crash disables the scripts for the session. A headless run then ends with exit code 2, because nobody watches it, while a windowed game runs on without its scripts.
- A game that asks for a screenshot or a perf log and does not get a whole one fails with exit code 1, so that automated checks notice.

The exit codes follow from these promises, and a script that runs a game reads them.

| Code | When it happens |
| --- | --- |
| 0 | The run ended well, or help was asked for. |
| 1 | The game cannot start, or a screenshot or a perf log that was asked for could not be made whole. |
| 2 | The scripts crashed in a headless run. |
| 3 | The command line has a mistake. |
| The game's own | A script asked to quit with that code. |

:::rule[Games link no tooling]
`AGENTS.md` says that games link no `Tooling` layer, and that no one widens the layer table to make an include pass. The reason is the one above: the player's program holds only what the player needs. The rule's home is [Layers and registries](../core/layers-registries.md).
:::

## A toy version

The part of the runtime that most surprises people is the clock. A game for players plays by the wall clock: if a frame takes long, the game catches up, or slows. A run that ends by itself, such as a check in a build server, must give the same answer on every machine, so its game time cannot follow the wall clock. The toy below models only that rule, in whole milliseconds so that every number is exact. A fixed step lasts 20 ms, one update runs at most four steps, and the played time counts steps.

```cpp sketch="worlds-runtime-toy.cpp"
// A toy of the runtime's rule for runs that end by themselves: every fixed step runs, and the game's played time counts
// steps, never the wall clock. All times are whole milliseconds, so the output is exact.
#include <algorithm>
#include <cstdio>

constexpr int c_StepMs = 20; // One fixed step: 50 steps a second
constexpr int c_MaxSteps = 4; // The most steps one update runs

struct ToyScene
{
	int Accumulator = 0;
	int Steps = 0;
};

// One update: the frame's time is limited to what the most steps can simulate, so no step is ever dropped.
void Update(ToyScene& scene, int frameMs)
{
	scene.Accumulator += std::min(frameMs, c_MaxSteps * c_StepMs);
	while (scene.Accumulator >= c_StepMs)
	{
		scene.Accumulator -= c_StepMs;
		scene.Steps++;
	}
}

double PlayedSeconds(const ToyScene& scene)
{
	return scene.Steps * c_StepMs / 1000.0;
}

void Report(const char* machine, int frameMs)
{
	ToyScene byFrames;
	for (int frame = 0; frame < 250; frame++)
		Update(byFrames, frameMs);
	std::printf("%-8s --frames 250: %5.2f s of game time\n", machine, PlayedSeconds(byFrames));

	ToyScene bySeconds;
	int frames = 0;
	while (PlayedSeconds(bySeconds) < 5.0)
	{
		Update(bySeconds, frameMs);
		frames++;
	}
	std::printf("%-8s --seconds 5:  %3d frames (%.2f s)\n", machine, frames, PlayedSeconds(bySeconds));
}

int main()
{
	Report("fast", 20);
	Report("middle", 50);
	Report("slow", 200);
	return 0;
}
```

```text output-of="worlds-runtime-toy.cpp"
fast     --frames 250:  5.00 s of game time
fast     --seconds 5:  250 frames (5.00 s)
middle   --frames 250: 12.50 s of game time
middle   --seconds 5:  100 frames (5.00 s)
slow     --frames 250: 20.00 s of game time
slow     --seconds 5:   63 frames (5.04 s)
```

1. **Line 18:** the frame's time is limited to what the most steps can simulate. This is the line that keeps every step.
2. **Lines 19–23:** each full step in the :term[accumulator]{id=accumulator} runs once, and no step is thrown away.
3. **Line 28:** the played time counts steps, never wall time.

The fast machine plays one step a frame, so 250 frames are 5 seconds and 5 seconds are 250 frames. The slow machine takes 200 ms a frame, but one update may simulate only 80 ms, so it plays four steps a frame. The same 250 frames then give 20 seconds of game time, and 5 seconds of game time take 63 frames, because 62 frames give 4.96 seconds and a 63rd must finish the last step. Neither number depends on the clock. Both depend on the machine, because the machine decides how long a frame takes, and the page returns to this when it measures a game.

## The start

The real start has two halves. The first is `CreateApplication`, which runs before any engine part exists. The second is `RuntimeLayer::OnAttach`, which runs once the window and the modules do exist.

### The command line is checked first

`CreateApplication` first answers a request for help, then validates every option. The runtime's options are one table, `c_Arguments`, which feeds the usage text, the check for unknown options and the reference page of options.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L340-L354"
constexpr CommandLineOption c_Arguments[] = {
	{ "--game", "<file.stgame>", "Play this game (default: the one .stgame manifest next to the executable)" },
	{ "--headless", nullptr, "Run the game without a window or graphics, like a dedicated server (60 frames per second)" },
	{ "--windowed", nullptr, "Open a window even when the game asks for fullscreen" },
	{ "--resolution", "<width>x<height>", "Open a window of exactly this many pixels" },
	{ "--frames", "<count>", "Stop after this many frames (every fixed step runs: checks, screenshots)" },
	{ "--seconds", "<count>", "Stop once the game played this many seconds of game time, in fixed steps from its start "
		"(every fixed step runs: checks, screenshots)" },
	{ "--screenshot", "<file.png>", "Save the last frame (with --frames or --seconds, and a window)" },
	{ "--asset-budget-mb", "<megabytes>", "The GPU texture budget of the game's assets" },
	{ "--perf-log", "<file.csv>", "Write a row of frame timings per frame" },
	{ "--save-directory", "<folder>", "Keep the game's save files in this folder (default: the player's data)" },
	{ "--quality", "<low|medium|high|ultra>", "Draw with this Graphics Quality preset for this run (default: the project's, with "
		"the players' saved options over it); nothing is saved" },
	{ "--help", nullptr, "Print this help and exit" } };
```

1. **Line 340:** one table that the usage text, the check for unknown options and the reference page all read.
2. **Line 342:** a flag has no value name, so it holds `nullptr` in that place.
3. **Lines 346–347:** `--seconds` counts game time in fixed steps from the start, and the text says so.
4. **Line 354:** `--help` is a row too, so the usage lists it.

Check what each row says and what it does not. `--headless` and `--frames` change the run's kind, as the next section shows. `--seconds` counts game time, never the wall clock, and says so in its text.

The check that follows reads each value and refuses what cannot work. It is written so that a run meant to end can never run forever by mistake.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L388-L408"
// A run meant to end by itself must not run forever because its frame count or game time was mistyped.
const std::optional<int64_t> frames = commandLine.GetIntOption("--frames");
if ((commandLine.HasFlag("--frames") || commandLine.GetOption("--frames")) && (!frames || *frames <= 0))
	return std::string("--frames needs a positive whole number of frames");
const std::optional<int64_t> seconds = commandLine.GetIntOption("--seconds");
if ((commandLine.HasFlag("--seconds") || commandLine.GetOption("--seconds")) && (!seconds || *seconds <= 0))
	return std::string("--seconds needs a positive whole number of seconds");
// The screenshot is taken on the last frame, so it needs a run that ends by itself and a window.
if (commandLine.GetOption("--screenshot") && ((!frames && !seconds) || commandLine.HasFlag("--headless")))
	return std::string("--screenshot needs --frames <count> or --seconds <count>, and a window (not --headless)");
if (commandLine.HasFlag("--perf-log") && commandLine.GetOption("--perf-log").value_or(std::string()).empty())
	return std::string("--perf-log needs the path of the CSV file to write");
if (commandLine.HasFlag("--save-directory") && commandLine.GetOption("--save-directory").value_or(std::string()).empty())
	return std::string("--save-directory needs the folder to keep the game's save files in");
if (commandLine.HasFlag("--quality") || commandLine.GetOption("--quality"))
{
	if (!ParseQuality(commandLine.GetOption("--quality").value_or(std::string())))
		return std::string("--quality needs one of low, medium, high or ultra");
	if (commandLine.HasFlag("--headless"))
		return std::string("--quality needs a window: a headless run draws nothing");
}
```

1. **Lines 390–391:** a frame count that is not a positive whole number is refused.
2. **Lines 396–397:** a screenshot needs a run that ends by itself and a window.
3. **Lines 402–407:** a quality needs the name of a preset and a window.

The first lines refuse a frame count or a number of seconds that is not a positive whole number, since a wrong `--frames` would otherwise start a game that never stops. Next, a screenshot needs a run that ends and a window, because the screenshot is taken on the last frame. Last, `--quality` needs a window, since a headless run draws nothing.

A request that breaks a rule prints the problem and the usage to the error stream and exits with code 3. The function also hands the command line to `FindUnknownArgument`, so an option that is not in the table fails the same way.

`GetProgramRun` reads the same command line, earlier, to decide where the output goes. A run that asks for help, runs headless, ends by itself or has a mistake is a :term[Console run]{id=console-run}, so that its text appears in the terminal that started it. A person who double-clicks the game gets an Interactive run and no console.

The difference matters on Windows, where `StrataRuntime` is a program of the windowed kind, entered at `mainCRTStartup`. It carries the strata mark as its icon and a version resource. A windowed program has no console of its own, so a Console run connects to the one that started it ([The platform layer](../core/platform.md)).

### The manifest, the presentation and the modules

After the options, `CreateApplication` takes the manifest from `--game` or from the single `.stgame` file next to the :term[executable]{id=executable}. The manifest names the game, and its name names the game's data folder, where the log and the saves go. The presentation, made from the manifest, gives the window its title, version and icon before anything starts ([The game's identity](game-identity.md)). A game with no manifest cannot start: the person gets a dialog that says why and what to try, and the exit code is 1.

Then the specification chooses the modules.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L475-L493"
specification.Headless = commandLine.HasFlag("--headless");
if (specification.Headless)
{
	specification.MaxFrameRate = c_HeadlessFrameRate;
}
else
{
	specification.Modules.push_back(GraphicsModule::Factory());
}
#if ST_WITH_AUDIO
specification.Modules.push_back(AudioModule::Factory({ .NullDevice = specification.Headless }));
#endif
specification.Modules.push_back(ProjectModule::Factory());
specification.Jobs.BackgroundThreadCount = c_BackgroundThreadCount;
presentation.ApplyTo(specification.Window);
specification.Window.Width = manifest->WindowWidth;
specification.Window.Height = manifest->WindowHeight;
specification.Window.Fullscreen = manifest->Fullscreen && !commandLine.HasFlag("--windowed");
specification.Window.VSync = manifest->VSync;
```

1. **Line 475:** headless is one flag of the specification, and the lines after it read that flag.
2. **Lines 476–483:** a headless run caps itself at 60 frames a second, since no :term[vsync]{id=vsync} paces it and a server should not keep a :term[processor core]{id=processor-core} busy. A windowed run lists the graphics module instead, and no other module needs to know.
3. **Line 485:** the audio module runs in both, but on a null device when headless, so sound code runs and nothing plays.
4. **Line 488:** two background threads, for every game.
5. **Line 492:** a manifest's fullscreen request holds unless the person passed `--windowed`.

The rest of `CreateApplication` copies the other options into `RuntimeOptions`, and returns a launch that makes the application later. Nothing in it names the asset pipeline. Games read cooked packs, and the importers are not linked at all.

### Three kinds of run

`RuntimeLayer::OnAttach` turns the options into the core's options. Three of its lines decide what kind of run this is.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L79-L91"
const bool endsByItself = m_Options.MaxFrames || m_Options.MaxSeconds;
runtimeOptions.TimeDilation = !endsByItself;
runtimeOptions.KeepEveryFixedStep = endsByItself;
runtimeOptions.SaveFilesDirectory = m_Options.SaveDirectory;
// The run's Graphics Quality preset over the project's and the players' (their saved choices stay as they are).
runtimeOptions.Quality = m_Options.Quality;
// Headless runs (servers, CI) have no window to render to; with one, scenes have their render proxies built before
// they start, so the frame that shows one does not build them all.
const bool renders = Application::Get().GetWindow() && Renderer::IsInitialized();
runtimeOptions.PrepareRenderScenes = renders;
// What the fixed steps move is drawn between their poses where frames show the wall clock: not in runs that end
// by themselves (their last frame must not depend on the machine) nor in headless ones, which draw nothing.
runtimeOptions.Interpolation = !endsByItself && renders;
```

1. **Line 79:** a run ends by itself when it has `--frames` or `--seconds`.
2. **Lines 80–81:** such a run never slows its time and keeps every fixed step. A game for players does the opposite.
3. **Lines 87–88:** a window and a ready renderer mean the scenes' :term[render proxies]{id=render-proxy} are built before a scene starts, so the first frame that shows a scene does not build them all.
4. **Line 91:** drawing between the last two poses of a fixed step needs the wall clock and a picture to draw.

The kinds are easiest to compare side by side.

| Kind of run | :term[Time dilation]{id=time-dilation} | Every fixed step kept | Render proxies prepared | :term[Interpolation]{id=interpolation} | Other |
| --- | --- | --- | --- | --- | --- |
| A windowed game | yes | no | yes | yes | The window's pacing |
| A run that ends by itself, with a window | no | yes | yes | no | Console run; screenshot allowed |
| A headless run | yes, unless it ends by itself | only if it ends by itself | no | no | 60 frames a second, no graphics processing unit (GPU), refuses `--quality` and `--screenshot` |

:::example[Which switches does this command line set?]
You run `StrataRuntime --game Coin.stgame --frames 600 --resolution 1280x720`. The command line has `--frames`, so the run ends by itself: dilation off, every fixed step kept, a Console run. It has no `--headless`, so the graphics module is listed and the renderer exists: render proxies are prepared, and interpolation is off. The window is exactly 1280 by 720 pixels, whatever the display's scale. Now add `--headless`: the same run needs no GPU, and a `--screenshot` or `--quality` added to it would be refused with exit code 3 before anything starts.
:::

## Bringing the game up

`GameRuntime::Create` is the heart of the start. It is a list of steps in a fixed order, and every failure returns `nullptr` with a message. The order exists so that nothing a later step needs is missing, and so that a failure leaves nothing half made. The first half reads the files.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L47-L84"
std::optional<GameManifest> manifest = GameManifest::Load(manifestPath, outError);
if (!manifest)
	return nullptr;

Scope<GameRuntime> runtime(new GameRuntime());
runtime->m_Opened = std::chrono::steady_clock::now();
runtime->m_Manifest = std::move(*manifest);
// The export validated the settings, so a section its module refuses is a damaged install, and the game must not run
// with settings it cannot read (bindings that do nothing, layers that collide wrongly). Sections no registered module
// claims are not provided.
if (runtime->m_Manifest.Settings)
{
	const SettingsRegistry& registry = options.Settings ? *options.Settings : SettingsRegistry::GetProcessRegistry();
	const std::vector<SettingsProblem> problems = runtime->m_Manifest.Settings->Validate(registry);
	if (!problems.empty())
	{
		if (outError)
			*outError = fmt::format("The game's settings section '{}' is invalid: {}", problems.front().Section, problems.front().Message);
		return nullptr;
	}
	runtime->m_SettingsProvider = CreateScope<EngineServices::ScopedProvider<IProjectSettings>>(*runtime->m_Manifest.Settings);
}
const std::filesystem::path packPath = manifestPath.parent_path() / FileSystem::FromUTF8(runtime->m_Manifest.AssetPack);
runtime->m_AssetManager = RuntimeAssetManager::Create(packPath, outError);
if (!runtime->m_AssetManager)
	return nullptr;
// Patches replace the game's assets before anything loads; one that is missing or broken stops the game, which
// would otherwise run with assets the patch was meant to replace.
for (const std::string& patch : runtime->m_Manifest.PatchPacks)
{
	std::string error;
	if (!runtime->m_AssetManager->Mount(manifestPath.parent_path() / FileSystem::FromUTF8(patch), &error))
	{
		if (outError)
			*outError = fmt::format("Mounting the patch pack '{}' failed: {}", patch, error);
		return nullptr;
	}
}
```

1. **Lines 47–49:** the manifest is read first. If it is damaged, nothing else exists to clean up.
2. **Lines 57–68:** the settings the export validated are validated again against the modules that are registered. A section that its module refuses is a damaged install, and a game must not run with bindings or layers it cannot read.
3. **Lines 69–72:** the asset pack is opened next to the manifest.
4. **Lines 75–84:** each :term[patch pack]{id=patch-pack} the manifest names is mounted before anything loads. A missing patch stops the game, since the game would otherwise run with the assets that the patch meant to replace ([Packs and exports](../assets/packs-export.md)).

The second half brings in the parts that scripts and scenes use. Its order matters as much as the first half's, because a script's first call may already load a save or read a graphics option.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L102-L146"
runtime->m_PreviousScriptEngine = ScriptEngine::GetActive();
if (!runtime->m_Manifest.ScriptModule.empty())
{
	runtime->m_ScriptEngine = CreateRef<ScriptEngine>();
	const std::filesystem::path modulePath = manifestPath.parent_path() / FileSystem::FromUTF8(runtime->m_Manifest.ScriptModule);
	std::string error;
	if (!runtime->m_ScriptEngine->LoadModule(modulePath, &error))
	{
		if (outError)
			*outError = fmt::format("Loading the game's script module failed: {}", error);
		return nullptr; // The destructor deactivates the asset manager
	}
}
ScriptEngine::SetActive(runtime->m_ScriptEngine);
// The game's save files, from its first script call on (OnCreate may load a save).
runtime->m_Saves = options.SaveFilesDirectory.empty() ? SaveDirectory::ForGame(runtime->m_Manifest.Name) : CreateScope<SaveDirectory>(options.SaveFilesDirectory);
runtime->m_SavesProvider = CreateScope<EngineServices::ScopedProvider<IGameSaves>>(*runtime->m_Saves);
// The bindings the players chose in an earlier session (InputActions::SaveBindings), with the manifest's actions.
InputActions::ResetSession();
InputActions::LoadBindings();
// The graphics options the players chose in an earlier session over the manifest's Graphics Quality (a version-4
// manifest has none: the section's default), and the command line's preset over both: from the first script call and
// the first frame on.
runtime->m_Graphics = CreateScope<GameGraphicsService>(runtime->m_Manifest.Settings ? &*runtime->m_Manifest.Settings : nullptr,
	runtime->m_Saves.get(), options.Settings);
runtime->m_Graphics->SetCommandLinePreset(options.Quality);
runtime->m_Graphics->LoadPlayerOptions();
runtime->m_GraphicsProvider = CreateScope<EngineServices::ScopedProvider<IGameGraphics>>(*runtime->m_Graphics);

// The loading scene first, so that it plays while the start scene loads (both load in the background).
const AssetHandle loadingScene = runtime->m_Manifest.LoadingScene;
if (loadingScene.IsValid())
{
	if (runtime->m_AssetManager->GetAssetType(loadingScene) != AssetType::Scene)
	{
		if (outError)
			*outError = fmt::format("The loading scene {} is not a scene of the game", loadingScene.ToString());
		return nullptr; // The destructor deactivates the asset manager and the script engine
	}
	runtime->m_LoadingSceneLoad = CreateScope<PendingScene>();
	runtime->m_LoadingSceneLoad->Scene = loadingScene;
	runtime->m_LoadingSceneLoad->Request = SceneLoader::LoadAsync(loadingScene, runtime->m_LoadOptions);
}
if (!runtime->LoadScene(runtime->m_Manifest.StartScene, outError))
	return nullptr;
```

1. **Lines 102–115:** a game with a script module gets a `ScriptEngine` of its own and loads the module in place. Nothing reloads it, so there is no copy to swap. The engine is made active before the start scene plays, and the host's earlier engine is remembered, to be restored when the game ends.
2. **Line 117:** the save folder is the player's folder for this game, or the one that `--save-directory` named.
3. **Lines 120–121:** the players' bindings from an earlier session load over the manifest's actions.
4. **Lines 125–129:** the graphics options come from the project's quality, the players' choices and the command line's preset, in that order of strength ([Quality settings](../image/quality-settings.md)).
5. **Lines 132–146:** the loading scene starts to load first, so that it plays while the start scene loads. A handle that is not a scene is an error here, not later.

The matching end is the :term[destructor]{id=destructor}. It stops the loads under way, then the scene, then restores the host's script engine and disables the active :term[asset manager]{id=asset-manager}. The game's bindings and graphics options end last, after the scene stopped, since the last calls of its scripts may still read them.

Compare this with the editor's play mode. The editor reads files from a project folder and can import and rebuild. The runtime reads one pack and can only play it. That is why the order is short and why a failure is always about files.

## Scene switches that never block

A game shows two scenes in its first seconds. The **loading scene** is a small scene that the manifest names, and it plays while the game's first scene loads.

The **start scene** is the first scene of the game itself. A level change later is a switch to another scene, and the problem is the same each time. A scene and everything it uses take longer to load than one frame, and a frame that waits shows a frozen or black window.

Strata solves it with the loads of [Sub-scenes](../world/sub-scenes.md). `GameRuntime` asks for a scene with `SceneLoader::LoadAsync` and keeps playing what it has until the request is ready. Every scene the game loads gets `PrepareSystems`, so its physics bodies and its first world cells exist before its first frame.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L188-L198"
if (m_SceneLoad && m_SceneLoad->Scene == scene)
	return true;
// A request for another scene replaces the one under way: its pins and the loads only it needed go. The new load
// starts first, so that what both use keeps loading (Cancel leaves assets others pin alone).
Scope<PendingScene> next = CreateScope<PendingScene>();
next->Scene = scene;
next->Request = SceneLoader::LoadAsync(scene, m_LoadOptions);
m_SceneLoad = std::move(next);
if (m_Scene)
	m_Scene->SetSceneLoadProgress(0.0f);
return true;
```

1. **Line 188:** a second request for the scene that is loading changes nothing. Scripts often ask in every update while a condition holds, and starting over each time would never finish.
2. **Lines 192–195:** a request for another scene replaces the one under way. The new load starts before the old one is cancelled, so that the assets both need keep loading.
3. **Lines 196–197:** the running scene's progress returns to zero, which a script reads with `Game::GetSceneLoadProgress` to draw a progress bar.

The swap itself is `StartScene`, and the part of the update that drives all of this is `UpdateSceneLoads`.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L214-L222"
Scene::ReleaseInBackground(std::move(m_Scene));
m_Scene = std::move(scene);
m_SceneHandle = handle;
m_Scene->SetTimeDilation(m_TimeDilation);
m_Scene->SetInterpolation(m_Interpolation);
m_Scene->OnRuntimeStart(SceneRuntimeMode::Play);
// What the previous scene used, this one's load did not bring in and this one does not request in its first frames is
// released then.
m_AssetManager->ScheduleTrim(AssetResidency::c_SceneSwitchTrimFrames, AssetResidency::c_SceneSwitchTrimFrames, loaded);
```

The previous scene goes to `Scene::ReleaseInBackground`, so that a scene with a million entities does not cost the frame tens of milliseconds. The new scene gets the run's dilation and interpolation, and starts. Then the runtime schedules a trim: three frames later, the assets that the old scene used and the new scene did not request are released. The delay lets the new scene request what it needs first, so that an asset both scenes use does not leave and return ([Residency](../assets/residency.md)).

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L250-L281"
if (!m_SceneLoad)
	return;
SceneLoadRequest& request = m_SceneLoad->Request;
request.Update(budget);
if (m_Scene)
	m_Scene->SetSceneLoadProgress(request.GetProgress());
if (!request.IsFinished())
	return;
if (request.GetState() == SceneLoadState::Ready)
{
	const bool first = !m_Started;
	StartScene(request.TakeScene(), m_SceneLoad->Scene, request.GetAssets());
	m_Started = true;
	m_ShowingLoadingScene = false;
	// Its pins go once the scene that uses the assets requests them itself (from its first frame on).
	m_SceneLoad.reset();
	m_LoadingSceneLoad.reset();
	if (first)
		ST_CORE_INFO("Started '{}' in {:.2f} s", m_Manifest.Name, std::chrono::duration<double>(std::chrono::steady_clock::now() - m_Opened).count());
	return;
}
const std::string error = request.GetError();
m_SceneLoad.reset();
if (m_Scene)
	m_Scene->SetSceneLoadProgress(std::nullopt);
if (!m_Started)
{
	m_StartError = fmt::format("Loading the start scene failed: {}", error);
	ST_CORE_ERROR("'{}' cannot start: {}", m_Manifest.Name, *m_StartError);
	return;
}
ST_CORE_ERROR("'{}' cannot switch scenes: {}", m_Manifest.Name, error);
```

1. **Lines 250–255:** the load advances by the frame's :term[work budget]{id=work-budget}, and a scene that is running learns the progress.
2. **Lines 258–269:** a ready scene starts. The first start also ends the loading scene's turn, and the log says how long the start took.
3. **Lines 271–281:** a failed load before the game started is a start error, which ends the run with exit code 1. A failed load after it is only logged, and the running scene continues.

:::example[A switch across eight frames]
A script asks for level 2 in frame 100. Say the new scene's preparation needs 30 ms of main-thread work in all. The frame's load budget is 4 ms, so the work spreads over 8 frames, because 30 divided by 4 is 7.5. In each of frames 100 to 107 the running level 1 still updates and draws, and its progress reads between 0 and 1.

In frame 108 the request is ready: `StartScene` hands level 1 to the background release, and level 2 starts. Its first frames request the assets they need. Three frames later, in frame 111, the trim releases what level 1 used and level 2 did not ask for. The player saw no gap, and no frame was longer than its usual work plus 4 ms.
:::

The function runs inside the :term[profiler]{id=profiler-instrumenting-vs-sampling} stage for scene loads, a stage of the frame :term[profiler]{id=profiler-instrumenting-vs-sampling}, so a switch appears as time in that stage across the frames between the request and the swap.

One more rule keeps a loading scene honest. A loading scene that asks for its own scene again, to start over, loads again beside the start scene's load, and the start scene's load continues. Without that rule, a loading animation that restarts itself would cancel the game's start.

Frames pass during all this, and nothing plays in the first of them. While no scene plays, the layer caps the :term[frame rate]{id=frame-rate} at 60 a second, so that the loading threads get the processor instead of hundreds of cleared frames. Once a scene plays, the cap is the game's own pacing. Ten seconds after its start, an exported Open World has left its loading scene behind and plays its start scene.

::figure{id=open-world-exported}

## The frame

`GameRuntime::Update` is what the layer calls once per frame.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L298-L313"
if (m_QuitRequest)
	return;
m_AssetManager->Update();
// One budget for the frame's loading work: the scene loads' preparation and the running scene's sub-scenes draw from it.
SceneWorkBudget budget = SceneWorkBudget::ForFrame(m_Scene ? m_Scene->GetSettings() : SceneSettings());
UpdateSceneLoads(&budget);
if (!m_Scene)
	return;
// The steps this update runs, each simulating the timestep the scene reads as the update begins.
const uint64_t stepsBefore = m_Scene->GetFixedStepCount();
const double fixedTimestep = m_Scene->GetFixedTimestep();
m_Scene->OnUpdateRuntime(m_KeepEveryFixedStep ? LimitToFixedSteps(*m_Scene, timestep) : timestep, &budget);
if (m_Started)
	m_PlayedSeconds += static_cast<double>(m_Scene->GetFixedStepCount() - stepsBefore) * fixedTimestep;
CheckScriptFault();
HandleSceneRequests();
```

1. **Line 298:** after a quit request, updates do nothing.
2. **Lines 302–303:** one `SceneWorkBudget` serves the frame. The scene loads' preparation and the running scene's sub-scenes draw from it, so loading work cannot add up to a long frame.
3. **Line 309:** a run that keeps every fixed step limits the :term[timestep]{id=time-step} first. Dropping the :term[backlog]{id=backlog} is how a game for players avoids a spiral of long frames, and it is exactly what such a run must not do.
4. **Line 311:** the played time grows by the fixed steps that ran, once the game has started. The loading scene's steps do not count.
5. **Lines 312–313:** the script crash is recorded, then the runtime acts on the scene's requests.

The limit is short enough to read whole.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L34-L40"
const float timeScale = scene.GetTimeScale();
// Paused or stopped time runs no steps (and stepping a paused scene runs one per update): nothing to limit.
if (timeScale <= 0.0f || scene.IsPaused())
	return timestep;
const float maxSteps = static_cast<float>(scene.GetMaxFixedSteps());
const float limit = maxSteps * scene.GetFixedTimestep() / timeScale;
return Timestep(std::min(static_cast<float>(timestep), limit));
```

A paused or stopped scene needs no limit. Otherwise the limit is the scene's most steps, times the step, divided by the :term[time scale]{id=time-scale}. The default for most steps is 8 at 60 steps a second, so one update may simulate 133 ms of game time. A longer frame plays less game time than it took, and the scene's clock agrees with the played time, which is the point.

Requests from the scene come last, in `HandleSceneRequests`. A script's `Game::LoadScene` becomes a request for a scene, `RequestQuit` a quit with the game's own exit code.

```cpp src="Strata/src/Strata/Runtime/GameRuntime.cpp#L348-L360"
const std::optional<UUID> request = m_Scene->TakeSceneLoadRequest();
if (!request)
	return;
const AssetHandle scene = request->IsValid() ? *request : m_SceneHandle;
// The loading scene starting itself over loads again on its own: the start scene's load goes on.
if (m_ShowingLoadingScene && scene == m_SceneHandle)
{
	RestartLoadingScene();
	return;
}
std::string error;
if (!LoadScene(scene, &error))
	ST_CORE_ERROR("'{}' cannot switch scenes: {}", m_Manifest.Name, error);
```

1. **Line 351:** the null handle means "this scene again".
2. **Lines 353–357:** a loading scene that restarts itself restarts only its own load.
3. **Lines 359–360:** a request that fails is logged, and the running scene keeps going.

The layer's `OnUpdate` then adds what only the program can decide. It runs in this order.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L142-L166"
m_Runtime->Update(timestep);
// A start scene that cannot be loaded leaves nothing to play.
if (const std::optional<std::string> startError = m_Runtime->GetStartError())
{
	ReportStartFailure(*startError);
	m_Runtime.reset();
	return;
}
// A headless run (a server, CI) has nobody to show a broken game to: a script crash ends it with exit code 2. A
// windowed game keeps running without its scripts; the crash is in the log.
if (m_Runtime->GetScriptFault() && Application::Get().GetSpecification().Headless)
{
	ST_CRITICAL("Stopping the headless game after a script crash");
	Application::Get().SetExitCode(c_ScriptCrashExitCode);
	Application::Get().Close();
	m_Runtime.reset();
	return;
}
// The game asked to end (Scene::RequestQuit): the process exits with its code.
if (const std::optional<int32_t> exitCode = m_Runtime->GetQuitRequest())
{
	Application::Get().SetExitCode(*exitCode);
	Application::Get().Close();
	return;
}
```

1. **Line 142:** the core updates first.
2. **Lines 144–149:** a start error ends the run with the reason. The runtime object is dropped, so nothing else touches it.
3. **Lines 152–159:** a script crash in a headless run ends it with exit code 2. A windowed game keeps running without its scripts, and the crash stays in the log. The crash is logged once, and again with its code location when symbolization finishes a moment later ([Crash containment](../scripting/crash-containment.md)).
4. **Lines 161–165:** a quit request becomes the process's exit code, whatever number the game chose.

The second half draws, and decides whether this was the run's last frame.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L168-L197"
m_WindowService->ApplyRequests();
if (m_Renderer)
{
	// Frames of minimized windows are skipped by the application; this frame has a back buffer, which the GPU waits
	// for only from here on (after the frame's asset uploads, which the update above submitted).
	GraphicsDevice& device = Renderer::GetGraphicsDevice();
	Renderer::PrepareBackBuffer();
	// Until the first scene (or the loading scene) plays, the frame is cleared, at most 60 times a second: the
	// loading threads get the CPU instead of hundreds of cleared frames.
	Application::Get().SetMaxFrameRate(m_Runtime->GetFrameRateCap(m_GamePacing));
	if (nvrhi::IFramebuffer* backBuffer = device.GetBackBufferFramebuffer())
	{
		if (m_Runtime->GetScene())
			m_Renderer->Render(m_Runtime->GetScene(), backBuffer, device.GetBackBufferSize());
		else
			m_Renderer->RenderEmpty(backBuffer, device.GetBackBufferSize());
	}
}
// The run's last frame: the last of --frames (the application closes after it), or the first by which the game
// played --seconds of game time, however many frames that took.
Application& application = Application::Get();
const bool lastOfFrames = m_Options.MaxFrames && application.GetFrameCount() + 1 == *m_Options.MaxFrames;
const bool playedEnough = m_Options.MaxSeconds && m_Runtime->GetPlayedSeconds() >= static_cast<double>(*m_Options.MaxSeconds);
if (playedEnough)
{
	ST_INFO("The game played {:.3f} s of game time in {} frames: stopping", m_Runtime->GetPlayedSeconds(), application.GetFrameCount() + 1);
	application.Close();
}
if (lastOfFrames || playedEnough)
	RequestScreenshot();
```

1. **Line 168:** the window's requests apply now, after the game's update and before the drawing.
2. **Lines 174–177:** the :term[back buffer]{id=back-buffer} is prepared after the frame's uploads, and the frame cap follows what plays.
3. **Lines 180–184:** a scene is drawn, and while none plays the frame is cleared.
4. **Lines 189–195:** the last frame is the last of `--frames`, or the first by which the game played enough seconds, however many frames that took.
5. **Lines 196–197:** a screenshot, if asked for, is taken of that frame.

Two failures of the screenshot are worth knowing. A screenshot that shows the missing-camera message, or a cleared frame because the start scene is still loading, fails the run with exit code 1. A check that photographs a broken game must not pass.

## What a window is never left showing

`GameRenderer` draws the scene that plays. It owns a `SceneRenderer`, follows the game's graphics options every frame and has one job that matters here: a player is never left with a black or stale window.

```cpp src="Strata/src/Strata/Runtime/GameRenderer.cpp#L105-L127"
if (m_LastScene.lock() != scene)
{
	m_Renderer->ResetExposureAdaptation();
	m_Renderer->ResetHistory();
	m_LastScene = scene;
	m_ShowingMessage = false; // A new scene without a camera is reported again
}

const float aspectRatio = static_cast<float>(size.x) / static_cast<float>(size.y);
if (Entity camera = scene->GetPrimaryCameraEntity())
{
	if (m_ShowingMessage)
	{
		ST_CORE_INFO("The scene '{}' has a primary camera again", scene->GetName());
		m_Renderer->ResetExposureAdaptation();
		m_Renderer->ResetHistory();
		m_ShowingMessage = false;
	}
	// The camera's lens defocuses the game's view when its Depth Of Field is on.
	SceneRenderOptions options;
	options.Lens = CameraLens::FromEntity(*scene, camera);
	return m_Renderer->Render(*scene, SceneCamera::FromEntity(*scene, camera, aspectRatio), target, options);
}
```

1. **Lines 105–111:** a scene that is not the last one drawn starts at its own brightness and without the old scene's temporal history. Exposure adapts over time, so a dark cellar entered from a bright field would otherwise start bright ([Exposure](../image/exposure.md), [Temporal anti-aliasing](../image/taa.md)).
2. **Line 114:** the picture comes from the :term[primary camera]{id=primary-camera}.
3. **Lines 116–122:** when a camera comes back, the history resets again and the message goes away.

```cpp src="Strata/src/Strata/Runtime/GameRenderer.cpp#L129-L151"
// A scene without a camera that has screen-space UI (a main menu needs no camera): its UI over an empty frame.
if (m_Renderer->HasOverlayContent(*scene))
{
	m_ShowingMessage = false;
	m_MessageText.GetComponent<TextComponent>().Text.clear();
	SceneCamera camera;
	camera.Projection = Math::PerspectiveReverseZ(camera.VerticalFOV, aspectRatio, camera.Near, camera.Far);
	camera.ClearColor = c_EmptyBackground;
	SceneRenderOptions options;
	options.OverlayScene = scene.get();
	return m_Renderer->Render(*m_MessageScene, camera, target, options);
}

if (!m_ShowingMessage)
{
	ST_CORE_ERROR("The scene '{}' has no active entity with a Camera component marked Primary: showing a message instead", scene->GetName());
	m_ShowingMessage = true;
}
UpdateMessage(*scene, size);
SceneCamera camera;
camera.Projection = Math::PerspectiveReverseZ(camera.VerticalFOV, aspectRatio, camera.Near, camera.Far);
camera.ClearColor = c_MessageBackground;
return m_Renderer->Render(*m_MessageScene, camera, target);
```

1. **Lines 130–139:** a scene with no camera but with screen-space interface is drawn over a dark frame, because a main menu needs no camera.
2. **Lines 142–145:** the missing camera is logged as an error once, not every frame.
3. **Lines 147–151:** the frame shows the words "No camera to show", the scene's name and the reason, in a size that reads at any window size.

`RenderEmpty` is the frame before any scene plays: plain dark, with no message, because loading is normal and not a mistake.

## Window and graphics options

Players change the window mode, the resolution and the vertical :term[sync]{id=synchronization}. A script calls `Game::SetWindowMode`, `SetResolution` or `SetVSync`, and the runtime provides the service behind them for as long as the game runs. The mistake to avoid is changing the window in the middle of a frame: the :term[swapchain]{id=swapchain} would then belong to a size that the frame's drawing did not use.

So `GameWindowService` stores the requests and applies them once per frame, after the update. It keeps only the latest request of each kind. A headless run has no window, so the service records and logs what was asked, and reports it back, so that a script reads the state it set.

```cpp src="Strata/src/Strata/Runtime/GameWindowService.cpp#L129-L148"
if (m_PendingWidth && m_PendingHeight)
{
	const glm::uvec2 requested(*m_PendingWidth, *m_PendingHeight);
	const bool resized = !m_Window->IsMinimized() && m_Window->GetFramebufferSize() != m_FramebufferAfterApply;
	if (!m_AppliedResolution || *m_AppliedResolution != requested || resized)
	{
		m_Window->SetResolution(requested.x, requested.y);
		m_AppliedResolution = requested;
		changed = true;
	}
}
if (m_PendingMode && ToWindowMode(*m_PendingMode) != m_Window->GetMode())
{
	m_Window->SetMode(ToWindowMode(*m_PendingMode));
	changed = true;
}
if (m_PendingVSync && *m_PendingVSync != m_Window->IsVSync())
{
	m_Window->SetVSync(*m_PendingVSync);
	changed = true;
```

1. **Line 129:** the size is applied only when a request for it exists.
2. **Lines 132–135:** the same size asked again is applied only when the player changed the window's size since. A window without a border keeps the desktop's size, and a display may lack the mode, so comparing the :term[framebuffer]{id=framebuffer} with the request would apply it in every frame.
3. **Lines 140–144:** the mode is applied only when it differs from the window's.
4. **Lines 145–148:** so is the vertical sync.

A game may therefore apply its options in every frame: what changes nothing is not applied and not logged. The window toy of the exercises shows the rule.

The players' graphics options are another service, `GameGraphicsService`, and the page [Quality settings](../image/quality-settings.md) teaches it. Only the graphics options reach a file: they live in `GraphicsOptions.json` in the save folder. The window options do not. The engine writes no file for them, so they last for the session, and a game that wants them back writes them to a save file itself, as [Levels and saves](../make/levels-saves.md) shows.

## Measuring a shipped game

A game maker asks "how fast is it?" and the answer must be a number that can be compared. Two things spoil comparisons: a run whose game time depends on the frame rate, and numbers that describe different frames. Strata gives a shipped game answers to both.

First, game time. `GetPlayedSeconds` counts fixed steps after the start scene begins, each at its scene's step, and not wall time. The loading scene's steps and the time a game stops do not count. With `KeepEveryFixedStep`, no step is dropped, so the number of steps does not depend on the frame rate. The toy showed the arithmetic: the same `--frames` count plays different game time on a slow and a fast machine, and the same `--seconds` count takes a different number of frames.

:::example[Reading two runs]
A game with a scene of 60 steps a second runs headless with `--frames 300`. A headless run holds 60 frames a second, so each frame plays one step: 300 steps are 5.00 seconds. A run with `--seconds 5` also needs 300 steps, and ends with the frame that completes them: frame 300.

Now take a slower computer whose frames last 200 ms. One update may play at most 8 steps, so each frame plays 8. With `--frames 300` the run plays 2,400 steps, which are 40 seconds. With `--seconds 5` it needs 38 frames.

Compare only runs that end by the same rule. The log of a `--seconds` run says how many frames it took, so read that line before you compare two runs.
:::

The second thing is the perf log. A **perf log** is a table of comma-separated values, one row per frame, in a `.csv` file that the runtime writes when you pass `--perf-log <file.csv>`.

The columns tell the frame's number, :term[work time]{id=work-time} and interval, and the time of each profiler stage. They add the busy share of the job system's threads and the :term[asset manager's]{id=asset-manager} counts. The upload queue, the device memory and the process memory follow. After these built-in columns come the extra columns of the program.

A **column group** is a list of extra column names that a program adds to the log, together with a function that writes their values for each row.

The runtime adds two groups. `GameRuntime` writes the world's streaming counts and the :term[physics capacity]{id=capacity} and step columns: `WorldCellsWanted`, `WorldCellsLoaded`, `PhysicsBodies`, `PhysicsStepMs` and others. `GameRenderer` writes what the renderer drew: `DrawCalls`, `Instances`, `Triangles` and more. A headless run leaves the renderer's group empty, and a column with nothing to report is an empty field, never a zero that would be read as a measurement.

The log has one catch. The processor finishes a frame long before the graphics processing unit (GPU) has times for it. A row must describe one frame, so the log works in two steps.

```mermaid caption="One frame in the perf log. The numbers are captured when the frame ends, and the row is written a few frames later, when the graphics card's times for that frame arrive." alt="A time line with frames N, N plus 1 and N plus 2 along it. An arrow from the end of frame N down to a box called captured numbers. A later arrow from the arrival of the GPU times, after frame N plus 2, to a box called row written, which points back to frame N."
flowchart LR
	F0[Frame N ends] -->|capture| C[Numbers of frame N held]
	F0 --> F1[Frame N+1] --> F2[Frame N+2]
	F2 -->|GPU times of N arrive| W[Row of frame N written]
	C --> W
```

The two listeners of `StartPerfLog` implement that diagram. Look at which one asks for the GPU's times, and at what each one does with the frame.

```cpp src="StrataRuntime/src/RuntimeApplication.cpp#L231-L247"
m_PerfLogListener = FrameProfiler::Get().AddFrameListener([this](const FrameSample& frame)
{
	const std::optional<AssetManagerStats> assets = m_Runtime ? std::optional<AssetManagerStats>(m_Runtime->GetAssetManager()->GetStats()) : std::nullopt;
	const GPUUploadQueueStats* uploads = Renderer::IsInitialized() ? &Renderer::GetUploadQueue().GetStats() : nullptr;
	std::optional<FramePerfDeviceMemory> device;
	if (Renderer::IsInitialized())
	{
		const StagingPool& staging = Renderer::GetStagingPool();
		device = FramePerfDeviceMemory { Renderer::GetGraphicsDevice().GetMemoryBudget().Usage, staging.GetIdleBytes() + staging.GetPendingBytes() };
	}
	m_PerfLog->CaptureFrame(frame, assets ? &*assets : nullptr, uploads, device ? &*device : nullptr);
});
m_PerfLogRowListener = FrameProfiler::Get().AddFrameListener([this](const FrameSample& frame)
{
	if (!m_PerfLog->WriteFrame(frame))
		Application::Get().SetExitCode(1); // A requested log that is incomplete fails the run, so CI notices
}, FrameListenerTiming::WithGPU);
```

1. **Lines 231–242:** one listener captures the frame when the profiler records it, after the frame's work time is measured, so that capturing costs the frame nothing.
2. **Lines 243–247:** a second listener, called only with the GPU's times, writes the row. A log that cannot be written whole sets exit code 1, so that a build server notices.

:::example[Reading one row]
Take a row with invented numbers: `WorkMs` 12.5, `IntervalMs` 16.7, `GPUBusyMs` 9.0 and `GPUFrame` 1. The frame started 16.7 ms after the one before it, so the game runs at 60 frames a second. Its work took 12.5 ms, so the frame had 4.2 ms of waiting, because 16.7 minus 12.5 is 4.2.

The graphics card needed 9.0 ms for its stages, which also fits in the interval. The row has GPU times, so `GPUFrame` is 1. If `WorkMs` were above 16.7 for many rows, the game would miss its pace on this machine.
:::

When the game ends, the runtime flushes the rows whose GPU times will never come, closes the file and logs how many rows it wrote. A log that is incomplete fails the run.

:::note
An exported game cannot run command scripts, simulated input or expectations. They run only in the editor. A game you want to check without the editor needs its own checks: a script that quits with a code, a headless run with `--frames`, a screenshot and a perf log. The engine's plan for later waves lists automation of exported games as future work.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Ship the editor as the player, with a play flag | Small engines that have one program for all uses | One program to keep consistent | Size, start time and the editor's attack surface in every player's hands |
| Load a scene on the frame and block until it is in | Simple engines and early console games | No loading scene, no progress, no second scene in memory | A frozen or black window for as long as the load takes |
| Apply window changes at once, when a script asks | Many small engines | The change appears immediately | A swapchain that changes in the middle of a frame, and an option applied again every frame |
| Let a game run at the wall clock in every run, also for checks | Most engines' test modes | One rule for all runs | A last frame that depends on the machine, so a check cannot give a stable answer |
| Write the perf log row at once, with the CPU's numbers only | Simple profilers | Rows without a delay | Columns about the GPU that describe another frame |

## How it is tested

The core's tests are the `Runtime.Game` suite in `StrataTests/src/Runtime/GameRuntimeTests.cpp`. They run a real game from a pack with no window: a game opens at once and starts its scene when the load is in. The loading scene plays and gives way. The played time counts only steps after the start. A run that keeps every fixed step plays the same clock on long frames.

A switch keeps the running scene playing until the next is in. A failed start does not start. A switch is timed in the scene-load stage while the replaced scene dies on a background thread. `Runtime.GameGraphics` covers the graphics options, `Runtime.FramePerfLog` and `Runtime.PerfLog` the log, and `GPU.Runtime.GameRenderer` the drawing, on the shared device.

The program's tests are CTests named `StrataRuntime.*`, defined in `StrataTests/CMakeLists.txt`. `StrataRuntime.Arguments.Help` and `StrataRuntime.Arguments.Unknown` check the usage and exit code 3, the `StrataRuntime.Invalid*` tests refuse a wrong value, and `StrataRuntime.HeadlessPacing` checks the 60 frames a second. `StrataRuntime.NoTooling` reads the linker map, and `StrataRuntime.NoCameraScreenshot` checks that the missing-camera frame fails the run. The ones that need an exported game share a fixture that exports a small game once. Run the unit tests with `StrataTests.exe --test-suite=Runtime*` and the program's tests with `ctest --preset windows-debug -R StrataRuntime`.

## Changing it safely

New runtime behavior has two homes. A behavior that needs no window belongs in `GameRuntime`, so that headless runs and tests reach it. A behavior that needs the window or the renderer belongs in `RuntimeLayer`, and in `GameRenderer` or `GameWindowService` when it is large.

To add an option, change three places. Add a row to `c_Arguments`, which gives it a usage line and lets `FindUnknownArgument` accept it. Validate its value in `CheckOptions`, and refuse combinations that cannot work. Read it in `CreateApplication`, and carry it in `RuntimeOptions`. Then add a `StrataRuntime` test that runs it, and one for its mistake.

Keep these rules, each with its reason.

- Every failure in `GameRuntime::Create` returns an error, and never asserts, since a bad file is not a programmer's mistake.
- Scenes that will run load with `PrepareSystems`, and loading work draws from the frame's `SceneWorkBudget`, so that a switch cannot make a long frame.
- Scenes are let go with `Scene::ReleaseInBackground`.
- Window requests wait for `ApplyRequests`.
- A run that ends by itself keeps every fixed step.
- Games link no tooling, and `StrataRuntime.NoTooling` proves it.
- A new fact that the log needs becomes a column group, and a group that writes another number of values than it names fails the log.

## Summary

- `CreateApplication` checks the command line first (exit code 3), finds the manifest and chooses the modules. `GameRuntime::Create` then reads the pack, the scripts, the saves and the graphics options, and every failure is an error with exit code 1.
- The kind of run sets the switches: a windowed game slows time instead of dropping steps and draws between steps. A run that ends by itself keeps every fixed step. A headless run has no renderer and a cap of 60 frames a second.
- A scene switch loads in the background and swaps in only when it is ready, so the window is never black or stale. A failed switch is logged, and the running scene continues. The window changes only between frames, and only when a request differs from its state.
- A perf log captures a frame when it ends and writes its row when the GPU's times arrive. Compare only runs that end by the same rule, because frames and game time depend on the machine in different ways.
- To add a runtime option you add a row to `c_Arguments`, a check in `CheckOptions`, a read in `CreateApplication` and a test.

## Check yourself

1. A build server runs `StrataRuntime --game Coin.stgame --headless --quality low`. What happens, and with which exit code?

   :::answer{tests="run-kinds,trace-start"}
   The run ends before anything starts, with exit code 3. `CheckOptions` refuses `--quality` in a headless run, since the run draws nothing, and the program prints the problem and the usage. No log file, window or game exists yet.
   :::

2. A script crashes during a game. Which is right? (a) The window closes and the exit code is 2. (b) A windowed game runs on without its scripts, and a headless one ends with exit code 2. (c) Both end with exit code 1.

   :::answer{tests="run-kinds"}
   Option (b). The runtime disables the scripts for the session and logs the crash once. A windowed player still sees the game, so it runs on. Nobody watches a headless run, so it ends with code 2. Option (a) is right only for the headless case, and option (c) is the code for a game that cannot start.
   :::

3. A script asks for level 2 in every update while a button is held, and the load takes 40 frames. How many loads start, and what does the player see meanwhile?

   :::answer{tests="scene-switch"}
   One load starts. A request for the scene that is already loading keeps its load, so starting over never happens. The player keeps seeing the running scene, and the script can read the load's progress.
   :::

4. A game ends by itself with `--seconds 3` on a computer whose frames take 100 ms. The scene runs 60 steps a second and allows 8 steps an update. How many frames does the run take?

   :::answer{tests="measure,run-kinds"}
   A frame of 100 ms would hold six steps, which is under the limit of 8, so each frame plays 6 steps (6 steps a frame is 0.1 s). Three seconds are 180 steps, so the run takes 30 frames.
   :::

5. A perf log row for frame 200 shows the frame's work time, a `GPUFrame` of 0 and empty :term[GPU stage]{id=gpu-stage-strata} columns. What does it mean?

   :::answer{tests="measure"}
   The row was written without the GPU's times for that frame, since they never arrived. The processor's numbers describe frame 200, and the GPU columns are empty, not zero, so nobody reads a missing measurement as a fast one. A frame at the very end of a run can lack them.
   :::

6. You add a row for `--mute` to `c_Arguments` and read the flag in `CreateApplication`, but write no check. What does the option `--mute` do, and what does the wrong name `--mutee` do?

   :::answer{tests="add-option"}
   `--mute` is accepted, because the table lists it, and a flag needs no value check. `--mutee` is in no row, so `FindUnknownArgument` reports it, and the run ends with exit code 3 and the usage before anything starts.
   :::

## Exercises

1. **Basic.** Run a built game headless with `--frames 300`, and again with `--seconds 5`. Which of the two runs plays an amount of game time that depends on the machine, and which has a frame count that depends on it? Use the toy to explain.

   :::answer[Worked solution]{tests="measure,run-kinds"}
   The run with `--frames 300` ends after a fixed number of frames, so its game time depends on how many steps one frame plays, which depends on the frame's length. The run with `--seconds 5` ends after a fixed amount of game time, so its number of frames depends on the machine. The code that decides is in `RuntimeLayer::OnUpdate` in `StrataRuntime/src/RuntimeApplication.cpp`: `lastOfFrames` counts frames and `playedEnough` reads `GetPlayedSeconds`. A headless run is capped at 60 frames a second, so on a machine that holds the pace, both give 5 seconds and 300 frames.
   :::

2. **Medium.** Write a toy window service that applies requests once per frame and logs only a change. Run it for four frames in which a game asks every frame for the same size, and in frame 2 also for another size first.

   :::answer[Worked solution]{tests="scene-switch,run-kinds" solution="sketches/worlds-runtime-window.cpp"}
   The service keeps the latest request of each kind and applies it in `ApplyRequests`. It compares each request with the window's state, and it logs only when something changed. In frame 1 the width equals the window's, so nothing happens. In frame 2 the latest request wins, 1600, so the window changes once. Frames 3 and 4 ask for 1600 again and change nothing.

   ```cpp sketch="worlds-runtime-window.cpp"
   // A toy window service: requests wait until the frame's end, the latest of each kind wins, and a request the window
   // already meets changes nothing and says nothing.
   #include <cstdio>
   #include <optional>

   struct ToyWindow
   {
   	int Width = 1280;
   	bool VSync = true;
   };

   class ToyWindowService
   {
   public:
   	explicit ToyWindowService(ToyWindow& window)
   		: m_Window(window)
   	{
   	}

   	void SetWidth(int width) { m_PendingWidth = width; }
   	void SetVSync(bool enabled) { m_PendingVSync = enabled; }

   	void ApplyRequests(int frame)
   	{
   		bool changed = false;
   		if (m_PendingWidth && *m_PendingWidth != m_Window.Width)
   		{
   			m_Window.Width = *m_PendingWidth;
   			changed = true;
   		}
   		if (m_PendingVSync && *m_PendingVSync != m_Window.VSync)
   		{
   			m_Window.VSync = *m_PendingVSync;
   			changed = true;
   		}
   		if (changed)
   			std::printf("frame %d: window %d wide, vsync %s\n", frame, m_Window.Width, m_Window.VSync ? "on" : "off");
   		m_PendingWidth.reset();
   		m_PendingVSync.reset();
   	}
   private:
   	ToyWindow& m_Window;
   	std::optional<int> m_PendingWidth;
   	std::optional<bool> m_PendingVSync;
   };

   int main()
   {
   	ToyWindow window;
   	ToyWindowService service(window);
   	for (int frame = 1; frame <= 4; frame++)
   	{
   		// A game that asks for its options in every update, and from frame 2 on wants 1600. In frame 2 it also asks for
   		// 1920 first: the latest request wins.
   		if (frame == 2)
   			service.SetWidth(1920);
   		service.SetWidth(frame >= 2 ? 1600 : 1280);
   		service.SetVSync(true);
   		service.ApplyRequests(frame);
   	}
   	return 0;
   }
   ```

   ```text output-of="worlds-runtime-window.cpp"
   frame 2: window 1600 wide, vsync on
   ```

   1. **Lines 20–21:** a request is only stored, so a script may ask at any moment of its update.
   2. **Lines 26–35:** each request is compared with the window's state, so a request that changes nothing is not applied.
   3. **Line 37:** only a real change is reported.
   4. **Lines 38–39:** every request is cleared after one application, so the latest request of a frame is the one that counts.

   The engine's `ApplyRequests` does the same, with a real window and with the extra rule for a resolution.
   :::

3. **Medium.** Trace it yourself. Find where a script's `Game::LoadScene` becomes a running scene.

   :::answer[Worked solution]{tests="scene-switch"}
   Put a breakpoint in `GameRuntime::HandleSceneRequests` in `Strata/src/Strata/Runtime/GameRuntime.cpp`: it takes the scene's load request. Another in `GameRuntime::UpdateSceneLoads` shows the request advancing, and one in `GameRuntime::StartScene` shows the swap once the load is ready. A :term[Tracy]{id=tracy} capture of the run shows the scene-load stage on the frames between.
   :::

4. **Hard.** Add a `--mute` option that makes a windowed game run its audio on the null device. Say what you change, and what tests you add.

   :::answer[Worked solution]{tests="add-option"}
   In `StrataRuntime/src/RuntimeApplication.cpp`, add the row `{ "--mute", nullptr, "Mix the game's sound without a device" }` to `c_Arguments`, so that the usage shows it and `FindUnknownArgument` accepts it. `CheckOptions` needs no value check for a flag. In `CreateApplication`, pass `commandLine.HasFlag("--mute")` together with the headless flag to the audio module's `NullDevice` field. Then add two tests beside `StrataRuntime.Arguments.Help` in `StrataTests/CMakeLists.txt`: one whose expected output of `--help` contains `--mute`, and one that runs an exported game with `--mute --frames 30` and expects exit code 0. Make that run windowed, since a headless one mixes on the null device anyway.

   Check that both fail when the row is missing: the help then lacks `--mute`, and the run exits with code 3 as an unknown argument.
   :::

## Where it lives in Strata

- `StrataRuntime/src/RuntimeApplication.cpp`: `RuntimeLayer`, `CheckOptions`, `c_Arguments`, `GetProgramRun`, `CreateApplication`, and the exit codes.
- `StrataRuntime/CMakeLists.txt` and `StrataRuntime/StrataRuntime.rc.in`: the Windows build, the icon and the linker map.
- `Strata/src/Strata/Runtime/GameRuntime.h` and `GameRuntime.cpp`: `GameRuntime`, `GameRuntimeOptions`, `Create`, `UpdateSceneLoads`, `Update`, `HandleSceneRequests`.
- `Strata/src/Strata/Runtime/GameRenderer.cpp`, `GameWindowService.cpp` and `FramePerfLog.h`.
- Tests: `StrataTests/src/Runtime/GameRuntimeTests.cpp`, `FramePerfLogTests.cpp`, `GPUGameRendererTests.cpp`, and the `StrataRuntime.*` tests in `StrataTests/CMakeLists.txt`.
- Commands: `StrataRuntime --help`, `--headless`, `--frames`, `--seconds`, `--perf-log`.

## Further reading

- Glenn Fiedler, "Fix Your Timestep!", on Gaffer On Games: why game time is counted in fixed steps; intermediate.
- Robert Nystrom, "Game Loop", in Game Programming Patterns: the loop that a runtime runs; beginner.
