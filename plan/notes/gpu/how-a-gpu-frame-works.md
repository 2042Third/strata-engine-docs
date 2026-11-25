# Notes: gpu/how-a-gpu-frame-works

## New terms

- Rasterization: the stage that finds which pixels a triangle covers, taking each pixel's center as one sample. Home: this page. Aliases: rasterizer.
- Bandwidth: how many bytes per second a memory can move. Home: this page. Aliases: memory bandwidth.

## Requests

- Words: rasterization and bandwidth (proposed as terms above; the word-list findings remain until admitted).
- Hosts: vulkan-tutorial.com and fgiesen.wordpress.com (cited in Further reading without links).
- Figure showcase-viewport uses a layout file layouts/scene-view.ini that the figure tool must supply.

## Since

- since 0.3.0: the frame-pacing row of the inventory (render-core:35) dates from 0.3.0.

## Not verified

- General GPU facts (wave sizes 32 or 64, register file numbers, bandwidth of a card) are textbook examples, not Strata facts.
- Strata's rejection of Vulkan below 1.2 at startup shows only as a log reason in the adapter choice (VulkanGraphicsDevice.cpp:642-644).
- The Vulkan present-mode names in the table follow the Vulkan specification, not checked at the pin beyond the three modes in code.

## Findings not applied

- None: the brief listed no open findings.

## Clerk

- Admitted terms: rasterization (aliases rasterizer, rasterize, rasterized, rasterizes, rasterizing; gpu/text asked the same words) and bandwidth (alias memory bandwidth), both homed here.
- Admitted to external-hosts.txt: vulkan-tutorial.com, fgiesen.wordpress.com.
- Left for the planner: `layouts/scene-view.ini`.

## Figures

- showcase-viewport (provisional build, not published; keeps its waitsFor): round 1 used the camera the project opens
  with and showed only a hazy horizon, no props. Round 2 sets the camera at (26, 3, 16) toward (6, 2.2, 8), field of
  view 50, with the sun behind it: the oil tank, the bus, drums, the hill and the sky show, with the grid, a camera's
  frustum and icons over them. The Scene panel alone at 797 × 499 pixels reads at the page's width.
  The paragraph's "open the editor and look" is true of a moved view only: the reader's first view is the horizon.
- showcase-viewport at v0.8.0 (pin 319075e3): waitsFor removed (the pin has editor.screenshot), taken in one round
  with the same recipe and published. It shows the rusty tank, the orange bus, red and grey drums, rocks along a sandy
  hill and a blue sky, with the grid, a camera's white frustum and icons over them; caption, alt and shows hold.
