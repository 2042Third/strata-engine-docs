# Brief: `reference/commands`

| Field | Value |
| --- | --- |
| Title | The command catalogue |
| Kind | R |
| Size | XL |
| Tracks | - |
| Needs | `editor/commands`, `basics/data-formats` |
| From | editor-core ch. 16; the editor's command registry (`editor.commands`: name, description, parameter schema, kind); may be split into one page per command group |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/commands` — The command catalogue

**Covers.** The paragraph on top says what the catalogue is: every command the editor registers, from the dump of
`editor.commands` in a `--no-gpu` editor at the pin, so the count is `:value{key="commands.count"}` and is never typed.
It says how to read an entry: the name `<group>.<action>`; the kind (Edit, Query or Session: what an undo step,
a replay and the journal do with it); the description, written for agents and shown as the engine wrote it; the
parameters as a table (name, type, required, default, description) with the JSON Schema in a closed block; the parsed
flags `MayDefer` (the command may take frames), `WaitsForAssets` (it waits for the background asset scan) and
`Results` (Content or Session: whether a replay may bind identifiers from its result); and the MCP toolset that
offers it as a tool. There is no result schema, so the result is the description's own words, with an example result
where a tutorial run recorded one (`reference/_examples/`). The generated part opens with a table of the command
groups (group, count, toolset), then one section per group in the order of `EditorCommandRegistry`, from `scene.*`,
`entity.*`, `component.*` and `prefab.*` to `graphics.resetPlayerOptions`. Hand-written: one sentence per group that
names the page teaching what the group does; a note that `editor.showPanel` and `editor.showDialog` are registered by
the editor's window (`EditorLayer`), not by `StrataEditorCore`, and fail in an editor without a window; and the
erratum on the count (`new:1`). `## Where it lives in Strata`: `EditorCommands.cpp`, the `Editor*Commands.cpp` and
`Commands/` files, `CommandJournalTests.cpp` (which pins every command's kind and flags) and `McpToolsets.cpp`. The
tool is `tools/reference.py`, route "commands". When the rendered file passes the site's largest-page budget, the
catalogue becomes one page per group (`reference/commands/<group>`, `../site.md`), and the outline gets those rows first.

**Leaves out.**

- How a command is registered, checked against its schema and run → `editor/commands`
- Commands that take frames and the poll that owns their data → `editor/deferred-commands`
- What an undo step records → `editor/undo`
- Running commands from the CLI and in command scripts → `make/commands`
- Command scripts, batches and expectations → `editor/command-scripts`
- The journal and replays, which use the kinds → `editor/journal`
- How commands become MCP tools and what each toolset is for → `automation/mcp`
- The protocol that carries a command, its errors and the CLI → `reference/automation`
- Adding a command → `editor/tutorial-command`

**Fit.** `fits`: about 2,000 words against XL (8,000). The generated catalogue gives the page its size: about 150
commands with their descriptions and parameter tables, roughly 18,000 words; the spike built it at that size, and its
largest page was the glossary (`../spike-report-1.md`), so no split by group is expected. The prose is the paragraph on
top, about 25 group sentences, the note on the window's two commands, the erratum and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:1` | erratum | home | The inventories count 151, 153 and 154 commands. The fact: `StrataEditorCore` registers 151 (63 Edit, 46 Query, 42 Session), and the editor's window adds `editor.showPanel` and `editor.showDialog`, also in a `--no-gpu` editor, where they fail. The page never types a count: `:value{key="commands.count"}`. Evidence: `StrataTests/src/Editor/CommandJournalTests.cpp:102-164` (the three lists), `:234` (the check of their total); `StrataEditor/src/EditorLayer.cpp:177`, `:233`; `StrataEditor/src/EditorLayer.cpp:187`, `:242` (they fail without a window) |
| `editor-core:54` | feature | use | The fields of `EditorCommand` that the columns show: name, description, schema, kind, results, flags |
| `editor-core:60-62` | feature | link | The kinds as a tested decision, the wait for the asset scan, and `editor.commands`, the dump's source |
| `editor-core:63` | feature | use | The two commands of the window, in the note |
| `editor-core:74-97` | feature | link | Every command group with its purpose, one sentence and a link each |
| `editor-core:236` | feature | link | `Defer(poll)`, behind the `MayDefer` column |
| `automation:149` | feature | link | `editor.commands` as agents call it |
| `automation:169` | feature | link | `EditorCommandResults`, behind the `Results` column |
| `automation:209` | feature | link | Every command becomes an MCP tool |
| `automation:211` | feature | link | The toolsets, behind the toolset column |
| `scene-ecs:235` | feature | link | The `entity.*` and `component.*` commands seen from the scene's side |
| `assets:212` | feature | home | The `asset.*` commands as catalogue entries; each is named on the page of its subject |
| `render-direct:50` | feature | link | The `material.*` commands |
| `scripting:205` | feature | link | The `script.*` commands |
| `animation:92` | feature | link | The `animation.*` commands |
| `audio-input:98` | feature | link | `audio.state` |
| `audio-input:179-180` | feature | link | The `input.*` and `inputActions.*` commands |
| `physics:172` | feature | link | `physics.stats` and `physics.setDetailedStats` |
| `gameui:214` | feature | link | `ui.create`, `ui.layout` and `ui.hitTest` |
| `worlds-runtime:111` | feature | link | The `world.*` commands |
| `worlds-runtime:167` | feature | link | The export commands of `project.*` |
| `worlds-runtime:181` | feature | link | The commands of the launcher, templates and samples |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What a command is and how to run one: names, schemas, kinds and the registry | `editor/commands` | must |
| JSON values and objects | `basics/data-formats` | must |
| Undo steps | `editor/undo` | helps |
| Commands that take frames | `editor/deferred-commands` | helps |
| The journal and replays | `editor/journal` | helps |
| MCP tools and toolsets | `automation/mcp` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-5 | should | missing-item | new item on `reference/commands` | Every command parameter follows value forms that no reference page states: IDs as 16 hexadecimal digits; an asset as a handle, a path relative to `Assets/` or `Builtin/<Name>`; component values in the scene file's form, with rotations as Euler degrees, a quaternion `[x, y, z, w]` or `{"Euler": [...]}`, enums by option name, asset properties as a UUID, an integer or null, and a value outside a property's range refused, never clamped. The form `Builtin/<Name>` appears on no page of the plan, and no reference page lists the nine built-in assets with their handles, though the smoke script that `editor/command-scripts` quotes uses `Builtin/Cube`. | `reference/commands` adds a hand-checked table "How values are written", one row per form with an example, checked against `PropertyJson.cpp` and `CommandUtils::FindAsset`, and a table of the built-in assets (name, type, handle: `Cube` to `Torus` 1 to 8, `DefaultMaterial` 0x10); the introduction names `editor/commands` and `assets/handles-meta`. About 200 words. | `allocation/reference.md:100-116`; `Strata/src/Strata/Reflection/PropertyJson.cpp:380-485`; `StrataEditor/src/Editor/CommandUtils.h:63-65`; `StrataEditor/src/Editor/CommandUtils.cpp:100-122`; `Strata/src/Strata/Asset/BuiltinAssets.h:24-38`; `Strata/src/Strata/Asset/BuiltinAssets.cpp:15-25`; `.claude/skills/strata-editor-automation/SKILL.md:276-284`; `StrataTests/Editor/SmokeCommands.json.in:8`; a search for `Builtin/` in `allocation/*.md` finds nothing |
| critic-reference-6 | should | missing-item | new item on `reference/commands` | The command script's step has no reference table: `command`, `parameters`, `expect` (JSON pointers mapped to `equals`, `min` and `max`), `bind`, `{"$ref": name, "pointer": ...}` and `until` (`steps` from 1 to 10,000,000, `seconds` 300 by default and at most a day, on a query with an `expect` only), and `editor.batch`'s 1,000 steps. Every sample's regression script is written in it, and the editor's own `--help` names only four of the keys. | `reference/commands` adds a hand-checked table of the step's keys, one row each with its form, an example and its limit, checked against `EditorCommandRunner.h` and `BatchCommands.cpp`; the introduction names `editor/command-scripts` and `make/automated-playtests`. About 150 words. | `allocation/reference.md:124`; `allocation/editor.md:1070-1079`; `StrataEditor/src/Editor/EditorCommandRunner.h:74-97`, `:135-137`; `StrataEditor/src/Editor/Commands/BatchCommands.cpp:23`; `StrataEditor/src/EditorApplication.cpp:66` |
