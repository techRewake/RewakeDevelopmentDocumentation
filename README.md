# Rewake Development Documentation

This repository owns the Sphinx sources for Rewake's development documentation.
The `main` branch contains the sources and translation catalogs. GitHub Actions
builds English and French sites on every push to `main` and publishes the
generated static site to the `gh-pages` branch.

## Build locally

```sh
make install
make
make serve
```

`make install` creates `.venv` and installs the documentation dependencies. The
Makefile uses that environment automatically, so activation is optional. If you
want to activate it for other commands, run `. .venv/bin/activate`.

The language chooser and builds are written to `_build/site/`, with pages at
`_build/site/en/` and `_build/site/fr/`. `make serve` builds the site and starts
Python's built-in HTTP server in the background at http://localhost:8000; its PID and log are
stored in `_build/http-server.pid` and `_build/http-server.log`. Python's
`http.server` is part of the standard library and needs no extra requirement. Run
`make stop` to stop the server; `fg` cannot attach to a background process
started by `make`.

## Update translations

```sh
make docs-catalogs
```

Edit the `msgstr` values under `docs/locale/en/` and `docs/locale/fr/`,
preserving Sphinx markup, references, code, and endpoint names. Untranslated
text falls back to the source language until its catalog entry is translated.

The source set still contains untranslated content in both directions; the
catalogs are being completed incrementally.
