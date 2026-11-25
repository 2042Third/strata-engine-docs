// The directive table and the directives that draw boxes and lists (plan/site.md, "Directives"; plan/style.md §12):
// for each, its markup, its accessible name, its print form and its failure messages, which name the page and the line.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { openForPrint } from '../../components/client/print.js';
import { c_Directives, directiveProblems } from '../../lib/directives.mjs';
import { parseMarkdown } from '../../lib/markdown.mjs';
import { c_DerivationSkip } from '../derivation.mjs';
import { fileEntry } from '../lists.mjs';
import { c_BottomStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Styles = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'styles');
const printCss = readFileSync(path.join(c_Styles, 'print.css'), 'utf8');
const bookCss = readFileSync(path.join(c_Styles, 'book.css'), 'utf8');

async function html(body, { env } = {}) {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` } });
	try {
		return await render(book.root, 'core/time', { env });
	} finally {
		book.remove();
	}
}

async function fails(body, ...patterns) {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` } });
	try {
		return await rejectsWith(render(book.root, 'core/time'), ...patterns);
	} finally {
		book.remove();
	}
}

/** The line of the page a message names ("src/content/docs/core/time.md:14:1: …"). */
function lineOf(message, pattern) {
	const line = message.split('\n').find((candidate) => pattern.test(candidate));
	assert.ok(line, `no line matches ${pattern}:\n${message}`);
	return Number(/time\.md:(\d+):\d+:/.exec(line)?.[1]);
}

/** The rules of a print style sheet's @media print block that name a selector. */
function printRule(selector) {
	const index = printCss.indexOf(selector);
	assert.ok(index >= 0, `print.css names ${selector}`);
	return printCss.slice(index, printCss.indexOf('}', index));
}

test('the table is the complete list of site.md and the generated value of pipelines.md §7.3, each directive in its form', () => {
	const names = ['note', 'tip', 'caution', 'danger', 'why', 'question', 'history', 'elsewhere', 'rule', 'simplified', 'analogy', 'example', 'derivation', 'test-out', 'answer', 'tabs', 'tab', 'steps', 'files', 'figure', 'compare', 'checkpoint', 'glossary', 'track-chooser', 'include', 'term', 'since', 'value'];
	assert.deepEqual(Object.keys(c_Directives).sort(), [...names].sort());
	assert.deepEqual(c_Directives.checkpoint.forms, ['leaf']);
	assert.deepEqual(c_Directives.term.forms, ['text']);
	assert.deepEqual(c_Directives.include.attributes, ['file']);
	assert.deepEqual(c_Directives.value, { forms: ['text'], label: 'none', attributes: ['key'] });
	const problems = (markdown) => {
		const found = [];
		const visit = (node) => {
			found.push(...directiveProblems(node));
			(node.children ?? []).forEach(visit);
		};
		visit(parseMarkdown(markdown));
		return found;
	};
	assert.deepEqual(problems(':::why[A title]\nText.\n:::\n\n:::note{icon=rocket}\nA note.\n:::\n'), []);
	assert.deepEqual(problems('Prose with a:b and std::vector.'), []);
	assert.match(problems('::why\n').join('\n'), /::why: :::why is a block/);
	assert.match(problems(':::checkpoint{stage=1}\n:::\n').join('\n'), /:::checkpoint: ::checkpoint stands on a line of its own/);
	assert.match(problems('A ::include{file="x.md"} here.\n\n:::term\nx\n:::\n').join('\n'), /:::term: :term stands inside a sentence/);
	assert.match(problems(':::derivation[Why]\nSteps.\n:::\n').join('\n'), /:::derivation\[Why\] takes no text in brackets/);
	assert.match(problems(':::why{tone=warm}\nText.\n:::\n').join('\n'), /:::why has no attribute "tone" \(it takes none\)/);
	assert.match(problems('::include{file="x.md" table=y}\n').join('\n'), /::include has no attribute "table" \(it takes file\)/);
	assert.match(problems('A :since{x=1} mark.').join('\n'), /:since needs its text in brackets/);
	assert.match(problems(':::note{tone=x}\nA note.\n:::\n').join('\n'), /:::note has no attribute "tone" \(it takes icon\)/);
});

test('a directive of the wrong form or with a wrong attribute fails at its own line', async () => {
	const body = 'Text.\n\n::why\n\n:::steps{start=2}\n1. One.\n:::\n';
	const error = await fails(body, /::why: :::why is a block/, /:::steps has no attribute "start"/);
	assert.doesNotMatch(error.message, /unknown directive/);
	// The test page's front matter has 17 lines and a blank line follows it: "::why" is on line 21 of the file.
	assert.equal(lineOf(error.message, /::why: :::why/), 21);
	assert.equal(lineOf(error.message, /:::steps has no/), 23);
});

test('the new asides render with Starlight\'s markup, their default titles as their accessible names', async () => {
	const out = await html(':::simplified\nFor now, assume one thread. [The full story](#a).\n:::\n\n:::example[Two frames]\nThe problem, the steps, the result.\n:::\n\n:::analogy\nThe accumulator is a bucket.\n\n**Where it breaks:** a bucket overflows.\n:::\n\n## A\n\nText.');
	assert.match(out, /<aside class="starlight-aside book-aside book-aside--simplified" aria-label="Simplified for now"><p class="starlight-aside__title" aria-hidden="true">Simplified for now<\/p>/);
	assert.match(out, /<aside class="starlight-aside book-aside book-aside--example" aria-label="Two frames">/);
	assert.match(out, /<aside class="starlight-aside book-aside book-aside--analogy" aria-label="An analogy">/);
	// The paragraph that says where the analogy breaks is marked, so that it stands apart.
	assert.match(out, /<p class="book-aside__limit"><strong>Where it breaks:<\/strong> a bucket overflows\.<\/p>/);
	assert.match(bookCss, /\.book-aside--analogy \{ --book-aside-color/);
	// Printed, an aside is not cut between two sheets.
	assert.match(printCss, /\.book-aside \{\s*break-inside: avoid;/);
});

test('an analogy ends with "Where it breaks", and an aside is never empty', async () => {
	await fails(':::analogy\nThe accumulator is a bucket.\n:::', /an analogy ends with the paragraph that says where it breaks: its last paragraph starts with "\*\*Where it breaks:\*\*"/);
	await fails(':::analogy\n**Where it breaks:** a bucket overflows.\n\nThe accumulator is a bucket.\n:::', /an analogy ends with the paragraph that says where it breaks/);
	await fails(':::example\n:::', /the :::example aside is empty/);
});

test('a derivation is a closed details titled "Where this comes from", its first line written by the plugin', async () => {
	const out = await html(':::derivation\nStart from $d = v t$.\n:::');
	assert.match(out, new RegExp(`<details class="book-derivation"><summary>Where this comes from</summary><div class="book-derivation__body"><p class="book-derivation__skip">${c_DerivationSkip.replace(/[.:]/g, '\\$&')}</p><p>Start from <span class="katex">`));
	assert.doesNotMatch(out, /<details class="book-derivation" open/);
	await fails(':::derivation[How]\nSteps.\n:::', /:::derivation\[How\] takes no text in brackets/);
	await fails(':::derivation\n:::', /the :::derivation box is empty/);
	// Printed, it opens: the script opens it before printing, and browsers that can show closed details' content do.
	assert.match(printRule('details.book-derivation::details-content'), /content-visibility: visible/);
});

test('printing opens every closed answer and derivation, and closes them again afterwards', () => {
	const details = (open) => ({ open });
	const closedAnswer = details(false);
	const openAnswer = details(true);
	const closedDerivation = details(false);
	const root = {
		querySelectorAll(selector) {
			assert.equal(selector, 'details.book-answer, details.book-derivation');
			return [closedAnswer, openAnswer, closedDerivation];
		},
	};
	const close = openForPrint(root);
	assert.deepEqual([closedAnswer.open, openAnswer.open, closedDerivation.open], [true, true, true]);
	close();
	assert.deepEqual([closedAnswer.open, openAnswer.open, closedDerivation.open], [false, true, false]);
});

test('steps draw Starlight\'s steps markup, a list that keeps its role and its first number', async () => {
	const out = await html(':::steps\n1. Open the editor.\n2. Press **Play**.\n:::\n\n:::steps\n3. Go on.\n4. Stop.\n:::');
	assert.match(out, /<ol class="sl-steps" role="list">\n<li>Open the editor\.<\/li>/);
	assert.match(out, /<ol start="3" class="sl-steps" role="list" style="--sl-steps-start: 2">/);
	// Starlight's own styles for the markup are in the book's style sheet, with its notice.
	assert.match(bookCss, /counter-reset: steps-counter var\(--sl-steps-start, 0\);/);
	assert.match(bookCss, /Starlight is under the MIT License:\s+Copyright \(c\) 2023 \[Astro contributors\]/);
	// Printed, the numbers are black on white, whatever the theme.
	assert.match(printRule('.sl-steps > li::before'), /color: #000;/);
});

test('steps hold one numbered list and nothing else', async () => {
	await fails(':::steps\n- One.\n- Two.\n:::', /:::steps holds one numbered list \(1\. 2\. 3\.\) and nothing else; it holds a bulleted list/);
	await fails(':::steps\n1. One.\n\nAnd a paragraph.\n:::', /it holds a numbered list, a paragraph/);
	await fails(':::steps\n:::', /it holds nothing/);
});

test('a file tree draws folders, files, comments and highlights, named for screen readers', async () => {
	const tree = ':::files\n- `My Game/`\n  - **Scripts/** the game\'s scripts\n    - Spinner.cpp: turns its entity\n  - Assets/\n  - …\n- README.md\n:::';
	const out = await html(tree);
	assert.match(out, /<figure class="book-files" aria-label="Files and folders"><ul class="book-files__tree">/);
	assert.match(out, /<li class="book-files__folder"><span class="book-files__entry"><svg class="book-files__icon"[^>]*aria-hidden="true"[^>]*>.*?<\/svg><span class="book-files__name"><span class="sr-only">Folder <\/span>My Game\/<\/span><\/span><ul>/s);
	assert.match(out, /<span class="book-files__name book-files__name--highlight"><span class="sr-only">Folder <\/span><strong>Scripts\/<\/strong><\/span> <span class="book-files__comment">the game’s scripts<\/span>/);
	assert.match(out, /<li class="book-files__file"><span class="book-files__entry"><svg[^>]*>.*?<\/svg><span class="book-files__name">Spinner\.cpp<\/span> <span class="book-files__comment">turns its entity<\/span><\/span><\/li>/s);
	assert.match(out, /<li class="book-files__folder"><span class="book-files__entry"><svg[^>]*>.*?<\/svg><span class="book-files__name"><span class="sr-only">Folder <\/span>Assets\/<\/span><\/span><\/li>/s);
	assert.match(out, /<li class="book-files__more"><span aria-hidden="true">…<\/span><span class="sr-only">More files<\/span><\/li>/);
	const named = await html(':::files[The project after step 3]\n- Spin/\n:::');
	assert.match(named, /<figure class="book-files"><figcaption class="book-files__caption">The project after step 3<\/figcaption><ul class="book-files__tree">/);
	// Printed, a tree is not cut between two sheets.
	assert.match(printCss, /\.book-files,/);
});

test('a file tree\'s items start with a name, hold one bulleted list at most, and the tree is one list', async () => {
	assert.deepEqual(fileEntry(parseMarkdown('`a b/` — two words').children[0]).name, 'a b/');
	assert.equal(fileEntry(parseMarkdown('[a link](x.md)').children[0]).error, 'an item of a file tree starts with the name of a file or folder (a word, a name in backticks, or a bold name)');
	await fails(':::files\n1. One\n:::', /:::files holds one bulleted list of files and folders, nested for what a folder holds, and nothing else; it holds a numbered list/);
	await fails(':::files\n- Spin/\n\n  A paragraph.\n:::', /"Spin\/" also holds a paragraph/);
	await fails(':::files\n- [Link](https://example.org/)\n:::', /starts with the name of a file or folder/);
	await fails(':::files\n- …\n  - x\n:::', /"…" stands for files left out: it holds no list/);
});

test(':since marks the first paragraph of a section with the book\'s release', async () => {
	const out = await html('## Smooth motion\n\n:since[0.8.0] Strata draws between poses.');
	assert.match(out, /<h2>Smooth motion<\/h2>\n<p><span class="book-badge book-badge--new book-since" data-pagefind-ignore="">New in 0.8.0<\/span> Strata draws between poses\.<\/p>/);
	assert.match(bookCss, /\.book-since \{/);
});

test(':since names the book\'s release, starts the first paragraph of a section, and is not on a page that is new', async () => {
	await fails('## A\n\n:since[0.7.0] Older.', /:since\[0\.7\.0\] marks a feature new in the book's release, which is 0\.8\.0 \(engine\.pin\)/);
	await fails('## A\n\n:since[eight] New.', /:since\[eight\]: write the release as X\.Y\.Z/);
	await fails('## A\n\nFirst.\n\n:since[0.8.0] Second.', /this paragraph is not the first one after its heading/);
	await fails('## A\n\nIt is :since[0.8.0] new.', /:since\[…\] starts its paragraph/);
	await fails('## A\n\n- :since[0.8.0] In a list.', /not a paragraph inside a list, a table or an aside/);
	await fails(':since[0.8.0] Before any heading.', /stands before the page's first heading/);
	// A bare ":since" is prose, as "a:b" is: only a mark with its text in brackets is the directive. (Starlight writes
	// such prose back as text after the book's plugins; the tests run without Starlight.)
	await html('## A\n\nThe word :since stays.');
	const book = makeBook({ pages: { 'world/new': `${frontmatter({ since: '0.8.0' })}\n## A\n\n:since[0.8.0] New.\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'world/new'), /the whole page is new in 0\.8\.0 \(since: 0\.8\.0 in its front matter, shown at the top\): its sections carry no :since\[0\.8\.0\]/);
	} finally {
		book.remove();
	}
});

test('tab sets of the style guide\'s keys hold its labels, in order', async () => {
	await html('::::tabs{sync=how}\n:::tab[In the editor]\nClick.\n:::\n:::tab[With a command]\nRun.\n:::\n::::');
	await html('::::tabs{sync=os}\n:::tab[Windows]\nA.\n:::\n:::tab[Linux]\nB.\n:::\n:::tab[macOS]\nC.\n:::\n::::');
	await fails('::::tabs{sync=how}\n:::tab[Editor]\nClick.\n:::\n:::tab[Command]\nRun.\n:::\n::::', /a tab set with sync=how holds the tabs "In the editor", "With a command", in this order \(style\.md §10\); this one holds "Editor", "Command"/);
	await fails('::::tabs{sync=os}\n:::tab[Linux]\nB.\n:::\n:::tab[Windows]\nA.\n:::\n::::', /sync=os holds the tabs "Windows", "Linux", "macOS"/);
	await fails('::::tabs{sync=os}\n:::tab[Windows]\nA.\n:::\n:::tab[Linux]\nB.\n:::\n::::', /this one holds "Windows", "Linux"/);
});

test('the report names every unknown directive with the book\'s list', async () => {
	const error = await fails(':::pitfall\nOops.\n:::\n\n::milestone{stage=1}', /unknown directive :::pitfall: the book knows :::note, :::tip/, /unknown directive ::milestone/);
	assert.match(error.message, /::checkpoint, ::glossary, ::track-chooser, ::include, :term, :since, :value/);
});

test('an MDX file under src/content fails the build', async () => {
	const { bookProblems } = await import('../../integrations/book.mjs');
	const { createBookContext } = await import('../index.mjs');
	const { readSettings } = await import('../../lib/settings.mjs');
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\nText.\n${c_BottomStrip}` }, files: { 'src/content/docs/core/extra.mdx': '# MDX\n' } });
	try {
		const context = createBookContext(readSettings({ root: book.root, env: { DOCS_BASE: '/book', DOCS_SITE: 'https://example.com' } }));
		const problems = await bookProblems(context);
		assert.ok(problems.includes('src/content/docs/core/extra.mdx: the book\'s pages are plain Markdown (.md); MDX is not read (site.md, "What MDX would have given")'), problems.join('\n'));
	} finally {
		book.remove();
	}
});
