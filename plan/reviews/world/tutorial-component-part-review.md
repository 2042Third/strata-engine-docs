# Part review: world/tutorial-component

- gap: exercise 2 asks which tests fail after the rename, and the answer named only the two feature tests; the reflection test (expects `WindZone`), the round trip test (loads a document that names it) and `Reflection.ComponentSchema` ("the component is no longer registered") fail too, which is why the worked solution changes two tests and the snapshot.
