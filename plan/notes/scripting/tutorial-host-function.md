# Notes: scripting/tutorial-host-function

## New terms

None. The page defines no term in bold.

## Requests

- The tutorial file starts from `{"tutorial": "gpu/debug-drawing"}`; `tutorials/gpu/debug-drawing.tutorial.json` does not exist yet (the page check fails on it, not mine).
- The brief asks for `{"tutorial": "gpu/debug-drawing", "exercise": 3}`; `tools/schemas/tutorial.schema.json` has no `exercise` key. The patch needs the state after `tutorials/gpu/debug-drawing/exercise-3.patch`.
- `Physics.WindZone` is left out of the patch's `tests` list: the tutorial checker does not know a suite that an earlier patch adds.
- No figures, no sketches, no new hosts. Links to `scripting/abi-sdk` and `scripting/script-system` are left out; the brief's "must" rows are used without them.

## Not verified

- Nothing was built or run: the patch was written against the pin plus the two earlier patches and checked only with `git apply --check`.
- That the editor and runtime feature runners accept the new feature scripts and the journal entry of `OnWindChanged`.
- That the two SDK coverage cases and the host-call check run inside the ctest name `StrataTests.FeatureTest`.
- That `RunFrames` at its default step runs a fixed step in each frame, so five frames are enough in the new tests.
- The page's `since: 0.3.0`: no release note was checked for when the host table first grew by appending.

## Findings not applied

- The brief lists no open findings.
- The brief's callback section ends with the test output as a text capture; ctest and compiler output cannot be captured without running them, so the page tells each result in words.

## Since

since 0.3.0: the append-only table and class descriptor are older than the first tag; not checked against a release note.

## Clerk

- Nothing to admit. The tutorial gpu/debug-drawing has a patch but no tutorial file, and the schema has no exercise key: the planner's (the page check fails on it).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
