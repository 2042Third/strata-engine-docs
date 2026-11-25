# Part review: `make/lighting`

- contradiction: the glow steps said "The silver coin does not change" and "warmer than the silver one", but `make/prefabs` reverts `Coin (1)` to gold, so all five coins share `Gold.stmat` (`tutorials/make/prefabs.tutorial.json`, `prefab.revert`); both sentences now say every coin changes.
