# Notes: ui/text

## New terms

None proposed: caret, ellipsis, placeholder and selection anchor are defined in bold on the page.

## Requests

- Further reading cites the Unicode Standard and Gregory, "Game Engine Architecture", without links; no host was added.

## Figures

- `text-overflow` and `field-states` were `runtime` recipes waiting for tier 3. Both are now `scene` recipes on a copy of the basic 3D template: `setup` builds a canvas with `ui.create` and `component.set`, and the editor's capture draws it. Taken at the final pin 319075e3 and published.
- `text-overflow`: a dark backdrop, three boxes with a wrapped text aligned Left, Center and Right, three boxes with one long text in Overflow, Truncate and Ellipsis, and white text over the PhysicsPlayground bricks picture (imported) without and with an outline of width 0.08. Round 1 was judged good.
- `field-states`: three fields from the input field preset (empty, holding a short name, and edited). The canvas's First Selected is the third field, so one Down press focuses it. Round 1 selected with Shift and Left after the focus; paused steps draw no frame, so the first scroll was computed only at the capture and kept the caret, not the text's end, at the right edge. Round 2 presses Left five times, then Shift and Right five times: the last word is selected, the caret ends the text at the right edge, and the start is cut at the left. Two edited states cannot show at once, because only the focused field is edited: the caption names one edited field.

## Since

0.4.0: Docs/Releases/0.4.0.md lists text and input fields among the game UI's first features, and `UIInputFieldComponent` is in `Strata/src/Strata/GameUI/GameUIComponents.h` at v0.4.0 (checked).

## Not verified

- Further reading entries come from general knowledge, not from the pin.
- Mermaid diagrams are not rendered.

## Findings not applied

- The brief's L fit note was overridden by the task: the page is size M (3,942 prose words).
- Brief rows gameui:372 and new:21 asked for the "word-wise caret" exercise as an extend patch: done as a standalone sketch (`sketches/ui-text-words.cpp`) because patches need core/first-change.
- The `GameUI.Text` suite's tests for `GameUIComponentTests.cpp` appear in one sentence only.
- `UISelectable` rule (new:20) and the mask rule appear in the contract, not as separate `:::rule` blocks; the one rule block states the asset rule of AGENTS.md.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
