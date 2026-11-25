# Brief: `assets/handles-meta`

| Field | Value |
| --- | --- |
| Title | Handles, `.meta` files and sub-assets |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/files`, `assets/what-is-an-asset` |
| From | assets; asset handles only (handles and UUIDs in general are `world/ecs`') |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/handles-meta` — Handles, `.meta` files and sub-assets

**Covers.** The job: every asset gets a name that survives renames, moves, re-imports and other machines. The problem
takes one paragraph that links `assets/what-is-an-asset` and `world/ecs`, with a short table of the approaches: paths,
IDs in a sidecar file (Unity's `.meta`), IDs inside the asset (Unreal), content hashes. The map: `AssetTypes.h` (the
handle and the types), `AssetRegistration` (reading and writing `.meta` files, finding duplicates), `AssetImporter`
(derived handles), `BuiltinAssets`, `AssetMetadata`. The contract: an `AssetHandle` is a `UUID`, a random, non-zero
64-bit number written as 16 upper-case hex digits. The `.meta` sidecar holds the handle, the type and the import
settings, and it is committed with its file. An invalid `.meta` is reported and never overwritten. The type enum is
append only, because packs and import records store its numbers. Handles 1 to 255 belong to the built-in assets. A toy
of about 40 lines keeps a path-to-handle table from sidecar files and derives a child's handle by hashing.

The real code, in the order a file meets it: the handle alias and the type enum; a real `.meta` (the Showcase's
`WeatheredSteel_arm.png.meta`); `AssetMetadata` (path, parent, sub-asset key, stored size); sub-assets and their keys
(`Mesh/0`, `Material/2`, `Texture/<image>/<usage>/<sampler>`, `Skeleton`, `Animation/<name>`); `DeriveSubAssetHandle`
(FNV-1a of the key, combined with the parent, moved out of 0 to 255, so it is the same on every machine); the built-in
assets (eight primitive meshes and the default material, whose objects come from factories the renderer registers, and
which no pack can replace); and files copied with their `.meta`, which share a handle until the scan gives the copies
new ones. Four rules end as why-boxes: by handle, never by path at run time (and why `Assets::Find` needs
`AlwaysInclude`); move, rename and delete through the editor; never overwrite an invalid `.meta`; built-in handles are
reserved. Then the alternatives, the tests (`Asset.Registration`) and changing it safely (append a type; never change
the derivation, which would break every reference to a sub-asset). The "trace it yourself" exercise computes a model's
material handle from the model's handle and the key, and finds the cache file of that name in `.strata/Cache`.

**Leaves out.**

- Handles and UUIDs in general, and why handles beat pointers → `world/ecs`
- What an import writes into the cache and the record → `assets/importing`
- Moving, deleting and restoring asset files, and the trash → `editor/trash-references`
- The handles of world cells, derived the same way → `worlds/grids`

**Fit.** `fits`: about 4,605 words against L (5,000). Three excerpts and the quote of `UUID.h`, the contract and four
rules with their why-boxes take the most words.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:253` | concept | home | Identity by handle, not by path: the approaches, Strata's choice and the mistakes |
| `assets:38` | feature | home | `AssetHandle` is `UUID` |
| `assets:39` | feature | home | The 13 types; their numbers are stored in files, so the enum is append only |
| `assets:43-48` | feature | home | `AssetMetadata`, `.meta` sidecars, sub-assets and their keys, derived handles, built-in assets, duplicate handles |
| `assets:375` | code | home | `Strata/src/Strata/Asset/AssetTypes.h:11-31`: the handle alias and the type enum with its "append only" note |
| `assets:378` | code | home | `Samples/Showcase/Assets/Generated/Props/WeatheredSteel_arm.png.meta:1-20`: a real sidecar with its import settings |
| `assets:380` | code | home | `Strata/src/Strata/Asset/AssetImporter.cpp:264-271`: `DeriveSubAssetHandle`, hashing that skips the reserved range |
| `assets:456` | figure | home | A file, its `.meta`, its cache file named by the handle, sub-assets with derived handles, built-ins 1-255 |
| `assets:520` | rule | home | By handle, never by path at run time |
| `assets:522` | rule | home | Move, rename and delete through the editor, or move the `.meta` along |
| `assets:524` | rule | home | Never overwrite an invalid `.meta`: it may hold a merge conflict |
| `assets:567` | rule | home | Built-in handles are reserved |
| `assets:638-639` | term | home | Asset handle, asset type |
| `assets:644` | term | home | `.meta` file, sidecar |
| `assets:654-656` | term | home | Sub-asset, derived handle, built-in asset |
| `animation:586` | term | home | Sub-asset, as the animation part words it (a model's skeleton and clips) |
| `editor-core:687` | term | home | `.meta` file, as the editor part words it |
| `new:1` | erratum | home | The assets inventory places `ReadAssetMeta`, `WriteAssetMeta` and `FindDuplicateHandles` at `AssetRegistration.h:283-304` and `:319-330`, and the scan's types at `:233-281`, but the header has 121 lines; writers cite the places below. Evidence: `Strata/src/Strata/Asset/AssetRegistration.h:72-93` (the `.meta` status, reader and writer), `:113-120` (`FindDuplicateHandles`), `:23-70` (scan phases, options, slices) |
| `new:24` | hands-on | home | Trace it yourself (D27): a model's material handle computed from the model's handle and the key `Material/0` as `DeriveSubAssetHandle` does, then the cache file of that name found in `.strata/Cache`. Evidence: `Strata/src/Strata/Asset/AssetImporter.cpp:264-271`; `Strata/src/Strata/Asset/EditorAssetManager.cpp:707` |
| `assets:377` | code | use | `Strata/src/Strata/Core/UUID.h:13-33`, quoted for the null value and the text form; its home is `world/ecs` |
| `assets:72` | feature | use | Built-in assets are memory assets, never evicted |
| `assets:141` | feature | use | Moves and the trash keep handles (taught in `editor/trash-references`) |
| `foundation:154` | feature | use | `UUID` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| What an asset, a source file and a stored form are | `assets/what-is-an-asset` | must |
| Handles instead of pointers; UUIDs as 64-bit values | `world/ecs` | must |
| Hashes (FNV-1a), and numbers written in hexadecimal | `basics/data-formats` | must |
| JSON | `basics/data-formats` | must |
| Scoped enums with a fixed underlying type | `basics/cpp-modern` | must |
| Writing a file atomically | `core/files` | helps |
| Git: committing files, merge conflicts | `basics/git` | helps |
| What an import produces, and import settings | `assets/importing` | helps |
| The trash, and undoing a delete | `editor/trash-references` | helps |
| Pruned exports and `AlwaysInclude` | `assets/packs-export` | helps |
| Memory assets, which are never evicted | `assets/loading` | helps |
| Eviction | `assets/residency` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `meta-file` | `.meta` file | sidecar |
| `asset-handle` | Asset handle | - |
| `asset-type` | Asset type | - |
| `built-in-asset` | Built-in asset | - |
| `derived-handle` | Derived handle | - |
| `sub-asset` | Sub-asset | - |
