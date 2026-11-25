# Part review: editor/deferred-commands (group 1 of 3)

- unclear: the paragraph after the `FrameTimeRecorder` quote let the reader take `c_FrameTimeReserve` as `editor.wait`'s reserve; at the pin `editor.wait` reserves exactly its count of frames and only `scene.open` and `project.export` reserve `c_FrameTimeReserve` (`StrataEditor/src/Editor/EditorStateCommands.cpp:914`, `EditorSceneCommands.cpp:109`, `EditorAssetCommands.cpp:502`); the paragraph now says so.
