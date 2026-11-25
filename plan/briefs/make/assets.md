# Brief: `make/assets`

| Field | Value |
| --- | --- |
| Title | Bringing in assets |
| Kind | H |
| Size | M |
| Tracks | G, B |
| Needs | `make/transforms-units`, `make/project-files` |
| From | gamedev "Bringing in assets" (§1.5, concept 6); assets (use side): import settings, Fast and High, sub-assets, safe moves and deletes; editor-core "Project files as history: the trash and references" (use side: deletes go to the trash and are undone); licenses, CC0 sources (Kenney, Poly Haven, Quaternius, ambientCG) and a `CREDITS.md`; handles in one paragraph; use home of the trash and of undoing asset deletes; Coin Run's coin model |
| Unit | `plan/allocation/make-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/assets` — Bringing in assets

**Covers.** The goal: bring Coin Run's coin model into the project and put it where the placeholder coin stands.
What must be true first: Coin Run at the end of `make/scenes-entities`, and the release folder of Strata at hand (its
`Samples/` hold the file). First, where assets come from: one paragraph on licenses (CC0 is free to use with no
conditions, CC-BY asks for credit, anything unclear stays out), places that give CC0 assets (Kenney, Poly Haven,
Quaternius, ambientCG), keeping downloads in a folder of their own, and a `CREDITS.md` table in the project (files,
source, author, license, changes) as the samples keep it. The steps. (1) In the Content Browser, **New ▸ Folder**
`Models`, then drag `Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb` (Kenney's Platformer Kit, CC0) onto it
(or **Import**; files dropped on the editor's window import into the shown folder): the import runs in the background
and the status bar's assets pill counts it. The formats in a small table: glTF 2.0 models (a `.gltf` brings its `.bin`
and its images), PNG, JPEG, TGA, BMP, PSD, GIF and HDR images, WAV, MP3, FLAC and Ogg sounds, TrueType and OpenType
fonts (`.ttf`, `.otf`), and `.cube` color lookup tables for a grade (`make/look`); OBJ and FBX are not read (`new:2`).
One line links the table of what the glTF importer supports and what it skips or clamps, each with the warning the
Asset tab shows, on `assets/models-gltf`. If you do not see it: a failed import (a broken file, an image the importer
refuses) posts one **Import failed** toast that names the file and the reason, with **Show Asset** and the Console's
line, and the Asset tab shows the reason above the import settings that may fix it (`assets:144`). (2) Expand the model
in the Content Browser: its sub-assets (meshes, materials, textures) are assets of their own; the Asset tab shows the
model's summary (meshes, triangles, materials, textures) and its import settings. (3) The `.meta` file beside
`coin-gold.glb` in the file browser (shown as `make/project-files` taught): one paragraph on handles, a stable identity
kept in that file, so that a scene names the asset by its handle and a rename or a move in the editor breaks nothing.
(4) Drag the model from the Content Browser into the Scene view: it places as a linked group of entities resting on the
ground (the drop's ghost and linked groups are `make/prefabs`'). (5) Check its size against the 1 m ball and set the
model's **Scale** import setting with Apply until the coin is the size the page gives; a model made in centimetres needs
0.01. A model's bounds have no menu or button (the Asset tab's summary shows no size,
`StrataEditor/src/Panels/AssetInspectorPanel.cpp:570-590`), so the editor tab compares the coin with the ball, and
`asset.info` with the bounds in metres stands only in the command tab. (6) The other import settings a maker uses, each
in a sentence: `BaseColorFactorsAreSRGB` for models whose exporter writes colors as sRGB (Kenney's), a texture's usage
guessed from its name (`_normal`, `_rough`), a texture's **Quality** Fast or High (the look, the stored size, the import
time), `RemoveSun` for skies (`make/lighting`). (7) Replace the placeholder: move the `Coin` tag to the model's root,
delete the Cylinder coin, name the model's root `Coin`. (8) Rename and move safely: rename the `Models` folder with F2
and see the `.meta` files follow. (9) Delete safely: **Delete...** on the coin model is refused while the scene uses it
(the Delete Asset dialog lists who uses it); an unused asset goes to the project's trash, and Ctrl+Z brings it back. `##
Result`: the coin model in the project and in the level, credited in `CREDITS.md`; it ends with the download of the
page's end state. `## Variations`: a model in centimetres; a texture whose source file changes on disk (the editor
imports it again in the background, hot reload of assets); a model from a downloaded pack. A paragraph of G4 points
forward: making a material with the imported texture is `make/materials`'. The exercises (`new:18`) are two editor
tasks.

**Leaves out.**

- What an asset is inside: sources and cooked forms → `assets/what-is-an-asset`
- Handles, `.meta` files and sub-assets inside → `assets/handles-meta`
- Import records, cache validity and background imports → `assets/importing`
- Textures for the GPU, mips and compression → `assets/textures`, `assets/texture-cooking`
- glTF and models as entity templates; the table of what the glTF importer supports and skips → `assets/models-gltf`
- The trash and references inside → `editor/trash-references`
- Linked groups, drops and their ghost → `make/prefabs`
- Materials from the imported textures → `make/materials`
- Sounds and fonts → `make/sound`, `make/hud`
- The index of everything Strata does not have → `appendix/not-in-strata`

**Fit.** `fits`: about 3,900 words against M (3,000). Nine steps take most of it, with the formats table, the paragraphs
on licenses and handles, three Variations, four pictures and two exercises. It is near M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:52-53` | feature | home | The Asset tab (import settings, the model's summary) and the Content Browser (folders, grid, thumbnails, drag and drop) |
| `gamedev:77` | feature | home | Importing by dropping files or with **Import**; background imports; a `.gltf` brings its `.bin` and images |
| `gamedev:78` | feature | home | The formats the importers read, `.otf` fonts and `.cube` lookup tables among them, which the item leaves out. The importers live in `Strata/src/Strata/Asset/` (`AssetPipeline` is a layer of `StrataTests/Architecture/Layers.json:113-117`, not a folder): writers cite `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` (read at the pin) |
| `gamedev:79` | feature | home | The asset types, named as the Content Browser shows them |
| `gamedev:80` | feature | home | `.meta` files and handles; never edited by hand |
| `gamedev:81` | feature | home | The import settings a maker uses: Scale, `BaseColorFactorsAreSRGB`, usage from names, `RemoveSun` named |
| `gamedev:82` | feature | home | Deletes to the project's trash, refused while used, undone by Ctrl+Z |
| `gamedev:83` | feature | home | The policy for downloads: CC0 or CC-BY, a folder of their own, `CREDITS.md` |
| `gamedev:304` | concept | home | Assets and import: sources against imported data, stable handles, background imports, import settings; the mistakes (centimetre models, sRGB factors, a normal map as color) |
| `gamedev:351` | concept | home | Licenses of assets: CC0, CC-BY's credit, unclear licenses kept out |
| `gamedev:445` | figure | home | The Content Browser's grid with thumbnails and an expanded model; its Scripts root is shown again by `make/first-script` |
| `gamedev:519` | rule | home | Asset licenses: CC0 or CC-BY only, credited |
| `gamedev:537` | hands-on | home | G4, its import and scale half: a model and a texture imported, the model's scale fixed; its material half is `make/materials`' |
| `gamedev:585` | term | home | Asset handle |
| `gamedev:586` | term | home | Import and import settings |
| `gamedev:587` | term | home | Sub-asset |
| `gamedev:665` | term | home | CC0 and CC-BY |
| `new:18` | hands-on | home | Exercises, two editor tasks: **Basic.** import `barrel.glb` from the same folder of the ThirdPerson sample (Kenney's Platformer Kit, CC0), place it beside the ball and check its size; **Medium.** place one barrel, predict whether **Delete...** on `barrel.glb` is refused, try it and read who uses it in the Delete Asset dialog, then delete the barrel entity, delete the model and bring it back with Ctrl+Z. Evidence: `Samples/ThirdPerson/Assets/Models/Platformer/barrel.glb`; `StrataEditor/src/Editor/EditorAssetCommands.cpp:899-903` (`asset.delete`: the trash, one undo step, refused while a scene uses it) |
| `new:2` | not-done | home | OBJ and FBX import: models are glTF only. Evidence: `Strata/src/Strata/Asset/AssetImporters.cpp:159-177` registers no OBJ or FBX importer (run at the pin); `Docs/Releases/0.7.0.md:414-415` |
| `assets:38` | feature | use | The asset handle |
| `assets:44-45` | feature | use | `.meta` sidecars; sub-assets |
| `assets:136-137` | feature | use | Import settings; background imports and hot reload of assets |
| `assets:144` | feature | use | Step 1's "If you do not see it": a failed import's one **Import failed** toast with **Show Asset** and the Console's line, and the reason in the Asset tab above the import settings. Evidence: `StrataEditor/src/Editor/EditorContext.cpp:2872-2895` (`NotifyImportFailures`); `StrataEditor/src/Panels/AssetInspectorPanel.cpp:143`, `:757-774` (`DrawImportOutcome`, drawn before the settings) (read at the pin) |
| `assets:141` | feature | use | Moves, renames and deletes as the editor does them |
| `assets:215` | feature | use | The Content Browser and the Asset tab |
| `assets:246` | concept | use | What an asset is: the source and what the game reads, at the user's level |
| `assets:253` | concept | use | Identity by handle, not by path, in one paragraph |
| `assets:496` | figure | use | The Content Browser with an import running |
| `assets:513-514` | figure | use | The refused delete; the status bar's assets pill |
| `assets:520` | rule | use | Reference assets by handle, never by path |
| `assets:522` | rule | use | Move, rename and delete through the editor |
| `assets:613` | hands-on | use | Import a model and its textures, read the sub-assets, place it |
| `assets:617` | hands-on | use | Fast against High, in step 6 |
| `assets:642` | term | use | Import and importer |
| `assets:644` | term | use | `.meta` file |
| `assets:733-734` | term | use | Referencers; trash |
| `editor-core:161-162` | feature | use | Delete to the trash; the check for users |
| `editor-core:338` | concept | use | Files are part of the history: deletes undone |
| `editor-core:521` | figure | use | The Delete Asset dialog listing the scene that uses the coin |
| `editor-ui:121` | feature | use | Files dropped on the window import into the shown folder |
| `editor-ui:146-147` | feature | use | The Asset tab and the Content Browser panels |
| `editor-ui:219` | feature | use | The Delete Asset confirmation |
| `editor-ui:554` | figure | use | The Content Browser's grid with an expanded model |
| `editor-ui:688` | hands-on | home | Import assets, browse thumbnails, drag a model into the view; making a material is `make/materials`' |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The project folder, `.meta` files, extensions and hidden files; undo | `make/project-files` | must |
| Sizes in metres and the scale of a Transform | `make/transforms-units` | must |
| Entities, the Hierarchy, the Inspector and tags | `make/scenes-entities` | must |

**Starting state.** The end state of `make/scenes-entities` (`startsFrom {"tutorial": "make/scenes-entities"}`):
the ground, four walls under **Walls**, the ball and the placeholder coin. The file comes from the release's
`Samples/ThirdPerson/Assets/Models/Platformer/coin-gold.glb` (credited in that sample's `CREDITS.md`), copied by the
tutorial file's `files` (its import is a `setup` step, shown as dragging the file into the Content Browser). The page
ends with the coin model placed and tagged; `make/materials` starts there.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cc-by` | CC-BY | - |
| `cc0` | CC0 | - |
| `import` | Import (use) | - |
| `asset-handle` | Asset handle (use) | - |
| `sub-asset` | Sub-asset (use) | - |
| `import-settings` | Import settings (use) | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-make-a-20 | should | missing-item | `make/assets` (step 4), `make/materials` (step 3), `make/prefabs` (step 3) | A placed model is a root entity named after its file, with one child entity per node of the file; the Mesh Renderer is on a child, and the root holds only its Transform and what the reader adds. `make/materials` step 3 sets the coin's Mesh Renderer in the Inspector and `make/prefabs` step 3 overrides its material; with the root `Coin` selected the reader finds no Mesh Renderer. | `make/assets` step 4 shows the placed group expanded in the Hierarchy (the root, its children with the mesh) in two sentences; `make/materials` step 3 and `make/prefabs` step 3 select the child, or drop the material on the mesh in the view (about 60 words). | `allocation/make-a.md:411-412`, `:419-420`, `:519-520`, `:613-614`; `Strata/src/Strata/Asset/GltfImporter.cpp:592`, `:1974-1987` |
