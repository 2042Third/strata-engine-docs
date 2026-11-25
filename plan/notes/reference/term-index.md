# Notes: reference/term-index

## New terms

None.

## Requests

- The route "terms" of tools/reference.py does not exist at the pin of the tool chain, and src/generated/reference/ holds no index file. The table is written by a script (docs-work/pages/reference-term-index/build.py) from the glossary and the quotes' symbols. A route that writes it, with the catalogue entries of critic-reference-19, should replace it.
- Size: the page counts about 16,000 prose words against XL; the lint's size is a known fault for a generated index.

## Hand-written tables

- The whole index table: read from src/content/glossary.json (terms, aliases, home, use), the fences of src/content/docs/**/*.md (`symbol=` or a `#Symbol` in `src=`) and src/generated/outline.json (titles, order). It lists only the pages that exist now; run build.py again after the later pages land.
- v0.8.0 pin move (pin 319075e3): table rebuilt by docs-work/pin-move/term-index/build.py (build2.py's rules, keeping the page's prose and its id-written titles) from the glossary, fences and outline as they stood then: 46 rows added (the appendix networking and game AI terms, the joined sub-scene entry, `GetEditorArguments`), 2 removed (the old sub-scene lines). The strip's `Strata/src/Strata/Scene/Scene.cpp` exists at the pin. Pages revised for the move after this rebuild are not in it: run the script again once they land.

## Not verified

Nothing about the engine is stated beyond the strip's file path.

## Findings not applied

- critic-reference-19: names that stand only in a generated catalogue (commands, properties, settings, SDK functions, options) have no row, because their route does not exist yet.

## Clerk

- Left for the planner: the route "terms". Tool: the lint's size rule no longer fires on a kind R page (R37).
