"""JSON with the line of every value, so that a tool's message about a JSON file names the line to change.

load(text) returns (data, lines): data as json.loads gives it, and lines maps every JSON pointer of the document
("" for the whole document, "/figures/0/id" for a member) to the line (from 1) where that value starts. A member's key
shares its value's line in the files the book writes; where it does not, the value's line is the one named.

line_of(lines, pointer) gives the line of the pointer, or of its nearest parent that has one (a field that is missing
is reported on the line of the object that should hold it).
"""

import bisect
import json


class JsonError(ValueError):
    """Invalid JSON; .line is the line (from 1) where the reader stopped."""

    def __init__(self, message, line):
        super().__init__('line %d: %s' % (line, message))
        self.line = line


def escape(part):
    return str(part).replace('~', '~0').replace('/', '~1')


def pointer_of(path):
    return ''.join('/' + escape(part) for part in path)


class Scanner:
    def __init__(self, text):
        self.text = text
        self.index = 0
        self.starts = [0]
        for position, char in enumerate(text):
            if char == '\n':
                self.starts.append(position + 1)
        self.lines = {}

    def line(self, index=None):
        return bisect.bisect_right(self.starts, self.index if index is None else index)

    def fail(self, message):
        raise JsonError(message, self.line())

    def skip(self):
        while self.index < len(self.text) and self.text[self.index] in ' \t\r\n':
            self.index += 1

    def value(self, path):
        self.skip()
        if self.index >= len(self.text):
            self.fail('the document ends where a value was expected')
        self.lines[pointer_of(path)] = self.line()
        char = self.text[self.index]
        if char == '{':
            self.index += 1
            self.skip()
            if self.text.startswith('}', self.index):
                self.index += 1
                return
            while True:
                self.skip()
                if not self.text.startswith('"', self.index):
                    self.fail('a key in double quotes was expected')
                key_line = self.line()
                key = self.string()
                self.skip()
                if not self.text.startswith(':', self.index):
                    self.fail('":" was expected after the key "%s"' % key)
                self.index += 1
                self.value(path + (key,))
                # The key's line, when the value starts on a later line ("key":\n [ ...): a reader looks for the key.
                self.lines[pointer_of(path + (key,))] = key_line
                self.skip()
                if self.text.startswith(',', self.index):
                    self.index += 1
                    continue
                if self.text.startswith('}', self.index):
                    self.index += 1
                    return
                self.fail('"," or "}" was expected')
        if char == '[':
            self.index += 1
            self.skip()
            if self.text.startswith(']', self.index):
                self.index += 1
                return
            number = 0
            while True:
                self.value(path + (number,))
                number += 1
                self.skip()
                if self.text.startswith(',', self.index):
                    self.index += 1
                    continue
                if self.text.startswith(']', self.index):
                    self.index += 1
                    return
                self.fail('"," or "]" was expected')
        if char == '"':
            self.string()
            return
        end = self.index
        while end < len(self.text) and self.text[end] not in ' \t\r\n,]}':
            end += 1
        if end == self.index:
            self.fail('a value was expected')
        self.index = end

    def string(self):
        # The opening quote is at self.index; a backslash escapes the next character.
        start = self.index
        self.index += 1
        while self.index < len(self.text):
            char = self.text[self.index]
            if char == '\\':
                self.index += 2
                continue
            if char == '"':
                self.index += 1
                return json.loads(self.text[start:self.index])
            if char == '\n':
                break
            self.index += 1
        self.fail('a string is not closed on its line')


def load(text):
    """(data, lines) of a JSON document; raises JsonError (with .line) on invalid JSON."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonError(error.msg, error.lineno)
    scanner = Scanner(text)
    scanner.value(())
    return data, scanner.lines


def line_of(lines, pointer):
    """The line of a pointer, or of its nearest parent with a line; 1 when none has one."""
    while True:
        if pointer in lines:
            return lines[pointer]
        if not pointer:
            return 1
        pointer = pointer.rsplit('/', 1)[0]
