# Card: checking a page

## The command

From the worktree's root, after each round of changes:

```sh
/c/msys64/mingw64/bin/python.exe -I tools/pagecheck.py <page id> [--fill-sketches]
```

It finds the pin clone itself (or `--engine <clone>`). It runs `markterms.py`, then the lint,
`pages.py check`, `names.py check`, `excerpts.py fill` then `check`, and, when the page has them, the sketches, figures
and tutorial checks. `--fill-sketches` first copies each sketch file and its real output into the page's fences.

## What the first run writes

`markterms` writes a `:term[…]{id=…}` mark at the first use of each term homed in your Needs closure, never a link;
`excerpts fill` writes each quote's lines into its empty fence. Your next edits start from the page as the run left
it, never from your draft: read the quotes' lines, then write their callouts. The lint reads the page before the run's
fills: after a quote or sketch changes, line numbers and `long-quote`, `cpp-feature` verdicts lag one run.

## Reading it

- One block per check: `passed`, or `FAIL (n failing)` with groups `<rule>: <count>`, at most five lines
  `file:line: message` each, and `(n more)`; the full list:
  `tools/lint.py <page id> --engine <clone>`.
- `warnings:` (lint `passive`, `noun-stack`, `term-source`): decide each; they do not fail.
- `other files, not counted:` and notes: not yours.
- `words: <n> prose words; size <S> holds <a> to <b>`, then `pagecheck: PASS` or `pagecheck: FAIL (<n> failing)`.

## Order of fixing

Apply all fixes of a round in one step, on the page as it is, then run again.

1. Front matter: `id`, `title`, `kind`, `size`, `tracks`, `needs`, `learn`, `since`, `status`, `front-matter`.
2. Structure (`pages`): headings, counts, answers and `tests`, examples, checkpoints.
3. Quotes and sketches: `excerpts`, then `sketches` (`--fill-sketches` after changing a sketch).
4. `names`, then the terms (`term-*`).
5. Code rules: `code-intro`, `code-follow`, `callouts`, `cpp-feature`, `long-quote`.
6. Language: `sentence-*`, `paragraph-length`, `word-list` and the word rules.
7. `size` and `time` last: every edit changes them.

## Your files

Scratch files go in a folder named after your page (the scratchpad is shared); write scripts with the Write
tool, never shell heredocs.

## What you may leave, and must report

Write each in the notes (`## Not verified` or `## Requests`) and in your final report:

- a `names` finding for a name at the pin that the dumps lack (not a perf budget key: write "the metric
  `MoveRoot100k` of the `Perf.Scene` suite");
- a figure not drawn or taken yet;
- `size` out of its range by less than 10 %;
- `word-list` for a word you proposed under `## New terms` or `## Requests`;
- a `sketches` notice "not compiled", or a check "skipped".

Fix everything else.

## Not yours

The site build (`astro build`, rendering Mermaid diagrams), taking and publishing pictures, running tutorials
(`tutorials.py run`), findings in other files, `src/sidebar.json` (`pages` O5, O9: report them), the glossary, tools,
and CI.
