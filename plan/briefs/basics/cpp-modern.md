# Brief: `basics/cpp-modern`

| Field | Value |
| --- | --- |
| Title | Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/cpp-generic` |
| From | new by split of `basics/cpp`; move semantics, `constexpr`, `std::optional`, `std::variant`, `std::span`, `std::string_view`, `enum class`, `if constexpr`, concepts and `requires`, macros, in the measure Strata's code uses them (scene-ecs concept 17) |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/cpp-modern` — Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts

**Covers.** In the measure Strata's code uses each feature. Move semantics: copying against moving, `std::move`, `&&` in
a type, what is left in an object moved from, and types that can only move (a unique pointer, a thread); perfect
forwarding with `std::forward` and `Args&&...`, read on `CreateScope`. `std::optional` in depth, beyond the `has_value`
and `value_or` of `basics/programming-3`: `std::nullopt`, `*` and `->`, `value()` and its exception, and when to return
one. `std::variant` and `std::visit`. Views that point into someone else's data: `std::string_view` and `std::span`, how
they dangle, and walking a span backwards with reverse iterators. Scoped enumerations with a fixed underlying type
(`enum class X : uint32_t`), `static_cast` to and from numbers, and flag operators for scoped enums, as Strata's
`Base.h` defines them. `constexpr` variables and functions, `static_assert` on them, `if constexpr`. `auto`, `decltype`
and type traits (`std::is_same_v`, `std::is_base_of_v`). Concepts and `requires`. The preprocessor: `#include`,
`#define` and macros with arguments, `#if`, `#ifdef` and `#error`, definitions that the build passes in (`ST_DIST`,
`ST_WITH_<MODULE>` as examples), and why macros are kept for what nothing else can do (`ST_CORE_ASSERT`,
`ST_SCRIPT_CLASS`). Exceptions: `throw`, `try` and `catch`, one sentence that unwinding runs the destructors of the
objects it leaves, and that engine code does not throw (the rule is `core/conventions`'). `std::filesystem::path`:
joining with `/` and the extension (why its text encoding matters on Windows is `core/files`'). Incomplete types: a
class declared but not defined (`class Scene;`), and what a `std::unique_ptr` or a `std::span` of one needs. The
Practice runs in the playground's script, from easy to hard: a copy against a move predicted, then run; a function that
returns a `std::optional`; a `std::variant` visited; a `constexpr` function and a scoped enum with its type; it ends
with the optional Coin Run item: a function that returns the nearest coin as a `std::optional` (none when all are
taken), an `enum class` for the game's state with a `switch`, and the number of coins as a `constexpr`.

**Leaves out.**

- Strata's rules for errors, asserts and exceptions → `core/conventions`
- Paths and text encodings on Windows → `core/files`
- The flags and portability of Strata's build → `engineering/flags-portability`
- Compile definitions set by CMake → `basics/build`
- Strata's reflection with `std::variant` values → `world/reflection`
- The macros of the script SDK inside → `scripting/abi-sdk`

**Fit.** `fits`: about 6,000 words against L (5,000). Thirteen features, each with a sketch from zero (about 4,700),
and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed parts (about 1,300); move
semantics and the preprocessor take the most, and the page stands about 500 words under L's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:150` | concept | home | Move semantics: copy against move, `std::move`, `&&`, the object moved from, types that only move. General knowledge. |
| `new:151` | concept | home | Perfect forwarding with `std::forward`, read on `CreateScope`. General knowledge. |
| `new:152` | concept | home | `std::optional` in depth, extending the use level of `basics/programming-3` (`has_value`, `value_or`): `std::nullopt`, `*`, `->`, `value()`. General knowledge. |
| `new:153` | concept | home | `std::variant` and `std::visit`. General knowledge. |
| `new:154` | concept | home | Views: `std::string_view` and `std::span`, how they dangle, reverse iterators over a span. General knowledge. |
| `new:155` | concept | home | Scoped enumerations with a fixed underlying type, `static_cast`, flag operators. General knowledge. |
| `new:156` | concept | home | `constexpr`, `static_assert` on it, `if constexpr`. General knowledge. |
| `new:157` | concept | home | `auto`, `decltype` and type traits. General knowledge. |
| `new:158` | concept | home | Concepts and `requires`. General knowledge. |
| `new:159` | concept | home | The preprocessor: `#include`, macros, `#if`, `#ifdef`, `#error`, definitions passed by the build. General knowledge. |
| `new:160` | concept | home | Exceptions: `throw`, `try`, `catch`; unwinding runs the destructors of the objects it leaves, in one sentence (core-q8). General knowledge. |
| `new:161` | concept | home | `std::filesystem::path`: joining, the extension. General knowledge. |
| `new:162` | concept | home | Incomplete types and forward declarations. General knowledge. |
| `new:163` | hands-on | home | Optional practice on Coin Run: the nearest coin as a `std::optional`, an `enum class` state with a `switch`, a `constexpr` count. General knowledge. |
| `new:220` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the sizes of two `std::vector`s logged after a copy and after a `std::move`; Medium: a function that returns `std::optional<int>` and a caller that uses `value_or`; Medium: a `std::variant<int, std::string>` logged with `std::visit`; Hard: a `constexpr` function checked with `static_assert`, and an `enum class` with a fixed underlying type cast to a number and back with `static_cast`. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `foundation:353` | code | use | `Base.h`: `CreateScope`'s forwarding and the flag operators for scoped enums (the whole excerpt is `core/conventions`') |
| `scene-ecs:336` | concept | use | `if constexpr` for tag types and `std::variant` for values, the part of the concept taught here |
| `foundation:275` | concept | link | Errors: asserts, verifies, returned errors and exceptions, linked to `core/conventions` |
| `foundation:317` | concept | link | Paths made from narrow strings on Windows, linked to `core/files` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Templates, lambdas and the standard containers | `basics/cpp-generic` | must |
| Ownership and `std::unique_ptr` | `basics/cpp-memory` | must |
| `std::optional` at the use level | `basics/programming-3` | must |
| Header files and `#include` | `basics/programming-3` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `c-concept` | C++ concept | - |
| `constexpr` | constexpr | - |
| `macro` | macro | - |
| `move-semantics` | move semantics | - |
| `preprocessor` | preprocessor | - |
| `requires-clause` | requires clause | - |
| `span` | span | std::span |
| `string-view` | string view | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-12 | should | thin-home | `basics/programming-3` (`new:71`) | Track G learns C++ only on `basics/programming-1` to `-3`, and `-3` promises that the reader can then read `reference/script-api`, which shows the SDK's declarations. They use words that no page of track G teaches: `std::string_view` 87 times in 10 headers (nearly every name an SDK function takes), `uint32_t` and `uint64_t` (71 and 47; `GetGamepadAxis`, which `basics/programming-2` quotes, takes a `uint32_t gamepad`), `template<typename T>` before a declaration (24), `explicit` (16), `[[maybe_unused]]` on the callbacks of `Script` (15), `constexpr` (12) and `= default` (8). `std::string_view` is taught only on `basics/cpp-modern` and the integer sizes only on `basics/numbers`, both off track G. | The section on reading a declaration adds a short table of these words, one sentence each for reading: what a `std::string_view` parameter accepts, and that one a callback receives is copied into a `std::string` to be kept; "u" and the bits in `uint32_t`; `template<typename T>` as the line before a template; the rest; each with its home on tracks B and E linked (about 200 words). | `allocation/basics-a.md:323-327`; `tracks.md:80-85`; `allocation/reference.md:3-16`; counted by `docs-work/C2/critic-basics-a/sdk_features.py` over `StrataScriptCore/Include/StrataScript/*.h` without `ScriptABI.h` and the `Detail` namespaces; `StrataScriptCore/Include/StrataScript/Input.h:328`; `StrataScriptCore/Include/StrataScript/Scene.h:24` |
| critic-basics-a-16 | should | missing-item | `basics/cpp-modern`, `basics/numbers`, `basics/cpp-generic` | A sweep of `Strata/src` finds C++ that track E's internals pages will quote and that no primer lists: `std::chrono` (348 lines in 70 files), structured bindings such as `auto [end, error]` (240 lines in 65 files), `reinterpret_cast` (103 in 47), `std::numeric_limits` (72 in 41) and `mutable` (65 in 28, mostly a mutex in a class with `const` member functions). `basics/threads`' practice times a mutex against an atomic, which needs a clock. And `static_cast` is used on `basics/cpp-generic` but taught on `basics/cpp-modern`, the next page. | `basics/cpp-modern` takes structured bindings, `mutable` and the casts (`reinterpret_cast`, and why a number is read from bytes through `std::memcpy` or `std::bit_cast`); `basics/numbers` takes `std::numeric_limits` beside the ranges; `basics/cpp-generic` takes `std::chrono::steady_clock` with durations, and `static_cast` where it first uses it (about 450 words over the three pages). | `grep -rnE` over `Strata/src` at the pin, counts as given; `Strata/src/Strata/Core/Application.cpp:28`; `Strata/src/Strata/Core/CommandLine.cpp:59`; `Strata/src/Strata/Core/BinaryStream.h:24`; `Strata/src/Strata/Core/BoundedRead.cpp:15`; `Strata/src/Strata/Core/BackgroundLogSink.h:74`; a search of `allocation/*.md` for `std::chrono`, `steady_clock`, `reinterpret_cast`, `numeric_limits` and "structured binding" finds nothing; `allocation/basics-a.md:879`, `:943`, `:1279` |
