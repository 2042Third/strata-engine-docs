---
id: editor/program
title: "The editor is a program: core, UI and host"
description: "Why Strata's editor is a separate program from the game, why its state lives in a core without UI, and what one editor frame does in order."
kind: concept
size: M
tracks: [E]
needs: [world/systems, core/windows-events, core/layers-registries]
time: 50
learn:
  - id: why-separate
    text: explain why an editor is a separate program from the game it makes
  - id: three-layers
    text: name the three layers of the editor and say which one a change belongs in
  - id: editor-frame
    text: trace one editor frame in order and say why command polls run before the views render
  - id: run-modes
    text: name the ways the editor runs and the exit code of a bad argument
since: 0.3.0
status: final
---

In [Your first game](../start/first-game.md) you pressed Play, stopped, moved a cube and pressed Play again, and the scene you edited stayed safe. You did that in a window full of panels. Someone has to write all of that: the panels, the buttons that place a cube, the list of what you changed, the copy of the scene that Play runs.

A game needs levels, objects and settings made by people who do not program. The tool that makes them is a large program in its own right. This page asks where that program lives, how it is built, and what it does in one frame.

## A menu inside the game breaks quickly

The first idea is the cheapest. Put a debug menu in the game: press a key, and a window opens that lets you move objects and change values. Many games start this way.

Then the questions begin. A designer moves a crate and wants it to stay there: the menu needs a save format and a place to save. The designer moves it again by mistake: the menu needs undo. A second designer wants a list of every object, a search box and a way to see what an object is made of. Each question adds code, and the code lives inside the game.

Now the game ships. Every player downloads the menu code, its fonts and its windows, none of which they need. Worse, the menu can reach every part of the game's state, so it can break the game in ways the game's own rules forbid. The tool and the product have different jobs: the tool changes content and must be safe to experiment in, and the product runs content and must be small and fast.

## An editor is a second program

The idea Strata uses is plain. An **editor** is a separate program that links the same engine as the game and holds the content you make. It plays that content in place, and the exported game omits it.

The editor links the same engine. A scene looks and moves in the editor as it does in the game, because the same code draws and moves it. The editor holds the content: the project, the scene you edit, the list of changes you can undo. It plays the content in place: Play makes a copy of the scene and runs it with the engine's own systems, so you test the game without leaving the tool.

:::why[Why is the editor a client of the engine and not part of it?]
A tool built into the engine's core would ship with every game, and every change to the tool would risk the engine. A client keeps the dependency one way: the editor knows the engine, the engine never knows the editor. The cost is that the editor needs a way to see inside the engine, and Strata pays it with the registries you met in [Layers and registries](../core/layers-registries.md).
:::

```mermaid caption="The editor and an exported game are two programs that stand on the same engine, and only the editor adds tools." alt="Two boxes side by side. The left box, the editor program, rests on the engine and on tooling libraries. The right box, the exported game, rests on the engine alone."
flowchart TB
    subgraph E["Editor program"]
        EA["Panels, commands, project state"]
    end
    subgraph G["Exported game"]
        GA["Game scripts and content"]
    end
    T["Tooling: Dear ImGui, asset pipeline, network"]
    N["Engine: scene, renderer, physics, audio"]
    EA --> T
    EA --> N
    GA --> N
    T --> N
```

The :term[tooling layers]{id=tooling-layer} sit beside the engine, and only the editor reaches them. Dear ImGui, the library that draws the editor's windows, is a tooling layer in the :term[layer table]{id=layer-table}, so a game never links it. How it works is the topic of [immediate mode](../editor-ui/immediate-mode.md).

## How engines make content

Engines have settled on three ways to give people a content tool. Each one answers a flaw of the one before.

Editing data files by hand is the first. The content is text, and a person changes it in a text editor. It costs nothing to build and :term[diffs]{id=diff} well in :term[version control]{id=version-control}. It breaks when the content is spatial: nobody can place a tree by typing coordinates and judging the result in their head.

An external content tool with an exporter is the second. A separate application makes the content, such as a level editor or a modelling program, and an exporter writes files the game reads. It works well for art. It breaks when the tool cannot run the game's own code: the person sees the level as the tool draws it, and learns how the game shows it only after an export.

An in-engine editor is the third. The editor is a program built on the engine, so the game runs inside it. Unity, Unreal Engine and Godot work this way. It shows the content exactly as the game does and lets a person play it at once. It costs the most: the editor is a large program that must be built, tested and kept in step with the engine.

| Approach | Cost to build | Quality of the view | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Hand-edited data files | Lowest | None for spatial content | Low | Small projects, configuration |
| External tool with an exporter | Medium: tool and exporter | Good for art, weak for how the game looks | Two formats to keep in step | Studios with their own level tools |
| In-engine editor | Highest | Exact: the game runs inside | The editor tracks every engine change | Unity, Unreal Engine, Godot, Strata |

:::example[The editor of your first game, seen twice]
Open the editor as you did for the first game. A person sees one program: a Hierarchy list on the left, the Scene view in the middle, an Inspector on the right and a Content Browser at the bottom. Select the cube and the Inspector shows its position.

The engineer sees three layers. A user interface (UI) library draws the Inspector and the Hierarchy. When you type a new position, that library does not move the cube. It asks the core to change the cube's transform, and the core records an undo step and marks the scene as changed.

When you press Play, the core copies the scene and runs the copy. The third layer, the engine, draws and simulates.

Count what this gives: one cube moved means one request, one change in one place and one undo step, whoever asked. The person asked by dragging a handle; a test or an agent could ask without any window.
:::

The figure shows the Third Person sample, with a crate selected in place of the cube.

::figure{id=editor-docked}

## Model and view

Inside the editor program a second question appears, and it is older than game tools. When a button changes the scene, where does the code that changes the scene live?

The simplest answer is: in the button. The Inspector's position field reads the transform, draws a box, and when you type, writes the new number straight into the scene. It is short, but no test can reach it. To check that moving a cube works, you need a window, a mouse and a person. Every field needs its own undo code, and a second front end, a :term[command line]{id=terminal-command} or an agent, has to copy all the rules.

The repair is a pattern older than games, called model and view. The **model** holds the state and the rules; the **view** draws the state and forwards what the person does. The view never decides. In the editor the model is a core without any UI, and the UI draws it.

## Strata splits the editor into three layers

Strata builds the editor from three pieces that `StrataEditor/CMakeLists.txt` declares, and that you can name now.

The **editor core**, the library `StrataEditorCore`, is the editor without any UI. It holds the project, the scene, the selection and the undo stack, and it runs commands. It links the engine and the tooling that only editors contain, which are the asset pipeline and the network, and it links no ImGui. The sources of its folder, `StrataEditor/src/Editor/`, are the core.

The interface library, `StrataEditorUI`, draws the core. It holds `StrataEditor/src/UI/`, `StrataEditor/src/Panels/` and `EditorLayer`, and it links the core and ImGui. It never touches the application directly. It reaches it through the **editor host**, the interface `EditorHost`. The host lists what the UI needs from the program that runs it: close the application, set the :term[exit code]{id=exit-code}, count frames, set the window title, and take a screenshot.

The :term[executable]{id=executable}, `StrataEditor`, is one file: `EditorApplication.cpp`. It reads the command line, builds the application and implements `EditorHost` on top of `Application`. The start sequence of [The first frame](../core/first-frame.md) is all that file does.

```mermaid caption="The editor is three layers over the engine, and each layer only calls the one below it." alt="Four boxes stacked. From the top: the editor executable, the interface library, the core library and the engine. A dotted arrow to a small box beside them shows that the interface library reaches the application through the host."
flowchart TB
    A["StrataEditor: one file, builds the application and the host"]
    B["StrataEditorUI: panels, EditorLayer, ImGui"]
    C["StrataEditorCore: EditorContext, commands, undo"]
    D["Strata engine and tooling layers"]
    H["EditorHost: window, frame count, close"]
    A --> B
    B --> C
    C --> D
    B -.-> H
    A -. implements .-> H
```

A **`EditorContext`** is the class that holds all editor state, on the :term[main thread]{id=main-thread} only, so that every operation goes through it. It is the central object of the core. The UI owns no state of its own that matters. It reads the context to draw, and it calls commands on the context to change it.

:::why[Why two libraries and not one?]
Tests need the core without a window and without a :term[graphics card]{id=gpu}, and the UI needs ImGui, which the core must not know. Two :term[static libraries]{id=static-library} enforce this in the build: the core cannot include a UI :term[header]{id=header}, because the core does not link it. The UI is a library too, so a test can draw it without a window, through a fake host. The cost is an interface to maintain, `EditorHost`, and a rule that every UI action passes through the core.
:::

`editor.screenshot {path, overwrite, panel}` shows the route from the core to the window. It takes a picture of the whole editor window or of one panel. The core cannot draw, so `EditorLayer` registers the command in the core's `EditorCommandRegistry`, and its handler asks the host for the pixels through `EditorHost::RequestWindowReadback`.

Now you can say which layer a change belongs in. A rule about what the editor may do, such as refusing to delete an asset that something uses, belongs in the core. A new panel, a colour or a shortcut belongs in the UI. A new need from the window, such as the exit code, belongs in the host and in the executable that implements it. Later pages teach the core's commands in [Editor commands](../editor/commands.md) and the UI's drawing in [The shell](../editor-ui/shell.md).

## What the context holds

`EditorContext` is large, and each later page of this part takes a piece of it. This tour names each piece once.

- The project and its `EditorAssetManager`: which folder is open, and every asset in it.
- The edited scene, and the running copy that Play creates and Stop discards.
- The play state, which says whether the editor is editing, playing or simulating.
- The selection: the entities you picked, kept in order.
- The inspection target: the entities or the one asset the Inspector shows.
- The undo stack, and the recovery journal that keeps scene changes not yet saved.
- The `DocumentSaver`, which writes files in the background.
- The viewport, the simulated input for the game and the game window.
- The command journal, the notifications and the thumbnails.
- The script engine and builder, and the export.

Two of these are small enough to look at closely, because the UI depends on how they change. The selection is a vector of entity identifiers that keeps the order you clicked, and a :term[hash]{id=hash} set beside it makes `IsSelected` a constant-time check. It carries a version number that grows on every change. The inspection target has a version too. A panel never compares the whole selection every frame: it remembers the last version it drew and draws again only when `GetSelectionVersion` or `GetInspectionVersion` returns a larger number.

### Switches that make tests deterministic

A test needs the same result on every run. A real editor watches files for changes, reloads scripts when a module is rebuilt, scans assets in the background and slows a running scene when it falls behind. All of that is fine for a person and bad for a test, so `EditorContextSpecification` holds a switch for each: `WatchAssetFiles`, `HotReloadScripts`, `TimeDilation`, `Interpolation` and `ImportInBackground`. Its :term[file paths]{id=path}, such as the recent-projects file and the preferences file, are empty in a test, and the lists then stay in memory.

`WatchAssetFiles` and `HotReloadScripts` are on by default, and a test can disable them. The other three are off by default. The editor application enables `TimeDilation`, `Interpolation` and `ImportInBackground` for interactive and automation sessions, as the field comments say. A test leaves those three off, so a running scene steps exactly as many times as the test counts, and every asset is imported when the project opens.

## One editor frame, in order

The :term[frame loop]{id=game-loop} of [the application](../core/frame-loop.md) calls each layer's update once per frame, then each module's update, then the UI module's render step, which calls each layer's `OnImGuiRender`. The editor has one layer, `EditorLayer`, which is both a layer of the application and the editor's shell. Its `OnUpdate` is the editor's own frame.

```cpp src="StrataEditor/src/EditorLayer.cpp#L921-L949" from="m_Context.Update(timestep);" to="m_Panels.OnUpdate(panelContext);" symbol="EditorLayer::OnUpdate"
m_Context.Update(timestep);
// Between frames: the system's fonts for Chinese, Japanese and Korean text join the editor's once read.
if (!m_Options.Headless)
	UI::EditorFonts::UpdateFallback();
// The launcher returns when the next project closes.
if (m_Context.HasProject())
	m_LauncherDismissed = false;
m_CommandRunner.Update(m_Context);
m_Automation.Update();
UpdateCommandScript();
UpdateWindowTitle();
UpdateSteppingFrameRate();

const double now = m_Host->GetTime();
// An automation request was answered or is pending: an agent drives the editor.
const uint64_t answered = m_Automation.GetCompletedRequestCount();
if (answered != m_LastAutomationRequests || m_Automation.GetPendingRequestCount() > 0)
{
	m_LastAutomationRequests = answered;
	m_LastAutomationTime = now;
}
m_FrameTimes.push_back(now);
while (!m_FrameTimes.empty() && now - m_FrameTimes.front() > c_FrameRateWindowSeconds)
	m_FrameTimes.pop_front();
UpdateFrameStats();
if (!m_Options.Headless)
{
	EditorPanelContext panelContext = MakePanelContext();
	m_Panels.OnUpdate(panelContext);
```

1. **Line 921:** the core updates first, so every later step sees current scripts, assets and scene.
2. **Line 928:** the command runner polls its waiting commands here, before any panel exists in this frame.
3. **Lines 929–930:** automation takes new requests and the command script runs its next step.
4. **Lines 946–949:** the panels update only when the editor has a window.

Before the excerpt, the layer records the last frame's time and applies the interface scale the person chose. The excerpt then runs in a fixed order. The core updates first, so that scripts, assets, saves and the running scene are current. Then the command runner polls the commands that wait for something, such as a script build. Automation reads new requests, and the command script runs its next step.

The panels update last, and only when the editor has a window.

The panels draw later in the same frame. The UI module's render step calls `OnImGuiRender` after every layer has updated. Every command poll of a frame therefore runs before any view renders in it.

```mermaid caption="Inside one frame, the core and every command poll finish before the views render." alt="A left-to-right sequence of one frame. Boxes in order: last frame time, core update, command polls, automation, command script, panel update, then the views render."
flowchart LR
    A["Last frame's time"] --> B["Core update"]
    B --> C["Command polls"]
    C --> D["Automation requests"]
    D --> E["Command script"]
    E --> F["Panel update"]
    F --> G["Views render"]
```

Why does the order matter? Suppose a command ends in frame 10: a script build finishes and the command's answer changes the scene. If the views rendered first, they would draw frame 10 with the old scene, and the person would see the change a frame late. Worse, a client such as an agent would ask for a capture and receive a picture that contradicts the answer it had been given. Polling first makes the answer and the picture agree in the same frame.

After the excerpt, the function checks three ways to end. The command `editor.quit` has already checked for changes not yet saved, so its frame closes the host. An idle timeout closes an editor that a vanished tool started. A frame limit ends a scripted run, and a command script that has not finished sets the exit code to 1, so a scripted run never looks successful by running out of frames.

## The ways the editor runs

One executable serves several jobs, and the command line chooses. The full table of options is in [the editor reference](../reference/editor.md); here are the four ideas.

A window is the default: the editor opens a window, creates a graphics device and draws the UI, as in the first game.

Headless is the second. [The first frame](../core/first-frame.md) defines the word for an application as a run without a window.

The editor has two options that begin it, and they differ. `--headless` runs without a window and keeps the graphics device, so captures and thumbnails still work. `--no-gpu` runs without a graphics device and implies `--headless`. Automation that needs no rendering, such as an export on a machine with no graphics card, uses it.

In both, the panels do not update and the sound mixes without a device. The :term[frame rate]{id=frame-rate} is capped at 60 frames per second, so the editor does not spin a :term[processor core]{id=processor-core} while it waits for a client.

Scripted is the third: `--commands` names a :term[JSON]{id=json} file of commands that run one after another at startup, and `--quit-after-commands` closes the editor when the script finishes. It suits tests and continuous integration, where nobody sits at the window.

The fourth is the refusal. The command line may hold an argument the table does not know, a flag given a value, or an option without its value. Then the editor prints what is wrong and its usage to :term[standard error]{id=standard-error}, and ends with exit code 3.

No log file, window or automation session exists yet. Exit code 3 is `CommandLineOptions::c_UsageExitCode`, which the :term[runtime]{id=runtime} uses too, and the command-line client ends its usage errors with the same number. `--help` and `--version` print and end with code 0.

## What this choice cannot do

A core with no UI costs extra steps. A cube drag that a UI could write in two lines becomes a request, a command and an undo step, and a new feature needs both a command and a panel.

The split does not make the editor small: the context is a large class that the later pages open piece by piece. It does not make the engine independent of the editor either, because the editor still needs engine hooks. [What Strata does not do](../appendix/not-in-strata.md) lists what the editor leaves to other tools.

## Common mistakes

- Putting a rule in a panel. Symptom: the rule holds in the UI and not for a test or an agent. Fix: move the rule into the core and make the panel call it.
- Writing scene data from a panel. Symptom: the change has no undo step and a save may skip it. Fix: change the scene through a command.
- Reaching the application from the UI. Symptom: a UI test needs a window. Fix: add the need to `EditorHost`, so a fake can answer it.
- Believing the editor is the engine. Symptom: you search for editor code in an exported game. Fix: remember that the editor is a client, and the game links the engine and no tooling.
- Treating `--headless` and `--no-gpu` as one. Symptom: a capture fails under `--no-gpu`. Fix: use `--headless` when you need pictures.

## Summary

- An editor is a separate program that links the same engine, holds the content, plays it in place and stays out of the exported game, because tool and product have different jobs.
- The editor has three layers. The core keeps state and logic in `EditorContext`, the UI draws it and calls the application only through `EditorHost`, and the executable is one file. A rule belongs in the core, a look in the UI and a window need in the host.
- One editor frame runs the core update, the command polls, automation, the command script and the panel update, and only then do the views render.
- The editor runs in a window, headless (`--headless` keeps the graphics device, `--no-gpu` drops it) or scripted with `--commands`, and a bad argument ends with exit code 3.

## Check yourself

1. A rule says that a prefab may not be deleted while a scene uses it. Where does the rule go? (a) In the Content Browser's delete button; (b) in the core, where the delete command is; (c) in `EditorHost`; (d) in the executable.

   :::answer{tests="three-layers"}
   (b). The core holds rules, so a person, a test and an agent all meet them. (a) fails because an agent never presses the button. (c) is wrong because the host only offers window and frame services. (d) is wrong because it only starts the application.
   :::

2. Why does the exported game contain no editor?

   :::answer{tests="why-separate"}
   The editor is a separate program that links the engine; the game links the engine and no tooling layer. Players would otherwise carry code they never use, and a tool that can reach every state could break the game's rules.
   :::

3. In frame 10 a command poll finishes a script build. Do the panels draw frame 10 with its result or without it? Say which function runs first.

   :::answer{tests="editor-frame"}
   With it. `EditorLayer::OnUpdate` runs the command runner's poll, and `OnImGuiRender` runs afterwards, because the UI module renders only after every layer has updated.
   :::

4. A build agent runs the editor on a machine with no graphics card to export a game. Which option does it pass, and what must it not expect?

   :::answer{tests="run-modes"}
   The agent passes `--no-gpu`, which implies `--headless`. It must not expect captures or thumbnails, because there is no graphics device.
   :::

5. You start the editor with an option it does not have. What happens, and what is the exit code?

   :::answer{tests="run-modes"}
   The editor prints the problem and its usage to standard error and ends before opening a window or a log file. The exit code is 3, the value of `CommandLineOptions::c_UsageExitCode`.
   :::

## Exercises

1. **Basic.** Run the editor with an argument it does not know, and read its exit code. Say why no window opened.

   :::answer[Worked solution]{tests="run-modes"}
   On Windows the editor is a window-subsystem program, so PowerShell does not wait for it unless you ask. Run `(Start-Process .\build\windows\bin\Debug\StrataEditor.exe -ArgumentList '--bogus' -Wait -PassThru).ExitCode` from the Strata folder. On Linux or macOS, run `./build/linux/bin/Debug/StrataEditor --bogus; echo $?`. Both print 3. No window opened because `EditorApplication.cpp` checks the arguments before it builds the application, and returns `CommandLineOptions::c_UsageExitCode`.
   :::

2. **Medium.** With a debugger, set a breakpoint in `EditorLayer::OnUpdate`, open a project and follow one frame. Name the line where the command polls run, and say what has not been drawn yet.

   :::answer[Worked solution]{tests="editor-frame"}
   Attach the debugger as [Debugging the engine](../core/debugging.md) describes, and break at the start of `EditorLayer::OnUpdate` in `StrataEditor/src/EditorLayer.cpp`. Step over until the call `m_CommandRunner.Update(m_Context);`. That is the poll. Nothing of this frame is drawn yet: `OnImGuiRender`, the function that draws the panels, has not been called, and it runs after the layer's update returns.
   :::

3. **Hard.** Write a toy editor with three parts: a core that holds a selection and a queue of requests, a UI that polls the core and then draws it, and a host that a test supplies. Run it without a window for three frames.

   :::answer[Worked solution]{tests="three-layers editor-frame" solution="sketches/editor-program-toy.cpp"}
   The core never prints, the UI never changes the selection by itself, and the fake host ends the run.

   ```cpp sketch="editor-program-toy.cpp"
   // A toy editor in three parts: a core with no UI, a UI that only calls and draws it, and a host the UI asks for the window.
   #include <cstdio>
   #include <string>
   #include <vector>

   namespace
   {

   	class Host
   	{
   	public:
   		virtual ~Host() = default;
   		virtual bool IsRunning() const = 0;
   		virtual void Close() = 0;
   		virtual int GetFrameCount() const = 0;
   	};

   	// All state and logic: no printing of its own, no host.
   	class Core
   	{
   	public:
   		void Queue(const std::string& name) { m_Queue.push_back(name); }

   		void Poll()
   		{
   			for (const std::string& name : m_Queue)
   			{
   				m_Selection.push_back(name);
   				++m_SelectionVersion;
   			}
   			m_Queue.clear();
   		}

   		const std::vector<std::string>& GetSelection() const { return m_Selection; }
   		int GetSelectionVersion() const { return m_SelectionVersion; }

   	private:
   		std::vector<std::string> m_Queue;
   		std::vector<std::string> m_Selection;
   		int m_SelectionVersion = 0;
   	};

   	// Draws the core and calls it; it never changes the core's data itself.
   	class Ui
   	{
   	public:
   		explicit Ui(Host& host)
   			: m_Host(host)
   		{
   		}

   		void Update(Core& core)
   		{
   			core.Poll();
   			std::printf("frame %d: polls done\n", m_Host.GetFrameCount());
   		}

   		void Render(const Core& core)
   		{
   			std::printf("frame %d: draw %zu selected, version %d\n", m_Host.GetFrameCount(), core.GetSelection().size(),
   				core.GetSelectionVersion());
   			if (m_Host.GetFrameCount() == 2)
   				m_Host.Close();
   		}

   	private:
   		Host& m_Host;
   	};

   	// A host without a window, as a test supplies it.
   	class FakeHost : public Host
   	{
   	public:
   		bool IsRunning() const override { return m_Running; }
   		void Close() override { m_Running = false; }
   		int GetFrameCount() const override { return m_Frames; }
   		void EndFrame() { ++m_Frames; }

   	private:
   		bool m_Running = true;
   		int m_Frames = 0;
   	};

   }

   int main()
   {
   	Core core;
   	FakeHost host;
   	Ui ui(host);
   	core.Queue("Cube");
   	while (host.IsRunning())
   	{
   		if (host.GetFrameCount() == 1)
   			core.Queue("Lamp");
   		ui.Update(core);
   		ui.Render(core);
   		host.EndFrame();
   	}
   	return 0;
   }
   ```

   ```text output-of="editor-program-toy.cpp"
   frame 0: polls done
   frame 0: draw 1 selected, version 1
   frame 1: polls done
   frame 1: draw 2 selected, version 2
   frame 2: polls done
   frame 2: draw 2 selected, version 2
   ```

   1. **Lines 9–16:** the host interface lists only what the UI needs, so a fake can stand in for a window.
   2. **Lines 24–32:** the core changes the selection and raises its version; it never prints.
   3. **Lines 52–56:** the UI polls the core before anything draws, as the editor's frame does.
   4. **Lines 58–63:** drawing only reads the core; the fake host ends the run at frame 2.
   5. **Lines 96–97:** the loop calls the update step, then the render step, in that order.
   :::

## Where it lives in Strata

- `StrataEditor/CMakeLists.txt` builds `StrataEditorCore`, `StrataEditorUI` and the `StrataEditor` executable.
- `StrataEditor/src/Editor/EditorContext.h` declares `EditorContext` and `EditorContextSpecification`.
- `StrataEditor/src/EditorHost.h` declares `EditorHost`; `StrataEditor/src/EditorApplication.cpp` implements it as `ApplicationEditorHost`.
- `StrataEditor/src/EditorLayer.cpp` holds `EditorLayer::OnUpdate` and `EditorLayer::OnImGuiRender`, and registers `editor.screenshot`.
- `Strata/src/Strata/Core/CommandLineOptions.h` holds `CommandLineOptions::c_UsageExitCode`.
- `StrataTests/Architecture/Layers.json` marks the `ImGui` layer as tooling.

## Further reading

- Game Programming Patterns, "Model View Controller" and related chapters: the old pattern of this page, in game terms (intermediate).
- Game Engine Architecture, the chapter on tools and the asset pipeline: how studios build and connect content tools (advanced).
- The Unity, Unreal Engine and Godot manuals' pages on the editor and the exported game: what each engine's editor does and what stays out of its games (beginner).
