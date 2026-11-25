# Card: tutorial runner

Run one page's tutorial and exercises against the pin build, find why a stage fails, mend, stamp. Change only that
page, its tutorial file and folder, what the run writes, and `plan/notes/<part>/<chapter>.md`.

## Places

- Book `G:/GameEngineAI/.worktrees/docs-book`; Bash `P=/c/msys64/mingw64/bin/python.exe`.
- Pin clone, run only: `G:/GameEngineAI/.worktrees/docs-pin`.
- `<work>`: `G:/GameEngineAI/.worktrees/docs-work/tutorial-runs/<page-key>-<round>`.
- `<dumps>`: `reference/_dumps/822a7a46dbcdd86e8e2eafde7e41d003e27260c8`.

## Steps for one page

1. Offline: `$P -I tools/tutorials.py check --quiet --dumps <dumps> --engine ../docs-pin <part>/<chapter>`; "differs
   from what compile writes" is fine (run compiles).
2. Chain: `startsFrom {"tutorial": X}` replays X's whole chain first; a failing link reads "the tutorial it starts
   from, X, failed: …". That is X's runner's: report it, wait.
3. Run, in PowerShell only, one page per hold:

   ```powershell
   Set-Location G:/GameEngineAI/.worktrees/docs-book
   python G:/GameEngineAI/.worktrees/docs-pin/Tools/PerfLock.py --label docs-tutorials --wait 30 --limit 20 -- C:/msys64/mingw64/bin/python.exe -I tools/tutorials.py run --engine G:/GameEngineAI/.worktrees/docs-pin --build G:/GameEngineAI/.worktrees/docs-pin/build/windows/bin/Release --work <work> <part>/<chapter> *> <work>.out
   ```

   `<part>/<chapter>` takes the tutorial and every exercise file; `<part>/<chapter>/exercise-2` one exercise.
4. Read the end of `<work>.out`: one line per file, `passed: … stamped …` or `failed: <file>:<line>: stage N: <why>`.
   Exit 0 all passed, 1 a failure, 2 preflight or usage.
5. Log: `<work>/log/NNNN-<command>.log` per call with its answer (parameters `params-NNNN.json`);
   `reader-copy-…-stage-N.log`. Projects: `<work>/tNN/`.
6. Every run writes the stamp and the reader copies (`public/downloads/tutorials/<page>/stage-N.commands.json`); a
   pass adds the stage zips.

## Whose fault

Read the failing call's answer in the log and its description in `<dumps>/commands.json`.

- File: a wrong parameter, bind or order, a check expecting what the engine does not do: mend it, and the page where
  it says the same.
- Page: a tab missing a step the file needs, a "You should see" the answer contradicts: mend it.
- Tool: stops on a correct file: fix it with a test in `tools/tests/` seen failing first.
- Engine: a command not doing what its description says: the page states what the pin does; notes `## Engine`.

Usual faults met:

- `entity.find` answers `{"entities": ["<id>"]}`: bind `/entities/0`, never `/entities/0/id`.
- `camera.focus` with nothing selected frames the whole scene.
- A file the page imports from the release: `asset.import {"file": "@RELEASE@/Samples/…"}` (setup, or commands where
  the page's tab runs it), never a copy into `Assets/`; a file the page copies by hand: copy it, then `asset.info` with
  `until` (it asks again through "no asset" answers).
- A code change inside a stage (build error and fix, hot reload, crash): `files` on the command it comes before; what
  depends on the editor's state across it (play mode, a crash) goes in `checks`, which the reader's copy leaves out.
- A tab with `component.set` on a component nobody added: add the `component.add` lines.
- Undo names: command `Set Translation of 'Sun'`, Inspector `Edit Transform Translation`, gizmo `Move Entity`.

## Page and file say the same

Per stage, the page's command tabs in order against `commands` (`entityName` stands for an ID): what one does, the
other tells. Add checks of the page's "You should see" values to thin files. Then `$P -I tools/pagecheck.py <page>`.

## What the run cannot take

Patch tutorials (phase B), a start from an engine exercise, a file without stages. Write them under `## Tutorial run`
in the notes.

## Commit

`git add <paths>; git commit -F <msg> -- <paths>`, one commit per page: "Run <page>'s tutorial: <what was mended>".
Stamps go in even when failed. On `index.lock` wait and retry.

## The lock

A hold takes 25 s (one exercise) to 4 minutes (a chain of 10); waits for engine perf runs passed 30 minutes: queue in
the background, work offline. After a stopped run, end only `StrataEditor.exe` processes naming your work folder.

## Never

Build the engine; change a file of the clone; weaken a check to make it pass; change what a step teaches to fit a wrong
file; mend another page's file; use `open: true` or `preferences.set`; leave an editor running.

## Patch tutorials

- Run, from the book, in PowerShell: `python <clone>/Tools/PerfLock.py --label docs-patch --wait 60 --limit 180 --
  C:/msys64/mingw64/bin/python.exe -I tools/tutorials.py patch --engine <clone> --build-dir <clone>/build/docs-patch
  --work <work> <part>/<chapter> *> <work>.out`. The end of `<work>.out`: one `passed:` or `failed: <file>: <why>`
  line per file; logs `<work>/log/NNNN-build.log`, `NNNN-test-<suite>.log`.
- `build/docs-patch` is shared and kept. A header change rebuilds in 1.5 to 6 minutes; a first build was not timed.
- The runner configures after every apply, and after the revert of a chain that adds or removes files (the
  engine's `CONFIGURE_DEPENDS` globs), so a chain that adds files passes in one run.
- An engine exercise runs its page's `patch.tests` and the suites its page's tutorial file names for it:
  `"exercises": {"<n>": {"tests": ["<suite>"]}}`.
- An exercise patch applies after the page's patch. To remake one: `git worktree add` the clone at the pin under
  `docs-work/patch-runs/`, apply and commit the chain, make the change, `git diff HEAD`; remove the worktree.
- An exercise meant to fail (an assert seen firing) can have no patch: drop `solution=`.
