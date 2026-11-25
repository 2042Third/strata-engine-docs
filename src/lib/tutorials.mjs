// A tutorial's files as the build reads them (plan/pipelines.md §6): the tutorial file
// tutorials/<part>/<chapter>.tutorial.json with its stages, the downloads tools/tutorials.py publishes into
// public/downloads/tutorials/<part>/<chapter>/ (the project after a stage, stage-<step>.zip, and the reader's copy of a
// stage's commands, stage-<step>.commands.json), and the stamp tutorials/<part>/<chapter>.stamp.json, which says that
// the tutorial ran against the engine at the pin (§6.4). The build writes none of them: ::checkpoint links the
// downloads, a worked solution's answer links the solution's download (public/downloads/solutions/, §6.3), and a
// release build refuses a tutorial without a current stamp.

import { createHash } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { withBase } from './settings.mjs';

/** The files of a tutorial page, relative to the project and absolute. */
export function tutorialPaths(settings, pageId) {
	const relative = {
		tutorial: `tutorials/${pageId}.tutorial.json`,
		stamp: `tutorials/${pageId}.stamp.json`,
		downloads: `public/downloads/tutorials/${pageId}`,
	};
	const absolute = Object.fromEntries(Object.entries(relative).map(([key, value]) => [key, path.join(settings.root, ...value.split('/'))]));
	return { relative, absolute };
}

function readJson(file) {
	try {
		return { data: JSON.parse(readFileSync(file, 'utf8')) };
	} catch (error) {
		if (error.code === 'ENOENT') return { missing: true };
		return { error: error.message };
	}
}

/**
 * The tutorial file of a page: `{ missing: true }`, `{ error }`, or `{ stages: Map<step, stage>, startsFrom, patch }`.
 * Only what the build needs is checked here; tools/tutorials.py check holds the whole schema.
 */
export function readTutorial(settings, pageId) {
	const { relative, absolute } = tutorialPaths(settings, pageId);
	const read = readJson(absolute.tutorial);
	if (read.missing) return { missing: true };
	if (read.error) return { error: `${relative.tutorial} is not valid JSON: ${read.error}` };
	const data = read.data;
	if (!data || typeof data !== 'object' || Array.isArray(data)) return { error: `${relative.tutorial} is not a JSON object` };
	if (data.page !== pageId) return { error: `${relative.tutorial} says "page": ${JSON.stringify(data.page)}; it is the tutorial of ${pageId}` };
	const stages = new Map();
	if (data.stages !== undefined) {
		if (!Array.isArray(data.stages)) return { error: `${relative.tutorial}: "stages" is not a list` };
		for (const stage of data.stages) {
			if (!stage || !Number.isInteger(stage.step) || stage.step < 1) return { error: `${relative.tutorial}: every stage has a "step", the number of the page's step` };
			stages.set(stage.step, stage);
		}
	}
	return { stages, startsFrom: data.startsFrom ?? null, patch: data.patch ?? null };
}

function fileInfo(file) {
	try {
		const info = statSync(file);
		return info.isFile() ? { bytes: info.size } : null;
	} catch (error) {
		if (error.code === 'ENOENT') return null;
		throw error;
	}
}

/**
 * A download the tools publish under public/ (`download`, such as "downloads/solutions/make/spin/exercise-1.zip"):
 * `{ url, bytes, relative }`, its URL under the base, its size and its path in the repository, or null when the file
 * does not exist yet.
 */
export function publishedDownload(settings, download) {
	const info = fileInfo(path.join(settings.root, 'public', ...download.split('/')));
	return info ? { url: withBase(settings.base, `/${download}`), bytes: info.bytes, relative: `public/${download}` } : null;
}

/**
 * The downloads of one stage: `{ zip, commands }`, each `{ url, bytes, relative }` or null when the file does not exist
 * (tools/tutorials.py has not published it yet).
 */
export function stageDownloads(settings, pageId, step) {
	const { relative } = tutorialPaths(settings, pageId);
	const one = (name) => publishedDownload(settings, `downloads/tutorials/${pageId}/${name}`);
	return { zip: one(`stage-${step}.zip`), commands: one(`stage-${step}.commands.json`), names: { zip: `${relative.downloads}/stage-${step}.zip`, commands: `${relative.downloads}/stage-${step}.commands.json` } };
}

/** "1.2 MB", "340 KB": a download's size for readers. */
export function formatBytes(bytes) {
	if (bytes >= 1000 * 1000) return `${(bytes / (1000 * 1000)).toFixed(1)} MB`;
	return `${Math.max(1, Math.round(bytes / 1000))} KB`;
}

function sha256(file) {
	return createHash('sha256').update(readFileSync(file)).digest('hex');
}

/** Why a run's inputs are not the files as they are now, or null (pipelines.md §6.4: the inputs a stamp records). */
function inputsProblem(settings, inputs, tutorialFile) {
	if (!inputs || typeof inputs !== 'object' || Array.isArray(inputs) || Object.keys(inputs).length === 0) return 'it records no inputs';
	if (!Object.hasOwn(inputs, tutorialFile)) return `its inputs do not hold ${tutorialFile}`;
	for (const [name, digest] of Object.entries(inputs)) {
		if (name.startsWith('/') || name.split('/').includes('..')) return `the input "${name}" is not a path of this repository`;
		const file = path.join(settings.root, ...name.split('/'));
		if (!fileInfo(file)) return `the input ${name} does not exist`;
		if (sha256(file) !== digest) return `${name} changed since the run`;
	}
	return null;
}

/**
 * Whether a tutorial changes the engine, as tools/tutorials.py's changes_engine decides: it has its patch, or its
 * startsFrom chain applies one (a tutorial of the chain with its patch, or a link that starts from an exercise's worked
 * solution). A chain that is broken or loops is false here; tools/tutorials.py check reports it.
 */
export function changesEngine(settings, pageId) {
	const seen = new Set();
	let key = pageId;
	while (!seen.has(key)) {
		seen.add(key);
		const tutorial = readTutorial(settings, key);
		if (tutorial.missing || tutorial.error) return false;
		if (tutorial.patch) return true;
		const from = tutorial.startsFrom;
		if (!from || typeof from !== 'object' || typeof from.tutorial !== 'string') return false;
		if (from.exercise !== undefined && from.exercise !== null) return true;
		key = from.tutorial;
	}
	return false;
}

/**
 * Why the stamp of a tutorial page is not current, as a list (empty when it is): a run that passed at the pin with the
 * inputs as they are now, by a pin build or a patch build, and, at a release pin, by the release's package too, unless
 * the tutorial changes the engine (pipelines.md §6.4).
 */
export function stampProblems(settings, pageId) {
	const { relative, absolute } = tutorialPaths(settings, pageId);
	const read = readJson(absolute.stamp);
	if (read.missing) return [`a release has a current stamp of every tutorial, and ${relative.stamp} does not exist: run the tutorial with python -I tools/tutorials.py run`];
	if (read.error) return [`${relative.stamp} is not valid JSON: ${read.error}`];
	const stamp = read.data;
	if (!stamp || stamp.page !== pageId || !Array.isArray(stamp.runs)) return [`${relative.stamp} is not the stamp of ${pageId} ("page" and a list of "runs")`];
	const { commit, prerelease } = settings.engine;
	const reasons = [];
	const current = (kinds) => stamp.runs.some((run, position) => {
		if (!run || run.passed !== true || !kinds.includes(run.build?.kind)) return false;
		if (run.engineCommit !== commit) {
			reasons.push(`run ${position + 1} was at engine ${String(run.engineCommit).slice(0, 8)}, not at the pin ${commit.slice(0, 8)}`);
			return false;
		}
		const problem = inputsProblem(settings, run.inputs, relative.tutorial);
		if (problem) reasons.push(`run ${position + 1}: ${problem}`);
		return problem === null;
	});
	const problems = [];
	const because = () => (reasons.length ? ` (${[...new Set(reasons)].join('; ')})` : '');
	if (!current(['pin-build', 'patch-build'])) problems.push(`${relative.stamp} is not current: no run by a pin build or a patch build passed at the pin with the inputs as they are now${because()}; run the tutorial again`);
	reasons.length = 0;
	// A tutorial that changes the engine cannot run in a package, so it needs no package run (tools/booklib/tutorials.py,
	// stamp_problems).
	if (!prerelease && !changesEngine(settings, pageId) && !current(['package'])) problems.push(`${relative.stamp} is not current: at a release pin a run of the release's package passes too${because()}`);
	return problems;
}
