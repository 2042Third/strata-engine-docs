# Part review of `make/levels-saves`

- wrong: "A checkpoint file" placed the player with `Entity::SetWorldPosition`, which the SDK lacks (the call is on `TransformComponent`), and the course's player is a character controller that `make/characters-cameras` moves only with `Teleport`; the sentence now names `Teleport` and links that page.
- wrong: step 3's pseudocode read `Scene::FindEntityByName("Player").GetWorldPosition()`, which `Entity` lacks; it now reads `.GetTransform().GetWorldPosition()`.
- step: step 3's limit of -10 m lay below the `FallHeight` of -8 m at which the course's `PlayerController` already teleports the player, so `Game::ReloadScene` never ran; the limit is -5 m and the "If you do not see it" names the -8 m.
- step: step 2's command tab passed the name `Goal` as `entity` in `parameters`, which takes only an entity ID; it now uses `entityName`, as the exercise's tutorial file does.
