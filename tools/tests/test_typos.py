"""The spelling settings (_typos.toml): quotes of the engine are not spell-checked, everything around them is.

Runs the pinned typos (tools/bootstrap.py puts it into .tools/) on pages written into a temporary folder, with the
repository's settings copied beside them."""

import glob
import os
import re
import shutil
import subprocess
import tempfile
import unittest

c_Root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_typos():
    found = shutil.which('typos')
    if found:
        return found
    for candidate in sorted(glob.glob(os.path.join(c_Root, '.tools', 'typos-*', 'typos*'))):
        if os.path.basename(candidate) in ('typos', 'typos.exe'):
            return candidate
    return None


# An indented quote in a list item, prose after it, an unquoted fence, and a quote whose lines hold a fence of their
# own (fill writes it with four backticks). Misspellings inside quotes are the engine's text and are not reported.
# The misspelt words are put together at run time, so that the repository's own spelling check passes this file.
c_Page = '''Intro.

1. A step.

   ```cpp src="Strata/a.cpp#L1-L2"
   int {receive};
   ```

   This {sentence} follows the quote.

   ```json
   {{}}
   ```

````markdown src="AGENTS.md#L1-L5"
Build it:

```sh
cmake --preset {windows}
```
````

The last {sentence}.
'''.format(receive='re' + 'cieve', sentence='sen' + 'tense', windows='wind' + 'wos')


@unittest.skipUnless(find_typos(), 'needs typos (python tools/bootstrap.py downloads it into .tools/)')
class TyposSettingsTests(unittest.TestCase):
    def test_quotes_are_skipped_and_the_prose_around_them_is_checked(self):
        folder = tempfile.mkdtemp(prefix='typos-')
        try:
            with open(os.path.join(c_Root, '_typos.toml'), encoding='utf-8') as file:
                settings = file.read()
            # The temporary folder may lie in .tools/, which the settings exclude for the repository.
            settings = re.sub(r'(?m)^\s*"\.tools/",\n', '', settings)
            with open(os.path.join(folder, '_typos.toml'), 'w', encoding='utf-8', newline='\n') as file:
                file.write(settings)
            with open(os.path.join(folder, 'page.md'), 'w', encoding='utf-8', newline='\n') as file:
                file.write(c_Page)
            result = subprocess.run([find_typos(), '--format', 'brief', 'page.md'], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = result.stdout.decode('utf-8', 'replace')
            lines = sorted(int(match) for match in re.findall(r'page\.md:(\d+):', output))
            self.assertEqual(lines, [9, 23], output)
        finally:
            shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
