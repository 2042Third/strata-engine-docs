// excerpts: Strata's code is quoted, never retyped. A fence with src="<engine path>#L<a>-L<b>" holds those lines of
// the engine at the pinned commit (tools/excerpts.py fills and checks them). The build gives it a header with the path,
// the lines and a link to them on GitHub at the pin, shows the engine's own line numbers, and turns mark="L<n>" into
// Expressive Code's line marks. Other sources have a namespace (plan/pipelines.md §3.2): "book:<path>" is a file of
// this repository (named as text: the repository is not public), "book:<path>.patch#hunk-<n>" a hunk of a tutorial's
// patch (its header names the engine file the hunk changes, at the pin), "vendor:<lib>/<path>" a file of a library the
// engine vendors (its header names the library's version and license from src/generated/vendor.json and links the
// file at the submodule's commit). The anchors that tools/excerpts.py keeps on a quote (symbol, from, to, overload,
// command) are its own.
// Fences of the book's own code are labelled: sketch="<file>" (a copy of sketches/<file>, compared here),
// output-of="<file>" (what the sketch prints) and pseudocode. A text figure, capture="<figure>" with variant="<name>"
// when its recipe has variants, shows the published text of a recipe of kind text (a command's result or a program's
// output, which tools/figures.py takes and fill copies into the fence; pipelines.md §5). Every other attribute of a
// fence is Expressive Code's; a name neither knows fails the build, so that a mistyped attribute is not ignored.

import { readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { captureAnchor, entryProblems, loadManifest, variantNames } from '../lib/figures.mjs';
import { engineUrl, withBase } from '../lib/settings.mjs';
import { loadVendor } from '../lib/vendor.mjs';
import { element, pageOf, parseMeta, report, text } from './shared.mjs';

export const c_MaxQuoteLines = 60;
export const c_MinInternalsQuotes = 3;
// The anchors tools/excerpts.py writes and keeps on a quote (pipelines.md §3.1 and §3.3).
export const c_QuoteAnchors = ['symbol', 'from', 'to', 'overload', 'command'];
const c_Own = ['src', 'mark', 'sketch', 'output-of', 'pseudocode', 'capture', 'variant', ...c_QuoteAnchors];
// Expressive Code's own props (its core, text markers, frames, line numbers, collapsible sections): with a value, and
// on their own.
export const c_CodeProps = ['title', 'frame', 'wrap', 'preserveIndent', 'hangingIndent', 'showLineNumbers', 'startLineNumber', 'collapse', 'collapseStyle', 'collapsePreserveIndent', 'lang', 'useDiffSyntax', 'ins', 'del', 'add', 'rem'];
export const c_CodeFlags = ['wrap', 'preserveIndent', 'showLineNumbers', 'useDiffSyntax', 'collapsePreserveIndent'];

/** Why a fence's other tokens are not Expressive Code's, or null. */
export function codePropsProblem(rest) {
	for (const token of rest) {
		// Line ranges ({3-5}), text and regular expression markers ("text", /re/).
		if (/^\{.*\}$/.test(token) || /^(["']).*\1$/.test(token) || /^\/.+\/$/.test(token)) continue;
		const name = /^([A-Za-z_][\w-]*)=/.exec(token)?.[1];
		if (name ? c_CodeProps.includes(name) : c_CodeFlags.includes(token)) continue;
		return `a code fence has no attribute "${name ?? token}": the book's are src, mark, sketch, output-of, pseudocode, capture and variant (with a quote's ${c_QuoteAnchors.join(', ')}), Expressive Code's are ${c_CodeProps.join(', ')} and {line ranges}`;
	}
	return null;
}

/**
 * Splits src="path#L10-L20" into `{ namespace, path, start, end }`, `{ namespace, path, symbol }` or, for a src without
 * lines beside command="<name>", `{ namespace, path, command }` (the draft forms that fill turns into lines,
 * pipelines.md §3.3), `{ namespace: 'book', path, hunk }` for a hunk of a patch, or `{ error }`. The namespace is
 * 'engine', 'book' or 'vendor' (with `lib`). `attributes` are the fence's other attributes (a Map).
 */
export function parseSource(value, attributes = new Map()) {
	const hash = value.indexOf('#');
	let file = hash < 0 ? value : value.slice(0, hash);
	const fragment = hash < 0 ? null : value.slice(hash + 1);
	let namespace = 'engine';
	let lib = null;
	if (file.startsWith('book:')) {
		namespace = 'book';
		file = file.slice('book:'.length);
	} else if (file.startsWith('vendor:')) {
		namespace = 'vendor';
		file = file.slice('vendor:'.length);
		lib = file.split('/')[0];
		if (!lib || !/^[A-Za-z0-9._-]+$/.test(lib) || file.split('/').length < 2) return { error: `src="${value}": a vendor source is vendor:<library>/<path in the library>, such as vendor:glm/glm/glm.hpp` };
	} else if (/^[a-z]+:/.test(file)) {
		return { error: `src="${value}": the sources are engine paths, book:<path> and vendor:<library>/<path> (pipelines.md §3.2)` };
	}
	if (!file || file.startsWith('/') || file.includes('\\') || file.split('/').includes('..')) return { error: `src="${value}": the path is relative to the ${namespace === 'engine' ? "engine's root" : namespace === 'book' ? "book's repository" : 'library'}, with "/" separators` };
	const hunk = /^hunk-([1-9][0-9]*)$/.exec(fragment);
	if (hunk) {
		if (namespace !== 'book' || !file.endsWith('.patch')) return { error: `src="${value}": #hunk-<n> names a hunk of a tutorial's patch, src="book:<path>.patch#hunk-<n>"` };
		return { namespace, path: file, hunk: Number(hunk[1]) };
	}
	const base = { namespace, path: file, ...(lib ? { lib } : {}) };
	if (fragment === null) {
		const command = attributes.get('command');
		if (typeof command === 'string' && command.trim()) return { ...base, command };
		return { error: `src="${value}" names no lines: write src="${value}#L<first>-L<last>", a symbol (src="${value}#<Class::Function>") or an editor command (command="<group.action>"), which tools/excerpts.py fill turns into lines` };
	}
	const lines = /^L(\d+)(?:-L(\d+))?$/.exec(fragment);
	if (lines) {
		const start = Number(lines[1]);
		const end = Number(lines[2] ?? lines[1]);
		if (start < 1 || end < start) return { error: `src="${value}": the range must run forwards from line 1 or later` };
		return { ...base, start, end };
	}
	// The symbol's form is tools/excerpts.py's (c_Symbol): a destructor such as ~Scene starts with "~".
	if (/^[A-Za-z_~][\w:~<>,]*$/.test(fragment)) return { ...base, symbol: fragment };
	return { error: `src="${value}": "#${fragment}" is neither lines (#L10-L20) nor a symbol (#Scene::OnUpdate)` };
}

/** Turns mark="L2251,L2253-L2255" into Expressive Code's marks counted from the quote's first line ("13,15-17"). */
export function relativeMarks(value, start, end) {
	const ranges = [];
	for (const part of value.split(',').map((item) => item.trim()).filter(Boolean)) {
		const match = /^L(\d+)(?:-L(\d+))?$/.exec(part);
		if (!match) return { error: `mark="${value}": write the engine's line numbers, such as L2251 or L2251-L2253` };
		const first = Number(match[1]);
		const last = Number(match[2] ?? match[1]);
		if (first < start || last > end || last < first) return { error: `mark="${value}": ${part} is not inside the quoted lines L${start}-L${end}` };
		ranges.push(first === last ? `${first - start + 1}` : `${first - start + 1}-${last - start + 1}`);
	}
	return { marks: ranges.join(',') };
}

function rangeText(start, end) {
	return start === end ? `line ${start}` : `lines ${start}–${end}`;
}

/** A link to lines of the engine at the pin. */
function engineLink(context, file, start, end) {
	return { type: 'link', url: engineUrl(context.settings.engine, file, start, end), children: [{ type: 'inlineCode', value: file }] };
}

/**
 * The download under <base>/downloads/ that a reader gets of a file of this repository, or null (plan/pipelines.md §3.2,
 * §5.7 and §6.3; plan/critique/rulings-6.md, R25: a quote of `book:<path>` links its download when the site publishes
 * one, never the repository). The tools publish into public/downloads/: a tutorial's patch
 * tutorials/<part>/<chapter>.patch as tutorials/<part>/<chapter>.patch; an exercise's solution
 * tutorials/<part>/<chapter>/exercise-<n>.patch as solutions/<part>/<chapter>/exercise-<n>.patch and
 * exercise-<n>.tutorial.json as solutions/<part>/<chapter>/exercise-<n>.zip; a lab, labs/<name>.json and the files of
 * labs/<name>/, as labs/<name>.zip.
 */
export function bookDownloadPath(file) {
	const segment = '[a-z0-9]+(?:-[a-z0-9]+)*';
	const patch = new RegExp(`^tutorials/(${segment})/(${segment})\\.patch$`).exec(file);
	if (patch) return `downloads/tutorials/${patch[1]}/${patch[2]}.patch`;
	const exercise = new RegExp(`^tutorials/(${segment})/(${segment})/(exercise-[1-9][0-9]*)\\.(patch|tutorial\\.json)$`).exec(file);
	if (exercise) return `downloads/solutions/${exercise[1]}/${exercise[2]}/${exercise[3]}.${exercise[4] === 'patch' ? 'patch' : 'zip'}`;
	const lab = new RegExp(`^labs/(${segment})(?:\\.json|/.+)$`).exec(file);
	if (lab) return `downloads/labs/${lab[1]}.zip`;
	return null;
}

/** The download of a file of this repository, `{ url }`, when public/ holds it; else null. */
export function bookDownload(settings, file) {
	const relative = bookDownloadPath(file);
	if (!relative) return null;
	try {
		if (!statSync(path.join(settings.root, 'public', ...relative.split('/'))).isFile()) return null;
	} catch (error) {
		if (error.code === 'ENOENT') return null;
		throw error;
	}
	return { url: withBase(settings.base, `/${relative}`) };
}

/** The name of a file of this repository in a header: its path, linking its download when there is one. */
function bookFileName(context, file) {
	const name = { type: 'inlineCode', value: file };
	const download = bookDownload(context.settings, file);
	// A URL of the site the build made itself: an element, which the links plugin (it checks the writer's links) leaves.
	return download ? element('a', { href: download.url }, [name]) : name;
}

/**
 * The header of a quote of a vendored library (pipelines.md §3.2; rulings-6 R22): the path, the lines, and the
 * library's name, version and license as the engine's notices record them at the pin, linking the file at the commit
 * of the library's submodule. The record is src/generated/vendor.json, which the tool chain writes; until it exists a
 * draft names the path and the lines only, and a release refuses the quote.
 */
function vendorHeader(context, file, node, source) {
	const { settings } = context;
	const commit = settings.engine.commit;
	const range = rangeText(source.start, source.end);
	const name = { type: 'inlineCode', value: `Strata/vendor/${source.path}` };
	const plain = () => element('p', { className: ['book-excerpt__source'] }, [name, text(`, ${range} (the library ${source.lib} as the engine ${commit.slice(0, 8)} vendors it)`)]);
	const vendor = loadVendor(settings.vendorFile);
	if (vendor.missing) {
		if (settings.release) report(file, node, `src="vendor:${source.path}…": a release names the version and license of every vendored library it quotes, and src/generated/vendor.json, which the tool chain writes, does not exist`);
		return plain();
	}
	if (vendor.error) {
		report(file, node, vendor.error);
		return plain();
	}
	if (vendor.pin !== commit) {
		report(file, node, `src/generated/vendor.json was written for engine ${vendor.pin.slice(0, 8)}, not for the pin ${commit.slice(0, 8)}: write it again at the pin`);
		return plain();
	}
	const library = vendor.libraries.get(source.lib);
	if (!library) {
		report(file, node, `src="vendor:${source.path}…": the engine's notices at the pin list no library "${source.lib}" (src/generated/vendor.json knows ${[...vendor.libraries.keys()].join(', ') || 'none'})`);
		return plain();
	}
	const inLibrary = source.path.slice(source.lib.length + 1);
	const lines = source.start === source.end ? `#L${source.start}` : `#L${source.start}-L${source.end}`;
	const link = { type: 'link', url: `${library.repository}/blob/${library.commit}/${inLibrary}${lines}`, children: [name] };
	return element('p', { className: ['book-excerpt__source'] }, [link, text(`, ${range} (${library.name} ${library.version}, ${library.license}, as the engine ${commit.slice(0, 8)} vendors it)`)]);
}

function sourceHeader(context, source) {
	const { commit } = context.settings.engine;
	const range = rangeText(source.start, source.end);
	if (source.namespace === 'book') {
		// The book's repository is not public: its files are named as text, or link their download.
		return element('p', { className: ['book-excerpt__source'] }, [bookFileName(context, source.path), text(`, ${range} (this book's own file)`)]);
	}
	return element('p', { className: ['book-excerpt__source'] }, [engineLink(context, source.path, source.start, source.end), text(`, ${range} (engine ${commit.slice(0, 8)})`)]);
}

/**
 * The n-th hunk of a unified diff (`git diff` format): `{ file, start, count, lines }`, where `file` is the engine path it
 * changes, `start` and `count` its lines at the pin (the "-" side of "@@ -a,b +c,d @@") and `lines` its body, or
 * `{ error }`.
 */
export function patchHunk(patchText, number) {
	const lines = patchText.replace(/\r\n?/g, '\n').split('\n');
	let file = null;
	let found = 0;
	for (let index = 0; index < lines.length; index++) {
		const line = lines[index];
		const old = /^--- (?:a\/(.+)|\/dev\/null)$/.exec(line);
		if (old) {
			file = old[1] ?? null;
			const next = /^\+\+\+ (?:b\/(.+)|\/dev\/null)$/.exec(lines[index + 1] ?? '');
			if (!file && next) file = next[1] ?? null;
			continue;
		}
		const header = /^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@/.exec(line);
		if (!header) continue;
		found++;
		if (found !== number) continue;
		const body = [];
		for (let inner = index + 1; inner < lines.length && /^[ +\-\\]/.test(lines[inner]) && !/^--- /.test(lines[inner]); inner++) body.push(lines[inner]);
		if (!file) return { error: `hunk ${number} names no file it changes` };
		return { file, start: Number(header[1]), count: header[2] === undefined ? 1 : Number(header[2]), lines: body };
	}
	return { error: `the patch has ${found} hunk${found === 1 ? '' : 's'}, not ${number}` };
}

// A sketch's header names its file as text, never as a link: the book's repository is not public, so the site links
// nowhere in it, and the fence below already holds the whole file.
function bookCodeHeader(label, file) {
	const children = [element('span', { className: ['book-code__label'] }, [text(label)])];
	if (file) {
		children.push(text(' · '));
		children.push({ type: 'inlineCode', value: `sketches/${file}` });
	}
	return element('p', { className: ['book-excerpt__source', 'book-code__header'] }, children);
}

/** Text with LF line ends only. */
export function normalizeLineEnds(value) {
	return value.replace(/\r\n?/g, '\n');
}

/**
 * Why a sketch's file name is not one of the page's (pipelines.md §4: sketches/<part>-<chapter>-<name>.<ext>, so that
 * two pages never share a file), or null. `written` is the attribute's value as the page writes it (an answer's
 * solution="sketches/<name>").
 */
export function sketchNameProblem(name, pageId, attribute = 'sketch', written = name) {
	if (!/^[A-Za-z0-9_-]+\.[A-Za-z0-9]+(\.[A-Za-z0-9]+)?$/.test(name)) return `${attribute}="${written}" must name a file of sketches/ with its extension, such as ${pageId.replace(/\//g, '-')}-toy.cpp`;
	const prefix = `${pageId.replace(/\//g, '-')}-`;
	if (!name.startsWith(prefix)) return `${attribute}="${written}": a sketch's file name starts with its page's id, ${prefix}<name>.<extension> (pipelines.md §4)`;
	return null;
}

/**
 * The fence of the book's own code that the excerpts plugin drew at a node: `{ kind: 'sketch' | 'output' |
 * 'pseudocode' | 'capture', file }` (`file` is null for pseudocode and text figures), or null. An answer whose worked
 * solution is a sketch looks for the sketch and its output inside it (src/plugins/answers.mjs).
 */
export function bookCodeOf(node) {
	return node?.data?.bookCode ?? null;
}

function bookCode(kind, file, children) {
	const wrapper = element('div', { className: ['book-excerpt', 'book-code', `book-code--${kind}`] }, children);
	wrapper.data.bookCode = { kind, file };
	return wrapper;
}

function readSketch(context, name) {
	try {
		return { text: normalizeLineEnds(readFileSync(path.join(context.settings.sketchesDir, name), 'utf8')).replace(/\n+$/, '') };
	} catch (error) {
		if (error.code === 'ENOENT') return { error: `sketch="${name}": sketches/${name} does not exist` };
		throw error;
	}
}

/** What a text figure's recipe runs, for its header: the editor command whose result it keeps, or the program. */
function captureSource(entry, variant) {
	const fields = { ...entry, ...(variant ? entry.variants?.[variant] : null) };
	const command = fields.text?.command?.command;
	if (typeof command === 'string' && command) return [text(' · the result of the editor command '), { type: 'inlineCode', value: command }];
	const program = fields.text?.program;
	if (typeof program === 'string' && program) return [text(' · the output of '), { type: 'inlineCode', value: program }];
	return [];
}

/**
 * A text figure (pipelines.md §5; the recipe and the published names of .tools/handover/figures-format.md §1, §3 and
 * §5): `{ node }`, a figure that holds the fence, with a header that says the engine printed it, and the recipe's
 * caption (style.md §11: every figure has one), or null after a problem. Its id is `anchor`, given as a picture's is.
 * The fence names a recipe of kind text of the page's manifest, and one of its variants when it has them. Its body
 * must equal the published src/assets/figures/<page>/<figure>[-<variant>].txt, which tools/figures.py fill copies into
 * it; until the text is taken, a draft labels the fence and a release fails.
 */
function captureFence(context, file, node, attributes, owner, anchor) {
	const id = attributes.get('capture');
	const variant = attributes.get('variant') ?? null;
	const written = `capture="${id}"`;
	if (node.lang !== 'text') report(file, node, `a text figure is a text fence: \`\`\`text ${written}`);
	let manifest;
	try {
		manifest = loadManifest(context.settings.figuresDir, owner);
	} catch (error) {
		report(file, node, error.message);
		return null;
	}
	const entry = manifest?.figures.get(id);
	if (!entry || entry.kind !== 'text') {
		const found = entry ? `; "${id}" is a figure of kind ${entry.kind ?? 'none'}, which ::figure{id=${id}} places` : '';
		report(file, node, `${written}: src/content/figures/${owner}.json has no text figure of that id${found}: add its recipe (kind text), or correct capture`);
		return null;
	}
	for (const problem of entryProblems(entry)) report(file, node, problem);
	const variants = variantNames(entry);
	if (variants.length && !variant) {
		report(file, node, `the text figure "${id}" has the variants ${variants.join(', ')}: name one with variant="…"`);
		return null;
	}
	if (variant && !variants.includes(variant)) {
		report(file, node, variants.length ? `the text figure "${id}" has no variant "${variant}" (it has ${variants.join(', ')})` : `the text figure "${id}" has no variants: remove variant="${variant}"`);
		return null;
	}
	const stem = [id, variant].filter(Boolean).join('-');
	const relative = `src/assets/figures/${owner}/${stem}.txt`;
	let published = null;
	try {
		published = normalizeLineEnds(readFileSync(path.join(context.settings.picturesDir, ...owner.split('/'), `${stem}.txt`), 'utf8')).replace(/\n+$/, '');
	} catch (error) {
		if (error.code !== 'ENOENT') throw error;
	}
	if (published === null) {
		if (context.settings.release) report(file, node, `the text figure ${stem} is not taken yet (${relative}): a release shows only text the engine printed; take it with python -I tools/figures.py take --kinds text, then publish and fill it`);
	} else if (published !== node.value.replace(/\n+$/, '')) {
		report(file, node, `the fence differs from ${relative}: run python -I tools/figures.py fill`);
	}
	const header = element('p', { className: ['book-excerpt__source', 'book-code__header'] }, [
		element('span', { className: ['book-code__label'] }, [text('Captured from the engine')]),
		...captureSource(entry, variant),
		...(published === null ? [text(' (draft: not captured yet)')] : []),
	]);
	const code = bookCode('capture', null, [header, node]);
	return { node: element('figure', { className: ['book-figure', 'book-figure--text'], id: anchor }, [code, element('figcaption', {}, [text(entry.caption ?? '')])]) };
}

export function remarkBookExcerpts(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			let quotes = 0;
			const sketches = new Set();
			// Text figures get their ids in document order, as the page index gives them (src/lib/pages.mjs).
			const captures = new Set();
			const replace = (parent) => {
				for (let i = 0; i < (parent.children?.length ?? 0); i++) {
					const node = parent.children[i];
					if (node.type !== 'code') {
						replace(node);
						continue;
					}
					// A page saved with CRLF line ends (Git for Windows checks files out so unless .gitattributes says
					// otherwise) keeps the "\r" in a fence's text; the files it is compared with have none.
					node.value = normalizeLineEnds(node.value);
					// A question copied onto a part's review page keeps the page it was written on (src/lib/partpages.mjs).
					const owner = node.data?.bookPageId ?? page.id;
					const { attributes, flags, rest } = parseMeta(node.meta, c_Own);
					const props = codePropsProblem(rest);
					if (props) report(file, node, props);
					if (!attributes.has('src')) {
						const anchors = c_QuoteAnchors.filter((name) => attributes.has(name));
						if (anchors.length) report(file, node, `${anchors.join(', ')} belong${anchors.length === 1 ? 's' : ''} to a quote of the engine, with src="…" (pipelines.md §3)`);
						if (attributes.has('mark')) report(file, node, attributes.has('sketch') ? 'mark="L…" counts the engine\'s lines and belongs to a quote with src="…"; mark lines of a sketch with Expressive Code\'s {3-5}' : 'mark="L…" counts the engine\'s lines and belongs to a quote with src="…"; use Expressive Code\'s {3-5} elsewhere');
					}
					const kinds = ['src', 'sketch', 'output-of', 'capture'].filter((name) => attributes.has(name)).concat(flags.has('pseudocode') ? ['pseudocode'] : []);
					if (kinds.length > 1) report(file, node, `a fence is one of a quote (src), a sketch, a sketch's output, a text figure (capture) or pseudocode, not ${kinds.join(' and ')}`);
					if (attributes.has('variant') && !attributes.has('capture')) report(file, node, `variant="${attributes.get('variant')}" chooses a variant of a text figure: it goes with capture="<figure>"`);
					if (attributes.has('src')) {
						const wrapped = quote(context, file, node, attributes, rest);
						if (wrapped) {
							parent.children[i] = wrapped.node;
							if (wrapped.engine) quotes++;
						}
					} else if (attributes.has('sketch')) {
						const name = attributes.get('sketch');
						const problem = sketchNameProblem(name, owner);
						if (problem) report(file, node, problem);
						else {
							const sketch = readSketch(context, name);
							if (sketch.error) report(file, node, sketch.error);
							else if (sketch.text !== node.value.replace(/\n+$/, '')) report(file, node, `the fence differs from sketches/${name}: run python tools/sketches.py fill`);
						}
						sketches.add(name);
						node.meta = rest.join(' ');
						parent.children[i] = bookCode('sketch', name, [bookCodeHeader('Sketch', name), node]);
					} else if (attributes.has('output-of')) {
						const name = attributes.get('output-of');
						const problem = sketchNameProblem(name, owner, 'output-of');
						if (problem) report(file, node, problem);
						else if (!sketches.has(name)) report(file, node, `output-of="${name}" shows what a sketch prints: the page shows that sketch first, in a fence with sketch="${name}"`);
						if (node.lang !== 'text') report(file, node, `the output of a sketch is a text fence: \`\`\`text output-of="${name}"`);
						node.meta = rest.join(' ');
						parent.children[i] = bookCode('output', name, [bookCodeHeader('Output of the sketch', name), node]);
					} else if (attributes.has('capture')) {
						node.meta = rest.join(' ');
						const anchor = captureAnchor(captures, { id: attributes.get('capture'), variant: attributes.get('variant') ?? null });
						const captured = captureFence(context, file, node, attributes, owner, anchor);
						if (captured) parent.children[i] = captured.node;
					} else if (flags.has('pseudocode')) {
						node.meta = rest.join(' ');
						parent.children[i] = bookCode('pseudocode', null, [bookCodeHeader('Pseudocode', null), node]);
					} else {
						node.meta = rest.join(' ');
					}
				}
			};
			replace(tree);
			if (page.kind === 'internals' && quotes < c_MinInternalsQuotes) {
				report(file, tree, `a page of kind internals quotes the engine at least ${c_MinInternalsQuotes} times; this one quotes it ${quotes} times`);
			}
		};
	};
}

/** A quote of a patch's hunk: `{ node }` with the header naming the engine file it changes, or null. */
function hunkQuote(context, file, node, source, rest) {
	if (node.lang !== 'diff') report(file, node, `a hunk of a patch is a diff fence: \`\`\`diff src="book:${source.path}#hunk-${source.hunk}"`);
	let patch;
	try {
		patch = readFileSync(path.join(context.settings.root, ...source.path.split('/')), 'utf8');
	} catch (error) {
		if (error.code !== 'ENOENT') throw error;
		report(file, node, `src="book:${source.path}#hunk-${source.hunk}": the patch ${source.path} does not exist`);
		return null;
	}
	const hunk = patchHunk(patch, source.hunk);
	if (hunk.error) {
		report(file, node, `src="book:${source.path}#hunk-${source.hunk}": ${hunk.error}`);
		return null;
	}
	const lineCount = node.value === '' ? 0 : node.value.split('\n').length;
	if (lineCount !== hunk.lines.length) report(file, node, `the fence holds ${lineCount} lines but hunk ${source.hunk} of ${source.path} has ${hunk.lines.length}: run python tools/excerpts.py fill`);
	node.meta = rest.join(' ');
	const { commit } = context.settings.engine;
	const end = Math.max(hunk.start, hunk.start + hunk.count - 1);
	const header = element('p', { className: ['book-excerpt__source'] }, [
		engineLink(context, hunk.file, hunk.start, end),
		text(`, ${hunk.count === 0 ? `after line ${hunk.start}` : rangeText(hunk.start, end)} at engine ${commit.slice(0, 8)}, changed by hunk ${source.hunk} of `),
		bookFileName(context, source.path),
	]);
	return { node: element('div', { className: ['book-excerpt', 'book-excerpt--patch'], dataSource: `book:${source.path}#hunk-${source.hunk}` }, [header, node]), engine: false };
}

/** A quote: `{ node, engine }` (engine: a quote of the engine itself, which P4 counts), or null after a problem. */
function quote(context, file, node, attributes, rest) {
	const source = parseSource(attributes.get('src'), attributes);
	if (source.error) {
		report(file, node, source.error);
		return null;
	}
	if (rest.some((token) => token.startsWith('title='))) report(file, node, 'a quote is titled by its source: remove title="…"');
	// Expressive Code's own line markers count the block's lines, not the engine's: on a quote they would mark other
	// lines than the writer meant (and move when the quote's range changes).
	const markers = rest.filter((token) => /^\{.*\}$/.test(token) || /^(ins|del)=/.test(token));
	if (markers.length) report(file, node, `a quote marks lines with mark="L<n>" in the engine's line numbers; ${markers.join(' ')} counts the block's lines: remove it`);
	if (source.hunk) {
		if (attributes.has('mark')) report(file, node, 'a hunk of a patch shows its changes with "+" and "-": it takes no mark="L…"');
		return hunkQuote(context, file, node, source, rest.filter((token) => !markers.includes(token)));
	}
	const engine = source.namespace === 'engine';
	if (source.symbol && attributes.has('command')) report(file, node, `src="${attributes.get('src')}" names its lines by a symbol, and command="${attributes.get('command')}" by an editor command: keep one of them (pipelines.md §3.3)`);
	if (source.symbol || source.command) {
		const named = source.symbol ? 'a symbol' : 'an editor command';
		if (context.settings.release) report(file, node, `src="${attributes.get('src')}" names ${named}: run python tools/excerpts.py fill before a release`);
		node.meta = rest.join(' ');
		const draft = source.symbol ? `${attributes.get('src').split('#')[0]}#${source.symbol}` : `${attributes.get('src')} command="${source.command}"`;
		return {
			node: element('div', { className: ['book-excerpt', 'book-excerpt--unfilled'] }, [
				element('p', { className: ['book-excerpt__source'] }, [{ type: 'inlineCode', value: draft }, text(' (draft: not filled from the engine yet)')]),
				node,
			]),
			engine,
		};
	}
	const lineCount = node.value === '' ? 0 : node.value.split('\n').length;
	const expected = source.end - source.start + 1;
	if (expected > c_MaxQuoteLines) report(file, node, `a quote holds at most ${c_MaxQuoteLines} lines; L${source.start}-L${source.end} is ${expected}: split it and walk through the parts`);
	if (lineCount !== expected) report(file, node, `the fence holds ${lineCount} lines but src names ${expected} (L${source.start}-L${source.end}): run python tools/excerpts.py fill`);
	else if (lineCount > 0) {
		// Expressive Code draws no blank line at the start or the end of a block. A blank first line would make every
		// line number (and every mark) one line late; a blank last line would show fewer lines than src names.
		const lines = node.value.split('\n');
		const first = lines.findIndex((line) => line.trim());
		const last = lines.findLastIndex((line) => line.trim());
		if (first < 0) report(file, node, `src="${attributes.get('src')}": every line of the quote is blank: quote lines that hold code`);
		else if (first > 0 || last < lines.length - 1) report(file, node, `src="${attributes.get('src')}": the quote ${first > 0 ? 'starts' : 'ends'} with a blank line, which Expressive Code does not draw, so ${first > 0 ? 'its line numbers and marks would be one line late' : 'the page would show fewer lines than src names'}: quote L${source.start + first}-L${source.start + last} instead`);
	}
	const meta = [`showLineNumbers`, `startLineNumber=${source.start}`, ...rest];
	if (attributes.has('mark')) {
		const marks = relativeMarks(attributes.get('mark'), source.start, source.end);
		if (marks.error) report(file, node, marks.error);
		else meta.push(`mark={${marks.marks}}`);
	}
	node.meta = meta.join(' ');
	const prefix = engine ? '' : `${source.namespace}:`;
	return { node: element('div', { className: ['book-excerpt'], dataSource: `${prefix}${source.path}#L${source.start}-L${source.end}` }, [source.namespace === 'vendor' ? vendorHeader(context, file, node, source) : sourceHeader(context, source), node]), engine };
}
