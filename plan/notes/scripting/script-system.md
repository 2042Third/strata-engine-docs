# Notes: scripting/script-system

## New terms

None proposed. The six terms the glossary homes here are defined in bold on the page: dispatch list, field override, instance, prefetch, sync point, update order. The page also defines "callback" and "reconciliation" in a sentence each without bold (callback is bold: it is homed elsewhere, so it is marked, not defined as new).

## Since

0.3.0: scripting, the callbacks and the ScriptSystem exist from the first engine tag (inventory scripting:164-169 lists them; animation:178 dates OnAnimationEvent 0.3.0).

## Requests

- Hosts for Further reading: none linked; the three sources are cited without links (Game Programming Patterns, Drepper's memory paper, the EnTT documentation).
- Figures: none requested; the three pictures are Mermaid diagrams.

## Not verified

- When each callback arrived is given by group (first set, physics, animation, game UI, last); no version numbers were checked.
- The other-engine statements in the alternatives table are generic and rest on general knowledge, not on a checked source.
- `script.get` reads live field values through `GetFieldValue` (checked in `EditorScriptCommands.cpp`); the inspector's write path through `SetFieldValue` (checked in `ScriptEdit.cpp`).
- Press edges repeating or missing in `OnFixedUpdate` rests on the strata-scripting skill's text, not on a test.

## Findings not applied

- The brief's frame order places animation events after the fixed steps. At the pin the Animation system updates after Scripting and before Physics in the update phase, and it dispatches its events there, so `OnAnimationEvent` runs after `OnUpdate` and before the fixed steps. The page follows the code (`AnimationRegistration.cpp`, `AnimationSystem.cpp` DispatchEvents inside OnUpdate).
- The brief's line numbers for `ScriptSystem.cpp` are shifted at the pin (update phases 195-221, dispatch 241-287, contacts 340-383 hold; the animation event is 389-409, the sync point 487-505).
- Hands-on `scripting:546` (measure dispatch) is a paragraph in "How it is tested", not an exercise; `scripting:548` (why copy the list) is exercise 2.
- No "What went wrong before" section: no bug history of this part was checked.

## Clerk

- Nothing to admit: callback is homed on basics/cpp-generic; reconciliation stays plain.
