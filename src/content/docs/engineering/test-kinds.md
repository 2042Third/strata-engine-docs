---
id: engineering/test-kinds
title: "GPU, end-to-end and package tests"
description: "The tests that need more than the test binary: a graphics device, the built programs, a toolchain or an installation, and how each kind stays reliable."
kind: internals
size: L
tracks: [E]
needs: [engineering/test-program, gpu/first-triangle, editor/command-scripts]
time: 85
learn:
  - id: choose-suite
    text: choose the kind of suite a change needs, from a unit suite to a package test
  - id: gpu-check
    text: write a GPU check that respects the shared device, reads results back and ends with the error count
  - id: flicker-meter
    text: explain what the flicker meter measures and why it keeps only pixels that three frames agree on
  - id: extend-end-to-end
    text: add an expectation to a sample's command script and run its test through ctest
  - id: trace-chain
    text: trace a fixture chain from its first test to every test that requires it
since: 0.3.0
status: final
---

Most of Strata's tests live inside one program, `StrataTests`, and finish in milliseconds. A few kinds of fact cannot be
checked there. Whether a :term[shader]{id=shader} draws the right pixels needs a :term[graphics processing unit]{id=gpu} (GPU). Whether the editor starts,
obeys a script and exits with the right code needs the editor itself. Whether a released archive holds the right files
needs a real installation.

This page covers the suites that reach outside the test program, how each one keeps its
results reliable, and how you choose among them. It does not teach how to write a GPU test from the first line (that is
[the first triangle](../gpu/first-triangle.md)), the command script format ([command scripts](../editor/command-scripts.md))
or the perf suites ([the perf lab](../engineering/perf-lab.md)).

## The problem and how engines solve it

A unit test runs one function and compares its result with a number you wrote down. That works while everything the
function needs is in memory. Three needs break it: a GPU, a second program, and a build :term[toolchain]{id=build-tools}. Each one brings a way
to fail that has nothing to do with the code under test.

Take the GPU first. A :term[renderer]{id=renderer} test draws a scene, copies the pixels to the :term[central processing unit]{id=processor} (CPU) and compares them with what the scene should look like. Engines solve the missing display with a device that has no window, called a headless device, and Strata does the same. Making a device is costly, and some drivers and :term[overlay]{id=overlay-core} tools handle repeated creation and destruction badly. So every test shares one device.

A graphics call that misuses the application programming interface (API) often still draws something plausible. The :term[validation layer]{id=validation-layer}, a checking layer between the program and the driver, reports such misuse as an error message. A test that only compares pixels would pass while the layer complains, so each test also checks that no new errors arrived. [The first triangle](../gpu/first-triangle.md) teaches both rules; this page takes them as given.

Three more problems arrive only with many GPU tests:

- Exactness. The same scene renders to slightly different :term[bytes]{id=byte} on different drivers and shader paths, so a test cannot ask for equal pixels everywhere. Engines choose between exact equality on one reference machine, a tolerance per colour channel, and a comparison with a stored image through a perceptual measure. Strata compares two renderings of one scene with a small tolerance, and keeps the scene simple, so a larger gap means a bug.
- Timing. The GPU works frames behind the CPU, so a count the renderer reports may describe an older frame. A test must wait for the right frame and never assume the answer is ready.
- Speed. Validation multiplies the cost of every call, so a test that measures time must run without it.

Now the second program. An :term[end-to-end test]{id=end-to-end-test} starts the built editor, command-line client or game and judges what the
user would see: its output, its :term[exit code]{id=exit-code} and the files it leaves. The dangers are a program that hangs, a port that
another test already uses, a leftover process that disturbs the next run, and state in the user's folders. Engines
answer with a timeout on every wait, a private folder for each run, and a rule that whatever a test starts, the test
ends. Strata adds ports that the test never fixes: the editor chooses one and publishes it in a session file that the
test reads.

The third need is the toolchain. A game's scripts build against an installed software development kit (:term[SDK]{id=sdk}), with :term[CMake]{id=cmake} and a :term[compiler]{id=compiler}, so a test of that path runs those programs for minutes. Concurrent builds through one toolchain fail in ways that look random, so such tests take a lock and run one at a time. The slowest check of all is the installation. The test installs the engine into a fresh folder and uses only what landed there, because a file missing from the install would otherwise hide behind the source tree next to it.

Cost explains why Strata keeps these suites apart from the unit tests. A developer runs the unit :term[shards]{id=shard} constantly. The
GPU suites need a driver and carry a label, `gpu`, so that a machine without one skips them with `-LE gpu`. The package
tests, which need a compiler, carry the label `package`. Labels and shards come from
[the test program](../engineering/test-program.md); this page names which suites carry which label and why.

## The map of the suites

The tests outside the unit shards fall into five families, and the rest of the page walks through them in this order. The GPU suites run inside `StrataTests` and share one device. The end-to-end suites also run inside `StrataTests`, but start the built programs. The command-script tests and the sample tests run those programs through `cmake -P` helper scripts, one script per sample. The package and install tests run the toolchain.

The next diagram shows the chains `ctest` builds from fixtures. A fixture is a name that one test prepares and others
require: :term[CTest]{id=ctest} runs the setup first, and skips a test whose required setup failed. The export chain cleans a folder,
has the editor export a small game into it, and then runs many tests on that game.

```mermaid caption="The export chain: a clean test, the editor's export, then every test that runs the exported game. Windowed checks come last and need a GPU." alt="A graph from a clean test to the editor export. From the export, arrows lead to the runtime tests that run the exported game: smoke, identity and perf log tests, and the windowed tests that need a GPU."
flowchart LR
	Clean["StrataExport.Clean<br/>(removes the folder)"] -->|StrataExportClean| Export["StrataEditor.Export<br/>(--no-gpu, exports SmokeGame)"]
	Export -->|StrataExportedGame| Smoke["StrataRuntime.Smoke<br/>Identity, Seconds, Invalid..."]
	Export -->|StrataExportedGame| PerfLog["StrataRuntime.PerfLog<br/>then its Check"]
	Export -->|StrataExportedGame| Windowed["Render, Resolution, PerfLogWindowed<br/>(label gpu)"]
```

The feature test has its own chain, and the sample tests have a third. A sample's export is a setup for the GPU
render checks, and for the perf suite that tours the exported Open World and Showcase games.

```mermaid caption="The feature-test chain and the sample chain. Each arrow is a fixture that the earlier test prepares and the later test requires." alt="Two graphs. The first runs from a clean test to a copy test, to the editor's feature test and to the runtime's feature tests. The second runs from a sample's test to its render check and to the sample perf test, which also needs the perf results clean."
flowchart LR
	FClean["StrataFeatureTest.Clean"] --> FCopy["StrataFeatureTest.Copy"]
	FCopy --> FEditor["StrataEditor.FeatureTest"]
	FEditor --> FRuntime["StrataRuntime.FeatureTest<br/>and FeatureTestQuality"]
	SampleTest["StrataEditor.OpenWorld<br/>StrataEditor.Showcase"] --> Render["StrataEditor.OpenWorldRender<br/>ShowcaseRender"]
	SampleTest --> PerfSamples["StrataTests.PerfGPU.Samples"]
	PerfClean["StrataTests.PerfResults.Clean"] --> PerfSamples
```

The perf results are a fourth chain of two links. `StrataTests.PerfResults.Clean` removes last run's result file, and
the perf suites require its fixture, so a result file always holds exactly one run. The feature-test chain belongs to
[the feature test](../engineering/feature-test.md).

## The contract

Two rules hold for every suite of these kinds, and each has a reason.

:::rule
Every GPU test gets its device from `Tests::GPUContext`, and every one ends with no new validation errors. Creating :term[Vulkan]{id=vulkan} instances again and again can crash drivers under load, and an error that no test reads is a bug nobody sees. See [the first triangle](../gpu/first-triangle.md).
:::

The second rule is for end-to-end suites: they own what they start. A test that starts a program gives it a private
session folder, never a fixed port, a timeout on every wait, and an ending that terminates the program even when a
check fails first. In practice that means a small class whose :term[destructor]{id=destructor} terminates the child, because a test that fails
stops at its first failed requirement and would otherwise leave the editor running.

Four working habits follow from these two rules. A test waits by the clock or on a condition, never by counting frames, because :term[frame time]{id=frame-time} differs between machines. A test keeps its files in a temporary folder that the test helpers create, and never sets its own environment for a child, because the setting would leak into the next test. A test reads no program from outside the build. All four serve one aim: the result of a test depends only on the build and the clock.

## A toy version

The toy test below does what every end-to-end test does at its core. It starts a program, waits for it by a deadline
and checks the exit code and the text it printed. The program under test is the toy itself, started again with a mode
word, so the sketch needs nothing else.

```cpp sketch="engineering-test-kinds-toy.cpp"
// A toy end-to-end test: start a program, wait for it by the clock, check its exit code and its output.
// The program under test is this executable itself, started again with a mode argument.
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <future>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

struct RunResult
{
	bool TimedOut = false;
	int ExitCode = -1;
	std::string Output;
};

// Runs `program mode`, sends its output to a file and gives up waiting after `timeout`.
RunResult RunProgram(const std::string& program, const std::string& mode, std::chrono::milliseconds timeout)
{
	const std::filesystem::path outputPath = std::filesystem::path("toy-" + mode + ".txt");
	std::string command = "\"" + program + "\" " + mode + " > \"" + outputPath.string() + "\"";
#if defined(_WIN32)
	command = "\"" + command + "\""; // cmd.exe strips one pair of quotes
#endif
	std::future<int> child = std::async(std::launch::async, [command]() { return std::system(command.c_str()); });

	RunResult result;
	// The deadline is a time, never a count of polls or frames.
	result.TimedOut = child.wait_for(timeout) != std::future_status::ready;
	result.ExitCode = child.get(); // a real harness would terminate the child here instead of waiting
	std::stringstream text;
	text << std::ifstream(outputPath).rdbuf(); // the temporary closes the file before it is removed
	result.Output = text.str();
	std::filesystem::remove(outputPath);
	return result;
}

int main(int argc, char** argv)
{
	if (argc > 1 && std::string(argv[1]) == "ready")
	{
		std::cout << "Running headless\n";
		return 0;
	}
	if (argc > 1 && std::string(argv[1]) == "slow")
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(400));
		return 0;
	}

	const RunResult quick = RunProgram(argv[0], "ready", std::chrono::seconds(10));
	std::cout << "ready: timed out " << quick.TimedOut << ", exit " << quick.ExitCode << ", says '" << quick.Output.substr(0, 16) << "'\n";
	const RunResult slow = RunProgram(argv[0], "slow", std::chrono::milliseconds(100));
	std::cout << "slow: timed out " << slow.TimedOut << ", exit " << slow.ExitCode << "\n";
	return 0;
}
```

```text output-of="engineering-test-kinds-toy.cpp"
ready: timed out 0, exit 0, says 'Running headless'
slow: timed out 1, exit 0
```

1. **Line 29:** `std::async` starts the child on its own thread, because `std::system` blocks until the program ends.
2. **Line 33:** The wait has a deadline in milliseconds, so a hung child cannot hang the test.
3. **Line 34:** `get` returns the exit code; a real harness would terminate the child here instead of waiting for it.
4. **Lines 44–53:** The program under test has two modes: print a line and exit, or sleep for 400 ms.
5. **Line 55:** The first run asks for the exit code 0 and the printed text.

The program under test prints a line or sleeps, and the first run of `RunProgram` finishes long before its ten second
deadline. The second run asks for 100 ms while the child sleeps for 400 ms, so the deadline passes. Both runs write the
output to a file, because a test can read that file after the child has gone.

The toy omits the part a real harness cannot: it waits for the slow child to finish, where Strata's `Process`
class terminates it. It also uses the shell to send the output into a file, where Strata captures the pipes itself. The structure is
the same: a start, a bounded wait, then checks on what the program did.

## The real code

### The shared device and its error count

A GPU suite begins by making a `Tests::GPUContext`. The :term[constructor]{id=constructor} below builds the shared device on the first call in
the process and later calls return the same device. Search for the lines about validation and for the place where the starting error count is kept.

```cpp src="StrataTests/src/Renderer/GPUTestUtils.cpp#L29-L50" symbol="GPUContext::GPUContext"
GPUContext::GPUContext()
{
	SharedGPU& shared = GetSharedGPU();
	if (!shared.Initialized)
	{
		shared.Initialized = true;
		GraphicsDeviceSpecification specification;
		specification.ApplicationName = "StrataTests";
		specification.Headless = true;
		// Validation layers multiply the CPU cost of every GPU call, so the perf tests measure without them: their
		// CTest (StrataTests.PerfGPU) sets STRATA_TEST_GPU_VALIDATION=0. Everything else validates.
		const std::optional<std::string> validation = Platform::GetEnvVar("STRATA_TEST_GPU_VALIDATION");
		specification.EnableValidation = !validation || *validation != "0";
		shared.Device = GraphicsDevice::Create(specification);
		if (shared.Device && !Renderer::Init(*shared.Device))
			shared.Device.reset();
	}

	m_Device = shared.Device.get();
	if (m_Device)
		m_InitialErrorCount = m_Device->GetErrorCount();
}
```

1. **Line 37:** `Headless` makes a device without a window, so the suite runs on a machine with a driver and no display.
2. **Lines 38–41:** Validation is on unless the variable holds `0`; the perf CTest disables it to measure time.
3. **Lines 42–44:** A device or renderer that fails to start is dropped, and `IsValid()` tells the test to stop.
4. **Line 49:** The error count at this moment is the baseline for `GetNewErrorCount()`.

The context makes a headless device, so no window exists. Validation stays on unless the :term[environment variable]{id=environment-variable} `STRATA_TEST_GPU_VALIDATION` is `0`. Only one CTest sets it: `StrataTests.PerfGPU`, whose job is to measure time, and validation would inflate every call. Every other GPU test validates.

The context also stores the device's error count at its start, so `GetNewErrorCount()` reports only the errors that arrived during this test. The shared device lives for the whole run, so errors of earlier tests must not fail a later one.

The destructor waits for the GPU and collects :term[deferred releases]{id=deferred-release}, so each test starts from an idle device. A related
method, `ExecuteAndWait`, runs a closed :term[command list]{id=command-list} and waits for it, then runs :term[NVRHI's]{id=nvrhi} garbage collection so the
command buffer returns to its pool. Without that step, every later `open()` would create a new command pool, and a
perf test that submits thousands of lists would measure the cost of that creation. The suite `GPU.TestUtils` checks this
with a reference count: after each of three submissions, the buffer the list wrote has one owner left, not one more
for every submission.

### Exact pixels against tolerances

An exact-pixel test needs a renderer that adds nothing of its own. Two helpers make one. `ExactSpecification()` disables
texture streaming and output :term[dithering]{id=dithering}, and `AddNeutralPostProcess` adds a post-process entity with no tone curve,
bloom, vignette or anti-aliasing, so colours that need no lighting come out unchanged. Both are taught in
[the post-effect tutorial](../image/tutorial-post-effect.md); here you only need to know that they exist and what they
remove.

:::example[One scene, three renderings, two tolerances]
The lighting suite `GPU.SceneRenderer.Lighting` checks clustered light culling with 500 point lights and 4 spot lights, in a view 160 pixels wide and 90 high. It renders the scene three times: with the normal clustered renderer, with a reference renderer that has one cluster and room for 1,024 lights, and with the CPU-driven path. The single-cluster image is the reference, because it has no culling to get wrong. The test calls `MaxDifference`, the largest gap in any byte of any pixel. The clustered result may differ from the reference by at most 2 of 255, and from the CPU path by at most 1.

Those numbers are tiny but not zero. Two shaders that add the same 500 lights in a different order round differently, and
a bound of 0 would fail on every other driver. A bound of 20 would hide a light dropped from a cluster, because one light
among 500 changes a pixel by only a few codes. The tolerance is chosen as the smallest gap the honest difference
allows, and the test then also counts the lights: `counts.Lights > 300` and `counts.CulledLights > 0`, so the scene
really exercised culling.
:::

### Counts that arrive frames later

A renderer that draws on the GPU also counts on the GPU: how many instances survived culling, how many draws it made. Those counters travel back to the CPU a few frames later, so reading the statistics right after `Render` can return an older frame's numbers. The helper `GetDrawnCounts(renderer)` hides that.

When the renderer drew with the CPU path, the helper returns the statistics at once. When the GPU drove the frame, it calls `ResolveGPUStats(true)` and requires that the counters belong to the frame the test rendered. It checks that the counter overflow is 0, then adds the GPU's numbers to what the CPU drew itself, such as transparent surfaces.

A sister helper, `GetLightCounts`, does the same for lights. A test waits for an exact frame and never renders again until the numbers look right. Waiting a count of frames passes on a fast machine and fails on a slow one. The related helper `AddUploadBacklog` shows the other face of the same delay. It adds enough meshes to exceed what the scene's GPU copy takes in two frames, so a test can check what happens when objects reach the GPU three or more frames late.

### Reading buffers and noise

Two more helpers read data back. `ReadBufferRange(gpu, buffer, offset, size)` creates a buffer that the CPU can read, copies the
range into it, waits with `ExecuteAndWait` and returns the bytes, or an empty vector when the copy cannot be made.
`ReadMeshGeometry` uses it to return each stream of a mesh (positions, attributes, skin, indices) as the geometry pool
holds them, or nothing while the mesh is not uploaded yet. The pool may compact and move a mesh, so a test reads the
location again every time. `MeasureNoise(image, rect)` returns how noisy a rectangle of a readback image is; the
reflection suites use it to check that a filter lowers noise and does not blur an edge.

### The flicker meter

Pixel tests judge one image. Some defects only exist between images: a light that gives a different result for the same
surface point in each frame. A person sees this as shimmer, and a unit test on a single frame cannot see it. The
**flicker meter** is the renderer tests' one tool for measuring it: the amount by which a surface point's value changes
from frame to frame, beyond a steady drift. Look at the type that carries one frame, and at what the comment above the
:term[namespace]{id=namespace} promises.

```cpp src="StrataTests/src/Renderer/FlickerMetrics.h#L11-L50"
// The wave's one flicker meter (suite Renderer.FlickerMetrics): how much a sequence's light changes from frame to frame at
// the same world point, beyond a steady drift. Each pixel of the newest frame of a triple is reprojected by depth into the
// two before it, and only where all three frames saw the same surface (depth and normal agree) the second difference of its
// value, relative to its mean, is measured. Statistics are fractions; reports multiply them by 100. Docs/DeveloperGuide.md,
// "GPU tests".
namespace Strata::Tests
{

	// One frame of a measured sequence, read back from a renderer that rendered it with HDROutput and a forced pre-exposure.
	struct FlickerFrame
	{
		uint32_t Width = 0, Height = 0;
		std::vector<float> Value;      // Rec. 709 luminance of the measured image (the HDR target)
		std::vector<float> ViewDepth;  // Meters along the camera's forward axis; 0 where nothing was drawn
		std::vector<glm::vec3> Normal; // World space, unit (the prepass's)
		glm::mat4 ViewProjection;      // The frame's, as rendered (jittered with TAA), camera-relative
		glm::dvec3 CameraPosition;
		glm::vec3 CameraForward;
	};

	struct FlickerResult
	{
		double Mean = 0, P99 = 0;         // Per pixel |d|
		double Blocks = 0, BlocksP99 = 0; // Per 32x32 block |mean d|
		double MeasuredShare = 0;         // Pixels measured over all pixels
		uint32_t Frames = 0;              // Triples averaged
	};

	// HDR, depth, normals; Renderer::ReadTexture.
	FlickerFrame ReadFlickerFrame(SceneRenderer& renderer, const SceneCamera& camera);

	// A frame as the person sees it: Value is the Rec. 709 luminance of the 8-bit output (GetOutputTexture) decoded from sRGB to
	// linear, after tone mapping and FXAA or TAA; depth and normals are the prepass's, as ReadFlickerFrame reads them.
	FlickerFrame ReadDisplayFlickerFrame(SceneRenderer& renderer, const SceneCamera& camera);

	// The linear Rec. 709 luminance of an 8-bit sRGB-encoded color (ReadDisplayFlickerFrame's Value).
	float GetDisplayLuminance(uint8_t red, uint8_t green, uint8_t blue);

	// a oldest.
	FlickerResult MeasureFlicker(const FlickerFrame& a, const FlickerFrame& b, const FlickerFrame& c, uint32_t blockPixels = 32);
```

1. **Lines 11–15:** The comment states the whole contract: reprojection by depth, agreement of the surface, and the second difference relative to the mean.
2. **Lines 20–28:** One frame holds the value, depth, normals and camera, everything needed to project a pixel into another frame.
3. **Lines 31–37:** The result has per pixel and per block statistics, all as fractions.
4. **Lines 49–50:** `MeasureFlicker` takes three frames, the oldest first.

The meter works on three frames at a time. Each pixel of the newest frame is turned into a world point by its depth, and
that point is projected into the two frames before it (reprojection by depth, as in
[motion vectors](../draw/motion-vectors.md)). A pixel counts only if all three frames saw the same surface there, which
means that depth and normal agree. Where an object appears from behind another, a disocclusion, the old frames saw
something else, and the pixel would score a difference that is not flicker.

For the pixels that remain, the meter takes the second difference of the value over the three frames, written as
$d$, divided by their mean. In symbols, $d = (c - 2b + a) / \max(m, 0.001)$, where $a$ is the oldest value, $b$ the
middle one, $c$ the newest and $m$ their mean. The value $d$ divides by never drops below 0.001, so a black pixel cannot divide by zero. The second difference is zero when the value changes by the same amount
each frame, so a light that fades steadily scores nothing.

Two small cases show the limits. Values of 1.0, 1.1 and 1.2 have a second difference of $1.2 - 2.2 + 1.0 = 0$: a
steady drift, no flicker. Values of 1.0, 1.1 and 1.0 give $1.0 - 2.2 + 1.0 = -0.2$ and a mean of 1.033, so $|d|$ is
0.194, about 19 % of the value. The suite `Renderer.FlickerMetrics` tests both kinds: a steady drift, and these three values exactly.

Then `FlickerResult` reports statistics. `Mean` and `P99` are the average and the 99th percentile of $|d|$ per pixel. `Blocks` and `BlocksP99` use blocks of 32 by 32 pixels and take the absolute value of each block's mean $d$. Random noise of single pixels cancels in that mean, so what remains is the change of a whole region. A block counts only when more than half of its pixels were measured.

`MeasuredShare` is the fraction of pixels measured, and a low share warns that the camera moved too fast for the test to say anything. `FlickerSequence` keeps only the last three frames, because a 3840 by 2160 frame holds about 166 MB here, and averages the triples it has seen.

The indirect-light suite uses it while the camera slides sideways for a number of frames. After each frame the test reads a `FlickerFrame`, adds it to a `FlickerSequence` and compares `Blocks` with a bound. One bound of the suite is `c_GIGrassBlocks = 0.00038`, which is 0.038 % of the value. The numbers are fractions, and the report multiplies them by 100 for people.

### The suites by area

The GPU suites carry the `GPU` prefix and the label `gpu`. They sit beside CPU suites of the same area, which check the
arithmetic without a device. The table shows the light area, and each light page of the book names its own.

| Area | GPU suite | CPU suite beside it | What the pair checks |
| --- | --- | --- | --- |
| Lights | `GPU.SceneRenderer.Lighting` | `Renderer.LightUnits` | The CPU suite checks that every light's intensity names its unit; the GPU suite checks clustering and shading on the device |
| Sun shadows | `GPU.SceneRenderer.Shadows` | `Renderer.ShadowCascades` | The CPU suite checks the cascade layout; the GPU suite draws and samples the cascades |
| Shadow filters | `GPU.SceneRenderer.ShadowFilter` | (none) | Only the device can show how a filter softens an edge, so no CPU suite stands beside it |
| Local light shadows | `GPU.SceneRenderer.LocalShadows` | `Renderer.ShadowView` | The CPU suite checks the shadow views; the GPU suite draws the shadows of point and spot lights |

The split follows one rule: whatever can be decided without a device is tested without one, because those tests run
everywhere and in milliseconds. The GPU suite only checks that the device agrees with the CPU result.

### The end-to-end suites

The `EndToEnd` suites start the built editor, command-line client and :term[runtime]{id=runtime}. CTest runs them as one test, `StrataEditor.Automation`, and passes the program paths in `STRATA_TEST_EDITOR_PATH`, `STRATA_TEST_CLI_PATH` and `STRATA_TEST_RUNTIME_PATH`. Run directly, the tests look next to the test :term[executable]{id=executable}.

There are three suites. `EndToEnd.StandardStreams` checks what the programs print and which exit code they end with, including Ctrl+C. `EndToEnd.EditorAutomation` lets an agent build, play, save and export a game through the command-line client, and checks that the Model Context Protocol (MCP) server lists the editor's commands as tools. `EndToEnd.Recovery` kills an editor and checks what the next one recovers.

Their setup follows the contract. A small structure creates a temporary folder, points `STRATA_SESSION_DIR` at a
folder inside it, and empties `STRATA_EDITOR_PORT`, `STRATA_EDITOR_TOKEN` and `STRATA_EDITOR_PATH`, so no real editor on
the machine can answer. A class `EditorProcess` starts the editor with `--no-gpu`, and its destructor terminates the
process if it still runs. The test never writes a port: it waits until the editor's session accepts a connection with its token and reads the port from it.

The recovery test shows why this design pays. It edits a scene, waits until the journal reaches the disk, then calls
`Kill()`, which ends the editor the way a crash would, without any cleanup of its own. A second editor starts on the same
project and the test checks that it offers the lost changes. No unit test can kill the process that runs it.

### Runners for programs that run by themselves

Not every end-to-end test is a C++ test. Two CMake scripts wrap a program for CTest. `ExpectFailure.cmake` runs a command and passes only if the exit code matches (1 by default, 3 for a :term[command line]{id=terminal-command} the program does not understand) and the output matches a pattern. A test with it notices a crash after a message as well as a missing message.

`RunAndExpect.cmake` is the opposite: the exit code must be 0, the output must contain every listed text, and every listed path must exist afterwards. With `MIN_SECONDS` the run must also have lasted at least that long. The runtime's option tests use both: an invalid frame count must fail with its message, and a valid game must write its log, icon and manifest next to itself.

### Command scripts as test data

A command script is a file, so it is test data. The editor's :term[smoke test]{id=smoke-test} is one: `StrataEditor.SmokeClean` removes the
project folder, `StrataEditor.Smoke` runs the editor windowed with `--commands`, and `StrataEditor.SmokeCaptureCheck`
reads the capture it wrote. The script is quoted whole on [command scripts](../editor/command-scripts.md). It creates a
floor, a sun, a lamp and a crate, takes a 960 by 540 capture at `SmokeViewport.png`, undoes and redoes an edit, plays,
steps two :term[fixed steps]{id=fixed-step} and stops. `--quit-after-commands` ends the editor when the script ends, and `--frames 3600` only
bounds a hang.

The capture check is the :term[helper mode]{id=helper-mode} `check-image` of `StrataTests`: the image must decode and must be neither nearly
black nor a single colour, and options can demand a dominant colour or an exact size. It is a deliberately weak check. It
catches a black frame, a broken capture path and a failed device, and leaves exact pixels to the GPU suites.

The test keeps its capture in the build folder. The picture below shows the same scene: the script's five entity steps
run in an empty project. The book's picture tool captures it at the same size, with the editor's overlays, from a camera
of its own.

::figure{id=smoke-scene}

Other scripts test how a run ends. `WILL_FAIL` is a CTest property that turns a failing exit into a pass. With it, a
failing command (`FailingCommands.json`), a script longer than its `--frames` budget (`UnfinishedCommands.json`) and a
quit before the last command (`QuitEarlyCommands.json`) must each fail the run. A script that waits within its budget
(`WaitCommands.json`) and one that ends with a quit (`QuitCommands.json`, with a 60 second timeout) must pass, so the
editor never hangs in the background.

### The export chain and the runtime's options

The chain in the first diagram runs the editor with `--no-gpu` on `ExportCommands.json`. That script creates a small game and exports it three times: plain, with a start scene that has no camera, and with a title, version and icon. The runtime tests of this chain then require the fixture `StrataExportedGame`. They run the exported game headless for a few frames. They check its identity (title, version and icon), the asset budget option, the perf log and a screenshot, and they feed bad values to `--frames`, `--seconds` and the quality preset.

The tests that need a window and a GPU carry the label `gpu`: `Render`, `Resolution`, `Quality`, `PerfLogWindowed` and `NoCameraScreenshot`. Everything else runs on a machine without graphics.

### Sample regressions

Each of the five samples (`Showcase`, `ThirdPerson`, `OpenWorld`, `PhysicsPlayground` and `Tetris`) has a command script
that plays it the way an agent does. `SampleProject.cmake` is the one runner behind all of them. Read its :term[header]{id=header}: it lists
the steps and the options of the runner.

```cmake src="StrataTests/Editor/SampleProject.cmake#L1-L20"
# Plays a sample project (Samples/<Directory>) through the real editor the way an agent does, then runs its exported games:
#   1. the sample is copied into an empty directory (its .strata cache is never copied), refusing a directory that does not
#      hold the named project;
#   2. the editor runs the sample's command script (COMMANDS, configured with the export directories as JSON strings:
#      @EXPORT_DIR_JSON@ and @PRUNED_EXPORT_DIR_JSON@), which builds, plays, checks with "expect" and "until" and exports
#      the game in full and pruned; its output must hold every EDITOR_EXPECT line;
#   3. both exports must hold the game, its .stgame manifest, its .stpak and the script module the manifest names, the
#      pruned pack must not be larger, and the games GAME_RUNS names (full, pruned or both, the default) run headless for
#      GAME_FRAMES frames (with a perf log when PERF_LOG is on: <export>/Perf.csv) with their saves in the work directory,
#      printing every GAME_EXPECT line.
# No output may hold a warning, error or critical line that no ALLOWED_MESSAGES expression matches, nor the editor's one
# that no EDITOR_ALLOWED_MESSAGES expression matches either (each with its reason where the test is declared).
#
# cmake -DEDITOR=<StrataEditor> -DSAMPLE_DIR=<Samples/Name> -DPROJECT_FILE=<Name.stproj> -DGAME=<exported name>
#       -DCOMMANDS=<NameCommands.json.in> -DWORK_DIR=<directory> -DEXECUTABLE_SUFFIX=<.exe or empty>
#       [-DEDITOR_EXPECT=a|b] [-DGAME_EXPECT=a|b] [-DGAME_FRAMES=120] [-DPERF_LOG=ON] [-DALLOWED_MESSAGES=regex|regex]
#       [-DEDITOR_ALLOWED_MESSAGES=regex|regex] [-DGAME_RUNS=full|pruned]
#       [-DPERF_CHECKER=<StrataTests> -DPERF_CHECK=--nonzero|Column|...] (the perf logs checked by check-perf-log)
#       -P SampleProject.cmake
# Lists are separated by '|' (a ';' would split the test's command line), so expressions use character classes, not '|'.
```

1. **Lines 2–3:** The copy leaves the `.strata` cache behind, so a stale cache cannot hide a bug.
2. **Lines 4–6:** The command script gets the export folders as :term[JSON]{id=json} strings and must print every expected line.
3. **Lines 7–10:** Both exports are checked, and the games run headless for a number of frames.
4. **Lines 11–12:** Any warning, error or critical line that no listed expression matches fails the run.
5. **Lines 14–19:** The options of the runner, written as the `cmake` call that CTest makes.

The runner copies the sample into an empty folder, never copying the `.strata` cache, so a stale cache cannot hide a
bug. The sample's script builds scripts, plays with :term[simulated input]{id=simulated-input}, and checks with `expect` and `until`. It then
exports the game twice: full, and pruned to what the scenes use. Both exports run headless, and the pruned pack must not
be larger than the full one. The last rule matters most: no output may hold a warning, error or critical line that an
`ALLOWED_MESSAGES` expression does not match, and each such expression is declared with its reason at the test.

The Tetris test is the shortest example of what a sample script proves. Its editor must print `Tetris: cleared 1 line; score 209, lines 1, level 2`,
which the script reaches by playing a fixed piece sequence, and later `Tetris: game over` and a restart with a second
seed. A change that breaks scoring, input or script loading breaks that line. GPU checks then run the editor headless on the copied
project with render command scripts (`StrataEditor.OpenWorldRender`, `StrataEditor.ShowcaseRender`), and `StrataTests.PerfGPU.Samples` tours the exported
Open World and Showcase games for the perf suites.

### Package and install tests

These tests run the toolchain, hold the `toolchain` lock and carry the label `package`; most have a 30 minute timeout. `StrataScriptCore.Package` and `StrataScriptCore.PackageDist` build a small project, `StrataTests/PackageProject`, through the installed-style SDK package with the engine's generator. They check that the package gives scripts the same `glm` definitions as the engine's own, and they load the module with the test executable.

`StrataTests.Package` runs the :term[doctest]{id=doctest} suites whose names start with `Package`, such as `Package.ScriptBuild`. `StrataEditor.Scripts` drives the real editor to create a project, build and attach a script, play and export the game. It then runs the export headless and checks that the script ran.

The strictest is `StrataEditor.Install`. Search for the list of expected entries and what a difference does.

```cmake src="StrataTests/Editor/InstallEndToEnd.cmake#L44-L60"
execute_process(COMMAND "${CMAKE_COMMAND}" --install "${BUILD_DIR}" --config "${CONFIG}" --prefix "${prefix}"
	OUTPUT_VARIABLE output ERROR_VARIABLE output RESULT_VARIABLE result)
message("${output}")
if(NOT result EQUAL 0)
	fail("cmake --install failed (${result})")
endif()

# Exactly what a release holds at its top: anything else (a dependency's install rules, a stray file) would ship too.
set(expected_entries
	"Docs" "README.md" "Samples" "Skills" "StrataCLI${EXECUTABLE_SUFFIX}" "StrataEditor${EXECUTABLE_SUFFIX}" "StrataInstall.json"
	"StrataRuntime${EXECUTABLE_SUFFIX}" "StrataScriptCore" "ThirdPartyNotices.md")
list(SORT expected_entries)
file(GLOB entries LIST_DIRECTORIES true RELATIVE "${prefix}" "${prefix}/*")
list(SORT entries)
if(NOT entries STREQUAL expected_entries)
	fail("the installation's top level holds '${entries}', expected '${expected_entries}'")
endif()
```

1. **Lines 44–49:** The test installs into the fresh prefix and fails with the exit code when the install fails.
2. **Lines 51–54:** The comment gives the reason for the list: a stray file would ship too.
3. **Lines 55–57:** Both lists are sorted, so the comparison does not depend on the order of files.
4. **Lines 58–60:** The whole listing is compared, and the failure message names both sides.

The test installs into a fresh prefix, the empty folder that `cmake --install` fills, and the top level must hold exactly the listed entries. A dependency's stray
install rule or a forgotten file would ship in the release, so the test compares the whole list, and does not search for the files it knows. It then checks that no sample carries a local `.strata` folder, that `StrataInstall.json` names the
build's version, and, on Windows, that the editor and runtime are windowed programs and the command-line client a console
program. It finally makes a project from the `basic3d` template with the installed editor alone, builds a script with the
installed SDK, plays, exports, and runs the game. The build's engine folder must be the installation, never the source
tree; the rules the install checks are on [releasing](../engineering/releasing.md).

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| A new device for every GPU test | Simple test setups | Complete isolation between tests | Driver crashes from instance churn, and much slower runs |
| Comparing renderings with stored reference images | Many engines and look-dev harnesses | Catches any visible change | Images that differ per driver, large files in the :term[repository]{id=repository} |
| Perceptual image difference with a threshold | Rendering test services | Fewer false failures from rounding | A threshold that hides small real bugs |
| Running end-to-end tests inside the test process | Libraries with no programs of their own | Faster tests, simple debugging | A crash or hang takes the whole run with it, and the exit code is never tested |
| Fixed ports and shared session folders | Quick local scripts | Simple setup | Collisions between tests and with a real editor |
| Building packages once and sharing them | Large build servers | Less time per run | Stale files hiding an install or build error |

Strata does use stored images, for the look-dev harness, and leaves their judgement to
[look-dev](../engineering/look-dev.md): a stored image answers whether the look changed, and a tolerance test answers
whether two paths agree. The two questions need different tools.

## How it is tested

The test helpers have tests of their own. The suite `GPU.TestUtils` checks that `ExecuteAndWait` recycles the command buffer: it counts the owners of a written buffer after three submissions and ends with `GetNewErrorCount() == 0`. The suite `Renderer.FlickerMetrics` has cases for a steady drift, an alternating value, depth and normal edges and a block with half its pixels measured. It also has cases for the reprojection that follows the camera, a sequence that holds three frames and the decoding of :term[sRGB]{id=srgb} into :term[luminance]{id=luminance}. The runners are tested by the CTest entries that use them, with `WILL_FAIL` where a failure is the point.

To run a family, use its label or name. `ctest --preset windows-debug -L gpu` runs the GPU kinds, `-L package` the
toolchain ones, and `-R StrataRuntime` the runtime's options (the chain's setup tests run first by themselves). To
see a chain's order without running it, use `ctest -N`, which lists the tests a run would include without running them; the fixtures, not the listing, decide what runs first. A single
GPU suite runs directly: `build/windows/bin/Debug/StrataTests.exe --test-suite=GPU.SceneRenderer.Lighting`.

## Changing it safely

Choose the cheapest kind that can see the defect. A rule of arithmetic belongs in a unit suite. A difference between
the CPU and GPU paths belongs in a `GPU` suite with a tolerance. A behaviour of a program as a whole, such as an exit
code or a printed message, belongs in an end-to-end test. A toolchain or installation question belongs in a package test.

When you add a GPU test, share the device through `GPUContext` and never create one. Render with `ExactSpecification` and `AddNeutralPostProcess` when pixels matter. End with `CHECK(gpu.GetNewErrorCount() == 0)`. Read counts through `GetDrawnCounts`, never from the renderer's statistics directly. A test that measures time belongs to the perf suites, which run without validation.

When you add an end-to-end test, give it a private session folder and an ending that terminates what it started.
Wait with `Tests::WaitUntil` and a time. Use `--no-gpu` unless the test needs pixels. Never set the environment for
a child outside a scoped helper. A new sample feature gets an `expect` in the sample's script, and a message that the
game logs on purpose and nobody listed gets an `ALLOWED_MESSAGES` entry with its reason, never a looser pattern.

Two edits often go wrong. A new CTest that uses an exported game must require `StrataExportedGame`, or it runs
before the export exists when `ctest -j` runs it in parallel. A new test that builds scripts must hold the `toolchain`
lock. Check both with `ctest -N` and one parallel run.

## Summary

- A change needs a GPU, a second program, a toolchain or an installation to be tested: choose the cheapest kind of suite that can see it.
- GPU suites share one device, end with no new validation errors, compare renderings with small tolerances and read counts for the right frame.
- The flicker meter projects the newest frame into the two before it and measures the second difference only where all three saw one surface.
- End-to-end tests give each run a private session and terminate what they started; sample tests copy a sample, run its command script, export it and fail on any warning nobody listed.
- Fixture chains order setup and use: you trace one by searching for its fixture name and confirm the order with `ctest -N`.

## Check yourself

1. A new test renders a scene with a post effect on and compares the output with a hard-coded colour. It fails on one
   driver by 1 code out of 255. What is wrong with the test?

   - A. Nothing: exact equality is the right check for pixels.
   - B. It should compare with a tolerance and use `ExactSpecification` and `AddNeutralPostProcess`.
   - C. It should create its own device for isolation.

   :::answer{tests="choose-suite,gpu-check"}
   B. A is wrong: different drivers round differently, so a bound of zero fails for no real fault. C is wrong: a
   second device brings the instance churn the shared device exists to avoid. With the neutral setup, a gap of 1 or 2
   codes is rounding, and a gap of 20 would be a bug.
   :::

2. The flicker meter reads values of 2.0, 2.0 and 2.2 at one world point in three frames. What is $|d|$, rounded to two decimals?

   :::answer{tests="flicker-meter"}
   The second difference is $2.2 - 4.0 + 2.0 = 0.2$. The mean is $6.2 / 3 = 2.067$, so $|d| = 0.2 / 2.067 = 0.10$. The
   value jumped at the last frame and did not drift, so the meter reports about 10 %.
   :::

3. A test reads `renderer.GetStats().Instances` right after `Render` and gets 0 on the GPU-driven path. Why, and what should it call?

   :::answer{tests="gpu-check"}
   On the GPU-driven path the GPU counts the instances it draws, so the CPU statistics hold only what the CPU drew itself, and the GPU's counters arrive frames later. The test should call `GetDrawnCounts(renderer)`, which resolves the GPU statistics, requires that they belong
   to this frame and adds them.
   :::

4. A developer adds a test that runs the exported game but forgets to require a fixture. `ctest -j 8` passes on their machine most of the time and fails on the build server. Why?

   :::answer{tests="trace-chain,choose-suite"}
   Without `FIXTURES_REQUIRED StrataExportedGame`, CTest has no reason to run the export first, so the test runs
   beside it or before it and finds no game. It passes when the export happens to finish earlier. Requiring the fixture
   makes CTest order them, and `ctest -N` shows the order.
   :::

5. Which kind of test checks that the released archive holds nothing but what a release promises?

   :::answer{tests="choose-suite"}
   The install test, `StrataEditor.Install`: it installs into a fresh prefix and compares the whole top-level listing
   with the expected one. A unit test cannot see an install rule, and the sample tests run the programs of the build folder.
   :::

6. You add a feature to a sample that logs a warning on purpose, and the sample's CTest now fails. What do you change?

   :::answer{tests="extend-end-to-end"}
   Add an `ALLOWED_MESSAGES` entry (or `EDITOR_ALLOWED_MESSAGES` for the editor's log) to that test's declaration in `StrataTests/CMakeLists.txt`, with a comment that gives the reason. The entry matches that one message. Loosening the runner would let a real warning pass, and the runner fails on any warning that nobody listed.
   :::

## Exercises

1. **Basic.** Write a GPU test that creates a buffer of 64 bytes, writes the values 0 to 15 as 32-bit :term[integers]{id=integer} into
   it, reads them back with `ReadBufferRange` and checks all of them. It must end with the error count check. Run it
   under validation.

   :::answer[Worked solution]{tests="gpu-check"}
   Start with `Tests::GPUContext gpu; REQUIRE(gpu.IsValid());`. Create a buffer with `byteSize = 64`, the initial state `CopyDest` and `keepInitialState = true`. Open a command list, call `writeBuffer(buffer, values, 64)`, close it and run `gpu.ExecuteAndWait(list)`.

   Then `ReadBufferRange(gpu, buffer, 0, 64)` returns 64 bytes: `REQUIRE(bytes.size() == 64)`. Copy them into 16 integers and compare each with its index. Finish with `CHECK(gpu.GetNewErrorCount() == 0)`. The `GPU.TestUtils` suite in `StrataTests/src/Renderer/GPUTestUtilsTests.cpp` is the model for the buffer and the list.
   :::

2. **Medium.** You added a feature to the Tetris sample that logs `Tetris: hold used`. Add the expectation so that its test
   fails when the line is missing, and run it.

   :::answer[Worked solution]{tests="extend-end-to-end,choose-suite"}
   The editor's output is checked by the `EDITOR_EXPECT` list of the `StrataEditor.Tetris` test in
   `StrataTests/CMakeLists.txt`: append `|Tetris: hold used` to its string. For a value rather than a log line, add an
   `expect` to a command of `StrataTests/Editor/TetrisCommands.json.in`, which names a :term[JSON pointer]{id=json-pointer} and a test, as the
   smoke script does with `"/stepsRun": { "equals": 2 }`. Re-run the :term[configure step]{id=configure-step}, then `ctest --preset windows-debug -R StrataEditor.Tetris`.
   Change the text and see the test fail, so you know the check can fail.
   :::

3. **Hard.** Trace it yourself: find every CTest that requires the exported game, starting at `StrataExport.Clean`, and
   confirm the order.

   :::answer[Worked solution]{tests="trace-chain"}
   Search `StrataTests/CMakeLists.txt` for `StrataExportClean`, which `StrataExport.Clean` prepares (near line 612). The
   test `StrataEditor.Export` requires it and prepares `StrataExportedGame` (near line 620). Search for
   `StrataExportedGame`: `StrataRuntime.Smoke`, `Identity`, `Seconds`, `PerfLog`, `Render`, `Resolution`, `PerfLogWindowed`
   and the invalid-option tests require it. Some of those prepare fixtures of their own, such as `StrataRuntimePerfLog`,
   which the perf log check requires. Run `ctest --preset windows-debug -N -R "StrataExport|StrataEditor.Export|StrataRuntime"`:
   the clean test and the export come before every runtime test.
   :::

## Where it lives in Strata

- GPU device and helpers: `StrataTests/src/Renderer/GPUTestUtils.h`, `GPUTestUtils.cpp`, `SceneRendererTestUtils.h`, `ReflectionMetrics.h`.
- Flicker meter: `StrataTests/src/Renderer/FlickerMetrics.h`, `FlickerMetrics.cpp`, suite `Renderer.FlickerMetrics`, used by `GPUSceneIndirectFlickerTests.cpp`.
- End-to-end suites: `StrataTests/src/Editor/StandardStreamsProcessTests.cpp`, `EditorAutomationProcessTests.cpp`; CTest `StrataEditor.Automation`.
- Runners: `StrataTests/ExpectFailure.cmake`, `StrataTests/Editor/RunAndExpect.cmake`, `SampleProject.cmake`, `ScriptsEndToEnd.cmake`, `InstallEndToEnd.cmake`.
- Command scripts as data: `StrataTests/Editor/SmokeCommands.json.in` and one `<Sample>Commands.json.in` per sample.
- Chains and labels: `StrataTests/CMakeLists.txt`; the setting `STRATA_TEST_GPU_VALIDATION`.

## Further reading

- CMake documentation, "ctest" and "FIXTURES_REQUIRED" test property (cmake.org): fixtures and labels, beginner to intermediate.
- Khronos Vulkan validation layers, in the Vulkan documentation (registry.khronos.org): what the layer reports, intermediate.
- Glenn Fiedler, "Fix your timestep" (gafferongames.com): why tests and games wait by time, not by frames, beginner.
