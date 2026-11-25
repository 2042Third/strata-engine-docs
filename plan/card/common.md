# Card: every page

With `kind-<letter>.md`, `checks.md` and your brief `plan/briefs/<part>/<chapter>.md`. Ids are `tools/lint.py` rules.

## When texts disagree

The tools (`pagecheck.py`) win over this card, the card over the brief: no checkpoints in a patch tutorial; a
sketch's rules over a toy's line count; the glossary's homes over the brief's Items; a standalone sketch, not a
playground script, as a code solution.

## Reader

Write for the least prepared persona: B0 (track B), G0 (G), E1 (E, none). B0 and G0 know computers, games and school
arithmetic, no programming, 3D or terminal; E1 also wrote small programs, but knows no C++ beyond basics, linear
algebra, graphics or engines. Assume only that, the brief's Needs closure and this page's earlier sections.

## Language

- Sentences: mean ≤ 20 words per page (`sentence-mean`), none > 35 (`sentence-max`). Only ".", "?" and "!" end one:
  clauses joined by semicolons or colons in a list item are one sentence; a colon before a list ends one.
- ≤ 5 sentences per paragraph; a list item is a paragraph (`paragraph-length`).
- ≤ 500 words of paragraphs between headings, figures, fences, lists, tables, formulas or asides (`prose-run`).
- Inline code and math count one word. Asides, answers, table cells, captions and alts (figures, Mermaid) are prose;
  captions and alts are plain text: no backticks, bold, marks or engine names. A caption and its alt are one paragraph.
- An engine path starts at the engine's root (`Strata/src/Strata/Core/`, never `Strata/Core/`); a glob matches a file
  at the pin (`Strata/src/Strata/Core/*.h`) (`names`).
- A code span stays on one line: one broken by a line end is read as prose.
- Every prose word is on `tools/data/common-words.txt` (the 8,991 headwords of 12dicts' bands 1 to 14),
  `extra-words.txt` (units, school mathematics) or `names.txt` (one
  ending of -s, -es, -ies, -ed, -d, -ing, -er, -est, -ly removed), or is a word of a glossary name or
  alias (alone too, marked or not: "preset" of "CMake preset"), code, a bold UI label, a number or math
  (`word-list`). Check a doubtful word before writing it: `grep -iw '^<word>' tools/data/*-words.txt tools/data/names.txt`.
  The entries of `## Further reading` are not read. Otherwise use a common word or propose the term
  (`## New terms`); names and extra words: `## Requests`. Refused: movable, removable (can move, can be removed),
  iterable (a loop visits), wrapper (a class around), copier, intrusive (built into the type), metadata (data about),
  refactor (rewrite), deprecated, hardcoded (written into the code), getter, setter (a function that reads, sets);
  `emplace`, `Debug` as code.
- An acronym's first use stands beside its expansion: "graphics processing unit (GPU)" (`acronym`); exempt: KB, MB,
  GB, 2D, 3D, OK and the names of `tools/data/acronyms.json`. Quoted text is read; Further reading entries are not.
  A bold definition writes **graphics processing unit** (GPU), the acronym plain; a term mark ("graphics card" marked
  as GPU) is no expansion. Headings and bold are skipped: the first plain use, link text and tables too, expands.
- Never: simply, just, obviously, of course, clearly, basically, easy, easily, trivial, trivially, needless to say, as
  everyone knows, it follows, it is easy to see (`banned-word`).
- Never e.g., i.e., etc., vs., cf., approx.: for example, that is, and others, against, compare, about
  (`abbreviation`).
- No n't, 're, 've, 'll, 'd, 'm, it's, that's, there's, what's, here's, let's; "Strata's" is fine (`contraction`).
- Single verbs, also for "turn it on" (`phrasal-verb`): find out→learn, set up→create, carry out→do, come up
  with→invent, look into→examine, point out→show, figure out→understand, go on→continue, go back→return, get rid
  of→remove, turn on/off→enable/disable, put off→delay, make up→form, give up→stop, look up→find, fill in/out→complete,
  leave out→omit, pick up→take, speed up→accelerate, slow down→slow, break down→fail, show up→appear, end up→become, run
  into→meet, look for→search for, think about or take into account → consider, keep up→continue, kick off→start.
- No idioms (`idiom`, `tools/data/idioms.txt`: under the hood, on the fly, from scratch…).
- No paragraph starts with "It", "They", or "This", "That", "These", "Those" before a verb or punctuation
  (`pronoun-start`).
- Link text names its target, never "here" or "read more" (`link-text`). Page links are relative `.md` paths
  (`../basics/numbers.md`), never `/basics/numbers/` or `.mdx` (`mdx`).
- Sentence case (`heading-case`, warning); headings ≤ `####`, no math (`deep-heading`). Warnings:
  `passive` (say who acts), `noun-stack`.
- Never ten words in a row from `plan/inventory/*.md`, `AGENTS.md`, `Docs/DeveloperGuide.md`, `Docs/Manual/*.md`
  (`copied-text`). Exact words: a block quote ≤ 60 words whose source stands on a line of its own at its end: a `>`
  line, then `> — <source>` (`block-quote-length`).
- Present tense, active, "you"; "Strata stores…", not "we". Purpose before mechanism. Never a glossary `avoid` name
  (`other-name`).
- `\$5` for money (`dollar-digit`); `a::b` (`scope-in-prose`) and `Ref<Scene>` (`html-in-prose`) only in backticks; no
  HTML; no TODO, FIXME, TBD, XXX (`unfinished`).
- Engine names in backticks, UI labels bold, both as written (**File ▸ New Project...**); keys **Ctrl+Z**; names
  the reader makes (`Spinner`) as code; test names, section names and log text in backticks.
- `names` checks every dotted code span (`Group.Name`) as a section, test or property at the pin: one the pin lacks
  (yours, another product's) is plain text or stays in a fence.

## Terms

- Your brief's "Terms the glossary homes on this page" lists them (id, term, aliases). Define each once in **bold**,
  anywhere on the page, best where it is first needed, in one sentence saying what it is (`term-defined`); an alias
  or plural is the term. A use before it (test-out, a table) is no failure.
- Never read `src/content/glossary.json`. A term homed in your Needs closure gets its `:term[…]{id=…}` mark at its
  first use from `tools/markterms.py` (pagecheck runs it); write plainly. No mark is needed in a block quote, the
  test-out box, a Further reading entry, a sentence that links the term's home, or in or right after the sentence of
  your bold definition.
- A name with a qualifier ("Layer (architecture)") is defined and matched by its words before the parenthesis:
  **layer** or **layers**.
- A term homed outside the closure is neither marked nor linked (`term-source` warns of your own mark): say in the
  sentence what it is, and link its home where that helps.
- A one-word term of the common list (step, tool) stays unmarked; where the page means the term, write
  `:term[step]{id=step}`.
- Read each line markterms marked: reword a sentence whose marked word has another sense.
- markterms never marks a link's text, but `term-mark` reads it: where a term's first use would be link text, use
  the term in plain prose before the link.
- ≤ 1 new term per paragraph (`term-paragraph`), ≤ 4 per `##` section (`term-section`). A term you propose counts
  once the clerk admits it: give it its own paragraph and count it now.
- Bold outside steps is a new term: never bold a term homed elsewhere. Propose a term: define it in bold; add it to `plan/notes/<part>/<chapter>.md`, `## New terms` (term, one-sentence
  definition, this page as home, aliases).

## Mathematics

Order: idea and picture; small numbers by hand; formula, each symbol read aloud with its unit; code; a check at the
limits. `$…$` inline, `$$` on own lines.

- Each new symbol of a display formula stands as inline math in the paragraph right after it: "$d$ is the distance, in
  metres" (`math-symbols`). An environment (`\begin{pmatrix}`, `bmatrix`, `cases`) fails: its name's letters read as
  symbols. Write a matrix's rows as inline math or a table.
- ≤ 4 display formulas per `##` section outside `:::derivation` (`math-derivation`, warning).
- Track G, not primers: display formulas inside `:::note[The formula]` or `:::derivation`, after a paragraph stating the
  result in words (`math-g`).
- Say how each operator is read.

## Teaching loop

Per idea: Show; Name the term; Explain why; Code (pseudocode, a sketch, then Strata's); Check (a question, its
`:::answer`, no `tests`).

## Front matter

```yaml
---
id: core/time
title: "Time: delta time, the fixed step and time scale"
description: "Why a game measures the time of each frame."
kind: concept
size: L
tracks: [E]
needs: [core/frame-loop, basics/math-change]
time: 45
learn:
  - id: delta-time
    text: explain why a game scales movement by the frame's delta time
since: 0.3.0
status: draft
---
```

- `id` is the path under `src/content/docs/` (`id`); `title` (quoted), `kind`, `size`, `tracks`, `needs` are the
  brief's row (same rule ids): the brief's title, whatever your task calls the page. Kinds: primer, concept,
  internals, tutorial, how-to, reference. Tracks `[]` for none; needs `a|b`, `[]` for "-".
- `description`: one sentence ≤ 160 characters, double quotes (`description`).
- `time` ≥ floor (prose words/120 + code lines/10, up to a multiple of 5); concept and internals ≤ 2 × floor
  (`time`).
- `learn`: 2–5 `{id, text}`, text starting with explain, compute, name, choose, write, build, find, predict, change,
  add, fix, trace, measure, compare, draw, export, create, run or set (`learn`).
- `since`: 0.3.0–0.8.0, only on concept, internals, tutorial, how-to pages of `make` and all parts `core` through `engineering`; a
  subject older than the first tag is 0.3.0; evidence in the notes' `## Since` (`since`).
- `status: draft` (`status`); no other key (`front-matter`), no `head` (`front-matter-head`).

## Strips

The build writes the top strip and box titles; you, the bottom strip:

- `## Summary`: one bullet per learn line, in order.
- Questions and exercises are numbered items, each followed by `:::answer{tests="<learn ids>"}`; every learn id is in
  a Check-yourself answer's `tests`.
- Exercises start **Basic.**, **Medium.** or **Hard.**, never going down (`exercise-order`).
- `## Further reading`: per source, what it gives and its level (beginner, intermediate, advanced). Link only hosts of
  `tools/external-hosts.txt`; cite another source without a link and ask for its host under `## Requests`.

## Code

- Fences name a language: `cpp`, `slang`, `json`, `cmake`, `sh`, `powershell`, `python`, `text`, `diff`, `mermaid`
  (`no-language`); C++ and shader fences are quotes, sketches or `pseudocode` (`unlabelled-code`).
- Write a quote with an empty body; pagecheck fills it; never type or edit one:

  ````md
  ```cpp src="Strata/src/Strata/Scene/Scene.cpp#Scene::OnUpdateRuntime" from="m_FixedTimeAccumulator += deltaTime;" to="steps++;"
  ```
  ````

  The symbol is a function (`Class::Function` or a free one); without `from`/`to`, all of it; each occurs once in it. Types, any lines:
  `src="<file>#L<a>-L<b>"`, empty body. Also `overload="2"`,
  `src="<file>" command="<group.action>"`, `mark="L<n>,L<a>-L<b>"`, `vendor:<lib>/…`, and
  `book:<path>#L<a>-L<b>` (the range is required).
- Quotes 5–60 lines (`long-quote`), the first and last holding code (`excerpts`). The brief's line numbers are hints: recheck them at the pin, and split a longer
  quote into two with text between. Your page's level: 1 when its whole Needs closure lies in `start`, `make` and
  `basics`; 3 when it holds a page of `assets` or a later part other than your own; else 2. On a level-1 page, any
  track, and on every page of track G or B, every fence (answers, solutions, a sketch's whole file) holds ≤ 25 lines,
  blank and comment lines included.
- Before a fence, a paragraph says what it does and what to look for (`code-intro`), right before it: a `:::question`
  stands before that paragraph. After it, a paragraph or numbered callouts (`code-follow`), never a figure, `:::question` or heading. Only a sketch's
  `output-of` fence may follow its fence directly: between a command's fence
  and a fence of its output stands a paragraph.
- Fences ≥ 10 lines (not outputs): then 1–5 callouts, a numbered list right after the fence with nothing between
  (a sketch's output fence follows the sketch directly, also in an answer, and the list follows the output), each item
  starting **Line N:** or **Lines N–M:** and saying why (`callouts`); in a step or an answer the list nests inside it;
  paragraphs starting so fail. A quote's callouts count its file's lines: `excerpts fill` rewrites a symbol quote into
  `src="<file>#L<a>-L<b>"`, numbered from a on the site; write them after that fill: the lint reads the page before the
  run's quote fill, so its line numbers shift. A sketch and a `#hunk-<n>` diff count from 1.
- C++ taught outside the Needs closure needs a `:::question` before its first fence, ≤ 2 sentences, linking every
  home the `cpp-feature` finding names (one finding per fence names them all): int, if, `=` → `basics/programming-1`;
  loops, functions, `return`, `struct`, `std::vector` → `-2`; classes, any call `a::b(`, `x.f(` or `p->f(` (so
  `glm::length(`, `std::printf(`), references, `#include` → `-3`; pointers, `nullptr`, `Ref` → `basics/cpp-memory`;
  inheritance, `virtual`, `override` → `basics/cpp-classes`; templates, lambdas, maps, algorithms →
  `basics/cpp-generic`; `std::move`, `constexpr`, `std::optional` → `basics/cpp-modern`; threads, atomics →
  `basics/threads`. Sketches, answers and engine quotes are read too (`const char*` is a pointer).
  No finding, no question.
- Sketch: your file `sketches/<part>-<chapter>-<name>.cpp`, a standalone C++20 program (glm available; no Strata or
  script API), with empty fences ```` ```cpp sketch="<file>" ```` and ```` ```text output-of="<file>" ````:
  `pagecheck.py <page> --fill-sketches` copies the file and its real output in. `sketch=` takes the bare file name; an
  answer's `solution="sketches/<file>"` takes the path. Minimal, Hazel style, warning-free;
  script code is `pseudocode`.
- Compile through pagecheck only: it finds MSYS2's g++ beside Python; `sketches.py` alone or `g++` in the Bash shell
  find none. Flags: `-std=c++20 -Wall -Wextra -Werror`, so initialize every field of an aggregate you brace.
- Explain Python line by line. Output is real: a sketch's, or ```` ```text capture="<figure id>" ````.
- Commands: their JSON and the UI path; never tell game makers to edit `.stscene`, `.stmat`, `.stproj` or `.meta`.

## Steps

Tutorials; how-tos on G or B (`step-parts`):

- One numbered list in `:::::steps` … `:::::`. Each step: the action in `::::tabs{sync=how}` (`:::tab[In the editor]`,
  `:::tab[With a command]`), then **You should see:** and **If you do not see it:**, optionally **Why:**.
- In a step, every bold span is read as a label of Strata's editor (`names`): start a step with a plain sentence, and
  write another program's labels in quotes ("Go to Definition"), outside steps too. Bold there only the editor's
  labels, keys
  (**Ctrl+P**, **Enter**) and glossary terms; a label your script makes (a field's) as code, `Is Gold`, and so are names and values (`Coin`, `Top Left`); define a new
  term outside the steps.
- No menu or button: start "This step has no menu or button: run the command."; the closure holds
  `make/automated-playtests` or `make/commands` (G, B) or `editor/commands` (E).
- OS steps: `::::tabs{sync=os}`, tabs `Windows`, `Linux`, `macOS`. A fence in a tab is introduced by a paragraph before
  the tabs or in a sibling tab; after it, a paragraph in the same tab, except in the last tab, whose fence the
  paragraph after the tab set follows.

## Figures

- Ask for a picture in `src/content/figures/<part>/<chapter>.json`, under `figures`: `id`, `shows` (one
  sentence), `caption` (what to notice), `alt` (what it shows), `kind` (`scene`, `live`, `editor`, `runtime`, `text`,
  `reference`, `tool`, `diagram`) and the recipe (`project`, `camera`, `setup` steps, `editorWindow`, `text`).
  Place it: `::figure{id=…}`, `::compare{id=…}`; a recipe with `variants` (two or more) is
  placed with `variant=<name>`, and so is its `capture=` fence.
- Captions and alts follow the paragraph and sentence rules. A caption writes no number but `{stats.<name>}` of a
  recorded value.
- `waitsFor` only for a picture the pin cannot take yet: `tier 1: capture complete`, `tier 1: command details`,
  `tier 1: asset types`, `tier 1: window size`, `tier 2: editor screenshot`, `tier 2: renderer switches`,
  `tier 2: debug view <specular|diffuse|clusters|culled|wireframe>`, or `tier 3: <capture>; <why no debug view shows it>`.
- Editor figures name a `project` (the welcome window has no picture). A `text` capture is a command's result
  (`command`, `keep`) or the output of `StrataEditor`, `StrataRuntime`, `StrataCLI` or `ctest` of the pin's build:
  never CMake, a compiler or a patched build.
- Never take pictures or start an engine program.
- A page whose pictures are all Mermaid diagrams has no figures file.
- Diagrams: ```` ```mermaid caption="…" alt="…" ```` (keywords as names get aliases), or your SVG
  `src/assets/figures/<part>/<chapter>/<id>.svg` with a `diagram` entry. No pictures from other engines or books.
  No check reads Mermaid node labels (engine and file names may stand there); the lint reads caption and alt.
- An editor figure's window layout (`layouts/<name>.ini`) is the planner's: name the layout it needs under
  `## Requests` and keep the entry.

## Directives

`:::note`, `:::tip`, `:::caution`, `:::danger`: extra, practice, mistake, data loss; `:::why`: a design decision;
`:::question`: a reader's question; `:::history`: what Strata did before; `:::elsewhere`: other engines, cited;
`:::rule`: a rule of `AGENTS.md`, its reason, a link; `:::simplified`: what is left out, with a link
(`simplified-link`);
`:::analogy`: last paragraph starts **Where it breaks:** (`analogy-limit`); `:::example`: worked example;
`:::derivation`: skippable, no label; `:::files[…]`: file tree; `::checkpoint{stage=N}`; `:since[0.8.0]`: new section;
`:value{key="…"}`: a key of `src/generated/reference/values.json`. Labels in brackets; a block holding blocks takes one more colon.

## Numbers and honesty

- Units with a space (16.7 ms, 19 %). Track G: a time in ms gives its share of a frame at 60 frames per second, "%"
  in the same sentence (`g-frame-share`: paragraphs, items, answers, asides, captions, quotes; not table cells).
- W8r pages: no number beside Low, Medium, High, Ultra (`w8r-preset`). Counts the engine can change:
  `:value{key="commands.count"}`.
- "At the pin" is engine commit `822a7a46` (release 0.8.0, prerelease; its programs report 0.7.0). Claims about Strata
  hold there, name the file, and were checked in the clone; code beats inventories and docs. Unverified: notes,
  `## Not verified`.
- Never false to simplify (`:::simplified`) or promising what Strata lacks; cite claims about other engines.

## Size

Prose words (`size`): S 600–2,250; M 2,251–4,000; L 4,001–6,500; XL 6,501–10,000; none for reference. Every pagecheck
run prints `words: <n> prose words; size <S> holds <a> to <b>`. Plan before writing: the pilot's first drafts ran 20 %
over. Its pages spent answers 7–12 % (60 words a Check or Exercise answer, 30 a try-it), asides 3–14 %, captions and
alts 60 a figure, a callout 22, the strip without answers 500–800; body text kept 53–74 %. Aim at the range's middle:
budget those first, the body gets the rest.

## Never

Mention how the book is made, or write the pin's commit or release as the book's state; short hashes of past engine
commits may stand where history or an exercise needs them.
