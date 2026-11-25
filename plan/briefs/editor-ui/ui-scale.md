# Brief: `editor-ui/ui-scale`

| Field | Value |
| --- | --- |
| Title | Pixels, points and UI scale |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `editor-ui/imgui-backends` |
| From | editor-ui ch. 5 (content scale, `ToUIScale`, even base sizes, fonts' DPI, Preferences > Interface, `--ui-scale`) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/ui-scale` — Pixels, points and UI scale

**Covers.** How the editor's UI keeps its size on every display. The problem and how engines solve it: displays differ
in density; the system reports a content scale; macOS and Wayland measure windows in points with a framebuffer twice as
large, Windows and X11 in pixels; one approach scales at draw time, another lays out in points and rasterizes fonts for
the framebuffer. Strata lays out in window units and scales the style. The map is a diagram: the content scale event →
`ImGuiLayer::ToUIScale`, which divides out the points factor → times the person's factor (Preferences ▸ Interface,
through `EditorHost`) or replaced by `--ui-scale` → clamped to [0.5, 4] → `ApplyStyle`, which builds the style from
ImGui's unscaled defaults, lets the style callback (the theme) scale it, and sets `FontScaleDpi`. In play the game gets
the display's UI scale (the override, or the content scale less the points factor) without the person's factor, which
sizes the editor and not the game. The content scale is `core/windows-events`' word: the page says it in one sentence
and links it.

The real code: `ToUIScale`, the factor and the clamp, and `ApplyStyle`; the theme's even base sizes, so that 150% and
200% give whole pixels; the platform backend's display size and framebuffer scale, set each frame. The rules: sizes are
multiples of the font size, and the style is built from unscaled defaults every time, because scaling a scaled style
compounds. A picture shows the same layout at 100% and at 200%. At the end the reader can predict the UI scale on a
given display and keep a new widget crisp at any scale.

**Leaves out.**

- The theme's colors, the type scale and the fonts → `editor-ui/design-system`
- The Preferences dialog and its Interface page → `editor-ui/settings-windows`
- Every command-line option of the editor → `reference/editor`
- Sizes and scale in game UI (the canvas scale) → `ui/layout`

**Fit.** `over`: about 4,300 words against M (3,000). One concept, three excerpts, two figures, two rules and the three
exercises (`new:29`) do not fit M. Propose L (5,000) by S2.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:37-38` | feature | home | The UI scale (content scale less the points factor, times the person's factor or the override, clamped to [0.5, 4], fonts by `FontScaleDpi`) and the style callback that receives ImGui's dark style unscaled |
| `editor-ui:326` | concept | home | Pixels, points and the UI scale: densities, content scale, points against pixels, the two approaches, Strata's, the rule of font-relative sizes, scaling twice and fixed widths as pitfalls |
| `editor-ui:431` | code | home | `Strata/src/Strata/ImGui/ImGuiLayer.cpp:169-232`: `ToUIScale` (169-177), the override, the factor and the clamp, and `ApplyStyle` from unscaled defaults (217-232) |
| `new:3` | code | home | `StrataEditor/src/UI/Theme.cpp:173-234`: the base sizes, all even or zero, so `ScaleAllSizes` gives whole pixels at 150% and 200%; hairlines of one pixel |
| `new:4` | code | home | `Strata/src/Strata/ImGui/ImGuiPlatform.cpp:186-204`: the display size and the framebuffer scale (pixels per window unit) set each frame, and delta time with its first-frame and minimum steps |
| `new:28` | feature | home | In play the editor gives the game the display's UI scale: the `--ui-scale` override, or the content scale less the points factor, never the person's interface factor, which sizes the editor and not the game; a game's canvases in the Game view keep the size a player's display gives them (critic-editor-ui-2, about 80 words, after the factor). Evidence: `StrataEditor/src/EditorLayer.cpp:636-638`; `Strata/src/Strata/ImGui/ImGuiLayer.h:68-71`; `StrataEditor/src/EditorHost.h:50-52`; `StrataEditor/src/Editor/EditorGameWindow.h:37-39` |
| `editor-ui:492` | figure | home | The UI scale computation from content scale to `ScaleAllSizes` and `FontScaleDpi` |
| `editor-ui:545` | figure | home | The default layout at `--ui-scale 2` beside 100% |
| `editor-ui:592` | rule | home | Sizes relative to the font, no fixed pixels above 16 |
| `editor-ui:631` | rule | home | Build the style from unscaled defaults every time |
| `editor-ui:722-725` | term | home | Points and pixels; UI scale; `FontScaleDpi` |
| `new:29` | hands-on | home | Exercises (D27): the UI scale predicted for three displays, Windows at a content scale of 1.5 with Interface at 125%, a Retina Mac at 2 with 100%, and any display with `--ui-scale 5` (Basic, predict); a breakpoint in `ImGuiLayer::ToUIScale` while the window moves to a display of another density, its window and framebuffer sizes read (Medium, trace); a scratch widget with a width of 200 fixed pixels in a panel made relative to the font and run at `--ui-scale 1` and `2`, then put back to watch the scan "Sizes scale with the font" fail (Hard, done: a patch). Evidence: `Strata/src/Strata/ImGui/ImGuiLayer.cpp:169-177`; `Strata/src/Strata/ImGui/ImGuiLayer.h:78-79` (the clamp to [0.5, 4]); `StrataTests/src/Editor/EditorUISourceTests.cpp:516-529` |
| `editor-ui:721` | term | use | Content scale and DPI, homed on `core/windows-events` with `gameui:624` (R31, D33): the page says the word in one sentence and links it |
| `editor-ui:54` | feature | use | `--ui-scale` among the options that matter to the UI |
| `editor-ui:62` | feature | use | `ApplyTheme` as the style callback, whose colors are `editor-ui/design-system`'s |
| `editor-ui:232` | feature | link | Preferences ▸ Interface sets the factor (`editor-ui/settings-windows`) |
| `editor-ui:258` | feature | link | The source scan "Sizes scale with the font" (`editor-ui/ui-testing`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Window size, framebuffer size and the content scale event | `core/windows-events` | must |
| ImGui's style and its push and pop | `editor-ui/imgui` | must |
| The ImGui layer, its style callback and the platform backend | `editor-ui/imgui-backends` | must |
| User settings sections (preferences) | `world/projects-settings` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `fontscaledpi` | FontScaleDpi | - |
| `pixels` | pixels | - |
| `points` | Points | - |
| `ui-scale` | UI scale | - |
