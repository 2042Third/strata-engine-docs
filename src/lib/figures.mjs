// Figure manifests (src/content/figures/<part>/<chapter>.json, the recipes of plan/pipelines.md §5.2) and the files
// tools/figures.py publishes from them into src/assets/figures/<part>/<chapter>/ (pipelines.md §5.7, site.md
// "Pictures"): one file per picture, named <figure>[-<variant>][-<crop>].<avif|webp|svg>, and taken.json, the stamps.
// tools/figures.py checks every recipe against its schema; this module reads what the build needs to draw a figure:
// which file a reference means and in which format, its caption and alt text, its crops, and whether the engine took
// it (a stamp in taken.json) or it is still a placeholder.

import { readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { parseMeta } from './markdown.mjs';

export const c_TakenFile = 'taken.json';
// Extensions a published picture of another format than its recipe's would have: the build names such a file instead
// of passing over it (.png is never published; site.md "Pictures").
export const c_PictureExtensions = ['.avif', '.webp', '.svg', '.png', '.jpg', '.jpeg', '.gif'];
// Pictures of the editor's interface and of other programs keep their pixels (pipelines.md §5.7).
const c_InterfaceKinds = ['editor', 'tool'];
const c_CropName = /^[a-z0-9]+(-[a-z0-9]+)*$/;
// A crop of a look-dev shot has no scale in Tools/LookDev/Shots.json; the book enlarges it 4 times, as LookDev.py does
// (.tools/handover/figures-format.md §2).
export const c_ShotCropScale = 4;
export const c_DefaultSize = [1920, 1080];
// Fields of the spike's recipes that pipelines.md §5.2 replaced, with what a writer writes instead.
const c_SpikeFields = {
	taken: 'stamps live in taken.json beside the published files, which tools/figures.py publish writes',
	crop: 'crops are named: "crops": [{"name": "<word>", "rect": [x0, y0, x1, y1], "scale": <1 to 8>}], normalized to the picture',
	capture: 'a live picture is "live": {"atFixedStep": <n>, "frames": <1 to 16>} with "play" (plan/pipelines.md §5.2)',
	waits_for: 'write "waitsFor" with one of the engine additions of plan/pipelines.md §11',
};

const s_Manifests = new Map();
const s_Taken = new Map();

function readJson(file, what) {
	let text;
	try {
		text = readFileSync(file, 'utf8');
	} catch (error) {
		if (error.code === 'ENOENT') return { missing: true };
		throw error;
	}
	try {
		return { text, data: JSON.parse(text) };
	} catch (error) {
		throw new Error(`${file}: ${what} is not valid JSON (${error.message})`);
	}
}

/** The manifest of a page: `{ file, figures: Map<id, entry> }`, or null when the page has none. Throws on bad JSON. */
export function loadManifest(figuresDir, pageId) {
	const file = path.join(figuresDir, `${pageId}.json`);
	const { missing, text, data } = readJson(file, 'the figure manifest');
	if (missing) return null;
	// Parsed once per content: manifests are small, and a time stamp can miss a change made within its resolution.
	const cached = s_Manifests.get(file);
	if (cached && cached.text === text) return cached.manifest;
	if (!data || !Array.isArray(data.figures)) throw new Error(`${file}: "figures" must be a list of figure recipes`);
	const figures = new Map();
	for (const entry of data.figures) {
		if (typeof entry?.id !== 'string') throw new Error(`${file}: a figure has no "id"`);
		if (figures.has(entry.id)) throw new Error(`${file}: the id "${entry.id}" is used twice`);
		figures.set(entry.id, entry);
	}
	const manifest = { file, figures };
	s_Manifests.set(file, { text, manifest });
	return manifest;
}

/**
 * The stamps of a page's published files (taken.json, pipelines.md §5.7): `{ file, files: Map<name, record> }`, or null
 * when nothing of the page is stamped. A record names its figure, variant and crop and holds the published file's
 * SHA-256; tools/figures.py checks the rest of it against tools/schemas/taken.schema.json. Throws on a file the build
 * cannot read.
 */
export function loadTaken(picturesDir, pageId) {
	const file = path.join(picturesDir, ...pageId.split('/'), c_TakenFile);
	const { missing, text, data } = readJson(file, c_TakenFile);
	if (missing) return null;
	const cached = s_Taken.get(file);
	if (cached && cached.text === text) return cached.taken;
	if (!data || typeof data.files !== 'object' || data.files === null || Array.isArray(data.files)) throw new Error(`${file}: "files" must map each published file's name to its stamp (tools/figures.py publish writes it)`);
	const files = new Map();
	for (const [name, record] of Object.entries(data.files)) {
		if (!record || typeof record !== 'object' || !/^[0-9a-f]{64}$/.test(record.sha256 ?? '')) throw new Error(`${file}: the stamp of ${name} has no "sha256" of 64 hex digits (publish the figure again with tools/figures.py publish)`);
		files.set(name, record);
	}
	const taken = { file, files };
	s_Taken.set(file, { text, taken });
	return taken;
}

/**
 * The id of a figure on its page. The first use of a recipe is "fig-<id>" (what links name); later uses of the same
 * recipe (a compare and its crop, variants shown as separate figures) are "fig-<id>-<variant or compare>[-<crop>]",
 * with "-2", "-3" when that is taken too, so that no two elements share an id. A crop adds its name ("-crop" when the
 * directive names none). `used` holds the ids given so far on the page; the page index (src/lib/pages.mjs) and the
 * figures plugin call this in document order.
 */
export function figureAnchor(used, directive) {
	const attributes = directive.attributes ?? {};
	const base = `fig-${attributes.id}`;
	const crop = 'crop' in attributes ? (attributes.crop || 'crop') : null;
	const suffix = [directive.name === 'compare' ? 'compare' : attributes.variant, crop].filter(Boolean).join('-');
	let anchor = [base, suffix ? `${base}-${suffix}` : null].find((candidate) => candidate && !used.has(candidate));
	for (let count = 2; !anchor; count++) if (!used.has(`${base}-${count}`)) anchor = `${base}-${count}`;
	used.add(anchor);
	return anchor;
}

/**
 * The text figure a fence shows (pipelines.md §5): `{ id, variant }` from its capture="…" and variant="…", or null for
 * another fence.
 */
export function captureOf(meta) {
	const { attributes } = parseMeta(meta, ['capture', 'variant']);
	return attributes.has('capture') ? { id: attributes.get('capture'), variant: attributes.get('variant') ?? null } : null;
}

/** The id of a text figure on its page, given as a picture's is (figureAnchor). */
export function captureAnchor(used, capture) {
	return figureAnchor(used, { name: 'figure', attributes: { id: capture.id, ...(capture.variant ? { variant: capture.variant } : {}) } });
}

/** The names of an entry's variants in their order ("off", "on"), or [] for a single picture. */
export function variantNames(entry) {
	return entry.variants && typeof entry.variants === 'object' ? Object.keys(entry.variants) : [];
}

/**
 * How a recipe's pictures are published (pipelines.md §5.7, as tools/figures.py reads it): "text" (a text figure, shown
 * in a fence), "svg" (a drawing), "lossless" (pictures of the interface unless their recipe says lossy; renders that say
 * so) or "lossy" (every other render, and the interface pictures whose recipe says so: those that are mostly the
 * engine's image, whose text stays as sharp at AVIF quality 90; plan/critique/rulings-13.md, R59).
 */
export function publishOf(entry) {
	if (entry.kind === 'text') return 'text';
	if (entry.kind === 'diagram') return 'svg';
	if (c_InterfaceKinds.includes(entry.kind)) return entry.publish === 'lossy' ? 'lossy' : 'lossless';
	return entry.publish === 'lossless' ? 'lossless' : 'lossy';
}

/** The file format of a way of publishing: AVIF for lossy pictures, lossless WebP, SVG drawings, text. */
export function extensionOf(publish) {
	return { lossy: '.avif', lossless: '.webp', svg: '.svg', text: '.txt' }[publish];
}

/** The published file's name of one picture: <figure>[-<variant>][-<crop>] and its extension (a crop is lossless WebP). */
export function pictureName(entry, variant = null, crop = null) {
	const stem = [entry.id, variant, crop].filter(Boolean).join('-');
	return `${stem}${crop ? '.webp' : extensionOf(publishOf(entry))}`;
}

/** The recipe's own crops, `[{ name, rect, scale }]` ([] when it has none, or when its crops are its shot's). */
export function recipeCrops(entry) {
	return Array.isArray(entry.crops) ? entry.crops : [];
}

/** The size of the picture a recipe captures: its `size`, or 1920 × 1080. */
export function captureSize(entry) {
	return Array.isArray(entry.size) && entry.size.length === 2 ? entry.size : c_DefaultSize;
}

/**
 * A crop's rectangle in the pixels of a picture of `width` × `height`: [x0, y0, x1, y1], cut as LookDev.py and
 * tools/figures.py cut it (each normalized corner times the size, rounded toward zero).
 */
export function cropPixels(rect, width, height) {
	return [Math.trunc(rect[0] * width), Math.trunc(rect[1] * height), Math.trunc(rect[2] * width), Math.trunc(rect[3] * height)];
}

/** The problems of the fields of a recipe that the build reads: caption, alt, shows, its crops, the spike's fields. */
export function entryProblems(entry) {
	const problems = [];
	if (typeof entry.caption !== 'string' || !entry.caption.trim()) problems.push(`figure "${entry.id}" has no caption (what to notice)`);
	if (typeof entry.alt !== 'string' || !entry.alt.trim()) problems.push(`figure "${entry.id}" has no alt text (what it shows)`);
	if (typeof entry.shows !== 'string' || !entry.shows.trim()) problems.push(`figure "${entry.id}" does not say what it "shows"`);
	for (const [field, instead] of Object.entries(c_SpikeFields)) if (field in entry) problems.push(`figure "${entry.id}" has the field "${field}", which recipes no longer have: ${instead}`);
	if ('crops' in entry) {
		if (!Array.isArray(entry.crops) || entry.crops.length === 0) problems.push(`figure "${entry.id}": "crops" is a list of at least one crop`);
		else if ('shot' in entry) problems.push(`figure "${entry.id}" has a shot, whose crops come from Tools/LookDev/Shots.json: remove "crops"`);
		const names = new Set();
		for (const crop of Array.isArray(entry.crops) ? entry.crops : []) {
			const name = crop?.name;
			if (typeof name !== 'string' || !c_CropName.test(name)) problems.push(`figure "${entry.id}": a crop's "name" is a lowercase word or words joined by "-" (found ${JSON.stringify(name)})`);
			else if (names.has(name)) problems.push(`figure "${entry.id}": the crop "${name}" is named twice`);
			names.add(name);
			const rect = crop?.rect;
			if (!Array.isArray(rect) || rect.length !== 4 || !rect.every((value) => typeof value === 'number' && value >= 0 && value <= 1) || rect[0] >= rect[2] || rect[1] >= rect[3]) {
				problems.push(`figure "${entry.id}": the crop "${name}" needs "rect": [x0, y0, x1, y1] from 0 to 1, with x0 < x1 and y0 < y1`);
			}
			if (!Number.isInteger(crop?.scale) || crop.scale < 1 || crop.scale > 8) problems.push(`figure "${entry.id}": the crop "${name}" needs a whole "scale" from 1 to 8 (the factor the page enlarges it by)`);
		}
	}
	return problems;
}

/** The crops taken.json stamps for one picture of a recipe (the names of a shot's crops, which the build cannot read). */
export function stampedCrops(taken, entry, variant) {
	if (!taken) return [];
	const names = [];
	for (const record of taken.files.values()) {
		if (record.figure === entry.id && (record.variant ?? null) === (variant ?? null) && typeof record.crop === 'string') names.push(record.crop);
	}
	return [...new Set(names)].sort();
}

/**
 * The crop a directive names: `{ crop: { name, scale, rect } }` or `{ error }`. `requested` is the directive's crop
 * attribute: a name, or "" for a bare `crop`, which a recipe with exactly one crop allows (figures-format.md §2). A
 * recipe with a shot takes the shot's crops (scale 4), whose names the build knows only from taken.json.
 */
export function resolveCrop(entry, requested, taken, variant) {
	const own = recipeCrops(entry);
	if (own.length) {
		if (requested) {
			const crop = own.find((candidate) => candidate?.name === requested);
			return crop ? { crop } : { error: `figure "${entry.id}" has no crop "${requested}" (it has ${own.map((candidate) => candidate?.name).join(', ')})` };
		}
		if (own.length === 1) return { crop: own[0] };
		return { error: `figure "${entry.id}" has the crops ${own.map((candidate) => candidate?.name).join(', ')}: name one with crop=<name>` };
	}
	if ('shot' in entry) {
		if (requested) return { crop: { name: requested, scale: c_ShotCropScale, rect: null } };
		const stamped = stampedCrops(taken, entry, variant);
		if (stamped.length === 1) return { crop: { name: stamped[0], scale: c_ShotCropScale, rect: null } };
		return { error: `figure "${entry.id}" takes its crops from the shot ${entry.shot} of Tools/LookDev/Shots.json: name one with crop=<name>` };
	}
	return { error: `figure "${entry.id}" has no crops in its recipe: add "crops", or remove crop` };
}

/** Whether a file exists (and is a file). */
export function isFile(file) {
	try {
		return statSync(file).isFile();
	} catch (error) {
		if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return false;
		throw error;
	}
}

/**
 * Files beside a picture that carry its name with another picture's extension ("shot.webp" or "shot.png" where the
 * recipe publishes "shot.avif"): published in the wrong format, they are named so that they are removed.
 */
export function strayPictures(folder, name) {
	const stem = name.slice(0, name.lastIndexOf('.'));
	let entries;
	try {
		entries = readdirSync(folder);
	} catch (error) {
		if (error.code === 'ENOENT') return [];
		throw error;
	}
	return entries.filter((other) => other !== name && c_PictureExtensions.some((extension) => other.toLowerCase() === `${stem}${extension}`)).sort();
}

/**
 * Every picture file a recipe promises: `{ name, variant, crop }` per published picture and crop ([] for a text
 * figure, which is a fence's text). A shot's crops are those taken.json stamps.
 */
export function promisedPictures(entry, taken = null) {
	if (entry.kind === 'text') return [];
	const variants = variantNames(entry);
	const result = [];
	for (const variant of variants.length ? variants : [null]) {
		result.push({ name: pictureName(entry, variant), variant, crop: null });
		if (entry.kind === 'diagram') continue;
		const crops = recipeCrops(entry).length ? recipeCrops(entry).map((crop) => crop?.name).filter((name) => typeof name === 'string') : ('shot' in entry ? stampedCrops(taken, entry, variant) : []);
		for (const crop of crops) result.push({ name: pictureName(entry, variant, crop), variant, crop });
	}
	return result;
}
