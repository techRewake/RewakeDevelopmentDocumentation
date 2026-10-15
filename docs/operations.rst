Operations
==========

Configuration
--------------

Copy ``.env.example`` to ``.env``. See :doc:`development` for how to obtain
each credential locally.

- **Tokens** (:doc:`authentication`): ``ADMIN_TOKEN``, ``HELLOPRO_TOKEN``,
  ``MACHINIO_TOKEN``, ``APP_TOKEN``, ``AIRTABLE_AUTOMATION_TOKEN`` (Airtable
  automations -> ``/internal/scripts/*`` only).
- **Airtable**: ``AIRTABLE_TOKEN``, ``AIRTABLE_BASE_ID`` -- production, or
  the dev base copied from it (see :doc:`development`).
- **Google**: ``GOOGLE_APPLICATION_CREDENTIALS`` (Gmail service account:
  bon de commande drafts and alert emails; set by ``docker-compose.yml`` to
  the mounted ``/home/rewake/credentials/rewake-service-account.json``),
  ``ALERT_EMAIL_SENDER``/``ALERT_EMAIL_RECIPIENTS`` (``create_product_shopify``
  failure alerts; defaults in ``api/constants.py``).
- **Catalog / AI**: ``OCR_URL`` (label OCR sidecar, default
  ``http://ocr:8000``), ``ANTHROPIC_API_KEY`` and/or ``OPENROUTER_API_KEY``
  (a provider without its key is skipped; neither set = AI reported as not
  configured, AI features answer 503 ``not_configured``), ``AI_DB_PATH`` (AI
  settings/usage SQLite, default ``/home/rewake/DB/ai.sqlite``).
- **Logging**: ``LOG_LEVEL`` (default ``INFO``), ``LOG_FORMAT``
  (``json``/``console``, default ``json``).
- **Scripts** (``api/scripts/``, queued via ``api/tasks.py`` -- see
  :doc:`architecture`): ``REDIS_URL`` for the Celery broker/backend
  (defaults to ``redis://localhost:6379/0``, ``redis://redis:6379/0`` under
  docker compose). ``VERIFICATION_SHOPIFY_DIR`` still exists too, but only
  to locate the legacy ``GET /internal/backups/`` directory (see
  :doc:`routes`) -- the ``verification_shopify`` script itself has been
  removed. ``update_product`` no longer shells out to a sibling project
  (``UV_BIN``/``UPDATE_PRODUCT_DIR``/``UPDATE_PRODUCT_HOST_DIR`` are gone,
  along with the bind mount they configured) -- see :doc:`update_product`.
- **Scheduled scripts**: ``SHOPIFY_CATALOG_RECONCILIATION_INTERVAL_SECONDS``
  (default ``3600``), ``AIRTABLE_CATALOG_STATS_HOUR``/``_MINUTE`` (default
  ``20``/``42``, interpreted in ``celery_app``'s ``Europe/Paris`` timezone)
  -- see the ``beat`` service below.
- **Shopify**: ``SHOPIFY_SHOP_DOMAIN``, ``SHOPIFY_CLIENT_ID``,
  ``SHOPIFY_CLIENT_SECRET`` (exchanged at runtime for a self-renewing token,
  cached in Redis -- see :doc:`development`), ``SHOPIFY_API_VERSION``,
  ``SHOPIFY_LOCATION_ID``, ``SHOPIFY_PDF_METAFIELD_NAMESPACE``/``_KEY`` and
  ``SHOPIFY_PDF_SOURCE_METAFIELD_KEY`` (optional, defaults in
  ``api/constants.py``) -- used by ``shopify_catalog_reconciliation``,
  ``create_product_shopify``, and ``update_product``.
- **Deploy**: ``TAG`` (default ``latest``) -- which
  ``ghcr.io/rewake-fr/api``/``api-ocr`` build ``docker-compose.yml`` and
  ``scripts/deploy/deploy.sh`` run.

Deployment
----------

Two ways to run this, and only one of them is meant for the real server:

**Building from source** (local dev, or if you'd rather not use the image):

.. code-block:: sh

   git pull
   docker compose up -d --build

**From the published image** (the real deploy, run in ``~/API`` on the
production server -- no build there at all):

.. code-block:: sh

   scripts/deploy/deploy.sh          # deploy "latest"
   scripts/deploy/deploy.sh sha-abc1234  # pin to, or roll back to, one build

``.github/workflows/ci.yml``'s ``image`` job builds and pushes
``ghcr.io/rewake-fr/api`` and the OCR sidecar ``ghcr.io/rewake-fr/api-ocr``
(from ``ocr/``) on every push to ``main`` (never on a PR, and
never from any other branch), tagged both ``latest`` and ``sha-<short
hash>`` -- the latter never moves, so it's always safe to pin or roll back
to. Since the source repo is private, so is the image; the server needs a
one-time ``docker login ghcr.io`` (a personal access token with
``read:packages``, or a fine-grained token scoped to this repo, as the
password) before its first pull -- never done by the deploy script itself,
and no credential is ever read or stored by it. ``deploy.sh`` runs
``docker compose pull``, then ``docker compose up -d --remove-orphans``, and
waits for ``http://localhost:3002/health/`` (15 tries, 2 s apart), printing
the ``api`` logs if it never answers. ``docker-compose.yml``'s services
declare both ``image:`` (what a real deploy pulls) and ``build:`` (what
local dev still uses via ``--build``), so either workflow works from the
same file.

Release notes
~~~~~~~~~~~~~

Once the image is pushed, the ``release`` job publishes a GitHub Release
tagged with the same ``sha-<short hash>`` (so each release is exactly one
deployable image, and its page shows the ``deploy.sh`` command for it). Its
notes are rendered by ``scripts/release/release_notes.py`` from the commits
since the previous ``sha-*`` release, grouped by Conventional Commits type
(``feat``, ``fix``, ``docs``, ``chore``...; anything unprefixed goes under
"Autres changements"). A commit that requires action at deploy time -- a
removed or renamed environment variable, a new Shopify scope -- should say
so in a ``BREAKING CHANGE:`` footer (or a ``type!:`` subject): it's then
listed first, under "Changements cassants". Releases run one at a time, in
push order; re-running a workflow never overwrites an existing release.

``docker-compose.yml`` runs five services: ``api`` (port 3002), ``worker``
(``celery -A api.celery_app worker``) and ``beat`` (``celery -A
api.celery_app beat`` -- required once any registered script has a real
``schedule``, currently ``shopify_catalog_reconciliation`` and
``airtable_catalog_stats``; its schedule state lives in
``/home/rewake/logs/celerybeat-schedule``), all three from the API image and
bind-mounting ``/home/rewake/DB`` and ``/home/rewake/logs``; ``redis``
(``redis:7-alpine``, ``redis-data`` volume); and ``ocr`` (the label OCR
sidecar, internal only on port 8000). The
container command uses ``uv run --no-sync``, so nothing tries to reach the
network at startup -- the image is built once with ``uv sync --frozen
--no-dev`` and run exactly as built.

Logging
-------

``structlog`` renders JSON (or ``console`` for local readability) to stdout
and to a rotating file (``LOG_FILE`` in ``api/constants.py``, currently
``/home/rewake/logs/api.log``); falls back to stdout-only if the log
directory isn't writable. A request-id middleware
(``api/utils/logger.py``) binds ``request_id``/``method``/``path``/
``client_ip`` to every log line for a request and adds ``X-Request-ID`` to
the response.

CI/CD
-----

``.github/workflows/ci.yml``'s ``quality`` job runs on every pull request
and every push to ``main``: ``uv run ruff check .``, ``uv run mypy api
scripts``, and a Sphinx build with ``-W`` (any warning fails it). **Tests are
deliberately not run in CI** -- many hit the real Airtable API (no mock
layer yet, see :doc:`development`) and need six token/credential secrets to
even pass, which turned out to be more fragile than valuable as a required
CI gate; run ``make test`` (or ``uv run pytest``) locally with a real
``.env`` instead. See :doc:`development` for other known gaps CI surfaces.
Its ``image`` job (build+push to GHCR) only
runs after ``quality`` passes, and only on a push to ``main``; ``release``
follows ``image`` -- see "Deployment" above.
