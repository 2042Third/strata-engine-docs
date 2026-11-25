# Part review: `assets/robustness`

- unclear: the callout of the glTF limits said "a floor of 4,194,304 elements, 4 more for each buffer byte", which reads as a sum; the pin computes `min(c_MaxGeometryBudget, max(c_MinGeometryBudget, bufferBytes * 4))` (`GltfImporter.cpp`), as the page's own example does; the callout now says 4 elements per buffer byte, never fewer than 4,194,304 or more than 268,435,456.
