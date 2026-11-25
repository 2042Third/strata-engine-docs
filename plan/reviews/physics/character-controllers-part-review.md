# Part review: `physics/character-controllers` (physics, group 2)

- gap: the toy's text says the circle ends at (1.146, 0.854) "which the program prints", but the sketch had no output fence, so the reader saw no print; added the sketch's `output-of` fence (filled from the real run).
- Checked against the pin without a finding: the component's defaults, `c_PresenceRadiusFraction` and the presence capsule's top and bottom (`MakeCapsule`), `c_LeaveGroundSpeed`, `c_ContactMargin`, `c_MoveIterations`, `c_MoveTolerance`, `c_MinBatchSize`, `c_BatchesPerThread`, `c_CharacterMass`, the external-move tolerance, the radius clamp, the step, slope, push and thread-count tests of `Physics.Character`, the SDK's `Move`, `Jump`, `Teleport`, `GetGroundState`.
