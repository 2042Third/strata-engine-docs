# Card: how-to (H)

One goal, reached by steps, for a reader who knows why. `time` includes doing it; `since` where common.md requires it.

## Order (exact headings in backticks; strips)

1. The goal in the first paragraph (the title names it), then a bulleted list of what must be true before the first
   step. Other sections before the steps (such as "What you need") are allowed.
2. Numbered steps in `:::::steps` (common.md, Steps). On track G or B every step has **You should see:** and **If you
   do not see it:** (`step-parts`); every numbered list before `## Result` is read as steps, so lists of other things
   there are bulleted. Steps that differ per system use `::::tabs{sync=os}`; another program's menus go in
   quotes ("Go to Definition"), not bold.
   A how-to may hold one `:::::steps` list in each of several `##` sections; each list counts from 1.
3. `## Result`: what the reader has now, with a picture (`::figure{id=…}`) when it is visible. A how-to of `make`
   block A that changes Coin Run ends it with a download of its end state. A figure's `project` is a template, a
   sample, look-dev or a lab, never a tutorial's state: rebuild it in `setup` with stand-ins, and say so under
   `## Requests`.
4. `## Variations`: the same goal under other conditions. Ends the body.

No theory: a section says why in at most two sentences and links the concept page.

## Bottom strip (exact, in order)

`## Summary` (one bullet per learn line), `## Check yourself` (3–6 questions with `:::answer{tests="…"}`),
`## Exercises` (1–4, **Basic.** to **Hard.**, each with `:::answer[Worked solution]{tests="…"}`),
`## Where it lives in Strata`, `## Further reading`. The steps are the page's worked example: no `:::example` is
required.

At least one exercise is done, not only answered: its answer `:::answer[Worked solution]{tests="…" solution="…"}` names
its file. On G or B before `make/first-script`, on G later, and on E before `basics/programming-1`: an editor task or a
command, `tutorials/<page id>/exercise-<n>.tutorial.json` (its form: `tools/schemas/tutorial.schema.json`, as in
`tutorials/start/install/exercise-2.tutorial.json`). On B later and on E from `basics/programming-1`: code, a
sketch `sketches/<part>-<chapter>-<name>.cpp` shown in full in the answer, then its `output-of` fence; after
`core/first-change`, also an engine change, `tutorials/<page id>/exercise-<n>.patch`. A page on several tracks meets
each. A trace exercise's answer names the file and function, without `solution=`; it is not the done one.

## Skeleton

````md
<The goal.> Before you start:

- <what must be true>

## <Install the build tools>

:::::steps

1. Open a terminal in the folder of the source.

   ::::tabs{sync=os}
   :::tab[Windows]
   <the action>
   :::
   :::tab[Linux]
   <the action>
   :::
   :::tab[macOS]
   <the action>
   :::
   ::::

   **You should see:** <what changed>.

   **If you do not see it:** <cause, and the way back>.

:::::

## Result

## Variations

## Summary

## Check yourself

## Exercises

## Where it lives in Strata

## Further reading
````
