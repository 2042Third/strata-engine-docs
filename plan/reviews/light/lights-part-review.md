# Part review: light/lights (group 2 of 3)

- order: the rule "One sun per frame" gave the sun "a set of shadow cascades" with no word on what a cascade is (homed later in `light/sun-shadows-1`); the sentence now says they are shadow images that each cover one range of distances from the camera.

Checked at the pin and holding: the component defaults (`Strata/src/Strata/Renderer/RendererComponents.h`: 3 lux, 10 cd and 10 m, 20 cd and 15 m, the rect light's 1 by 0.5 m, 25 nits and 10 m, `c_MaxSourceRadius` 2, `ShadowSoftness` 0.53), `LightRecord` 128 bytes, `LightData` 64 (mirrored in `Strata/shaders/Include/Scene.slang`), `LightShape` 48, `c_MaxChanges` 65,536, the rect bound (range plus the half diagonal), the preview sun's 55 degrees, the frame's default sun (0, -1, 0, 0) of zero color, the sky loop's first active light, the glTF ranges (10 sqrt(I), at least 0.1 m, the import scale, cones 1 to 89 degrees) and the test suites named.
