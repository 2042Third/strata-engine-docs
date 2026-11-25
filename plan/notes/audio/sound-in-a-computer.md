# Notes: audio/sound-in-a-computer

## Since

0.3.0: the audio module and its mixer format (Strata/src/Strata/Audio/AudioEngine.h) are older than the first tag (not checked against tags).

## New terms

- Pull model: the way an audio device asks the mixer for each period on its own thread, instead of the game pushing queued buffers; home: this page.
- Sample rate: how many samples are taken each second for each channel; home: this page.
- Decibel: a unit that scales amplitude by 10^(g/20) for g decibels; home: this page (glossary lists it under gain's item).
- Thread: code that runs at the same time as other code; defined here in one sentence for the audio thread (home: basics/threads).

## Requests

- Names for names.txt: FMOD, Wwise, OpenAL (also acronym exemption for FMOD).
- Hosts for external-hosts.txt: www.fmod.com, www.audiokinetic.com.
- No figures file: the one picture is a Mermaid diagram.

## Not verified

- Wood.ogg: stereo, 44,100 Hz, 13,805 frames read from the Ogg header and last granule position; 6,233 bytes from the file.
- Claims about FMOD, Wwise, OpenAL Soft, XAudio2 and system interfaces (model, contents, users) come from general knowledge, not from the pin; Further reading names their documents.
- The reason in the why aside (a separate authoring program) is a design inference, not a statement found at the pin.
- miniaudio's licence and that its device thread pulls the node graph are taken from the header comment of AudioEngine.h and the inventory; vendored source not read.
- Period length depends on the backend; only the tests' 11 ms comment is cited.

## Findings not applied

None: the brief listed no open findings.

## Clerk

- Admitted the term pull model, homed here. Page fix for term-paragraph: its sentence became its own paragraph, after the audio thread's.
- Refused as terms: sample rate (homed on basics/signals), decibel (homed on basics/numbers), thread (homed on basics/threads); only their homes word them.
- Admitted to names.txt: FMOD, Wwise, OpenAL. FMOD entered tools/data/acronyms.json's exempt list (a product's name, not an acronym the page can spell out).
- Not admitted: www.fmod.com (no title to one fetch) and www.audiokinetic.com (an error page); left for the planner.
