// Tutorials (plan/style.md §7.4 and §10; plan/pipelines.md §6): "::checkpoint{stage=…}" ends each step section with
// the downloads of the project after that step and the picture of what the reader should now have, a release refuses a
// tutorial without a current stamp, and a step that has no menu or button needs the page that teaches running a command
// in the page's Needs closure.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readSettings } from '../../lib/settings.mjs';
import { formatBytes, stampProblems } from '../../lib/tutorials.mjs';
import { checkpointProblems } from '../strips.mjs';
import { parseMarkdown } from '../../lib/markdown.mjs';
import { bottomStrip, c_BottomStrip, c_Pin, c_ReleaseSite, c_TutorialOpening, checkpointPictureFiles, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Commit = /^commit (\S+)/m.exec(c_Pin)[1];
// A test tutorial: its opening sections, `body` (step sections whose checkpoints come before the last one's), and the
// last step section with its checkpoint (step 9 when the body holds checkpoints of its own, else step 1).
const tutorialPage = (body, overrides = {}) => {
	const last = /::checkpoint/.test(body) ? bottomStrip('tutorial').replace('::checkpoint{stage=1}', '::checkpoint{stage=9}') : bottomStrip('tutorial');
	return `${frontmatter({ kind: 'tutorial', ...overrides })}\n${c_TutorialOpening}\n${body}${last}`;
};
const tutorialFile = (stages, extra = {}) => JSON.stringify({ page: 'make/spin', startsFrom: { template: 'basic3d' }, stages, ...extra });
const sha = (text) => createHash('sha256').update(text).digest('hex');

function book(body, files = {}, overrides = {}) {
	return makeBook({ pages: { 'make/spin': tutorialPage(body, overrides) }, files: { ...checkpointPictureFiles('make/spin'), ...files } });
}

test('a checkpoint links the project after its step and the step\'s commands, with their sizes', async () => {
	const files = {
		'tutorials/make/spin.tutorial.json': tutorialFile([{ step: 1, endState: true }]),
		'public/downloads/tutorials/make/spin/stage-1.zip': 'z'.repeat(1_234_567),
		'public/downloads/tutorials/make/spin/stage-1.commands.json': '[]'.repeat(600),
	};
	const spin = book('', files);
	try {
		const out = await render(spin.root, 'make/spin');
		assert.match(out, /<div class="book-checkpoint" role="group" aria-label="Checkpoint 1"><div class="book-checkpoint__downloads" data-pagefind-ignore=""><p class="book-checkpoint__title">Checkpoint 1<\/p><ul><li><a href="\/book\/downloads\/tutorials\/make\/spin\/stage-1\.zip" download>Download the project as it is at this checkpoint<\/a> \(ZIP, 1\.2 MB\)<\/li><li><a href="\/book\/downloads\/tutorials\/make\/spin\/stage-1\.commands\.json" download>Download the editor commands that lead here<\/a> \(JSON, 1 KB\), to run them on your own project<\/li><\/ul><\/div>/);
		// A release with every download and the tutorial file passes the checkpoint (the stamp is tested below).
		assert.equal(formatBytes(340_000), '340 KB');
	} finally {
		spin.remove();
	}
});

test('before the tools publish a stage, the checkpoint is a draft note; a release refuses it', async () => {
	const spin = book('');
	try {
		const out = await render(spin.root, 'make/spin');
		assert.match(out, /<p class="book-checkpoint__title">Checkpoint 1<\/p><p class="book-checkpoint__pending"><span class="book-draft-label">Draft<\/span> The downloads of this checkpoint are made when the tutorial runs against the engine\.<\/p>/);
		const error = await rejectsWith(render(spin.root, 'make/spin', { env: { DOCS_RELEASE: '1' } }), /::checkpoint\{stage=1\}: the page's tutorial file tutorials\/make\/spin\.tutorial\.json does not exist/, /a release has the downloads of every checkpoint, and public\/downloads\/tutorials\/make\/spin\/stage-1\.zip and public\/downloads\/tutorials\/make\/spin\/stage-1\.commands\.json do not exist/);
		assert.match(error.message, /a release has a current stamp of every tutorial, and tutorials\/make\/spin\.stamp\.json does not exist/);
	} finally {
		spin.remove();
	}
});

test('a checkpoint names a stage of the tutorial file that ends in a state the reader can download', async () => {
	const cases = [
		[tutorialFile([{ step: 2, endState: true }]), /::checkpoint\{stage=1\}: tutorials\/make\/spin\.tutorial\.json has no stage with "step": 1 \(its steps: 2\)/],
		[tutorialFile([{ step: 1 }]), /the stage is no end state in tutorials\/make\/spin\.tutorial\.json \("endState": true\)/],
		[tutorialFile([], { patch: { file: 'tutorials/make/spin.patch' } }), /changes the engine with a patch, which has no project to download/],
		[JSON.stringify({ page: 'make/other', stages: [] }), /says "page": "make\/other"; it is the tutorial of make\/spin/],
		['{ not json', /tutorials\/make\/spin\.tutorial\.json is not valid JSON/],
	];
	for (const [tutorial, pattern] of cases) {
		const spin = book('', { 'tutorials/make/spin.tutorial.json': tutorial });
		try {
			await rejectsWith(render(spin.root, 'make/spin'), pattern);
		} finally {
			spin.remove();
		}
	}
	// A tutorial that starts from a sample publishes no project: its checkpoint offers the step's commands only.
	const sample = book('', { 'tutorials/make/spin.tutorial.json': tutorialFile([{ step: 1 }], { startsFrom: { sample: 'Showcase' } }), 'public/downloads/tutorials/make/spin/stage-1.commands.json': '[]' });
	try {
		const out = await render(sample.root, 'make/spin');
		assert.match(out, /This tutorial starts from a sample project, which you already have/);
		assert.doesNotMatch(out, /stage-1\.zip/);
		assert.match(out, /stage-1\.commands\.json/);
	} finally {
		sample.remove();
	}
});

test('a checkpoint stands only on tutorials, names its step, and the steps go up', async () => {
	const concept = makeBook({ pages: { 'core/time': `${frontmatter()}\nText.\n\n::checkpoint{stage=1}\n${c_BottomStrip}` } });
	try {
		await rejectsWith(render(concept.root, 'core/time'), /::checkpoint ends a section of a tutorial \(style\.md §7\.4\); this page's kind is concept/);
	} finally {
		concept.remove();
	}
	for (const [body, pattern] of [
		['## Step one\n\nDo it.\n\n::checkpoint\n', /::checkpoint needs the number of the step it ends: ::checkpoint\{stage=4\}/],
		['## Step one\n\nDo it.\n\n::checkpoint{stage=two}\n', /::checkpoint needs the number of the step it ends/],
		['## Step one\n\nDo it.\n\n::checkpoint{stage=3}\n\n## Step two\n\nDo it.\n\n::checkpoint{stage=2}\n', /::checkpoint\{stage=2\} comes after the checkpoint of step 3: the steps of a page's checkpoints go up/],
		['## Step one\n\nDo it.\n\n::checkpoint{stage=1 zip=yes}\n', /::checkpoint has no attribute "zip" \(it takes stage\)/],
	]) {
		const spin = book(body);
		try {
			await rejectsWith(render(spin.root, 'make/spin'), pattern);
		} finally {
			spin.remove();
		}
	}
});

test('a checkpoint takes in the picture after it, headed "You should now have", inside its group', async () => {
	const spin = book('');
	try {
		const out = await render(spin.root, 'make/spin');
		assert.match(out, /<div class="book-checkpoint" role="group" aria-label="Checkpoint 1"><div class="book-checkpoint__downloads" data-pagefind-ignore="">[\s\S]*?<\/div><div class="book-checkpoint__picture"><p class="book-checkpoint__have">You should now have<\/p><figure class="book-figure" id="fig-now"><div class="book-figure__drawing" role="img" aria-label="A cube on the ground\." tabindex="0"><svg[\s\S]*?<\/svg><\/div><figcaption>The project as it is now\.<\/figcaption><\/figure><\/div><\/div>/);
		// The picture moved into the box: the page holds it once.
		assert.equal(out.match(/<figure /g).length, 1);
	} finally {
		spin.remove();
	}
	// The recipe of the picture is the page's: an unknown id is the figures plugin's problem, reported once.
	const unknown = book('', { 'src/content/figures/make/spin.json': JSON.stringify({ figures: [] }) });
	try {
		const error = await rejectsWith(render(unknown.root, 'make/spin'), /::figure\{id=now\}: src\/content\/figures\/make\/spin\.json has no figure "now"/);
		assert.doesNotMatch(error.message, /is followed by its picture/);
	} finally {
		unknown.remove();
	}
});

test('a checkpoint without its picture, or with a slider for it, fails at the checkpoint\'s line', async () => {
	const strip = (picture) => bottomStrip('tutorial').replace('\n::figure{id=now}\n', picture);
	const page = (picture) => `${frontmatter({ kind: 'tutorial' })}\n${c_TutorialOpening}${strip(picture)}`;
	const without = makeBook({ pages: { 'make/spin': page('') }, files: checkpointPictureFiles('make/spin') });
	try {
		const error = await rejectsWith(render(without.root, 'make/spin'), /::checkpoint\{stage=1\} is followed by its picture, headed "You should now have": write ::figure\{id=…\} on the line after it, with a recipe of the page's figure manifest that shows the project at this point \(style\.md §7\.4\)/);
		// The test page's front matter has 17 lines and a blank line; the opening sections take 7 more, the step section 4.
		assert.match(error.message, /spin\.md:31:1: ::checkpoint\{stage=1\} is followed by its picture/);
	} finally {
		without.remove();
	}
	const slider = makeBook({ pages: { 'make/spin': page('\n::compare{id=now}\n') }, files: checkpointPictureFiles('make/spin') });
	try {
		await rejectsWith(render(slider.root, 'make/spin'), /::checkpoint\{stage=1\} is followed by one picture of the project at this point, headed "You should now have": a ::figure\{id=…\}, not a ::compare slider/);
	} finally {
		slider.remove();
	}
});

test('each step section of a tutorial ends with its checkpoint and the checkpoint\'s picture', () => {
	const strip = '\n## Summary\n\n- x\n';
	const page = (sections) => parseMarkdown(`${c_TutorialOpening}\n${sections}${strip}`);
	assert.deepEqual(checkpointProblems(page('## Make it\n\nDo.\n\n::checkpoint{stage=1}\n'), false), []);
	assert.deepEqual(checkpointProblems(page('## Make it\n\nDo.\n\n::checkpoint{stage=1}\n\n::figure{id=now}\n'), false), []);
	const [problem] = checkpointProblems(page('## Make it\n\n::checkpoint{stage=1}\n\nMore text.\n'), false);
	assert.match(problem.message, /the step section "## Make it" of a tutorial ends with ::checkpoint\{stage=…\}, the project as it is after its last step, and then the checkpoint's "You should now have" picture, ::figure\{id=…\} \(style\.md §7\.4\)/);
	// A tutorial that changes the engine has no checkpoints.
	assert.deepEqual(checkpointProblems(page('## Change the engine\n\nPatch it.\n'), true), []);
});

test('a step that has no menu or button needs, in the Needs closure, the page that teaches running a command', async () => {
	const step = '## Make it\n\n1. This step has no menu or button: run the command.\n\n   ```json\n   { "command": "play.start" }\n   ```\n\n::checkpoint{stage=1}\n\n::figure{id=now}\n';
	const pages = (needs) => ({
		'make/spin': tutorialPage(step, { tracks: '[G, B]', needs }),
		'make/commands': `${frontmatter({ kind: 'how-to', tracks: '[G, B]', since: undefined })}\n## Result\n\nIt works.\n\n## Variations\n\n- One thing to know.\n${c_BottomStrip.replace(/^\n## Common mistakes[\s\S]*?(?=\n## Summary)/, '')}`,
	});
	const without = makeBook({ pages: pages('[]'), files: checkpointPictureFiles('make/spin') });
	try {
		await rejectsWith(render(without.root, 'make/spin'), /a step that has no menu or button runs a command, and make\/commands, which teaches running one, is not in the page's Needs closure \(tracks G and B; style\.md §10\)/);
	} finally {
		without.remove();
	}
	const withNeed = makeBook({ pages: pages('[make/commands]'), files: checkpointPictureFiles('make/spin'), outline: (data) => {
		// make/commands comes before the tutorial on both tracks.
		for (const letter of ['G', 'B']) data.tracks[letter].sort((a, b) => (a.id === 'make/commands' ? -1 : b.id === 'make/commands' ? 1 : 0));
		data.parts[1].pages.sort((a) => (a === 'make/commands' ? -1 : 1));
		data.pages.sort((a) => (a.id === 'make/commands' ? -1 : 1));
	} });
	try {
		await render(withNeed.root, 'make/spin');
	} finally {
		withNeed.remove();
	}
});

test('a release needs a current stamp: a passing run at the pin with the inputs as they are now', async () => {
	const tutorial = tutorialFile([{ step: 1, endState: true }]);
	const run = (extra = {}) => ({ build: { kind: 'pin-build' }, engineCommit: c_Commit, inputs: { 'tutorials/make/spin.tutorial.json': sha(tutorial) }, passed: true, ...extra });
	const stamp = (runs) => JSON.stringify({ page: 'make/spin', runs });
	const files = (runs) => ({
		'tutorials/make/spin.tutorial.json': tutorial,
		'tutorials/make/spin.stamp.json': stamp(runs),
		'public/downloads/tutorials/make/spin/stage-1.zip': 'zip',
		'public/downloads/tutorials/make/spin/stage-1.commands.json': '[]',
	});
	const settingsOf = (root) => readSettings({ root, env: { DOCS_BASE: '/book', DOCS_SITE: c_ReleaseSite, DOCS_RELEASE: '1' } });
	const cases = [
		[[run()], []],
		[[run({ passed: false })], [/no run by a pin build or a patch build passed at the pin/]],
		[[run({ engineCommit: '0'.repeat(40) })], [/run 1 was at engine 00000000, not at the pin 822a7a46/]],
		[[run({ inputs: { 'tutorials/make/spin.tutorial.json': sha('older') } })], [/run 1: tutorials\/make\/spin\.tutorial\.json changed since the run/]],
		[[run({ inputs: { 'tutorials/make/other.json': sha('x') } })], [/its inputs do not hold tutorials\/make\/spin\.tutorial\.json/]],
		[[run({ inputs: { 'tutorials/make/spin.tutorial.json': sha(tutorial), 'tutorials/make/spin/Gone.cpp': sha('x') } })], [/the input tutorials\/make\/spin\/Gone\.cpp does not exist/]],
		[[run({ build: { kind: 'package' } })], [/no run by a pin build or a patch build/]],
	];
	for (const [runs, patterns] of cases) {
		const spin = book('', files(runs), { status: 'reviewed' });
		try {
			const problems = stampProblems(settingsOf(spin.root), 'make/spin');
			assert.equal(problems.length, patterns.length, problems.join('\n'));
			patterns.forEach((pattern, index) => assert.match(problems[index], pattern));
			if (patterns.length === 0) await render(spin.root, 'make/spin', { env: { DOCS_RELEASE: '1' } });
			else await rejectsWith(render(spin.root, 'make/spin', { env: { DOCS_RELEASE: '1' } }), patterns[0]);
		} finally {
			spin.remove();
		}
	}
	// At a release pin (not a pre-release), a run of the release's package passes too.
	const released = book('', { ...files([run()]), 'engine.pin': c_Pin.replace('prerelease yes', 'prerelease no') }, { status: 'reviewed' });
	try {
		const [problem] = stampProblems(settingsOf(released.root), 'make/spin');
		assert.match(problem, /at a release pin a run of the release's package passes too/);
	} finally {
		released.remove();
	}
	// A tutorial that changes the engine cannot run in a package: its patch, or a chain that applies one, needs none.
	const patched = tutorialFile([{ step: 1, endState: true }], { patch: { file: 'tutorials/make/spin.patch' } });
	const patchRun = { build: { kind: 'patch-build' }, engineCommit: c_Commit, inputs: { 'tutorials/make/spin.tutorial.json': sha(patched) }, passed: true };
	const afterPatch = JSON.stringify({ page: 'make/turn', startsFrom: { tutorial: 'make/spin' }, stages: [{ step: 1, endState: true }] });
	const turnRun = { build: { kind: 'patch-build' }, engineCommit: c_Commit, inputs: { 'tutorials/make/turn.tutorial.json': sha(afterPatch) }, passed: true };
	const engine = book('', {
		'tutorials/make/spin.tutorial.json': patched,
		'tutorials/make/spin.stamp.json': stamp([patchRun]),
		'tutorials/make/turn.tutorial.json': afterPatch,
		'tutorials/make/turn.stamp.json': JSON.stringify({ page: 'make/turn', runs: [turnRun] }),
		'engine.pin': c_Pin.replace('prerelease yes', 'prerelease no'),
	}, { status: 'reviewed' });
	try {
		assert.deepEqual(stampProblems(settingsOf(engine.root), 'make/spin'), []);
		assert.deepEqual(stampProblems(settingsOf(engine.root), 'make/turn'), []);
	} finally {
		engine.remove();
	}
	// A draft build reads no stamp.
	const draft = book('', { 'tutorials/make/spin.tutorial.json': tutorial });
	try {
		await render(draft.root, 'make/spin');
	} finally {
		draft.remove();
	}
});

for (const [setting, base] of [['/', ''], ['/strata-engine-docs', '/strata-engine-docs'], ['/x/y', '/x/y']]) {
	test(`a checkpoint's downloads are under the base ${setting}`, async () => {
		const spin = book('', {
			'tutorials/make/spin.tutorial.json': tutorialFile([{ step: 1, endState: true }]),
			'public/downloads/tutorials/make/spin/stage-1.zip': 'zip',
			'public/downloads/tutorials/make/spin/stage-1.commands.json': '[]',
		});
		try {
			const out = await render(spin.root, 'make/spin', { env: { DOCS_BASE: setting } });
			assert.match(out, new RegExp(`href="${base}/downloads/tutorials/make/spin/stage-1\\.zip"`));
			assert.match(out, new RegExp(`href="${base}/downloads/tutorials/make/spin/stage-1\\.commands\\.json"`));
		} finally {
			spin.remove();
		}
	});
}

test('a how-to offers its tutorial file\'s last stage at the end of its Result, and no other stage', async () => {
	const page = `${frontmatter({ kind: 'how-to' })}\n## Make the room\n\nDo it.\n\n## Light it\n\nDo it.\n${bottomStrip('how-to')}`;
	const tutorial = tutorialFile([{ step: 1, endState: true }, { step: 2, endState: true }]);
	const files = {
		'tutorials/make/spin.tutorial.json': tutorial,
		'public/downloads/tutorials/make/spin/stage-2.zip': 'z'.repeat(2_500_000),
		'public/downloads/tutorials/make/spin/stage-2.commands.json': '[]'.repeat(900),
	};
	const howTo = makeBook({ pages: { 'make/spin': page }, files });
	try {
		const out = await render(howTo.root, 'make/spin');
		assert.match(out, /<h2[^>]*>Result<\/h2>[\s\S]*?<p>It works\.<\/p>\s*<div class="book-checkpoint book-result" role="group" aria-label="The result"><div class="book-checkpoint__downloads" data-pagefind-ignore=""><p class="book-checkpoint__title">The result<\/p><ul><li><a href="\/book\/downloads\/tutorials\/make\/spin\/stage-2\.zip" download>Download the project as it is at the end<\/a> \(ZIP, 2\.5 MB\)<\/li><li><a href="\/book\/downloads\/tutorials\/make\/spin\/stage-2\.commands\.json" download>Download the editor commands of the last step<\/a> \(JSON, 2 KB\), to run them on your own project<\/li><\/ul><\/div><\/div>[\s\S]*?<h2[^>]*>Variations<\/h2>/);
		assert.doesNotMatch(out, /stage-1\./);
	} finally {
		howTo.remove();
	}
	// Before the tools publish the stage, the box is a draft note, and a release refuses it.
	const pending = makeBook({ pages: { 'make/spin': page }, files: { 'tutorials/make/spin.tutorial.json': tutorial } });
	try {
		assert.match(await render(pending.root, 'make/spin'), /<p class="book-checkpoint__title">The result<\/p><p class="book-checkpoint__pending"><span class="book-draft-label">Draft<\/span> The downloads of the result are made when the how-to runs against the engine\.<\/p>/);
		await rejectsWith(render(pending.root, 'make/spin', { env: { DOCS_RELEASE: '1' } }), /a release has the download of a how-to's end state, the last stage of tutorials\/make\/spin\.tutorial\.json, and public\/downloads\/tutorials\/make\/spin\/stage-2\.zip and public\/downloads\/tutorials\/make\/spin\/stage-2\.commands\.json do not exist/);
	} finally {
		pending.remove();
	}
	// A how-to without a tutorial file has nothing to download.
	const plain = makeBook({ pages: { 'make/spin': page } });
	try {
		assert.doesNotMatch(await render(plain.root, 'make/spin'), /book-result/);
	} finally {
		plain.remove();
	}
});

test('the checkpoint box prints whole, with its picture', () => {
	const print = readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', 'styles', 'print.css'), 'utf8');
	assert.match(print, /\.book-checkpoint,/);
});
