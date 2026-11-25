# Part review: editor/undo (group 1 of 3)

- wrong: exercise 1's answer said "the undo removes the second step"; `UndoStack::Undo` only moves the position back and the step waits as the redo branch (`StrataEditor/src/Editor/UndoStack.cpp:156-186`); now "reverts the second step, which waits as the redo branch".
