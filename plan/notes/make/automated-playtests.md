# Notes: make/automated-playtests

## New terms

None. The page defines the seven glossary terms of its brief in bold: command, command script, simulated input, input sequence, viewport capture, activity journal, replay.

## Since

0.3.0: command scripts and `--commands` (inventory gamedev:227, since column 0.3.0).

## Requests

- Extra words: `comma`, `commas` (JSON is taught from zero; no other word fits).
- Hosts for Further reading (cited without links): json.org, martinfowler.com.

## Not verified

- The UI variation script (`ui.create` button, `ui.hitTest` at the screen center, `input.click` giving `clicked` true) was read in code, not run; the Tetris HUD may cover the center.
- The medium exercise's `until` on the game over text was not run.
- Recovery data offered after a script that leaves edits: read in code, not run.
- Tetris copy keeps the sample's entity IDs, and the exercise's level text "Level: 1": read from the sample's code, not run.
- Install paths in the OS tabs are placeholders; the macOS and Linux program paths depend on the release.
- Exit code 0 for a passing script: only the failure path (1) was read.

## Findings not applied

- critic-make-b2-24 (home of the activity journal): a planner decision; the page defines the term and leaves the glossary as it is.
- The viewport capture variation and `new:5` are applied as text only; no figure is requested (the page has one Mermaid diagram).
- The brief's "a call takes about a tenth of a second": not found at the pin, omitted.

## Clerk

- Admitted to extra-words.txt: comma, commas (G0 has 1). Admitted to external-hosts.txt: json.org, martinfowler.com (each front page is the site it claims).
- Page fix: the quote that started with a blank line now starts with its first line.

## Track walk G, final, segment 10 (2026-11-24)

- Checked with the 0.8.0 package: `project.openSample` answers in an editor that shows only its launcher; the page's
  PowerShell line (`& StrataEditor.exe ... | Write-Output`, then `$LASTEXITCODE`) prints 0 for the three-command test.
  The first run logs the warning "The scripts of 'Tetris' are not built yet ..." and "Script build 1 finished in 5.6 s";
  the second run does not.
- Page mended: step 1 names the editor that takes the call and `editor.quit`; step 3's "You should see" names the first
  run's warning and build.
