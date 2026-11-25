"""The prose of a page as plan/style.md §2.2 defines it, read into blocks, words and sentences with the file's line
numbers, for tools/lint.py.

- **Prose** is the visible text: paragraphs, list items, headings, table cells, block quotes, asides and answers (with
  the titles of containers, such as `:::note[The formula]`), and the captions and alternative texts of the page's
  figures. Front matter, code fences, display math (`$$`) and HTML comments are not prose; a fence is a block of its
  own, and so is a display formula.
- A **word** is a run of characters between spaces. An inline code span and an inline formula each count as one word
  (with what touches them: "`Scene`'s" is one word). Link targets are not words; link text is. The words of a
  `:term[text]{id=…}` mark are its text; Markdown's emphasis marks are not part of any word.
- A **sentence** ends at a word that ends with ".", "?" or "!" (closing quotes, brackets and emphasis may follow), or at
  the end of its block; inline code and formulas never end one. So a list item without a final stop is one sentence,
  and a colon that introduces a list ends its paragraph's last sentence. Headings, table cells and container titles
  hold words but no sentences.
- A **paragraph** is a block of prose lines between blank lines; each list item is a paragraph of its own, and so is
  each further paragraph inside an item.

Container directives follow remark-directive as booklib/blocks.py reads them: `:::name[label]{attributes}` opens one,
a line of colons alone closes the innermost one opened with no more colons. `::name{…}` is a leaf directive (a figure,
a checkpoint), a block of its own. Lists follow CommonMark's indentation: a line indented at least as far as an item's
text belongs to that item.
"""

import re

from booklib import blocks, markdown

c_Item = re.compile(r'^(?P<indent>[ \t]*)(?P<marker>[-*+]|(?P<number>\d{1,9})[.)])(?P<space>[ \t]+|$)(?P<rest>.*)$')
c_Heading = re.compile(r'^(?P<hashes>#{1,6})(?:[ \t]+(?P<title>.*?))?[ \t]*#*[ \t]*$')
c_Leaf = re.compile(r'^::(?P<name>[A-Za-z][\w-]*)(?:\[(?P<label>[^\]]*)\])?(?:\{(?P<attributes>[^}]*)\})?\s*$')
c_TableSeparator = re.compile(r'^\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$')
c_SentenceEnd = re.compile(r'[.?!]["\'\)\]\*_’”]*$')
c_Inline = re.compile(r'''
    (?P<code>(?P<ticks>`+)(?P<codetext>.+?)(?P=ticks))
  | (?P<math>(?<![\\$])\$(?P<mathtext>[^$\s](?:[^$]*?[^$\s\\])?)\$(?!\$))
  | (?P<image>!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]*)\))
  | (?P<link>\[(?P<linktext>(?:[^\[\]]|\[[^\[\]]*\])*)\]\((?P<target>[^)\s]*)(?:\s+"[^"]*")?\))
  | (?P<directive>(?<![\w:]):(?P<dname>[A-Za-z][\w-]*)\[(?P<dlabel>[^\]]*)\](?:\{(?P<dattributes>[^}]*)\})?)
  | (?P<mark>(?<![\w:]):(?P<mname>[A-Za-z][\w-]*)\{(?P<mattributes>[^}]*)\})
  | (?P<autolink><(?P<url>https?://[^>\s]+)>)
  | (?P<comment><!--.*?-->)
  | (?P<html></?[A-Za-z][^<>]*>)
  | (?P<strong>\*\*|__)
  | (?P<escape>\\(?P<escaped>[\\`*_{}\[\]()\#+\-.!$|<>~"']))
''', re.VERBOSE)
c_Space = re.compile(r'(\s+)')
c_EmphasisStart = re.compile(r'(^|(?<=\s)|(?<=[(\["\']))[*_]+(?=\S)')
c_EmphasisEnd = re.compile(r'(?<=\S)[*_]+(?=$|\s|[.,;:!?)\]"\'])')
c_NotWord = re.compile(r'[^\w]+')
c_EndCharacters = set('.?!"\')]*_\u2019\u201d')
c_Punctuation = '.,;:!?"\'()[]{}<>*_~‘’“”…'


class Word:
    """A word of prose. `text` is what the reader reads (a code span's code, a formula's TeX); `kind` is "word",
    "code" or "math" (a word that holds a code span or a formula); `bold` when it stands inside **…**; `link` the
    target of the link it stands in; `term` the id of the `:term` mark it stands in."""

    __slots__ = ('text', 'kind', 'bold', 'link', 'link_id', 'term', 'line', 'directive', 'end', 'bare', 'plain', 'key')

    def __init__(self, text, kind, bold, link, term, line, directive=None):
        self.text = text
        self.kind = kind
        self.bold = bold
        self.link = link[0] if link else None
        self.link_id = link[1] if link else None  # which link of the block: two links side by side differ
        self.term = term
        self.line = line
        self.directive = directive
        self.end = False  # the word ends a sentence
        self.bare = text.strip(c_Punctuation)  # without the punctuation around it ("time." -> "time")
        plain = self.bare
        if plain.endswith(("'s", '\u2019s')):
            plain = plain[:-2]
        self.plain = plain.rstrip("'\u2019")  # without a possessive ("Strata's" -> "Strata")
        self.key = self.bare.lower()

    def __repr__(self):
        return 'Word(%r, %s)' % (self.text, self.kind)


class Block:
    """A block of the page. `kind`: paragraph, item, heading, table, quote, label (a container's title), caption
    (a figure's caption or alt text), fence, math, open, close, leaf, html. `line` is its first line, `lines` the
    (number, text) of its lines. Prose blocks have `words`; `sentences` are lists of words (none for headings, tables
    and labels). `containers` are the open directives around it, outermost first; `items` the list items it stands
    in, outermost first; `section` the title of its level-2 section (None before the first)."""

    def __init__(self, kind, line, containers, section, indent=0):
        self.kind = kind
        self.line = line
        self.lines = []
        self.containers = list(containers)
        self.section = section
        self.section_line = None
        self.indent = indent
        self.items = []
        self.words = []
        self.sentences = []
        self.level = None  # headings
        self.ordered = False  # items
        self.number = None
        self.content_indent = 0
        self.list_id = None
        self.fence = None  # fences
        self.directive = None  # open, close, leaf: the Directive or (name, label, attributes)
        self.rows = []  # tables: lists of cells, each a list of words
        self.source = None  # captions: the manifest's file

    @property
    def text(self):
        return ' '.join(text.strip() for _, text in self.lines)

    @property
    def end_line(self):
        return self.lines[-1][0] if self.lines else self.line

    def inside(self, name):
        return any(directive.name == name for directive in self.containers)

    def __repr__(self):
        return 'Block(%s, line %d)' % (self.kind, self.line)


class Page:
    """The blocks of a page's body, in order (`blocks`), every container directive (`directives`) and the containers
    never closed (`unclosed`)."""

    def __init__(self, text):
        self.text = text
        self.blocks = []
        self.directives = []
        self.unclosed = []
        parse(self)

    def next_block(self, block, skip=('html',)):
        index = self.blocks.index(block) + 1
        while index < len(self.blocks) and self.blocks[index].kind in skip:
            index += 1
        return self.blocks[index] if index < len(self.blocks) else None

    def previous_block(self, block, skip=('html',)):
        index = self.blocks.index(block) - 1
        while index >= 0 and self.blocks[index].kind in skip:
            index -= 1
        return self.blocks[index] if index >= 0 else None


def indent_width(text):
    width = 0
    for char in text:
        if char == ' ':
            width += 1
        elif char == '\t':
            width += 4 - width % 4
        else:
            break
    return width


def parse(page):
    lines = page.text.split('\n')
    start = markdown.frontmatter_end(lines)
    fences = {fence.open_line: fence for fence in markdown.fences(page.text)}
    stack = []
    section = [None, None]
    current = None  # the block quote whose lines continue (paragraphs and items gather their own lines)
    blank = True
    number = start + 1
    item_stack = []  # the list items open at this line, outermost first
    list_counter = [0]

    def add(kind, line_number, indent=0):
        block = Block(kind, line_number, stack, section[0], indent)
        block.section_line = section[1]
        while item_stack and indent < item_stack[-1].content_indent and kind != 'item':
            item_stack.pop()
        block.items = list(item_stack)
        page.blocks.append(block)
        return block

    while number <= len(lines):
        raw = lines[number - 1].rstrip('\r')
        stripped = raw.strip()
        indent = indent_width(raw)
        if number in fences:
            fence = fences[number]
            block = add('fence', number, indent)
            block.fence = fence
            last = fence.close_line if fence.close_line is not None else len(lines)
            block.lines = [(line, lines[line - 1].rstrip('\r')) for line in range(number, last + 1)]
            number = last + 1
            current, blank = None, False
            continue
        if not stripped:
            current, blank = None, True
            number += 1
            continue
        if stripped.startswith('<!--'):
            block = add('html', number, indent)
            while True:
                block.lines.append((number, lines[number - 1].rstrip('\r')))
                if '-->' in lines[number - 1] or number >= len(lines):
                    break
                number += 1
            number += 1
            current, blank = None, False
            continue
        if stripped.startswith('$$'):
            block = add('math', number, indent)
            block.lines.append((number, raw))
            closed = stripped != '$$' and stripped.endswith('$$') and len(stripped) > 2
            while not closed and number < len(lines):
                number += 1
                block.lines.append((number, lines[number - 1].rstrip('\r')))
                closed = lines[number - 1].strip().endswith('$$')
            number += 1
            current, blank = None, False
            continue
        opening = blocks.c_ContainerOpen.match(stripped)
        closing = blocks.c_ContainerClose.match(stripped)
        if closing and stack:
            length = len(closing.group('marker'))
            block = add('close', number, indent)
            block.lines.append((number, raw))
            for index in range(len(stack) - 1, -1, -1):
                if len(stack[index].marker) <= length:
                    block.directive = stack[index]
                    for directive in stack[index:]:
                        directive.close_line = number
                    del stack[index:]
                    break
            block.containers = list(stack)
            number += 1
            current, blank = None, False
            continue
        if opening:
            directive = blocks.Directive(opening.group('name'), opening.group('label'),
                                         blocks.parse_attributes(opening.group('attributes')), number,
                                         opening.group('marker'), len(stack), stack[-1] if stack else None)
            block = add('open', number, indent)
            block.lines.append((number, raw))
            block.directive = directive
            page.directives.append(directive)
            stack.append(directive)
            if directive.label:
                label = add('label', number, indent)
                label.lines.append((number, directive.label))
                label.words = inline_words(directive.label, number)
            number += 1
            current, blank = None, False
            continue
        leaf = c_Leaf.match(stripped)
        if leaf:
            block = add('leaf', number, indent)
            block.lines.append((number, raw))
            block.directive = (leaf.group('name'), leaf.group('label'), blocks.parse_attributes(leaf.group('attributes')))
            number += 1
            current, blank = None, False
            continue
        heading = c_Heading.match(stripped) if stripped.startswith('#') else None
        if heading and (heading.group('title') is not None or stripped.strip('#') == ''):
            block = add('heading', number, indent)
            block.level = len(heading.group('hashes'))
            title = heading.group('title') or ''
            block.lines.append((number, title))
            block.words = inline_words(title, number)
            if block.level == 2 and not stack:
                section[0], section[1] = title, number
                block.section, block.section_line = title, number
            number += 1
            current, blank = None, False
            continue
        if stripped.startswith('|'):
            block = add('table', number, indent)
            while number <= len(lines) and lines[number - 1].strip().startswith('|'):
                row_text = lines[number - 1].rstrip('\r')
                block.lines.append((number, row_text))
                if not c_TableSeparator.match(row_text.strip()):
                    block.rows.append([inline_words(cell, number) for cell in table_cells(row_text)])
                number += 1
            block.words = [word for row in block.rows for cell in row for word in cell]
            current, blank = None, False
            continue
        if stripped.startswith('>'):
            if current is not None and current.kind == 'quote' and not blank:
                block = current
            else:
                block = add('quote', number, indent)
            block.lines.append((number, re.sub(r'^\s*>\s?', '', raw)))
            current, blank = block, False
            number += 1
            finish_quote = number > len(lines) or not lines[number - 1].strip().startswith('>')
            if finish_quote:
                fill_prose(block)
            continue
        item = c_Item.match(raw)
        if item:
            marker_indent = indent_width(item.group('indent'))
            while item_stack and item_stack[-1].indent >= marker_indent:
                item_stack.pop()
            block = Block('item', number, stack, section[0], marker_indent)
            block.section_line = section[1]
            block.items = list(item_stack)
            block.ordered = item.group('number') is not None
            block.number = int(item.group('number')) if block.ordered else None
            rest = item.group('rest')
            space = len(item.group('space')) if item.group('space') else 1
            block.content_indent = marker_indent + len(item.group('marker')) + (space if 0 < space <= 4 else 1)
            previous = next((other for other in reversed(page.blocks) if other.kind == 'item' and other.items == block.items
                             and other.indent == marker_indent), None)
            continues = previous is not None and previous.ordered == block.ordered and list_continues(page, previous, block)
            if continues:
                block.list_id = previous.list_id
            else:
                list_counter[0] += 1
                block.list_id = list_counter[0]
            page.blocks.append(block)
            item_stack.append(block)
            block.lines.append((number, rest))
            current, blank = block, False
            number += 1
            gather_continuation(page, block, lines, number)
            number = block.end_line + 1
            fill_prose(block)
            current = None
            continue
        block = add('paragraph', number, indent)
        block.lines.append((number, raw))
        number += 1
        gather_continuation(page, block, lines, number)
        number = block.end_line + 1
        if block.kind == 'paragraph' and re.match(r'^\s*<[A-Za-z/]', block.lines[0][1]) and not re.search(r'[A-Za-z]{2,}', re.sub(r'<[^>]*>', '', block.text)):
            block.kind = 'html'
        else:
            fill_prose(block)
        current, blank = None, False
    page.unclosed = stack


def list_continues(page, previous, block):
    """True when every block between the previous item and this one stands inside the previous item: anything else
    (a heading, a paragraph or a fence at a smaller indentation) ends the list."""
    index = page.blocks.index(previous) + 1
    return all(previous in other.items or other.kind == 'html' for other in page.blocks[index:])


def gather_continuation(page, block, lines, number):
    """Adds to a paragraph or item the lines that continue it: lines up to a blank line or the start of another
    block."""
    while number <= len(lines):
        raw = lines[number - 1].rstrip('\r')
        stripped = raw.strip()
        if not stripped or starts_block(raw, stripped):
            break
        block.lines.append((number, raw))
        number += 1


def starts_block(raw, stripped):
    if stripped.startswith(('```', '~~~', '$$', '<!--', '|', '>')):
        return True
    if blocks.c_ContainerOpen.match(stripped) or blocks.c_ContainerClose.match(stripped) or c_Leaf.match(stripped):
        return True
    if c_Heading.match(stripped) and stripped.startswith('#'):
        return True
    return bool(c_Item.match(raw))


def table_cells(row):
    """The cells of a table row, split at "|" outside code spans and escapes."""
    text = row.strip()
    if text.startswith('|'):
        text = text[1:]
    if text.endswith('|') and not text.endswith('\\|'):
        text = text[:-1]
    cells, current, index, ticks = [], '', 0, None
    while index < len(text):
        char = text[index]
        if char == '\\' and index + 1 < len(text):
            current += text[index:index + 2]
            index += 2
            continue
        if char == '`':
            run = re.match(r'`+', text[index:]).group(0)
            if ticks is None:
                ticks = run
            elif run == ticks:
                ticks = None
            current += run
            index += len(run)
            continue
        if char == '|' and ticks is None:
            cells.append(current)
            current = ''
        else:
            current += char
        index += 1
    cells.append(current)
    return cells


def fill_prose(block):
    """Reads the words and sentences of a prose block from its lines. Emphasis and links may run over line ends."""
    first = block.lines[0][0] if block.lines else block.line
    text = '\n'.join(text.strip() for _, text in block.lines)
    block.words = inline_words(text, first)
    if block.kind in ('paragraph', 'item', 'quote', 'caption'):
        block.sentences = split_sentences(block.words)


def split_sentences(words):
    sentences = []
    current = []
    for word in words:
        current.append(word)
        if word.end:
            sentences.append(current)
            current = []
    if current:
        sentences.append(current)
    return sentences


class _Builder:
    """Collects the pieces of words: a word ends at a space or a line end. `line` follows the line ends it passes."""

    def __init__(self, line):
        self.line = line
        self.words = []
        self.pieces = []  # (text, kind, bold, link, term, directive, line)

    def text(self, text, bold, link, term, directive=None):
        for part in c_Space.split(text):
            if not part:
                continue
            if part.isspace():
                self.flush()
                self.line += part.count('\n')
            else:
                self.pieces.append((part, 'word', bold, link, term, directive, self.line))

    def atom(self, text, kind, bold, link, term):
        self.pieces.append((text.replace('\n', ' '), kind, bold, link, term, None, self.line))
        self.line += text.count('\n')

    def flush(self):
        if not self.pieces:
            return
        if len(self.pieces) == 1:  # the usual word: one piece
            part, kind, bold, link, term, directive, line = self.pieces[0]
            word = Word(part, kind, bold and (kind != 'word' or bool(part.strip(c_Punctuation))), link, term, line, directive)
            word.end = kind == 'word' and part[-1:] in c_EndCharacters and bool(c_SentenceEnd.search(part))
            self.words.append(word)
            self.pieces = []
            return
        kinds = {piece[1] for piece in self.pieces}
        kind = 'code' if 'code' in kinds else 'math' if 'math' in kinds else 'word'
        text = ''.join(piece[0] for piece in self.pieces)
        marked = [piece for piece in self.pieces if piece[1] != 'word' or piece[0].strip(c_Punctuation)]
        bold = bool(marked) and all(piece[2] for piece in marked)
        link = next((piece[3] for piece in self.pieces if piece[3] is not None), None)
        term = next((piece[4] for piece in self.pieces if piece[4] is not None), None)
        directive = next((piece[5] for piece in self.pieces if piece[5] is not None), None)
        word = Word(text, kind, bold, link, term, self.pieces[0][6], directive)
        last = self.pieces[-1]
        word.end = last[1] == 'word' and bool(c_SentenceEnd.search(last[0]))
        self.words.append(word)
        self.pieces = []


def next_link(state, target):
    state['links'] = state.get('links', 0) + 1
    return (target, state['links'])


def inline_words(text, line, link=None, term=None, builder=None, state=None):
    """The words of prose text that starts on `line` (see the module's description)."""
    own = builder is None
    builder = builder or _Builder(line)
    state = state if state is not None else {'bold': False}
    position = 0
    for match in c_Inline.finditer(text):
        if match.start() > position:
            builder.text(strip_emphasis(text[position:match.start()]), state['bold'], link, term)
        position = match.end()
        if match.group('code'):
            code = match.group('codetext')
            builder.atom(code.strip() or code, 'code', state['bold'], link, term)
        elif match.group('math'):
            builder.atom(match.group('mathtext'), 'math', state['bold'], link, term)
        elif match.group('image'):
            builder.text(match.group('alt'), state['bold'], next_link(state, match.group('src')), term)
        elif match.group('link'):
            inline_words(match.group('linktext'), line, next_link(state, match.group('target')), term, builder, state)
        elif match.group('directive'):
            name = match.group('dname')
            if name == 'term':
                mark = blocks.parse_attributes(match.group('dattributes')).get('id', '')
                inline_words(match.group('dlabel'), line, link, mark, builder, state)
            elif name == 'since':
                builder.text('New in ' + match.group('dlabel'), state['bold'], link, term, 'since')
            else:
                builder.text(match.group('dlabel'), state['bold'], link, term, name)
        elif match.group('mark'):
            # A text directive without a label, such as :value{key="commands.count"}: the build puts one value of the
            # engine there, so it reads as one word the engine decides, like inline code.
            attributes = blocks.parse_attributes(match.group('mattributes'))
            builder.atom(attributes.get('key') or match.group('mname'), 'code', state['bold'], link, term)
        elif match.group('autolink'):
            builder.atom(match.group('url'), 'word', state['bold'], next_link(state, match.group('url')), term)
        elif match.group('comment') or match.group('html'):
            builder.line += match.group(0).count('\n')
        elif match.group('strong'):
            state['bold'] = not state['bold']
        elif match.group('escape'):
            builder.text(match.group('escaped'), state['bold'], link, term)
    if position < len(text):
        builder.text(strip_emphasis(text[position:]), state['bold'], link, term)
    if own:
        builder.flush()
        return builder.words
    return None


def strip_emphasis(text):
    """Text without the single-character emphasis marks (*a*, _a_) at the edges of its words; an underscore inside a
    word (snake_case) stays."""
    if '*' not in text and '_' not in text:
        return text
    return c_EmphasisEnd.sub('', c_EmphasisStart.sub('', text))


def normalize(word):
    """A word lowercased and without punctuation (copied-text compares runs of these)."""
    if word.isalnum():
        return word.lower()
    return c_NotWord.sub('', word.lower())
