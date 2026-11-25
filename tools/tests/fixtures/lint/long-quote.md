An engine quote has 5 to 60 lines; on pages of tracks G or B and on level-1 pages every fence has at most 25 lines
(style.md §9.1). core/time is on track E at level 2; make/scenes is on G and B.

%%% pass core/time
The quote:

```cpp src="Strata/src/Strata/Core/Time.h#L1-L5"
int line1;
int line2;
int line3;
int line4;
int line5;
```

It declares. The output:

```text
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
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
```

It prints.

%%% pass core/time
The quote, before the tool fills it:

```cpp src="Strata/src/Strata/Core/Time.h#Time"
```

It declares.

%%% fail core/time 3
The quote:

```cpp src="Strata/src/Strata/Core/Time.h#L1-L2"
int line1;
int line2;
```

It declares.

%%% fail make/scenes 3
The output:

```text
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
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
```

It prints.
