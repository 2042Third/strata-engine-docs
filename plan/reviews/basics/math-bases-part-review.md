# Part review: basics/math-bases (group 3 of 5)

- wrong: "Strata's shaders build the frame from the normal alone" is true only of TangentBasis in Strata/shaders/Include/IBL.slang, used for light sampling (ImportanceSampleGGX, SampleCosineHemisphere); normal maps take the vertex tangent (Strata/shaders/Scene/Mesh.vert.slang a_Tangent), so the page now says "Strata's light sampling builds the frame from the normal alone".
