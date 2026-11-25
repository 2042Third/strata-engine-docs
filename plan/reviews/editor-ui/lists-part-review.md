# Part review: `editor-ui/lists`

- contradiction: "The font is 16 pixels" stated as a fact, while `editor-ui/shell` gives 14 pixels at 100 % (`EditorFonts.cpp:36`, body size 14); now "suppose the font is 16 pixels", an assumed size (two words cut to stay within L).
- wrong: the payload table's targets omitted the Inspector: `STRATA_ENTITIES` and `STRATA_ASSET` are also accepted by the Inspector's entity and asset fields (`PropertyWidgets.cpp:719`, `:822`); both rows now add "Inspector fields".
