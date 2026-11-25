# Part review: editor/projects (group 2 of 3)

- wrong: the note on `OpenProject` said the editor calls the blocking form "only at startup without a window"; `EditorLayer` calls it at startup when `OpenStartSceneInBackground` is false, which `EditorApplication.cpp:431` sets for scripted runs (`--frames` or a command script), windowed or not; now "at the startup of a scripted run, one with a command script or the `--frames` option".
- wrong: exercise 2's answer put the template test "beside `ProjectSamplesTests.cpp`"; the templates have their own suite file, `StrataTests/src/Editor/EditorTemplateTests.cpp` (`project.templates`, `project.create with basic3d ...`); now "Add a test to `EditorTemplateTests.cpp`".
