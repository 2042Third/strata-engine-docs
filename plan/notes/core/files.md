# Notes: `core/files`

## New terms

None proposed. The page defines the glossary's own entries: atomic write (with "staged file"), atomic rename, TOCTOU,
file lock, file mode 0700 and DACL. "Private folder" is explained in a sentence, not in bold, because the glossary
holds no such entry under that name (see Requests).

## Requests

- `tools/data/extra-words.txt`: "discretionary", the first word of the expansion of DACL (discretionary access control
  list). The `word-list` finding for it is left until the word is added.
- Hosts for `tools/external-hosts.txt`: `sqlite.org` ("Atomic Commit In SQLite"), `danluu.com` ("Files are hard"),
  `man7.org` (the `rename(2)` manual page). The three Further reading entries cite them without a link until then.
- Glossary: the brief's items `foundation:630`, `foundation:631` and `automation:757` name entries (reparse point,
  junction, symbolic link, private directory, owner-only file) that the term list of the brief does not carry and the
  glossary does not match; the page explains symbolic links, junctions and private folders in plain sentences. Decide
  whether they become entries homed here (the book calls a directory a folder).
- Figure `foundation:422` (the atomic write with a crash at each point) is carried by the toy sketch and its output,
  not drawn; the TOCTOU "check and read through one handle" picture is not drawn either. The page has no figures file.

## Not verified

- That the usual local file systems of Windows, Linux and macOS make a replacing rename one step: an operating system
  behaviour, stated from general knowledge, not from the pin.
- That `std::filesystem::rename` replaces an existing file on every platform of the pin's compilers: relied on by the
  engine and covered by the test "A committed write replaces the file" (`Core.AtomicFileWriter`), not read in a library.
- That a POSIX `rename` never fails because a reader holds the destination open: the pin's code has no retry there.
- What the three Further reading entries say (SQLite's atomic commit page, "Files are hard", Microsoft's `MoveFileEx`
  page): not fetched.
- The Python kill loop of exercise 2 was run once on Windows (40 rounds a mode: 4 damaged in place, 0 atomic); the
  in-place count varies with timing.
- The claim that Windows programs written only for Windows use UTF-16 paths, and that databases use journals, are
  general statements in the alternatives table, not claims about Strata.

## Findings not applied

- `foundation:529` asks for a kill loop around `FileSystem::WriteText`. A loop around the engine's own call needs the
  engine built, so exercise 2 kills a Python writer that follows the same temporary-file-and-rename steps, and exercise
  3 traces `WriteText` itself.
- `foundation:125`: what the asset manager does with watcher changes is left to `assets/importing`, as the brief says.
- `RemoveTrailingSeparators`, `GetFileSize`, `GetLastWriteTime`, `IsSameFile` and `CreatePrivateDirectory` are named or
  left out; none is needed to teach the three rules.
- All other open findings of the brief: `foundation:699` applied (the manifest's part in the UTF-8 rule is told, and
  the log's narrow path is called no defect), after checking `Strata/src/Strata/Core/Log.cpp` and `CMake/Strata.manifest`
  at the pin; the manifest is linked into `StrataEditor`, `StrataRuntime`, `StrataCLI` and `StrataTests`.

## Since

- `FileSystem` with its temporary-file write exists in the first commit `a0f2865f` (2026-10-08), before the tag
  `v0.3.0` (2026-10-13): since 0.3.0.
- `AtomicFileWriter` (`9b72c08d`, 2026-10-13) and the one-handle reads and `BoundedRead` (`dd367dab`, 2026-10-09) came
  in the same weeks; the page's subject as a whole is older than the first tag.

## Clerk

- `extra-words.txt`: discretionary.
- `external-hosts.txt`: `sqlite.org`, `danluu.com`, `man7.org` (front pages fetched: SQLite, Dan Luu's posts, man7.org).
- Left for the planner: entries for reparse point, junction, symbolic link, private directory and owner-only file (the page explains them without bold, so a term would fail `term-defined`); the figures.
