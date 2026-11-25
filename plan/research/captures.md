# Research: how pictures of Strata are taken, and how the book takes them

Surveyed at `main` 822a7a46 of `G:/GameEngineAI` (read only; nothing was built or run). Paths are relative to that
repository. "DG" is `Docs/DeveloperGuide.md` (line numbers of this commit), "LD" is `Tools/LookDev.py`, "Shots" is
`Tools/LookDev/Shots.json`, "VC" is `StrataEditor/src/Editor/EditorViewportCommands.cpp`.

The situation in one paragraph: every picture of the 3D scene Strata takes today goes through **one editor command,
`viewport.capture`**. It renders a frame of its own through a separate capture renderer (`ViewportRenderer`), off screen.
That works in a headless editor (`--headless`: no window, GPU on) and needs no panel. It waits until the picture is
complete, meaning assets loaded, mips at the wanted level, text glyphs ready, exposure settled, TAA history full and GI
settled. It writes a PNG and returns a JSON report saying what was still missing. Two harnesses are built on it:
`Tools/LookDev.py`, which drives headless editors through `StrataCLI` from a table of shots (`Shots.json`), and editor
command scripts (`StrataEditor --commands x.json --quit-after-commands`), which the Showcase uses for its committed
screenshots and its render regression (`ShowcaseRenderCommands.json`). A capture can also be *live*: it reads back
what the Scene or Game view actually presented while the game played. That needs a windowed editor. Pictures of the
**whole editor** (UI included) exist only as `--screenshot <png>`, which saves the back buffer on the last frame of a
windowed run. There is no command for them. The **runtime** (exported game) has `--resolution WxH --seconds N
--screenshot <png> --quality <preset>`. GPU unit tests never write images (only `ImageWriterTests` calls `SavePNG`):
they compare pixels in memory, so they are a source of *settings* for exact pictures, not of pictures.

---

## 1. How a picture is taken, step by step

### 1.0 Common ground (every route)

- **Binaries:** `build/<preset>/bin/<Config>/StrataEditor(.exe)`, `StrataCLI(.exe)`, and for exported games
  `<project>/Build/<Game>(.exe)`. Use a Release build for pictures. LookDev's baselines are Release builds (DG 768-771).
  A Debug build renders the same pixels, but more slowly.
- **Never open a sample in place.** Copy it without its `.strata` folder, because `.strata/EditorViewport.json` holds
  the person's editor camera, debug view and Scene-view quality per scene (DG 3466-3474). LD `prepare_project` copies
  with `shutil.ignore_patterns(".strata")`. The look-dev project and the `basic3d` project are *made* by command scripts
  in a work directory (LD 155-188).
- **Private session directory:** set `STRATA_SESSION_DIR` to a fresh path for every run (LD 69-71: `<temp>/StrataLookDev-<pid>-<time>`).
  The editor makes the folder private itself. This keeps the run away from the person's editors and tokens. Also set
  `STRATA_EDITOR_PATH` to the editor binary, so `StrataCLI launch` starts that build.
- **Recent projects:** scripted runs (`--frames`, `--commands`) only read the user's recent-projects file (DG 3509).
  `STRATA_RECENT_PROJECTS` points the editor at another file (DG 3507). Point it at a committed, controlled file for
  launcher pictures.
- **Output paths:** `viewport.capture {path}` is relative to the project directory or absolute. Folders are created,
  network and device paths are refused, and an existing file is an error unless `overwrite: true` (`CommandUtils::ResolveOutputPath`,
  DG 3847-3851). LookDev refuses outputs inside the engine's tracked tree (`is_inside_tracked_tree`, LD
  42-49). `build*` and `.worktrees` are allowed.
- **Serialize GPU work:** only one capture run should be on the machine at a time. Run it under
  `python Tools/PerfLock.py --label <who> --limit 90 -- <command...>`. A full look-dev run takes longer than the lock's
  default 25-minute limit (DG 757-759). The lock is an OS file lock in `<temp>/StrataPerfLock/`. It waits up to `--wait`
  minutes (default 30, then exit 75), ends the whole process tree after `--limit` minutes (exit 124), and
  `--status` names the holder (`Tools/PerfLock.py` docstring). The pictures themselves are deterministic under load.
  What contention breaks is the frame-bounded waits: `waitForAssets` gives up after 300 frames, and mips after 120. A
  picture taken under contention can then come back incomplete. That is why every capture must assert completeness (see
  `PICTURE_COMPLETE` below).

### 1.1 A scene shot (sample or look-dev scene) at a chosen size and anti-aliasing mode

**Route A: the look-dev harness (existing shots).**

```sh
python -I Tools/LookDev.py capture --build build/windows/bin/Release \
    --projects Showcase --shots "showcase.shot2" --sizes 1920x1080 --aa taa --repeat 2 \
    --quality high --output <out dir> [--work <dir> --keep-work]
```

What it does (LD 449-576):

1. It copies the sample (or makes `Basic3D` from the `basic3d` template, or `LookDev` from `LookDevScene.json`). It
   does this by running `StrataEditor --headless --no-automation --commands <script> --quit-after-commands --frames 36000`
   (LD 93-100), with `@LOOKDEV_DIRECTORY@`, `@LEAF_TEXTURE@` and `@GRASS_TEXTURE@` filled in and the
   `lookdev.grassCards` macro expanded.
2. It runs `StrataCLI launch --headless --project <copy> --idle-timeout 900` (LD 106-114). Only live shots get a window.
3. For each shot it sends `scene.open {scene, force: true}`. A world also gets `world.loadCells {region: ±20000 m, wait: true}`,
   so streaming does not depend on the camera (LD 228-234). Re-opening with `force` throws away the previous shot's
   setup changes, because nothing is ever saved.
4. It runs the shot's `Setup` steps. `entityName` is replaced by the first `entity.find {name}` hit, and `repoFile` by
   an absolute path for `asset.import` (LD 209-225).
5. For each AA mode it sends `component.set` to every `PostProcess` entity (LD 48-54, 525-530). The values per mode:
   - `taa`: `{AntiAliasing: true, AntiAliasingMethod: "TAA"}`
   - `fxaa`: `{true, "FXAA"}`
   - `off`: `{AntiAliasing: false}`
   - `morph`: `{true, "Morphological"}`

   A scene without a PostProcess entity is left at the defaults (FXAA on).
6. For each size and repeat it sends `viewport.capture`, built in `capture_still` (LD 237-255):

   ```json
   {"camera": "scene" | "editor"  (or "position", "target", "fov"),
    "width": W, "height": H, "overlays": false, "path": "<png>", "overwrite": true,
    "debugView": "<view>"?, "quality": "<preset>"?}
   ```

7. It sends `editor.quit {force: true}`. Afterwards it crops (normalized rects, enlarged 4 times by nearest neighbour)
   and computes the metrics. It checks each repeat against the first; the difference should be 0 (`selfDifference`).
   Outputs: `shots/<shot>-<W>x<H>-<aa>.png`, `crops/`, `stats/<name>.json` (each repeat's full result without the image),
   `stages.csv`, `index.html`, `run.json` (DG 698-704).

Limits: `--sizes` must be 16-4096 pixels each way (LD 542-552). `viewport.capture` has the same limit and is also
bounded by the device (VC 34-35, 1379). `--quality` takes `project|low|medium|high|ultra` (LD 455). Shot names never
change and shots are only appended (Shots `_comment`, DG 757), so **a book figure may name a look-dev shot and stay
valid**.

**Route B: a command script (what the Showcase's committed screenshots use).** Write a JSON array and run one headless
editor on a *copy* of the project:

```sh
StrataEditor --headless --no-automation --project <copy> --commands figures.json \
    --quit-after-commands --frames 36000
```

```json
[
 {"command": "scene.open", "parameters": {"scene": "Scenes/Outpost.stscene", "force": true}},
 {"command": "scene.loadStatus", "parameters": {"wait": true}},
 {"command": "entity.find", "parameters": {"name": "Post Process"}, "bind": {"pp": "/entities/0"}},
 {"command": "component.set", "parameters": {"entity": {"$ref": "pp"}, "component": "PostProcess",
   "values": {"AntiAliasing": true, "AntiAliasingMethod": "TAA"}}},
 {"command": "viewport.capture", "parameters": {"position": [19.03, 1.6, -5.91], "target": [13.02, 2.493, 0.1],
   "fov": 40.0, "width": 1920, "height": 1080, "quality": "high", "overlays": false,
   "path": "C:/out/fig-3-2.png", "overwrite": true},
  "expect": {"/pendingAssets": {"equals": 0}, "/texturesBelowWanted": {"equals": 0},
             "/localShadowViewsPending": {"equals": 0}, "/reflectionProbesPending": {"equals": 0},
             "/preExposureSettled": {"equals": true}, "/temporalFrames": {"min": 8}}}
]
```

- The `expect` block is `PICTURE_COMPLETE` from `Tools/GenerateShowcaseTerrain.py` 2163-2165. The generator's
  `pictures` script uses it for `Screenshots/Shot1-6.png` (960x540 at High, no overlays, each shot's LookDev camera)
  and `Assets/Icon.png` (256x256 of shot 2), ending with `scene.save` and `editor.wait {frames: 600}` for the thumbnail
  (2179-2197). An unmet `expect` fails the step, and the process exits 1 (DG 3209-3226).
- `bind`/`$ref` carry fresh entity IDs between steps. `until {steps|seconds}` repeats a *query* until its `expect`
  holds (DG 3213-3222).
- `--frames N` bounds the run. `--quit-after-commands` closes the editor once the script finishes. A script still
  unfinished at the last frame exits 1 (DG 3224-3226, `EditorLayer.cpp` 690-697).
- `ShowcaseRenderCommands.json` is the model of a render regression. It binds 15 entities, sets a station, and
  captures 10 views at 960x540 at High (three with `debugView`), with `expect`s on `/debugView/shadows/cascades/4/far`
  and `/debugView/lighting/surfaceEv100/p50`.

**Route C: automation (interactive or a custom driver).** Start with
`StrataCLI launch --headless --project <copy> --idle-timeout <s>`. Then call
`StrataCLI call viewport.capture @params.json --project <copy> --timeout 300000`; LD writes the params to files to
avoid quoting problems (LD 116-129). `--save-image shot.png` writes the image from the result
(`.claude/skills/strata-editor-automation/SKILL.md` 57). Finish with `editor.quit {force: true}`. This is the only
route for live captures, because the capture must be in flight while `play.step` or `input.sequence` runs (LD 258-278).

**The camera.**
- `camera: "scene"` uses the scene's primary camera. It fails without one. Its size is the Game view's when that view
  keeps an aspect or a fixed size (`viewport.setSettings {gameView: {mode: "custom", width, height}}`).
- `camera: "editor"` uses the editor camera as the project restores it, which is not reproducible on a fresh copy.
  On first open the editor frames the scene (DG 3475-3478).
- `position` + `target` (+ `fov`) uses a camera of the capture's own. `camera.get` is not changed, and the result reports
  `camera: "custom"` (DG 3672-3674). **Book figures should use `position`/`target`/`fov`, or `camera: "scene"`.**
- `camera.set {position, target, yaw, pitch, distance, fov, near, far, flySpeed}` moves the person's editor camera. Use
  it only for whole-editor pictures.

**The size.** `width` and `height` default to the viewport's size, which is 1280x720 while the viewport is hidden,
for example when headless (VC description). Give only one of them and the viewport's aspect ratio is kept.

### 1.2 The same shot with one feature off, or a debug view on

- **Feature off:** add `Setup` steps (LookDev) or script steps *before* the capture. Each step changes a component
  property, an entity's activity, a material preview, or the project's quality section. Then capture the same camera
  again and give the output a suffix. The patterns in use:
  - `showcase.shot3.noprobe`: `entity.setActive {Probe.Golden.Yard, false}`.
  - `showcase.shot6.nofire`: the `Fire` PointLight at intensity 0.
  - `tp.grain`: PostProcess `FilmGrain` and `ChromaticAberration`.
  - `tp.dof`: Camera `DepthOfField`.
  - `ow.sunward.flare`: `LensFlare` 1.
  - `lookdev.room.view.gi` vs `lookdev.sunroom.lit.gi`: `GlobalIllumination` true.

  Every switch is listed in the table of section 2.
- **Material A/B without touching files:** `material.set {material, properties, save: false}` changes only the loaded
  material, as a preview (DG 3709-3712). Use it to turn off a normal map, clear coat or transmission for one picture.
- **One quality row:** `viewport.capture {quality}` takes only presets (`project|low|medium|high|ultra`, VC 1270-1272).
  To change one knob, for example `ContactShadows` (0 in every preset) or `ReflectionProbeResolution`:
  1. On the copy, run `project.setSettings {section: "Renderer.Quality", value: {"Preset": "Custom", ...}}`. Fields left
     out of a simple section take their defaults (DG `project.setSettings` description), and Custom's defaults are High's
     values (DG 4049).
  2. Capture with `quality` left out or `"project"`.

  The feature test uses `{"Preset": "Custom", "ContactShadows": 16}` (`StrataTests/FeatureTest/FeatureTest.stproj`
  166-167), and `lookdev.polished` documents a Custom A/B of `ReflectionProbeResolution` (DG 754-756).
- **Debug view:** add `"debugView": "<name>"` to the capture (the `DebugView` field of a shot, or LookDev's
  `--debug-view`). The 15 names (VC 1262-1268; `ViewportDebugView` in `StrataEditor/src/Editor/StreamingView.h` 27-47):

  | View | What it shows |
  | --- | --- |
  | `none` | the plain image |
  | `streaming` | tints: pending Sulfur, failed Cinnabar, placeholder boxes for meshes still loading |
  | `lod` | tints per level of detail 0/1/2/3+ |
  | `mip` | tints by how many mip levels the worst texture lacks |
  | `motion` | per-pixel motion as hue and strength. Renders twice; a still scene shows none |
  | `shadows` | receivers colored by screen pixels per shadow texel, cascades outlined, plus `debugView.shadows` statistics |
  | `lighting` | lit surfaces shaded white |
  | `ao` | ambient occlusion |
  | `indirect` | indirect light alone |
  | `luminance` | EV100 bands |
  | `albedo` | base colors, with values outside 0.03-0.85 marked |
  | `voxels` | GI's voxels |
  | `gi` | GI's light on white surfaces |
  | `open` | the share of the sky surfaces see |
  | `probes` | GI's probes |

  The tint views add a legend, but only in the Scene view's UI, not in captures. The lighting views return
  `debugView.lighting {surfaceEv100, sunIlluminance, skyIlluminance, sunToSkyRatio...}`, which the book can quote under
  a figure. A view change resets the temporal history (DG "Lighting debug views"), and the capture's waits cover that.
- **Viewport settings that touch pictures** (`viewport.setSettings`, DG 3684-3690): `grid`, `selectionOutline`,
  `sceneGizmos`, `allColliders`, `stats`, `previewLighting`, `gameUI`, `gizmo`, `space`, snap steps, `debugView`,
  `quality`, `gameView`, `canvasMode` (the 2D canvas view, DG 3832-3846), and `editPose` (DG 3727-3728). They are
  validated as a whole and saved per project in `.strata`, which is one more reason to work on copies.
  `overlays: true` on a capture draws the overlays that are enabled. The placement ghost is never drawn in captures
  (DG 3553).

### 1.3 A picture of the whole editor with chosen panels

Only one mechanism exists. `--screenshot <file.png>` reads the window's back buffer, with the UI, once the last frame is
on screen. It needs a window and a GPU (`EditorApplication.cpp` 195-204; `GraphicsModule::RequestBackBufferCapture`;
`EditorLayer.cpp` 566-589, 699-700). Headless and `--no-gpu` runs get an empty image, and the run fails with "Screenshot
failed: Image is empty" (CTest `StrataEditor.ScreenshotWithoutGPU`, `StrataTests/CMakeLists.txt` 483-488).

```sh
# Windows: the editor is a GUI-subsystem program; from PowerShell use Start-Process -Wait (AGENTS.md "Windows subsystem")
StrataEditor --windowed --ui-scale 1 --layout <figure-layout.ini> --no-automation \
    --project <copy> --commands editor-figure.json --quit-after-commands --frames 36000 \
    --screenshot <out>/editor-inspector.png
```

- `--windowed` opens a 1600x900 window instead of a maximized one (`EditorApplication.cpp` 72, 347-349). This is the
  only control over the size. Maximized windows depend on the display.
- `--ui-scale 1` fixes the UI scale (the range is `ImGuiLayer::c_MinScale..c_MaxScale`).
- `--layout <file.ini>` keeps the panel arrangement in that file instead of `<user data>/Strata/EditorLayout.ini`
  (DG 3240-3242). Commit one `.ini` per arrangement the book shows. Runs with `--frames` do not save the layout
  (DG 3231).
- Inside the script:
  - `scene.open`.
  - `selection.set {entities: [...], asset?}` selects, so the Inspector shows the entity or the Asset tab shows the asset.
  - `editor.showPanel {panel}` focuses a panel. The panels are Streaming, Performance, Problems, Activity,
    ProjectSettings, Console, ContentBrowser, Hierarchy, Inspector, AssetInspector, Viewport or Scene, and Game.
    `scripts` (ContentBrowser) and `search` (Hierarchy) refine it (`EditorLayer.cpp` 177-231). It fails headless.
  - `editor.showDialog {dialog}` opens one of export, newProject (`template`), openSample (`sample`), recovery,
    newScript, preferences (`section`), externalEditor or about (`EditorLayer.cpp` 233-328).
  - `viewport.setSettings` sets overlays, debug view, quality and the Game view size.
  - `camera.set` places the Scene view.
  - `play.start {paused: true}` and `play.step {steps}` show a running game.
  - End with `editor.wait {frames: N}` so thumbnails, fonts and panels settle before the last frame is shot.
- When `--quit-after-commands` ends the run, the screenshot shows the frame the script ended on (CTest
  `StrataEditor.QuitScreenshot`, `StrataTests/CMakeLists.txt` 437-446).
- **The launcher:** a windowed editor without `--project` shows the launcher (CTest `StrataEditor.LauncherSmoke`).
  Point `STRATA_RECENT_PROJECTS` at a controlled file. The footer shows the version, commit, GPU and startup time, which
  will not reproduce.

### 1.4 A picture of a running game

Three routes, from most to least reproducible:

1. **Rendered still of the paused game.** This works headless.
   - Run `play.start {paused: true}`. Fixed step 0 comes after the script build (DG 3768-3769).
   - Advance exactly: `play.step {steps: N}`, or `input.sequence {events, steps}` to play input timed in fixed steps
     (DG 3736-3790).
   - Capture with `viewport.capture {camera: "scene", width, height, ...}`. The scene camera shows the game's HUD and
     canvases; editor views hide them (DG 3487-3489).
   - `play.stop`.

   Paused and stepped frames draw the exact simulated poses (DG 3734-3735). Showcase-style scripted games can be set up
   before play: `script.build`, then `script.setField {entityName: "Outpost", class: "Outpost", field: "StartShot",
   value: 2}`.
2. **Live capture of the Game view** (motion, TAA trails, motion blur). This needs a **windowed** editor (LD 493:
   `windowed = any("Live" in shot ...)`) and automation:
   - `editor.showPanel {panel: "Game"}`.
   - `viewport.setSettings {gameView: {mode: "custom", width, height}}`.
   - `play.start {paused: true}`.
   - Start, in the background, `viewport.capture {live: true, camera: "scene", atFixedStep: S, frames: F (1-16), path,
     overwrite}`.
   - Then `input.sequence {steps: S+F+2, events}` or `play.step {steps}`. Then wait for the capture's answer, then
     `play.stop` (LD 258-278).

   Files come out as `<name>-1.png` and up. Live captures refuse the parameters of rendered ones (size, debugView,
   quality, overlays, waitForAssets...). Every run of the same steps shows the same game state, but **the jitter phase
   differs** (DG 3681-3683).
3. **The exported runtime.** Run `project.export` (headless editor), then:

   ```sh
   <project>/Build/<Game> --resolution 1280x720 --seconds 22 --quality high --screenshot out.png [--save-directory <dir>]
   ```

   Runs that end by themselves keep every fixed step and draw no interpolation, so the last frame shows the same game
   time on every machine (`RuntimeApplication.cpp` 72-90). `--screenshot` needs `--frames` or `--seconds` and a window
   (not `--headless`). It fails when the frame shows the missing-camera message or a cleared loading frame (`RuntimeApplication.cpp`
   272-310, 392-397). CTest `StrataRuntime.ShowcaseWindowed` does exactly this (`StrataTests/CMakeLists.txt` 1015-1021).

---

## 2. Every rendering feature: how to isolate it, where it shows best, what must be built

Derived from the components (`Renderer/RendererComponents.h`, `Scene/Components.h` `CameraComponent`, `Renderer/Material.h`),
the quality rows (`Renderer/RendererQuality.cpp` 39-55, 157-179; DG 4014-4038), the debug views (above) and the
renderer's sections of DG (3953-6260).

Legend for "Build?":
- **no**: an existing scene shows it, and often an existing look-dev shot names it.
- **setup**: an existing scene plus `Setup` steps.
- **yes**: no sample or look-dev scene has it, so the book's own look-dev script must make a scene.

All switches are `component.set {entity|entityName, component, values}` unless another command is named.

### 2.1 Lights and shadows

| Feature | Isolate it (switch, where) | Best scene / existing shot | Build? |
| --- | --- | --- | --- |
| Directional light (sun), physical lux | `DirectionalLight.Intensity`, `Color`; `lighting.applySkyPreset {preset, sunElevation, sunAzimuth}` | LookDev `lookdev.overview`; Showcase stations | no |
| Sun shadow cascades (stable, PCSS filter, blend, distribution) | `DirectionalLight.CastShadows`, `ShadowDistance`, `CascadeBlend`, `CascadeDistribution`, `ShadowSoftness` (angular diameter); quality rows `ShadowResolution`, `ShadowCascades`, `ShadowFilterQuality` (capture `quality: low` vs `ultra`); `debugView: "shadows"` outlines the cascades | `showcase.shot1` + `showcase.shot1.view.shadows` (cascades to 550 m at dawn); `tp.scene` crops `robot-shadow`, `sign-shadow` | no |
| Screen-space shadow mask + contact shadows | Contact shadows are 0 steps in every preset: `project.setSettings Renderer.Quality {Preset: Custom, ContactShadows: 16}`; per light `ContactShadowLength` (0 off) | `lookdev.contact` (5 cm plate), `tp.feet` | setup (Custom quality on the copy) |
| Point lights (clustered, physical candela) | `PointLight.Intensity/Range/Color`, `entity.setActive` | LookDev `Room Lamp` (`lookdev.room`); ThirdPerson lanterns (`tp.lantern`); Showcase Dusk fire and lanterns | no |
| Spot lights | `SpotLight` cones, `InnerConeAngle`/`OuterConeAngle` | **no sample or look-dev scene has one** (only `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene`) | yes |
| Local light shadows (atlas) | `PointLight/SpotLight.CastShadows`, `ShadowFilterRadius`; rows `LocalShadowAtlasSize`, `LocalShadowMaxTile`, `MaxShadowedLocalLights` | `lookdev.room`, `tp.lantern`, `showcase.shot6` | no |
| Sized sources (highlight width) | `PointLight.SourceRadius` (0 vs 0.06), sun `ShadowSoftness` | `lookdev.lantern.sheet` vs `.sized`, `lookdev.lantern.wet` vs `.sized` | no |
| Preview lighting (editor views of unlit scenes) | `viewport.setSettings {previewLighting}`; editor camera on a scene with no light | an `empty`-template scene with a cube | yes (trivial) |

### 2.2 Sky, environment, atmosphere, fog

| Feature | Isolate it | Best scene / shot | Build? |
| --- | --- | --- | --- |
| Sky: environment map (HDR) | `SkyLight.Source = EnvironmentMap`, `Rotation`, `BackgroundBlur`, `ShowBackground` | ThirdPerson (`kloofendal...puresky_1k.hdr`; `tp.scene`) | no |
| Sky: procedural | `Source = Procedural`, Zenith/Horizon/Ground colors, `SunSize/SunIntensity` | the `basic3d` template (`basic3d.scene`) | no |
| Sky: physical atmosphere | `Source = Atmosphere`, `AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`; presets Clear/Hazy/Overcast/GoldenHour; night (sun below the horizon) | `lookdev.sky`, `lookdev.overcast`, `lookdev.night`, `ow.lowsun` | no |
| Image-based lighting (irradiance + prefiltered cube) | `SkyLight.Intensity` 0 vs 1; `debugView: "indirect"`; row `EnvironmentResolution` (256 vs 512: Medium vs High) | `lookdev.view.indirect`; the Mirror scene for sharp sky reflections | no |
| Aerial perspective | `SkyLight.AerialPerspective` false/true, `AerialPerspectiveScale` | `ow.scene` (mountain crop), `showcase.shot1` | no |
| Height fog | `entity.setActive {Fog}` or `HeightFog.Density`, `HeightFalloff`, `SunScattering`, `ColorFromSky` | Showcase `Fog` (shot1 0.006), OpenWorld Height Fog | no |
| Time of day | Showcase: `GenerateShowcaseTerrain.py setup --station Dawn\|Golden\|Dusk --format lookdev\|script` prints the steps; elsewhere `lighting.applySkyPreset` or the Sun's `Transform.Rotation` (`ow.lowsun`) | Showcase's six shots; `lookdev.sunroom.sun0/sunhigh` | no |

### 2.3 Surfaces and materials

| Feature | Isolate it | Best scene / shot | Build? |
| --- | --- | --- | --- |
| PBR metal/roughness, GGX | `material.set {save: false}` `Roughness`, `Metallic`; `debugView: "lighting"`, `"albedo"` | LookDev `Specular` roughness ladder (`lookdev.ior` camera), `lookdev.mirror` (0.02/0.1/0.3) | no |
| Multiple-scattering energy compensation (white furnace) | **no switch** (`PBR.slang` `GetSpecularEnergy`); show the furnace row | `lookdev.furnace` (AA off, neutral post process) | no (A/B impossible: gap) |
| F0 from IOR | `IOR` per material | `lookdev.ior` (four IOR spheres) | no |
| Specular anti-aliasing | `SceneRendererSpecification::SpecularAntiAliasing`, **not reachable from commands** | `lookdev.sheet` | gap |
| Normal maps (X/Y, Z reconstructed) | `material.set {NormalMap: null, save: false}` or `NormalScale` 0 | Showcase scans (`showcase.macro` rock), bus sheet waves (`showcase.shot2`) | no |
| Occlusion maps + AO multi-bounce | `OcclusionStrength`; `PostProcess.AmbientOcclusionMultiBounce` | Showcase scans | no |
| Emission + bloom | `EmissiveIntensity`; `PostProcess.Bloom`, `BloomIntensity/Threshold/Radius` | ThirdPerson `LanternGlow.stmat`; Showcase embers/wicks at Dusk (`showcase.shot6.held`) | no |
| Alpha mask (cutout), double-sided | `AlphaMode`, `AlphaCutoff`, `DoubleSided` | LookDev `Leaves` (`lookdev.foliage.near/far`), `Scenes/Grass.stscene` (`lookdev.grass`) | no |
| Alpha blend (sorted transparents) | `AlphaMode: Blend` | OpenWorld `Water.stmat` (`ow.water`), PhysicsPlayground `Ghost.stmat` | no |
| Clear coat | `material.set {Clearcoat: 0, save: false}` | PhysicsPlayground `PlasticBlue.stmat` balls (`pp.scene` crop `balls`) | no |
| Glass / transmission (IOR, thickness, attenuation) | `Transmission`, `Thickness`, `AttenuationColor/Distance` | PhysicsPlayground `Glass.stmat` (the ball pit's walls) | setup (camera to the pit) |
| Unlit materials | `Unlit` | none set in samples | yes (trivial) |
| UV tiling/offset | `UVTiling`, `UVOffset` | Showcase ground (scans at real-size tiling) | no |
| Mirrored instances (negative scale) | `Transform.Scale` with one negative axis | none | yes |
| World-space text, screen-space text | `Text.ScreenSpace`; capture with `camera: "scene"` to see HUD text | Tetris (`ScreenSpace: false` in `Main.stscene`), ThirdPerson HUD | no |

### 2.4 Screen-space and global effects

| Feature | Isolate it | Best scene / shot | Build? |
| --- | --- | --- | --- |
| Ambient occlusion (GTAO + denoiser) | `PostProcess.AmbientOcclusion`, `Radius`, `Intensity`; row `AmbientOcclusionQuality`; `debugView: "ao"` | `tp.view.ao`, `tp.scene.view.ao`, `lookdev.view.ao` | no |
| Reflection probes (box projection, blending, bake) | `entity.setActive` on the probe; `BoxProjection`, `Intensity`, `Priority`; row `ReflectionProbeResolution`; `lighting.bakeProbes` (copies only: a bake trashes the old capture, DG 742-746) | `showcase.shot3` vs `.noprobe`, `lookdev.patch`, `lookdev.polished` | no |
| Screen-space reflections | `PostProcess.ScreenSpaceReflections`, `Intensity`, `MaxRoughness`; row `Reflections` (Off/Checkerboard (TAA only)/Spatial/SpatialHigh) | `lookdev.mirror`, `lookdev.wet`, `showcase.shot4` (puddles) | no |
| Global illumination (experimental radiance cascades) | `PostProcess.GlobalIllumination`, `GlobalIlluminationIntensity`; row `GlobalIllumination` (Off at Low and Medium, so capture at `high`); views `voxels`, `gi`, `open`, `probes` | `lookdev.cornell(.view.gi)`, `lookdev.sunroom*`, `lookdev.yard*`, `tp.scene.lit.gi` | no |
| Auto exposure, metering, exposure key, manual EV | `PostProcess.AutoExposure`, `Exposure`, `AutoExposureMetering`, `AutoExposureKey`, `Low/HighPercentile`; `debugView: "luminance"` | `showcase.shot6.held` (manual exposure), `basic3d.view.luminance`, `showcase.measure.*` | no |
| Bloom | `Bloom`, `BloomIntensity`, `BloomThreshold`, `BloomRadius` | Showcase Dusk (`showcase.shot6`), ThirdPerson lanterns | no |
| Lens flares | `PostProcess.LensFlare` 0 vs 1 (sun in view) | `ow.sunward` vs `ow.sunward.flare` | no |
| Tone curves | `Tonemapper` None/Reinhard/ACES/AgX/KhronosNeutral/Filmic, `Toe`, `Shoulder` | a high-range frame: `showcase.shot2` or `showcase.shot6.held` | setup |
| Grading: white balance, slope/offset/power, saturation, contrast | `WhiteBalanceTemperature/Tint`, `ColorSlope/Offset/Power`, `Saturation`, `Contrast` | any Showcase shot | setup |
| Color lookup (.cube) | `ColorLookup`, `ColorLookupIntensity` (import with `asset.import`) | `tp.lut` (imports `StrataTests/FeatureTest/Assets/Lighting/Feature/Warm.cube`) | no |
| Vignette | `Vignette` (0.12 default vs 0) | any wide shot | setup |
| Film grain, chromatic aberration | `FilmGrain`, `ChromaticAberration`; players' rows | `tp.grain` (crops `center`, `corner`, enlarged) | no |
| Depth of field | `Camera.DepthOfField`, `FocusDistance`/`FocusEntity`, `Aperture`, `SensorHeight`; scene camera only (`camera: "scene"`); players' row | `tp.dof` (the robot in focus) | no |
| Motion blur | `PostProcess.MotionBlur`, `ShutterAngle`, `MaxLength`; row `MotionBlurQuality` (Off at Low); editor views never blur | `tp.live.*.mb90/.mb180` (**live captures only**) | no, but windowed |
| Anti-aliasing: TAA (Sharp/Original/Custom), FXAA, morphological, off | `AntiAliasing`, `AntiAliasingMethod`, `TAAPreset`, the `TAA*` tunables; LookDev `--aa taa,fxaa,off,morph` | `lookdev.thin` (poles, fence), `lookdev.foliage.far`; motion: `tp.live.turn*` | no |
| Output dither (no banding) | `SceneRendererSpecification::DitherOutput`, **not reachable from commands** | `lookdev.night` (sky `Bands` metric) | gap |

### 2.5 Geometry, streaming and the pipeline

| Feature | Isolate it | Best scene / shot | Build? |
| --- | --- | --- | --- |
| Levels of detail (error-based) + fades | `debugView: "lod"` (`entitiesPerLOD`, `lodErrorPixels`); rows `LODErrorPixels`/`MinProjectedPixels` (`quality: low` vs `ultra`) | Showcase rocks (six LODs); OpenWorld (`ow.scene`) | no |
| Texture streaming / mips | `debugView: "mip"`, `"streaming"`; `asset.setBudget` (small pools) with `waitForAssets: false` to show coarse mips | OpenWorld; Showcase scans | setup |
| GPU-driven culling and batching | **same pixels by design**; `SceneRendererSpecification::GPUDriven` not exposed; figures quote `renderStats` (draws, instances, `gpuDriven`) | OpenWorld's 20,000 instances (`ow.scene`); PhysicsPlayground | diagram, not picture |
| Skinned meshes | edit mode shows the rest pose; `animation.preview {entity, state, clip, time}` poses it; or play paused + `play.step` | ThirdPerson robot (`tp.feet`), OpenWorld foxes | setup |
| World streaming (cells) | `world.loadCells {region\|cells, wait}`; Scene-view cell bounds overlay (`CellBoundsOverlay` colors; whole-editor picture); `world.edit {visibleLayers}` | OpenWorld `Worlds/Island.stscene` | no |
| Camera-relative precision far from the origin | nothing to switch: place content at 10-20 km (`WorldData::c_SupportedExtent`) | none | yes |
| Orthographic projection | `Camera.Projection = Orthographic` (capture cameras are perspective) | none | yes |
| Game UI (canvases, widgets, masks) | `camera: "scene"`; `viewport.setSettings {gameUI, canvasMode}` | ThirdPerson `MainMenu.stscene`, PhysicsPlayground tool panel, Tetris HUD | no |
| Editor overlays (grid, outline, gizmos, collider and light shapes) | `capture {overlays: true}` with `camera: "editor"` or custom; `selection.set`; `viewport.setSettings {grid, selectionOutline, sceneGizmos, allColliders}` | PhysicsPlayground (colliders), any scene | no |
| Project thumbnail / asset thumbnails | `scene.save` writes `.strata/Thumbnail.png` (480x270), then `editor.wait {frames: 600}` | Showcase `Picture.png` route | no |

---

## 3. What makes captures reproducible, and what does not

**What the capture itself guarantees** (`viewport.capture`, VC 34-81, DG 3639-3672):

- **Waits before the picture.** Every limit is counted in frames:
  - `c_MaxCaptureTextFrames` 120: glyphs.
  - `c_MaxCaptureExposureFrames` 8: pre-exposure. The first frame resets the adaptation (`ResetExposureAdaptation`), so
    **automatic exposure meters at once in captures**.
  - `c_TemporalSettleFrames` = `SceneRenderer::c_TemporalJitterPhases` = 8, up to `c_MaxCaptureTemporalFrames` 16:
    the TAA history holds 8 frames of the full view, the mean of the jitter's phases.
  - `c_MaxCaptureAssetFrames` 300: assets, with `waitForAssets` (default true).
  - `c_MaxCaptureMipFrames` 120: textures below their wanted mip.
  - `c_MaxCapturePoseFrames` 8: animators' poses.
  - `c_MaxCaptureInstanceFrames` 120: new mesh renderers.
  - `c_MaxCaptureGIFrames` = `c_GIMaxSettleFrames` (38) + 16: GI settled.
- **Everything drawn in the first frame.** Every local light's shadow views, and conversion of every loaded probe
  capture.
- **It reports instead of failing.** The result says what was still missing: `pendingAssets`, `texturesBelowWanted`,
  `localShadowViewsPending`, `reflectionProbesPending`, `preExposureSettled`, `temporalFrames`, `stalePoses`,
  `pendingTextGlyphs`, `globalIlluminationSettled`. **The book's driver must assert `PICTURE_COMPLETE`**
  (`GenerateShowcaseTerrain.py` 2163-2165), plus `globalIlluminationSettled: true` for GI figures.
- **Film grain:** capture renderers set `GrainSeed` 0, so "a picture taken again is the same". Live views and games
  draw new grain every frame (DG 5655-5658).
- **Dither:** static noise, so the same on every capture (DG 5416-5440).
- **Repeats:** LookDev checks that repeats are equal. "0 on a deterministic driver" (DG 700-701); `selfDifference` in
  `stats/`. The driver should take two repeats and fail on any difference.

**What the figure must pin down** (the manifest's job):

1. **The build:** engine commit and configuration (Release). The GPU and driver go into the provenance: `editor.status
   {sections: ["editor"]}` names them (LD 507). Different GPUs and drivers are not bit-identical.
2. **The project state:** a fresh copy without `.strata`, scenes re-opened with `force` for every figure, nothing saved
   (except deliberate bakes on a throwaway copy).
3. **The camera:** explicit `position`/`target`/`fov`, or `camera: "scene"`. Never the editor camera.
4. **The size:** keep the figure at one fixed size. Shadow maps under High's `AutoFine` jump from 4096 to 8192 at
   1440 rows (DG 4019, 4046-4051), so a 2560x1440 picture and a 1920x1080 one differ in shadow detail, not just
   resolution. Bloom radius and chromatic aberration scale with the image (DG 5643-5647). Recommendation: 1920x1080 for
   full figures, crops enlarged 4 times by nearest neighbour for detail, 3840x2160 only where detail is the point.
5. **The quality:** always pass `quality` explicitly (`"high"`, as the Showcase pictures do), or set the Custom section
   on the copy and record it. The Scene view's own quality is saved per project and may differ (DG 4080-4087).
6. **The AA mode:** set it on the PostProcess entity every time. The component default is FXAA (`RendererComponents.h`
   298); `basic3d` and most samples use TAA. Checkerboard SSR at Medium needs TAA (Showcase README "Known limits").
7. **The time of day:** set it in the figure (Showcase stations via `setup --station`, `lighting.applySkyPreset` with
   elevation and azimuth, or the Sun's rotation). OpenWorld's `DayNight` script and the Showcase director change the
   light only in play mode, so edit-mode captures show the saved scene's light.
8. **Seeds:** the generators are seeded and quantized (`GenerateShowcaseTerrain.py` `SEED = 20261101`; grass cards
   `lookdev.grassCards {count, seed, ...}`; the tool draws its leaf and grass textures itself, LD 234-275). Nothing in a
   capture draws random numbers at run time except grain, which is seeded in captures.
9. **Worlds:** load every cell (`world.loadCells` over the ±20 km region, `wait: true`) or the content depends on the
   camera and the streaming speed (LD 228-234).
10. **Play-mode stills:** pause before step 0 and use `play.step` or `input.sequence`. Never capture an unpaused game,
    because unpaused play drops steps when a frame runs late (DG 3218-3220).

**What does not reproduce (today):**

- **Pixel bits across GPUs and drivers.** Within one machine and build, repeats are exact.
- **Recompiled shaders.** The guide records a case where declaring unused frame-constant fields made GTAO's and SSR's
  repeats differ (up to 700 pixels) for reasons not found (DG 5048-5062). Repeats must stay part of the check.
- **Live captures:** the jitter phase differs between runs; the game state does not (DG 3681-3683).
- **Runtime screenshots:** game time is exact with `--seconds`. But how many frames ran, and so the TAA history,
  automatic exposure's adaptation over wall time and the streaming state at the last frame, depend on the machine.
  Use runtime pictures only to show "the shipped game" without claims about exact pixels.
- **Whole-editor screenshots:** the content changes with the machine and the moment:
  - the launcher footer (GPU, startup time, commit)
  - the Console's timestamps
  - Performance and Streaming numbers
  - the status bar
  - asset-browser thumbnails rendered in the background
  - the window size when not `--windowed`
  - the display's scale when `--ui-scale` is not given

  Treat them as illustrations and retake them per release.
- **Probe bakes:** a bake draws the probes' present captures, so few passes depend on what the project held. Only
  eight passes (`BAKE_PASSES`) converge to 0.01% (DG 6521-6530). Never bake in a figure run except on a throwaway copy
  of a probe that was saved unbaked (`lookdev.patch`).
- **GPU timings** (`renderStats.gpuMs`): valid only alone on the machine, under PerfLock (DG 757-759).
- **The `motion` debug view of a still scene** shows nothing (DG 3660-3662).

---

## 4. The book's capture manifest and its driver

### 4.1 Manifest format (one entry per figure)

One JSON file in the book's repository, for example `figures/Captures.json`. It is versioned like `Shots.json`:
append figures, never change one's camera silently.

```json
{
  "Format": "StrataBookCaptures", "Version": 1,
  "Engine": {"Commit": "822a7a46", "Configuration": "Release"},
  "Projects": {
    "Showcase":  {"Sample": "Showcase", "Scene": "Scenes/Outpost.stscene"},
    "OpenWorld": {"Sample": "OpenWorld", "Scene": "Worlds/Island.stscene", "LoadWorld": true},
    "LookDev":   {"LookDevProject": true, "Scene": "Scenes/LookDev.stscene"},
    "BookLab":   {"Script": "projects/BookLab.json", "Scene": "Scenes/Spot.stscene"},
    "Feature":   {"Directory": "StrataTests/FeatureTest", "Scene": "Scenes/Feature.stscene"}
  },
  "Defaults": {"Size": [1920, 1080], "Quality": "high", "AntiAliasing": "taa", "Repeat": 2,
               "Expect": "PictureComplete", "Overlays": false},
  "Figures": [
    {
      "Id": "rendering/reflections/probe-on-off",
      "Chapter": "17-reflections",
      "Kind": "still",
      "Project": "Showcase",
      "LookDevShot": "showcase.shot3",
      "Variants": [
        {"Suffix": "probe", "Setup": []},
        {"Suffix": "noprobe", "Setup": [{"Command": "entity.setActive",
                                         "Parameters": {"entityName": "Probe.Golden.Yard", "active": false}}]}
      ],
      "Crops": [{"Name": "streak", "Rect": [0.3, 0.15, 0.42, 0.8]}],
      "Output": "rendering/reflections/probe-{variant}.png",
      "Alt": "The oil tank's shell at golden hour, with and without the yard's reflection probe"
    },
    {
      "Id": "rendering/shadows/cascades",
      "Kind": "still", "Project": "Showcase",
      "Station": "Dawn",
      "Camera": {"Position": [-29.7, 25.811, -58.0], "Target": [40.0, 0.0, 40.0], "Fov": 50.0},
      "Setup": [{"Command": "component.set", "Parameters": {"entityName": "Sun", "component": "DirectionalLight",
                 "values": {"ShadowDistance": 600.0}}}],
      "QualitySection": null,
      "DebugView": "shadows",
      "AntiAliasing": "taa",
      "Size": [1920, 1080],
      "Expect": {"/debugView/shadows/complete": {"equals": true}},
      "Record": ["/debugView/shadows/cascades"],
      "Output": "rendering/shadows/cascades.png"
    },
    {
      "Id": "rendering/shadows/contact",
      "Kind": "still", "Project": "LookDev", "LookDevShot": "lookdev.contact",
      "QualitySection": {"Preset": "Custom", "ContactShadows": 16},
      "Variants": [{"Suffix": "off", "QualitySection": {"Preset": "Custom", "ContactShadows": 0}}, {"Suffix": "on"}],
      "Output": "rendering/shadows/contact-{variant}.png"
    },
    {
      "Id": "post/motion-blur",
      "Kind": "live", "Project": "ThirdPerson", "LookDevShot": "tp.live.slow.mb180",
      "Output": "post/motion-blur-{frame}.png"
    },
    {
      "Id": "editor/inspector-light",
      "Kind": "editor", "Project": "Showcase",
      "Window": {"Windowed": true, "UIScale": 1, "Layout": "layouts/InspectorRight.ini"},
      "Commands": [{"command": "entity.find", "parameters": {"name": "Sun"}, "bind": {"sun": "/entities/0"}},
                   {"command": "selection.set", "parameters": {"entities": [{"$ref": "sun"}]}},
                   {"command": "editor.showPanel", "parameters": {"panel": "Inspector"}}],
      "SettleFrames": 120,
      "Output": "editor/inspector-light.png"
    },
    {
      "Id": "games/showcase-runtime",
      "Kind": "runtime", "Project": "Showcase",
      "Arguments": ["--resolution", "1280x720", "--seconds", "22", "--quality", "high"],
      "Output": "games/showcase-runtime.png"
    }
  ]
}
```

Field rules:

- **`Kind`:** `still` (a rendered capture), `live`, `editor` (a whole-window screenshot) or `runtime` (an exported game).
- **`Project`:** where the project comes from.
  - `Sample` is copied without `.strata`.
  - `Template` is `project.create {template}`.
  - `Script` is a book-owned command script that builds a lab scene from the `empty` template, like `LookDevScene.json`.
    These are the "yes" rows of section 2.
  - `LookDevProject` reuses LookDev's work directory.
  - `Directory` copies another engine folder, for example the feature test.
- **`LookDevShot`:** inherits the camera, Setup, Scene, DebugView and AntiAliasing of a `Shots.json` entry. The book's
  fields then override it, and Variants add to it. This is safe because shots are append-only.
- **`Station`:** expands to `GenerateShowcaseTerrain.py setup --station <s> --format lookdev`, run by the driver.
  Never copy the steps by hand (DG 6507-6510).
- **`Camera`:** `{"Scene": true}`, `{"Editor": true}` (whole-editor figures only), or `Position`/`Target`/`Fov`.
- **`Setup`:** Shots.json's step form, including `entityName` and `repoFile`.
- **`QualitySection`:** a `Renderer.Quality` value set on the copy with `project.setSettings`. When it is present the
  capture omits `quality`.
- **`Variants`:** A/B sets that share everything else. `{variant}` in `Output` is the variant's suffix.
- **`Expect`:** the default `"PictureComplete"` is the six-pointer block above. A GI figure adds
  `/globalIlluminationSettled`. `Record` lists result pointers to keep in the figure's sidecar JSON (statistics for
  captions).
- **`Output`:** relative to the book's `figures/` folder. Beside each PNG the driver writes `<name>.json`: the engine
  commit, the editor's version line, the GPU, the capture's full result minus the image, and the sizes.

### 4.2 Driver outline (`tools/capture.py`, standard library only, run with `python -I`)

```text
capture.py check   --manifest figures/Captures.json                     # offline: schema, unique Ids/Outputs,
                                                                        # LookDevShot names exist in <engine>/Tools/LookDev/Shots.json,
                                                                        # Variants well formed, sizes 16-4096, debug views known
capture.py run     --engine G:/GameEngineAI --build <bin dir> --out <dir> [--figures <glob>] [--kinds still,live,...]
                   [--work <dir> --keep-work]
capture.py compare --before <dir> --after <dir> --output <dir>         # delegates to LookDev.py compare
capture.py publish --from <dir> --to figures/                          # copies PNGs + sidecars after review
```

`run`, in order:

1. **Preflight.**
   - Refuse an `--out` inside the engine's tracked tree (same rule as LD `is_inside_tracked_tree`).
   - Check that `<engine>` HEAD matches `Engine.Commit` (warn if not).
   - Read `StrataEditor --version`.
   - Make a private `STRATA_SESSION_DIR` and set `STRATA_EDITOR_PATH` and `STRATA_RECENT_PROJECTS` (a controlled file).
2. **Projects.** Prepare each project the selected figures use:
   - Copy the sample without `.strata`.
   - Or run the lab script with `StrataEditor --headless --no-automation --commands <script> --quit-after-commands
     --frames 36000`.
   - For `LookDevProject`, run `python -I <engine>/Tools/LookDev.py capture --build ... --projects LookDev --shots
     lookdev.overview --sizes 320x180 --aa off --repeat 1 --work <work>/lookdev --keep-work` once, then copy
     `<work>/lookdev/projects/LookDev`. Making the project is LD's job, and its placeholders and macros stay its own.
3. **Stills, one headless editor per project, through a generated command script** (route B). There are no ports, no
   automation and no quoting, and an unmet `expect` makes the exit code 1. For each figure and each variant the driver
   emits, in order:
   1. `scene.open {force: true}`, then `scene.loadStatus {wait: true}`, then `world.loadCells` for worlds.
   2. The station steps, the Setup steps and the variant's steps. `entityName` is resolved by an `entity.find` step
      with `bind`, and each use becomes `{"$ref": ...}`.
   3. `project.setSettings` for the `QualitySection`, or `{reset: true}` when the figure has none, so that one
      figure's section does not leak into the next.
   4. `component.set` of the AA mode on the PostProcess entity (found by `entity.find {component: "PostProcess"}`).
   5. `viewport.capture` once per repeat, with `path`, `overwrite: true` and `expect`.

   Figures in one script share the editor but never state, because each starts with `scene.open {force: true}` and
   nothing is saved. Run the script as `StrataEditor --headless --no-automation --project <copy> --commands
   <gen>.json --quit-after-commands --frames 36000`, with a timeout of `frames / 30` seconds as LD uses. Save its
   stdout and stderr per project. To recover the `Record` statistics without automation, read the capture results from
   the log, or run the figure through route C instead. Simpler: run stills through route C, a copy of LD's `Children`
   and `Editor` classes (`StrataCLI launch --headless`, `call` with params files, `editor.quit`), and save the result
   JSON directly. **Recommended:** route C for stills too, so every result lands in the sidecar.
   Route B stays available for CI-like retakes.
4. **Live figures** (windowed `StrataCLI launch` without `--headless`) follow LD `capture_live`: Game panel,
   `gameView` custom size, `play.start {paused: true}`, the capture started in the background, then `input.sequence`
   or `play.step`, then `play.stop`. When the figure has a `LookDevShot`, delegate instead to `LookDev.py capture
   --live-only --shots <name>`.
5. **Editor figures** run one windowed editor per figure: `StrataEditor --windowed --ui-scale <s> --layout <ini copy>
   --no-automation --project <copy> --commands <figure>.json --quit-after-commands --frames 36000 --screenshot <png>`.
   The figure's `Commands` are followed by `editor.wait {frames: SettleFrames}`. On Windows the program is started
   with `subprocess.run` and waited for, because it is a GUI program. Copy the layout file first, because the editor
   may write it.
6. **Runtime figures:** `project.export` in a headless editor (or reuse an export), then `<Build>/<Game> <Arguments>
   --screenshot <png>`. The exit code must be 0 (it is 1 when the frame shows a message or a cleared loading frame).
7. **Post-process.** Reuse LD's `read_png` and `write_png` by import (`sys.path.insert(0, <engine>/Tools)`, `import
   LookDev`; the module only runs `main` under `__main__`), or copy them with their notice.
   - Check the size.
   - Check that the repeats' difference is 0.
   - Write the crops (4 times) and the sidecar.
   - Write `index.html` for review.
   - Exit 1 if any figure failed or came back incomplete.
8. **Wrap the whole run** in `python <engine>/Tools/PerfLock.py --label book-captures --limit 90 -- python -I
   tools/capture.py run ...`.

Review flow: retake per engine release, then `capture.py compare` (LookDev's signed differences show which figures
changed), then a person looks at the changed ones, then `publish`.

---

## 5. Gaps: what cannot be isolated or shown today without new commands or scenes

**New commands or options the engine would need (each is a small change; each would serve tests too):**

1. **A screenshot of the editor window on demand.** There is no `editor.screenshot {path, panel?}`; there is only
   `--screenshot` on the last frame of a run. There is also no window-size option beyond `--windowed` (1600x900).
   Pictures of a single panel (Inspector, Content Browser) need cropping by hand from known layout rectangles.
   Proposed: `editor.screenshot {path, overwrite, panel?}` (the back buffer, optionally cropped to a panel's rectangle)
   and `--window-size WxH`.
2. **Intermediate render targets.** The textbook's pipeline chapters want the depth prepass, the normals, the velocity
   target as data (the `motion` view is an illustration), the shadow cascades and atlas themselves, the screen-space
   shadow mask, the HDR image before tone mapping, the bloom chain, the exposure histogram, the probe cubes and the
   prefiltered mips. None of them can be read out. Proposed: `viewport.capture {target: "depth" | "normals" |
   "velocity" | "shadowMask" | "cascade<n>" | "localShadowAtlas" | "hdr" | "bloom<n>" | ...}` with a fixed visualization
   per target.
3. **Switches that live only in `SceneRendererSpecification`:** `SpecularAntiAliasing`, `DitherOutput` (the banding
   figure), `GPUDriven` (CPU vs GPU path: the same pixels, but the stats figure wants both), and `TextureStreaming`.
   There is no command to flip them for a capture. Proposed: `viewport.capture {renderer: {specularAntiAliasing,
   dither, gpuDriven}}`, refused outside the capture renderer.
4. **Effects that cannot be turned off at all:** multiple-scattering energy compensation (`GetSpecularEnergy`), the
   horizon fade, and the specular lobe vs the diffuse part. A "specular only" or "diffuse only" lighting view would
   make the BRDF chapter's figures. Today there are only `lighting` (white albedo), `indirect`, `ao` and `albedo`.
5. **Views that do not exist:** wireframe, overdraw, light clusters (forward+ heat map), shadow-caster culling,
   reflection-probe influence boxes (the boxes show only as gizmos of the selection), normal, roughness and metallic
   buffers, and a split-screen A/B.
6. **Motion blur and TAA motion artifacts as stills.** They exist only as live captures, which need a windowed editor
   and a jitter phase that differs between runs. A rendered capture of a paused game has no motion: its previous frame
   is the same view. Proposed: `viewport.capture {cameraMotion: {from, to}}`, or a rendered capture that steps
   the game between its two frames.
7. **The placement ghost and drag-and-drop UI** never appear in captures (DG 3553), and drags cannot be simulated. Only
   a person can take those editor pictures.
8. **Orthographic capture cameras.** Capture cameras are perspective (`position/target/fov`). An orthographic figure
   needs a scene camera entity.
9. **Debug-view legends.** These are the colors with counts per color, drawn in the Scene view's UI (`UI::Legend`), not
   in captures. The book must draw its own legend from the result's counts, or take a whole-editor picture.

**Scenes that must be built (the book's own lab script, `projects/BookLab.json`, made through editor commands like
`LookDevScene.json`):**

- A **spot light** scene (cones, inner and outer angles, shadows). No sample has a spot light.
- **Mirrored instances** (negative scale), next to an unmirrored copy.
- **Unlit materials** and a material ladder for normal-map strength, clear coat on and off, and transmission
  thickness and attenuation, framed as a lab. PhysicsPlayground has clear coat and glass, but in action, not
  side by side.
- **Far from the origin** (10-20 km): camera-relative precision vs a naive comparison. There is no naive mode to compare
  with: the gap is in the engine, so the figure can only show that it holds.
- An **orthographic camera**.
- A **preview-lighting** scene: one cube, no light, editor camera.
- A **tone-curve chart**: a row of emissive patches stepping by one EV from -6 to +10, captured under each `Tonemapper`.
  This needs a scene of unlit or emissive cards; the samples have no exposure chart.
- **Spot and point light falloff** on a flat plane with a grid texture (inverse square and `Range`).
- For the **game-making half** of the book: a step-by-step tutorial game whose stages are saved scenes (each chapter's
  starting point). Tetris and the other samples are finished games, not stages.

**Not gaps, but cautions:**

- **GI is experimental.** It is off at Low and Medium, so its figures must capture at `high` or `ultra`.
- **Checkerboard SSR (Medium) needs TAA.** Without it the SSR figures show only the probes.
- **Look-dev shots that name entity IDs** (`4BC76BF041EAD086`, ThirdPerson's Post Process) depend on the samples
  keeping those entities. LookDev's `entityName` form is more robust, and the book's own figures should use names.
