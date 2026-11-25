# Brief: `basics/programming-1`

| Field | Value |
| --- | --- |
| Title | Programming from zero I: values, variables, expressions and decisions |
| Kind | P |
| Size | L |
| Tracks | G, B, E |
| Needs | `make/first-script`\|`start/first-game` |
| From | new; curricula 1.1; values and types, variables, expressions, `if` and `switch`, each idea run in a script; names in a namespace such as `Key::Space`, and scoped enum values such as `CursorMode::Locked`; namespaces and `::` (`using namespace Strata;`, `glm::`); learncpp lessons linked per section; Coin Run checkpoint: the coins' spin speed in a variable, and an `if` that spins a gold coin faster |
| Unit | `plan/allocation/basics-a.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `basics/programming-1` — Programming from zero I: values, variables, expressions and decisions

**Covers.** The reader has never programmed. The playground is a Strata script: on tracks G and B the reader's own
`Coin` script from `make/first-script`, on track E the `Spinner` of `start/first-game`; output goes to the log (the
Console) and to the coin that turns. Each section links its learncpp lesson. In order: a program as steps that run in
order, source code, and the script as the frame the page fills in: `OnCreate` runs once, `OnUpdate` every frame, and
the class around them is read as a frame here and taught on `basics/programming-3` (a script at the use level: a class
and calls into the SDK). Statements end with `;`, braces group them, `//` starts a comment. The first call into the
SDK: `Log::Info` takes its pieces separated by commas and joins them (it is not a format string), so
`Log::Info("Speed: ", speed)` prints both; `true` and `false` print as words, a `glm::vec3` as `(x, y, z)`; `Trace`,
`Warn` and `Error` are named as the class's other levels, and `reference/script-api` lists its declarations. Values and
types: `int`, `float` with the `f` of `90.0f`, `double`, `bool`, text in double quotes, and `int32_t` named as the
whole number that fields use (its size is `basics/numbers`'). Variables: declare with a type and a first value, assign,
names that say what they hold, `const`; a field is a variable that the editor shows. Expressions: arithmetic, the order
of operations, integer division and `%`, mixing `int` and `float`, `+=` and `++`. Comparisons give a `bool`; `&&`, `||`
and `!` join them. Decisions: `if`, `else if`, `else`, and blocks with their scope (a variable lives inside its braces).
Namespaces and `::`: `Strata::`, `glm::vec3`, `glm::radians`, `using namespace Strata;`, and `Key::Space`, a name inside
the namespace `Key`, used with `Input::IsKeyDown(Key::Space)` in an `if`. Scoped enumerations: `enum class` with
values written after the type's name and `::` (`CursorMode::Locked`, shown from `Input.h`), and `switch` with `case`,
`break` and `default`. Common mistakes: `=` in place of `==`, a missing `;`, integer division where a fraction was
meant, a variable used outside its braces. The Practice runs in the playground's script, from easy to hard: integer
and float division predicted, then run; a `const` speed changed; the lines of an `if` and its `else` put in order; a
`switch` whose missing `break` shows in the output; it ends with the Coin Run item: the spin speed in a variable, and
a `bool` field `IsGold` ticked on one coin in the Inspector with an `if` that spins that coin faster.

**Leaves out.**

- Loops, functions, lists, structs and text → `basics/programming-2`
- Classes, references, pointers, files of code and reading errors → `basics/programming-3`
- What is special to script code (`override`, `ST_SCRIPT_CLASS`, `ST_SCRIPT_FIELD`) → `make/first-script`
- Binary, the sizes and ranges of integer types, floating-point precision → `basics/numbers`
- Vectors and the turn in the spin's line as mathematics → `basics/math-vectors`, `basics/math-rotations`
- Finding bugs with the log and a debugger → `basics/debugging`

**Fit.** `fits`: about 5,500 words against L (5,000). Ten ideas from zero, each run in the script with its output,
with the quotes of `Log.h` and `Input.h` (about 4,150), and the common mistakes, the Practice's four exercises, the
Coin Run item and the fixed parts (about 1,350); values and types, expressions and decisions take the most.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `new:34` | concept | home | A program as steps in order, source code, and the script as the playground: `OnCreate` once, `OnUpdate` every frame. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:30-33` |
| `new:35` | concept | home | Statements and `;`, braces, comments. General knowledge. |
| `new:36` | code | home | `StrataScriptCore/Include/StrataScript/Log.h:58-73`: `Log` joins its arguments ("Arguments are concatenated") and has four levels |
| `new:37` | concept | home | Values and types: `int`, `float` and its `f`, `double`, `bool`, text in quotes; `int32_t` named. General knowledge. |
| `new:38` | concept | home | Variables: declare, give a first value, assign, name, `const`; a field as a variable the editor shows. General knowledge. |
| `new:39` | concept | home | Expressions and arithmetic operators, the order of operations, integer division and `%`, `+=` and `++`. General knowledge. |
| `new:40` | concept | home | Comparison operators, `bool`, and the logical operators `&&`, `\|\|` and `!`. General knowledge. |
| `new:41` | concept | home | `if`, `else if`, `else`; blocks and scope. General knowledge. |
| `new:42` | concept | home | Namespaces and `::`: `Strata::`, `glm::`, `using namespace`; `Key::Space` as a name in the namespace `Key`. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:16-24` |
| `new:43` | concept | home | Scoped enumerations (`enum class`) and `switch` with `case`, `break` and `default`. General knowledge. |
| `new:44` | code | home | `StrataScriptCore/Include/StrataScript/Input.h:212-217`: `CursorMode`, a scoped enumeration of the SDK |
| `new:45` | erratum | home | The outline's row wrote "scoped enum values written as `Key::Space`" until R30 (D6) corrected it. At the pin `Key` is a namespace whose unnamed enum has the type `KeyCode` (`uint16_t`), so `Key::Space` is a name in a namespace; the SDK's scoped enumerations are `CursorMode`, `GamepadButton`, `WindowMode` and others. The page teaches both and never calls `Key::Space` a scoped enum value. Evidence: `StrataScriptCore/Include/StrataScript/Input.h:16-24`, `StrataScriptCore/Include/StrataScript/Input.h:212-217` |
| `new:46` | hands-on | home | Coin Run practice: the spin speed in a variable, a `bool` field `IsGold` and an `if` that spins the gold coin faster, from `make/first-script`'s checkpoint. Evidence: `StrataScriptCore/Include/StrataScript/Script.h:854-856` |
| `new:212` | hands-on | home | Practice before the Coin Run item, run in the playground's script and read in the Console, from easy to hard: Basic, predict then run: what `Log::Info` prints for `7 / 2`, `7 % 2` and `7 / 2.0f`; Basic, modify: a `const float` speed doubled and the spin watched; Medium, a Parsons problem: the shuffled lines of an `if`, `else if` and `else` that log "slow", "fast" or "very fast" for a speed; Hard: a `switch` on a whole number with `case`, `break` and `default` that logs one word per value, and a missing `break` found from the output. Evidence: `StrataScriptCore/Include/StrataScript/Log.h:58-73` |
| `gamedev:359` | code | use | The generated `Spinner`, read again line by line as values, a variable and an expression |
| `scripting:105` | feature | use | The `Script` base class, as the frame the page writes in |
| `scripting:124` | feature | home | `Log`, the first class of the SDK the reader calls: `Log::Info` writes to the Console, its arguments joined in order (no format string), `true` and `false` as words and a `glm::vec3` as `(x, y, z)`; `Trace`, `Warn` and `Error` are named as its other levels, which `basics/debugging` uses; its declarations are linked to `reference/script-api` |
| `scripting:122` | feature | use | `Input::IsKeyDown` in an `if` |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| Editing a script in the code editor, building with **Ctrl+B**, Play, and reading `Log::Info` in the Console | `start/first-game` | must |
| How to read code you do not understand yet | `start/how-to-read` | helps |
| Coin Run's `Coin` script and its `DegreesPerSecond` field | `make/first-script` | helps |
| A rotation as an axis and an angle, in degrees and radians | `make/transforms-units` | helps |
| Memory as numbered cells | `basics/computer` | helps |

**Starting state.** The end state of `make/first-script`, from which the Coin Run item of the Practice starts: Coin
Run lit for play, its five coin instances spinning by the reader's `Coin` script and its `DegreesPerSecond` field; on
track E it is downloaded. The other exercises run in the playground: on tracks G and B the reader's own `Coin` script,
on track E the `Spinner` of `start/first-game`'s project.

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `assignment` | assignment | - |
| `boolean` | boolean | - |
| `comparison-operator` | comparison operator | - |
| `condition` | condition | - |
| `expression` | expression | - |
| `if-statement` | if statement | - |
| `logical-operator` | logical operator | - |
| `namespace` | namespace | - |
| `operator` | operator | - |
| `scope` | scope | - |
| `scoped-enumeration` | scoped enumeration | enum class, scoped enum |
| `statement` | statement | - |
| `switch-statement` | switch statement | - |
| `type` | type | data type |
| `value` | value | - |
| `variable` | variable | - |

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-basics-a-1 | must | missing-item | `new:59` on `basics/programming-2`; the playground of `basics/programming-1` to `basics/debugging` on tracks G and B | On tracks G and B the playground is the reader's `Coin` script, which runs on all five instances of the coin prefab. Every line a practice logs in `OnCreate` appears five times. Worse, the Coin Run item of `basics/programming-2` puts a loop that instantiates the coin prefab into that script: every coin it makes carries the same script, runs `OnCreate` and makes coins again, so their number grows every frame until the editor stalls. style.md defines the playground as a project whose one script moves one entity. | On tracks G and B the playground is a script of its own (`Playground`, made with **Scripts ▸ New Script...**) on one new empty entity of Coin Run, as style.md §8 asks; the Starting state of the five pages says so (about 40 words on `basics/programming-1`). `new:59` puts `PlaceCoin` and its loop in a new script `CoinLine` on its own empty entity, with one sentence on why it never goes into `Coin` (about 80 words). | `allocation/basics-a.md:158-160`, `:229-230`, `:248-253`, `:284`, `:300-306`; `allocation/make-a.md:829-830`; `style.md:616-617`; `StrataScriptCore/Include/StrataScript/Scene.h:152-156` |
| critic-basics-a-2 | must | order | `basics/programming-1`, `basics/programming-3` on track E | Track E reads `basics` right after `start` and never reads `make/first-script`, so its rules for script classes reach no page of track E before part `scripting`: a field is registered with `ST_SCRIPT_FIELD`; `ST_SCRIPT_CLASS` stands once per class, in a `.cpp`; setup goes in `OnCreate`, because the module constructs one instance without an entity; a build during Play reloads the module and runs `OnReload` in place of `OnCreate`. `start/first-game` names the macros and says that `basics/programming-3` teaches them, and `basics/programming-3` leaves them to `make/first-script`. Yet the E reader adds the field `IsGold` on `basics/programming-1` and splits `Coin` into `Coin.h` and `Coin.cpp` on `basics/programming-3`, where a registration left in the header fails the module's load with "class 'Coin' is registered twice". | `basics/programming-3`'s section on files of code takes the registration as files of code see it, on every track: `ST_SCRIPT_CLASS` in the class's `.cpp` and the message when a header holds it, each field listed with `ST_SCRIPT_FIELD`, and why setup is in `OnCreate` (`use` rows of `gamedev:523` and `scripting:470`, about 200 words). `basics/programming-1` adds for track E the two lines that add a field and one rule of the loop: stop, build, Play again, because a build during Play runs `OnReload`, not `OnCreate` (about 80 words). | `tracks.md:29`, `:221-228`; `allocation/start.md:250-252`; `allocation/basics-a.md:178-179`, `:185`, `:330-332`, `:341`, `:379`; `allocation/make-a.md:842-846`; `StrataScriptCore/Include/StrataScript/Script.h:49-52`, `:68-69`, `:842-852`; `Strata/src/Strata/Scripting/ScriptModule.cpp:980-983` |
| critic-basics-a-8 | must | stale-item | `basics/numbers` (`new:87`, `new:216`) | The page says that integer division "rounds down" and gives `(a + b - 1) / b` as the rule that rounds up. C++ truncates toward zero: -7 / 2 is -3, not -4, and -7 % 2 is -1. Both rules hold only for a non-negative `a` and a positive `b`. Engines meet negative coordinates all the time: Strata floors its world cell coordinates and has its own `FloorDivide` for the GI grid for exactly this reason. | Teach division as truncation toward zero, the sign of `%`, floor division for negative values (the shape of `FloorDivide`) and the condition of the round-up rule; the Practice's division case gets a negative dividend, predicted then run (about 120 words). `basics/programming-1`'s `%` gets one sentence: a negative left operand gives a negative remainder. | `allocation/basics-a.md:170`, `:519-520`, `:573`, `:587`; `Strata/src/Strata/Renderer/GlobalIlluminationLayout.cpp:17-21`; `Strata/src/Strata/World/WorldGrid.cpp:20-22`; the C++ standard, [expr.mul] (the quotient is truncated toward zero) |
| critic-basics-a-11 | should | stale-item | `basics/debugging` (`new:75`, `gamedev:54`); `basics/programming-1` (`scripting:124`) | The log as a tool leans on "the Console's ... file and line that open the code". A script's own `Log` line carries no file and line: the SDK passes only the level and the text, and the Console opens only messages in a compiler's or a crash report's form. Two facts the method needs are missing: `Log::Trace` lines stay hidden until the Console's Trace box is ticked, and the Console keeps the last 4,096 lines, so a line logged every frame pushes the earlier ones out in about a minute (the log file keeps them). | Say that a log line names its place in its own text (the class and the callback), that build errors and crash reports are the lines that open the code, that Trace is off by default, and that the Console holds 4,096 lines while the file holds all (about 100 words); `basics/programming-1` says in one sentence that Trace lines need the box ticked. | `allocation/basics-a.md:165-166`, `:388-390`, `:427`, `:441`; `StrataScriptCore/Include/StrataScript/Log.h:74-83`; `StrataEditor/src/Panels/ConsolePanel.cpp:28`, `:66-70`, `:139-146`; `StrataEditor/src/Panels/ConsolePanel.h:45`; `StrataEditor/src/Editor/ScriptBuild.h:132-135`; `Strata/src/Strata/Core/Log.h:73`; `Strata/src/Strata/Core/Log.cpp:65-69` |
| critic-basics-a-12 | should | thin-home | `basics/programming-3` (`new:71`) | Track G learns C++ only on `basics/programming-1` to `-3`, and `-3` promises that the reader can then read `reference/script-api`, which shows the SDK's declarations. They use words that no page of track G teaches: `std::string_view` 87 times in 10 headers (nearly every name an SDK function takes), `uint32_t` and `uint64_t` (71 and 47; `GetGamepadAxis`, which `basics/programming-2` quotes, takes a `uint32_t gamepad`), `template<typename T>` before a declaration (24), `explicit` (16), `[[maybe_unused]]` on the callbacks of `Script` (15), `constexpr` (12) and `= default` (8). `std::string_view` is taught only on `basics/cpp-modern` and the integer sizes only on `basics/numbers`, both off track G. | The section on reading a declaration adds a short table of these words, one sentence each for reading: what a `std::string_view` parameter accepts, and that one a callback receives is copied into a `std::string` to be kept; "u" and the bits in `uint32_t`; `template<typename T>` as the line before a template; the rest; each with its home on tracks B and E linked (about 200 words). | `allocation/basics-a.md:323-327`; `tracks.md:80-85`; `allocation/reference.md:3-16`; counted by `docs-work/C2/critic-basics-a/sdk_features.py` over `StrataScriptCore/Include/StrataScript/*.h` without `ScriptABI.h` and the `Detail` namespaces; `StrataScriptCore/Include/StrataScript/Input.h:328`; `StrataScriptCore/Include/StrataScript/Scene.h:24` |
| critic-basics-a-17 | should | missing-item | `basics/programming-3` (`new:72`) | Reading compile errors teaches the first error first, at its file and line. The errors the SDK raises on purpose break that rule: a `double` field, a script class that is not default constructible, or `GetScript` on a class that is no script fail a `static_assert` whose first line points into `Script.h`, and the reader's own line is in the notes that follow ("required from here", "see reference to ... being compiled"). `basics/programming-1` teaches `double` and that a field is a variable the editor shows, so a `double` field is a likely first attempt. | The section shows one such error (a `double` field: "Unsupported script field type") from MSVC and from GCC or Clang, and how to find one's own line in its notes; the list of field types stays `make/script-fields`' (critic-scripting-14) and is linked (about 120 words). | `allocation/basics-a.md:167-169`, `:327-328`, `:365`; `StrataScriptCore/Include/StrataScript/Script.h:594-595`, `:784-786`, `:819`; `allocation/completeness.md:351` |
