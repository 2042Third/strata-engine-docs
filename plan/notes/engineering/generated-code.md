# Notes: engineering/generated-code

## New terms

None proposed: `committed generator` and `embedded shader registry` are the glossary's, defined in bold on the page.

## Since

0.3.0: `CMake/StrataShaders.cmake` came in the first commit a0f2865f (2026-10-08, "Add build system, pinned dependencies and engine core"); `CMake/StrataVersionCommit.cmake` in 789e70e5 (2026-10-09).

## Requests

None. The two diagrams are Mermaid; no figures file.

## Not verified

- That `file(CONFIGURE)` and `configure_file` leave an identical file untouched is CMake's documented behavior; the pin's comments in `CMake/StrataVersionCommit.cmake` rely on it, but no build ran here.
- The sample count (300 files including a header) in the problem section is a stated supposition, not a measurement.
- No build was run: file locations under `build/<preset>/Strata/EmbeddedShaders/` are derived from the CMake code.

## Findings not applied

None open in the brief beyond the two open items, both applied (no shader count typed; only the two Showcase generators have CTests). "What went wrong before" omitted: no regression history was examined for this area.

## Clerk

- Nothing to admit.
