# Part review: draw/gpu-driven (group 2 of 2)

- wrong: "The pin has no editor setting or command for `GPUDriven`": `viewport.capture` has a `GPUDriven` switch in its `renderer` parameter (`StrataEditor/src/Editor/ViewportRenderer.cpp:156`, `EditorViewportCommands.cpp:1270`); the bullet now says so.
- wrong: the empty-scene rule said "a scene with no proxies at all" and linked AGENTS.md; `m_GPUCullFrame` tests `GetProxyCapacity() > 0` (a render scene that never had a proxy), and the rule is the developer guide's (`Docs/DeveloperGuide.md:4365-4368`), now linked there.
- wrong: the shadow use bit was "casts into a cascade"; `ST_FEEDBACK_SHADOW` also marks casters of point and spot lights' shadow views (test "Feedback marks the casters of point and spot lights' shadow views outside the view as the CPU's walk does").
