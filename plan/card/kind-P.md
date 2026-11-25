# Card: primer (P)

A lesson from zero on something that is not Strata's own: programming, mathematics, how computers work. No `since`;
`time` includes doing the practice.

## Order (strips checks the exact headings)

1. `::::test-out`, the page's first thing, before any heading or text: exactly 5 numbered questions, each followed by
   `:::answer{tests="<learn ids>"}`. The answers' `tests` together cover every learn id. At least 3 questions ask the
   reader to do something (compute, predict output, write one line). None repeats a Check-yourself question. The build
   writes the box's title and instruction.
2. `## Why you will need this` (first section): what the reader will do with it, naming 2 or 3 pages that use it.
3. The idea on the smallest example: Show, Name, Explain. Headings say what each section establishes.
4. Worked examples: each an `:::example`, then a try-it question with `:::answer` (no `tests`). Faded examples (less
   help each time) where the idea needs practice. At least one `:::example` before the strip.
5. `## Common mistakes`: each mistake, its symptom, its fix. Ends the body.
6. `## Summary`: one bullet per learn line, in order.
7. `## Check yourself`: 3–6 numbered questions (multiple choice with real mistakes as wrong options, predict the
   output, short computations), each with `:::answer{tests="…"}`.
8. `## Practice`: 3–8 numbered exercises, **Basic.**, **Medium.**, **Hard.** never going down, each with
   `:::answer[Worked solution]{tests="…"}`.
9. `## Where the book uses it`: ≥ 3 links to pages whose Needs closure holds this primer, each with one sentence on
   what it uses.
10. `## Further reading`.

## Done, not only answered

At least one practice exercise is done on the reader's workbench, as the tracks require: on G or B before
`make/first-script`, and on E before `basics/programming-1`, an editor task or a command,
`solution="tutorials/<page id>/exercise-<n>.tutorial.json"`; later, code:
`:::answer[Worked solution]{tests="…" solution="sketches/<part>-<chapter>-<name>.cpp"}`, showing the sketch in full
and then its `output-of` fence. The checks compile only standalone programs, so the solution is a sketch even
where the exercise asks for the playground's script (a Basic 3D project printing to the **Console**): the script
itself is `pseudocode`.

## Skeleton

````md
::::test-out
1. What does this line print? …

   :::answer{tests="read-loop"}
   The answer, with its reasoning.
   :::

2. …
::::

## Why you will need this

## <The idea, as a claim>

:::example[<problem>]
…
:::

## Common mistakes

## Summary

## Check yourself

## Practice

1. **Basic.** …

   :::answer[Worked solution]{tests="read-loop" solution="sketches/basics-loops-count.cpp"}
   …
   :::

## Where the book uses it

## Further reading
````
