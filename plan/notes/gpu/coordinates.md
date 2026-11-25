# Notes: gpu/coordinates

## New terms

None proposed. Terms defined in bold: space, framebuffer (as the brief's glossary), texture coordinates, viewport flip, fullscreen triangle, winding order, winding, reversed Z, infinite far plane, depth test functions, primary camera.

## Since

Coordinate conventions and CameraComponent exist from the first renderer; since 0.3.0 (first tag).

## Requests

- Words for the extra list: UV (used in code names and the title only), logarithmic.

## Not verified

- The approaches table's "Used by" column names no other engine (no citations); the claim about log depth costs is general knowledge, cited only in Further reading.
- The precision table is computed with the page's sketch formulas (float spacing over the slope), not read from the engine.
- NVRHI's flip (`VKViewportWithDXCoords`) was read in the vendored submodule on disk; the pin's git tree holds no vendor files, so the page names the function without a path.
- No figure: the chain of spaces is a Mermaid diagram; the precision plot is a table.

## Findings not applied

- The brief lists no open findings.
- Brief items not carried: the Inspector figure (`scene-ecs:474`) is a use-figure, not requested here; the plot of `render-core:507` is a table.

## Clerk

- Admitted the term texture coordinates, homed here (aliases UV, UV coordinates), for the word UV; admitted logarithmic to extra-words.txt (basics/numbers).
