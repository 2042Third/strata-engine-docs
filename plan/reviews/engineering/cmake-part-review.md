# Part review of `engineering/cmake`

- wrong: the target graph's caption said every program links a game's libraries, and its alt that the command-line client links the game interface target; `StrataCLILib` links only `Strata::Network` (`StrataCLI/CMakeLists.txt:15`), so the caption names the editor, the runtime and the test program, and the alt says the client links only the network layer.
