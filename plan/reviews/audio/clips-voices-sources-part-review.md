# Part review of `audio/clips-voices-sources`

- wrong: a file whose header claims too many frames "fails when its data runs out" (body and Check-yourself 2): `DecodeAllFrames` ends with success at `MA_AT_END` and fails only on a decoding error (`AudioClip.cpp:47-52`); now "its decoding ends, or fails, where its data runs out" and "decoding stops where the data ends".
- unclear: "decodes 44,100 frames per second" was marked as the game's frame rate; the frames are audio frames, so the sentence now says "frames each second" and carries no mark.

Checked and holding: the importer (extensions, 1 MiB threshold, the warning, the `Streamed` check, version 1), `Wood.ogg.meta` `Decompressed`, the cooked `STAU` layout, the data source, the destruction order, `Start`, `Play`, `ResetVoice`, `SetClip` making a voice at once, the validation of `AudioSource`, the callout line numbers.
