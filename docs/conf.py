project = "Rewake API"
copyright = "Rewake"
author = "Rewake"

extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinxcontrib.mermaid"]
myst_fence_as_directive = ["mermaid"]
# "#1-avant-de-commencer"-style links between headings (manuals).
myst_heading_anchors = 3

locale_dirs = ["locale"]
gettext_compact = False
gettext_uuid = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "manuals/images/**"]

html_theme = "sphinx_rtd_theme"
html_copy_source = False
