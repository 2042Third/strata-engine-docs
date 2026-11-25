// figures: ::figure{id=…} draws a picture of the chapter's figure manifest with its caption and alt text, and
// ::figure{id=… crop=<name>} one of its crops; ::compare{id=…} two variants of one recipe as a before/after slider (a
// web component; without scripts both pictures show side by side, labelled with their variants' names). Each picture
// is the one file tools/figures.py published for it (plan/site.md "Pictures"): a lossy render is an AVIF served at its
// own width with a 960-pixel AVIF beside it in its srcset; a lossless picture or a crop is a WebP served alone; a
// drawing is SVG, inlined. A crop is shown at the largest whole factor up to its recipe's scale that fits the column
// (src/styles/book.css), never smoothed. The page's first picture loads at once, at high priority, when it stands in
// the first screen (where it is the largest thing painted); every other picture, a slider's second side too, loads
// when it is near.
// A picture the engine has not taken yet shows as a labelled placeholder (no file), or with a "placeholder picture"
// note (a file without its stamp in taken.json), in drafts; a release build refuses both, and a figure no take makes at
// the pin (waitsFor, blocked) whatever its files: its page places the figure that stands in for it (standIn).

import path from 'node:path';
import { captureSize, cropPixels, entryProblems, figureAnchor, isFile, loadManifest, loadTaken, pictureName, publishOf, resolveCrop, strayPictures, variantNames } from '../lib/figures.mjs';
import { describePicture, readText, servedAs, servedFiles } from '../lib/images.mjs';
import { element, hastElement, pageOf, rawHtml, report, text, withoutTerms } from './shared.mjs';

// The width of the content column (Starlight's layout with src/styles/book.css, measured in the built site): the
// viewport less 1rem of padding on each side below 50rem; beside the 18.75rem sidebar from 50rem; beside the sidebar
// and the table of contents, with 1.5rem of padding, from 72rem; never more than 48rem (--sl-content-width). A phone of
// 412 pixels thus asks for 380, and at 1.75 device pixels per pixel takes the 960-pixel candidate.
export const c_Sizes = [
	'(min-width: 91.5rem) 48rem',
	'(min-width: 85.5rem) calc(50vw + 2.25rem)',
	'(min-width: 72rem) calc(100vw - 40.5rem)',
	'(min-width: 68.75rem) 48rem',
	'(min-width: 50rem) calc(100vw - 20.75rem)',
	'calc(100vw - 2rem)',
].join(', ');
// The first screen: a figure after more text than this stands below it, on a desktop's screen as on a phone's, where
// even a figure at the top of a page starts below the first screen (measured in the built site, 2026-11-25: at
// 1350 × 940 a figure after about 240 characters of text starts at 936 pixels; at 412 × 823 the first figure of every
// page starts below 970). Only a figure in the first screen can be the largest thing painted, so only it loads at once
// and at a high priority: Lighthouse counts every request that starts before the largest paint, and a picture below
// the first screen that loaded at once moved image/spatial-aa's by the download of its 7 MB (measured 2026-11-25).
export const c_FirstScreenCharacters = 300;

const c_Formats = { avif: 'AVIF (a lossy picture)', webp: 'lossless WebP', svg: 'SVG (a drawing)' };

/** The figure directive's attributes: `{ id, variant, crop, before, after }`, or `{ error }`. */
export function figureAttributes(node) {
	const attributes = node.attributes ?? {};
	const known = node.name === 'compare' ? ['id', 'before', 'after'] : ['id', 'variant', 'crop'];
	// A leaf figure's label would vanish: its caption comes from the recipe (a container figure's body adds to it).
	if (node.type === 'leafDirective' && node.children?.length) return { error: `::${node.name}[…] takes no label: the caption comes from the recipe (or write :::${node.name}{id=…} with text that adds to it)` };
	for (const name of Object.keys(attributes)) if (!known.includes(name)) return { error: `::${node.name} has no attribute "${name}" (it takes ${known.join(', ')})` };
	if (!attributes.id) return { error: `::${node.name} needs an id: ::${node.name}{id=<id of the chapter's figure manifest>}` };
	return { id: attributes.id, variant: attributes.variant ?? null, crop: 'crop' in attributes ? String(attributes.crop ?? '') : null, before: attributes.before ?? null, after: attributes.after ?? null };
}

/** The `srcset` of a lossy picture: its derived AVIFs and the published file, each with its width. */
export function sourceSet(files) {
	return files.map((file) => `${file.url} ${file.width}w`).join(', ');
}

function placeholder(entry, width, height, label) {
	return withoutTerms(element('div', { className: ['book-placeholder'], role: 'img', ariaLabel: entry.alt, style: `aspect-ratio: ${width} / ${height}` }, [
		element('strong', { className: ['book-placeholder__title'] }, [text(label)]),
		element('span', { className: ['book-placeholder__shows'] }, [text(entry.shows ?? '')]),
		element('span', { className: ['book-placeholder__recipe'] }, [text(`Recipe: ${entry.id}`)]),
	]));
}

/** The size a placeholder of a picture keeps the page's place for: the capture's, or a crop's rectangle of it. */
function placeholderSize(entry, crop) {
	const [width, height] = captureSize(entry);
	if (!crop) return [width, height];
	if (!crop.rect) return [16, 9];
	const [x0, y0, x1, y1] = cropPixels(crop.rect, width, height);
	return [x1 - x0, y1 - y0];
}

/**
 * The <img> of a published picture (hast): its own file as `src`, with the derived AVIFs in `srcset` and the column's
 * width in `sizes` when it is lossy, its size, and `loading="eager"` with `fetchpriority="high"` for the page's first
 * picture when it stands in the first screen (`inFirstScreen`); `loading="lazy"` for every other.
 */
export function imageHast(files, entry, { first, inFirstScreen = false, crop }) {
	const [published, ...derived] = files;
	const atOnce = first && inFirstScreen;
	const properties = { src: published.url, width: published.width, height: published.height, alt: entry.alt, decoding: 'async', loading: atOnce ? 'eager' : 'lazy' };
	if (atOnce) properties.fetchPriority = 'high';
	if (derived.length) {
		properties.srcSet = sourceSet([...derived, published]);
		properties.sizes = c_Sizes;
	}
	if (crop) properties.className = ['book-crop__img'];
	return { type: 'element', tagName: 'img', properties, children: [] };
}

/**
 * One picture of an entry, drawn or as its placeholder: `{ node, draft, size, record }`. `state.first` is true until
 * the page's first picture is drawn; `state.textBefore` counts the characters of text the page shows before it.
 */
async function drawPicture(context, file, directive, pageId, entry, variant, crop, state, taken) {
	const name = pictureName(entry, variant, crop?.name ?? null);
	const folder = path.join(context.settings.picturesDir, ...pageId.split('/'));
	const relativeFolder = path.relative(context.settings.root, folder).split(path.sep).join('/');
	const publish = crop ? 'lossless' : publishOf(entry);
	for (const stray of strayPictures(folder, name)) {
		report(file, directive, `${relativeFolder}/${stray}: figure "${entry.id}" is published as ${name} (${crop ? 'a crop is lossless WebP' : c_Formats[path.extname(name).slice(1)]})${stray.toLowerCase().endsWith('.png') ? '; PNG is not a published format' : ''}: remove ${stray}`);
	}
	const [placeWidth, placeHeight] = placeholderSize(entry, crop);
	const published = path.join(folder, name);
	if (!isFile(published)) {
		const drawing = publish === 'svg';
		if (context.settings.release) report(file, directive, `figure "${entry.id}" has no ${drawing ? 'drawing' : crop ? 'crop' : 'picture'} ${relativeFolder}/${name} yet: a release needs every picture`);
		return { node: placeholder(entry, placeWidth, placeHeight, drawing ? 'Drawing not made yet' : crop ? 'Crop not taken yet' : 'Picture not taken yet'), draft: true, size: null, record: null };
	}
	const description = await describePicture(published);
	const expected = path.extname(name).slice(1);
	if (description.format !== expected) {
		report(file, directive, `${relativeFolder}/${name} is ${description.format ? `a ${description.format.toUpperCase()} file` : 'no picture the build can read'}, not what its name says: publish it again with tools/figures.py publish`);
		return { node: placeholder(entry, placeWidth, placeHeight, 'Picture not taken yet'), draft: true, size: null, record: null };
	}
	if (expected === 'webp' && description.lossless !== true) {
		report(file, directive, `${relativeFolder}/${name} is a lossy WebP file: ${crop ? 'crops' : 'these pictures'} are lossless WebP; publish it again with tools/figures.py publish`);
	}
	const record = taken?.files.get(name) ?? null;
	// A drawing (kind "diagram", an SVG file) is the writer's own work: no engine takes it, so it has no stamp, and it is
	// final when its page is (a release build refuses draft pages). tools/figures.py applies the same rule.
	if (publish === 'svg') {
		if (record) report(file, directive, `figure "${entry.id}" is a drawing, which no engine takes: its file needs no stamp in taken.json`);
		// Its box scrolls on a narrow screen (book.css), so it takes the keyboard's focus.
		return { node: element('div', { className: ['book-figure__drawing'], role: 'img', ariaLabel: entry.alt, tabIndex: 0 }, [rawHtml(readText(published))]), draft: false, size: [description.width, description.height], record: null };
	}
	let draft = false;
	if (!record) {
		draft = true;
		if (context.settings.release) report(file, directive, `figure "${entry.id}": ${relativeFolder}/${name} is a placeholder picture: taken.json has no stamp for it (take and publish it with tools/figures.py)`);
	} else if (record.sha256 !== description.hash) {
		report(file, directive, `figure "${entry.id}": ${relativeFolder}/${name} is not the file the engine took (its SHA-256 differs from its stamp in taken.json): take and publish it again with tools/figures.py`);
	}
	const relative = path.relative(context.settings.picturesDir, published).split(path.sep).join('/');
	const served = await servedAs(context.settings.picturesDir, relative, description);
	const files = servedFiles({ base: context.settings.base, cacheDir: context.settings.cacheDir }, description, served);
	const image = imageHast(files, entry, { first: state.first, inFirstScreen: state.textBefore <= c_FirstScreenCharacters, crop: Boolean(crop) });
	state.first = false;
	// The picture links its published file, for a full-size view.
	let node = hastElement('a', { className: ['book-figure__zoom'], href: files[0].url }, [image]);
	if (crop) {
		// The style sheet enlarges the crop by the largest whole factor up to its scale that fits the column; a crop wider
		// than the column scrolls (and its link keeps the scrolled box reachable from the keyboard).
		node = element('div', { className: ['book-crop'], style: `--book-crop-width: ${description.width}px; --book-crop-scale: ${crop.scale}` }, [node]);
	}
	return { node, draft, size: [description.width, description.height], record };
}

/** Why no take makes the figure at the pin ("waits for …", "is blocked: …"), or null: every variant waits or is blocked. */
export function unmadeReason(entry) {
	const sides = variantNames(entry).length ? variantNames(entry).map((name) => ({ ...entry, ...entry.variants[name] })) : [entry];
	if (!sides.every((side) => side.waitsFor || side.blocked)) return null;
	const side = sides[0];
	return side.waitsFor ? `waits for ${side.waitsFor}` : `is blocked: ${side.blocked}`;
}

function caption(entry, extra, draft) {
	const children = [text(entry.caption ?? ''), ...extra];
	if (draft) children.push(text(' '), withoutTerms(element('span', { className: ['book-draft-label'] }, [text('Placeholder picture: the engine has not rendered this figure yet.')])));
	return element('figcaption', {}, children);
}

export function remarkBookFigures(context) {
	return function attacher() {
		return async function transformer(tree, file) {
			const index = await context.index();
			const page = pageOf(file, index);
			if (!page) return;
			const jobs = [];
			// The text before each figure, in document order: how far down the page it stands (c_FirstScreenCharacters).
			let characters = 0;
			const find = (parent) => {
				(parent.children ?? []).forEach((node, position) => {
					if ((node.type === 'leafDirective' || node.type === 'containerDirective') && (node.name === 'figure' || node.name === 'compare')) {
						jobs.push({ parent, position, node, textBefore: characters });
						return;
					}
					if (typeof node.value === 'string') characters += node.value.length;
					find(node);
				});
			};
			find(tree);
			if (jobs.length === 0) return;
			// Ids in document order, as the page index gives them (a recipe used twice gets two ids).
			const used = new Set();
			for (const job of jobs) job.anchor = job.node.attributes?.id ? figureAnchor(used, job.node) : null;
			// A figure is drawn from the manifest and the stamps of the page it was written on: a question copied onto a
			// part's review page keeps its own page's pictures (src/lib/partpages.mjs).
			const owners = new Map();
			const state = { first: true, textBefore: 0 };
			for (const job of jobs) {
				const owner = job.node.data?.bookPageId ?? page.id;
				if (!owners.has(owner)) {
					try {
						owners.set(owner, { manifest: loadManifest(context.settings.figuresDir, owner), taken: loadTaken(context.settings.picturesDir, owner) });
					} catch (error) {
						owners.set(owner, { error: error.message });
					}
				}
				const { manifest, taken, error } = owners.get(owner);
				state.textBefore = job.textBefore;
				if (error) {
					report(file, job.node, error);
					continue;
				}
				const replacement = await drawFigure(context, file, owner, manifest, taken, job.node, job.anchor, state);
				if (replacement) job.parent.children[job.position] = replacement;
			}
		};
	};
}

async function drawFigure(context, file, pageId, manifest, taken, node, anchor, state) {
	const attributes = figureAttributes(node);
	if (attributes.error) {
		report(file, node, attributes.error);
		return null;
	}
	if (!manifest) {
		report(file, node, `::${node.name}{id=${attributes.id}}: the page has no figure manifest (src/content/figures/${pageId}.json)`);
		return null;
	}
	const entry = manifest.figures.get(attributes.id);
	if (!entry) {
		report(file, node, `::${node.name}{id=${attributes.id}}: src/content/figures/${pageId}.json has no figure "${attributes.id}"`);
		return null;
	}
	const variants = variantNames(entry);
	// A text figure is text the engine printed: a fence shows it, so that it can be read, copied and searched.
	if (entry.kind === 'text') {
		report(file, node, `figure "${entry.id}" is a text figure: show it in a fence, \`\`\`text capture="${entry.id}"${variants.length ? ` variant="${variants[0]}"` : ''}`);
		return null;
	}
	const problems = entryProblems(entry);
	for (const problem of problems) report(file, node, problem);
	if (problems.length) return null;
	// A figure no take makes at the pin (it waits for an engine addition, or is blocked) is a placeholder in every build:
	// drafts keep it, a release shows none, and the page places its stand-in instead (plan/pipelines.md §11).
	const unmade = unmadeReason(entry);
	if (unmade && context.settings.release) {
		report(file, node, `figure "${entry.id}" ${unmade}, so a release would show a placeholder: ${entry.standIn ? `place its stand-in ::figure{id=${entry.standIn}} in its place` : 'place the figure that stands in for it (its recipe\'s standIn) in its place'}`);
	}
	// The body of a container figure adds to the caption (links and terms are welcome there).
	const extra = node.type === 'containerDirective' && node.children.length ? [text(' '), ...node.children.flatMap((child) => (child.type === 'paragraph' ? child.children : [child]))] : [];
	if (node.name === 'figure') {
		const variant = attributes.variant;
		if (variants.length && !variant) {
			report(file, node, `figure "${entry.id}" has the variants ${variants.join(', ')}: name one with variant=…, or draw them with ::compare`);
			return null;
		}
		if (variant && !variants.includes(variant)) {
			report(file, node, `figure "${entry.id}" has no variant "${variant}" (it has ${variants.join(', ') || 'none'})`);
			return null;
		}
		let crop = null;
		if (attributes.crop !== null) {
			if (entry.kind === 'diagram') {
				report(file, node, `figure "${entry.id}" is a drawing: it has no crops`);
				return null;
			}
			const resolved = resolveCrop(entry, attributes.crop, taken, variant);
			if (resolved.error) {
				report(file, node, resolved.error);
				return null;
			}
			crop = resolved.crop;
		}
		const { node: picture, draft } = await drawPicture(context, file, node, pageId, entry, variant, crop, state, taken);
		return element('figure', { className: crop ? ['book-figure', 'book-figure--crop'] : ['book-figure'], id: anchor }, [picture, caption(entry, extra, draft)]);
	}
	const before = attributes.before ?? variants[0];
	const after = attributes.after ?? variants[1];
	if (variants.length < 2 || !variants.includes(before) || !variants.includes(after) || before === after) {
		report(file, node, `::compare{id=${entry.id}} needs two different variants of the recipe (it has ${variants.join(', ') || 'none'})`);
		return null;
	}
	if (entry.kind === 'diagram') {
		report(file, node, `figure "${entry.id}" is a drawing, which has no variants to compare: draw two figures`);
		return null;
	}
	const items = [];
	const sides = [];
	let draft = false;
	for (const variant of [before, after]) {
		const drawn = await drawPicture(context, file, node, pageId, entry, variant, null, state, taken);
		draft ||= drawn.draft;
		sides.push({ variant, ...drawn });
		// The slider names its sides after the variants (a variant has no label of its own: pipelines.md §5.2).
		items.push(element('div', { className: ['book-compare__item'], dataLabel: variant }, [drawn.node, withoutTerms(element('span', { className: ['book-compare__label'] }, [text(variant)]))]));
	}
	// Both sides of a slider line up only when they are the same size and encoded alike (site.md "Pictures").
	const [one, other] = sides;
	if (one.size && other.size && (one.size[0] !== other.size[0] || one.size[1] !== other.size[1])) {
		report(file, node, `::compare{id=${entry.id}}: the sides ${one.variant} (${one.size.join(' × ')}) and ${other.variant} (${other.size.join(' × ')}) differ in size: take and publish both again`);
	}
	if (one.record && other.record && JSON.stringify(one.record.encoder ?? null) !== JSON.stringify(other.record.encoder ?? null)) {
		report(file, node, `::compare{id=${entry.id}}: the sides ${one.variant} and ${other.variant} were encoded with different settings (taken.json): publish both again with tools/figures.py publish`);
	}
	return element('figure', { className: ['book-figure', 'book-compare'], id: anchor }, [
		element('book-compare', {}, [element('div', { className: ['book-compare__pair'] }, items)]),
		caption(entry, extra, draft),
	]);
}
