# Part review of `gpu/binding`

- wrong: the slot rule said the next free slot of the scene layout's list is 55; the comment in `Strata/shaders/Include/Scene.slang` at the pin names 61 (54-60 are taken), and the rule box and Medium exercise 2 now say 61 (`register(t61)`, binding 61).
- wrong: the MoltenVK budget said the scene set uses 12 storage buffers; `Docs/DeveloperGuide.md` at the pin counts 13 (the lights' shapes among them), and the contract paragraph and exercise 2 (13 to 14) now say so.
- wrong: the mirror check was quoted as `8 * 64 + 27 * 16` (944 bytes); `SceneRenderData.h` at the pin asserts `8 * 64 + 28 * 16`, 960 bytes, and the sentence now gives 28 values and 960 bytes.
