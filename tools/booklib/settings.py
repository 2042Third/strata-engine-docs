"""The deployment's values of site.json at the repository's root (rulings 6, R24): the base path, the origin and the
copyright line. The build reads the same file through src/lib/settings.mjs; both apply the same rules to a base and
an origin, and tools/tests/fixtures/settings-cases.json holds the cases both are tested on.

    {"base": "/strata-engine-docs", "origin": "https://<host>", "copyright": {"holder": "2042Third", "year": 2026}}

No other file of the repository writes the origin, this one included (tools/lint.py, rule literal-origin): the address
is site.json's, and code and tests that need one read it from there or pass https://example.com.
"""

import json
import os
import re
from urllib.parse import urlsplit

c_File = 'site.json'


class SettingsError(Exception):
    pass


def normalize_base(value):
    """A base path as "/a/b" (no trailing slash), or "" for the root of the host, written "/". An empty value is
    refused rather than read as the root."""
    text = str(value if value is not None else '').strip()
    if text == '':
        raise SettingsError('the base is empty: write / for the root of the host')
    if text == '/':
        return ''
    if not text.startswith('/'):
        raise SettingsError('the base must start with "/": %s' % json.dumps(value))
    if text.startswith('//'):
        raise SettingsError('the base must be a path, not a host: %s' % json.dumps(value))
    if not re.match(r'^[A-Za-z0-9/._~-]+$', text):
        raise SettingsError('the base may hold only letters, digits and / . _ ~ -: %s' % json.dumps(value))
    base = text[:-1] if text.endswith('/') else text
    segments = base.split('/')[1:]
    if any(segment == '' for segment in segments):
        raise SettingsError('the base has an empty segment ("//"): %s' % json.dumps(value))
    if any(segment in ('.', '..') for segment in segments):
        raise SettingsError('the base must not contain . or .. segments: %s' % json.dumps(value))
    return base


def normalize_origin(value):
    """An origin as "https://host[:port]": http or https, with no path, query or fragment."""
    text = str(value if value is not None else '')
    try:
        parts = urlsplit(text)
        port = parts.port
    except ValueError:
        raise SettingsError('the origin must be an absolute URL such as https://example.com: %s' % json.dumps(value))
    if parts.scheme not in ('http', 'https') or not parts.hostname:
        raise SettingsError('the origin must be an absolute http or https URL such as https://example.com: %s' % json.dumps(value))
    if parts.path not in ('', '/') or parts.query or parts.fragment or '?' in text or '#' in text:
        raise SettingsError('the origin holds no path: put the path in the base: %s' % json.dumps(value))
    if parts.username or parts.password:
        raise SettingsError('the origin holds no user name or password: %s' % json.dumps(value))
    default = {'http': 80, 'https': 443}[parts.scheme]
    host = '[%s]' % parts.hostname if ':' in parts.hostname else parts.hostname
    return '%s://%s%s' % (parts.scheme, host, '' if port in (None, default) else ':%d' % port)


def release_origin_problem(origin):
    """Why a release build cannot use this origin (rulings 6, R24), or None: it is https, names neither this machine
    nor the placeholder, and carries no path."""
    parts = urlsplit(origin)
    if parts.scheme != 'https':
        return 'a release is served over https, not from %s' % origin
    if parts.hostname in ('localhost', '127.0.0.1'):
        return 'a release is not served from this machine (%s)' % origin
    if parts.hostname == 'example.com':
        return '%s is the placeholder that tests use: a release names the real origin' % origin
    if parts.path not in ('', '/'):
        return 'the origin %s carries a path: put it in the base' % origin
    return None


def read_site(root):
    """site.json's values: {"base", "origin", "copyright"}, the base and the origin normalized."""
    path = os.path.join(root, c_File)
    try:
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        raise SettingsError('%s does not exist: it holds the base, the origin and the copyright line (rulings 6, R24)' % c_File)
    except (OSError, ValueError) as error:
        raise SettingsError('%s cannot be read: %s' % (c_File, error))
    if not isinstance(data, dict):
        raise SettingsError('%s holds an object with base, origin and copyright' % c_File)
    unknown = sorted(set(data) - {'base', 'origin', 'copyright'})
    if unknown:
        raise SettingsError('%s: unknown keys %s: the keys are base, origin and copyright' % (c_File, ', '.join(unknown)))
    copyright = data.get('copyright')
    if not isinstance(copyright, dict) or not isinstance(copyright.get('holder'), str) or not copyright['holder'].strip() \
            or not isinstance(copyright.get('year'), int) or isinstance(copyright.get('year'), bool):
        raise SettingsError('%s: copyright is {"holder": "<name>", "year": <year>}' % c_File)
    return {'base': normalize_base(data.get('base')), 'origin': normalize_origin(data.get('origin')),
            'copyright': {'holder': copyright['holder'], 'year': copyright['year']}}
