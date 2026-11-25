# Card: tutorial (T)

The reader makes something step by step. `time` includes doing it; `since` only in parts `make` and `core` to
`engineering`, never in `start` or `basics`.

## Order (exact headings in backticks; strips)

1. `## What you will make` (first section): one or two sentences and `::figure{id=…}` of the result.
2. `## What you need`: the starting point (a template, a copy of a sample, or an earlier tutorial's end state with its
   checkpoint download); every file to import with its source and license (the release's `Samples/*/Assets/` or
   `tutorials/assets/`); the time it takes; for an engine change, the source build of `core/first-change`.
3. Step sections, each named as a task ("Make the ball roll"): one `:::::steps` list (common.md, Steps). Each section
   ends with `::checkpoint{stage=N}` and then its "You should now have" picture `::figure{id=…}`; N counts 1, 2, 3 in
   page order, while each section's steps count from 1 again. A section that explains, no task, stands before
   `## What you need` (`pages`).
4. Every step that changes the screen has a whole-editor picture (`editor` figure, the control to use marked),
   except before a project is open: editor figures name a project. A figure's `project` is a template, a sample,
   look-dev or a lab, never this tutorial's state: rebuild it in `setup` with stand-ins (a cube for the coin), or
   give `waitsFor: tier 2: editor screenshot`; say which under `## Requests`.

## Bottom strip (exact, in order)

`## Summary` (what the reader made and learned, one bullet per learn line), `## Check yourself` (3–6 questions),
`## Exercises` (1–4, **Basic.** to **Hard.**: open extensions, "make it yours", with hints and worked solutions),
`## Where it lives in Strata`, `## Further reading`. These five end the page: no section after them; a "what next"
goes in the last step section, before its `::checkpoint`. At least one exercise is done: its
`:::answer[Worked solution]{tests="…" solution="…"}` names `tutorials/<page id>/exercise-<n>.tutorial.json` (an
editor or command task) or, for an engine change, `tutorials/<page id>/exercise-<n>.patch`.

## The tutorial file

`tutorials/<part>/<chapter>.tutorial.json`: `page`, `startsFrom` (`{"template": "basic3d"}`, `{"sample": "<id>"}`,
`{"tutorial": "<page id>"}`), and `stages`, one per checkpoint:
`{"step": N, "files": [{"from": "book:tutorials/…", "to": "Scripts/…"}], "commands": [<steps with "expect", "checks">]}`,
with `"endState": true` on every stage (each checkpoint offers a download). One `startsFrom` per file: when a first
section works on another project (a sample's copy), its stage has no commands; say so under `## Requests`. Count
game time in fixed steps (`play.step {steps}`), never frames. A step finds its entity with
`"entityName": "<Name>"` (one match; it passes `entity`), never `entity` in `parameters`; a `$ref` names a value an
earlier step of the same stage binds. A file the page imports from the release is `asset.import` of
`"@RELEASE@/Samples/…"`; a code change inside a stage is `files` on the command it comes before; `until` waits through
failing answers (`asset.info` of an asset being imported). `startsFrom` may name a tutorial not written yet: findings
in its file are not yours; report them. Script code
lives in `tutorials/<part>/<chapter>/` and is quoted with `src="book:tutorials/<part>/<chapter>/<file>#L<a>-L<b>"`. You never
run the tutorial: its first run is the integrator's.

An engine-changing tutorial (track E) quotes each change from its patch
(```` ```diff src="book:tutorials/<part>/<chapter>.patch#hunk-<n>" ````; callouts count the hunk's lines from 1) and
has no checkpoints, whatever its brief says. For "You should see", a text capture shows `ctest` or a Strata program
of the pin's build; what CMake, a compiler or the patched build prints is told in words, its key line in backticks.

## Skeleton

````md
## What you will make

<The result in a sentence.>

::figure{id=result}

## What you need

## <Make the ball roll>

:::::steps

1. <The action, as a plain sentence.>

   ::::tabs{sync=how}
   :::tab[In the editor]
   <the clicks and keys, UI labels in bold: **Menu ▸ Item**>
   :::
   :::tab[With a command]

   ```json
   { "command": "<group.action>", "parameters": { } }
   ```

   :::
   ::::

   **You should see:** <what changed>.

   **If you do not see it:** <cause, and the way back>.

:::::

::checkpoint{stage=1}

::figure{id=ball-rolls}

## Summary

## Check yourself

## Exercises

## Where it lives in Strata

## Further reading
````
