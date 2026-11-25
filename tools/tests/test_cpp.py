"""Tests of tools/booklib/cpp.py: the tokenizer, brackets, string literals, comments, struct members and constant
expressions that the reference's parsed routes read the engine with."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from booklib import cpp  # noqa: E402


class TokenizeTests(unittest.TestCase):
    def test_strings_are_decoded_and_adjacent_ones_join(self):
        source = cpp.tokenize('auto a = "x\\"y" "\\xE2\\x96\\xB8 z\\n";\nauto b = R"(raw "text")";\nauto c = u8"\\101";\n')
        strings = [token for token in source.tokens if token.kind == 'str']
        self.assertEqual([token.value for token in strings], ['x"y', '\u25b8 z\n', 'raw "text"', 'A'])
        self.assertEqual(cpp.string_at(source.tokens, source.tokens.index(strings[0])), ('x"y\u25b8 z\n', source.tokens.index(strings[1]) + 1))
        self.assertEqual(cpp.strings(source.tokens, 0, len(source.tokens)), [('x"y\u25b8 z\n', 1), ('raw "text"', 2), ('A', 3)])

    def test_comments_stand_beside_the_tokens_with_their_lines(self):
        text = ('// first line\n// second line\nint a = 1; // trailing\n\n/*\n * A block\n * comment.\n */\nint b;\n'
                '////////\n// After a ruler\nint c;\n')
        source = cpp.tokenize(text)
        self.assertNotIn('first', [token.text for token in source.tokens])
        self.assertEqual(cpp.comment_before(source, 3), 'first line second line')
        self.assertEqual(cpp.comment_on(source, 3), 'trailing')
        self.assertEqual(cpp.comment_before(source, 9), 'A block comment.')
        self.assertEqual(cpp.comment_before(source, 12), 'After a ruler')
        self.assertEqual(cpp.comment_before(source, 4), '')

    def test_preprocessor_lines_are_one_token_with_their_continuations(self):
        source = cpp.tokenize('#define A(x) \\\n\tB(x)\nint a = A(1);\n#  include <x>\n')
        directives = [token for token in source.tokens if token.kind == 'pp']
        self.assertEqual(len(directives), 2)
        self.assertIn('B(x)', directives[0].text)
        self.assertEqual(directives[1].line, 4)
        self.assertEqual([token.text for token in source.tokens if token.kind != 'pp'][:3], ['int', 'a', '='])

    def test_brackets_lists_and_spelling(self):
        source = cpp.tokenize('f({ "a", g(1, 2) }, [x, y](int z) { return z; }, std::pair<int, int>{});')
        tokens = source.tokens
        self.assertEqual(cpp.match(tokens, 1), len(tokens) - 2)
        parts = cpp.split_top(tokens, 2, len(tokens) - 2)
        self.assertEqual(len(parts), 4)  # commas in template arguments split: callers join what follows
        self.assertEqual(cpp.spelled(source, parts[0][0], parts[0][1] - 1), '{ "a", g(1, 2) }')
        angle = [index for index, token in enumerate(tokens) if token.text == '<'][0]
        self.assertEqual(tokens[cpp.match_angle(tokens, angle)].text, '>')
        multiline = cpp.tokenize('int  f(int a, /* why */\n\t\tint b);')
        self.assertEqual(cpp.spelled(multiline, 0, len(multiline.tokens) - 2), 'int f(int a, int b)')


class StructTests(unittest.TestCase):
    c_Text = """
	struct Spec
	{
		std::string Name = "R"; // Its name
		// Lights per frame.
		uint32_t MaxLights = 4096;
		glm::uvec3 Grid = { 16, 9, 24 };
		float Values[4] = {};
		void (*Callback)(int value);
		void Validate() const;
		bool Ready() const { return true; }
		enum class Mode : uint8_t
		{
			A,
			B
		};
		struct Inner
		{
			int Hidden = 0;
		};
	public:
		Mode Kind = Mode::A;
	};
	"""

    def test_data_members_with_their_comments(self):
        members = cpp.struct_members(cpp.tokenize(self.c_Text), 'Spec')
        self.assertEqual([member['name'] for member in members], ['Name', 'MaxLights', 'Grid', 'Values', 'Callback', 'Kind'])
        by_name = {member['name']: member for member in members}
        self.assertEqual(by_name['Name']['comment'], 'Its name')
        self.assertEqual(by_name['MaxLights']['comment'], 'Lights per frame.')
        self.assertEqual(by_name['MaxLights']['default'], '4096')
        self.assertEqual(by_name['Grid']['default'], '{ 16, 9, 24 }')
        self.assertEqual(by_name['Kind']['type'], 'Mode')
        self.assertIsNone(cpp.struct_members(cpp.tokenize(self.c_Text), 'Missing'))


class EvaluateTests(unittest.TestCase):
    def test_constant_expressions(self):
        cases = {"1u << 21": 2097152, "512 * 1024": 524288, "1'000'000.0f": 1000000.0, "(1 << 27) - 1": 134217727, '0xFFFFF': 1048575,
                 'static_cast<size_t>(4096)': 4096, 'size_t { 1 } << 53': 1 << 53, '1.0e-3f': 0.001, '-5': -5, '7 / 2': 3, '7.0 / 2': 3.5,
                 'true': 1, 'c_Other * 2': 6}
        for text, value in cases.items():
            self.assertEqual(cpp.evaluate(text, {'c_Other': 3}), value, text)
        for text in ('entt::entt_traits<entt::entity>::entity_mask', 'f(2)', '1 +', '"text"', 'c_Unknown'):
            self.assertIsNone(cpp.evaluate(text), text)


if __name__ == '__main__':
    unittest.main()
