# Notes: light/sky

## New terms

None proposed. The glossary terms homed here (environment map, procedural sky) are defined in bold. The page also bolds "sky preset" and "double sun" as page-local terms; the clerk may admit them (sky preset: a stored bundle of sky light and sun values in real units, applied by lighting.applySkyPreset; double sun: the sun lighting a scene twice, once from a directional light and once from the map).

## Requests

- Extra word: illuminance (used 6 times in prose; the units page asked for it too).
- Figure `sky-sources` (project Showcase): variant `map` needs the sky light's EnvironmentMap set to one of the sample's HDR maps (Samples/Showcase/Assets/Lighting/Outpost); the recipe only sets Source, so the planner must choose the map and the entity name `Sky` (not tried).
- Figure `extract-sun` (compare, variants before and after): the `after` variant runs `lighting.extractSun`, but the page's Remove Sun step (`asset.setImportSettings` with `RemoveSun` true, which needs the map's asset id and a re-import) is not in the recipe; the planner must add it. The `before` variant also needs a map with a sun and no directional light.
- Figure `sky-presets` (Basic 3D, four variants): setup uses `lighting.applySkyPreset`; not tried.

## Not verified

- The Hosek-Wilkie, Preetham, Bruneton and Hillaire references in Further reading (authors, years, titles) are from memory of the public papers, not from the engine.
- Which sky settings the Showcase sample has, and that it has an entity named `Sky`.
- The Overcast sky's 7,700 lux and the Clear sun's 95,000 lux on the ground are the code's comments (`SkyPresets.cpp`), not measured; the sun-to-sky ratio of 0.17 is my arithmetic from them.
- Exercise 1's Lighting view legend text (a note "Sun : sky" under the legend) is read from `StreamingView.cpp`, not seen in the editor.
- That the default sun direction without a directional light is 45 degrees up: from the comment in `RendererComponents.h` (`SkyLightComponent`), not from `GetDefaultSunDirection`'s body.

## Findings not applied

- The brief's item for the HDR before/after figure (`assets:511`) is one figure with `render-direct:564`: done as the `extract-sun` compare.
- The brief lists the `HDRSun` import setting as `assets/texture-cooking`'s: the page names `RemoveSun` and links it, and teaches only the command side.
- The brief's "recomputed only when its parameters change": the code compares the whole parameter set exactly (`UpdateEnvironment`); the page says so.
- Brief's exercise "Extract Sun on an HDR map" (render-direct:648): not given as a separate exercise; the page keeps the double-sun check question and the figure instead, to stay within size M.
- The brief's "How it is tested" names GPU.ProceduralSky and Editor.Lighting: done, plus Asset.HDRSun.
- The "What went wrong before" section is omitted: no regression with a test was verified at the pin.

## Since

0.3.0: the sky light component and the environment map and procedural sources (inventory render-direct:151); Extract Sun and Remove Sun came in 0.6.0 and the presets in 0.7.0.

## Figures

Photographed 2026-11-18, three rounds in all, every figure published.

- `sky-sources`: the Showcase has no sky map (its HDR files are probe bakes), so the recipe moved to the ThirdPerson
  sample's `Scenes/Course.stscene`, whose `Sky` uses the `kloofendal_48d_partly_cloudy_puresky_1k` map (cooked with
  `RemoveSun`, its sun extracted into `Sun`). Round 1 (scene camera) showed the game HUD and little sky; round 2 hid
  `HUD` and `Menus` and raised the camera's aim; round 3 centered the course. The sunlit ground changes little between
  sources, so the caption now says the skies differ and the ground far less.
- `sky-presets`: an explicit camera brings the cube and its shadow closer. Hazy's shadow is barely softer than Clear's,
  so the alt says "almost as dark" instead of "softer".
- `extract-sun`: also on the ThirdPerson course. Both variants set `RemoveSun` false and remove the `Sun`'s
  `DirectionalLight` (the map's sun, no light); `after` runs `lighting.extractSun` then sets `RemoveSun` true, the
  Inspector button's two steps. The sun is outside the frame, so the alt no longer mentions a sun disk.
- `extract-sun`, mended 2026-11-18 (words only, pictures kept): in `after` the tree casts no shadow one can see; the
  robot, sign, flowers, mushrooms and right-hand fence do, and an object out of frame casts the broad shadow at lower
  right, so the alt names those. The clouds darken from `before` to `after` because auto exposure moves from EV100
  0.79 to 1.80 (the results' `renderStats.exposure.ev100`), one stop, for the sunlit ground; the caption now says so
  and that the sun is out of frame.
- Retaken 2026-11-23 at v0.8.0 (319075e3), one round, recipes unchanged. `figures.py compare`: the four `sky-presets`
  pictures are identical; the `sky-sources` and `extract-sun` pictures differ in about 3 % of pixels by at most 27
  levels (mean under 0.02), noise only. The skies, shadows and exposure still match the captions and alts, so publish
  kept the files and stamped them checked at the new pin.

## Clerk

- Admitted terms homed here: sky preset, double sun.
