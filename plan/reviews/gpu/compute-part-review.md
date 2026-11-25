# Part review: gpu/compute (group 1 of 2)

- wrong: "The weight added for a pixel is 1, or more for a pixel near the center in center-weighted metering"; MeteringWeight (Histogram.comp.slang:42-50) returns 1 without center weighting and round(16 x (0.25 + 0.75 x falloff)), 4 to 16, with it; now "from 4 at the edges to 16 at the center".
