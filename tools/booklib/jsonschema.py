"""A JSON Schema (draft 2020-12) validator for the keywords the book's schemas use, with the standard library only.

Supported: type, enum, const, required, properties, additionalProperties, propertyNames, minProperties,
maxProperties, items, prefixItems, minItems, maxItems, uniqueItems, minLength, maxLength, pattern, minimum, maximum,
exclusiveMinimum, exclusiveMaximum, oneOf, anyOf and $ref to "#/$defs/..." (the editor's parameter schemas use the
annotation deprecated as well). Any other keyword raises SchemaError, so that a schema never silently checks less than
it says.

errors(value) gives (place, message) pairs with the place written for people ("/figures/0/id", "(the document)");
problems(value) gives the same with the raw JSON pointer ("" for the document), which booklib.jsonpos turns into a
line. A value that matches none of a oneOf's or anyOf's forms is reported once, with the problems of the form it came
closest to (one whose type it has, then the one with the fewest problems), so that the message says what to change.

Validator(schema, accept) takes a predicate: a value it accepts meets every schema (tools/tutorials.py passes the
$ref of a command step, which stands for any value).
"""

import re

c_Annotations = {'$schema', '$id', 'title', 'description', '$defs', 'default', 'examples', '$comment', 'deprecated'}
c_Keywords = {
    'type', 'enum', 'const', 'required', 'properties', 'additionalProperties', 'propertyNames', 'minProperties',
    'maxProperties', 'items', 'prefixItems', 'minItems', 'maxItems', 'uniqueItems', 'minLength', 'maxLength', 'pattern',
    'minimum', 'maximum', 'exclusiveMinimum', 'exclusiveMaximum', '$ref', 'oneOf', 'anyOf',
}


class SchemaError(Exception):
    pass


def type_matches(value, name):
    if name == 'object':
        return isinstance(value, dict)
    if name == 'array':
        return isinstance(value, list)
    if name == 'string':
        return isinstance(value, str)
    if name == 'boolean':
        return isinstance(value, bool)
    if name == 'null':
        return value is None
    if name == 'integer':
        return isinstance(value, int) and not isinstance(value, bool) or isinstance(value, float) and value.is_integer()
    if name == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise SchemaError('unknown type %r' % name)


def raw_pointer(path):
    return ''.join('/' + str(part).replace('~', '~0').replace('/', '~1') for part in path)


def pointer(path):
    return raw_pointer(path) or '(the document)'


def canonical(value):
    """A value's form for comparing JSON values: 1 and 1.0 are one number, true is no number."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return (type(value).__name__, value)
    if isinstance(value, (int, float)):
        return ('number', float(value))
    if isinstance(value, list):
        return ('array', tuple(canonical(item) for item in value))
    return ('object', tuple(sorted((key, canonical(item)) for key, item in value.items())))


class Validator:
    def __init__(self, schema, accept=None):
        self.schema = schema
        self.accept = accept

    def resolve(self, reference):
        if not reference.startswith('#/'):
            raise SchemaError('only local references are supported: %s' % reference)
        node = self.schema
        for part in reference[2:].split('/'):
            node = node[part.replace('~1', '/').replace('~0', '~')]
        return node

    def errors(self, value, schema=None, path=()):
        """Every problem of value as (JSON pointer, message), in document order."""
        return [(pointer(place), message) for place, message in self.check(value, self.schema if schema is None else schema, tuple(path))]

    def problems(self, value, schema=None, path=()):
        """Every problem of value as (raw JSON pointer, message): "" is the document."""
        return [(raw_pointer(place), message) for place, message in self.check(value, self.schema if schema is None else schema, tuple(path))]

    def check(self, value, schema, path):
        """Every problem as (path tuple, message), in document order."""
        if schema is True or (self.accept is not None and self.accept(value)):
            return []
        if schema is False:
            return [(path, 'no value is allowed here')]
        unknown = set(schema) - c_Keywords - c_Annotations
        if unknown:
            raise SchemaError('unsupported keywords %s at %s' % (sorted(unknown), pointer(path)))
        found = []
        if '$ref' in schema:
            found += self.check(value, self.resolve(schema['$ref']), path)
        for keyword in ('oneOf', 'anyOf'):
            if keyword in schema:
                found += self.forms(value, schema[keyword], path, keyword)
        if 'type' in schema:
            names = schema['type'] if isinstance(schema['type'], list) else [schema['type']]
            if not any(type_matches(value, name) for name in names):
                return found + [(path, 'must be of type %s' % ' or '.join(names))]
        if 'enum' in schema and value not in schema['enum']:
            found.append((path, 'must be one of %s' % ', '.join(map(repr, schema['enum']))))
        if 'const' in schema and value != schema['const']:
            found.append((path, 'must be %r' % (schema['const'],)))
        if isinstance(value, str):
            if len(value) < schema.get('minLength', 0):
                found.append((path, 'must hold at least %d characters' % schema['minLength']))
            if 'maxLength' in schema and len(value) > schema['maxLength']:
                found.append((path, 'must hold at most %d characters' % schema['maxLength']))
            if 'pattern' in schema and not re.search(schema['pattern'], value):
                found.append((path, '%r does not match %s' % (value, schema['pattern'])))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if 'minimum' in schema and value < schema['minimum']:
                found.append((path, 'must be at least %s' % schema['minimum']))
            if 'maximum' in schema and value > schema['maximum']:
                found.append((path, 'must be at most %s' % schema['maximum']))
            if 'exclusiveMinimum' in schema and value <= schema['exclusiveMinimum']:
                found.append((path, 'must be greater than %s' % schema['exclusiveMinimum']))
            if 'exclusiveMaximum' in schema and value >= schema['exclusiveMaximum']:
                found.append((path, 'must be less than %s' % schema['exclusiveMaximum']))
        if isinstance(value, dict):
            for name in schema.get('required', []):
                if name not in value:
                    found.append((path, 'needs "%s"' % name))
            if len(value) < schema.get('minProperties', 0):
                found.append((path, 'needs at least %d entries' % schema['minProperties']))
            if 'maxProperties' in schema and len(value) > schema['maxProperties']:
                found.append((path, 'holds at most %d entries' % schema['maxProperties']))
            properties = schema.get('properties', {})
            for name, item in value.items():
                if 'propertyNames' in schema:
                    for _, message in self.check(name, schema['propertyNames'], path):
                        found.append((path + (name,), 'the name: %s' % message))
                if name in properties:
                    found += self.check(item, properties[name], path + (name,))
                elif 'additionalProperties' in schema:
                    extra = schema['additionalProperties']
                    if extra is False:
                        found.append((path + (name,), 'is not a known field'))
                    else:
                        found += self.check(item, extra, path + (name,))
        if isinstance(value, list):
            if len(value) < schema.get('minItems', 0):
                found.append((path, 'needs at least %d items' % schema['minItems']))
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                found.append((path, 'holds at most %d items' % schema['maxItems']))
            if schema.get('uniqueItems') and len(set(canonical(item) for item in value)) < len(value):
                found.append((path, 'holds the same item twice'))
            prefix = schema.get('prefixItems', [])
            for index, item in enumerate(value):
                if index < len(prefix):
                    found += self.check(item, prefix[index], path + (index,))
                elif 'items' in schema:
                    found += self.check(item, schema['items'], path + (index,))
        return found

    def forms(self, value, forms, path, keyword):
        """The problems of a oneOf or anyOf: none when exactly one form (oneOf) or at least one (anyOf) matches."""
        if not isinstance(forms, list) or not forms:
            raise SchemaError('%s needs a list of forms at %s' % (keyword, pointer(path)))
        results = [self.check(value, form, path) for form in forms]
        matching = [index for index, problems in enumerate(results) if not problems]
        if keyword == 'oneOf' and len(matching) > 1:
            return [(path, 'matches %d of its forms; it must match exactly one' % len(matching))]
        if matching:
            return []
        # The closest form: one whose type and constant the value has, then the one with the fewest problems.
        def distance(problems):
            wrong_kind = any(place == path and (message.startswith('must be of type') or message.startswith('must be ')) for place, message in problems)
            return (wrong_kind, len(problems))
        closest = min(results, key=distance)
        titles = [form.get('title') for form in forms if isinstance(form, dict) and form.get('title')]
        named = ' (%s)' % '; '.join(titles) if len(titles) == len(forms) else ''
        first_place, first_message = closest[0]
        return [(path, 'is none of its %d forms%s; the closest form says: %s %s' % (len(forms), named, pointer(first_place), first_message))] + closest[1:]
