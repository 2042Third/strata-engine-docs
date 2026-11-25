# Inventory: indirect light (render-indirect)

Area: ambient light and occlusion, reflection probes, screen-space reflections, global illumination, specular occlusion,
the white-furnace test and the lighting debug views. Checkout: `G:/GameEngineAI`, branch `main` at `822a7a46`. All paths are
relative to the repository root. Line numbers are at that commit.

Abbreviations: **DG** = `Docs/DeveloperGuide.md`, **ML** = `Docs/Manual/Lighting.md`, **RN8** = `Docs/Plans/Wave8/ReleaseNotes.md`
(0.8.0 in preparation), **R** = `Strata/src/Strata/Renderer/`, **SH** = `Strata/shaders/`.

Document sections used (heading line in the file):

| Doc | Heading | Line |
| --- | --- | --- |
| DG | Look-dev harness | 666 |
| DG | Scene renderer and lighting | 3955 |
| DG | Quality settings | 4009 |
| DG | Lighting | 4797 |
| DG | Ambient occlusion | 4907 |
| DG | Global illumination | 4942 |
| DG | Light units and exposure | 5297 |
| DG | Fog and atmosphere (boundary: the atmosphere's sky cube) | 5754 |
| DG | Reflections | 5843 |
| ML | The sky | 72 |
| ML | Reflection probes / Times of day with baked probes | 189 / 219 |
| ML | Screen-space reflections | 229 |
| ML | Materials that keep their energy | 259 |
| ML | Sun and sky presets | 279 |
| ML | Ambient occlusion | 306 |
| ML | Global illumination (experimental) | 320 |
| ML | Debug views | 361 |
| RN8 | What's new: Reflections (R1) 81, Reflections (R2) 119, GI stages 1-4 189-239, "smooth light between probes" 241, "light at contacts" 253; Known issues 369 | |
| Spec | `Docs/Plans/Wave8/specs/radiance-cascades-world.md` (the GI's design, D1-D19; "Review corrections" at 1293 win over the body) | 1 |
| Spec | `Docs/Plans/Wave8/specs/reflections.md` (R1/R2 design; not read in detail) | |
| Spec | `Docs/Plans/Wave8/specs/radiance-cascades.md` (the superseded **screen-space** form of the GI plan; not read) | |
| Plan | `Docs/Plans/Wave8/plan.md` 4.3 `reflections` (586), 4.4 `radiance-cascades` (648), S0.11 the indirect seam (331) | |

Release history from `Docs/Releases/*.md`: image-based lighting from HDR maps and the procedural sky and GTAO since **0.3.0**
(0.3.0.md:49-50); reflection probes, Checkerboard screen-space reflections (TAA only), Extract Sun / Remove Sun, the physical
atmosphere and the `imageCubeArray` requirement in **0.6.0** (0.6.0.md:60-75, 303); energy compensation, specular
anti-aliasing, history-free AO denoising, AO radius clamp and multi-bounce, sky presets, the five lighting debug views and the
Spatial screen-space reflections at High/Ultra in **0.7.0** (0.7.0.md:68-75); IOR-to-F0, sized highlights (sun Angular
Diameter, point/spot `SourceRadius`), 256-texel probes at High/Ultra, sun-free probe bakes, SSR validation (R1/R2), the
indirect seam (`IndirectLight.slang`) and experimental global illumination in the coming **0.8.0** (RN8).

---

## 1. Features

### 1.1 Image-based lighting from the sky (the "environment")

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| Sky light component | First active `SkyLightComponent` lights the scene: `EnvironmentMap` (equirect HDR), `Procedural`, or `Atmosphere`; `Intensity`, `Rotation` (maps only), `ShowBackground`, `BackgroundBlur`, `AmbientColor` (fallback without a map) | `R/RendererComponents.h:80-125` (`SkyLightSource` 80, `SkyLightComponent` 91); chosen in `SceneRenderer::UpdateEnvironment` `R/SceneRenderer.cpp:912` | DG 3955 (bullet "Image-based lighting comes from..."), ML 72 |
| Procedural sky cube | Zenith/horizon/ground colors (nits) + sun disk where the directional light comes from; written into mip 0 of the environment cube; recomputed only when `ProceduralSkyParameters` change (`SceneRendererStats::EnvironmentUpdates`) | `SH/IBL/ProceduralSky.comp.slang`; `SceneRenderer::GetProceduralSkyParameters` `R/SceneRenderer.cpp:895` | DG 3955; test `GPU.ProceduralSky` (`StrataTests/src/Renderer/GPUProceduralSkyTests.cpp:69`) |
| Equirect to cube | Converts an equirectangular HDR texture into a cube (sky maps and probe captures) | `SH/IBL/EquirectToCube.comp.slang`, `Include/IBL.slang` `DirectionToEquirect` (IBL.slang:28-34) | DG 3955, 5843 |
| Environment filter chain | One chain for every sky source: cube mips (`CubeDownsample`), irradiance cube (32/face, 256 cosine samples), prefiltered cube (6 roughness levels 0, 0.2..1; per-face size = quality's `EnvironmentResolution`: 256 Low/Medium, 512 High/Ultra) | `SceneRenderer::FilterEnvironment`/`FilterEnvironmentStep` `R/SceneRenderer.cpp:863-893`; constants `R/SceneRenderer.cpp:52-61`; `SH/IBL/CubeDownsample.comp.slang`, `Irradiance.comp.slang`, `Prefilter.comp.slang` | DG 3955 |
| Filtered importance sampling | Each GGX/cosine sample reads a source mip matched to its solid angle, so few samples give no noise | `SH/IBL/Prefilter.comp.slang:35-58`, `Irradiance.comp.slang:28-42` | DG 3955 |
| Prefilter sample budget | `RendererQuality::GetPrefilterSamples(size, mip)`: 512 at 256; at 512, 128 for levels 1-2 | `R/RendererQuality.h:225-228` | DG 3955 |
| BRDF lookup table (split sum) | 128x128 RG16F table of (scale, bias) of F0 over (NoV, roughness), 512 samples, height-correlated Smith | `SH/IBL/BRDFLut.comp.slang`; created `R/SceneRenderer.cpp:656-668` | DG 4797 (Energy compensation) |
| Shared environments | Maps of a texture shared between renderers by texture and size | `SceneRenderer::FindSharedEnvironment` `R/SceneRenderer.h:1457` | DG 3955 |
| Constant ambient | `AmbientColor` lights diffuse only when there is no environment (form `ST_INDIRECT_AMBIENT`) | `SH/Include/IndirectLight.slang:76-80` | DG 4797 (indirect seam) |
| Preview lighting | Editor views of an unlit scene get a preview sun and the default procedural sky (`SceneRenderOptions::PreviewEnvironment`, `NeedsPreviewLighting`) | `R/SceneRenderer.h:398, 827`; `R/SceneRenderer.cpp:929-935` | DG 3955 |
| Extract Sun / Remove Sun | Editor: make the directional light the map's sun; the importer paints the disk out of the map | `lighting.extractSun` `StrataEditor/src/Editor/EditorLightingCommands.cpp:977`; tests `GPU.Editor.Lighting` (`StrataTests/src/Editor/GPUEditorLightingTests.cpp:598, 777`) | ML 72 |
| Sky presets | Clear / Hazy / Overcast / Golden Hour (sun + sky + auto exposure) in one undo step | `lighting.applySkyPreset` `EditorLightingCommands.cpp:953`; `R/SkyPresets.h` | ML 279; tests `Editor.Lighting` (`EditorLightingCommandTests.cpp:71`) |
| Atmosphere sky cube | The atmosphere writes the environment cube too (one prefilter level per frame, switched every half degree of sun) | `R/SceneRendererAtmosphere.cpp`, `SH/IBL/AtmosphereCube.comp.slang` | DG 5754 (owned by the fog/atmosphere area; only its output is used here) |

### 1.2 The shading model the indirect light rests on (PBR.slang)

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| GGX + height-correlated Smith + Schlick | Microfacet specular, Lambert diffuse | `SH/Include/PBR.slang:33-57` | DG 4797 |
| Multiple-scattering energy compensation | Specular x `1 + F0 (1/E - 1)`, E = dfg.x + dfg.y; also image light, coat, glass | `GetSpecularEnergy` `PBR.slang:59-71`; used `Forward.frag.slang:127` (`SpecularColor`) | DG 4797; ML 259; arrived 0.7.0 |
| Specular anti-aliasing | Roughness widened by the normal's screen-space variance (cap 0.18) | `WidenRoughness` `PBR.slang:73-91`; `Forward.frag.slang:398-414`; `SceneRendererSpecification::SpecularAntiAliasing` (`MaterialParams.z`) | DG 4797; 0.7.0 |
| F0 from IOR | `((n-1)/(n+1))^2`, 1.5 -> literal 0.04 | `MaterialGPU::GetDielectricF0` `R/MaterialData.cpp:51-59` (into `MaterialData::Absorption.w`) | DG 4797; ML 259; 0.8.0 |
| Sized highlights | Sun Angular Diameter and point/spot `SourceRadius` widen only D | `GetSourceLobeAlpha2` `PBR.slang:21-31`, `GetLobeAlpha` 119-124; `RenderData::GetSunLobeAlpha2` `R/SceneRenderData.h:121-128`; `FrameConstants::ReflectionParams.w` set `R/SceneRenderer.cpp:2565-2573` | DG 4797, 5843 (Highlights); 0.8.0 |
| Horizon fade | Image light fades when a normal map turns R below the geometric surface | `GetHorizonFade` `PBR.slang:93-102` | DG 4797 |

### 1.3 The indirect light's seam (forward pass)

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| `IndirectInputs` | Per-pixel struct both gathers read (split-sum reflectance, R, geometric normal, occlusions, probes, SSR, sky reads, GI field) | `SH/Include/IndirectLight.slang:15-39`; filled by `GetIndirectInputs` `SH/Scene/Forward.frag.slang:118-171` | DG 4797 (The indirect light's seam) |
| The four forms | `ST_INDIRECT_PROBES/SCREEN/SKY/AMBIENT`, 0.7.0's branch order kept bit for bit | `IndirectLight.slang:9-13`; chosen `Forward.frag.slang:157-159` | DG 4797 |
| Diffuse gather | Probes' SH irradiance + sky's share, or sky, or ambient; times occlusion color | `GatherIndirectDiffuse` `IndirectLight.slang:52-82` | DG 4797 |
| Specular gather | Probes' radiance + sky share; SSR mixed premultiplied; specular occlusion only on the fallback | `GatherIndirectSpecular` `IndirectLight.slang:84-107` | DG 4797, 5843 |
| Field gather (GI join) | Field irradiance on diffuse albedo, under diffuse occlusion without the multi-bounce fit | `GatherIndirectField` `IndirectLight.slang:109-118`; join `Forward.frag.slang:301-321` | DG 4942 (The join) |
| Compose | Each form's scale where 0.7.0 applied it | `ComposeIndirect` `IndirectLight.slang:120-129` | DG 4797 |
| Clear coat's image light | Coat reflects probes/sky via `SampleSpecularLight`, with its own Lagarde occlusion and horizon fade | `Forward.frag.slang:107-116, 323-335` | DG "Clear coat and glass" (6071; other area) |
| Probe capture mode | `MaterialParams.w` 1 drops lights' specular in a bake | `LightSurface` `Forward.frag.slang:84-101` | DG 5843 (bake) |

### 1.4 Ambient occlusion

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| GTAO | Horizon-based, cosine-weighted visibility per screen slice from prepass depth+normals | `SH/Effects/GTAO.comp.slang:41-141`; dispatch `SceneRenderer::RenderAmbientOcclusion` `R/SceneRendererAmbientOcclusion.cpp:116-143` | DG 4907; ML 306; 0.3.0 |
| Quality samples | Low 1x4, Medium 2x6, High 3x8, Ultra 4x12 (slices x steps per side) | `AmbientOcclusionLevel` `R/RendererQuality.h:74-86`; table `R/RendererQuality.cpp:214-216`; row 50 | DG 4907, 4009 |
| Fixed 4x4 pattern (no history) | Slice rotation and step jitter from the ordered-dither order, never the frame | `GTAO.comp.slang:32-33, 70-73` | DG 4907; 0.7.0 |
| History-free denoiser | Separable 5x5 tent resolve of the 16 phases + 5x5 bilateral blur, one dispatch, 24x24 shared tile | `SH/Effects/AODenoise.comp.slang` (`ResolveAlong` 68-90, main 92-172) | DG 4907; 0.7.0 |
| Radius clamp | World radius kept on screen between 0.3% (>= 1.5 px) and 12% of view height | `GTAO.comp.slang:61-68`; `c_AOMinRadiusFraction`/`Max` `R/SceneRenderData.h:450-451`; `R/SceneRendererAmbientOcclusion.cpp:125-126` | DG 4907; ML 306 |
| Thin-occluder relaxation | Horizon relaxes toward lower samples by `1 - 0.9^(6/steps)` | `GTAO.comp.slang:123-126`; `SceneRendererAmbientOcclusion.cpp:127-128` | DG 4907 |
| Multi-bounce fit | `x / (1 - rho (1-x) h(x, rho))`, fitted to 2D radiosity | `SH/Include/AmbientOcclusionFit.slang:1-17`, `R/AmbientOcclusionFit.h`; generator `Tools/FitAOMultiBounce.py`; applied `Forward.frag.slang:293-296` | DG 4907; ML 306; 0.7.0 |
| Half-float targets | R16F when the device stores it, R32F else; shader variants `GTAOHalf`, `AODenoiseHalf` | `SceneRendererAmbientOcclusion.cpp:26-60`; `Strata/CMakeLists.txt:195, 197` | DG 4907 |
| Component fields | `PostProcessComponent::AmbientOcclusion` (on), `AmbientOcclusionRadius` (1 m), `AmbientOcclusionIntensity` (1), `AmbientOcclusionMultiBounce` (on) | `R/RendererComponents.h:286-291` | ML 306 |
| Where AO applies | Indirect light only (diffuse x occlusion color; specular through Lagarde's specular occlusion); not on transparent surfaces | `Forward.frag.slang:284-296`, 160-166 | DG 4797, 4907 |

### 1.5 Specular occlusion

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| Lagarde's specular occlusion | `clamp(pow(NoV + ao, exp2(-16 r - 1)) - 1 + ao)` times horizon fade, on the probes/sky fallback | `Forward.frag.slang:160-164` | DG 4797, 5843 |
| SSR keeps its light | What a screen ray found is darkened only by the material's occlusion map (`ScreenReflectionOcclusion`) | `Forward.frag.slang:165-166`; `IndirectLight.slang:101-105` | DG 5843; RN8 R1; 0.8.0 |
| Planned: open share in specular occlusion | GI field's sky visibility along R (D18.4, below the cut, not on main) | spec `radiance-cascades-world.md:896-917` | not landed |

### 1.6 Reflection probes

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| `ReflectionProbeComponent` | `Capture` (equirect HDR, nits), `Extents` (half sizes, x entity scale), `BlendDistance`, `BoxProjection`, `Intensity`, `Priority`; `c_MinExtent` 0.01 | `R/RendererComponents.h:153-170` | DG 5843; ML 189; 0.6.0 |
| Per-frame gather and ranking | Active probes with a capture, frustum-tested bounding sphere, strongest `MaxReflectionProbes` (<= 16): priority, then smaller volume, then entity | `SceneRenderer::GatherReflectionProbes` `R/SceneRendererReflectionProbes.cpp:193-430`; `IsStronger` 59-66 | DG 5843 |
| Shader: two-probe blend | Walk the list (<= 16 box tests), blend the first two whose boxes hold the pixel | `EvaluateReflectionProbes` `SH/Include/ReflectionProbes.slang:98-125`; weight `GetProbeWeight` 60-70 | DG 5843 |
| Box projection | Ray-box exit point looked up from the box center | `GetProbeLookup` `ReflectionProbes.slang:72-86` | DG 5843; ML 189 |
| SH irradiance | 9 RGB coefficients per slot, projected on GPU from the cube's 32-texel level | `SH/IBL/ProbeIrradiance.comp.slang:42-87`; `Include/SphericalHarmonics.slang`; `EvaluateProbeIrradiance` `ReflectionProbes.slang:42-51` | DG 5843 |
| Probe cache (cube array) | RGBA16F cube per slot (`ReflectionProbeResolution` 128 Low/Med, 256 High/Ultra; 6 levels), LRU slot reuse, made with the first probe in view, released when none | `EnsureReflectionProbeResources` `SceneRendererReflectionProbes.cpp:113`; `acquireSlot` lambda ~277-296; row `R/RendererQuality.cpp:55`, `R/RendererQuality.h:159-165` | DG 5843; 256 at High in 0.8.0 |
| Capture residency hold | Capture requested at High priority, held whole in the texture streamer until converted, then released to its mip tail | `hold`/`holdWhole` lambdas `SceneRendererReflectionProbes.cpp:~297-318`; `ReleaseStaleReflectionProbeHolds` 107 | DG 5843; DG "Residency" (asset area) |
| GPU conversion | EquirectToCube -> downsample -> Prefilter into the slot's 6 levels -> ProbeIrradiance; at most 2 per frame with `SpreadLightingUpdates` | `SceneRenderer::ConvertReflectionProbes` `SceneRendererReflectionProbes.cpp:451-506`; `c_ReflectionProbeConversionsPerFrame` | DG 5843 |
| Resolution change takeover | New-size cubes filled beside the shown ones, swapped once every probe in view converted | `m_ReflectionProbesNext` (`SceneRendererReflectionProbes.cpp:457`) | DG 5843; test `GPUReflectionProbeTests.cpp:522` |
| Bindings | SRV 9 cube array (black one-slot without probes), SRV 10 probe buffer (`RenderData::ReflectionProbeBuffer`, 3.6 KB) | `ReflectionProbes.slang:16-40`; `R/SceneRenderData.h:304-339` | DG 5843 |
| Stats | `ReflectionProbes`, `ReflectionProbeConversions`, `ReflectionProbesPending` | `SceneRendererStats` in `R/SceneRenderer.h` | DG 5843 |
| Probe bake | `lighting.bakeProbes`: own renderer (`ForBake()`), six 256-px 90-degree HDR views per probe with `HDROutput` + `ProbeCapture` (no sun disk, no light specular), power-of-two pre-exposure, assembled into 1024x512 equirect `.hdr`, imported to `Assets/Lighting/<scene>/<id>.hdr`, one undo step that trashes the probe's previous bake | `StrataEditor/src/Editor/EditorLightingCommands.cpp:872`; `StrataEditor/src/Editor/ProbeBake.h:19-47` (`GetFaceCamera`, `AssembleEquirect`, `ChoosePreExposure`, `RemoveStaging`), `ProbeBake.cpp` | DG 5843 (The bake); ML 189; sun-free in 0.8.0 |
| Bounces by re-baking | A bake draws the probes' current captures, so each bake adds a bounce; the showcase bakes 8 times | DG 5843; ML 189; RN8 176-180 | |
| Times of day pattern | One probe set per time of day, switched with `SetActive` from a script | ML 219; `Samples/Showcase` | |

### 1.7 Screen-space reflections

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| Component fields | `PostProcessComponent::ScreenSpaceReflections` (off), `...Intensity` (1), `...MaxRoughness` (0.5; fades over last quarter) | `R/RendererComponents.h:313-317` (note: its comment still says "with TAA only", true only of Checkerboard) | ML 229 |
| Quality row `Reflections` | Off (Low), Checkerboard (Medium, 0.6.0, TAA only), Spatial (High), SpatialHigh (Ultra) | `ReflectionsQuality` `R/RendererQuality.h:88-98`; row `R/RendererQuality.cpp:52`; steps `GetScreenReflectionSteps` (`RendererQuality.h:110-120, 222`) | DG 5843, 4009 |
| Surface target | Prepass variant writes normal-mapped view normal (octahedral), widened roughness, metallic (RGBA16F) | `SH/Scene/DepthPrepass.frag.slang` with `ST_PREPASS_SURFACE` (lines 14, 42-162); registered `Strata/CMakeLists.txt:183-184` | DG 5843 |
| Shared ray setup | Screen-space line in (UV, depth), cut at screen edge / far / near, rejects rays into the surface | `BeginScreenRay` `SH/Include/ScreenReflections.slang:39-86` | DG 5843 |
| Hit confidence | Back-facing hits get 0; edge fade only when the ray leaves the screen | `GetHitConfidence` `ScreenReflections.slang:88-102` | DG 5843; RN8 R1 |
| Checkerboard trace | Half res, one pixel of each 2x2 per frame, 24 quadratic steps + IGN that turns per frame, 6 bisections, thickness margin, reads the TAA history along the hit's motion | `SH/Effects/ScreenSpaceReflections.comp.slang:51-127`; `SceneRenderer::TraceScreenReflections` `R/SceneRendererScreenReflections.cpp:137` | DG 5843; 0.6.0 |
| Spatial trace | Full res, every pixel, 32 (48) steps offset by GTAO's fixed 4x4 order, candidate crossings validated (depth or plane crossing), up to `MaxCandidates` (2/3) rejected, last point half a pixel before the end | `SH/Effects/ScreenSpaceReflectionsSpatial.comp.slang:190-274` (`BisectCrossing` 123-149, `ValidateCrossing` 151-171, `RefineCrossing` 173-188, `RefinePlaneCrossing` 95-115); `TraceSpatialReflections` `SceneRendererScreenReflections.cpp:296` | DG 5843; 0.7.0, validation 0.8.0 |
| Previous-frame color copy | Full-res copy (B10G11R11) beside the half-res blurred scene-color copy glass reads; sharp up to roughness 0.05, blurred levels from 0.15 | `SH/Effects/SceneColorCopy.comp.slang`; `ScreenSpaceReflectionsSpatial.comp.slang:264-271` | DG 5843 |
| Spatial resolve | 5x5 ratio estimator, kernel (0.5,1,1,1,0.5), GGX-lobe weight over neighbour's density, plane and normal weights | `SH/Effects/ReflectionResolve.comp.slang:42-120` | DG 5843; RN8 R1 |
| Forward mix | Premultiplied: `radiance (1-a) + rgb` over the probes'/sky's specular before the split sum | `Forward.frag.slang:139-146`; `IndirectLight.slang:101-105` | DG 5843 |
| Pending first frame | Spatial modes need a previous copy; captures render one more frame (`c_MaxCaptureReflectionFrames`, `ProjectThumbnail::c_MaxReflectionFrames`) | DG 5843 | |
| Memory | Checkerboard ~20 MiB at 1080p; Spatial ~150 MiB more at 4K | DG 5843; ML 229; `ReflectionsBytes` `R/RendererQuality.cpp:106-130` | |
| Transparent surfaces get none | Deferred | DG 5843; ML 229 | |

### 1.8 Global illumination (experimental, world-space radiance cascades)

What `main` has: stages 1-4 of the spec (voxels; light behind debug views; join to shading; multi-bounce), plus the two
hardening batches "smooth light between probes" (depth moments, RN8 241) and "light at contacts" (relocation and the voxel
guard, RN8 253). Not on main (spec D18 "below the cut", `radiance-cascades-world.md:896-917`): local lights in the voxels,
dynamic/skinned occupancy, the open share in specular occlusion, an Ultra layout, textured albedo per voxel, hardware ray
queries; nested probe-field levels and denser probes near surfaces (DG 4942 intro: "follow"). DG mentions an octahedral and
an SH field tried in "batch 1, not landed" (DG GI "What it cannot do").

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| Scene ask | `PostProcessComponent::GlobalIllumination` (off), `GlobalIlluminationIntensity` (1, 0-4, inactive reason) | `R/RendererComponents.h:292-296` | DG 4942; ML 320 |
| Quality row | `Renderer.Quality.GlobalIllumination`: Off/Low/High (Off at Low, Medium; High at High, Ultra), memory by `GetMemoryBytes` | `GlobalIlluminationLevel` `R/RendererQuality.h:100-108`; row `R/RendererQuality.cpp:54, 148-172` | DG 4942, 4009 |
| Layout | High: 4 voxel levels 128x64x128 from 10 cm, 4 cascades from 0.5 m (48x40x48 probes), 16..1024 directions; Low: 3 levels 64x32x64 from 20 cm, 3 cascades from 1 m. 146.4 MiB High, 22.6 MiB Low | `GlobalIllumination::ComputeLayout` `R/GlobalIlluminationLayout.cpp:147-192`; structs `R/GlobalIlluminationLayout.h:25-105` | DG 4942 (Layout) |
| Voxel clipmap (CPU) | Per level a camera-centered window snapped to 4-voxel steps, toroidal storage, anchors (1024-voxel multiples), region queue (changes, slabs, whole windows), budgets 500k / 4M triangles a frame | `VoxelClipmap` `R/VoxelClipmap.h:84-225`, `R/VoxelClipmap.cpp`; arithmetic `GlobalIlluminationLayout.h:121-187` | DG 4942 (The clipmap) |
| What enters the voxels | Static-arena indexed opaque/alpha-masked submeshes; movers excluded for 30 frames; LOD within half a voxel for open meshes; material means (`RenderData::GIMaterial`, `Texture::GetLinearMean`) | `VoxelClipmap.cpp`; `IVoxelSceneSource` `VoxelClipmap.h:24-41` | DG 4942 (What enters) |
| GPU voxelization | `VoxelTriangles` (thread per triangle, Akenine-Moller test, buffer atomics), `VoxelTiles` (large triangles, indirect), `VoxelFill` (winding columns: closed meshes become solid), `VoxelFinalize` (material/emission RGB9E5/normal, two-sided detection) | `SH/GI/VoxelTriangles.comp.slang`, `VoxelTiles`, `VoxelFill`, `VoxelFinalize`; `SH/Include/Voxelize.slang` (`TriangleBoxOverlap` 160-196, `IsVoxelSolidFor` 290, `FacesVoxel` 308, `WriteVoxel` 320); dispatch `SceneRenderer::RecordGlobalIllumination` `R/SceneRendererGlobalIllumination.cpp:639-831` | DG 4942 (Voxelization, Closed meshes and the fill, Finalize) |
| Closed-mesh test | Welded positions, every directed edge has one opposite | `MeshUtils::IsClosed`, `Mesh::IsClosed` | DG 4942; test `Renderer.Mesh` "Closed meshes are found" |
| Light injection | Every voxel of every level every frame: albedo x sun irradiance x voxel shadow walk + emission (+ last frame's field for bounces) | `SH/GI/VoxelInject.comp.slang` (header 9-21) | DG 4942 (The light) |
| Level downsample | Coarser levels take the finer level's light where it holds the scene | `SH/GI/VoxelDownsample.comp.slang` | DG 4942 |
| Probe validity, move, relocation | Dead probes inside solids; probes on surfaces move off along the normal; cascade-0 probes > half inside search their cell (4 rings of 26 directions) | `SH/GI/ProbeValidity.comp.slang` (header 1-21) | DG 4942 (D18.7 relocation) |
| Probe weights | Each probe's 8 parents' trilinear weights x validity x transmittance | `SH/GI/ProbeWeights.comp.slang` | DG 4942 |
| Cascade march + merge | Top cascade down to 1: front-to-back voxel march with transmittance, lead-in, overlap, sub-rays; unabsorbed rays continue into parents' merged rays; only the top reads the sky | `SH/GI/CascadeMarch.comp.slang:25-100`; `SH/Include/GIMarch.slang:21-76` | DG 4942 |
| Field reduce | Cascade 0's 64 directions continued by cascade 1, summed into an ambient cube (6 RGBA16F faces) per probe + depth moments (10x10 octahedral tile) | `SH/GI/FieldReduce.comp.slang` (header 5-19) | DG 4942 |
| Multi-bounce by re-injection | Last frame's field read at each voxel, x clamped albedo (<= 0.9) x gain; bounce per frame; settle frames from the brightest albedo | `GlobalIlluminationSettings::BounceGain` `GlobalIlluminationLayout.h:25-33`; `GetSettleFrames` `GlobalIlluminationLayout.cpp:405-412`; `SettleGlobalIllumination` `SceneRendererGlobalIllumination.cpp:615` | DG 4942 (Multi-bounce); 0.8.0 stage 4 |
| Field sampling in the forward pass | 8 cascade-0 probes around the normal-biased point: trilinear x validity x facing x voxel-guard visibility; min-visible fade; fade at the field's edge | `SampleIrradianceField` `SH/Include/GIField.slang:181-236`; `ReadAmbientCube` 41-51; `GetFieldWeight` 35-39; `PushOutOfSolid` 139 | DG 4942 (The field in the forward pass) |
| Level sampling | Finest level whose valid box holds the point, blended by distance from camera | `SH/Include/GlobalIllumination.slang:157-189` | DG 4942 (Sampling) |
| The join | `ReflectionParams.y` 1 / `.z` intensity; diffuse = today's x (1-w) + field x w; specular untouched; off -> 0.7.0's image bit for bit | `R/SceneRenderer.cpp:3321-3330`; `Forward.frag.slang:301-321` | DG 4942 (The join) |
| Field constants b3 | `RenderData::GIFieldConstants` in its own buffer, not `FrameConstants` (and the unexplained reason: recompiled GTAO/SSR repeat differently) | `GIField.slang:13-24`; DG 4942 (Finalize bullet) | DG 4942; Roadmap open item (`Docs/Roadmap.md:662`) |
| Debug views | `voxels`, `gi`, `open`, `probes` (`GI/VoxelView.frag`, `GI/ProbeView.frag`) | `SceneLightingView` `R/SceneRenderer.h:324-336`; `SceneRenderer::DrawVoxelView` `SceneRendererGlobalIllumination.cpp:1077`, `DrawProbeView` 1175 | DG 4942; ML 320 |
| Stats and readbacks | `GlobalIllumination`, `...Pending`, `...Settled`, `GIVoxelizedTriangles`, `GIQueuedRegions`, `GIWaitingProxies`, `GIMovingProxies`, `GIUnvoxelizedSubmeshes`; GPU `GITiles`, `GITileOverflow`, `GIDeadProbes`, `GILiveProbes`, `GISurfaceVoxels`; `ReadGlobalIllumination{Voxels,Validity,Field,FieldDepth}` | `SceneRendererGlobalIllumination.cpp:1040-1175` | DG 4942 (Statistics) |
| Capture waits | `viewport.capture` and the project picture wait for `GlobalIlluminationSettled` (`c_MaxCaptureGIFrames`, `c_MaxGIFrames`) | Editor `EditorViewportCommands.cpp`, `ProjectThumbnail` | DG 4942 |
| GPU stage | `GPU.RadianceCascades` (after `GPU.AO`, before `GPU.Reflections`) | `R/SceneRenderer.cpp:3460-3478` | DG 4942 |

### 1.9 Lighting debug views, statistics and the white furnace

| Feature | What it is | Where | Doc |
| --- | --- | --- | --- |
| Lighting views | `Lighting` (albedo 1), `AmbientOcclusion`, `Indirect`, `Luminance` (EV100 bands), `Albedo` (marks < 0.03, > 0.85) + the GI four | `SceneLightingView` `R/SceneRenderer.h:324-336`; colors `LightingViewColors` 338-363; `SH/Overlay/LightingView.frag.slang`; `SH/Include/LightingView.slang`; forward branch `GetLightingView` `Forward.frag.slang:72-82, 280-292` | DG 4797 (Lighting debug views); ML 361; 0.7.0 |
| Value views without pre-exposure | AO/Albedo/Open written unexposed (half-float subnormals otherwise) | `IsLightingValueView` `Forward.frag.slang:78-82`; `SceneRenderer::IsLightingValueView` `R/SceneRendererLightingView.cpp:73` | DG 4797 |
| Statistics | GPU histograms (EV100 quarter bins -8..24, value bins), ring of 3 readbacks; percentiles, `SunIlluminance`, `SkyIlluminance`, `SunToSkyRatio` | `SH/Effects/LightingViewStats.comp.slang`; `RecordLightingView` `SceneRendererLightingView.cpp:97`, `ResolveLightingViewStats` 257; `LightingViewStats` `R/SceneRenderer.h:365-` | DG 4797 (Statistics) |
| History and exposure under views | View change resets TAA; value views hold the pre-exposure | DG 4797 (History and exposure) | |
| Editor/agent access | Viewport debug view chip; `viewport.capture`/`viewport.setSettings` `debugView` enum `lighting, ao, indirect, luminance, albedo, voxels, gi, open, probes` | `StrataEditor/src/Editor/EditorViewportCommands.cpp:147-151` | DG 4797, 4942 |
| White furnace (tests) | Uniform white environment: white metal and white dielectric must return 1 at every roughness and IOR | `GPU.SceneRenderer.Lighting` `StrataTests/src/Renderer/GPUSceneLightingTests.cpp:860-1010` | DG 4797 (Energy compensation) |
| White furnace (look-dev) | `Scenes/Furnace.stscene`, shot `lookdev.furnace` (Tonemapper None) | `Tools/LookDev/LookDevScene.json`, `Tools/LookDev/Shots.json:34` | DG 666, 4797 |
| Look-dev shots for this area | `lookdev.mirror` (SSR roughness), `lookdev.sheet`, `.sheet.angle`, `.wet`, `.wet.sunward`, `.patch` (probe bake without box projection), `lookdev.cornell`, `lookdev.cornell.view.gi`; scenes Mirror, Specular, Cornell | `Tools/LookDev/Shots.json:34, 74-80, 148-149` | DG 666 |
| Flicker meter | `Tests::MeasureFlicker`: 32 px block changes in camera strafes (Gate W bounds) | `StrataTests/src/Renderer/GPUSceneIndirectFlickerTests.cpp:143-269`; `ReflectionMetrics.h` (`Pattern3/4`, noise) | DG 4942, 5843 |

### 1.10 Frame placement (pass order of this area)

`SceneRenderer::RenderFrame` (`R/SceneRenderer.cpp:2901`): `PrepareGlobalIllumination` 3205 and `GatherReflectionProbes` 3207
on the CPU; prepass (with the surface target when SSR traces); screen shadows; `GPU.AO` 3453-3459; `GPU.RadianceCascades`
3460-3478; `GPU.Reflections` 3479-3488 (probe conversions, then the SSR trace); `GPU.Opaque` (forward pass reads AO SRV 11,
probes SRV 9/10, SSR SRV 18, GI b3/SRV 35-40/54); sky; scene-color copies (`GPU.Transparent`); post; lighting-view overlays
3712.

### 1.11 How completeness was checked

- Every file in `R/` whose name touches the area was accounted for: `AmbientOcclusionFit.h`, `SceneRendererAmbientOcclusion.cpp`,
  `SceneRendererReflectionProbes.cpp`, `SceneRendererScreenReflections.cpp`, `SceneRendererGlobalIllumination.{h,cpp}`,
  `GlobalIlluminationLayout.{h,cpp}`, `VoxelClipmap.{h,cpp}`, `SceneRendererLightingView.cpp`, `SkyPresets.h`, plus the
  shared `RendererComponents.h`, `RendererQuality.{h,cpp}`, `SceneRenderData.h`, `SceneRenderer.{h,cpp}`, `MaterialData.cpp`.
- Every shader entry registered in `Strata/CMakeLists.txt:106-135, 166, 183-198` of folders `IBL/` (non-atmosphere),
  `Effects/` (GTAO, AODenoise, SSR x2, ReflectionResolve, SceneColorCopy, LightingViewStats), `GI/` (all 12) and
  `Overlay/LightingView.frag` is listed; includes `AmbientOcclusionFit, IBL, IndirectLight, PBR, ReflectionProbes,
  ScreenReflections, SphericalHarmonics, GIField, GIMarch, GIProbes, GlobalIllumination, Voxelize, LightingView` listed.
- Components/fields: `SkyLightComponent` (all fields), `ReflectionProbeComponent` (all), `PostProcessComponent`'s AO, GI and
  SSR fields. Quality rows: `AmbientOcclusionQuality`, `EnvironmentResolution`, `Reflections`, `ReflectionProbeResolution`,
  `GlobalIllumination` (`RendererQuality.cpp:167-172` rows table). Commands: `lighting.bakeProbes`, `lighting.applySkyPreset`,
  `lighting.extractSun`, `viewport.capture`/`setSettings` `debugView`. Asset types: none new (captures are ordinary HDR
  textures). Script host functions: none in this area (scripts only toggle entities/components).
- Test suites listed in section 6 were matched against DG's test names for each section.
- Not exhaustive: every `SceneRendererStats` field of the area (named from the DG only), and the editor's Inspector UI for
  probes (Bake button) and Graphics Quality rows (UI code not read).

---

## 2. Concepts to teach (dependency order)

1. **What "indirect light" is.** Direct light arrives from a light source in one step; indirect light has bounced off
   something (the sky is a special case: light scattered by air, treated as a distant emitter). The rendering equation as
   the definition; why real-time engines split it: direct lights analytically, everything else approximated.
   *Engines:* split into ambient diffuse and ambient specular, each from a cheap proxy. *Strata:* the same split, made
   explicit in two gathers (`IndirectLight.slang`). *Newcomer error:* thinking ambient light is "a constant to brighten
   shadows" (Strata's constant `AmbientColor` exists only as the last fallback).

2. **Radiance, irradiance, solid angle, cosine weighting; luminance in nits.** Needed for every formula here (irradiance
   over pi, "radiance scale"). Strata uses physical units on one scale (DG 5297, other area). *Error:* mixing nits and lux,
   forgetting the 1/pi of Lambert.

3. **Microfacet BRDF recap (GGX, Smith, Fresnel, F0, roughness vs alpha).** Prerequisite from the direct-lighting chapter
   (other area), but the indirect chapters need F0, `alpha = roughness^2`, and the lobe. *Strata:* glTF metal-roughness;
   `c_MinRoughness` 0.045. *Error:* using perceptual roughness where alpha is meant.

4. **Environment maps and cube maps.** Equirectangular vs cube; face conventions (`CubeTexelDirection`, IBL.slang:10-24);
   texel solid angle. *Error:* face orientation mistakes; sampling the pole of an equirect (`atan2(0,0)` guarded at
   IBL.slang:30-33).

5. **Image-based lighting: diffuse irradiance.** Convolving the environment with a cosine lobe; storing it as a small cube
   (sky: 32/face) or as 9 spherical-harmonic coefficients (probes). *Engines:* irradiance cubes, SH (Ramamoorthi-Hanrahan
   band factors pi, 2pi/3, pi/4), ambient cubes (Valve). *Strata:* cube for the sky, SH-9 for probes, an ambient cube for the
   GI field. *Error:* forgetting the band factors, or that SH ringing can go negative (clamped at ReflectionProbes.slang:50).

6. **Image-based lighting: specular and the split-sum approximation (Karis 2013).** Prefiltered radiance per roughness mip
   (assume N = V = R) times a 2D BRDF table of scale and bias of F0. Importance sampling GGX; filtered importance sampling to
   kill noise. *Strata:* 6 levels (roughness 0..1 step 0.2), mip from `roughness * EnvironmentParams.z`; resolution by quality.
   *Error:* assuming the split sum is exact (it fails at grazing angles; the N=V=R assumption removes stretched reflections).

7. **Energy conservation and the white furnace test.** A white surface under a uniform white sky must reflect 1. Single
   scattering GGX loses energy at high roughness; multiple-scattering compensation (Kulla-Conty / Fdez-Aguera style
   `1 + F0(1/E - 1)`). Diffuse gets `1 - specular`. *Strata:* compensation everywhere image and direct specular appear; the
   furnace is a test and a look-dev shot. *Error:* "fixing" dark rough metals by brightening albedo; adding diffuse and
   specular without the `1 - F` split.

8. **Specular aliasing and geometric specular AA (Kaplanyan/Tokuyoshi).** Normals varying under a pixel; widening roughness
   by derivative variance; the derivative rule (only primitive-local interpolants, uniform control flow). *Error:* taking
   derivatives after `discard` or of values from other primitives, which breaks quad uniformity and the two draw paths.

9. **Ambient occlusion.** What occlusion of ambient light means; visibility vs obscurance; screen-space methods (Crytek
   SSAO, HBAO, GTAO by Jimenez et al. 2016), baked AO maps, ray-traced AO. *Strata:* GTAO from the prepass, material AO maps
   multiplied, applied to indirect light only. *Errors:* applying AO to direct light (shadows already do that), applying it to
   specular unchanged, dark halos from thin occluders, radius in pixels vs metres.

10. **Noise, patterns and denoising without history.** Why AO is computed with few samples per pixel; temporal accumulation
    (TAA-dependent) vs spatial resolve of a fixed interleaved pattern. *Strata:* a 4x4 ordered-dither pattern whose 16
    phases a separable 5x5 tent kernel weighs exactly once, so one frame is complete; bilateral weights (depth, normal).
    Wave 7's rule: nothing that needs TAA to look right. *Error:* using frame-varying noise and expecting TAA to clean it
    (it then ghosts and differs between AA modes).

11. **Multi-bounce AO.** Occluded light is not lost: occluders reflect it. Jimenez's polynomial vs Strata's rational fit to
    2D radiosity (`Tools/FitAOMultiBounce.py`). *Error:* believing AO darkens white corners as much as black ones.

12. **Specular occlusion.** Deriving specular visibility from AO (Lagarde 2014), horizon fade for normal maps. *Error:*
    leaving reflections of the sky inside a crevice; occluding what SSR actually saw (fixed in 0.8.0).

13. **Local reflections: reflection probes.** Parallax problem of a distant-environment assumption; box projection
    (Lagarde/Zanuttini 2012 "parallax-corrected cubemaps"); blending overlapping probes; baking; probe priorities; memory
    via cube arrays. *Strata:* baked in the editor only, at most 16 per view, two blended per pixel, LRU slot cache, captures
    stored as equirect HDR textures and converted on the GPU at run time. *Errors:* baking the sun disk or highlights into a
    probe (double-counting direct light, seen from the wrong place); a box that does not match the room; expecting probes to
    update at run time.

14. **Screen-space ray marching.** Rays as straight lines in (UV, depth) under perspective (depth linear in screen space in
    post-projection z); stepping, bisection refinement, thickness heuristics, hierarchical-Z tracing (and why Strata
    rejected it for grazing floors), confidence and fades, reusing the previous frame's color along motion vectors.
    *Strata:* two modes (Checkerboard + TAA; Spatial without history, validated crossings, 5x5 ratio-estimator resolve).
    *Errors:* fading all hits near every edge; accepting any point behind a surface as a hit (ghosts of thin posts);
    reflecting back faces; using SSR on rough surfaces.

15. **Fallback hierarchy.** SSR -> probes -> sky -> constant ambient, and why each layer replaces the next by a weight
    (premultiplied alpha, no black edges). *Error:* mixing un-premultiplied colors, giving black fringes.

16. **Global illumination: the problem and families.** Baked lightmaps, irradiance volumes/probes (DDGI), voxel cone tracing
    (VXGI/SVOGI), screen-space GI, signed-distance-field and hardware ray tracing (Lumen), radiance cascades (Sannikov / Path of
    Exile 2). Trade-offs: dynamic vs baked, temporal accumulation vs per-frame determinism, memory, thin walls. *Strata:*
    world-space radiance cascades over a voxel clipmap, no screen input and no history (owner decision 2026-11-03: no SSGI);
    experimental. *Error:* expecting GI to be "free bounce light"; ignoring leaks through thin walls.

17. **Voxelization and clipmaps.** Conservative triangle-box overlap (Akenine-Moller), atomics, solid fill by winding,
    two-sided voxels, clipmap levels, toroidal addressing and scrolling, anchors for camera-independent bits, budgets per
    frame. *Error:* recomputing the whole volume when the camera moves; floating-point origins far from zero (anchors).

18. **Radiance cascades.** The penumbra condition: near a probe angular resolution can be low and spatial resolution high,
    far away the opposite; cascades with 4x directions and 4x interval length; merging a child's unabsorbed ray into its
    parents' merged ray; only the top cascade sees the sky. *Error:* light leaking or doubling at interval borders (the
    lead-in and overlap rules exist for this).

19. **Probe fields and their visibility.** Trilinear probe interpolation, dead probes, probe relocation, Chebyshev depth-moment
    visibility (DDGI) and why Strata replaced it as the weighting by a voxel-transmittance guard (fence crawl), normal and view
    bias. *Error:* renormalizing a vanishing weight (stepping at cell borders).

20. **Multi-bounce by re-injection and convergence.** Feeding last frame's field back into the voxels; geometric series of
    albedo; settle frames; why deterministic (still frames bit-identical) without temporal blending. *Error:* thinking
    "uses last frame" equals "temporal accumulation".

21. **Measuring light: debug views, EV100, sun-to-sky ratio, albedo ranges.** Checking lighting by numbers. *Error:* judging
    exposure-dependent images by eye; albedos outside 0.03-0.85.

22. **"Bit for bit when off".** A teaching point specific to Strata: every feature is free and invisible when off (dummy
    SRVs, form preserved), checked by tests. *Error:* adding a uniform branch that changes rounding of the default path.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know |
| --- | --- | --- | --- |
| 1 | `SH/IBL/BRDFLut.comp.slang:20-49` | The split-sum BRDF table: importance-sampled GGX, the `4 V NoL VoH / NoH` weight where D cancels, scale/bias of F0 | Concept 3, 6; Monte Carlo basics |
| 2 | `SH/IBL/Prefilter.comp.slang:22-59` | Prefiltered environment with N = V = R and filtered importance sampling (mip from sample solid angle) | Cube maps, GGX pdf |
| 3 | `SH/IBL/Irradiance.comp.slang:22-43` | Cosine-hemisphere convolution, same mip trick | Irradiance |
| 4 | `SH/IBL/ProbeIrradiance.comp.slang:42-87` + `SH/Include/SphericalHarmonics.slang:1-19` | SH-9 projection of a cube with texel solid angles, group-shared reduction, band factors | SH basics; compute groups |
| 5 | `SH/Include/PBR.slang:59-71` | Multiple-scattering energy compensation in four lines | Concept 7 |
| 6 | `StrataTests/src/Renderer/GPUSceneLightingTests.cpp:860-914` | The white furnace as a test: what "energy conservation" means numerically, copper's expected value from the formula | Concept 7, doctest |
| 7 | `SH/Include/PBR.slang:73-102` | Specular AA (`WidenRoughness`) and the horizon fade | Derivatives in shaders |
| 8 | `SH/Include/IndirectLight.slang:1-131` (whole) | The seam: one struct, two gathers, four forms, compose; how features add without changing the default image | Concepts 5-6, 12, 15 |
| 9 | `SH/Scene/Forward.frag.slang:118-171` | Filling the inputs: split-sum reflectance, probe evaluation, SSR sample, sky reads, Lagarde's specular occlusion | #8 |
| 10 | `SH/Scene/Forward.frag.slang:280-338` | Where AO, multi-bounce, the GI join and the clear coat meet in `ShadeLitSurface` | #8, #9 |
| 11 | `SH/Effects/GTAO.comp.slang:41-141` | GTAO: slices, horizons, cosine-weighted arc integral, radius clamp, thin-occluder relaxation, fixed pattern | Concept 9; view-space reconstruction |
| 12 | `SH/Effects/AODenoise.comp.slang:1-90` (header + `ResolveAlong`) | History-free resolve: tent weights that weigh each phase once, bilateral depth/normal weights, separable passes in group-shared memory | Concept 10; compute shared memory |
| 13 | `SH/Include/AmbientOcclusionFit.slang:1-17` and `Tools/FitAOMultiBounce.py:1-45` (docstring) | A generated, fitted model, and why the planned polynomial was rejected | Concept 11 |
| 14 | `R/SceneRendererAmbientOcclusion.cpp:116-143` | CPU side of a compute effect: clamping user values, push constants, two dispatches | NVRHI basics |
| 15 | `SH/Include/ReflectionProbes.slang:54-125` | Box-local transform, blend weight, box projection ray-box exit, two-probe blending | Concept 13 |
| 16 | `R/SceneRendererReflectionProbes.cpp:58-66` and `193-260` | Ranking probes (priority, volume, entity) and gathering them per frame with validation of non-finite transforms | ECS views, frustum test |
| 17 | `R/SceneRendererReflectionProbes.cpp:451-506` | A capture's GPU conversion chain (equirect -> cube mips -> prefilter levels -> SH) reusing the sky's pipelines | #2, #4 |
| 18 | `StrataEditor/src/Editor/ProbeBake.h:19-47` | What a bake is: six 90-degree cameras, equirect assembly, power-of-two pre-exposure, staging folder lifetime | Concept 13; jobs |
| 19 | `SH/Include/ScreenReflections.slang:39-102` | A reflected ray clipped to the screen in (UV, depth) space; confidence (facing, exit-edge fade) | Projection matrices, reversed-Z |
| 20 | `SH/Effects/ScreenSpaceReflections.comp.slang:51-115` | The classic linear march + bisection + thickness, reading TAA history along motion vectors | #19 |
| 21 | `SH/Effects/ScreenSpaceReflectionsSpatial.comp.slang:151-274` | Validated crossings (central algorithm, long): candidates, bisection, validation, plane crossing, candidate budget | #20 |
| 22 | `SH/Effects/ReflectionResolve.comp.slang:75-120` | Ratio estimator under a GGX lobe weight, plane/normal weights | Concept 14, importance weights |
| 23 | `R/SceneRenderer.cpp:3453-3490` | The frame's order: AO, GI, reflections before the opaque pass, each in a GPU stage | Frame graph basics |
| 24 | `R/GlobalIlluminationLayout.cpp:147-192` | A GI layout from first principles: voxel levels, cascades (spacing x2, directions x4, intervals x4), field extent | Concepts 17-18 |
| 25 | `SH/Include/Voxelize.slang:160-196` | Akenine-Moller triangle-box overlap (separating axis theorem) | Vector math, SAT |
| 26 | `SH/Include/GIMarch.slang:21-76` | Front-to-back march with transmittance, runs, lead-in, depth moments (central algorithm) | Concept 18; volume rendering |
| 27 | `SH/GI/CascadeMarch.comp.slang:25-100` | The merge: unabsorbed light continues into eight parents' four directions; only the top reads the sky | #26 |
| 28 | `SH/Include/GIField.slang:41-51` and `181-236` | Ambient-cube read and the forward gather (trilinear x validity x facing x guard, min-visible normalization) | Concept 19 |
| 29 | `R/GlobalIlluminationLayout.cpp:405-412` | Settling a geometric series: frames until a bounce adds less than 0.25% | Concept 20 |
| 30 | `SH/Include/IndirectLight.slang:109-118` + `SH/Scene/Forward.frag.slang:301-321` | How the GI joins shading and stays bit-identical when off (`x * 1 + 0`) | #8 |

---

## 4. Figures

### Diagrams

1. **The indirect-light fallback stack**: per pixel, SSR (confidence a) over probes (weight w, two blended) over sky (1 - w)
   over constant ambient; diffuse vs specular columns; where AO / specular occlusion / multi-bounce multiply; where the GI
   field replaces diffuse. (Data flow.)
2. **Split sum**: the integral split into prefiltered radiance (cube mip chain by roughness) times the BRDF table (2D plot of
   scale and bias over NoV x roughness). (Illustrated equation + LUT image.)
3. **Environment filter chain**: source (map / procedural / atmosphere) -> cube mip 0 -> downsample mips -> irradiance cube
   and prefiltered levels; probes: equirect capture -> scratch cube -> slot's 6 levels + 9 SH coefficients. (Data flow.)
4. **Cube face conventions and equirect mapping** (IBL.slang). (Geometry.)
5. **Filtered importance sampling**: sample solid angle vs texel solid angle -> mip choice. (Geometry.)
6. **Energy loss of single-scattering GGX** vs roughness, and the compensation (chart: E(NoV, r) and the factor).
7. **GTAO slice**: a view-space slice, the two horizons h0/h1, the projected normal angle n, the cosine-weighted arc.
   (Geometry.)
8. **The 4x4 ordered-dither pattern and the 5x5 tent kernel**: why each of the 16 phases gets weight 1 (grid figure).
9. **Thin-occluder relaxation**: horizon over steps with and without relaxation behind a pole. (Plot.)
10. **Multi-bounce fit**: y(x) curves for several albedos vs the radiosity reference means. (Chart.)
11. **Box projection**: room, probe at center, surface point, reflected ray hitting the box face, lookup direction from the
    center. (Geometry.)
12. **Probe blending**: two overlapping boxes, blend-distance ramps, stronger over weaker. (Geometry.)
13. **Probe cache / slots**: cube array of 16 slots, LRU assignment, conversion budget 2/frame, resolution-change takeover.
    (State/timeline.)
14. **Probe bake timeline**: six face renders, readback, assembly on jobs, write on I/O job, import, one undo step, trash of
    previous capture. (Timeline / sequence.)
15. **Screen-space ray**: view-space ray projected to a 2D line in (UV, depth); cut at screen edge / far plane; steps denser
    near start; bisection. (Geometry.)
16. **Thickness and false hits**: ray passing behind a thin post (ghost in 0.7.0) vs validated crossing; plane-crossing case at
    a wall's top edge. (Geometry, two panels.)
17. **Checkerboard vs Spatial pipelines**: half-res 2x2 rotation + TAA history vs full-res trace + resolve + color copy.
    (Data flow, memory per pixel.)
18. **Back faces in mirrors (the crescent)**: why the screen cannot show an object's back. (Geometry.)
19. **SSR edge fade rule**: only near the exit edge the ray leaves through. (Screen diagram.)
20. **GI overview**: geometry pool -> CPU clipmap regions -> voxelization passes -> injection -> downsample -> validity ->
    weights -> cascade marches top-down -> field reduce -> forward gather; previous field feeding injection. (Data flow.)
21. **Voxel clipmap levels and toroidal scrolling**: nested windows (10/20/40/80 cm), a scroll writing only entered slabs,
    anchor cells. (Memory layout.)
22. **Voxel classes**: surface (lit layer), solid interior from winding fill, two-sided thin wall, alpha-masked partial.
    (Cross-section.)
23. **Radiance cascades**: probe grids per cascade (0.5/1/2/4 m), directions per probe (16..1024), intervals [0,s0],
    [s0,4s0]..., lead-in and overlap, merge to eight parents. (Geometry.)
24. **Field gather**: point, normal bias, view bias, eight probes, facing, guard segment through voxels, dead probe.
    (Geometry.)
25. **Re-injection over frames**: frame k uses field of frame k-1; light after k frames = first k terms; settle curve.
    (Timeline + series plot.)
26. **Lighting view statistics pipeline**: histogram pass -> ring of readbacks -> percentiles. (Data flow.)

### Screenshots (each with how it is isolated)

Use the look-dev harness (`python -I Tools/LookDev.py capture --build <bin>`, DG 666) where a shot exists; otherwise the editor
with `viewport.capture` and `debugView`.

1. Sky only lighting a white sphere and rough/smooth metal spheres: Basic3D template, sky light Procedural vs Environment Map
   vs Atmosphere (Inspector Sky section; `Source` field).
2. Prefiltered levels: a mirror ball at roughness 0, 0.2 ... 1 under an HDR map (`lookdev.furnace` style row with a map).
3. White furnace before/after energy compensation: `lookdev.furnace` (Tonemapper None); "before" needs an old build (0.6.0)
   or a mental figure; at minimum the 0.7.0+ row with readings.
4. Specular AA: a normal-mapped sphere at 4K with `SceneRendererSpecification::SpecularAntiAliasing` on/off (engine-side
   switch, a test or tool build).
5. Horizon fade: a strong normal map at grazing view, before (needs code toggle) / after.
6. IOR: water 1.33 vs default 1.5 vs 2.42 dielectric spheres (material IOR field).
7. AO on/off: ThirdPerson or Physics Playground, Post Process `AmbientOcclusion` toggle; plus debug view `ao`.
8. AO quality Low/Medium/High/Ultra: Graphics Quality rows (project setting `Renderer.Quality.AmbientOcclusionQuality`).
9. AO radius: 0.25, 1, 3 m (`AmbientOcclusionRadius`), near and far object to show the clamp.
10. Thin occluders: look-dev poles/fence/plate with AO view.
11. Multi-bounce: white plaster corner vs dark soil corner, `AmbientOcclusionMultiBounce` on/off, `ao` view vs lit.
12. Same AO image with TAA, FXAA, none (LookDev `--aa`).
13. Reflection probe on/off in a room: Showcase hut (`showcase.*` shot 3 has a "without the yard's probe" variant); toggle
    entity active.
14. Box projection on/off (`BoxProjection` field): `lookdev.patch` uses a probe without box projection.
15. Probe blend: two overlapping boxes with different captures, `BlendDistance` 0 vs 1 m.
16. Probe resolution 128 vs 256: mirror ball (Graphics Quality `ReflectionProbeResolution`).
17. Bake with sun disk (0.7.0 behaviour) vs without: `lookdev.patch` crop `patch` (needs old build for "before").
18. Repeated bakes adding bounces: bake 1, 2, 8 times (Showcase script bakes eight).
19. SSR off / Checkerboard+TAA / Spatial / SpatialHigh: `lookdev.mirror`, Graphics Quality `Reflections` row and Post Process
    `ScreenSpaceReflections`.
20. SSR max roughness: polished/satin/glossy crops of `lookdev.mirror`; `ScreenSpaceReflectionsMaxRoughness` 0.2 vs 0.5.
21. SSR edge fade: wet ground, `lookdev.wet.sunward` left/right crops.
22. SSR thin posts and wall edge: `lookdev.sheet` crop `post-wall`.
23. Crescent of a ball's back: `lookdev.sheet.angle` crop `crescents`.
24. Screen-door before the resolve (needs code toggle) vs after: `lookdev.sheet` rough sheet.
25. AO not darkening SSR: wet ground beside an object (`lookdev.wet` `edge`).
26. Sized sun highlight: Clear vs Overcast preset on a mirror sphere (Angular Diameter 0.53 vs 10).
27. GI off/on in the Cornell box: `lookdev.cornell` vs Post Process `GlobalIllumination` true; Graphics Quality High.
28. GI views: `lookdev.cornell.view.gi`; debug views `voxels`, `open`, `probes` in the sun room / Cornell (look-dev scene).
29. GI Low vs High (Graphics Quality `GlobalIllumination` row).
30. GI one bounce vs every bounce (needs `BounceGain` 0, engine-side; tests do this).
31. GI artefacts (honest "what it cannot do"): dark notches under the Cornell sphere, thin wall two-sided (voxels view in
    error color), the field's edge outdoors (yard).
32. Lighting debug views: Lighting, Indirect, Luminance (EV bands with legend), Albedo (marks) on the Showcase or ThirdPerson.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Indirect light must keep its energy** (DG 4797, AGENTS "Light keeps its energy"): check every shading change with the
   white furnace (tests and `lookdev.furnace`). Why: a lobe that loses light makes rough metals dull and tempts artists to
   paint wrong albedos.
2. **Diffuse gets what specular leaves** (`1 - SpecularColor` for image light, `1 - F` for direct): otherwise surfaces
   reflect more than they receive.
3. **The derivative rule** (DG 4797): derivatives only of the primitive's own interpolants and textures, in quad-uniform
   control flow, before `discard`. Why: both draw paths (CPU batches and GPU-driven) must give the same pixels, and a quad
   belongs to one primitive.
4. **IOR 1.5 stays the literal 0.04** (`MaterialData.cpp:51-59`). Why: the formula gives 0.040000003 and would change every
   default material's bits.
5. **A light's size widens only its highlight's D** (DG 4797, 5843). Why: masking belongs to the microsurface; diffuse,
   shadows, culling and shadow caches must not change (a radius change would otherwise redraw shadow views).
6. **AO darkens indirect light only**; direct light has shadows. Specular uses Lagarde's specular occlusion, not raw AO.
7. **No history for AO**: fixed 4x4 pattern, never the frame (DG 4907). Why: an image must be the same with TAA, FXAA or none,
   and two frames of a still view identical; frame noise would need TAA (wave 7 rule).
8. **AO radius clamped on screen** (0.3%-12% of height). Why: constant cost and look at every resolution; near surfaces do not
   reach across the screen.
9. **Change the multi-bounce fit only by running `Tools/FitAOMultiBounce.py --write`** (generated files: shader, C++ header,
   test reference). Why: three copies must agree; the tests compare against the script's reference.
10. **SSR light is visible light**: AO must not darken what a screen ray found (RN8 R1). Why: the ray already saw what blocks
    it; 0.7.0 drew dark smudges on wet ground.
11. **Fade only where rays leave the screen** (`GetHitConfidence`). Why: fading near every edge drew sky wedges.
12. **Keep only validated crossings** (Spatial). Why: "any point behind a surface" read thin posts as ghosts and broke wall
    edges.
13. **Hierarchical (Hi-Z) march rejected** for Spatial: grazing rays over floors ran out of iterations (stripes at 4K). A
    teaching point that the textbook algorithm is not always right.
14. **Never fill an object's back in a mirror** with its front's colors ("option F" tried and rejected). Why: front-lit rims.
15. **Checkerboard needs TAA**; it is Medium's exception to "nothing needs TAA" (it keeps 0.6.0's costs).
16. **Premultiplied SSR results**: a texel that found nothing adds no black at reflection edges.
17. **Probes are baked in the editor, never at run time**; a bake draws no sun disk and no lights' highlights (DG 5843). Why:
    direct light is already shaded with shadows; a highlight seen from the probe's center lands in the wrong place.
18. **Bake where the probe stands now** (`Scene::GetWorldTransform`, not the cached matrix). Why: a command of the same frame
    may have moved it.
19. **A bake replaces only its own earlier capture** and trashes it in the same undo step; never delete assets directly
    (editor rules: trash, undo, `DocumentSaver`).
20. **Captures are held whole until converted** and released after. Why: nothing draws a capture, so the streamer would never
    raise its levels; holding forever wastes memory.
21. **Conversions are spread (2 per frame)** in interactive renderers, not in bakes/captures. Why: frame time; and the
    conversion's cost follows each texel's sample chain, not the total.
22. **Features cost nothing when off** and the image stays bit for bit (dummy black cube array, black SSR texture, GI dummy
    SRVs; tests check). Why: the engine's rule that toggles are free and safe.
23. **GI traces world data only, never the screen** (AGENTS "Global illumination"; owner 2026-11-03). Why: screen-space GI
    needs temporal accumulation and misses what is off screen; determinism prevents flicker and smear.
24. **A frame without GI keeps the old expression bit for bit** (`ReflectionParams.y` 0). The join uses `x * 1 + 0` forms.
25. **GI constants live in their own buffer (b3), not `FrameConstants`**. Why: an unexplained effect where adding fields made
    recompiled GTAO/SSR repeat non-identically; new frame constants must check the `ao` view's repeats.
26. **Anchors for voxel coordinates**: the same scene voxelizes to the same bits wherever the camera is; worlds stay within
    20 km (floating point).
27. **Movers stay out of the voxels for 30 frames**; skinned meshes never enter. Why: no voxel work per frame for moving
    things and no popping of light.
28. **Walls must be thicker than two voxels** (20 cm High, 40 cm Low) or they turn two-sided and dark from both sides
    (ML 320).
29. **Captures and the project picture wait for GI to settle** (bounded waits). Why: bounces arrive one frame each.
30. **No blocking**: probe captures not loaded light nothing and are waited for by captures only; GI pending shows today's
    light.

---

## 6. Hands-on

### Game developers

| # | Exercise | Difficulty | Proves |
| --- | --- | --- | --- |
| G1 | Light a scene with each sky source (Procedural, HDR map with Extract Sun, Atmosphere); compare with the Lighting and Luminance views and read the sun-to-sky ratio | Easy | Sky as indirect light; measuring light |
| G2 | Apply the four sky presets and explain the ratio table (ML 279) | Easy | Physical lighting balance |
| G3 | Tune AO: radius, intensity, multi-bounce on white vs dark materials; compare `ao` view and lit image | Easy | What AO does and where it applies |
| G4 | Add a Reflection Probe to a room, fit its box, bake, toggle Box Projection, add a second probe with Priority and Blend Distance | Medium | Probes, parallax correction, blending |
| G5 | Bake repeatedly after a lighting change and observe bounces settle | Medium | Bakes as bounces |
| G6 | Times of day with baked probes: two probe sets switched by a script with `SetActive` and preloaded captures (`Assets::GetLoadProgress`) | Hard | Probe workflow in a game (ML 219, Showcase) |
| G7 | Make a wet floor: IOR 1.33, low roughness, SSR on, compare Graphics Quality Medium (TAA) vs High; find the crescent and off-screen limits | Medium | SSR's possibilities and limits |
| G8 | Build a small closed room with a window (walls >= 20 cm), turn GI on at High, use `gi`, `open`, `voxels`, `probes` views; make a wall too thin and see it go two-sided | Medium | What experimental GI can and cannot do |
| G9 | Albedo audit: fix materials the Albedo view marks | Easy | Plausible materials |
| G10 | Agent route: do G4 and G8 through `StrataCLI` (`lighting.bakeProbes`, `viewport.capture --debugView gi`) | Medium | Automation of lighting work |

### Engine developers

| # | Exercise | Difficulty | Proves |
| --- | --- | --- | --- |
| E1 | Write a CPU white furnace: integrate GGX + Smith over the hemisphere for F0 = 1, plot E(NoV, r), derive the compensation; compare with `BRDFLut.comp` | Medium | Split sum and energy compensation |
| E2 | Read and run `Renderer.AmbientOcclusion`; run `Tools/FitAOMultiBounce.py` (print only) and explain its errors table | Easy | Fitting a model to a reference |
| E3 | Add a new lighting debug view (e.g. specular occlusion as gray): `SceneLightingView`, `ST_LIGHTING_VIEW_*`, forward branch, overlay, editor enum, test in `GPU.SceneRenderer.LightingViews` | Hard | The whole path of a view and the "nothing when off" rule |
| E4 | Change GTAO's pattern to a frame-varying one in a scratch branch and observe `GPU.SceneRenderer.AmbientOcclusion` "no pattern without TAA" fail | Medium | Why the history-free design exists |
| E5 | Implement a probe-weight visualization (each probe's box weight as color) behind a view | Hard | Probe blending math |
| E6 | Box projection by hand: given a box and a ray, compute the lookup direction on paper, then check against `GetProbeLookup` | Easy | Parallax correction |
| E7 | Re-create the 0.7.0 SSR acceptance ("any point behind") in the Spatial trace and watch `GPU.SceneRenderer.SSR` "Thin posts..." fail | Medium | Validation of crossings |
| E8 | Write a CPU screen-space ray march over a synthetic depth buffer with bisection; reproduce the grazing-floor failure of a Hi-Z march | Hard | Screen-space tracing trade-offs |
| E9 | Compute `ComputeLayout` memory by hand for Low and check `Renderer.GlobalIlluminationLayout` "Memory adds up" | Easy | GI layout |
| E10 | Implement the CPU triangle-box test and voxelize a box; compare with `Tests::ReferenceVoxels` (`StrataTests/src/Renderer/GIScenes.h`) | Hard | Voxelization |
| E11 | 1D radiance cascades toy (Python/C++): two cascades, merge rule, compare with brute force | Hard | The cascade idea |
| E12 | Settle frames: derive `GetSettleFrames` for albedo 0.58 and 0.73 (12, 17) | Easy | Bounce series convergence |
| E13 | Add a field to `IndirectInputs` for a new term and keep the default image bit for bit (run `GPU.SceneRenderer.Lighting`, `.ReflectionProbes`) | Hard | The seam's contract |

---

## 7. Glossary

- **Indirect light**: light that reached a surface after bouncing (or from the sky), not straight from a light.
- **Image-based lighting (IBL)**: lighting from an image of the surroundings (environment map).
- **Environment map**: an HDR picture of all directions around a point; equirectangular (lat-long) or cube.
- **Equirectangular**: a 2:1 image mapping longitude to x and latitude to y.
- **Cube map**: six square faces covering all directions; **cube array**: many cube maps in one texture (Vulkan `imageCubeArray`).
- **Mip / mip chain**: successively halved copies of a texture.
- **Irradiance**: light power arriving per area from all directions (cosine-weighted).
- **Radiance**: light per area per solid angle along one direction; what a pixel sees.
- **Solid angle**: the 2D "angle" a region of directions covers, in steradians (4 pi for the sphere).
- **Nits / lux / EV100**: luminance (cd/m^2), illuminance, exposure value log2(nits)+3 as the views use it.
- **Lambert diffuse**: a surface scattering equally in all directions; radiance = albedo x irradiance / pi.
- **Albedo**: the share of light a surface reflects diffusely (base color).
- **F0**: reflectance at normal incidence; **IOR**: index of refraction, from which a dielectric's F0 follows.
- **Fresnel (Schlick)**: reflectance rising toward grazing angles.
- **GGX**: a microfacet normal distribution; **alpha**: roughness squared; **perceptual roughness**: the authored value.
- **Smith visibility (height-correlated)**: microfacet shadowing-masking term.
- **Split-sum approximation**: specular IBL as prefiltered radiance times a precomputed BRDF scale/bias.
- **BRDF lookup table (LUT)**: the 2D texture of that scale and bias over NoV and roughness.
- **Prefiltered environment**: the sky blurred by the GGX lobe, one mip per roughness.
- **Importance sampling / filtered importance sampling**: sampling where the lobe is large; reading blurrier mips for sparse samples.
- **Hammersley sequence**: a low-discrepancy point set used for sampling.
- **Spherical harmonics (SH, 9 coefficients, bands 0-2)**: a smooth basis on the sphere; stores low-frequency irradiance compactly.
- **Ambient cube**: six values per probe (one per axis direction) blended by the normal's squared components.
- **Energy compensation / multiple scattering**: restoring light single-scattering GGX loses at high roughness.
- **White furnace test**: render a white surface under a uniform white sky; it must look exactly white.
- **Specular aliasing / specular AA**: flickering highlights from sub-pixel normal changes; widening roughness to prevent it.
- **Horizon fade**: removing image light reflected below the geometric surface.
- **Ambient occlusion (AO)**: the share of ambient light a point receives given nearby geometry.
- **GTAO**: ground-truth AO, horizon-based integration in screen slices (Jimenez et al. 2016).
- **Slice / horizon angle**: a 2D plane through the view direction; the highest occluder angle on each side.
- **Bilateral filter**: a blur weighted by similarity (depth, normal) so edges stay sharp.
- **Ordered dither (4x4 Bayer order)**: a fixed pattern of 16 offsets that tiles the screen.
- **Tent kernel**: weights (0.5,1,1,1,0.5) that give a 4-periodic pattern uniform weight.
- **Multi-bounce AO**: correction that adds light reflected by occluders into a crevice.
- **Radiosity**: a method solving diffuse light exchange between patches (used offline to fit the AO model).
- **Specular occlusion (Lagarde)**: specular visibility estimated from AO, NoV and roughness.
- **Reflection probe**: a captured environment at a point that lights a region.
- **Capture / bake**: rendering a probe's surroundings into its texture (in the editor).
- **Influence box / extents / blend distance**: where a probe applies and how it fades out.
- **Box projection (parallax correction)**: intersecting the reflected ray with the box to look up the right direction.
- **Probe priority**: which probe wins in overlaps.
- **Probe cache / slot**: a renderer's cube-array entry holding a converted capture.
- **Pre-exposure**: scaling HDR values before storage so they fit half floats; divided out later.
- **HDR output / ProbeCapture**: render options used by the bake (no tone mapping; no sun disk, no light highlights).
- **Screen-space reflections (SSR)**: reflections found by marching rays through the depth buffer.
- **Depth buffer / reversed-Z**: per-pixel depth, here 1 near and 0 far.
- **Prepass / surface target**: a depth-only pass that also writes normals, roughness, metallic for SSR.
- **Octahedral encoding**: storing a unit vector in two numbers.
- **Ray march / step / bisection**: stepping along a ray; halving an interval to find a crossing.
- **Thickness tolerance**: how far behind a depth a ray may be and still count as hitting it.
- **Candidate / validated crossing**: a step that might be a hit; one that passed the validity checks.
- **Hi-Z (hierarchical depth) march**: tracing over a depth pyramid to skip empty space.
- **Confidence**: how much a reflection is trusted (0-1), used as alpha.
- **Premultiplied alpha**: color already multiplied by its alpha, so empty texels add nothing.
- **Interleaved gradient noise (IGN)**: a cheap per-pixel noise.
- **TAA history**: the previous frame's resolved image TAA blends with.
- **Motion vectors / velocity**: where each pixel was last frame.
- **Checkerboard / Spatial / SpatialHigh**: Strata's three SSR modes.
- **Ratio estimator**: a weighted average dividing weighted sums by weight sums.
- **Global illumination (GI)**: all indirect light, including bounces between surfaces.
- **Voxel / voxelization**: a 3D grid cell; converting triangles into occupied cells.
- **Clipmap**: nested grids around the camera, each twice the cell size of the one before.
- **Toroidal addressing**: storing world cells modulo the grid size so scrolling rewrites only new slabs.
- **Slab / region / brick / anchor**: pieces of a window queued for voxelization; aligned blocks; the origin voxel coordinates are relative to.
- **Triangle-box overlap (Akenine-Moller)**: separating-axis test for whether a triangle touches a box.
- **Winding / solid fill**: counting surface crossings along a column to find inside voxels of closed meshes.
- **Closed mesh**: every edge shared by exactly two faces in opposite directions.
- **Two-sided voxel**: a voxel holding both faces of a wall thinner than it; it gets no light.
- **RGB9E5**: a shared-exponent HDR color format in 32 bits.
- **Light injection**: lighting voxels directly by the sun and emission.
- **Probe / cascade / interval / direction tile**: points that gather light; levels with coarser spacing and more directions; the distance range each level traces; the octahedral grid of ray directions.
- **Radiance cascades**: a hierarchy of probes with growing intervals and angular resolution, merged top-down (Sannikov).
- **Merge / miss rule**: continuing a child's unabsorbed ray into its parents' rays; only the top reaches the sky.
- **Lead-in / overlap**: occlusion-only start of a march; marching a spacing past the interval's end.
- **Transmittance / occupancy**: how much light passes a sample; how full a voxel is.
- **Dead probe / validity / relocation**: a probe inside a solid; a 0-1 liveness; moving it to open space.
- **Irradiance field**: the cascade-0 probes' ambient cubes the forward pass reads.
- **Depth moments / Chebyshev test (DDGI)**: mean and variance of hit distances used for visibility.
- **Guard (voxel guard)**: Strata's visibility from probe to point through the voxels.
- **Normal bias / view bias**: moving the sample point off the surface toward its normal / the viewer.
- **Open share**: the share of the sky a surface sees (the `open` view).
- **Re-injection / multi-bounce / bounce gain**: adding last frame's field to the voxels' light to get further bounces.
- **Settled / pending**: GI's bounces converged; voxels of the window not ready yet.
- **Join**: replacing today's diffuse indirect light by the field's.
- **Look-dev**: fixed reference shots for judging image changes.
- **Flicker meter**: frame-to-frame change of 32 px blocks in a strafe.
- **Sun-to-sky ratio**: illuminance from the sun over that from the sky on flat ground.

---

## 8. Proposed chapters

1. **Light that bounced: the indirect-light problem** (concept, both, S). After it the reader can name the parts of indirect
   light, the fallback stack and the engine families of solutions. Prereqs: direct lighting and PBR basics, light units.
2. **Lighting from the sky: image-based lighting and the split sum** (internals, engine, L). Explain and modify the
   environment filter chain, BRDF LUT, irradiance; sky sources. Prereqs: ch 1, cube maps/textures, PBR, Monte Carlo basics.
3. **Keeping the light: energy, the white furnace and specular anti-aliasing** (internals, engine, M). Derive and test energy
   compensation, F0 from IOR, sized highlights, horizon fade. Prereqs: ch 2.
4. **Ambient occlusion without history** (internals, engine, L). Explain GTAO, the fixed pattern and denoiser, radius clamp,
   thin occluders, multi-bounce fit, specular occlusion. Prereqs: ch 1, depth prepass, compute shaders.
5. **Reflection probes: local reflections baked in the editor** (internals, both, L). Explain box projection, blending, the
   probe cache and conversions, the bake. Prereqs: ch 2; asset residency (other area); editor commands (other area).
6. **Using sky, AO and probes in your game** (tutorial, game, M). Set up a sky, tune AO, place and bake probes, times of day.
   Prereqs: editor basics, ch 1 (light reading only).
7. **Screen-space reflections** (internals, engine, XL). Explain screen-space rays, the Checkerboard and Spatial traces,
   validation, the resolve, fallbacks and limits. Prereqs: ch 2, 5; motion vectors and TAA (other area); prepass.
8. **Shiny worlds: a wet-floor tutorial** (tutorial, game, S). Make wet ground and polished metal with SSR, probes and IOR;
   read the limits. Prereqs: ch 6.
9. **Global illumination I: voxels of the world** (internals, engine, L). Explain the voxel clipmap, voxelization, fill,
   finalize, budgets and anchors. Prereqs: ch 1; geometry pool and render scene (other area); compute atomics.
10. **Global illumination II: radiance cascades and the field** (internals, engine, XL). Explain injection, cascades, merge,
    field reduce, the forward gather, multi-bounce and settling; what is experimental. Prereqs: ch 9, ch 4 (AO), ch 2.
11. **Trying global illumination in a scene** (tutorial, game, S). Turn GI on, use its views, avoid its pitfalls (thin walls,
    field edge). Prereqs: ch 6.
12. **Measuring light: debug views and statistics** (reference + tutorial, both, M). Use and extend the lighting views and
    stats, the look-dev harness and flicker meter. Prereqs: ch 1; exposure (other area).
13. **Reference: indirect-light settings** (reference, both, S). Every component field, quality row, command and debug view
    of the area with defaults and costs. Prereqs: none.

---

## 9. Not determined

- **Not read in full:** `R/VoxelClipmap.cpp` (825 lines), most of `R/SceneRendererGlobalIllumination.cpp` (read the header,
  pass order and function list), `SH/GI/VoxelTriangles`, `VoxelTiles`, `VoxelFill` (header only), `VoxelFinalize`,
  `VoxelDownsample`, `ProbeValidity` (header only), `ProbeWeights`, `FieldReduce` (header only), `VoxelView.frag`,
  `ProbeView.frag`, `Include/GIProbes.slang`, `Include/GlobalIllumination.slang` bodies, most of `Include/Voxelize.slang`;
  `R/SceneRendererScreenReflections.cpp` bodies; `R/SceneRendererLightingView.cpp` and `Effects/LightingViewStats.comp` bodies;
  `Overlay/LightingView.frag`; `IBL/ProceduralSky`, `EquirectToCube`, `CubeDownsample`; `Scene/DepthPrepass.frag` surface
  variant body; `StrataEditor/src/Editor/ProbeBake.cpp` and `EditorLightingCommands.cpp` bodies; the Inspector UI for probes
  and the Graphics Quality page.
- **Specs not read:** `Docs/Plans/Wave8/specs/reflections.md`, `radiance-cascades.md` (the superseded screen-space plan),
  and `radiance-cascades-world.md` beyond its goal (42-62) and D18 (896-917) and the headings; its "Review corrections"
  (1293-) override its body and were not read.
- **GI batches 2 and 3**: the task says they are still landing. Main has stages 1-4 plus the "smooth light between probes" and
  "light at contacts" work (RN8 241-270). I could not determine which of these the planner calls batch 1/2/3 or what the
  in-flight batches add (the `.worktrees` are off limits); the GI chapters must be written against main and revisited.
- **Exact line ranges of lambdas** in `GatherReflectionProbes` (`acquireSlot`, `hold`, `holdWhole`, `convert`) are approximate
  (~277-330); the function spans 193-430.
- **The cause of the FrameConstants/GTAO non-repeatability** is unexplained in the documents themselves (DG 4942).
- **GI stage time variance** (4.4 vs 6.5 ms in the same build) is unexplained (RN8 Known issues).
- **Whether screenshots of "before" states** (0.6.0/0.7.0 behaviour: no energy compensation, sun disk in bakes, ghost posts)
  can be produced without old builds: probably needs release binaries of 0.6.0/0.7.0.
- **SSR's component comment** (`RendererComponents.h:313-314`, "with TAA only") contradicts the Spatial modes; authors should
  follow DG 5843 and ML 229.
- Atmosphere's role in the environment (one prefilter level per frame, half-degree switching) belongs to the fog/atmosphere
  area and was not read here beyond DG 3955.
