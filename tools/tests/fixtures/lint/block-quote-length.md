A block quote of prose has at most 60 words and a line that names its source (style.md §2.1).

%%% pass core/time
> The main thread owns the scene.
> — AGENTS.md, "Architecture rules"

%%% fail core/time 1 4
> %%repeat 15 The main thread waits.%%
> — AGENTS.md

> The main thread owns the scene.
