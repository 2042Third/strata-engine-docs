# Notes: light/area-lights

## New terms

None proposed. The four homed terms (area light, lobe widening, LTC, source radius) are defined in bold; "angular diameter" is the alias and stands in plain text.

## Since

0.8.0: sized highlights (`GetSunLobeAlpha2`, `GetSourceLobeAlpha2`, the `SourceRadius` of point and spot lights, the sun's Angular Diameter) and the rect light with Light Surface and `lighting.makeAreaLight` are all in the 0.8.0 release notes (`Docs/Releases/0.8.0.md`, "Rect lights", "Highlights like in a drawing", "Shading").

## Requests

- Figure `sun-angular-diameter` (variants `diameter-0`, `diameter-053`, `diameter-10`; shot `lookdev.mirror`, crop of the polished ball, sun `ShadowSoftness` 0, 0.53 and 10): not taken. The recipe sets `ShadowSoftness` on the entity `Sun` of `Scenes/Mirror.stscene` (the sun exists in `Tools/LookDev/LookDevScene.json` at the pin); whether the sun's glint lies in the shot's frame was not checked.
- Figure `lantern-source-radius` (variants `radius-0`, `radius-005`, `radius-03`; shot `lookdev.lantern.wet`): not taken. The recipe sets `SourceRadius` on the entities `Lantern` and `Lantern 2` of the Specular scene, as the shots `lookdev.lantern.wet.sized` do at 0.06.
- No words for `tools/data/extra-words.txt`; no hosts; no layouts.

## Not verified

- The look of both figures: the captions say what the physics predicts (point, disk, wide glow), not what a picture shows. No picture was taken.
- The claims about the representative point method (the 2013 course notes of Unreal Engine 4) and about LTC's published properties (closed form over a polygon, no sampling) rest on the cited papers, not on the pin.
- The sentence "The records of lights are built on the main thread" rests on the threading rule of `AGENTS.md` and on `RenderLights` following component signals; the thread of each call was not traced.
- The numbers from the release notes (2.7 % opaque pass at Medium; 1.1 to 1.4 times the exact light at roughness 0.25 seen 87 degrees off the normal) and the Manual's "a few hundred arithmetic operations and twelve table reads": quoted, not measured again.
- Passive and noun-stack warnings (11 and 7) were left: they stand in sentences whose actor is a quantity ("the share is multiplied by").
- The markterms mark of "nits" is `lux` (the glossary's alias of that term); the sentence keeps its sense.

## Findings not applied

- The brief lists no open findings.
- Brief item `new:7` (disk lights, "only if their stage lands"): they did not land at the pin; the page says so under "What Strata does not do".
- Brief item `render-direct:665` (exercise "sketch where a rect light enters"): applied as exercise 4 with a written answer, no code solution.
- The brief's evidence lines (`Forward.frag.slang:244`, `:276`, `SceneRenderer.cpp:2573`, `PBR.slang:143`) are of the old commit; the page uses the pin's (`Forward.frag.slang` 393, `SceneRenderer.cpp` 2691, `PBR.slang` 24 and 143).

## Movable claims

Statements a later release may change:

- The cost of a scene with a rect light: the showcase's opaque pass takes 2.7 % longer at Medium; the Manual's few hundred operations and twelve table reads for each pixel a light reaches.
- The fit's error: 1.1 to 1.4 times the exact light at roughness 0.25, seen 87 degrees off the normal.
- The limits of the sizes: the Angular Diameter within 0 to 10 degrees (default 0.53), the source radius within 0 to 2 m (default 0), a rect light's units Nits and Lumens, `LightData` of 64 bytes and `LightRecord` of 128 bytes.
- The table: two layers of 64 by 64 entries read with four loads.
- No disk lights and no other shape than the rectangle (disk lights are planned for a later wave); a source radius gives no diffuse light and no softer shadow.
- Known issue: rect lights are not yet in global illumination, so a scene with it counts a light surface's light twice.
- The sizes the figures' text gives from the Manual (a lantern's bulb 0.03 to 0.06 m, a fire pit's flames 0.2 to 0.3 m).
- Test names of `GPU.SceneRenderer.Lighting`, `Renderer.RenderScene`, `Renderer.AreaLights` and `GPU.SceneRenderer.AreaLights` quoted in "How it is tested" and "What went wrong before".

## Figures

Both taken at v0.8.0 (pin 319075e3) and published after three rounds each.

- `sun-angular-diameter`: round 1 (shot `lookdev.mirror`) showed no highlight at all: the Mirror scene's balls are rough red (0.6), and the sun stands behind the camera. Round 2 framed the sun's reflection in the polished floor (Floor Polished, roughness 0.02) at fov 30: 0 and 0.53 looked alike, and auto exposure darkened the 10-degree picture by 2.5 EV. Round 3: fov 18 and one manual exposure (Exposure -12.9, the auto value of the first two). The 0.53 spot is a little larger than the 0 spot, the 10-degree glow covers most of the frame; the glow's center is still clipped white, so the lower peak does not show and the caption no longer claims it. Page words to change: "over a polished ball" before the figures should say "in a polished floor". A lower exposure (about -16) would show the 10-degree glow's lower peak as gray while the point stays white, at the cost of a near-black floor.
- `lantern-source-radius`: round 1 (shot `lookdev.lantern.wet`, fov 50) showed the reflection a few pixels wide. Round 3 aims a 10-degree camera at the reflection of Lantern 2 and fixes the exposure (-7.85, the shot's auto value). Radius 0 gives a thin streak, not a point; the caption says so. The lantern itself is out of the frame, so the sentence after the figures, "the lantern does not look any softer", cannot be judged in them.

Mended after a viewer's review (2026-11-23):

- `sun-angular-diameter`: the caption now says that the small spots clip to white and that the wide glow spreads the same light, so the brighter-looking 10-degree frame no longer seems to contradict the example's 1,100 times lower peak. The page's "over a polished ball" (line 267) still needs "reflected in a polished floor": the Mirror scene has no polished ball (its balls are rough red, roughness 0.6).
- `lantern-source-radius`: fov 10 to 6 enlarges the streak 1.7 times, so the 0.05 m streak's extra length (about 19 % at the earlier framing: 222 to 265 px of 720 above the background) shows; the caption says a bulb's radius makes it only a little longer. The page's sentence after the figures (line 275) claims the sets never change rough surfaces' brightness or shadows, but the close frames hold neither; it would need "These close views show only the highlight; the same settings leave rough surfaces and shadows unchanged."
