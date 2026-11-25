# Part review of `audio/testing`

- contradiction: "`AudioTests.cpp` holds the suites `Audio.Engine`, `Audio.Source`, `Audio.Spatial` and `Audio.OneShot`" omits `Audio.Clip`, which `AudioTests.cpp:310` holds and `audio/clips-voices-sources` names there; added.
- unclear: "(50 ms at 48,000 frames per second)" was marked as the game's frame rate; the frames are audio frames, so it now says "frames each second" and carries no mark.

Checked and holding: the helpers of `AudioTestUtils.h`, 4,800 frames as 44 periods of 440 Hz, the panning test, `audio.state` and its two failures, the release-note line on the audio preview (`Docs/Releases/0.3.0.md:177`), `AudioFeatures` requesting its clip in `OnCreate`, `measureAtDistance` with min 1 and max 50, the callout line numbers.
