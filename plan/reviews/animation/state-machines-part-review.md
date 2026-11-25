# Part review: `animation/state-machines`

- wrong: "calls `Advance` once per update on the main thread": `AnimationSystem` calls `AnimatorInstance::Advance` from `StepRecord` inside `JobSystem::ParallelFor` (`AnimationSystem.cpp:648-653`, `:760`), as `animation/system` teaches; now "in a parallel job that writes only that animator's record", with a link to the system page.
- wrong: "A parameter has a Name, a Type ... and a Default": a trigger has none (`AnimationController.cpp:287`, "Trigger '{}' has no default: triggers start cleared"; the robot's triggers carry no `Default`); now "and, unless it is a trigger, a Default (a trigger starts cleared)".
- wrong: the commands table said `PlayClip` is always accepted; `AnimationSystem::PlayClip` refuses a handle that is none or not an animation clip (`AnimationSystem.cpp:983`); the cell now says so.
- wrong: the test "Triggers are consumed by the transition that fires, once" was said to run "a chain of two states"; it runs three states A, B and C with two transitions (`AnimatorTests.cpp:192-195`); corrected.
- unclear: "It has parameters of three types" read as Mecanim's (Unity's has four, with integers); now "Strata's has parameters of three types".
