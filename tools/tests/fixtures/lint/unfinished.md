No TODO, FIXME, TBD or XXX left in a page: in prose and in the book's own fences, not in quotes of the engine (the
spike's rule, style.md §2.2).

%%% pass core/time
The list is finished.

```cpp src="Strata/src/Strata/Core/Time.h#L1-L5"
int line1; // TODO in the engine's own code
int line2;
int line3;
int line4;
int line5;
```

%%% fail core/time 1 4
TODO: finish the list.

```text
FIXME
```
