# Brief: `engineering/look-dev`

| Field | Value |
| --- | --- |
| Title | The look-dev harness |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `engineering/test-kinds`, `gpu/frame-tour` |
| From | build-test ch. 11 (capture, compare, signed images, metrics, the harness's own tests) |
| Unit | `plan/allocation/engineering.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `engineering/look-dev` — The look-dev harness

**Covers.** The job: the look-dev harness takes fixed pictures of the samples, of a new project and of a look-dev
scene through headless editors, and compares two sets of them; it is how a rendering change is judged, and the source
of many of the book's pictures. The problem: image regression testing; golden images, which break across GPUs and
drivers, against before-and-after comparisons with signed differences, deterministic repeats, crops of the regions
that matter and GPU times beside the pictures; the mistake of reading a number without looking at the signed image.
The map: capture (copy the samples and never open them in place; build the Basic 3D and look-dev projects with command
scripts; every shot at every size, anti-aliasing mode and repeat; crops enlarged four times; each repeat's
`renderStats` and its difference with the first; a table of GPU stage times; a static page) and compare (differing
pixels, the absolute and the signed difference images, crops side by side, the ratio of GPU times). The contract:
shots are appended and never changed, so that captures of every build keep comparing; the repeats of one build differ
by zero pixels; the harness uses only Python's standard library, its PNG reader and writer included. The toy: the
absolute difference of two images in 25 lines. The real code: the shots file and its projects; `capture_still`, which
drives `viewport.capture` for every repeat; `signed_difference`, red where the after picture is brighter and blue
where it is darker, and why an absolute difference cannot show a region that shifted as a whole; `compare` and
`ratio`; shots with `--debug-view`, `--aa`, `--quality`, and live shots with simulated input. The paragraph that
introduces the page's first Python fence says in one or two sentences what differs from C++ in it: no page of the
book teaches reading Python, so the page supplies it (R45). The shots by area, as the
rendering parts use them, in a table read from `Tools/LookDev/Shots.json` at the pin and never typed from the
inventories: the white furnace, the contact, thin and room shots, the low sun; the mirror, sheet, wet,
patch and Cornell shots of the indirect light, with the lighting views (`lookdev.view.*`), `lookdev.polished` and the
GI shots of the yard, the room, the sun room and the sealed room, about 30 more than the inventory names. How it is tested: `StrataTools.LookDevOffline` without a GPU, and
`StrataTools.LookDev`, which runs `selftest`. Exercises: capture one shot twice and see zero differences, then compare
it against a build with one small change and read the signed image; trace it yourself: follow one shot by a search
from its entry in `Shots.json` through `capture_still` to the `viewport.capture` call and the editor's command that
answers it. At the end the reader can capture and compare
two builds and tell a real change from noise.

**Leaves out.**

- Finding a conversion slip in a shader with the compare → `gpu/shaders`
- What each debug view shows → `gpu/debugging`
- The white furnace as a test of energy → `light/energy`
- How a figure of the book is made from a shot, and the machine that rendered it → `reference/figures`
- The flicker metrics → `engineering/test-kinds`
- Driving the editor with command scripts → `editor/command-scripts`

**Fit.** `fits`: about 3,295 words against M (3,000). One concept, three excerpts, two figures, the toy and the table of
shots by area, read from `Tools/LookDev/Shots.json`, take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `build-test:359` | concept | home | Image regression testing: golden images against signed before-and-after differences, deterministic repeats, crops, GPU timings beside pictures; the mistake of a number read without the image |
| `build-test:226`, `render-direct:181`, `render-image:286` | feature | home | The harness and its shots, as three inventories list them (the build's, the light area's furnace and contact shots, and the image area's `--aa`, `--debug-view` and `--live`) |
| `render-indirect:196` | feature | home | The indirect area's shots in the page's table of shots by area, read from `Tools/LookDev/Shots.json` at the pin: the inventory's nine and about 30 more (the lighting views `lookdev.view.lighting`, `.ao`, `.indirect`, `.luminance` and `.albedo`, the probe shot `lookdev.polished`, and the GI shots `lookdev.yard*`, `lookdev.room.view.*`, `lookdev.sunroom*`, `lookdev.sealedroom.view.gi`, `lookdev.grass.view.indirect`) |
| `new:15` | code | home | `Tools/LookDev/Shots.json:1-14`: the format, the rule never to change a shot, the projects and the first shot with its crops |
| `new:16` | code | home | `Tools/LookDev.py:750-769`: `capture_still`, every repeat of a shot through `viewport.capture` |
| `new:17` | code | home | `Tools/LookDev.py:340-359`: `signed_difference`, and the reason in its docstring |
| `build-test:454` | figure | home | The harness: capture (copies, headless editors, shots by sizes, modes and repeats) and compare (differences, signed differences, crops, GPU ratio) |
| `build-test:469` | figure | home | The `index.html` of `Tools/LookDev.py compare`: one pair side by side with its signed difference |
| `new:37` | hands-on | home | Trace it yourself, by a search: one shot from its entry in `Shots.json` through `capture_still` to the `viewport.capture` call and the editor's command that answers it (about 150 words). Evidence: `Tools/LookDev/Shots.json:27`; `Tools/LookDev.py:750-769`; `StrataEditor/src/Editor/EditorViewportCommands.cpp:1211` |
| `build-test:696`, `build-test:697`, `render-image:736` | term | home | Look-dev harness, with look-dev as the image inventory words it (one entry); signed difference image |
| `build-test:172` | feature | use | `StrataTools.LookDevOffline` and `StrataTools.LookDev`, homed with the other `tools` CTests on `engineering/generated-code` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Command scripts run by a headless editor | `editor/command-scripts` | must |
| The passes of a frame, anti-aliasing and TAA | `gpu/frame-tour` | must |
| The test suites and their CTests | `engineering/test-kinds` | must |
| `viewport.capture` and the editor's cameras | `editor/camera-viewport` | helps |
| The debug views | `gpu/debugging` | helps |
| GPU stages and their times | `gpu/readback-timing` | helps |
| Images as bytes: pixels and channels | `basics/bytes` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `look-dev` | Look-dev | - |
| `look-dev-harness` | Look-dev harness | - |
| `signed-difference-image` | Signed difference image | - |
