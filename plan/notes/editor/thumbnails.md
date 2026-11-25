# Notes: editor/thumbnails

## New terms

- key (thumbnail key): one number, a hash of the version, the image size and the handle and content stamp of an asset and everything it depends on; a thumbnail is current while its stored key equals the computed one. Home: editor/thumbnails. Aliases: thumbnail key, cache key.

## Requests

- No figures file: the only picture is a Mermaid diagram.
- Hosts: none requested (Further reading names a source without a link).

## Not verified

- Who else uses each alternative technique in the table is stated generally, with no named product.
- The GPU-driven rendering cost of one thumbnail in milliseconds was not measured; the page gives none.

## Findings not applied

- Brief says PNG files are "named by the key": at the pin they are named by the asset handle (`ThumbnailCache::GetFile`); the key is stored in the index file (`Index.json`, with `Version`), which is read as empty when its version differs from `c_Version`. The page states the code's behavior.
- The brief's open findings list was empty.

## Since

- ThumbnailCache: 0.3.0, from the engine inventory (editor-core line 256, the "since" column); not re-derived from tags.

## Clerk

- Admitted Key (editor), homed here, with the alias thumbnail key; cache key is a general phrase and was left out.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
