// Starts the staged site's server (tools/crawl.py --serve-only) for the browser checks, on a free port, and stops it
// afterwards. With --url the checks use a server that already runs (the copied files in nginx, the container).
//
// Run directly (npm run preview), it serves the built site for a person's browser, with search, which `astro dev` does
// not run (plan/site.md, "Search"), until Ctrl+C:
//
//     node scripts/serve.mjs [--port 4321] [--root <book folder>]      (PYTHON names Python where it is not on the PATH)

import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const c_Root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const c_PreviewPort = '4321';

/** The Python program the checks start: PYTHON, or the usual name of the platform. */
export function pythonProgram(env = process.env, platform = process.platform) {
	return env.PYTHON ?? (platform === 'win32' ? 'python' : 'python3');
}

/** The command of `npm run preview`: `{ program, args }`, tools/crawl.py staging dist/ and serving it on --port. */
export function previewCommand(argv, { env = process.env, platform = process.platform } = {}) {
	const option = (name, fallback) => {
		const index = argv.indexOf(name);
		return index >= 0 ? argv[index + 1] : fallback;
	};
	const root = path.resolve(option('--root', c_Root));
	return { program: pythonProgram(env, platform), args: ['-I', path.join(c_Root, 'tools', 'crawl.py'), '--serve-only', '--root', root, '--port', option('--port', c_PreviewPort)] };
}

function freePort() {
	return new Promise((resolve, reject) => {
		const server = createServer();
		server.unref();
		server.on('error', reject);
		server.listen(0, '127.0.0.1', () => {
			const { port } = server.address();
			server.close(() => resolve(port));
		});
	});
}

async function waitFor(url, seconds) {
	const deadline = Date.now() + seconds * 1000;
	while (Date.now() < deadline) {
		try {
			const response = await fetch(url);
			if (response.ok) return;
		} catch {
			// Not listening yet.
		}
		await new Promise((resolve) => setTimeout(resolve, 200));
	}
	throw new Error(`the staged site did not answer at ${url} within ${seconds} s`);
}

/** `{ url, stop }`: the base URL of the site (ending with "/") and a function that stops the server if this started it. */
export async function serveSite({ argv = process.argv, base = process.env.DOCS_BASE ?? '/strata-engine-docs' } = {}) {
	const index = argv.indexOf('--url');
	if (index >= 0) {
		const url = argv[index + 1].endsWith('/') ? argv[index + 1] : `${argv[index + 1]}/`;
		return { url, stop: async () => {} };
	}
	const rootIndex = argv.indexOf('--root');
	const root = rootIndex >= 0 ? path.resolve(argv[rootIndex + 1]) : c_Root;
	const port = await freePort();
	const child = spawn(pythonProgram(), ['-I', path.join(c_Root, 'tools', 'crawl.py'), '--serve-only', '--root', root, '--port', String(port)], { stdio: ['ignore', 'ignore', 'inherit'] });
	const normalized = base === '/' ? '' : base.replace(/\/$/, '');
	const url = `http://127.0.0.1:${port}${normalized}/`;
	try {
		await waitFor(url, 60);
	} catch (error) {
		child.kill();
		throw error;
	}
	return {
		url,
		stop: () => new Promise((resolve) => {
			child.once('exit', resolve);
			child.kill();
		}),
	};
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
	const { program, args } = previewCommand(process.argv.slice(2));
	const child = spawn(program, args, { stdio: 'inherit' });
	child.on('error', (error) => {
		console.error(`preview: ${program} did not start (${error.message}); name Python in PYTHON`);
		process.exitCode = 2;
	});
	child.on('exit', (code) => {
		process.exitCode ??= code ?? 0;
	});
	// The server goes when this script is stopped, whoever stops it.
	for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill());
}
