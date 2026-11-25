---
id: basics/cpp-modern
title: "Modern C++ as Strata uses it: move semantics, constexpr, optional, variant, span and concepts"
description: "Learn the C++ features Strata's code uses beyond the basics: moves, forwarding, optional, variant, views, scoped enumerations, constexpr, concepts and macros."
kind: primer
size: L
tracks: [B, E]
needs: [basics/cpp-generic]
time: 105
learn:
  - id: move-semantics
    text: explain the difference between a copy and a move, and predict what an object moved from holds
  - id: optional-variant
    text: choose between std::optional and std::variant for a value that may be missing or of several types, and write the code that reads it
  - id: views
    text: name what a string view and a span point to, and predict when they point to something that is gone
  - id: enum-constexpr
    text: write a scoped enumeration with a fixed type and flag operators, and a constexpr value checked by static_assert
  - id: compile-time
    text: "predict what a macro with arguments, an #if block and a type trait decide before the program runs"
status: final
---

::::test-out

1. What does the third line write, and what may you rely on about `a` after the second line?

   ```cpp pseudocode
   std::vector<int> a = { 1, 2, 3 };
   std::vector<int> b = std::move(a);
   Log::Info("b has ", b.size(), " numbers");
   ```

   Look at what `std::move` does to `a` before `b` is built.

   :::answer{tests="move-semantics"}
   The line writes `b has 3 numbers`. The vector `a` is still valid, but the standard does not say what it holds. You may
   assign to it or destroy it, and you must not rely on its contents. In practice it is empty.
   :::

2. The variable `lives` is a `std::optional<int>` that holds nothing. What does `Log::Info(lives.value_or(3));` write?

   :::answer{tests="optional-variant"}
   The line writes 3. `value_or` returns the held number, or its argument when the optional is empty.
   :::

3. Why is this function wrong?

   ```cpp pseudocode
   std::string_view GetName()
   {
   	std::string text = "gold";
   	return text;
   }
   ```

   Ask who owns the letters after the function returns.

   :::answer{tests="views"}
   A string view does not own letters: it points to them. The string `text` dies at the closing brace, so the view
   points to memory that is gone.
   :::

4. Write one line that declares a scoped enumeration `Mode` with the values `Menu` and `Play`, stored in one byte.

   :::answer{tests="enum-constexpr"}
   `enum class Mode : uint8_t { Menu, Play };`. The `: uint8_t` after the name fixes the size to one byte.
   :::

5. With `#define DOUBLE(x) x * 2`, what number does `int n = DOUBLE(3 + 1);` give?

   :::answer{tests="compile-time"}
   The line gives 5. The preprocessor pastes text, so the line becomes `3 + 1 * 2`, and the multiplication comes first.
   :::

::::

## Why you will need this

The C++ you meet in Strata's headers is not the C++ of a first course. It moves objects instead of copying them, returns
`std::optional` when an answer may be missing, and checks sizes while it compiles. You need these features to read the engine
at all.

This page teaches them in the measure the engine uses them, each on a small program you can run. [Conventions](../core/conventions.md)
reads the engine's rules on errors with `std::optional` and exceptions. [Files and paths](../core/files.md) uses
`std::filesystem::path` and views. [Reflection](../world/reflection.md) reads a property's `std::variant`. At the end, you
write the functions of a coin game as the optional last exercise.

This page needs no download. Only the Practice needs a project: the one that holds your `Playground` script, which [Programming from zero I](programming-1.md#the-playground-is-a-script-of-your-own) puts on an empty entity, and Coin Run for the optional last exercise, which names a download.

Each sketch is a whole program: save it as `sketch.cpp` and compile it with C++20 in the terminal of [How a C++ program is built](build.md#open-a-terminal-that-finds-a-compiler), the next page. On Windows, run `cl /std:c++20 /EHsc sketch.cpp` and then `.\sketch.exe`. On Linux and macOS, run `c++ -std=c++20 sketch.cpp -o sketch` and then `./sketch`. Without a compiler, read each output and its notes.

## Moving an object hands over its contents

A function builds a list of 1,000 :term[floating-point numbers]{id=floating-point-number} and returns it. If returning meant copying, the engine would
allocate a second block of 4,000 :term[bytes]{id=byte}, copy every number into it and free the first block. Nobody needs the first block
after the return, so the copy is wasted work.

A `std::vector` is small itself: usually three pointers, 24 bytes in all, that lead to a block of memory the vector owns.
Copying the vector makes a new block and copies each number. Moving it gives the three pointers to the new vector and
sets the old ones to null, and the 4,000 bytes stay where they are.

**Move semantics** are the C++ rules that let an object hand its contents to another object, instead of copying them,
when the source is no longer needed. The compiler knows a source is no longer needed when it is a temporary, such as the
result of a :term[function call]{id=function-call} that nobody named. For a variable with a name, you say so with `std::move(x)`.

Despite its name, `std::move` moves nothing. It labels `x` as "you may empty this one", by turning it into an `rvalue`
reference. Such a reference is written `T&&` in a type, and it binds only to temporaries and to values labelled by
`std::move`. The move happens in the type's move :term[constructor]{id=constructor}, `Type(Type&&)`, which takes the contents and leaves the
source empty.

The next program copies a string of 40 letters and then moves it.

```cpp sketch="basics-cpp-modern-move.cpp"
// A copy keeps the source; a move takes its contents and leaves the source valid but empty in practice.
#include <iostream>
#include <string>
#include <utility>

int main()
{
	std::string original(40, 'a');
	std::string copy = original;
	std::string moved = std::move(original);
	std::cout << "copy " << copy.size() << ", moved " << moved.size() << '\n';
	std::cout << "original after the move: " << original.size() << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-move.cpp"
copy 40, moved 40
original after the move: 0
```

1. **Line 10:** `std::move(original)` is the only difference from line 9, and it changes the cost: a copy of 40 letters or the
   passing on of one pointer.

After the move, `original` holds nothing in this compiler, but the standard promises less: the object moved from is
valid, and the standard does not say what it holds. You may destroy it or assign a new value to it. Reading its value is a mistake, even
when it works today.

:::example[What a return costs]
A function returns a `std::vector<float>` of 1,000 numbers. A float takes 4 bytes, so the block is 4,000 bytes.

A copy allocates 4,000 bytes and copies all of them. A move copies the three pointers, 24 bytes, and the new vector owns
the old block. A :term[local variable]{id=local-variable} that a function returns is moved for you, and often the compiler skips even that move, so
writing `return std::move(local);` blocks the saving and is a mistake.
:::

Try it: A `double` takes 8 bytes. How many bytes does a copy of a vector of 250 of them copy, and a move?

:::answer
A copy copies 250 × 8 = 2,000 bytes into a new block. A move copies only the three pointers, 24 bytes, whatever the
length.
:::

Some types can only move. A `std::unique_ptr` has one owner, so copying it would make two owners and the type forbids it:
you hand it over with `std::move`. A `std::thread` is the same, because one thread has one handle. Strata uses moves where
it passes a job along: `Application::SubmitToMainThread` in `Strata/src/Strata/Core/Application.cpp` moves the function it
receives into the queue, and `BinaryWriter::TakeData` hands out its whole byte buffer with `std::move(m_Data)`.

## Forwarding passes an argument on as it came

`CreateScope<T>(args...)` builds a `T` from arguments the caller chooses. It must pass each argument on exactly as it
came: a named object copied, a temporary moved. A plain function cannot do that, because inside it every parameter has
a name and counts as a named object.

A parameter written `Args&&... args` in a template is a **forwarding reference**: it binds to both kinds and remembers
which one it got. The `...` makes `Args` a list of any number of types, one per argument, and `args...` stands for all
the arguments in turn. `std::forward<Args>(args)...` then gives each argument back as a temporary if the caller passed one
and as a named object otherwise. Passing arguments on this way is called perfect forwarding. Strata's `CreateScope`
and `CreateRef` do it.

```cpp src="Strata/src/Strata/Core/Base.h#L45-L49"
template<typename T, typename... Args>
constexpr Scope<T> CreateScope(Args&&... args)
{
	return std::make_unique<T>(std::forward<Args>(args)...);
}
```

The program below builds a `Tracer`, which says how it was made, through a forwarding function and through a naive one.

```cpp sketch="basics-cpp-modern-forward.cpp"
// Forwarding keeps an argument's kind: a named object is copied, a moved one is moved.
#include <iostream>
#include <utility>

struct Tracer
{
	Tracer() = default;
	Tracer(const Tracer&) { std::cout << "copied\n"; }
	Tracer(Tracer&&) noexcept { std::cout << "moved\n"; }
};

template<typename... Args>
void Forwarding(Args&&... args) { Tracer item(std::forward<Args>(args)...); }

template<typename... Args>
void Naive(Args&&... args) { Tracer item(args...); }

int main()
{
	Tracer tracer;
	std::cout << "forwarding a named object: "; Forwarding(tracer);
	std::cout << "forwarding a moved object: "; Forwarding(std::move(tracer));
	std::cout << "naive, a moved object: "; Naive(std::move(tracer));
}
```

```text output-of="basics-cpp-modern-forward.cpp"
forwarding a named object: copied
forwarding a moved object: moved
naive, a moved object: copied
```

1. **Line 13:** `std::forward<Args>(args)...` keeps the caller's kind of argument, so a moved object arrives moved.
2. **Line 16:** `args...` names the arguments, so each one counts as named and is copied even though the caller moved it.

Strata also forwards in `ST_BIND_EVENT_FN` in `Base.h`, which makes a :term[function object]{id=function-object} from `auto&&... args` and
`std::forward<decltype(args)>(args)...`; a later page covers events.

## An optional holds a value or nothing

A function that reads the option `--width` from the command line has two kinds of answer: a number, or "the option is
absent". Returning -1 for absent fails when -1 is a valid answer. A `std::optional<T>` holds either a `T` or nothing, and
its type says so, so the caller cannot forget the second case.

```cpp src="Strata/src/Strata/Core/CommandLine.cpp#L54-L62"
const std::optional<std::string> text = GetOption(name);
if (!text)
	return std::nullopt;

int64_t value = 0;
const auto [end, error] = std::from_chars(text->data(), text->data() + text->size(), value);
if (error != std::errc() || end != text->data() + text->size())
	return std::nullopt;
return value;
```

`CommandLine::GetIntOption` shows the whole kit. `return std::nullopt;` returns the empty optional. `!text` is true when
the optional is empty. `text->data()` reaches a member of the held string with `->`, and `*text` would be the held string
itself.

The last line, `return value;`, turns a plain number into an optional that holds it. Line 59 holds a structured binding,
which a later section explains.

Reading an empty optional is the mistake to avoid. `*` and `->` do not check: on an empty optional they are :term[undefined
behavior]{id=undefined-behavior}. `value()` checks and throws a `std::bad_optional_access`, which the exceptions section shows. `value_or(x)`
returns the held value or `x`. The safe habit is to test first, as `GetIntOption` does with `!text`, or to supply a
fallback with `value_or`.

```cpp sketch="basics-cpp-modern-optional.cpp"
// A function that may have no answer returns std::optional; the caller checks it before use.
#include <iostream>
#include <optional>
#include <string>

std::optional<int> FindIndex(const std::string& text, char letter)
{
	const size_t position = text.find(letter);
	if (position == std::string::npos)
		return std::nullopt;
	return static_cast<int>(position);
}

int main()
{
	const std::optional<int> found = FindIndex("strata", 'a');
	const std::optional<int> missing = FindIndex("strata", 'z');
	if (found)
		std::cout << "found at " << *found << '\n';
	std::cout << "missing has a value: " << missing.has_value() << ", value_or(-1): " << missing.value_or(-1) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-optional.cpp"
found at 3
missing has a value: 0, value_or(-1): -1
```

1. **Line 10:** the search failed, so the function returns `std::nullopt`, "no answer".
2. **Line 19:** `*found` is read only inside the `if (found)` test that proves a value is there.
3. **Line 20:** `value_or(-1)` gives the fallback for the empty optional, so no check is needed.

Return an optional when absence is a normal result and needs no explanation: a search, a lookup, a reading of text. When the caller
needs to know why it failed, return a result :term[struct]{id=struct} with a message. When the absence is a mistake in the program, assert
instead. [Conventions](../core/conventions.md) gives Strata's rules for the three. An optional stores its value inside
itself, with a flag, so it costs no :term[heap allocation]{id=dynamic-allocation}.

## A variant holds one of several types

An inspector shows properties whose values are :term[booleans]{id=boolean}, whole numbers, vectors, text and more. A list of them needs one
type that can hold any of those. A **variant**, `std::variant<A, B, C>`, holds exactly one of its alternatives at a time
and remembers which: `index()` is the number of the alternative held, counted from 0. Strata's `PropertyValue` in
`Strata/src/Strata/Reflection/Property.h` is a variant of ten types, among them `bool`, `float`, `glm::vec3` and `std::string`.

To read a variant you ask for the alternative you expect: `std::get_if<float>(&value)` returns a pointer, null when the
variant holds something else, and `std::get<float>(value)` throws then. To handle every alternative, call `std::visit(f, value)`. That call runs `f` with whatever the variant holds, so `f` must accept every alternative. A generic :term[lambda]{id=lambda} with a
`const auto&` parameter does.

```cpp src="Strata/src/Strata/Reflection/Property.cpp#L176-L184"
std::visit([&](const auto& vector)
{
	using VectorType = std::decay_t<decltype(vector)>;
	if constexpr (std::is_same_v<VectorType, glm::vec2> || std::is_same_v<VectorType, glm::vec3> || std::is_same_v<VectorType, glm::vec4>)
	{
		for (glm::length_t index = 0; index < VectorType::length() && inside; index++)
			inside = check(vector[index]) || outside(describe(vector[index]));
	}
}, value);
```

Inside the lambda, `std::decay_t<decltype(vector)>` is the held type without `const` and `&`, here named `VectorType`. The `if constexpr` keeps the loop only for the three vector types. For a `bool` or a `std::string` the loop is not compiled at all,
which is the point: `vector[index]` would be an error for them. The `if constexpr` section explains why.

```cpp sketch="basics-cpp-modern-variant.cpp"
// A variant holds one of its types; std::visit calls the lambda with whichever it holds.
#include <iostream>
#include <string>
#include <variant>
using Value = std::variant<int, float, std::string>;
std::string Describe(const Value& value)
{
	return std::visit([](const auto& item) -> std::string
	{
		using T = std::decay_t<decltype(item)>;
		if constexpr (std::is_same_v<T, int>)
			return "int " + std::to_string(item);
		else if constexpr (std::is_same_v<T, float>)
			return "float " + std::to_string(item);
		else
			return "text " + item;
	}, value);
}
int main()
{
	const Value values[] = { 7, 2.5f, std::string("gold") };
	for (const Value& value : values)
		std::cout << value.index() << ": " << Describe(value) << '\n';
}
```

```text output-of="basics-cpp-modern-variant.cpp"
0: int 7
1: float 2.500000
2: text gold
```

1. **Line 8:** `std::visit` calls the lambda once, with the alternative the variant holds.
2. **Lines 10–16:** one branch per type; `if constexpr` compiles only the branch that matches, and the `else` takes the string.

[Reflection](../world/reflection.md) shows how Strata uses its `PropertyValue` for the inspector and the files.

## A view points into someone else's data

A function that prints a name takes `const std::string&`. Calling it with the text `"gold"` first builds a `std::string`:
a copy of four letters into a new block. A **string view**, `std::string_view`, is a pointer to letters and a length, so
it accepts a literal, a `std::string` or a part of one without copying.

A **span**, `std::span<T>`, is the same for any
run of values: a pointer and a count. `std::span<const T>` reads the values and cannot change them.

Many of Strata's functions that only read text or bytes take views. `BinaryReader::ReadView` in
`Strata/src/Strata/Core/BinaryStream.h` returns a `std::span<const uint8_t>` of the next bytes, with no copy, and
`CommandLine::GetIntOption` takes a `std::string_view`. A view is only a pointer and a length, so you pass it by value.

A view owns nothing, so it is only as good as the data it points to. It dangles when that data is gone: a view of a local
string returned from a function, a view of a temporary string, a span of a vector that then grows and moves its block.

```cpp pseudocode
std::string_view view = std::string("gold"); // the temporary dies at the semicolon
std::span<int> all(numbers);
numbers.push_back(1);                        // may move the block: all points to the old one
```

In the first line the string dies before the view is used, and in the last two the block moves before the span is used. Both point to memory
that is gone, and neither line shows an error when it is compiled.

:::example[When a vector grows under a span]
A vector holds 4 numbers in a block with room for exactly 4, and a span `all` holds the address of that block and the count 4.
The call `push_back(1)` needs room for a fifth number, so the vector allocates a block for more, copies the 4 numbers
across and frees the old block.

The span `all` still holds the address of the freed block. Reading through it is undefined behavior, and it may even
appear to work for a while.
:::

Try it: how do you keep a span safe while a vector grows?

:::answer
Make the span after the last change to the vector, or call `reserve` first so that the block does not move. A span made
after the `push_back` points to the new block.
:::

Two more facts. Older C functions find the end of text by a zero byte after the last letter, and a view of part of a
string has no zero there. So never pass a view's `data()` to a function that expects such text.
A script function that receives a view and must keep the text copies it into a `std::string` first.

A span walks backwards with reverse :term[iterators]{id=iterator}: `rbegin()` starts at the last value, `rend()` is the end, and `++` moves
toward the front. Strata walks lists from the newest entry this way, as `AssetManager.cpp` does over `m_ContentChanges`.

```cpp sketch="basics-cpp-modern-span.cpp"
// A span views a run of numbers it does not own; the last numbers are reached with the reverse iterators.
#include <iostream>
#include <span>
#include <vector>

void PrintBackwards(std::span<const int> values)
{
	for (auto it = values.rbegin(); it != values.rend(); ++it)
		std::cout << *it << ' ';
	std::cout << '\n';
}

int main()
{
	const std::vector<int> scores = { 10, 20, 30, 40, 50 };
	PrintBackwards(scores);
	PrintBackwards(std::span<const int>(scores).first(3));
	std::cout << "size " << std::span<const int>(scores).size() << ", bytes " << std::span<const int>(scores).size_bytes() << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-span.cpp"
50 40 30 20 10 
30 20 10 
size 5, bytes 20
```

1. **Line 8:** the loop walks from the last value to the first; `++it` goes backwards.
2. **Line 17:** `first(3)` makes a smaller view of the same numbers, still without a copy.

## A scoped enumeration has a type and a name

A plain `enum` pours its names into the surrounding scope and turns into an `int` without a word, so `Red` and a
number mix by accident. You met the safer form in [Programming 1](../basics/programming-1.md): `enum class` keeps its
names inside, as `Access::Read`. It also lets you fix the underlying type, as in `enum class Access : uint8_t`, which
makes the size one byte and the range 0 to 255.

A :term[scoped enumeration]{id=scoped-enumeration} never converts silently. `static_cast<int>(Access::Write)` gives the number, and
`static_cast<Access>(2)` gives the enumeration back. The second cast checks nothing: it accepts 200 although no name has
that value. A number read from a file must be checked before you cast it.

Flags need more. Each flag is one bit, made by `ST_BIT(n)`, which is `1u << n`, and a set of flags is several bits
together. Scoped enumerations have no `|` or `&`, so Strata defines them with one macro in `Base.h`.

```cpp src="Strata/src/Strata/Core/Base.h#L30-L37"
// Bitwise operators for an `enum class` used as a set of flags.
#define ST_DEFINE_ENUM_FLAG_OPERATORS(EnumType) \
	constexpr EnumType operator|(EnumType a, EnumType b) { return static_cast<EnumType>(static_cast<std::underlying_type_t<EnumType>>(a) | static_cast<std::underlying_type_t<EnumType>>(b)); } \
	constexpr EnumType operator&(EnumType a, EnumType b) { return static_cast<EnumType>(static_cast<std::underlying_type_t<EnumType>>(a) & static_cast<std::underlying_type_t<EnumType>>(b)); } \
	constexpr EnumType operator~(EnumType a) { return static_cast<EnumType>(~static_cast<std::underlying_type_t<EnumType>>(a)); } \
	constexpr EnumType& operator|=(EnumType& a, EnumType b) { return a = a | b; } \
	constexpr EnumType& operator&=(EnumType& a, EnumType b) { return a = a & b; } \
	constexpr bool HasFlag(EnumType value, EnumType flag) { return (value & flag) == flag; }
```

`ST_DEFINE_ENUM_FLAG_OPERATORS(EnumType)` writes `|`, `&`, `~`, `|=`, `&=` and `HasFlag` for the type it is given. Each
casts to the underlying type, works there and casts back. A macro does this because the same text is needed for every
flag type.

```cpp src="Strata/src/Strata/Reflection/ComponentRegistry.h#L24-L33"
enum class ComponentFlags : uint32_t
{
	None = 0,
	Hidden = ST_BIT(0),       // Internal: not shown in the inspector or add-component menus
	NotRemovable = ST_BIT(1), // Present on every entity (e.g. Transform)
	NoCopy = ST_BIT(2),       // Not copied when entering play mode
	NoSerialize = ST_BIT(3),  // Not written as a component (the scene serializer stores it itself, e.g. ID, parent)
	EngineAdded = ST_BIT(4)   // Added only by the engine (e.g. prefab links): visible and removable, never added by users or tools
};
ST_DEFINE_ENUM_FLAG_OPERATORS(ComponentFlags)
```

1. **Line 24:** `: uint32_t` fixes the type, so the flags fit in 32 bits.
2. **Lines 27–31:** each name is one bit, made by `ST_BIT`.
3. **Line 33:** this one line gives `ComponentFlags` all its operators.

:::example[Two flags in one number]
`ComponentFlags::Hidden | ComponentFlags::NoCopy` is `ST_BIT(0) | ST_BIT(2)`, which is 1 | 4. In binary that is 001 and
100, and the `|` gives 101, the number 5.

`HasFlag(value, NoCopy)` computes `(5 & 4) == 4`. 5 & 4 is 4, so the answer is true. `HasFlag(value, NotRemovable)`
computes `(5 & 2) == 2`. 5 & 2 is 0, so the answer is false.
:::

Try it: What number is `ComponentFlags::NotRemovable | ComponentFlags::EngineAdded`?

:::answer
`NotRemovable` is `ST_BIT(1)`, 2, and `EngineAdded` is `ST_BIT(4)`, 16. Together they are 18.
:::

The next program does the same with its own type.

```cpp sketch="basics-cpp-modern-flags.cpp"
// A scoped enumeration with a fixed type, cast to a number and back, and used as a set of flags.
#include <cstdint>
#include <iostream>

enum class Access : uint8_t
{
	None = 0,
	Read = 1u << 0,
	Write = 1u << 1,
	Execute = 1u << 2
};

constexpr Access operator|(Access a, Access b) { return static_cast<Access>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b)); }
constexpr Access operator&(Access a, Access b) { return static_cast<Access>(static_cast<uint8_t>(a) & static_cast<uint8_t>(b)); }
constexpr bool HasFlag(Access value, Access flag) { return (value & flag) == flag; }

int main()
{
	const Access mine = Access::Read | Access::Execute;
	std::cout << "number " << static_cast<int>(mine) << ", size " << sizeof(Access) << '\n';
	std::cout << "read " << HasFlag(mine, Access::Read) << ", write " << HasFlag(mine, Access::Write) << '\n';
	std::cout << "from number 2: " << (static_cast<Access>(2) == Access::Write) << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-flags.cpp"
number 5, size 1
read 1, write 0
from number 2: 1
```

1. **Line 5:** `: uint8_t` makes the enumeration one byte, which `sizeof` confirms.
2. **Line 13:** the operator is `constexpr`, so the compiler may use it at :term[compile time]{id=compile-time}.
3. **Line 22:** a cast turns the number 2 into `Access::Write`, and nothing checks that 2 is a valid value.

## constexpr computes before the program runs

Some values are known before the program starts: the size of an array, a limit, the size of a struct. If the compiler
computes them, they cost nothing at run time, and a wrong one stops the build. The word **constexpr** marks a variable or
function whose value the compiler can compute while compiling. A `constexpr` variable can be used where a constant is
required: an array size, a :term[template argument]{id=template-argument}.

Strata names such constants with a `c_` prefix, as `Application::c_InterruptedExitCode` (130) and
`BackgroundLogSink::c_MaxQueuedMessages` (65536). A `constexpr` function runs at compile time when all its arguments are
constants, and as an ordinary function when they are not.

`static_assert(condition)` checks a `constexpr` condition while compiling and fails the build when it is false. Strata
uses it to pin the size of a struct.

```cpp src="Strata/src/Strata/Core/RadixSort.h#L10-L16"
struct SortItem
{
	uint64_t Key = 0;
	uint32_t Value = 0;
	uint32_t Padding = 0;
};
static_assert(sizeof(SortItem) == 16);
```

The check on the last line pins the size of `SortItem` to 16 bytes: 8 for the key, 4 for the value and 4 for the padding
that the struct spells out. If someone adds a field, the build fails at this line instead of the sort breaking at run time.

`if constexpr (condition)` picks a branch while compiling, and the other branch is dropped, so it need not compile for
this type. Strata's component storage uses it for tag components, structs with no data, whose test is
`std::is_empty_v<T>`: a tag stores nothing, and a value is stored for every other type.

```cpp sketch="basics-cpp-modern-constexpr.cpp"
// A constexpr function runs at compile time when its arguments are known; if constexpr drops the branch not taken.
#include <iostream>
#include <type_traits>

constexpr int Factorial(int n) { return n <= 1 ? 1 : n * Factorial(n - 1); }
static_assert(Factorial(5) == 120);
struct Tag {};
struct Health { int Points = 100; };

template<typename T>
int SizeOfValue()
{
	if constexpr (std::is_empty_v<T>)
		return 0;
	else
		return static_cast<int>(sizeof(T));
}

int main()
{
	constexpr int c_Slots = Factorial(4);
	int values[c_Slots] = {};
	std::cout << "slots " << c_Slots << ", array " << sizeof(values) / sizeof(values[0]) << '\n';
	std::cout << "tag " << SizeOfValue<Tag>() << ", health " << SizeOfValue<Health>() << '\n';
}
```

```text output-of="basics-cpp-modern-constexpr.cpp"
slots 24, array 24
tag 0, health 4
```

1. **Lines 5–6:** `Factorial` runs in the compiler, and `static_assert` proves 5! is 120 before the program exists.
2. **Lines 13–16:** a tag takes the first branch and returns 0; `Health` takes the second and returns 4, the size of its `int`.
3. **Line 21:** `Factorial(4)` is 24, a constant, so it may size the array.

## `auto`, `decltype` and type traits ask about types

`auto` makes the compiler work out a variable's type from its first value.

The line `const auto [end, error] = std::from_chars(...)` holds a **structured binding**: it splits a returned pair or
struct into named variables, here the position where the reading stopped and its error code. Strata uses it for numbers
read from text in `CommandLine.cpp`. `decltype(x)` is the declared type of `x`; it appears in the lambda above as
`decltype(vector)`.

A **type trait** is a template in `<type_traits>` that answers a question about a type while compiling. Names ending in
`_v` give a value, and names ending in `_t` give a type.

- `std::is_same_v<A, B>` is true when `A` and `B` are the same type.
- `std::is_base_of_v<Base, Derived>` is true when `Derived` inherits from `Base`. Strata's scene systems check this in a
  `static_assert` in `SceneSystem.h`.
- `std::is_trivially_copyable_v<T>` is true when copying the bytes of a `T` copies the `T`. `BinaryWriter::Write` asserts it.
- `std::underlying_type_t<E>` is the :term[integer]{id=integer} type under an enumeration, as `ST_DEFINE_ENUM_FLAG_OPERATORS` uses it.

## Concepts name what a template needs

A template accepts any type, and a wrong one fails deep inside it, with a long error. `BinaryWriter::Write` guards itself
with a `static_assert` that carries a sentence. A **C++ concept** is a named condition on template parameters, checked
at the call, so the error names the broken condition.

A **requires clause** attaches a condition to one template, with no name for it.

```cpp pseudocode
template<typename T>
concept RawBytes = std::is_trivially_copyable_v<T>;

template<RawBytes T>
void Write(const T& value);          // the concept stands where typename stood

template<typename T>
	requires std::is_trivially_copyable_v<T>
void WriteAgain(const T& value);     // a requires clause, with the condition written out
```

Strata's sources define no concept and write no requires clause. Its templates check their types with
`static_assert` and the traits above. You still meet concepts in the :term[standard library]{id=standard-library}, in `<concepts>`, and a `requires`
line is a condition on the template that follows it. A related form, a requires expression, appears in
`StrataScriptCore/Include/StrataScript/Script.h`: `if constexpr (requires { &T::OnCreate; })` is true when the code in the
braces compiles, here when `T` has a member named `OnCreate`.

## The preprocessor edits text before the compiler reads it

Some choices cannot be made by the compiler: which file to include, whether this is a shipping build, how to compile an
assertion out without a trace. The **preprocessor** is a first pass over the source that obeys the lines starting with
`#` and replaces macros, before the compiler sees the code. `#include "file"` pastes the file's text where the line stands,
and `#pragma once` stops a header from being pasted twice.

A **macro** is a name that the preprocessor replaces with text. `#define SQUARE(x) ((x) * (x))` is a macro with an
argument: `SQUARE(1 + 2)` is replaced by the text `((1 + 2) * (1 + 2))`. The preprocessor pastes text, not values, so
an argument without brackets breaks, and an argument with a side effect runs twice.

```cpp sketch="basics-cpp-modern-macros.cpp"
// The preprocessor replaces macro text before the compiler reads it, so parentheses decide the result.
#include <iostream>

#define BAD_SQUARE(x) x * x
#define SQUARE(x) ((x) * (x))
#define SHOW(expression) std::cout << #expression << " = " << (expression) << " at line " << __LINE__ << '\n'

#if defined(ST_DIST)
	#define MODE "shipping"
#else
	#define MODE "development"
#endif

int main()
{
	SHOW(BAD_SQUARE(1 + 2));
	SHOW(SQUARE(1 + 2));
	std::cout << "mode " << MODE << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-macros.cpp"
BAD_SQUARE(1 + 2) = 5 at line 16
SQUARE(1 + 2) = 9 at line 17
mode development
```

1. **Line 4:** `x * x` with no brackets turns `1 + 2` into `1 + 2 * 1 + 2`, which is 5.
2. **Line 6:** `#expression` makes the text of the argument a string, and `__LINE__` is the line of the use.
3. **Lines 8–12:** `#if defined(...)`, `#else` and `#endif` keep one `#define` and drop the other before compiling.

:::example[Expanding by hand]
`BAD_SQUARE(1 + 2)` is replaced by `1 + 2 * 1 + 2`. Multiplication comes first, so the line is 1 + 2 + 2, which is 5.

`SQUARE(1 + 2)` is replaced by `((1 + 2) * (1 + 2))`, which is 3 × 3 = 9. The brackets around each `x` are the
whole fix.
:::

Try it: What does `#define DOUBLE(x) ((x) + (x))` give for `DOUBLE(2 * 3)`, and what goes wrong for `DOUBLE(count++)`?

:::answer
`((2 * 3) + (2 * 3))` is 12. For `DOUBLE(count++)` the text `count++` appears twice, so `count` grows by 2 and the
two reads differ.
:::

The build decides much of this. `#if` tests a condition, `#ifdef NAME` tests only that the name exists, and `#error "text"`
stops the build with a message. `PlatformDetection.h` stops the build with `#error` on a platform Strata does not support.

The build passes definitions to the compiler (the details are in [Building](../basics/build.md)). The Dist configuration,
the build that ships to players, defines `ST_DIST`, and `Base.h` tests it with `#if !defined(ST_DIST)` to define `ST_ENABLE_ASSERTS`. The options named
`ST_WITH_` followed by a module, such as audio, are always defined, as 1 or 0, so the engine writes `#if ST_WITH_AUDIO`
and not `#ifdef`, which would be true for 0 as well.

```cpp src="Strata/src/Strata/Core/Assert.h#L63-L70"
// Asserts are compiled out of Dist builds; the condition must not have side effects.
#ifdef ST_ENABLE_ASSERTS
	#define ST_CORE_ASSERT(condition, ...) ST_INTERNAL_ASSERT_IMPL(true, false, condition, __VA_ARGS__)
	#define ST_ASSERT(condition, ...) ST_INTERNAL_ASSERT_IMPL(false, false, condition, __VA_ARGS__)
#else
	#define ST_CORE_ASSERT(condition, ...) ((void)0)
	#define ST_ASSERT(condition, ...) ((void)0)
#endif
```

When `ST_ENABLE_ASSERTS` is defined, the macro runs the check. Otherwise it becomes `((void)0)`, an expression that does nothing.

:::why[Why the engine keeps these macros]
`ST_CORE_ASSERT` must know the text of the condition, the file and the line of the call, and must vanish without a trace
in a Dist build. A function sees none of those, and no function can skip evaluating its arguments. So a macro does the
work, and the comment on line 63 states the cost: the condition must have no side effects, because in Dist it is not run.
:::

`ST_SCRIPT_CLASS(Spinner)` in a script is also a macro. The software development kit (SDK) for scripts is the subject of
[the script SDK](../scripting/abi-sdk.md), which shows what that macro expands to.

## Exceptions jump out of the code that failed

An exception is C++'s way to leave a function without a normal return. `throw` starts one, `try { ... }` marks code
that may throw, and `catch (const std::type&)` handles it. While the exception travels up, C++ runs the
:term[destructor]{id=destructor} of every object whose block it leaves; the standard calls this `unwinding`. Without a `catch` the program
ends.

```cpp sketch="basics-cpp-modern-exceptions.cpp"
// Reading an empty optional with value() throws; the throw runs the destructor of every object it leaves.
#include <iostream>
#include <optional>
struct Guard
{
	~Guard() { std::cout << "guard released\n"; }
};
int Work()
{
	Guard guard;
	const std::optional<int> nothing;
	return nothing.value();
}
int main()
{
	try
	{
		std::cout << Work() << '\n';
	}
	catch (const std::bad_optional_access&)
	{
		std::cout << "caught a bad optional access\n";
	}
}
```

```text output-of="basics-cpp-modern-exceptions.cpp"
guard released
caught a bad optional access
```

1. **Line 12:** `value()` on an empty optional throws, and the guard is destroyed on the way out.
2. **Lines 20–22:** the handler runs after the guard line, so the order shows the objects being destroyed first.

Strata's own code does not throw: it returns errors. But the standard library and other libraries throw, so Strata
catches them where they enter.

```cpp src="Strata/src/Strata/Core/JobSystem.cpp#L37-L48"
try
{
	job.Function();
}
catch (const std::exception& exception)
{
	ST_CORE_ERROR("JobSystem: job threw an exception: {}", exception.what());
}
catch (...)
{
	ST_CORE_ERROR("JobSystem: job threw an unknown exception");
}
```

1. **Lines 41–44:** a job that throws a standard exception is logged, and the worker continues.
2. **Lines 45–48:** `catch (...)` takes anything else, so no exception kills a worker thread.

:::rule[Engine code does not throw]
A failure the program can survive returns `bool`, `std::optional` or a result struct, and the code that calls a third-party
library catches its exceptions. A thrown exception that no one catches would end the whole program. [Conventions](../core/conventions.md) has the
full rule.
:::

## A path joins with a slash

`std::filesystem::path` holds a file name or a folder path and does the joining for you. The `/` operator joins parts
with the slash the system needs: `root / "Textures" / "Brick.png"`. Its functions answer questions about the pieces:
`filename()`, `stem()` (the name without the extension), `extension()` and `parent_path()`. Strata builds a save folder
with `... / "Saves"` in `SaveFiles.cpp`.

```cpp sketch="basics-cpp-modern-path.cpp"
// A path joins parts with the slash operator and answers questions about its pieces.
#include <filesystem>
#include <iostream>

int main()
{
	const std::filesystem::path root = "Assets";
	const std::filesystem::path texture = root / "Textures" / "Brick.png";
	std::cout << texture.generic_string() << '\n';
	std::cout << "file " << texture.filename().generic_string() << ", name " << texture.stem().generic_string() << ", extension " << texture.extension().generic_string() << '\n';
	std::cout << "folder " << texture.parent_path().generic_string() << '\n';
	return 0;
}
```

```text output-of="basics-cpp-modern-path.cpp"
Assets/Textures/Brick.png
file Brick.png, name Brick, extension .png
folder Assets/Textures
```

1. **Line 8:** two `/` joins make one path; the pieces are chosen by name, never by cutting the text.

The text inside a path is the trap. On Windows a path made from a narrow string uses the system's code page, not UTF-8.
Strata converts at that boundary with `FileSystem::FromUTF8`; [Files and paths](../core/files.md) explains the reason.

## An incomplete type is a name without a body

The line `class Scene;` declares that a class named `Scene` exists and says nothing else. Until its definition is seen,
`Scene` is an **incomplete type**: a name without a body. You can write a pointer or a reference to it and use it as a
parameter type, but you cannot create one, take its `sizeof` or call its members.

A header that needs only a pointer declares the class this way, instead of including the whole header. That keeps
compile times short and breaks include cycles. `Scene` is declared so in many Strata headers, such as `CookedScene.h`.

A `std::unique_ptr<T>` of an incomplete `T` works until the pointer must delete the object, in its destructor. So the
class declares the destructor in the header and defines it in the `.cpp` file, where `T` is complete. `FileWatcher` does
this with a private `Impl`.

```cpp src="Strata/src/Strata/Core/FileWatcher.h#L50-L65"
	FileWatcher();
	~FileWatcher();

	FileWatcher(const FileWatcher&) = delete;
	FileWatcher& operator=(const FileWatcher&) = delete;

	bool Start(const std::filesystem::path& directory, const FileWatcherSettings& settings = {});
	void Stop();
	bool IsRunning() const;
	const std::filesystem::path& GetDirectory() const;

	// Returns the changes detected since the previous call, coalesced per file, oldest first.
	std::vector<FileChange> PollChanges();
private:
	struct Impl;
	Scope<Impl> m_Impl;
```

1. **Lines 50–51:** the constructor and destructor are declared here and defined in `FileWatcher.cpp`, where `Impl` is complete.
2. **Lines 53–54:** copying is deleted, so two watchers never share one `Impl`.
3. **Lines 64–65:** `struct Impl;` names a type without a body, yet `Scope<Impl>` is already a member.

A `std::span<T>` is stricter: its element type must be complete, so a span of `Scene` needs the whole definition, while
a span of `Scene*` does not.

## Casts, `mutable` and bytes

`static_cast` converts between related types and is checked while compiling. `reinterpret_cast` makes the compiler read
the same bytes as another type, with no check. Strata uses it, for example, to view a value as bytes in `BinaryWriter::Write`.
Reading a number back out of bytes goes through `std::memcpy` in `BinaryReader::ReadBytes`: casting a byte pointer to a
`uint32_t*` is undefined behavior. `std::bit_cast<uint32_t>(f)` reads a `float` as the same 32 bits, as `AudioSystem.cpp` does.

The word `mutable` marks a member that a `const` function may change. Strata uses it for the mutex of a class whose
read-only functions must still lock: `mutable std::mutex m_Mutex;` in `BackgroundLogSink.h`.

## Common mistakes

- **Using an object after `std::move`.** The symptom is an empty vector or string where you expected your data. Assign
  a new value before you use it again, or do not move what you still need.
- **Writing `return std::move(local);`.** The symptom is none: the code works but copies more than needed. Return the
  local by its name and the compiler moves or skips the copy.
- **Reading an optional with `*` without a test.** The symptom is a crash or a garbage value. Test it first, or use
  `value_or`.
- **Returning a `std::string_view` of a local string.** The symptom is text that changes or crashes. Return a
  `std::string`, which owns its letters.
- **Omitting brackets in a macro, or a side effect inside `ST_CORE_ASSERT`.** The symptom is 5 where you wanted 9, or
  code that runs in Debug and vanishes in Dist. Write `((x) * (x))`, and keep conditions free of side effects.
- **Casting a number from a file into an `enum class`.** The symptom is a value that matches no name, and a `switch`
  that skips every case. Check the range before the cast.

## Summary

- A move hands an object's contents to another object and leaves the source valid, with contents the standard does not
  define; `std::move` labels the source, and `std::forward` keeps an argument's kind.
- `std::optional` is for an answer that may be absent, and `std::variant` with `std::visit` is for one of several types;
  test an optional before `*` or use `value_or`.
- A string view and a span point into data they do not own, and they dangle when it dies or moves.
- A scoped enumeration has a fixed type, a cast checks nothing, and `ST_DEFINE_ENUM_FLAG_OPERATORS` gives it flag
  operators; `constexpr` and `static_assert` compute and check before the program runs.
- The preprocessor pastes text before compiling: macros need brackets, `#if` follows the build's definitions, and
  concepts and traits ask questions about types.

## Check yourself

1. After `std::string b = std::move(a);`, which statement is true?

   - A. `a` is unchanged.
   - B. `a` is valid, but the standard does not say what it holds.
   - C. `a` is deleted, and using it does not compile.
   - D. `b` is a copy of `a`.

   :::answer{tests="move-semantics"}
   B. The move may empty `a`, so you may assign to it or destroy it, but not rely on what it holds. A is wrong because
   the move usually changes `a`. C is wrong because `a` still exists. D is wrong because a move does not copy.
   :::

2. What does this write?

   ```cpp pseudocode
   std::optional<int> a = 4;
   std::optional<int> b;
   Log::Info(a.value_or(0) + b.value_or(10));
   ```

   Evaluate each `value_or` on its own.

   :::answer{tests="optional-variant"}
   `a` holds 4, so `a.value_or(0)` is 4. `b` is empty, so `b.value_or(10)` is 10. The line writes the sum, 14.
   :::

3. Which of these leaves a view pointing to something that is gone? Choose every one.

   - A. `std::string_view view = "gold";`
   - B. `std::string_view view = std::string("gold");`
   - C. A `std::span<int>` of a vector, then `push_back` on the vector.
   - D. A `std::span<int>` of a vector, then reading the span at once.

   :::answer{tests="views"}
   B and C. In B the temporary string dies at the end of the statement. In C the vector may allocate a new block, and the span keeps
   the old address. A is safe because a literal lasts for the whole program, and D reads before anything changes.
   :::

4. What number is `ComponentFlags::NoCopy | ComponentFlags::Hidden`, and what does `HasFlag` of that value and
   `ComponentFlags::NotRemovable` give?

   :::answer{tests="enum-constexpr"}
   `NoCopy` is `ST_BIT(2)`, 4, and `Hidden` is `ST_BIT(0)`, 1, so the value is 5. `NotRemovable` is 2, and 5 & 2 is 0, which
   is not 2, so `HasFlag` gives false.
   :::

5. A build contains `ST_CORE_ASSERT(count++ < 10);`. What differs between a Debug and a Dist build?

   :::answer{tests="compile-time"}
   In Debug the condition runs and `count` grows by one each time. In Dist the macro becomes `((void)0)`, so `count++`
   never runs. A side effect inside an assert makes the two builds behave differently.
   :::

## Practice

Run exercises 1 to 4 in your `Playground` script, from [Programming from zero I](../basics/programming-1.md#the-playground-is-a-script-of-your-own). Each solution is a plain
C++ program that does the same.

If the **Console** still shows the lines of your earlier code, read the last line of the build: `(the module was up to date)` at its end means that it compiled nothing. A build compares the times of files, and a drive that keeps them in steps of two seconds can hide a change saved right after a build. Save the file again and press **Ctrl+B**.

1. **Basic.** Predict the two lines that log the sizes of two `std::vector<int>` after a copy and after a `std::move`
   of a vector with five numbers. Then run them.

   :::answer[Worked solution]{tests="move-semantics" solution="sketches/basics-cpp-modern-vectors.cpp"}
   The copy leaves both vectors with 5 numbers. The move gives the numbers to the new vector, so the old one reports 0 in
   practice, though only "valid" is promised.

   ```cpp sketch="basics-cpp-modern-vectors.cpp"
   // Practice 1: the sizes of two vectors after a copy and after a move.
   #include <iostream>
   #include <utility>
   #include <vector>

   int main()
   {
   	std::vector<int> first = { 1, 2, 3, 4, 5 };
   	std::vector<int> copied = first;
   	std::cout << "after the copy: first " << first.size() << ", copied " << copied.size() << '\n';
   	std::vector<int> moved = std::move(first);
   	std::cout << "after the move: first " << first.size() << ", moved " << moved.size() << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-modern-vectors.cpp"
   after the copy: first 5, copied 5
   after the move: first 0, moved 5
   ```

   1. **Line 11:** this is the only move; every line before it copies.
   :::

2. **Medium.** Write a function that returns `std::optional<int>`: the first even number of a list, or nothing. Log
   the answer for a list with one and a list without, using `value_or(-1)`.

   :::answer[Worked solution]{tests="optional-variant" solution="sketches/basics-cpp-modern-firsteven.cpp"}
   The function returns the number at the first match and `std::nullopt` after the loop. The caller needs no test.

   ```cpp sketch="basics-cpp-modern-firsteven.cpp"
   // Practice 2: a function that returns an optional, and a caller that supplies a fallback with value_or.
   #include <iostream>
   #include <optional>
   #include <vector>

   std::optional<int> FirstEven(const std::vector<int>& numbers)
   {
   	for (int number : numbers)
   		if (number % 2 == 0)
   			return number;
   	return std::nullopt;
   }

   int main()
   {
   	std::cout << "first: " << FirstEven({ 3, 5, 8, 10 }).value_or(-1) << '\n';
   	std::cout << "second: " << FirstEven({ 3, 5, 7 }).value_or(-1) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-modern-firsteven.cpp"
   first: 8
   second: -1
   ```

   1. **Lines 8–11:** the loop returns early on a match; falling out of it means no even number exists.
   :::

3. **Medium.** Log a `std::variant<int, std::string>` that holds 42, and then one that holds `"gold"`, with
   `std::visit`.

   :::answer[Worked solution]{tests="optional-variant" solution="sketches/basics-cpp-modern-visit.cpp"}
   The generic lambda accepts both types, and `<<` prints each.

   ```cpp sketch="basics-cpp-modern-visit.cpp"
   // Practice 3: a variant of an int and a string, written out through std::visit.
   #include <iostream>
   #include <string>
   #include <variant>

   int main()
   {
   	const std::variant<int, std::string> values[] = { 42, std::string("gold") };
   	for (const auto& value : values)
   	{
   		std::visit([](const auto& item) { std::cout << "holds " << item << '\n'; }, value);
   	}
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-modern-visit.cpp"
   holds 42
   holds gold
   ```

   1. **Line 11:** the lambda takes `const auto&`, so one lambda serves both alternatives.
   :::

4. **Hard.** Write a `constexpr` function `Cube` and check `Cube(3) == 27` with `static_assert`. Declare an
   `enum class Level : uint8_t` with `Easy`, `Normal`, `Hard`, cast `Level::Hard` to a number and `number - 1` back
   to a `Level`.

   :::answer[Worked solution]{tests="enum-constexpr" solution="sketches/basics-cpp-modern-levels.cpp"}
   `Hard` is 3, and 2 casts back to `Normal`. The assert needs no run: the compiler checks it.

   ```cpp sketch="basics-cpp-modern-levels.cpp"
   // Practice 4: a constexpr function checked by static_assert, and an enum class cast to a number and back.
   #include <cstdint>
   #include <iostream>

   constexpr int Cube(int n) { return n * n * n; }
   static_assert(Cube(3) == 27);

   enum class Level : uint8_t
   {
   	Easy = 1,
   	Normal = 2,
   	Hard = 3
   };

   int main()
   {
   	const int number = static_cast<int>(Level::Hard);
   	const Level back = static_cast<Level>(number - 1);
   	std::cout << "Hard is " << number << ", one lower is Normal: " << (back == Level::Normal) << '\n';
   	std::cout << "cube of 3 is " << Cube(3) << '\n';
   	return 0;
   }
   ```

   ```text output-of="basics-cpp-modern-levels.cpp"
   Hard is 3, one lower is Normal: 1
   cube of 3 is 27
   ```

   1. **Line 6:** if `Cube` were wrong, the build would stop here.
   2. **Lines 17–18:** both conversions need `static_cast`, and nothing checks the range.
   :::

5. **Hard.** Optional, on Coin Run: your Coin Run from [Coin Run](../make/project-coin-run.md), or Checkpoint 4 at the end of [Ship the finished game](../make/project-coin-run.md#ship-the-finished-game), opened with **File ▸ Open Project...**. Write a
   function that returns the nearest coin not yet taken as a `std::optional`, with nothing when all are taken. Add an
   `enum class` for the game's state, used with a `switch`, and the number of coins as a `constexpr`.

   :::answer[Worked solution]{tests="optional-variant,enum-constexpr" solution="sketches/basics-cpp-modern-coins.cpp"}
   The function keeps the best index found so far, and an empty optional means every coin is taken. Here the first coin
   is taken, so the nearest is the one at 1.5.

   ```cpp sketch="basics-cpp-modern-coins.cpp"
   // Practice 5: the nearest coin as an optional, a game state with a switch, and the coin count as a constexpr.
   #include <cstdint>
   #include <iostream>
   #include <optional>
   enum class GameState : uint8_t { Playing, Won };
   constexpr size_t c_CoinCount = 3;
   struct Coin { float Distance = 0.0f; bool Taken = false; };
   std::optional<size_t> FindNearest(const Coin (&coins)[c_CoinCount])
   {
   	std::optional<size_t> best;
   	for (size_t index = 0; index < c_CoinCount; index++)
   		if (!coins[index].Taken && (!best || coins[index].Distance < coins[*best].Distance)) best = index;
   	return best;
   }
   int main()
   {
   	const Coin open[c_CoinCount] = { { 4.0f, true }, { 1.5f }, { 9.0f } };
   	const Coin taken[c_CoinCount] = { { 4.0f, true }, { 1.5f, true }, { 9.0f, true } };
   	std::cout << "nearest: " << *FindNearest(open) << '\n';
   	switch (FindNearest(taken) ? GameState::Playing : GameState::Won)
   	{
   		case GameState::Playing: std::cout << "keep going\n"; break;
   		case GameState::Won: std::cout << "you win\n"; break;
   	}
   }
   ```

   ```text output-of="basics-cpp-modern-coins.cpp"
   nearest: 1
   you win
   ```

   1. **Line 12:** `!best` accepts the first free coin, and `*best` reads only once `best` holds an index.
   2. **Lines 20–24:** the `switch` names every state, so the compiler can warn about a missing case.
   :::

## Where the book uses it

- [Conventions](../core/conventions.md) uses `std::optional` as a returned error and the rule against throwing.
- [Files and paths](../core/files.md) uses `std::filesystem::path` and `std::string_view`.
- [Reflection](../world/reflection.md) uses `std::variant` and `std::visit` for property values.
- [The script SDK](../scripting/abi-sdk.md) uses macros such as `ST_SCRIPT_CLASS` and a type that only moves.
- [Flags and portability](../engineering/flags-portability.md) uses `#if`, `#error` and the build's definitions.

## Further reading

- Learn C++, [learncpp.com](https://www.learncpp.com): lessons on move semantics, `std::optional`, `constexpr`, the
  preprocessor and exceptions. Beginner to intermediate.
- cppreference, [en.cppreference.com](https://en.cppreference.com): the reference for `std::variant`, `std::span`,
  concepts and type traits. Intermediate to advanced.
