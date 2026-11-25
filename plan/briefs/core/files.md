# Brief: `core/files`

| Field | Value |
| --- | --- |
| Title | Files you can trust |
| Kind | I |
| Size | L |
| Tracks | E |
| Needs | `core/platform`, `basics/bytes` |
| From | new by split of `core/platform`; foundation §1.7 (`FileSystem`, `AtomicFileWriter`, `FileReader`, `FileLock`, `FileWatcher`, `BoundedRead`), concepts 23-24: UTF-8 paths, atomic writes, private files and TOCTOU; home of atomic writes and private files |
| Unit | `plan/allocation/core.md` |

An item's first cell names its source: `<inventory>:<line>` is a line of `plan/inventory/<inventory>.md`.

## `core/files` — Files you can trust

**Covers.** The job: how engine code names, reads and writes files so that no crash, no other program and no other user
leaves it with half a file, a wrong file or a planted one. The problem in a short section: what goes wrong (partial
writes and crashes, readers that see half a file, a rename on Windows that fails while another program holds the file,
the time between checking a file and using it, permissions, links and junctions) and the approaches (writing in place, a
temporary file and a rename, a journal); the rename also makes a folder whole, filled under another name and renamed
into place, as the build's Slang cache is. The map: `FileSystem`, `AtomicFileWriter`, `FileReader`, `FileLock`,
`FileWatcher` and `BoundedRead` in Core, the private-file functions on `Platform`, and their halves per OS. The
contract, text and paths first: strings are UTF-8 `std::string` everywhere; a `std::filesystem::path` made from a narrow
string on Windows uses the process's code page, so paths go through `FromUTF8` and `ToUTF8`, which convert through
`char8_t` and write `/`; the application manifest makes UTF-8 the code page of Strata's programs, as a second line of
defence. Then `FileSystem` (reads without exceptions, whole, a prefix or a range; atomic writes by a temporary file and
a rename; copies that follow no link; containment with `IsInside` and `IsInsideResolved`; `GetUniquePath`; a count of
operations per thread that lets tests prove the main thread did no file I/O); `AtomicFileWriter` and `DocumentOutput` (a
streaming atomic writer with a 1 MB buffer for huge documents written on background threads, `Commit` or `Abort`);
`FileReader` (one open file read at given offsets by many threads); `FileLock` (an exclusive lock between processes,
released when the process ends); `FileWatcher` and `FileChangeNotifier` (a thread that rescans a tree after the OS's
notifications on Windows and by polling elsewhere, and `PollChanges` on the caller's thread); `BoundedRead` (read to the
end with a cap, never trusting a size read earlier); the private-file contract (directories only the user may change,
created for the owner alone and checked when they exist; `WritePrivateFile` through an exclusive temporary file and a
rename; `IsTrustedFile`, and `ReadTrustedFile`, which checks and reads through one handle; `RenameNoReplace`;
`GetUserRuntimeDirectory`). The rules: strings are UTF-8 and convert at `std::filesystem`'s boundary; every write is
atomic; files only the user may change go through the private-file functions. The toy is an atomic write in 30 lines,
with a crash at each point; the real code is the atomic write, the UTF-8 conversion and the private-directory contract
in `Platform.h`. The page's example: a document saved while the process is killed at each step leaves the old file or
the new one, never half of either. The exercises kill a writing process in a loop, and trace `WriteText` to its rename
on the reader's OS. `FileLock` comes with its term, file lock, and the build's users of such locks (Slang's fetch,
`PerfLock.py`). At the end the reader can write a file that survives a crash, read a file someone else could have
changed, and convert a path without mangling its name.

**Leaves out.**

- Text encodings and bytes in general → `basics/bytes`
- Untrusted contents: validation, checksums and bounded sizes → `assets/robustness`
- Scene documents written as a stream → `world/serialization`
- Saves that never stall the editor → `editor/saving`
- Asset hot reload from file changes → `assets/importing`
- Session files and the token's private files → `automation/security`
- Save files of games → `scripting/host-api`

**Fit.** `fits`: about 4,550 words against L (5,000). The contract of `FileSystem`, the atomic writers and the
private-file functions, with three quotes, takes the most, then the two concepts (text and paths, safe writing and
trust); two exercises follow.

**Items.**

| Item | Type | Role | What the page takes from it |
| --- | --- | --- | --- |
| `foundation:317` | concept | home | Text and paths: UTF-8 against UTF-16 and Windows' wide calls, a path made from a narrow string on Windows, `char8_t`, generic separators; the mistake `path(std::string)` |
| `foundation:321` | concept | home | Safe writing and trust: partial writes, a temporary file and a rename, Windows' retried rename, TOCTOU, POSIX modes and Windows DACLs, links and junctions |
| `foundation:122` | feature | home | `FileSystem` |
| `foundation:123` | feature | home | `AtomicFileWriter` and `DocumentOutput` |
| `foundation:124` | feature | home | `FileReader` |
| `foundation:125` | feature | home | `FileWatcher` and `FileChangeNotifier`; how the asset manager acts on their changes is `assets/importing`'s |
| `foundation:126` | feature | home | `FileLock` |
| `build-test:642` | term | home | File lock: an OS lock on a file that serializes processes, the term of `FileLock`, with the build's users named (Slang's fetch at the first configure, `PerfLock.py`); passed by `engineering` (the merge "File lock"); `engineering/third-party` links it |
| `foundation:127` | feature | home | `BoundedRead` |
| `foundation:121` | feature | home | Private directories and files: one contract on every OS |
| `foundation:367` | code | home | `Strata/src/Strata/Core/FileSystem.cpp:102-135`: the atomic write (temporary file, flush, rename, clean-up); with `FileSystem.cpp:341-350`, the UTF-8 conversion through `char8_t` |
| `foundation:368` | code | home | `Strata/src/Strata/Core/Platform.h:92-129`: a security contract written as the interface's comment (private directories) |
| `foundation:422` | figure | home | The atomic write with a crash at each point (the old file or the new one), and the check and read through one handle |
| `foundation:479` | rule | home | Strings are UTF-8; convert at `std::filesystem`'s boundary with `FromUTF8` and `ToUTF8` |
| `foundation:481` | rule | home | Files only the current user may change go through the private-file functions; trusted files are checked and read through one handle |
| `foundation:483` | rule | home | Every write is atomic (a temporary file and a rename) |
| `foundation:529` | hands-on | home | A file written atomically with `FileSystem::WriteText` while the process is killed in a loop: always the old file or the new one |
| `new:31` | hands-on | home | Trace it yourself: `FileSystem::WriteText` followed with the debugger or a search to the temporary file, its flush and the `std::filesystem::rename` that replaces the old file, and `WritePrivateFile` on the reader's OS to its own rename (`MoveFileExW` on Windows); the steps written down with what a crash between each leaves. Evidence: `Strata/src/Strata/Core/FileSystem.cpp:102-146`; `Strata/src/Platform/Windows/WindowsPlatform.cpp:658` |
| `foundation:628` | term | home | Atomic write |
| `editor-core:702` | term | home | Atomic write, the same entry as `foundation:628` |
| `foundation:629` | term | home | TOCTOU |
| `foundation:630` | term | home | Two entries: DACL and file mode 0700 |
| `foundation:631` | term | home | Three entries: reparse point, junction and symbolic link |
| `automation:757` | term | home | Two entries: private directory and owner-only file (POSIX modes 0700 and 0600, a protected DACL on Windows); the session files kept in them are `automation/security`'s |
| `build-test:643` | term | home | Atomic rename: the step that makes a write atomic, for a file or for a folder filled under another name, as the build's Slang cache is (`engineering/third-party`) |
| `foundation:699` | open | home | Checked at the pin: `Strata/src/Strata/Core/Log.cpp:224` hands spdlog the log's path as a narrow string, and `CMake/Strata.manifest:2-3, 7` makes UTF-8 the code page of the editor, the runtime, the CLI and the tests, so the narrow path is UTF-8 there; the page tells the manifest's part in the UTF-8 rule and calls nothing a defect |
| `foundation:627` | term | link | UTF-8, UTF-16 and code page, whose entries are `basics/bytes`' |
| `build-test:48` | feature | use | The Windows application manifest: UTF-8 as the process's code page, long paths |

**Assumes.**

| Concept | Taught by | Depth |
| --- | --- | --- |
| UTF-8 and text encodings | `basics/bytes` | must |
| The platform seam and the `Platform` class | `core/platform` | must |
| Threads and the job system's pools | `core/jobs` | must |
| The rule that the main thread does no file I/O | `core/jobs` | must |
| Writing and running one test case | `core/first-change` | must |
| `std::filesystem::path` | `basics/cpp-modern` | helps |
| Folders, paths and permissions as a user meets them | `basics/tools` | helps |

## Terms the glossary homes on this page

From `src/content/glossary.json`. The page defines each in **bold** somewhere on it, in one sentence that says
what it is (`term-defined`); a term marked (use) is homed in `use`, for a game maker. Where the Items above
disagree, the glossary's home wins.

| Id | Term | Aliases |
| --- | --- | --- |
| `atomic-rename` | Atomic rename | - |
| `atomic-write` | Atomic write | staged file |
| `dacl` | DACL | - |
| `file-lock` | File lock | - |
| `file-mode-0700` | file mode 0700 | - |
| `toctou` | TOCTOU | - |
