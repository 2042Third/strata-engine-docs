# Brief: `editor/commands`

| Field | Value |
| --- | --- |
| Title | Commands |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `world/reflection`, `basics/data-formats`, `editor/program` |
| From | editor-core ch. 2 "Commands: one API for people, agents and tests" and §1.2.1 (every command group); running one command from a terminal with `StrataCLI call`, parameters from a file (`@file`), which later pages of track E use for a step that has no menu or button (`style.md` §10); home of "commands are the API" |
| Unit | `plan/allocation/editor.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor/commands` — Commands

**Covers.** The problem: a person, an AI agent and a test must make the same edit in the same way, and get the same
answer. The idea is the command pattern: one named operation that takes a JSON object and returns JSON or an error. The
approaches (in-process command objects, scripting APIs, remote calls) come in one paragraph that links forward to the
pages on agents. Strata's choice, "commands are the API": every operation is a command named `<group>.<action>`, with a
description written for agents, a JSON Schema, a kind (Edit, Query, Session) and two flags, in one registry that the UI,
the automation server and command scripts all call. The contract follows in the order a call flows: `EditorCommand` and
`EditorCommandResult` (a value or an error whose kind tells a wrong request from a wrong moment), `Execute` (the journal
entry, the wait for the asset scan, the undo step attributed), the schema check before the handler (unknown and missing
parameters refused; exceptions caught only at the third-party boundary), `CommandArguments` collecting the first
problem, and `CommandUtils` (assets and entities resolved, components applied with the inspector's validation and value
ranges, files written for clients through `ResolveOutputPath`). The rules come with their reasons: every change goes
through a command; invalid input is rejected without side effects; one undo step per successful mutation; component
writes are signalled; commands are written for agents (a description that says what the command does and returns, a
complete schema with property descriptions and `required`, IDs as 16-digit hexadecimal strings, assets by handle or
path, results as JSON objects with camelCase keys, images as `{"Image": {"MimeType", "Data"}}`), because every command
is also an RPC method and an MCP tool whose description and schema are all an agent reads. The smallest complete
mutating command, `entity.rename`, is walked through line by line, with its transaction named and linked to
`editor/undo`. Kinds and flags are decisions a test checks (the kind lists of `CommandJournalTests.cpp`);
`editor.commands` lists the registry; the UI adds two commands of its own; owners add sections to `editor.status`
(status providers; the command itself is `automation/agents`', linked forward). A table maps every command group to what
it is for and the page that teaches it (the `ui` group names `ui/input` beside `make/automated-playtests`). The
`entity.*` row says more, because the clipboard is three commands: `entity.copy` is a Query whose result (entity data
under a format header) feeds `entity.paste`, an Edit that gives the copies new IDs under a parent at an index, points
references between the copies at each other (the remapping is `world/serialization`'s and is linked), makes names unique
and warns about data this build cannot read; `entity.duplicate` puts each copy right after its original, in one undo
step. Last, the reader runs one command from a terminal with `StrataCLI call <command>`, its parameters inline, from a
file (`@file`) or from standard input, which later pages of track E use for steps that have no menu or button. The
example renames the Ground of a `basic3d` project from the terminal, reads the answer, then sends a wrong parameter and
reads the error. The toy is a registry of three commands in 60 lines. The trace exercise follows a call with an unknown
parameter from `Execute` to the line of `CheckParameters` that refuses it. The page never types the number of commands
(`:value`). Afterwards the reader can read any command's registration, call it from a terminal and say why a call was
refused.

**Leaves out.**

- Undo steps, transactions and `FinishEdit` → `editor/undo`
- Commands that answer in a later frame (`Defer`, `MayDefer`, `WaitsForAssets`) → `editor/deferred-commands`
- The activity journal and replays → `editor/journal`
- Every command with its parameters → `reference/commands`
- How a request reaches the registry over the network → `automation/rpc-server`
- StrataCLI's structure and the MCP server → `automation/mcp`
- Adding a command → `editor/tutorial-command`

**Fit.** `over`: about 7,350 words against L (5,000). Counted again from the sections, with the clipboard of the
`entity.*` row, the rule on writing commands for agents and the trace exercise: two concepts, the contract in six
features, six excerpts, six rules, the group table and three hands-on pass L's top; the next size is XL (8,000) (S2).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-core:299` | concept | home | The command pattern and a single API for three clients; schema as contract; error kinds |
| `editor-core:305` | concept | home | Validate first and change nothing on failure; `CommandArguments` keeps the first problem |
| `editor-core:54-60` | feature | home | `EditorCommand`, `EditorCommandResult`, `Execute`, the schema check, `CommandArguments`, `CommandUtils`, kinds as a tested decision |
| `editor-core:62-65` | feature | home | `editor.commands`, the two UI-only commands, value ranges, output paths |
| `editor-core:47` | feature | home | Status providers: sections of `editor.status` that their owners register; the command `editor.status` is homed on `automation/agents` (`automation:148`), and the page's sentence on providers links it forward |
| `editor-core:74`, `editor-core:76-97` | feature | home | The map of every command group: what each is for and the page that teaches it; the `ui` group (`editor-core:93`) names `ui/input` beside `make/automated-playtests` (R44) |
| `editor-core:75` | feature | home | The `entity.*` row of the group map, with the clipboard: `entity.copy`, a Query whose result (entity data under a format header) feeds `entity.paste`, an Edit (new IDs, a parent and an index, references between the copies pointed at the copies, names made unique, warnings for data this build cannot read); `entity.duplicate`, each copy right after its original, one undo step; the remapping is `world/serialization`'s (`scene-ecs:33`), linked. At the pin: `StrataEditor/src/Editor/Commands/EntityCommands.cpp:220-224`, `:288-303`, `:305-345` |
| `editor-core:381` | code | home | `StrataEditor/src/Editor/EditorCommands.h:44-80`: `EditorCommandResult`, value, error, kind and defer in one struct |
| `editor-core:383` | code | home | `StrataEditor/src/Editor/EditorCommands.h:84-113`: `EditorCommand` and `MayDefer`, metadata as decisions |
| `editor-core:385` | code | home | `StrataEditor/src/Editor/Commands/EntityCommands.cpp:514-528`: `entity.rename`, the smallest complete mutating command |
| `editor-core:389` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:105-151`: `Execute`, the journal, the scan wait, the `MayDefer` assertion, undo attribution |
| `editor-core:391` | code | home | `StrataEditor/src/Editor/EditorCommands.cpp:174-221`: `Run` and `CheckParameters`, the schema as contract |
| `editor-core:463` | figure | home | Three clients, one registry |
| `editor-core:465` | figure | home | The command lifecycle; its deferred branch is drawn here and explained on `editor/deferred-commands` |
| `editor-core:542` | rule | home | Every change goes through a command (or a transaction or `SetPropertyWithUndo` for continuous UI edits) |
| `editor-core:546` | rule | home | Reject invalid input without side effects; one undo step per successful mutation |
| `editor-core:550` | rule | home | Signal component writes (`MarkModified`), shown in `entity.rename` |
| `editor-core:558` | rule | home | Mark every command's kind, its session results, `MayDefer` and `WaitsForAssets`; what each mark is for, with links forward |
| `editor-core:591` | rule | home | Files written for clients go through `ResolveOutputPath` |
| `new:69` | rule | home | Write commands for agents: a description that says what the command does and returns, a complete schema (property descriptions, `required`), IDs as 16-digit hexadecimal strings, assets by handle or path, results as JSON objects with camelCase keys, images as `{"Image": {"MimeType", "Data"}}`; the reason: every registered command is an RPC method and an MCP tool, whose description and `inputSchema` are what an agent reads (about 120 words; `automation/rpc-server`'s rule `automation:613` links it). Evidence: `Docs/DeveloperGuide.md:6281-6289` |
| `editor-core:651-656` | term | home | Command, command registry, JSON Schema, command kind, session results, `InvalidParameters` and `Failed` |
| `new:1` | erratum | home | The inventories count 151, 153 and 154 commands. At the pin `StrataEditorCore` registers 151 (63 Edit, 46 Query, 42 Session) and the UI adds `editor.showPanel` and `editor.showDialog`; the page writes `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` and `:234`; `StrataEditor/src/EditorLayer.cpp:177`, `:233` |
| `automation:192-193` | feature | use | `StrataCLI call` with parameters inline, `@file` or `-`, and its exit codes, at the level of running one command |
| `automation:155` | feature | home | The command contract as the automation survey states it (`EditorCommand`, `EditorCommandResult`, `CheckParameters`); one home with `editor-core:54-57` |
| `automation:149` | feature | home | `editor.commands`, which lists the registry with each command's kind and flags; one home with `editor-core:62` |
| `editor-ui:780` | term | home | Status provider: a section of `editor.status` that its owner registers; one home with `editor-core:47` |
| `scene-ecs:235` | feature | home | The commands on scenes, entities, components and prefabs, as rows of the group map |
| `gamedev:366` | code | home | `StrataEditor/src/Panels/SceneHierarchyPanel.cpp:129-151`: the Hierarchy's Create menu runs `entity.create`; with `:72-91`, the presets it sends |
| `gamedev:556` | hands-on | home | Exercise: a Hierarchy preset that goes through `entity.create`, which proves that the UI calls commands |
| `new:49` | hands-on | home | Trace it yourself (D27): with a breakpoint in `EditorCommandRegistry::Execute`, call `entity.rename` from a terminal with an unknown parameter, follow the call into `Run`, and name the line of `CheckParameters` that refuses it before the handler runs. Evidence: `StrataEditor/src/Editor/EditorCommands.cpp:105-151`, `:174-221` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The editor core, `EditorContext` and the frame order | `editor/program` | must |
| JSON: objects, arrays, strings, numbers | `basics/data-formats` | must |
| Lambdas and `std::function` | `basics/cpp-generic` | must |
| `std::optional` | `basics/cpp-modern` | helps |
| Errors returned, never thrown; exceptions caught at the call site | `core/conventions` | must |
| Entities and their UUIDs | `world/ecs` | must |
| The transform contract and change signals | `world/scene-graph` | must |
| Reflection: `ComponentInfo`, `PropertyInfo`, ranges | `world/reflection` | must |
| Entities serialized and made again with fresh IDs, references remapped | `world/serialization` | helps |
| A terminal: running a program with arguments, quoting a path | `basics/tools` | must |
| Reading a command's JSON in a book's command tab | `start/how-to-read` | helps |
| Paths that are safe to write (UTF-8 paths, reserved names) | `core/files` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `failed` | `Failed` | - |
| `invalidparameters` | `InvalidParameters` | - |
| `command` | Command | - |
| `command-kind` | Command kind | - |
| `command-registry` | Command registry | EditorCommandRegistry |
| `json-schema` | JSON Schema | - |
| `session-results` | Session results | - |
| `status-provider` | Status provider | - |
