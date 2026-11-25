# Brief: `make/automated-playtests`

| Field | Value |
| --- | --- |
| Title | Automated play-tests |
| Kind | H |
| Size | L |
| Tracks | G |
| Needs | `make/menus`, `basics/tools`\|`start/install` |
| From | gamedev "Automated play-tests and AI agents" (the play-test half: §1.17, concept 23); editor-core "Scripting the editor: command scripts, batches, record and replay" (use side); audio-input "Letting tools play: simulated input" (use side); JSON as a reader writes it: objects, arrays, strings, numbers, quotes and commas, and the editor's message for a broken file; command scripts with `play.step`, `input.sequence`, `expect`, `until` and `bind`, run with `StrataEditor --commands <file>` (in PowerShell with `\| Write-Output`, so that it waits); what a replay script is, and the Activity panel's **Copy as script**; turning a session into a regression test is `make/with-an-agent`'s (G15); gameui "Testing and automating game UI" (use side: `ui.create`, `ui.layout`, `ui.hitTest`, `input.click`); use home of simulated input, command scripts, record and replay |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/automated-playtests` — Automated play-tests

**Covers.** The goal: a play-test the editor runs by itself, which fails when a change breaks the game. What must be
true first: a terminal (`start/install`), a copy of the Tetris sample, and the menus of `make/menus` for the UI section.
The order. Why a script: a person cannot repeat a play-test exactly, a script can (the testing loop: build, play,
simulated input, observe, check, run again). JSON as the reader writes it, from zero: objects, arrays, strings, numbers,
`true` and `false`, quotes and commas, and the editor's message for a broken file. A command script: a list of steps,
each a `command` with its `parameters`; the first one starts play, reads the score's text and stops; it runs with
`StrataEditor --project <dir> --commands test.json --quit-after-commands` (on Windows piped to `Write-Output`, so that
PowerShell waits), and its exit code says passed (0) or failed (1). `expect` on a result: `equals`, `min` and `max` at a
JSON pointer such as `/values/Text`. Exact play: `play.start {paused: true}`, `play.step {steps}`, simulated keys and
actions held for a number of fixed steps, `input.sequence` with events at given steps, and why the same steps give the
same game on any computer (seeds, fixed steps, paused waits; a call takes about a tenth of a second and the steps per
frame differ between machines). `until` for an outcome that takes game time; `bind` and `$ref` for an ID a step returns.
The Tetris regression as the model (the excerpt): fields set so that time cannot move the pieces, an `input.sequence` of
26 steps, an exact score of 209; the excerpt ends there (line 24), because the sample's script then waits 300 frames for
game over, which the book's scripts never do (the erratum below): they wait with `until`. What a test can read:
`editor.status` errors, `log.read`, `component.get`, `script.get` (fields, live), `physics.stats`, `audio.state`,
`input.state`, and `viewport.capture` of a picture at a fixed step for a person to look at. Game UI tested without eyes:
`ui.create` builds a menu in one undo step, `ui.layout` gives every rect at 1280 x 720 and 2560 x 1440 without drawing,
`ui.hitTest` names what lies under a point, `input.click` presses a button in play. Record and replay: every command,
also those the person's clicks in menus and panels run, lands in the activity journal; the Activity panel's **Copy as
script** turns one entry into a step; what a replay script is: a session's commands as a script whose later steps refer
to earlier results through `bind` and `$ref`; turning a session into a regression test is `make/with-an-agent`'s (G15),
linked. What Strata does not do here: an exported game runs no command script. Result: a test file that fails when the
score rule changes. Variations: a smoke test of the reader's own game (build, play, a few steps, no errors in
`editor.status`) modeled on the engine's smoke script; a physics play-test that pauses and waits with `until` (the
Physics Playground's pattern); a test of a game's audio (`audio.state`). The exercise: the Tetris test made to fail by
one changed field, and its failing `expect` read.

**Leaves out.**

- Running commands from outside a running editor with StrataCLI → `make/commands`
- Exporting a whole session as a replay script and running it on a copy → `make/with-an-agent`
- How command scripts, batches and the replay export are built → `editor/command-scripts`, `editor/journal`
- How simulated input merges with the real devices → `input/simulated`
- Stepping a paused game as the editor does it → `editor/stepping`
- How UI layout and hit tests work → `ui/layout`, `ui/input`
- Tests of the engine itself → `engineering/testing`

**Fit.** `fits`: about 4,500 words against L (5,000): JSON from zero, the command script's parts, exact play with its
reasons, the Tetris excerpt, the UI tests and record and replay, each with its steps, take the most; the three
variations and the exercise take about 500.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:224` | feature | home | Simulated input: `input.key`, `mouseButton`, `mouseMove`, `scroll`, `click`, `type`, `gamepadButton`, `gamepadAxis`, `action`, `releaseAll`, `state`; durations in fixed steps |
| `gamedev:225` | feature | home | Deterministic sequences: `input.sequence {steps, events, observe}`, `play.step` answering after its steps, `play.start {paused}` |
| `gamedev:226` | feature | home | Viewport capture with its camera, size, debug view, quality and fixed step; it waits for assets |
| `gamedev:227` | feature | home | Command scripts and expectations: `--commands` and `--quit-after-commands`, `expect`, `until`, `bind` and `$ref`, exit code 1 on failure |
| `gamedev:228` | feature | home | What a replay script is: the journal turned into a command script with bindings; the export and the regression test made from it are `make/with-an-agent`'s (G15) |
| `gamedev:230` | feature | home | What a test reads: `editor.status` errors, `log.read`, `script.status`, `component.get`, `entity.get`, `physics.stats`, `animation.info` |
| `gamedev:346` | concept | home | Testing a game: determinism, observability, automated play-tests, regression scripts; the mistake of timing-dependent checks |
| `gamedev:375` | code | home | `StrataTests/Editor/TetrisCommands.json.in:1-24`: `expect`, `script.setField` that takes timing out, `ui.layout` at two resolutions, an `input.sequence` of 26 steps and the exact score 209 |
| `gamedev:431` | figure | home | The testing loop: script, build, play, simulated input, observe, regression script |
| `gamedev:516` | rule | home | Deterministic play-tests: seeds, input durations in fixed steps, `input.sequence`, paused `until` waits |
| `gamedev:655` | term | home | Command, command script, expect, until, bind |
| `gamedev:656` | term | home | Simulated input, input sequence |
| `gamedev:657` | term | home | Viewport capture |
| `gamedev:658` | term | home | Activity journal, replay |
| `gameui:214` | feature | home | `ui.create` (presets in one transaction, a canvas when needed, anchor presets), `ui.layout` (rects at any screen without rendering), `ui.hitTest` |
| `gameui:384` | concept | home | Testing UI headlessly: simulated input, layout without rendering, hit tests; agents build UI through commands |
| `gameui:586` | hands-on | home | A menu built with `ui.create` and checked with `ui.hitTest` and `input.click` in play |
| `physics:456` | hands-on | home | Variation: a script that pauses, steps to a fixed step and checks an outcome with `until`, as the Playground's regression |
| `build-test:598` | hands-on | home | Variation: a smoke test of the reader's game modeled on `SmokeCommands.json.in`, run with `--commands` and `--quit-after-commands`; why PowerShell needs the pipe (the page writes `\| Write-Output`, as `start/install` taught) |
| `audio-input:573` | hands-on | home | Playing a game by commands (`input.key {steps}`, `input.action`), reading `audio.state` and `input.state`, an `input.sequence` that gives the same result at different frame rates |
| `new:5` | not-done | home | Automating an exported game: command scripts, simulated input and expectations run in the editor only. Evidence: `Docs/Roadmap.md:1697`; `Docs/Releases/0.7.0.md:414` |
| `new:20` | erratum | home | `StrataTests/Editor/TetrisCommands.json.in:28`, the Tetris sample's command script, waits 300 frames (`editor.wait {frames}`) before it reads game over: the page's excerpt ends at line 24, its own scripts wait with `until` in fixed steps, and it never shows the sample's wait as a model. Evidence: `StrataTests/Editor/TetrisCommands.json.in:28`; `AGENTS.md:117-118` (tests wait by the clock or a condition, never frames) |
| `new:24` | hands-on | home | Exercise, done with a command script: the Tetris test's `LinesPerLevel` step set to 2 and the test run again; it fails with exit code 1, and the reader finds in its output which `expect` failed and why. Evidence: `StrataTests/Editor/TetrisCommands.json.in:5` (`LinesPerLevel` 1), `:22-24` (the lines, score and level expected) |
| `editor-core:222-226` | feature | use | Pause and step, `play.start {paused}`, `play.step {steps, wait}`, the editor's simulated input |
| `editor-core:240` | feature | use | The command script format with `expect`, `bind`, `$ref` and `until` (home `editor/command-scripts`) |
| `editor-core:359` | concept | use | Scripts of commands, record and replay (the replay as a regression test is `make/with-an-agent`'s) |
| `editor-core:450` | code | use | The engine's smoke script, the model of the smoke-test variation (home `editor/command-scripts`) |
| `editor-core:535` | figure | use | A command script's run in the terminal with its exit code |
| `editor-core:580` | rule | use | Tools count game time in fixed steps, never frames |
| `editor-core:615` | hands-on | use | A first command script, run headless |
| `editor-core:662-665` | term | link | Command script, `expect`, `bind` and `$ref`, `until` |
| `audio-input:136`, `audio-input:164` | feature | use | The virtual devices; simulated actions |
| `audio-input:357` | concept | use | Simulated input, determinism and fixed steps |
| `audio-input:464` | figure | use | Simulated holds counted in fixed steps |
| `audio-input:521` | rule | link | Durations of simulated input count fixed steps, and while a running game updates at time scale 0 its frames too (the input step count, `StrataEditor/src/Editor/EditorContext.h:349-352`): linked to `editor/stepping`, which teaches it |
| `audio-input:98` | feature | use | `audio.state` |
| `physics:172` | feature | use | `physics.stats` |
| `automation:157` | feature | use | Command scripts, the same format `editor.batch` and the export use |
| `automation:176` | feature | use | The Activity panel's **Copy as script** |
| `automation:666` | hands-on | home | A deterministic play-test: paused, an `input.sequence` with observations, checks on its samples |
| `automation:444` | concept | use | Determinism for agents and tests |
| `gamedev:229` | feature | link | The samples' regressions run by CTest (home `engineering/test-kinds`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| A terminal: running a program with arguments, quoting a path, `\| Write-Output` on Windows | `start/install` | must |
| Reading a command and its JSON result | `start/how-to-read` | must |
| Opening a copy of a sample | `start/first-game` | must |
| Play, pause and step; "same inputs, same game" | `make/play-test-debug` | must |
| Fixed steps and the frame | `make/script-loop` | must |
| Script fields | `make/first-script` | must |
| Input actions | `make/input` | must |
| UI canvases, texts and buttons | `make/hud` | must |
| Menus, buttons and their events | `make/menus` | must |
| Random numbers and seeds | `make/recipes` | helps |

**Starting state.** A copy of the Tetris sample made with File ▸ Open Sample (its scene's entity IDs are those of the
sample, so the page's script names them), and the end checkpoint of `make/menus`, downloadable, for the UI section.

**Command-only steps.**

- Every step of the page that runs a test: the reader writes a command script and runs it with `StrataEditor --project
  <dir> --commands <file> --quit-after-commands`; no menu or button runs a command script. The page is track G's
  teacher of running a command script (R33, D20), so these steps need no `make/commands`.
- The commands inside the scripts (`play.start`, `play.step`, `input.sequence`, `component.get`, `script.setField`,
  `ui.create`, `ui.layout`, `ui.hitTest`, `input.click`, `viewport.capture`), which the scripts run, not the reader.
- The export of a whole session (`editor.activity.export`) needs StrataCLI and a running editor: moved to
  `make/with-an-agent` (process.md, "Allocation and part briefs"); this page uses **Copy as script** in the Activity
  panel instead.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `viewport-capture` | Viewport capture | - |
| `replay` | Replay (use) | - |
| `simulated-input` | Simulated input (use) | virtual device |
| `command` | Command (use) | - |
| `input-sequence` | Input sequence (use) | - |
| `command-script` | Command script (use) | - |
| `activity-journal` | Activity journal (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-b2-5 | should | missing-item | `make/automated-playtests` (`gamedev:375`, `gameui:586`, `new:24`) | The excerpt's `script.setField` steps (lines 5 and 6) run in Edit mode, so they edit the copy's scene: each is an undo step, and the scene stays modified; the UI section's `ui.create` does the same. With `--quit-after-commands` the editor closes without asking, and the unsaved changes are written as recovery data, which the editor offers the next time the reader opens the copy. The sample's script undoes its edits and checks that the scene is unmodified (lines 38 to 41); the excerpt ends at line 24. | The page's scripts end as the sample's does: `play.stop`, one `edit.undo` per edit, and `scene.info` expecting `/modified` false, quoted as a second short excerpt (lines 38-41) with one sentence why. About 80 words. This is critic-make-c-4's point on the page that teaches command scripts; `make/project-tetris` then links it. The recovery offer was read in the code, not run. | `allocation/make-b2.md:682-684`, `:723`, `:730-732`; `allocation/completeness/make-c.md:10` (critic-make-c-4); pin: `StrataTests/Editor/TetrisCommands.json.in:4-6`, `:38-41`; `StrataEditor/src/Editor/EditorScriptCommands.cpp:635-637`; `StrataEditor/src/EditorLayer.cpp:549-571`; `StrataEditor/src/Editor/EditorContext.cpp:692-696` (unsaved changes written as recovery data when the scene goes, closing included), `:410-414` (offered when the project opens) |
| critic-make-b2-6 | should | missing-item | `make/automated-playtests` (the smoke-test variation `build-test:598`, the exercise, the UI section) | Every command takes an entity by its ID, up to 16 hexadecimal digits, and the page's script uses the sample's fixed IDs. No page of track G says what such an ID is in a command, or where readers find the IDs of their own game: the Inspector's Copy ID button, or `entity.find {name}` with `bind`. The IDs are stable once the scene is saved, and a copy keeps the sample's. | A paragraph in the command-script section: what the ID is, the Inspector's Copy ID button, `entity.find` with a `bind` of `/entities/0`, and why the sample's IDs still name the copy's entities. About 100 words, with a `use` row of the command. critic-make-c-5 asks to teach `entity.find` on `make/project-tetris`; this page comes first and its own variations need it (forPlanner). | `allocation/make-b2.md:734`, `:774`; `allocation/completeness/make-c.md:11` (critic-make-c-5); pin: `StrataEditor/src/Panels/InspectorPanel.cpp:564`; `StrataEditor/src/Editor/CommandUtils.cpp:71-74`; `StrataEditor/src/Editor/Commands/EntityCommands.cpp:401-411`; `StrataTests/Editor/ThirdPersonCommands.json.in:8`; `.claude/skills/strata-make-a-game/SKILL.md:422` |
| critic-make-b2-7 | should | missing-item | `make/automated-playtests` (the first run; Command-only steps) | The line `StrataEditor --project <dir> --commands test.json --quit-after-commands` names three places: the program, the project and the script. `--project` and `--commands` are read from the terminal's current folder, while `start/install` taught only a program run from its own folder. The test's editor also opens the project from disk, so what the reader has not saved in the open editor is not tested. | The first run step gives the line in OS tabs, with the program's full path in quotes and the terminal in the project's folder (`--project .`, `--commands test.json`); its "If you do not see it" names the message "Cannot read 'test.json'" and "save in the editor first". About 80 words. | `allocation/make-b2.md:675-677`, `:779-781`; `allocation/start.md:153`; pin: `StrataEditor/src/EditorApplication.cpp:65-67`, `:292-297`; `StrataEditor/src/Editor/EditorCommandRunner.cpp:561-567`; `StrataEditor/src/EditorLayer.cpp:459-467` |
| critic-make-b2-15 | should | shape | `make/samples` (Covers; the variation "reading a sample's regression script"); `make/automated-playtests` (the smoke-test variation) | The samples' regression scripts live in `StrataTests/Editor/`, which the release archive does not ship: it installs the programs, the samples, the SDK, the manual and the skills. The READMEs name those files, the page says each regression is a command script of the engine's tests, and its variation has the reader read one that the reader does not have. | The variation reads a part the page quotes (for example the Physics Playground's paused `until` steps), or the book offers the file among the page's downloads; the sentence on regressions says they are in the engine's repository, not in the archive. `make/automated-playtests` quotes what its smoke-test variation models in the same way. About 40 words. | `allocation/make-b2.md:986-987`, `:999`, `:734`; pin: `CMake/StrataPackaging.cmake:55-85`; `Samples/PhysicsPlayground/README.md:54`; `Samples/OpenWorld/README.md:58`; `Samples/Tetris/README.md:41`; `Samples/ThirdPerson/README.md:72` |
| critic-make-b2-20 | could | thin-home | `make/automated-playtests` (`gamedev:227`, `gamedev:516`) | Two limits that a reader meets when testing their own game are not listed. `expect` compares with constants only, so a relative check (moved 3 m) needs a script field that computes it. `until` needs an `expect` and gives up after its `steps` or `seconds` (300 s by default). | One sentence each in the `expect` and `until` steps. About 50 words. | `allocation/make-b2.md:677-681`; pin: `StrataEditor/src/Editor/EditorCommandRunner.cpp:157-183`, `:472-476`; `StrataEditor/src/Editor/EditorCommandRunner.h:135`; `.claude/skills/strata-make-a-game/SKILL.md:424-429` |
| critic-make-b2-24 | could | wrong-home | `make/automated-playtests` (`gamedev:658`); `make/with-an-agent` | The term "activity journal, replay" is homed on `make/automated-playtests`, which first shows the journal and Copy as script. book.md's one-home row of the activity journal names `make/with-an-agent` as its use page, and the outline calls that page the use home of the activity journal, so the glossary step would find two answers. | One of two changes (forPlanner): book.md's row names `make/automated-playtests`, the earlier page where the reader meets the journal, and `make/with-an-agent` keeps its feature rows; or the term row moves to `make/with-an-agent`, and `make/automated-playtests` says in one sentence what the journal is. No words added. | `allocation/make-b2.md:689-691`, `:729`, `:924`; `book.md:360`; `outline-1.md:219`, `:221` |
