# Brief: `assets/extending`

| Field | Value |
| --- | --- |
| Title | Tutorial: adding an asset type |
| Kind | T |
| Size | L |
| Tracks | E |
| Needs | `assets/uploads`, `assets/robustness`, `world/tutorial-component` |
| From | assets "Extending the pipeline" |
| Unit | `plan/allocation/assets.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `assets/extending` — Tutorial: adding an asset type

**Covers.** What you will make: a new asset type in the engine, a plain text asset (`.sttxt`, stored as its source, as
the inventory's hands-on proposes), from its `AssetType` value to a file the editor imports and a game loads, with the
tests the engine's rules ask for. The sections follow the checklist of `Docs/DeveloperGuide.md`, "Adding an asset
type". Section 1, the type: append a value to `AssetType` (never insert one: packs and records store the numbers), give
it a name, and write the `Asset` subclass, whose `GetMemoryUsage` reports its bytes in the CPU pool. Section 2, the
loader: register it in the registration function of the module that owns the type, take the bytes over with
`TakeBytes`, and reject what is not valid UTF-8 or is too large; the loader runs on a worker and returns no asset when it
fails. Section 3, the importer: one that stores its source after checking it, on the model of the font importer,
registered in `RegisterAssetPipeline`, at version 1. Section 4, the tests: a round trip, and truncated and garbage
stored forms rejected without a crash, with the layering test still passing. Section 5, the feature test: an asset of
the new type with its `.meta` in `StrataTests/FeatureTest/Assets`, because the feature test fails when a registered type
has none.

Each section ends with a checkpoint of the patch, and its "You should see" is the build or the test output. The
exercises make it the reader's own: an importer setting with an inactive reason and a version bump; a manager
extension that counts its updates and adds a statistic; a document type that names other assets and records its
references. At the end the reader has changed the engine the way the part's pages describe, and has seen each rule of
the checklist hold in a test.

**Leaves out.**

- The checks of the feature test in full → `engineering/feature-test`
- Corruption sweeps and their machinery → `engineering/test-program`
- An asset type that uploads to the GPU in steps → `assets/uploads`
- A component with an asset property → `capstone/build`

**Fit.** `fits`: about 4,200 words against L (5,000). Five sections of two or three steps each, the quoted hunks of the
patch, and three exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `assets:585` | hands-on | home | Add a toy asset type: the page's example, from the type to the feature test |
| `assets:588` | hands-on | home | Exercise: an importer setting with `GetInactiveReason` and a version bump |
| `assets:606` | hands-on | home | Exercise: a manager extension that counts its updates and adds a statistic |
| `new:22` | code | home | `Strata/src/Strata/Asset/AssetImporters.cpp:140-155`: the font importer, which stores its source after checking it, the model for the page's importer |
| `assets:39` | feature | use | The type enum is append only |
| `assets:55` | feature | use | `RegisterAssetPipeline` |
| `assets:56` | feature | use | Manager extensions, for the second exercise |
| `assets:136` | feature | use | Import settings, for the first exercise |
| `assets:218` | feature | use | The feature test fails when a registered type has no asset |
| `assets:382` | code | use | The `Asset` base class |
| `assets:386` | code | use | Loaders registered by a module, `TakeBytes` |
| `assets:543` | rule | use | Report memory per pool |
| `assets:552` | rule | use | Loaders reject garbage without crashing |
| `assets:554` | rule | use | A new document type records its references, for the third exercise |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Building Strata from source and running one test | `core/first-change` | must |
| Adding a component, its registration and the feature test's minimum | `world/tutorial-component` | must |
| The `Asset` base class, loaders and their registry | `assets/loading` | must |
| Importers, `RegisterAssetPipeline`, settings and versions | `assets/importing` | must |
| `.meta` files and handles | `assets/handles-meta` | must |
| Loaders that reject truncated and garbage bytes | `assets/robustness` | must |
| UTF-8 | `basics/bytes` | must |
| The finalize contract | `assets/uploads` | helps |
| References a document records | `assets/references` | helps |
| The feature test in full | `engineering/feature-test` | helps |
| Corruption sweeps | `engineering/test-program` | helps |

**Starting state.** The engine's source at the pin, built as `core/first-change` teaches, with no patch applied: the
tutorial's patch starts from the pin (`startsFrom` `{"pin": true}`), not from the WindZone chain of
`world/tutorial-component`.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
