#!/usr/bin/env python3
"""The book's language lint: every rule of plan/style.md that a program can measure, under the rule ids style.md gives
(§2.1 and §2.2, §3, §4, §6.1, §8, §9.1, §10, §12 and §13), the site's two rules (plan/site.md, "The base path",
rules 3 and 4), and literal-origin (plan/critique/rulings-6.md, R24: the origin of site.json is written in no other
file but deploy/README.md, README.md and plan/; without a site.json lint notes that the rule did not run).

    python -I tools/lint.py [pages...] --engine <pin clone> [--root <book>] [--plan <folder>] [--glossary <file>]
                            [--report <folder>]

pages      page ids (core/time); default: every page under src/content/docs/.
--engine   the pin clone (plan/pipelines.md §1.2; default: the STRATA_ENGINE variable). The rule copied-text reads
           AGENTS.md, Docs/DeveloperGuide.md and Docs/Manual/*.md at engine.pin's commit through one git process; the
           tool stops with exit code 2 when the clone does not have that commit (pipelines.md §1.4, check 1).
--plan     the plan folder (default: <root>/plan): the outline (plan/outline-*.md and tracks.md, read by
           tools/booklib/outline.py) gives each page's row, Needs closure, level and W8r mark; plan/inventory/*.md
           are the other sources of copied-text.
--glossary the glossary (default: src/content/glossary.json).
--report   writes one reading report per page into the folder (style.md §2.2): words, sentences, their mean and the
           longest, the paragraphs over the limit, the new terms per section, the words outside the lists, and the
           warnings. The provenance reviewer reads it with the page.

Every finding is "<file>:<line>: <rule>: <message>": the page (or its figure manifest), the line, the rule id and
what to do. Rules marked (warning) are reported for the writer and the reviewers to decide and do not fail; every
other rule fails, and none is waived on the page: style.md allows only its warnings and the exemptions each rule
states. With page ids named, it also prints for each page "<file>: words: <n> prose words; size <S|M|L|XL> holds <a>
to <b>", the count the size rule measures. The word lists are tools/data/ (common-words.txt and verbs.txt come from 12dicts through tools/wordlists.py;
extra-words.txt, names.txt, acronyms.json, phrasal-verbs.json, idioms.txt, function-words.txt and cpp-features.json are
the book's).

Only the standard library is used. Exit codes: 0 when no rule fails (warnings may be printed), 1 when a rule fails,
2 for usage or environment errors.
"""

import argparse
import bisect
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pages as page_checks  # noqa: E402
from booklib import markdown, outline as outline_rules, prose, repo, settings  # noqa: E402

c_Data = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# The rules: (id, where the plan states it, warning, what fails).
c_Rules = [
    ('sentence-mean', 'style.md §2.2', False, 'the sentences of a page average more than 20 words'),
    ('sentence-max', 'style.md §2.2', False, 'a sentence has more than 35 words'),
    ('paragraph-length', 'style.md §2.2', False, 'a paragraph (each list item is one) holds more than five sentences'),
    ('prose-run', 'style.md §2.2', False, 'more than 500 words of paragraphs come without a heading, figure, fence, list, table, display formula or aside'),
    ('word-list', 'style.md §2.2, §2.3', False, 'a word is on none of the word lists and is no word of a glossary name, code, UI label, number or name (the entries of Further reading are not read)'),
    ('acronym', 'style.md §2.2', False, 'an acronym is not spelled out in parentheses beside its first use'),
    ('banned-word', 'style.md §2.2', False, 'simply, just, obviously, of course, clearly, basically, easy, easily, trivial, trivially, needless to say, as everyone knows, it follows, it is easy to see'),
    ('abbreviation', 'style.md §2.2', False, 'e.g., i.e., etc., vs., cf. or approx.'),
    ('contraction', 'style.md §2.2', False, "a contraction (n't, 're, 've, 'll, 'd, 'm, it's, that's, there's, what's, here's, let's)"),
    ('phrasal-verb', 'style.md §2.2', False, 'a phrasal verb of tools/data/phrasal-verbs.json where a single verb exists'),
    ('idiom', 'style.md §2.1, §2.2', False, 'an idiom of tools/data/idioms.txt'),
    ('pronoun-start', 'style.md §2.2', False, 'a paragraph starts with It or They, or with This, That, These or Those followed by punctuation or a verb'),
    ('noun-stack', 'style.md §2.2', True, 'three or more words in a row that are no function words, verbs or words ending in -ly, -ing or -ed'),
    ('passive', 'style.md §2.2', True, 'a form of "be" followed within two words by a word ending in -ed or -en or by an irregular past participle'),
    ('link-text', 'style.md §2.1, §2.2', False, 'link text "here", "this", "this page", "link", "click here" or "read more"'),
    ('copied-text', 'style.md §2.1, §2.2', False, 'ten words in a row that also stand in plan/inventory/*.md, or in AGENTS.md, Docs/DeveloperGuide.md or Docs/Manual/*.md at the pin'),
    ('heading-case', 'style.md §2.1, §2.2', True, 'a capitalized word after the first of a heading or title that is no name, glossary term written with capitals, or code'),
    ('size', 'style.md §2.2, §6.1', False, "the prose words do not fit the page's size (S 600 to 2,250; M 2,251 to 4,000; L 4,001 to 6,500; XL 6,501 to 10,000), or the size is not the row's"),
    ('time', 'style.md §2.2, §6.1', False, 'time is below the reading floor (prose words / 120 + lines of code / 10, rounded up to 5 minutes), or above twice it on concept and internals pages'),
    ('other-name', 'style.md §2.1, §3', False, 'a name the glossary lists under "avoid"'),
    ('block-quote-length', 'style.md §2.1', False, 'a block quote over 60 words, or without a line that names its source'),
    ('deep-heading', 'style.md §2.1', False, 'a heading below level 4, or math in a heading'),
    ('dollar-digit', 'style.md §4', False, '"$" before a digit in prose, which Markdown reads as math'),
    ('scope-in-prose', 'style.md §2.2 (spike)', False, '"a::b" outside backticks'),
    ('html-in-prose', 'style.md §2.2 (spike)', False, 'raw HTML, or a template such as Ref<Scene>, outside backticks'),
    ('unfinished', 'style.md §2.2 (spike)', False, 'TODO, FIXME, TBD or XXX left in a page'),
    ('unlabelled-code', 'style.md §2.2, §9.2', False, 'a C++ or shader fence that is no quote (src=), no sketch (sketch=) and not marked pseudocode'),
    ('no-language', 'style.md §2.2', False, 'a fence without a language'),
    ('long-quote', 'style.md §9.1', False, 'an engine quote outside 5 to 60 lines, or a fence over 25 lines on a page of track G or B or of level 1'),
    ('mdx', 'style.md §2.2, site.md', False, 'an .mdx file under src/content'),
    ('term-mark', 'style.md §3', False, 'the first use of a term homed in the Needs closure is not a :term mark (outside quotes, the test-out box and Further reading entries; a sentence that links its home, holds or follows a bold definition asks for none)'),
    ('term-source', 'style.md §3', True, "a marked term's home is neither the page nor in its Needs closure"),
    ('term-defined', 'style.md §3', False, 'on its home page or use home, a term is nowhere in bold'),
    ('term-paragraph', 'style.md §3', False, 'a paragraph defines more than one new term'),
    ('term-section', 'style.md §3', False, 'a level-2 section defines more than four new terms'),
    ('math-symbols', 'style.md §4', False, 'a symbol of a display formula that the page has not named is not inline math in the block after it'),
    ('math-derivation', 'style.md §4', True, 'more than four display formulas in one level-2 section outside :::derivation boxes'),
    ('math-g', 'style.md §4', False, 'on a page of track G that is no primer, a display formula outside a :::note[The formula] aside or a :::derivation box, or such an aside without a paragraph before it'),
    ('exercise-order', 'style.md §8', False, 'an exercise does not start with **Basic.**, **Medium.** or **Hard.**, or the levels go down'),
    ('code-intro', 'style.md §9.1', False, 'the block before a fence is no paragraph'),
    ('code-follow', 'style.md §9.1', False, 'the block after a fence is no paragraph or numbered list (or the output of the same sketch, then one)'),
    ('callouts', 'style.md §9.1', False, 'a fence of 10 or more lines is not followed by 1 to 5 callouts that start with "Line N:" or "Lines N–M:" inside its lines'),
    ('cpp-feature', 'style.md §9.1', False, 'a C++ feature whose home is neither the page nor in its Needs closure has no :::question aside, linking the home, before its first fence (one finding per fence names every such feature)'),
    ('step-parts', 'style.md §10', False, 'a step of a tutorial, or of a how-to on track G or B, lacks **You should see:** or **If you do not see it:**'),
    ('simplified-link', 'style.md §12', False, 'a :::simplified aside holds no link'),
    ('analogy-limit', 'style.md §12', False, 'the last paragraph of an :::analogy aside does not start with **Where it breaks:**'),
    ('g-frame-share', 'style.md §13', False, 'on a page of track G, a time in ms without its share of a frame (a % in the same sentence)'),
    ('w8r-preset', 'style.md §13', False, 'on a page the outline marks W8r, a number in the same sentence as Low, Medium, High or Ultra'),
    ('id', 'style.md §6.1, site.md O1 and O7', False, "the id is not the file's path, not a valid id, or not a row of the outline"),
    ('title', 'style.md §6.1, rulings 5 R17', False, "the title is missing, not in double quotes, or not the row's"),
    ('description', 'style.md §6.1', False, 'the description is missing, not in double quotes, or not one sentence of at most 160 characters'),
    ('kind', 'style.md §6.1', False, "the kind is not a kind, or not the row's"),
    ('tracks', 'style.md §6.1', False, "the tracks are not letters of G, B and E, or not the row's"),
    ('needs', 'style.md §6.1', False, "the Needs are not page ids, more than five, or not the row's"),
    ('learn', 'style.md §6.1', False, 'the learn lines are not two to five {id, text} with an observable verb'),
    ('since', 'style.md §6.1', False, 'since is missing where it is required, present where it is not, or not a release from 0.3.0 to the pin\'s'),
    ('status', 'style.md §6.1', False, 'the status is not draft, reviewed or final'),
    ('front-matter', 'style.md §6.1', False, 'the front matter cannot be read, or holds a key that is not the book\'s'),
    ('inline-env', 'site.md, "The base path", rule 3', False, 'import.meta.env inside a <script is:inline>'),
    ('literal-origin', 'rulings 6, R24', False, 'the origin of site.json written in another file than site.json, deploy/README.md, README.md and plan/'),
    ('front-matter-head', 'site.md, "The base path", rule 4', False, 'a head key in a page\'s front matter'),
]
c_RuleIds = [rule for rule, _, _, _ in c_Rules]
c_Warnings = {rule for rule, _, warning, _ in c_Rules if warning}
c_FrontMatterRules = ('id', 'title', 'description', 'kind', 'size', 'tracks', 'needs', 'time', 'learn', 'since', 'status')

c_MaxMean = 20
c_MaxSentence = 35
c_MaxParagraph = 5
c_MaxRun = 500
c_MaxQuoteWords = 60
c_QuoteLines = (5, 60)
c_MaxShortFence = 25
c_CalloutsFrom = 10
c_MaxCallouts = 5
c_CopiedRun = 10
c_MaxNewTerms = 4
c_MaxDerivationFormulas = 4
c_ReadingSpeed = 120  # prose words a minute
c_CodeSpeed = 10  # lines of code a minute
c_Sizes = outline_rules.c_Ranges  # S 600 to 2,250 and so on: one table, which plan/book.md states (outline.py checks it)
c_CodeLanguages = ('cpp', 'c++', 'c', 'h', 'hpp', 'hlsl', 'slang', 'glsl')
c_Banned = outline_rules.c_BannedWords
c_Abbreviations = ('e.g.', 'i.e.', 'etc.', 'vs.', 'cf.', 'approx.')
c_AbbreviationUse = {'e.g.': 'for example', 'i.e.': 'that is', 'etc.': 'and others', 'vs.': 'against', 'cf.': 'compare', 'approx.': 'about'}
c_Contraction = re.compile(r"n['\u2019]t\b|['\u2019](re|ve|ll|d|m)\b|\b(it|that|there|what|here|let)['\u2019]s\b", re.IGNORECASE)
c_LinkTexts = ('here', 'this', 'this page', 'link', 'click here', 'read more')
c_BeForms = ('am', 'is', 'are', 'was', 'were', 'be', 'been', 'being')
c_Pronouns = ('it', 'them', 'this', 'that', 'these', 'those', 'him', 'her', 'us', 'you', 'me')
c_SingularPointers = ('This', 'That')
c_PluralPointers = ('These', 'Those')
c_ExerciseLevels = ('Basic.', 'Medium.', 'Hard.')
c_ExerciseSections = ('Exercises', 'Practice')
c_Presets = ('Low', 'Medium', 'High', 'Ultra')
c_StepSee = '**You should see:**'
c_StepUnseen = '**If you do not see it:**'
c_DerivedEndings = ('ies', 'es', 's', 'ed', 'd', 'ing', 'er', 'est', 'ly')
c_Url = re.compile(r'\]\([^)]*\)|<https?://[^>]+>|https?://\S+')
c_Greek = ('alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa',
           'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi',
           'varphi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi',
           'Psi', 'Omega')
c_TexTextCommands = ('text', 'textrm', 'textit', 'textbf', 'mathrm', 'operatorname', 'mbox', 'texttt', 'textsf')
c_TexAccents = ('vec', 'hat', 'bar', 'tilde', 'dot', 'ddot', 'mathbf', 'boldsymbol', 'bm', 'mathcal', 'mathbb', 'mathit',
                'overline', 'underline', 'widehat', 'widetilde', 'overrightarrow')
c_Acronym = re.compile(r'^(?=(?:[0-9]*[A-Z]){2})[A-Z0-9]+(s)?$')
c_OpeningPunctuation = '"\'([{“‘'
c_TwoLetters = re.compile(r'[A-Za-z]{2}')
c_Digit = re.compile(r'\d')
c_TrailingPunctuation = re.compile(r'[.,;:!?)\]"\'\u2019\u201d]+$')
c_LowerWord = re.compile(r"^[a-z][a-z'-]*$")
c_PlainWord = re.compile(r'^[A-Za-z]+$')
c_NotLetters = re.compile(r"[^A-Za-z']+")
c_Possessive = re.compile(r"['\u2019]s$")
c_Number = re.compile(r'^[-+\u2212]?\d+([.,]\d+)*$')
c_InlineScript = re.compile(r'<script\b(?P<attributes>[^>]*)>(?P<body>.*?)</script\s*>', re.DOTALL | re.IGNORECASE)
# literal-origin: the files that may write the origin (rulings 6, R24), and the folders no rule reads.
c_OriginFiles = ('site.json', 'deploy/README.md', 'README.md')
c_UnreadFolders = ('.git', 'node_modules', '.tools', 'dist', 'stage', 'release', 'originals', '.astro', '.cache', 'plan')
c_MaxScannedBytes = 8 * 1024 * 1024
c_SiteCode = ('.astro', '.html', '.md', '.mdx', '.js', '.mjs', '.ts', '.jsx', '.tsx', '.svelte', '.vue')


class Finding:
    def __init__(self, path, line, rule, message):
        self.path, self.line, self.rule, self.message = path, line, rule, message

    @property
    def warning(self):
        return self.rule in c_Warnings

    def __str__(self):
        return '%s:%d: %s%s: %s' % (self.path, self.line, self.rule, ' (warning)' if self.warning else '', self.message)

    def __repr__(self):
        return 'Finding(%r)' % str(self)


class LintError(Exception):
    """An environment or usage error: exit code 2."""


# The word lists of tools/data/.

def read_lines(path):
    with open(path, encoding='utf-8') as file:
        return [line.rstrip('\n') for line in file if line.strip() and not line.startswith('#')]


def read_json(path):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


class WordLists:
    def __init__(self, folder=c_Data):
        try:
            self.common = set()  # common-words.txt alone: its headwords and their forms (a term of one of these is an everyday word)
            for line in read_lines(os.path.join(folder, 'common-words.txt')):
                self.common.update(word.lower() for word in line.split())
            self.vocabulary = set(self.common)
            self.extra = {}
            for line in read_lines(os.path.join(folder, 'extra-words.txt')):
                word, _, covered = line.partition('\t')
                self.extra[word.strip().lower()] = covered.strip()
            self.vocabulary.update(self.extra)
            self.memo = {}
            self.names = set()
            self.long_names = {}  # first word -> word tuples of names of several words
            for name in read_lines(os.path.join(folder, 'names.txt')):
                words = tuple(name.split())
                if len(words) == 1:
                    self.names.add(words[0])
                else:
                    self.long_names.setdefault(words[0], []).append(words)
            for first in self.long_names:
                self.long_names[first].sort(key=len, reverse=True)
            self.name_firsts = self.names | set(self.long_names)
            self.acronyms = set(read_json(os.path.join(folder, 'acronyms.json'))['exempt'])
            self.phrasal = read_json(os.path.join(folder, 'phrasal-verbs.json'))['verbs']
            self.idioms = [tuple(line.strip().lower().split()) for line in read_lines(os.path.join(folder, 'idioms.txt'))]
            self.idiom_starts = {}  # a form of an idiom's first word -> the idioms
            for idiom in self.idioms:
                first = idiom[0]
                forms = {first, first + 's', first + 'es', first + 'ed', first + 'd', first + 'ing',
                         first + first[-1:] + 'ing', first + first[-1:] + 'ed'}
                if first.endswith('e'):
                    forms.add(first[:-1] + 'ing')
                for form in forms:
                    self.idiom_starts.setdefault(form, []).append(idiom)
            self.phrasal_forms = {}  # a form of a phrasal verb -> its entries
            for entry in self.phrasal:
                for form in entry['forms']:
                    self.phrasal_forms.setdefault(form, []).append(entry)
            self.function_words = {line.strip().lower() for line in read_lines(os.path.join(folder, 'function-words.txt'))}
            self.verb_forms = set()
            self.third_forms = set()
            self.base_forms = set()
            self.irregular_pasts = set()
            self.modals = set()
            for line in read_lines(os.path.join(folder, 'verbs.txt')):
                fields = line.split('\t')
                if len(fields) != 4:
                    raise LintError('%s: "%s" does not have four fields separated by tabs' % (os.path.join(folder, 'verbs.txt'), line))
                base, third, pasts, ing = fields
                forms = [form for form in [base, third, ing] + pasts.split(',') if form and form != '-']
                self.verb_forms.update(forms)
                self.base_forms.add(base)
                self.third_forms.add(third)
                if third == base:
                    self.modals.add(base)
                    continue  # a modal's past ("could") is no participle
                if base in ('be', 'have'):
                    continue  # "It is what was drawn": "was" and "had" are no participles of a passive
                for past in pasts.split(','):
                    if past and past != '-' and not past.endswith('ed'):
                        self.irregular_pasts.add(past)
            self.features = read_json(os.path.join(folder, 'cpp-features.json'))['features']
            for feature in self.features:
                feature['compiled'] = [re.compile(pattern, re.MULTILINE) for pattern in feature['patterns']]
        except (OSError, ValueError, KeyError) as error:
            raise LintError('the word lists in %s cannot be read: %s' % (folder, error))

    def known(self, word):
        """True when a word (lowercase, letters only) or the word without one ending of style.md §2.2 is listed."""
        if word in self.vocabulary:
            return True
        if word in self.memo:
            return self.memo[word]
        self.memo[word] = found = self.derived(word)
        return found

    def common_word(self, word):
        """True when a word (lowercase) is one of common-words.txt, as its lines give it (a headword and its forms) or
        with the plural endings the glossary's names take (style.md §3, "simple plurals"; rulings-11.md, R53)."""
        if word in self.common:
            return True
        if word.endswith('ies') and word[:-3] + 'y' in self.common:
            return True
        return (word.endswith('es') and word[:-2] in self.common) or (word.endswith('s') and word[:-1] in self.common)

    def derived(self, word):
        for ending in c_DerivedEndings:
            if word.endswith(ending) and len(word) > len(ending) + 1:
                stem = word[:-len(ending)]
                if ending == 'ies' and stem + 'y' in self.vocabulary:
                    return True
                if ending != 'ies' and stem in self.vocabulary:
                    return True
        return False


# The glossary.

c_Qualifier = re.compile(r'^(?P<base>.*?\S)\s*\([^()]*\)$')


def base_name(name):
    """The words of a name that a page writes: a trailing parenthesis qualifies the entry ("Clip (animation)") and is
    no part of them (rulings-11.md, R53)."""
    match = c_Qualifier.match(name.strip())
    return match.group('base') if match else name.strip()


class Glossary:
    def __init__(self, entries):
        self.entries = []
        self.by_id = {}
        self.names = {}  # tuple of lowercase words -> entry (the first that has the name)
        self.choices = {}  # tuple of lowercase words -> every entry that has the name, in the glossary's order
        self.avoid = {}  # tuple of lowercase words -> entry
        self.longest = 1
        self.capital_words = set()  # the capitalized words of names written with capitals (heading-case keeps them)
        plain_homes = plain_name_homes(entries)
        for raw in entries:
            if not isinstance(raw, dict) or not isinstance(raw.get('term'), str):
                continue
            entry = dict(raw)
            entry['id'] = raw.get('id') or page_checks.glossary_id(raw['term'])
            self.entries.append(entry)
            self.by_id.setdefault(entry['id'], entry)
            names = [raw['term']] + [alias for alias in raw.get('aliases') or [] if isinstance(alias, str)]
            entry['names'] = names
            for name in names:
                words = name_words(name, raw.get('home'), plain_homes)
                name = ' '.join(words)
                if any(char.isupper() for char in name):
                    self.capital_words.update(word for word in name.split() if word[:1].isupper())
                # A page's word key drops the apostrophes around it ("players'" -> "players"), so the name's do too.
                for variant in plural_variants(tuple(word.strip("'’") for word in name.lower().split())):
                    self.names.setdefault(variant, entry)
                    owners = self.choices.setdefault(variant, [])
                    if entry not in owners:
                        owners.append(entry)
                    self.longest = max(self.longest, len(variant))
            for name in raw.get('avoid') or []:
                if isinstance(name, str):
                    for variant in plural_variants(tuple(base_name(name).lower().split())):
                        self.avoid.setdefault(variant, entry)
                        self.longest = max(self.longest, len(variant))
        self.firsts = {name[0] for name in self.names}
        self.avoid_firsts = {name[0] for name in self.avoid}
        # Every word of a name or alias, its head word alone included ("preset" of "CMake preset"): a known word of
        # word-list wherever it stands, marked or not (rulings-11.md, R54).
        self.words = {part.lower() for name in self.names for word in name for part in word_parts(word)}

    def known(self, word):
        """True when a word (lowercase) or the word without one ending of style.md §2.2 is a word of a glossary name."""
        if word in self.words:
            return True
        for ending in c_DerivedEndings:
            if word.endswith(ending) and len(word) > len(ending) + 1:
                stem = word[:-len(ending)]
                if (stem + 'y' if ending == 'ies' else stem) in self.words:
                    return True
        return False


def plain_name_homes(entries):
    """(lowercase words of a name without a qualifier, home) of every entry: the names a qualified name of the same
    home must not take over."""
    homes = set()
    for raw in entries:
        if not isinstance(raw, dict) or not isinstance(raw.get('term'), str):
            continue
        for name in [raw['term']] + [alias for alias in raw.get('aliases') or [] if isinstance(alias, str)]:
            if not c_Qualifier.match(name.strip()):
                homes.add((tuple(name.lower().split()), raw.get('home')))
    return homes


def name_words(name, home, plain_homes):
    """The words a page writes for a name. A qualifier is no part of them (R53), except where another entry of the
    same home holds the name before it ("luminance" and "Luminance (Y)", both homed on basics/color): the page cannot
    write the two apart otherwise, so the qualified entry is written with its parenthesis, as its whole name."""
    base = base_name(name)
    if base != name.strip() and (tuple(base.lower().split()), home) in plain_homes:
        return [part for part in (word.strip('()') for word in name.split()) if part]
    return base.split()


def code_name(name):
    """The code of a name written as one code span ("`ST_CORE_ASSERT`"), else None. Code spans joined by punctuation
    without spaces ("`sigsetjmp`/`siglongjmp`") are one code word of a page's text, so their code is the spans joined."""
    match = re.fullmatch(r'`[^`]+`(?:[^\s`\w]+`[^`]+`)*', name.strip())
    return match.group(0).replace('`', '') if match else None


def defined_as_code(page, entry):
    """True when the page writes one of the entry's code names as a bold code span: a code word is no word that
    match_names reads, so a term whose name is code is defined by **`ST_CORE_ASSERT`** alone."""
    codes = {code for code in map(code_name, entry.get('names', [])) if code}
    if not codes:
        return False
    return any(word.kind == 'code' and word.bold and word.text in codes
               for block in page.body.blocks if block.kind not in ('heading', 'label') for word in block.words)


def plural_variants(words):
    """A name and its simple plurals (style.md §3: "simple plurals"): -s, -es, and -y as -ies."""
    if not words:
        return []
    last = words[-1]
    variants = [words, words[:-1] + (last + 's',), words[:-1] + (last + 'es',)]
    if last.endswith('y'):
        variants.append(words[:-1] + (last[:-1] + 'ies',))
    return variants


def read_glossary(path):
    try:
        data = read_json(path)
    except FileNotFoundError:
        return Glossary([])
    except (OSError, ValueError) as error:
        raise LintError('the glossary %s cannot be read: %s' % (path, error))
    return Glossary(data.get('terms', []) if isinstance(data, dict) else [])


# The sources of copied-text.

class Sources:
    """Every run of c_CopiedRun words (lowercased, punctuation removed) of the source documents."""

    def __init__(self, documents):
        self.runs = set()
        self.texts = []
        for name, text in documents:
            words = [word for word in (prose.normalize(part) for part in c_Url.sub(']', text).split()) if word]
            self.texts.append((name, ' %s ' % ' '.join(words)))
            for index in range(len(words) - c_CopiedRun + 1):
                self.runs.add(hash(tuple(words[index:index + c_CopiedRun])))

    def source_of(self, words):
        joined = ' %s ' % ' '.join(words)
        return next((name for name, text in self.texts if joined in text), 'a source')


def read_sources(engine, commit, plan):
    documents = []
    inventory = os.path.join(plan, 'inventory')
    if os.path.isdir(inventory):
        for name in sorted(os.listdir(inventory)):
            if name.endswith('.md'):
                documents.append(('plan/inventory/' + name, repo.read_text(os.path.join(inventory, name))))
    listing = engine.git('ls-tree', '--name-only', commit + '~0', 'Docs/Manual/', check=False)
    manual = sorted(name for name in listing.stdout.decode('utf-8', 'replace').split('\n') if name.endswith('.md')
                    and name.count('/') == 2)
    for path in ['AGENTS.md', 'Docs/DeveloperGuide.md'] + manual:
        lines = engine.read(commit, path)
        if lines is not None:
            documents.append((path + ' at the pin', '\n'.join(lines)))
    return Sources(documents)


# A page and what the rules read of it.

class PageText:
    def __init__(self, lint, page_id, path):
        self.id = page_id
        self.path = path
        self.file = lint.layout.relative(path)
        self.book_page = page_checks.BookPage(lint.layout, path)
        self.data = self.book_page.data or {}
        self.text = self.book_page.text
        self.body = prose.Page(self.text)
        self.row = lint.outline.by_id.get(page_id)
        self.kind = self.data.get('kind') if isinstance(self.data.get('kind'), str) else None
        tracks = self.data.get('tracks')
        self.tracks = [track for track in tracks if isinstance(track, str)] if isinstance(tracks, list) else []
        self.level = outline_rules.level(lint.outline, self.row) if self.row is not None else None
        self.taught = outline_rules.taught(lint.outline, page_id, lint.taught_memo) if self.row is not None else set()
        self.captions = []
        for block in self.body.blocks:
            if block.kind == 'fence' and block.fence.lang == 'mermaid':
                for key in ('caption', 'alt'):
                    if block.fence.attributes.get(key):
                        self.captions.append(caption_block(block.fence.attributes[key], block.line, self.file))
        manifest = os.path.join(lint.layout.figures, *(page_id + '.json').split('/'))
        if os.path.isfile(manifest):
            self.captions += manifest_captions(manifest, lint.layout.relative(manifest))

    def blocks(self, kinds=None, quotes=True, captions=True):
        found = [block for block in self.body.blocks if block.words and (quotes or block.kind != 'quote')]
        if captions:
            found += self.captions
        return [block for block in found if kinds is None or block.kind in kinds]


def caption_block(text, line, source):
    block = prose.Block('caption', line, [], None)
    block.lines = [(line, text)]
    block.source = source
    prose.fill_prose(block)
    return block


def manifest_captions(path, relative):
    """The caption and alt text of every figure of a manifest, with the manifest's lines."""
    text = repo.read_text(path)
    try:
        data = json.loads(text)
    except ValueError:
        return []  # tools/figures.py check reports a manifest that is not JSON
    lines = text.split('\n')
    found = []
    position = 0
    for figure in data.get('figures', []) if isinstance(data, dict) else []:
        if not isinstance(figure, dict):
            continue
        for key in ('caption', 'alt'):
            value = figure.get(key)
            if not isinstance(value, str):
                continue
            line = next((index + 1 for index in range(position, len(lines)) if '"%s"' % key in lines[index]), position + 1)
            position = max(position, line - 1)
            found.append(caption_block(value, line, relative))
    return found


class Terms:
    """What the term rules read: the outline, the word lists and the glossary. tools/markterms.py runs the term rules
    with it alone (it needs no engine); Lint adds the engine and the sources of copied-text."""

    def __init__(self, layout, plan=None, book=outline_rules.c_Book, glossary=None, data=c_Data):
        self.layout = layout
        self.plan = plan or os.path.join(layout.root, 'plan')
        self.outline = outline_rules.read(self.plan, book, documents=False)
        self.taught_memo = {}
        self.words = WordLists(data)
        self.glossary = read_glossary(glossary or layout.glossary)


class Lint(Terms):
    def __init__(self, layout, engine_path, plan=None, book=outline_rules.c_Book, glossary=None, data=c_Data):
        self.layout = layout
        self.plan = plan or os.path.join(layout.root, 'plan')
        try:
            self.pin = repo.read_pin(layout.pin_file)
        except (OSError, ValueError) as error:
            raise LintError('engine.pin cannot be read: %s' % error)
        try:
            self.engine = repo.Engine(engine_path)
            self.commit = self.engine.resolve(self.pin['commit'])
        except repo.EngineError as error:
            raise LintError(str(error))
        try:
            Terms.__init__(self, layout, plan, book, glossary, data)
            self.sources = read_sources(self.engine, self.commit, self.plan)
        finally:
            self.engine.close()

    def run(self, names=(), report_folder=None):
        self.notes = []
        self.measured = []  # (file, prose words, size) of each page linted: what the size rule counted
        findings = site_findings(self.layout) + origin_findings(self.layout, self.notes)
        known = {page_id for page_id, _ in self.layout.pages()}
        names = [repo.named_page(name) for name in names]
        for name in names:
            if name not in known:
                raise LintError('no page %s under src/content/docs/ (give page ids such as core/time)' % name)
        for page_id, path in self.layout.pages():
            if names and page_id not in names:
                continue
            page = PageText(self, page_id, path)
            page_findings, report = lint_page(self, page)
            findings += page_findings
            if 'words' in report:
                self.measured.append((page.file, report['words'], page.data.get('size')))
            if report_folder:
                write_report(report_folder, page, report, page_findings)
        return findings


# Site code: rules inline-env and mdx.

def site_findings(layout):
    findings = []
    source = os.path.join(layout.root, 'src')
    for folder, directories, files in os.walk(source):
        directories[:] = sorted(directory for directory in directories if directory not in ('node_modules', '.astro'))
        for name in sorted(files):
            path = os.path.join(folder, name)
            relative = layout.relative(path)
            if name.endswith('.mdx') and relative.startswith('src/content/'):
                findings.append(Finding(relative, 1, 'mdx', 'the book is plain Markdown: rename the file to .md and write '
                                        'directives instead of components (site.md, "What MDX would have given")'))
            if not name.endswith(c_SiteCode):
                continue
            try:
                text = repo.read_text(path)
            except (OSError, UnicodeDecodeError):
                continue
            for match in c_InlineScript.finditer(text):
                if not re.search(r'(^|\s)is:inline(\s|=|$)', match.group('attributes')):
                    continue
                body_start = match.start('body')
                for use in re.finditer(r'import\.meta\.env', match.group('body')):
                    line = text.count('\n', 0, body_start + use.start()) + 1
                    findings.append(Finding(relative, line, 'inline-env', 'import.meta.env stays literal in an inline script '
                                            '(Vite does not process it): pass the value through a data- attribute or '
                                            'define:vars (site.md, "The base path", rule 3)'))
    return findings


def origin_findings(layout, notes):
    """literal-origin: the origin of site.json in any other file of the repository but the three that may hold it and
    plan/. Without a readable site.json the rule is not run, and a note says so."""
    try:
        origin = settings.read_site(layout.root)['origin']
    except settings.SettingsError as error:
        notes.append('literal-origin was not checked: %s' % error)
        return []
    needle = ('//' + origin.split('//', 1)[1]).lower().encode('utf-8')
    findings = []
    for folder, directories, files in os.walk(layout.root):
        relative_folder = os.path.relpath(folder, layout.root).replace(os.sep, '/')
        directories[:] = sorted(directory for directory in directories
                                if not (relative_folder == '.' and directory in c_UnreadFolders)
                                and directory not in ('.git', 'node_modules', '__pycache__'))
        for name in sorted(files):
            path = os.path.join(folder, name)
            relative = layout.relative(path)
            if relative in c_OriginFiles:
                continue
            try:
                if os.path.getsize(path) > c_MaxScannedBytes:
                    continue
                with open(path, 'rb') as file:
                    data = file.read()
            except OSError:
                continue
            if b'\0' in data[:8192]:
                continue  # a picture, a font, an archive
            lowered = data.lower()
            start = lowered.find(needle)
            while start >= 0:
                findings.append(Finding(relative, lowered.count(b'\n', 0, start) + 1, 'literal-origin',
                                        'the address %s is written only in site.json (rulings 6, R24): read it from there '
                                        '(src/lib/settings.mjs in the build, tools/booklib/settings.py in the tools)' % origin))
                start = lowered.find(needle, start + 1)
    return findings


# The rules of one page.

def lint_page(lint, page):
    findings = []
    report = {}

    def add(block_or_line, rule, message, source=None):
        if isinstance(block_or_line, int):
            line, file = block_or_line, source or page.file
        else:
            line, file = block_or_line.line, block_or_line.source or page.file
        findings.append(Finding(file, line, rule, message))

    front_matter_rules(lint, page, findings)
    if page.book_page.special:
        language_rules(lint, page, add, report)
        return findings, report
    occurrences = term_occurrences(lint, page)
    language_rules(lint, page, add, report)
    term_rules(lint, page, add, report, occurrences)
    math_rules(lint, page, add)
    code_rules(lint, page, add)
    structure_rules(lint, page, add)
    number_rules(lint, page, add)
    measure_rules(lint, page, add, report)
    return findings, report


def front_matter_rules(lint, page, findings):
    """style.md §6.1 through tools/pages.py's checks (one implementation), each message under its key's rule."""
    book_page = page.book_page
    report = page_checks.Report(release=False)
    if book_page.error:
        findings.append(Finding(page.file, page_checks.error_line(book_page.error), 'front-matter',
                                'the front matter is not valid YAML or not the book\'s subset: %s'
                                % re.sub(r'^line \d+: ', '', book_page.error)))
    page_checks.check_quoting(book_page, report)
    if not book_page.error:
        if book_page.special:
            page_checks.check_special_page(book_page, report)
        elif book_page.part_page:
            page_checks.check_part_page(book_page, lint.outline, report)
        else:
            if page.row is None:
                findings.append(Finding(page.file, 1, 'id', '%s is no row of the outline (plan/outline-*.md): ask the planner '
                                        'for a row, or rename the file to its row\'s id' % page.id))
            page_checks.check_book_page(book_page, page.row, lint.outline, lint.pin, report)
        if not book_page.special:
            for problem, advice in outline_rules.id_problems(page.id, part_page=book_page.part_page):
                findings.append(Finding(page.file, 1, 'id', '%s: %s' % (problem, advice)))
    for where, message in report.errors:
        key = getattr(where, 'key', None)
        if key == 'head':
            rule = 'front-matter-head'
            message = 'pages set no head: remove the key (site.md, "The base path", rule 4)'
        elif key in c_FrontMatterRules:
            rule = key
        else:
            rule = 'front-matter'
        file, _, line = where.rpartition(':')
        findings.append(Finding(file, int(line) if line.isdigit() else 1, rule, message))


# Words and their lookups.

def bare(word):
    """A word without the punctuation around it and without a possessive "'s"."""
    return word.plain


def name_spans(lint, words):
    """The indexes of the words that belong to a name of tools/data/names.txt, as written."""
    covered = set()
    if not any(word.plain in lint.words.name_firsts for word in words):
        return covered
    texts = [bare(word) if word.kind == 'word' else None for word in words]
    for index, word in enumerate(words):
        if texts[index] is None:
            continue
        if texts[index] in lint.words.names or word.bare in lint.words.names:
            covered.add(index)
        for name in lint.words.long_names.get(texts[index], []):
            if tuple(texts[index:index + len(name)]) == name:
                covered.update(range(index, index + len(name)))
                break
    return covered


def word_parts(text):
    if c_PlainWord.match(text):
        return [text]
    return [part for part in c_NotLetters.split(text) if part.strip("'")]


class Occurrence:
    def __init__(self, entry, block, words, synthetic=False):
        self.entry = entry
        self.block = block
        self.words = words
        self.line = words[0].line
        self.bold = all(word.bold for word in words)
        marks = {word.term for word in words}
        self.mark = marks.pop() if len(marks) == 1 else None
        links = {word.link for word in words}
        self.link = links.pop() if len(links) == 1 else None
        self.synthetic = synthetic


def match_names(table, longest, words, firsts=None):
    """(start, end, entry) of the longest names of a table found in a list of words (code and formulas break a
    name; a possessive "'s" on its last word is allowed). `firsts` is the set of the names' first words."""
    found = []
    index = 0
    keys = [word.key if word.kind == 'word' else None for word in words]
    plain = [word.plain.lower() if word.kind == 'word' else None for word in words]
    while index < len(words):
        if keys[index] is None or (firsts is not None and keys[index] not in firsts and plain[index] not in firsts):
            index += 1
            continue
        hit = None
        for length in range(min(longest, len(words) - index), 0, -1):
            window = keys[index:index + length]
            if None in window:
                continue
            for candidate in (tuple(window), tuple(window[:-1]) + (plain[index + length - 1],)):
                if candidate in table:
                    hit = (index, index + length, table[candidate])
                    break
            if hit:
                break
        if hit:
            found.append(hit)
            index = hit[1]
        else:
            index += 1
    return found


def choose_entry(page, entries):
    """Of the entries that share a name ("Batch (assets)", "Batch (draw)"), the one a page means: the one homed on
    the page, else the one taught in its Needs closure, else the first."""
    if len(entries) == 1:
        return entries[0]
    for entry in entries:
        if is_home(entry, page.id):
            return entry
    for entry in entries:
        if taught_before(page, entry):
            return entry
    return entries[0]


def term_occurrences(lint, page):
    """Every use of a glossary name on the page, in reading order, outside headings, container titles and captions."""
    occurrences = []
    glossary = lint.glossary
    for block in page.body.blocks:
        if not block.words or block.kind in ('heading', 'label'):
            continue
        found = match_names(glossary.choices, glossary.longest, block.words, glossary.firsts)
        covered = set()
        for start, end, entries in found:
            occurrence = Occurrence(choose_entry(page, entries), block, block.words[start:end])
            occurrences.append(occurrence)
            covered.update(range(start, end))
        # A :term mark whose text holds none of its entry's names is a use of that entry too.
        index = 0
        while index < len(block.words):
            word = block.words[index]
            if word.term is None:
                index += 1
                continue
            end = index
            while end < len(block.words) and block.words[end].term == word.term:
                end += 1
            entry = glossary.by_id.get(word.term)
            if not any(other.block is block and other.entry is entry and other.words[0] in block.words[index:end]
                       for other in occurrences):
                occurrences.append(Occurrence(entry, block, block.words[index:end], synthetic=True))
            index = end
    occurrences.sort(key=lambda occurrence: (page.body.blocks.index(occurrence.block), occurrence.block.words.index(occurrence.words[0])))
    return occurrences


def is_home(entry, page_id):
    return entry is not None and page_id in (entry.get('home'), entry.get('use'))


class TextView:
    """The words joined by single spaces (code and formulas as one sign each); line_at(offset) is the line of the word
    at a character."""

    def __init__(self, words):
        parts = []
        self.starts = []
        self.words = words
        position = 0
        for word in words:
            piece = word.text if word.kind == 'word' else '\u2400'
            self.starts.append(position)
            parts.append(piece)
            position += len(piece) + 1
        self.text = ' '.join(parts)

    def line_at(self, offset):
        return self.words[max(bisect.bisect_right(self.starts, offset) - 1, 0)].line


def word_pattern(phrase):
    return re.compile(r'(?<![\w-])' + r'\s+'.join(map(re.escape, phrase.split())) + r'(?![\w-])', re.IGNORECASE)


c_BannedPatterns = [(word, word_pattern(word)) for word in c_Banned]
c_AbbreviationPatterns = [(text, re.compile(r'(?<![A-Za-z])' + re.escape(text), re.IGNORECASE)) for text in c_Abbreviations]


def further_reading_entry(block):
    """True for a list item of the section "## Further reading": an entry that names a source."""
    return block.kind == 'item' and block.section == 'Further reading'


def language_rules(lint, page, add, report):
    """style.md §2.1 and §2.2: the rules on the words of each prose block."""
    lists = lint.words
    glossary = lint.glossary
    own_blocks = page.blocks(quotes=False)
    unknown = {}
    acronyms_seen = set()
    for block in page.blocks():
        words = block.words
        names = name_spans(lint, words)
        view = TextView(words)
        text = view.text
        own = block.kind != 'quote'
        further = further_reading_entry(block)  # names of people and works: word-list does not read them (R54)
        if own:
            lowered = text.lower()
            for phrase, pattern in c_BannedPatterns:
                if phrase.split()[0] not in lowered:
                    continue
                for match in pattern.finditer(text):
                    add(view.line_at(match.start()), 'banned-word', '"%s" tells a reader who is lost that the reader is the problem: '
                        'say what to do instead ("only" or "immediately" where "just" was meant)' % phrase, block.source)
            for abbreviation, pattern in c_AbbreviationPatterns:
                for match in pattern.finditer(text):
                    add(view.line_at(match.start()), 'abbreviation', 'write "%s" instead of "%s"' % (c_AbbreviationUse[abbreviation], abbreviation), block.source)
            for index, word in enumerate(words):
                if word.kind == 'word' and ("'" in word.text or '\u2019' in word.text) and c_Contraction.search(word.text):
                    add(word.line, 'contraction', 'write "%s" out in full (no contractions; a possessive \'s is fine)' % word.bare, block.source)
            phrasal_verbs(lists, block, add)
            idioms(lists, block, add)
        for start, end, entry in match_names(lint.glossary.avoid, lint.glossary.longest, words, lint.glossary.avoid_firsts):
            add(words[start].line, 'other-name', '"%s" is called "%s" in this book (the glossary decides the name)'
                % (' '.join(word.bare for word in words[start:end]), entry['term']), block.source)
        for index, word in enumerate(words):
            if word.kind != 'word':
                continue
            if own and not word.bold and index not in names and block.kind not in ('heading', 'label') and not further:
                acronym_check(lists, block, index, acronyms_seen, add)
            if not own or word.bold or index in names or word.term is not None or further:
                continue
            text = bare(word)
            if not c_TwoLetters.search(text) or c_Digit.search(text):
                continue  # numbers, symbols and single letters (the x axis, track G)
            if c_PlainWord.match(text):
                known = lists.known(text.lower()) or glossary.known(text.lower())
            else:
                known = all(len(part.strip("'")) < 2 or lists.known(part.lower().strip("'")) or glossary.known(part.lower().strip("'"))
                            for part in word_parts(text))
            if not known:
                key = text.lower()
                if key not in unknown:
                    unknown[key] = (word.line, block.source or page.file, text, 0)
                line, file, shown, count = unknown[key]
                unknown[key] = (line, file, shown, count + 1)
        link_text_check(block, add)
    for key, (line, file, shown, count) in sorted(unknown.items(), key=lambda item: (item[1][1] != page.file, item[1][0])):
        add(line, 'word-list', '"%s"%s is on no word list (style.md §2.3): use a listed word, make it a glossary term through the '
            'chapter\'s notes, write it as code or a UI label, or ask the part editor to add it to tools/data/extra-words.txt'
            % (shown, ' (%d uses)' % count if count > 1 else ''), file)
    report['unknown'] = sorted((shown, line, count) for line, _, shown, count in unknown.values())
    sentence_rules(lint, page, own_blocks, add, report)
    raw_line_rules(lint, page, add)


def acronym_check(lists, block, index, seen, add):
    word = block.words[index]
    text = word.bare
    if len(text) < 2 or not (text[0].isupper() or text[0].isdigit()):
        return
    match = c_Acronym.match(text)
    if not match:
        return
    stem = text[:-1] if match.group(1) else text
    if stem in lists.acronyms or text in lists.acronyms or stem in seen:
        return
    seen.add(stem)
    words = block.words
    inside = word.text.startswith('(') and re.match(r'^\(\S+\)[.,;:!?]*$', word.text) and index >= 2
    after = False
    if index + 1 < len(words) and words[index + 1].text.startswith('('):
        count = 0
        for other in words[index + 1:]:
            count += 1
            if ')' in other.text:
                break
        else:
            count = 0
        after = count >= 2
    if not (inside or after):
        add(word.line, 'acronym', 'spell "%s" out at its first use on the page, with the acronym in parentheses: '
            '"graphics processing unit (GPU)"' % stem, block.source)


def phrasal_verbs(lists, block, add):
    words = [word if word.kind == 'word' else None for word in block.words]
    keys = [bare(word).lower() if word is not None else None for word in words]
    for index, key in enumerate(keys):
        for entry in lists.phrasal_forms.get(key, ()):
            if words[index].text.lower() != key:
                continue
            particle = entry['particle'].split()
            for gap in (0, 1):
                start = index + 1 + gap
                if gap and (start - 1 >= len(keys) or keys[start - 1] not in c_Pronouns or words[start - 1].text.lower() != keys[start - 1]):
                    continue
                if keys[start:start + len(particle)] == particle:
                    add(words[index].line, 'phrasal-verb', '"%s" is the phrasal verb "%s": write "%s"'
                        % (' '.join(word.text for word in words[index:start + len(particle)]), entry['phrase'], entry['use']), block.source)
                    break


def idioms(lists, block, add):
    keys = [bare(word).lower() if word.kind == 'word' else None for word in block.words]
    for index, key in enumerate(keys):
        for idiom in lists.idiom_starts.get(key, ()):
            if tuple(keys[index + 1:index + len(idiom)]) == idiom[1:]:
                add(block.words[index].line, 'idiom', '"%s" is an idiom: say what you mean in plain words'
                    % ' '.join(word.text for word in block.words[index:index + len(idiom)]), block.source)


def link_text_check(block, add):
    index = 0
    words = block.words
    while index < len(words):
        if words[index].link is None:
            index += 1
            continue
        end = index
        while end < len(words) and words[end].link_id == words[index].link_id:
            end += 1
        text = ' '.join(word.bare for word in words[index:end]).lower().strip()
        if text in c_LinkTexts:
            add(words[index].line, 'link-text', 'the link text "%s" does not say where it goes: write the page\'s or the section\'s '
                'name as the link text' % text, block.source)
        index = end


def sentence_rules(lint, page, blocks, add, report):
    """sentence-mean, sentence-max, paragraph-length, pronoun-start, passive, noun-stack, copied-text."""
    lists = lint.words
    sentences = []
    over = []
    for block in blocks:
        if block.kind in ('paragraph', 'item', 'caption'):
            for sentence in block.sentences:
                sentences.append((block, sentence))
                if len(sentence) > c_MaxSentence:
                    add(sentence[0].line, 'sentence-max', 'this sentence has %d words, more than %d: make two sentences, one '
                        'claim each' % (len(sentence), c_MaxSentence), block.source)
            if len(block.sentences) > c_MaxParagraph:
                over.append((block.line, len(block.sentences)))
                add(block, 'paragraph-length', 'this %s holds %d sentences, more than %d: split it where its idea changes'
                    % ('list item' if block.kind == 'item' else 'paragraph', len(block.sentences), c_MaxParagraph))
            pronoun_start(lists, block, add)
            for sentence in block.sentences:
                passive(lists, block, sentence, add)
                noun_stack(lint, block, sentence, add)
        if block.kind == 'heading':
            noun_stack(lint, block, block.words, add)
        copied_text(lint, block, add)
    words = sum(len(sentence) for _, sentence in sentences)
    mean = words / len(sentences) if sentences else 0.0
    longest = sorted(sentences, key=lambda pair: -len(pair[1]))
    report['sentences'] = len(sentences)
    report['mean'] = mean
    report['longest'] = (len(longest[0][1]), longest[0][1][0].line) if longest else (0, 0)
    report['paragraphs over'] = over
    if mean > c_MaxMean:
        examples = ', '.join('line %d: %d words' % (sentence[0].line, len(sentence)) for _, sentence in longest[:3])
        add(1, 'sentence-mean', 'the sentences of the page average %.1f words, more than %d: split the longest (%s)'
            % (mean, c_MaxMean, examples))


def pronoun_start(lists, block, add):
    words = [word for word in block.words if word.kind != 'word' or word.bare]
    if not words or words[0].kind != 'word':
        return
    first = words[0].text.lstrip('"\'(\u201c\u2018*_')
    head = re.match(r"^[A-Za-z]+", first)
    if not head:
        return
    head = head.group(0)
    if head in ('It', 'They') and first[len(head):len(head) + 1] in ('', ' ', "'", '\u2019', ',', ';', ':', '.'):
        if first[len(head):] in ("'s", '\u2019s'):
            return  # "Its" is a possessive pronoun too, but "It's" is a contraction the contraction rule reports
        add(words[0].line, 'pronoun-start', 'the %s starts with "%s", whose noun is in another paragraph: name the thing'
            % (block_name(block), head), block.source)
        return
    if head not in c_SingularPointers + c_PluralPointers:
        return
    rest = first[len(head):]
    following = words[1] if len(words) > 1 else None
    verb = False
    if following is not None and following.kind == 'word':
        key = bare(following).lower()
        if head in c_SingularPointers:
            verb = key in lists.third_forms or key in lists.modals
        else:
            verb = key in lists.base_forms or key in ('are', 'were') or key in lists.modals
    if rest[:1] in (',', ';', ':', '.', '!', '?') or verb or following is None:
        add(words[0].line, 'pronoun-start', 'the %s starts with "%s %s", which points at a noun in another paragraph: name '
            'the thing ("This step…" passes, "This means…" does not)' % (block_name(block), head, following.text if following and not rest else ''),
            block.source)


def block_name(block):
    return {'item': 'list item', 'caption': 'caption'}.get(block.kind, 'paragraph')


def passive(lists, block, sentence, add):
    keys = [bare(word).lower() if word.kind == 'word' else None for word in sentence]
    for index, key in enumerate(keys):
        if key not in c_BeForms or sentence[index].text.lower().strip('"\'(') != key:
            continue
        for other in keys[index + 1:index + 3]:
            if other is None:
                break
            if other.endswith(('ed', 'en')) or other in lists.irregular_pasts:
                add(sentence[index].line, 'passive', '"%s %s" may be the passive voice: say who acts ("Strata stores…")'
                    % (sentence[index].text, ' '.join(word.text for word in sentence[index + 1:index + 1 + keys[index + 1:index + 3].index(other) + 1])),
                    block.source)
                return


def noun_stack(lint, block, words, add):
    lists = lint.words
    names = name_spans(lint, words)
    run = []

    def report():
        if len(run) >= 3:
            add(run[0].line, 'noun-stack', '"%s" may stack nouns: say who does what, with verbs ("Each scene system says '
                'when it runs")' % ' '.join(other.bare for other in run), block.source)

    for index, word in enumerate(words + [None]):
        candidate = False
        punctuated = True
        if word is not None and word.kind == 'word' and not word.bold and index not in names:
            if word.text[:1] in c_OpeningPunctuation:
                report()  # "in a row" means with no punctuation between: "(descriptors" starts a new run
                run = []
            key = word.text.lstrip(c_OpeningPunctuation).lower()
            core = c_TrailingPunctuation.sub('', key)
            candidate = (c_LowerWord.match(core) is not None and core not in lists.function_words
                         and core not in lists.verb_forms and not core.endswith(('ly', 'ing', 'ed')))
            punctuated = core != key
        if candidate:
            run.append(word)
        if not candidate or punctuated:
            report()
            run = []


def copied_text(lint, block, add):
    if block.kind == 'quote':
        return
    words = [(prose.normalize(word.text), word) for word in block.words]
    words = [(key, word) for key, word in words if key]
    keys = [key for key, _ in words]
    for index in range(len(keys) - c_CopiedRun + 1):
        if hash(tuple(keys[index:index + c_CopiedRun])) in lint.sources.runs:
            source = lint.sources.source_of(keys[index:index + c_CopiedRun])
            add(words[index][1].line, 'copied-text', '%d words in a row ("%s…") stand in %s: say it in your own words, or quote '
                'exact words in a block quote that names its source' % (c_CopiedRun, ' '.join(word.text for _, word in words[index:index + 5]), source),
                block.source)
            return


def raw_line_rules(lint, page, add):
    """The spike's rules on the lines of prose: dollar-digit, scope-in-prose, html-in-prose, unfinished,
    deep-heading, block-quote-length, heading-case."""
    for block in page.body.blocks:
        if block.kind in ('paragraph', 'item', 'heading', 'table', 'quote', 'label', 'html'):
            for number, line in block.lines:
                visible = c_Url.sub(lambda match: ' ' * len(match.group(0)), markdown.strip_inline_code(line))
                if block.kind != 'html' and price_like(visible):
                    add(number, 'dollar-digit', '"$" before a digit starts math: "$5 and $10" is read as a formula; write \\$ for a price')
                scope = re.search(r'\S*\w::\w\S*', visible)
                if scope:
                    add(number, 'scope-in-prose', 'write identifiers such as %s in backticks' % scope.group(0))
                if re.search(r'<[A-Za-z/]', re.sub(r'<!--.*?-->', '', visible)) and not visible.lstrip().startswith('<!--'):
                    add(number, 'html-in-prose', 'raw HTML or a template outside backticks: write types such as `Ref<Scene>` in '
                        'backticks, and use the book\'s directives instead of HTML')
                if re.search(r'\b(TODO|FIXME|TBD|XXX)\b', line):
                    add(number, 'unfinished', 'unfinished work is left in the page: finish it or remove the mark')
        if block.kind == 'fence' and 'src' not in block.fence.attributes:
            for offset, line in enumerate(block.fence.body):
                if re.search(r'\b(TODO|FIXME|TBD|XXX)\b', line):
                    add(block.line + 1 + offset, 'unfinished', 'unfinished work is left in the page: finish it or remove the mark')
        if block.kind == 'heading':
            if block.level > 4:
                add(block, 'deep-heading', 'headings go four levels deep at most: split the section instead')
            if any(word.kind == 'math' for word in block.words) or '$' in markdown.strip_inline_code(block.lines[0][1]):
                add(block, 'deep-heading', 'no math in headings: it would become the heading\'s anchor; name the quantity in words')
            heading_case(lint, page, block.words, block.line, add)
        if block.kind == 'quote':
            count = len(block.words)
            if count > c_MaxQuoteWords:
                add(block, 'block-quote-length', 'a block quote of another text holds %d words: quote at most %d and say the rest '
                    'in your own words' % (count, c_MaxQuoteWords))
            if not any(re.match(r'^\s*(\u2014|\u2013|--|Source:)', text) for _, text in block.lines):
                add(block, 'block-quote-length', 'a block quote names its source: end it with a line "— <source>" (a file '
                    'of the engine at the pin, or a page)')
    title = page.data.get('title')
    if isinstance(title, str) and 'title' in page.book_page.values:
        line = page.book_page.values['title'][0]
        heading_case(lint, page, prose.inline_words(title, line), line, add)


def heading_case(lint, page, words, line, add):
    names = name_spans(lint, words)
    capital_terms = lint.glossary.capital_words
    for index, word in enumerate(words):
        if index == 0 or word.kind != 'word' or index in names:
            continue
        text = bare(word)
        if not re.match(r'^[A-Z][a-z]', text) or text in capital_terms or text == 'I':
            continue
        add(line, 'heading-case', '"%s" is capitalized: headings and titles are in sentence case (names, glossary terms '
            'written with capitals and code keep theirs; a name missing from tools/data/names.txt is added there)' % text)


def price_like(text):
    """True when a "$" before a digit opens what would be read as math but looks like money: the formula would end in a
    space ("$5 and $10"), be followed by a digit, or never close on the line."""
    for match in re.finditer(r'(?<!\\)\$(?=\d)', text):
        end = text.find('$', match.end())
        if end < 0 or text[end - 1] == ' ' or text[end + 1:end + 2].isdigit():
            return True
    return False


# Terms (style.md §3).

def taught_before(page, entry):
    """True when the term's home (or use home) is a page of the page's Needs closure: a mark of it may stand there."""
    return entry.get('home') in page.taught or entry.get('use') in page.taught


def unmarked_place(occurrence):
    """True for a use that asks for no mark and is no first use (rulings-11.md, R54): in a block quote (someone else's
    words), in the test-out box (it comes before the page teaches anything), or anywhere in an entry of Further reading
    (a source's title, its authors and what it gives: the entry names the source, it teaches nothing)."""
    block = occurrence.block
    return block.kind == 'quote' or block.inside('test-out') or further_reading_entry(block)


def sentence_of(occurrence):
    """The index of the sentence of the block that holds the use's first word (0 for a block without sentences)."""
    first = occurrence.words[0]
    return next((index for index, sentence in enumerate(occurrence.block.sentences) if any(word is first for word in sentence)), 0)


def defining_sentences(occurrences):
    """(entry id, block id, sentence index) of each sentence that holds a bold use of a term: the page's own definition.
    No use in that sentence asks for a mark (the second pilot: a mark written beside the writer's definition)."""
    return {(occurrence.entry['id'], id(occurrence.block), sentence_of(occurrence)) for occurrence in occurrences
            if occurrence.entry is not None and occurrence.bold and not occurrence.synthetic and occurrence.mark is None}


def adjacent(page, earlier, later):
    """True when a block is the block after another, or the same block: "directly after"."""
    return later is earlier or page.body.next_block(earlier) is later


def first_uses(page, occurrences):
    """The first use of each entry on the page that term-mark reads (entry id -> occurrence, or None for an entry the
    page defines itself), in reading order. A word in bold on a page that is not the term's home is a UI label, not a
    use; but when the term's next use stands in the same block or the one after it, the bold words are the page's own
    definition and that use asks for no mark (R54), and so does a use in the sentence that holds the bold words. Uses of
    unmarked_place are skipped."""
    first = {}
    defining = defining_sentences(occurrences)
    for index, occurrence in enumerate(occurrences):
        entry = occurrence.entry
        if entry is None or entry['id'] in first or unmarked_place(occurrence):
            continue
        if not occurrence.bold and (entry['id'], id(occurrence.block), sentence_of(occurrence)) in defining:
            first[entry['id']] = None  # a use in the sentence of the page's own bold definition: the page defines it
            continue
        if occurrence.bold and not is_home(entry, page.id) and occurrence.mark is None:
            following = next((other for other in occurrences[index + 1:] if other.entry is entry and not unmarked_place(other)), None)
            if following is not None and not following.bold and adjacent(page, occurrence.block, following.block):
                first[entry['id']] = None
            continue
        first[entry['id']] = occurrence
    return first


def sentence_links_home(page, occurrence):
    """True when the sentence of a use (the block, for a table or a title) links the term's home or use home."""
    block, entry = occurrence.block, occurrence.entry
    words = next((sentence for sentence in block.sentences if any(word is occurrence.words[0] for word in sentence)), block.words)
    homes = (entry.get('home'), entry.get('use'))
    return any(word.link and page_checks.link_target(page.id, word.link) in homes for word in words)


def everyday_use(lint, occurrence):
    """An unmarked use of a name that is one word of the common list (rulings-11.md, R53): the word's everyday sense is
    far more frequent than the term's, so the use asks for no mark."""
    return (occurrence.mark is None and len(occurrence.words) == 1 and occurrence.words[0].kind == 'word'
            and lint.words.common_word(occurrence.words[0].plain.lower()))


def needs_mark(lint, page, occurrence):
    """True when the first use of a term whose home is in the page's Needs closure is neither a mark, a link to its
    home, an everyday word nor in a sentence that links its home: what term-mark reports, and what tools/markterms.py
    writes a mark for. A term homed outside the closure asks for nothing (rulings-11.md, R54): the writer says in the
    sentence what it is."""
    entry = occurrence.entry
    if is_home(entry, page.id) or entry.get('known') or occurrence.mark == entry['id'] or not taught_before(page, entry):
        return False
    if everyday_use(lint, occurrence):
        return False
    return not sentence_links_home(page, occurrence)


def unmarked_terms(lint, page, occurrences=None):
    """The first uses that term-mark reports, in reading order."""
    occurrences = term_occurrences(lint, page) if occurrences is None else occurrences
    return [occurrence for occurrence in first_uses(page, occurrences).values()
            if occurrence is not None and needs_mark(lint, page, occurrence)]


def term_rules(lint, page, add, report, occurrences):
    for occurrence in occurrences:
        if occurrence.mark is not None and any(word.link for word in occurrence.words):
            # The site's build refuses it (src/plugins/glossary.mjs): a mark is a link of its own.
            add(occurrence.line, 'term-mark', 'the mark :term[%s]{id=%s} stands inside a link, which the build refuses: '
                'drop the mark and keep the link' % (' '.join(word.text for word in occurrence.words), occurrence.mark),
                occurrence.block.source)
            continue
        if occurrence.entry is None:
            add(occurrence.line, 'term-mark', 'the mark :term[%s]{id=%s} names no glossary entry: use the id of an entry of '
                'src/content/glossary.json, or ask the glossary admitter for the term through the chapter\'s notes'
                % (' '.join(word.text for word in occurrence.words), occurrence.mark), occurrence.block.source)
            continue
        entry = occurrence.entry
        if occurrence.mark == entry['id'] and not is_home(entry, page.id) and not taught_before(page, entry):
            add(occurrence.line, 'term-source', '"%s" is taught on %s, which is not in the Needs closure of %s: drop the '
                'mark and say in the sentence what it is, linking its home where that helps, or ask the planner for the Need'
                % (entry['term'], entry.get('home'), page.id), occurrence.block.source)
    homed = {}  # entry id -> the page's uses of a term it homes, in reading order
    for occurrence in occurrences:
        if occurrence.entry is not None and is_home(occurrence.entry, page.id):
            homed.setdefault(occurrence.entry['id'], []).append(occurrence)
    defined = []
    for entry_id, group in homed.items():
        # The bold definition may stand anywhere on the home page (R54); a use before it is no failure.
        definition = next((occurrence for occurrence in group if occurrence.bold and not occurrence.synthetic), None)
        if definition is not None:
            defined.append(definition)
            continue
        plain = [occurrence for occurrence in group if not (occurrence.block.inside('test-out') or occurrence.block.kind == 'table')]
        where = (plain or group)[0]
        add(where.line, 'term-defined', 'this page is the home of "%s": define it in **bold** somewhere on the page, in one '
            'sentence that says what it is' % where.entry['term'], where.block.source)
    for occurrence in unmarked_terms(lint, page, occurrences):
        entry = occurrence.entry
        add(occurrence.line, 'term-mark', 'the first use of "%s" on the page is not marked: write :term[%s]{id=%s} (or run '
            'tools/markterms.py)' % (entry['term'], ' '.join(word.bare for word in occurrence.words), entry['id']),
            occurrence.block.source)
    for entry in lint.glossary.entries:
        if is_home(entry, page.id) and entry['id'] not in homed and not defined_as_code(page, entry):
            add(1, 'term-defined', 'this page is the home of "%s" but never uses it: define it in **bold** where the page first '
                'needs it' % entry['term'])
    by_block = {}
    by_section = {}
    for occurrence in defined:
        by_block.setdefault(id(occurrence.block), []).append(occurrence)
        by_section.setdefault((occurrence.block.section_line, occurrence.block.section), []).append(occurrence)
    for group in by_block.values():
        if len(group) > 1:
            add(group[1].line, 'term-paragraph', 'this paragraph defines %d new terms (%s): give each new term its own paragraph'
                % (len(group), ', '.join(occurrence.entry['term'] for occurrence in group)))
    report['terms'] = []
    for (line, title), group in sorted(by_section.items(), key=lambda item: item[0][0] or 0):
        report['terms'].append((title or '(before the first section)', line or 1, [occurrence.entry['term'] for occurrence in group]))
        if len(group) > c_MaxNewTerms:
            add(line or 1, 'term-section', 'the section "%s" defines %d new terms, more than %d: split it'
                % (title or 'before the first heading', len(group), c_MaxNewTerms))


# Mathematics (style.md §4).

def tex_symbols(tex):
    """The symbols of a formula: single letters, Greek letters and subscripted symbols ("x_i"), each once."""
    text = tex
    for command in c_TexTextCommands:
        text = re.sub(r'\\%s\s*\{[^{}]*\}' % command, ' ', text)
    for command in c_TexAccents:
        text = re.sub(r'\\%s\s*\{([^{}]*)\}' % command, r' \1 ', text)
        text = re.sub(r'\\%s\s+([A-Za-z])' % command, r' \1 ', text)
    symbols = []
    pattern = re.compile(r'\\([A-Za-z]+)|([A-Za-z])')
    position = 0
    while True:
        match = pattern.search(text, position)
        if not match:
            break
        position = match.end()
        if match.group(1):
            if match.group(1) not in c_Greek:
                continue
            symbol = '\\' + match.group(1)
        else:
            symbol = match.group(2)
        subscript = re.match(r'\s*_\s*(\{[^{}]*\}|\\[A-Za-z]+|[A-Za-z0-9])', text[position:])
        if subscript:
            symbol += '_' + re.sub(r'\s+', '', subscript.group(1).strip('{}'))
            position += subscript.end()
        if symbol not in symbols:
            symbols.append(symbol)
    return symbols


def inline_math(block):
    found = []
    for word in block.words:
        if word.kind == 'math':
            for match in re.finditer(r'\$([^$]+)\$', '$%s$' % word.text if '$' not in word.text else word.text):
                found.extend(tex_symbols(match.group(1)))
            if '$' not in word.text:
                found.extend(tex_symbols(word.text))
    return found


def math_rules(lint, page, add):
    named = set()
    blocks = page.body.blocks
    per_section = {}
    for index, block in enumerate(blocks):
        if block.words and block.kind != 'math':
            named.update(inline_math(block))
            continue
        if block.kind != 'math':
            continue
        tex = '\n'.join(text for _, text in block.lines).strip()
        tex = tex[2:] if tex.startswith('$$') else tex
        tex = tex[:-2] if tex.endswith('$$') else tex
        symbols = [symbol for symbol in tex_symbols(tex) if symbol not in named]
        following = page.body.next_block(block)
        after = set(inline_math(following)) if following is not None and following.kind in ('paragraph', 'item') else set()
        missing = [symbol for symbol in symbols if symbol not in after]
        if missing:
            add(block, 'math-symbols', 'name %s right after the formula, each as inline math with what it is and its unit '
                '("$d$ is the distance, in metres")' % ', '.join('$%s$' % symbol for symbol in missing))
        named.update(symbols)
        if not block.inside('derivation'):
            per_section.setdefault((block.section_line, block.section), []).append(block)
        if 'G' in page.tracks and page.kind != 'primer':
            aside = next((directive for directive in reversed(block.containers)
                          if directive.name == 'derivation' or (directive.name == 'note' and (directive.label or '').strip() == 'The formula')), None)
            if aside is None:
                add(block, 'math-g', 'on a page of track G, a formula stands in a :::note[The formula] aside or a :::derivation '
                    'box, after a paragraph that states its result in words')
            else:
                opening = next(other for other in blocks if other.kind == 'open' and other.directive is aside)
                before = page.body.previous_block(opening)
                if before is None or before.kind not in ('paragraph', 'item'):
                    add(opening, 'math-g', 'the paragraph before the formula\'s aside states its result in words: add it')
    for (line, title), formulas in per_section.items():
        if len(formulas) > c_MaxDerivationFormulas:
            add(line or formulas[0].line, 'math-derivation', 'the section "%s" shows %d display formulas outside a :::derivation '
                'box: put a derivation of more than three steps in one' % (title or 'before the first heading', len(formulas)))


# Code (style.md §9.1).

def fence_numbers(fence):
    """The first and the last line number a fence shows: the engine's lines for a quote, else 1 to its length."""
    match = re.search(r'#L(\d+)-L(\d+)$', fence.attributes.get('src', ''))
    if match:
        return int(match.group(1)), int(match.group(2))
    return 1, max(len(fence.body), 1)


def is_quote(fence):
    return 'src' in fence.attributes and not fence.attributes['src'].startswith('book:')


def code_rules(lint, page, add):
    blocks = page.body.blocks
    short = bool(set(page.tracks) & {'G', 'B'}) or page.level == 1
    feature_homes_seen = set()
    for block in blocks:
        if block.kind != 'fence':
            continue
        fence = block.fence
        if not fence.lang:
            add(block, 'no-language', 'name the fence\'s language (```cpp, ```json, ```text…)')
            continue
        if fence.lang == 'mermaid':
            continue  # a diagram is a figure (style.md §11), not code
        lang = fence.lang.lower()
        if 'src' not in fence.attributes and lang in c_CodeLanguages and 'sketch' not in fence.attributes and 'pseudocode' not in fence.flags:
            add(block, 'unlabelled-code', 'code that is not quoted from the engine is a sketch (sketch="<file>") or pseudocode')
        if is_quote(fence) and fence.body and not c_QuoteLines[0] <= len(fence.body) <= c_QuoteLines[1]:
            add(block, 'long-quote', 'a quote of the engine holds %d to %d lines; this one holds %d: split a long function into '
                'quotes with text between them' % (c_QuoteLines[0], c_QuoteLines[1], len(fence.body)))
        if short and len(fence.body) > c_MaxShortFence:
            add(block, 'long-quote', 'on pages of tracks G and B and on level-1 pages a fence holds at most %d lines; this one '
                'holds %d: show it in parts with text between them' % (c_MaxShortFence, len(fence.body)))
        before = page.body.previous_block(block)
        output_of = fence.attributes.get('output-of')
        after_sketch = (output_of and before is not None and before.kind == 'fence'
                        and before.fence.attributes.get('sketch') == output_of)
        if not after_sketch and (before is None or before.kind not in ('paragraph', 'item')):
            sibling = tab_sibling_has_words(page, block)
            if not sibling:
                add(block, 'code-intro', 'say before the fence, in a paragraph, what the code does and what to look for')
        following = follow_block(page, block)
        if output_of and before is not None and before.kind == 'fence' and before.fence.attributes.get('sketch') == output_of:
            pass  # the sketch's own check looks past its output
        elif following is None or not (following.kind == 'paragraph' or (following.kind == 'item' and following.ordered)):
            if not (following is not None and following.kind == 'fence' and fence.attributes.get('sketch')
                    and following.fence.attributes.get('output-of') == fence.attributes.get('sketch')
                    and follow_ok(follow_block(page, following))):
                add(block, 'code-follow', 'say after the fence what the code showed: a paragraph, or numbered callouts')
        if len(fence.body) >= c_CalloutsFrom and not output_of:
            callout_check(page, block, add)
        if lang in ('cpp', 'c++', 'h', 'hpp') and ('src' in fence.attributes or 'sketch' in fence.attributes):
            cpp_features(lint, page, block, feature_homes_seen, add)


def follow_ok(block):
    return block is not None and (block.kind == 'paragraph' or (block.kind == 'item' and block.ordered))


def follow_block(page, block):
    """The block after a fence; a fence that ends a tab is followed by what follows its tab set."""
    following = page.body.next_block(block)
    while following is not None and following.kind == 'close' and following.directive is not None \
            and following.directive.name in ('tab', 'tabs'):
        following = page.body.next_block(following)
    return following


def tab_sibling_has_words(page, block):
    """True for a fence in a tab whose sibling tab says the same step in words."""
    tab = next((directive for directive in reversed(block.containers) if directive.name == 'tab'), None)
    if tab is None or tab.parent is None or tab.parent.name != 'tabs':
        return False
    for other in page.body.blocks:
        if other.kind in ('paragraph', 'item') and other.containers and other.containers[-1] is not tab \
                and any(directive.name == 'tab' and directive.parent is tab.parent for directive in other.containers):
            return True
    return False


def callout_check(page, block, add):
    following = page.body.next_block(block)
    if following is not None and following.kind == 'fence' and following.fence.attributes.get('output-of') \
            and following.fence.attributes.get('output-of') == block.fence.attributes.get('sketch'):
        following = page.body.next_block(following)
    low, high = fence_numbers(block.fence)
    if following is None or following.kind != 'item' or not following.ordered:
        add(block, 'callouts', 'a fence of %d lines is followed by numbered callouts, 1 to %d items that start with "**Line N:**" '
            'or "**Lines N–M:**" and say why the line is there' % (len(block.fence.body), c_MaxCallouts))
        return
    items = [other for other in page.body.blocks if other.kind == 'item' and other.list_id == following.list_id
             and other.items == following.items]
    if len(items) > c_MaxCallouts:
        add(following, 'callouts', 'callouts are at most %d; this list has %d: point at the lines that carry the idea'
            % (c_MaxCallouts, len(items)))
    for item in items:
        text = re.sub(r'\*\*', '', item.lines[0][1]).strip()
        match = re.match(r'^Lines?\s+(\d+)(?:\s*[\u2013\u2014-]\s*(\d+))?:', text)
        if not match:
            add(item, 'callouts', 'a callout starts with "**Line N:**" or "**Lines N–M:**"')
            continue
        first, last = int(match.group(1)), int(match.group(2) or match.group(1))
        if not (low <= first <= last <= high):
            add(item, 'callouts', 'the callout points at line %s, outside the fence\'s lines %d to %d' % (
                first if first == last else '%d–%d' % (first, last), low, high))


def strip_code_comments(code):
    code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)
    code = re.sub(r'//[^\n]*', '', code)
    code = re.sub(r'R"\((.*?)\)"', '""', code, flags=re.DOTALL)
    return re.sub(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)\'', '""', code)


def cpp_features(lint, page, block, seen, add):
    """One finding per fence that names every untaught feature it uses without a question before it, with the homes
    the question must link (rulings-11.md, R54: one run shows everything)."""
    code = strip_code_comments(block.fence.text)
    missing = []  # (feature, home)
    for feature in lint.words.features:
        home = feature['home']
        if home == page.id or home in page.taught or feature['feature'] in seen:
            continue
        if not any(pattern.search(code) for pattern in feature['compiled']):
            continue
        seen.add(feature['feature'])
        if not question_before(page, block, home):
            missing.append((feature['feature'], home))
    if missing:
        homes = []
        for _, home in missing:
            if home not in homes:
                homes.append(home)
        add(block, 'cpp-feature', 'the code uses %s, which this page\'s Needs closure does not teach: put a :::question aside '
            'before this fence, at most two sentences, that links %s' % (
                '; '.join('%s (%s)' % pair for pair in missing), ', '.join('../%s.md' % home for home in homes)))


def question_before(page, block, home):
    for directive in page.body.directives:
        if directive.name != 'question' or directive.line >= block.line:
            continue
        for other in page.body.blocks:
            if other.containers and directive in other.containers:
                for word in other.words:
                    if word.link and page_checks.link_target(page.id, word.link) == home:
                        return True
    return False


# Questions, steps and asides (style.md §8, §10, §12).

def top_items(page, section_titles, ordered=True):
    return [block for block in page.body.blocks if block.kind == 'item' and block.ordered == ordered and not block.items
            and block.section in section_titles and not block.containers]


def item_extent(page, item):
    return [item] + [block for block in page.body.blocks if item in block.items]


def structure_rules(lint, page, add):
    # exercise-order
    for title in c_ExerciseSections:
        levels = []
        for item in top_items(page, (title,)):
            first = next((word for word in item.words), None)
            level = first.text if first is not None and first.bold and first.text in c_ExerciseLevels else None
            if level is None:
                add(item, 'exercise-order', 'an exercise starts with its level in bold: **Basic.**, **Medium.** or **Hard.**')
                continue
            if levels and c_ExerciseLevels.index(level) < c_ExerciseLevels.index(levels[-1]):
                add(item, 'exercise-order', 'the exercises go from easy to hard: %s comes after %s' % (level, levels[-1]))
            levels.append(level)
    # step-parts
    if page.kind == 'tutorial' or (page.kind == 'how-to' and set(page.tracks) & {'G', 'B'}):
        titles = [block.section for block in page.body.blocks if block.kind == 'heading' and block.level == 2 and not block.containers]
        strip = page_checks.c_Strips.get(page.kind, [])
        if page.kind == 'tutorial':
            start = titles.index('What you need') + 1 if 'What you need' in titles else 0
            end = next((index for index, title in enumerate(titles) if title in strip and index >= start), len(titles))
            steps = set(titles[start:end])
        else:
            end = titles.index('Result') if 'Result' in titles else len(titles)
            steps = set(titles[:end]) | {None}
        for item in page.body.blocks:
            if item.kind != 'item' or not item.ordered or item.items or item.section not in steps:
                continue
            if item.containers and item.containers[-1].name != 'steps':
                continue
            lead = re.sub(r'\*\*', '', item.lines[0][1]).strip()
            if re.match(r'^Lines?\s+\d', lead):
                continue  # callouts of a fence
            text = '\n'.join(line for block in item_extent(page, item) for _, line in block.lines)
            missing = [part for part in (c_StepSee, c_StepUnseen) if part not in text]
            if missing:
                add(item, 'step-parts', 'every step states what the reader should see and what to do when it does not happen: '
                    'add %s' % ' and '.join(missing))
    # simplified-link and analogy-limit
    for directive in page.body.directives:
        inner = [block for block in page.body.blocks if directive in block.containers and block.kind in ('paragraph', 'item')]
        if directive.name == 'simplified' and not any(word.link for block in inner for word in block.words):
            add(directive.line, 'simplified-link', 'a :::simplified aside links the page with the full story')
        if directive.name == 'analogy':
            own = [block for block in inner if block.containers[-1] is directive and block.kind == 'paragraph']
            if not own or not own[-1].lines[0][1].strip().startswith('**Where it breaks:**'):
                add(directive.line, 'analogy-limit', 'the last paragraph of an :::analogy aside starts with **Where it breaks:** and '
                    'says where the analogy stops being true')


def number_rules(lint, page, add):
    w8r = page.row is not None and page.row.mark == 'W8r'
    g_page = 'G' in page.tracks
    if not (w8r or g_page):
        return
    for block in page.blocks(kinds=('paragraph', 'item', 'caption', 'quote')):
        for sentence in block.sentences:
            texts = [word.text for word in sentence if word.kind == 'word']
            if g_page:
                has_ms = any((c_Number.match(word.bare) and index + 1 < len(sentence) and sentence[index + 1].kind == 'word'
                              and sentence[index + 1].bare == 'ms') or re.match(r'^\d+([.,]\d+)?ms$', word.bare)
                             for index, word in enumerate(sentence) if word.kind == 'word')
                if has_ms and not any('%' in text for text in texts):
                    add(sentence[0].line, 'g-frame-share', 'on a page of track G a time in ms also gives its share of a frame at 60 '
                        'frames per second ("2.1 ms, 13 % of a frame at 60 frames per second") and says that a slower GPU takes '
                        'longer', block.source)
            if w8r:
                preset = any(word.kind == 'word' and word.bare in c_Presets for word in sentence)
                number = any(re.search(r'\d', word.text) for word in sentence if word.kind in ('word', 'math'))
                if preset and number:
                    add(sentence[0].line, 'w8r-preset', 'pages marked W8r state no preset value in prose: take the value from '
                        'the generated reference tables', block.source)


# Size, time and the reading report.

def measure_rules(lint, page, add, report):
    words = sum(len(block.words) for block in page.blocks())
    code_lines = sum(len(block.fence.body) for block in page.body.blocks if block.kind == 'fence' and block.fence.lang != 'mermaid')
    report['words'] = words
    report['code lines'] = code_lines
    size = page.data.get('size')
    # rulings-8.md, R37: a page of kind reference always fits (its tables are as long as the engine makes them).
    if size in c_Sizes and page.kind != 'reference':
        low, high = c_Sizes[size]
        if not low <= words <= high:
            add(1, 'size', 'the page has %d prose words; size %s holds %s to %s: cut the page, or ask the planner to change the '
                'outline\'s size' % (words, size, format(low, ','), format(high, ',')))
    time = page.data.get('time')
    floor = math.ceil((words / c_ReadingSpeed + code_lines / c_CodeSpeed) / 5) * 5
    report['floor'] = floor
    if isinstance(time, int) and not isinstance(time, bool) and page.kind != 'reference':
        line = page.book_page.values.get('time', (1,))[0]
        if time < floor:
            add(line, 'time', 'time: %d is below the reading floor of %d minutes (%d prose words / %d + %d lines of code / %d, '
                'rounded up to 5): write time: %d or more' % (time, floor, words, c_ReadingSpeed, code_lines, c_CodeSpeed, floor))
        elif page.kind in ('concept', 'internals') and time > 2 * floor:
            add(line, 'time', 'time: %d is more than twice the reading floor of %d minutes: write at most %d' % (time, floor, 2 * floor))
    prose_runs(page, add)


def prose_runs(page, add):
    run, start = 0, None
    for block in page.body.blocks + [None]:
        if block is not None and block.kind == 'paragraph' and not block.items:
            if start is None:
                start = block
            run += len(block.words)
            continue
        if block is not None and block.kind in ('html',):
            continue
        if run > c_MaxRun:
            add(start, 'prose-run', '%d words of prose come without a break: add a heading, a figure, a list, a table or an '
                'example (at most %d)' % (run, c_MaxRun))
        run, start = 0, None


def words_line(words, size):
    """The prose words of a page beside its size's range, as the lint prints them for named pages and
    tools/pagecheck.py shows them in every run (rulings-11.md, R54)."""
    if size in c_Sizes:
        low, high = c_Sizes[size]
        return 'words: %d prose words; size %s holds %s to %s' % (words, size, format(low, ','), format(high, ','))
    return 'words: %d prose words; the page has no size of S, M, L or XL' % words


def write_report(folder, page, report, findings):
    path = os.path.join(folder, *(page.id + '.txt').split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ['Reading report of %s (%s)' % (page.id, page.file), '']
    size = page.data.get('size')
    lines.append('Words: %d%s' % (report.get('words', 0), (' (size %s: %s to %s)' % (size, format(c_Sizes[size][0], ','), format(c_Sizes[size][1], ',')))
                                  if size in c_Sizes else ''))
    lines.append('Lines of code shown: %d; reading floor: %d minutes; time: %s' % (report.get('code lines', 0), report.get('floor', 0), page.data.get('time', '-')))
    longest = report.get('longest', (0, 0))
    lines.append('Sentences: %d; mean %.1f words; longest %d words (line %d)' % (report.get('sentences', 0), report.get('mean', 0.0), longest[0], longest[1]))
    over = report.get('paragraphs over', [])
    lines.append('Paragraphs over %d sentences: %s' % (c_MaxParagraph, ', '.join('line %d (%d)' % pair for pair in over) or 'none'))
    lines.append('New terms per section:')
    for title, line, terms in report.get('terms', []):
        lines.append('  %s (line %d): %s' % (title, line, ', '.join(terms)))
    if not report.get('terms'):
        lines.append('  none')
    unknown = report.get('unknown', [])
    lines.append('Words outside the lists (%d): %s' % (len(unknown), ', '.join('%s (line %d%s)' % (word, line, ', %d uses' % count if count > 1 else '')
                                                                            for word, line, count in unknown) or 'none'))
    warnings = [finding for finding in findings if finding.warning]
    lines.append('Warnings (%d):' % len(warnings))
    lines.extend('  %s' % finding for finding in warnings)
    failures = [finding for finding in findings if not finding.warning]
    lines.append('Failing rules (%d):' % len(failures))
    lines.extend('  %s' % finding for finding in failures)
    repo.write_text(path, '\n'.join(lines) + '\n')


def rules_text():
    width = max(len(rule) for rule in c_RuleIds) + 10
    return '\n'.join('  %s%s (%s)' % (('%s%s' % (rule, ' (warning)' if warning else '')).ljust(width), text, where)
                     for rule, where, warning, text in c_Rules)


def main(argv=None, book=outline_rules.c_Book):
    repo.utf8_output()
    parser = argparse.ArgumentParser(
        description='The book\'s language lint: every rule id of plan/style.md, the site\'s inline-env and '
                    'front-matter-head, and literal-origin (rulings 6, R24).',
        epilog=__doc__.split('\n\n', 1)[1] + '\nRules:\n' + rules_text(),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('pages', nargs='*', help='page ids (default: every page)')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: the STRATA_ENGINE variable)')
    parser.add_argument('--plan', help='the plan folder (default: <root>/plan)')
    parser.add_argument('--glossary', help='the glossary (default: src/content/glossary.json)')
    parser.add_argument('--report', help='a folder for one reading report per page')
    options = parser.parse_args(argv)
    try:
        lint = Lint(repo.Layout(options.root), options.engine, plan=options.plan, book=book, glossary=options.glossary)
        findings = lint.run(options.pages, options.report)
        for note in lint.notes:
            print('lint: note: %s' % note, file=sys.stderr)
    except LintError as error:
        print('lint: %s' % error, file=sys.stderr)
        return 2
    except OSError as error:
        print('lint: %s' % error, file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    if options.pages:
        for file, words, size in lint.measured:
            print('%s: %s' % (file, words_line(words, size)))
    failures = sum(1 for finding in findings if not finding.warning)
    print('lint: %d failing, %d warning%s' % (failures, len(findings) - failures, '' if len(findings) - failures == 1 else 's'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
