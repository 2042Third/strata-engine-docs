# Brief: `basics/programming-3`

| Field | Value |
| --- | --- |
| Title | Programming from zero III: classes, references, files of code and reading errors |
| Kind | P |
| Size | L |
| Tracks | G, B, E |
| Needs | `basics/programming-2` |
| From | new; gamedev concept 11 (classes, inheritance and `override` at the level a script needs, headers and sources, compile errors and the Problems panel); references at the use level; pointers at the use level (`T*`, a `nullptr` check, `->`: what `GetScript<T>()` returns); `std::optional` with `has_value` and `value_or` (what `Entity::GetProperty` and `Game::ReadSaveText` return); template arguments in angle brackets (`GetProperty<float>`); Coin Run checkpoint: a `Coin` class with a field, and a `BobbingCoin` derived from it |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/programming-3` — Programming from zero III: classes, references, files of code and reading errors

**Covers.** The same playground, and the C++ of gamedev concept 11 as far as a script needs it (the rules that are
special to scripts stay `make/first-script`'s). Classes: values and the functions that work on them in one type,
`public:` and `private:`, member functions called with `.`; a script class is a class, and each entity gets its own
object of it with its own fields. Constructors and the first values written beside the members (why a script does its
setup in `OnCreate` is `make/first-script`'s). Inheritance at the level a script needs: `class Coin : public Script`,
the base class and the derived class, `override`, a derived class that calls its base's function
(`Coin::OnUpdate(deltaTime)`), and a derived script whose base's fields still show in the editor. References: `&` in a
type, a function that changes its caller's variable, `const &` that avoids a copy (as the SDK's `const glm::vec3&`).
Pointers at the use level: `T*`, `nullptr`, the check before use, and `->`, on what `GetScript<T>()` returns.
`std::optional` at the use level: `has_value`, `value_or` and `*`, on what `Entity::GetProperty` and
`Game::ReadSaveText` return. Template arguments in angle brackets: `GetProperty<float>`, `GetScript<Coin>`,
`std::vector<int>`. Files of code: a header (`.h`) declares, a source file (`.cpp`) defines, `#include` copies a header
in; a class in a header and its functions in a source file; every `.cpp` and `.h` of the `Scripts` folder belongs to
the module; calling a public member function of another class through its header. Reading a C++ declaration: return
type, name, parameters with types and defaults, `const` and `static`, and an enum's declaration, practised on lines of
the SDK's headers, so that `reference/script-api` can be read; the earlier pages' parts (scoped enum values from
`basics/programming-1`, numbers turned into text with `std::to_string` from `basics/programming-2`) are read again in
declarations. Reading compile errors: the first error first, its file and line, the common messages (a missing `;`, an
unknown name, a wrong type, a missing `#include`), the Problems panel, and warnings against errors. The Practice runs
in the playground's script, from easy to hard: a value and a reference parameter predicted, then run; a small class
in a header and a source file; a property and a script read through `std::optional` and a pointer; planted compile
errors fixed from the first message; it ends with the Coin Run item: a `Coin` class with a field, in `Coin.h` and
`Coin.cpp`, and a `BobbingCoin` derived from it that also bobs.

**Leaves out.**

- Virtual calls, interfaces and operators in depth → `basics/cpp-classes`
- Pointers, lifetimes, ownership and smart pointers in depth → `basics/cpp-memory`
- `std::optional` beyond the use level, and the rest of modern C++ → `basics/cpp-modern`
- Templates written by the reader → `basics/cpp-generic`
- Compiling and linking, and why a header is not compiled alone → `basics/build`
- `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD` and no work in the constructor → `make/first-script`
- The callbacks and when each runs → `make/script-loop`
- Finding a bug in running code → `basics/debugging`

**Fit.** `fits`: about 5,800 words against L (5,000). Ten ideas from zero with the two quotes of `Entity.h` and a set
of compiler messages (about 4,450), and the common mistakes, the Practice's four exercises, the Coin Run item and the
fixed parts (about 1,350); classes, files of code and reading compile errors take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:60` | concept | home | Classes: data and functions together, `public:` and `private:`, member functions. General knowledge. |
| `new:61` | concept | home | Constructors and first values written beside the members. General knowledge. |
| `new:62` | concept | home | Objects: the engine makes one object of a script class per entity, each with its own fields. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-31` |
| `new:63` | concept | home | Inheritance at the script's level: base and derived class, `override`, calling the base's function; a derived script registers its base's fields. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:779-786` |
| `new:64` | concept | home | References: `&` in a type, changing the caller's variable, `const &` to avoid a copy. General knowledge. |
| `new:65` | concept | home | Pointers at the use level: `*` in a type (`T*`), `nullptr`, the check before use, `->`. General knowledge. |
| `new:66` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:86-92`: `GetScript<T>` returns a `T*` |
| `new:67` | concept | home | `std::optional` at the use level: `has_value`, `value_or`, `*`. General knowledge. |
| `new:68` | code | home | `StrataScriptCore/Include/StrataScript/Entity.h:66-72`: `GetProperty<T>` returns a `std::optional<T>`, with the types its comment lists |
| `new:69` | concept | home | Template arguments in angle brackets. General knowledge. |
| `new:70` | concept | home | Files of code: header and source, `#include`, declaration and definition; every `.cpp` and `.h` of the `Scripts` folder is in the module. Evidence: `StrataEditor/src/Editor/ScriptProject.cpp:213-215` |
| `new:71` | concept | home | Reading a C++ declaration: return type, name, parameters, defaults, `const`, `static`, an enum. General knowledge. |
| `new:72` | concept | home | Reading compile errors: the first one first, file and line, common messages, warnings against errors. General knowledge. |
| `new:73` | hands-on | home | Coin Run practice: a `Coin` class with a field in `Coin.h` and `Coin.cpp`, and `BobbingCoin` derived from it. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:779-786` |
| `new:214` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: a function that takes an `int` by value and one that takes it by `&`, and what the caller's variable holds after each; Medium: a class `Counter` with a `private` count, a constructor and two `public` member functions, declared in a header and defined in a source file; Medium: a component's property read with `GetProperty<float>` and `value_or`, and `GetScript<T>()` checked against `nullptr` before `->`; Hard: three planted compile errors (a missing `;`, an unknown name, a missing `#include`), each fixed from the first message in the Problems panel. Evidence: `StrataScriptCore/Include/StrataScript/Entity.h:66-72`, `StrataScriptCore/Include/StrataScript/Entity.h:86-92` |
| `gamedev:317` | concept | home | Scripts in C++: classes, inheritance for `override`, public members as fields, headers and sources, compile errors and the Problems panel; the rules special to scripts are `make/first-script`'s and building the module is `make/script-builds`' |
| `gamedev:372` | code | use | `Samples/Tetris/Scripts/TetrisGame.h:8-106`: a class in a header, read for its declarations |
| `scripting:118` | feature | use | `Entity`'s `GetScript` and `GetProperty` |
| `scripting:129` | feature | use | `Game::ReadSaveText` and its `std::optional` |
| `editor-ui:149` | feature | use | The Problems panel, where compile errors are read |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Loops, functions, structs, `std::vector` and `std::string` | `basics/programming-2` | must |
| The script class, `override` and the Problems panel as `make/first-script` shows them | `make/first-script` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin
Run lit for play, its five coin instances spinning by the reader's `Coin` script in `Coin.cpp`; on track E it is
downloaded. The other exercises run in the playground, as on `basics/programming-1`.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `base-class` | base class | parent class |
| `c-reference` | C++ reference | - |
| `class` | class | - |
| `compile-error` | compile error | compiler error |
| `compile-time` | compile time | - |
| `constructor` | constructor | - |
| `declaration` | declaration | - |
| `derived-class` | derived class | subclass, child class |
| `header-file` | header file | - |
| `include-directive` | include directive | - |
| `inheritance` | inheritance | - |
| `member-function` | member function | method |
| `null-pointer` | null pointer | - |
| `object` | object | - |
| `optional-value` | optional value | - |
| `pointer` | pointer | - |
| `source-file` | source file | source asset |
| `template-argument` | template argument | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-2 | must | order | `basics/programming-1`, `basics/programming-3` on track E | Track E reads `basics` right after `start` and never reads `make/first-script`, so its rules for script classes reach no page of track E before part `scripting`: a field is registered with `ST_SCRIPT_FIELD`; `ST_SCRIPT_CLASS` stands once per class, in a `.cpp`; setup goes in `OnCreate`, because the module constructs one instance without an entity; a build during Play reloads the module and runs `OnReload` in place of `OnCreate`. `start/first-game` names the macros and says that `basics/programming-3` teaches them, and `basics/programming-3` leaves them to `make/first-script`. Yet the E reader adds the field `IsGold` on `basics/programming-1` and splits `Coin` into `Coin.h` and `Coin.cpp` on `basics/programming-3`, where a registration left in the header fails the module's load with "class 'Coin' is registered twice". | `basics/programming-3`'s section on files of code takes the registration as files of code see it, on every track: `ST_SCRIPT_CLASS` in the class's `.cpp` and the message when a header holds it, each field listed with `ST_SCRIPT_FIELD`, and why setup is in `OnCreate` (`use` rows of `gamedev:523` and `scripting:470`, about 200 words). `basics/programming-1` adds for track E the two lines that add a field and one rule of the loop: stop, build, Play again, because a build during Play runs `OnReload`, not `OnCreate` (about 80 words). | `tracks.md:29`, `:221-228`; `allocation/start.md:250-252`; `allocation/basics-a.md:178-179`, `:185`, `:330-332`, `:341`, `:379`; `allocation/make-a.md:842-846`; `StrataScriptCore/Include/StrataScript/Script.h:49-52`, `:68-69`, `:842-852`; `Strata/src/Strata/Scripting/ScriptModule.cpp:980-983` |
| critic-basics-a-6 | must | missing-item | `basics/programming-3` (`new:70`) | The page has the reader write headers (`Coin.h`, a `Counter` class, `BobbingCoin` built on `Coin`), but no page of the plan teaches `#pragma once` or include guards. A header that one source file includes twice, directly and through another header, defines its class twice, and the build stops with a redefinition error. Every header of the samples and of the SDK starts with `#pragma once`, and AGENTS.md asks it of every header. | The section on files of code adds `#pragma once` as the first line of every header, with the error it prevents shown once (about 100 words); `basics/build` names include guards as the older form in one sentence beside translation units. | `allocation/basics-a.md:321-323`, `:363`, `:366-367`; a search of `allocation/*.md` for "pragma once" and "include guard" finds nothing; `Samples/Tetris/Scripts/TetrisGame.h:1`; `StrataScriptCore/Include/StrataScript/Script.h:1`; `AGENTS.md:150` |
| critic-basics-a-12 | should | thin-home | `basics/programming-3` (`new:71`) | Track G learns C++ only on `basics/programming-1` to `-3`, and `-3` promises that the reader can then read `reference/script-api`, which shows the SDK's declarations. They use words that no page of track G teaches: `std::string_view` 87 times in 10 headers (nearly every name an SDK function takes), `uint32_t` and `uint64_t` (71 and 47; `GetGamepadAxis`, which `basics/programming-2` quotes, takes a `uint32_t gamepad`), `template<typename T>` before a declaration (24), `explicit` (16), `[[maybe_unused]]` on the callbacks of `Script` (15), `constexpr` (12) and `= default` (8). `std::string_view` is taught only on `basics/cpp-modern` and the integer sizes only on `basics/numbers`, both off track G. | The section on reading a declaration adds a short table of these words, one sentence each for reading: what a `std::string_view` parameter accepts, and that one a callback receives is copied into a `std::string` to be kept; "u" and the bits in `uint32_t`; `template<typename T>` as the line before a template; the rest; each with its home on tracks B and E linked (about 200 words). | `allocation/basics-a.md:323-327`; `tracks.md:80-85`; `allocation/reference.md:3-16`; counted by `docs-work/C2/critic-basics-a/sdk_features.py` over `StrataScriptCore/Include/StrataScript/*.h` without `ScriptABI.h` and the `Detail` namespaces; `StrataScriptCore/Include/StrataScript/Input.h:328`; `StrataScriptCore/Include/StrataScript/Scene.h:24` |
| critic-basics-a-13 | should | thin-home | `basics/programming-3` (`new:63`, `new:73`) | The Covers says that a derived script's base fields "still show in the editor". At the pin nothing is inherited: each class's `ST_SCRIPT_CLASS` block runs alone, so `BobbingCoin` shows `DegreesPerSecond` only if its own block lists `ST_SCRIPT_FIELD(DegreesPerSecond)`, which `Field` accepts because the member belongs to a base. And `GetScript<Coin>()` returns `nullptr` on an entity whose script is a `BobbingCoin`: the engine finds a script by its exact class name. | The inheritance paragraph and the Coin Run item state both facts, with the line that lists the base's field (about 80 words). | `allocation/basics-a.md:315-316`, `:356`, `:366`; `StrataScriptCore/Include/StrataScript/Script.h:779-786`, `:802-808`, `:816-828`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:962-969` |
| critic-basics-a-17 | should | missing-item | `basics/programming-3` (`new:72`) | Reading compile errors teaches the first error first, at its file and line. The errors the SDK raises on purpose break that rule: a `double` field, a script class that is not default constructible, or `GetScript` on a class that is no script fail a `static_assert` whose first line points into `Script.h`, and the reader's own line is in the notes that follow ("required from here", "see reference to ... being compiled"). `basics/programming-1` teaches `double` and that a field is a variable the editor shows, so a `double` field is a likely first attempt. | The section shows one such error (a `double` field: "Unsupported script field type") from MSVC and from GCC or Clang, and how to find one's own line in its notes; the list of field types stays `make/script-fields`' (critic-scripting-14) and is linked (about 120 words). | `allocation/basics-a.md:167-169`, `:327-328`, `:365`; `StrataScriptCore/Include/StrataScript/Script.h:594-595`, `:784-786`, `:819`; `allocation/completeness.md:351` |
