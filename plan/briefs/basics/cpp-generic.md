# Brief: `basics/cpp-generic`

| Field | Value |
| --- | --- |
| Title | Generic C++: templates, lambdas and the standard containers |
| Kind | P |
| Size | L |
| Tracks | B, E |
| Needs | `basics/cpp-classes`, `basics/trees-graphs` |
| From | new by split of `basics/cpp`; templates, lambdas and captures, `std::function`, the standard containers; scene-ecs concept 17 (type erasure with `std::function` and `void*`, CRTP, pointers to members) |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/cpp-generic` — Generic C++: templates, lambdas and the standard containers

**Covers.** Templates: a function template and a class template, the compiler that writes a version for each type,
type and value arguments, several arguments (a format string and its values as an example), and `static_assert` that
checks a template's argument while compiling. The standard containers and what they cost, from
`basics/data-structures`: `std::vector`, `std::array`, `std::deque`, `std::map` and its order, `std::unordered_map`,
`std::set`, `std::bitset`, `std::pair` and `std::tuple`. Iterators: `begin` and `end`, the range-based `for` as
iterators, reverse iterators, and iterators that a change of the container makes invalid. The standard algorithms:
`std::sort` with a comparator, `std::find_if`, `std::remove_if` with `erase`. `std::map`'s node handles: `extract`
and `insert` with a hint. Lambdas: their syntax, captures by value and by reference, `this`, and object lifetimes (a
lambda that keeps a reference to a local that is gone). `std::function`: keeping any callable, callbacks stored in a
container, a function that takes a function and returns one. The C form of a callback: function pointers and a user
pointer (`void*`), and calling a C library from C++ with its configuration structs and result codes. Type erasure
(scene-ecs concept 17): one type that hides many, `std::function` and `void*` with `static_cast` back; CRTP, a base
class template that knows its derived class, for builders that chain calls; pointers to members (`float Coin::*`,
`&Coin::Speed`), as `ST_SCRIPT_FIELD` passes a member to the builder (`if constexpr` and `std::variant` of the same
concept are `basics/cpp-modern`'s). The Practice runs in the playground's script, from easy to hard: a function
template; sorting and removing with lambdas; captures by value and by reference predicted, then run; stored callbacks
and an iterator a change made invalid; it ends with the optional Coin Run item: sort the coins left by their distance
to the ball with `std::sort` and a lambda, and call a stored callback when the last coin is taken.

**Leaves out.**

- Move semantics, `if constexpr`, `std::variant`, concepts and `requires` → `basics/cpp-modern`
- What each data structure costs, from zero → `basics/data-structures`, `basics/trees-graphs`
- Strata's reflection, its builders and type erasure in use → `world/reflection`
- What `ST_SCRIPT_CLASS` and `ST_SCRIPT_FIELD` do inside → `scripting/abi-sdk`
- Callbacks from a window library → `core/windows-events`
- Job functions moved into a queue → `core/jobs`

**Fit.** `fits`: about 5,550 words against L (5,000). Templates, the containers and their iterators, the algorithms,
node handles, lambdas, `std::function`, the C form of callbacks, type erasure, CRTP and pointers to members, twelve
ideas from zero (about 4,250), and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed
parts (about 1,300); the containers and lambdas take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:139` | concept | home | Function and class templates; type and value arguments; several arguments. General knowledge. |
| `new:140` | concept | home | `static_assert` that checks a template's argument while compiling. General knowledge. |
| `new:141` | concept | home | The standard containers and their costs, `std::pair` and `std::tuple`. General knowledge. |
| `new:142` | concept | home | Iterators, reverse iterators, and iterators made invalid by a change. General knowledge. |
| `new:143` | concept | home | The standard algorithms: `std::sort` with a comparator, `std::find_if`, `std::remove_if`. General knowledge. |
| `new:144` | concept | home | `std::map`'s node handles: `extract`, and `insert` with a hint. General knowledge. |
| `new:145` | concept | home | Lambdas and captures by value and by reference; object lifetimes in a capture. General knowledge. |
| `new:146` | concept | home | `std::function`, callbacks in a container, functions that take and return functions. General knowledge. |
| `new:147` | concept | home | Function pointers and a user pointer; calling a C library: configuration structs and result codes. General knowledge. |
| `new:148` | concept | home | Pointers to members, as `ST_SCRIPT_FIELD` passes a member to the builder. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:857-858` |
| `new:149` | hands-on | home | Optional practice on Coin Run: coins sorted by distance with a lambda; a callback when the last coin is taken. General knowledge. |
| `new:219` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic: a function template `Largest` called with `int` and with `float`; Medium: `std::sort` with a lambda comparator, then `std::remove_if` with `erase`; Medium, predict then run: a lambda that captures a counter by value and one that captures it by reference, both called after the counter changes; Hard: a `std::vector` of `std::function` callbacks called in order, and why an iterator kept across a `push_back` must not be used. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scene-ecs:336` | concept | home | Type erasure and templates: `std::function`, `void*` with `static_cast`, CRTP builders; its `if constexpr` and `std::variant` are taught on `basics/cpp-modern` |
| `scene-ecs:651` | term | home | Type erasure |
| `scene-ecs:652` | term | home | CRTP |
| `scripting:113` | feature | use | `ScriptClassBuilder<T>::Field<&T::M>`, a pointer to a member as a template argument |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Template arguments in angle brackets | `basics/programming-3` | must |
| Arrays and hash maps, and what they cost | `basics/data-structures` | must |
| Trees and ordered maps, and what they cost | `basics/trees-graphs` | must |
| Pointers, references and object lifetimes | `basics/cpp-memory` | must |
| Virtual functions | `basics/cpp-classes` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `c-template` | C++ template | - |
| `callback` | callback | - |
| `container` | container | - |
| `crtp` | CRTP | curiously recurring template pattern |
| `function-object` | function object | - |
| `iterator` | iterator | - |
| `lambda` | lambda | lambda expression |
| `lambda-capture` | lambda capture | - |
| `standard-library` | standard library | C++ standard library |
| `type-erasure` | type erasure | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-16 | should | missing-item | `basics/cpp-modern`, `basics/numbers`, `basics/cpp-generic` | A sweep of `Strata/src` finds C++ that track E's internals pages will quote and that no primer lists: `std::chrono` (348 lines in 70 files), structured bindings such as `auto [end, error]` (240 lines in 65 files), `reinterpret_cast` (103 in 47), `std::numeric_limits` (72 in 41) and `mutable` (65 in 28, mostly a mutex in a class with `const` member functions). `basics/threads`' practice times a mutex against an atomic, which needs a clock. And `static_cast` is used on `basics/cpp-generic` but taught on `basics/cpp-modern`, the next page. | `basics/cpp-modern` takes structured bindings, `mutable` and the casts (`reinterpret_cast`, and why a number is read from bytes through `std::memcpy` or `std::bit_cast`); `basics/numbers` takes `std::numeric_limits` beside the ranges; `basics/cpp-generic` takes `std::chrono::steady_clock` with durations, and `static_cast` where it first uses it (about 450 words over the three pages). | `grep -rnE` over `Strata/src` at the pin, counts as given; `Strata/src/Strata/Core/Application.cpp:28`; `Strata/src/Strata/Core/CommandLine.cpp:59`; `Strata/src/Strata/Core/BinaryStream.h:24`; `Strata/src/Strata/Core/BoundedRead.cpp:15`; `Strata/src/Strata/Core/BackgroundLogSink.h:74`; a search of `allocation/*.md` for `std::chrono`, `steady_clock`, `reinterpret_cast`, `numeric_limits` and "structured binding" finds nothing; `allocation/basics-a.md:879`, `:943`, `:1279` |
