# Walk of track G, segment 1 (G-final-1)

- Track G, persona G0 (game maker). Entries walked, in order: `start/install`, `start/first-game`, `start/what-an-engine-is`, `start/coming-from`.
- Package: official Strata 0.8.0 Windows x64 (copied from the unpacked archive into `walk-G-final-1/Strata-0.8.0-windows-x64`).
- How: no screen, so every step ran through its command tab with StrataCLI against a headless editor (`StrataCLI launch --headless`, learned from `make/with-an-agent`), under the perf lock, one editor per hold; no editor left running. Work folder `G:/GameEngineAI/.worktrees/docs-work/walk-G-final-1/`; command transcripts in its `tools/run2.log` and `tools/run3.log`. Editor preferences were never changed.
- What matched: `--version` printed `Strata Editor 0.8.0`; the log's first line and `Graphics device:` line are as the page says; the Tetris copy built (5.7 s) and played, its Script lines are in the log; project.create gives the five entities; the cube falls (rests at y 0.4999), slides off the 35 degree ramp to x 1.9, and with Friction 0.05 and Restitution 0.7 reaches x 8.6 (near the 10 m edge); Spinner turns, and after the edit to 360 the log holds `Spinner starts with 360 degrees per second`; the coin's Radius override shows in prefab.status and prefab.revert returns 0.7; Input.Actions holds Gameplay with Move, Look, Jump. The pages' checks (friction square roots, frame times, the Unity and Unreal conversions) are right.

## Entries

### WK1 (start/install, "Install Strata and the build tools", steps 1 to 4) left the book
The download, the terminal, `cd ~\Downloads` and `Expand-Archive` (with the Unblock tick) were not walked: the package was already unpacked. I copied the folder into my work folder and compared `dir` with the page's table (all entries there). The page says "Download ... from the releases page": no link I could follow from here.

### WK2 (start/install, "Start the editor", step 8) left the book
The step says double-click StrataEditor and look for the launcher with New Project, Open Project and Open Sample. I cannot see or click, so I could not check this "You should see". I started a headless editor with `StrataCLI launch --headless`, a command the install page never names (I took it from `make/with-an-agent`, a side step). The headless editor answered editor.status with `launcher: false`.

### WK3 (start/install, "Run the editor with an argument" and Result) guessed
Step 7 ran as written: `.\StrataEditor --version | Write-Output` printed `Strata Editor 0.8.0`. The page says Visual Studio's C++ CMake tools bring CMake; here the editor found Visual Studio 2026 and a CMake from another folder (MSYS2, version 4.2.2). Nothing on the page says whether that is fine; I guessed yes, and the build worked.

### WK4 (start/install, "When something goes wrong" and Help > About) left the book
The log at `%LOCALAPPDATA%\Strata\Logs\StrataEditor.log` exists, and its lines read `[time] [info] App: Strata Editor 0.8.0 (Windows)` and `Strata: Graphics device: NVIDIA ... (Vulkan 1.3.0, driver ...)`: the page says the first line is `Strata Editor <version> (<system>)`, so a reader meets a time stamp, `[info]` and `App:` before it. Help > About Strata cannot be opened without a screen; I read the version from `editor.status` (`engineVersion`) instead.

### WK5 (start/first-game, "Start the editor you built") did not match
Both tabs assume the reader built the editor: "Open the StrataEditor program in the folder where the install page built it", and the command tab is `build/windows/bin/Debug/StrataEditor.exe`. A reader of the package has no `build/` folder, and the install page unpacked an archive, it built nothing. I used the unpacked folder's StrataEditor through StrataCLI. The "You should see: the launcher, Recent projects says No recent projects yet" could not be seen headless.

### WK6 (start/first-game, "Play Tetris, then stop it" and the key table) left the book
Keys cannot be pressed from the command tab, so I did not play Tetris; I only ran play.start, waited 120 frames (60 FPS, work 0.06 ms per frame), read the Script lines (`Tetris: new game with seed 60`) and ran play.stop. The Game view, the status bar "Building to play" and the Stop button could not be seen. The play.start answer did say `built ... reason: the project's scripts are not built yet, seconds 5.74`, which fits the page.

### WK7 (start/first-game, "Place and move a cube" and the next sections) guessed
The command tabs gave no picture, so the "You should see" of each Scene-view step was checked by numbers (Transform values, entity.get after play) and by viewport.capture with camera `scene` after 30 and 300 frames. They fit the text and the page's pictures. The step "Undo what you did" is a component.set in the command tab, not an undo; I took it as the same result. Gizmo drags, F2 rename and the Add Component search were not done.

### WK8 (start/first-game, "Attach the script") did not match
The tab's command `script.add` answered `"fields": {}` and component.get showed `Fields: {}`. The page says the Inspector shows "Degrees Per Second" set to 90. I could not see the Inspector, and the command answer shows no field value; I guessed 90 from the code.

### WK9 (start/first-game, "Choose your code editor" and "Open the file") left the book
`script.setExternalEditor` changes the editor's preferences and `script.open` starts the system's program, so I ran neither (the step depends on the preferences). I edited `Scripts/Spinner.cpp` with a script instead. The file the editor wrote does not look like the page's listing: it starts with a five-line comment and uses tabs. The page says "Here is the file as the editor wrote it" with line numbers 236 to 257 of ScriptProject.cpp, which a reader cannot match with the file on disk.

### WK10 (start/first-game, "Next, make the script write a line") failed
My first edit (insert `OnCreate`) did not change the file, because I searched for two spaces and the file uses tabs. The build passed, play ran, and `log.read` with `logger: Script, newest` answered only the old Tetris lines, not an error. The page's "If you do not see it: the line is missing" fits, but nothing says the log still holds lines of the other project. After I inserted the function with tabs, the line `Spinner starts with 360 degrees per second` appeared, as the page says.

### WK11 (start/first-game, exercises) left the book
Basic (Gravity Scale 0.2) and the two Medium exercises (-90, the Log::Info line moved into OnUpdate) were answered by thinking only and compared with the page's answers (they agree); I did not run them. The Check yourself answers (friction at 20 degrees: 0.36 under 0.5; about 27 degrees) are right by my arithmetic.

### WK12 (start/what-an-engine-is, pictures) left the book
The six frame pictures and the other figures are AVIF files. The Read tool cannot open AVIF, so I fetched them (about 9 KB each) and could not look at them; I used the captions. The caption says an orange cube; the first-game result picture is described as a pale grey cube, and my own captures show a pale grey cube (not compared by eye).

### WK13 (start/what-an-engine-is, "Medium" exercise and "What the frame pill measures") left the book
The exercise says File > Open Sample > Tetris, while first-game uses the launcher button Open Sample. The frame pill and its word idle are in the status bar, not in a command. `editor.perf` gave `frame.avgMs 0.06` and `framesPerSecond 60.0` for Tetris, but nothing on the page says whether editor.perf shows idle; I could not see the pill or idle. The arithmetic exercise (8.3 ms, 40.0 ms, 125, 25) is right.

### WK14 (start/what-an-engine-is and start/coming-from, "Next on your track") guessed
The bottom strip of each page prints three different "Next on your track" targets: "Coming from Unity, Unreal or Godot", "A tour of the editor" and "How a computer runs a program". I do not know which is G0's, so I followed the assignment (coming-from).

### WK15 (start/coming-from, "Before you start") did not match
The page asks for "You made something in Unity, Unreal or Godot". G0 has used no engine. The page says it is optional, so I walked it anyway; the map tables mean little to G0 (every Unity, Unreal and Godot word is new), but the page's steps worked.

### WK16 (start/coming-from, "Select Player and read its components" and the coin steps) guessed
The command tabs name entities by id (`AAE2EAF90F8A1799` for Player, `959D47C78B26E82F` for Coin 1). They worked in my copy of the sample, so the ids are stable, but the page never says that the ids are fixed or how to find them (`entity.find`); the "In the editor" tab says to click the name. The bold label, the accent bar and Revert in the right-click menu could not be seen; prefab.status listed the Radius override and prefab.revert gave Radius 0.7.

### WK17 (start/coming-from, "Open ThirdPersonPlayer.cpp" and "Open the project's input actions") left the book
`script.open` was not run (it starts the external editor of the preferences). I read `Scripts/ThirdPersonPlayer.h` lines 41 to 45 and `.cpp` lines 54 to 58 from the copy: they match the listings. `project.settings` with `Input.Actions` answered a large schema plus the maps; I found `Gameplay` with `Move`, `Look` and `Jump` (and a `UI` map) by searching the text. The Project Settings window could not be seen. The exercise (camera in the Course scene, `FollowCamera.cpp` with `OnLateUpdate`) was checked only in the file; its Unreal to Strata conversion (-4, 2.5, -12) is right.

## Answers

Answered 2026-11-24 by the page fixer at v0.8.0 (319075e3). Why the walker went wrong, in most entries: it drove a
headless editor by command only, and the command tabs said nothing of what their answers hold or of what shows only in
the window; two listings of `start/first-game` showed text that is not the reader's file. Facts were read at the pin and
in the walker's transcripts (`docs-work/walk-G-final-1/tools/run2.log`, `run3.log`, which ran the official package).
No entry is the engine's fault, so no page gains a `## Engine` note.

| Entry | Page | Outcome | What changed, or why no fault |
| --- | --- | --- | --- |
| WK1 | start/install | rejected | The walk handed the walker an unpacked package, so steps 1 to 4 had nothing to do. The releases link answers (the page and the v0.8.0 tag both return HTTP 200); a reader with a browser follows it. |
| WK2 | start/install | rejected | Step 8 is for a reader at a screen: a headless editor has no window, so `launcher: false` is its normal state. The install page comes before every page that teaches commands, so it gives none, by style.md §10. |
| WK3 | start/install | fixed | Step 9's Windows tab says that a CMake of the reader's own, in `PATH` or `Program Files\CMake`, is tried first and used when it is 3.25 or later and knows the Visual Studio, the workload's otherwise (`StrataEditor/src/Editor/ScriptToolchain.cpp:288-304`). The log section names the `[Scripts] Found` line that tells which tools were chosen (`ScriptBuild.cpp:1108-1110`). |
| WK4 | start/install | fixed | The log section shows a line's form, date and time, `[info]`, `App:` or `Strata:` (`Strata/src/Strata/Core/Log.cpp:225`), with an example first line; Check yourself 5 and exercise 2 read the first line after that prefix. Help ▸ About shows only in the window; exercise 2 already names `editor.status`. |
| WK5 | start/first-game | fixed | Fixed before the walk by the part review (4c6c6add, 07:47 the same day): step 1 starts the editor from the unpacked folder (`.\StrataEditor`, `./StrataEditor`). The walker's served site was older than that commit. The launcher is not seen headless (WK2). |
| WK6 | start/first-game | fixed | Step 4's command tab says that playing is for the reader's hands, that a command can press keys (`input.key`, taught on Automated play-tests) but cannot watch the blocks, and that this command only stops the game. |
| WK7 | start/first-game | fixed | "Undo what you did" says in its command tab why it sets values instead of `edit.undo`: the previous command set all three values in one undo step, so an undo would also take back the lift. Gizmo drags, **F2** and the Add Component search exist only in the window. |
| WK8 | start/first-game | fixed | "Attach the script" runs `script.get` after `script.add`, as the tutorial file already did, and says that `script.add`'s `fields` lists only the entity's own values (empty here) while `script.get` answers `DegreesPerSecond` 90, the class default. |
| WK9 | start/first-game | fixed | The listings are now the reader's file. `tutorials/start/first-game/Spinner-90.cpp` is the template byte for byte (the text of `MakeExampleScript`, `StrataEditor/src/Editor/ScriptProject.cpp:231-257`); the page quotes its five-line comment and then lines 7 to 28, with callouts by the file's own numbers, and says the book draws each tab as two spaces. `Spinner.cpp` and the exercise 2 solution carry the same comment, so the final listing (lines 11 to 33; callouts 15, 17–20, 22–27) matches the file on disk. Not running `script.setExternalEditor` and `script.open` follows the walk's rule on preferences; the steps are right for a reader. The tutorial and exercise 2 pass at the pin build and with the package after the change. |
| WK10 | start/first-game | fixed | The miss came from the listing drawn with spaces (now said, WK9). The log step's If you do not see it names a file without the change, and says that the Console keeps every line since the editor started, so the newest `Script` lines may be those of the Tetris copy: then `OnCreate` did not run. |
| WK11 | start/first-game | rejected | The exercises answered by thought agree with the page's answers, and exercise 2's file passes at the pin build and with the package. Nothing to change. |
| WK12 | start/what-an-engine-is | fixed | The six pictures paint the cube orange on purpose (the recipe's material, base color 0.8, 0.32, 0.08; the original of frame 0 was looked at), and their captions are right. The page now says beside them that their cube is orange and the reader's was pale grey. AVIF is the site's format for every picture. |
| WK13 | start/what-an-engine-is | fixed | The exercise names the launcher's **Open Sample...** beside **File ▸ Open Sample ▸ Tetris**; both exist at the pin (`StrataEditor/src/Panels/WelcomePanel.cpp:403`, `StrataEditor/src/EditorLayer.cpp:1756`). Where it lives says that the word idle shows only in the pill: `editor.perf` has no such field (`StrataEditor/src/Editor/EditorStateCommands.cpp:160-176`). The pill itself shows only in the window. |
| WK14 | start/what-an-engine-is | rejected | The strip writes each track's links into a hidden `<template>` and the book's script shows only the chosen track's set (`src/components/Pagination.astro`). The walker's text extraction read all three templates; a reader who chose track G on How to read sees one link, to Coming from Unity, Unreal or Godot. |
| WK15 | start/coming-from | fixed | The opening tells a reader who has used no other engine that the page is optional, names the next page of tracks G (A tour of the editor) and E (How a computer runs a program), and says that the last section's steps need no other engine. |
| WK16 | start/coming-from | fixed | Step 3's command tab says that the sample stores the IDs in its scene, so every copy has them, and that `entity.find` with the name answers them; step 4's tab says what `prefab.status` lists in place of the bold label, before and after the revert. |
| WK17 | start/coming-from | fixed | Step 6's command tab says where the maps stand in `project.settings`' long answer (`value`, `Maps`, the map named `Gameplay`, its `Actions` with `Name`, `Kind` and `Bindings`, `Key/Space` for `Jump`). Not running `script.open` follows the walk's rule on preferences; the listings matched. |

## Confirm

Confirmed 2026-11-24 at v0.8.0 (package unpacked copy in `docs-work/walk-G-final-1/confirm/`, transcripts `run.log`, `run4.log`, `run5.log` there), as G0, through StrataCLI against headless editors under the perf lock; no editor of mine is left running. Two things of the walk itself: (1) the served site was built before the first-game fix (6b5e5140): its first-game page lacks the WK6, WK7, WK8, WK9 and WK10 text, so those entries were read in `src/content/docs/start/first-game.md` at HEAD (install, what-an-engine-is and coming-from were served fixed); rebuild the preview before the next walk. (2) A first attempt of mine passed a path without its drive (a script slip), and so created an empty project at the root of the drive; it is mine and may be deleted (the safety check refused my `rm`).

| Entry | Now | What the walker saw |
| --- | --- | --- |
| WK3 | confirmed | Step 9's Windows tab says an own CMake in PATH or Program Files\CMake is tried first and used when 3.25 or later and knowing the Visual Studio. After the first build the log holds `[info] App: [Scripts] Found Visual Studio 18 2026 with Visual Studio Community 2026 18.3 (...), CMake 4.1.2-msvc8 (...)`: the page's description of the line is right, and here it chose the workload's CMake, as the page allows. No guess needed. |
| WK4 | confirmed | `%LOCALAPPDATA%\Strata\Logs\StrataEditor.log` starts with `[2026-11-24 14:18:15.579] [info] App: Strata Editor 0.8.0 (Windows)`, the form of the page's example; `log.read` answers the same line as sequence 1 (logger `App`, message `Strata Editor 0.8.0 (Windows)`), next to `editor.status`. The log is cleared at every editor start, so "first line" is always that session's. |
| WK5 | confirmed (no change to test) | Step 1 starts `.\StrataEditor` from the unpacked folder; headless start through `StrataCLI launch --headless` worked. |
| WK6 | confirmed | The tab of "Play Tetris, then stop it" now says playing is for the hands, that a command can press keys but cannot watch the blocks, and that this command only stops. `play.stop` answered state `Edit`. Nothing to guess. |
| WK7 | confirmed | The "Undo what you did" tab says why it sets values instead of `edit.undo` (one undo step for all three values; an undo would take back the lift). The reader knows what to do and why. |
| WK8 | confirmed | `script.add` answered `fields: {}`; `script.get` answered `DegreesPerSecond` 90 (`known` true, `live` false), exactly as the tab now says. |
| WK9 | confirmed | `Scripts/Spinner.cpp` on disk equals `Spinner-90.cpp` byte for byte: comment lines 1-5 as quoted, class at line 12, field at 15, `OnUpdate` at 17. After the edit to 360 and the added `OnCreate`, lines 11-33 of the file equal the final listing. |
| WK10 | confirmed, with a note | After a real rebuild the log holds `Spinner starts with 360 degrees per second` (logger Script, `script.status` callbacks `OnCreate`, `OnUpdate`). My first try failed: my script edited the file in the same clock second in which the first build wrote the DLL, MSBuild saw nothing newer and built nothing (`script.status` listed only `OnUpdate`; the newest Script lines were Tetris's, as the page's If-you-do-not-see-it says). A reader saves minutes later, so this is no book fault; the page's text led to the cause (the file on disk was right, the build had not seen it, so touching the file and building again fixed it). Worth a line only if the book wants to cover builds in the same second: not needed. |
| WK12 | confirmed | The sentence under the six pictures says the picture's cube is orange so that it stands out and the reader's was pale grey. |
| WK13 | confirmed | Exercise 2 names **Open Sample...** and **File ▸ Open Sample ▸ Tetris**. On a playing Tetris copy `editor.perf` answered `frame.avgMs` 0.066, `framesPerSecond` 60.0, `frames` 120: ms far under 1000/60, as the answer says; it has no idle field, and "Where it lives" says the word shows only in the pill. Headless has no pill, as the page says. |
| WK14 | confirmed by reading, not in a browser | I have no browser. The served page holds one template per track; `src/components/client/book.js` (`applyTrack`) replaces the links with the chosen track's template, and the game template of what-an-engine-is holds Previous: Your first game and Next: Coming from Unity, Unreal or Godot. Not seen on a screen. |
| WK15 | confirmed | The opening says the page is optional, that a reader who has used no other engine loses nothing by skipping it, and names A tour of the editor (track G) and How a computer runs a program (E); the last section's steps need no other engine. No guess about skipping. |
| WK16 | confirmed | `entity.find {name: Player}` answered `AAE2EAF90F8A1799`, `{name: Coin 1}` answered `959D47C78B26E82F`: the tab's IDs. `component.set` Radius 1.2 then `prefab.status` listed under `overrides` component `SphereCollider`, property `Radius` (modified true); after `prefab.revert` `overrides` is empty (modified false) and `component.get` reads Radius 0.7, as the tab says. |
| WK17 | confirmed | `project.settings {section: Input.Actions}` answers the section's description and schema first; `value.Maps` holds the maps `UI` and `Gameplay`, the latter's `Actions` with `Name`, `Kind`, `Bindings`; `Jump` is a Button bound to `Key/Space`. The tab's pointer finds it. |

Open for the next editor of the book: nothing in these entries. Rebuild the served preview (the first-game page was stale).
