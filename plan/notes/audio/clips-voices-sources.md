# Notes: audio/clips-voices-sources

## New terms

None proposed.

## Since

0.3.0: the audio importer and clips are listed in release 0.3.0 notes (inventory audio-input:45-52).

## Requests

- Layout `layouts/inspector-import.ini`: the inspector showing the import settings of `Samples/PhysicsPlayground/Assets/Sounds/Impacts/Wood.ogg`, with the load mode tooltip open.
- External hosts: Unity manual and FMOD documentation are cited in Further reading without links.

## Not verified

- The duration and channel count of `Wood.ogg`: the page uses an assumed clip of 0.4 s, one channel, 44,100 Hz as a labelled example.
- The mixing period in frames (the page uses 480 frames at 48,000 Hz as an example only).
- Behaviour of other engines' load types (Unity, audio libraries): stated generally, cited in Further reading only.

## Findings not applied

The brief lists no open findings.

## Clerk

- Hosts: the Unity manual and FMOD documentation were not asked as hosts with a front page; none admitted.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.

## Figures

- `import-settings`, round 1 (provisional build): the recipe named a layout that did not exist (`layouts/inspector-import.ini`) and the Inspector, where an asset's settings are not; it now selects `Sounds/Impacts/Wood.ogg` and pictures the Asset tab at its own pixels with `layouts/make-sound-short.ini` (1280 × 540), as `editor-ui/inspectors`'s `asset-audio` does. The picture shows Load Mode at Decompressed under Import Settings and the clip's preview (0:00.3, 44100 Hz, stereo). The tooltip the old caption named cannot be shown (no command opens a hover tooltip); caption and alt now say what is visible, and the page's paragraph already names the two modes and the 1 MiB threshold. `waitsFor` kept.
- `import-settings`, round 2 (pin v0.8.0, 319075e3): `check` found `editor.screenshot` at the pin, so `waitsFor` is removed. One take, unchanged recipe: the Asset tab shows Load Mode at Decompressed, Revert and Apply, Play, 0:00.3 · 44100 Hz · stereo and an orange waveform of one knock that dies away, as caption and alt say. Published.
