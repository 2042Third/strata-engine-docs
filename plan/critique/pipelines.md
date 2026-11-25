# Critique: the pipelines against the real engine

Key: `pipelines`. Lens: `pipelines.md` and `process.md` checked against the engine's code and tools at `822a7a46`
(read only, nothing built or run). Engine paths are relative to `G:/GameEngineAI`. "VC" means
`StrataEditor/src/Editor/EditorViewportCommands.cpp`, "LD" means `Tools/LookDev.py`, "DG" means
`Docs/DeveloperGuide.md`. Plan line numbers are the numbers of each file on its own.

Verdict: the four pipelines are the right idea, and `research/captures.md` covers the capture side well. But
`pipelines.md` dropped most of that research and invented a recipe and a fence format that the engine and Expressive
Code do not accept. Its own examples name four things that do not exist. The process also has no editor binary at the
pin for phase A, even though the phase A pilot needs one. **Fix first:** say where the binary at the pin comes from
(B1). Then rebase the recipe on `captures.md` §4 and the real `viewport.capture` result (M1-M3), and add an offline
`check` for every format that runs at the end of the write stage (M13-M14).

Severity counts: 1 blocker, 18 major, 13 minor.

---

## Blocker

### B1. Phase A has no editor at the pin, and "the working tree does not matter" is false for three of the four pipelines

- **Where:** `pipelines.md` lines 9-11 ("reads files with `git show <pin>:<path>`, so the working tree of that clone
  does not matter"), 74, 110, 120 (`--engine-build <bin folder>`). `process.md` lines 69-72 (the pilot includes the
  tutorial `make/first-script` "through all stages"), 97-100, 118 ("its tutorial has a current stamp").
- **What is wrong:**
  - The process forbids every way of getting a binary at the pin: "No docs agent builds the engine … or uses the GPU
    before 0.8.0" (`process.md` 98-99). Yet "Headless editors (for tutorials) run one at a time in phase A"
    (97-98). No release package of `822a7a46` exists: GitHub releases stop at v0.7.0.
  - `--headless` keeps the GPU. `EditorApplication.cpp:70` says "Run without a window (rendering stays available for
    captures)". Only `--no-gpu` (line 71) runs without a device. So a phase A headless editor breaks the plan's own
    no-GPU rule unless it is given `--no-gpu`.
  - The only local build, `build/windows`, is at `822a7a46dbcd` today (its `VersionCommit.h`). It follows `main`,
    which wave 8 is about to move.
  - A dev build's script builds compile against `<engine dir>/StrataScriptCore`, which is the live working tree.
    `ScriptToolchain.cpp:712` resolves the SDK from `EngineDirectory`, and `ScriptProject.cpp:223` uses
    `${STRATA_ENGINE_DIR}/StrataScriptCore/CMake`. Copying the binaries elsewhere therefore does not freeze the
    script builds.
  - Figures read the working tree as well. LD's `prepare_project` copies `ROOT / "Samples"`, `resolve_setup` turns
    `repoFile` into a path under `ROOT`, and `Shots.json`, `LookDevScene.json` and `GenerateShowcaseTerrain.py setup`
    are run from the checkout.
  - `StrataEditor --version` prints only `Strata Editor 0.7.0` (`EditorApplication.cpp:269`). The commit is reported
    only by `editor.status {sections: ["engine"]}` as `engineCommit`: 12 hex digits, with no dirty flag
    (`CMake/StrataVersionCommit.cmake`).
- **Proposed change** (`pipelines.md` "The pin"):
  > Two engine inputs.
  >
  > (a) `--engine <clone>`: a separate clone (not a worktree of `G:/GameEngineAI`), read with
  > `git cat-file --batch` at the full 40-hex pin. Used for excerpts and parsing.
  >
  > (b) `--build <folder>`: a build of exactly that commit.
  > - Phase A: one Release build of the pin, made once by the orchestrator in that clone, under
  >   `Tools/PerfLock.py`.
  > - Phase B: the official v0.8.x Windows package, checked against its `.sha256`. This is the build readers have,
  >   and its script SDK is self-contained.
  >
  > Every tool calls `editor.status {sections: ["engine"]}` and stops when `engineCommit` is not a prefix of the pin.
  > For figures and labs, the clone's working tree must be checked out at the pin and be clean
  > (`git status --porcelain` empty).

  In `process.md` 97-99, replace the phase A sentence with:
  > Phase A editors run with `--no-gpu`, one at a time, each inside
  > `python <engine>/Tools/PerfLock.py --label docs-<tool> --limit 90 -- …`. Script builds use every core and would
  > disturb wave 8's perf runs.

---

## Major

### M1. The recipe format names things that do not exist and lacks what most figures need

- **Where:** `pipelines.md` 53-72 and 80.
- **Evidence (wrong names):**
  - `entity.setProperty` is not one of the 154 registered commands. Properties are set with `component.set
    {entity|entities, component, values}` (`Commands/EntityCommands.cpp:721-729`). Its `entity` is an ID only:
    `EntitySchema` has the pattern `^[0-9A-Fa-f]{1,16}$` (`CommandUtils.cpp:71-74`). `entityName` is LookDev's
    Python convention, which `resolve_setup` resolves with `entity.find`. `captures.md` line 301 blurs this.
  - `"AntiAliasing = None"` is not a value. `AntiAliasing` is a bool and `AntiAliasingMethod` is FXAA, TAA or
    Morphological (`Renderer/RendererComponents.cpp:490-491`).
  - `"shot": "Showcase/Dusk"` is not a shot. Shot names look like `showcase.shot6`, and Dusk is a *station* of
    `GenerateShowcaseTerrain.py` (`STATIONS`, 175-178).
  - The example's thin-geometry lab already exists as the shot `lookdev.thin` (poles and fence crops).
- **Evidence (missing):**
  - `scene`: Shots.json has a scene per project and per shot (e.g. `lookdev.polished` uses `Scenes/Specular.stscene`).
  - `camera: "scene"`: depth of field and the HUD need the scene camera, and it cannot be combined with
    position/target/fov (VC 1309-1310).
  - `overlays`: the capture's own camera defaults to editor overlays **on** (VC 443, 763), so every recipe without
    it shows the grid and gizmos.
  - Play-mode stills (`play.start {paused}`, `play.step`, `input.sequence`).
  - World cells (`world.loadCells` ±20000 m, `wait`).
  - Stations, and Custom quality rows (`project.setSettings Renderer.Quality {Preset: Custom, …}`, then capture with
    `quality: "project"`).
  - Material previews (`material.set {save: false}`).
  - `debugView`.
  - `record` pointers for the numbers captions quote.
  - The project kinds the LookDev project and labs need. The plan's example only shows a sample path.
  - Crops in Shots.json's normalized `[x0, y0, x1, y1]` form. The plan uses pixel rects, which cannot inherit a
    shot's crops.
- **Proposed change.** Base the format on `captures.md` §4.1 and replace lines 53-72 with:

```json
{
  "id": "taa-thin", "shows": "…", "caption": "…", "alt": "…",
  "kind": "scene",
  "project": {"lookdev": true},
  "scene": "Scenes/LookDev.stscene",
  "shot": "lookdev.thin",
  "camera": {"position": [6, 1.5, 8], "target": [6, 0.8, 0], "fov": 40},
  "size": [1920, 1080],
  "quality": "high",
  "antiAliasing": "taa",
  "overlays": false,
  "setup": [{"command": "component.set", "entityName": "Sun",
             "parameters": {"component": "DirectionalLight", "values": {"Intensity": 120000}}}],
  "variants": {"off": {"antiAliasing": "off"}, "on": {"antiAliasing": "taa"}},
  "crops": [{"name": "fence", "rect": [0.6, 0.3, 0.95, 0.9], "scale": 4}],
  "expect": "complete",
  "record": ["/renderStats/shadowMapSize", "/temporalFrames"],
  "publish": "lossless"
}
```

  Field rules:
  - `project` is one of:
    - `{"sample": "<id>"}`: made with `project.openSample`; see m4.
    - `{"template": "empty" | "basic3d"}`.
    - `{"lookdev": true}`: the LookDev project made by `LookDev.py`, per `captures.md` §4.2.2.
    - `{"lab": "labs/<x>.json", "template": "empty"}`.
  - `camera` is `{position, target, fov}` or `"scene"`. `"editor"` is refused.
  - `quality` is a preset, or `{"custom": {<Renderer.Quality rows>}}`.
  - Also allowed: `world: {"loadAll": true}`, `station: "Dawn" | "Golden" | "Dusk"`, `postProcess: {…}` (applied to
    the one PostProcess entity), `materials: {"<path>": {…}}`, `debugView`, `play: {"steps", "input"}`, and
    `engine: "v0.7.0"` for "before" pictures.
  - A variant may override any field except `camera`, `size` and `crops`, so that sliders line up.
  - `setup` steps are the engine's command-script steps (`{command, parameters, expect, bind}`,
    `EditorCommandRunner.h:75`), plus `entityName`. The tool turns `entityName` into an `entity.find` plus `bind`
    and fails unless exactly one entity matches.
  - Move `taken` out of the writer's file (see M16).

### M2. The completeness test fails every non-TAA picture and skips fields the capture reports

- **Where:** `pipelines.md` 76-77: "no pending assets, …, at least 8 temporal frames; for global illumination also
  its settled flag".
- **Evidence:**
  - `temporalFrames` is 0 without TAA (`SceneRenderer.cpp:3045`), and the capture waits for history only under TAA
    (VC 827). The plan's own TAA off/on example can therefore never pass its "off" variant. The FXAA, morphological
    and off variants of every AA figure fail the same way.
  - The result also reports `stalePoses`, `pendingTextGlyphs`, `ui.pendingGlyphs`, `renderStats.deferredInstanceBytes`,
    `previewLighting`, `hiddenScreenSpaceTexts`, `ui.hiddenCanvases`, `notice` and, for the shadows view,
    `debugView.shadows.complete` (VC 956-988, 156-170).
  - `globalIlluminationSettled` is `true` without GI (`SceneRenderer.h:676`), so it can be required always.
  - Every wait is bounded in frames, and the command still *succeeds* when a bound runs out (VC 808-847). Only the
    client's assertions catch an incomplete picture.
  - A spatial SSR frame still waiting for its previous color is waited for (`c_MaxCaptureReflectionFrames` 2, VC 830)
    but never reported.
- **Proposed change:** define `"expect": "complete"` in `pipelines.md` as:

```json
{"/pendingAssets": {"equals": 0}, "/texturesBelowWanted": {"equals": 0}, "/stalePoses": {"equals": 0},
 "/pendingTextGlyphs": {"equals": 0}, "/ui/pendingGlyphs": {"equals": 0},
 "/localShadowViewsPending": {"equals": 0}, "/reflectionProbesPending": {"equals": 0},
 "/preExposureSettled": {"equals": true}, "/globalIlluminationSettled": {"equals": true},
 "/renderStats/deferredInstanceBytes": {"equals": 0}, "/previewLighting": {"equals": false}}
```

  Conditional additions:
  - Add `"/temporalFrames": {"min": 8}` only when the variant's AA is TAA.
  - Add `"/debugView/shadows/complete": {"equals": true}` with `debugView: "shadows"`.
  - The tool fails when `notice` is present.
  - A recipe may relax `previewLighting` (the preview-lighting figure).

  Add to the engine's additions (M15): a `complete` bool and an `incomplete: [reasons]` array in the result, and
  `screenSpaceReflectionsPending`. LookDev, the Showcase generator and the book would then share one definition.

### M3. The take algorithm leaks state between variants and figures

- **Where:** `pipelines.md` 74-79.
- **Evidence:**
  - `project.setSettings` changes the copy's project and is not undone by `scene.open`. A Custom `Renderer.Quality`
    from one figure stays for the next.
  - `viewport.setSettings` persists for the session (`captures.md` 204-208).
  - `lighting.bakeProbes` moves the previous capture to the trash (DG 742-746).
  - `captures.md` §4.2 step 3 had the correct order. `pipelines.md` dropped it.
- **Proposed change:** add to line 74:
  > Per figure and variant, in one editor per project copy, in this order:
  > 1. `scene.open {scene, force: true}`, then `scene.loadStatus {wait: true}`, then `world.loadCells` for worlds.
  > 2. `project.setSettings {section: "Renderer.Quality", reset: true}`, or the `custom` value.
  > 3. The station steps (generated by `GenerateShowcaseTerrain.py setup --format script`, never copied by hand:
  >    DG 6507-6510), the shot's `Setup`, the figure's `setup` and the variant's.
  > 4. AA and `postProcess` on the PostProcess entity (`entity.find {component: "PostProcess"}` must return one).
  > 5. `play`.
  > 6. Two `viewport.capture` calls with explicit `overlays`, `quality` and `debugView`.
  > 7. `play.stop`.
  >
  > A figure that bakes gets a fresh copy of its own.

### M4. "Capture twice, require identical files" is applied to kinds where it is false, and says nothing about failures

- **Where:** `pipelines.md` 43-47, 77-78, 89-90.
- **Evidence:**
  - Live captures: "every run of the same steps shows the same game state, but the jitter phase differs" (VC
    1247-1250; DG via `captures.md` 274-276).
  - Live captures refuse `quality` (VC 644). They draw with the Game view's quality: the project's, with the players'
    options.
  - Runtime screenshots depend on the frames the machine ran (`captures.md` 445-447).
  - Still captures are deterministic by design. History, GI and exposure restart for each capture
    (`SceneRenderer::ReleaseRenderTargets` releases GI, `SceneRenderer.cpp:2247-2262`), and noise follows the
    renderer's own temporal frame (`SceneRenderer.cpp:3116`).
  - DG 5048-5062, however, records unexplained repeat differences of GTAO and SSR after shader recompiles.
- **Proposed change:**
  - The identity rule applies to `kind: scene` only.
  - `live`: the tool checks that `fixedSteps` are equal across runs, and the photographer judges.
  - `runtime`: pass `--quality` and `--save-directory <empty temp dir>`, and require exit code 0.
  - Live figures set the project's `Renderer.Quality` preset on the copy first.
  - On a repeat mismatch, retake once in a fresh editor. If the second run also differs, mark the figure
    `nondeterministic`, do not publish it, and report it to the engine with the two images.

### M5. The published formats destroy what pixel-level figures show

- **Where:** `pipelines.md` 85-88 ("WebP at quality 92 for renders", crops "enlarged by whole factors without
  smoothing"). `site.md` line 18 ("sharp: AVIF and WebP in 960, 1920 and 3840 widths from one published original").
  `pipelines.md` 3-5 ("standard library only").
- **Evidence:**
  - Lossy WebP is always 4:2:0. At q92 it smears exactly the subjects of `image/encoding`, `image/lens-effects`,
    `image/spatial-aa`, `image/taa`, `indirect/ssr` and `light/sun-shadows-2`: dither, grain, chromatic aberration,
    banding, specular aliasing, the TAA crawl and SSR noise patterns.
  - The look-dev harness measures differences of 2-8 codes (DG 693-697).
  - Re-encoding by sharp from a lossy original is lossy twice. Resampling the 4× nearest-neighbour crops to
    960/1920/3840 smooths them again, and a 3840 file derived from a 1920 capture adds nothing.
  - Python's standard library cannot encode WebP.
- **Proposed change:**
  - `figures.py` writes PNG only, and `sha256` covers the PNG.
  - The published original is a PNG in `src/assets/figures/…`.
  - Recipes carry `publish: "lossy" | "lossless"`. The default is lossless for parts `image`, `indirect`, `light` and
    for every crop and compare slider.
  - The figures plugin derives AVIF/WebP widths only for `lossy` figures. It never resamples `lossless` figures, which
    are served at native size with `image-rendering: pixelated`.
  - The spike's budget (site check 9) measures the repository and page weight with real PNGs.

### M6. The fence format collides with Expressive Code and has no rules for real engine files

- **Where:** `pipelines.md` 21-24, 27-33. `style.md` 72-75.
- **Evidence:**
  - Expressive Code's `mark="…"` marks **text**, not lines: "To match a string of text inside your code block's
    lines, simply wrap it in quotes" (expressive-code.com, Text Markers). `mark="L2251"` would highlight the literal
    string "L2251".
  - EC's line markers count lines in the block: "Text Markers are not aware of the shifted line numbers"
    (Line Numbers plugin).
  - The example symbol `Scene::OnUpdate` does not exist. `Scene.cpp` has `OnUpdateRuntime` (2199) and
    `OnUpdateEditor` (2355). `OnUpdateRuntime` is 156 lines, well over the 60-line limit.
  - Overloads exist, e.g. `ComponentRegistry::SetInactiveReason` at `ComponentRegistry.h` 253 and 258.
  - Command handlers are lambdas inside `Register*Commands` functions of 400+ lines (VC 994-1399).
  - Inside a function the code sits two tabs deep, with `#ifdef ST_DEBUG` at column 0 (`Scene.cpp` 2215-2217). A
    common-prefix dedent therefore removes nothing.
  - Tabs are 4 columns (`.editorconfig`), and `ColumnLimit: 0`: lines reach 245 columns.
    - `EditorViewportCommands.cpp`: 382 of 1,401 lines exceed 100 columns.
    - `SceneRenderer.cpp`: 704 of 4,267 lines exceed 100 columns.
- **Proposed change:** use attributes that the excerpts plugin owns and EC ignores:

  ```` ```cpp src="engine:Strata/src/Strata/Scene/Scene.cpp" lines="2220-2243" highlight="2224,2238-2240" ````

  - The plugin emits EC's `startLineNumber=2220` and `mark={5,19-21}`.
  - While a page is being written, anchors replace `lines`:
    - `symbol="Scene::OnUpdateRuntime" from="const bool stepping" to="return;"`: substrings that must be unique
      within the symbol;
    - `symbol="…" overload=2` for overloads;
    - `command="viewport.capture"`: the `Register(… "viewport.capture"` block.
  - `fill` refuses a range over 60 lines.
  - Normalization: remove the smallest count of leading tabs over the non-blank lines that are not column-0
    preprocessor lines. Show tabs as 4 columns. Set EC `wrap` with `preserveIndent` for C++ and Slang. `check`
    compares after this normalization, and nothing else is ever changed.

### M7. `git show <pin>:path` cannot read vendor code or the book's own files

- **Where:** `pipelines.md` 10-11, 27-29, 115-116.
- **Evidence:**
  - All 19 libraries under `Strata/vendor/` are gitlinks: `git ls-tree 822a7a46 Strata/vendor/` shows mode `160000`
    for entt, imgui, box3d, NVRHI, glm and the rest. Yet `world/ecs` ("with EnTT inside"), `editor/imgui`,
    `physics/world-step` and `gpu/vulkan-nvrhi` will want to quote them.
  - Tutorial script files live in the docs repository (line 115), but `src=` reads the engine.
  - Some files exist only in builds: `Version.h` (from `Version.h.in`), `VersionCommit.h`, the embedded shaders and
    `Package/StrataInstall.json`.
  - Wave 8 moves code across files. Its branches add `SceneRendererRadianceCascades.cpp` and rewrite
    `SceneRendererLocalShadows.cpp` (971 lines changed), so a relocation that searches only the same file loses
    quotes.
- **Proposed change:** add source namespaces.
  - `engine:<path>`: a blob at the pin.
  - `vendor:<lib>/<path>`: the submodule commit from `git ls-tree <pin> Strata/vendor/<lib>`, read from the
    submodule at that commit. It links to the library's own GitHub at that commit, and the license line goes into
    `appendix/credits`.
  - `book:<path>`: the docs repository.
  - Build outputs are shown only through their templates and generators.
  - `relocate` searches the whole tree at the new pin (`git grep -F` of the block's most distinctive line) before it
    falls back to the symbol.

### M8. A tutorial cannot be a plain engine command script

- **Where:** `pipelines.md` 108-116. `style.md` 64-66. `process.md` 23-24 ("the part's running example").
- **Evidence:**
  - The command-script loader rejects every key except `command`, `parameters`, `expect`, `bind` and `until`
    (`EditorCommandRunner.cpp:431-433`). Page step numbers, file copies and comments cannot live in the script.
  - `project.create` needs an absolute directory (`EditorAssetCommands.cpp:279`, 292-293), and `asset.import` needs
    absolute files.
  - No command writes a script's source. `script.create` writes a template (`EditorScriptCommands.cpp:417-432`).
  - The only templates are `empty` and `basic3d` (`EditorAssetCommands.cpp:281`). Parts with a running example, and
    the XL project tutorials, need to start where an earlier page ended.
  - `expect` has only `equals`, `min` and `max` (`EditorCommandRunner.h:79-81`). `log.read` has no text filter
    (`EditorStateCommands.cpp:985-992`), so "the console says Hello" cannot be checked.
- **Proposed change:** use a book format, `tutorials/<part>/<chapter>.tutorial.json`:

```json
{"startsFrom": {"template": "basic3d"},
 "placeholders": ["@PROJECT@", "@BOOK@"],
 "stages": [{"step": 3,
             "files": [{"from": "book:tutorials/make/first-script/Player.cpp", "to": "Scripts/Player.cpp"}],
             "commands": [{"command": "script.build"}],
             "checks": [{"pointer": "/errors", "length": 0}]}]}
```

  - `startsFrom` may also be `{"sample": "Tetris"}` or `{"tutorial": "make/prefabs"}`, which replays that tutorial
    first.
  - `tutorials.py` compiles each stage into an engine command script (or drives StrataCLI calls), copies the files
    between stages, and evaluates its own `checks`: `contains`, `approx` with a tolerance, and `length`.
  - Readers download the compiled script with the placeholders filled.
  - Scripts count game time in `play.step` / `until {steps}`, never `editor.wait` frames (AGENTS, "Tools count game
    time in fixed steps").

### M9. Eight engine-change tutorials and every code-changing exercise have no runner

- **Where:**
  - The pages: `start/first-engine-change` (outline-1:22), `world/tutorial-component` (outline-2:17),
    `assets/extending` (outline-2:41), `gpu/first-triangle` (outline-2:51), `image/tutorial-post-effect`
    (outline-3:60), `scripting/host-api` (outline-4:18), `editor/tutorial-command` (outline-4:71),
    `editor/tutorial-panel` (outline-4:88).
  - `style.md` 52 ("at least one changes or runs real code") and 66. `process.md` 46-49 (the novice "does the
    exercises", with "no code").
- **Evidence:**
  - The tutorial tool only drives an editor. These pages change engine code, so they need a configure, a build and
    `ctest`.
  - The process forbids building, so no stage ever runs their steps or the worked solutions of code exercises.
  - The engine's own rules require tests, the feature test and layering for exactly these changes (AGENTS golden
    rules 2 and 6, "Layers").
- **Proposed change:** add `tutorials.py patch` to `pipelines.md`:
  > Apply `tutorials/<part>/<chapter>.patch` to the pin clone. Build only the touched targets in one persistent docs
  > build directory. Run the tests the page names plus `Architecture.Layering` and the feature test. Revert, then
  > stamp.
  - The page quotes hunks with `src="book:…patch#hunk-2"`.
  - Phase B runs it on the owner's machine under PerfLock.
  - Code exercises carry a solution patch that the same runner checks.
  - `process.md` 46-49: the novice answers conceptual questions only. Code exercises are judged by the runner.

### M10. UI steps cannot be verified as planned

- **Where:** `pipelines.md` 112-113 ("the reviewer walks them by hand in a windowed editor"). `style.md` 65 (every
  tutorial step has a UI half).
- **Evidence:**
  - Reviewers are agents without a pointer on a screen.
  - The process bars the GPU in phase A, and a windowed editor needs it.
  - `editor.showPanel` and `editor.showDialog` fail headless (`EditorLayer.cpp` 177-328, via `captures.md` 236).
  - UI labels are string literals, so they can be checked. Examples: `BeginMenu("File")` (`EditorLayer.cpp:1456`),
    `"Add Component"` (`Panels/InspectorPanel.cpp:448`), `BeginMenu("Create Child")`
    (`SceneHierarchyPanel.cpp:929`).
- **Proposed change:**
  1. The names lint (M13) checks every **Menu ▸ Item** path and button label against string literals in
     `StrataEditor/src/{UI,Panels}` and `EditorLayer.cpp` at the pin.
  2. In phase B, each tutorial step gets a whole-editor picture (`--screenshot`, one run per step until
     `editor.screenshot` exists), which the photographer judges against the step's text.
  3. The release checklist lists the UI-only tutorials for the owner to walk once.

  Strike "the reviewer walks them by hand".

### M11. The reference tables assume listings the engine does not have

- **Where:** `pipelines.md` 120-135. `outline-4.md` 132-134 (`reference/*` sources). `process.md` 121-122 ("by
  construction").
- **Evidence by table:**

  | Table | What the engine gives | Route |
  | --- | --- | --- |
  | commands | `editor.commands` gives name, description, parameter schema and kind (`EditorCommands.cpp:66-79`). There is **no result schema**: `EditorCommand` has none (`EditorCommands.h:87-106`). `MayDefer`, `WaitsForAssets`, `Results` and the MCP toolset (`StrataCLI/src/CLI/McpToolsets.cpp`) are not reported. | command + parse |
  | components | `component.list` gives Name, DisplayName, Type, Description, Section, Min/Max, AssetType, Options, ReadOnly and PhysicsLayer (`Reflection/PropertyJson.cpp:488-517`). There are **no defaults and no inactive reasons**. Hidden and `NoSerialize` components and hidden or transient properties are skipped (`EntityCommands.cpp:619-626`). | command; defaults by a dump script; inactive reasons parsed |
  | inactive reasons | A function of a component's values (`Reflection/Property.h:91-92`), reported per entity by `entity.get` (`EntityCommands.cpp:364-390`). | parse the `SetInactiveReason(s)` calls |
  | settings | `project.settings` (needs a project) and `preferences.get` (reads the person's file). Simple sections' schemas carry `default` (`Core/SettingsRegistry.cpp:260`). | command on an empty project; use `default`, not `value` |
  | asset types, importer versions | No command. Versions are `return N;` in `TextureImporter.h:89`, `GltfImporter.h:39`, `ColorLookupImporter.h:49` and three anonymous classes in `AssetImporters.cpp` 47, 92, 146. | parse, or a new `asset.types` |
  | quality rows and presets | The `c_<Row>Row = {Low, Medium, High, Ultra}` lines (`RendererQuality.cpp:38-55`), plus the section schema. | parse + command |
  | debug views | The `viewport.capture` schema's enum (VC 147-151). | command |
  | GPU stages | `GPUPassTimer` registrations. `gpuMs` keys appear only for stages that ran. | parse |
  | script API | See m14. | parse |

- **Proposed change:**
  - Replace the table on lines 123-131 with this route table.
  - Line 125: change "JSON Schema of parameters and result" to "parameter schema; the result as the description
    states, with an example result recorded by a tutorial run".
  - Component defaults come from a dump script: an `empty` project, then `entity.create`, `component.add` and
    `entity.get` for each addable component.
  - `process.md` 122: change "(generated, so by construction)" to "every component `component.list` returns, with
    the hidden and `NoSerialize` ones listed from the source".
  - Add to M15: `editor.commands` reports `mayDefer`, `waitsForAssets` and `results`, and a new `asset.types` command.

### M12. The reference is generated too late and its CI check cannot run

- **Where:** `process.md` 89 (reference generated in phase B). `pipelines.md` 133-135 ("the check fails when they
  differ from what the pin generates").
- **Evidence:** CI has no editor, and phase A has no package (B1). Yet writers and reviewers in phase A need the exact
  names.
- **Proposed change:**
  - `reference.py dump --build <pin build> --no-gpu` writes raw dumps to
    `reference/_dumps/<pin>/{commands,components,component-defaults,settings,preferences}.json`, each with
    `engineCommit`. It runs once in phase A step 2 and again at each pin move.
  - `reference.py render` is pure Python. It turns the dumps and the parsed sources into
    `reference/_generated/*.md`.
  - CI checks that render reproduces the committed Markdown and that the dumps' `engineCommit` matches `engine.pin`.

### M13. Reviewers need a names lint

- **Where:** `process.md` 43-45 (the technical review checks "each statement about the engine").
- **Evidence:**
  - The plan's own examples name four things that do not exist: `entity.setProperty`, `AntiAliasing = None`,
    `Scene::OnUpdate` and `Showcase/Dusk`. This kind of mistake is cheap for a tool and costly for a reader.
  - Reading cannot settle runtime behavior. The reviewer should not spend its time on names.
- **Proposed change:** add `tools/names.py` to `pipelines.md`. It checks:
  - every backticked command, parameter, component, property, enum value, settings id, debug view, quality row,
    SDK function and macro against the dumps (M12) and the SDK parse;
  - every path against `git ls-tree -r <pin>`;
  - every UI path against the UI literals (M10).

  It runs as the writer's exit check and as a site check. The technical reviewer receives its report together with
  the tutorial run logs and the capture sidecars, so that numbers in captions are compared with recorded values.

### M14. Excerpts are filled after review, so reviewers judge code they cannot see

- **Where:** `process.md` 39-40, 52-53 ("Integrate: … excerpts are filled and checked"), 50-51 ("Confirm runs for L
  and XL pages …").
- **Evidence:**
  - The symbol form exists "while a page is being written" (`pipelines.md` 30-31), so reviewers would judge fences
    with no lines in them.
  - `fill` may then pick other lines or hit the 60-line limit after review.
  - A fixer can swap a quote on an M page with no confirm.
- **Proposed change:**
  - The write stage ends with `excerpts.py fill && excerpts.py check`, `figures.py check`, `tutorials.py check` and
    `names.py`.
  - A page with anchor-form fences cannot enter review.
  - Any change of a fence's `src` or `lines` after review triggers confirm.

### M15. The engine additions are not "a small engine change", miss items, and would split the pin

- **Where:** `pipelines.md` 93-101. `process.md` 87.
- **Evidence:**
  - `editor.screenshot {panel}` must reach panel rectangles in ImGui from `StrataEditorCore`, which reaches the UI
    only through `EditorHost` (AGENTS "Editor").
  - The renderer switches are construction-time `SceneRendererSpecification` fields (`SceneRenderer.h` 142-254:
    FadeLevelsOfDetail, GPUDriven, BatchAcrossMaterials, TextureStreaming, SpecularAntiAliasing, VisibilityFeedback,
    OcclusionCulling, DitherOutput). Flipping them needs a capture renderer per specification.
  - Intermediate targets are released after every capture (`ReleaseRenderTargets`, `SceneRenderer.cpp:2247-2275`),
    and the PNG output is 8-bit. Each target needs its own visualization and GPU tests.
  - Missing from the list:
    - a light-cluster view (`light/many-lights`);
    - an energy-compensation switch (`GetSpecularEnergy`; `captures.md` 333: "A/B impossible");
    - wireframe (`draw/lod`, `gpu/geometry-pool`);
    - a culled/occluded tint (`draw/occlusion`, `draw/visibility-feedback`);
    - a glyph-atlas readout (`gpu/text`);
    - `--window-size`;
    - M2's `complete`, and M11's command flags.
  - New views change renderer code, so the statement "they change no rendering, so the book stays about 0.8.0" does
    not hold as written.
- **Proposed change:** replace lines 97-101 with tiers:
  - **Tier 1 (small, one commit each):** `complete`/`incomplete` and `screenSpaceReflectionsPending` in the capture
    result; flags in `editor.commands`; `asset.types`; `--window-size`.
  - **Tier 2 (medium):**
    - `editor.screenshot {path, overwrite, panel?}` through `EditorHost`;
    - `viewport.capture {renderer: {…}}`, refused outside captures, including energy compensation;
    - debug views `specular`, `diffuse`, `clusters`, `culled`, `wireframe`.
  - **Tier 3 (large; diagrams until then):** `viewport.capture {target: depth|normals|velocity|shadowMask|cascade<n>|
    localShadowAtlas|bloom<n>|glyphAtlas}`, and motion stills.

  The additions land on a `release/0.8` branch as **v0.8.1**, containing only them. `engine.pin` moves to v0.8.1 for
  text and pictures alike, so the book has one pin. The work is planned as engine work (by engine agents, under the
  engine's review), not by docs agents.

### M16. Several agents would write the same files

- **Where:** `pipelines.md` 70 (`taken` inside the writer's manifest), 81-83 (shared `labs/`), 139-142 (one
  `glossary.json`; "the editor pass admits them" while part editors run in parallel), 13-15 (`pin.py move` rewrites
  every page). `site.md` 150-163 (one `src/sidebar.json`). `process.md` 52-53.
- **Proposed change:** add an ownership table to `process.md`.

  | File | Only written by |
  | --- | --- |
  | `src/content/docs/<part>/<chapter>.md` | writer, fixer, part editor; integrator for mechanical repairs only (link paths, front-matter syntax, fence fill) |
  | `src/content/figures/<part>/<chapter>.json` | writer, fixer |
  | `src/assets/figures/<part>/<chapter>/{*.png, taken.json, *.result.json}` | `figures.py` (photographer) |
  | `tutorials/<part>/<chapter>.*` | writer, fixer; `stamp.json` only `tutorials.py` |
  | `labs/<name>.json` | the page the brief names as its owner; others ask through notes |
  | `sketches/<part>-<chapter>-<name>.*` | that page's writer (the prefix prevents collisions) |
  | `src/content/glossary.json` | one admitter at a time, from the notes |
  | `src/sidebar.json`, `engine.pin` | integrator; pin moves only during a freeze with no page pipeline open |
  | `reference/_dumps`, `reference/_generated` | `reference.py` |
  | `plan/notes/<part>/<chapter>.md`, `plan/reviews/<part>/<chapter>-<role>.md` | the writer and each reviewer |

  Each page pipeline works on a branch of its own that touches only its rows, and the integrator merges.

### M17. The pilot cannot exercise the picture pipeline

- **Where:** `process.md` 69-72 (`image/tone-mapping` "picture recipes") and 97-99. `process.md` 87 (pictures only in
  phase B).
- **Evidence:** about 120 rendering pages would write recipes in phase A against a format that nothing has run. The
  format's errors (M1-M3) would show up only after those pages are "reviewed". PerfLock exists so that GPU runs never
  overlap perf measurements (DG 757-759).
- **Proposed change:**
  - In phase A step 2, add `figures.py check`, run offline against the pin's dumps:
    - schema and unique ids;
    - shot names, scenes and entity names at the pin;
    - debug-view and quality enums;
    - sizes from 16 to 4096;
    - refusal of `Camera: "editor"` shots.
  - Either allow one PerfLock'ed GPU session for the pilot's recipes, or replace `image/tone-mapping` in the pilot
    with a page whose figures are diagrams and move the recipe pilot to the start of phase B.

### M18. A missing step in the photographer's loop: re-reading pages once pictures exist

- **Where:** `process.md` 39-40, 87-88. `style.md` 23 (the Show beat is a picture).
- **Evidence:** novice review of rendering pages happens over placeholders, so captions and the paragraphs that point
  into a figure ("notice the crawl on the fence") are never read against the real picture.
- **Proposed change:** in phase B step 8, after a page's pictures are taken, a short novice re-read covers the
  captions and the text around each figure. Status `final` requires it.

---

## Minor

- **m1. A short hash as the pin.** `pipelines.md` 9 stores `822a7a46`. Store the full 40-hex sha, with the tag as a
  comment: tags can move, and rc tags exist (`v0.3.0-rc1…rc3`).
- **m2. Whole-editor pictures do not depend on the machine's fonts.** `pipelines.md` 89 says they do, but the
  editor's fonts are committed files (AGENTS, "Third-party code"). The real variance comes from:
  - the display scale without `--ui-scale`;
  - the window size without `--windowed` (1600×900, `EditorApplication.cpp:72`);
  - the launcher footer's GPU and startup time;
  - Console timestamps and live statistics;
  - background thumbnails.

  Add `--windowed --ui-scale 1`, a copied `--layout`, a controlled `STRATA_RECENT_PROJECTS` file, and a final
  `editor.wait`.
- **m3. Shipped-game options.** The row on `pipelines.md` 46 lacks `--save-directory <empty dir>` (the default is the
  player's data: `StrataRuntime/src/RuntimeApplication.cpp:351`), `--quality` and `--windowed`. `--screenshot` needs a window
  and a GPU.
- **m4. Making sample copies.** Use `project.openSample {sample, directory}` (`EditorAssetCommands.cpp:388-397`). It
  copies the build's own `Samples` without `.strata` (`.strata` also holds play-mode saves and players' options:
  `EditorContext.cpp:1393`, 1647). This avoids copying the clone's working tree (B1).
- **m5. "Before" pictures from older releases.** `pipelines.md` 103-104. Packages v0.6.0 and v0.7.0 exist on GitHub,
  but their capture results lack fields (M2). LookDev baselines of every shot at both sizes and in all modes already
  exist on the reference machine (DG 769-772). With the owner's leave, take "before" pictures from them, and add
  `engine` to the recipe.
- **m6. Stamp contents.** `pipelines.md` 110-112. A stamp holds:
  - `engineCommit` from `editor.status`, and the build or package id;
  - OS and configuration;
  - the sha256 of the compiled script *and of every copied file*;
  - the checks' results.

  Draft pages are exempt until phase B.
- **m7. Moving the pin cannot list "the pictures to take again".** `pipelines.md` 13-15. Retake all of them and diff
  with `LookDev.py compare` (signed differences). The list of changed pictures goes to the photographer.
- **m8. One process per quote.** Run `git cat-file --batch` once instead of 1,500 `git show` processes.
- **m9. Compiling sketches.** `pipelines.md` 34-35. Slang sketches need the slangc pinned by `CMake/StrataSlang.cmake`
  (SHA-256). C++ sketches need `-std=c++20` and glm from the pin's submodule.
- **m10. Labs readers can run.** `pipelines.md` 81-83. Labs assume an open project (`--project <dir> --commands
  lab.json`) and contain no `project.create`. Their textures are generated the way LD's `make_leaf_texture` does, or
  are committed CC0 files credited in `appendix/credits`.
- **m11. Shot hazards.**
  - `Camera: "editor"` shots (e.g. `tp.editor`) are not reproducible on copies.
  - Shots that name entity IDs (`tp.dof` with `350D7DDD7ED21DD5`) depend on the sample's content.
  - Shots.json freezes only "an existing shot's camera or crops" (its `_comment`). Setup steps and AA modes may still
    change, and look-dev content appended to a scene can enter old frames. Re-judge reused shots at each pin move.
- **m12. The capture's own camera is an editor view.** In edit mode a scene without lights gets preview lighting, and
  the HUD and canvases are hidden (VC 1218-1220, 444). Game pictures use `camera: "scene"` or play mode, and the
  completeness check rejects `previewLighting: true` (M2).
- **m13. Players' graphics options cannot be set.** Only `graphics.resetPlayerOptions` exists. Figures of the options
  menus (`make/look`, `image/quality-settings`) need a script in play mode or a new command.
- **m14. Listing the script API.**
  - Host functions are the members of the C struct `StrataScriptHostAPI` (`ScriptABI.h` from line 312), whose
    declaration order is the ABI's append order. `ST_SCRIPT_HOST_FUNCTIONS` lives in the engine
    (`Scripting/ScriptHostAPI.cpp:3431`), not in the SDK headers, which outline-4:132 implies.
  - Callbacks are the members of `StrataScriptClassDesc` (772-831).
  - SDK classes: port the rules of `StrataTests/src/FeatureTest/SDKReader.h` (tokenizer plus scope tracking), but
    keep the `//` comments.
  - Macros: `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` (`Script.h` 852-857).
  - "Added in" for each host function comes from `git log -S` over the release tags.
- **m15. Integrator's kit.** The integrator needs the pin clone, the pinned Node and Python tools, the dumps, write
  access only to its rows in M16, and a rule that a content failure goes back to the fixer, never into an integrator
  edit.
- **m16. Run every tool under PerfLock.** Tutorials and reference dumps run under
  `python <engine>/Tools/PerfLock.py --label docs-… --limit 90 -- python -I tools/….py`, with a private
  `STRATA_SESSION_DIR`, a controlled `STRATA_RECENT_PROJECTS`, and `--no-gpu` unless they capture.
- **m17. Optional: tutorials in docs CI after 0.8.0.** The Linux package on `ubuntu-24.04`, `--no-gpu`, and CMake
  plus GCC for script builds would let CI re-run every editor tutorial on each push instead of trusting stamps.

## Proposed tool commands (one place)

```text
excerpts.py  fill | check | relocate | list     --engine <clone> --pin <sha>
names.py     check                              --dumps reference/_dumps/<pin> --engine <clone>
figures.py   check                              (offline; dumps + Shots.json at the pin)
figures.py   take    --build <bin> --engine <clone at pin> [--figures <glob>] [--kinds scene,live,editor,runtime]
figures.py   compare --before <dir> --after <dir>   (delegates to Tools/LookDev.py compare)
figures.py   publish --from <dir>
tutorials.py check                              (offline: compiled scripts against the commands dump's schemas)
tutorials.py run     --build <bin> [--no-gpu]
tutorials.py patch   --engine <clone> --build-dir <dir>
reference.py dump    --build <bin> --no-gpu     (writes reference/_dumps/<pin>)
reference.py render                             (pure; CI)
pin.py       move <sha> | status                (only during a freeze)
```

Every runner is wrapped in `Tools/PerfLock.py` and uses a private session directory.

## Not checked

- I ran nothing: whether still captures repeat bit for bit with GI on, and how long script builds take, are
  inferred from the code and the DG, not measured.
- I read the inventories only where `captures.md` cited them.
- The site and framework choices (Astro and Starlight versions, Expressive Code 0.44.3 existing) are the site
  critic's lens. I checked only EC's marker semantics.
- Wave 8 branches were inspected only as `git diff --stat` and two short diffs from the main repository, to gauge
  what moves at the re-pin.
