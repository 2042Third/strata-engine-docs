# Brief: `basics/numbers`

| Field | Value |
| --- | --- |
| Title | Numbers in a computer: binary, integers, floating point and precision |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/computer`, `basics/programming-1` |
| From | new (curricula 1.1, 1.2); binary and hexadecimal, two's complement, shifts and masks, packing keys, IEEE 754, spacing that grows with magnitude, rounding and determinism; powers and logarithms (EV stops, decibels), the exponential function and the number e; home of floating point and precision, and of exponentials |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/numbers` — Numbers in a computer: binary, integers, floating point and precision

**Covers.** The page starts track B's second visit to `basics` and uses the reader's Coin Run as its source of numbers.
Binary: place values worth twice the place to their right, counting in binary, a bit, a byte of eight bits; hexadecimal
with four bits per digit and the `0x` prefix (colors, addresses and hashes are written in it); other bases, and writing
a number's digits backwards behind the point in base 2 and base 3 (the radical inverse that `image/taa` uses). Integers
of fixed sizes: `int8_t` to `uint64_t`, `int32_t` and `uint32_t`, their ranges, 16-bit samples of sound; two's
complement for signed integers; integer overflow, which wraps for unsigned types and is not allowed for signed ones
(undefined behavior is `basics/cpp-memory`'s). Integer division that rounds down, the rule that rounds up
(`(a + b - 1) / b`), and `%`. Bits: the bitwise operators `&`, `|`, `^` and `~`, masks that keep, set, clear and test
bits, bit flags (a collision layer's mask in words); shifts `<<` and `>>` as multiplying and dividing by powers of two;
two numbers packed into one integer and taken out again (an index of 20 bits and a version of 12, as `world/ecs` shows);
counting trailing zeros (`std::countr_zero`); interleaving the bits of two numbers (Morton order). Floating point: a
sign, an exponent and a significand (IEEE 754), `float` of 32 bits and `double` of 64, and the bits of a float laid out
in a figure; the spacing between neighbouring floats grows with their size, so precision falls far from the origin (the
gap at 1 m, 1 km and 20 km in a table; a timer in a `float` after hours) and `double` is the cure where it matters.
Rounding: which operations are exact (small integers, halving and doubling), why `0.1 + 0.2` is not `0.3`, comparing
with a tolerance, and quantizing a float into fewer bits. Determinism: the same inputs give the same bits, and why two
results can still differ in the last bit (the order of additions; fused multiply-add in one sentence, which is
`engineering/flags-portability`'s); Strata's promise that results do not depend on the number of threads is `core/jobs`'
design decision. The values that are not numbers: infinities, NaN (which is not equal to itself and spreads through
every sum), overflow of floats to infinity, subnormals near zero, and half floats of 16 bits with their range and the
integers they hold exactly. Powers: powers of two, sizes in KiB, MiB and GiB against kB and MB, bandwidth in GB/s; a
geometric series (1 + 1/2 + 1/4 + ...) is named in one sentence with a link to `basics/math-interpolation`, which
teaches it and its sum. Logarithms: the exponent asked for backwards, base 2 (how many times a size halves: mip levels)
and base 10, the logarithm of a product; ratios on a logarithmic scale, EV stops (each a factor of two of light) and
decibels (10 dB is ten times the energy). The exponential function and the number e: growth or decay by the same factor
in each equal step, `exp(-k t)`, which `basics/math-interpolation` turns into smoothing. The Practice runs by hand and
in the playground's script, from easy to hard: numbers converted between binary, decimal and hexadecimal; an integer's
overflow predicted, then run; bits set, cleared and tested with masks; a float sum compared with and without a
tolerance; the gap between neighbouring floats measured; it ends with the optional Coin Run item: keep the HUD's timer
in a `float`, find after how long adding one frame's time no longer changes it, and keep it in a `double`.

**Leaves out.**

- Bytes in files, byte order and text → `basics/bytes`
- The sRGB curve and the half-float range for colors → `basics/color`
- Fused multiply-add and determinism across compilers → `engineering/flags-portability`
- Strata's deterministic parallel work → `core/jobs`
- Why a world must stream, and its 20 km limit → `worlds/why-streaming`
- Rendering relative to the camera → `draw/mirrors-camera-relative`
- Exponential smoothing and `1 - exp(-k dt)` → `basics/math-interpolation`
- A geometric series and its sum → `basics/math-interpolation`
- Exposure in EV stops in the editor → `make/lighting`
- Undefined behavior → `basics/cpp-memory`

**Fit.** `over`: about 7,050 words against L (5,000). Seventeen ideas from zero at B0's length with the figure of a
float's bits and the table of gaps (about 5,750), and the common mistakes, the Practice's five exercises, the Coin Run
item and the fixed parts (about 1,300). A primer is at most L, so the page splits (S3), in this order on tracks B and E:
`basics/numbers` "Numbers in a computer: binary, integers, bits and floating point" (L, about 5,800) and
`basics/math-powers` "Powers, logarithms and the exponential function" (S, about 2,100 with a practice of its own);
`book.md`'s one-home row for powers and logarithms would then name the second.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:82` | concept | home | Binary: place values, counting, a bit, a byte of eight bits. General knowledge. |
| `new:83` | concept | home | Hexadecimal: four bits per digit and the `0x` prefix. General knowledge. |
| `new:84` | concept | home | Other bases, and a number's digits written backwards behind the point (the radical inverse in base 2 and 3). General knowledge. |
| `new:85` | concept | home | Integer types of fixed sizes and their ranges; 16-bit samples. General knowledge. |
| `new:86` | concept | home | Two's complement, signed and unsigned, and integer overflow. General knowledge. |
| `new:87` | concept | home | Integer division that rounds down, the rule that rounds up, and `%`. General knowledge. |
| `new:88` | concept | home | Bitwise operators, masks and bit flags. General knowledge. |
| `new:89` | concept | home | Shifts, two numbers packed into one integer, counting trailing zeros, interleaved bits (Morton order). General knowledge. |
| `new:90` | concept | home | Floating point: sign, exponent and significand; `float` and `double`; the bits of a float. General knowledge. |
| `new:91` | concept | home | Spacing that grows with magnitude: precision far from the origin, a float timer after hours, `double`. General knowledge. |
| `new:92` | concept | home | Rounding: exact operations, `0.1 + 0.2`, tolerances, quantizing a float into fewer bits. General knowledge. |
| `new:93` | concept | home | Determinism as the same bits for the same inputs, and why two results differ in the last bit. General knowledge. |
| `new:94` | concept | home | Infinities, NaN, overflow of floats, subnormals, and half floats with their range and exact values. General knowledge. |
| `new:95` | concept | home | Powers and powers of two; KiB, MiB and GiB against kB and MB; bandwidth in GB/s. General knowledge. |
| `new:96` | concept | link | A geometric series, named beside the powers with a link to `basics/math-interpolation`, which teaches it and its sum. General knowledge. |
| `new:97` | concept | home | Logarithms: base 2 and base 10, the logarithm of a product. General knowledge. |
| `new:98` | concept | home | Ratios on a logarithmic scale: EV stops and decibels. General knowledge. |
| `new:99` | concept | home | The exponential function and the number e; decay by the same factor in each step, `exp(-k t)`. General knowledge. |
| `new:100` | hands-on | home | Optional practice on Coin Run: the HUD's timer in a `float` stops growing; keep it in a `double`. General knowledge. |
| `new:216` | hands-on | home | Practice before the Coin Run item, by hand and in the playground's script with `Log::Info`, from easy to hard: Basic: 13 written in binary and `0xFF` in decimal, each checked with a logged value; Basic, predict then run: a `uint16_t` of 65,535 plus one stored back, and an `int` division that rounds down; Medium: bit 3 of a flags value set, cleared and tested with masks; Medium, predict then run: `0.1f + 0.2f == 0.3f`, then the same sum compared with a tolerance; Hard: the gap between neighbouring floats at 1, 1,000 and 20,000 found with `std::nextafter` and logged. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `physics:538` | term | home | Determinism, in general; that Strata's holds for any thread count is linked to `core/jobs` |
| `render-image:639` | term | home | NaN and Inf, the results of broken arithmetic |
| `scene-ecs:421` | figure | link | The entity handle's 20-bit index and its version, linked to `world/ecs` as the packing example |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Memory as numbered bytes | `basics/computer` | must |
| Variables, the types `int`, `float`, `double` and `bool`, and operators | `basics/programming-1` | must |
| Loops, for the worked examples that repeat a step | `basics/programming-2` | helps |
| Exposure in EV stops as the editor shows it | `make/lighting` | helps |
| Coin Run's HUD timer | `make/hud` | helps |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run by hand and in the playground's script.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `binary` | binary | base 2 |
| `bit` | bit | - |
| `bit-mask` | bit mask | - |
| `bit-shift` | bit shift | - |
| `bitwise-operator` | bitwise operator | - |
| `decibel` | decibel | dB |
| `determinism` | determinism | deterministic |
| `eulers-number` | Euler's number | - |
| `exponent` | exponent | - |
| `exponential-function` | exponential function | - |
| `exposure-stop` | exposure stop | EV stop |
| `floating-point-number` | floating-point number | floating point |
| `hexadecimal` | hexadecimal | hex, base 16 |
| `integer` | integer | - |
| `integer-overflow` | integer overflow | overflow |
| `logarithm` | logarithm | - |
| `nan` | NaN | Inf |
| `power` | power | - |
| `precision` | precision | - |
| `rounding-error` | rounding error | round-off error |
| `twos-complement` | two's complement | - |
| `unsigned-integer` | unsigned integer | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-7 | must | stale-item | `basics/numbers` (`new:216`, `new:92`, `new:91`) | The Practice asks the reader to predict, then run, `0.1f + 0.2f == 0.3f` as the case of "0.1 + 0.2 is not 0.3". In `float` the sum rounds to the same float as `0.3f`, so the program logs `true` and contradicts the lesson; only in `double` do the two differ. Besides, `Log::Info` writes floats with six significant digits, so the reader never sees a difference: the double sum logs `0.3`, and the float after 1 (`std::nextafter`) logs `1`. | The exercise uses `0.1 + 0.2 == 0.3` in `double`, or ten additions of `0.1f` against `1.0f` (both `false`), predicted then run. The page teaches how to print every digit (a string made with `std::ostringstream` and `std::setprecision`, 9 digits for a float and 17 for a double, then logged) and says that `Log` shows six (about 120 words). The gap exercise logs the difference, not the neighbour. | `allocation/basics-a.md:527-528`, `:587`; `StrataScriptCore/Include/StrataScript/Log.h:21-25`, `:74-83` (a default `std::ostringstream`); computed in IEEE single precision by `docs-work/C2/critic-basics-a/floats.py`: 0.1f + 0.2f and 0.3f are both 0.30000001192092896, ten times 0.1f is 1.0000001192092896 |
| critic-basics-a-8 | must | stale-item | `basics/numbers` (`new:87`, `new:216`) | The page says that integer division "rounds down" and gives `(a + b - 1) / b` as the rule that rounds up. C++ truncates toward zero: -7 / 2 is -3, not -4, and -7 % 2 is -1. Both rules hold only for a non-negative `a` and a positive `b`. Engines meet negative coordinates all the time: Strata floors its world cell coordinates and has its own `FloorDivide` for the GI grid for exactly this reason. | Teach division as truncation toward zero, the sign of `%`, floor division for negative values (the shape of `FloorDivide`) and the condition of the round-up rule; the Practice's division case gets a negative dividend, predicted then run (about 120 words). `basics/programming-1`'s `%` gets one sentence: a negative left operand gives a negative remainder. | `allocation/basics-a.md:170`, `:519-520`, `:573`, `:587`; `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:17-21`; `Strata/src/Strata/World/WorldGrid.cpp:20-22`; the C++ standard, [expr.mul] (the quotient is truncated toward zero) |
| critic-basics-a-12 | should | thin-home | `basics/programming-3` (`new:71`) | Track G learns C++ only on `basics/programming-1` to `-3`, and `-3` promises that the reader can then read `reference/script-api`, which shows the SDK's declarations. They use words that no page of track G teaches: `std::string_view` 87 times in 10 headers (nearly every name an SDK function takes), `uint32_t` and `uint64_t` (71 and 47; `GetGamepadAxis`, which `basics/programming-2` quotes, takes a `uint32_t gamepad`), `template<typename T>` before a declaration (24), `explicit` (16), `[[maybe_unused]]` on the callbacks of `Script` (15), `constexpr` (12) and `= default` (8). `std::string_view` is taught only on `basics/cpp-modern` and the integer sizes only on `basics/numbers`, both off track G. | The section on reading a declaration adds a short table of these words, one sentence each for reading: what a `std::string_view` parameter accepts, and that one a callback receives is copied into a `std::string` to be kept; "u" and the bits in `uint32_t`; `template<typename T>` as the line before a template; the rest; each with its home on tracks B and E linked (about 200 words). | `allocation/basics-a.md:323-327`; `tracks.md:80-85`; `allocation/reference.md:3-16`; counted by `docs-work/C2/critic-basics-a/sdk_features.py` over `StrataScriptCore/Include/StrataScript/*.h` without `ScriptABI.h` and the `Detail` namespaces; `StrataScriptCore/Include/StrataScript/Input.h:328`; `StrataScriptCore/Include/StrataScript/Scene.h:24` |
| critic-basics-a-16 | should | missing-item | `basics/cpp-modern`, `basics/numbers`, `basics/cpp-generic` | A sweep of `Strata/src` finds C++ that track E's internals pages will quote and that no primer lists: `std::chrono` (348 lines in 70 files), structured bindings such as `auto [end, error]` (240 lines in 65 files), `reinterpret_cast` (103 in 47), `std::numeric_limits` (72 in 41) and `mutable` (65 in 28, mostly a mutex in a class with `const` member functions). `basics/threads`' practice times a mutex against an atomic, which needs a clock. And `static_cast` is used on `basics/cpp-generic` but taught on `basics/cpp-modern`, the next page. | `basics/cpp-modern` takes structured bindings, `mutable` and the casts (`reinterpret_cast`, and why a number is read from bytes through `std::memcpy` or `std::bit_cast`); `basics/numbers` takes `std::numeric_limits` beside the ranges; `basics/cpp-generic` takes `std::chrono::steady_clock` with durations, and `static_cast` where it first uses it (about 450 words over the three pages). | `grep -rnE` over `Strata/src` at the pin, counts as given; `Strata/src/Strata/Core/Application.cpp:28`; `Strata/src/Strata/Core/CommandLine.cpp:59`; `Strata/src/Strata/Core/BinaryStream.h:24`; `Strata/src/Strata/Core/BoundedRead.cpp:15`; `Strata/src/Strata/Core/BackgroundLogSink.h:74`; a search of `allocation/*.md` for `std::chrono`, `steady_clock`, `reinterpret_cast`, `numeric_limits` and "structured binding" finds nothing; `allocation/basics-a.md:879`, `:943`, `:1279` |
| critic-basics-a-20 | should | order | `basics/cpp-memory` (`new:129`, `new:217`) | The Practice writes an arena that hands out memory in a row. To put objects into it, the reader needs alignment (each object at an address that is a multiple of its `alignof`) and a way to construct an object in raw memory (placement `new` or `std::construct_at`, and the destructor called by hand). Alignment is taught on `basics/bytes`, five pages later on tracks B and E, and placement `new` and `std::construct_at` are on no page. Without them the arena is undefined behavior, on the page that teaches undefined behavior. | The allocator section teaches alignment in the measure the arena needs (round the offset up to `alignof(T)` with the round-up rule of `basics/numbers`) and `std::construct_at` with `std::destroy_at`, and links `basics/bytes` for layouts and padding (about 150 words). | `allocation/basics-a.md:751-752`, `:790`, `:1092-1093`, `:1123`; `tracks.md:187-192`; a search of `allocation/*.md` for "placement new", "construct_at" and "alignof" finds nothing |
| critic-basics-a-22 | should | missing-item | `basics/bytes` (`new:176`, `new:208`); `basics/numbers` (`new:85`) | `Log::Info` writes each value with `<<`, so a `uint8_t` or an `int8_t` prints as a character: a byte of 65 logs "A", and 200 logs a byte that is no valid UTF-8. `basics/bytes`' practice reads and writes bytes and logs them, and `basics/numbers` teaches `int8_t` and `uint8_t` with their overflow. | Both pages' Common mistakes hold it, with the fix (log `int(value)`, or `+value`) (about 60 words each). | `StrataScriptCore/Include/StrataScript/Log.h:21-25`; `allocation/basics-a.md:517`, `:1089-1090`, `:1100` |
| critic-basics-a-25 | could | shape | `basics/numbers` (`new:100`) | The optional Coin Run item waits until adding one frame's time no longer changes a `float` timer. At 60 frames a second that happens only after 2^19 s, about 146 hours; the item cannot be watched as written. Long before, from about 4.6 hours on, each frame already adds 5 to 90 percent too much or too little, which is the more useful lesson. | The item starts the timer at a large value (600,000 s) to see the stall, and at about 20,000 s to see the drift, each predicted from the table of gaps first (about 60 words). | `allocation/basics-a.md:541-542`, `:586`; computed by `docs-work/C2/critic-basics-a/timer.py`: one frame adds 0.017578 s at 2^14 s, 0.015625 s from 2^15 s, 0.03125 s at 2^18 s and nothing from 2^19 s |
