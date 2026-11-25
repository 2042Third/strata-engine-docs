# Part review: `assets/residency`

- wrong: "`SetResidencyBudgets` ... clamps time values that are not numbers to 0": the pin's `AssetManagerBase::SetResidencyBudgets` sets a finalize or upload time that is negative or not finite to 0 (an infinite one is a number too); the sentence now says "negative or not finite".
