---
id: reference/figures
title: "Index of figures and their recipes"
description: "Every picture of the book with what it shows, the recipe that makes it, the GPU that took it, and how to make it again."
kind: reference
size: L
tracks: []
needs: []
status: final
---

A reader of a graphics book soon asks: how was this picture made, and can I make it myself? Every picture of this book has a **recipe**: a short written description of the project it starts from, the camera, the settings and the commands that bring the scene to the moment shown. The table below lists the :value{key="figures.count"} figures that have a recipe, so you can find a picture, see what it shows and learn how to reproduce it.

A row is one figure. The first two columns name the page that shows it and its id on that page. The third gives what it shows. The fourth is the recipe in short: its kind, the project or sample it starts from, and the look-dev shot it uses, when it uses one.

A shot is a fixed camera view of the look-dev harness, a tool of the engine that takes the same pictures on every build so that two builds can be compared.

The fifth column tells whether the picture exists yet. The sixth names the :term[graphics processing unit]{id=gpu} (GPU) of the machine that took the picture. A figure not taken yet has no GPU.

The kind says how a picture is made. A `scene` figure is a still of a project's scene. A `live` figure reads back what the Game view presented while the game ran, to show motion. An `editor` figure shows the editor's window, and a `runtime` figure a game running in the runtime program. A `text` figure is the output of a command or a program.

A `reference` figure is the output of a small program you can read and run. A `tool` figure is a page of a tool, and a `diagram` is drawn, not taken.

A slider that compares two pictures is two variants of one recipe. The variants share the project, the camera and the size, and change only what the slider is about, such as a setting or a version of the engine. The table lists the recipe once; the two sides of a slider are its variants.

::include{file="figures.md"}

## How the pictures are made

One scripted run takes all the pictures of one kind. The run starts a headless editor, one that opens no window, on a copy of the recipe's project. The editor plays the recipe's steps in their order, and then asks for the picture with the command `viewport.capture`. The run takes every figure twice and accepts it only when both takes give the same bytes, or the same text for a text figure.

Only one such run goes at a time on a machine. The run goes through `Tools/PerfLock.py`, which holds a lock file in the temporary folder of the user. A run waits while another program measures the machine. The wait matters because the GPU times a picture records mean little when something else uses the GPU.

A recipe never opens a shipped project in place. A recipe that names a sample starts from a fresh copy of it.

A recipe that names the look-dev project starts from the project that `Tools/LookDev.py` builds with a command script from the `empty` template. A recipe that names a template starts from a new project of that template. After each figure, the run restores the project's settings, so the steps of one figure never leak into the next. A figure that needs a scene opened again, or that bakes reflection probes, gets a copy of its own.

Three measures keep a picture from depending on the machine. First, the recipe states every setting that changes the look: the quality preset or its custom fields, the anti-aliasing mode, the post-processing values and the time of day. A setting the recipe omits stays at the project's value, so the picture shows what a new project gets.

Second, the recipe's `record` field names values of the capture's result, which the run stores with the picture. A caption may quote such a value, so a number in a caption is always one the capture measured. Third, the `expect` and `expectAlso` fields of a recipe state what the result must hold: that every asset finished loading, or that a counter lies in a range. The run rejects a take that breaks the expectation.

The renderer has two ways to choose what to draw and to draw it.

The default is the GPU-driven path, on devices that support it. The other is the path of the central processing unit (CPU), the reference and the fallback. The result of a capture reports which one drew the frame as `renderStats.gpuDriven`. A figure that is about the GPU-driven path states that with an `expectAlso` check on that value, so a machine that falls back to the CPU path cannot produce it by mistake. The editor always draws thumbnails through the CPU path, with the same pixels, so a picture of the Content Browser does not depend on the device either.

## Making a picture again

You need a build of the engine at the version the book describes, a GPU for every kind but `text` and `reference`, and the figure's recipe. The recipe sits in a file of the book named for the page that shows the figure. Read its fields from the top and repeat them in the editor, or through its command interface, in this order.

First copy the project. For a sample, copy the sample's folder and open the copy: opening the original would change it. Then open the scene the recipe names, apply its `setup` steps, which are editor commands with their parameters, and set the quality, anti-aliasing, time of day and post-processing it lists. Then capture. The parameters of the command are the recipe's camera, size, quality and debug view, a mode that draws one part of the image alone, such as the shadows.

The next fence shows one capture as a command. Look at `camera`, which asks for the scene's own camera, and at `quality`, which draws at a preset whatever the project chose.

```json
{
  "command": "viewport.capture",
  "parameters": {
    "camera": "scene",
    "width": 1920,
    "height": 1080,
    "quality": "high"
  }
}
```

The command renders the scene and returns the picture. Before it returns, it renders again while assets are still loading, up to about five seconds, and while the effects that need several frames settle, so the picture you get is complete. Its result also holds `renderStats`, from which you can read the draws, the lights and the GPU's time per stage. Your picture will match the book's closely, not bit for bit: another GPU or driver rounds differently, and the table names the GPU of the book's picture so you can judge a difference.

A `text` figure is simpler. Run the command or the program of its recipe, with the arguments it lists, and keep the parts of the result it names. A `reference` figure is a small program: compile it, run it and compare its output.

## Where the before pictures come from

Some figures are a slider with a "before" side, a picture of an older release. The recipe names a baseline set instead of taking a new picture: `v0.6.0`, `v0.7.0` or `v0.7.0-medium`, the last being the stills of release 0.7.0 at the Medium preset. Each set came from the look-dev harness run on that release's build: every shot of the harness, at each size and anti-aliasing mode.

A before picture therefore needs a shot of the harness; a recipe that sets `baseline` must name one. The harness only adds shots and content, never changes them, so a capture of any build still compares with a capture of an older one. If a baseline lacks the shot, the size or the anti-aliasing mode the recipe asks for, the check of the recipe fails and says which is missing.

The harness also makes the comparison. Its `compare` command reports the pixels that differ between two sets, difference images and the ratio of the GPU times. [The look-dev page](../engineering/look-dev.md) teaches the harness as a tool; [the debugging page](../gpu/debugging.md) teaches the debug views and the capture command itself. Capturing the viewport for a game, as a test, is the subject of [automated playtests](../make/automated-playtests.md).

## Where it lives in Strata

- `Tools/LookDev.py`: the look-dev harness, which captures the fixed shots of the samples and compares two sets of them.
- `Tools/LookDev/Shots.json`: the shots a recipe names with its `shot` field.
- `Tools/LookDev/LookDevScene.json`: the command script that builds the look-dev project.
- `Tools/PerfLock.py`: the lock that lets one run measure the machine at a time.
- `viewport.capture`: the command that renders and returns a picture, with its `renderStats`.
- `Samples/`: the sample projects that recipes copy; all but Tetris keep their own screenshots in a `Screenshots` folder.
