---
id: basics/cpp-generic
title: "Generic C++: templates, lambdas and the standard containers"
description: "Templates, the standard containers and algorithms, lambdas, std::function, C callbacks, type erasure and CRTP: the C++ that Strata's engine code is made of."
kind: primer
size: L
tracks: [B, E]
needs: [basics/cpp-classes, basics/trees-graphs]
time: 110
learn:
  - id: templates
    text: write a function template and a class template, and explain what the compiler makes of each use
  - id: containers
    text: choose a standard container and algorithm from what each costs, and name what makes an iterator invalid
  - id: lambdas
    text: predict what a lambda reads when it captures by value or by reference, and name when a capture dangles
  - id: callbacks
    text: write a list of std::function callbacks and explain the C form with a function pointer and a user pointer
  - id: erasure
    text: explain type erasure, CRTP and a pointer to a member as the engine's property and script builders use them
status: final
---

::::test-out

1. Write a function template `Twice` that returns its argument multiplied by 2, for any type that can be multiplied.

   :::answer{tests="templates"}
   The answer is a template with one open type, `T`:

   ```cpp pseudocode
   template<typename T>
   T Twice(T value)
   {
   	return value * 2;
   }
   ```

   `T` stands for the type. The compiler writes `Twice` for `int` when you call `Twice(4)` and for `float` when you call `Twice(1.5f)`.
   :::

2. The vector `v` holds 1, 2, 3, 4. What does it hold after `v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; }), v.end());`?

   :::answer{tests="containers"}
   The vector holds 1 and 3. `remove_if` moves the odd values to the front and returns the new end, and `erase` cuts off the rest.
   :::

3. What do `a()` and `b()` return in the code below?

   ```cpp pseudocode
   int n = 1;
   auto a = [n]() { return n; };
   auto b = [&n]() { return n; };
   n = 5;
   ```

   Read the capture lists in the square brackets.

   :::answer{tests="lambdas"}
   `a()` returns 1 and `b()` returns 5. The lambda `a` copied `n` when it was made; `b` reads the variable itself.
   :::

4. A C library asks for a callback. Which two values do you give it in place of a lambda that has captures?

   :::answer{tests="callbacks"}
   A pointer to a plain function, and a `void*` user pointer. The library hands the user pointer back to your function, which turns it into the real type.
   :::

5. With `struct Coin { float Speed; };` and `float Coin::* field = &Coin::Speed;`, what does `coin.*field` give for a coin whose `Speed` is 3?

   :::answer{tests="erasure"}
   The result is 3. A pointer to a member names the field `Speed` of the class, and `.*` reads that field from the object on its left.
   :::

::::

## Why you will need this

Strata's engine code is written with the tools of this page. Its log calls accept any number of values, its property lists
store one small function per field, and its work queues hold callbacks. Without the ideas below, those lines read as noise.

This page teaches templates, the standard containers and algorithms, lambdas, and the ways a program keeps a function to
call later. It ends with type erasure and the curiously recurring template pattern (CRTP), two ways to hide a type.

You will meet these ideas again. [Modern C++](../basics/cpp-modern.md) builds on them, and [Threads](../basics/threads.md)
starts a thread from a lambda. The script lesson on the application binary interface (ABI) and the software development kit (SDK),
[Inside the ABI and the SDK](../scripting/abi-sdk.md), reads how `ST_SCRIPT_FIELD` passes a member of your class to a template.
At the end you sort the coins of Coin Run by their distance to the ball.

This page needs no download. Only the Practice needs a project: the one that holds your `Playground` script, which [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own) puts on an empty entity, and Coin Run for the optional last exercise, which names a download.

Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), two pages on. On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## A template is a function the compiler writes for you

Suppose you need the square of an `int`, and later of a `float`. You write `SquareInt`, then `SquareFloat`, and the two
bodies are the same except for the type. A third type means a third copy, and a fix to one copy must reach all of them.

A **C++ template** is code with a type left open, from which the compiler writes a version for each type you use. The
type gets a name in angle brackets, as `GetScript<Coin>` did in [Programming 3](../basics/programming-3.md).

```cpp sketch="basics-cpp-generic-templates.cpp"
// A function template and a class template: the compiler writes one version for each argument it meets.
#include <iostream>

template<typename T>
T Square(T value)
{
	return value * value;
}

template<typename T, int Count>
struct Row
{
	T Values[Count] = {};
	int Size() const { return Count; }
};

int main()
{
	std::cout << "Square(4) = " << Square(4) << '\n';
	std::cout << "Square(1.5f) = " << Square(1.5f) << '\n';
	std::cout << "bytes of Row<float, 3>: " << sizeof(Row<float, 3>) << '\n';
	std::cout << "bytes of Row<double, 3>: " << sizeof(Row<double, 3>) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-templates.cpp"
Square(4) = 16
Square(1.5f) = 2.25
bytes of Row<float, 3>: 12
bytes of Row<double, 3>: 24
```

1. **Lines 4–8:** `T` is the open type. The call `Square(4)` has an `int` argument, so the compiler finds that `T` is `int`.
2. **Lines 10–15:** a class template takes a type and a number. `Row<float, 3>` and `Row<double, 3>` are two different
   types, which is why their sizes differ.

Follow one call by hand. The compiler sees `Square(4)`, finds that `T` is `int`, and writes `int Square(int value)` with the
body `return value * value;`. The result is 16. For `Square(1.5f)` it writes a second function for `float` and the result
is 2.25. The program holds two functions, and each is plain code that was checked for its own type.

```mermaid caption="One template gives one function for each type that a call uses; a type nobody uses gets no function." alt="A box for the template Square points to two boxes: Square for whole numbers, which the call with 4 uses, and Square for float, which the call with 1.5 uses."
flowchart LR
    A["template Square of T"] --> B["Square for whole numbers: Square(4) gives 16"]
    A --> C["Square for float: Square(1.5f) gives 2.25"]
```

An argument that is a type is a **type argument**; the `3` of `Row<float, 3>` is a value argument, a number the compiler
knows while it builds. A template may take several of each. All of this happens during the build: a template costs
build time and program size, one copy of the code per type, and nothing extra while the game runs.

The number of arguments can vary too. The SDK's `Log::Info` accepts any number of values and writes them one after the
other. Read the lines below for the `...` marks.

```cpp src="StrataScriptCore/Include/StrataScript/Log.h#L63-L86"
	template<typename... Args>
	static void Trace(const Args&... args) { Write(StrataScriptLogLevel_Trace, args...); }

	template<typename... Args>
	static void Info(const Args&... args) { Write(StrataScriptLogLevel_Info, args...); }

	template<typename... Args>
	static void Warn(const Args&... args) { Write(StrataScriptLogLevel_Warn, args...); }

	template<typename... Args>
	static void Error(const Args&... args) { Write(StrataScriptLogLevel_Error, args...); }
private:
	template<typename... Args>
	static void Write(uint32_t level, const Args&... args)
	{
		const StrataScriptHostAPI* host = Detail::GetHost();
		if (!host)
			return;

		std::ostringstream stream;
		(Detail::AppendLogValue(stream, args), ...);
		const std::string message = stream.str();
		host->Log(level, Detail::ToABIString(message));
	}
```

1. **Lines 66–67:** `typename... Args` is a pack, a list of types of any length; `const Args&... args` is the matching list of values.
2. **Line 67:** `Info` hands the whole pack on to `Write`.
3. **Lines 75–76:** `Write` is a template as well; the pack arrives there as `args`.
4. **Line 83:** the fold expression with `, ...` calls `AppendLogValue` once for each value, in order.

The engine's own log macros work the same way with a format string first. In `ST_CORE_INFO("Loaded {}", path)` each `{}`
takes the next value. A template that takes a format string and then values is the standard shape of a log call.

:::why[Why templates and not one function that takes any value]
A function that takes a `void*` has forgotten the type, so the compiler cannot check it and the program must remember
the type by itself. A template keeps the type, so a wrong call stops the build, and the code for each type is as fast
as code written by hand. The price is that every version is built again in each file that uses it, so templates live in headers.
:::

## `static_assert` stops a wrong argument at build time

A template accepts every type until its body fails to build, and the failure message can run to dozens of lines.
`static_assert(condition, "message")` gives a short message that you write, and it fails the build when the condition
is false.

Take `Half`, which divides by 2. For `Half(5.0f)` the answer is 2.5. For `Half(5)` the division of whole numbers gives 2
and drops the 0.5, with no warning. The assertion below turns that silent loss into a stopped build.

```cpp sketch="basics-cpp-generic-staticassert.cpp"
// A static_assert inside a template checks the argument while the program builds.
#include <iostream>
#include <type_traits>

template<typename T>
T Half(T value)
{
	static_assert(std::is_floating_point_v<T>, "Half needs a float or a double");
	return value / 2;
}

int main()
{
	std::cout << "Half(5.0f) = " << Half(5.0f) << '\n';
	// Half(5) does not build: T is int, and the message above appears in the build output.
	return 0;
}
```

```text output-of="basics-cpp-generic-staticassert.cpp"
Half(5.0f) = 2.5
```

1. **Line 8:** `std::is_floating_point_v<T>` is a question about a type that the compiler answers while it writes the version for `T`.

The check costs nothing at run time, because the program that is built holds no trace of it. Strata uses the same tool
where a script declares a field. The function that registers a field checks its type, which is why a `double` field
stops the build with a message of its own.

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L778-L794"
// Registers a public data member as a field. Its value in a default-constructed instance is the default.
template<auto Member>
ScriptClassBuilder& Field(std::string_view name)
{
	using Traits = Detail::MemberPointerTraits<decltype(Member)>;
	using MemberType = typename Traits::MemberType;
	static_assert(std::is_base_of_v<typename Traits::ClassType, T>, "The field must be a member of the script class or its bases");
	static_assert(Detail::c_IsFieldType<MemberType>,
		"Unsupported script field type: use bool, int32_t, float, glm::vec2/3/4, glm::quat, std::string, Strata::Entity or Strata::AssetHandle");

	Detail::FieldBinding& field = m_Record.Fields.emplace_back();
	field.Name = std::string(name);
	field.Type = Detail::ValueTraits<MemberType>::Type;
	field.Get = &Detail::GetFieldValue<T, Member>;
	field.Set = &Detail::SetFieldValue<T, Member>;
	return *this;
}
```

1. **Lines 778–780:** `Field` takes a pointer to a member as its :term[template argument]{id=template-argument}; a later section shows what that is.
2. **Lines 782–783:** the traits pull the class and the field's type out of the pointer's type.
3. **Lines 784–786:** two assertions: the member belongs to the script's class, and its type is one of the field types.
4. **Lines 791–792:** two function pointers, written for this class and this member, are stored with the field.

## The standard library holds the containers you would write otherwise

You have a list of coins, a table from names to values, and a set of tags with no repeats. Writing each structure
yourself is slow, and a mistake in it is likely.

The **standard library** is the code that comes with every C++ compiler.

A **container** is a ready-made type from that library that holds many values: a list, a table or a set, each built for a kind of job.

The costs below come from the lessons on [arrays and hash maps](../basics/data-structures.md) and on
[trees and ordered maps](../basics/trees-graphs.md). The table names each container, how it finds a value, and a use in the engine.

| Container | What it holds | Finding a value | Strata uses it for |
| --- | --- | --- | --- |
| `std::vector` | a row that grows at the end | by position, one step | the main-thread queue `m_MainThreadQueue` in `Strata/src/Strata/Core/Application.h` |
| `std::array` | a row whose size is part of its type | by position, one step | the three recency orders of the asset manager, in `Strata/src/Strata/Asset/AssetManager.h` |
| `std::deque` | a row with fast adding at both ends | by position, one step | the latest content changes, oldest first, in the same file |
| `std::map` | keys kept in sorted order | by key, about 10 steps for 1,000 keys | `RecencyOrder` in the same file |
| `std::unordered_map` | keys in no order | by key, about 1 step | the script instances of each entity, in `Strata/src/Strata/Scripting/ScriptSystem.h` |
| `std::set` | keys without values, no repeats | by key, about 10 steps for 1,000 keys | the indexed folders of the editor's asset manager |
| `std::bitset` | a fixed number of on or off flags | by position, one step | the key states in `Strata/src/Strata/Input/Input.cpp` |
| `std::pair` | two values of any types | by name, `first` and `second` | a width and a height from `GetSizeOption` in `Strata/src/Strata/Core/CommandLine.h` |
| `std::tuple` | any fixed number of values | by position, `std::get<1>` | the sort key of the streaming queue in `Strata/src/Strata/Asset/AssetStreamingQueue.h` |

The step counts come from halving. A sorted tree with 1,000 keys needs about 10 comparisons to find one, because $2^{10}$
is 1,024; here $2^{10}$ is read "two to the power ten". A :term[hash table]{id=hash-map} needs about one step whatever its size, and a
vector in no order may need all 1,000.

Choose by the question you ask most. If you walk the values in order, choose `std::map`. If you only look values up, choose
`std::unordered_map`. If neither, a `std::vector` holds its values side by side in memory and is usually the fastest to walk.

```cpp sketch="basics-cpp-generic-containers.cpp"
// Four containers that hold the same coin values.
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

int main()
{
	std::vector<int> values = { 30, 10, 20, 10 };
	std::map<std::string, int> ordered = { { "gold", 3 }, { "bronze", 1 }, { "silver", 2 } };
	std::unordered_map<std::string, int> hashed(ordered.begin(), ordered.end());
	std::set<int> unique(values.begin(), values.end());

	std::cout << "vector[2] = " << values[2] << ", size " << values.size() << '\n';
	std::cout << "map in order:";
	for (const auto& entry : ordered)
		std::cout << ' ' << entry.first << '=' << entry.second;
	std::cout << "\nunordered_map silver = " << hashed.at("silver") << '\n';
	std::cout << "set holds " << unique.size() << " values, first " << *unique.begin() << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-containers.cpp"
vector[2] = 20, size 4
map in order: bronze=1 gold=3 silver=2
unordered_map silver = 2
set holds 3 values, first 10
```

1. **Lines 11–14:** four containers made from the same values; the set drops the repeated 10.
2. **Lines 17–19:** the map lists its keys sorted: bronze, gold, silver. A hash table would not promise any order.
3. **Line 20:** `at` looks a key up and complains when it is missing; the `[]` of a map adds the key when it is missing.

## An iterator is a position in a container

You often need to visit every value without knowing how the container stores them. An **iterator** is an object that
stands for one position in a container: `*it` reads the value there and `++it` moves to the next. Every container hands
out iterators the same way, so one loop shape works for all of them.

`v.begin()` is the first position and `v.end()` is one past the last, where no value lives. A loop runs while the
iterator differs from `end()`. The range-based `for` that you know is a short form of exactly this loop.

```cpp pseudocode
for (int value : v)       // the short form
	Log::Info(value);

for (auto it = v.begin(); it != v.end(); ++it)   // what the compiler runs
	Log::Info(*it);
```

`v.rbegin()` and `v.rend()` give reverse iterators, which walk from the last value to the first. The sketch below walks forward, walks
backward, and removes values while it walks.

```cpp sketch="basics-cpp-generic-iterators.cpp"
// Iterators: a forward walk, a reverse walk, and an erase that hands back the next position.
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> v = { 10, 20, 30, 40 };
	for (std::vector<int>::iterator it = v.begin(); it != v.end(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
	for (auto it = v.rbegin(); it != v.rend(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
	for (auto it = v.begin(); it != v.end();)
	{
		if (*it == 20 || *it == 30)
			it = v.erase(it);
		else
			++it;
	}
	std::cout << "left: " << v.size() << ", first " << v[0] << ", last " << v[1] << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-iterators.cpp"
10 20 30 40 
40 30 20 10 
left: 2, first 10, last 40
```

1. **Lines 14–20:** `erase` removes the value and returns the position of the next one, so the loop moves on only when it did not erase.

An iterator can become **invalid**: it points at a place that no longer holds what it did, and using it is undefined
behaviour. Take a vector with room for 4 values that already holds 4. A fifth `push_back` finds no room, so the vector
allocates a larger block, copies the 4 values, and frees the old block. An iterator taken before points into the freed block.

The same holds for pointers and references into the vector. For a `std::vector`, `erase` makes the erased position and every
one after it invalid. An insert into a `std::unordered_map` can make iterators invalid when the table grows, while an insert
into a `std::map` leaves them valid. The safe habit is to take an iterator again after any change, or to keep an index.

## The standard algorithms work on ranges

You have a list of 6 numbers and need it sorted, the first even one, and all the even ones gone. The standard library
holds these jobs as functions that take two iterators, the start and the end of the range to work on.

`std::sort` puts the values in order. By default it uses `<`, and you may pass a function that decides which of two
values goes first; sorting 1,000 values takes about 10,000 comparisons. `std::find_if` returns an iterator to the first
value for which a function answers true, or `end()` when none does. `std::remove_if` removes in a surprising way:
it moves the values you keep to the front and returns the new end, but it receives iterators and cannot change the
container's size. The size changes only when you call `erase` on the container with the range from the new end to the old end.

Follow the numbers. Sorted from the highest, `5 2 8 1 9 3` becomes `9 8 5 3 2 1`. The first even value is 8. Removing the even
values keeps 9, 5, 3 and 1 in front; the container still holds 6 values, and the last two have no promised content. `erase`
cuts them off and leaves 4.

```cpp sketch="basics-cpp-generic-algorithms.cpp"
// Sort with a comparator function, find the first match, and remove with the erase idiom.
#include <algorithm>
#include <iostream>
#include <vector>

bool Higher(int a, int b) { return a > b; }
bool IsEven(int value) { return value % 2 == 0; }

int main()
{
	std::vector<int> v = { 5, 2, 8, 1, 9, 3 };
	std::sort(v.begin(), v.end(), Higher);
	std::cout << "first: " << v.front() << '\n';
	auto found = std::find_if(v.begin(), v.end(), IsEven);
	std::cout << "first even: " << *found << '\n';
	auto newEnd = std::remove_if(v.begin(), v.end(), IsEven);
	std::cout << "size before erase: " << v.size() << '\n';
	v.erase(newEnd, v.end());
	std::cout << "size after erase: " << v.size() << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-algorithms.cpp"
first: 9
first even: 8
size before erase: 6
size after erase: 4
```

1. **Lines 6–7:** two small functions that answer a question about values; the algorithms call them.
2. **Line 16:** `remove_if` returns the new end, and the size still reads 6 on line 17.
3. **Line 18:** `erase` with the range from the new end to the old end shrinks the vector to 4. Writing `remove_if` without `erase` is a common mistake.

The engine writes this pair of calls in many places. In `Strata/src/Strata/Scripting/ScriptSystem.cpp` the function
`IsDestroyed` is the test, passed by its name with `&`, and the erase follows on the same line.

:::note[Measuring what a sort costs]
To time a piece of code, read a clock before and after. `std::chrono::steady_clock` never runs backward, unlike the clock on the
wall, so it suits measuring. The difference of two readings is a duration; `duration_cast` turns it into a unit you choose.

```cpp pseudocode
const auto start = std::chrono::steady_clock::now();
std::sort(v.begin(), v.end());
const auto elapsed = std::chrono::steady_clock::now() - start;
const auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(elapsed).count();
```

Strata uses the same clock for deadlines: the code in `Strata/src/Platform/Posix/PosixProcess.cpp` adds a time to
`steady_clock::now()` and waits until the clock passes it.
:::

## A map node can move without a copy

A `std::map` keeps its entries in nodes, each one allocated on its own. Suppose you must change an entry's key, which
decides its place in the sorted order. Erasing the entry and inserting a new one frees a node and allocates another.
`extract` takes the node out of the map without freeing it and hands you a **node handle**; you may change `key()`
while you hold it, and `insert` puts it back.

:::question[What is `std::move`?]
The call `std::move` hands a value over instead of copying it; [Modern C++](../basics/cpp-modern.md) teaches it. Read `std::move(node)` as "give this node to `insert`".
:::

The sketch below moves the node with key 2 to the end of a small map; search for the hint in the last call.

```cpp sketch="basics-cpp-generic-nodes.cpp"
// Moving one node of a map to the end of the order, without a copy and without a search for the new place.
#include <iostream>
#include <map>
#include <string>
#include <utility>

int main()
{
	std::map<int, std::string> order = { { 1, "tree" }, { 2, "rock" }, { 3, "coin" } };
	auto node = order.extract(2);
	node.key() = 4;
	order.insert(order.end(), std::move(node));
	for (const auto& entry : order)
		std::cout << entry.first << ' ' << entry.second << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-nodes.cpp"
1 tree
3 coin
4 rock
```

1. **Line 10:** `extract(2)` takes out the node with key 2.
2. **Lines 11–12:** the key becomes 4, then the node goes in with `order.end()` as the hint. The hint says where the node probably belongs; when it is right, the insert takes one step.

The asset manager does this on every request for an asset. Its recency order is a map from a frame number and a
sequence number to an asset, and the latest request must go last.

```cpp src="Strata/src/Strata/Asset/AssetResidency.cpp#L343-L347"
ST_CORE_ASSERT(entry.RecencyNodes[index]->second == entry.Metadata.Handle, "Asset {} is missing from a recency order",
	entry.Metadata.Handle.ToString());
auto node = order.extract(entry.RecencyNodes[index]);
node.key() = key;
entry.RecencyNodes[index] = order.insert(order.end(), std::move(node));
```

The comment above these lines in the file explains the choice. Extracting the entry's own node and inserting it with the end as hint
both take :term[constant time]{id=constant-time}. A search for the key would walk down a tree of every resident asset, and a renderer requests
thousands of assets each frame.

## A lambda is a function you write where you use it

Look back at the algorithms sketch: `Higher` and `IsEven` sit far from the call that uses them. A test that needs a value
from the caller, such as a limit, has no place to get it.

A **lambda** is a function written in the middle of an expression, with no name, and it can keep values from the code around
it. Its written form has four parts: `[captures](parameters) { body }`.

A lambda is a short way to write a class. For each one the compiler writes a small class with a call operator and builds one object of it, a
**function object**: a value that you call like a function. The values the lambda keeps are the members of that object. For this reason
every lambda has its own type that you cannot spell, and you write `auto` for a variable that holds one.

The list in the square brackets is the **lambda capture**: what the lambda takes from the code around it. `[limit]`
copies `limit` when the lambda is made, `[&total]` keeps a reference to `total`, and `[this]` keeps the pointer to the
current object. `[]` keeps nothing.

Follow the numbers in the sketch. The vector holds 5, 2, 8 and is sorted from the highest: 8, 5, 2. `isBig` captures `limit`,
which is 4, by value, and the code then sets `limit` to 6. The count still uses 4 and finds 2 values above it (8 and 5); a capture
by reference would have used 6 and found 1. The last lambda captures `total` by reference and adds each value to it, so `total` ends at 15.

```cpp sketch="basics-cpp-generic-lambdas.cpp"
// A lambda is a function written where it is used; its capture list chooses what it keeps.
#include <algorithm>
#include <iostream>
#include <vector>

int main()
{
	std::vector<int> v = { 5, 2, 8 };
	std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });

	int limit = 4;
	auto isBig = [limit](int x) { return x > limit; };
	limit = 6;
	std::cout << "big with the old limit: " << std::count_if(v.begin(), v.end(), isBig) << '\n';

	int total = 0;
	std::for_each(v.begin(), v.end(), [&total](int x) { total += x; });
	std::cout << "sorted first " << v.front() << ", total " << total << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-lambdas.cpp"
big with the old limit: 2
sorted first 8, total 15
```

1. **Line 9:** a lambda with no captures as the ordering test, written at the call.
2. **Lines 12–13:** the copy was taken at line 12, so line 13 cannot reach it.
3. **Line 17:** `&total` lets the lambda change the caller's variable.

The engine uses lambdas as the sketch does. The lines below remove the simulated events of keys, buttons and axes from a
queue; the test is written in place and needs no name.

```cpp src="Strata/src/Strata/Input/Input.cpp#L744-L748"
queue.erase(std::remove_if(queue.begin(), queue.end(), [](const SimulatedEvent& event)
{
	return event.Type == SimulatedEventType::Key || event.Type == SimulatedEventType::MouseButton || event.Type == SimulatedEventType::GamepadButton
		|| event.Type == SimulatedEventType::GamepadAxis;
}), queue.end());
```

A capture by reference is a promise that the variable lives as long as the lambda does. Break it and the lambda reads
memory that has been freed.

```cpp pseudocode
auto MakeCounter()
{
	int count = 0;
	return [&count]() { return count; };   // count is destroyed when MakeCounter returns
}
```

The returned lambda holds a reference to `count`, which no longer exists after the function returns; reading it is
undefined behaviour, and the program may print anything or crash. Capture `[count]` instead and the lambda keeps its own copy.
The same holds for `[this]`: a lambda stored in a long-lived list that keeps the pointer to an object reads freed memory once the object is gone.

:::caution[Lifetimes]
Capture by value when the lambda lives longer than the function that made it. Capture by reference only when the lambda is used and
dropped inside the same function, as `[&total]` was above.
:::

The engine meets the `[this]` rule in one macro. `ST_BIND_EVENT_FN` in `Strata/src/Strata/Core/Base.h` makes a lambda that
captures `this` and calls a :term[member function]{id=member-function}, and `Application` uses it to give the window a function to call with each event. The
application owns its window, so the window is gone before the pointer is.

## `std::function` keeps anything you can call

Every lambda has its own type, so a variable, a list or a function parameter cannot name "any lambda". `std::function<void()>` is one
type that holds anything you can call with the signature in its angle brackets: a plain function, a lambda, a function object. The
type before the round brackets is the result, and the types inside them are the arguments, so `std::function<int(int)>` takes an
`int` and returns an `int`.

A **callback** is a function that you give to other code, so that the other code calls it later, when something happens. A
list of callbacks is a list of `std::function` values, called one after the other in the order they were added.

```cpp sketch="basics-cpp-generic-callbacks.cpp"
// A list of std::function callbacks, run in the order they were added.
#include <functional>
#include <iostream>
#include <vector>

int main()
{
	std::vector<std::function<void()>> callbacks;
	int coins = 0;
	callbacks.push_back([&coins]() { coins++; });
	callbacks.push_back([&coins]() { coins += 10; });
	callbacks.push_back([]() { std::cout << "all callbacks ran\n"; });
	for (const auto& callback : callbacks)
		callback();
	std::cout << "coins: " << coins << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-callbacks.cpp"
all callbacks ran
coins: 11
```

1. **Lines 10–12:** three lambdas, all stored as the same type; the first two keep `coins` by reference.
2. **Lines 13–14:** the loop calls them in the order they were added; `coins` goes 0, 1, 11.

:::question[What is the lock in the first line of the function?]
A lock lets one thread at a time use the queue; [Threads](../basics/threads.md) teaches it. Read the line as "wait for my turn".
:::

The application queue works the same way. A worker thread hands a function to `SubmitToMainThread`, which stores it in the
vector `m_MainThreadQueue`, and the main thread calls the functions at the start of its next frame.

```cpp src="Strata/src/Strata/Core/Application.cpp#L196-L200"
void Application::SubmitToMainThread(std::function<void()> function)
{
	std::scoped_lock<std::mutex> lock(m_MainThreadQueueMutex);
	m_MainThreadQueue.emplace_back(std::move(function));
}
```

A function can take a function and give one back. `MakeAdder(2)` returns a lambda that adds 2, and `Twice` calls the
function it receives two times: `Twice(addTwo, 5)` is `addTwo(addTwo(5))`, which is 9.

```cpp sketch="basics-cpp-generic-adder.cpp"
// A function that returns a function, and a function that takes one.
#include <functional>
#include <iostream>

std::function<int(int)> MakeAdder(int amount)
{
	return [amount](int x) { return x + amount; };
}

int Twice(const std::function<int(int)>& function, int x)
{
	return function(function(x));
}

int main()
{
	auto addTwo = MakeAdder(2);
	std::cout << "addTwo(5) = " << addTwo(5) << '\n';
	std::cout << "Twice(addTwo, 5) = " << Twice(addTwo, 5) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-adder.cpp"
addTwo(5) = 7
Twice(addTwo, 5) = 9
```

1. **Line 7:** the lambda copies `amount`, so it keeps working after `MakeAdder` has returned.
2. **Line 12:** a call through a `std::function` runs whatever it holds.

A `std::function` costs a little. The call goes through one more jump, and a lambda with a large capture may need a memory
allocation. An empty `std::function` is false in an `if`, and calling it fails; engine code checks first, as the window code does with `if (data.EventCallback)`.

## C libraries take a function pointer and a user pointer

Many libraries the engine uses, such as the window library GLFW and the audio library miniaudio, are written in C. C has
no lambdas and no `std::function`. It has the **function pointer**: the address of a plain function, written
`void (*function)(void* userData, int tick)` for a function that takes a `void*` and an `int` and returns nothing.

A plain function has no captures, so how does it reach your data? The library takes a second value, a `void*` **user
pointer**, stores it, and passes it back on every call. It is a hand-made `std::function`: the function pointer is the code
and the user pointer is the captured data. A lambda with no captures converts to a function pointer; one that has captures does not, because it
needs somewhere to keep them.

```cpp sketch="basics-cpp-generic-cstyle.cpp"
// The C form of a callback: a function pointer, a user pointer and a result code.
#include <iostream>

enum Result { Success = 0, InvalidArgument = 1 };

Result RunTicks(int count, void (*function)(void* userData, int tick), void* userData)
{
	if (!function || count < 0)
		return InvalidArgument;
	for (int tick = 1; tick <= count; tick++)
		function(userData, tick);
	return Success;
}

void AddTick(void* userData, int tick)
{
	*static_cast<int*>(userData) += tick;
}

int main()
{
	int sum = 0;
	Result result = RunTicks(4, AddTick, &sum);
	std::cout << "result " << result << ", sum " << sum << '\n';
}
```

```text output-of="basics-cpp-generic-cstyle.cpp"
result 0, sum 10
```

1. **Line 6:** the parameter list takes the function pointer, then the user pointer.
2. **Lines 8–9:** a result code reports misuse: a null function or a negative count returns `InvalidArgument`, and nothing runs.
3. **Line 17:** `static_cast<int*>(userData)` turns the `void*` back into the pointer it was.

`static_cast<T>(value)` converts a value to the type `T` by rules the compiler checks. A `void*` forgets its type, and
`static_cast` is how code states which type it was. The compiler cannot check that claim: if the user pointer pointed at a
`float` and the function casts it to `int*`, the function reads garbage. Always cast back to the very type you stored.

The window code of the engine does exactly this. It stores a pointer to its window data as the window's user pointer and
passes a lambda without captures as the callback.

```cpp src="Strata/src/Platform/GLFW/GLFWWindow.cpp#L230-L241"
glfwSetWindowUserPointer(m_Window, &m_Data);

glfwSetWindowSizeCallback(m_Window, [](GLFWwindow* window, int newWidth, int newHeight)
{
	WindowData& data = *static_cast<WindowData*>(glfwGetWindowUserPointer(window));
	data.Width = static_cast<uint32_t>(newWidth);
	data.Height = static_cast<uint32_t>(newHeight);

	WindowResizeEvent event(data.Width, data.Height);
	if (data.EventCallback)
		data.EventCallback(event);
});
```

1. **Line 230:** the window's data is stored as the user pointer.
2. **Line 232:** the lambda has no captures, so it converts to the function pointer the library wants.
3. **Line 234:** the user pointer comes back as a `void*`, and `static_cast` returns it to `WindowData`.
4. **Lines 239–240:** the stored `EventCallback` is a `std::function`, so the C callback hands over to C++.

A C library also takes its settings in a **configuration struct**: a plain :term[struct]{id=struct} that you complete and pass by pointer. The audio
engine makes the struct with a function that sets defaults, changes the fields it needs, and passes it on. The library
returns a **result code**, a number that names success or the kind of failure, and the caller compares it with the success value.
No exception flows out of C, and the engine does not throw, so every result code is checked.

```cpp src="Strata/src/Strata/Audio/AudioEngine.cpp#L85-L97"
ma_result InitializeEngine(AudioEngineData& data, ma_engine_config config, bool useDevice)
{
	ma_engine& engine = data.Engine;
	config.noDevice = useDevice ? MA_FALSE : MA_TRUE;
	config.onProcess = ApplyPendingWorldUp;
	config.pProcessUserData = &data;
	// Start the device only once the listener and volume are set. This also avoids ma_engine_init's
	// auto-start failure path, which does not uninitialize its internal resource manager.
	config.noAutoStart = MA_TRUE;

	ma_result result = ma_engine_init(&config, &engine);
	if (result != MA_SUCCESS)
		return result;
```

1. **Lines 89–90:** the callback and its user pointer, `&data`, go into the configuration.
2. **Line 95:** the library gets a pointer to the configuration and to the engine object, and returns a result code.
3. **Lines 96–97:** anything but `MA_SUCCESS` returns at once; the caller logs the reason and continues without audio output.

The callback of line 89, `ApplyPendingWorldUp`, starts with `static_cast<AudioEngineData*>(userData)`, the same two steps as in the toy
above.

## Type erasure hides many types behind one

An engine meets a problem that no loop can solve with plain templates. The editor must draw the properties of every component
from one list, without knowing which component each entry belongs to. **Type erasure** is hiding many concrete types behind
one type, so that code which handles the one type needs no knowledge of the many. You have met two forms: a `void*` that
forgot its type, and a `std::function` that forgot which function it holds.

To read a field of a class without writing its name in the code you need a way to name the field. A **pointer to a member** names a field of a
class, not a field of one object. Its type for a `float` field of `Coin` is `float Coin::*`, and `&Coin::Speed` makes one. To use it, pick an
object: `coin.*field` for an object, `pointer->*field` for a pointer.

```cpp sketch="basics-cpp-generic-members.cpp"
// A pointer to a member names a field of a class, not of one object: it works on any object of the class.
#include <iostream>

struct Coin
{
	float Speed = 2.0f;
	float Height = 0.5f;
};

float Read(const Coin& coin, float Coin::* field)
{
	return coin.*field;
}

int main()
{
	Coin slow;
	Coin fast;
	fast.Speed = 6.0f;
	float Coin::* field = &Coin::Speed;
	std::cout << "slow " << Read(slow, field) << ", fast " << Read(fast, field) << '\n';
	std::cout << "height " << Read(fast, &Coin::Height) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-members.cpp"
slow 2, fast 6
height 0.5
```

1. **Line 10:** `Read` takes any coin and any `float` field of the class.
2. **Line 20:** `&Coin::Speed` is the same pointer for `slow` and `fast`; `Read` gives 2 for one and 6 for the other.

Now combine the two ideas. The next sketch stores a function that reads a field of `Coin` and one that reads a field of `Light`
under one type, `std::function<float(const void*)>`. The lambda captures the member pointer, and inside it the `const void*`
returns to the class with `static_cast`.

```cpp sketch="basics-cpp-generic-erasure.cpp"
// Type erasure: one getter type for fields of different classes, built from a pointer to a member.
#include <functional>
#include <iostream>

struct Coin { float Speed = 2.0f; };
struct Light { float Intensity = 800.0f; };

template<typename T>
std::function<float(const void*)> MakeGetter(float T::* member)
{
	return [member](const void* object) { return static_cast<const T*>(object)->*member; };
}

int main()
{
	Coin coin;
	Light light;
	std::function<float(const void*)> getters[2] = { MakeGetter(&Coin::Speed), MakeGetter(&Light::Intensity) };
	std::cout << getters[0](&coin) << ' ' << getters[1](&light) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-generic-erasure.cpp"
2 800
```

1. **Lines 8–12:** one template makes a reading function for any class `T`; the member pointer is captured by value.
2. **Line 11:** the cast back to `const T*` is correct because the template knows `T` and the list does not.
3. **Line 18:** the array holds reading functions made for two unrelated classes, and each reads its own field.

The engine's property list is built exactly so. `Property` receives a pointer to a member and stores one function that reads it and one
that writes it, each a `std::function` over `const void*` or `void*`.

```cpp src="Strata/src/Strata/Reflection/PropertyBuilder.h#L46-L65"
// Fluent registration of reflected properties of type T into a property list. Derived (CRTP) is the concrete
// builder returned from each call, so builders can add their own methods (see ComponentInfoBuilder).
template<typename T, typename Derived>
class PropertyBuilderBase
{
public:
	explicit PropertyBuilderBase(std::vector<PropertyInfo>& properties)
		: m_Properties(properties)
	{
	}

	template<typename Member>
	Derived& Property(std::string name, Member T::* member, const PropertyOptions& options = {})
	{
		PropertyInfo& property = AddProperty();
		Detail::ApplyPropertyOptions(property, name, Detail::DeducePropertyType<Member>(options.Color), options);
		property.Getter = [member](const void* object) -> PropertyValue { return static_cast<const T*>(object)->*member; };
		property.Setter = [member](void* object, const PropertyValue& value) { static_cast<T*>(object)->*member = std::get<Member>(value); };
		return Self();
	}
```

1. **Lines 46–49:** `Derived` is the builder's own type, the subject of the next section.
2. **Line 58:** the member pointer is `Member T::* member`, and the compiler works out `Member` from the call.
3. **Lines 62–63:** the lambdas capture `member`, and cast the `const void*` and `void*` back to `T`.
4. **Line 64:** `Self()` returns the builder so that the next call can follow.

The script system does the same with a function pointer in place of a `std::function`. The macro `ST_SCRIPT_FIELD(Speed)`
expands, in short, to `Field<&ClassType::Speed>("Speed")` on the class's builder, with `ClassType` your script class: the member pointer as a template argument. `Field` stores two function pointers
made for that class and member. The first reads the field through a reference to the `Script` base:

```cpp src="StrataScriptCore/Include/StrataScript/Script.h#L160-L165"
template<typename T, auto Member>
void GetFieldValue(const Script& script, StrataScriptValue& outValue)
{
	using MemberType = typename MemberPointerTraits<decltype(Member)>::MemberType;
	outValue = ValueTraits<MemberType>::ToValue(static_cast<const T&>(script).*Member);
}
```

The script module knows `T`, so `static_cast<const T&>(script).*Member` is correct there, while the engine on the other side of the
C boundary sees only a record of names, types and functions.

## CRTP lets a base class return the derived type

A builder lets you chain calls: `builder.WithId(7).Gold()`. If `WithId` lives in a :term[base class]{id=base-class} and returns the base,
the chain loses the derived type, and `.Gold()` no longer exists on the result. **CRTP**, the curiously recurring template
pattern, fixes this: a :term[derived class]{id=derived-class} names itself as the argument of its own base class template, so the base knows the type that
derives from it.

```cpp sketch="basics-cpp-generic-crtp.cpp"
// CRTP: the base template returns the derived type, so calls chain without losing it.
#include <iostream>

template<typename Derived>
struct Builder
{
	int Id = 0;
	Derived& WithId(int id)
	{
		Id = id;
		return static_cast<Derived&>(*this);
	}
};
struct CoinBuilder : Builder<CoinBuilder>
{
	bool IsGold = false;
	CoinBuilder& Gold() { IsGold = true; return *this; }
};

int main()
{
	CoinBuilder builder;
	builder.WithId(7).Gold();
	std::cout << "id " << builder.Id << ", gold " << builder.IsGold << '\n';
}
```

```text output-of="basics-cpp-generic-crtp.cpp"
id 7, gold 1
```

1. **Lines 4–5:** the base takes the derived type as `Derived`.
2. **Lines 8–12:** `WithId` returns `Derived&`; the cast is safe because the object really is a `Derived`.
3. **Line 14:** the derived class passes itself to its base, `Builder<CoinBuilder>`, the recurring part of the name.

:::example[The property builder chains the same way]
The property builder is the same shape. `PropertyBuilderBase<T, Derived>` returns `Derived&` from every call, and
`ComponentInfoBuilder<T>` in `Strata/src/Strata/Reflection/ComponentRegistry.h` derives from `PropertyBuilderBase<T, ComponentInfoBuilder<T>>`,
so a chain of property calls may continue with the calls that the component builder adds.
:::

:::why[Why CRTP and not a virtual function]
A :term[virtual function]{id=virtual-function} returns the base type, because every override must return the same type as the base's declaration. CRTP makes
the base a different class for each derived class, so the return type is exact, and the compiler resolves every
call during the build, with no table lookup. The cost is that the base is a template, so it lives in a header, and an error message names the long
type.
:::

## Common mistakes

- **Using an iterator after the container changed.** Symptom: a crash or garbage after `push_back` or `erase` in a loop. Fix: take
  `begin()` again, use `it = v.erase(it)`, or keep an index.
- **`remove_if` without `erase`.** Symptom: the size does not change and the end holds leftovers. Fix: write
  `v.erase(std::remove_if(...), v.end())`.
- **A reference capture that outlives the variable.** Symptom: a callback prints garbage or crashes, but only sometimes. Fix:
  capture by value, or keep the lambda inside the function.
- **A `[this]` capture that outlives the object.** Symptom: the same, in a callback stored in a list. Fix: remove the
  callback when the object goes, or keep the data in a shared object.
- **Calling an empty `std::function`.** Symptom: a failure when a callback was never set. Fix: test it with `if (callback)`.
- **A wrong `static_cast` from `void*`.** Symptom: nonsense values with no error. Fix: cast to the type you stored.
- **A template body in a `.cpp` file.** Symptom: an error from the linker that a function is undefined. Fix: put the body in
  the header, because the compiler needs it where the call is.
- **`[]` on a map for a lookup.** Symptom: the map grows when you only read it. Fix: use `find` or `at`.

## Summary

- A C++ template is code with an open type or number, and the compiler writes one version for each use. A `static_assert` stops a wrong argument at build time, and a pack takes any number of arguments.
- The standard containers differ in what they cost to find, add and walk. An iterator is a position, and a push or an erase can make one invalid; `sort`, `find_if` and `remove_if` with `erase` work on ranges.
- A lambda writes a function where you use it. A capture by value keeps a copy; a capture by reference reads the variable and dangles when the variable dies.
- `std::function` keeps anything you can call and lets you store callbacks. The C form is a function pointer plus a `void*` user pointer, with settings in a struct and a result code back.
- Type erasure hides many types behind one, with `std::function` or `void*` and `static_cast`. Pointers to members name a field of a class, and CRTP lets a base class return the derived type.

## Check yourself

1. You must list the coins by name from A to Z and look each up by name. Which container? A: `std::vector`; B: `std::map`; C: `std::unordered_map`; D: `std::bitset`.

   :::answer{tests="containers"}
   B. A map keeps its keys sorted, so a walk lists names from A to Z, and a lookup takes about 10 steps for 1,000 names. A is searched step by step; C has no order; D holds on and off flags.
   :::

2. What does this print? `int n = 2; auto f = [n]() { return n * 3; }; n = 10; Log::Info(f());` A: 6; B: 30; C: 2; D: it does not build.

   :::answer{tests="lambdas"}
   A. The lambda copied `n` when it was made, so it multiplies 2 by 3. B is what `[&n]` would print. C and D do not follow from the code.
   :::

3. A loop holds `auto it = v.begin();` and then calls `v.push_back(1);`. Which statement is true? A: `it` is always valid; B: `it` may now point at freed memory; C: `push_back` changes `it` to the new `begin()`; D: `it` is valid for a `std::vector` and invalid for a `std::map`.

   :::answer{tests="containers"}
   B. If the vector had no room, it moved its values to a new block. C is wrong because an iterator never updates itself. D has it backward: inserting into a map keeps iterators valid.
   :::

4. A program calls `Largest(3, 2.5f)` on `template<typename T> T Largest(T a, T b)`. What happens? A: it returns 3; B: it builds and returns 3.0f; C: the build fails, because `T` would be `int` for one argument and `float` for the other; D: it returns 2.5.

   :::answer{tests="templates"}
   C. The compiler works out `T` from each argument and the two disagree. Write `Largest<float>(3, 2.5f)` to name `T` yourself.
   :::

5. A C library calls `void OnTick(void* userData)` every second. You want the function to increase a counter in your class. What do you pass as the user pointer? A: a `std::function`; B: `&counter`, and `OnTick` casts it back with `static_cast`; C: nothing, because a C function cannot reach any data; D: a lambda with captures.

   :::answer{tests="callbacks"}
   B. The user pointer is the way data crosses a C interface. A and D need C++ machinery that C does not know; C is wrong because the user pointer exists for this.
   :::

6. Why does `PropertyBuilderBase<T, Derived>` take `Derived` as a template argument? A: so each property is stored twice; B: so its methods can return the derived builder and chains keep working; C: so the builder can use virtual functions; D: so `T` can be erased.

   :::answer{tests="erasure"}
   B. Returning `Derived&` lets `.Property(...)` be followed by a call that only the derived builder has. The pattern needs no virtual function, and `T` is the type of the component, not erased.
   :::

## Practice

Run exercises 1 to 4 in `Playground`, the script of [Programming from zero I](../basics/programming-1.md#the-playground-is-a-script-of-your-own); stop the game before each build. Exercise 5
is optional and works in Coin Run.

If the **Console** still shows the lines of your earlier code, read the last line of the build: `(the module was up to date)` at its end means that it compiled nothing. A build compares the times of files, and a drive that keeps them in steps of two seconds can hide a change saved right after a build. Save the file again and press **Ctrl+B**.

1. **Basic.** Write a function template `Largest` that returns the larger of two values. Call it with two `int` values and with two
   `float` values and log both results.

   :::answer[Worked solution]{tests="templates" solution="sketches/basics-cpp-generic-largest.cpp"}
   In the script, put the template above the class and call it in `OnCreate` with `Log::Info`. The program below does the same in plain C++.

   ```cpp sketch="basics-cpp-generic-largest.cpp"
   // Practice 1: a function template Largest, called with int and with float.
   #include <iostream>

   template<typename T>
   T Largest(T a, T b)
   {
   	return a > b ? a : b;
   }

   int main()
   {
   	std::cout << "Largest(3, 7) = " << Largest(3, 7) << '\n';
   	std::cout << "Largest(2.5f, 1.5f) = " << Largest(2.5f, 1.5f) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-generic-largest.cpp"
   Largest(3, 7) = 7
   Largest(2.5f, 1.5f) = 2.5
   ```

   1. **Line 7:** `a > b ? a : b` gives `a` when the test is true and `b` when it is false.
   2. **Lines 12–13:** one call with `int` values and one with `float` values; the compiler writes two versions.
   :::

2. **Medium.** A vector holds 4, 9, 1, 7, 3. Sort it from the highest with a lambda, then remove every value below 4 with
   `remove_if` and `erase`. Predict what remains, then run it.

   :::answer[Worked solution]{tests="containers lambdas" solution="sketches/basics-cpp-generic-sortremove.cpp"}
   Sorted, the vector reads 9, 7, 4, 3, 1. `remove_if` keeps 9, 7 and 4, and `erase` drops the two leftovers.

   ```cpp sketch="basics-cpp-generic-sortremove.cpp"
   // Practice 2: sort with a lambda, then remove with remove_if and erase.
   #include <algorithm>
   #include <iostream>
   #include <vector>

   int main()
   {
   	std::vector<int> v = { 4, 9, 1, 7, 3 };
   	std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
   	v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x < 4; }), v.end());
   	for (int value : v)
   		std::cout << value << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-generic-sortremove.cpp"
   9
   7
   4
   ```

   1. **Line 9:** the first lambda says which of two values goes first.
   2. **Line 10:** the second lambda says which values to remove, and `erase` cuts off what `remove_if` left at the end.
   :::

3. **Medium.** Predict, then run: a counter starts at 1. One lambda captures it by value and one by reference, and both return the counter times 10. The counter is set to 3, and then both lambdas are called. What do they return?

   :::answer[Worked solution]{tests="lambdas" solution="sketches/basics-cpp-generic-captures.cpp"}
   The first returns 10, because it copied 1; the second returns 30, because it reads the variable, which is 3 by then.

   ```cpp sketch="basics-cpp-generic-captures.cpp"
   // Practice 3: a counter captured by value and by reference, read after the counter changes.
   #include <iostream>

   int main()
   {
   	int counter = 1;
   	auto byValue = [counter]() { return counter * 10; };
   	auto byReference = [&counter]() { return counter * 10; };
   	counter = 3;
   	std::cout << "by value: " << byValue() << '\n';
   	std::cout << "by reference: " << byReference() << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-generic-captures.cpp"
   by value: 10
   by reference: 30
   ```

   1. **Lines 7–8:** the first lambda copies the counter and the second keeps a reference to it.
   2. **Line 9:** the change reaches only the lambda that holds the reference.
   :::

4. **Hard.** Store three callbacks in a `std::vector` of `std::function<void()>` and call them in order. Keep the position of the second one while you add the third, and explain why an iterator
   kept across the `push_back` must not be used.

   :::answer[Worked solution]{tests="callbacks containers" solution="sketches/basics-cpp-generic-stored.cpp"}
   An index counts from the start, so growth cannot break it. The iterator would point into the block the vector freed when it moved to larger memory.

   ```cpp sketch="basics-cpp-generic-stored.cpp"
   // Practice 4: stored callbacks run in order; a position kept as an index survives the vector growing.
   #include <functional>
   #include <iostream>
   #include <vector>

   int main()
   {
   	std::vector<std::function<void()>> callbacks;
   	callbacks.push_back([]() { std::cout << "first\n"; });
   	callbacks.push_back([]() { std::cout << "second\n"; });
   	size_t next = 1; // an iterator such as callbacks.begin() + 1 would be invalid after the next push_back
   	callbacks.push_back([]() { std::cout << "third\n"; });
   	for (const auto& callback : callbacks)
   		callback();
   	callbacks[next]();
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-generic-stored.cpp"
   first
   second
   third
   second
   ```

   1. **Line 11:** the position is kept as an index.
   2. **Line 12:** this `push_back` may move every callback to a new block; an iterator taken at line 11 would then be invalid.
   3. **Line 15:** the index still names the second callback.
   :::

5. **Hard.** Optional, on Coin Run: your Coin Run from [Coin Run](../make/project-coin-run.md), or Checkpoint 4 at the end of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), opened with **File ▸ Open Project...**. Its coins carry the tag `Coin` and appear once play starts, and the ball is the entity `Ball`. In a new script on the ball, sort the coins that are left by
   their distance to the ball with `std::sort` and a lambda, and call a stored callback when the last coin is taken.

   :::answer[Worked solution]{tests="lambdas callbacks" solution="sketches/basics-cpp-generic-coinrun.cpp"}
   The sketch keeps the logic in plain C++ with coin positions in a struct. In the script, the lambda captures the ball's position by value and compares the distances of two coins.

   ```cpp sketch="basics-cpp-generic-coinrun.cpp"
   // Practice 5: coins sorted by their distance to the ball, and a stored callback when the last coin is taken.
   #include <algorithm>
   #include <cmath>
   #include <functional>
   #include <iostream>
   #include <vector>

   struct Coin { float X; float Z; };

   int main()
   {
   	std::vector<Coin> coins = { { 3.0f, 4.0f }, { 1.0f, 0.0f }, { 0.0f, 2.0f } };
   	std::function<void()> onAllTaken = []() { std::cout << "all coins taken\n"; };
   	std::sort(coins.begin(), coins.end(), [](const Coin& a, const Coin& b)
   	{
   		return std::hypot(a.X, a.Z) < std::hypot(b.X, b.Z);
   	});
   	std::cout << "nearest: " << coins.front().X << ", " << coins.front().Z << '\n';
   	while (!coins.empty())
   	{
   		coins.erase(coins.begin());
   		if (coins.empty() && onAllTaken)
   			onAllTaken();
   	}
   }
   ```

   ```text output-of="basics-cpp-generic-coinrun.cpp"
   nearest: 1, 0
   all coins taken
   ```

   1. **Lines 14–17:** the lambda orders two coins by their distance to the ball, which this sketch puts at the origin.
   2. **Lines 21–23:** the stored callback runs only when the last coin has gone.

   In the script the list is `std::vector<Entity> coins = Scene::FindEntitiesByTag("Coin");`, taken again after each coin
   goes, and the comparison reads `a.GetTransform().GetWorldPosition()`. The stored callback is a `std::function<void()>` member that the code calls when the list is empty.
   :::

## Where the book uses it

- [Modern C++](../basics/cpp-modern.md) builds on templates and lambdas to teach moving values, `if constexpr` and `std::variant`.
- [Threads](../basics/threads.md) starts each thread from a lambda and hands it values by capture.
- [Inside the ABI and the SDK](../scripting/abi-sdk.md) reads `ST_SCRIPT_FIELD`, the member pointer as a template argument, and the function pointers of the script interface.
- [Entities and components, with EnTT inside](../world/ecs.md) reads calls such as `GetComponent<T>`, which take the component type as a template argument.

## Further reading

- [cppreference: templates](https://en.cppreference.com/w/cpp/language/templates): the rules of function and class templates and their arguments; intermediate.
- [cppreference: containers library](https://en.cppreference.com/w/cpp/container): every container with the cost of each operation; intermediate.
- [cppreference: lambda expressions](https://en.cppreference.com/w/cpp/language/lambda): the full capture rules; intermediate.
- [cppreference: `std::function`](https://en.cppreference.com/w/cpp/utility/functional/function): what it holds and when it allocates; intermediate.
- Learn C++ (learncpp.com), chapters 11, 16, 18, 20 and 26: function templates, `std::vector`, iterators and algorithms, function pointers and lambdas, class templates; beginner.
