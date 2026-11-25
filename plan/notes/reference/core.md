# Notes: reference/core

## New terms

None proposed. The page defines in bold: precompiled header, sticky failure (no glossary home claimed).

## Requests

None.

## Hand-written tables

All tables of the page: no generated file for Core exists in src/generated/reference/. Read from, at the pin,
Strata/src/Strata/Core/: UUID.h, Hash.h, Crypto.h, Base64.h, BinaryStream.h, JsonUtils.h, JsonEvents.h, StringUtils.h,
RadixSort.h, RangeAllocator.h, AmortizedCheck.h, Prefetch.h, ParallelClone.h, CommandLine.h, CommandLineOptions.h,
EmbeddedFiles.h, Version.h.in, Base.h; and Strata/src/stpch.h.

## Not verified

- The teaching pages named under each table were chosen from the brief; their content was not re-read.
- That StrataTests/src/Core holds tests for every helper (found tests for Base64, BinaryStream, Crypto, JsonUtils, RadixSort, RangeAllocator, StringUtils).
- The lint size (2,477 words against M) counts tables; reference pages are not size-checked.

## Findings not applied

- critic-reference-2: names the teaching page under each table (applied for this page).
- critic-reference-16: the other 30 Core headers and Math headers are not covered; the brief's Covers lists about 15 headers and the finding is "could".

## Clerk

- Refused: the bold words the page defines locally (precompiled header, homed on engineering/flags-portability; sticky failure) are not admitted: a reference page restates terms whose homes are their chapters, and the page proposed none.
