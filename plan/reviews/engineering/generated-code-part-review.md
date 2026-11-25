# Part review of `engineering/generated-code`

- order: "two custom commands ... the CMake page taught them": `engineering/cmake` never teaches `add_custom_command`; the sentence now says what a custom command is.
- wrong: the generators table and "Only two generators have a CTest" missed `Tools/ConvertLTCTable.py`, which writes `Renderer/LTCTable.inl` and has the CTest `StrataTools.LTCTable` (selftest, label `tools`, `StrataTests/CMakeLists.txt:375`); a row added, the paragraph says three (split to keep five sentences), Check yourself 4's option C, How it is tested, Changing it safely and Where it lives name it.
