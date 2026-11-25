## New terms

None proposed. The page defines `debug-view-gpu` (the brief's glossary term) in bold as "debug view".

## Requests

- Names for `tools/data/names.txt`: RenderDoc, Nsight (capture tools; the page also uses them in the prerequisites and variations).
- A host for `tools/external-hosts.txt`: renderdoc.org (Further reading link).

## Not verified

- Capture-tool steps (RenderDoc launch, Nsight frame debugging activity, the event tree) were not run on a GPU; the markers are checked in the code (NVRHI writes Vulkan debug labels when VK_EXT_debug_utils is present).
- Nsight showing the same marker tree and adding card counters, and macOS capture tools: general claims, not checked at the pin.
- The editor's log line about validation: only the "validation enabled" suffix of the device line is checked in code.
- A figure of a validation error as a text capture is not requested: it needs a patched build, which a capture may not use.
- Which page teaches the shadows view and the GI views: taken from the sidebar ids (light/sun-shadows-1, indirect/ao, indirect/gi-voxels).
- v0.8.0 pin move: the views specular, diffuse, clusters, culled and wireframe (menu names and legends in StrataEditor/src/Panels/ViewportPanel.cpp, colors in StreamingView.h) and the capture's renderer switches (ViewportRenderer.cpp) were read in code, not run; their reading pages (light/brdf, light/many-lights, draw/occlusion, draw/lod, light/energy, image/encoding, indirect/gi-cascades, draw/mip-streaming, indirect/ibl) were chosen from the sidebar ids and the pages' subjects.

## Findings not applied

None: the brief lists no open findings after its terms table.

## Clerk

- Admitted to names.txt: RenderDoc, Nsight; to external-hosts.txt: renderdoc.org.
