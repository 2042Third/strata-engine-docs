# Notes: engineering/ci

## New terms

- workflow: a file in `.github/workflows/` that names the events that start it and holds jobs of steps (home: engineering/ci; aliases: GitHub Actions workflow). Defined in bold on the page.

## Requests

- Word list (`tools/data/extra-words.txt`): "workflow" (8 uses; the proposed term above).
- The glossary entry "`ci/<name>` branch" (id `ci-name-branch`) cannot be satisfied by the lint: its name mixes code and words, so `term-defined` finds no bold definition whether the page writes it as bold code (**`ci/<name>`** branch) or as plain bold. Ask the planner to give the entry a code-only name or alias such as `ci/<name>`.
- Further reading cites GitHub Docs pages and the ccache, sccache and Ninja manuals without links; the host docs.github.com is not on `tools/external-hosts.txt` as far as checked (only github.com was seen).
- Figure not drawn: the brief's picture of GitHub's pages (a CI run, an annotation in a pull request, a release page) needs GitHub access and no recipe can capture it; the page has Mermaid diagrams only (no figures file).
- The page links `../engineering/releasing.md` nowhere; it does not mention the release workflow.

## Since

0.4.0: the compiler cache in Actions and `Tools/CIStatus.py` arrived in wave 4 (plan/inventory/build-test.md, "Arrived" column: cache 0.4.0; CIStatus wave 4 step 0; Windows Debug and the Dist job wave 4).

## Not verified

- "Apple Clang 17" for the macOS job and the Apple Clang 15 history come from `Docs/DeveloperGuide.md`, not from `ci.yml` (which only names `macos-15`).
- The incident of wave 3 (a Dist break) comes from the comment in `ci.yml` and the inventory, not from the history.
- Which tests also run in each job (`StrataShaders.TargetHLSL`, `StrataTools.LookDevOffline`) is the developer guide's statement; the page attributes it to the guide.
- The cache arithmetic uses the measured sizes in the comments of `ci.yml`; the 10,240 MB figure is 10 GB counted in 1,024-MB units, an assumption about how GitHub counts.

## Findings not applied

- The brief's picture of GitHub's pages (`build-test:467`): not drawn, see Requests.
- `Tools/CompatLint.py` appears only in the "Where it lives" list and the rule box, as the brief says (link role).
- The brief's "workflow of ten lines": the toy has 13 and 16 lines in two fences so that it can show the trigger, the matrix and the test condition.

## Clerk

- Admitted the term workflow (aliases workflows, GitHub Actions workflow), homed here; it also lets engineering/releasing use the word.
- Admitted to external-hosts.txt: docs.github.com (GitHub's documentation).
- The entry `ci/<name>` branch (id ci-name-branch) now has the code alias `ci/<name>`, so the page's **`ci/<name>`** defines it (a bold code name defines a term); its definition is the page's sentence.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
