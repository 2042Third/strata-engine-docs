# Brief: `image/quality-settings`

| Field | Value |
| --- | --- |
| Title | Quality settings and players' graphics options |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `image/taa`, `light/sun-shadows-2`, `world/projects-settings` |
| From | render-image ch. 11; 1.9 (cost against look, rows and presets, traits, Custom, the section, `IGameGraphics`, the options file, the script SDK, why no render scale); home of "never below native resolution" · W8r (the quality rows and their presets) |
| Unit | `plan/allocation/image.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `image/quality-settings` — Quality settings and players' graphics options

**Covers.** The job: keep a scene's look apart from a machine's cost, and let players choose within it. The page opens
with the Physics Playground's look-dev shot `pp.scene` at Low, Medium, High and Ultra (`render-image:515`): the scene
asks for no screen-space reflections, global illumination or motion blur, so the caption names what changes from the
generated table (the detail of its shadows, its ambient occlusion, its levels of detail, its sky's prefiltered
reflections), while its exposure, curve and grade stay as the scene set them. The full section "The problem and how
engines solve it": quality presets in engines, cost knobs against look controls, dynamic resolution and temporal
upscalers. This page is the home of Strata's first design
decision, never below native resolution (a `:::why` aside: no render scale below 1, no dynamic resolution, no temporal
upscaling; the price is a GPU cost that does not adapt, and MSAA and supersampling are the alternatives the Roadmap
keeps; `new:11`). The map (diagram `render-image:475`, which also draws the runtime's layering of `worlds-runtime:380`):
the section's default (High), the project's value, the players' choices, the `--quality` option; rows that follow the
preset, and the players' rows; `GameRenderer` pulls the result by its version. Medium is Strata 0.6.0's costs and
`SceneRendererSpecification`'s default, so tests, tools and perf scenes keep their cost and a new row's default is
Medium's value; High is the `Renderer.Quality` section's default, the programs' (`AGENTS.md`'s rule, with its reason).
The toy is a preset table and an override layer in about 40 lines.

The real code: code #30 (`PresetRow`, one line per knob with its four values; the row traits; `ApplyQualityOverrides` on
the frame's copy of the Post Process component), `RendererQualitySettings` and its enums, `GetPreset`, `Clamp`,
`ResolveShadowMapSize`, the `Renderer.Quality` section (`MakeSection`, `FromSectionValue`, `ToSectionValue`, its
version) and the live changes of `SetQuality`. The players' options: `IGameGraphics` (quoted from `EngineServices.h`),
`GameGraphicsService` and `GraphicsOptions.json`, written atomically and read within a bound, the value pulled when
asked by a version compare, so that the service does no work per frame; how a player's choices combine: a row that
follows the preset, when set, switches the player's preset to Custom from the look in effect, choosing a preset keeps
only the preset and the rows that do not follow it, each option reports its source (project, player or command line), a
reset of the preset also removes the rows that follow it, choices go by name and never by number, and a file that is no
options file is ignored with one warning while a load never rewrites it; the script SDK's `Graphics` (`Options`, `Get`,
`Set`, `SetPreset`, `Reset`, `Save`, with `GraphicsOption` and `QualityPreset`; the Manual's example) and its seven host
functions; who follows which quality (diagram `render-image:477`: the game, the Game view, the Scene view's chip,
captures, thumbnails and bakes, `--quality` and its log line). Figures: `render-image:517` (the Graphics Quality page
and the Scene view's chip; the Post Process inspector's TAA tunables are `editor-ui:560`'s picture, shown on
`image/taa`) and `render-image:519` (the Third-Person sample's Graphics menu). The rules: a quality row never changes a
look control (exposure, curve, grade) and never adds an effect, but scales or drops the cost of what a scene asks for
(some presets drop a scene's reflections or motion blur, others give global illumination to the scenes that ask for it;
the generated table shows which); the four comfort rows (`MotionBlur`, `DepthOfField`, `FilmGrain`,
`ChromaticAberration`) only turn off, and the `AntiAliasing` row is a preference that may turn anti-aliasing on and
choose its method, where the guide's table says otherwise (`new:12`); adding a row touches every place the guide lists
and bumps the section's version; only `GameGraphicsService` touches the options file. Each effect's own row and its cost
are taught on that effect's page; this page has the table as a whole, generated, and states no preset value in prose.
How it is tested: `Renderer.Quality`, `GPU.SceneRenderer.Quality` (`new:29`: `SetQuality` makes again only what a
changed knob sizes; changing the quality and back draws the same image), `Runtime.GameGraphics` and its sweep,
`Scripting.Graphics`, `Editor.GameGraphics`. The exercises trace a player's choice from a script to the renderer
(`new:26`) and add a quality row. At the end the reader can add a row, say what a player's choice overrides, and defend
native resolution.

**Leaves out.**

- Each effect's own quality row and its cost → `light/sun-shadows-1`, `light/local-shadows`, `indirect/ao`, `indirect/ssr`, `indirect/probes`, `indirect/gi-cascades`, `image/motion-blur`
- The script ABI and how host functions are added → `scripting/host-api`
- How the Graphics Quality page is drawn → `editor-ui/settings-windows`
- A game's settings screen and its Graphics row → `make/menus`, `make/quality`
- The runtime that owns the players' options in a shipped game → `worlds/runtime`
- Every measured cost and its budget → `reference/performance`
- Every row with its four preset values → `reference/renderer`

**Fit.** `fits`: about 5,400 words against L (5,000). The decision, the layers with their two diagrams, three excerpts
and the players' options with the rules of how their choices combine take the most words; each effect's row stays on
its own page. Phase B must read again the rows that wave 8 adds and changes
(reflections modes, probe resolution, global illumination, the section's version) and the presets table, which this
W8r page's named section holds, and the entry of "What Strata does not do" that the page states, rendering below native
resolution (`new:11`), a claim checked again at the pin move (rule 6).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `render-image:384` | concept | home | Quality presets as a product concept: look against cost, rows, presets, Custom, players' overrides, memory estimates; never below native as a policy with trade-offs; the errors (look controls in a row, players turning on an effect a scene never authored; the `AntiAliasing` row is a preference, not an effect, and may turn anti-aliasing on) |
| `render-image:227-260` | feature | home | `RendererQualitySettings` and its enums; Medium is 0.6.0's costs and the specification's default, so tests, tools and perf scenes keep their cost and a new row's default is Medium's value, and High is the section's default (`Strata/src/Strata/Renderer/RendererQuality.h:26-27`; `AGENTS.md:397`; `Docs/DeveloperGuide.md:4040-4045`); the preset table, `GetPreset`, `Clamp`, `ResolveShadowMapSize`; the `Renderer.Quality` section; the row traits and memory estimators; the players' rows: the four comfort rows (`MotionBlur`, `DepthOfField`, `FilmGrain`, `ChromaticAberration`, `SceneEffectChoice`) only turn off, and the `AntiAliasing` row (`AntiAliasingChoice`) is a preference that may turn anti-aliasing on and choose its method (`SceneRendererPost.cpp:458-486`); `SetQuality`; who follows what; `IGameGraphics` (`Strata/src/Strata/Core/EngineServices.h:152-184`), `GameGraphicsService` and the options file, and how a player's choices combine (a row that follows the preset switches the player to Custom from the look in effect; a preset keeps only the preset and the rows that do not follow it; each option's source; reset; names, never numbers; a bad file ignored with one warning and never rewritten by a load: `EngineServices.h:139-183`, `StrataScriptCore/Include/StrataScript/ScriptABI.h:705-725`, `Docs/DeveloperGuide.md:4123-4152`); the script SDK and its host functions; the editor's page, chip and commands; `--quality` and its log line; no render scale |
| `render-image:424` | code | home | `Strata/src/Strata/Renderer/RendererQuality.cpp:32-55`: the presets as a row per knob; with 156-179, the row traits; with `SceneRendererPost.cpp:458-486`, the players' overrides applied to the frame's copy |
| `render-image:565`, `render-image:567` | rule | home | Quality rows never change a scene's look, said precisely: a row never changes a look control (exposure, curve, grade) and never adds an effect, but scales or drops the cost of what a scene asks for (presets drop a scene's reflections or motion blur, or give global illumination to scenes that ask for it: `RendererQuality.cpp:52-54`, `SceneRendererPost.cpp:480`); the four comfort rows only turn off, and the `AntiAliasing` row is a preference that may turn anti-aliasing on and choose its method; adding a quality row, every place it touches |
| `render-image:572` | rule | home | Only `GameGraphicsService` touches `GraphicsOptions.json`: written atomically, read at most 64 KiB, validated |
| `render-image:475`, `render-image:477` | figure | home | Diagrams: the quality layers from the section's default to `--quality`; where quality is chosen in the editor |
| `render-image:515-519` | figure | home | The look-dev shot `pp.scene` at the four presets (the sweep): the Physics Playground asks for no screen-space reflections, global illumination or motion blur, so the caption names what changes from the generated table (shadows, ambient occlusion, levels of detail, the sky's prefiltered reflections) (`Samples/PhysicsPlayground/Assets/Scenes/Main.stscene:6`: `ScreenSpaceReflections` and `MotionBlur` false, no `GlobalIllumination`, whose default is false at `Strata/src/Strata/Renderer/RendererComponents.h:295`; `Tools/LookDev/Shots.json:19`); the editor's Graphics Quality page and quality chip (the Post Process inspector's TAA tunables are dropped here: `editor-ui:560` shows them, captured once, and `image/taa` uses it); the Third-Person sample's Graphics menu |
| `render-image:625` | hands-on | home | Exercise: add a quality row (a cap on the bloom's levels, or the depth of field's samples), with its traits, memory estimate, section version and feature-test value |
| `new:26` | hands-on | home | Exercise (trace it yourself): follow one `Graphics::Set` of a script from the SDK through the host function and `GameGraphicsService::SetOption` to the version that `GameRenderer::FollowQuality` compares and the call of `SceneRenderer::SetQuality`; the reader says on which frame the change shows and what a frame with no change costs. Evidence: `StrataScriptCore/Include/StrataScript/Graphics.h:180-188`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:3238-3300`; `Strata/src/Strata/Runtime/GameGraphicsService.cpp:502`; `Strata/src/Strata/Runtime/GameRenderer.cpp:57-78` |
| `render-image:728-732` | term | home | Quality preset, row and knob; Custom; row traits; players' rows; graphics options |
| `render-image:734` | term | home | Render scale, dynamic resolution and temporal upscaling |
| `new:29` | feature | home | How it is tested, beside the suites the inventory names: `GPU.SceneRenderer.Quality`, whose cases check that `SetQuality` makes again only what a changed knob sizes and that changing the quality and back draws the same image. Evidence: `StrataTests/src/Renderer/GPUSceneQualityTests.cpp:110, 197, 297` |
| `new:12` | erratum | home | The Developer Guide's table says that the five players' rows (`AntiAliasing`, `MotionBlur`, `DepthOfField`, `FilmGrain`, `ChromaticAberration`) only turn off what a scene uses. At the pin the four comfort rows only turn off (`SceneEffectChoice`), and the `AntiAliasing` row can also choose FXAA, TAA or Morphological, which turns anti-aliasing on for a scene that has it off, as the Manual says; the page states what the code does. Evidence: `Docs/DeveloperGuide.md:4031`; `Strata/src/Strata/Renderer/RendererQuality.h:55-70, 173-177`; `Strata/src/Strata/Renderer/SceneRendererPost.cpp:458-486`; `Docs/Manual/AntiAliasing.md:58-59` |
| `new:11` | not-done | home | Rendering below native resolution, dynamic resolution, temporal upscalers: left out by decision (the first design decision). Evidence: `Docs/Roadmap.md:1642-1643`; `Docs/Releases/0.7.0.md:408-409`, run again at the pin |
| `scripting:130` | feature | home | The SDK's `Graphics`, `GraphicsOption` and `QualityPreset` (`StrataScriptCore/Include/StrataScript/Graphics.h:18-107`): players' graphics options by name, presets, reset, save |
| `worlds-runtime:92` | feature | home | Graphics options from scripts: `Graphics::Options`, `Get`, `Set`, `SetPreset`, `Reset` and `Save` reach `IGameGraphics` |
| `worlds-runtime:135` | feature | home | `GameGraphicsService` as `IGameGraphics`: the project's quality, the player's `GraphicsOptions.json` and `--quality`; the value pulled when asked, an integer compare when nothing changed, no per-frame work (`Strata/src/Strata/Runtime/GameGraphicsService.h:43-46`); the rules by which a player's choices combine, as the service applies them: a row that follows the preset switches the player to Custom from the look in effect, a chosen preset keeps only the preset and the rows that do not follow it, each option's source, the resets, choices by name, and a bad options file ignored with one warning and never rewritten by a load (`Docs/DeveloperGuide.md:4123-4152`) |
| `worlds-runtime:380` | figure | home | The graphics option layering, the project's `Renderer.Quality` under the player's file under `--quality`: drawn as one diagram with `render-image:475`, with the versions `GameRenderer` pulls |
| `worlds-runtime:451` | rule | home | Only `GameGraphicsService` touches `GraphicsOptions.json`, in the runtime area's words: one owner of a player's file avoids conflicting writes and keeps validation in one place |
| `worlds-runtime:565` | term | home | Graphics preset |
| `render-image:574` | rule | use | The native-resolution half of the rule; its temporal half is taught by `image/taa` |
| `render-image:426` | code | use | The Manual's example of the SDK's `Graphics` (`Docs/Manual/Graphics.md:99-109`), one of the short snippets |
| `render-image:733` | term | use | Settings section; its home is `world/projects-settings` |
| `render-image:603` | hands-on | link | A Graphics options menu made by a game maker; `make/quality` |
| `editor-core:97` | feature | use | `graphics.resetPlayerOptions` |
| `editor-ui:229` | feature | link | The Graphics Quality page's drawing; `editor-ui/settings-windows` |
| `render-direct:189` | feature | link | `ShadowResolution`, a row taught on its feature's page |
| `render-scene:183` | feature | link | The render-scene area's quality rows, taught on their pages |
| `render-indirect:138`, `render-indirect:163` | feature | link | The reflections and global illumination rows, taught on their pages |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Projects and settings sections: versions, validation, `IProjectSettings` | `world/projects-settings` | must |
| Engine services and engine modules | `core/engine-modules` | must |
| Temporal anti-aliasing | `image/taa` | must |
| Files you can trust: atomic writes, private files | `core/files` | must |
| Sun shadows (rows of the table) | `light/sun-shadows-2` | helps |
| A script at the use level: a call into the SDK | `basics/programming-1` | helps |
| A script at the use level: a class | `basics/programming-3` | helps |
| The host API: engine services behind a C table | `scripting/host-api` | helps |
| Inactive reasons: a property that another property turns off (`SetInactiveReason`) | `world/reflection` | helps |
| Running an editor command from a line to paste | `start/how-to-read` | helps |
| The runtime: `GameRuntime` | `worlds/runtime` | helps |
| Readback and GPU timestamps and stages | `gpu/readback-timing` | helps |
| Reflection: properties with titles and descriptions | `world/reflection` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `custom-preset` | Custom (preset) | - |
| `graphics-options` | Graphics options | - |
| `graphics-preset` | Graphics preset | - |
| `players-rows` | Players' rows | - |
| `quality-preset` | Quality preset | - |
| `render-scale` | Render scale | dynamic resolution, temporal upscaling |
| `row-traits` | Row traits | - |
