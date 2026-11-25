# Part review: `physics/queries` (physics, group 2)

- wrong: the overlap order was called "the order in which Strata made their bodies" (contract, the real code, summary, check 3, exercise 1); the sort key's low half is box3d's body slot (`GetBodyKey`, `body.index1`), and `b3AllocId` gives a freed slot to the next new body, so the order is the slots' order, which is creation order only until a slot is freed. Corrected in all five places.
- (size) a sign-post sentence at the end of the problem section was removed to keep the page within size M after the correction.
