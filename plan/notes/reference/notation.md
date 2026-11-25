# Notes: reference/notation

## New terms

None.

## Requests

None.

## Not verified

- The checked claim that a model faces +Z (glTF) rests on the comment of Math.h and AGENTS.md, not on a loader test.
- "Pack blocks, upload budgets" as uses of KiB and MiB come from header comments only.

## Hand-written tables

- Space and geometry, Units, Light levels, Color: read from Math.h, Common.slang, Scene.slang, StrataShaders.cmake, SceneRenderer.cpp, ScriptABI.h, RendererComponents.h, TextureImporter.h, MaterialTextures.slang, Docs/DeveloperGuide.md (reference values).
- Rechecked row by row at v0.8.0 (319075e3): every row held; added the rect light's units (nits for its face, or lumens with `Units` Lumens, L = P / (pi A)) from RendererComponents.h and AreaLights.h.

## Findings not applied

- Symbol table (4) of the brief: src/generated/reference/ holds no symbols file, so it is omitted.
- critic-reference-13: concerns reference/game-makers and the generator, not this page.

## Size

The lint reports 1,4xx words against M: a known fault of the tool for reference pages; not padded.

## Clerk

- Nothing asked; nothing admitted.
