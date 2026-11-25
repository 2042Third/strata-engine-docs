# Notes: assets/handles-meta

## New terms

None. The six terms of the brief are defined in bold on the page.

## Requests

None.

## Since

0.3.0: the handle, the `.meta` file and derived sub-asset handles are the asset pipeline's base; the page has no older tag to cite.

## Not verified

- Unity's `.meta` file holding a globally unique identifier: stated from the brief, linked to the manual's front page only.
- Unreal keeping an asset's identity inside its package files: from the brief, no source cited at the pin.
- The shortest-path rule of copied files was read in `FindDuplicateHandles`; the file manager names ("Name - Copy", "Name (1)") come from the code comment.
- `RemoveUnusedCacheFiles` drops the cache files that name no valid handle: read from its call and name, its body was not read.
- The collision chance (about 1 in 37 million for one million assets) is the page's own arithmetic, not an engine fact.

## Findings not applied

- `new:1` (the header's line numbers): applied; the page cites `AssetRegistration.h` by the lines that hold the declarations.
- `assets:72` (built-in assets never evicted): not stated; the page says only that built-ins are added as memory assets.
- `assets:456` figure (file, `.meta`, cache file, sub-assets, built-ins): drawn as one Mermaid diagram of the map, without a cache-file-per-sub-asset picture; the worked example shows that name in text.

## Clerk

- Nothing asked.
