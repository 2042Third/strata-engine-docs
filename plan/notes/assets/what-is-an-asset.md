# Notes: assets/what-is-an-asset

## New terms

None proposed. The seven homed terms (asset, stored form, import, importer, cook, cooked asset, engine-native asset, asset manager) are defined in bold.

## Requests

- Host for a Further reading entry: dev.epicgames.com (Unreal "Cooking and Chunking"), cited without a link.

## Not verified

- That NativeAssetImporter only checks and registers a file (the page says the stored form is the source itself, which StoresSourceDirectly shows).
- The exact bytes of the cached texture; the page gives a computed estimate (about 1.4 million bytes) from the format rules.
- That the exported folder holds the runtime program, the manifest, the notices and the pack: GameExport.cpp:309 and 701-707 show pack, program and notices; the manifest name comes from AGENTS.md.
- What Unity, Godot and Unreal do beyond what their documents (Further reading) say.
- That Physics may include Asset but not Renderer in the layer table (taken from the AssetMeshProvider comments).

## Findings not applied

None: the brief listed no open findings.

## Clerk

- Not admitted: dev.epicgames.com, whose front page gave no answer to one fetch (as in the earlier batch); left for the planner.
