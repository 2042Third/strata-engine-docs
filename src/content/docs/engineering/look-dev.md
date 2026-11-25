---
id: engineering/look-dev
title: "The look-dev harness"
description: "How Strata takes fixed pictures of its samples and a look-dev scene, compares two builds with signed differences, and tells a real change from noise."
kind: internals
size: M
tracks: [E]
needs: [engineering/test-kinds, gpu/frame-tour]
time: 50
learn:
  - id: why-signed
    text: explain why a before-and-after comparison with a signed image finds changes that a golden image or a single number misses
  - id: difference-numbers
    text: compute the differing pixels, the largest and the mean difference of two small images by hand
  - id: capture-compare
    text: run a capture twice, compare it with a changed build and tell a real change from noise
  - id: trace-shot
    text: trace one shot from its entry in the shots file to the editor command that takes the picture
since: 0.7.0
status: final
---

You change a :term[shader]{id=shader}, and the unit tests pass. Did the grass look worse? Did the shadow under the robot move? A test cannot say, because nobody wrote down what the picture should be.

The **look-dev harness** is a Python tool, `Tools/LookDev.py`, that takes fixed pictures of the samples, of a new project and of a look-dev scene through headless editors, and compares two sets of them. It does not decide whether a change is good: it shows what changed, and a person looks.

**Look-dev** is the work of judging how a scene looks and changing the :term[renderer]{id=renderer} or the content until the look is right. The harness is how Strata judges a rendering change, and many pictures of this book come from its shots.

## The problem and how engines solve it

A change to the shadow filter should leave most of the screen alone. You must learn where the picture moved, by how much, and whether the change cost time. Engines meet this with two habits.

The first is the **golden image**: a picture saved when the result looked right, which every later run must match, within some tolerance. Two :term[graphics processing units]{id=gpu} (GPUs), or two driver versions, round differently, so a golden image written on one machine fails on another with no change in the code. A tolerance wide enough to forgive that also forgives a real change that is small.

The second is the before-and-after comparison, and it is the one Strata uses. You render the same shots with the old build and the new build on the same machine, and compare the two sets. The machine's habits cancel out, because both sets have them.

A comparison that gives one number is not enough. A change can lower the mean error and still wreck the picture, because one small region got much worse. The opposite also happens: a mean of zero hides a region that got brighter and another that got darker by the same amount. A person must look at the signed image, which shows where the difference lies and which way it points.

Three more habits make the comparison worth trusting: repeats that prove the render is steady, crops of the regions that matter, and GPU times beside the pictures. The suites of [the test kinds](../engineering/test-kinds.md) cannot replace it: they check numbers and states, not looks.

:::example
A 1,920 by 1,080 picture holds 2,073,600 pixels, and a shader change makes 1,800 of them differ, each by at most 3 steps on a scale of 255. The mean difference over all pixels is below 0.01, a number that looks like nothing. Yet the 1,800 pixels may all lie along one shadow edge, and the signed image shows them as a thin blue line: the shadow grew a little. The number says the change is tiny; the image says where it is and which way it went.
:::

## The map

The harness has two halves. **Capture** makes a folder of pictures and numbers for one build. **Compare** reads two such folders and reports what differs. A third command, `ratio`, divides the time of one GPU stage by another in the same frames, and `selftest` checks the tool itself.

```mermaid caption="Capture turns one build into a folder of pictures, crops, statistics and GPU times. Compare reads two folders and writes difference images, side-by-side crops and GPU time ratios." alt="Two boxes feed a third. Capture of the before build and capture of the after build each make a folder. Compare reads both folders and writes difference images, signed images, crops and a ratio table."
flowchart LR
  B1[build before] --> C1[capture]
  B2[build after] --> C2[capture]
  C1 --> F1[folder: shots crops stats stages.csv index.html]
  C2 --> F2[folder: shots crops stats stages.csv index.html]
  F1 --> CMP[compare]
  F2 --> CMP
  CMP --> R[diff signed crops compare.json index.html]
```

Capture takes these steps for one build.

1. Capture copies the four 3D samples (`ThirdPerson`, `PhysicsPlayground`, `OpenWorld`, `Showcase`) into a work folder and never opens them in place, so a capture cannot change a sample.
2. Capture makes two more projects: `Basic3D` from the `basic3d` template, and `LookDev` from the :term[command script]{id=command-script} `Tools/LookDev/LookDevScene.json`. [The command scripts page](../editor/command-scripts.md) shows how such a script runs in a headless editor.
3. Capture starts one headless editor per project with `StrataCLI launch`, all in one private session folder of the run.
4. For every shot of `Tools/LookDev/Shots.json`, at every size, anti-aliasing mode and repeat, it asks the editor for a picture. The defaults are 3840 by 2160 and 1920 by 1080 pixels, the modes temporal anti-aliasing (TAA), fast approximate anti-aliasing (FXAA) and off, and five repeats.
5. After the editors quit, it reads the pictures back in worker processes on all cores but one, cuts the crops, and writes the statistics and the page.

The look-dev project's script makes white spheres for the white furnace test: under even white light, a white surface must look exactly as bright as the light. It also makes a room with a lit window, a dark floor under screen-space reflections, poles, a fence, a thin plate, a leaf card and the physical sky. Other scenes are lit by flat panels made into area lights. Each look property keeps the default of its component, so a build shows what new content gets.

The output folder holds:

- `shots/`: one picture per shot, size and mode, the first repeat.
- `crops/`: each shot's regions of interest, enlarged 4 times.
- `stats/`: the `renderStats` of every repeat, with GPU times, and the number of pixels in which each repeat differs from the first.
- `stages.csv`: per picture, the median GPU busy time and the time of each stage, with triangles, draws and shadow draws.
- `index.html` and `run.json`: a static page of everything, and the build's version line, the editor's GPU and the outcome of every shot.

The harness refuses an output folder inside the :term[repository's]{id=repository} tracked files; build trees and `.worktrees` are fine. Its :term[exit code]{id=exit-code} is 1 when a shot failed.

For every picture the two sets share, compare counts the differing pixels and finds the largest and the mean channel difference. It writes a difference image to `diff/`, a signed image to `signed/` and the crops side by side. It also divides the two builds' GPU times, stage by stage. [The frame tour](../gpu/frame-tour.md) names the stages. Its page, `index.html`, shows these:

::figure{id=compare-layout}

## The contract

These rules keep the pictures of different builds comparable.

1. **Shots are appended and never changed.** The shots file says so in its own comment. Change a shot's camera or crops, and the capture of every earlier build no longer matches it: the old sets no longer compare. A new view is a new shot.
2. **The repeats of one build should differ by zero pixels.** Each repeat is compared with the first, and the result lands in `stats/`. A number above zero means the render is not steady (a streaming texture, a late asset, a driver that varies). At the pin some shots vary: two captures of a polished metal shot without anti-aliasing differ in 3,077 pixels. A difference between builds counts only beyond the shot's own repeats.
3. **The harness uses only Python's standard library.** It reads and writes its own PNG files with `zlib` and `struct`. Nothing to install means it runs on a fresh machine, in a continuous integration (CI) job and in every :term[worktree]{id=worktree}.
4. **A timing needs a quiet machine.** Pictures are exact on any machine, but trust GPU times only from runs that were alone on it. A busy machine moves a time by more than most changes do. For that reason `ratio` divides one stage by another stage of the same frames: a ratio holds when other programs run beside it, an absolute time does not.

:::why
Strata compares two builds on one machine instead of keeping golden images, because a golden image is a claim about a machine. The cost is two captures for every change, one of a build from before it. Strata pays it, because a test that fails on every new driver gets switched off.
:::

## A toy version

The core of compare is small. Think of two images as rows of grey values from 0 to 255. For every pixel, subtract. Count the pixels that differ, remember the largest difference and add up all differences to get a mean.

:::question
New to C++? The toy uses loops and functions ([programming 2](../basics/programming-2.md)) and calls such as `std::abs(` ([programming 3](../basics/programming-3.md)).
:::

The toy compares a row of eight pixels, all at 100, with two copies: one has four pixels at 106, the other four at 94. Watch what the absolute difference says about each, and what the signed list says.

```cpp sketch="engineering-look-dev-toy.cpp"
// A toy comparison of two one-row grey images: the absolute difference and the signed one.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <vector>

struct Difference
{
	int Differing = 0;
	int Largest = 0;
	float Mean = 0.0f;
};

Difference Absolute(const std::vector<int>& before, const std::vector<int>& after)
{
	Difference result;
	int total = 0;
	for (size_t index = 0; index < before.size(); index++)
	{
		int delta = std::abs(after[index] - before[index]);
		if (delta == 0)
			continue;
		result.Differing++;
		result.Largest = std::max(result.Largest, delta);
		total += delta;
	}
	result.Mean = static_cast<float>(total) / static_cast<float>(before.size());
	return result;
}

void Report(const char* name, const std::vector<int>& before, const std::vector<int>& after)
{
	Difference difference = Absolute(before, after);
	std::printf("%s: %d differ, largest %d, mean %.2f, signed:", name, difference.Differing, difference.Largest, difference.Mean);
	for (size_t index = 0; index < before.size(); index++)
		std::printf(" %d", after[index] - before[index]);
	std::printf("\n");
}

int main()
{
	std::vector<int> before = { 100, 100, 100, 100, 100, 100, 100, 100 };
	std::vector<int> brighter = { 100, 100, 106, 106, 106, 106, 100, 100 };
	std::vector<int> darker = { 100, 100, 94, 94, 94, 94, 100, 100 };
	Report("brighter", before, brighter);
	Report("darker", before, darker);
	return 0;
}
```

```text output-of="engineering-look-dev-toy.cpp"
brighter: 4 differ, largest 6, mean 3.00, signed: 0 0 6 6 6 6 0 0
darker: 4 differ, largest 6, mean 3.00, signed: 0 0 -6 -6 -6 -6 0 0
```

1. **Line 20:** the absolute difference of one pixel, always zero or more.
2. **Line 27:** the mean: the sum of all differences over the number of pixels.
3. **Line 36:** the signed value keeps the sign that the absolute one drops.

The absolute numbers are the same for both cases: 4 pixels differ, the largest difference is 6, and the mean is 24 over 8 pixels, which is 3. The signed list is not the same: plus 6 on four pixels in one case, minus 6 in the other. The signed difference tells them apart, and the real harness draws that sign as a color.

## The real code

The real harness compares colour pictures read from PNG files, in worker processes. The sections follow the data: the shots file, the capture of one shot, the two differences and the compare.

### The shots file

The shots file lists the projects and the shots. Look at the comment on line 4, at a project that loads a world, and at the first shot with its crops.

```json src="Tools/LookDev/Shots.json#L1-L14"
{
	"Format": "StrataLookDevShots",
	"Version": 1,
	"_comment": "The look-dev harness's projects and shots (Tools/LookDev.py; Docs/DeveloperGuide.md, \"Look-dev harness\"). Append shots and projects; never change an existing shot's camera or crops, so that captures of every build keep comparing. Crops are normalized [x0, y0, x1, y1] of the picture.",
	"Projects": {
		"ThirdPerson": {"Sample": "ThirdPerson", "Scene": "Scenes/Course.stscene"},
		"PhysicsPlayground": {"Sample": "PhysicsPlayground", "Scene": "Scenes/Main.stscene"},
		"OpenWorld": {"Sample": "OpenWorld", "Scene": "Worlds/Island.stscene", "LoadWorld": true},
		"Basic3D": {"Name": "Basic3D", "Template": "basic3d", "Scene": "Scenes/Main.stscene"},
		"LookDev": {"Name": "LookDev", "Script": "LookDevScene.json", "Scene": "Scenes/LookDev.stscene"},
		"Showcase": {"Sample": "Showcase", "Scene": "Scenes/Outpost.stscene"}
	},
	"Shots": [
		{"Name": "tp.scene", "Project": "ThirdPerson", "Camera": "scene", "Crops": [{"Name": "robot-shadow", "Rect": [0.28, 0.6, 0.4, 0.74]}, {"Name": "feet", "Rect": [0.44, 0.64, 0.555, 0.755]}, {"Name": "far-coins", "Rect": [0.43, 0.12, 0.57, 0.27]}, {"Name": "sign-shadow", "Rect": [0.62, 0.52, 0.86, 0.7]}]},
```

1. **Line 4:** the rule in the file's own comment: append, never change a shot's camera or crops.
2. **Line 8:** a project that loads its whole world and keeps every cell loaded, so a shot shows the same content however fast cells stream.
3. **Line 10:** a project built by a script, not copied from a sample.
4. **Line 14:** a shot with four named crops, rectangles in fractions of the picture.

A project is a sample, or a project made from a template, or one built by a script. A shot names its project and gives a camera: the scene's camera (`scene`), the editor's opening view (`editor`), or a position, a target and a :term[field of view]{id=field-of-view}. Its crops are rectangles in fractions of the picture, from 0 to 1, so they work at every size. A shot may also carry:

- `Setup`: editor commands run on the scene before the capture, such as a change to the sun's rotation.
- `AntiAliasing`: the modes this shot is taken in, instead of all three.
- `DebugView`: the debug view the picture shows. [The debugging page](../gpu/debugging.md) says what each view shows.
- `Scene`: another scene of the project.
- `Metrics`: rectangles for which the harness computes a noise or banding number on the first repeat.
- `Live`: a played shot, described below.

### Capture, one repeat at a time

Python reads differently from C++ in three ways that matter here. Leading spaces mark a block, not braces. A variable has no written type. A string that starts with `f` writes the values of expressions in braces into the text, so `f"{name}.png"` is the name and `.png`.

The function `capture_still` takes the picture of one shot at one size and mode, as often as the repeat count says. Look at where the first repeat goes, and what the call to the editor receives.

```python src="Tools/LookDev.py#L750-L768"
def capture_still(editor, shot, size, mode, repeat, quality, output, work, debug_view="none"):
    """Every repeat of a shot at a size and mode: their results (without the image), the first saved in shots/."""
    results = []
    name = shot_file_name(shot, size, mode)
    for index in range(repeat):
        path = output / "shots" / f"{name}.png" if index == 0 else Path(work) / "repeats" / f"{name}-{index}.png"
        params = dict(camera_parameters(shot))
        params.update({"width": size[0], "height": size[1], "overlays": False, "path": str(path), "overwrite": True})
        if "DebugView" in shot:
            params["debugView"] = shot["DebugView"]
        if quality != "project":
            params["quality"] = quality
        if debug_view != "none":
            params["debugView"] = debug_view
        result = editor.call("viewport.capture", params)
        result.pop("Image", None)
        result["file"] = str(path)
        results.append(result)
    return results
```

1. **Line 755:** the first repeat goes to `shots/`, the later ones to a work folder.
2. **Line 757:** the size, no :term[overlays]{id=overlay-core}, the path and permission to replace the file.
3. **Line 764:** the whole job: one call of the editor's command.
4. **Line 765:** the picture is already in the file, so the result drops it.

The harness never renders anything: it asks a running editor, through the command `viewport.capture`, and the editor answers with the picture and its `renderStats`. [The camera page](../editor/camera-viewport.md) describes the command and the editor's cameras.

The editor renders again while assets load, while temporal anti-aliasing fills its history and while global illumination settles, but every wait has a bound in frames. When a bound runs out, the command answers anyway, with `complete` false and `incomplete` listing the fields that say what the picture lacks, such as `/pendingAssets`. Check `stats/` before you trust a difference.

Its `renderer` parameter switches techniques for one picture: specular anti-aliasing, energy compensation, occlusion culling, texture streaming, the bounces of global illumination and others. Such a capture draws through a renderer of its own and changes no view. A pair from one build, with a switch and without, shows what one technique does; the harness compares builds and sends no switches.

A shot of a different kind, a live shot, plays the scene and reads back what the :term[Game view]{id=game-view} presented. Its entry has a :term[fixed step]{id=fixed-step} to start at, a number of frames, and :term[simulated input]{id=simulated-input} events. Live shots judge motion and run only with `--live` or `--live-only`, in windowed editors.

### Two differences

The absolute difference, `difference`, matches the toy: per pixel, the absolute value of the channel differences, counted and drawn as an image eight times as bright. The signed one is the new idea: a **signed difference image** shows each pixel's change with its sign, red where the after picture is brighter and blue where it is darker. Read the text under its first line and the two lines that write red and blue.

```python src="Tools/LookDev.py#L340-L359"
def signed_difference(before, after, gain):
    """The signed difference of two images as an RGB image: per pixel v, the mean over the first three channels of
    (after - before), shows as red min(255, round(v * gain)) where the after picture is brighter and as blue
    min(255, round(-v * gain)) where it is darker. A slip in a shader darkens or brightens a region coherently, which
    the absolute difference cannot show."""
    if (before.width, before.height) != (after.width, after.height):
        raise ToolError(f"sizes differ: {before.width}x{before.height} and {after.width}x{after.height}")
    channels = min(before.channels, after.channels, 3)
    out = Image(before.width, before.height, 3)
    for index in range(before.width * before.height):
        a = before.data[index * before.channels:index * before.channels + channels]
        b = after.data[index * after.channels:index * after.channels + channels]
        if a == b:
            continue
        v = sum(b[channel] - a[channel] for channel in range(channels)) / channels
        if v > 0:
            out.data[index * 3] = min(255, round(v * gain))
        elif v < 0:
            out.data[index * 3 + 2] = min(255, round(-v * gain))
    return out
```

1. **Line 352:** identical pixels are skipped and stay black.
2. **Line 354:** the signed value, the mean of the channels' change.
3. **Line 356:** brighter becomes red, scaled by the gain and capped at 255.
4. **Line 358:** darker becomes blue in the same way.

For each pixel, the code averages the three channels' value of after minus before. A positive average is drawn as red, a negative one as blue, and the strength is the size of the average times a gain, 32 by default, capped at 255. A change of 6 steps is then 192 of 255: visible, where the plain difference of 6 would be nearly black.

A shadow edge that moved one pixel to the right makes a thin line of pixels brighter and a neighbor line darker. The absolute difference shows two thin lines, the same as a noisy edge would give. The signed image shows red beside blue, which is the mark of movement. A wide red region means a light got stronger, and a wide blue one means a surface got darker. A scattered mix of both at one or two steps is rounding.

### Compare and ratio

`compare` works in worker processes. For each anti-aliasing mode it prints one line: how many pictures differ, the median number of differing pixels, and the largest difference. It reports differences without failing. Its exit code is 1 only when one set has a picture the other lacks, because a missing picture means the two captures are not of the same shots.

`ratio` is a smaller command on one capture. Given two stage names, it divides the first by the second for every repeat of every picture, and writes the median, the smallest and the largest to `ratio.csv`.

### The shots by area

The shots file has grown with the renderer. The table lists the groups, as the rendering parts of the book use them. The names come from `Tools/LookDev/Shots.json` at the pin.

| Area | Shots | What they judge |
| --- | --- | --- |
| Samples | `tp.scene`, `pp.scene`, `ow.scene`, `basic3d.scene`, `showcase.scene`, and the `.editor` forms of all but the showcase | The scene's own camera and the editor's opening view. |
| Close views | `tp.feet`, `tp.sign`, `tp.lantern`, `ow.water`, `showcase.shot1` to `showcase.shot6` | Close-ups of details that audits chose, and the showcase's six views. |
| Direct light | `lookdev.furnace`, `lookdev.contact`, `lookdev.thin`, `lookdev.room`, `lookdev.sky`, `ow.lowsun` | White furnace spheres, a plate's contact shadow, thin poles and a fence, a room, the sky, a low sun. |
| Reflections | `lookdev.mirror`, `lookdev.sheet`, `lookdev.wet`, `lookdev.tank`, `lookdev.ior`, `lookdev.night`, `lookdev.overcast` | Reflections on metal, wet ground and spheres of different indices of refraction. |
| Lantern highlights | `lookdev.lantern.wet`, `lookdev.lantern.sheet` and their `.sized` forms | Glints of the two lanterns on a wet plane and a sheet, with the bulb's size. |
| Area lights | `lookdev.cornell.rect`, `lookdev.cornell.rect.top`, `lookdev.rect.wet`, `lookdev.rect.wet.low`, `lookdev.rect.metal`, `lookdev.rect.strip` | A Cornell box under its ceiling panel, a streak on wet ground, panels over metals, a strip light. |
| Probes | `lookdev.patch`, `lookdev.polished` | What the reflection probe adds, and its resolution on a polished panel. |
| Lighting views | `lookdev.view.lighting`, `.ao`, `.indirect`, `.luminance`, `.albedo`, and the same views of other samples | One debug view of a scene, to see one term of the light. |
| Global illumination | `lookdev.cornell`, `lookdev.yard*`, `lookdev.grass*`, `lookdev.room.view.*`, `lookdev.sunroom*`, `lookdev.sealedroom.view.gi` | The indirect light in a Cornell box, a yard, grass, a room, a sun room and a sealed room. |
| Motion | `tp.live.*`, `ow.live.tour`, `showcase.live.*` | Played shots with simulated input: motion blur and shimmer. |

Names with a `.view.` part take a debug view.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Golden images with a tolerance | Test suites that run on one fixed machine | A pass or fail answer in each CI run, with no second build | A failure on every new driver, or a tolerance that hides small real changes |
| Perceptual metrics, which weigh differences by how visible they are | Research and some image tools | One score per picture that follows what an eye notices | A score that hides where the change lies, and a model to trust and maintain |
| A person comparing screenshots by eye | Small teams, early in a project | No tool to write or keep | Slow, tiring work, and small changes that go unseen |

## How it is tested

The harness has two tests, and both run its `selftest` command. `StrataTools.LookDevOffline` runs without a GPU or an editor: it sends a PNG through the reader and writer, and checks the signed difference, the summary for each mode and the metrics on two made-up images. A 4 by 4 ordered pattern and a ramp with one step give numbers that can be worked out by hand. CI runs it on every job that excludes the `gpu` and `perf` labels, which is every build but :term[Dist]{id=dist}.

`StrataTools.LookDev` has the labels `gpu` and `tools`. It builds the look-dev project from its command script with the build's editor and takes one shot at 320 by 180 pixels with FXAA, twice. Then it checks every output: sizes, crops, statistics with no pending asset, no difference between the two repeats, the page, and a compare of the set with itself. Both tests need Python 3.10 or later, found when :term[CMake]{id=cmake} configures; without it, they fail and say so. The test list is homed with the other tools tests on [the page on generated code](../engineering/generated-code.md).

## Changing it safely

- Append a shot or a project; never edit one.
- After changing `LookDevScene.json`, run the next capture with `--fresh-work`. A kept work folder keeps its stale projects.
- The GPU tests of global illumination (`StrataTests/src/Renderer/GIScenes.cpp`) rebuild the rooms of `LookDevScene.json` in C++. When you change one, change the other.
- The noise and pattern metrics have a C++ twin in `StrataTests/src/Renderer/ReflectionMetrics.h`. Change both.
- Run `selftest` without `--build` before you commit, and the GPU test when the capture path changed.

## Summary

- A golden image fails across machines, so Strata compares two builds on one machine; a mean alone hides where a change lies, and the signed difference image shows its direction.
- The differing pixels, the largest and the mean difference come from per-pixel subtraction, and the signed value keeps the sign.
- Repeats must differ by zero pixels, shots are only appended, and GPU times count only from quiet runs; a real change is a coherent signed region.
- A shot is traced by a search: its entry in the shots file, `capture_still`, `viewport.capture`, and the command in the editor.

## Check yourself

1. A change gives 1,000 differing pixels out of two million, a largest difference of 2 and a mean of 0.001. Is the change harmless?

   :::answer{tests="why-signed"}
   Not known. The numbers do not say where the change is or which way it goes: the 1,000 pixels could be a shadow edge that grew. Look at the signed image. A coherent red or blue region that follows geometry is a real change; a scatter of both is rounding.
   :::

2. Two images of four pixels hold 10, 20, 30, 40 before and 10, 25, 30, 32 after. What are the differing pixels, the largest difference and the mean difference?

   :::answer{tests="difference-numbers"}
   Two pixels differ: the second by 5 and the fourth by 8. The largest is 8. The mean is the sum, 13, over 4 pixels, which is 3.25. The signed values are plus 5 and minus 8: one pixel brighter, one darker.
   :::

3. The repeats of one build differ by 12 pixels. Which is right: the compare against another build is fine, since 12 is small; or the render is not steady, and the compare would find noise?

   :::answer{tests="capture-compare"}
   The second. The harness expects zero. Pixels that differ between repeats of one build mean something varies, such as a texture still streaming, and a few pixels between builds could be the same variation.
   :::

4. You want a new camera position that shows an existing shot's detail better. What do you do, and why not edit the old shot?

   :::answer{tests="capture-compare"}
   Append a new shot with a new name and the new camera. Editing the old shot changes its pictures, so a capture of an older build no longer matches it.
   :::

5. A picture has the wrong size. Which function puts the size into the parameters, and which command receives them?

   :::answer{tests="trace-shot"}
   The function `capture_still` in `Tools/LookDev.py` sets `width` and `height` from the size, and sends them to the command `viewport.capture`, which the editor registers in `EditorViewportCommands.cpp`.
   :::

## Exercises

1. **Basic.** Capture one shot twice and compare the two sets. What do you expect, and which command shows it?

   :::answer[Worked solution]{tests="capture-compare"}
   Run `capture` twice with the same build and different labels, for example with `--shots "lookdev.contact" --sizes 1920x1080 --aa taa`, then `compare <first> <second> --output <folder>`. A steady render gives zero differing pixels in every picture, and the printed line says that none differ. A count above zero means the render varies; learn why before you compare builds.

   ```sh
   python -I Tools/LookDev.py capture --build build/windows/bin/Release --label a --shots "lookdev.contact" --sizes 1920x1080 --aa taa
   python -I Tools/LookDev.py capture --build build/windows/bin/Release --label b --shots "lookdev.contact" --sizes 1920x1080 --aa taa
   python -I Tools/LookDev.py compare <folder a> <folder b> --output <folder>
   ```

   Each capture prints the folder it wrote; give those folders to compare.
   :::

2. **Medium.** Write the signed difference of single grey values, with a gain of 32 and a cap of 255, and print the red and blue values for changes of 6, minus 6, 10 and 0.

   :::answer[Worked solution]{tests="difference-numbers" solution="sketches/engineering-look-dev-signed.cpp"}
   A positive change goes to red and a negative one to blue, each times the gain and capped at 255. Six times 32 is 192, and 10 times 32 is 320, which the cap brings to 255. A zero change is black. The program prints these values.

   ```cpp sketch="engineering-look-dev-signed.cpp"
   // The signed difference image of single grey values: red where brighter, blue where darker.
   #include <algorithm>
   #include <cstdio>

   int main()
   {
   	const float gain = 32.0f;
   	const int deltas[] = { 6, -6, 10, 0 };
   	for (int delta : deltas)
   	{
   		int red = delta > 0 ? std::min(255, static_cast<int>(delta * gain + 0.5f)) : 0;
   		int blue = delta < 0 ? std::min(255, static_cast<int>(-delta * gain + 0.5f)) : 0;
   		std::printf("delta %d: red %d, blue %d\n", delta, red, blue);
   	}
   	return 0;
   }
   ```

   ```text output-of="engineering-look-dev-signed.cpp"
   delta 6: red 192, blue 0
   delta -6: red 0, blue 192
   delta 10: red 255, blue 0
   delta 0: red 0, blue 0
   ```

   1. **Line 11:** a positive change goes to red, scaled by the gain and capped at 255.
   2. **Line 12:** a negative change goes to blue in the same way.
   :::

3. **Hard.** Trace it yourself: for the shot `lookdev.contact`, follow the call from its entry in the shots file to the editor's command that answers. Use a search, not a debugger.

   :::answer[Worked solution]{tests="trace-shot"}
   Search `Tools/LookDev/Shots.json` for the name: the entry holds the camera and the crops. Search `Tools/LookDev.py` for `viewport.capture`: `capture_still` builds the parameters (size, path, `overwrite`, and a debug view or quality when given) and sends them to the editor. Search `StrataEditor/src/Editor/EditorViewportCommands.cpp` for the same name: the editor registers the command there, and its handler renders the scene and returns the picture.
   :::

## Where it lives in Strata

- `Tools/LookDev.py`: the tool, with `capture`, `compare`, `ratio` and `selftest`; `capture_still`, `signed_difference`, `compare_command`.
- `Tools/LookDev/Shots.json` and `Tools/LookDev/LookDevScene.json`: the shots and the look-dev project's script.
- `StrataEditor/src/Editor/EditorViewportCommands.cpp`: the `viewport.capture` command.
- `StrataTests/CMakeLists.txt`: `StrataTools.LookDevOffline` and `StrataTools.LookDev`.
- `Docs/DeveloperGuide.md`: the section on the look-dev harness.

## Further reading

- The Python documentation on `zlib` and `struct`, the modules the harness reads PNG files with (intermediate).
- The PNG specification, on chunks and row filters, for the reader in `read_png` (advanced).
- Papers and talks on image regression testing and perceptual difference metrics, for the alternatives the table above names (intermediate).
