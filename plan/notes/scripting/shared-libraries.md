# Notes: scripting/shared-libraries

## New terms

None proposed.

## Requests

- None. The page names no external host links (Further reading cites sources without links).

## Since

- since 0.6.0: the script ABI at version 1 and 0.6.0 modules loading on 0.7.0 (Docs/Releases/0.7.0.md); the pagecheck accepted it.

## Not verified

- Name mangling examples (`_ZN7Spinner8OnUpdateEf`, `?OnUpdate@Spinner@@QEAAXM@Z`) and the Windows classic DLL search order come from general knowledge, not the pin.
- The 56-byte struct of the versioning example is an invented later version of `StrataScriptModuleAPI`; the 48-byte size is computed from the header on a 64-bit machine, not measured.
- Claims about COM, Vulkan, Python, protocol buffers and Linux `ld.so` behavior are general knowledge.
- Whether a load from a private copy is used for hot reload in every case: only the loader's comment and error text were read.

## Findings not applied

- The brief lists no open findings.
- Left out by design: macOS `@loader_path`, and the Win32 `cbSize` details beyond the pattern.

## Clerk

- Nothing asked.
