// Every directive of the book's table (src/lib/directives.mjs) with its accessible name and its print form, in one
// place, so that a directive added to the table without both fails here. The pages of one test book hold every
// directive; Starlight's own asides run through Starlight's plugin after the book's, as in the build. The markup and the
// failure messages of each directive are tested beside its plugin (blocks, directives, figures, diagrams,
// glossary-strips, include, terms, testout, tutorials and answers).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { c_PrintedDetails } from '../../components/client/print.js';
import { c_Directives } from '../../lib/directives.mjs';
import { prefixChapter } from '../../lib/print.mjs';
import { stampedFile } from '../../lib/reference.mjs';
import { bottomStrip, c_ReferenceStrip, c_TutorialOpening, checkpointPictureFiles, frontmatter, makeBook, primerBody, render } from './helpers.mjs';

const c_Here = path.dirname(fileURLToPath(import.meta.url));
const c_Root = path.join(c_Here, '..', '..', '..');
// The style sheets without their comments, so that a rule's selector list is only selectors.
const withoutComments = (css) => css.replace(/\/\*[\s\S]*?\*\//g, '');
const c_PrintCss = withoutComments(readFileSync(path.join(c_Here, '..', '..', 'styles', 'print.css'), 'utf8'));
const c_StarlightPrintSource = readFileSync(path.join(c_Root, 'node_modules', '@astrojs', 'starlight', 'dist', 'style', 'print.css'), 'utf8');
const c_StarlightPrintCss = withoutComments(c_StarlightPrintSource);

// Starlight draws :::note, :::tip, :::caution and :::danger after the book's plugins; its English titles are its own.
const { remarkAsides } = await import(new URL('../../../node_modules/@astrojs/starlight/dist/integrations/remark-asides.js', import.meta.url));
const c_StarlightTitles = { 'aside.note': 'Note', 'aside.tip': 'Tip', 'aside.caution': 'Caution', 'aside.danger': 'Danger' };
const c_Starlight = [remarkAsides({ absolutePathToLang: () => 'en', useTranslations: () => (key) => c_StarlightTitles[key] ?? key })];

/** The declarations of the print style sheet's rule whose selector list holds `selector`. */
function printRule(css, selector) {
	for (const match of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
		const selectors = match[1].split(',').map((item) => item.trim());
		if (selectors.includes(selector)) return match[2];
	}
	return null;
}

/** Whether the book's print style sheet hides anything of the class. */
function hiddenInPrint(className) {
	for (const match of c_PrintCss.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
		if (/display:\s*none/.test(match[2]) && match[1].includes(className)) return true;
	}
	return false;
}

const c_Glossary = { terms: [{ id: 'fixed-step', term: 'fixed step', definition: 'A slice of simulated time of one length.', home: 'core/loop' }] };
const c_Recipes = {
	figures: [
		{ id: 'shot', shows: 'A cube on the ground.', kind: 'scene', caption: 'Notice the cube.', alt: 'A grey cube.', size: [1920, 1080] },
		{ id: 'pair', shows: 'The cube without and with its shadow.', kind: 'scene', caption: 'The shadow grounds it.', alt: 'A cube.', size: [1920, 1080], variants: { off: {}, on: {} } },
	],
};
const c_Table = stampedFile('\n## Budgets\n\n| Test | Budget |\n| --- | --- |\n| `Perf.Scene.Update` | 2.0 ms |\n', '822a7a46dbcdd86e8e2eafde7e41d003e27260c8');
const c_Body = `:::note
A note.
:::

:::tip[Practice this]
A tip.
:::

:::caution
A mistake people make.
:::

:::danger
Data loss.
:::

${['why', 'question', 'history', 'elsewhere', 'rule', 'simplified'].map((name) => `:::${name}\nText.\n:::\n`).join('\n')}
:::analogy
A jar of coins.

**Where it breaks:** a jar has no cap.
:::

:::derivation
The steps.
:::

What does it print?

:::answer
Nothing.
:::

::::tabs{sync=os}
:::tab[Windows]
One.
:::
:::tab[Linux]
Two.
:::
:::tab[macOS]
Three.
:::
::::

:::steps
1. Open the editor.
2. Press **Play**.
:::

:::files
- Spin/
  - Spinner.cpp
:::

::figure{id=shot}

::compare{id=pair}

## New things

:since[0.8.0] Strata counts each :term[fixed step]{id=fixed-step}.

The editor has :value{key="commands.count"} commands.
`;

const c_Uses = '- [Time](../core/time.md) counts with it.\n- [Steps](../core/steps.md) adds them.\n- [Loop](../core/loop.md) reads them.\n';
const user = (title, body = 'Text.') => `${frontmatter({ title: `"${title}"`, needs: '[basics/numbers]', tracks: '[B, E]', since: '0.3.0' })}\n${body}\n${bottomStrip('concept')}`;
const howTo = (body) => `${frontmatter({ kind: 'how-to', tracks: '[G, B, E]', since: undefined })}\n${body}\n${bottomStrip('how-to')}`;

const s_Book = makeBook({
	glossary: c_Glossary,
	pages: {
		'start/how-to-read': howTo('::track-chooser'),
		'make/spin': `${frontmatter({ kind: 'tutorial', tracks: '[G, B]' })}\n${c_TutorialOpening}${bottomStrip('tutorial')}`,
		'basics/numbers': `${frontmatter({ title: '"Numbers"', kind: 'primer', tracks: '[B, E]', since: undefined })}\n${primerBody(c_Uses)}`,
		'core/time': user('Time', c_Body),
		'core/steps': user('Steps'),
		'core/loop': user('Loop'),
		'reference/glossary': `${frontmatter({ kind: 'reference', tracks: '[]', tableOfContents: 'false' })}\nThe list.\n\n::glossary\n${c_ReferenceStrip}`,
		'reference/performance': `${frontmatter({ kind: 'reference', tracks: '[]' })}\nThe table of every perf budget.\n\n::include{file="performance.md"}\n${c_ReferenceStrip}`,
	},
	files: { 'src/content/figures/core/time.json': JSON.stringify(c_Recipes), 'src/generated/reference/performance.md': c_Table, 'src/generated/reference/values.json': '{"commands.count": 151, "engine.commit": "822a7a46dbcdd86e8e2eafde7e41d003e27260c8"}', ...checkpointPictureFiles('make/spin') },
});
const s_Pages = {};
try {
	for (const id of ['start/how-to-read', 'make/spin', 'basics/numbers', 'core/time', 'reference/glossary', 'reference/performance']) {
		s_Pages[id] = await render(s_Book.root, id, { after: c_Starlight });
	}
} finally {
	s_Book.remove();
}
const time = s_Pages['core/time'];

const bookAside = (name, title) => ({
	name: () => assert.match(time, new RegExp(`<aside class="starlight-aside book-aside book-aside--${name}" aria-label="${title}"><p class="starlight-aside__title" aria-hidden="true">${title}</p>`)),
	print: () => assert.match(printRule(c_PrintCss, '.book-aside'), /break-inside: avoid/),
});
const starlightAside = (name, title) => ({
	name: () => assert.match(time, new RegExp(`<aside aria-label="${title}" class="starlight-aside starlight-aside--${name}">`)),
	// Starlight's own print style sheet keeps an aside on one sheet.
	print: () => assert.match(printRule(c_StarlightPrintCss, '.starlight-aside'), /break-inside: avoid/),
});

/** name → { name: its accessible name, print: its print form }, for every directive of the table. */
const c_Forms = {
	note: starlightAside('note', 'Note'),
	tip: starlightAside('tip', 'Practice this'),
	caution: starlightAside('caution', 'Caution'),
	danger: starlightAside('danger', 'Danger'),
	why: bookAside('why', 'Why it is so'),
	question: bookAside('question', 'A question you may have'),
	history: bookAside('history', 'How it came to be'),
	elsewhere: bookAside('elsewhere', 'In other engines'),
	rule: bookAside('rule', 'A rule of the engine'),
	simplified: bookAside('simplified', 'Simplified for now'),
	analogy: bookAside('analogy', 'An analogy'),
	example: bookAside('example', 'Worked example'),
	derivation: {
		// A details element is named by its summary.
		name: () => assert.match(time, /<details class="book-derivation"><summary>Where this comes from<\/summary>/),
		print: () => {
			assert.ok(c_PrintedDetails.split(', ').includes('details.book-derivation'));
			assert.match(printRule(c_PrintCss, 'details.book-derivation::details-content'), /content-visibility: visible/);
		},
	},
	'test-out': {
		name: () => assert.match(s_Pages['basics/numbers'], /^<section class="book-test-out" aria-label="Test out">/),
		// Printed, the box shows its title, instruction and links, and its five answers open as every answer does.
		print: () => {
			assert.equal(hiddenInPrint('book-test-out'), false);
			const box = s_Pages['basics/numbers'].slice(0, s_Pages['basics/numbers'].indexOf('</section>'));
			assert.equal(box.match(/<details class="book-answer">/g).length, 5);
			assert.ok(c_PrintedDetails.split(', ').includes('details.book-answer'));
		},
	},
	answer: {
		name: () => assert.match(time, /<details class="book-answer"><summary>Answer<\/summary>/),
		print: () => assert.match(printRule(c_PrintCss, 'details.book-answer::details-content'), /content-visibility: visible/),
	},
	tabs: {
		// Each panel is named by its label, which the script turns into the tab's name (book.js).
		name: () => assert.match(time, /<book-tabs data-sync="os"><div class="book-tabs__panel" data-label="Windows"><p class="book-tabs__label">Windows<\/p>/),
		// Printed, every panel shows under its label, and the row of tabs is hidden.
		print: () => {
			assert.match(printRule(c_PrintCss, "book-tabs[data-enhanced] .book-tabs__panel[hidden]"), /display: block !important/);
			assert.match(printRule(c_PrintCss, 'book-tabs[data-enhanced] .book-tabs__label'), /display: block/);
			assert.match(printRule(c_PrintCss, '.book-tabs__list'), /display: none !important/);
		},
	},
	tab: {
		name: () => assert.match(time, /data-label="Linux"><p class="book-tabs__label">Linux<\/p>/),
		print: () => assert.match(printRule(c_PrintCss, "book-tabs[data-enhanced] .book-tabs__panel[hidden]"), /display: block !important/),
	},
	steps: {
		// Without list markers, role="list" keeps the list a list for screen readers.
		name: () => assert.match(time, /<ol class="sl-steps" role="list">/),
		print: () => assert.match(printRule(c_PrintCss, '.sl-steps > li::before'), /color: #000;/),
	},
	files: {
		name: () => assert.match(time, /<figure class="book-files" aria-label="Files and folders">[\s\S]*?<span class="sr-only">Folder <\/span>Spin\//),
		print: () => assert.match(printRule(c_PrintCss, '.book-files'), /break-inside: avoid/),
	},
	figure: {
		// A picture not taken yet is a placeholder named by the recipe's alt text; the caption names the figure.
		name: () => assert.match(time, /<figure class="book-figure" id="fig-shot"><div class="book-placeholder" role="img" aria-label="A grey cube\." [^>]*>[\s\S]*?<figcaption>Notice the cube\./),
		print: () => assert.match(printRule(c_PrintCss, '.book-figure'), /break-inside: avoid/),
	},
	compare: {
		name: () => assert.match(time, /<div class="book-compare__item" data-label="off"><div class="book-placeholder" role="img" aria-label="A cube\."[\s\S]*?<span class="book-compare__label">off<\/span>/),
		// Printed, both pictures stand side by side, the second one whole, and the slider's range is hidden.
		print: () => {
			assert.match(printRule(c_PrintCss, 'book-compare[data-enhanced] .book-compare__pair'), /grid-template-columns: 1fr 1fr/);
			assert.match(printRule(c_PrintCss, 'book-compare[data-enhanced] .book-compare__item:last-child'), /clip-path: none/);
			assert.match(printRule(c_PrintCss, '.book-compare__range'), /display: none !important/);
		},
	},
	checkpoint: {
		name: () => assert.match(s_Pages['make/spin'], /<div class="book-checkpoint" role="group" aria-label="Checkpoint 1">[\s\S]*?<p class="book-checkpoint__have">You should now have<\/p><figure class="book-figure" id="fig-now">/),
		print: () => assert.match(printRule(c_PrintCss, '.book-checkpoint'), /break-inside: avoid/),
	},
	glossary: {
		// Each term names its definition (dt and dd).
		name: () => assert.match(s_Pages['reference/glossary'], /<dl class="book-glossary"><dt id="fixed-step" data-pagefind-title="fixed step">fixed step<\/dt><dd>/),
		// Printed as on the screen: nothing of it is hidden, and Starlight prints its colors as the light theme's.
		print: () => {
			assert.equal(hiddenInPrint('book-glossary'), false);
			assert.match(c_StarlightPrintSource, /force light mode when printing/);
			assert.match(printRule(c_StarlightPrintCss, ':root'), /--sl-color-white: hsl\(224, 10%, 10%\)/);
		},
	},
	'track-chooser': {
		name: () => assert.match(s_Pages['start/how-to-read'], /<li class="book-track" data-track="game"><strong>Games<\/strong> \(G\)[\s\S]*?<a href="\/book\/start\/how-to-read\/" class="book-track__start">Start with: /),
		// Printed, the buttons that choose a track are hidden; the links to each track's first page stay.
		print: () => {
			assert.match(printRule(c_PrintCss, '.book-track__choose'), /display: none !important/);
			assert.equal(hiddenInPrint('book-track__start'), false);
		},
	},
	include: {
		// The included table's headings are headings of the page.
		name: () => assert.match(s_Pages['reference/performance'], /<div class="book-reference" data-pagefind-weight="0\.3"><h2>Budgets<\/h2><table>/),
		// The print view of the part holds the table with the chapter's own ids (src/lib/print.mjs).
		print: () => {
			const printed = prefixChapter('<div class="book-reference"><h2 id="budgets">Budgets</h2><table></table></div><a href="#budgets">x</a>', 'reference/performance', new Set(['reference/performance']), '/book');
			assert.match(printed, /<div class="book-reference"><h2 id="reference--performance--budgets">Budgets<\/h2><table><\/table><\/div><a href="#reference--performance--budgets">/);
		},
	},
	term: {
		name: () => assert.match(time, /<button type="button" class="book-term__button" popovertarget="book-term-fixed-step" data-pagefind-ignore=""><span aria-hidden="true">\?<\/span><span class="sr-only">Definition of fixed step<\/span><\/button>/),
		// Printed, the link stays and the button and its popover are hidden.
		print: () => assert.match(printRule(c_PrintCss, '.book-term__popover'), /display: none !important/),
	},
	since: {
		name: () => assert.match(time, /<h2>New things<\/h2>\n<p><span class="book-badge book-badge--new book-since" data-pagefind-ignore="">New in 0\.8\.0<\/span> Strata counts/),
		// Printed as on the screen, in the light theme's colors.
		print: () => {
			assert.equal(hiddenInPrint('book-since'), false);
			assert.equal(hiddenInPrint('book-badge'), false);
		},
	},
	value: {
		// The value is words of its sentence: a screen reader reads the number where the mark stood.
		name: () => assert.match(time, /<p>The editor has <span class="book-value">151<\/span> commands\.<\/p>/),
		// Printed as on the screen.
		print: () => assert.equal(hiddenInPrint('book-value'), false),
	},
};

test('every directive of the table has its accessible name and its print form here', () => {
	assert.deepEqual(Object.keys(c_Forms).sort(), Object.keys(c_Directives).sort());
});

for (const [name, form] of Object.entries(c_Forms)) {
	test(`${name}: its accessible name`, () => form.name());
	test(`${name}: its print form`, () => form.print());
}
