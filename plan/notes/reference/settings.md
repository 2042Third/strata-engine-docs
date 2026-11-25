# Notes: reference/settings

## New terms

- settings section: a named block of values one part of the engine owns, with a description of allowed values (home: this page; aliases: section).

## Requests

None.

## Hand-written tables

- "What each section is for": scope and editing pages read from Strata/src/Strata/*/*Registration.cpp, StrataEditor/src/EditorLayer.cpp (m_SettingsPages.Register: Input.Actions, Scene.CollisionLayers, Renderer.Quality, Editor.ExternalEditor have custom pages; the others use the generic page).

## Not verified

- The Preferences dialog and Project Settings window open as stated by name only; menu labels were not checked.
- The idle-throttling sentence follows the generated Editor.FrameRate text.

## Findings not applied

- critic-reference-1 (project file table): belongs to reference/worlds-runtime; this page only links it.
- critic-reference-20 applied: the default of Input.Actions is linked to reference/audio-input, but the generated include still shows it (generated file, not editable here).

## Clerk

- Refused: settings section (homed on world/projects-settings; only its home words it).
