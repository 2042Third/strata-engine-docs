# Part review of `light/material-data`

- contradiction: the opening said the concept page `light/materials` names the descriptor set for each material and Strata's buffer of records and texture table; that page does not, `gpu/binding` does (its "One set per material" row); the sentence now credits `gpu/binding`.
- wrong: the Summary said a missing map reads "white, black or the flat normal"; at the pin (`MaterialGPU::Build`) no absent map reads black, only the glow map while loading; the bullet now says "white or the flat normal".
