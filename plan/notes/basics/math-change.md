# Notes: basics/math-change

## New terms

None proposed. The page defines the fifteen glossary terms of its brief in bold (rate of change, derivative, accumulation, integral, velocity, acceleration, numerical integration, time step, explicit Euler method, semi-implicit Euler method, Newton's laws of motion, force, mass, momentum, impulse). "Slope" and "explode" are used without bold.

## Requests

- Words: "newton" (12 uses) and "newtons" (13 uses), the unit of force, for `tools/data/extra-words.txt` next to the other units; the page needs them in nearly every Newton and impulse sentence, and "N" alone would be unreadable for the least prepared reader.
- Host for Further reading (no link written, so none needed yet): 3blue1brown.com, for the video series "Essence of calculus".
- Figures (kind `diagram`, in `src/content/figures/basics/math-change.json`, not drawn yet): `position-slope`, `speed-rectangles`, `two-springs`, `exploding-step`. The numbers of the last two come from the sketches `basics-math-change-spring.cpp` and `basics-math-change-explode.cpp`.
- Warnings left: the lint's `passive` and `noun-stack` warnings are copular uses ("is the speed"), titles of linked pages or math ("is added"); no real passive was left.

## Not verified

- That the speed from two positions of a fixed step is close to `RigidBody::GetLinearVelocity`, and differs after a collision (Practice 5): general knowledge; no engine program was started.
- That a jump-pad trigger needs no further setup than "a pad that is a trigger" (`IsTrigger` is a property of the `RigidBody` component at the pin; the Coin Run scene's setup is `make/project-coin-run`'s).
- What `LinearDamping` of 0.05 does exactly (only its default at the pin, `Strata/src/Strata/Physics/PhysicsComponents.h`, is stated; the page says "loses a little speed").
- The error formula (half gravity times step times time), the stability limit of 2 s and the 1.25 energy factor are general mathematics, confirmed by the page's sketches, not by the engine.
- That `light/atmosphere` and `audio/spatial` use accumulation and velocities as the last section says: taken from the brief.

## Findings not applied

None: the brief lists no open findings.

## Since

Not applicable: a primer has no `since`.

## Clerk

- `extra-words.txt`: "newton", "newtons" (the unit). `www.3blue1brown.com` admitted (see `basics/math-matrices`).

## Track walk E-final-4

Each sketch of the page compiled with `cl /std:c++20 /EHsc` (Visual Studio 2026, 19.50) and with g++ 15 `-std=c++20`, glm from the 0.8.0 package's `StrataScriptCore/ThirdParty/glm`; both printed the same output (`docs-work/walkfix-E4/cl/`, 2026-11-24). The exact Windows line of the page was run in PowerShell in a Visual Studio developer environment (`cmdtest/`).
