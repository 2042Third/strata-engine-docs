# Part review of `make/reflections`

- step: six command tabs passed entity names (`Sky`, `Post Process`, `Room Probe`) as `entity` in `parameters`, which takes only IDs; they now use `entityName`.
- step: step 18's `entity.duplicate` listed the names `Room Noon` and `Yard Noon` in `entities`; it now lists their IDs as placeholders.
- gap: the brief's not-done item on cube-map textures was missing; the probe section now says that a capture is one flat `.hdr` picture of the whole sphere and that the renderer makes the cube while the game runs (`RendererComponents.h:198`).
