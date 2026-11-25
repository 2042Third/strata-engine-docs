// Worked solutions (plan/style.md §8; plan/pipelines.md §4, §6.2 and §6.3): an answer's `solution` names the file the
// book's checks run, and the reader gets it from the page. A sketch is shown in full in the answer with its output; an
// editor exercise or an engine exercise is linked as its download under the base, which a draft may lack and a release
// may not.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseSolution } from '../answers.mjs';
import { c_BottomStrip, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Sketch = 'int main() { return 0; }';

/** An answer with a solution, as a page holds it: its label, its attributes and its body. */
function answer(solution, body = 'Done.') {
	return `Do it.\n\n:::answer[Worked solution]{tests="one-thing" solution="${solution}"}\n${body}\n:::\n`;
}

function sketchFences(name, { output = true } = {}) {
	const sketch = `The whole program:\n\n\`\`\`cpp sketch="${name}"\n${c_Sketch}\n\`\`\`\n`;
	return output ? `${sketch}\nIt prints:\n\n\`\`\`text output-of="${name}"\nnothing\n\`\`\`\n` : sketch;
}

function bookWith(body, files = {}) {
	return makeBook({ pages: { 'core/time': `${frontmatter()}\n${body}\n${c_BottomStrip}` }, files });
}

async function renders(body, files, options) {
	const book = bookWith(body, files);
	try {
		return await render(book.root, 'core/time', options);
	} finally {
		book.remove();
	}
}

async function fails(body, files, ...patterns) {
	const book = bookWith(body, files);
	try {
		return await rejectsWith(render(book.root, 'core/time'), ...patterns);
	} finally {
		book.remove();
	}
}

test('a solution names a sketch of its page, or an exercise file of its page', () => {
	assert.deepEqual(parseSolution('sketches/core-time-answer.cpp', 'core/time'), { kind: 'sketch', name: 'core-time-answer.cpp' });
	assert.deepEqual(parseSolution('tutorials/core/time/exercise-2.tutorial.json', 'core/time'), { kind: 'exercise', file: 'tutorials/core/time/exercise-2.tutorial.json', format: 'zip' });
	assert.deepEqual(parseSolution('tutorials/core/time/exercise-1.patch', 'core/time'), { kind: 'exercise', file: 'tutorials/core/time/exercise-1.patch', format: 'patch' });
	assert.match(parseSolution('sketches/answer.cpp', 'core/time').error, /solution="sketches\/answer\.cpp": a sketch's file name starts with its page's id, core-time-<name>\.<extension>/);
	assert.match(parseSolution('tutorials/world/ecs/exercise-1.patch', 'core/time').error, /the solution of an exercise is a file of its own page, tutorials\/core\/time\/exercise-<n>\.patch/);
	assert.match(parseSolution('tutorials/core/time/exercise-0.patch', 'core/time').error, /names the file of a worked solution/);
	assert.match(parseSolution('solutions/one.zip', 'core/time').error, /solution="solutions\/one\.zip" names the file of a worked solution: a sketch the answer shows with its output \(solution="sketches\/core-time-<name>\.cpp"\), an editor exercise \(solution="tutorials\/core\/time\/exercise-<n>\.tutorial\.json"\) or an engine exercise \(solution="tutorials\/core\/time\/exercise-<n>\.patch"\) \(style\.md §8\)/);
});

test('a sketch solution is shown in full in its answer, with its output, and has no download', async () => {
	const files = { 'sketches/core-time-answer.cpp': `${c_Sketch}\n` };
	const out = await renders(answer('sketches/core-time-answer.cpp', sketchFences('core-time-answer.cpp')), files);
	assert.match(out, /<details class="book-answer"><summary>Worked solution<\/summary><div class="book-answer__body"><p>The whole program:<\/p><div class="book-excerpt book-code book-code--sketch">/);
	assert.match(out, /book-code--output/);
	assert.doesNotMatch(out, /book-answer__download|book-answer__pending/);
	// The sketch stands before the answer, or the answer shows no output: the reader would not have the whole solution.
	await fails(`${sketchFences('core-time-answer.cpp')}\n${answer('sketches/core-time-answer.cpp')}`, files, /solution="sketches\/core-time-answer\.cpp": the answer shows the sketch in full, with its output: a fence with sketch="core-time-answer\.cpp", then its ```text output-of="core-time-answer\.cpp" fence \(style\.md §8\)/);
	await fails(answer('sketches/core-time-answer.cpp', sketchFences('core-time-answer.cpp', { output: false })), files, /the answer shows the sketch in full, with its output/);
	// The sketch's file is compared with the fence as everywhere (src/plugins/excerpts.mjs).
	await fails(answer('sketches/core-time-answer.cpp', sketchFences('core-time-answer.cpp')), {}, /sketch="core-time-answer\.cpp": sketches\/core-time-answer\.cpp does not exist/);
});

test('an exercise\'s solution links its download with its size; until the tools write it, a draft note', async () => {
	const files = {
		'tutorials/core/time/exercise-1.tutorial.json': '{}',
		'tutorials/core/time/exercise-2.patch': 'diff',
		'public/downloads/solutions/core/time/exercise-1.zip': 'z'.repeat(3_400),
		'public/downloads/solutions/core/time/exercise-2.patch': 'p'.repeat(1_900),
	};
	const out = await renders(`${answer('tutorials/core/time/exercise-1.tutorial.json')}\n${answer('tutorials/core/time/exercise-2.patch')}`, files);
	assert.match(out, /<div class="book-answer__body"><p>Done\.<\/p><p class="book-answer__download"><a href="\/book\/downloads\/solutions\/core\/time\/exercise-1\.zip" download>Download the worked solution<\/a> \(ZIP, 3 KB\): the editor commands of the solution and the files they copy, to run on your own project<\/p><\/div>/);
	assert.match(out, /<a href="\/book\/downloads\/solutions\/core\/time\/exercise-2\.patch" download>Download the worked solution<\/a> \(patch, 2 KB\): the solution's change to the engine's source, to apply with git apply<\/p>/);
	// The answer never names the book's repository: the reader gets the file only as the download.
	assert.doesNotMatch(out, /tutorials\/core\/time\/exercise/);
	const pending = await renders(answer('tutorials/core/time/exercise-1.tutorial.json'), { 'tutorials/core/time/exercise-1.tutorial.json': '{}' });
	assert.match(pending, /<p class="book-answer__pending"><span class="book-draft-label">Draft<\/span> The download of this solution is made when the book's checks run it against the engine\.<\/p>/);
	const book = bookWith(answer('tutorials/core/time/exercise-1.tutorial.json'), { 'tutorials/core/time/exercise-1.tutorial.json': '{}' });
	try {
		await rejectsWith(render(book.root, 'core/time', { env: { DOCS_RELEASE: '1' } }), /solution="tutorials\/core\/time\/exercise-1\.tutorial\.json": a release has the download of every worked solution, and public\/downloads\/solutions\/core\/time\/exercise-1\.zip does not exist: write it with python -I tools\/tutorials\.py compile/);
	} finally {
		book.remove();
	}
});

test('a solution names a file that exists, in one of the three forms, at the answer\'s line', async () => {
	const error = await fails(`Text.\n\n${answer('tutorials/core/time/exercise-3.patch')}\n${answer('sketches/answer.cpp')}`, {}, /solution="tutorials\/core\/time\/exercise-3\.patch": tutorials\/core\/time\/exercise-3\.patch does not exist/, /solution="sketches\/answer\.cpp": a sketch's file name starts with its page's id/);
	// The test page's front matter has 17 lines and a blank line; "Text." and a blank line, then the question.
	assert.match(error.message, /time\.md:23:1: solution="tutorials\/core\/time\/exercise-3\.patch"/);
	await fails(answer(''), {}, /:::answer\{solution=""\} names no file/);
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`a worked solution's download is under the base ${setting}`, async () => {
		const files = { 'tutorials/core/time/exercise-1.patch': 'diff', 'public/downloads/solutions/core/time/exercise-1.patch': 'diff' };
		const out = await renders(answer('tutorials/core/time/exercise-1.patch'), files, { env: { DOCS_BASE: setting } });
		assert.match(out, new RegExp(`<a href="${base}/downloads/solutions/core/time/exercise-1\\.patch" download>`));
	});
}
