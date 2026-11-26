import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseSource, relativeMarks } from '../excerpts.mjs';
import { bottomStrip, c_BottomStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const fence = (meta, lines) => `\`\`\`cpp ${meta}\n${lines.join('\n')}\n\`\`\``;
const lines = (count) => Array.from({ length: count }, (_, index) => `int line${index};`);

test('parseSource reads lines, single lines and symbols, and rejects the rest', () => {
	assert.deepEqual(parseSource('Strata/a.cpp#L10-L20'), { namespace: 'engine', path: 'Strata/a.cpp', start: 10, end: 20 });
	assert.deepEqual(parseSource('Strata/a.cpp#L7'), { namespace: 'engine', path: 'Strata/a.cpp', start: 7, end: 7 });
	assert.deepEqual(parseSource('Strata/a.cpp#Scene::OnUpdate'), { namespace: 'engine', path: 'Strata/a.cpp', symbol: 'Scene::OnUpdate' });
	assert.match(parseSource('Strata/a.cpp').error, /names no lines: write src="Strata\/a\.cpp#L<first>-L<last>", a symbol .* or an editor command \(command="<group\.action>"\)/);
	// The draft forms of pipelines.md §3.3, as tools/excerpts.py reads them: a destructor's symbol, and a command's
	// registration, whose src names the file without lines.
	assert.deepEqual(parseSource('Strata/a.cpp#~Scene'), { namespace: 'engine', path: 'Strata/a.cpp', symbol: '~Scene' });
	assert.deepEqual(parseSource('StrataEditor/src/Editor/EditorViewportCommands.cpp', new Map([['command', 'viewport.capture']])), { namespace: 'engine', path: 'StrataEditor/src/Editor/EditorViewportCommands.cpp', command: 'viewport.capture' });
	assert.match(parseSource('Strata/a.cpp', new Map([['command', ' ']])).error, /names no lines/);
	assert.match(parseSource('/abs/a.cpp#L1').error, /relative to the engine/);
	assert.match(parseSource('Strata/../a.cpp#L1').error, /relative to the engine/);
	assert.match(parseSource('a.cpp#L9-L3').error, /run forwards/);
});

test('relativeMarks counts from the quote\'s first line and refuses lines outside it', () => {
	assert.deepEqual(relativeMarks('L2251,L2253-L2255', 2239, 2262), { marks: '13,15-17' });
	assert.match(relativeMarks('L2300', 2239, 2262).error, /not inside/);
	assert.match(relativeMarks('2251', 2239, 2262).error, /engine's line numbers/);
});

test('a quote gets its source header, the engine\'s line numbers and relative marks', async () => {
	const page = `${frontmatter()}\n${fence('src="Strata/src/a.cpp#L100-L104" mark="L102"', lines(5))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, /class="book-excerpt__source"/);
		assert.match(html, /href="https:\/\/github\.com\/2042Third\/GameEngine\/blob\/822a7a46dbcdd86e8e2eafde7e41d003e27260c8\/Strata\/src\/a\.cpp#L100-L104"/);
		assert.match(html, /lines 100–104 \(engine 822a7a46\)/);
		// The meta reaches Expressive Code on the code element of the HTML tree.
		const tree = await render(book.root, 'core/time', { tree: true });
		const code = tree.children.find((node) => node.properties?.className?.includes('book-excerpt')).children[1].children[0];
		assert.equal(code.data.meta, 'showLineNumbers startLineNumber=100 mark={3}');
	} finally {
		book.remove();
	}
});

test('a quote whose body does not hold its range, or holds more than 60 lines, fails', async () => {
	const page = `${frontmatter()}\n${fence('src="Strata/a.cpp#L1-L5"', lines(4))}\n\n${fence('src="Strata/b.cpp#L1-L61"', lines(61))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /holds 4 lines but src names 5/, /at most 60 lines/);
	} finally {
		book.remove();
	}
});

test('a quote that starts or ends with a blank line fails, since Expressive Code would not draw it', async () => {
	const body = (text) => `\`\`\`cpp src="Strata/a.cpp#L10-L13"\n${text}\n\`\`\``;
	for (const [text, pattern] of [
		['\nint a;\nint b;\nint c;', /starts with a blank line, which Expressive Code does not draw, so its line numbers and marks would be one line late: quote L11-L13 instead/],
		['int a;\nint b;\n\t\n', /ends with a blank line, which Expressive Code does not draw, so the page would show fewer lines than src names: quote L10-L11 instead/],
		['\n\n\n', /every line of the quote is blank/],
	]) {
		const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body(text)}\n${c_BottomStrip}` } });
		try {
			await rejectsWith(render(book.root, 'core/time'), pattern);
		} finally {
			book.remove();
		}
	}
	// Blank lines inside the quote are the engine's and stay.
	const inside = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body('int a;\n\n\nint d;')}\n${c_BottomStrip}` } });
	try {
		assert.match(await render(inside.root, 'core/time'), /int d;/);
	} finally {
		inside.remove();
	}
});

test('a symbol quote is a draft: labelled in drafts, refused by a release build', async () => {
	const page = `${frontmatter()}\n${fence('src="Strata/a.cpp#Scene::OnUpdate"', [])}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		assert.match(await render(book.root, 'core/time'), /not filled from the engine yet/);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /names a symbol: run python tools\/excerpts\.py fill/);
	} finally {
		book.remove();
	}
});

test('a command quote is a draft as a symbol quote is, and a quote names its lines one way', async () => {
	const draft = fence('src="StrataEditor/src/Editor/EditorViewportCommands.cpp" command="viewport.capture"', []);
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${draft}\n${c_BottomStrip}` } });
	try {
		assert.match(await render(book.root, 'core/time'), /<p class="book-excerpt__source"><code>StrataEditor\/src\/Editor\/EditorViewportCommands\.cpp command="viewport\.capture"<\/code> \(draft: not filled from the engine yet\)<\/p>/);
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /src="StrataEditor\/src\/Editor\/EditorViewportCommands\.cpp" names an editor command: run python tools\/excerpts\.py fill before a release/);
	} finally {
		book.remove();
	}
	const both = makeBook({ pages: { 'core/time': `${frontmatter()}\n${fence('src="Strata/a.cpp#Scene::OnUpdate" command="scene.update"', [])}\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(both.root, 'core/time'), /names its lines by a symbol, and command="scene\.update" by an editor command: keep one of them/);
	} finally {
		both.remove();
	}
});

test('a page of kind internals needs three quotes', async () => {
	const page = `${frontmatter({ kind: 'internals' })}\n${fence('src="Strata/a.cpp#L1-L2"', lines(2))}\n${bottomStrip('internals')}`;
	const book = makeBook({ pages: { 'world/ecs': page } });
	try {
		await rejectsWith(render(book.root, 'world/ecs'), /quotes the engine at least 3 times; this one quotes it 1 times/);
	} finally {
		book.remove();
	}
});

test('a sketch fence must equal its file; output and pseudocode are labelled', async () => {
	const page = `${frontmatter()}\n${fence('sketch="core-time-toy.cpp"', ['int main() { return 0; }'])}\n\n\`\`\`text output-of="core-time-toy.cpp"\nhello\n\`\`\`\n\n\`\`\`cpp pseudocode\nstep();\n\`\`\`\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page }, files: { 'sketches/core-time-toy.cpp': 'int main() { return 0; }\n' } });
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, /Sketch/);
		// The header names the file as text: the book's repository is not public, so the site links nowhere in it.
		assert.match(html, /<p class="book-excerpt__source book-code__header"><span class="book-code__label">Sketch<\/span> · <code>sketches\/core-time-toy\.cpp<\/code><\/p>/);
		assert.doesNotMatch(html, /<a [^>]*href="[^"]*sketches\//);
		assert.match(html, /Output of the sketch/);
		assert.match(html, /Pseudocode/);
	} finally {
		book.remove();
	}
	const changed = makeBook({ pages: { 'core/time': page }, files: { 'sketches/core-time-toy.cpp': 'int main() { return 1; }\n' } });
	try {
		await rejectsWith(render(changed.root, 'core/time'), /differs from sketches\/core-time-toy\.cpp/);
	} finally {
		changed.remove();
	}
});

test('a page saved with CRLF line ends renders like the same page with LF', async () => {
	// Git for Windows checks files out with CRLF unless .gitattributes says otherwise; the fence then keeps "\r" in its
	// text, while the sketch file and the quote's lines have none.
	const sketch = ['#include <cstdio>', '', 'int main()', '{', '\treturn 0;', '}'];
	const page = `${frontmatter()}\n${fence('sketch="core-time-toy.cpp"', sketch)}\n\n${fence('src="Strata/a.cpp#L1-L5"', lines(5))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page.replace(/\n/g, '\r\n') }, files: { 'sketches/core-time-toy.cpp': `${sketch.join('\n')}\n` } });
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, /Sketch/);
		assert.doesNotMatch(html, /\r/);
	} finally {
		book.remove();
	}
});

test('a sketch takes no engine marks, and a quote no block-relative markers', async () => {
	const page = `${frontmatter()}\n${fence('sketch="core-time-toy.cpp" mark="L1"', ['int main() { return 0; }'])}\n\n${fence('src="Strata/a.cpp#L1-L5" {2} ins={3}', lines(5))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page }, files: { 'sketches/core-time-toy.cpp': 'int main() { return 0; }\n' } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /mark lines of a sketch with Expressive Code/, /\{2\} ins=\{3\} counts the block's lines/);
	} finally {
		book.remove();
	}
});

test('a fence attribute neither the book nor Expressive Code knows fails; Expressive Code\'s own pass', async () => {
	const { codePropsProblem } = await import('../excerpts.mjs');
	assert.equal(codePropsProblem(['title="main.cpp"', '{3-5}', 'ins={2}', '"two words"', '/re gex/', 'wrap', 'collapse={1-4}', 'frame="terminal"', 'showLineNumbers']), null);
	assert.match(codePropsProblem(['heading="main.cpp"']), /a code fence has no attribute "heading": the book's are src, mark, sketch, output-of \(with platform\), pseudocode, capture and variant/);
	assert.match(codePropsProblem(['pseudo']), /no attribute "pseudo"/);
	const page = `${frontmatter()}\n\`\`\`cpp snippet="core-time-toy.cpp"\nint x;\n\`\`\`\n\n\`\`\`json title="A command" {1}\n{ "command": "play.start" }\n\`\`\`\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		const error = await rejectsWith(render(book.root, 'core/time'), /a code fence has no attribute "snippet"/);
		assert.match(error.message, /has 1 problem/);
	} finally {
		book.remove();
	}
});

test('a quote keeps the anchors tools/excerpts.py writes; other fences take none of them', async () => {
	const kept = `${frontmatter()}\n${fence('src="Strata/a.cpp#L1-L5" symbol="Scene::OnUpdate" from="a" to="b"', lines(5))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': kept } });
	try {
		const tree = await render(book.root, 'core/time', { tree: true });
		const code = tree.children.find((node) => node.properties?.className?.includes('book-excerpt')).children[1].children[0];
		assert.equal(code.data.meta, 'showLineNumbers startLineNumber=1');
	} finally {
		book.remove();
	}
	const misplaced = makeBook({ pages: { 'core/time': `${frontmatter()}\n${fence('symbol="Scene::OnUpdate"', ['int x;'])}\n\n\`\`\`text output-of="core-time-toy.cpp" mark="L1"\nhello\n\`\`\`\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(misplaced.root, 'core/time'), /symbol belongs to a quote of the engine, with src="…"/, /mark="L…" counts the engine's lines and belongs to a quote with src="…"; use Expressive Code's \{3-5\} elsewhere/);
	} finally {
		misplaced.remove();
	}
});

test('a sketch\'s output may be shown per platform, each fence naming its platform', async () => {
	const outputs = ['windows', 'linux', 'macos'].map((platform, index) => `:::tab[${['Windows', 'Linux', 'macOS'][index]}]\n\n\`\`\`text output-of="core-time-toy.cpp" platform="${platform}"\nlong ${index ? 8 : 4}\n\`\`\`\n\n:::`);
	const page = `${frontmatter()}\n${fence('sketch="core-time-toy.cpp"', ['int main() { return 0; }'])}\n\n::::tabs{sync=os}\n${outputs.join('\n')}\n::::\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page }, files: { 'sketches/core-time-toy.cpp': 'int main() { return 0; }\n' } });
	try {
		const html = await render(book.root, 'core/time');
		assert.equal(html.match(/Output of the sketch/g)?.length, 3);
		assert.match(html, /long 4/);
		assert.match(html, /long 8/);
	} finally {
		book.remove();
	}
});

test('a sketch\'s file starts with its page\'s id, and its output follows it as a text fence', async () => {
	const page = (body) => makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` }, files: { 'sketches/core-time-toy.cpp': 'int main() { return 0; }\n', 'sketches/toy.cpp': 'int main() { return 0; }\n' } });
	const cases = [
		[fence('sketch="toy.cpp"', ['int main() { return 0; }']), /sketch="toy\.cpp": a sketch's file name starts with its page's id, core-time-<name>\.<extension> \(pipelines\.md §4\)/],
		[fence('sketch="core-time-toy"', ['int main() { return 0; }']), /sketch="core-time-toy" must name a file of sketches\/ with its extension/],
		['```text output-of="core-time-toy.cpp"\nhello\n```', /output-of="core-time-toy\.cpp" shows what a sketch prints: the page shows that sketch first, in a fence with sketch="core-time-toy\.cpp"/],
		[`${fence('sketch="core-time-toy.cpp"', ['int main() { return 0; }'])}\n\n\`\`\`cpp output-of="core-time-toy.cpp"\nhello\n\`\`\``, /the output of a sketch is a text fence: ```text output-of="core-time-toy\.cpp"/],
		[`${fence('sketch="core-time-toy.cpp"', ['int main() { return 0; }'])}\n\n\`\`\`text output-of="core-time-toy.cpp" platform="bsd"\nhello\n\`\`\``, /platform="bsd" is not one of windows, linux, macos/],
		[fence('sketch="core-time-toy.cpp" platform="linux"', ['int main() { return 0; }']), /platform="linux" names the platform of a sketch's output: it goes with output-of="<file>"/],
		[fence('sketch="core-time-toy.cpp" pseudocode', ['int main() { return 0; }']), /a fence is one of a quote \(src\), a sketch, a sketch's output, a text figure \(capture\) or pseudocode, not sketch and pseudocode/],
	];
	for (const [body, pattern] of cases) {
		const book = page(body);
		try {
			await rejectsWith(render(book.root, 'core/time'), pattern);
		} finally {
			book.remove();
		}
	}
});

test('quotes of the book\'s own files and of vendored libraries name their source as text', async () => {
	assert.deepEqual(parseSource('book:tutorials/make/first-script/Spinner.cpp#L1-L3'), { namespace: 'book', path: 'tutorials/make/first-script/Spinner.cpp', start: 1, end: 3 });
	assert.deepEqual(parseSource('vendor:glm/glm/glm.hpp#L10-L12'), { namespace: 'vendor', path: 'glm/glm/glm.hpp', lib: 'glm', start: 10, end: 12 });
	assert.deepEqual(parseSource('book:tutorials/world/wind.patch#hunk-2'), { namespace: 'book', path: 'tutorials/world/wind.patch', hunk: 2 });
	assert.match(parseSource('vendor:glm#L1').error, /a vendor source is vendor:<library>\/<path in the library>/);
	assert.match(parseSource('github:x/y#L1').error, /the sources are engine paths, book:<path> and vendor:<library>\/<path>/);
	assert.match(parseSource('Strata/a.cpp#hunk-1').error, /#hunk-<n> names a hunk of a tutorial's patch/);
	const page = `${frontmatter()}\n${fence('src="book:tutorials/core/time/Toy.cpp#L1-L2"', lines(2))}\n\n${fence('src="vendor:glm/glm/glm.hpp#L10-L12"', lines(3))}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, /<p class="book-excerpt__source"><code>tutorials\/core\/time\/Toy\.cpp<\/code>, lines 1–2 \(this book's own file\)<\/p>/);
		assert.match(html, /<p class="book-excerpt__source"><code>Strata\/vendor\/glm\/glm\/glm\.hpp<\/code>, lines 10–12 \(the library glm as the engine 822a7a46 vendors it\)<\/p>/);
		// Neither links GitHub: the book's repository is not public, and without src/generated/vendor.json the build has
		// no record of a library's.
		assert.doesNotMatch(html, /github\.com/);
	} finally {
		book.remove();
	}
});

test('a vendored library\'s quote names its version and license and links the file at the submodule\'s commit', async () => {
	const pin = '822a7a46dbcdd86e8e2eafde7e41d003e27260c8';
	const glm = { name: 'glm', version: '1.0.3', license: 'MIT', repository: 'https://github.com/g-truc/glm', commit: 'a'.repeat(40) };
	const record = (data) => ({ 'src/generated/vendor.json': JSON.stringify(data) });
	const page = `${frontmatter()}\n${fence('src="vendor:glm/glm/glm.hpp#L10-L12"', lines(3))}\n${c_BottomStrip}`;
	const vendorBook = (files) => makeBook({ pages: { 'core/time': page }, files });
	const book = vendorBook(record({ pin, libraries: { glm } }));
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, new RegExp(`<p class="book-excerpt__source"><a href="https://github\\.com/g-truc/glm/blob/${'a'.repeat(40)}/glm/glm\\.hpp#L10-L12"><code>Strata/vendor/glm/glm/glm\\.hpp</code></a>, lines 10–12 \\(glm 1\\.0\\.3, MIT, as the engine 822a7a46 vendors it\\)</p>`));
	} finally {
		book.remove();
	}
	for (const [files, pattern] of [
		[record({ pin, libraries: {} }), /src="vendor:glm\/glm\/glm\.hpp…": the engine's notices at the pin list no library "glm" \(src\/generated\/vendor\.json knows none\)/],
		[record({ pin: 'b'.repeat(40), libraries: { glm } }), /src\/generated\/vendor\.json was written for engine bbbbbbbb, not for the pin 822a7a46: write it again at the pin/],
		[record({ pin, libraries: { glm: { ...glm, license: '' } } }), /src\/generated\/vendor\.json: the library "glm" has no license/],
		[record({ pin, libraries: { glm: { ...glm, repository: 'git@github.com:g-truc/glm' } } }), /the repository of "glm" is not an https address of a repository/],
		[{ 'src/generated/vendor.json': '{ not json' }, /src\/generated\/vendor\.json is not valid JSON/],
	]) {
		const wrong = vendorBook(files);
		try {
			await rejectsWith(render(wrong.root, 'core/time'), pattern);
		} finally {
			wrong.remove();
		}
	}
	// A release names every quoted library's version and license: without the record it refuses the quote.
	const release = makeBook({ pages: { 'core/time': page.replace('status: draft', 'status: final') } });
	try {
		await rejectsWith(render(release.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /a release names the version and license of every vendored library it quotes, and src\/generated\/vendor\.json, which the tool chain writes, does not exist/);
	} finally {
		release.remove();
	}
});

test('a hunk of a tutorial\'s patch names the engine file and lines it changes, and links the patch\'s download', async () => {
	const { patchHunk } = await import('../excerpts.mjs');
	const patch = 'diff --git a/Strata/src/Strata/Scene/Scene.h b/Strata/src/Strata/Scene/Scene.h\n--- a/Strata/src/Strata/Scene/Scene.h\n+++ b/Strata/src/Strata/Scene/Scene.h\n@@ -10,3 +10,4 @@ class Scene\n a\n-b\n+c\n+d\n e\ndiff --git a/Strata/src/New.cpp b/Strata/src/New.cpp\n--- /dev/null\n+++ b/Strata/src/New.cpp\n@@ -0,0 +1,2 @@\n+x\n+y\n';
	assert.deepEqual(patchHunk(patch, 1), { file: 'Strata/src/Strata/Scene/Scene.h', start: 10, count: 3, lines: [' a', '-b', '+c', '+d', ' e'] });
	assert.deepEqual(patchHunk(patch, 2), { file: 'Strata/src/New.cpp', start: 0, count: 0, lines: ['+x', '+y'] });
	assert.match(patchHunk(patch, 3).error, /the patch has 2 hunks, not 3/);
	const hunk = (meta, body) => `\`\`\`diff ${meta}\n${body.join('\n')}\n\`\`\``;
	const page = `${frontmatter()}\n${hunk('src="book:tutorials/core/time.patch#hunk-1"', [' a', '-b', '+c', '+d', ' e'])}\n${c_BottomStrip}`;
	const book = makeBook({ pages: { 'core/time': page }, files: { 'tutorials/core/time.patch': patch, 'public/downloads/tutorials/core/time.patch': patch } });
	try {
		const html = await render(book.root, 'core/time');
		assert.match(html, /<div class="book-excerpt book-excerpt--patch" data-source="book:tutorials\/core\/time\.patch#hunk-1"><p class="book-excerpt__source"><a href="https:\/\/github\.com\/2042Third\/GameEngine\/blob\/822a7a46dbcdd86e8e2eafde7e41d003e27260c8\/Strata\/src\/Strata\/Scene\/Scene\.h#L10-L12"><code>Strata\/src\/Strata\/Scene\/Scene\.h<\/code><\/a>, lines 10–12 at engine 822a7a46, changed by hunk 1 of <a href="\/book\/downloads\/tutorials\/core\/time\.patch"><code>tutorials\/core\/time\.patch<\/code><\/a><\/p>/);
	} finally {
		book.remove();
	}
	const wrong = makeBook({ pages: { 'core/time': `${frontmatter()}\n${hunk('src="book:tutorials/core/time.patch#hunk-1"', [' a'])}\n\n\`\`\`cpp src="book:tutorials/core/gone.patch#hunk-1"\nx\n\`\`\`\n${c_BottomStrip}` }, files: { 'tutorials/core/time.patch': patch } });
	try {
		await rejectsWith(render(wrong.root, 'core/time'), /the fence holds 1 lines but hunk 1 of tutorials\/core\/time\.patch has 5/, /a hunk of a patch is a diff fence/, /the patch tutorials\/core\/gone\.patch does not exist/);
	} finally {
		wrong.remove();
	}
});

test('only quotes of the engine itself count toward an internals page\'s three', async () => {
	const quotes = [fence('src="Strata/a.cpp#L1-L2"', lines(2)), fence('src="Strata/b.cpp#L1-L2"', lines(2)), fence('src="book:tutorials/world/ecs/Toy.cpp#L1-L2"', lines(2))].join('\n\n');
	const book = makeBook({ pages: { 'world/ecs': `${frontmatter({ kind: 'internals' })}\n${quotes}\n${bottomStrip('internals')}` } });
	try {
		await rejectsWith(render(book.root, 'world/ecs'), /quotes the engine at least 3 times; this one quotes it 2 times/);
	} finally {
		book.remove();
	}
});

test('a file of this repository names its download: patches, worked solutions and labs', async () => {
	const { bookDownloadPath } = await import('../excerpts.mjs');
	assert.equal(bookDownloadPath('tutorials/world/tutorial-component.patch'), 'downloads/tutorials/world/tutorial-component.patch');
	assert.equal(bookDownloadPath('tutorials/core/time/exercise-2.patch'), 'downloads/solutions/core/time/exercise-2.patch');
	assert.equal(bookDownloadPath('tutorials/make/first-script/exercise-1.tutorial.json'), 'downloads/solutions/make/first-script/exercise-1.zip');
	assert.equal(bookDownloadPath('labs/spot-lights.json'), 'downloads/labs/spot-lights.zip');
	assert.equal(bookDownloadPath('labs/spot-lights/Meshes/Wall.gltf'), 'downloads/labs/spot-lights.zip');
	// The tutorial's own files are in its checkpoints' projects, not downloads of their own.
	assert.equal(bookDownloadPath('tutorials/make/first-script/Spinner.cpp'), null);
	const page = `${frontmatter()}\n${fence('src="book:labs/spot-lights.json#L1-L2"', lines(2))}\n\n${fence('src="book:labs/mirrors.json#L1-L2"', lines(2))}\n${c_BottomStrip}`;
	for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
		const book = makeBook({ pages: { 'core/time': page }, files: { 'public/downloads/labs/spot-lights.zip': 'zip' } });
		try {
			const html = await render(book.root, 'core/time', { env: { DOCS_BASE: setting } });
			assert.match(html, new RegExp(`<a href="${base}/downloads/labs/spot-lights\\.zip"><code>labs/spot-lights\\.json</code></a>, lines 1–2 \\(this book's own file\\)`));
			// A lab whose download is not published yet is named as text.
			assert.match(html, /<p class="book-excerpt__source"><code>labs\/mirrors\.json<\/code>, lines 1–2/);
		} finally {
			book.remove();
		}
	}
});

test('printed, code blocks take Expressive Code\'s light colors whatever the reader\'s theme', async () => {
	// Starlight prints its colors as the light theme's; a quote, a sketch or its output in the dark theme's light colors
	// would stand on a light background. Checked in Chromium too: the dark theme's output prints rgb(64, 63, 83).
	const { readFileSync } = await import('node:fs');
	const path = (await import('node:path')).default;
	const { fileURLToPath } = await import('node:url');
	const print = readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'styles', 'print.css'), 'utf8');
	// The plain text, whose token spans src/lib/ec-compact.mjs leaves out, prints in the color those spans printed.
	assert.match(print, /:root \.expressive-code \{\n\t\t--ec-codeFg: #403f53;\n\t\t--ec-lineNumbers-fg: var\(--sl-color-gray-3\);\n\t\}/);
	assert.match(print, /:root \.expressive-code \.ec-line :where\(span\[style\^='--'\]:not\(\[class\]\)\) \{\n\t\tcolor: var\(--1, inherit\);\n\t\tbackground-color: var\(--1bg, transparent\);/);
});

// A text figure's recipe (.tools/handover/figures-format.md §1): a command's result, or with variants a program's output.
const c_TextRecipes = {
	figures: [
		{ id: 'status', kind: 'text', shows: 'What editor.status answers', caption: 'The editor reports its engine version.', alt: 'The result of editor.status.', text: { command: { command: 'editor.status' }, keep: ['/engineVersion'] } },
		{ id: 'help', kind: 'text', shows: 'The runtime\'s help', caption: 'The runtime lists its options.', alt: 'The help of the runtime.', variants: { short: { text: { program: 'StrataRuntime', arguments: ['--help'] } }, long: { text: { program: 'StrataCLI', arguments: ['--help'] } } } },
		{ id: 'shot', kind: 'editor', shows: 'The editor', caption: 'The editor after the step.', alt: 'The editor window.' },
	],
};

function textFigureBook(body, { published = { 'status.txt': '{ "engineVersion": "0.7.0" }\n', 'help-short.txt': 'Usage: StrataRuntime [--game <file>]\n' }, status = 'draft' } = {}) {
	const files = { 'src/content/figures/core/time.json': JSON.stringify(c_TextRecipes) };
	for (const [name, content] of Object.entries(published)) files[`src/assets/figures/core/time/${name}`] = content;
	return makeBook({ pages: { 'core/time': `${frontmatter({ status })}\n${body}\n${c_BottomStrip}` }, files });
}

test('a text figure shows the published text with a header that says the engine printed it', async () => {
	const body = '```text capture="status"\n{ "engineVersion": "0.7.0" }\n```\n\n```text capture="help" variant="short"\nUsage: StrataRuntime [--game <file>]\n```';
	const book = textFigureBook(body);
	try {
		const html = await render(book.root, 'core/time');
		// A figure like a picture's (style.md §11): its id, the fence with its header, and the recipe's caption.
		assert.match(html, /<figure class="book-figure book-figure--text" id="fig-status"><div class="book-excerpt book-code book-code--capture"><p class="book-excerpt__source book-code__header"><span class="book-code__label">Captured from the engine<\/span> · the result of the editor command <code>editor\.status<\/code><\/p><pre><code class="language-text">\{ "engineVersion": "0\.7\.0" \}\n<\/code><\/pre><\/div><figcaption>The editor reports its engine version\.<\/figcaption><\/figure>/);
		assert.match(html, /<figure class="book-figure book-figure--text" id="fig-help">/);
		// A variant may run another program: its header names the variant's.
		assert.match(html, /<span class="book-code__label">Captured from the engine<\/span> · the output of <code>StrataRuntime<\/code><\/p>/);
		assert.doesNotMatch(html, /not captured yet/);
		// The attributes are the book's: Expressive Code never sees them.
		assert.doesNotMatch(html, /capture=|variant=/);
	} finally {
		book.remove();
	}
	// Release builds show it the same way once it is taken.
	const release = textFigureBook('```text capture="status"\n{ "engineVersion": "0.7.0" }\n```', { status: 'reviewed' });
	try {
		assert.match(await render(release.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /book-code--capture/);
	} finally {
		release.remove();
	}
});

test('a text figure\'s id is the one the page index gives it, so that links to it are checked', async () => {
	const { collectAnchors } = await import('../../lib/pages.mjs');
	const { parseMarkdown } = await import('../../lib/markdown.mjs');
	const body = '::figure{id=shot}\n\n```text capture="help" variant="short"\nUsage: StrataRuntime [--game <file>]\n```\n\n```text capture="help" variant="long"\nx\n```\n\n```text capture="status"\n{ "engineVersion": "0.7.0" }\n```';
	const anchors = collectAnchors(parseMarkdown(body));
	for (const id of ['fig-shot', 'fig-help', 'fig-help-long', 'fig-status']) assert.ok(anchors.has(id), id);
	const book = textFigureBook(body, { published: { 'help-short.txt': 'Usage: StrataRuntime [--game <file>]\n', 'help-long.txt': 'x\n', 'status.txt': '{ "engineVersion": "0.7.0" }\n' } });
	try {
		const html = await render(book.root, 'core/time');
		const ids = [...html.matchAll(/<figure class="book-figure[^"]*" id="([^"]+)"/g)].map((match) => match[1]);
		assert.deepEqual(ids, ['fig-shot', 'fig-help', 'fig-help-long', 'fig-status']);
	} finally {
		book.remove();
	}
});

test('a text figure not taken yet is labelled in drafts and fails a release', async () => {
	const book = textFigureBook('```text capture="status"\n```', { published: {} });
	const reviewed = textFigureBook('```text capture="status"\n```', { published: {}, status: 'reviewed' });
	try {
		assert.match(await render(book.root, 'core/time'), /Captured from the engine<\/span> · the result of the editor command <code>editor\.status<\/code> \(draft: not captured yet\)<\/p>/);
		await rejectsWith(render(reviewed.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /the text figure status is not taken yet \(src\/assets\/figures\/core\/time\/status\.txt\): a release shows only text the engine printed/);
	} finally {
		book.remove();
		reviewed.remove();
	}
});

test('a text figure names a text recipe of its page, one of its variants, and holds the published text', async () => {
	const cases = [
		['```text capture="status"\n{ "engineVersion": "0.6.0" }\n```', /core\/time\.md:\d+:\d+: the fence differs from src\/assets\/figures\/core\/time\/status\.txt: run python -I tools\/figures\.py fill/],
		['```json capture="status"\n{ "engineVersion": "0.7.0" }\n```', /a text figure is a text fence: ```text capture="status"/],
		['```text capture="nothing"\nx\n```', /capture="nothing": src\/content\/figures\/core\/time\.json has no text figure of that id: add its recipe \(kind text\), or correct capture/],
		['```text capture="shot"\nx\n```', /capture="shot": src\/content\/figures\/core\/time\.json has no text figure of that id; "shot" is a figure of kind editor, which ::figure\{id=shot\} places/],
		['```text capture="help"\nx\n```', /the text figure "help" has the variants short, long: name one with variant="…"/],
		['```text capture="help" variant="medium"\nx\n```', /the text figure "help" has no variant "medium" \(it has short, long\)/],
		['```text capture="status" variant="short"\nx\n```', /the text figure "status" has no variants: remove variant="short"/],
		['```text variant="short"\nx\n```', /variant="short" chooses a variant of a text figure: it goes with capture="<figure>"/],
		['```text capture="status" pseudocode\nx\n```', /a fence is one of a quote \(src\), a sketch, a sketch's output, a text figure \(capture\) or pseudocode, not capture and pseudocode/],
		['::figure{id=status}', /figure "status" is a text figure: show it in a fence, ```text capture="status"/],
		['::figure{id=help variant=short}', /figure "help" is a text figure: show it in a fence, ```text capture="help" variant="short"/],
	];
	for (const [body, pattern] of cases) {
		const book = textFigureBook(body);
		try {
			await rejectsWith(render(book.root, 'core/time'), pattern);
		} finally {
			book.remove();
		}
	}
	// A text figure is a figure: its recipe has a caption, alt text and what it shows, as a picture's has.
	const recipes = JSON.parse(JSON.stringify(c_TextRecipes));
	delete recipes.figures[0].caption;
	const uncaptioned = makeBook({ pages: { 'core/time': `${frontmatter()}\n\`\`\`text capture="status"\n{ "engineVersion": "0.7.0" }\n\`\`\`\n${c_BottomStrip}` }, files: { 'src/content/figures/core/time.json': JSON.stringify(recipes), 'src/assets/figures/core/time/status.txt': '{ "engineVersion": "0.7.0" }\n' } });
	try {
		await rejectsWith(render(uncaptioned.root, 'core/time'), /figure "status" has no caption \(what to notice\)/);
	} finally {
		uncaptioned.remove();
	}
	// Without a manifest the page has no text figure either.
	const bare = makeBook({ pages: { 'core/time': `${frontmatter()}\n\`\`\`text capture="status"\nx\n\`\`\`\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(bare.root, 'core/time'), /capture="status": src\/content\/figures\/core\/time\.json has no text figure of that id/);
	} finally {
		bare.remove();
	}
});
