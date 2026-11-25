# Part review of `make/lamps`

- step: ten command tabs passed entity names (`Sun`, `Post Process`, `Lamp`, `Sign Spot`) as `entity` in `parameters`, and `lighting.makeAreaLight` passed `Ceiling Panel` so, which the editor rejects (entity IDs only); they now use `entityName`, as `tutorials/make/lamps.tutorial.json` does.
- step: `entity.setParent`, the housing's `entity.create` and the arm lantern's `prefab.instantiate` passed the names `Lantern` and `Arm` as `parent`; they now name `<id of Lantern>` and `<id of Arm>`, as the page's other placeholders do.
