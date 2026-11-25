# Part review: `world/scene-graph`

- wrong: "the runtime update also calls `UpdateWorldTransforms` ... between fixed steps": at the pin `Scene::OnUpdateRuntime` calls it before the systems and, while it interpolates, before the fixed loop and in the capture after it, never between steps; corrected.
- gap: the brief's `scene-ecs:52-56` (Transform edited as Euler degrees in the Inspector) was not taught; added to the callout of `TransformComponent` (`ComponentRegistration.cpp`: the Rotation's tooltip "Edited as Euler angles in degrees").
