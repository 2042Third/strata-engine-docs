# Notes: capstone/plan

## New terms

- spec (alias: specs): a written design that names the goal, the starting point, the decisions, the steps, the tests and the acceptance numbers of a change before the change begins. Home: capstone/plan.

## Requests

- Words: spec, specs (the new term above).
- The tutorial file has no `patch.experiment`: tools/schemas/tutorial.schema.json allows only `file` and `tests` under `patch`. The page tells the layering experiment in words (an include of `Strata/Physics/PhysicsComponents.h` in `Strata/src/Strata/Scripting/ScriptHostAPI.cpp`, the key line of `Architecture.Layering`, then `git checkout`). The planner should add the field to the schema and the file, with a text capture of the failing output.
- No figures file: the one picture is a Mermaid diagram.
- Links to ../capstone/build.md and ../capstone/land.md (pages not written yet) and to engineering/contributing (a Need).
- The exercise-2 patch applies on top of tutorials/capstone/plan.patch.

## Since

since is not written: part capstone is not among the parts that carry it. The wind zone chain and Docs/Plans/Wave8 are 0.8.0 work.

## Not verified

- The exact failing line of the experiment (file name and line number come from the run); its format is the one `LayeringTests.cpp` checks.
- Statements about the wind chain (the chain's zone treats both modes alike; WindZoneSystem registers before Physics) come from the book's own patches, not from the pin.
- The names in the spec (Arrow kind, wind.sample, Wind::GetForceAt, the 0.1 ms target) are design proposals, not code at the pin.

## Findings not applied

- critic-capstone-12: the page has one picture, the Mermaid parts map, which is the picture of "What you will make".
- critic-capstone-10: the erratum has no section of its own; the page names the seven services in a step and links world/systems.
- All other findings (3, 6, 7, 8) are applied: the module rule with the editor exception, the documents list in the spec, the first hour and the review, the scale rule and the layers decision.

## Clerk

- Admitted the term spec (alias specs), homed here.
- The clerk shortened the quote's to= at the fence of PhysicsRegistration.cpp to a part without quotes: the site's reader ends an attribute at an inner quote.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Tutorial run

- 2026-11-24, pin 319075e3: the patch and exercise-2 apply on the chain from editor/tutorial-command and pass as written; `Architecture.Layering` and the feature test pass on the built chain. The experiment of step 3 (the failing include) is told in words and was not run.
