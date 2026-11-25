# Notes: animation/limits

## Since

since: 0.3.0. The animation controller and the Animation system landed in 0.3.0 (inventory animation:52 row for AnimationController, version 0.3.0); the absences are older than any tag.

## New terms

- inverse kinematics (IK): finding the joint angles that put a hand or foot at a target; home animation/limits; aliases: IK.
- ragdoll: a character turned into physics bodies joined by constraints, so it falls limp; home animation/limits; aliases: ragdolls.

## Requests

- Extra words (word-list, left because proposed above): IK, ragdoll, ragdolls.
- External host: dev.epicgames.com (Unreal documentation on Animation Blueprints, layered blends and IK Rig, cited without a link); the GDC Vault for Simon Clavet's 2016 talk (cited without a link).
- The tutorial file exercise-1.tutorial.json starts from the basic3d template and imports the robot from the release folder; its two log checks assume the two warnings are the first two of level Warn, in this order (morph target animation, then morph targets, the order of the importer's sorted set).

## Not verified

- The robot's faces carry morph targets: the glb holds a "targets" string; no importer run was made.
- The walk-to-run numbers on the page (1.0 s, 0.6 s, 0.25 s) are invented for the example; the robot's real offset is in the Roadmap's tranche 2 line, which the brief forbids quoting.
- The Console search field and the Import button of the Content Browser were read in the source only.
- Whether the Unity, Godot and Unreal pages cited still hold those URLs.

## Findings not applied

- animation:641 and new:12 (no bounds overlay): the page states only that no skeleton overlay exists and that the Asset tab shows a joint tree; bounds overlays are not claimed.
- The Roadmap wave 9 entry is a shortened quote of `animation-runtime-2` (Blend2D, additive clips, float curves, IK, compressed clips); the tranche 2 line is not used.
- Dual-quaternion absence is stated from the brief's search; the page does not repeat the grep result.

## Clerk

- Admitted the term ragdoll, homed here (ragdolls was already in extra-words.txt).
- Inverse kinematics is not bold on the page: IK entered extra-words.txt instead (the page spells it out in its table); the term is the planner's.
- Not admitted: dev.epicgames.com (no title to one fetch, as in an earlier batch); left for the planner. The GDC Vault (gdcvault.com) is on the list.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
