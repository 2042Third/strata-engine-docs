# Part review: image/spatial-aa

- wrong: Check yourself 2's answer explained the distractors as "B divides by the longer distance alone and C adds the shares", which gives neither 0.125 nor 0.375; B is one over the sum (1/8) and C is 0.5 minus that.

Checked without change: FXAA's constants, luma weights and step sizes (12 samples, 26.5 pixels), the worked FXAA example (2.6 against 1.0, offset 0.25, subpixel 0.0414, result 0.7), the morphological thresholds (0.05, 5 %), luma weights, `c_MaxSearch` 32, the 132 by 132 table, the Z-run and blend examples, the 50 MB targets, `RenderPostDisplay`'s fallback, `ApplyQualityOverrides`, the Basic 3D template's TAA, the subpixel and slope measurements of Docs/DeveloperGuide.md, the test suites and cases, the look-dev `--aa` modes and `tp.live.slow`.
Not a page fault: pagecheck's figures step fails because tools/figures.py's placed_crops counts only ::figure directives, so the crops of aliasing-floor and subpixel-pair placed by ::compare count as unplaced.
