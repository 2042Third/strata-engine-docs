// The CI workflows against plan/site.md's "CI" section (and plan/critique/rulings-5.md R16, rulings-6.md R24, R25 and
// R27), the rules actionlint cannot know because they are the book's:
// - every action is pinned by its full commit SHA, and the default permission is `contents: read`; only the jobs
//   `report` and `release` of book.yml may write, and only contents;
// - book.yml runs on every push (branches and tags, with no filter), on pull requests and by hand, cancels superseded
//   runs except for tags, and has the jobs of site.md's table with their needs: release only on a book-v* tag, report
//   whatever the other jobs did and never for a pull request;
// - no repository variable, no secret beyond the workflow's own token, and no DOCS_SITE (a tagged build is a release
//   for site.json's address);
// - every step after the toolchain's bootstrap sources .tools/env.sh, and every check of book.yml runs through
//   tools/cistatus.py step, which writes its reason as an ::error annotation that the report job records;
// - the caches have the keys of site.md's table (Playwright's names the version package.json pins), and a job that
//   restores Playwright's browsers installs their system libraries on every run;
// - checkouts are one commit deep;
// - links.yml runs on Mondays at 06:00 UTC and by hand, checks the pages' web links with lychee, reports them in the
//   job summary, leaves out the engine's repository and fails when the repository holds more than 1 GB.
//
//     node scripts/workflows.mjs [--root <book folder>]

import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parse } from 'yaml';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_Book = '.github/workflows/book.yml';
export const c_Links = '.github/workflows/links.yml';
// owner/repository[/path]@<40 hex>: a tag or a branch can be moved under the workflow, a commit cannot.
const c_Pinned = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_./-]+@[0-9a-f]{40}$/;
// plan/site.md's table: each job and the jobs it needs.
export const c_Jobs = {
	lint: [],
	excerpts: [],
	build: ['lint'],
	'serve-test': ['build'],
	release: ['excerpts', 'serve-test'],
	report: ['lint', 'excerpts', 'build', 'serve-test', 'release'],
};
const c_Writers = new Set(['report', 'release']);
const c_Concurrency = { group: 'book-${{ github.ref }}', 'cancel-in-progress': "${{ !startsWith(github.ref, 'refs/tags/') }}" };
const c_PushFilters = ['branches', 'branches-ignore', 'tags', 'tags-ignore', 'paths', 'paths-ignore'];
// A command that checks something; in book.yml each runs through tools/cistatus.py step (rulings 5, R16).
const c_Check = new RegExp([
	String.raw`tools/(?:pages|lint|names|excerpts|sketches|figures|tutorials|reference|pin|notices|crawl|budgets|release|measure)\.py\b`,
	String.raw`plan/check_outline\.py`,
	String.raw`tools/servertest\.py (?:nginx|url|static)\b`,
	String.raw`\bunittest discover\b`,
	String.raw`\bnpm test\b`,
	String.raw`\bnpm run diagrams\b`,
	String.raw`\bnode scripts/`,
	String.raw`\bastro build\b`,
	String.raw`(?:^|[\s;&|(])(?:typos|markdownlint-cli2|actionlint)(?=\s|$)`,
].join('|'));
const c_EnvLine = /^\s*(?:\.|source) \.tools\/env\.sh\s*$/m;
const c_Bootstrap = /\btools\/bootstrap\.py\b/;

/** The cache keys of plan/site.md's table, by the cache's path; Playwright's names the version of package.json. */
export function expectedCacheKeys(playwrightVersion) {
	return {
		'.tools': "tools-${{ hashFiles('tools/toolchain.json') }}",
		'.tools/npm-cache': "npm-${{ hashFiles('package-lock.json') }}",
		'.cache/astro*': "astro-${{ hashFiles('package-lock.json', 'astro.config.mjs', 'ec.config.mjs', 'src/plugins/**', 'src/lib/**') }}",
		'.cache/images': "images-${{ hashFiles('src/assets/figures/**', 'src/lib/images.mjs') }}",
		'.tools/ms-playwright': `playwright-${playwrightVersion}-\${{ runner.os }}`,
		'engine/.git': 'engine-${{ steps.pin.outputs.commit }}',
	};
}

/** A run script's logical lines: a line ending with a backslash is joined to the next by one space; comments are left
 * out. */
export function logicalLines(script) {
	const lines = [];
	let parts = [];
	const finish = () => {
		const line = parts.filter(Boolean).join(' ');
		if (line && !line.startsWith('#')) lines.push(line);
		parts = [];
	};
	for (const line of String(script).split('\n')) {
		const text = line.trim();
		if (text.endsWith('\\')) {
			parts.push(text.slice(0, -1).trimEnd());
			continue;
		}
		parts.push(text);
		finish();
	}
	finish();
	return lines;
}

/** Every string of a parsed document (keys and values), with the path that leads to it; comments are not in it. */
function strings(node, where = '', found = []) {
	if (typeof node === 'string') found.push([where, node]);
	else if (Array.isArray(node)) node.forEach((item, index) => strings(item, `${where}[${index}]`, found));
	else if (node && typeof node === 'object') {
		for (const [key, value] of Object.entries(node)) {
			found.push([where, key]);
			strings(value, where ? `${where}.${key}` : key, found);
		}
	}
	return found;
}

/** A workflow's triggers as an object, whichever of GitHub's three forms `on` takes (a name, a list, a mapping). */
function triggersOf(document) {
	const on = document.on;
	if (typeof on === 'string') return { [on]: null };
	if (Array.isArray(on)) return Object.fromEntries(on.map((name) => [String(name), null]));
	return on && typeof on === 'object' ? on : {};
}

function stepName(job, step, index) {
	return `jobs.${job}, step ${index + 1} (${step.name ?? step.uses ?? 'unnamed'})`;
}

/** The rules both workflows follow: pinned actions, read by default, one-commit checkouts, env.sh after bootstrap. */
function commonProblems(file, document, writers) {
	const problems = [];
	const permissions = document.permissions;
	if (!permissions || typeof permissions !== 'object' || Object.keys(permissions).length !== 1 || permissions.contents !== 'read') {
		problems.push(`${file}: the default permission must be exactly "contents: read" (plan/site.md, "CI"), not ${JSON.stringify(permissions ?? null)}`);
	}
	for (const [job, body] of Object.entries(document.jobs ?? {}).map(([name, value]) => [name, value ?? {}])) {
		const own = body.permissions;
		if (typeof own === 'string') problems.push(`${file}: jobs.${job} sets the permissions "${own}"; name each one`);
		else if (own) {
			for (const [scope, level] of Object.entries(own)) {
				if (level === 'write' && !(scope === 'contents' && writers.has(job))) {
					const who = writers.size ? `only ${[...writers].join(' and ')} may write, and only contents` : 'no job of this workflow writes';
					problems.push(`${file}: jobs.${job} may not have "${scope}: write"; ${who} (plan/site.md, "CI")`);
				}
			}
		}
		const steps = body.steps ?? [];
		const bootstrap = steps.findIndex((step) => c_Bootstrap.test(step.run ?? ''));
		steps.forEach((step, index) => {
			if (step.uses !== undefined && !c_Pinned.test(step.uses)) {
				problems.push(`${file}: ${stepName(job, step, index)} uses ${step.uses}: pin the action by its full commit SHA (plan/site.md, "CI")`);
			}
			if (step.uses?.startsWith('actions/checkout@') && step.with?.['fetch-depth'] !== undefined && Number(step.with['fetch-depth']) !== 1) {
				problems.push(`${file}: ${stepName(job, step, index)} checks out ${step.with['fetch-depth']} commits deep; the checkout is one commit deep (plan/site.md, "CI")`);
			}
			if (step.run === undefined || bootstrap < 0 || index < bootstrap) return;
			const lines = logicalLines(step.run);
			const onlyBootstrap = index === bootstrap && lines.every((line) => c_Bootstrap.test(line));
			if (!onlyBootstrap && !c_EnvLine.test(step.run)) {
				problems.push(`${file}: ${stepName(job, step, index)} does not source .tools/env.sh; every step after the toolchain's bootstrap does (plan/site.md, "CI")`);
			}
		});
	}
	return problems;
}

/** What breaks the book's rules in book.yml's text; `playwrightVersion` is package.json's. */
export function bookProblems(text, { playwrightVersion, file = c_Book } = {}) {
	let document;
	try {
		document = parse(text);
	} catch (error) {
		return [`${file}: not YAML: ${error.message}`];
	}
	if (!document || typeof document !== 'object') return [`${file}: holds no workflow`];
	const problems = commonProblems(file, document, c_Writers);
	const on = triggersOf(document);
	const triggers = Object.keys(on).sort();
	if (triggers.join(',') !== 'pull_request,push,workflow_dispatch') {
		problems.push(`${file}: runs on ${triggers.join(', ') || 'nothing'}; it runs on push, pull_request and workflow_dispatch (plan/site.md, "CI")`);
	}
	for (const filter of c_PushFilters) {
		if (on.push && typeof on.push === 'object' && on.push[filter] !== undefined) {
			problems.push(`${file}: push is filtered by ${filter}; it runs on every branch and tag, main, ci/<name> and book-v* among them (rulings 6, R27)`);
		}
	}
	const concurrency = document.concurrency ?? {};
	for (const [key, value] of Object.entries(c_Concurrency)) {
		if (concurrency[key] !== value) problems.push(`${file}: concurrency.${key} is ${JSON.stringify(concurrency[key] ?? null)}, not ${JSON.stringify(value)}: superseded runs are cancelled, except for tags`);
	}
	const jobs = document.jobs ?? {};
	const names = Object.keys(jobs);
	for (const job of Object.keys(c_Jobs)) if (!names.includes(job)) problems.push(`${file}: has no job ${job} (plan/site.md, "CI")`);
	for (const job of names) if (!(job in c_Jobs)) problems.push(`${file}: the job ${job} is not one of plan/site.md's (${Object.keys(c_Jobs).join(', ')})`);
	for (const [job, needed] of Object.entries(c_Jobs)) {
		if (!jobs[job]) continue;
		const needs = [jobs[job].needs ?? []].flat();
		for (const other of needed) if (!needs.includes(other)) problems.push(`${file}: jobs.${job} does not need ${other}`);
		if (!needed.length && needs.length) problems.push(`${file}: jobs.${job} needs ${needs.join(', ')}; it needs no other job`);
	}
	const releaseIf = String(jobs.release?.if ?? '');
	if (jobs.release && !releaseIf.includes("'refs/tags/book-v'")) problems.push(`${file}: jobs.release runs only on a book-v* tag; its if is ${JSON.stringify(releaseIf)}`);
	const reportIf = String(jobs.report?.if ?? '');
	if (jobs.report && !(reportIf.includes('always()') && /github\.event_name != 'pull_request'/.test(reportIf))) {
		problems.push(`${file}: jobs.report runs whatever the other jobs did and never for a pull request; its if is ${JSON.stringify(reportIf)}`);
	}
	for (const [where, value] of strings(document)) {
		if (/\bvars\./.test(value)) problems.push(`${file}: ${where || 'the top'} reads a repository variable (${value.trim().slice(0, 60)}); none is needed (rulings 6, R24)`);
		for (const match of value.matchAll(/\bsecrets\.(\w+)/g)) {
			if (match[1] !== 'GITHUB_TOKEN') problems.push(`${file}: ${where || 'the top'} reads the secret ${match[1]}; no secret is needed beyond the workflow's own token (plan/site.md, "CI")`);
		}
		if (/\bDOCS_SITE\b/.test(value)) problems.push(`${file}: ${where || 'the top'} names DOCS_SITE; a tagged build is a release for site.json's address (rulings 6, R24)`);
	}
	const keys = expectedCacheKeys(playwrightVersion);
	for (const [job, body] of Object.entries(jobs).map(([name, value]) => [name, value ?? {}])) {
		const steps = body.steps ?? [];
		let restoresBrowsers = false;
		steps.forEach((step, index) => {
			if (step.uses?.startsWith('actions/cache@')) {
				const paths = String(step.with?.path ?? '').split('\n').map((line) => line.trim()).filter(Boolean);
				const own = paths.filter((line) => !line.startsWith('!'));
				const expected = own.length === 1 ? keys[own[0]] : undefined;
				if (expected === undefined) problems.push(`${file}: ${stepName(job, step, index)} caches ${own.join(', ')}, which is not a cache of plan/site.md's table`);
				else if (step.with.key !== expected) problems.push(`${file}: ${stepName(job, step, index)} has the key ${step.with.key}, not ${expected} (plan/site.md, "Caches")`);
				if (own[0] === '.tools' && !paths.includes('!.tools/ms-playwright')) problems.push(`${file}: ${stepName(job, step, index)} caches the toolchain with Playwright's browsers, which have their own cache`);
				if (own[0] === '.tools/ms-playwright') restoresBrowsers = true;
			}
			if (step.run === undefined) return;
			for (const line of logicalLines(step.run)) {
				if (c_Check.test(line) && !line.includes('tools/cistatus.py step ')) {
					problems.push(`${file}: ${stepName(job, step, index)} runs "${line.slice(0, 80)}" without tools/cistatus.py step, so a failure leaves no ::error annotation (rulings 5, R16)`);
				}
			}
		});
		if (restoresBrowsers && !steps.some((step) => /\bplaywright install-deps\b/.test(step.run ?? ''))) {
			problems.push(`${file}: jobs.${job} restores Playwright's browsers but does not install their system libraries; they are installed on every run (plan/site.md, "Caches")`);
		}
	}
	return problems;
}

/** What breaks the book's rules in links.yml's text. */
export function linksProblems(text, { file = c_Links } = {}) {
	let document;
	try {
		document = parse(text);
	} catch (error) {
		return [`${file}: not YAML: ${error.message}`];
	}
	if (!document || typeof document !== 'object') return [`${file}: holds no workflow`];
	const problems = commonProblems(file, document, new Set());
	const on = triggersOf(document);
	const triggers = Object.keys(on).sort();
	const crons = [on.schedule ?? []].flat().map((entry) => entry?.cron);
	if (triggers.join(',') !== 'schedule,workflow_dispatch' || crons.join(',') !== '0 6 * * 1') {
		problems.push(`${file}: runs on ${triggers.join(', ') || 'nothing'} (cron ${crons.join(', ') || 'none'}); it runs on Mondays at 06:00 UTC ("0 6 * * 1") and by hand (plan/site.md, "CI")`);
	}
	const runs = Object.values(document.jobs ?? {}).flatMap((job) => (job.steps ?? []).map((step) => String(step.run ?? '')));
	const lychee = runs.find((run) => /(?:^|\s)lychee\s/m.test(run));
	if (!lychee) problems.push(`${file}: no step runs lychee on the pages' links`);
	else {
		if (!lychee.includes("'src/content/docs/**/*.md'")) problems.push(`${file}: lychee does not read 'src/content/docs/**/*.md'`);
		if (!/--exclude "\^\$\{repository\}"/.test(lychee) || !lychee.includes('engine.pin')) problems.push(`${file}: lychee does not leave out the engine's repository of engine.pin; tools/excerpts.py check reads those links with git`);
		if (!lychee.includes('$GITHUB_STEP_SUMMARY')) problems.push(`${file}: lychee's findings are not reported in the job summary`);
		if (!/-ne 2\b/.test(lychee)) problems.push(`${file}: a failing link fails the job; lychee's findings are only reported, because other sites fail now and then`);
	}
	const size = runs.find((run) => run.includes('gh api "repos/$GITHUB_REPOSITORY" --jq .size'));
	if (!size) problems.push(`${file}: no step reads the repository's size with gh api "repos/$GITHUB_REPOSITORY" --jq .size`);
	else if (!/-gt 1048576\b/.test(size) || !/exit 1/.test(size)) problems.push(`${file}: the repository's size does not fail the job above 1 GB (1,048,576 KB)`);
	return problems;
}

/** Both workflows of a book folder, with package.json's Playwright version. */
export function workflowProblems(root = c_Root) {
	const manifest = JSON.parse(readFileSync(path.join(root, 'package.json'), 'utf8'));
	const playwrightVersion = manifest.dependencies?.playwright ?? manifest.devDependencies?.playwright;
	return [
		...bookProblems(readFileSync(path.join(root, c_Book), 'utf8'), { playwrightVersion }),
		...linksProblems(readFileSync(path.join(root, c_Links), 'utf8')),
	];
}

async function main(argv) {
	const at = argv.indexOf('--root');
	const root = at >= 0 ? path.resolve(argv[at + 1]) : c_Root;
	const problems = workflowProblems(root);
	for (const problem of problems) console.log(problem);
	console.log(`workflows: 2 files, ${problems.length} problem${problems.length === 1 ? '' : 's'}`);
	return problems.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) process.exitCode = await main(process.argv.slice(2));
