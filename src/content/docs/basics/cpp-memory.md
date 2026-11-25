---
id: basics/cpp-memory
title: "C++ memory: pointers, references, lifetimes, RAII and smart pointers"
description: "How a C++ program borrows, owns and gives back memory: pointers, references, lifetimes, destructors, smart pointers and allocators."
kind: primer
size: L
tracks: [B, E]
needs: [basics/programming-3, basics/computer]
time: 130
learn:
  - id: pointers
    text: explain what a pointer and a reference hold, and choose between them
  - id: lifetimes
    text: predict when and in what order the destructors of locals, statics and heap objects run
  - id: memory-bugs
    text: find a leak, a dangling pointer, a double delete or a use after free in a short program
  - id: ownership
    text: choose a unique pointer, a shared pointer, a weak pointer or a raw pointer for who owns an object
  - id: allocators
    text: explain why an engine avoids heap allocation in a frame, and write an arena that rounds up to alignment
status: final
---

::::test-out

1. The code below gives one number two names. What does it log?

   ```cpp pseudocode
   int apples = 4;
   int* basket = &apples;
   *basket = 9;
   Log::Info(apples);
   ```

   Read `&apples` as "the address of apples" and `*basket` as "the object at that address".

   :::answer{tests="pointers"}
   The log shows 9. `basket` holds the address of `apples`, and `*basket = 9;` stores 9 at that address, which is where `apples` lives.
   :::

2. A scope makes the object `x`, then the object `y`. Both destructors log their name. In which order do the names appear when the closing brace is reached?

   :::answer{tests="lifetimes"}
   `y`, then `x`. Destructors run in the reverse order of construction, so the object made last goes first.
   :::

3. Name the bug in the code below, and say one way to avoid it.

   ```cpp pseudocode
   int* p = new int(5);
   delete p;
   Log::Info(*p);
   ```

   Look at which line ends the object and which line reads it later.

   :::answer{tests="memory-bugs"}
   A use after free: the last line reads memory that `delete` already gave back. Avoid it by not touching `p` after `delete`, or by holding the number in a unique pointer that deletes it at the end of its scope.
   :::

4. Three systems use one texture and finish at unpredictable times, so nobody knows who is last. Which smart pointer fits: unique, shared or weak?

   :::answer{tests="ownership"}
   A shared pointer. It counts the owners and deletes the texture when the last one lets go. A unique pointer allows one owner only, and a weak pointer owns nothing.
   :::

5. An arena has 64 bytes and 5 of them are used. A caller asks for 8 bytes that must start at a multiple of 8. At which offset do they start?

   :::answer{tests="allocators"}
   At offset 8. Round 5 up to the next multiple of 8: (5 + 7) / 8 × 8 = 8. The 3 bytes between 5 and 8 stay unused.
   :::

::::

## Why you will need this

A script keeps a `Coin*` from `GetScript<Coin>()` and, a frame later, the coin is gone. The engine passes `Ref<Scene>` and `Scope<AssetImporter>` through its headers, and each says who keeps an object alive. Memory in C++ is yours to manage, and the language does not warn you when you manage it wrongly.

Three later pages build on this one. [C++ classes in depth](cpp-classes.md) uses destructors and ownership to explain virtual calls and interfaces. [Conventions](../core/conventions.md) states Strata's rules for `Scope`, `Ref` and borrowed pointers. [Residency](../assets/residency.md) explains why a frame holds an asset by handle and not by `Ref`.

This page needs no download. Only the Practice needs a project: the one that holds your `Playground` script, which [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own) puts on an empty entity.

Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), four pages on. On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A pointer holds an address you can follow

A function that should add a coin to `coins` cannot do it with a copy of the number. A copy is a second number in another place, and the original stays as it was. The function needs the place of the original, not its value.

[Memory](computer.md) is a row of numbered bytes, and the number of a byte is its address. An `int` takes four bytes. Say `coins` sits at address 1008: it fills the bytes 1008 to 1011, and the next `int` starts at 1012.

```mermaid caption="Three whole numbers lie in a row of memory, four bytes apart. The pointer where is a variable of its own whose value, 1008, is the address of the middle one." alt="A row of three boxes labelled 1004: 7, 1008: 3 and 1012: 9, each the address then the value. A separate box labelled where equals 1008 has an arrow to the middle box."
flowchart LR
    subgraph row["Memory"]
        direction LR
        A["1004: 7"] --- B["1008: 3"] --- C["1012: 9"]
    end
    P["where = 1008"] --> B
```

A pointer is a variable whose value is such an address. Three symbols work with it. `&coins` reads "the address of `coins`" and gives 1008. A variable of type `int*` stores it: the `*` in a type reads "pointer to". In an expression `*where` reads "the object at that address", and following a pointer to that object is to **dereference** it.

The same two symbols mean different things in a type and in an expression. In `int* where = &coins;` the `*` belongs to the type, and the `&` takes an address. In `*where = 10;` the `*` is the dereference. For a pointer to a :term[struct]{id=struct}, `p->Value` is short for `(*p).Value`: follow the pointer, then take the member.

The program below uses all three symbols. Read the output against the comments: the pointer writes to `coins` without ever naming it.

```cpp sketch="basics-cpp-memory-pointers.cpp"
// A pointer holds an address: & takes one, * follows it, -> follows it to a member.
#include <iostream>

struct Coin
{
	int Value = 5;
};

int main()
{
	int coins = 3;
	int* where = &coins; // where holds the address of coins
	*where = 10;         // follow the address and store 10 there
	std::cout << "coins: " << coins << ", through the pointer: " << *where << '\n';
	Coin gold;
	Coin* p = &gold;
	p->Value = 8; // the same as (*p).Value = 8
	std::cout << "gold.Value: " << gold.Value << '\n';
	int row[3] = { 7, 8, 9 };
	int* second = row + 1; // one int along the row, not one byte
	std::cout << "second: " << *second << ", elements apart: " << second - row << '\n';
	int* none = nullptr;
	std::cout << "none is null: " << std::boolalpha << (none == nullptr) << '\n';
}
```

```text output-of="basics-cpp-memory-pointers.cpp"
coins: 10, through the pointer: 10
gold.Value: 8
second: 8, elements apart: 1
none is null: true
```

1. **Line 12:** `&coins` is the address; `where` is a second variable that holds it, not a second `coins`.
2. **Line 13:** the dereference writes through the address, so `coins` itself changes.
3. **Line 17:** `->` reaches the member `Value` of the `Coin` that `p` points to.
4. **Line 20:** adding 1 to a pointer moves it one element of its type, here four bytes, not one byte.
5. **Line 22:** `nullptr` is the pointer that points at nothing. Test a pointer against it before you follow it, because following it is a bug (see [undefined behavior](#undefined-behavior-is-a-rule-that-nothing-checks)).

A pointer is itself a number the size of an address: 8 bytes on a 64-bit computer. The type tells the compiler how many bytes to read at the address and how to read them.

:::example[Walking a row by hand]
`int row[3]` lies at address 2000, so `row[0]` is at 2000, `row[1]` at 2004 and `row[2]` at 2008. The pointer `row + 2` holds 2000 + 2 × 4 = 2008, and `*(row + 2)` reads the third number. The spellings `row[2]` and `*(row + 2)` name the same object.
:::

Try it: `float values[4]` lies at address 500, and a `float` takes four bytes. What address does `values + 3` hold?

:::answer
The address is 512. The pointer moves three elements of four bytes each: 500 + 3 × 4 = 512.
:::

## A reference is another name that cannot be empty

Passing a big value to a function copies it. A `Level` that holds 1,000 `float` heights is 4,000 bytes. A function called 1,000 times per frame, 60 frames per second, copies 4,000 × 1,000 × 60 = 240,000,000 bytes each second to read a number or two.

A reference avoids the copy. `Level& level` is a second name for the caller's object, so the function reads and writes the original. `const Level& level` is a reference that promises not to write, and it also accepts a temporary value, such as the result of another call. Pass large values to functions as `const` references, and small ones (`int`, `float`, a pointer) by value.

```cpp sketch="basics-cpp-memory-references.cpp"
// A reference is a second name for an object; a const reference passes a large value without a copy.
#include <iostream>

struct Level { float Heights[1000]; }; // 4,000 bytes

void Raise(int& value) { value += 1; }
float Peek(const Level& level) { return level.Heights[7]; } // reads the caller's level: no copy

int main()
{
	int coins = 3;
	int& alias = coins; // a second name for coins
	alias = 4;
	Raise(coins);
	Level level{};
	level.Heights[7] = 2.5f;
	std::cout << "coins: " << coins << ", alias: " << alias << '\n';
	std::cout << "peek: " << Peek(level) << ", level is " << sizeof(Level) << " bytes\n";
}
```

```text output-of="basics-cpp-memory-references.cpp"
coins: 5, alias: 5
peek: 2.5, level is 4000 bytes
```

1. **Line 6:** `Raise` takes `int&`, so the `+= 1` changes the caller's `coins`.
2. **Line 7:** `Peek` takes `const Level&`: the 4,000 bytes are not copied, and the compiler rejects a write to `level` inside it.
3. **Line 12:** `alias` is a second name for `coins`; the output shows that both names print 5.

A reference differs from a pointer in three ways. A reference must refer to an object when it is made, so it is never null. It cannot be pointed elsewhere later: `alias = 4;` stores 4 in `coins`, it does not make `alias` name another object. And you write it without `&` and `*`.

| Question | Pointer | Reference |
| --- | --- | --- |
| Can it be empty? | Yes: `nullptr` | No |
| Can it point elsewhere later? | Yes | No |
| Reaching the object | `*p`, `p->x` | `r`, `r.x` |
| Use it when | the object may be absent, or the target changes | the object must exist for the call |

Strata follows that split. `GameRenderer::Render` in `Strata/src/Strata/Runtime/GameRenderer.h` takes `const Ref<Scene>& scene` and a pointer to the image it draws into: the scene is required and borrowed for the call, and the image is a handle from a graphics library.

## Every object has a lifetime

A function builds a `Coin` and wants to return it. Returning a pointer to a :term[local variable]{id=local-variable} does not work, because the local is gone when the function ends. The question behind it is how long an object lives, and C++ has three answers.

The **lifetime** of an object is the stretch of a run between its construction and its destruction. Three kinds exist, and the table names the place, the start and the end of each.

| Kind | Examples | Lives in | Starts | Ends |
| --- | --- | --- | --- | --- |
| Automatic | locals, parameters | the stack | the line that declares it | the closing brace |
| Static | globals, `static` locals | fixed memory | before `main`; a `static` local when its line first runs | the end of the program |
| Dynamic | `new` | the heap | `new` | `delete` |

An automatic object needs no care: the stack takes it back by itself at the brace. A static object lasts to the end of the run, so a global keeps its value between calls, and a `static` local is a global that only one function can see. **Dynamic allocation**, also called heap allocation, is the third kind: you ask the heap for memory with `new`, and it stays yours until you give it back with `delete`. Use it when an object must last longer than the function that made it, or is too large for the stack, which often holds only 1 to 8 MB.

```cpp sketch="basics-cpp-memory-lifetimes.cpp"
// Three lifetimes: automatic (the braces), static (the whole run) and dynamic (new until delete).
#include <iostream>

int s_Total = 0; // a global: built before main starts, kept to the end

int CountCalls()
{
	static int calls = 0; // built the first time this line runs, kept to the end
	calls++;
	return calls;
}

int main()
{
	CountCalls(); CountCalls();
	std::cout << "calls: " << CountCalls() << '\n';
	{
		int inner = 7; // automatic: gone at the closing brace
		s_Total += inner;
	}
	int* onHeap = new int(40); // dynamic: lives until delete
	s_Total += *onHeap;
	delete onHeap;
	std::cout << "total: " << s_Total << '\n';
}
```

```text output-of="basics-cpp-memory-lifetimes.cpp"
calls: 3
total: 47
```

1. **Line 4:** the global exists before `main` starts and lasts to the end.
2. **Line 8:** the `static` local is built once, on the first call, and keeps its value, so the third call returns 3.
3. **Line 18:** `inner` is automatic: it is gone at the brace on line 20.
4. **Lines 21–23:** `new` returns a pointer to heap memory, and exactly one `delete` returns it. The memory stays alive across the braces in between.

## What goes wrong with dynamic memory

The heap gives you freedom and takes away the stack's tidiness. Two mistakes start from the same fact: after `new`, nothing ends the object but you.

A **memory leak** is memory that was allocated and never freed, so the program cannot use it again and nothing owns it. Here is the damage by hand. A function that leaks 64 bytes is called 60 times each second. In one hour it loses 64 × 60 × 3,600 = 13,824,000 bytes, about 14 MB, and a game runs for hours.

```cpp pseudocode
void Spawn()
{
	Enemy* enemy = new Enemy(); // the only pointer to the new object is a local
	// no delete: when Spawn ends, `enemy` is gone and the object is lost
}
```

The pointer was the only way to find the object. When the function returns, the pointer dies and the memory stays allocated.

A **dangling pointer** is a pointer to an object whose lifetime has ended. The address is still a number, but the memory behind it is no longer yours. Two common sources: a pointer to a local that went out of scope, and a pointer that kept its value after `delete`.

```cpp pseudocode
int* Broken()
{
	int local = 5;
	return &local; // `local` is destroyed at the closing brace: the caller gets a dangling pointer
}
```

Reading or writing through a dangling pointer is a use after free, even for a local. Deleting twice is its mirror: `delete p; delete p;` hands the same block back to the heap two times, and the heap's records break. Two pointers to one object make this likely: each owner deletes it, and the second `delete` is the bug.

:::example[Who deletes it?]
A level script makes an `Enemy` with `new` and stores the pointer in a list. The spawner also keeps the pointer in a local variable `last`. When the enemy dies, the list deletes it, and later the spawner deletes `last`. The object is deleted twice. The fault is not in a line of code but in a missing answer: nobody decided which of the two owns the enemy.
:::

Try it: the list deletes the enemy and the spawner then reads `last->Health`. Which bug is that?

:::answer
A use after free. `last` is a dangling pointer: it still holds the address, but the enemy's lifetime ended when the list deleted it.
:::

## Undefined behavior is a rule that nothing checks

Take an array of three numbers and write to `row[3]`. The array has `row[0]`, `row[1]` and `row[2]`, so index 3 is past its end. C++ does not check the index. The write lands on whatever sits behind the array: perhaps unused space, perhaps your `coins`.

**Undefined behavior** (UB) is what C++ calls a program that breaks a rule of the language that nothing checks. The language promises no result: the program may seem to work, crash, give a wrong answer, or work today and fail after the next compiler update. The compiler may also assume the rule is never broken and rewrite the code on that basis, so the damage can appear far from the broken line.

Three cases to know. Reading or writing past an array's end is UB, and so is following a null or a dangling pointer. Overflow of a signed integer is UB too: a 32-bit `int` holds at most 2,147,483,647, and adding 1 to it is not defined to wrap to a negative number. A compiler may even assume `x + 1 > x` is always true for an `int`, and delete the check. Overflow of an unsigned integer is different: it wraps by definition.

```cpp pseudocode
int row[3] = { 7, 8, 9 };
int hidden = row[3];      // reads past the end: undefined behavior
int big = 2147483647;
big = big + 1;            // signed overflow: undefined behavior
```

Neither line has a defined result: one reads memory beyond the array, and the other computes a value the language does not define.

:::why[Why C++ leaves behavior undefined]
A check on every index and every addition costs time on every run, and a game pays that cost in every frame. C++ leaves the check to you and promises speed in return. The price is bugs that no error message reports. Strata reports programmer mistakes with `ST_CORE_ASSERT`, which its shipping builds compile out, and you find the rest with the tools of [Debugging](debugging.md).
:::

Hold on to one rule: a program with UB has no meaning, even in the lines that look fine.

## Destructors give back what a lifetime took

Returning memory with `delete` at the end of every path is fragile. A function with three early returns needs the `delete` before each, and the fourth path added next month will forget it. The language has a better tool: code that runs by itself at the end of a lifetime.

A **destructor** is a :term[member function]{id=member-function} named `~` plus the class name, which C++ calls automatically when an object's lifetime ends. For an automatic object that is the closing brace. For a `delete`d object it is the `delete`. The destructor of a class never takes arguments, and the class's own members are destroyed after its body has run.

The order follows one rule: the objects of a scope are destroyed in the reverse order of their construction. A later object may use an earlier one, so the later one must go first. The program makes four objects of a class that logs when it is made and when it drops.

```cpp sketch="basics-cpp-memory-order.cpp"
// A destructor runs at the closing brace, and the objects of a scope go in the reverse order of their making.
#include <iostream>

struct Noisy
{
	const char* Name;
	explicit Noisy(const char* name)
		: Name(name)
	{
		std::cout << "make " << Name << '\n';
	}
	~Noisy() { std::cout << "drop " << Name << '\n'; }
};

int main()
{
	Noisy a("a");
	{
		Noisy b("b");
		Noisy c("c");
	}
	Noisy d("d");
}
```

```text output-of="basics-cpp-memory-order.cpp"
make a
make b
make c
drop c
drop b
make d
drop d
drop a
```

1. **Line 12:** the destructor logs, so the output shows when each object ends.
2. **Lines 19–20:** `b` and `c` live in an inner scope, so at the brace on line 21 `c` drops first and then `b`.
3. **Line 23:** the closing brace of `main` ends `d` first, since it was made later, and then `a`.

:::example[Predict the order]
A scope makes `P`, then `Q`, then an inner scope makes `R` and ends, then `S` is made, then the outer scope ends. The makes go P, Q, R, S. At the inner brace R drops. At the outer brace the survivors drop in reverse: S, Q, P. The full log is make P, make Q, make R, drop R, make S, drop S, drop Q, drop P.
:::

Try it: a scope makes `A`, `B` and `C` in this order and ends. Write the three drops.

:::answer
Drop C, drop B, drop A: the reverse of the makes.
:::

The tie between a resource and an object is **resource acquisition is initialization** (RAII): the :term[constructor]{id=constructor} acquires it (opens a file, takes a lock, allocates memory) and the destructor releases it. The object cannot be forgotten, because C++ calls the destructor on every way out of the scope. Strata's code does not throw exceptions, but early `return` lines are exit enough.

```cpp sketch="basics-cpp-memory-guard.cpp"
// RAII: the constructor opens, the destructor closes, and every way out of the function runs the destructor.
#include <iostream>

struct Guard
{
	Guard() { std::cout << "open\n"; }
	~Guard() { std::cout << "close\n"; }
};

bool Load(bool fail)
{
	Guard file;
	if (fail)
		return false; // an early exit still runs the destructor
	std::cout << "loaded\n";
	return true;
}

int main()
{
	std::cout << "call 1\n";
	Load(false);
	std::cout << "call 2\n";
	Load(true);
}
```

```text output-of="basics-cpp-memory-guard.cpp"
call 1
open
loaded
close
call 2
open
close
```

1. **Lines 6–7:** the constructor stands for opening a file and the destructor for closing it.
2. **Line 14:** the early return leaves the function, and the output shows `close` there too.

## One owner: unique pointers

A pointer from `new` has a second problem beyond leaks: nothing in its type says who deletes it. Pass it to three functions and each may assume a different answer. **Ownership** is the duty to end an object's lifetime. A program stays correct when each heap object has a clear owner, and that owner deletes it once.

A **smart pointer** is an object that holds a pointer and deletes what it points to in its own destructor. It is RAII applied to heap memory: the pointer cannot leak, because its owner's end is its delete. The standard library has three, in `<memory>`.

The first is the **unique pointer**, `std::unique_ptr<T>`, the only owner of its object. You make one with `std::make_unique<T>(arguments)`, which builds the object on the heap and wraps it. It works like a raw pointer for reading (`*p`, `p->x`), takes no more space than one, and deletes the object when it goes out of scope.

A unique pointer cannot be copied, because two copies would be two owners and two deletes. A copy line fails to compile. Ownership moves instead: one pointer hands the object to another and becomes empty.

:::question[What is `std::move`?]
`std::move` is the call that hands an object's contents to another variable. [Modern C++](cpp-modern.md) teaches how; here, read it as "give it away".
:::

The program makes an enemy in a factory function, a function that builds and returns an object. It returns the unique pointer by value, which moves it out. Then the owner changes in `main`.

```cpp sketch="basics-cpp-memory-unique.cpp"
// One owner: make_unique builds the object, the unique pointer deletes it, and ownership moves but never copies.
#include <iostream>
#include <memory>
#include <utility>

struct Enemy
{
	int Health = 0;
	~Enemy() { std::cout << "enemy deleted\n"; }
};

std::unique_ptr<Enemy> MakeEnemy(int health)
{
	std::unique_ptr<Enemy> enemy = std::make_unique<Enemy>();
	enemy->Health = health;
	return enemy; // ownership leaves with the returned value
}

int main()
{
	std::unique_ptr<Enemy> first = MakeEnemy(30);
	std::unique_ptr<Enemy> second = std::move(first); // hand the object over
	std::cout << "first empty: " << std::boolalpha << (first == nullptr) << ", health " << second->Health << '\n';
}
```

```text output-of="basics-cpp-memory-unique.cpp"
first empty: true, health 30
enemy deleted
```

1. **Line 14:** `make_unique` builds the `Enemy` on the heap and returns the owning pointer.
2. **Line 16:** returning a local unique pointer moves it out of the function: the factory hands its caller the ownership.
3. **Line 22:** `std::move` gives the object to `second`, and `first` becomes empty, as the output shows.
4. **Line 24:** the brace destroys `second`, whose destructor deletes the enemy: `enemy deleted` comes last.

A class with a unique pointer as a member inherits the restriction: its objects cannot be copied, only moved. That is a feature. The type says that one such object owns the resource, and the compiler enforces it.

## Shared ownership: shared pointers

Sometimes no single owner exists. Three materials use one texture, and they end in any order. The last one to finish should free it, and nobody knows in advance which that is.

A **shared pointer**, `std::shared_ptr<T>`, is a smart pointer that several owners hold at once. It keeps a count of its owners, the reference count. A copy raises the count, a destroyed or reset owner lowers it, and the object is deleted when the count reaches 0. `use_count()` reads the count. You make one with `std::make_shared<T>(arguments)`.

```cpp sketch="basics-cpp-memory-shared.cpp"
// A shared pointer counts its owners, and the object is deleted when the count reaches 0.
#include <iostream>
#include <memory>

struct Texture
{
	~Texture() { std::cout << "texture deleted\n"; }
};

int main()
{
	std::shared_ptr<Texture> a = std::make_shared<Texture>();
	std::cout << "count " << a.use_count() << '\n';
	{
		std::shared_ptr<Texture> b = a; // a copy: a second owner
		std::cout << "count " << a.use_count() << '\n';
	}
	std::cout << "count " << a.use_count() << '\n';
	a.reset(); // the last owner lets go
	std::cout << "sizes " << sizeof(std::unique_ptr<Texture>) << " and " << sizeof(std::shared_ptr<Texture>) << '\n';
}
```

```text output-of="basics-cpp-memory-shared.cpp"
count 1
count 2
count 1
texture deleted
sizes 8 and 16
```

1. **Line 12:** one owner, count 1.
2. **Line 15:** the copy `b` is a second owner; the count is 2 until the brace on line 17 destroys `b`.
3. **Line 19:** `reset()` lets `a` go. It is the last owner, so the texture is deleted before the next line.
4. **Line 20:** the sizes on a 64-bit computer: a unique pointer is one address, a shared pointer two.

The cost is the second address. A shared pointer holds the object's address and the address of a control block, a small record beside the object with the counts. `make_shared` allocates the object and the block together, in one request. Each copy and each destroyed owner changes a count with atomic operations, which are safe when several threads share the pointer ([Threads](threads.md) teaches them), and slower than a plain copy of an address.

Shared state is the use: two parts of a program that hold the same shared pointer see the same object, and a change by one is visible to the other. The danger is the reverse of its comfort. An object that many hold lives until the last holder lets go, and a forgotten holder keeps it alive for the whole run. When you only look at the object during a call, pass `const Ref<T>&` and the count stays unchanged.

## Weak pointers and cycles

Two nodes of a scene each hold the other: a parent owns its child, and the child wants a way back to the parent. If both links are shared pointers, each node's count includes the other. When the last outside owner leaves, each still counts 1, and neither reaches 0.

A **weak pointer**, `std::weak_ptr<T>`, watches an object without owning it. It does not change the count. `expired()` tells whether the object is gone, and `lock()` gives a shared pointer if the object lives, or an empty one if it does not. Hold a `lock()` result only for the lines that use it.

```cpp sketch="basics-cpp-memory-weak.cpp"
// A weak pointer watches an object it does not own; lock() gives a shared pointer while the object lives.
#include <iostream>
#include <memory>

int main()
{
	std::shared_ptr<int> owner = std::make_shared<int>(42);
	std::weak_ptr<int> watcher = owner;
	std::cout << "count " << owner.use_count() << '\n';
	if (std::shared_ptr<int> alive = watcher.lock())
		std::cout << "alive: " << *alive << ", count " << owner.use_count() << '\n';
	owner.reset();
	std::cout << "expired: " << std::boolalpha << watcher.expired() << '\n';
	std::cout << "lock gives null: " << (watcher.lock() == nullptr) << '\n';
}
```

```text output-of="basics-cpp-memory-weak.cpp"
count 1
alive: 42, count 2
expired: true
lock gives null: true
```

1. **Line 8:** a weak pointer from a shared one; the count on line 9 stays 1.
2. **Line 10:** `lock()` returns a shared pointer, so the count is 2 for the length of the `if` body.
3. **Line 12:** after the owner lets go, `expired()` is true and `lock()` gives null.

The cycle sketch builds two pairs of nodes. In the first, the second node links back with a weak pointer. In the second, both links are shared.

```cpp sketch="basics-cpp-memory-cycle.cpp"
// Two nodes that own each other never reach a count of 0; a weak link in one direction lets both go.
#include <iostream>
#include <memory>

struct Node
{
	std::shared_ptr<Node> Strong;
	std::weak_ptr<Node> Weak;
	~Node() { std::cout << "node deleted\n"; }
};
void Pair(bool cycle)
{
	std::shared_ptr<Node> a = std::make_shared<Node>();
	std::shared_ptr<Node> b = std::make_shared<Node>();
	a->Strong = b;
	if (cycle) b->Strong = a; else b->Weak = a;
}
int main()
{
	std::cout << "weak back link\n";
	Pair(false);
	std::cout << "cycle\n";
	Pair(true);
	std::cout << "end\n";
}
```

```text output-of="basics-cpp-memory-cycle.cpp"
weak back link
node deleted
node deleted
cycle
end
```

1. **Line 16:** the back link is weak or strong, as the argument says.
2. **Line 23:** the cycle never prints `node deleted`: both nodes leak, and no error says so.

The rule that follows: the owner holds the child by a shared or unique pointer, the child holds the owner by a weak pointer or a raw pointer.

## Strata's names for the three: `Scope`, `Ref` and `WeakRef`

Strata uses the three smart pointers throughout its headers and gives them shorter names in one header. `Strata/src/Strata/Core/Base.h` holds the names and a helper function for each of the first two.

:::question[What are the angle brackets and the dots?]
`template<typename T>` and `Args&&... args` make one definition work for any type: [Generic C++](cpp-generic.md) teaches them. `constexpr` and `std::forward` come with [Modern C++](cpp-modern.md); here, read each as a function that passes its arguments on.
:::

The quote shows the three short names and the two helper functions. Read the right side of each `using` and the `return` lines.

```cpp src="Strata/src/Strata/Core/Base.h#L42-L61"
template<typename T>
using Scope = std::unique_ptr<T>;

template<typename T, typename... Args>
constexpr Scope<T> CreateScope(Args&&... args)
{
	return std::make_unique<T>(std::forward<Args>(args)...);
}

template<typename T>
using Ref = std::shared_ptr<T>;

template<typename T, typename... Args>
constexpr Ref<T> CreateRef(Args&&... args)
{
	return std::make_shared<T>(std::forward<Args>(args)...);
}

template<typename T>
using WeakRef = std::weak_ptr<T>;
```

1. **Line 43:** `Scope<T>` is `std::unique_ptr<T>` under another name.
2. **Lines 46–48:** `CreateScope` passes its arguments to `std::make_unique` and returns the owner.
3. **Line 52:** `Ref<T>` is `std::shared_ptr<T>`; `CreateRef` on line 55 calls `std::make_shared`.
4. **Line 61:** `WeakRef<T>` is `std::weak_ptr<T>`.

You use them as the standard types: `Scope<Enemy> enemy = CreateScope<Enemy>();` and `Ref<Texture> texture = CreateRef<Texture>();`. They are the same types, so every fact of this page holds for them.

:::why[Why short names?]
A short name costs nothing at run time: `Scope<T>` is exactly `std::unique_ptr<T>`. The gain is in the reading. Every ownership decision in the engine's headers appears in two short names, which one search finds, and the engine's guide gives each a job: `Scope` for one owner, `Ref` for shared ownership. [Conventions](../core/conventions.md) states the rules.
:::

The engine's own headers show the roles. `Strata/src/Strata/Asset/AssetImporter.h` declares `static void Register(Scope<AssetImporter> importer);`, a function that takes over the importer it receives. `Strata/src/Strata/Asset/AssetManager.h` stores its extensions in `std::vector<Scope<AssetManagerExtension>> m_Extensions;`, the list that owns them. `GameRuntime::GetScene` in `Strata/src/Strata/Runtime/GameRuntime.h` returns `const Ref<Scene>&`: the runtime holds a shared scene and lends out a reference to the owner without raising the count.

## Raw pointers are borrowed

A raw pointer, the plain `T*` of the first section, has no destructor logic. In modern C++ it says one thing: I use this object, I do not own it. The rule that follows is short. Never `delete` a pointer that you did not receive from `new` yourself, or that something else owns. Check how long the owner lives before you keep a pointer past one call.

```mermaid caption="Who ends the object decides the kind of pointer: one owner, many owners, or no owner at all." alt="A diagram that starts with the question who ends the object. One owner leads to a unique pointer. Many owners lead to a shared pointer. A user that is not an owner takes a reference when the object is always present, and a raw pointer when it may be absent. It takes a weak pointer when it must notice the end."
flowchart TD
    Q["Who ends the object's life?"] --> U["One owner: unique pointer"]
    Q --> S["Many owners: shared pointer"]
    Q --> N["Not me, I only use it"]
    N --> R["Always present: reference"]
    N --> P["May be absent: raw pointer"]
    N --> W["Must notice when it dies: weak pointer"]
```

A script meets this every day. `Entity::GetScript<T>()` returns a `T*` to the script object that the engine owns. The pointer is borrowed: the script may use it now. The engine ends the object at the end of a frame in which the entity is destroyed, or when a hot reload (the editor rebuilds the scripts while the game runs) replaces the module. The last exercise of this page keeps such a pointer one frame too long.

## Heap allocation costs time, so engines allocate early

A `new` is not free. The heap must find a free block of the right size, mark it taken and keep its books. In a program with several threads, the heap may have to take a lock, so two threads that allocate wait for each other. Over many allocations the free memory splits into small pieces, and a request for a big block fails although the total is large.

A frame has about 16.7 ms at 60 frames per second. Say a heap request takes 100 nanoseconds (ns); the figure is an assumption of this example. Then 10,000 requests in one frame take 10,000 × 100 ns = 1 ms, about 6 % of the frame, spent on records and not on the game. Engines therefore allocate early, at load time, and use the memory again, or they allocate cheaply from a block they already have.

An **allocator** is code that hands out and takes back pieces of memory under a rule of its own. The three simple ones each trade a freedom for speed.

An arena gives memory out in a row and frees it all at once. A counter of the used bytes moves forward by each request, so a request costs one addition, and a reset sets the counter back to 0. You cannot free one piece alone.

The only care is alignment: an `int` must start at an address that is a multiple of 4, a `double` at a multiple of 8. The arena rounds the next offset up to the multiple before handing it out: `(used + align - 1) / align * align`. [Numbers](numbers.md) teaches the round-up rule, and [Bytes](bytes.md) the layouts and padding behind alignment.

```cpp sketch="basics-cpp-memory-arena.cpp"
// An arena hands out memory in a row: round the offset up to the alignment, give the bytes, move on.
#include <cstddef>
#include <iostream>

struct Arena
{
	alignas(8) unsigned char Bytes[64];
	std::size_t Used = 0;
	std::size_t Allocate(std::size_t size, std::size_t align)
	{
		std::size_t start = (Used + align - 1) / align * align;
		if (start + size > sizeof(Bytes)) return sizeof(Bytes);
		Used = start + size;
		return start;
	}
};

int main()
{
	Arena arena;
	std::cout << arena.Allocate(1, 1) << ' ' << arena.Allocate(8, 8) << ' ' << arena.Allocate(4, 4) << '\n';
	std::cout << arena.Allocate(100, 1) << ' ';
	arena.Used = 0; // free everything at once
	std::cout << arena.Allocate(8, 8) << '\n';
}
```

```text output-of="basics-cpp-memory-arena.cpp"
0 8 16
64 0
```

1. **Line 7:** `alignas(8)` starts the buffer at a multiple of 8. An offset that is a multiple of 8 lands at an aligned address only then.
2. **Line 11:** the rounding: 1 byte used and align 8 give (1 + 7) / 8 × 8 = 8, the second output number.
3. **Line 12:** a request that does not fit returns 64, the buffer's size, as the failure value.
4. **Line 23:** setting `Used` back to 0 frees everything at once, and the next request starts at 0.

A pool hands out slots of one size. A free list threads through the unused slots: each free slot says which free slot comes next. Taking the first slot and giving one back are one step each, and the order of giving back does not matter, because every slot fits every request.

```cpp sketch="basics-cpp-memory-pool.cpp"
// A pool of four equal slots: a free list links the unused slots, so taking and giving back cost one step.
#include <iostream>

struct Pool
{
	int Next[4] = { 1, 2, 3, -1 }; // for a free slot: the free slot after it, or -1
	int Head = 0;                  // the first free slot, or -1 when none is free
	int Take() { int slot = Head; if (slot >= 0) Head = Next[slot]; return slot; }
	void Give(int slot) { Next[slot] = Head; Head = slot; }
};

int main()
{
	Pool pool;
	int a = pool.Take(), b = pool.Take(), c = pool.Take();
	std::cout << "took " << a << ' ' << b << ' ' << c << '\n';
	pool.Give(b);
	std::cout << "after giving back " << b << ", next take: " << pool.Take() << '\n';
	std::cout << "then: " << pool.Take() << ' ' << pool.Take() << '\n';
}
```

```text output-of="basics-cpp-memory-pool.cpp"
took 0 1 2
after giving back 1, next take: 1
then: 3 -1
```

1. **Line 6:** `Next` is the free list: slot 0 points to 1, slot 1 to 2, slot 2 to 3, and slot 3 to `-1`, the end.
2. **Line 8:** `Take` removes the head of the list.
3. **Line 9:** `Give` puts a slot back at the head, so the next `Take` returns it, as the second line of output shows.

An arena holds objects only when they are built in its bytes. `std::construct_at(pointer, arguments)` builds an object at an address you give it, and `std::destroy_at(pointer)` runs its destructor by hand. A type without a destructor that does work needs no destroy call before the arena resets. Two more tools appear in Exercise 4: `alignof(T)` gives the alignment of a type, and `reinterpret_cast<T*>(address)` reads an address of raw bytes as a pointer to `T`.

Strata has one allocator of this family. `RangeAllocator` in `Strata/src/Strata/Core/RangeAllocator.h` hands out offsets over a range, with alignment, and merges neighbouring free ranges when they are returned. It holds no memory itself: the units are whatever the caller's buffer holds. The renderer's geometry pool uses it to place meshes inside large buffers on the :term[graphics processing unit]{id=gpu} (GPU), as [The geometry pool](../gpu/geometry-pool.md) shows.

## Common mistakes

- **A `new` without a `delete`.** The symptom is memory use that grows during play, and nothing fails. Hold the object in a unique pointer, so its end deletes it.
- **A `delete` twice.** The symptom is a crash in the heap, often far from the second `delete`. Give the object one owner, and set a raw pointer you keep to `nullptr` after the object ends.
- **A pointer to a local returned from a function.** The symptom is wrong values or a crash after the call. Return the object by value, or a unique pointer to a heap object.
- **A pointer kept into a `std::vector` that then grows.** The vector moves its elements to new memory, and the pointer dangles. Keep the index, or request the pointer again after the change.
- **Two shared pointers made from one raw pointer.** Each starts its own count, and the object is deleted twice. Copy the shared pointer, never rebuild it from a raw pointer.
- **A cycle of shared pointers.** The symptom is a destructor that never logs. Make one link a weak pointer.
- **A reference to a temporary that is gone.** A reference to an object that ended is as dangling as a pointer. Check the owner's lifetime before you keep one.

## Summary

- A pointer holds an address that `*` follows, and `->` follows it to a member. A reference is another name for an object, never empty and never rebound; pass large values by `const` reference.
- Locals live to the closing brace, statics to the end of the run, and heap objects until `delete`. Destructors run at the end of a lifetime, in the reverse order of construction, and RAII uses them to release resources on every path.
- A leak, a dangling pointer, a double delete and a use after free all come from an unclear owner. Undefined behavior, such as signed overflow or an index past the end, has no defined result.
- `std::unique_ptr` is the sole owner and only moves, `std::shared_ptr` counts owners and costs a control block and atomic counts, and `std::weak_ptr` watches without owning and breaks cycles. Strata names them `Scope`, `Ref` and `WeakRef`, and raw pointers are borrowed.
- Heap allocation costs time, so engines allocate at load or from allocators: an arena rounds offsets up to alignment and frees all at once, a pool hands out equal slots through a free list.

## Check yourself

1. What does `int* p = &x; *p = 7;` do to `x`?

   - A. Nothing: `p` holds a copy of `x`.
   - B. It stores 7 in `x`.
   - C. It stores 7 in `p`.
   - D. It does not compile, because `&` is only for references.

   :::answer{tests="pointers"}
   B. `&x` is the address of `x`, `p` stores it, and `*p = 7` writes 7 at that address. A reads a pointer as a copy, C confuses the pointer with its object, and D mixes up the `&` of a type with the `&` of an expression.
   :::

2. A function has `static int calls = 0;` as its first line and is called three times. How often does the initialization run, and what does the third call see?

   - A. Three times; the third call sees 0.
   - B. Once; the third call sees the count that the second left.
   - C. Once; each call starts again from 0.
   - D. Never; static variables start in `main`.

   :::answer{tests="lifetimes"}
   B. A `static` local is built when its line is first reached and lives until the program ends, so later calls see the stored value. A and C treat it as an ordinary local.
   :::

3. Which line has the bug?

   ```cpp pseudocode
   Enemy* a = new Enemy();
   Enemy* b = a;
   delete a;
   b->Health = 0;
   ```

   Trace which line ends the enemy and which line uses it later.

   :::answer{tests="memory-bugs"}
   The last line: a use after free. `b` held the same address as `a`, and the `delete` ended the enemy. `b` is dangling, and the write is undefined behavior.
   :::

4. A class has a `std::unique_ptr<Texture>` member, and you write `Material copy = material;`. What happens?

   - A. It compiles, and the two materials share the texture.
   - B. It compiles, and the texture is copied.
   - C. It does not compile: the unique pointer cannot be copied, so `Material` cannot be.
   - D. It compiles, and `material` becomes empty.

   :::answer{tests="ownership"}
   C. A copy would give the texture two owners. Moving works: `Material moved = std::move(material);`. D describes a move, not a copy.
   :::

5. An arena has 24 bytes used and gets a request for 4 bytes aligned to 16. Where do the bytes start, and how many bytes are used after?

   - A. Offset 24, 28 used.
   - B. Offset 32, 36 used.
   - C. Offset 16, 20 used.
   - D. Offset 28, 32 used.

   :::answer{tests="allocators"}
   B. (24 + 15) / 16 × 16 = 32, and 32 + 4 = 36. A ignores alignment, C moves backwards over used bytes, and D adds the size before rounding.
   :::

## Practice

Every exercise runs in the `Playground` script of [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own). For exercises 1 to 4, put the code into `OnCreate`, add `#include <memory>` at the top of the file, press **Ctrl+B** to build, press Play and read the **Console**. The worked solutions are complete programs that print with `std::cout`; the script prints the same lines with `Log::Info`.

If the **Console** still shows the lines of your earlier code, read the last line of the build: `(the module was up to date)` at its end means that it compiled nothing. A build compares the times of files, and a drive that keeps them in steps of two seconds can hide a change saved right after a build. Save the file again and press **Ctrl+B**.

1. **Basic.** Predict the log, then run it. Four objects are made, one of them in an inner scope. Write the eight lines before you build.

   ```cpp pseudocode
   struct Noisy { const char* Name; Noisy(const char* name) : Name(name) { Log::Info("make ", Name); } ~Noisy() { Log::Info("drop ", Name); } };
   Noisy x("x");
   Noisy y("y");
   {
   	Noisy z("z");
   }
   Noisy w("w");
   ```

   The struct goes above your script class, and the other lines go into `OnCreate`.

   :::answer[Worked solution]{tests="lifetimes" solution="sketches/basics-cpp-memory-exercise-order.cpp"}
   The log is make x, make y, make z, drop z, make w, drop w, drop y, drop x: the inner scope ends first, then the outer objects drop in reverse.

   ```cpp sketch="basics-cpp-memory-exercise-order.cpp"
   // Exercise 1: four objects, one of them in a nested scope; the log shows the order of makes and drops.
   #include <iostream>

   struct Noisy
   {
   	const char* Name;
   	explicit Noisy(const char* name)
   		: Name(name)
   	{
   		std::cout << "make " << Name << '\n';
   	}
   	~Noisy() { std::cout << "drop " << Name << '\n'; }
   };

   int main()
   {
   	Noisy x("x");
   	Noisy y("y");
   	{
   		Noisy z("z");
   	}
   	Noisy w("w");
   }
   ```

   ```text output-of="basics-cpp-memory-exercise-order.cpp"
   make x
   make y
   make z
   drop z
   make w
   drop w
   drop y
   drop x
   ```

   1. **Line 21:** `z` is gone at the brace; the log shows `drop z` before `make w`.
   :::

2. **Medium.** Make `std::unique_ptr<int> a = std::make_unique<int>(5);` and then try `std::unique_ptr<int> b = a;`. Read the :term[compile error]{id=compile-error}, then change the line so that it compiles, and log `*b`.

   :::answer[Worked solution]{tests="ownership" solution="sketches/basics-cpp-memory-exercise-move.cpp"}
   The compiler reports a use of a deleted function: the copy constructor of `unique_ptr` is deleted, because two owners would mean two deletes. The line that compiles uses `std::move(a)`, which hands the object to `b` and empties `a`.

   ```cpp sketch="basics-cpp-memory-exercise-move.cpp"
   // Exercise 2: the copy does not compile; the move does, and leaves the first pointer empty.
   #include <iostream>
   #include <memory>
   #include <utility>

   int main()
   {
   	std::unique_ptr<int> a = std::make_unique<int>(5);
   	std::unique_ptr<int> b = std::move(a);
   	std::cout << "b holds " << *b << ", a is empty: " << std::boolalpha << (a == nullptr) << '\n';
   }
   ```

   ```text output-of="basics-cpp-memory-exercise-move.cpp"
   b holds 5, a is empty: true
   ```

   1. **Line 10:** `a` is empty after the move, so the program compares it with `nullptr` and does not read it.
   :::

3. **Medium.** Make `std::shared_ptr<int> a`, a `std::weak_ptr<int>` from it, and two more shared copies. Log `use_count()`, reset one copy, log again, reset the rest, and log `expired()` of the weak pointer. Predict all three values.

   :::answer[Worked solution]{tests="ownership" solution="sketches/basics-cpp-memory-exercise-count.cpp"}
   The count is 3 (`a`, `b`, `c`; the weak pointer does not count), then 2 after `b.reset()`. After the last owner resets, the object is gone and `expired()` is true.

   ```cpp sketch="basics-cpp-memory-exercise-count.cpp"
   // Exercise 3: the count of a shared pointer as copies come and go, and a weak pointer that expires.
   #include <iostream>
   #include <memory>

   int main()
   {
   	std::shared_ptr<int> a = std::make_shared<int>(1);
   	std::weak_ptr<int> w = a;
   	std::shared_ptr<int> b = a;
   	std::shared_ptr<int> c = b;
   	std::cout << "count " << a.use_count() << '\n';
   	b.reset();
   	std::cout << "count " << a.use_count() << '\n';
   	a.reset();
   	c.reset();
   	std::cout << "expired " << std::boolalpha << w.expired() << '\n';
   }
   ```

   ```text output-of="basics-cpp-memory-exercise-count.cpp"
   count 3
   count 2
   expired true
   ```

   1. **Line 8:** the weak pointer watches `a`'s object and adds nothing to the count.
   2. **Lines 14–15:** the last two owners reset, so the count reaches 0 and the object is deleted.
   :::

4. **Hard.** Extend the arena of this page: a function `Create` that rounds the offset up to `alignof(Particle)`, builds a `Particle` in the bytes with `std::construct_at`, and returns a pointer, or `nullptr` when the buffer is full. Create particles in a loop until it fails, and log how many fit.

   :::answer[Worked solution]{tests="allocators" solution="sketches/basics-cpp-memory-exercise-arena.cpp"}
   A `Particle` takes 8 bytes (a `float` and an `int`) and has alignment 4, and the buffer has 64 bytes, so 8 fit. The fixed alignment of the buffer start (`alignas(8)`) makes every offset that is a multiple of 4 an aligned address.

   ```cpp sketch="basics-cpp-memory-exercise-arena.cpp"
   // Exercise 4: an arena over a fixed buffer, whose bytes become Particle objects through std::construct_at.
   #include <cstddef>
   #include <iostream>
   #include <memory>

   struct Particle { float X; int Id; };
   struct Arena
   {
   	alignas(8) unsigned char Bytes[64];
   	std::size_t Used = 0;
   	Particle* Create(float x, int id)
   	{
   		std::size_t start = (Used + alignof(Particle) - 1) / alignof(Particle) * alignof(Particle);
   		if (start + sizeof(Particle) > sizeof(Bytes)) return nullptr;
   		Used = start + sizeof(Particle);
   		return std::construct_at(reinterpret_cast<Particle*>(Bytes + start), Particle{ x, id });
   	}
   };
   int main()
   {
   	Arena arena; int made = 0;
   	while (arena.Create(0.5f, made) != nullptr) made++;
   	std::cout << "made " << made << ", used " << arena.Used << " bytes\n";
   	std::destroy_at(reinterpret_cast<Particle*>(arena.Bytes)); // nothing to clean up here; shows the call
   }
   ```

   ```text output-of="basics-cpp-memory-exercise-arena.cpp"
   made 8, used 64 bytes
   ```

   1. **Line 13:** the same round-up as the arena of this page, with the type's own alignment.
   2. **Line 16:** `std::construct_at` builds the particle in the buffer.
   3. **Line 24:** `std::destroy_at` runs the destructor by hand. A `Particle` has nothing to clean up, but a type that does needs this call before the arena resets.
   :::

5. **Hard.** Optional: in `Playground.cpp`, replace everything below `using namespace Strata;` with the code below, press **Ctrl+B** and play. The script makes an entity `Marker` with a script of its own and keeps the pointer that `AddScript<Marker>()` returns. In frame 60 it destroys the entity, as a game destroys a coin that the ball collects. Watch the **Console**, say what goes wrong, and fix it.

   ```cpp pseudocode
   class Marker : public Script {};

   class Playground : public Script
   {
   public:
   	void OnCreate() override { m_Marker = Scene::CreateEntity("Marker").AddScript<Marker>(); }

   	void OnUpdate(float) override
   	{
   		m_Frame++;
   		if (m_Frame == 60)
   			m_Marker->GetEntity().Destroy();
   		if (m_Frame >= 58 && m_Frame <= 62)
   			Log::Info("frame ", m_Frame, ", marker: ", m_Marker->GetEntity().GetName());
   	}

   private:
   	Marker* m_Marker = nullptr;
   	int m_Frame = 0;
   };

   ST_SCRIPT_CLASS(Marker) {}
   ST_SCRIPT_CLASS(Playground) {}
   ```

   1. **Line 6:** `AddScript<Marker>()` returns the address of a script object that the engine owns.
   2. **Line 12:** `Destroy` ends the entity, and its script object with it, at the end of frame 60.
   3. **Line 14:** frames 61 and 62 still read through the pointer.

   :::answer[Worked solution]{tests="memory-bugs"}
   The pointer is borrowed: the engine owns the `Marker` object and deletes it with the entity at the end of frame 60, so `m_Marker` dangles from frame 61 on. Reading it is undefined behavior: the script may log a stale name, crash, or seem to work.

   In a run with the 0.8.0 release, frames 58 to 60 logged `Marker`. Frame 61 brought the warning `GetEntityName (called by script 'Playground' on entity 'Playground'): entity ... does not exist`, and frames 61 and 62 logged an empty name: the freed memory still held the old entity's number. Another build may crash at the same line.

   The fix is to keep what stays valid and ask again each time. An `Entity` is a plain value that holds the entity's identifier number, and `GetScript` returns `nullptr` when the entity or its script is gone. The member `Entity m_MarkerEntity;` takes the place of `m_Marker`.

   ```cpp pseudocode
   	void OnCreate() override
   	{
   		m_MarkerEntity = Scene::CreateEntity("Marker");
   		m_MarkerEntity.AddScript<Marker>();
   	}

   	void OnUpdate(float) override
   	{
   		m_Frame++;
   		if (m_Frame == 60)
   			m_MarkerEntity.Destroy();
   		Marker* marker = m_MarkerEntity.GetScript<Marker>();
   		if (m_Frame >= 58 && m_Frame <= 62)
   			Log::Info("frame ", m_Frame, ", marker: ", marker ? marker->GetEntity().GetName() : "gone");
   	}
   ```

   1. **Line 3:** the script keeps the entity, a plain value, and no pointer.
   2. **Line 12:** it asks for the script again in every frame; the pointer lives for one frame.
   3. **Line 14:** a missing script is a case the code handles. The fixed script logs `Marker` in frames 58 to 60 and `gone` in frames 61 and 62. `Destroy` takes effect at the end of the frame, so frame 60 still finds the script.

   A hot reload is the other way to lose a script object. A rebuild while the game runs deletes every script instance and makes new ones of the new code. The new `Playground` keeps only its fields, so `m_Marker` and `m_MarkerEntity` start over, and `OnReload` runs instead of `OnCreate`. A script that keeps an entity or a pointer finds it again in `OnReload`, here with `Scene::FindEntityByName("Marker")`.
   :::

## Where the book uses it

- [C++ classes in depth](cpp-classes.md) uses destructors and ownership to explain virtual calls and interfaces.
- [Conventions](../core/conventions.md) uses `Scope`, `Ref`, borrowed pointers and RAII as Strata's rules.
- [Residency](../assets/residency.md) uses the cost of a shared count and dangling pointers to explain why assets are held by handle.
- [Resource lifetimes on the GPU](../gpu/resources-lifetimes.md) uses ownership and delayed destruction for graphics objects.

## Further reading

- Learn C++ (learncpp.com), chapters 12 and 22: pointers, references and smart pointers in small lessons; beginner.
- [cppreference: smart pointers](https://en.cppreference.com/w/cpp/memory): the library's reference for `unique_ptr`, `shared_ptr` and `weak_ptr`; intermediate.
- [cppreference: undefined behavior](https://en.cppreference.com/w/cpp/language/ub): the list of cases the language leaves undefined; intermediate.
- A Tour of C++ by Bjarne Stroustrup, the chapter on resource management: why RAII is the language's answer to cleanup; intermediate.
- Effective Modern C++ by Scott Meyers, items 18 to 22: the rules for the three smart pointers; advanced.
