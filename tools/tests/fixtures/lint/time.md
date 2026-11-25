The front matter's time is at least the reading floor (prose words / 120 + lines of code shown / 10, rounded up to a
multiple of 5 minutes), and at most twice it on concept and internals pages (style.md §2.2). 600 words and 10 lines of
code give 5 + 1 = 6, so a floor of 10 minutes. appendix/history is a concept page.

%%% pass appendix/history time=10
%%repeat 200 The ball rolls.%%

The sketch prints ten lines:

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
```

It counts.

%%% pass appendix/history time=10
%%repeat 200 The ball rolls.%%

%%% fail appendix/history key:time time=5
%%repeat 200 The ball rolls.%%

The sketch prints ten lines:

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
```

It counts.

%%% fail appendix/history key:time time=11
%%repeat 200 The ball rolls.%%
