# Notes: assets/robustness

## New terms

- untrusted input: bytes that come from outside the running program, which may be cut, damaged by an accident or written to cause harm, so the program checks them before use. Home: assets/robustness. Aliases: untrusted file.
- write-ahead ordering: writing the data first and the note that names it last, so that a note never points at data that is not there yet. Home: assets/robustness. Aliases: cache before record.
- cancellation flag: a yes-or-no value the code that wants a job stopped sets, and the job reads at the points where stopping is safe. Home: assets/robustness. Aliases: cancel flag.

## Requests

- Word: "cyclic" (cyclic redundancy check, spelled out at the first use of CRC).
- Names for later pages: SQLite, Dan Luu (cited in Further reading only, which is not read).
- External hosts: sqlite.org and danluu.com are already on the list; the PNG specification, libFuzzer and Git documentation entries are cited without a link.
- Tutorial patch: tutorials/assets/robustness/exercise-3.patch applies to the pin (git apply --check) but was not built or run.

## Since

0.3.0: pack validation on open (wave 2, 0.3.0) and import cancellation (wave 2, 0.3.0) per plan/inventory/assets.md; the import record store is 0.4.0.

## Not verified

- The patch's test was not compiled or run; it assumes GetEntries()[0] is the entry whose first block is Blocks[0] (the sources' order).
- The Roadmap figures (17 imports, 5.6-12 s to 0.06-0.34 s) come from Docs/Roadmap.md at the pin, not measured.
- The claims about PNG, zip, ext4, Git, SQLite, ZFS-style file systems in the approaches table are general knowledge, not cited to a fetched source.
- That cgltf itself checks accessor ranges before the geometry budget is not verified; the page says only that the budget catches the claim.
- ImportContext's texture and glTF check points are from Docs/Architecture.md, not read in each importer.

## Findings not applied

None: the brief lists no open findings.

## Clerk

- Admitted terms homed here: untrusted input (alias untrusted file), write-ahead ordering ("cache before record" is no alias: no page writes it as a name). Refused: cancellation flag, which the glossary homes on assets/importing (only its home words it).
- Admitted to extra-words.txt: cyclic. Admitted to names.txt: SQLite, Dan Luu.
- Left for the planner: the exercise patch's build and run.
