# Brief: `make/with-an-agent`

| Field | Value |
| --- | --- |
| Title | Making a game with an AI agent |
| Kind | T |
| Size | L |
| Tracks | G |
| Needs | `make/commands` |
| From | automation "Connecting an AI agent (MCP)", "Making a game as an agent"; gamedev §1.19 (hands-on G15); skill `strata-make-a-game`; the launcher's agent card, toolsets, presence, the Activity panel (Copy as script, Re-run, Undo to here), steering an agent safely; Tetris as the model; use home of the activity journal |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/with-an-agent` — Making a game with an AI agent

**Covers.** The tutorial lets an AI agent build a level in the reader's editor while the reader watches, checks and
undoes. It opens with the idea: an agent is a program driven by a language model that acts through tools; Strata gives
it the editor's commands as tools through MCP, so it does what the menus do, and every step it takes is journaled (the
agent's path: the agent, `StrataCLI mcp`, the editor's loopback connection, the same commands as the UI). Sections, each
ending in a checkpoint: connect an agent from the launcher's "Connect an AI agent" card (the exact `claude mcp add
strata -- "<StrataCLI>" mcp` line, copied), and see the automation pill turn to "Agent connected"; what the agent sees:
the `core` toolset (at most 32 tools), `strata_describe`, `strata_toolsets` to enable another group such as `scene`,
`strata_call` for any command, and the shipped skills (editor automation, scripting, making a game) placed where the
agent reads them; ask the agent to place props with `asset.place` and watch the viewport's agent chip and the outline
flash of what it changed; the Activity panel: every row by the person, the agent (by name) or a script, a row's details,
**Copy as script**, **Re-run**, **Undo to here**; steering an agent safely (unsaved changes are refused unless forced, a
toast names the agent that discarded changes and offers Recover, an agent's name is shown but never trusted, what to ask
an agent to check: `editor.status`, a capture; and one sentence with a pointer to recovery on `make/project-files`: an
editor the agent started with `strata_launch_editor` closes after 600 s without a client, and its unsaved scene changes
are discarded and kept as recovery data); the session as a regression: note where the session starts, have
`editor.activity.export` write it as a command script with `bind` and `$ref`, add `expect`s, copy the project's
`Scripts/` (and any source assets the session generated) into a fresh copy, because files written outside commands are
not in the script (if you do not see the scripts build in the replay, they were not copied), and run the script on the
copy with `StrataEditor --commands` (G15); the whole game the agent way: the `strata-make-a-game` playbook in eight
steps (an editor, a project and a plan, assets, scripts, the scene, playing and looking, a regression, the export), with
the Tetris sample as the game an agent made through the editor alone. What Strata does not do here: MCP resources,
prompts and logging, a transport other than the standard streams, and cancellation (an agent that gives up loses only
the answer; the editor finishes the command). The exercise: an agent's three props taken back with **Undo to here**. At
the end the reader can connect an agent, follow and undo what it does, and keep its work as a test.

**Leaves out.**

- Why automate an editor, tools for agents and accountability, as engine design → `automation/agents`
- The MCP server's protocol, tool mapping and token budget → `automation/mcp`
- The journal, command kinds and how a replay script is built → `editor/journal`
- Running commands from the terminal → `make/commands`
- Command scripts and their checks → `make/automated-playtests`
- The Activity panel's drawing → `editor-ui/instrument-panels`

**Fit.** `fits`: about 4,450 words against L (5,000): the idea and its diagram, seven sections of about 17 steps (an
agent's answers shown as text captures), the safety rules, the playbook's outline and the exercise take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:55` | feature | home | The Activity panel: every command with who ran it (person, agent, script); a session exported as a replayable command script |
| `gamedev:248` | feature | home | The skills shipped in the archive's `Skills/`: editor automation, scripting, making a game |
| `gamedev:433` | figure | home | The agent's path: the agent, MCP (`StrataCLI mcp`), JSON-RPC on loopback with a token, the editor's commands (the same as the UI's) |
| `gamedev:455` | figure | home | The Activity panel listing commands by the person and by an agent |
| `gamedev:548` | hands-on | home | G15: an agent connected through MCP places props with `asset.place`; the Activity panel; the session exported as a command script and replayed on a fresh copy |
| `gamedev:660` | term | home | MCP, toolset |
| `automation:225` | feature | home | The package readme's "Connect an AI agent": the `claude mcp add` line, the toolsets, where the skills go |
| `automation:581` | figure | home | The Activity panel after an agent's session: rows by source, an expanded entry, Copy as script, Re-run, Undo to here |
| `automation:584` | figure | home | The toast that names the agent that discarded unsaved changes, with Recover |
| `automation:643` | rule | home | Commands that replace the scene refuse unsaved changes unless `force`; an agent never forces away a person's work |
| `automation:662` | hands-on | home | Connect Claude Code with `claude mcp add strata -- <bin>/StrataCLI mcp`, ask for a scene, watch the pill, the chip and the Activity panel, enable `scene` with `strata_toolsets` |
| `automation:668` | hands-on | home | A session turned into a regression test: note `journal.latest`, build, `editor.activity.export`, add `expect`, copy `Scripts/` (and generated source assets) into the fresh copy first, because files written outside commands are not in the script (`.claude/skills/strata-make-a-game/SKILL.md:441-443`), run it on the copy with `--commands` (passed to `make/automated-playtests`; it needs StrataCLI, so it is taken here) |
| `automation:673` | hands-on | home | A whole game the agent way: the `strata-make-a-game` playbook, Tetris as the reference, a regression script and the exported game run headless |
| `editor-ui:694` | hands-on | home | Connecting an agent from the launcher, watching the agent chip and the outline flash, inspecting its work in the Activity panel |
| `new:19` | not-done | home | MCP resources, prompts and logging, a transport other than the standard streams, and cancellation: the MCP server offers tools only, and nothing cancels a command once it is sent; an agent that gives up or disconnects only loses the answer, and the editor finishes the command, as after the CLI's exit code 4. Evidence: `StrataCLI/src/CLI/McpServer.cpp:367-372` (every notification but `notifications/initialized` is dropped), `:379-397`, `:420` (the `tools` capability alone); `StrataCLI/src/CLI/CliApplication.cpp:357-358` (standard input and output); `StrataCLI/src/CLI/CliApplication.h:24` (exit code 4: the command may still be running in the editor); `git grep -n -i "notifications/cancel" 822a7a46 -- StrataCLI Strata/src/Strata/Network` finds nothing |
| `new:26` | hands-on | home | Exercise, done in the editor: the agent asked to add three props, its work taken back with **Undo to here** on the Activity panel's last row before the agent's first, and the Hierarchy checked. Evidence: `StrataEditor/src/Panels/ActivityPanel.cpp:393-397` (Undo to here undoes the steps after the row) |
| `automation:182-185` | feature | use | The automation pill, the agent chip, the outline flash, the launcher's "Connect an AI agent" card |
| `automation:176` | feature | use | The Activity panel: rows, details, Copy as script, Re-run, Undo to here |
| `automation:152`, `automation:173` | feature | use | `editor.activity.export`; the replay script with its bindings |
| `automation:207-209`, `automation:211`, `automation:213-214` | feature | use | MCP's protocol, the generic tools, commands as tools, toolsets, the 32-tool budget, `strata_describe` |
| `automation:215`, `automation:136` | feature | use | An editor started with `strata_launch_editor` closes after 600 s without a client, and its unsaved scene changes are discarded and kept as recovery data (`StrataCLI/src/CLI/McpServer.h:34-36`; `StrataEditor/src/EditorLayer.cpp:684-691`) |
| `automation:223-224` | feature | use | The skills `strata-editor-automation` and `strata-make-a-game` |
| `automation:415`, `automation:430`, `automation:444` | concept | use | MCP and tool design for models, accountability (journal, presence, replay), determinism for agents |
| `automation:530`, `automation:562`, `automation:564` | figure | use | The four layers, the toolsets, the replay export |
| `automation:574`, `automation:579`, `automation:588` | figure | use | The launcher's card, the agent chip and flash, the agent's tool list |
| `automation:634`, `automation:640` | rule | use | At most 32 tools by default; client names shown, never trusted |
| `editor-core:243` | feature | use | `editor.activity` and `editor.activity.export` (home `editor/journal`) |
| `editor-core:504` | figure | use | Record and replay: entries, the export, a run on a copy |
| `editor-ui:204`, `editor-ui:214` | feature | use | The agent chip and flash; the launcher with its agent card |
| `automation:704`, `automation:769`, `automation:771-773`, `automation:780`, `automation:782-783` | term | link | Agent, MCP, tool, toolset, core toolset, activity journal, presence, replay script |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Running commands from a terminal with StrataCLI | `make/commands` | must |
| Command scripts, `expect`, `bind` and `$ref` | `make/automated-playtests` | must |
| Undo and unsaved changes | `make/project-files` | must |
| Prefabs and placing them | `make/prefabs` | must |
| The launcher | `start/first-game` | must |
| Installing a program | `start/install` | helps |

**Starting state.** The page's starting checkpoint, downloadable: a new project from the Basic 3D template with the
tutorial asset pack's props as prefabs (CC0, credited), saved; an AI agent program that speaks MCP installed on the
reader's computer (the page names Claude Code, whose line the launcher shows); and a copy of the Tetris sample for the
last section.

**Command-only steps.**

- `claude mcp add strata -- "<StrataCLI>" mcp`, the agent program's line that the launcher's card gives.
- The session's export, `editor.activity.export`: a command called with StrataCLI, taught by `make/commands` (a Need).
- The replay on a fresh copy: a command script run with `StrataEditor --commands`, taught by `make/automated-playtests`
  (in the closure through `make/commands`).

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
| critic-make-b2-3 | must | missing-item | `make/with-an-agent` (the connect section; `automation:225`, `automation:662`; Command-only steps) | The launcher's line `claude mcp add strata -- "<StrataCLI>" mcp` adds the server at Claude Code's default scope, local: it loads only when Claude Code starts in the folder where the line ran. A reader who pastes it in one terminal and starts the agent in the game project's folder, where the package readme puts the skills, sees no Strata tools, and the page does not say why. | The connect step says to run the line in the folder where the agent will start (the game project's), or to add `--scope user` before `strata` so that every folder has it; its "If you do not see it" names `claude mcp list` and the scope. About 60 words. The scope is Claude Code's rule, read in its documentation, not at the pin: the brief cites the page, and phase B reads it again. | `allocation/make-b2.md:887-888`, `:930`, `:934`, `:967`, `:973`; pin: `StrataEditor/src/Panels/WelcomePanel.cpp:101`; `Docs/Releases/PackageReadme.md:110-121` (no scope; the skills go into `~/.claude/skills/` or the project's `.claude/skills/`); `https://code.claude.com/docs/en/mcp` ("Local scope is the default. A local-scoped server loads only in the project where you added it"), read 2026-11-10 |
| critic-make-b2-8 | should | missing-item | `make/with-an-agent` (What you need; Starting state) | The tutorial needs a program that is not part of Strata, and the page says only that one is installed. Claude Code is installed with its own installer and needs a paid plan or a Console account; the free plan does not include it. A reader with another MCP client gets no line from the launcher: that client needs the server entry "program `StrataCLI`, argument `mcp`", which speaks over the standard streams. | What you need lists the agent program with its source, the account it needs and that it may cost money, and one sentence for other MCP clients (the program and its argument). About 100 words. Whether a reader without an agent can follow the page another way goes to the planner. | `allocation/make-b2.md:966-969`; `style.md:521-524` (What you need); pin: `StrataEditor/src/Panels/WelcomePanel.cpp:818-822` ("Claude Code and other MCP clients"); `StrataCLI/src/CLI/CliApplication.cpp:596` (MCP on stdin and stdout); `https://code.claude.com/docs/en/setup`, "Authenticate" ("The free claude.ai plan does not include Claude Code access"), read 2026-11-10 |
| critic-make-b2-9 | should | shape | `make/with-an-agent` (each section's checkpoint) | A tutorial's step section ends with a checkpoint that the tutorial tool makes by running the stage, and a picture headed "You should now have". In the agent's sections a language model acts: what it places, and where, differs from run to run, and no tool of the plan runs an agent for a stage. The page's list does not say how these checkpoints are made or what the reader's project shares with them. | Each agent section's stage runs a command script that stands in for the agent (a recorded session, as G15 exports one); its "You should see" names what is fixed (the props exist, the journal's rows, the pill) and says that positions differ, and the next section starts from either project. About 60 words; the rule for such stages goes to the planner. | `allocation/make-b2.md:886-887`, `:917-918`; `style.md:525-528`; `pipelines.md:662-668` (an MCP client scripted for figures only) |
| critic-make-b2-24 | could | wrong-home | `make/automated-playtests` (`gamedev:658`); `make/with-an-agent` | The term "activity journal, replay" is homed on `make/automated-playtests`, which first shows the journal and Copy as script. book.md's one-home row of the activity journal names `make/with-an-agent` as its use page, and the outline calls that page the use home of the activity journal, so the glossary step would find two answers. | One of two changes (forPlanner): book.md's row names `make/automated-playtests`, the earlier page where the reader meets the journal, and `make/with-an-agent` keeps its feature rows; or the term row moves to `make/with-an-agent`, and `make/automated-playtests` says in one sentence what the journal is. No words added. | `allocation/make-b2.md:689-691`, `:729`, `:924`; `book.md:360`; `outline-1.md:219`, `:221` |
