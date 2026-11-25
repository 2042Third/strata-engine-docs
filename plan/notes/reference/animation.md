# Notes: reference/animation

## New terms

None.

## Requests

None. No figures; the page has no figures file.

## Hand-written tables

All tables are hand-written; src/generated/reference/ holds no animation table. Each was read at the pin from:
- Controller format keys, parameter kinds, condition operators: `Strata/src/Strata/Animation/AnimationController.h`, `AnimationController.cpp` (DataFromJson, Create, DataToJson), `AnimatorInstance.cpp` (ConditionsHold, ConsumeTriggers, exit times, transition order).
- "STSK" and "STAC" layouts: `Skeleton.cpp`, `AnimationClip.cpp`, `AnimationClip.h` (Serialize, Deserialize, enums).
- Limits: `Skeleton.h`, `AnimationClip.h`, `AnimationController.h`, `AnimatorInstance.h`.
- Scene services: `Strata/src/Strata/Scene/SceneServices.h` (ISkinningPoses, IAnimatorControl, IAnimationEventSource).

## Not verified

- The sample controller `Samples/ThirdPerson/Assets/Animations/Robot.stanimator` was only partly read; the page claims it is a complete controller.
- The JSON fence transition (Idle to Walk, 0.15 s) is illustrative, not copied from a sample.
- Byte order of cooked numbers (native, copied with BinaryWriter) not checked across platforms.

## Findings not applied

- critic-reference-2: applied (every table has an introduction naming its teaching page), except that the limits and services tables name their page in the paragraph above rather than one sentence each.
- critic-reference-12: applies to other pages, not this one.
- Size lint reports against the outline row: known fault, not padded.

## Clerk

- Nothing asked; nothing admitted.
