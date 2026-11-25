---
id: engineering/index
title: "Building, testing and releasing the engine"
description: "The pages of the part on building, testing and releasing the engine: how they build on each other and what you can do after them."
tracks: [E]
status: final
generated: index
---

This part follows the engine from a source file to a released archive. It starts with building Strata, and with the CMake files, flags, pinned libraries and generated code that decide what the build holds. The turning point is testing: the idea of a test, then the test program, the kinds of suites, the feature test, the performance lab and a harness that compares two builds. The last pages cover continuous integration (CI), packaging and the review through which a change lands. You can then build and test the engine, choose the test a change needs, and land a change.
