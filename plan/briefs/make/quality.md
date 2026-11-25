# Brief: `make/quality`

| Field | Value |
| --- | --- |
| Title | Graphics quality and options for players |
| Kind | H |
| Size | M |
| Tracks | G |
| Needs | `make/look`, `make/menus` |
| From | gamedev "The camera's image and graphics quality" (the quality half); Manual/AntiAliasing, Manual/Graphics (presets, costs, the quality chip, `--quality`, players' options, why there is no render scale); scripting "The gameplay API, part 3": `Graphics`, `GraphicsOption`, `QualityPreset`; it adds the Graphics row to the settings screen of `make/menus`; use home of players' graphics options · W8r (the presets table) |
| Unit | `plan/allocation/make-b2.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `make/quality` — Graphics quality and options for players

**Covers.** The goal: choose how the game smooths its edges and how much the renderer spends, and let players choose
too. What must be true first: the settings screen of `make/menus` (its end checkpoint). The steps, in order.
Anti-aliasing on the Post Process: FXAA, Morphological or TAA, and TAA's presets Sharp, Original and Custom; which suits
which look (thin detail and moving cameras: TAA; flat colors and pixel art such as Tetris: FXAA or Morphological,
because TAA softens them), with the comparison on a thin-detail scene. **Project Settings ▸ Graphics Quality**: the
presets Low, Medium, High (the default) and Ultra side by side, a row per setting with its memory and GPU time, and
Custom; a preset changes what the renderer spends, never what a scene stores (its lights, its Post Process, its sky).
The presets table is the W8r section: its values come from generated tables. The Scene view's quality chip for one view,
and that the Game view draws as the game will. `--quality low` for one run of the exported game. Then the players' side:
a Graphics row added to the settings screen, a toggle group of the four presets that acts only on the toggle switched on
and calls `Graphics::SetPreset` and `Graphics::Save` (the Third-Person sample's code, quoted), an anti-aliasing choice
with `Graphics::Set("AntiAliasing", ...)`, and `Graphics::GetPreset` to show the choice in effect; where the choice is
kept (`GraphicsOptions.json` beside the game's saves, in the editor the project's `.strata/Saves`), that a player's
saved preset hides the project's while you play in the editor, and **Reset Player Options** on the Graphics Quality
page. Why there is no render scale, the design decision named again in two sentences with a link to
`image/quality-settings`. What Strata does not do here: no command sets a player's options; no MSAA and no supersampling
(a render scale above 1); no HDR display output (the swap chain is sRGB only). Result: a settings screen whose Graphics
row works in the exported game. Variations: a Custom preset one row at a time; `Graphics::Options()` for a full options
screen. The exercise: the anti-aliasing shoot-out on the Physics Playground's floor.

**Leaves out.**

- How FXAA and morphological AA work → `image/spatial-aa`
- How TAA works, and its tunables → `image/taa`
- How presets, traits and the players' file are built → `image/quality-settings`
- The quality rows of each post effect → `make/look`
- Building the settings screen, toggles and toggle groups → `make/menus`
- Measuring what the presets cost in a game → `make/performance`

**Fit.** `fits`: about 3,700 words against M (3,000): eleven steps, one excerpt, two figures, the idea of the
anti-aliasing kinds and of presets as cost knobs, and the exercise take the most; the TAA tunables stay on `image/taa`.
W8r: phase B revises the presets table, with the rows 0.8.0 changes (shadows of lamps, global illumination, reflections)
and their costs, and checks the page's three not-done entries again (MSAA and supersampling; HDR display output; setting
a player's graphics options by command).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gamedev:116` | feature | home | Anti-aliasing: FXAA, TAA (Sharp, Original, Custom), Morphological |
| `gamedev:117` | feature | home | Graphics Quality: the project page with Low, Medium, High, Ultra and Custom, the cost per row, players' choices, the Scene view's quality chip, `--quality` |
| `gamedev:205` | feature | home | Graphics options for players: `Graphics::SetPreset`, `Set`, `Get`, `Reset`, `Save`, `Options`, `FindOption`; `GraphicsOptions.json`; resetting them |
| `gamedev:314` | concept | home | The camera's image and quality: anti-aliasing kinds, presets as cost knobs, no render scale; the mistakes (a render-scale slider looked for, TAA on pixel art) |
| `gamedev:380` | code | home | `Samples/ThirdPerson/Scripts/SettingsMenu.cpp:26-39`: the Graphics row as one toggle group, the events of switched-off toggles ignored, `Graphics::SetPreset` and `Graphics::Save` |
| `gamedev:465` | figure | home | TAA against FXAA on a thin-detail scene; TAA softening a Tetris-like flat image |
| `gamedev:466` | figure | home | Graphics Quality Low against High on the Showcase's second shot |
| `gamedev:518` | rule | home | No render scale, ever: presets lower costs, not resolution |
| `gamedev:601` | term | home | Anti-aliasing (FXAA, TAA, Morphological) |
| `gamedev:602` | term | home | Graphics Quality preset |
| `render-image:603` | hands-on | home | A Graphics options menu: preset toggles and an anti-aliasing chooser, `GraphicsOptions.json` checked, the runtime restarted, reset |
| `new:1` | not-done | home | Setting a player's graphics options by command: the only graphics command deletes them. Evidence: `StrataEditor/src/Editor/EditorGraphicsCommands.cpp:16`, `graphics.resetPlayerOptions`, the file's only command; `git grep -n "\"graphics\." 822a7a46 -- StrataEditor/src` finds only it, registered there and run by the page's **Reset Player Options** (`StrataEditor/src/UI/GraphicsQualityPage.cpp:350`) |
| `new:17` | not-done | home | MSAA and supersampling (a render scale above 1): no multisampled targets and no render scale above 1; edges are smoothed by FXAA, Morphological or TAA. Evidence: `Strata/src/Strata/Renderer/SceneRenderer.cpp:2767` refuses targets whose sample count is not 1; `Docs/Roadmap.md:944, 1670, 1672`; `Docs/Releases/0.7.0.md:409, 411` |
| `new:18` | not-done | home | HDR display output (HDR10, scRGB): the swap chain is sRGB only, so the game's picture is an SDR picture on every display. Evidence: `Strata/src/Platform/Vulkan/VulkanGraphicsDevice.cpp:1131-1136` (an 8-bit UNORM back buffer in the sRGB nonlinear color space) |
| `render-image:194`, `render-image:196`, `render-image:198`, `render-image:203`, `render-image:214` | feature | use | The Post Process's anti-aliasing and its methods; TAA's presets |
| `render-image:227`, `render-image:232`, `render-image:243` | feature | use | The quality settings, the presets table, who follows which quality (project, Scene view chip, Game view, `--quality`) |
| `render-image:246`, `render-image:250`, `render-image:254`, `render-image:258`, `render-image:260` | feature | use | The players' options file, the SDK's `Graphics`, the Graphics Quality page and its reset, the runtime's `--quality`, no render scale |
| `scripting:130` | feature | use | `Graphics`, `GraphicsOption`, `QualityPreset` in the SDK (home `image/quality-settings`) |
| `worlds-runtime:92`, `worlds-runtime:135` | feature | use | Graphics options from scripts; the service that owns the file |
| `editor-ui:229` | feature | use | The Graphics Quality page: preset chips, the table, the Custom column, the players' banner and reset |
| `render-image:362`, `render-image:364`, `render-image:371`, `render-image:384` | concept | use | Aliasing, spatial AA, TAA and presets as a product concept, at a maker's level |
| `render-image:506`, `render-image:509`, `render-image:515`, `render-image:517`, `render-image:519` | figure | use | AA crops, TAA's presets in a pan, the presets of one shot, the Graphics Quality page, the Third-Person settings menu |
| `worlds-runtime:380` | figure | use | The layers of the choice: the project, the player's file, `--quality` |
| `render-image:597` | hands-on | use | The page's exercise, done in the editor: the anti-aliasing shoot-out on the Physics Playground's floor |
| `render-image:565`, `render-image:572`, `render-image:574` | rule | use | Quality rows never change a scene's look; only the graphics service touches the players' file; never below native resolution |
| `gamedev:520` | rule | use | In a toggle group act only on value 1 (home `make/menus`) |
| `render-image:693-694`, `render-image:698`, `render-image:728-729` | term | link | FXAA, morphological AA, TAA, quality preset and row, Custom |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| The settings screen, toggles and toggle groups, `OnUIValueChanged` | `make/menus` | must |
| The Post Process component | `make/lighting` | must |
| The post effects and their players' rows | `make/look` | must |
| Exporting the game and running it from a terminal with an option | `make/export` | must |
| `std::optional` in a script | `basics/programming-3` | helps |
| Where a game keeps its save files | `make/levels-saves` | helps |

**Starting state.** The end checkpoint of `make/menus`, downloadable: its project with the settings screen (volume,
window mode, vsync) built and working in play.

**Command-only steps.** none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `anti-aliasing` | Anti-aliasing | - |
| `graphics-quality-preset` | Graphics Quality preset | - |
