"""Reading C++ source as text, for the parsed routes of the generated reference (plan/pipelines.md §7.1). It is no
compiler: a tokenizer that keeps string literals (decoded) and comments (beside the tokens), and helpers that find a
bracket's partner, split a list at its top-level commas, join adjacent literals, read the data members of a struct and
evaluate the constant expressions that limits are written in.

- tokenize(text) returns Source: .tokens (Token: kind, text, line, value) and .comments (Comment: line, end, text, style).
  Kinds: "id", "num", "str", "chr", "punct", "pp" (a preprocessor line with its continuations). A string's value is the
  decoded text (escapes, \\x and octal bytes as UTF-8, raw strings); "::", "->", "..." and "##" are single tokens.
- match(tokens, index): the index of the bracket that closes the one at index ("(", "[", "{"), or None.
- split_top(tokens, start, end): [(start, end)] of the parts between top-level commas of tokens[start:end].
- string_at(tokens, index): (value, index after) of the adjacent string literals starting at index, or None.
- comment_before(source, line): the comment block that ends on the line before `line` (nothing between), or ''.
- comment_on(source, line): a comment that starts on `line` after code (a trailing comment), or ''.
- spelled(source, first, last): the source text of tokens[first..last] on one line, without comments.
- struct_members(source, name): the data members of `struct name { ... };` with their comments.
- evaluate(text, names): the value of a constant expression (numbers, + - * / % << >> | &, parentheses, static_cast,
  digit separators and suffixes, names in `names`), or None when it holds anything else.
"""

import re

c_Punctuators = ('::', '->', '...', '##')
c_Identifier = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
c_Number = re.compile(r"(?:0[xX][0-9A-Fa-f']+|0[bB][01']+|(?:\d[\d']*\.?[\d']*|\.\d[\d']*)(?:[eE][+-]?\d+)?)[A-Za-z]*")
c_Escapes = {'n': '\n', 't': '\t', 'r': '\r', '0': '\0', '\\': '\\', '"': '"', "'": "'", '?': '?', 'a': '\a', 'b': '\b',
             'f': '\f', 'v': '\v'}
c_Opening = {'(': ')', '[': ']', '{': '}'}


class Token:
    __slots__ = ('kind', 'text', 'line', 'value', 'start', 'end')

    def __init__(self, kind, text, line, value=None, start=0, end=0):
        self.kind, self.text, self.line, self.value, self.start, self.end = kind, text, line, value, start, end

    def __repr__(self):
        return 'Token(%s, %r, %d)' % (self.kind, self.text, self.line)


class Comment:
    __slots__ = ('line', 'end', 'text', 'style', 'trailing')

    def __init__(self, line, end, text, style, trailing):
        self.line, self.end, self.text, self.style, self.trailing = line, end, text, style, trailing


class Source:
    def __init__(self, text):
        self.text = text
        self.lines = text.split('\n')
        self.tokens = []
        self.comments = []
        self.by_end = {}
        self.by_start = {}


def decode_escapes(body):
    """The text of a string literal's body; \\x and octal escapes are bytes, joined as UTF-8."""
    out = bytearray()
    index = 0
    while index < len(body):
        char = body[index]
        if char != '\\' or index + 1 >= len(body):
            out += char.encode('utf-8')
            index += 1
            continue
        code = body[index + 1]
        if code == 'x':
            match = re.match(r'[0-9A-Fa-f]+', body[index + 2:])
            digits = match.group(0) if match else ''
            out.append(int(digits or '0', 16) & 0xFF)
            index += 2 + len(digits)
        elif code in '01234567':
            match = re.match(r'[0-7]{1,3}', body[index + 1:])
            out.append(int(match.group(0), 8) & 0xFF)
            index += 1 + len(match.group(0))
        elif code in 'uU':
            width = 4 if code == 'u' else 8
            out += chr(int(body[index + 2:index + 2 + width], 16)).encode('utf-8')
            index += 2 + width
        else:
            out += c_Escapes.get(code, code).encode('utf-8')
            index += 2
    return out.decode('utf-8', 'replace')


def tokenize(text):
    """The tokens and comments of C++ source (CRLF read as LF)."""
    text = text.replace('\r\n', '\n')
    source = Source(text)
    index = 0
    line = 1
    length = len(text)
    line_has_code = False
    while index < length:
        char = text[index]
        if char == '\n':
            line += 1
            index += 1
            line_has_code = False
            continue
        if char in ' \t\f\v\r':
            index += 1
            continue
        if text.startswith('//', index):
            end = text.find('\n', index)
            end = length if end < 0 else end
            comment = Comment(line, line, text[index + 2:end], '//', line_has_code)
            source.comments.append(comment)
            index = end
            continue
        if text.startswith('/*', index):
            end = text.find('*/', index + 2)
            end = length if end < 0 else end
            body = text[index + 2:end]
            comment = Comment(line, line + body.count('\n'), body, '/*', line_has_code)
            source.comments.append(comment)
            line += body.count('\n')
            index = end + 2
            continue
        if char == '#' and not line_has_code:
            start = index
            start_line = line
            while index < length:
                end = text.find('\n', index)
                end = length if end < 0 else end
                if end > 0 and text[end - 1] == '\\' and end < length:
                    line += 1
                    index = end + 1
                    continue
                index = end
                break
            source.tokens.append(Token('pp', text[start:index], start_line, None, start, index))
            continue
        line_has_code = True
        raw = re.match(r'(?:u8|u|U|L)?R"([^()\\ ]{0,16})\(', text[index:index + 24])
        if raw:
            delimiter = ')' + raw.group(1) + '"'
            body_start = index + raw.end()
            end = text.find(delimiter, body_start)
            end = length if end < 0 else end
            body = text[body_start:end]
            source.tokens.append(Token('str', text[index:end + len(delimiter)], line, body, index, end + len(delimiter)))
            line += body.count('\n')
            index = end + len(delimiter)
            continue
        prefix = re.match(r'(?:u8|u|U|L)?(["\'])', text[index:index + 4])
        if prefix:
            quote = prefix.group(1)
            body_start = index + prefix.end()
            cursor = body_start
            while cursor < length and text[cursor] != quote and text[cursor] != '\n':
                cursor += 2 if text[cursor] == '\\' else 1
            body = text[body_start:cursor]
            kind = 'str' if quote == '"' else 'chr'
            source.tokens.append(Token(kind, text[index:cursor + 1], line, decode_escapes(body), index, cursor + 1))
            index = cursor + 1
            continue
        identifier = c_Identifier.match(text, index)
        if identifier:
            source.tokens.append(Token('id', identifier.group(0), line, None, index, identifier.end()))
            index = identifier.end()
            continue
        number = c_Number.match(text, index)
        if number and number.group(0):
            source.tokens.append(Token('num', number.group(0), line, None, index, number.end()))
            index = number.end()
            continue
        for punctuator in c_Punctuators:
            if text.startswith(punctuator, index):
                source.tokens.append(Token('punct', punctuator, line, None, index, index + len(punctuator)))
                index += len(punctuator)
                break
        else:
            source.tokens.append(Token('punct', char, line, None, index, index + 1))
            index += 1
    # Comment blocks: consecutive // lines (or one /* */) that are not trailing a line of code.
    blocks = []
    for comment in source.comments:
        if comment.trailing:
            source.by_start.setdefault(comment.line, comment)
            continue
        if blocks and blocks[-1][-1].style == '//' and comment.style == '//' and comment.line == blocks[-1][-1].end + 1:
            blocks[-1].append(comment)
        else:
            blocks.append([comment])
    for block in blocks:
        source.by_end[block[-1].end] = block
    return source


def comment_text(comments):
    """A comment block as one paragraph: the lines joined, leading stars and slashes of C comments removed."""
    parts = []
    for comment in comments:
        for raw in comment.text.split('\n'):
            stripped = raw.strip()
            if comment.style == '/*':
                stripped = re.sub(r'^\*+\s?', '', stripped).strip()
            if stripped.startswith('/') and set(stripped) == {'/'}:
                continue  # a ruler line of slashes
            if stripped:
                parts.append(stripped)
    return ' '.join(parts)


def comment_before(source, line):
    """The comment block that ends on the line just before `line`, as one paragraph ('' when there is none)."""
    block = source.by_end.get(line - 1)
    return comment_text(block) if block else ''


def comment_on(source, line):
    """The trailing comment of a line of code, as one paragraph ('' when there is none)."""
    comment = source.by_start.get(line)
    return comment_text([comment]) if comment else ''


def match(tokens, index):
    """The index of the token that closes the bracket at index, or None (angle brackets are not brackets here)."""
    opening = tokens[index].text
    closing = c_Opening.get(opening)
    if closing is None:
        return None
    depth = 0
    for position in range(index, len(tokens)):
        text = tokens[position].text
        if tokens[position].kind != 'punct':
            continue
        if text in c_Opening:
            depth += 1
        elif text in (')', ']', '}'):
            depth -= 1
            if depth == 0:
                return position if text == closing else None
    return None


def match_angle(tokens, index, end=None):
    """The index of the ">" that closes the "<" at index (round, square and curly brackets nest inside), or None."""
    end = len(tokens) if end is None else end
    depth = 0
    position = index
    while position < end:
        token = tokens[position]
        if token.kind == 'punct' and token.text in c_Opening:
            closed = match(tokens, position)
            if closed is None:
                return None
            position = closed + 1
            continue
        if token.text == '<':
            depth += 1
        elif token.text == '>':
            depth -= 1
            if depth == 0:
                return position
        elif token.text in (';', ')', ']', '}'):
            return None
        position += 1
    return None


def split_top(tokens, start, end):
    """The (start, end) ranges between the commas of tokens[start:end] that are outside every bracket."""
    parts = []
    depth = 0
    first = start
    for position in range(start, end):
        token = tokens[position]
        if token.kind != 'punct':
            continue
        if token.text in c_Opening:
            depth += 1
        elif token.text in (')', ']', '}'):
            depth -= 1
        elif token.text == ',' and depth == 0:
            parts.append((first, position))
            first = position + 1
    if first < end or parts:
        parts.append((first, end))
    return parts


def string_at(tokens, index):
    """(text, index after) of the adjacent string literals that start at index, or None when none starts there."""
    if index >= len(tokens) or tokens[index].kind != 'str':
        return None
    value = ''
    position = index
    while position < len(tokens) and tokens[position].kind == 'str':
        value += tokens[position].value
        position += 1
    return value, position


def strings(tokens, start, end):
    """[(text, line)] of every run of adjacent string literals in tokens[start:end]."""
    found = []
    position = start
    while position < end:
        joined = string_at(tokens, position)
        if joined is None:
            position += 1
            continue
        found.append((joined[0], tokens[position].line))
        position = min(joined[1], end)
    return found


def spelled(source, first, last):
    """The source text of tokens[first] to tokens[last] (both included) on one line: comments dropped, white space
    collapsed to single spaces."""
    text = source.text[source.tokens[first].start:source.tokens[last].end]
    text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
    text = re.sub(r'//[^\n]*', ' ', text)
    return ' '.join(text.split())


def find_struct(source, name):
    """(index of "{", index of "}") of the definition `struct name {` or `class name {`, or None."""
    tokens = source.tokens
    for index in range(len(tokens) - 2):
        if tokens[index].text in ('struct', 'class') and tokens[index + 1].text == name:
            position = index + 2
            while position < len(tokens) and tokens[position].text not in ('{', ';'):
                position += 1
            if position < len(tokens) and tokens[position].text == '{':
                closed = match(tokens, position)
                if closed is not None:
                    return position, closed
    return None


def struct_members(source, name):
    """The data members of the struct or class `name`, in declaration order: [{name, type, default, line, comment}]. Member
    functions, nested types, using declarations, friends and access labels are left out; a comment block right above a
    member, or a trailing comment on its line, is its comment."""
    found = find_struct(source, name)
    if found is None:
        return None
    open_index, close_index = found
    tokens = source.tokens
    members = []
    position = open_index + 1
    while position < close_index:
        start = position
        # A statement: up to ";" at depth 0, or a block (a function's body, a nested type) that closes it.
        end = position
        body = False
        while end < close_index:
            token = tokens[end]
            if token.kind == 'punct' and token.text in ('(', '['):
                end = match(tokens, end) or end
            elif token.kind == 'punct' and token.text == '{':
                closed = match(tokens, end)
                before = [item.text for item in tokens[start:end]]
                if '=' in before or (before and before[-1] not in (')', 'const', 'override', 'final', 'noexcept') and '(' not in before
                                     and not set(before) & {'struct', 'class', 'enum', 'union', 'namespace'}):
                    end = closed or end  # a brace initializer: part of the statement
                else:
                    end = closed or end
                    body = True
                    break
            elif token.text == ';':
                break
            elif token.kind == 'pp':
                break
            end += 1
        first = start
        position = end + 1
        if body and end + 1 < close_index and tokens[end + 1].text == ';':
            position = end + 2
        while first + 1 < end and tokens[first].text in ('public', 'private', 'protected') and tokens[first + 1].text == ':':
            first += 2
        if first >= end or body:
            continue
        statement = tokens[first:end]
        words = [token.text for token in statement]
        if set(words) & {'using', 'friend', 'typedef', 'struct', 'class', 'enum', 'union', 'template', 'static_assert', 'operator'}:
            continue
        equals = words.index('=') if '=' in words else None
        declarator = words[:equals] if equals is not None else words
        brace = declarator.index('{') if '{' in declarator else None
        if brace is not None:
            declarator = declarator[:brace]
        if '(' in declarator:
            # A function pointer member, "Ret (*Name)(...)", is data; any other parenthesis declares a function.
            if not (len(declarator) > declarator.index('(') + 2 and declarator[declarator.index('(') + 1] == '*'):
                continue
            member = declarator[declarator.index('(') + 2]
            type_text = spelled(source, first, end - 1)
        else:
            if not declarator or not c_Identifier.fullmatch(declarator[-1] if declarator[-1] != ']' else 'x'):
                continue
            if declarator[-1] == ']':
                member = declarator[declarator.index('[') - 1]
                type_tokens = declarator.index('[') - 1
            else:
                member = declarator[-1]
                type_tokens = len(declarator) - 1
            type_text = spelled(source, first, first + type_tokens - 1) if type_tokens else ''
        default = None
        if equals is not None:
            default = spelled(source, first + equals + 1, end - 1)
        elif brace is not None:
            default = spelled(source, first + len(declarator), end - 1)
        line = statement[0].line
        comment = comment_before(source, line) or comment_on(source, statement[-1].line) or comment_on(source, line)
        members.append({'name': member, 'type': type_text, 'default': default, 'line': line, 'comment': comment})
    return members


c_Expression = re.compile(r"\s*(0[xX][0-9A-Fa-f']+|0[bB][01']+|\d[\d']*\.?[\d']*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)"
                          r"([uUlLfF]*)|\s*([A-Za-z_][A-Za-z0-9_:<>]*)|\s*(<<|>>|[-+*/%()|&~])")


def evaluate(text, names=None):
    """The value of a constant expression, or None. Integers stay integers; a float literal or a division with a float
    makes a float. `static_cast<T>(x)` and `T(x)` casts of arithmetic types are read through; names come from `names`."""
    names = names or {}
    text = re.sub(r'static_cast\s*<[^<>]*>', '', text)
    text = re.sub(r'\b(?:u?int(?:8|16|32|64)_t|size_t|float|double|uint32_t)\s*(?=\()', '', text)
    text = re.sub(r'\b(?:u?int(?:8|16|32|64)_t|size_t)\s*\{\s*([^{}]*)\}', r'(\1)', text)
    items = []
    position = 0
    text = text.strip()
    while position < len(text):
        found = c_Expression.match(text, position)
        if not found or found.end() == position:
            return None
        position = found.end()
        if found.group(1):
            literal = found.group(1).replace("'", '')
            suffix = found.group(2) or ''
            if literal.lower().startswith('0x'):
                items.append(int(literal, 16))
            elif literal.lower().startswith('0b'):
                items.append(int(literal, 2))
            elif any(char in literal for char in '.eE') or 'f' in suffix.lower():
                items.append(float(literal))
            else:
                items.append(int(literal))
        elif found.group(3):
            name = found.group(3)
            if name in ('true', 'false'):
                items.append(1 if name == 'true' else 0)
            elif name in names and isinstance(names[name], (int, float)):
                items.append(names[name])
            else:
                return None
        else:
            items.append(found.group(4))
    parser = _ExpressionParser(items)
    try:
        value = parser.expression()
    except (ValueError, ZeroDivisionError, IndexError, TypeError):
        return None
    return value if parser.position == len(items) else None


class _ExpressionParser:
    c_Levels = [('|',), ('&',), ('<<', '>>'), ('+', '-'), ('*', '/', '%')]

    def __init__(self, items):
        self.items = items
        self.position = 0

    def peek(self):
        return self.items[self.position] if self.position < len(self.items) else None

    def expression(self, level=0):
        if level == len(self.c_Levels):
            return self.unary()
        value = self.expression(level + 1)
        while isinstance(self.peek(), str) and self.peek() in self.c_Levels[level]:
            operator = self.items[self.position]
            self.position += 1
            right = self.expression(level + 1)
            if operator == '|':
                value = int(value) | int(right)
            elif operator == '&':
                value = int(value) & int(right)
            elif operator == '<<':
                value = int(value) << int(right)
            elif operator == '>>':
                value = int(value) >> int(right)
            elif operator == '+':
                value = value + right
            elif operator == '-':
                value = value - right
            elif operator == '*':
                value = value * right
            elif operator == '/':
                value = value / right if isinstance(value, float) or isinstance(right, float) else value // right
            else:
                value = value % right
        return value

    def unary(self):
        item = self.peek()
        if item == '-':
            self.position += 1
            return -self.unary()
        if item == '+':
            self.position += 1
            return self.unary()
        if item == '~':
            self.position += 1
            return ~int(self.unary())
        if item == '(':
            self.position += 1
            value = self.expression()
            if self.peek() != ')':
                raise ValueError('no closing parenthesis')
            self.position += 1
            return value
        if isinstance(item, (int, float)):
            self.position += 1
            return item
        raise ValueError('not a value: %r' % (item,))
