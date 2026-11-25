---
id: basics/programming-3
title: "Programming from zero III: classes, references, files of code and reading errors"
description: "Learn classes, inheritance, references, pointers, optional values, header and source files, and how to read a compile error in a Strata script."
kind: primer
size: L
tracks: [G, B, E]
needs: [basics/programming-2]
time: 120
learn:
  - id: classes
    text: write a class with a private member, a constructor and member functions, and explain that each entity gets its own object
  - id: inheritance
    text: write a derived class that overrides a function and calls its base class's version
  - id: refs-pointers
    text: predict what a call does with a value, a reference and a pointer, and write the check before a pointer or an optional value is used
  - id: files-declarations
    text: explain what a header file and a source file hold, and read the declaration of a function
  - id: compile-errors
    text: fix a compile error from the first message of the build
status: final
---

::::test-out

1. A class `Box` has a private member `int m_Count = 0;` and a public function `Add()` that adds 1 to it. You make two
   objects, `a` and `b`, and call `a.Add()` three times. What does `b` hold?

   :::answer{tests="classes"}
   The answer is 0. Each object has its own `m_Count`, so the three calls change only `a`.
   :::

2. `Gem` is a script built on the script `Coin`. Write the first line of its class, and the line inside its `OnUpdate`
   that runs `Coin`'s version first.

   :::answer{tests="inheritance"}
   `class Gem : public Coin` and `Coin::OnUpdate(deltaTime);`. The `OnUpdate` of `Gem` carries `override`.
   :::

3. What does the last line write?

   ```cpp pseudocode
   void Add(int& n) { n += 2; }
   int x = 5;
   Add(x);
   Add(x);
   Log::Info(x);
   ```

   Follow `x` through each call.

   :::answer{tests="refs-pointers"}
   `9`. The `&` makes `n` another name for `x`, so each call adds 2 to `x` itself: 5, 7, 9.
   :::

4. Which file holds the line `int GetCount() const;` of a class `Counter`, and which holds the line
   `int Counter::GetCount() const { return m_Count; }`?

   :::answer{tests="files-declarations"}
   The first is a declaration and stands in the header file, `Counter.h`. The second is the definition, with the body,
   and stands in the source file, `Counter.cpp`.
   :::

5. A build lists three errors, one under another. Which one do you read first, and why?

   :::answer{tests="compile-errors"}
   The first. A mistake early in a file often confuses the compiler about the lines after it, so the later errors
   may disappear when the first is fixed.
   :::

::::

## Why you will need this

Every script you write is a class, it lives in files, and its mistakes come back as a list of error messages. This page
teaches those three things from the beginning. Then it teaches the small tools that script code uses all the time:
references, pointers, optional values and angle brackets.

You use the ideas at once. [Debugging](../basics/debugging.md) starts from the messages you learn to read here. [The
script loop](../make/script-loop.md) adds the other functions that the engine calls on your class. The reference
for the application programming interface (API) of scripts, [Script API](../reference/script-api.md), lists declarations, and
after this page you can read them. At the end you split
your `Coin` into two files and build a `BobbingCoin` on it.

## A class keeps values and their functions together

In [Programming 2](../basics/programming-2.md) a `struct` held values, and separate functions worked on them. Nothing
stopped any function from writing a nonsense number into a coin count. A **class** is a type that holds values together
with the functions that work on them, and that can hide the values from other code.

:::question[What are the lines I have not seen yet?]
This page teaches everything with a dot, a `::` or `#include`. [Classes in C++](../basics/cpp-classes.md) teaches
`virtual` and `override`; read `virtual` as "a derived class may replace this function".
:::

Here is a purse that counts coins. Read the class first, then the lines of `main` that use it.

```cpp sketch="basics-programming-3-purse.cpp"
// A class that keeps its coin count private and offers two member functions.
#include <iostream>

class Purse
{
public:
	void Add(int coins) { m_Coins += coins; }
	int GetCoins() const { return m_Coins; }
private:
	int m_Coins = 10;
};

int main()
{
	Purse first;
	Purse second;
	first.Add(5);
	std::cout << "first has " << first.GetCoins() << '\n';
	std::cout << "second has " << second.GetCoins() << '\n';
	return 0;
}
```

```text output-of="basics-programming-3-purse.cpp"
first has 15
second has 10
```

1. **Lines 4–11:** the class `Purse`. The `;` after the closing brace belongs to the class, and people often forget it.
2. **Line 6:** code anywhere may use the members after `public:`.
3. **Line 9:** only the functions of the class may use the members after `private:`.
4. **Line 10:** `m_Coins` starts at 10. The first value stands beside the member.
5. **Lines 15–17:** two purses, and only `first` receives coins.

A **member function** is a function that belongs to a class. You call it on a variable of that class with a dot:
`first.Add(5)` runs `Add` for `first`. The word `const` after `GetCoins()` promises that the function does not change the
purse.

An **object** is one value of a class, with its own copy of every member. The output shows it: `first` holds 15 and
`second` still holds 10. Code outside the class cannot write `second.m_Coins = 3;`; the build refuses it. All changes pass
through `Add`, so one function can enforce a rule, such as refusing to add a negative number.

The engine's habit is a `m_` before the name of a private member. The members that a script shows in the editor, its
fields, are public and have no prefix: `DegreesPerSecond`.

A script class is a class like `Purse`. The engine makes one object of it for every entity that carries the script, and
each object has its own fields.

:::why[Why every entity gets its own object]
The comment above `Script` in `StrataScriptCore/Include/StrataScript/Script.h` says that the engine creates one
instance per entity. The reason is that five coins can turn at five speeds: changing `DegreesPerSecond` on one coin
changes one object. The price is that an object sees only itself. To reach the script of another entity, you ask the
entity for it with `GetScript`, shown below.
:::

:::example[Two purses by hand]
Follow `m_Coins` of both purses through `main`, and write each value after the line that changes it.

| After | `first.m_Coins` | `second.m_Coins` |
| --- | --- | --- |
| Lines 15 and 16: two objects made | 10 | 10 |
| Line 17: `first.Add(5)` | 15 | 10 |

:::

Try it: after one more call, `second.Add(7)`, what do the two purses hold?

:::answer
`first` holds 15 and `second` holds 17. Each call changes only the object it is called on.
:::

## A constructor sets the first values

A value beside the member is one way to start an object. A **constructor** is a function that runs when an object is
made, has the name of its class and has no return type. Use it when the first value depends on something you pass in.

```cpp pseudocode
Purse(int startCoins)
	: m_Coins(startCoins)
{
}
```

The line `: m_Coins(startCoins)` sets the member before the body runs. The `Entity` class of the software development kit
(SDK) for scripts uses the same form. The line `Purse rich(100);` then makes a purse that holds 100.

A script class is different: the engine must be able to make it without arguments. The comment above `Script` says that
the module makes one object when it loads, only to read the default values of the fields. Constructor code runs for that
object too, so put gameplay setup in `OnCreate`, which runs once for each entity ([Your first script](../make/first-script.md)
explains the rule).

## Inheritance builds a new class on an old one

You want coins that bob as well as spin. Copying the code of `Coin` would give two copies to keep equal.
**Inheritance** lets a class take over the members of another class and add to them.

The class that gives its members is the **base class**. Your coin's turning script is the class `Coin` of your
first script, with the same lines as the `Spinner` that the editor writes into a new project. In `class Coin : public Script`, the `Script` after the colon is the base class, and `Coin` takes over `GetEntity()`, `GetTransform()` and the empty `OnCreate` and `OnUpdate`.

The class that takes them over is the **derived class**, `Coin` here. You write `: public` before the base class's name
every time. A derived class can replace a function of its base class. The sketch below shows how, with a pickup that
gives points and a bonus pickup built on it.

```cpp sketch="basics-programming-3-pickup.cpp"
#include <iostream>

class Pickup
{
public:
	int Points = 10;
	virtual void OnCollect() { std::cout << "collected " << Points << " points\n"; }
};

class BonusPickup : public Pickup
{
public:
	void OnCollect() override { Pickup::OnCollect(); std::cout << "plus a bonus of 5\n"; }
};

int main()
{
	BonusPickup pickup;
	pickup.Points = 20;
	pickup.OnCollect();
	return 0;
}
```

```text output-of="basics-programming-3-pickup.cpp"
collected 20 points
plus a bonus of 5
```

1. **Line 7:** the base class's `OnCollect` is marked `virtual`, which allows a derived class to replace it. `Script`
   marks its `On...` functions the same way.
2. **Line 10:** `BonusPickup` is a `Pickup` and adds to it.
3. **Line 13:** `override` says that this function replaces the base class's function. If no base function has this
   name and these parameters, the compiler refuses, so a wrong name such as `OnUpdat` cannot silently never run.
4. **Line 13:** `Pickup::OnCollect();` runs the base class's version first. Without that call, the replacement would
   hide the points message.

The field `Points` belongs to `Pickup`, and the object `pickup` has it. The output shows the base version, then the bonus.

A derived script follows the same pattern. `class BobbingCoin : public Coin` has the `DegreesPerSecond` of `Coin`, and
its own `OnUpdate` can call `Coin::OnUpdate(deltaTime)` to keep the spin. The registration is where scripts differ,
because the engine reads each class's `ST_SCRIPT_CLASS` block alone and inherits nothing from the block of the base.

```cpp pseudocode
ST_SCRIPT_CLASS(BobbingCoin)
{
	ST_SCRIPT_FIELD(DegreesPerSecond); // a field of the base class, listed again
	ST_SCRIPT_FIELD(Height);           // a field of BobbingCoin itself
}
```

The first line of the block is what makes the editor show `DegreesPerSecond` on a `BobbingCoin`. `Field` accepts a member
of a base class, but you must list it.

:::caution[`GetScript<Coin>()` does not find a `BobbingCoin`]
The engine finds a script on an entity by its exact class name. On an entity whose script is `BobbingCoin`,
`GetScript<Coin>()` returns `nullptr`, although a `BobbingCoin` is a `Coin`. Ask for the class the entity carries.
:::

## A reference is another name for a variable

A function normally receives a copy of what you pass. In the first function of the next sketch, the copy grows by 5 and
the caller's variable stays as it was. A **C++ reference** is a second name for a variable that already exists. You write
it with an `&` after the type, and a function that takes one changes the caller's variable itself.

```cpp sketch="basics-programming-3-references.cpp"
// Three ways to pass a number: a copy, the caller's variable and a read-only view.
#include <iostream>

void AddByValue(int number) { number += 5; }
void AddByReference(int& number) { number += 5; }
int Twice(const int& number) { return number * 2; }

int main()
{
	int coins = 10;
	AddByValue(coins);
	std::cout << "after AddByValue: " << coins << '\n';
	AddByReference(coins);
	std::cout << "after AddByReference: " << coins << '\n';
	std::cout << "Twice: " << Twice(coins) << ", coins is " << coins << '\n';
	return 0;
}
```

```text output-of="basics-programming-3-references.cpp"
after AddByValue: 10
after AddByReference: 15
Twice: 30, coins is 15
```

1. **Line 4:** `int number` is a copy, so `number += 5` changes the copy and `coins` stays 10.
2. **Line 5:** `int& number` is another name for the caller's variable, so `coins` receives the 5.
3. **Line 6:** `const int&` is a name that can only read. It avoids a copy and cannot change the caller's variable.
4. **Lines 11–15:** the calls at lines 11, 13 and 15 look the same. Only the function's parameter decides whether the variable changes.

Use `const &` for what a function only reads and that is larger than a number. A `std::string` or a `std::vector` can
hold thousands of values, and a copy would copy them all. The SDK follows the habit: `SetTranslation` in `Entity.h` takes
a `const glm::vec3& translation`, so the function reads your vector without a copy.

:::example[Trace a reference]
A function `void Double(int& number)` doubles its argument. Start with `int gems = 4;` and call `Double(gems);` twice.

After the first call `gems` is 8, because `number` is `gems` itself. After the second call it is 16.
:::

Try it: the same function written `void Double(int number)`. What does `gems` hold after two calls?

:::answer

The answer is 4. Each call doubles a copy and throws the copy away.

:::

## A pointer says where an object lives

:::question[What are the star and the arrow?]
This page teaches pointers at the level scripts need, and [Memory in C++](../basics/cpp-memory.md) teaches them in full.
Read the `template` line in the quote as a placeholder; [Generic C++](../basics/cpp-generic.md) teaches it.
:::

A script cannot hold the script object of another entity as a value, because that object belongs to the engine. Instead
`GetScript` gives you a **pointer**: a value that says where an object is in memory. A pointer to a `Coin` has the type
`Coin*`. The quote shows `GetScript` and its neighbours in `Entity.h`.

```cpp src="StrataScriptCore/Include/StrataScript/Entity.h#L86-L92"
// Script instances on this entity, by class (must be registered with ST_SCRIPT_CLASS) or by class name.
template<typename T>
T* GetScript() const;
template<typename T>
T* AddScript();
bool HasScript(std::string_view className) const;
bool AddScript(std::string_view className);
```

The first function, `T* GetScript() const`, returns a `T*`. The comment above it says that you must register the class
with `ST_SCRIPT_CLASS`. Two things follow from the star. You reach a member through the pointer with an arrow, `->`, not
a dot, and the pointer may point to nothing.

A **null pointer** is a pointer that points to nothing, and you write it `nullptr`. `GetScript` returns it when the entity
has no script of that class. Reading a member through a null pointer crashes your scripts: the engine catches it, stops
the game and lists the crash in the Problems panel. So you check first.

```cpp sketch="basics-programming-3-pointer.cpp"
// A pointer to a coin, the check before use and a null pointer.
#include <iostream>

struct Coin
{
	int Value = 5;
};

int main()
{
	Coin gold;
	Coin* found = &gold;
	Coin* missing = nullptr;
	if (found != nullptr)
		std::cout << "found, value " << found->Value << '\n';
	if (missing == nullptr)
		std::cout << "missing points to nothing\n";
	return 0;
}
```

```text output-of="basics-programming-3-pointer.cpp"
found, value 5
missing points to nothing
```

1. **Line 12:** `&gold` gives the address of the variable `gold`. Here `&` before a variable is not the reference of a type;
   it makes a pointer value. A script rarely needs it, because `GetScript` gives you pointers.
2. **Lines 14–15:** the check `found != nullptr`, then `found->Value`. The arrow is a dot for pointers.
3. **Line 16:** `missing` is empty, so the code never reads through it.

In a script the same pattern reads like the code below. The `if` makes the variable and tests it in one line, the form
that the `OpenWorld` sample uses in `IslandHud.cpp`.

```cpp pseudocode
Entity player = Scene::FindEntityByName("Player");
if (Coin* coin = player.GetScript<Coin>())
	Log::Info("The coin spins at ", coin->DegreesPerSecond);
```

`if (coin)` is true when the pointer is not null. Fetch the pointer each time you need it: after a hot reload the engine
makes every script object again, and a pointer you stored in a member would point to an old one.

:::simplified[Pointers at the use level]
This page omits who owns an object, how long it lives, `new` and `delete`, and smart pointers. Script code never
deletes what `GetScript` returns. The rest is in [Memory in C++](../basics/cpp-memory.md).
:::

## An optional value holds a value or nothing

:::question[What is `std::optional`?]
The type `std::optional` comes from the standard library, and [Modern C++](../basics/cpp-modern.md) teaches it in full.
This section shows the three things a script does with it.
:::

Some calls cannot always answer. Asking an entity for the intensity of a light fails when the entity has no light, and
asking for a save file fails when nobody saved yet. An **optional value** is a value that may be absent, written
`std::optional<T>` with the type of the value in the brackets. The quote shows `GetProperty`, which returns one.

```cpp src="StrataScriptCore/Include/StrataScript/Entity.h#L67-L72"
// Reflected property of a component. T: bool, int32_t, uint32_t, int64_t, float, glm::vec2/3/4, glm::quat,
// std::string, Entity or AssetHandle. Enum properties are integers; colors are vec3/vec4.
template<typename T>
std::optional<T> GetProperty(std::string_view component, std::string_view property) const;
template<typename T>
bool SetProperty(std::string_view component, std::string_view property, const T& value);
```

The comment lists the types that `T` may be, from `bool` and `float` to `glm::vec3`, `std::string` and `Entity`. The
function returns an empty optional when the entity does not exist, has no such component or property, or the property
has another type. `Game::ReadSaveText` returns a `std::optional<std::string>` in the same way.

```cpp sketch="basics-programming-3-optional.cpp"
// An optional number: empty at first, then filled.
#include <iostream>
#include <optional>

int main()
{
	std::optional<float> speed;
	std::cout << "empty: " << speed.value_or(3.0f) << '\n';
	if (speed.has_value())
		std::cout << "never written\n";
	speed = 7.5f;
	if (speed.has_value())
		std::cout << "filled: " << *speed << '\n';
	return 0;
}
```

```text output-of="basics-programming-3-optional.cpp"
empty: 3
filled: 7.5
```

1. **Line 7:** a new optional starts empty.
2. **Line 8:** `value_or(3.0f)` gives the stored value, or 3 when there is none.
3. **Line 9:** `has_value()` is true when a value is there.
4. **Line 13:** `*speed` reads the value. Use it only after `has_value()`; on an empty optional the result is undefined.

For a property, the line is short:

```cpp pseudocode
const float intensity = GetEntity().GetProperty<float>("PointLight", "Intensity").value_or(-1.0f);
```

Without a point light on the entity, `intensity` holds -1, the fallback you chose. With one, it holds the light's value.
Use `value_or` when a fallback makes sense, and `has_value()` when the two cases need different code.

## Angle brackets give a template its type

You met the brackets in `std::vector<int>`. A **template argument** is the type that you write in angle brackets after
the name of a template, and it fills a placeholder in the template's declaration. In `GetProperty<float>` the argument
`float` is `T`, so the function returns a `std::optional<float>`.

You must write the argument when the compiler cannot guess it. The parameters of `GetProperty` are two names, and none has
the type `T`, so only your `<float>` can tell it. `GetScript<Coin>()` has no parameters at all. You do not write
templates yourself in this book until [Generic C++](../basics/cpp-generic.md); here you only use them.

## Files of code: headers declare, source files define

A script grows past one file. The `Coin` class of your `BobbingCoin` has to be known to the file that defines it. C++
solves this with two kinds of file.

A **declaration** is a line that tells the compiler that a name exists and what type it has, without the body.

A **header file**, ending in `.h`, holds the declarations of a class.

A **source file**, ending in `.cpp`, holds the definitions: the bodies of the functions. Here is the purse in two files.

```cpp pseudocode
#pragma once

class Purse
{
public:
	void Add(int coins);
	int GetCoins() const;
private:
	int m_Coins = 10;
};
```

1. **Line 1:** `#pragma once` is the first line of every header. It makes the compiler read the file only once per source
   file.
2. **Lines 6–7:** two declarations. The functions end with `;` and have no body here.
3. **Line 9:** the private member stays in the header, because every file that makes a `Purse` must know its size.

The functions get bodies in the source file.

```cpp pseudocode
#include "Purse.h"

void Purse::Add(int coins) { m_Coins += coins; }
int Purse::GetCoins() const { return m_Coins; }
```

The `Purse::` before each name says which class the function belongs to, as `Key::Space` named a key in [Programming
1](../basics/programming-1.md). An **include directive** is a line starting with `#include`; the compiler replaces it with
the text of the named file. Quotes, as in `"Purse.h"`, name a file of your own, and angle brackets, as in `<optional>`,
name a library header.

Any other file that uses `Purse` writes `#include "Purse.h"` at its top and then calls `Add` and `GetCoins` through the
header. It never needs to see the bodies. The build compiles each `.cpp` file alone, so a change inside `Purse.cpp`
compiles one file again; [the build](../basics/build.md) explains how the pieces join.

:::caution[Why `#pragma once`]
A file that includes `Purse.h` directly and through another header would read the class twice. The compiler stops: for
the file `Twice.cpp` that includes `Purse.h` two times, GCC prints `error: redefinition of 'class Purse'`. With
`#pragma once` as the first line the second include does nothing. Older code reaches the same end with an include guard,
a few lines of `#ifndef`; [the build](../basics/build.md) names it.
:::

Strata adds three rules for the files of a script project.

- Every `.cpp` and `.h` file in the project's `Scripts` folder, and in folders below it, belongs to the script module,
  except in folders whose names start with a dot. You keep no list: a new file joins the module at the next build.
- `ST_SCRIPT_CLASS(Coin)` stands once per class, in the class's `.cpp` file, never in a header. The macro makes a
  registration in every source file that includes it, so a header that two files include registers `Coin` twice, and the
  engine reports `class 'Coin' is registered twice` when it loads the module.
- Each field gets its line `ST_SCRIPT_FIELD(Name);` in that block, and the setup of a script goes in `OnCreate`, as the
  constructor section said.

## Reading a declaration

The reference pages of this book show declarations from the SDK headers. Each follows one pattern: the return type, the
name, the parameters in brackets, then words such as `const`. Take this line from `Entity.h`.

`bool SetParent(Entity parent, bool keepWorldTransform = true);`

The return type `bool` comes first: the function answers yes or no. The name is `SetParent`. Two parameters follow, each
as its type and its name. The second has a default after the `=`, so `child.SetParent(parent)` is a valid call. The final
`;` says that this line is a declaration only.

| Declaration | How to read it |
| --- | --- |
| `std::string GetName() const;` | Returns a `std::string`, takes nothing, and does not change the entity (`const`). |
| `static bool IsKeyDown(KeyCode key)` | `static` marks a function you call on the class itself: `Input::IsKeyDown(Key::Space)`. No object is needed. |
| `static float GetGamepadAxis(GamepadAxis axis, uint32_t gamepad = 0, float deadZone = c_DefaultDeadZone)` | Needs one argument, `axis`. The other two have defaults; the last default is a named constant. |
| `static std::optional<std::string> ReadSaveText(std::string_view name)` | A function of the class `Game`; it returns the text of a save file, or an empty optional. |

An enum's declaration lists its names. The one below is `GamepadAxis` from `Input.h`.

```cpp src="StrataScriptCore/Include/StrataScript/Input.h#L196-L204"
enum class GamepadAxis : uint32_t
{
	LeftX = 0,
	LeftY = 1,
	RightX = 2,
	RightY = 3,
	LeftTrigger = 4,
	RightTrigger = 5
};
```

`enum class` makes the names scoped, so you write `GamepadAxis::LeftX`. The part `: uint32_t` says what whole number
type holds it, and a number after a name, such as the 0 of `LeftX`, is its value. A few more words appear in nearly every SDK header.

| Word | What to read |
| --- | --- |
| `std::string_view` | Text that the function only reads. A string literal and a `std::string` both fit, without a copy. A view does not own the characters, so copy the text into a `std::string` to keep it. See [Modern C++](../basics/cpp-modern.md). |
| `uint32_t`, `uint64_t` | Whole numbers that are never negative. The `u` is for unsigned, and the number is the bits: 32 bits count from 0 to 4,294,967,295. See [Numbers](../basics/numbers.md). |
| `template<typename T>` | A line before a template; `T` is the placeholder that a template argument fills. See [Generic C++](../basics/cpp-generic.md). |
| `explicit` | Before a constructor of one parameter: the compiler never converts a value silently. `Entity(5)` is allowed; `Entity e = 5;` is not. |
| `[[maybe_unused]]` | Before a parameter that the body may not use. The callbacks of `Script` carry it so that the compiler does not warn. |
| `constexpr` | The value can be computed at compile time, before the program runs. See [Modern C++](../basics/cpp-modern.md). |
| `= default` | The compiler writes the usual version of this function. `constexpr Entity() = default;` is the empty constructor. |

Try it: read `static void SetTimeScale(float timeScale)`.

:::answer
The function returns nothing (`void`), takes one `float`, and is `static`, so you call it on the class: `Time::SetTimeScale(0.5f)`.
:::

## Reading a compile error

You press **Ctrl+B** and the build fails. A **compile error** is a message of the compiler that says that your source breaks
a rule of the language, so no program comes out.

**Compile time** is the stretch when the compiler reads your source, before anything runs. Every compile error appears
then, never while the game plays.

Four habits cover most errors.

1. Read the first error first. Later errors often follow from it, and fixing the first can remove them all.
2. Read the file and line in the message, and look at the line before it too.
3. Change one thing, then build again.
4. Read the message in words. It usually names what the compiler could not find or match.

Here is a function with a missing `;`. The :term[pseudocode]{id=pseudocode} shows the file as written.

```cpp pseudocode
int main()
{
	int coins = 3
	int bonus = 2;
	return coins + bonus;
}
```

The compiler printed these lines, from the file `Scripts/Wallet.cpp`. Each message reads `file:line:column: error: text`.

```text
Scripts/Wallet.cpp: In function 'int main()':
Scripts/Wallet.cpp:4:9: error: expected ',' or ';' before 'int'
Scripts/Wallet.cpp:5:24: error: 'bonus' was not declared in this scope
```

The first error points at line 4, not line 3, where the `;` is missing. The compiler read `int coins = 3`, saw `int` where
it expected `;`, and stopped there. The second error follows from the first: because line 4 did not count as a
declaration, `bonus` does not exist. Add the `;` at the end of line 3, and both messages go.

:::example[Three errors, one cause]
A file `Shop.cpp` forgets to include the header of `Purse`. These messages are real output.

```text
Scripts/Shop.cpp: In function 'int main()':
Scripts/Shop.cpp:3:9: error: 'Purse' was not declared in this scope
Scripts/Shop.cpp:4:9: error: 'purse' was not declared in this scope
Scripts/Shop.cpp:5:21: error: invalid conversion from 'const char*' to 'int' [-fpermissive]
```

The first error says that the name `Purse` is unknown. A missing `#include` looks like any unknown name, because to the
compiler the class does not exist. The second error is a knock-on: `purse` was never made. The third error is separate:
line 5 assigns text to `total`, an `int`, a wrong type.
:::

Try it: which error do you fix, and how?

:::answer
The first: add `#include "Purse.h"` at the top of `Shop.cpp`. The second error then goes. Build again, and fix the third by
giving `total` a number, or by making it a `std::string`.
:::

The wording differs between compilers. Visual Studio's compiler writes a code and the file as `file(line,column)`:
`error C2065: 'speed': undeclared identifier` means an unknown name, the same as `was not declared`. The words to search for
are the same on every platform:

- `expected ';'`: a `;` is missing, at the end of the line before the one named.
- `was not declared` or `undeclared identifier`: a spelling mistake, a missing `#include`, or a missing `Strata::`.
- `invalid conversion` or `cannot convert`: a value of the wrong type.
- `redefinition of`: a header without `#pragma once` that two includes read twice.

The **Problems** panel shows the same list. Each error is a row with a red icon, the message (with its code, when the
compiler gives one), the file and the line. A line at the top counts the rows, for example `Build 3 failed: 2 errors, 0
warnings.` The rows keep the compiler's order, so the first row is the first error. To jump to the
mistake, double-click its row: your code editor opens the file at the line. A build that **Play** starts and that fails
opens the panel for you.

A warning is a row with a triangle. It marks code that the compiler accepts but doubts, such as a conversion that may lose
digits. A warning does not stop the build: the panel says `Build 4 succeeded with 1 warning.`, and the module loads. Read
warnings, because they often point at a real mistake, but fix errors first.

Some errors come from the SDK on purpose. A `double` field is a likely first attempt, because `double` is a type you know.
For a file `Coin.cpp` that lists `ST_SCRIPT_FIELD(DegreesPerSecond);` on its line 13, with the member declared as `double`,
GCC on Linux prints:

```text
In file included from StrataScriptCore/Include/StrataScript/StrataScript.h:21,
                 from Scripts/Coin.cpp:1:
Scripts/Coin.cpp:13:2:   required from here
StrataScriptCore/Include/StrataScript/Script.h:785:47: error: static assertion failed: Unsupported script field type: use bool, int32_t, float, glm::vec2/3/4, glm::quat, std::string, Strata::Entity or Strata::AssetHandle
```

The output omits the code lines that the compiler prints beside each message, and the long line that names the template.
The first error points into `Script.h`, a file you did not write. Your own line is in the lines above it: `Scripts/Coin.cpp:13:2:
required from here`.

Try it in your `Playground` script, whose field `Speed` no other code reads: write `double Speed` instead of `float Speed`
and build. The Problems panel keeps only the rows of errors and warnings, and every row of this build names `Script.h`.
Visual Studio's compiler gives three: `C2338` with `static assertion failed` and the message above, then `C2027` and
`C2065`, two knock-ons. No row names your file.

Your line is in the build's output, which the **Console** shows: type `Playground.cpp(` in its **Search** box. On Windows
the search shows two lines that end in `Scripts\Playground.cpp(<line>,2):`, where `<line>` is the line of
`ST_SCRIPT_FIELD(Speed);`: 28 in the file that **New Script** wrote, later if you added lines above it. Clear the search to
read the line below the first: `see reference to function template instantiation`, and the name of the template.

A `double` that code passes to a function of `float` values fails earlier, in your own file. Make the same change in the
`Coin` of [Your first script](../make/first-script.md), and both rows name `Coin.cpp` at the line of `glm::angleAxis`:
`C2672` says that no `angleAxis` matches, and `C2737` that `turn` has no value.

The fix is a field type from the message's list: `float` here. [Fields in the editor](../make/script-fields.md) lists them
all.

## Common mistakes

- **A function changes a copy.** Symptom: the caller's variable keeps its value. Fix: take the parameter by reference,
  `int& number`.
- **A pointer is used without a check.** Symptom: the script crashes when the entity lacks the script. Fix: test
  `if (pointer)` or `!= nullptr` before `->`.
- **`GetScript<Coin>()` on an entity whose script is `BobbingCoin`.** Symptom: `nullptr`, though the entity has a coin
  script. Fix: ask for the exact class the entity carries.
- **`*value` on an empty optional.** Symptom: garbage or a crash. Fix: `value_or(fallback)`, or test `has_value()` first.
- **`ST_SCRIPT_CLASS` in a header, or a function body in a header that two files include.** Symptom: `class 'Coin' is
  registered twice` or a redefinition error. Fix: registration and bodies go in the `.cpp`; keep `#pragma once` in the
  header.
- **A missing `;` after a class's closing brace.** Symptom: an error at the next line, not at the brace. Fix: end the
  class with `};`.
- **Fixing the last error first.** Symptom: you chase messages that disappear later anyway. Fix: fix the first row, then
  build again.

## Summary

- A class keeps values and their member functions together, hides what is `private`, starts with a constructor or a first
  value, and the engine makes one object of a script class for each entity.
- A derived class takes over its base class's members, replaces a function with `override` and can call
  `Coin::OnUpdate(deltaTime)`; a script lists a base class's field again in its own registration.
- A parameter with `&` changes the caller's variable, `const &` avoids a copy, a pointer is checked against `nullptr`
  before `->`, and an optional value is read with `value_or` or after `has_value()`.
- A header declares and a source file defines; `#include` copies a header in; a declaration reads as return type, name,
  parameters with defaults, then `const` or `static`.
- You read a compile error from the first message, at its file and line, and the Problems panel lists the errors in that order.

## Check yourself

1. A class `Lamp` has a private `bool m_On = false;` and a public function `Switch()` that flips it. You make two lamps,
   `a` and `b`, and call `a.Switch();`. Can `main` write `a.m_On = true;`, and what does `b` hold?

   :::answer{tests="classes"}
   No: the member is private, so the build refuses the line. `b` holds `false`, because each object has its own `m_On`
   and the call changed only `a`.
   :::

2. `Gem` is derived from `Coin`. Its `void OnUpdate(float deltaTime) override {}` has an empty body, and gems stop
   spinning although `Coin::OnUpdate` spins. Why, and what fixes it?

   :::answer{tests="inheritance"}
   The empty function replaces the base class's version, so the spin never runs. Call `Coin::OnUpdate(deltaTime);` as the
   first line of the body.
   :::

3. An entity carries a `BobbingCoin` script, and `BobbingCoin` is derived from `Coin`. What does
   `entity.GetScript<Coin>()` return? Is it A, a pointer to the `BobbingCoin`; B, `nullptr`; C, a compile error; or D, a
   `std::optional<Coin>`?

   :::answer{tests="inheritance"}
   B. The engine finds scripts by their exact class name, and the name on this entity is `BobbingCoin`. Asking for
   `GetScript<BobbingCoin>()` returns the pointer.
   :::

4. Read `static float GetGamepadAxis(GamepadAxis axis, uint32_t gamepad = 0, float deadZone = c_DefaultDeadZone)`. What
   does it return, and which call is valid?

   :::answer{tests="files-declarations"}
   The function returns a `float`. `Input::GetGamepadAxis(GamepadAxis::LeftX)` is valid: the function is `static`, so you
   call it on `Input`, and the two parameters with defaults may be omitted.
   :::

5. The build prints `Scripts/Wallet.cpp:4:9: error: expected ',' or ';' before 'int'` and a second error about `bonus`.
   Which line do you edit, and what happens to the second error?

   :::answer{tests="compile-errors"}
   Edit line 3, the line before the one named: add the missing `;` at its end. The second error is a knock-on and
   disappears with the first.
   :::

6. Write one line that reads the text of the save file `"Slot 1"` into a `const std::string` and uses `"empty"` when there is
   no such file.

   :::answer{tests="refs-pointers"}
   `const std::string text = Game::ReadSaveText("Slot 1").value_or("empty");`. `ReadSaveText` returns a
   `std::optional<std::string>`, and `value_or` supplies the fallback.
   :::

## Practice

Run exercises 1 to 4 in your `Playground` script, and stop the game before each build. Exercise 5 changes your Coin Run
project.

1. **Basic.** Above the class `Playground`, write `void Double(int number)` and `void DoubleInPlace(int& number)`; each sets
   `number` to `number * 2`. In `OnCreate`, make `int gems = 4;` and log it after `Double(gems)`, after
   `DoubleInPlace(gems)` and after a second `DoubleInPlace(gems)`. Predict the three numbers before you build, then
   play and compare.

   :::answer[Worked solution]{tests="refs-pointers" solution="sketches/basics-programming-3-practice-reference.cpp"}
   The Console shows 4, 8 and 16. The first call doubles a copy, the second doubles `gems` itself, and the third doubles it
   again. The program below does the same in plain C++.

   ```cpp sketch="basics-programming-3-practice-reference.cpp"
   // Practice 1: a number passed by value and by reference.
   #include <iostream>

   void Double(int number) { number = number * 2; }
   void DoubleInPlace(int& number) { number = number * 2; }

   int main()
   {
   	int gems = 4;
   	Double(gems);
   	std::cout << "after Double: " << gems << '\n';
   	DoubleInPlace(gems);
   	std::cout << "after DoubleInPlace: " << gems << '\n';
   	DoubleInPlace(gems);
   	std::cout << "after a second DoubleInPlace: " << gems << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-programming-3-practice-reference.cpp"
   after Double: 4
   after DoubleInPlace: 8
   after a second DoubleInPlace: 16
   ```

   1. **Line 4:** the parameter is a copy, so the doubling vanishes with the copy.
   2. **Line 5:** the parameter is `gems` itself, so the doubling stays.
   :::

2. **Medium.** Write a class `Counter` with a private `int m_Count`, a constructor that takes the start value, and two public
   member functions: `Increase()` adds 1 and `GetCount()` returns the count. Put the class in `Counter.h` and the function
   bodies in `Counter.cpp`, both in the project's `Scripts` folder. In `Playground.cpp`, include the header, make
   `Counter counter(3);`, call `Increase()` twice and log `GetCount()`.

   :::answer[Worked solution]{tests="classes files-declarations" solution="sketches/basics-programming-3-practice-counter.cpp"}
   The Console shows 5. The header holds the class with the declarations and `#pragma once`; the source file starts with
   `#include "Counter.h"` and defines each function with `Counter::`. The program below joins both files into one, with
   a comment where each begins.

   ```cpp sketch="basics-programming-3-practice-counter.cpp"
   #include <iostream>

   // The class as Counter.h declares it.
   class Counter
   {
   public:
   	Counter(int start);
   	void Increase();
   	int GetCount() const;
   private:
   	int m_Count = 0;
   };

   // The functions as Counter.cpp defines them.
   Counter::Counter(int start) : m_Count(start) {}
   void Counter::Increase() { m_Count++; }
   int Counter::GetCount() const { return m_Count; }

   int main()
   {
   	Counter counter(3);
   	counter.Increase();
   	counter.Increase();
   	std::cout << "count is " << counter.GetCount() << '\n';
   }
   ```

   ```text output-of="basics-programming-3-practice-counter.cpp"
   count is 5
   ```

   1. **Lines 4–12:** the class as the header declares it.
   2. **Line 15:** the constructor sets `m_Count` to the start value before its empty body runs.
   3. **Lines 16–17:** the other two definitions; `const` repeats from the declaration.
   4. **Line 21:** `Counter counter(3);` starts the object at 3.
   :::

3. **Medium.** In the Inspector, add a point light component to the entity of `Playground`. In `OnCreate`, read its `Intensity`
   with `GetProperty<float>` and a fallback of -1. Then ask the entity for its own `Playground` script and log its field
   `Speed`, guarded by a check. Last, define an empty script class `class Unused : public Script {};` above `Playground`, register it with
   `ST_SCRIPT_CLASS(Unused) {}`, and ask for it the same way: it is on no entity.

   :::answer[Worked solution]{tests="refs-pointers"}
   In code, the component's name is `PointLight`. The lines below do all three jobs.

   ```cpp pseudocode
   const float intensity = GetEntity().GetProperty<float>("PointLight", "Intensity").value_or(-1.0f);
   Log::Info("Playground.OnCreate: intensity ", intensity);
   if (Playground* self = GetEntity().GetScript<Playground>())
   	Log::Info("Playground.OnCreate: Speed is ", self->Speed);
   if (Unused* unused = GetEntity().GetScript<Unused>())
   	Log::Info("Playground.OnCreate: found an Unused script");
   else
   	Log::Info("Playground.OnCreate: no Unused script on this entity");
   ```

   The Console shows the light's intensity, the value of `Speed`, and the last line, because `GetScript<Unused>()` is
   `nullptr`. Remove the light and play again: the first line shows -1, the fallback. Above it the engine writes a
   warning, once per play, that ends `has no PointLight component`: a call that cannot do its job says why, and still
   gives back an empty optional.
   :::

4. **Hard.** Start from an empty `OnCreate`: delete the lines of exercises 1 to 3 from it, and the line
   `#include "Counter.h"` that exercise 2 added at the top. Keep the files `Counter.h` and `Counter.cpp`. Then add these
   four lines to `OnCreate`. They hold three planted errors: a missing `;`, an unknown name and a
   missing include.

   Build once, then fix the errors one at a time, always from the first row of the Problems panel, and
   build again after each fix.

   ```cpp pseudocode
   int coins = 3
   Log::Info("Playground.OnCreate: coins ", coins);
   Log::Info("Playground.OnCreate: bonus ", bonus);
   Counter counter(1);
   ```

   Expect more than three rows at first, because one mistake can cause others.

   :::answer[Worked solution]{tests="compile-errors"}
   The first row names the line of the missing `;` or the line below it, depending on the compiler. Visual Studio's
   compiler shows five rows: `C2143` with `missing ';'` on the line below, `C2065` for `bonus`, `C2065` for `Counter`,
   and two knock-ons about `counter`. Add the `;` and build.

   The next first row says that `bonus` is unknown: write `int bonus = 2;` above its line. The last says that `Counter` is
   unknown: add `#include "Counter.h"` at the top of `Playground.cpp`, as in exercise 2. After the third build the panel
   reads `Build N succeeded.` and the Console shows the two lines.

   A `Counter` row that comes first means that a line above the four still uses `Counter`, a line of exercise 2 that
   stayed in `OnCreate`. The compiler reports in the order of the file.
   :::

5. **Hard.** Start from Coin Run and its coin prefab, as [Your first script](../make/first-script.md) left them. Split its
   `Coin.cpp` into a class `Coin` in `Coin.h` and its body in `Coin.cpp`, with its field `DegreesPerSecond`. Then write a
   class `BobbingCoin`, derived from `Coin`, that keeps the spin and also moves up and down by a field `Height`. Put
   `BobbingCoin` on the coin prefab in the place of `Coin`, and play.

   To change the prefab, select one coin. In its Script component, press the cross of `Coin` to remove it, then open
   **Add Script...** and pick `BobbingCoin`. Open the menu of the Script component and choose **Apply to Prefab**: the
   other four coins change too.

   :::answer[Worked solution]{tests="classes inheritance files-declarations" solution="sketches/basics-programming-3-practice-coinrun.cpp"}
   Start with the header. It declares the class and its function and uses `Strata::Script`, because a header does not
   say `using namespace`.

   ```cpp pseudocode
   #pragma once

   #include "StrataScript/StrataScript.h"

   class Coin : public Strata::Script
   {
   public:
   	float DegreesPerSecond = 90.0f;

   	void OnUpdate(float deltaTime) override;
   };
   ```

   1. **Line 5:** the class is built on the engine's `Script`.
   2. **Line 10:** only the declaration of `OnUpdate` stands here; its body is in `Coin.cpp`.

   The source file defines `OnUpdate` and registers the class once.

   ```cpp pseudocode
   #include "Coin.h"

   using namespace Strata;

   void Coin::OnUpdate(float deltaTime)
   {
   	TransformComponent transform = GetTransform();
   	const glm::quat turn = glm::angleAxis(glm::radians(DegreesPerSecond * deltaTime), glm::vec3(0.0f, 1.0f, 0.0f));
   	transform.SetRotation(turn * transform.GetRotation());
   }

   ST_SCRIPT_CLASS(Coin)
   {
   	ST_SCRIPT_FIELD(DegreesPerSecond);
   }
   ```

   1. **Line 5:** `Coin::` says that this is the body of the declared function.
   2. **Line 12:** the registration stands in the `.cpp`, never in the header.

   `BobbingCoin` stores the height of the coin in `OnCreate`, and each frame sets the height to that base plus a sine wave.

   ```cpp pseudocode
   class BobbingCoin : public Coin
   {
   public:
   	float Height = 0.25f;

   	void OnCreate() override { m_BaseHeight = GetTransform().GetTranslation().y; }
   	void OnUpdate(float deltaTime) override
   	{
   		Coin::OnUpdate(deltaTime);
   		m_Time += deltaTime;
   		TransformComponent transform = GetTransform();
   		glm::vec3 position = transform.GetTranslation();
   		position.y = m_BaseHeight + Height * std::sin(m_Time * 2.0f);
   		transform.SetTranslation(position);
   	}
   private:
   	float m_BaseHeight = 0.0f;
   	float m_Time = 0.0f;
   };
   ```

   1. **Line 6:** the script stores the base height once, so the coin bobs around where you placed it.
   2. **Line 9:** the first line of the new work runs the spin of `Coin`.
   3. **Line 13:** the bob sets only the height and keeps the other two coordinates.

   Put the class, with the include of `Coin.h` and `using namespace Strata;` above it, in `BobbingCoin.cpp`, and add its
   registration. The block lists
   the field of the base class again, as the inheritance section said.

   ```cpp pseudocode
   ST_SCRIPT_CLASS(BobbingCoin)
   {
   	ST_SCRIPT_FIELD(DegreesPerSecond);
   	ST_SCRIPT_FIELD(Height);
   }
   ```

   Stop the game before a build: a build during **Play** makes the objects again, so `m_BaseHeight` would start over at 0.
   The program below has the same shape in plain C++. Its base class `Coin` turns by 90 degrees per second, and one
   `OnUpdate` of 0.5 seconds moves the angle to 45 degrees; the bob follows the angle.

   ```cpp sketch="basics-programming-3-practice-coinrun.cpp"
   #include <cmath>
   #include <iostream>

   class Coin
   {
   public:
   	float Angle = 0.0f;
   	virtual void OnUpdate(float deltaTime) { Angle += 90.0f * deltaTime; }
   };

   class BobbingCoin : public Coin
   {
   public:
   	void OnUpdate(float deltaTime) override
   	{
   		Coin::OnUpdate(deltaTime);
   		std::cout << "angle " << Angle << ", offset " << 0.5f * std::sin(Angle * 0.01745f) << '\n';
   	}
   };

   int main()
   {
   	BobbingCoin coin;
   	coin.OnUpdate(0.5f);
   }
   ```

   ```text output-of="basics-programming-3-practice-coinrun.cpp"
   angle 45, offset 0.353501
   ```

   1. **Line 8:** the base class's `OnUpdate` adds 90 degrees per second of the time given.
   2. **Line 16:** the derived function runs the base class's work first.
   3. **Line 17:** then it adds its own work, a sine of the angle.
   4. **Line 24:** half a second turns the coin 45 degrees.
   :::

## Where the book uses it

- [Debugging](../basics/debugging.md) uses compile errors and the Problems panel as the first kind of bug to read.
- [The script loop](../make/script-loop.md) uses classes, `override` and the calls that the engine makes on your class.
- [The build](../basics/build.md) uses header and source files, `#include` and `#pragma once` to explain what the compiler
  and the linker do with them.
- [The script API reference](../reference/script-api.md) uses declarations, `static`, defaults, `std::optional` and template
  arguments in every entry.

## Further reading

- Learn C++ (learncpp.com), chapters 13 to 15 and 2: lessons on classes, constructors, references, and header and source
  files; beginner.
- [cppreference: classes](https://en.cppreference.com/w/cpp/language/classes): the exact rules of `class`, access and
  members; intermediate.
- [cppreference: derived classes](https://en.cppreference.com/w/cpp/language/derived_class): inheritance and `override`;
  intermediate.
- [cppreference: reference declaration](https://en.cppreference.com/w/cpp/language/reference): `&` in types and `const &`;
  intermediate.
- [cppreference: optional values](https://en.cppreference.com/w/cpp/utility/optional): `has_value`, `value_or` and `*`;
  intermediate.
