---
id: image/tutorial-post-effect
title: "Tutorial: adding a post effect"
description: "Add a letterbox to Strata's renderer from the property to the tests: push constants, a shader, a pass in the post chain, a GPU stage and a GPU test."
kind: tutorial
size: L
tracks: [E]
needs: [image/taa, gpu/first-triangle, core/first-change]
time: 150
learn:
  - id: push-constants
    text: explain why a new post effect takes its parameters by push constants and never by new frame constant fields
  - id: post-source
    text: trace how a new pass reads the frame's post source and becomes the next post source
  - id: neutral-value
    text: build an effect that is off in the neutral test helper and renders bit for bit the same at its neutral value
  - id: failure-path
    text: predict what a frame shows when the new pass cannot make its resources
  - id: exact-test
    text: write a GPU test that checks the pixels of an effect exactly
since: 0.7.0
status: final
---

## What you will make

You will add a letterbox to Strata's :term[renderer]{id=renderer}: two black bars, one at the top and one at the bottom of the image, that crop it to a wider shape, as a cinema screen does. A new property of the Post Process component switches the effect on. A new pass in the post chain draws the bars.

::figure{id=result}

Here is the problem in numbers. The renderer draws a frame of 1920 by 1080 pixels, a ratio of 1.78 between width and height, while a film frame is wider, 2.39. A picture 1920 pixels wide and 2.39 times wider than tall is $1920 / 2.39 = 803.3$ rows high. The other $1080 - 803.3 = 276.7$ rows become bars: 138 rows above the picture and 138 below it. Your pass will compute that count and paint those rows black.

The editor's Game view also letterboxes: it fits a chosen aspect ratio into its panel. That is a choice of the panel around the image. No pass of Strata's renderer crops the image itself, and that is the pass you write here.

## The rules a new effect follows

Strata's guide for its developers states four rules for a new post effect. You meet each one again in a step.

1. The effect takes its parameters by :term[push constants]{id=push-constants}, or by a buffer of its own, and never by new fields of `FrameConstants`. The frame constants are one block that every scene pass reads. A new field would move the layout that all of those passes share.
2. The effect runs between the temporal anti-aliasing (:term[TAA]{id=taa}) resolve and the tone mapping, as [the page on the post chain](why-post.md) explains. It reads the frame's :term[post source]{id=post-source}, the texture that the passes before it wrote, and never a texture of its own choosing.
3. The effect is off in `Tests::AddNeutralPostProcess`, the helper that tests use to get exact colors.
4. The effect keeps the image bit for bit the same when its property has its neutral value. The tests compare images with exact values, so a default that changes one bit breaks them.

The chain after your change looks like the diagram. Because the new pass comes after the TAA resolve, the history of the TAA never contains bars: the pass works on a copy of the resolved image.

```mermaid caption="The post chain with the new pass: it comes after the motion blur and before the exposure, the bloom and the tone mapping." alt="A row of boxes joined by arrows: TAA resolve, depth of field, motion blur, the new letterbox, exposure, bloom, tone mapping, and anti-aliasing. The letterbox box has a different shade."
flowchart LR
  A[TAA resolve] --> B[Depth of field] --> C[Motion blur] --> D[Letterbox] --> E[Exposure] --> F[Bloom] --> G[Tone mapping] --> H[FXAA or morphological]
  style D fill:#fde68a,stroke:#92400e
```

## What you need

- The engine built from source and its tests passing, as [your first engine change](../core/first-change.md) builds them. The commands below write `<preset>` for your :term[CMake preset]{id=cmake-preset}, as that page does.
- The test of [the first triangle](../gpu/first-triangle.md): a :term[graphics processing unit]{id=gpu} (GPU) that the test suites can use, and the shared `Tests::GPUContext` it introduced.
- No file to import. You change :term[source files]{id=source-file} and one scene file of the feature test. The book's patch of the whole change, `tutorials/image/tutorial-post-effect.patch`, is the copy to compare with.
- About two and a half hours. Most of the time goes to builds, because the renderer's :term[header]{id=header} is included in many files.

:::files[The files you change or add]

- `Strata/src/Strata/Renderer/`
  - `RendererComponents.h`, `RendererComponents.cpp`: the property.
  - `PostProcessData.h`, `PostProcessMath.h`, `PostProcessMath.cpp`: the push constants and the bar rows.
  - `SceneRenderer.h`, `SceneRenderer.cpp`, `SceneRendererPost.cpp`: the pass.
- `Strata/shaders/PostProcess/`: the new :term[shader]{id=shader} `Letterbox.comp.slang`.
- `Strata/CMakeLists.txt`: the shader's entry.
- `StrataTests/`: tests, the neutral helper and the feature scene.

:::

## Add the property to the Post Process component

The effect needs two settings: whether it runs, and the aspect ratio of the picture. A switch that is off is the neutral value, so a scene saved before your change renders as it did. The aspect ratio matters only while the switch is on, and the inspector says so with an :term[inactive reason]{id=inactive-reason}.

:::::steps

1. Add two fields to `PostProcessComponent`, the component that holds every post-processing setting. Search for the default of each: `false` for the switch, so a scene without the property is unchanged.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-8"
    		// A lens's flares around very bright light (0: none): ghosts mirrored through the image's center, a halo and the
    		// directional light's starburst when its disk is in view. The bloom chain feeds them (it runs for them with Bloom off).
    		float LensFlare = 0.0f;
   +		// Letterbox (off by default): black bars at the top and bottom crop the image to LetterboxAspect, a width over a height; a
   +		// view that is already that wide or wider shows no bars.
   +		bool Letterbox = false;
   +		float LetterboxAspect = 2.39f;
    		float Saturation = 1.0f;
    		float Contrast = 1.0f; // Around middle gray; 1 = unchanged
    		// The Filmic curve's look, each in [0, 1]: how deep the shadows go (higher crushes the darkest tones) and how softly the
   ```

   1. **Line 6:** the switch is off by default: this is the neutral value.
   2. **Line 7:** 2.39 is a common film ratio.

   **You should see:** two new fields beside `LensFlare` in `RendererComponents.h`.

   **If you do not see it:** you edited another header. The path is `Strata/src/Strata/Renderer/RendererComponents.h`.

2. Write the function that gives the inactive reason. A reason is a sentence that the inspector shows beside a property that has no effect now, and the function returns an empty text when the property is active.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-6"
    			return post.MotionBlur ? std::string() : "Motion Blur is off";
    		}
    
   +		std::string WithLetterbox(const PostProcessComponent& post)
   +		{
   +			return post.Letterbox ? std::string() : "Letterbox is off";
   +		}
   +
    		std::string WithColorLookup(const PostProcessComponent& post)
    		{
    			return post.ColorLookup.IsValid() ? std::string() : "No Color Lookup is set";
   ```

   1. **Line 4:** the function reads the component and nothing else.
   2. **Line 6:** the sentence names the switch and says "off", as the other reasons do.

   **You should see:** `WithLetterbox` above `WithColorLookup` in `RendererComponents.cpp`.

   **If you do not see it:** the reason functions stand together near the top of the file, before the registration code.

3. Register both properties and attach the reason. The registration is what the [reflection system](../world/reflection.md) reads to save, show and set a property. The range of the aspect is 1 to 4, in steps of 0.01.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-7"
    			.Section("Lens")
    			.Property("LensFlare", &PostProcessComponent::LensFlare,
    				WithTooltip(Slider(0.0f, 1.0f), "A lens's flares around very bright light, with restraint: faint tinted ghosts mirrored through the "
   -					"image's center, a halo, and six rays around the sun's disk while it is in view and not covered. 0 none"));
   +					"image's center, a halo, and six rays around the sun's disk while it is in view and not covered. 0 none"))
   +			.Property("Letterbox", &PostProcessComponent::Letterbox,
   +				WithTooltip({}, "Black bars at the top and bottom crop the image to the aspect ratio below, as a cinema screen does; a view "
   +					"that is already that wide shows none"))
   +			.Property("LetterboxAspect", &PostProcessComponent::LetterboxAspect,
   +				WithTooltip(Range(1.0f, 4.0f, 0.01f), "The aspect ratio (width over height) of the picture between the bars: 2.39 is wide cinema"));
    		// Exposure is the compensation SceneRenderer applies with automatic exposure too: always active.
    		SetInactiveReasons<PostProcessComponent>({ "AutoExposureMinEV", "AutoExposureMaxEV", "AutoExposureSpeed", "AutoExposureMetering",
    			"AutoExposureLowPercentile", "AutoExposureHighPercentile", "AutoExposureLightSpeed", "AutoExposureKey" }, &WithAutoExposure);
    		SetInactiveReasons<PostProcessComponent>({ "BloomIntensity", "BloomThreshold", "BloomRadius" }, &WithBloom);
    		SetInactiveReasons<PostProcessComponent>({ "MotionBlurShutterAngle", "MotionBlurMaxLength" }, &WithMotionBlur);
   +		SetInactiveReasons<PostProcessComponent>({ "LetterboxAspect" }, &WithLetterbox);
    		SetInactiveReasons<PostProcessComponent>({ "ColorLookupIntensity" }, &WithColorLookup);
    		SetInactiveReasons<PostProcessComponent>({ "Toe" }, &WithFilmicToe);
    		SetInactiveReasons<PostProcessComponent>({ "Shoulder" }, &WithFilmicShoulder);
   ```

   1. **Line 6:** the switch is a `bool`, so it takes a tooltip and no range.
   2. **Line 10:** the range clamps a loaded value, so a scene file with an aspect of 100 loads as 4.
   3. **Line 16:** one call attaches the reason to the aspect.

   **You should see:** the registration of `Letterbox` and `LetterboxAspect` after `LensFlare`, and the reason call after the motion blur's.

   **If you do not see it:** the registration before yours must end with `))` and not `));`. The final character moves to your last property.

4. Build the test program and run the suite of the editor commands, which checks the inactive properties of a Post Process.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataTests --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=Editor.Commands
   ```

   The first command builds, and the second runs one suite. Read the failing checks: they list the inactive properties, and your new reason adds one to the list.

   **You should see:** the build succeeds, and the suite fails at the checks that list inactive properties, with `LetterboxAspect` in the failure text.

   **If you do not see it:** when the build fails, read the first error: a missing include or a wrong name of a field is the usual cause. When the suite passes, the reason call of the step before is missing.

   **Why:** a failing test that you did not write shows where your change reaches. You repair it next.

5. Add the new row to the three places in `EditorCommandTests.cpp` that list the inactive properties of a Post Process. The :term[diff]{id=diff} shows the first.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-28"
    		const nlohmann::json post = harness.Run("component.get", { { "entity", c }, { "component", "PostProcess" } });
    		CHECK(post["inactive"] == WithTemporalRows({ { "BloomIntensity", "Bloom is off" }, { "BloomThreshold", "Bloom is off" }, { "BloomRadius", "Bloom is off" },
    			{ "MotionBlurShutterAngle", "Motion Blur is off" }, { "MotionBlurMaxLength", "Motion Blur is off" },
   -			{ "ColorLookupIntensity", "No Color Lookup is set" }, { "GlobalIlluminationIntensity", "Global Illumination is off" } }, c_OnlyTAA));
   +			{ "ColorLookupIntensity", "No Color Lookup is set" }, { "GlobalIlluminationIntensity", "Global Illumination is off" },
   +			{ "LetterboxAspect", "Letterbox is off" } }, c_OnlyTAA));
    		CHECK(harness.Run("entity.get", { { "entity", c } })["inactive"] == nlohmann::json { { "PostProcess", post["inactive"] } });
    		harness.Run("component.remove", { { "entity", c }, { "component", "PostProcess" } });
    		CHECK_FALSE(harness.Run("entity.get", { { "entity", c } }).contains("inactive"));
   ```

   The other two lists get the same row, `{ "LetterboxAspect", "Letterbox is off" }`, before their closing brackets. The patch file shows both.

   **You should see:** the suite `Editor.Commands` passes when you rebuild and run it.

   **If you do not see it:** a failure that still names a row means that one of the three lists keeps its old text.

6. Add the property to two more tests. The reflection test checks the reason in both states of the switch.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-35"
    		// The motion blur's shutter and length only with motion blur.
    		CHECK(reason("PostProcess", "MotionBlurShutterAngle") == "Motion Blur is off");
    		CHECK(reason("PostProcess", "MotionBlurMaxLength") == "Motion Blur is off");
   +		// The letterbox's aspect only with the letterbox.
   +		CHECK(reason("PostProcess", "LetterboxAspect") == "Letterbox is off");
   +		post.Letterbox = true;
   +		CHECK(reason("PostProcess", "LetterboxAspect").empty());
   +		post.Letterbox = false;
    		post.MotionBlur = true;
    		CHECK(reason("PostProcess", "MotionBlurShutterAngle").empty());
    		post.MotionBlur = false;
   ```

   1. **Line 5:** with the switch off, the aspect has the reason.
   2. **Line 7:** with the switch on, the reason is gone.

   The test of the groups of the inspector, in `RendererComponentsTests.cpp`, gains `{ "Letterbox", "Lens" }` and `{ "LetterboxAspect", "Lens" }` in its table.

   **You should see:** `Renderer.Components` and `Scene.InactiveProperties` pass when you run them as in step 4.

   **If you do not see it:** the files are in `StrataTests/src/Renderer/` and `StrataTests/src/Scene/`.

:::::

## Choose the bar rows and the push constants

The shader needs one number: the rows of each bar. The :term[central processing unit]{id=processor} (:term[CPU]{id=processor}) calculates it, because the same number also decides whether the pass runs at all. Calculate it by hand first.

Take a smaller image of 1024 by 576 pixels and an aspect of 2. The picture is $1024 / 2 = 512$ rows high. The spare rows are $576 - 512 = 64$, and half of them, 32, go above and 32 below.

$$r = \left\lfloor \frac{h - w / a}{2} \right\rfloor$$

The symbol $r$ is the rows of each bar. The symbol $h$ is the image height in pixels, $w$ is its width in pixels, and $a$ is the aspect ratio, a number without a unit. The brackets $\lfloor x \rfloor$ round $x$ down to a whole number. For 1920 by 1080 and $a = 2.39$, the formula gives $\lfloor 138.3 \rfloor = 138$, as in the example at the start.

Check the limits. When $w / a$ is larger than $h$, the image is already wider than the aspect, the spare space is negative, and the answer must be 0: no bars, no pass. When $a$ is huge, $w / a$ approaches 0, and the code keeps at least one row of picture.

:::::steps

1. Declare the function in the header of the :term[CPU twins]{id=cpu-twin} of the :term[post passes]{id=post-pass}' math. A twin is code that calculates on the CPU what a shader calculates on the GPU, so that a test can check it. Here the twin also decides whether the pass runs.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-5"
    	};
    	MotionBlurProfile GetMotionBlurProfile(float lengthPixels, uint32_t sampleCount);
    
   +	// The rows of each black bar that crop a `width` by `height` image to `aspect` (width over height): 0 when the image is not
   +	// taller than that (or `aspect` is not a positive number), and always at least one row of picture.
   +	uint32_t GetLetterboxBarRows(uint32_t width, uint32_t height, float aspect);
   +
    }
   ```

   The comment states the promises: 0 for a wide image, 0 for a bad aspect, and a row of picture always.

   **You should see:** the declaration at the end of `PostProcessMath.h`, inside the :term[namespace]{id=namespace}.

   **If you do not see it:** the namespace is `Strata::PostProcessMath`; the function goes before its closing brace.

2. Write the function in `PostProcessMath.cpp`.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-4"
    		return glm::clamp(FilmicConstants::c_Outset * glm::mix(whole, perChannel, channel), glm::vec3(0.0f), glm::vec3(1.0f));
    	}
    
   +	uint32_t GetLetterboxBarRows(uint32_t width, uint32_t height, float aspect)
   +	{
   +		if (width == 0 || height < 3 || !std::isfinite(aspect) || aspect <= 0.0f)
   +			return 0;
   +		const float spare = static_cast<float>(height) - static_cast<float>(width) / aspect;
   +		if (!(spare >= 2.0f))
   +			return 0;
   +		return std::min(static_cast<uint32_t>(spare * 0.5f), (height - 1) / 2);
   +	}
   +
    }
   ```

   1. **Line 6:** a bad aspect (not a number, zero or negative) and a tiny image return 0 before any division.
   2. **Line 8:** the spare rows, in :term[floating point]{id=floating-point-number}: the height minus the height of the picture.
   3. **Line 9:** less than two spare rows hold no bar. The written form also catches a value that is not a number.
   4. **Line 11:** half of the spare rows, rounded down, and never more than half of the height minus one.

   **You should see:** the function after `ApplyFilmic`.

   **If you do not see it:** the file ends with the closing brace of the namespace; the function goes before it.

3. Write the test with the numbers you calculated: both examples, the limits and a bad aspect.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-32"
    			spread16 = std::max(spread16, value);
    		CHECK(spread16 < spread8);
    	}
   +
   +	TEST_CASE("The letterbox's bars crop the image to the aspect and leave rows of picture")
   +	{
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1024, 576, 2.0f) == 32);
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, 2.39f) == 138);
   +		// A view as wide as the aspect, or wider, or a bad aspect: no bars.
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, 16.0f / 9.0f) == 0);
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, 1.0f) == 0);
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, 0.0f) == 0);
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, std::numeric_limits<float>::quiet_NaN()) == 0);
   +		// An absurd aspect keeps two rows of picture.
   +		CHECK(PostProcessMath::GetLetterboxBarRows(1920, 1080, 1000.0f) == 539);
   +	}
    }
   ```

   1. **Lines 7–8:** the two examples of this section.
   2. **Line 15:** at an aspect of 1000 the picture is 1.92 rows high, so the formula says 539.04 and the cap leaves two rows of picture.

   **You should see:** build, then run `StrataTests --test-suite=Renderer.PostProcessMath`. The suite passes with one more test case.

   **If you do not see it:** a failing check shows the value the function returned. Compare it with your hand calculation before you change the test.

4. Declare the push constants. :term[NVRHI]{id=nvrhi} allows push constants of at most 128 :term[bytes]{id=byte}, so a pass with few parameters uses them. A pass with more, as the tone mapping, uses a :term[constant buffer]{id=constant-buffer} of its own.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-3"
    		static_assert(offsetof(TonemapConstants, Operator) == 16 && offsetof(TonemapConstants, DitherLevels) == 32);
    		static_assert(offsetof(TonemapConstants, VignetteTangents) == 40 && offsetof(TonemapConstants, FilmicToeSlope) == 48);
    
   +		// PostProcess/Letterbox.comp (push constants).
   +		struct LetterboxParameters
   +		{
   +			uint32_t BarRows; // Rows of each black bar, at the top and at the bottom of the image
   +			uint32_t Padding0;
   +			uint32_t Padding1;
   +			uint32_t Padding2;
   +		};
   +		static_assert(sizeof(LetterboxParameters) == 16);
   +		static_assert(offsetof(LetterboxParameters, BarRows) == 0);
   +
    		// PostProcess/MorphologicalEdges.frag and MorphologicalBlend.frag (push constants): the edges' thresholds (a luma
    		// difference of the display-encoded image; a depth jump beyond the neighboring steps, relative to the depth) and the blend's
    		// dither.
   ```

   1. **Line 7:** `BarRows` is the only parameter.
   2. **Lines 8–10:** padding keeps the size a multiple of 16 bytes, which the shader's declaration and the host both assume.
   3. **Lines 12–13:** the `static_assert` lines stop the build when the size or the offset changes without the shader.

   **You should see:** the :term[struct]{id=struct} between the tone mapping's asserts and the morphological block.

   **If you do not see it:** the file is `PostProcessData.h`; the structs of the passes follow each other there.

:::::

## Write the shader and register it

A compute shader runs one small program for each pixel. Yours reads a pixel of the source and writes it to the output, unless the pixel lies in a bar, where it writes black. The build compiles each file that `strata_add_shaders` lists.

:::::steps

1. Create the file `Letterbox.comp.slang` in the folder `Strata/shaders/PostProcess/`. All of its lines are new.

   ```slang src="book:tutorials/image/tutorial-post-effect/Letterbox.comp.slang#L1-L28"
   #include "Include/Common.slang"

   // The letterbox: black bars over the first and the last BarRows rows of the post source, written into the next source. Every
   // other texel is copied as it is, alpha included (the depth of field's and the motion blur's mark of what they blurred).

   Texture2D<float4> u_Source : register(t0);
   [vk::image_format("rgba16f")] RWTexture2D<float4> o_Output : register(u0);

   struct LetterboxParameters
   {
   	uint BarRows; // Rows of each bar
   	uint Padding0;
   	uint Padding1;
   	uint Padding2;
   };
   [[vk::push_constant]] ConstantBuffer<LetterboxParameters> u_Parameters;

   [numthreads(8, 8, 1)]
   void main(uint3 globalID : SV_DispatchThreadID)
   {
   	uint2 size;
   	u_Source.GetDimensions(size.x, size.y);
   	if (any(globalID.xy >= size))
   		return;
   	float4 color = u_Source.Load(int3(globalID.xy, 0));
   	bool inBar = globalID.y < u_Parameters.BarRows || globalID.y >= size.y - u_Parameters.BarRows;
   	o_Output[globalID.xy] = float4(inBar ? float3(0.0) : SanitizeHDR(color.rgb), color.a);
   }
   ```

   1. **Line 6:** slot `t0` is the source to read; slot `u0` is the output to write.
   2. **Line 16:** `[[vk::push_constant]]` marks the constant block as push constants, which the host writes with `setPushConstants`.
   3. **Lines 23–24:** a pixel outside the image does nothing. Threads start in groups of 8 by 8, so the last groups reach past the edge of an image whose size is not a multiple of 8.
   4. **Lines 26–27:** a bar row is black, any other pixel is a copy through `SanitizeHDR`, and the alpha channel passes through.

   **You should see:** a new file of 28 lines.

   **If you do not see it:** the name matters. The pipeline asks for `PostProcess/Letterbox.comp`, and the build adds `.slang`.

   **Why:** the copy keeps alpha because the depth of field and the motion blur use it to mark what they blurred, and the tone mapping reads that mark.

2. List the shader in `strata_add_shaders`, after the motion blur's.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-1"
    		PostProcess/MotionBlurTiles.comp
    		PostProcess/MotionBlurNeighbors.comp
    		PostProcess/MotionBlur.comp
   +		PostProcess/Letterbox.comp
    		PostProcess/DepthOfFieldPrepare.comp
    		PostProcess/DepthOfFieldTiles.comp
    		PostProcess/DepthOfFieldDilate.comp
   ```

   The entry names the file without `.slang`. A shader that is not in the list is never compiled or embedded.

   **You should see:** the new line between `MotionBlur.comp` and the depth of field's shaders.

   **If you do not see it:** the list is in `Strata/CMakeLists.txt`, in the call that names `Strata_Renderer`.

3. Run the :term[configure step]{id=configure-step} again and build the engine library.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --target Strata --parallel
   ```

   The first command reads the new file list. The second compiles the shader with :term[Slang]{id=slang}, and then the renderer's sources.

   **You should see:** the build ends without errors, and Slang reports nothing for `Letterbox.comp.slang`.

   **If you do not see it:** a shader error names the file and a line. Compare your file with the listing, including the first line.

:::::

## Declare the pass and its source

The renderer keeps one variable, the post source, that names the texture the next pass reads. Every pass that reads it owns one :term[binding set]{id=binding-set} for each possible source, because a binding set holds the exact texture. A new source needs a new name, and every reader of the source learns it.

:::::steps

1. Add `Letterbox` to the list of sources and extend `SelectPostSet`, the function that picks a set, by one argument.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-11"
    		bool CreatePostTargets(uint32_t width, uint32_t height, std::string& outFailure);
    		void ReleasePostTargets(std::vector<nvrhi::ResourceHandle>& released);
    		// What post-processing reads after the TAA resolve: the HDR target, the TAA's newest history texture, or the output of the
   -		// depth of field or of the motion blur. Each pass that reads it has a binding set per source.
   +		// depth of field, of the motion blur or of the letterbox. Each pass that reads it has a binding set per source.
    		enum class PostSource : uint8_t
    		{
    			HDR,
    			History,
    			DepthOfField,
   -			MotionBlur
   +			MotionBlur,
   +			Letterbox
    		};
    		// The set of `source` among a pass's sets per source (the history's: the newest texture's).
    		nvrhi::IBindingSet* SelectPostSet(PostSource source, nvrhi::IBindingSet* hdr, const std::array<nvrhi::BindingSetHandle, 2>& history,
   -			nvrhi::IBindingSet* depthOfField, nvrhi::IBindingSet* motionBlur) const;
   +			nvrhi::IBindingSet* depthOfField, nvrhi::IBindingSet* motionBlur, nvrhi::IBindingSet* letterbox = nullptr) const;
    		// The exposure and the bloom of the post source; returns whether bloom ran. `keyReferenceLog2`: log2 of the luminance of a
    		// gray card facing the frame's directional light (unset without one).
    		// `sunUV`: where the directional light's disk is, when it is in front of the camera (the lens flare's starburst). Sets
   ```

   1. **Line 13:** the new source, after `MotionBlur`.
   2. **Line 18:** the new argument has a default of `nullptr`, so the caller that cannot see the letterbox, the motion blur, stays as it is.

   **You should see:** the enum with five names.

   **If you do not see it:** the enum is `PostSource` in `SceneRenderer.h`, near `CreatePostTargets`.

2. Teach the function about the new source. In `SceneRendererPost.cpp`, give its definition the same fifth argument, without the default, and add a case.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-17"
    				return depthOfField;
    			case PostSource::MotionBlur:
    				return motionBlur;
   +			case PostSource::Letterbox:
   +				return letterbox;
    		}
    		return hdr;
    	}
   ```

   Without the case, GCC and Clang warn about a `switch` that omits a name of the enum, and Strata's automatic builds on Linux and macOS turn the warning into an error. The Microsoft :term[compiler]{id=compiler} gives no such warning at its level 4, so on Windows count the cases yourself.

   **You should see:** the function with a fifth argument and a fifth case.

   **If you do not see it:** the definition is near the top of the file, after the release functions of the post targets.

3. Declare the three new functions of the pass.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-12"
    		bool EnsureMotionBlurResources();
    		// The motion blur's targets and sets (made again by the next frame that blurs).
    		void ReleaseMotionBlurTargets(std::vector<nvrhi::ResourceHandle>& released);
   +		// The letterbox of the post source (HDR, History, DepthOfField or MotionBlur) into m_LetterboxTexture: `barRows` black rows at
   +		// the top and at the bottom. False (reported) when its resources cannot be made: the frame shows the image without bars.
   +		bool RenderLetterbox(nvrhi::ICommandList* commandList, PostSource source, uint32_t barRows);
   +		bool EnsureLetterboxResources();
   +		// The target and the sets of its output.
   +		bool CreateLetterboxTarget();
   +		// The letterbox's target and sets (made again by the next frame that draws bars).
   +		void ReleaseLetterboxTargets(std::vector<nvrhi::ResourceHandle>& released);
    		// The players' quality rows applied to the scene's settings: the anti-aliasing method they chose and their motion blur.
    		static void ApplyQualityOverrides(PostProcessComponent& settings, const RendererQualitySettings& quality);
    		// Tone mapping of the post source into `output`, or into the LDR target and FXAA from it into `output` (FXAA unless the frame
   ```

   1. **Line 6:** `RenderLetterbox` records the pass; it returns `false` when its resources cannot be made.
   2. **Line 9:** `CreateLetterboxTarget` makes the target and the sets of the output.

   **You should see:** the new block beside the motion blur's declarations.

   **If you do not see it:** the block goes between `ReleaseMotionBlurTargets` and `ApplyQualityOverrides`.

4. Declare the members of the pass.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-13"
    		nvrhi::BindingSetHandle m_DepthOfFieldExposureSet;
    		nvrhi::BindingSetHandle m_DepthOfFieldBloomSet;
    		nvrhi::BindingSetHandle m_DepthOfFieldTonemapSet;
   +		// Letterbox (SceneRendererPost.cpp): its layout and pipeline, its target (made by the first frame that draws bars, released
   +		// with the render targets), its sets per source (HDR, History 0, History 1, the depth of field's output, the motion blur's)
   +		// and the post sets of its output (exposure, bloom's prefilter, tone mapping).
   +		nvrhi::BindingLayoutHandle m_LetterboxLayout;
   +		nvrhi::ComputePipelineHandle m_LetterboxPipeline;
   +		nvrhi::TextureHandle m_LetterboxTexture;
   +		std::array<nvrhi::BindingSetHandle, 5> m_LetterboxSets;
   +		nvrhi::BindingSetHandle m_LetterboxExposureSet;
   +		nvrhi::BindingSetHandle m_LetterboxBloomSet;
   +		nvrhi::BindingSetHandle m_LetterboxTonemapSet;
   +		bool m_LetterboxBlurMask = false; // The letterbox's source marked what it blurred in alpha, which the output keeps
    		nvrhi::FramebufferHandle m_LDRFramebuffer;
    		bool m_ResetExposure = true;
    		// The pre-exposure (SceneRendererStats::PreExposure): the value frames are drawn with; whether it settled; a reset asked
   ```

   1. **Line 10:** one set for each source: the image of :term[high dynamic range]{id=high-dynamic-range} (HDR), two history textures, the output of the depth of field and the output of the motion blur.
   2. **Lines 11–13:** three sets for the readers that follow: the exposure, the bloom and the tone mapping.
   3. **Line 14:** the flag is explained in the last step of the section that records the pass.

   **You should see:** the block after the depth of field's members.

   **If you do not see it:** the members are in `SceneRenderer.h`, near `m_DepthOfFieldTonemapSet`.

:::::

## Create the pass's resources

Everything the pass needs is made once and kept: the layout and the pipeline when the renderer starts, the target and the sets at the first frame that draws bars. When something cannot be made, the pass reports it, returns `false`, and the frame continues without bars.

:::::steps

1. Create the layout and the pipeline in `CreatePostResources`, beside the motion blur's.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-14"
    		m_MotionBlurTilesPipeline = CreateComputePipeline("PostProcess/MotionBlurTiles.comp", m_MotionBlurLayout);
    		m_MotionBlurNeighborsPipeline = CreateComputePipeline("PostProcess/MotionBlurNeighbors.comp", m_MotionBlurLayout);
    		m_MotionBlurPipeline = CreateComputePipeline("PostProcess/MotionBlur.comp", m_MotionBlurLayout);
   +		// Letterbox: the source, the target and the bar rows.
   +		nvrhi::BindingLayoutDesc letterboxLayout;
   +		letterboxLayout.visibility = nvrhi::ShaderType::Compute;
   +		letterboxLayout.bindings = { nvrhi::BindingLayoutItem::Texture_SRV(0), nvrhi::BindingLayoutItem::Texture_UAV(0),
   +			nvrhi::BindingLayoutItem::PushConstants(0, sizeof(RenderData::LetterboxParameters)) };
   +		m_LetterboxLayout = m_Device->createBindingLayout(letterboxLayout);
   +		ST_CORE_VERIFY(m_LetterboxLayout, "SceneRenderer: failed to create the letterbox's layout");
   +		m_LetterboxPipeline = CreateComputePipeline("PostProcess/Letterbox.comp", m_LetterboxLayout);
    		// Depth of field: one layout for its five passes, as the motion blur's; the composite's bilinear reads use the linear
    		// clamping sampler at Include/Scene.slang's slot 8.
    		nvrhi::BindingLayoutDesc depthOfFieldLayout;
   ```

   1. **Lines 7–8:** the layout lists what the shader binds: a texture to read, a texture to write and the push constants at slot 0.
   2. **Line 10:** a layout that cannot be made stops the renderer, as the other layouts do, because it means a mistake of a programmer.
   3. **Line 11:** the pipeline is made from the shader's name. A shader missing from the build stops the renderer too; a pipeline that the device cannot make is a null handle that a later step checks.

   **You should see:** the new lines after the motion blur's pipelines.

   **If you do not see it:** `CreatePostResources` is in `SceneRendererPost.cpp`, and the motion blur's layout is a few lines above the depth of field's.

2. Write the function that makes the target and the sets of its output.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-20"
    		return true;
    	}
    
   +	bool SceneRenderer::CreateLetterboxTarget()
   +	{
   +		const uint32_t width = m_ViewportSize.x;
   +		const uint32_t height = m_ViewportSize.y;
   +		nvrhi::TextureDesc desc;
   +		desc.width = std::max(width, 1u);
   +		desc.height = std::max(height, 1u);
   +		desc.format = c_HDRFormat;
   +		desc.isUAV = true;
   +		desc.debugName = m_Specification.DebugName + ".Letterbox";
   +		desc.initialState = nvrhi::ResourceStates::ShaderResource;
   +		desc.keepInitialState = true;
   +		nvrhi::TextureHandle letterboxed = m_Device->createTexture(desc);
   +		if (!letterboxed)
   +		{
   +			m_Errors.Report(fmt::format("failed to create the letterbox's target for a {}x{} viewport; drawing without the letterbox", width, height));
   +			return false;
   +		}
   +		// The output as the post source, as the HDR target's sets (CreatePostTargets).
   +		nvrhi::BindingSetDesc exposure;
   +		exposure.bindings = { nvrhi::BindingSetItem::Texture_SRV(0, letterboxed), nvrhi::BindingSetItem::StructuredBuffer_UAV(0, m_HistogramBuffer),
   +			nvrhi::BindingSetItem::StructuredBuffer_UAV(1, m_ExposureBuffer), nvrhi::BindingSetItem::PushConstants(0, sizeof(RenderData::ExposureParameters)) };
   +		nvrhi::BindingSetDesc bloom;
   +		bloom.bindings = { nvrhi::BindingSetItem::Texture_SRV(0, letterboxed), nvrhi::BindingSetItem::Sampler(0, m_LinearClampSampler),
   +			nvrhi::BindingSetItem::Texture_UAV(0, m_BloomTexture, nvrhi::Format::UNKNOWN, nvrhi::TextureSubresourceSet(0, 1, 0, 1)),
   +			nvrhi::BindingSetItem::StructuredBuffer_SRV(1, m_ExposureBuffer), nvrhi::BindingSetItem::PushConstants(0, sizeof(RenderData::BloomParameters)) };
   +		nvrhi::BindingSetDesc tonemap;
   +		tonemap.bindings = { nvrhi::BindingSetItem::Texture_SRV(0, letterboxed), nvrhi::BindingSetItem::Sampler(0, m_PointClampSampler),
   +			nvrhi::BindingSetItem::Texture_SRV(1, m_BloomTexture, nvrhi::Format::UNKNOWN, nvrhi::TextureSubresourceSet(0, 1, 0, 1)),
   +			nvrhi::BindingSetItem::Sampler(1, m_LinearClampSampler), nvrhi::BindingSetItem::StructuredBuffer_SRV(2, m_ExposureBuffer),
   +			nvrhi::BindingSetItem::ConstantBuffer(0, m_TonemapConstantBuffer) };
   +		nvrhi::BindingSetHandle exposureSet = m_Device->createBindingSet(exposure, m_ExposureBindingLayout);
   +		nvrhi::BindingSetHandle bloomSet = m_Device->createBindingSet(bloom, m_BloomBindingLayout);
   +		nvrhi::BindingSetHandle tonemapSet = m_Device->createBindingSet(tonemap, m_TonemapBindingLayout);
   +		if (!exposureSet || !bloomSet || !tonemapSet)
   +		{
   +			m_Errors.Report(fmt::format("failed to create the letterbox's bindings for a {}x{} viewport; drawing without the letterbox", width, height));
   +			return false;
   +		}
   +		m_LetterboxTexture = std::move(letterboxed);
   +		m_LetterboxExposureSet = std::move(exposureSet);
   +		m_LetterboxBloomSet = std::move(bloomSet);
   +		m_LetterboxTonemapSet = std::move(tonemapSet);
   +		return true;
   +	}
   +
    	bool SceneRenderer::RenderMotionBlur(nvrhi::ICommandList* commandList, const PostProcessComponent& postProcess, PostSource source)
    	{
    		if (!EnsureMotionBlurResources())
   ```

   1. **Lines 8–15:** the target has the format of the :term[HDR image]{id=hdr-image}, and a shader may write it.
   2. **Lines 17–21:** when it cannot be made, the function reports why and returns `false`.
   3. **Lines 22–37:** three sets bind the new texture for the readers that follow, as the HDR target's sets do.
   4. **Lines 38–42:** a set that fails makes the whole function fail, before anything is kept.

   **You should see:** the function before `RenderMotionBlur`.

   **If you do not see it:** any place at function level works; this one keeps the post passes together.

3. Write the function that releases the target and the function that makes everything the pass needs.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-21"
    		return true;
    	}
    
   +	void SceneRenderer::ReleaseLetterboxTargets(std::vector<nvrhi::ResourceHandle>& released)
   +	{
   +		auto release = [&released](auto& handle)
   +		{
   +			if (handle)
   +				released.emplace_back(handle.Get());
   +			handle = nullptr;
   +		};
   +		release(m_LetterboxTexture);
   +		for (nvrhi::BindingSetHandle& set : m_LetterboxSets)
   +			release(set);
   +		release(m_LetterboxExposureSet);
   +		release(m_LetterboxBloomSet);
   +		release(m_LetterboxTonemapSet);
   +	}
   +
   +	bool SceneRenderer::EnsureLetterboxResources()
   +	{
   +		if (!m_LetterboxPipeline)
   +		{
   +			m_Errors.Report("the letterbox's pipeline could not be made; drawing without the letterbox");
   +			return false;
   +		}
   +		if (!m_LetterboxTexture && !CreateLetterboxTarget())
   +			return false;
   +		// The pass's set per source, once the source exists: the HDR target, the TAA's two history textures, the depth of field's
   +		// and the motion blur's outputs.
   +		nvrhi::ITexture* const sources[] = { m_HDRTexture.Get(), m_HistoryTextures[0].Get(), m_HistoryTextures[1].Get(), m_DepthOfFieldTexture.Get(),
   +			m_MotionBlurTexture.Get() };
   +		for (size_t index = 0; index < m_LetterboxSets.size(); index++)
   +		{
   +			if (!sources[index] || m_LetterboxSets[index])
   +				continue;
   +			nvrhi::BindingSetDesc desc;
   +			desc.bindings = { nvrhi::BindingSetItem::Texture_SRV(0, sources[index]), nvrhi::BindingSetItem::Texture_UAV(0, m_LetterboxTexture),
   +				nvrhi::BindingSetItem::PushConstants(0, sizeof(RenderData::LetterboxParameters)) };
   +			m_LetterboxSets[index] = m_Device->createBindingSet(desc, m_LetterboxLayout);
   +			if (!m_LetterboxSets[index])
   +			{
   +				m_Errors.Report("failed to create the letterbox's bindings of its source; drawing without the letterbox");
   +				return false;
   +			}
   +		}
   +		return true;
   +	}
   +
    	bool SceneRenderer::EnsureDepthOfFieldResources()
    	{
    		const uint32_t width = m_ViewportSize.x;
   ```

   1. **Lines 6–11:** a handle goes to the renderer's :term[deferred release]{id=deferred-release} and is never destroyed at once, because the GPU may still read it.
   2. **Lines 22–26:** a pipeline that could not be made is reported and ends the pass for this frame.
   3. **Lines 29–46:** the set of each source is made when the source exists: the history textures and the two outputs appear later than the HDR target.

   **You should see:** two functions before `EnsureDepthOfFieldResources`.

   **If you do not see it:** the release :term[lambda]{id=lambda} is the same as in the motion blur's release function.

4. Release the sets of the pass where the textures they bind are released. The output of the motion blur goes when the motion blur releases its targets, and a set that kept it would read a dead texture.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-18"
    		release(m_MotionBlurExposureSet);
    		release(m_MotionBlurBloomSet);
    		release(m_MotionBlurTonemapSet);
   +		// The letterbox's set of the motion blur's output binds it: made again with the next one.
   +		release(m_LetterboxSets[4]);
    	}
    
    	void SceneRenderer::ReleaseDepthOfFieldTargets(std::vector<nvrhi::ResourceHandle>& released)
   ```

   The same holds for the output of the depth of field, whose set number 3 goes in `ReleaseDepthOfFieldTargets`. One call, `ReleaseLetterboxTargets(released)`, also joins the release of the post targets when the viewport changes size.

   **You should see:** three small changes in `SceneRendererPost.cpp`.

   **If you do not see it:** search for `release(m_MotionBlurTonemapSet)`, for `release(m_MotionBlurGatherSets[3])` and for `ReleaseDepthOfFieldTargets(released);`.

:::::

## Record the pass in the frame

Now the pass runs. `RenderFrame` already switches the source after the depth of field and the motion blur. Read that block first: it is the pattern to copy.

```cpp src="Strata/src/Strata/Renderer/SceneRenderer.cpp#L3796-L3818"
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
gpuTimer.Next(gpuStages.Post);
```

1. **Line 3797:** the source starts as the history of the TAA, or the HDR image when no resolve happened.
2. **Lines 3802–3805:** the pass returns whether it worked. On success the source changes, and on failure `degraded` is set.
3. **Line 3818:** from here on, the time belongs to the Post stage of the GPU.

:::::steps

1. Write the pass. It checks its resources, picks the set of the current source, fills the push constants and dispatches.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-22"
    		return true;
    	}
    
   +	bool SceneRenderer::RenderLetterbox(nvrhi::ICommandList* commandList, PostSource source, uint32_t barRows)
   +	{
   +		ST_CORE_ASSERT(source != PostSource::Letterbox, "SceneRenderer: the letterbox does not read its own output");
   +		if (!EnsureLetterboxResources())
   +			return false;
   +		size_t sourceIndex = 0;
   +		switch (source)
   +		{
   +			case PostSource::HDR:
   +				sourceIndex = 0;
   +				break;
   +			case PostSource::History:
   +				sourceIndex = 1 + m_HistoryIndex;
   +				break;
   +			case PostSource::DepthOfField:
   +				sourceIndex = 3;
   +				break;
   +			case PostSource::MotionBlur:
   +				sourceIndex = 4;
   +				break;
   +			case PostSource::Letterbox:
   +				break;
   +		}
   +		if (!m_LetterboxSets[sourceIndex])
   +		{
   +			m_Errors.Report("the letterbox's source has no bindings; drawing without the letterbox");
   +			return false;
   +		}
   +		RenderData::LetterboxParameters parameters = {};
   +		parameters.BarRows = barRows;
   +		nvrhi::ComputeState state;
   +		state.pipeline = m_LetterboxPipeline;
   +		state.bindings = { m_LetterboxSets[sourceIndex] };
   +		commandList->setComputeState(state);
   +		commandList->setPushConstants(&parameters, sizeof(parameters));
   +		commandList->dispatch(DispatchGroups(m_ViewportSize.x), DispatchGroups(m_ViewportSize.y), 1);
   +		// The depth of field's and the motion blur's alpha marks what they blurred; the shader keeps it.
   +		m_LetterboxBlurMask = source == PostSource::DepthOfField || source == PostSource::MotionBlur;
   +		return true;
   +	}
   +
    	bool SceneRenderer::EnsureMorphologicalResources(nvrhi::ICommandList* commandList)
    	{
    		if (m_MorphologicalEdges)
   ```

   1. **Line 7:** a failure of the resources returns `false`, and the caller keeps the old source.
   2. **Lines 9–26:** the set depends on the source. The history has two textures, and `m_HistoryIndex` names the newest.
   3. **Lines 27–31:** a source without a set is also a failure, reported once.
   4. **Line 39:** `DispatchGroups` turns pixels into groups of 8 threads.
   5. **Line 41:** the flag remembers whether the source carried the blur mark in its alpha.

   **You should see:** the function between the depth of field's pass and `EnsureMorphologicalResources`.

   **If you do not see it:** the `switch` needs every name of the enum; without the `Letterbox` case GCC and Clang warn.

2. Call the pass from `RenderFrame`, right after `gpuTimer.Next(gpuStages.Post)`.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-10"
    			commandList->endMarker();
    		}
    		gpuTimer.Next(gpuStages.Post);
   +		// The letterbox: bars over the post source, which then is the letterbox's output. A frame whose image is as wide as the
   +		// aspect has no bars to draw.
   +		const uint32_t letterboxRows = postProcess.Letterbox ? PostProcessMath::GetLetterboxBarRows(m_ViewportSize.x, m_ViewportSize.y, postProcess.LetterboxAspect) : 0u;
   +		if (letterboxRows > 0)
   +		{
   +			commandList->beginMarker("Letterbox");
   +			if (RenderLetterbox(commandList, postSource, letterboxRows))
   +				postSource = PostSource::Letterbox;
   +			else
   +				degraded = true;
   +			commandList->endMarker();
   +		}
    		// The exposure key's reference: the luminance of a gray card (albedo 0.18) facing the directional light, as Forward.frag
    		// lights it (the atmosphere's transmittance included); none without a light.
    		std::optional<float> keyReferenceLog2;
   ```

   1. **Lines 6–7:** the pass runs only when the effect is on and the bars have at least one row.
   2. **Lines 10–13:** the pattern of the depth of field: the source changes on success, and `degraded` marks a frame without bars on failure.

   **You should see:** the block between `gpuTimer.Next(gpuStages.Post)` and the comment of the :term[exposure key]{id=exposure-key}.

   **If you do not see it:** a build error about `GetLetterboxBarRows` means that the include of the next step is missing.

   **Why:** `degraded` is the renderer's way to say that a frame is complete but lacks something. A degraded frame keeps its errors, and they clear only on a frame without a failure.

3. Include the header of the math functions in `SceneRenderer.cpp`.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-9"
    #include "Strata/Renderer/LODSelection.h"
    #include "Strata/Renderer/Material.h"
    #include "Strata/Renderer/Mesh.h"
   +#include "Strata/Renderer/PostProcessMath.h"
    #include "Strata/Renderer/RenderScene.h"
    #include "Strata/Renderer/RenderSceneGPU.h"
    #include "Strata/Renderer/Renderer.h"
   ```

   The includes follow the order of their names, so `PostProcessMath.h` stands after `Mesh.h`.

   **You should see:** one new include line.

   **If you do not see it:** the include list is at the top, after `stpch.h` and the file's own header.

4. Hand the new source to the three readers: the exposure, the bloom and the tone mapping. Each takes its set from `SelectPostSet`, and each now passes the set of the letterbox as the last argument. The diff shows the tone mapping's.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-26"
    		m_TonemapConstantsWritten = true;
    		DrawFullscreen(commandList, GetFullscreenPipeline(m_TonemapPipelines, m_TonemapPixelShader, { m_TonemapBindingLayout, m_TonemapInputLayout },
    			tonemapTarget->getFramebufferInfo()), tonemapTarget, SelectPostSet(source, m_TonemapBindingSet, m_TemporalTonemapSets, m_DepthOfFieldTonemapSet,
   -			m_MotionBlurTonemapSet), nullptr, 0, inputSet);
   +			m_MotionBlurTonemapSet, m_LetterboxTonemapSet), nullptr, 0, inputSet);
    		commandList->endMarker();
    		if (morphological)
    		{
   ```

   The exposure and the bloom do the same in `RenderPostHDR`, with `m_LetterboxExposureSet` and `m_LetterboxBloomSet`. A reader that you forget would pass a null set for the new source, and its call would crash or draw nothing. Search the file for every call of `SelectPostSet`: there are four, and the motion blur's keeps the default. The depth of field reads only the HDR image or the history and picks its set without the function.

   **You should see:** three calls with the new argument.

   **If you do not see it:** a build error about the number of arguments means that you changed a declaration but not a call, or the other way round.

5. Keep the blur mark. The tone mapping does not sharpen the pixels that the depth of field or the motion blur blurred, and it learns them from the source. With the letterbox between, the source is the letterbox's, so the flag of step 1 tells the tone mapping what came before.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-25"
    		tonemap.FilmicShoulderPower = filmic.ShoulderPower;
    		const PostProcessMath::ColorGrading grading = GetColorGrading(postProcess);
    		// The depth of field's and the motion blur's outputs mark what they blurred in alpha.
   -		const bool blurMask = source == PostSource::DepthOfField || source == PostSource::MotionBlur;
   +		const bool blurMask = source == PostSource::DepthOfField || source == PostSource::MotionBlur
   +			|| (source == PostSource::Letterbox && m_LetterboxBlurMask);
    		tonemap.ColorFlags = (grading.Active ? RenderData::c_TonemapColorGrading : 0u) | (blurMask ? RenderData::c_TonemapBlurMask : 0u);
    		for (int row = 0; row < 3; row++)
    			tonemap.ColorRows[row] = glm::vec4(grading.Matrix[0][row], grading.Matrix[1][row], grading.Matrix[2][row], 0.0f);
   ```

   Without this change the sharpening would reach blurred pixels as soon as the bars are on. No test of the pass alone would notice.

   **You should see:** `blurMask` computed over two lines.

   **If you do not see it:** the line is in `RenderPostDisplay`, near the start of the tone mapping's constants.

6. Build the test program. The header changed, so many files compile.

   ```sh
   cmake --build build/<preset> --config Debug --target StrataTests --parallel
   ```

   The build takes a while. The project compiles with warnings as errors.

   **You should see:** the build ends with no error and no warning.

   **If you do not see it:** read the first error from the top. A message about an unused variable or a missing return points at the step that declared the name.

:::::

The exposure and the bloom read the new source, so they see the image with its bars. The bars are black pixels in the exposure's :term[histogram]{id=histogram}, and the bloom reads black there. The effect has a cost beyond its own pass, and a review can ask for it.

## Keep the effect off where tests need exact pixels

Rule 3 says that the neutral helper turns the effect off. The default is already off, but a test that depends on exact colors should not depend on a default.

:::::steps

1. Set the switch in `AddNeutralPostProcess`, next to the vignette.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-34"
    		postProcess.AutoExposureLightSpeed = postProcess.AutoExposureSpeed;
    		postProcess.AutoExposureKey = 0.0f;
    		postProcess.Vignette = 0.0f;
   +		postProcess.Letterbox = false;
    		postProcess.Bloom = false;
    		postProcess.AmbientOcclusion = false;
    		postProcess.AmbientOcclusionMultiBounce = false;
   ```

   The helper lists every post effect that would change a color: the tone curve, the vignette, the bloom, the occlusion and the anti-aliasing. It now lists the letterbox, so a later default of `true` cannot change the pixels of a test.

   **You should see:** one new line after `Vignette`.

   **If you do not see it:** the helper is in `StrataTests/src/Renderer/SceneRendererTestUtils.h`.

:::::

Rule 4 holds in two ways. When the switch is off, the number of rows is 0, `RenderLetterbox` never runs and no texture is made: the frame is the old frame. The same holds when the switch is on but the bars would have no rows.

When bars are drawn, every pixel between them is a copy of the source: `SanitizeHDR` changes only a bad value. Such a value is not a number or lies outside the range from 0 to the largest HDR value. The GPU test below checks both ways.

## Choose the GPU stage

Each GPU pass belongs to a stage, a named span of the frame whose time the :term[profiler]{id=profiler-instrumenting-vs-sampling} reports. A pass goes into the stage it belongs to, or into a stage of its own. The engine registers the stages in one list.

```cpp src="Strata/src/Strata/Renderer/GPUProfiler.cpp#L62-L66" from="stages.TAA" to="stages.Overlays" symbol="RendererGPUStages::Get"
stages.TAA = RegisterGPUStage("GPU.TAA");
stages.MotionBlur = RegisterGPUStage("GPU.MotionBlur");
stages.DepthOfField = RegisterGPUStage("GPU.DepthOfField");
stages.Post = RegisterGPUStage("GPU.Post");
stages.Overlays = RegisterGPUStage("GPU.Overlays");
```

Your pass runs after `gpuTimer.Next(gpuStages.Post)`, so its time counts in the Post stage, the stage of the exposure, the bloom and the tone mapping. That is the right place for a cheap pass that belongs to their chain. The depth of field and the motion blur have stages of their own, because each is a whole effect with several passes and a cost worth seeing apart.

A stage of its own adds a name to every profile and every performance log, and it appears in five lists. Exercise 3 asks you to add one.

## Test the pass on the GPU

The GPU test renders a wall of one gray code under the neutral post-processing and reads the pixels back. The first test case checks the bars and the picture between them exactly. The second checks rule 4.

:::::steps

1. Create the file `GPUSceneLetterboxTests.cpp` in `StrataTests/src/Renderer/`. The first part holds the includes, the wall and the helper that renders it and reads the pixels.

   ```cpp src="book:tutorials/image/tutorial-post-effect/GPUSceneLetterboxTests.cpp#L1-L40"
   #include "Renderer/SceneRendererTestUtils.h"
   #include "Strata/Renderer/PostProcessMath.h"
   #include "Strata/Renderer/RendererComponents.h"

   using namespace Strata;
   using namespace Strata::Tests;

   // The letterbox (PostProcess/Letterbox.comp): black bars that crop the image to a wider aspect, off by default.
   namespace
   {

   	constexpr uint32_t c_Width = 1024;
   	constexpr uint32_t c_Height = 576;
   	constexpr int c_Code = 128;

   	// A wall of one display code (unlit, the neutral post-processing shows it unchanged) filling the view.
   	struct GrayWall
   	{
   		Scene SceneData;
   		PostProcessComponent* PostProcess = nullptr;

   		explicit GrayWall(SceneTestAssets& assets)
   		{
   			PostProcess = &AddNeutralPostProcess(SceneData);
   			AddMesh(SceneData, BuiltinAssets::QuadMesh, assets.AddMaterial(Emitting(PostProcessMath::SRGBToLinear(static_cast<float>(c_Code) / 255.0f))),
   				glm::vec3(0.0f), "Wall")
   				.GetComponent<TransformComponent>().Scale = glm::vec3(40.0f, 40.0f, 1.0f);
   		}
   	};

   	ReadbackImage RenderWall(SceneRenderer& renderer, GrayWall& wall)
   	{
   		const SceneCamera camera = LookAt(glm::vec3(0.0f, 0.0f, 2.0f), glm::vec3(0.0f), static_cast<float>(c_Width) / static_cast<float>(c_Height));
   		REQUIRE(renderer.Render(wall.SceneData, camera));
   		ReadbackImage image;
   		REQUIRE(Renderer::ReadTexture(renderer.GetOutputTexture(), image));
   		return image;
   	}

   }
   ```

   1. **Line 24:** `AddNeutralPostProcess` makes the post-processing plain.
   2. **Line 25:** the wall shows one display code, 128, as a flat color, and fills the view.
   3. **Line 36:** `Renderer::ReadTexture` blocks until the pixels arrive. Only tests and tools may use it.

   **You should see:** a new file with no suite in it yet.

   **If you do not see it:** the file goes next to the other `GPUScene` tests.

2. Add the suite and its first test case.

   ```cpp src="book:tutorials/image/tutorial-post-effect/GPUSceneLetterboxTests.cpp#L42-L71"
   TEST_SUITE("GPU.SceneRenderer.Letterbox")
   {
   	TEST_CASE("The letterbox blacks the bars and leaves the picture between them as it was")
   	{
   		GPUContext gpu;
   		REQUIRE(gpu.IsValid());
   		SceneTestAssets assets;
   		GrayWall wall(assets);
   		SceneRenderer renderer(ExactSpecification());
   		renderer.SetViewportSize(c_Width, c_Height);
   		const ReadbackImage plain = RenderWall(renderer, wall);
   		CHECK(Red(plain, c_Width / 2, c_Height / 2) == c_Code);

   		// 1024 / 2 = 512 rows of picture, so 32 rows of bar above and below.
   		wall.PostProcess->Letterbox = true;
   		wall.PostProcess->LetterboxAspect = 2.0f;
   		const ReadbackImage barred = RenderWall(renderer, wall);
   		for (uint32_t x = 0; x < c_Width; x++)
   		{
   			for (uint32_t y = 0; y < c_Height; y++)
   			{
   				const bool inBar = y < 32 || y >= c_Height - 32;
   				if (inBar)
   					CHECK(GetPixelRGBA8(barred, x, y) == glm::u8vec4(0, 0, 0, 255));
   				else
   					CHECK(GetPixelRGBA8(barred, x, y) == GetPixelRGBA8(plain, x, y));
   			}
   		}
   		CHECK(gpu.GetNewErrorCount() == 0);
   	}
   ```

   1. **Line 46:** the shared device comes from `Tests::GPUContext`. A test never creates a device.
   2. **Line 50:** `ExactSpecification()` disables texture streaming and the :term[dither]{id=dither}, so the pixels are exact.
   3. **Lines 63–67:** the bars are 32 rows, as you calculated. Each pixel in them is exactly black, and each other pixel equals the same pixel of the frame without the effect.
   4. **Line 70:** the test ends by checking that the GPU reported no new error.

   **You should see:** a test case that renders two frames.

   **If you do not see it:** a failure at a pixel of a bar means that the pass did not run. Check `Letterbox` in the scene and the call in `RenderFrame`.

3. Add the second test case, for rule 4.

   ```cpp src="book:tutorials/image/tutorial-post-effect/GPUSceneLetterboxTests.cpp#L73-L94"
   	TEST_CASE("A view as wide as the aspect, or at the neutral value, renders bit for bit as without the effect")
   	{
   		GPUContext gpu;
   		REQUIRE(gpu.IsValid());
   		SceneTestAssets assets;
   		GrayWall wall(assets);
   		SceneRenderer renderer(ExactSpecification());
   		renderer.SetViewportSize(c_Width, c_Height);
   		const ReadbackImage plain = RenderWall(renderer, wall);

   		// The neutral value is off: AddNeutralPostProcess leaves the letterbox off, and the bars wait for it.
   		CHECK_FALSE(wall.PostProcess->Letterbox);
   		wall.PostProcess->LetterboxAspect = 2.0f;
   		CHECK(MaxDifference(RenderWall(renderer, wall), plain) == 0);

   		// On, with an aspect the view already has (a narrower one): no bars, no pass.
   		wall.PostProcess->Letterbox = true;
   		wall.PostProcess->LetterboxAspect = 1.0f;
   		CHECK(MaxDifference(RenderWall(renderer, wall), plain) == 0);
   		CHECK(gpu.GetNewErrorCount() == 0);
   	}
   }
   ```

   1. **Line 84:** the neutral value is off, and the test says it.
   2. **Line 86:** `MaxDifference` is the largest difference of any channel of any pixel, and it must be 0.
   3. **Line 90:** the switch is on, but an aspect of 1 is narrower than the view, so no bars exist and no pass runs.

   **You should see:** a second test case in the suite.

   **If you do not see it:** a difference above 0 means that a frame without bars changed. Check that the number of rows is 0 in that frame.

4. Run the configure step again, since a file is new, then build and run the suite.

   ```sh
   cmake --preset <preset>
   cmake --build build/<preset> --config Debug --target StrataTests --parallel
   build/<preset>/bin/Debug/StrataTests --test-suite=GPU.SceneRenderer.Letterbox
   ```

   The first command finds the new file, the second builds, and the third runs the one suite on your GPU.

   **You should see:** both test cases pass, and no validation error appears.

   **If you do not see it:** a failure of the first `REQUIRE` means that no usable GPU was found; [the first triangle](../gpu/first-triangle.md) shows how to check the device. Any other failure shows the pixel and the two values.

:::::

:::rule[A new test must fail without its change]
Run the test once with the pass disabled and watch it fail. Comment out the call in `RenderFrame`, rebuild and run the suite: the first test case must fail at the first pixel of a bar. Restore the call afterward. Strata's guide for its developers asks this of every test; the details: [testing an engine](../engineering/test-kinds.md).
:::

## Cover the effect in the feature test and see it

Strata's feature test fails when a property keeps its default value on every entity that has the component. A new property needs a value that is not the default in the feature scene, which also proves that it saves and loads.

:::::steps

1. Add both properties, with values that are not the defaults, to the Post Process of the feature scene.

   ```diff src="book:tutorials/image/tutorial-post-effect.patch#hunk-27"
    						"ColorLookup": "F7A0000000000011",
    						"ColorLookupIntensity": 0.5,
    						"LensFlare": 0.5,
   +						"Letterbox": true,
   +						"LetterboxAspect": 2.0,
    						"ColorOffset": [
    							0.0,
    							0.0,
   ```

   The switch is on, and the aspect is 2 and not 2.39. A game maker never edits a scene file by hand; here it is the engine's own test data.

   **You should see:** two new lines after `LensFlare`.

   **If you do not see it:** the file is `StrataTests/FeatureTest/Assets/Scenes/Feature.stscene`; search for `LensFlare`.

2. Build everything and run the whole set of tests, as the review checklist asks before a commit.

   ```sh
   cmake --build build/<preset> --config Debug --parallel
   ctest --preset <preset>-debug -j 8
   ```

   The first command builds the editor and the other programs as well. The second runs every test, eight at a time.

   **You should see:** the run ends with a summary that says all tests passed, and the feature test is among them.

   **If you do not see it:** the feature test names the property that it found unused. A warning or an error in the log of a test names the place; read it before anything else.

3. Look at the effect. Start the editor, open a scene that has a Post Process, and enable the letterbox.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Start the editor you built, select the entity that holds the Post Process component, and scroll the inspector down to its group `Lens`. Enable `Letterbox`, then change `Letterbox Aspect`, and watch the bars follow in the Scene view.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<id>", "component": "PostProcess", "values": { "Letterbox": true, "LetterboxAspect": 2.39 } } }
   ```

   The command sets both values in one undo step. Replace `<id>` with the id of the entity that holds the Post Process.
   :::
   ::::

   **You should see:** two black bars above and below the image of the viewport. While the switch is off, the aspect field is inactive and shows its reason.

   **If you do not see it:** an editor built before your change has no property: build the editor again. A viewport that is already wider than the aspect shows no bars: lower the aspect.

:::::

The drawing shows where your rows appear: the Lens group of the editor before your change has four rows, and your switch and aspect field join it below **Lens Flare**.

::figure{id=lens-group}

The tutorial ends here. A game maker meets your effect as a property in the inspector, and a command or a scene file sets it. The review checklist of the engine asks one last time for a clean diff: tests, style, and the documents that describe behavior.

## Summary

- A new post effect takes its parameters by push constants, or by a buffer of its own, never by new frame constant fields, so the scene passes keep a stable layout.
- The new pass follows the post source: it reads the set of the current source, writes its own texture, becomes the next source, and every reader after it gets a set for it.
- The effect is off in the neutral helper, and at its neutral value it never runs, so the image is bit for bit the same.
- When the pass cannot make its resources it reports, returns failure, and `RenderFrame` sets `degraded`; the frame continues with the old source and no bars.
- A GPU test with the shared context, `ExactSpecification` and the error count checks the bars and the picture between them pixel by pixel.

## Check yourself

1. Why does the letterbox take `BarRows` by push constants and not as a new field of `FrameConstants`?

   :::answer{tests="push-constants"}
   The frame constants are one block that the scene passes share, and a new field moves a layout that all of them depend on. A post pass keeps its data in its own struct, here 16 bytes, which the shader and the host agree on and the `static_assert` lines check. Push constants hold up to 128 bytes; a pass that needs more, as the tone mapping, uses a buffer of its own.
   :::

2. The motion blur runs, and then the letterbox. Which texture does the letterbox read, and which set does the tone mapping take afterward?

   :::answer{tests="post-source"}
   The letterbox reads the output of the motion blur, through its set number 4. It writes `m_LetterboxTexture`, and `RenderFrame` sets the post source to `Letterbox`. The tone mapping then calls `SelectPostSet` with that source and takes `m_LetterboxTonemapSet`, which binds the letterbox's texture. The history is untouched.
   :::

3. A scene has `Letterbox` on and an aspect of 1.5, and the viewport is 1280 by 720. What does the frame show, and does the pass run?

   :::answer{tests="neutral-value"}
   The picture would be 1280 / 1.5 = 853 rows high, which is more than the 720 rows of the view, so the spare space is negative and `GetLetterboxBarRows` returns 0. No bars exist, `RenderLetterbox` never runs, and the frame equals the frame with the effect off, bit for bit.
   :::

4. The target of the letterbox cannot be created, because the GPU has no memory left. What does the viewer see, and what does the renderer do with the error?

   :::answer{tests="failure-path"}
   `CreateLetterboxTarget` reports the error and returns `false`, so `RenderLetterbox` returns `false`, and `RenderFrame` keeps the old post source and sets `degraded`. The viewer sees the frame without bars, complete otherwise. The error stays while frames fail and clears on the first frame without a failure.
   :::

5. Why does the first GPU test render with `ExactSpecification()` and not with the default specification?

   :::answer{tests="exact-test"}
   The default streams textures and dithers the output, so pixels can differ by a code from the exact values. `ExactSpecification()` turns both off, so a bar pixel must be exactly 0 and every other pixel exactly as without the effect. The test also checks `GetNewErrorCount()` at its end.
   :::

## Exercises

1. **Basic.** Predict the bar rows for 1280 by 720 at an aspect of 2.39, and for 2560 by 1080 at the same aspect. Add both as checks to the math test and run the suite.

   Hint: use the formula of the second section, and round down.

   :::answer{tests="neutral-value"}
   For 1280 by 720: 1280 / 2.39 = 535.6, the spare rows are 184.4, half is 92.2, so 92 rows. For 2560 by 1080: 2560 / 2.39 = 1071.1, the spare rows are 8.9, half is 4.4, so 4 rows. The checks are `CHECK(PostProcessMath::GetLetterboxBarRows(1280, 720, 2.39f) == 92);` and the same with `(2560, 1080, 2.39f) == 4`. The suite passes with two more checks.
   :::

2. **Medium.** Give the bars a color that the component sets: a `LetterboxColor` property with a range of 0 to 1 for each channel, black by default. Give it a push constant and a value in the feature scene. Extend the GPU test: a red bar must read exactly red.

   Hint: the scene color carries the pre-exposure, so multiply the color by `m_PreExposure` before it goes into the push constants. The reason of the aspect applies to the color too.

   :::answer[Worked solution]{tests="push-constants exact-test" solution="tutorials/image/tutorial-post-effect/exercise-1.patch"}
   The component gains a `glm::vec3`, registered with the range and the reason of `WithLetterbox`. The push constants grow by a `glm::vec4` at offset 16, so their size is 32 and the `static_assert` lines change. The shader writes that color in a bar.

   `RenderLetterbox` clamps each channel to 0 to 1 and multiplies by `m_PreExposure`, because the exposure and the tone mapping later undo the pre-exposure. The new test case reads a pixel of a bar and expects 255, 0, 0, 255. At the default of black, the bars are as before, and the neutral value still renders bit for bit.
   :::

3. **Hard.** Give the letterbox a :term[GPU stage]{id=gpu-stage-strata} of its own and read its time in the `gpuMs` of `viewport.capture`. Then say when a stage of its own is worth its line in every profile.

   Hint: register the stage in frame order, and search the guide for the five lists that name the stages.

   :::answer{tests="post-source"}
   Add a field to `RendererGPUStages` in `GPUProfiler.h`, register it in `GPUProfiler.cpp` before the Post stage, and call `gpuTimer.Next` for it before the pass in `RenderFrame`, then `Next(gpuStages.Post)` after the pass. Add the name at the same position to the five lists: the description of `editor.perf`, `EditorProfilerTests.cpp`, `FramePerfLogTests.cpp`, the stage table of `Docs/Architecture.md` and the automation skill. `viewport.capture` then reports the stage in `gpuMs`, on a machine whose GPU writes timestamps. A stage of its own is worth its line when the pass is costly, when you tune it, or when it is a whole effect like the depth of field. A cheap pass that belongs to a chain stays in the stage of the chain.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Renderer/SceneRendererPost.cpp`: the post passes, `SelectPostSet`, the depth of field and the motion blur, which your pass follows.
- `Strata/src/Strata/Renderer/SceneRenderer.cpp`: `RenderFrame`, where the post source changes.
- `Strata/src/Strata/Renderer/PostProcessData.h`: the GPU data of every post pass, with its `static_assert` lines.
- `Strata/src/Strata/Renderer/RendererComponents.cpp`: the registration of the Post Process properties and their inactive reasons.
- `Strata/src/Strata/Renderer/GPUProfiler.cpp`: the GPU stages.
- `StrataTests/src/Renderer/SceneRendererTestUtils.h`: `AddNeutralPostProcess`, `ExactSpecification` and the other test helpers.

## Further reading

- [NVRHI](https://github.com/NVIDIA-RTX/NVRHI): the graphics layer that Strata renders through; its repository documents binding sets, layouts and push constants. Intermediate.
- [The Vulkan specification](https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html): the chapter on push constants gives the 128 byte guarantee behind the limit. Advanced.
- [doctest](https://github.com/doctest/doctest): the test framework of Strata's tests, with its filters and `CHECK` macros. Beginner.
