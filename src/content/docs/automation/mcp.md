---
id: automation/mcp
title: "StrataCLI and its MCP server"
description: "How StrataCLI reaches the editor from a terminal and, as an MCP server, offers its commands to a language model as tools, within a fixed budget."
kind: internals
size: L
tracks: [E]
needs: [automation/sessions]
time: 90
learn:
  - id: agent-view
    text: explain what an agent sees of a command, from its tool name and description to the shape of its result
  - id: toolset-budget
    text: find the toolset of a command and keep the default tool list within 32 tools and 30 KiB
  - id: read-cli
    text: trace a tool call and a call from a terminal through the code of StrataCLI, with the exit code each gives
since: 0.3.0
status: final
---

**StrataCLI** is the program that carries the editor's commands to clients that cannot speak the editor's own protocol. Such clients are a shell script, a test, or a program driven by a language model. It has two jobs. Run from a terminal, it connects to a running editor, sends one command and prints the answer.

Run as `StrataCLI mcp`, it becomes a server. A program built on a language model starts that server as a child process and talks to it through its standard streams. The server offers the editor's commands to that model as tools.

This page teaches how both jobs work, because both are small and a change to either must keep a few rules. [Sessions and discovery](../automation/sessions.md) covers how to find or launch an editor. [How the editor makes games with agents](../automation/agents.md) covers why tools for a model are designed as they are. StrataCLI is a client and a translator: it never runs a command itself, and it holds no scene.

## The problem and how engines solve it

A language model cannot press a button. It reads text and writes text, and a surrounding program lets it act by offering **tools**: each tool has a name, a sentence that says what it does and a description of its arguments. The model reads every definition before each answer, so every tool costs space in the model's limited memory. [How the editor makes games with agents](../automation/agents.md) explains that cost and how a model chooses.

Strata has well over a hundred operations: its editor commands (:value{key="commands.count"} at the pin, and a running editor adds more). Three ways to offer them are open. One tool per command gives the model the most direct view, but the bill grows with the catalogue.

Strata did this until 0.4.0. At 121 tools the definitions cost about 27,000 tokens (a token is a piece of a word, the unit in which a model reads and pays), close to the 128 tools that clients accept. If every definition cost the same, each would take about 223 tokens, and 32 of them about 7,100.

One generic tool, a `call` that takes a method name and an object, costs almost nothing. The model must then already know the names and arguments, and it gets no schema to check its guess against. The third way groups commands in **toolsets**. A few groups are listed as full tools while the rest stay available by name. Strata takes the third way, with the generic tool as the fallback.

## The map

The server sits between two worlds. On one side stands the **MCP client**, the program built on a language model (Claude Code, for example) that starts the server and asks it for tools. On the other side stands the editor, which serves its own requests on the :term[loopback]{id=loopback} address. StrataCLI translates between them, one line of :term[JSON]{id=json} at a time.

:::why
The editor could speak the Model Context Protocol itself. Strata keeps the two apart for a reason: a client starts a program and talks through its standard streams, while the editor listens on a port behind a token. StrataCLI is the one place where the first is turned into the second, and it can be tested without an editor.
:::

```mermaid caption="The path of a tool call. The client writes a line to the server's standard input. The server finds the command behind the tool name, sends it to the editor over a local network connection and writes the mapped answer to its standard output." alt="A diagram with four boxes from left to right: the MCP client, StrataCLI with its server and toolset table, the editor connection, and the editor. Arrows run from the client to StrataCLI over standard input and back over standard output, and from StrataCLI through the connection to the editor over a local network link. A launcher box starts the editor."
flowchart LR
  Client["MCP client"] -- "stdin: one JSON message per line" --> Main["main, RunCli"]
  Main -- "stdout: results and protocol" --> Client
  Main --> Server["McpServer"]
  Server --> Sets["McpToolsets"]
  Server --> Image["ImageOutput"]
  Server --> Conn["EditorConnection"]
  Conn -- "TCP, loopback" --> Editor["Editor: RpcServer"]
  Server -.-> Launcher["EditorLauncher"]
  Launcher -. "starts" .-> Editor
```

The files form two layers. `StrataCLI/src/Main.cpp` is a thin `main`. Everything else lives in the :term[static library]{id=static-library} `StrataCLILib`, so the tests link it and run the same code the :term[executable]{id=executable} runs. The library links only the `Network` layer of the engine: no :term[renderer]{id=renderer}, no scene, no assets.

Inside the library, `CliApplication` parses the arguments and runs the commands `call`, `list`, `status`, `launch` and `mcp`. `EditorConnection` and `EditorLauncher` find, pin and start an editor, exactly as [Sessions and discovery](../automation/sessions.md) describes; the commands typed in a terminal and the server share them. `McpServer` speaks the protocol. `McpToolsets` holds the tables that decide which commands become tools and shortens their definitions. `ImageOutput` decodes the images that captures return.

Two threads run in the server. The :term[main thread]{id=main-thread} handles messages and calls the editor. A reader thread, named `McpInput`, only reads lines from :term[standard input]{id=standard-input} and queues them. The reason shows in the real code below.

### The protocol in six messages

The **Model Context Protocol** (MCP) is a dialect of :term[JSON-RPC 2.0]{id=json-rpc-2-0} that lets a client discover and call the tools of a server. [JSON-RPC in Strata](../automation/json-rpc.md) teaches the request and answer format underneath. Over standard streams each message is one line of JSON.

A **server**, here and throughout, is a program that waits for requests and answers them. The MCP server is StrataCLI itself.

The conversation starts with `initialize`. The client names the protocol version it wants. Strata speaks three, 2024-11-05, 2025-03-26 and 2025-06-18, and answers any other request with the newest. The answer holds the chosen version, the capabilities (`tools` with `listChanged` set), the server's name and version, and `instructions`: a paragraph for the model that says to call `strata_status` first and how the tools work. The client may also pass `clientInfo.name`; the server passes it to the editor when it connects, so the editor shows who is connected.

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","clientInfo":{"name":"claude-code"}}}
```

The line above is what a client sends first. The client then sends the notification `notifications/initialized`, a message without an id that gets no answer. `ping` answers an empty object. `tools/list` returns the tools, and `tools/call` runs one with `name` and `arguments`. Any other method gets the standard "method not found" error, and a line that is not valid JSON gets the :term[standard error]{id=standard-error} for invalid JSON.

Two more message kinds appear later. The server sends `notifications/tools/list_changed` when its tool list changes, and `notifications/progress` while a long call runs, for a client that asked for it. A client may also send a batch, a :term[JSON array]{id=json-array} of messages, as the 2025-03-26 revision allowed; the server answers it with an array of answers, omitting those for notifications. Responses from the client are ignored, because the server never sends a request.

## The contract

What may a caller assume, and what must a change to this code keep? Five rules, each with its reason.

**Standard output carries only results and protocol; logs go to standard error; the streams are binary.** A client reads standard output line by line as JSON. One stray log line, or a line end that Windows turns into two :term[bytes]{id=byte}, breaks the message. `main` therefore switches the streams to binary mode before anything else, and the :term[logger]{id=logger} writes to standard error. Input lines may end in `\r`, which the server accepts.

:::rule
At most 32 tools and 30 KiB by default, and a command added to `core` takes another command's place. Clients cap the number of tools and charge tokens for every definition ([Automation rules](../automation/agents.md)). The test `CLI.McpToolsets` fails when the default list grows past either limit.
:::

The default list is the **core toolset** plus the generic tools. The core toolset is the group of commands listed as tools when nobody asks for more; :value{key="toolsets.core.count"} commands at the pin.

The **generic tools** are the five that the server always lists: `strata_status`, `strata_launch_editor`, `strata_describe`, `strata_toolsets` and `strata_call`. A sixth, `strata_list_methods`, answers a call by name but is not listed. Together that is 32, the limit, so no new generic tool fits without removing one, and a new core command must displace one.

**The first sentence of a command's description says what the command does.** The compact definition keeps only that sentence (below), so a description that opens with background hides the purpose from the model, which then guesses from the name.

**A timeout of StrataCLI, exit code 4, does not mean the command failed.** StrataCLI stopped waiting, and the editor may still be running the command. Never start another editor because of it: two editors would work on the same project folder and its files. Read the state first, then decide.

**A tool name belongs to one method.** A tool name is the method name with every character outside letters, digits, `_` and `-` replaced by `_`, cut to 64 characters. If two methods give the same name, or a method gives a name that a generic tool owns, the server does not list the later one and logs a warning. Call it with `strata_call` instead.

## A toy version

Before the real code, a small server that shows the whole job: it reads one JSON message per line, lists two commands as tools and calls them. It is a complete program that reads its input from a list in `main`, with hand-made JSON handling so that it stays short. It cannot read arbitrary JSON; the real server uses a library.

```cpp sketch="automation-mcp-toy.cpp"
// A toy MCP server: one JSON message per line in, one per line out. It lists two commands as tools and calls them.
#include <iostream>
#include <string>
#include <vector>

struct Command
{
	std::string Name;
	std::string Description;
};

static const std::vector<Command> s_Commands = {
	{ "entity.create", "Creates an entity. Returns its ID." },
	{ "scene.save", "Writes the open scene to its file." } };

// Characters outside letters, digits, "_" and "-" become "_": entity.create becomes entity_create.
std::string MakeToolName(const std::string& method)
{
	std::string name;
	for (char character : method)
	{
		const bool valid = (character >= 'a' && character <= 'z') || (character >= 'A' && character <= 'Z')
			|| (character >= '0' && character <= '9') || character == '_' || character == '-';
		name.push_back(valid ? character : '_');
	}
	return name;
}

std::string FirstSentence(const std::string& text)
{
	const size_t end = text.find(". ");
	return end == std::string::npos ? text : text.substr(0, end + 1);
}

// The text of a field of one flat message: a quoted string, or a number up to the next "," or "}".
std::string ReadField(const std::string& line, const std::string& key)
{
	const size_t at = line.find("\"" + key + "\":");
	if (at == std::string::npos)
		return {};
	size_t start = at + key.size() + 3;
	const bool quoted = line[start] == '"';
	if (quoted)
		start++;
	const size_t end = line.find_first_of(quoted ? "\"" : ",}", start);
	return line.substr(start, end - start);
}

std::string Reply(const std::string& id, const std::string& result)
{
	return "{\"jsonrpc\":\"2.0\",\"id\":" + id + ",\"result\":" + result + "}";
}

std::string HandleLine(const std::string& line)
{
	const std::string method = ReadField(line, "method");
	const std::string id = ReadField(line, "id");
	if (id.empty())
		return {}; // A notification has no id and gets no answer.
	if (method == "initialize")
		return Reply(id, "{\"protocolVersion\":\"2025-06-18\",\"capabilities\":{\"tools\":{}},\"serverInfo\":{\"name\":\"toy\"}}");
	if (method == "tools/list")
	{
		std::string tools;
		for (const Command& command : s_Commands)
		{
			tools += std::string(tools.empty() ? "" : ",") + "{\"name\":\"" + MakeToolName(command.Name) + "\",\"description\":\""
				+ FirstSentence(command.Description) + "\",\"inputSchema\":{\"type\":\"object\"}}";
		}
		return Reply(id, "{\"tools\":[" + tools + "]}");
	}
	if (method == "tools/call")
	{
		const std::string name = ReadField(line, "name");
		for (const Command& command : s_Commands)
		{
			if (MakeToolName(command.Name) == name)
				return Reply(id, "{\"content\":[{\"type\":\"text\",\"text\":\"ran " + command.Name + "\"}],\"isError\":false}");
		}
		return Reply(id, "{\"content\":[{\"type\":\"text\",\"text\":\"Unknown tool " + name + "\"}],\"isError\":true}");
	}
	return "{\"jsonrpc\":\"2.0\",\"id\":" + id + ",\"error\":{\"code\":-32601,\"message\":\"Method not found\"}}";
}

int main()
{
	const std::vector<std::string> input = {
		R"({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}})",
		R"({"jsonrpc":"2.0","method":"notifications/initialized"})",
		R"({"jsonrpc":"2.0","id":2,"method":"tools/list"})",
		R"({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"entity_create","arguments":{}}})",
		R"({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"scene_load","arguments":{}}})" };
	for (const std::string& line : input)
	{
		const std::string answer = HandleLine(line);
		if (!answer.empty())
			std::cout << answer << "\n";
	}
	return 0;
}
```

```text output-of="automation-mcp-toy.cpp"
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{}},"serverInfo":{"name":"toy"}}}
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"entity_create","description":"Creates an entity.","inputSchema":{"type":"object"}},{"name":"scene_save","description":"Writes the open scene to its file.","inputSchema":{"type":"object"}}]}}
{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"ran entity.create"}],"isError":false}}
{"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"Unknown tool scene_load"}],"isError":true}}
```

1. **Line 17:** the name rule, so that `entity.create` becomes `entity_create`.
2. **Line 36:** hand-made reading of one field of a flat message; the real server uses a JSON library.
3. **Line 58:** a message without an id is a notification and gets no answer.
4. **Line 68:** the list shows only the first sentence of each description.
5. **Line 80:** an unknown tool is a result with `isError` true, not a protocol error.

The program shows four ideas. The `initialized` notification gets no answer, because it has no id. `MakeToolName` turns `entity.create` into `entity_create`, because tool names may not hold a dot. The tool list shows only the first sentence of each description. An unknown tool is an ordinary answer with `isError` set, not a protocol error, so the model reads the problem and can react.

The toy omits almost everything that makes the real server useful: the editor connection, toolsets, structured results, images, progress and a clock for idle work. The next section takes them in the order of the data flow.

## The real code

### Startup: main and the build

A process starts in `main`. The excerpt shows what happens before any command runs.

```cpp src="StrataCLI/src/Main.cpp#L11-L28" symbol="main"
int main(int argc, char** argv)
{
	// stdout/stdin carry machine-readable output and the MCP protocol: no newline translation. Input lines may then
	// end in "\r", which the MCP server tolerates.
	Strata::Platform::SetBinaryStandardStreams();

	std::vector<std::string> arguments;
	for (int index = 1; index < argc; index++)
		arguments.emplace_back(argv[index] ? argv[index] : "");

	const bool verbose = std::find(arguments.begin(), arguments.end(), "--verbose") != arguments.end();
	Strata::CLI::InitializeCliLogging(verbose);

	const int exitCode = Strata::CLI::RunCli(arguments, std::cin, std::cout, std::cerr);
	std::cout.flush();
	Strata::Log::Shutdown();
	return exitCode;
}
```

1. **Line 15:** the streams become binary before anything is read or written.
2. **Lines 21-22:** logging goes to standard error, with trace detail only for `--verbose`.
3. **Line 24:** `RunCli` receives the three streams it may use, so tests call it with string streams.
4. **Lines 25-26:** the output is flushed before the logger shuts down.

The next excerpt is the build file that keeps `main` this small.

```cmake src="StrataCLI/CMakeLists.txt#L6-L18"
file(GLOB_RECURSE STRATA_CLI_SOURCES CONFIGURE_DEPENDS
	"${CMAKE_CURRENT_SOURCE_DIR}/src/CLI/*.h"
	"${CMAKE_CURRENT_SOURCE_DIR}/src/CLI/*.cpp")

add_library(StrataCLILib STATIC ${STRATA_CLI_SOURCES})
strata_configure_target(StrataCLILib)
source_group(TREE "${CMAKE_CURRENT_SOURCE_DIR}/src" FILES ${STRATA_CLI_SOURCES})
target_include_directories(StrataCLILib PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/src")
# The CLI is a network client of the editor: Core and Network only, nothing of the engine's runtime.
target_link_libraries(StrataCLILib PUBLIC Strata::Network)

add_executable(StrataCLI "${CMAKE_CURRENT_SOURCE_DIR}/src/Main.cpp")
strata_configure_target(StrataCLI)
```

1. **Line 10:** all sources of the program are one static library.
2. **Line 15:** the library links the `Network` layer and nothing else of the engine.
3. **Lines 17-18:** the executable is one file linked against the library.

The comment in the file says all logic lives in `StrataCLILib`. The library links `Strata::Network` and nothing else of the engine, which keeps the program small and keeps the engine's layers honest: a command-line client has no business including the renderer. The executable is one :term[source file]{id=source-file} plus the library.

### What the model sees: names, schemas and results

Three small functions turn an editor method into a tool. `MakeToolName` is the replacement rule above. `MakeToolInputSchema` takes the method's parameter schema and makes sure it is an object schema, because MCP demands `"type": "object"` for tool arguments; a method with no schema, or a non-object schema, gets an empty object schema. The third, `MakeToolResult`, deserves a closer look, since it decides what the model reads.

```cpp src="StrataCLI/src/CLI/McpServer.cpp#L210-L254" symbol="MakeToolResult"
nlohmann::json MakeToolResult(const RpcResult& result)
{
	if (result.IsError())
	{
		const RpcError& error = result.GetError();
		std::string text = fmt::format("Error {}: {}", error.Code, error.Message);
		if (!error.Data.is_null())
			text += "\n" + PrettyPrint(error.Data);
		return MakeToolError(text);
	}

	const nlohmann::json& value = result.GetValue();
	nlohmann::json content = nlohmann::json::array();
	nlohmann::json toolResult = nlohmann::json::object();
	if (!value.is_object())
	{
		content.push_back(MakeTextContent(PrettyPrint(value)));
		toolResult["content"] = std::move(content);
		toolResult["isError"] = false;
		return toolResult;
	}

	// Methods return images (e.g. viewport captures) as {"Image": {"MimeType", "Data" (base64)}}. They become
	// image content; the remaining fields are the text and structured content, without the large payload.
	nlohmann::json remaining = value;
	std::optional<nlohmann::json> image;
	if (const auto imageField = remaining.find("Image"); imageField != remaining.end() && imageField->is_object())
	{
		const auto mimeType = imageField->find("MimeType");
		const auto data = imageField->find("Data");
		if (mimeType != imageField->end() && mimeType->is_string() && data != imageField->end() && data->is_string())
		{
			image = nlohmann::json { { "type", "image" }, { "data", *data }, { "mimeType", *mimeType } };
			remaining.erase(imageField);
		}
	}

	content.push_back(MakeTextContent(PrettyPrint(remaining)));
	if (image)
		content.push_back(std::move(*image));
	toolResult["content"] = std::move(content);
	toolResult["structuredContent"] = std::move(remaining);
	toolResult["isError"] = false;
	return toolResult;
}
```

1. **Lines 212-219:** an error becomes text with the code, the message and the error's data.
2. **Lines 224-230:** a result that is not an object becomes plain text.
3. **Lines 236-245:** an `Image` field with a string `MimeType` and `Data` moves out into image content.
4. **Lines 247-249:** the text comes first and the picture second.
5. **Line 251:** the remaining object also travels as `structuredContent`.

An error becomes a tool result with `isError` true, not a JSON-RPC error. The text carries the code, the message and the error's data, so the model sees why a command failed and can correct itself. A protocol error would reach the client's code instead, where the model might never see it.

A result that is not an object becomes plain text. An object becomes text plus a copy in **`structuredContent`** (the MCP field that carries a tool's result as JSON beside its text), for clients that read data instead of prose.

The `Image` field is the exception. A capture returns `{"Image": {"MimeType", "Data"}}`, and the function turns it into image content, a separate item in the list. The model then sees the picture itself, and the large :term[base64]{id=base64} string stays out of both the text and `structuredContent`. An `Image` field that lacks a string `MimeType` or `Data` stays in the text, and a test covers that case.

### Which commands become tools

`McpToolsets.cpp` holds the tables. Three constant arrays decide where a command belongs: `c_CoreCommands`, then `c_ExactToolsets`, then `c_PrefixToolsets`. Core is a list of names. The other toolsets go by prefix: `scene.`, `entity.`, `component.`, `prefab.`, `selection.`, `edit.` and `lighting.` all map to `scene`. A command can sit in two toolsets at once: `entity.create` is in `core` and in `scene`, so enabling `scene` adds the commands of the group that core omits.

```cpp src="StrataCLI/src/CLI/McpToolsets.cpp#L123-L137" symbol="McpToolsets::GetGroupToolset"
std::string GetGroupToolset(std::string_view method)
{
	for (const auto& [name, toolset] : c_ExactToolsets)
	{
		if (method == name)
			return std::string(toolset);
	}
	for (const auto& [prefix, toolset] : c_PrefixToolsets)
	{
		if (method.starts_with(prefix))
			return std::string(toolset);
	}
	const size_t dot = method.find('.');
	return std::string(dot == std::string_view::npos ? method : method.substr(0, dot));
}
```

1. **Lines 125-129:** exact names win over prefixes.
2. **Lines 130-134:** the first prefix that matches decides.
3. **Lines 135-136:** a group that no table knows names its own toolset.

The function checks the exact names first. The command `asset.place` is an asset command by prefix but belongs with the scene, because it puts things in a scene. The command `editor.perf` has its own toolset `perf`, and the project commands that save settings go to `settings`, not `assets`. Only then does the function try the prefixes.

A group that no table knows is not an error. The group becomes a toolset named after itself, so a new command group works at once and is listed only when the client asks for it: `weather.set` lands in `weather`. The budget test still asks for a table entry, so a real group goes into the table.

The table makes thirteen toolsets (`toolsets.count` is :value{key="toolsets.count"}), each with a one-line description that `strata_describe` shows. The test "Commands map to toolsets by exact name, then by group" holds the table's behavior. Another test in `CLI.McpToolsets` talks to a fake editor with the real :term[command registry]{id=command-registry} and checks that every command lands in a toolset the table names.

### Compact definitions

A tool definition has a description and a schema full of property descriptions. Most of the cost is text the model rarely needs. A **compact definition** is a tool definition cut down to the first sentence of its description and of each property's description, with the schema's structure (types, enums, ranges, required fields) kept whole. `strata_describe` returns the full text on demand.

```cpp src="StrataCLI/src/CLI/McpToolsets.cpp#L153-L173" symbol="McpToolsets::FirstSentence"
std::string FirstSentence(std::string_view text, size_t maxLength, bool* outCut)
{
	const size_t end = FindSentenceEnd(text);
	std::string_view sentence = text.substr(0, end);
	if (outCut)
		*outCut = end < text.size() || sentence.size() > maxLength;
	if (sentence.size() <= maxLength)
		return std::string(sentence);
	if (maxLength == 0)
		return {};
	// Cut at the last space that leaves room for the ellipsis, else in the middle of the word (never inside a UTF-8
	// sequence).
	size_t length = sentence.rfind(' ', maxLength - 1);
	if (length == std::string_view::npos || length == 0)
	{
		length = maxLength - 1;
		while (length > 0 && (static_cast<unsigned char>(sentence[length]) & 0xC0) == 0x80)
			length--;
	}
	return std::string(sentence.substr(0, length)) + "\xE2\x80\xA6"; // An ellipsis: the rest is in strata_describe
}
```

1. **Line 155:** `FindSentenceEnd` (not shown) searches for a full stop followed by a space, and skips a full stop that ends a short form of a word.
2. **Line 158:** `outCut` tells the caller whether anything was omitted.
3. **Line 165:** the cut falls at the last space that leaves room for the ellipsis.
4. **Lines 168-170:** without a space the cut falls inside the word, and steps back over :term[UTF-8 continuation bytes]{id=utf-8-continuation-byte}.
5. **Line 172:** one ellipsis character marks the cut.

A word never breaks in the middle if a space exists. If none exists, the function cuts inside the word, and steps back while the byte it stands on is a :term[UTF-8 continuation byte]{id=utf-8-continuation-byte} (the form 10xxxxxx), so the cut never lands inside a character. The limits are 160 characters for a description and 100 for a property.

`MakeCompactToolDefinition` calls it, and adds the text " (details: strata_describe)" when anything was omitted. The note tells the model where to read more. Property descriptions are cut the same way, also inside nested objects and array items.

### The stream runner

`RunMcpServer` connects standard input to the server. Reading a line blocks, and the server must also do work while the client is silent: connect again to an editor that restarted, notice that a launched editor exited, and announce a changed tool list. One thread cannot do both with a plain `getline`.

```cpp src="StrataCLI/src/CLI/McpServer.cpp#L860-L916" symbol="RunMcpServer"
void RunMcpServer(McpServer& server, std::istream& input, std::chrono::milliseconds tickInterval)
{
	struct InputQueue
	{
		std::mutex Mutex;
		std::condition_variable Condition;
		std::deque<std::string> Lines;
		bool Finished = false;
	};

	InputQueue queue;
	std::thread reader([&queue, &input]()
	{
		Platform::SetCurrentThreadName("McpInput");
		std::string line;
		while (std::getline(input, line))
		{
			{
				std::scoped_lock<std::mutex> lock(queue.Mutex);
				queue.Lines.push_back(std::move(line));
			}
			queue.Condition.notify_one();
			line.clear();
		}

		{
			std::scoped_lock<std::mutex> lock(queue.Mutex);
			queue.Finished = true;
		}
		queue.Condition.notify_one();
	});

	auto nextTick = std::chrono::steady_clock::now() + tickInterval;
	while (true)
	{
		std::deque<std::string> lines;
		bool finished = false;
		{
			std::unique_lock<std::mutex> lock(queue.Mutex);
			queue.Condition.wait_until(lock, nextTick, [&queue]() { return !queue.Lines.empty() || queue.Finished; });
			lines.swap(queue.Lines);
			finished = queue.Finished;
		}

		for (const std::string& line : lines)
			server.HandleLine(line);
		if (finished && lines.empty())
			break;

		if (std::chrono::steady_clock::now() >= nextTick)
		{
			server.Tick();
			nextTick = std::chrono::steady_clock::now() + tickInterval;
		}
	}
	reader.join();
}
```

1. **Lines 862-868:** the queue holds the :term[mutex]{id=mutex}, the :term[condition variable]{id=condition-variable}, the lines and a flag for the end of input.
2. **Lines 871-890:** the reader thread only moves lines into the queue and wakes the loop.
3. **Line 899:** `wait_until` ends at the next tick, a new line or the end of input.
4. **Lines 904-907:** the loop handles the queued lines in order and stops when input ended and nothing is left.
5. **Lines 909-913:** when the time has come, `Tick` runs and the next tick is set.

The reader thread reads lines and pushes them into a queue under a :term[mutex]{id=mutex}. The :term[main loop]{id=game-loop} waits on a :term[condition variable]{id=condition-variable} until either a line arrives, the input ends or the next tick is due. `wait_until` takes the tick time, so the wait ends by itself every two seconds when nothing happens. When the input has ended and the queue is empty, the loop stops, and the reader is joined. A client that closes its end therefore stops the server.

Everything that touches the editor connection happens on the main thread, so the server needs no lock of its own. That is why its class comment says it is not thread-safe, and why the queue is the only shared object.

### From a tool call to the editor

Everything the model asks arrives as `tools/call`. The generic tools are matched by name first. Any other name is found in `m_ToolToMethod`, the table that `RefreshEditorState` builds from the editor's method list.

```cpp src="StrataCLI/src/CLI/McpServer.cpp#L476-L492" from="auto method = m_ToolToMethod.find(name);" to="return MakeToolResult(result);" symbol="McpServer::HandleToolsCall"
auto method = m_ToolToMethod.find(name);
if (method == m_ToolToMethod.end() || !m_Connection.IsConnected())
{
	RefreshEditorState();
	method = m_ToolToMethod.find(name);
}
if (method == m_ToolToMethod.end())
{
	if (!m_Connection.IsConnected())
		return MakeToolError(fmt::format("Unknown tool '{}': no Strata editor is connected ({}). Use strata_launch_editor to start one.", name, m_Connection.GetLastError()));
	return MakeToolError(fmt::format("Unknown tool '{}'", name));
}

const RpcResult result = m_Connection.Call(method->second, arguments, m_Specification.CallTimeout);
if (!m_Connection.IsConnected())
	RefreshEditorState(); // The editor went away; drop its tools (announced after the response)
return MakeToolResult(result);
```

1. **Lines 476-481:** the lookup, with one refresh of the editor's method list when the name is unknown or the connection is down.
2. **Lines 482-487:** a name that is still unknown becomes an error result, with a different text when no editor is connected.
3. **Line 489:** the call goes to the editor with the server's timeout.
4. **Lines 490-492:** after a lost connection the tools are dropped, and the result is mapped.

The lookup does not check the enabled toolsets. That check happens only when the list is built (`BuildEditorTools`), so a command outside the enabled toolsets still answers when a client calls its tool by name. If the name is unknown, or no editor is connected, the server refreshes its state once and looks again, because an editor may have started since the last refresh. A name that is still unknown becomes an error result: one text for "no editor connected", another for a plain unknown tool. After the call, a lost connection drops the tools, and the change is announced after the response.

The announcement is the notification **`tools/list_changed`** (the MCP message that tells a client to ask for `tools/list` again). `HandleLine` calls `AnnounceToolChanges` after every message, and `Tick` calls it too. The function builds the current editor tools, compares their text form with what the client last saw and sends the notice only if they differ. Enabling a toolset, an editor that connects and an editor that disappears all use this one path.

### Launching and progress

`strata_launch_editor` takes `project`, `headless` and `noGpu`. It takes an editor that already has the project open, or, without a project, an empty editor this server started with the same options. Otherwise it launches one with `--idle-timeout 600`, so an editor that the agent forgot closes after ten minutes without a client, and the server stays connected while it runs.

The call answers when the project is ready, which can take minutes for a large project.

A client that wants to know how far along it is puts a **progress token** in the call's `_meta`. The token is a value the client chooses, which the server echoes in each `notifications/progress` message so the client can match it to the call.

The server turns the launcher's steps into one percentage: registering assets fills 0 to 50, applying them 50 to 90, and opening the start scene 90 to 100. A percentage that is not higher than the last one is not sent, because MCP progress only rises.

### Around the server: the commands of a terminal

The :term[terminal commands]{id=terminal-command} use the same connection. `call <method> [params]` takes its parameters inline, from standard input with `-`, or from a file with `@file`. The last two avoid the quoting trouble of JSON on a command line, especially on Windows.

`list` prints the methods, and `list --json` adds their schemas. `status` shows whether an editor answers and which sessions exist. `launch` starts an editor and prints progress lines to standard error, so standard output stays the session's description. The token never appears in that description.

The :term[exit codes]{id=exit-code} tell a script what happened without reading text.

| Code | Meaning |
| --- | --- |
| 0 | The command worked |
| 1 | The editor refused or failed the command |
| 2 | No editor answered, the link broke, or the launch failed |
| 3 | The arguments were wrong |
| 4 | No answer came within `--timeout` (30,000 ms by default); the command may still run |
| 5 | An answer came, but `--save-image` could not write the file |

The mapping from an error to a code is a few lines.

```cpp src="StrataCLI/src/CLI/CliApplication.cpp#L102-L114" symbol="ReportCallFailure"
int ReportCallFailure(const RpcResult& result, std::ostream& errorOutput)
{
	const RpcError& error = result.GetError();
	nlohmann::json description = nlohmann::json { { "code", error.Code }, { "message", error.Message } };
	if (!error.Data.is_null())
		description["data"] = error.Data;
	errorOutput << PrettyPrint(description) << "\n";

	// A timeout is not a lost editor: the command may still be running, and starting another editor would be wrong.
	if (error.Code == JsonRpc::ErrorCode::Timeout)
		return ExitCode::Timeout;
	return error.Code == JsonRpc::ErrorCode::ConnectionClosed ? ExitCode::ConnectionFailure : ExitCode::RpcError;
}
```

1. **Line 108:** the error goes to standard error as JSON with code, message and data.
2. **Lines 111-112:** a timeout gives exit 4, because the editor may still run the command.
3. **Line 113:** a closed connection gives exit 2, and any other error gives exit 1.

The function prints the error as JSON on standard error. A timeout code gives exit 4 and a closed connection gives exit 2; any other error, which means the editor itself refused or failed the command, gives exit 1. The MCP server has no such split: all three arrive as an `isError` text, because a model reads text and not exit codes.

```mermaid caption="One failing call as each client sees it. The editor's error code decides the exit code of a terminal call, while the server turns every error into the same kind of text result." alt="A flow from the error of a call to two outcomes. For a terminal call a timeout gives exit code 4, a closed connection gives exit code 2 and any other error gives exit code 1. For the server every error becomes a tool result whose error flag is true and whose text starts with the word Error, the code and the message."
flowchart LR
  E["Error of a call"] --> T{"Code"}
  T -- "Timeout" --> X4["CLI: exit 4"]
  T -- "ConnectionClosed" --> X2["CLI: exit 2"]
  T -- "any other" --> X1["CLI: exit 1"]
  E --> M["MCP: isError true, text with code, message and data"]
```

With `--save-image`, `call` writes an image result to a file. `SaveResultImage` decodes the base64 and replaces the large `Data` field with `{"File", "Size"}`, so the printed result stays short. Each base64 digit is one of 64 characters, A to Z, a to z, 0 to 9, + and /, worth 0 to 63 in that order, so it carries six bits. Four digits give three bytes, and two or three digits at the end give one or two.

The decoder is strict. It accepts the standard alphabet and ignores spaces and line ends. Padding is optional, may only stand at the end and may only complete a group of four; any other character, or a lone leftover digit, is an error.

A saved picture must be the picture that the editor sent. A corrupt one fails with exit 5 instead of leaving a broken file.

:::example[A session, from the client and from a terminal]
Say you add the server to Claude Code with `claude mcp add strata -- StrataCLI mcp`. The client starts the program and sends `initialize`. With no editor connected, `tools/list` holds only the five generic tools, a fact that the test "Only the generic tools are listed without an editor" checks. The model calls `strata_status`, then `strata_launch_editor` with a project. Now the list holds 5 generic tools and :value{key="toolsets.core.count"} core commands: 32 tools.

The model creates an entity with this call.

```json
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"entity_create","arguments":{"name":"Crate"}}}
```

The server finds `entity_create` in `m_ToolToMethod`, calls `entity.create` on the editor and gets `{"id": "<16 hexadecimal digits>"}`. `MakeToolResult` answers with text content, the same object as `structuredContent` and `isError` false. In the tool list, the description of `entity_create` was the first sentence of the command's text, 124 characters long, plus the 27-character note " (details: strata_describe)". The note appears because the full text continues after that sentence.

A capture works the same way. The model calls `viewport_capture`. The editor answers with a PNG in the `Data` field of `Image`, with `width` and `height` beside it. `MakeToolResult` puts the text and a second item of type `image` into `content`, so the model sees the picture.

The model needs a scene command that core lacks, say `entity.rename`. It calls `strata_toolsets` with `{"enable": ["scene"]}`. The answer lists `["core", "scene"]` and the new count of editor tools. After the answer, the server sends `notifications/tools/list_changed`, and the client asks for `tools/list` again. Had the model skipped that step, `strata_call` with `{"method": "entity.rename"}` would also have worked.

From a terminal the same work reads as follows. Each line ends with the exit code it gives.

```sh
StrataCLI call entity.create '{"name":"Crate"}'     # 0, prints {"id": ...}
StrataCLI call viewport.capture --save-image a.png  # 0, Data replaced by File and Size
StrataCLI call entity.makeCoffee                    # 1, an unknown method: error JSON on stderr
StrataCLI call viewport.capture --timeout 50        # 4 if the capture takes longer
StrataCLI status                                    # 2 when no editor is reachable
```

The last two lines show why the codes exist, and the fourth shows the rule. A script that sees 4 must not launch another editor. It asks `status`, or waits. The editor finishes the command either way.
:::

## What the server does not do

The server offers tools and nothing else: `initialize` declares the `tools` capability alone, with no resources, prompts or logging. The standard streams are its only transport. Every notification except `notifications/initialized` is dropped, and nothing cancels a command once it is sent. A client that cancels, times out or disconnects loses only the answer, and the editor finishes what it started, as it does after exit code 4. [What Strata does not do](../appendix/not-in-strata.md) lists such gaps together.

:::history
Until 0.4.0 every command was a tool. The toolsets and the compact definitions came with that release, when 121 tools cost about 27,000 tokens. The `settings` toolset joined in 0.6.0.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| One tool per command | Strata until 0.4.0 | The model sees every command at once and needs no discovery step | Tokens for definitions the model never uses, and the tool limit of clients |
| One generic call tool only | Strata offers it as `strata_call` | A list of one tool and no maintenance of tables | No schemas to check arguments, and the model must know every name |
| The editor speaks MCP itself | No program of Strata | One process less between client and editor | A second protocol and a listening port for clients, beside the editor's own loopback service with its token |
| Cancellation of commands | No program of Strata | An agent could stop a long capture | A command that can stop half way, which needs a clean way back |
| A search tool over descriptions | Exercise 4 of this page | Finds a command by words instead of by group | One more generic tool, which costs a place in the 32 |

## How it is tested

The tests of StrataCLI run without a real editor: a fake editor, `Tests::PumpedRpcServer`, serves the methods, and each test uses its own session folder. Run a suite with `StrataTests.exe --test-suite=CLI.Mcp` (the binary is under `build/windows/bin/Debug/`).

- `CLI.Commands` covers argument parsing, the order of discovery, `call` with its exit codes (including the timeout), parameters from standard input and from a file, `--save-image`, the strict base64 decoder, `list`, `status` and `launch`.
- `CLI.Mcp` covers the start of a session with its version negotiation, protocol errors, the tool list with and without an editor, the routing of calls, the mapping of results and the announcements of changes. It also covers launching, with a search for a running editor to use again, progress notifications and the stream runner.
- `CLI.McpToolsets` holds the mapping of commands to toolsets, the compact definitions, and the budget test. The budget test starts a fake editor with every command of the editor's registry, lists the tools, and checks at most 32 tools and 30,720 bytes. It also checks that every command lands in a known toolset and that every core command exists. It also prints the total size of the definitions of every command. Any figure for the whole catalogue must come from that output.
- `CLI.Discovery` covers how an editor is found through :term[session files]{id=session-file} and how the path of the editor program is chosen.
- `CLI.McpPresence` checks that the client's name reaches the editor when the connection opens.

## Changing it safely

**A new command in an existing group** needs nothing in StrataCLI: the group's prefix already maps it to a toolset. A **new command group** goes into the prefix table. When it gets a toolset of its own, that toolset goes into the table of toolsets with a description, or `CLI.McpToolsets` fails the "every command lands in a toolset the table names" check. A command in `core` makes the list grow, and the budget test fails at 33 tools or at the byte limit, so another command leaves `core`.

**A new generic tool** also counts against the 32, since the five generic tools are listed in every state. Give the first sentence of its description the purpose, add its cases to `CLI.Mcp`, and check the byte total.

The rules that apply, and why:

- Never log to standard output, and keep the streams binary: protocol lines must stay intact.
- Report every error as a result, never a crash: a model that reads `isError` text can try again, one that meets a dead server cannot.
- Keep calls to the editor on the main thread of the server, because the queue is the only shared object.
- Test anything new with a fake editor: no test of StrataCLI needs a real editor.

## Summary

- An agent sees a command as a tool with a name made from the method, one sentence of description, a schema with short property texts, and a result as text, `structuredContent` and images. Errors arrive as text with `isError` set.
- The default list is the :value{key="toolsets.core.count"} core commands plus five generic tools, at most 32 tools and 30 KiB. A command belongs to a toolset by exact name, then by prefix; an unknown group names its own.
- A tool call goes from the reader thread through `HandleLine`, `HandleMessage` and `HandleToolsCall` to the editor connection, and a terminal call goes through `RunCallCommand` to an exit code from 0 to 5.

## Check yourself

1. A client lists tools while an editor is connected and finds `entity_create` but not `entity_rename`. Which statement is right? (a) The editor lacks `entity.rename`. (b) The `scene` toolset is not enabled, but `strata_call` with `entity.rename` still works. (c) The model must restart the server.
   :::answer{tests="agent-view,toolset-budget"}
   (b). `entity.create` is in `core` and `scene`; `entity.rename` only in `scene`. Option (a) is wrong because the table groups commands the editor has; option (c) is wrong because `strata_toolsets` enables the toolset at once and the server announces the change.
   :::
2. A command's description is "Background on scenes. Creates a scene." What does the model read of it?
   :::answer{tests="agent-view"}
   Only "Background on scenes." plus the note " (details: strata_describe)". The first sentence is kept, so a description that opens with background hides what the command does. This is why the first sentence must say it.
   :::
3. `FirstSentence` receives the single word `Unbroken` and a limit of 4. What does it return?
   :::answer{tests="agent-view"}
   `Unb` plus one ellipsis character. The word holds no space, so the cut falls inside it at the limit minus one, which is 3, and the ellipsis is the fourth character.
   :::
4. A script runs `StrataCLI call input.sequence ... --timeout 1000` and gets exit code 4. What must it not do?
   :::answer{tests="read-cli"}
   A script must not start another editor or conclude that the command failed. Exit 4 means only that no answer came in time; the editor may still run the command.
   :::
5. Decode the base64 text `QUJD`, and the text `QQ` with its two padding characters. Say what the single digit `Q` gives.
   :::answer{tests="read-cli"}
   `QUJD` gives the three bytes of the text `ABC`, and `QQ` with its padding gives the one byte of `A`. A single digit carries no byte, so the decoder rejects `Q` and `call` exits with 5.
   :::

## Exercises

1. **Basic.** Trace one `tools/call` of `entity_create` through the code, with a debugger or a search. Name the function where each step happens, from the reader thread to `MakeToolResult`. Say where a tool outside the enabled toolsets is still found, and where an unknown tool's error is made.
   :::answer[Worked solution]{tests="read-cli"}
   Search for `tools/call` in `StrataCLI/src/CLI/McpServer.cpp`. The reader thread of `RunMcpServer` queues the line. The main loop calls `McpServer::HandleLine`, which reads it and calls `McpServer::HandleMessage`, and that calls `McpServer::HandleToolsCall`. The lookup in `m_ToolToMethod` finds `entity.create`, and it finds a tool outside the enabled toolsets too, because only `BuildEditorTools` checks the toolsets. The error for an unknown tool is made in the same function after the second lookup, and then the editor connection's `Call` sends the method and `MakeToolResult` maps the answer.
   :::
2. **Medium.** Write `Cut`, a function that shortens a sentence to a length in bytes at a space, or inside a word without splitting a :term[UTF-8]{id=utf-8} character. Predict its output for a few inputs.
   :::answer[Worked solution]{tests="agent-view"}
   The sketch below follows `FirstSentence`. For a limit of 12, "A rather long sentence" has a space at index 8, so it gives "A rather" and the ellipsis. The word `Unbroken` has no space, so it keeps three characters and the ellipsis. Four é characters take eight bytes. Cuts at 5 and at 4 bytes both stop before a half character.

   ```cpp sketch="automation-mcp-cut.cpp"
   // Cuts a sentence to a length in bytes at a space, or inside a word but never inside a UTF-8 sequence.
   #include <iostream>
   #include <string>

   std::string Cut(const std::string& text, size_t maxLength)
   {
   	if (text.size() <= maxLength)
   		return text;
   	size_t length = text.rfind(' ', maxLength - 1);
   	if (length == std::string::npos || length == 0)
   	{
   		length = maxLength - 1;
   		// A byte of the form 10xxxxxx continues a character: step back to the byte that starts it.
   		while (length > 0 && (static_cast<unsigned char>(text[length]) & 0xC0) == 0x80)
   			length--;
   	}
   	return text.substr(0, length) + "\xE2\x80\xA6";
   }

   int main()
   {
   	std::cout << Cut("A rather long sentence", 12) << "\n";
   	std::cout << Cut("Unbroken", 4) << "\n";
   	std::cout << Cut("\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9", 5) << "\n";
   	std::cout << Cut("\xC3\xA9\xC3\xA9\xC3\xA9\xC3\xA9", 4) << "\n";
   	return 0;
   }
   ```

   ```text output-of="automation-mcp-cut.cpp"
   A rather…
   Unb…
   éé…
   é…
   ```

   1. **Line 9:** the cut falls at the last space that leaves room for the ellipsis.
   2. **Lines 12-15:** without a space the cut steps back over continuation bytes.
   3. **Line 17:** one ellipsis character is added.
   :::
3. **Hard.** Register a Query command and make it a tool. Which test fails first, and which after it?
   :::answer[Worked solution]{tests="toolset-budget"}
   Register the command in its group's file with a first sentence that says what it does. `Editor.Journal` fails until the name is in `c_QueryCommands` of `StrataTests/src/Editor/CommandJournalTests.cpp` and in each flag list that applies to it, because every command is in exactly one kind list. `StrataCLI list` then shows it. `CLI.McpToolsets` fails until the command's group maps to a toolset of the table, so add a prefix line for a new group. Then the tool appears once its toolset is enabled, and a call from the terminal shows in the :term[activity journal]{id=activity-journal}.
   :::
4. **Hard.** Design a generic tool that searches the descriptions of all commands, keeping the 32-tool budget.
   :::answer[Worked solution]{tests="toolset-budget"}
   The five generic tools plus :value{key="toolsets.core.count"} core commands fill the list, so something must leave. Either the new tool replaces `strata_describe`, whose purpose it can absorb with a `query` argument, or a core command leaves `core`. Add an entry to `GetGenericTools`, extend `IsGenericTool`, handle the name in `HandleToolsCall`, and add `CLI.Mcp` cases for a match, no match and a missing editor. Then run `CLI.McpToolsets` to confirm 32 tools and 30,720 bytes.
   :::

## Where it lives in Strata

- `StrataCLI/src/Main.cpp` and `StrataCLI/CMakeLists.txt`: the thin `main` and the library.
- `StrataCLI/src/CLI/McpServer.cpp`: the server, the helpers, the generic tools and `RunMcpServer`.
- `StrataCLI/src/CLI/McpToolsets.cpp`: the toolset tables and the compact definitions.
- `StrataCLI/src/CLI/CliApplication.cpp` and `StrataCLI/src/CLI/ImageOutput.cpp`: the commands, exit codes and image saving.
- Tests: `CLI.Commands`, `CLI.Discovery`, `CLI.Mcp`, `CLI.McpToolsets` (also in `StrataTests/src/Editor/EditorMcpToolsetsTests.cpp`), `CLI.McpPresence`.
- Command: `StrataCLI mcp --toolsets <name,...|all>`.

## Further reading

- The Model Context Protocol specification, modelcontextprotocol.io: the messages, versions and capabilities of the protocol (intermediate).
- The JSON-RPC 2.0 specification: the request, answer and batch format under MCP (beginner).
