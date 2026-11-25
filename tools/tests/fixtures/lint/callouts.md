A fence of 10 or more lines is followed by a numbered list of 1 to 5 callouts, each starting with "Line N:" or
"Lines N–M:" inside the line numbers the fence shows: the engine's for a quote (style.md §9.1).

%%% pass core/time
The quote:

```cpp src="Strata/src/Strata/Core/Time.h#L20-L29"
int line20;
int line21;
int line22;
int line23;
int line24;
int line25;
int line26;
int line27;
int line28;
int line29;
```

1. **Line 20:** the first field.
2. **Lines 28–29:** the last two.

The output of ten lines needs none:

```text output-of="core-time-count.cpp"
1
2
3
4
5
6
7
8
9
10
```

It counts.

%%% fail core/time 3 31
The sketch:

```cpp sketch="core-time-ten.cpp"
int a1;
int a2;
int a3;
int a4;
int a5;
int a6;
int a7;
int a8;
int a9;
int a10;
```

It declares ten values.

```cpp src="Strata/src/Strata/Core/Time.h#L20-L29"
int line20;
int line21;
int line22;
int line23;
int line24;
int line25;
int line26;
int line27;
int line28;
int line29;
```

1. **Line 5:** outside the quote's lines.
