# Part review: `physics/why`

- wrong: Common mistakes said "a script writes a transform field and the body ignores it"; at the pin the script host's `SetTransform` calls `MarkModified` (`Strata/src/Strata/Scripting/ScriptHostAPI.cpp`), so a script's write always reaches the body. Now "engine code writes a transform field".

Checked at the pin: the Playground's 500 balls of four materials, 64 dominoes and 100-ball pour, the warning "has a Rigid Body but no collider; it is not simulated", the 0.5.0 notes (1 cm against 11 to 15 cm of drift, about 40 % faster, bodies added one at a time, triggers without triangle meshes), the 1e5 m body limit, the bullet flag and box3d's static sweep, the files named, and the exercise against its tutorial file.
