---
id: automation/sessions
title: "Sessions, discovery and launching"
description: "How a client finds the right editor, starts one and stays with it, and how an editor's automation starts, idles and stops in order."
kind: internals
size: L
tracks: [E]
needs: [automation/security]
time: 85
learn:
  - id: predict-editor
    text: predict which editor a client reaches when several editors run and the client restarts
  - id: launch-ready
    text: explain how a launch judges that an editor is ready, and why it uses progress and no fixed timeout
  - id: close-order
    text: name the order in which an editor closes its automation and why no client loses an answer
since: 0.3.0
status: final
---

An agent that drives the editor must first reach it. This page covers how a client finds the right editor among those that run, how it starts one when none runs, and how it stays with the editor it chose. It also covers the editor's side: how its :term[automation]{id=automation} starts, publishes itself, idles and stops. It does not cover what a session file holds or why you can trust it, which [Automation security](security.md) teaches, nor the protocol that runs after the connection exists.

## The problem and how engines solve it

An editor listens on a network port, and the number of that port is chosen when the editor starts: the :term[operating system]{id=operating-system} hands out a free one. Nobody can know it in advance. Three problems follow from that, and each one has more than one answer.

The first problem is finding. You may run one editor, or three at once, one for each project. A client that wants "the editor" must learn which port to use, and for which editor. Programs solve this in four usual ways.

- A fixed, well-known port. Every client knows the number, so no lookup is needed. The cost is a clash: a second editor cannot listen, because the port is taken, and another program may hold it already.
- A registry or discovery service, a third program that every server tells its address and every client asks. It scales, but it is one more program that can be down, and it must be installed and secured.
- A file in a known place. Each server writes its address into a file, and a client reads the files. There is nothing to install, and the files show what runs, but a file stays after a crash, so a client must check that the writer is still alive.
- :term[Environment variables]{id=environment-variable} handed to a child. A parent that starts the server tells its child the port through the environment. This is exact, but it works only for the parent and its children, never for a tool that starts later in another terminal.

Strata uses the third way and one piece of the fourth. Each editor writes a file, and the client reads the files; that is **discovery**, the way a client finds an editor: an explicit address, else the project it names, else the newest editor that runs. For a case where you know the address, such as a forwarded port, the client also accepts it directly from the :term[command line]{id=terminal-command} and the environment.

The second problem is staying. A client that connects, loses the connection and then connects again must not reach a different editor. Suppose an agent works on project `Cave` in one editor, which crashes while a second editor for project `Beach` still runs. A client that says "connect to whatever runs" would now send the agent's next commands, such as "delete this entity" or "save", to `Beach`, and nobody would notice. The agent would damage the wrong project with full confidence.

Other tools avoid this by never connecting again on their own: a database client that loses its server raises an error and stops. Strata chooses a middle path called **pinning**: after its first connection, a client stays with that editor, and after a restart it accepts only an editor of the same project.

The third problem is readiness. A started process is not a usable editor. Before a client can work, the editor must publish its session, then scan the project's assets, then open the start scene. For a large project this takes minutes.

A client that guesses a fixed wait fails twice: with a short wait it stops waiting for a healthy editor, and with a long wait it hangs for minutes after a crash. Strata judges readiness by **progress**: it asks the editor how far it is and fails only when nothing has changed for a long while.

The editor has a fourth concern, its own end. An editor that an agent started has no person who will close it. If the agent goes away, the editor would run for ever. Strata gives the editor an **idle timeout**, a time after which an editor with no client and no pending command closes itself. And when an editor closes, a client that waits for an answer must still get one.

:::why[Files, and not a service]
A discovery service would add a program that must run before any editor, and a fixed port would allow one editor per machine. A file in a private folder needs nothing the operating system lacks. The folder's permissions are the security, since only the same user can read the token. The cost is that a crashed editor leaves its file behind. So every reader must check that the process named in a file still runs, as the client code of this page does on each read.
:::

## The map

Two kinds of file exist, and [Automation security](security.md) shows what each one holds. This page shows who writes them, in which order, and who reads them.

```mermaid caption="The editor writes the project's pointer first and the per-user session second. The client reads both, applies the pin and connects. A launch starts the editor and polls it." alt="A flow chart with three groups. The editor writes a pointer file in the project and then a session file in the user's session folder. The client's discovery reads both files, the connection applies the pin and connects to the editor, and a launch starts the editor and asks it for its status."
flowchart LR
	subgraph Editor
		A["EditorAutomation: Start, UpdateSession, Stop"]
	end
	subgraph Disk
		P["project/.strata/EditorSession.json (pointer, no secret)"]
		S["Sessions/pid.json (port and token, owner only)"]
	end
	subgraph Client
		D["DiscoverEditorEndpoints"]
		C["EditorConnection with its pin"]
		L["LaunchEditor"]
	end
	A -->|"1 writes first"| P
	A -->|"2 writes second"| S
	D -->|reads| P
	D -->|reads| S
	D --> C
	C -->|"connect and authenticate"| A
	L -->|"starts, then polls editor.status"| A
```

The editor side lives in `StrataEditor/src/Editor/EditorAutomation.cpp` and the files' code in `Strata/src/Strata/Network/EditorSession.cpp`. The client side lives in `StrataCLI/src/CLI/`: `EditorConnection.cpp` holds discovery and the pin, and `EditorLauncher.cpp` holds the launch. The command-line client and its agent server, `StrataCLI mcp`, share this code. The editor's :term[main thread]{id=main-thread} runs everything of the editor's side.

A session file is named after the process: `Sessions/<process id>.json`. The folder is the per-user data folder of Strata, unless the environment variable `STRATA_SESSION_DIR` names another. The editor and the clients both honour that variable, and a client that starts an editor passes the variable on, because a child inherits its parent's environment. Tests rely on this to keep a private folder.

## The contract

Four rules hold for everything on this page. Each has a reason.

1. **A connection never silently switches editors.** Once connected through a session, a client talks to that process. After a restart it talks to an editor that has the same project open, and to no other. When neither exists, the call fails with a message that names the missing editor and says how to start it again. The reason is the damage of the wrong-project case above: a visible failure costs a second try, and a silent switch costs a project.
2. **Readiness is judged by progress, never by a fixed timeout.** A launch waits as long as the scan or the scene load keeps moving, and fails when nothing has changed for the stall time. The reason is that a project's size decides how long it takes, and no constant fits both a toy project and a game with a hundred thousand assets.
3. **An editor closes in a fixed order: pending commands are cancelled, then the session is removed, then the server stops.** The reason is that each step protects a different party. The cancelled commands still send their answers over connections that are still open. No new client finds an editor that is going away. The server stops last, after its :term[grace period]{id=graceful-stop}.
4. **Tests and agents never use a person's own session folder.** They set `STRATA_SESSION_DIR` to a private folder. The reason is that discovery picks the newest editor. A test that scans the real folder could connect to the editor you work in. A test that wrote there could hide your editor from your own tools.

:::rule[Tests never touch a real session folder]
A test that reads or writes the real session folder can reach your own editor, and a test of the client should not need a real editor at all. So the tests of this page write fake session files into a temporary folder and start small fake editors.
:::

## A toy version

Before the real code, a small program that does the job in its simplest form. The "files" are rows in a vector, and a flag stands for the check that the process still runs. `FindSessions` drops the dead rows and sorts the others newest first; `Discover` then keeps only the editors that have the named project open.

```cpp sketch="automation-sessions-toy.cpp"
// A toy discovery: the session files are rows in a vector, and "alive" stands for the check of the process.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Session
{
	uint32_t ProcessId = 0;
	uint16_t Port = 0;
	std::string StartedAt;
	std::string ProjectPath;
	bool Alive = false;
};

// Newest first: the timestamps have one fixed format, so comparing the text compares the times.
static std::vector<Session> FindSessions(std::vector<Session> files)
{
	std::erase_if(files, [](const Session& session) { return !session.Alive; });
	std::sort(files.begin(), files.end(), [](const Session& left, const Session& right)
	{
		if (left.StartedAt != right.StartedAt)
			return left.StartedAt > right.StartedAt;
		return left.ProcessId > right.ProcessId;
	});
	return files;
}

// With a project, only the editors that have it open; without one, every editor.
static std::vector<Session> Discover(const std::vector<Session>& files, const std::string& project)
{
	std::vector<Session> sessions = FindSessions(files);
	if (!project.empty())
		std::erase_if(sessions, [&](const Session& session) { return session.ProjectPath != project; });
	return sessions;
}

static void Print(const std::string& title, const std::vector<Session>& sessions)
{
	std::cout << title << ":";
	for (const Session& session : sessions)
		std::cout << " " << session.Port;
	std::cout << "\n";
}

int main()
{
	const std::vector<Session> files = {
		{ 40101, 51001, "2026-01-01T00:00:00Z", "Cave", true },
		{ 40102, 51002, "2026-02-01T00:00:00Z", "Beach", true },
		{ 40103, 51003, "2026-03-01T00:00:00Z", "", true },
		{ 40104, 51004, "2025-12-01T00:00:00Z", "Cave", true },
		{ 40105, 51005, "2026-04-01T00:00:00Z", "Beach", false } };

	Print("every editor", Discover(files, ""));
	Print("project Cave", Discover(files, "Cave"));
	Print("project Beach", Discover(files, "Beach"));
	return 0;
}
```

```text output-of="automation-sessions-toy.cpp"
every editor: 51003 51002 51001 51004
project Cave: 51001 51004
project Beach: 51002
```

1. **Line 20:** a dead row is dropped, as the real function deletes the file of an exited editor.
2. **Lines 23–25:** newest first, and the larger process id first on equal times.
3. **Lines 34–35:** a project keeps only the editors that have it open.

The three lines show the idea. Without a project, the editor with the latest start time comes first. With the project `Cave` only the two editors that have it open remain, again newest first. The dead editor, process `40105`, never appears.

The toy omits what the real code adds: the pointer file, the address check, the check of the process by its start time, the explicit endpoint, and the pin. The next sections add them one by one.

## Session files and discovery in the real code

### Writing: the pointer first

When the editor's automation starts, it writes the project's pointer and then the session. The order has a reason that a comment in the code states: a client that finds the session, for instance a launch that waits for it, must then find the pointer too.

A missing pointer is not an error, since a read-only project folder cannot hold one, and clients also match the session's project path. A session that cannot be written is an error, and the pointer that was written a moment before is removed again.

```cpp src="Strata/src/Strata/Network/EditorSession.cpp#L200-L216" from="if (!info.ProjectPath.empty())" to="RemoveProjectPointer(info);" symbol="EditorSession::WriteSessionFiles"
if (!info.ProjectPath.empty())
{
	const std::filesystem::path pointerFile = GetProjectSessionFilePath(FileSystem::FromUTF8(info.ProjectPath));
	const std::string pointer = MakeProjectPointer(info).dump(1, '\t', false, nlohmann::json::error_handler_t::replace) + "\n";
	if (!Platform::WritePrivateFile(pointerFile, pointer, &problem))
		ST_CORE_WARN("EditorSession: the project's session pointer cannot be written: {}", problem);
}

const std::filesystem::path sessionFile = GetSessionFilePath(*sessionDirectory, info.ProcessId);
const std::string session = info.ToJson().dump(1, '\t', false, nlohmann::json::error_handler_t::replace) + "\n";
if (!Platform::WritePrivateFile(sessionFile, session, &problem))
{
	ST_CORE_ERROR("EditorSession: {}", problem);
	if (error)
		*error = problem;
	// No pointer to a session that does not exist.
	RemoveProjectPointer(info);
```

1. **Lines 200–206:** the pointer comes first, and a failure to write it only warns.
2. **Lines 208–216:** a failure to write the session is an error, and it takes the pointer back.

The pointer holds five fields: the process id, the project, the editor's version, the headless flag and the start time as text. It never holds the port or the token. A client that reads a pointer therefore learns which process to look at, and nothing it could use to connect. To get the port and the token it must open the per-user session of that process, which only the same user can read.

### Reading: discovery

`DiscoverEditorEndpoints` returns a list of candidate endpoints, best first. The client tries them in order. There are three cases, from the most specific to the least.

```cpp src="StrataCLI/src/CLI/EditorConnection.cpp#L47-L86" symbol="DiscoverEditorEndpoints"
std::vector<EditorEndpoint> DiscoverEditorEndpoints(const EditorConnectionOptions& options, std::string* error)
{
	std::vector<EditorEndpoint> endpoints;
	if (options.Port)
	{
		EditorEndpoint& endpoint = endpoints.emplace_back();
		endpoint.Host = options.Host;
		endpoint.Port = *options.Port;
		endpoint.Token = options.Token;
		endpoint.Source = "explicit";
		return endpoints;
	}

	std::filesystem::path sessionDirectory = options.SessionDirectory;
	if (sessionDirectory.empty())
	{
		std::optional<std::filesystem::path> defaultDirectory = EditorSession::GetSessionDirectory(error);
		if (!defaultDirectory)
			return endpoints;
		sessionDirectory = std::move(*defaultDirectory);
	}

	const std::vector<EditorSessionInfo> sessions = EditorSession::FindSessions(sessionDirectory);
	if (!options.ProjectDirectory.empty())
	{
		if (std::optional<EditorSessionInfo> projectSession = EditorSession::ReadProjectSession(options.ProjectDirectory, sessionDirectory))
			AddSessionEndpoint(endpoints, *projectSession, "project");

		for (const EditorSessionInfo& session : sessions)
		{
			if (EditorSession::IsSameProject(session.ProjectPath, options.ProjectDirectory) && !IsDuplicate(endpoints, session))
				AddSessionEndpoint(endpoints, session, "session");
		}
		return endpoints;
	}

	for (const EditorSessionInfo& session : sessions)
		AddSessionEndpoint(endpoints, session, "session");
	return endpoints;
}
```

1. **Lines 50–58:** an explicit port returns at once, with no file read.
2. **Lines 72–73:** with a project, the pointer's session comes first.
3. **Lines 75–80:** then the other sessions that name the project, without a duplicate, and nothing else.
4. **Lines 83–85:** without a project, every session, in the order of `FindSessions`.

The sessions come from `FindSessions`. That function reads each `.json` file of the folder and ignores a file whose name does not match the process id inside.

Discovery checks each process by its start time, as the security page taught. A process that runs with the recorded start time is alive. One that is gone, or has another start time, is stale, and its file is deleted. One whose start time cannot be read is skipped and kept, because it may be a live editor.

Then the function sorts by the start timestamp, newest first, and by process id when two timestamps are equal. The timestamps have a fixed format, so comparing them as text compares them as times.

The test `Endpoints are discovered in precedence order` of the suite `CLI.Discovery` shows the three cases with four sessions. Their ports are 40101 to 40104; the project `P` is open in 40101 and 40104, 40102 has another project, and the project's pointer names 40104, whose start time is the oldest.

| Call | Candidates, first to last |
| --- | --- |
| No project, no port | 40103, 40102, 40101, 40104 (newest first) |
| Project `P` | 40104 (from the pointer), then 40101 (a session that names `P`) |
| An explicit port | only that port; no file is read |

An explicit endpoint turns discovery off. `--port` or the variable `STRATA_EDITOR_PORT` names the port, and the token comes from `STRATA_EDITOR_TOKEN` or `--token`. The option `--host` is accepted only together with a port.

The client does not check that this host is a :term[loopback]{id=loopback} address, and the test uses `10.1.2.3`. Only a session that discovery finds must name a loopback address; a session on another address is ignored with a warning. That difference is deliberate: a session file is data that someone else could have written, while an explicit endpoint is your own choice. The editor still checks the token when the client connects, so you can reach an editor through a forwarded port, and a wrong host fails that check.

`IsSameProject` decides whether two paths name one project. It asks the file system whether the paths are `equivalent`, which sees through links and different spellings, and falls back to comparing :term[normalized]{id=normalization} text when a folder no longer exists.

### Staying: the pin

When a connection succeeds through a session, the client remembers three things about that editor: its process id, its start time and the project it had open. That is the pin. On every later attempt to connect, `EditorConnection::EnsureConnected` builds the candidate list, adds the pinned process's own session file, and drops every candidate that the pin refuses.

```cpp src="StrataCLI/src/CLI/EditorConnection.cpp#L271-L283" symbol="EditorConnection::IsPinnedEditor"
bool EditorConnection::IsPinnedEditor(const EditorEndpoint& endpoint) const
{
	// Explicit endpoints are fixed by configuration and need no pinning.
	if (!m_Pinned || !endpoint.Session)
		return true;
	// The same editor process, whatever project it has open now. Discovery only returns sessions whose process runs
	// with the recorded start time, so a matching start time rules out a process that reused the id.
	if (endpoint.Session->ProcessId == m_Pinned->ProcessId && endpoint.Session->ProcessStartTime == m_Pinned->ProcessStartTime)
		return true;
	if (!m_Pinned->ProjectPath.empty())
		return EditorSession::IsSameProject(endpoint.Session->ProjectPath, FileSystem::FromUTF8(m_Pinned->ProjectPath));
	return false;
}
```

1. **Lines 274–275:** an explicit endpoint, or a client with no pin, passes.
2. **Lines 278–279:** the same process and start time passes, whatever project it has open.
3. **Lines 280–282:** otherwise only an editor with the pinned project passes.

An editor passes if it is the same process, whatever project it has open now, or if it has the same project as the pinned editor had. The start time guards the first test: a new process that received the same process id has another start time. The second test is what lets the client follow a restart. An explicit endpoint passes always, since a configuration fixed it and no session is involved.

Why add the pinned process's own file? Because discovery by project would miss an editor that opened another project after the pin was made; its session now names the new project. Adding its file as the first candidate keeps the client with it. Only an explicit choice, `ConnectToSession`, forgets the pin and pins the new editor.

```mermaid caption="A client has no pin until its first connection through a session. After that, the same process is always accepted, and a new process only when it has the pinned project. When the pinned editor is gone, other editors are refused until one of the pinned project returns." alt="A state diagram. The client has no pin until it connects through a session, which pins it. A pinned client stays pinned when the same process or a new process with the same project is accepted. When the editor is gone, the client is disconnected and stays so while other editors are refused. A new editor of the pinned project returns it to the pinned state."
stateDiagram-v2
	[*] --> Unpinned
	Unpinned --> Pinned : first connection through a session
	Pinned --> Pinned : same process, any project
	Pinned --> Pinned : new process with the pinned project
	Pinned --> Disconnected : the editor is gone
	Disconnected --> Disconnected : any other editor is refused
	Disconnected --> Pinned : an editor of the pinned project returns
```

:::example[Two editors, one client, one restart]
Take two editors. Editor A has project `Cave` open and listens on port 51001, and it started on 1 January. Editor B has `Beach` open on port 51002, and it started on 1 February.

1. The client runs `StrataCLI call rpc.ping` with no project. Discovery lists both sessions newest first: B, then A. The client connects to B and pins process B with project `Beach`.
2. A second client runs the same call with `--project Cave`. A new client has no pin, so discovery returns the pointer's session first, which is A. This client connects to A.
3. Now B crashes. The first client's next call finds the connection closed. Discovery lists A, which is alive, but the pin refuses it: its process differs and its project `Cave` is not `Beach`. The call fails with the message that the editor for `Beach` is not running and that other editors are not used automatically.
4. You start a new editor for `Beach`. It has a new process id and a later start time. The next call lists it, the pin accepts it by its project, and the client now pins the new process.

At no step did the client send a command to A by accident. The cost is step 3: a person or an agent must act before work continues.
:::

## Launching

An agent that finds no editor must start one. `LaunchEditor` does this, and `StrataCLI launch` and the agent server both use it. It first checks what it can check before it starts anything: the editor program is a regular file, the project folder exists, and a usable session folder exists. Without a usable folder nobody could find the editor later, so nothing starts.

The editor program is found in a fixed order: the option `--editor`, else the environment variable `STRATA_EDITOR_PATH`, else the program next to `StrataCLI`. `ResolveEditorPath` makes the path absolute. The reason is in its comment. A relative path would be checked against the :term[current folder]{id=current-folder}. A bare name is searched on `PATH` when the process starts, so the checked path and the started path could differ.

`GetEditorArguments` builds the editor's command line from the launch's specification. Watch the flags: each one is added only when the caller asked for it.

```cpp src="StrataCLI/src/CLI/EditorLauncher.cpp#L60-L88" from="if (!specification.ProjectDirectory.empty())" to="return arguments;" symbol="GetEditorArguments"
if (!specification.ProjectDirectory.empty())
{
	std::error_code error;
	std::filesystem::path projectDirectory = std::filesystem::absolute(specification.ProjectDirectory, error);
	if (error)
		projectDirectory = specification.ProjectDirectory;
	arguments = { "--project", FileSystem::ToUTF8(projectDirectory.lexically_normal()) };
}
if (specification.Headless)
	arguments.push_back("--headless");
if (specification.NoGpu)
	arguments.push_back("--no-gpu");
if (!specification.WindowSize.empty())
{
	arguments.push_back("--window-size");
	arguments.push_back(specification.WindowSize);
}
if (specification.UIScale)
{
	// The shortest form that reads back as the same float (1, 1.5), as the editor parses it.
	arguments.push_back("--ui-scale");
	arguments.push_back(fmt::format("{}", *specification.UIScale));
}
if (specification.IdleTimeout)
{
	arguments.push_back("--idle-timeout");
	arguments.push_back(std::to_string(specification.IdleTimeout->count()));
}
return arguments;
```

1. **Lines 62–66:** the project path is made absolute and normalized before it becomes an argument.
2. **Lines 68–87:** each flag is added only when asked.
3. **Lines 72–76:** a window size passes through in the form the editor reads.

The arguments are `--project` with an :term[absolute path]{id=absolute-path}, and on request `--headless`, `--no-gpu`, `--window-size`, `--ui-scale` and `--idle-timeout`.

A headless run has no window but keeps the graphics device, as [First frame](../core/first-frame.md) teaches. **No-gpu** is a run without a graphics device, which implies headless. It serves work such as exporting a game or processing assets on a machine that has no :term[graphics card]{id=gpu}.

`--window-size` asks for the opposite: a window of exactly `<width>x<height>` pixels, such as `1600x900`, instead of a window that fills the screen. Together with `--ui-scale`, it makes pictures of the editor compare across machines. The size must be at least `640x360`, and it cannot be combined with `--headless` or `--no-gpu`, which open no window. `StrataCLI launch` checks the value before it starts anything, because the launched editor's output is discarded and its own refusal would go unseen. The size counts only when the window opens.

Then comes the wait, in two stages. `LaunchEditor` starts the editor detached, with its output discarded, so it keeps running after the launching command ends.

```cpp src="StrataCLI/src/CLI/EditorLauncher.cpp#L116-L161" from="ProcessSpecification processSpecification;" to="result.Session = std::move(*session);" symbol="LaunchEditor"
ProcessSpecification processSpecification;
processSpecification.Executable = specification.EditorPath;
processSpecification.Arguments = GetEditorArguments(specification);
processSpecification.Output = ProcessOutputMode::Discard;
processSpecification.Detached = true;

result.EditorProcess = CreateScope<Process>();
if (!result.EditorProcess->Start(processSpecification))
{
	result.Error = result.EditorProcess->GetLastError();
	result.EditorProcess.reset();
	return result;
}

const uint32_t processId = result.EditorProcess->GetProcessID();
ST_INFO("Started the editor (process {}), waiting for its session", processId);

Process& process = *result.EditorProcess;
std::optional<EditorSessionInfo> session = WaitForEditorSession(processId, sessionDirectory, specification.WaitTimeout,
	[&process]() { return process.IsRunning(); }, &result.Error);
if (!session)
{
	// Nobody could reach it (and it may never quit by itself): stop it rather than leave it running unseen. One that
	// ended by itself could not start: its exit code, and its log, say why (its output went to the null device).
	if (process.IsRunning())
	{
		if (process.Terminate())
			result.Error += "; the editor was stopped";
	}
	else if (const std::optional<int> exitCode = process.GetExitCode())
	{
		result.Error += fmt::format(" (exit code {}: the editor's log, Logs/StrataEditor.log in the user's Strata data folder, says why)", *exitCode);
	}
	return result;
}

if (specification.WaitForProject && !specification.ProjectDirectory.empty()
	&& !WaitForEditorProject(*session, specification.StallTimeout, specification.OnProgress, [&process]() { return process.IsRunning(); }, &result.Error))
{
	if (process.IsRunning() && process.Terminate())
		result.Error += "; the editor was stopped";
	return result;
}

result.Success = true;
result.Session = std::move(*session);
```

1. **Lines 116–120:** the arguments go to a detached process whose output is discarded.
2. **Lines 134–135:** the wait gets a :term[callback]{id=callback} that tells whether the child still runs.
3. **Lines 136–150:** when no session appears, the launch stops the editor it started, or reports the :term[exit code]{id=exit-code} of one that ended by itself.
4. **Lines 152–158:** the second stage runs only for a project and only when asked, with the same stop on failure.
5. **Lines 160–161:** on success the caller gets the session.

Stage one waits for the session. `WaitForEditorSession` reads the session file of the child's process id every 50 ms, and when it exists it tries to connect and prove its token, within one second. It stops early if the child process has exited, which turns a crash at startup into an error message at once; that message names the exit code and points to the editor's log. Its own limit, `--wait-timeout`, given in milliseconds, is 60,000 ms by default, and it bounds only this first stage.

Stage two waits for the project, and only when the launch has a project. A fixed timeout would be wrong here, as the next section shows. If either stage fails, the launch terminates the editor it started. The code's comment gives the reason: nobody could reach that editor, and it might never quit by itself.

### Ready means progress

`WaitForEditorProject` connects with the session it was given and asks `editor.status` every 250 ms, requesting the section `sceneLoad`. The compact answer of `editor.status` leaves the start scene's load out, so the section must be asked for by name.

```cpp src="StrataCLI/src/CLI/EditorLauncher.cpp#L178-L192" overload="2" from="std::optional<EditorStartupProgress> last;" to="continue;" symbol="WaitForEditorProject"
std::optional<EditorStartupProgress> last;
auto lastChange = std::chrono::steady_clock::now();
// The compact editor.status leaves the start scene's load out: ask for it. An editor from before the sections
// refuses the parameter, and reports the load without it.
nlohmann::json statusParameters = { { "sections", nlohmann::json::array({ "sceneLoad" }) } };
while (true)
{
	const RpcResult status = client.Call("editor.status", statusParameters, c_StatusTimeout);
	// An editor without the status (an older one) has nothing to wait for.
	if (status.IsError() && status.GetError().Code == static_cast<int>(JsonRpc::ErrorCode::MethodNotFound))
		return true;
	if (status.IsError() && status.GetError().Code == static_cast<int>(JsonRpc::ErrorCode::InvalidParams) && !statusParameters.empty())
	{
		statusParameters = nlohmann::json::object();
		continue;
```

1. **Line 178:** the last progress value, kept to see whether anything changed.
2. **Lines 187–188:** an editor without `editor.status` counts as ready.
3. **Lines 189–192:** an editor that refuses the sections is asked again without them.

The first calls handle editors of other ages. An editor that does not know `editor.status` has nothing to wait for, so the client treats it as ready. An editor that refuses the `sections` parameter is asked again without it, and its plain answer reports the load. A failed call is not yet a failure: the client checks that the process still runs and that it can connect again.

```cpp src="StrataCLI/src/CLI/EditorLauncher.cpp#L203-L245" overload="2" from="const nlohmann::json& value = status.GetValue();" to="std::this_thread::sleep_for(c_ProjectPollInterval);" symbol="WaitForEditorProject"
	const nlohmann::json& value = status.GetValue();
	const nlohmann::json* assets = value.is_object() ? JsonUtils::Find(value, "assets") : nullptr;
	const nlohmann::json* scanning = assets && assets->is_object() ? JsonUtils::Find(*assets, "scanning") : nullptr;
	const nlohmann::json* sceneLoad = value.is_object() ? JsonUtils::Find(value, "sceneLoad") : nullptr;
	EditorStartupProgress progress;
	if (scanning && scanning->is_object())
	{
		progress.Phase = JsonUtils::GetString(*scanning, "phase");
		progress.Done = JsonUtils::GetUInt(*scanning, "done", 0);
		progress.Total = JsonUtils::GetUInt(*scanning, "total", 0);
		progress.Message = progress.Total > 0
			? fmt::format("Scanning the project's assets: {} / {}", StringUtils::FormatThousands(progress.Done), StringUtils::FormatThousands(progress.Total))
			: fmt::format("Scanning the project's assets: {} files found", StringUtils::FormatThousands(progress.Done));
	}
	else if (sceneLoad && sceneLoad->is_object())
	{
		progress.Phase = "OpeningScene";
		progress.Done = static_cast<uint64_t>(std::clamp(static_cast<double>(JsonUtils::GetFloat(*sceneLoad, "progress", 0.0f)), 0.0, 1.0) * 100.0);
		progress.Total = 100;
		progress.Message = fmt::format("Opening the start scene: {}%", progress.Done);
	}
	else
	{
		return true;
	}
	const bool changed = !last || last->Phase != progress.Phase || last->Done != progress.Done || last->Total != progress.Total;
	if (changed)
	{
		lastChange = std::chrono::steady_clock::now();
		if (onProgress)
			onProgress(progress);
		last = std::move(progress);
	}
}
if (std::chrono::steady_clock::now() - lastChange >= stallTimeout)
{
	const std::string where = last ? last->Message : std::string("the editor's status");
	return fail(fmt::format("The editor's project stopped progressing: no change for {} s ({})",
		std::chrono::duration_cast<std::chrono::seconds>(stallTimeout).count(), where));
}
if (isProcessAlive && !isProcessAlive())
	return fail("The editor exited while its project was opening");
std::this_thread::sleep_for(c_ProjectPollInterval);
```

1. **Lines 224–227:** neither a scan nor a load is running, so the editor is ready.
2. **Lines 228–235:** a changed value resets the stall timer and goes to the caller.
3. **Lines 237–242:** no change for the stall time fails the launch and names where it stopped.
4. **Line 245:** the poll interval, 250 ms.

An answer is turned into one progress value. If the :term[asset scan]{id=asset-scan} is running, the value is its phase, with the files done and the total, or only the files found while the total is still unknown. Otherwise, if the start scene is loading, it is the load's fraction as a percentage of 100. If neither is running, the editor is ready and the function returns true.

Whenever the value differs from the last one, the stall timer restarts and the progress message goes to the caller. When the time since the last change reaches the stall time, 60 seconds by default, the launch fails and names where it stopped.

A scan of 70,000 files that takes four minutes never fails, because the count changes every few hundred milliseconds. The same scan that freezes at 41,000 files fails 60 seconds after its last change, and the error says "Scanning the project's assets: 41,000 / 70,000". The command prints the messages on its error stream, such as "Scanning the project's assets: 7,000 / 70,000" and "Opening the start scene: 40%", while the session's description goes to the output.

```mermaid caption="A launch over time. The session appears first. Then the client asks for the status every 250 ms. Each change of the scan or the load restarts the stall timer, and the launch is ready when neither runs." alt="A sequence chart with a launch and an editor. The launch starts the editor, which writes its pointer and then its session. The launch reads the session and proves its token. In a loop the launch asks for the status and the editor answers with scan or load progress, and any change resets the stall timer. When no scan and no load remain, the launch is ready."
sequenceDiagram
	participant L as launch
	participant E as editor
	L->>E: start the process with the project and flags
	E->>E: write the pointer, then the session
	L->>E: read the session file, connect, authenticate
	loop every 250 ms
		L->>E: status with the scene load section
		E-->>L: scan phase and files, or scene load fraction
		Note over L: a change resets the stall timer
	end
	E-->>L: no scan and no load, so ready
```

:::why[Progress and not a longer timeout]
A timeout of ten minutes would cover most projects, and would still fail for a bigger one, while a crash would take ten minutes to report. Asking for progress turns the question from "how long does this take" into "is it still working", which has an answer for every project size. The cost is that the editor must report its progress honestly: a phase that does not count would look like a stall. The scan and the scene load were built to report, and the tests below fake both.
:::

## The editor's side

### Start, follow and stop

`EditorAutomation::Start` runs in a fixed order, and each step has a reason. It generates a token. It registers the editor's methods before it listens, so the first client that lists the methods sees all of them. It starts the server on the port that `--automation-port` names, where 0, the default, asks the operating system for a free one.

Last, it publishes the session. If that fails the whole start fails, because an editor that nobody could find is worse than a clear error. On any failure `Start` undoes what it did.

The session follows the project. `UpdateSession` compares the project that the editor has open with the session's project path, and when they differ, it writes the new session and then removes the old pointer. It runs every frame, and also in the completion of each command, before the answer goes out. A client that sends `project.create` and then calls again with `--project` immediately finds the editor, because no frame runs between the command and the answer. The test `The session is published, follows the project and is removed` checks exactly this.

```cpp src="StrataEditor/src/Editor/EditorAutomation.cpp#L125-L141" symbol="EditorAutomation::Stop"
void EditorAutomation::Stop()
{
	if (!m_Server.IsRunning())
		return;

	m_State->RefreshSession = nullptr;
	m_Context.SetStatusProvider(c_StatusSection, nullptr);
	// No new client should find an editor that is going away.
	if (m_Session)
	{
		EditorSession::RemoveSessionFiles(*m_Session);
		m_Session.reset();
	}
	m_Server.Stop(m_Specification.ShutdownGracePeriod);
	UnregisterMethods();
	ST_INFO("Automation: stopped ({} requests answered)", m_State->CompletedRequests);
}
```

1. **Lines 130–131:** the automation stops answering status and refreshing the session.
2. **Lines 133–137:** the session files go first.
3. **Line 138:** the server stops last, with its grace period.

`Stop` mirrors `Start`. It first removes the session files, so no new client finds an editor that is going away. Only then does it stop the server, with a grace period of 2 seconds by default, as the page on [the automation server](rpc-server.md) explains. The removal takes the pointer too, but only while it is still this editor's own pointer, because another editor may have written a newer one in the meantime.

### The idle timeout

The idle timeout is the time after which an editor that has no connected client and no pending command closes itself. The option `--idle-timeout` gives it in seconds, and 0 means never. Each update, the editor's automation records the last moment when a client was connected or a request was pending. `HasIdledOut` is true when the time since then reaches the timeout.

The editor's layer then logs a warning and closes the editor. If the scene has changes that are not saved, the warning says they are discarded, and adds that they stay as recovery data when recovery is active. The option accepts at most a week.

Two defaults differ, on purpose. The editor itself has no idle timeout by default, since a person may leave it open. The agent server passes 600 seconds to the editors that it starts, and `StrataCLI launch` passes a timeout only when you give one. An editor that an agent started and then forgot is the case the timeout exists for. A 600 second timeout means that after the last client has gone, the editor stays ten minutes, so an agent that restarts its client in that time finds it again.

### Closing in order

An editor closes in `EditorLayer::OnDetach`, and the order is the third rule of the contract.

```cpp src="StrataEditor/src/EditorLayer.cpp#L881-L890" from="m_CommandRunner.CancelAll(" to="m_Automation.Stop();" symbol="EditorLayer::OnDetach"
m_CommandRunner.CancelAll("The editor is closing");
m_ScreenshotsToRead.clear();
if (m_UIDrawn)
{
	EditorPanelContext panelContext = MakePanelContext();
	m_Panels.OnDetach(panelContext);
}
m_Panels.RemoveSettingsHandler();
m_ProjectDialogs.RemoveSettingsHandler();
m_Automation.Stop();
```

1. **Line 881:** the running commands are cancelled before anything else closes.
2. **Line 882:** the screenshots that pending `editor.screenshot` commands wait for are dropped.
3. **Line 890:** the automation server stops last, after every cancelled command has answered.

`CancelAll` comes first, while the project is still open, because the completions of the cancelled commands may still read the editor's state. [Deferred commands](../editor/deferred-commands.md) teach that a cancelled command completes with a Cancelled result. Those completions send their answers over connections that are still open, and so a client that waited for a long command learns that it was cancelled, and does not only see a dropped connection. Only then does `Stop` run. If the order were reversed, the server would stop first and the answers of the cancelled commands would have nowhere to go.

Ctrl+C in a terminal and the signal `SIGTERM` take the same road. The :term[entry point]{id=entry-point-gpu} of each program installs an interrupt handler, `Platform::InstallInterruptHandler`, which only records the request. The :term[main loop]{id=game-loop} sees it, logs a warning and closes the application with the :term[exit code]{id=exit-code} 130, which runs `OnDetach` like any other close. [Platform](../core/platform.md) teaches the handlers. A headless editor whose automation cannot start and that runs without `--frames` exits with code 1, since nothing could ever reach or close it.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A fixed well-known port | Many databases and language servers | No files, and clients that need no lookup | One editor per machine, and a clash with any other program on that port |
| A discovery service | Service meshes and some build farms | Discovery across machines and health checks | A program to run and to secure, which a local tool does not need |
| Environment variables only | Test harnesses that start their own child | No files to clean up | No way to reach an editor that a person started, or one started by another tool |
| Connect again to whatever runs | Simple clients | No error after a restart | The wrong-project case: commands reach another editor without a sign |
| A fixed readiness timeout | Many scripts that wait for a server | One number, and no status call | Failures on large projects, and long hangs on crashes |

## How it is tested

The suite `CLI.Discovery` in `StrataTests/src/CLI/EditorDiscoveryTests.cpp` has a case for each of these, and none needs a real editor. The cases write fake session files for live helper processes into a temporary folder. They start small fake editors in the test process.

The cases cover the order of endpoints, sessions on IPv6, a restarted editor that is found again, the editor path, and the checks before a launch. They also cover the pin: staying with the editor after a crash, following a project switch, and refusing other editors.

The launch cases start the test program itself as a fake editor: the variable `STRATA_TEST_FAKE_EDITOR` makes it serve `editor.status` instead of running tests.

One makes the fake scan last 7,000 ms, longer than the 5,000 ms session wait the test sets, and checks that the launch succeeds. One checks the start scene's load, which is reported only in the `sceneLoad` section. One checks an editor that refuses the sections. One makes progress stop and checks that the launch fails with the stall and terminates the editor, while a launch without waiting returns at the session.

The suite `Editor.Automation` checks the editor's side: the case `The session is published, follows the project and is removed` and the case `The idle timeout runs while no client is connected and nothing is pending`, which checks that a connected client or a pending request keeps the editor alive. To run both suites, give the test program a filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=CLI.Discovery
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Automation
```

The launch cases set `STRATA_SESSION_DIR` to a temporary folder through `Tests::ScopedEnvironmentVariable`, so the editors they start publish there and never in your own session folder.

## Changing it safely

A change here touches the way every agent reaches every editor, so a few rules apply.

- Keep the write order: pointer first, then session. A launch relies on it.
- Never write a port or a token into the pointer. The project folder may be shared, and the pointer is untrusted by design.
- Never widen the pin. A new rule that accepts more editors than the same process or the same project reopens the wrong-project case. Add the case to `Reconnects stay with the pinned editor` first.
- Keep readiness on progress. A new startup phase must report through `editor.status`, or the launch will see a stall while the phase runs. Extend the fake editors of the tests.
- Keep the closing order. Any new service of the editor that answers clients stops after `CancelAll` and, if it holds the session, before the server stops.
- A new editor option goes into the editor's `c_Arguments` list, which also feeds its usage text.

Run the suites `CLI.Discovery` and `Editor.Automation`, and the end-to-end suites that start the built programs, before a commit.

## Summary

- A client finds an editor by discovery: an explicit port, else the project's pointer and the sessions that name the project, else every live session newest first. It pins the first editor it reaches and, after a restart, accepts only an editor of the same project.
- A launch starts the editor, waits for its session, and then judges readiness by progress: any change of the scan or the load resets the stall timer.
- An editor writes the pointer first, follows its project, idles out when unused, and closes by cancelling commands, removing the session and stopping the server.

## Check yourself

1. Four sessions exist, with start times of January, February, March and December of the year before, and no client names a project. In which order does discovery list them, and what decides a tie?

   :::answer{tests="predict-editor"}
   The newest start time first: March, February, January, then December. When two start times are equal, the larger process id comes first. The timestamps have a fixed format, so their text order is their time order.
   :::

2. A client is pinned to an editor for project `Cave`. The editor opens project `Beach`, and the connection drops. Another editor for `Cave` also runs. Which editor does the next call reach: (a) the other `Cave` editor, which discovery by project finds, (b) the first editor, which the pin names, or (c) none, because the project changed?

   :::answer{tests="predict-editor"}
   Option (b). The pin accepts the same process whatever project it has open, and the client adds that process's own session file as the first candidate. Option (a) is wrong because the pinned process is tried first, and the pin would accept the other `Cave` editor only if the pinned one were gone. Option (c) is wrong for the same reason.
   :::

3. A launch of a big project has run for six minutes. Its scan reports 20,000 of 90,000 files, then 21,000. Should the launch fail? What would make it fail?

   :::answer{tests="launch-ready"}
   No. The count changed, so the stall timer restarted, and the launch fails only after 60 seconds, by default, with no change at all. Six minutes of steady progress is a healthy launch, and a fixed timeout of five minutes would have failed it.
   :::

4. The editor's code stops the server and then cancels the pending commands. What goes wrong for a client that waits for a long command?

   :::answer{tests="close-order"}
   The client gets no answer. The connection closes when the server stops, and the cancelled command's completion has no open connection to send its Cancelled result over. The client sees a dropped connection and cannot tell a cancel from a crash. The real order cancels first, so every waiting client is answered.
   :::

## Exercises

1. **Basic.** Trace it yourself. Set `STRATA_SESSION_DIR` to a scratch folder. Run `StrataCLI launch --headless --project ./Cave` and, when it returns, `StrataCLI launch --headless`. Then compare `StrataCLI call rpc.ping` with `StrataCLI call rpc.ping --project ./Cave`: predict which editor each reaches, and confirm it in the code.

   :::answer[Worked solution]{tests="predict-editor"}
   The call without a project reaches the second editor, the one without a project, because it started later and discovery lists every live session newest first. The call with `--project ./Cave` reaches the first editor, whose pointer and session name `Cave`.

   Confirm it in `StrataCLI/src/CLI/EditorConnection.cpp`. In `DiscoverEditorEndpoints`, the branch `if (!options.ProjectDirectory.empty())` reads the pointer through `EditorSession::ReadProjectSession` and then adds the sessions for which `IsSameProject` is true. Otherwise the last loop adds every session in the order that `EditorSession::FindSessions` returned them. The case `Endpoints are discovered in precedence order` in `StrataTests/src/CLI/EditorDiscoveryTests.cpp` shows the same order with four sessions.
   :::

2. **Medium.** A client is pinned to the editor of process 700 with project `Cave`. Three sessions are alive: process 700, now with project `Beach`; process 800 with `Cave`; process 900 with `Beach`. List the candidates the pin accepts, and say which the client uses.

   :::answer[Worked solution]{tests="predict-editor"}
   `AddPinnedProcessEndpoint` puts process 700 first, since the pin names it. `IsPinnedEditor` accepts 700, because its process and start time match. It accepts 800, because its project is `Cave`, the pinned one. It refuses 900: another process, and `Beach` is not `Cave`. The client tries 700 first and uses it, and keeps 800 as a fallback.
   :::

3. **Hard.** Write a program that models the stall timer. It polls every 250 ms and reads a list of progress counts; it fails when the count has not changed for 2,000 ms. Run it on a stuck scan and on a slow scan that changes every 1,750 ms.

   :::answer[Worked solution]{solution="sketches/automation-sessions-stall.cpp" tests="launch-ready"}
   The program keeps the time of the last change, as `WaitForEditorProject` does. Each poll first updates it when the count differs, and then checks the stall. The stuck scan fails at 2,500 ms, since its count last changed at 500 ms. The slow scan never fails, because its gaps of 1,750 ms stay below the limit.

   ```cpp sketch="automation-sessions-stall.cpp"
   // The stall timer of a launch: it restarts whenever the progress count changes.
   #include <cstddef>
   #include <iostream>
   #include <string>
   #include <vector>

   static void Run(const std::string& title, const std::vector<int>& counts)
   {
   	const int pollMilliseconds = 250;
   	const int stallMilliseconds = 2000;
   	int last = -1;
   	int lastChange = 0;
   	for (size_t poll = 0; poll < counts.size(); poll++)
   	{
   		const int now = static_cast<int>(poll) * pollMilliseconds;
   		if (counts[poll] != last)
   		{
   			last = counts[poll];
   			lastChange = now;
   		}
   		if (now - lastChange >= stallMilliseconds)
   		{
   			std::cout << title << ": stalled at " << now << " ms, last change at " << lastChange << " ms\n";
   			return;
   		}
   	}
   	std::cout << title << ": ready\n";
   }

   int main()
   {
   	std::vector<int> stuck = { 10, 20, 30 };
   	stuck.resize(20, 30);

   	std::vector<int> slow;
   	for (int poll = 0; poll < 20; poll++)
   		slow.push_back(poll / 7);

   	Run("stuck", stuck);
   	Run("slow", slow);
   	return 0;
   }
   ```

   ```text output-of="automation-sessions-stall.cpp"
   stuck: stalled at 2500 ms, last change at 500 ms
   slow: ready
   ```

   1. **Lines 16–20:** a changed count restarts the timer, as in the real loop.
   2. **Lines 21–25:** the stall check runs after the update, so a change always wins.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Network/EditorSession.cpp`: `WriteSessionFiles`, `FindSessions`, `ReadProjectSession`, `IsSameProject` and `GetSessionDirectory`.
- `StrataCLI/src/CLI/EditorConnection.cpp`: `DiscoverEditorEndpoints`, `EditorConnection::EnsureConnected` and `EditorConnection::IsPinnedEditor`.
- `StrataCLI/src/CLI/EditorLauncher.cpp`: `ResolveEditorPath`, `LaunchEditor`, `WaitForEditorSession` and `WaitForEditorProject`.
- `StrataEditor/src/Editor/EditorAutomation.cpp`: `Start`, `Stop`, `UpdateSession` and `HasIdledOut`; `StrataEditor/src/EditorLayer.cpp`: `OnDetach`.
- Tests: the suites `CLI.Discovery` and `Editor.Automation`.
- Settings: `STRATA_SESSION_DIR`, `STRATA_EDITOR_PATH`, `STRATA_EDITOR_PORT`, `STRATA_EDITOR_TOKEN`, and the editor options `--automation-port`, `--idle-timeout`, `--no-automation`, `--headless` and `--no-gpu`.

## Further reading

- The Language Server Protocol specification (documentation; intermediate): how editors and servers agree on a connection that a parent process starts.
- Kubernetes documentation on liveness and readiness probes (documentation; beginner): the same split between a process that runs and a process that is ready.
- Martin Kleppmann, "Designing Data-Intensive Applications", chapter 8 (book; intermediate): why a fixed timeout cannot tell a slow peer from a dead one.
