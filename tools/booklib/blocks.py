"""The block structure of a page that the page checks read: level-2 sections, container directives (`:::name`), list
items and relative links, with the file's line numbers.

Container directives follow remark-directive, as the build reads them: a line of three or more colons, a name, an
optional `[label]` and an optional `{attributes}` opens one; a line of colons alone closes the innermost open
container whose opening had no more colons than it. Leaf directives (`::name`) and text directives (`:name`) open
nothing. Everything inside code fences is skipped.
"""

import re

from booklib import markdown

c_ContainerOpen = re.compile(r'^(?P<marker>:{3,})(?P<name>[A-Za-z][\w-]*)(?:\[(?P<label>[^\]]*)\])?(?:\{(?P<attributes>[^}]*)\})?\s*$')
c_ContainerClose = re.compile(r'^(?P<marker>:{3,})\s*$')
c_Heading = re.compile(r'^(?P<hashes>#{1,6})\s+(?P<title>.*?)\s*#*\s*$')
c_Attribute = re.compile(r'''(?P<key>[A-Za-z_][\w-]*)(?:=(?P<value>"[^"]*"|'[^']*'|[^\s"'=<>`]+))?|#(?P<id>[\w-]+)|\.(?P<class>[\w-]+)''')
c_OrderedItem = re.compile(r'^(?P<number>\d{1,9})[.)](?:[ \t]+|$)')
c_BulletItem = re.compile(r'^[-*+](?:[ \t]+|$)')
c_Link = re.compile(r'(?<!!)\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)(?:\s+"[^"]*")?\)')


def parse_attributes(text):
    """The {…} of a directive as a dict: key="value", key='value', key=value, a bare key (an empty value), #id and
    .class (remark-directive's shorthands)."""
    attributes = {}
    for match in c_Attribute.finditer(text or ''):
        if match.group('id'):
            attributes['id'] = match.group('id')
        elif match.group('class'):
            attributes['class'] = (attributes.get('class', '') + ' ' + match.group('class')).strip()
        else:
            value = match.group('value')
            if value is None:
                value = ''
            elif value[:1] in '"\'':
                value = value[1:-1]
            attributes[match.group('key')] = value
    return attributes


def split_ids(value):
    """The learn ids of a `tests` attribute: separated by spaces or commas."""
    return [item for item in re.split(r'[\s,]+', value or '') if item]


class Directive:
    def __init__(self, name, label, attributes, line, marker, depth, parent):
        self.name = name
        self.label = label
        self.attributes = attributes
        self.line = line
        self.marker = marker
        self.depth = depth  # 0 for a container at the top of the page
        self.parent = parent
        self.close_line = None


class Line:
    """A line of the page outside front matter and fences, with the containers it stands in."""

    def __init__(self, number, text, containers):
        self.number = number
        self.text = text
        self.stripped = text.lstrip(' \t')
        self.indent = len(text) - len(self.stripped)
        self.containers = containers  # the open directives around the line, outermost first


class Section:
    """A heading of level 2 (`## Title`) and the lines up to the next one."""

    def __init__(self, title, line):
        self.title = title
        self.line = line
        self.lines = []


class Page:
    """The structure of a page's body: `lines` (outside front matter and fences), `directives` (every container),
    `headings` ((level, title, line) of each heading outside containers), `sections` (level 2), `intro` (the lines
    before the first level-2 heading)."""

    def __init__(self, text):
        self.text = text
        self.lines = []
        self.directives = []
        self.headings = []
        self.sections = []
        self.intro = []
        self.unclosed = []
        stack = []
        for number, raw in markdown.prose_lines(text):
            stripped = raw.strip()
            opening = c_ContainerOpen.match(stripped)
            closing = c_ContainerClose.match(stripped)
            if closing and stack:
                length = len(closing.group('marker'))
                for index in range(len(stack) - 1, -1, -1):
                    if len(stack[index].marker) <= length:
                        for directive in stack[index:]:
                            directive.close_line = number
                        del stack[index:]
                        break
                self.lines.append(Line(number, raw, list(stack)))
                self.add_to_section(self.lines[-1])
                continue
            line = Line(number, raw, list(stack))
            self.lines.append(line)
            if opening:
                directive = Directive(opening.group('name'), opening.group('label'), parse_attributes(opening.group('attributes')),
                                      number, opening.group('marker'), len(stack), stack[-1] if stack else None)
                self.directives.append(directive)
                stack.append(directive)
                self.add_to_section(line)
                continue
            heading = c_Heading.match(raw) if not stack else None
            if heading:
                level = len(heading.group('hashes'))
                self.headings.append((level, heading.group('title'), number))
                if level == 2:
                    self.sections.append(Section(heading.group('title'), number))
                    continue
            self.add_to_section(line)
        self.unclosed = stack

    def add_to_section(self, line):
        if self.sections:
            self.sections[-1].lines.append(line)
        else:
            self.intro.append(line)

    def section(self, title):
        return next((section for section in self.sections if section.title == title), None)


def items(lines, depth, ordered=True):
    """The list items that start at column 0 of the given containers' depth, as (line, the lines up to the next item)."""
    pattern = c_OrderedItem if ordered else c_BulletItem
    result = []
    for line in lines:
        if len(line.containers) == depth and line.indent == 0 and pattern.match(line.text):
            result.append((line, []))
        elif result:
            result[-1][1].append(line)
    return result


def answers_in(lines):
    """The `:::answer` directives that open on the given lines."""
    found = []
    for line in lines:
        opening = c_ContainerOpen.match(line.stripped)
        if opening and opening.group('name') == 'answer':
            found.append((line, parse_attributes(opening.group('attributes'))))
    return found


def links(lines):
    """(line, target) of every Markdown link on the lines, outside inline code."""
    found = []
    for line in lines:
        for match in c_Link.finditer(markdown.strip_inline_code(line.text)):
            found.append((line, match.group('target')))
    return found
