# Notes: gpu/shaders

## New terms

None proposed.

## Since

0.3.0: shaders have been embedded SPIR-V since 0.3.0 (plan/inventory/render-core.md, row 125); the page's subject is older than the first tag.

## Requests

- A generated value `shaders.includeCount` (the number of files in `Strata/shaders/Include/` at the pin; 40 by listing). The page uses `:value{key="shaders.includeCount"}`.
- External host `shader-slang.org` for the Slang user guide (cited without a link in Further reading).

## Not verified

- The folder of the generated header in a build tree (`EmbeddedShaders` under the `Strata` folder of the build folder): derived from `CMake/StrataShaders.cmake` (`CMAKE_CURRENT_BINARY_DIR`), not seen in a build.
- That `Architecture.Shaders` needs no graphics card (inferred from its reading sources only).
- The 0.7.0 look-dev set's location, so the page says "the saved set of the earlier release" without a path.

## Findings not applied

None: the brief listed no open findings. The brief's inventory slip (39 include files) is avoided by a generated value.

## Clerk

- No term asked.
- Admitted to external-hosts.txt: shader-slang.org.
- Left for the planner: the generated value `shaders.includeCount` (a change to tools/reference.py render).
