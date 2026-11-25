# Part review of `engineering/ci`

- unclear: "For each of the first five it prints" read as five kinds of error line, of which the paragraph names four; now "the first five errors it finds" (`c_MaxLocatedErrors = 5`).
- gap: `CIStatus.py status` exits 3 also when no run has started, and its 0 means completed, not green (`Tools/CIStatus.py:11-12`, `:72-86`); the sentence says both now, split in two for `sentence-max`.
