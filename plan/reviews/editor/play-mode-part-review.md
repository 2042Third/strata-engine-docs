# Part review: editor/play-mode (group 2 of 3)

- wrong: the example's `component.set` sent `"entity": "Sun"`; the `entity` parameter is an ID (`EntitySchema`, pattern `^[0-9A-Fa-f]{1,16}$`, `CommandUtils.cpp:73-76`), so the call would be refused; the request now carries an ID, and the paragraph before it says that it stands for the ID `entity.find` returns for `Sun`.
