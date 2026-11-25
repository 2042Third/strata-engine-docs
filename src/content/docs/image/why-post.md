---
id: image/why-post
title: "Why images need post-processing, and Strata's post chain"
description: "Why a renderer keeps light in a high dynamic range target and converts it to display values in a chain of passes, and the order of Strata's chain."
kind: concept
size: M
tracks: [E]
needs: [gpu/frame-tour, light/brdf]
time: 40
learn:
  - id: numbers-not-color
    text: explain why renderer values are light in nits and not display codes, and why doubling a code does not double the brightness
  - id: hdr-target
    text: choose a format for a high dynamic range target and compute where a value overflows or loses precision
  - id: chain-order
    text: name every pass of the post chain in order and say what each reads and writes
  - id: find-pass
    text: find which pass to examine when an image is too dark, banded or jagged
  - id: failure-path
    text: predict what a frame shows when a post pass cannot make its resources
since: 0.3.0
status: final
---

Look at the two pictures below. They show one frame of one scene. The :term[renderer]{id=renderer} computed the same numbers for both.

::compare{id=problem-pair}

The left picture puts the renderer's numbers, a :term[high dynamic range]{id=high-dynamic-range} (HDR) image, on the screen as they are. The right picture is the same frame after Strata's chain of post-processing passes, and the sky has a color again.

This page explains why the left picture happens, what an engine does about it, and the order of the passes that Strata runs between the lit scene and the display. Each later page of this part takes one of those passes.

## The numbers of a frame are light, not color

A frame is a grid of pixels, and each pixel holds a few numbers: red, green and blue, and often a fourth. A display turns such numbers into light. The numbers a display expects are **codes**: whole values from 0 to 255 for each channel, spaced so that equal steps look like equal steps to an eye.

The renderer works with a different kind of number. It computes how much light leaves a surface toward the camera, as radiance in nits (candelas per square metre, the unit of [Light units and exposure](../light/units-exposure.md)). Those numbers follow physics: twice the light is twice the number.

A white sheet of paper in direct sun sends about 30,000 nits toward you. The sun's disk sends about 1,600,000,000. A dark corner of a room sends about 0.1.

Compare the extremes: 1,600,000,000 divided by 0.1 is 16,000,000,000, about ten orders of magnitude. A display cannot show that range. Its darkest and brightest codes differ by a factor of a few thousand at most.

## Where the naive answer breaks

The naive answer is to write the renderer's numbers straight into the 8-bit codes, and to clamp whatever is above the largest code. Three things break.

First, the scale. A code of 255 means "as bright as this display goes", while 1.0 in a renderer means nothing in particular. If the renderer treats 1.0 as white, a wall in the sun at 30,000 nits and the sun at 1,600,000,000 nits both clamp to 1.0. The sky, the wall and the sun become one flat white.

Second, the steps. An 8-bit code has only 256 levels, and eyes see dark levels more finely than bright ones. Storing light directly in 256 equal steps leaves too few steps in the shadows, and smooth dark gradients show visible bands.

Third, the arithmetic. Lighting adds, scales and blends light, and those operations are only right for values proportional to light. The display's own spacing of codes is not proportional to light, as the next example shows.

Two relations between a value and light have names.

A value is **display-linear** when it is proportional to the light the display emits, so twice the number means twice the light.

A value is **encoded** when the display's :term[transfer function]{id=transfer-function} has been applied to it, so that equal steps look equal. A color picked in an image editor is almost always encoded.

The **sRGB encoding** is the standard curve for that. [Color](../basics/color.md) gives the formula.

:::example[Doubling a code does not double the light]
Take a linear value of 0.2 and double it to 0.4, so there is twice the light. The sRGB encoding turns 0.2 into 0.485, which is code 124 of 255. It turns 0.4 into 0.665, which is code 170. Twice the light moved the code from 124 to 170, a factor of 1.37 and not 2.

Now go the other way and mix half black and half white on purpose. A linear 0.5 is correct for that mix, and its encoded value is 0.735, code 188. A program that averages the two codes 0 and 255 gets code 128, which a display shows as a linear 0.216: the mix is far too dark.
:::

Two errors follow. Light computed on encoded values is wrong, and 1.0 is a number, not white. The renderer therefore keeps light linear, with no upper limit, for as long as it can, and converts to codes once, at the end. The steps between are the subject of this page.

## The idea: keep light in a wide target, then convert in passes

An **HDR image** is an image whose values are light, with no upper limit, stored as :term[floating-point numbers]{id=floating-point-number}. The renderer draws the scene into one such image, the HDR target. Every effect that needs real light, such as bloom, motion blur and the metering of the exposure, works on that image.

An image meant for a display is a low dynamic range (LDR) image. Its values lie between 0 and 1, and the image is **display-referred**: its values describe what the screen should show.

**Tone mapping** converts an HDR image into an LDR one. It multiplies the light by an exposure and bends the result with a tone curve, so that bright values approach white without clipping. Then it encodes the answer for the display.

A **full-screen pass** is a draw or dispatch that visits every pixel of an image and writes one output image. The post chain is a sequence of such passes, each reading the image the one before left. The diagram shows the chain in the order Strata runs it, and the stage of the :term[graphics processing unit]{id=gpu} (GPU) timer that covers each part.

```mermaid caption="The post chain of one frame. Light stays linear through the first six boxes; tone mapping makes display values, and only the passes after it work on those." alt="A row of boxes from the HDR target through temporal anti-aliasing, depth of field, motion blur, exposure, bloom with the lens flare, tone mapping and spatial anti-aliasing to text, overlays and the display target."
flowchart LR
    HDR["HDR target (RGBA16F)"] --> TAA["TAA resolve (GPU.TAA)"]
    TAA --> DOF["Depth of field (GPU.DepthOfField)"]
    DOF --> MB["Motion blur (GPU.MotionBlur)"]
    MB --> EXP["Exposure"]
    subgraph POST["GPU.Post"]
        EXP --> BLOOM["Bloom down, lens flare, bloom up"]
        BLOOM --> TM["Tone mapping"]
        TM --> AA["FXAA or morphological AA"]
    end
    AA --> OV["Text and overlays"]
    OV --> OUT["Display target"]
```

Read the diagram from left to right. Every box before tone mapping still holds light, and the box named tone mapping is where the conversion happens. The next sections explain each choice: the format of the first box, then the order of the rest.

## How engines store an HDR image

An HDR target is a texture whose format stores floating-point values. Three formats are common, and they trade range, precision and memory.

| Format | Bits per pixel | Largest value | Precision (steps in a value) | Cost and use |
| --- | --- | --- | --- | --- |
| `R11G11B10F` | 32 | about 65,000 | 6 bits in red and green, 5 in blue: about 1.6 % to 3 % | Smallest and fastest; no alpha channel and no negative values; colors can shift in dark gradients; used when :term[bandwidth]{id=bandwidth} is tight |
| `RGBA16F` | 64 | 65,504 | 10 bits: about 0.1 % | Twice the memory; fits most scenes once the light is scaled; the usual choice of engines for the lit image |
| `RGBA32F` | 128 | about 3 × 10^38 | 23 bits: about 0.00001 % | Four times the memory of the 32-bit format; used for accumulation and reference renders, rarely for a whole frame |

The 16-bit format is the compromise, yet its range is small beside ten orders of magnitude. A :term[half-float]{id=half-float} cannot hold more than 65,504; larger values become infinity. Below $2^{-14}$, about 0.000061, it loses precision, because values there are :term[subnormal]{id=subnormal-number} and step by a fixed amount. [Color](../basics/color.md) shows the bits.

Engines handle this by scaling. They multiply the light by a power of two, called the **pre-exposure**, as they write it. They divide it out where they read it. The useful part of the scene then sits in the middle of the half-float range. Powers of two are exact in floating point: scaling by them changes no bits of the :term[mantissa]{id=significand}, only the :term[exponent]{id=exponent}.

:::example[Fitting a scene in the sun into `RGBA16F`]
Use the three values from before: the sun at 1,600,000,000 nits, white paper at 30,000 nits and a dark corner at 0.1 :term[nit]{id=nit}. Stored as they are, the sun is above 65,504 and becomes infinity. Infinity then spreads: a blur that averages it with its neighbors makes them infinite too.

Now scale by $2^{-15}$, which is 1/32,768. The sun becomes 48,828, the paper 0.916 and the dark corner 0.0000031. All three fit under 65,504. The corner now lies below 0.000061, so it is subnormal and stored with a step of 0.00000006, about 2 % of its value.

A pre-exposure that is too small buries shadows in coarse steps; one that is too large pushes the sun over the edge. The choice is the subject of [Pre-exposure](pre-exposure.md).
:::

## Strata's choice: `RGBA16F`, pre-exposure and a finite target

Strata renders the scene into an `RGBA16F` target, named `c_HDRFormat` in `SceneRenderer`. Each value is :term[luminance]{id=luminance} times the frame's pre-exposure, a power of two. `GetHDRTexture` returns the texture for code that needs the lit image itself.

Every pass that writes the target keeps it finite with `SanitizeHDR`: it turns :term[NaN]{id=nan} and negative values into 0 and anything above 65,000 into 65,000. A NaN is the result of an invalid operation such as 0 divided by 0. One NaN in one pixel spreads through a blur, and through the history of temporal anti-aliasing, until the frame is black. Clamping at the writer stops that at the source. [Keeping HDR values finite](../light/brdf.md) shows the code and why each writer calls it.

:::why[Why not a smaller or a larger format?]
`R11G11B10F` halves the memory, but its 5 or 6 bits of precision band in the dark gradients that bloom and soft shadows produce, and it holds no alpha. `RGBA32F` removes every range problem, but doubles the memory and the bandwidth of every pass that touches the frame, and the post chain reads the frame many times. `RGBA16F` with pre-exposure keeps the precision of 10 bits where the picture is, at a cost of one scale factor that every writer and reader must apply. A writer that forgets the scale produces a wrong picture without an error.
:::

## The chain's order and why it holds

Strata's own comment at the top of `Strata/src/Strata/Renderer/SceneRendererPost.cpp` states the rule that makes the passes independent:

> Post passes take their parameters by push constants or buffers of their own, never FrameConstants.
>
> — Strata/src/Strata/Renderer/SceneRendererPost.cpp

A pass therefore adds no field to the per-frame constants that every :term[shader]{id=shader} reads. It owns its settings, and a new effect touches no other pass.

The order follows one principle: do the work on linear light first, meter the result, and touch display values last.

1. **Temporal anti-aliasing (TAA) resolve** blends the frame with the history of earlier frames along the motion vectors. It needs the linear image, because blending after the tone curve would blend values that are not proportional to light. When it runs, its output is the frame that all later passes read, and the spatial anti-aliasing of step 7 is skipped.
2. **Depth of field** blurs by distance from the focus. It runs on frames seen through a lens, that is perspective views, and needs light that is still linear so that a small bright highlight spreads into a bright disc.
3. **Motion blur** smears what moves. It runs only when the frame has a motion history and the camera did not cut, because a cut makes the motion between the two frames meaningless.
4. **Exposure** meters the image, or takes the manual setting, and writes the factor that tone mapping will apply. It comes after the effects above because they change how bright the picture is, and the meter must see the picture that will be shown. [Exposure](exposure.md) explains the metering.
5. **Bloom** shrinks the image into a chain of half-resolution images and enlarges it back, and the **lens flare** draws between the shrinking and the enlarging. Bloom adds the glow of real light, so it also works on linear values.
6. **Tone mapping** applies the exposure, adds the bloom, the vignette, the grading and the color lookup, and writes display values into the display target. When spatial anti-aliasing follows, it writes an LDR target instead.
7. **Spatial anti-aliasing** smooths edges, by fast approximate anti-aliasing (FXAA) or by morphological anti-aliasing. Both look at neighboring display values, because an edge is a difference a viewer sees. The last pass that writes the display image, this one or else the tone mapping, adds the dither: a faint noise that hides the bands between 8-bit codes. The morphological method finds edges and rebuilds the lines they stand for, in each frame alone.
8. **Text and overlays** are drawn last in an output texture and copied into the target by `Copy.frag`, so that :term[gizmos]{id=gizmo-start} and text are never blurred or tone mapped.

The overview comment says the same of the chain's middle: tone mapping reads the exposure buffer, the bloom, the vignette and the grading in one pass. Strata records the first part of the chain, `RenderPostHDR`, then the text and overlay preparation, then `RenderPostDisplay`.

### Post source: the one image the chain reads

The chain skips passes that are off, so the image a pass reads is not always the one before it in the diagram. The **post source** is the texture the post passes read this frame: the HDR target, the history of the temporal anti-aliasing (TAA) resolve, the depth of field output or the motion blur output. `PostSource` lists the four, and `SelectPostSet` picks the :term[binding set]{id=binding-set} of the current one. The source starts at the TAA's resolved image when there is one, else at the HDR target, and each pass that runs replaces it.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3796-L3817"
const bool resolved = m_TemporalResolved;
PostSource postSource = resolved ? PostSource::History : PostSource::HDR;
if (options.Lens && !camera.Orthographic && m_Specification.Quality.DepthOfField != SceneEffectChoice::Off)
{
	gpuTimer.Next(gpuStages.DepthOfField);
	commandList->beginMarker("DepthOfField");
	if (RenderDepthOfField(commandList, *options.Lens, postSource))
		postSource = PostSource::DepthOfField;
	else
		degraded = true;
	commandList->endMarker();
}
if (motionBlurWanted && m_Stats.MotionHistory && !cameraCut)
{
	gpuTimer.Next(gpuStages.MotionBlur);
	commandList->beginMarker("MotionBlur");
	if (RenderMotionBlur(commandList, postProcess, postSource))
		postSource = PostSource::MotionBlur;
	else
		degraded = true;
	commandList->endMarker();
}
```

1. **Line 3797:** the source starts at `History` when temporal anti-aliasing resolved the frame, else at `HDR`.
2. **Lines 3798–3807:** depth of field runs with a lens, a perspective view and its quality row not off. On success the source becomes its output; on failure the frame is marked degraded.
3. **Lines 3808–3817:** motion blur follows the same pattern, with a motion history and no camera cut.

The quote shows the switching for the two effects between the resolve and the exposure. Notice that a pass that fails leaves the source as it was. The [post effect tutorial](tutorial-post-effect.md) walks the whole function.

### Frames that end early, and the machinery

Not every frame goes through the chain. A frame with `HDROutput` ends with its HDR image: it runs no exposure, bloom, tone mapping, text or overlay, because its reader wants light and not a picture. The reflection probe bake is such a frame.

Every post pass that draws, rather than computes, calls `DrawFullscreen`. It sets the pipeline, the framebuffer and the binding sets, pushes the constants and draws three vertices. Three vertices are enough because the triangle is larger than the screen ([Coordinates](../gpu/coordinates.md) explains it), and the pipelines are cached per framebuffer ([Binding](../gpu/binding.md) explains the cache). The overlays' copy is one such draw with `Copy.frag`.

The GPU timer splits the chain into five stages, named with the prefix "GPU." in the profiler: `TAA`, `DepthOfField`, `MotionBlur`, `Post` and `Overlays`. The `Post` stage holds the exposure, the bloom, the lens flare, the tone mapping and the spatial anti-aliasing; `Overlays` holds the text, the overlays and their copy. The shaders' arithmetic has copies in C++ for the :term[central processing unit]{id=processor} (CPU), the twins in `PostProcessMath`, so that tests compute what the GPU must show ([Tone mapping](tone-mapping.md) teaches the pattern). The chain also reports its state in `renderStats`; [Renderer reference](../reference/renderer.md) lists the keys.

## One component, and no volumes

One `PostProcess` component, shown as **Post Process** in the editor, holds every setting of the chain, in inspector sections such as Tone and color, Exposure, Bloom and Anti-aliasing. `GetPostProcessSettings` walks the scene and returns the first active component, or the defaults when there is none. Other engines blend settings from volumes placed in the world. Strata has none: a second component never mixes with the first, and no shape limits where the first applies.

## What Strata's choice cannot do

The format keeps 10 bits of precision, so a very dark region of a bright frame can band under strong grading. The target holds one value per pixel, so no pass can recover what the lit pass already clamped: a value above 65,000 is 65,000 for all later passes. The chain is also not a graph a game can rearrange: the order is fixed in `RenderFrame`, and a project adds no pass of its own. [What Strata does not do](../appendix/not-in-strata.md) lists the related limits.

A pass can also fail. When an effect cannot make its resources, the frame continues without it, and the error is logged once.

- Depth of field, motion blur and the lens flare are skipped.
- The morphological anti-aliasing falls back to FXAA.
- The color lookup and the lens flare bind dummy textures, which the tone mapping skips at intensity 0.
- The frame is marked degraded, and the error stays until the first frame that is drawn whole clears it.

A frame whose tone mapping inputs cannot be bound at all produces no image, rather than a stale one.

## Common mistakes

1. **Reading 1.0 as white.** The symptom is a flat white sky, as in the left picture. The fix is to remember that a stored 1.0 depends on the pre-exposure; exposure and tone mapping decide what the display shows.
2. **Expecting a doubled value to look twice as bright.** The symptom is a gradient that looks too steep in the shadows. The fix is to double light, not codes, and to let the sRGB encoding at the end make the codes.
3. **Lighting or tone mapping encoded values.** The symptom is dark mixes and muddy bloom. The fix is to decode a texture's colors before use and encode once, last.
4. **Ignoring the half-float limits.** The symptom is black holes where a very bright highlight was, or bands in dark regions. The fix is to keep a value under 65,504 after the pre-exposure and above $2^{-14}$ where detail matters.
5. **Letting a NaN into the target.** The symptom is a black patch that grows through bloom or temporal history. The fix is to pass every written value through `SanitizeHDR`.

## Summary

- Renderer values are light in nits; display codes are an encoded, display-referred scale, so doubling a code does not double the light and 1.0 is not white.
- Strata draws into an `RGBA16F` target that holds luminance times a power-of-two pre-exposure, kept finite by `SanitizeHDR`; the format trades 10 bits of precision and a 65,504 limit for half the memory of `RGBA32F`.
- The chain runs TAA resolve, depth of field, motion blur, exposure, bloom with the lens flare, tone mapping, FXAA or morphological anti-aliasing and the overlays; `PostSource` names the image each reads.
- A dark image points at exposure or tone mapping, banding at the format or the dither, and jagged edges at the anti-aliasing pass.
- A pass that cannot make its resources is skipped or replaced, the frame is marked degraded, and the error is logged once.

## Check yourself

1. A material's linear value goes from 0.2 to 0.4. Which is right: (a) the code doubles; (b) the light doubles and the code rises 1.4 times; (c) the light rises 40 %; (d) nothing changes, because the display clamps?

   :::answer{tests="numbers-not-color"}
   Option (b). Doubling a linear value doubles the light, and the encoding turns 0.2 into code 124 and 0.4 into code 170. Option (a) treats codes as light, the mistake of the example. Option (c) reads the doubling as an increase of 40 %. Option (d) confuses the display's limit with the renderer's range: 0.4 is below 1.0 anyway.
   :::

2. A highlight of 1,000,000 nits is written with a pre-exposure of 1 into an `RGBA16F` target through `SanitizeHDR`. What does the pixel hold, and what would it hold with a pre-exposure of $2^{-4}$?

   :::answer{tests="hdr-target"}
   With a pre-exposure of 1 the value 1,000,000 is above the limit, so `SanitizeHDR` writes 65,000, and every later pass sees a highlight 15 times too dark. With $2^{-4}$, which is 1/16, the value is 62,500, which fits under 65,000 and is stored with a step of 32.
   :::

3. In which order do these passes run: tone mapping, motion blur, bloom, TAA resolve, FXAA, exposure?

   :::answer{tests="chain-order"}
   TAA resolve, motion blur, exposure, bloom, tone mapping, FXAA. The first four work on linear light, tone mapping makes display values, and FXAA looks at the display values it made.
   :::

4. The picture is too dark, has bands in a dark gradient, or shows jagged edges. For each, name the pass to examine first.

   :::answer{tests="find-pass"}
   Too dark: the exposure, because the factor is wrong (the metering, or a manual exposure of the Post Process); then the tone mapping. Bands: the tone mapping and the pass after it, which write the display image and dither it, then the pre-exposure that sets the precision of dark values. Jagged edges: the anti-aliasing, that is the TAA resolve when TAA is chosen, else FXAA or the morphological pass.
   :::

5. A project selects the morphological anti-aliasing, and the GPU cannot make its textures. What does the viewer see, and what does the log say?

   :::answer{tests="failure-path"}
   The frame is drawn with FXAA, so the edges are still smoothed, and the frame is marked degraded. The log shows the error once, however many frames follow, and the first frame drawn whole clears it.
   :::

## Exercises

1. **Basic.** A scene has a sun of 1,600,000,000 nits and shadows of 0.5 nit. Which pre-exposure that is a power of two puts the sun closest below 65,504, and is the shadow then above $2^{-14}$?

   :::answer[Worked solution]{tests="hdr-target"}
   Divide the sun by the limit: 1,600,000,000 / 65,504 is about 24,425, and the next power of two above is $2^{15}$, which is 32,768. So the pre-exposure is $2^{-15}$ and the sun is 48,828. The shadow becomes 0.5 / 32,768 = 0.0000153, which is below $2^{-14}$ = 0.000061, so it is subnormal. The scene's range is too wide for full precision at both ends of it.
   :::

2. **Medium.** Predict, then run. On a copy of the Basic 3D template, turn the chain's effects off one at a time. Before each capture predict which pass's output changes: `Bloom` off, then `AntiAliasing` off, then `AutoExposure` off with `Exposure` 0, then `Tonemapper` None.

   :::answer[Worked solution]{tests="chain-order,find-pass" solution="tutorials/image/why-post/exercise-2.tutorial.json"}
   Without bloom the glow around bright light is gone, and only the bloom pass changes. Without anti-aliasing the TAA of this template stops, so edges show steps and shimmer when the camera moves. A manual `Exposure` of 0 multiplies the light by 1 and the pre-exposure is divided out, so the picture turns almost white. `Tonemapper` None then removes the curve, and what is left is the problem picture: a clipped sky. The command file sets each value and reads it back; capture the viewport after each with `viewport.capture`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: the overview comment, `SelectPostSet`, `DrawFullscreen` and the passes of the chain.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `RenderFrame`'s source switching, the `HDROutput` exit and `GetPostProcessSettings`.
- `Strata/src/Strata/Renderer/SceneRenderer.h`: `c_HDRFormat`, `GetHDRTexture` and `PostSource`.
- `Strata/src/Strata/Renderer/PostProcessMath.h`: the CPU twins of the shaders' math.
- `Strata/src/Strata/Renderer/RendererComponents.h`: `PostProcessComponent`, the settings of the chain.
- `Strata/shaders/PostProcess/*.slang`: the passes; `Strata/shaders/Include/Common.slang` holds `SanitizeHDR`.
- The **Post Process** component in the **Inspector**, and the commands `component.get`, `component.set` and `viewport.capture`.

## Further reading

- Real-Time Rendering, fourth edition, the chapters on color, tone mapping and image-space effects: the standard reference (advanced).
- John Hable, "Uncharted 2: HDR Lighting", GDC 2010: an early account of filmic tone mapping in a game (intermediate).
- Sébastien Lagarde and Charles de Rousiers, "Moving Frostbite to Physically Based Rendering", SIGGRAPH 2014: light units and exposure in an engine (advanced).
