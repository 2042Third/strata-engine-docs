# Brief: `image/motion-blur`

| Field | Value |
| --- | --- |
| Title | Motion blur |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `image/taa` |
| From | render-image ch. 10 (first half); 1.7 (tile max, neighbor max, the gather, the CPU profile model, shutter-angle and cut rules), concept 16, diagram 19; split from `image/motion-blur-dof` |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/motion-blur` — Motion blur

**Covers.** The job: blur what moves while the shutter is open, as a film camera does, without blurring the UI and
without blurring across a cut. The page starts from `render-image:513`: the Third-Person course while the camera turns,
with motion blur off, at a 90 and at a 180 degree shutter, and a crop of the far course and the robot. The section "The
problem and how engines solve it": the shutter angle, the blur a sample-and-hold display adds by itself, scatter against
gather, McGuire's reconstruction with tile maxima and neighbor maxima, depth-aware weights, static stratified offsets
against temporal noise. Strata's variant (diagram `render-image:472`): the tile maximum, the neighbor maximum with its
diagonal rule, a gather along two directions, depth weights, and no blur under a pixel at 1080 rows. The toy is a
gather along each pixel's own motion in about 30 lines.

The real code: code #28 (`GetBlurVelocity` with the shutter's share, the clamp and the sub-pixel drop; the gather's
depth weights), the CPU model `GetMotionBlurProfile` that the tests compare with, and the CPU side `RenderMotionBlur`
with its conditions: no motion history on the first frame, after a resize or on a camera cut. Which views blur
(`new:32`): only the game's camera while the game plays; the editor camera, captures and thumbnails never do, while
depth of field shows in every view and capture through a scene camera. The blur mask in the output's alpha stops the
TAA's sharpening where motion blur or depth of field blurred. The fields `MotionBlur`, `MotionBlurShutterAngle` and
`MotionBlurMaxLength`; the `MotionBlurSamples` quality row and the players' row are named here, with their cost, and the
rows as a system are taught in `image/quality-settings`; the motion view of `draw/motion-vectors` helps to read the
blur. How it is tested: `GPU.SceneRenderer.MotionBlur`, `Renderer.PostProcessMath`. Exercises: a streak's length
predicted and measured at two shutters, and the editor camera that stays sharp (`new:23`); the frames that never blur
traced to their lines (`new:24`). At the end the reader can set a shutter, predict the blur's length in pixels, and say
why a cut and the UI are never blurred.

**Leaves out.**

- How motion vectors and the motion history are made, and the motion view → `draw/motion-vectors`
- Depth of field, the other effect that writes the blur mask → `image/depth-of-field`
- Quality rows, presets and the players' rows as a system → `image/quality-settings`
- Motion blur in a game's look → `make/look`

**Fit.** `fits`: about 3,650 words against M (3,000). The reconstruction (tile and neighbor maxima, the gather with
depth weights), with one excerpt in two files, the CPU model, one diagram and one figure with its sweep, takes the most
words, then the two exercises.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:378` | concept | home | Motion blur: shutter angle, sample-and-hold blur, tile-max and neighbor-max reconstruction, depth-aware scatter as gather, stratified offsets; the errors (blurring a cut, blurring the UI) |
| `render-image:175` | feature | home | The three shaders and `Include/MotionBlur.slang`; `EnsureMotionBlurResources` and `RenderMotionBlur` (`SceneRendererPost.cpp:538-695`); the CPU model `GetMotionBlurProfile` (`PostProcessMath.cpp:212-267`); the fields and their defaults; the conditions (`SceneRenderer.cpp:2989, 3598-3607`) |
| `render-image:189` | feature | home | The blur mask in alpha: no sharpening where depth of field or motion blur blurred (`c_TonemapBlurMask`, `MotionBlurParameters::SourceMask`) |
| `render-image:422` | code | home | `Strata/shaders/Include/MotionBlur.slang:25-39`: the blur velocity with the shutter, the clamp and the sub-pixel drop; with `MotionBlur.comp.slang:25-54`, the depth-aware sample weights |
| `render-image:579` | rule | home | Motion blur skips the first frame and camera cuts, and never blurs the UI or the overlays |
| `render-image:472` | figure | home | Diagram: tiles, the neighbor maximum with the diagonal rule, samples along two directions, depth weights |
| `render-image:513` | figure | home | Motion blur off, at 90 and at 180 degrees on `tp.live.turn` (the off and on, and the sweep), with a crop of the far course and the robot |
| `render-image:715-717` | term | home | Shutter angle; tile max and neighbor max; sample-and-hold blur |
| `new:32` | feature | home | Which views blur: only the game's camera, and only while the game plays, in the live views (the Game view, a Scene view through the game's camera); the editor camera and renderers of single images (captures, thumbnails) never blur. Depth of field is a lens's, not a moment's: every view and capture through a scene camera with depth of field shows it, playing or not. Evidence: `StrataEditor/src/Editor/ViewportRenderer.cpp:222-227`; `Strata/src/Strata/Renderer/SceneRenderer.h:440-445`; `Docs/Manual/Camera.md:122-123, 147-148` |
| `new:23` | hands-on | home | Exercise (predict, then run): predict from `GetBlurVelocity` how long a streak the camera's turn leaves at a 180 and at a 90 degree shutter, then run what the look-dev shots `tp.live.turn.mb180` and `tp.live.turn.mb90` run (the Post Process's MotionBlur and MotionBlurShutterAngle, a turn by the `Gameplay/Look` action, a live capture) and measure it; then look at the same turn through the editor camera, which never blurs. Evidence: `Strata/shaders/Include/MotionBlur.slang:25-39`; `Tools/LookDev/Shots.json:40-41`; `StrataEditor/src/Editor/ViewportRenderer.cpp:222-225` |
| `new:24` | hands-on | home | Exercise (trace it yourself): find the frames that never blur and the line that decides each: `motionBlurWanted` (the view's option, a HDR output, the component's field and its shutter), the camera cut from `IsCameraCut`, the motion history, and the condition that runs the pass. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2989, 3010, 3598`; `Strata/src/Strata/Renderer/SceneRenderer.h:1739` |
| `render-image:512` | figure | use | The motion view while the camera turns; its home is `draw/motion-vectors` |
| `render-image:171` | feature | use | The velocity target that the blur reads; its home is `draw/motion-vectors` |
| `render-image:238` | feature | use | The players' `MotionBlur` row; its home is `image/quality-settings` |
| `render-scene:173` | feature | use | Motion vectors as the render-scene area gives them |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Temporal anti-aliasing: the history, camera cuts, sharpening | `image/taa` | must |
| Motion vectors and motion history | `draw/motion-vectors` | must |
| Compute shaders: thread groups, shared memory | `gpu/compute` | must |
| Strata's depth conventions and view distance | `gpu/coordinates` | must |
| Noise and sampling patterns: stratified offsets | `basics/math-probability` | helps |
| Players' graphics options; presets and traits | `image/quality-settings` | helps |
| Running an editor command from a line to paste (the exercise) | `start/how-to-read` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `sample-and-hold-blur` | Sample-and-hold blur | - |
| `shutter-angle` | Shutter angle | - |
| `tile-max` | Tile max | neighbor max |
