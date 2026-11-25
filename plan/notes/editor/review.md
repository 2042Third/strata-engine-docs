# Notes: editor/review

Pages each exercise of `editor/review` needs (all under `editor/`):

1. Basic: undo, saving (save point, `MarkSaved`, dropped redo branch).
2. Basic: command-scripts, stepping (`until` in a paused game, fixed step count, exit code 1).
3. Medium: recovery, undo (write times of 2 s and 10 s, structural steps fold into segments).
4. Medium: camera-viewport, placement, commands (orbit camera position, grid plane hit, support function, view changes record no undo step).
5. Medium: journal, play-mode, commands (replay of Edit commands, running copy skipped, edits outside commands, undo history).
6. Hard: trash-references, undo, journal (referencers from memory, `force`, open scene never deleted, failed undo keeps its step).
7. Hard: worlds, undo, saving (re-celling, dirty marks, two-request save, `CheckCells` and a failed undo, marks stay after undo).
8. Hard: deferred-commands, command-scripts, stepping, play-mode, undo (`MayDefer` and `editor.batch`, waiting step in a script, running copy edits vanish at Stop).
