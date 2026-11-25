# Part review of `basics/math-probability` (group 5 of 5)

- wrong: the Coin Run pseudocode called `GetEntity().SetWorldPosition(...)`; the SDK's `Entity` has no `SetWorldPosition` (it is a member of `TransformComponent`, `StrataScriptCore/Include/StrataScript/Entity.h:212`), so it now calls `GetTransform().SetWorldPosition(...)`.
- wrong: "The grain adds the frame's number to its stream"; `AddFilmGrain` salts its streams with `8u + 4u * frame` (`Strata/shaders/Include/Grain.slang:21`), so the sentence now says the stream number grows with the frame's number.
- gap (not applied): the brief's "Where the book uses it" names `engineering/testing`, but that page does not have this primer in its Needs closure, and pagecheck's `pages` check refuses the link; the list stays as written.
