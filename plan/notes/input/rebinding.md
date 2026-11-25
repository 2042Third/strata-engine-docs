# Notes: input/rebinding

## New terms

- session: one run of the game, a play session in the editor or one start of an exported game; home input/rebinding; no aliases.

## Requests

- No new names or extra words. No figures file: both pictures are Mermaid diagrams.

## Not verified

- That the Third-Person sample names its action map Gameplay (the page's example uses Gameplay/Jump as the engine's own header comment does).
- That the editor's Input Actions page is what calls ReadSavedBindings (only EditorContext was seen calling it).
- The script SDK name of the reset (inputActions.resetPlayerBindings was not found at the pin by that spelling; the page omits it).
- The doctest filter "*capture*" was not run.
- Links to input/devices-state-free pages: ../worlds/game-identity.md, ../basics/data-formats.md, ../basics/programming-3.md, ../basics/cpp-modern.md were not checked to exist.

## Findings not applied

- The brief lists no open findings.
- Not on the page for size: the capture's timeout in the editor owner and the "In play" screenshot (figure request, home editor-ui/settings-windows).

## Since

- 0.6.0: Docs/Releases/0.6.0.md line 98 names players' bindings and capture.

## Left failing

- term-defined: the page is the home of "Players' bindings" and defines it in bold, but the lint reports it never uses it, so its matcher seems not to read the plural possessive "players'" (straight or curly apostrophe, and "Players bindings", all tried).

## Clerk

- Refused the term session: a common word (tools/data/common-words.txt) in its everyday sense; the bold may stay.
- Fixed the tool defect behind its term-defined finding: "Players' bindings" now matches the page's words (tools/lint.py).
