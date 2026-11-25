// A primer's Test out box (plan/style.md §7.1; rule P3 of plan/site.md, "Page shape") and the rest of what style.md
// §14 gives the strips: the exact headings of each kind's body (§7) and a worked example before the bottom strip (§8).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseMarkdown } from '../../lib/markdown.mjs';
import { bodyHeadingsProblems, exampleProblems, generalSectionProblems, proseWords, testOutProblems } from '../strips.mjs';
import { c_TestOutInstruction } from '../testout.mjs';
import { bottomStrip, c_BottomStrip, c_TestOut, frontmatter, makeBook, primerBody, rejectsWith, render } from './helpers.mjs';

const learn = ['one-thing', 'another-thing'];
const uses = '- [Time](../core/time.md) counts with it.\n- [Steps](../core/steps.md) adds them.\n- [Loop](../core/loop.md) reads them.\n';
const user = (title, needs = '[basics/numbers]') => `${frontmatter({ title: `"${title}"`, needs, tracks: '[B, E]', since: undefined })}\nText.\n${c_BottomStrip}`;

function primerBook(body = primerBody(uses), extra = {}) {
	return makeBook({
		pages: {
			'basics/numbers': `${frontmatter({ title: '"Numbers"', kind: 'primer', tracks: '[B, E]', since: undefined })}\n${body}`,
			'core/time': user('Time'),
			'core/steps': user('Steps'),
			'core/loop': user('Loop'),
			...extra,
		},
	});
}

test('the Test out box opens a primer with its title, its instruction and the next page of each track', async () => {
	const book = primerBook();
	try {
		const out = await render(book.root, 'basics/numbers');
		assert.ok(out.startsWith('<section class="book-test-out" aria-label="Test out"><div class="book-test-out__intro" data-pagefind-ignore=""><p class="book-test-out__title">Test out</p>'), out.slice(0, 300));
		assert.match(out, new RegExp(`<p class="book-test-out__instruction">${c_TestOutInstruction.replace(/[.:]/g, '\\$&')}</p>`));
		// The test book's tracks list the pages in the order the test wrote them: Time follows the primer on B and E.
		assert.match(out, /<ul class="book-test-out__next"><li data-book-track="beginner">Beginner \(B\): <a href="\/book\/core\/time\/">Time<\/a><\/li><li data-book-track="engine">Engine builder \(E\): <a href="\/book\/core\/time\/">Time<\/a><\/li><\/ul><\/div>/);
		// The five questions follow with their hidden answers.
		assert.equal((out.match(/<details class="book-answer">/g) ?? []).length, 5 + 3 + 3);
		assert.match(out, /<\/ol><\/section>\n<h2>Why you will need this<\/h2>/);
	} finally {
		book.remove();
	}
});

test('a track whose later pages are not written yet says so in the box', async () => {
	// The pages that use the primer are on track E only: on track B no later page is written.
	const onE = (title) => user(title).replace('tracks: [B, E]', 'tracks: [E]');
	const book = primerBook(primerBody(uses), { 'core/time': onE('Time'), 'core/steps': onE('Steps'), 'core/loop': onE('Loop') });
	try {
		const out = await render(book.root, 'basics/numbers');
		assert.match(out, /<li data-book-track="beginner">Beginner \(B\): <span class="book-top-strip__unwritten">no later page of this track is written yet<\/span><\/li><li data-book-track="engine">Engine builder \(E\): <a href="\/book\/core\/time\/">Time<\/a><\/li>/);
	} finally {
		book.remove();
	}
});

test('the Test out box stands only on primers', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\n${c_TestOut}\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /the Test out box stands only on primers \(style\.md §12\): remove it/);
	} finally {
		book.remove();
	}
});

test('P3: one box, first on the page, five questions each answered with tests that cover every objective', () => {
	const problems = (markdown) => testOutProblems(parseMarkdown(markdown), learn).map((problem) => problem.message);
	assert.deepEqual(problems(`${c_TestOut}\n## Why you will need this\n`), []);
	assert.deepEqual(problems(`<!-- a comment may stand first -->\n\n${c_TestOut}`), []);
	assert.match(problems('## Why you will need this\n\nText.\n').join('\n'), /^P3: a primer opens with its Test out box \(::::test-out holding five questions, each with an :::answer\{tests="…"\}\) before any heading$/);
	assert.match(problems(`Text.\n\n${c_TestOut}`).join('\n'), /P3: the Test out box is the first thing of the page, before any heading and any text/);
	assert.match(problems(`${c_TestOut}\n${c_TestOut}`).join('\n'), /P3: a primer has one Test out box: remove this one/);
	const four = c_TestOut.replace(/\n5\. Question 5\?[\s\S]*?:::\n(?=::::)/, '\n');
	assert.match(problems(four).join('\n'), /P3: the Test out box holds 4 numbered questions; it holds exactly 5/);
	const unanswered = c_TestOut.replace('5. Question 5?\n\n   :::answer{tests="one-thing"}\n   Yes.\n   :::\n', '5. Question 5?\n');
	assert.match(problems(unanswered).join('\n'), /P3: each Test out question is followed by an :::answer\{tests="…"\}: add one/);
	const untested = c_TestOut.replace('5. Question 5?\n\n   :::answer{tests="one-thing"}', '5. Question 5?\n\n   :::answer');
	assert.match(problems(untested).join('\n'), /P3: the answer carries tests="<learn ids>", the objectives the question tests/);
	const narrow = c_TestOut.replace(/tests="another-thing"/g, 'tests="one-thing"');
	assert.match(problems(narrow).join('\n'), /P3: the Test out answers' tests do not cover the learn id "another-thing": a reader who passes the box must know everything the page teaches/);
});

test('P3 fails the build at the box\'s line', async () => {
	const book = primerBook(primerBody(uses).replace(/tests="another-thing"/, 'tests="one-thing"').replace(/tests="another-thing"/, 'tests="one-thing"'));
	try {
		await rejectsWith(render(book.root, 'basics/numbers'), /basics\/numbers\.md:\d+:1: P3: the Test out answers' tests do not cover the learn id "another-thing"/);
	} finally {
		book.remove();
	}
});

test('P1: the exact headings of the body of each kind, in their order, the first one first', () => {
	const problems = (kind, markdown) => bodyHeadingsProblems(parseMarkdown(markdown), kind).map((problem) => problem.message).join('\n');
	assert.equal(problems('primer', '## Why you will need this\n\n## The idea\n\n## Common mistakes\n'), '');
	assert.match(problems('primer', '## The idea\n\n## Why you will need this\n\n## Common mistakes\n'), /P1: the first section of a primer page is "## Why you will need this" \(style\.md §7\)/);
	assert.match(problems('primer', '## Why you will need this\n'), /P1: a primer page has the section "## Common mistakes" \(style\.md §7\): add it/);
	assert.match(problems('internals', '## The job\n\n## How it is tested\n\n## The problem and how engines solve it\n\n## Alternatives Strata did not choose\n\n## Changing it safely\n'), /P1: the sections "## The problem and how engines solve it", "## Alternatives Strata did not choose", "## How it is tested", "## Changing it safely" stand in this order on an internals page/);
	assert.match(problems('tutorial', '## What you need\n\n## What you will make\n'), /the first section of a tutorial page is "## What you will make"/);
	assert.match(problems('how-to', '## Variations\n'), /P1: a how-to page has the section "## Result"/);
	assert.equal(problems('concept', '## The idea\n\n## Common mistakes\n'), '');
	assert.equal(problems('reference', '## Anything\n'), '');
});

test('a worked example stands before the bottom strip of primers, concept and internals pages', async () => {
	const problems = (kind, markdown) => exampleProblems(parseMarkdown(markdown), kind).map((problem) => problem.message).join('\n');
	assert.equal(problems('concept', ':::example\nWorked.\n:::\n\n## Summary\n'), '');
	assert.match(problems('concept', '## Summary\n\n:::example\nToo late.\n:::\n'), /a :::example stands before the bottom strip of a concept page: a worked example comes before the first exercise \(style\.md §8\)/);
	assert.match(problems('primer', 'Text.\n\n## Summary\n'), /before the bottom strip of a primer page/);
	assert.equal(problems('how-to', 'Text.\n'), '');
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\nText.\n${bottomStrip('concept').replace(/\n:::example\n[\s\S]*?\n:::\n/, '')}` } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /core\/time\.md:\d+:1: a :::example stands before the bottom strip of a concept page/);
	} finally {
		book.remove();
	}
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`the Test out box's links to the next pages are under the base ${setting}`, async () => {
		const book = primerBook();
		try {
			const out = await render(book.root, 'basics/numbers', { env: { DOCS_BASE: setting } });
			const box = out.slice(0, out.indexOf('</section>'));
			const links = [...box.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
			assert.deepEqual(links, [`${base}/core/time/`, `${base}/core/time/`]);
		} finally {
			book.remove();
		}
	});
}

test('an internals page\'s general section holds at most a fifth of its prose words', () => {
	assert.equal(proseWords(parseMarkdown('Two words.\n\n```cpp\nint not_prose;\n```\n\nThe `Scene` class and $a + b$.\n').children), 7);
	const page = (general, rest) => parseMarkdown(`## The job\n\n${rest}\n\n## The problem and how engines solve it\n\n${general}\n\n## Changing it safely\n\nText.\n`);
	const words = (count) => Array.from({ length: count }, () => 'word').join(' ');
	assert.deepEqual(generalSectionProblems(page(words(20), words(79)), 'internals'), []);
	const [problem] = generalSectionProblems(page(words(30), words(79)), 'internals');
	assert.match(problem.message, /the section "## The problem and how engines solve it" holds 30 of the page's 110 prose words; it holds at most a fifth \(style\.md §7\.3\)/);
	assert.deepEqual(generalSectionProblems(page(words(30), words(10)), 'concept'), []);
});
