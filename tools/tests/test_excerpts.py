"""excerpts.py (plan/pipelines.md §3) against a small engine repository with history and a vendored library."""

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

# The tools and this folder as packages, however unittest was started: discover -s tools/tests -t tools, -t . or
# discover tools/tests (plan/pipelines.md writes the last one).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests import helpers  # noqa: E402
import excerpts
from booklib import markdown, repo

c_Source = """#include "Scene.h"

namespace Strata
{
	// Runs one frame.
	void Scene::OnUpdate(float deltaTime)
	{
		const char* text = "{ not a brace }";
#ifdef ST_DEBUG
		Check();
#endif
		if (deltaTime > 0.0f)
		{
			Step(deltaTime);
		}
	}

	void Scene::Step(float deltaTime);

	int Scene::Count(int a)
	{
		return a;
	}

	int Scene::Count(int a, int b)
	{
		return a + b;
	}
}
"""

c_Commands = """void RegisterThings(EditorCommandRegistry& registry)
{
	registry.Register({ "thing.make",
		"Makes a thing.",
		ObjectSchema({}),
		[](EditorContext& context, const nlohmann::json&)
		{
			return EditorCommandResult::Ok({ { "made", "(yes)" } });
		}, EditorCommandKind::Edit });

	registry.Register({ "thing.drop",
		"Drops it.",
		ObjectSchema({}),
		[](EditorContext&, const nlohmann::json&) { return EditorCommandResult::Ok({}); } });
}
"""

c_Notices = """# Third-Party Notices

| Library | Version | License | Shipped in games | Purpose |
| --- | --- | --- | --- | --- |
| [glm](https://github.com/g-truc/glm) | 1.0.3 | MIT | Yes | Math |
"""

c_Moved = '// A new first line.\n\n' + c_Source
c_Changed = c_Source.replace('Step(deltaTime);\n\t\t}', 'StepTwice(deltaTime);\n\t\t}')


def quiet(function, *arguments):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        code = function(list(arguments))
    return code, output.getvalue()


class ExcerptTests(unittest.TestCase):
    def setUp(self):
        self.engine_repo = helpers.TempEngine()
        self.glm = self.engine_repo.add_submodule('Strata/vendor/glm', {'glm/vec3.hpp': '#pragma once\n\nnamespace glm\n{\n\tstruct vec3\n\t{\n\t\tfloat x;\n\t};\n}\n'},
                                                  'https://github.com/g-truc/glm.git')
        self.first = self.engine_repo.commit({'Strata/src/Scene.cpp': c_Source, 'Strata/src/Commands.cpp': c_Commands, 'ThirdPartyNotices.md': c_Notices,
                                              'Strata/src/Version.h.in': '#define ST_VERSION "@V@"\n',
                                              'Strata/src/Scene.h': 'class Scene\n{\n\tfloat GetStep() const\n\t{\n\t\treturn 1.0f;\n\t}\n};\n'})
        self.book = helpers.TempBook(self.first)
        self.engine = repo.Engine(self.engine_repo.root)

    def tearDown(self):
        self.engine.close()
        self.book.cleanup()
        self.engine_repo.cleanup()

    def page(self, fences, kind='concept', page_id='core/time'):
        self.book.page(page_id, helpers.frontmatter(kind=kind, id=page_id) + '\n' + '\n\n'.join(fences) + '\n' + helpers.c_BottomStrip)
        return self.book.path('src/content/docs/%s.md' % page_id)

    def text(self, page_id='core/time'):
        return self.book.read('src/content/docs/%s.md' % page_id)

    def run_tool(self, *arguments):
        return quiet(excerpts.main, *(list(arguments) + ['--root', self.book.root, '--engine', self.engine_repo.root]))

    # fill and the draft forms (§3.3) ----------------------------------------------------------------------------------

    def test_a_symbol_becomes_its_lines_with_the_comment_above_and_keeps_its_anchor(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        text = self.text()
        # Lines 5-16, one tab less (the smallest indentation), the preprocessor lines at column 0 left as they are.
        self.assertIn('```cpp src="Strata/src/Scene.cpp#L5-L16" symbol="Scene::OnUpdate"\n// Runs one frame.\nvoid Scene::OnUpdate(float deltaTime)\n{\n', text)
        self.assertIn('\n#ifdef ST_DEBUG\n\tCheck();\n#endif\n', text)
        self.assertEqual(self.run_tool('check')[0], 0)
        # fill again changes nothing.
        self.assertIn('excerpts:', self.run_tool('check')[1])
        before = self.text()
        self.run_tool('fill')
        self.assertEqual(self.text(), before)

    def test_from_and_to_hold_no_double_quote(self):
        # The site's reader ends an attribute at an inner quote, escaped or not, and refuses the fence.
        for anchors in ('from="if (\\"x" to="Step(deltaTime);"', 'from="if (deltaTime" to="Step("a");"'):
            self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate" %s\n```' % anchors])
            code, output = self.run_tool('check')
            self.assertEqual(code, 1, output)
            self.assertIn('holds a double quote: the site\'s Markdown reader ends the attribute at it', output)
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate" from="if (deltaTime" to="Step(deltaTime);"\n```'])
        self.assertNotIn('holds a double quote', self.run_tool('check')[1])

    def test_from_and_to_choose_lines_inside_the_definition(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate" from="if (deltaTime" to="Step(deltaTime);"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        self.assertIn('src="Strata/src/Scene.cpp#L12-L14" from="if (deltaTime" to="Step(deltaTime);" symbol="Scene::OnUpdate"\nif (deltaTime > 0.0f)\n{\n\tStep(deltaTime);\n```', self.text())
        # A text that occurs twice inside the definition is refused, and the fence is left as it was.
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate" from="deltaTime" to="Step"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 1)
        self.assertIn('from="deltaTime" occurs 3 times inside the definition of Scene::OnUpdate', output)
        self.assertIn('the quote is left as it is', output)
        self.assertIn('src="Strata/src/Scene.cpp#Scene::OnUpdate" from="deltaTime"', self.text())

    def test_several_definitions_need_overload(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::Count"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 1)
        self.assertIn('"Scene::Count" has 2 definitions (lines 20, 25): add overload="<n>"', output)
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::Count" overload="2"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        self.assertIn('src="Strata/src/Scene.cpp#L25-L28" overload="2" symbol="Scene::Count"\nint Scene::Count(int a, int b)\n', self.text())
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::Count" overload="3"\n```'])
        self.assertIn('overload="3", but "Scene::Count" has 2 definitions', self.run_tool('fill')[1])

    def test_a_command_form_quotes_its_registration(self):
        self.page(['```cpp src="Strata/src/Commands.cpp" command="thing.make"\n```'])
        self.assertIn('the quote is a draft', self.run_tool('check')[1])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        text = self.text()
        self.assertIn('```cpp src="Strata/src/Commands.cpp#L3-L9" command="thing.make"\nregistry.Register({ "thing.make",\n', text)
        self.assertIn('}, EditorCommandKind::Edit });\n```', text)
        self.assertEqual(self.run_tool('check')[0], 0)
        self.page(['```cpp src="Strata/src/Commands.cpp" command="thing.missing"\n```'])
        self.assertIn('no Register( call holds "thing.missing",', self.run_tool('fill')[1])

    def test_fill_refuses_long_ranges_and_missing_files(self):
        long = self.engine_repo.commit({'Strata/src/Long.cpp': ''.join('int a%d;\n' % number for number in range(70))})
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % long)
        self.page(['```cpp src="Strata/src/Long.cpp#L1-L61"\n```', '```cpp src="Strata/src/Gone.cpp#L1-L5"\n```', '```cpp src="Strata/src/Version.h#L1"\n```',
                   '```cpp src="Strata/src/Scene.cpp#L20-L40"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 1)
        self.assertIn('would hold 61 lines (at most 60)', output)
        self.assertIn('Strata/src/Scene.cpp has 29 lines; the quote names L20-L40: write its draft form again and run fill', output)
        self.assertIn('Strata/src/Gone.cpp does not exist in the engine', output)
        self.assertIn('it exists only in builds, made from Strata/src/Version.h.in; quote that', output)

    def test_normalization_removes_the_smallest_indentation_only(self):
        self.assertEqual(excerpts.normalize(['\t\tint a;', '', '#ifdef X', '\t\t\tint b;', '\t\t#pragma once']),
                         ['int a;', '', '#ifdef X', '\tint b;', '#pragma once'])
        self.assertEqual(excerpts.normalize(['int a;', '\tint b;']), ['int a;', '\tint b;'])

    # sources (§3.2) ---------------------------------------------------------------------------------------------------

    def test_vendor_quotes_read_the_submodule_at_its_recorded_commit_and_need_their_credit(self):
        self.page(['```cpp src="vendor:glm/glm/vec3.hpp#glm::vec3"\n```'])
        code, output = self.run_tool('fill')
        self.assertIn('no definition of "glm::vec3"', output)
        self.assertIn('src/generated/vendor.json: written', output)
        self.page(['```cpp src="vendor:glm/glm/vec3.hpp#L5-L8"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        self.assertIn('src="vendor:glm/glm/vec3.hpp#L5-L8"\nstruct vec3\n{\n\tfloat x;\n};\n```', self.text())
        # fill writes the data the build's header needs (rulings-6, R26); check fails when it is stale.
        self.assertEqual(json.loads(self.book.read('src/generated/vendor.json')), {'pin': self.first, 'libraries': {'glm': {
            'name': 'glm', 'version': '1.0.3', 'license': 'MIT', 'repository': 'https://github.com/g-truc/glm', 'commit': self.glm}}})
        self.book.write('src/generated/vendor.json', '{"pin": "old", "libraries": {}}\n')
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('src/generated/vendor.json is stale: run python -I tools/excerpts.py fill', output)
        self.run_tool('fill')
        # appendix/credits is not written: a note in a draft, an error in a release.
        code, output = self.run_tool('check')
        self.assertEqual(code, 0, output)
        self.assertIn('note: vendor:glm: appendix/credits is not written yet, so the credit of glm (MIT) is not checked', output)
        code, output = self.run_tool('check', '--release')
        self.assertEqual(code, 1)
        self.assertIn('appendix/credits is not written, and a release needs it to credit glm (MIT)', output)
        self.book.page('appendix/credits', helpers.frontmatter(id='appendix/credits', kind='reference') + '\n- glm, by G-Truc, under its license.\n')
        self.assertIn('does not name glm with its license MIT on one line', self.run_tool('check')[1])
        self.book.page('appendix/credits', helpers.frontmatter(id='appendix/credits', kind='reference') + '\n| glm | 1.0.3 | MIT |\n')
        self.assertEqual(self.run_tool('check', '--release')[0], 0)
        # A library ThirdPartyNotices.md does not list, and an engine path into a submodule.
        self.page(['```cpp src="vendor:imgui/imgui.h#L1"\n```', '```cpp src="Strata/vendor/glm/glm/vec3.hpp#L1"\n```'])
        output = self.run_tool('check')[1]
        self.assertIn('Strata/vendor/imgui is not a submodule of the engine', output)
        self.assertIn('is inside the submodule Strata/vendor/glm: quote it as vendor:glm/glm/vec3.hpp', output)

    def test_a_vendor_library_must_be_in_the_engine_s_notices(self):
        engine = self.engine_repo.commit({'ThirdPartyNotices.md': '# Third-Party Notices\n'})
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % engine)
        self.page(['```cpp src="vendor:glm/glm/vec3.hpp#L5-L8"\n```'])
        self.run_tool('fill')
        self.assertIn('ThirdPartyNotices.md at %s does not list this library' % engine[:8], self.run_tool('check')[1])

    def test_book_files_and_the_hunks_of_patches(self):
        self.book.write('tutorials/world/wind/WindZone.cpp', 'struct WindZone\n{\n\tfloat Strength;\n};\n')
        patch = ('diff --git a/Strata/src/Scene.cpp b/Strata/src/Scene.cpp\n--- a/Strata/src/Scene.cpp\n+++ b/Strata/src/Scene.cpp\n'
                 '@@ -1,2 +1,3 @@\n #include "Scene.h"\n+#include "Wind.h"\n \n@@ -20,1 +21,1 @@\n-\tint Scene::Count(int a)\n+\tint Scene::Count(long a)\n')
        self.book.write('tutorials/world/wind.patch', patch)
        self.page(['```cpp src="book:tutorials/world/wind/WindZone.cpp#L1-L4"\n```', '```diff src="book:tutorials/world/wind.patch#hunk-2"\n```',
                   '```cpp src="book:tutorials/world/wind/Missing.cpp#L1"\n```', '```diff src="book:tutorials/world/wind.patch#hunk-3"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 1)
        self.assertIn('book:tutorials/world/wind/Missing.cpp does not exist in this repository', output)
        self.assertIn('the patch has 2 hunks, not 3: name a hunk from 1 to 2', output)
        text = self.text()
        self.assertIn('src="book:tutorials/world/wind/WindZone.cpp#L1-L4"\nstruct WindZone\n', text)
        self.assertIn('src="book:tutorials/world/wind.patch#hunk-2"\n-\tint Scene::Count(int a)\n+\tint Scene::Count(long a)\n```', text)
        # A hunk takes no mark; a book quote follows no pin.
        self.page(['```diff src="book:tutorials/world/wind.patch#hunk-1" mark="L1"\n #include "Scene.h"\n+#include "Wind.h"\n \n```'])
        self.assertIn('a hunk of a patch shows its changes with "+" and "-": remove mark', self.run_tool('check')[1])
        with self.assertRaises(excerpts.ExcerptError):
            excerpts.parse_source('Strata/src/Scene.cpp#hunk-1')

    # check (§3.5) -----------------------------------------------------------------------------------------------------

    def test_check_names_the_first_line_that_differs(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#L6-L7"\nvoid Scene::OnUpdate(float deltaTime)\n{ changed\n```'])
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('time.md:21: the quote differs from Strata/src/Scene.cpp', output)
        self.assertIn("(line L7): the page says '{ changed', the source '{'; run python -I tools/excerpts.py fill", output)

    def test_check_refuses_a_quote_that_starts_or_ends_with_a_blank_line(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#L2-L3"\n\nnamespace Strata\n```', '```cpp src="Strata/src/Scene.cpp#L1-L2"\n#include "Scene.h"\n\n```'])
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('src="Strata/src/Scene.cpp#L2-L3": the quote starts with a blank line, which Expressive Code does not draw, so its '
                      'line numbers and marks would be one line late: quote L3-L3 instead', output)
        self.assertIn('src="Strata/src/Scene.cpp#L1-L2": the quote ends with a blank line', output)

    def test_check_counts_internals_quotes_and_engine_paths_in_prose(self):
        self.book.page('world/ecs', helpers.frontmatter(kind='internals', id='world/ecs') + '\nSee `Strata/src/Scene.cpp:12`, `Strata/src/Missing.cpp`, '
                       '`Strata/vendor/glm/glm/vec3.hpp` and `Strata/vendor/glm/glm/gone.hpp`.\n\n```cpp src="Strata/src/Scene.cpp#L1"\n#include "Scene.h"\n```\n' + helpers.c_BottomStrip)
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('ecs.md:1: a page of kind internals quotes the engine at least 3 times; this one quotes it 1 time', output)
        self.assertIn('`Strata/src/Missing.cpp` does not exist in the engine', output)
        self.assertIn('`Strata/vendor/glm/glm/gone.hpp` does not exist', output)
        self.assertNotIn('`Strata/src/Scene.cpp` does not exist', output)
        self.assertNotIn('vec3.hpp` does not exist', output)

    def test_drafts_long_quotes_and_refused_markers_fail_the_check(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate"\n```', '```cpp src="Strata/src/Scene.cpp#L1-L61"\n```',
                   '```cpp src="Strata/src/Scene.cpp#L1-L2" {2} title="x" ins="y"\n#include "Scene.h"\n\n```',
                   '```cpp src="Strata/src/Scene.cpp#L1-L2" mark="L9"\n#include "Scene.h"\n\n```',
                   '```cpp src="Strata/src/Scene.cpp#L1-L2" mark="Scene"\n#include "Scene.h"\n\n```',
                   '```cpp mark="L2"\nint a;\n```'])
        code, output = self.run_tool('check')
        self.assertEqual(code, 1)
        self.assertIn('the quote is a draft (src="Strata/src/Scene.cpp#Scene::OnUpdate"): run python -I tools/excerpts.py fill', output)
        self.assertIn('the quote holds 61 lines; at most 60', output)
        self.assertIn("Expressive Code's line markers ({2}) count the block's lines", output)
        self.assertIn('title= is not used on a quote', output)
        self.assertIn('ins= is not used on a quote', output)
        self.assertIn('mark="L9" names lines outside the quote L1-L2', output)
        self.assertIn('mark="Scene" is not the file\'s lines', output)
        self.assertIn('mark="L…" names the lines of a quoted file, but this fence has no src=', output)

    def test_fill_lengthens_the_fence_when_the_quoted_lines_hold_a_fence(self):
        # AGENTS.md holds ```sh blocks; a line of ``` alone inside a ``` quote would close it and scramble the page.
        guide = '# Guide\n\nBuild:\n\n```sh\ncmake --preset windows\n```\n\nThen test.\n'
        engine = self.engine_repo.commit({'AGENTS.md': guide})
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % engine)
        self.page(['```markdown src="AGENTS.md#L1-L9"\n```', '```cpp src="Strata/src/Scene.cpp#L1"\n```'])
        code, output = self.run_tool('fill')
        self.assertEqual(code, 0, output)
        page = self.text()
        self.assertIn('````markdown src="AGENTS.md#L1-L9"\n# Guide\n', page)
        self.assertIn('Then test.\n````\n', page)
        self.assertEqual([fence.attributes['src'] for fence in markdown.fences(page) if 'src' in fence.attributes], ['AGENTS.md#L1-L9', 'Strata/src/Scene.cpp#L1'])
        self.assertEqual(self.run_tool('check')[0], 0)
        self.assertEqual(markdown.safe_marker(['```'], '`````'), '`````')

    def test_a_clone_without_the_pin_stops_with_exit_code_2(self):
        self.book.write('engine.pin', 'commit %s\nrelease 0.8.0\nprerelease yes\nrepository https://github.com/2042Third/GameEngine\n' % ('1' * 40))
        self.page(['```cpp src="Strata/src/Scene.cpp#L1"\n```'])
        code, output = self.run_tool('check')
        self.assertEqual(code, 2)
        self.assertIn('pipelines.md §1.4, check 1', output)
        self.assertEqual(quiet(excerpts.main, 'check', 'no/page', '--root', self.book.root, '--engine', self.engine_repo.root)[0], 2)

    def test_the_help_says_what_the_plan_says(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
            excerpts.main(['--help'])
        help_text = ' '.join(output.getvalue().split())
        for words in ('vendor:<lib>/<path>', 'book:<path>.patch#hunk-<n>', 'overload="<n>"', 'command="<name>"', 'moved-file', 'with --since <commit>',
                      'more than 60 lines', 'fewer than three quotes', 'smallest number of leading tabs', 'git grep -F', 'appendix/credits'):
            self.assertIn(words, help_text)

    # relocate (§3.5) --------------------------------------------------------------------------------------------------

    def test_relocate_same_moved_changed_and_missing(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate" mark="L14"\n```', '```cpp src="Strata/src/Scene.cpp#L1"\n```'])
        self.assertEqual(self.run_tool('fill')[0], 0)
        moved = self.engine_repo.commit({'Strata/src/Scene.cpp': c_Moved})
        code, output = self.run_tool('relocate', '--from', self.first, '--to', moved, '--write')
        self.assertEqual(code, 0, output)
        self.assertIn('moved: Strata/src/Scene.cpp#L5-L16 -> Strata/src/Scene.cpp#L7-L18', output)
        self.assertIn('src="Strata/src/Scene.cpp#L7-L18" mark="L16" symbol="Scene::OnUpdate"', self.text())
        changed = self.engine_repo.commit({'Strata/src/Scene.cpp': c_Changed})
        code, output = self.run_tool('relocate', '--from', moved, '--to', changed)
        self.assertEqual(code, 1)
        self.assertIn('changed: Strata/src/Scene.cpp#L7-L18: the text changed; Scene::OnUpdate is now at L5-L16', output)
        removed = self.engine_repo.commit({'Strata/src/Scene.cpp': None})
        code, output = self.run_tool('relocate', '--from', moved, '--to', removed)
        self.assertEqual(code, 1)
        self.assertIn('missing: Strata/src/Scene.cpp#L7-L18: Strata/src/Scene.cpp does not exist at', output)
        self.assertIn(': find what took its place at the new pin and quote that, or remove the quote', output)

    def test_relocate_finds_a_quote_in_another_file(self):
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate"\n```'])
        self.assertEqual(self.run_tool('fill')[0], 0)
        renamed = self.engine_repo.commit({'Strata/src/Scene.cpp': None, 'Strata/src/World/SceneUpdate.cpp': '// Moved here.\n' + c_Source})
        code, output = self.run_tool('relocate', '--from', self.first, '--to', renamed, '--write')
        self.assertEqual(code, 1, output)
        self.assertIn('moved-file: Strata/src/Scene.cpp#L5-L16 -> Strata/src/World/SceneUpdate.cpp#L6-L17: the quote is in another file now', output)
        self.assertIn('src="Strata/src/World/SceneUpdate.cpp#L6-L17"', self.text())

    def test_relocate_shifts_the_callouts_of_a_moved_quote(self):
        callouts = ('1. **Lines 5–6:** the comment and the head.\n2. **Line 7:** the frame begins.\n'
                    '3. **Lines 2-3:** outside the quote, left alone.\n\n## Next\n\n4. **Line 6:** under the next heading.')
        self.page(['```cpp src="Strata/src/Scene.cpp#Scene::OnUpdate"\n```\n\n' + callouts])
        self.assertEqual(self.run_tool('fill')[0], 0)
        moved = self.engine_repo.commit({'Strata/src/Scene.cpp': c_Moved})
        code, output = self.run_tool('relocate', '--from', self.first, '--to', moved, '--write')
        self.assertEqual(code, 0, output)
        text = self.text()
        self.assertIn('1. **Lines 7–8:** the comment and the head.\n2. **Line 9:** the frame begins.\n'
                      '3. **Lines 2-3:** outside the quote, left alone.', text)
        self.assertIn('4. **Line 6:** under the next heading.', text)
        # Without --write nothing changes.
        self.assertEqual(self.run_tool('relocate', '--from', moved, '--to', self.first)[0], 0)
        self.assertIn('**Lines 7–8:**', self.text())

    def test_relocate_finds_a_quote_whose_preprocessor_lines_were_indented(self):
        # Filled, the body keeps an indented #define one tab less; normalized once more, the body would lose a tab it
        # needs, so the quote must be compared as it was filled.
        source = 'namespace A\n{\n\tnamespace B\n\t{\n\t\tint F()\n\t\t{\n#if X\n\t#define Y 1\n#endif\n\t\t\treturn 1;\n\t\t}\n\t}\n}\n'
        start = self.engine_repo.commit({'Strata/src/Define.cpp': source})
        self.book.write('engine.pin', self.book.read('engine.pin').replace(self.first, start))
        self.page(['```cpp src="Strata/src/Define.cpp#L5-L11"\n```'])
        self.assertEqual(self.run_tool('fill')[0], 0)
        self.assertIn('\tint F()\n\t{\n#if X\n#define Y 1\n#endif\n\t\treturn 1;\n\t}\n```', self.text())
        moved = self.engine_repo.commit({'Strata/src/Define.cpp': '// First.\n' + source})
        code, output = self.run_tool('relocate', '--from', start, '--to', moved)
        self.assertIn('moved: Strata/src/Define.cpp#L5-L11 -> Strata/src/Define.cpp#L6-L12', output)

    def test_shift_marks(self):
        self.assertEqual(excerpts.shift_marks('cpp src="a#L1-L9" mark="L2,L4-L5" {x}', 3), 'cpp src="a#L1-L9" mark="L5,L7-L8" {x}')
        self.assertEqual(excerpts.shift_marks('cpp mark=L2', -1), 'cpp mark="L1"')
        self.assertEqual(excerpts.shift_marks('cpp mark="2"', 3), 'cpp mark="2"')

    # list --since -----------------------------------------------------------------------------------------------------

    def test_list_since_a_commit_of_the_book(self):
        book_git = lambda *arguments: subprocess.run(['git', '-C', self.book.root] + list(arguments), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for arguments in (('init', '-q'), ('config', 'user.email', 'test@example.com'), ('config', 'user.name', 'Test'), ('config', 'commit.gpgsign', 'false')):
            book_git(*arguments)
        self.page(['```cpp src="Strata/src/Scene.cpp#L1"\n#include "Scene.h"\n```', '```cpp src="Strata/src/Scene.h#L3-L6"\n```'])
        book_git('add', '-A')
        book_git('commit', '-q', '-m', 'first')
        since = subprocess.run(['git', '-C', self.book.root, 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode().strip()
        self.page(['```cpp src="Strata/src/Scene.cpp#L1"\n#include "Scene.h"\n```', '```cpp src="Strata/src/Scene.h#L3-L7"\n```'])
        code, output = quiet(excerpts.main, 'list', '--root', self.book.root)
        self.assertEqual(output.count('src/content/docs/core/time.md:'), 2)
        code, output = quiet(excerpts.main, 'list', '--since', since, '--root', self.book.root)
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), 'src/content/docs/core/time.md:23: Strata/src/Scene.h#L3-L7')
        self.assertEqual(quiet(excerpts.main, 'list', '--since', 'nothing-here', '--root', self.book.root)[0], 2)


if __name__ == '__main__':
    unittest.main()
