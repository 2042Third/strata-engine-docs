# Notes: make/with-an-agent

## New terms

None: agent, toolset, activity journal, loopback and replay script are explained in plain words or defined in bold without being proposed as glossary homes (the glossary homes none here).

## Since

- 0.3.0: MCP server and Activity panel (inventory gamedev:55, gamedev:248); toolsets came in 0.4.0.

## Requests

- Names: `Claude` (12 uses: Claude Code, the agent program the launcher's card names).
- Layout: `layouts/make-with-an-agent.ini` (Scene view, Hierarchy, Activity panel at the bottom, status bar) for six editor figures; the `connected` and `steering` pictures need a connected client and a toast.
- Starting checkpoint: three cube-based prefabs (Crate, Barrel, Lamp) made by the stage 1 commands, instead of the brief's asset pack props; no outside license is needed. The tetris figure needs the Tetris sample's copy (its recipe starts from basic3d: the integrator must swap in the sample).
- The tutorial's stage 7 changes to a sample copy: its stage has no commands. Stages 1, 2, 5 and 7 have no commands (an agent connects, a toast and a sample cannot be scripted); stage 3 stands in for the agent with three `asset.place` calls (positions fixed, the agent's differ).
- Hosts for Further reading (cited without links): code.claude.com, modelcontextprotocol.io.

## Not verified

- `claude mcp add` scopes, `claude mcp list`, `/mcp`, the free-plan statement: Claude Code's documentation as the brief cites it, not at the pin.
- The pill text beside the agent's name (the name the client gives is Claude Code's own).
- `StrataCLI launch --project` opens a window editor (the usage line shows the option; only headless is shown in the skill).
- Whether the Hierarchy names a placed prefab after the prefab, and that the title bar marks the scene changed.
- The launcher card's place in the window ("at the bottom of the project list") and the copy button's presence beside the line (`UI::CopyableCode`).
- The exact text of the error that `scene.open` returns over unsaved changes.
- `edit.undo` one step per call; `editor.status` result shape.

## Findings not applied

- critic-make-b2-3, critic-make-b2-8: applied (scope paragraph in step 3; What you need).
- critic-make-b2-9: applied as stand-in stages and the fixed-versus-varying sentence in What you need.
- critic-make-b2-24: a planner decision; the page defines the journal in bold and leaves the glossary as it is.
- The brief's tutorial asset pack props: replaced by cube-based prefabs.

## Clerk

- Admitted to names.txt: Claude. Admitted to external-hosts.txt: code.claude.com, modelcontextprotocol.io (each front page is the site it claims).
- Left for the planner: `layouts/make-with-an-agent.ini`, the connected and steering figures, the Tetris figure's project, the stand-in stages.

## Figures

- result (scene): published in round 1. The recipe's camera "scene" (basic3d's camera at 0, 2, 6 looking at the origin) was replaced by position 0, 1.4, 8.5, target 0, 0.55, 3, fov 34, so the three placed props fill the frame; the alt now says what the picture shows (a cube, a taller narrow box and a thin post, light grey, shadows to the left), since the barrel is a box, not a drum.
- Editor figures (2026-11-18, provisional build 5b975ad2831e, nothing published; every recipe keeps `waitsFor: tier 2: editor screenshot`). A take runs the steps as a command script in an editor started with `--no-automation`: no automation client is ever connected, so the status bar pill reads **Automation off**, the agent chip never shows, every Activity row carries the command script's scroll icon (never the robot or the pointer), and the toast names "A command script". The take also adds its own `editor.wait`, `editor.showPanel` and `editor.screenshot`, which the Activity panel lists as its last rows (no command sets **Changes only** or selects a row). New layouts: `layouts/make-with-an-agent.ini` (960 × 540, Activity in the bottom tabs) and `layouts/make-with-an-agent-activity.ini` (same window, 340 px bottom tabs, for the Activity panel alone).
- connected: cannot. The pill **Agent connected** needs a connected client. The page gets nothing true from a take; nearest honest picture: a diagram of agent, `StrataCLI mcp` and editor, or a picture once the figure tool can connect a client. Recipe left as written.
- toolsets: cannot. Toolsets live in the MCP server, not in the editor, and the robot rows need an automation client. Recipe left; proposal: a text figure of `strata_describe`'s answer, or drop the figure.
- placed: good in round 1. Steps: the stand-in prefabs, three `asset.place` (bound) and `camera.focus` on them; whole window 960 × 540. Caption now names the Scene view and the Hierarchy rows (Crate, Barrel, Lamp, blue prefab rows); the chip is dropped from it, since a take cannot show it. The title bar's changed mark is outside the picture.
- activity: good in round 2. Round 1 (200 px bottom tabs) showed four rows, three of them the take's own; round 2 uses the taller layout. A fourth `asset.place` stands in for **Re-run** and an `edit.undo` for **Undo to here**. No command selects a row, so the details with **Copy as script**, **Re-run** and **Undo to here** cannot show; the caption says what is there: the placements, the undo, scroll icons, and that the last three rows took the picture. What the page's words need: a row selected (a command or a test hook to select an Activity row) and an agent's robot rows.
- steering: good in round 1. `scene.open` with `force` after the placements gives the toast "A command script discarded unsaved changes" with **Show in Activity** and **Recover...**; caption and alt say a command script, where the page's agent would be named.
- regression: good in round 2 (same layout change as activity). `editor.activity.export` to `Regression/Props.json` is its own row after the three placements.
- activity and regression, retake (2026-11-18): the viewer saw 516 × 200 pictures with the placement rows scrolled out; that take predates the 340 px layout. Retaken with `layouts/make-with-an-agent-activity.ini`, recipes unchanged: 596 × 340, activity shows the four `asset.place` rows (Crate, Barrel, Lamp, Lamp (1)), `edit.undo` and the take's three rows (17 of 17); regression shows `entity.delete`, the three placements, `editor.activity.export` and the take's three rows (16 of 16).
- tetris: good in round 1. Project changed to `{sample: "Tetris"}`, `camera.focus` on Well; the edit-mode scene shows the well and the Next box, no pieces (pieces come in play). Alt rewritten to that; "a score at its side" was not in the picture.
- Pin v0.8.0 (319075e3, 2026-11-23), one hold, all eight taken with the pin's Release build, recipes unchanged:
  - result: compared with its published file (0 of 1 differ, largest difference 0); the original is the same bytes, so publish keeps it (`unchanged`, stamp still names 822a7a46).
  - placed, activity, steering, regression, tetris: published in round 1. placed shows the three props in the Scene view (the main camera's frustum lines cross it) and Crate, Barrel, Lamp in blue in the Hierarchy; activity shows the four placements, the undo and the take's three rows (17 of 17); steering the toast "A command script discarded unsaved changes" with **Show in Activity** and **Recover...**; regression the three placements, the export row and the take's three rows (16 of 16); tetris the well, the Next box and the rows Well and Board (status bar: "Scripts not built").
  - connected: still cannot. The status bar pill reads **Automation off**; no take connects a client. Not published; nearest honest picture as above (a diagram of agent, `StrataCLI mcp` and editor).
  - toolsets: still cannot. The Activity rows are the command script's (scroll icons), and the visible ones are mostly the take's own (`editor.showPanel`, `editor.wait`, `editor.screenshot`); no toolset shows. Not published; proposal as above.
- Last round (2026-11-24, pin v0.8.0 319075e3, the tool's new `automation` field):
  - connected: published in round 1. The recipe now has `automation: {client: "claude-code"}` and ends with `editor.status` (the question of the section's last step): StrataCLI mcp sends every step. The picture shows the pill **Agent connected · claude-code**, the Scene view's chip **Agent: entity.delete · now** (the latest edit: the prefab steps, a stand-in for the starting checkpoint, are the agent's here) and robot rows in Activity (`prefab.create`, `entity.delete`, `editor.status`, `editor.screenshot`, 13 of 13). Caption and alt say that; the old caption's "waits for its first command" was not true of a take that makes the checkpoint through the agent.
  - toolsets: blocked, drawn stand-in `toolsets-drawing` placed in its place. Toolsets live in `StrataCLI mcp` (`StrataCLI/src/CLI/McpToolsets.cpp`), not in the editor: no window shows which are enabled, and `strata_describe` and `strata_toolsets` run no command, so an agent client's take adds no row for them. The drawing shows the tools at the start (core, 27 commands, and the five generic tools, at most 32), the other twelve toolsets of the pin, `strata_toolsets {"enable": ["scene"]}` bringing scene (with `asset.place`) in, and `strata_call` reaching every command. The recipe stays as the request for a later edition (a picture of the agent program's own tool list).
  - Page words: the size limit (6,500) was passed by the drawing's caption; "What you need" lost the installer clause and the MCP client's long form, and the placed and tetris captions were shortened.

## Tutorial run

- 2026-11-18, round 3: the tutorial and exercise 1 pass at the pin (Release build), stamped. Round 1 failed on the runner's own guess (`editor.status`'s `scene.scene` is a handle; the name is `scene.name`).
- Strengthened with the page's values: stage 1 `editor.status` (project and scene named); stage 3 the `editor.activity` marker and `scene.hierarchy` (Crate, Barrel, Lamp, each named after its prefab: verified); stage 4 `editor.activity` by source Automation and the first `asset.place` entry (parameters `asset`, `point`; result with `placedOn`, `point`, `bounds`: verified), then the hierarchy back at 8 entities after the undo; stage 5 `editor.status` (no unread errors); stage 6 the export without the reader's `since` (14 steps and edits from the session's start, none outside commands); exercise 1 the hierarchy at 8 entities before and after.
- What the run cannot take: stage 4's `editor.showPanel` (fails in a `--no-gpu` editor), the client name (a run's rows name `StrataCLI`, not an agent), and a number noted in stage 3 used in stages 4 and 6 (binds do not cross stages). Stage 5's refused `scene.open`, forced open and `scene.recover`: the runner saves the scene at every stage start, and no step can expect a failing answer. Stage 6's script edit, copy and replay run outside the editor. Stage 7 opens a sample (the chain starts from a template).
- Page mended: section five's "not saved yet" was false for a reader starting from the stage 4 download (saved): one sentence says to place one more prop first.
- 2026-11-23, pin v0.8.0 (319075e3), round 1: the tutorial (7 stages) and exercise 1 pass as written with the pin's Release build; restamped, stage zips rewritten. Nothing mended.
- 2026-11-24, final run (process step 15): the pin-build run was still current (`check --release` asked only for the package); the tutorial (7 stages) and exercise 1 pass as written with the official v0.8.0 package (Strata-0.8.0-windows-x64.zip), round 1; `check --release` finds nothing. Nothing mended.

## Engine

- None found: every command the run used did what its description says.

## Settled with the editor (2026-11-18)

- `toolsets`: caption and alt no longer name a robot icon; a row's icon is its source's (`ActivityPanel.cpp`: Bot, MousePointer, ScrollText), and a take runs as a command script. The page's robot icons, agent chip, **Agent connected** pill and `claude-code` toast stay: they are what a reader with a connected agent sees (`EditorLayer.cpp`, `EditorContext.cpp`).
- `connected`: left. No take can connect a client, so the picture cannot show the pill; the figure stays unpublished until the figure tool can connect one.
- `activity`, `steering`, `tetris`: the captions already say what the takes show; the page's steps stand.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package in a headless editor (`docs-work/walkfix-G10`, `verify.py`, `results-all.json`):
  `editor.showPanel` fails without a window; `play.step` on a playing game fails with "Stepping needs a paused running
  scene (play.pause)"; in Windows PowerShell 5.1 `call play.step "{\"steps\": 60}"` exits 3, and the `echo '<json>' |
  StrataCLI call <method> -` form works for `play.pause`, `play.step` and `editor.activity`; the export after the
  session's marker writes 6 steps (four `asset.place`, `edit.undo`, the forced `scene.open`), `bindings` 0 and the
  `scene.recover` warning; `scene.recover` applies with the entry's `id` and with its `scene`.
- Page mended: a reader without an agent runs the command tabs; the activity, `play.step` and pause calls use standard
  input; `editor.showPanel` without a window; the recovery entry's `id` named; the bind sentence says when the export
  binds, and no longer asks to keep a bind. Cuts to stay within size L: the capture's `renderer` sentence, the
  window-size sentence, shorter closing paragraph.
