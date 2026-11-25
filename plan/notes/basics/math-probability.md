# Notes: `basics/math-probability`

## New terms

- **exclusive** (cases): two cases that cannot both happen, so their probabilities add. Home: `basics/math-probability`.
  Aliases: mutually exclusive.
- **independent** (events): two events where one does not change the other, so their probabilities multiply. Home:
  `basics/math-probability`. Aliases: none.
- **uniform** (distribution): a distribution where every value, or every part of a range of the same size, is equally
  likely. Home: `basics/math-probability`. Aliases: uniform distribution.
- **mean**: the sum of samples divided by their count; a mean of many samples lies near the expected value. Home:
  `basics/math-probability`. Aliases: average.
- **variance**: the average of the squared distances of samples from their mean. Home: `basics/math-probability`.
  Aliases: none.
- **standard deviation**: the square root of the variance, in the units of the samples. Home:
  `basics/math-probability`. Aliases: spread.
- **stratified sampling**: cutting a range into equal cells and putting one random point in each. Home:
  `basics/math-probability`. Aliases: stratified offsets, stratified.

The page also defines the glossary's entries of its brief in bold: probability, random variable, probability
distribution, probability density, expected value, pseudo-random number generator, seed, PCG32, Monte Carlo
integration, importance sampling, low-discrepancy sequence, Hammersley sequence, noise, white noise, blue noise, Vogel
disk, Poisson disk sampling, interleaved gradient noise.

## Requests

- `tools/data/extra-words.txt`: "permuted" and "congruential" (the expansion of PCG beside its first use, as the
  acronym rule asks), and "stratified" (proposed above). Their word-list findings are left until then.
- `tools/external-hosts.txt`: `pbr-book.org` (the book "Physically Based Rendering") and `www.pcg-random.org` (the PCG
  paper). The Further reading entries cite both without links until the hosts exist.
- Figures: six diagram requests in `src/content/figures/basics/math-probability.json` (the sums of two dice, the
  triangle density with an area shaded, darts in a quarter circle, Hammersley against random points, white against blue
  noise, the Vogel spiral). None is drawn yet.
- The brief's "Where the book uses it" names `make/recipes` and `engineering/testing`; the `pages` check refuses them
  because their Needs closure does not hold this page. The section links `basics/math-sphere`, `light/reflectance`,
  `light/energy`, `light/sun-shadows-2` and `indirect/problem` instead; `make/recipes` stays as a link in the opening
  section. If those two pages list this primer in their Needs, the section can name them again.
- Word choices made to stay on the word list: "text patches" for "blotches", "uneven" for "patchy", "inverse sine" for
  "arcsine", "ten times" for "tenfold", "the part after the point" for "fractional part", "a rectangle and a small
  triangle" for "trapezoid".
- Sketch limits: the page's level is 1, so every sketch holds at most 25 lines. The importance sketch drops its blank
  lines and header comment to fit; the others use `std::mt19937` for the same reason, and the PCG sketch starts its
  generators from large states (the SDK's `Seed` takes six more lines).

## Not verified

- The expansion of PCG ("permuted congruential generator", O'Neill's paper) is general knowledge; the engine's comment
  names only "PCG32, XSH-RR variant".
- That Strata's solutions work with the gold coins of `make/project-coin-run`: the Coin Run exercise is pseudocode over
  the SDK calls `Random`, `Range`, `Chance`, `GetEntity().SetWorldPosition` and a `Seed` field (all read at the pin in
  `StrataScriptCore/Include/StrataScript/`), but the page of Coin Run does not exist yet, so its end state is unchecked.
- The figures' pictures (not drawn).

## Findings not applied

- The brief's Fit says the page splits and that ideas 8, 10 and 11 move to `basics/noise-patterns`. The glossary homes
  blue noise, white noise, noise, the Vogel disk, Poisson disk sampling and interleaved gradient noise on this page, and
  the task asks for the whole of Covers, so the page teaches them in short sections. No `basics/noise-patterns` page is
  written here.
- Not applied: the item `build-test:227` beyond one paragraph; how the blue-noise table is generated and checked stays
  with `engineering/generated-code`, as the Leaves out says.

Applied: critic-basics-b-4 (the first shader quote is introduced by what differs from C++, and each shader quote is
followed by its explanation), critic-basics-b-16 (an unseeded generator gives the same sequence), critic-basics-b-17
(the triangle of two dice, the grain's square root of 3, `PixelRandom` as a hash without state), critic-basics-b-20
(the importance example is a density on a line, and the hemisphere is `basics/math-sphere`'s).

## Clerk

- Admitted: Exclusive (cases) (alias mutually exclusive), Uniform (distribution) (alias uniform distribution), variance, standard deviation (alias "spread" left out: one everyday word), stratified sampling (aliases stratified offsets, stratified).
- Refused: mean (school arithmetic, G0 has 6: the average of a few numbers).
- `extra-words.txt`: "permuted", "congruential". `external-hosts.txt`: `pbr-book.org`, `www.pcg-random.org` (front pages fetched).
- Left for the planner: the Needs of `make/recipes` and `engineering/testing`.
- Not admitted, because the page check would then fail and the page is the writer's: independent-events (its paragraph would define 2 terms with Exclusive (cases) (term-paragraph)). The part's reviewer splits the paragraph or section or bolds the term; the next clerk admits it then.

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).

Checkpoint 4 of `make/project-coin-run` already holds `Scripts/CoinPlacer.cpp` (it places the five coins), so the exercise's script is now `RandomCoin`.
