# Notes: `scripting/symbolization`

## New terms

None. The page bolds the glossary's own terms (symbolization, PDB, DbgHelp, inlining, inline frame) and "return addresses", "base address" and "offset", which are explained in plain words.

## Requests

- No figures file: the Problems panel picture (`scripting:435`) needs a project with a crashed script module, which no sample has; the Faults module is a test module. A planner recipe would be needed.
- `tools/data/extra-words.txt`: none needed. "unwind data" and the format name `ELF` stand in code spans.

## Since

`since: 0.3.0`: `Symbolizer` and the Windows and POSIX files came with `48e4c763` ("Create, build, open and debug scripts from the editor"); the inline trace with `1139714d`. `git tag --contains` lists `v0.3.0` first for both, and `Symbolizer.h` at `v0.3.0` already holds `InlinedCall`.

## Not verified

- The table of alternatives (crash dump files with a symbol server, symbolizing libraries and `addr2line`, frame-pointer walks, handlers on the crashing thread) is written from general knowledge; no source was opened.
- That a call instruction is five bytes in the worked example is x64 general knowledge; the addresses and offsets of the example are invented, as the page says.
- That symbol values of a Linux shared library are offsets from its base: the code compares them that way; the ELF specification was not opened.

## Findings not applied

- `scripting:435` figure (Problems panel picture): left out, see Requests; the panel is described in words.
- `new:6` erratum: applied as a caution on the page; `Symbolizer.h:14` at the pin says `dladdr` only.

## Clerk

- Nothing to admit.
- Left for the planner: the figures, layouts, links and other requests of ## Requests that this section does not name.
