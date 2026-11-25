"""tools/wordlists.py: the common-word list and the verb list made from 12dicts, on a small archive of the same form,
and the committed lists' shape (plan/style.md §2.3: the 8,991 headwords of the bands 1 to 14, the first line names the list and its
license)."""

import contextlib
import hashlib
import io
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import wordlists  # noqa: E402

c_Frequency = '''----- 1 -----
be
    am, are, been, is, was, were
the
----- 2 -----
write
(April)
----- 12 -----
rare
'''
c_Lemmas = '''April
be
    am, are -> [are], been, being -> [being], is, was, were
clean
    cleaned, cleaner, cleanest, cleaning, cleanliness, cleanly, cleans
color
    colored -> [colored], colorful, coloring -> [coloring], colors, colour, coloured -> [colored], colours
frame
    framed, frames, framing
rare
    rarely, rarer, rarest
run
    ran, running, runs
set
    sets, setting
the
write
    writ -> [writ], writes, writing -> [writing], written, wrote
'''


def archive(folder):
    path = os.path.join(folder, '12dicts-test.zip')
    with zipfile.ZipFile(path, 'w') as file:
        file.writestr(wordlists.c_FrequencyList, c_Frequency)
        file.writestr(wordlists.c_LemmaList, c_Lemmas)
    with open(path, 'rb') as file:
        return path, hashlib.sha256(file.read()).hexdigest()


class WordListTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='wordlists-test-')
        self.archive, self.sha256 = archive(self.folder)
        self.texts = wordlists.read_archive(self.archive, self.sha256)

    def tearDown(self):
        helpers.remove_tree(self.folder)

    def test_common_words_are_the_bands_with_their_forms(self):
        lines = wordlists.common_words(self.texts, last_band=11)
        self.assertEqual(lines, ['be am are been being is was were', 'the', 'write writ writes writing written wrote', 'April'])

    def test_verbs_and_their_forms(self):
        verbs = {line.split('\t')[0]: line.split('\t') for line in wordlists.verbs(self.texts)}
        self.assertEqual(verbs['be'], ['be', 'is', 'am,are,was,were,been', 'being'])
        self.assertEqual(verbs['write'], ['write', 'writes', 'writ,written,wrote', 'writing'])
        self.assertEqual(verbs['clean'], ['clean', 'cleans', 'cleaned', 'cleaning'])  # no cleaner, cleanly
        self.assertEqual(verbs['color'], ['color', 'colors', 'colored', 'coloring'])  # colour is a spelling, no form
        self.assertEqual(verbs['set'], ['set', 'sets', 'set', 'setting'])  # the past is the base
        self.assertEqual(verbs['run'], ['run', 'runs', 'ran,run', 'running'])
        self.assertEqual(verbs['frame'][2], 'framed')
        self.assertNotIn('rare', verbs)
        self.assertNotIn('the', verbs)

    def test_another_archive_is_refused(self):
        with self.assertRaises(wordlists.ArchiveError) as raised:
            wordlists.read_archive(self.archive)
        self.assertIn('download it again', str(raised.exception))

    def test_check_finds_a_stale_list(self):
        data = os.path.join(self.folder, 'data')
        files = wordlists.outputs(self.texts)
        os.makedirs(data)
        for name, text in files.items():
            with open(os.path.join(data, name), 'w', encoding='utf-8', newline='\n') as file:
                file.write(text)
        self.assertEqual(wordlists.stale_files(files, data), [])
        with open(os.path.join(data, wordlists.c_VerbsFile), 'a', encoding='utf-8') as file:
            file.write('added\tby\thand\t-\n')
        self.assertEqual(wordlists.stale_files(files, data), [os.path.join(data, wordlists.c_VerbsFile)])

    def test_the_command_refuses_another_archive(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = wordlists.main(['check', '--archive', self.archive, '--data', self.folder])
        self.assertEqual(code, 2)  # the small archive is not 12dicts 6.0.2
        self.assertIn('SHA-256', output.getvalue())

    def test_the_committed_lists(self):
        with open(os.path.join(wordlists.c_Data, wordlists.c_CommonFile), encoding='utf-8') as file:
            lines = file.read().split('\n')
        self.assertIn('12dicts 6.0.2', lines[0])
        self.assertIn('public domain', lines[0])
        self.assertIn('12dicts-notice.txt', lines[0])
        headwords = [line for line in lines if line and not line.startswith('#')]
        self.assertIn('bands 1 to 14 ', lines[0])
        self.assertEqual(len(headwords), 8991)
        self.assertTrue(os.path.isfile(os.path.join(wordlists.c_Data, '12dicts-notice.txt')))
        with open(os.path.join(wordlists.c_Data, wordlists.c_VerbsFile), encoding='utf-8') as file:
            verbs = [line for line in file.read().split('\n') if line and not line.startswith('#')]
        self.assertTrue(all(len(line.split('\t')) == 4 for line in verbs))


if __name__ == '__main__':
    unittest.main()
