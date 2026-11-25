# Part review: editor/worlds (group 2 of 3)

- unclear: the first Mermaid diagram's node read `Scene :term[sub-scenes]{id=sub-scene}`, a term mark inside a diagram label that would show as raw text; now `Scene sub-scenes` (the term keeps its mark at its first prose use under "Re-celling").
- wrong: check-yourself 4's answer said the next save "writes the World document again with the index entries, and lists any cell whose file already exists"; `EditorWorld::FinishSave` refreshes index entries only for the cells that save writes, lists the cells made in memory whose documents now exist (`m_NewCells`), and writes the document only when it differs (`EditorWorld.cpp:721-743`, header comment at `EditorWorld.h:151-155`); the answer now says so.
