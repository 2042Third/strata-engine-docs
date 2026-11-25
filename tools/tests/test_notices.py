"""notices.py (plan/pipelines.md §15; rulings 6, R22 and R26): the three sections of public/third-party-notices.txt,
the license texts named once, the checks on the list and the built site, and what each --sections reads."""

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import notices  # noqa: E402

c_MitBody = ('Permission is hereby granted, free of charge, to any person obtaining a copy of this software.\n\n'
             'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.\n')
c_Notices = '''# Third-Party Notices

| Library | Version | License | Shipped in games | Purpose |
| --- | --- | --- | --- | --- |
| [EnTT](https://github.com/skypjack/entt) | 3.16.0 | MIT | Yes | Entity-component system |

## Code derived from other projects

| Project | Version | License | Strata's files | What was derived |
| --- | --- | --- | --- | --- |
| [lab](https://github.com/example/lab) | as of 2026-11-03 | MIT | `Strata/shaders/Include/March.slang`, `Include/Field.slang` | the march |
| [other](https://github.com/example/other) | 1.0 | MIT | `Strata/src/Other.cpp` | nothing quoted |

lab:

```
MIT License

Copyright (c) 2026 Lab Author

%s```

other:

```
Copyright (c) 2020 Other

%s```
''' % (c_MitBody, c_MitBody)


class NoticesTests(unittest.TestCase):
    def setUp(self):
        self.engine = helpers.TempEngine()
        self.engine.add_submodule('Strata/vendor/entt', {'LICENSE': 'The MIT License (MIT)\n\nCopyright (c) 2017-2025 Michele Caini\n\n' + c_MitBody,
                                                         'src/entt.hpp': 'int a;\nint b;\n'}, 'https://github.com/skypjack/entt.git')
        pin = self.engine.commit({'ThirdPartyNotices.md': c_Notices, 'Strata/shaders/Include/March.slang': 'a\nb\n',
                                  'Strata/shaders/Include/Field.slang': 'c\n', 'Strata/src/Other.cpp': 'd\n',
                                  'Samples/Tetris/CREDITS.md': '# Credits\n\nThe blocks are Strata\'s.\n'})
        self.book = helpers.TempBook(pin_commit=pin)
        self.book.page('core/time', '---\nid: core/time\n---\n\n```cpp src="vendor:entt/src/entt.hpp#L1-L2"\nint a;\nint b;\n```\n\n'
                       '```cpp src="Strata/shaders/Include/Field.slang#L1-L1"\nc\n```\n')
        self.book.write('src/content/figures/core/time.json', json.dumps({'figures': [{'id': 'a', 'project': {'sample': 'Tetris'}}]}))
        self.book.write('node_modules/katex/LICENSE', 'The MIT License (MIT)\n\nCopyright (c) 2013-2020 Khan Academy\n\n' + c_MitBody)
        self.book.write('node_modules/other/LICENSE.md', 'Copyright (c) 2023 Someone Else\n\n' + c_MitBody + '\n# Bundled\nmore\n')
        self.lock = {'name': 'book', 'lockfileVersion': 3, 'packages': {'node_modules/katex': {'version': '0.16.47', 'license': 'MIT'},
                                                                         'node_modules/other': {'version': '1.0.0', 'license': 'MIT'}}}
        self.write_lock()
        self.data = {'components': [
            {'name': 'KaTeX', 'package': 'katex', 'version': '0.16.47', 'license': 'MIT', 'copyright': ['Copyright (c) 2013-2020 Khan Academy'],
             'licenseFile': 'katex/LICENSE', 'files': ['_astro/KaTeX_*']},
            {'name': 'Other', 'package': 'other', 'version': '1.0.0', 'license': 'MIT', 'copyright': ['Copyright (c) 2023 Someone Else'],
             'licenseFile': 'other/LICENSE.md', 'licenseUntil': '# Bundled', 'files': ['_astro/page.*.js']}],
            'own': {'why': 'the site', 'files': ['_astro/Own.*.js']},
            'shows': [{'name': 'Fox', 'license': 'CC-BY-4.0', 'copyright': ['© 2014, tomkranis.'], 'source': 'https://example.com/fox'}]}
        self.write_list()

    def tearDown(self):
        self.book.cleanup()
        self.engine.cleanup()

    def write_lock(self):
        self.book.write('package-lock.json', json.dumps(self.lock))

    def write_list(self):
        self.book.write('tools/data/notices.json', json.dumps(self.data, ensure_ascii=False))

    def run_tool(self, *arguments, engine=True):
        output = io.StringIO()
        extra = ['--engine', self.engine.root] if engine else []
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = notices.main(list(arguments) + ['--root', self.book.root] + extra)
        return code, output.getvalue()

    def test_write_holds_the_three_sections_and_each_text_once(self):
        code, output = self.run_tool('write')
        self.assertEqual(code, 0, output)
        text = self.book.read('public/third-party-notices.txt')
        for line in ('==== A. What this site ships ====', '==== B. What this book quotes ====',
                     '==== C. What this book shows and gives out ====', '==== License texts ===='):
            self.assertIn('\n%s\n' % line, text)
        self.assertIn('  Copyright (c) 2013-2020 Khan Academy\n', text)
        self.assertIn('EnTT (vendor:entt)\n', text)
        self.assertIn('  Copyright (c) 2017-2025 Michele Caini\n', text)
        # The derived project whose file a page quotes, with the relative entry resolved against the full path before it.
        self.assertIn('lab\n  Code derived from it that the book quotes: Strata/shaders/Include/Field.slang\n', text)
        self.assertNotIn('other\n', text)
        self.assertIn('Samples/Tetris/CREDITS.md at the engine', text)
        self.assertIn('    The blocks are Strata\'s.\n', text)
        self.assertIn('Fox\n  License: CC-BY-4.0\n  © 2014, tomkranis.\n', text)
        self.assertNotIn('# Bundled', text)  # licenseUntil
        # KaTeX's and EnTT's files hold the same text once their copyright lines are out; the others are their own.
        names = notices.c_TextReference.findall(text)
        self.assertEqual(len(set(names)), 3)
        self.assertEqual(len([line for line in text.split('\n') if line.startswith('---- text ')]), 3)
        self.assertNotIn('Copyright', text.split('==== License texts ====')[-1])
        for sections in ([], ['--sections', 'A'], ['--sections', 'BC']):
            code, output = self.run_tool('check', *sections)
            self.assertEqual(code, 0, output)

    def test_a_stale_section_fails_only_the_check_that_reads_it(self):
        self.run_tool('write')
        text = self.book.read('public/third-party-notices.txt')
        self.book.write('public/third-party-notices.txt', text.replace('Michele Caini', 'Someone'))
        self.assertEqual(self.run_tool('check', '--sections', 'A', engine=False)[0], 0)
        code, output = self.run_tool('check', '--sections', 'BC')
        self.assertEqual(code, 1)
        self.assertIn('section B (What this book quotes) is not what write writes', output)
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('public/third-party-notices.txt:', output)
        self.book.write('public/third-party-notices.txt', text.replace(c_MitBody.split('\n')[0], 'Changed.', 1))
        code, output = self.run_tool('check', '--sections', 'A', engine=False)
        self.assertEqual(code, 1)
        self.assertIn('the license text', output)

    def test_another_version_in_the_lock_fails_and_write_refuses(self):
        self.run_tool('write')
        self.lock['packages']['node_modules/katex']['version'] = '0.16.48'
        self.write_lock()
        code, output = self.run_tool('check', '--sections', 'A', engine=False)
        self.assertEqual(code, 1)
        self.assertIn('the list records katex 0.16.47, and package-lock.json has 0.16.48', output)
        before = self.book.read('public/third-party-notices.txt')
        code, output = self.run_tool('write')
        self.assertEqual(code, 1)
        self.assertIn('nothing written', output)
        self.assertEqual(self.book.read('public/third-party-notices.txt'), before)

    def test_a_license_outside_the_allowlist_or_a_copyright_line_not_in_its_file_fails(self):
        self.data['components'][0]['license'] = 'GPL-3.0'
        self.data['components'][1]['copyright'] = ['Copyright (c) 2023 Somebody']
        self.write_list()
        code, output = self.run_tool('write')
        self.assertEqual(code, 1)
        self.assertIn('the license GPL-3.0 is outside the allowlist', output)
        self.assertIn('the copyright line "Copyright (c) 2023 Somebody" is not in node_modules/other/LICENSE.md', output)

    def test_the_built_site_s_fonts_scripts_and_webassembly_need_a_component(self):
        self.run_tool('write')
        dist = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, dist)
        for name in ('_astro/KaTeX_Main-Regular.abc.woff2', '_astro/page.abc.js', '_astro/Own.abc.js', '_astro/style.css',
                     'pagefind/wasm.en.pagefind', 'fonts/inter.woff2'):
            os.makedirs(os.path.join(dist, os.path.dirname(name)), exist_ok=True)
            open(os.path.join(dist, name), 'w').close()
        code, output = self.run_tool('check', '--sections', 'A', '--dist', dist, engine=False)
        self.assertEqual(code, 1)
        self.assertIn('the font fonts/inter.woff2, which no component', output)
        self.assertIn('the WebAssembly file pagefind/wasm.en.pagefind', output)
        self.assertNotIn('page.abc.js', output)
        self.assertNotIn('Own.abc.js', output)
        self.assertNotIn('style.css', output)
        os.remove(os.path.join(dist, 'fonts', 'inter.woff2'))
        os.remove(os.path.join(dist, 'pagefind', 'wasm.en.pagefind'))
        self.assertEqual(self.run_tool('check', '--sections', 'A', '--dist', dist, engine=False)[0], 0)
        self.assertEqual(self.run_tool('check', '--sections', 'A', '--dist', os.path.join(dist, 'missing'), engine=False)[0], 2)

    def test_each_set_of_sections_reads_only_its_sources(self):
        self.run_tool('write')
        helpers.remove_tree(self.book.path('node_modules'))
        code, output = self.run_tool('check', '--sections', 'A', engine=False)
        self.assertEqual(code, 2)
        self.assertIn('node_modules does not exist', output)
        self.assertEqual(self.run_tool('check', '--sections', 'BC')[0], 0)
        code, output = notices_main_with_engine(self.book.root, os.path.join(self.engine.root, 'missing'))
        self.assertEqual(code, 2)
        self.assertEqual(self.run_tool('check', '--sections', 'D')[0], 2)


def notices_main_with_engine(root, engine):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = notices.main(['check', '--sections', 'BC', '--root', root, '--engine', engine])
    return code, output.getvalue()


if __name__ == '__main__':
    unittest.main()
