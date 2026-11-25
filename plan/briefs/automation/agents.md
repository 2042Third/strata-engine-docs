# Brief: `automation/agents`

| Field | Value |
| --- | --- |
| Title | How the editor makes games with agents |
| Kind | C |
| Size | M |
| Tracks | E |
| Needs | `editor/journal` |
| From | automation concepts 2.1 (why automate an editor), 2.12 (the design of tools), 2.13 (accountability), 2.14 (determinism for agents); gamedev ch. 30 (the agent path diagram) |
| Unit | `plan/allocation/automation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `automation/agents` — How the editor makes games with agents

**Covers.** The problem as a reader meets it: an AI agent in a terminal is asked to build a level, and an editor is
windows and clicks that a program cannot use. The naive answers break: simulated clicks fail when the layout moves, and
a second API written for agents drifts away from what the UI does. The idea: every editor operation is already a
command (its home is `editor/commands`: one sentence and a link), so the editor only has to offer the same commands to
other programs. The approaches engines use, each brought in by the flaw of the one before: an embedded script language
(Python in Unreal and Blender, C# editor scripts in Unity), a batch mode (Unity's `-batchmode -executeMethod`, Godot's
`--headless --script`), a remote-control protocol over a socket (Unreal's Remote Control API, the browser DevTools
protocol, language servers) and UI automation, ending with a table of their costs. Strata's choice and its reason: a
batch mode (`--commands` scripts) and a remote protocol on one registry, so a feature reaches agents the moment it
registers a command, with no code for automation. The map of the part: the four layers (transport, editor binding,
clients, the person's view) in one diagram, each with the page that explains it. Then what an agent is: a program built
on a language model that reads tool descriptions and calls tools. What it sees (names, descriptions and schemas only),
what every definition costs (tokens of its context) and what its clients allow (about 128 tools); the ways to design
tools for it (one tool per operation, one generic call, sets that change, a tool that describes the others) and
Strata's mix of a small default set and generic tools, with a bridge to `automation/mcp`. What an agent reads first:
`editor.status`, compact unless it asks for sections, and `log.read`; the skills that ship in the release archive as
its manual (three; the scripting skill's subject, the script SDK, is taught in the part `scripting`). Accountability:
the person must see what the agent did, undo it and keep its work as a test; Strata journals every command with its
origin, shows that an agent is present and exports a session as a script (the mechanism is `editor/journal`'s).
Determinism for agents: a call takes about a tenth of a second and frame rates differ from machine to machine, so tools
count game time in fixed steps (`editor/stepping`). The worked example reads the end-to-end test in which an agent
builds, plays, undoes, saves and exports a game through StrataCLI, call by call. What the choice cannot do: an exported
game cannot be driven this way (`worlds/runtime`). The page never types the number of commands (`:value`). Afterwards
the reader can say why Strata offers commands instead of a scripting API, name the four layers and their pages, and
judge a command's description and kind as an agent will read them.

**Leaves out.**

- Running one command from a terminal → `editor/commands`
- The journal entry, command origins and the replay export → `editor/journal`
- Fixed steps, `play.step` and `input.sequence` → `editor/stepping`
- Command scripts and `editor.batch` → `editor/command-scripts`
- Connecting Claude Code and making a game with it, step by step → `make/with-an-agent`
- How the status bar shows connected agents → `editor-ui/status`
- The viewport's agent chip and flash → `editor-ui/scene-view`
- Sockets, framing and JSON-RPC → `automation/json-rpc`
- The MCP protocol, the toolsets and their code → `automation/mcp`
- Why an exported game has no automation → `worlds/runtime`

**Fit.** `fits`: about 3,900 words against M (3,000). The four approaches with their table, the design of tools for
language models and the worked example take the most, then the exercise; accountability and determinism are a
paragraph each that links its home.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `automation:269` | concept | home | Why automate an editor: embedded scripting, batch modes, remote control, UI automation; their table; Strata's batch mode and remote protocol on one registry |
| `automation:415` | concept | home | Tool design for language models: what an agent sees and pays for, the four ways to offer tools, Strata's mix of a core toolset and generic tools; the protocol and its code are `automation/mcp`'s |
| `automation:430` | concept | home | Accountability as a design goal: see what the agent did, undo it, replay it; logs, undo histories, macro recorders and event sourcing compared; the journal itself is linked |
| `automation:444` | concept | home | Why an agent's play-test counts fixed steps, never frames |
| `automation:148` | feature | home | `editor.status` as an agent's first call: compact by default, sections (`automation`, `editor`, `sceneLoad`, `recovery`) on request |
| `automation:154` | feature | home | `log.read`, and the unread errors that `editor.status` counts |
| `automation:223-224` | feature | home | The skills `strata-editor-automation` and `strata-make-a-game`: what each teaches an agent; the third skill that ships, `strata-scripting`, is named here, and its subject, the script SDK, is taught in the part `scripting` |
| `automation:226` | feature | home | StrataCLI and three skills (`strata-editor-automation`, `strata-make-a-game`, `strata-scripting`) ship in the release archive's `Skills/`, next to the editor (`CMake/StrataPackaging.cmake:84-85`) |
| `automation:242` | feature | home | The suite `EndToEnd.EditorAutomation`: real processes, an agent's whole session, MCP's tools, answers while a large project scans |
| `automation:520` | code | home | `StrataTests/src/Editor/EditorAutomationProcessTests.cpp:341-437`: an agent's session as a test (list, status, create a project, entities, a deferred wait, play, undo, errors, save, export, quit); the handshake test of the same item is read on `automation/security` |
| `automation:530` | figure | home | The four layers: MCP client, StrataCLI, loopback TCP, the server's threads, the binding and the registry, with `call` and `--commands` as other ways in |
| `new:8` | hands-on | home | The page's exercise (D27), done on the workbench with commands from a terminal (about 250 words): read the editor as an agent does: `editor.status` compact, then with the sections `automation` and `sceneLoad`, and `log.read` from level Error, through `StrataCLI call`; say what each answer tells an agent before it acts and why reading the errors clears `errors.unread`; then judge the first sentence of three commands' descriptions in `StrataCLI list` as an agent reads them. Evidence: `StrataEditor/src/Editor/EditorStateCommands.cpp:733-750` (`editor.status`: compact by default, its sections), `:981-984` (`log.read` marks the errors read for `editor.status`); `StrataCLI/src/CLI/CliApplication.cpp:587` (`list`: the methods and their descriptions) |
| `automation:703-704` | term | home | Automation; agent (AI agent) |
| `automation:771` | term | home | Tool (of a language model) |
| `automation:776` | term | home | Tokens (of a language model), with a qualifier: the session token is `automation/security`'s |
| `automation:613` | rule | use | Commands are the API: no RPC endpoint per feature, named as the reason for the part; its home is `automation/rpc-server` |
| `editor-core:299` | concept | use | The command pattern and one API for three clients, as the base of the part |
| `editor-core:463` | figure | link | Three clients, one registry |
| `editor-core:359` | concept | link | Command scripts, record and replay |
| `editor-core:372` | concept | link | Telling the person what happened |
| `gamedev:433` | figure | link | The agent path, drawn for game makers on `make/with-an-agent` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Commands are the API: one registry, a description, a JSON Schema and a kind per command | `editor/commands` | must |
| Running a command from a terminal with `StrataCLI call` | `editor/commands` | must |
| Command scripts with `expect`, `bind` and `$ref`; `editor.batch` | `editor/command-scripts` | must |
| The activity journal, command origins and the replay export | `editor/journal` | must |
| Fixed steps, `play.step` and `input.sequence` | `editor/stepping` | must |
| JSON objects, arrays, strings and numbers | `basics/data-formats` | must |
| Commands that answer in a later frame (`editor.wait`) | `editor/deferred-commands` | helps |
| Play mode and the running copy that `play.stop` discards | `editor/play-mode` | helps |
| Undo steps and their names | `editor/undo` | helps |
| The unsaved-changes guard and `force` | `editor/saving` | helps |
| A process | `basics/computer` | helps |
| The status bar's pills | `editor-ui/status` | helps |
| Exporting a game | `worlds/export` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `ai-agent` | AI agent | - |
| `automation` | Automation | - |
| `tokens-llm` | Tokens (LLM) | - |
| `tool` | Tool | - |
