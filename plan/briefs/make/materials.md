# Brief: `make/materials`

| Field | Value |
| --- | --- |
| Title | Materials |
| Kind | T |
| Size | L |
| Tracks | G, B |
| Needs | `make/assets` |
| From | gamedev "Materials" (§1.6, concept 8); render-direct "Describing surfaces: Strata's material model" (use side); normal maps and their import setting `FlipGreen`; emission as a color and a strength (its value in nits is `make/lighting`'s); the albedo audit with the debug view; Coin Run's gold coin and the ball's material |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/materials` — Materials

**Covers.** The page gives Coin Run a gold coin and a ball with a textured metal material, and teaches the material
model at the maker's level. The idea first, in one paragraph and the grid of spheres from rough to smooth, metal and
not: a material says how a surface answers light, with a base color, a metallic value and a roughness, and the rest
(maps, emission, alpha) builds on them; physically based means the values mean the same under any light. Colors as
three numbers from 0 to 1 are explained from zero beside the color picker. The steps. (1) **New ▸ Material** in a
`Materials` folder of the Content Browser: `Materials/Gold.stmat`, open in the Asset tab's material editor. (2) Base
color: a gold color from the page's table of plausible values; metallic 1 (metals take their color from the base
color); roughness 0.3. (3) Give the coin the material (the Mesh Renderer's **Material** in the Inspector, or a drop of
the material on the coin in the view). (4) Drag the roughness from 0 to 1 and watch the sun's highlight spread; set
metallic to 0 and see painted gold, the mistake of a metallic value on paint. (5) The ball's material: import
`Metal032_Color.jpg`, `Metal032_MetallicRoughness.jpg` and `Metal032_NormalGL.jpg` from
`Samples/PhysicsPlayground/Assets/Textures/Metal/` (ambientCG, CC0); each texture's usage is guessed from its name;
make `Materials/Ball.stmat` with the three maps and a UV tiling. (6) Normal maps from zero: bumps drawn without
geometry, read as data and never as color; set a normal map's usage to Color on purpose and see the material editor's
warning with **Fix**; the import setting `FlipGreen` for maps made the DirectX way (a name with `dx` turns it on), seen
by turning it on and back. (7) Emission as a color and a strength, on the coin, faint; its value in nits is
`make/lighting`'s. (8) Alpha modes on a scratch cube, deleted afterwards: Opaque, Mask with its cutoff, Blend with an
alpha of 0.4; glass with Transmission and IOR 1.5; clear coat, Unlit and Double Sided in one sentence each. (9) The
albedo audit: the Scene view's debug view chip ▸ **Albedo** marks base colors outside the plausible range; a wall set to
pure white is marked, and the reader fixes it to the value the view accepts. (10) Save. The table of guidance for
makers: water and wet surfaces IOR 1.33 with roughness 0.02 to 0.06, glass 1.5, painted surfaces roughness 0.15 to 0.45,
base colors above 0.85 look like plastic. What Strata does not do here (`new:3`): no shaders as assets and no material
graphs, because every surface uses the one physically based model; and (`new:19`) no material parameters per entity,
such as a tint or a hit flash, and no material changes from scripts: a loaded material never changes, so a game gives
the Mesh Renderer another material, as the Tetris sample does. Common mistakes: near-white base colors, metallic on
paint, a normal map imported as color. At the end the reader can make, assign and audit materials; the checkpoint
holds the gold coin and the metal ball.

**Leaves out.**

- The material model as physics: the BRDF, Fresnel and energy → `light/materials`, `light/reflectance`
- The material's GPU record and the normal decode → `light/material-data`
- Clear coat and transmission in depth → `light/clearcoat-transmission`
- Textures for the GPU: color spaces and compression → `assets/textures`
- The albedo view and the other measuring views inside → `light/measuring-light`
- Emission in nits and light units → `make/lighting`
- Reflections that make metals look right → `make/reflections`
- Colors and color spaces as a subject → `basics/color`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 4,400 words against L (5,000). Ten steps at B0's length take most of it, with the material idea,
colors as numbers and normal maps taught from zero, the guidance table, the sphere grid, five pictures and the albedo
exercise.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:89` | feature | home | Material documents: **New ▸ Material**, the material editor, the properties a maker sets |
| `gamedev:90` | feature | home | The guidance table of plausible values |
| `gamedev:309` | concept | home | Materials and physically based shading at the maker's level; the mistakes (near-white colors, metallic paint) |
| `gamedev:448` | figure | home | The material editor in the Asset tab; the normal-map warning with **Fix** |
| `gamedev:589` | term | home | Material |
| `gamedev:590` | term | home | PBR |
| `render-indirect:539` | hands-on | home | Step 9: the albedo audit, fixing what the Albedo view marks |
| `new:3` | not-done | home | Shaders as assets and material graphs: shaders are compiled at build time and embedded. Evidence: `Strata/src/Strata/Asset/AssetTypes.h:14-31` has no shader type (run at the pin); `strata_add_shaders` in `Strata/CMakeLists.txt:80` |
| `new:19` | not-done | home | Material parameters per entity, such as a tint or a hit flash, and material changes from scripts: a loaded material never changes, and a game gives `MeshRenderer.Material` another asset. Evidence: `Strata/src/Strata/Renderer/Material.h:87-90`; `git grep -ni material 822a7a46 -- StrataScriptCore/Include/StrataScript/ScriptABI.h` finds nothing (run at the pin); `Samples/Tetris/Scripts/TetrisBoard.cpp:365` |
| `gamedev:537` | hands-on | use | G4's material half: a material made with the imported texture |
| `render-direct:35-37` | feature | use | The metallic-roughness material, the alpha modes, emission as a color and a strength |
| `render-direct:39` | feature | use | The texture maps a material takes |
| `render-direct:44` | feature | use | Normal maps read as two channels |
| `render-direct:46-47` | feature | use | Clear coat and glass, named |
| `render-direct:50` | feature | use | `material.create`, `material.get`, `material.set` in the steps' command tabs |
| `render-direct:300` | concept | use | The surface description, at the maker's level |
| `render-direct:307` | concept | use | Textures as color or data; normal maps |
| `render-direct:526` | figure | use | The metallic-roughness grid of spheres |
| `render-direct:531` | figure | use | A normal map on and off |
| `render-direct:541` | figure | use | The Albedo view marking out-of-range albedos |
| `render-direct:563` | figure | use | Glass at IOR 1.5 |
| `render-direct:641` | hands-on | use | A material set audited in the Albedo view, as an exercise |
| `assets:165-166` | feature | use | Normal map conventions; the texture-usage warnings |
| `assets:498` | figure | use | The same texture as color, as a normal map and as data |
| `assets:615` | hands-on | use | A normal map fixed by its name: tokens, `FlipGreen`, the warning |
| `assets:714` | term | use | Normal map |
| `editor-ui:185-186` | feature | use | The Mesh Renderer's material section; the material editor with its **Fix** |
| `editor-ui:561` | figure | use | The Asset tab with a material being edited |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Importing textures, the Asset tab and import settings | `make/assets` | must |
| Components and the Inspector | `make/scenes-entities` | must |
| The Scene view's chips | `make/editor-tour` | helps |
| Colors and color spaces as a subject | `basics/color` | helps |

**Starting state.** The end state of `make/assets` (`startsFrom {"tutorial": "make/assets"}`): the level with the coin
model placed, scaled and tagged. The three texture files come from the release's
`Samples/PhysicsPlayground/Assets/Textures/Metal/` (credited in that sample's `CREDITS.md`). The page ends with
`Materials/Gold.stmat` on the coin and `Materials/Ball.stmat` on the ball.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `material` | Material | - |
| `pbr` | PBR | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-20 | should | missing-item | `make/assets` (step 4), `make/materials` (step 3), `make/prefabs` (step 3) | A placed model is a root entity named after its file, with one child entity per node of the file; the Mesh Renderer is on a child, and the root holds only its Transform and what the reader adds. `make/materials` step 3 sets the coin's Mesh Renderer in the Inspector and `make/prefabs` step 3 overrides its material; with the root `Coin` selected the reader finds no Mesh Renderer. | `make/assets` step 4 shows the placed group expanded in the Hierarchy (the root, its children with the mesh) in two sentences; `make/materials` step 3 and `make/prefabs` step 3 select the child, or drop the material on the mesh in the view (about 60 words). | `allocation/make-a.md:411-412`, `:419-420`, `:519-520`, `:613-614`; `Strata/src/Strata/Asset/GltfImporter.cpp:592`, `:1974-1987` |
| critic-make-a-21 | should | missing-item | `make/materials` (step 5) | A material's numbers multiply its maps: the Metal/Rough Map's blue and green channels are scaled by Metallic and Roughness. A new material has Metallic 0 and Roughness 0.5, so `Ball.stmat` with the three maps shows no metal and half the map's roughness until both are 1. Only `light/material-data` (track E) states the rule, and no tooltip says it. | Step 5 sets Metallic and Roughness to 1 once the **Metal/Rough Map** is in place, with one sentence on why (about 40 words). | `allocation/make-a.md:521-524`; `allocation/light.md:89`; `Strata/src/Strata/Renderer/Material.h:23`, `:27-28`; `Strata/src/Strata/Renderer/Material.cpp:31-32`, `:48-49` |
