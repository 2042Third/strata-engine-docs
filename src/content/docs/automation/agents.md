---
id: automation/agents
title: "How the editor makes games with agents"
description: "Why Strata's editor offers its commands to other programs, how an AI agent reads them, and what keeps the person in control."
kind: concept
size: M
tracks: [E]
needs: [editor/journal]
time: 45
learn:
  - id: why-commands
    text: explain why Strata offers commands to agents instead of a scripting API
  - id: four-layers
    text: name the four layers between an agent and the editor and the page that explains each
  - id: tool-cost
    text: explain what an agent sees of a tool, what a definition costs and how Strata limits it
  - id: judge-command
    text: compare the first sentence and kind of a command as an agent reads them
  - id: agent-session
    text: trace an agent's session through StrataCLI call by call
since: 0.3.0
status: final
---

You ask a program that writes text to build a level: a floor, four walls and a ball that falls. The program lives in a terminal. It can read and write words, and it can start other programs. The editor, in contrast, is windows, panels and mouse clicks. How does the program reach a button it cannot see?

The answer is **automation**: another program, not a person, operates the editor.

The program in the story is an **AI agent**: a program built on a language model that reads descriptions of tools and calls them to reach a goal. This page shows why Strata can serve such an agent without a second interface, what the agent sees, and how the person stays in charge.

## Clicks and a second API both break

The first idea is to let the agent act as a person does: take a picture of the screen, find the button and send a click. Engineers call this user interface (UI) automation, and it fails in three ways. A click depends on where the button is, so a moved panel or another window size breaks it. The program must guess what a picture means. And it is slow: one picture and one guess for every step.

The second idea is to write a separate interface for agents, with its own list of operations. It works at first. Then someone adds a feature to the editor and forgets the agent interface, or the two disagree on what "delete an entity" does. Each feature now exists twice, and the copies drift apart.

## Every operation is already a command

Strata starts from the other side. Every operation of the editor, from creating an entity to exporting a game, is a command, as the page [Commands](../editor/commands.md) explains. A command has a name such as `entity.create`, a description, a :term[JSON Schema]{id=json-schema} for its parameters and a kind. The menus and buttons call these commands. They hold no logic of their own.

So the editor does not need a second interface. It must only offer the same commands to other programs. A script, a test, a person at a terminal and an agent then use the one registry that the menus use. A change made through a command has an :term[undo step]{id=undo-step} and a journal entry, like a click. A new feature reaches every client the moment it registers a command.

```mermaid caption="The menus and every other client call the same registry of commands, so a feature written once reaches all of them." alt="Three boxes, for menus, command scripts and remote clients, point to one box named command registry. It points to the scene and the project."
flowchart LR
    UI["Menus and buttons"] --> R["Command registry"]
    S["Command scripts"] --> R
    C["Remote clients and agents"] --> R
    R --> P["Scene and project"]
```

So the part has one rule: commands are the application programming interface (API). Strata writes no endpoint for a feature; it registers a command with a description that an agent can act on.

## How engines let other programs in

Other engines meet the same problem, and four answers are common. Each is brought in by the flaw of the one before.

An **embedded script language** runs inside the editor. Python in Unreal and Blender, and C# editor scripts in Unity, can call the editor's own functions. The flaw: the script runs in a person's open editor, and the language's API is a second surface that grows beside the interface.

A **batch mode** starts the editor without a window, runs one script and exits. Unity does this with `-batchmode -executeMethod`, and Godot with `--headless --script`. It suits a build server. The flaw: nothing answers between the start and the exit, so a program that must look at a result and then choose its next step has to start the editor again for each step.

A **remote-control protocol** keeps the editor running and listens on a network socket. Unreal's Remote Control API, the browser developer tools' protocol and language servers work this way. A client sends a request, reads the answer and sends the next. The flaw: the protocol exposes whatever its authors chose to expose, and a feature without a handler is out of reach.

**UI automation**, the idea from the start of this page, needs no help from the editor. That is its one strength, and it is brittle for the reasons above.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Embedded script language | Learn a second API | Full reach where the API exposes it | A language and its bindings to maintain | Unreal, Blender, Unity |
| Batch mode | Start the editor for every run | Same result each run, no feedback between steps | A :term[command line]{id=terminal-command} and an :term[exit code]{id=exit-code} | Unity, Godot |
| Remote protocol | A socket, a format and a security model | Live answers, any client | A server inside the editor | Unreal, browsers, language servers |
| UI automation | Pictures and clicks | Breaks when the layout moves | None in the editor, much in the client | Test tools for any program |

:::example[Reaching a rename from four directions]
Take one operation: rename the entity `Ball` to `Sphere`. An embedded script calls a function inside the open editor. A batch mode runs a script file and you read the result after the exit. A remote protocol takes one message and sends one reply. UI automation finds the hierarchy row on a picture, double-clicks it, types the new name and presses **Enter**.

Now move the hierarchy panel to the right. The first three still work, since none used the panel's place. The fourth clicks on empty ground.
:::

## Strata offers a batch mode and a remote protocol on one registry

Strata takes two of the four. The batch mode is `StrataEditor --commands script.json`, which runs a [command script](../editor/command-scripts.md) at startup. The remote protocol is JSON-RPC on the loopback network, which the editor serves while it runs. Both call the registry of the diagram above. The Model Context Protocol (MCP) turns the same commands into tools for language models.

:::why[Why not a scripting API in the editor?]
A scripting API is a second surface. Every feature needs a function in it, a test for the function and a rule for what happens in :term[Play mode]{id=play-mode}, with undo and when scenes load. A registry has one surface. The command already has an :term[undo step]{id=undo-step}, a journal entry, a kind and a schema, and the remote protocol adds no code for it.

The cost is that a command is data in and data out. A client cannot hold an editor object and call methods on it as an embedded script can. Strata accepts this: :term[JSON]{id=json} crosses every boundary, so a client in any language may crash without harming the editor.
:::

The rest of the part follows one path. A client reaches the editor through four layers, and each has its own page.

## Four layers between an agent and the editor

```mermaid caption="An agent's call crosses four layers: the client, the transport, the editor's binding to the registry and the person's view of what happened." alt="Four boxes in a row. A client box holds an MCP client or StrataCLI. A transport box shows a loopback network connection. A binding box shows the editor's server thread, a request queue and the main thread running the registry. A view box shows the person's status bar, viewport and Activity panel."
flowchart LR
    A["Clients: an MCP client or StrataCLI, with call and --commands as other ways in"] --> B["Transport: loopback TCP, JSON-RPC"]
    B --> C["Editor binding: server thread, request queue, main thread, registry"]
    C --> D["The person's view: status bar, viewport chip, Activity panel"]
```

The first layer is the **clients**: a program such as Claude Code that speaks MCP, or `StrataCLI`, which is both a command line for one call and the MCP server that Claude Code starts. The page [Model Context Protocol and toolsets](../automation/mcp.md) explains them. The second layer is the **transport**, the loopback connection and its message format, taught in [JSON-RPC](../automation/json-rpc.md). It listens on this machine only.

The third layer is the editor's **binding**. A network thread reads requests and queues them, and the :term[main thread]{id=main-thread} runs each command in the registry, because only the main thread may touch the scene. The page [The editor's server](../automation/rpc-server.md) explains this layer. The fourth layer is the person's view: the status bar, the :term[viewport]{id=viewport-input} and the Activity panel show that an agent is present and what it did. The page [The activity journal and replays](../editor/journal.md) explains how.

## What an agent sees, and what it pays

A **tool** is one operation that a language model may call: it has a name, a description and a JSON Schema of its parameters. The agent sees nothing else of a tool. It cannot read the source or the menus. If the description is vague, the agent guesses.

The text of every tool definition is part of the agent's input, which a language model reads as **tokens**: small pieces of text, a few letters or a short word each. A model can hold only so many tokens at once, the context. Every definition takes space in it for the whole session, and that space is lost to the plan, the files and the results. Clients also cap the number of tools they accept; some allow about 128.

Strata has more commands than that cap. If each became a tool with its full text, the definitions could fill much of the context before the first call. The design question is how to offer many operations through few tools.

## Four ways to offer tools

Engines and tool makers use four designs, each answering a flaw of the one before.

- **One tool per operation.** Every command is a tool. The agent sees exactly what exists, and the schema checks each call. The cost: every definition is paid for at once, and the cap is reached quickly.
- **One generic tool.** A single tool takes a command name and its parameters. It costs almost nothing, but the agent must know the names and the parameters before it starts.
- **Sets that change.** Tools come in named groups, and the agent enables the groups it needs. The cost is held down, but the client must support a changing list.
- **A tool that describes the others.** The agent asks for the description of a command when it needs it. It pays only for what it uses, at the price of one more call.

Strata mixes them. `StrataCLI mcp` lists a small default set, the `core` toolset, with one tool for each command a game is made and tested with. It adds generic tools: `strata_status`, `strata_launch_editor`, `strata_describe`, `strata_toolsets` and `strata_call`. Definitions are compact: the first sentence of each description.

The agent asks `strata_describe` for the full text, enables more toolsets when it needs them, and reaches any command through `strata_call`. A test holds the default set within its budget, and the page [Model Context Protocol and toolsets](../automation/mcp.md) shows how the toolsets work.

The first sentence of a description is often all an agent reads. A first sentence that names the action in words an agent would search for makes the command found and used. The second thing an agent reads is the kind, which `editor.commands` lists beside each description: Edit changes the scene or the project, Query only reads, and Session changes the editor's session, such as Play mode. From the kind an agent knows which calls are safe to try and which a replay repeats.

## What an agent reads first

A new agent knows nothing about the open editor. Its first call is `editor.status`, which the command's own description calls the place to start. The default answer is compact: the engine version, the project, the scene and its entity count, the play state, the selection, the undo names, the error count and the state of assets. The agent can ask for sections that add more, such as `automation`, `editor`, `sceneLoad` and `recovery`.

A section the agent does not ask for costs it nothing. The section of an editor part exists only while that part runs: an editor started with `--no-automation` refuses `automation` as an unknown section.

The `errors.unread` count is the second thing to read. It counts the errors logged since the last `log.read`. Reading the log from level Error marks them read, so the count measures what the agent has not yet seen.

An agent also needs a manual. Release archives ship three skills in a `Skills/` folder next to the editor: `strata-editor-automation`, `strata-make-a-game` and `strata-scripting`. The first teaches how to get an editor, call commands and handle undo, saves, play mode and errors. The second is a guide to a whole game, from a plan to an export; the Tetris sample was made with it. The third teaches the script software development kit (:term[SDK]{id=sdk}), which the part on scripting covers.

A person who connects Claude Code follows [Making a game with an agent](../make/with-an-agent.md).

## The person stays in charge

When a person and an agent share an editor, the person needs three things: to see what the agent did, to undo it, and to keep the work as a test.

Four tools meet this need. A log lists what happened but cannot reverse it. An undo history reverses but does not say who acted. A :term[macro]{id=macro} recorder keeps the actions but sees only what the interface does. Event sourcing keeps every change as a stored event, so you can rebuild the state; the journal follows that model.

Strata journals every command once, with its origin and the name the client gave, and shows an agent's presence in the interface. A session exports as a command script that repeats it on a fresh copy of the project. The mechanism belongs to [The activity journal and replays](../editor/journal.md). Here the point is the design goal: a client may be as powerful as a person only if the person can see, undo and replay what it does.

## Agents count fixed steps, not frames

An agent's call takes about a tenth of a second. Between two calls a running game continues, and a machine with a faster display runs more frames in that time. A test that says "press jump, wait 30 frames, read the height" gives different answers on two machines, and on one machine at two moments.

So the tools count game time in :term[fixed steps]{id=fixed-step}, never in frames, as [Fixed steps, stepping and input sequences](../editor/stepping.md) shows. An agent that says "advance 60 steps" gets one second of game time everywhere. This is why `play.step` and `input.sequence` take steps.

:::example[An agent's whole session, call by call]
Strata has a test that plays the part of an agent. It starts a headless editor, which runs without a window, here also without a graphics device, and talks to it only through `StrataCLI`, as Claude Code would. The test case is in `StrataTests/src/Editor/EditorAutomationProcessTests.cpp`.

:::question
Can I follow a test written in C++ if I do not know the language yet? Yes, by its comments and call names, and the pages on [functions](../basics/programming-2.md), [classes](../basics/programming-3.md), [pointers](../basics/cpp-memory.md), [templates and lambdas](../basics/cpp-generic.md) and [modern C++](../basics/cpp-modern.md) explain the rest.
:::

First the agent discovers the editor. It lists the commands, reads the schema of `entity.create` and asks for status with two sections. Search the code for what the test checks: a description is present and a schema has a `name`.

```cpp src="StrataTests/src/Editor/EditorAutomationProcessTests.cpp#L341-L374"
TEST_CASE("An agent builds, plays, saves and exports a game through StrataCLI")
{
	if (!HasBuiltExecutables())
		return;
	EndToEndEnvironment environment("EndToEndCli");
	const std::filesystem::path projectDirectory = environment.Root / "Tetris";
	const std::filesystem::path buildDirectory = environment.Root / "Build";

	// A headless editor without a GPU, serving automation on a free port, and found through its session file.
	EditorProcess editor;
	REQUIRE(editor.Start({ "--no-gpu" }));
	const std::optional<EditorSessionInfo> session = editor.WaitForSession(environment.SessionDirectory);
	REQUIRE(session.has_value());
	CHECK(session->Headless);
	CHECK(session->ProjectPath.empty());

	// Discovery: the commands, with descriptions and parameter schemas.
	const CliResult list = RunCli({ "list" });
	REQUIRE(list.ExitCode == 0);
	for (const char* method : { "entity.create", "component.set", "editor.wait", "editor.status", "editor.quit", "project.export" })
		CHECK_MESSAGE(ContainsLine(list.Output, method), method);
	const CliResult schemas = RunCli({ "list", "--json" });
	REQUIRE(schemas.ExitCode == 0);
	const nlohmann::json& methods = schemas.Json["methods"];
	const auto entityCreate = std::find_if(methods.begin(), methods.end(), [](const nlohmann::json& method) { return method["name"] == "entity.create"; });
	REQUIRE(entityCreate != methods.end());
	CHECK((*entityCreate)["paramsSchema"]["properties"].contains("name"));
	CHECK_FALSE((*entityCreate)["description"].get<std::string>().empty());

	nlohmann::json status = Call("editor.status", { { "sections", { "automation", "editor" } } });
	CHECK(status["project"]["open"] == false);
	CHECK(status["automation"]["port"] == session->Port);
	CHECK(status["editor"]["headless"] == true);
	CHECK(status["editor"]["graphicsDevice"] == false);
```

1. **Line 351:** the test starts the editor with `--no-gpu`, so a build machine without a :term[graphics card]{id=gpu} can run it.
2. **Line 358:** `list` prints every command with its description; `list --json` adds the parameter schemas that the agent reads before it calls.
3. **Line 370:** `editor.status` with the sections `automation` and `editor` shows the port the editor serves and that it is headless.

Next the agent builds a scene, plays it and undoes an edit. The calls create a project, add an entity with its transform, add a mesh and scale it. Then they start Play mode and add an entity in it. In Play mode, changes go to a :term[running copy]{id=running-copy}, so the answer carries a warning, and `play.stop` discards the copy.

```cpp src="StrataTests/src/Editor/EditorAutomationProcessTests.cpp#L377-L402"
Call("project.create", { { "directory", FileSystem::ToUTF8(projectDirectory) }, { "name", "Tetris" } });
// The session follows the project before the answer arrives: the very next call finds the editor by it.
const CliResult byNewProject = RunCli({ "call", "editor.status", "--project", FileSystem::ToUTF8(projectDirectory) });
REQUIRE_MESSAGE(byNewProject.ExitCode == 0, byNewProject.ErrorOutput);
CHECK(byNewProject.Json["project"]["name"] == "Tetris");
const nlohmann::json board = Call("entity.create", { { "name", "Board" }, { "components", { { "Transform", { { "Translation", { 0, 1, 0 } } } } } } });
const std::string boardId = board["id"].get<std::string>();
Call("component.add", { { "entity", boardId }, { "component", "MeshRenderer" }, { "values", { { "Mesh", "Builtin/Cube" } } } });
Call("component.set", { { "entity", boardId }, { "component", "Transform" }, { "values", { { "Scale", { 2, 2, 2 } } } } });
CHECK(Call("component.get", { { "entity", boardId }, { "component", "Transform" } })["values"]["Scale"] == nlohmann::json { 2.0, 2.0, 2.0 });

// Deferred commands answer once their frames have passed.
CHECK(Call("editor.wait", { { "frames", 10 } })["frames"] == 10);

// Play: changes apply to the running copy, with a warning, and play.stop discards them.
CHECK(Call("play.start")["state"] == "Play");
const nlohmann::json temporary = Call("entity.create", { { "name", "Temporary" } });
CHECK(temporary.contains("warning"));
Call("editor.wait", { { "frames", 5 } });
CHECK(Call("play.stop")["state"] == "Edit");
CHECK(Call("entity.find", { { "name", "Temporary" } })["entities"].empty());

// Undo the last edit.
const nlohmann::json undone = Call("edit.undo");
CHECK(undone["redo"].get<std::string>().rfind("Set Scale of ", 0) == 0); // The step names what it changed
CHECK(Call("component.get", { { "entity", boardId }, { "component", "Transform" } })["values"]["Scale"] == nlohmann::json { 1.0, 1.0, 1.0 });
```

1. **Line 382:** one `entity.create` call carries the name and the transform; the result holds the new entity's identifier (ID).
2. **Lines 392–397:** `play.start` begins Play mode, the edit gets a `warning`, and after `play.stop` the entity is gone.
3. **Lines 400–402:** `edit.undo` names the step it reverts, and the scale returns to 1.

Last the agent meets errors, saves and exports. A bad call returns a structured error with the command's own parameter schema attached, so the agent can correct itself from the error alone.

```cpp src="StrataTests/src/Editor/EditorAutomationProcessTests.cpp#L405-L420"
const nlohmann::json invalid = CallError("entity.get", { { "entity", "00000000DEADBEEF" } });
CHECK(invalid["code"] == JsonRpc::ErrorCode::InvalidParams);
CHECK(invalid["data"]["command"] == "entity.get");
CHECK(invalid["data"]["parameters"]["properties"].contains("entity"));
CHECK(CallError("no.such.command")["code"] == JsonRpc::ErrorCode::MethodNotFound);
const nlohmann::json unsaved = CallError("editor.quit");
CHECK(unsaved["code"] == JsonRpc::ErrorCode::OperationFailed);
CHECK(unsaved["message"].get<std::string>().find("unsaved changes") != std::string::npos);

// Save, then export a playable game.
Call("scene.saveAs", { { "path", "Scenes/Main.stscene" } });
Call("project.setStartScene", { { "scene", "Scenes/Main.stscene" } });
const nlohmann::json exported = Call("project.export", { { "directory", FileSystem::ToUTF8(buildDirectory) }, { "includeRuntime", false } });
CHECK(FileSystem::IsRegularFile(FileSystem::FromUTF8(exported["manifest"].get<std::string>())));
CHECK(FileSystem::IsRegularFile(FileSystem::FromUTF8(exported["assetPack"].get<std::string>())));
CHECK(exported["assetCount"].get<int>() > 0);
```

1. **Lines 405–409:** a wrong ID and an unknown command return codes, and the error holds the command's schema.
2. **Lines 410–412:** the quit fails because the scene has changes not yet saved.
3. **Lines 415–420:** `scene.saveAs`, `project.setStartScene` and `project.export` end the session.

After the export the test asks for status by project folder and finds the editor, so the session follows the project. The quit that failed with a clear reason now succeeds.
:::

## What this design cannot do

An exported game has no automation. The editor serves the commands. A shipped game runs in the :term[runtime]{id=runtime}, which has no editor and no registry to serve, so an agent cannot drive a game that a player holds. To test such a game, test it in the editor, in Play mode, before the export. The page [The runtime](../worlds/runtime.md) explains why the exported game lacks it.

Commands are also whole operations, not a live view. An agent cannot watch a frame as it renders; it asks for a capture and reads it. Strata does not offer a script language that runs inside the editor either, because the design chose commands over a second surface; the appendix [What Strata does not do](../appendix/not-in-strata.md) lists such choices.

## Common mistakes

- **Writing an endpoint for a feature.** The symptom: the feature works for agents but has no undo and no journal entry. The fix: register a command and write nothing else.
- **Writing a description for people.** The symptom: an agent opens with the wrong command or skips a right one. The fix: make the first sentence say what the command does, in words an agent would search for, and describe every parameter in its schema.
- **Waiting in frames.** The symptom: a play-test passes on your machine and fails on a slower one. The fix: count fixed steps with `play.step` or `input.sequence`.
- **Reading the compact status as everything.** The symptom: an agent acts without knowing a scene is still loading. The fix: ask for the `sceneLoad` section when a project has been opened.
- **Taking an entity's ID from the selection in a session you want to replay.** The symptom: the replay finds no such entity. The fix: bind the ID of what the session created, as the journal page shows.

## Summary

- Strata offers the commands that the menus call to other programs, because a second surface for agents would drift from the interface.
- Four layers lie between an agent and the editor: the clients, the transport, the editor binding and the person's view.
- An agent sees only a tool's name, description and schema. Each definition costs tokens and clients cap the count, so Strata lists a small core set, compact definitions and generic tools.
- An agent reads the first sentence and the kind of a command, so a first sentence that names the action makes the command usable.
- An agent's session runs through StrataCLI call by call: discover, read status, build, play, undo, save, export and quit.

## Check yourself

1. A teammate proposes a new feature with an endpoint only for agents, "because it is quicker than a command". Which reason against it is right? (a) The endpoint would be slower; (b) the feature would exist twice, and the copies would drift apart; (c) agents cannot call endpoints; (d) endpoints cannot return JSON.

   :::answer{tests="why-commands"}
   Option (b). The registry is the one surface the menus, scripts and agents share, so a second one means two implementations. Option (a) is false and (d) is false, since an endpoint can answer quickly and in JSON. Option (c) is false: agents call whatever they are given.
   :::

2. Name the four layers, from the agent to the person, and the page that explains each.

   :::answer{tests="four-layers"}
   Clients, with the MCP page. Transport, with the JSON-RPC page. The editor binding, with the server page. The person's view, with the journal page.
   :::

3. The editor has :value{key="commands.count"} commands and the client takes about 128 tools. Which design fits: one tool per command, one generic tool, or Strata's mix? Give the cost of the other two.

   :::answer{tests="tool-cost"}
   Strata's mix: a small core set, compact definitions and generic tools. One tool per command passes the cap and fills the context with definitions. One generic tool is cheap, but the agent must already know every name and parameter.
   :::

4. Two commands have these first sentences: "Overview of the editor; start here to orient yourself." and "Internal state handling for the scene subsystem." Which will an agent use well, and why?

   :::answer{tests="judge-command"}
   The first. It says what the command returns and when to call it. The second names an internal part and no action, so an agent cannot tell when it applies and may skip it or call it by mistake.
   :::

5. In the session test, `play.start` is followed by `entity.create` for `Temporary`, then `play.stop`. Does `Temporary` exist afterwards, and why?

   :::answer{tests="agent-session"}
   No. In Play mode the edit goes to the running copy, so the answer carries a warning, and `play.stop` discards the copy. The test checks that `entity.find` returns no entity named `Temporary`.
   :::

## Exercises

1. **Basic.** With the Tetris sample open in the editor, read it as an agent does. Call `editor.status` compact, then with the sections `automation` and `sceneLoad`, then `log.read` from level Error, then `editor.status` again. Say what each answer tells an agent before it acts, and why the last call shows no errors waiting.

   :::answer[Worked solution]{tests="tool-cost agent-session" solution="tutorials/automation/agents/exercise-1.tutorial.json"}
   Run `StrataCLI call editor.status`, then `StrataCLI call editor.status '{"sections":["automation","sceneLoad"]}'`, then `StrataCLI call log.read '{"minLevel":"Error"}'`, then `StrataCLI call editor.status` again. The compact answer shows the project (`Tetris`), the scene (`Main`) and the play state (`Edit`); `automation` adds the port and the clients, among them `StrataCLI` itself; `sceneLoad` is null when no scene is loading.

   The log read marks every error read, so `errors.unread` is 0 in the last answer. The sample opens without errors, so it was 0 before as well. Run as a command script, the calls need an editor that serves automation. Started with `--no-automation`, the editor refuses the section `automation`.
   :::

2. **Medium.** In `StrataCLI list`, find three commands and judge the first sentence of each: does it say what the command does, in words an agent would use? Rewrite one that does not.

   :::answer[Worked solution]{tests="judge-command"}
   Pick three, such as `entity.create`, `play.step` and `log.read`. A good first sentence has a verb and an object. If one opens with a condition or a detail of the implementation, move the action first and keep the detail after it.
   :::

3. **Hard.** Design the tools for a new feature, a command `light.setColor`, for agents: write its first sentence, say what its kind is and why, and say whether it belongs in the `core` toolset.

   :::answer[Worked solution]{tests="judge-command tool-cost"}
   A first sentence: "Sets the color of a light on an entity." Its kind is Edit, since it changes project content, so a replay repeats it. It stays out of `core`, which holds what a game is made with every time. A group that the toolset map of `StrataCLI` does not name becomes a toolset of its own name, so it would sit in a `light` toolset. Adding `light.` to the map beside `lighting.` puts it in `scene`, which an agent enables when it needs it.
   :::

## Where it lives in Strata

- The commands: `editor.status`, `log.read`, `editor.activity`, `editor.activity.export`, `editor.batch`, `editor.wait`, `play.step` and `input.sequence`.
- The editor program: `StrataEditor --commands`, `--no-gpu` and `--headless`; the client: `StrataCLI call`, `list`, `status`, `launch` and `mcp`.
- The MCP tools: `strata_status`, `strata_launch_editor`, `strata_describe`, `strata_toolsets` and `strata_call`.
- The skills, installed under `Skills/` by `CMake/StrataPackaging.cmake`: `strata-editor-automation`, `strata-make-a-game` and `strata-scripting`.
- The test: the suite `EndToEnd.EditorAutomation`, in `StrataTests/src/Editor/EditorAutomationProcessTests.cpp`.

## Further reading

- Model Context Protocol documentation, modelcontextprotocol.io: the protocol an agent's client speaks (intermediate).
- Claude Code documentation, code.claude.com: how a person connects an agent to an MCP server (beginner).
- Unity manual, docs.unity3d.com: batch mode and editor scripting (intermediate).
- Godot documentation, docs.godotengine.org: command line options, including headless runs and scripts (intermediate).
- Unreal Engine documentation on Python scripting and the Remote Control API (intermediate).
- Language Server Protocol specification and Chrome DevTools Protocol documentation: two remote-control protocols (advanced).
- Martin Fowler, "Event Sourcing", martinfowler.com: keeping changes as stored events (intermediate).
