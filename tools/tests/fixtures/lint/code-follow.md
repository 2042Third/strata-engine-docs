After every fence, the text says what the code showed: the block after it is a paragraph or a numbered list, or the
output-of fence of the same sketch followed by one (style.md §9.1). A fence that ends a tab is followed by what
follows its tab set.

%%% pass core/time
The command:

```json
{ "command": "script.build" }
```

It builds.

The sketch:

```cpp sketch="core-time-count.cpp"
int main() { return 0; }
```

```text output-of="core-time-count.cpp"
0
```

1. **Line 1:** the program returns at once.

The steps:

1. Build.

   ::::tabs{sync=how}
   :::tab[With a command]
   Run:

   ```json
   { "command": "script.build" }
   ```

   :::
   ::::

   It builds.

%%% fail core/time 3 11
The command:

```json
{ "command": "script.build" }
```

## Next

The sketch:

```cpp sketch="core-time-count.cpp"
int main() { return 0; }
```

```text output-of="core-time-count.cpp"
0
```

- A bullet is no callout.
