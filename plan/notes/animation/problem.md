# Notes: animation/problem

## New terms

None. Morph target (blend shape) is defined in bold from the glossary.

## Requests

- Word "skeletal" is not on the word lists; the page writes "skeleton animation". Consider adding "skeletal" to extra-words.txt.
- Further reading cites two sources without links (glTF 2.0 specification; Gregory, Game Engine Architecture): no host requested.

## Since

0.3.0: Docs/Releases/0.3.0.md:63 (glTF skins and animations import as skeletons, clips and skinned meshes; controllers with joints that other entities attach to).

## Not verified

- The robot's 7,214 vertices, 24 frames, and the Running/Walking/Idle key counts come from reading RobotExpressive.glb's JSON (position accessors; rotation and translation sampler inputs, morph-weight channels excluded); not checked against `animation.info`.
- Page links of the map (importing, clips, state-machines, system, skinning, root-motion, time-events, make/animation, appendix/not-in-strata) assume those pages exist.
- The robot's skinned meshes: only the Hand meshes carry JOINTS_0; others are rigid parts (read from the glb).

## Findings not applied

- Brief says thousands of vertices bend at knees and elbows: at the pin the robot is mostly rigid parts on joints, only hands skinned; the page says so.
- Erratum new:14 applied: only the Open World foxes are named, no Showcase Fox.

## Clerk

- Admitted to extra-words.txt: skeletal.
