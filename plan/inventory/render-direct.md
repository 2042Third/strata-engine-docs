# Inventory: materials and direct light (`render-direct`)

Surveyed at `main` 822a7a46 (2026-11-10). Scope: the material model, the BRDF and its energy compensation, light types,
light records and clustering, light units and exposure, sun shadows, local light shadows, the sky and the physical
atmosphere, height fog and aerial perspective, clear coat and glass, texture slots, the debug views that show these, and
what exists for area lights.

Paths: `R/` = `Strata/src/Strata/Renderer/`, `SH/` = `Strata/shaders/`, `T/` = `StrataTests/src/Renderer/`,
`DG` = `Docs/DeveloperGuide.md`, `ARCH` = `Docs/Architecture.md`, `ML` = `Docs/Manual/Lighting.md`,
`MG` = `Docs/Manual/Graphics.md`, `MC` = `Docs/Manual/Camera.md`, `RN8` = `Docs/Plans/Wave8/ReleaseNotes.md` (0.8.0 to be,
the parts already on main). Release numbers come from `Docs/Releases/0.x.0.md` and RN8; "0.8.0 (main)" means landed on main
in wave 8 but not yet released.

Boundaries with neighbouring areas (the planner must give these to other chapters, and this area must link to them):

- Image-based lighting's *filtering* chain (environment cube, irradiance, prefiltered mips, `FilterEnvironment`), the
  reflection probes, screen-space reflections and `Include/IndirectLight.slang`'s gathers belong to an indirect
  light/reflections area. This area owns the *sky sources* that feed that chain and the BRDF table the forward pass reads.
- Global illumination (radiance cascades, voxels, the `gi`, `open`, `voxels`, `probes` views) is another area.
- Exposure metering, tone curves, bloom and the rest of post-processing are the post-processing area; this area owns the
  *units* and the *pre-exposure* (why the HDR target can hold a real sun) and must hand over cleanly to "Exposure" there.
- The render scene, the GPU-driven path (`Cull.comp`), batching, camera-relative space, the shader conventions (Slang,
  registers, reversed-Z) are the render-architecture area; this area assumes them and points back.
- Texture import (sRGB vs data, BC5/BC7, `Grayscale`, Remove Sun) is the asset pipeline area; Extract Sun's editor
  command is listed here because it creates a light.

---

## 1. Features

### 1.1 Material model (`Material` asset, `.stmat`)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Metallic-roughness PBR material | glTF 2.0 model: `BaseColor` (linear RGBA), `Metallic`, `Roughness` (perceptual), `NormalScale`, `OcclusionStrength`, `UVTiling`/`UVOffset`, `DoubleSided`, `Unlit` | `R/Material.h:24-63` `MaterialProperties`; JSON `Material::Serialize/FromJson` (`R/Material.cpp`); `Material::GetPropertyInfos` reflection | DG "Materials" (editor commands) 3692; DG "Material texture slots" 6120 | 0.3.0 |
| Alpha modes | `MaterialAlphaMode::Opaque/Mask/Blend` with `AlphaCutoff`; Mask cuts in prepass, shadow pass (`SH/Scene/ShadowMask.frag`) and forward; Blend sorted back to front | `R/Material.h:16-21`; `MaterialGPU::GetFlags` `R/MaterialData.cpp:14-22`; `SH/Scene/Forward.frag.slang:451-462` | DG "Clear coat and glass" 6083 | 0.3.0 |
| Emission in nits | `EmissiveColor * EmissiveIntensity` times the emissive map is luminance (cd/m^2); a map still loading is black, not white | `R/Material.h:29-31`; `R/MaterialData.cpp:66,83` | DG "Light units and exposure" 5330; ML "Lights and their units" 8 | units 0.6.0 |
| Material is immutable once loaded | Edits publish a new object through `ReplaceLoadedAsset`; renderers learn from that | `R/Material.h:87-90` | DG "Materials" 3692; AGENTS.md Rendering | — |
| Nine texture maps | base color (sRGB), metallic-roughness (G rough, B metal), normal, occlusion (R), emission (sRGB), coat strength (R), coat roughness (G), coat normal, transmission (R) | `MaterialGPU::GetTextureMaps` `R/MaterialData.cpp:24-28`, `c_TextureMapCount` `R/MaterialData.h:30` | DG "Material texture slots" 6128 | coat/transmission maps 0.6.0 |
| GPU material record | `RenderData::MaterialData`, 144 bytes, mirrored by `SH/Include/Scene.slang`; flags `c_MaterialAlphaMask/AlphaBlend/Unlit/DoubleSided/Clearcoat(16)/Transmissive(32)` | `R/SceneRenderData.h:21-26, 218-248`; `MaterialGPU::Build` `R/MaterialData.cpp:61-95` | DG 6128 | 144 B since 0.6.0 |
| Neutral fallbacks | missing maps read white, flat normal or black; table entries 0-2 are white, black, flat normal | `R/TextureTable.h` (`c_White`, `c_Black`, `c_FlatNormal`); `R/MaterialData.cpp:79-92` | DG 6122 | — |
| Exact flat normal | the flat normal texture is (0.5, 0.5, 1) in half floats; 8-bit 128/255 tilted every surface 0.3 degrees in 0.7.0 | `Renderer::GetFlatNormalTexture` | DG 6122; RN8:92 | fix 0.8.0 (main) |
| Texture table indirection | material maps hold table indices; entries pack bindless slot (24 bits), sampler (7 bits), grayscale bit (`c_TextureSlotGrayscale`, bit 31); mip fade-in by `minLod` | `R/TextureTable.h`; `SH/Include/MaterialTextures.slang:16-43` | DG 6122 | — |
| Normal maps as XY | Z reconstructed from X and Y so BC5 and RGBA8 shade alike; back faces flip the frame | `GetMappedNormal` `SH/Include/MaterialTextures.slang:47-65`; `GetShadingNormal` 69-72 | DG 6122; AGENTS.md Rendering | — |
| IOR to F0 | dielectric F0 = ((n-1)/(n+1))^2, n clamped to [1, 3]; literal 0.04 at 1.5 (bit-exact with older scenes); stored in `MaterialData::Absorption.w` | `MaterialGPU::GetDielectricF0` `R/MaterialData.cpp:51-59`; `SH/Scene/Forward.frag.slang:215` | DG "Lighting" 4826; ML "Materials that keep their energy" 259 | 0.8.0 (main) |
| Clear coat | dielectric layer (IOR 1.5, F0 0.04) with its own roughness, strength and normal map; base keeps 1 - F | `MaterialProperties::Clearcoat*` `R/Material.h:47-53`; `EvaluateClearcoat` `SH/Include/PBR.slang:157-192`; `SH/Scene/Forward.frag.slang:96-101, 324-335, 409-415` | DG "Clear coat and glass" 6073 | 0.6.0 |
| Glass (transmission) | `Transmission`, `IOR`, `Thickness` (mesh units along the normal), `AttenuationColor`/`AttenuationDistance` (Beer's law); drawn first in the transparent pass, unblended, writes depth, ids and velocity | `R/Material.h:55-62`; `MaterialGPU::GetAbsorption` `R/MaterialData.cpp:40-49`; `TransmitLight` `SH/Scene/Forward.frag.slang:354-371`; `SceneRenderer::DrawBatches` glass branch `R/SceneRenderer.cpp:2699-2743` | DG 6083 | 0.6.0 |
| Scene-color copy | half-resolution, 6-level (B10G11R11 or RGBA16F) copy of the HDR image after the sky, read by glass at SRV 19 | `R/SceneRendererGlass.cpp`; `SH/Effects/SceneColorCopy.comp.slang` (+`SceneColorCopyFallback` variant) | DG 6091 | 0.6.0 |
| glTF material extensions | `KHR_materials_clearcoat`, `_transmission`, `_volume`, `_ior`, `KHR_lights_punctual`, emissive strength 1:1 | `GltfImporter` (asset area) | DG 6103, 5335 | 0.6.0 |
| Material editing commands | `material.create`, `material.set`, `material.get`; `AssetEdit` writes and publishes | `StrataEditor/src/Editor/AssetEdit*` | DG "Materials" 3692 | — |

### 1.2 Shading (BRDF and its corrections)

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Cook-Torrance GGX BRDF | GGX distribution, height-correlated Smith visibility, Schlick Fresnel, Lambert diffuse weighted by (1 - F)(1 - metallic) | `SH/Include/PBR.slang:33-57, 126-155` | DG "Scene renderer and lighting" 3955 | 0.3.0 |
| Minimum roughness | `c_MinRoughness` 0.045 keeps mirrors from aliasing and dividing by zero | `SH/Include/PBR.slang:10` | code comment | — |
| Split-sum BRDF table | (NoV, roughness) -> scale and bias of F0, same Smith visibility as direct light | `SH/IBL/BRDFLut.comp.slang:20-49`; SRV t5 `u_BRDFLut` | DG 3986 | 0.3.0 |
| Multiple-scattering energy compensation | specular times `1 + F0 (1/E - 1)` with E = dfg.x + dfg.y, applied to direct and image light, coat and glass | `GetSpecularEnergy` `SH/Include/PBR.slang:59-71`; used in `ShadeLitSurface` `SH/Scene/Forward.frag.slang:217-226` | DG "Lighting" 4799; ML 259 | 0.7.0 |
| Specular anti-aliasing | lobe widened by the variance of the shading normal over the pixel (`alpha^2 += min(2*0.25*(|dN/dx|^2+|dN/dy|^2), 0.18)`) | `WidenRoughness` `SH/Include/PBR.slang:73-91`; `SH/Scene/Forward.frag.slang:401-402, 414`; `SceneRendererSpecification::SpecularAntiAliasing` (`R/SceneRenderer.h:207`), `MaterialParams.z` | DG 4812; ML 259 | 0.7.0 |
| Highlights of sized sources | sun disk and bulb/flame radius widen only D, keeping it normalized: `sqrt(alpha^2 + sourceAlpha2)` | `GetSourceLobeAlpha2`, `GetLobeAlpha` `SH/Include/PBR.slang:12-31, 119-124`; `RenderData::GetSunLobeAlpha2` `R/SceneRenderData.h:114-128` | DG 4836; ML 8 | 0.8.0 (main) |
| Horizon fade | image light reflected below the geometric surface fades out: `clamp(1 + R.Ng/0.25, 0, 1)^2` | `GetHorizonFade` `SH/Include/PBR.slang:93-102`; `SH/Scene/Forward.frag.slang:162-164, 331-332` | DG 4862 | not dated (0.7.0 Manual mentions it) |
| Probe-capture mode | `MaterialParams.w` = 1 drops the lights' specular in reflection-probe captures | `LightSurface` `SH/Scene/Forward.frag.slang:84-103` | DG 3986 (probes in Reflections) | — |
| Forward shader variants | `Forward.frag`, `ForwardTransparent.frag`, four `ForwardGlass*` variants (entity ids, velocity) from one source with defines | `SH/Scene/Forward.frag.slang:18-29`; `Strata/CMakeLists.txt:174-178` | DG 3957 | glass 0.6.0 |
| Opaque forward with EQUAL depth test | opaque surfaces shaded after the prepass, `[earlydepthstencil]`, discard only by LOD fade | `SH/Scene/Forward.frag.slang:19-21, 31-33` | DG 3957 | — |
| Derivative rule | every derivative before the first discard; derivatives only of the primitive's interpolants and textures in quad-uniform control flow | `SH/Scene/Forward.frag.slang:380-383, 398-402` | DG 4549, 4812 | rule 0.7.0/0.8.0 |
| `SanitizeHDR` | NaN to 0, clamp to 65,000 before writing RGBA16F | `SH/Include/Common.slang:49-57` | DG 4544 | — |
| Mirrored instances | negative determinant: clockwise pipelines, tangent sign flipped | `c_InstanceMirrored` (render scene) | DG 4544 | — |

### 1.3 Light types and their data

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Directional light | `DirectionalLightComponent`: `Color`, `Intensity` (lux, default 3), `CastShadows`, `ShadowDistance` (80 m), `ShadowSoftness` (angular diameter, 0.53 degrees; Inspector "Angular Diameter"), `ShadowBias` (1 texel), `ShadowNormalBias` (1.5 texels), `CascadeBlend` (0.1, max 0.5), `ContactShadowLength` (0.3 m, max 2), `CascadeDistribution` (0.9) | `R/RendererComponents.h:21-46`; registration `R/RendererComponents.cpp:280-315` | DG 5324; ML 8, 115 | 0.3.0; blend 0.6.0; contact 0.7.0; distribution 0.8.0 (main) |
| One sun per frame | the brightest active directional light shines (shines along entity -Z); others ignored | `SceneRenderer::CollectLights` `R/SceneRenderer.cpp:2557-2601` | not stated in DG as a rule (code only) | — |
| Point light | `PointLightComponent`: `Color`, `Intensity` (candela, 10), `Range` (10 m), `SourceRadius` (0-2 m), `CastShadows` (off), `ShadowBias`, `ShadowNormalBias`, `ShadowFilterRadius` (1.5, max 8 texels) | `R/RendererComponents.h:50-63`; `R/RendererComponents.cpp:317-334` | DG 5326; ML 8 | 0.3.0; shadows 0.6.0; radius 0.8.0 (main) |
| Spot light | `SpotLightComponent`: as point plus `InnerConeAngle` (20) and `OuterConeAngle` (30) half angles; candela along the axis, not spread over the cone | `R/RendererComponents.h:66-78`; `R/RendererComponents.cpp:336-355` | DG 5326; ML 8 | 0.3.0 |
| Windowed inverse-square falloff | `window^2 / d^2`, window = clamp(1 - (d^2/r^2)^2) | `DistanceAttenuation` `SH/Include/PBR.slang:194-200` | DG 5326 | 0.3.0 |
| Smooth spot cone | `t^2` between cos(outer) and cos(inner) | `SpotAttenuation` `SH/Include/PBR.slang:202-207` | — | 0.3.0 |
| Light records (render scene) | one 96-byte `RenderData::LightRecord` per light component, kept from EnTT signals and transform changes, with a change log for the GPU mirror; inactive lights keep a record marked not drawn | `R/RenderLights.h:16-129`; `RenderLights::MakeRecord`, `GetSpotBounds` `R/RenderLights.cpp:44-85`; `R/SceneRenderData.h:264-279` | DG 4508; ARCH "Render scene" 2270 | 0.4.0 (commit 4ca26bfb) |
| Spot bounding sphere | smallest sphere around the cone's region (two cases around 45 degrees) | `RenderLights::GetSpotBounds` `R/RenderLights.cpp:44-54` | — | — |
| Drawn transforms | lights placed where the scene draws their entity (interpolated fixed-step motion) | `RenderLights::Sync` `R/RenderLights.cpp:276` | AGENTS.md "Drawn transforms"; DG Interpolation | 0.8.0 (main) commit 2b14f17d |
| Light uniform for shading | `RenderData::LightData`, 64 bytes, camera-relative; `SpotAngles.z` shadow slot + 1, `.w` source radius | `R/SceneRenderData.h:250-259`; `SH/Include/Scene.slang` t2 `u_Lights` | DG 4508 | — |
| Preview lighting | editor views of scenes with no light get a preview sun (55 degrees up) and the default procedural sky | `SceneRenderer::NeedsPreviewLighting`, `GetPreviewSunDirection` `R/SceneRenderer.cpp:175-212`; `SceneRenderOptions::PreviewEnvironment` | DG 4000 | — |

### 1.4 Many lights: culling and clustered shading

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| CPU light path | frustum-cull records by bounding sphere, rank by relevance (camera inside first, then projected size `r/(d-r)`), cap at `MaxLights` (4096), warn once | `SceneRenderer::CollectLights` `R/SceneRenderer.cpp:2635-2697`; `SceneRendererSpecification::MaxLights` `R/SceneRenderer.h:145` | DG 4508 | 0.3.0 |
| GPU light path | `LightCull.comp` tests every record against the camera-relative frustum, `LightCompact.comp` packs visible ones in record order, no cap | `SH/Scene/LightCull.comp.slang`, `SH/Scene/LightCompact.comp.slang`; `SH/Include/Lights.slang`; `m_GPULightsFrame` `R/SceneRenderer.cpp:2625-2633` | DG 4508; ARCH 2270 | 0.4.0 (commit 4ca26bfb, in tag v0.4.0) |
| Clustered assignment | 16x9x24 froxels (exponential depth slices), up to `MaxLightsPerCluster` (256) per cluster, one thread per cluster testing spheres against cluster AABBs via shared memory | `SH/Scene/LightClusters.comp.slang:42-193`; `SH/Include/Clusters.slang`; grid in `R/SceneRenderer.h:146-150`; slice constants `R/SceneRenderer.cpp:2612-2620` | DG 4508 | 0.3.0 |
| Relevance-preserving overflow | a full cluster on the GPU path finds by bisection over ordered float bits the relevance of its last kept light | `SH/Scene/LightClusters.comp.slang:103-189`; `GetLightRelevance` `SH/Include/Clusters.slang:67-78`; `SH/Include/OrderedFloat.slang` | DG 4508; ARCH 2270 | with the GPU light path (0.4.0) or later: not dated |
| Forward cluster loop | the pixel's cluster index from screen tile and log depth; per light range test, attenuation, local shadow, source lobe, `LightSurface` | `SH/Scene/Forward.frag.slang:249-279` | DG 4508 | 0.3.0 |
| Light statistics | `SceneRendererStats::CulledLights`, `DroppedLights`; `SceneRendererGPUStats::Lights`, `CulledLights`; `Tests::GetLightCounts` | `R/SceneRenderer.h:548, 767` | DG 4508 | — |

### 1.5 Light units, HDR and pre-exposure

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Photometric units on one scale | lux (sun), candela (point, spot), nits (sky, ambient, emission); no hidden factors; `Renderer.LightUnits` checks the tooltips name units | `R/RendererComponents.h:17-20`; `T/LightUnitsTests.cpp` | DG 5322-5338; ML 8 | 0.6.0 |
| Exposure model | tonemapper sees L * M; manual `M = 2^Exposure`; auto `M = 2^Exposure * 0.18 / 2^a * 2^k`; EV100 = log2(L) + 3; Exposure about 0.5 - EV100 | `PostProcessComponent` `R/RendererComponents.h:260-360`; `SH/PostProcess/Exposure.comp.slang`, `Histogram.comp.slang`, `SH/Include/Exposure.slang` | DG 5339-5352; ML "Exposure" 61; MC "Exposure" 13 | auto 0.3.0; MaxEV 16 0.6.0; key 0.7.0 |
| Pre-exposure | every HDR writer multiplies by a power of two P (`FrameConstants::TemporalParams.y`) so a 100,000 lux sun and a 1.3e9-nit disk fit in half floats; exact because a power of two | `SceneRenderer::ChoosePreExposure` `R/SceneRenderer.cpp:1531-1598`; `c_PreExposureHeadroomStops` (2), `c_MaxPreExposureStops` (24) `R/SceneRenderer.h:991-996`; writes `SH/Scene/Forward.frag.slang:463-465`, `SH/Scene/Skybox.frag.slang:50` | DG 5365-5388; ML 8 | 0.6.0 |
| Settled pre-exposure | captures and project pictures wait (at most 8 frames) for a readback drawn with the current P | `SceneRendererStats::PreExposureSettled` `R/SceneRenderer.h:698-699` | DG 5379 | 0.6.0 |
| Reference values table | sun, sky, overcast, office, moon, lamp, candle, monitor with exposures | — | DG 5353; ML 36-47 | 0.6.0 |
| Balanced default template | Basic 3D: Clear preset, 120,000 lux sun 40 degrees up at azimuth 20; sun/shade ratio at least 5 (`GPU.Editor.Lighting`) | `ProjectTemplates::GetBasic3DSunDirection` (editor) | DG 5299 | 0.7.0 |

### 1.6 Sun shadows

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Cascade map | one D32 array, a layer per cascade (1-5), made with the first shadowed sun, released at zero viewport | `SceneRenderer::EnsureShadowMap`, `ReleaseShadowMap` `R/SceneRenderer.cpp:1716-1897`; `c_MaxCascades` 5 `R/SceneRenderData.h:43` | DG 4521 | 0.3.0 |
| Stable cascade layout | splits by distance (fixed start 1.5 m, log/uniform blend by `CascadeDistribution`, first split at most 7.5 m), smallest sphere per slice (lens only), square covers sphere + 33-texel filter reach + 1 snapping texel, centered on whole texels of absolute light space in double | `R/ShadowCascades.h:13-108`, `R/ShadowCascades.cpp:14-141`; `SceneRenderer::LayOutShadowCascades`, `FindShadowCasters` `R/SceneRendererExtraction.cpp:388-612` | DG "Sun shadows" 4642-4701; ML 115; RN8:278-296 | 0.8.0 (main); 0.7.0 fitted to receivers by readback, 0.6.0 fixed spheres |
| Fifth (near) cascade | High and Ultra: a cascade from the near clip to 1.5 m, its sphere at most 2 m (`c_MaxNearRadius`, `GetRadiusLimit` by bisection) | `R/ShadowCascades.cpp:23-71` | DG 4649-4661; MG 16-17 | 0.8.0 (main) |
| Depth fit on the GPU | `CascadeFit.comp` sets each cascade's depth range from its sphere's far side to the nearest caster (at most `c_MaxShadowCasterDistance` 100 km beyond); both paths | `SH/Scene/CascadeFit.comp.slang`; `RenderData::CascadeFitConstants` `R/SceneRenderData.h:145-158`; `SceneRenderer::FitCascades` `R/SceneRendererExtraction.cpp:1256` | DG 4526 | 0.4.0 |
| Pancaking | casters between the light and the near plane flattened onto it instead of clipped | `SH/Scene/ShadowMesh.vert.slang:46-51` | DG 4526 | — |
| Sub-texel casters dropped | casters whose light-space extent is under 1 texel of a cascade are not drawn into it (`c_MinCasterTexels`), counted per cascade | `SceneRenderer::GetCascadeMask` `R/SceneRendererExtraction.cpp:614-634`; `SceneRendererStats::SubTexelCasters` | DG 4526 | 0.7.0 |
| Deterministic caster search | one job per cascade, parallel chunks merged in chunk order | `FindShadowCasters` | DG 4526; ARCH 2209 table | 0.4.0+ |
| Containment-based selection | the first cascade whose split lies beyond the depth *and* whose square holds the position 33 texels inside | `SelectShadowCascade`, `ShadowCascadeHolds` `SH/Include/Shadows.slang:45-74` | DG 4677 | 0.8.0 (main) |
| Cascade blend | last `CascadeBlend` of each slice mixes into the next cascade (last one fades out to the shadow distance); next slice starts at the band | `CascadeBlendWeight` `SH/Include/Shadows.slang:76-92`; `EvaluateDirectionalShadow` 262-282; `GetLayout` `R/ShadowCascades.cpp:104-129` | DG 4535 | 0.6.0 |
| Cascade cache | layers redrawn only when camera, light, boxes or a caster in them change; still camera keeps layers | `PrepareShadowCache`; `SceneRenderer::InvalidateShadowCache` `R/SceneRenderer.cpp:2006` | DG 4696; `GPU.SceneRenderer.Shadows` "Cascades are kept..." | 0.4.0 |
| Biases | rasterizer slope bias, 1-texel depth bias, 1.5-texel normal offset (texel-relative), receiver plane depth bias from the inverse-transpose of the light projection | `SampleCascadeShadow` `SH/Include/Shadows.slang:148-167`; `ReceiverDepthGradient` 94-111 | DG 4590 | 0.3.0; receiver plane 0.7.0 |
| Physical PCSS filter | penumbra half-width `s tan(a)` from the blockers' mean separation, classified lit/umbra exactly from depth ranges, fixed 4-tap tent below a texel, Vogel disk of 8/16/24/32 taps above 1-2 texels, turned by a fixed 64x64 blue-noise tile; nothing changes per frame | `SampleCascadeShadow` `SH/Include/Shadows.slang:143-260`; `SH/Include/BlueNoise.slang`; `R/BlueNoise.h`; `Tools/GenerateBlueNoise.py` | DG "Sun shadows" 4558 | PCSS 0.3.0; physical width, ranges, fixed noise 0.7.0; search distance per receiver 0.8.0 (main) |
| Shadow depth ranges | R32_UINT pyramid (cells of 4, 8, 16 texels) of (nearest, farthest) rounded outward; built right after the layers | `SH/Scene/ShadowRanges.comp.slang` (+`ShadowRangesDownsample` variant); `SceneRenderer::CreateShadowRanges`, `BuildShadowRanges` `R/SceneRenderer.cpp:1778-1855`; SRV 32 | DG 4582 | 0.7.0 |
| Screen-space shadow mask | after the prepass, `ScreenShadows.frag` evaluates the filter per opaque pixel into RG8 (sqrt visibility, blur radius), `ScreenShadowsBlur.frag` blurs H then V with plane-distance and normal weights; forward reads SRV 28 | `R/SceneRendererScreenShadows.cpp:25-244`; `SH/Effects/ScreenShadows.frag.slang`, `ScreenShadowsBlur.frag.slang`; GPU stage `GPU.ScreenShadows` | DG 4594 | 0.7.0 |
| Stair-step blur | where the tent leaves a partly lit edge on a grazed receiver whose stretched texel covers more than 1.5 pixels, blur by its footprint (at most 4 px) | `ReceiverTexelPixels` `SH/Effects/ScreenShadows.frag.slang:32-51, 81-89` | DG 4594 | 0.8.0 (main) |
| Contact shadows | screen-space march toward the sun over the prepass depth, own-face test, thickness `0.02 + 0.005 d`; Custom quality only (0 steps in every preset since 0.8.0) | `SH/Effects/ContactShadows.frag.slang`; `RendererQualitySettings::ContactShadows`; `DirectionalLightComponent::ContactShadowLength` | DG 4614; ML 115 | 0.7.0 (High/Ultra), off in presets 0.8.0 (main) |
| Transparent receivers | transparent and glass variants call `SampleDirectionalShadow` per pixel (no blur, no contact) | `SH/Scene/Forward.frag.slang:233-242`; `SH/Include/Shadows.slang:284-288` | DG 4719 | — |
| Alpha-masked casters | cut-out texels discarded in the shadow pass | `SH/Scene/ShadowMask.frag.slang` | `GPU.SceneRenderer.Shadows` "Alpha-masked surfaces..." | — |
| Cascade statistics | each slice's near, far, texel size in `SceneRendererStats::Cascades`; `renderStats.cascades` in `editor.perf` and `viewport.capture` | `FindShadowCasters` `R/SceneRendererExtraction.cpp:463-466` | DG 4696 | 0.7.0 |

### 1.7 Shadows of point and spot lights

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Shadow atlas | one D32 atlas (`LocalShadowAtlasSize` 2048/4096/4096/8192), tiles of 128 to `LocalShadowMaxTile` texels | `R/SceneRendererLocalShadows.cpp:793-840` `EnsureLocalShadowAtlas`; SRV 8 | DG "Local light shadows" 4750 | 0.6.0 |
| Quadtree tile allocator | power-of-two tiles in Morton order, merge on free, deterministic | `R/ShadowAtlasAllocator.h:21-81`, `.cpp` | DG 4750; `T/ShadowAtlasAllocatorTests.cpp` | 0.6.0 |
| Tile fitting by relevance | wanted size from the range's size on screen (hysteresis 1.25/0.4), halved in rounds from the least relevant | `ShadowAtlasAllocator::FitTileSizes`; constants `R/SceneRendererLocalShadows.cpp:37-47` | DG 4750 | 0.6.0 |
| Spot = 1 view, point = 6 cube faces | spot views capped at 80 degrees half angle; faces +X,-X,+Y,-Y,+Z,-Z picked by major axis | `c_MaxSpotShadowHalfAngle` `R/SceneRendererLocalShadows.cpp:48-50`; `SelectLocalShadowView` `SH/Include/LocalShadows.slang:43-56` | DG 4750 | 0.6.0 |
| Guard band | each view widened by `ceil(filter + 1.42 normalBias) + 1` texels so taps never leave the face | `c_NormalBiasReach` `R/SceneRendererLocalShadows.cpp:55-58` | DG 4750 | 0.6.0 |
| View cache keyed in world space | `LocalShadowViewKey` (position, direction, range, near, angle, tile) plus `LocalShadowContent` versions; matrices rebuilt camera-relative in double; casters' bounds followed (up to 65,536) | `R/SceneRenderer.h:1249-1321`; `GetLocalShadowViewProjection` `R/SceneRendererLocalShadows.cpp:130` | DG 4763 | 0.6.0 |
| Redraw budget and fade | at most `LocalShadowViewsPerFrame` (12) views a frame, nearest first; a light shadows once all views hold content and fades in over `c_LocalShadowFadeFrames` (8); rank fade | `SceneRendererSpecification::SpreadLightingUpdates`, `CacheLocalShadows` `R/SceneRenderer.h:260-271, 955` | DG 4772 | 0.6.0 |
| Sampling | 16 Poisson taps clamped inside the tile, rotated per pixel by interleaved gradient noise that also turns with the TAA frame; depth bias toward the light, normal bias off the surface, in texels at the surface's depth | `SampleLocalShadow`, `LocalShadowSampleRotation` `SH/Include/LocalShadows.slang:32-97` | DG 4782 | 0.6.0 |
| Shadow data per slot | `RenderData::LocalShadowData` (six matrices, tiles, biases, strength, light) at scene SRV 13; `c_MaxShadowedLocalLights` 16 | `R/SceneRenderData.h:281-302` | DG 4782 | 0.6.0 |
| Local shadow vertex shaders | `LocalShadowMesh(.vert/Skinned)` variants of `ShadowMesh.vert` with `ST_LOCAL_SHADOW` | `Strata/CMakeLists.txt:189-191` | DG 4782 | 0.6.0 |

### 1.8 Sky

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Sky light component | `SkyLightComponent`: `Source` (EnvironmentMap, Procedural, Atmosphere), `Intensity`, `Rotation`, `ShowBackground`, `BackgroundBlur`, `AmbientColor` (nits), procedural colors, `SunSize`, `SunIntensity`, atmosphere `AtmosphereDensity`, `AtmosphereHaze`, `GroundAlbedo`, `AerialPerspective`, `AerialPerspectiveScale` (0-64); inactive reasons per source | `R/RendererComponents.h:80-124`; `R/RendererComponents.cpp:30-90, 357-403` | DG 3986; ML "The sky" 72 | 0.3.0; atmosphere 0.6.0; aerial 0.7.0 |
| Environment map source | equirectangular HDR texture into a 512 cube, then the shared filter chain (irradiance 32, prefiltered 256/512 with 6 levels) | `SceneRenderer::ProcessEnvironment`, `FilterEnvironment` `R/SceneRenderer.cpp:767-898`; `SH/IBL/EquirectToCube.comp.slang` | DG 3986 | 0.3.0 |
| Procedural sky | zenith/horizon/ground gradient in nits and the sun's disk where the sun is; recomputed only when parameters change exactly | `SH/IBL/ProceduralSky.comp.slang`; `SceneRenderer::GenerateProceduralSky`, `GetProceduralSkyParameters` `R/SceneRenderer.cpp:827-916`; `RenderData::ProceduralSkyParameters` `R/SceneRenderData.h:381-394` | DG 3986, 5299 | 0.3.0; colors x0.25 0.7.0 |
| Physical atmosphere | Earth's (Rayleigh, Mie, ozone; ground at y = 0, radii 6360/6460 km); tables: transmittance 256x64, multiple scattering 32x32, sky view 192x108 | `R/Atmosphere.h:15-76`, `R/Atmosphere.cpp`; `SH/Include/Atmosphere.slang`, `AtmospherePass.slang`; `SH/IBL/Atmosphere{Transmittance,MultipleScattering,SkyView,Cube,Aerial}.comp.slang`; `R/SceneRendererAtmosphere.cpp:48-474` | DG "Fog and atmosphere" 5775-5823 | 0.6.0 |
| Sun color through the air | CPU computes the transmittance toward the sun in double, fades by the disk's share above the horizon, multiplies the directional light | `Atmosphere::ComputeSunTransmittance` `R/Atmosphere.cpp:90-101` | DG 5803 | 0.6.0 |
| Storage scale | tables of light per lux stored times 2^14 so twilight stays out of half-float subnormals; readers multiply by `EnvironmentParams.x` | `Atmosphere::c_StorageScale` `R/Atmosphere.h:43-48`; `ST_ATMOSPHERE_STORAGE_SCALE` | DG 5788; RN8:128 | 0.8.0 (main) |
| Atmosphere environment refresh | double-buffered maps recomputed in 14 steps once the sun moved 0.5 degrees; first and sun-on/off at once | `SceneRenderer::UpdateAtmosphere` `R/SceneRendererAtmosphere.cpp:195-360` | DG 5808 | 0.6.0 |
| Atmosphere background | sky-view table times intensity plus the analytic sun disk (illuminance over solid angle, pixel-smoothed edge) | `SH/Scene/Skybox.frag.slang:20-34` (`SkyboxAtmosphere` variant) | DG 5799 | 0.6.0 |
| Sun and sky presets | Clear, Hazy, Overcast, GoldenHour: sky + sun values, one undo step; turn on auto exposure, MaxEV to 16; return `groundIlluminance` | `R/SkyPresets.h:14-53`, `R/SkyPresets.cpp`; `lighting.applySkyPreset` `StrataEditor/src/Editor/EditorLightingCommands.cpp:953` | DG 5306; ML "Sun and sky presets" 279 | 0.7.0 |
| Extract Sun / Remove Sun | find the sun in an HDR map, make it the directional light; the importer paints it out | `Strata/src/Strata/Asset/HDRSun.h`; `lighting.extractSun` `EditorLightingCommands.cpp:977`; Inspector `InspectorPanel.cpp:1663` | DG 3420-3424; ML 72 | 0.6.0 |
| Sun to sky ratio | lighting views report sun and sky illuminance on flat ground and their ratio | `LightingViewStats` `R/SceneRenderer.h:366`; `R/SceneRendererLightingView.cpp` | DG 4888; ML 279, 361 | 0.7.0 |

### 1.9 Fog and aerial perspective

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Height fog component | `HeightFogComponent`: `Density` (0.02/m), `HeightFalloff` (0.2, min 1e-4), `BaseHeight`, `StartDistance`, `MaxOpacity`, `Color` (albedo), `ColorFromSky`, `SunScattering` (HG asymmetry x0.9); first active one applies | `R/RendererComponents.h:126-151`; `R/RendererComponents.cpp:405-424`; `SceneRenderer::FindHeightFog`, `SetHeightFog` `R/SceneRenderer.cpp:1395-1445` | DG "Fog and atmosphere" 5756-5774; ML "Height fog" 106 | 0.6.0 |
| Analytic fog integral | exponential density integrated per pixel in closed form, written so nothing overflows; sky fogged at infinite distance | `SH/Include/Fog.slang:13-110` | DG 5756 | 0.6.0 |
| Fog lighting | sky light (procedural horizon, environment irradiance from above, atmosphere's horizon toward the ray's azimuth, or ambient) plus the sun through Henyey-Greenstein | `GetFogInscattering` `SH/Include/Fog.slang:30-59`; `FrameConstants::FogLight` `R/SceneRenderData.h:85-92` | DG 5766 | 0.6.0; atmosphere horizon 0.7.0 |
| Aerial perspective | 32x32x32 froxel volume (in-scattering + transmittance, 512 KiB) per frame, slices at D((k+0.5)/32)^2, two trilinear fetches per pixel, before height fog | `SH/IBL/AtmosphereAerial.comp.slang`; `SH/Include/AerialPerspective.slang:17-26`; `SceneRenderer::SetAerialPerspective`, `RenderAerialPerspective` `R/SceneRendererAtmosphere.cpp:367-474`; `RenderData::c_AerialSize`... `R/SceneRenderData.h:420-433`; GPU stage `GPU.Aerial` | DG 5824 | 0.7.0 |
| Fog limits | no volume: no shafts, no local lights in fog, no shadows in fog (volumetric stream planned in wave 8, not on main) | `R/RendererComponents.h:126-129` | DG 5766; `Docs/Plans/Wave8/plan.md` 4.9 (line 867) | — |

### 1.10 Debug views and measurements of light

| Feature | What it is | Where | Documented | Release |
| --- | --- | --- | --- | --- |
| Shadows debug view | colors receivers by screen pixels per shadow texel (green 1, yellow 2, red 4+), cascade edges white, blend bands hatched, uncovered veiled; stats per cascade (median, p10, p90, share at 4+) | `R/SceneRendererShadowView.cpp`; `R/ShadowView.h`, `.cpp` (`ShadowView::Summarize`); `SH/Include/ShadowView.slang`; `SH/Overlay/ShadowView.frag.slang`; `SH/Debug/ShadowViewStats.comp.slang`; `SceneRenderOptions::ShowShadowView` | DG 4722-4747; ML 115 (end) | 0.7.0 |
| Lighting debug views | `SceneLightingView`: Lighting (albedo 1), AmbientOcclusion, Indirect, Luminance (EV100 bands), Albedo (marks outside 0.03-0.85) | `R/SceneRenderer.h:322-337`; `R/SceneRendererLightingView.cpp`; `SH/Overlay/LightingView.frag.slang`; `SH/Include/LightingView.slang`; forward reads `MaterialParams.y` `SH/Scene/Forward.frag.slang:72-82, 385-437` | DG 4874-4906; ML "Debug views" 361 | 0.7.0 |
| Lighting statistics | quarter-EV histograms of surfaces and background, value bins, sun/sky illuminance and ratio, via a ring of readbacks | `SH/Effects/LightingViewStats.comp.slang`; `RenderData::LightingViewStatsData` `R/SceneRenderData.h:621-646` | DG 4888 | 0.7.0 |
| Editor and agent access | `viewport.capture {debugView: shadows|lighting|ao|indirect|luminance|albedo}` and `viewport.setSettings`; result `debugView.shadows`, `debugView.lighting` | `StrataEditor/src/Editor/EditorViewportCommands.cpp:135-150, 1242-1270`; chip `StrataEditor/src/Panels/ViewportPanel.cpp:624` | DG "View commands" 3610; ML 115, 361 | 0.7.0 |
| Look-dev harness | fixed shots including `lookdev.furnace` (metals, dielectrics), `lookdev.contact`, `lookdev.thin`, `lookdev.room`, `lookdev.sky`, `ow.lowsun` | `Tools/LookDev.py`, `Tools/LookDev/Shots.json`, `LookDevScene.json` | DG "Look-dev harness" 666 | 0.7.0 |

### 1.11 Quality rows that belong to this area

`RendererQualitySettings` (`R/RendererQuality.h:122-160`), preset rows `R/RendererQuality.cpp:39-51`, traits `R/RendererQuality.cpp:158-168`; MG "The presets" 9; DG "Quality settings" 4009.

| Row | Low | Medium | High | Ultra | GPU stage |
| --- | --- | --- | --- | --- | --- |
| `ShadowResolution` | 1024 | 2048 | AutoFine (4096 below 1440 rows, 8192 from) | 8192 | GPU.Shadows |
| `ShadowCascades` | 3 | 4 | 5 | 5 | GPU.Shadows |
| `LocalShadowAtlasSize` | 2048 | 4096 | 4096 | 8192 | GPU.Shadows |
| `LocalShadowMaxTile` | 512 | 1024 | 1024 | 2048 | GPU.Shadows |
| `MaxShadowedLocalLights` | 4 | 16 | 16 | 16 | GPU.Shadows |
| `ShadowFilterQuality` (disk taps) | 8 | 16 | 24 | 32 | GPU.ScreenShadows |
| `ContactShadows` (steps; Custom 0 or 4-32) | 0 | 0 | 0 | 0 | GPU.ScreenShadows |
| `EnvironmentResolution` (prefiltered sky) | 256 | 256 | 512 | 512 | none |

Renderer specification switches (not quality rows): `MaxLights` 4096, `LightClusterGrid` {16,9,24}, `MaxLightsPerCluster`
256, `SpecularAntiAliasing`, `ExtendedStorageFormats`, `CacheLocalShadows`, `SpreadLightingUpdates`,
`LocalShadowViewsPerFrame` 12 (`R/SceneRenderer.h:145-271`).

### 1.12 GPU stages and bindings of the area

Stages in frame order (`SceneRenderer::RenderFrame` `R/SceneRenderer.cpp:3285-3560`): `GPU.Setup` (environment, procedural
sky, atmosphere tables), `GPU.Cull` (light culling and `BuildLightClusters`), `GPU.Aerial`, `GPU.Shadows` (`FitCascades`,
cascade draws, `BuildShadowRanges`, local shadow views), `GPU.Prepass`, `GPU.ScreenShadows`, `GPU.AO`, (`GPU.RadianceCascades`,
`GPU.Reflections`: other areas), `GPU.Opaque` (forward, sky), `GPU.Transparent` (scene-color copy, glass, blended), `GPU.TAA`,
`GPU.Post`, `GPU.Overlays` (shadow and lighting views).

Scene bindings used here (`SH/Include/Scene.slang`, `Shadows.slang`, etc.): b0 frame constants; t1 materials; t2 lights;
t3 irradiance; t4 prefiltered; t5 BRDF table; t6 environment cube; t7 cascade map; t8 local atlas; t11 AO; t12 cluster
lists; t13 local shadow data; t16 texture table; t17 `u_Cascades`; t18 screen reflections; t19 scene-color copy; t27
sky-view table; t28 screen shadow mask; t29 aerial volume; t32 shadow ranges; t33 blue noise; s9 comparison sampler.

### 1.13 Area lights

Not on main. Nothing in `Strata/src` or `Strata/shaders` implements rectangle, disk or tube lights (grep for `AreaLight`,
`RectLight`, `LTC` finds nothing relevant). The Roadmap lists area lights as later work (`Docs/Roadmap.md:949, 1672`), and
sized point/spot lights' *diffuse* light and shadows (PCSS) are listed as not done (`Docs/Roadmap.md` around 947: "sized local
lights' diffuse light and shadows (PCSS; their highlights take `SourceRadius` since wave 8)"). A branch
`agent/wave8-area-lights` exists (last commit 2026-11-09; subjects include "Add the rect lights' LTC tables and their shading
math", "Close each stretch under the horizon in the clipped form factor"): rect lights shaded with linearly transformed
cosines, not merged and not read here. What main has for "area-like" lights: `SourceRadius` (point, spot) and the sun's
Angular Diameter, which widen *highlights only* (energy-conserving lobe widening), and the sun's physically sized penumbra.

### 1.14 Tests that define the area's behaviour

CPU: `Renderer.LightUnits` (`T/LightUnitsTests.cpp`), `Renderer.ShadowCascades` (`T/ShadowCascadesTests.cpp`, 5 cases),
`Renderer.ShadowAtlas` (`T/ShadowAtlasAllocatorTests.cpp`, 4 cases), `MaterialTests.cpp`, `RendererComponentsTests.cpp`,
`RendererQualityTests.cpp`, `BlueNoiseTests.cpp`.
GPU: `GPU.SceneRenderer.Lighting` (`T/GPUSceneLightingTests.cpp`: units at 65,536 lux vs 1 lux bit-identical 303; spot cone
378; clustered = brute force 429; culling and relevance 496; GPU path beyond MaxLights 561; BRDF table and filtering 651;
white furnace metals 860; dielectrics by IOR 917; direct specular compensated 958; coat over metal 992; sized sun 1011;
source radius 1073), `GPU.SceneRenderer.Shadows` (`T/GPUSceneShadowTests.cpp`: acne at grazing angles 182, sub-texel
casters 321, alpha mask 360, cache 415, blend seam 490, fade 616), `GPU.SceneRenderer.ShadowFilter` (penumbra width 112,
TAA-independence 153, thin caster never lost 186, tent smoothness 245, ranges hold every texel 284, contacts recede at most
2.5 texels 370), `GPU.SceneRenderer.ShadowCascades` (first frame after a turn final 240, strafe without shimmer 298, ball
shot 501/540), `GPU.SceneRenderer.ScreenShadows`, `.ContactShadows`, `.ShadowView`, `.LocalShadows`
(`T/GPUSceneLocalShadowTests.cpp`), `.Fog` (`T/GPUSceneFogTests.cpp`: matches the integral 107, sky at infinity 204,
density 0 bit-identical 391), `GPU.Atmosphere` (`T/GPUAtmosphereTests.cpp`, `T/GPUAerialPerspectiveTests.cpp`: GPU table vs
CPU within 1% 188, night sky without bands 589, no daytime clamp 658), `GPU.ProceduralSky`, `GPU.SceneRenderer.Materials`
(`T/GPUSceneMaterialTests.cpp`, `T/GPUSceneSpecularTests.cpp`), `GPU.SceneRenderer.LightingViews`.
Perf: `PerfGPU.Renderer.ScreenShadows4K*`, `ShadowRedraw4K*`, `Transmission` (provisional).

### How completeness was checked

- Every header in `R/` was listed; those of this area are accounted for: `RendererComponents.h` (five light/sky/fog
  components plus `PostProcessComponent` exposure fields), `Material.h`, `MaterialData.h`, `RenderLights.h`,
  `ShadowCascades.h`, `ShadowAtlasAllocator.h`, `ShadowView.h`, `Atmosphere.h`, `SkyPresets.h`, `SceneRenderData.h` (the
  structs listed above), `TextureTable.h`, `BlueNoise.h`, `RendererQuality.h` (rows above), `SceneRenderer.h` (the members
  and structs cited). The `SceneRenderer*.cpp` feature files of this area: `Atmosphere`, `LocalShadows`, `ScreenShadows`,
  `ShadowView`, `LightingView`, `Glass`, plus `CollectLights`, `SetHeightFog`, `ChoosePreExposure`, environment functions
  in `SceneRenderer.cpp` and the cascade functions in `SceneRendererExtraction.cpp`.
- Every registered component of the area (`RegisterRendererComponents` `R/RendererComponents.cpp:271-424`):
  DirectionalLight, PointLight, SpotLight, SkyLight, HeightFog (ReflectionProbe belongs to the reflections area;
  PostProcess to post-processing; MeshRenderer's `CastShadows` noted). Every property of them is in 1.3, 1.8 and 1.9.
- Every shader entry of `Strata/CMakeLists.txt:89-198` that this area owns: `Scene/Forward.frag` (+5 variants),
  `Skybox.frag` (+Atmosphere), `ShadowMesh.vert` (+3 variants), `ShadowMask.frag`, `LightClusters.comp`, `LightCull.comp`,
  `LightCompact.comp`, `CascadeFit.comp`, `ShadowRanges.comp` (+Downsample), `Debug/ShadowViewStats.comp`,
  `IBL/ProceduralSky.comp`, `IBL/BRDFLut.comp`, `IBL/Atmosphere*.comp` (5), `Effects/SceneColorCopy.comp` (+Fallback),
  `Effects/ScreenShadows.frag`, `ContactShadows.frag`, `ScreenShadowsBlur.frag`, `LightingViewStats.comp`,
  `Overlay/ShadowView.frag`, `LightingView.frag`; and the includes `PBR`, `Lights`, `Clusters`, `Shadows`,
  `LocalShadows`, `Fog`, `Atmosphere`, `AtmospherePass`, `AerialPerspective`, `MaterialTextures`, `BlueNoise`,
  `ShadowView`, `LightingView`, `Exposure` (shared with post).
- Editor commands of the area: `lighting.applySkyPreset`, `lighting.extractSun` (and `lighting.bakeProbes`, which belongs
  to reflections), `material.create/set/get`, the `debugView` parameter of `viewport.capture`/`viewport.setSettings`.
- No host function of the script ABI is specific to lights: scripts reach light, sky and fog fields through the generic
  property access (`Entity::GetProperty/SetProperty("PointLight", "Color", ...)`, `StrataTests/FeatureTest/Scripts/
  ComponentFeatures.cpp:56, 114`).
- No asset type is specific to the area beyond Material (Texture and ColorLookup belong elsewhere).

---

## 2. Concepts to teach (dependency order)

Each: the problem, the approaches engines use, what Strata does and why, what newcomers get wrong.

1. **Light as a quantity: radiance, irradiance, and the photometric units.**
   Problem: a renderer adds and multiplies light, so its numbers must mean something. Approaches: arbitrary "intensity"
   (most older engines, Unity built-in), radiometric watts, photometric units (Frostbite 2014, Unreal's physical units,
   Filament). Strata: photometric on one scale with no hidden factors: lux for the sun, candela for points and spots,
   nits for the sky and emission (`R/RendererComponents.h:17-20`; DG 5322). Why: values from the real world and from glTF
   work as they are, and ratios (sun to sky) become physical. Mistakes: confusing lumens with candela (P/4pi), expecting
   a narrower spot cone to brighten (it does not: candela along the axis), mixing a "3 lux" default scene with a real
   120,000 lux sun.

2. **Linear color, HDR targets and floating-point range.**
   Problem: light spans 10 orders of magnitude; sRGB is a display encoding. Approaches: LDR with gamma tricks, HDR float
   targets, R11G11B10. Strata: RGBA16F HDR target, `SanitizeHDR` clamps at 65,000 and removes NaN; base color textures
   are sRGB, data maps linear. Mistakes: doing lighting on sRGB values; ignoring half-float limits (65,504 max, subnormals
   below 2^-14); letting a NaN spread through post-processing.

3. **Exposure, EV100 and pre-exposure.**
   Problem: map physical luminance to a display; keep a real sun representable in half floats. Approaches: fixed
   exposure, eye adaptation from an average, camera EV settings, pre-exposure (Frostbite/Unreal). Strata: manual
   `2^Exposure` or histogram-metered auto exposure (post area), and a power-of-two pre-exposure P that every HDR writer
   applies (`ChoosePreExposure`), exact because powers of two only shift the exponent. Mistakes: thinking pre-exposure
   changes the image (it never does unless something overflows); clipping a real sun with MaxEV 12.

4. **The surface description: the metallic-roughness model.**
   Problem: describe how a surface reflects light with few, artist-friendly numbers. Approaches: Phong/Blinn specular
   power, specular-glossiness, metallic-roughness (Disney 2012, glTF). Strata: glTF 2.0 metallic-roughness with texture
   maps, factors multiply maps (`R/Material.h:24-63`). Mistakes: putting a metal's color in the diffuse; using albedos
   outside 0.03-0.85 (the Albedo view marks them); treating roughness as linear alpha (it is perceptual, alpha =
   roughness^2).

5. **Textures as material inputs: color vs data, normal maps, tangent space.**
   Problem: per-texel variation; normal maps need a frame. Approaches: per-material descriptor sets, bindless tables.
   Strata: bindless textures behind a texture table (index -> slot, sampler, grayscale bit), XY normal maps with Z
   reconstructed, flat normal exact in half floats (`MaterialTextures.slang`). Mistakes: reading Z from BC5; sampling a
   normal map as sRGB; the 128/255 "flat" normal that tilts surfaces.

6. **The rendering equation for a single light, and the BRDF.**
   Problem: how much light leaves toward the eye from light arriving from one direction. Approach industry-wide:
   Cook-Torrance microfacet specular (D, G/V, F) plus Lambert diffuse. Strata: GGX D, height-correlated Smith V, Schlick
   F, Lambert weighted by (1-F)(1-metallic) (`PBR.slang:33-57, 129-148`). Mistakes: forgetting the NoL cosine; dividing
   diffuse by pi twice or never; using uncorrelated Smith.

7. **Fresnel, F0 and the index of refraction.**
   Problem: reflectance rises toward grazing angles; head-on reflectance of dielectrics depends on IOR. Strata: F0 =
   ((n-1)/(n+1))^2 from the material's IOR, 0.04 literal at 1.5 to stay bit-exact, metals take F0 from albedo
   (`MaterialData.cpp:51-59`, `Forward.frag:215`). Mistakes: thinking water is 4% (it is 2%); hard-coding 0.04 everywhere.

8. **Image-based lighting and the split sum (as far as this area needs it).**
   Problem: integrate the BRDF against a whole sky. Approach: Karis 2013 split sum (prefiltered radiance x BRDF table).
   Strata: `BRDFLut.comp` table read by the forward pass; the prefilter chain belongs to the reflections chapter.
   Needed here because the BRDF table also drives energy compensation.

9. **Energy conservation and multiple scattering.**
   Problem: single-scattering GGX loses light at high roughness (rough metals look dull). Approaches: Kulla-Conty 2017,
   Fdez-Aguera 2019, Filament's `1 + F0 (1/E - 1)`. Strata: the last, from the BRDF table already fetched, applied to every
   specular term (`GetSpecularEnergy`). Verified by the white furnace (`GPUSceneLightingTests.cpp:860`). Mistakes:
   compensating diffuse too; checking shading by eye instead of with a furnace.

10. **Specular aliasing and how to filter a highlight.**
    Problem: a highlight narrower than a pixel sparkles. Approaches: Toksvig, LEAN/CLEAN maps, Kaplanyan-Tokuyoshi
    screen-space normal variance, TAA. Strata: screen-space variance widening (`WidenRoughness`), capped at 0.18, and the
    rule that derivatives come only from the primitive's own inputs so both draw paths stay pixel-equal. Mistakes: taking
    derivatives after a `discard`; relying on TAA to hide sparkle.

11. **Light sources: directional, point, spot; attenuation and range.**
    Problem: model the sun and lamps cheaply. Approaches: punctual lights with inverse-square falloff and a windowing
    function (Karis 2013), linear/quadratic "attenuation constants" (legacy). Strata: windowed inverse square to `Range`,
    `t^2` cone falloff, one directional light (the brightest). Mistakes: giving lights huge ranges (cost; the range is a
    culling bound, not a brightness), expecting several suns.

12. **Sized sources and highlights.**
    Problem: real lights have size; point lights give pin-point highlights. Approaches: representative point (Karis), LTC
    area lights (Heitz 2016), lobe widening (roughness modification, "sphere normalization"). Strata: lobe widening of D
    only, normalized, for the sun's disk and bulbs (`GetSourceLobeAlpha2`). Main has no diffuse or shadow effect of size
    and no area lights. Mistakes: using a large SourceRadius as "softer light" (it dims and widens highlights only).

13. **Many lights: forward, deferred, tiled and clustered shading.**
    Problem: hundreds of lights, each pixel touched by few. Approaches: multi-pass forward, deferred (G-buffer), tiled
    deferred/forward+ (2D tiles), clustered (3D froxels, Olsson 2012, Doom 2016). Strata: clustered forward (16x9x24
    exponential slices), lights culled on the CPU (ranked, capped) or the GPU (uncapped), full clusters keep the most
    relevant. The documents do not say why Strata chose forward over deferred; what the code shows is one shader source
    compiled into opaque, transparent and glass variants, with a depth prepass (EQUAL test) so opaque pixels are shaded
    once, and screen-space inputs (AO, shadow mask, reflections) produced from the prepass. Mistakes: linear depth slices (wasted near clusters); thinking a cluster cap drops random lights.

14. **Shadow mapping.**
    Problem: is a point visible from the light? Approach: render depth from the light, compare. Concepts: light space,
    orthographic vs perspective shadow projections, reversed-Z, comparison samplers and PCF, shadow acne and peter-panning,
    slope/depth/normal biases, receiver plane bias, pancaking. Strata: reversed-Z D32, hardware comparison sampler,
    texel-relative biases, receiver plane from the inverse-transpose (not screen derivatives) (`Shadows.slang:94-111`).
    Mistakes: constant world-space bias; screen-space derivatives for the receiver plane (wrong at silhouettes, depend on
    quad grouping).

15. **Cascaded shadow maps and their stability.**
    Problem: one map cannot cover a whole view finely. Approaches: CSM/PSSM (log-uniform splits), fit to receivers
    (SDSM), stable CSM (bounding spheres + texel snapping, Valient 2008), virtual shadow maps (Unreal 5). Strata: stable
    cascades (fixed splits from 1.5 m, smallest sphere per slice, snapping in double, containment selection, blend bands,
    a fifth near cascade at High/Ultra) after trying receiver fitting in 0.7.0 and dropping it: the first frame after a
    turn is final and nothing near the camera re-cuts the slices (DG 4642). Mistakes: selecting a cascade by depth alone;
    snapping in float far from the origin; resizing squares as the camera turns (shimmer).

16. **Soft shadows: PCF, PCSS, contact hardening, noise.**
    Problem: real penumbrae widen with blocker distance. Approaches: fixed PCF, PCSS (Fernando 2005), VSM/ESM/MSM,
    ray-traced shadows. Strata: PCSS at the physical width `s tan(a)` with an exact lit/umbra classification from a depth
    range pyramid (never misses a thin caster), tent for narrow edges, Vogel disk turned by fixed blue noise, screen-space
    mask and edge-aware blur; nothing changes per frame, so a still view is identical with and without TAA. Mistakes:
    temporal noise that only TAA hides (the owner's rule: no history needed); blocker searches that miss thin casters.

17. **Screen-space shadow passes and contact shadows.**
    Problem: cost per pixel and detail below a texel. Approaches: deferred shadow masks (many engines), screen-space
    contact shadows (Days Gone, Unreal). Strata: mask after the prepass for opaque surfaces, per-pixel filter for
    transparent ones, contact shadows only under Custom quality because they shimmer. Mistakes: thinking contact shadows
    respect `CastShadows` (they come from every opaque pixel on screen).

18. **Shadows of local lights: atlases, cube faces, caching.**
    Problem: many shadowed lamps, each 1 or 6 views. Approaches: cube maps per light, dual-paraboloid, a shared atlas,
    caching static shadows. Strata: one atlas with quadtree tiles sized by screen size and relevance, guard bands, cached
    views keyed in world space, a redraw budget with fade-in, 16 shadowed lights at most on main. Mistakes: letting the lamp
    model cast into its own light; expecting a moving light to be free.

19. **The sky as a light source.**
    Problem: the sky lights everything from every direction. Approaches: constant ambient, HDR photographs, analytic skies
    (Preetham, Hosek-Wilkie), physical atmospheres (Bruneton 2008, Hillaire 2020). Strata: three sources into the same
    filter chain; an environment map's sun can be extracted into a shadow-casting directional light. Mistakes: leaving the
    sun in the HDR map and adding a directional light (double sun).

20. **Physical atmosphere: participating media basics.**
    Problem: blue sky, red sunsets, the sun's color at the ground. Concepts: extinction, scattering, absorption, optical
    depth, transmittance (Beer-Lambert), phase functions (Rayleigh, Henyey-Greenstein/Cornette-Shanks for Mie), single vs
    multiple scattering, precomputed LUTs. Strata: Hillaire-style LUTs (transmittance, multiple scattering, sky view,
    aerial froxels), a CPU double-precision transmittance for the sun's color, a 2^14 storage scale against half-float
    subnormals, double-buffered environment refresh. Mistakes: dimming the sun twice (the light's intensity is *above* the
    atmosphere); expecting the light's intensity to change the tables (it does not: tables are per lux).

21. **Fog: exponential height fog and aerial perspective.**
    Problem: distance haze without volumes. Approaches: distance fog, analytic height fog (Wenzel 2006, Unreal's
    exponential height fog), froxel volumetric fog (Wronski 2014). Strata: analytic height fog per pixel (no pass), lit by
    sky and sun (HG phase), applied after aerial perspective, sky fogged at infinite distance; no volumetric fog on main.
    Mistakes: expecting light shafts; zero falloff (infinite integral; hence `c_MinHeightFalloff`).

22. **Layered materials and transmission.**
    Problem: car paint, varnish; glass that refracts. Approaches: layered BRDFs (Weidlich-Wilkie), screen-space
    refraction from a color copy, ray-traced refraction. Strata: one coat lobe over the base, glass reading a mip-chained
    half-resolution scene-color copy at the refracted exit point, Beer's-law absorption. Limits: no glass behind glass, no
    AO or shadows from glass. Mistakes: expecting glass to cast shadows; blended surfaces behind glass.

23. **Measuring lighting instead of eyeballing it.**
    Problem: "looks right" fails across scenes and monitors. Approaches: false-color luminance, albedo validation, furnace
    tests, shadow texel density views. Strata: Lighting/AO/Indirect/Luminance/Albedo views with statistics, the shadows
    view (pixels per texel), the furnace shot, sun-to-sky ratio. Mistakes: tuning exposure to fix wrong albedo.

---

## 3. Code worth showing

| # | File and lines | What it teaches | Reader must know first |
| --- | --- | --- | --- |
| 1 | `R/RendererComponents.h:17-78` | Light components as plain data with units in comments; defaults; constants of ranges | C++ structs, the ECS idea |
| 2 | `R/Material.h:23-63` | The whole material model in one struct, glTF packing of maps | concept 4 |
| 3 | `R/MaterialData.cpp:40-59` | Beer's law absorption from a color and a distance; F0 from IOR with the bit-exact 1.5 case | Fresnel basics; float rounding |
| 4 | `R/MaterialData.cpp:61-95` | CPU material to GPU record; fallback textures, flags | texture table |
| 5 | `SH/Include/MaterialTextures.slang:47-65` | Tangent frame, XY normal decode, back-face flip | vectors, tangent space |
| 6 | `SH/Include/PBR.slang:33-57` | GGX D, correlated Smith V, Schlick F in 25 lines | concept 6 |
| 7 | `SH/Include/PBR.slang:126-148` | `EvaluateLightWeighted`: the whole direct-light BRDF and its weights | #6 |
| 8 | `SH/Include/PBR.slang:59-71` with `SH/Scene/Forward.frag.slang:211-218` | Energy compensation from the BRDF table | split sum table |
| 9 | `SH/IBL/BRDFLut.comp.slang:20-49` | Importance sampling GGX and deriving the table (pdf cancels D) | Monte Carlo basics |
| 10 | `SH/Include/PBR.slang:73-91` | Specular anti-aliasing by normal variance | derivatives `ddx/ddy` |
| 11 | `SH/Include/PBR.slang:12-31, 119-124` and `R/SceneRenderData.h:114-128` | Sized sources by lobe widening; the same math on CPU and GPU | #6, angles |
| 12 | `SH/Include/PBR.slang:194-207` | Windowed inverse-square and spot cone falloff | concept 11 |
| 13 | `R/RenderLights.cpp:44-85` | A light record: validation of non-finite values, spot bounding sphere | bounding spheres |
| 14 | `R/SceneRenderer.cpp:2557-2601` | Picking the sun; preview lighting; frame constants from components | ECS views |
| 15 | `R/SceneRenderer.cpp:2612-2697` | CPU light culling, relevance ranking, cap, camera-relative upload in double | frustum culling; precision |
| 16 | `SH/Include/Clusters.slang:49-78` | Log depth slices, cluster index, relevance | concept 13 |
| 17 | `SH/Scene/LightClusters.comp.slang:42-101` (and 103-189 as an advanced box) | Building cluster lists in a compute shader with shared memory; relevance bisection over ordered floats | compute shaders, groupshared |
| 18 | `SH/Scene/Forward.frag.slang:198-279` | `ShadeLitSurface`: sun with mask, cluster loop with local shadows and source lobes | #7, #16 |
| 19 | `SH/Scene/Forward.frag.slang:374-427` | The main: sample everything before any discard, coat and glass setup | derivative rule |
| 20 | `R/ShadowCascades.cpp:14-21, 56-71` | Log-uniform splits; why splits start at a fixed distance | concept 15 |
| 21 | `R/ShadowCascades.cpp:73-102` | Smallest sphere around a frustum slice, lens only | geometry of frusta |
| 22 | `R/ShadowCascades.cpp:104-141` | Layout with blend bands; texel snapping in double | #20, #21 |
| 23 | `SH/Include/Shadows.slang:45-92` | Containment-based cascade selection and blend weights | #22 |
| 24 | `SH/Include/Shadows.slang:94-111` | Receiver plane depth bias from the projection's cofactor | matrices, planes |
| 25 | `SH/Include/Shadows.slang:143-260` (central, long) | Physical PCSS: depth-range classification, blocker estimate, tent, Vogel disk with blue noise | concepts 14, 16 |
| 26 | `SH/Scene/ShadowRanges.comp.slang:27-70` | Building a conservative min/max pyramid with outward rounding | reversed-Z |
| 27 | `SH/Scene/ShadowMesh.vert.slang:46-51` | Pancaking in two lines | orthographic projection |
| 28 | `SH/Effects/ScreenShadows.frag.slang:53-92` | Reconstructing position and normal from the prepass, encoding visibility as sqrt | prepass, octahedral normals |
| 29 | `SH/Include/LocalShadows.slang:43-97` | Cube face selection, biases in texels at depth, Poisson PCF clamped to a tile | atlas concept |
| 30 | `R/ShadowAtlasAllocator.h:21-56` | A quadtree allocator's contract (deterministic, merge on free, FitTileSizes) | quadtrees |
| 31 | `R/Atmosphere.cpp:18-33, 61-101` | Extinction profiles, midpoint transmittance quadrature, sun transmittance with the disk's horizon share | concept 20 |
| 32 | `SH/Include/AtmospherePass.slang:73-89` and `SH/IBL/AtmosphereSkyView.comp.slang:16-51` | One integration segment of single + multiple scattering; quadratic step distribution | #31 |
| 33 | `SH/Scene/Skybox.frag.slang:12-50` | Sky background, analytic sun disk as illuminance over solid angle, fogged sky, pre-exposure | units |
| 34 | `SH/Include/Fog.slang:16-96` | Closed-form height fog integral that cannot overflow; HG phase; blend | exponentials |
| 35 | `SH/Include/AerialPerspective.slang:17-26` | Reading a froxel volume with a quadratic depth mapping | 3D textures |
| 36 | `R/SceneRenderer.cpp:1531-1598` | Pre-exposure choice from asynchronous readbacks, epochs, hysteresis | concept 3 |
| 37 | `SH/Scene/Forward.frag.slang:354-371` | Glass: refraction to an exit point, mip by roughness, Beer's law | #3 |

Two central algorithms to show whole even though long: #25 (`SampleCascadeShadow`) and #22 with #21 (the stable layout).
#17's overflow half is advanced; show 42-101 in the main text.

---

## 4. Figures

### Diagrams

1. **Light units map**: lux on a surface, candela along a direction, nits off a surface/sky; arrows with `pi L = E` and
   `I = P / 4pi`; the reference values table placed on a log scale from moonlight to the sun's disk.
2. **HDR range and pre-exposure**: a log axis of half-float range (2^-24 subnormal, 2^-14 normal, 65,504 max) with a
   sunlit scene's luminances before and after multiplying by P = 2^-19.
3. **Microfacet BRDF anatomy**: D, G/V, F as three panels; how roughness widens D; Fresnel curve for IOR 1.33/1.5/2.42
   and metals.
4. **Energy compensation**: plot of E(NoV, roughness) from the BRDF table and the 1/E factor; furnace sphere rows before
   and after.
5. **Data flow of a material**: `.stmat` JSON -> `MaterialProperties` -> `MaterialGPU::Build` -> `MaterialData` (144 B,
   memory layout diagram of its fields) -> texture table entry -> bindless slot -> `SampleMaterialTexture`.
6. **Light record flow**: component change -> EnTT signal -> `RenderLights` queue -> `Sync` -> record + change log ->
   `RenderSceneGPU` mirror -> `LightCull` -> `LightCompact` -> light buffer -> `LightClusters` -> cluster lists ->
   `Forward.frag`; with the CPU path branch (`CollectLights` ranking, cap).
7. **Froxel grid**: a view frustum cut into 16x9 tiles and 24 exponential slices; one cluster's AABB; a light sphere
   overlapping several clusters; cluster buffer layout (count + indices, stride 257).
8. **Frame timeline of the area's passes**: GPU.Setup (sky, atmosphere tables) -> Cull (lights) -> Aerial -> Shadows (fit,
   cascades, ranges, local views) -> Prepass -> ScreenShadows (mask, contact, blur) -> AO -> Opaque (forward, sky) ->
   Transparent (copy, glass, blended) -> Post -> Overlays (shadow/lighting views).
9. **Shadow mapping basics**: light view, depth comparison, acne and the three biases, pancaking.
10. **Stable cascades**: top view of the camera frustum with 4+1 slices, their bounding spheres, squares snapped to the
    light-space texel grid, blend bands; a second panel showing the camera turned 90 degrees with identical spheres.
11. **Cascade selection by containment**: a position near a square's edge pushed by the normal offset, why depth alone
    fails.
12. **PCSS geometry**: sun disk of angular radius a, blocker at separation s, penumbra 2 s tan(a); then the filter's
    decision tree: range cells -> lit / umbra / penumbra -> tent or Vogel disk.
13. **Depth range pyramid**: a 16x16 patch of shadow texels, level-0 cells of 4x4 with (nearest, farthest), levels 1-2;
    the outward rounding.
14. **Screen-space mask pipeline**: prepass depth + normal -> ScreenShadows (RG8: sqrt visibility, blur radius) ->
    [ContactShadows] -> blur H -> blur V -> forward SRV 28; ping-pong targets A and B.
15. **Local shadow atlas**: an 4096 atlas with quadtree tiles of a point light's six faces and spot lights, guard bands
    drawn; state machine of a view (no content -> drawn -> cached -> dirty -> redrawn) with fade-in.
16. **Atmosphere LUTs**: the four tables with their axes (transmittance: height x mu; multiple scattering: height x sun
    mu; sky view: azimuth x elevation crowded at the horizon; aerial: screen x screen x depth), what reads each.
17. **Atmosphere environment refresh**: a state machine (current maps, refresh in 14 steps, spare), triggers (0.5 degree,
    settings, sun on/off).
18. **Height fog integral**: density vs height curve, a view ray, the optical depth formula; blend with in-scattered light.
19. **Glass**: refracted ray to the exit point at `Thickness * |M^T n|`, sampling the half-res copy at a roughness mip.
20. **Shading order within one pixel**: material sample -> shading normal -> roughness widening -> sun (mask) -> cluster
    lights -> indirect (other chapter) -> coat -> emission -> aerial perspective -> height fog -> glass transmission ->
    pre-exposure -> SanitizeHDR.

### Screenshots (each with scene and how to isolate the feature)

Use the look-dev project (`Tools/LookDev/LookDevScene.json`, built by `Tools/LookDev.py`), Basic 3D, and the samples (copies).
Captures through `viewport.capture`, which accepts `debugView` and `quality`.

1. Metallic-roughness grid: a row of spheres roughness 0-1 for metal and dielectric (look-dev "Furnace" entity, shot
   `lookdev.furnace`, regions `metals` and `dielectrics`); toggle by `material.set`.
2. White furnace before/after energy compensation: same shot, Tonemapper None (text note: 0.6.0 build or a hacked shader
   for "before", or the plotted values).
3. IOR: water (1.33) vs glass (1.5) vs diamond (2.42) puddles; the Showcase's puddles (IOR 1.33) under the atmosphere.
4. Normal map on/off on a brick wall; and the 0.3-degree flat-normal bug on a mirror plane (explain with a diagram if no
   old build).
5. Specular anti-aliasing on/off: a bumpy metal sphere at 4K, `SceneRendererSpecification::SpecularAntiAliasing` (tests
   only) or crops from `GPU.SceneRenderer.Materials`; for the book, two captures with a custom build flag.
6. Sun Angular Diameter 0 vs 0.53 vs 10 on a mirror sphere and on shadows (`DirectionalLight.ShadowSoftness`).
7. Point light Source Radius 0 vs 0.05 vs 0.3 on wet ground (Showcase fire, Source Radius 0.25, and lanterns 0.04).
8. Spot light cone inner/outer angles on a wall; point light range window.
9. Many lights: a grid of 1,000 small point lights (scene built by commands), with `Lighting` debug view.
10. Light units: the same scene at 65,536 lux / exposure -16 and 1 lux / exposure 0, identical (mirror of the test).
11. Luminance debug view of a sunlit street and an interior (Third-Person `tp.scene`, look-dev `lookdev.room`).
12. Albedo debug view marking out-of-range albedos (Basic 3D with a black and a white cube).
13. Shadows debug view at Medium vs High (`viewport.capture {debugView: "shadows", quality: "medium"/"high"}`) on the
    Third-Person course; legend with pixels per texel.
14. Cascade blend 0 vs 0.1 across a split (a long fence; `DirectionalLight.CascadeBlend`).
15. Penumbra growing with distance: look-dev `lookdev.thin` (poles 3, 5, 10 cm) at Angular Diameter 0.53 and 2.
16. Shadow filter taps 8 vs 32 on a wide penumbra (Custom quality `ShadowFilterQuality`), without TAA.
17. Shadow acne with `ShadowBias` and `ShadowNormalBias` 0 vs defaults at a grazing sun (`ow.lowsun` shot).
18. Stair steps on a grazed receiver with and without the stair blur (needs an engine change; else the test crops of
    `GPU.SceneRenderer.ScreenShadows` "Hard edges on a receiver the sun grazes").
19. Contact shadows: look-dev `lookdev.contact` (5 cm plate) with Custom `ContactShadows` 16 vs 0.
20. Fifth cascade: Showcase shot 5 (door post 0.3 m away) at four vs five cascades (`ShadowCascades` 4/5 Custom), in the
    shadows view.
21. Point light shadows: Third-Person lanterns under trees (`tp.lantern`), `CastShadows` on/off; `ShadowFilterRadius` 0
    vs 8; the lamp-casting-into-its-own-light pitfall.
22. Sky sources side by side: environment map, procedural, atmosphere (`SkyLight.Source`), same scene.
23. Atmosphere times of day: sun elevation 60, 20, 6, 0, -6 degrees (`lighting.applySkyPreset {preset: "Clear",
    sunElevation: ...}`), with the sun's ground illuminance from the command's `groundIlluminance`.
24. Presets Clear / Hazy / Overcast / GoldenHour on Basic 3D.
25. Aerial perspective on/off and scale 1 vs 6 (Open World `ow.scene`, mountains; `SkyLight.AerialPerspective`).
26. Height fog: density, falloff, `SunScattering` 0 vs 1 looking toward the sun, `ColorFromSky` on/off, `MaxOpacity`
    (Showcase or Open World).
27. Clear coat: Physics Playground balls (coat), coat roughness 0 vs 0.5, coat normal map.
28. Glass: Physics Playground ball pit walls; IOR 1.0 vs 1.5, Thickness 0 vs 0.1, attenuation color.
29. Extract Sun: an HDR map with its sun, before and after Extract Sun + Remove Sun (shadows appear).
30. Preview lighting: an unlit scene in the editor vs the game view.

---

## 5. Rules and pitfalls ("why" boxes)

1. **Every intensity has a unit, and nothing rescales it.** Hidden factors make physical values meaningless and break
   imported glTF lights (candela and lux are read 1:1). DG 5322; `Renderer.LightUnits`.
2. **A spot light's candela is along its axis.** Narrowing the cone does not brighten it; to keep lumens, compute
   P / (2pi(1 - cos t)). DG 5326.
3. **The sun's intensity is above the atmosphere under the Atmosphere source.** The renderer multiplies in the
   transmittance; dimming it yourself darkens twice. DG 5803.
4. **Every HDR writer multiplies by the pre-exposure, and every reader divides it out.** A pass that forgets either shows
   wrong brightness only when P is not 1, i.e. in real-daylight scenes (`Forward.frag:362, 465`, `Skybox.frag:50`,
   screen reflections `/ TemporalParams.y`). DG 5365.
5. **Value views are written without pre-exposure.** At P = 2^-19 an albedo of 0.03 becomes subnormal in half floats.
   `Forward.frag:463-465`.
6. **Clamp HDR with `SanitizeHDR`.** Inf and NaN turn black after tone mapping or spread through blur and bloom. DG 4544.
7. **Read normal maps as XY and reconstruct Z.** BC5 stores only two channels; RGBA8 and BC5 must shade alike. DG 6122.
8. **The flat normal must be exactly flat.** 128/255 is not 0.5; it tilted every unmapped surface by 0.3 degrees and
   mirrors' reflections by twice that. DG 6122.
9. **F0 0.04 is written out at IOR 1.5.** The formula gives 0.040000003, which would change every default material by a
   rounding and break bit-exact tests. `MaterialData.cpp:53-55`.
10. **Take derivatives before any `discard`, only of the primitive's own interpolants and textures, in quad-uniform flow.**
    A discarding neighbour leaves derivatives undefined (Mesa drops the lane, MoltenVK shows nothing), and derivatives of
    data from other primitives make the CPU and GPU-driven paths differ. DG 4549, 4812; `Architecture.Shaders`.
11. **Check shading changes with the white furnace and the debug views, not by eye.** Energy errors hide under exposure.
    DG 4799; `GPUSceneLightingTests.cpp:860, 917`.
12. **Sized sources widen only D and keep it normalized.** Widening visibility or not renormalizing adds light. A larger
    SourceRadius than the real bulb dims and spreads the highlight. DG 4836.
13. **Light records are kept from signals: a direct write to a light field must signal** (`MarkModified`,
    `registry.patch`), like transform writes. AGENTS.md "Scene caches"; ARCH 2270.
14. **Every reader of `LightRecord` sizes by `sizeof`; `LightData` stays 64 bytes, `MaterialData` 144.** Shaders mirror
    the layouts by hand. DG 4508, 6128.
15. **Select a cascade with `SelectShadowCascade`, never by depth alone.** The normal offset can move a lookup off its
    square, and a split alone does not say which square holds the point. DG 4677.
16. **Cascade layouts come only from `ShadowCascades::GetLayout`, the view's alone; nothing is read back.** Fitting to a
    readback made shadows sharpen over a second after a turn and jump when a ball passed the camera (0.7.0). AGENTS.md
    Rendering; DG 4642.
17. **Snap in double, in absolute light space.** Float snapping far from the origin crawls. `GetSquare`.
18. **The sun's filter uses fixed noise, never `TemporalParams.z`.** A still view must be the same image in every frame
    with and without TAA (owner's direction: no TAA dependence). DG 4558. Local lights still turn with TAA on main (wave 8
    plan 4.7 step 6 moves them to fixed noise).
19. **Change both shadow paths together.** Opaque surfaces read the mask (SRV 28), transparent ones call
    `SampleDirectionalShadow`. DG 4719; AGENTS.md.
20. **A new input of how casters are drawn changes a version the shadow caches compare.** Otherwise cached cascades and
    local views keep stale shadows. AGENTS.md; `LocalShadowContent`.
21. **Contact shadows come from every opaque pixel on screen.** They ignore `CastShadows`, see nothing off screen, and
    shimmer in motion, which is why no preset draws them. DG 4614.
22. **Keep the lamp mesh out of its own light's shadow** (Cast Shadows off on the lamp mesh), or it darkens the room.
    ML 115.
23. **Only one directional light shines** (the brightest), and only the first active SkyLight, HeightFog and Post Process
    apply. `CollectLights`, `FindHeightFog`.
24. **Atmosphere table readers multiply by `EnvironmentParams.x`.** The tables store light per lux times 2^14; only
    `GetMultipleScattering` divides itself. DG 5788.
25. **Height fog needs a falloff above 0.** With none the integral toward the sky never ends. `c_MinHeightFalloff`.
26. **Fog is not a volume.** No shafts, no local lights, no shadows in fog on main; do not promise them. DG 5766.
27. **Glass is not in the prepass.** It gets no AO, casts no shadow, and the copy holds no transparent surface, so glass
    behind glass is not seen. DG 6108.
28. **A real sun needs automatic exposure with MaxEV 16.** Older scenes stored 12 and clip. DG 5384.
29. **Fragment shaders shading lights in non-uniform flow use explicit LOD comparisons** (`SampleCmpLevelZero`); zero
    gradients cost 2.2-2.4 times as much. DG 4709; `Shadows.slang:119-126`.
30. **Documentation drift to watch:** `ML` "Shadows" table says 3/4/4/4 cascades while code and `MG:17` say 3/4/5/5 (the
    prose explains the fifth); ML says "at most 16 point and spot lights cast shadows" while Low allows 4. The book should
    take numbers from `R/RendererQuality.cpp:39-51`.

---

## 6. Hands-on

### For game developers (editor, samples, scripts)

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Light Basic 3D with each preset and read `groundIlluminance` and the sun-to-sky ratio from the Lighting view legend | easy | presets, units, the ratio |
| Build a night scene: a 0.2 lux moon, a 64 cd lamp (800 lm), a 1 cd candle; set exposure manually from the reference table; then switch to auto exposure | easy | candela/lumen conversion, EV100 |
| Make a material set: rough copper, polished gold, wet asphalt (IOR 1.33 puddle over rough dark ground), check albedos in the Albedo view | easy | metallic-roughness, IOR, albedo ranges |
| Shadow tuning: on the Third-Person course find acne at a low sun, fix it with biases, then see peter-panning when overdone; compare Medium and High in the Shadows view | medium | biases, cascades, quality |
| Penumbra study: three poles at 0.5, 2 and 8 m from a wall; Angular Diameter 0.53 vs 2; measure the soft edge against 1.374 s tan(a) | medium | PCSS geometry |
| Lantern town: four shadowed point lights, Source Radius 0.04, moving one with a script (`SetProperty`, transform) and watching redraw stats (`renderStats`) | medium | local shadows, caching cost |
| Day cycle script: rotate the sun entity over time under the Atmosphere source; observe environment refresh every 0.5 degrees and the sky at sunset | medium | atmosphere, refresh |
| Valley fog: Height Fog with base at the valley floor, falloff for 50 m thickness, Sun Scattering toward a low sun; tune density to hide half at 35 m | easy | fog parameters |
| Glass display case with a coloured liquid (Thickness, attenuation) and a varnished wooden base (clear coat) | medium | transmission and coat, their limits |
| Extract Sun from an HDR map and verify shadows appear and the sky no longer double-lights | easy | sky vs sun |

### For engine developers (change or extend the engine)

| Exercise | Difficulty | Proves |
| --- | --- | --- |
| Write a CPU reference of `EvaluateLightWeighted` and compare with a 1-pixel GPU render (pattern of `GPUSceneLightingTests`) | medium | BRDF terms, test harness |
| Re-derive the BRDF table: run `BRDFLut.comp`'s integral in C++ for a few (NoV, roughness) and compare with the GPU table | medium | split sum, importance sampling |
| Disable energy compensation locally and measure the furnace loss per roughness; plot against 1/E | medium | multiple scattering |
| Add a `Spot` light "lumens mode" helper that converts to candela for a given cone (an editor command or Inspector tooltip), with a unit test | easy | units, component registry |
| Change the cluster grid (e.g. 32x18x32) and measure `GPU.Cull`/`GPU.Opaque` with `editor.perf`; explain the trade | medium | clustered shading costs |
| Write a unit test for `ShadowCascades::GetLayout`: a turned camera keeps spheres; spheres hold their slices (extend `T/ShadowCascadesTests.cpp`) | easy | stable cascades |
| Implement cascade selection by depth only (on a branch), show the artefact the containment test prevents with the shadows view | medium | containment |
| Visualize the depth-range pyramid level 0 as a debug overlay | hard | pyramid layout, debug passes, GPU stages |
| Move `LocalShadowSampleRotation` to the fixed blue-noise tile (wave 8 plan 4.7 step 6) and show a still frame is identical with and without TAA | medium | noise rules, tests |
| Add a fog parameter (e.g. a second exponential layer) end to end: component field, `SetHeightFog`, `Fog.slang`, analytic test against numeric integration, feature test entry | hard | component pipeline, analytic integrals, rule 6 |
| Evaluate the atmosphere's transmittance on the CPU at sunset and compare with the light color reported by `SceneRendererStats::SunTransmittance` | easy | atmosphere math |
| Sketch area lights: read Heitz 2016 LTC and outline where a rect light would enter `LightRecord`, `LightData`, clusters and `ShadeLitSurface` (compare later with the branch once merged) | hard | the light pipeline end to end |

---

## 7. Glossary

- **Albedo / base color**: the fraction of light a surface reflects diffusely (dielectric) or its F0 color (metal).
- **Metallic**: 0 dielectric, 1 conductor; blends diffuse off and F0 toward the albedo.
- **Perceptual roughness**: the artist's roughness; GGX alpha = roughness squared.
- **BRDF**: bidirectional reflectance distribution function, reflected radiance per irradiance for a pair of directions.
- **Microfacet**: a tiny mirror; rough surfaces are distributions of them.
- **GGX / Trowbridge-Reitz**: the microfacet normal distribution D used here.
- **Smith visibility (height-correlated)**: masking-shadowing term G combined with the BRDF's denominator as V.
- **Fresnel / Schlick approximation**: reflectance rising toward grazing angles; `F0 + (1 - F0)(1 - cos)^5`.
- **F0**: reflectance at normal incidence.
- **IOR**: index of refraction; sets a dielectric's F0 and glass's refraction.
- **Lambert**: ideal diffuse reflection, albedo / pi.
- **Split sum**: approximating the image-light integral as prefiltered radiance times a BRDF table.
- **BRDF table (LUT)**: 2D table of F0 scale and bias by NoV and roughness.
- **Directional albedo (E)**: the fraction of light a lobe reflects for one view direction.
- **Energy compensation**: restoring the light single-scattering GGX loses.
- **White furnace test**: a uniform 1-nit sky; an energy-conserving white surface must show 1 everywhere.
- **Specular aliasing**: sparkle from highlights narrower than a pixel.
- **Specular anti-aliasing (geometric)**: widening roughness by the normal's variance over a pixel.
- **Horizon fade**: fading image light reflected below the geometric surface.
- **Clear coat**: a thin dielectric layer with its own lobe over the base.
- **Transmission**: light passing through a surface (glass).
- **Beer-Lambert law**: exponential absorption with distance; transmittance `exp(-sigma d)`.
- **Attenuation color / distance**: the color white light has after a distance in a volume.
- **Scene-color copy**: a copy of the HDR image glass refracts.
- **Lux (lx)**: illuminance, lumens per square meter.
- **Candela (cd)**: luminous intensity, lumens per steradian.
- **Nit (cd/m^2)**: luminance.
- **Lumen (lm)**: luminous flux; a point light of P lm has P / 4pi cd.
- **EV100**: exposure value at ISO 100; log2(L) + 3 for an average luminance L.
- **Middle gray**: 18% reflectance, the target of metering.
- **Exposure key**: Strata's offset that lets interiors meter darker than sunlight.
- **Pre-exposure**: a power-of-two scale applied to HDR values so they fit half floats.
- **Half float / RGBA16F / subnormal**: 16-bit float format; values below 2^-14 lose precision.
- **Punctual light**: a light with no size (point, spot, directional).
- **Range (light)**: where a light's windowed falloff reaches zero; also its culling bound.
- **Inner/outer cone angle**: half angles of full and zero spot light.
- **Source radius / angular diameter**: a light's size, which widens its highlights here.
- **Lobe widening**: modelling a sized source by broadening the BRDF lobe.
- **Area light / LTC**: lights with surface; linearly transformed cosines shade them (not on main).
- **Light record**: the render scene's per-light data (96 bytes).
- **Relevance**: how much a light matters to the view (projected size of its region).
- **Clustered shading / froxel**: frustum voxel grid; each cluster lists the lights reaching it.
- **Exponential depth slices**: cluster slices spaced in log depth.
- **Light culling**: removing lights whose region misses the view.
- **Shadow map**: depth image rendered from the light.
- **Reversed-Z**: depth 1 near, 0 far, for float precision; nearer to the light is larger.
- **Comparison sampler / PCF**: hardware depth comparison with bilinear filtering / percentage-closer filtering.
- **Shadow acne / peter-panning**: self-shadowing speckles / shadows detached from casters by too much bias.
- **Depth bias, slope bias, normal offset, receiver plane bias**: the four ways to fight acne.
- **Pancaking**: flattening casters in front of a shadow near plane onto it.
- **Cascaded shadow maps (CSM)**: several shadow maps for slices of the view distance.
- **Split / slice**: a cascade's far distance / its range of view distances.
- **Logarithmic vs uniform splits, distribution**: how splits are spaced and blended.
- **Stable cascades**: cascades whose size depends only on the lens and that snap to whole texels.
- **Texel snapping**: moving a shadow square in whole texels so edges do not crawl.
- **Cascade blend band**: the end of a slice where it mixes into the next cascade.
- **Containment (cascade selection)**: picking the first cascade whose square holds the point.
- **Texel density / pixels per texel**: how many screen pixels one shadow texel covers.
- **PCSS**: percentage-closer soft shadows: blocker search, penumbra estimate, variable filter.
- **Umbra / penumbra**: fully / partly shadowed region.
- **Contact hardening**: shadows sharp at contact, softer with distance.
- **Depth range pyramid**: per cell (nearest, farthest) depths for quick lit/umbra decisions.
- **Tent filter**: a fixed small bilinear filter of 4 taps.
- **Vogel disk**: spiral sample pattern by the golden angle.
- **Blue noise**: noise without low frequencies, for less visible grain.
- **Screen-space shadow mask**: a per-pixel shadow image computed after the prepass.
- **Edge-aware (bilateral) blur**: blur weighted to not cross surfaces.
- **Contact shadows**: screen-space ray marches for small occluders.
- **Shadow atlas / tile / guard band**: one texture holding many shadow views / one view's square / its margin.
- **Quadtree allocator**: power-of-two tile allocation that merges free quarters.
- **Cube shadow (six faces)**: a point light's six perspective views.
- **Environment map (equirectangular HDR)**: a 360-degree photo of light.
- **Procedural sky**: a sky gradient computed from colors.
- **Physical atmosphere**: sky computed from scattering in air.
- **Rayleigh / Mie scattering**: scattering by molecules (blue) / aerosols (white, forward).
- **Ozone absorption**: absorption layer that tints twilight.
- **Extinction / optical depth / transmittance**: loss coefficient / its integral / exp(-optical depth).
- **Phase function / Henyey-Greenstein**: angular distribution of scattering; the one-parameter model.
- **Single / multiple scattering**: one bounce in the medium / all higher orders.
- **LUT (transmittance, multiple scattering, sky view)**: precomputed tables of the atmosphere.
- **Aerial perspective**: haze and dimming of distant surfaces by air.
- **Storage scale**: the 2^14 factor that keeps atmosphere tables out of subnormals.
- **Height fog**: fog whose density decays exponentially with height.
- **In-scattering**: light scattered into the view ray.
- **Sun-to-sky ratio**: illuminance from the sun over that from the sky on flat ground.
- **Preview lighting**: the editor's stand-in sun and sky for unlit scenes.
- **Debug view (lighting, AO, indirect, luminance, albedo, shadows)**: overlays that show light as numbers.
- **GPU stage**: a named, timed section of the frame on the GPU.

---

## 8. Proposed chapters (teaching order)

1. **Light by the numbers: units, HDR and exposure** (concept, both, M, 4 screenshots). Purpose: the reader can explain
   lux, candela and nits, convert lumens, pick an exposure from EV100, and say why the HDR target needs a pre-exposure.
   Prerequisites: rendering basics (what a pixel shader writes), floating point.
2. **Describing surfaces: Strata's material model** (concept + reference, both, M, 5). Purpose: author metallic-roughness
   materials with maps, alpha modes, emission and IOR, and know how a `.stmat` reaches the GPU. Prereq: ch. 1, textures.
3. **The BRDF in code** (internals, engine, L, 4). Purpose: read and modify `PBR.slang`: GGX, Smith, Schlick, Lambert,
   the BRDF table, energy compensation, specular AA, sized-source lobes, the horizon fade; verify with a furnace.
   Prereq: ch. 2, vectors and dot products, Monte Carlo intuition (box).
4. **Lights: sun, points and spots** (concept + internals, both, M, 4). Purpose: place and tune lights, explain falloff
   and cones, and follow a light component into a light record and frame constants. Prereq: ch. 1, 3; ECS and render
   scene basics.
5. **Many lights: culling and clustered forward shading** (internals, engine, L, 2). Purpose: explain forward vs deferred
   vs tiled vs clustered, read `CollectLights`, `LightCull/Compact/Clusters.comp` and the forward loop, and measure costs.
   Prereq: ch. 4, compute shaders, GPU-driven path basics.
6. **Shadow mapping fundamentals** (concept, engine, M, 3). Purpose: render and sample a shadow map, explain reversed-Z
   comparisons, acne and the four biases, pancaking. Prereq: projections, depth buffers.
7. **Sun shadows I: stable cascaded shadow maps** (internals, engine, L, 4). Purpose: explain and modify the stable
   layout, the fifth cascade, containment, blend bands, the GPU depth fit, caster selection and caching; read the shadows
   view. Prereq: ch. 6.
8. **Sun shadows II: the soft shadow of a real sun** (internals, engine, XL, 6). Purpose: derive PCSS at physical width,
   the depth-range classification, tent and Vogel disk with blue noise, the screen-space mask and blur, contact shadows,
   the transparent path, and why nothing depends on the frame. Prereq: ch. 7, sampling and noise.
9. **Shadows of point and spot lights** (internals, engine, M, 3). Purpose: explain the atlas, quadtree tiles, cube faces,
   guard bands, view caching, the redraw budget and fades. Prereq: ch. 6, ch. 5.
10. **The sky: maps, a procedural sky and Earth's atmosphere** (concept + internals, both, L, 5). Purpose: choose a sky
    source, extract a sun, use presets; understand Rayleigh/Mie/ozone, the LUTs, the sun's transmittance, the storage
    scale and the environment refresh. Prereq: ch. 1, 4; IBL overview (link to the reflections chapter).
11. **Air and fog: aerial perspective and height fog** (internals, both, M, 3). Purpose: tune fog, derive the closed-form
    integral, read the aerial volume; know what fog cannot do. Prereq: ch. 10.
12. **Layers and glass: clear coat and transmission** (internals, both, M, 3). Purpose: author coats and glass, follow
    the coat lobe and the scene-color copy, know the limits. Prereq: ch. 3, transparent pass basics.
13. **Lighting a scene in the editor (tutorial)** (tutorial, game, M, 4). Purpose: light an outdoor and an indoor scene
    from presets and real values, balance the sun-to-sky ratio, tune shadows and fog, validate with the debug views.
    Prereq: ch. 1, 2, 4 (game-facing parts), editor basics.
14. **Measuring light: debug views, statistics and look-dev** (reference + tutorial, both, S, 3). Purpose: use and read
    every view and its statistics from the editor and from agents (`viewport.capture`), and run look-dev comparisons.
    Prereq: ch. 1, 7.
15. **Reference: lighting components, material properties and quality rows** (reference, both, S, 0). Purpose: one place
    for every field, unit, default, range and preset value. Prereq: none.

Area lights: a placeholder section in ch. 4 ("lights with size: what main does, what LTC rect lights add") until the
branch lands; then a chapter of its own (internals, M).

---

## 9. Not determined

- **Not read**: `ScreenShadowsBlur.frag` beyond its header comments; `ContactShadows.frag` beyond its header;
  `LightCompact.comp` body; `CascadeFit.comp` after line 40; `SH/Include/Atmosphere.slang` table mappings and phase
  function bodies; `AtmosphereMultipleScattering.comp`, `AtmosphereAerial.comp`, `AtmosphereCube.comp`,
  `AtmosphereTransmittance.comp` bodies; `ProceduralSky.comp` after line 45; `Irradiance.comp`; `SceneRendererLocalShadows.cpp`
  beyond its constants (the `FindLocalShadowCasters`, `FitTileSizes` use, `CommitLocalShadows` logic); `ShadowAtlasAllocator.cpp`;
  `SceneRendererScreenShadows.cpp`, `SceneRendererShadowView.cpp` and `SceneRendererLightingView.cpp` bodies;
  `GatherShadowDraws`, `PrepareShadowCache`, `GetCascadeMask`; the GPU-driven shadow culling (`Cull.comp`'s shadow
  phases, `SceneRendererGPUDriven.cpp`); `R/RendererComponents.cpp` tooltips' full text; `SkyPresets.cpp` values beyond
  the DG table; the editor's Inspector Sky section; the test bodies (only their names and a few headers were read).
- **Exposure metering details** (`Exposure.comp`, `Histogram.comp`, exposure key math) were skimmed only; they are the
  post-processing area's.
- **Why forward (clustered) rather than deferred** is not stated in the documents read; the book needs the authors' reason
  or must present it as a trade-off without attributing a motive.
- **Release of the horizon fade** is not stated in the documents (the 0.7.0-era Manual paragraph mentions it; DG does not
  date it).
- **Whether contact shadows ever were on in a shipped preset**: 0.7.0 release notes say High and Ultra drew them; 0.8.0
  (main) turned them off. Confirmed by DG 4614 and `R/RendererQuality.cpp:49`, but the 0.7.0 row values were not checked in
  history.
- **Area lights**: only branch commit subjects were seen (`agent/wave8-area-lights`); the design, components and shader
  changes are unknown. Wave 8's `local-lights` stream (more than 16 shadowed lights, tile lifetime, fixed local noise,
  scheduler) is on `agent/wave8-local-lights`, also not merged: chapter 9's numbers (16 lights, 12 views per frame, turning
  noise) may change. The `volumetric` stream (shafts and cones in fog, `Docs/Plans/Wave8/plan.md:867-899`) and the
  `showcase-engine` blended layer and wetness (`plan.md:900-916`, a change to `MaterialData`'s 144 bytes) are planned, not
  on main.
- **Which samples show which features** was checked only by grepping scene files (Showcase Outpost: atmosphere, height
  fog, six point lights; Physics Playground: atmosphere; Third-Person: two point lights with shadows); the Open World's
  world cells were not inspected. Screenshot plans for Open World rely on the 0.6.0 and 0.7.0 release notes.
- **Exact screenshot reproducibility**: whether `viewport.capture` can set `SpecularAntiAliasing` or force a cascade count
  of 4 at High was not checked (both are specification fields or Custom quality rows); some "before/after" shots may need
  a modified build.
- **Docs drift**: ML's shadows table (3/4/4/4 cascades) disagrees with the code (3/4/5/5); ML's "at most 16 shadowed
  lights" ignores Low's 4. Not verified which document the maintainers consider current beyond the code.
