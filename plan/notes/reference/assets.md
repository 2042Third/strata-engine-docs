# Notes: reference/assets

## New terms

None proposed.

## Requests

None. Links to reference/audio-input, reference/scene, reference/commands and reference/worlds-runtime point at pages written elsewhere at the same time.

## Not verified

- The glTF importer makes Mesh sub-assets (read from its header comment); the Material sub-assets likewise.
- The font and audio clip importers are NativeAssetImporter-like classes in AssetImporters.cpp (taken from the generated table).
- importMB default (a quarter of physical memory) is taken from the asset.setBudget description, not from code.
- Cooked audio "STAU" and scene "STSC" versions read from headers only.
- The brief's asks for material properties, import settings and limits tables (critic-reference-3, -4, -8) need generated tables the folder lacks.

## Hand-written tables

- Types by native extension, loader module and importer: Strata/src/Strata/Asset/AssetTypes.cpp, the five *Registration.cpp files, GltfImporter.h.
- Stored forms: AssetRegistration.h, CookedTexture.h, AssetPack.h, Mesh.h, ColorLookup.h, ImportRecordStore.h, AudioClipAsset.h, CookedScene.h.
- Residency budgets: AssetResidency.h.
- AssetManagerStats fields: AssetManager.h.
- Streaming panel columns: StreamingPanel.cpp.

## Findings not applied

- critic-reference-3 (material properties table): no generated table; needs material.get route.
- critic-reference-4 (import settings table): no generated table.
- critic-reference-8 (limits table): no generated table in this folder for assets.
- critic-reference-2: applied (each table names its teaching page), except the stats table of AssetManagerStats links Residency only.

## Clerk

- Nothing asked; nothing admitted.
