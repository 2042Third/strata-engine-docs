# Notes for world/review

Pages each cumulative exercise needs (by number in src/content/docs/world/review.md):

1. Basic: world/ecs (handle bits, versions, UUID), world/scene-graph (two forms of the hierarchy), world/serialization (Parent in the file).
2. Basic: world/systems (accumulator, cap), world/interpolation (step alpha, drawn time).
3. Medium: world/systems (cap at a project rate, dropped steps), world/projects-settings (Scene.Timing, FixedRate), world/interpolation (alpha after a cap).
4. Medium: world/tutorial-component (WindZone ranges), world/reflection (clamp in files, refusal in commands), world/serialization (unknown components kept, unknown properties skipped).
5. Medium: world/sub-scenes (chunks, estimate, 2 ms cap, entity limit), world/systems (SceneSettings limits).
6. Hard: world/prefabs (override records, Propagate), world/scene-graph (local and world positions, SetParent keeping the world place).
7. Hard: world/projects-settings (hand-over, ApplyProjectTiming), world/sub-scenes (worker and main thread), world/systems (cap, steps), world/interpolation (alpha with interpolation off).
8. Hard: world/scene-graph (transform contract, GetWorldTransform between updates, validation, frame cost), world/systems (update before fixed steps), world/tutorial-component (the WindZone system).
