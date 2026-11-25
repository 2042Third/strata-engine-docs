# The clerk's procedure for the writers' notes

After each wave, a clerk admits what the wave's notes (`plan/notes/<part>/<chapter>.md`) ask. Writers never edit the
glossary or the word lists; the clerk does, from their notes only.

## New terms

- A term the asking page homes and the glossary lacks: add an entry to `plan/glossary/admitted.json` (the schema of
  `seed.json`: `id`, `term`, `definition`, `home`, `aliases`, `avoid`), its home the asking page, its definition the
  page's one sentence.
- A new wording or aliases for a term the asking page homes: an entry with the same id and term; the home page's
  wording replaces the definition.
- A meaning the glossary holds under another home: the term `<Word> (<part>)`, id `<word>-<part>`.
- Refuse, and say why: a term that is an everyday word used in its everyday sense (a unit, school mathematics, a word
  of `tools/data/common-words.txt` or `extra-words.txt`); a term the glossary homes on another page (only its home
  words it); a term that is already an alias of an entry (its home is the planner's).

## Requests

- A proper name (product, sample, person): a line of `tools/data/names.txt`.
- An everyday or school word: a line of `tools/data/extra-words.txt`, a tab, then its covering line (the persona item
  of `plan/style.md` §1.1, "G0 has 5").
- A word of a field: a term request for the home page the request names, in `admitted.json`, defined from the asking
  page's sentence.
- An external host: a line of `tools/external-hosts.txt` when it is a publisher's, a standards body's, a project's own
  site or a well-known reference, after one fetch of its front page shows it is what it claims. A host the fetch
  cannot confirm stays out and goes to the planner.
- Figures, tools, layouts, homes of existing terms: the planner's.

## Leave alone

`## Not verified` and `## Findings not applied` stay as they are: the part's reviewer reads them.

## Run and record

```sh
/c/msys64/mingw64/bin/python.exe -I plan/glossary/merge.py
/c/msys64/mingw64/bin/python.exe -I plan/glossary/merge.py --check
/c/msys64/mingw64/bin/python.exe -I tools/pages.py check
/c/msys64/mingw64/bin/python.exe -I -m unittest discover -s tools/tests
```

`merge-report.md`'s "Admitted from the pages' notes" lists what entered, and "Admitted term refused" what the merge
refused; fix those. No `src/content/glossary.json` error may appear in the page check. Then add to each notes file a
`## Clerk` section: what was admitted, refused (with the reason), and left for the planner. Commit the notes,
`admitted.json`, `merge.py`'s outputs and the lists together.
