---
id: make/sound
title: "Sound"
description: "Give Coin Run its sounds: a coin one-shot, impact thuds that scale with the hit, looping music and a volume option, and place them in space."
kind: tutorial
size: M
tracks: [G, B]
needs: [make/physics]
time: 45
learn:
  - id: spatial-source
    text: build an entity that plays a clip in space and tune how its volume falls with distance
  - id: early-request
    text: explain why a one-shot is dropped when its clip was not requested before it is needed
  - id: coin-oneshot
    text: write a script that requests a clip in OnCreate and plays it as a one-shot where a coin is collected
  - id: impact-volume
    text: compute the volume of an impact sound from the speeds of two bodies along the contact normal
  - id: music-volume
    text: set a looping music source that is not spatial and change the game's master volume from keys
since: 0.3.0
status: final
---

## What you will make

Coin Run gets ears. A coin chimes where you collect it, the ball thuds harder the harder it hits, music loops under the game, and two keys change the volume.

::figure{id=result}

## How a game makes sound

A sound file stores a wave of air pressure. Strata reads WAV, FLAC, MP3 and Ogg Vorbis files. An imported file becomes a **clip**, an asset that the game can play many times at once.

A clip is silent until something plays it. The first thing that can is an **audio source**, a component that plays one clip from the entity that carries it, with its own volume, pitch, loop switch and 3D switch.

The volume is a factor: 1 plays the clip as recorded, 0.5 plays it at half the amplitude, and the slider reaches up to 4. The pitch is a speed factor. Pitch 2 plays twice as fast and sounds higher; 0.5 plays half as fast and sounds lower.

Sound needs a point of view, as a picture does. The **listener** is the entity whose position and direction the game hears from, like the camera for the eyes. The Basic 3D template gives its Main Camera an **Audio Listener** component. Strata uses the first active Audio Listener in the Hierarchy, and without one it uses the primary camera.

A 3D source behaves like a sound in a room. It gets quieter as the listener walks away from it, and it moves between the left and right speaker as it passes the listener's side. A source that moves quickly toward you also raises its pitch, as a passing siren does.

Some sounds belong to no entity: a coin chime, a thud. A **one-shot** is a sound that a script fires once and forgets; the engine plays it to the end and releases it. You fire one with `Audio::PlayOneShot` (no position) or `Audio::PlayOneShotAt` (a place in the world).

```mermaid caption="From file to speaker: a clip is played by a source or a one-shot, and the listener's position and direction decide the volume of each speaker." alt="A chain of boxes: sound file, clip, audio source or one-shot, mix heard from the listener, speakers."
flowchart LR
  A[Sound file] --> B[Clip]
  B --> C[Audio source or one-shot]
  C --> D[Mix heard from the listener]
  D --> E[Speakers]
```

### Distance and rolloff

The volume of a spatial source depends on its distance to the listener. Strata uses the inverse model: the distance is first limited to the range from Min Distance to Max Distance, then the gain is $\text{min} / (\text{min} + \text{rolloff} \times (d - \text{min}))$. Read it as: inside the minimum distance the sound has full volume, and a larger rolloff makes it fall faster.

For the defaults (min 1 m, rolloff 1), by hand:

| Distance $d$ | Gain |
| --- | --- |
| 1 m | 1 / (1 + 0) = 1.00 |
| 2 m | 1 / (1 + 1) = 0.50 |
| 5 m | 1 / (1 + 4) = 0.20 |
| 11 m | 1 / (1 + 10) = 0.09 |
| 50 m and farther | 1 / 50 = 0.02, the same at any larger distance |

## What you need

- The end of the [physics tutorial](physics.md): the rolling ball and the trigger coins. Your scene and your `Coin` script stay as they are, and this page adds to them.
- A sound output, such as speakers. Sound plays only in Play mode, so a scene you only look at is silent.
- `Coin.ogg` from the release's `Samples/ThirdPerson/Assets/Sounds/` (Kenney, Creative Commons Zero (:term[CC0]{id=cc0}), public domain).
- `Soft.ogg` from the release's `Samples/PhysicsPlayground/Assets/Sounds/Impacts/` (Kenney, CC0).
- `Complete.ogg` from the same folder as `Coin.ogg` (Kenney, CC0), a short tune that stands in for music: neither the release nor the book ships a music file. A long music file of your own works the same way, when its license lets you use it.
- About 45 minutes.

## Hear your first sounds

A new source plays at once because **Play On Start** is on by default, and it is spatial by default: Min Distance 1 m, Max Distance 50 m, Rolloff 1. You hear it from where the entity stands. When you change the **Clip** of a source, in the Inspector or from a script, the source stops and drops a Play that had not started yet; Play then starts the new clip.

:::::steps

1. Import `Coin.ogg` into a `Sounds` folder of your project's assets, then select it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Content Browser, press **Import** and choose the file, or drop it onto the editor. Select the new asset, open the **Asset** tab and press **Play** under **Preview**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Sounds/Coin.ogg", "directory": "Sounds" } }
   ```

   :::
   ::::

   **You should see:** a waveform, the picture of the wave: the louder the sound, the taller the line. A short chime, a fraction of a second long, plays with a moving line over the waveform.

   **If you do not see it:** the **Play** button is disabled when the editor found no sound device. Check your system's output, then start the editor again.

   ::figure{id=asset-preview}

2. Create an entity named `Hum` with an audio source, and set its clip.

   ::::tabs{sync=how}
   :::tab[In the editor]
   In the Hierarchy press **+** and choose **Audio Source**. Select the entity, then drag `Coin.ogg` from the Content Browser into the **Clip** field of the Inspector. Tick **Loop** so you can hear it repeat.
   :::
   :::tab[With a command]

   ```json
   { "command": "entity.create", "parameters": { "name": "Hum", "components": { "AudioSource": { "Clip": "Sounds/Coin.ogg", "Loop": true } } } }
   ```

   :::
   ::::

   **You should see:** the Inspector with **Play On Start** ticked, **Volume** 1, **Pitch** 1 and **Spatial** ticked. Nothing sounds yet, because the scene is not playing.

   **If you do not see it:** if the new entity has no **Clip** field, you made a plain entity; choose **Add Component** in the Inspector and add **Audio Source**.

3. Press **Play** and listen.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**. While the game runs, change **Volume** and **Pitch** of `Hum` and listen to each change.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start" }
   ```

   Then ask what plays with `{ "command": "audio.state" }`; it answers only while the game runs.
   :::
   ::::

   **You should see:** the chime repeating, and the voice of `Hum` in the answer of `audio.state`, with `playing` true.

   **If you do not see it:** Strata decodes the file in the background. A source whose clip is still loading starts when the clip is ready. If you hear nothing for seconds, check that the clip field is not empty.

4. While the game plays, move the source and the listener, and change the distance fields.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select `Hum` and change its **Translation** in the Inspector (try 0, 0.5, 0, then 0, 0.5, 30). Change **Max Distance** to 5 and **Rolloff** to 3 and compare. Press **Stop** when you are done, because changes made while playing are discarded.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.set", "parameters": { "entity": "<the ID of Hum>", "component": "Transform", "values": { "Translation": [0, 0.5, 30] } } }
   { "command": "component.set", "parameters": { "entity": "<the ID of Hum>", "component": "AudioSource", "values": { "MaxDistance": 5, "Rolloff": 3 } } }
   ```

   Commands take the identifier (ID) that `entity.create` answered, not the name. Then `play.stop`.
   :::
   ::::

   **You should see:** the chime fading as the source goes away, and staying at a low steady volume beyond Max Distance. Sources left or right of the camera sound louder in the matching speaker.

   **If you do not see it:** a source with **Spatial** cleared ignores all of this and plays at full volume from every direction.

5. Make the ball the listener: give it an **Audio Listener** and disable the camera's.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the Ball, choose **Add Component** and add **Audio Listener**. Select Main Camera and clear **Active** of its Audio Listener, because the first active listener in the Hierarchy wins.
   :::
   :::tab[With a command]

   ```json
   { "command": "component.add", "parameters": { "entity": "<the ID of Ball>", "component": "AudioListener" } }
   ```

   Then use `component.set` on the Main Camera's `AudioListener` with `{ "Active": false }`; while playing, `audio.state` names the Ball as `listener`.
   :::
   ::::

   **You should see:** with the game running and the ball rolling, the chime of `Hum` follows the ball's distance, not the camera's.

   **If you do not see it:** if nothing changed, the camera's listener is still active. Check that its **Active** box is clear.

:::::

Delete `Hum` before you continue, or clear its **Loop** and **Play On Start**: Coin Run needs no humming. Keep the ball's Audio Listener.

::checkpoint{stage=1}

::figure{id=inspector-source}

## Give the coin its sound

The coin destroys itself at once, so its sound needs no entity: that is the job of a one-shot.

The clip must be in memory when the coin is collected. An asset loads in the background and Strata never stops a frame to wait for it. A script that asks for a clip only at the moment it needs it gets nothing, because the load has only started.

The fix is to request the clip early, in `OnCreate`, which runs when the game starts. `Assets::RequestLoad` asks the engine to load it and keep it ready. A one-shot whose clip is still loading waits at most 0.25 s of game time; if the clip is not ready by then, the sound is dropped and the Console shows a warning.

:::rule
Never block a frame on an asset: request what you will need early. This keeps frames steady; the loading page [Residency](../assets/residency.md) gives the full reason.
:::

Your `Coin` script needs two changes. The first is a private member and the request. `Assets::Find` returns the handle of the asset at a path, and `RequestLoad` starts loading it.

```pseudocode
private:
	AssetHandle m_Sound;

void OnCreate() override
{
	m_Sound = Assets::Find("Sounds/Coin.ogg");
	Assets::RequestLoad(m_Sound);
}
```

The second change goes in `OnTriggerEnter`, right where the coin is collected and before the coin destroys itself. Put it and `GetEntity().Destroy();` in braces under the `if`. The one-shot plays at the coin's :term[world position]{id=world-position}, so it comes from where the coin was.

```pseudocode
Audio::PlayOneShotAt(m_Sound, GetTransform().GetWorldPosition());
```

A script rebuilt while the game runs gets `OnReload` instead of `OnCreate`, and its members that are not :term[script fields]{id=script-field} start empty. Give `Coin` an `OnReload` that calls `OnCreate`, so the rebuilt script finds and requests the clip too.

:::::steps

1. Find the clip's path: right-click `Coin.ogg` in the Content Browser and choose **Copy Path**.

   ::::tabs{sync=how}
   :::tab[In the editor]
   The path is relative to the project's assets folder and uses `/`, so you get `Sounds/Coin.ogg`.
   :::
   :::tab[With a command]
   This step has no menu or button: run the command.

   ```json
   { "command": "asset.list", "parameters": { "type": "AudioClip" } }
   ```

   :::
   ::::

   **You should see:** the text `Sounds/Coin.ogg` ready to paste.

   **If you do not see it:** if the path has a drive letter, you copied the file from the system; copy from the Content Browser.

2. Edit your `Coin` script: add a handle field, find and request the clip in `OnCreate`, and play it where the coin is collected.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Open `Scripts/Coin.cpp` in your code editor and make the changes shown above the steps. The checkpoint download holds the result.
   :::
   :::tab[With a command]
   This step edits a file in your code editor; there is no command for it.
   :::
   ::::

   **You should see:** a script that finds the clip once and plays it where the coin is.

   **If you do not see it:** if your `OnCreate` already exists, add the two lines to it rather than adding a second function.

3. Build, play, and collect a coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Press **Play**: the editor builds the changed script first. Roll the ball into a coin.
   :::
   :::tab[With a command]

   ```json
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "input.sequence", "parameters": { "events": [ { "step": 0, "key": "S", "action": "tap", "steps": 150 } ], "steps": 180 } }
   ```

   **S** rolls the ball into the coin at 0, 0.8, 3; `audio.state` then shows `oneShots` `played` 1, `dropped` 0. Then `play.stop`.
   :::
   ::::

   **You should see:** the chime from the coin's place, louder when you are near it, and no warning in the Console.

   **If you do not see it:** if the build fails, `script.status` lists the errors. If the coin is silent, `audio.state` shows `dropped` counted in its `oneShots` field.

4. Skip the request on purpose to see the failure. Put `//` in front of the line `Assets::RequestLoad(m_Sound);`, which turns it into a comment that the build ignores, then play and collect a coin.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Edit the script and press **Play**. Remove the `//` afterwards.
   :::
   :::tab[With a command]
   Play and roll as in step 3, then read the log:

   ```json
   { "command": "log.read", "parameters": { "newest": true, "limit": 50 } }
   ```

   Then `play.stop`, remove the `//` and run `script.build`.
   :::
   ::::

   **You should see:** possibly nothing, because a short clip can load within 0.25 s of game time. When the load is slower, the first coin is silent and the Console shows `Audio: dropped a one-shot of 'Sounds/Coin.ogg': its clip took longer than 0.25 s to load`.

   **If you do not see it:** the clip was fast. The drop is real for big clips and slow disks, which is why the request belongs in `OnCreate`.

:::::

::checkpoint{stage=2}

::figure{id=coin-console crop=log}

## Make the ball sound when it hits

A thud should be louder for a hard hit. The ball's script receives `OnCollisionEnter` when a contact begins, and the contact carries the point and the normal, the direction that points from the ball to the other body. It does not carry the force of the hit, so the script computes a speed from the bodies' velocities.

:::question
The code below uses classes and `override`: see [Classes and inheritance](../basics/cpp-classes.md) if they are new.
:::

The Physics Playground does this in its `Impact` script. Its method reads each body's velocity and takes how fast they move apart along the normal. That is a dot product: multiply the x, y and z parts of the velocity by those of the normal and add the three results. Because the normal has length 1, the sum is the part of the velocity that points along it. It then adds half of the larger speed and turns the result into a volume.

```cpp src="Samples/PhysicsPlayground/Scripts/Impact.cpp#L48-L61" symbol="Impact::OnCollisionEnter"
void OnCollisionEnter(const Collision& collision) override
{
	// The contact is reported after the step that resolved it, so the bodies already move apart: how fast they move
	// along the contact's normal now (a bounce keeps most of the impact's speed, a thud little), plus how fast either
	// still moves, tells a hard hit from a touch without tracking every body's velocity every step.
	const glm::vec3 own = GetEntity().GetRigidBody().GetLinearVelocity();
	const glm::vec3 other = collision.Other.IsValid() ? collision.Other.GetRigidBody().GetLinearVelocity() : glm::vec3(0.0f);
	const float separating = std::abs(glm::dot(own - other, collision.Normal));
	const float speed = separating + 0.5f * std::max(glm::length(own), glm::length(other));
	if (speed < MinSpeed || !m_Sound.IsValid() || !TakeSoundBudget())
		return;
	const float volume = std::clamp(speed / FullVolumeSpeed, 0.1f, 1.0f);
	Audio::PlayOneShotAt(m_Sound, collision.Point, volume, 0.9f + 0.2f * std::min(1.0f, speed / FullVolumeSpeed));
}
```

1. **Line 48:** `OnCollisionEnter` runs on the main thread after the physics step that made the contact.
2. **Lines 53–55:** the ball's velocity, the other body's (zero when the contact has no other entity) and their separating speed along the normal.
3. **Line 56:** the separating speed plus half of the faster body's speed, in metres per second.
4. **Line 57:** a touch below the minimum speed makes no sound. The Playground also checks a budget here; this page omits it.
5. **Lines 59–60:** the volume rises with the speed until it reaches full volume, and the sound plays where the bodies met.

A worked example. When the event arrives, the ball still moves at 6 m/s along the normal and the ground does not move. The dot product of the velocity difference with the normal is then 6 m/s, so the separating speed is 6 m/s. The larger speed is also 6 m/s, so the speed is 6 + 0.5 × 6 = 9 m/s.

The volume is 9 / 10 = 0.9 and the pitch is 0.9 + 0.2 × 0.9 = 1.08. A slow touch at 0.8 m/s along the normal gives 0.8 + 0.5 × 0.8 = 1.2 m/s. That is below the minimum of 1.5 m/s, so nothing plays.

:::why
The contact event reports only that a contact began, with a point and a normal. Strata gives scripts no stay event and no impulse of the contact, so the script reads velocities instead. A thud after the step looks like speed along the normal, plus a share of the speed that remains.
:::

:::::steps

1. Import `Soft.ogg` into `Sounds/Impacts`, then create the `Bump` script and build it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import the file as in the first section, into the folder `Sounds/Impacts`. In the Content Browser choose **New** and make a script named `Bump`, replace its code with the file `Bump.cpp` of this page's checkpoint download, and press **Play** to build.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/PhysicsPlayground/Assets/Sounds/Impacts/Soft.ogg", "directory": "Sounds/Impacts" } }
   { "command": "script.create", "parameters": { "class": "Bump" } }
   ```

   Then put the download's code into `Scripts/Bump.cpp` and run `script.build`.
   :::
   ::::

   **You should see:** a successful build, and `Bump` in the list of :term[script classes]{id=script-class}.

   **If you do not see it:** the diagnostics of `script.status` name the line of the error.

2. Add `Bump` to the Ball and play.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Select the Ball, choose **Add Component**, then **Script**, and pick `Bump`.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.add", "parameters": { "entity": "<the Ball's id>", "class": "Bump" } }
   { "command": "play.start", "parameters": { "paused": true } }
   { "command": "play.step", "parameters": { "steps": 120 } }
   ```

   The ball falls onto the ground; `audio.state` counts one thud in `oneShots`. Then `play.stop`.
   :::
   ::::

   **You should see:** a soft thud where the ball lands, loud after a fall and silent while it rolls gently.

   **If you do not see it:** the Console warns `Bump: there is no asset at Sounds/Impacts/Soft.ogg` when the file is in another folder. Move it, or change the path in the script.

:::::

The Playground's script also budgets its sounds per second, for pours of hundreds of bodies; see [Recipes](recipes.md).

::checkpoint{stage=3}

::figure{id=impact-clip}

## Add music and a volume option

Music is long, loops, and has no place in the world. Clear **Spatial**, so it plays at the same volume from everywhere, and set **Loop**.

The clip has a **Load Mode** in its :term[import settings]{id=import-settings}. **Decompressed** decodes the file once when it loads, which suits short effects: the chime and the thud. **Streamed** keeps the compressed bytes and decodes them as they play, which suits long music, and a file over 1 MiB starts as Streamed. A Streamed clip is not read from the disk as it plays: the bytes are all in memory, and only the decoding is spread over time.

:::::steps

1. Import `Complete.ogg` as your music, check its **Load Mode** in the Asset tab, and make a source for it.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Import the file into `Sounds/Music`. Select it, find **Load Mode** in the **Asset** tab and choose `Streamed`: the small file starts as `Decompressed`. Create an Audio Source named `Music` as before, set its **Clip**, tick **Loop** and clear **Spatial**.
   :::
   :::tab[With a command]

   ```json
   { "command": "asset.import", "parameters": { "file": "<release folder>/Samples/ThirdPerson/Assets/Sounds/Complete.ogg", "directory": "Sounds/Music" } }
   { "command": "asset.setImportSettings", "parameters": { "asset": "Sounds/Music/Complete.ogg", "settings": { "LoadMode": "Streamed" } } }
   { "command": "entity.create", "parameters": { "name": "Music", "components": { "AudioSource": { "Clip": "Sounds/Music/Complete.ogg", "Loop": true, "Spatial": false } } } }
   ```

   Before the change, `asset.info` shows `LoadMode` `Decompressed`.
   :::
   ::::

   **You should see:** the tune starting when you press **Play** and repeating, at the same volume wherever the ball is.

   **If you do not see it:** if the volume changes with distance, **Spatial** is still ticked.

2. Add a `VolumeKeys` script to a new entity: the two keys change `Audio::SetMasterVolume`.

   ::::tabs{sync=how}
   :::tab[In the editor]
   Create the script `VolumeKeys` as before and add it to an entity named `Game`. Replace the new file's text with the file below and save.
   :::
   :::tab[With a command]

   ```json
   { "command": "script.create", "parameters": { "class": "VolumeKeys" } }
   ```

   Replace its text with the file below in your code editor, run `script.build`, create `Game` with `entity.create` and attach the class with `script.add`. While playing, `input.key` `Minus` takes `masterVolume` in `audio.state` from 1 to 0.9; two taps of `Equal` make it 1.1.
   :::
   ::::

   **You should see:** after a build, the music getting quieter with **-** and louder with **=** while the game plays.

   **If you do not see it:** if a key does nothing, check the key names in the code; the keys are the ones on the main keyboard row.

:::::

The master volume is the volume of everything the game plays, one number: 1 is unchanged. Look at how the two keys of `VolumeKeys` change it in steps of 0.1.

```cpp src="book:tutorials/make/sound/VolumeKeys.cpp#L1-L22"
#include "StrataScript/StrataScript.h"

using namespace Strata;

// Changes the game's master volume in steps of 0.1: Minus lowers it, Equal raises it.
class VolumeKeys : public Script
{
public:
	void OnUpdate(float deltaTime) override
	{
		float volume = Audio::GetMasterVolume();
		if (Input::IsKeyPressed(Key::Minus))
			volume -= 0.1f;
		if (Input::IsKeyPressed(Key::Equal))
			volume += 0.1f;
		Audio::SetMasterVolume(volume);
	}
};

ST_SCRIPT_CLASS(VolumeKeys)
{
}
```

1. **Lines 11–15:** the script reads the volume, changes it by 0.1 for a press of **-** or **=**, and writes it back.
2. **Lines 20–22:** the class has no field, so its registration is empty.

The master volume stays after the scene ends, like the sound option of a game. The editor remembers its own volume when play starts and restores it at **Stop**, so a quiet test game never leaves the editor quiet. Press **Ctrl+S** to save the scene when you are happy.

### What Strata does not do here

Sound in Strata is deliberately small. Each of these is absent at this version:

- Buses (groups of sounds mixed together), effects such as echo, and a model of the head and ears.
- Music systems and ducking, the lowering of music when speech plays.
- Occlusion, the muffling behind a wall, and echo zones.
- Virtual voices and voice priorities. At most 64 one-shots play at once in a scene; beyond, the oldest is cut off.
- A listener per world: the audio engine has one.

::checkpoint{stage=4}

::figure{id=music-source}

## Summary

- You placed a source with a clip and tuned its distance, and moved the listener to the ball.
- A one-shot is dropped when its clip is not loaded within 0.25 s, so you request the clip first.
- The coin requests its clip in `OnCreate` and plays it with `Audio::PlayOneShotAt`.
- The impact volume comes from the separating speed plus half the faster speed, divided by a full-volume speed.
- Music is a looping source that is not spatial, with a Streamed clip, and the master volume comes from two keys.

## Check yourself

1. A source stands 5 m from the listener with Min Distance 1 m, Max Distance 50 m and Rolloff 1. What gain does the inverse model give?

   :::answer{tests="spatial-source"}
   The gain is 1 / (1 + 1 × (5 − 1)) = 0.2. The source plays at one fifth of its volume.
   :::

2. Your coin script calls `Audio::PlayOneShotAt` on collection but never requests the clip, and the first coin is silent with a warning in the Console. Why?

   :::answer{tests="early-request"}
   The clip loads in the background. A one-shot waits at most 0.25 s of game time for it, then drops it and warns. Requesting the clip in `OnCreate` has it ready.
   :::

3. Where does the coin sound come from in the world, and which call does that?

   :::answer{tests="coin-oneshot"}
   The sound comes from the coin's world position. `Audio::PlayOneShotAt` takes that position, so the sound is spatial; `Audio::PlayOneShot` would play it without a place.
   :::

4. The ball falls at 4 m/s onto still ground, along the normal. With a full-volume speed of 10 m/s, what volume does the impact script play?

   :::answer{tests="impact-volume"}
   The separating speed is 4 m/s, and half the larger speed adds 2 m/s, so the speed is 6 m/s. The volume is 6 / 10 = 0.6.
   :::

5. Which two settings does a music source need so the music has the same volume everywhere and repeats?

   :::answer{tests="music-volume"}
   **Spatial** cleared and **Loop** ticked. A Streamed clip suits its length, and `Audio::SetMasterVolume` sets the game's volume.
   :::

## Exercises

1. **Basic.** Place a looping source named `Campfire` at 6 m from the origin that fades out for the listener between 2 m and 15 m, with Rolloff 2. What gain does it give at 6 m?

   :::answer[Worked solution]{tests="spatial-source" solution="tutorials/make/sound/exercise-1.tutorial.json"}
   Create the source as in the solution file. At 6 m the gain is 2 / (2 + 2 × (6 − 2)) = 0.2.
   :::

2. **Medium.** Make the thud's pitch depend on the speed in the other direction: low for hard hits. Which line changes, and what are the pitches at 1.5 m/s and 10 m/s?

   :::answer[Answer]{tests="impact-volume"}
   Change `0.9f + 0.2f * ...` to `1.1f - 0.2f * ...`. At 1.5 m/s the pitch is 1.1 − 0.2 × 0.15 = 1.07; at 10 m/s it is 0.9.
   :::

3. **Hard.** Keep a rarely used clip loaded, so it plays at once when needed. Which two calls do you use?

   :::answer[Answer]{tests="early-request"}
   `Assets::RequestLoad` in `OnCreate` keeps the clip loaded; `Audio::PlayOneShot` plays it later without a wait.
   :::

## Where it lives in Strata

The components are in `Strata/src/Strata/Audio/AudioComponents.h` and the scene system that plays sources and one-shots in `Strata/src/Strata/Audio/AudioSystem.cpp`. The scripts' `AudioSource` and `Audio` are in `StrataScriptCore/Include/StrataScript/Audio.h`. The impact script of the Physics Playground is `Samples/PhysicsPlayground/Scripts/Impact.cpp`. The editor's waveform preview is in `StrataEditor/src/Editor/AudioPreview.cpp`.

## Further reading

- The miniaudio documentation: the audio library under Strata's mixer, with its attenuation models (intermediate).
- Kenney's sound packs: the free sources of the sample clips (beginner).
