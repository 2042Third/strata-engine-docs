# Brief: `basics/cpp-classes`

| Field | Value |
| --- | --- |
| Title | C++ classes in depth: inheritance, virtual calls and interfaces |
| Kind | P |
| Size | M |
| Tracks | B, E |
| Needs | `basics/cpp-memory` |
| From | new by split of `basics/cpp`; inheritance, `virtual` and `override`, interfaces (one interface with a virtual call), operators; type erasure is `basics/cpp-generic`'s |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/cpp-classes` — C++ classes in depth: inheritance, virtual calls and interfaces

**Covers.** The page extends the inheritance that `basics/programming-3` used for `override`. Inheritance in depth:
`public`, `protected` and `private` members, and the order in which the constructors and destructors of a base and a
derived class run. Virtual functions: a call through a base pointer or reference reaches the derived class's function;
`virtual`, `override` and `final`; the SDK's `Script` with its virtual callbacks as the first example. How a virtual
call works: one table of functions per class and a hidden pointer in each object, drawn, and what the call costs (one
more memory read, no inlining). Pure virtual functions (`= 0`), abstract classes, and interfaces: one interface with two
implementations and a virtual call, which is how an engine lets a lower layer call code written above it (`Window`,
`EngineModule`, an undo step as examples named for the parts that teach them). Virtual destructors, and deleting through
a base pointer. Polymorphism, and slicing (a derived object copied into a base value loses its own part). Operator
overloading: `+`, `==` and `[]` for one's own types, glm's vector operators as the example, and a defaulted `==`.
Enough to read a test framework's macros, which make classes that derive from one base. The Practice runs in the
playground's script, from easy to hard: the order of constructors and destructors predicted, then run; a call with and
without `virtual`; slicing; operators for a small struct; it ends with the optional Coin Run item: a base class
`Pickup` with a virtual `OnCollected`, and `Coin` and a new `SpeedBoost` derived from it, called through a `Pickup*`.

**Leaves out.**

- Templates, and type erasure without inheritance → `basics/cpp-generic`
- Strata's interfaces and registries as architecture → `core/layers-registries`
- The engine module interface → `core/engine-modules`
- Windows, events and layers → `core/windows-events`
- How the SDK detects which callbacks a script overrides → `scripting/abi-sdk`

**Fit.** `fits`: about 3,950 words against M (3,000). Eight ideas with sketches and the drawing of a table of
functions (about 2,650), and the common mistakes, the Practice's four exercises, the Coin Run item and the fixed parts
(about 1,300); virtual calls and interfaces take the most, and the page stands about 50 words under M's top.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:131` | concept | home | Inheritance in depth: access, and the order of constructors and destructors. General knowledge. |
| `new:132` | concept | home | Virtual functions: a call through a base pointer, `virtual`, `override`, `final`. General knowledge. |
| `new:133` | concept | home | How a virtual call works: a table of functions per class, a hidden pointer per object, the cost. General knowledge. |
| `new:134` | concept | home | Pure virtual functions, abstract classes and interfaces; an interface that lets lower code call higher code. General knowledge. |
| `new:135` | concept | home | Virtual destructors. General knowledge. |
| `new:136` | concept | home | Polymorphism and slicing. General knowledge. |
| `new:137` | concept | home | Operator overloading, glm's operators, a defaulted `==`. General knowledge. |
| `new:138` | hands-on | home | Optional practice on Coin Run: `Pickup` with a virtual `OnCollected`, `Coin` and `SpeedBoost` derived from it. General knowledge. |
| `new:218` | hands-on | home | Practice before the Coin Run item, in the playground's script, from easy to hard: Basic, predict then run: the order of a base's and a derived class's constructor and destructor logs; Medium: one call through a base reference, with and without `virtual`; Medium, predict then run: a derived object copied into a base value, and what its virtual call logs (slicing); Hard: `operator+` and a defaulted `==` for a small `Money` struct. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `scripting:105` | feature | use | The `Script` base class and its virtual callbacks as the first example |
| `foundation:348` | code | link | `EngineModule.h`, an interface with virtual hooks, linked to `core/engine-modules` |
| `foundation:350` | code | link | `Event.h`, a base class and its derived events, linked to `core/windows-events` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Inheritance and `override` at the script's level | `basics/programming-3` | must |
| Pointers, references, destructors and ownership | `basics/cpp-memory` | must |

**Starting state.** The end state of `make/project-coin-run`, downloaded on track E, from which the optional Coin Run
item of the Practice starts. The other exercises run in the playground's script.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `abstract-class` | abstract class | - |
| `interface` | interface | - |
| `operator-overloading` | operator overloading | - |
| `polymorphism` | polymorphism | - |
| `pure-virtual-function` | pure virtual function | - |
| `virtual-function` | virtual function | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-14 | should | stale-item | `basics/cpp-classes` (`new:138`) | The Coin Run item calls `OnCollected` "through a `Pickup*`". The natural way to get one, `GetScript<Pickup>()`, returns `nullptr` for a `Coin` or a `SpeedBoost`, because `GetScript` asks the engine for the class registered under `T`'s own name. A solution written that way compiles and collects nothing. | The item gets the pointer from `GetScript<Coin>()` or `GetScript<SpeedBoost>()` and converts it to `Pickup*`, which is the derived-to-base conversion the page teaches; `Pickup` itself is not registered with `ST_SCRIPT_CLASS` (about 60 words). | `allocation/basics-a.md:824-825`, `:850`; `StrataScriptCore/Include/StrataScript/Script.h:816-828`; `Strata/src/Strata/Scripting/ScriptHostAPI.cpp:962-969` |
