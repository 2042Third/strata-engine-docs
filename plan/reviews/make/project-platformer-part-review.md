# Part review: make/project-platformer

- wrong: the course table's y was "the height of the block's centre"; the kit block's origin is its base (the glb spans y 0 to 2), as the paragraph above says; now "the block's base".
- step: stage 3 step 6 said the robot slides "in its pose without moving its legs"; the importer gives the model an Animator that plays the file's first clip (`GltfImporter.cpp`, Play On Start), so in play the robot dances; corrected.
- step: stage 5 step 3 said the Scene view shows the robot "in the Idle pose, breathing a little"; edit mode shows the rest pose by default (`EditorViewport.h`, `AnimationEditPose::Rest`, as make/animation says); now rest pose until play starts it in Idle, and the failure case is a robot that still dances in play.
- wrong: the jump pad's failure line said the player's centre must pass within 0.8 m of the pad's centre; the capsule (radius 0.4) overlaps the box earlier; now the capsule must reach inside 0.8 m.
- step: stage 6 step 9 said the player returns to the second checkpoint after a fall; island C cannot be reached before the platform of stage 7, so the player is back at the first one (the tutorial checks `Checkpoint` 1).
- wrong: stage 9's failure line named "the Console log of the game"; an exported game has no Console, its log is `Game.log` (make/export).
- gap: the Hard exercise asks for the course completed, but its solution checked only a coin; the answer now says how the goal is checked (`Completed` true at (2, 6.1, -40)); its last sentence was shortened to keep the page within XL.
