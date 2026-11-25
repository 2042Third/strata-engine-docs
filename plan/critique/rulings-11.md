# Rulings 11: the lean path to the written book

The time left for the book decides how it is made (2026-11-11): the plan's ceremony between the settled units and
the pages is cut, and what the trial of the writer's card found is settled here. Where this file differs from an
earlier file, this file wins.

## R50 — The common words

The lint's `word-list` rule exists to keep rare words and jargon out of a page, or to make them glossary terms. With
the 2,807 headwords of the frequency bands 1 to 11 it also refuses everyday words (diagram, database, swap, scanner,
replay), and a writer's first draft fails on them more often than on every other rule together. The list widens to
the frequency bands of 12dicts' `2+2+3frq` that give at least 8,000 headwords: the smallest last band that reaches
that count. `tools/wordlists.py`, `tools/data/common-words.txt`, the tests, style.md §2.3 and `plan/card/common.md`
state the new band and count. A word of a field (shader, texture, compiler) stays a glossary term whatever band it is
in: the glossary wins over the list, as today.

## R51 — The glossary is filled before the pages

`src/content/glossary.json` takes, by script (`plan/glossary/merge.py`), the seed's entries and every term of the
inventories, with the definition the seed or the inventory gives and the home that the units' files give its row.
There is no admitter per term. A page's writer who needs another wording, a new term, or a term of a page it needs
writes it in `plan/notes/<page id>.md` (the card's `## New terms` and `## Requests`); the notes are merged by script
after each wave, and the home page's wording wins. Writers do not edit the glossary file: they would overwrite each
other.

## R52 — Who writes and who checks

- One writer per page, from the page's brief (`plan/briefs/`), the card (`plan/card/`) and the engine at the pin. The
  unit's whole file, style.md, pipelines.md and site.md are not a writer's reading.
- A writer's exit is `tools/pagecheck.py <page id>` passing, with the exceptions `plan/card/checks.md` lists, each
  reported.
- The part briefs, the admitter, the per-page technical reviewer and provenance reviewer, the part editors' passes and
  the six sample readings of process.md are replaced by one review pass per part after its pages exist: reviewers
  check a part's pages against the engine at the pin and against each other, and correct them.
- The pilot is six pages of different kinds; it measures the cost of a page and corrects the card.
- The waves and phase B keep process.md's order and lists.

## R53 — Terms that are everyday words, qualifiers, and marks made by a tool

The glossary filled by R51 has 1,604 entries. Its merge report and the lint on a sample page showed four things to
settle before pages are written.

- **A term that is one everyday word.** Where a term or an alias is a single word of the common list (tool, reach,
  down, page, step, project), `term-mark` does not ask for a mark at the word's first use on a page: the word is used
  in its everyday sense far more often than as the term. A writer marks it where the page uses the term's own sense.
  On the term's home and use pages nothing changes (`term-defined`). The site's matcher follows the same rule.
- **A name with a qualifier.** In "Clip (animation)" the parenthesis says which meaning the entry holds; it is no part
  of the words a page writes. The lint and the site match the name before the parenthesis (and then the rule above
  applies when that name is one everyday word); the glossary page shows the whole name.
- **One word, several meanings.** The 80 words that pages of different parts home enter the glossary once per
  meaning, as "<Word> (<part of the home page>)" with the id `<word>-<part>`, by the merge script. A home page's
  writer may ask for a better qualifier in its notes.
- **Definitions are plain text.** The merge removes backquotes and bold marks from a definition, since the site
  shows it as plain text.
- **Marks are made by a tool.** `tools/markterms.py <page id>` writes the marks a page needs: at the first use of a
  term whose home is in the page's Needs closure, the `:term` mark; at the first use of a term whose home is
  outside it, the link to its home in the form the lint accepts. It never touches a heading, code, a definition in
  bold or a word the rule above exempts, and it changes nothing a second time. `tools/pagecheck.py` runs it before
  the lint. So a writer does not read the glossary: it defines the terms its brief homes on the page, writes
  plainly, and lets the tool mark.

The report's other lists (rows that ask for several entries of one line, one definition for several names, the four
refused definitions, the three terms without a home) are settled by the home pages' writers through their notes
(R51). Where the seed and an inventory give one term two homes, the seed's home stands.

## R54 — What the pilot showed: the checks must not fight the writer

Six pages were written and checked (2026-11-11). They teach well, and their checkers still corrected three to ten
statements about Strata on each, so every page keeps its checker. The writers spent most of their turns on the
checks, not on the page: 75 to 128 turns each. The reports are in `docs-work/pilot/report.md`. These rules change:

- **A glossary word is a known word.** Every word of a glossary term or alias passes `word-list`, wherever it stands
  and however often, marked or not, its head word alone included ("preset" of "CMake preset").
- **A page marks the terms it builds on.** `term-mark` asks for a mark only at the first use of a term whose home is
  the page itself or in its Needs closure, and `tools/markterms.py` writes only those. A term homed outside the
  closure is neither marked nor linked by the tool, and `term-source` is a warning: a writer who uses such a term
  says in the sentence what it is, and links its home where that helps.
- **A homed term is defined somewhere on its page.** `term-defined` asks for the bold definition anywhere on the home
  page, not at the first use; a use in the test-out box or in a table before it is no failure.
- **Further reading names people.** `word-list` does not read the entries of `## Further reading`.
- **Units and school mathematics are everyday words.** `tools/data/extra-words.txt` takes the units a page of this
  book needs (Hz, millisecond, microsecond, nanosecond, ns, and their plurals where the endings rule does not cover
  them) and the words of school mathematics the pilot's primer missed (subtract, multiplication, perpendicular,
  hypotenuse, parallelogram, quadrant, theorem, amplitude, inverse, infinity, counterclockwise, clockwise, algebra),
  each with its covering line.
- **One run shows everything.** `cpp-feature` reports every feature of a fence in one run. `tools/pagecheck.py`
  prints the page's prose words beside its size's range in every run.
- **Where two texts disagree, the tool wins**, and the card says so case by case: no checkpoints in a patch
  tutorial; a sketch's rules over the toy's line count; the glossary's home over the brief's.
- **The card states what cost a round.** Every gap of the pilot's reports that these rules do not remove is stated in
  the card, which may grow to 2,400 words for `common.md` and 600 for a kind card; a kind card names no other kind
  card.
- A brief lists the terms the glossary homes on its page (`plan/briefs/make_briefs.py`).
