---
id: gpu/frame-tour
title: "A frame of the scene renderer, pass by pass"
description: "What SceneRenderer::Render does with a scene and a camera, pass by pass, and the rule that a feature turned off is invisible bit for bit and costs nothing."
kind: internals
size: XL
tracks: [E]
needs: [gpu/coordinates, gpu/binding, gpu/geometry-pool]
time: 100
learn:
  - id: passes-order
    text: name the passes of a frame in the order the renderer records them and the stage that times each
  - id: equal-invariant
    text: explain why the opaque pass needs the prepass's positions to the bit
  - id: off-rule
    text: explain what a feature that is off must leave in a frame
  - id: target-rules
    text: choose the size and format of a target that Render accepts
  - id: trace-pass
    text: trace a pass from its marker to its stage and its switch
since: 0.3.0
status: final
---

You give the engine a scene and a camera, and it hands back one picture. `SceneRenderer::Render` is the function that does this work for every view in Strata: the game window, the editor's Scene view, a thumbnail. It records one long list of graphics commands, in a fixed order, and submits the list to the :term[graphics processing unit]{id=gpu} (GPU). This page walks that list from the first check to the last overlay. It does not teach each effect, because every pass names the page that does; it teaches the order, what each pass reads and writes, and the rules that keep the passes consistent.

## The problem and how engines solve it

Think of one frame at 1920 by 1080 pixels. That is 2,073,600 pixels, and the engine must decide the color of each one in about 16.7 ms. The expensive part of that decision is shading: the program that works out how a surface looks under every light, with its textures, its shadows and the sky around it. Every design in this section is a way to run that program as few times as possible while keeping the answer correct.

### Forward rendering and its two costs

The plainest design draws each mesh and shades its pixels at once. A **forward** :term[renderer]{id=renderer} shades a pixel in the same pass that draws the surface covering it. It needs no memory beyond the picture and the :term[depth buffer]{id=depth-buffer}, and it treats glass and every material in the same way.

Forward rendering has two costs. The first is wasted shading. Suppose a street scene has, on average, three surfaces covering each pixel: a wall, a car in front of it and a lamp in front of the car. The depth test keeps only the nearest surface, but if the wall is drawn first, its pixels were already shaded. Three layers on every pixel mean 6,220,800 shading runs, where 2,073,600 would give the same picture.

Drawing the nearest meshes first helps, but no order is right from every camera position. The second cost is lights. A shading program that loops over every light in the scene costs time in proportion to the light count, for every pixel, even when a light is far away and reaches nothing. A hundred lights make every pixel pay for a hundred.

### The depth prepass

The cure for wasted shading is to separate two questions: which surface is nearest, and what color is it? A **depth prepass** draws every opaque mesh first with a tiny program that writes only depth, and whatever small facts later passes need. The depth buffer then holds the nearest surface at every pixel. The shading pass then draws the meshes again and keeps a pixel only where its own depth equals the stored one, an **EQUAL depth test**. Each pixel is shaded once, for the surface that is truly in front.

The prepass is cheap, because its program is small and it writes no colors. It also gives other effects what they need before shading starts: a depth image to find shadows in, to estimate occlusion from and to find a surface's normal from. Strata's whole frame is built on it.

### Many lights: clusters

To stop every pixel paying for every light, an engine sorts lights by where they reach. **Clustered forward** shading cuts the camera's view into a grid of boxes, called clusters, finds which lights touch each box, and stores a short list per box. A pixel reads the list of its own box and loops only over those lights. The page on [many lights](../light/many-lights.md) teaches the grid. Here you need only that compute :term[shaders]{id=shader} build the grid before the shading pass.

### Deferred rendering and visibility buffers

A different cure splits the work the other way. A **deferred** renderer first draws all meshes into several image-sized targets, together called the G-buffer, which hold for every pixel the facts that shading needs: base color, normal, roughness and so on. A later pass shades each pixel once from those facts, and the lights become a loop over the screen instead of a loop inside every material.

Deferred shading has costs. At 1920 by 1080, a G-buffer of four 4-byte color targets and a 4-byte depth buffer is 20 :term[bytes]{id=byte} per pixel, or 41,472,000 bytes (41.5 MB) that every frame writes and then reads again. Transparent surfaces cannot live in a G-buffer, since one pixel holds one surface, so they need a forward pass anyway. And every material must fit the same stored facts.

A visibility buffer goes one step further. Its first pass stores only which triangle covers each pixel, and a later pass fetches that triangle's data and shades. It saves memory and shading work, and it asks much more of the shader, which must rebuild every surface from a triangle number. The table compares the four designs.

| Design | Shading runs per pixel | Memory beyond the picture | Many lights | Main cost |
| --- | --- | --- | --- | --- |
| Forward | One per covering surface | None | A loop over all lights, slow | Wasted shading and light count |
| Forward with a depth prepass | One | Depth, drawn twice | The same as forward | Every opaque mesh is drawn twice |
| Clustered forward with a prepass | One | Depth, extra targets, light lists | A short list per cluster | Drawing twice; building the clusters |
| Deferred | One | About 20 bytes per pixel at 1080p | A loop over the screen, cheap | Memory traffic; no blending in the G-buffer |
| Visibility buffer | One | A triangle number per pixel | Cheap | A heavy shading program |

Strata uses clustered forward with a depth, normal and entity identifier (ID) prepass, and an opaque pass that tests depth for equality. The engine's own documents say what the design is and how it works. They give no reason for choosing it over a deferred design, and this page does not invent one. Judge it by the trade in the table: it gains blending that works the same for every surface, a depth and normal image before shading starts, and no per-pixel material record to store. It pays by drawing every opaque mesh twice, and by demanding one rule of the shaders: the two draws must agree to the last bit.

## The map

The frame is one :term[command list]{id=command-list}, and the renderer divides it into GPU stages: named intervals that the profiler times (the page on [GPU timing](readback-timing.md) teaches how). The renderer calls `gpuTimer.Next(stage)` between passes, and each stage runs from its first command to the next call. A stage whose pass does not run is never started, so it has no time. The profiler writes each name with the prefix GPU and a dot.

```mermaid caption="The frame from top to bottom. Each box is a stage of the profiler; its words name the passes timed in it and the stages that run only on some frames." alt="A vertical sequence of boxes in recording order. Checks, extraction and constants come first, on the processor. Then come setup, culling, the haze volume, shadows and the prepass. Screen-space passes and the opaque pass follow, then transparent surfaces, temporal and post passes, and overlays last."
flowchart TB
	subgraph Cpu["On the processor, before recording"]
		K1["Checks, scene sync, scene mirror on the card, constants"]
	end
	subgraph Setup["Setup"]
		S1["Environment, fog, tables; light culling and clusters on CPU-path frames"]
	end
	subgraph Cull["Cull: GPU-driven frames only"]
		C1["Scene culling; light culling and clusters"]
	end
	subgraph Aerial["Aerial: atmosphere skies only"]
		A1["Haze volume"]
	end
	subgraph Shadows["Shadows: when a light casts"]
		H1["Sun cascades; local light shadow tiles"]
	end
	subgraph Prepass["Prepass"]
		P1["Clears; depth, normals, entity IDs"]
	end
	subgraph Screen["Screen shadows, AO, GI, Reflections"]
		R1["Read depth and normals; write masks, occlusion, voxels, reflections"]
	end
	subgraph Opaque["Opaque"]
		O1["Equal-depth pass into the HDR target; then the sky"]
	end
	subgraph Transparent["Transparent"]
		T1["Color copy; glass; blended surfaces"]
	end
	subgraph Post["TAA, DepthOfField, MotionBlur, Post"]
		X1["Resolve; defocus; blur; exposure, bloom, flares; tone mapping"]
	end
	subgraph Overlays["Overlays"]
		V1["Debug views, grid, outline, text, game UI; copy into the target"]
	end
	Cpu --> Setup --> Cull --> Aerial --> Shadows --> Prepass --> Screen --> Opaque --> Transparent --> Post --> Overlays
```

The prepass writes three targets and the opaque pass writes one, and every later pass reads some of them. The second diagram follows the targets of one view. The editor has no debug view that shows raw depth, normals or entity IDs, so a diagram stands in for the pictures.

```mermaid caption="The targets of one view. The prepass fills depth, normals and entity IDs; the passes after it read them and add light to the color target, which the post chain turns into the display image." alt="A flow diagram from left to right. The prepass writes depth, normals and entity IDs. Screen-space passes read depth and normals and write masks. The opaque pass reads the masks and depth and writes the color target, which the transparent pass changes. The post chain writes the display image, overlays draw over it, and picking reads the entity IDs."
flowchart LR
	pre["Prepass"] --> depth["Depth"]
	pre --> nrm["Normals"]
	pre --> ids["Entity IDs"]
	depth --> ss["Screen-space passes"]
	nrm --> ss
	ss --> masks["Masks: shadow, occlusion, reflection"]
	masks --> opq["Opaque pass"]
	depth --> opq
	opq --> hdr["HDR color"]
	hdr --> trn["Transparent pass"]
	trn --> hdr
	hdr --> post["Post chain"]
	post --> out["Display image"]
	out --> ovl["Overlays"]
	ids --> pick["Picking and outlines"]
```

The code is spread over a handful of files. All the renderer's members are declared in one :term[header]{id=header}, `Strata/src/Strata/Renderer/SceneRenderer.h`, grouped under a comment that names the file that defines them. The table lists the files.

| File in `Strata/src/Strata/Renderer/` | What it holds |
| --- | --- |
| `SceneRenderer.cpp` | The frame itself, `RenderFrame`, and what its passes share |
| `SceneRendererPost.cpp` | Depth of field, motion blur, exposure, bloom, flares, tone mapping, anti-aliasing |
| `SceneRendererAmbientOcclusion.cpp` | Ambient occlusion and its filter |
| `SceneRendererScreenShadows.cpp` | The sun's screen-space shadow mask |
| `SceneRendererLocalShadows.cpp` | Point, spot and rectangle light shadows |
| `SceneRendererAreaShadows.cpp` | The rectangle lights' screen-space shadow masks |
| `SceneRendererScreenReflections.cpp` and `SceneRendererReflectionProbes.cpp` | Screen-space reflections and probe conversions |
| `SceneRendererAtmosphere.cpp` | Atmosphere tables and the haze volume |
| `SceneRendererGlobalIllumination.cpp` | Voxel global illumination |
| `SceneRendererGlass.cpp` | Glass |
| `SceneRendererExtraction.cpp` and `SceneRendererGPUDriven.cpp` | Gathering what to draw, and culling on the card |
| `SceneRendererLightingView.cpp` and `SceneRendererShadowView.cpp` | The debug views of lighting and shadows |
| `SceneRendererGeometryViews.cpp` | The **Wireframe** and **Culled** debug views |

The pattern is one feature, one file, one call in `RenderFrame`. A feature's new pass goes into its own file, and `RenderFrame` calls it and times it in its GPU stage.

## The contract

Callers of `SceneRenderer` may rely on the following rules, and must obey them. Each has its reason.

- **One renderer, one viewport.** `SetViewportSize(width, height)` sizes every internal target at once. A size above the device's texture limit, or a failed allocation, is logged, and `Render` then fails until a valid size is set. A size of 0 releases the targets, which is what a hidden view wants. The old targets go through `Renderer::ReleaseDeferred`, because frames still on the card may read them ([resources and their lifetimes](resources-lifetimes.md) teaches why).
- **Call `SetQuality` after `SetViewportSize`.** Some quality rows depend on the viewport, such as a shadow map size set to Auto, and they resolve for the rows the frame draws at. `SetQuality` remakes only what a changed row sizes. It returns whether it released the cascades or the local shadow atlas, and the temporal history then starts again.
- **`Render(scene, camera, target, options)` returns a bool.** True means a picture exists. False means nothing was drawn: an empty viewport, an invalid target, or render targets that are unavailable. The function logs the reason once and leaves `GetStats().Rendered` false. It never changes the picture's size and never throws.
- **Main thread only.** Rendering is submitted from the thread that owns the scene.
- **Resets belong to the caller.** `ResetExposureAdaptation` makes the next frame jump to the scene's brightness, and `ResetHistory` starts the temporal history again. A caller that loads another scene or cuts the camera calls them.

:::rule[Targets have the viewport's size and a fixed format]
A `target` passed to `Render` must have exactly one color attachment, one sample per pixel, the viewport's size and a format of unsigned :term[normalized]{id=normalization} (:term[UNORM]{id=unorm}) values that is not :term[sRGB]{id=srgb}. `Render` returns false and logs instead of changing the size. The reason is in the display transform below: the shaders write values that are already sRGB-encoded, so an sRGB target would encode them twice. See the [renderer reference](../reference/renderer.md) for the options.
:::

The outputs of a renderer are textures it owns. With no `target`, the picture is in `GetOutputTexture()`, which is `RGBA8_UNORM` with sRGB-encoded values and is made by the first frame that needs it. Beside it stand `GetHDRTexture()`, `GetDepthTexture()`, `GetNormalTexture()` and `GetEntityIDTexture()`, which is null without entity IDs. A renderer that draws only into targets, and composes no overlay or text, never makes the output texture at all.

### Options, statistics and callers

`SceneRenderOptions` carries what differs between views, and its defaults draw a scene exactly as a game shows it. The editor sets `PreviewEnvironment` to light a scene that has no light. It hides the game's user interface (UI) with `DrawScreenSpaceText`, and it enables `ShowGrid`, outlines and the lighting views. Tools use `MotionVectors`, `PreExposure` and `HDROutput`. With the last, the frame ends with its image in :term[high dynamic range]{id=high-dynamic-range} (HDR), accepts no target and applies no exposure, tone mapping or overlay.

After a frame, `GetStats()` answers at once with what the :term[central processing unit]{id=processor} (CPU) did: the lights, the proxy updates, the pre-exposure, the jitter, whether temporal anti-aliasing (TAA) ran. It also counts the rectangle lights among the lights (`AreaLights`), the local shadows that fade in or out (`LocalShadowFading`), and whether the forward pass read the global illumination (GI) field (`GlobalIlluminationShaded`). `GetGPUStats()` answers with GPU times that are two or three frames old, because the card finishes late. `ResolveGPUStats(true)` waits for them; use it in tests and tools only.

The simplest caller is `GameRenderer::Render` in `Strata/src/Strata/Runtime/GameRenderer.cpp`. It sets the viewport size, applies the project's quality through `SetQuality`, and finds the :term[primary camera]{id=primary-camera}: the first active entity, in hierarchy order, whose camera is marked Primary. It builds a `SceneCamera` from that entity and calls `Render` with the :term[back buffer]{id=back-buffer} as the target. When a new scene appears, it calls both resets.

The renderer makes no entity ID buffer for a game, since a game does not pick. The editor's `ViewportRenderer` and `ThumbnailCache` call the same function with other cameras and options. The [coordinates page](coordinates.md) teaches what a `SceneCamera` holds: a :term[reversed-Z]{id=reversed-z} projection and a position.

### A feature that is off is invisible and free

The renderer's most important rule appears in every feature page. When a feature is off, the frame must be bit for bit the frame the renderer drew before the feature existed, and the feature must cost nothing. No target is made for it, no GPU stage is timed for it, and any shader input it would read is bound to a dummy. "Bit for bit" means the stored colors are identical, not close.

The renderer's own code shows the rule. It makes a 1 by 1 dummy shadow array, named `NoShadows`, for shaders to bind when no shadow map exists. A comment at the global illumination join says that without the field, the indirect light is Strata 0.7.0's, bit for bit. The forward shaders keep the rectangle lights' code and the field's gather in separate forms, chosen by `AreaLights` and `Field` of the pipeline's key, and only frames that need them draw with those forms. The shadow, ambient occlusion and reflection passes each sit inside an `if`, so a frame without them starts no timer for them.

:::why[Why bit for bit, and not almost]
A pass that changes the default picture by one rounding makes every exact-pixel test and every saved comparison image suspect, and the cause is hard to find because nothing looks wrong. Bit for bit gives tests a clean claim: with the feature off, the output equals the output of a renderer without the code. The cost is care: a shader that tests a flag in a :term[uniform branch]{id=uniform-branch} must leave the arithmetic of the default path alone. A developer may not rewrite the default expression "while there", because the same additions in another order round differently. Several tests compare an off feature with a disabled one, for example the fog suite's check that a scene renders the same without fog, with a disabled one and with one of density 0.
:::

## A toy frame

Before the real code, here is a frame at the smallest size that keeps the ideas. The toy screen is 12 pixels wide and 4 high. Two flat quads cover it: a far one over columns 0 to 8 and a near one over columns 5 to 11, so columns 5 to 8 are covered twice. The toy keeps the engine's reversed-Z rule: a larger depth is nearer, and the depth buffer is cleared to 0.

A fragment is one surface's claim on one pixel: the shader runs once per fragment that passes the depth test.

The program draws the frame three ways. First it runs a forward pass alone, which tests depth with greater-or-equal and writes it. Then it runs a prepass and a forward pass that tests for equality, and a third run gives the forward pass another depth formula that is equal on paper. At the end, a post pass tone maps one row. Search the output for the shading counts and for the word "holes".

```cpp sketch="gpu-frame-tour-toy.cpp"
#include <cstdio>
#include <vector>

// A toy frame on a 12 by 4 screen: a prepass, a forward pass and one post pass. Reversed-Z: a larger depth is nearer,
// and the depth buffer is cleared to 0, the far plane.
namespace
{
	constexpr int c_Width = 12;
	constexpr int c_Height = 4;

	struct Quad
	{
		int X0, X1; // Columns covered, X1 exclusive
		float Depth;
		float Brightness;
	};

	struct Frame
	{
		std::vector<float> Depth = std::vector<float>(c_Width * c_Height, 0.0f);
		std::vector<float> Color = std::vector<float>(c_Width * c_Height, 0.05f); // The clear color
		int Shaded = 0; // Fragments the expensive shader ran for
	};

	enum class Mode
	{
		DepthOnly, // The prepass
		Forward,   // A forward pass that tests greater-or-equal and writes depth
		Equal      // A forward pass after a prepass: shades only where the depth is equal
	};

	// The vertex math: the same formula in both passes, or a rearranged one that is equal on paper.
	float QuadDepth(const Quad& quad, int x, bool rearranged)
	{
		const float column = static_cast<float>(x);
		return rearranged ? quad.Depth * 0.3f + 0.0003f * column : (quad.Depth + 0.001f * column) * 0.3f;
	}

	void Draw(Frame& frame, const std::vector<Quad>& quads, Mode mode, bool rearranged)
	{
		for (const Quad& quad : quads)
			for (int y = 0; y < c_Height; y++)
				for (int x = quad.X0; x < quad.X1; x++)
				{
					float& stored = frame.Depth[y * c_Width + x];
					const float depth = QuadDepth(quad, x, rearranged);
					if (mode == Mode::Equal ? depth != stored : depth < stored)
						continue;
					if (mode != Mode::Equal)
						stored = depth;
					if (mode == Mode::DepthOnly)
						continue;
					frame.Shaded++;
					frame.Color[y * c_Width + x] = quad.Brightness;
				}
	}

	void Report(const char* name, const Frame& frame)
	{
		int holes = 0;
		for (float value : frame.Color)
			holes += value == 0.05f ? 1 : 0;
		std::printf("%s %d fragments shaded, %d holes\n", name, frame.Shaded, holes);
	}
}

int main()
{
	// The far quad is drawn first, the near quad over it: the worst order for a forward pass alone.
	const std::vector<Quad> quads = { { 0, 9, 2.0f, 1.0f }, { 5, 12, 3.0f, 4.0f } };

	Frame forwardOnly;
	Draw(forwardOnly, quads, Mode::Forward, false);
	Report("forward only:        ", forwardOnly);

	Frame withPrepass;
	Draw(withPrepass, quads, Mode::DepthOnly, false);
	Draw(withPrepass, quads, Mode::Equal, false);
	Report("prepass, same math:  ", withPrepass);

	Frame mismatched;
	Draw(mismatched, quads, Mode::DepthOnly, false);
	Draw(mismatched, quads, Mode::Equal, true);
	Report("prepass, other math: ", mismatched);

	std::printf("post pass, top row:  "); // Tone mapping: x / (1 + x) maps any brightness into 0 to 1
	for (int x = 0; x < c_Width; x++)
		std::printf(" %.2f", withPrepass.Color[x] / (1.0f + withPrepass.Color[x]));
	std::printf("\n");
	return 0;
}
```

```text output-of="gpu-frame-tour-toy.cpp"
forward only:         64 fragments shaded, 0 holes
prepass, same math:   48 fragments shaded, 0 holes
prepass, other math:  28 fragments shaded, 20 holes
post pass, top row:   0.50 0.50 0.50 0.50 0.50 0.80 0.80 0.80 0.80 0.80 0.80 0.80
```

1. **Line 18:** The `Frame` holds the depth buffer, cleared to 0, and the color buffer, cleared to the clear color, with a count of the fragments that the expensive shader ran for.
2. **Lines 33–36:** The vertex math. The flag `rearranged` picks a formula that is equal to the first on paper but orders its float operations differently.
3. **Line 47:** The only test. The second pass of a prepass frame passes where the depth is equal; every other draw passes where the depth is greater or equal.
4. **Line 50:** Depth is written by every draw except the equal pass, which keeps the prepass's values.
5. **Line 83:** The third run draws the prepass with one formula and the equal pass with the other.

The numbers teach three things. The forward pass alone shades 64 fragments, because the far quad's pixels in columns 5 to 8 were shaded before the near quad covered them: 16 shaded per row where 12 are visible, 4 rows. The prepass run shades 48, one for each of the 12 visible pixels in each row, with no holes. The saving is 25 %, and a real scene with three layers saves much more.

The last run is the danger. The two depth formulas differ only in the order of their float operations, yet 5 visible pixels per row, 20 in all, fail the equality test, shade nothing and show the clear color. These holes are in front of everything and are still not drawn. A smaller tolerance on the test is not the fix. The fix is that the prepass and the forward pass compute positions the same way, and that the hardware keeps the result identical.

The post pass at the end has the same shape as the real one. It applies a function to the lit value, here `x / (1 + x)`, that maps any brightness into the range 0 to 1.

## The real frame, in order

The rest of the page follows `SceneRenderer::RenderFrame` in `Strata/src/Strata/Renderer/SceneRenderer.cpp` from its first line to its last. The function is about 930 lines long. The steps below group it into 24, numbered from 0, so you can match them to the diagram and to a capture. For each pass you get what it does, the page that teaches it and the GPU stage that times it.

### Steps 0 to 3: checks, extraction and constants

Step 0 resolves the GPU statistics of earlier frames and resets this frame's. A viewport of 0 by 0 returns false quietly, since a minimized window is not an error. Invalid render targets, an invalid `target`, or a `target` together with `HDROutput` report an error and return false. These checks run before any command is recorded, so a failure leaves nothing half done.

Step 1 brings the scene's render proxies up to date. `RenderScene::Sync` follows what changed since the last frame, and the extraction preparation begins; the profiler times it as a CPU stage. [The render scene](../draw/render-scene.md) teaches proxies and extraction.

Step 2 updates the card's copy of the render scene, in a command list of its own that runs before the frame's. Only proxies the copy holds are drawn, so a mesh that has not finished loading is not there yet, or is drawn with a fallback.

Step 3 is the long CPU stretch. It collects lights, resolves assets, builds the draw arguments and fills the frame constants. Two details matter for later passes. The :term[view matrix]{id=view-matrix} is camera-relative: the camera's translation is omitted, and shaders work with positions measured from the camera.

The jitter goes only into this frame's copy of the projection. The CPU chooses levels of detail with the camera's own matrices, and so do the motion vectors, so a camera that did not move gives the same matrix twice. [TAA](../image/taa.md) teaches the jitter, a Halton sample that repeats every 8 frames.

### Steps 4 and 5: the command list and the first stage

The next lines open the command list and start the timer. Look at three things: the list opens before any command, `beginMarker` names the whole frame after the renderer's `DebugName`, and the timer starts in the `Setup` stage.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3473-L3479" from="nvrhi::ICommandList* commandList = m_CommandList;" to="GPUPassTimer gpuTimer(commandList, gpuStages.Setup, &BeginGPURecord());" symbol="SceneRenderer::RenderFrame"
nvrhi::ICommandList* commandList = m_CommandList;
ReserveFrameConstantVersions();
commandList->open();
commandList->beginMarker(m_Specification.DebugName.c_str());
// The GPU's time per pass: each stage runs from its first command to the next stage's.
const RendererGPUStages& gpuStages = RendererGPUStages::Get();
GPUPassTimer gpuTimer(commandList, gpuStages.Setup, &BeginGPURecord());
```

Everything recorded until the next `Next` call counts in `Setup`: the environment (image-based lighting, the procedural sky or the atmosphere's tables), the height fog, the haze setup, the :term[texture table]{id=texture-table-strata} uploads and the geometry tables. The binding sets are made again when a buffer was recreated, as the page on [binding](binding.md) explains. The geometry comes from the pool that the page on the [geometry pool](geometry-pool.md) describes.

### Steps 6 to 8: culling, light clusters and the haze volume

On a GPU-driven frame, `gpuTimer.Next(gpuStages.Cull)` has run, and compute shaders do the scene's culling ([GPU-driven rendering](../draw/gpu-driven.md) teaches it). The quote starts after that. Look at which stage each pass is timed in: the light passes call no `Next`, and only the haze pass does.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3561-L3578" from="if (m_GPULightsFrame && frame.LightCounts.x > 0)" to="RenderAerialPerspective(commandList, camera);" symbol="SceneRenderer::RenderFrame"
if (m_GPULightsFrame && frame.LightCounts.x > 0)
{
	commandList->beginMarker("LightCull");
	RunGPULightCulling(commandList, camera);
	commandList->endMarker();
}
if (frame.LightCounts.x > 0)
{
	commandList->beginMarker("LightClusters");
	BuildLightClusters(commandList);
	commandList->endMarker();
}
// After the frame's constants and the atmosphere's tables; the next stage's start ends its interval.
if (m_AerialFrame)
{
	gpuTimer.Next(gpuStages.Aerial);
	commandList->beginMarker("Aerial");
	RenderAerialPerspective(commandList, camera);
```

1. **Line 3561:** The light passes record only when the frame has lights, so a scene without lights pays nothing for them.
2. **Lines 3564–3570:** Neither light pass calls `Next`. Both join the stage that is already running.
3. **Lines 3574–3576:** The haze pass starts its own stage inside its `if`, so without an atmosphere no `Aerial` time exists.

The light culling and the cluster build take the stage that is already running: `Cull` on a GPU-driven frame, and `Setup` on a frame of the CPU path, which never starts `Cull`. A document that lists the light passes under `Cull` alone is wrong for the CPU path. Both passes run only when the frame has lights, which is the off rule again: no lights, no clusters, no time.

The aerial perspective volume is a small 3D texture of haze that atmosphere skies use. It gets its own stage, `Aerial`, and runs only when `m_AerialFrame` is set. A scene without an atmosphere shows no `Aerial` time, and the [atmosphere page](../light/atmosphere.md) teaches the volume.

### Steps 9 and 10: shadows, clears and the prepass

Step 9 draws the sun's shadow cascades and the shadow tiles of point, spot and rectangle lights, under the `Shadows` marker, in the `Shadows` stage. It starts `FitCascades`, then `DrawShadows` (or `DrawGPUShadows` on the GPU-driven path). Inside `LocalShadows`, it clears the tiles no light needs, draws the local views and builds their depth ranges. A rectangle light's views also draw its back faces into a second atlas, and its soft shadow reads both. The step runs only when the sun casts a shadow or local work waits: a view to draw, a tile to clear or new ranges.

[Sun shadows](../light/sun-shadows-1.md) and [lights](../light/lights.md) teach what goes in the cascades and the tiles. The shadow map draws push their stored depth away from the light, and they never touch the camera's depth buffer.

Step 10 starts the `Prepass` stage and clears the targets before anything draws. In the quote, look at what each clear writes, and at the two phases of the GPU-driven prepass.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3620-L3645" from="gpuTimer.Next(gpuStages.Prepass);" to="DrawBatches(commandList, Pass::Prepass, false);" symbol="SceneRenderer::RenderFrame"
gpuTimer.Next(gpuStages.Prepass);
const glm::vec4 clear = camera.ClearColor;
commandList->clearDepthStencilTexture(m_DepthTexture, nvrhi::AllSubresources, true, 0.0f, false, 0);
commandList->clearTextureFloat(m_NormalTexture, nvrhi::AllSubresources, nvrhi::Color(0.0f));
if (m_EntityIDTexture)
	commandList->clearTextureUInt(m_EntityIDTexture, nvrhi::AllSubresources, 0);
if (m_MotionFrame)
	commandList->clearTextureFloat(m_VelocityTexture, nvrhi::AllSubresources, nvrhi::Color(0.0f));
// The clear color is a luminance too: pre-exposed like everything drawn over it.
commandList->clearTextureFloat(m_HDRTexture, nvrhi::AllSubresources,
	nvrhi::Color(SRGBToLinear(clear.r) * m_PreExposure, SRGBToLinear(clear.g) * m_PreExposure, SRGBToLinear(clear.b) * m_PreExposure, 1.0f));

commandList->beginMarker("Prepass");
if (m_GPUDrivenFrame)
{
	DrawGPUView(commandList, Pass::Prepass, 0, m_CullConstants.FirstPhaseViewBuckets);
	if (IsOcclusionCulled())
	{
		// What the first phase did not draw, found visible against its depth, in the same frame.
		RunOcclusionPhase(commandList);
		DrawGPUView(commandList, Pass::Prepass, m_CullConstants.FirstPhaseViewBuckets, m_CullConstants.ViewBucketCount);
	}
	RecordCullReadback(commandList);
}
else
	DrawBatches(commandList, Pass::Prepass, false);
```

1. **Line 3620:** The `Prepass` stage starts here, so everything before it in the frame is timed in earlier stages.
2. **Line 3622:** Depth is cleared to 0, the :term[far plane]{id=far-plane} under reversed-Z, and not to 1.
3. **Lines 3629–3630:** The clear color is converted to linear light and multiplied by the pre-exposure.
4. **Lines 3635–3640:** The GPU-driven path draws a first phase, then finds what that phase missed, and draws it as a second phase.
5. **Line 3645:** The CPU path draws the prepass in one call.

The clears show the data the frame uses. Depth is cleared to 0, the :term[far plane]{id=far-plane} under reversed-Z. Normals and entity IDs clear to 0, which means "no entity" for the IDs. The color target is cleared to the camera's clear color, converted from sRGB to linear and multiplied by the pre-exposure, because the clear color is a light value like every other.

The pre-exposure is a scale the frame applies to all its light values, and the HDR section below explains it. The CPU path then draws the prepass with `DrawBatches`, and the GPU-driven path draws it in two phases: the second finds, against the first phase's depth, what the culling of the first phase wrongly removed.

The prepass is where the **entity ID buffer** is made: a render target of 32-bit :term[unsigned integers]{id=unsigned-integer} that stores, for each pixel, the number of the entity whose surface is in front. The value 0 means no entity. The editor reads one pixel of it to learn which object is under the mouse, and the outline pass reads it to find silhouettes. A renderer without the buffer picks nothing, which is why `GameRenderer` omits it.

The three prepass targets have the formats in the code: depth is `D32`, the normal is `RG16_FLOAT` and the entity ID is `R32_UINT`. At 1920 by 1080 that is 12 bytes a pixel, 24,883,200 bytes (24.9 MB), against 20 bytes for the G-buffer above. A frame with motion vectors, or with screen-space reflections, adds attachments after these.

### Why the opaque pass tests for equality

The pipeline's key picks the depth test of each pass. The quote shows the choice for the passes of one switch. Look at the `Prepass` and `Opaque` cases, and at the shadow passes between them: the passes of the shadow maps write depth with a bias, and the back-face passes write it without one.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L2566-L2592"
// Reversed-Z: nearer surfaces have larger depth values.
nvrhi::DepthStencilState& depth = desc.renderState.depthStencilState;
depth.setDepthTestEnable(true);
switch (key.PassType)
{
	case Pass::Prepass:
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		break;
	case Pass::Shadow:
	case Pass::ShadowMasked:
	case Pass::LocalShadow:
	case Pass::LocalShadowMasked:
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		// Push stored depth away from the light against shadow acne. NVRHI enables the depth bias only with a
		// non-zero constant part, which also keeps the slope part working.
		desc.renderState.rasterState.setDepthBias(c_ShadowDepthBias).setSlopeScaleDepthBias(c_ShadowSlopeDepthBias);
		break;
	case Pass::LocalShadowBack:
	case Pass::LocalShadowBackMasked:
		// Where the back faces are, unbiased: the filter counts a path's point as inside a solid only before the back face,
		// so a bias toward the light thins the solids the paths at a box's foot cross, and one away from it thickens
		// them into the space beside. No acne follows: the filter never compares a receiver with the back faces alone.
		depth.setDepthWriteEnable(true).setDepthFunc(nvrhi::ComparisonFunc::GreaterOrEqual);
		break;
	case Pass::Opaque:
		depth.setDepthWriteEnable(false).setDepthFunc(nvrhi::ComparisonFunc::Equal);
		break;
```

1. **Lines 2571–2572:** The prepass writes depth and passes where the depth is greater or equal.
2. **Lines 2574–2582:** The shadow passes use the same test and add a depth bias against shadow acne.
3. **Lines 2583–2589:** The back faces of rectangle lights' views use the same test with no bias, because a bias would change the thickness of solids that the shadow filter measures.
4. **Lines 2590–2591:** The opaque pass writes no depth and passes only on equal.

The prepass writes depth with greater-or-equal, so nearer surfaces win, and the opaque pass writes no depth and passes only on equal. Between them they have the property the toy showed: a pixel is shaded for the surface the prepass kept and for no other. The fragment shader also forces early depth testing, so a failed pixel never runs the expensive program.

Equality of floats is the sharp part. The depth the opaque pass computes for a pixel must be the very number the prepass stored, to the last bit, so the vertex shader must produce the same clip-space position in both passes. An **invariant position** is a vertex shader output that the :term[compiler]{id=compiler} promises to compute identically in every shader that uses the same inputs and expressions. No :term[optimization]{id=optimization} may then rearrange the operations of one shader and not the other. In :term[Vulkan]{id=vulkan} the promise is the `Invariant` decoration on the position output.

Strata's shader language, :term[Slang]{id=slang}, has no way to write that decoration, so the shader build adds it. Each entry named in the `INVARIANT_POSITION` list of `strata_add_shaders` in `Strata/CMakeLists.txt` goes through `StrataShaderTool`. The tool inserts `OpDecorate %v Invariant` after the position's `BuiltIn` in the :term[SPIR-V]{id=spir-v} module. The entries are `Scene/Mesh.vert` and its variants. The tool fails the build if an entry is not a vertex shader or has no position output, so the guarantee cannot vanish quietly.

Two more facts follow from the rule. Both passes use the same vertex program variants: skinned meshes use the skinned variants in the prepass and in the forward pass. A frame with motion vectors uses the velocity vertex shaders in both, so that their depths agree (`PipelineKey` has `Skinned` and `Velocity` for this reason). The level-of-detail fade is also decided the same way in both passes. A developer who changes the position math of `Mesh.vert` for one pass alone makes holes of the kind the toy printed.

:::example[Counting the cost of the second draw]
Say shading one pixel costs 30 units and a prepass fragment costs 1 unit. Take the street scene of three layers on 2,073,600 pixels. Without a prepass, every covering fragment is shaded: 6,220,800 × 30 = 186,624,000 units.

With a prepass, all 6,220,800 fragments run the small program, 6,220,800 units, and only the 2,073,600 visible pixels are shaded: 62,208,000 units. The total is 68,428,800 units, 37 % of the first number, so the prepass saves 63 %. The costs are invented to show the shape. The engine's real costs depend on the scene, and its performance tests state budgets.
:::

### Steps 11 to 14: the passes that read the prepass

With depth and normals ready, four passes run before any color is shaded. Each has its own stage, and each is skipped when it is off.

Step 11 is the screen-space shadow masks, in `ScreenShadows`. For the sun, it evaluates the cascades' filter at every pixel of the prepass, adds contact shadows, and writes a two-channel target that the opaque pass reads; [sun shadows](../light/sun-shadows-1.md) teaches it. For each rectangle light with a shadow, at most 4, `RenderAreaShadowMasks` writes a mask from the local tiles, their depth ranges and their back faces. The stage runs when the sun has shadows or a rectangle light has a mask.

Step 12 is ambient occlusion, in `AO`, run when the scene's post-process settings ask for it; [ambient occlusion](../indirect/ao.md) teaches it. Step 13 is the voxel global illumination (GI), an experimental feature that runs only where a quality row above Off and the scene's setting ask for it. Its stage is named `RadianceCascades`, a name an earlier design gave it. If its work fails, the frame counts as degraded and the forward pass reads no field this frame. [Voxel GI](../indirect/gi-voxels.md) teaches it.

Step 14 converts reflection probes and traces screen-space reflections, in `Reflections`. It runs when probes need converting or a reflection trace is wanted, and [reflections](../indirect/ssr.md) teaches it.

### Steps 15 to 17: the opaque pass, the sky and the transparents

The opaque pass is short at this level. In the quote, look at how little code stands between the stage start and the draws.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3699-L3704" from="gpuTimer.Next(gpuStages.Opaque);" to="DrawBatches(commandList, Pass::Opaque, false);" symbol="SceneRenderer::RenderFrame"
gpuTimer.Next(gpuStages.Opaque);
commandList->beginMarker("Opaque");
if (m_GPUDrivenFrame)
	DrawGPUView(commandList, Pass::Opaque, 0, m_CullConstants.ViewBucketCount);
else
	DrawBatches(commandList, Pass::Opaque, false);
```

The pass starts its stage and draws the batches, either from the CPU's lists or by indirect draws that the culling wrote. Everything that makes it expensive is in the shader, `Forward.frag`: the surface, the lights in the pixel's cluster, the sun with its shadow mask, the image-based light, the reflections and the fog. The pass writes the color target and tests against the prepass depth. [Lights](../light/lights.md) teaches the lights, and [the surface model](../light/brdf.md) teaches the surface. A frame whose scene has a rectangle light draws with the forms of the shaders that shade such lights, and a frame that reads the GI field draws with the forms that gather it.

Step 16 draws the sky. It is one triangle that covers the screen, drawn at depth 0, the far plane, with the greater-or-equal test and no depth write. Pixels where a surface is in front have a larger depth and fail, and the cleared pixels pass. The sky therefore fills only the gaps, and Exercise 2 shows why the test must be greater-or-equal and not strictly greater. The sky and the opaque pass share the `Opaque` stage.

Step 17 starts `Transparent`. If a glass surface is in view, or the spatial reflections want it, the renderer first copies the image into a half-resolution texture with mip levels. Glass can then look at what lies behind it. Then it draws glass, and the blended surfaces after it, back to front. Blended surfaces write no depth, so the order of drawing matters for them and for nothing else.

### Steps 18 to 21: time, lens and the display

Step 18 copies the motion history for the next frame and, when the scene chose it, resolves temporal anti-aliasing, all in `TAA`. When the resources of TAA cannot be made, the frame uses fast approximate anti-aliasing (FXAA) instead. Step 19, depth of field, runs next in `DepthOfField`, only through a lens and only for perspective cameras. Step 20 is motion blur, in `MotionBlur`. The registration lists motion blur before depth of field, but the code runs depth of field first, and that is the order of the times.

Step 21 is the `Post` stage: exposure, bloom and lens flares (`RenderPostHDR`), then the color lookup, tone mapping and the final anti-aliasing (`RenderPostDisplay`). [The post chain](../image/why-post.md) teaches each effect. Here you need the foundation: what the HDR target is, and how it becomes a picture.

#### The HDR target and the display transform

A picture in high dynamic range (HDR) holds light amounts with no upper limit. The opaque and transparent passes write into one, in the format `RGBA16_FLOAT`: four channels of half float, a 16-bit :term[floating-point number]{id=floating-point-number} whose largest value is 65,504 ([color](../basics/color.md) teaches the format). The values are linear, so twice the light is twice the number. The renderer also multiplies them by the frame's pre-exposure, a power of two that it chooses, which scales a float exactly unless a value overflows. A wall in full sun can hold 50,000 while a shadowed corner holds 0.02, in the same image.

A screen cannot show 50,000. Tone mapping is the function that maps those linear values into the range 0 to 1 that a display can show, and it decides how highlights roll off. The toy's `x / (1 + x)` is the plainest such curve, and [tone mapping](../image/tone-mapping.md) teaches the engine's. Exposure comes before it: it scales the light so that an average scene lands in the middle of the curve.

The last step is sRGB encoding. Displays do not respond linearly to numbers, so images store values bent by a curve close to a power of 1/2.2, which spends more of the 8 bits on dark tones. Strata does this encoding itself, in the tone mapping shader: it clamps the value to 0 to 1 and calls `LinearToSRGB`. The intermediate image that anti-aliasing reads has the format `R10G10B10A2_UNORM` and holds sRGB-encoded values, and the output texture is `RGBA8_UNORM`.

The target rule in the contract has its reason here. With a UNORM target the hardware writes the number as given. With an sRGB target it would apply the curve a second time and brighten the picture. Encoding in the shader also lets the passes after tone mapping, such as the morphological anti-aliasing, convert back to linear light when they must blend.

### Steps 22 and 23: overlays, close and execute

Step 22 is `Overlays`. The overlays are drawn over the finished image with exact display colors, and they test against the scene's depth without changing it. They are the lighting and GI views (which replace the image), the **Wireframe** and **Culled** views, the grid, entity tints, the selection outline, debug lines, text and the game's UI. When temporal anti-aliasing ran, the overlays use the camera's own matrices, so lines stay steady. If a `target` was given and anything was composed in the output texture, the last pass copies the output into the target; otherwise the post chain wrote into the target directly.

Step 23 ends the timer, closes the command list and calls `ExecuteFrame`, which submits it. After that the renderer submits its readbacks (culling counters, exposure, shadow views), commits the shadow caches and sets `Rendered`. If nothing degraded, the error state clears. The failure paths between steps call the same close-and-execute sequence, so the uploads recorded so far are not lost.

The step table gathers the order, the stage and the page that teaches each part.

| Steps | What happens | Timed in | Taught on |
| --- | --- | --- | --- |
| 0 to 3 | Checks, sync, scene mirror, constants | The CPU, not a GPU stage | [render scene](../draw/render-scene.md), [TAA](../image/taa.md) |
| 4, 5 | Command list, environment, fog, tables | `Setup` | [binding](binding.md) |
| 6 | GPU culling (GPU-driven frames) | `Cull` | [GPU-driven rendering](../draw/gpu-driven.md) |
| 7 | Light culling and clusters | `Cull`, or `Setup` on the CPU path | [many lights](../light/many-lights.md) |
| 8 | Haze volume | `Aerial` | [atmosphere](../light/atmosphere.md) |
| 9 | Sun and local light shadows | `Shadows` | [sun shadows](../light/sun-shadows-1.md) |
| 10 | Clears and the prepass | `Prepass` | this page |
| 11 | Screen-space shadow masks | `ScreenShadows` | [sun shadows](../light/sun-shadows-1.md) |
| 12 | Ambient occlusion | `AO` | [ambient occlusion](../indirect/ao.md) |
| 13 | GI voxels | `RadianceCascades` | [GI voxels](../indirect/gi-voxels.md) |
| 14 | Probe conversion, reflections | `Reflections` | [reflections](../indirect/ssr.md) |
| 15, 16 | Opaque pass, sky | `Opaque` | this page |
| 17 | Color copy, glass, blended surfaces | `Transparent` | [lights](../light/lights.md) |
| 18 | Motion copy, TAA resolve | `TAA` | [TAA](../image/taa.md) |
| 19, 20 | Depth of field, motion blur | `DepthOfField`, `MotionBlur` | [post chain](../image/why-post.md) |
| 21 | Exposure to anti-aliasing | `Post` | [post chain](../image/why-post.md) |
| 22 | Overlays, copy into the target | `Overlays` | [debug drawing](debug-drawing.md) |
| 23 | Close and execute | none | this page |

### Looking inside a frame

Every `beginMarker` in `RenderFrame` opens a named group, and a graphics debugger that reads Vulkan's debug labels can show a capture as a tree of them. The names are the ones in the code. The renderer's `DebugName` names the whole frame. Inside it stand `Cull`, `LightCull`, `LightClusters`, `Aerial`, `Shadows` (with `LocalShadows` inside), `Prepass`, `ScreenShadows`, `AmbientOcclusion`, `GlobalIllumination`, `Reflections`, `Opaque`, `Sky`, `SceneColorCopy`, `Transparent`, `MotionCopy`, `TAA`, `DepthOfField`, `MotionBlur`, `LightingView`, `Overlays` and `Copy`. The GI views name their group `VoxelView` or `ProbeView` instead of `LightingView`.

To read a capture, find `Prepass` and look at its three attachments: depth in reversed-Z (near is bright), the two-channel normals, and the entity IDs as :term[integers]{id=integer}. Find `Opaque` and check that its depth state is equal and its target is the color target. Find the first group after `Opaque` that writes a UNORM target. That is the post chain, and the target before it holds values above 1. A missing group is information, not an error: the pass was off, and the step was skipped.

:::tip[Match the stage to the marker]
The marker names are not the stage names. `Sky` runs inside the `Opaque` stage, `SceneColorCopy` inside `Transparent`, and `MotionCopy` and `TAA` inside the `TAA` stage. When a profile says the `Opaque` stage is slow, look at both the `Opaque` and `Sky` groups.
:::

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Deferred shading with a G-buffer | Described in the book under Further reading | Lighting cost that does not depend on the scene's complexity | Blending, memory and traffic for the G-buffer, one material layout for all |
| Forward without a prepass | Described in the book under Further reading | Each mesh drawn once | The depth and normal images that shadows, occlusion and reflections read |
| Tiled forward (2D tiles) | Described in the 2012 paper on clustered shading | Simpler light lists | Depth-aware lists, so more lights per pixel in deep scenes |
| Visibility buffer | Described in the 2013 paper on visibility buffers | Little memory and no wasted shading | A shading program that rebuilds each surface from a triangle number |
| A render graph | Described in the 2017 conference talk on frame graphs | Passes that declare reads and writes, so barriers and memory follow | A new layer, and passes that today are ordered by hand |

The sources stand under Further reading. The choice among these is a trade, not a ranking: the table says what a change would cost, not that Strata's design is best.

### What Strata does not do here

Some things a reader may expect in a frame are absent at the pin.

- **Particles, trails and decals.** No effect of these kinds exists in the renderer. A search for `particle` or `decal` in `Strata/src` and `Strata/shaders` finds nothing, and the word `trails` appears only in help texts of the anti-aliasing settings. The file `Docs/Roadmap.md` lists them as a later item.
- **A render graph.** No frame graph exists. `RenderFrame` orders the passes by hand, as the code above shows, and each pass decides what it reads.
- **A second view.** A frame has one camera. No split-screen, picture-in-picture or camera that renders into a texture for a mirror or a map in a corner exists. The game's camera is the primary one, and [cameras and characters](../make/characters-cameras.md) tells makers how to switch.

## How it is tested

The renderer's tests that need a card are the `GPU.SceneRenderer` suites in `StrataTests/src/Renderer/`. They share one device through `Tests::GPUContext`. The file `GPUSceneRendererTests.cpp` holds the suite `GPU.SceneRenderer`, and these cases matter here:

- Lit meshes render, empty pixels show the clear color, and entities can be picked.
- The renderer draws into matching targets and rejects invalid ones.
- Rendering into a target makes the output texture only to compose overlays or text.
- Viewports beyond the device limit fail gracefully.
- A change of size right after a frame keeps the old targets until the card is done.

The off-means-invisible rule has its tests per feature. The file `GPUSceneFogTests.cpp` renders a scene without fog, with a disabled fog and with density 0, and compares the images. The file `GPUSceneDepthOfFieldTests.cpp` checks that the focus plane renders bit-identically to depth of field off. The invariant decoration has a test in the suite `Renderer.ShaderTool`, which checks that a vertex shader's position is decorated once and that other shaders are refused.

CTest runs every GPU suite as one test, `StrataTests.GPU`, labelled `gpu`: `ctest --preset windows-debug -L gpu`. For these suites alone, run the test program with `--test-suite=GPU.SceneRenderer*`. Tests labelled `gpu` need a graphics card.

## Changing it safely

Extension points are few and strict. A new pass goes into a file of its own, or the file of its feature. Its members are declared in `SceneRenderer.h` under a comment that names the file, and `RenderFrame` makes one call.

- **Give it a stage.** Time the pass with a stage of `RendererGPUStages`, registered with its module and started with `gpuTimer.Next(stage)` only where the pass runs. A new stage is one more row of that :term[struct]{id=struct} and of the profiler's tables.
- **Give it a slot.** Place it where its inputs are ready and its output is read: after the prepass if it needs depth, before the opaque pass if the forward shader reads it. A pass that reads the motion history runs before the motion copy.
- **Give it a dummy.** A shader input that the pass fills must be bound to a small dummy when the pass is off, so that the binding sets stay valid.
- **Make it invisible when off.** Make no target, time no stage, and add no field to `FrameConstants` (post effects add none). Keep the default image bit for bit, with a test that compares it.
- **Draw the same way twice.** Anything that changes how the prepass draws must change the forward pass too.

:::rule[Drawing changes keep both passes in step]
Every pass draws skinned instances with the skinned variants and mirrored ones with clockwise pipelines. The prepass and the forward pass must then give the same bits, because of the equal depth test above. See the [renderer reference](../reference/renderer.md).
:::

Exact-pixel tests disable post effects through `Tests::AddNeutralPostProcess` and use `Tests::ExactSpecification()` so that dither does not move the values. Before you merge a change, run the whole `GPU.SceneRenderer` family, including the suites `GPUDriven` and `Feedback`, because the CPU path and the culling shader must draw the same things.

## Summary

- The renderer records one command list in a fixed order: checks and extraction on the CPU, then setup, culling, shadows, the prepass, screen-space passes, the opaque pass, transparents, temporal and post passes, and overlays. Each pass is timed in a GPU stage.
- Strata draws a depth, normal and entity ID prepass and shades opaque surfaces with an equal depth test; that works only because the vertex position is invariant, so both passes compute the same bits.
- A feature that is off leaves the frame bit for bit as before and costs nothing: no target, no timed stage, a dummy where a shader would read it.
- A target for `Render` has one color attachment, the viewport's size and a UNORM format that is not sRGB, because the engine encodes sRGB in its own shader after tone mapping.
- Each pass has a marker, a stage and a switch in `RenderFrame`, and you can trace a pass from one to the other two.

## Check yourself

1. The opaque pass tests depth for equality. Which statement is right? (a) It is the same test as the prepass, with another name. (b) It passes only where the pixel's depth is exactly the prepass's, so each pixel shades once. (c) It passes wherever the depth is within a small tolerance of the prepass's.

   :::answer{tests="equal-invariant"}
   Option (b) is right. Option (a) is wrong: the prepass uses greater-or-equal and writes depth, while the opaque pass uses equal and writes none. Option (c) is wrong because the test has no tolerance, which is why the positions must match to the bit.
   :::

2. In the toy, swap the order of the two quads so that the near quad is drawn first. How many fragments does the forward pass alone shade?

   :::answer{tests="equal-invariant passes-order"}
   The near quad's 7 pixels per row pass. The far quad then covers columns 0 to 8, but in columns 5 to 8 its depth is smaller than the stored depth, so the test fails there. Only the 5 pixels of columns 0 to 4 pass. That is 12 per row and 48 in all, the same as the prepass run. With the best order, forward alone shades only what is visible, and the prepass makes that true for every order.
   :::

3. A frame takes the CPU path, which never starts the `Cull` stage, and the scene has 30 lights. In which stage's time are the light culling and the light clusters?

   :::answer{tests="passes-order"}
   The `Setup` stage. The timer never started `Cull` on this frame, so the stage that is running when the light passes record is `Setup`. On a GPU-driven frame the same passes land in `Cull`.
   :::

4. Your game draws into a target of 1280 by 720 with one `SRGBA8_UNORM` color attachment, and the renderer's viewport is 1920 by 1080. What does `Render` do, and what must change?

   :::answer{tests="target-rules"}
   `Render` logs an error and returns false, with `Rendered` false. The format check comes first: the format is sRGB, which is refused. Fixing it to a UNORM format that is not sRGB, such as `RGBA8_UNORM`, reveals the next fault, because the size differs from the viewport. The target must have the viewport's size too, or `SetViewportSize` must be given 1280 by 720. The renderer never changes the picture's size, and an sRGB target would encode the values twice.
   :::

5. A developer adds a new effect with a flag, and in the branch for the flag being off, writes the default path's lighting sum in a new order. The effect is off in the default scene. What is wrong?

   :::answer{tests="off-rule"}
   The default frame may change in the last bits, because adding the same numbers in a different order rounds differently. A feature that is off must leave the default path's arithmetic as it was, so that the default image stays bit for bit the same. The fix is to keep the old expression for the off case and use the new one only when the feature is on. A test must compare the off image with the image from before the feature.
   :::

6. You must find where the `Aerial` step is skipped. Which marker, which stage and which switch do you search for?

   :::answer{tests="trace-pass"}
   Search `RenderFrame` for `beginMarker("Aerial")`. Directly above it, `gpuTimer.Next(gpuStages.Aerial)` starts the `Aerial` stage, and both lines sit inside `if (m_AerialFrame)`. The function `SetAerialPerspective`, called earlier in the frame, sets that flag.
   :::

## Exercises

1. **Basic.** A view is 1280 by 720 pixels with an entity ID buffer. Compute the bytes of depth (`D32`), normals (`RG16_FLOAT`), entity IDs (`R32_UINT`) and the color target (`RGBA16_FLOAT`), and their total.

   :::answer[Worked solution]{tests="passes-order"}
   The view has 1280 × 720 = 921,600 pixels. Depth, normals and entity IDs each take 4 bytes a pixel: 3,686,400 bytes each. The color target takes 8 bytes a pixel: 7,372,800 bytes. The total is 3 × 3,686,400 + 7,372,800 = 18,432,000 bytes, which is 18.4 MB. Without entity IDs the total is 14,745,600 bytes.
   :::

2. **Medium.** Write a program for one row of eight pixels where an opaque surface covers columns 2 to 5. Run a sky at depth 0 with the greater-or-equal test, then with strictly greater, and print how many pixels each shades.

   :::answer[Worked solution]{tests="equal-invariant" solution="sketches/gpu-frame-tour-sky.cpp"}
   The depth buffer starts at 0 everywhere and holds 0.5 in the four covered columns. The sky's depth is 0. Greater-or-equal passes where the stored depth is at most 0, which is the four empty pixels. Strictly greater passes nowhere, since 0 is not greater than 0, which is why the sky pass uses greater-or-equal.

   ```cpp sketch="gpu-frame-tour-sky.cpp"
   #include <cstdio>
   #include <vector>

   // One row of eight pixels after the prepass. Reversed-Z: the far plane is depth 0 and the buffer is cleared to it.
   int main()
   {
   	constexpr int c_Width = 8;
   	std::vector<float> depth(c_Width, 0.0f);
   	for (int x = 2; x < 6; x++)
   		depth[x] = 0.5f; // An opaque surface covers columns 2 to 5

   	// The sky is a triangle drawn at depth 0, the far plane, after the opaque pass.
   	const float skyDepth = 0.0f;
   	int shadedGreaterOrEqual = 0;
   	int shadedGreater = 0;
   	for (int x = 0; x < c_Width; x++)
   	{
   		if (skyDepth >= depth[x])
   			shadedGreaterOrEqual++;
   		if (skyDepth > depth[x])
   			shadedGreater++;
   	}
   	std::printf("sky with GreaterOrEqual: %d of %d pixels\n", shadedGreaterOrEqual, c_Width);
   	std::printf("sky with Greater:        %d of %d pixels\n", shadedGreater, c_Width);
   	return 0;
   }
   ```

   ```text output-of="gpu-frame-tour-sky.cpp"
   sky with GreaterOrEqual: 4 of 8 pixels
   sky with Greater:        0 of 8 pixels
   ```

   1. **Line 8:** Every pixel starts at depth 0, the far plane.
   2. **Line 10:** The opaque surface sets four pixels to 0.5.
   3. **Lines 18–21:** The two tests count the pixels that each would shade.
   :::

3. **Hard.** Trace it yourself: find the pass that draws the aerial perspective volume in `RenderFrame`, the stage its time goes to, the switch that skips it and the page that teaches the feature. Then render a scene without an atmosphere on a source build, with a breakpoint there, and see the step skipped.

   :::answer[Worked solution]{tests="trace-pass"}
   In `Strata/src/Strata/Renderer/SceneRenderer.cpp`, in the function `SceneRenderer::RenderFrame`, the block that starts `if (m_AerialFrame)` calls `gpuTimer.Next(gpuStages.Aerial)`, begins the marker `Aerial` and calls `RenderAerialPerspective`. The stage is `Aerial`, and the switch is `m_AerialFrame`, which `SetAerialPerspective` sets (the function is in `Strata/src/Strata/Renderer/SceneRendererAtmosphere.cpp`). With a scene whose sky is not the atmosphere, the breakpoint on the `if` shows the flag false and the body never runs, so no `Aerial` group and no `Aerial` time appear. The [atmosphere page](../light/atmosphere.md) teaches the feature.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderer.h` and `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `SceneRenderer`, `SceneRenderer::Render`, `SceneRenderer::RenderFrame`, `SceneRenderer::SetViewportSize`, `SceneRenderer::SetQuality`, `SceneRenderer::ValidateTarget`, `SceneRenderOptions`, `SceneRendererStats`, `SceneRendererGPUStats` and `SceneCamera`.
- `Strata/src/Strata/Renderer/GPUProfiler.h`: `RendererGPUStages` and `GPUPassTimer`.
- `Strata/src/Strata/Runtime/GameRenderer.cpp`: `GameRenderer::Render`, the simplest caller.
- `Strata/shaders/Scene/`: `DepthPrepass.frag.slang`, `Forward.frag.slang`, `Mesh.vert.slang` and `Skybox.frag.slang`; `Strata/shaders/PostProcess/Tonemap.frag.slang`.
- `CMake/StrataShaderTool/SpirvModule.cpp`: `DecoratePositionInvariant`; `Strata/CMakeLists.txt`: the `INVARIANT_POSITION` list.
- `StrataTests/src/Renderer/GPUSceneRendererTests.cpp` and `StrataTests/src/Renderer/ShaderToolTests.cpp`: the suites `GPU.SceneRenderer` and `Renderer.ShaderTool`.

## Further reading

- Jason Gregory, "Game Engine Architecture", the chapter on rendering: forward and deferred pipelines in a full engine, intermediate.
- Ola Olsson, Markus Billeter and Ulf Assarsson, "Clustered Deferred and Forward Shading" (2012): tiled and clustered light lists, advanced.
- Christopher Burns and Warren Hunt, "The Visibility Buffer: A Cache-Friendly Approach to Deferred Shading" (2013): the visibility buffer, advanced.
- Yuriy O'Donnell, "FrameGraph: Extensible Rendering Architecture in Frostbite" (GDC 2017): a render graph in a production engine, advanced.
- The Vulkan specification, the `Invariant` decoration of the `Position` built-in: what the guarantee covers, advanced.
