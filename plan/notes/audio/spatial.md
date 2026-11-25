# Notes: audio/spatial

## New terms

None proposed; all eleven terms of the brief are defined in bold on the page.

## Requests

- External hosts: none. Further reading cites the OpenAL 1.1 specification and the miniaudio manual without links.
- Figures `listener-frame` and `gain-curves` are SVGs under `src/assets/figures/audio/spatial/`, drawn by hand from the page's numbers.

## Since

Not set beyond 0.3.0; the audio module's first release was not checked.

## Not verified

- The audio module's first release tag (the `since` of 0.3.0 is a default).
- That miniaudio's gain smoothing default of 8 ms applies at runtime: Strata sets no value; read from `ma_engine_init`, not stated on the page.
- The brief's timeline figure (fixed steps at 60 Hz against frames at 144 Hz) is not drawn; the page gives the worked example in numbers and a sketch.

## Findings not applied

- The Fit paragraph proposes size L; the task fixed M, so the page is M (3,411 words).
- The brief's mention of a rolling ball past the listener is an exercise (computed ratios); no sample script was found that places one.
- The pan law is stated as miniaudio's (each ear takes (1 + dot) / 2 of the gain, floor 0.2), read in `ma_spatializer_process_pcm_frames`; "pan" mode of `ma_panner` is not used by the spatializer.

## Clerk

- Nothing to admit.
