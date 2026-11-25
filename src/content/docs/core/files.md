---
id: core/files
title: "Files you can trust"
description: "How Strata names, reads and writes files so that a crash, another program or another user never leaves it with half a file, a wrong file or a planted one."
kind: internals
size: L
tracks: [E]
needs: [core/platform, basics/bytes]
time: 85
learn:
  - id: atomic-write
    text: explain why a write through a temporary file and a rename leaves the old file or the new one after a crash
  - id: utf8-paths
    text: explain why a path made from a narrow string breaks on Windows and what FromUTF8 and ToUTF8 do
  - id: toctou
    text: explain how checking a file and then using it fails, and how ReadTrustedFile closes the gap
  - id: private-files
    text: choose the function that writes, checks and reads a file that only the current user may change
  - id: file-tools
    text: name what FileReader, FileLock, FileWatcher and BoundedRead are each for
since: 0.3.0
status: final
---

Every file the engine touches, from a scene on disk to a token that lets a program talk to the editor, passes through a
small set of Core classes. Their job is to make four promises:

- A file is named with the same text on every system.
- A write leaves the old contents or the new ones, never half of either.
- A file that only the current user may change is checked before it is believed.
- A reader that is told a size does not trust it.

The page does not teach what is inside a file. Checking contents that you cannot trust, saves that never stall the
editor and session files belong to other pages.

## The problem and how engines solve it

Saving looks like one action, but the disk sees several: empty the file, write the first part, write the next part. A
program can stop between any two of them. A crash, a power cut, a user who ends the process or a bug can all do it. After
the stop, the file holds the start of the new text and nothing more, and the old text is gone. A player has lost a level.

The first approach is to write in place, as the toy later on this page does. It needs no extra space and it keeps the file's
identity, but a stop at the wrong moment destroys the data. The second approach writes the new contents into a temporary
file next to the real one and then renames the temporary file over the real one. The old file stays whole until the last
step, and the last step is a single change of a name.

An **atomic write** replaces the contents of a file so that every reader, and every crash, sees all of the old contents
or all of the new ones, never a mix. Strata writes into a temporary file, also called a staged file, and then renames
it over the destination. Atomic means that the system treats the change as one step.

The step that makes this true is the **atomic rename**, which gives a file or a folder a new name in one step that no
reader and no crash can see half done. The name leads to the old object or to the new one. The usual local file systems
of Windows, Linux and macOS offer a rename that replaces its target this way. The idea works for a folder too. Strata's
build fills a folder with the extracted Slang :term[compiler]{id=compiler} under another name and renames it into place, so no build ever
sees half of it.

A third approach is a journal: write down what you intend to change, change it, then mark it done. After a crash, the
program reads the journal and finishes or undoes the work. Databases use it because they change small parts of huge
files. A journal costs a second file and a recovery step, which a game's documents do not need.

Four more problems come with the rename and with sharing a machine:

- On Windows, a rename over a file fails while another program has the file open without allowing it to be deleted, for
  example a tool that polls it. Strata's code for private files tries such a rename again for a moment; the plain write
  does not, and reports failure.
- A rename does not ask the system to copy the :term[bytes]{id=byte} to the disk. Strata flushes the program's buffer to the :term[operating system]{id=operating-system} but never asks
  for the disk. The promise therefore holds when the process dies, and not when the machine loses power.
- Time of check to time of use (**TOCTOU**) is the gap between checking a fact about a file and acting on it, in which
  another program can change the file. A regular file is an ordinary file, not a folder or a link. Check that a path names a regular file that you own, then open it: in between,
  someone replaces the file with a link to a secret one. Opening first and checking the open file closes the gap.
- On a shared machine another user can plant files in a folder they can write to. A symbolic link is a file that holds
  another path, and Windows has junctions, folders that lead to another folder. A program that follows a link or a
  junction reads or writes somewhere it did not mean to.

## The map

Callers use one class for paths and whole files, and the others for the special cases. Everything below `FileSystem`
that differs per system sits in `Strata/src/Platform/Windows/` or `Strata/src/Platform/Posix/`, which serve Linux and
macOS.

```mermaid caption="The classes of file handling: the callers, the shared classes, and the halves that differ per system." alt="A diagram. Callers use the file system class for paths and whole files, the atomic writer for large documents, the reader for ranges, the lock, the watcher and the bounded read. The platform class holds the private file functions. The reader, the lock, the watcher's notifier and the platform class each have a Windows half and a half for Linux and macOS."
flowchart LR
	callers["engine code"] --> fs["FileSystem (Core)"]
	callers --> writer["AtomicFileWriter (Core)"]
	callers --> reader["FileReader (Core)"]
	callers --> lock["FileLock (Core)"]
	callers --> watcher["FileWatcher (Core)"]
	callers --> bounded["BoundedRead (Core)"]
	callers --> platform["Platform: private files (Core)"]
	writer --> output["DocumentOutput"]
	watcher --> notifier["FileChangeNotifier"]
	platform --> bounded
	reader --> halves["Windows... / Posix..."]
	lock --> halves
	notifier --> halves
	platform --> halves
```

All of the classes are in `Strata/src/Strata/Core/`. Any thread may call `FileSystem`. A thread that serves the frame,
the :term[main thread]{id=main-thread}, calls it only for small things; large work goes to background threads, where `AtomicFileWriter` runs.
`FileWatcher` owns a thread of its own. The classes are described one by one below, after the rules that all of them
follow.

## The contract

### Text and paths

Strings in Strata are :term[UTF-8]{id=utf-8} `std::string`s everywhere: in logs, JSON, script calls and file names. UTF-8 stores text as
bytes and is the same on every system. Windows is the exception that matters. Its file calls speak UTF-16, and its
narrow calls read bytes in the process's code page, a table that maps bytes to characters and that differs per
computer. A `std::filesystem::path` made from a narrow string on Windows therefore reads those bytes in that code page.

:::example[A name that changes on the way]
The folder name `Zoë` is the three characters Z, o and ë. In UTF-8 it is the four bytes `5A 6F C3 AB`. Read in code
page 1252, the two bytes `C3 AB` are the two characters Ã and «, so the path names a folder `ZoÃ«` that does not exist. The
program finds no file, or writes into a stranger's folder. Convert through UTF-8 explicitly, and the name stays the
same.
:::

:::rule[Strings are UTF-8; convert at the boundary of `std::filesystem`]
`AGENTS.md` asks code to convert with `FileSystem::FromUTF8` and `FileSystem::ToUTF8` wherever a string meets a
`std::filesystem::path`, and never to construct a `path` from a narrow string on Windows. A path holds the platform's
characters; a string holds UTF-8; the two functions are the only bridge.
:::

`FromUTF8` copies the bytes into a `char8_t` string, the standard's type for UTF-8, and builds the path from it, so the
library converts to the platform's form with the right meaning. `ToUTF8` does the reverse and writes the generic form,
with `/` between the names on every system, so a stored path means the same on all three.

As a second line of defence, the Windows programs of Strata carry an application manifest, `CMake/Strata.manifest`, that
makes UTF-8 the process's code page and enables long paths. The editor, the :term[runtime]{id=runtime}, the command-line client and the
tests are linked with it. The log's file sink takes a narrow path (`Strata/src/Strata/Core/Log.cpp`) and relies on this
manifest: the narrow string is UTF-8 there. The rule stands; the manifest only makes a slip harmless.

### Paths and whole files: `FileSystem`

`FileSystem` reports every failure through its :term[return value]{id=return-value} and never throws. A read returns an empty `std::optional`
when the file is missing, is not a regular file or cannot be read. `ReadBytes` and `ReadText` read all of a file,
`ReadBytesPrefix` the first bytes up to a limit, and `ReadBytesRange` a range from an offset. A range that starts past
the end returns no bytes, not an error. `ReadText` removes the three-byte marker that some editors put at the start of UTF-8 text.

Writes are atomic: `WriteBytes` and `WriteText` write a temporary file next to the destination and rename it over the
destination, creating the folders first. Other calls that matter for trust: `Copy` and `CopyDirectory` never follow a
link. `CopyDirectory` skips links and special files with a logged warning, never writes through a link in the
destination, and refuses to copy a folder into itself. `IsInside` decides by the text of two paths whether one is under
the other; `IsInsideResolved` first resolves links, so a link inside a folder that points outside is outside.
`GetUniquePath` appends ` (1)`, ` (2)` and so on before the extension until the name is free. <!-- markdownlint-disable-line MD038 -->

One more feature serves tests. Each thread has a count of the file operations it made, `GetThreadOperationCount`, which
the calls above and `AtomicFileWriter` increase. A test reads the count before and after some code on the main thread
and checks that it did not change. That is how the engine proves that the asset manager's update does no file work on
the main thread.

### Writing large documents

`AtomicFileWriter` is the streaming form of the same idea, for documents too large to hold in memory: a scene of a
million entities is hundreds of MB. It implements `DocumentOutput`, the place a document writer sends its bytes
in order. The writer gathers bytes in a buffer of 1 MB, writes them into `<path>.tmp<n>`, and `Commit` renames that file
over the destination. `Abort`, or a :term[destructor]{id=destructor} that runs before `Commit`, removes the temporary file and leaves the
destination as it was. One thread uses a writer at a time, and the engine uses it on background threads.

### Reading from many threads, locking, watching, bounding

`FileReader` keeps one file open and reads byte ranges at explicit offsets: `ReadFile` with an `OVERLAPPED` structure on
Windows, `pread` elsewhere. No reader shares a file position, so many threads read at once without a lock. Other
programs may rename or delete the file while it is open, and the reader keeps reading the file it opened. Asset packs
keep one reader for their whole life.

A **file lock** is a lock the operating system attaches to an open file, so that only one process at a time holds it;
the system releases it when the holder ends, however it ends. `FileLock::Create` makes a new file already locked and
fails when the file exists; `TryAcquire` locks an existing file and fails when someone else holds the lock. Another
process tests whether the owner still lives by trying to take the lock. The build uses the same idea: :term[CMake's]{id=cmake}
`file(LOCK)` makes the fetches of Slang at the first configure take turns, and `Tools/PerfLock.py` does the same for measurements.

`FileWatcher` reports added, modified and removed files below a folder. A background thread scans the tree, compares it
with the last scan, and reports a change only after the file's size and time have been stable for the debounce time,
150 ms by default. So no consumer sees a file still being written. On Windows a `FileChangeNotifier` wakes the thread
when the system reports a change; elsewhere the thread polls every 500 ms by default. The caller collects changes with
`PollChanges` on its own thread, and no :term[callback]{id=callback} runs on the watcher's thread; the asset manager's use of the changes belongs to the page on importing.

`BoundedRead::ReadAll` reads a source to its end and keeps at most a maximum number of bytes. It takes a size hint, but
the hint only sizes the first buffer. A file that grew since someone looked at it is still read to its end, and the
result is `Complete`, `TooLarge` or `Failed`; the data of anything but `Complete` is empty.

### Files only the current user may change

The functions of `Platform` for this share one contract, written as the comment of the class. A private folder is one
that only the current user may add to, replace in or rename in. The editor's session files and the copies of script
modules the engine loads live in such folders, so an attacker who could write there could take control.

On Linux and macOS an owner-only folder has **file mode 0700**: the owner may read, write and enter it, and nobody else
may do anything. A new owner-only file has mode 0600.

On Windows the equivalent is a **DACL**, the discretionary access control list: the list of rules that says who may do
what with a file or folder. Strata's is protected, which means it inherits nothing from the parent, and has one entry
that grants the current user full access.

`EnsurePrivateDirectory` creates a folder with those rights, or checks an existing one: it must be a real folder, not a
link. The current user must own it; on Windows the Administrators or `SYSTEM` may own it too, because a program started with administrator rights creates folders that they own. On
Linux and macOS, if group or others have any right on it, the function tightens it to 0700. On Windows it never changes
an existing folder's rights.

`WritePrivateFile` writes a file through an exclusive temporary file and a rename, and only its owner can read or write
the result. `IsTrustedFile` says whether a file can be believed to come from the current user. `ReadTrustedFile` checks
and reads through one handle, the program's open connection to the file, which closes the time of check to time of use (TOCTOU) gap. `RenameNoReplace` renames and fails when the target exists.
`GetUserRuntimeDirectory` returns a per-user private folder for files that matter only while the program runs.

:::rule[Files for the current user alone use the private-file functions]
A file made with default permissions may be read or replaced by another account, so `AGENTS.md` forbids making these
files that way. Use `WritePrivateFile` to write, `ReadTrustedFile` to read, and `EnsurePrivateDirectory`,
`CreatePrivateDirectory` or `GetUserRuntimeDirectory` for the folder: all follow one contract.
:::

:::rule[Every write is atomic]
A write that stops in the middle, or is read in the middle, must never expose half a file. Write through
`FileSystem::WriteText`, `WriteBytes`, `AtomicFileWriter` or `WritePrivateFile`, never by opening the destination and
writing into it.
:::

## A toy version

The toy saves the same text twice: in place, and through a temporary file. A "kill" is a `return`, so nothing after it
runs, as nothing runs after a process dies. After each kill the program reads the file back and says what it is and how
many files the folder holds. Look at the second of the two as well as the first.

```cpp sketch="core-files-toy.cpp"
// A toy save: the same text written in place and through a temporary file, with the process "killed" after each step.
// A kill is a return: nothing after it runs, as when a process dies.
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

namespace
{
	const std::string c_Old = "OLD OLD OLD OLD";
	const std::string c_New = "NEW NEW NEW NEW NEW";

	// Three steps: open the file (which empties it), write the first half, write the rest.
	void SaveInPlace(const std::filesystem::path& path, int killAfter)
	{
		if (killAfter == 0)
			return;
		const size_t half = c_New.size() / 2;
		std::ofstream stream(path, std::ios::binary | std::ios::trunc);
		if (killAfter == 1)
			return;
		stream.write(c_New.data(), static_cast<std::streamsize>(half));
		stream.flush();
		if (killAfter == 2)
			return;
		stream.write(c_New.data() + half, static_cast<std::streamsize>(c_New.size() - half));
	}

	// Four steps: open a temporary file, write both halves into it, rename it over the file.
	void SaveAtomically(const std::filesystem::path& path, int killAfter)
	{
		if (killAfter == 0)
			return;
		const size_t half = c_New.size() / 2;
		std::filesystem::path temporary = path;
		temporary += ".tmp0";
		std::ofstream stream(temporary, std::ios::binary | std::ios::trunc);
		if (killAfter == 1)
			return;
		stream.write(c_New.data(), static_cast<std::streamsize>(half));
		stream.flush();
		if (killAfter == 2)
			return;
		stream.write(c_New.data() + half, static_cast<std::streamsize>(c_New.size() - half));
		stream.close();
		if (killAfter == 3)
			return;
		std::filesystem::rename(temporary, path);
	}

	std::string Describe(const std::filesystem::path& path)
	{
		std::ifstream stream(path, std::ios::binary);
		const std::string text((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
		if (text == c_Old)
			return "the old file";
		if (text == c_New)
			return "the new file";
		return "DAMAGED, holds \"" + text + "\"";
	}
}

int main()
{
	const std::filesystem::path directory = std::filesystem::temp_directory_path() / "strata-toy-files";
	const std::filesystem::path path = directory / "save.txt";
	for (const bool atomic : { false, true })
	{
		for (int killAfter = 0; killAfter <= (atomic ? 4 : 3); killAfter++)
		{
			std::filesystem::remove_all(directory);
			std::filesystem::create_directories(directory);
			std::ofstream(path, std::ios::binary) << c_Old;
			atomic ? SaveAtomically(path, killAfter) : SaveInPlace(path, killAfter);
			size_t entries = 0;
			for (const auto& entry : std::filesystem::directory_iterator(directory))
				entries += entry.is_regular_file() ? 1 : 0;
			std::cout << (atomic ? "atomic " : "in place ") << "killed after step " << killAfter << ": " << Describe(path) << ", " << entries << " file(s) in the folder\n";
		}
	}
	std::filesystem::remove_all(directory);
}
```

```text output-of="core-files-toy.cpp"
in place killed after step 0: the old file, 1 file(s) in the folder
in place killed after step 1: DAMAGED, holds "", 1 file(s) in the folder
in place killed after step 2: DAMAGED, holds "NEW NEW N", 1 file(s) in the folder
in place killed after step 3: the new file, 1 file(s) in the folder
atomic killed after step 0: the old file, 1 file(s) in the folder
atomic killed after step 1: the old file, 2 file(s) in the folder
atomic killed after step 2: the old file, 2 file(s) in the folder
atomic killed after step 3: the old file, 2 file(s) in the folder
atomic killed after step 4: the new file, 1 file(s) in the folder
```

1. **Lines 20–27:** in place, opening the file on line 20 already empties it; a kill after it leaves nothing, and a kill after line 24 leaves nine bytes of the new text.
2. **Lines 38–46:** the atomic save writes only into `save.txt.tmp0`, so the destination stays untouched through all of these steps.
3. **Line 49:** the rename is the only line that touches the destination, and it is one step.

:::example[One save, killed at every step]
The old file holds 15 bytes and the new text is 19. Written in place, a kill after step 1 leaves an empty file, and after
step 2 nine bytes, `NEW NEW N`. Only a kill before the first step or after the last leaves a whole file: two damaged
moments out of four. Written through a temporary file, the old file survives every kill from 0 to 3, and the new one
appears at step 4, so the file is never damaged. The cost shows in the file count: a kill at step 1, 2 or 3 leaves a
stray temporary file in the folder.
:::

Two things the toy skipped: it never flushes to the disk, and it uses one fixed temporary name. The real code uses a
counter in the name, so two writers of one file never share a temporary file.

## The real code

Data flows from a caller's string to a path, through a write, and into the private-file checks. The first quote is the
atomic write that `FileSystem::WriteBytes` and `WriteText` share.

```cpp src="Strata/src/Strata/Core/FileSystem.cpp#L102-L135"
static bool WriteFileAtomically(const std::filesystem::path& path, const void* data, size_t size)
{
	std::error_code error;
	if (path.has_parent_path())
		std::filesystem::create_directories(path.parent_path(), error);

	static std::atomic<uint32_t> s_TempCounter = 0;
	std::filesystem::path tempPath = path;
	tempPath += ".tmp" + std::to_string(s_TempCounter.fetch_add(1));

	{
		std::ofstream stream(tempPath, std::ios::binary | std::ios::trunc);
		if (!stream)
			return false;
		if (size > 0)
			stream.write(static_cast<const char*>(data), static_cast<std::streamsize>(size));
		stream.flush();
		if (!stream)
		{
			stream.close();
			std::filesystem::remove(tempPath, error);
			return false;
		}
	}

	std::filesystem::rename(tempPath, path, error);
	if (error)
	{
		std::error_code removeError;
		std::filesystem::remove(tempPath, removeError);
		return false;
	}
	return true;
}
```

1. **Lines 108–110:** a counter, shared by all threads, numbers the temporary file: two threads that write the same file never open the same temporary one.
2. **Line 113:** `std::ios::trunc` empties the temporary file, never the destination.
3. **Line 118:** `flush` hands the buffer to the operating system. It does not ask for the disk: this is the line where the promise stops at "the process dies".
4. **Lines 119–124:** a failed write removes the temporary file and reports false, so no failure leaves a stray file behind.
5. **Lines 127–133:** the rename is the step that publishes the file. If it fails, for example on Windows while a reader blocks it, the temporary file is removed and the function returns false, with the destination as it was.

The toy had no failure paths and no counter, and it returned after a crash instead of cleaning up: the real function has to handle an error at every call. Note that a crash, unlike an error, leaves its temporary file; a failed call does not.

The conversion that all paths pass through is short.

```cpp src="Strata/src/Strata/Core/FileSystem.cpp#L341-L350"
std::filesystem::path FileSystem::FromUTF8(std::string_view utf8)
{
	return std::filesystem::path(std::u8string(reinterpret_cast<const char8_t*>(utf8.data()), utf8.size()));
}

std::string FileSystem::ToUTF8(const std::filesystem::path& path)
{
	const std::u8string text = path.generic_u8string();
	return std::string(reinterpret_cast<const char*>(text.data()), text.size());
}
```

1. **Line 343:** the bytes are read as `char8_t`, which tells `std::filesystem` that they are UTF-8; the :term[constructor]{id=constructor} converts them to the platform's form.
2. **Line 348:** `generic_u8string` gives UTF-8 with `/` between the names, the same on every system.

The comment that holds the contract of private folders is the next quote. It is a security contract written as the comment of an interface: each rule says what a caller may assume.

```cpp src="Strata/src/Strata/Core/Platform.h#L92-L107"
// Private directories hold files that nobody but the current user may add, replace or rename: editor session
// files (tokens), the copies of script modules the engine loads. EnsurePrivateDirectory, CreatePrivateDirectory and
// GetUserRuntimeDirectory share one contract:
//  - A directory they create is owner-only from the start. POSIX: mode 0700. Windows: a protected DACL (nothing
//    inherited from the parent) whose single entry grants the current user full access and is inherited by what
//    is created inside.
//  - An existing directory qualifies only if it is a real directory (not a symbolic link or junction) that only
//    the current user can modify.
//      POSIX:   owned by the current user. If group or others have any permission on it, it is tightened to
//               mode 0700 (they could plant or replace files in it, or read what it holds).
//      Windows: owned by the current user, the Administrators or SYSTEM (an elevated run creates objects owned by
//               the Administrators), with no access control entry that grants anyone else modify rights; its
//               permissions are never changed. Reparse points that hold the object's own data (such as cloud
//               placeholders) are accepted.
//  - The directory containing it is not checked, and missing parents are created with default permissions:
//    callers that do not control the parent check it themselves (GetUserRuntimeDirectory does).
```

1. **Lines 92–94:** who the contract is for, and the three functions that share it.
2. **Lines 95–97:** a new folder is owner-only from the start, so there is no moment in which another user could enter it.
3. **Lines 98–101:** on Linux and macOS an existing folder must be real and owned by the user, and loose rights are tightened, not tolerated.
4. **Lines 102–105:** on Windows the Administrators and `SYSTEM` count as the user, and the rights are never changed.
5. **Lines 106–107:** the folder that holds the private folder is not checked, so a caller who does not control it checks it.

The `WritePrivateFile` of Windows differs from the plain write in one place: the final rename. A reader that holds the destination open without allowing it to be deleted makes the rename fail for a moment, so the code tries again.

```cpp src="Strata/src/Platform/Windows/WindowsPlatform.cpp#L653-L666"
DWORD moveError = ERROR_SUCCESS;
for (int attempt = 0; attempt < c_ReplaceAttempts; attempt++)
{
	if (attempt > 0)
		Sleep(c_ReplaceRetryDelayMilliseconds);
	if (MoveFileExW(temporaryPath.c_str(), path.c_str(), MOVEFILE_REPLACE_EXISTING))
		return true;
	moveError = ::GetLastError();
	if (moveError != ERROR_ACCESS_DENIED && moveError != ERROR_SHARING_VIOLATION)
		break;
}

DeleteFileW(temporaryPath.c_str());
return SetError(error, fmt::format("Failed to replace '{}': {}", FileSystem::ToUTF8(path), WindowsUtils::GetErrorMessage(moveError)));
```

1. **Lines 654–657:** up to 10 attempts, with a pause of 20 ms before each new attempt (the constants stand at the top of the file).
2. **Line 658:** `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING` is the atomic rename of Windows.
3. **Line 661:** only access denied and a sharing violation are worth another try; any other error stops at once.
4. **Line 665:** after the last failure the temporary file is deleted, so the folder holds only the old file.

The Linux and macOS half has no loop, because `rename` there does not fail when a reader has the file open. It differs elsewhere. It creates the temporary file with `O_CREAT | O_EXCL | O_NOFOLLOW` and mode 0600, so the data lands only in a file this call made, never in a planted file or a link. The Windows half uses `CREATE_NEW` and a security descriptor for the same purpose.

The last quote is the check and the read through one descriptor, the Linux and macOS name for a handle, in the form that `ReadTrustedFile` takes there.

```cpp src="Strata/src/Platform/Posix/PosixPlatform.cpp#L180-L205"
const int descriptor = open(path.c_str(), O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
if (descriptor < 0)
{
	SetError(error, fmt::format("Cannot open '{}': {}", name, GetErrorMessage(errno)));
	return std::nullopt;
}

struct DescriptorGuard
{
	int Descriptor;
	~DescriptorGuard() { close(Descriptor); }
} descriptorGuard { descriptor };

struct stat information = {};
if (fstat(descriptor, &information) != 0 || !S_ISREG(information.st_mode))
{
	SetError(error, fmt::format("'{}' is not a regular file", name));
	return std::nullopt;
}
if (requireTrusted && !CheckOwnedAndPrivate(information, name, error))
	return std::nullopt;
if (information.st_size < 0 || static_cast<uint64_t>(information.st_size) > maxSize)
{
	SetError(error, fmt::format("'{}' is larger than {} bytes", name, maxSize));
	return std::nullopt;
}
```

1. **Line 180:** `O_NOFOLLOW` refuses a final symbolic link, and `O_NONBLOCK` keeps the open of a named pipe, a file that another program writes into as it runs, from waiting for a writer.
2. **Lines 193–194:** `fstat` asks about the open file, not the path, so the answer is about the file the descriptor holds; anything but a regular file is refused.
3. **Lines 199–200:** the trust check, owner and permissions, runs on the same descriptor.
4. **Lines 201–205:** the size is checked against the maximum before the read. The read itself goes through `BoundedRead`, which refuses a file that grew after this check.

Between the check and the read the path can change as often as it likes: the descriptor still names the file that was
checked. The Windows half does the same with one handle opened with delete sharing, so a writer can still replace the
file atomically while it is read.

## Alternatives Strata did not choose

| Technique | Who uses it | What Strata would gain | What Strata would lose |
| --- | --- | --- | --- |
| Write in place | Log files and simple tools | No extra space and no rename | A stop in the middle destroys the file |
| Ask the system to flush to the disk before the rename | Databases | The new file survives a power cut | Every save waits for the disk |
| A journal or write-ahead log | Databases | Small changes to a huge file without rewriting it | A second file and a recovery step at start |
| UTF-16 `std::wstring` paths everywhere | Programs written only for Windows | No conversion on Windows | Every log, JSON and script string must convert, and Linux and macOS need another type |
| The system's change notifications alone | Tools that need instant answers on one system | No scan of the tree | More code per system, and lost events when the system's queue fills |

Strata keeps the cheapest design that survives a dying process, which is what a crash in a game or an editor is. It
pays for a flush to the disk only where the loss would hurt more than the wait; the code reviewed above shows no such
place, and the page does not promise one.

## How it is tested

Each class has a suite named after it. Run one with the test program, for example
`build/windows/bin/Debug/StrataTests.exe --test-suite=Core.FileSystem`.

- `Core.FileSystem`: round trips of text and binary files, the leading marker of UTF-8 text, UTF-8 names in Chinese and
  Russian, trailing slashes, containment and the per-thread operation count. A copy of a folder never follows or
  writes through a link.
- `Core.AtomicFileWriter`: a commit replaces the file through and past the buffer. A writer that was stopped, or dropped,
  leaves the file as it was and removes its temporary file. A writer that cannot create its file names the file and the
  system's reason.
- `Core.BoundedRead`: a source is read to its end whatever the hint said, a source larger than the limit is refused,
  and read failures are reported.
- `Core.FileReader` and `Core.FileWatcher`: ranges, many threads at once, and the events of the watcher, including that
  a file created and deleted before it is observed produces no event.
- `Core.Platform`: file locks are exclusive and end with their process; private files are replaced atomically and
  checked; links and folders that others can write are refused; `RenameNoReplace` never replaces.

## Changing it safely

New file code starts from the table of the contract: what string is this, who may change the file, and what if the
process dies now? The questions and the rules they come from:

- Add no new way to open a destination for writing. Use the existing writers, or add a function beside them with its
  test; a plain stream into the destination breaks the atomic rule.
- Add a platform half under `Strata/src/Platform/Windows/` or `Strata/src/Platform/Posix/` and keep `Platform.h` the one contract; never include
  `<Windows.h>` in a :term[header]{id=header}.
- Keep every function free of exceptions and report failure by return value; a failed write leaves the destination as it
  was and removes its temporary file.
- Count an operation with `FileSystem::CountThreadOperation` in any new file code that does not go through
  `FileSystem`, so that the tests that watch the main thread see it.
- Run `Core.*` and, after a change to the private-file code, the suites on the operating systems you did not change.
  The Windows half and the half for Linux and macOS are separate code, and each has tests of its own.

## What went wrong before

Before the commit `dd367dab`, `ReadRegularFile` read the size it had seen plus one byte. A file that grew between the size
check and the read came back as a torn prefix, cut at a stale size. Files such as `/proc/<id>/stat` report a size of 0
but have contents. The commit made the function read to the end, bounded by the maximum plus one byte, through
`BoundedRead`. Its regression test is the first test case of `Core.BoundedRead`, which tries sizes 0, 1, 10, the true size
and 1000 with chunks of 1, 7 and 64 bytes.

The same commit made `ReadTrustedFile` check on the handle it reads through, so the trust check and the read have no gap.

## Summary

- A write through a temporary file and a rename leaves the old file or the new one when the process dies, because the rename is one step. A failed write removes its temporary file, while a crash leaves it.
- Paths go through `FromUTF8` and `ToUTF8` because a narrow string on Windows is read in the code page; the manifest makes UTF-8 that code page as a second line of defence.
- A check and a use are two moments. `ReadTrustedFile` and `ReadRegularFile` open once and check and read through the same handle, so a swap in between changes nothing.
- A file that only the current user may change is written with `WritePrivateFile`, checked with `IsTrustedFile` or `ReadTrustedFile`, and kept in a folder from `EnsurePrivateDirectory`.
- `FileReader` reads ranges from many threads, `FileLock` makes processes take turns, `FileWatcher` reports settled changes on the caller's thread, and `BoundedRead` reads to the end with a cap whatever the hint says.

## Check yourself

1. A program writes a 100 MB document with `AtomicFileWriter` and is killed by the operating system after 60 MB went into the temporary file. What does the folder hold afterwards?

   :::answer{tests="atomic-write"}
   The destination holds the old document, whole, because nothing renamed. The temporary file `<path>.tmp<n>` stays with
   its 60 MB (or the part the system had received): a kill runs no destructor, so nothing removes it. A later write picks
   another name. The temporary file holds part of the new document, but no reader opens it: readers open the destination.
   :::

2. On Windows a program without the manifest, whose code page is 1252, converts the UTF-8 name `Zoë` by building a `std::filesystem::path` straight from the bytes. Which of these is right? (a) The path names `Zoë`. (b) The path names `ZoÃ«`. (c) The call fails with an error.

   :::answer{tests="utf8-paths"}
   (b). The four bytes `5A 6F C3 AB` are read as four characters of the code page, and `C3` and `AB` are Ã and «. (a) holds only
   where the code page is UTF-8, which the manifest arranges for Strata's programs. (c) is wrong: the call succeeds and
   names a different path, which is the danger. `FromUTF8` avoids it.
   :::

3. Code calls `Platform::IsTrustedFile(path)`, then `FileSystem::ReadText(path)`. What can an attacker who can write in the folder do, and what is the fix?

   :::answer{tests="toctou"}
   Between the two calls the attacker replaces the trusted file with their own or with a link; `ReadText` then reads
   what the attacker chose. That is a TOCTOU failure. The fix is one call, `Platform::ReadTrustedFile(path, maxSize)`,
   which opens the file once and checks the owner and the permissions on that same handle before reading it.
   :::

4. Which function writes the token file that only the editor's user may read, and which reads it back? (a) `FileSystem::WriteText` and `FileSystem::ReadText`. (b) `Platform::WritePrivateFile` and `Platform::ReadTrustedFile`. (c) `AtomicFileWriter` and `FileReader`.

   :::answer{tests="private-files"}
   (b). `WritePrivateFile` creates the file for its owner alone and renames it into place; `ReadTrustedFile` refuses a
   file another account could have changed. (a) is atomic but creates the file with the folder's default rights, which
   other accounts may read or replace. (c) is atomic and bounded but checks nothing about the owner.
   :::

5. Match each need to a class. (1) Eight threads read an asset pack. (2) A second editor must not use a folder that a running one owns. (3) The asset folder is watched for new files. (4) A file of unknown size is read with a cap.

   :::answer{tests="file-tools"}
   (1) `FileReader`: one open file, reads at offsets, no shared position. (2) `FileLock`: the owner holds a lock that
   the system drops when the process ends, and the other editor fails to take it. (3) `FileWatcher`, which reports the
   settled changes on the caller's thread. (4) `BoundedRead`, which reads to the end whatever size was reported and
   refuses what is larger than the cap.
   :::

## Exercises

1. **Basic.** Write `ReadAll` as a program of your own: it reads from an `std::istream` with a size hint and a maximum, never trusts the hint, and refuses a source above the maximum. Run it with a source of 10 bytes, hints 0, 3 and 500, and maximums 10 and 9. Predict the table first.

   :::answer[Worked solution]{tests="file-tools" solution="sketches/core-files-bounded.cpp"}
   The hint sizes the first buffer, one byte above the smaller of the hint and the maximum. The buffer doubles up to
   the maximum plus one byte; holding one byte past the maximum is the proof that the source is too large. A maximum
   of 10 keeps all 10 bytes whatever the hint. A maximum of 9 refuses them whatever the hint.

   ```cpp sketch="core-files-bounded.cpp"
   // Reads a source to its end with a cap, trusting a size hint for nothing but the first buffer.
   #include <algorithm>
   #include <cstdio>
   #include <sstream>
   #include <string>

   enum class Status
   {
   	Complete,
   	TooLarge
   };

   Status ReadAll(std::istream& source, size_t sizeHint, size_t maxSize, std::string& contents)
   {
   	contents.clear();
   	std::string buffer(std::min(sizeHint, maxSize) + 1, '\0');
   	size_t total = 0;
   	while (true)
   	{
   		if (total == buffer.size())
   			buffer.resize(std::min(buffer.size() * 2, maxSize + 1));
   		if (total == buffer.size())
   			break; // one byte past the cap is held: the source is too large
   		source.read(buffer.data() + total, static_cast<std::streamsize>(buffer.size() - total));
   		const size_t count = static_cast<size_t>(source.gcount());
   		if (count == 0)
   			break;
   		total += count;
   	}
   	if (total > maxSize)
   		return Status::TooLarge;
   	contents.assign(buffer, 0, total);
   	return Status::Complete;
   }

   int main()
   {
   	const std::string data = "0123456789"; // ten bytes
   	for (const size_t hint : { size_t(0), size_t(3), size_t(500) })
   	{
   		for (const size_t cap : { size_t(10), size_t(9) })
   		{
   			std::istringstream source(data);
   			std::string contents;
   			const Status status = ReadAll(source, hint, cap, contents);
   			std::printf("hint %3zu, cap %2zu: %s, %zu bytes kept\n", hint, cap, status == Status::Complete ? "complete" : "too large", contents.size());
   		}
   	}
   }
   ```

   ```text output-of="core-files-bounded.cpp"
   hint   0, cap 10: complete, 10 bytes kept
   hint   0, cap  9: too large, 0 bytes kept
   hint   3, cap 10: complete, 10 bytes kept
   hint   3, cap  9: too large, 0 bytes kept
   hint 500, cap 10: complete, 10 bytes kept
   hint 500, cap  9: too large, 0 bytes kept
   ```

   1. **Line 16:** the hint sizes the first buffer, but never above the maximum plus one byte.
   2. **Lines 20–23:** a full buffer doubles up to the maximum plus one byte; once it holds that one byte more, the source is too large.
   3. **Lines 24–28:** the loop reads until the source returns nothing, so a wrong hint changes only how often the buffer grows.
   4. **Lines 30–31:** more bytes than the maximum means `TooLarge`, and nothing is kept.
   :::

2. **Medium.** Kill a writing process in a loop. Write a program that starts a child, lets it write a file of 4 MB over and over, ends the child after a random time, and checks that the file is whole. Do it once for a write in place and once for a write through a temporary file and a rename.

   :::answer[Worked solution]{tests="atomic-write"}
   The child fills the file with one byte value that changes in each version. A whole file has the full length and one
   value only. The script below does both modes; run it with `python -I killloop.py run`.

   ```python
   import os
   import random
   import subprocess
   import sys
   import time

   PATH = "payload.bin"
   SIZE = 4_000_000


   def writer(mode):
       version = 0
       while True:
           version = version % 250 + 1
           data = bytes([version]) * SIZE
           if mode == "inplace":
               with open(PATH, "wb") as stream:
                   stream.write(data)
           else:
               with open(PATH + ".tmp", "wb") as stream:
                   stream.write(data)
               os.replace(PATH + ".tmp", PATH)


   def read_bytes(name):
       with open(name, "rb") as stream:
           return stream.read()


   def patiently(action, name):
       for attempt in range(100):
           try:
               return action(name)
           except PermissionError:
               if attempt == 99:
                   raise
               time.sleep(0.05)


   def damaged_after_kills(mode, rounds):
       damaged = 0
       for _ in range(rounds):
           for name in (PATH, PATH + ".tmp"):
               if os.path.exists(name):
                   patiently(os.remove, name)
           process = subprocess.Popen([sys.executable, "-I", __file__, "writer", mode])
           time.sleep(random.uniform(0.05, 0.3))
           process.kill()
           process.wait()
           if os.path.exists(PATH):
               data = patiently(read_bytes, PATH)
               if len(data) != SIZE or data.count(data[:1]) != SIZE:
                   damaged += 1
       return damaged


   if sys.argv[1] == "writer":
       writer(sys.argv[2])
   else:
       for mode in ("inplace", "atomic"):
           print(mode, "damaged:", damaged_after_kills(mode, 40), "of 40")
   ```

   1. **Lines 11–22:** the child. In place, `open(PATH, "wb")` empties the file first; atomically, the data goes to `payload.bin.tmp`, and `os.replace` renames it over the file in one step.
   2. **Lines 25–37:** `read_bytes` reads a whole file. `patiently` tries again for up to 5 s while Windows answers `PermissionError`: another program, such as a virus scanner, can hold a file for a moment after the child that wrote it has ended. Without it, a run on Windows can stop at a removal before it prints anything.
   3. **Lines 42–49:** each round starts clean and starts the child with the interpreter, `-I` and this file as the script. After a random pause of 50 to 300 ms, `kill` ends the child without letting it clean up, as a crash does.
   4. **Lines 50–53:** the check. The file must have 4,000,000 bytes, all equal; a shorter file or a mix of two values is damaged.
   5. **Lines 57–61:** the same file runs as the child or as the parent, and the parent prints the counts of both modes.

   In six runs on Windows the in-place mode left 5 to 12 damaged files of 40 and the atomic mode none. The in-place count varies
   with the timing, because a kill damages the file only while a write is under way; the atomic count is always 0,
   and a stray `payload.bin.tmp` is the only trace.
   :::

3. **Hard.** Trace it yourself. Start at `FileSystem::WriteText` and follow it, with the debugger or a search, to its temporary file, its flush and the `std::filesystem::rename` that replaces the old file. Then do the same for `Platform::WritePrivateFile` on your operating system, to its own rename. Write down, for each step, what a crash right after it leaves.

   :::answer[Worked solution]{tests="atomic-write private-files"}
   `WriteText` in `Strata/src/Strata/Core/FileSystem.cpp` calls `CountThreadOperation` and then the static function
   `WriteFileAtomically`. Its steps: create the parent folders; number a temporary name `<path>.tmp<n>`; open it and
   empty it; write; `flush`; close at the end of the block; `std::filesystem::rename`. A crash before the rename leaves
   the old file and a temporary file; a crash after leaves the new file.

   `WritePrivateFile` is in `Strata/src/Platform/Windows/WindowsPlatform.cpp` (`CreateFileW` with `CREATE_NEW` and an
   owner-only security descriptor, `WriteFile`, `CloseHandle`, then up to 10 `MoveFileExW` attempts with
   `MOVEFILE_REPLACE_EXISTING`) and in `Strata/src/Platform/Posix/PosixPlatform.cpp` (`open` with `O_EXCL`, `write`,
   `close`, `rename`). A crash before the rename leaves the old file and a temporary file named `.tmp-` and 16 :term[hexadecimal]{id=hexadecimal}
   digits; after it, the new file.
   :::

## Where it lives in Strata

- `Strata/src/Strata/Core/FileSystem.h` and `FileSystem.cpp`: paths, reads, atomic writes, copies, containment, the operation count.
- `Strata/src/Strata/Core/AtomicFileWriter.h`, `AtomicFileWriter.cpp` and `DocumentOutput.h`: the streaming writer.
- `Strata/src/Strata/Core/FileReader.h`, `FileLock.h`, `FileWatcher.h`, `FileChangeNotifier.h` and `BoundedRead.h`, with the halves in `Strata/src/Platform/Windows/` and `Strata/src/Platform/Posix/`.
- `Strata/src/Strata/Core/Platform.h`: the private-file contract and its functions; `WindowsFileSecurity.cpp`: the Windows owner and access rules.
- `CMake/Strata.manifest`: UTF-8 and long paths for the Windows programs.
- `StrataTests/src/Core/`: `FileSystemTests.cpp`, `AtomicFileWriterTests.cpp`, `BoundedReadTests.cpp`, `FileReaderTests.cpp`, `FileWatcherTests.cpp`, `PlatformTests.cpp` and `PlatformSecurityTests.cpp`.
- `CMake/StrataSlang.cmake` and `Tools/PerfLock.py`: the build's file locks.

## Further reading

- SQLite's documentation, "Atomic Commit In SQLite": how a database commits with a journal and flushes to the disk. Advanced.
- Dan Luu, "Files are hard": what file systems promise after a crash, and where programs assume more. Intermediate.
- [Microsoft's documentation of `MoveFileEx`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw): the Windows rename and its replace flag. Intermediate.
- [The page of `std::filesystem::rename` in an online manual of C++](https://en.cppreference.com/w/cpp/filesystem/rename): what the standard promises when the target exists. Beginner.
- The manual page of `rename(2)` on Linux: the POSIX guarantee that a replacing rename is atomic. Intermediate.
