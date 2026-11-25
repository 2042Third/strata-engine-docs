# Brief: `animation/editor`

| Field | Value |
| --- | --- |
| Title | Edit-mode poses and previews |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `animation/system`, `animation/skinning` |
| From | animation ch. 13 (the internals half); 1.11, concept 21 (`AnimationPreview`, rest poses shared per skeleton, the `ClipStart` edit pose, render transforms for attachments, the idle cost); the how-to half is `make/animation`'s |
| Unit | `plan/allocation/animation.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `animation/editor` — Edit-mode poses and previews

**Covers.** The job: `AnimationPreview` is the poses provider of scenes that do not play (the edited scene, and the
scenes that thumbnails render): it shows rest poses or the first frame of what each animator plays on start, answers
preview requests, and never writes the scene. Why it is needed (edit-mode posing): a scene that does not play has no
Animation system, and without a provider a skinned mesh is drawn in its bind pose, which in many files lies along an
axis (a Z-up export under an "Armature" node); the page shows it with a diagram or a GPU test capture, because the
editor always installs a preview. The providers diagram: `AnimationPreview` for the edited scene and thumbnails,
`AnimationSystem` for the play copy; pose versions belong to their provider, so the render scene recomputes every
palette when the provider changes. The same evaluation as play (the excerpt): `EvaluateAnimator` runs an
`AnimatorInstance` with transitions off. Rest poses shared per skeleton (the excerpt): an edit-pose key of skeleton,
controller, clip and root motion; animators looked at only on component signals; poses computed again only when a
reimport changes their sources, so an idle editor pays nothing (`AnimationPreviewStats`). The ClipStart edit pose and
`viewport.setSettings {editPose: "rest" | "clipStart"}`, the Scene view's camera chip (the robot both ways, as a
screenshot). Render transforms (the excerpt): attachments, and the meshes under them, drawn at their joints through
`ISkinningPoses::GetRenderTransforms`, never written (the rule: previews change no scene data). Posed bounds in the
editor's tools: `SceneBounds::GetPosedMeshBounds` for framing, focus, drop to ground and placement. Thumbnails make a
rest-pose preview for each scene they render. The animation commands, the editor's API for this part:
`animation.createController` makes a `.stanimator` from JSON sections; `animation.setController` replaces the given
sections as one undo step (`AssetEdit::SetControllerData`); `animation.info` (a Query) describes a model, a skeleton, a
clip, a controller, or a live animator's state and parameters; `animation.preview` (Session) is deferred until the
requested pose shows and refuses while the game plays (screenshot, with the preview chip). Each command is given as
the line to paste, with a link forward to `editor/commands`. The toy: a provider that returns rest poses, in about 40
lines. How it is tested: `Animation.Preview` (a request is posed once its own pose is computed; rest poses are what
animators evaluate with nothing playing; computed once per skeleton and again only after a reimport; a request wins
over the rest pose; the clip-start edit pose), the GPU case "Skinned models stand in their rest pose in edited scenes
as they do in play before their first animation, on both paths", and `EditorAnimationTests.cpp`. The exercise is a
trace in the debugger: how often the clip-start pose is computed for animators that share a skeleton and a clip. At
the end the reader can explain what draws a character in the editor before Play, and why editing it writes nothing to
the scene.

**Leaves out.**

- Using the preview chip → `make/commands`
- Using the Asset tab's tables and the Inspector's live state → `make/animation`
- Commands, their kinds and deferred results in general → `editor/commands`, `editor/deferred-commands`
- How thumbnails are rendered and cached → `editor/thumbnails`
- Placing content and its ghost → `editor/placement`

**Fit.** `over`: about 4,410 words against M (3,000). At or over M's top of 4,000, the page takes the next size, L (S2:
the estimate is inside L's range); three excerpts of the preview, four figures and the four commands take the most, and
the Simulate case and the trace are among what puts it over.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:153` | feature | home | A new provider recomputes every palette: versions are a provider's own (`RenderScene.cpp` 1357-1360, 1390) |
| `animation:164-170` | feature | home | The preview provider, the same evaluation as play, rest poses, the ClipStart edit pose, render transforms, the idle cost, posed bounds in editor tools |
| `animation:185-189` | feature | home | `animation.createController`, `animation.setController`, `animation.info`, `animation.preview`, `viewport.setSettings {editPose}` |
| `animation:193` | feature | home | Thumbnails make a rest-pose preview per scene they render |
| `animation:322` | concept | home | Edit-mode posing: bind pose against rest pose, rest poses per skeleton, requests that change no scene data, render transforms |
| `new:6` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:39-80`: `EvaluateAnimator`, the play-mode evaluation with transitions off |
| `new:7` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:266-304`: the edit-pose key and the animators examined only when they change |
| `new:8` | code | home | `Strata/src/Strata/Animation/AnimationPreview.cpp:440-502`: render transforms for attachments and the meshes under them |
| `animation:403` | figure | home | Diagram 14, the providers of `ISkinningPoses` |
| `animation:410` | figure | home | Screenshot 1: the robot in edit mode, rest pose and clip start side by side |
| `animation:412` | figure | home | Screenshot 2: the bind pose without a provider, as a diagram or a GPU test capture |
| `animation:415` | figure | home | Screenshot 3: `animation.preview` with the preview chip |
| `animation:461` | rule | home | Pose versions belong to their provider |
| `animation:478` | rule | home | Previews change no scene data |
| `animation:581-583` | term | home | Edit pose, pose preview, render transform |
| `animation:643` | open | home | Screenshot 2 cannot be made by editor use: the figure is a diagram or a test capture |
| `new:33` | open | home | Check: Simulate and skinned meshes. The page plans "the editor always installs a preview", and `animation:643` says the bind pose cannot be shown by editor use; both fail while Simulate runs: the running copy has no Animation system and the preview serves only the edited scene, so the viewport draws the copy's skinned meshes in their bind pose (read from the code, not run). After the photographer's capture in the pin's editor, the page states the Simulate case beside the providers (about 60 words) and screenshot 2 (`animation:412`) is made in Simulate; the check blocks the page's brief (R39). Evidence: `Strata/src/Strata/Animation/AnimationRegistration.cpp:33-36`; `Strata/src/Strata/Scene/Scene.cpp:2114-2115`; `StrataEditor/src/Editor/EditorContext.cpp:1382`, `:1399`, `:2697-2704`; `StrataEditor/src/Editor/EditorContext.h:313`, `:823`; `Strata/src/Strata/Renderer/RenderScene.cpp:1286`, `:1348`, `:1374-1384` |
| `new:34` | hands-on | home | Trace it yourself (done, track E): with a breakpoint on the call of `EvaluateAnimator` in `UpdateRestPoses`, run "The clip-start edit pose shows the first frame of what animators play on start, once per skeleton and clip" in the engine's source build, and count the hits for animators that share a skeleton and a clip. Evidence: `Strata/src/Strata/Animation/AnimationPreview.cpp:306-406` (the call at line 389), `:266-304` (the edit-pose key); `StrataTests/src/Animation/AnimationSystemTests.cpp:1540` |
| `editor-core:90` | feature | use | The `animation.*` command group |
| `animation:190` | feature | link | The preview chip, taught on `make/commands` |
| `animation:191-192` | feature | link | The Asset tab's views and the Inspector's live state, taught on `make/animation` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The Animation system, its scene services and the poses provider | `animation/system` | must |
| Skinning: bind pose and palettes | `animation/skinning` | must |
| Content versions and reimports (hot reload of assets) | `assets/importing` | must |
| Reading and running a command | `start/how-to-read` | helps |
| Commands are the API: the registry, kinds, schemas | `editor/commands` | helps |
| Commands that take frames (`Defer`, `MayDefer`) | `editor/deferred-commands` | helps |
| Undo and redo | `editor/undo` | helps |
| Play and Simulate: the running copy | `editor/play-mode` | helps |
| Thumbnails | `editor/thumbnails` | helps |
| Placing content | `editor/placement` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `edit-pose` | Edit pose | - |
| `pose-preview` | Pose preview | - |
| `render-transform` | Render transform | - |
