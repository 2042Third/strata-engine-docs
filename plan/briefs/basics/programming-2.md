# Brief: `basics/programming-2`

| Field | Value |
| --- | --- |
| Title | Programming from zero II: loops, functions, lists and structs |
| Kind | P |
| Size | L |
| Tracks | G, B, E |
| Needs | `basics/programming-1` |
| From | new; curricula 1.1; loops, functions, parameters and return values, static member functions called as `Input::IsActionDown`, `std::vector` and `std::array`, structs, `std::string` with `std::to_string` and `std::stoi`; Coin Run checkpoint: a function and a loop that line coins up, with the lines that request and instantiate the prefab given |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/programming-2` — Programming from zero II: loops, functions, lists and structs

**Covers.** The same playground. Loops: `while` with its condition checked before each turn, and why a loop that never
ends freezes the editor, which logs nothing (the call cannot be stopped; the engine has a watchdog that would log it,
but only tests turn it on, `scripting/crash-containment`; so the editor must be closed, and recovery is
`make/project-files`'); `for` that counts from 0 while `i < count`, and the range-based `for` over a list. Functions: a
name, parameters with types, a body and a return value; calling one with arguments; arguments copied into parameters;
local variables that start over at each call, unlike fields; `void`. Default arguments and functions that share a name
with other parameters, read on `Scene::Instantiate`'s four forms. Static member functions called through a type's name
and `::`, as `Input::IsActionDown("Jump")` and `Input::GetGamepadAxis(axis, 0)` with its default dead zone. Lists:
`std::array<float, 3>` with indexes from 0 and reading past the end as a mistake; `std::vector` with `push_back`, `size`
and a loop over it. Structs: values grouped under one name, members reached with `.`, and `glm::vec3` as the struct of
`x`, `y` and `z`. Text: `std::string`, joining with `+`, comparing with `==`, `std::to_string` (numbers turned into
text) and `std::stoi` (text turned into a number); `std::stoi` on text that is no number throws an exception, and the
editor then turns that script off on its entity (named here, explained by `scripting/crash-containment`). Common
mistakes: a loop off by one, a function that forgets to return, changing a parameter and expecting the caller's variable
to change. The Practice runs in the playground's script, from easy to hard: a `for` loop's output predicted, then run; a
function with a default argument; a `std::vector` summed; numbers turned into text and back; it ends with the Coin Run
item: a function `PlaceCoin` and a loop that line coins up, with the lines that request and instantiate the prefab
given. The coin prefab is asked for in `OnCreate` and the loop runs once it is loaded, because `Instantiate` never waits
for an asset and returns a null entity until it is loaded (the page says so in two sentences; asking early is
`make/scripting-scene`'s use home).

**Leaves out.**

- Classes, references, pointers and `std::optional` → `basics/programming-3`
- Asking for assets early and finding entities → `make/scripting-scene`
- Exceptions in C++ → `basics/cpp-modern`
- What an exception and a crash do to a script → `scripting/crash-containment`
- What lists cost, and other data structures → `basics/data-structures`, `basics/trees-graphs`
- The standard containers in depth → `basics/cpp-generic`

**Fit.** `fits`: about 5,400 words against L (5,000). Nine ideas from zero run in the script, with the quotes of
`Scene.h` and `Input.h` (about 3,950), and the common mistakes, the Practice's four exercises, the Coin Run item with
its given lines and the fixed parts (about 1,450); functions, loops and text take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:47` | concept | home | `while` loops; a loop that never ends freezes the editor, which logs nothing: the engine's watchdog is off unless a host sets a timeout, and only tests set one (`scripting/crash-containment`); close the editor, and recovery is `make/project-files`'. Evidence: `Strata/src/Strata/Scripting/ScriptEngine.cpp:35`, `Strata/src/Strata/Scripting/ScriptEngine.cpp:257-266`, `Strata/src/Strata/Scripting/ScriptWatchdog.h:16-18`, `Docs/Architecture.md:1415`; `git grep -n SetWatchdogTimeout 822a7a46` finds the call only in `StrataTests/src/Scripting/ScriptFaultTests.cpp` and `StrataTests/src/Scripting/ScriptModuleTests.cpp` |
| `new:48` | concept | home | `for` loops that count from 0, and the range-based `for` over a list. General knowledge. |
| `new:49` | concept | home | Functions: name, parameters, body, return value; calling with arguments; arguments copied. General knowledge. |
| `new:50` | concept | home | Local variables and their scope, against fields that keep their values. General knowledge. |
| `new:51` | concept | home | Default arguments, and functions that share a name with other parameters. General knowledge. |
| `new:52` | code | home | `StrataScriptCore/Include/StrataScript/Scene.h:177-186`: `Scene::Instantiate` by path, with default arguments |
| `new:53` | concept | home | Static member functions called through the type's name and `::`, with default arguments (`GetGamepadAxis`). Evidence: `StrataScriptCore/Include/StrataScript/Input.h:328` |
| `new:54` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:380-388`: `Input::IsActionDown`, a static member function with its comment |
| `new:55` | concept | home | `std::array`, indexes from 0, reading past the end. General knowledge. |
| `new:56` | concept | home | `std::vector`: `push_back`, `size`, a loop over it. General knowledge. |
| `new:57` | concept | home | Structs and members; `glm::vec3` as a struct of three floats. General knowledge. |
| `new:58` | concept | home | `std::string`: joining, comparing, `std::to_string` and `std::stoi`, and the exception of `std::stoi`. General knowledge. |
| `new:59` | hands-on | home | Coin Run practice: `PlaceCoin` and a loop that line coins up; the lines that request and instantiate the prefab are given: `Assets::Find` and `Assets::RequestLoad` in `OnCreate`, a check of `Assets::IsLoaded`, then `Scene::Instantiate` with a `bool` so that the loop runs once, because `Instantiate` never waits. Evidence: `StrataScriptCore/Include/StrataScript/Scene.h:18-42`, `StrataScriptCore/Include/StrataScript/Scene.h:152-156` |
| `new:213` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: what a `for` loop logs from 0 while `i < 3`, and the extra turn that `<=` gives; Medium: a function `Clamp` with a default argument, called with and without it; Medium: the speeds of a `std::vector<float>` summed in a range-based `for` and logged; Hard, faded examples: a score turned into text with `std::to_string` and back with `std::stoi`, three times with less help each time, the last on text that is no number, predicted before the run. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scripting:121` | feature | use | `Assets::Find`, `Assets::RequestLoad`, `Assets::IsLoaded` and `Scene::Instantiate`, the given lines of the practice |
| `scripting:122` | feature | use | `Input`'s static member functions |
| `scripting:176` | feature | use | The watchdog, named as on only in tests, so that in the editor an endless loop freezes it and logs nothing |
| `scripting:190` | feature | use | An exception switches off one instance, named for `std::stoi` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Values, variables, expressions, `if` and namespaces | `basics/programming-1` | must |
| The coin as a prefab | `make/prefabs` | helps |
| A position as three numbers (x, y, z) | `make/transforms-units` | helps |
| Recovery after the editor was closed | `make/project-files` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin Run
lit for play, its five instances of `Prefabs/Coin.stprefab` spinning by the reader's `Coin` script; on track E it is
downloaded. The practice gives the lines that request and instantiate the prefab (`book.md`'s running examples):
`Assets::Find("Prefabs/Coin.stprefab")` and `Assets::RequestLoad` in `OnCreate`, a check of `Assets::IsLoaded` in
`OnUpdate`, and `Scene::Instantiate` with a `bool` so that the loop runs once
(`StrataScriptCore/Include/StrataScript/Scene.h:18-42`, `:152-156`). The other exercises run in the playground, as on
`basics/programming-1`.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `array` | array | std::array |
| `array-index` | array index | - |
| `dynamic-array` | dynamic array | std::vector |
| `for-loop` | for loop | - |
| `function` | function | - |
| `function-argument` | function argument | - |
| `function-call` | function call | - |
| `local-variable` | local variable | - |
| `loop` | loop | - |
| `member` | member | - |
| `parameter` | parameter | - |
| `return-value` | return value | - |
| `static-member-function` | static member function | - |
| `string` | string | text string, std::string |
| `struct` | struct | - |
| `while-loop` | while loop | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-1 | must | missing-item | `new:59` on `basics/programming-2`; the playground of `basics/programming-1` to `basics/debugging` on tracks G and B | On tracks G and B the playground is the reader's `Coin` script, which runs on all five instances of the coin prefab. Every line a practice logs in `OnCreate` appears five times. Worse, the Coin Run item of `basics/programming-2` puts a loop that instantiates the coin prefab into that script: every coin it makes carries the same script, runs `OnCreate` and makes coins again, so their number grows every frame until the editor stalls. style.md defines the playground as a project whose one script moves one entity. | On tracks G and B the playground is a script of its own (`Playground`, made with **Scripts ▸ New Script...**) on one new empty entity of Coin Run, as style.md §8 asks; the Starting state of the five pages says so (about 40 words on `basics/programming-1`). `new:59` puts `PlaceCoin` and its loop in a new script `CoinLine` on its own empty entity, with one sentence on why it never goes into `Coin` (about 80 words). | `allocation/basics-a.md:158-160`, `:229-230`, `:248-253`, `:284`, `:300-306`; `allocation/make-a.md:829-830`; `style.md:616-617`; `StrataScriptCore/Include/StrataScript/Scene.h:152-156` |
| critic-basics-a-12 | should | thin-home | `basics/programming-3` (`new:71`) | Track G learns C++ only on `basics/programming-1` to `-3`, and `-3` promises that the reader can then read `reference/script-api`, which shows the SDK's declarations. They use words that no page of track G teaches: `std::string_view` 87 times in 10 headers (nearly every name an SDK function takes), `uint32_t` and `uint64_t` (71 and 47; `GetGamepadAxis`, which `basics/programming-2` quotes, takes a `uint32_t gamepad`), `template<typename T>` before a declaration (24), `explicit` (16), `[[maybe_unused]]` on the callbacks of `Script` (15), `constexpr` (12) and `= default` (8). `std::string_view` is taught only on `basics/cpp-modern` and the integer sizes only on `basics/numbers`, both off track G. | The section on reading a declaration adds a short table of these words, one sentence each for reading: what a `std::string_view` parameter accepts, and that one a callback receives is copied into a `std::string` to be kept; "u" and the bits in `uint32_t`; `template<typename T>` as the line before a template; the rest; each with its home on tracks B and E linked (about 200 words). | `allocation/basics-a.md:323-327`; `tracks.md:80-85`; `allocation/reference.md:3-16`; counted by `docs-work/C2/critic-basics-a/sdk_features.py` over `StrataScriptCore/Include/StrataScript/*.h` without `ScriptABI.h` and the `Detail` namespaces; `StrataScriptCore/Include/StrataScript/Input.h:328`; `StrataScriptCore/Include/StrataScript/Scene.h:24` |
| critic-basics-a-26 | could | missing-item | `basics/programming-2` (`new:57`) | Structs are taught as values that copy, but the SDK mixes two kinds of object that look alike: `Entity` and `TransformComponent` are handles that name engine data, so a copy still changes the same entity, while `GetTranslation()` returns a `glm::vec3` value, so `p.y += 1` on it moves nothing until `SetTranslation(p)`. The Spinner's own lines use both. | One worked example in the structs section: a handle copied, a value copied, and the write-back (about 100 words); `make/scripting-scene` keeps its use. | `allocation/basics-a.md:243-244`, `:247-248`; `StrataScriptCore/Include/StrataScript/Entity.h:26-27`, `:160-175`; `StrataEditor/src/Editor/ScriptProject.cpp:246-250` |
| critic-basics-a-27 | could | missing-item | `basics/programming-2` (`new:47`) | An endless loop freezes the editor and "the editor must be closed", but a frozen window does not close from its own button. Track G reads this page without `basics/computer`, which teaches the system's process viewer. | One sentence per OS: Task Manager's End task, Force Quit (Cmd+Option+Esc), the System Monitor's End Process or `kill` (about 50 words). | `allocation/basics-a.md:234-237`, `:272`; `tracks.md:77-85`; `style.md:41-44` |
