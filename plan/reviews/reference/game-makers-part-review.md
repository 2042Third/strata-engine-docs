# Part review: `reference/game-makers`

- wrong: `SkyLight` `Source` listed `EnvironmentMap` or `Procedural`; the property's options at the pin are `EnvironmentMap`, `Procedural` and `Atmosphere` (components dump); now all three.
- unclear: the components table promises the default of a new component, but `RigidBody` `Type` listed three values without one; the default is `Dynamic` (component-defaults dump); now "`Dynamic`; or `Static`, `Kinematic`".
- wrong: "The next table lists them in the order a frame runs them": the UI callbacks run before the frame's `OnUpdate` (`StrataScriptCore/Include/StrataScript/Script.h`), and collisions after the fixed step; now says a frame runs `OnUpdate`, `OnFixedUpdate` and `OnLateUpdate` in that order, and the UI callbacks before `OnUpdate`.
