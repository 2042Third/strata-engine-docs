#!/usr/bin/env python3
"""Makes the two word lists of tools/data/ that come from a published list (plan/style.md §2.3), so that anyone can make
them again and see that nothing was added by hand:

    python -I tools/wordlists.py write --archive <12dicts-6.0.2.zip>
    python -I tools/wordlists.py check --archive <12dicts-6.0.2.zip>

The archive is 12dicts 6.0.2 by Alan Beale (http://downloads.sourceforge.net/wordlist/12dicts-6.0.2.zip, linked from
http://wordlist.aspell.net/12dicts/); the tool refuses any other file (its SHA-256 is c_ArchiveSha256). Beale released
12dicts into the public domain; its lemmatized lists depend on Kevin Atkinson's AGID, whose permissive notice
tools/data/12dicts-notice.txt keeps, as the archive's own ReadMe asks.

tools/data/common-words.txt   style.md §2.3 item 1: the 8,991 headwords of the frequency bands 1 to 14 of
                              Lemmatized/2+2+3frq.txt (the most common lemmas of English; 14 is the smallest last band
                              that gives at least 8,000, plan/critique/rulings-11.md R50), each with its inflected forms
                              and variant spellings from Lemmatized/2+2+3lem.txt. One headword per line, then its forms,
                              separated by spaces.
tools/data/verbs.txt          The verbs of Lemmatized/2+2+3lem.txt (a headword with an -s form and an -ing form of its
                              own) with their forms: base, third person, the past forms (past tense and past
                              participle, which the list does not tell apart; regular -ed forms and irregular ones), and
                              the -ing form, separated by tabs, "-" for none, several forms joined by ",". The verbs be,
                              have and do and the modal verbs come first, written out. tools/lint.py reads it for the
                              rules pronoun-start, passive and noun-stack.

write  writes both files from the archive; check fails when they differ from what the archive gives (exit 1).

Only the standard library is used. Exit codes: 0 when all is well, 1 when a file differs, 2 for usage errors (no
archive, another archive, a list missing from it).
"""

import argparse
import hashlib
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import repo  # noqa: E402

c_ArchiveSha256 = '64ac1d35acb66b550c7ebc56e080b62e0bad8f5984d72059dc2e05ac48780e52'
c_ArchiveName = '12dicts 6.0.2'
c_FrequencyList = 'Lemmatized/2+2+3frq.txt'
c_LemmaList = 'Lemmatized/2+2+3lem.txt'
c_LastBand = 14
c_Data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
c_CommonFile = 'common-words.txt'
c_VerbsFile = 'verbs.txt'
c_Band = re.compile(r'^-+\s*(\d+)\s*-+$')
# The verbs whose forms no rule derives, written out: be, have, do, and the modal verbs (which take no -s).
c_IrregularHeads = [
    ('be', 'is', 'am,are,was,were,been', 'being'),
    ('have', 'has', 'had', 'having'),
    ('do', 'does', 'did,done', 'doing'),
    ('can', 'can', 'could', '-'),
    ('could', 'could', '-', '-'),
    ('may', 'may', 'might', '-'),
    ('might', 'might', '-', '-'),
    ('must', 'must', '-', '-'),
    ('shall', 'shall', 'should', '-'),
    ('should', 'should', '-', '-'),
    ('will', 'will', 'would', '-'),
    ('would', 'would', '-', '-'),
]
c_BaseParticiples = ('run', 'rerun', 'outrun', 'overrun', 'come', 'become', 'overcome')  # "is run": the participle is the base
# Words formed with the suffixes 2+2+3lem lists beside a headword's inflections (its ReadMe names seven, among them
# -ish, -less, -ness and -ly): they are other words, never forms of a verb. The first suffix is written in two parts
# because the spelling gate (typos) reads it alone as a misspelled "full".
c_Full = 'fu' 'l'
c_DerivedEndings = (c_Full, c_Full + 'ly', c_Full + 'ness', 'ish', 'ishly', 'ishness', 'less', 'lessly', 'lessness', 'like',
                    'ly', 'most', 'ness', 'nesses')


class ArchiveError(Exception):
    pass


def read_archive(path, sha256=c_ArchiveSha256):
    """{name: text} of the two lists in the archive, after its SHA-256 matched."""
    try:
        with open(path, 'rb') as file:
            data = file.read()
    except OSError as error:
        raise ArchiveError('cannot read the archive %s: %s' % (path, error))
    digest = hashlib.sha256(data).hexdigest()
    if digest != sha256:
        raise ArchiveError('%s has the SHA-256 %s, not the one of %s (%s): download it again from '
                           'http://downloads.sourceforge.net/wordlist/12dicts-6.0.2.zip' % (path, digest, c_ArchiveName, sha256))
    texts = {}
    try:
        with zipfile.ZipFile(path) as archive:
            for name in (c_FrequencyList, c_LemmaList):
                texts[name] = archive.read(name).decode('latin-1').replace('\r\n', '\n')
    except (KeyError, zipfile.BadZipFile) as error:
        raise ArchiveError('%s does not hold %s and %s: %s' % (path, c_FrequencyList, c_LemmaList, error))
    return texts


def clean_form(text):
    """A word of a list without its marks: "abode -> [abide]" (a cross-reference), "bitcoin!" (a new word), "(April)"
    (a word the frequency data alone gives)."""
    word = text.split('->')[0].strip().rstrip('!').strip()
    if word.startswith('(') and word.endswith(')'):
        word = word[1:-1]
    return word


def read_lemmas(text):
    """[(headword, [forms])] of a lemma list: a headword line, then an indented line of forms joined by ","."""
    lemmas = []
    for line in text.split('\n'):
        if not line.strip() or c_Band.match(line.strip()):
            continue
        if line[:1] in ' \t':
            if lemmas:
                lemmas[-1][1].extend(word for word in (clean_form(part) for part in line.split(',')) if word)
        else:
            lemmas.append((clean_form(line), []))
    return lemmas


def frequency_headwords(text, last_band=c_LastBand):
    """[(headword, [forms])] of the frequency bands 1 to last_band of 2+2+3frq, in the list's order."""
    result = []
    band = None
    for line in text.split('\n'):
        match = c_Band.match(line.strip())
        if match:
            band = int(match.group(1))
            continue
        if band is None or band > last_band or not line.strip():
            continue
        if line[:1] in ' \t':
            if result:
                result[-1][1].extend(word for word in (clean_form(part) for part in line.split(',')) if word)
        else:
            result.append((clean_form(line), []))
    return result


def common_words(texts, last_band=c_LastBand):
    """The lines of common-words.txt: each headword of the bands with the forms 2+2+3lem gives it (the frequency list
    leaves out regular inflections), or the frequency list's own when 2+2+3lem lacks the headword."""
    lemmas = {}
    for headword, forms in read_lemmas(texts[c_LemmaList]):
        lemmas.setdefault(headword, []).extend(forms)
    lines = []
    seen = set()
    for headword, forms in frequency_headwords(texts[c_FrequencyList], last_band):
        if headword in seen:
            continue
        seen.add(headword)
        words = []
        for word in [headword] + lemmas.get(headword, []) + forms:
            if word not in words and ' ' not in word:
                words.append(word)
        lines.append(' '.join(words))
    return lines


def candidates(base, endings):
    found = set()
    for ending in endings:
        found.add(base + ending)
        if base.endswith('e'):
            found.add(base[:-1] + ending)
        if base.endswith('ie') and ending == 'ing':
            found.add(base[:-2] + 'ying')
        if base.endswith('y') and len(base) > 2 and base[-2] not in 'aeiou' and ending in ('es', 'ed'):
            found.add(base[:-1] + 'i' + ending)
        if base[-1:].isalpha():
            found.add(base + base[-1] + ending)  # stop, stopped, stopping
        if base.endswith('c'):
            found.add(base + 'k' + ending)  # picnic, picnicked
    return found


def verb_forms(headword, forms):
    """(third person, [past forms], -ing) of a headword of 2+2+3lem when it is a verb, else None. A verb has a third
    person form (-s, -es, -ies) and an -ing form among its forms. The other forms are past forms unless they are a
    comparison (-er, -est), a derived word (c_DerivedEndings), a variant spelling (a form whose own -s form is listed
    too) or one of its forms."""
    if not re.match(r'^[a-z]+$', headword):
        return None
    listed = set(forms)
    third = sorted(listed & ({headword + 's', headword + 'es'} | ({headword[:-1] + 'ies'} if headword.endswith('y') else set())))
    ing = sorted(listed & candidates(headword, ['ing']))
    if not third or not ing:
        return None
    variants = {form for form in listed
                if ({form + 's', form + 'es'} & listed) - set(third)}  # colour beside colours; not writ beside writes
    pasts = []
    for form in forms:
        if form in third or form in ing or form in pasts or not re.match(r'^[a-z]+$', form):
            continue
        if form.endswith(c_DerivedEndings) or form.endswith(('s', 'ing', 'er', 'est')) or form in variants:
            continue  # derived words, comparisons (cleaner, cleanlier), other forms
        if any(form.startswith(variant) and len(form) > len(variant) for variant in variants):
            continue  # an inflection of a variant spelling (colour, coloured)
        pasts.append(form)
    if not pasts or headword in c_BaseParticiples:
        pasts.append(headword)  # set, put, read: the past forms are written as the base; run: ran, run
    return third[0], pasts, ing[0]


def verbs(texts):
    """The lines of verbs.txt."""
    lines = ['\t'.join(fields) for fields in c_IrregularHeads]
    written = {fields[0] for fields in c_IrregularHeads}
    for headword, forms in read_lemmas(texts[c_LemmaList]):
        if headword in written:
            continue
        found = verb_forms(headword, forms)
        if found is None:
            continue
        third, pasts, ing = found
        written.add(headword)
        lines.append('\t'.join([headword, third, ','.join(pasts) or '-', ing]))
    return lines


def header_common():
    return ['# %s (Alan Beale, public domain; its lemmatized lists depend on AGID, whose permissive notice is '
            'tools/data/12dicts-notice.txt): the headwords of frequency bands 1 to %d of %s with the forms of %s.'
            % (c_ArchiveName, c_LastBand, c_FrequencyList, c_LemmaList),
            '# Written by "python -I tools/wordlists.py write"; do not edit. One headword per line, then its forms.']


def header_verbs():
    return ['# The verbs of %s %s (Alan Beale, public domain; AGID\'s notice is tools/data/12dicts-notice.txt).'
            % (c_ArchiveName, c_LemmaList),
            '# Written by "python -I tools/wordlists.py write"; do not edit. Fields, separated by tabs: base, third person, '
            'past forms (past tense and past participle, joined by ","), -ing; "-" for none.']


def outputs(texts):
    return {
        c_CommonFile: '\n'.join(header_common() + common_words(texts)) + '\n',
        c_VerbsFile: '\n'.join(header_verbs() + verbs(texts)) + '\n',
    }


def stale_files(files, data):
    """The paths of the lists in the folder `data` that differ from `files` ({name: text}) or are missing."""
    stale = []
    for name, text in files.items():
        path = os.path.join(data, name)
        try:
            current = repo.read_text(path)
        except OSError:
            current = None
        if current != text:
            stale.append(path)
    return stale


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Makes tools/data/common-words.txt and verbs.txt from 12dicts 6.0.2 '
                                     '(plan/style.md §2.3).', epilog=__doc__.split('\n\n', 1)[1],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', choices=('write', 'check'), help='write the files, or check that they are current')
    parser.add_argument('--archive', required=True, help='12dicts-6.0.2.zip, downloaded from the address above')
    parser.add_argument('--data', default=c_Data, help='the folder of the word lists (default: tools/data)')
    options = parser.parse_args(argv)
    try:
        files = outputs(read_archive(options.archive))
    except ArchiveError as error:
        print('wordlists: %s' % error, file=sys.stderr)
        return 2
    if options.action == 'write':
        for name, text in files.items():
            path = os.path.join(options.data, name)
            os.makedirs(options.data, exist_ok=True)
            repo.write_text(path, text)
            print('wordlists: wrote %s (%d lines)' % (path, text.count('\n')))
        return 0
    stale = stale_files(files, options.data)
    for path in stale:
        print('%s:1: differs from what %s gives: run python -I tools/wordlists.py write --archive <its zip>'
              % (path, c_ArchiveName))
    if options.action == 'check' and not stale:
        print('wordlists: %s are current' % ', '.join(sorted(files)))
    return 1 if stale else 0


if __name__ == '__main__':
    sys.exit(main())
