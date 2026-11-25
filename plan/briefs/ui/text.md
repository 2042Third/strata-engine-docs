# Brief: `ui/text`

| Field | Value |
| --- | --- |
| Title | Text and text fields |
| Kind | I |
| Size | M |
| Tracks | E |
| Needs | `ui/layout`, `ui/input`, `gpu/text`, `input/devices-state` |
| From | gameui ch. 6 (how rects, sizes and overflow modes drive `ShapeText`) and input-field editing (concept 20, §1.9's input-field row, `GameUISystem.cpp` 557-747, code #18); glyph rendering is `gpu/text` |
| Unit | `plan/allocation/ui.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `ui/text` — Text and text fields

**Covers.** The job: give every `UIText` its shaped lines from its rect, and let a player type one line into a field.
Fonts, shaping and the glyph atlas are `gpu/text`'s; drawing the glyphs, the caret and the selection is
`ui/drawing`'s. The problem section is one paragraph that links `gpu/text`: layout needs only a font's metrics, never
its pixels. The map shows `GameUIText.cpp` beside `Renderer/TextLayout.h` and the editing code of `GameUISystem`. The
contract: layout never rasterizes a glyph (it runs headless, in commands and tests), and a field's text element is a
`UIText` that a mask clips. A toy of about 40 lines keeps a one-line field: insert at the caret, delete one character
backwards by its UTF-8 bytes, scroll to keep the caret in view.

The real code comes in two halves. First a text in its rect, on the Third-Person menu's titles and labels: how the rect
sets the shaping options in `GetMeasureOptions` and `GetShapeOptions` (wrap at the rect's width in em, a maximum width
and a box height for Truncate and Ellipsis, a fitted rect measured unwrapped), the default font while the text's font
loads and the reshape when it arrives, and the shape cache per element and layout, so a text is shaped once for
measuring and drawing. Then the field, on the GPU test's field scene: one line, never wrapped or cut; a field needs a
`UISelectable` on its entity, since editing starts when the focused selectable holds the field (the preset adds it and
the mask); `PlaceFieldLine` scrolls it so the caret stays inside; the caret stops; the editing state (caret, anchor,
blink). Editing: the field takes the keyboard while it is edited (keyboard capture), so the UI map's keyboard bindings
go quiet (Space types a space and submits nothing, the field reads its own keys) while a gamepad still edits (its
Submit submits, its Cancel ends editing, its Left and Right move the caret); typed text goes in at the
caret within the character limit counted in code points, control characters are dropped, Backspace, Delete, the arrows,
Home and End repeat like the UI actions, Shift selects, Ctrl+A or Cmd+A selects all, Enter submits, Escape ends editing
but keeps the capture to the end of the frame, the caret blinks every 0.53 s, and every caret move stops on a character
boundary. A click on the field puts the caret at the nearest character, also on a world-space canvas. The page then says
what Strata does not do: localization and right-to-left text, and showing the text an input method is composing. It ends
with the alternatives, the tests (`GameUI.Text`, the `GameUI.InputField` suite), changing it safely, and two exercises
(a typed character traced through the editing code, and word-wise caret moves added). At the end the reader can say how
a rect's size and overflow mode become shaping options, and follow one key press from `Input` to a changed field.

**Leaves out.**

- Fonts, shaping, glyph atlases and signed distance fields → `gpu/text`
- Glyph quads, the selection and caret quads, the glyph table → `ui/drawing`
- The focus model, Submit and navigation → `ui/input`
- Typed text and keyboard capture inside `Input` → `input/devices-state`
- Composed text in the editor's own text fields → `editor-ui/imgui-backends`
- A name field in a game's menu → `make/menus`

**Fit.** `over`: about 4,600 words against M (3,000). Four excerpts (the shaping options, `PlaceFieldLine`, the UTF-8
boundaries, the editing loop), the concept of text input, three figures, three rules, the UI map while a field is
edited, two absences and the internals sections pass M's top of 4,000; by S2 the page takes L, whose range holds the
estimate.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `gameui:58` | feature | home | `UITextComponent`: text, font, size in canvas units per em, color, alignments, wrap, overflow, line spacing, outline, raycast target off by default |
| `gameui:115-120` | feature | home | Shaping from metrics without rasterizing; the default font while a font loads, and the reshape; the shape cache; wrapping, maximum width, box height and overflow from the rect; a field's line, never wrapped, scrolled to the caret; caret stops |
| `new:4` | code | home | `Strata/src/Strata/GameUI/GameUIText.cpp:65-89`: `GetMeasureOptions` and `GetShapeOptions`, how the rect's size, wrap and overflow mode become the options of `ShapeText` |
| `gameui:64` | feature | home | `UIInputFieldComponent`: text, text element, placeholder, character limit in code points, caret and selection colors, event target |
| `gameui:90` | feature | home | The field's editing state in `GameUIScene` (caret, anchor, blink), and the caret found from a point |
| `gameui:411` | code | home | `Strata/src/Strata/GameUI/GameUIText.cpp:111-142`: `PlaceFieldLine`, a single line scrolled to keep the caret in view |
| `gameui:372` | concept | home | Text input: caret and selection anchor, byte offsets on character boundaries, typed text per frame without an input method, repeated edit keys, one scrolled line, the placeholder; the mistake of moving the caret by bytes |
| `gameui:191-192` | feature | home | Editing in `GameUISystem` (capture, typed text at the caret, limit, edit keys with repeat, Shift, Ctrl+A or Cmd+A, Enter, Escape, the 0.53 s blink, UTF-8 boundaries), and a click that puts the caret at the nearest character |
| `new:5` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:68-94`: `IsContinuationByte`, `PreviousBoundary` and `NextBoundary`, moving over UTF-8 one character at a time |
| `new:6` | code | home | `Strata/src/Strata/GameUI/GameUISystem.cpp:708-747`: typed text inserted at the caret within the character limit, the field written with `registry.patch`, the caret's blink, Enter and Escape |
| `new:19` | feature | home | The UI map while a field is edited: keyboard capture silences `Input::IsKeyDown`, which the input actions read, so the map's keyboard bindings go quiet (Space types a space and submits nothing; the field reads Enter, Escape, Left, Right, Home and End itself, and the keyboard's Up and Down do nothing), while a gamepad still edits: its Submit submits, its Cancel ends editing, its Left and Right move the caret, and its Up and Down navigate away. The page cites `UpdateNavigation`. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:509-551` (the comments at 516 and 548), `:589-592`, `:740-746`; `Strata/src/Strata/Input/InputActions.cpp:349`, `:390`; `Strata/src/Strata/Input/Input.h:101-104` |
| `gameui:237` | feature | home | The suite `GameUI.Text` (`GameUITextTests.cpp`); `GameUIComponentTests.cpp`'s suites, which round-trip every UI component, in one sentence |
| `gameui:472` | figure | home | The input field model: the text's bytes, caret and anchor, the selection quad, the caret quad, the scroll window over the line |
| `gameui:487` | figure | home | Text alignments, wrapping, Truncate against Ellipsis, an outline over a busy background |
| `gameui:493` | figure | home | An input field empty with its placeholder, while typing with a selection and the caret, and a long text scrolled (the scene of `GPUGameUITests.cpp`'s field test; no sample has an input field) |
| `gameui:522` | rule | home | Layout never rasterizes glyphs: it runs headless and must not depend on the atlas or its budget |
| `gameui:554` | rule | home | Keep the field's text element a `UIText` and give the field a `UIMask`: the text element draws text, caret and selection, and a scrolled line would spill |
| `new:20` | rule | home | Give the field a `UISelectable` on its own entity: only selectables take the focus, and editing starts when the focused selectable holds a `UIInputField`, so a field built by hand without one never takes the keyboard; the Input Field preset adds the selectable and the mask. Evidence: `Strata/src/Strata/GameUI/GameUIComponents.h:255`; `Strata/src/Strata/GameUI/GameUISystem.cpp:493-507`; `StrataEditor/src/Editor/GameUIPresets.cpp:179-200` |
| `new:21` | hands-on | home | Exercises (D27): Trace it yourself: breakpoints in `UpdateEditing` while "é" is typed into a playground field made with Hierarchy > + > UI > Input Field and Backspace is pressed show the two bytes inserted at the caret, `PreviousBoundary` stepping back over both, and the patch that signals the change; Hard, extend (done): word-wise caret moves on Ctrl+Left and Ctrl+Right that stop on character boundaries, with Shift selecting, and tests in the `GameUI.InputField` suite. Evidence: `Strata/src/Strata/GameUI/GameUISystem.cpp:630-747`, `:68-94`, `:613-628` (`MoveCaret` moves one character or to an end, never by words); `StrataTests/src/GameUI/GameUIInputTests.cpp:1132` |
| `gameui:648` | term | home | Ellipsis, truncate and overflow |
| `gameui:677`, `gameui:679` | term | home | Caret and selection anchor; placeholder |
| `new:7` | not-done | home | No localization and no right-to-left text. Evidence: `Docs/Releases/0.7.0.md:413-416` lists localization as not in the release; `Docs/Roadmap.md:1713` ("Localization with string tables and font fallback chains"); `git grep -niE "locali[sz]\|right-to-left\|\brtl\b\|bidi" 822a7a46 -- Strata/src` finds nothing |
| `new:8` | not-done | home | Game UI shows no text that an input method is still composing, and no candidate window; committed text arrives. Evidence: `Strata/src/Strata/Input/Input.h:148` (characters arrive with input methods applied); no "preedit" in `Strata/vendor/glfw/include/GLFW/glfw3.h`; the editor's fields take composed text, `Strata/src/Strata/ImGui/ImGuiPlatform.h:25-26` |
| `gameui:743` | open | home | Settled at the pin: games receive committed text; composition is not shown (`new:8`) |
| `gameui:303` | concept | use | Shaping against rasterizing, from `gpu/text`: the page uses that layout needs metrics only |
| `gameui:135` | feature | link | The glyph quads, and the selection quad behind them and the caret quad after them (`ui/drawing`) |
| `gameui:195` | feature | use | The typed text of the input frame and its 1,024-byte limit (its home is `input/devices-state`) |
| `gameui:236` | feature | use | The `GameUI.InputField` suite of `GameUIInputTests.cpp` (its home is `ui/input`) |
| `render-core:235` | feature | use | `ShapeText` and `MeasureCaretStops` of `Renderer/TextLayout.h` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Shaping: glyphs, advances, line breaks and the options of `ShapeText` | `gpu/text` | must |
| UTF-8, code points and multi-byte characters | `basics/bytes` | must |
| Typed text per input frame, and keyboard capture | `input/devices-state` | must |
| The rect, fit content and masks | `ui/layout` | must |
| Focus: the one widget that keys act on | `ui/what-game-ui-does` | must |
| Writing a component with `registry.patch` | `world/scene-graph` | must |
| The repeat timing of the UI actions | `input/actions` | helps |
| Font assets that load later, at a priority | `assets/residency` | helps |
| How Submit and focus changes become events | `ui/input` | helps |
| How the glyphs, caret and selection are drawn | `ui/drawing` | helps |
| Input methods in the editor's text fields | `editor-ui/imgui-backends` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `caret` | Caret | - |
| `ellipsis` | Ellipsis | truncate |
| `placeholder` | Placeholder | - |
| `selection-anchor` | selection anchor | - |
