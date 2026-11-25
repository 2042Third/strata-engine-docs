# Notes: editor/command-scripts

## New terms

None proposed. The page defines the glossary's seven terms (command script, JSON pointer, `expect`, `bind`, `$ref`, `until`, batch) in bold.

## Since

0.3.0: `StrataEditor/src/Editor/EditorCommandRunner.cpp` was added in commit 344ae703 (2026-10-09), contained in tag v0.3.0. `editor.batch` (`BatchCommands.cpp`, commit 3196a8c8, 2026-10-14) first appears in v0.4.0; the page states no version for it.

## Requests

- Figure `script-run` (`src/content/figures/editor/command-scripts.json`): a text capture of `StrataEditor --no-gpu --no-automation --quit-after-commands --commands FallTest.json`. The recipe needs the page's script saved as `FallTest.json` in the capture's working directory (the planner's capture setup); the page shows the script in full.
- Words: none beyond the lists.

## Not verified

- The example script was not run (no engine program may be started): that `entity.create` accepts `"Type": "Dynamic"` as a string in `RigidBody`, that `play.start` with `paused: true` works with `--no-gpu`, and that the height after 60 fixed steps lies in 4 to 6 (calculated from 9.81 m/s² and a step of 1/60 s: about 5.0 m, not measured).
- That `project.create` accepts the relative directory `FallTestProject` (the smoke script passes an absolute path).
- The exact log lines of the example run (the capture fence is filled by the figure pipeline); the page quotes only the two lines of `EditorLayer::UpdateCommandScript`.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `script-run` (text, blocked; 0 rounds, not taken). `tools/figures.py take` runs a text figure's program twice with
  the pin's build folder (`docs-pin/build/windows/bin/Release`) as its working directory, and a text recipe has no way
  to supply an input file. So `--commands FallTest.json` would name a file that is not there (the build folder belongs
  to the pin clone and must not get one). The page's script also creates its project in the fixed folder
  `C:/Work/FallTestProject`: a take would write outside the book's folders, and the second run of the pair (the
  determinism check) would meet the project the first one left. An absolute path into `docs-work` in the manifest
  would only work on this machine. What it needs, a tool addition and not an engine one: a text recipe field that
  writes named files (the page's script, with the project directory as a placeholder the tool fills with a new folder
  per run) into a fresh working folder per run, which the tool then uses as the program's working directory; plus
  redact expressions for the project path and the times. The page's words need no change once that exists (the
  `Not verified` items above, `RigidBody.Type` as a string and the height after 60 steps, are then checked by the take).
  Nearest honest picture until then: none from a run. The fence stays empty; the paragraph after it already quotes the
  final line "Command script finished (5 commands)" from `EditorLayer.cpp:561`.
- `script-run`, rechecked at the pin v0.8.0 (319075e3, 2026-11-23): still blocked, not taken. The engine has all the
  page needs; the tool does not. `take_text_program` still runs the program in the build folder, and `check` now
  refuses `files` on a figure that is no editor or scene figure (the field added for project copies), and refuses
  absolute paths. So the addition above is still needed: `files` for text program figures, copied into a fresh working
  folder per run, with the project directory as a placeholder the tool fills.
- `script-run`, taken at the pin v0.8.0 (319075e3, 2026-11-24) once `files` reached program text figures. The page's
  script is staged from `tutorials/editor/command-scripts/FallTest.json` into a fresh run folder per run, which the
  editor sees as `S:\`. Round 1: the two runs differed in the new entity's id and in "Started in 0.13 s"; both are
  redacted now, with the times. Round 2 gave the same text twice. What the run settles from `Not verified`:
  `RigidBody.Type` "Dynamic" is accepted as a string, `play.start` paused works with `--no-gpu`, the height after 60
  steps is 5.1553044 (inside 4 to 6), and `project.create` takes a relative directory: `Project::Create` makes it
  absolute against the working directory (`Strata/src/Strata/Project/Project.cpp:182`), although its schema says
  "Absolute directory". So the page's script now writes `FallTestProject` instead of `C:/Work/FallTestProject`, and
  the sentence after it says where the folder goes and that a second run needs it deleted ("already contains a
  project", `Project.cpp:187-188`). The log has start-up lines before the steps and the audio's shutdown after the
  script's last line, so the sentence before the fence, the caption, alt and shows say so, and the paragraph after it
  no longer calls "Command script finished" the last line of the log.
  The fence of 14 lines needs callouts (lint), so the paragraph after it became three callouts (lines 6–7, 12, 13)
  and the failing variant's paragraph; words were cut to keep size M (3991). The fifth step's sentence said the
  transform is read "by its name"; the step uses the bound id (`$ref`), so it says so now.
