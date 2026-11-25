# Notes: animation/importing

## New terms

None proposed: the page defines the glossary's `animator` in bold and defines no other term.

## Requests

- No new words or hosts. No figures file: the one diagram is Mermaid.

## Since

- since 0.3.0: the importer's animation steps were part of 0.3.0 (`animation:63-68`, inventory column "0.3.0"); the import scale baking is 0.4.0 (version 8 comment in `GltfImporter.h`).

## Not verified

- The "Who uses it" column of the alternatives table names kinds of engines and tools, not products; no source was checked.
- That a changed `Scale` setting imports the model again (it follows from the settings hash of the import records, not read in the code).
- That the `AnimationController` loader's JSON source is edited by hand (the file extension `.stanimator` was checked, not its authoring path).

## Findings not applied

- `new:1` is applied: the page states version 11 and says the engine's `Docs/Architecture.md` still says 9.
- `animation:25` (guards) applied in prose; the per-guard line numbers were not listed.
- The 1.4 items on "stable handles" are taught through keys and derived ids; a handle-stability test (`GltfSkinImportTests.cpp:285`) is named.

## Clerk

- Nothing asked.
