# Brief: `reference/figures`

| Field | Value |
| --- | --- |
| Title | Index of figures and their recipes |
| Kind | R |
| Size | L |
| Tracks | - |
| Needs | - |
| From | generated from the figure manifests; names the GPU of the machine that rendered them |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/figures` — Index of figures and their recipes

**Covers.** The paragraph on top says what the page is: every picture of the book, generated from the figure
manifests and `taken.json` (`../pipelines.md` §5.8), and how to read a row: the figure's id and the page that shows
it, what it shows (the recipe's `shows` line), its kind (scene, live, editor, runtime, text, reference, tool), its
recipe (project or sample, camera, settings and steps), the pin it was taken at, the GPU it was taken on (from `taken.json`),
its size and, for a slider, its pair. Hand-written: (1) how the pictures are made, in one
short section that names the photographer's run (`figures.py take` with the GPU, one run at a time, under the perf
lock), the project copies a recipe starts from, and how each picture is isolated from the machine (the recorded
settings, the forced CPU path of thumbnails, the GPU-driven path that never ran on the CI's GPUs and the
`expectAlso` check of figures that need it), written for readers; the inventories' notes on how pictures are made
instruct the photographer and stand in `../pipelines.md` §5.5, not here (R44); (2) how a reader makes a picture again
from its recipe with a build of the pin; (3) where "before" pictures come from (the look-dev baseline sets of older
releases, named with their tag). `## Where it lives in Strata` names the look-dev harness (`Tools/LookDev.py`),
`viewport.capture` and the sample screenshots. The tool is `tools/figures.py`; the page is rendered from the manifests
by the build.

**Leaves out.**

- The look-dev harness as a tool → `engineering/look-dev`
- Credits and licenses of the assets in the pictures → `appendix/credits`
- Capturing the viewport for a game → `make/automated-playtests`

**Fit.** `fits`: about 1,100 words against L (5,000). The generated rows give the page its size: about 600 pictures with
their recipes, roughly 18,000 words, which may need a split by part under the site's largest-page budget; the rows of
the W8 pages' figures arrive in phase B. The prose is the paragraph on top and the three hand-written sections.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:374-427` | figure | link | The 26 figures of the animation inventory, as rows once their manifests and recipes exist |
| `assets:453-514` | figure | link | The 29 figures of the assets inventory, as rows once their manifests and recipes exist |
| `audio-input:419-483` | figure | link | The 36 figures of the audio-input inventory, as rows once their manifests and recipes exist |
| `automation:530-590` | figure | link | The 24 figures of the automation inventory, as rows once their manifests and recipes exist |
| `build-test:420-472` | figure | link | The 28 figures of the build-test inventory, as rows once their manifests and recipes exist |
| `editor-core:461-535` | figure | link | The 35 figures of the editor-core inventory, as rows once their manifests and recipes exist |
| `editor-ui:476-582` | figure | link | The 58 figures of the editor-ui inventory, as rows once their manifests and recipes exist |
| `foundation:385-441` | figure | link | The 26 figures of the foundation inventory, as rows once their manifests and recipes exist |
| `gamedev:396-475` | figure | link | The 53 figures of the gamedev inventory, as rows once their manifests and recipes exist |
| `gameui:435-505` | figure | link | The 38 figures of the gameui inventory, as rows once their manifests and recipes exist |
| `physics:333-382` | figure | link | The 26 figures of the physics inventory, as rows once their manifests and recipes exist |
| `render-core:484-543` | figure | link | The 26 figures of the render-core inventory, as rows once their manifests and recipes exist |
| `render-direct:480-565` | figure | link | The 50 figures of the render-direct inventory, as rows once their manifests and recipes exist |
| `render-image:437-519` | figure | link | The 50 figures of the render-image inventory, as rows once their manifests and recipes exist |
| `render-indirect:375-461` | figure | link | The 58 figures of the render-indirect inventory, as rows once their manifests and recipes exist |
| `render-scene:383-454` | figure | link | The 31 figures of the render-scene inventory, as rows once their manifests and recipes exist |
| `scene-ecs:417-494` | figure | link | The 37 figures of the scene-ecs inventory, as rows once their manifests and recipes exist |
| `scripting:398-442` | figure | link | The 22 figures of the scripting inventory, as rows once their manifests and recipes exist |
| `worlds-runtime:346-408` | figure | link | The 36 figures of the worlds-runtime inventory, as rows once their manifests and recipes exist |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Capturing the viewport and debug views | `gpu/debugging` | helps |
| The look-dev harness | `engineering/look-dev` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.
