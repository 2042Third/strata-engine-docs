# Rulings 12: one pin, and the order of the book's last steps

Written when the book resumed (2026-11-18), with 221 of 335 pages written and the engine's release 0.8.0 not yet
made. Where this file differs from an earlier file, this file wins.

## R55 — The final pin is the release 0.8.0, and the additions are in it

pipelines.md §11 has the engine's capture additions land after 0.8.0 and ship as v0.8.1, with a second pin move. The
release 0.8.0 has not been made, so the additions go into it: tier 1, tier 2 with its extension, and the two fixes
asked with tier 1 (a failure exit code after an exception leaves the frame loop; debug information in script modules
built with GCC or Clang). Wherever the plan writes "v0.8.1" for the final pin, the additions or those two fixes, read
0.8.0. The book moves its pin once, from `822a7a46` to the commit of the tag `v0.8.0`.

`tools/figures.py` recognizes the additions from the dumps of the pin, as before: a figure's `waitsFor` is dropped
when the pin has what it waits for. A tier 3 request that the release does not meet stays a diagram or a text
description on its page, and its `waitsFor` stays.

## R56 — The order of the last steps

1. The remaining pages that do not wait for wave 8 are written at `822a7a46` as the others were: the rest of wave 5,
   wave 6, then `reference` and `appendix` (they were set for phase B only because they follow the others; a kind R
   page's tables are rendered from the dumps and are rendered again after the pin moves).
2. When the engine has released 0.8.0: the pin build and the dumps at the tag; `pin.py report`, then `pin.py move`;
   `excerpts.py relocate` and `check`, `names.py check` and the lint over every page; a reviser for each page that
   these flag and for each W8r section; the seven W8 pages are written.
3. The pictures, at the final pin: the scene, runtime, text and tool figures are taken by `figures.py take` and each
   is judged against what its recipe says it shows; the editor figures follow with their layouts; a figure that a
   drawing serves is drawn. The rendering features come first.
4. The whole book through its checks and the site's build; the merge into `main`; the first push as `ci/site`, and
   `main` when its CI is green.

## R57 — Two captures within a level are one picture; a text's timings are taken once

In the first batch of pictures six figures passed the photographer's eye and were refused because their two captures
differed by one level in a few pixels, or because a text figure's timings differed at every call. Two captures of one
recipe count as the same picture when every channel of every pixel differs by at most 1 level and at most 0.5 per cent
of the pixels differ at all: output dither and the last bit of a filter are not a fault of the recipe. The first
capture is kept and its stamp records the measured difference (`pairDifference`: pixels, per cent, largest level).
Anything larger stays "nondeterministic" and fails the figure, as before.

A text figure of timings cannot repeat. Its recipe names the values that are measurements in `text.measured`: JSON
pointers inside `keep` for a command's answer, regular expressions for a program's output (beside `redact`, which
replaces what it matches). The two runs are compared without them, the values are published as the first run gave
them, and the caption says they are one run's measurements; `tools/figures.py check` refuses a caption without "one
run". pipelines.md §5.6 and `plan/card/photo.md` state both rules.
