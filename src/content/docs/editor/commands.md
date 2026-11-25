---
id: editor/commands
title: "Commands"
description: "How every editor operation is one named command with a schema, so a person, an AI agent and a test make the same edit and get the same answer."
kind: internals
size: L
tracks: [E]
needs: [world/reflection, basics/data-formats, editor/program]
time: 90
learn:
  - id: command-contract
    text: explain what each part of a command registration is for and what a call does in order
  - id: call-from-terminal
    text: run one command from a terminal with StrataCLI call and read its answer or error
  - id: trace-refusal
    text: trace a call with an unknown parameter from Execute to the line that refuses it
  - id: write-for-agents
    text: choose the kind, flags and schema of a new command so that an agent can use it
since: 0.3.0
status: final
---

The editor changes a project in more than a hundred ways: it creates an entity, moves an asset, starts the game, saves a scene. Strata gives each way one name, one description, one description of its inputs and one handler, and calls the bundle a command. The Hierarchy panel, an artificial intelligence (AI) agent, a recorded script and a unit test all call the same command, so they get the same edit and the same answer. You learn here what a command is, what the registry does between a call and the handler, which rules every command follows and why, and how you run one from a terminal. Undo, answers that arrive in a later frame, the activity journal and the network path each have their own page.

## The problem and how engines solve it

Think of renaming an entity in the Hierarchy panel. A person clicks and types a name. Now an agent must do the same thing with no mouse, and a test must do it a thousand times. If each of the three has its own code path, the three drift apart: the person's rename records an undo step, the agent's does not, and the test passes while the real editor is broken.

Engines solve this in three common ways. The first keeps in-process command objects: the user interface (UI) builds an object such as "rename entity 7", and the editor runs it. That gives undo for free but serves only code inside the program.

The second exposes a scripting interface, so an outside tool writes small programs against the editor's own classes. That is flexible, but the tool must know the internal classes, and a mistake can reach any part of the editor. The third makes remote calls: the editor listens on a port, and a tool sends a named request. Remote calls suit agents; the pages on [agents](../automation/agents.md) and the [automation server](../automation/rpc-server.md) show how Strata offers them.

Strata combines the first and the third with one rule, **commands are the API**. A **command** is a named editor operation that takes one :term[JSON object]{id=json-object} of parameters and returns a :term[JSON]{id=json} value or an error. The name is `<group>.<action>`, as in `entity.create`. Every operation of the editor is such a command, kept in one place, and the UI, the automation server and command scripts all call it there.

The choice has a cost. A button cannot hand a live C++ object to its operation; it must put what it means into JSON, and the handler must read it back and check it. That is slower to write than a direct call, and it forces every handler to defend itself against bad input. Strata accepts both costs because the same defence is what makes the editor safe to drive from outside.

## The map

Three kinds of caller reach one registry. The **command registry** (`EditorCommandRegistry`) is the editor's table from names to commands.

```mermaid caption="The panels, the automation server and command scripts all call the same registry, whose handlers change the editor's scene and project." alt="Three boxes on the left: the editor's panels, the automation server for agents and terminals, and command scripts and tests. Arrows from all three lead into one box, the command registry, and from it to the handlers, which change the scene and the project."
flowchart LR
    UI["Editor panels"] --> R["Command registry"]
    A["Automation server (agents, StrataCLI)"] --> R
    S["Command scripts and tests"] --> R
    R --> H["Handlers"]
    H --> E["Scene and project"]
```

Each entry holds the description an agent reads and the handler that does the work. It also holds a parameter description in the form of a **JSON Schema**: a JSON document that states which parameters an object may hold, their types and which are required.

The files live in `StrataEditor/src/Editor/`. `EditorCommands.h` and `EditorCommands.cpp` hold the command, its result, the registry and the argument reader. `CommandUtils.h` holds helpers shared by handlers. The commands themselves live in files by group, such as `Commands/EntityCommands.cpp`. All of it runs on the :term[main thread]{id=main-thread}, as the [editor program](../editor/program.md) page explains, so a handler never races with a frame.

The second diagram follows one call. Everything the registry does for a command happens in this order, and the rest of the page explains each box.

```mermaid caption="A call is found, recorded in the journal, run after the schema check, and finished with the undo step noted; a handler that answers later takes the branch on the right." alt="A flow of boxes from top to bottom: find the command, begin a journal entry, then either wait for the asset scan or run. Running checks the schema, then calls the handler. After that the undo step is attributed and the journal entry is completed, or suspended when the answer is pending."
flowchart TD
    F["Find the command by name"] --> J["Begin a journal entry"]
    J --> W{"Waits for the asset scan?"}
    W -- yes --> D["Defer: poll each frame until the scan ends"]
    W -- no --> RUN["Run: schema check, then handler"]
    D --> RUN
    RUN --> U["Attribute the undo step to the entry"]
    U --> P{"Answer pending?"}
    P -- no --> C["Complete the entry with the result"]
    P -- yes --> S["Suspend the entry (the deferred commands page)"]
```

## The contract

Callers may rely on the rules below, and a command author must keep them. Each rule comes with its reason.

### The result

A call returns an `EditorCommandResult`. On success it holds a JSON value, or null when there is nothing to return. On failure it holds an error message and a kind. The kind exists because callers must tell two situations apart: a request that is wrong, and a request that is right but cannot be done now.

The kinds are `UnknownCommand`, `InvalidParameters`, `Failed`, `Cancelled` and `Internal`. The first two blame the caller. `Cancelled` means a pending command was abandoned, for example because the editor is closing. `Internal` means an unexpected failure inside a command.

**`InvalidParameters`** is the error kind for a request the command cannot accept: a parameter that is unknown, missing, of the wrong type, out of range, or that names something that does not exist.

**`Failed`** is the error kind for a request that was valid, but that the command could not do at this moment, such as asking to undo when there is nothing to undo. The distinction is a promise to the client. With `InvalidParameters` the client edits its request and tries again. With `Failed` the same request may succeed later, once the editor is in another state.

### The registration

A command is a :term[struct]{id=struct} with a name, a description, a parameter schema, a handler and a few marks. The description is written for agents: it says what the command does and what it returns. The schema is the contract for the parameters.

A **command kind** is the mark that says what a command does to the project. There are three. `Edit` changes the scene, its assets or the project. `Query` changes nothing. `Session` changes only the editor's own session: the open project, play mode, the view or the selection.

Two more marks refine this. The **session results** mark names the queries whose answers follow the editor's session, such as the selection, so a replay of recorded commands never relies on the identifiers (IDs) they show. Those IDs differ from one session to the next.

`WaitsForAssets` marks a command that answers from the whole asset registry, so it waits while the project's assets are scanned in the background. `MayDefer` marks a command that may answer in a later frame. The command `editor.commands` reports all three marks of every command to agents, as `results`, `mayDefer` and `waitsForAssets`; that last one is also true for every `Edit`. The [deferred commands](../editor/deferred-commands.md) page teaches both flags in full, and the [journal](../editor/journal.md) page teaches what a replay keeps and what it drops.

A command that states no kind counts as an `Edit`. That default is safe: a replay then never forgets an edit, at the price of repeating a harmless query. To make the choice deliberate, Strata tests it, as the section on testing shows.

### The call, in order

`Execute` is the only door. It finds the command and opens a journal entry that records who called, the name and the parameters. It notes how many undo records exist. If the command is an `Edit`, or marked `WaitsForAssets`, and the project's assets are still being scanned, the call is deferred until the scan ends; this wait belongs to the registry, not to the handler. Then `Run` checks the parameters and calls the handler.

When the handler returns, `Execute` attributes any undo step that appeared to the journal entry, so the activity log can say which command made which step. The entry is completed with the result, or suspended while the result is pending. Both the journal and the undo steps are the subject of their own pages: [undo](../editor/undo.md) and [the journal](../editor/journal.md).

### The schema check

Before the handler runs, `CheckParameters` compares the call with the schema. A parameter the schema does not declare is refused, and the message lists the ones the command accepts. A parameter in `required` that is missing is refused. Both refusals are `InvalidParameters`, and the handler never runs.

The reason is in a comment of the code: a parameter with a wrong name or a missing one must not silently change what a call means. If `{"nam": "Floor"}` were ignored, a rename would quietly do nothing. The check looks at names only, not at types or values. Types and ranges are checked when the handler reads its arguments, which is the job of the next helper.

### Reading arguments

`CommandArguments` reads parameters without throwing. Each `Get` call (`GetString`, `GetBool`, `GetInt` with a minimum and maximum, `GetEntity`, `GetEntities` and others) returns a value, and if something is wrong it records the problem. A later problem is ignored, so only the first is kept.

The handler reads all of its arguments, then asks `IsValid` once. If it is false, `Fail` returns the first problem as `InvalidParameters`. Collecting first means a handler has a single exit for bad input and cannot forget to check one parameter before using another.

`CommandUtils` adds what many handlers need. It builds schemas (`ObjectSchema`, `StringSchema`, `EntitySchema`), finds assets by handle or by path, and applies component values with the same validation the inspector uses, including the value ranges of reflection. An out-of-range value is `InvalidParameters`, and nothing changes. It also writes files for clients through `ResolveOutputPath`, which the rules below explain.

:::why
Engine code does not throw, but the `nlohmann::json` library that reads JSON can. `Run` wraps the schema check and the handler in a try block: an exception from the library becomes the `Internal` kind, with the command's name in the message. Everything else returns errors, as the [conventions](../core/conventions.md) page describes.
:::

### The rules and their reasons

Six rules follow from this design. The first three are rules of the engine's developer guide.

:::rule
A change to a scene or project is made by a command; continuous edits such as dragging a slider may use a transaction instead. Reason: a change that skips the registry has no description, no schema, no journal entry and no undo step, so agents and tests cannot see it. The checklist at the end of this page applies the rule.
:::

:::rule
A command rejects invalid input without side effects and records one undo step for each successful mutation. Reason: a call that fails halfway would leave a half-changed project that no client can detect, and two steps for one call would make a person press undo twice.
:::

:::rule
Code that writes component fields signals the change, for example with `MarkModified`. Reason: the scene caches transforms, names and more, and a silent write leaves the caches stale. The `entity.rename` command below shows it.
:::

The other three concern clients. The fourth covers files: one that a command writes for a client goes through `ResolveOutputPath`. Relative paths resolve against the project folder, and network paths, device paths and reserved names such as `CON` are refused. The extension must match, and an existing file is replaced only with `overwrite: true`. The reason is that the client chooses the path, and a client must not replace any file on the machine.

The fifth rule is that commands are written for agents. Every registered command is also a method of the automation server and a tool of the Model Context Protocol (MCP) server, which lets artificial intelligence agents call tools. An agent sees only the command's description and schema. So the description says what the command does and returns, and the schema is complete: a description on each property and a `required` list.

Identifiers are strings of 16 :term[hexadecimal]{id=hexadecimal} digits, assets are given by handle or by path, and results are JSON objects with `camelCase` keys. An image comes as `{"Image": {"MimeType": "...", "Data": "..."}}`. The pages on the [automation server](../automation/rpc-server.md) and [MCP](../automation/mcp.md) show what an agent receives.

The sixth rule: mark each command's kind, its session results, `MayDefer` and `WaitsForAssets` deliberately. The kind decides what a replay does with the command and whether it waits for the asset scan.

## A toy version

:::question
New to C++ classes, :term[lambdas]{id=lambda} and maps? Read [programming 3](../basics/programming-3.md) and [generic C++](../basics/cpp-generic.md) first.
:::

Before reading the real code, build the idea in a small program of its own. The toy has a registry with three commands (a rename, a count and an undo), a result with an error kind, the schema check by name, and a journal that only counts calls. Parameters are a map of strings instead of JSON, so the program needs no library. The program makes seven calls, and five of them fail, some by a wrong request and one by the editor's state. Look at `Run`: it holds the whole contract in under twenty lines.

```cpp sketch="editor-commands-toy.cpp"
#include <algorithm>
#include <charconv>
#include <cstdio>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <utility>
#include <vector>

namespace Toy
{

	using Parameters = std::map<std::string, std::string>;

	enum class ErrorKind { None, UnknownCommand, InvalidParameters, Failed };

	struct Result
	{
		bool Success = true;
		std::string Value;
		std::string Error;
		ErrorKind Kind = ErrorKind::None;

		static Result Ok(std::string value) { return { true, std::move(value), {}, ErrorKind::None }; }
		static Result Fail(std::string error, ErrorKind kind) { return { false, {}, std::move(error), kind }; }
	};

	struct Command
	{
		std::string Name;
		std::vector<std::string> Allowed;
		std::vector<std::string> Required;
		std::function<Result(const Parameters&)> Handler;
	};

	class Registry
	{
	public:
		void Register(Command command) { m_Commands[command.Name] = std::move(command); }

		Result Execute(const std::string& name, const Parameters& parameters)
		{
			Result result = Run(name, parameters);
			m_Journal.push_back(name + (result.Success ? " ok" : " failed"));
			return result;
		}

		const std::vector<std::string>& GetJournal() const { return m_Journal; }

	private:
		Result Run(const std::string& name, const Parameters& parameters)
		{
			auto found = m_Commands.find(name);
			if (found == m_Commands.end())
				return Result::Fail("Unknown command '" + name + "'", ErrorKind::UnknownCommand);
			const Command& command = found->second;
			for (const auto& [key, value] : parameters)
			{
				if (std::find(command.Allowed.begin(), command.Allowed.end(), key) == command.Allowed.end())
					return Result::Fail("Unknown parameter '" + key + "' for " + name, ErrorKind::InvalidParameters);
			}
			for (const std::string& key : command.Required)
			{
				if (!parameters.contains(key))
					return Result::Fail("Missing parameter '" + key + "' for " + name, ErrorKind::InvalidParameters);
			}
			return command.Handler(parameters);
		}

		std::map<std::string, Command> m_Commands;
		std::vector<std::string> m_Journal;
	};

}

int main()
{
	using namespace Toy;

	std::vector<std::string> names = { "Ground", "Crate" };
	std::vector<std::pair<size_t, std::string>> undoStack;
	Registry registry;

	registry.Register({ "entity.rename", { "index", "name" }, { "index", "name" }, [&](const Parameters& parameters)
	{
		size_t index = 0;
		const std::string& text = parameters.at("index");
		std::from_chars(text.data(), text.data() + text.size(), index);
		if (index >= names.size())
			return Result::Fail("Parameter 'index': no entity " + text, ErrorKind::InvalidParameters);
		undoStack.push_back({ index, names[index] });
		names[index] = parameters.at("name");
		return Result::Ok(names[index]);
	} });
	registry.Register({ "entity.count", {}, {}, [&](const Parameters&) { return Result::Ok(std::to_string(names.size())); } });
	registry.Register({ "edit.undo", {}, {}, [&](const Parameters&)
	{
		if (undoStack.empty())
			return Result::Fail("Nothing to undo", ErrorKind::Failed);
		names[undoStack.back().first] = undoStack.back().second;
		undoStack.pop_back();
		return Result::Ok("undone");
	} });

	const std::vector<std::pair<std::string, Parameters>> calls = {
		{ "entity.rename", { { "index", "0" }, { "name", "Floor" } } },
		{ "entity.rename", { { "index", "0" }, { "nam", "Floor" } } },
		{ "entity.rename", { { "index", "0" } } },
		{ "entity.rename", { { "index", "7" }, { "name", "Lamp" } } },
		{ "edit.undo", {} },
		{ "edit.undo", {} },
		{ "entity.fly", {} },
	};
	for (const auto& [name, parameters] : calls)
	{
		const Result result = registry.Execute(name, parameters);
		std::printf("%-14s %s  %s\n", name.c_str(), result.Success ? "OK  " : "FAIL", (result.Success ? result.Value : result.Error).c_str());
	}
	std::printf("journal: %zu entries, first '%s'\n", registry.GetJournal().size(), registry.GetJournal().front().c_str());
	std::printf("names: %s, %s\n", names[0].c_str(), names[1].c_str());
	return 0;
}
```

```text output-of="editor-commands-toy.cpp"
entity.rename  OK    Floor
entity.rename  FAIL  Unknown parameter 'nam' for entity.rename
entity.rename  FAIL  Missing parameter 'name' for entity.rename
entity.rename  FAIL  Parameter 'index': no entity 7
edit.undo      OK    undone
edit.undo      FAIL  Nothing to undo
entity.fly     FAIL  Unknown command 'entity.fly'
journal: 7 entries, first 'entity.rename ok'
names: Ground, Crate
```

1. **Lines 18–27:** `Result` carries success, a value, an error and its kind, as the real struct does.
2. **Lines 52–56:** `Run` finds the command first and answers `UnknownCommand` when there is none.
3. **Lines 58–67:** two loops, the schema check: a name the command does not allow, then a required name that is missing. Neither looks at a value.
4. **Line 68:** only now does the handler run.
5. **Lines 90–91:** the handler finds what the registry cannot: an entity that does not exist.

The first call renames entity 0 and the answer is the new name. The second writes `nam` instead of `name`: the registry refuses it before the handler runs, naming the parameter, so the handler never sees the wrong call. The third omits `name`, the fourth names an entity that does not exist, and that one is found by the handler, not by the registry: the registry knows names, the handler knows entities. The first `edit.undo` restores the name, and the second finds an empty stack and fails with the other kind, because nothing is wrong with the request. The last call names a command that does not exist.

The toy omits JSON, the schema types, the scan wait, the undo attribution and the deferred answers. The real code adds them, one at a time, in the order of the flow diagram.

## The real code

The result comes first. The struct holds the outcome of every call.

```cpp src="StrataEditor/src/Editor/EditorCommands.h#L44-L49"
struct EditorCommandResult
{
	bool Success = true;
	nlohmann::json Value; // Result data (null when the command returns nothing)
	std::string Error;
	EditorCommandError ErrorKind = EditorCommandError::None; // Set for failures
```

Success, a value and an error with its kind are what the toy had too. The real struct adds more fields: `Pending` for answers that come later, `ErrorData` for details a client can act on, and `JournalId`, which `Execute` completes. The factories keep call sites short: `Ok`, `Fail`, `InvalidParameters` and `Defer`.

Next is the command itself, with every mark as a decision.

```cpp src="StrataEditor/src/Editor/EditorCommands.h#L87-L105"
struct EditorCommand
{
	std::string Name;          // "<group>.<action>", e.g. "entity.create"
	std::string Description;   // One or two sentences for tool listings
	nlohmann::json Parameters; // JSON Schema of the parameter object
	EditorCommandHandler Handler;
	// Commands that do not change the project say so: an unmarked command counts as an edit, so a replay never misses
	// one.
	EditorCommandKind Kind = EditorCommandKind::Edit;
	// Queries whose results follow the editor's session (the selection, the journal, what is loaded) say so: replays
	// never bind the IDs those show.
	EditorCommandResults Results = EditorCommandResults::Content;
	// Commands that answer from the whole asset registry (asset, material, prefab queries; the export) say so: while the
	// project's assets are scanned in the background they wait for the scan, as every Edit command does
	// (EditorCommandRegistry::Execute). Session queries (editor.status, editor.wait, log.read) answer at once.
	bool WaitsForAssets = false;
	// The handler may answer later (EditorCommandResult::Defer: loads, builds, captures, waits): editor.batch refuses such
	// commands, which cannot finish within its frame, and Debug builds assert that an unmarked command never defers.
	bool MayDefer = false;
```

1. **Lines 89–92:** the name, the description for agents, the schema and the handler, the four parts every command has.
2. **Line 95:** the kind, `Edit` by default.
3. **Line 98:** the results mark, `Content` by default.
4. **Line 102:** `WaitsForAssets`, off by default.
5. **Line 105:** `MayDefer`, off by default.

The comments of the code say why each default is what it is. The kind defaults to Edit so that a replay never misses an edit, and the results default to content for the same reason. `MayDefer` is `false` because a command that may defer must say so: `editor.batch` refuses such commands, which cannot finish inside its frame.

Now the door, `Execute`. Read it against the flow diagram: the journal begins, the scan wait or `Run`, the assertion about deferring, the undo attribution, the journal's end.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L110-L156" symbol="EditorCommandRegistry::Execute"
EditorCommandResult EditorCommandRegistry::Execute(EditorContext& context, std::string_view name, const nlohmann::json& parameters,
	const CommandOrigin& origin) const
{
	// Command work shows in the frame profiler (editor.perf) instead of as untimed time; the stages of what a command runs
	// (a scene load's, the renderer's of a capture) nest in it and count for themselves.
	ST_PROFILE_STAGE("Editor.Commands");
	const EditorCommand* command = Find(name);
	CommandJournal& journal = context.GetJournal();
	const UndoStack& undo = context.GetUndoStack();
	journal.NoteEditsOutsideCommands(undo);
	const uint64_t entry = journal.Begin(origin, name, command ? command->Kind : EditorCommandKind::Query,
		command ? command->Results : EditorCommandResults::Content, parameters, context.IsPlaying());
	const uint64_t records = undo.GetRecordCount();
	EditorCommandResult result;
	if (command && context.IsWaitingForAssets() && WaitsForAssetScan(*command))
	{
		// The registry is still filling: the command runs once the scan ended (and goes on from there if it defers itself).
		// This deferral is the registry's, not the handler's, so it needs no MayDefer; what the handler answers then does.
		result = EditorCommandResult::Defer([this, command, name = std::string(name), parameters = nlohmann::json(parameters)](EditorContext& context)
			-> std::optional<EditorCommandResult>
		{
			if (context.IsWaitingForAssets())
				return std::nullopt;
			EditorCommandResult deferred = Run(context, command, name, parameters);
			ST_ASSERT(!deferred.IsPending() || command->MayDefer, "Command '{}' answered later (Defer) but is not registered with MayDefer", name);
			return deferred;
		});
	}
	else
	{
		result = Run(context, command, name, parameters);
		// The flag keeps editor.batch from starting what cannot finish in its frame: it must be right.
		ST_ASSERT(!result.IsPending() || !command || command->MayDefer, "Command '{}' answered later (Defer) but is not registered with MayDefer", name);
	}
	// A step the handler recorded (or extended) is the command's.
	journal.NoteUndo(entry, undo, records);
	result.JournalId = entry;
	if (result.IsPending())
	{
		journal.Suspend(entry);
	}
	else
	{
		journal.Complete(entry, result);
	}
	return result;
}
```

1. **Line 116:** the command is found; a missing one still gets a journal entry.
2. **Line 120:** the entry opens with the caller, the name and the parameters.
3. **Lines 124–137:** while assets are scanned, an `Edit` or `WaitsForAssets` command is deferred, and `Run` happens later.
4. **Line 140:** otherwise `Run` is called at once.
5. **Lines 145–154:** the new undo steps are attributed to the entry, which is then suspended or completed.

The registry's own wait takes the first branch. The assertion in the second branch fires in Debug builds when a command that is not marked `MayDefer` answers later, because `editor.batch` trusts the flag. The toy's journal counted calls; this one stores who called, with what parameters, and which undo records the call added.

`Run` and `CheckParameters` come next. They are the schema as contract.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L179-L199" symbol="EditorCommandRegistry::Run"
EditorCommandResult EditorCommandRegistry::Run(EditorContext& context, const EditorCommand* command, std::string_view name, const nlohmann::json& parameters) const
{
	if (!command)
		return EditorCommandResult::Fail(fmt::format("Unknown command '{}' (editor.commands lists them)", name), EditorCommandError::UnknownCommand);
	if (!parameters.is_object() && !parameters.is_null())
		return EditorCommandResult::InvalidParameters("Command parameters must be a JSON object");

	const nlohmann::json& arguments = parameters.is_null() ? nlohmann::json::object() : parameters;
	try
	{
		// The schema is the contract: a misspelled or missing parameter must not silently change the meaning.
		if (std::optional<std::string> problem = CheckParameters(*command, arguments))
			return EditorCommandResult::InvalidParameters(std::move(*problem));
		return command->Handler(context, arguments);
	}
	catch (const std::exception& exception)
	{
		// Engine code does not throw; this guards third-party code (JSON access) used by handlers.
		return EditorCommandResult::Fail(fmt::format("Command '{}' failed: {}", name, exception.what()), EditorCommandError::Internal);
	}
}
```

1. **Line 181:** an unknown name is refused first, with the kind `UnknownCommand`.
2. **Lines 187–192:** inside the try block the schema check runs, and only then the handler.
3. **Lines 194–198:** the catch turns a third-party exception into `Internal`.

A missing command and parameters that are not an object are refused first. The try block guards the schema check and the handler together, and the comment says why: the engine itself does not throw, so the catch is for third-party code.

```cpp src="StrataEditor/src/Editor/EditorCommands.cpp#L201-L226" symbol="EditorCommandRegistry::CheckParameters"
std::optional<std::string> EditorCommandRegistry::CheckParameters(const EditorCommand& command, const nlohmann::json& parameters)
{
	if (!parameters.is_object())
		return std::string("Command parameters must be a JSON object");
	if (const auto declared = command.Parameters.find("properties"); declared != command.Parameters.end() && declared->is_object())
	{
		for (const auto& [key, value] : parameters.items())
		{
			if (declared->contains(key))
				continue;
			std::string expected;
			for (const auto& [parameter, schema] : declared->items())
				expected += (expected.empty() ? "" : ", ") + parameter;
			return fmt::format("Unknown parameter '{}' for {} (parameters: {})", key, command.Name, expected.empty() ? "none" : expected);
		}
	}
	if (const auto required = command.Parameters.find("required"); required != command.Parameters.end() && required->is_array())
	{
		for (const nlohmann::json& parameter : *required)
		{
			if (parameter.is_string() && !parameters.contains(parameter.get<std::string>()))
				return fmt::format("Missing parameter '{}' for {}", parameter.get<std::string>(), command.Name);
		}
	}
	return std::nullopt;
}
```

1. **Line 214:** the message that refuses an unknown name and lists the accepted ones.
2. **Line 222:** the message that refuses a missing required name.

The loop over `parameters.items()` is the refusal of unknown names, and it builds the list of accepted ones for the message. The loop over `required` is the refusal of missing ones. Neither looks at a value.

The smallest complete command that changes something is `entity.rename`. Read the registration top to bottom: the description, the schema, the handler.

```cpp src="StrataEditor/src/Editor/Commands/EntityCommands.cpp#L514-L528"
registry.Register({ "entity.rename", "Renames an entity (undoable; while playing it changes the running copy only). Returns {entity, name}.",
	ObjectSchema({ { "entity", EntitySchema("Entity") }, { "name", StringSchema("New name") } }, { "entity", "name" }),
	[](EditorContext& context, const nlohmann::json& parameters)
	{
		Scene& scene = *context.GetActiveScene();
		CommandArguments arguments(parameters);
		Entity entity = arguments.GetEntity(scene, "entity");
		const std::string name = arguments.GetString("name");
		if (!arguments.IsValid())
			return arguments.Fail();
		SceneEditTransaction transaction(scene, fmt::format("Rename {} to {}", SceneEdit::QuoteName(entity.GetName()), SceneEdit::QuoteName(name)), { entity.GetUUID() });
		entity.GetComponent<NameComponent>().Name = name;
		entity.MarkModified<NameComponent>();
		return FinishEdit(context, transaction, { { "entity", UUIDToJson(entity.GetUUID()) }, { "name", name } });
	} });
```

1. **Lines 514–515:** the description tells an agent what comes back; the schema lists `entity` and `name` as required.
2. **Lines 520–523:** all arguments are read, then one check ends the call before anything changes.
3. **Line 524:** the transaction names the undo step and the entity it touches.
4. **Line 526:** `MarkModified` signals the write to the scene's caches.
5. **Line 527:** `FinishEdit` records the step and builds the answer.

The handler follows the pattern of every command that changes something. It reads all arguments first, so that bad input exits through `arguments.Fail()` before anything changes. Then it opens a transaction that names the step ("Rename 'Ground' to 'Floor'") and the entity it touches.

The write goes to the `NameComponent`, and `MarkModified` signals it, as the third rule demands. `FinishEdit` closes the transaction and returns the result. The [undo](../editor/undo.md) page teaches transactions; here it is enough to know that one successful call leaves one step.

`FinishEdit` itself does two more things worth knowing.

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

1. **Lines 437–441:** a scene that is still opening is read-only: the edit is undone and the call fails.
2. **Line 442:** the step is committed.
3. **Lines 443–449:** while the game plays, the answer carries a warning and the `RunningCopy` flag.

If the scene is read-only because it is still opening, the edit is rolled back and the call fails. In play mode the edit changes the running copy only, which `play.stop` discards, so the result carries a warning that says so and the result is flagged `RunningCopy`.

:::example
A call with a spelling mistake, traced through the real code. The caller sends `entity.rename` with `{"entity": "0123456789abcdef", "nam": "Floor"}`. `Execute` finds the command and opens a journal entry. The command is an `Edit`, so the registry checks whether the asset scan is running; suppose it is not.

`Run` calls `CheckParameters`. The schema declares `entity` and `name`, so the loop reaches `nam` and builds the message `Unknown parameter 'nam' for entity.rename (parameters: entity, name)`. `Run` returns `InvalidParameters` with that message. The handler never ran, so no transaction opened and no undo record was added. `Execute` completes the journal entry with the failure.
:::

## The command groups

The registry holds one command per operation, and the names group them by what they work on. The page about each area teaches its commands; the reference page [Commands](../reference/commands.md) lists every command with its parameters. The count is :value{key="commands.count"} at this version, and it changes, so do not memorize it. The editor's UI registers three commands of its own, `editor.showPanel`, `editor.showDialog` and `editor.screenshot`, because only the UI can open a window or take a picture of it. The rest come from the :term[editor core]{id=editor-core}, which runs without any UI.

| Group | What it is for | Where it is taught |
| --- | --- | --- |
| `scene.*` | Open, save and create scenes, load sub-scenes, recovery | [Scene graph](../world/scene-graph.md) |
| `entity.*` | Create, delete, rename, parent, find, copy and paste entities | Below, and [entities](../world/ecs.md) |
| `component.*` | Add, remove, get and set component values | [Reflection](../world/reflection.md) |
| `prefab.*` | Create prefabs, place instances, apply and revert | [Prefab instances](../editor/prefab-instances.md) |
| `asset.*` | Import, move, delete, place and inspect asset files | [Assets](../assets/what-is-an-asset.md) |
| `material.*` | Get, create and set materials | [Materials](../light/materials.md) |
| `project.*` | Create, open, export and configure projects | [Projects](../editor/projects.md) |
| `edit.*` | Undo, redo and read the history | [Undo](../editor/undo.md) |
| `editor.*` | Status, activity, waiting, profiling, batches and screenshots | [Journal](../editor/journal.md), [agents](../automation/agents.md) |
| `selection.*`, `log.read` | Read and set the selection, read the log | [Editor program](../editor/program.md) |
| `play.*` | Start, pause, step and stop the game | [Play mode](../editor/play-mode.md) |
| `input.*` | Simulated keys, mouse and gamepad | [Simulated input](../input/simulated.md), [automated playtests](../make/automated-playtests.md) |
| `camera.*`, `viewport.*` | Move the editor camera, change view settings, capture | [Camera and viewport](../editor/camera-viewport.md) |
| `script.*` | Build, reload and attach game scripts | [Script builds](../editor/script-builds.md) |
| `ui.*` | Create game UI, lay it out and test hits | [UI input](../ui/input.md) |
| `world.*`, `physics.*` | World streaming and physics diagnostics | [Worlds](../editor/worlds.md) |
| `animation.*`, `lighting.*`, `audio.state` | Animation, lighting tools, audio diagnostics | The page of each area |
| `preferences.*`, `inputActions.*`, `graphics.*` | The person's preferences, input actions, player graphics | The page of each area |

### The clipboard is three commands

The `entity.*` group holds the clipboard, and it shows how commands compose. `entity.copy` is a `Query`: it changes nothing and returns entity data under a :term[header]{id=header} that names the format, plus the copied roots and a count. Entities below another copied entity are copied with it, not twice.

`entity.paste` is an `Edit` that takes that data and makes new entities from it. Its optional `parent` and `index` choose where the copies go; the default is the top level, after the last child.

The paste gives the copies new IDs, since two entities cannot share one. References between copied entities are pointed at the copies, while references to entities outside the copy stay. That remapping is part of :term[serialization]{id=serialization}; see [World serialization](../world/serialization.md). A top-level copy whose name one of its new siblings already has receives a number, so `Crate` becomes `Crate (1)`.

Data that this build cannot read produces warnings in the result, not a failure. `entity.duplicate` does copy and paste in one step: it places each copy right after its original, in one undo step.

Because the clipboard is a pair of commands that exchange JSON, an agent can copy from one scene, open another, and paste there. A button could not offer that, and nothing special was written for it.

### Status providers

One more piece belongs here. The command `editor.status` answers the question every agent asks first: what state is the editor in? Its built-in sections come from the editor core, and the parts of the editor that own other information add more. A **status provider** is a function an owner registers with the editor context to produce one extra section of `editor.status`.

The automation server registers its own that way. A provider runs on the main thread, only when a client asks for its section or when the default answer includes its short form. The command itself is taught on the [agents](../automation/agents.md) page.

## Running a command from a terminal

`StrataCLI` is the command-line client of the editor. Its `call` verb runs one command in a running editor and prints the answer. A later page of this track tells you to run a command when a step has no menu or button; this is how.

```sh
StrataCLI call <command> [parameters] [--project <folder>] [--timeout <ms>]
```

The parameters are one JSON object. You can write it inline in quotes, read it from a file with `@file`, or pipe it in with `-` to read :term[standard input]{id=standard-input}. Quoting JSON on a :term[command line]{id=terminal-command} is error-prone, especially on Windows, so a file is the safest way. With no parameters the call sends an empty object.

A file saved with a :term[byte order]{id=endianness} mark is accepted; one saved as :term[UTF-16]{id=utf-8} is refused with a message that asks for UTF-8. Without `--project` the client picks the newest editor session it finds.

On success the answer prints to :term[standard output]{id=standard-output} as JSON with one field per line, and the :term[exit code]{id=exit-code} is 0. When the editor answers with an error, the client prints a JSON object with `code` and `message` to :term[standard error]{id=standard-error}, plus `data` when there is any, and exits with 1.

Exit code 2 means no editor could be reached. Code 3 is a misuse of the command line, 4 a timeout (the command may still be running), and 5 an image that the option `--save-image` could not save to a file.

Errors from the registry arrive as JSON-RPC codes: `UnknownCommand` is -32601, `InvalidParameters` is -32602 and carries the command's name and schema in `data`, `Failed` is -32005, `Cancelled` is -32006 and `Internal` is -32603. A client that gets -32602 can correct itself from the schema without another round trip.

:::example
Rename the entity `Ground` of a project made from the `basic3d` template, then make a mistake on purpose. The project is in `~/Games/Demo`, and the editor has it open. First find the ID, since `entity.rename` needs it.

```sh
StrataCLI call entity.find '{"name": "Ground"}' --project ~/Games/Demo
```

On Windows the shell may break the quotes, so write `{"name": "Ground"}` into a file `find.json` and pass `@find.json` instead. The answer is an object with an `entities` array that holds one ID, a string of 16 hexadecimal digits. Put that ID into a file `rename.json` next to you, with the new name:

```json
{ "entity": "<the ID from entity.find>", "name": "Floor" }
```

Run the command with the file.

```sh
StrataCLI call entity.rename @rename.json --project ~/Games/Demo
```

The answer is an object with the keys `entity` and `name`, and `name` reads `Floor`. In the editor the Hierarchy shows `Floor`. Now write the key wrongly, so that the file reads `"nam": "Floor"`, and run it again. The client prints the refusal on standard error and exits with 1:

```text
{
  "code": -32602,
  "message": "Unknown parameter 'nam' for entity.rename (parameters: entity, name)",
  "data": { "command": "entity.rename", "parameters": { "...": "the command's schema" } }
}
```

Nothing changed: no undo step was added, and the name is still `Floor`. The `data` object carries the schema, so the caller can see which parameters the command accepts.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Direct calls from each panel into editor classes | Small tools | Less code per feature | Agents and tests could not reach the feature; behaviour would differ by caller |
| Command objects only inside the process | Many editors with undo | Typed arguments, no JSON reading | No outside client; each command needs a way to become data later |
| An embedded scripting language that drives the editor | Editors with an extension language | Flexible automation | A large surface that can reach any state; no schema an agent can read |
| A separate remote interface next to the UI code | Servers with a management interface | Clean network design | Two interfaces to keep equal, which drift apart |
| Types generated from schemas | Projects with large interfaces | Compile-time checking of calls | A build step, and agents still need the schema at run time |

Strata's choice costs a schema written by hand and a description for each command, and some JSON reading in each handler. It buys one surface that people, agents, scripts and tests share, and that tells a client how to fix its request.

## How it is tested

The suite `Editor.Journal` in `StrataTests/src/Editor/CommandJournalTests.cpp` holds the decision about kinds. It lists every built-in command in exactly one of three lists: `Edit`, `Query` and `Session`. The test checks each command against its lists: the kind, the session results mark, `MayDefer` and `WaitsForAssets` must all match, and no list may name a command that the registry lacks. A new command therefore fails the test until its author decides its kind. The commands that the window adds are checked in the suite `Editor.UI.Dialogs`, because the test's registry does not hold them.

Other suites call commands as a client would, for example `StrataTests/src/Editor/AssetCommandTests.cpp`. Run some tests directly with a doctest filter:

```sh
build/windows/bin/Debug/StrataTests.exe --test-suite=Editor.Journal
```

The program prints a summary of the test cases and checks that ran, and it exits with a failure code when one check fails.

## Changing it safely

You extend the command layer by registering a command, never by calling lower code from a panel. The [command tutorial](../editor/tutorial-command.md) walks through adding one. The checks you pass before a commit follow from the rules above.

- Decide the kind and the flags, and add the name to the matching list of `CommandJournalTests.cpp`.
- Write the description for an agent and give every property a description, and a `required` list. A thin schema is the cheapest way to make an agent fail.
- Read all arguments through `CommandArguments` and exit with `Fail` before changing anything. Open a transaction only after the checks, and close it with `FinishEdit`.
- Signal every write to a component with `MarkModified` or `registry.patch`.
- A command from the UI passes `CommandOrigin { CommandSource::UI }`, so the journal credits the person.
- A command that may wait must return `Defer` and be registered with `MayDefer`; the page on [deferred commands](../editor/deferred-commands.md) teaches it.
- Files for clients go through `ResolveOutputPath`.

Test a refused call as well as a good one: the regression test for a refusal checks that the project is unchanged afterwards.

## Summary

- A command is a named operation with a description, a JSON Schema, a kind and flags; the registry runs it in a fixed order and every client shares it.
- You run one from a terminal with `StrataCLI call`, with parameters inline, from `@file` or from standard input, and the exit code tells how it ended.
- A call with an unknown or missing parameter is refused by `CheckParameters` inside `Run`, before the handler, as `InvalidParameters`.
- A new command decides its kind and flags, reads arguments with `CommandArguments`, changes nothing on failure and writes its description and schema for agents.

## Check yourself

1. A client sends `entity.rename` with a valid `entity` and a `name` of 5 while the schema says string. Which part of the call refuses it?

   - A. `CheckParameters`, because it checks types.
   - B. `CommandArguments` inside the handler, because the schema check looks at names only.
   - C. The journal, because it validates parameters.
   - D. Nothing refuses it; the name becomes `5`.

   :::answer{tests="command-contract"}
   B. `CheckParameters` compares names with `properties` and `required`, so A is wrong. The handler's `GetString` records a type error, and `arguments.Fail()` returns it as `InvalidParameters`. The journal only records the call, so C is wrong, and D is wrong because the handler checks the type.
   :::

2. `edit.undo` is called when nothing has been done. Which error kind comes back, and what may the client do?

   :::answer{tests="command-contract"}
   `Failed`. The request was valid, but the editor is in a state where it cannot be done. The client need not change the request; it can try again after something has been done. An `InvalidParameters` error would instead tell the client to change what it sent.
   :::

3. You run `StrataCLI call entity.rename @rename.json` and the shell shows exit code 1 and a JSON object with `-32602`. What does each part tell you?

   :::answer{tests="call-from-terminal"}
   Exit code 1 means the editor answered with an error, not that no editor was found (that would be 2). The code -32602 is `InvalidParameters`: your request is wrong, and `data` holds the command's schema so that you can correct it. The editor itself is fine.
   :::

4. A new command only reads the scene and returns the number of entities. Which kind and flags do you give it, and which test fails if you forget?

   :::answer{tests="write-for-agents"}
   The kind is `Query`: it changes nothing, and replays omit it. It needs no `MayDefer`, since it answers at once. A query that answers from the whole asset registry would also set `WaitsForAssets`; this one reads the scene only. If you state no kind it counts as an `Edit`, and the kinds test in `CommandJournalTests.cpp` fails until the name is in the `Query` list and the registration says so.
   :::

5. Two mistakes are in one call: `entity.rename` gets `nam` instead of `name`, and `entity` is missing. How many messages does the caller get, and which one?

   :::answer{tests="trace-refusal"}
   One message, the one for `nam`. In `CheckParameters` the loop over the call's parameters runs before the loop over `required`, and each loop returns at the first problem. The caller learns of the missing `entity` only after it fixes the name.
   :::

## Exercises

1. **Basic.** In the toy's output, say which of the seven calls the registry refuses before the handler runs, and which the handler refuses. Then say which function of the real code would refuse the fourth call.

   :::answer[Worked solution]{tests="command-contract"}
   The registry refuses the second, third and seventh calls: a wrong name, a missing name and an unknown command. The handler refuses the fourth, `index` 7, because only the handler knows which entities exist. The sixth call, the second undo, fails with the other kind: the request is fine and the state is not. In the real code the handler produces the error for the fourth call through `CommandArguments::GetEntity`, which records "no entity ... in the scene"; `CheckParameters` cannot know it, because it compares only names.
   :::

2. **Medium.** Trace it yourself. Start the editor in a debugger and put a breakpoint in `EditorCommandRegistry::Execute`. Call `entity.rename` from a terminal with an unknown parameter. Follow the call into `Run` and name the file, function and line that refuses it.

   :::answer[Worked solution]{tests="trace-refusal"}
   The breakpoint stops in `Execute` in `StrataEditor/src/Editor/EditorCommands.cpp`. Stepping over the scan check, you enter `Run`, then `CheckParameters`. The refusal is the `return fmt::format("Unknown parameter '{}' for {} ...` inside the loop over `parameters.items()`. `Run` wraps it with `InvalidParameters` and returns, so the `command->Handler` line is never reached.
   :::

3. **Hard.** An agent passes `entity` as the 16-digit string it got from `entity.find`. Write a function `IsEntityId` that accepts exactly 16 hexadecimal digits in either case and rejects everything else, including the all-zero string, and test it on six strings.

   :::answer[Worked solution]{tests="write-for-agents"}
   The function checks the length first, then each character against the three ranges, and last that some digit is not `0`. The all-zero rule is this exercise's own; the real reader reports `an ID (16 hexadecimal digits)` for what it does not accept.

   ```cpp sketch="editor-commands-id.cpp"
   #include <cstdio>
   #include <string_view>

   namespace Exercise
   {

   	// Exactly 16 hexadecimal digits, either case, and not all zeros.
   	bool IsEntityId(std::string_view text)
   	{
   		if (text.size() != 16)
   			return false;
   		bool anyNonZero = false;
   		for (const char c : text)
   		{
   			const bool digit = c >= '0' && c <= '9';
   			const bool lower = c >= 'a' && c <= 'f';
   			const bool upper = c >= 'A' && c <= 'F';
   			if (!digit && !lower && !upper)
   				return false;
   			if (c != '0')
   				anyNonZero = true;
   		}
   		return anyNonZero;
   	}

   }

   int main()
   {
   	const std::string_view samples[] = { "0123456789abcdef", "0123456789ABCDEF", "0000000000000000", "0123456789abcde", "0123456789abcdeg", "" };
   	for (const std::string_view sample : samples)
   		std::printf("'%.*s' -> %s\n", static_cast<int>(sample.size()), sample.data(), Exercise::IsEntityId(sample) ? "valid" : "refused");
   	return 0;
   }
   ```

   ```text output-of="editor-commands-id.cpp"
   '0123456789abcdef' -> valid
   '0123456789ABCDEF' -> valid
   '0000000000000000' -> refused
   '0123456789abcde' -> refused
   '0123456789abcdeg' -> refused
   '' -> refused
   ```

   1. **Lines 10–11:** a text that is not 16 characters long is refused at once.
   2. **Lines 15–19:** each character must be a digit or a letter from `a` to `f`, in either case.
   3. **Lines 20–23:** the string is valid only when some digit is not `0`.
   :::

## Where it lives in Strata

- `StrataEditor/src/Editor/EditorCommands.h` and `EditorCommands.cpp`: `EditorCommand`, `EditorCommandResult`, `EditorCommandRegistry` (`Execute`, `Run`, `CheckParameters`), `CommandArguments`.
- `StrataEditor/src/Editor/CommandUtils.h`: schema helpers, `FinishEdit`, `RollBackEdit`, `ResolveOutputPath`.
- `StrataEditor/src/Editor/Commands/EntityCommands.cpp`: `entity.rename`, `entity.copy`, `entity.paste`, `entity.duplicate`.
- `StrataEditor/src/EditorLayer.cpp`: the UI's three commands.
- `StrataCLI/src/CLI/CliApplication.cpp`: `call`, `@file`, the exit codes.
- Tests: `Editor.Journal` in `StrataTests/src/Editor/CommandJournalTests.cpp`.
- Commands: `editor.commands` lists the registry with each command's description, schema and kind.

## Further reading

- The command pattern, in any book on object-oriented design patterns: intermediate.
- The JSON Schema specification: what the keywords `properties` and `required` mean; intermediate.
- The JSON-RPC 2.0 specification: the error codes the registry's kinds map to; beginner.
