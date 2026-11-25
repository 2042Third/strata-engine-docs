# Notes: editor-ui/widget-kit

## New terms

- None proposed. The page defines the brief's eleven terms (widget kit, InvisibleButton, item probe, chip, chip strip, pill, banner, card, entry card, section header, nfd) in bold.

## Requests

- Extra word: "toolbar" (8 uses; the Scene view's toolbar). The page fails `word-list` on it only.
- Figures: the Scene view's toolbar wide and narrow needs layouts `layouts/scene-toolbar-wide.ini` and `layouts/scene-toolbar-narrow.ini` (the narrow one needs a Scene view of about 600 pixels). The brief's zoomed crop of the kit (editor-ui:547) is not requested: no recipe can show a crop of the widgets yet.
- The Mermaid diagrams (anatomy, two frames) carry no figure entry.
- Further reading names Dear ImGui's wiki and Game Programming Patterns without links; no host request.
- The exercise "Hard" is a paper exercise with a worked answer; no sketch or patch accompanies it.

## Figures

- scene-toolbar (editor, two variants): published at the pin v0.8.0 (319075e3) in one take, `waitsFor` removed. The wide picture (950 × 120) shows the eleven labeled chips in one row, Camera to Game camera, none cut; the narrow one (300 × 200) shows every chip as an icon, seven on the first row and four on the second, as caption and alt say. Earlier rounds below were taken with the provisional build. Both variants picture the `Viewport` panel in a 1280 × 720 window; the layouts made for it change only the Scene view's size (copies of `layouts/scene-view.ini`).
- Round 1: `scene-toolbar-wide.ini` (Scene view 1076 × 200) showed all eleven chips labeled in one row, but at 71 % of its pixels in the column; `scene-toolbar-narrow.ini` (Scene view 300 × 200) showed every chip as an icon, seven on the first row and four on the second.
- Round 2: the wide Scene view is 950 × 120, just wider than the labeled row (Camera to Game camera), so it reads at about 80 % and shows little empty ground. The narrow picture is unchanged.
- The caption said the narrow view draws "the last chips" as icons; the strip wraps only once every chip is an icon, so the caption, alt and shows now say every chip, and they name the Scene view's width, not the window's. The page's sentence before the figures calls the two cases "a wide and a narrow window": the pictures differ in the Scene view's width inside one window size.

## Not verified

- The disabled fade of `GetColorU32` is ImGui's own behavior (alpha multiplied while a disabled scope is open); read from the ImGui API, not checked in the vendored source.
- The "Who uses it" cells of the alternatives table are generic descriptions of approaches, not claims about named products.
- The page was not run in a built editor; the chip-strip numbers are computed by hand and by the page's sketch.

## Findings not applied

- The brief lists no open findings.
- Brief item `editor-ui:547` (a zoomed crop of the kit) is not carried: see Requests.
- The Scene view toolbar's width numbers in the worked example are the toy's, not the real chips' widths.

## Since

- since 0.3.0: `Widgets.cpp` and `ItemProbe.cpp` were added in the commit 9c8c35b4, contained in tag v0.3.0.

## Clerk

- Admitted to extra-words.txt: toolbar (asked by three pages).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
