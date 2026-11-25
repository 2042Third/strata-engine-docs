# Notes: reference/build

## New terms

None. The page defines configure preset, label and shard in bold; the glossary homes none of them here, so the clerk may admit them.

## Requests

None.

## Not verified

- The tools table's "Taught in" links (generated-code for the sample and committed generators, ci for CompatLint/CI scripts, physics/tuning for PhysicsSweep) were chosen by page names that mention the tool, not by reading each page.
- The label table's "Release and Dist only" for fuzz and perf is from the CONFIGURATIONS of the tests; the rest of the label meanings are summarized from which tests carry them.

## Hand-written tables

- Label table: `StrataTests/CMakeLists.txt` (set_tests_properties LABELS).
- Tools table: the docstrings of `Tools/*.py` (v0.8.0 added `Tools/ConvertLTCTable.py`, its CTest `StrataTools.LTCTable`; the generated-code page does not teach it yet), `StrataTests/FeatureTest/Tools/GenerateAssets.py`, `StrataEditor/Tools/GenerateIconHeader.py`, `.github/scripts/*`.

## Findings not applied

- critic-reference-9 applied as prose (the three cache variables are named in the introduction), not as table rows: the generated build.md does not hold them.
- critic-reference-17 (layer table from `Layers.json`): not applied; no generated file exists for it.
- critic-reference-2: applied by naming the teaching page in each section introduction.
- The generated file puts all four tables in one include, so section introductions for presets, tests and shards follow the include.
- Size lint is the known reference fault; none seen (1,132 words).

## Clerk

- Refused: configure preset (a reference page homes no term; the planner may home it in engineering/build-system); label and shard are homed on engineering/test-program.
