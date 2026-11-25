---
id: basics/programming-1
title: "Programming from zero I: values, variables, expressions and decisions"
description: "Learn the first ideas of programming in a Strata script: values and types, variables, expressions, if chains, namespaces and switch."
kind: primer
size: L
tracks: [G, B, E]
needs: [make/first-script|start/first-game]
time: 105
learn:
  - id: script-frame
    text: name what a statement, a brace and a comment are, and when OnCreate and OnUpdate run
  - id: types-variables
    text: choose a type for a value and declare, assign and name a variable
  - id: expressions
    text: compute an expression, with the order of operations, integer division and the remainder
  - id: decisions
    text: write an if chain from comparisons and logical operators, and predict which branch runs
  - id: names-switch
    text: write a switch on a scoped enumeration and read a name with a double colon such as Key::Space
status: final
---

::::test-out

1. What does the line `Log::Info("Half: ", 7 / 2);` write to the Console?

   :::answer{tests="expressions"}
   `Half: 3`. Both numbers are whole numbers, so the division gives a whole number and drops the fraction 0.5.
   :::

2. Write one line that declares a variable `speed` with the value 90 and that no later line may change.

   :::answer{tests="types-variables"}
   `const float speed = 90.0f;`. The type is `float`, the `f` marks the number as a `float`, and `const` forbids a later
   assignment.
   :::

3. The variable `coins` holds 12. Which word does this code write: A, B or C?

   ```cpp pseudocode
   if (coins > 5 && coins < 10)
   	Log::Info("A");
   else if (coins > 5)
   	Log::Info("B");
   else
   	Log::Info("C");
   ```

   Test the conditions from the top, with 12 in `coins`.

   :::answer{tests="decisions"}
   B. The first condition needs both comparisons to be true, and `coins < 10` is false for 12. The second condition,
   `coins > 5`, is true, so its line runs and the `else` is skipped.
   :::

4. In `Input::IsKeyDown(Key::Space)`, what is `Key` and what is `Space`?

   :::answer{tests="names-switch"}
   `Key` is a namespace, a named group of names. `Space` is a name inside it, and `::` joins the two.
   :::

5. A script logs one line in `OnCreate` and one in `OnUpdate`. How many lines of each appear after 2 seconds of play at
   50 frames per second?

   :::answer{tests="script-frame"}
   One line from `OnCreate`, which runs once, and about 100 from `OnUpdate`, which runs every frame: 2 × 50.
   :::

::::

## Why you will need this

Every script is a program, and a program is built from a few small ideas: values, variables, expressions and
decisions. This page teaches them from nothing, one at a time, and you run each idea in a script of your own.

The ideas come back on every page that follows. [Programming 2](../basics/programming-2.md) adds loops and functions to
them. [Vectors](../basics/math-vectors.md) computes with them. [Debugging](../basics/debugging.md) finds the mistakes they
cause. At the end of this page you change your spinning script, the `Coin` of your first script or the `Spinner` of your
first game: it turns faster when you tick a box in the Inspector.

## A script is steps that run in order

Think of a recipe: crack the egg, stir, bake. Swap two steps and the cake changes. A program is a list of steps like
that, and the computer does them in the order written. The text of the steps is the :term[source code]{id=source-code}, which you write in a
code editor.

A game script cuts the list into pieces that the engine calls at set times.

:::question[What are the lines I have not seen yet?]
Functions are taught in [Programming 2](../basics/programming-2.md), classes, `#include` and calls in [Programming
3](../basics/programming-3.md), and inheritance and `override` in [Classes in C++](../basics/cpp-classes.md). Read the
class as a frame to complete and a call as "do this named job".
:::

The editor writes the script below into every new project, as `Scripts/Spinner.cpp`. Your file starts with five comment
lines that say how to attach the script, and the quote omits them. The numbers beside the lines are those of the
engine's file that holds the text. In your `Spinner.cpp` each line is 229 lower: line 238 is line 9.

The `Coin` of your first script holds the same code under its own name. Search for one variable, one function that the
engine calls and one registration.

```cpp src="StrataEditor/src/Editor/ScriptProject.cpp#L236-L257"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Turns its entity around the world's Y axis.
class Spinner : public Script
{
public:
	float DegreesPerSecond = 90.0f; // A field: editable per entity, kept across hot reloads

	void OnUpdate(float deltaTime) override
	{
		TransformComponent transform = GetTransform();
		const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
		transform.SetRotation(turn * transform.GetRotation());
	}
};

ST_SCRIPT_CLASS(Spinner)
{
	ST_SCRIPT_FIELD(DegreesPerSecond);
}
```

1. **Line 238:** `using namespace Strata;` lets the script write `Script` for the engine's `Strata::Script`.
2. **Line 244:** `DegreesPerSecond` holds a number, 90 at the start, and the editor shows it.
3. **Lines 246–251:** `OnUpdate` is the function the engine calls every frame; its three statements run from top to bottom.
4. **Lines 254–256:** the registration tells the engine the class and its field; [Your first
   script](../make/first-script.md) explains it.

A **statement** is one complete step, and in C++ it ends with `;`. Braces, `{` and `}`, group statements into a block: the
statements of `OnUpdate` stand between lines 247 and 251. Two slashes, `//`, start a comment: the rest of the line is for
human readers, and the computer skips it.

The engine calls the functions of a script at fixed moments. `OnCreate` runs once, when the entity starts playing and
before the first update. `OnUpdate` runs every frame, with `deltaTime`, the seconds since the last frame. A game at 50
frames per second calls `OnUpdate` 50 times each second.

```mermaid caption="The start function runs once when play begins; the update function runs again in every frame until you stop." alt="A flow of boxes. Press Play leads to the start function, which runs once. An arrow leads to the update function of frame one, then frame two, then the next frames. Press Stop ends the flow."
flowchart LR
    A["Press Play"] --> B["OnCreate (once)"]
    B --> C["OnUpdate: frame 1"]
    C --> D["OnUpdate: frame 2"]
    D --> E["OnUpdate: every next frame"]
    E --> F["Press Stop"]
```

## The playground is a script of your own

You work in the project that [Your first script](../make/first-script.md) left: Coin Run, whose five coins are
instances of the prefab `Prefabs/Coin.stprefab` and turn with your `Coin` script. The project of [Your first
game](../start/first-game.md) works too: there the cube `Top` turns with `Spinner`. If you have neither, download the
project at the last checkpoint of Your first script and open it.

A script runs once for every entity that carries it. Your spinning script sits on several coins or cubes, so a line it logs
would appear once for each. The exercises in this page therefore run in a
script of their own, on one entity.

::::tabs{sync=how}
:::tab[In the editor]

1. In the Hierarchy, press the plus button and choose **Empty**. You get one new entity.
2. Choose **Scripts ▸ New Script...** and name the class `Playground`. The editor writes a script with empty `OnCreate`
   and `OnUpdate` functions and a `float` field `Speed`, opens it, and starts a build.
3. Select the new entity, choose **Add Component ▸ Script** in the Inspector, and pick `Playground`.
4. Type statements between the braces of `OnCreate`, press **Ctrl+B** to build, press **Play**, and read the
   **Console**.

:::
:::tab[With a command]
The same steps as commands. `script.add` takes only a class that is built, so the build comes before it. The last two
lines stop the game and read the newest lines of the Console.

```json
{ "command": "entity.create", "parameters": { "name": "Playground" } }
{ "command": "script.create", "parameters": { "class": "Playground", "open": true } }
{ "command": "script.build" }
{ "command": "script.add", "parameters": { "entity": "<id of Playground>", "class": "Playground" } }
{ "command": "play.start" }
{ "command": "play.stop" }
{ "command": "log.read", "parameters": { "newest": true, "limit": 20 } }
```

:::
::::

To change the script, stop the game first: edit, build, then press **Play** again. A build during play reloads the
script and runs `OnReload` in place of `OnCreate`, so lines you wrote in `OnCreate` stay silent.

## `Log::Info` writes the pieces you give it

A script needs a way to show you a value. `Log::Info` writes a line to the **Console**, and `Log` is the first part of
the script library that you call. A call is a name followed by `(...)`; the pieces inside are its arguments.

:::question[What is the `template` line?]
A `template` line, taught in [Generic C++](../basics/cpp-generic.md), lets a function take any arguments, and the `&` in a
type makes a reference, taught in [Programming 3](../basics/programming-3.md); you only call the functions below.
:::

The class `Log` has one function for each level. Read its two comment lines first.

```cpp src="StrataScriptCore/Include/StrataScript/Log.h#L58-L73"
// Writes to the engine log (the editor console). Arguments are concatenated:
//   Log::Info("Player ", GetEntity().GetName(), " has ", health, " health at ", position);
class Log
{
public:
	template<typename... Args>
	static void Trace(const Args&... args) { Write(StrataScriptLogLevel_Trace, args...); }

	template<typename... Args>
	static void Info(const Args&... args) { Write(StrataScriptLogLevel_Info, args...); }

	template<typename... Args>
	static void Warn(const Args&... args) { Write(StrataScriptLogLevel_Warn, args...); }

	template<typename... Args>
	static void Error(const Args&... args) { Write(StrataScriptLogLevel_Error, args...); }
```

1. **Lines 58–59:** the comment is the rule: the arguments are joined in the order you write them, with nothing added
   between them. There is no format string.
2. **Lines 63–73:** four levels, one function each. `Info` is the everyday one; `Warn` and `Error` mark problems.

`Log::Info("Speed: ", 90.0f)` writes `Speed: 90`. A `bool` prints as the word `true` or `false`. A `glm::vec3` prints as
`(x, y, z)`, so `Log::Info(glm::vec3(1.0f, 2.0f, 3.0f))` writes `(1, 2, 3)`. Each Console line starts with the time in
seconds and the name `Script`, then your text.

The Console hides `Trace` lines until you tick its **Trace** box, and it keeps only the last 4,096 lines. A line logged
in `OnUpdate` appears in every frame, so it pushes older lines out in a minute or two. The script's own line carries no
file and line, so put the place in the text: `Log::Info("Playground.OnCreate: speed ", speed)`. [The script
reference](../reference/script-api.md) lists every declaration of `Log`.

:::example[Two lines in `OnCreate`]
Add these to `OnCreate` of `Playground`, build and play. The first line joins four pieces; the second shows a `bool`.

```cpp pseudocode
Log::Info("Playground.OnCreate: coins ", 3, ", gold ", false);
Log::Info("Playground.OnCreate: ", 2 + 3);
```

The Console shows `Playground.OnCreate: coins 3, gold false` and `Playground.OnCreate: 5`. The sum is computed before it
is written.
:::

:::example[Order matters]
A statement sees only what the statements above it did. Here `speed` is read twice, with a change between the reads.

```cpp pseudocode
float speed = 10.0f;
Log::Info("Before: ", speed);
speed = 20.0f;
Log::Info("After: ", speed);
```

The Console shows `Before: 10`, then `After: 20`. Swap the second and third lines and it shows `Before: 20`, because the change
now runs first.
:::

Try it: what does `Log::Info("a", 1, "b")` write?

:::answer
`a1b`. Nothing is added between the arguments, so there are no spaces.
:::

## A value has a type

A **value** is a piece of data that a program holds and works with: the number 90, the word "Coin", the answer yes.

Each value has a **type**, which says what kind of value it is and so what the computer may do with it. You cannot add
two words the way you add two numbers, and the type is how the computer knows.

The program below keeps four values and prints them. The `<<` signs do what the arguments of `Log::Info` do: join the
pieces in order. The sketch is a program of its own, so it prints with `std::cout`.

```cpp sketch="basics-programming-1-types.cpp"
// Values of four types, kept in variables, and what a chain of << prints for each.
#include <cstdint>
#include <iostream>

int main()
{
	std::cout << std::boolalpha; // print true and false as words, as Log::Info does

	int32_t coins = 3;   // a whole number
	float speed = 90.0f; // a number with a fraction; the f makes it a float
	double exact = 0.1;  // a number with a fraction, kept with more digits
	bool isGold = true;  // true or false

	coins = coins + 1; // assignment: the right side is computed first, then stored in coins
	speed = 2.5f;      // a new value replaces the old one

	std::cout << "Coins: " << coins << '\n';
	std::cout << "Speed: " << speed << '\n';
	std::cout << "Exact: " << exact << '\n';
	std::cout << "Gold: " << isGold << '\n';
	return 0;
}
```

```text output-of="basics-programming-1-types.cpp"
Coins: 4
Speed: 2.5
Exact: 0.1
Gold: true
```

1. **Lines 9–12:** four types: a whole number, a number with a fraction, the same with more digits, and a truth value.
2. **Line 14:** the right side is computed first, and the result goes into `coins`.

The common types are these. `int` holds a whole number such as 3 or -12. `float` holds a number with a fraction such as
90.0f, and the `f` after the digits marks it as a `float`. `double` is the same kind of number with more digits.

`bool` holds `true` or `false`. Text goes in double quotes, as in `"Coin"`; text gets its own page, [Programming
2](../basics/programming-2.md). Without the `f`, `90.0` is a `double`, and a `float` variable that receives it converts
the value and may lose digits.

Fields use `int32_t` for whole numbers, a whole number of exactly 32 bits; [Numbers](../basics/numbers.md) explains bits
and the range of each type. A field can be `bool`, `int32_t`, `float` or one of a few other types, but not `double`: the
build stops with the message `Unsupported script field type`. Most of Strata's script functions use `float`:
`OnUpdate(float deltaTime)`, and a `glm::vec3` holds three `float` values. The cost is fewer digits than `double`; the gain is one type that every part of
the script library agrees on.

:::example[Choosing a type]
A coin game counts the coins you collect, knows how fast a coin turns, and knows whether a coin is gold. The count is a
whole number: `int32_t`. The speed has a fraction, such as 90.5 degrees per second: `float`. Gold is yes or no: `bool`.

```cpp pseudocode
int32_t coinsCollected = 0;
float degreesPerSecond = 90.0f;
bool isGold = false;
```

Each line follows one pattern: type, name, `=`, first value, `;`.
:::

Try it: choose a type for the number of lives, the volume from 0.0 to 1.0, and "the door is open".

:::answer
Lives: `int32_t`, a whole number. Volume: `float`, because 0.5 has a fraction. The door: `bool`, because it is true or
false.
:::

## A variable names a value

A **variable** is a named place that holds a value of one type. You declare it by writing its type, its name and a first
value: `float speed = 90.0f;`. The first value matters. A variable without one holds whatever happened to be in memory,
and a program that reads it gives a different result at each run.

To change what it holds, you write an **assignment**: a statement that stores a new value in a variable, with the
variable on the left of `=` and the new value on the right. In `speed = 120.0f;` the old value is gone. `=` here does
not ask "are these equal?". It means "store".

Choose names that say what the variable holds: `degreesPerSecond`, not `d` or `x2`. Strata's code writes ordinary
variables with a small first letter, such as `deltaTime`, and a script's fields with a capital, such as
`DegreesPerSecond`. A name may hold letters, digits and underscores, and it may not start with a digit. Capitals count: `Speed` and `speed`
are two different names.

Put `const` before the type to forbid a later change: `const float speed = 90.0f;`. The build fails on a line that
assigns to `speed`. Use `const` for every value that should never change; the compiler then guards it for you.

A **field** is a variable that belongs to a script class and that the editor shows. It is a public variable of the
class, with a matching `ST_SCRIPT_FIELD(Name);` line inside the braces of `ST_SCRIPT_CLASS`. You set its value per entity
in the Inspector, and it keeps that value when the script is built again during play. A plain variable inside a function
is gone when the function ends, so it starts fresh in every frame.

The two lines that add a field `IsGold` to a script are these, one in the class and one in the registration. After you
add them, stop the game, build, and press **Play**.

```cpp pseudocode
bool IsGold = false;     // in the class, with the other public variables
ST_SCRIPT_FIELD(IsGold); // in the braces of ST_SCRIPT_CLASS
```

The first line gives the field its type, name and first value, so a new entity starts with its box not ticked. The second
line makes the editor show it.

:::example[Trace a variable]
Follow `coins` through four statements, writing its value after each one.

```cpp pseudocode
int32_t coins = 3; // coins is 3
coins = coins + 2; // the right side is 3 + 2, so coins is 5
coins += 1;        // coins is 6
coins++;           // coins is 7
```

Each statement reads the old value, computes, and stores the result. After the last line the variable holds 7. When a
program gives a result you did not expect, a trace like this, written on paper, finds the line where the value went wrong.
:::

Try it: trace `float speed = 10.0f; speed = speed * 3.0f; speed -= 5.0f;` and give the final value.

:::answer
10 after the first line, 30 after the second, and 25 after `speed -= 5.0f;`, which means `speed = speed - 5.0f;`.
:::

## An expression has a value

An **expression** is a piece of code that has a value: `7`, `speed`, `speed * 2.0f` and `coins > 5` are expressions. A
statement often stores an expression's value in a variable or passes it to a call.

An **operator** is a symbol that combines values into a new value. The arithmetic operators are `+`, `-`, `*` for
multiplication and `/` for division, and `%` for the remainder of a division. The operator `*` runs before `+`, as in
school: `2 + 3 * 4` is 14. What stands in `( )` runs first: `(2 + 3) * 4` is 20. Operators of one rank run from left to
right, so `10 - 4 - 3` is 3.

Two rules of division trip every beginner. First, when both numbers are whole, the result is whole: the fraction is cut
off, toward zero. `7 / 2` is 3, and `-7 / 2` is -3. Second, `%` gives what is left over: `7 % 2` is 1, and a negative
left number gives a negative remainder, so `-7 % 2` is -1. When one number is a `float`, the other converts to `float`
and the result has a fraction: `7 / 2.0f` is 3.5.

Storing a fraction in a whole-number variable cuts the fraction off too: `int whole = 3.9f;` leaves 3 in `whole`. Two
shortcuts save typing. `total += 2;` means `total = total + 2;`, and `total++;` adds 1.

```cpp sketch="basics-programming-1-arithmetic.cpp"
// The order of operations, a division of whole numbers, a mixed division and the shortcuts += and ++.
#include <iostream>

int main()
{
	std::cout << "2 + 3 * 4 = " << 2 + 3 * 4 << '\n';
	std::cout << "(2 + 3) * 4 = " << (2 + 3) * 4 << '\n';
	std::cout << "10 - 4 - 3 = " << 10 - 4 - 3 << '\n';

	const int coins = 7;
	const int players = 2;
	std::cout << "7 / 2 = " << coins / players << '\n';
	std::cout << "7 / 2.0f = " << coins / 2.0f << '\n';

	float share = 1 / 2;   // 1 / 2 is a division of whole numbers: the 0 is stored as 0.0f
	float fixedShare = 1 / 2.0f;
	std::cout << "share = " << share << ", fixedShare = " << fixedShare << '\n';

	int total = 5;
	total += 2; // the same as total = total + 2
	total++;    // the same as total = total + 1
	std::cout << "total = " << total << '\n';
	return 0;
}
```

```text output-of="basics-programming-1-arithmetic.cpp"
2 + 3 * 4 = 14
(2 + 3) * 4 = 20
10 - 4 - 3 = 3
7 / 2 = 3
7 / 2.0f = 3.5
share = 0, fixedShare = 0.5
total = 8
```

1. **Lines 15–17:** `1 / 2` divides whole numbers, so `share` is 0 even though a `float` stores it.
2. **Lines 19–22:** the two shortcuts, and the result 8.

:::example[One frame of the spin]
The line that starts `const glm::quat turn` computes `glm::radians(DegreesPerSecond * deltaTime)`. Take `DegreesPerSecond` = 90 and a
frame of 0.02 seconds, as at 50 frames per second. The product is 90 × 0.02 = 1.8, so the cube turns 1.8 degrees in that
frame; `glm::radians` then converts the angle to radians, the unit that `glm::angleAxis` takes. At 100 frames per second `deltaTime` is
0.01 and each frame turns 0.9 degrees, but the turn in one second stays 90.
:::

Try it: compute `20 - 6 / 2 * 3`, then `17 % 5`, then `3 / 2 + 3 / 2.0f`.

:::answer
`6 / 2 * 3` runs left to right: 3 × 3 = 9, and 20 - 9 = 11. `17 % 5` is 2, because 5 fits three times in 17 and leaves 2.
`3 / 2` is 1 and `3 / 2.0f` is 1.5, so the sum is 2.5.
:::

## A comparison gives a boolean

A **boolean** is a value that is either `true` or `false`; the `bool` type holds one.

A **comparison operator** compares two values and gives a boolean. The six are `==` for "equal", `!=` for "not equal", `<`, `<=`, `>` and `>=`. With `coins`
equal to 12, `coins > 5` is `true`, `coins == 5` is `false` and `coins != 5` is `true`.

A **logical operator** combines booleans. `&&` reads "and" and is `true` only when both sides are. `||` reads "or" and is
`true` when at least one side is. `!` reads "not" and turns `true` into `false` and back.

With `coins` equal to 12, `coins > 5 && coins < 10` is `false`, and `coins > 5 || coins < 10` is `true`. `&&` runs before
`||`; write `( )` when you mix them, so that a reader never has to remember the rule.

A **condition** is an expression whose boolean value decides what a program does next. The next section uses one.

| Operator | Reads | `coins` is 12 |
| --- | --- | --- |
| `coins == 12` | equal | `true` |
| `coins < 12` | less than | `false` |
| `coins <= 12` | less than or equal | `true` |
| `coins != 12 \|\| coins > 20` | not equal, or greater than 20 | `false` |

The two operators that join booleans give these values for every pair of inputs.

| Left | Right | Left `&&` right | Left `\|\|` right |
| --- | --- | --- | --- |
| `true` | `true` | `true` | `true` |
| `true` | `false` | `false` | `true` |
| `false` | `true` | `false` | `true` |
| `false` | `false` | `false` | `false` |

Try it: with `speed` equal to 70, give the value of `speed >= 50 && speed < 70`.

:::answer
`false`. `speed >= 50` is `true`, but `speed < 70` is `false` because 70 is not less than 70, so `&&` gives `false`.
:::

## An if statement chooses what runs

An **if statement** runs a block only when its condition is `true`. Add `else if` for a second condition, tested only
when the first failed, and `else` for what remains. The computer tests the conditions from the top and runs the first
block whose condition is `true`; it skips the rest.

The sketch below sorts a coin count into "none", "few" and "many", combines two booleans, and declares a variable inside
a block. Predict the first word before you read the output: `coins` is 12.

```cpp sketch="basics-programming-1-decisions.cpp"
// An if chain, comparisons joined by && and ||, and a variable that lives only inside its braces.
#include <iostream>

int main()
{
	std::cout << std::boolalpha;
	const int coins = 12;
	if (coins == 0)
		std::cout << "none\n";
	else if (coins < 10)
		std::cout << "few\n";
	else
		std::cout << "many\n";

	const bool isGold = false;
	const bool nearPlayer = true;
	std::cout << "gold and near: " << (isGold && nearPlayer) << '\n';
	std::cout << "gold or near: " << (isGold || nearPlayer) << '\n';
	std::cout << "not gold: " << !isGold << '\n';
	if (nearPlayer)
	{
		const int bonus = 5; // exists only between these braces
		std::cout << "bonus: " << bonus << '\n';
	}
}
```

```text output-of="basics-programming-1-decisions.cpp"
many
gold and near: false
gold or near: true
not gold: true
bonus: 5
```

1. **Lines 8–13:** an `if` chain. 12 is not 0 and not below 10, so the `else` runs. Without braces, one statement follows
   each condition.
2. **Lines 20–24:** `bonus` is declared inside braces and gone after the closing one.

The block of a condition also sets a **scope**: the part of the code where a name exists. A variable lives from its
declaration to the closing brace of its block. Outside those braces its name is unknown, and a build that uses it fails
with an error naming the variable.

A script uses an `if` to react to the player. `Input::IsKeyDown(Key::Space)` is `true` in every frame in which the player
holds the space bar.

```cpp pseudocode
if (Input::IsKeyDown(Key::Space))
{
	Log::Info("Space is down");
}
```

The line is written in every frame while the key is held, about 50 lines each second at 50 frames per second. It also fills
the Console's 4,096 lines quickly, so remove such a line when you are done.

:::example[Which branch runs?]
The chain from the sketch, with `coins` set to 0, 7 and 12. For 0, the first condition `coins == 0` is `true`: "none", and the
rest is skipped. For 7, the first is `false`, the second `coins < 10` is `true`: "few". For 12, both are `false`: "many".
:::

Try it: with `coins` equal to 10, which word does the chain write?

:::answer
"many". `10 == 0` is `false`, and `10 < 10` is `false` because 10 is not less than 10, so the `else` runs. The boundary
belongs to the branch whose comparison is `<=` or `>=`, or to the `else`.
:::

## A namespace groups names

A **namespace** is a named group of names. You reach a name in it with `::`, written between the group and the name.
`glm::vec3` is the type `vec3` of the library `glm`, and `glm::radians` is its function. The engine's own names live in
the namespace `Strata`: `Strata::Script`. Without groups, two libraries that both define `Length` would collide.

The line `using namespace Strata;` at the top of a script says: when a name is unknown, look in `Strata` too. That is why
the generated script can write `Script` and `Log` without the prefix. `glm` is not covered by it, so `glm::` stays.

The names of keys are in a namespace of the script library.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L19-L26"
// Key codes (US keyboard layout). The values are part of the script ABI and match the engine's.
namespace Key
{
	enum : KeyCode
	{
		Space = 32,
		Apostrophe = 39,
		Comma = 44,
```

`Key` is the namespace, and `Space` is a name inside it with the number 32. The `enum` inside it has no name of its own and
gives the names the type `KeyCode`, a whole number. You write `Key::Space`, and `Input::IsKeyDown(Key::Space)` asks whether that key is
down. `Input` is a class here and also joined with `::`; classes belong to [Programming
3](../basics/programming-3.md).

Try it: what do `Strata::Log::Info` and `glm::length` have in common, and what differs?

:::answer
Both write a name after `::`. The left part says where the name lives: the engine's namespace `Strata`, or the library
`glm`. In `Strata::Log::Info`, `Log` is a class inside `Strata`.
:::

## A scoped enumeration names a few choices

An enumeration is a type whose values are a short list of names. A **scoped enumeration**, written `enum class`, keeps its
value names inside the type: you write the type, `::`, and the value. The script library uses one for the mouse cursor.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L212-L217"
enum class CursorMode : uint32_t
{
	Normal = StrataScriptCursorMode_Normal,
	Hidden = StrataScriptCursorMode_Hidden, // Hidden over the game's window
	Locked = StrataScriptCursorMode_Locked  // Hidden and kept in the window; GetMouseDelta keeps reporting movement (mouse look)
};
```

`CursorMode::Locked` hides the cursor and keeps it in the window; `Input::SetCursorMode(CursorMode::Locked)` sets it.
`Locked` alone means nothing, and a scoped value does not turn into a number by accident. That differs from `Key::Space`,
which is a name in a namespace, not a scoped enumeration value. Both use `::`, and the left part tells you which it is.

A **switch statement** compares one value, a whole number or an enumeration value, with a list of `case` labels and runs
the statements after the matching one. A
`break` ends the case; without it the code runs on into the next case. `default` catches every other value.

```cpp sketch="basics-programming-1-switch.cpp"
// A scoped enumeration and a switch on it: one case runs on into the next, and default catches the rest.
#include <iostream>

enum class Mode { Normal, Hidden, Locked };

int main()
{
	const Mode mode = Mode::Hidden;
	switch (mode)
	{
		case Mode::Hidden:
			std::cout << "hidden\n";
			[[fallthrough]]; // no break: the lines of the next case run too
		case Mode::Locked:
			std::cout << "locked\n";
			break;
		default:
			std::cout << "other\n";
			break;
	}
}
```

```text output-of="basics-programming-1-switch.cpp"
hidden
locked
```

1. **Lines 11–14:** `Hidden` has no `break`, so after "hidden" the line of the next case runs.
2. **Line 13:** `[[fallthrough]];` tells the compiler and the reader that the missing `break` is on purpose.
3. **Lines 17–19:** `default` catches a value that no case names, such as `Mode::Normal`.

An `if` chain and a `switch` often give the same result. Use `switch` when one value is tested against several exact
choices, such as an enumeration's values. The cost: forgetting a `break` is silent, and the output shows it only when you
read it.

:::example[Which lines run?]
In the sketch, `mode` is `Mode::Hidden`: the switch jumps to that case, prints "hidden", runs on into `Locked` and
prints "locked", and stops at its `break`. With `Mode::Locked` only "locked" prints. With `Mode::Normal` no case
matches, and `default` prints "other".
:::

Try it: change `mode` in the sketch to `Mode::Locked`. What prints, and how many lines?

:::answer
One line, "locked". The switch jumps to the `Locked` case, whose `break` ends it.
:::

## Common mistakes

- **`=` in place of `==`.** `if (coins = 5)` stores 5 in `coins` and the condition is true, whatever `coins` held. Write
  `if (coins == 5)`.
- **A missing `;`.** The build fails, and the error often names the line after the missing `;`. Check the end of the line
  before.
- **Integer division where a fraction was meant.** `Speed / 2` with a whole `Speed` loses the fraction, and `1 / 2` is 0.
  Write `2.0f` or use `float` variables.
- **A variable used outside its braces.** The build reports an unknown name. Declare the variable before the block that
  needs it, or use it only inside its block.
- **A missing `break`.** The output shows lines of two cases. Add the `break`, or write `[[fallthrough]];` when the run-on
  is meant.
- **A format string in `Log::Info`.** `Log::Info("Speed: {}", speed)` writes `Speed: {}90`, because the arguments are
  only joined. Write `Log::Info("Speed: ", speed)`.
- **A `double` field.** The build stops with `Unsupported script field type`. Declare it as `float`.
- **A wrong capital.** `speed` where the field is `Speed` is an unknown name, and the build fails. Copy the spelling.

## Summary

- A script is statements that run in order, each ending with `;`; braces group them and `//` starts a comment; `OnCreate`
  runs once and `OnUpdate` every frame.
- Every value has a type (`int32_t`, `float`, `bool`); a variable is declared with a type and a first value, assigned with
  `=`, named for what it holds, and frozen with `const`.
- An expression follows the order of operations; whole-number division drops the fraction, `%` gives the remainder, and
  one `float` makes the division keep its fraction.
- A comparison gives a boolean, `&&`, `||` and `!` combine booleans, and an `if` chain runs the first block whose
  condition is true; a variable lives inside its braces.
- A name with `::` lives in a namespace or a scoped enumeration, such as `Key::Space` or `CursorMode::Locked`; a `switch`
  runs one case, and a missing `break` runs on.

## Check yourself

1. `Log::Info(10 / 4);` writes which line? A: `2.5`. B: `2`. C: `3`. D: `2.0`.

   :::answer{tests="expressions"}
   B. Both numbers are whole, so the division is whole and drops the 0.5. A needs `10 / 4.0f`; C rounds up, and C++ never
   rounds in a whole-number division; D shows a fraction that a whole number does not have.
   :::

2. Which line declares a variable that a later line cannot change? A: `float s = 9.0f;`. B: `const float s = 9.0f;`. C:
   `float const;`. D: `s = 9.0f;`.

   :::answer{tests="types-variables"}
   B. `const` forbids later assignments. A is an ordinary variable. C is not a declaration. D assigns to a variable that
   must already exist.
   :::

3. With `a` equal to `true` and `b` equal to `false`, what does `Log::Info(a && !b, " ", a || b, " ", !a);` write?

   :::answer{tests="decisions"}
   `true true false`. `!b` is `true`, so `a && !b` is `true`. `a || b` is `true`. `!a` is `false`. A `bool` prints as a
   word.
   :::

4. Which statement about `Key::Space` is right? A: `Key` is a scoped enumeration. B: `Key` is a namespace and `Space` a
   name in it. C: `Space` is a function. D: `Key` is a variable.

   :::answer{tests="names-switch"}
   B. At the pin, `Key` is a namespace holding an enumeration without a name, of key numbers. `CursorMode` is the scoped enumeration
   of the same file. C and D confuse `::` with a call and a variable.
   :::

5. Predict the output for `int level = 3;` with a `switch` that has `case 3:` writing "three" and no `break`, followed by
   `case 4:` writing "four" with a `break`.

   :::answer{tests="names-switch script-frame"}
   Two lines: "three", then "four". The missing `break` lets the run continue into the next case. The lines run in
   `OnCreate` once, in `OnUpdate` in every frame.
   :::

## Practice

Run exercises 1, 3 and 4 in `Playground`; exercises 2 and 5 change your spinning script, so stop the game before each build.

1. **Basic.** Predict what `Log::Info` writes for `7 / 2`, `7 % 2`, `7 / 2.0f`, `-7 / 2` and `-7 % 2`, one line each. Then
   add the five lines to `OnCreate`, play, and compare.

   :::answer[Worked solution]{tests="expressions" solution="sketches/basics-programming-1-division.cpp"}
   The Console shows 3, 1, 3.5, -3 and -1. A whole-number division drops the fraction toward zero, and the remainder
   takes the sign of the left number. The program below does the same in plain C++.

   ```cpp sketch="basics-programming-1-division.cpp"
   // Practice 1: what division and the remainder print for whole numbers, a mixed pair and a negative number.
   #include <iostream>

   int main()
   {
   	std::cout << "7 / 2 = " << 7 / 2 << '\n';
   	std::cout << "7 % 2 = " << 7 % 2 << '\n';
   	std::cout << "7 / 2.0f = " << 7 / 2.0f << '\n';
   	std::cout << "-7 / 2 = " << -7 / 2 << '\n';
   	std::cout << "-7 % 2 = " << -7 % 2 << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-1-division.cpp"
   7 / 2 = 3
   7 % 2 = 1
   7 / 2.0f = 3.5
   -7 / 2 = -3
   -7 % 2 = -1
   ```

   1. **Lines 6–10:** each line prints a label and one computed value.
   :::

2. **Basic.** In your spinning script, put `const float speed = 90.0f;` as the first line of `OnUpdate`, and use `speed` in
   place of `DegreesPerSecond`. Change 90.0f to 180.0f and watch it turn. Then add the line `speed = 45.0f;` below it.

   :::answer[Worked solution]{tests="types-variables"}
   With 180.0f the coin or cube turns twice as fast, because the turn of each frame is the speed times `deltaTime`. The extra line
   breaks the build: `speed` is `const`, and the error names it. Remove the line, or remove `const` if the speed must
   change.
   :::

3. **Medium.** Put these six lines in order to write "slow" below 50, "fast" from 50 to below 100, and "very fast" from
   100. Then say what each of 30, 70 and 100 writes.

   ```cpp pseudocode
   	Log::Info("fast");
   else
   if (speed < 50.0f)
   	Log::Info("very fast");
   else if (speed < 100.0f)
   	Log::Info("slow");
   ```

   Each `Log::Info` line follows the condition it answers, and `else` comes last.

   :::answer[Worked solution]{tests="decisions"}
   The order is `if (speed < 50.0f)`, `Log::Info("slow");`, `else if (speed < 100.0f)`, `Log::Info("fast");`, `else`,
   `Log::Info("very fast");`. Each `Log::Info` line follows the condition it belongs to. 30 writes "slow", 70 writes
   "fast", and 100 writes "very fast", because 100 is not below 100.
   :::

4. **Hard.** Write a `switch` on `int level` that logs "one", "two" or "three" for 1, 2 and 3 and "other" in `default`.
   Leave the `break` out of `case 2`. Predict the output for 2, run it, then restore the `break`.

   :::answer[Worked solution]{tests="names-switch" solution="sketches/basics-programming-1-fallthrough.cpp"}
   For 2 the output is "two" and "three": the run continues past the missing `break`. In the script, use the same
   statements with `Log::Info`.

   ```cpp sketch="basics-programming-1-fallthrough.cpp"
   // Practice 4: a switch on a whole number whose case 2 has no break, so the output shows the missing break.
   #include <iostream>

   int main()
   {
   	const int level = 2;
   	switch (level)
   	{
   		case 1:
   			std::cout << "one\n";
   			break;
   		case 2:
   			std::cout << "two\n";
   			[[fallthrough]]; // the missing break
   		case 3:
   			std::cout << "three\n";
   			break;
   		default:
   			std::cout << "other\n";
   			break;
   	}
   	return 0;
   }
   ```

   ```text output-of="basics-programming-1-fallthrough.cpp"
   two
   three
   ```

   1. **Lines 12–14:** `case 2` has no `break`; the attribute marks it as intended, to keep the build free of warnings.
   :::

5. **Hard.** In your spinning script, `Coin` or `Spinner`, move the spin speed into a variable, add a `bool` field `IsGold`, and write an `if` that
   makes it turn twice as fast when `IsGold` is ticked. Tick the box on one coin or cube in the Inspector, and play.

   :::answer[Worked solution]{tests="types-variables decisions" solution="sketches/basics-programming-1-goldspin.cpp"}
   Add the field and its registration, then change `OnUpdate`. After the build, select that coin or cube, find its script in the
   Inspector, tick **Is Gold** (the Inspector puts spaces in the name), and play: it turns twice as fast.

   ```cpp pseudocode
   float speed = DegreesPerSecond;
   if (IsGold)
   {
   	speed = speed * 2.0f;
   }
   // then use speed where DegreesPerSecond stood
   ```

   The sketch below computes the same turn of one frame of 0.02 seconds for both cases.

   ```cpp sketch="basics-programming-1-goldspin.cpp"
   // Practice 5: the turn of one frame for a plain coin and a gold coin, as the script's OnUpdate computes it.
   #include <iostream>

   int main()
   {
   	const float degreesPerSecond = 90.0f;
   	const float deltaTime = 0.02f; // one frame of 0.02 seconds, 50 frames per second

   	bool isGold = false; // the coin as the Inspector shows it: the box is not ticked
   	float speed = degreesPerSecond;
   	if (isGold)
   		speed = speed * 2.0f;
   	std::cout << "plain coin: " << speed * deltaTime << " degrees\n";

   	isGold = true; // the box is ticked
   	speed = degreesPerSecond;
   	if (isGold)
   		speed = speed * 2.0f;
   	std::cout << "gold coin: " << speed * deltaTime << " degrees\n";
   	return 0;
   }
   ```

   ```text output-of="basics-programming-1-goldspin.cpp"
   plain coin: 1.8 degrees
   gold coin: 3.6 degrees
   ```

   1. **Lines 9–13:** `speed` starts as the field's value, and the `if` doubles it only for a gold coin.
   :::

## Where the book uses it

- [Programming 2](../basics/programming-2.md) uses variables, expressions and `if` inside loops and functions.
- [Vectors](../basics/math-vectors.md) uses `float` variables, expressions and `Log::Info` to compute with positions.
- [Numbers](../basics/numbers.md) uses `int32_t`, `float` and the division of whole numbers to show their limits.
- [Debugging](../basics/debugging.md) uses `Log` and its levels, and conditions in `if`, to find a bug.

## Further reading

- Learn C++ (learncpp.com), chapters 1, 4 and 5: lessons on statements, variables, operators, `if` and `switch`; beginner.
- [cppreference: if statement](https://en.cppreference.com/w/cpp/language/if): the exact rules of `if`; intermediate.
- [cppreference: switch statement](https://en.cppreference.com/w/cpp/language/switch): `case`, `break` and fall through;
  intermediate.
- [cppreference: scoped enumerations](https://en.cppreference.com/w/cpp/language/enum): `enum class`; intermediate.
