# Notes: draw/batching

## Since

0.3.0: the sort key, batches and the draw list, material-free instancing and parallel extraction are in the 0.3.0 rows of the render-scene inventory (the byte-skipping radix sort came later, Roadmap.md:172); indirect arguments and buckets 0.4.0.

## New terms

None proposed. Defined from the brief's list: draw list, draw entry, batch, bucket, sort key, radix sort (LSD), indirect draw, material-free instancing, first instance, base instance, SV_VulkanInstanceID.

## Requests

- Words used without a glossary term and accepted by the lint: none open.
- Figures: none (one Mermaid diagram). The brief's figure rows (render-scene:394, :440) are not drawn: the key is a table, and the 1,000-cube comparison needs two pictures of the same image (project and `BatchAcrossMaterials` off, a renderer switch).

## Not verified

- Why the 10,000 distinct meshes need 8 draw commands (only the measured value is stated).
- That placing often-changing fields low shrinks the draw list's changed range: stated as a consequence of the sort order, not as the engine's documented intent.
- The cube's index count and the exact value of a cube's key (mesh slot 5 is an example, not a measured slot).
- The two Further reading entries beyond the Vulkan specification are cited from memory without links.

## Findings not applied

None open in the brief. The perf values come through `:value` keys. The brief's "trace it yourself" item is exercise 4; the toy is 90 lines, as the sketch rules require.

## Clerk

- Nothing to admit. The perf numbers: tools/reference.py render now writes the keys perf.<name>.<Measured|Budget|Unit> into values.json; the page states them in prose naming StrataTests/Perf/Budgets.json and may use the keys.
