# Part review: editor/script-builds (group 2 of 3)

- step: the worked build told the reader to "change the name of the field it uses to one that does not exist"; the class `script.create {"class": "Coin"}` writes (template `behaviour`) declares `Speed` and uses it only in `ST_SCRIPT_FIELD(Speed);` (`ScriptProject.cpp:325-370`); the step now names that line and says to change the name in it to one the class does not declare.
