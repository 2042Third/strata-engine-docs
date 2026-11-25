# Inventory: From light to picture (exposure, tone mapping, post effects, anti-aliasing, quality presets)

Area key: `render-image`. Surveyed at `main` 822a7a46 (2026-11-10). Paths are relative to the repository root
(`G:/GameEngineAI`); `R/` is short for `Strata/src/Strata/Renderer/`, `S/` for `Strata/shaders/`, `DG` for
`Docs/DeveloperGuide.md`, `Arch` for `Docs/Architecture.md`. Line numbers are at this commit.

What the area is, in one paragraph: the scene passes leave a linear HDR image (RGBA16F, luminance in nits times a
power-of-two "pre-exposure"). Everything from there to the 8- or 10-bit display image is this area: the TAA resolve
(blending the jittered frame with the renderer's history), depth of field and motion blur, automatic exposure (a GPU
luminance histogram, a metering window, eye-like adaptation, an "exposure key" against a sun-lit gray card), bloom (a
half-resolution mip chain), lens flares, then one full-screen tone-mapping pass (chromatic aberration, exposure, TAA
sharpening, bloom and flare composition, a cos^4 lens vignette, white balance and slope/offset/power grading, contrast, a
tone curve - Strata's own fitted "Filmic" by default - saturation, sRGB encoding, a 3D color lookup, film grain, and a
triangular dither), and finally FXAA or a morphological anti-aliasing of Strata's own design. Around it: the
`RendererQualitySettings` struct and its `Renderer.Quality` settings section (Low/Medium/High/Ultra/Custom presets, a row
per costly knob), the players' graphics options (`IGameGraphics`, `GameGraphicsService`, `GraphicsOptions.json`, the
script SDK's `Graphics`), and the decision never to render below native resolution.

---

## 1. Features

Each entry: what it is - where it lives - where documented - release (when the documents say).

### 1.1 The HDR image and the post chain

- **HDR scene color target**: RGBA16F (`SceneRenderer::c_HDRFormat`, `R/SceneRenderer.h:1682`); holds luminance x the
  frame's pre-exposure. Readable via `GetHDRTexture` (`R/SceneRenderer.h:856`). DG "Light units and exposure" (5297), the
  pre-exposure bullet. 0.3.0 had HDR; pre-exposure 0.6.0.
- **`SanitizeHDR`**: NaN to 0, negatives to 0, overflow (Inf included) to `c_MaxHDRValue` = 65000 -
  `S/Include/Common.slang:49-57`. Used by every HDR writer (forward, sky, TAA output `S/PostProcess/TAA.comp.slang:271`).
  AGENTS.md "Rendering" rule; DG "Light units and exposure".
- **`c_MaxExposedValue` = 1e8 and `ExposeSceneColor`**: clamps exposed values before the curves, NaN cleared -
  `S/PostProcess/Tonemap.frag.slang:72-89`.
- **HDR alpha convention**: alpha 1 for opaque writers, blended transparents multiply it by 1-a, so after the
  transparent pass it is transmittance (read only by TAA's reactive mask) - DG "Motion vectors and TAA" (4349), "HDR alpha
  convention" bullet.
- **Post chain order and `PostSource`**: TAA resolve -> depth of field -> motion blur -> exposure -> bloom downsamples ->
  lens flare -> bloom upsamples -> (text/overlay preparation, color lookup resolve) -> tone mapping -> FXAA or
  morphological -> overlays. `PostSource` {HDR, History, DepthOfField, MotionBlur} (`R/SceneRenderer.h:1609`) selects
  one binding set per source (`SelectPostSet`, `R/SceneRendererPost.cpp:441-456`); orchestration in
  `SceneRenderer::RenderFrame` (`R/SceneRenderer.cpp:3542-3668`). File overview comment
  `R/SceneRendererPost.cpp:22-31`. DG "Post-processing" (5389) first paragraph; Arch 316 and GPU stage table 940-946.
- **`HDROutput` frames**: end with the HDR image, no post at all (reflection-probe bake) - `SceneRenderOptions::HDROutput`
  (`R/SceneRenderer.h:425-428`), early exit `R/SceneRenderer.cpp:3558-3581`.
- **Fullscreen pass machinery**: vertex-bufferless fullscreen triangle `S/PostProcess/Fullscreen.vert.slang:5-13`;
  `SceneRenderer::DrawFullscreen` (`R/SceneRendererPost.cpp:1350-1364`); `GetFullscreenPipeline` caching per framebuffer
  info; `Copy.frag` for the overlays' copy into a target (`S/PostProcess/Copy.frag.slang`, `m_CopyBindingLayout`).
- **Post GPU data** (constant buffers, push constants, slots, static_asserted std140 offsets): `R/PostProcessData.h`
  (whole file). DG "Post-processing", "Parameters" bullet.
- **Tone mapping's volatile constant buffer** (`TonemapConstants`, 176 bytes, outgrew NVRHI's 128-byte push constants):
  `R/SceneRendererPost.cpp:110-121`; versioning argument in the comment. DG "Post-processing", "Parameters".
- **CPU twins of shader math** (for tests): `R/PostProcessMath.h/.cpp` - sRGB, `MixBits`/`PixelRandom`/
  `TriangularNoise`/`DitherToCodes`, Filmic, white balance, grading, motion-blur profile model.
- **GPU stages**: `GPU.TAA` (motion copy + resolve), `GPU.DepthOfField`, `GPU.MotionBlur`, `GPU.Post` (exposure, bloom,
  lens flare, tone map, FXAA/morphological) - Arch 940-946; `R/GPUProfiler.h:38`.
- **Statistics** (`SceneRendererStats`, `R/SceneRenderer.h:509-760`): `PreExposure`, `PreExposureSettled`,
  `ExposureLog2Luminance`, `ExposureKeyStops`, `ExposureKeyReferenceLog2`, `BloomLevels`, `Dithered`, `TemporalAntiAliasing`,
  `TemporalFrames`, `HistoryResets`, `Jitter`, `MotionBlurred`, `MotionBlurSamples`, `MotionBlurTileSize`, `DepthOfField`,
  `DepthOfFieldLens`, `DepthOfFieldInfinityCoC`, `LensFlare`, `LensFlareSun`, `ColorLookup`, `MorphologicalAntiAliasing`,
  `Quality`. Reported to agents as `renderStats.*` (`exposure.ev100/keyStops/cardEv100`, `motionBlur`, `depthOfField`,
  `lensFlare`, `colorLookup`, `quality`) in `editor.perf` and `viewport.capture`. DG sections throughout.

### 1.2 Exposure

- **Manual exposure**: `PostProcessComponent::Exposure` (EV, registered [-16, 16]); `M = 2^Exposure` written by the CPU
  into the exposure buffer - `R/SceneRendererPost.cpp:927-935`. DG "Light units and exposure".
- **Exposure buffer**: 4 floats (`c_ExposureLogLuminance`, `c_ExposureMultiplier`, `c_ExposureKeyStops`) -
  `R/PostProcessData.h:150-158`, `S/Include/Exposure.slang:1-21` (defines, histogram range).
- **Pre-exposure**: every HDR writer multiplies by a power of two P (`FrameConstants::TemporalParams.y`); histogram and
  bloom threshold divide it out; tone map applies M/P; TAA history rescaled by P/P_prev (`ResolveTemporal`,
  `R/SceneRenderer.cpp:1694`). Choice `ChoosePreExposure` (`R/SceneRenderer.cpp:1531-1598`), `GetPreExposureFor`
  (1514-1520), headroom 2 stops and range 2^+-24 (`R/SceneRenderer.h:991-996`), readback ring of `BufferReadback`s
  (`R/SceneRendererPost.cpp:148-153, 978-997`), epochs (`StartPreExposureEpoch`, 1522-1529), forced by
  `SceneRenderOptions::PreExposure` (`R/SceneRenderer.h:421-424`). DG "Light units and exposure", "Pre-exposure" bullets.
  0.6.0.
- **Luminance histogram**: 256 bins, bin 0 = black (ignored), bins 1-255 over log2 [-12, 16] -
  `S/Include/Exposure.slang:12-37`, `S/PostProcess/Histogram.comp.slang:54-71` (16x16 groups, group-shared bins,
  `InterlockedAdd`). Dispatch and barrier `R/SceneRendererPost.cpp:962-976`. DG "Light units and exposure".
- **Metering modes**: `ExposureMetering` {Average, CenterWeighted (default)} (`R/RendererComponents.h:184-190`); weight
  function `MeteringWeight` (`S/PostProcess/Histogram.comp.slang:39-50`). DG "Post-processing", "Exposure" bullet. 0.7.0.
- **Percentile metering window**: `AutoExposureLowPercentile` 0.1 / `HighPercentile` 0.9, at least 0.02 apart -
  `S/PostProcess/Exposure.comp.slang:56-78`, `R/SceneRendererPost.cpp:945-950`.
- **Adaptation (light/dark speeds)**: `AutoExposureLightSpeed` 3/s, `AutoExposureSpeed` 1.5/s, per-frame fraction
  `1 - exp(-dt*speed)`; `dt` the wall clock capped at 0.25 s (`StepSeconds`, `R/SceneRendererPost.cpp:79-87`;
  `c_MaxStepSeconds`, `R/SceneRenderer.h:1569-1573`) or `SceneRenderOptions::AdaptationSeconds`. GPU side
  `Exposure.comp.slang:80-91`. Separate light speed 0.7.0.
- **Min/Max EV clamp**: `AutoExposureMinEV` -4, `AutoExposureMaxEV` 16 (12 until 0.5.0).
- **Exposure key**: `AutoExposureKey` 0.12; `k = clamp(key*(a - log2 Lref), -2, 0)`, Lref = luminance of a 0.18 gray card
  facing the directional light (`R/SceneRenderer.cpp:3609-3616`), range constants `R/PostProcessData.h:183-188`, GPU
  `Exposure.comp.slang:92-97`. It never brightens (reasoning in the header comment). DG "Post-processing", "Exposure".
  0.7.0.
- **Exposure reset / jump**: `ResetExposureAdaptation`, `JumpExposureAdaptation` (`R/SceneRenderer.h:981-990`), called by
  `GameRenderer::Render` on scene change (`R/../Runtime/GameRenderer.cpp:103-121`) and by captures.
- **EV100 conversion and reference table** (Exposure ~ 0.5 - EV100; MinEV/MaxEV = EV100 - 3): DG "Light units and
  exposure", the camera bullet and table.
- **Light units** (lux, candela, nits) feeding exposure: DG "Light units and exposure"; `Docs/Manual/Lighting.md`
  (other area). 0.6.0.
- **Sky presets that set exposure safely** (`lighting.applySkyPreset` turns manual exposure automatic, raises MaxEV):
  DG "Light units and exposure", sky presets bullet. (Mostly the Lighting area.)
- **Luminance lighting view** (EV100 bands) for judging exposure: `SceneLightingView::Luminance`
  (`R/SceneRenderer.h:330`), `viewport.capture {debugView: "luminance"}`.

### 1.3 Tone curves

- **`TonemapOperator`** {None, Reinhard, ACES, AgX, KhronosNeutral, Filmic} (`R/RendererComponents.h:171-182`; values
  are file/script API, appended only). Shader switch `S/PostProcess/Tonemap.frag.slang:249-257`. Filmic default since
  0.7.0 (ACES before; stored scenes keep theirs).
- **Reinhard** `x/(1+x)` (Tonemap.frag 251); **ACES** Stephen Hill's RRT+ODT fit (121-130); **AgX** base transform with
  polynomial contrast (132-153); **Khronos PBR Neutral** (155-171); **None**: clipped.
- **Filmic** (Strata's): curve `S/Include/Filmic.slang:11-21`, operator with inset/outset and the shadow-vs-highlight
  channel blend `S/Include/Filmic.slang:28-40`; constants `S/Include/FilmicConstants.slang` and `R/FilmicConstants.h`
  (generated); CPU reference `PostProcessMath::MakeFilmicCurve/EvaluateFilmicCurve/ApplyFilmic`
  (`R/PostProcessMath.cpp:111-137`); `Toe`, `Shoulder` look controls. Fitter `Tools/FitFilmic.py` (header lines 1-73 state
  the form and targets T1-T9). DG "Post-processing", "Tone curves" bullet. 0.7.0.
- **Contrast** around middle gray in log space before the curve (Tonemap.frag 245-247); **Saturation** after the curve
  (259-260).
- **Middle-gray display values per curve** (Filmic 0.18 -> sRGB 118; ACES 0.106; Khronos 0.14; AgX 0.215): DG "Light
  units and exposure", exposure bullet.

### 1.4 Color

- **White balance**: `WhiteBalanceTemperature` (2000-15000 K, 6500 neutral), `WhiteBalanceTint` (-1..1) -
  `PostProcessMath::GetWhiteBalanceMatrix` (`R/PostProcessMath.cpp:163-176`: CAT02 von Kries in double), locus
  `GetWhiteLocus` (144-156) over `R/WhiteBalanceLocus.inl` (generated by `Tools/GenerateWhiteBalance.py`), cached per key
  in `SceneRenderer::GetColorGrading` (`R/SceneRendererPost.cpp:1335-1348`). DG "Post-processing", "Color". 0.7.0.
- **Slope/offset/power grading** (ASC-CDL-like, on scene-linear light around middle gray): `MakeColorGrading` /
  `ApplyColorGrading` (`R/PostProcessMath.cpp:178-210`), shader `Tonemap.frag:237-244`, `ColorFlags` skip bit
  `c_TonemapColorGrading` (`R/PostProcessData.h:76-79`). 0.7.0.
- **sRGB encoding** (IEC 61966-2-1): `S/Include/Common.slang:25-39`, CPU twin `PostProcessMath::LinearToSRGB`.
- **Color lookup (3D LUT) asset**: `ColorLookup` (`R/ColorLookup.h:24-65`, `R/ColorLookup.cpp`), cooked `STLU` format,
  `AssetType::ColorLookup`, importer `Asset/ColorLookupImporter` (`.cube` parser, `Size` setting 17/33/65/File),
  sampled in Tonemap.frag 263-270 with half-texel remap, resolved per frame `ResolveColorLookup`
  (`R/SceneRendererPost.cpp:1159-1165`), bound through the tone mapping's second set with dummies
  (`GetTonemapInputSet`, 1167-1218). DG "Post-processing", "Color lookup"; Arch 1642 (asset table);
  `Docs/Manual/Camera.md` "Color lookups". 0.7.0.

### 1.5 Display output

- **Dither** (triangular, static per pixel, exact black/white, mean-preserving): `S/Include/Dither.slang:10-51`, CPU twin
  `R/PostProcessMath.cpp:68-109`; levels by target format `GetDitherLevels` (`R/SceneRendererPost.cpp:57-75`); which pass
  dithers (`R/SceneRendererPost.cpp:1285-1294`); switch `SceneRendererSpecification::DitherOutput`
  (`R/SceneRenderer.h:249-254`). DG "Post-processing", "Output and dither". 0.7.0.
- **10-bit LDR intermediate** (`c_LDRFormat` = R10G10B10A2_UNORM, `R/SceneRenderer.h:1686`; `m_LDRTexture`) written by
  the tone map when FXAA/morphological follows, undithered.

### 1.6 Lens and film effects

- **Bloom** (Jimenez COD:AW, 13-tap downsample with Karis average on the first, 3x3 tent upsample): shader
  `S/PostProcess/Bloom.comp.slang:6-140`; chain allocation (half-res mips down to 4 px, max 8,
  `R/SceneRendererPost.cpp:323-362`), `GetBloomSpan` (999-1008), `DispatchBloom` (1010-1026), downsample/upsample drivers
  (1028-1047), composition in Tonemap.frag 194-205 (energy-conserving lerp at threshold 0, additive above).
  `Bloom`, `BloomIntensity` 0.04, `BloomThreshold` 0 (soft knee = threshold/2), `BloomRadius` 64/1080 (resolution
  independent since 0.7.0). DG "Post-processing", "Bloom". Bloom since 0.3.0.
- **Vignette** (lens cos^4 fall-off on scene-linear light, before grading): Tonemap.frag 229-236;
  `GetVignetteTangents` (`R/SceneRendererPost.cpp:1150-1157`). `Vignette` 0.12. DG "Post-processing", "Vignette". Lens
  model 0.7.0 (a ring after the curve before).
- **Chromatic aberration** (lateral, red magnified / blue shrunk about the center): Tonemap.frag 178-185; scale
  `c_ChromaticAberrationScale` (`R/PostProcessData.h:52-54`). DG "Post-processing", "Film grain and chromatic
  aberration". 0.7.0.
- **Film grain** (mid-tone weighted, near-Gaussian, per frame, after AA): `S/Include/Grain.slang:17-25`;
  `c_FilmGrainAmplitude` 0.04; added in the last display pass (tone map, FXAA's `Finish`, or morphological blend);
  `SceneRenderOptions::GrainSeed` for deterministic stills (`R/SceneRenderer.h:446-449`). 0.7.0.
- **Lens flares** (ghosts, halo, sun starburst): `S/PostProcess/LensFlare.comp.slang` (ghost scales/tints 37-45,
  `BrightPart` 72-82, `EdgeFade` 85-90, `SunVisibility` 94-110, main 112-137); CPU `EnsureLensFlareResources`,
  `RenderLensFlare` (`R/SceneRendererPost.cpp:1085-1148`); starburst drawn in Tonemap.frag 206-228; sun projection
  `R/SceneRenderer.cpp:3617-3628`. `LensFlare` 0..1. DG "Post-processing", "Lens flares". 0.7.0.

### 1.7 Motion blur and depth of field (post effects that need geometry data)

- **Motion vectors / velocity target** (RG16F; unjittered current minus previous UV; motion history copy
  `S/Scene/MotionCopy.comp.slang`; `GetCameraMotion` `S/Include/Motion.slang:6-15`): DG "Motion vectors and TAA". Mostly
  the render-scene area; this area consumes them. 0.6.0.
- **Motion debug view** `ShowMotionVectors` (`S/Overlay/MotionView.frag.slang`, `R/SceneRenderer.h:483-487`).
- **Motion blur** (tile max / neighbor max reconstruction, depth-aware gather, designed here): shaders
  `S/PostProcess/MotionBlurTiles.comp.slang`, `MotionBlurNeighbors.comp.slang`, `MotionBlur.comp.slang` (weights 25-54,
  gather 56-116), shared `S/Include/MotionBlur.slang` (`GetBlurVelocity` 25-39, packing 53-71,
  `GetUniformTolerance` 73-78); CPU `EnsureMotionBlurResources`/`RenderMotionBlur` (`R/SceneRendererPost.cpp:538-695`);
  CPU model `PostProcessMath::GetMotionBlurProfile` (`R/PostProcessMath.cpp:212-285`). Component fields `MotionBlur`
  (off), `MotionBlurShutterAngle` 180, `MotionBlurMaxLength` 0.02. Conditions `R/SceneRenderer.cpp:2989, 3598-3607`. DG
  "Post-processing", "Motion blur"; Manual Camera.md "Motion blur". 0.7.0.
- **Depth of field** (thin-lens CoC, half-res prepare, near-field tiles + dilate, 48-tap Vogel gather of two fields,
  full-res composite with a jitter-stable fade): shaders `S/PostProcess/DepthOfField{Prepare,Tiles,Dilate,Gather,
  Composite}.comp.slang`, `S/Include/DepthOfField.slang`; lens `CameraLens` (`R/SceneRenderer.h:85-102`), `FromEntity`
  and CoC math (`R/SceneRendererPost.cpp:254-299`), `RenderDepthOfField` (815-860); camera fields on `CameraComponent`
  (`Strata/src/Strata/Scene/Components.h:143-149`: `DepthOfField`, `FocusDistance`, `FocusEntity`, `Aperture`,
  `SensorHeight`). DG "Post-processing", "Depth of field"; Manual Camera.md "Depth of field". 0.7.0. (Likely shared with
  the Camera/Scene area; it sits in this chain.)
- **Blur mask in alpha** (no sharpening where DoF/MB blurred): `c_TonemapBlurMask`, Tonemap.frag 187-191,
  `MotionBlurParameters::SourceMask`.

### 1.8 Anti-aliasing

- **`PostProcessComponent::AntiAliasing` + `AntiAliasingMethod`** {FXAA (default), TAA, Morphological}
  (`R/RendererComponents.h:192-202`).
- **FXAA** (after FXAA 3.11 quality, on display-encoded luma, 12-step edge search, `c_Subpixel` 0.25): `S/PostProcess/
  FXAA.frag.slang:7-169`. DG "Post-processing", "FXAA's subpixel blend". Since 0.3.0; subpixel 0.75 -> 0.25 in 0.7.0.
- **Morphological AA** (3 passes: edges with local contrast and depth jumps, weights from a run search + area table,
  linear-light blend): `S/PostProcess/MorphologicalEdges.frag.slang`, `MorphologicalWeights.frag.slang` (17-78),
  `MorphologicalBlend.frag.slang`; area table `R/MorphologicalAreaTable.inl` (generated by `Tools/GenerateAreaTable.py`,
  132x132 RG8); resources `EnsureMorphologicalResources` (`R/SceneRendererPost.cpp:862-919`), passes 1303-1320. Not the
  published SMAA (shares no table). DG "Post-processing", "Morphological anti-aliasing"; Manual AntiAliasing.md. 0.7.0.
- **Temporal AA (TAA)**:
  - Jitter: 8 phases of Halton(2,3) `GetTemporalJitter` (`R/SceneRenderer.cpp:2800-2816`), applied only to the frame's
    projection copy (`R/SceneRenderer.cpp:3092-3104`), `JitterParams`; `c_TemporalJitterPhases` (`R/SceneRenderer.h:1000-1003`).
  - History lifetime/reset rules (`R/SceneRenderer.cpp:3006-3043`), `ResetHistory` (`R/SceneRenderer.h:997-999`),
    `SceneRendererSpecification::TemporalAntiAliasing` (`R/SceneRenderer.h:240-248`).
  - Resources: ping-pong RGBA16F history and per-texture post sets (`EnsureTemporalResources`, `R/SceneRenderer.cpp:1600-1683`).
  - Resolve: `ResolveTemporal` (1685-1714) and `S/PostProcess/TAA.comp.slang` (whole file): nearest-depth 3x3 motion,
    Catmull-Rom 9-tap history fetch (162-190), YCoCg min/max clamp or variance clip (83-123), luminance-weighted blend
    (266-268), motion weight, resampling term (249-256), reactive mask for transparents (144-155, 257-265), disocclusion
    rejection via history alpha view distance (125-142), output alpha = signed view distance (271).
  - Golden-ratio noise turn for other effects' noise (`TemporalParams.z`, `R/SceneRenderer.cpp:3114-3117`).
  - Settings: `TemporalAntiAliasingSettings`, `TemporalHistoryClamp`, `TemporalAntiAliasingPreset` {Sharp (default),
    Original, Custom}, tables `c_TAAOriginalSettings`, `c_TAASharpSettings`, ranges (`R/RendererComponents.h:204-256`);
    `GetTemporalAntiAliasingSettings`, `GetTemporalAntiAliasingCustomStart`, `SetTemporalAntiAliasingSettings`
    (`R/RendererComponents.cpp:654-734`); ten `TAA*` tunables on the component (302-312 of the header).
  - Sharpening of the displayed image only (`Sharpen`, Tonemap.frag 91-119; exponent from CPU prototype
    `StrataTests/src/Renderer/TAATestUtils.h` / `TAASharpeningTests.cpp`).
  - Settling of single images (`c_TemporalSettleFrames` 8, capture/thumbnail rules): DG "Motion vectors and TAA".
  - DG "Motion vectors and TAA" (4349-4487); Manual `Docs/Manual/AntiAliasing.md`. TAA 0.6.0 (with presets per 0.6.0
    notes); used by the Basic 3D template and 3D samples.
- **Overlays keep unjittered matrices** (`R/SceneRenderer.cpp:3682-3695`).

### 1.9 Quality settings and players' options

- **`RendererQualitySettings`** (`R/RendererQuality.h:119-184`) and enums `RendererQualityPreset` (23-30),
  `ShadowMapResolution`, `MotionBlurSamples`, `AntiAliasingChoice`, `SceneEffectChoice`, `AmbientOcclusionLevel`,
  `ReflectionsQuality`, `GlobalIlluminationLevel` (33-117). Medium = 0.6.0's costs (spec default); High = section default.
  DG "Quality settings" (4009-4152); Manual `Docs/Manual/Graphics.md`. 0.7.0 (rows added in wave 8: reflections modes,
  probe resolution, GI; `c_SectionVersion` 6).
- **Preset table** (`PresetRow<T>` one line per knob, `R/RendererQuality.cpp:32-55`), `GetPreset` (443), `Clamp` (480),
  `ResolveShadowMapSize` (Auto/AutoFine by 1440 rows).
- **`Renderer.Quality` settings section**: `MakeSection` (`R/RendererQuality.cpp:707-806`), `FromSectionValue` (808-),
  `ToSectionValue`, `GetProjectQuality`; field titles/descriptions written for players and agents.
- **Row traits** (`FollowsPreset`, `GPUStage`, `MemoryBytes`) `c_RowTraits` (`R/RendererQuality.cpp:156-179`) and memory
  estimators (57-154); `OptionModel`, `FindRow`, `Normalize`, `MakeCustomStart` (`R/RendererQuality.h:247-291`).
- **Players' rows** (comfort, not cost; never turn on what the scene lacks): `AntiAliasing`, `MotionBlur`,
  `DepthOfField`, `FilmGrain`, `ChromaticAberration`; applied by `SceneRenderer::ApplyQualityOverrides`
  (`R/SceneRendererPost.cpp:458-486`) to the per-frame copy of the Post Process (`R/SceneRenderer.cpp:2962-2963`); DoF
  row read in `RenderFrame` (3588).
- **`SceneRenderer::SetQuality`** live changes (`R/SceneRenderer.h:1006-1016`) - what is re-made, history restart.
- **Who follows what quality** (game: `IGameGraphics`; editor Game view, Scene view chip `viewport.setSettings {quality}`,
  captures `viewport.capture {quality}`, thumbnails/bake `ForThumbnails()`/`ForBake()`, `GameRenderer::SetQualityOverride`,
  `--quality`): DG "Quality settings", "Who follows what".
- **Players' graphics options service**: `IGameGraphics` (`Strata/src/Strata/Core/EngineServices.h:152-184`),
  `GameGraphicsService` and `GraphicsOptionsFile` (`Strata/src/Strata/Runtime/GameGraphicsService.h:22-96`, `.cpp`),
  owned by `GameRuntime` and `EditorContext`; `GraphicsOptions.json` envelope. DG "Quality settings", "Players' options",
  "The players' file". 0.7.0.
- **Script SDK**: `StrataScriptCore/Include/StrataScript/Graphics.h` (`Graphics::Options/Get/Set/SetPreset/Reset/Save`,
  `QualityPreset`); host functions `GraphicsGetOptionCount` ... `GraphicsSaveOptions`
  (`StrataScriptCore/Include/StrataScript/ScriptABI.h:730-737`, seven appended in 0.7.0); implementation in
  `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`. Example in Manual Graphics.md "Players' options".
- **Editor**: Project Settings > Graphics Quality page (`StrataEditor/src/UI/GraphicsQualityPage.cpp/.h`), Scene view
  quality chip (`StrataEditor/src/Editor/EditorViewport.h`), commands `project.setSettings`, `viewport.setSettings
  {quality}`, `viewport.capture {quality, live, debugView}`, `graphics.resetPlayerOptions`
  (`StrataEditor/src/Editor/EditorGraphicsCommands.cpp`).
- **Runtime**: `StrataRuntime --quality <low|medium|high|ultra>`; "Graphics quality: <preset> (<source>)" log
  (`Strata/src/Strata/Runtime/GameRenderer.cpp:51-93`).
- **No render scale** (policy): Manual `Docs/Manual/Graphics.md` "Why there is no render scale" (120-124); DG "Quality
  settings" first paragraph (4013); `Docs/Roadmap.md:1636-1643` (owner's direction 2026-10-26: native resolution only,
  no dynamic resolution, no temporal upscaling, nothing may need temporal accumulation to look right); 0.6.0 release
  notes 487 had planned render scaling - later ruled out; render scale *above* 1 for live views and supersampled stills
  remain ideas (`Docs/Roadmap.md:1653-1672`).

### 1.10 The component and its editor surface

- **`PostProcessComponent`** (`R/RendererComponents.h:258-360`): every field above plus AO, GI and SSR switches (other
  areas). Registered as "PostProcess" / "Post Process" with sections Tone and color, Exposure, Bloom, Ambient occlusion,
  Global illumination, Anti-aliasing, Reflections, Lens, Motion (`R/RendererComponents.cpp:447-615`); inactive reasons
  for dependent properties (616-639: e.g. TAA tunables greyed unless Custom). First active entity with it wins
  (`SceneRenderer::GetPostProcessSettings`, `R/SceneRenderer.cpp:1447-1455`).
- **Test helpers**: `Tests::AddNeutralPostProcess`, `AddTemporalPostProcess`, `ExactSpecification`
  (`StrataTests/src/Renderer/SceneRendererTestUtils.h:237-277`).

### 1.11 Generators (committed outputs, never hand-edited)

- `Tools/FitFilmic.py` -> `S/Include/FilmicConstants.slang`, `R/FilmicConstants.h` (`--check`, `--from-committed`,
  `--rewrite`).
- `Tools/GenerateWhiteBalance.py` -> `R/WhiteBalanceLocus.inl` (91 entries, 60-510 mireds).
- `Tools/GenerateAreaTable.py` -> `R/MorphologicalAreaTable.inl`.
- `Tools/GenerateBlueNoise.py` -> `R/BlueNoise.h` (void-and-cluster 64x64): used by the *sun shadow filter*
  (`S/Include/BlueNoise.slang`), not by post-processing; listed in the brief, belongs to the shadows area. It is the
  contrast case the book can use when teaching dither noise (static white-noise hash for the dither vs. blue noise for
  shadow taps).
- `Tools/LookDev.py` + `Tools/LookDev/Shots.json`: the look-dev harness that captures the sample shots (the screenshot
  source, `--aa taa,fxaa,off`, `--debug-view luminance`, `--live`).

### How completeness was checked

- Every file of `R/` was listed; those of this area are accounted for: `SceneRendererPost.cpp`, `PostProcessData.h`,
  `PostProcessMath.h/.cpp`, `FilmicConstants.h`, `WhiteBalanceLocus.inl`, `MorphologicalAreaTable.inl`, `ColorLookup.h/.cpp`,
  `RendererQuality.h/.cpp`, and the parts of `SceneRenderer.h/.cpp` (pre-exposure, TAA, jitter, post orchestration,
  options, stats) and `RendererComponents.h/.cpp` (PostProcess, TAA settings). `BlueNoise.h` noted as shadows'.
- Every shader entry in `S/PostProcess/` (20 files) is listed above, and the includes they use (`Exposure`, `Filmic`,
  `FilmicConstants`, `Dither`, `Grain`, `MotionBlur`, `Motion`, `DepthOfField`, `Common`), plus `Scene/MotionCopy.comp`
  and `Overlay/MotionView.frag`; cross-checked with `strata_add_shaders` in `Strata/CMakeLists.txt:102, 136-155, 164`.
- Every field of `PostProcessComponent` and every registered property (RendererComponents.cpp 447-615) is covered
  except AO, GI and SSR fields (other areas).
- Every field of `RendererQualitySettings` and every `c_RowTraits` line is covered (the non-post knobs - shadows, LOD,
  AO, reflections, probes, GI - only as rows of the table; their algorithms belong to their areas).
- Every `PostProcessMath` function and every `TEST_SUITE` whose name matches the area (listed in section 6/9 sources) was
  found by grep.
- Script host functions: the seven `Graphics*` entries of `ScriptABI.h:730-737`. Settings section: `Renderer.Quality`.
  Asset type: `ColorLookup`. Editor command specific to the area: `graphics.resetPlayerOptions` (others shared).
- DG headings 3853-5754 scanned; sections read in full: "Quality settings", "Motion vectors and TAA", "Light units and
  exposure", "Post-processing". Manual pages read in full: Camera.md, AntiAliasing.md, Graphics.md.

---

## 2. Concepts to teach (dependency order)

1. **A frame is an array of numbers, and "light" is not "color".** Problem: the renderer computes physical light
   (radiance in nits); a display shows codes 0-255 in a non-linear encoding. Approaches: render straight to LDR (old
   forward renderers, clamping); render to an HDR float buffer and map later (all modern engines). Strata: RGBA16F HDR,
   then a post chain. Newcomer error: thinking a value of 1.0 means "white" in the HDR buffer, or that doubling a pixel
   value doubles perceived brightness.
2. **Floating-point formats and their limits.** Half floats: max 65504, subnormals below 2^-14, NaN/Inf propagation.
   Approaches: R11G11B10F, RGBA16F, RGBA32F; scaling ("pre-exposure", Frostbite/UE). Strata: RGBA16F + `SanitizeHDR` +
   power-of-two pre-exposure (exact scaling). Error: one NaN from a broken material spreading through bloom and TAA to
   the whole screen (why Bloom.comp zeroes non-finite values, why `SanitizeHDR` is a rule).
3. **Photometric units and the camera exposure model.** Lux, candela, nits; EV100; middle gray 0.18; reflected-light
   meter K=12.5; "sunny 16". Approaches: arbitrary units with exposure 1 (many hobby engines), physical units with
   camera exposure (Frostbite, UE, Filament). Strata: physical units, nothing rescaled; Exposure ~ 0.5 - EV100. Error:
   lighting a scene with "intensity 1 sun" then fighting exposure; expecting EV in the engine to equal EV100 (off by 3).
4. **Pre-exposure.** Why: a 100,000 lux scene does not fit half floats unexposed. Approaches: previous frame's exposure
   (Frostbite), fixed scale. Strata: power of two chosen from GPU readback of earlier frames' metering, 2 stops headroom,
   changed only when off by more than a stop, epochs; history rescaled exactly. Error: using a non-power-of-two (inexact,
   would change images) or reading the exposure back synchronously (GPU stall).
5. **Automatic exposure: metering.** Histogram in log2 luminance; average vs. center-weighted vs. spot; percentile
   windows; ignoring black. Approaches: mip-chain average of log luminance (older), histogram (UE, Frostbite). Strata:
   GPU histogram with group-shared bins, weighted, bin 0 excluded, percentile-clipped weighted mean. Error: metering the
   black background of a small object (overexposure), letting the sun disk move exposure.
6. **Automatic exposure: adaptation and intent.** Exponential smoothing frame-rate independent (`1 - exp(-dt k)`),
   asymmetric light/dark speeds (eye physiology), clamping, and the problem that "meter everything to gray" makes rooms
   look like noon. Approaches: exposure compensation curves by luminance (UE "Exposure Compensation Curve"), manual EV
   ranges. Strata: the exposure key vs. a sun-lit gray card, darkening only (reasons). Error: lerping by a constant per
   frame (frame-rate dependent), a pause becoming one huge step (why `c_MaxStepSeconds`).
7. **Tone mapping.** Mapping [0, inf) to [0,1]; the S-curve of film (toe, linear part, shoulder); per-channel vs.
   luminance curves and the hue-skew problem ("notorious six"); gamut compression (AgX inset/outset). Approaches:
   Reinhard, Hable/Uncharted 2, ACES RRT/ODT and Hill's fit, AgX, Khronos PBR Neutral, GT tonemapper. Strata: keeps five
   and adds Filmic, fitted by an offline optimizer against stated targets, with a luminance-scaled toe and per-channel
   shoulder blended by stops. Errors: tone mapping in sRGB-encoded space; expecting middle gray to stay middle gray under
   ACES (it darkens ~0.8 EV); applying saturation before the curve.
8. **Display encoding and quantization.** sRGB transfer, why 8 bits band in dark gradients, dithering (rectangular vs.
   triangular PDF, noise modulation, temporal vs. static), 10-bit intermediates. Strata: TPDF static hash, applied once in
   the last pass, exact black and white. Error: dithering twice (tone map + FXAA), dithering in linear space, letting
   FXAA see dither noise as edges.
9. **Color grading and white balance.** Chromaticity (CIE xy, 1960 uv), Planckian and daylight locus, mireds, chromatic
   adaptation (von Kries, CAT02), ASC CDL (slope/offset/power), 3D LUTs and their domain/half-texel addressing, grading
   in scene-linear vs. display space. Strata: white balance + CDL on scene-linear before the curve; LUT after the curve on
   encoded values (what grading tools assume). Error: multiplying RGB by a color to white-balance (not an adaptation);
   sampling a LUT without the half-texel remap.
10. **Convolution, mip chains and bloom.** Point spread of a lens, separable vs. pyramid blurs, downsample filters (box,
    13-tap COD:AW), firefly suppression (Karis average), threshold vs. energy-conserving mix, resolution independence.
    Strata: half-res chain to 4 px, radius as image fraction, fractional deepest level. Error: thresholded bloom that
    darkens everything else when lerped; bloom halo that shrinks at 4K.
11. **Lens models for vignette, chromatic aberration, flares.** cos^4 law, lateral CA as radial scale per channel,
    ghosts as mirrored images through the optical center, starbursts from aperture blades. Strata: physically motivated,
    restrained defaults, all off or low. Error: vignette after tone mapping (darkens differently), flares from the whole
    image (should be from the bright part only).
12. **Sampling and aliasing.** Pixels as point samples, Nyquist, geometric vs. shading vs. temporal aliasing,
    supersampling (SSAA), MSAA (Strata has none), post-process AA. Error: thinking AA is "blur".
13. **Spatial post AA.** FXAA (luma edge detection, edge walking, subpixel blend), MLAA/SMAA (pattern classification,
    area tables), depth-aware edges. Strata: FXAA at a reduced subpixel factor for texture detail; its own morphological
    AA with an exactly integrated area table and "U shapes blend nothing". Error: running FXAA on HDR/linear values (it
    expects encoded luma).
14. **Motion vectors and reprojection.** Per-pixel screen motion from current and previous matrices, camera motion for the
    sky, the need for previous transforms (motion history), unjittered vs. jittered. (Taught in the render-scene area;
    recalled here.) Error: computing motion with jittered matrices (jitter appears as motion).
15. **Temporal anti-aliasing.** Sub-pixel jitter (Halton), accumulation as exponential moving average, history
    reprojection with a sharp filter (Catmull-Rom), neighborhood clamping/clipping in YCoCg (Karis/Salvi), luminance
    weighting against flicker, disocclusion detection, reactive masks for transparents, motion-adaptive weights,
    resampling blur and sharpening, history invalidation (cuts, resizes). Approaches: UE TAA/TSR, Frostbite, DLAA/FSR
    (upscalers - out of policy). Strata: jitter only in the frame's camera copy, renderer-owned history, presets Sharp/
    Original/Custom, sharpening only on display. Errors: jittering the shared camera (shadow caches redraw), sharpening
    the history (feedback ringing), resetting on slow frames (counted in frames, not time).
16. **Motion blur.** Shutter angle, sample-and-hold display blur, McGuire's tile-max/neighbor-max reconstruction,
    depth-aware scatter-as-gather, static stratification vs. temporal noise. Strata: designed variant; drop blur under
    a pixel at 1080 rows. Error: blurring when the camera cuts; blurring the UI.
17. **Depth of field.** Thin lens, circle of confusion formula, near/far fields, scatter-as-gather on a Vogel disk,
    premultiplied near field, tile dilation, interaction with TAA jitter. Error: blurring sharp foreground into the
    background ("haloing"), DoF flicker at in-focus silhouettes under TAA.
18. **Quality presets as a product concept.** Separating look (scene) from cost (machine); rows, presets, Custom,
    player overrides layered over the project; memory estimates; why "never below native" is a policy with trade-offs
    (no dynamic resolution means fixed GPU cost; MSAA/supersampling are the alternatives). Error: putting look controls
    into a quality row (scenes would change look per machine), letting players turn on effects the scene never authored.

---

## 3. Code worth showing (excerpts)

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `R/SceneRendererPost.cpp:22-31` | The post chain in words, from the HDR image to the display; why post passes take no `FrameConstants` fields | What a render target is |
| 2 | `R/SceneRenderer.cpp:3582-3629` | The orchestration: post source switching HDR -> History -> DepthOfField -> MotionBlur, the gray-card key reference, the sun's UV | Ch. 1; GPU stages |
| 3 | `S/Include/Common.slang:49-57` | `SanitizeHDR`: why NaN/Inf must never reach an HDR target | Half floats |
| 4 | `R/SceneRenderer.cpp:1514-1520` and `1531-1598` | Pre-exposure as a power of two, chosen from asynchronous readbacks with hysteresis and epochs | Exposure, GPU-CPU latency |
| 5 | `S/Include/Exposure.slang:23-37` | Log-luminance histogram binning, NaN to bin 0 by a negated comparison | log2, histograms |
| 6 | `S/PostProcess/Histogram.comp.slang:39-71` | Compute shader with group-shared memory and atomics; center-weighted metering weight | Compute shaders, workgroups |
| 7 | `S/PostProcess/Exposure.comp.slang:40-98` | Percentile-window weighted mean, asymmetric adaptation, the key, the multiplier formula | #5, #6 |
| 8 | `R/SceneRendererPost.cpp:921-976` | CPU side of exposure: frame-rate-independent adaptation, parameter clamping, explicit barrier between two dispatches through one binding set (NVRHI pitfall) | #7 |
| 9 | `S/Include/Filmic.slang:11-40` | The Filmic curve and operator: toe in log-log, shoulder power, inset/outset, the shadow/highlight blend | Tone mapping concept, matrices |
| 10 | `R/PostProcessMath.cpp:111-137` | CPU twin of the curve; how `Toe`/`Shoulder` become Ct, Tw, q (slope matching at middle gray) | #9 |
| 11 | `S/PostProcess/Tonemap.frag.slang:121-171` | Four classic operators side by side (Reinhard, Hill's ACES, AgX, Khronos Neutral) | #9 |
| 12 | `S/PostProcess/Tonemap.frag.slang:173-275` | The whole display pass in order: CA, expose, sharpen, bloom, flare, vignette, grading, contrast, curve, saturation, encode, LUT, grain, dither | Everything before |
| 13 | `R/PostProcessMath.cpp:163-201` | White balance by CAT02 von Kries in double; grading matrix composition; the "Active" flag that makes defaults bit-identical | Chromaticity, matrices |
| 14 | `S/Include/Dither.slang:10-51` | Integer hash noise and the TPDF dither with exact ends | sRGB codes, probability basics |
| 15 | `S/Include/Grain.slang:17-25` | Zero-mean near-Gaussian grain by summing uniforms, mid-tone weighting | #14 |
| 16 | `S/PostProcess/Bloom.comp.slang:38-100` | 13-tap downsample as five weighted boxes, Karis weights, tent upsample, soft-knee threshold | Texture sampling, mips |
| 17 | `R/SceneRendererPost.cpp:999-1047` | Bloom span from a radius fraction, fractional deepest level, the loop structure | #16 |
| 18 | `R/SceneRendererPost.cpp:1220-1333` | Decision logic: which pass tone-maps into which target, who dithers, who adds grain, FXAA vs. morphological fallback, the constant buffer write | #12 |
| 19 | `S/PostProcess/FXAA.frag.slang:51-169` | FXAA: local contrast test, edge orientation from second derivatives, edge walk, subpixel blend | Luma, edges |
| 20 | `S/PostProcess/MorphologicalWeights.frag.slang:17-78` | Run search, crossing classification and area-table lookup | Morphological AA concept |
| 21 | `R/SceneRenderer.cpp:2800-2816` | Halton (2,3) radical inverse: a low-discrepancy jitter in 15 lines | Number bases |
| 22 | `R/SceneRenderer.cpp:3006-3043` and `3092-3117` | History continuation rules; jitter only in the frame's projection copy; golden-ratio noise turn | TAA concept, camera matrices |
| 23 | `S/PostProcess/TAA.comp.slang:162-190` | Catmull-Rom in 9 bilinear taps (weight merging trick) | Bilinear filtering, cubic splines |
| 24 | `S/PostProcess/TAA.comp.slang:192-272` | The resolve: nearest-depth motion, inside test, clamp, weights, luminance-weighted blend, alpha = view distance | #21-23 |
| 25 | `S/PostProcess/TAA.comp.slang:83-142` | Variance clipping toward the mean in compressed YCoCg; one-sided disocclusion test with `GatherAlpha` | #24, statistics (mean, std dev) |
| 26 | `S/PostProcess/Tonemap.frag.slang:91-119` | Bounded, contrast-adaptive luminance-only sharpening | #24 |
| 27 | `R/RendererComponents.h:220-256` and `R/RendererComponents.cpp:680-718` | Presets as tables, normalization so equal looks compare equal, Custom's start | C++ designated initializers |
| 28 | `S/Include/MotionBlur.slang:25-39` and `S/PostProcess/MotionBlur.comp.slang:25-54` | Blur velocity with shutter, clamp and sub-pixel drop; depth-aware sample weights | Motion vectors |
| 29 | `R/SceneRendererPost.cpp:254-299` | Thin-lens focal length from field of view; circle of confusion | Optics basics |
| 30 | `R/RendererQuality.cpp:32-55` and `156-179`; `R/SceneRendererPost.cpp:458-486` | Quality as data: a row per knob, traits; players' overrides applied to a per-frame copy | C++ `std::array`, structs |

Small pieces suitable as inline snippets: `GetDitherLevels` (`R/SceneRendererPost.cpp:60-75`), `GetVignetteTangents`
(1150-1157), `StepSeconds` (79-87), `TonemapConstants` with its static_asserts (`R/PostProcessData.h:19-51`), the
`GameGraphicsService` script example (Manual Graphics.md 99-109), `AddNeutralPostProcess`
(`StrataTests/src/Renderer/SceneRendererTestUtils.h:248-267`).

---

## 4. Figures

### Diagrams

1. **The post chain data flow** (one frame): HDR target (+ alpha transmittance), velocity, depth -> TAA (history A/B
   ping-pong) -> DoF (half-res, tiles, gather, composite) -> Motion blur (tiles, neighbors, gather) -> post source ->
   histogram -> exposure buffer (-> readback ring -> next frames' pre-exposure) -> bloom chain down -> lens flare -> bloom
   up -> tone map (+ LUT, flare via set 1) -> LDR 10-bit -> FXAA | morphological (3 passes) -> output -> overlays/copy.
   Mark GPU stages.
2. **Inside the tone-mapping pass**: the ordered stages of `Tonemap.frag` with the domain of each (scene-linear exposed,
   display-linear, encoded) - where white balance, vignette, contrast, curve, saturation, LUT, grain and dither sit.
3. **Exposure timeline**: frames N, N+1, N+2...: metering on GPU at N, readback ready at N+k, pre-exposure step, history
   rescale; epochs on reset/manual stretches; settled flag.
4. **Exposure state machine**: manual / automatic / held (value lighting views) / reset; `m_ResetExposure`,
   `m_ResetPreExposure`, `m_PreExposureAutomatic`, `m_PreExposureSettled`.
5. **Histogram and percentile window**: 256 bins over log2 [-12, 16], bin 0 excluded, the low/high window shading, the
   weighted mean; center-weighted weight map (16 at center to 4 at edges).
6. **Tone curves plot**: the six operators on a log-x axis (stops from middle gray), with middle-gray markers; Filmic's
   toe/shoulder variations for Toe/Shoulder 0, 0.5, 1.
7. **Hue skew vs. Filmic's per-channel shoulder**: a saturated ramp through per-channel, luminance-only, and Filmic's
   blend (chromaticity diagram path to white).
8. **White locus**: CIE 1960 uv plot of the Planckian and daylight loci, the blend 4000-5000 K, the tint normal; the
   CAT02 pipeline as a matrix chain.
9. **Dither**: code-value staircase, rectangular vs. triangular noise PDFs, the end-snapping rule; why noise modulation
   matters.
10. **Bloom mip chain**: the half-res pyramid, 13-tap footprint (five boxes and weights), tent upsample, fractional
    deepest level.
11. **Lens flare geometry**: ghosts mirrored through the image center at scales -1.6, -0.7, 0.45, 1.2; halo ring; sun
    visibility taps.
12. **FXAA steps**: local contrast, edge orientation, walk along the edge, blend offset.
13. **Morphological AA**: edge map, a run with its two crossings, Z/L/U shapes and the reconstructed line, the area
    table's layout (4x4 crossing blocks of 33x33 distances).
14. **TAA overview**: jitter pattern (8 Halton points in a pixel), reprojection along motion of the nearest surface,
    history fetch, neighborhood box, blend weight; a "trail" being clamped away.
15. **Catmull-Rom weight merging**: 4x4 texels -> 3x3 bilinear fetches.
16. **Variance clipping in YCoCg**: min/max box vs. mean +- k sigma box, the line toward the mean.
17. **Disocclusion test**: previous camera's forward axis, stored view distances in history alpha, the threshold.
18. **TAA history lifecycle**: continue vs. reset conditions (cut, scene, resize, skipped device frame, ResetHistory),
    frames 1-8 evenly averaged then exponential (weights curve).
19. **Motion blur**: tiles, neighbor max with the diagonal rule, gather samples along two directions, depth weights.
20. **Depth of field**: thin lens geometry, CoC vs. distance curve, near/far fields, the composite's fade near in-focus
    depth.
21. **Quality layers**: section default (High) -> project value -> player's choices -> `--quality`; rows following
    the preset vs. players' rows; Custom start rule.
22. **Where quality is chosen in the editor**: Game view, Scene view chip, captures, thumbnails/bake (fixed 0.6.0).

### Screenshots (each with how to isolate it)

Default sources: the look-dev harness (`python -I Tools/LookDev.py capture --shots <glob> --aa taa,fxaa,off`), sample
copies (ThirdPerson `Scenes/Course.stscene`, PhysicsPlayground, Showcase `Scenes/Outpost.stscene`, the look-dev scene),
toggled with `component.set` on the active `PostProcess` and taken with `viewport.capture` (optionally `quality`).

1. HDR without tone mapping vs. with: `Tonemapper None` + `Exposure 0` vs. Filmic; the clipped sky.
2. Exposure sweep: manual `Exposure` -16, -14, -12 on a sunlit sample (AutoExposure false).
3. Auto exposure on/off and metering Average vs. CenterWeighted on a shot with a bright sky in the top (lookdev.overview).
4. The exposure key: `lookdev.room` with `AutoExposureKey` 0 vs. 0.12 (interior reads darker); add `renderStats.exposure`.
5. Luminance debug view (`debugView: "luminance"`, EV100 bands) of lookdev.overview and lookdev.room.
6. Adaptation: a sequence leaving a tunnel/interior (live capture `{live, frames}`) at light speed 3 vs. 0.
7. Tone curves side by side: same shot under None, Reinhard, ACES (Exposure +0.8), AgX, KhronosNeutral, Filmic
   (`component.set Tonemapper`); include saturated lights (`lookdev.lantern.*`) to show hue skew.
8. Filmic Toe 0/0.5/1 and Shoulder 0/0.5/1 on a high-contrast scene (lookdev.night or a sunset).
9. White balance 3200, 6500, 9000 K and tint -1/+1 on an interior lit by lamps.
10. Slope/offset/power examples (warm shadows via ColorOffset) vs. defaults.
11. Color lookup: Feature test's `Warm.cube` at intensity 0, 0.5, 1 (StrataTests/FeatureTest, `Lighting/Feature/Warm.cube`).
12. Banding vs. dither: a dark sky gradient with `DitherOutput` off (needs a renderer spec: only via tests/tools) vs. on;
    enlarge 4x and raise levels to make bands visible. (May need a test-harness capture; editor has no toggle.)
13. Bloom: off, default 0.04, intensity 0.2, threshold 1 vs. 0; BloomRadius 0.02 vs. 0.06 vs. 0.15; 1080 vs. 2160 same
    share.
14. Vignette 0, 0.12, 1 on a flat bright wall at 60 degree FOV; and an orthographic view.
15. Chromatic aberration 0 vs. 1 cropped at a corner (4x crop).
16. Film grain 0, 0.3, 1 on mid-gray (crop).
17. Lens flare 0 vs. 0.5 with the sun in view (lookdev.overview or Showcase) and with the sun behind a wall (no
    starburst).
18. Aliasing: AntiAliasing off vs. FXAA vs. Morphological vs. TAA Sharp at 4x crops (`--aa off,fxaa,taa`; morph via
    `component.set AntiAliasingMethod Morphological`; PhysicsPlayground's tiled floor region 1750,1150 360x360 at 3840x2160).
19. FXAA subpixel 0.25 vs. 0.75 (needs a shader edit: an engine-dev exercise screenshot).
20. TAA Original vs. Sharp vs. Custom in a slow pan (`viewport.capture {live}`), fine texture.
21. TAA trail: a moving object over glints, MinMax vs. Variance; and disocclusion ghost on/off.
22. Transparent surface under TAA with TransparentWeight 0 vs. 0.5.
23. Motion vectors debug view (`debugView: "motion"` / `ShowMotionVectors`) while the camera turns.
24. Motion blur: `tp.live.turn` with `.mb180` / `.mb90` / off (DG lists the shots), crop of the far course and the robot.
25. Depth of field: `tp.dof` (robot at f/2) vs. off; f/1.4 vs. f/8; FocusEntity.
26. Quality presets Low/Medium/High/Ultra of one shot (`viewport.capture {quality: "low"...}`), noting that post looks
    the same (the presets change cost knobs, not the look) - the motion blur samples row as the only post-related one.
27. The editor: Project Settings > Graphics Quality page (columns, Custom, players' choices, GPU stage times), the
    Scene view's quality chip, the Post Process inspector with greyed TAA tunables and tooltips.
28. The Third-Person sample's in-game Graphics settings menu (made with `StrataScript/Graphics.h`).

---

## 5. Rules and pitfalls ("why" boxes)

1. **Every HDR writer clamps with `SanitizeHDR`.** One NaN or Inf becomes a black hole or spreads through bloom, TAA and
   exposure to the whole screen; half floats overflow at 65504 (AGENTS.md "Rendering"; Common.slang 49-57).
2. **Pre-exposure is a power of two and is divided out exactly.** Multiplying by 2^n is exact in floating point unless it
   overflows/underflows, so changing it changes no image; any other factor would (DG "Light units and exposure").
3. **Never read the exposure back synchronously.** A readback ring polled frames later keeps the CPU from waiting for the
   GPU; the pre-exposure follows with hysteresis (only when off by >1 stop) so it does not oscillate.
4. **Adaptation is frame-rate independent and pauses are capped.** `1 - exp(-dt k)` and `c_MaxStepSeconds` 0.25: a
   breakpoint or minimized window must not become one giant exposure jump; tests set `AdaptationSeconds`.
5. **The exposure key only darkens.** The card measures the sun alone; brightening scenes lit by more than the sun would
   make an overcast day lighter than a sunny one and jump at dusk (PostProcessData.h 183-188).
6. **Post passes take parameters by push constants or their own buffers, never new `FrameConstants` fields.** Keeps the
   scene passes' constant layout stable and the post passes self-contained (DG "Post-processing", "Parameters";
   AGENTS.md).
7. **`TonemapConstants` grows only by appending vec4-aligned blocks** checked by static_asserts: std140 layout must
   match the shader byte for byte (PostProcessData.h 11-13, 48-51, 116-117).
8. **NVRHI places barriers only when binding sets change**: the histogram then exposure dispatch through one set needs an
   explicit `setBufferState` + `commitBarriers` (`R/SceneRendererPost.cpp:970-972`; AGENTS.md "NVRHI pitfalls").
9. **A new post effect runs between the TAA resolve and the tone mapping, reads the frame's `PostSource`, is off in
   `AddNeutralPostProcess` and bit-identical at its neutral value.** So exact-pixel tests keep meaning and the TAA history
   never contains post effects (DG "Post-processing", "A new effect"; AGENTS.md).
10. **Neutral settings render bit-identically**: grading's `Active` flag, `ColorLookupIntensity` 0, uniform branches; a
    default that "changes nothing" must not change a single bit (tests compare).
11. **Generated constants are never hand-edited** (`FilmicConstants`, `WhiteBalanceLocus.inl`, `MorphologicalAreaTable.inl`):
    their generators verify targets (`FitFilmic.py --check`).
12. **Dither once, in the last pass, in the encoded domain; grain just before it.** Dithering twice doubles noise;
    grain added before FXAA/morphological is detected as edges and blended away (Grain.slang 5-10).
13. **The dither is static, not temporal.** One code of static noise is invisible as a pattern, TAA has nothing to
    accumulate, and captures stay deterministic (Dither.slang 3-6).
14. **Jitter only the frame's copy of the camera.** Jittering `SceneCamera::Projection` would change culling, LOD, and the
    shadow cascade cache key every frame, redrawing every cascade (DG "Motion vectors and TAA").
15. **Motion vectors use unjittered matrices built in double.** A still camera must give exactly zero motion; jitter
    must not appear as motion.
16. **Sharpen only the displayed image, never the history**, and never where DoF/MB blurred (blur mask). Sharpening fed
    back into the history rings; sharpening a blur cuts streaks into steps.
17. **TAA history is counted in frames, not time, and belongs to the renderer**: slow frames keep it; each view keeps
    its own so editor views, captures and thumbnails do not disturb each other (Arch 318-323).
18. **Single images settle or turn TAA off**: captures render until 8 complete frames; thumbnails use FXAA; otherwise a
    still shows one jittered frame.
19. **The HDR alpha convention is load-bearing**: a new HDR writer that does not write alpha 1 (or multiply by 1-a for
    blended surfaces) breaks the TAA's reactive mask.
20. **Quality rows never change a scene's look**, only costs; the players' rows may turn off, never turn on, what a scene
    uses (RendererQuality.h 119-121, 170-177).
21. **Adding a quality row** touches the struct (Medium's value as default), its `PresetRow` line, `GetPreset`,
    `FromSectionValue`, `ToSectionValue`, the section field, `Clamp`, the renderer (both draw paths and caches), the
    traits line, the feature test's Custom value, and bumps `c_SectionVersion` (DG "Quality settings", "Adding a knob").
22. **Preset numbers and enum values are file and script API**: never renumber `RendererQualityPreset`,
    `TonemapOperator`, `AntiAliasingMode`, `TemporalAntiAliasingPreset`; append only.
23. **Only `GameGraphicsService` touches `GraphicsOptions.json`**, written atomically, read at most 64 KiB, validated
    (AGENTS.md "Scripting").
24. **Never render below native resolution** (owner's direction): no render scale <1, no dynamic resolution, no temporal
    upscaling, and nothing may need temporal accumulation to look right - which is why every effect is stable without TAA
    (sun shadows' fixed noise, AO resolved within the frame, static dither and motion-blur offsets).
25. **Color lookup loads asynchronously**: nothing applies while it loads; the frame counts it as pending; bindings swap
    through dummies so the post sets never need rebuilding (assets rule "never block on a load").
26. **Motion blur skips the first frame and camera cuts** (a cut's motion spans the cut) and never blurs UI/overlays.

---

## 6. Hands-on

### For game developers (editor, scripts)

1. **Find your exposure** (easy): open the Basic 3D template, switch Auto Exposure off, find the manual Exposure that
   matches auto (read `renderStats.exposure.ev100`, apply Exposure ~ 0.5 - EV100). Proves: EV, middle gray, units.
2. **Interior vs. exterior** (easy): make a room with a window in a sunny scene; compare AutoExposureKey 0, 0.12, 0.3.
   Proves: why metering to gray is not enough; the key.
3. **Pick a tone curve** (easy): render one shot with all six curves, compensate ACES by +0.8 EV; describe hue changes
   on a red lamp. Proves: what a curve does to mid-tones and saturated highlights.
4. **A night look** (medium): follow the Camera.md recipe (Exposure -1.5, 4500 K, Toe 0.6, bloom 0.06); justify each.
   Proves: grading order (white balance before curve, saturation after).
5. **Import a LUT** (medium): export a `.cube` from a grading tool (or write a 17^3 one in Python), import it with Size
   33, apply at 0.5. Proves: LUT domain, display-referred grading.
6. **Anti-aliasing shoot-out** (medium): PhysicsPlayground floor under Off/FXAA/Morphological/TAA Sharp/Original, still
   and in a slow pan (`viewport.capture {live}`). Proves: spatial vs. temporal trade-offs, texture detail.
7. **Tune TAA Custom** (medium): start Custom from Sharp; find where Resample Weight 0.5 brings back stair-steps. Proves:
   understanding of each tunable.
8. **Motion blur and DoF for a racing camera** (medium): shutter 180 vs. 90, FocusEntity on the car, f/2.8. Proves:
   shutter angle, CoC, players' rows.
9. **A Graphics options menu** (medium): write a script with Low/Medium/High/Ultra toggles and an anti-aliasing chooser
   (`Graphics::SetPreset`, `Graphics::Set("AntiAliasing", "FXAA")`, `Graphics::Save`), check `GraphicsOptions.json`,
   restart the runtime, reset with `graphics.resetPlayerOptions`. Proves: the layering project/player/command line.

### For engine developers

1. **Add a debug curve** (easy): add a `TonemapOperator` value (appended) that shows false color by stops around middle
   gray; register it; extend the feature test. Proves: enum-as-API rule, shader switch, registration.
2. **CPU twin test** (easy): write a doctest comparing `PostProcessMath::EvaluateFilmicCurve` to a hand-computed table
   and checking monotonicity. Proves: the CPU-twin testing pattern.
3. **Spot metering** (medium): add `ExposureMetering::Spot` (appended) with a small Gaussian; update Histogram.comp,
   the registration, a GPU test that puts a bright spot in the center. Proves: histogram weighting, enum/API rules,
   GPU test conventions (`Tests::GPUContext`, error count).
4. **Prove the pre-exposure is exact** (medium): reproduce `GPU.SceneRenderer.PostProcess`'s bit-identity case with two
   forced pre-exposures. Proves: floating-point exactness of powers of two.
5. **A new post effect** (hard): implement a "sharpen without TAA" or "letterbox" effect following DG "A new effect":
   parameters by push constants, `PostSource` sets, off in `AddNeutralPostProcess`, bit-identical at neutral, a GPU
   stage only if its own, feature test coverage. Proves: the whole post architecture.
6. **Change FXAA's subpixel and measure** (medium): rebuild with 0.75 vs. 0.25, measure texture detail with the
   look-dev harness's crops. Proves: quality measurement, not opinion.
7. **TAA without clamping** (medium, throwaway branch): disable the clamp and watch ghosts; then implement the variance
   clip from scratch and compare with TAA.comp. Proves: why neighborhood clamping exists.
8. **Add a quality row** (hard): e.g. bloom chain levels cap or DoF sample count as a cost row; follow every step of DG
   "Adding a knob" including traits, memory estimate, section version, feature test. Proves: quality architecture.
9. **Refit Filmic** (hard): change a target in `FitFilmic.py` (e.g. Shoulder default white at 7 stops), run the fit, see
   which tests move. Proves: the generated-constants workflow.

---

## 7. Glossary

- **HDR (high dynamic range) image**: an image whose values are light, unbounded above, stored in floats.
- **LDR / display-referred**: values in [0, 1] meant for a display.
- **Scene-linear / display-linear / encoded**: proportional to scene light / proportional to display light / after the
  sRGB transfer function.
- **Half float (RGBA16F)**: 16-bit float, max 65504, about 3 decimal digits.
- **NaN / Inf**: not-a-number and infinity results of broken arithmetic.
- **`SanitizeHDR`**: Strata's clamp of NaN, negatives and overflow before storing HDR colors.
- **Nit (cd/m^2)**: unit of luminance. **Lux**: illuminance. **Candela**: luminous intensity.
- **Luminance (Y)**: weighted sum 0.2126 R + 0.7152 G + 0.0722 B of linear Rec.709 color.
- **Luma**: the same kind of weighted sum of encoded values (FXAA's 0.299/0.587/0.114).
- **Exposure / EV / stop**: a factor of light scaling; one stop doubles it; EV is log2.
- **EV100**: exposure value at ISO 100; in Strata EV100 = log2(L) + 3.
- **Middle gray**: 18% reflectance, the value metering targets.
- **Exposure compensation**: stops added on top of metering (`Exposure`).
- **Metering**: measuring scene brightness for exposure (average, center-weighted, spot).
- **Percentile window**: ignoring the darkest and brightest shares of pixels when metering.
- **Light/dark adaptation**: how fast exposure follows brighter/darker scenes.
- **Exposure key**: Strata's rule darkening scenes that meter below a sun-lit gray card.
- **Gray card**: a 0.18 albedo reference surface.
- **Pre-exposure**: a power-of-two scale applied when writing HDR so values fit half floats.
- **Readback**: copying GPU data to the CPU, here asynchronously over a ring of buffers.
- **Histogram**: count of pixels per luminance bin.
- **Tone mapping / tone curve / operator**: the function from exposed light to display values.
- **Toe / shoulder**: the curve's shadow and highlight roll-offs.
- **Reinhard, ACES, AgX, Khronos PBR Neutral**: published tone operators.
- **Filmic (Strata)**: Strata's fitted operator.
- **Inset / outset (gamut compression)**: matrices pulling colors toward white before a per-channel curve and back after.
- **Hue skew**: per-channel curves changing a color's hue as it brightens.
- **ICtCp**: a perceptual color space used by FitFilmic to measure hue.
- **Saturation / contrast**: post-curve chroma scaling / pre-curve log-space slope around middle gray.
- **White balance**: choosing which light shows as white.
- **Color temperature / kelvin / mired**: light color by a black body's temperature; mired = 10^6 / K.
- **Planckian locus / daylight locus**: chromaticities of black bodies / CIE daylight illuminants.
- **CIE 1931 xy, CIE 1960 uv**: chromaticity coordinate systems.
- **Tint**: shift along green-magenta perpendicular to the locus.
- **Chromatic adaptation, von Kries, CAT02**: scaling cone responses to change white; CAT02 is CIE's matrix.
- **D65**: sRGB's white point (6504 K daylight).
- **Slope / offset / power (CDL)**: per-channel gain, lift and gamma-like grading.
- **3D LUT / color lookup / `.cube`**: a lattice mapping colors to colors; the common file format.
- **Trilinear interpolation**: blending 8 lattice points.
- **Half-texel remap**: addressing lattice points at texel centers.
- **sRGB transfer function**: the piecewise power-2.4 encoding of displays.
- **Banding / quantization**: visible steps from too few codes.
- **Dither / TPDF**: adding noise before quantizing; triangular probability density noise.
- **Noise modulation**: noise power varying with signal level (TPDF avoids it).
- **10-bit intermediate (R10G10B10A2)**: the LDR target before FXAA.
- **Film grain**: random texture imitating film.
- **Bloom**: glow from light scattered by a lens.
- **Mip chain / pyramid**: successively halved images.
- **Karis average**: luminance-weighted averaging that suppresses fireflies.
- **Firefly**: a single very bright pixel that flickers.
- **Tent filter**: 1-2-1 weighted blur.
- **Soft knee**: smooth threshold transition.
- **Vignette / cos^4 law**: light fall-off toward image corners.
- **Field angle**: angle of a pixel's ray from the optical axis.
- **Chromatic aberration (lateral)**: color-dependent magnification causing fringes.
- **Lens flare / ghost / halo / starburst**: internal reflections, ring, diffraction rays.
- **Aliasing**: artifacts from undersampling (jaggies, crawling, shimmer).
- **Supersampling (SSAA) / MSAA**: more samples per pixel / per-pixel coverage samples (Strata has neither).
- **FXAA**: fast approximate AA by edge detection and blending.
- **MLAA / SMAA / morphological AA**: AA reconstructing edge shapes from patterns; Strata's own variant.
- **Area table**: precomputed coverage per edge pattern and distance.
- **Z, L, U shapes**: run shapes by how the staircase turns at its ends.
- **Subpixel blend**: FXAA's smoothing of single-pixel features.
- **TAA**: temporal anti-aliasing, accumulating jittered frames.
- **Jitter / Halton sequence / radical inverse**: sub-pixel camera offsets; a low-discrepancy sequence; its construction.
- **History**: the accumulated previous image (ping-pong pair).
- **Reprojection**: fetching the history where the surface was last frame.
- **Motion vector / velocity target**: per-pixel screen motion since the previous frame.
- **Motion history**: the renderer's copy of previous instance transforms and palettes.
- **Catmull-Rom filter**: a sharp cubic interpolation with negative lobes.
- **Neighborhood clamp / variance clipping**: limiting history to the current 3x3 colors' range / to a box around their mean.
- **YCoCg**: luma-chroma color space used for clamping.
- **Ghosting / trail**: stale history visible behind moving objects.
- **Disocclusion**: a surface becoming visible that was hidden last frame.
- **Reactive mask**: raising the current frame's weight where history is unreliable (transparents).
- **Resampling blur**: softening from re-filtering history between texels each frame.
- **Sharpening (TAA)**: contrast-adaptive restoration of detail on the displayed image.
- **Camera cut**: a discontinuous camera change that invalidates histories.
- **Settle frames**: frames a still capture renders before it is taken (8).
- **Golden-ratio turn**: rotating per-pixel noise each history frame for even coverage.
- **Shutter angle**: share of frame time the shutter is open (180 = half).
- **Tile max / neighbor max**: per-tile maximum motion for motion blur.
- **Sample-and-hold blur**: display-induced blur of eye-tracked motion.
- **Circle of confusion (CoC)**: blur disk diameter of an out-of-focus point.
- **Thin lens / f-number / focal length / sensor height**: optics parameters of DoF.
- **Near field / far field**: regions in front of / behind focus.
- **Vogel (golden-angle) disk**: evenly spread spiral sample pattern.
- **Scatter-as-gather**: emulating spreading of light by gathering samples whose blur covers the pixel.
- **Post source**: which texture post passes read this frame (HDR, history, DoF, motion blur).
- **Fullscreen triangle**: one oversize triangle covering the viewport.
- **Push constants / volatile constant buffer**: small per-draw data / per-frame-versioned buffer in NVRHI.
- **std140**: GPU constant buffer layout rules.
- **Uniform branch**: a branch every thread takes the same way (cheap).
- **Quality preset / row / knob**: a named set of cost settings / one setting with a value per preset.
- **Custom (preset)**: hand-set rows.
- **Row traits (`FollowsPreset`, `GPUStage`, `MemoryBytes`)**: metadata of each row for UIs.
- **Players' rows**: comfort rows players can set under any preset.
- **Graphics options**: the players' layer over the project's quality.
- **Settings section (`Renderer.Quality`)**: a versioned block of project settings.
- **Render scale / dynamic resolution / temporal upscaling**: rendering below output size and scaling up (ruled out in
  Strata).
- **Look-dev**: controlled reference shots used to judge rendering changes.

---

## 8. Proposed chapters (teaching order)

1. **From light to picture: why images need post-processing** - concept, both, prerequisites: render targets, linear
   light (Lighting area), shaders basics. Size M, 2 screenshots. Purpose: explain HDR, the post chain and its order,
   half floats and `SanitizeHDR`, the fullscreen pass, `PostSource`.
2. **Exposure: camera, eye and meter** - concept+internals, both; prereq ch. 1, light units. Size L, 5 screenshots.
   Purpose: manual exposure and EV100, histogram metering, percentiles, center weighting, adaptation, the key, debug views.
3. **Fitting light into half floats: the pre-exposure** - internals, engine; prereq ch. 2, floating point. Size M, 0
   screenshots (diagrams). Purpose: power-of-two scaling, asynchronous readbacks, epochs, settling, TAA rescale.
4. **Tone mapping and Strata's Filmic curve** - concept+internals, both; prereq ch. 2. Size L, 3 screenshots. Purpose:
   tone curves, hue skew, the five classic operators, Filmic's form, its fit (FitFilmic.py), Toe/Shoulder, contrast and
   saturation.
5. **Color: white balance, grading and lookups** - concept+internals, both; prereq ch. 4, color spaces basics. Size L,
   3 screenshots. Purpose: chromaticity, the white locus, CAT02, CDL, `.cube` LUTs and the asset, grading order.
6. **The last step: encoding, dithering and grain** - internals, engine (with a game box); prereq ch. 5. Size M, 2
   screenshots. Purpose: sRGB, banding, TPDF dither, where it runs, film grain, determinism, the 10-bit intermediate.
7. **Lens effects: bloom, vignette, flares and fringes** - concept+internals, both; prereq ch. 2, 4. Size L, 5
   screenshots. Purpose: bloom pyramid, Karis average, radius independence, cos^4 vignette, ghosts/halo/starburst, CA.
8. **Aliasing and spatial anti-aliasing: FXAA and morphological AA** - concept+internals, both; prereq ch. 1, 6. Size L,
   3 screenshots. Purpose: sampling theory light, FXAA's algorithm, Strata's morphological AA and its area table.
9. **Temporal anti-aliasing** - concept+internals, both; prereq ch. 8, motion vectors (render-scene area), camera
   matrices. Size XL, 5 screenshots. Purpose: jitter, history, reprojection, Catmull-Rom, clamping and clipping, weights,
   disocclusion, reactive mask, sharpening, presets, history lifecycle, settling.
10. **Motion blur and depth of field** - concept+internals, both; prereq ch. 9 (motion vectors, TAA interaction), camera.
    Size L, 4 screenshots. Purpose: shutter, tile-max reconstruction, depth-aware gather; thin lens, CoC, two-field
    gather, composite stability under TAA. (Coordinate with the Camera area; this chapter owns the passes.)
11. **Quality settings and players' graphics options** - concept+internals+reference, both; prereq ch. 1 (and a
    passing knowledge of shadows/AO/reflections). Size L, 3 screenshots. Purpose: cost vs. look, rows and presets,
    traits, Custom, the section, who follows what, `IGameGraphics`, the options file, the script SDK, why no render
    scale.
12. **Tutorial: giving a scene a camera look** - tutorial, game; prereq ch. 2-7, 9. Size M, 6 screenshots. Purpose:
    take a sample from default to a styled day and night look with exposure, Filmic, grading, a LUT, bloom, vignette,
    TAA Sharp, and a Graphics menu.
13. **Tutorial: adding a post effect to Strata** - tutorial, engine; prereq ch. 1, 6, 9. Size M, 1 screenshot.
    Purpose: implement an effect end to end following the rules (push constants, PostSource, neutral helper, tests,
    GPU stage, feature test).
14. **Reference: Post Process component and Renderer.Quality** - reference, both; prereq none. Size M, 0 screenshots.
    Purpose: every property with range, default and effect; every quality row with its four preset values and cost.

---

## 9. Not determined

- **Not read line by line**: `R/SceneRendererPost.cpp:697-813` (`EnsureDepthOfFieldResources`); the DoF shaders'
  bodies (Prepare, Tiles, Dilate, Gather, Composite) beyond their header comments and function lists; MotionBlurTiles
  and MotionBlurNeighbors bodies; `MotionBlur.comp` gather body (56-116) only skimmed by structure; LensFlare.comp bodies
  (50-137); MorphologicalEdges and MorphologicalBlend bodies; FXAA.frag lines 140-169; Bloom.comp 125-140.
- `R/RendererQuality.cpp` 200-972 (parsers, `Clamp`, `MakeSection` field texts, `Normalize`, `MakeCustomStart`) read only
  by their signatures and the DG description.
- `Strata/src/Strata/Runtime/GameGraphicsService.cpp`, `Scripting/ScriptHostAPI.cpp`'s graphics functions,
  `StrataScriptCore/Include/StrataScript/Graphics.h` bodies, `StrataEditor/src/UI/GraphicsQualityPage.cpp`,
  `EditorGraphicsCommands.cpp`: located, not read.
- `R/ColorLookup.cpp` and `Asset/ColorLookupImporter` (cube parsing, resampling): from DG only.
- Tests: only the test-case names of PostProcessMath, GPUScenePostProcess, GPUSceneCamera, GPUSceneTAA, RendererQuality,
  TAASharpening were read; bodies of all test files, `GPUSceneTAAQualityTests.cpp`, `TAATestUtils.h`, motion blur, DoF,
  lens flare, morphological, grain, color lookup, `GameGraphicsTests.cpp`, `ScriptGraphicsTests.cpp` not read.
- `Docs/DeveloperGuide.md` "Look-dev harness" section, "Interpolation", "Sun shadows" (static noise rationale),
  "Lighting" (white furnace) not read; Arch beyond lines 300-330 and 925-960 not read.
- **Documentation drift found** (worth a note to the planner, not to the book): DG "Color lookup" bullet speaks of
  `m_ColorLookupLayout` and `GetColorLookupSet` and "five tone-mapping sets", while the code uses `m_TonemapInputLayout` /
  `GetTonemapInputSet` shared with the lens flare (`R/SceneRendererPost.cpp:102-109, 1167-1218`); DG "Sharpening" names
  `TonemapParameters::Sharpening`, the struct is `RenderData::TonemapConstants`; DG says `RenderData::c_TemporalSkyDistance`,
  the TAA shader uses a local `c_SkyDistance` (65504). Several converted shaders include `Include/Common.slang` twice
  (harmless, guarded; a wave-8 GLSL-to-Slang conversion artifact, see `S/Include/Common.slang:59-61`).
- Release attribution is partly inferred: bloom, tone mapping, "color grading" and FXAA appear in 0.3.0's list; it is not
  stated which tone operators existed then (ACES was the default until 0.7.0). TAA's presets: the 0.6.0 notes describe
  Sharp/Original/Custom, so presets shipped with 0.6.0. Wave-8 (0.8.0, unreleased) changes in this area beyond the shader
  conversion and new quality rows were not traced.
- Exact GPU costs are from the docs (RTX 5090, M2 Max), several marked provisional; not verified (no runs allowed).
- Whether the editor exposes `DitherOutput` (it seems not: a specification field only) - affects screenshot 12.
- Ownership boundaries to settle with the planner: depth of field (Camera area?), motion vectors and motion history
  (render-scene area), light units and sky presets (Lighting area), the non-post quality rows (shadows, AO, reflections,
  GI areas), `Tools/GenerateBlueNoise.py` (shadows).
