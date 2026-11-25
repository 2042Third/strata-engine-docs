# Notes: animation/root-motion

## New terms

None proposed. The page defines in-place animation, root motion and root motion joint in bold (glossary homes). It also
bolds "ancestors' rest transform" and "crossing" as local words; the clerk may admit or reword them.

## Requests

- Figure `extraction` is an own SVG (`src/assets/figures/animation/root-motion/extraction.svg`) with a `diagram` entry.
- Further reading cites a book and generic documentation without links.

## Not verified

- Claims about other engines in the alternatives table (who uses motion matching, three-axis root motion, in-place clips) are not checked.
- The tests suite run line ("reports passed") is doctest behaviour, not read at the pin.
- The importer rule "lowest-numbered joint of the skin" is from `GltfImporter.cpp` around line 1111, read only as a `std::min` over joint indices.

## Findings not applied

The brief lists no open findings.

## Since

`since: 0.3.0`: tag v0.3.0 already holds `AnimationSystem::ApplyRootMotion`, `RootMotionSetup`, `c_MaxRootMotionLoops` and the `AddCharacterMotion` hand-off.

## Clerk

- Nothing asked as a term: the local bolds ancestors' rest transform and crossing stay plain (crossing is a common word).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
