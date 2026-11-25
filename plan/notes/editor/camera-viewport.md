# Notes: editor/camera-viewport

## New terms

- capture: a picture of the edited scene that a command renders and returns, not a screenshot of the viewport; home editor/camera-viewport; aliases: viewport capture.

## Requests

- Glossary entry "Editor camera; orbit" (id `editor-camera-orbit`): lint's `term-defined` can never be satisfied. A bold "editor camera", "orbit", "editor camera orbit" and the literal "editor camera; orbit" were all tried; none matches. Please repair the entry's term or aliases.
- No figures file: both diagrams are Mermaid. The camera model figure (editor-core:500, editor-ui:516) is not drawn; the page carries the geometry in a worked example with numbers.
- Further reading names three sources without links (Unity Manual, Physically Based Rendering, Game Programming Patterns); no host request.

## Not verified

- The Unity Manual claim in Further reading (that its Scene view has orbit, pan, zoom and fly moves) was not checked.
- The "Who uses it" cells of the alternatives table are generic descriptions of tools, not claims about named engines.
- The panel's mouse and key bindings were read from `ViewportPanel.cpp` (right button fly, middle pan, Alt and left orbit, F8, F, Home); the drags themselves are the Scene view page's.
- The page was not run in a built editor: the example's numbers are computed by hand from the code (box bounds, aspect 1280 by 720).

## Findings not applied

- The brief lists no open findings. The inventory's "Dolly by 0.85 per wheel step" and "pitch 89" hold at the pin.
- Brief item `new:65` names spatial reflections (2) and the probes' limit as separate limits; the page folds probes into the shadow views' limit of 16 (`c_MaxCaptureLightingFrames`), as the code does.

## Since

- since 0.3.0: the editor camera and view commands (brief and inventory: 0.3.0; per-scene cameras came later).

## Clerk

- Admitted the term Capture (editor), homed here; refused its alias viewport capture: the glossary homes that term on make/automated-playtests (only its home words it).
- Repaired the entry "Editor camera; orbit" (id editor-camera-orbit): its term is now editor camera, and orbit camera and orbit are entries of their own, each defined from the page's bold sentence.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
