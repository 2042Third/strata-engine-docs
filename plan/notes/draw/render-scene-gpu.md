# Notes: draw/render-scene-gpu

## New terms

None proposed. The page defines the glossary terms GPU copy, culling record, mesh table (with material table), resident and upload budget.

## Since

0.4.0: the inventory dates the shared copy, the proxy log and the residency rule to 0.4.0; release and recycling came in 0.7.0.

## Requests

None. The page has no figures file: both pictures are Mermaid diagrams.

## Not verified

- Why a texture that streams levels does not rebuild a material: the header says it does not; the reason given (the table names textures by bindless index, which stays) is read from the header comment, not traced.
- That a direct write "races with frames that still read the old data": inferred from the staging order rule, not from a failing case.
- That thumbnails draw one small scene after another through recycled buffers: taken from the class comment of the cache.
- The 65,536-entry log capacity is not on the page (inventory only).

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Nothing asked.
