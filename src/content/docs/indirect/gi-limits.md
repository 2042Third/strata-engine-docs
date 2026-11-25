---
id: indirect/gi-limits
title: "Global illumination III: moving objects, limits and what comes next"
description: "What Strata's bounce light holds and what it cannot: moving objects, thin walls, the field's edge, the cost when it is off and what other engines add."
kind: concept
size: M
tracks: [E]
needs: [indirect/gi-cascades]
time: 40
learn:
  - id: what-is-covered
    text: name what enters the voxels, what lights them and how far the probe field reaches
  - id: thin-things
    text: compute whether a wall, gap or prop of a given size is resolved at the High and Low rows
  - id: movers
    text: trace what happens to the light of a moving object from its first move until its exact shape takes over
  - id: off-is-invisible
    text: explain why a frame without global illumination equals the old image bit for bit and what its cost still is
  - id: will-it-help
    text: predict from the description of a scene which limit decides whether global illumination helps
since: 0.8.0
status: final
---

:term[Global illumination]{id=global-illumination} (GI) gives a scene bounce light: the sun lights a floor, the floor lights the walls, and a room with no lamp in view still has soft light in its corners. [Global illumination with radiance cascades](../indirect/gi-cascades.md) showed how Strata makes it. Here you enable it in two scenes and search for what is wrong, and a drawing shows a third limit. Each figure shows a limit of the method, not a mistake of the scene.

The first picture is the Cornell box: a white room with a red wall, a green wall and a glowing panel in the ceiling. A white ball stands on the floor. Under the ball's rim a black band with stair-stepped edges lies on the floor.

::figure{id=cornell-notches}

In the second picture a free-standing wall only 6 cm thick stands in the same room, seen in the :term[voxels]{id=voxel} debug view. That view shows the voxels of a wall in an error color when the wall is too thin to keep its two sides apart. This wall shows the error color all over.

::figure{id=thin-wall-voxels}

The third figure draws the field from above. Bounce light ends at the edge of a box around the camera, and beyond it the light is that of a scene without GI. The edge shows only where bounce light is strong.

::figure{id=field-edge-plan}

Strata calls the feature experimental. This page says what it can hold, so that you can tell before you build a scene whether it will help.

## The naive answer: free bounce light everywhere

A switch in a scene's post-processing settings sounds like a promise: every surface gets the bounce light it would get in life. Five things would have to hold for that promise.

- Everything that blocks or bounces light is in the voxel copy of the world, at its true thickness.
- Everything that emits light feeds the voxels.
- The probes are close enough to resolve every corner.
- The field of probes reaches every surface the camera sees.
- Every surface sees at least some of the probes.

The figures break the first and the last three. The black band comes from probes 0.5 m apart, the wall from voxels wider than it is, and the drawn edge from a field that stops. Moving objects, characters and lamps break the first two.

All of the limits share one cause. The method pays memory and time for a bounded copy of the world, and the copy has a grain (voxels from 10 cm, probes 0.5 m apart) and an edge (a box around the camera).

## Two bounded copies hold the light

The diagram shows what each copy takes in. Read it from the left: the solid arrows feed the copies and the dashed one marks what never enters.

```mermaid caption="Static meshes, moving boxes, the sun and glowing surfaces feed the voxel copy. The probes read it, and the join gives only diffuse light to shading. Characters and point or spot lights never enter." alt="A flow chart from four sources to a voxel copy, then to a probe field, a join and the image. A dashed arrow from characters and lamps stops short of the voxel copy."
flowchart LR
    A["Static meshes"] --> V["Voxel copy around the camera"]
    B["Moving objects as boxes"] --> V
    C["Sun, sky and glowing surfaces"] --> V
    D["Characters, point and spot lights"] -.-> |"left out"| V
    V --> P["Probe field around the camera"]
    P --> J["Join: diffuse light only"]
    J --> I["Image"]
```

The voxel copy holds geometry, in four levels of 128 x 64 x 128 voxels at High. The finest voxels are 10 cm wide, and each level has voxels twice as wide as the one before. At Low there are three levels, from 20 cm. Opaque and alpha-masked meshes that are not skinned enter, but only the first 256 :term[submeshes]{id=submesh} of each mesh. A material enters as the mean color of its texture, so a stone texture with dark cracks becomes one gray.

Light enters the voxels from the sun and from glowing surfaces, and then from the bounces of that light, one more bounce in each frame. A point or spot light adds nothing, so a scene lit by torches gets no torch bounce. The sky reaches the probes only through rays that leave the voxels.

The field holds the light at the probes. At High the probes are 0.5 m from each other, and at Low they are 1 m from each other. A surface reads the eight probes around it, each weighted by its distance and by whether it sees the surface.

The field covers a box around the camera. At High the field has full strength out to 7.5 m from the camera sideways and 5.5 m above or below it. At Low those numbers are 7 m and 2.8 m. Beyond them it fades to today's light over 2 m more.

A probe stores the light by direction in a few numbers. For a wall turned 30 degrees from the world's axes that storage blurs, and the wall glows softly around a patch of sunlight, up to 2.7 times the light of its shadowed part.

The join then changes only the diffuse :term[indirect light]{id=indirect-light}. Specular light keeps what it had, so a polished floor shows no bounced color in its reflections.

### A gap smaller than a voxel closes

The black band of the first picture follows from numbers. The ball has a radius $R$ of 0.9 m and touches the floor. At a horizontal distance $d$ from the contact its bottom lies $h = R - \sqrt{R^2 - d^2}$ above the floor.

:::example[Why the floor under the ball turns black]
At $d$ = 0.3 m the gap is $0.9 - \sqrt{0.81 - 0.09}$, about 5 cm. At 0.4 m it is about 9 cm, and at 0.5 m about 15 cm. A voxel is solid wherever any face reaches into it, so the layer of 10 cm voxels above the floor is solid out to 0.41 m from the contact: the gap vanishes from the copy.

The camera still sees the floor there through the gap. No probe sees those points, because the probes are 0.5 m apart and the voxels around them are solid. A point that sees none of its eight probes gets no field light. It is not given the sky: it is dark, and darker than without GI.
:::

The same arithmetic explains the wall. A wall 6 cm thick lies inside one 10 cm voxel, which holds both of its faces. Their normals point against each other, so the voxel is marked two-sided and takes light from neither side. The same wall placed across a voxel boundary puts each face in a voxel of its own, and neither voxel is marked. A wall must be thicker than two voxels, 20 cm at High and 40 cm at Low, to keep its sides apart.

## A moving object is a box until it rests

Turning a mesh into voxels means testing every triangle against the voxels around it. Doing that each frame for a swinging door would cost more than the light is worth. Strata does it twice per move instead.

When an object gets a new place, the voxels its triangles made fade out over 0.25 s. Meanwhile each submesh of the object is an oriented box, a box turned with the object, in a separate dynamic layer. A box needs no triangles, so a mover costs the same whatever its mesh. After the object has kept its place for 0.25 s, its triangles make voxels again, and those fade in over another 0.25 s.

:::history[A count of frames became a clock]
An earlier design kept a mover out of the voxels for 30 frames. At 60 :term[frames per second]{id=frame-rate} its shade and bounce then arrived half a second after it stopped, and later at lower rates. The release counts the :term[renderer's]{id=renderer} clock, so the wait is 0.25 s at any frame rate.
:::

Take a crate pushed across the floor of a room lit by the sun, at 75 frames per second. While it moves, it shades the floor beside it as a box and tints it with its color. After it stops, 19 frames pass before its exact shape takes over: 18 frames make 0.24 s, one frame short of the wait.

Then the light beside the crate changes by what the box and the shape differ by. Under an open sky, a point 0.3 m from a 0.5 m box sees its light change by as much as 26 %. In a closed room lit by bounces the change is larger: the release notes record one frame that steps the floor beside a Cornell box by 27.6 %.

The layer has limits. It takes at most 64 moving parts, which are submeshes, and 512 bricks of 8 x 8 x 8 voxels at High, half as many at Low. A 1 m box reaches about 50 bricks at High, so about ten such boxes fill the layer. Whatever lies past a limit stays out of the bounce light until it rests. Characters never enter the voxels: they receive the field, and they neither block nor bounce light.

## Other engines pay to add what Strata lacks

Each approach below begins with the flaw of the one before it. A table follows, and its sources are in Further reading.

Baked light stores the bounce of a static scene in lightmaps and probes. Reading it is cheap and its quality is the best for what never changes, but a sun that moves or a door that opens needs a new bake.

So engines keep a dynamic copy of the static world, as Strata does and as Godot's signed distance field global illumination does. The light follows the sun, but objects that move do not take part.

To include moving objects, a probe grid such as the one in the paper on dynamic diffuse global illumination traces rays against the current scene and blends the result over frames. Moving objects take part, and the price is lag and a trace of the real scene. Unreal's :term[Lumen]{id=lumen} traces a mix of screen, distance field and, on capable cards, triangle rays. Hardware ray queries test rays against the real triangles: thin walls are exact, and the price is the most time and a card that has the feature.

| Approach | Cost | Quality | Complexity | Used by |
| --- | --- | --- | --- | --- |
| Baked probes and lightmaps | A bake, then a lookup | Best for static light, no reaction | Bake tools | Unity, Unreal, Godot |
| Dynamic copy of the static world | Memory and passes each frame | Reacts to the sun, thin walls leak | High | Godot, Strata |
| Probes traced in the current scene | Rays each frame, history | Moving objects, lags behind changes | High | Dynamic diffuse global illumination |
| Hardware ray queries | The most, a capable card | Closest to the reference | High | Lumen's hardware mode |

## Off costs nothing visible, and the rest is stated

Strata treats GI as an experiment that must be free to leave off. It reads world data and the camera's place, never the screen. A frame keeps the old image of version 0.7.0 bit for bit, which means that every pixel has the same value. That holds when the scene does not ask for GI, when the quality row is Off and while the field is pending because the camera jumped or the voxels are rebuilt.

:::why[Why a feature that is off changes no bit]
A game that never enables GI must not pay for it, and a test must be able to prove that. Two rules deliver both, and [A frame of the scene renderer, pass by pass](../gpu/frame-tour.md) states the rule for the whole renderer. A frame that does not use the field draws with forward :term[shaders]{id=shader} that hold none of the gather, and their pipelines are made only when a frame joins the field. A frame that uses the field with a weight of 0 gets the old light too, because the join multiplies today's light by 1 and adds 0.
:::

The join in the forward shader sets the field's weight and blends today's diffuse light with the field's. Specular light is composed once and added as it was.

```slang src="Strata/shaders/Scene/Forward.frag.slang#L432-L443"
	indirectInputs.FieldWeight = field.a;
	indirectInputs.FieldIrradiance = field.rgb * (u_Frame.ReflectionParams.z / ST_GI_RADIANCE_SCALE);
	indirectInputs.FieldOpen = openShare;
	if (lightingView == ST_LIGHTING_VIEW_SPECULAR)
		indirect = ComposeIndirect(indirectInputs, float3(0.0), GatherIndirectSpecular(indirectInputs));
	else if (lightingView == ST_LIGHTING_VIEW_DIFFUSE)
		indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface) * (1.0 - indirectInputs.FieldWeight), float3(0.0))
			+ GatherIndirectField(indirectInputs, surface) * indirectInputs.FieldWeight;
	else
		indirect = ComposeIndirect(indirectInputs, GatherIndirectDiffuse(indirectInputs, surface) * (1.0 - indirectInputs.FieldWeight),
			GatherIndirectSpecular(indirectInputs)) + GatherIndirectField(indirectInputs, surface) * indirectInputs.FieldWeight;
}
```

1. **Line 432:** the field's weight: 1 inside the box and 0 beyond its fade.
2. **Lines 438-439:** the diffuse view blends today's diffuse light with the field's by that weight.
3. **Lines 441-442:** the lit view does the same for the diffuse part and adds the specular part unchanged.

What it costs is measured and stated. In the look-dev shots without GI at 3840 x 2160, the time of `GPU.Opaque` differs by -0.010 to +0.007 ms from the build before the second batch of GI work. With GI at High the stage `GPU.RadianceCascades` takes about 4.2 ms, and the gather in the forward pass adds 0.3 to 0.8 ms, plus 0.10 to 0.12 ms to `GPU.Opaque`.

One exception runs GI where nothing asks for it: a GI debug view. At the Off row it shows High's layout.

## What the field cannot do

Each limit below has one cause. The release notes' Known issues give the measured misses, and [Trying global illumination](../make/gi.md) shows how to work around them in a game.

| Limit | Cause |
| --- | --- |
| A surface that sees none of its eight probes is dark, never the sky: gaps, ledges and wall feet, outdoors too | Inside the field the join replaces today's light with the probes' light, and these probes give none |
| Walls and gaps thinner than two voxels go two-sided | One voxel holds both faces, and their normals cancel |
| Thin props become lumps of whole voxels | A voxel is solid where any face reaches into it |
| A model colored from one palette texture takes the palette's mean everywhere | A material enters as the mean of its maps |
| Voxels of double-sided materials have no facing | Their triangles add no normal |
| Glowing values above 65,408 :term[nits]{id=lux} clamp | A voxel stores its emission in a format that ends there |
| An editor view from far above shows only the coarse levels | The fine levels are windows around the camera |
| Submeshes past a mesh's 256th are omitted, and the log says so once | A work item names its submesh in 8 bits |
| Low bounces once | Its coarse field would make a Cornell box about 1.8 times as bright as High's |
| A baked probe capture holds no GI | A bake renders at the Medium row, where GI is Off ([Reflection probes](../indirect/probes.md)) |

### What Strata does not do

The documents list more work as later, without a date. These parts are not built:

- Local lights do not feed the voxels, and a panel made a rect light counts its light twice in a GI scene.
- Characters do not take part, and moving objects are boxes while they move.
- Specular light stays as it was, and the field adds no :term[open share]{id=open-share} to :term[specular occlusion]{id=specular-occlusion-lagarde}.
- There is no `Ultra` row, no color read from the texture at each voxel and no hardware ray queries.
- There are no nested probe fields and no denser probes near surfaces.

Probe relocation is built and is taught on the cascades page. [What Strata does not do](../appendix/not-in-strata.md) covers the general techniques.

## Common mistakes

- **A wall thinner than two voxels.** The symptom is a wall that is dark on both sides. Build walls 20 cm or thicker at High, and 40 cm at Low.
- **Expecting a moving door to change the bounce at once.** The symptom is shade that shifts a quarter of a second after the door stops. The box shades at once, but the exact shape arrives later, so judge the light after the wait and the fade.
- **Judging the light before it settles.** After a cut each bounce arrives one frame later: a room lit by the sun took 13 frames, a Cornell box 18 and a closed white box 39. Wait, as captures do.
- **Reading one measurement of the GI stage as the cost.** The stage read 4.4 ms in some runs and 6.5 ms in others of one build, with no known cause. Compare builds by interleaved runs.

## Summary

- Static opaque meshes enter the voxels as triangles, lit by the sun and glowing surfaces; lamps and characters do not enter, and the field covers a box around the camera.
- A gap, wall or prop under two voxels (under 20 cm at High, under 40 cm at Low) is not resolved. It closes, goes two-sided or blurs, and the probes cannot see into it.
- A moving object is a box for 0.25 s after its last move, then its triangles make voxels, which fade in over 0.25 s; characters never enter.
- A frame without GI equals the old image bit for bit, because it draws with shaders that hold none of the gather; its `GPU.Opaque` time stays within -0.010 to +0.007 ms of the build before.
- Ask which limit decides: lamps, thin things, movers, range or what the probes cannot see.

## Check yourself

1. A cave is lit by twenty point-light torches and has stone walls 30 cm thick. What does GI at High add?
   - A. Bounce light from every torch.
   - B. No torch bounce, because only the sun and glowing surfaces feed the voxels; the walls are thick enough to keep their sides apart.
   - C. Dark walls, because 30 cm is under two voxels.
   - D. Torch bounce for a quarter of a second after each torch is placed.

   :::answer{tests="what-is-covered"}
   B. A is the mistake of expecting every light to bounce: point and spot lights add nothing to the voxels. C is wrong because two voxels at High are 20 cm. D confuses lamps with moving objects, which are the only things the quarter second concerns.
   :::

2. A fence rail is 8 cm thick and a wall is 25 cm thick. Which is resolved at High, and which at Low?

   :::answer{tests="thin-things"}
   The rail is under one voxel at both rows (10 cm and 20 cm), so it is not resolved: it blurs into whole voxels. The wall is thicker than two voxels at High (20 cm), so it keeps its sides apart, but at Low the limit is 40 cm and the wall goes two-sided.
   :::

3. A crate stops at 75 frames per second. In which frame after the stop do its triangles return to the voxels?

   :::answer{tests="movers"}
   In frame 19. The first frame adds 1/75 s, and 18 frames give 0.24 s, under the 0.25 s wait; the 19th gives 0.2533 s. The voxels then fade in over a further 0.25 s.
   :::

4. Which statement about a frame without GI is true?
   - A. Its pixels differ slightly from 0.7.0 because the join adds zero.
   - B. Its image equals the old one bit for bit; with the field's weight 0 the join gives today's light as `x * 1 + 0`.
   - C. It costs the full 4.2 ms stage.
   - D. A GI debug view at the Off row shows nothing.

   :::answer{tests="off-is-invisible"}
   B. A is wrong because multiplying by 1 and adding 0 change no value. C is wrong: nothing runs. D is wrong: a GI debug view runs GI at Off with High's layout.
   :::

5. In an open field you stand 1.7 m above the ground, and a rock lies 20 m away. Does the rock get field light at High?

   :::answer{tests="will-it-help what-is-covered"}
   No. The field is full within 7.5 m horizontally and gone at 9.5 m, so the rock keeps today's light, exactly as without GI.
   :::

## Exercises

1. **Basic.** Name the limit that decides each scene: (a) a cave lit only by torches, (b) a hall lit by the sun whose door swings, (c) a grove of poles 5 cm thick.

   :::answer[Worked solution]{tests="will-it-help"}
   (a) Lamps feed no voxels, so GI adds no torch bounce. (b) The door is a box while it moves, and its exact shape arrives 0.25 s after it stops, so the light beside it shifts then. (c) The poles are thinner than a voxel, so they become lumps and the probes cannot resolve them.
   :::

2. **Medium.** A sketch counts the frames before a mover rests by the clock, and the seconds an earlier design needed with a count of 30 frames. Predict its line for 45 frames per second, then run it.

   ::::answer[Worked solution]{tests="movers" solution="sketches/indirect-gi-limits-rest.cpp"}
   :::question
   The sketch uses loops, functions and `std::printf`: see [loops and functions](../basics/programming-2.md) and [calls and includes](../basics/programming-3.md).
   :::

   At 45 frames per second a frame lasts 0.0222 s. Eleven frames give 0.244 s and twelve give 0.267 s, so the line reads 12 frames and 0.267 s by the clock, against 0.667 s for 30 frames. The sketch adds one frame's time until the clock reaches the wait.

   ```cpp sketch="indirect-gi-limits-rest.cpp"
   #include <cstdint>
   #include <cstdio>

   // What the renderer waits before a moved object counts as resting, by the clock.
   const double c_RestSeconds = 0.25;
   // What an earlier design waited, by a count of frames.
   const uint32_t c_RestFrames = 30;

   // Adds one frame's time per frame until the clock reaches the wait; returns the frames that took.
   static uint32_t CountFramesToRest(double framesPerSecond)
   {
   	const double frameSeconds = 1.0 / framesPerSecond;
   	double waited = 0.0;
   	uint32_t frames = 0;
   	while (waited < c_RestSeconds)
   	{
   		waited += frameSeconds;
   		frames++;
   	}
   	return frames;
   }

   int main()
   {
   	const double rates[] = { 30.0, 45.0, 75.0, 90.0 };
   	std::printf("fps  frames  clock(s)  count(s)\n");
   	for (const double rate : rates)
   	{
   		const uint32_t frames = CountFramesToRest(rate);
   		std::printf("%3.0f  %6u  %8.3f  %8.3f\n", rate, frames, frames / rate, c_RestFrames / rate);
   	}
   	return 0;
   }
   ```

   ```text output-of="indirect-gi-limits-rest.cpp"
   fps  frames  clock(s)  count(s)
    30       8     0.267     1.000
    45      12     0.267     0.667
    75      19     0.253     0.400
    90      23     0.256     0.333
   ```

   1. **Lines 5-7:** the two waits, the clock's and the old count's.
   2. **Lines 15-19:** the loop adds one frame's time per frame and counts the frames.
   3. **Lines 29-30:** each row prints the frames, the clock's seconds and the count's seconds.
   ::::

3. **Hard.** Apply the patch that lowers `c_GIMoverRestSeconds` from 0.25 to 0.1. Predict whether the test `A moved proxy queues its old and new bounds` still passes, and what a door that swings back and forth with pauses of 0.15 s would cost the voxel passes. Then run the test.

   :::answer[Worked solution]{tests="movers off-is-invisible" solution="tutorials/indirect/gi-limits/exercise-3.patch"}
   The test passes: it sets the :term[frame time]{id=frame-time} to 0.4 times the constant and counts three frames, so it scales with the constant. With 0.25 s the door's pauses are too short to rest, so it stays a box: the dynamic layer writes its bricks, and no triangle makes voxels. With 0.1 s each pause counts as a rest: the door's triangles make voxels at each stop, its old bounds are cleared again at each start, and each hand-over fades for 0.25 s. The light beside the door steps more often. Run it with `StrataTests --test-case="A moved proxy queues its old and new bounds"`.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRenderData.h`: `c_GIMoverRestSeconds`, `c_GIMoverFadeSeconds`, `c_GIMaxMoverBoxes`.
- `Strata/src/Strata/Renderer/VoxelClipmap.cpp`: the rest clock of a moving proxy.
- `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp`: `FieldFullExtent`, `FieldFade` and the bounces of each row.
- `Strata/src/Strata/Renderer/SceneRendererGlobalIllumination.cpp`: the log of left-out submeshes.
- `Strata/shaders/Scene/Forward.frag.slang` and `Strata/shaders/Include/IndirectLight.slang`: the join.
- `PostProcessComponent::GlobalIllumination` and the quality row `Renderer.Quality.GlobalIllumination`.
- `StrataTests/src/Renderer/VoxelClipmapTests.cpp`: the suite `Renderer.VoxelClipmap`.
- `Docs/Releases/0.8.0.md`: the Known issues.

## Further reading

- Zander Majercik and others, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields" (2019): probe grids traced in the current scene; intermediate.
- Cyril Crassin and others, "Interactive Indirect Illumination Using Voxel Cone Tracing" (2011): a voxel copy of the world; advanced.
- Epic Games, the Unreal Engine documentation of Lumen: a shipped mix of tracing methods; beginner.
- The [Godot documentation of signed distance field global illumination](https://docs.godotengine.org/en/stable/tutorials/3d/global_illumination/using_sdfgi.html): a dynamic copy of the static world and its limits; beginner.
- The [Unity documentation of light probes](https://docs.unity3d.com/Manual/LightProbes.html): baked probes that moving objects read; beginner.
