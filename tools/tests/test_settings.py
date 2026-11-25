"""tools/booklib/settings.py: site.json's base, origin and copyright (rulings 6, R24), on the cases the build's
src/lib/settings.mjs is tested on too (tools/tests/fixtures/settings-cases.json)."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
from booklib import settings  # noqa: E402

with open(os.path.join(helpers.c_Fixtures, 'settings-cases.json'), encoding='utf-8') as file:
    c_Cases = json.load(file)


class SettingsTests(unittest.TestCase):
    def test_bases(self):
        for case in c_Cases['base']:
            with self.subTest(value=case['value']):
                if case.get('error'):
                    self.assertRaises(settings.SettingsError, settings.normalize_base, case['value'])
                else:
                    self.assertEqual(settings.normalize_base(case['value']), case['base'])

    def test_origins(self):
        for case in c_Cases['origin']:
            with self.subTest(value=case['value']):
                if case.get('error'):
                    self.assertRaises(settings.SettingsError, settings.normalize_origin, case['value'])
                else:
                    self.assertEqual(settings.normalize_origin(case['value']), case['origin'])

    def test_release_origins(self):
        for case in c_Cases['release']:
            with self.subTest(origin=case['origin']):
                self.assertEqual(settings.release_origin_problem(case['origin']) is not None, case['refused'])

    def test_site_json(self):
        root = tempfile.mkdtemp(prefix='settings-test-')
        try:
            with self.assertRaises(settings.SettingsError) as raised:
                settings.read_site(root)
            self.assertIn('site.json does not exist', str(raised.exception))
            path = os.path.join(root, 'site.json')
            values = {'base': '/strata-engine-docs/', 'origin': 'https://Books.Example.org/', 'copyright': {'holder': 'The owner', 'year': 2026}}
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(values, file)
            self.assertEqual(settings.read_site(root), {'base': '/strata-engine-docs', 'origin': 'https://books.example.org',
                                                        'copyright': {'holder': 'The owner', 'year': 2026}})
            for broken in ({'base': '/a', 'origin': 'https://a.org', 'copyright': {'holder': '', 'year': 2026}},
                           {'base': '/a', 'origin': 'https://a.org', 'copyright': {'holder': 'x', 'year': '2026'}},
                           {'base': '/a', 'origin': 'https://a.org/x', 'copyright': {'holder': 'x', 'year': 2026}},
                           {'base': '/a', 'origin': 'https://a.org', 'copyright': {'holder': 'x', 'year': 2026}, 'site': 'x'}):
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(broken, file)
                with self.subTest(broken=broken):
                    self.assertRaises(settings.SettingsError, settings.read_site, root)
        finally:
            shutil.rmtree(root)


if __name__ == '__main__':
    unittest.main()
