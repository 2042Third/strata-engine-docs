# Brief: `basics/math-probability`

| Field | Value |
| --- | --- |
| Title | Chance: probability, noise, integrals and Monte Carlo |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/math-change`, `basics/signals` |
| From | new by split of `basics/math-light`; curricula 1.2 ("Randomness"); random variables, density, expected value, seeds and generators (the SDK's `Random` is PCG32); white and blue noise, Hammersley, Vogel and Poisson patterns, interleaved gradient noise; integrals as areas, Monte Carlo integration; home of noise and sampling patterns |
| Unit | `plan/allocation/basics-b.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/math-probability` — Chance: probability, noise, integrals and Monte Carlo

**Covers.** In order: (1) probability: a number from 0 to 1, counted from equally likely cases (a die), the chances of
cases that cannot both happen added, those of independent events multiplied; (2) random variables and probability
distributions: a list of values with their chances, the uniform distribution, and for values on a range the probability
density, whose area over a part of the range is that part's chance; (3) the expected value and the mean, and the spread:
the variance and the standard deviation, computed from a table of samples (the spread that `image/taa` measures); (4)
pseudo-random numbers and seeds: a fixed rule that gives a sequence that looks random, the seed that starts it, read in
the SDK's `Random` (PCG32: the state update, the output's shift and rotation, `NextFloat`, and `Range`, which draws again
instead of using a biased remainder); (5) integrals as areas, recalled from `basics/math-change`; (6) Monte Carlo
integration: the average of a function at random points times the size of the range, with an error that falls as one
over the square root of the number of points, worked by darts in a quarter circle that estimate π; (7) importance
sampling: more samples where the function is large, each divided by its density, with a cosine-shaped density as the
example (cosine weighting); (8) white noise and blue noise: clumps and gaps against an even spread, why blue noise looks
finer, and Strata's 64×64 blue-noise table, made by void and cluster; (9) low-discrepancy sequences: the Hammersley set,
whose second coordinate reverses the bits of the index (Strata's two-line `Hammersley`), and stratified offsets, one
random point in each cell of a grid; (10) disk patterns: the Vogel disk, points on a spiral each turned by the golden
angle, and Poisson disk sampling, random points never closer than a set distance; (11) interleaved gradient noise: a
cheap value per pixel, computed from the pixel's position, whose neighbors differ evenly (Strata's
`InterleavedGradientNoise`).

Figures: a histogram of the sums of two dice, a density with an area shaded, darts in a quarter circle, white against
blue noise, Hammersley points against random points, the Vogel spiral. The common mistakes: `rand() % n` and its bias,
a seed from the clock in a test, a Monte Carlo estimate not divided by the density, white noise where blue noise is
wanted, a generator seeded again every frame. Practice (three to eight exercises, `style.md` §8) ends with the optional
Coin Run item: the coins placed at random with `Random` and a seed, so that one seed always gives the same level, and
`Chance(0.25)` to make some of them gold; the gold coins over 1,000 seeds are counted and compared with the expected
value. "Where the
book uses it" names `make/recipes`, `light/energy`, `light/sun-shadows-2`, `indirect/problem` and `engineering/testing`.

**Leaves out.**

- Random numbers and seeds in a game maker's recipes → `make/recipes`
- Integrals over directions and the hemisphere → `basics/math-sphere`
- Sampling the GGX lobe, and filtered importance sampling → `indirect/ibl`
- The BRDF table and its samples → `light/energy`
- The sun's filter: the Vogel disk turned by fixed blue noise → `light/sun-shadows-2`
- The Poisson taps of local shadows → `light/local-shadows`
- Halton jitter → `image/taa`
- The engine's own `Random` → `core/math`
- How the blue-noise table is generated and checked → `engineering/generated-code`
- Rates and accumulation → `basics/math-change`

**Fit.** `over`: about 8,300 words against L (5,000). Ten ideas from zero at 500 words each, the upper value for B0, and
idea (5), integrals as areas recalled from `basics/math-change`, at 200 (5,200); the six figures (900), the five common
mistakes (600), the PCG32 excerpt (250), the `Hammersley` and noise excerpts (150), the opening (100) and the fixed
parts with the Test out box, Practice and the Coin Run item (1,100). A primer is at most L, so the page splits (S3):
`basics/math-probability`, "Chance: probability, random numbers, integrals and Monte Carlo" (L, about 6,300: ideas 1 to
7 and 9, so that Hammersley and stratified offsets stand beside the estimates they improve), and after it
`basics/noise-patterns`, "Noise patterns: blue noise, the Vogel and Poisson disks and interleaved gradient noise" (M,
about 3,200: ideas 8, 10 and 11).

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:96` | concept | home | Probability from equally likely cases; adding exclusive cases, multiplying independent events. Figure: the sums of two dice. General knowledge. |
| `new:97` | concept | home | Random variables, probability distributions, the uniform distribution, probability density. Figure: a density with an area shaded. General knowledge. |
| `new:98` | concept | home | The expected value, the mean, the variance and the standard deviation. General knowledge. |
| `new:99` | concept | home | Pseudo-random number generators and seeds; uniform ranges and the bias of a remainder. General knowledge. |
| `new:100` | concept | use | Integrals as areas, recalled for estimating them: the integral as accumulation is `basics/math-change`'s (its row `new:58`; book.md's row of change over time). General knowledge. |
| `new:101` | concept | home | Monte Carlo integration and its error, one over the square root of the count. Figure: darts in a quarter circle. General knowledge. |
| `new:102` | concept | home | Importance sampling: samples where the function is large, divided by their density; cosine weighting. General knowledge. |
| `new:103` | concept | home | White noise and blue noise. Figure: the two side by side. General knowledge. |
| `new:104` | concept | home | Low-discrepancy sequences: the Hammersley set by bit reversal; stratified offsets. Figure: Hammersley against random points. General knowledge. |
| `new:105` | concept | home | The Vogel disk and the golden angle; Poisson disk sampling. Figure: the Vogel spiral. General knowledge. |
| `new:106` | concept | home | Interleaved gradient noise. General knowledge. |
| `new:107` | code | home | `Strata/shaders/Include/IBL.slang:36-39`: `Hammersley`, the index over the count and the index with its 32 bits reversed (`reversebits`) |
| `new:108` | hands-on | home | Coin Run practice, from `make/project-coin-run`'s end state: coins placed with a seeded `Random`, some made gold by `Chance(0.25)`, counted over 1,000 seeds against the expected value. Evidence: `StrataScriptCore/Include/StrataScript/Gameplay.h:26-38` (the seed) and `:81-104` (`Range`, `Chance`) |
| `scripting:383` | code | home | `StrataScriptCore/Include/StrataScript/Gameplay.h:19-110`: the SDK's `Random`, PCG32 (XSH-RR): `Seed`, `NextUInt`'s state update, shift and rotation, `Range` drawing again below the threshold, `NextFloat`, `Chance` |
| `scripting:600` | term | home | PCG32, a small, fast and statistically good pseudo-random number generator |
| `scripting:343` | concept | use | Two parts of the SDK's determinism helpers, read in `scripting:383`: the seeded PCG32 and the unbiased range by rejection (`StrataScriptCore/Include/StrataScript/Gameplay.h:62-70`, a value below the threshold drawn again); the concept's home is `make/recipes` |
| `render-direct:734` | term | home | Vogel disk, a spiral by the golden angle; one glossary entry with `render-image:721` and the seed's |
| `render-image:721` | term | home | Vogel (golden-angle) disk, an evenly spread spiral |
| `render-direct:735` | term | home | Blue noise, noise without low frequencies; one glossary entry with the seed's |
| `render-indirect:584` | term | home | Hammersley sequence; one glossary entry with the seed's |
| `render-indirect:618` | term | home | Interleaved gradient noise (IGN); one glossary entry with the seed's |
| `render-core:459` | code | use | `InterleavedGradientNoise` in `Strata/shaders/Include/Common.slang:41-46`, read as the formula's code; the excerpt's home is `gpu/shaders` |
| `build-test:227` | feature | use | `Tools/GenerateBlueNoise.py`, which makes the 64×64 blue-noise table by void and cluster |
| `render-direct:123` | feature | link | The sun's soft-shadow filter, a Vogel disk turned by blue noise, on `light/sun-shadows-2` |
| `render-indirect:583` | term | link | Importance sampling and filtered importance sampling, the item's home row on `indirect/ibl`; the glossary step gives "importance sampling" to this page, which teaches it (`new:102`), and "filtered importance sampling" to `indirect/ibl` (R48) |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Integrals as accumulation: the area under a graph | `basics/math-change` | must |
| Binary, bits, shifts, masks and the exclusive or | `basics/numbers` | must |
| Unsigned 32-bit and 64-bit integers, and overflow that wraps | `basics/numbers` | must |
| Sampling, frequency and aliasing | `basics/signals` | must |
| Sine, cosine and radians | `basics/math-vectors` | must |
| Loops, functions and `std::vector` | `basics/programming-2` | must |
| A class kept as a member of a script | `basics/programming-3` | helps |
| A script of the playground with `Log::Info` | `basics/programming-1` | must |
| Random numbers in a game maker's recipes | `make/recipes` | helps |

**Starting state.** The optional Coin Run item of Practice starts from the download of `make/project-coin-run`'s end
state, as the outline's introduction of part `basics` says for every primer after `basics/debugging`: Coin Run as
`make/project-coin-run` finishes it, with the rolling ball, the spinning coins, the HUD, the sounds, winning, losing and
the restart. The page's other examples and exercises run in the playground (`style.md` §8), which is no checkpoint.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `blue-noise` | blue noise | - |
| `expected-value` | expected value | expectation |
| `hammersley-sequence` | Hammersley sequence | Hammersley set |
| `importance-sampling` | Importance sampling | - |
| `interleaved-gradient-noise` | interleaved gradient noise | IGN |
| `low-discrepancy-sequence` | low-discrepancy sequence | - |
| `monte-carlo-integration` | Monte Carlo integration | - |
| `noise` | noise | - |
| `pcg32` | PCG32 | - |
| `poisson-disk-sampling` | Poisson disk sampling | - |
| `probability` | probability | - |
| `probability-density` | probability density | probability density function |
| `probability-distribution` | probability distribution | distribution |
| `pseudo-random-number-generator` | pseudo-random number generator | random number generator, PRNG |
| `random-variable` | random variable | - |
| `seed` | seed | - |
| `vogel-disk` | Vogel disk | Vogel spiral |
| `white-noise` | white noise | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-b-4 | should | order | `new:24` (`basics/math-bases`); `render-image:130`, `render-image:642` (`basics/color`); `render-scene:360` (`basics/signals`); `new:107`, `render-core:459` (`basics/math-probability`); `new:117`, `new:118`, `render-indirect:245` (`basics/math-sphere`) | Five pages quote Strata's shaders, which are written in Slang. No page before them teaches how to read Slang: `gpu/shaders` does, after part `basics` on track E and never on track B. No Assumes row names it, and style.md has a rule for Python fences but none for shader fences. The quotes rest on what differs from C++ and glm: `float3`, `float3x3` whose constructor takes rows (the point of `TangentBasis`), `mul`, swizzles such as `.yx`, `frac`, `select`, `reversebits`. | The first shader quote of each of the five pages is introduced by two or three sentences on what in it differs from C++ and glm, and each shader quote is followed by its explanation line by line, as R31 asks of Python (about 60 words a page). See forPlanner for a rule in style.md §9.1. | `allocation/basics-b.md:212`, `:697`, `:699`, `:779`, `:868`, `:878`, `:957-958`, `:963`; `allocation/gpu.md:189`, `:238`; `style.md:634-636`, `:679`; `tracks.md:208`; `Strata/shaders/Include/IBL.slang:41-48`; `Strata/shaders/Include/Common.slang:25-39`; `Strata/shaders/Include/Scene.slang:362-377` |
| critic-basics-b-16 | could | missing-item | `new:99` and the Assumes row of `make/recipes` on `basics/math-probability` | The SDK's `Random` made without a seed gives the same numbers in every run. Only `make/recipes` says so, on track G. The page's Assumes row names that page, which is on neither of the page's tracks, although the page itself teaches `Random`. | Idea (4) adds one sentence: an unseeded generator always gives the same sequence; seed it from a fixed number for a test and from something that varies for variety (about 40 words). Delete the Assumes row, or make it a link forward for readers who go on to track G. | `allocation/basics-b.md:808-810`, `:860`, `:895`; `allocation/make-b1.md:339-340`; `StrataScriptCore/Include/StrataScript/Gameplay.h:19-26`; `tracks.md:132-208` |
| critic-basics-b-17 | could | missing-item | `new:96`, `new:98` and `new:99` on `basics/math-probability` | Strata's post effects draw their noise in a way the page does not name. A hash of the pixel gives a random number with no state (`PixelRandom`), and sums of such numbers shape the noise: the dither adds two of them (a triangular distribution), and the film grain adds four and scales them by √3, so that their standard deviation is 1. The page's figure of two dice already shows the triangle. | Idea (1) or (2) names the triangle of the dice figure as the sum of two uniform values; idea (3) works the grain's √3 as an example of the standard deviation; idea (4) adds a hash of a position as a random number without state, beside a generator with a state (about 120 words). `image/encoding` keeps the dither's code. | `allocation/basics-b.md:803-807`, `:822`, `:857`, `:859`; `allocation/image.md:473`; `Strata/shaders/Include/Dither.slang:4-25`, `:30-35`; `Strata/shaders/Include/Grain.slang:22` |
| critic-basics-b-20 | could | order | `new:102` on `basics/math-probability` | Idea (7) takes a cosine-shaped density as its example of importance sampling. Densities over the hemisphere, with their sin θ, are taught on `basics/math-sphere`, the next page, and the Leaves out sends them there. If the example is the hemisphere's cosine weighting, the page uses what comes after it. | The row says that the example is a density on a line (cos x from 0 to π/2), and that cosine-weighted directions over the hemisphere are `basics/math-sphere`'s (`new:114`) (about 20 words). | `allocation/basics-b.md:812-814`, `:834`, `:863`, `:914-916`, `:954`; `allocation/indirect.md:399` |
