#!/usr/bin/env python3
"""The third-party notices (plan/pipelines.md §15; plan/site.md, "The copyright statement and the notices"; rulings 6,
R22 and R26): public/third-party-notices.txt, which the site serves as <base>/third-party-notices.txt and links from
the footer of every page.

    python -I tools/notices.py write --engine <clone>
    python -I tools/notices.py check --engine <clone> [--dist <built site>]
    python -I tools/notices.py check --sections A [--dist <built site>]
    python -I tools/notices.py check --sections BC --engine <clone>

The file has three sections and the license texts:
  A  What this site ships: every component of tools/data/notices.json (kept by hand: per component its package and
     version, its license id, its copyright lines, the license file in node_modules and the files of the built site
     that are its), each license's text read from node_modules. The versions are checked against package-lock.json.
  B  What this book quotes: every vendored library a page quotes with vendor:<lib>, with the version and license
     ThirdPartyNotices.md records at the pin and the license file of the library's submodule at the commit the pin
     records for it; and every project of ThirdPartyNotices.md's "Code derived from other projects" whose files a page
     quotes, with the license text that ThirdPartyNotices.md gives for it.
  C  What this book shows and gives out: the CREDITS.md at the pin of every sample that a figure recipe or a tutorial
     uses, labs/CREDITS.md and tutorials/assets/CREDITS.md when they exist, and the full credits that notices.json keeps
     for files whose own credit at the pin is incomplete (the fox of Open World, rulings 6, R22).

write   writes the file. It needs both node_modules and the engine (--engine), and refuses (exit 1, nothing written)
        while check would fail on the list.
check   fails (exit 1) when the committed file differs from what write writes; when a component of the list has
        another version in package-lock.json than the list records, so that a person reads every upgrade; when a
        component's license is outside the allowlist (MIT, MIT-0, ISC, 0BSD, BSD-2-Clause, BSD-3-Clause, Apache-2.0,
        OFL-1.1, CC0-1.0, BlueOak-1.0.0, Unicode-3.0, Zlib); when a copyright line of the list is not in the file it
        is said to come from. With --dist, after a build, it also fails when the built site holds a font file, a
        script or a WebAssembly file that no component of the list (or the list's "own" files, the site's own code)
        claims. --sections names what one job can check (R26): A reads package-lock.json and node_modules and no
        engine; BC reads the engine and no node_modules; each compares only those sections of the committed file and
        the license texts they name. Without --sections, check covers the whole file.

Each license text appears once: a text is the license file without its copyright lines (each entry states its own),
and it is named by the first 8 hex digits of its SHA-256, so a text keeps its name whatever else changes.

Exit codes: 0 current, 1 problems, 2 something the asked sections read is missing (the pin that --engine must resolve,
a submodule's checkout, package-lock.json, node_modules or the --dist folder) or a usage error.
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from booklib import repo  # noqa: E402
import excerpts  # noqa: E402

c_Output = 'public/third-party-notices.txt'
c_List = 'tools/data/notices.json'
c_Allowed = ('MIT', 'MIT-0', 'ISC', '0BSD', 'BSD-2-Clause', 'BSD-3-Clause', 'Apache-2.0', 'OFL-1.1', 'CC0-1.0',
             'BlueOak-1.0.0', 'Unicode-3.0', 'Zlib')
c_Titles = {'A': 'What this site ships', 'B': 'What this book quotes', 'C': 'What this book shows and gives out'}
c_Texts = 'License texts'
c_SectionLine = re.compile(r'^==== (?:(?P<letter>[ABC])\. .*|' + c_Texts + ') ====$')
c_TextLine = re.compile(r'^---- text (?P<id>[0-9a-f]{8}): .* ----$')
c_TextReference = re.compile(r'\(text ([0-9a-f]{8})\)')
c_CopyrightLine = re.compile(r'^\s*(copyright\b|\(c\)|©)', re.IGNORECASE)
c_LicenseName = re.compile(r'^(licen[cs]e|copying|unlicense)([.-][\w.-]*)?$', re.IGNORECASE)
c_FontFiles = ('.woff2', '.woff', '.ttf', '.otf', '.eot')
c_ScriptFiles = ('.js', '.mjs', '.cjs')
c_Width = 120
c_Derived = '## Code derived from other projects'

c_Header = """Third-party notices of the Strata Engine Book

Written by python -I tools/notices.py write; do not edit. The book itself is all rights reserved (license.txt); this
file names the work of others that the site ships, that the book quotes and that it shows and gives out, each with its
license and its copyright lines as its own notice states them.

The layout: three sections, each starting with a line "==== <letter>. <title> ====", then the license texts, starting
with the line "==== License texts ====". Each license text starts with a line "---- text <name>: <license> ----", and
an entry names the text it is under with "(text <name>)". A text is the license file without its copyright lines
(the entry states them), and its name is the first 8 hex digits of the SHA-256 of the text.
"""


class Missing(Exception):
    """Something the asked sections read is missing: exit 2."""


class Notices:
    def __init__(self):
        self.problems = []
        self.texts = {}  # name: (license id, text)

    def problem(self, message):
        self.problems.append(message)

    def text(self, license_id, raw, omit=()):
        """The name of the license text that raw holds, without its copyright lines and the lines omit names."""
        lines = [line.rstrip() for line in raw.replace('\r\n', '\n').split('\n')]
        kept = [line for line in lines if not c_CopyrightLine.match(line) and line.strip() not in omit]
        body = re.sub(r'\n{3,}', '\n\n', '\n'.join(kept)).strip('\n') + '\n'
        name = hashlib.sha256(body.encode('utf-8')).hexdigest()[:8]
        self.texts.setdefault(name, (license_id, body))
        return name


def entry(text):
    """One line of an entry, indented and wrapped at the file's width."""
    return textwrap.wrap(text, c_Width, initial_indent='  ', subsequent_indent='    ', break_long_words=False, break_on_hyphens=False)


def copyright_lines(text):
    found = []
    for line in text.replace('\r\n', '\n').split('\n'):
        stripped = line.strip()
        if c_CopyrightLine.match(stripped) and stripped not in found:
            found.append(stripped)
    return found


def read_json(path):
    with open(path, encoding='utf-8') as file:
        return json.load(file)


# Section A ----------------------------------------------------------------------------------------------------------

def read_list(layout):
    path = os.path.join(layout.root, *c_List.split('/'))
    try:
        data = read_json(path)
    except FileNotFoundError:
        raise Missing('%s does not exist: it lists what the site ships (plan/pipelines.md §15)' % c_List)
    except ValueError as error:
        raise Missing('%s is not valid JSON: %s' % (c_List, error))
    if not isinstance(data, dict) or not isinstance(data.get('components'), list):
        raise Missing('%s holds {"components": [...], "own": {...}, "shows": [...]}' % c_List)
    return data


def read_lock(layout):
    path = os.path.join(layout.root, 'package-lock.json')
    if not os.path.isfile(path):
        raise Missing('package-lock.json does not exist: section A checks the versions against it')
    if not os.path.isdir(os.path.join(layout.root, 'node_modules')):
        raise Missing('node_modules does not exist: run npm ci (section A reads the license texts from it)')
    try:
        return read_json(path).get('packages') or {}
    except ValueError as error:
        raise Missing('package-lock.json is not valid JSON: %s' % error)


def package_text(layout, relative):
    """The text of a file under node_modules, or None."""
    path = os.path.join(layout.root, 'node_modules', *relative.split('/'))
    return repo.read_text(path) if os.path.isfile(path) else None


def section_a(layout, notices, data, lock):
    lines = []
    for index, component in enumerate(data['components']):
        where = '%s: components[%d]' % (c_List, index)
        try:
            name, package, version, license_id = (component[key] for key in ('name', 'package', 'version', 'license'))
            copyright_list, license_file = component['copyright'], component['licenseFile']
        except (KeyError, TypeError):
            notices.problem('%s: give name, package, version, license, copyright and licenseFile' % where)
            continue
        packages = dict(component.get('packages') or {})
        packages[package] = version
        for each, wanted in sorted(packages.items()):
            locked = (lock.get('node_modules/' + each) or {}).get('version')
            if locked is None:
                notices.problem('%s (%s): package-lock.json has no package %s: correct the list, or run npm install' % (where, name, each))
            elif locked != wanted:
                notices.problem('%s (%s): the list records %s %s, and package-lock.json has %s: read the new version\'s '
                                'license and copyright lines, then record %s' % (where, name, each, wanted, locked, locked))
        if license_id not in c_Allowed:
            notices.problem('%s (%s): the license %s is outside the allowlist of rulings 6, R22 (%s)' % (where, name, license_id, ', '.join(c_Allowed)))
        text = package_text(layout, license_file)
        if text is None:
            notices.problem('%s (%s): node_modules/%s does not exist: name the license file the package ships' % (where, name, license_file))
            continue
        if component.get('licenseUntil'):
            if component['licenseUntil'] not in text:
                notices.problem('%s (%s): licenseUntil "%s" is not a line of node_modules/%s' % (where, name, component['licenseUntil'], license_file))
            text = text.split(component['licenseUntil'], 1)[0]
        source = component.get('copyrightFrom')
        source_text = text
        if source and '/' in source and ' ' not in source:
            source_text = package_text(layout, source)
            if source_text is None:
                notices.problem('%s (%s): copyrightFrom names node_modules/%s, which does not exist' % (where, name, source))
                source_text = ''
        elif source:
            source_text = None  # a sentence: where the lines stand, read by a person
        for line in copyright_list:
            if source_text is not None and line not in source_text:
                notices.problem('%s (%s): the copyright line "%s" is not in node_modules/%s: copy it as the notice writes it'
                                % (where, name, line, source or license_file))
        text_name = notices.text(license_id, text, component.get('omit') or ())
        lines.append(name)
        lines += entry('Package: %s' % ', '.join('%s %s' % pair for pair in [(package, version)] + sorted(
            (each, wanted) for each, wanted in packages.items() if each != package)))
        lines += entry('License: %s (text %s)' % (license_id, text_name))
        lines.extend('  %s' % line for line in copyright_list)
        if source and source_text is None:
            lines += entry('Where the copyright lines stand: %s.' % source)
        if component.get('files'):
            lines += entry('In the site: %s' % ', '.join(component['files']))
        lines.append('')
    return lines


def dist_problems(layout, data, dist):
    """The font, script and WebAssembly files of the built site that no component claims."""
    if not os.path.isdir(dist):
        raise Missing('--dist %s is no folder: build the site first' % dist)
    patterns = [pattern for component in data['components'] for pattern in component.get('files') or []]
    patterns += list((data.get('own') or {}).get('files') or [])
    problems = []
    for folder, directories, files in os.walk(dist):
        directories.sort()
        for name in sorted(files):
            relative = os.path.relpath(os.path.join(folder, name), dist).replace(os.sep, '/')
            lowered = name.lower()
            kind = ('font' if lowered.endswith(c_FontFiles) else 'script' if lowered.endswith(c_ScriptFiles)
                    else 'WebAssembly file' if lowered.endswith('.wasm') or (lowered.startswith('wasm.') and lowered.endswith('.pagefind'))
                    else None)
            if kind and not any(fnmatch.fnmatchcase(relative, pattern) for pattern in patterns):
                problems.append('%s: the built site holds the %s %s, which no component of %s claims: add it to the files of '
                                'its component (or a new component with its license), or to "own" when it is the site\'s own code'
                                % (dist.replace('\\', '/'), kind, relative, c_List))
    return problems


# Sections B and C ---------------------------------------------------------------------------------------------------

def quoted_sources(layout):
    """(vendored libraries quoted, engine paths quoted) over every page."""
    libraries, paths = set(), set()
    for _, path in layout.pages():
        for _, source in excerpts.quotes(repo.read_text(path)):
            if isinstance(source, excerpts.Source):
                if source.namespace == 'vendor':
                    libraries.add(source.lib)
                elif source.namespace == 'engine':
                    paths.add(source.path)
    return libraries, paths


def derived_projects(engine, pin, lines):
    """[(name, url, version, license, files, license text)] of ThirdPartyNotices.md's "Code derived from other projects"."""
    if c_Derived not in lines:
        return []
    section = lines[lines.index(c_Derived) + 1:]
    section = section[:next((index for index, line in enumerate(section) if line.startswith('## ')), len(section))]
    top = set(engine.tree(pin) or {})
    projects = []
    for line in section:
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')] if line.startswith('| [') else []
        link = re.match(r'^\[([^\]]+)\]\((https?://[^)]+)\)', cells[0]) if len(cells) >= 4 else None
        if not link:
            continue
        files, folder = [], ''
        for entry in re.findall(r'`([^`]+)`', cells[3]):
            if entry.split('/', 1)[0] in top:
                path = entry
            else:
                path = None
                base = folder
                while path is None:
                    candidate = (base + '/' + entry) if base else entry
                    if engine.exists(pin, candidate) or not base:
                        path = candidate
                    base = base.rpartition('/')[0]
            files.append(path)
            folder = path.rpartition('/')[0]
        text = license_block(section, link.group(1))
        projects.append((link.group(1), link.group(2), cells[1], cells[2], files, text))
    return projects


def license_block(section, name):
    """The fenced text below the line "<name>:" of the section, or None."""
    for index, line in enumerate(section):
        if line.strip() == name + ':':
            rest = section[index + 1:]
            starts = [number for number, text in enumerate(rest) if text.startswith('```')]
            if len(starts) >= 2:
                return '\n'.join(rest[starts[0] + 1:starts[1]])
    return None


def section_b(layout, notices, engine, pin):
    lines = []
    vendors = excerpts.Vendors(engine, pin)
    libraries, paths = quoted_sources(layout)
    for lib in sorted(libraries):
        record = vendors.record(lib)
        if record is None:
            notices.problem('vendor:%s: ThirdPartyNotices.md at the pin does not list the library, so its notice cannot be '
                            'written: quote a library the engine lists (plan/pipelines.md §3.2)' % lib)
            continue
        folder = 'Strata/vendor/' + lib
        try:
            library = engine.submodule(folder)
            commit = library.resolve(record['commit'])
        except repo.EngineError as error:
            raise Missing('%s: %s (run git submodule update --init in the clone)' % (folder, error))
        names = sorted(name for name, (mode, _) in (library.tree(commit) or {}).items() if mode != '040000' and c_LicenseName.match(name))
        if not names:
            notices.problem('vendor:%s: the library has no license file (LICENSE, COPYING...) at %s: its notice cannot be written'
                            % (lib, commit[:12]))
            continue
        lines.append('%s (vendor:%s)' % (record['name'], lib))
        lines += entry('Version: %s, commit %s of %s (%s at the pin)' % (record['version'], record['commit'], record['repository'], folder))
        for name in names:
            text = '\n'.join(library.read(commit, name) or [])
            lines.append('  License: %s (text %s; the file %s)' % (record['license'], notices.text(record['license'], text), name))
            lines.extend('  %s' % line for line in copyright_lines(text))
        lines.append('')
    notice_lines = engine.read(pin, 'ThirdPartyNotices.md') or []
    for name, url, version, license_id, files, text in derived_projects(engine, pin, notice_lines):
        quoted = [path for path in files if path in paths]
        if not quoted:
            continue
        if text is None:
            notices.problem('ThirdPartyNotices.md: the project %s has no license text below its table ("%s:" and a fence), so its '
                            'notice cannot be written' % (name, name))
            continue
        lines.append(name)
        lines += entry('Code derived from it that the book quotes: %s' % ', '.join(quoted))
        lines += entry('Version: %s, %s' % (version, url))
        lines += entry('License: %s (text %s)' % (license_id, notices.text(license_id, text)))
        lines.extend('  %s' % line for line in copyright_lines(text))
        lines.append('')
    return lines


def used_samples(layout):
    """{sample folder: the first book file that uses it}: figure recipes and tutorials."""
    found = {}

    def walk(value, relative):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'sample' and isinstance(item, str):
                    found.setdefault(item, relative)
                walk(item, relative)
        elif isinstance(value, list):
            for item in value:
                walk(item, relative)
        elif isinstance(value, str):
            match = re.match(r'^Samples/([A-Za-z0-9_-]+)/', value)
            if match:
                found.setdefault(match.group(1), relative)

    for top, suffix in ((layout.figures, '.json'), (layout.tutorials, '.tutorial.json')):
        for folder, directories, files in os.walk(top):
            directories.sort()
            for name in sorted(files):
                if name.endswith(suffix):
                    path = os.path.join(folder, name)
                    try:
                        walk(read_json(path), layout.relative(path))
                    except ValueError:
                        continue  # figures.py and tutorials.py report a file that is not JSON
    return found


def indented(text):
    return ['    ' + line if line.strip() else '' for line in text.rstrip('\n').split('\n')]


def section_c(layout, notices, data, engine, pin):
    lines = []
    for sample, user in sorted(used_samples(layout).items()):
        path = 'Samples/%s/CREDITS.md' % sample
        text = engine.read(pin, path)
        if text is None:
            notices.problem('%s uses the sample %s, which has no %s at the pin: its assets cannot be credited' % (user, sample, path))
            continue
        lines += textwrap.wrap('%s at the engine\'s commit %s (used by %s and other files of the book):' % (path, pin, user), c_Width,
                               break_long_words=False, break_on_hyphens=False)
        lines.append('')
        lines.extend(indented('\n'.join(text)))
        lines.append('')
    for relative in ('labs/CREDITS.md', 'tutorials/assets/CREDITS.md'):
        path = os.path.join(layout.root, *relative.split('/'))
        if os.path.isfile(path):
            lines.append('%s of the book:' % relative)
            lines.append('')
            lines.extend(indented(repo.read_text(path)))
            lines.append('')
    for index, item in enumerate(data.get('shows') or []):
        try:
            lines.append(item['name'])
            lines += entry('License: %s' % item['license'])
            lines.extend('  %s' % line for line in item['copyright'])
            lines += entry('Source: %s' % item['source'])
            if item.get('note'):
                lines += entry(item['note'])
            lines.append('')
        except (KeyError, TypeError):
            notices.problem('%s: shows[%d]: give name, license, copyright, source and optionally note' % (c_List, index))
    return lines


# The file -----------------------------------------------------------------------------------------------------------

def build(layout, sections, engine_path, dist=None):
    """(notices, {letter: lines}, problems of dist). Missing when something the sections read is missing."""
    notices = Notices()
    data = read_list(layout)
    blocks = {}
    dist_found = []
    if 'A' in sections:
        lock = read_lock(layout)
        blocks['A'] = section_a(layout, notices, data, lock)
        if dist:
            dist_found = dist_problems(layout, data, dist)
    if 'B' in sections or 'C' in sections:
        try:
            engine = repo.Engine(engine_path)
            pin = engine.resolve(repo.read_pin(layout.pin_file)['commit'])
        except (repo.EngineError, OSError, ValueError) as error:
            raise Missing(str(error))
        try:
            if 'B' in sections:
                blocks['B'] = section_b(layout, notices, engine, pin)
            if 'C' in sections:
                blocks['C'] = section_c(layout, notices, data, engine, pin)
        except repo.EngineError as error:
            raise Missing(str(error))
        finally:
            engine.close()
    return notices, blocks, dist_found


def section_text(letter, lines):
    body = '\n'.join(lines).rstrip('\n')
    return '==== %s. %s ====\n\n%s\n' % (letter, c_Titles[letter], body if body else '(nothing)')


def text_block(notices, name):
    license_id, body = notices.texts[name]
    return '---- text %s: %s ----\n\n%s' % (name, license_id, body)


def file_text(notices, blocks):
    parts = [c_Header] + [section_text(letter, blocks[letter]) for letter in 'ABC']
    parts.append('==== %s ====\n' % c_Texts)
    parts += [text_block(notices, name) for name in sorted(notices.texts)]
    return '\n'.join(parts)


def split_file(text):
    """{letter: section text, ('text', name): text block}, from a committed file."""
    found = {}
    key, current = None, []

    def close():
        if key is not None:
            found[key] = '\n'.join(current).rstrip('\n') + '\n'

    for line in text.split('\n'):
        section = c_SectionLine.match(line)
        block = c_TextLine.match(line)
        if section or block:
            close()
            key = section.group('letter') if section else ('text', block.group('id'))
            current = [line]
            if section and not section.group('letter'):
                close()
                key, current = None, []
        elif key is not None:
            current.append(line)
    close()
    return found


def compare(layout, notices, blocks, sections):
    """Messages where the committed file differs from what write writes, for the asked sections."""
    path = os.path.join(layout.root, *c_Output.split('/'))
    if not os.path.isfile(path):
        return ['%s does not exist: run python -I tools/notices.py write --engine <clone>' % c_Output]
    committed = repo.read_text(path)
    if sections == 'ABC':
        expected = file_text(notices, blocks)
        if committed == expected:
            return []
        old, new = committed.split('\n'), expected.split('\n')
        line = next((number for number, (a, b) in enumerate(zip(old, new), 1) if a != b), min(len(old), len(new)) + 1)
        return ['%s:%d: the file is not what write writes: run python -I tools/notices.py write --engine <clone>' % (c_Output, line)]
    parts = split_file(committed)
    messages = []
    for letter in sections:
        expected = section_text(letter, blocks[letter])
        if parts.get(letter) != expected:
            messages.append('%s: section %s (%s) is not what write writes: run python -I tools/notices.py write --engine <clone>'
                            % (c_Output, letter, c_Titles[letter]))
        for name in sorted(set(c_TextReference.findall(expected))):
            block = text_block(notices, name).rstrip('\n') + '\n'
            if parts.get(('text', name)) != block:
                messages.append('%s: the license text %s that section %s names is %s: run python -I tools/notices.py write '
                                '--engine <clone>' % (c_Output, name, letter, 'missing' if ('text', name) not in parts else 'not what write writes'))
    return messages


def main(argv=None):
    repo.utf8_output()
    parser = argparse.ArgumentParser(description='Writes and checks the third-party notices (plan/pipelines.md §15).',
                                     epilog=__doc__.split('\n\n', 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', choices=['write', 'check'])
    parser.add_argument('--engine', default=repo.c_DefaultEngine, help='the pin clone (default: $STRATA_ENGINE)')
    parser.add_argument('--sections', help='check: A, BC or ABC (default: the whole file)')
    parser.add_argument('--dist', help='check: the built site, whose fonts, scripts and WebAssembly files the list must claim')
    parser.add_argument('--root', help='the book\'s folder (default: this repository)')
    options = parser.parse_args(argv)
    sections = ''.join(letter for letter in 'ABC' if letter in (options.sections or 'ABC').upper())
    if options.sections and (not sections or set(options.sections.upper()) - set('ABC')):
        print('notices: --sections takes the letters A, B and C, such as A or BC', file=sys.stderr)
        return 2
    if options.command == 'write' and (options.sections or options.dist):
        print('notices: write writes the whole file: give it --engine only', file=sys.stderr)
        return 2
    if options.dist and 'A' not in sections:
        print('notices: --dist checks what the site ships: give it with section A', file=sys.stderr)
        return 2
    layout = repo.Layout(options.root)
    try:
        notices, blocks, dist_found = build(layout, sections, options.engine, os.path.abspath(options.dist) if options.dist else None)
    except Missing as error:
        print('notices: %s' % error, file=sys.stderr)
        return 2
    problems = notices.problems + dist_found
    if options.command == 'write':
        for message in problems:
            print(message)
        if problems:
            print('notices: %d problems: nothing written; correct %s or the book first' % (len(problems), c_List))
            return 1
        path = os.path.join(layout.root, *c_Output.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        repo.write_text(path, file_text(notices, blocks))
        print('notices: wrote %s (%d license texts)' % (c_Output, len(notices.texts)))
        return 0
    problems += compare(layout, notices, blocks, sections)
    for message in problems:
        print(message)
    print('notices: %s (sections %s)' % ('%d problems' % len(problems) if problems else 'current', sections))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
