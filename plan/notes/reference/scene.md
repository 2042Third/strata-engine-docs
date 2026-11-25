# Notes: reference/scene

## New terms

None. The page defines `scene` in bold as the `Scene` class; the glossary homes no term here.

## Requests

None.

## Hand-written tables

All tables except the generated limits table are written by hand, because src/generated/reference/ holds no Scene, Entity, reflection, settings-type or format table.
- Scene API (eight groups): Strata/src/Strata/Scene/Scene.h
- Entity API: Strata/src/Strata/Scene/Entity.h
- Systems table: Strata/src/Strata/Scene/SceneSystem.h and the six *Registration.cpp (Scripting, GameUI, Animation, World, Physics, Audio)
- ComponentFlags, PropertyType, PropertyFlags: Strata/src/Strata/Reflection/ComponentRegistry.h, Property.h
- SettingsFieldType, SettingsScope: Strata/src/Strata/Core/SettingsRegistry.h
- Extra limits table: SettingsRegistry.h, Project/Project.h, Reflection/PropertyBinary.h, Scene/CookedScene.h
- File formats table: SceneSerializer.h, Prefab.h, SceneDocumentReader.cpp, SceneDocumentWriter.cpp, CookedScene.h, Project/Project.h

## Not verified

- Model documents have no file extension listed in the header; the row gives none.
- The `OnRuntimeStart` meaning is kept to "Starts the run".
- Reference page links ../reference/settings.md and the worlds reference are not yet pages.

## Findings not applied

- critic-reference-1 (project file keys table): belongs to reference/worlds-runtime; this page gives the file one row and a paragraph.
- critic-reference-2: applied (each table names its teaching page).
- critic-reference-16: concerns reference/core.
- critic-reference-18: applied (systems table).
- Brief names SettingsRegistry::c_MaxValueBytes; at the pin the constant is SettingsSection::c_MaxValueBytes; the page says so.
- Size lint: the tool compares this page with the M row; known fault for reference pages.

## Clerk

- Refused: the bold words the page defines locally (scene) are not admitted: a reference page restates terms whose homes are their chapters, and the page proposed none.
