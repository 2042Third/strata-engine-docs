# Notes: start/how-to-read

## New terms

None. The nine terms of the brief are defined in bold on the page: reading track (introduction), source code,
programming language, comment, pseudocode (section "How to read code you do not understand yet"), primer (step 2),
engine release (step 4), prerequisite (step 5), tutorial checkpoint (step 6).

## Requests

- Word: "Glossary" (the title of `reference/glossary`, used as link text in step 7). Add it to `extra-words.txt`; its
  `word-list` failure is the page's only open finding.
- Host: `developer.mozilla.org` for the Further reading entry "Working with JSON" (cited without a link).

## Not verified

- The track chooser, the kept tab choice, the term popover and the print view are read from the site's code
  (`src/components/`, `src/plugins/`, `src/lib/`); no browser was run.
- The site keeps archived editions at `<base>/v<major>.<minor>/` only in its deploy rules; whether an edition for
  release 0.8.0 exists is not known, so the page says "when the site keeps one".
- `StrataCLI call` with a quoted `@params.json` in Windows PowerShell and the piped `-` form are read from
  `StrataCLI/src/CLI/CliApplication.cpp` and the critic's finding; no program was started.
- The search result shows the part and kind beside the title (`src/lib/search.mjs`); the filters by part, kind and
  track exist as data but the page does not claim that the search box shows them.

## Findings not applied

None: critic-start-1 (OS tabs, `@params.json` quoted in PowerShell, `-` form, UTF-8, what `StrataCLI` is),
critic-start-12 (`## Result` and `## Variations` with search, print view, other release), critic-start-14 (macOS
Command key sentence in step 6) and critic-start-16 (the Cube command with three components) are applied. The Cube's
`Transform` place is explained as the Scene view's look (`SceneHierarchyPanel.cpp` `CreatePreset`).

## Clerk

- `extra-words.txt`: "glossary".
- `external-hosts.txt`: `developer.mozilla.org` (front page fetched: MDN Web Docs).
