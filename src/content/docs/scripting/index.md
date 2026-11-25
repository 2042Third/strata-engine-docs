---
id: scripting/index
title: "Scripting"
description: "The pages of the part on scripting: how game code runs beside the engine, how the pages build on each other and what you can do after them."
tracks: [E]
status: final
generated: index
---

This part explains how game code runs beside the engine without being a piece of it. It starts with the reasons for a separate module, then builds the shared library and the binary contract. The turning point is the engine's side: it loads a module, contains its crashes, names the line of each and calls its scripts in a fixed order. Hot reload, the host functions and a tutorial that adds one follow. At the end you can predict what the engine does with a module that is new, old, broken or rebuilt.
