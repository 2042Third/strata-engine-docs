# Notes: `image/review`

## Pages each exercise needs

1. Basic: `image/why-post`, `image/exposure`, `image/pre-exposure` (EV100 and the manual factor, the 65,000 clamp, the choice of P with 2 stops of headroom, the dead band, subnormal values).
2. Basic: `image/spatial-aa`, `image/encoding`, `image/quality-settings` (the player's row over the scene's method, the fallback to FXAA, which shader dithers, the FXAA edge offset).
3. Medium: `image/tone-mapping`, `image/grading`, `image/encoding`, `image/exposure` (slope in stops before the curve, the Filmic and `Reinhard` values, rounding and the two dithers, the lookup coordinate).
4. Medium: `image/lens-effects`, `image/exposure`, `image/pre-exposure` (bloom span and `BloomScale`, the threshold on the exposed color with the knee, why a reader divides P out).
5. Medium: `image/motion-blur`, `image/taa`, `image/why-post` (blur length, clamp and floor, tile size, camera cut, the post source).
6. Medium: `image/depth-of-field`, `image/quality-settings` (focal length from the field of view, circle of confusion, the sharp range, which views show the lens).
7. Hard: `image/quality-settings`, `image/spatial-aa`, `image/encoding`, `image/motion-blur` (Set, SetPreset and Reset, Custom, comfort rows, project change under a saved Custom).
8. Hard: `image/tutorial-post-effect`, `image/pre-exposure`, `image/why-post`, `image/exposure` (a writer that forgets P, the chain position, the exact GPU test, the failure path).

## Not covered

`image/lens-effects` has no exercise on the vignette, the aberration or the flare; exercise 4 uses its bloom.

## Seen

- `image/exposure` (Check yourself 1 and the text) gives log2 (0.18 / 2048) as -13.46; the value is -13.47. The exercises use -13.47.
- `image/tone-mapping` summary says Filmic gives 0.5069 at two stops above middle gray, and its Check yourself 2 gives 0.6515 at three stops; exercise 3 uses 0.5069 from the table and `Reinhard` 0.72 / 1.72 = 0.4186.
