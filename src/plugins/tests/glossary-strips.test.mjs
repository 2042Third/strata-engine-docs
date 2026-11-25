// The glossary's links and list, and the strips plugin's check of the bottom strip (src/plugins/tests/frontmatter.test.mjs
// tests its checks of the front matter).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { glossaryId, normalizeGlossary } from '../../lib/glossary.mjs';
import { parseMarkdown } from '../../lib/markdown.mjs';
import { bottomStripProblems } from '../strips.mjs';
import { bottomStrip, c_BottomStrip, c_ReferenceStrip, frontmatter, makeBook, primerBody, rejectsWith, render } from './helpers.mjs';

const glossary = {
	terms: [
		{ id: 'fixed-step', term: 'fixed step', definition: 'A slice of simulated time of one length.', home: 'core/time' },
		{ id: 'draw-call', term: 'draw call', definition: 'One request to the GPU to draw.', home: 'gpu/draw' },
		{ id: 'taa', term: 'TAA', definition: 'Temporal anti-aliasing.', home: 'image/taa' },
	],
};
const glossaryPage = `${frontmatter({ title: '"Glossary"', kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\nThe list.\n\n::glossary\n${c_ReferenceStrip}`;

test('an entry\'s id is its term in lowercase words joined by "-", as tools/pages.py writes it', () => {
	assert.equal(glossaryId('draw call'), 'draw-call');
	assert.equal(glossaryId('TAA'), 'taa');
	assert.equal(glossaryId("two's complement"), 'twos-complement');
	assert.equal(glossaryId('Newton’s laws of motion'), 'newtons-laws-of-motion');
	assert.equal(glossaryId('Rec. 709'), 'rec-709');
	assert.equal(glossaryId('C++ template'), 'c-template');
	assert.equal(glossaryId('big-O notation'), 'big-o-notation');
});

test('the build reads each entry\'s id from the file and refuses an entry it could not link', () => {
	const read = (terms) => normalizeGlossary({ terms }).problems.join('\n');
	const { terms } = normalizeGlossary({ terms: [{ id: 'hot-reload-script', term: 'hot reload (script)', definition: 'A thing.', home: 'scripting/hot-reload', use: 'make/first-script', known: false, aliases: ['reload'], avoid: ['live coding'] }] });
	assert.deepEqual(terms, [{ id: 'hot-reload-script', term: 'hot reload (script)', definition: 'A thing.', home: 'scripting/hot-reload', use: 'make/first-script', aliases: ['reload'], avoid: ['live coding'], known: false }]);
	assert.match(read([{ term: 'draw call', definition: 'A thing.', home: 'gpu/draw' }]), /term 1 \(draw call\): "id" is missing: write "id": "draw-call"/);
	assert.match(read([{ id: 'drawcall', term: 'draw call', definition: 'A thing.', home: 'gpu/draw' }]), /"id" is the term in lowercase words joined by "-": write "id": "draw-call"/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.', home: 'core/time', level: 2 }]), /term 1 \(step\): "level" is not a key of an entry \(id, term, definition, home, use, aliases, avoid, known\)/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.' }]), /"home" must be the id of the page that defines the term/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.', home: 'core/time', use: 'core/loop' }]), /"use" names the page of part make where a game maker uses the term/);
	assert.match(read([{ id: 'folder', term: 'folder', definition: 'A thing.', home: 'basics/tools', known: 'yes' }]), /"known" is true or false/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.', home: 'core/time', avoid: 'tick' }]), /"avoid" must be a list of names/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.', home: 'core/time', avoid: ['tick'] }, { id: 'tick', term: 'tick', definition: 'A thing.', home: 'core/time' }]), /"step": the avoided name "tick" is a name of "tick": the book uses a name or avoids it, not both/);
	assert.match(read([{ id: 'step', term: 'step', definition: 'A thing.', home: 'core/time' }, { id: 'step', term: 'Step!', definition: 'A thing.', home: 'core/time' }]), /the id "step" also names "step": two meanings get two qualified terms/);
});

test('the glossary rejects one name for two things and definitions longer than a sentence', () => {
	const { problems } = normalizeGlossary({ terms: [{ id: 'step', term: 'step', definition: 'One. Two.', home: 'core/time' }, { id: 'pace', term: 'pace', definition: 'A thing.', home: 'core/time', aliases: ['Step'] }] });
	assert.ok(problems.some((problem) => /one sentence/.test(problem)));
	assert.ok(problems.some((problem) => /the name "Step" also names "step"/.test(problem)));
});

test('the build links no term on its own: a use the writer did not mark stays words, with no title', async () => {
	const page = `${frontmatter()}\n## A fixed step heading\n\nEach draw call costs. More draw calls cost more. \`fixed step\` in code, then a fixed step and TAA.\n${c_BottomStrip}`;
	const book = makeBook({ glossary, pages: { 'world/ecs': page, 'reference/glossary': glossaryPage } });
	try {
		const out = await render(book.root, 'world/ecs');
		assert.match(out, /<p>Each draw call costs\. More draw calls cost more\. <code>fixed step<\/code> in code, then a fixed step and TAA\.<\/p>/);
		assert.doesNotMatch(out, /book-term|glossary\/#|title=/);
	} finally {
		book.remove();
	}
});

test('the glossary page lists every entry in one <dl>, each <dt> a result of its own in search', async () => {
	const terms = { terms: [
		...glossary.terms,
		{ id: 'script-field', term: 'script field', definition: 'A value of a script that the editor shows.', home: 'scripting/fields', use: 'make/first-script', aliases: ['field'] },
	] };
	const home = `${frontmatter({ title: '"Time"' })}\nA **fixed step** is a slice.\n${c_BottomStrip}`;
	const use = `${frontmatter({ title: '"Your first script"' })}\nText.\n${c_BottomStrip}`;
	const book = makeBook({ glossary: terms, pages: { 'core/time': home, 'make/first-script': use, 'reference/glossary': glossaryPage } });
	try {
		const list = await render(book.root, 'reference/glossary');
		assert.equal(list.match(/<dl class="book-glossary">/g).length, 1);
		// Alphabetical: draw call, fixed step, script field, TAA.
		assert.deepEqual([...list.matchAll(/<dt id="([^"]+)"/g)].map((match) => match[1]), ['draw-call', 'fixed-step', 'script-field', 'taa']);
		// The definition and its links stay out of the search index (the term and its other names stay in).
		assert.match(list, /<dt id="fixed-step" data-pagefind-title="fixed step">fixed step<\/dt><dd><span class="book-glossary__definition" data-pagefind-ignore="">A slice of simulated time of one length\. <a href="\/book\/core\/time\/">Read: Time<\/a><\/span><\/dd>/);
		// An entry whose home page is not written yet names no page.
		assert.match(list, /<dt id="draw-call" data-pagefind-title="draw call">draw call<\/dt><dd><span class="book-glossary__definition" data-pagefind-ignore="">One request to the GPU to draw\.<\/span><\/dd>/);
		// A term a game maker acts on also links its page of part make, once that page is written.
		assert.match(list, /<dt id="script-field" data-pagefind-title="script field">script field<\/dt><dd><span class="book-glossary__definition" data-pagefind-ignore="">A value of a script that the editor shows\. <a href="\/book\/make\/first-script\/">Used in: Your first script<\/a><\/span><span class="book-glossary__aliases"> Also called: field\.<\/span><\/dd>/);
	} finally {
		book.remove();
	}
});

test('the glossary page has no table of contents', async () => {
	const withContents = `${frontmatter({ title: '"Glossary"', kind: 'reference', tracks: '[]' })}\nThe list.\n\n::glossary\n${c_ReferenceStrip}`;
	const book = makeBook({ glossary, pages: { 'reference/glossary': withContents } });
	try {
		// The front matter has 10 lines and a blank line: "The list.", a blank line, then the directive.
		await rejectsWith(render(book.root, 'reference/glossary'), /glossary\.md:14:1: reference\/glossary\.md sets "tableOfContents: false" in its front matter: the list of every term needs no table of contents/);
	} finally {
		book.remove();
	}
});

test('the glossary list stands only on the glossary page, and a glossary with terms needs that page', async () => {
	const elsewhere = makeBook({ glossary, pages: { 'core/time': `${frontmatter()}\nText.\n\n::glossary\n${c_BottomStrip}`, 'reference/glossary': glossaryPage } });
	try {
		const error = await rejectsWith(render(elsewhere.root, 'core/time'), /::glossary belongs on reference\/glossary\.md/);
		// The test page's front matter has 17 lines and a blank line; "Text." and a blank line, then the directive.
		assert.match(error.message, /time\.md:21:1: ::glossary belongs on/);
		assert.match(await render(elsewhere.root, 'reference/glossary'), /<dl class="book-glossary">/);
	} finally {
		elsewhere.remove();
	}
	const missing = makeBook({ glossary, pages: { 'core/time': `${frontmatter()}\nText.\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(missing.root, 'core/time'), /src\/content\/glossary\.json has terms, but the glossary page reference\/glossary\.md does not exist/);
	} finally {
		missing.remove();
	}
});

test('the bottom strip needs its five sections in order and the right number of questions, each answered', async () => {
	const page = `${frontmatter()}\nText.\n\n## Common mistakes\n\n- z\n\n## Summary\n\n- x\n\n## Exercises\n\n1. Do.\n\n## Check yourself\n\n1. Q?\n\n   :::answer\n   A.\n   :::\n\n## Further reading\n\n- y\n`;
	const book = makeBook({ pages: { 'core/time': page } });
	try {
		await rejectsWith(
			render(book.root, 'core/time'),
			/every question and exercise under "## Exercises" is followed by an :::answer/,
			/P1: "## Check yourself" holds 1 numbered items; it holds 3 to 6/,
			/P1: a concept page ends with the sections "## Summary", "## Check yourself", "## Exercises", "## Where it lives in Strata", "## Further reading", in this order \(style\.md §6\.3\); its last sections are "## Common mistakes", "## Summary", "## Exercises", "## Check yourself", "## Further reading" \(missing: "## Where it lives in Strata"\)/,
			/P1: "## Summary" holds 1 bulleted items; it holds one per objective of "learn" \(2\)/,
		);
	} finally {
		book.remove();
	}
});

test('the body ends with the section of its kind, and the bottom strip ends the page', () => {
	const strip = bottomStrip('concept').replace(/^\n## Common mistakes\n\n- One thing to know\.\n/, '');
	const body = (...titles) => titles.map((title) => `\n## ${title}\n\nText.\n`).join('');
	const problems = (kind, markdown) => bottomStripProblems(parseMarkdown(`Intro.\n${markdown}`), kind, 2).map((problem) => problem.message).join('\n');
	assert.match(problems('concept', `${body('The idea')}${strip}`), /^P1: the body of a concept page ends with "## Common mistakes" before the bottom strip/);
	assert.equal(problems('concept', `${body('The idea', 'Common mistakes')}${strip}`), '');
	assert.equal(problems('internals', `${body('Changing it safely')}${strip}`), '');
	assert.equal(problems('internals', `${body('Changing it safely', 'What went wrong before')}${strip}`), '');
	assert.match(problems('internals', `${body('What went wrong before')}${strip}`), /^P1: the body of an internals page ends with "## Changing it safely", followed by "## What went wrong before" when the history has one/);
	assert.match(problems('tutorial', `${body('What you will make', 'What you need')}${strip}`), /^P1: a tutorial ends its body with its last step section/);
	assert.match(problems('tutorial', strip), /^P1: a tutorial ends its body with its last step section/);
	assert.equal(problems('tutorial', `${body('What you will make', 'What you need', 'Make it spin')}${strip}`), '');
	assert.match(problems('how-to', `${body('Result')}${strip}`), /^P1: the body of a how-to page ends with "## Variations"/);
	assert.equal(problems('how-to', `${body('Result', 'Variations')}${strip}`), '');
	assert.match(problems('concept', `${body('Common mistakes')}${strip}${body('More')}`), /^P1: a concept page ends with the sections .*; its last sections are "## Check yourself", "## Exercises", "## Where it lives in Strata", "## Further reading", "## More"$/);
	// A reference page ends with its generated tables and "## Where it lives in Strata"; it has no Summary to count.
	assert.equal(bottomStripProblems(parseMarkdown('The table.\n\n## Where it lives in Strata\n\n- a file\n'), 'reference', 0).length, 0);
});

test('a question is a numbered item, and its answer may follow it outside the item', async () => {
	const question = (n, indent = '   ') => `${n}. Question ${n}?\n\n${indent}:::answer{tests="one-thing another-thing"}\n${indent}Yes.\n${indent}:::\n`;
	const check = (items) => `## Check yourself\n\n${items.join('\n')}`;
	const withCheck = (items) => c_BottomStrip.replace(/## Check yourself\n[\s\S]*?(?=## Exercises)/, `${check(items)}\n`);
	const book = makeBook({
		pages: {
			// The answers stand at the left margin, which ends the list: each new number starts a list of its own.
			'core/margin': `${frontmatter()}\nText.\n${withCheck([1, 2, 3].map((n) => question(n, '')))}`,
			'core/seven': `${frontmatter()}\nText.\n${withCheck([1, 2, 3, 4, 5, 6, 7].map((n) => question(n)))}`,
			'core/unanswered': `${frontmatter()}\nText.\n${withCheck([question(1), question(2), '3. Question 3?\n'])}`,
		},
	});
	try {
		await render(book.root, 'core/margin');
		await rejectsWith(render(book.root, 'core/seven'), /P1: "## Check yourself" holds 7 numbered items; it holds 3 to 6/);
		await rejectsWith(render(book.root, 'core/unanswered'), /every question and exercise under "## Check yourself" is followed by an :::answer/);
	} finally {
		book.remove();
	}
});

test('a primer links at least three pages that have it in their Needs closure', async () => {
	const primer = (uses) => `${frontmatter({ kind: 'primer', tracks: '[B, E]', since: undefined })}\n${primerBody(uses)}`;
	const user = (needs, tracks = '[B, E]') => `${frontmatter({ needs, tracks, since: undefined })}\nText.\n${c_BottomStrip}`;
	const pages = {
		// basics/numbers is the first row of its part: basics/later, whose row has "-", needs it (style.md §1.2).
		'basics/numbers': primer('- [Later](later.md) builds on it.\n- [Count](count.md) counts. [Count again](count.md#_top).\n- [Either](either.md) reads them.\n'),
		'basics/later': user('[]'),
		'basics/count': user('[basics/later]'),
		'basics/either': user('[basics/other|basics/numbers]'),
		// A page that is no row of the outline (the outline below leaves it out; it is on no track).
		'basics/other': user('[]', '[]'),
		'basics/few': primer('- [Later](later.md) uses it.\n- [Either](either.md) too.\n- [The primer itself](few.md).\n'),
		'basics/wrong': primer('- [Later](later.md) uses it.\n- [Count](count.md) counts.\n- [Other](other.md) reads them.\n'),
	};
	const book = makeBook({ pages, outline: (data) => { data.pages = data.pages.filter((row) => row.id !== 'basics/other'); data.parts[2].pages = data.parts[2].pages.filter((id) => id !== 'basics/other'); } });
	try {
		await render(book.root, 'basics/numbers');
		await rejectsWith(render(book.root, 'basics/few'), /"## Where the book uses it" links 2 pages; it links at least 3/);
		const error = await rejectsWith(render(book.root, 'basics/wrong'), /basics\/later does not have basics\/wrong in its Needs closure/, /links basics\/other, which is no row of the outline/);
		assert.doesNotMatch(error.message, /links \d+ pages?;/);
	} finally {
		book.remove();
	}
});

test('a release build refuses draft pages', async () => {
	const book = makeBook({ pages: { 'core/time': `${frontmatter()}\nText.\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /a release build has no draft pages/);
	} finally {
		book.remove();
	}
});

test('a marked term links to its entry and is not linked again; an unknown id fails', async () => {
	const page = `${frontmatter()}\nEvery :term[draw]{id=draw-call} costs; each draw call more.\n${c_BottomStrip}`;
	const book = makeBook({ glossary, pages: { 'world/ecs': page, 'reference/glossary': glossaryPage } });
	try {
		const out = await render(book.root, 'world/ecs');
		assert.match(out, /Every <span class="book-term-use"><a class="book-term" href="\/book\/reference\/glossary\/#draw-call">draw<\/a><button [^>]*popovertarget="book-term-draw-call" data-pagefind-ignore="">[\s\S]*?<\/span><\/span> costs; each draw call more\./);
	} finally {
		book.remove();
	}
	const wrong = makeBook({ glossary, pages: { 'world/ecs': `${frontmatter()}\nA :term[thing]{id=nothing} here.\n${c_BottomStrip}`, 'reference/glossary': glossaryPage } });
	try {
		await rejectsWith(render(wrong.root, 'world/ecs'), /the glossary has no entry "nothing"/);
	} finally {
		wrong.remove();
	}
});

test('an unknown inline directive with a label or attributes fails; bare a:b prose stays text', async () => {
	const book = makeBook({ pages: { 'world/ecs': `${frontmatter()}\nThere are :count[12]{key=commands.count} commands, and a:b.\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(book.root, 'world/ecs'), /unknown inline directive :count\[…\]: the book knows :term\[text\]\{id=…\}, :since\[release\] and :value\{key=…\}/);
	} finally {
		book.remove();
	}
});

test('the build\'s titles and summaries hold no glossary link, and no link stands inside a marked term', async () => {
	// Aside titles are aria-hidden (a link there is a serious axe violation, aria-hidden-focus); a link inside <summary>
	// competes with opening the answer; a link inside a link is invalid HTML.
	const terms = { terms: [...glossary.terms, { id: 'engine', term: 'engine', definition: 'A program games are made with.', home: 'core/engine' }, { id: 'answer', term: 'answer', definition: 'What a question asks for.', home: 'core/answers' }, { id: 'accumulator', term: 'accumulator', definition: 'The time not yet simulated.', home: 'core/time' }] };
	const page = `${frontmatter()}\n:::why[Why a fixed step?]\nBecause.\n:::\n\n:::elsewhere\nOther tools.\n:::\n\nA question?\n\n:::answer\nYes.\n:::\n\nEach :term[fixed step taken from the accumulator]{id=fixed-step} moves. :term[Draw calls]{id=draw-call} add up.\n${c_BottomStrip}`;
	const book = makeBook({ glossary: terms, pages: { 'world/ecs': page, 'reference/glossary': glossaryPage } });
	try {
		const out = await render(book.root, 'world/ecs');
		assert.match(out, /<p class="starlight-aside__title" aria-hidden="true">Why a fixed step\?<\/p>/);
		assert.match(out, /<p class="starlight-aside__title" aria-hidden="true">In other engines<\/p>/);
		assert.match(out, /<summary>Answer<\/summary>/);
		assert.match(out, /<a class="book-term" href="\/book\/reference\/glossary\/#fixed-step">fixed step taken from the accumulator<\/a>/);
		assert.doesNotMatch(out, /<a [^>]*>[^<]*<a /);
		// A term marked outside those places is linked.
		assert.match(out, /<a class="book-term" href="\/book\/reference\/glossary\/#draw-call"/);
	} finally {
		book.remove();
	}
});

test('a directive a plugin reported is not reported again as unknown', async () => {
	const book = makeBook({ glossary, pages: { 'world/ecs': `${frontmatter()}\nA :term[thing]{id=nothing} here.\n\n::figure{id=nope}\n${c_BottomStrip}`, 'reference/glossary': glossaryPage } });
	try {
		const error = await rejectsWith(render(book.root, 'world/ecs'), /the glossary has no entry "nothing"/, /::figure\{id=nope\}: the page has no figure manifest/);
		assert.doesNotMatch(error.message, /unknown (inline )?directive/);
		assert.match(error.message, /has 2 problems/);
	} finally {
		book.remove();
	}
});
