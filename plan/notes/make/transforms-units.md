# Notes: make/transforms-units

## New terms

None proposed. The page defines in bold, without homing: axis, metre, factor, right-handed, pitch, yaw, roll, radian, relative, glTF (candidates for a glossary if the planner wants them).

## Requests

- Host `dev.epicgames.com` (Unreal Engine's coordinate system, cited in Further reading without a link) and `docs.blender.org` (Blender's axes, cited without a link).
- Figures not drawn: the page has one Mermaid diagram (the axes) and no figures file. Pictures that would help, not requested: the Move and Rotate gizmos on the ground and the coin (editor), World against Local on a turned crate (editor).

## Since

0.3.0: the Transform component, the gizmo, Hierarchy reparenting and the quaternion rotation are in the oldest engine (`Strata/src/Strata/Scene/ComponentRegistration.cpp`, `StrataEditor/src/Editor/TransformEdit.cpp`). Not checked against the 0.3.0 tag itself.

## Not verified

- That Coin Run's walls, ball and coin have the numbers the page assumes (the page of `make/scenes-entities` is not written at the pin of this worktree): only (0, 0.5, -10) is the brief's.
- The Hierarchy shows Sun, Earth and Moon as the page says when dragging (the drop calls `entity.setParent`, whose `keepWorldTransform` defaults to true; checked in code, not run).
- The Local gizmo's blue arrow direction on the Marker (follows from ImGuizmo's LOCAL mode and +Z = blue; not run).
- That glTF models face +Z: stated by the engine's skill file and the glTF specification; no importer code checked.
- Mirrored drawing: the render scene sets the `Mirrored` flag when the determinant of the world matrix is negative; the draw with reversed faces and flipped tangents is from `Docs/DeveloperGuide.md` (4546), not read in the pipeline code.
- The exercise-2 tutorial file was run at the pin (2026-11-18) and passes; it now also checks the answer's claim that the Moon's local Translation stays (2, 0, 0).

## Findings not applied

- critic-make-a-15: applied. The page teaches **Translation** as the Inspector's word for position and names `SetTranslation` and `SetWorldPosition` in its code section. `make/scenes-entities` step 2 is another page's change.
- critic-make-a-18: belongs to `make/input` (steps 1 and 5). This page carries the matching mistake (a stick or key gives +Y, forward is -Z) in a note and in Common mistakes, without the code line.
- Brief item: "radians in `SetEulerAngles`" is stated in the page's Where-it-lives list; the page's code section quotes the `GetEulerAngles` comment (radians).
- Brief item: the code section is placed before "Common mistakes", not last, because the card says Common mistakes ends the body.

## Clerk

- No term asked; the bold words stay plain definitions.
- Hosts `dev.epicgames.com` and `docs.blender.org` not admitted: one fetch of each front page did not show the site (no page, a challenge page); left for the planner.

## Track walk G-final-2 (2026-11-24)

Answers in `plan/walks/G-final-2.md` (WK26, WK27). The section on Strata's choice says how a command reads the
worked-out angles: `entity.get` with `world` returns `world.rotation.euler` through `Math::QuatToEulerDegrees`
(`StrataEditor/src/Editor/CommandUtils.cpp:162-173`), the function the Inspector uses (`StrataEditor/src/UI/PropertyWidgets.cpp:576`).
The exercises say before exercise 3 what running a sketch needs.
