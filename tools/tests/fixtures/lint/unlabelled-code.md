Code that is not quoted from the engine is a sketch or pseudocode (style.md §9.2; the spike's rule).

%%% pass core/time
A sketch:

```cpp sketch="core-time-a.cpp"
int main() { return 0; }
```

Pseudocode:

```cpp pseudocode
position = position + speed * deltaTime;
```

A quote:

```hlsl src="Strata/shaders/a.slang#L1-L5"
```

It is done.

%%% fail core/time 3 9
Some code:

```cpp
int main() { return 0; }
```

A shader:

```slang
float4 main() : SV_Target { return 1; }
```

It is done.
