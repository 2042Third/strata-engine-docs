# Notes: ui/what-game-ui-does

## New terms

None proposed. Canvas, UI element, screen space, focus, immediate-mode GUI and retained-mode GUI are defined in bold from the brief's glossary rows. "Canvas unit" is used plain (homed by ui/layout).

## Since

0.4.0: Docs/Releases/0.4.0.md lines 52-59 (the whole module); 0.6.0: Docs/Releases/0.6.0.md lines 99-100 (rebindable UI map).

## Requests

- Exercise 2 files: tutorials/ui/what-game-ui-does/exercise-2.tutorial.json and ProbeButton.cpp (not run by me).
- No figures file: all three pictures are Mermaid diagrams.

## Not verified

- Before 0.4.0 the only UI was screen-space text in pixels (from the brief; the TextComponent ScreenAnchor exists at the pin).
- Page-to-component mapping of the tour (which page explains each component) follows the part's briefs, not written pages.

## Tutorial run

- 2026-11-18, round 1: exercise-2 failed: `log.read` answers oldest messages first, so `/messages/0` was the editor's banner. Round 2: reads the Script logger and checks the whole list; strengthened with the answer's three claims (click at time scale 0 comes, button state hover, no left press over the button, a press on empty space). Passes.
- 2026-11-24, final run: the pin-build stamp was current; exercise-2 passes as written with the official v0.8.0 package too (`tutorials.py check --release` finds nothing).

## Engine

None found.

## Findings not applied

None open in the brief.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
