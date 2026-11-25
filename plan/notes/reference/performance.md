## New terms

None.

## Requests

None.

## Not verified

- The "Read next" page links of the suites table point to pages by their briefs' ids; their existence was not checked.
- The word count (1,378) is below the M row: a known fault of the tool for reference pages.
- No generated CPU-stages table exists in src/generated/reference/, so it is hand-written.

## Hand-written tables

- The suites table: read from the TEST_SUITE names of StrataTests/src/Perf/*.cpp and StrataTests/src/Editor/*Perf*.cpp, and the metric names of StrataTests/Perf/Budgets.json.
- The CPU stages table: read from c_BuiltinFrameStages (Strata/src/Strata/Core/FrameProfiler.h), the ST_PROFILE_STAGE calls and the ProfileStage of each scene system's registration, at the pin.

## Findings not applied

None open in the brief.

## Clerk

- Nothing asked; nothing admitted.
