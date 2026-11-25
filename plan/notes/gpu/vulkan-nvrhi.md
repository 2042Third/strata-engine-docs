# Notes: gpu/vulkan-nvrhi

## New terms

None proposed. The fourteen terms the brief homes here are defined in bold on the page (RHI, NVRHI, Vulkan,
MoltenVK, instance, physical device, logical device, validation layer, surface, UNORM, sRGB formats, semaphore,
immediate command list, device lost).

## Requests

- Host: `docs.vulkan.org` (the Vulkan Guide), `vulkan-tutorial.com` and `bgfx.github.io`, cited in Further
  reading without a link until the hosts are allowed.

## Since

`since: 0.3.0`: the inventory dates `VulkanGraphicsDevice`, the swap chain, device selection, frame pacing and the
`Renderer` hub to 0.3.0 (plan/inventory/render-core.md, lines 28 to 37 and 61 to 64); the deferred acquire wait is 0.4.0.

## Not verified

- Statements on other engines and libraries (Further reading's bgfx entry; the alternatives table's "who uses it" cells are generic).
- The guarantee that `FIFO` is always supported (the code comment says so; the specification was not read).
- That the validation layer costs time on every call (general knowledge, no measurement at the pin).
- Which driver gives which result for a listed but unloadable layer: taken from the code's comment.

## Findings not applied

None: the brief carries no open findings.

## Clerk

- No term asked.
- Admitted to external-hosts.txt: vulkan-tutorial.com. Not admitted: docs.vulkan.org (its front page answered a redirect notice) and bgfx.github.io ("Site not found"); left for the planner.
