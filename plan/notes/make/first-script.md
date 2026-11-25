# Notes: make/first-script

## New terms

None proposed. The page defines crash containment, external editor, field, hot reload, Problems panel, script class, script field, script module and SDK, all homed on it.

## Since

0.3.0: the Scripts menu, New Script, Ctrl+B, hot reload and crash containment are in the first-tag manual (inventory gamedev:129-133, all 0.3.0).

## Requests

- All nine figures are editor or scene pictures of Coin Run with the script built; the figure recipes use the basic3d template and `waitsFor` "tier 2: editor screenshot" because the recipe schema offers no Coin Run project and no panel or dialog commands (Preferences, New Script, toast). The layout file `layouts/first-script.ini` does not exist yet.
- The tutorial starts from `make/lighting`, which has no tutorial file in the stage commands of this page: stage commands avoid entity names, because the names of the five coin instances are not known.

## Not verified

- That a second `ST_SCRIPT_CLASS(X)` in a header fails the build or only registers twice: the rule says "once", with the reason that several files include a header.
- The exact placement of the Problems panel's crash rows and the Console's crash text at the pin's build (read from EditorContext.cpp, not run).
- The Preferences External Editor page's exact labels beyond "External Editor" and **Apply**.
- The line the compiler reports for a missing semicolon (MSVC, clang and gcc differ); the page says it is often the next line.
- Which menu item opens the Script component's Apply to Prefab (the component header's menu, InspectorPanel.cpp:846).
- `preferences.set` value shape for Editor.ExternalEditor: {"Command": ...} from ExternalEditor.cpp c_CommandKey.

## Findings not applied

- critic-make-a-23: applied (`public:` and `[[maybe_unused]]` each get a sentence in the template list).
- The brief's field change in the Inspector is done before Play, not during it, so that no play-mode edit is needed.
- Step 7 of the brief (Log::Info) and step 8 are merged into one section.

## Figures

Editor figures, taken once with the provisional build (engine 5b975ad2831e, 2026-11-18); nothing published, `waitsFor` kept.

- prefs: round 1 shows the Preferences dialog on its External Editor page, with the Command field and the editors
  found (VS Code, Visual Studio; no user name in the paths). Good.
- new-script-dialog: round 1 shows the dialog with the grey example name PlayerController, the Empty class box and the
  line "Writes Scripts/<Class>.cpp". Good.
- scripts-root: round 1 shows CMakeLists.txt, Coin.cpp (Coin) and the template's Spinner.cpp (Spinner); caption, alt
  and shows now say "lists the files". Good.
- inspector-coin: round 1 shows the Script component with the class Coin and Degrees Per Second 90. The coin is a
  plain entity, not an instance of the prefab the page speaks of (no Coin Run project). Good.
- problems-error: round 1 shows one row: C2143, missing ';' before '}', Scripts/Coin.cpp, line 13 (MSVC). Good.
- console-log: round 1 recipe copied stage 3, which copies only the exercise's file (default -180); it now copies
  `CoinLog.cpp`. Shows five "Coin starts with" lines (90 four times, 180 once) between the editor's command lines.
  Good. Round 2 (a viewer's report): the picture has nine lines, five marked [Script] (the coins') and four marked
  [App] (script.add, play.start, editor.wait, editor.showPanel), and the caption said only "one line for each coin".
  Caption, alt and shows now say which lines are the coins' and that the [App] lines are the editor's commands. The
  picture itself is right and unchanged, so no retake: the take's own commands are what put the [App] lines there.
- crash-toast: round 1 shows the toast "Script crash: play mode stopped" with Show Problems, the status bar at Editing
  and a Problems row with Coin::OnUpdate, Scripts/Coin.cpp, line 18. Good.
- coins-reloaded: cannot. The recipe's one `script.build` shows a "Scripts built" toast, no coins, not playing. The
  state needs the source changed while Play runs (`files` with `atStep` opens a new window without play) and the
  tumbling is motion, which a still cannot show. The page needs instead: a diagram of a coin's turn around the
  upright axis before the rebuild and around the horizontal axis after it, or no figure; the recipe is left as it was.

### At the pin 319075e3 (v0.8.0), 2026-11-23

All nine published; `waitsFor` removed (check: the pin has `editor.screenshot`).

- The seven editor figures: one take each, the same states as the provisional round above (Console: script.add,
  five [Script] lines, play.start, editor.wait, editor.showPanel; no user name in Preferences or the Console). Published.
- result: round 1 had no coins (the recipe only built a script on Basic 3D, `camera: "scene"`). Now a staged still:
  five gold Cylinder coins at the page's positions (x -3 to 3, 0.8 m up, z -4), camera at (0, 2.2, 6), fov 26; four
  face the camera and the middle one is turned 60 degrees around the upright axis, as the faster coin would be. Round 2
  published. It is a still of the scene, not the running game: no Game view, no script attached.
- coins-reloaded: the editor recipe cannot show a hot reload (no command changes a source during Play; `atStep`
  reopens the window without play) and the tumble is motion. Changed to a scene still with the same row and camera as
  result, each coin tipped 40 degrees around the X axis and the middle one 75 degrees: beside result it shows the
  change of axis. It cannot show that Play kept running; caption, alt and shows no longer claim it. Round 2 published.
  A take of the real reload would need a command that writes a project file while playing.
- crash-toast, a viewer's report (2026-11-23): the Problems panel was one row tall at 960 × 540 and its row was cut
  at "Ac"; the page says the panel "lists the crash and its stack". Round 2: `layouts/first-script-crash.ini` at
  960 × 720 (bottom tabs 586 × 260): still one row, the rest empty. The pin's Problems panel leaves out the crash's own
  frame (the crash row stands for it), the SDK thunks and frames without a source, so a crash inside `Coin::OnUpdate`
  itself has no stack rows. Round 3, published: 960 × 620 (bottom tabs 586 × 160), the toast with the whole message
  above the one row (`Scripts/Coin.cpp`, line 18). The caption now says no stack rows follow. The "3 errors" pill counts
  unread Console errors, not Problems rows. For the page's "lists the crash and its stack" to hold in the panel, the
  crash would have to happen in a function `OnUpdate` calls (the frames of `script.status`'s `lastFault` keep the rest);
  the page's step 3 would need to say "lists the crash" instead.

## Clerk

- No term or word asked.
- Left for the planner: the nine figures, `layouts/first-script.ini`, the tutorial's start.
- Settled 2026-11-18: step 2 names the grey example `PlayerController` of the Class name field; inspector-coin's plain entity stands (the caption claims no prefab marks).

## Tutorial run

- 2026-11-18, pin build, `tools/tutorials.py run`: the file now does what stages 2 and 3 tell: `script.add` on `Coin`,
  `prefab.apply`, `script.setField` 180, 60 paused steps (`Coin (2)` turns 90 degrees, quaternion y 0.7071; `Coin` 180
  degrees, y 1.0), and `log.read` holds "Coin starts with 90 degrees per second" and the 180 line. It passed in a
  scratch copy of the book with two earlier links mended there. In this book the run stops before stage 1, because its
  chain fails (the stamp says so): `make/editor-tour` stage 2 (`camera.focus` with nothing selected frames the whole
  scene, distance 31.1, the check asks 10 within 10) and `make/assets` stage 1 (files copied into `Assets/` are not
  registered yet when `asset.info` runs; `entity.find` answers IDs, so its bind is `/entities/0`, not
  `/entities/0/id`). Run again once those pass.
- 2026-11-18, second run: passed, with exercise 1, the chain through `make/lighting` passing. Stages 3 and 4 now run
  every step with `files` on the command each edit comes before: `CoinNoSemicolon.cpp`, then `script.build {wait:
  false}` and `script.status` until the build ends (one error, "syntax error: missing ';' before '}'" in `Coin.cpp`; the
  tab shows the same two commands, since `script.build` alone fails); `CoinLog.cpp` and a clean build; the new
  `CoinTumble.cpp` built while the game plays (`reloaded: true`, play goes on); `CoinLog.cpp` again; `CoinCrash.cpp`,
  `play.start`, play back in Edit and `script.status`'s `lastFault` naming `Coin` and `OnUpdate`; the fix, a clean build
  and 30 steps of play. The reader's copies ran in parts (three for stage 3, five for stage 4). The command tabs of
  stage 4 now show the `play.start`, `play.stop` and `script.build` their steps run. `script.open` (step 3 of stage 3)
  is left out of the file: it would open a program on the shared machine.
- 2026-11-18, third run (chain through the mended `make/lighting`): passed as written, then the thin parts got the
  page's own values and passed again. Stage 4 now checks, with `script.get` while the reloaded game plays, that `Coin`
  is live with Degrees Per Second 180 and `Coin (2)` 90 ("the faster coin is still faster"). Exercise 1 now checks its
  answer: the log holds "Coin starts with -180 degrees per second" and the 180 line, and after 30 steps `Coin (2)`
  turned the other way (quaternion y -0.7071) while `Coin`, with its own 180, kept its way (y 0.7071).
- 2026-11-23, at the pin 319075e3 (v0.8.0), the chain through `make/lighting` replayed: the tutorial (4 stages) and
  exercise 1 passed as written; stamps and stage zips rewritten, the reader's copies unchanged.
- `script.create` runs without `open`: with no external editor set, the pin opens the file in the system's default
  application (its answer: `openedWith: "the default application"`), which no run may do on a shared machine.

## Track walk G, final, segment 3 (2026-11-24)

Answers to `plan/walks/G-final-3.md`, WK16 to WK21:

- WK16, WK17: with no external editor set, `script.create {open: true}` and `script.open` open the file with the
  system's default application and answer `openedWith: "the default application"`
  (`StrataEditor/src/Editor/ExternalEditor.cpp:383-393` at the pin); nothing refuses. Step 2 of Create the script and
  step 3 of the build error now say so (the old fix step said the editor refuses). The engine line below stays for
  the planner; the page states what the pin does.
- WK18: the attach step's tab adds `prefab.apply` on the root, as the tutorial file runs it, and says where
  `<coin id>` comes from, that `script.add` lists only given fields and that `prefab.apply` counts the four other
  coins; the editor tab says to select the root.
- WK19: the log section says that the reader types the whole `OnCreate` (lines 10 to 13) back, since the 21-line file
  has none; "In step 3 you put" became "Step 3 below puts".
- WK20: the build decides by file times, which some drives (FAT, exFAT) keep in steps of 2 seconds
  (`tools/tutorials.py` `c_TimeStepSeconds`), so an edit saved right after a build can look built. The crash step's
  "If you do not see it" names the case and the fix (save again, build, play).
- WK21: matched; nothing to change.

## Engine

- `script.create {open: true}` with no external editor set opens the file with the system's default application;
  its description says "in the external editor", and step 2's "If you do not see it" expects only a Console line. For
  the planner: which is meant.
