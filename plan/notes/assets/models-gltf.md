# Notes: assets/models-gltf

## New terms

None proposed.

## Since

`since: 0.3.0`: the inventory dates the importer's entity template, animator root and skeleton to 0.3.0 (`animation:68`, importer rows); version 10 and 11 came later and are named in the page by version number.

## Requests

- Extra words: `vertices` (plural of the glossary term vertex; used 10 times), `accessor`, `accessors` (glTF's name for a typed view of buffer data; defined in place by use on the toy's page section).
- External hosts: none needed; Further reading cites the glTF 2.0 specification (Khronos Group), the meshoptimizer project and Garland and Heckbert's 1997 paper without links.
- Figures: none; the one diagram is Mermaid.

## Not verified

- The editor's asset inspector shows `importWarnings`: the brief says "the Asset tab"; the page names only the command `asset.info` for certain and says the inspector shows them.
- That the renderer uses a level's recorded error to choose levels at draw time (stated in one sentence; the draw part owns it).
- That the model records references and bounds through `ImportResult` (taken from the assets inventory, not re-read in the importer's code).
- That `ReadSettings` turns a bad value into a warning (read only from the call site in `Run`).
- That the editor copies a model's external files using `FindExternalFiles` (the page says it lists them; `asset.import`'s description says it copies the files a model reads).

## Findings not applied

None: the errata `new:11` (version 9 in `Docs/Architecture.md`, 11 in the code) and `new:12` (header line numbers) are applied. `Asset.Gltf` test for the cooked mesh version and the quote of `Mesh.h` lines 107-113 are on the page.

## Clerk

- Admitted to extra-words.txt: accessor, accessors (not a term: the page explains them in passing, in no bold sentence). vertices was already there.
