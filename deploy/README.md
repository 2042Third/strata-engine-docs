# Deploying the book

The Strata Engine Book is a static site: plain files under one path prefix, `/strata-engine-docs`. It is served at
`https://pdm.pw/strata-engine-docs/` by nginx, beside the site that `https://pdm.pw/` already serves. Nothing is
loaded from another host, and nothing runs on the server but nginx.

There are two ways to serve it, both tested with nginx 1.20.1 (what `https://pdm.pw` runs) and 1.30.6:

- **Copied files** (section 2, recommended for `https://pdm.pw`): the host's own nginx serves the files. No other
  program runs.
- **The container** (section 3): nginx in a container serves the files, and the host's nginx forwards the prefix to
  it.

Every command below runs on the server, in a POSIX shell, with the rights to write `/etc/nginx` and `/srv/www` (put
`sudo` in front where your account needs it). `<tag>` is the release's tag, such as `book-v0.8.0-r1`, the first
release of the book of Strata 0.8.0.

## 1. What a release holds

A release is a GitHub Release of the book's repository, tagged `book-v<engine release>-r<n>`. Download its assets
from the release's page; while the repository is private, sign in, or run `gh release download <tag>` with your own
login. A build of CI that is not a release has the tag `main-<first 8 hex digits of the commit>` and the same assets,
as an artifact of its run.

| Asset | Holds |
| --- | --- |
| `strata-engine-docs-<tag>.tar.gz` | one folder, `strata-engine-docs/`: the built site, with a `.gz` beside every text file of 1 KB or more |
| `strata-engine-docs-deploy-<tag>.tar.gz` | one folder, `deploy/`: this file, the nginx files, the Dockerfiles, the copy script, and the two files written for this build: `nginx-csp.conf` (its Content Security Policy) and `nginx-redirects.conf` (its moved pages) |
| `SHA256SUMS` | the SHA-256 of both tarballs |
| `strata-engine-docs-originals-<tag>.tar` | the pictures' PNG originals, attached later; a deployment does not need it |

Check the downloads and unpack both tarballs into one new, empty folder:

```sh
cd <the folder that holds the three downloaded files>
sha256sum -c SHA256SUMS                     # both lines must say OK
rm -rf /tmp/book-new && mkdir -p /tmp/book-new
tar -xzf strata-engine-docs-<tag>.tar.gz -C /tmp/book-new
tar -xzf strata-engine-docs-deploy-<tag>.tar.gz -C /tmp/book-new
ls /tmp/book-new                            # deploy  strata-engine-docs
```

## 2. Copied files into the host's nginx

This is the way for a host that already serves a site with nginx, as `https://pdm.pw` does. The book needs nginx
1.20.1 or later. A current nginx is the safer host (1.30.6 fixes CVE-2026-15176, which concerns `alias` after
`rewrite`; the book uses `root`, never `alias`), but the book does not wait for an upgrade.

1. **Check that nginx can send the `.gz` files.** Before the first `nginx -t`:

   ```sh
   nginx -V 2>&1 | tr ' ' '\n' | grep -x -- --with-http_gzip_static_module
   ```

   When this prints nothing, nginx lacks the module, and `gzip_static` would be an unknown directive: delete the line
   `gzip_static on;` from `/etc/nginx/snippets/strata-engine-docs.conf` after step 2. nginx then compresses while it
   serves (`gzip on` stays), and the `.gz` files lie unused.

2. **Put the server files in place.**

   ```sh
   mkdir -p /etc/nginx/conf.d /etc/nginx/snippets /srv/www
   cp /tmp/book-new/deploy/nginx-http.conf /etc/nginx/conf.d/strata-engine-docs-http.conf
   cp /tmp/book-new/deploy/nginx.conf /etc/nginx/snippets/strata-engine-docs.conf
   cp /tmp/book-new/deploy/nginx-csp.conf /etc/nginx/snippets/strata-engine-docs-csp.conf
   cp /tmp/book-new/deploy/nginx-redirects.conf /etc/nginx/snippets/strata-engine-docs-redirects.conf
   ```

   `strata-engine-docs-http.conf` belongs to nginx's `http` context: it maps each kind of file to its
   `Cache-Control`. Most installations include every `/etc/nginx/conf.d/*.conf` there; see whether yours does:

   ```sh
   grep -n 'include /etc/nginx/conf.d/\*.conf;' /etc/nginx/nginx.conf
   ```

   When that prints nothing, paste this line into the `http { … }` block of `/etc/nginx/nginx.conf`, once (twice would
   define the map twice, which `nginx -t` refuses):

   ```nginx
   include /etc/nginx/conf.d/strata-engine-docs-http.conf;
   ```

   Then paste this line into the `server { … }` block of the site that answers `https://pdm.pw/` (the block with
   `listen 443` and `server_name pdm.pw`), beside its own `location` blocks:

   ```nginx
   include /etc/nginx/snippets/strata-engine-docs.conf;
   ```

   That file holds the book's `location ^~ /strata-engine-docs/` and the redirect of `/strata-engine-docs` to
   `/strata-engine-docs/`. The `^~` keeps the host's own regular-expression locations (such as
   `location ~* \.(css|js)$ { expires 30d; }`) from taking the book's files. Its `root /srv/www;` names the folder that
   holds `strata-engine-docs/`; to keep the book elsewhere, change that one line (and the paths below), never into
   `alias`.

3. **The host's own headers.** The book's `location` sends the book's headers (`Content-Security-Policy`,
   `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Cache-Control`), each with `always`, so that its
   404 page has them too. nginx then drops every `add_header` of the server block inside that location: the host's
   `X-Frame-Options` and `X-Content-Type-Options` do not arrive twice. The book sends no `Strict-Transport-Security`,
   because that header binds the whole host and is the host's decision. A header of the host that must also reach the
   book's pages goes into `/etc/nginx/snippets/strata-engine-docs-host-headers.conf`, with `always`, for example:

   ```nginx
   add_header Strict-Transport-Security "max-age=31536000" always;
   ```

   Without such a file nothing is added: the book's location includes `strata-engine-docs-host-headers*.conf`, a name
   that may match no file.

4. **Check and reload nginx.**

   ```sh
   nginx -t && nginx -s reload
   ```

5. **Copy the site.** `rsync` must be installed (Debian and Ubuntu: `apt install rsync`).

   ```sh
   /tmp/book-new/deploy/deploy-files.sh /tmp/book-new/strata-engine-docs /srv/www/strata-engine-docs
   ```

   The script copies in two passes. The first adds the new files and deletes nothing, so a page a reader opened
   before the copy still finds its files, which are named by their hash. The second deletes what the new build no
   longer has, but never archived versions of the book (`v0.8/` and the like) or `versions.json`. Each file is
   written beside the old one and renamed over it, so a reader gets the old file or the new one, never half of one.

6. **Look.** `curl -sI https://pdm.pw/strata-engine-docs/` answers `HTTP/1.1 200 OK`, and the book opens in a browser.
   Section 5 says how to check the whole deployment.

A new release repeats the steps from section 1: the server files change with every build (`nginx-csp.conf` holds the
hashes of the build's inline scripts), so copy all four again, reload, and copy the site.

## 3. The container behind the host's nginx

For an owner who prefers to keep the book's server apart: the container runs nginx 1.30.6 and serves only the book, on
`127.0.0.1:8080`; the host's nginx forwards `/strata-engine-docs/` to it and does nothing else for the book, which
nginx 1.20.1 does. The server needs Docker.

1. **Build the image** in the folder that holds the unpacked release (section 1):

   ```sh
   cd /tmp/book-new
   docker build -f deploy/Dockerfile -t strata-engine-docs:<tag> .
   ```

   `deploy/Dockerfile` builds nothing: it copies nginx's files and the built site into
   `nginxinc/nginx-unprivileged:1.30.6-alpine` and checks the configuration with `nginx -t`. The image holds nothing
   else.

2. **Run it** read-only, as an unprivileged user, reachable only from the server itself:

   ```sh
   docker run -d --name strata-engine-docs --restart unless-stopped --read-only --tmpfs /tmp \
     --tmpfs /var/cache/nginx -p 127.0.0.1:8080:8080 strata-engine-docs:<tag>
   curl -sI http://127.0.0.1:8080/strata-engine-docs/     # HTTP/1.1 200 OK
   ```

3. **Forward the prefix.** Copy the proxy's lines and include them in the `server { … }` block of the site that answers
   `https://pdm.pw/`:

   ```sh
   mkdir -p /etc/nginx/snippets
   cp /tmp/book-new/deploy/nginx-proxy.conf /etc/nginx/snippets/strata-engine-docs-proxy.conf
   ```

   ```nginx
   include /etc/nginx/snippets/strata-engine-docs-proxy.conf;
   ```

   Then `nginx -t && nginx -s reload`. Nothing of `nginx-http.conf`, `nginx.conf` or the generated files goes into the
   host's nginx: the container holds them.

   What the pasted lines do: `proxy_pass http://127.0.0.1:8080;` has no path after the port, so the prefix reaches the
   container unchanged. `proxy_http_version 1.1;` lets the container compress: nginx before 1.29.7 forwards over
   HTTP/1.0 unless told otherwise, and nginx compresses nothing for HTTP/1.0. The container sends the book's headers.
   A `location` without an `add_header` would inherit the server block's, so the host's `X-Frame-Options` and
   `X-Content-Type-Options` would arrive a second time beside the container's; the line
   `add_header X-Strata-Docs "" always;` ends that inheritance and sends nothing, because nginx never sends a header
   whose value is empty. `expires off;` keeps a host's `expires` from adding a second `Cache-Control`. A header of the
   host that must also reach the book's pages goes into `/etc/nginx/snippets/strata-engine-docs-host-headers.conf`, as
   in section 2, step 3.

4. **A new release:** build its image (step 1), then replace the container:

   ```sh
   docker rm -f strata-engine-docs
   docker run -d --name strata-engine-docs --restart unless-stopped --read-only --tmpfs /tmp \
     --tmpfs /var/cache/nginx -p 127.0.0.1:8080:8080 strata-engine-docs:<new tag>
   ```

**Building on the server.** `deploy/Dockerfile.build` builds the site from a clone of the repository and then serves
it like `deploy/Dockerfile`: `docker build -f deploy/Dockerfile.build -t strata-engine-docs:<commit> .` in the clone.
It needs about 4 GB of free memory and up to 30 minutes on four cores when no cache is there yet. Without build
arguments it builds for the place `site.json` names; `--build-arg DOCS_RELEASE=1` makes a release build, which refuses
draft pages and placeholders. Run the image as in step 2.

## 4. robots.txt

The book has no `robots.txt` of its own: crawlers read only the host's, `https://pdm.pw/robots.txt`. Add this line to
that file, beside the host's own `Sitemap` line:

```text
Sitemap: https://pdm.pw/strata-engine-docs/sitemap-index.xml
```

A Hugo site copies `static/robots.txt` as it is; when its configuration sets `enableRobotsTXT = true`, it renders the
template `layouts/robots.txt` instead, or, when the site has no such file, Hugo's own, which is the one line
`User-agent: *` (then create `layouts/robots.txt` with that line). Put the `Sitemap` line into the file the site uses,
and build and deploy the Hugo site again.

## 5. Accepting a deployment

Two checks read the live address and change nothing. They run on any machine with Python 3 and a clone of the book's
repository (the tools use the standard library only), with the release's three files in a folder `release/<tag>/` and
the site unpacked as in section 1:

```sh
python tools/crawl.py --url https://pdm.pw/strata-engine-docs/ --dist /tmp/book-new/strata-engine-docs
python tools/servertest.py url --url https://pdm.pw/strata-engine-docs/ --release release/<tag>
```

Both must end with 0 problems. The crawl follows every link, picture, script and style sheet of the book and fails
on anything that answers other than 200, leaves the prefix or loads from another host. The server test checks every
header: the redirects, the cache of each kind of file, the types, the compression, the 404 page, the moved pages, and
the book's four headers on every answer under the prefix, each exactly once and with the release's policy. With a
host-headers file, name its header: `--host-header "Strict-Transport-Security: max-age=31536000"`. For the container,
add `--container`.

## 6. Moving the book

The address is written in one file, `site.json` in the repository's root (`origin` and `base`). To move the book:

1. Change `site.json`, tag a release, and deploy it at the new place (sections 1 to 5). When the base changes too, the
   files of `deploy/` are written for the new base in the same commit (a test of the repository says how).
2. Let the old host answer every path under the old prefix with a 301 to the same path at the new address. In the old
   server block, in place of the book's include:

   ```nginx
   location = /strata-engine-docs {
   	return 301 https://<new host>/strata-engine-docs/;
   }
   location ^~ /strata-engine-docs/ {
   	return 301 https://<new host>$request_uri;
   }
   ```

   When the base changes as well, the first block returns `301 https://<new host><new base>/`, and the second block's
   `return` line becomes `rewrite ^/strata-engine-docs/(.*)$ https://<new host><new base>/$1 permanent;`.

Canonical links and the sitemap follow from the rebuild. What a reader's browser kept for the old origin (the theme,
the chosen track) is lost.

A build for another place that does not move the book (a copy elsewhere, a test) takes `DOCS_BASE` and `DOCS_SITE`
for that one build, then `python tools/release.py assemble --tag <tag> --base <base>`, which writes every file of
`deploy/` for that base and names the site's folder after it (`docs/strata/`, or `site/` for the root of a host).

## 7. Reading offline

Unpack the site tarball, then serve the folder that holds `strata-engine-docs/`:

```sh
mkdir -p ~/book && tar -xzf strata-engine-docs-<tag>.tar.gz -C ~/book
cd ~/book && python3 -m http.server 8000
```

and open `http://localhost:8000/strata-engine-docs/`. Search works and nothing reaches the network. Opening the files
directly (`file://`) does not work: every URL starts with the prefix, and the search fetches its files.
