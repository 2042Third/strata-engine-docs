At most 500 words of prose come without a break: a heading, a figure, a code fence, a list, a table, a display
formula or an aside (style.md §2.2). Reported at the run's first paragraph.

%%% pass core/time
%%repeat 50 The ball rolls on.%%

%%repeat 50 The ball rolls on.%%

## A break

%%repeat 50 The ball rolls on.%%

%%% fail core/time 3
## A section

%%repeat 50 The ball rolls on.%%

%%repeat 50 The ball rolls on.%%

%%repeat 26 The ball rolls on.%%

- A list ends the run.
