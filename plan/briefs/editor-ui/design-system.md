# Brief: `editor-ui/design-system`

| Field | Value |
| --- | --- |
| Title | The design system: theme, fonts, icons |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `editor-ui/ui-scale`, `gpu/text` |
| From | editor-ui ch. 6 (Bedrock tokens, `ApplyTheme`, the font atlas and the icon merge, the CJK fallback, the `Icons.h` generator, the source scans); home of the editor's font loading (ImGui's own atlas, not `FontAtlasCache`) |
| Unit | `plan/allocation/editor-ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `editor-ui/design-system` — The design system: theme, fonts, icons

**Covers.** The editor's look as a system that many people and agents keep consistent. The problem and how engines
solve it: raw colors in code drift apart; a design system names its colors (tokens), gives them meanings (semantic
colors), fixes a type scale and an icon set, and enforces them by mechanism. The map: the Bedrock palette's 16 tokens →
`ThemeColors`, the meanings (accent, levels, axes, play states, text, surfaces) → `ApplyTheme`'s role table → every
`ImGuiCol_` (a diagram), with the axis colors that reappear in the gizmo and in vector fields. The contract: colors
only from tokens; text only through the editor's fonts, with icons as text; UTF-8 encoded once.

The real code: the role table with its `static_assert`, so an ImGui upgrade that adds a color slot fails the build, and
`ApplyTheme`; text rendering for tools: ImGui's own font atlas (not the engine's `FontAtlasCache`), Inter and JetBrains
Mono, Lucide merged into Unicode's Private Use Area with excluded ranges, an offset and a minimum advance (a diagram of
the atlas); the CJK fallback, read from system fonts on an I/O job and merged between frames, and the glyph generation
that invalidates measured widths; the trust boundary: the atlas reads only the compiled-in fonts and the system's
fallback fonts, never a project's font file, which is why it may skip the engine's font validation (`gpu/text`). Then
the type scale (12, 14, 17, 24) and `UI::PushFont`; `Icons.h`, generated from the font's code points by
`GenerateIconHeader.py`; entity and asset-type icons; the brand mark drawn as vectors, and the window's icon, the mark
at nine sizes so that no system stretches a smaller image; the fonts and the notices compiled into the editor, with the
fonts' licenses. The page states the entry of "What Strata does not do": editor themes other than Bedrock. Pictures:
ImGui's default style beside Bedrock, and a CJK project name. At the end the reader can add a theme meaning, use an
icon, and watch the source scan fail on a hex color.

**Leaves out.**

- How the engine shapes and draws game text, and its glyph atlas → `gpu/text`
- The UI scale the theme's sizes are multiplied by → `editor-ui/ui-scale`
- The widgets built on the tokens → `editor-ui/widget-kit`
- The source scans as tests → `editor-ui/ui-testing`
- Third-party licenses and notices in general → `engineering/third-party`
- How `strata_embed_file` and the committed generators work → `engineering/generated-code`

**Fit.** `fits`: about 5,300 words against L (5,000). Two concepts from zero, three excerpts, four figures and three
rules take the most; the window's icon, the trust boundary and the one theme take a few sentences each, and the scans
are only named here.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `editor-ui:50` | feature | home | The fonts and `ThirdPartyNotices.md` compiled in with `strata_embed_file`: the editor reads no font file |
| `editor-ui:60-69` | feature | home | The Bedrock palette, `ThemeColors`, `ApplyTheme`, the token list for tests, `EditorFonts` and the type scale, the CJK fallback, `Icons.h`, entity icons, asset-type icons and names, the brand mark |
| `editor-ui:334` | concept | home | A design system for tools: tokens against semantic colors, a type scale, an icon set, rules enforced by mechanism; "just this once" hex colors |
| `editor-ui:339` | concept | home | Text rendering for tools: merged fonts, icons in the Private Use Area, excluded ranges, fallback scripts loaded off the main thread, the fallback glyph; icons in the monospace font, UTF-8 encoded twice, fonts loaded in a frame |
| `editor-ui:439` | code | home | `StrataEditor/src/UI/Theme.cpp:92-171`: the role table of pointers to members and its `static_assert` over `ImGuiCol_COUNT`; with `ApplyTheme` at 253-270 |
| `editor-ui:440` | code | home | `StrataEditor/src/UI/EditorFonts.cpp:77-97`: a text font with the icon range excluded, and Lucide merged in with an offset and a minimum advance |
| `editor-ui:441` | code | home | `StrataEditor/src/UI/EditorFonts.cpp:131-197`: the fallback fonts read once on an I/O job and merged between frames behind the editor's glyphs; the glyph generation |
| `editor-ui:494` | figure | home | Tokens → meanings → `ImGuiCol_` roles, and where the axis colors reappear |
| `editor-ui:496` | figure | home | The font atlas: Inter with Lucide and the CJK fallback, SemiBold the same, the monospace font without icons |
| `editor-ui:546` | figure | home | ImGui's default dark style (Help ▸ ImGui Demo with `--imgui-demo`) beside Bedrock |
| `editor-ui:582` | figure | home | A CJK project name drawn through the fallback fonts |
| `editor-ui:588` | rule | home | Colors only from theme tokens, enforced by the `static_assert` and the source scan |
| `editor-ui:596` | rule | home | Text through the editor's fonts, never ImGui's built-in font; icons are text, so swatches are drawn as rectangles |
| `editor-ui:598` | rule | home | UTF-8 encoded once (a "·" pasted through a Latin-1 tool turns into "Â·") |
| `editor-ui:668` | hands-on | home | Add a theme meaning and use it; then put a hex color in a panel and watch `Editor.UI.Source` fail |
| `editor-ui:717-720` | term | home | Fallback glyph (the word glyph is `gpu/text`'s, `render-core:762`, and the page links it); Private Use Area; merge mode; icon font |
| `editor-ui:727-729` | term | home | Theme and Bedrock; token, palette and semantic color; type scale |
| `editor-ui:793-794` | term | home | Inter, JetBrains Mono and Lucide; CJK |
| `new:5` | feature | home | The editor's fonts and their licenses: Inter 4.1 and JetBrains Mono 2.304 under the SIL Open Font License 1.1, Lucide 1.47.0 under ISC (icons from Feather also MIT), committed in `StrataEditor/Resources/Fonts` and compiled in. Evidence: `ThirdPartyNotices.md:34-38`; `StrataEditor/CMakeLists.txt:58-62` |
| `new:30` | not-done | home | Editor themes other than Bedrock: the editor has one palette, installed by one style callback, and no preference chooses a theme; the Roadmap leaves theme variants for later. Evidence: `StrataEditor/src/UI/Theme.h:10`, `:86-92` (the one palette and `ApplyTheme`); `StrataEditor/src/Editor/EditorPreferences.cpp:69-74` (three preference sections: the external editor, the interface and the frame rate); `Docs/Roadmap.md:985-993` ("rebinding editor shortcuts and theme variants", left for later); `grep -rn "Editor.Theme" StrataEditor/src` finds nothing |
| `new:31` | feature | home | The editor window's icon: the strata mark as raw RGBA8 images at nine sizes from 16 to 64 pixels, the small and large icons of Windows at 100 to 200% display scaling, so the system never stretches a smaller image, and a 256-pixel PNG for macOS's Dock, decoded at start; embedded by the editor's build and drawn by `Tools/GenerateBrandAssets.py` (critic-editor-ui-9, about 60 words, with the brand mark). Evidence: `StrataEditor/src/EditorIcon.h:14-26`, `:33-37`; `StrataEditor/src/EditorApplication.cpp:47-60`; `Tools/GenerateBrandAssets.py:1-21` |
| `new:32` | rule | home | The editor's ImGui atlas reads only the fonts compiled into the editor and the system's fallback fonts, never a project's font file: that is why ImGui's own rasterizer may read them without `FontValidation`, which guards the engine's text; the page links `gpu/text`'s validation (critic-editor-ui-10, about 50 words, in the text-rendering section). Evidence: `StrataEditor/src/UI/EditorFonts.cpp:69-75` (the only `AddFontFromMemoryTTF` call in `StrataEditor/src`), `:131-152` (the fallback read from `Platform::FindFallbackFontFiles`); `AGENTS.md:412`; `Docs/DeveloperGuide.md:6204` |
| `new:33` | hands-on | home | Trace it yourself (D27): a search for `ImGuiCol_Button` in `Theme.cpp` leads to its row of the role table and the palette token it reads; a breakpoint in `ApplyTheme` then shows the colors written from the tokens, and the call made again by `ImGuiLayer::ApplyStyle` when the UI scale changes. Evidence: `StrataEditor/src/UI/Theme.cpp:92-171` (the role table; `ImGuiCol_Button` at 124), `:253-257`; `Strata/src/Strata/ImGui/ImGuiLayer.cpp:217-232` |
| `editor-ui:38` | feature | use | The style callback through which `ApplyTheme` receives the style and the scale |
| `editor-ui:716` | term | use | Font atlas, as `gpu/text` defines it; the editor's atlas is ImGui's own |
| `editor-ui:258` | feature | link | The source scans that enforce the rules (`editor-ui/ui-testing`) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Text: fonts, glyphs, the glyph atlas and font validation | `gpu/text` | must |
| Color values, sRGB and alpha | `basics/color` | must |
| Unicode code points and UTF-8 | `basics/bytes` | must |
| Jobs on I/O threads and results taken on the main thread | `core/jobs` | must |
| The UI scale and the style callback | `editor-ui/ui-scale` | must |
| `constexpr` | `basics/cpp-modern` | helps |
| `static_assert` (the role table's check over `ImGuiCol_COUNT`) | `basics/cpp-generic` | helps |
| Embedded files and committed generators | `engineering/generated-code` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `cjk` | CJK | - |
| `fallback-glyph` | fallback glyph | - |
| `icon-font` | Icon font | - |
| `merge-mode` | Merge mode | - |
| `private-use-area` | Private Use Area | PUA |
| `theme` | Theme | Bedrock |
| `token` | Token | semantic color |
| `type-scale` | Type scale | - |
