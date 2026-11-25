# Notes: animation/skinning

## New terms

None proposed. The page defines the glossary terms bind pose, inverse bind matrix, skinning, linear blend skinning, dual quaternion skinning, influence, skin and skinning palette in bold; "animator" and "rigid binding" are bold-defined as plain words (animator is homed on animation/importing).

## Since

0.3.0: the skinned-mesh row of plan/inventory/animation.md (line 65, since 0.3.0); linear blend skinning shaders and palette rows (150-154) also 0.3.0.

## Requests

- Figure, not drawn: the feature test's arm (Arm Rig) in the entity-ID view, bind pose and posed (brief item animation:424, screenshot 9). The pin has no entity-ID debug view to capture; tier 3.
- The page spells the artifact "twist collapse": "candy-wrapper" fails the word list ("wrapper" is refused). The brief's name for it is candy-wrapper collapse; add an alias if the planner wants it searchable.

## Not verified

- The "Used by" column of the model table (props and weapons for rigid binding; glTF and most real-time engines for linear blend skinning; engines and tools that offer dual quaternions as an option) is general knowledge, not checked in a source.
- The statements about dual quaternion skinning (no collapse, a bulge at bends, no scale, eight numbers per joint) and the three Further reading citations come from memory, not from a fetched source.
- That the linked pages (animation/importing, animation/limits, appendix/not-in-strata, editor-ui/scene-view, physics/building-bodies) exist with the described content: they were not at the worktree when written.
- "GPUAnimationTests.cpp 117" in the brief does not call ComputePalette; the page says the test compares a posed tube with a mesh skinned on the processor, which is what the code does.

## Findings not applied

- The brief lists no open findings. Screenshot 9 (animation:424) is requested, not drawn (see Requests).

## Clerk

- Nothing to admit. The alias candy-wrapper collapse is the planner's (the page writes twist collapse).
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
