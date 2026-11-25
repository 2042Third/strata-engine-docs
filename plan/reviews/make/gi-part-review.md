# Part review of `make/gi`

- step: five command tabs passed `Post Process` and `Wall East Low` as `entity` in `parameters`; they now use `entityName`, as `tutorials/make/gi.tutorial.json` does.
- unclear: the page says the presets Low and Medium draw no global illumination, then gives walls "40 cm at Low" and an exercise "at Low"; at the pin the GI has its own levels Off, Low and High (`RendererQuality.cpp:57`, `:244`), High and Ultra use High, and only a Custom quality chooses Low; the thin-walls item now says so and the exercise names the GI's Low level.
