# Part review: `make/hud`

- wrong: exercise 2's answer counted the coins in `OnCreate`, but `CoinPlacer` instantiates them in its `OnUpdate` once the prefab has loaded (make/scripting-scene), so that count is 0; the answer now keeps the largest count seen as the total.
