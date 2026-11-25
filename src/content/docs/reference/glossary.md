---
id: reference/glossary
title: "Glossary"
description: "Every term the book defines, with its one-sentence definition, its other names and the page where it is explained."
kind: reference
size: XL
tracks: []
needs: []
status: final
tableOfContents: false
---

This page is the list of every term the book defines, sorted by letter. You can read it from the top, or search it with the browser's find command when you meet a word you do not know. An entry gives the term in bold and its definition in one sentence. After "Read" comes the page that teaches it, and after "Also called" the other names the book accepts for it. That page is the term's home: follow its link to learn the idea in full, with examples.

A game maker may use a term in a different place than the page that teaches it. Then the entry also names that second page, the term's use home, after "Used in". A term from the book's first parts, such as a word of computers or arithmetic, links to the page of `start` or `basics` that teaches it from the beginning.

On the other pages, the first use of a term in a page links to its entry here. The small button beside that link shows the definition without leaving the page; following the link itself lands your browser on the entry here.

::glossary

## Entries with a bracketed word

A word that means two different things has two entries, each followed by a word in brackets, for example "Batch (assets)" and "Batch (draw)", two of the senses of "batch". The bracketed word tells the senses apart: it is never part of the name you meet in the editor or the code. Other entries carry a short name or a detail in brackets, as "Attachment (socket)" does; those entries have one sense only. A page that uses such a word links the entry of the sense it means, so a link never leads to a definition of the other sense.

An entry never holds two definitions. When one idea has two parts that a reader could confuse, the book gives each part its own entry. Look at the bracketed word first when two entries share a word.

## Where it lives in Strata

- `src/content/glossary.json`: the book's file of terms, the source of every entry above.
- Each entry for an engine term links its home page. The section "Where it lives in Strata" of that page names the engine files, commands and tests that build the thing.
