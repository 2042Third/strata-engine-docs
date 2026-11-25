# Part review: `make/materials`

- unclear: step 2 said a name with `metal` holds data, yet `Metal032_Color` comes out `Color`; the importer matches whole words split at `_`, `-` and capitals (`TextureImporter.cpp` `GetNameTokens`), and one sentence now says so.
- wrong: the Albedo step's fallback said to choose the Scene view's chip, "not the Game view's"; the Game view has no debug views (only `ViewportPanel.cpp` draws the chip), and the line now says so.
- step: the audit's last step said "Select `Wall`, press **Delete**" while Coin Run already holds a `Wall` under `Walls` (`make/scenes-entities`); the step now names the new top-level `Wall`, so the reader does not delete a wall of the level.
