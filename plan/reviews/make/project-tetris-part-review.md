# Part review: make/project-tetris

- wrong: "static_cast converts ... as stage 2's code does when it picks a color by index": the board picks a material with a switch (`GetMaterial`), and stage 2's cast is the bag turning a number into a piece; now says the bag of this stage does it.
