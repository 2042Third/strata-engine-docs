// Diagrams (plan/site.md "Diagrams"): the committed drawings of src/generated/diagrams/ and their stamps, the page's
// inlined SVGs with their accessible names, npm run diagrams (draw, --check), and the measures of budget row 18 that
// scripts/diagram-checks.mjs and `npm run diagrams -- --contrast` apply in a browser (labels inside their boxes,
// contrast, captions and names). No test starts a browser: the build never does.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { c_ContrastFixtures, c_RendererKey, compactDrawing, diagramFiles, diagramHash, diagramType, drawingFile, idPrefix, inlineDrawing, parseDrawing, readDrawings, renameDiagramIds, sourceProblems } from '../../lib/diagrams.mjs';
import { inputsDigest } from '../index.mjs';
import { readSettings } from '../../lib/settings.mjs';
import { loadPageIndex } from '../../lib/pages.mjs';
import { c_BottomStrip, committedDiagram, frontmatter, makeBook, rejectsWith, render } from './helpers.mjs';

const c_Source = 'flowchart LR\n    A --> B';
const fence = (source = c_Source, meta = 'caption="A leads to B." alt="Two boxes, A and B, with an arrow."') => `\`\`\`mermaid ${meta}\n${source}\n\`\`\``;
const page = (body) => `${frontmatter()}\n${body}\n${c_BottomStrip}`;

function write(root, files) {
	for (const [relative, content] of Object.entries(files)) {
		const file = path.join(root, ...relative.split('/'));
		mkdirSync(path.dirname(file), { recursive: true });
		writeFileSync(file, content);
	}
}

test('a diagram is named by its text and the renderer\'s key: line ends and the space around it do not count', () => {
	assert.match(diagramHash(c_Source), /^[0-9a-f]{16}$/);
	assert.equal(diagramHash(`\n  ${c_Source.replace(/\n/g, '\r\n')}  \n`), diagramHash(c_Source));
	assert.notEqual(diagramHash('flowchart LR\n    A --> C'), diagramHash(c_Source));
	assert.notEqual(diagramHash(c_Source, '0'.repeat(16)), diagramHash(c_Source));
	assert.match(c_RendererKey, /^[0-9a-f]{16}$/);
	const files = diagramFiles('/d', 'abc');
	assert.deepEqual(files, { light: path.join('/d', 'abc-light.svg'), dark: path.join('/d', 'abc-dark.svg') });
	assert.equal(idPrefix('0123456789abcdef', 'dark'), 'dg-0123456789abcdef-dark');
});

test('a drawing\'s file is its stamp line, then its SVG; an edit after drawing shows', () => {
	const text = drawingFile({ hash: '0123456789abcdef', theme: 'light', svg: '<svg></svg>' });
	assert.match(text, /^<!-- drawn by scripts\/diagrams\.mjs; renderer [0-9a-f]{16}; diagram 0123456789abcdef; theme light; sha256 [0-9a-f]{64}; do not edit -->\n<svg><\/svg>\n$/);
	const read = parseDrawing(text);
	assert.deepEqual([read.stamp.diagram, read.stamp.theme, read.svg, read.intact], ['0123456789abcdef', 'light', '<svg></svg>', true]);
	assert.equal(parseDrawing(text.replace('<svg></svg>', '<svg><g/></svg>')).intact, false);
	assert.match(parseDrawing('<svg></svg>\n').error, /not the stamp/);
});

test('readDrawings: both drawings, the themes missing, a stale or edited file', async () => {
	const book = makeBook({});
	try {
		const dir = path.join(book.root, 'src', 'generated', 'diagrams');
		const hash = diagramHash(c_Source);
		assert.deepEqual(await readDrawings(dir, c_Source), { hash, missing: ['light', 'dark'] });
		const { files } = committedDiagram(c_Source);
		write(book.root, { [`src/generated/diagrams/${hash}-light.svg`]: files[`src/generated/diagrams/${hash}-light.svg`] });
		assert.deepEqual((await readDrawings(dir, c_Source)).missing, ['dark']);
		write(book.root, files);
		const drawings = await readDrawings(dir, c_Source);
		assert.match(drawings.light, new RegExp(`^<svg id="dg-${hash}-light"`));
		assert.match(drawings.dark, /<text x="4" y="14">dark<\/text>/);
		const dark = path.join(dir, `${hash}-dark.svg`);
		writeFileSync(dark, files[`src/generated/diagrams/${hash}-dark.svg`].replace('>dark<', '>edited<'));
		assert.match((await readDrawings(dir, c_Source)).error, /was edited after it was drawn: draw it again with npm run diagrams/);
		writeFileSync(dark, drawingFile({ hash, theme: 'dark', svg: '<svg></svg>', rendererKey: 'f'.repeat(16) }));
		assert.match((await readDrawings(dir, c_Source)).error, /its stamp names another diagram, theme or renderer/);
		writeFileSync(dark, '<svg></svg>');
		assert.match((await readDrawings(dir, c_Source)).error, /its first line is not the stamp/);
	} finally {
		book.remove();
	}
});

test('the page inlines a drawing as an image named by the fence\'s alt text', () => {
	const svg = '<svg id="dg-0123456789abcdef-light" role="graphics-document document" aria-roledescription="flowchart-v2" aria-labelledby="x"><style>#dg-0123456789abcdef-light .a{}</style><g id="dg-0123456789abcdef-light-actor0"></g><use href="#dg-0123456789abcdef-light-actor0"/><rect class="a"/></svg>';
	const inlined = inlineDrawing(svg, { hash: '0123456789abcdef', theme: 'light', alt: 'Two "boxes" & one arrow.' });
	assert.match(inlined, /^<svg role="img" aria-label="Two &quot;boxes&quot; &amp; one arrow\." id="dg-0123456789abcdef-light"><title>Two &quot;boxes&quot; &amp; one arrow\.<\/title><style>/);
	assert.doesNotMatch(inlined, /aria-roledescription|graphics-document|aria-labelledby/);
	// The same diagram a second time on a page: every id and every reference to it is renamed alike.
	const second = inlineDrawing(svg, { hash: '0123456789abcdef', theme: 'light', alt: 'A.', occurrence: 2 });
	assert.match(second, /id="dg-0123456789abcdef-light-2"/);
	assert.match(second, /#dg-0123456789abcdef-light-2 \.a\{\}/);
	assert.match(second, /<g id="dg-0123456789abcdef-light-2-actor0"><\/g><use href="#dg-0123456789abcdef-light-2-actor0"\/>/);
	const ids = (text) => [...text.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
	assert.equal(ids(inlined).filter((id) => ids(second).includes(id)).length, 0);
});

test('paint that names an element the drawing lacks leaves its style sheet, paint that names one stays', () => {
	// Mermaid styles the "neo" look's shapes with a gradient only drawings in that look define: gate (a)'s lychee reads
	// url(#…) as a fragment of the page and fails on the missing one.
	const svg = '<svg id="dg-a-light"><style>#dg-a-light [data-look="neo"].node rect{stroke:url(#dg-a-light-gradient);filter:none;}'
		+ '#dg-a-light .edge{stroke:url(#dg-a-light-arrow) red;stroke-width:1px}#dg-a-light .icon{fill:url(#dg-a-light-gradient)}</style>'
		+ '<defs><marker id="dg-a-light-arrow"/></defs><rect fill="url(#dg-a-light-gradient)"/>'
		+ '<g class="node" data-look="neo"><rect/></g><path class="edge"/><circle class="icon"/></svg>';
	const inlined = inlineDrawing(svg, { hash: 'a', theme: 'light', alt: 'A.' });
	assert.match(inlined, /\[data-look="neo"\]\.node rect\{filter:none;\}/);
	assert.match(inlined, /\.edge\{stroke:url\(#dg-a-light-arrow\) red;stroke-width:1px\}/);
	assert.match(inlined, /\.icon\{\}/);
	assert.doesNotMatch(inlined.match(/<style>[\s\S]*<\/style>/)[0], /gradient/);
	// Outside the style sheet nothing is touched: an attribute is the drawing's own markup.
	assert.match(inlined, /<rect fill="url\(#dg-a-light-gradient\)"\/>/);
});

test('renameDiagramIds replaces the batch id everywhere and leaves longer numbers to the prefix of other ids', () => {
	const svg = '<svg id="b-1"><style>#b-1 .node{}</style><marker id="b-1_arrow"/><g id="b-12"/></svg>';
	assert.equal(renameDiagramIds(svg, 'b-1', 'dg-x'), '<svg id="dg-x"><style>#dg-x .node{}</style><marker id="dg-x_arrow"/><g id="dg-x-b-12"/></svg>');
});

test('every id of a drawn diagram starts with its own prefix, so the light and dark copies share none', () => {
	// Sequence diagrams write ids that do not derive from the diagram's id ("actor0", "root-0").
	const svg = '<svg id="b-0" aria-labelledby="chart-title-b-0 actor0"><style>#b-0 .actor{} #actor0 rect{fill:#fff} #root-0{}</style>'
		+ '<defs><marker id="arrowhead"/></defs><g id="root-0"><rect id="actor0"/><use href="#actor0"/><line marker-end="url(#arrowhead)"/></g>'
		+ '<text>#actor0 stays text</text></svg>';
	const light = renameDiagramIds(svg, 'b-0', 'dg-k-light');
	const dark = renameDiagramIds(svg, 'b-0', 'dg-k-dark');
	assert.equal(light, '<svg id="dg-k-light" aria-labelledby="chart-title-dg-k-light dg-k-light-actor0"><style>#dg-k-light .actor{} #dg-k-light-actor0 rect{fill:#fff} #dg-k-light-root-0{}</style>'
		+ '<defs><marker id="dg-k-light-arrowhead"/></defs><g id="dg-k-light-root-0"><rect id="dg-k-light-actor0"/><use href="#dg-k-light-actor0"/><line marker-end="url(#dg-k-light-arrowhead)"/></g>'
		+ '<text>#actor0 stays text</text></svg>');
	const ids = (text) => [...text.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
	assert.equal(ids(light).filter((id) => ids(dark).includes(id)).length, 0);
	for (const id of ids(light)) assert.ok(id.startsWith('dg-k-light'), id);
});

test('a diagram\'s accessible name is its fence\'s: accTitle and accDescr are refused', () => {
	assert.deepEqual(sourceProblems(c_Source), []);
	assert.match(sourceProblems('flowchart LR\n    accTitle: A title\n    A --> B')[0], /remove accTitle and accDescr/);
	assert.match(sourceProblems('sequenceDiagram\n  accDescr: words\n  A->>B: hi')[0], /remove accTitle and accDescr/);
	// A time chart's task marked crit; the book's own time chart and line chart are types the contrast fixture holds.
	assert.match(sourceProblems('gantt\n    dateFormat X\n    section A\n    One :done, crit, a1, 0, 10')[0], /marked crit/);
	assert.match(sourceProblems('gantt\n    section A\n    One :crit, a1, 0, 10')[0], /marked crit/);
	assert.deepEqual(sourceProblems('gantt\n    dateFormat X\n    section Critical path\n    Prepares frame 1 :p1, 0, 10\n    Done :done, d1, 10, 20'), []);
	assert.equal(diagramType('gantt\n    dateFormat X'), 'gantt');
	assert.equal(diagramType('xychart-beta\n    line [1, 2]'), 'xychart');
});

test('the type of a diagram, as the contrast fixture names it', () => {
	assert.equal(diagramType('flowchart LR\n  A --> B'), 'flowchart');
	assert.equal(diagramType('graph TD\n  A --> B'), 'flowchart');
	assert.equal(diagramType('%% a comment\n\nsequenceDiagram\n  A->>B: hi'), 'sequenceDiagram');
	assert.equal(diagramType('---\ntitle: A\n---\nstateDiagram-v2\n  [*] --> A'), 'stateDiagram');
	assert.equal(diagramType('classDiagram\n  class A'), 'classDiagram');
	assert.equal(diagramType('erDiagram\n  A ||--o{ B : has'), 'erDiagram');
	assert.equal(diagramType('pie title Pets\n  "Dogs" : 386'), null);
	assert.equal(diagramType('---\nnever closed'), null);
	for (const [type, source] of Object.entries(c_ContrastFixtures)) assert.equal(diagramType(source), type);
});

test('a diagram is drawn from its committed files in both themes, with its caption and accessible name, and search reads the first drawing only', async () => {
	const { files } = committedDiagram(c_Source);
	const book = makeBook({ pages: { 'core/time': page(fence()) }, files });
	try {
		const out = await render(book.root, 'core/time');
		const hash = diagramHash(c_Source);
		assert.match(out, new RegExp(`<figure class="book-diagram"><div class="book-diagram__svg book-diagram__svg--light"><svg role="img" aria-label="Two boxes, A and B, with an arrow\\." id="dg-${hash}-light" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 20"><title>Two boxes, A and B, with an arrow\\.</title>`));
		assert.match(out, new RegExp(`<div class="book-diagram__svg book-diagram__svg--dark" data-pagefind-ignore=""><svg role="img" aria-label="Two boxes, A and B, with an arrow\\." id="dg-${hash}-dark"`));
		assert.match(out, /<figcaption>A leads to B\.<\/figcaption><\/figure>/);
		assert.doesNotMatch(out, /drawn by scripts\/diagrams\.mjs|aria-roledescription/);
	} finally {
		book.remove();
	}
});

test('the same diagram twice on a page: the second copy\'s ids are its own', async () => {
	const book = makeBook({ pages: { 'core/time': page(`${fence()}\n\nText.\n\n${fence()}`) }, files: committedDiagram(c_Source).files });
	try {
		const out = await render(book.root, 'core/time');
		const ids = [...out.matchAll(/\sid="(dg-[^"]+)"/g)].map((match) => match[1]);
		assert.equal(ids.length, new Set(ids).size, ids.join(' '));
		assert.equal(ids.filter((id) => id.endsWith('-light-2')).length, 1);
	} finally {
		book.remove();
	}
});

test('the build reads only committed drawings: a missing or edited one fails, naming npm run diagrams', async () => {
	const book = makeBook({ pages: { 'core/time': page(fence()) } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /the diagram has no committed drawing \(src\/generated\/diagrams\/[0-9a-f]{16}-light\.svg and src\/generated\/diagrams\/[0-9a-f]{16}-dark\.svg are missing\): run npm run diagrams/);
		const { files, hash } = committedDiagram(c_Source);
		write(book.root, files);
		writeFileSync(path.join(book.root, 'src', 'generated', 'diagrams', `${hash}-light.svg`), files[`src/generated/diagrams/${hash}-light.svg`].replace('#333', '#334'));
		await rejectsWith(render(book.root, 'core/time'), /was edited after it was drawn/);
	} finally {
		book.remove();
	}
});

test('a diagram needs a caption and alt text, and no name of Mermaid\'s own', async () => {
	const titled = 'flowchart LR\n    accTitle: Steps\n    A --> B';
	const book = makeBook({ pages: { 'core/time': page(`${fence(c_Source, '')}\n\n${fence(titled)}`) }, files: { ...committedDiagram(c_Source).files, ...committedDiagram(titled).files } });
	try {
		await rejectsWith(render(book.root, 'core/time'), /needs caption=/, /needs alt=/, /remove accTitle and accDescr/);
	} finally {
		book.remove();
	}
});

test('a change of a committed drawing renders every page again (the inputs digest)', async () => {
	const { files, hash } = committedDiagram(c_Source);
	const book = makeBook({ pages: { 'core/time': page(fence()) }, files });
	try {
		const settings = readSettings({ root: book.root, env: {} });
		const index = await loadPageIndex(settings.docsDir, { revalidate: true });
		const before = inputsDigest(settings, index);
		const file = path.join(book.root, 'src', 'generated', 'diagrams', `${hash}-dark.svg`);
		writeFileSync(file, `${readFileSync(file, 'utf8')}\n`);
		assert.notEqual(inputsDigest(settings, index), before);
	} finally {
		book.remove();
	}
});

test('npm run diagrams --check: every fence has its two files, every file a fence, a caption, alt text and a known type', async () => {
	const { checkDiagrams, drawBook, loadBook, parseArguments } = await import('../../../scripts/diagrams.mjs');
	assert.deepEqual(parseArguments(['--check', '--root', 'x']).mode, 'check');
	assert.throws(() => parseArguments(['--check', '--contrast']), /two runs/);
	assert.throws(() => parseArguments(['--draw']), /unknown argument --draw/);
	const pie = 'pie title Pets\n    "Dogs" : 386';
	const book = makeBook({ pages: { 'core/time': page(`${fence()}\n\n${fence(pie, 'caption="Pets."')}`) }, files: committedDiagram(c_Source).files });
	try {
		const { settings, diagrams } = await loadBook(book.root);
		assert.equal(diagrams.length, 2);
		assert.match(diagrams[0].where, /^src\/content\/docs\/core\/time\.md:\d+$/);
		write(book.root, { 'src/generated/diagrams/ffffffffffffffff-light.svg': 'old', 'src/generated/diagrams/notes.txt': 'x' });
		const problems = await checkDiagrams(settings.diagramsDir, diagrams);
		assert.equal(problems.length, 5, problems.join('\n'));
		assert.match(problems.join('\n'), /the diagram has no alt="…"/);
		assert.match(problems.join('\n'), /the diagram's type is not one the contrast fixture holds/);
		assert.match(problems.join('\n'), /no committed drawing \([0-9a-f]{16}-light\.svg, [0-9a-f]{16}-dark\.svg\): run npm run diagrams/);
		assert.match(problems.join('\n'), /ffffffffffffffff-light\.svg: no fence of the book draws it/);
		assert.match(problems.join('\n'), /notes\.txt: not a drawing of npm run diagrams/);
		// Drawing leaves what is committed and removes what no fence draws; with nothing missing it starts no browser.
		const clean = diagrams.slice(0, 1);
		const { drawn, removed, failures } = await drawBook(settings.diagramsDir, clean);
		assert.deepEqual([drawn, removed, failures], [[], ['ffffffffffffffff-light.svg'], []]);
		assert.deepEqual((await checkDiagrams(settings.diagramsDir, clean)).filter((line) => !line.includes('notes.txt')), []);
	} finally {
		book.remove();
	}
});

test('npm run diagrams lists the part pages\' generated Needs graphs with their caption and alt text', async () => {
	const { loadBook } = await import('../../../scripts/diagrams.mjs');
	const partPage = (generated) => `---\nid: core/${generated}\ntitle: "${generated === 'index' ? 'Engine architecture' : 'Review: engine architecture'}"\ndescription: "The part's ${generated} page."\ntracks: [E]\nstatus: draft\ngenerated: ${generated}\n---\n\nText.\n`;
	const book = makeBook({
		pages: { 'core/index': partPage('index'), 'core/review': partPage('review'), 'core/time': page('Text.') },
		outline: (data) => {
			data.parts.find((part) => part.slug === 'core').partPages = true;
		},
	});
	try {
		const { diagrams } = await loadBook(book.root);
		assert.equal(diagrams.length, 1);
		assert.match(diagrams[0].source, /^flowchart/);
		assert.match(diagrams[0].meta, /^caption="[^"]+" alt="[^"]+"$/);
		assert.match(diagrams[0].where, /^src\/content\/docs\/core\/index\.md:/);
	} finally {
		book.remove();
	}
});

test('the contrast check measures on each theme\'s page background', async () => {
	const { c_Backgrounds, fixturePage } = await import('../../../scripts/diagrams.mjs');
	assert.match(fixturePage('<svg></svg>', 'light', 'file:///font.woff2'), /background: #ffffff;[\s\S]*<svg><\/svg>/);
	assert.match(fixturePage('<svg></svg>', 'dark', 'file:///font.woff2'), new RegExp(`background: ${c_Backgrounds.dark.replace(/[()]/g, '\\$&')};`));
	assert.match(fixturePage('<svg></svg>', 'dark', 'file:///font.woff2'), /src: url\('file:\/\/\/font\.woff2'\)/);
});

test('compactDrawing drops the rules, keyframes, markers and data attributes a drawing never paints with', () => {
	const css = [
		'#dg{font-size:16px;}',
		'#dg .node rect{fill:#eee;}',
		'#dg .error-icon{fill:#a44141;}',
		'#dg .cluster-label text,#dg .node text{fill:#333;}',
		'#dg .edge:not(.thick){stroke-width:1px;}',
		'#dg [data-look="neo"].node rect{fill:url(#gradient);}',
		'#dg .moving{animation:dash 5s linear infinite;}',
		'@keyframes dash{to{stroke-dashoffset:0;}}',
		'@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}',
	].join('');
	const svg = `<svg id="dg"><style>${css}</style><marker id="dg-pointEnd"><path d="M0,0"></path></marker><marker id="dg-cross"><path d="M1,1"></path></marker>`
		+ `<g class="node" data-look="classic" data-id="A"><rect></rect><text>A</text></g>`
		+ `<path class="edge" style=";" data-points="W3siIn0=" marker-end="url(#dg-pointEnd)"></path></svg>`;
	const compact = compactDrawing(svg);
	assert.match(compact, /#dg\{font-size:16px;\}#dg \.node rect\{fill:#eee;\}/);
	assert.doesNotMatch(compact, /error-icon/);
	// A list stays when one selector can match; a functional pseudo-class keeps its selector.
	assert.match(compact, /#dg \.cluster-label text,#dg \.node text\{fill:#333;\}/);
	assert.match(compact, /#dg \.edge:not\(\.thick\)\{stroke-width:1px;\}/);
	// The data attribute a selector reads stays; the others go, and so does the empty style.
	assert.match(compact, /data-look="classic"/);
	assert.doesNotMatch(compact, /data-id=|data-points=|style=";"/);
	assert.match(compact, /<marker id="dg-pointEnd">/);
	assert.doesNotMatch(compact, /dg-cross/);
	// No element is "moving": its rule goes, and with it the keyframes only that rule named.
	assert.doesNotMatch(compact, /moving|@keyframes dash|edge-animation-frame/);
	const moving = compactDrawing(svg.replace('class="edge"', 'class="edge moving"'));
	assert.match(moving, /@keyframes dash\{to\{stroke-dashoffset:0;\}\}/);
	assert.doesNotMatch(moving, /edge-animation-frame/);
});
