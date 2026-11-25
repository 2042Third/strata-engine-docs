"""The front matter of a page: the YAML block between the first two "---" lines.

The standard library has no YAML reader, so this reads the subset the book's front matter uses and rejects everything
else with a message, instead of guessing: "key: value" pairs at the top level, values that are plain or quoted
strings, numbers, booleans and null of YAML 1.2's core schema (as Astro reads them), flow lists ("[a, b]") or block
lists ("- a" on the following lines) whose items are scalars or mappings of scalars ("- id: x" with "  text: y"
below it, style.md's learn lines), one level of nested "key: value" lines, and comments ("# ..." on a line of its own,
or after a value and a space). A plain value may not contain ": " or start with a character YAML treats
specially, exactly as YAML would refuse it. The build's reader (src/lib/markdown.mjs) refuses what this subset does
not read, and both are tested on the same cases (tools/tests/fixtures/frontmatter.json).
"""

import re

c_Key = re.compile(r'^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$')
# YAML 1.2's core schema, which Astro and the build read front matter with.
c_Integer = re.compile(r'^[-+]?[0-9]+$')
c_Octal = re.compile(r'^0o[0-7]+$')
c_Hexadecimal = re.compile(r'^0x[0-9a-fA-F]+$')
c_Float = re.compile(r'^[-+]?(\.[0-9]+|[0-9]+(\.[0-9]*)?)([eE][-+]?[0-9]+)?$')
c_Special = {'.inf': float('inf'), '.Inf': float('inf'), '.INF': float('inf'), '+.inf': float('inf'), '+.Inf': float('inf'), '+.INF': float('inf'),
             '-.inf': float('-inf'), '-.Inf': float('-inf'), '-.INF': float('-inf')}
c_True = ('true', 'True', 'TRUE')
c_False = ('false', 'False', 'FALSE')
c_Null = ('null', 'Null', 'NULL', '~')
c_ReservedStart = set('[]{}#&*!|>\'"%@`,?:-')


class FrontmatterError(Exception):
    def __init__(self, message, line):
        super().__init__('line %d: %s' % (line, message))
        self.line = line


def split(text):
    """Returns (front matter text or None, body, line number of the body's first line). As Astro, the front matter
    may follow a byte-order mark (Notepad writes one) and blank lines."""
    if text.startswith('\ufeff'):
        text = text[1:]
    lines = text.splitlines(keepends=True)
    first = 0
    while first < len(lines) and not lines[first].strip(' \t\r\n'):
        first += 1
    if first >= len(lines) or lines[first].rstrip('\r\n') != '---':
        return None, text, 1
    for index in range(first + 1, len(lines)):
        if lines[index].rstrip('\r\n').rstrip(' \t') == '---':
            return ''.join(lines[first + 1:index]), ''.join(lines[index + 1:]), index + 2
    raise FrontmatterError('the front matter has no closing "---" line', first + 1)


def strip_comment(value, line):
    """The value without a trailing comment: outside quotes, "#" after a space or tab starts one, as in YAML."""
    quote = None
    index = 0
    while index < len(value):
        char = value[index]
        if quote:
            if quote == '"' and char == '\\':
                index += 2
                continue
            if char == quote:
                if quote == "'" and value[index + 1:index + 2] == "'":
                    index += 2
                    continue
                quote = None
        elif char in '"\'' and (index == 0 or value[index - 1] in ' \t[,'):
            quote = char
        elif char == '#' and index > 0 and value[index - 1] in ' \t':
            return value[:index].rstrip()
        index += 1
    return value.rstrip()


def parse_scalar(raw, line):
    value = raw.strip()
    if value == '':
        return None
    if value[0] == '"':
        if len(value) < 2 or not value.endswith('"'):
            raise FrontmatterError('the quoted value has no closing "', line)
        return parse_double_quoted(value[1:-1], line)
    if value[0] == "'":
        if len(value) < 2 or not value.endswith("'"):
            raise FrontmatterError("the quoted value has no closing '", line)
        inner = value[1:-1]
        if re.search(r"(?<!')'(?!')", inner.replace("''", '')):
            raise FrontmatterError("a ' inside a single-quoted value is written ''", line)
        return inner.replace("''", "'")
    if value in c_True:
        return True
    if value in c_False:
        return False
    if value in c_Null:
        return None
    if c_Integer.match(value):
        return int(value)
    if c_Octal.match(value):
        return int(value[2:], 8)
    if c_Hexadecimal.match(value):
        return int(value[2:], 16)
    if c_Float.match(value):
        return float(value)
    if value in c_Special:
        return c_Special[value]
    if value in ('.nan', '.NaN', '.NAN'):
        return float('nan')
    if value[0] in c_ReservedStart and not (value[0] == '-' and len(value) > 1 and value[1] != ' '):
        raise FrontmatterError('a value starting with %r must be quoted' % value[0], line)
    if ': ' in value or value.endswith(':'):
        raise FrontmatterError('a value containing ": " must be quoted (YAML would read a second key)', line)
    return value


def parse_double_quoted(inner, line):
    out = []
    escapes = {'n': '\n', 't': '\t', '"': '"', '\\': '\\', '/': '/'}
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == '\\':
            if index + 1 >= len(inner) or inner[index + 1] not in escapes:
                raise FrontmatterError('unknown escape in a quoted value', line)
            out.append(escapes[inner[index + 1]])
            index += 2
            continue
        if char == '"':
            raise FrontmatterError('a " inside a double-quoted value is written \\"', line)
        out.append(char)
        index += 1
    return ''.join(out)


def split_flow(inner, line):
    """Splits the inside of "[a, 'b, c', d]" at top-level commas."""
    items = []
    current = ''
    quote = None
    for char in inner:
        if quote:
            current += char
            if char == quote:
                quote = None
        elif char in '"\'':
            quote = char
            current += char
        elif char == ',':
            items.append(current)
            current = ''
        elif char in '[]{}':
            raise FrontmatterError('nested lists and mappings are not part of the book\'s front matter', line)
        else:
            current += char
    if quote:
        raise FrontmatterError('a quoted list item has no closing quote', line)
    if current.strip() or items:
        items.append(current)
    if any(not item.strip() for item in items):
        raise FrontmatterError('the list has an empty item', line)
    return items


def parse_item_mapping(lines, index, first_line, key, column, content, item_number):
    """The mapping of one list item whose first "key: value" is `content` (on the item's line) and whose other keys
    follow on lines indented to `column`, as YAML reads "- id: x" with "  text: y" below it. Values are scalars.
    Returns (mapping, index of the first line after it)."""
    mapping = {}

    def add(text, number):
        match = c_Key.match(text)
        if not match:
            raise FrontmatterError('expected "key: value" inside an item of the list %r' % key, number)
        name, value = match.group(1), (match.group(2) or '').strip()
        if name in mapping:
            raise FrontmatterError('the key %r appears twice in an item of the list %r' % (name, key), number)
        if value[:1] in ('[', '{'):
            raise FrontmatterError('nested lists and mappings are not part of the book\'s front matter', number)
        if value[:1] in ('|', '>'):
            raise FrontmatterError('block scalars (| and >) are not part of the book\'s front matter', number)
        mapping[name] = parse_scalar(value, number)

    add(content, item_number)
    while index < len(lines):
        raw = lines[index]
        number = first_line + index
        if not raw.strip() or raw.strip().startswith('#'):
            index += 1
            continue
        indent = len(raw) - len(raw.lstrip(' '))
        if indent < column:
            break
        if indent > column:
            raise FrontmatterError('inside an item of the list %r, only "key: value" lines in the column of its first key are read' % key, number)
        add(strip_comment(raw.strip(), number), number)
        index += 1
    return mapping, index


def parse(text, first_line=2):
    """Parses the front matter text into a dict. Line numbers in errors count from first_line (the line after ---)."""
    data = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        number = first_line + index
        index += 1
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        if raw[0] in ' \t':
            raise FrontmatterError('unexpected indentation (only top-level keys and "- " list items are used)', number)
        match = c_Key.match(raw)
        if not match:
            raise FrontmatterError('expected "key: value"', number)
        key, value = match.group(1), strip_comment(match.group(2) or '', number)
        if key in data:
            raise FrontmatterError('the key %r appears twice' % key, number)
        stripped = value.strip()
        if stripped.startswith('['):
            if not stripped.endswith(']'):
                raise FrontmatterError('a flow list must close on the same line', number)
            data[key] = [parse_scalar(item, number) for item in split_flow(stripped[1:-1], number)]
        elif (stripped == '' or stripped.startswith('#')) and index < len(lines) and re.match(r'^\s+[A-Za-z_][A-Za-z0-9_-]*:(\s|$)', lines[index]):
            # One level of nested "key: value" lines (Starlight's hero: title, tagline).
            nested = {}
            while index < len(lines) and (re.match(r'^\s+[A-Za-z_][A-Za-z0-9_-]*:(\s|$)', lines[index]) or not lines[index].strip()):
                item = lines[index]
                item_number = first_line + index
                index += 1
                if not item.strip():
                    continue
                item_match = c_Key.match(strip_comment(item.strip(), item_number))
                if not item_match:
                    raise FrontmatterError('expected "key: value" inside %r' % key, item_number)
                inner = (item_match.group(2) or '').strip()
                if inner == '' or inner[0] in '[{|>':
                    raise FrontmatterError('only "key: value" lines are read inside %r' % key, item_number)
                nested[item_match.group(1)] = parse_scalar(inner, item_number)
            data[key] = nested
        elif stripped == '' or stripped.startswith('#'):
            items = []
            dash_column = None
            while index < len(lines) and (lines[index].startswith(' ') or lines[index].startswith('-') or not lines[index].strip()):
                item = lines[index]
                item_number = first_line + index
                index += 1
                if not item.strip() or item.strip().startswith('#'):
                    continue
                item_match = re.match(r'^(\s*)-( +)(.*)$', strip_comment(item, item_number))
                if not item_match:
                    raise FrontmatterError('expected a "- item" line of the list %r' % key, item_number)
                content = item_match.group(3)
                if dash_column is None:
                    dash_column = len(item_match.group(1))
                elif len(item_match.group(1)) != dash_column:
                    raise FrontmatterError('the items of the list %r stand at two indentations: put every "- " in the '
                                           'same column' % key, item_number)
                is_mapping = bool(c_Key.match(content))
                if items and isinstance(items[0], dict) != is_mapping:
                    raise FrontmatterError('the list %r mixes items that are "key: value" mappings with plain values: '
                                           'write every item the same way' % key, item_number)
                if is_mapping:
                    # An item that is a mapping ("- id: x" and "  text: y" below it, style.md's learn lines): its keys
                    # stand in the column of the first one.
                    column = len(item_match.group(1)) + 1 + len(item_match.group(2))
                    mapping, index = parse_item_mapping(lines, index, first_line, key, column, content, item_number)
                    items.append(mapping)
                    continue
                items.append(parse_scalar(content, item_number))
            data[key] = items if items else None
        elif stripped[0] in '|>':
            raise FrontmatterError('block scalars (| and >) are not part of the book\'s front matter', number)
        elif stripped.startswith('{'):
            raise FrontmatterError('mappings are not part of the book\'s front matter', number)
        else:
            data[key] = parse_scalar(value, number)
    return data


def read(text):
    """(data or None, body, body line, error message or None) of a whole page."""
    try:
        front, body, body_line = split(text)
    except FrontmatterError as error:
        return None, text, 1, str(error)
    if front is None:
        return None, body, body_line, 'the page has no front matter'
    try:
        # Errors name lines of the file: the front matter may start after a byte-order mark and blank lines.
        return parse(front, body_line - len(front.splitlines(True)) - 1), body, body_line, None
    except FrontmatterError as error:
        return None, body, body_line, str(error)
