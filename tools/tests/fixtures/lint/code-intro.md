Before every fence, a paragraph says what the code does (style.md §9.1). Exempt: a fence in a tab whose sibling tab
states the step in words, and an output-of fence right after its sketch.

%%% pass core/time
The sketch counts the steps:

```cpp sketch="core-time-count.cpp"
int main() { return 0; }
```

```text output-of="core-time-count.cpp"
0
```

It prints nothing.

1. Build the scripts.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Choose **Scripts ▸ Build Scripts**.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   It builds.

%%% fail core/time 3 11
## The code

```json
{ "command": "script.build" }
```

$$
x = 1
$$

```json
{ "command": "script.build" }
```

It builds.
