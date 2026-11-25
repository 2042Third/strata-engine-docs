# Notes: indirect/ssr

## New terms

- bisection: halving the interval between the last ray point in front of a surface and the first point behind it, keeping the half that holds the crossing. Home: indirect/ssr. Aliases: bisect, bisections, halving.

## Requests

- Word list: "bisection" (and its forms) is proposed above; pagecheck's word-list failure for it, three lines, is left for that reason.
- Figures: scene recipes ssr-modes-sweep (compare, variants off, checkerboard, spatial, spatialhigh, set through the quality row), ssr-roughness-sweep (compare, two variants of the component's maximum roughness), ssr-edge-fade-crop, ssr-posts-crop, ssr-crescent-crop, ssr-ao-wet; all use the look-dev project and its shots (lookdev.mirror, lookdev.wet.sunward, lookdev.sheet, lookdev.sheet.angle, lookdev.wet) and wait for tier 2: renderer switches. The entity name "Post Process" in the roughness sweep recipe is a guess. Five diagrams with numbers (ssr-ray-line, ssr-edge-fade-diagram, ssr-post-ghost, ssr-crescent-diagram, ssr-screen-door) are requests for the planner to draw; the pipelines diagram is Mermaid.
- Hosts for Further reading (cited without links): the Journal of Computer Graphics Techniques paper, SIGGRAPH 2015 and GPU Pro 5.
- Sketches: sketches/indirect-ssr-toy.cpp (the toy), sketches/indirect-ssr-hiz.cpp (exercise 3's solution).

## Not verified

- The Who-uses-it column and the Further reading entries (McGuire and Mara; Stachowiak; Uludag) are from memory, not from the pin.
- That the look-dev shots show what the captions say (the figures are not taken).
- Exercise 2 (the 0.7.0 acceptance) was not built or run; the failing test named is the one whose comment describes that fault.
- The `ST_PREPASS_SURFACE` macro is not named on the page because the names check does not find it (CMake lists it inside a string); the page says "a variant of the depth prepass shader".
- The sketch of the hierarchical march is a one-dimensional model, not the engine's shader of 0.7.0 (that code is not at the pin).
- The 0.7.0 faults (ghost posts, sky wedges, dark wet ground) are from the tests' comments and the inventory, not from the 0.7.0 code.

## Findings not applied

- None open. render-indirect:707 / new:11 (the component's comment says "with TAA only") is stated as the erratum at the end of "What went wrong before"; new:10 (no reflections of or through transparent surfaces, no clear-coat reflections) is stated in "The forward mix". E7 is exercise 2 (described, no patch); E8 is exercise 3 and the toy section; new:25 is exercise 1.
- Brief items on the flicker meter's use and the gate bounds are only referenced (suite and link to test kinds).

## Since

- 0.6.0: Docs/Releases/0.6.0.md lists screen-space reflections (Checkerboard) among what 0.6.0 added; Spatial and SpatialHigh came in 0.7.0.
- 0.8.0: in frames with a rect light the Checkerboard trace runs a variant (`ST_SSR_LIGHT_SURFACES`) that traces nothing from a light surface and sends no color from a hit on one; the quote of its second half shows it. The look-dev figures no longer wait for the renderer switches, which the pin has.

## Clerk

- Admitted the term bisection (aliases bisect, bisects, bisections, halving), homed here; its bold on the page defines it.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

Taken at the pin 319075e3 (v0.8.0); none had been published before. All six published.

- ssr-modes-sweep: round 1 drew without TAA (temporalFrames 0), so Checkerboard traced nothing and matched Off. Round 2 sets `antiAliasing: taa` for all four variants: Checkerboard shows the reflection with a fringe of noise, Spatial and SpatialHigh are clean and differ in under 200 pixels. The Mirror scene has no probes, so the caption names the sky's light only.
- ssr-roughness-sweep: one round. The floors are 0.02, 0.1 and 0.3 rough, so at 0.2 only the glossy floor (0.3) loses its reflection, and the satin floor keeps it; the old caption said both lost it. The caption and alt now say so; the fade over the last quarter shows no edge here (the floors are uniform), so the caption no longer claims it. The shot's crops (polished, satin, glossy) are screen thirds, and the floors' borders run diagonally across them: the "glossy" crop holds part of the satin floor.
- ssr-edge-fade-crop: one round. The camera faces the low sun, so the objects are backlit, not sunlit; caption and alt now describe the far wall's and the posts' reflections reaching both sides.
- ssr-posts-crop: round 1 (shot lookdev.sheet) showed the posts' reflections 10 pixels wide at the far end of a grazing sheet. Round 2 frames the wet ground with Post 2, Post 3, the crates and the white Box wall at camera (-14, 1.3, 25): each post reflects once and the wall's top edge reflects straight.
- ssr-crescent-crop: round 1 (shot lookdev.sheet.angle) showed no ball reflection in the sheet (the ladder spheres stand 5.75 m before it and reflect mostly off the sheet's end). Rounds 2 and 3 add a white ball ("Crescent Ball", SpecPostWhite) 1.25 m before the sheet and look down from (5, 3.6, 1.5) at fov 24: the reflection keeps a lit crescent along its top, and the rest shows the sheet's fallback.
- ssr-ao-wet: round 1 (shot lookdev.wet) framed the crates 70 pixels high. Round 2 frames Crate 2 close from (-11.5, 1.0, 17). Its reflection is darker than the crate (Fresnel of the wet ground), not "as bright as the box": the alt now says a darker copy with an even tone up to the contact line.
