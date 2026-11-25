# Part review: `make/transforms-units`

- contradiction: the forward check read the Main Camera at (0, 2, 6) aiming at the origin, but `make/scenes-entities` step 5 moved Coin Run's camera to (0, 16, 13), Rotation (-55, 0, 0); the paragraph now reads the reader's camera.
- step: "Drag the red ring a quarter of the way ... X shows 90" on the coin, which already has Rotation (90, 0, 0) from `make/scenes-entities`, so a quarter drag shows 180 or 0; the text now reads the 90 already there, drags a little and undoes.
- wrong: common mistake 3 linked `make/assets` as "Models, textures and sounds"; its title is "Bringing in assets".
- wrong: "The coin's turn is the `Spinner` script": the coins spin with the reader's `Coin` class (`make/first-script`); `Spinner` is the new project's example, so the sentence now says a turn like the coin's is in it.
