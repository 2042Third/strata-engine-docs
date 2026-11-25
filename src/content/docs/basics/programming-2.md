---
id: basics/programming-2
title: "Programming from zero II: loops, functions, lists and structs"
description: "Learn loops, functions, lists, structs and text in a Strata script, and line up coins in Coin Run with a function and a loop."
kind: primer
size: L
tracks: [G, B, E]
needs: [basics/programming-1]
time: 120
learn:
  - id: loops
    text: write a while loop and a for loop and predict how many turns each runs
  - id: functions
    text: write a function with parameters, a return value and a default argument, and predict its result
  - id: copies
    text: explain why a changed parameter or a local variable never reaches the code that called the function
  - id: lists-structs
    text: write a std::vector loop and a struct, and read a member with a dot
  - id: text
    text: predict what std::to_string and std::stoi give, and what std::stoi does with text that is no number
status: final
---

::::test-out

1. What does this loop write to the Console, and which line comes last?

   ```cpp pseudocode
   for (int i = 0; i < 4; i++)
   	Log::Info("i = ", i);
   ```

   Count the turns first.

   :::answer{tests="loops"}
   Four lines, `i = 0` to `i = 3`, and `i = 3` comes last. The variable `i` starts at 0 and the loop stops when `i < 4` is
   false, which happens at 4.
   :::

2. Write a function `Twice` that takes one `float` named `value` and gives back twice that number.

   :::answer{tests="functions"}
   `float Twice(float value) { return value * 2.0f; }`. The type before the name is the type of the number that comes back,
   and `return` sends it to the caller.
   :::

3. What does the last line write to the Console?

   ```cpp pseudocode
   void AddBonus(int score)
   {
   	score = score + 10;
   }
   // later, in OnCreate:
   int coins = 5;
   AddBonus(coins);
   Log::Info(coins);
   ```

   Ask which variable `AddBonus` changes.

   :::answer{tests="copies"}
   `5`. The parameter `score` is a copy of `coins`, so the function adds 10 to the copy and the copy is gone when the
   function ends.
   :::

4. Write the two lines that make an empty `std::vector<float>` named `speeds` and add the number 4.5 to it.

   :::answer{tests="lists-structs"}
   `std::vector<float> speeds;` and `speeds.push_back(4.5f);`. The type in the angle brackets says what the list holds,
   and `push_back` adds one value at the end.
   :::

5. What do `std::to_string(7) + "!"` and `std::stoi("8") + 1` give?

   :::answer{tests="text"}
   The text `7!` and the number 9. The first turns 7 into text and joins the sign `!` to it; the second turns the
   text "8" into a number and adds 1.
   :::

::::

## Why you will need this

Coin Run needs more coins, in a neat line. With only what Programming 1 taught, you write the same few lines once for each
coin, and a sixth coin means a sixth copy. This page gives you the tools that remove the copies: loops repeat steps,
functions name a job, lists keep many values, structs group values and strings hold words.

You use them on almost every page after this one. [Vectors](../basics/math-vectors.md) writes functions that take and
return positions. [Programming 3](../basics/programming-3.md) builds classes out of functions and structs. [Data
structures](../basics/data-structures.md) asks what a list costs. At the end of this page you write a script that lines
coins up in Coin Run.

:::question[What are the lines I have not seen yet?]
Calls such as `scores.size()` and the `#include` lines of the sketches are taught in [Programming
3](../basics/programming-3.md). For now, read `scores.size()` as "ask `scores` for its size" and treat the rest as names
to copy.
:::

## A loop repeats steps while a condition holds

Suppose a script must write the numbers 0, 1 and 2 to the Console. Three `Log::Info` lines do it. For 1,000 numbers the
same lines would fill many pages, and one typing mistake would hide among them.

A **loop** is a block of statements that the computer runs again and again. One run of the block is a turn. The
simplest loop is the while loop, and you read it as a sentence.

A **while loop** checks a condition, runs its block when the condition is true, and then checks the condition again.

```cpp pseudocode
int turn = 0;
while (turn < 3)
{
	Log::Info("turn ", turn);
	turn = turn + 1;
}
```

Read it as: while `turn` is below 3, write the line and add 1. The check comes before every turn, also before the first.
With `turn` at 0, 1 and 2 the condition is true, so the block runs three times. With `turn` at 3 the condition is false,
the loop ends, and the statement after the closing brace runs.

Because the check comes first, a loop can have zero turns. If `turn` were 5 at the start, `turn < 3` would be false at
once, and the block would never run.

```mermaid caption="A while loop checks its condition before each turn: true runs the block and checks again, false leaves the loop." alt="A flow of boxes. Check the condition. When it is true, run the block and return to the check. When it is false, leave the loop."
flowchart LR
    A["Check the condition"] -->|true| B["Run the block"]
    B --> A
    A -->|false| C["Leave the loop"]
```

:::example[Count the turns]
A loop starts with `n` at 10 and runs `while (n > 0)` with `n = n - 4;` in its block. Follow `n` by hand.

The check sees 10, which is above 0, and the block makes `n` 6. The check sees 6, and `n` becomes 2. The check sees 2, and `n` becomes
-2. The check sees -2, which is not above 0, so the loop ends.

The loop ran 3 turns, and `n` ends at -2, not at 0. A loop stops only when the check fails, and the check runs only
between turns.
:::

Try it: how many turns does `while (n < 3)` run when `n` starts at 3?

:::answer
None. The check sees 3, `3 < 3` is false, and the block never runs.
:::

:::caution[A loop that never ends freezes the editor]
If nothing in the block can make the condition false, the loop never ends. Your script runs on the same thread that
draws the editor, so the editor cannot draw another frame until your code returns. The window freezes, and the
**Console** stays empty, because the engine writes no message for you.

Strata has a watchdog that would log a script call that runs too long, but it is off unless a program sets a timeout,
and only the engine's own tests do. Even then it only logs: it cannot stop the loop. The details are on [Crash
containment](../scripting/crash-containment.md).

You must end the editor from outside, and its own close button does not answer, because the frozen thread also handles it.
On Windows, press **Ctrl+Shift+Esc**, select the editor in the Task Manager and
choose **End task**. On macOS, press **Cmd+Option+Esc**, select the editor and choose **Force Quit**. On Linux, use the
System Monitor's **End Process**, or run `kill` with the editor's process number.

[Project files](../make/project-files.md) says how to recover afterwards. Save your scene before you press **Play** on a
loop you have not tried.
:::

## A for loop puts the counting in one line

The `while` loop spreads its counting over three places: the start of the variable, the check and the change. Count loops
are so common that C++ has a form that keeps all three together.

A **for loop** holds the start, the check and the step in its first line, separated by `;` signs. The sketch below runs
the same three turns as before, once with `while` and once with `for`.

```cpp sketch="basics-programming-2-loops.cpp"
// A while loop and a for loop that each run three turns.
#include <iostream>

int main()
{
	int turn = 0;
	while (turn < 3) // checked before every turn
	{
		std::cout << "while " << turn << '\n';
		turn = turn + 1; // without this line the condition never becomes false
	}

	for (int i = 0; i < 3; i++) // start; condition; step
		std::cout << "for " << i << '\n';
	return 0;
}
```

```text output-of="basics-programming-2-loops.cpp"
while 0
while 1
while 2
for 0
for 1
for 2
```

1. **Lines 7–11:** the `while` loop; the last line of its block changes `turn`, so the check can fail.
2. **Line 13:** the three parts: `int i = 0` runs once at the start, `i < 3` is checked before each turn, and `i++` runs
   after each turn.

The step `i++` adds 1 to `i`, as `i = i + 1` does. Programmers start at 0 and test `i < count`: the loop then runs
exactly `count` turns, and `i` takes the values 0 up to `count - 1`. Lists start at 0 as well, so the same `i` can walk a
list from its first value to its last.

Writing `i <= 3` instead gives four turns, 0, 1, 2 and 3. A loop with one turn too many or too few is an **off-by-one
mistake**, and it is the most common loop mistake. Check a loop with pencil and paper: count its turns for the smallest case.

:::example[Five coins in a line]
Coin Run will need five coins, one every 2 metres along the X axis. A loop with `i` from 0 while `i < 5` has five turns.
The x position of turn `i` is `i * 2`.

The values are 0, 2, 4, 6 and 8 metres. The last coin is at `4 * 2`, not at `5 * 2`, because `i` never reaches 5.
:::

Try it: how many turns does `for (int i = 2; i < 6; i++)` run, and which values does `i` take?

:::answer
Four turns, with `i` at 2, 3, 4 and 5. The loop starts at 2, not 0, so the number of turns is 6 - 2.
:::

## A function gives a job a name

You already use functions: `Log::Info` and `Input::IsKeyDown` are jobs that someone else wrote and named, and `OnUpdate`
is a job that you write and the engine calls. This section shows how you make your own.

A **function** is a named block of statements that you can run from anywhere by writing its name. When a job appears in
two places, a function holds it once. If the job changes, you change one place, and the two places cannot disagree.

A **function call** is the use of a function's name, followed by brackets, which runs the function's block. Here is
the smallest function, with no input and no output.

```cpp pseudocode
void LogGreeting()
{
	Log::Info("Hello, coin");
}
// in OnCreate:
LogGreeting();
LogGreeting();
```

The word `void` says that the function gives nothing back. The two calls write the line twice. When the computer meets a
call, it jumps into the function, runs the block to the closing brace, and returns to the line after the call.
The sketches on this page start in `main`, the function the computer calls first.

## Parameters carry values in and a return value brings one out

Most jobs need input: "double this number", "move this point". A **parameter** is a variable in the function's
brackets, with a type, that receives a value at each call.

A **function argument** is the value you write in a call for one parameter. In `Add(coins, 3)` the arguments are `coins`
and `3`.

A **return value** is the value that a call gives back to the line that made the call. You write its type before the
function's name, and you end the function with `return` and a value.

```cpp sketch="basics-programming-2-functions.cpp"
// A function with two parameters and a return value, and a void function that changes only its copy.
#include <iostream>

int Add(int a, int b) // a and b are parameters
{
	return a + b;
}

void ReportDouble(int value) // void: gives nothing back
{
	value = value * 2; // changes the copy
	std::cout << "inside: " << value << '\n';
}

int main()
{
	int coins = 4;
	int total = Add(coins, 3); // the arguments are 4 and 3
	std::cout << "total: " << total << '\n';
	ReportDouble(coins);
	std::cout << "outside: " << coins << '\n';
	return 0;
}
```

```text output-of="basics-programming-2-functions.cpp"
total: 7
inside: 8
outside: 4
```

1. **Line 4:** `int Add(int a, int b)`: the function gives back an `int` and takes two `int` parameters.
2. **Line 6:** `return` ends the function and the call becomes the value `a + b`.
3. **Lines 9–13:** `void` function; it changes `value`, but `coins` stays 4 outside, as the output shows.
4. **Line 18:** `Add(coins, 3)` copies 4 into `a` and 3 into `b`, and `total` receives 7.

A call is a short chain of steps. The computer works out each argument, copies it into the matching parameter, runs the
block, and replaces the call with the returned value. The arguments match the parameters by position, from left to right.

The copy is the key rule. A function never touches the caller's variable: it works on its own copies. That keeps a
function safe, because nothing outside can change under it, and you can read it without looking at the caller.

The cost is that a function cannot change the caller's number directly. To get a result back, return it and store it:
with a function `int Double(int value)` that ends in `return value * 2;`, write `coins = Double(coins);`. [Programming 3](../basics/programming-3.md) teaches references, which let a function change the
caller's variable on purpose.

:::example[Follow a call by hand]
The function is `float Half(float value) { return value / 2.0f; }` and the line is `float x = Half(9.0f) + 1.0f;`.

The computer runs `Half` with `value` at 9, so the function returns 4.5. The call is replaced by 4.5, the line becomes
`4.5 + 1.0`, and `x` holds 5.5. The 9 itself is not changed anywhere.
:::

Try it: what does `Half(Half(8.0f))` give?

:::answer

The answer is 2. The inner call returns 4, and the outer call halves that 4.

:::

## A local variable lives for one call

A **local variable** is a variable declared inside a function. It is made when the computer reaches its line and is gone at the
function's closing brace. The parameters of a function are local variables too. The next call makes everything again from
the start.

```cpp sketch="basics-programming-2-locals.cpp"
// A local variable is made again, with its first value, at every call.
#include <iostream>

void Count()
{
	int hits = 0;
	hits = hits + 1;
	std::cout << "hits: " << hits << '\n';
}

int main()
{
	Count();
	Count();
	return 0;
}
```

```text output-of="basics-programming-2-locals.cpp"
hits: 1
hits: 1
```

1. **Line 6:** `hits` is made with 0 at each call, so the second call cannot see the first call's value.

You met the opposite in Programming 1: a script's field keeps its value from frame to frame. In the next script, after
three frames `Hits` holds 3, but `bonus` is 1 in every frame.

```cpp pseudocode
int Hits = 0; // a field of the script class
void OnUpdate(float deltaTime)
{
	int bonus = 0; // a local variable: made again every frame
	bonus = bonus + 1;
	Hits = Hits + 1;
}
```

A script uses both kinds. A name inside one function never clashes with a name in another, which lets you read each function
alone. The cost is that a local variable cannot carry a value to the next call, so a value that must last, such
as a score, belongs in a field.

## Default arguments and shared names let one name do several jobs

Strata's script library lets you create an entity from a prefab with one name, `Instantiate`, written in four ways. The
two forms that take a path are below. Read the parameters after the `=` signs first.

```cpp src="StrataScriptCore/Include/StrataScript/Scene.h#L177-L186"
static Entity Instantiate(std::string_view assetPath, Entity parent = Entity())
{
	return Instantiate(Assets::Find(assetPath), parent);
}

static Entity Instantiate(std::string_view assetPath, const glm::vec3& translation, const glm::quat& rotation = glm::quat(1.0f, 0.0f, 0.0f, 0.0f),
	const glm::vec3& scale = glm::vec3(1.0f), Entity parent = Entity())
{
	return Instantiate(Assets::Find(assetPath), translation, rotation, scale, parent);
}
```

1. **Line 177:** `Entity parent = Entity()` is a default argument: a call may omit it, and the parameter then
   holds an empty entity.
2. **Lines 182–183:** a second `Instantiate` with the same name but other parameters: a position, then a rotation, a scale
   and a parent, each with a default. A `glm::vec3` is three numbers; read `const` and `&` as nothing until Programming 3.
3. **Line 179:** the form looks the asset up by its path and passes it to the form that takes an asset; line 185 does the
   same.

A **default argument** is a value written after `=` in a parameter, which the call uses when it gives no argument for
that parameter. Defaults must come last: a call fills the parameters from the left, so it can omit only the
parameters at the end.

Two functions may also share one name when their parameters differ. The computer picks the one whose parameters fit the
arguments of the call. The sketch shows both ideas.

```cpp sketch="basics-programming-2-defaults.cpp"
// A default argument fills a parameter the call leaves out; two functions may share a name.
#include <iostream>

float Scale(float value, float factor = 2.0f)
{
	return value * factor;
}
void Show(int number)
{
	std::cout << "int " << number << '\n';
}
void Show(float number)
{
	std::cout << "float " << number << '\n';
}

int main()
{
	std::cout << Scale(5.0f) << '\n';       // factor is 2
	std::cout << Scale(5.0f, 3.0f) << '\n'; // factor is 3
	Show(7);
	Show(7.5f);
	return 0;
}
```

```text output-of="basics-programming-2-defaults.cpp"
10
15
int 7
float 7.5
```

1. **Line 4:** `factor` has a default of 2, so `Scale(5.0f)` returns 10.
2. **Lines 8–15:** two functions named `Show`; the call `Show(7)` passes a whole number and runs the first, and
   `Show(7.5f)` runs the second.
3. **Line 20:** this call gives the factor, so the default stays unused and the result is 15.

Strata chose this so that one name, `Instantiate`, covers one job: to create the prefab's entities. Without it, the library
would need a name for each combination of arguments. The cost is that a call can reach another form than you meant, so
read the parameters of the forms when a call acts strangely.

`Instantiate` never waits for an asset. If the prefab is not loaded yet, it starts loading it and returns a null entity.
So ask for the asset early, in `OnCreate`, and call `Instantiate` after `Assets::IsLoaded` says yes.

## Static member functions are called through a type's name

You have written `Log::Info` and `Input::IsKeyDown` without asking what the double colon joins. `Log` and `Input` are
names of types. A **static member function** is a function that belongs to a type's name and needs no object of that
type: you call it by writing the type, `::` and the function.

:::question[What are `host` and `->`?]
The `*` after a type and the `->` sign belong to pointers, taught in [Pointers and memory in C++](../basics/cpp-memory.md).
Read the comment and the first line, and treat the body as "ask the engine".
:::

Here is one of Input's functions, with the comment above it.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L380-L388"
// Input actions: the project's named controls (Project Settings > Input Actions), which players can rebind. Name an
// action "<Map>/<Action>" ("Gameplay/Jump"), or by its bare name ("Jump") when no other map has an action of that name;
// unknown and ambiguous names read as up and the engine logs a warning. Read actions rather than keys wherever a player
// could want another control. The state is the current frame's, like keys': read Pressed and Released in OnUpdate.
static bool IsActionDown(std::string_view action)
{
	const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(InputIsActionDown);
	return host && host->InputIsActionDown(Detail::GetContext(), Detail::ToABIString(action));
}
```

The comment gives the rule for names: `"Gameplay/Jump"` or the bare name `"Jump"`. An unknown name reads as up, which
means not pressed, and the engine logs a warning. The return type is `bool`, so the call fits in an `if`: `if (Input::IsActionDown("Jump"))`. The
parameter type `std::string_view` accepts text in quotes; [Modern C++](../basics/cpp-modern.md) explains it.

Another static member function has defaults for the end of its parameters. Read the comment and the first line.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L326-L331"
// An axis with a dead zone: values within it read 0, the rest is rescaled so that the axis still reaches 1 (a dead zone
// of 0 reads the device's value).
static float GetGamepadAxis(GamepadAxis axis, uint32_t gamepad = 0, float deadZone = c_DefaultDeadZone)
{
	const StrataScriptHostAPI* host = ST_SCRIPT_DETAIL_HOST_WITH(GetGamepadAxis);
	const float value = host ? host->GetGamepadAxis(Detail::GetContext(), gamepad, static_cast<uint32_t>(axis)) : 0.0f;
```

`Input::GetGamepadAxis(GamepadAxis::LeftX)` omits the last two arguments. The gamepad number defaults to 0, the first
gamepad, and the dead zone defaults to 0.15, the constant `c_DefaultDeadZone`. A stick at rest never reads exactly 0, so
every value within the dead zone reads 0, and the other values are scaled so that the stick can still reach 1. The type `uint32_t` is a whole number
that is never negative; [Numbers](../basics/numbers.md) explains it.

:::why[Input, Log, Scene and Assets are static]
A game has one keyboard, one log and one scene being played, so these types need no object that you create, keep or pass
into every function. A script calls them from anywhere, and the call reads like its name: `Input::IsActionDown("Jump")`.
The cost is that these calls are global: any function can reach them, so you must read a function's body to see
that it uses input.
:::

## An array holds a fixed number of values

A coin game has five coin speeds. Five variables, `speed1` to `speed5`, are hard to loop over. One variable that holds
five numbers is better.

An **array** is a fixed number of values of one type stored one after the other. In C++ the standard form is
`std::array<float, 3>`: the type of the values, then the count.

Each value has a number. An **array index** is the position of a value in an array or a list, counted from 0. A
`std::array<float, 3>` has indexes 0, 1 and 2, and you read one with square brackets: `speeds[0]`.

A **dynamic array**, in C++ `std::vector`, is a list that grows and shrinks while the program runs. Use an array when you
know the count, and a vector when you do not. The sketch shows both.

```cpp sketch="basics-programming-2-lists.cpp"
// A std::array of three floats and a std::vector that grows; the vector is summed two ways.
#include <array>
#include <iostream>
#include <vector>

int main()
{
	std::array<float, 3> speeds = { 10.0f, 20.0f, 30.0f }; // indexes 0, 1 and 2
	std::cout << "first " << speeds[0] << ", last " << speeds[2] << '\n';

	std::vector<float> scores; // starts empty
	scores.push_back(5.0f);
	scores.push_back(7.5f);
	scores.push_back(2.0f);
	std::cout << "count " << scores.size() << '\n';

	float total = 0.0f;
	for (float score : scores) // one turn per element
		total = total + score;
	std::cout << "total " << total << '\n';

	for (std::size_t i = 0; i < scores.size(); i++) // the same walk, with an index
		std::cout << i << ": " << scores[i] << '\n';
	return 0;
}
```

```text output-of="basics-programming-2-lists.cpp"
first 10, last 30
count 3
total 14.5
0: 5
1: 7.5
2: 2
```

1. **Line 8:** an array of three `float` values with the first values written in braces.
2. **Lines 12–14:** `push_back` adds a value at the end of the vector, which started empty.
3. **Line 15:** `size()` gives the number of values, which is 3 here.
4. **Lines 18–19:** the range-based `for`: the loop takes each value of the list in order and copies it into `score`.
5. **Line 22:** the counted form over the same vector. `std::size_t` is the type of a size: a whole number never below 0.

Read the loop on line 18 as "for each `score` in `scores`". It is the clearest way to visit all values, and it has no
index to get wrong. The variable `score` is a copy, so changing it does not change the vector. Use the counted form when
you need the index, as line 22 does.

The last index is `size() - 1`, one less than the count. In the array of three, `speeds[3]` is a mistake: no value lives
there. C++ does not check, so the line reads memory that belongs to something else. The result is an unpredictable number
or a crash. A crash in a script stops play, and [Crash containment](../scripting/crash-containment.md) explains why the
editor survives it.

The choice has a price on each side. An array of fixed size is simple and fast. A vector is flexible, but it asks for
memory when it grows; [Data structures](../basics/data-structures.md) shows what that costs.

:::example[Sum a list by hand]
A vector holds 5, 7.5 and 2. The loop starts with `total` at 0 and adds each value in turn.

After the first value `total` is 5. After the second it is 12.5. After the third it is 14.5, and the loop ends because no
value is left. Writing the starting 0 matters: a variable without a first value holds a random number.
:::

Try it: after one more `push_back(1.0f)`, what are `size()` and `scores[3]`?

:::answer
`size()` is 4, and `scores[3]` is 1. The new value goes at the end, and the indexes count from 0.
:::

## A struct groups values under one name

A position has three numbers. A function that moves a position would take three parameters and could return only one
number, so the three would have to be sent back in pieces. Loose numbers also let you mix up their order.

A **struct** is a type that you design: it groups several values under one name.

A **member** is one named value inside a struct, and you reach it with a dot: `point.X`.

```cpp sketch="basics-programming-2-structs.cpp"
// A struct groups three floats; a function receives a copy, changes it and returns it.
#include <iostream>

struct Point
{
	float X = 0.0f;
	float Y = 0.0f;
	float Z = 0.0f;
};

Point MoveRight(Point point, float distance)
{
	point.X = point.X + distance; // the copy moves
	return point;
}

int main()
{
	Point start = { 1.0f, 2.0f, 3.0f };
	Point moved = MoveRight(start, 4.0f);
	std::cout << "start " << start.X << ", " << start.Y << ", " << start.Z << '\n';
	std::cout << "moved " << moved.X << ", " << moved.Y << ", " << moved.Z << '\n';
	return 0;
}
```

```text output-of="basics-programming-2-structs.cpp"
start 1, 2, 3
moved 5, 2, 3
```

1. **Lines 4–9:** `Point` is a struct with three `float` members; each starts at 0.
2. **Lines 11–15:** the parameter `point` is a copy of the whole struct, as every parameter is, so `start` is not changed.
3. **Line 19:** a list in braces fills the members in the order they are written.
4. **Line 20:** `moved` receives the returned copy: `start` stays at 1, 2, 3 and `moved` is at 5, 2, 3.

Strata uses structs everywhere. The library's `glm::vec3` is a struct with members `x`, `y` and `z`, and
`AssetHandle` is a struct with one member, `ID`, a number that names an asset. [Vectors](../basics/math-vectors.md)
computes with `glm::vec3`.

:::example[A handle, a value and the write-back]
Two kinds of object look alike in a script. An `Entity` holds only the number of an entity, so a copy of it still names the
same entity, and a change through the copy reaches the real one. A `glm::vec3` holds the three numbers themselves, so
`GetTranslation()` hands you a copy.

```cpp pseudocode
glm::vec3 position = GetTransform().GetTranslation(); // a copy of the numbers
position.y = position.y + 1.0f;                       // moves the copy only
GetTransform().SetTranslation(position);              // writes the copy back
```

Without the last line nothing moves. Like `MoveRight` above, you must store what changed.
:::

Try it: which one line makes `start` move in the sketch's `main`?

:::answer
`start = MoveRight(start, 4.0f);`. The call returns the moved copy, and the assignment stores it in `start`.
:::

## Text is a string

A script writes names, scores and messages. A **string** is a piece of text kept as a row of characters; in C++ the type is
`std::string`. A word in double quotes such as `"Coin"` is text, and you can keep it in a `std::string` variable.

Four things cover most uses. The sign `+` joins two strings, `==` asks whether two strings hold the same letters, and two
functions convert between numbers and text. `std::to_string` turns a number into text, and `std::stoi` turns text into a
whole number. The sketch runs all four.

```cpp sketch="basics-programming-2-text.cpp"
// Joining and comparing text, and turning numbers into text and back.
#include <iostream>
#include <string>

int main()
{
	std::cout << std::boolalpha;
	std::string name = "Coin";
	std::string label = name + " " + std::to_string(3); // + joins
	std::cout << label << '\n';
	std::cout << (name == "Coin") << '\n';  // compares the letters
	std::cout << (name == "coin") << '\n';  // capitals count
	std::cout << std::to_string(2.5f) << '\n';

	int score = std::stoi("42");
	std::cout << score + 1 << '\n';
	std::cout << std::stoi("12 coins") << '\n'; // reads the digits, stops at the space
	return 0;
}
```

```text output-of="basics-programming-2-text.cpp"
Coin 3
true
false
2.500000
43
12
```

1. **Line 9:** `std::to_string(3)` makes the text `"3"`, and `+` joins the three pieces.
2. **Lines 11–12:** `==` compares letters, and capitals count, so `"Coin"` and `"coin"` differ.
3. **Line 13:** a `float` becomes text with six digits after the point.
4. **Lines 15–17:** `std::stoi` reads digits from the front and stops at the first character that is no digit.

`Log::Info` joins numbers and text itself, so you need `std::to_string` only to build a string that you keep or pass on,
such as a label for the game's interface. `std::stoi("abc")` has no digits to read, and it cannot return a number. It
throws an exception, which is C++'s way to say "I cannot do this". [Modern C++](../basics/cpp-modern.md) explains
exceptions.

Strata contains the damage. The script library catches the exception, writes an error to the **Console**, and switches
off that script on its entity: it gets no more calls until you rebuild the scripts or press **Play** again. Other scripts and the editor continue.
[Crash containment](../scripting/crash-containment.md) says what happens to the rest.

:::example[A score in and out of text]
A script builds the line `"Score: 120"` and reads back the typed text `"120"`.

The first step is `"Score: " + std::to_string(120)`, which joins the two pieces to `Score: 120`. The second is
`std::stoi("120")`, which gives the number 120, so `120 + 30` is 150. A text such as "120 coins" also gives 120, but
"coins 120" throws, because the first character is no digit.
:::

Try it: what does `std::to_string(2.5f)` give?

:::answer
`2.500000`. The text keeps six digits after the point, so it is not always the shortest form.
:::

## Common mistakes

- **A loop with one turn too many or too few.** Symptom: a list's last value is skipped or a coin appears twice.
  Fix: write `i < count` from 0, and count the turns by hand for the smallest case, one or two.
- **A loop that never ends.** Symptom: the editor freezes and the **Console** stays empty. Fix: make sure the block changes
  what the check reads; end the editor from outside as described above.
- **A function that forgets to return.** Symptom: the call gives a number that makes no sense, and the compiler usually
  warns. Fix: every path through a function with a return type must end in `return` and a value.
- **Changing a parameter and expecting the caller's variable to change.** Symptom: the number outside is the old one.
  Fix: give the function a return type, return the new value and store it: `coins = AddBonus(coins);`.
- **Reading past the end of a list.** Symptom: wild numbers or a crash, with no message. Fix: the last index is `size() - 1`;
  prefer the range-based `for`.
- **Adding a number to text with `+`.** `"Score: " + 3` does not join: it cuts three letters off the front of the text.
  Fix: write `"Score: " + std::to_string(3)`.
- **`std::stoi` on text that is no number.** Symptom: the script stops, and the Console shows an error with the words
  `The script is disabled.` Fix: use it only on text you know holds digits.

## Summary

- You write a `while` loop with a condition checked before each turn and a `for` loop that counts from 0 while `i < count`,
  and you count the turns to avoid an off-by-one mistake.
- A function has a name, typed parameters, a body and a return value, can give defaults to its last parameters, and is called
  with arguments.
- Parameters and local variables are copies and are made again at every call, so a change never reaches the caller; return
  the result or keep it in a field.
- A `std::vector` grows with `push_back`, is visited with a range-based `for`, and counts from index 0; a struct groups values
  that you read with a dot.
- `std::to_string` makes text from a number and `std::stoi` makes a number from text, and `std::stoi` on text with no digits
  throws an exception that switches off the script.

## Check yourself

1. A loop runs `while (n < 3)` with `n = n + 1;` in its block. How many turns does it run when `n` is 5 at the start?
   A: 0. B: 1. C: 3.

   :::answer{tests="loops"}
   A. The check comes before the first turn, and `5 < 3` is false, so the block never runs. Answer B is the mistake of
   checking after the turn.
   :::

2. With `total` at 0, what is `total` after `for (int i = 1; i <= 3; i++) total = total + i;`?

   :::answer{tests="loops"}
   The answer is 6. The loop has three turns, with `i` at 1, 2 and 3, and the sums are 1, 3 and 6.
   :::

3. A function is `int Triple(int x) { x * 3; }`. What is wrong?
   A: it multiplies the wrong way. B: it never returns the result. C: `x` must be `float`.

   :::answer{tests="functions"}
   B. The statement `x * 3;` computes a number and throws it away. The function needs `return x * 3;`.
   :::

4. `Point a = { 1.0f, 2.0f, 3.0f }; Point b = a; b.X = 9.0f;` What is `a.X`?

   :::answer{tests="copies"}
   1. The line `Point b = a;` copies the struct, so `b.X = 9.0f;` changes only the copy.
   :::

5. A `std::array<int, 4>` named `values` exists. Which of `values[0]`, `values[3]` and `values[4]` is a mistake?

   :::answer{tests="lists-structs"}
   `values[4]`. The indexes are 0, 1, 2 and 3, so index 4 is past the end.
   :::

6. A script's `OnCreate` runs `int score = std::stoi("abc");`. What happens?

   :::answer{tests="text"}
   `std::stoi` throws an exception, because `"abc"` has no digits. The script library catches it, writes an error to the
   **Console**, and switches off that script on its entity.
   :::

## Practice

Run these in the `Playground` script of Programming 1, a script of its own on one empty entity. Write a function above
the line `class Playground : public Script`, and the other lines in `OnCreate`. Stop the game before you build.

1. **Basic.** Predict what `for (int i = 0; i < 3; i++) Log::Info("i = ", i);` writes. Then run it, change `<` to `<=`
   and predict again.

   :::answer[Worked solution]{tests="loops" solution="sketches/basics-programming-2-forlog.cpp"}
   Three lines, `i = 0` to `i = 2`, and with `<=` a fourth line, `i = 3`. The sketch runs both loops outside the game.

   ```cpp sketch="basics-programming-2-forlog.cpp"
   // Practice 1: what a for loop logs from 0 while i < 3, and what <= adds.
   #include <iostream>

   int main()
   {
   	for (int i = 0; i < 3; i++)
   		std::cout << "i = " << i << '\n';
   	std::cout << "--\n";
   	for (int i = 0; i <= 3; i++)
   		std::cout << "i = " << i << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-forlog.cpp"
   i = 0
   i = 1
   i = 2
   --
   i = 0
   i = 1
   i = 2
   i = 3
   ```

   1. **Lines 6–10:** the only difference is `<` or `<=`, and the second loop has one more turn.
   :::

2. **Medium.** Write a function `Clamp` with a `float value` and a `float top` that defaults to 1. It gives back 0 when
   `value` is below 0, `top` when `value` is above `top`, and `value` otherwise. Log `Clamp(1.7f)`, `Clamp(1.7f, 5.0f)` and
   `Clamp(-2.0f)`.

   :::answer[Worked solution]{tests="functions" solution="sketches/basics-programming-2-clamp.cpp"}
   The three logs are 1, 1.7 and 0. The first call uses the default top of 1.

   ```cpp sketch="basics-programming-2-clamp.cpp"
   // Practice 2: Clamp keeps a value between 0 and a top that defaults to 1.
   #include <iostream>

   float Clamp(float value, float top = 1.0f)
   {
   	if (value < 0.0f)
   		return 0.0f;
   	if (value > top)
   		return top;
   	return value;
   }

   int main()
   {
   	std::cout << Clamp(1.7f) << '\n';
   	std::cout << Clamp(1.7f, 5.0f) << '\n';
   	std::cout << Clamp(-2.0f) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-clamp.cpp"
   1
   1.7
   0
   ```

   1. **Lines 4–11:** each `return` ends the function at once, so the later lines run only for values that passed the earlier
      checks.
   :::

3. **Medium.** Make a `std::vector<float>` with the speeds 12.5, 30 and 7.5. Sum them in a range-based `for` and log the
   total.

   :::answer[Worked solution]{tests="lists-structs" solution="sketches/basics-programming-2-sum.cpp"}
   The total is 50: 12.5 + 30 = 42.5, and 42.5 + 7.5 = 50.

   ```cpp sketch="basics-programming-2-sum.cpp"
   // Practice 3: the speeds of a std::vector<float> summed in a range-based for.
   #include <iostream>
   #include <vector>

   int main()
   {
   	std::vector<float> speeds;
   	speeds.push_back(12.5f);
   	speeds.push_back(30.0f);
   	speeds.push_back(7.5f);

   	float total = 0.0f;
   	for (float speed : speeds)
   		total = total + speed;
   	std::cout << "total " << total << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-sum.cpp"
   total 50
   ```

   1. **Lines 13–14:** the loop copies each speed into `speed` and adds it to `total`, which started at 0.
   :::

4. **Hard.** Three steps, with less help each time. Step one: make the `int` variable `score` 120 and log the text `"Score: "`
   joined with `std::to_string(score)`. Then turn the text `"120"` into a number with `std::stoi` and log it plus 30.

   :::answer[Worked solution]{tests="text" solution="sketches/basics-programming-2-score.cpp"}
   The two lines are `Score: 120` and `Bonus score: 150`.

   ```cpp sketch="basics-programming-2-score.cpp"
   // Practice 4: a score turned into text, and text turned into a number.
   #include <iostream>
   #include <string>

   int main()
   {
   	int score = 120;
   	std::string line = "Score: " + std::to_string(score);
   	std::cout << line << '\n';

   	std::string typed = "120";
   	int parsed = std::stoi(typed);
   	std::cout << "Bonus score: " << parsed + 30 << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-score.cpp"
   Score: 120
   Bonus score: 150
   ```

   1. **Line 8:** `std::to_string(score)` makes the text, and `+` joins it to the label.
   2. **Line 12:** `std::stoi` gives a number, so the sum is a number, not text.
   :::

5. **Hard.** Step two: turn the number of lives, 3, into the text `"Lives: 3"`, and the text `"41"` into a number plus 1. Log
   both. Do not look at the last step.

   :::answer[Worked solution]{tests="text"}
   Use `"Lives: " + std::to_string(3)` for the first and `std::stoi("41") + 1` for the second. The Console shows `Lives:
   3` and `42`. If the first line shows `es: `, you wrote `"Lives: " + 3` and the `+` cut text. <!-- markdownlint-disable-line MD038 -->
   :::

6. **Hard.** Step three, with no help. Predict what `std::stoi("42")`, `std::stoi("42 coins")` and `std::stoi("coins")` each do.
   Write your prediction, then run the lines one at a time in `OnCreate`, with the sketch below if you want to compare.

   :::answer[Worked solution]{tests="text" solution="sketches/basics-programming-2-parse.cpp"}
   The first gives 42, and the second also 42, because `std::stoi` stops at the space. The third has no digit to read: it throws,
   the **Console** shows an error that says the script threw an exception and `The script is disabled.`, and the
   `Playground` does nothing more until you rebuild. The sketch shows the cases with digits.

   ```cpp sketch="basics-programming-2-parse.cpp"
   // Practice 6: what std::stoi makes of text that starts with digits.
   #include <iostream>
   #include <string>

   int main()
   {
   	std::cout << std::stoi("42") << '\n';
   	std::cout << std::stoi("42 coins") << '\n';
   	std::cout << std::stoi("-7") << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-parse.cpp"
   42
   42
   -7
   ```

   1. **Lines 7–9:** each call reads the leading digits and ignores the rest of the text.
   :::

7. **Hard.** Coin Run item. Make a script `CoinLine` with **Scripts ▸ New Script...** and attach it to a new empty entity.

   Write a function `PlaceCoin` that places one coin by index, and a loop that places five
   coins in a line with it. The lines that ask for and create the prefab are given. They ask for the prefab in
   `OnCreate`, check `Assets::IsLoaded` in `OnUpdate`, and use a `bool` so that the loop runs once.

   The prefab `Prefabs/Coin.stprefab` is the coin of Coin Run, the one that [Your first script](../make/first-script.md)
   gave your `Coin` script. A project of [Your first game](../start/first-game.md) has no coin prefab: download the
   project at the last checkpoint of Your first script, and do this exercise there.

   Keep this loop out of `Coin`: every coin that loop makes would run the loop again, and the number of coins would grow every
   frame until the editor stalls.

   ```cpp pseudocode
   class CoinLine : public Script
   {
   public:
   	AssetHandle m_Coin;
   	bool m_Placed = false;

   	void OnCreate() override
   	{
   		m_Coin = Assets::Find("Prefabs/Coin.stprefab");
   		Assets::RequestLoad(m_Coin);
   	}

   	void OnUpdate([[maybe_unused]] float deltaTime) override
   	{
   		if (m_Placed || !Assets::IsLoaded(m_Coin))
   			return;
   		m_Placed = true;
   		// your loop goes here
   	}
   };
   ```

   1. **Lines 4–5:** members that are not fields; the Inspector does not show them, and a hot reload resets them.
   2. **Lines 9–10:** find the prefab by its path and ask the engine to load it.
   3. **Lines 15–16:** `Instantiate` never waits, so `OnUpdate` returns until the prefab is loaded, and after the coins are placed.
   4. **Lines 17–18:** the `bool` is set before the loop, so the loop runs once, in the first frame with a loaded prefab.
   5. **Line 13:** `[[maybe_unused]]` tells the compiler that `deltaTime` stays unused on purpose, so it does not warn.

   :::answer[Worked solution]{tests="lists-structs" solution="sketches/basics-programming-2-coinline.cpp"}
   Write the function above the class, and the loop where the comment stands. Choose the position's numbers to fit your scene, and if your coin prefab has another path, write that path on line 9.

   ```cpp pseudocode
   Entity PlaceCoin(AssetHandle coin, int index)
   {
   	return Scene::Instantiate(coin, glm::vec3(index * 2.0f, 1.0f, 0.0f));
   }
   // in OnUpdate, in place of the comment:
   for (int i = 0; i < 5; i++)
   	PlaceCoin(m_Coin, i);
   ```

   Play: five coins appear in a line, 2 metres apart. The sketch computes the five positions with the same loop and a
   `PlaceCoin` that gives back a struct.

   ```cpp sketch="basics-programming-2-coinline.cpp"
   // Practice 7: PlaceCoin turns an index into a position, and a loop places five coins in a line.
   #include <iostream>

   struct Point
   {
   	float X = 0.0f;
   	float Y = 0.0f;
   	float Z = 0.0f;
   };

   Point PlaceCoin(int index, float spacing = 2.0f)
   {
   	return { index * spacing, 1.0f, 0.0f }; // the coins stand along the X axis
   }

   int main()
   {
   	for (int i = 0; i < 5; i++)
   	{
   		Point spot = PlaceCoin(i);
   		std::cout << "coin " << i << " at " << spot.X << ", " << spot.Y << ", " << spot.Z << '\n';
   	}
   	return 0;
   }
   ```

   ```text output-of="basics-programming-2-coinline.cpp"
   coin 0 at 0, 1, 0
   coin 1 at 2, 1, 0
   coin 2 at 4, 1, 0
   coin 3 at 6, 1, 0
   coin 4 at 8, 1, 0
   ```

   1. **Lines 11–14:** `PlaceCoin` turns an index into a position; `spacing` has a default of 2.
   2. **Lines 18–22:** the loop has five turns, so `i` runs from 0 to 4, and the coin at `i = 4` stands at 8.
   :::

## Where the book uses it

- [Vectors](../basics/math-vectors.md) uses functions with parameters and return values, and structs, to compute with positions.
- [Programming 3](../basics/programming-3.md) uses functions, structs and `std::vector` to build classes and references.
- [Data structures](../basics/data-structures.md) uses `std::vector` and `std::array` to compare what lists cost.
- [Finding bugs](../basics/debugging.md) uses loops and the off-by-one mistake as examples of bugs to find.

## Further reading

- Learn C++ (learncpp.com), chapters 5, 8 and 11: lessons on loops, functions, arrays and `std::vector`; beginner.
- [cppreference: for loop](https://en.cppreference.com/w/cpp/language/for): the exact rules of `for` and the range-based form; intermediate.
- [cppreference: default arguments](https://en.cppreference.com/w/cpp/language/default_arguments): where defaults may stand; intermediate.
- [cppreference: the list type](https://en.cppreference.com/w/cpp/container/vector): every operation of the list type; intermediate.
- [cppreference: the number reader](https://en.cppreference.com/w/cpp/string/basic_string/stol): what the number reader accepts and when it throws; intermediate.
