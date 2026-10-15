.DEFAULT_GOAL := help

.PHONY: help install setup docs serve stop docs-gettext docs-catalogs clean

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

help:
	@echo "make install       Create .venv and install documentation dependencies"
	@echo "make setup         Alias for install"
	@echo "make docs          Build the English and French sites"
	@echo "make serve         Build the sites and serve them with Python at http://localhost:8000"
	@echo "make stop          Stop the background documentation server"
	@echo "make docs-gettext  Extract translatable strings"
	@echo "make docs-catalogs Update English and French translation catalogs"
	@echo "make clean         Remove generated build files"

install setup:
	python3 -m venv .venv
	.venv/bin/python -m pip install -r requirements-docs.txt

docs:
	$(PYTHON) -m sphinx -E -b html -d _build/doctrees/en -D language=en docs _build/site/en
	$(PYTHON) -m sphinx -E -b html -d _build/doctrees/fr -D language=fr docs _build/site/fr
	cp docs/site-index.html _build/site/index.html
	touch _build/site/.nojekyll

serve: docs
	@mkdir -p _build
	@nohup $(PYTHON) -m http.server 8000 --bind 127.0.0.1 --directory _build/site > _build/http-server.log 2>&1 < /dev/null & echo $$! > _build/http-server.pid
	@sleep 1
	@if kill -0 "$$(cat _build/http-server.pid)" 2>/dev/null; then echo "Serving _build/site with Python at http://localhost:8000 (PID $$(cat _build/http-server.pid))"; else echo "Python HTTP server failed to start; see _build/http-server.log"; rm -f _build/http-server.pid; exit 1; fi

stop:
	@if [ -f _build/http-server.pid ]; then \
		pid=$$(cat _build/http-server.pid); \
		if kill -0 "$$pid" 2>/dev/null; then kill "$$pid" && echo "Stopped documentation server (PID $$pid)"; \
		else echo "Documentation server is not running"; fi; \
		rm -f _build/http-server.pid; \
	else echo "No documentation server PID file found"; fi

docs-gettext:
	$(PYTHON) -m sphinx -E -b gettext -d _build/doctrees/gettext docs _build/gettext

docs-catalogs: docs-gettext
	sphinx-intl update -d docs/locale -p _build/gettext -l en -l fr -j 1

clean:
	rm -rf _build
