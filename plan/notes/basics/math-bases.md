# Notes: basics/math-bases

## New terms

- Transpose: the matrix with rows and columns swapped, so the number in row i and column j moves to row j and column i. Home: basics/math-bases. Aliases: transposed matrix.
- Orthonormal basis: three vectors of length 1 at right angles to each other; the columns of a rotation form one. Home: basics/math-bases. Aliases: orthonormal frame.
- Bitangent: a second direction along a surface, at a right angle to its tangent. Home: basics/math-bases. Aliases: -.
- Tangent space: the space whose axes are a surface's tangent, bitangent and normal. Home: basics/math-bases. Aliases: tangent frame.
- Determinant: the factor by which a matrix multiplies areas in 2D or volumes in 3D; negative for a mirror, zero for a flat matrix. Home: basics/math-bases. Aliases: -.

## Requests

- Words for tools/data/extra-words.txt: transpose, bitangent, orthonormal (all three are bold-defined on the page as proposed terms).
- Figure `bent-normal` (kind diagram, recipe in src/content/figures/basics/math-bases.json) is not drawn yet.
- Sidebar: basics/math-bases is in no track list yet (pages O5 names B and E); the planner adds it to the lists of tracks B and E.

## Not verified

- The entity names `Ball` and `Coin` in the end state of make/project-coin-run (Practice 5 types them; the answer says nothing else about the project).
- That the linked pages draw/mirrors-camera-relative, light/materials, physics/building-bodies, animation/skinning, basics/math-rotations, core/math and world/scene-graph exist under these paths.
- The page states glm's default constructors leave values unset (no GLM_FORCE_CTOR_INIT define at the pin; checked in the build files, not by running a program).

## Findings not applied

- None. critic-basics-b-4 is applied (the Slang quote is introduced by what differs from C++ and read line by line afterwards). critic-basics-b-9 is applied (Practice 5 logs the matrix column by column, and a common mistake names the matrix declared without a value). Erratum new:121 is applied: the page says that TRS cannot hold a shear and describes DecomposeTransform by what Math.cpp does (fails for non-finite values, w near zero and a scale near zero; mirror folded into x; shear dropped).

## Clerk

- Admitted: transpose, orthonormal basis, bitangent, tangent space, determinant. Their words pass `word-list` as glossary words (R54), so no extra words.
- The clerk split the paragraph that defined bitangent and tangent space into two (term-paragraph); no word changed.

## Track walk E, final, segment 3 (2026-11-24)

- WK1 (`plan/walks/E-final-3.md`): Practice 5 names its start, your Coin Run or Checkpoint 4 of Ship the finished game,
  with a link to that section. Not built: `FrameDemo` finds the spawned `Coin` by name during play and returns until it
  exists.
