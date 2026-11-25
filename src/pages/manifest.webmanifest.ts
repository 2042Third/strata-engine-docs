// The web manifest, under the base path like everything else (start URL, scope and icon: src/lib/manifest.mjs).
import type { APIRoute } from 'astro';
import { webManifest } from '../lib/manifest.mjs';

export const GET: APIRoute = () => {
	const base = import.meta.env.BASE_URL.replace(/\/$/, '');
	return new Response(JSON.stringify(webManifest(base), null, '\t'), { headers: { 'Content-Type': 'application/manifest+json' } });
};
