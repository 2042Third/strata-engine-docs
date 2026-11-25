# Part review: indirect/gi-cascades

- contradiction: "How it is tested" said the layout tests check "that High bounces and Low does not", while the page (and the test "High bounces on, Low once") says Low bounces once; now "High bounces on and Low bounces once".
- wrong: exercise 3 said `GatherIndirectField` weighs the result by the field's weight; at the pin it only puts the irradiance on the surface (`IndirectLight.slang` 113-118), and `ShadeLitSurface` in `Forward.frag.slang` multiplies by `FieldWeight`.
