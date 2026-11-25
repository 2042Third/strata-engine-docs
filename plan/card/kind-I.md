# Card: internals (I)

How one part of Strata works, for readers who will change it. `time` ≤ 2 × the floor; `since` as common.md says.

## Order (exact headings in backticks; strips)

1. The job, in one paragraph before the first heading (no heading of its own): what this part does and does not
   do.
2. `## The problem and how engines solve it`: the approaches and their costs, in at most a fifth of the page's prose
   words. When the part's concept page holds this, one paragraph that links it.
3. The map: a diagram of the files, who calls whom, which thread runs what, what each part owns.
4. The contract: what callers may assume and must do, each rule with its reason (`:::rule` for an `AGENTS.md` rule).
5. A toy version: a sketch of 30 to 80 lines (several fences allowed) doing the job simply. Where a compiled,
   warning-free Hazel-style program needs more, the sketch's rules win: as short as they allow. No check counts
   the toy's lines.
6. The real code, in the order data flows, with each difference from the toy and its reason. At least three
   quotes (`excerpts check`).
7. `## Alternatives Strata did not choose`: a table with the columns Technique, Who uses it, What Strata would gain,
   What Strata would lose; sources in Further reading.
8. `## How it is tested`: the suites, what they check, how to run them.
9. `## Changing it safely`: extension points, the `AGENTS.md` rules that apply with reasons, the checks to pass.
10. `## What went wrong before`: a real bug and its regression test, only when the history has one.

At least one `:::example` stands before the strip.

## Bottom strip (exact, in order)

`## Summary` (one bullet per learn line), `## Check yourself` (3–6 questions), `## Exercises` (1–4, **Basic.** to
**Hard.**), `## Where it lives in Strata` (files, classes, tests, commands, settings), `## Further reading`.
Check-yourself answers: multiple choice whose wrong options are the page's mistakes (the answer says why each is
right or wrong), predict the output, short computations. Exercise answers: `:::answer[Worked solution]{tests="…"}`,
worked step by step. One exercise is "trace it yourself": find where something happens with a debugger or a
search; its answer names the file and function, without `solution=`. At least one is done: code, a sketch
`sketches/<part>-<chapter>-<name>.cpp` shown in full in the answer with its `output-of` fence, or an "extend"
exercise, `solution="tutorials/<page id>/exercise-<n>.patch"` (after `core/first-change`).

## Skeleton

````md
<The job.>

## The problem and how engines solve it

## <The map>

## <The contract>

## <A toy version>

<What the toy does.>

```cpp sketch="<part>-<chapter>-toy.cpp"
```

<What it showed.>

## <The real code>

<What to look for.>

```cpp src="<engine path>#<Class::Function>"
```

1. **Line <n>:** <why the line is there>.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |

## How it is tested

## Changing it safely

## Summary

## Check yourself

## Exercises

## Where it lives in Strata

## Further reading
````

Write a quote's callouts after pagecheck filled its lines.
