# Walk G-final-10: track G (game maker, G0), segment 10

Entries walked, in order: `make/large-worlds`, `make/performance`, `make/automated-playtests`, `make/commands`,
`make/with-an-agent`, `make/samples`. Package: Strata 0.8.0 Windows x64 (official archive); book built at
127.0.0.1:4329, "Checked against Strata 0.8.0 at commit 319075e3". Work folder:
`G:/GameEngineAI/.worktrees/docs-work/walk-G-final-10/` (projects, logs `lw1.log`, `pf.log`, `pt.log`, `cm.log`, `ag.log`,
`sm.log`, `f-*.log`, `f3.log`; scripts in `tools/`).

How it was walked. No screen: every step was done through its command tab with StrataCLI against an editor started with
`StrataCLI launch --headless`, or with `StrataEditor --commands ... --no-gpu`, under the perf lock. Every "In the editor"
picture, panel, chip, toast and tooltip is therefore not compared (see the end). Starting points were the stage downloads of
each page (large-worlds stage-1, performance stage-1, with-an-agent stage-1); for `make/commands` the last stage zips of Coin
Run (stage 4), Animation (stage 9) and the large-worlds project. What is not listed below matched its "You should see": world.info
four layers, world.status counts, world.cook numbers, the teleport end position, the three perf logs, the Tetris play-test
(score 209, the failing "Score: 210" line, the Basic exercise answer), ui.hitTest and input.click, the smoke test, the atomic
editor.batch failing at step 2, the scatter as one undo step with undo and redo, exit codes 1 and 3, viewport.capture
--save-image, animation.info, 32 MCP tools at first and 67 after enabling `scene`.

## Entries

WK1. make/large-worlds, "What you need" and the stage download. Kind: did not match. The section lists a loading scene first
and says "the first stage's command file makes" the four parts. The only download is Checkpoint 1 (stage-1.zip); it holds the
Meadow world, prefabs and Teleport.cpp, but no loading scene, and the section names no starting download. I used stage-1. The
export step later says "with your loading scene as the start"; the project has none (the export itself worked).

WK2. make/large-worlds, "Fill the cells", read the cell of a tile and "Push the Rock over a cell border". Kind: guessed. The
command tabs cannot show an entity's cell (the page says so for world.status; entity.get has no cell either). I never saw "Cell:
Terrain (0, 0)" or the change to (1, -1); I only moved the Rock with component.set and trusted the cell count after the save
(world.info: Terrain 5 cells, Props 4).

WK3. make/large-worlds, "See the cells stream", pin a far cell. Kind: did not match. world.loadCells for Terrain (0, 0) after
the save answered state Loaded with `"entities": 0`, although that cell holds a Tile. The page does not say what the number
counts, so I could not tell whether the answer was right.

WK4. make/large-worlds, "Teleport without falling", "Take the prefetch away". Kind: left the book. I did not edit Teleport.cpp
and rebuild to see the ball fall, and did not read the script's ReachRadius field after script.add (the call answered exit 0).
The prefetching version worked: the ball stood at 608, 0.93, 608 a moment after input.action.

WK5. make/large-worlds, Exercises, Basic. Kind: did not match. With the ball's Streaming Source Radius at 100, world.status
stayed at 7 loaded and 7 wanted, the same as with Radius 0, because all seven cells of this world lie within 100 m of the ball.
The answer says fewer cells load around the ball; with this project's content they do not.

WK6. make/performance, "What you need". Kind: did not match. "Download the starting checkpoint": the only download is
Checkpoint 1, and it already holds the Field entity with FieldSpawner attached, and the Hut. Then "Create an empty entity named
Field and attach the script": script.add answered exit 1 "'Field' already has the script FieldSpawner".

WK7. make/performance, "Spawn the field and read the Stats chip" (hut step) and "Watch streaming". Kind: did not match. The
command tabs say to read `renderStats.occludedProxies` and `renderStats.pendingAssets` from editor.perf. In my headless editor,
while the game played, `renderStats` and `gameRenderStats` were `null`, so I never saw an occluded count. gpu.boundBy read
"unknown" at first, then "capped".

WK8. make/performance, "Make the field cheaper", switch shadows off. Kind: guessed. The command tab asks for "the innermost
rock_largeA id". entity.find returns two ids with that name and the page does not say which one is inner. The first had no
MeshRenderer (exit 1, "has no MeshRenderer component"); the second took CastShadows false.

WK9. make/automated-playtests, "Make a copy of Tetris, then close the editor". Kind: guessed. The command tab says run
project.openSample, then "close the editor", with no command named for closing and no word on which editor makes the first call
(a project must already be open). I opened the large-worlds project, called project.openSample and then editor.quit (a name I
know from make/commands, a later page).

WK10. make/automated-playtests, "Run the script". Kind: left the book. I did not use the page's PowerShell line
(`& StrataEditor.exe ... | Write-Output`, `$LASTEXITCODE`); I started the editor from a script with its output redirected, and my
exit-code capture came back empty. Pass or fail I read from "Command script finished (N commands)" against "... finished with
errors" (11 commands on pass; errors on the "Score: 210" file); I never saw the codes 0 and 1. The first run also logs a warning
"scripts of 'Tetris' are not built yet" and builds for 5 s, which the "You should see" does not mention.

WK11. make/commands, "Do what no menu can", scatter. Kind: left the book. "Download scatter.json of the book": there is no link on
the page (only the exercise solution zip is offered). I could not write 200 entries by hand, so I generated the file with a loop
of my own in PowerShell, which G0 cannot do. The projects that later steps name (Coin Run end checkpoint, Animation, Large worlds,
the Reflections courtyard, the GI room) are not linked from the page either; I looked up the last stage zip of the Coin Run,
Animation and Large worlds pages.

WK12. make/commands, "Change a world's layers". Kind: failed. `{ "world": "Worlds/Meadow", "layers": [...] }` as printed answers
exit 1 "Parameter 'world': no asset 'Worlds/Meadow'". world.info on the same project works with "Worlds/Meadow.stworld". I did not
retry setLayers with the extension, so the five-layer result is unseen.

WK13. make/commands, "List the commands". Kind: did not match. "About 156 lines": StrataCLI list printed 161 lines.

WK14. make/commands, "Do what no menu can" (controller, preview, probes). Kind: left the book. I ran animation.info (clips Dance,
Death, Idle and more came back) but not animation.createController, animation.preview or lighting.bakeProbes (the last needs the
Reflections and GI projects, which I did not fetch).

WK15. make/with-an-agent, whole page. Kind: left the book. Claude Code is not installed here and needs a paid plan, so I did not
run `claude mcp add`, the agent's prompts or the skills copy. I did the command tabs by hand and spoke MCP over stdin to
`StrataCLI mcp`: initialize and tools/list gave 32 tools (27 + 5); strata_toolsets {"enable":["scene"]} gave 67 tools.

WK16. make/with-an-agent, "Read the Activity panel and undo". Kind: did not match. `editor.showPanel` {"panel":"Activity"}
answered exit 1 "This editor runs without a window: it has no panels to show". I had started the editor with --headless (my
choice; the page's launch line has no such option).

WK17. make/with-an-agent, "Keep the session as a test". Kind: did not match. editor.activity.export (since 0) wrote 7 steps with
`bindings: 0`, and the file holds no `bind` on any asset.place step, while the page says "Keep the rest of each step as the export
wrote it, including its bind". I did not add the expects or delete scene.open; I ran the raw export on the copy (the log said
finished, 7 commands; the closing scene.open left a scene with no props).

WK18. make/with-an-agent, "Bring the props back". Kind: guessed. `"scene": "<id from the list>"`: each scene.recoveryStatus entry
has both an `id` ("767B...-6E07...") and a `scene` ("767B..."). I guessed `id`, which applied. The `scene` value failed with
"cannot be applied: the scene file changed after these changes were made".

WK19. make/with-an-agent, "Ask the agent to describe how Tetris was made" and the activity steps (Windows PowerShell 5.1).
Kind: failed. `StrataCLI call play.step "{\"steps\": 60}"` (no Windows note on this one) answered exit 3 "'call' expects <method>
[params-json | - | @file]", as did the same form for editor.activity. Also play.step on a game that is playing answers "Stepping
needs a paused running scene (play.pause)"; the page calls 60 steps "a good unit for a check" without pausing first.

WK20. make/samples, Physics Playground, "Change one thing". Kind: guessed. The command tab has `"entity": "<the entity's id>"` and
the editor tab says to search the Hierarchy; no command or name is given. entity.find {"name":"Playground"} is empty; the entity is
called Game (I found that by reading the package's scene file, which G0 would not do). After that script.setField worked, and 600
paused steps gave DominoesDown 44.

WK21. make/samples, Open World then Outpost. Kind: did not match. After setting TourOnStart in the Open World copy (edit mode) the
scene was modified, and project.openSample "Showcase" answered exit 1 "scene 'Island' has unsaved changes, which opening the
sample would discard". The page runs on in that order and says nothing about saving first in the command tab.

WK22. make/samples, "about 260 MB of free disk for the three copies". Kind: did not match. After openSample and script.build the
Open World copy measured 188 MB and the Playground 88 MB (with `.strata`); the page says the Open World copy is "about 90 MB" (the
package folder is 92 MB; the copy grows once it builds and imports).

## Not walked, and why

- All "In the editor" tabs and every picture: no screen (strip, Inspector cell line, Cells chip, Streaming panel, Stats chip,
  Performance panel, Activity panel, toasts, launcher card, photo mode, Ctrl+P play of the samples, "Bodies: 615").
- make/large-worlds: dragging in the editor; `world.create` and the Make the world steps were covered by the stage-1 download.
- make/performance: the ten-material and 500-character exercises; the vsync variation; the spreadsheet chart (the three logs were
  read with awk: 600 rows each, GPUBusyMs 0.23 on Low and 0.39 on Ultra, game exit 0).
- make/automated-playtests: the audio and physics variations; the Medium exercise ran (14 commands, no error).
- make/commands: exit code 2 (no editor), controller, preview and probes (WK14).
- make/with-an-agent: the agent itself (WK15) and the last section's whole-game prompt.

## Answers

Checks were run with the official 0.8.0 package under the perf lock, in `docs-work/walkfix-G10`: one headless editor with
the GPU (`verify.py`, results in `results-all.json`, `results-pf2-ow.json` and `results-rf.json`, projects in `run/`,
made from the checkpoint zips of `large-worlds` 1 and 7, `performance` 1, `animation` 9 and `with-an-agent` 1 and the
result downloads of `reflections` and `gi`), and the page's PowerShell line of `make/automated-playtests`
(`tetris.ps1`, `tetris.out`). The changed tutorial files were run with the pin build and with the package (`runs/`):
`large-worlds` (7 stages and exercise 1) passed with both; `commands` exercise 1 failed with both in the chain it starts
from, `make/project-coin-run` stage 3 (`log.read`: no message "script 'BallControl' has no field 'Speed'" among the
newest 50), before its own stage ran: that is the chain's runner's, and `make/input`, which the warning comes from, is
being changed in this worktree now. The log lists no patches under "## Built by the integrator". No
engine fault was found beyond the one the notes of `make/large-worlds` already hold under "## Engine" (the cells'
`entities` count, WK3).

### WK1
- Fixed on `make/large-worlds` and its tutorial file. Why: "What you need" asked for the loading scene of
  `make/levels-saves`, which no download holds, and named no start. The export also had a fault the walker could not
  see: the project's start scene stayed the template's `Scenes/Main` (`project.settings` at stage 7), so the exported
  game would start without the world.
- Change: the first item names a Basic 3D project with the four parts, or Checkpoint 1 at the end of "Make the world"
  (its project, or its commands on a project of your own), and says that a loading scene is welcome but not needed. The
  export section starts with a new step, **File ▸ Set as Start Scene** with `Worlds/Meadow` open
  (`project.setStartScene`); its "Why" names **Loading Scene** for a reader who has one, and the export's "You should
  see" no longer promises a loading scene. Stage 7 runs `project.setStartScene` (checked: the start scene became
  Meadow's handle).

### WK2
- Fixed on `make/large-worlds` and its tutorial file. Why: no command tells an entity's cell (`entity.get` with `world`
  answers `active, bounds, children, components, id, name, parent, world`), and the tab said only that.
- Change: "read the cell of a tile" says that commands read the cells instead, from the tile's position and, after the
  save, from `world.status` with `cells`, and names the four Terrain cells; the Rock's step names the Props cell
  (1, -1) that the list then holds, beside (0, -1) and (-1, 0). The save step's tab runs `world.status {cells: true}`
  and names the seven cells it lists (checked: Terrain (0, 0), (-1, -1), (0, -1), (-1, 0); Props (0, -1), (-1, 0),
  (1, -1)). Stage 3 checks the list's 7 cells.

### WK3
- Fixed on `make/large-worlds` and its tutorial file. Why: `entities` counts what loading the cell's file created
  (`WorldStreamer.h:60`, under "## Engine" in the notes already); a cell made in the session stays loaded with the
  entities you made, so it reads 0. Checked: `world.loadCells` after the save gave 0; after `scene.open` of Meadow it
  gave 1, and `world.status` gave 1 for each Terrain cell and 3 for each Props cell.
- Change: the pin step's tab adds `"wait": true` and says what `entities` counts, why it reads 0 and that opening the
  scene again gives 1. Stage 3 opens the scene again and checks `entities` 1.

### WK4
- Fixed on `make/large-worlds` and its tutorial file. Why: "Take the prefetch away" had never run (the notes' "Not
  run"), and its "You should see" is false: with the prefetch removed as the page says, the ball still lands at 608,
  0.5, 608 (`lw7-noprefetch-track`), because the ball is the streaming source and the island's two small cells load
  before it has fallen half a meter. The tab of "Attach the Teleport script" also gave no way to read `ReachRadius`.
- Change: the attach step's tab adds `script.get` (checked: `ReachRadius` 48). Step 5 gives the two lines to add and
  where, the commands that play and read the ball, and what the reader sees: the ball lands anyway, because the cells
  won a race. Its "Why" names what loses the race (a fuller cell, a mesh collider that still builds, a player that is no
  source) and says that the prefetch turns the race into a wait. The trap's sentence in "Why a level streams" says the
  ground may not be there. Stage 6 now runs the step: `TeleportNoPrefetch.cpp` (new), build, play, the action, the ball
  at 608, 0.5, 608, then `Teleport.cpp` back and a build.

### WK5
- Fixed on `make/large-worlds`. Why: with a Radius of 100 every one of the seven cells lies within 64 m of the ball, so
  nothing changes (checked: 7 wanted and loaded at 0 and at 100; at 50 one cell stops being wanted but stays loaded,
  inside the half-cell margin).
- Change: the Basic exercise sets the Radius to 1000; the answer says that nine cells load, the island's two too,
  because 1000 m replaces every layer's 256 m and the island's corner is 814 m away (checked: 9 wanted and loaded), and
  that a small radius such as 100 changes nothing in this world.

### WK6
- Fixed on `make/performance`. Why: "What you need" offered a starting checkpoint that does not exist; Checkpoint 1 is
  the end of the first section, with the `Field` and its script already in place.
- Change: the item says that no download starts the page, and that Checkpoint 1 holds the parts with the `Field` and
  its script, so a reader who takes it skips the section's first two steps. Step 1 copies `FieldSpawner.cpp` from that
  checkpoint's `Scripts`.

### WK7
- Fixed on `make/performance`. Why: `renderStats` is "the viewport's latest frame (null while it
  renders none)", and an editor without a window draws no viewport (checked: `renderStats` and `gameRenderStats` null,
  `boundBy` unknown). A capture answers with the same numbers: from above the field 0 occluded and 4539 visible, from
  behind the hut 1982 and 3283.
- Change: the hut step's tab reads `renderStats.occludedProxies` from `viewport.capture` with the editor camera before
  and after the move and gives the two readings; the bound step's "If you do not see it" names unknown until the GPU's
  times arrive and in an editor without a window. "Watch streaming" reads `world.status` as the camera moves (checked
  on the Open World: `loading` 4 and `loaded` 19 at once, `loaded` 50 three seconds later). Found on the way: a
  capture's last frame keeps the sun's cascades (`cachedCascades` 5), so `shadowDraws` reads 0 with shadows on and off;
  the shadows step no longer promises `renderStats.shadowDraws` and says that the change shows while the camera moves.
  Small cuts keep the page within size M. The tutorial file is unchanged: a file with `viewport.capture` is skipped by
  `tutorials.py run`, which still refuses `--pictures`, so the capture's readings are this check's, not the file's.

### WK8
- Fixed on `make/performance`. Why: the prefab's copy has two entities named `rock_largeA`, the root and the child
  with the mesh (checked: `entity.find` by the name gives two, with `"component": "MeshRenderer"` one); the tutorial
  file already asked that way, the page did not.
- Change: the tab runs `entity.find` with the name and the component, then `component.set` on that ID.

### WK9
- Fixed on `make/automated-playtests`. Why: the tab named no editor for the call and no command to close it.
- Change: any running editor takes the call, also one that shows only its launcher (checked: `project.openSample`
  answered in an editor with no project); the editor closes with `editor.quit`.

### WK10
- Fixed on `make/automated-playtests`. Why: the first run's warning and build were missing from the "You should see".
  The page's PowerShell line works: run from the copy's folder it printed the log and then 0 (`tetris.out`), the first
  run with "The scripts of 'Tetris' are not built yet" and "Script build 1 finished in 5.6 s", the second without them.
- Change: step 3's "You should see" names the warning and the build of the first run.

### WK11
- Fixed on `make/commands` and its exercise file. Why: `scatter.json` was no download (`tutorials/make/commands/` is
  not published), and the projects the steps name had no links.
- Change: exercise 1's stage copies `scatter.json` into the project, so the Hard exercise's solution download holds
  it; step 1 says to take it from there and put it where `StrataCLI` runs, and the answer names it. "Before you start"
  links Checkpoint 4 of `make/project-coin-run`; the steps link Checkpoint 9 of `make/animation`, Checkpoint 7 of
  `make/large-worlds` and the result downloads of `make/reflections` and `make/gi`.
- The run wrote the solution zip with `scatter.json` and `stage-1.commands.json`; the exercise's own stage did not run,
  because its chain failed first (see the top), so the stamp records a failure.

### WK12
- Fixed on `make/commands`. Why: `world` takes the asset's path with its extension. Checked: `Worlds/Meadow` answers
  "Parameter 'world': no asset 'Worlds/Meadow'"; `Worlds/Meadow.stworld` gives five layers, `Decals` with 32 m cells
  and a streaming distance of 128 m, and one undo takes it back.
- Change: the JSON names `Worlds/Meadow.stworld`, a sentence says why and quotes the error, and the "You should see"
  adds the 128 m and the undo.

### WK13
- Fixed on `make/commands`. Why: `StrataCLI list` prints the 156 commands and the connection's own methods
  (`rpc.handshake`, `rpc.authenticate`, `rpc.ping`, `rpc.listMethods`): 160 lines and an empty last one.
- Change: the "You should see" says a line for each command and a few more at the top whose names start with `rpc.`.

### WK14
- Fixed on `make/commands`. Why: the walker did not run these steps; they were run here. `animation.createController`
  with the page's file and the clip handles answered with the two states and their clips; `animation.preview` posed the
  robot (`posed` true) and `{stop: true}` stopped it. `lighting.bakeProbes {}` on the download of `make/reflections`
  failed with "The scene has no active reflection probe": that download is the courtyard as the page starts it, with no
  probe. With the probe of that page's step 6 the bake wrote `Lighting/Main/<probe id>.hdr` (`complete` true); the
  capture with `debugView` `gi` on the result of `make/gi` answered complete.
- Change: step 6 adds the probe first (`entity.create` with `probe.json`), and names the error of a missing probe and
  the texture's path.

### WK15
- Fixed on `make/with-an-agent`. Why: the page did not say what a reader without an agent program does; the walker's
  way, the command tabs by hand, is the one open to that reader.
- Change: one sentence after "What you need": without an agent program, run the calls of each command tab yourself;
  only the agent's own answers stay unseen.

### WK16
- Fixed on `make/with-an-agent`. Why: `editor.showPanel` fails in an editor without a window, `--no-gpu` or headless
  (its description; checked).
- Change: the tab says so, and that `editor.activity` still answers.

### WK17
- Fixed on `make/with-an-agent`. Why: the export binds only an id that a later step uses, and no step of this session
  uses a placed prop's id (checked: 6 steps, `bindings` 0, `unrepeatableEdits` 1 with the `scene.recover` warning).
- Change: the paragraph says when the export writes a bind and that it writes none here; the export's "You should see"
  adds `bindings` 0; "Keep the rest of each step as the export wrote it" no longer names a bind. The walker's run of the
  raw export, which ended with no props, is what the step's editor tab warns of.

### WK18
- Fixed on `make/with-an-agent`. Why: the placeholder did not say which of the entry's two values to copy. Checked: the
  entry's `scene` applied here too (it takes the newest applicable entry); the walker's failure with it came after the
  entry had been used.
- Change: the tab names the entry's `id`, the value with a dash, with an example, and says what the `scene` does.

### WK19
- Fixed on `make/with-an-agent`. Why: JSON inside the command line breaks in Windows PowerShell 5.1 (checked: exit 3),
  and `play.step` needs a paused game (checked: "Stepping needs a paused running scene (play.pause)").
- Change: the three calls with parameters (`editor.activity` twice, `play.step`) take them on standard input,
  `echo '<json>' | StrataCLI call <method> -`, which worked in PowerShell 5.1 for `play.pause`, `play.step` and
  `editor.activity`; the Tetris step pauses with `play.pause` first and says why.

### WK20
- Fixed on `make/samples`. Why: the script sits on the entity `Game` (checked: `entity.find` with the name
  `Playground` is empty; `Game` has the script `Playground`).
- Change: the editor tab searches `Game`; the command tab finds `Game` with `entity.find`, then sets the field and
  saves.

### WK21
- Fixed on `make/samples`. Why: `project.openSample` refuses over unsaved changes (checked for the Playground's field
  and the Open World's `TourOnStart`), and the steps changed the scene without saving.
- Change: steps 4 and 6 save (**Ctrl+S**, `scene.save`), and their "If you do not see it" quote the refusal; step 6's
  tab finds `Player` first.

### WK22
- Fixed on `make/samples`. Why: the page's sizes were disk use on this machine's exFAT drive, whose large clusters count
  every small file big (the package's Open World: 92 MB of disk, 16.8 MB of files). Checked as files: Playground 28 MB
  opened and 41.5 MB built and played, Open World 19.4 and 42.5 MB, Outpost 347 MB opened (283 MB of import cache) and
  362 MB played; about 446 MB in all.
- Change: about 450 MB of free disk for the three copies; the Open World's copy about 20 MB, 40 MB once built and
  played; the Outpost about 80 MB as it ships and about 360 MB as a copy once imported.

### Steps for a fresh walker
- `make/large-worlds`: from Checkpoint 1, "Fill the cells" steps 3 and 5 and "See the cells stream" steps 3 and 4 by
  their command tabs; "Teleport without falling" steps 2 and 5 from Checkpoint 5; the Basic exercise from Checkpoint
  7; "Export the world" steps 1 and 2.
- `make/performance`: "What you need" with Checkpoint 1; the hut step and the bound step; "Make the field cheaper"
  step 3; "Watch streaming" step 2 on a copy of the Open World.
- `make/automated-playtests`: steps 1 and 3, the first from an editor that shows its launcher.
- `make/commands`: "List the commands"; "Do what no menu can" steps 1, 4 and 6 from the downloads the page now links.
- `make/with-an-agent`: in Windows PowerShell 5.1, the command tabs of "Ask the agent to place props" step 1, "Read the
  Activity panel and undo" steps 1 and 2, "Steer the agent safely" step 3, "Keep the session as a test" steps 1 and 2,
  and "Make a whole game the agent's way" step 2.
- `make/samples`: steps 4 to 7 in order, and the disk sizes.

## Confirm

Confirmed as persona G0 against the book as built after the fixes (the served build was rebuilt while I waited; I read the
pages only after it showed `project.setStartScene`). Official 0.8.0 package, StrataCLI against one editor per project under
the perf lock, projects and logs in `docs-work/walk-G-final-10/confirm/` (`lw.log`, `lw2.log`, `pf.log`, `ap.log`, `cm.log`,
`wa.log`, `wa2.log`, `wa3.log`, `sm.log`; scripts in `tools/`). Starting points were the downloads the pages name: Checkpoints
1, 5, 6 and 7 of `make/large-worlds`, Checkpoint 1 of `make/performance` and `make/with-an-agent`, Coin Run Checkpoint 4,
the Hard exercise's solution of `make/commands` (for `scatter.json`), and the result downloads of `make/reflections` and
`make/gi`. Editors were headless (GPU on) except the one of `make/with-an-agent`, which the page's own
`StrataCLI launch --project` line started with a window. Not done: every "In the editor" tab and picture (no screen), the
launcher card itself (a headless editor with no project is the nearest to "shows only its launcher"; its `editor.status`
reads `launcher` false), the claim that `editor.showPanel` fails headless (not re-run; the windowed editor answered it).

### WK1
- Gets through, one gap. "What you need" now names Checkpoint 1 and says its project holds the four parts and the empty
  world; I took it and `world.info` listed the four layers. The export: `project.setStartScene` answered the handle of
  Meadow and `project.settings` showed it. But from the Checkpoint 6 download `project.export` first failed: "'Worlds/Meadow.stscene'
  uses scripts, but no script module is loaded: build the scripts (script.build)". A reader who walked the teleport section
  has built them; one who starts from the download has not, and the export step does not say so. After `script.build` the
  export wrote LargeWorlds.exe, .stgame, .stpak and the scripts dll (16 MB).

### WK2
- Gets through. Before the save `world.status {cells: true}` read 4 dirty, 0 loaded and an empty list, as the tab says. I
  placed Pine (10, 0, -20), Rock (60, 0, -20) moved to x 70 (its id is in the `prefab.instantiate` answer under
  `instances[0].id`) and Stump (-20, 0, 20; the page gives no position for it, so I chose one in cell (-1, 0)). After the
  save the list held the seven cells the page names: Terrain (0, 0), (-1, 0), (0, -1), (-1, -1) and Props (0, -1), (-1, 0),
  (1, -1), with 0 dirty and 7 loaded.

### WK3
- Gets through. `world.loadCells` with `wait: true` answered Loaded with `entities` 0 before and 1 after `scene.open`; the
  list then read 1 for each Terrain cell and 3 for each Props cell, as the tab says.

### WK4
- Gets through. After `script.build` and `script.add`, `script.get` listed class Teleport with `ReachRadius` 48. With the
  two lines added to Begin as the page says, the ball stood at 608, 0.4999, 608 after 10 + 300 steps: it lands anyway, as
  "You should see" now says. Step 4 (with the prefetch) also ended with the ball on the far tile.

### WK5
- Gets through, with a small guess. With Radius 1000 `world.status` read `playing` loaded 9 and wanted 9, while the
  block `cells` of the same answer still read 7 (the edit scene's own cells); the page says only "read world.status".
  With Radius 100 both read 7. The answer (nine cells, 814 m, 100 changes nothing) matches.

### WK6
- Gets through. "No download starts the page ... take Checkpoint 1": the project holds the Field with FieldSpawner and the
  Hut; `entity.find` found both, `script.build` succeeded and `play.start` spawned the field. No "already has the script"
  error came because I did not repeat step 2.

### WK7
- Gets through. `viewport.capture` with the editor camera: `renderStats.occludedProxies` 0 (visible 987) above the field,
  1982 (visible 3283) after `camera.set` behind the hut, the numbers the page quotes. `editor.perf` `gpu.boundBy` read
  "capped" after captures had drawn frames, and "unknown" (frames 0) on a later read with nothing drawing; the page's
  "unknown ... in an editor without a window" covers it. `world.status` on the Open World copy after `camera.set`: wanted 53,
  loading 4 at once, loaded 53 four seconds later; flying 600 m away gave unloading 43, then 0.

### WK8
- Gets through. `entity.find {name: "rock_largeA", component: "MeshRenderer"}` returned one id; `component.set`
  `CastShadows` false took it; `prefab.apply` with `entity` and `component` answered the prefab path; `entity.delete` of
  the copy's root and `play.start` followed. A capture then read `shadowDraws` 0, which the page says.

### WK9
- Gets through. In a headless editor with no project, `project.openSample` {sample "Tetris", directory} answered the project
  file, then `editor.quit` closed it; the folder held Tetris.stproj, Assets and Scripts (and README, CREDITS, a picture).

### WK10
- Gets through. The page's PowerShell line (`& StrataEditor.exe --project . --commands Playtest.json
  --quit-after-commands --no-gpu | Write-Output`, then `$LASTEXITCODE`) printed the log, the warning "The scripts of 'Tetris'
  are not built yet", "Script build 1 finished in 5.3 s", "Command script finished (3 commands)" and 0; the second run had
  no warning and no build and printed 0 again.

### WK11
- Gets through. The page names where `scatter.json` is (the Hard exercise's solution; its zip holds it) and the links go to
  the pages' anchors, from which I took Coin Run Checkpoint 4. `prefab.instantiate '@scatter.json'` made 200 coins: tag
  Coin 200, the last at 19, 0.8, 9, only one entity named plain "Coin", "Coin (1)" first; one `edit.undo` removed all.

### WK12
- Gets through. `world.setLayers` with `Worlds/Meadow.stworld` on Checkpoint 7 answered five layers, Decals with cellSize 32
  and streamingDistance 128; one `edit.undo` took it back ("Set the layers of Meadow").

### WK13
- Gets through. `StrataCLI list` printed 160 lines: 156 commands and 4 `rpc.` lines at the top; no empty line.

### WK14
- Gets through. `lighting.bakeProbes {}` on the Reflections download first failed with "The scene has no active reflection
  probe", as the page warns; after `entity.create '@probe.json'` it answered `complete` true and wrote
  `Lighting/Main/<probe id>.hdr`. `viewport.capture '@gi.json' --save-image gi.png` on the GI download wrote a 1.4 MB
  picture with `complete` true.

### WK15
- Gets through. The sentence is there ("Without an agent program, run the calls of each With a command tab yourself"); I
  ran the tabs by hand in Windows PowerShell 5.1.26100.

### WK16
- Gets through. In the editor started by the page's `StrataCLI launch --project` line (with a window)
  `editor.showPanel {panel: "Activity"}` answered; `editor.activity` with `source` "Automation" listed the rows (client
  "StrataCLI", source Automation). The headless failure the tab warns of I did not re-run.

### WK17
- Gets through, one mismatch. `editor.activity.export` with `since` gave `steps` 7, `bindings` 0 and the warning about
  `scene.recover`; the file held place, place, place, place, undo, place, scene.open. After deleting the scene.open step and
  adding the expect to each placement the file had five placements, not the "four placements" of "You should see": the
  Steer section told me to place one more prop before `scene.open`, and that placement is in the session. The copy ran with
  exit code 0 ("Command script finished (6 commands)").

### WK18
- Gets through. `scene.recoveryStatus` gave `id` "767BA8F8BB482CB8-..." and `scene` "767BA8F8BB482CB8"; `scene.recover` with
  the `id` applied and the Crate and Lamp were back (`entity.find`). The `scene` value applied too when it was the newest
  entry.

### WK19
- Gets through. In Windows PowerShell 5.1 `echo '<json>' | StrataCLI call editor.activity -` (also with `newest`, `since`,
  `command`), `play.pause` and `play.step` all worked; `play.step` while playing unpaused answered "Stepping needs a paused
  running scene (play.pause)" and after the pause ran 60 steps (`stepsRun` 60).

### WK20
- Gets through. `entity.find {name: "Game"}` gave the id; `script.setField` Playground `SlowMotionScale` 0.1 and `scene.save`
  answered. I had opened the copy and played it once first, as step 3 does, so the script module was built.

### WK21
- Gets through. After step 4's save `project.openSample` OpenWorld worked; after step 6's `entity.find` Player,
  `script.setField` TourOnStart false and `scene.save`, `project.openSample` Showcase worked with no refusal.

### WK22
- Gets through. File sizes: Physics Playground 26.7 MB opened, 39.6 MB played; Open World 16.7 MB opened ("about 20 MB"),
  40.5 MB played ("about 40 MB"); Outpost 331 MB opened and imported, 346 MB played ("about 360 MB"); together 426 MB
  against "about 450 MB of free disk".
