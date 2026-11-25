# The plan of the Strata Engine Book

This folder is the plan of the book: what it contains, how it is written and checked, and how the site is built and
deployed. It is written for the agents and people who make the book. Readers never see it: the site does not publish
`plan/`.

## Files

| File | What it decides or holds |
| --- | --- |
| [book.md](book.md) | The readers and personas, the tracks, the kinds of page, the parts, one home per concept, the design decisions taught as decisions, what Strata does not do, the running examples |
| [outline-1.md](outline-1.md) … [outline-4.md](outline-4.md) | Every page: id, title, kind, size, tracks, Needs, sources and marks, in 25 parts. `outline-1.md` gives the rules of the tables |
| [tracks.md](tracks.md) | The three reading orders G, B and E, each as a numbered list of page ids |
| [check_outline.py](check_outline.py) | Checks the outline against its rules, the rulings and `tracks.md`, the writing waves against the Needs, and the counts that `book.md`, `process.md` and this file state. Run `python plan/check_outline.py`; `--counts`, `--words` and `--waves` print the counts |
| [style.md](style.md) | How a page is written: the personas' exact knowledge lists, the language rules the linter measures, terms, mathematics, front matter, the shape of each kind, questions, code, steps, figures, numbers |
| [site.md](site.md) | The web project: framework and versions, the base path `/strata-engine-docs`, the Markdown, plugins, checks, the budgets and the spike, deployment, versions, CI |
| [pipelines.md](pipelines.md) | The engine at the pin; quotes, sketches, pictures, tutorials, the generated reference, the names lint, the glossary, moving the pin, the engine additions of v0.8.1, files and who writes them |
| [process.md](process.md) | The roles, what a writer is given, the stages of a page, the provenance check, track walks, who writes and commits what, the order of the work, not interfering with the engine's work, the budget, the definition of done |
| `inventory/` | What the survey found in each of the engine's 19 areas, at engine commit `822a7a46` |
| `research/` | The studies behind the framework, the teaching method and the capture method. Background only: where a study says otherwise (for example `research/framework.md` §5, a complete configuration written before the plan), `site.md` and `pipelines.md` decide (`site.md`, "Where this file overrides the research") |
| `critique/` | The ten critics' reports; `summary.md`, which merges them; `rulings-1.md` to `rulings-10.md`, the planner's decisions (a later file wins over an earlier one), which win over the summary and the critics; `dispositions.md`, one row per finding: accepted, accepted with the option named, or rejected with the reason, and where it landed |

Made during the work (process.md, "Files and who writes them"): `spike-report-1.md` (the first spike's report, which
`critique/rulings-5.md` judges), `spike-report.md` (the completed site's), `allocation/`, `briefs/`, `notes/`,
`reviews/` and `walks/`.

## Decisions at a glance

1. **One book, three tracks.** G (game maker): `start`, then `make`, stepping into the programming primers. B
   (beginner): `start`, block A of `make` with the first primers between its pages, then the rest of `basics`; then
   track G or track E. E (engine builder): `start`, `basics`, then the engine parts in order. The personas G0, B0 and E1
   are exact knowledge lists (style.md); a page is written and reviewed for the least prepared persona of its tracks.
2. **Programming and mathematics from zero are in the book**: the 30 primers of `basics`, each with a Test out box. The
   programming primers use a Strata script as the playground, so no second toolchain is needed.
3. **The outline is checked.** 335 pages in 25 parts (0 to 24). Every page has its tracks and at most five page ids
   in its Needs, and each Need comes earlier on every track of the page. `check_outline.py` proves it, and that the
   counts this plan states are the outline's.
4. **Six kinds of page**: primer, concept, internals, tutorial, how-to, reference. The 17 parts of eight or more pages
   also get a generated index page and review page.
5. **One home per concept** (book.md). Two running examples: Coin Run (track G, block A of `make`) and WindZone (track
   E, from `world/tutorial-component` to the capstone).
6. **The engine is the source of truth.** Code is quoted from the engine at a pinned commit, and a check fails when a
   quote no longer matches. Pictures are rendered by the engine from recipes kept in this repository. Tutorials are run
   against a build of the pin. Reference pages are generated, or parsed from the source and checked.
7. **The engine at the pin** is one separate clone, built once per pin in Release. In phase A editors run `--no-gpu`,
   one at a time, under the engine's perf lock. No docs agent touches the engine's own worktrees.
8. **The book targets engine release 0.8.0; its final pin is v0.8.1.** Text is written against `822a7a46`. The seven
   W8 pages (local lights and their shadows, area lights, global illumination, and the `make` pages on lamps and GI)
   are written after 0.8.0; the seven W8r pages have one named section revised then. The capture additions ship in
   v0.8.1, made by the engine's agents.
9. **Pictures.** The repository commits the published files (renders as AVIF; crops and pictures of the interface as
   lossless WebP) and their recipes. The PNG originals of a book release go into an archive attached to that release.
   "Before" pictures come from the engine's look-dev baseline sets of older releases. They are not committed in the
   engine repository; the planner copies them once to `docs-baselines` (pipelines.md §5.5).
10. **The site** is Astro Starlight, built to static files that work under `/strata-engine-docs`. nginx serves it, as
    files copied into the host's nginx or as a container behind it, at `https://pdm.pw/strata-engine-docs/`, an
    address written once, in `site.json`, so that it can move. Caddy is not supported (`critique/rulings-6.md`, R23,
    R24). The spike passes only when every row of site.md's budget table passes. A row that still fails after its
    remedy fails the spike, and then the fallback is built and measured against the same table before any page is
    written.
11. **Review.** A technical review against the code at the pin, and a provenance review against the persona's list and
    the Needs closure ("used but not taught" cannot be rejected). Track walks test G after wave 2 and G and E at the
    end. A pilot of seven pages comes first, then six waves in Needs order, then phase B.
12. **Who.** The plan, the rulings, the briefs and the judging of samples are the orchestrator's; every other role is an
    Opus agent. Readers are modelled by personas and agents. The owner is invited to give the book to a real beginner
    and to walk one tutorial by hand; nothing waits for either.
13. **Closed source.** The book is the owner's work, all rights reserved: its text, pictures, diagrams, sketches,
    tutorial files, labs, downloads and the site's own code and tools. No open license covers it, and nothing invites
    copies or contributions. One permission lets readers use and ship the book's code in their own programs and games;
    third-party material keeps its own terms and notices (`critique/rulings-6.md`, R20 to R22).

## State (2026-11-10)

- The survey is done: 19 inventories and three studies, at `822a7a46`.
- The critique is done: ten critics, merged in `critique/summary.md` (8 blockers, 62 major and 41 minor findings).
  The planner ruled (`critique/rulings-1.md` to `rulings-3.md`), and the plan's files are revised by the rulings.
  The planner then read the revised plan and decided what was left open (`critique/rulings-4.md`).
- The owner decided the book's license and where the site lives (2026-11-10): the book is closed source, all rights
  reserved, and nginx serves it at `https://pdm.pw/strata-engine-docs/`. The planner ruled on what follows
  (`critique/rulings-6.md`), and the plan's files are revised by that ruling.
- The outline is final: 335 pages; `check_outline.py` passes.
- The spike is built in this repository (the pinned toolchain, the Markdown plugins, the site under its base path, the
  tools, sample pages, the browser checks, and deployments tested with nginx). Measured at the book's size, the
  framework passes (`critique/rulings-5.md`): the fallback is not built. The site is being completed to meet site.md
  ("The spike against this file"); its report measures every row of the budget table.
- The allocation is being written (`allocation/README.md`): every item of the inventories gets one home page.
- No page of the book is written. The spike's sample pages show the site's features; they are not reviewed pages.
- `engine.pin` names `822a7a46` (release 0.8.0, prerelease).

## Next steps

1. The spike's verdict (site.md, "Budgets and the spike").
2. The pin build and the tools (pipelines.md §1 and §13), beside step 1.
3. The glossary seed: 400 entries of a beginner's vocabulary.
4. The allocation of every part, and the completeness critic.
5. The glossary, once the allocation is settled (`critique/rulings-7.md`, R33 and R35). The inventories' terms, about
   1,590 (R40), join the seed, one entry per term. Where the seed has the term, the seed's entry wins. A `make`
   page is the `use` of its twin's entry: a term homed on a `make` page and its twin, the same term with the same
   meaning homed on another page, are one entry, whose `home` is the other page. Otherwise the home is the term's row
   in `book.md`'s one-home table, or, by the principle of `critique/rulings-7.md`, R28, the page in the Needs closure
   of every page that marks the term. A word with several meanings gets one qualified entry per meaning (`book.md`,
   rule 6); the candidates are the homonym groups of `G:/GameEngineAI/.worktrees/docs-work/B/duplicates/judge_c.txt`
   and the critics' lists of such words (`allocation/completeness.md`).
6. The part briefs. A page with a "Check:" item gets no brief until the check's result has replaced the item
   (`critique/rulings-7.md`, R34). The four checks that the engine's agents run are the exception: their pages are
   briefed and written from the code at the pin, and say that it was read, not run (`critique/rulings-9.md`, R39).
7. The pilot of seven pages.

Then waves 1 to 6 and phase B (process.md, "Order").

## Open questions for the owner

None of these holds the work back (`critique/rulings-6.md`, "For the owner"). The owner answered one more on
2026-11-10: the docs repository is public for now, and pushing is allowed (R27).

| Question | Until answered |
| --- | --- |
| Whose name stands in the copyright line? | `2042Third`, in `site.json` (R20) |
| Is R21's permission for the book's code the one the owner wants? | R21 as written |
| Copied files or the container on `https://pdm.pw`; and what does `nginx -V` print there? | both ways are tested; copied files are recommended (R23) |
| Under what terms may people use the engine? Its repository has no license file. | the book says only what the engine's repository says |
