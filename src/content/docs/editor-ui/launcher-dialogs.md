---
id: editor-ui/launcher-dialogs
title: "Launcher and dialogs"
description: "The screens around the editing: the launcher, the project dialogs, About, Export, Recover, Delete and New Script, and how they run commands and ask again."
kind: internals
size: L
tracks: [E]
needs: [editor-ui/shell, editor/projects, editor/recovery, editor/trash-references, worlds/export]
time: 80
learn:
  - id: command-per-button
    text: name the command that each button of the launcher and the project dialogs runs
  - id: re-ask
    text: explain why a dialog asks again when the scene changed after the person answered
  - id: read-off-thread
    text: explain how the launcher reads the recent projects and their pictures without blocking a frame
  - id: export-hide
    text: compare what Cancel Export and Hide do while an export runs
  - id: agent-states
    text: name the four states of the agent card and what causes each
since: 0.3.0
status: final
---

The **launcher** is the screen the editor shows while no project is open. Around it stand the dialogs that start, finish or guard work: New Project, Open Sample, About Strata, Export Game, **Recover Unsaved Changes**, Delete and New Script. This page explains how they are built, so that you can change one without breaking the rules they share.

The launcher and the dialogs draw state and collect choices. They never change a project themselves: every action they take is a command, and every question they ask goes through the editor's one question machinery. The page does not explain what a project, a template or a recent project is, how an export works, how recovery data is written, or why a delete can be refused. The pages that own those subjects come first in your reading.

## The problem and how engines solve it

A person who starts an editor has no project yet, so every panel the editor owns has nothing to show. Something must still fill the window and offer the first step: create a project, open one, or look at a finished game. After that first step the editor keeps asking small questions in dialogs: where to put a copy, whether to throw away changes, which folder to export to.

These screens look simple, but three demands make them hard. The first demand is speed: a frame of the editor lasts 16.7 ms at 60 :term[frames per second]{id=frame-rate}, and a start screen that reads a network share to draw a picture can stall for seconds. The second is safety: the person may hold work not yet saved when they press New Project, and an agent may change the scene while a dialog waits. The third is reach: artificial intelligence (AI) agents drive the editor through commands, so a button that does something no command can do is a feature that agents never reach.

Engines solve the first step in three ways. Some ship a separate program for it. A separate program can show projects made with several engine versions and can start the right editor for each. It costs a second program to install and update, and it knows nothing about the state of a running editor.

Some engines draw the start screen inside the editor's own window, as a window that fills the space the panels would use. The editor already has the :term[fonts]{id=font}, the theme and the widgets, and the same binary shows the screen. The cost is that the start screen shares a process, and so a frame, with everything else.

Some engines use the :term[operating system's]{id=operating-system} own file and message dialogs. Those look native and cost no code. They also block the program's :term[frame loop]{id=game-loop} until the person answers, and a :term[modal]{id=modal} system dialog cannot show a progress bar or react to an export that an agent started.

Strata takes the second way. The launcher is an editor panel in a special placement, and the dialogs are modal windows drawn by the editor's own interface library.

Strata pays for that choice in two ways. Nothing may wait inside a frame, so every slow read moves to a job. Nothing may assume the answer to a question stays true, so a dialog must check again before it acts. The rest of the page shows how each cost is paid.

## The map

Two kinds of code draw these screens. The launcher is a panel, the `WelcomePanel` in `StrataEditor/src/Panels/WelcomePanel.cpp`, registered in the **Launcher** placement. A panel of that placement has no menu item and no saved window state. `EditorLayer` draws it in place of the :term[dock space]{id=dock-space} whenever no project is open.

The dialogs live in `StrataEditor/src/UI/`: `ProjectDialogs`, `AboutDialog`, `ExportDialog`, `RecoveryDialog`, `ScriptDialogs` and `DeleteAssetDialog`. `EditorLayer` calls the `Draw` function of most of them every frame, after the panels, so a dialog stands over the launcher and over the docked panels alike.

One exception matters. The Delete dialog belongs to the Content Browser panel, which opens and draws it, because only that panel knows which asset or folder the person chose. The other dialogs belong to `EditorLayer`.

```mermaid caption="Each frame the editor layer draws the launcher or the docked panels, then the dialogs. Panels and dialogs reach the editor through the shell and run commands. Slow reads leave the frame as jobs and return as results that a later frame polls." alt="A flow of boxes. The editor layer leads to the launcher when no project is open and to the dock space when one is open. It also leads to the dialogs. The launcher and the dialogs lead to the editor shell, which leads to the command registry. A dashed arrow from the launcher goes to a background job that reads files, and a dashed arrow from the job returns to the launcher."
flowchart TD
    Layer["EditorLayer, each frame"] -->|no project| Launcher["WelcomePanel"]
    Layer -->|project open| Dock["Dock space and panels"]
    Layer --> Dialogs["Dialogs"]
    Launcher --> Shell["EditorShell"]
    Dialogs --> Shell
    Shell --> Commands["Command registry"]
    Launcher -.->|submits| Job["Background read"]
    Job -.->|polled later| Launcher
```

The panel and the dialogs never call `EditorLayer` directly. They receive an `EditorPanelContext` that holds the editor's state, the :term[command registry]{id=command-registry}, a runner for commands that finish over several frames and a pointer to an `EditorShell`. The shell is a small interface that `EditorLayer` implements: it shows dialogs (`ShowNewProjectDialog`, `ShowOpenSampleDialog`, `ShowAboutDialog`), asks the questions about changes not yet saved (`RequestDiscardChanges`, `RequestReleaseProject`, `DrawDiscardQuestion`) and answers facts about the running editor (`GetEnvironment`, `GetAutomationState`). When the context holds no shell, the screens run the plain forms of the commands, without `force`, so that changes not yet saved make the command fail.

The launcher itself has four parts. A **sidebar** on the left holds the mark, the three starting buttons and the link past the launcher. A **hero band** above the main area greets the person. The main area holds the :term[recent projects]{id=recent-projects}, the cards that start something new and the agent card, all in one scrolling region. A **footer** shows the build.

## The contract

Callers and authors of these screens follow six rules. Each has a reason, and the first two come from the engine's own rules for the editor.

1. A button that changes a project or a scene runs a command. Buttons that only change what the window draws, such as Copy Path or Continue without a project, do not need one.
2. A dialog that replaces the scene asks first, through the shell, and passes `force` to its command only after the person answered.
3. A dialog asks again when the scene changed after the answer.
4. A dialog that waits for a command that takes several frames uses the runner and shows what it knows each frame.
5. Slow or uncertain reads, such as files on a network share, run as jobs; the screen shows what it knows while they run.
6. A screen takes its colors, sizes and widgets from the editor's theme and :term[widget kit]{id=widget-kit}, and passes the :term[command origin]{id=origin} `CommandSource::UI` so that the activity journal shows who acted.

:::rule
Every change to the scene or the project goes through a command, and user interface (UI) code that runs one passes `CommandOrigin { CommandSource::UI }`. The reason: agents, scripts and people then share one path, and the journal and the :term[undo stack]{id=undo-stack} see every change. Read the rule in full in the engine's guide, section "Editor".
:::

:::rule
A command that replaces the edited scene refuses unless it gets `force`, and UI code passes `force` only after the person answered the question about the changes. The reason: a refused command is the last guard against silent loss, and the question is the person's only chance to save first. See [the shell's questions](shell.md) and [recovery](../editor/recovery.md).
:::

Rule 5 has a price. The dialogs do touch the disk on the :term[main thread]{id=main-thread} in two places. They test whether a folder exists when the name or the location changes, and they suggest a free project name when they open. Both are single small tests, run once per change and never once per frame. The launcher, whose reads can be slow, never touches the disk in a frame.

## A toy version

The toy below keeps the two ideas that matter most. A dialog runs one command by name through a registry, and a dialog remembers which version of the scene the person answered about, so that it can notice later changes. It has no window: a loop of frames stands in for the editor's, and `bool` arguments stand in for button presses.

:::question
New to the C++ on this page? Read [functions and loops](../basics/programming-2.md), [classes and calls](../basics/programming-3.md), [pointers and `Ref`](../basics/cpp-memory.md), [lambdas and maps](../basics/cpp-generic.md) and [modern C++](../basics/cpp-modern.md) first.
:::

The `NewProjectDialog` class stores the version of the scene at the moment the dialog opened. Its `Draw` function does nothing until Create is pressed. When Create arrives and the version differs, the dialog does not run the command: it asks again.

```cpp sketch="editor-ui-launcher-dialogs-toy.cpp"
// A toy dialog: it runs one command, and asks again when the scene changed after the person answered.
#include <cstdio>
#include <functional>
#include <map>
#include <string>

struct Editor
{
	int SceneVersion = 0;
	std::string ProjectName;
};

class CommandRegistry
{
public:
	using Command = std::function<bool(Editor&, const std::string&)>;

	void Register(const std::string& name, Command command) { m_Commands[name] = command; }

	bool Execute(Editor& editor, const std::string& name, const std::string& argument)
	{
		const auto found = m_Commands.find(name);
		return found != m_Commands.end() && found->second(editor, argument);
	}

private:
	std::map<std::string, Command> m_Commands;
};

class NewProjectDialog
{
public:
	// The person has answered the question about unsaved changes by the time the dialog opens.
	void Open(const Editor& editor) { m_AnsweredVersion = editor.SceneVersion; m_Name = "My Project"; }

	// One frame. Returns false once the dialog is done.
	bool Draw(Editor& editor, CommandRegistry& commands, bool createPressed, bool personAnswered)
	{
		if (personAnswered)
			m_AnsweredVersion = editor.SceneVersion; // the new answer covers the new changes
		else if (!createPressed)
			return true;
		if (editor.SceneVersion != m_AnsweredVersion)
		{
			std::printf("  the scene changed since the answer: asking again\n");
			return true;
		}
		const bool created = commands.Execute(editor, "project.create", m_Name);
		std::printf("  project.create %s\n", created ? "succeeded" : "failed");
		return !created;
	}

private:
	int m_AnsweredVersion = 0;
	std::string m_Name;
};

int main()
{
	Editor editor;
	editor.SceneVersion = 12;
	CommandRegistry commands;
	commands.Register("project.create", [](Editor& target, const std::string& name)
	{
		target.ProjectName = name;
		return true;
	});

	NewProjectDialog dialog;
	dialog.Open(editor);
	std::printf("frame 1: an agent creates an entity\n");
	editor.SceneVersion = 13;
	std::printf("frame 2: Create pressed\n");
	bool open = dialog.Draw(editor, commands, true, false);
	std::printf("frame 3: the person answers\n");
	open = dialog.Draw(editor, commands, false, true);
	std::printf("dialog open: %s, project: %s\n", open ? "yes" : "no", editor.ProjectName.c_str());
	return 0;
}
```

```text output-of="editor-ui-launcher-dialogs-toy.cpp"
frame 1: an agent creates an entity
frame 2: Create pressed
  the scene changed since the answer: asking again
frame 3: the person answers
  project.create succeeded
dialog open: no, project: My Project
```

1. **Line 34:** opening the dialog stores the scene's version, the moment the person has answered.
2. **Lines 39-42:** a new answer stores the current version, and a frame without a press or an answer does nothing.
3. **Lines 43-47:** a version that differs from the answered one means the answer no longer covers the scene, so the dialog asks again.
4. **Line 48:** the action is a command run by name through the registry, never code inside the dialog.

In the run, an agent changes the scene in frame 1, so the version moves from 12 to 13. Create in frame 2 finds that the answer no longer covers the scene and asks again. Only after the person answers in frame 3 does `project.create` run. The real dialogs add four things: a real question widget, templates, a location that the program remembers, and a check of the name before the button becomes active.

## The real code

The real code is told in the order that data flows. First the launcher reads its lists, then a project dialog guards its action, then the Export dialog follows a long task.

### Reading recent projects off the frame

The launcher lists the projects you opened before, with a picture each. The list lives in a file that other editors of the same person may change, and a project may sit on a drive that is gone. Looking at those paths can take seconds, so `Refresh` never looks at them itself.

The next quote submits one read to the input and output (I/O) job queue. Search for the guard that allows one read at a time, for the change count taken before the job starts, and for the fact that the job writes only into its own result object.

```cpp src="StrataEditor/src/Panels/WelcomePanel.cpp#L225-L255"
void WelcomePanel::Refresh(EditorPanelContext& context)
{
	m_RefreshedAt = ImGui::GetTime();
	ReadStarters(context);

	// Other editors of the user may have changed the list, and projects may have been deleted or gone out of reach (a
	// network share, a drive): the file and the projects are looked at on an I/O thread, since a path out of reach can
	// take seconds to answer. One read at a time; until it lands, the cards show what is known.
	if (m_RefreshJob.IsValid() && !m_RefreshJob.IsComplete())
		return;
	const RecentProjects& recent = context.Context.GetRecentProjects();
	std::vector<std::filesystem::path> known;
	for (const RecentProject& project : recent.GetAllProjects())
		known.push_back(project.Path);
	Ref<RefreshResult> result = CreateRef<RefreshResult>();
	result->ChangeCount = recent.GetChangeCount();
	m_RefreshResult = result;
	m_RefreshJob = JobSystem::SubmitIO([result, file = recent.GetFile(), known = std::move(known)]() mutable
	{
		result->File = RecentProjects::ReadFile(file);
		if (result->File.Projects)
		{
			for (const RecentProject& project : *result->File.Projects)
			{
				if (std::find(known.begin(), known.end(), project.Path) == known.end())
					known.push_back(project.Path);
			}
		}
		result->Check = RecentProjects::CheckProjects(known);
	}, JobPriority::Low);
}
```

1. **Line 233:** a read that is still running makes `Refresh` return, so reads never pile up while a slow share answers.
2. **Line 240:** the change count of the recent-project list is stored before the job starts; the job later hands it back so that the main thread can tell whether the list changed meanwhile.
3. **Lines 242-254:** the job reads the file and checks every path on a worker thread with low priority; the main thread never waits for it.

`Refresh` runs when the launcher appears and again every `c_RefreshSeconds`, which is 2.0 seconds. The result comes back through `PollRefresh`, which runs every frame and costs one test while the job is busy.

```cpp src="StrataEditor/src/Panels/WelcomePanel.cpp#L257-L279"
void WelcomePanel::PollRefresh(EditorPanelContext& context)
{
	if (!m_RefreshResult || !m_RefreshJob.IsComplete())
		return;
	const Ref<RefreshResult> result = std::move(m_RefreshResult);
	m_RefreshResult = nullptr;
	m_RefreshJob = JobHandle();

	RecentProjects& recent = context.Context.GetRecentProjects();
	m_MissingProjects = std::move(result->Check.Missing);
	if (result->ChangeCount == recent.GetChangeCount())
	{
		recent.ApplyFile(result->File);
		// Deleted projects leave the list for good; those out of reach stay on it, hidden until they are back.
		recent.Forget(result->Check.Gone);
	}
	else
	{
		// The list changed while the file was read (a project opened): the read may predate that, so read again.
		m_RefreshedAt = 0.0;
	}
	UpdateRecentProjects(recent);
}
```

1. **Line 259:** while the job runs, the function returns at once; the cards keep what is known.
2. **Lines 267-272:** the file and the verdicts apply only when the change count is still the one the job saw. Paths that are gone leave the list for good, and paths out of reach stay on it and hide.
3. **Lines 273-277:** when the count differs, a project opened in the meantime, so the file the job read may be older than that. The function drops the result and resets the refresh time, so the next frame reads again.

The pictures follow the same pattern in `GetImage`: one job per picture decodes the file into pixels, and the main thread uploads the pixels to the :term[graphics card]{id=gpu} in a later frame. When the launcher hides, the pictures are released through `Renderer::ReleaseDeferred`, because the project that was open has a new picture after its save.

### Asking before a project dialog acts

The project dialogs open after the person answered the question about the scene's changes not yet saved: `EditorLayer::ShowNewProjectDialog` calls `RequestReleaseProject` first and opens the dialog inside its action. The answer therefore describes the scene as it was when the dialog opened. The dialog may stay open for a minute while the person types a name, and the scene may change in that minute: an agent may run `entity.create`, or a save may finish. The next quote shows how the dialog keeps track.

Read `NoteAnswer` for what the dialog stores, then `MayReplaceScene` for the test and for what happens when the test fails.

```cpp src="StrataEditor/src/UI/ProjectDialogs.cpp#L221-L258"
void ProjectDialogs::NoteAnswer(EditorContext& context)
{
	// The dialogs open once the person has answered (EditorShell::RequestDiscardChanges), so what the scene holds now is
	// what they answered about.
	m_AnsweredVersion = context.GetUndoStack().GetVersion();
	m_AnsweredWrites = GetProjectFileWrites(context);
	m_Answered = false;
}

uint64_t ProjectDialogs::GetProjectFileWrites(const EditorContext& context)
{
	return context.GetProjectFileWriter() ? context.GetProjectFileWriter()->GetWriteCount() : 0;
}

bool ProjectDialogs::MayReplaceScene(EditorPanelContext& context)
{
	EditorContext& editor = context.Context;
	// The dialogs create or open a project, which releases the open one: its unwritten settings (the project file's last
	// write failed) are asked about too, for the failure the person saw.
	const bool answered = (!editor.IsSceneModified() || editor.GetUndoStack().GetVersion() == m_AnsweredVersion)
		&& (!editor.HasUnwrittenProjectSettings() || GetProjectFileWrites(editor) == m_AnsweredWrites);
	// A save in flight (an agent's scene.save while the dialog is open) is never lost: the project waits for it, as the
	// commands that replace the scene do, so that they run at once once it is written.
	if (!context.Shell)
		return !editor.HasSavesInFlight();
	if (answered && !editor.HasSavesInFlight())
		return true;
	// The scene changed since the answer, or a save writes: the person decides about these changes too (after the saving
	// dialog), over the dialog (DrawDiscardQuestion). The answer may come in a later frame; the dialog submits once it came.
	EditorContext* answeredContext = &editor;
	context.Shell->RequestReleaseProject([this, answeredContext]()
	{
		m_AnsweredVersion = answeredContext->GetUndoStack().GetVersion();
		m_AnsweredWrites = GetProjectFileWrites(*answeredContext);
		m_Answered = true;
	});
	return false;
}
```

1. **Lines 225-226:** the undo stack's version and the count of project-file writes are stored when the dialog opens, the moment the person answered.
2. **Lines 240-241:** the answer still holds when the scene has no changes or its version is unchanged, and when the project file has no new failed write.
3. **Lines 244-247:** without a shell the function only checks for saves :term[in flight]{id=in-flight}; with one, a clean answer and no save in flight let the action run.
4. **Lines 251-256:** otherwise `RequestReleaseProject` asks over the dialog. Its :term[callback]{id=callback} stores the new version and sets `m_Answered`, and `Draw` treats that flag as a press of the primary button, so the action runs by itself once the person answers.

The function returns `false` after it asks. The dialog does nothing that frame, and the question stays on screen until the person decides. A person who chooses Cancel leaves the dialog open and the scene untouched. After the answer, the dialog submits at once, and `project.create` or `project.openSample` runs with `force` set to true.

:::example[An agent edits the scene while New Project is open]
The scene is at undo version 12 when you press File ▸ New Project and answer `Don't Save`. The dialog opens with 12 stored. You type a name, and meanwhile an agent runs `entity.create`, which moves the version to 13 and marks the scene modified. You press Create.

`MayReplaceScene` sees a modified scene and a version of 13 against the stored 12, so `answered` is false. It asks again, over the dialog. You answer `Don't Save` a second time, the callback stores 13, and the dialog runs `project.create` in the next frame. If you had cancelled the second question, nothing would have happened, and the agent's entity would still be in your scene.

The price of the guard is one extra question in a rare case. The alternative is a project created over changes that nobody decided about.
:::

### Following an export, whoever started it

An export runs for seconds or minutes, and a person may press Export in the dialog or an agent may run `project.export`. The Export dialog must show the progress in both cases. It also must not stop the export when the person only wants the window out of the way.

The next quote is the part of `ExportDialog::Draw` that picks what the dialog shows and which buttons it offers. Look at how the dialog decides it is showing progress, and at the two buttons.

```cpp src="StrataEditor/src/UI/ExportDialog.cpp#L193-L215"
const Ref<GameExport>& current = context.Context.GetGameExport();
const bool running = current && !current->IsFinished();
// The dialog's own export shows its progress until its command answered (a frame after the export ended).
const bool showProgress = m_Exporting || running;
if (!context.Context.HasProject() && !showProgress)
	open = false;
else if (showProgress)
	DrawProgress(context, width);
else if (m_Finished)
	DrawOutcome(width);
else
	DrawFields(context, width);

ImGui::Spacing();
if (showProgress)
{
	// Closing the dialog leaves the export running; Cancel stops it (whoever started it).
	PlaceButtons(width, { "Cancel Export", "Hide" });
	if (UI::DialogButton("Export.Cancel", "Cancel Export", false, running))
		RunEditorCommand(context.Context, context.Commands, "project.cancelExport");
	ImGui::SameLine();
	if (UI::DialogButton("Export.Hide", "Hide"))
		open = false;
```

1. **Lines 193-196:** the dialog asks the editor for the current export object, whoever created it, and shows progress when its own command is waiting or the export is not finished.
2. **Lines 199-200:** with progress to show, the dialog calls `DrawProgress`, which draws the stage name and a bar from the export's own progress value.
3. **Lines 210-212:** Cancel Export runs `project.cancelExport`, which stops the export even when an agent started it. The button is disabled once the export has ended.
4. **Lines 214-215:** Hide only closes the dialog. The export keeps running, and the **Export** button at the top of the window then has the tooltip "Show the running export".

Two more functions complete the picture. `WatchExports` notices an export that a command started while the dialog was open or opening, and shows its progress and, later, its outcome. `StartExport` collects the fields into the parameters of `project.export` and runs it through the runner, so the frame loop never waits.

## The screens one by one

Each screen below names its commands, so that by the end you can tell what every button runs.

### The launcher

The sidebar's top button, **New Project**, calls `ShowNewProjectDialog`, which asks the shell and then opens the dialog. **Open Project...** opens the system's file picker for a `.stproj` file, and the project then opens through `project.open` after the same question.

**Open Sample...** opens a copy of a finished game: one sample goes straight to its dialog, and several give a small menu. At the bottom the link **Continue without a project** only sets a flag in `EditorLayer`: the editor then shows an empty scene with its built-in meshes and materials, and saving needs a project.

**File ▸ Show Launcher** clears the flag again. Closing a project also leads back to the launcher. Dropping a `.stproj` file on the window opens its project, on the launcher too.

The main area has three sections. **Recent projects** shows one card per project, with the project's picture or, until it loads, a colored badge with its initials. The badge color comes from a :term[hash]{id=hash} of the name, so a project keeps its color. A card shows the name, the folder, and when you opened it, with the engine version when it differs from the running one.

The search field above the cards keeps the projects whose name or path contains every word you type. A click opens the project through `project.open`, after the question about changes not yet saved. The context menu offers Open, Show in Folder, Copy Path and Remove from List, which runs `editor.removeRecentProject`. Without any recent project, a quiet well explains where the cards will appear.

**Start something new** shows one card per template and one per sample. The basic3d template comes first. A template card opens New Project with that template chosen, and a sample card opens the Open Sample dialog. The cards share one grid with the recent projects, so that every section ends at the same right edge. Rows are balanced: five cards in a grid of four columns make rows of three and two, not four and one.

The agent card is the last block. Its job is to teach an AI agent's way in: the line `claude mcp add strata -- "<path to StrataCLI>" mcp` with a button that copies it, and a pill that shows the state of the editor's automation server. When `StrataCLI` is not next to the editor, a warning stands in place of the line. The pill has four forms, and the code picks the first that fits:

| State | Pill text | Cause |
| --- | --- | --- |
| Failed | Automation failed | Automation was asked for but could not start, for example a taken `--automation-port`; the tooltip gives the reason |
| Off | Automation is off | The editor started with `--no-automation` |
| Connected | One agent connected, or a count of agents | At least one agent holds a connection |
| Ready | Ready on port with the number | The server runs and nobody has connected yet |

The next quote shows the choice. Look at the order of the tests: the failed state comes before the off state, because both have `Running` false and only `Enabled` tells them apart.

```cpp src="StrataEditor/src/Panels/WelcomePanel.cpp#L783-L811"
std::string state;
std::string tooltip = "The editor's automation server: agents find it through its session file (StrataCLI)";
ImVec4 stateColor = colors.TextSecondary;
const char* stateIcon = Icons::Radio;
if (!automation.Running && automation.Enabled)
{
	// Asked for, but it could not start (a taken --automation-port, a session file that cannot be written).
	state = "Automation failed";
	tooltip = "Automation could not start, so agents cannot reach this editor: " + automation.Error;
	stateColor = colors.Error;
	stateIcon = Icons::CircleAlert;
}
else if (!automation.Running)
{
	state = "Automation is off";
	tooltip = "Started with --no-automation: agents cannot reach this editor";
	stateColor = colors.Warning;
	stateIcon = Icons::CircleAlert;
}
else if (automation.Clients > 0)
{
	state = fmt::format("{} {} connected", automation.Clients, automation.Clients == 1 ? "agent" : "agents");
	stateColor = colors.Success;
	stateIcon = Icons::PlugZap;
}
else
{
	state = fmt::format("Ready on port {}", automation.Port);
}
```

1. **Lines 787-794:** a server that was asked for but is not running has failed, and the pill carries the error text in its tooltip.
2. **Lines 795-801:** a server that was not asked for is off, and the tooltip names the flag.
3. **Lines 802-807:** a running server with clients shows how many agents are connected, with the singular for one.
4. **Lines 808-811:** a running server without clients shows its port, which is what an agent needs to find it.

The **footer** shows the engine name, version and commit, then the graphics processing unit (GPU) adapter with its graphics application programming interface (API) and version (or "no GPU"), and how long the start took. Its **About Strata** link opens the About dialog. Errors that the launcher gets, such as a project that cannot be opened, show in a red banner at the top of the main area with a button that dismisses it.

::figure{id=launcher-recent}

### New Project and Open Sample

Both dialogs share `ProjectDialogs`. New Project shows a card per template, with `basic3d` first and chosen, a **Name** field and a **Location** field with **Browse...**. A line under the fields says what the dialog will do, or why it cannot: `Creates` and the :term[full path]{id=absolute-path}, or a problem in the warning color. The checks run when the name or the location changes. They cover an empty or relative location, a location that is a file, an empty name, a name the project rules refuse, and a folder that exists and is not empty.

The suggested name is **My Project**; when the folder holds one already, the dialog counts up to **My Project 2** and so on, until 999.

Create runs `project.create` with the folder, the name, the template and `force`. Open Sample shows the sample's name and description, a **Folder** field and the same location field. Its button, **Copy and Open**, runs `project.openSample` with the sample, the folder and `force` through the runner, because the copy opens at once while its start scene loads over the next frames. The sample itself stays as it is.

The location is remembered in the editor's `imgui.ini`, in a section named `StrataLauncher` with a line `ProjectLocation=`, and the file keeps only absolute paths. The dialog stores a new location after a success, not after a press, so a failed attempt does not move it. Before anything is stored, the default is the folder `StrataProjects` in the home folder.

### About Strata

About is the one dialog that only shows facts. A table lists the version, the commit, the platform, the graphics processing unit (GPU), its driver, the graphics application programming interface (API), the time from start to the first frame and the interface scale. **Copy Details** puts the same rows on the clipboard as plain text, headed by the editor's name, which makes a bug report one paste.

The third-party notices come from `ThirdPartyNotices.md`, which the editor embeds when it is built. The dialog parses that Markdown once, on the first opening, and the `Markdown` drawer shows it in a scrolling box. Because the text is compiled in, About reads no file.

::figure{id=about-strata}

### Export Game

**File ▸ Export Game...** and the **Export** button at the top of the window open one dialog. Its fields follow the parameters of `project.export`. The first is the output folder, which starts as the project's folder name plus " Build", beside the project folder. The others are the window size, a fullscreen choice and three options: **Copy the runtime**, **Copy the script symbols** and `Leave out unused assets`.

The initial values come from the defaults of `GameExportOptions`, so the dialog and a command without arguments agree. The loading scene is a list of the project's scenes other than the start scene, and choosing one runs `project.setExportSettings`, because the choice belongs to the project. A summary line names the game's title, version, company and icon, with a link to the Game page of Project Settings.

While the fields show, the dialog checks the folder when it changes and when the dialog opens, never once per frame. Details of the export itself are in [worlds/export](../worlds/export.md); the pictures of the dialog before, during and after an export are on [the packs and export page](../assets/packs-export.md).

When an export ends well, the result line says how many assets and how large the pack is, how long it took, and where it went, and **Open Folder** shows the folder. When it fails, the line gives the error, and **Back** returns to the fields with the folder checked again.

### Recovering changes

`RecoveryDialog`, titled **Recover Unsaved Changes**, opens itself, once for each project that opens, after the recovery scan finds changes that still apply and that were not discarded on purpose before. When only earlier discards remain, a notification says that they can still be recovered.

Each entry shows the scene's name, its path (or "never saved"), the entity count, the age and why the changes were left. **Recover** replaces the edited scene, so it asks about the scene's own changes not yet saved first, over the dialog, and then runs `scene.recover` with the action `apply` and `force` set to true. **Discard** runs the same command with the action `discard`, and **Discard All** appears when more than one entry waits.

**Later** closes the dialog, and a notification then says where the changes are. The dialog closes by itself when nothing applies any more. Recover stays disabled while a scene is loading, since loading would replace what the person recovers.

### Delete asset

The Delete dialog opens from the Content Browser for an asset or a folder. It says that the file moves to the project's trash and that Edit ▸ Undo brings it back. When other assets or scenes use what the person deletes, it lists them in a scrolling box, and its button reads **Delete Anyway**. Pressing the button runs `asset.delete` or `asset.deleteFolder`, with `force` when something uses the asset. Why a plain delete is refused is the subject of [the trash and references](../editor/trash-references.md); this dialog is the place where the person sees the refusal's reason before they decide to delete anyway.

### New Script

**New Script** asks for a class name and has an **Empty class** option. It checks the name against the project when the name changes. **Create** runs `script.create` with the template `behaviour` or `empty` and `open` set to true, then runs `script.build` without waiting, so that the class is ready to attach when the build ends. The External Editor page of Preferences belongs to [the settings windows](settings-windows.md).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A separate launcher program | Unity Hub for Unity | Projects of several engine versions in one list; the editor starts only when needed | A second program to build, ship and update; no view of the running editor's state |
| System file and message dialogs | Many small tools | Native look, no code for the dialog | A blocked frame loop; no progress bar; no reaction to an export that an agent started |
| Dialogs that do the work themselves | Older editors | Fewer layers | Agents could not reach the same action; no journal; no single place that checks the scene |
| A start page inside the editor's binary | Godot's project manager, Unreal's project browser | One program; shared theme and widgets | The screen shares the process and the frame with everything else |
| A queue of dialogs, asked once at the start | Simple wizards | One question for a whole chain of actions | A scene that changes after the answer goes unnoticed |

Strata chose the last row's opposite: each action asks for itself and checks again when the answer may be stale.

## How it is tested

The launcher's tests are in `StrataTests/src/Editor/EditorLauncherTests.cpp`, suite `Editor.Launcher`. They draw the editor's interface without a window and press buttons through :term[item probes]{id=item-probe}. Cases cover these flows:

- The switch from the launcher to the dock space, and Continue without a project.
- Creating a project from a template card in a remembered location, and the question before New Project.
- The question that comes again over the dialog, and the sample copy.
- Recent-project cards and their removal, the read on an I/O thread with projects out of reach, and the search.
- An error that shows on the launcher, and a project file dropped on the window.
- The agent card's copied command and its failure text, and About.
- The shared grid, at 100 % and at 150 % of scale.

The export dialog has its own suite, `Editor.ExportDialog`, in `EditorExportDialogTests.cpp`: it covers progress and the folder button, the defaults, the loading scene, an export that a command started and a cancel, and the folder check.

Run a suite directly with the doctest filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Launcher
```

A new regression test for these screens must fail without the fix, as the engine's rules require. The usual route is to run the failing flow in a test, then revert the fix and watch the test fail.

## Changing it safely

Adding a dialog follows a short path. Write a class in `StrataEditor/src/UI/` with an `Open` function that sets a flag and a `Draw` function that opens its modal on the first frame and ends it with the editor's `EndModal`. Draw it from `EditorLayer::OnImGuiRender`, or from the panel that owns the choice, as the Content Browser does for Delete.

Add a `Show...` function to `EditorShell` only when a panel must open it. Run commands, never write files. If the dialog opens by command, extend `editor.showDialog`, whose enum lists the dialogs agents may open.

Four rules protect you. A dialog that can replace the scene calls `DrawDiscardQuestion` between its modal's begin and end, because a question asked from anywhere else opens over the whole window and closes the modal. Any file test that can be slow moves to a job, and the result returns by a poll, never by a callback from the worker. A new button that changes something needs a command, with a description written for agents. The theme and sizes in text heights come from the widget kit, so the screen follows the person's scale.

Before the commit, run `Editor.Launcher` and the suite of the dialog you touched, then the full editor tests for the label that suits your machine. A test of the same suite draws the launcher at 100 % and at 150 % of scale and checks it for :term[id]{id=id} conflicts, so a new control must keep its ids unique.

## Summary

- Every button that changes a project or scene runs a command: `project.create`, `project.openSample`, `project.open`, `editor.removeRecentProject`, `project.export`, `project.cancelExport`, `scene.recover`, `asset.delete` and `script.create`.
- A dialog stores the undo version when the person answers and asks again over itself when the version differs, so a change that came after the answer is never lost silently.
- The launcher reads the recent-project file, the existence of projects and their pictures on I/O jobs, one read at a time, and applies a result only when the list did not change meanwhile.
- Cancel Export stops an export whoever started it, while Hide only closes the dialog and the export continues.
- The agent card shows one of four states, checked in the order failed, off, connected and ready on a port, above the line that connects Claude Code.

## Check yourself

1. A launcher card opens a project. Which statement is right?

   - A. The card calls `Project::Load` directly, because the launcher has no project yet.
   - B. The card asks the shell about changes not yet saved and then runs `project.open` with `force`.
   - C. The card runs `project.open` without a question, because no scene is open on the launcher.

   :::answer{tests="command-per-button re-ask"}
   B. Every project action is a command, and `OpenRecentProject` runs `project.open` through the runner after `RequestDiscardChanges`. A is wrong because UI code never loads a project itself. C is wrong because a person who chose Continue without a project may hold a scene not yet saved, which the question protects.
   :::

2. Run the toy from this page, but let the person answer in frame 2 as well as press Create. What does frame 2 print?

   :::answer{tests="re-ask"}
   The call has `personAnswered` true, so the dialog stores version 13 as the answer. The versions match, so it prints that `project.create` succeeded, and the dialog closes. The answer in the same frame covers the change.
   :::

3. The launcher's job finishes with change count 7, and the recent-project list now has count 8. What does `PollRefresh` do with the result?

   - A. It applies the file anyway, since a newer read is always better.
   - B. It drops the result and resets the refresh time so the next frame reads again.
   - C. It blocks until the list reaches count 7 again.

   :::answer{tests="read-off-thread"}
   B. The read may be older than the change, so applying it could undo a project that the person opened a moment ago. A is wrong for that reason. C is wrong because nothing in the launcher waits.
   :::

4. An agent starts an export, and you open the Export dialog. You press Hide. What happens?

   :::answer{tests="export-hide"}
   The dialog shows the agent's progress from the shared export object, and Hide only closes the window. The export keeps running, and the **Export** button at the top of the window then has the tooltip "Show the running export". Cancel Export would stop it, and the dialog does that through `project.cancelExport` whoever started it.
   :::

5. You start the editor with `--no-automation`. The pill reads "Automation is off". You instead start two editors on one port with `--automation-port`. What does the second one show, and why not the same text?

   :::answer{tests="agent-states"}
   The second editor shows "Automation failed", with the reason in the tooltip. Both states have `Running` false, but in the second the automation was asked for, so `Enabled` is true. The code tests that case first.
   :::

## Exercises

1. **Basic.** Find which command each button of New Project and Open Sample runs. Search `StrataEditor/src/UI/ProjectDialogs.cpp` for the command names, and write down which of the two dialogs uses the runner and why.

   :::answer[Worked solution]{tests="command-per-button"}
   Search for `project.create` and `project.openSample`. The first stands in `ProjectDialogs::DrawNewProject`, where `RunNow` runs it and waits for the answer. The second stands in `ProjectDialogs::DrawOpenSample`, where `StartEditorCommand` hands it to the runner. The sample copy opens a project whose start scene loads over several frames, so the dialog must not wait for it, while a template project is written at once. The templates and samples lists come from `project.templates` and `project.samples`, run in `OpenNewProject` and `OpenSample`.
   :::

2. **Medium.** Write a function `MakeUniqueName` that takes the set of names already taken in a folder and a base name, and returns `My Project`, `My Project 2` and so on, the way the dialog does. Test it with a folder that holds three names, one of them a gap.

   :::answer[Worked solution]{tests="command-per-button" solution="sketches/editor-ui-launcher-dialogs-unique.cpp"}
   The loop counts from 1. The first candidate is the base alone, and later ones add the number after a space. The first candidate that no entry in the folder uses is the answer, so a gap such as `My Project 3` is filled before the count reaches 5.

   ```cpp sketch="editor-ui-launcher-dialogs-unique.cpp"
   // A free folder name, as the New Project dialog suggests it: "My Project", "My Project 2", and so on.
   #include <cstdio>
   #include <set>
   #include <string>

   std::string MakeUniqueName(const std::set<std::string>& taken, const std::string& base)
   {
   	for (int number = 1; number <= 999; number++)
   	{
   		const std::string name = number == 1 ? base : base + " " + std::to_string(number);
   		if (taken.count(name) == 0)
   			return name;
   	}
   	return base; // 999 names taken: give up and let the dialog show the problem
   }

   int main()
   {
   	const std::set<std::string> taken = { "My Project", "My Project 2", "My Project 4" };
   	std::printf("free in a folder with three: %s\n", MakeUniqueName(taken, "My Project").c_str());
   	std::printf("free in an empty folder: %s\n", MakeUniqueName({}, "My Project").c_str());
   	return 0;
   }
   ```

   ```text output-of="editor-ui-launcher-dialogs-unique.cpp"
   free in a folder with three: My Project 3
   free in an empty folder: My Project
   ```

   1. **Line 8:** the loop counts candidates from 1 up to the limit of 999 that the dialog uses.
   2. **Line 10:** the first candidate is the base alone, and later ones add the number after a space.
   3. **Line 14:** with every name taken, the function gives the base back, and the dialog then shows the problem.
   :::

3. **Medium.** Start the editor. From a terminal, send `editor.showDialog` with the dialog `about` through StrataCLI. Press **Copy Details**, paste the text into a file, and find which line names the :term[graphics API]{id=graphics-api}.

   :::answer[Worked solution]{tests="command-per-button"}
   The command opens About for the person at the window. The pasted text begins with "Strata Editor" and has one line per row of the table, such as `Version:`, `GPU:` and `Graphics API:`. The `Graphics API:` line holds the API name and its version. The text comes from `AboutDialog::FormatDetails`, which uses the same rows as the table, so what you read on screen is what you paste.
   :::

4. **Hard.** Open New Project, answer `Don't Save`, and leave the dialog open. From a terminal run `entity.create`, then press Create. Predict what happens before you run it, then run it.

   :::answer[Worked solution]{tests="re-ask"}
   The question about changes not yet saved shows again, over the dialog. The agent's entity moved the undo version past the one stored when the dialog opened, so `MayReplaceScene` asks again with `RequestReleaseProject`. Answer `Don't Save`, and the dialog runs `project.create`. The behavior is checked by the test "New Project asks again about changes made while it was open, over the dialog".
   :::

## Where it lives in Strata

- Panels and dialogs: `StrataEditor/src/Panels/WelcomePanel.cpp`, `StrataEditor/src/UI/ProjectDialogs.cpp`, `StrataEditor/src/UI/AboutDialog.cpp`, `StrataEditor/src/UI/ExportDialog.cpp`, `StrataEditor/src/UI/RecoveryDialog.cpp`, `StrataEditor/src/UI/DeleteAssetDialog.cpp` and `StrataEditor/src/UI/ScriptDialogs.cpp`.
- The shell: `StrataEditor/src/UI/EditorShell.h`, implemented by `EditorLayer` in `StrataEditor/src/EditorLayer.cpp`, which draws the launcher in `DrawLauncher` and the dialogs in `OnImGuiRender`.
- Commands: `project.templates`, `project.samples`, `project.create`, `project.open`, `project.openSample`, `project.export`, `project.cancelExport`, `project.setExportSettings`, `editor.removeRecentProject`, `scene.recover`, `asset.delete`, `asset.deleteFolder`, `script.create` and `editor.showDialog`.
- Settings: the `StrataLauncher` section of `imgui.ini`, and the command-line flags `--no-automation` and `--automation-port`.
- Tests: suites `Editor.Launcher` and `Editor.ExportDialog`, and `StrataTests/src/Editor/RecoveryTests.cpp`.

## Further reading

- Dear ImGui documentation on popups and modal windows: how the interface library opens and closes modal dialogs (intermediate).
- The Unity Hub and Godot project manager documentation: two other answers to the start screen problem (beginner).
- Jakob Nielsen's articles on error messages and confirmation dialogs: when a question helps a person and when it only interrupts (beginner).
