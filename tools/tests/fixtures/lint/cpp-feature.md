The first use of a C++ feature whose home is neither the page nor in its Needs closure gets a :::question aside before
its fence that links the home (style.md §9.1; the features are tools/data/cpp-features.json). core/time's closure
holds basics/programming-1 (int, if) but not basics/programming-3 (class) or basics/cpp-memory (pointers).

%%% pass core/time
:::question[What is a class?]
A class groups values with the functions that use them: [the third programming primer](../basics/programming-3.md)
teaches it.
:::

The sketch:

```cpp sketch="core-time-class.cpp"
// A class with a pointer -> in a comment
class Ball
{
	int Speed = 2;
};
```

It holds a speed.

```cpp pseudocode
Ball* ball = nullptr;
```

Pseudocode is not checked.

%%% fail core/time 3
The sketch:

```cpp sketch="core-time-class.cpp"
class Ball
{
	int Speed = 2;
	Ball* Next = nullptr;
};
```

It holds a speed.

```cpp sketch="core-time-other.cpp"
class Wall {};
```

The same features again are not reported again.
