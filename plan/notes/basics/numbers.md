# Notes: `basics/numbers`

## New terms

- **radical inverse**: a whole number's digits written backwards behind the point in a base, so that 3 in base 2 gives
  0.75. Home: `basics/numbers`. Aliases: none. (`image/taa` uses it.)
- **Morton order**: the order of numbers made by mixing the bits of two or three coordinates into one. Home:
  `basics/numbers`. Aliases: Z-order.
- **significand**: the digits of a floating-point number after its leading one. Home: `basics/numbers`. Aliases:
  mantissa.
- **subnormal number**: a float below the smallest one of the usual form, whose leading 1 is dropped. Home:
  `basics/numbers`. Aliases: subnormal, denormal.
- **half float**: a floating-point number of 16 bits (1 sign, 5 exponent, 10 significand bits). Home:
  `basics/numbers`. Aliases: half-precision float. (`basics/color` uses it.)
- **tolerance**: a small distance within which two numbers count as equal. Home: `basics/numbers`.
- **quantizing**: storing a number in fewer bits by rounding it to the nearest of fewer values. Home:
  `basics/numbers`. Aliases: quantize.
- **bit flags**: a number whose bits are separate yes-or-no settings. Home: `basics/numbers`. Aliases: flags.

The page also defines the glossary's entries of its brief in bold: binary, bit, power, exponent, hexadecimal, integer,
unsigned integer, two's complement, integer overflow, bitwise operator, bit mask, bit shift, floating-point number,
precision, rounding error, NaN, determinism, logarithm, exposure stop, decibel, exponential function, Euler's number.

## Requests

- `tools/data/extra-words.txt`: the units "KiB", "MiB" and "GiB" (sizes in powers of two, the brief's item `new:95`).
  Their word-list findings are left until then.
- `tools/data/names.txt`: "IEEE" (the standard 754 named in the float section; its expansion stands beside it).
  "Morton" is the name in "Morton order", proposed above.
- "significand" and "Morton": proposed under New terms; their word-list findings are left until the terms exist.
- Figures: two diagram requests in `src/content/figures/basics/numbers.json` (the bits of a float; the gaps between
  floats in three doublings). Neither is drawn yet.
- The `sketches` check fails in this worktree on other pages' files (`basics-build-*`, `basics-trees-graphs-breadth`,
  `basics-data-formats-glob`); the ten sketches of this page (`basics-numbers-*`) compile and pass.
- Word choices made to stay on the word list: "clock" for the brief's "timer"; "mixing" for "interleaving" (the brief's
  Morton item). If "timer" and "interleave" join the extra words, the page could use the brief's words.

## Not verified

- Coin Run's HUD: the page's Practice 6 says the HUD shows a clock and asks for the script that updates it to start at
  600,000 s and at 20,000 s. `make/hud` and `make/project-coin-run` are not written: the names of the script and its
  variable were not checked, so the exercise does not name them.
- That one unit of a Strata scene is one metre: the gap table says "if one unit is one metre".
- Whether Strata's audio mix is 32-bit floats everywhere: the page says only that `AudioEngine::ReadFrames` hands out
  `float` frames (`AudioEngine.h`) and that decompressed clips are 32-bit floats (`AudioClip.h`).
- That the half float's range is the reason for `c_MaxHDRValue`: the shader comment says "the format's maximum is 65504;
  anything above becomes Inf" and the constant is 65000 (`Strata/shaders/Include/Common.slang`).
- Morton order and `std::countr_zero` are taught as general knowledge: no Morton code exists at the pin. The
  `countr_zero` loop over the moved bodies is in `PhysicsWorld.cpp` (write-back of poses); the page only names the file.
- `std::numeric_limits` is named in one sentence; its use in Strata (72 lines in 41 files by the critic's count) was
  not recounted.

## Findings not applied

- critic-basics-a-7: applied. The Practice uses ten additions of 0.1f against 1.0f (false) and the double sum in the
  body, teaches nine and seventeen digits through a string, and says `Log` shows six; the gap exercise logs the
  difference.
- critic-basics-a-8: applied. Division is taught as truncation toward zero, `%` takes the sign of the left number,
  `FloorDivide` is quoted (`GlobalIlluminationLayout.cpp:17-21`), the round-up rule states its condition. The
  Practice's division case uses `-7 / 2`, `-7 % 2` and the floor, predicted then run. The one sentence for
  `basics/programming-1`'s `%` belongs to that page.
- critic-basics-a-12: not for this page (`basics/programming-3`).
- critic-basics-a-16: the part for this page is applied (`std::numeric_limits` beside the ranges); the rest belongs to
  `basics/cpp-modern` and `basics/cpp-generic`.
- critic-basics-a-20: not for this page (`basics/cpp-memory`); this page's round-up rule is the one it will use.
- critic-basics-a-22: applied as a common mistake (log `int(value)` or `+value`).
- critic-basics-a-25: applied in Practice 6 (start at 600,000 s to see the stall and at 20,000 s to see the drift, each
  predicted from the table of gaps first).
- The brief's Fit note asks for a split into `basics/numbers` and `basics/math-powers`; the page keeps the powers,
  logarithms and the exponential function (in about 800 words) because the planner's brief and Items assign them here.
  Practice items for logarithms and `exp` are in Check yourself, not Practice.
- Practice 1 and 3 have no sketch (their answers show the line of code in prose): the size limit left no words for the
  callouts of two more sketches. The brief's Practice also asks to log each value; the answers say so.

## Clerk

- Admitted: Morton order (alias Z-order), significand (alias mantissa), subnormal number (aliases subnormal, subnormals, denormal; also asked by `basics/color`, decided here).
- Refused: radical inverse (homed on `image/taa`), half float ("half-float" is homed on `basics/color`), tolerance (homed on `basics/math-geometry`), quantizing ("quantization" is homed on `basics/color`): only their homes word them; the planner may move them.
- `extra-words.txt`: "kib", "mib", "gib" (units), "timer". `names.txt`: "IEEE".
- Not admitted, because the page check would then fail and the page is the writer's: bit-flags (its paragraph would define 2 terms with bit mask, and its section 5 (term-paragraph, term-section)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.
- Marks made by the clerk so that the admitted terms are defined (no word changed): **significand** in its defining sentence, and **subnormal numbers** for **subnormal** numbers.
