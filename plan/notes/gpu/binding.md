# Notes: gpu/binding

## Since

Binding layouts, the key cache and the bindless table are in the inventory as 0.3.0 features (render-core:94, :100, :127); the texture table is 0.4.0 in the inventory, the page's learn lines concern 0.3.0 material.

## New terms

- Constant buffer: a buffer of values a shader reads at a `b` register, the same for every thread of a draw (home: gpu/binding; the glossary entry of new:41, apart from the volatile constant buffer). Defined in bold on the page; the brief's term table does not list its id.

## Requests

- Hosts: none new (one link to github.com).
- Words: none (every word found in the lists after rewording).

## Not verified

- The Direct3D 11 slot model and the Vulkan and Direct3D 12 descriptor models are described from general knowledge, not from the pin.
- The reason of the push constant rule beyond the guide's note on other targets (a conversion gives push blocks registers equal to their C++ slots).
- That the build's Vulkan descriptor sets need every slot filled; the page says only that the layout's shape is fixed.
- Compile time of a new pipeline is stated as "takes milliseconds" in general, not measured.

## Findings not applied

- None: the brief listed no open findings.

## Clerk

- Refused: constant buffer, which the glossary homes on gpu/resources-lifetimes (only its home words it); a move of its home is the planner's.
