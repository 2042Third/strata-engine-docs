# Brief: `reference/term-index`

| Field | Value |
| --- | --- |
| Title | Index of terms and engine identifiers |
| Kind | R |
| Size | XL |
| Tracks | - |
| Needs | - |
| From | new; generated from the glossary's home pages and the excerpt fences' symbols, so a reader finds the page that defines a name; not `reference/index`, which is the part's generated map |
| Unit | `plan/allocation/reference.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `reference/term-index` — Index of terms and engine identifiers

**Covers.** The paragraph on top says what the page is: an index that sends a reader from a name to the page that
defines it, generated from two sources, and how it differs from the glossary (no definitions, only places) and from
`reference/index` (the part's generated map). (1) Terms: every glossary entry with its home page and use home,
alphabetical, with its aliases pointing to the same entry. (2) Engine identifiers: every symbol that the excerpt
fences of the book name (classes, functions, macros, commands, settings sections, files), from the fences' `symbol`
attributes, which `excerpts.py fill` writes (`../pipelines.md` §3), each with the page whose excerpt quotes it first and
the other pages that quote it, so that a reader with `Scene::OnUpdateRuntime` or `ST_CORE_ASSERT` finds where the book
shows it. The two lists share one alphabet, each entry marked as a term or an identifier. Hand-written: the paragraph on
top and `## Where it lives in Strata`. The tool is `tools/reference.py render`, route "terms" (`../pipelines.md` §7.1),
which reads `src/content/glossary.json` (its entries' terms, aliases, `home` and `use`) and the `symbol` attributes of
the pages' quotes, so it runs after `excerpts.py fill`; the search test of `../site.md` expects a concept's home among
the first results, and this page is the fallback.

**Leaves out.**

- The definitions → `reference/glossary`
- The full facts of each identifier → `reference/script-api`, `reference/commands`, `reference/components`,
  `reference/settings`, `reference/core`

**Fit.** `fits`: about 350 words against XL (8,000). The generated index gives the page its size: about 2,000 terms and
several thousand identifiers, roughly 20,000 words of names and links, fewer bytes than the glossary, whose size the
spike measured within the largest-page budget. The prose is the paragraph on top and the strip.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `animation:527-589` | term | link | The 63 terms of the animation glossary, each with its home page |
| `assets:637-737` | term | link | The 101 terms of the assets glossary, each with its home page |
| `audio-input:606-693` | term | link | The 87 terms of the audio-input glossary, each with its home page |
| `automation:703-786` | term | link | The 81 terms of the automation glossary, each with its home page |
| `build-test:609-698` | term | link | The 84 terms of the build-test glossary, each with its home page |
| `editor-core:648-740` | term | link | The 93 terms of the editor-core glossary, each with its home page |
| `editor-ui:700-794` | term | link | The 88 terms of the editor-ui glossary, each with its home page |
| `foundation:548-645` | term | link | The 94 terms of the foundation glossary, each with its home page |
| `gamedev:569-665` | term | link | The 97 terms of the gamedev glossary, each with its home page |
| `gameui:617-685` | term | link | The 69 terms of the gameui glossary, each with its home page |
| `physics:477-541` | term | link | The 65 terms of the physics glossary, each with its home page |
| `render-core:679-775` | term | link | The 89 terms of the render-core glossary, each with its home page |
| `render-direct:671-758` | term | link | The 88 terms of the render-direct glossary, each with its home page |
| `render-image:634-736` | term | link | The 101 terms of the render-image glossary, each with its home page |
| `render-indirect:564-650` | term | link | The 87 terms of the render-indirect glossary, each with its home page |
| `render-scene:569-654` | term | link | The 86 terms of the render-scene glossary, each with its home page |
| `scene-ecs:611-693` | term | link | The 80 terms of the scene-ecs glossary, each with its home page |
| `scripting:557-621` | term | link | The 58 terms of the scripting glossary, each with its home page |
| `worlds-runtime:513-568` | term | link | The 56 terms of the worlds-runtime glossary, each with its home page |
| `animation:334-365` | code | link | The identifiers of the 31 excerpts of the animation inventory, each with the page that quotes it |
| `assets:375-444` | code | link | The identifiers of the 34 excerpts of the assets inventory, each with the page that quotes it |
| `audio-input:376-408` | code | link | The identifiers of the 32 excerpts of the audio-input inventory, each with the page that quotes it |
| `automation:458-520` | code | link | The identifiers of the 32 excerpts of the automation inventory, each with the page that quotes it |
| `build-test:378-411` | code | link | The identifiers of the 34 excerpts of the build-test inventory, each with the page that quotes it |
| `editor-core:381-450` | code | link | The identifiers of the 35 excerpts of the editor-core inventory, each with the page that quotes it |
| `editor-ui:429-466` | code | link | The identifiers of the 38 excerpts of the editor-ui inventory, each with the page that quotes it |
| `foundation:342-373` | code | link | The identifiers of the 31 excerpts of the foundation inventory, each with the page that quotes it |
| `gamedev:359-388` | code | link | The identifiers of the 30 excerpts of the gamedev inventory, each with the page that quotes it |
| `gameui:394-425` | code | link | The identifiers of the 31 excerpts of the gameui inventory, each with the page that quotes it |
| `physics:296-325` | code | link | The identifiers of the 30 excerpts of the physics inventory, each with the page that quotes it |
| `render-core:442-474` | code | link | The identifiers of the 33 excerpts of the render-core inventory, each with the page that quotes it |
| `render-direct:433-469` | code | link | The identifiers of the 37 excerpts of the render-direct inventory, each with the page that quotes it |
| `render-image:395-426` | code | link | The identifiers of the 31 excerpts of the render-image inventory, each with the page that quotes it |
| `render-indirect:338-367` | code | link | The identifiers of the 30 excerpts of the render-indirect inventory, each with the page that quotes it |
| `render-scene:341-373` | code | link | The identifiers of the 32 excerpts of the render-scene inventory, each with the page that quotes it |
| `scene-ecs:373-407` | code | link | The identifiers of the 35 excerpts of the scene-ecs inventory, each with the page that quotes it |
| `scripting:354-387` | code | link | The identifiers of the 34 excerpts of the scripting inventory, each with the page that quotes it |
| `worlds-runtime:308-338` | code | link | The identifiers of the 31 excerpts of the worlds-runtime inventory, each with the page that quotes it |

**Assumes.**

none

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

None: the glossary homes no term on this page.

## Open findings of the completeness critic that name this page

Each is checked against the engine at the pin and applied where it holds; the page's writer reports the ones it
did not apply, with the reason.

| Id | Severity | Kind | Where | Finding | Proposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| critic-reference-19 | could | missing-item | `reference/term-index` | The index reads only the glossary and the `symbol` attributes of quotes, so a name that appears only in a generated catalogue (a command, a component property, a settings section, an SDK function, a program or CMake option, an environment variable) has no entry, though the page exists to send a reader from a name to its page. | Route "terms" also reads the dumps and the parsed tables and gives each such id an entry that points to its catalogue anchor and to the teaching page that the catalogue row names. No prose added; `../pipelines.md` §7.1, row "terms", says so. | `allocation/reference.md:1329-1340`; `../pipelines.md:1102` |
