Translations and publishing
============================

The documentation is published as two static Sphinx builds under ``/en/``
and ``/fr/`` in the public
`RewakeDevelopmentDocumentation repository <https://github.com/techRewake/RewakeDevelopmentDocumentation>`_.
The root page links to both languages. The generated site includes HTML and
the assets Sphinx needs to render it.

Translations use Sphinx gettext catalogs in ``docs/locale/<language>/``.
The source pages currently mix English and French. Each language catalog
translates pages written in the other language; untranslated text falls
back to its source language until its catalog is completed.

To refresh the translation templates and create or update the French catalogs:

.. code-block:: sh

   make docs-gettext
   make docs-catalogs

Translate the ``msgstr`` values in the relevant ``docs/locale/<language>/``
catalogs while preserving Sphinx roles, references, code, and markup. Build
both languages locally with:

.. code-block:: sh

   make docs       # English and French

The ``Build and publish documentation`` GitHub Actions workflow builds both
languages on every push to ``main`` and pushes the generated site to the
``gh-pages`` branch using the repository's ``GITHUB_TOKEN``. In the GitHub
repository settings, configure Pages to deploy from the ``gh-pages`` branch
root. The workflow can also be started manually from the Actions tab.
