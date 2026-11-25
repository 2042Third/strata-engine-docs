# Notes: editor/recovery

## New terms

None proposed. The page defines the glossary terms recovery journal, base hash, structural step and discarded (recovery) in bold.

## Since

0.3.0: the journal and scene.recover (inventory editor-core, release column 0.3.0).

## Requests

- Figures: the Mermaid map is the only picture. The Recover Unsaved Changes dialog and the toast after a forced scene.open belong to editor-ui/launcher-dialogs and are not requested here.

## Not verified

- The test case of exercise 2 (segments of sizes 1, 1 and 2 through RecoveryHarness commands) was not written or run.
- The file name is the scene handle (or Untitled) plus a session id, read from MakeJournalStem; the page says "named with the scene's handle and a session id".
- The "within a frame" write for an edit after a long pause follows from Update's 10 s test; no test run confirmed it.
- Links to editor/saving.md and basics/programming-3.md assume those pages exist.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
