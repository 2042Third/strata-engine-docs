# Part review of `audio/sound-in-a-computer`

- contradiction: "The sound hardware cuts it at the limit" against `audio/engine`, which says Strata's mix is not clipped and the device backend decides (miniaudio's engine sets `noClip`, `Strata/vendor/miniaudio/miniaudio.h:77579`); now "The device or its driver cuts it at the limit".

Checked at the pin (319075e3) and holding: `Wood.ogg` is 6,233 bytes, 2 channels, 44,100 Hz, 13,805 frames (its last Ogg page); `AudioEngineSpecification` 48,000 Hz and 2 channels; the test comment of about 11 ms (`StrataTests/src/Audio/AudioTestUtils.h:25`); `STRATA_WITH_AUDIO` in `Strata/vendor/CMakeLists.txt:133`.
