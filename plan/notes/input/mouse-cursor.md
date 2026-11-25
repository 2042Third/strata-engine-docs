# Notes: input/mouse-cursor

## Since

0.3.0: `SetViewport`, `SetGameCursorMode` and `CursorMode` first appear in `Strata/src/Strata/Input/Input.cpp` in commits contained in v0.3.0, the first tag (`git log -S` at the pin).

## New terms

None proposed. The page defines the three terms the brief homes: viewport (input), cursor mode (alias cursor lock), mouse delta.

## Requests

- Host `glfw.org` for the Further reading entry (cited without a link until then).
- Words: none required.

## Not verified

- On a scaled display the exported game's position (screen coordinates) and `Game::GetWindowSize` (framebuffer pixels) differ by the content scale: read in the code, not run; the page says so.
- The Game view's letterboxing algorithm is not stated; exercise 2 assumes a centered, largest fit as its own assumption.
- That a positive yaw change turns the camera left or right is not stated on the page.

## Findings not applied

- Section "What went wrong before": omitted; no bug with a regression test is recorded in the brief for this part.
- The brief's figure (diagram with the formula) is a Mermaid diagram plus the formula in text; no figures file.

## Clerk

- Nothing to admit: www.glfw.org is on the list; the page may link it.
