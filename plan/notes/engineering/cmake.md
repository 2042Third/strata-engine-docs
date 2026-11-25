# Notes: engineering/cmake

## Since

`since: 0.4.0`: `CMake/StrataLayers.cmake` and `StrataTests/Architecture/CheckNoTooling.cmake` were added in engine commit dd83f1e0 ("Build one library per layer from the layer table", 2026-10-13), first contained in the tag v0.4.0.

## New terms

- usage requirements: what a CMake target hands to the targets that link it (include folders, definitions, links); the keywords PUBLIC, PRIVATE and INTERFACE say who receives them. Home: engineering/cmake. Aliases: none. Defined in bold as a plain term in "The problem and how engines solve it", together with the bold term "targets" (target, CMake): a named thing to build, such as a library or a program, that carries its own include folders, definitions and links.

## Requests

- Word `Bazel` (written in code font on the page, in the Alternatives table).
- Figure: none requested; all four pictures are Mermaid diagrams. The brief's text captures of two configure failures (build-test:459) are not requested: the card forbids CMake output as a text capture.

## Not verified

- That a build in Visual Studio without a configure leaves a new file out of its library (the brief's hands-on `build-test:555`): not stated at the pin, so the page says only what `Architecture.Libraries` reports.
- The exact lines of the closure error when the forbidden link is Scene to AssetPipeline: the page says the first path is `StrataRuntime -> Strata -> Strata_Scene -> Strata_AssetPipeline` (from reading the walk and the sketch), not from a configure run.
- Bazel's visibility rules as an alternative (general knowledge, no citation in the pin).

## Findings not applied

- The brief lists no open findings at its end.
- `strata_copy_runtime_resources` is named as a helper that no target calls at the pin: checked by search; no call site in CMake files.

## Clerk

- Admitted the terms usage requirements and Target (CMake) (alias CMake target), homed here; the glossary's target is engineering/perf-lab's.
- Admitted to names.txt: Bazel.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
