---
id: basics/cpp-classes
title: "C++ classes in depth: inheritance, virtual calls and interfaces"
description: "Learn how a derived class is built, how a virtual call reaches the right function, and how an interface lets engine code call code written later."
kind: primer
size: M
tracks: [B, E]
needs: [basics/cpp-memory]
time: 90
learn:
  - id: inheritance-order
    text: predict the order in which the constructors and destructors of a base class and a derived class run
  - id: virtual-call
    text: explain how a call through a base reference reaches the derived class's function, and what the call costs
  - id: interfaces
    text: write an abstract class with a pure virtual function, two implementations and a call through the base
  - id: destructor-slicing
    text: find the two mistakes of deleting through a base without a virtual destructor and of copying into a base value
  - id: operators
    text: write the addition and the equality operators for a small struct
status: final
---

::::test-out

1. Class `B` derives from class `A`. Each constructor and destructor writes its own class name. In which order do four names appear for one `B` object that is made and then goes out of scope?

   :::answer{tests="inheritance-order"}
   `A` (the base is built first), `B`, `B` (the derived class is destroyed first), `A`. The destructors run in the reverse order of the constructors.
   :::

2. A `Shape` has a function `Area` that returns 0, and `Square` derives from it and returns 16. The code `const Shape& shape = square; shape.Area();` runs. What does it give when `Area` is `virtual` in `Shape`, and what when it is not?

   :::answer{tests="virtual-call"}
   16 with `virtual`: the call looks at the real class of the object. 0 without it: the compiler picks the function from the type of the reference, which is `Shape`.
   :::

3. Write the line that declares a pure virtual function `Draw` with no parameters and no result in a class `Widget`.

   :::answer{tests="interfaces"}
   `virtual void Draw() = 0;`. The `= 0` gives the function no body, so `Widget` becomes an abstract class and a derived class must write `Draw`.
   :::

4. `Pickup* pickup = new Coin(); delete pickup;` runs, and the destructor of `Pickup` is not virtual. Which destructors run, and is that allowed?

   :::answer{tests="destructor-slicing"}
   Usually only the destructor of `Pickup` runs, and what `Coin` added is never cleaned up. The C++ rules call this undefined behavior; a virtual destructor in `Pickup` fixes it.
   :::

5. A struct `Money` holds one `int` named `Cents`. Write the line that adds two `Money` values with `+`.

   :::answer{tests="operators"}
   `Money operator+(const Money& other) const { return Money { Cents + other.Cents }; }`. The function is a member, so the left value is `this` and the right value is `other`.
   :::

::::

## Why you will need this

Every script you wrote is a class that derives from `Script`, and the engine calls your `OnUpdate` without knowing your class. This page explains the machinery behind that call and the habits that keep it safe.

Three later pages use it. [Generic C++](../basics/cpp-generic.md) builds templates on top of classes. [Engine modules](../core/engine-modules.md) shows the engine's services as classes behind one interface. [Windows, events and layers](../core/windows-events.md) reads `Window` and `Event`, which are :term[base classes]{id=base-class}. The last exercise makes pickups that share a base class.

This page needs no download. Only the Practice needs a project: the one that holds your `Playground` script, which [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own) puts on an empty entity.

Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), three pages on. On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A derived class contains its base

Suppose Coin Run grows from coins to speed boosts and shields. Each needs a name, a value and a way to say "I was collected". Copying that code into three classes means three places to fix one mistake.

**Inheritance** lets one class build on another, as [Programming 3](../basics/programming-3.md) showed for scripts. In `class Coin : public Pickup`, `Pickup` is the base class and `Coin` is the :term[derived class]{id=derived-class}. A `Coin` object holds everything a `Pickup` holds, followed by what `Coin` adds, so a `Coin` is a `Pickup` in every place the code asks for one.

Members have an access level. A `public` member is open to all code. A `protected` member is open to the class and its derived classes. A `private` member is open to the class alone. The word `public` before the base name keeps the base's public members public in the derived class; this page uses only that form.

A derived object is built in layers, and the order matters. Read the sketch before you run it, and write down the four lines you expect.

```cpp sketch="basics-cpp-classes-order.cpp"
// A base class and a derived class: the order of their constructors and destructors.
#include <iostream>

class Pickup
{
public:
	Pickup() { std::cout << "Pickup built\n"; }
	~Pickup() { std::cout << "Pickup destroyed\n"; }
};

class Coin : public Pickup
{
public:
	Coin() { std::cout << "Coin built\n"; }
	~Coin() { std::cout << "Coin destroyed\n"; }
};

int main()
{
	Coin coin;
	return 0;
}
```

```text output-of="basics-cpp-classes-order.cpp"
Pickup built
Coin built
Coin destroyed
Pickup destroyed
```

1. **Line 11:** `: public Pickup` makes `Coin` a derived class.
2. **Line 20:** one `Coin` object runs the :term[constructor]{id=constructor} of `Pickup` first and the constructor of `Coin` second; at the closing brace the :term[destructors]{id=destructor} run in the opposite order.

The base is built first because the derived constructor may use it, and destroyed last for the same reason. A derived class's own members sit between the two: the base, then the members in the order written, then the body of the derived constructor. Destruction reverses all of it. `Script` shows why the order is useful: its constructor stores the entity the script belongs to, so `GetEntity()` already works when the constructor of your own class starts. Still, put game set-up in `OnCreate`: the engine also builds one object of each script class with no entity, to read the default values of its fields.

## A virtual function runs the object's own version

A game keeps one list of pickups and calls the same function on each. The list holds `Pickup` pointers or references, because a list has one element type. The question is which `OnCollected` runs when the real object is a `Coin`.

By default the compiler decides from the declared type, before the program runs. A **virtual function** is a :term[member function]{id=member-function} whose call through a base pointer or reference runs the version of the object's real class, decided while the program runs. Compare the two kinds side by side.

```cpp sketch="basics-cpp-classes-virtual.cpp"
// A call through a base reference: Describe is not virtual, OnCollected is.
#include <iostream>

class Pickup
{
public:
	virtual ~Pickup() = default;
	void Describe() const { std::cout << "a pickup\n"; }
	virtual void OnCollected() const { std::cout << "pickup collected\n"; }
};

class Coin : public Pickup
{
public:
	void Describe() const { std::cout << "a coin\n"; }
	void OnCollected() const override { std::cout << "coin collected\n"; }
};

int main()
{
	Coin coin;
	const Pickup& pickup = coin;
	pickup.Describe();
	pickup.OnCollected();
}
```

```text output-of="basics-cpp-classes-virtual.cpp"
a pickup
coin collected
```

1. **Line 9:** `virtual` in the base makes `OnCollected` a virtual function.
2. **Line 16:** `override` asks the compiler to check that this function replaces a virtual one of the base.
3. **Line 22:** the reference has the type `Pickup` but names a `Coin`.
4. **Lines 23–24:** `Describe` runs the base version, `OnCollected` the derived one.

The word `override` is a safety net. If the derived function differs by a letter or by a missing `const`, the compiler stops with an error; without `override` it would quietly make a second, unrelated function. The word `final` closes a door: a `final` function cannot be overridden again, and a `final` class cannot be a base. Strata marks `EditorActionGroup` as `final`, because nothing derives from a group of undo steps.

:::example[A wrong letter that `override` catches]
`SpeedBoost` derives from `Pickup` and declares `void OnCollect() const override`, one letter short of the base's `OnCollected`. No base function has that name, so the compiler reports an error on that line. Without `override`, the build would pass, `SpeedBoost` would own a new function that nothing calls, and a boost would log "pickup collected" through the base.
:::

::::question[Try it: what does the call print?]
`SpeedBoost` spells `OnCollected` correctly and prints "speed boost collected". A `const Pickup&` names a `SpeedBoost`. What does `OnCollected` print through it?

:::answer
"speed boost collected". The call is virtual, so the real class of the object decides, not the type of the reference.
:::
::::

## The Script class is the first example

The engine holds your script as a `Script` and calls its callbacks. Here is the head of the class in the software development kit (SDK) of scripts.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L78-L88"
virtual ~Script() = default;

Script(const Script&) = delete;
Script& operator=(const Script&) = delete;

virtual void OnCreate() {}
virtual void OnUpdate([[maybe_unused]] float deltaTime) {}
virtual void OnFixedUpdate([[maybe_unused]] float fixedDeltaTime) {}
virtual void OnLateUpdate([[maybe_unused]] float deltaTime) {}
virtual void OnDestroy() {}
virtual void OnReload() {}
```

1. **Line 78:** the destructor is virtual, a rule explained below.
2. **Lines 80–81:** copying a `Script` is deleted, so no one can slice one.
3. **Lines 83–88:** each callback is a virtual function with an empty body, so a script overrides only the ones it needs.

A script class such as `Coin` in `Samples/ThirdPerson/Scripts/Coin.cpp` overrides `OnCreate`, `OnReload`, `OnUpdate` and `OnTriggerEnter` with `override`. When a coin's trigger fires, the engine calls `OnTriggerEnter` through a `Script` pointer, and the virtual call reaches `Coin`. The call site never names `Coin`.

## How a virtual call works

The call must find the right function while the program runs, so each object needs a clue about its real class. The compiler adds that clue as a hidden pointer in every object whose class has a virtual function. The pointer leads to the **virtual table**: a table, made once per class, that lists the address of each virtual function of that class.

```mermaid caption="A pointer to a pickup follows the hidden pointer of its object to the table of its own class, and the table names the function to run." alt="A pickup pointer leads to a coin object that holds a hidden pointer to the table of the coin class; a speed boost object leads to its own table."
flowchart LR
	pointer["Pickup pointer"] --> coin["coin object: hidden pointer, Points, Bonus"]
	coin --> coinTable["table of Coin: the Coin version"]
	boost["boost object: hidden pointer, Seconds"] --> boostTable["table of SpeedBoost: the SpeedBoost version"]
```

For the call `pickup->OnCollected()` the program reads the hidden pointer, reads the slot for `OnCollected` in that table, and jumps to the address found. A `SpeedBoost` has its own table, with its own function in the same slot, so the same two reads reach different code. Compilers usually give a slot to each virtual function in the order of declaration, and a derived class keeps the base's slots in place. A slot number then means the same function for every class in the family.

The hidden pointer has a price in memory. The next sketch measures it.

```cpp sketch="basics-cpp-classes-size.cpp"
// The cost of the hidden pointer: the size of an object with and without a virtual function.
#include <iostream>

struct Plain
{
	int Value = 0;
};

struct WithVirtual
{
	int Value = 0;
	virtual ~WithVirtual() = default;
};

int main()
{
	std::cout << "Plain: " << sizeof(Plain) << " bytes\n";
	std::cout << "WithVirtual: " << sizeof(WithVirtual) << " bytes\n";
	return 0;
}
```

```text output-of="basics-cpp-classes-size.cpp"
Plain: 4 bytes
WithVirtual: 16 bytes
```

1. **Line 6:** `Plain` holds one `int`, 4 :term[bytes]{id=byte}.
2. **Line 12:** one virtual function, here the destructor, adds the hidden pointer.
3. **Lines 17–18:** the sizes on a 64-bit machine; the pointer takes 8 bytes and the `int` is padded to reach a multiple of 8.

A second virtual function adds no more bytes, because the table grows, not the object. The price in time is one more memory read per call, and the compiler cannot replace the call with the function's body, because it does not know which function will run. For a callback that runs once per frame per object the price is small. For a call inside a loop over a million points of a model it is not, and engine code keeps virtual calls for the boundaries between parts.

## An interface lets low code call high code

An engine is built in layers, and a lower layer must sometimes call code that a higher layer, or a game, provides later. The lower layer cannot name that code, because naming it would make the lower layer depend upward. The way out is a class that only says what can be called.

A **pure virtual function** is a virtual function declared with `= 0` and no body, so each derived class must write it.

A class with at least one pure virtual function is an **abstract class**: no object of it can exist, but pointers and references to it can.

An **interface** is an abstract class that holds no data and states what its users may call. Both sides depend on the interface: the caller uses it, and the implementations derive from it.

```cpp sketch="basics-cpp-classes-interface.cpp"
#include <iostream>
struct Module
{
	virtual ~Module() = default;
	virtual void OnUpdate() const = 0;
};

struct Audio : Module
{
	void OnUpdate() const override { std::cout << "mixing sound\n"; }
};

struct Physics : Module
{
	void OnUpdate() const override { std::cout << "moving bodies\n"; }
};

void Run(const Module& module) { module.OnUpdate(); }

int main()
{
	Run(Audio());
	Run(Physics());
}
```

```text output-of="basics-cpp-classes-interface.cpp"
mixing sound
moving bodies
```

1. **Line 5:** `= 0` makes `Module` abstract; `Module module;` would not compile.
2. **Lines 10–15:** each implementation overrides the pure function.
3. **Line 18:** `Run` knows only `Module`, so a new module needs no change here.
4. **Lines 22–23:** the temporary objects convert to `Module` references.

Strata uses this shape in many places. `Window` in `Strata/src/Strata/Core/Window.h` declares pure virtual functions such as `ProcessEvents` and `SetVSync`. `Application` holds a `Scope<Window>` and never includes the GLFW library, whose `GLFWWindow` implements the interface in `Strata/src/Platform/GLFW/`. Tests give the application a stand-in window through `WindowFactory`.

`EngineModule` in `Strata/src/Strata/Core/EngineModule.h` has two pure functions, `GetName` and `OnInit`, and many hooks with default bodies, such as `OnUpdate`, so a module overrides what it needs. [Engine modules](../core/engine-modules.md) explains the hooks. The editor's undo steps follow the same pattern.

```cpp src="StrataEditor/src/Editor/UndoStack.h#L34-L38"
virtual ~EditorAction() = default;

virtual const std::string& GetName() const = 0;
virtual bool Execute(std::string* outError) = 0;
virtual bool Undo(std::string* outError) = 0;
```

The `UndoStack` owns each step as a `Scope<EditorAction>` and calls `Execute` and `Undo` without knowing what the step changes. A step can be an asset edit, a prefab apply or a group of steps. [Layers, registries and the composition root](../core/layers-registries.md) shows how the engine uses the pattern to keep its layers apart.

The choice has a cost. Every call through an interface is a virtual call, the objects usually live on the heap behind a pointer, and a reader must open two files to see which code runs. Strata pays that price where the dependency direction matters.

## Deleting through a base needs a virtual destructor

Engine code owns a `Module` pointer and not an `Audio` object, so it deletes through the base pointer. The next sketch does the same with a `Coin`, and its base has a virtual destructor.

```cpp sketch="basics-cpp-classes-destructor.cpp"
// Deleting a Coin through a Pickup pointer: the virtual destructor runs both destructors.
#include <iostream>

struct Pickup
{
	virtual ~Pickup() { std::cout << "Pickup destroyed\n"; }
};

struct Coin : Pickup
{
	~Coin() override { std::cout << "Coin destroyed\n"; }
};

int main()
{
	Pickup* pickup = new Coin();
	delete pickup;
}
```

```text output-of="basics-cpp-classes-destructor.cpp"
Coin destroyed
Pickup destroyed
```

1. **Line 6:** `virtual` here makes the destructor of every derived class virtual too.
2. **Line 11:** `override` is allowed on a destructor; the compiler checks the base's one is virtual.
3. **Lines 16–17:** the delete goes through a `Pickup` pointer, yet both destructors run, `Coin` first.

Without `virtual` on line 6, the delete would call only the destructor of `Pickup`. The C++ rules call that :term[undefined behavior]{id=undefined-behavior}: the program may skip the `Coin` destructor, leak what `Coin` owns, or do worse. The rule is short: a class with a virtual function, which is meant as a base, gets a virtual destructor. `Script`, `EngineModule` and `EditorAction` all follow it, and so does every owner that deletes through a base, such as `Scope`.

## One call, many forms: polymorphism and slicing

The interface and the `Script` callbacks share one idea. **Polymorphism** is the use of one base type, with calls that run different code depending on the real object. The base pointer or reference is what makes it work, and a value is what breaks it.

**Slicing** is what happens when a derived object is copied into a base value: the copy keeps only the base part, and the derived part and its virtual behavior are lost. The copy is a true `Pickup`, so its table is the table of `Pickup`.

```cpp sketch="basics-cpp-classes-slicing.cpp"
// Slicing: copying a Coin into a Pickup value keeps only the Pickup part.
#include <iostream>

struct Pickup
{
	int Points = 1;
	virtual ~Pickup() = default;
	virtual void OnCollected() const { std::cout << "pickup: " << Points << "\n"; }
};

struct Coin : Pickup
{
	int Bonus = 5;
	void OnCollected() const override { std::cout << "coin: " << Points + Bonus << "\n"; }
};

int main()
{
	Coin coin;
	const Pickup& reference = coin;
	const Pickup copy = coin;
	reference.OnCollected();
	copy.OnCollected();
}
```

```text output-of="basics-cpp-classes-slicing.cpp"
coin: 6
pickup: 1
```

1. **Line 20:** a reference keeps the object, so the call is virtual.
2. **Line 21:** a value copies only the `Pickup` part; `Bonus` is gone.
3. **Lines 22–23:** the reference prints `coin: 6` and the copy prints `pickup: 1`.

:::example[What a slice keeps]
`Coin` holds `Points` 1 and `Bonus` 5. Through the reference, `Points + Bonus` is 6. The copy has only `Points`, 1, and the function of `Pickup`. No error, no warning: the program runs and prints the wrong class's answer.
:::

::::question[Try it: how do you stop the slice?]
Which change on line 21 of the sketch makes both calls print `coin: 6`?

:::answer
Write `const Pickup& copy = coin;`. A reference makes no copy, so the object stays whole.
:::
::::

Three habits avoid slicing. Pass base types by reference or pointer, never by value. Keep a collection of owning pointers, not of values. Delete the copy, as `Script` does, so a slice does not compile.

## Operators for your own types

Add two `glm::vec3` values and you write `a + b`. For your own :term[struct]{id=struct} the compiler does not know what `+` means, and `Add(a, b)` reads worse in a formula. **Operator overloading** is the definition of what an operator such as `+`, `==` or `[]` does for a class, by writing a function whose name is `operator` and the symbol.

glm does this for its vectors: `a + b` adds them component by component, `a == b` compares them, and `v[0]` reads the first component. The sketch makes a tiny vector with the same two operators that matter most.

```cpp sketch="basics-cpp-classes-vec2.cpp"
// Operators for one's own type, as glm has them: + adds, and the compiler writes ==.
#include <iostream>

struct Vec2
{
	float X = 0.0f;
	float Y = 0.0f;

	Vec2 operator+(const Vec2& other) const { return Vec2 { X + other.X, Y + other.Y }; }
	bool operator==(const Vec2& other) const = default;
};

int main()
{
	const Vec2 sum = Vec2 { 1.0f, 2.0f } + Vec2 { 3.0f, 4.0f };
	std::cout << sum.X << " " << sum.Y << "\n";
	std::cout << std::boolalpha << (sum == Vec2 { 4.0f, 6.0f }) << " " << (sum == Vec2 {}) << "\n";
}
```

```text output-of="basics-cpp-classes-vec2.cpp"
4 6
true false
```

1. **Line 9:** `a + b` calls this function on `a`, with `b` as `other`, and the result is a new `Vec2`.
2. **Line 10:** `= default` asks the compiler to write `==`, comparing the members in order.
3. **Line 15:** the operator reads as the function `operator+` called on the left value.

An operator on a class is an ordinary function with a special name, so it can overload `[]`, `-`, `*` and `<` in the same way. Keep to the usual meaning: a `+` that subtracts is a trap for the next reader. Write an operator only where the type is a number, a vector or a value in the same sense; a coin collecting itself is a function, not an operator.

A comparison of floats with `==` is exact, so `0.1 + 0.2 == 0.3` is false in `double`. The defaulted `==` inherits this, and a game compares positions with a small tolerance instead.

## Reading a test framework's macros

Strata's tests use doctest, whose `TEST_CASE` macro writes a function around the test. The related macro `TEST_CASE_FIXTURE(Fixture, "name")` writes a struct that derives from `Fixture` and puts the test inside it, so the test body reads the fixture's members as its own. When a test macro looks strange, expect a derived class behind it.

## Common mistakes

- **No `virtual` in the base.** The derived function hides the base one, and a call through a base reference runs the base version. Mark the base function `virtual` and the derived one `override`.
- **A signature that differs.** A missing `const` or a wrong parameter makes a new function. Write `override`, and the compiler reports it.
- **A base without a virtual destructor.** Deleting a derived object through a base pointer is undefined behavior. Give the base `virtual ~Name() = default;`.
- **A base type passed by value.** The derived part is sliced off, and virtual calls reach the base. Pass `const Pickup&` or a pointer.
- **A virtual call inside a constructor.** The derived part is not built yet, so the base version runs. Call virtual functions in a separate `OnCreate`-style function, as scripts do.
- **An object of an abstract class.** The build reports that it cannot make an object of an abstract class. Make an object of a derived class.

## Summary

- A derived class is built after its base and destroyed before it; members sit between the two, and `public`, `protected` and `private` set who sees a member.
- A virtual function is called through a hidden pointer to the table of the object's own class, which costs one more memory read and blocks inlining; `override` catches signature mistakes.
- A pure virtual function (`= 0`) makes a class abstract; an abstract class with no data is an interface, which lets lower code call code written above it.
- Delete through a base only with a virtual destructor, and never copy a derived object into a base value: slicing loses the derived part.
- Operators for your own types are functions named `operator` and the symbol; `= default` writes `==` for you.

## Check yourself

1. Class `C` derives from `B`, which derives from `A`, and each destructor writes its name. A `C` object goes out of scope. Which order is right: A: `~A ~B ~C`; B: `~C ~B ~A`; C: `~C ~A ~B`; D: `~B ~C ~A`?

   :::answer{tests="inheritance-order"}
   B. Destruction reverses construction, which went `A`, `B`, `C`. A is the construction order; C and D put a base before a class that derives from it.
   :::

2. A developer writes `void OnCollect() const override` in `SpeedBoost`, but the base declares `OnCollected`. What happens: A: the base version always runs; B: the compiler reports an error; C: the derived version runs; D: the program crashes when run?

   :::answer{tests="virtual-call"}
   B. `override` tells the compiler a base function with this name and signature must exist. Without the word, A would be the result, silently.
   :::

3. `Module` has the pure virtual function `OnUpdate`. Which line fails to compile: A: `Module* module = new Audio();`; B: `const Module& module = Audio();`; C: `Module module;`; D: `Audio audio;`, with `Audio` overriding `OnUpdate`?

   :::answer{tests="interfaces"}
   C. `Module` is abstract, so no object of it can exist. A and B make an `Audio` object and keep a base pointer or reference. D makes a complete derived object.
   :::

4. Which line slices a `Coin` named `coin`: A: `Pickup& p = coin;`; B: `Pickup* p = &coin;`; C: `Pickup p = coin;`; D: `Show(coin);` with `void Show(const Pickup& p)`?

   :::answer{tests="destructor-slicing"}
   C. It copies `coin` into a `Pickup` value and keeps only the `Pickup` part. A, B and D use a reference or a pointer, so the object stays whole.
   :::

5. A struct `Point` has two `int` members and the line `bool operator==(const Point& other) const = default;`. What does `a == b` compare?

   :::answer{tests="operators"}
   Both members, in the order declared: the result is true only when each pair is equal. The compiler writes the comparison, so adding a member later keeps it correct.
   :::

## Practice

Run every exercise in `Playground`, the script of [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own). For exercises 1 to 4, write the classes above your script class, make the objects in `OnCreate`, and write with `Log::Info` where the answers use `std::cout`.

If the **Console** still shows the lines of your earlier code, read the last line of the build: `(the module was up to date)` at its end means that it compiled nothing. A build compares the times of files, and a drive that keeps them in steps of two seconds can hide a change saved right after a build. Save the file again and press **Ctrl+B**.

1. **Basic.** Predict the order of six log lines for a `Gem` that derives from `Item` and has a member `Glow`, each with a constructor and destructor that log. Then run it.

   :::answer[Worked solution]{tests="inheritance-order" solution="sketches/basics-cpp-classes-members.cpp"}
   The base first, then the member, then the body of `Gem`; the destructors run in reverse. The program below does it in plain C++.

   ```cpp sketch="basics-cpp-classes-members.cpp"
   #include <iostream>
   struct Glow
   {
   	Glow() { std::cout << "Glow built\n"; }
   	~Glow() { std::cout << "Glow destroyed\n"; }
   };

   struct Item
   {
   	Item() { std::cout << "Item built\n"; }
   	~Item() { std::cout << "Item destroyed\n"; }
   };

   struct Gem : Item
   {
   	Glow Light;
   	Gem() { std::cout << "Gem built\n"; }
   	~Gem() { std::cout << "Gem destroyed\n"; }
   };

   int main()
   {
   	Gem gem;
   }
   ```

   ```text output-of="basics-cpp-classes-members.cpp"
   Item built
   Glow built
   Gem built
   Gem destroyed
   Glow destroyed
   Item destroyed
   ```

   1. **Line 16:** `Light` is built after `Item` and before the body of `Gem`.
   2. **Line 23:** one object runs all six lines.
   :::

2. **Medium.** Call `Area` through a `const Shape&` that names a `Square`. Predict the output, remove `virtual` from `Shape::Area`, and predict again.

   :::answer[Worked solution]{tests="virtual-call" solution="sketches/basics-cpp-classes-area.cpp"}
   With `virtual` the call prints `area 16`; without it, `area 0`, because the compiler picks `Shape::Area` from the reference's type.

   ```cpp sketch="basics-cpp-classes-area.cpp"
   // Practice 2: one call through a base reference reaches the derived Area because Area is virtual.
   #include <iostream>

   struct Shape
   {
   	virtual ~Shape() = default;
   	virtual float Area() const { return 0.0f; }
   };

   struct Square : Shape
   {
   	float Side = 4.0f;
   	float Area() const override { return Side * Side; }
   };

   void Print(const Shape& shape) { std::cout << "area " << shape.Area() << "\n"; }

   int main()
   {
   	Print(Square());
   }
   ```

   ```text output-of="basics-cpp-classes-area.cpp"
   area 16
   ```

   1. **Line 7:** the one word to remove for the second run.
   2. **Line 16:** `Print` sees only a `Shape`, so only the virtual call finds `Square`.
   :::

3. **Medium.** Predict what a function taking a `Pickup` by value prints for a `Coin`, and what a function taking `const Pickup&` prints.

   :::answer[Worked solution]{tests="destructor-slicing" solution="sketches/basics-cpp-classes-byvalue.cpp"}
   The value version prints `pickup`: the parameter is a sliced copy. The reference version prints `coin`.

   ```cpp sketch="basics-cpp-classes-byvalue.cpp"
   // Practice 3: passing a Coin by value slices it; passing it by reference does not.
   #include <iostream>

   struct Pickup
   {
   	virtual ~Pickup() = default;
   	virtual const char* Name() const { return "pickup"; }
   };

   struct Coin : Pickup
   {
   	const char* Name() const override { return "coin"; }
   };

   void ByValue(Pickup pickup) { std::cout << "value: " << pickup.Name() << "\n"; }
   void ByReference(const Pickup& pickup) { std::cout << "reference: " << pickup.Name() << "\n"; }

   int main()
   {
   	ByValue(Coin());
   	ByReference(Coin());
   }
   ```

   ```text output-of="basics-cpp-classes-byvalue.cpp"
   value: pickup
   reference: coin
   ```

   1. **Line 15:** the parameter is a new `Pickup`, built by copying the base part of the `Coin`.
   2. **Line 16:** the reference names the real `Coin`.
   :::

4. **Hard.** Write a struct `Money` with `int Cents`, an `operator+` and a defaulted `operator==`. Add 150 and 275 and compare the sum with 425 and with 150.

   :::answer[Worked solution]{tests="operators" solution="sketches/basics-cpp-classes-money.cpp"}
   The sum is 425 cents; the comparisons print `true` and `false`.

   ```cpp sketch="basics-cpp-classes-money.cpp"
   // Practice 4: operator+ and a defaulted == for a small Money struct.
   #include <iostream>

   struct Money
   {
   	int Cents = 0;

   	Money operator+(const Money& other) const { return Money { Cents + other.Cents }; }
   	bool operator==(const Money& other) const = default;
   };

   int main()
   {
   	const Money sum = Money { 150 } + Money { 275 };
   	std::cout << sum.Cents << " cents\n";
   	std::cout << std::boolalpha << (sum == Money { 425 }) << " " << (sum == Money { 150 }) << "\n";
   }
   ```

   ```text output-of="basics-cpp-classes-money.cpp"
   425 cents
   true false
   ```

   1. **Line 8:** the member function adds the cents of both values.
   2. **Line 9:** the compiler compares `Cents`.
   :::

5. **Hard.** Optional: remove the classes of exercises 1 to 4 from `Playground.cpp`. Above `Playground`, make a base class `Pickup` that derives from `Script` and has a virtual `OnCollected`, and two scripts derived from it, `Star` and `SpeedBoost`, each logging its own line. Only `Star` and `SpeedBoost` get `ST_SCRIPT_CLASS`. In `OnCreate`, make an entity for each with `Scene::CreateEntity("Star").AddScript<Star>()` and the same for `SpeedBoost`, log whether `GetScript<Pickup>()` finds anything on them, and call `OnCollected` on each through a `Pickup*`.

   :::answer[Worked solution]{tests="interfaces virtual-call" solution="sketches/basics-cpp-classes-pickups.cpp"}
   `Pickup` derives from `Script` and is never registered, because the engine finds a script by the name of its own class: `GetScript<Pickup>()` returns `nullptr` for a `Star`. Ask for the exact class, then convert the pointer to the base. The plain C++ program below shows the pointer conversion and the virtual call.

   ```cpp sketch="basics-cpp-classes-pickups.cpp"
   #include <iostream>
   struct Pickup
   {
   	virtual ~Pickup() = default;
   	virtual void OnCollected() const = 0;
   };

   struct Star : Pickup
   {
   	void OnCollected() const override { std::cout << "star collected\n"; }
   };

   struct SpeedBoost : Pickup
   {
   	void OnCollected() const override { std::cout << "speed boost collected\n"; }
   };

   int main()
   {
   	const Star star;
   	const SpeedBoost boost;
   	const Pickup* pickups[2] = { &star, &boost };
   	for (const Pickup* pickup : pickups)
   		pickup->OnCollected();
   }
   ```

   ```text output-of="basics-cpp-classes-pickups.cpp"
   star collected
   speed boost collected
   ```

   1. **Line 5:** the pure function makes `Pickup` an interface.
   2. **Line 22:** `Star*` and `SpeedBoost*` addresses convert to `Pickup*`.
   3. **Lines 23–24:** the virtual call picks the class.

   In the script, `OnCreate` makes the two entities and asks each for every real class in turn.

   ```cpp pseudocode
   void OnCreate() override
   {
   	Entity star = Scene::CreateEntity("Star");
   	star.AddScript<Star>();
   	Entity boost = Scene::CreateEntity("Boost");
   	boost.AddScript<SpeedBoost>();

   	for (Entity entity : { star, boost })
   	{
   		Log::Info(entity.GetName(), ": GetScript<Pickup> is null: ", entity.GetScript<Pickup>() == nullptr);
   		Pickup* pickup = entity.GetScript<Star>();
   		if (!pickup)
   			pickup = entity.GetScript<SpeedBoost>();
   		if (pickup)
   			pickup->OnCollected();
   	}
   }
   ```

   1. **Line 10:** `GetScript<Pickup>()` finds nothing, since no class named `Pickup` is registered.
   2. **Lines 11–13:** the script asks for `Star` first and falls back to `SpeedBoost`; either address converts to `Pickup*`.
   3. **Line 15:** the call goes through the base only when a script was found, and runs the version of the real class.

   The **Console** shows `Star: GetScript<Pickup> is null: true`, `star collected`, `Boost: GetScript<Pickup> is null: true` and `speed boost collected`.
   :::

## Where the book uses it

- [Generic C++](../basics/cpp-generic.md) uses virtual calls and abstract classes as the contrast to templates and type erasure.
- [Engine modules](../core/engine-modules.md) uses the interface `EngineModule`, whose hooks a module overrides.
- [Windows, events and layers](../core/windows-events.md) uses the `Window` interface and the `Event` base class with its derived events.
- [Layers, registries and the composition root](../core/layers-registries.md) uses interfaces to let a lower layer call a higher one.

## Further reading

- Learn C++ (learncpp.com), chapters 24 and 25 on inheritance and virtual functions: lessons with many small programs; beginner.
- [cppreference: virtual functions](https://en.cppreference.com/w/cpp/language/virtual): the exact rules of `virtual`, `override` and `final`; intermediate.
- [cppreference: abstract classes](https://en.cppreference.com/w/cpp/language/abstract_class): pure virtual functions and what they forbid; intermediate.
- [cppreference: operator overloading](https://en.cppreference.com/w/cpp/language/operators): every overloadable operator and the defaulted comparison; intermediate.
