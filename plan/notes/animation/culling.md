# Notes: animation/culling

## New terms

- play revision: a counter in an animator instance that changes whenever what plays changes (a state, a transition, a clip); the reach's cache keys on it. Home: this page (bold in "The reach"). Aliases: none.

## Since

0.3.0: WhenVisible and the reach (inventory animation:129, 132); refinements 0.4.0 (rigid parts, stale poses: Roadmap 327-329 at the pin). Reach versioning: release not stated (animation:645 stays open).

## Requests

- Words: PixelMannen, tomkranis, AsoboStudio, scurest (the fox's authors, in the figure's caption).
- Layout: `layouts/scene-view.ini` for the figure `foxes-afar` (recipe kept, `waitsFor` tier 2: editor screenshot).
- The caption names the authors and the license kind; the version numbers (CC0 1.0, CC BY 4.0) stay out because a caption writes no number; `appendix/credits` holds the full credit.
- Further reading names the Unity manual and the Unreal Engine documentation without links (no page URL was fetched).

## Not verified

- Unity's three Culling Mode choices and their behaviour, and Unreal's update rate optimization: written from memory of their manuals, not fetched.
- The page `editor/stepping`, `light/sun-shadows-1` and `draw/gpu-driven` are linked by their planned ids.
- The foxes' count (30) and cells (10) come from the brief's evidence, not re-counted.

## Findings not applied

- animation:645 (release of each refinement): only 0.4.0 for stale poses and rigid parts is evidenced by the Roadmap; the rest stays 0.3.0 by the page's `since`.
- new:31 (the recipe must set WhenVisible on all 30 foxes): the figure sets one entity named `Fox`, and pagecheck's `figures` finds no entity of that name at the pin; the photographer settles how (every fox of the world).
- Brief item "the Course's chest" example: the Samples folder at the pin has no Course sample, so the page says "a model made of rigid parts, such as a chest" without naming it.
- E4 as an engine patch: the exercise has no patch file; the page gives a worked solution naming the files, with the statistic defined as joints posed.

## Clerk

- Admitted the term play revision, homed here.
- Admitted to names.txt: PixelMannen, tomkranis, AsoboStudio, scurest.
- Figure foxes-afar: its setup step named the entity Fox, which no scene document of OpenWorld holds (the foxes are Fox (1) and on in the Wildlife cells, set to AlwaysAnimate); the clerk removed the step and the clause of its shows that it made true. A recipe that sets every fox to WhenVisible is the planner's.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- foxes-afar (editor, Viewport panel of `layouts/scene-view.ini`, provisional build 5b975ad2831e; `waitsFor` kept). Not good after three rounds: no fox shows.
  - The recipe now loads the Wildlife cell -3,-1 (`world.loadCells`, wait), finds its six Animators (`entity.find` by component, bound as a list), sets them all to WhenVisible in one `component.set`, hides the scene gizmos and frames them with `camera.focus` at pitch -50 (the camera ends 85 m from the camp at -144, 14, -48). The paragraph's "the recipe sets WhenVisible" is now true of the six foxes in view, not of all thirty: the other cells are not loaded by the recipe.
  - Round 1: `camera.set` from (-112, 40, -12) at fov 24, low over the trees: the camp and canopy, no fox.
  - Round 2: higher, from (-126, 76, -18) at fov 28: the clearing around the camp, no fox; enlarged, small dark shadows lie on the grass with nothing above them.
  - Round 3: `camera.focus` on the six foxes and `editPose: "clipStart"`: the focus centres on the camp, as the foxes' positions say, and again no fox body is drawn; the fox-sized shadows remain.
  - What it suggests: in edit mode the foxes' skinned meshes cast shadows but are not drawn in the main view, whether in the rest pose or the clip's first frame. Untested: whether that happens only with WhenVisible (a round without the `component.set` would tell) or in edit mode at all (a take with `play: true` would show the foxes posed and wandering). Worth an engine check before the pin moves.
  - The page gets, until then: no picture. The nearest honest one is the same view with `play: true` (the foxes posed by the game, the caption unchanged), or, if the shadows are the engine's fault, the retake once it is fixed.
- foxes-afar at the pin v0.8.0 (319075e3, Release build): published after three rounds; `waitsFor` removed (check asked).
  - Round 1: the recipe as it stood (`camera.focus` on the six foxes, pitch -50, 85 m): the camp and forest; enlarged, a fox body is drawn on the grass right of the camp. The engine now draws the foxes in edit mode: the old take's missing bodies are gone.
  - Round 2: `camera.set` target (-144, 13, -48), yaw 35, pitch -45, 42 m, fov 30: one fox beside a round tree, the others under the canopy.
  - Round 3 (published): pitch -70, 55 m, fov 28: two foxes in the clearing (Fox (5) above the right tent, Fox (6) beside the round tree), about 25 px long; the rest stand under trees or off the frame. Caption, alt and shows rewritten to that.
  - The page's paragraph under "Many animators" is no longer true of the picture: it says "no fox bodies" and "drew only the foxes' shadows"; the picture shows two fox bodies. It also says "the cells around the camp" while the recipe loads one Wildlife cell (-3, -1). The writer should say the picture shows two of the six foxes in view, small, from high above.
- foxes-afar mended after a viewer's report (the two foxes were 12 to 20 px long; the caption hinted that foxes under trees are skipped). Two rounds at the pin's Release build.
  - Round 1: `camera.set` on the midpoint of Fox (5) and Fox (6) (-139.3, 14, -59.2), yaw -23 (the two foxes side by side across the frame), pitch -65, 28 m, fov 24: both foxes about 45 px long, but Fox (6) half behind the round tree's crown.
  - Round 2 (published): yaw 157, the same otherwise: Fox (5) on the grass by a red flower on the right; Fox (6) on the left stands on top of the round tree (its document height, 18.8 m, is the crown's: the sample placed it there) and casts its shadow on the crown. The camp's tents are out of the frame.
  - Caption, alt and shows now name both spots and say what the renderer reports: foxes whose bodies or shadows the view draws are posed every update; foxes outside the frame keep their time and skip their poses. The claim about foxes hidden among the trees is gone.
  - Seen in both rounds, at the same place on the ground (about 3 m from Fox (5), against the sun's direction from it): a fox-shaped shadow with no body above it. The cell holds only the six foxes, none there. Worth an engine check (a stale shadow of a skinned caster?); the caption does not mention it.
  - For the writer (the page's words were not changed here): the paragraph above the figure under "Many animators" still says the picture shows the camp and no fox bodies, only shadows. It should say the camera looks from above at two of the six foxes, one on the grass and one on top of a tree, and that the recipe loads one Wildlife cell, not the cells around the camp.
