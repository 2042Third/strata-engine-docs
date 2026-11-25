# Part review of `gpu/geometry-pool`

- contradiction: "Growing" said the new capacity is the larger of double and the request, while the limits paragraph, the worked example and exercise 4 (and `GrowRequested` at the pin) take the larger of double the capacity and the capacity plus the request; the section now points to that growth rule.
