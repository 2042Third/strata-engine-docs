# Notes: appendix/math-cheatsheet

## New terms

None.

## Requests

- Extra words for tools/data/extra-words.txt: theta, phi, omega, mu, sigma, exp (names of symbols read aloud in the symbol table).

## Not verified

- The primers' own wording of each formula was spot-checked, not every row against its page.

## Verified at the pin

- Matrix order: `ComposeTransform` builds T R S and `ComposeWorldTransform` returns `parentWorld * local` (Strata/src/Strata/Math/Math.cpp).
- Reversed depth: `PerspectiveReverseZ` calls `glm::perspectiveRH_ZO` with near and far swapped, which gives n(f - d) / (d(f - n)); Math.h's conventions comment states near 1, far 0.
- Rechecked at v0.8.0 (319075e3): `ComposeTransform`, `ComposeWorldTransform` and `PerspectiveReverseZ` unchanged; `OctahedralEncode` (Scene.slang) still divides by the sum of sizes, keeps n.xy for n.z >= 0 and folds otherwise; SphericalHarmonics.slang still uses 0.282095 and 0.488603 (y, z, x). The basics pages' formulas and worked numbers (sRGB 0.461 and 0.214, smoothstep 0.156, smoothing weight 0.0645, decay 0.368 and 0.347) still match the rows. Nothing on the page changed.

## Hand-written tables

- Both tables (symbols; formulas in 14 groups): no file of src/generated/reference/ holds them. Read from the basics pages (numbers, data-structures, trees-graphs, math-vectors, -matrices, -bases, -projection, -rotations, -geometry, -change, -interpolation, color, signals, math-probability, math-sphere) and Strata/shaders/Include/Scene.slang (OctahedralEncode).

## Findings not applied

- critic-appendix-17: applied (Delta, sigma, E[X], variance, bit place values, n-bit range, shifts and masks, tree/heap/sort costs). Not applied: nothing.
- The brief's d/dx, partial and nabla: no page of the book uses partial or nabla, so the page says so and has no row.

## Clerk

- Extra words: theta, phi, omega, mu, sigma, exp, and divisor (school mathematics; divisor failed the word list without a request).
