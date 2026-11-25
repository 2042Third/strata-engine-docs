# Notes: engineering/look-dev

## New terms

None proposed. The page defines look-dev, look-dev harness and signed difference image (glossary homes).

## Since

- since 0.7.0: the harness and its shots are listed at 0.7.0 in the render inventories (Docs/DeveloperGuide.md "Look-dev harness" at the pin).

## Requests

- Figure `compare-page` (tool): the index.html of `Tools/LookDev.py compare` for one pair; not taken (tier 3, kept as `waitsFor`); the drawing `compare-layout` stands in.
- Further reading entries cite the Python documentation, the PNG specification and image-testing literature without links.

## Not verified

- The Alternatives table's "Who uses it" cells are general practice, not checked against named products.
- The shots table's descriptions of `tp.feet`, `tp.sign`, `tp.lantern` and `ow.water` rest on the shot names and crops, not on their scenes.
- Whether wider GPU or driver differences break golden images is stated as general practice, not measured at the pin.

## Findings not applied

- The brief lists no open findings.
- The brief's 150-word trace exercise and the Exercises are written; the capture-twice exercise was not run (no engine program is started).

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `compare-page` (tool) still waits: no take of the pin's picture tool shows a page that a tool writes (the kinds take the editor's viewport, the editor window, a game or a program's text). Its caption claimed the before and after pictures beside the difference image; at the pin, `compare_command` puts only the absolute and signed difference images in a picture's section, and the before and after appear only as side-by-side crops. Its shows, caption and alt now follow the code; `waitsFor` is kept as the request, `standIn` is `compare-layout`.
- `compare-layout` (diagram) stands in: the page's layout as `compare_command` and `write_index` build it, with the section titles as written, the gains 8 and 32, the crops section and both tables; counts and cells stay names, since no run was made. Purple notes name the folders and are marked in the caption as not on the page. The page's paragraph gained one sentence that introduces it.
