# Notes: assets/references

## New terms

None. The six terms homed on the page (dependency, dependency closure, closure scope, prefetch, headroom, group load) are the glossary's.

## Since

0.3.0: the scanner and pack dependency tables came with wave 2 (`pack-v2`) in 0.3.0, per the assets inventory (line 116).

## Requests

- No new names or words. The prose words `evict` forms were avoided; `eviction` is the glossary term.
- No figures file: the map is a Mermaid diagram.

## Not verified

- The "Native" marker of engine documents' records, and that a save passes the references it already has: taken from the inventory, not read in `EditorAssetManager.cpp`.
- That deletes refuse while something uses an asset: inventory only; the page links the editor page for it.
- The measurements (25 MB, 60 to 100 MB, 12.6 GB against 280 MB) come from `Docs/Architecture.md` and code comments; not re-measured.
- The names of the books and chapters in Further reading are from memory.
- "GPU.SceneRenderer.GPUDriven" in Changing it safely comes from `AGENTS.md`; not looked up in the tests.

## Findings not applied

- The brief's trace exercise says a breakpoint shows where the `Load` scope stops at another scene in a Showcase scene. At the pin, neither `Outpost.stscene` nor `Loading.stscene` names the other by handle (the loading scene is a project setting), so the skip never fires for them. The exercise says so and asks the reader to add a script field in a copy of the sample.
- Erratum `new:13` applied: the scanner is described from `AssetDependencies.h` lines 30 to 52.

## Clerk

- Nothing asked.
