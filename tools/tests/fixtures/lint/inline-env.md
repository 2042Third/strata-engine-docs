No import.meta.env inside a <script is:inline> of the site's code (site.md, "The base path", rule 3): Vite does not
process inline scripts, so the expression would stay literal.

%%% pass core/time
A page.
%%% file src/components/Base.astro
---
const base = import.meta.env.BASE_URL;
---
<div data-base={base}></div>
<script>
	const other = import.meta.env.BASE_URL;
</script>
<script is:inline>
	const fromData = document.currentScript.dataset.base;
</script>

%%% fail core/time src/components/Base.astro:3
A page.
%%% file src/components/Base.astro
<div></div>
<script is:inline>
	const base = import.meta.env.BASE_URL;
</script>
