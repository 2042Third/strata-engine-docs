"""Reading the parts of the book's Markdown the tools need, line by line: fenced code blocks (with their info string
and attributes), and the text outside them (prose, for the linter).

Fences follow CommonMark: three or more backticks or tildes open a fence, indented by the container it sits in (a
list item indents its fences); the same character, at least as many times, with nothing after it, closes it. The
indentation of the opening fence is removed from the lines inside, as CommonMark does.
"""

import re

c_FenceOpen = re.compile(r'^(?P<indent>[ \t]*)(?P<marker>`{3,}|~{3,})(?P<info>.*)$')
c_MetaToken = re.compile(r'''([A-Za-z_][\w-]*)=("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\{[^}]*\}|/(?:[^/\\]|\\.)+/|\S+)|\{[^}]*\}|\S+''')


class Fence:
    """A fenced code block. Line numbers count from 1 in the whole file; body lines are without the fence's indent."""

    def __init__(self, open_line, close_line, indent, marker, info, body):
        self.open_line = open_line
        self.close_line = close_line
        self.indent = indent
        self.marker = marker
        self.info = info
        self.body = body
        parts = info.strip().split(None, 1)
        self.lang = parts[0] if parts else ''
        self.meta = parts[1] if len(parts) > 1 else ''
        self.attributes, self.flags = parse_meta(self.meta)

    @property
    def text(self):
        return '\n'.join(self.body)


def parse_meta(meta):
    """Attributes (name=value, quotes removed) and bare flags of a fence's meta string."""
    attributes = {}
    flags = []
    for match in c_MetaToken.finditer(meta):
        name, value = match.group(1), match.group(2)
        if name:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
                value = re.sub(r'\\(.)', r'\1', value[1:-1])
            attributes[name] = value
        else:
            flags.append(match.group(0))
    return attributes, flags


def strip_indent(line, indent):
    """Removes up to len(indent) leading spaces or tabs (CommonMark removes the opening fence's indentation)."""
    count = 0
    while count < len(indent) and count < len(line) and line[count] in ' \t':
        count += 1
    return line[count:]


def frontmatter_end(lines):
    """Index of the first line after the front matter (0 when there is none). As Astro, the front matter may follow a
    byte-order mark and blank lines."""
    first = 0
    while first < len(lines) and not lines[first].lstrip('\ufeff').strip():
        first += 1
    if first < len(lines) and lines[first].lstrip('\ufeff').rstrip('\r') == '---':
        for index in range(first + 1, len(lines)):
            if lines[index].rstrip('\r').rstrip(' \t') == '---':
                return index + 1
    return 0


def fences(text):
    """Every fenced code block of a Markdown file, in order. An unclosed fence runs to the end of the file."""
    lines = text.split('\n')
    result = []
    index = frontmatter_end(lines)
    while index < len(lines):
        match = c_FenceOpen.match(lines[index].rstrip('\r'))
        if not match or (match.group('marker')[0] == '`' and '`' in match.group('info')):
            index += 1
            continue
        indent, marker, info = match.group('indent'), match.group('marker'), match.group('info')
        closing = re.compile(r'^[ \t]*' + re.escape(marker[0]) + '{' + str(len(marker)) + r',}[ \t]*$')
        body = []
        end = index + 1
        while end < len(lines) and not closing.match(lines[end].rstrip('\r')):
            body.append(strip_indent(lines[end].rstrip('\r'), indent))
            end += 1
        result.append(Fence(index + 1, end + 1 if end < len(lines) else None, indent, marker, info, body))
        index = end + 1
    return result


def safe_marker(body, marker):
    """The fence marker for a body: `marker`, or a longer run of its character when a line of the body starts with as
    many of them or more (Markdown in AGENTS.md holds ```sh blocks): a line of ``` alone would close a ``` fence
    early and turn the rest of the page into code."""
    char = marker[0]
    longest = 0
    for line in body:
        run = re.match(r'^[ \t]*(' + re.escape(char) + r'+)', line)
        if run:
            longest = max(longest, len(run.group(1)))
    return marker if longest < len(marker) else char * (longest + 1)


def replace_fence_body(text, fence, new_body):
    """The file's text with the fence's body replaced by new_body (lines), indented like the fence. When the body
    holds a run of the fence's character that could close it, both fence lines get a longer marker (safe_marker)."""
    lines = text.split('\n')
    if fence.close_line is None:
        raise ValueError('the fence opened on line %d is never closed' % fence.open_line)
    marker = safe_marker(new_body, fence.marker)
    if marker != fence.marker:
        lines[fence.open_line - 1] = fence.indent + marker + fence.info
        lines[fence.close_line - 1] = re.sub(re.escape(fence.marker[0]) + '+', marker, lines[fence.close_line - 1], count=1)
    indented = [(fence.indent + line) if line else line for line in new_body]
    lines[fence.open_line:fence.close_line - 1] = indented
    return '\n'.join(lines)


def replace_fence_info(text, fence, info):
    """The file's text with the fence's info string replaced; the marker on the line stays (replace_fence_body may
    have made it longer)."""
    lines = text.split('\n')
    current = re.match(r'^[ \t]*(' + re.escape(fence.marker[0]) + '{3,})', lines[fence.open_line - 1])
    marker = current.group(1) if current else fence.marker
    lines[fence.open_line - 1] = fence.indent + marker + info
    return '\n'.join(lines)


def prose_lines(text):
    """(line number, line) of every line outside front matter and fences: what the reader reads as text."""
    lines = text.split('\n')
    inside = set()
    for fence in fences(text):
        last = fence.close_line if fence.close_line is not None else len(lines)
        inside.update(range(fence.open_line, last + 1))
    start = frontmatter_end(lines)
    return [(number, lines[number - 1].rstrip('\r')) for number in range(start + 1, len(lines) + 1) if number not in inside]


def strip_inline_code(line):
    """The line with `code spans` replaced by spaces of the same length (columns stay where they were)."""
    return re.sub(r'(`+)(.+?)\1', lambda match: ' ' * len(match.group(0)), line)
