# Card: reference (R)

Generated tables with a little text, for looking things up. Most of the page comes from `tools/reference.py`.

## Front matter

`id`, `title`, `description`, `kind: reference`, `size` (the row's; not checked: reference pages have no `size`
range), `tracks` (`[]` for pages on no track), `needs`, `status: draft`. No `time`, no `learn`, no `since` (strips).

## Order

1. One paragraph on top: what the table is and how to read it (what a row and each column mean). Several paragraphs
   are allowed when the table needs them; each follows the language rules.
2. The generated table: `::include{file="<table>.md"}`, a file of `src/generated/reference/` (only on pages of
   `reference`). Never copy or retype a generated table, and never type a count the engine can change: use
   `:value{key="…"}` (keys in `src/generated/reference/values.json`).
3. Hand-written notes only where the generator allows them. A table the brief names that `src/generated/reference/`
   lacks is written by hand from the pin's files: list each under `## Hand-written tables` in the notes, with the
   engine files it was read from (`plan/notes/HAND-TABLES.md` collects them for the check after the pin moves).
   A link to an outline page that is not written yet is allowed: the pages check accepts it.
4. `## Where it lives in Strata` (exact; the only section of the strip): the files, commands and tests the table comes
   from. Every name is checked by names.

No questions, no answers, no exercises, no `:::example`.

## Rules that still apply

All of common.md's language, term, code and honesty rules. The fourth reader of a reference page is a contributor or an
agent who arrived by search: write so that E1 can read it, and say what each term E1's list does not hold is, linking
its home.

## Skeleton

````md
---
id: reference/performance
title: "Measured costs and their budgets"
description: "Every cost the engine's speed tests measure, with its budget."
kind: reference
size: M
tracks: []
needs: []
status: draft
---

<What the table is.> The engine's speed tests measure :value{key="perfBudgets.count"} costs. <How to read a row.>

::include{file="performance.md"}

## Where it lives in Strata

- `StrataTests/Perf/Budgets.json`: <what it holds>.
````
